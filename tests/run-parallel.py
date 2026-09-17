#!/usr/bin/env python3
"""run-parallel: run tests/run.sh's independent gate steps concurrently.

tests/run.sh builds the seed-integrity snapshot and its EXIT trap, computes any
serial prerequisites (e.g. SPEC_BUDGET), then hands EVERY gate step to this
orchestrator as one already-variable-expanded shell command line per input line.

This is the TOP-LEVEL dispatcher. The concurrency budget, the cross-process
token pool, and the grouped-output / exit-code-aggregation machinery all live in
one place — tests/gate_pool.py — so this runner and every internally-parallel
suite obey the SAME `GATE_JOBS` knob and the SAME global ceiling. This file is
the thin wrapper that feeds run.sh's steps to that shared dispatcher.

Why this exists, and what it must NOT weaken:

  * The whole-run seed-integrity guard stays in run.sh — one snapshot before,
    one comparison in the EXIT trap. This orchestrator never touches the seed
    and takes no snapshot of its own; it only runs the steps between.
  * A naive `cmd &` loses exit codes. gate_pool.dispatch aggregates every step's
    status and exits non-zero if ANY step failed, naming each failed step — so
    the gate still fails the whole run on any red step, and `set -euo pipefail`
    in run.sh still aborts if this orchestrator returns non-zero.
  * Output is captured per step and printed GROUPED, never interleaved.
  * Portability floor is python3 stdlib only.

These steps are the COORDINATORS: several of them are suites that themselves run
scenarios from the shared pool. So this dispatcher runs its steps token-FREE
(pooled=False) — a coordinator that held a token while waiting on its own
children could deadlock the pool. The leaves inside the suites draw the tokens;
the global ceiling is still `resolve_workers()`, enforced by the shared pool.

Usage:
    python3 tests/run-parallel.py STEPS_FILE
        STEPS_FILE has one shell command per line (blank / #-comment lines
        ignored). Concurrency is gate_pool.resolve_workers(): an explicit
        $GATE_JOBS clamped to [4, 64], else the auto default clamp(cpu*2, 8, 64).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_pool  # noqa: E402  (sibling module, same dir)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run-parallel.py STEPS_FILE", file=sys.stderr)
        return 2
    steps = [
        (gate_pool._label(ln.strip()), ln.strip())
        for ln in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    if not steps:
        print("run-parallel: FAIL — zero steps to run", file=sys.stderr)
        return 1
    workers = min(gate_pool.resolve_workers(), len(steps))
    header = "run-parallel: %d gate steps, %d workers" % (len(steps), workers)
    return gate_pool.dispatch(steps, pooled=False, prefix="run-parallel",
                              noun="step", header=header)


if __name__ == "__main__":
    raise SystemExit(main())
