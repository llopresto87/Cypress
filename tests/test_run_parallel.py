#!/usr/bin/env python3
"""tests/run-parallel.py: a failing step must fail the batch (the `cmd &`
false green), be named, and never be dropped."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ORCH = Path(__file__).resolve().parent / "run-parallel.py"


def run_orch(step_lines):
    """Run the orchestrator over a fixture steps file; return (rc, output)."""
    with tempfile.NamedTemporaryFile("w", suffix=".steps", delete=False) as fh:
        fh.write("\n".join(step_lines) + "\n")
    try:
        proc = subprocess.run([sys.executable, str(ORCH), fh.name],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    finally:
        os.unlink(fh.name)


class AggregationTests(unittest.TestCase):
    def test_all_green_exits_zero(self):
        rc, out = run_orch(["echo AAA_marker", "echo BBB_marker", "python3 -c 'pass'"])
        self.assertEqual(rc, 0, f"all-passing batch must exit 0:\n{out}")
        self.assertIn("OK", out)
        self.assertIn("AAA_marker", out)
        self.assertIn("BBB_marker", out)
        self.assertGreaterEqual(out.count("[PASS]"), 2)  # grouped per step

    def test_every_failure_is_aggregated_not_just_the_first(self):
        rc, out = run_orch(["false", "true", "bash -c 'exit 3' /x/red-step.sh --lint"])
        self.assertNotEqual(rc, 0, f"a failing step must fail the batch:\n{out}")
        self.assertIn("2 of 3 step(s) failed", out)
        self.assertIn("exit 3", out)
        self.assertIn("x red-step.sh --lint  (rc=3)", out)  # bare-command label

    def test_empty_steps_file_is_a_failure(self):
        rc, out = run_orch(["", "# only a comment"])
        self.assertNotEqual(rc, 0, "zero runnable steps must fail, not pass")


if __name__ == "__main__":
    unittest.main(verbosity=1)
