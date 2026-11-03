#!/usr/bin/env python3
"""tests/gate_pool.py: the GATE_JOBS clamp, the two class budgets, the
measured profile and the cross-process token pool.
Exit-code aggregation is pinned by tests/test_run_parallel.py."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_pool  # noqa: E402

AUTO = max(8, min((os.cpu_count() or 4) * (1 + gate_pool.IO_OVERSUBSCRIBE), 64))


class ClampTests(unittest.TestCase):
    def test_gate_jobs_clamp(self):
        for jobs, want in [("1", 4), ("3", 4), ("16", 16), ("64", 64),
                           ("1000", 64), (None, AUTO), ("not-a-number", AUTO)]:
            env = {} if jobs is None else {"GATE_JOBS": jobs}
            with self.subTest(jobs=jobs), mock.patch.dict(os.environ, env):
                if jobs is None:
                    os.environ.pop("GATE_JOBS", None)
                self.assertEqual(gate_pool.resolve_workers(), want)
        self.assertGreaterEqual(AUTO, 8)  # a small box still oversubscribes


class ClassBudgetTests(unittest.TestCase):
    def test_cpu_tokens_match_cores_and_io_tokens_oversubscribe(self):
        with mock.patch.dict(os.environ, {}):
            os.environ.pop("GATE_JOBS", None)
            cores = os.cpu_count() or 1
            self.assertEqual(gate_pool.cpu_slots(), min(cores, gate_pool.resolve_workers()))
            self.assertGreaterEqual(gate_pool.io_slots(), gate_pool.cpu_slots())
        with mock.patch.dict(os.environ, {"GATE_JOBS": "4"}):
            self.assertLessEqual(gate_pool.cpu_slots(), 4)

    def test_class_follows_the_measured_ratio(self):
        self.assertTrue(gate_pool.is_cpu_bound(None))                 # never measured
        self.assertTrue(gate_pool.is_cpu_bound({"wall": 10, "cpu": 9}))
        self.assertFalse(gate_pool.is_cpu_bound({"wall": 10, "cpu": 2}))

    def test_a_coordinator_is_recognised_by_its_script(self):
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        (d / "suite.sh").write_text('python3 "$ROOT/tests/gate_pool.py" run "$F"\n')
        (d / "leaf.sh").write_text("echo hi\n")
        self.assertTrue(gate_pool.is_coordinator("bash %s" % (d / "suite.sh")))
        self.assertFalse(gate_pool.is_coordinator("bash %s" % (d / "leaf.sh")))

    def test_a_run_records_its_measurements_and_orders_longest_first(self):
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        prof = d / "profile.json"
        prof.write_text('{"long": {"wall": 50, "cpu": 1}, "short": {"wall": 1, "cpu": 1}}')
        f = d / "s.scn"
        f.write_text("short\techo short\nlong\techo long\n")
        env = dict(os.environ, GATE_PROFILE=str(prof), GATE_JOBS="4")
        env.pop("GATE_PARENT", None)
        out = subprocess.run([sys.executable, str(HERE / "gate_pool.py"), "run", str(f)],
                             capture_output=True, text=True, env=env).stdout
        self.assertIn("[PASS] long", out)
        data = __import__("json").loads(prof.read_text())
        self.assertIn("cpu", data["short"]); self.assertLess(data["long"]["wall"], 50)


class SkipTests(unittest.TestCase):
    def test_skip_is_not_reported_as_pass(self):
        """A step that exits 0 because its input was absent checked nothing:
        its header and the summary say SKIP, never PASS."""
        f = Path(tempfile.mkdtemp()) / "s.scn"
        self.addCleanup(shutil.rmtree, f.parent, True)
        f.write_text("absent\techo 'agnosticism lint: SKIPPED — no local forbid list'\n"
                     "real\techo 'grill lint: PASS'\n")
        out = subprocess.run([sys.executable, str(HERE / "gate_pool.py"), "run", str(f)],
                             capture_output=True, text=True).stdout
        self.assertIn("[SKIP] absent", out)
        self.assertIn("[PASS] real", out)
        self.assertIn("1 skipped (checked nothing)", out)
        self.assertNotIn("all 2", out)


class TokenPoolTests(unittest.TestCase):
    def test_pool_is_shared_across_processes(self):
        """Two gate_pool runs sharing one pool dir never exceed the budget
        together (which also bounds each run on its own)."""
        pooldir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, pooldir, True)
        files = []
        for tag in ("a", "b"):
            f = Path(pooldir + ".%s.scn" % tag)
            self.addCleanup(f.unlink)
            f.write_text("".join(
                "%s%d\tn=$(ls -d %s/tok.* 2>/dev/null | wc -l | tr -d ' '); "
                "echo CONC=$n; sleep 0.05\n" % (tag, i, pooldir) for i in range(15)))
            files.append(f)
        env = dict(os.environ, GATE_JOBS="6", GATE_POOL_DIR=pooldir)
        procs = [subprocess.Popen(
            [sys.executable, str(HERE / "gate_pool.py"), "run", str(f)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            for f in files]
        out = b"".join(p.communicate()[0] for p in procs).decode()
        concs = [int(m) for m in re.findall(r"CONC=(\d+)", out)]
        self.assertTrue(concs)
        self.assertLessEqual(max(concs), 6,
                             "shared pool did not bound cross-process concurrency")


if __name__ == "__main__":
    unittest.main(verbosity=1)
