#!/usr/bin/env python3
"""tests/gate_pool.py's own regression — the gate's shared concurrency budget.

gate_pool.py is runner infrastructure, not a gate: it RUNS the scenarios the
suites assert with. Two of its properties are load-bearing and easy to regress
silently, so they are pinned here:

  * the ONE concurrency knob: an explicit $GATE_JOBS is clamped to [4, 64];
    with no override the AUTO default is `clamp(cpu_count * 2, 8, 64)` — the
    gate is I/O-bound, so it oversubscribes cores on purpose (floor 8, never
    past 64);
  * the cross-process token pool caps the TOTAL leaf subprocesses across every
    parallel suite to the budget, so N parallel suites cannot become N*budget
    installs on the box (the cpu_count**2 explosion).

Its exit-code aggregation — the `cmd &` false green — is pinned by
tests/test_run_parallel.py, which drives the same dispatch path through the
top-level runner. Stdlib unittest, no third-party imports.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_pool  # noqa: E402

CPU = os.cpu_count() or 4


class ClampTests(unittest.TestCase):
    def _workers(self, jobs):
        env = os.environ.pop("GATE_JOBS", None)
        try:
            if jobs is not None:
                os.environ["GATE_JOBS"] = jobs
            else:
                os.environ.pop("GATE_JOBS", None)
            return gate_pool.resolve_workers()
        finally:
            os.environ.pop("GATE_JOBS", None)
            if env is not None:
                os.environ["GATE_JOBS"] = env

    def test_floor_is_four(self):
        self.assertEqual(self._workers("1"), 4)
        self.assertEqual(self._workers("3"), 4)

    def test_ceiling_is_sixty_four(self):
        self.assertEqual(self._workers("64"), 64)
        self.assertEqual(self._workers("1000"), 64)

    def test_passthrough_in_range(self):
        self.assertEqual(self._workers("16"), 16)

    def test_unset_oversubscribes_cores_clamped(self):
        # AUTO default: I/O-bound work oversubscribes cores (x2), floor 8, cap 64.
        self.assertEqual(self._workers(None), max(8, min(CPU * 2, 64)))

    def test_garbage_falls_back_to_auto_default(self):
        self.assertEqual(self._workers("not-a-number"), max(8, min(CPU * 2, 64)))

    def test_small_box_gets_oversubscribed_floor(self):
        # A 1-4 core laptop must still get the measured overlap win (>= 8),
        # not a 4-wide undersubscription.
        self.assertGreaterEqual(self._workers(None), 8)


class TokenPoolTests(unittest.TestCase):
    def test_pool_caps_total_concurrency_to_budget(self):
        """Many scenarios, a budget of 4, each recording how many token slots
        exist while it holds one: the observed peak must never exceed 4."""
        pooldir = tempfile.mkdtemp()
        scn = tempfile.NamedTemporaryFile("w", suffix=".scn", delete=False)
        for i in range(40):
            scn.write("s%d\tn=$(ls -d %s/tok.* 2>/dev/null | wc -l | tr -d ' '); "
                      "echo CONC=$n; sleep 0.03\n" % (i, pooldir))
        scn.close()
        env = dict(os.environ, GATE_JOBS="4", GATE_POOL_DIR=pooldir)
        proc = subprocess.run(
            [sys.executable, str(HERE / "gate_pool.py"), "run", scn.name],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        os.unlink(scn.name)
        import re, shutil
        concs = [int(m) for m in re.findall(r"CONC=(\d+)",
                                            proc.stdout.decode())]
        shutil.rmtree(pooldir, ignore_errors=True)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(concs, "no concurrency samples captured")
        self.assertLessEqual(max(concs), 4,
                             "token pool let concurrency exceed the budget")

    def test_pool_is_shared_across_processes(self):
        """Two SEPARATE gate_pool invocations sharing one pool dir must together
        never exceed the budget — the cross-process bound, not just in-process."""
        pooldir = tempfile.mkdtemp()
        files = []
        for tag in ("a", "b"):
            f = tempfile.NamedTemporaryFile("w", suffix=".scn", delete=False)
            for i in range(15):
                f.write("%s%d\tn=$(ls -d %s/tok.* 2>/dev/null | wc -l | tr -d ' '); "
                        "echo CONC=$n; sleep 0.05\n" % (tag, i, pooldir))
            f.close()
            files.append(f.name)
        env = dict(os.environ, GATE_JOBS="6", GATE_POOL_DIR=pooldir)
        procs = [subprocess.Popen(
            [sys.executable, str(HERE / "gate_pool.py"), "run", f],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            for f in files]
        out = b""
        for p in procs:
            o, _ = p.communicate()
            out += o
        import re, shutil
        for f in files:
            os.unlink(f)
        shutil.rmtree(pooldir, ignore_errors=True)
        concs = [int(m) for m in re.findall(r"CONC=(\d+)", out.decode())]
        self.assertTrue(concs)
        self.assertLessEqual(max(concs), 6,
                             "shared pool did not bound cross-process concurrency")


class DispatchTests(unittest.TestCase):
    def _run(self, lines, jobs=None):
        f = tempfile.NamedTemporaryFile("w", suffix=".scn", delete=False)
        f.write("\n".join(lines) + "\n")
        f.close()
        env = dict(os.environ)
        env.pop("GATE_POOL_DIR", None)
        if jobs is not None:
            env["GATE_JOBS"] = str(jobs)
        try:
            p = subprocess.run(
                [sys.executable, str(HERE / "gate_pool.py"), "run", f.name],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            return p.returncode, p.stdout.decode()
        finally:
            os.unlink(f.name)

    def test_all_green_exits_zero(self):
        rc, out = self._run(["a\ttrue", "b\ttrue"])
        self.assertEqual(rc, 0, out)
        self.assertIn("OK", out)

    def test_one_red_fails_and_is_named(self):
        rc, out = self._run(["a\ttrue", "boom\texit 7"])
        self.assertNotEqual(rc, 0)
        self.assertIn("boom", out)
        self.assertIn("FAIL", out)

    def test_bare_command_without_label_still_runs(self):
        rc, out = self._run(["echo hello_marker"])
        self.assertEqual(rc, 0, out)
        self.assertIn("hello_marker", out)

    def test_empty_file_is_a_failure(self):
        rc, out = self._run(["", "# comment only"])
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
