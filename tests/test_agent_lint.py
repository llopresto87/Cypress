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
public-interface test per the tester charter. Stdlib + pytest only; no deps.

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

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# --------------------------------------------------------------------------
# Locations pinned by the plan.
# --------------------------------------------------------------------------
# Paths are derived from this test file's own location so the suite is
# project-agnostic and portable — no absolute or host-specific path is baked in.
HERE = Path(__file__).resolve().parent   # <seed>/tests
SEED = HERE.parent                        # the seed root (this repo)
REPO = SEED.parent                        # the host project the seed is installed into, if any

# The tool: prefer the live install (where --route/--eval actually run in a
# session, plan §4.2/§5); fall back to the seed source. Either satisfies RED.
AGENT_LINT_CANDIDATES = [
    REPO / ".claude" / "agent-lint.py",
    SEED / "integrations" / "claude-code" / "agent-lint.py",
]
# The roster's HOME is the seed's own agents/ directory; REPO/.claude/agents is
# only a harness PROJECTION of it, and it exists solely when the seed happens to
# be installed into its own parent directory. Resolving the roster to the
# projection alone made this whole suite pass in that one layout and fail in a
# standalone seed checkout — which is how the seed itself is worked on
# (CLAUDE.md: "this repository IS the seed"). Prefer the projection when it is
# really there (it exercises the installed path), else fall back to the home.
ROSTER = next(
    (p for p in (REPO / ".claude" / "agents", SEED / "agents") if p.is_dir()),
    SEED / "agents",
)
LIVE_AGENTS = ROSTER

# The golden routing corpus has ONE home: the seed's agents/ dir. install.sh
# copies it to .claude/agents/ as a projection. This suite reads the home
# directly — it used to keep a third copy under tests/agent_router/, which is a
# second home by definition and had already drifted (its header still claimed
# "13 agent defs" while the roster had grown well past that). Parity between
# home and installed projection is asserted in tests/test-full-install.sh,
# where a projection actually exists.
CORPUS_TSV = SEED / "agents" / "_routes.golden.tsv"
GOLDEN_COPIES = list(dict.fromkeys([
    REPO / ".claude" / "agents" / "_routes.golden.tsv",
    CORPUS_TSV,
]))

# Tests that exercise the REAL roster pin it explicitly. Relying on the tool's
# walk-up discovery made them pass only when the seed sat inside an installed
# plant. (Planted-malformation tests must NOT use this — walk-up from their own
# tmp project root is exactly what they are testing.)
ROSTER_ARGS = ["--dir", str(ROSTER)]

# Mirrors the frontmatter `name:` of every file in agents/ (seed-lint.py owns
# the roster<->manifest<->kernel agreement; this set only keeps the golden
# corpus honest about which names are routable).
ALL_AGENTS = {
    "orchestrator", "architect", "implementer", "reviewer", "tester",
    "security", "reliability", "data-ml", "product", "docs-librarian",
    "research-scout", "pentest", "devils-advocate", "multi-agent-architect",
    "growth-orchestrator", "growth-scout", "seed-installer",
}


