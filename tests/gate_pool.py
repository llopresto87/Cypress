#!/usr/bin/env python3
"""gate_pool: the gate's shared concurrency budget and scenario runner.

1. Two classes of work, two budgets. A step or scenario whose last measured
   CPU time over wall time is at least CPU_RATIO is CPU-bound and takes one of
   `cpu_slots()` tokens, one per core, so CPU-heavy work never shares a core.
   One below it waits on I/O and subprocess start-up, and takes one of
   `io_slots()` tokens, IO_OVERSUBSCRIBE per core, so waiting work overlaps.
   Work never measured counts as CPU-bound. An explicit `GATE_JOBS` caps the
   total (clamped to [4, 64]) and the CPU budget within it.
2. The runner measures what it runs: each child's CPU time (its rusage,
   reaped descendants included) and wall time go to the profile, a JSON cache
   outside the seed (`$GATE_PROFILE`, default
   `~/.cache/cypress-gate/profile.json`), keyed by label. The next run reads
   the class and starts the longest work first, which shortens the critical
   path. A missing or unreadable profile only loses the hints.
3. `TokenPool` is a cross-process counting semaphore, so the TOTAL work across
   every parallel suite stays within each budget. `$GATE_POOL_DIR` names the
   shared directory; unset, the pools are no-ops. Slots are atomic `os.mkdir`
   directories (POSIX, stdlib).

A coordinator (a step that runs its own scenarios through this module) never
holds a token while it waits on its children, so the pools cannot deadlock:
run-parallel.py runs such a step token-free and every other step under its
class's token.

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

import json
import re

MIN_WORKERS = 4          # floor for an explicit GATE_JOBS
MAX_WORKERS = 64         # ceiling, bounds thread/memory blowup
IO_OVERSUBSCRIBE = 4     # I/O-bound tokens per core
DEFAULT_MIN_WORKERS = 8  # auto-default floor for a 1-4 core box
CPU_RATIO = 0.5          # cpu/wall at or above this: CPU-bound
PROFILE = os.environ.get("GATE_PROFILE") or os.path.join(
    os.path.expanduser("~"), ".cache", "cypress-gate", "profile.json")



# A step that exits 0 because its input was absent checked nothing: it is
# reported as SKIP, never as PASS (a skipped donor-token scan once read PASS).
_SKIP_RE = __import__("re").compile(r"^[A-Za-z][\w .-]*: SKIP(PED)?\b", __import__("re").M)


def skipped(r) -> bool:
    return r["rc"] == 0 and bool(_SKIP_RE.search(r.get("output") or ""))

def resolve_workers() -> int:
    """The total budget: GATE_JOBS clamped to [4, 64]; unset or garbage, one
    CPU token per core plus IO_OVERSUBSCRIBE I/O tokens per core, capped."""
    raw = os.environ.get("GATE_JOBS")
    if raw:
        try:
            return max(MIN_WORKERS, min(int(raw), MAX_WORKERS))
        except ValueError:
            pass
    cpu = os.cpu_count() or DEFAULT_MIN_WORKERS
    return max(DEFAULT_MIN_WORKERS, min(cpu * (1 + IO_OVERSUBSCRIBE), MAX_WORKERS))


def cpu_slots() -> int:
    """CPU-bound tokens: one per core, never more than the total budget."""
    return max(1, min(os.cpu_count() or 1, resolve_workers()))


def io_slots() -> int:
    """I/O-bound tokens: the rest of the total budget, at least one per core."""
    return max(cpu_slots(), resolve_workers() - cpu_slots())


def load_profile() -> dict:
    try:
        with open(PROFILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_profile(updates: dict) -> None:
    """Merge this run's measurements into the profile; a failure loses hints only."""
    if not updates:
        return
    try:
        data = load_profile()
        data.update(updates)
        os.makedirs(os.path.dirname(PROFILE), exist_ok=True)
        tmp = "%s.%d.tmp" % (PROFILE, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=0, sort_keys=True)
        os.replace(tmp, PROFILE)
    except OSError:
        pass


