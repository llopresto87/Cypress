#!/usr/bin/env python3
"""run-parallel: run tests/run.sh's gate steps concurrently.

run.sh keeps the seed-integrity snapshot and its EXIT trap; this script only
runs the steps between. Budget, grouped output and exit-code aggregation live
in tests/gate_pool.py. The steps are coordinators (suites that draw pool tokens
for their own leaves), so they run token-free (pooled=False).

Usage: python3 tests/run-parallel.py STEPS_FILE
    One shell command per line; blank and #-comment lines are ignored.
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
