#!/usr/bin/env python3
"""gate_pool: the gate's ONE shared concurrency budget and scenario runner.

`tests/run.sh` is a tree of gate steps; several of the slow steps are
themselves a suite of INDEPENDENT scenarios (an install into its own temp
target, a planted-violation lint against its own temp copy). This module is the
single home for two facts every one of those places must agree on:

  1. HOW MANY things may run at once, anywhere in the gate. `resolve_workers()`
     honours an explicit `GATE_JOBS` (clamped to [4, 64]); with no override the
     AUTO default is `clamp(cpu_count * 2, 8, 64)`. The gate is I/O-bound — each
     step forks install.sh, copies trees and spawns python far more than it
     burns CPU — so oversubscribing cores overlaps that I/O wait and is faster
     even on a 4-core laptop (measured: a 4->8 worker budget nearly halved the
     wall time). One knob, `GATE_JOBS`, read here and nowhere else, honoured by
     the top-level `run-parallel.py` AND by every internally-parallel suite.

  2. A CROSS-PROCESS token pool (`TokenPool`) so that the TOTAL number of heavy
     leaf subprocesses running at once — summed over EVERY suite that is
     parallel at the same moment — stays <= the budget. Without it, N parallel
     suites each running `budget` workers would put `N * budget` installs on the
     box at once: the `cpu_count**2` explosion. The pool makes the ceiling
     `budget`, flat, no matter how many suites overlap. `$GATE_POOL_DIR` names
     the shared pool directory; when it is unset (a suite run on its own, not
     under run.sh) the pool is a no-op and the suite's own worker count bounds
     it.

Why a token pool and not just a small per-suite worker count: the suites do not
know about each other. The bound has to be GLOBAL, and the only thing every
process shares is the filesystem. `TokenPool` is a counting semaphore built from
atomic `os.mkdir` on slot directories — POSIX-atomic on macOS and Linux, no
`flock`, no third-party dependency, no GNU tool.

Only LEAF work acquires a token (the actual install / lint subprocess). A
coordinator never holds a token while waiting for its children, so the pool
cannot deadlock: `budget` coordinators each waiting on children would still
leave every token free for those children. The top-level dispatcher therefore
runs its steps token-FREE (they ARE the coordinators); the leaves inside them
draw from the pool.

Portability floor: python3 stdlib only, bash 3.2 hosts run this unchanged.

Usage as a library (the top-level run-parallel.py):
    import gate_pool
    rc = gate_pool.dispatch(scenarios, pooled=False)   # coordinators, no token

Usage as a CLI (a suite parallelising its own scenarios):
    python3 tests/gate_pool.py run SCENARIOS_FILE
        Each line is one scenario: "LABEL<TAB>SHELL COMMAND", or just a command
        (a label is then derived). Blank and #-comment lines are ignored. Every
        scenario runs `bash -c COMMAND` under one pool token, output is captured
        and printed GROUPED (never interleaved), every exit code is aggregated,
        and the run exits 1 naming each failed scenario if ANY failed — so a red
        scenario still fails the whole gate.
"""

from __future__ import annotations

import concurrent.futures
import os
import subprocess
import sys
import time
from pathlib import Path

MIN_WORKERS = 4          # absolute floor for an explicit GATE_JOBS override
MAX_WORKERS = 64         # absolute ceiling, bounds thread/memory blowup
IO_OVERSUBSCRIBE = 2     # gate work is I/O-bound (each step forks install.sh,
                         # copies trees, greps, spawns python) far more than it
                         # burns CPU — a 16-worker run drew only ~594% of 1600%
                         # CPU, so cores sit idle on I/O. Running MORE workers
                         # than cores overlaps that wait: measured, a 4->8
                         # worker budget nearly halved the wall time. So the
                         # AUTO default oversubscribes cores rather than matching
                         # them.
DEFAULT_MIN_WORKERS = 8  # auto-default floor: a 1-4 core laptop still gets the
                         # measured overlap win, not a 4-wide undersubscription.


def resolve_workers() -> int:
    """The gate's one concurrency knob.

    An explicit GATE_JOBS is honoured verbatim, clamped to [4, 64].
    With no GATE_JOBS the AUTO default is clamp(cpu_count * 2, 8, 64): the work
    is I/O-bound, so oversubscribing cores overlaps I/O wait and is faster even
    on a small box — never fewer than 8, never more than 64.
    """
    raw = os.environ.get("GATE_JOBS")
    if raw:
        try:
            return max(MIN_WORKERS, min(int(raw), MAX_WORKERS))
        except ValueError:
            pass
    cpu = os.cpu_count() or DEFAULT_MIN_WORKERS
    return max(DEFAULT_MIN_WORKERS, min(cpu * IO_OVERSUBSCRIBE, MAX_WORKERS))


