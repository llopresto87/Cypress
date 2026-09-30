#!/usr/bin/env python3
"""CLI-contract tests for integrations/claude-code/agent-lint.py.

Every test drives the tool through `--route`, `--lint` or `--eval`. Stdlib
unittest only, so the suite runs under a bare `python3 tests/test_agent_lint.py`.
The runs of the tool over the real roster and corpus are gate steps in
tests/run.sh; this suite tests fixtures and the router's scoring rules.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent   # <seed>/tests
SEED = HERE.parent                        # the seed root
LINT = SEED / "integrations" / "claude-code" / "agent-lint.py"

# The roster is the seed's own agents/, whatever the seed is checked out
# inside. CYPRESS_ROSTER_DIR names another roster and is used verbatim.
_ROSTER_ENV = "CYPRESS_ROSTER_DIR"
_roster_override = (os.environ.get(_ROSTER_ENV) or "").strip()
if _roster_override:
    ROSTER = Path(_roster_override)
    ROSTER_RULE = f"explicit — ${_ROSTER_ENV}"
else:
    ROSTER = SEED / "agents"
    ROSTER_RULE = "default — <seed>/agents"
print(f"roster: {ROSTER}  (rule: {ROSTER_RULE})", file=sys.stderr)

CORPUS_TSV = ROSTER / "_routes.golden.tsv"
ROSTER_ARGS = ["--dir", str(ROSTER)]


def _roster_names() -> set:
    """Agent names derived from the roster's frontmatter, never listed."""
    names = set()
    files = [f for f in sorted(ROSTER.glob("*.md")) if not f.name.startswith("_")]
    for f in files:
        text = f.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        m = re.search(r"^name:\s*(.+)$", text[4:text.index("\n---\n", 3)], re.M)
        if m:
            names.add(m.group(1).strip())
    if not names:
        raise SystemExit(f"no agent names derivable from {ROSTER} — "
                         f"the corpus check would pass vacuously")
    if len(names) != len(files):
        raise SystemExit(
            f"{len(files)} agent file(s) in {ROSTER} but only {len(names)} "
            f"derivable name(s) — a file with no `name:` silently leaves the roster")
    return names


ALL_AGENTS = _roster_names()


def lint_constant(name: str) -> int:
    """A module-level int of agent-lint, read from its text (an import can
    serve a stale bytecode cache when a value changes but the size does not)."""
    m = re.search(rf"^{name}\s*=\s*([0-9_]+)", LINT.read_text(encoding="utf-8"), re.M)
    assert m, f"{name} is not a module-level int in {LINT}"
    return int(m.group(1).replace("_", ""))


