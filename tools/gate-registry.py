#!/usr/bin/env python3
"""gate-registry: what each gate asserts, what it reads, and which kind of
false green it defends against.

A gate's verdict is only worth what its INPUT SET is worth. `tests/run.sh` runs
thirty steps and exits 0; that sentence is what a reader takes away, and it is
not the same claim as "the seed complies with everything it checks". Six of the
suites read only `tests/fixtures/`: they prove a linter works and say nothing
about whether the tree it ships obeys it. That difference was invisible because
nothing recorded it.

So each gate declares the false-green class it is exposed to:

  coverage        it reads fewer inputs than its name implies
  scope           it reads fixtures, not the shipped artifact
  self-reference  it scores an artifact against data co-authored with it
  representation  its fixture does not represent the real case
  evidence        it can pass without the evidence it claims to check
  semantic        it checks syntax where the property is meaning
  none            its input set is the artifact it certifies

The registry is DERIVED, not maintained: `--lint` parses tests/run.sh and fails
when a step has no entry, or an entry names a step that no longer runs. Adding a
gate without saying what it can miss is itself a defect, and this is the check
that says so.

It also holds the runner's own shell contract, because every classification
above is worth nothing if the runner cannot fail. Deleting the `e` from
`set -euo pipefail` was measured to take a run with three FAIL lines in its log
— a 9 744-byte kernel, over budget — to EXIT=0, without touching a single
numeric literal, so `ratchet-lint` never fired either. Suffixing one gate line
with `|| true` does the same to that gate, and the step parser stops its tail
group at `|`, so the registry went on counting it. Both are one token, and
neither is a number, a step name or a registry entry: nothing else in the tree
was looking at them.

Usage:
    python3 tools/gate-registry.py --lint      # every run.sh step is classified
    python3 tools/gate-registry.py --table     # markdown, for documentation
    python3 tools/gate-registry.py --summary   # counts by class and scope

No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_SH = ROOT / "tests" / "run.sh"

# scope: what the gate actually reads.
#   real-tree     the shipped artifact itself
#   fixtures      tests/fixtures/ only
#   temp-install  a disposable install of the real seed
FIXTURES, REAL, TEMP = "fixtures", "real-tree", "temp-install"

# The directories a gate may live in. One home: `run_sh_steps()` scans these and
# `runner_contract_problems()` refuses a gate placed outside them, so the two
# cannot drift into a gate that runs and is invisible here.
RUN_SH_STEP_DIRS = ("tests", "tools", "integrations", "templates")

# step key -> (asserts, scope, false-green class, note)
# The key is the basename of the script, or the tool plus its distinguishing
# flag where one script is run more than once.
GATES: dict[str, tuple[str, str, str, str]] = {
    "test-unified-graph-install.sh": (
        "every knowledge artifact lands under one docs/graph/ root", TEMP, "none", ""),
    "test-knowledge-paths.sh": (
        "graph paths referenced by the machinery resolve", REAL, "none", ""),
    "test-orchestration-entry.sh": (
        "the tool-neutral entry prompt drives the documented flow", REAL, "semantic",
        "asserts the prompt SAYS the right things; cannot assert a session obeys it"),
    "test-tier-lanes.sh": (
        "T2's covered and contained lanes stay distinct", REAL, "semantic",
        "tier classification is a judgment the gate can only check the wording of"),
    "test-graph-artifacts.sh": (
        "template artifacts exist and carry their required shape", REAL, "none", ""),
    "test-spec-lint.sh": (
        "the spec linter finds shape defects", FIXTURES, "scope",
        "proves the linter works against planted fixtures; the seed's own "
        "docs/specs/ are swept by the spec-lint.py step below"),
    "spec-lint.py": (
        "the seed's own two specs carry no fabricated sign-off, no invented "
        "status, and no live spec without contracts; uncovered contracts stay "
        "within a ratcheted budget", REAL, "coverage",
        "the coverage half is enumerated debt, not a pass: the budget only stops "
        "that number RISING. It matches a slug ANYWHERE under tests/ — including "
        "in a COMMENT, verified: three contracts became 'covered' when a "
        "docstring in tests/seed-lint.py happened to name them, and the count "
        "fell 23 -> 20 with no test written. A contract whose §10 row cites a "
        "test that asserts something adjacent also still reads as covered. "
        "seed-lint's check_spec_rows_name_their_contract is the stricter "
        "companion: it requires the slug in the test the ROW cites"),
    "test-grill-lint.sh": (
        "the plan-of-record linter finds shape defects", FIXTURES, "scope",
        "proves the linter works; the seed's docs/plans/ use a different heading "
        "convention and are not swept"),
    "test-full-install.sh": (
        "every adapter delivers the runtime machinery it promises", TEMP, "coverage",
        "checks presence and the command roster, not the placement contract "
        "(test-install-placement.sh owns that)"),
    "test-install-placement.sh": (
        "M1/M2/M3/M7/M8/M9 over every destination an install writes", TEMP,
        "coverage",
        "discovers the destination set from a real install, so a destination "
        "added later is covered without anyone remembering — but discovery "
        "cannot see a destination the installer STOPPED writing, which is why "
        "the M1 completeness check walks the seed's own inventory instead. "
        "Classified `none` until a reviewer patched place_file to skip one "
        "protocol and watched the suite stay green"),
    "test-plant-state.sh": (
        "S1-S6: owner decisions survive, record agrees with disk", TEMP, "none", ""),
    "test-install-kernel-modes.sh": (
        "K1-K6: one kernel body, copy isolates, symlink is live", TEMP,
        "coverage",
        "K3 exercises one adapter and K5 re-runs under --copy, so neither saw "
        "the multi-adapter --symlink case where the pair flipped on every run "
        "and backups grew without bound. That case now lives in "
        "test-install-placement.sh's M3 section"),
    "test-seed-budgets.sh": (
        "special-character targets, and that the seed's budgets can fail", TEMP, "none",
        "the budget half exists because a budget nobody has seen fail is a "
        "constant, not a gate"),
    "test-install-adoption.sh": (
        "an install into a target that is not pristine: existing instructions, "
        "a partial install, a path in the way, a read-only target", TEMP, "coverage",
        "covers the failure shapes that were actually observed; a target can be "
        "non-pristine in ways nobody has thought of yet, and only those are here"),
    "test-bound-hook.sh": (
        "the bounded-execution guard blocks what it claims to", FIXTURES, "representation",
        "the fixture is a synthetic command line, not a real session's"),
    "test-graft-tools.sh": (
        "the graft audit classifies backups and finds buried customization",
        FIXTURES, "scope", "fixture plants only; totality against a real install "
        "is asserted by test-install-placement.sh's M8 case"),
    "test-nested-checkout.sh": (
        "the three upward walkers stop at the plant root: an ancestor "
        "checkout's linter, register and roster are all unreachable, and the "
        "plant's own artifacts at its own repo root still are", TEMP, "coverage",
        "asserts the boundary BEHAVIOUR that seed-lint's canonical-block check "
        "can only hold byte-identical — three copies of one WRONG rule pass "
        "that check and fail this one. Its own residual: it exercises the "
        "three walkers that exist, so a fourth upward walk added later is "
        "covered by nothing until someone adds it here"),
    "test_frontmatter_contract.py": (
        "what the one frontmatter reader DOES — nesting, comment boundary, "
        "repeated keys, refusal of a continuation — asserted against every "
        "published copy", REAL, "coverage",
        "the truth half of a pair whose other half is sameness. seed-lint holds "
        "the four copies byte-identical and test_metadata_equivalence holds the "
        "consumers in agreement; both are tautologies, and three "
        "one-word mutations applied to ALL FOUR copies passed every gate before "
        "this existed. Its own residual: it asserts the shapes the seed's "
        "frontmatter actually uses, so a shape nobody writes yet is unbound"),
    "test-collected-count.sh": (
        "no unittest suite has quietly stopped collecting tests, against a "
        "per-suite floor in tests/collected.json", REAL, "coverage",
        "it counts what a suite COLLECTS, not what its assertions are worth: a "
        "test whose body is replaced by `pass` still counts. It exists because "
        "renaming the 27 of 50 methods in test_agent_lint.py that no spec row "
        "cites took the suite from 69 tests to 43 with the whole gate green"),
    "test-tool-help.sh": (
        "every shipped tool with a CLI answers --help on its own terms, "
        "discovered by walking the tool directories rather than by a list",
        REAL, "coverage",
        "it asserts --help exits 0 and prints something, not that what it "
        "prints is accurate or current. Hooks are excluded by shape: they are "
        "invoked by a harness with a payload on stdin, never by a person with "
        "flags"),
    "roster-justification.py --gaps": (
        "every machinery node can answer why it is on the roster",
        REAL, "semantic",
        "it checks each node carries a `prevents:` and at least one peer edge — "
        "presence, not truth. Two reference documents point readers here as the "
        "published home for the roster's justification, and an adversarial pass "
        "found eight shipped `prevents:` lines that are false or already "
        "prevented by another node, every one of which passes this step. It "
        "does now print routing demand per corpus class rather than summing it, "
        "which is the defect SPEC-0002 forbids for --eval and this tool escaped "
        "only because the spec scopes itself to --eval. Its OTHER residual was "
        "narrower and worse and is now closed: a node it could not read used to "
        "leave the denominator, so `chmod 000` on one agent turned '0 gaps, of "
        "60' into '0 gaps, of 59' at exit 0 — a smaller denominator presented "
        "as a clean bill. It names and fails on an unreadable node now "
        "(test-lint-audibility.sh case 5)"),
    "test_tool_authorship.py": (
        "a repeated operation has an author, and the close-out still spawns once",
        REAL, "semantic",
        "it holds the three-way split structurally — rule.toolcraft keeps exactly "
        "one home and the linter's map agrees with it, the tool-smith is routable "
        "and carries at least three golden rows (counted, not grepped: deleting "
        "all three left the section comment behind and satisfied a substring "
        "check while the agent became measured by nothing), canonize states its "
        "producer and is checked against disclaimers that named the agent while "
        "removing it, and the scope refusal is checked against charters asserting "
        "its opposite. It cannot tell whether the tool-smith APPLIES its bar "
        "honestly: building on two instances and a hunch, or refusing one that "
        "had earned building, passes every check here"),
    "test_brainstorm_modes.py": (
        "both brainstorm modes exist, are reachable, and differ where it matters",
        REAL, "semantic",
        "it reads the two mode nodes and asserts the seam structurally. The "
        "exit check forbids the negations FIRST and then requires the "
        "affirmative, because a positive regex for the property matched its own "
        "inversion — 'Never exit WITHOUT user CONFIRMATION' passed a check "
        "written to forbid exactly that. It still cannot tell whether a session "
        "PICKED the right mode for a given decision, which is the failure that "
        "actually costs something and is judgement exercised mid-session"),
    "test-entry-paths.sh": (
        "every way into the seed reaches the protocol that fits the target",
        REAL, "semantic",
        "MEASURED against six simultaneous behaviour inversions, twice. Round 1 "
        "of an adversarial review reverted all six and this step stayed green "
        "(evasion: a comma, dropped backticks, a parenthetical aside). Round 2 "
        "inverted them a second way — satisfying every literal while negating "
        "the sentence ('It is false that the producer is X') — and it stayed "
        "green again. Natural-language negation is unbounded, so no list of "
        "banned phrases closes it. MEASURED, and an earlier version of this "
        "note claimed four of six were caught — that was WRONG, and a later "
        "round proved it by inverting more carefully: ONE of the six is "
        "caught. The one is `initialize`'s fork arms, read as TABLE CELLS "
        "with swap detection, which prose cannot fake. The kernel tie, the "
        "installer tie and grow's sub-step ban are still substring regexes "
        "and each was walked past by a reworded negation (`it is false that "
        "an empty repo goes to from-scratch` satisfies the co-occurrence "
        "window; `control resumes at Phase 2` is not the banned `and "
        "resume`). Routing IS parsed from an installed plant's LOAD block "
        "only, which is real, but no inversion of the four targets it. "
        "FIVE REMAIN INVERTIBLE and none is claimed"),
    "test-growth-audit.sh": (
        "UNKNOWN rows are disclosed rather than silently dropped", FIXTURES, "scope", ""),
    "test-agnosticism-lint.sh": (
        "the agnosticism floor finds leaked host IPs and pinned CVEs",
        FIXTURES, "scope", "seed-lint.py runs the same scanner over the real corpora"),
    "test-prose-lint.sh": (
        "the prose linter finds its nine violation classes", FIXTURES, "scope", ""),
    "test-lint-audibility.sh": (
        "V5: an unreadable input is named and is fatal, in four linters",
        FIXTURES, "none", "the input set IS unreadable files; fixtures are the "
        "only way to produce one"),
    "prose-lint.py --file README --file DOCUMENTATION": (
        "the seed's own front-door prose meets the floor", REAL, "coverage",
        "2 of ~340 markdown files; documentation/*-reference.md are exempt by a "
        "recorded genre decision in run.sh"),
    "test-status-register.sh": (
        "the status vocabulary is controlled and queryable", FIXTURES, "scope", ""),
    "test-status-migrate.sh": (
        "status migration is exact and idempotent", FIXTURES, "scope", ""),
    "test-seed-lint.sh": (
        "the seed linter's own contract, and that every check_* in it is either "
        "exercised by a planted violation or declared unprotected", REAL, "scope",
        "the planted violations run against a hermetic COPY, so they prove the "
        "linter fires and say nothing about the shipped tree; the "
        "check-coverage-binder step at its end is what reads $ROOT, and it reads "
        "only the NAMES of the checks, not what they assert"),
    "test-legal-lint.sh": (
        "the legal citability contract", FIXTURES, "scope", ""),
    "test-tool-corpus.sh": (
        "a page claiming portable stability ships code that compiles and works",
        REAL, "representation",
        "one page's verifier calls `yaml.safe_load`, and PyYAML is not stdlib. "
        "This used to be `if python3 -c 'import yaml'` with a SKIP branch that "
        "still printed PASS — and the seed's CI has no `pip install`, so both "
        "legs took it and a mandatory check went unexecuted inside a green "
        "gate. The suite now supplies its own stdlib `safe_load` for its own "
        "two fixtures, so the check runs everywhere. The residual is what that "
        "trades: where PyYAML is absent the verifier is exercised over a "
        "simpler parser than the one a user would have, so a defect that needs "
        "real YAML — anchors, flow style, type coercion — is reachable here "
        "only on a host that happens to have PyYAML installed"),
    "test_graph_lint.py": (
        "the graph linter's CLI contract", FIXTURES, "scope", ""),
    "agent-lint.py --lint": (
        "roster frontmatter, and can_delegate == (Task in tools)", REAL, "none", ""),
    "agent-lint.py --eval": (
        "routing, per corpus class, gated on confident-wrong = 0", REAL, "self-reference",
        "the contract class is co-authored with the triggers it scores and is "
        "labelled a consistency check; the paraphrase class is the held-out one, "
        "and an overlap check keeps it held out. SLACK, stated rather than left "
        "to be discovered: EVAL_THRESHOLD 0.95 against a measured 0.984 bites at "
        "58 of 61, so THREE contract rows can stop routing to their own agent "
        "with this green. That headroom is deliberate — adding an agent shifts "
        "df globally and can drop unrelated routes — but it is slack, not a "
        "measurement. PARAPHRASE_FLOOR and the adversarial budget now carry "
        "none"),
    "test_agent_lint.py": (
        "the router's CLI contract and the corpus-honesty rules", REAL, "scope",
        "ROSTER resolves to the seed's own agents/ and --eval runs against the "
        "shipped corpus, so this DOES bind the tree — but only the roster and "
        "the golden rows. Breaking a shipped agent's routing_triggers fails it; "
        "breaking anything else in the seed does not."),
    "test_router_reach.py": (
        "no routing vocabulary is unreachable by its own inflection, in either "
        "router, and every stem collision has been reviewed", REAL, "coverage",
        "it enumerates the vocabulary exhaustively but probes ONE inflection "
        "rule per word — the regular plural. An irregular a charter starts "
        "using (analyses/analysis is already known) is not measured, and the "
        "STEM_IRREGULAR map is deliberately tiny rather than a lexicon"),
    "test_metadata_equivalence.py": (
        "the five frontmatter parsers and two router tokenizers agree on one "
        "shared input table", REAL, "evidence",
        "it pins agreement BETWEEN the copies, which is a weaker claim than "
        "agreement with the truth: four byte-identical frontmatter.py copies "
        "mutated the SAME wrong way pass this and every other gate. One "
        "property is truth-checked (a multi-line description is refused); the "
        "rest are checked only for sameness. Both divergences this residual "
        "used to name are closed — graph-lint received the compound-fragment "
        "fix (asserted here now, on resolve()'s own scoring path), and the "
        "multi-line description is refused by every consumer of the shared "
        "reader; status-register remains the one recorded exception"),
    "seed-lint.py": (
        "one home per fact; kernel, body and eager budgets; manifest agreement; "
        "SINGLE_WRITER derived from install.sh by count and shape",
        REAL, "semantic",
        "most checks here are structural and mean what they say, and four rounds "
        "of adversarial mutation have been spent making that true: the mirror "
        "checks now read EVERY view of each reference document (summary table, "
        "per-node section, edge table, grouping), fail on an ABSENT mirror "
        "rather than skipping it, refuse a row that does not parse, and bind a "
        "cited test to the FILE that cites it. Each of those closed a "
        "demonstrated false green — including three checks added in an earlier "
        "round that were themselves inert. The one "
        "exception is each machinery node's `prevents:` — the failure the node's "
        "absence produces. The linter can tell that it exists, is long enough to "
        "name a failure, and shares no ten-word run with `description:` (a "
        "first-60-characters comparison was defeated by a preamble, so it "
        "compares content wherever it starts). It cannot tell whether it is "
        "TRUE, and an adversarial pass found eight shipped `prevents:` lines "
        "that are false or already prevented by another node. A well-formed "
        "untrue one passes this gate; only a reader who knows the domain "
        "catches it. SINGLE_WRITER's derivation has its own residual, and this "
        "is where SPEC-0001 §4 says it lives: it reads shell with regexes, so a "
        "write under a non-python inline interpreter or under `eval` is invisible "
        "to it. Two shapes the spec used to list here — a write inside a command "
        "substitution, and one on the right of a pipe — were re-tested and are "
        "caught. A third residual is the bigger one: the four placers were "
        "exempted WHOLESALE until 7.16.0, so a raw write hidden inside "
        "`place_file` destroyed a file outside the target with this gate green. "
        "They are counted rows now, but the check still sees only writes it can "
        "attribute to a function it can find"),
    "ratchet-lint.py": (
        "no budget, threshold or debt ledger has been loosened since it was "
        "recorded", REAL, "evidence",
        "it compares the shipped values against tests/ratchets.json and cannot "
        "stop someone editing both in one commit — what it stops is a limit "
        "being loosened SILENTLY, inside a change that looks like it is about "
        "something else. A tripwire, not a vault"),
    "test_gate_registry.py": (
        "the registry's parser sees every invocation spelling, and refuses in "
        "both directions", REAL, "scope",
        "the parser is exercised against synthetic run.sh files, but the suite "
        "also reads the REAL tests/run.sh — adding an unclassified step to it "
        "fails this suite. Verified. The real "
        "one is exercised by the step below"),
    "test_gate_pool.py": (
        "the shared concurrency budget clamps to [4, 64] and its cross-process "
        "token pool caps TOTAL leaf subprocesses across every parallel suite to "
        "that budget", REAL, "coverage",
        "it exercises the clamp and the pool bound over synthetic scenarios "
        "(sleep + a slot count), which is the cpu_count**2 explosion the pool "
        "exists to prevent; it does not re-run the real suites, so a suite that "
        "parallelised its scenarios but dropped an assertion is out of scope — "
        "that is each suite's own row, and each suite carries a red-on-break "
        "check. The exit-code aggregation half is pinned next door in "
        "test_run_parallel.py, which drives the same dispatch path"),
    "test_run_parallel.py": (
        "the parallel dispatcher fails the whole run when ANY step fails, "
        "aggregates every exit code rather than only the first, and names each "
        "failed step", REAL, "coverage",
        "it exercises the aggregation and exit-code contract over synthetic "
        "step lists (true/false/exit N), which is the invariant a naive `cmd &` "
        "scheme loses; it does not re-run the real 45-gate batch, so a step that "
        "PASSES for the wrong reason is out of its scope — that is each gate's "
        "own row above. The dispatcher itself is documented in the NON_STEP "
        "GUARDS below, since it is the runner, not a gate"),
    "gate-registry.py --lint": (
        "every gate in tests/run.sh declares what it reads and what it can miss",
        REAL, "semantic",
        "it checks that a classification EXISTS, not that it is true: a step "
        "whose entry wrongly claims `real-tree` passes here. The entries are "
        "prose an author must keep honest, and this gate only keeps them "
        "present and in sync with the runner"),
    "legal-lint.py": (
        "every legal entry states its edition, or is in the dated debt ledger",
        REAL, "evidence",
        "45 entries predate the check and sit in an enumerated ledger that may "
        "only shrink; the gate passes while they are outstanding, by design"),
}


def run_sh_steps() -> list[str]:
    """The gate steps tests/run.sh actually executes, in order.

    The parser is deliberately forgiving about SHAPE and strict about coverage.
    An earlier version anchored the interpreter to the start of the line and
    required a `$ROOT`-spelled path, and silently missed four ordinary
    spellings — a line continuation, a step inside a
    subshell, an interpreter flag before the path, and a relative path without
    `$ROOT` — returning 4 of 8 real invocations while reporting OK. A registry
    that cannot see a gate is precisely the false green it exists to prevent,
    and it fails in the quietest possible way: by finding nothing to complain
    about.

    So: join continuations, then scan for an interpreter anywhere on the line
    rather than at its start, and accept a path with or without `$ROOT`.
    """
    raw = RUN_SH.read_text(encoding="utf-8")
    # Join backslash continuations before anything else looks at lines.
    raw = re.sub(r"\\\n\s*", " ", raw)
    steps = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", line)
        # `bash`/`python3` anywhere on the line (inside `( ... )`, after `&&`,
        # after an `if ...; then`), with optional interpreter flags, and a path
        # that may or may not be spelled through $ROOT.
        # Three more spellings a reviewer found still invisible: direct
        # execution relying on the executable bit with no interpreter word at
        # all (`"$ROOT/tests/x.sh"`), an interpreter reached through a variable
        # (`$PY "$ROOT/tools/x.py"`), and a versioned binary (`python3.12`).
        # None appear in run.sh today, which is exactly why they are worth
        # matching: the failure mode is a future line nobody classifies, and
        # this tool reporting OK about it.
        # `templates/` joined the path alternation when the seed started running
        # templates/knowledge-graph/spec-lint.py over its own specs: a gate that
        # lives where the SHIPPED linters live was invisible here, and the
        # registry said OK about a step it could not see.
        for m in re.finditer(
                r'(?:\b(?:bash|sh|python3(?:\.\d+)?)\b|\$\{?[A-Z_]+\}?)?'
                r'((?:\s+-[A-Za-z]+)*)\s*'
                r'"?(?:\$\{?ROOT\}?/)?((?:' + "|".join(RUN_SH_STEP_DIRS) + r')'
                r'/[A-Za-z0-9_./-]+\.(?:sh|py))"?([^;&|)]*)',
                line):
            path, rest = m.group(2), m.group(3)
            if path.startswith("/dev/"):
                continue
            # tests/run-parallel.py is the RUNNER that dispatches the steps
            # below — infrastructure, not a gate that asserts a property of the
            # seed. It is accountable in NON_STEP_GUARDS (its false green is
            # losing a sub-step's failure) and pinned by tests/test_run_parallel.py,
            # so it is skipped here exactly like the analogous run.sh EXIT trap
            # has no step line to parse. It must live under a scanned directory
            # (runner_contract_problems refuses a runner reached from outside
            # them), so it is named explicitly rather than hidden by shape.
            if path == "tests/run-parallel.py":
                continue
            name = Path(path).name
            # A tool with a reporting mode and a checking mode is two different
            # steps; only the checking mode is a gate, and the registry must be
            # able to tell them apart. `--gaps` joined --lint/--eval when
            # roster-justification.py was wired in.
            flag = re.search(r"--(lint|eval|gaps)\b", rest)
            if flag:
                name = f"{name} --{flag.group(1)}"
            elif name == "prose-lint.py":
                name = "prose-lint.py --file README --file DOCUMENTATION"
            if name not in steps:
                steps.append(name)
    return steps


def runner_contract_problems() -> list[str]:
    """What the runner must be, for any verdict below it to mean anything.

    Three one-token routes to a green gate, none of which the step parser can
    see, because it is looking at which gates are listed rather than at whether
    the shell will act on what they return:

      - `set -euo pipefail` weakened: a failing step no longer ends the run, and
        the EXIT trap returns the status of the last command instead.
      - a gate line suffixed `|| true` (or `|| :`, or `; true`): the step runs,
        is parsed, is classified, and cannot fail.
      - a gate under a directory outside the parser's own alternation: invisible
        on ADD, and caught on MOVE only because the old key disappears.
    """
    raw = RUN_SH.read_text(encoding="utf-8")
    problems = []

    if not re.search(r"^set -euo pipefail$", raw, re.M):
        problems.append(
            "tests/run.sh does not carry `set -euo pipefail` on a line of its "
            "own — without it a red step does not end the run, and the gate "
            "reports the exit status of whatever ran last")

    dirs = "|".join(RUN_SH_STEP_DIRS)
    for n, line in enumerate(raw.splitlines(), 1):
        stripped = re.sub(r"\s+#.*$", "", line.strip())
        if not stripped or stripped.startswith("#"):
            continue
        has_gate = re.search(rf'(?:{dirs})/[A-Za-z0-9_./-]+\.(?:sh|py)', stripped)
        if has_gate and re.search(r"(?:\|\|\s*(?:true|:)|;\s*true)\s*$", stripped):
            problems.append(
                f"tests/run.sh:{n} ends a gate line with `|| true` — the step "
                f"runs, is classified here, and cannot fail: {stripped}")
        if not has_gate and re.search(
                r'(?:\bbash|\bsh|\bpython3(?:\.\d+)?)\s+"?(?:\$\{?ROOT\}?/)'
                r'[A-Za-z0-9_./-]+\.(?:sh|py)', stripped):
            problems.append(
                f"tests/run.sh:{n} runs a gate from a directory this parser "
                f"does not scan ({dirs}) — it would be invisible to the "
                f"registry: {stripped}")
    return problems


def cmd_lint() -> int:
    steps = run_sh_steps()
    if not steps:
        print("gate-registry: FAIL — parsed zero steps out of tests/run.sh; the "
              "parser and the runner have diverged", file=sys.stderr)
        return 1
    problems = runner_contract_problems()
    for s in steps:
        if s not in GATES:
            problems.append(
                f"tests/run.sh runs '{s}' with no registry entry — say what it "
                f"asserts, what it reads, and which false green it can still "
                f"produce")
    for k in GATES:
        if k not in steps:
            problems.append(
                f"registry lists '{k}' but tests/run.sh no longer runs it — a "
                f"documented gate that does not run is the plainest false green "
                f"there is")
    for k, (asserts, scope, cls, _note) in GATES.items():
        if scope not in (FIXTURES, REAL, TEMP):
            problems.append(f"{k}: unknown scope {scope!r}")
        if cls not in ("coverage", "scope", "self-reference", "representation",
                       "evidence", "semantic", "none"):
            problems.append(f"{k}: unknown false-green class {cls!r}")
        if not asserts:
            problems.append(f"{k}: does not say what it asserts")
    if problems:
        for p in problems:
            print(f"  !! {p}", file=sys.stderr)
        print(f"gate-registry: FAIL ({len(problems)} finding(s))", file=sys.stderr)
        return 1
    fixture_only = sum(1 for k in steps if GATES[k][1] == FIXTURES)
    print(f"gate-registry: OK — {len(steps)} gate(s) classified; "
          f"{fixture_only} read fixtures only")
    return 0


def cmd_table() -> int:
    print("| Gate | Asserts | Reads | False green it can still produce |")
    print("|---|---|---|---|")
    for s in run_sh_steps():
        asserts, scope, cls, note = GATES[s]
        detail = f"**{cls}** — {note}" if note else (
            "—" if cls == "none" else f"**{cls}**")
        print(f"| `{s}` | {asserts} | {scope} | {detail} |")
    return 0


def cmd_summary() -> int:
    steps = run_sh_steps()
    by_scope: dict[str, int] = {}
    by_class: dict[str, int] = {}
    for s in steps:
        _a, scope, cls, _n = GATES[s]
        by_scope[scope] = by_scope.get(scope, 0) + 1
        by_class[cls] = by_class.get(cls, 0) + 1
    print(f"gates: {len(steps)}")
    print("  by what they read:")
    for k, v in sorted(by_scope.items()):
        print(f"    {k:<14} {v}")
    print("  by the false green they can still produce:")
    for k, v in sorted(by_class.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {k:<14} {v}")
    return 0


# Guards that are NOT steps in tests/run.sh and are therefore invisible to the
# parser above — but which can still produce a false green, which is what this
# file exists to record. A run-level EXIT trap is still a gate; it just has no
# line for `cmd_lint` to find, so it had no row here at all.
NON_STEP_GUARDS = {
    "gate_pool.py (shared concurrency budget + scenario dispatcher)": (
        "the gate's ONE concurrency knob ($GATE_JOBS clamped to [4,64], else "
        "the I/O-oversubscribed auto default clamp(cpu*2, 8, 64)) "
        "and its cross-process token pool, so the TOTAL leaf subprocesses across "
        "every parallel suite stay <= the budget (never cpu_count**2), plus the "
        "grouped-output / exit-code aggregation every internally-parallel suite "
        "and run-parallel.py share",
        "coverage",
        "NOT a gate: it asserts nothing about the seed, it RUNS the scenarios "
        "that do. Invisible to the step parser because no run.sh line names it — "
        "the suites call it internally. Its false green is the `cmd &` one — a "
        "failing scenario reported green — pinned by tests/test_run_parallel.py "
        "(which drives this module's dispatch/aggregation) and by every suite's "
        "own red-on-break check. BLIND TO: whether a scenario passed for the "
        "right reason (each suite's own asserts own that), and it takes no seed "
        "snapshot — the whole-run _seed_digest EXIT trap stays the single "
        "integrity guard."),
    "run-parallel.py (tests/run.sh step dispatcher)": (
        "every gate step run.sh hands it runs, its exit code is aggregated, and "
        "a single red step fails the whole gate (exit 1) with the step named — "
        "so parallelising the run did not weaken `set -euo pipefail`'s abort",
        "coverage",
        "NOT a gate: it asserts nothing about the seed, it RUNS the gates that "
        "do, so the step parser skips it by name. Its false green is the one a "
        "`cmd &` scheme has — a failing step reported green — and that is pinned "
        "by tests/test_run_parallel.py, a real step above. BLIND TO: whether a "
        "step passed for the right reason (each gate's own row owns that), and "
        "it takes no seed snapshot of its own — the whole-run _seed_digest EXIT "
        "trap remains the single integrity guard, unchanged."),
    "_seed_digest (tests/run.sh EXIT trap)": (
        "the gate did not modify the seed it was testing — type, mode, path, "
        "bytes (sha256) and link target, over the tree and over .git",
        "coverage",
        "BLIND TO: (1) .git/objects and .git/logs, pruned because they churn on "
        "any read — a file written into either is invisible; (2) mtime-only "
        "changes, deliberately, since a read can touch them; (3) bytecode under "
        "__pycache__/*.pyc, deliberately, since a gate run creates it. It is NO "
        "LONGER blind to a stray .pyc outside __pycache__ (the 7.13.1 "
        "regression), nor to a same-length content edit — cksum was a 32-bit "
        "affine CRC and a collision was constructed on demand; sha256 "
        "replaced it at a measured cost of 2ms over 482 files. It is also no "
        "longer GNU-only: `find -printf` and `sha256sum` are absent on macOS, "
        "so this died on its first line under `set -e` with zero diagnostic and "
        "the mac leg of the CI matrix executed no gates at all. The walk is "
        "python3 now, which every suite here already requires."),
    ".github/workflows/gate.yml": (
        "the seed's own gate runs on every push and pull request, on two "
        "platforms, with no `pip install` step — so a third-party import in a "
        "default-gate test fails there even where it passes locally",
        "evidence",
        "NOT a step in tests/run.sh, and nothing in the gate asserts the "
        "workflow exists: deleting the file leaves every suite green, which is "
        "why `check_ci_workflow` in tests/seed-lint.py now holds its shape. "
        "What no check can hold is whether a run ever went GREEN — the file is "
        "untracked as of 7.16.0 and has never executed, so the macOS leg in "
        "particular is configured rather than demonstrated."),
}


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else "--lint"
    if arg in ("-h", "--help"):
        print(__doc__)
        return 0
    if arg == "--lint":
        return cmd_lint()
    if arg == "--table":
        rc = cmd_table()
        print()
        print("NON-STEP GUARDS (not parsed from run.sh; still able to go green wrongly):")
        for name, (asserts, cls, residual) in sorted(NON_STEP_GUARDS.items()):
            print(f"  {name}")
            print(f"    asserts : {asserts}")
            print(f"    class   : {cls}")
            print(f"    residual: {residual}")
        return rc
    if arg == "--summary":
        rc = cmd_summary()
        print(f"  non-step guards recorded: {len(NON_STEP_GUARDS)} "
              f"(run --table for what each can still miss)")
        return rc
    print(f"unknown option {arg} (try --help)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
