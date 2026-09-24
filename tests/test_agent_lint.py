#!/usr/bin/env python3
"""RED tests authorizing P0 of the agent-routing plan.

Plan of record:
  cypress/docs/plans/agent-routing-and-delegation.md  (§4 design, §6 P0)

These tests are written BEFORE the production artifact exists (test-first,
kernel §3.4). The artifact `implementer` must build to turn them GREEN is the
mechanical agent-router `agent-lint.py` (plan §4.2), with:
  install target : .claude/agent-lint.py
  seed source    : cypress/integrations/claude-code/agent-lint.py
plus the new `routing_triggers:` (+ `can_delegate:`) frontmatter on every
agent def (plan §4.1 / §6 P0), and the golden routing set
`.claude/agents/_routes.golden.tsv` (plan §4.3).

Every test drives the tool through its CLI (the public contract per plan §4.2:
`--route` / `--lint` / `--eval`) rather than importing internals — a
public-interface test per the tester charter. Stdlib only (unittest); no
third-party deps — following the same discipline tests/test_graph_lint.py
already does (the seed's own rule: no third-party import in a shipped
script), so this suite runs under a bare `python3 tests/test_agent_lint.py`
and a green gate can no longer silently skip it for want of an optional
package.

RED reason: `agent-lint.py` does not exist yet, so `require_lint()` fails every
test with a clear "not built yet" message. When the tool + frontmatter + golden
ship, these go GREEN.

Contract map (P0 acceptance, plan §6):
  test_route_*                 -> --route returns a ranked specialist list + band
  test_confidence_*            -> confidence bands NONE/LOW/MEDIUM/HIGH (§4.2)
  test_scoring_*               -> triggers/name > description; IDF de-weights
                                  generic terms; distinctive trigger dominates
  test_inline_tools_*          -> frontmatter parser closes the inline-tools gap
  test_triggers_parse_real*    -> triggers parse from a real agent def shape
  test_lint_*                  -> --lint validates routing_triggers, fails on
                                  planted malformation (§4.1 rules 1-2)
  test_eval_*                  -> --eval runs the golden set, gates on >=90%,
                                  novel-stack -> LOW (§4.3)
  test_banner_honesty_note     -> "keyword heuristic" honesty note (§4.2)
"""

from __future__ import annotations

import os
import re
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# --------------------------------------------------------------------------
# Locations pinned by the plan.
# --------------------------------------------------------------------------
# Paths are derived from this test file's own location so the suite is
# project-agnostic and portable — no absolute or host-specific path is baked in.
HERE = Path(__file__).resolve().parent   # <seed>/tests
SEED = HERE.parent                        # the seed root (this repo)
REPO = SEED.parent                        # the host project the seed is installed into, if any

# NOTHING this suite reads is resolved through REPO. It survives only as the
# `cwd` a handful of --route/--eval cases run the tool from, where the roster is
# pinned by ROSTER_ARGS and the cwd decides nothing (SPEC-0001 §7,
# ROSTER_SUITE_CWD_IS_THE_HOST — a disclosed residual, narrowed in the same
# pass that ever removes a --dir pin, never before).

# The tool under test is the SEED's copy. It used to prefer REPO/.claude/, on
# the theory that the installed path is the one a session runs — but that copy
# belongs to whatever the seed happens to be checked out inside, so the suite
# tested a file the seed does not ship and cannot fix. test-full-install.sh is
# where the INSTALLED tool is exercised, against an install that gate builds.
AGENT_LINT_CANDIDATES = [
    SEED / "integrations" / "claude-code" / "agent-lint.py",
]

# The roster's HOME is the seed's own agents/ directory; a host's
# `.claude/agents` is only a harness PROJECTION of it, and it exists solely
# when the seed happens to be checked out inside a plant that installed it.
# This suite used to PREFER that projection when it was there. That preference
# is retired, not repaired, and the reason is worth keeping: a directory that
# satisfies SPEC-0001 §6's projection predicate is byte-identical to the seed's
# own roster, so reading it exercises nothing the seed home does not — while a
# projection that has DRIFTED (every grown plant adds agents of its own) fed
# this suite names the seed does not ship. That is not a hypothetical: nested
# inside such a plant, `bash tests/run.sh` aborted at its agent-lint step with
# "golden corpus does not cover: ['<the plant's agent>']" and, under `set -e`,
# left every later step unrun. The intent the preference served — that home and
# installed projection agree — keeps a live home in tests/test-full-install.sh,
# which decides it with the §6 predicate against an install it builds itself.
#
# So: the seed's own agents/, whatever sits above it. A caller who means a
# different roster names it, and it is honoured verbatim with no fallback and
# no substitution; the two refusal guards in _roster_names() below apply to it
# exactly as they apply to the default.
_ROSTER_ENV = "CYPRESS_ROSTER_DIR"
_roster_override = (os.environ.get(_ROSTER_ENV) or "").strip()
if _roster_override:
    ROSTER = Path(_roster_override)
    ROSTER_RULE = f"explicit — ${_ROSTER_ENV}"
else:
    ROSTER = SEED / "agents"
    ROSTER_RULE = "default — <seed>/agents"
LIVE_AGENTS = ROSTER

# A green that does not say which roster it read is a green about a roster the
# reader has not identified. Stated once, at import, before any case runs.
print(f"roster: {ROSTER}  (rule: {ROSTER_RULE})", file=sys.stderr)

# The golden routing corpus has ONE home: the roster's own directory. install.sh
# copies it to .claude/agents/ as a projection. This suite reads the home
# directly — it used to keep a third copy under tests/agent_router/, which is a
# second home by definition and had already drifted (its header still claimed
# "13 agent defs" while the roster had grown well past that). Parity between
# home and installed projection is asserted in tests/test-full-install.sh,
# where a projection actually exists.
CORPUS_TSV = ROSTER / "_routes.golden.tsv"
GOLDEN_COPIES = list(dict.fromkeys([CORPUS_TSV]))

# Tests that exercise the REAL roster pin it explicitly. Relying on the tool's
# walk-up discovery made them pass only when the seed sat inside an installed
# plant. (Planted-malformation tests must NOT use this — walk-up from their own
# tmp project root is exactly what they are testing.)
ROSTER_ARGS = ["--dir", str(ROSTER)]

# DERIVED from the frontmatter `name:` of every file in agents/, never listed.
# This was a hand-maintained set whose own comment said it mirrored the roster,
# which is the same "count in prose" defect CLAUDE.md warns about and which this
# repo has now been bitten by three times: a roster addition went green on every
# gate except this one, and the failure blamed the golden corpus for naming a
# "non-roster agent" that was in fact on the roster. The set exists only to keep
# the corpus honest about which names are routable; seed-lint.py owns the real
# roster<->manifest<->kernel agreement.
def _roster_names() -> set:
    names = set()
    for f in sorted(ROSTER.glob("*.md")):
        if f.name.startswith("_"):
            continue
        text = f.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        head = text[4:text.index("\n---\n", 3)]
        for line in head.splitlines():
            if line.startswith("name:"):
                names.add(line.split(":", 1)[1].strip())
                break
    files = [f for f in ROSTER.glob("*.md") if not f.name.startswith("_")]
    if not names:
        raise SystemExit(f"no agent names derivable from {ROSTER} — "
                         f"the corpus check would pass vacuously")
    # An EMPTY roster was guarded; a PARTIAL one was not. Deleting `name:` from
    # one agent dropped it out of ALL_AGENTS, so `covered - ALL_AGENTS` went
    # empty and the corpus check passed while the agent was unroutable.
    if len(names) != len(files):
        raise SystemExit(
            f"{len(files)} agent file(s) in {ROSTER} but only {len(names)} "
            f"derivable name(s) — a file with no `name:` silently leaves the "
            f"roster, and every corpus check downstream passes vacuously")
    return names


ALL_AGENTS = _roster_names()


def _locate_agent_lint():
    for c in AGENT_LINT_CANDIDATES:
        if c.exists():
            return c
    return None


def lint_constant(name: str) -> int:
    """Read a module-level int constant out of the shipped agent-lint source.

    From TEXT, never by importing: agent-lint is a script rather than a package,
    and `ratchet-lint.py` already found that importing it can serve a stale
    bytecode cache when a value changes without changing the file's (mtime,
    size) — `8_000` and `7_600` are the same byte length. A test that asserts a
    floor has to read the floor the tool will actually use.
    """
    src = require_lint().read_text(encoding="utf-8")
    m = re.search(rf"^{name}\s*=\s*([0-9_]+)", src, re.M)
    assert m, f"{name} is not a module-level int in {require_lint()}"
    return int(m.group(1).replace("_", ""))


def require_lint() -> Path:
    """The RED gate: fail with a clear reason when the artifact is absent."""
    lint = _locate_agent_lint()
    assert lint is not None, (
        "RED: agent-lint.py has not been built yet. Expected at one of:\n  "
        + "\n  ".join(str(c) for c in AGENT_LINT_CANDIDATES)
        + "\nThese tests authorize P0 of "
        "cypress/docs/plans/agent-routing-and-delegation.md. "
        "They go GREEN once `implementer` ships agent-lint.py, the "
        "routing_triggers frontmatter on the roster, and the golden set."
    )
    return lint


def _load_lint_module():
    """agent-lint as a module, compiled from its current source text.

    Executed from text for the reason `lint_constant` reads text: an import
    can serve a stale bytecode cache.
    """
    import types
    path = require_lint()
    mod = types.ModuleType("agent_lint_under_test")
    mod.__file__ = str(path)
    sys.modules[mod.__name__] = mod
    try:
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), mod.__dict__)
    finally:
        sys.modules.pop(mod.__name__, None)
    return mod