class TokenPool:
    """A cross-process counting semaphore of `size` tokens.

    A token is an atomically-created slot directory under `root`; `os.mkdir`
    fails with FileExistsError when the slot is taken, which is the POSIX-atomic
    test-and-set this relies on. When `root` is None (no `$GATE_POOL_DIR`) the
    pool is a no-op and `size` alone — the caller's worker count — bounds
    concurrency.
    """

    def __init__(self, size: int, root: str | None = None):
        self.size = max(1, size)
        self.root = root if root is not None else os.environ.get("GATE_POOL_DIR")
        if self.root:
            os.makedirs(self.root, exist_ok=True)

    def acquire(self) -> str | None:
        if not self.root:
            return None
        i = 0
        while True:
            slot = os.path.join(self.root, "tok.%d" % (i % self.size))
            try:
                os.mkdir(slot)
                return slot
            except FileExistsError:
                i += 1
                if i % self.size == 0:
                    time.sleep(0.005)
            except OSError:
                # A transient FS error must not wedge the gate; fall back to
                # running without a token rather than blocking for ever.
                return None

    def release(self, slot: str | None) -> None:
        if slot:
            try:
                os.rmdir(slot)
            except OSError:
                pass


def _label(cmd: str) -> str:
    """A short, stable name for grouped output: the script basename plus any
    distinguishing --flag, mirroring tools/gate-registry.py's step keys."""
    parts = cmd.split()
    name = cmd
    for tok in parts:
        base = tok.strip('"').split("/")[-1]
        if base.endswith(".sh") or base.endswith(".py"):
            name = base
            break
    for tok in parts:
        if tok in ("--lint", "--eval", "--gaps"):
            name = "%s %s" % (name, tok)
            break
    return name


def parse_scenarios(path: str) -> list[tuple[str, str]]:
    """Read a scenarios file: one 'LABEL<TAB>COMMAND' (or bare COMMAND) per
    line, blanks and #-comments skipped. Returns [(label, command), ...]."""
    out = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if "\t" in ln:
            label, cmd = ln.split("\t", 1)
            label, cmd = label.strip(), cmd.strip()
        else:
            cmd = ln.strip()
            label = _label(cmd)
        out.append((label, cmd))
    return out


def _run_one(idx: int, label: str, cmd: str, pool: TokenPool | None) -> dict:
    start = time.monotonic()
    slot = pool.acquire() if pool else None
    try:
        proc = subprocess.run(
            ["bash", "-c", cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    finally:
        if pool:
            pool.release(slot)
    return {
        "idx": idx,
        "cmd": cmd,
        "label": label,
        "rc": proc.returncode,
        "output": proc.stdout.decode("utf-8", "replace"),
        "secs": time.monotonic() - start,
    }


def dispatch(scenarios: list[tuple[str, str]], pooled: bool,
             prefix: str = "gate_pool", noun: str = "scenario",
             header: str | None = None) -> int:
    """Run (label, command) scenarios concurrently under the shared budget.

    pooled=True  : each leaf scenario acquires one cross-process token, so this
                   suite's concurrency sums with every other parallel suite's
                   into a single global ceiling of `resolve_workers()`.
    pooled=False : the top-level dispatcher — its steps are coordinators, never
                   token holders, so they cannot starve the leaves beneath them.

    `prefix` and `noun` shape the summary lines so the top-level runner keeps
    saying "step" (its own regression pins that wording) while a suite says
    "scenario".
    """
    if not scenarios:
        print("%s: FAIL — zero %ss to run" % (prefix, noun), file=sys.stderr)
        return 1

    workers = resolve_workers()
    workers = max(1, min(workers, len(scenarios)))
    pool = TokenPool(resolve_workers()) if pooled else None

    t0 = time.monotonic()
    if header:
        print(header, flush=True)

    results: list[dict] = [None] * len(scenarios)  # type: ignore[list-item]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {
            ex.submit(_run_one, i, lbl, cmd, pool): i
            for i, (lbl, cmd) in enumerate(scenarios)
        }
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            r = fut.result()
            results[r["idx"]] = r
            done += 1
            mark = "ok  " if r["rc"] == 0 else "FAIL"
            print("  [%2d/%d] %s %s (%.1fs)"
                  % (done, len(scenarios), mark, r["label"], r["secs"]),
                  flush=True)

    failed = [r for r in results if r["rc"] != 0]
    for r in results:
        head = "PASS" if r["rc"] == 0 else ("FAIL rc=%d" % r["rc"])
        print("\n" + "=" * 72)
        print("[%s] %s  (%.1fs)" % (head, r["label"], r["secs"]))
        print("  $ %s" % r["cmd"])
        print("-" * 72)
        sys.stdout.write(r["output"])
        if r["output"] and not r["output"].endswith("\n"):
            sys.stdout.write("\n")

    total = time.monotonic() - t0
    print("\n" + "=" * 72)
    if failed:
        print("%s: FAIL — %d of %d %s(s) failed in %.1fs:"
              % (prefix, len(failed), len(scenarios), noun, total))
        for r in failed:
            print("    x %s  (rc=%d)" % (r["label"], r["rc"]))
        return 1
    print("%s: OK — all %d %ss passed in %.1fs"
          % (prefix, len(scenarios), noun, total))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "run" and len(argv) == 3:
        scenarios = parse_scenarios(argv[2])
        header = "gate_pool: %d scenarios" % len(scenarios)
        return dispatch(scenarios, pooled=True, prefix="gate_pool",
                        noun="scenario", header=header)
    if len(argv) >= 2 and argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    print("usage: gate_pool.py run SCENARIOS_FILE", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