def is_cpu_bound(entry: dict | None) -> bool:
    if not entry or not entry.get("wall"):
        return True                     # never measured: assume the heavier class
    return entry.get("cpu", 0) / entry["wall"] >= CPU_RATIO


_COORD = re.compile(r"gate_pool\.py[\"']?\s+run\b|\bgate_pool\b.*\bdispatch\b")


def is_coordinator(cmd: str) -> bool:
    """A step whose script runs its own scenarios through this module."""
    for tok in cmd.split():
        path = tok.strip("\"'")
        if path.endswith((".sh", ".py")) and os.path.isfile(path):
            try:
                return bool(_COORD.search(Path(path).read_text(encoding="utf-8", errors="replace")))
            except OSError:
                return False
    return False


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
        i, delay = 0, 0.01
        while True:
            slot = os.path.join(self.root, "tok.%d" % (i % self.size))
            try:
                os.mkdir(slot)
                return slot
            except FileExistsError:
                i += 1
                if i % self.size == 0:      # a full sweep found no slot: back off
                    time.sleep(delay)
                    delay = min(delay * 2, 0.25)
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
        env = dict(os.environ, GATE_PARENT=label)
        proc = subprocess.Popen(["bash", "-c", cmd], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, env=env)
        ran = time.monotonic()
        out = proc.stdout.read()
        _, status, ru = os.wait4(proc.pid, 0)
        proc.returncode = os.waitstatus_to_exitcode(status)
        proc.stdout.close()
    finally:
        if pool:
            pool.release(slot)
    return {
        "idx": idx,
        "cmd": cmd,
        "label": label,
        "rc": proc.returncode,
        "output": out.decode("utf-8", "replace"),
        "secs": time.monotonic() - start,
        "wall": time.monotonic() - ran,
        "cpu": ru.ru_utime + ru.ru_stime,
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
    root = os.environ.get("GATE_POOL_DIR")
    pools = {"cpu": TokenPool(cpu_slots(), os.path.join(root, "cpu") if root else None),
             "io": TokenPool(io_slots(), os.path.join(root, "io") if root else None)}
    parent = os.environ.get("GATE_PARENT", "")
    key = lambda lbl: "%s::%s" % (parent, lbl) if parent and pooled else lbl
    profile = load_profile()

    def pool_for(lbl: str, cmd: str) -> TokenPool | None:
        if not pooled and is_coordinator(cmd):
            return None                 # it waits on its own pooled scenarios
        return pools["cpu" if is_cpu_bound(profile.get(key(lbl))) else "io"]

    # longest first by the last measured wall time; never measured goes first
    order = sorted(range(len(scenarios)),
                   key=lambda i: -(profile.get(key(scenarios[i][0]), {}).get("wall") or 1e9))

    t0 = time.monotonic()
    if header:
        print(header, flush=True)

    results: list[dict] = [None] * len(scenarios)  # type: ignore[list-item]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {
            ex.submit(_run_one, i, scenarios[i][0], scenarios[i][1],
                      pool_for(*scenarios[i])): i
            for i in order
        }
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            r = fut.result()
            results[r["idx"]] = r
            done += 1
            mark = ("skip" if skipped(r) else "ok  ") if r["rc"] == 0 else "FAIL"
            print("  [%2d/%d] %s %s (%.1fs)"
                  % (done, len(scenarios), mark, r["label"], r["secs"]),
                  flush=True)

    save_profile({key(r["label"]): {"wall": round(r["wall"], 2), "cpu": round(r["cpu"], 2)}
                  for r in results})
    failed = [r for r in results if r["rc"] != 0]
    for r in results:
        head = (("SKIP" if skipped(r) else "PASS") if r["rc"] == 0
                else ("FAIL rc=%d" % r["rc"]))
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
    skips = [r for r in results if skipped(r)]
    if skips:
        print("%s: OK — %d of %d %ss passed, %d skipped (checked nothing) in %.1fs:"
              % (prefix, len(scenarios) - len(skips), len(scenarios), noun, len(skips), total))
        for r in skips:
            print("    - %s" % r["label"])
        return 0
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
