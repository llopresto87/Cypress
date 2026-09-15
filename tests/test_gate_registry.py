#!/usr/bin/env python3
"""The gate registry's own regression.

`tools/gate-registry.py` audits whether every gate is classified, and had
nothing auditing it. Its parser shipped seeing 4 of 8 ordinary invocation
spellings while reporting OK — the quietest possible false green, since a gate
it cannot see is not reported as unclassified, it is simply not there. That was
fixed twice, and both fixes were held in place by nothing.

Stdlib unittest, like every other suite here; no third-party imports.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import pathlib
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE.parent
TOOL = SEED / "tools" / "gate-registry.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("gate_registry_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gate_registry_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


class ParserTests(unittest.TestCase):
    """Every spelling a reviewer could construct must be visible.

    Each line below was, at some point, invisible to this parser while it
    reported OK. They are kept as one table because the defect is not any single
    spelling — it is the parser being narrower than the shell it reads.
    """

    SPELLINGS = {
        'bash "$ROOT/tests/test-plain.sh"': "test-plain.sh",
        'if [ -f x ]; then bash "$ROOT/tests/test-guarded.sh"; fi': "test-guarded.sh",
        '( cd "$ROOT" && bash "$ROOT/tests/test-subshell.sh" )': "test-subshell.sh",
        '( cd "$ROOT" && bash tests/test-relative.sh )': "test-relative.sh",
        'python3 -u "$ROOT/tools/test-flagged.py"': "test-flagged.py",
        '"$ROOT/tests/test-direct-exec.sh"': "test-direct-exec.sh",
        '$PY "$ROOT/tools/test-var-interp.py"': "test-var-interp.py",
        'python3.12 "$ROOT/tools/test-versioned.py"': "test-versioned.py",
        'bash "$ROOT/tests/test-with-args.sh" --some-arg': "test-with-args.sh",
    }

    def setUp(self):
        self.mod = load_tool()
        self.tmp = Path(tempfile.mkdtemp(prefix="cypress-gatereg-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _steps_for(self, lines):
        run_sh = self.tmp / "run.sh"
        run_sh.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + "\n".join(lines) + "\n")
        self.mod.RUN_SH = run_sh
        return self.mod.run_sh_steps()

    def test_every_invocation_spelling_is_seen(self):
        steps = self._steps_for(list(self.SPELLINGS))
        for line, expected in self.SPELLINGS.items():
            with self.subTest(line=line):
                self.assertIn(expected, steps,
                              f"parser did not see {expected!r} in: {line}")

    def test_a_line_continuation_is_joined(self):
        steps = self._steps_for(['bash \\', '    "$ROOT/tests/test-continued.sh"'])
        self.assertIn("test-continued.sh", steps)

    def test_comments_are_not_steps(self):
        steps = self._steps_for(['# bash "$ROOT/tests/test-commented.sh"',
                                 'bash "$ROOT/tests/test-real.sh"'])
        self.assertNotIn("test-commented.sh", steps)
        self.assertIn("test-real.sh", steps)

    def test_a_flag_distinguishes_two_runs_of_one_tool(self):
        steps = self._steps_for([
            'python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint --dir "$ROOT/agents"',
            'python3 "$ROOT/integrations/claude-code/agent-lint.py" --eval --dir "$ROOT/agents"',
        ])
        self.assertIn("agent-lint.py --lint", steps)
        self.assertIn("agent-lint.py --eval", steps)

    def test_parsing_nothing_is_itself_a_failure(self):
        """A parser that matches no steps must not report a clean registry —
        that is the shape the original defect took."""
        run_sh = self.tmp / "empty-run.sh"
        run_sh.write_text("#!/usr/bin/env bash\necho nothing here\n")
        self.mod.RUN_SH = run_sh
        # Captured: this asserts a FAILURE, and letting its banner reach the
        # gate log puts the word FAIL in a clean run. A passing suite should not
        # print the thing a reader scans for.
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = self.mod.cmd_lint()
        self.assertNotEqual(rc, 0, "zero parsed steps must fail, not pass")
        self.assertIn("parsed zero steps", buf_err.getvalue() + buf_out.getvalue())


class RefusalTests(unittest.TestCase):
    """The registry refuses in both directions, and both were proved by hand
    once. This is what keeps them proved."""

    def setUp(self):
        self.mod = load_tool()
        self.tmp = Path(tempfile.mkdtemp(prefix="cypress-gatereg2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _lint_with(self, lines, gates=None):
        """Run cmd_lint against a fixture run.sh AND a fixture GATES dict.

        Leaving the real 34-entry GATES in place while pointing RUN_SH at a
        two-line fixture made every clean `bash tests/run.sh` print thirty
        "registry lists X but run.sh no longer runs it" lines and a
        `gate-registry: FAIL` banner as routine noise. That is not a false green
        — the suite still turns genuinely red — but a passing run that prints
        FAIL teaches a reader to skim past the word, and defeats any `grep FAIL`
        someone wraps around the gate. The fixture gets a fixture roster.
        """
        run_sh = self.tmp / "run.sh"
        # A fixture runner is still a runner: `cmd_lint` holds the shell
        # contract as well as the roster, so the fixture carries the same
        # options the real one must.
        run_sh.write_text("#!/usr/bin/env bash\nset -euo pipefail\n"
                          + "\n".join(lines) + "\n")
        self.mod.RUN_SH = run_sh
        self.mod.GATES = gates if gates is not None else {}
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = self.mod.cmd_lint()
        return rc

    def test_an_unclassified_step_is_refused(self):
        rc = self._lint_with(['bash "$ROOT/tests/test-classified.sh"',
                              'bash "$ROOT/tests/test-brand-new-unclassified.sh"'],
                             gates={"test-classified.sh": ("x", "fixtures", "none", "")})
        self.assertNotEqual(rc, 0, "a step with no registry entry must fail")

    def test_a_registered_step_that_no_longer_runs_is_refused(self):
        """A documented gate that does not run is the plainest false green
        there is."""
        rc = self._lint_with(['bash "$ROOT/tests/test-still-there.sh"'],
                             gates={
                                 "test-still-there.sh": ("x", "fixtures", "none", ""),
                                 "test-retired-but-still-listed.sh": ("y", "fixtures", "none", ""),
                             })
        self.assertNotEqual(rc, 0, "an entry for a step not in run.sh must fail")

    def test_a_fully_matching_pair_passes(self):
        """The other direction, so the two refusals above are not just a tool
        that always fails."""
        rc = self._lint_with(['bash "$ROOT/tests/test-only.sh"'],
                             gates={"test-only.sh": ("x", "fixtures", "none", "")})
        self.assertEqual(rc, 0, "a run.sh and registry that agree must pass")


class RealTreeTests(unittest.TestCase):
    def test_the_shipped_registry_is_clean(self):
        mod = load_tool()
        self.assertEqual(mod.cmd_lint(), 0,
                         "the real tests/run.sh must be fully classified")

    def test_the_real_runner_carries_the_shell_options_that_make_it_fail(self):
        """Read from the REAL tests/run.sh, not a synthetic one.

        Every classification in the registry is a claim about a gate's input
        set. None of them is worth anything if the runner does not act on what
        a gate returns, and that is one character: `set -euo pipefail` minus
        the `e` took a run carrying three FAIL lines — a kernel 1 744 bytes
        over budget — to EXIT=0. The other tests in this file write
        `set -euo pipefail` into their own fixtures and so could never have
        seen it.
        """
        mod = load_tool()
        raw = mod.RUN_SH.read_text(encoding="utf-8")
        self.assertRegex(
            raw, r"(?m)^set -euo pipefail$",
            "tests/run.sh must carry `set -euo pipefail` on a line of its own")
        self.assertEqual(
            mod.runner_contract_problems(), [],
            "the shipped runner must satisfy its own shell contract")

    def test_a_neutralized_gate_line_is_refused(self):
        """`|| true` leaves the step running, parsed and classified — and
        unable to fail. The step parser's tail group stops at `|`, so the
        registry went on counting it as a gate."""
        mod = load_tool()
        raw = mod.RUN_SH.read_text(encoding="utf-8")
        line = next(l for l in raw.splitlines()
                    if re.search(r'bash "\$ROOT/tests/[a-z0-9-]+\.sh"$', l.strip()))
        self._assert_refused(mod, raw.replace(line, line + " || true"),
                             "|| true")

    def test_a_gate_outside_the_scanned_directories_is_refused(self):
        """Invisible on ADD: the parser only scans four directories, so a gate
        placed elsewhere runs while the registry reports OK about a tree it
        cannot see."""
        mod = load_tool()
        raw = mod.RUN_SH.read_text(encoding="utf-8")
        self._assert_refused(mod, raw + '\nbash "$ROOT/scripts/newgate.sh"\n',
                             "does not scan")

    def _assert_refused(self, mod, mutated_run_sh, expected_fragment):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "run.sh"
            path.write_text(mutated_run_sh, encoding="utf-8")
            original, mod.RUN_SH = mod.RUN_SH, path
            try:
                problems = mod.runner_contract_problems()
            finally:
                mod.RUN_SH = original
        self.assertTrue(
            any(expected_fragment in p for p in problems),
            f"expected a {expected_fragment!r} finding, got {problems}")

    def test_every_entry_declares_a_known_scope_and_class(self):
        mod = load_tool()
        classes = {"coverage", "scope", "self-reference", "representation",
                   "evidence", "semantic", "none"}
        for key, (asserts, scope, cls, _note) in mod.GATES.items():
            with self.subTest(gate=key):
                self.assertTrue(asserts, f"{key} does not say what it asserts")
                self.assertIn(scope, (mod.FIXTURES, mod.REAL, mod.TEMP))
                self.assertIn(cls, classes)


if __name__ == "__main__":
    unittest.main(verbosity=1)