def _load_lint_module():
    """agent-lint as a module, compiled from its current source text."""
    mod = types.ModuleType("agent_lint_under_test")
    mod.__file__ = str(LINT)
    sys.modules[mod.__name__] = mod
    try:
        exec(compile(LINT.read_text(encoding="utf-8"), str(LINT), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(mod.__name__, None)
    return mod


def run(script: Path, args, cwd: Path) -> subprocess.CompletedProcess:
    # No --dir is injected: fixture tests rely on the tool walking up from cwd.
    return subprocess.run([sys.executable, str(script), *args], cwd=str(cwd),
                          capture_output=True, text=True, timeout=60)


def route(task: str) -> subprocess.CompletedProcess:
    """--route over the real roster."""
    return run(LINT, ["--route", task, *ROSTER_ARGS], cwd=SEED)


_BAND_RE = re.compile(r"confidence:\s*(HIGH|MEDIUM|LOW|NONE)", re.IGNORECASE)


def band(out: str):
    m = _BAND_RE.search(out)
    return m.group(1).upper() if m else None


FLOOR = lint_constant("FLOOR")


def score_of(out: str, agent: str):
    """The printed score for one agent in a --route ranking, or 0 if unranked."""
    m = re.search(rf"^\s*{re.escape(agent)}\s+\S+\s+\S+\s+score=(\d+)", out, re.M)
    return int(m.group(1)) if m else 0


def top_pick(out: str):
    """First ranked (indented) agent name printed after the ROUTE header."""
    if "ROUTE" not in out:
        return None
    for ln in out.split("ROUTE", 1)[1].splitlines()[1:]:
        s = ln.strip()
        if not s:
            continue
        if s.upper().startswith("HINT") or ln[0] not in " \t":
            break
        return s.split()[0]
    return None


def agent_md(name, *, description="handles project work",
             tools="[Read, Write, Edit, Glob, Grep, Bash]", model="opus",
             effort="medium", origin=None, triggers=("do the work",),
             can_delegate=False, max_spawn_depth=None, delegates_to=None,
             body="Body of the agent definition."):
    """An agent def. `None` omits a key (`model`, `effort`, ...); `triggers=()`
    emits an empty list."""
    out = ["---", f"name: {name}", f"description: {description}"]
    if origin is not None:
        out.append(f"origin: {origin}")
    if tools is not None:
        out.append(f"tools: {tools}")
    if model is not None:
        out.append(f"model: {model}")
    if effort is not None:
        out.append(f"effort: {effort}")
    if triggers is not None:
        out.append("routing_triggers:")
        out += [f'  - "{t}"' for t in triggers]
    out.append(f"can_delegate: {'true' if can_delegate else 'false'}")
    if max_spawn_depth is not None:
        out.append(f"max_spawn_depth: {max_spawn_depth}")
    if delegates_to is not None:
        out.append("delegates_to:")
        out += [f"  - {d}" for d in delegates_to]
    return "\n".join(out + ["---", "", body, ""])


def build_project(tmp_path: Path, agents: dict, golden: str | None = None):
    """A hermetic project <root>/.claude/{agent-lint.py, frontmatter.py, agents/},
    so the tool's walk-up from cwd=<root> finds only this fixture roster."""
    root = tmp_path / "proj"
    adir = root / ".claude" / "agents"
    adir.mkdir(parents=True)
    dst = root / ".claude" / "agent-lint.py"
    shutil.copy(LINT, dst)
    shutil.copy(SEED / "templates" / "knowledge-graph" / "frontmatter.py",
                root / ".claude" / "frontmatter.py")
    for stem, content in agents.items():
        (adir / f"{stem}.md").write_text(content, encoding="utf-8")
    if golden is not None:
        (adir / "_routes.golden.tsv").write_text(golden, encoding="utf-8")
    return root, dst


def load_corpus():
    """Rows as (task, expected, corpus_class), parsed from the documented
    format rather than through the tool's loader; the class defaults to
    `contract`."""
    rows = []
    for line in CORPUS_TSV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        parts = [c.strip() for c in line.split("\t")]
        rows.append((parts[0], parts[1], parts[2] if len(parts) > 2 and parts[2] else "contract"))
    return rows


class TmpCase(unittest.TestCase):
    """A temp directory per test, and --lint / --route over a fixture roster."""

    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def _lint(self, agents):
        root, dst = build_project(self.tmp_path, agents)
        return run(dst, ["--lint"], cwd=root)

    def _route(self, agents, task):
        root, dst = build_project(self.tmp_path, agents)
        return run(dst, ["--route", task], cwd=root)


class RealRosterCase(TmpCase):
    """--eval over a temp copy of the real roster with an edited corpus."""

    def setUp(self):
        super().setUp()
        self.roster = self.tmp_path / "agents"
        self.roster.mkdir()
        for f in ROSTER.glob("*.md"):
            shutil.copy(f, self.roster / f.name)
        shutil.copy(CORPUS_TSV, self.roster / CORPUS_TSV.name)

    def _rows(self):
        return [l + "\n" for l in CORPUS_TSV.read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#") and "\t" in l]

    def _write(self, rows):
        text = rows if isinstance(rows, str) else "# task\texpected\tclass\n" + "".join(rows)
        (self.roster / "_routes.golden.tsv").write_text(text, encoding="utf-8")

    def _eval(self):
        return run(LINT, ["--eval", "--dir", str(self.roster)], cwd=self.tmp_path)


# ==========================================================================
# 1. --route: ranked list, confidence band, representative top picks.
# ==========================================================================
REPRESENTATIVE = [
    ("audit this diff against the spec", "reviewer"),
    ("review the pull request before we merge", "reviewer"),
    ("write the failing test that encodes the spec contract", "tester"),
    ("add a regression test for this bug", "tester"),
    ("make the failing test pass", "implementer"),
    ("design the data model for the orders service", "architect"),
    ("choose a framework and write the adr for the split", "architect"),
    ("the deploy is flaking under load, add observability", "reliability"),
    ("configure rollback and capacity budgets for the cluster", "reliability"),
    ("author a graph node for the auth subsystem", "docs-librarian"),
    ("fix the wiki page that fails graph validation", "docs-librarian"),
    ("add a threat model for the upload endpoint", "security"),
    ("assess the supply-chain and secrets handling risk", "security"),
    ("design a multi-agent topology with bounded delegation", "multi-agent-architect"),
    ("diagnose runaway fan-out in the agent fleet", "multi-agent-architect"),
    ("generate synthetic fixture data for tests not sourced from production", "data-ml"),
    ("write the acceptance criteria and the user flow", "product"),
    ("retrieve the authoritative upstream documentation for a new library", "research-scout"),
    ("run an authorized penetration test of the login", "pentest"),
]


class RouteTests(unittest.TestCase):
    def test_route_emits_ranked_list_and_band(self):
        """--route prints a band, a ranked list and the honesty note."""
        r = route("write the failing test that encodes the contract")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(band(r.stdout), {"HIGH", "MEDIUM", "LOW", "NONE"}, r.stdout)
        self.assertIsNotNone(top_pick(r.stdout), r.stdout)
        # BannerTests.test_banner_honesty_note: the router says it is a heuristic.
        self.assertIn("keyword heuristic", r.stdout.lower(), r.stdout)


def _make_representative_test(task, expected):
    def test(self):
        r = route(task)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(top_pick(r.stdout), expected, f"task {task!r}:\n{r.stdout}")
    return test


for _i, (_task, _expected) in enumerate(REPRESENTATIVE):
    _slug = re.sub(r"[^a-z0-9]+", "_", _task.lower()).strip("_")[:40]
    setattr(RouteTests,
            f"test_route_representative_top_pick_{_i:02d}_{_expected.replace('-', '_')}_{_slug}",
            _make_representative_test(_task, _expected))
del _i, _task, _expected, _slug


# ==========================================================================
# 2. Confidence bands and scoring.
# ==========================================================================
def _band_roster():
    return {
        "reviewer": agent_md("reviewer", description="reviews code diffs",
                             triggers=["audit the diff for regressions"]),
        "alpha": agent_md("alpha", description="writes code modules",
                          triggers=["migrate the postgres schema"]),
        "beta": agent_md("beta", description="refactors code paths",
                         triggers=["quarantine the flaky end-to-end fixture"]),
        "gamma": agent_md("gamma", description="ships code to prod",
                          triggers=["provision the kubernetes cluster"]),
    }


class ConfidenceTests(TmpCase):
    def test_confidence_high_on_unambiguous_task(self):
        r = self._route(_band_roster(), "audit the diff for regressions")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(band(r.stdout), "HIGH", r.stdout)
        self.assertEqual(top_pick(r.stdout), "reviewer", r.stdout)

    def test_confidence_none_on_no_match(self):
        r = self._route(_band_roster(), "xyzzy plugh frobnicate quux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(band(r.stdout), "NONE", r.stdout)
        self.assertIn("commission", r.stdout.lower(), r.stdout)

    def test_confidence_low_on_novel_stack(self):
        r = self._route(_band_roster(), "set up a cobol batch job on the mainframe")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(band(r.stdout), {"LOW", "NONE"}, r.stdout)
        self.assertIn("commission", r.stdout.lower(), r.stdout)


class ScoringTests(TmpCase):
    def test_scoring_distinctive_trigger_dominates(self):
        r = self._route(_band_roster(), "quarantine the flaky end-to-end fixture")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(top_pick(r.stdout), "beta", r.stdout)

    def test_scoring_generic_word_does_not_misroute(self):
        """A word every agent shares ('code') must not route HIGH."""
        r = self._route(_band_roster(), "improve the code")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual(band(r.stdout), "HIGH", r.stdout)

    def test_scoring_trigger_beats_description(self):
        agents = {
            "trig": agent_md("trig", description="a plain worker",
                             triggers=["reconcile the ledger"]),
            "desc": agent_md("desc", description="this agent will reconcile things",
                             triggers=["unrelated placeholder phrase"]),
        }
        r = self._route(agents, "reconcile the accounts")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(top_pick(r.stdout), "trig", r.stdout)

    def test_a_rare_word_in_a_real_trigger_still_dominates(self):
        """Asserts SPEC-0002 RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH and
        COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE (the compound the roster writes still
        routes, hyphenated or not). Real roster; each row routes HIGH to its owner."""
        for task, owner in (
                ("diagnose runaway fan-out in the agent fleet", "multi-agent-architect"),
                ("starting completely from scratch, set up the docs graph for this repo",
                 "growth-orchestrator"),
                ("assess the supply-chain and secrets handling risk", "security")):
            with self.subTest(task=task):
                r = route(task)
                self.assertEqual(band(r.stdout), "HIGH", r.stdout)
                self.assertEqual(top_pick(r.stdout), owner, r.stdout)

    def test_a_compound_fragment_does_not_earn_a_confident_route(self):
        """Asserts SPEC-0002 COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE and
        RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH. Real roster; none of these may
        carry a confident route: a description-only rare word, a fragment of a
        hyphenated compound, and a compound nobody on the roster writes."""
        for task in ("burns money", "chain of calls",
                     "configure the sap abap transport request"):
            with self.subTest(task=task):
                r = route(task)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn(band(r.stdout), ("LOW", "NONE"), r.stdout)
        # A compound found only in description prose licenses nothing:
        # `claim-bearing` is in devils-advocate's description, not its triggers.
        r = route("we need to sort out the claim bearing situation in the billing module")
        self.assertNotEqual(top_pick(r.stdout), "devils-advocate", r.stdout)
        self.assertLess(score_of(r.stdout, "devils-advocate"), FLOOR, r.stdout)


# ==========================================================================
# 3. --lint: spawn grants, triggers, effort, delegation depth.
# ==========================================================================
_LEAF = agent_md("leaf", tools="[Read, Grep]", triggers=["do the leaf work"])


class InlineToolsTests(TmpCase):
    def test_inline_tools_list_parsed_detects_task_present(self):
        """can_delegate must equal a spawn grant in the inline `tools:` list,
        which proves the list is parsed into tokens."""
        for tools, can_delegate, ok in (
                ("[Read, Write, Bash, Task]", True, True),    # valid delegator
                ("[Read, Write, Task]", False, False),        # Task present
                ("[Read, Write, Edit]", True, False),         # Task absent
                ("[Read, Agent(leaf)]", False, False)):       # parenthesized grant
            with self.subTest(tools=tools, can_delegate=can_delegate):
                extra = dict(max_spawn_depth=1, delegates_to=["leaf"]) if can_delegate else {}
                r = self._lint({"boss": agent_md("boss", tools=tools, can_delegate=can_delegate,
                                                 triggers=["coordinate the work"], **extra),
                                "leaf": _LEAF})
                self.assertEqual(r.returncode == 0, ok, r.stdout + r.stderr)
                shutil.rmtree(self.tmp_path / "proj")
        grants_spawn = _load_lint_module().grants_spawn
        for raw, want in (("[Read, Task]", True), ("[Agent, Read]", True),
                          ("[Agent(leaf)]", True), ("Task", True),
                          ("[Read, Grep]", False), ("[]", False)):
            self.assertIs(grants_spawn(raw), want, raw)

    def test_agent_grant_without_can_delegate_fails_lint(self):
        """`Agent` is the spawn tool's canonical name, `Task` its alias."""
        r = self._lint({"boss": agent_md("boss", tools="[Read, Write, Agent]",
                                         triggers=["coordinate the work"]),
                        "leaf": _LEAF})
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("spawn tool", r.stdout + r.stderr)

    def test_agent_grant_with_can_delegate_passes_lint(self):
        r = self._lint({"boss": agent_md("boss", tools="[Read, Write, Bash, Agent]",
                                         triggers=["coordinate the work"], can_delegate=True,
                                         max_spawn_depth=1, delegates_to=["leaf"]),
                        "leaf": _LEAF})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_omitted_tools_fails_lint(self):
        """No `tools:` line inherits every tool, the spawn tool included."""
        r = self._lint({"boss": agent_md("boss", tools=None, triggers=["coordinate the work"]),
                        "leaf": _LEAF})
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_delegator_without_tools_line_fails_through_the_omission_branch(self):
        r = self._lint({"boss": agent_md("boss", tools=None, triggers=["coordinate the work"],
                                         can_delegate=True, max_spawn_depth=1,
                                         delegates_to=["leaf"]),
                        "leaf": _LEAF})
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        self.assertIn("boss", out)
        self.assertIn("omits its tools: line", out)


def _valid_roster():
    return {
        "reviewer": agent_md("reviewer", triggers=["audit the diff"]),
        "tester": agent_md("tester", triggers=["write the failing test"]),
        "architect": agent_md("architect", triggers=["design the data model"]),
    }


class LintTriggersTests(TmpCase):
    def test_lint_passes_on_valid_roster(self):
        r = self._lint(_valid_roster())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_lint_fails_on_missing_triggers(self):
        """A missing and an empty routing_triggers both fail, naming the agent."""
        for triggers in (None, ()):
            with self.subTest(triggers=triggers):
                r = self._lint({**_valid_roster(), "broken": agent_md("broken", triggers=triggers)})
                self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("broken", r.stdout + r.stderr)
                shutil.rmtree(self.tmp_path / "proj")


class LintEffortTests(TmpCase):
    """SPEC-0005 AGENT_DECLARES_EFFORT: `effort:` is required and one of
    low, medium, high, whoever owns the agent."""

    def _assert_refused(self, agent_name, **kw):
        r = self._lint({**_valid_roster(), "zz": agent_md(agent_name, **kw)})
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        line = next((ln for ln in out.splitlines() if agent_name in ln), "")
        self.assertIn("effort", line, out)
        return out

    def test_lint_accepts_each_value_in_the_closed_set(self):
        """Asserts SPEC-0005 AGENT_DECLARES_EFFORT."""
        r = self._lint({
            "slow": agent_md("slow", effort="low", triggers=["sweep the lint warnings"]),
            "mid": agent_md("mid", effort="medium", triggers=["write the failing test"]),
            "deep": agent_md("deep", effort="high", triggers=["design the data model"]),
        })
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_lint_fails_on_missing_effort(self):
        """Asserts SPEC-0005 AGENT_DECLARES_EFFORT."""
        self._assert_refused("lazy", effort=None, triggers=["tidy the imports"])

    def test_lint_fails_on_effort_outside_the_set(self):
        """Asserts SPEC-0005 AGENT_DECLARES_EFFORT. `xhigh` is a host value
        outside the seed's closed set."""
        self.assertIn("xhigh", self._assert_refused("eager", effort="xhigh",
                                                    triggers=["tidy the imports"]))

    def test_lint_fails_on_plant_agent_without_effort(self):
        """Asserts SPEC-0005 AGENT_WITHOUT_EFFORT_AFTER_GRAFT: a plant's own
        agent (`origin: project`) is held to the same rule."""
        self._assert_refused("plant-expert", origin="project", effort=None,
                             description="owns the mimsy borogove pipeline",
                             triggers=["tune the mimsy borogove pipeline"])


class LintModelClassTests(TmpCase):
    """SPEC-0005 AGENT_DECLARES_MODEL_CLASS: `model:` is required and one of
    opus, sonnet, haiku, inherit, whoever owns the agent (adr-0022, S3)."""

    def _assert_refused(self, agent_name, **kw):
        r = self._lint({**_valid_roster(), "zz": agent_md(agent_name, **kw)})
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out)
        line = next((ln for ln in out.splitlines() if agent_name in ln), "")
        self.assertIn("model", line, out)
        return out

    def test_lint_accepts_each_model_class_token(self):
        """Asserts SPEC-0005 AGENT_DECLARES_MODEL_CLASS. A plant agent on
        `haiku` or `inherit` keeps passing after graft."""
        r = self._lint({
            "big": agent_md("big", model="opus", triggers=["design the data model"]),
            "mid": agent_md("mid", model="sonnet", triggers=["write the failing test"]),
            "cheap": agent_md("cheap", model="haiku", origin="project",
                              triggers=["sweep the lint warnings"]),
            "same": agent_md("same", model="inherit", origin="project",
                             triggers=["tidy the imports"]),
        })
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_lint_fails_on_missing_model(self):
        """Asserts SPEC-0005 AGENT_DECLARES_MODEL_CLASS. An absent `model:`
        key gets the missing message, not the outside-the-set one."""
        out = self._assert_refused("modelless", model=None, triggers=["tidy the imports"])
        line = next(ln for ln in out.splitlines() if "modelless" in ln)
        self.assertIn("model missing", line, out)

    def test_lint_fails_on_model_outside_the_set(self):
        """Asserts SPEC-0005 AGENT_DECLARES_MODEL_CLASS. A full model id
        belongs in the plant's model map, not in the agent."""
        self.assertIn("provider-a/model-x",
                      self._assert_refused("pinned", model="provider-a/model-x",
                                           triggers=["tidy the imports"]))

    def test_lint_fails_on_plant_agent_with_model_outside_the_set(self):
        """Asserts SPEC-0005 AGENT_MODEL_OUTSIDE_SET_AFTER_GRAFT: a plant's own
        agent (`origin: project`) is held to the same rule."""
        self.assertIn("provider-a/model-x",
                      self._assert_refused("plant-pinned", origin="project",
                                           model="provider-a/model-x",
                                           description="owns the mimsy borogove pipeline",
                                           triggers=["tune the mimsy borogove pipeline"]))


def _delegator(name, *, depth, delegates_to, trigger):
    # `Task` in tools keeps the spawn-grant rule silent, so only depth can fail.
    return agent_md(name, tools="[Read, Write, Bash, Task]", triggers=[trigger],
                    can_delegate=True, max_spawn_depth=depth, delegates_to=delegates_to)


class LintDepthTests(TmpCase):
    """ADR-B: max_spawn_depth in [1,3]; every delegates_to target is a known,
    strictly shallower agent."""

    def _refused(self, agents, *needles):
        r = self._lint({**agents, "leaf": agent_md("leaf", triggers=["do the leaf work"])})
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        for n in needles:
            self.assertIn(n, out)

    def test_lint_fails_on_delegates_to_equal_depth(self):
        self._refused({"boss": _delegator("boss", depth=1, delegates_to=["mid"],
                                          trigger="coordinate the delegation"),
                       "mid": _delegator("mid", depth=1, delegates_to=["leaf"],
                                         trigger="carry the middle work")},
                      "ADR-B", "boss", "mid")

    def test_lint_fails_on_delegates_to_greater_depth(self):
        self._refused({"boss": _delegator("boss", depth=1, delegates_to=["mid"],
                                          trigger="coordinate the delegation"),
                       "mid": _delegator("mid", depth=2, delegates_to=["leaf"],
                                         trigger="carry the middle work")},
                      "ADR-B", "boss", "mid")

    def test_lint_fails_on_max_spawn_depth_out_of_range(self):
        self._refused({"boss": _delegator("boss", depth=5, delegates_to=["leaf"],
                                          trigger="coordinate the delegation")},
                      "max_spawn_depth", "[1,3]", "boss")

    def test_lint_fails_on_delegates_to_unknown_agent(self):
        self._refused({"boss": _delegator("boss", depth=1, delegates_to=["ghost"],
                                          trigger="coordinate the delegation")},
                      "unknown agent", "ghost", "boss")


# ==========================================================================
# 4. --eval: the golden-corpus gate.
# ==========================================================================
_EVAL_ROSTER = {
    "reviewer": agent_md("reviewer", triggers=["audit the diff against the spec",
                                               "review the pull request"]),
    "tester": agent_md("tester", triggers=["write the failing test",
                                           "add a regression test"]),
    "implementer": agent_md("implementer", triggers=["make the failing test pass",
                                                     "turn the red test green"]),
    "architect": agent_md("architect", triggers=["design the data model",
                                                 "write the adr for the split"]),
}

_GOOD_GOLDEN = (
    "# task\texpected\n"
    "audit the diff against the spec\treviewer\n"
    "review the pull request now\treviewer\n"
    "write the failing test first\ttester\n"
    "add a regression test for the bug\ttester\n"
    "make the failing test pass\timplementer\n"
    "turn the red test green\timplementer\n"
    "design the data model\tarchitect\n"
    "write the adr for the split\tarchitect\n"
    "set up a cobol batch job on the mainframe\tLOW\n"
)

_BAD_GOLDEN = (
    "# task\texpected (deliberately mislabeled)\n"
    "audit the diff against the spec\ttester\n"
    "review the pull request now\ttester\n"
    "write the failing test first\treviewer\n"
    "add a regression test for the bug\treviewer\n"
    "make the failing test pass\tarchitect\n"
    "turn the red test green\tarchitect\n"
    "design the data model\timplementer\n"
    "write the adr for the split\timplementer\n"
)


class EvalTests(TmpCase):
    def _eval(self, golden):
        root, dst = build_project(self.tmp_path, _EVAL_ROSTER, golden=golden)
        return run(dst, ["--eval"], cwd=root)

    def test_eval_passes_on_good_golden(self):
        r = self._eval(_GOOD_GOLDEN)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(re.search(r"\d", r.stdout), r.stdout)

    def test_eval_fails_on_zero_labeled_rows(self):
        """Only LOW rows once scored 0/0 as 100%; it must fail and say why."""
        r = self._eval("# task\texpected\tclass\n"
                       "set up a cobol batch job on the mainframe\tLOW\tunknown-domain\n"
                       "port the firmware to the new dsp\tLOW\tunknown-domain\n")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("vacuous", r.stdout + r.stderr)

    def test_eval_fails_below_threshold(self):
        r = self._eval(_BAD_GOLDEN)
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)


class AdversarialBudgetTests(RealRosterCase):
    def test_exceeding_the_budget_fails_the_gate(self):
        """Asserts SPEC-0002 THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO.

        Built on the real corpus, the only one that meets every other floor,
        so the failure can only come from the budget."""
        budget = lint_constant("ADVERSARIAL_CONFIDENT_WRONG_BUDGET")
        control = self._eval()
        self.assertEqual(control.returncode, 0, control.stdout + control.stderr)
        # Another agent's trigger, labelled adversarial: confidently wrong.
        baits = [("audit this diff against the spec once more", "tester"),
                 ("write the failing test that encodes the contract, first", "reviewer"),
                 ("make the failing test pass today", "architect"),
                 ("design the data model for the orders service now", "implementer")]
        self._write("".join(self._rows()) + "".join(
            f"{t}\t{w}\tadversarial\n" for t, w in baits[:budget + 2]))
        r = self._eval()
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout + r.stderr, r"adversarial.*budget|budget.*adversarial")


class CorpusHonestyTests(RealRosterCase):
    """--eval reports each class on its own, and a row cannot lie about
    being held out."""

    def test_classes_are_reported_separately_and_never_averaged(self):
        """SPEC-0002 EVERY_NUMBER_NAMES_ITS_CORPUS and OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY.

        Per line: every class publishes its own accuracy and overlap, and no
        line carries a cross-class word beside a number."""
        r = run(LINT, ["--eval", *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        seen = {m.group(1): line for line in r.stdout.splitlines()
                if (m := re.match(r"\s+(contract|paraphrase|adversarial|unknown-domain)\s+n=", line))}
        for cls in ("contract", "paraphrase", "adversarial", "unknown-domain"):
            self.assertIn(cls, seen, r.stdout)
            self.assertIn("mean-overlap-with-target=", seen[cls])
            self.assertIn("confident-correct=", seen[cls])
        banned = re.compile(r"(overall|averaged|all classes|across (all )?classes|combined "
                            r"accuracy|aggregate)", re.I)
        for line in r.stdout.splitlines():
            self.assertFalse(banned.search(line) and re.search(r"\d", line),
                             f"a figure that names no single class:\n{line}")

    def test_a_near_copy_may_not_be_labelled_paraphrase(self):
        """Asserts SPEC-0002 HELD_OUT_STAYS_HELD_OUT, SPEC-0002 MISLABELLED_PARAPHRASE."""
        rows = self._rows()
        # Relabel one contract row in place (the corpus refuses duplicate tasks).
        i = next(i for i, row in enumerate(rows)
                 if (p := row.rstrip("\n").split("\t"))[1] != "LOW"
                 and (len(p) == 2 or p[2] == "contract"))
        rows[i] = "\t".join(rows[i].rstrip("\n").split("\t")[:2]) + "\tparaphrase\n"
        self._write(rows)
        r = self._eval()
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("mislabelled paraphrase", r.stderr)

    def test_a_confident_wrong_route_fails_even_when_the_average_is_fine(self):
        """Asserts SPEC-0002 CONFIDENT_MISROUTE, SPEC-0002 CONFIDENT_WRONG_IS_THE_GATE."""
        self._write(self._rows() + [
            "turn this red test green and change nothing else\tlegal\tparaphrase\n"])
        r = self._eval()
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn("confident-and-wrong", r.stderr.lower())

    def test_abstention_on_a_held_out_row_is_not_a_failure(self):
        """Asserts SPEC-0002 ABSTENTION_IS_A_CORRECT_OUTCOME."""
        self._write(self._rows() + [
            "the quarterly board deck needs a nicer font\tui-ux-designer\tparaphrase\n"])
        r = self._eval()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_corpus_that_asks_for_no_routes_is_vacuous(self):
        """Asserts SPEC-0002 VACUOUS_CORPUS_IS_REFUSED."""
        self._write(["set up a cobol batch job on the mainframe\tLOW\tunknown-domain\n",
                     "port the firmware to the new dsp\tLOW\tunknown-domain\n"])
        r = self._eval()
        self.assertNotEqual(r.returncode, 0, r.stdout)


class UnknownDomainTests(RealRosterCase):
    def test_the_shipped_unknown_domain_rows_all_abstain(self):
        """Asserts SPEC-0002 UNKNOWN_DOMAIN_MUST_ABSTAIN."""
        r = run(LINT, ["--eval", *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = [l for l in r.stdout.splitlines() if "unknown-domain" in l and "n=" in l]
        self.assertTrue(line, r.stdout)
        self.assertIn("CONFIDENT-WRONG=0", line[0])

    def test_a_leaking_unknown_domain_row_fails_the_gate(self):
        """Asserts SPEC-0002 UNKNOWN_DOMAIN_MUST_ABSTAIN."""
        # Reaches reviewer; worded apart from the corpus's own reviewer row.
        self._write(self._rows() + [
            "go through this pull request against the written spec\tLOW\tunknown-domain\n"])
        r = self._eval()
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn("leak", r.stderr.lower())

    def test_a_padded_trigger_copy_cannot_pass_as_held_out(self):
        """Asserts SPEC-0002 HELD_OUT_STAYS_HELD_OUT and HELD_OUT_SET_MAY_NOT_BE_EMPTIED.

        Neither a padded trigger copy nor a LOW-expecting row may count as
        held out (the latter was test_a_row_expecting_low_may_not_wear_another_class)."""
        for row, needle in (
                ("please assess the supply-chain and secrets handling risk today"
                 "\tsecurity\tparaphrase\n", "mislabelled paraphrase"),
                ("zzqx frobnicate widget\tLOW\tparaphrase\n", "")):
            with self.subTest(row=row):
                self._write(self._rows() + [row])
                r = self._eval()
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assertIn(needle, r.stderr)


class ClassFloorTests(RealRosterCase):
    def test_emptying_a_whole_class_is_refused(self):
        """Asserts SPEC-0002 NEITHER_HELD_OUT_SET_MAY_BE_THINNED.

        Emptied (0 rows) or thinned to one below its floor, a held-out class
        fails, and the refusal names the count and the floor."""
        text = CORPUS_TSV.read_text(encoding="utf-8")
        lines = text.splitlines()
        for cls, floor in (("paraphrase", lint_constant("PARAPHRASE_MIN_ROWS")),
                           ("adversarial", lint_constant("ADVERSARIAL_MIN_ROWS"))):
            rows = [l for l in lines if l.rstrip().endswith("\t" + cls)]
            self.assertGreaterEqual(len(rows), floor, cls)
            for keep in (0, floor - 1):
                with self.subTest(cls=cls, keep=keep):
                    drop = set(rows[:len(rows) - keep])
                    self._write("\n".join(l for l in lines if l not in drop) + "\n")
                    r = self._eval()
                    self.assertNotEqual(r.returncode, 0, r.stdout)
                    self.assertIn(f"{cls} set has {keep} rows" if keep == 0
                                  else f"{keep} rows", r.stderr)
                    if keep:
                        self.assertIn(str(floor), r.stderr)

    def test_the_shipped_corpus_may_not_drop_its_class_column(self):
        """Without the class column every floor switches off, so the seed's
        corpus declares each class and meets each floor."""
        classes = {}
        for _, _, cls in load_corpus():
            classes[cls] = classes.get(cls, 0) + 1
        for cls in ("paraphrase", "adversarial", "unknown-domain"):
            self.assertIn(cls, classes)
        self.assertGreaterEqual(classes["paraphrase"], lint_constant("PARAPHRASE_MIN_ROWS"))
        self.assertGreaterEqual(classes["adversarial"], lint_constant("ADVERSARIAL_MIN_ROWS"))

    def test_a_legacy_two_column_corpus_still_passes(self):
        self._write("# task\texpected\n"
                    "audit this diff against the spec\treviewer\n"
                    "set up a cobol batch job on the mainframe\tLOW\n")
        r = self._eval()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class MeasuredRosterTests(RealRosterCase):
    """PARAPHRASE_FLOOR gates only the roster it was measured over (every
    agent `origin: seed`); on a grown roster it is reported, not gated."""

    GATED = "below the recorded floor"
    REPORTED = "Reported, not gated"

    def _neutered_corpus(self) -> str:
        """Every paraphrase task replaced by vocabulary no agent carries."""
        out, n = [], 0
        for line in CORPUS_TSV.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) > 2 and parts[2].strip() == "paraphrase":
                n += 1
                parts[0] = " ".join(f"{w}{n}" for w in
                                    ("zyzzogeton", "brillig", "slithy", "borogove"))
                line = "\t".join(parts)
            out.append(line)
        assert n, "no paraphrase rows in the shipped corpus to neuter"
        return "\n".join(out) + "\n"

    def test_the_measured_roster_still_gates_on_the_paraphrase_floor(self):
        """Asserts SPEC-0002 AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER's Except."""
        self._write(self._neutered_corpus())
        r = self._eval()
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(self.GATED, r.stderr)
        self.assertNotIn(self.REPORTED, r.stdout)

    def test_a_grown_roster_reports_the_paraphrase_floor_instead_of_gating_on_it(self):
        """Asserts SPEC-0002 AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER."""
        self._write(self._neutered_corpus())
        (self.roster / "zz-plant-expert.md").write_text(
            agent_md("plant-expert", origin="project",
                     description="owns the mimsy borogove pipeline",
                     triggers=("tune the mimsy borogove pipeline",)), encoding="utf-8")
        r = self._eval()
        self.assertNotIn(self.GATED, r.stderr)
        self.assertIn(self.REPORTED, r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_shipped_roster_is_the_measured_one(self):
        """Every shipped agent carries the origin the floor is keyed to."""
        m = re.search(r'^MEASURED_ROSTER_ORIGIN\s*=\s*"([a-z]+)"',
                      LINT.read_text(encoding="utf-8"), re.M)
        self.assertIsNotNone(m, "MEASURED_ROSTER_ORIGIN is not a module-level string")
        for f in sorted(ROSTER.glob("*.md")):
            if not f.name.startswith("_"):
                head = f.read_text(encoding="utf-8").split("\n---\n", 1)[0]
                self.assertIn(f"origin: {m.group(1)}", head, f.name)


class GoldenCorpusTests(unittest.TestCase):
    def test_golden_corpus_is_wellformed_and_covers_the_roster(self):
        """Asserts SPEC-0002 HELD_OUT_SET_MAY_NOT_BE_EMPTIED."""
        rows = load_corpus()
        self.assertTrue(rows, f"golden corpus is empty: {CORPUS_TSV}")
        covered = {a for _, a, _ in rows if a != "LOW"}
        self.assertFalse(covered - ALL_AGENTS,
                         f"{CORPUS_TSV} names agents absent from {ROSTER} "
                         f"({ROSTER_RULE}): {sorted(covered - ALL_AGENTS)}")
        missing = (ALL_AGENTS - {"orchestrator"}) - covered
        self.assertFalse(missing, f"{CORPUS_TSV} does not cover agent(s) of {ROSTER} "
                                  f"({ROSTER_RULE}): {sorted(missing)}")
        self.assertGreaterEqual(sum(1 for _, a, _ in rows if a == "LOW"), 3)
        bad = {c for _, _, c in rows} - {"contract", "paraphrase", "adversarial", "unknown-domain"}
        self.assertFalse(bad, f"unknown corpus class(es): {sorted(bad)}")
        self.assertGreaterEqual(sum(1 for r in rows if r[2] == "paraphrase"), 15,
                                "the paraphrase (held-out) set must keep >=15 rows")


if __name__ == "__main__":
    unittest.main(verbosity=2)