def _locate_agent_lint():
    for c in AGENT_LINT_CANDIDATES:
        if c.exists():
            return c
    return None


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
    """
    out = ["---", f"name: {name}", f"description: {description}",
           f"tools: {tools}", f"model: {model}"]
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
    for stem, content in agents.items():
        (adir / f"{stem}.md").write_text(content, encoding="utf-8")
    if golden is not None:
        (adir / "_routes.golden.tsv").write_text(golden, encoding="utf-8")
    return root, dst


def load_corpus():
    rows = []
    for line in CORPUS_TSV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "\t" not in line:
            continue
        task, expected = line.split("\t", 1)
        rows.append((task.strip(), expected.strip()))
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


@pytest.mark.parametrize("task,expected", REPRESENTATIVE,
                         ids=[f"{a}<-{t[:32]}" for t, a in REPRESENTATIVE])
def test_route_representative_top_pick(task, expected):
    lint = require_lint()
    r = run(lint, ["--route", task, *ROSTER_ARGS], cwd=REPO)
    assert r.returncode == 0, f"--route should exit 0.\nstderr:\n{r.stderr}"
    assert top_pick(r.stdout) == expected, (
        f"task {task!r}\nexpected top specialist {expected!r}\n"
        f"--- stdout ---\n{r.stdout}"
    )


def test_route_emits_ranked_list_and_band():
    """--route prints a confidence band and a ranked list (plan §4.2 shape)."""
    lint = require_lint()
    r = run(lint, ["--route", "write the failing test that encodes the contract",
                   *ROSTER_ARGS], cwd=REPO)
    assert r.returncode == 0, r.stderr
    assert band(r.stdout) in {"HIGH", "MEDIUM", "LOW", "NONE"}, (
        f"no confidence band in output:\n{r.stdout}"
    )
    assert top_pick(r.stdout) is not None, (
        f"no ranked specialist line in output:\n{r.stdout}"
    )


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


def test_confidence_high_on_unambiguous_task(tmp_path):
    """A task hitting one agent's distinctive triggers -> HIGH, that agent top."""
    root, dst = build_project(tmp_path, _band_roster())
    r = run(dst, ["--route", "audit the diff for regressions"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert band(r.stdout) == "HIGH", f"expected HIGH:\n{r.stdout}"
    assert top_pick(r.stdout) == "reviewer", r.stdout


def test_confidence_none_on_no_match(tmp_path):
    """Gibberish matches nothing -> NONE, and the hint points at commission."""
    root, dst = build_project(tmp_path, _band_roster())
    r = run(dst, ["--route", "xyzzy plugh frobnicate quux"], cwd=root)
    assert r.returncode == 0, f"--route must not crash on a no-match:\n{r.stderr}"
    assert band(r.stdout) == "NONE", f"expected NONE:\n{r.stdout}"
    assert "commission" in r.stdout.lower(), (
        f"NONE hint must recommend commissioning an expert:\n{r.stdout}"
    )


def test_confidence_low_on_novel_stack(tmp_path):
    """A novel-stack task no specialist covers -> LOW/NONE + commission hint."""
    root, dst = build_project(tmp_path, _band_roster())
    r = run(dst, ["--route", "set up a cobol batch job on the mainframe"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert band(r.stdout) in {"LOW", "NONE"}, (
        f"a novel-stack task must be LOW/NONE (commission path):\n{r.stdout}"
    )
    assert "commission" in r.stdout.lower(), r.stdout


# ==========================================================================
# 3. Scoring: triggers/name weighted above description; IDF de-weights generic
#    terms; a distinctive trigger dominates a generic word (plan §4.2).
# ==========================================================================
def test_scoring_distinctive_trigger_dominates(tmp_path):
    root, dst = build_project(tmp_path, _band_roster())
    r = run(dst, ["--route", "quarantine the flaky end-to-end fixture"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert top_pick(r.stdout) == "beta", (
        f"a distinctive trigger must dominate:\n{r.stdout}"
    )


def test_scoring_generic_word_does_not_misroute(tmp_path):
    """'code' is generic (df high -> weight 1 across the roster); a task carrying
    only a generic word must not yield a confident HIGH pick."""
    root, dst = build_project(tmp_path, _band_roster())
    r = run(dst, ["--route", "improve the code"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert band(r.stdout) != "HIGH", (
        f"a generic word shared across agents must not route HIGH:\n{r.stdout}"
    )


def test_scoring_trigger_beats_description(tmp_path):
    """Same term in one agent's trigger vs another's description -> trigger wins
    (triggers are 2x, description is the 1x fallback, plan §4.2)."""
    agents = {
        "trig": agent_md("trig", description="a plain worker",
                         triggers=["reconcile the ledger"]),
        "desc": agent_md("desc", description="this agent will reconcile things",
                         triggers=["unrelated placeholder phrase"]),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--route", "reconcile the accounts"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert top_pick(r.stdout) == "trig", (
        f"a trigger match must outrank a description match:\n{r.stdout}"
    )


# ==========================================================================
# 4. Frontmatter parser closes the inline-`tools:` list gap (plan §4.2).
#    Observable via §4.1 rule 2: can_delegate == (Task in tools). The tool can
#    only enforce this if it parsed the inline list into real tokens.
# ==========================================================================
def test_inline_tools_list_parsed_valid_delegator(tmp_path):
    agents = {
        "boss": agent_md("boss", tools="[Read, Write, Bash, Task]",
                         triggers=["coordinate the work"],
                         can_delegate=True, max_spawn_depth=1,
                         delegates_to=["leaf"]),
        "leaf": agent_md("leaf", tools="[Read, Grep]",
                         triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    assert r.returncode == 0, (
        f"--lint should accept a well-formed roster with an inline Task grant:\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_inline_tools_list_parsed_detects_task_present(tmp_path):
    """tools has Task (inline) but can_delegate:false -> --lint fails. Proves the
    inline list was parsed into tokens, not treated as an opaque string."""
    agents = {
        "boss": agent_md("boss", tools="[Read, Write, Task]",
                         triggers=["coordinate the work"], can_delegate=False),
        "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    assert r.returncode != 0, (
        "can_delegate:false while Task is in the inline tools list must fail "
        f"--lint (§4.1 rule 2):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_inline_tools_list_parsed_detects_task_absent(tmp_path):
    """tools lacks Task but can_delegate:true -> --lint fails."""
    agents = {
        "boss": agent_md("boss", tools="[Read, Write, Edit]",
                         triggers=["coordinate the work"], can_delegate=True,
                         max_spawn_depth=1, delegates_to=["leaf"]),
        "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    assert r.returncode != 0, (
        "can_delegate:true without Task in tools must fail --lint (§4.1 rule 2):\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_triggers_parse_from_real_agent_def(tmp_path):
    """Triggers + the real inline `tools:` line parse from a REAL agent def.

    Take the live tester def verbatim (its real `tools: [Read, Write, Edit,
    Glob, Grep, Bash]` inline line), give it a distinctive trigger, and confirm
    --route selects it from that phrase — proving the parser handled the real
    frontmatter shape, not just synthetic fixtures.
    """
    src = LIVE_AGENTS / "04-tester.md"
    assert src.exists(), f"expected a real agent def at {src}"
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
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--route", "quarantine the flaky characterization fixture"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert top_pick(r.stdout) == "tester", (
        f"router must parse triggers from a real agent def's frontmatter:\n{r.stdout}"
    )


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


def test_lint_passes_on_valid_roster(tmp_path):
    root, dst = build_project(tmp_path, _valid_roster())
    r = run(dst, ["--lint"], cwd=root)
    assert r.returncode == 0, (
        f"--lint should pass a well-formed roster:\nstdout:\n{r.stdout}\n"
        f"stderr:\n{r.stderr}"
    )


def test_lint_fails_on_missing_triggers(tmp_path):
    agents = _valid_roster()
    agents["broken"] = agent_md("broken", triggers=None)  # no routing_triggers key
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    assert r.returncode != 0, "missing routing_triggers must fail --lint"
    assert "broken" in (r.stdout + r.stderr), (
        f"--lint must name the offending agent:\nstdout:\n{r.stdout}\n"
        f"stderr:\n{r.stderr}"
    )


def test_lint_fails_on_empty_triggers(tmp_path):
    agents = _valid_roster()
    agents["hollow"] = agent_md("hollow", triggers=())  # present but empty list
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    assert r.returncode != 0, "empty routing_triggers must fail --lint"
    assert "hollow" in (r.stdout + r.stderr), (
        f"--lint must name the agent with empty triggers:\nstdout:\n{r.stdout}\n"
        f"stderr:\n{r.stderr}"
    )


def test_lint_real_roster_passes():
    """--lint validates routing_triggers across the real roster (P0 gate)."""
    lint = require_lint()
    r = run(lint, ["--lint", *ROSTER_ARGS], cwd=REPO)
    assert r.returncode == 0, (
        "--lint must pass over the real agent defs once P0 frontmatter lands:\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


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


def test_lint_fails_on_delegates_to_equal_depth(tmp_path):
    """depth-1 → depth-1 edge: the target is not strictly shallower, so the
    allowlist violates ADR-B and --lint must reject it."""
    agents = {
        "boss": _delegator("boss", depth=1, delegates_to=["mid"],
                           trigger="coordinate the delegation"),
        "mid": _delegator("mid", depth=1, delegates_to=["leaf"],
                          trigger="carry the middle work"),
        "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    out = r.stdout + r.stderr
    assert r.returncode != 0, (
        "a delegates_to edge to an EQUAL-depth agent must fail --lint (ADR-B):\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "ADR-B" in out and "boss" in out and "mid" in out, (
        f"--lint must name the offending equal-depth edge (ADR-B):\n{out}"
    )


def test_lint_fails_on_delegates_to_greater_depth(tmp_path):
    """depth-1 → depth-2 edge: the target is DEEPER than the delegator, the
    strongest form of the ADR-B violation; --lint must reject it."""
    agents = {
        "boss": _delegator("boss", depth=1, delegates_to=["mid"],
                           trigger="coordinate the delegation"),
        "mid": _delegator("mid", depth=2, delegates_to=["leaf"],
                          trigger="carry the middle work"),
        "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    out = r.stdout + r.stderr
    assert r.returncode != 0, (
        "a delegates_to edge to a GREATER-depth agent must fail --lint (ADR-B):\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "ADR-B" in out and "boss" in out and "mid" in out, (
        f"--lint must name the offending greater-depth edge (ADR-B):\n{out}"
    )


def test_lint_fails_on_max_spawn_depth_out_of_range(tmp_path):
    """max_spawn_depth=5 is outside the [1,3] ADR-B bound; --lint must reject
    it (the delegates_to allowlist is otherwise valid, isolating the range
    error)."""
    agents = {
        "boss": _delegator("boss", depth=5, delegates_to=["leaf"],
                           trigger="coordinate the delegation"),
        "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    out = r.stdout + r.stderr
    assert r.returncode != 0, (
        "max_spawn_depth outside [1,3] must fail --lint (§4.1 rule 3):\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "max_spawn_depth" in out and "[1,3]" in out and "boss" in out, (
        f"--lint must flag the out-of-range max_spawn_depth on the agent:\n{out}"
    )


def test_lint_fails_on_delegates_to_unknown_agent(tmp_path):
    """delegates_to names an agent absent from the roster; --lint must reject
    the dangling edge (§4.1 rule 3)."""
    agents = {
        "boss": _delegator("boss", depth=1, delegates_to=["ghost"],
                           trigger="coordinate the delegation"),
        "leaf": agent_md("leaf", triggers=["do the leaf work"], can_delegate=False),
    }
    root, dst = build_project(tmp_path, agents)
    r = run(dst, ["--lint"], cwd=root)
    out = r.stdout + r.stderr
    assert r.returncode != 0, (
        "a delegates_to edge to an UNKNOWN agent must fail --lint (§4.1 rule 3):\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "unknown agent" in out and "ghost" in out and "boss" in out, (
        f"--lint must name the dangling delegates_to target:\n{out}"
    )


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


def test_eval_passes_on_good_golden(tmp_path):
    root, dst = build_project(tmp_path, _EVAL_ROSTER, golden=_GOOD_GOLDEN)
    r = run(dst, ["--eval"], cwd=root)
    assert r.returncode == 0, (
        f"--eval should pass at >=90% top-1 with novel->LOW:\nstdout:\n{r.stdout}\n"
        f"stderr:\n{r.stderr}"
    )
    assert re.search(r"\d", r.stdout), (
        f"--eval should report an accuracy figure:\n{r.stdout}"
    )


def test_eval_fails_below_threshold(tmp_path):
    root, dst = build_project(tmp_path, _EVAL_ROSTER, golden=_BAD_GOLDEN)
    r = run(dst, ["--eval"], cwd=root)
    assert r.returncode != 0, (
        "--eval must exit non-zero when top-1 accuracy is below threshold "
        f"(fail-closed gate):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_eval_real_golden_meets_threshold():
    """--eval over the real install (reads .claude/agents/_routes.golden.tsv)."""
    lint = require_lint()
    r = run(lint, ["--eval", *ROSTER_ARGS], cwd=REPO)
    assert r.returncode == 0, (
        "--eval must pass over the production golden set once P0 lands:\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


# ==========================================================================
# 7. Honesty note in the banner (plan §4.2) — same discipline as route-hook.
# ==========================================================================
def test_banner_honesty_note(tmp_path):
    root, dst = build_project(tmp_path, _valid_roster())
    r = run(dst, ["--route", "audit the diff"], cwd=root)
    assert r.returncode == 0, r.stderr
    assert "keyword heuristic" in r.stdout.lower(), (
        "the router must print the 'keyword heuristic — reason over it' honesty "
        f"note so it is not mistaken for an oracle:\n{r.stdout}"
    )


# ==========================================================================
# 8. Golden corpus sanity (housekeeping of tester-owned test data, not a P0
#    behavior contract — passes independent of the tool).
# ==========================================================================
def test_golden_corpus_is_wellformed_and_covers_the_roster():
    rows = load_corpus()
    assert rows, f"golden corpus is empty: {CORPUS_TSV}"
    covered = {a for _, a in rows if a != "LOW"}
    unknown = covered - ALL_AGENTS
    assert not unknown, f"golden corpus names non-roster agents: {sorted(unknown)}"
    missing = (ALL_AGENTS - {"orchestrator"}) - covered
    assert not missing, f"golden corpus does not cover: {sorted(missing)}"
    assert sum(1 for _, a in rows if a == "LOW") >= 3, (
        "golden corpus needs >=3 novel-stack (LOW) rows (plan §4.3)"
    )


# ==========================================================================
# 9. Golden corpus parity across its shipped copies (one-home-per-fact, kernel
#    §3.2). The install copy (.claude/agents/), the seed copy (expert-seed-
#    system/agents/), and this test fixture must be byte-identical, or --eval
#    can pass on the shipped copy while the fixture rots (or vice versa).
#    Robust to install layout: paths that are absent are skipped, not errors.
# ==========================================================================
def test_golden_corpus_copies_are_byte_identical():
    present = [(p, p.read_bytes()) for p in GOLDEN_COPIES if p.exists()]
    if len(present) < 2:
        pytest.skip(
            "fewer than two golden-corpus copies present to compare: "
            + (", ".join(str(p) for p, _ in present) or "<none>")
        )
    ref_path, ref_bytes = present[0]
    for p, data in present[1:]:
        assert data == ref_bytes, (
            f"golden routing corpus drift (one-home-per-fact, kernel §3.2):\n"
            f"  {p} ({len(data)} bytes)\n"
            f"differs from\n"
            f"  {ref_path} ({len(ref_bytes)} bytes)\n"
            "the three shipped copies must be kept byte-identical."
        )
