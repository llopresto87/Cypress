#!/usr/bin/env python3
"""tests/run-parallel.py's own regression.

The parallel dispatcher is runner infrastructure, not a gate — it runs the
gates. Its one dangerous failure mode is the one a naive `cmd &` scheme has:
running a step that FAILS and reporting the whole batch green anyway. If that
regressed, every gate below it would still be executed and every verdict lost,
which is the quietest false green this repository can produce. So the aggregate
exit code, the naming of failed steps, and the all-green path are pinned here.

Stdlib unittest, no third-party imports, like every suite in this gate.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORCH = HERE / "run-parallel.py"


def run_orch(step_lines, jobs=None):
    """Run the orchestrator over a fixture steps file; return (rc, output)."""
    with tempfile.NamedTemporaryFile("w", suffix=".steps", delete=False) as fh:
        fh.write("\n".join(step_lines) + "\n")
        steps_path = fh.name
    env = dict(os.environ)
    if jobs is not None:
        env["GATE_JOBS"] = str(jobs)
    try:
        proc = subprocess.run(
            [sys.executable, str(ORCH), steps_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
        )
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    finally:
        os.unlink(steps_path)


class AggregationTests(unittest.TestCase):
    def test_all_green_exits_zero(self):
        rc, out = run_orch(["true", "true", "python3 -c 'pass'"])
        self.assertEqual(rc, 0, f"all-passing batch must exit 0:\n{out}")
        self.assertIn("OK", out)

    def test_one_red_step_fails_the_whole_batch(self):
        """The invariant a `cmd &` scheme loses: a single failing step must
        take the whole run non-zero."""
        rc, out = run_orch(["true", "false", "true"])
        self.assertNotEqual(rc, 0, f"a failing step must fail the batch:\n{out}")

    def test_a_failed_step_is_named(self):
        rc, out = run_orch(["true", "bash -c 'exit 7'"])
        self.assertNotEqual(rc, 0)
        # The failing command is echoed in its grouped block and the summary.
        self.assertIn("exit 7", out)
        self.assertRegex(out, r"FAIL")

    def test_every_failure_is_aggregated_not_just_the_first(self):
        rc, out = run_orch(["false", "true", "bash -c 'exit 3'"])
        self.assertNotEqual(rc, 0)
        # Both failures reported, not only the first encountered.
        self.assertIn("2 of 3 step(s) failed", out)

    def test_output_is_grouped_per_step(self):
        rc, out = run_orch([
            "echo AAA_marker",
            "echo BBB_marker",
        ])
        self.assertEqual(rc, 0, out)
        self.assertIn("AAA_marker", out)
        self.assertIn("BBB_marker", out)
        # Each step gets its own PASS header.
        self.assertGreaterEqual(out.count("[PASS]"), 2)

    def test_empty_steps_file_is_a_failure(self):
        rc, out = run_orch(["", "# only a comment"])
        self.assertNotEqual(rc, 0, "zero runnable steps must fail, not pass")

    def test_serialized_single_worker_still_aggregates(self):
        rc, out = run_orch(["true", "false"], jobs=1)
        self.assertNotEqual(rc, 0)

    def test_high_concurrency_does_not_drop_a_failure(self):
        steps = ["true"] * 20 + ["false"] + ["true"] * 20
        rc, out = run_orch(steps, jobs=16)
        self.assertNotEqual(rc, 0, "a lone failure among many must not be lost")


if __name__ == "__main__":
    unittest.main(verbosity=1)
