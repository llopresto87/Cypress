#!/usr/bin/env python3
"""tests/gate_pool.py: the GATE_JOBS clamp and the cross-process token pool.
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

AUTO = max(8, min((os.cpu_count() or 4) * 2, 64))


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