def run(script: Path, args, cwd: Path) -> subprocess.CompletedProcess:
    # NOTE: planted-malformation tests deliberately rely on the tool walking up
    # from their tmp project root, so this must NOT inject --dir. The
    # real-roster tests pin the roster themselves via ROSTER_ARGS.
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
    )


# --------------------------------------------------------------------------
# Output parsing helpers (mirror the pinned --route output shape, plan §4.2).
#
#   task: <task>
#
#   ROUTE (ranked, confidence: HIGH):
#     implementer      opus   can_delegate=false   score=14
#     tester           opus   can_delegate=false   score=6
#   HINT: ...
# --------------------------------------------------------------------------
_BAND_RE = re.compile(r"confidence:\s*(HIGH|MEDIUM|LOW|NONE)", re.IGNORECASE)


def band(out: str):
    m = _BAND_RE.search(out)
    return m.group(1).upper() if m else None


# `FLOOR` is read from the router rather than restated: a confidence threshold
# is the router's fact, and a copy of it here would be a second home for it.
FLOOR = int(re.search(r"^FLOOR\s*=\s*(\d+)",
                      (SEED / "integrations/claude-code/agent-lint.py")
                      .read_text(encoding="utf-8"), re.M).group(1))


def score_of(out: str, agent: str):
    """The printed score for one agent in a --route ranking, or 0 if unranked."""
    m = re.search(rf"^\s*{re.escape(agent)}\s+\S+\s+\S+\s+score=(\d+)",
                  out, re.M)
    return int(m.group(1)) if m else 0


def top_pick(out: str):
    """First ranked (indented) agent name printed after the ROUTE header."""
    if "ROUTE" not in out:
        return None
    tail = out.split("ROUTE", 1)[1]
    for ln in tail.splitlines()[1:]:  # skip the remainder of the header line
        s = ln.strip()
        if not s:
            continue
        if s.upper().startswith("HINT"):
            break
        if ln[0] in " \t":
            return s.split()[0]
        break  # a non-indented, non-HINT line ends the ranked block
    return None


# --------------------------------------------------------------------------
# Hermetic fixture agents (deterministic algorithm/lint/eval tests).
# --------------------------------------------------------------------------
def agent_md(
    name,
    *,
    description="handles project work",
    tools="[Read, Write, Edit, Glob, Grep, Bash]",
    model="opus",
    triggers=("do the work",),
    can_delegate=False,
    max_spawn_depth=None,
    delegates_to=None,
    body="Body of the agent definition.",
):
    """Build an agent def with the extended P0 frontmatter (plan §4.1).

    `tools` is emitted as the INLINE list form the real agent defs use
    (`tools: [a, b]`) — the parser gap this router must close.
    `triggers=None` omits the block entirely; `triggers=()` emits an empty
    `routing_triggers:` — the two malformations the linter must reject.
    `tools=None` omits the `tools:` line, which on the host means the agent
    inherits every tool, the spawn tool included.
    """
    out = ["---", f"name: {name}", f"description: {description}"]
    if tools is not None:
        out.append(f"tools: {tools}")
    out.append(f"model: {model}")
    if triggers is not None:
        out.append("routing_triggers:")
        for t in triggers:
            out.append(f'  - "{t}"')
    out.append(f"can_delegate: {'true' if can_delegate else 'false'}")
    if max_spawn_depth is not None:
        out.append(f"max_spawn_depth: {max_spawn_depth}")
    if delegates_to is not None:
        out.append("delegates_to:")
        for d in delegates_to:
            out.append(f"  - {d}")
    out.append("---")
    out.append("")
    out.append(body)
    out.append("")
    return "\n".join(out)


def build_project(tmp_path: Path, agents: dict, golden: str | None = None):
    """Materialize a hermetic project: <root>/.claude/{agent-lint.py,agents/}.

    Copying the located tool into <root>/.claude and running with cwd=<root>
    makes the tool's walk-up for `.claude/agents/` (plan §4.2) resolve to this
    fixture roster, so scoring is isolated from the real roster.
    """
    lint = require_lint()
    root = tmp_path / "proj"
    adir = root / ".claude" / "agents"
    adir.mkdir(parents=True)
    dst = root / ".claude" / "agent-lint.py"
    shutil.copy(lint, dst)
    # ...and the frontmatter reader it imports, beside it. agent-lint is a
    # standalone script, so the import resolves next to the script: every place
    # the engine TRAVELS carries the reader — install.sh does for all three of
    # its destinations, and so must a fixture that copies it into a temp plant.
    shutil.copy(SEED / "templates" / "knowledge-graph" / "frontmatter.py",
                root / ".claude" / "frontmatter.py")
    for stem, content in agents.items():
        (adir / f"{stem}.md").write_text(content, encoding="utf-8")
    if golden is not None:
        (adir / "_routes.golden.tsv").write_text(golden, encoding="utf-8")
    return root, dst


def load_corpus():
    """Rows as (task, expected, corpus_class).

    Parsed here rather than imported from the tool on purpose: this file is a
    CLI-contract test (see the module docstring), so it reads the corpus the way
    the documented format says to, and a divergence between the format and the
    tool's loader shows up as a test failure rather than being papered over by
    sharing the same code. The class column is optional and defaults to
    `contract`; the header of _routes.golden.tsv owns what the classes mean.
    """
    rows = []
    for line in CORPUS_TSV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        parts = [c.strip() for c in line.split("\t")]
        cls = parts[2] if len(parts) > 2 and parts[2] else "contract"
        rows.append((parts[0], parts[1], cls))
    return rows


