#!/usr/bin/env python3
"""gate_pool: the gate's one shared concurrency budget and scenario runner.

1. `resolve_workers()` is the one knob. An explicit `GATE_JOBS` is clamped to
   [4, 64]; unset, the default is clamp(cpu_count * 2, 8, 64). Gate work is
   I/O-bound, so oversubscribing cores is faster (measured: 4 -> 8 workers
   nearly halved wall time).
2. `TokenPool` is a cross-process counting semaphore, so the TOTAL leaf
   subprocesses across every parallel suite stay <= the budget, not
   N suites * budget. `$GATE_POOL_DIR` names the shared directory; unset, the
   pool is a no-op. Slots are atomic `os.mkdir` directories (POSIX, stdlib).

Only leaf work takes a token. A coordinator never holds one while it waits on
its children, so the pool cannot deadlock; run-parallel.py runs its steps
token-free for that reason.

Usage as a CLI (a suite running its own scenarios):
    python3 tests/gate_pool.py run SCENARIOS_FILE
        One scenario per line: "LABEL<TAB>COMMAND" or a bare command (label
        derived). Blank and #-comment lines are ignored. Each runs `bash -c`
        under one token; output is printed grouped; the run exits 1 naming
        each failed scenario.
"""

from __future__ import annotations

import concurrent.futures
import os
import subprocess
import sys
import time
from pathlib import Path

MIN_WORKERS = 4          # floor for an explicit GATE_JOBS
MAX_WORKERS = 64         # ceiling, bounds thread/memory blowup
IO_OVERSUBSCRIBE = 2     # auto default: workers per core (I/O-bound work)
DEFAULT_MIN_WORKERS = 8  # auto-default floor for a 1-4 core box


def resolve_workers() -> int:
    """GATE_JOBS clamped to [4, 64]; unset or garbage: clamp(cpu*2, 8, 64)."""
    raw = os.environ.get("GATE_JOBS")
    if raw:
        try:
            return max(MIN_WORKERS, min(int(raw), MAX_WORKERS))
        except ValueError:
            pass
    cpu = os.cpu_count() or DEFAULT_MIN_WORKERS
    return max(DEFAULT_MIN_WORKERS, min(cpu * IO_OVERSUBSCRIBE, MAX_WORKERS))


class TokenPool:
    """`size` tokens as slot directories under `root`; a no-op without root."""

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
                # A transient FS error must not wedge the gate: run tokenless.
                return None

    def release(self, slot: str | None) -> None:
        if slot:
            try:
                os.rmdir(slot)
            except OSError:
                pass


def _label(cmd: str) -> str:
    """Script basename plus any --lint/--eval/--gaps flag (gate-registry keys)."""
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
    """[(label, command), ...] from a scenarios file (see module docstring)."""
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
    """Run (label, command) pairs under the shared budget; 0 only if all pass.

    pooled=True: each leaf takes a cross-process token. pooled=False: the
    top-level coordinators, which never hold a token. `prefix` and `noun`
    shape the summary ("step" for run-parallel, "scenario" for a suite).
    """
    if not scenarios:
        print("%s: FAIL — zero %ss to run" % (prefix, noun), file=sys.stderr)
        return 1

    budget = resolve_workers()
    workers = max(1, min(budget, len(scenarios)))
    pool = TokenPool(budget) if pooled else None

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