# ==========================================================================
# 1. --route: ranked specialist list + confidence band for representative
#    golden tasks; assert the TOP pick (plan §6 P0 acceptance; task brief).
#    Run against the REAL 13-agent roster (with the triggers P0 adds).
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
    """Section 1: --route returns a ranked specialist list + confidence band."""

    def test_route_emits_ranked_list_and_band(self):
        """--route prints a confidence band and a ranked list (plan §4.2 shape)."""
        lint = require_lint()
        r = run(lint, ["--route", "write the failing test that encodes the contract",
                       *ROSTER_ARGS], cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(band(r.stdout), {"HIGH", "MEDIUM", "LOW", "NONE"},
                      f"no confidence band in output:\n{r.stdout}")
        self.assertIsNotNone(top_pick(r.stdout),
                             f"no ranked specialist line in output:\n{r.stdout}")


# One test PER (task, expected) pair, generated below rather than a single
# subTest loop: the prior parametrized version gave each case its own
# collected test id (19 of them), and a green gate run is counted by test
# count, so a faithful port keeps that same count — a subTest loop would
# collapse all 19 into a single collected test and silently shrink the
# suite's reported size.
def _make_representative_test(task, expected):
    def test(self):
        lint = require_lint()
        r = run(lint, ["--route", task, *ROSTER_ARGS], cwd=REPO)
        self.assertEqual(r.returncode, 0, f"--route should exit 0.\nstderr:\n{r.stderr}")
        self.assertEqual(top_pick(r.stdout), expected, (
            f"task {task!r}\nexpected top specialist {expected!r}\n"
            f"--- stdout ---\n{r.stdout}"
        ))
    return test


for _i, (_task, _expected) in enumerate(REPRESENTATIVE):
    _slug = re.sub(r"[^a-z0-9]+", "_", _task.lower()).strip("_")[:40]
    setattr(RouteTests,
            f"test_route_representative_top_pick_{_i:02d}_{_expected.replace('-', '_')}_{_slug}",
            _make_representative_test(_task, _expected))
del _i, _task, _expected, _slug


# ==========================================================================
# 2. Confidence bands (plan §4.2).
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


class ConfidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-confidence-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_confidence_high_on_unambiguous_task(self):
        """A task hitting one agent's distinctive triggers -> HIGH, that agent top."""
        root, dst = build_project(self.tmp_path, _band_roster())
        r = run(dst, ["--route", "audit the diff for regressions"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(band(r.stdout), "HIGH", f"expected HIGH:\n{r.stdout}")
        self.assertEqual(top_pick(r.stdout), "reviewer", r.stdout)

    def test_confidence_none_on_no_match(self):
        """Gibberish matches nothing -> NONE, and the hint points at commission."""
        root, dst = build_project(self.tmp_path, _band_roster())
        r = run(dst, ["--route", "xyzzy plugh frobnicate quux"], cwd=root)
        self.assertEqual(r.returncode, 0, f"--route must not crash on a no-match:\n{r.stderr}")
        self.assertEqual(band(r.stdout), "NONE", f"expected NONE:\n{r.stdout}")
        self.assertIn("commission", r.stdout.lower(),
                      f"NONE hint must recommend commissioning an expert:\n{r.stdout}")

    def test_confidence_low_on_novel_stack(self):
        """A novel-stack task no specialist covers -> LOW/NONE + commission hint."""
        root, dst = build_project(self.tmp_path, _band_roster())
        r = run(dst, ["--route", "set up a cobol batch job on the mainframe"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(band(r.stdout), {"LOW", "NONE"},
                     f"a novel-stack task must be LOW/NONE (commission path):\n{r.stdout}")
        self.assertIn("commission", r.stdout.lower(), r.stdout)


# ==========================================================================
# 3. Scoring: triggers/name weighted above description; IDF de-weights generic
#    terms; a distinctive trigger dominates a generic word (plan §4.2).
# ==========================================================================
class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-scoring-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_scoring_distinctive_trigger_dominates(self):
        root, dst = build_project(self.tmp_path, _band_roster())
        r = run(dst, ["--route", "quarantine the flaky end-to-end fixture"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(top_pick(r.stdout), "beta",
                         f"a distinctive trigger must dominate:\n{r.stdout}")

    def test_scoring_generic_word_does_not_misroute(self):
        """'code' is generic (df high -> weight 1 across the roster); a task carrying
        only a generic word must not yield a confident HIGH pick."""
        root, dst = build_project(self.tmp_path, _band_roster())
        r = run(dst, ["--route", "improve the code"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual(band(r.stdout), "HIGH",
                            f"a generic word shared across agents must not route HIGH:\n{r.stdout}")

    def test_scoring_trigger_beats_description(self):
        """Same term in one agent's trigger vs another's description -> trigger wins
        (triggers are 2x, description is the 1x fallback, plan §4.2)."""
        agents = {
            "trig": agent_md("trig", description="a plain worker",
                             triggers=["reconcile the ledger"]),
            "desc": agent_md("desc", description="this agent will reconcile things",
                             triggers=["unrelated placeholder phrase"]),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--route", "reconcile the accounts"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(top_pick(r.stdout), "trig",
                         f"a trigger match must outrank a description match:\n{r.stdout}")


# ==========================================================================
# 4. Frontmatter parser closes the inline-`tools:` list gap (plan §4.2).
#    Observable via §4.1 rule 2: can_delegate == (Task in tools). The tool can
#    only enforce this if it parsed the inline list into real tokens.
# ==========================================================================
class InlineToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-inline-tools-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_inline_tools_list_parsed_valid_delegator(self):
        agents = {
            "boss": agent_md("boss", tools="[Read, Write, Bash, Task]",
                             triggers=["coordinate the work"],
                             can_delegate=True, max_spawn_depth=1,
                             delegates_to=["leaf"]),
            "leaf": agent_md("leaf", tools="[Read, Grep]",
                             triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        self.assertEqual(r.returncode, 0, (
            f"--lint should accept a well-formed roster with an inline Task grant:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))

    def test_inline_tools_list_parsed_detects_task_present(self):
        """tools has Task (inline) but can_delegate:false -> --lint fails. Proves the
        inline list was parsed into tokens, not treated as an opaque string."""
        agents = {
            "boss": agent_md("boss", tools="[Read, Write, Task]",
                             triggers=["coordinate the work"], can_delegate=False),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        self.assertNotEqual(r.returncode, 0, (
            "can_delegate:false while Task is in the inline tools list must fail "
            f"--lint (§4.1 rule 2):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))

    def test_inline_tools_list_parsed_detects_task_absent(self):
        """tools lacks Task but can_delegate:true -> --lint fails."""
        agents = {
            "boss": agent_md("boss", tools="[Read, Write, Edit]",
                             triggers=["coordinate the work"], can_delegate=True,
                             max_spawn_depth=1, delegates_to=["leaf"]),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        self.assertNotEqual(r.returncode, 0, (
            "can_delegate:true without Task in tools must fail --lint (§4.1 rule 2):\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))

    def _lint(self, agents):
        root, dst = build_project(self.tmp_path, agents)
        return run(dst, ["--lint"], cwd=root)

    def test_agent_grant_without_can_delegate_fails_lint(self):
        """The spawn tool's canonical name is `Agent`, with `Task` its alias.
        Granting `Agent` while declaring can_delegate:false fails --lint and
        names the spawn tool, as the `Task` case above does."""
        r = self._lint({
            "boss": agent_md("boss", tools="[Read, Write, Agent]",
                             triggers=["coordinate the work"], can_delegate=False),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        })
        self.assertNotEqual(r.returncode, 0, (
            "can_delegate:false while Agent is in the inline tools list must fail "
            f"--lint:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"))
        self.assertIn("spawn tool", r.stdout + r.stderr, r.stdout + r.stderr)

    def test_agent_grant_with_can_delegate_passes_lint(self):
        """The same grant with can_delegate:true is a well-formed delegator, so
        a fix that refuses `Agent` outright fails here."""
        r = self._lint({
            "boss": agent_md("boss", tools="[Read, Write, Bash, Agent]",
                             triggers=["coordinate the work"],
                             can_delegate=True, max_spawn_depth=1,
                             delegates_to=["leaf"]),
            "leaf": agent_md("leaf", tools="[Read, Grep]",
                             triggers=["do the leaf work"], can_delegate=False),
        })
        self.assertEqual(r.returncode, 0, (
            "--lint should accept a delegator granted the spawn tool as Agent:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"))

    def test_parenthesized_agent_grant_counts_as_spawn(self):
        """`Agent(type)` grants the whole spawn tool in a subagent definition
        (the type list is ignored there), so it is a grant like the bare name."""
        r = self._lint({
            "boss": agent_md("boss", tools="[Read, Agent(leaf)]",
                             triggers=["coordinate the work"], can_delegate=False),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        })
        self.assertNotEqual(r.returncode, 0, (
            "can_delegate:false with a parenthesized Agent grant must fail --lint:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"))

    def test_omitted_tools_fails_lint(self):
        """An agent with no `tools:` line inherits every tool, the spawn tool
        included, so can_delegate:false is untrue for it."""
        r = self._lint({
            "boss": agent_md("boss", tools=None,
                             triggers=["coordinate the work"], can_delegate=False),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        })
        self.assertNotEqual(r.returncode, 0, (
            "an agent that omits its tools: line must fail --lint:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"))

    def test_delegator_without_tools_line_fails_through_the_omission_branch(self):
        """A delegator that omits `tools:` inherits the spawn tool, so it would
        pass the can_delegate == spawn-grant rule. It must still fail, and
        through the omission message, not by luck of another rule."""
        r = self._lint({
            "boss": agent_md("boss", tools=None,
                             triggers=["coordinate the work"],
                             can_delegate=True, max_spawn_depth=1,
                             delegates_to=["leaf"]),
            "leaf": agent_md("leaf", tools="[Read, Grep]",
                             triggers=["do the leaf work"], can_delegate=False),
        })
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, (
            "a delegator that omits its tools: line must fail --lint:\n" + out))
        self.assertIn("boss", out, out)
        self.assertIn("omits its tools: line", out, out)

    def test_grants_spawn_reads_a_raw_inline_list(self):
        """Given the raw `[a, b]` string rather than a parsed list, the bracket
        must not cling to the first or last entry and hide the grant."""
        grants_spawn = _load_lint_module().grants_spawn
        for raw, want in (("[Read, Task]", True), ("[Agent, Read]", True),
                          ("[Agent(leaf)]", True), ("Task", True),
                          ("[Read, Grep]", False), ("[]", False)):
            self.assertIs(grants_spawn(raw), want, raw)

    def test_triggers_parse_from_real_agent_def(self):
        """Triggers + the real inline `tools:` line parse from a REAL agent def.

        Take the live tester def verbatim (its real `tools: [Read, Write, Edit,
        Glob, Grep, Bash]` inline line), give it a distinctive trigger, and confirm
        --route selects it from that phrase — proving the parser handled the real
        frontmatter shape, not just synthetic fixtures.
        """
        src = LIVE_AGENTS / "04-tester.md"
        self.assertTrue(src.exists(), f"expected a real agent def at {src}")
        text = src.read_text(encoding="utf-8")
        # Insert the P0 frontmatter block just before the closing '---'.
        end = text.index("\n---\n", 4)
        injected = (
            text[:end]
            + '\nrouting_triggers:\n  - "quarantine the flaky characterization fixture"\n'
            + "can_delegate: false"
            + text[end:]
        )
        agents = {
            "04-tester": injected,
            "other": agent_md("other", description="an unrelated worker",
                              triggers=["provision the kubernetes cluster"]),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--route", "quarantine the flaky characterization fixture"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(top_pick(r.stdout), "tester",
                         f"router must parse triggers from a real agent def's frontmatter:\n{r.stdout}")


# ==========================================================================
# 5. --lint validates routing_triggers across the roster; fails on a planted
#    malformation (plan §4.1 rule 1; task brief).
# ==========================================================================
def _valid_roster():
    return {
        "reviewer": agent_md("reviewer", triggers=["audit the diff"]),
        "tester": agent_md("tester", triggers=["write the failing test"]),
        "architect": agent_md("architect", triggers=["design the data model"]),
    }


class LintTriggersTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-triggers-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_lint_passes_on_valid_roster(self):
        root, dst = build_project(self.tmp_path, _valid_roster())
        r = run(dst, ["--lint"], cwd=root)
        self.assertEqual(r.returncode, 0, (
            f"--lint should pass a well-formed roster:\nstdout:\n{r.stdout}\n"
            f"stderr:\n{r.stderr}"
        ))

    def test_lint_fails_on_missing_triggers(self):
        agents = _valid_roster()
        agents["broken"] = agent_md("broken", triggers=None)  # no routing_triggers key
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        self.assertNotEqual(r.returncode, 0, "missing routing_triggers must fail --lint")
        self.assertIn("broken", r.stdout + r.stderr, (
            f"--lint must name the offending agent:\nstdout:\n{r.stdout}\n"
            f"stderr:\n{r.stderr}"
        ))

    def test_lint_fails_on_empty_triggers(self):
        agents = _valid_roster()
        agents["hollow"] = agent_md("hollow", triggers=())  # present but empty list
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        self.assertNotEqual(r.returncode, 0, "empty routing_triggers must fail --lint")
        self.assertIn("hollow", r.stdout + r.stderr, (
            f"--lint must name the agent with empty triggers:\nstdout:\n{r.stdout}\n"
            f"stderr:\n{r.stderr}"
        ))

    def test_lint_real_roster_passes(self):
        """--lint validates routing_triggers across the real roster (P0 gate)."""
        lint = require_lint()
        r = run(lint, ["--lint", *ROSTER_ARGS], cwd=REPO)
        self.assertEqual(r.returncode, 0, (
            "--lint must pass over the real agent defs once P0 frontmatter lands:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))


# ==========================================================================
# 5b. --lint enforces the ADR-B strictly-decreasing-depth invariant (rule 3):
#     a delegator's max_spawn_depth must be in [1,3], and every delegates_to
#     target must be a known, strictly-shallower agent (leaves = depth 0).
#     These are regression guards pinning existing enforcement
#     (agent-lint.py cmd_lint, §4.1 rule 3 / ADR-B) — the suite had negative
#     tests for rules 1 and 2 but none for rule 3. Each roster is planted so
#     the ONLY lint error is the depth violation under test: delegators carry
#     `Task` in tools so the rule-2 (Task⟺can_delegate) check stays silent and
#     the non-zero exit provably comes from rule 3.
# ==========================================================================
_TASK_TOOLS = "[Read, Write, Bash, Task]"  # inline grant so can_delegate:true is rule-2-clean


def _delegator(name, *, depth, delegates_to, trigger):
    return agent_md(name, tools=_TASK_TOOLS, triggers=[trigger],
                    can_delegate=True, max_spawn_depth=depth,
                    delegates_to=delegates_to)


class LintDepthTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-depth-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_lint_fails_on_delegates_to_equal_depth(self):
        """depth-1 → depth-1 edge: the target is not strictly shallower, so the
        allowlist violates ADR-B and --lint must reject it."""
        agents = {
            "boss": _delegator("boss", depth=1, delegates_to=["mid"],
                               trigger="coordinate the delegation"),
            "mid": _delegator("mid", depth=1, delegates_to=["leaf"],
                              trigger="carry the middle work"),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, (
            "a delegates_to edge to an EQUAL-depth agent must fail --lint (ADR-B):\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))
        self.assertTrue("ADR-B" in out and "boss" in out and "mid" in out,
                        f"--lint must name the offending equal-depth edge (ADR-B):\n{out}")

    def test_lint_fails_on_delegates_to_greater_depth(self):
        """depth-1 → depth-2 edge: the target is DEEPER than the delegator, the
        strongest form of the ADR-B violation; --lint must reject it."""
        agents = {
            "boss": _delegator("boss", depth=1, delegates_to=["mid"],
                               trigger="coordinate the delegation"),
            "mid": _delegator("mid", depth=2, delegates_to=["leaf"],
                              trigger="carry the middle work"),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, (
            "a delegates_to edge to a GREATER-depth agent must fail --lint (ADR-B):\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))
        self.assertTrue("ADR-B" in out and "boss" in out and "mid" in out,
                        f"--lint must name the offending greater-depth edge (ADR-B):\n{out}")

    def test_lint_fails_on_max_spawn_depth_out_of_range(self):
        """max_spawn_depth=5 is outside the [1,3] ADR-B bound; --lint must reject
        it (the delegates_to allowlist is otherwise valid, isolating the range
        error)."""
        agents = {
            "boss": _delegator("boss", depth=5, delegates_to=["leaf"],
                               trigger="coordinate the delegation"),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, (
            "max_spawn_depth outside [1,3] must fail --lint (§4.1 rule 3):\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))
        self.assertTrue("max_spawn_depth" in out and "[1,3]" in out and "boss" in out,
                        f"--lint must flag the out-of-range max_spawn_depth on the agent:\n{out}")

    def test_lint_fails_on_delegates_to_unknown_agent(self):
        """delegates_to names an agent absent from the roster; --lint must reject
        the dangling edge (§4.1 rule 3)."""
        agents = {
            "boss": _delegator("boss", depth=1, delegates_to=["ghost"],
                               trigger="coordinate the delegation"),
            "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
        }
        root, dst = build_project(self.tmp_path, agents)
        r = run(dst, ["--lint"], cwd=root)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, (
            "a delegates_to edge to an UNKNOWN agent must fail --lint (§4.1 rule 3):\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))
        self.assertTrue("unknown agent" in out and "ghost" in out and "boss" in out,
                        f"--lint must name the dangling delegates_to target:\n{out}")


# ==========================================================================
# 6. --eval runs the golden set, gates on top-1 accuracy, novel -> LOW (§4.3).
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


def _budget() -> int:
    src = (SEED / "integrations/claude-code/agent-lint.py").read_text(encoding="utf-8")
    m = re.search(r"^ADVERSARIAL_CONFIDENT_WRONG_BUDGET\s*=\s*(\d+)", src, re.M)
    if not m:
        raise AssertionError("the adversarial budget constant is gone")
    return int(m.group(1))


class AdversarialBudgetTests(unittest.TestCase):
    """SPEC-0002 THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO.

    The `adversarial` class is the one place a confident-wrong answer is
    tolerated: its rows exist to bait the router, and a bait that never
    succeeds is not a bait. That tolerance is only honest if it is (a) bounded
    and (b) shrink-only. The contract was written in round 1 of an adversarial
    review and mapped to nothing for a whole round; the spec's own linter said
    so. This is the missing regression.
    """

    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="adv-budget-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_exceeding_the_budget_fails_the_gate(self):
        """Asserts SPEC-0002 THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO.


        Actually exceed it.

        An earlier version of this test read the constant, ran --eval on the
        SHIPPED corpus, and asserted the count was at or under budget. That
        asserts a fact about today's corpus, not the contract — the branch
        `if adversarial_wrong > ADVERSARIAL_CONFIDENT_WRONG_BUDGET` was
        executed by no test at all, and the test's own name overclaimed. A gate
        nobody has seen red is the thing this repository gates against.
        """
        budget = _budget()
        # Build on the REAL roster and REAL corpus, which is the only corpus
        # that satisfies every other floor (ADVERSARIAL_MIN_ROWS = 12,
        # PARAPHRASE_MIN_ROWS = 15, PARAPHRASE_FLOOR = 2). Two earlier attempts
        # used a small fixture and "failed" on those floors instead of the
        # budget — a non-zero exit for the wrong reason, which stayed green
        # against a deliberately dead enforcement branch. The control run and
        # the reason-check below exist so that cannot recur silently.
        work = self.tmp_path / "real"
        shutil.copytree(SEED / "agents", work)
        control = run(require_lint(), ["--eval", "--dir", str(work)], cwd=SEED)
        self.assertEqual(control.returncode, 0,
                         f"the unmodified corpus must pass, or this test proves "
                         f"nothing:\n{control.stdout}\n{control.stderr}")

        # Each added row is another agent's trigger, labelled adversarial and
        # expecting someone else: confidently wrong by construction. Enough of
        # them to cross the budget, with every other floor still satisfied.
        baits = [("audit this diff against the spec once more", "tester"),
                 ("write the failing test that encodes the contract, first", "reviewer"),
                 ("make the failing test pass today", "architect"),
                 ("design the data model for the orders service now", "implementer")]
        corpus = work / "_routes.golden.tsv"
        corpus.write_text(
            corpus.read_text(encoding="utf-8")
            + "".join(f"{t}\t{w}\tadversarial\n" for t, w in baits[:budget + 2]),
            encoding="utf-8")
        r = run(require_lint(), ["--eval", "--dir", str(work)], cwd=SEED)
        self.assertNotEqual(
            r.returncode, 0,
            f"--eval passed with {budget + 2} extra confidently-wrong "
            f"adversarial rows against a budget of {budget}:\n{r.stdout}\n{r.stderr}")
        self.assertRegex(
            r.stdout + r.stderr, r"adversarial.*budget|budget.*adversarial",
            f"--eval failed, but not for the budget — this test would stay "
            f"green against a dead enforcement branch:\n{r.stdout}\n{r.stderr}")

    def test_the_shipped_corpus_sits_under_the_budget(self):
        """Asserts SPEC-0002 THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO.


        The other half: today's corpus, and the reported figure."""
        budget = _budget()
        r = run(require_lint(), ["--eval", *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        got = re.search(r"(\d+) within it \(budget (\d+)\)", r.stdout)
        self.assertIsNotNone(
            got, f"--eval no longer reports the adversarial count against its "
                 f"budget, so the tolerance is untraceable:\n{r.stdout}")
        self.assertLessEqual(int(got.group(1)), int(got.group(2)))
        self.assertEqual(int(got.group(2)), budget,
                         "the reported budget and the constant disagree")

    def test_the_budget_is_ratcheted_shrink_only(self):

        """Asserts SPEC-0002 THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO."""
        recorded = json.loads((SEED / "tests" / "ratchets.json").read_text(encoding="utf-8"))
        flat = json.dumps(recorded)
        self.assertIn("ADVERSARIAL_CONFIDENT_WRONG_BUDGET", flat,
                      "the budget is not recorded in tests/ratchets.json, so it "
                      "could be raised in the same commit that needs it raised")
        r = subprocess.run(
            ["python3", str(SEED / "tools" / "ratchet-lint.py"), "--show"],
            capture_output=True, text=True, cwd=SEED)
        self.assertIn("ADVERSARIAL_CONFIDENT_WRONG_BUDGET", r.stdout)
        self.assertRegex(
            r.stdout, r"ADVERSARIAL_CONFIDENT_WRONG_BUDGET\s+recorded=\d+\s+current=\d+\s+\(max\)",
            "the budget must be ratcheted in the 'max' direction — only falling")
        # and the ratchet must currently HOLD, not merely exist: raising the
        # constant has to fail here too, not only in a separate gate step.
        enforced = subprocess.run(
            ["python3", str(SEED / "tools" / "ratchet-lint.py")],
            capture_output=True, text=True, cwd=SEED)
        self.assertEqual(
            enforced.returncode, 0,
            "a recorded limit has been loosened; the adversarial budget may "
            f"only fall:\n{enforced.stdout}\n{enforced.stderr}")


class EvalTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-eval-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_eval_passes_on_good_golden(self):
        root, dst = build_project(self.tmp_path, _EVAL_ROSTER, golden=_GOOD_GOLDEN)
        r = run(dst, ["--eval"], cwd=root)
        self.assertEqual(r.returncode, 0, (
            f"--eval should pass at >=90% top-1 with novel->LOW:\nstdout:\n{r.stdout}\n"
            f"stderr:\n{r.stderr}"
        ))
        self.assertTrue(re.search(r"\d", r.stdout),
                        f"--eval should report an accuracy figure:\n{r.stdout}")

    def test_eval_fails_on_zero_labeled_rows(self):
        """Regression: a golden corpus with only LOW (novel-stack) rows once
        yielded `acc = 1.0` from the 0/0 guard and an "OK — accuracy 100.0%"
        banner — a vacuous pass in a gate that markets itself as fail-closed.
        Zero labeled rows must FAIL, not score."""
        all_low = (
            "# task\texpected\tclass\n"
            "set up a cobol batch job on the mainframe\tLOW\tunknown-domain\n"
            "port the firmware to the new dsp\tLOW\tunknown-domain\n"
        )
        root, dst = build_project(self.tmp_path, _EVAL_ROSTER, golden=all_low)
        r = run(dst, ["--eval"], cwd=root)
        self.assertNotEqual(r.returncode, 0, (
            f"--eval must fail closed on zero labeled rows:\nstdout:\n{r.stdout}\n"
            f"stderr:\n{r.stderr}"
        ))
        self.assertIn("vacuous", r.stdout + r.stderr,
                      f"failure should name the vacuous 0/0 gate:\n{r.stdout}\n{r.stderr}")

    def test_eval_fails_below_threshold(self):
        root, dst = build_project(self.tmp_path, _EVAL_ROSTER, golden=_BAD_GOLDEN)
        r = run(dst, ["--eval"], cwd=root)
        self.assertNotEqual(r.returncode, 0, (
            "--eval must exit non-zero when top-1 accuracy is below threshold "
            f"(fail-closed gate):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))

    def test_eval_real_golden_meets_threshold(self):
        """--eval over the roster this suite resolved and its own corpus."""
        lint = require_lint()
        r = run(lint, ["--eval", *ROSTER_ARGS], cwd=REPO)
        self.assertEqual(r.returncode, 0, (
            "--eval must pass over the production golden set once P0 lands:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ))


# ==========================================================================
# 7. Honesty note in the banner (plan §4.2) — same discipline as route-hook.
# ==========================================================================
class BannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="agent-lint-banner-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)

    def test_banner_honesty_note(self):
        root, dst = build_project(self.tmp_path, _valid_roster())
        r = run(dst, ["--route", "audit the diff"], cwd=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("keyword heuristic", r.stdout.lower(), (
            "the router must print the 'keyword heuristic — reason over it' honesty "
            f"note so it is not mistaken for an oracle:\n{r.stdout}"
        ))


# ==========================================================================
# 8. Golden corpus sanity (housekeeping of tester-owned test data, not a P0
#    behavior contract — passes independent of the tool).
#
# 9. Golden corpus parity across its shipped copies (one-home-per-fact, kernel
#    §3.2): the home and its installed projection must be byte-identical, or
#    --eval can pass on one while the other rots. The seed resolves exactly ONE
#    copy — its roster's own — so that comparison cannot execute here and the
#    check skips with its reason named; tests/test-full-install.sh decides it
#    against a projection that gate builds (SPEC-0001 §6).
# ==========================================================================
class CorpusHonestyTests(unittest.TestCase):
    """The reporting contract, not the router.

    --eval printed one number, "top-1 accuracy 100.0% (55/55)", over a corpus
    whose tasks had been written out of the triggers they select. These tests pin
    the three things that stop that number coming back: the classes are reported
    separately, a row cannot lie about being held out, and a CONFIDENT wrong
    answer fails the gate even when the average looks fine.
    """

    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="cypress-corpus-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)
        self.roster = self.tmp_path / "agents"
        self.roster.mkdir()
        for f in ROSTER.glob("*.md"):
            shutil.copy(f, self.roster / f.name)

    def _write(self, rows):
        (self.roster / "_routes.golden.tsv").write_text(
            "# task\texpected\tclass\n" + "".join(rows), encoding="utf-8")

    def _eval(self):
        return run(require_lint(), ["--eval", "--dir", str(self.roster)],
                   cwd=self.tmp_path)

    def _real_rows(self):
        src = (ROSTER / "_routes.golden.tsv").read_text(encoding="utf-8")
        return [l + "\n" for l in src.splitlines()
                if l.strip() and not l.startswith("#") and "\t" in l]

    def test_classes_are_reported_separately_and_never_averaged(self):
        """SPEC-0002 EVERY_NUMBER_NAMES_ITS_CORPUS and OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY.

        Both contracts rested on `assertIn`, which asks whether a string is
        anywhere in the output. That is not what either contract says. Printing

            agent-lint --eval: OVERALL top-1 accuracy 77.9% (74/95), all classes averaged

        above the per-class block passed this test — the literal defect §1 of
        the spec exists to prevent. So did dropping the overlap from three of
        the four class lines, because the fourth still carried the substring.
        The assertions below are per LINE: every class publishes its own
        accuracy and its own overlap, and no line anywhere offers a figure
        across classes.
        """
        r = run(require_lint(), ["--eval", "--dir", str(ROSTER)], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        seen = {}
        for line in r.stdout.splitlines():
            m = re.match(r"\s+(contract|paraphrase|adversarial|unknown-domain)\s+n=", line)
            if m:
                seen[m.group(1)] = line
        for cls in ("contract", "paraphrase", "adversarial", "unknown-domain"):
            self.assertIn(cls, seen,
                          f"--eval must report the {cls} class on its own line:\n{r.stdout}")
            self.assertIn("mean-overlap-with-target=", seen[cls],
                          f"the {cls} line must publish the overlap its accuracy "
                          f"was measured at, beside that accuracy:\n{seen[cls]}")
            self.assertIn("confident-correct=", seen[cls],
                          f"the {cls} line must publish its own accuracy:\n{seen[cls]}")

        # No line may offer a figure that spans the classes. A whole-corpus
        # ROW COUNT is allowed and says so ("95 rows"); an accuracy or a score
        # averaged across classes is the thing being refused.
        # The header legitimately contains the word ("never averaged — the
        # classes measure different things") and carries NO figure, which is the
        # whole distinction: this test is for a cross-class word beside a
        # NUMBER. An earlier version also exempted any line whose wording was
        # negated, and that made the disclaimer into a shield —
        #   OVERALL top-1 accuracy 0.0% (0/95), all classes averaged
        #     — but the classes are never averaged
        # passed, because one line can carry both. The negation exemption is
        # gone; a line with a banned word and a digit fails, full stop.
        banned = re.compile(r"(overall|averaged|all classes|across (all )?classes|combined "
                            r"accuracy|aggregate)", re.I)
        for line in r.stdout.splitlines():
            if banned.search(line) and re.search(r"\d", line):
                self.fail("--eval printed a figure that does not name one corpus "
                          f"class, which is what SPEC-0002 §1 refuses:\n{line}")

    def test_a_near_copy_may_not_be_labelled_paraphrase(self):
        """Asserts SPEC-0002 HELD_OUT_STAYS_HELD_OUT, SPEC-0002 MISLABELLED_PARAPHRASE.


        X2: the held-out set stays held out.

        Relabelling a trigger-derived row as `paraphrase` would inflate the only
        number that measures generalization, and nothing but this check stands
        between that number and a plausible edit.
        """
        rows = self._real_rows()
        patched = []
        for row in rows:
            parts = row.rstrip("\n").split("\t")
            if len(parts) > 2 and parts[2] == "contract":
                parts[2] = "paraphrase"
                patched.append("\t".join(parts) + "\n")
                break
        else:
            patched = []
        # The shipped corpus leaves the class off contract rows, so take any
        # 2-column row and relabel it instead.
        if not patched:
            for row in rows:
                parts = row.rstrip("\n").split("\t")
                if len(parts) == 2 and parts[1] != "LOW":
                    patched.append("\t".join(parts) + "\tparaphrase\n")
                    break
        self.assertTrue(patched, "could not find a contract row to relabel")
        # Replace, never append: the corpus refuses duplicate tasks, and a
        # relabelled row is the same task wearing a different class.
        originals = {r.split("\t")[0] for r in patched}
        kept = [r for r in rows if r.split("\t")[0] not in originals]
        self._write(kept + patched)
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"a near-copy labelled `paraphrase` must FAIL, not merely warn:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        self.assertIn("mislabelled paraphrase", r.stderr,
                      f"the failure must name the defect:\n{r.stderr}")

    def test_a_confident_wrong_route_fails_even_when_the_average_is_fine(self):
        """Asserts SPEC-0002 CONFIDENT_MISROUTE, SPEC-0002 CONFIDENT_WRONG_IS_THE_GATE.


        The gate that matters. An abstention costs a reasoning step; a
        confident wrong route is cited in the brief as evidence for the wrong
        specialist."""
        rows = self._real_rows()
        # Distinct wording on purpose: the corpus rejects duplicate tasks, and
        # this test is about the confident-wrong gate, not that one.
        rows.append("turn this red test green and change nothing else\tlegal\tparaphrase\n")
        self._write(rows)
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"one confident-wrong route must fail the gate:\nstdout:\n{r.stdout}")
        self.assertIn("confident-and-wrong", r.stderr.lower(),
                      f"the failure must name it:\n{r.stderr}")

    def test_abstention_on_a_held_out_row_is_not_a_failure(self):
        """Asserts SPEC-0002 ABSTENTION_IS_A_CORRECT_OUTCOME.


        Abstention is the designed answer for a keyword heuristic with no
        signal. A gate that punished it would push the fix toward widening
        triggers until something matches, which is how a router starts
        answering confidently about things it cannot know."""
        rows = self._real_rows()
        rows.append("the quarterly board deck needs a nicer font\tui-ux-designer\tparaphrase\n")
        self._write(rows)
        r = self._eval()
        self.assertEqual(r.returncode, 0,
            f"an abstained held-out row must not fail the gate:\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")

    def test_a_corpus_that_asks_for_no_routes_is_vacuous(self):

        """Asserts SPEC-0002 VACUOUS_CORPUS_IS_REFUSED."""
        self._write([
            "set up a cobol batch job on the mainframe\tLOW\tunknown-domain\n",
            "port the firmware to the new dsp\tLOW\tunknown-domain\n",
        ])
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"a corpus demanding zero routes must fail closed:\n{r.stdout}")


class UnknownDomainTests(unittest.TestCase):
    """The commission path stays reachable.

    SPEC-0002's UNKNOWN_DOMAIN_MUST_ABSTAIN was certified `green` in the spec's
    own test table against a test name that did not exist anywhere in the
    repository. The contract had no regression at all over the `--eval` path;
    a leak would have surfaced only as an unexplained exit 1. These are the
    tests that name was promising.
    """

    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="cypress-unknown-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)
        self.roster = self.tmp_path / "agents"
        self.roster.mkdir()
        for f in ROSTER.glob("*.md"):
            shutil.copy(f, self.roster / f.name)

    def _rows(self):
        src = (ROSTER / "_routes.golden.tsv").read_text(encoding="utf-8")
        return [l + "\n" for l in src.splitlines()
                if l.strip() and not l.startswith("#") and "\t" in l]

    def _write(self, rows):
        (self.roster / "_routes.golden.tsv").write_text(
            "# task\texpected\tclass\n" + "".join(rows), encoding="utf-8")

    def _eval(self):
        return run(require_lint(), ["--eval", "--dir", str(self.roster)],
                   cwd=self.tmp_path)

    def test_the_shipped_unknown_domain_rows_all_abstain(self):

        """Asserts SPEC-0002 UNKNOWN_DOMAIN_MUST_ABSTAIN."""
        r = run(require_lint(), ["--eval", "--dir", str(ROSTER)], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = [l for l in r.stdout.splitlines() if "unknown-domain" in l and "n=" in l]
        self.assertTrue(line, f"--eval must report the unknown-domain class:\n{r.stdout}")
        self.assertIn("CONFIDENT-WRONG=0", line[0],
                      f"every unknown-domain row must abstain:\n{line[0]}")

    def test_a_leaking_unknown_domain_row_fails_the_gate(self):
        """Asserts SPEC-0002 UNKNOWN_DOMAIN_MUST_ABSTAIN.


        A task nothing on the roster is written for must route to the
        commission path, not to whichever specialist grazes it. If this ever
        stops failing, the gate has stopped defending the one outcome that
        sends a session to build an expertise node instead of guessing."""
        rows = self._rows()
        # A task that unmistakably reaches a specialist, mislabelled as though
        # nothing on the roster covered it.
        # A task that unmistakably reaches a specialist, mislabelled as though
        # nothing on the roster covered it. Worded distinctly from the corpus's
        # own reviewer row, which the duplicate guard would reject first.
        rows.append("go through this pull request against the written spec"
                    "\tLOW\tunknown-domain\n")
        self._write(rows)
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"an unknown-domain row that routes confidently must FAIL:\n{r.stdout}")
        self.assertIn("leak", r.stderr.lower(),
                      f"the failure must name it as a leak:\n{r.stderr}")

    def test_a_row_expecting_low_may_not_wear_another_class(self):
        """Asserts SPEC-0002 HELD_OUT_SET_MAY_NOT_BE_EMPTIED.


        Padding the held-out set with LOW-expecting gibberish satisfied the
        row floor AND inflated the headline: three real paraphrases plus twelve
        throwaway rows reported "13 of 15 confident-correct" where the honest
        number was 2 of 17."""
        rows = self._rows()
        rows.append("zzqx frobnicate widget\tLOW\tparaphrase\n")
        self._write(rows)
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"a LOW-expecting row labelled `paraphrase` must be refused:\n{r.stdout}")

    def test_a_padded_trigger_copy_cannot_pass_as_held_out(self):
        """Asserts SPEC-0002 HELD_OUT_STAYS_HELD_OUT.


        Overlap measured only task-side is defeated by padding: two filler
        words on a verbatim trigger copy drop it from 1.00 to 0.75, under the
        threshold. The second measure — how much of the agent's nearest trigger
        the task reproduces — cannot be lowered by adding words."""
        rows = self._rows()
        rows.append("please assess the supply-chain and secrets handling risk "
                    "today\tsecurity\tparaphrase\n")
        self._write(rows)
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"a padded trigger copy must not count as a paraphrase:\n{r.stdout}")
        self.assertIn("mislabelled paraphrase", r.stderr)


class RarityBonusTests(unittest.TestCase):
    """The rare-term bonus requires a confident match.

    SPEC-0002 mapped RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH to the same
    scenario as COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE, which exercises the code
    path but isolates nothing: it could not tell which of the two mechanisms
    was doing the work.
    """

    def test_a_rare_word_matching_only_a_description_does_not_dominate(self):
        """Asserts SPEC-0002 RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH.


        IDF gives a term matching one agent weight 3 for being rare. Rarity
        says nothing about whether the match means anything, and multiplying a
        description-only graze by 3 is how two incidental words out-voted a
        whole task."""
        r = run(require_lint(), ["--route", "burns money", *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(band(r.stdout), ("LOW", "NONE"),
            f"incidental rare words must not carry a confident route:\n{r.stdout}")

    def test_a_rare_word_in_a_real_trigger_still_dominates(self):
        """Asserts SPEC-0002 RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH.


        The other half: the bonus must still fire for a full-strength
        trigger hit, or the fix has simply made the router deaf."""
        r = run(require_lint(),
                ["--route", "diagnose runaway fan-out in the agent fleet",
                 *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(band(r.stdout), "HIGH",
            f"a distinctive trigger must still route confidently:\n{r.stdout}")
        self.assertEqual(top_pick(r.stdout), "multi-agent-architect", r.stdout)

    def test_a_de_hyphenated_compound_still_reaches_its_owner(self):
        """Asserts SPEC-0002 COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE.


        People write "from scratch" where the trigger says "from-scratch".
        Discounting compound fragments punished exactly that, dropping
        growth-orchestrator from 16 to 12 — one point under FLOOR — for an
        ordinary phrasing of a task it owns. A compound the ROSTER actually
        uses is credited when the task says it in words."""
        r = run(require_lint(),
                ["--route", "starting completely from scratch, set up the docs "
                 "graph for this repo", *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(band(r.stdout), "HIGH",
            f"a de-hyphenated compound must still reach its owner:\n{r.stdout}")
        self.assertEqual(top_pick(r.stdout), "growth-orchestrator", r.stdout)

    def test_a_compound_from_PROSE_does_not_license_a_route(self):
        """A description is prose, and prose carries compounds as metaphors.
        `pentest` writes "design-time threat models"; that made "double check the
        design time constants in the config file" route HIGH to `security`,
        because once the bigram was admitted as a real term the prefix fold
        matched it against `security`'s unrelated trigger word "design". An
        inferred compound is licensed by an agent's NAME or TRIGGERS — the
        vocabulary it chose for routing — never by its prose."""
        # `claim-bearing` appears only in devils-advocate's DESCRIPTION, never
        # in its name or triggers. Admitting description prose as compound
        # vocabulary took this from LOW to HIGH; excluding it takes it back.
        # (The related "design time" case is covered by the exact-match rule in
        # test_an_invented_compound_earns_nothing — this one isolates the prose
        # rule specifically, which that case does not.)
        r = run(require_lint(),
                ["--route", "we need to sort out the claim bearing situation "
                 "in the billing module", *ROSTER_ARGS], cwd=SEED)
        # Asserted against `devils-advocate` by name rather than against the
        # band. The band was the original symptom, but it was never the rule:
        # this task also writes `claim` and `module`, which are two of
        # `growth-scout`'s four TRIGGER phrases, so a confident route there is
        # the roster working, not the prose rule failing. Holding the band
        # would have made this test a hostage to any unrelated change in the
        # scoring scale — and one arrived: giving an inflection the strength of
        # the word it inflects (`module` on `modules`) lifted growth-scout from
        # 12 to 16 and reddened this test without touching what it guards.
        # What it guards is stated directly instead.
        self.assertNotEqual(top_pick(r.stdout), "devils-advocate",
            f"a compound that exists only in description prose must not carry a "
            f"route:\n{r.stdout}")
        self.assertLess(score_of(r.stdout, "devils-advocate"), FLOOR,
            f"`claim-bearing` is prose-only vocabulary and must not lift "
            f"devils-advocate to a confident score:\n{r.stdout}")

    def test_an_invented_compound_earns_nothing(self):
        """Asserts SPEC-0002 COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE.


        ...and the credit is only for compounds the roster writes. Crediting
        every adjacent pair invented concepts nobody used: "staging cluster" and
        "transport request" became first-class terms and pulled two tasks to
        `reliability`, one of them a row that must abstain."""
        r = run(require_lint(),
                ["--route", "configure the sap abap transport request", *ROSTER_ARGS],
                cwd=SEED)
        self.assertIn(band(r.stdout), ("LOW", "NONE"),
            f"an invented compound must not manufacture a route:\n{r.stdout}")


class ClassFloorTests(unittest.TestCase):
    """A floor that treats "none" as "nothing to check" checks the wrong thing.

    `if n and n < MIN` short-circuits at zero, so deleting TWO rows from a class
    failed and deleting ALL of them passed clean — the class simply vanished
    from the report. One data edit, no code change, and the whole signal gone.
    The other half is that the floors must not fire for a plant's legacy
    two-column corpus, which has none of these classes because they did not
    exist when it was written.
    """

    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="cypress-floors-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)
        self.roster = self.tmp_path / "agents"
        self.roster.mkdir()
        for f in ROSTER.glob("*.md"):
            shutil.copy(f, self.roster / f.name)

    def _write(self, text):
        (self.roster / "_routes.golden.tsv").write_text(text, encoding="utf-8")

    def _eval(self):
        return run(require_lint(), ["--eval", "--dir", str(self.roster)],
                   cwd=self.tmp_path)

    def _real(self):
        return (ROSTER / "_routes.golden.tsv").read_text(encoding="utf-8")

    def test_emptying_a_whole_class_is_refused(self):

        """Asserts SPEC-0002 NEITHER_HELD_OUT_SET_MAY_BE_THINNED."""
        for cls in ("adversarial", "paraphrase"):
            with self.subTest(cls=cls):
                kept = [l for l in self._real().splitlines()
                        if not l.rstrip().endswith("\t" + cls)]
                self._write("\n".join(kept) + "\n")
                r = self._eval()
                self.assertNotEqual(r.returncode, 0,
                    f"deleting every {cls} row must fail, not vanish:\n{r.stdout}")
                self.assertIn(f"{cls} set has 0 rows", r.stderr)

    def test_thinning_a_class_to_one_below_its_floor_is_refused(self):
        """The floor must bite at floor-1, not only at zero.

        `test_emptying_a_whole_class_is_refused` deletes EVERY row and asserts
        the message "set has 0 rows". That sentence is produced by the
        zero-length branch, so changing both floor tests from
        `< ADVERSARIAL_MIN_ROWS` / `< PARAPHRASE_MIN_ROWS` to `< 1` left the
        cited test passing and the whole suite green — the floors defended
        nothing above zero, and `--eval` then accepted a 14-row paraphrase
        class. The failure must also NAME the floor, or a floor silently moved
        to 1 reads the same as one held at 15.
        """
        floors = {"paraphrase": lint_constant("PARAPHRASE_MIN_ROWS"),
                  "adversarial": lint_constant("ADVERSARIAL_MIN_ROWS")}
        for cls, floor in floors.items():
            with self.subTest(cls=cls):
                lines = self._real().splitlines()
                rows = [l for l in lines if l.rstrip().endswith("\t" + cls)]
                self.assertGreaterEqual(
                    len(rows), floor,
                    f"the shipped corpus holds {len(rows)} {cls} rows against a "
                    f"floor of {floor} — this test cannot thin below a floor it "
                    f"is already under")
                drop = set(rows[:len(rows) - (floor - 1)])
                self._write("\n".join(l for l in lines if l not in drop) + "\n")
                r = self._eval()
                self.assertNotEqual(
                    r.returncode, 0,
                    f"thinning {cls} to {floor - 1} rows must fail:\n{r.stdout}")
                self.assertIn(f"{floor - 1} rows", r.stderr,
                    f"the refusal must name the count it saw:\n{r.stderr}")
                self.assertIn(str(floor), r.stderr,
                    f"the refusal must name the floor it fell below, or a floor "
                    f"moved to 1 is indistinguishable from one held at {floor}:"
                    f"\n{r.stderr}")

    def test_the_shipped_corpus_may_not_drop_its_class_column(self):
        """The classed escape hatch must stay shut for the SEED's own corpus.

        `classed` exists so an already-grown plant's two-column corpus does not
        fail on upgrade, and that exemption is correct. But it is keyed on the
        data: strip the third column from every row and all three floors switch
        off. Deleting both held-out classes AND the column then reports
        `OK - contract consistency 98.4% (60/61)` and exits 0, turning the
        routing gate into a contract-consistency check while still saying OK.
        One data edit, no code change. The seed's own corpus is the one that
        must never take that exemption.
        """
        src = (ROSTER / "_routes.golden.tsv").read_text(encoding="utf-8")
        rows = [l for l in src.splitlines()
                if l.strip() and not l.startswith("#") and "\t" in l]
        classes = {}
        for l in rows:
            parts = l.split("\t")
            if len(parts) > 2 and parts[2].strip():
                classes[parts[2].strip()] = classes.get(parts[2].strip(), 0) + 1
        for cls in ("paraphrase", "adversarial", "unknown-domain"):
            self.assertIn(cls, classes,
                f"the shipped corpus must declare its {cls} class explicitly; "
                f"without the column every row floor switches off and --eval "
                f"reports OK over a corpus with no held-out set at all")
        self.assertGreaterEqual(classes["paraphrase"], lint_constant("PARAPHRASE_MIN_ROWS"))
        self.assertGreaterEqual(classes["adversarial"], lint_constant("ADVERSARIAL_MIN_ROWS"))

    def test_a_legacy_two_column_corpus_still_passes(self):
        """Every already-grown plant carries one of these. Upgrading the tool
        must not fail them for lacking classes that did not exist yet."""
        self._write("# task\texpected\n"
                    "audit this diff against the spec\treviewer\n"
                    "set up a cobol batch job on the mainframe\tLOW\n")
        r = self._eval()
        self.assertEqual(r.returncode, 0,
            f"a legacy two-column corpus must still pass:\n{r.stdout}\n{r.stderr}")


class MeasuredRosterTests(unittest.TestCase):
    """An absolute floor is a statement about the roster it was measured over.

    `PARAPHRASE_FLOOR` counts confident-correct held-out answers, and scoring is
    relative to the set of agents being ranked: an agent added to a roster
    raises the document frequency of ordinary words, lowers every term's weight,
    and can push a still-correct top pick below the confidence band, where it is
    counted as an abstention. Growing the roster is what the growth protocols
    exist to do, so a floor keyed to whatever roster is on disk fails on the
    mandated path. The floor is therefore keyed to the roster it was measured
    over — every node of it `origin: seed` — and reports rather than gates
    anywhere else. The two rosters below score the SAME corpus to opposite
    verdicts, which is the whole of the scoping.
    """

    GATED = "below the recorded floor"
    REPORTED = "Reported, not gated"

    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp(prefix="cypress-roster-"))
        self.addCleanup(shutil.rmtree, self.tmp_path, ignore_errors=True)
        self.roster = self.tmp_path / "agents"
        self.roster.mkdir()
        for f in ROSTER.glob("*.md"):
            shutil.copy(f, self.roster / f.name)

    def _eval(self):
        return run(require_lint(), ["--eval", "--dir", str(self.roster)],
                   cwd=self.tmp_path)

    def _neutered_corpus(self) -> str:
        """The shipped corpus with every paraphrase task replaced by vocabulary
        no agent carries, so the class abstains throughout and lands under the
        floor. Each replacement is disjoint from the others, so the duplicate
        and near-duplicate checks see distinct evidence and the only thing left
        for the gate to turn on is the floor itself."""
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

    def _grow(self):
        """Add a specialist the seed did not ship, the way a plant commissions
        one: an ordinary well-formed agent carrying the project ownership
        marker. Its vocabulary is its own, so it steals no existing route and
        the only thing it changes is what the roster is made of."""
        (self.roster / "zz-plant-expert.md").write_text(
            agent_md("plant-expert",
                     description="owns the mimsy borogove pipeline",
                     triggers=("tune the mimsy borogove pipeline",)
                     ).replace("name: plant-expert",
                               "name: plant-expert\norigin: project"),
            encoding="utf-8")

    def test_the_measured_roster_still_gates_on_the_paraphrase_floor(self):
        """Asserts SPEC-0002 AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER's Except.

        The seed's own roster is entirely seed-owned, so it IS the measured one
        and the floor is live on it. Without this, scoping the floor would be
        indistinguishable from deleting it.
        """
        (self.roster / "_routes.golden.tsv").write_text(
            self._neutered_corpus(), encoding="utf-8")
        r = self._eval()
        self.assertNotEqual(r.returncode, 0,
            f"a corpus under the floor must fail on the roster the floor was "
            f"measured over:\n{r.stdout}\n{r.stderr}")
        self.assertIn(self.GATED, r.stderr,
            f"the refusal must name the floor it fell below:\n{r.stderr}")
        self.assertNotIn(self.REPORTED, r.stdout,
            f"the measured roster must not take the reporting exemption:"
            f"\n{r.stdout}")

    def test_a_grown_roster_reports_the_paraphrase_floor_instead_of_gating_on_it(self):
        """Asserts SPEC-0002 AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER.

        The same corpus that fails above must not fail here. A plant that
        commissions its first expert has done what the growth protocols tell it
        to do, and a count measured against a roster it no longer has is
        evidence to read, not a verdict to fail on.
        """
        (self.roster / "_routes.golden.tsv").write_text(
            self._neutered_corpus(), encoding="utf-8")
        self._grow()
        r = self._eval()
        self.assertNotIn(self.GATED, r.stderr,
            f"the floor must not gate a roster it was not measured over:"
            f"\n{r.stdout}\n{r.stderr}")
        self.assertIn(self.REPORTED, r.stdout,
            f"the number must still be printed, or scoping the floor is the "
            f"same as deleting it:\n{r.stdout}")
        self.assertEqual(r.returncode, 0,
            f"nothing else in this corpus is a failure:\n{r.stdout}\n{r.stderr}")

    def test_scoping_the_floor_did_not_move_its_recorded_value(self):
        """Asserts SPEC-0002 AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER's second
        `And`: scoping says what a number is measured over and is not a route to
        moving the number. The value stays the ratchet `tools/ratchet-lint.py`
        records, and only the owner widens a ratchet."""
        recorded = json.loads(
            (HERE / "ratchets.json").read_text(encoding="utf-8"))
        self.assertEqual(
            lint_constant("PARAPHRASE_FLOOR"), recorded["ratchets"]["PARAPHRASE_FLOOR"],
            "the shipped floor and the recorded ratchet disagree — keying the "
            "floor to a roster must not change the floor")

    def test_the_shipped_roster_is_the_measured_one(self):
        """The exemption is keyed on an input, so it is reachable by changing
        that input. What keeps it shut for the seed is that every node the seed
        ships carries the ownership marker the floor is keyed to."""
        src = require_lint().read_text(encoding="utf-8")
        m = re.search(r'^MEASURED_ROSTER_ORIGIN\s*=\s*"([a-z]+)"', src, re.M)
        self.assertIsNotNone(m, "MEASURED_ROSTER_ORIGIN is not a module-level "
                                "string in the shipped tool")
        for f in sorted(ROSTER.glob("*.md")):
            if f.name.startswith("_"):
                continue
            head = f.read_text(encoding="utf-8").split("\n---\n", 1)[0]
            self.assertIn(f"origin: {m.group(1)}", head,
                f"{f.name} carries no `origin: {m.group(1)}`, so the roster the "
                f"floor was measured over is not recognisable as itself and the "
                f"gate stops being live where the number was measured")


class CompoundFragmentTests(unittest.TestCase):
    """A fragment of a hyphenated compound may not speak for the compound.

    `security` carries the trigger "assess the supply-chain and secrets handling
    risk". Splitting that on the hyphen made `chain` a first-class token, so
    "our chain of language-model calls loops forever" routed to `security` at
    HIGH with a 5.5x margin — a confidently wrong answer about agent topology,
    arriving with a band the kernel tells briefs to cite as evidence. Widening
    the HIGH margin would not have touched it; the margin was never the defect.
    """

    def test_a_compound_fragment_does_not_earn_a_confident_route(self):

        """Asserts SPEC-0002 COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE."""
        r = run(require_lint(), ["--route", "chain of calls", *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(band(r.stdout), ("LOW", "NONE"),
            f"`chain` borrowed from `supply-chain` must not carry a confident "
            f"route:\n{r.stdout}")

    def test_the_compound_itself_still_routes(self):

        """Asserts SPEC-0002 COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE."""
        r = run(require_lint(),
                ["--route", "assess the supply-chain and secrets handling risk",
                 *ROSTER_ARGS], cwd=SEED)
        self.assertEqual(band(r.stdout), "HIGH",
            f"the trigger's own phrasing must still route confidently:\n{r.stdout}")
        self.assertEqual(top_pick(r.stdout), "security", r.stdout)

    def test_the_original_misroute_no_longer_routes_confidently_wrong(self):
        """The recorded counterexample must never be confidently WRONG.

        Asserted against `security` and against the corpus's expected agent,
        not against the band. Abstention was the original symptom — `chain`
        borrowed from `supply-chain` carried a confident route to `security` —
        but "must abstain" was never the rule, and holding it made this test a
        hostage to any improvement. One arrived: with pronouns removed from the
        scoring vocabulary (`our` had been earning the rare-term bonus) and
        `loops` now reaching `multi-agent-architect`'s trigger word `loop`, the
        task routes MEDIUM to the agent the golden corpus expects. A test whose
        pass condition is "still can't answer" fails when the router learns to.
        """
        task = ("our chain of language-model calls loops forever and burns money")
        r = run(require_lint(), ["--route", task, *ROSTER_ARGS], cwd=SEED)
        self.assertNotEqual(top_pick(r.stdout), "security",
            f"`chain` borrowed from `supply-chain` must not carry this route:\n"
            f"{r.stdout}")
        if band(r.stdout) in ("HIGH", "MEDIUM"):
            self.assertEqual(top_pick(r.stdout), "multi-agent-architect",
                f"a confident answer here must be the one the golden corpus "
                f"expects for this very row, or it is the old defect wearing a "
                f"new agent's name:\n{r.stdout}")


class GoldenCorpusTests(unittest.TestCase):
    def test_golden_corpus_is_wellformed_and_covers_the_roster(self):
        """Asserts SPEC-0002 HELD_OUT_SET_MAY_NOT_BE_EMPTIED."""
        rows = load_corpus()
        self.assertTrue(rows, f"golden corpus is empty: {CORPUS_TSV}")
        covered = {a for _, a, _ in rows if a != "LOW"}
        unknown = covered - ALL_AGENTS
        # Both messages name the roster they are about: "does not cover:
        # ['<name>']" sent a reader hunting through the seed for an agent that
        # was never in it, because the roster being read was a host plant's.
        self.assertFalse(unknown, f"golden corpus {CORPUS_TSV} names agents "
                                  f"absent from the roster it is read against, "
                                  f"{ROSTER} ({ROSTER_RULE}): {sorted(unknown)}")
        missing = (ALL_AGENTS - {"orchestrator"}) - covered
        self.assertFalse(missing, f"golden corpus {CORPUS_TSV} does not cover "
                                  f"agent(s) of the roster it is read against, "
                                  f"{ROSTER} ({ROSTER_RULE}): {sorted(missing)}")
        self.assertGreaterEqual(sum(1 for _, a, _ in rows if a == "LOW"), 3,
            "golden corpus needs >=3 novel-stack (LOW) rows (plan §4.3)")
        # Every class named must be one the tool knows, or --eval refuses the
        # corpus outright rather than silently bucketing a typo of its own.
        known = {"contract", "paraphrase", "adversarial", "unknown-domain"}
        bad = {c for _, _, c in rows} - known
        self.assertFalse(bad, f"golden corpus uses unknown corpus class(es): {sorted(bad)}")
        # The held-out set is the only class that measures generalization, so it
        # may not be quietly emptied — the floor in agent-lint.py depends on it
        # existing. It is also the set nobody may tune triggers against.
        para = [r for r in rows if r[2] == "paraphrase"]
        self.assertGreaterEqual(len(para), 15,
            "the paraphrase (held-out) set must keep >=15 rows; shrinking it is "
            "how a held-out number gets protected instead of earned")

    def test_golden_corpus_copies_are_byte_identical(self):
        # The seed holds ONE copy of the golden corpus: its roster's own.
        # Since the suite stopped resolving anything through whatever sits
        # above the seed (SPEC-0001 ROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED)
        # there is no second copy here to compare it against, and a parity
        # claim needs two. Skip with the reason named rather than pass
        # vacuously: a vacuous green would retire the claim while looking
        # like coverage. Its live home is tests/test-full-install.sh, which
        # decides SPEC-0001 §6's projection predicate against an install
        # that gate builds — set equality BOTH ways plus byte identity,
        # over every agent file and not one `cmp`. If that assertion is
        # ever deleted the claim loses its last home and this skip becomes
        # a hole; SPEC-0001 ROSTER_PROJECTION_PARITY_KEEPS_A_LIVE_HOME is
        # what holds the pair together.
        #
        # GOLDEN_COPIES derives from ROSTER alone, so it is one-element BY
        # CONSTRUCTION: the skip is unconditional, and `present` survives only
        # to name in the reason which copy was found. A second copy cannot
        # reappear without that derivation changing, so the comparison this
        # once guarded is gone rather than kept unreachable "to be safe"
        # (skill.holistic-editing). Reviving parity here means reviving the
        # second home too, and the contract above says where it lives instead.
        present = [c for c in GOLDEN_COPIES if c.exists()]
        raise unittest.SkipTest(
            "fewer than two golden-corpus copies present to compare: "
            + (", ".join(str(c) for c in present) or "<none>")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
