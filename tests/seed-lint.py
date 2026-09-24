#!/usr/bin/env python3
"""seed-lint: one-home-per-fact enforcement for the seed's OWN meta-facts.

graph-lint.py guards a grown plant's docs/graph/; nothing guarded the
seed's meta-documentation, and its duplicated facts drifted (README said
5 coordinators and a 9 KB kernel while frontmatter said six and 27 KB).
This linter makes that failure class deterministic to catch:

  1. roster: agents/ frontmatter <-> manifest.json <-> kernel §1 table
  2. delegator invariant: can_delegate == (spawn tool in tools), read by
     agent-lint's own predicate; tools: listed; allowlists resolve
  3. numeric claims: "N-agent team" and "N coordinators" match reality
  4. kernel budget: core/AGENTS.md stays under KERNEL_BUDGET bytes
  5. kernel anchors: §3.1–§3.8 headings exist (cited seed-wide)
  6. manifest paths: every cataloged file exists on disk
  7. canonical bootstrap block exists and the kernel references it
  8. harness registration: the "installed but not spawnable" rule has one
     home (method.delegation) and every dispatch/install surface points at it
  9. corpus agnosticism floor: no leaked host-IP literal or pinned CVE, and
     no dangling corpus/template cross-reference, in the shipped prose
     (objective leaks only — project names and stack fingerprints stay human
     judgment, since the seed cannot enumerate plant names without naming
     them). The scan itself is `tools/agnosticism-lint.py`, shared machinery
     any agnostic tree can run; this file calls it, it does not copy it.
 10. spec compatibility claims: a stated shell floor is the one the code it
     describes actually holds (the claim, never the word — a spec that
     RECORDS an old claim is not making it)

Dependency-free; exit 0 clean, 1 with findings.
"""
import contextlib
import importlib.util
import json
import re
import sys
import types
import pathlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The one frontmatter reader, from beside this file. A byte-identical copy sits
# next to every consumer because the linters that ship into plants are
# standalone scripts with no package to import from.
import importlib.util as _ilu
_fm_spec = _ilu.spec_from_file_location(
    "cypress_frontmatter", Path(__file__).resolve().parent / "frontmatter.py")
_frontmatter = _ilu.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)
KERNEL = ROOT / "core" / "AGENTS.md"
KERNEL_BUDGET = 8_000  # bytes; 6.0.0 shrank the kernel to a bootstrap —
                       # depth lives in graph machinery nodes, not here

# Every surface the seed MEASURES, it must also BOUND. Until 7.16.0 the kernel
# was the only bounded one: `est_tokens` was checked for honesty (within 2x of
# the measured body) and never for a ceiling, so the machinery could grow
# without limit as long as it declared the growth accurately. An honest number
# is not a budget.
#
# MACHINERY_BODY_CEILING bounds any single routable node. It is not the
# 170-line ceiling graph-lint.py applies to PROJECT nodes — that one exempts
# machinery explicitly, so it bound none of the nodes that needed bounding.
# 1000 is a ratchet against unbounded growth. Raising it is an owner decision
# with a recorded reason, never an edit made to fit new text. Counted as this
# check counts them — `wc -l` minus frontmatter, with the body's trailing
# newline stripped — because the number a reader compares against must be the
# one the check uses.
MACHINERY_BODY_CEILING = 1_000

# The cross-project meta-loop gets its own, larger ceiling. Owner decision,
# 2026-09-14, recorded in docs/decisions/adr-0007-lifecycle-protocol-ceiling.md.
#
# graft, grow and harvest are the only protocols that write into a repository
# the seed does not own, and the defining defect of the 7.16.0 remediation was
# a graft that destroyed three plant customizations while the audit reported
# "clean". Procedural completeness in these three is load-bearing for safety.
#
# The cost the general ceiling protects against is not being paid here: the
# router selects a node from its `load_when:` triggers in the index and never
# opens the body to decide whether it wants the body, so these 2500 lines are
# read only by a session actually performing the operation — which needs the
# whole procedure. Compressing them to fit a number trades a data-loss risk for
# a token-budget one that does not exist at this position in the graph.
#
# It is a ceiling and not an exemption: a governing procedure nobody finishes
# reading fails the same way a truncated one does. It is roughly 1.8x today's
# largest (graft, 1 384 body lines), which is room for the reworks these three
# are owed, and it ratchets like every other limit — ratchet-lint fails on a
# raise and the owner's `--bless` is the signature. The multiple is a derived
# figure written in prose beside the number it derives from, so it drifts every
# time either moves: it read "2.5x" against a 991-line graft and stayed there
# through the lifecycle rework that took graft to 1 384.
LIFECYCLE_BODY_CEILING = 2_500

# CHARTER_VOCAB_DEBT bounds how many words an agent's own charter uses heavily
# and distinctively while NO task can route on them — they appear in the body

# How many live contracts across the seed's own two specs carry no test naming
# their slug. Opened at 23 and fell to 2 when every §10 row was bound to the
# test that asserts it — the two that remain are the two rows honestly marked
# `pending`, which have no test at all. Enumerated debt, not a lie: both specs are back-written over
# behaviour that already shipped. It is a ratchet so the backlog can only
# shrink — a contract LOSING its test fails the gate even while the backlog
# stands, and spec-lint refuses a budget looser than reality so the record
# cannot drift above the debt it records. Derived by
# `spec-lint.py --specs docs/specs --uncovered-budget`, never counted by hand:
# three careful hand counts of this number produced 4, then 5, then 26.
SPEC_UNCOVERED_BUDGET = 2

# How many `green` rows in the specs' §10 cite a test that does not NAME the
# contract it certifies. A ceiling, so the debt may only shrink.
#
# §10 is the page a future session reads to decide whether a contract is
# defended. It said green 50 times and was derived from nothing: the row was
# checked for three things — the named test exists, it is in the cited file, it
# is not skipped — and never for whether the test has anything to do with the
# contract. Repointing one routing contract's row at a real, running, unrelated
# test in the same file — one about legacy two-column corpora — passed both
# linters.
#
# The debt opened at 48 and was paid to 0 in one pass: most were genuinely
# tested — the symlink-replacement contract by
# M2, the backup contract by M7. The test simply does not name the contract, so
# nothing binds the two and the row rests on someone's memory. Paying this down
# means naming the slug in the asserting test, not renaming tests cosmetically.
SPEC_ROW_UNBOUND_BUDGET = 0

# How much of one node's `prevents:` vocabulary may also appear in another's.
# A ceiling, so it ratchets down: two nodes drifting toward the same failure is
# the "moved collisions" class, and it recurs because nothing measured it.
# Set at 0.30 against a measured maximum of 0.16 (ingest-library vs
# library-wiki, genuine near-neighbours). 0.50 was the first guess and left
# 34 points of slack — enough for a reworded duplicate to pass, which is the
# exact shape this catches.
PREVENTS_OVERLAP_CEILING = 0.30
# Its sibling, and it was a bare literal three checks away: the share of a
# `prevents:` line's distinctive words that may already appear in the same
# node's `description:`. Setting it to 0.99 disabled the check with
# `ratchet-lint` and `seed-lint` both green — a limit outside the ratchet is a
# limit that can be moved in a change about something else, which is the whole
# of what the ratchet exists to stop.
PREVENTS_RESTATEMENT_CEILING = 0.60
# Lines of frontmatter on a routable node. A node is loaded WHOLE, and until
# 7.16.0 only its body was bounded: 2 000 lines of frontmatter on one node
# passed every gate in the suite.
FRONTMATTER_CEILING = 100
# Below this many distinctive words a `prevents:` cannot be meaningfully
# compared. It is a FLOOR that produces findings, not a filter that hides them.
PREVENTS_MIN_WORDS = 6
# and in neither the name, the routing_triggers, nor the description. It was 27
# when first measured and 12 after 7.16.0's additions; each survivor is
# deliberate and named in docs/plans/router-lexical-reach/evidence-reach.md:
# `security`/`scan` and `security`/`keys` were MEASURED to cost an adversarial
# row (a deploy pipeline's scan step is reliability's, and "signing keys"
# reached "signed documentation"), `architect`/`legal` and
# `orchestrator`/`specify` would collide with a roster member and a protocol of
# that name, `ui-ux-designer`/`criteria` belongs to `product` by that charter's
# own words, and the rest are generic. A ceiling, so it may only fall: closing a
# hole is free, and opening one has to be argued.
#
# The bound, stated because it is the part that misleads: this measures only
# DISTINCTIVE holes. It cannot see a word that is common across charters and
# still the agent's defining term — `docs-librarian` was unreachable by
# "document" while scoring 0 here. That class is found by rewording tasks, and
# is held by the golden corpus instead.
CHARTER_VOCAB_DEBT = 12


# Named explicitly rather than derived. The three are a closed set fixed by
# what they do — carry the seed outward, grow a plant from it, fold lessons
# back — not by any property of their text, so there is nothing honest to
# derive it from. A fourth name here is an owner decision like the number is.
LIFECYCLE_NODES = frozenset({
    "protocols/graft.md",
    "protocols/grow.md",
    "protocols/harvest.md",
})

# EAGER_BUDGET bounds what a harness loads on EVERY session before any routing
# happens: the kernel, plus whatever roster/skill metadata that harness
# enumerates at start-up. 41_600 bytes is about 5.2x KERNEL_BUDGET (8_000),
# which is the room the roster and skill descriptions need at the current
# roster size.
EAGER_BUDGET = 41_600

# Named, dated, countable exemptions — the idiom legal-lint.py uses for edition
# debt: a surface that exceeds its budget today is ENUMERATED with its measured
# value, never waived by raising the budget to fit it. The gate reports the debt
# and fails if it GROWS, so the ledger can only shrink.
#
# github-copilot projects each skill as `.github/instructions/<name>-skill.md`
# carrying `applyTo: '**'`, which applies the file to every file in the
# workspace — so every skill BODY is always-on context there, not the
# descriptions the other harnesses enumerate. That was 112 280 of the 138 535
# bytes below, and it contradicts progressive discovery on the one harness that
# pays for it: the bodies already live in docs/graph/skills/ where a session
# reads them on demand. Narrowing the projection to a pointer is a change to
# what an installed plant receives, so it is the owner's call, recorded as
# decision 1 in docs/plans/grill-7.15.0-remediation.md §4.
# Per-skill boilerplate in a Copilot instruction file: the GENERATED header and
# the three-line pointer. Measured from an install, not guessed; it is here so
# the modelled figure tracks what actually ships rather than drifting below it.
# 5_638 -> 5_644 when the frontmatter readers were consolidated: the shared
# reader strips the surrounding quotes off a quoted scalar and seed-lint's
# old parser did not, so skill_desc fell 8435 -> 8429 across three quoted
# descriptions at two bytes each (context-router, holistic-editing,
# validate-knowledge). The quotes are YAML syntax, not description text, so
# the new figure is the more correct one and the constant follows it. The
# modelled eager surface is unchanged at 31 893 — six bytes moved from one
# term to the other.
COPILOT_POINTER_OVERHEAD = 5_644

EAGER_EXEMPTIONS: dict[str, tuple[int, str]] = {
    # Empty, and that is the point. github-copilot sat here at 138 535 bytes
    # because its skill projections shipped whole bodies as always-applied
    # context. Narrowing them to pointers took it to 31 893, under the
    # 32 000 budget every other harness already met, so the debt is discharged
    # rather than carried. An entry returning here means a harness has started
    # paying for something it has not earned.
}

# 6.0.0: the eight rules' full statements live in (only) these machinery
# nodes; the kernel keeps one-line anchors. Each rule fact-key must be
# owned by exactly this file and no other.
RULE_HOMES = {
    "rule.spec": "protocols/specify.md",
    "rule.knowledge": "skills/context-router/SKILL.md",
    "rule.grill": "protocols/grill.md",
    "rule.test-first": "protocols/test-first.md",
    "rule.verify": "protocols/verify.md",
    "rule.deliver": "protocols/deliver.md",
    "rule.canonize": "protocols/canonize.md",
    "rule.toolcraft": "skills/toolcraft/SKILL.md",
}
# 6.4.0: "installed but not spawnable" — a harness registers agent types when a
# SESSION STARTS, so the session that installs a roster cannot spawn it. The rule
# has one home and a fixed set of referrers: every surface that dispatches a
# specialist by name or installs the projection they come from. A referrer that
# drops the pointer silently re-opens the trap, so the fact key IS the
# machine-checkable pointer (the same referenced-never-paraphrased discipline the
# bootstrap-block check enforces).
REGISTRATION_FACT = "delegation.harness-registration"
REGISTRATION_HOME = "core/method/delegation.md"
REGISTRATION_REFERRERS = (
    # protocols that install the projection and/or dispatch by name
    "protocols/grow.md",
    "protocols/graft.md",
    "protocols/from-scratch.md",
    "protocols/initialize.md",
    "protocols/specify.md",
    "protocols/canonize.md",
    "protocols/recover.md",      # the node a failed dispatch actually lands on
    "protocols/deliver.md",      # the gate that must see a declared emulation
    # agents that install it or route to it
    "agents/00-orchestrator.md",
    "agents/growth-orchestrator.md",
    "agents/seed-installer.md",
    # the handback that carries the declaration
    "templates/prompts/handback-payload.md",
    # entry surfaces and installers
    "INSTALL_PROMPT.md",
    "GRAFT_PROMPT.md",
    "INSTALL.md",
    "README.md",
    "install.sh",
    # per-host docs that own the enumeration mechanism, and the router that
    # names specialists off disk rather than out of the session registry
    "integrations/claude-code/README.md",
    "integrations/claude-code/agent-lint.py",
    "integrations/opencode/README.md",
    "integrations/codex/README.md",
    "integrations/github-copilot/README.md",
    "integrations/prime-agent/README.md",
)
WORD_NUMS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
             "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
             "sixteen": 16, "seventeen": 17}

# SPEC-0004, the front door: the limits its checks hold (§6 "Constants"). The
# first-screen marker and the first install.sh command are recorded at the
# lines the README increment measured, with no headroom; the caps themselves
# live only in the spec's §6 table, which check_fd_first_screen_order reads, so
# raising a cap is a spec change a lock edit cannot make.
FRONT_DOOR_SPEC = "docs/specs/SPEC-0004-front-door.md"
FIRST_SCREEN_MARKER = "<!-- first-screen-end -->"
FIRST_HEADING_MAX_LINE = 6
FIRST_SCREEN_MAX_LINES = 53
FIRST_COMMAND_LINE = 46
FRONT_DOOR_RELEASE = "7.29.0"   # from this manifest version the ledger is empty
README_CATALOG_CEILING = 3      # distinct names per category README may name
LIMITS_MIN_REQUESTED = 3
LIMITS_MIN_UNMEASURED = 2
DEFINITION_OVERLAP_CEILING = 0.50
DEFINITION_SHINGLE = 3          # content tokens per shingle
DEFINITION_MIN_TOKENS = 5       # below this a definition is compared whole
BODY_FIGURE_HOME = "DOCUMENTATION.md"
# The project-node body ceiling in templates/knowledge-graph/graph-lint.py, a
# different fact from the seed's own body figures; each value must still occur
# there as a literal, so the exemption cannot outlive the ceiling it names.
PROJECT_NODE_LINE_FIGURES = frozenset({150, 170})

# The pending ledger: every SPEC-0004 contract observed failing on the shipped
# tree while the front-door prose is rewritten. A member prints one PENDING line
# and leaves the exit status alone; a member whose check finds nothing is itself
# a finding, so a slug leaves in the commit that clears it. Mirrored in
# tests/ratchets.json (`set`: members only leave), and empty once SPEC-0004 is
# `implemented` or the manifest reaches FRONT_DOOR_RELEASE.
FRONT_DOOR_PENDING = frozenset()

findings: list[str] = []


def fail(msg: str) -> None:
    findings.append(msg)


def load_tool(filename: str):
    """Import a seed tool as a module so its rules have one home. seed-lint
    checks the seed against the same code the plants are held to, rather than a
    restatement of it that can drift.

    A bare filename names a tool under `tools/`; a path with a separator is
    read relative to the seed root, which is how the graph engine that ships
    inside `templates/knowledge-graph/` is reached."""
    path = ROOT / filename if "/" in filename else ROOT / "tools" / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:      # pragma: no cover - unreachable
        raise SystemExit(f"seed lint: cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    # Registered before execution: a module defining a @dataclass looks itself
    # up in sys.modules while the decorator runs, and an unregistered module
    # fails there rather than at import.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_agnosticism_lint():
    """The agnosticism scan is shared machinery — `tools/agnosticism-lint.py`,
    which any project-agnostic tree can run on its own. The seed does not keep
    a second copy of it; it calls it and renders the findings in its own voice.
    Loaded by path because the file is named as a CLI, not as a module."""
    return load_tool("agnosticism-lint.py")


def frontmatter_block(path: Path) -> str:
    """The YAML frontmatter's text, and nothing else. A template may open with
    an HTML header comment, so the block is located by its delimiters rather
    than assumed to start the file — and a worked example further down carries
    the same keys at column 0, which is exactly what a whole-file match would
    accept in place of the frontmatter that has to carry them."""
    lines = path.read_text(encoding="utf-8").split("\n")
    try:
        start = lines.index("---")
        end = lines.index("---", start + 1)
    except ValueError:
        return ""
    return "\n".join(lines[start + 1:end])


# Words a `prevents:` line and a `description:` will share for grammatical
# reasons rather than because one restates the other.
_PREVENTS_STOP = frozenset("""
this that with from into when what which where whose there their them they
node nodes seed plant graph session sessions task tasks work works never
always every each only also because rather than without after before
""".split())

def parse_frontmatter(path: Path) -> dict:
    """Delegates to the one frontmatter reader. Keeps the `_body` key callers use.

    This held its own parser, one of seven. It was permissive BY ACCIDENT: a
    line matching neither its `key:value` regex nor its list-item regex simply
    fell through the loop and was dropped, so a description continued on a
    second line lost its continuation with no error and no finding. The shared
    reader raises instead.
    """
    text = path.read_text(encoding="utf-8")
    try:
        meta, body = _frontmatter.parse(text, path)
    except _frontmatter.FrontmatterError as e:
        fail(str(e))
        return {}
    meta["_body"] = body
    return meta


def check_plan_ledgers() -> None:
    """A split plan's index and its files must agree.

    `grill-lint.py` enforces this for a PLANT, whose plan is one file at
    `docs/graph/plans/grill.md` in the template's `## N.` section shape. The
    seed's own plans are neither: there are many of them, named per body of
    work, and they use `## §N` headings deliberately (CLAUDE.md — the seed keeps
    its self-docs outside docs/graph/). Pointing grill-lint at them would mean
    rewriting every one of them to a convention they were never written in, which is
    a different project, not a check.

    What IS shared is the ledger invariant, and it is the part a split can
    actually get wrong: an index row pointing at a file that is not there, or a
    file nobody indexes. The second is the dangerous one — work that exists,
    reads as progress, and is unreachable. So that much is checked here, in the
    seed's own terms.

    A plan with no sibling directory is not in ledger form and is skipped.
    """
    plans = ROOT / "docs" / "plans"
    if not plans.is_dir():
        return
    for index in sorted(plans.glob("*.md")):
        children_dir = plans / index.stem
        if not children_dir.is_dir():
            continue
        text = index.read_text(encoding="utf-8", errors="replace")
        for child in sorted(children_dir.glob("*.md")):
            if child.name not in text:
                fail(f"docs/plans/{index.stem}/{child.name} is not referenced by "
                     f"{index.name} — a record nobody points at is unreachable, "
                     f"and reads as work that was done")
        for ref in sorted(set(re.findall(
                rf"{re.escape(index.stem)}/([A-Za-z0-9._-]+\.md)", text))):
            if not (children_dir / ref).is_file():
                fail(f"{index.name} points at {index.stem}/{ref}, which does not "
                     f"exist — an index row is a promise the record is written down")


def _classification_names(path: Path) -> set:
    """The ALL-CAPS classification names a tool actually prints.

    Read out of the source text rather than imported: graft-audit.py builds its
    vocabulary as `counts = {"IDENTICAL": 0, ...}` inside a function, so there is
    no module-level constant to import, and adding one purely so a linter can
    read it would put the tool's shape at the linter's convenience.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    # Two idioms, because the tool uses two: keys of the counts dict, and the
    # verdict word that opens a printed line ("  UNRESOLVED — 3 backup(s) ...").
    # Reading only the dict misses UNRESOLVED and UNFILLED, which are verdicts a
    # steward sees and a protocol may legitimately name.
    named = set(re.findall(r'"([A-Z][A-Z-]{3,})"', text))
    # `f"  UNRESOLVED — ..."` and `f"  UNFILLED {path}"`: the verdict word opens
    # the printed line. Anchor on that position rather than on what follows it,
    # because the two verdicts differ in exactly what follows.
    printed = set(re.findall(r'f"\s+([A-Z][A-Z-]{3,})\b', text))
    return named | printed


def check_protocol_reference() -> None:
    """`documentation/protocols-reference.md`'s table must match the nodes.

    The table restates four frontmatter fields — owns, requires, peers,
    est_tokens — for every protocol, by hand. When this check was first
    written, THIRTEEN of the rows were stale: `verify` was missing eight
    owned facts, `grill` three, `canonize` three, and every `est_tokens` in the
    table was the value from whenever someone last remembered. It had drifted
    quietly for many releases because nothing compared it to anything.

    `seed-lint` already holds the manifest, the kernel roster line and README to
    the agent frontmatter. This is the same check one table over, and it exists
    because a reference someone reads instead of the node is a second home for
    the fact — the exact defect the lifecycle-protocol rework was closing inside
    the protocols themselves while the table describing them said otherwise.
    """
    ref = ROOT / "documentation" / "protocols-reference.md"
    if not ref.is_file():
        fail("documentation/protocols-reference.md is missing — the protocol "
             "reference is part of the seed's self-docs, not optional")
        return
    nodes = {fm["id"]: fm for label, fm, _b in machinery_nodes()
             if label.startswith("protocols/")}
    seen = set()
    row = re.compile(r"^\|\s*([a-z-]+)\s*\|\s*`(protocol\.[a-z-]+)`\s*\|(.*)\|"
                     r"\s*(\d+)\s*\|\s*$")
    for line in ref.read_text(encoding="utf-8", errors="replace").splitlines():
        m = row.match(line)
        if not m:
            continue
        name, pid, middle, tokens = m.group(1), m.group(2), m.group(3), int(m.group(4))
        fm = nodes.get(pid)
        if fm is None:
            fail(f"protocols-reference.md lists {pid}, which is not a protocol "
                 f"node — a row for a node that does not exist is a reader's "
                 f"dead end")
            continue
        seen.add(pid)
        if int(fm["est_tokens"]) != tokens:
            fail(f"protocols-reference.md row {name}: est_tokens {tokens}, but "
                 f"{pid} declares {fm['est_tokens']} — the node is the home; "
                 f"regenerate the row, never the other way round")
        cells = [c.strip() for c in middle.split("|")]
        listed = set(re.findall(r"`([a-z][a-z0-9.-]+)`", cells[0]))
        owns = set(fm.get("owns") or [])
        if listed != owns:
            missing, extra = sorted(owns - listed), sorted(listed - owns)
            fail(f"protocols-reference.md row {name}: owns disagrees with "
                 f"{pid} — missing {missing}, extra {extra}")
    for pid in sorted(set(nodes) - seen):
        fail(f"protocols-reference.md has no row for {pid} — a protocol absent "
             f"from the reference is one a reader of the reference cannot know "
             f"exists")

    # The per-protocol sections restate the same four fields a second time, so a
    # reader of one protocol need not scroll to the table. Two views, one home:
    # both are held here. Fixing only the table would leave the stale copy the
    # reader of that section actually sees — which is how `verify` came to be
    # listed with three of its eleven owned facts in both places at once.
    text = ref.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(
        r"^- \*\*id:\*\* `(protocol\.[a-z-]+)`[^\n]*\n((?:(?:- \*\*(?:owns|requires|"
        r"peers|load_when):\*\*|  )[^\n]*\n)+)", text, re.M)
    for pid, block in blocks:
        fm = nodes.get(pid)
        if fm is None:
            continue
        flat = " ".join(block.split())
        for field in ("owns", "requires", "peers"):
            want = set(fm.get(field) or [])
            seg = re.search(rf"\*\*{field}:\*\*(.*?)(?:- \*\*|$)", flat)
            got = set(re.findall(r"`([a-z][a-z0-9.-]+)`", seg.group(1))) if seg else set()
            if want != got:
                fail(f"protocols-reference.md section for {pid}: {field} "
                     f"disagrees with the node — missing {sorted(want - got)}, "
                     f"extra {sorted(got - want)}")
        want_lw = fm.get("load_when") or []
        seg = re.search(r"\*\*load_when:\*\*(.*?)$", flat)
        got_lw = re.findall(r'"([^"]+)"', seg.group(1)) if seg else []
        if [" ".join(x.split()) for x in want_lw] != got_lw:
            fail(f"protocols-reference.md section for {pid}: load_when lists "
                 f"{len(got_lw)} trigger(s), the node declares {len(want_lw)} — "
                 f"a routing trigger missing from the reference is one a reader "
                 f"of the reference will not know routes here")
    for pid in sorted(set(nodes) - {b[0] for b in blocks}):
        fail(f"protocols-reference.md has no per-protocol section for {pid}")

    # A field stated twice in one section is the failure this check exists to
    # prevent, and the block capture above cannot see it: it stops at the first
    # non-field bullet, so a second copy sitting after `- **artifacts:**` reads
    # as absent. That happened — three sections carried two `load_when:` bullets,
    # the fresh one before `artifacts:` and the original after it, and this check
    # reported PASS over the duplicate. Scan the whole section instead.
    sections = re.split(r"^- \*\*id:\*\* `protocol\.", text, flags=re.M)[1:]
    for sec in sections:
        pid = "protocol." + sec.split("`", 1)[0]
        for field in ("owns", "requires", "peers", "load_when"):
            n = len(re.findall(rf"^- \*\*{field}:\*\*", sec, re.M))
            if n > 1:
                fail(f"protocols-reference.md section for {pid}: `{field}` is "
                     f"stated {n} times — a field with two homes in the document "
                     f"whose purpose is one home, and the reader sees whichever "
                     f"copy they reach first")


# The classes a gate row may declare, in ADR-0003's vocabulary: hard = a harness
# refuses, soft = a contract refuses, detective = caught after the fact,
# judgment = a named human or agent decides and no tool can.
GATE_CLASSES = frozenset({"hard", "soft", "detective", "judgment"})


def check_file_endings() -> None:
    """Every machinery node ends with exactly one newline.

    `protocols/graft.md` lost its trailing newline to a hand re-wrap, and
    nothing in the gate noticed — reading a file cannot show you a newline that
    is not there, so the author's "I verified it by reading it" was structurally
    unable to find it. POSIX text files end with one; a missing one makes `cat`
    of two files run them together and shows up as a spurious hunk in every
    later diff.
    """
    for label, _fm, _body in machinery_nodes():
        raw = (ROOT / label).read_bytes()
        if not raw:
            fail(f"{label} is empty")
        elif not raw.endswith(b"\n"):
            fail(f"{label} does not end with a newline — a hand re-wrap drops "
                 f"this silently and no amount of reading the file reveals it")
        elif raw.endswith(b"\n\n\n"):
            fail(f"{label} ends with blank lines — one trailing newline, not a "
                 f"gap someone's editor left behind")


def check_gate_single_home() -> None:
    """A lifecycle protocol's gates live in its table, and its pointers resolve.

    Before the 7.16.0 rework each gate in these three files was written between
    two and eight times: graft stated every gate once as Phase 7 prose and again
    as an integrity-gate template row, so every gate added since 6.12.0 had to be
    written twice in the same commit; harvest carried each Phase 4 gate in five
    places and the agnosticism rule in eight. That is the growth engine the
    rework removed, and it is also the defect these protocols instruct a plant to
    fix in its own graph.

    What is checked mechanically, and what is not:

    - Every `<protocol>.gate.<slug>` id is DECLARED exactly once, in a table row
      carrying a class from GATE_CLASSES. A second declaration is the duplicate
      home returning.
    - Every reference to a gate id elsewhere in the file RESOLVES to a declared
      row. A dangling pointer is how a phase and a table drift apart without
      either looking wrong on its own.
    - No row declares a class outside the vocabulary, and none leaves the class
      cell blank. A gate with no class is one nobody has decided is enforceable.

    NOT checked — the list is longer than the one limit first recorded here, and
    a review found the rest, which is itself the argument for writing them down:

    - Whether a row's *assertion* is restated in prose elsewhere in the file.
      Detecting that needs phrase matching, and phrase matching is how the last
      drift check in this repository was fooled: it passed on reworded text. The
      ids are the contract; restating a gate's substance defeats this check.
    - An **unbackticked** mention (`graft.gate.backups` written bare) is
      invisible to both the declaration and the reference scan.
    - References are stem-bound: a gate named from any file other than the three
      is not checked at all, so a skill or agent may cite a gate that no longer
      exists.
    - A fenced code block is scanned like prose, so an example naming a gate id
      reads as a live reference.
    - "One table" is not enforced despite the failure text saying so: three
      one-row tables satisfy every rule here. Nor can the file carry a
      cross-reference table, since any line starting with `|` is a declaration.
    - The class is the last cell, so a row with a trailing column after the class
      is misread. Emphasis and case are normalised; a trailing gloss is not.
    - A `judgment` row must carry the literal marker `Judge:` in its Command
      cell. Whether the name after it is a real, reachable judge is not checked —
      fifteen of sixteen rows named one in prose before the marker existed, and
      the sixteenth read as if it did, which is why the marker is the contract
      rather than the prose. The cell is checked because the first cut of this
      rule searched the whole joined row and passed thirteen markers sitting in
      the wrong column.
    """
    declared: dict[str, str] = {}
    for label in sorted(LIFECYCLE_NODES):
        path = ROOT / label
        if not path.is_file():
            # This was a `continue` with a comment claiming check_body_ceiling's
            # probe covered membership. There is no such probe: that check globs
            # `protocols/*.md`, so a renamed node is simply yielded under a
            # different label and a deleted one is absent. Renaming graft.md made
            # this whole check report nothing, with the 1000-line machinery
            # ceiling as the only accidental backstop — which grow and harvest
            # do not breach. A named node that is not there is a defect, not a
            # skip.
            fail(f"{label} is named in LIFECYCLE_NODES but is not a file — a "
                 f"renamed or deleted lifecycle node silently drops out of every "
                 f"gate check that names it")
            continue
        stem = Path(label).stem
        body = body_of(path)
        rows, refs, widths = {}, set(), {}
        for line in body.splitlines():
            ids = re.findall(rf"`({re.escape(stem)}\.gate\.[a-z0-9-]+)`", line)
            if not ids:
                continue
            if line.lstrip().startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                # Column count, because a cell is not the only thing that can
                # break. A shell pipe written into a Command cell splits the row
                # into extra columns, and reading only cells[-1] validated the
                # class of a row that was structurally broken — the class landed
                # in what used to be a different column and still parsed. Found
                # by an author whose own first pass did it. Rows in one table
                # must agree; the modal width is the table's.
                widths.setdefault(len(cells), []).append(ids[0])
                gid = ids[0]
                if gid in rows:
                    fail(f"{label}: gate id `{gid}` is declared twice — a second "
                         f"declaration is the duplicate home the gate table exists "
                         f"to remove")
                # Tolerate `**soft**` and `Soft`: the cell's job is to name a
                # class, and rejecting a bolded or capitalised one teaches
                # authors to fight the parser rather than to classify honestly.
                cls = re.sub(r"[`*_ ]", "", cells[-1]).lower() if cells else ""
                if cls == "hard":
                    fail(f"{label}: gate `{ids[0]}` declares class `hard`. No "
                         f"harness prevents a steward applying an upgrade, "
                         f"delivering a growth or committing a harvest — see the "
                         f"2026-09-14 Amendment to ADR-0003. A linter someone may "
                         f"decline to run is a contract, so this is `soft`")
                elif cls not in GATE_CLASSES:
                    fail(f"{label}: gate `{gid}` declares class {cls!r}, not one "
                         f"of {sorted(GATE_CLASSES)} — a gate with no class is one "
                         f"nobody has decided is enforceable")
                # cells[-3] is the Command column in both row shapes. `cells`
                # here has already had its outer pipes stripped before the split,
                # so a five-column graft/grow row is [id, asserts, command,
                # on-failure, class] and a six-column harvest row prefixes a
                # display number — Command is third from last in each. Two ways
                # to get this wrong were both hit while writing it: checking the
                # JOINED row passed thirteen markers sitting in the On-failure
                # cell, and counting from a RAW split (which keeps a leading and
                # trailing empty) lands on `asserts` instead.
                if cls == "judgment" and "Judge:" not in cells[-3]:
                    fail(f"{label}: gate `{ids[0]}` is `judgment` and names no "
                         f"judge — write `Judge: <who>` in the Command cell. A "
                         f"judgment nobody owns is not an enforcement class, it "
                         f"is an unassigned intention")
                rows[gid] = cls
                refs.update(ids[1:])
            else:
                refs.update(ids)
        if not rows:
            fail(f"{label}: no gate table found — a lifecycle protocol states its "
                 f"gates in one table, by id, so adding one is a single edit")
            continue
        if len(widths) > 1:
            modal = max(widths, key=lambda w: len(widths[w]))
            for w, gids in sorted(widths.items()):
                if w == modal:
                    continue
                fail(f"{label}: gate row(s) {sorted(gids)} have {w} columns "
                     f"where the table has {modal} — a pipe inside a cell (a "
                     f"shell command, an or-list) splits the row, and every "
                     f"cell after it is read as the wrong column")
        for gid in sorted(refs - set(rows)):
            fail(f"{label}: references gate `{gid}`, which no table row declares "
                 f"— a pointer with no target is how a phase and its table drift "
                 f"apart without either looking wrong alone")
        for gid, cls in rows.items():
            if gid in declared:
                fail(f"{label}: gate id `{gid}` is also declared in "
                     f"{declared[gid]} — gate ids are global, like `owns`")
            declared[gid] = label


def check_charter_vocabulary() -> None:
    """An agent must be reachable by the words its own charter leans on.

    The router scores a task against each agent's name, routing_triggers and
    description. A word an agent's body uses over and over, that few other
    charters use, and that appears in none of those three, is a door with no
    handle: the agent is written for that work and no phrasing of it arrives.

    Measured at 27 across 19 agents when introduced — `docs-librarian` had no
    `document`, `documentation`, `written` or `record`; `security` had no
    `vulnerability`, and both are closed now. The CURRENT ceiling is
    `CHARTER_VOCAB_DEBT`, which is where the live figure belongs: this
    docstring held 27 for three releases while the constant beside it said 12,
    so the same file carried both the right and the wrong version of one fact,
    550 lines apart.
    """
    holes = _charter_vocabulary_holes()
    total = sum(len(v) for v in holes.values())
    if total > CHARTER_VOCAB_DEBT:
        listed = "; ".join(f"{a}: {', '.join(w)}"
                           for a, w in sorted(holes.items()))
        fail(f"{total} charter words are unreachable by the router, over the "
             f"recorded {CHARTER_VOCAB_DEBT} — {listed}. Put the word in the "
             f"agent's routing_triggers if the charter means it, and if it does "
             f"not, take it out of the charter; do not raise the ceiling")


def _charter_vocabulary_holes() -> dict:
    """agent -> words its charter leans on that no task can route on.

    Leans on: used at least 5 times in that agent's own body, by no more than
    four charters in total, and matching nothing in that agent's name,
    routing_triggers or description.
    """
    import collections
    agent_lint = ROOT / "integrations/claude-code/agent-lint.py"
    mod = types.ModuleType("_seedlint_agent_lint")
    mod.__file__ = str(agent_lint)
    sys.modules[mod.__name__] = mod
    exec(compile(agent_lint.read_text(encoding="utf-8"),
                 str(agent_lint), "exec"), mod.__dict__)
    agents = mod.load_agents(ROOT / "agents")

    bodies, body_df = {}, collections.Counter()
    for a in agents:
        toks = [w for w in re.findall(r"[a-z][a-z0-9_-]{3,}", a.body.lower())
                if w not in mod.STOPWORDS]
        bodies[a.name] = collections.Counter(toks)
        body_df.update(set(toks))

    out = {}
    for a in agents:
        name, trig, desc = mod._token_sets(a)
        reach = {k: 2 for k in set(name) | set(trig) | set(desc)}
        words = sorted(w for w, c in bodies[a.name].items()
                       if c >= 5 and body_df[w] <= 4 and mod._match(w, reach) == 0)
        if words:
            out[a.name] = words
    return out


def check_reference_second_views() -> None:
    """Every reference document states its facts in MORE THAN ONE view.

    Round 2 of an adversarial review repaired the per-agent sections and left
    the summary table; repaired the Delegation bullet and left the coordinator
    edge-list table; repaired the skills summary table and left "Roles at a
    glance" twenty lines below. Six findings, one generator: a check that reads
    one view per document licenses the other views to drift.

    The first version of THIS function then reproduced the defect it was
    written for. Its edge-table regex demanded `agent.architect` where the
    table writes `architect` — zero matches, an inert check, and the row it
    guarded was already stale. Neither table view had a completeness pass, so
    deleting a row was invisible; a row missing its leading number column was
    skipped silently; and "Roles at a glance" was a token scan over raw prose
    behind an unanchored heading. All four are closed below, and each is
    exercised by tests/test-seed-lint.sh.
    """
    ag = ROOT / "documentation" / "agents-reference.md"
    sk = ROOT / "documentation" / "skills-and-templates-reference.md"
    if not (ag.is_file() and sk.is_file()):
        return
    agents = {fm["id"]: fm for label, fm, _b in machinery_nodes()
              if label.startswith("agents/")}
    skills = {fm["id"]: fm for label, fm, _b in machinery_nodes()
              if label.startswith("skills/")}
    at, st = ag.read_text(encoding="utf-8"), sk.read_text(encoding="utf-8")

    def norm(names):
        return {n if n.startswith("agent.") else f"agent.{n}" for n in names}

    # (1) agents-reference §6 summary table: the `owns` column, and every agent
    #     must have a row (deleting one used to be invisible).
    seen_rows = set()
    for line in at.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|\s*`[a-z-]+`", line):
            # a row that LOOKS like a roster row but does not parse is a
            # silently-skipped check, so refuse it rather than ignore it
            if re.match(r"^\|\s*`(agent\.)?[a-z-]+`\s*\|\s*`agent\.[a-z-]+`", line):
                fail(f"agents-reference summary table: row is missing its index "
                     f"column, which makes the owns check skip it silently: "
                     f"{line[:70]}")
            continue
        m = re.match(r"^\|\s*\d+\s*\|\s*`([a-z-]+)`\s*\|\s*`(agent\.[a-z-]+)`\s*\|(.*)\|\s*$", line)
        if not m:
            fail(f"agents-reference summary table: unparsable row: {line[:70]}")
            continue
        fm = agents.get(m.group(2))
        if fm is None:
            fail(f"agents-reference summary table lists {m.group(2)}, not a node")
            continue
        seen_rows.add(m.group(2))
        listed = set(re.findall(r"`([a-z][a-z0-9._-]+)`", m.group(3).split("|")[-1]))
        declared = set(fm.get("owns") or [])
        if listed != declared:
            fail(f"agents-reference summary table: {m.group(1)} owns disagrees "
                 f"with frontmatter — missing {sorted(declared - listed)}, "
                 f"extra {sorted(listed - declared)}")
    for aid in sorted(set(agents) - seen_rows):
        fail(f"agents-reference summary table has no row for {aid} — a roster "
             f"member absent from the table is one a reader cannot find")
    # Read the count wherever it lands in the heading. `if hdr and ...` made
    # the claim optional on its own wording: "## 6. Summary table (14 agents)"
    # passed with a 20-row table under it.
    h6 = re.search(r"^## 6\..*$", at, re.M)
    if not h6:
        fail("agents-reference has no '## 6.' summary-table heading")
    else:
        n = re.search(r"(\d+)\s+agents", h6.group(0))
        if not n:
            fail(f"agents-reference §6 heading states no agent count: "
                 f"{h6.group(0)!r} — the count is the claim being checked")
        elif int(n.group(1)) != len(agents):
            fail(f"agents-reference §6 heading says {n.group(1)} agents; "
                 f"agents/ has {len(agents)}")

    # (2) the coordinator edge-list table. The cells write bare names.
    seen_edges = set()
    for line in at.splitlines():
        m = re.match(r"^\|\s*`([a-z-]+)`\s*\|([^|]*)\|([^|]*)\|", line)
        if not m:
            continue
        nid = f"agent.{m.group(1)}"
        fm = agents.get(nid)
        if fm is None or not fm.get("delegates_to"):
            continue
        cells = m.group(2) + " " + m.group(3)
        if "`" not in cells:
            continue
        listed = norm(re.findall(r"`(?:agent\.)?([a-z-]+)`", cells))
        declared = norm(fm["delegates_to"])
        seen_edges.add(nid)
        if listed != declared:
            fail(f"agents-reference edge table: {m.group(1)} delegates_to "
                 f"disagrees with frontmatter — missing "
                 f"{sorted(declared - listed)}, extra {sorted(listed - declared)}")
    for aid, fm in sorted(agents.items()):
        if fm.get("delegates_to") and aid not in seen_edges:
            fail(f"agents-reference edge table has no row for {aid}, which "
                 f"declares delegates_to — an absent row is not an agreeing one")

    # (3) skills "Roles at a glance": read the TABLE CELLS, not the prose
    #     around them, and require the marker to exist. Two regex attempts got
    #     this wrong — one demanded a `#` heading the file does not use, and
    #     `re.S` let `.*` span from an earlier heading — so it is line-based.
    lines = st.splitlines()
    def _owns_grouping(i):
        # the marker that owns the grouping is the one followed (within two
        # blank-ish lines) by a table whose header is Group/Skills
        for l in lines[i + 1:i + 4]:
            if l.startswith("|") and "group" in l.lower() and "skill" in l.lower():
                return True
        return False
    cands = [i for i, l in enumerate(lines) if l.strip().startswith("Roles at a glance")]
    owning = [i for i in cands if _owns_grouping(i)]
    if cands and not owning:
        fail("skills-reference: 'Roles at a glance' names no Group/Skills table "
             "— a forward reference to another table makes the completeness "
             "check read that table instead, and it can never fail")
    idx = owning[0] if owning else None
    if idx is None:
        fail("skills-reference: no 'Roles at a glance' grouping — removing or "
             "renaming it silently removes the completeness check with it")
    else:
        cells = []
        for l in lines[idx + 1:]:
            if l.startswith("|"):
                cells.append(l)
            elif cells and not l.strip():
                break
        if not cells:
            fail("skills-reference: 'Roles at a glance' has no table rows")
        named = set(re.findall(r"[a-z][a-z-]{3,}", " ".join(cells)))
        for sid in skills:
            n = sid.split(".", 1)[1]
            if n not in named:
                fail(f"skills-reference 'Roles at a glance' omits {n} from its "
                     f"table rows — a grouping that silently drops a skill is "
                     f"a partial list presented as a complete one")

    # (4) DOCUMENTATION.md's own skill list
    doc = ROOT / "DOCUMENTATION.md"
    if doc.is_file():
        dt = doc.read_text(encoding="utf-8")
        blk = re.search(r"### 8\.1 The (\d+) skills(.*?)(?=\n### |\n## )", dt, re.S)
        if not blk:
            fail("DOCUMENTATION.md has no '### 8.1 The N skills' section")
        else:
            if int(blk.group(1)) != len(skills):
                fail(f"DOCUMENTATION.md §8.1 heading says {blk.group(1)} skills; "
                     f"skills/ has {len(skills)}")
            named = set(re.findall(r"`([a-z][a-z-]+)`", blk.group(2)))
            for sid in skills:
                n = sid.split(".", 1)[1]
                if n not in named:
                    fail(f"DOCUMENTATION.md §8.1 omits `{n}` — the heading "
                         f"states a count the list does not meet")


def check_skills_reference() -> None:
    """`documentation/skills-and-templates-reference.md` mirrors skill frontmatter.

    `check_protocols_reference` holds the same two views for protocols and has
    since 7.16.0. Nothing held them for skills, and an adversarial pass found
    the cost: 8 of 15 `est_tokens` cells wrong, three `owns`/`peers` lists
    stale in BOTH the summary table and the per-skill section, and two skills
    added in this release missing from a "Roles at a glance" grouping. Every
    one of them passed `seed lint: PASS`.

    The frontmatter is the home. Both views follow it.
    """
    ref = ROOT / "documentation" / "skills-and-templates-reference.md"
    if not ref.is_file():
        fail("documentation/skills-and-templates-reference.md is missing")
        return
    nodes = {fm["id"]: fm for label, fm, _b in machinery_nodes()
             if label.startswith("skills/")}
    text = ref.read_text(encoding="utf-8", errors="replace")

    def facts(cell: str, owner: str) -> set:
        # the table abbreviates `adopt-existing.refresh` as `.refresh`
        out = set()
        for tok in re.findall(r"`([a-z.][a-z0-9.-]*)`", cell):
            out.add(f"{owner}{tok}" if tok.startswith(".") else tok)
        return out

    seen = set()
    row = re.compile(r"^\|\s*([a-z-]+)\s*\|\s*`(skill\.[a-z-]+)`\s*\|(.*)\|"
                     r"\s*(\d+)\s*\|\s*$")
    for line in text.splitlines():
        m = row.match(line)
        if not m:
            continue
        name, sid, middle, tokens = m.group(1), m.group(2), m.group(3), int(m.group(4))
        fm = nodes.get(sid)
        if fm is None:
            fail(f"skills-reference: table lists {sid}, which is not a skill node")
            continue
        seen.add(sid)
        if int(fm["est_tokens"]) != tokens:
            fail(f"skills-reference row {name}: est_tokens {tokens}, but {sid} "
                 f"declares {fm['est_tokens']} — the node is the home")
        cells = [c.strip() for c in middle.split("|")]
        if len(cells) < 3:
            fail(f"skills-reference row {name}: {len(cells)} mirrored column(s), "
                 f"expected owns/requires/peers — a removed column silently "
                 f"removes the check with it")
            continue
        for idx, key in ((0, "owns"), (1, "requires"), (2, "peers")):
            listed = facts(cells[idx], name)
            declared = set(fm.get(key) or [])
            if listed != declared:
                fail(f"skills-reference row {name}: {key} disagrees with {sid} "
                     f"— missing {sorted(declared - listed)}, "
                     f"extra {sorted(listed - declared)}")
    for sid in sorted(set(nodes) - seen):
        fail(f"skills-reference: no summary-table row for {sid}")

    # the per-skill A.N sections restate owns/requires/peers a second time
    for sid, fm in sorted(nodes.items()):
        name = sid.split(".", 1)[1]
        sec = re.search(rf"^## A\.\d+ {re.escape(name)}\n(.*?)(?=^## |\Z)",
                        text, re.M | re.S)
        if not sec:
            fail(f"skills-reference: no per-skill section for {name}")
            continue
        # the metadata paragraph runs to the first blank line; slicing a fixed
        # 900 characters was an untested truncation that could silently drop a
        # field off the end of a long one.
        head = sec.group(1).split("\n\n", 2)
        head = "\n\n".join(head[:2])
        for key in ("owns", "requires", "peers"):
            m = re.search(rf"\*\*{key}:\*\*(.*?)(?=·\s*\*\*|\n\n|\Z)", head, re.S | re.I)
            if not m:
                if fm.get(key):
                    fail(f"skills-reference §A {name}: no '{key}' in the metadata "
                         f"paragraph, but {sid} declares one — an absent mirror "
                         f"is not an agreeing one")
                continue
            listed = facts(m.group(1), name)
            declared = set(fm.get(key) or [])
            if listed != declared:
                fail(f"skills-reference §A {name}: {key} disagrees with {sid} "
                     f"— missing {sorted(declared - listed)}, "
                     f"extra {sorted(listed - declared)}")


def fmof(a) -> dict:
    """Frontmatter of an agent node, for keys the loader does not surface."""
    return parse_frontmatter(a.path) if getattr(a, "path", None) else {}


def check_agents_reference() -> None:
    """`documentation/agents-reference.md` mirrors two things; hold both.

    Per agent it restates the `routing_triggers` from that agent's frontmatter
    and the golden-corpus rows expecting it. Neither was checked, and the
    golden half had gone quietly wrong: every section listed only the original
    contract rows — 3 of `architect`'s 5, 2 of `legal`'s 7 — under a heading
    reading "every row expecting `architect`". A partial list presented as a
    complete one is the defect this repository spent a whole remediation on,
    sitting in the file that documents the roster.

    The frontmatter and the corpus are the homes; this file follows them.
    """
    ref = ROOT / "documentation" / "agents-reference.md"
    if not ref.is_file():
        fail("documentation/agents-reference.md is missing")
        return
    text = ref.read_text(encoding="utf-8", errors="replace")

    agent_lint = ROOT / "integrations/claude-code/agent-lint.py"
    mod = types.ModuleType("_seedlint_agent_lint_ref")
    mod.__file__ = str(agent_lint)
    sys.modules[mod.__name__] = mod
    exec(compile(agent_lint.read_text(encoding="utf-8"),
                 str(agent_lint), "exec"), mod.__dict__)
    rows, _classed = mod.load_golden(ROOT / "agents")
    golden: dict = {}
    for task, expected, cls in rows:
        golden.setdefault(expected, []).append((task, cls))

    for a in mod.load_agents(ROOT / "agents"):
        anchor = f"*Source file: `agents/{a.path.name}`*"
        i = text.find(anchor)
        if i < 0:
            fail(f"agents-reference has no section for {a.path.name} — a roster "
                 f"member the reference does not document")
            continue
        nxt = text.find("*Source file: `agents/", i + 1)
        section = text[i: nxt if nxt > 0 else len(text)]

        trig = re.search(r"- \*\*routing_triggers:\*\*\n((?:  - \".*\"\n)+)",
                         section)
        listed = re.findall(r'^  - "(.*)"$', trig.group(1), re.M) if trig else []
        if listed != a.triggers:
            fail(f"agents-reference: {a.name} routing_triggers do not match "
                 f"agents/{a.path.name} ({len(listed)} listed, "
                 f"{len(a.triggers)} in frontmatter) — the frontmatter is the "
                 f"home; the reference follows it")

        # The per-agent section also restates owns/requires/peers/delegates_to.
        # Only routing_triggers and the golden rows were held, and an
        # adversarial pass found 8 of 20 agents stale in the unheld fields —
        # `architect` missing `architect.legal-checkpoint` (cited by name 20
        # lines above), three agents missing their `*.spawn-scope`, `pentest`
        # showing `requires: —` against a real edge. Frontmatter is the home.
        def _listed(label):
            m = re.search(rf"^- \*\*{label}[^:]*:\*\*(.*?)(?=^- \*\*|\n\n)",
                          section, re.M | re.S | re.I)
            if m is None:
                return None
            if m.group(1).strip() in ("—", "-", "none", "(none)"):
                return set()
            return set(re.findall(r"`([a-z][a-z0-9._-]+)`", m.group(1)))

        # `delegates_to` is written inside the prose "- **Delegation:**" bullet,
        # not as its own field. An earlier version of this check looked for a
        # "- **delegates_to:**" line, found none, and skipped — passing
        # vacuously while the list was short by one. A field the reference
        # states in a different shape is still a mirrored field.
        deleg = re.search(r"^- \*\*Delegation:\*\*(.*?)(?=^- \*\*|\n\n)",
                          section, re.M | re.S)
        if deleg and "delegates_to" in deleg.group(1):
            tail = deleg.group(1).split("delegates_to", 1)[1]
            listed = {f"agent.{n}" for n in re.findall(r"`([a-z][a-z-]+)`", tail)}
            declared = {f"agent.{d}" for d in (fmof(a).get("delegates_to") or [])}
            if listed != declared:
                fail(f"agents-reference: {a.name} delegates_to disagrees with "
                     f"agents/{a.path.name} — missing "
                     f"{sorted(declared - listed)}, extra {sorted(listed - declared)}")
        elif fmof(a).get("delegates_to"):
            fail(f"agents-reference: {a.name} declares delegates_to in "
                 f"frontmatter but its Delegation bullet does not list it")

        for label, key in (("owns", "owns"), ("requires", "requires"),
                           ("peers", "peers")):
            listed = _listed(label)
            if listed is None:
                # A MISSING bullet is a finding, not a pass. Deleting the line
                # (or capitalising its label) used to remove the mirror check
                # along with the mirror — the same "an absent list is not an
                # empty one" defect the golden-rows check below was fixed for.
                if getattr(a, key, None) or fmof(a).get(key):
                    fail(f"agents-reference: {a.name} has no '{label}' bullet, "
                         f"but agents/{a.path.name} declares one — a mirror "
                         f"that is absent is not a mirror that agrees")
                continue
            declared = set(getattr(a, key, None) or fmof(a).get(key) or [])
            if key == "delegates_to":
                declared = {f"agent.{d}" if not d.startswith("agent.") else d
                            for d in declared}
                listed = {f"agent.{d}" if not d.startswith("agent.") else d
                          for d in listed}
            if listed != declared:
                fail(f"agents-reference: {a.name} {key} disagrees with "
                     f"agents/{a.path.name} — missing "
                     f"{sorted(declared - listed)}, extra {sorted(listed - declared)}")

        gold = re.search(
            r"- \*\*Golden routing tasks\*\*[^\n]*\n((?:  - \".*\"[^\n]*\n)+)",
            section)
        if not gold and golden.get(a.name):
            # `if gold:` alone was vacuous on ABSENCE: an agent whose block was
            # never written passed, because there was nothing to compare. That
            # is the same "partial list presented as complete" defect one level
            # up — a missing list reads as "no rows expect this agent".
            fail(f"agents-reference: {a.name} has no 'Golden routing tasks' "
                 f"block, but {len(golden[a.name])} corpus row(s) expect it — "
                 f"an absent list is not an empty one")
        if gold:
            shown = re.findall(r'^  - "(.*)" — `(.*)`$', gold.group(1), re.M)
            if shown != golden.get(a.name, []):
                fail(f"agents-reference: {a.name} golden rows do not match "
                     f"agents/_routes.golden.tsv ({len(shown)} listed, "
                     f"{len(golden.get(a.name, []))} in the corpus) — and each "
                     f"row must carry its class, because the classes measure "
                     f"different things and are never merged")


def _canonical_blocks_must_match(homes: tuple, what: str, why: str,
                           names: tuple) -> None:
    """Hold named blocks byte-identical across the files that must share them.

    The `# --- canonical <name> ---` delimiters are what makes two copies
    comparable at all; everything between them is compared byte for byte.

    `names` scopes the comparison, because one file can carry blocks belonging
    to more than one invariant: `agent-lint.py` holds the router scorer it
    shares with `graph-lint.py` AND the plant-root boundary it shares with the
    two hooks, and neither set is a defect in the other's homes.
    """
    texts = {}
    for rel in homes:
        path = ROOT / rel
        if not path.is_file():
            fail(f"{rel} is missing — the canonical {what} blocks have no home there")
            return
        texts[rel] = path.read_text(encoding="utf-8", errors="replace")

    marker = re.compile(
        r"# --- canonical (?P<name>[a-z -]+?) -+\n(?P<body>.*?)"
        r"# --- end canonical (?P=name) -+\n", re.S)
    blocks = {rel: {m.group("name"): m.group(0)
                    for m in marker.finditer(txt) if m.group("name") in names}
              for rel, txt in texts.items()}

    first = homes[0]
    if not blocks[first]:
        fail(f"{first} declares no canonical {what} block — the "
             f"`# --- canonical <name> ---` delimiters are what makes the "
             f"copies comparable at all")
        return
    for name, body in sorted(blocks[first].items()):
        for other_rel in homes[1:]:
            other = blocks[other_rel].get(name)
            if other is None:
                fail(f"canonical block {name!r} exists in {first} but not in "
                     f"{other_rel} — {why}")
            elif other != body:
                fail(f"canonical block {name!r} differs between {first} and "
                     f"{other_rel} — {why}")
    for other_rel in homes[1:]:
        for name in sorted(set(blocks[other_rel]) - set(blocks[first])):
            fail(f"canonical block {name!r} exists in {other_rel} but not in "
                 f"{first} — see above")


def check_canonical_router_blocks() -> None:
    """One scorer, two routers, and no way for them to drift apart quietly.

    `agent-lint.py` (which specialist does the work) and `graph-lint.py` (which
    nodes a session loads) carry one scorer by copy, because each installs into
    a plant as a standalone file and cannot share an import without changing
    the placed file set. The copy is not theoretical: the compound-fragment fix
    reached only one of the two, and a `STEM = 6` fold whose own comment cited
    "test/tests, node/nodes" handled neither — in both files, for four
    releases, because nothing compared them.

    So every part that CAN be identical is held identical, in the same shape as
    the brief templates' canonical block: delimited by name, compared byte for
    byte. `_match` itself is excluded and stays hand-kept — one takes a dict of
    token strengths and the other a set, so they cannot be the same bytes, and
    pretending otherwise would put the tools' shape at the linter's
    convenience.
    """
    _canonical_blocks_must_match(
        ("integrations/claude-code/agent-lint.py",
         "templates/knowledge-graph/graph-lint.py"),
        "router",
        "a router that scores differently routes differently, and the last "
        "time these two drifted it went unnoticed for four releases; copy one "
        "over the other deliberately",
        names=("stopwords", "stemmer"))


def check_canonical_plant_root_boundary() -> None:
    """One boundary rule, three walkers, none of them able to drift out of it.

    `route-hook.py`, `status-hook.py` and `agent-lint.py` each resolve a plant
    artifact by walking UP from the cwd and from their own location. Bounding
    one of the three closed the instance and left the class: from a git repo at
    `outer/sub/child` with no roster of its own, `agent-lint.py --route`
    returned the ANCESTOR repository's agent at HIGH confidence, score 36, and
    `--lint` printed OK over that foreign roster — and `agent-lint.py` is the
    router the kernel mandates on all five harnesses and a graft exit gate.

    All three ship into a plant as standalone files and cannot share an import
    without changing the placed file set, so the rule is held by byte-identity
    in the same shape as the router scorer above.
    """
    _canonical_blocks_must_match(
        ("integrations/claude-code/route-hook.py",
         "integrations/claude-code/status-hook.py",
         "integrations/claude-code/agent-lint.py"),
        "plant-root boundary",
        "a walker without the boundary reads an ancestor repository's "
        "artifact, chosen by directory nesting; all three stop at the same "
        "place or none of them does",
        names=("plant-root boundary",))


# SPEC-0003 I-8: the per-prompt hooks, and the Prime Agent overlay section
# beside them, point at the kernel and restate none of it.
HOOK_TEXT_FILES = ("integrations/claude-code/route-hook.py",
                   "integrations/prime-agent/route-extension.ts")
PRIME_OVERLAY = "integrations/prime-agent/APPEND_SYSTEM.md"
PRIME_OVERLAY_SECTION = "## Surfaced nodes"
KERNEL_RUN = 4          # consecutive kernel tokens that count as a restatement
TIER_TOKEN = re.compile(r"\bT[0-3]\b")


def _decode_escapes(text: str) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)


def _kernel_tokens(text: str) -> list:
    """The shared normalisation: escapes decoded, markdown `*` and backticks
    dropped, lowercased, split into runs of [a-z0-9]."""
    text = _decode_escapes(text).replace("*", "").replace("`", "").lower()
    return re.findall(r"[a-z0-9]+", text)


def _kernel_rule_text(kernel: str) -> list:
    """The §0 "The task is…" cells and the FIRST MOVE numbered steps, as text."""
    lines = kernel.splitlines()
    cells = []
    head = next((i for i, l in enumerate(lines)
                 if l.startswith("|") and "The task is" in l), None)
    if head is not None:
        header = [c.strip() for c in lines[head].strip("|").split("|")]
        col = next(i for i, c in enumerate(header) if "The task is" in c)
        for line in lines[head + 1:]:
            if not line.startswith("|"):
                break
            row = [c.strip() for c in line.strip("|").split("|")]
            if len(row) > col and not re.fullmatch(r":?-+:?", row[col]):
                cells.append(row[col])
    steps = []
    start = next((i for i, l in enumerate(lines)
                  if l.startswith(">") and "FIRST MOVE" in l), None)
    if start is not None:
        open_step = False
        for line in lines[start + 1:]:
            if not line.startswith(">"):
                break
            body = line[1:]
            m = re.match(r"\s*\d+\.\s+(.*)", body)
            if m:
                steps.append(m.group(1))
                open_step = True
            elif open_step and re.match(r"\s{2,}\S", body):
                steps[-1] += " " + body.strip()
            else:
                open_step = False
    return cells + steps


def _kernel_run_in(tokens: list, runs: set):
    for i in range(len(tokens) - KERNEL_RUN + 1):
        run = tuple(tokens[i:i + KERNEL_RUN])
        if run in runs:
            return " ".join(run)
    return None


def _overlay_section(text: str):
    """The overlay's one PRIME_OVERLAY_SECTION, heading to the next `## `, and
    how many such headings the text holds. The section is None unless there is
    exactly one."""
    lines = text.splitlines(keepends=True)
    heads = [i for i, l in enumerate(lines) if l.rstrip() == PRIME_OVERLAY_SECTION]
    if len(heads) != 1:
        return None, len(heads)
    end = heads[0] + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "".join(lines[heads[0]:end]), 1


# One check, two slugs: HOOK_TEXT_RESTATES_NO_KERNEL_RULE over the whole of each
# hook file, and PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE over the overlay section.
# The absolute claim that hooks do not reach subagents. The host runs tool
# hooks inside a subagent (docs/graph/method/delegation.md, "Every brief
# carries the graph discipline"), so the claim is false wherever it ships.
HOOK_REACH_PHRASE = re.compile(
    r"\b(?:hooks? (?:do(?:es)? not|cannot|can't) reach|no hooks? reach(?:es)?)\b", re.I)
# What install.sh places, plus the front door. Records (docs/decisions/,
# docs/plans/, docs/specs/, CHANGELOG.md) keep what they said when written.
HOOK_REACH_ROOTS = ("core", "agents", "protocols", "skills", "templates")
HOOK_REACH_FILES = ("DOCUMENTATION.md",)


def check_hook_reach_phrases() -> None:
    """No shipped or front-door file says hooks do not reach subagents.

    Six method and reference files and the orchestrator charter said it, and
    it was the stated reason the brief is "the only enforcement" across the
    spawn boundary. The brief is still the only carrier of the discipline, but
    for a narrower reason: no hook the seed installs carries it into a worker's
    turn. A reworded absolute claim is outside this pattern and goes to review.
    """
    paths = [ROOT / f for f in HOOK_REACH_FILES]
    paths += sorted((ROOT / "documentation").glob("*.md"))
    for top in HOOK_REACH_ROOTS:
        paths += sorted(p for p in (ROOT / top).rglob("*") if p.is_file()
                        and p.suffix in (".md", ".py", ".sh", ".json", ".ts"))
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            m = HOOK_REACH_PHRASE.search(line)
            if m:
                fail(f"{path.relative_to(ROOT).as_posix()}:{n}: says hooks do not "
                     f"reach subagents ('{m.group(0)}'); tool hooks fire inside a "
                     f"subagent. Say what the seed's hooks carry, and link "
                     f"docs/graph/method/delegation.md")


def check_hook_text_restates_no_kernel_rule() -> None:
    """Per-prompt text points at the kernel; it does not carry a copy of it.

    The route hook injected a paragraph that paraphrased the tier table and the
    FIRST MOVE steps on every prompt: a second home for the kernel's rules,
    free to drift from the first and paid for again with every message. The
    pointer line replaced it, and this check keeps copies from creeping back,
    in comments and docstrings too, since a comment is where the next copy
    starts. Two rules: any run of KERNEL_RUN consecutive tokens taken from a §0
    "The task is…" cell or a FIRST MOVE step, under one normalisation for both
    sides; and any bare tier token, read case-sensitively, which catches a
    paraphrase of the tier table that shares no such run.
    """
    kernel = (ROOT / "core" / "AGENTS.md").read_text(encoding="utf-8")
    rule_text = _kernel_rule_text(kernel)
    runs = set()
    for text in rule_text:
        toks = _kernel_tokens(text)
        runs.update(tuple(toks[i:i + KERNEL_RUN]) for i in range(len(toks) - KERNEL_RUN + 1))
    if len(rule_text) < 6 or not runs:
        fail(f"HOOK_TEXT_RESTATES_NO_KERNEL_RULE: found {len(rule_text)} §0 cells and "
             f"FIRST MOVE steps in core/AGENTS.md; the kernel's shape moved, so this "
             f"check would compare against nothing")
        return
    scanned = [(rel, (ROOT / rel).read_text(encoding="utf-8"), "HOOK_TEXT_RESTATES_NO_KERNEL_RULE")
               for rel in HOOK_TEXT_FILES]
    overlay = ROOT / PRIME_OVERLAY
    section, heads = (_overlay_section(overlay.read_text(encoding="utf-8"))
                      if overlay.is_file() else (None, 0))
    if section is None:
        # A renamed or doubled heading must not switch the overlay half off.
        fail(f"PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE: {PRIME_OVERLAY} has {heads} "
             f"`{PRIME_OVERLAY_SECTION}` sections, so the section cannot be checked; "
             f"exactly one is required (SPEC-0003 I-8)")
    else:
        scanned.append((f"{PRIME_OVERLAY} ({PRIME_OVERLAY_SECTION})", section,
                        "PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE"))
    for where, text, slug in scanned:
        run = _kernel_run_in(_kernel_tokens(text), runs)
        if run:
            fail(f"{slug}: {where} restates the kernel ('{run}' is a run of "
                 f"{KERNEL_RUN} tokens from a §0 cell or a FIRST MOVE step). "
                 f"Point at the kernel instead of copying it (SPEC-0003 I-8)")
        tier = TIER_TOKEN.search(_decode_escapes(text))
        if tier:
            fail(f"{slug}: {where} names the tier token '{tier.group(0)}', which "
                 f"restates the kernel's §0 table. Point at the kernel instead "
                 f"(SPEC-0003 I-8)")


def check_spec_test_mapping() -> None:
    """Every test a spec's §10 cites must exist.

    SPEC-0002 shipped with `UNKNOWN_DOMAIN_MUST_ABSTAIN` marked `green` against
    `test_eval_novel_stack_rows_stay_low` — a name that appeared nowhere in the
    repository. The contract had no regression at all, and the table said it
    was covered. A spec that certifies a test nobody wrote is worse than one
    with an honest gap, because the gap is invisible: nothing fails, and the
    row reads as evidence.

    Cheap to check and therefore not worth trusting a human to re-grep.
    """
    specs = ROOT / "docs" / "specs"
    if not specs.is_dir():
        return
    # The seed's own specs must stay in a status spec-lint actually CHECKS.
    # `back-written` was pinned by nothing, and `draft` is a KNOWN status
    # outside LIVE_STATUSES — so two one-word edits gave
    # `spec lint: PASS — no live contracts to cover (0 live spec(s))` and a full
    # gate EXIT=0 with both specs unchecked. Twelve checks go silent, including
    # the one that refuses a fabricated sign-off, and a draft is exempt from
    # sign-offs anyway. The closed-enum fix stopped an UNKNOWN status doing
    # this; a legitimate one walked straight through the same door.
    #
    # There is no state in which these two are drafts: both are back-written
    # over behaviour that already shipped.
    for spec in sorted(specs.glob("SPEC-*.md")):
        head = spec.read_text(encoding="utf-8", errors="replace")[:2000]
        m = re.search(r"^status:\s*([\w-]+)", head, re.M)
        status = m.group(1) if m else "(none)"
        if status not in ("active", "implemented", "back-written"):
            fail(f"{spec.relative_to(ROOT)}: status is {status!r}, which is "
                 f"outside spec-lint's LIVE_STATUSES — every shape and coverage "
                 f"check silently stops running on it, including the one that "
                 f"refuses a fabricated sign-off. The seed's own specs are "
                 f"back-written over shipped behaviour; there is no state in "
                 f"which they are drafts.")
    for spec in sorted(specs.glob("SPEC-*.md")):
        head = spec.read_text(encoding="utf-8", errors="replace")[:2000]
        # The frontmatter's `status_evidence:` carries the promotion evidence —
        # the kernel points at it as the spec's `active` moment — and nothing
        # read it. The identical string four lines lower, inside the §10 table,
        # IS checked; swapping a real path for `tests/test-no-such-file.sh` in
        # the FIELD left the whole suite green. That is this check's own
        # docstring ("a spec that certifies a test nobody wrote") happening in
        # the one place it was not looking.
        m = re.search(r"^status_evidence:\s*(.+)$", head, re.M)
        if m:
            for cited in re.findall(r"tests/[A-Za-z0-9_./-]+\.(?:sh|py)", m.group(1)):
                if not (ROOT / cited).is_file():
                    fail(f"{spec.relative_to(ROOT)}: status_evidence cites "
                         f"'{cited}', which does not exist. The field is the "
                         f"spec's promotion evidence, so a path that resolves "
                         f"to nothing certifies nothing")

    for spec in sorted(specs.glob("SPEC-*.md")):
        text = spec.read_text(encoding="utf-8", errors="replace")
        # Bind the test NAME to the FILE the row cites. Searching every
        # tests/test_*.py made the file column decorative: a row could name a
        # real test and point at an unrelated suite and pass. The shell-case
        # check below was already file-bound; the Python rows were not.
        for row in re.findall(r"^\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|\s*$",
                              text, re.M):
            name_c = row[1].strip().strip("`").strip()
            file_c = row[2].strip().strip("`").strip()
            status_c = row[4].strip().strip("`").strip()
            m = re.fullmatch(r"(test_[a-z0-9_]+)", name_c)
            if not m or not file_c.startswith("tests/"):
                continue
            name, rel = m.group(1), file_c
            f = ROOT / rel
            if not f.is_file():
                continue          # the missing-file check below reports it
            body = f.read_text(encoding="utf-8", errors="replace")
            if f"def {name}(" not in body:
                fail(f"{spec.name}: cites test '{name}' in '{rel}', which does "
                     f"not define it — the file column is part of the claim")
                continue
            # A row may not say `green` for a test that never runs. Take the
            # WHOLE contiguous decorator run above the def (a multi-line
            # decorator pushed the `@` outside a fixed 4-line window), every
            # skip spelling, and a SkipTest raised in the body.
            seg = body.split(f"def {name}(", 1)[0]
            deco = []
            for line in reversed(seg.splitlines()):
                st = line.lstrip()
                if not st or st.startswith("#"):
                    continue          # blank lines and comments are not the end
                if st.startswith(("@", ")", "]", '"', "'")) or (
                        deco and not st.startswith(("def ", "class "))):
                    deco.append(line)
                    continue
                break
            # A class-level skip parks every test in the class at once. The
            # enclosing class header is the last `class X` before this def.
            cls = seg.rsplit("\nclass ", 1)
            if len(cls) == 2:
                before_cls = cls[0]
                cls_deco = []
                for line in reversed(before_cls.splitlines()):
                    st = line.lstrip()
                    if not st or st.startswith("#"):
                        continue
                    if st.startswith(("@", ")", "]")) or (
                            cls_deco and not st.startswith(("def ", "class "))):
                        cls_deco.append(line)
                        continue
                    break
                deco += cls_deco
                if "__unittest_skip__" in cls[1].split("\n    def ", 1)[0]:
                    deco.append("__unittest_skip__")
            after = body.split(f"def {name}(", 1)[1]
            nxt = re.split(r"\n    def |\nclass ", after, maxsplit=1)[0]
            skipped = (re.search(r"@(unittest\.)?skip(If|Unless)?\b|__unittest_skip__", "\n".join(deco))
                       or re.search(r"raise\s+(unittest\.)?SkipTest\b", nxt)
                       or re.search(r"self\.skipTest\(", nxt))
            if skipped and status_c.lower() == "green":
                fail(f"{spec.name}: row for '{name}' says green, but the test "
                     f"skips ({skipped.group(0)}) — a skip is not a pass")

        for name in sorted(set(re.findall(r"\|\s*(test_[a-z0-9_]+)\s*\|", text))):
            if not any(f"def {name}(" in f.read_text(encoding="utf-8", errors="replace")
                       for f in (ROOT / "tests").glob("test_*.py")):
                fail(f"{spec.name}: cites test '{name}', which does not exist "
                     f"in tests/ — a spec may not certify coverage nobody wrote")
        for rel in sorted(set(re.findall(r"\|\s*(tests/[A-Za-z0-9_.-]+)\s*\|", text))):
            if not (ROOT / rel).exists():
                fail(f"{spec.name}: cites test file '{rel}', which does not exist")
        # A shell suite has no `def test_x`, so SPEC-0001's §10 names its cases
        # in prose — and prose was unverifiable: a fabricated row citing a real
        # .sh file passed silently, which is the same "certifies coverage nobody
        # wrote" defect in the one spec-authoring style the check missed.
        # The rows do carry a machine-checkable anchor: the invariant label they
        # open with (M7, S6, K3, D1...). Require it to appear in the file cited.
        # EVERY row citing a .sh must be one the strict binder below can read.
        # The binder wants the label bare and leading; `**M99**`, `- M99` and
        # `P9` each fail to bind and were skipped silently. Three earlier
        # attempts missed it: one asked only whether the cell CONTAINED
        # something label-shaped; one harvested labels from the whole file, so
        # `**M99**` was satisfied by another row's `M9`; and one sat at the
        # wrong indentation and ran once, after the loop, against the last
        # spec — which has no .sh rows at all.
        _strict = re.compile(
            r"\|[\s`]*([MSKVXE]\d+|D\d+)[\s`]*[^|]*\|\s*(tests/[A-Za-z0-9_.-]+\.sh)\s*\|")
        _cites = re.compile(r"\|([^|]*)\|\s*`?(tests/[A-Za-z0-9_.-]+\.sh)`?\s*\|")
        for line in text.splitlines():
            mc = _cites.search(line)
            if mc and not _strict.search(line):
                fail(f"{spec.name}: a §10 row cites {mc.group(2)} with a first "
                     f"cell the invariant-label check cannot bind "
                     f"({mc.group(1).strip()[:50]!r}) — a styled, prefixed or "
                     f"unrecognised label skips that check silently")
        for label, rel in re.findall(
                    r"\|[\s`]*([MSKVXE]\d+|D\d+)[\s`]*[^|]*\|\s*(tests/[A-Za-z0-9_.-]+\.sh)\s*\|",
                    text):
                f = ROOT / rel
                if f.exists() and label not in f.read_text(encoding="utf-8", errors="replace"):
                    fail(f"{spec.name}: §10 cites '{label}' in {rel}, which never "
                         f"mentions it — the row certifies a check that file does "
                         f"not contain")


def machinery_nodes():
    """Every routable node the seed installs into a plant's docs/graph/, as
    (label, frontmatter dict, body). The homes are install.sh's
    place_graph_machinery list — protocols, method, agents, skills."""
    for sub in ("protocols", "core/method", "agents"):
        for f in sorted((ROOT / sub).glob("*.md")):
            if f.name.startswith("_"):
                continue
            yield f.relative_to(ROOT).as_posix(), parse_frontmatter(f), body_of(f)
    for d in sorted((ROOT / "skills").iterdir()):
        f = d / "SKILL.md"
        if f.is_file():
            yield f.relative_to(ROOT).as_posix(), parse_frontmatter(f), body_of(f)


def body_of(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


# Every raw write in install.sh that does NOT go through one of the four named
# placement operations, keyed by the function that holds it and the command
# word that performs it. SPEC-0001's SINGLE_WRITER asserts the four operations
# are the only way bytes reach a destination; that was FALSE as written, and a
# prose "And" clause listing the exceptions would have been satisfied by its own
# negation. So the exceptions are a SET, derived from the script on every run
# and compared against this table. A new bypass fails because it is not here; a
# removed one fails because this table is then stale. Neither can be argued
# with, which is the point.
INSTALL_WRITE_EXCEPTIONS = {
    # (function, verb): (how many such writes there are, why they are not placed)
    #
    # The COUNT is the half that matters. Keyed on (function, verb) alone, every
    # pair already present was an open licence: a second `cp` at `<main>` level,
    # or a fifth in install_github_copilot, was absorbed silently because the key
    # existed. A new write now fails whether or not its neighbours look like it.

    # --- into the TARGET: authored, not placed. SPEC-0001 §4 records these. ---
    ("record_instruction_migration", "mv"): (2, "target",
        "moves a symlink standing at the note path aside, and moves a HARD LINK "
        "aside for the same reason — `cat >` and `>>` both write the inode, so a "
        "note hardlinked to a file outside the target had the migration ledger "
        "appended into that outside file, exit 0, and `-L` is false for it. "
        "place_file's own idiom, but the note is authored here rather than "
        "copied from the seed"),
    ("record_instruction_migration", "cat"): (1, "target",
        "writes the migration note's header; there is no seed-side source file "
        "to place, the body is generated from the kernel that was replaced"),
    ("record_instruction_migration", ">>"): (1, "target",
        "appends one ledger row per replaced kernel; an append, which none of "
        "the four operations expresses"),
    ("place_kernel", "mv"): (1, "target",
        "backs up the SIBLING kernel before the link replaces it"),
    ("place_kernel", "rm"): (1, "target",
        "removes the sibling before `ln -s`; a link cannot be placed over a file"),
    ("place_kernel", "ln"): (1, "target",
        "lays the sibling link BY HAND — it is project-local and relative, "
        "pointing inside the target rather than into the seed, which place_file "
        "cannot express. §4 described this write; the table did not hold it, "
        "because the verb sits behind an `if` and the parser was line-anchored"),
    ("place_kernel", "cp"): (1, "target",
        "the no-symlink fallback — an independent kernel copy where the "
        "filesystem refused a link"),
    ("fill_plant_facts", "embedded"): (1, "target",
        "rewrites docs/graph/index.md IN PLACE through an embedded python "
        "heredoc, because the plant's own facts are merged into a file the "
        "plant owns rather than copied over it. install.sh:807 says so in its "
        "own words. A fourth authored write into the target, invisible to this "
        "check until the embedded pass existed"),

    ("retire_copilot_hook_duplicates", "mv"): (1, "target",
        "retires a .github/hooks/ file that .claude/settings.json now "
        "supersedes, moving it to a timestamped backup beside itself. The "
        "Copilot side already skipped these when settings.json was present; "
        "that guard ran in one direction only, so adopting Copilot first and "
        "Claude Code second left both wired and every hook firing twice. An "
        "authored retirement, not a placement — there is no seed source to "
        "place, and place_file cannot express a removal"),

    ("ensure_dir", "mkdir"): (1, "target",
        "creates a destination directory before a placer writes into it. The "
        "one write every placer depends on, and it is a directory rather than "
        "content — but it IS a write into the target, and it was invisible "
        "twice over: `mkdir` was not a detected verb, and ensure_dir was "
        "exempted wholesale"),

    # --- into a TEMP tree only; these never touch PROJECT_DIR ---
    ("stage", "mkdir"): (1, "temp", "creates the staging directory under $tmp"),
    ("<main>", "mkdir"): (2, "temp", "creates the verification tree under $tmp"),
    ("generate_slash_commands", "cat"): (1, "temp", "writes a command file into $tmp"),
    ("write_seed_stamp", ">"): (1, "temp", "writes the stamp into $tmp before place_state"),
    ("install_codex", "embedded"): (1, "temp", "renders the config snippet into $tmp"),
    ("install_github_copilot", "embedded"): (4, "temp",
        "renders the four Copilot projections into $tmp, each then placed"),
    ("<main>", "cp"): (1, "temp", "copies the graph into the verification tree under $tmp"),
    ("<main>", ":"): (1, "temp", "truncates a settings file inside $tmp"),
    ("<main>", ">"): (1, "temp", "captures a generator's output into a log under $tmp"),
    ("<main>", "rm"): (2, "temp", "removes the verification tree under $tmp"),
}
# Derived, not counted by hand. This used to be a literal beside a tuple of four
# function NAMES, and anything outside that tuple defaulted to temp-side — so a
# new function writing into the plant was classified harmless by omission, and
# an eleventh target-side write passed with SPEC-0001 §4 still saying ten. Every
# row declares its own side now, and a row that declares neither is refused.
TARGET_SIDE_WRITE_EXCEPTIONS = sum(
    n for (n, side, _why) in INSTALL_WRITE_EXCEPTIONS.values() if side == "target")
NAMED_PLACERS = ("place_file", "place_generated", "place_if_missing", "place_state")

# The writes the placers themselves perform. These are the four operations
# SINGLE_WRITER routes everything ELSE through, so they are the one place a raw
# write is correct — but "correct here" is not "uncounted here". The placers
# were exempted WHOLESALE, exactly as `ensure_dir` once was, and the comment
# recording that ensure_dir fix sat four lines above the line still doing it for
# the placers. A reviewer put one `case "$dest" in */.github/hooks/*) cat "$src"
# > "$dest"; return ;; esac` inside place_file and watched `tests/run.sh` exit 0
# while an install destroyed a file outside --project-dir. Counted rows now.
PLACER_WRITES = {
    ("place_file", "mv"): (1, "moves the existing destination aside as the backup"),
    ("place_file", "ln"): (1, "creates the seed link under --symlink"),
    ("place_file", "cp"): (1, "copies the seed file into place under --copy"),
    ("place_if_missing", "cp"): (1, "first placement of a file the plant then owns"),
    ("place_state", "cp"): (1, "stages the new stamp beside its destination"),
    ("place_state", "mv"): (1, "renames the staged stamp onto the destination name"),
}


def install_write_sites() -> dict:
    """Derive every raw write in install.sh, attributed to the function holding it.

    Scope, stated rather than implied. This reads shell with regexes, and shell
    cannot be read with regexes — a full parser is the only thing that would
    make this exhaustive, and building one is not worth it here. What it does
    cover, each shape having actually walked past an earlier version:

    - the DEFINITION line is scanned, so `evil() { cp a b; }` on one line is
      seen (it used to `continue` before scanning);
    - both `name() {` and `function name {`, so attribution does not silently
      fall back to `<main>`;
    - a write behind `if`, `elif`, `while`, `then`, `do`, `else`, `&&`, `||` or
      `;`, by stripping those prefixes before the verb test;
    - `sed -i`, `dd`, `rsync`, `tee`, beside `cp`/`mv`/`ln`/`rm`/`install`;
    - writes performed by an embedded python heredoc — `write_text`, `open(…,
      "w")`, `shutil.copy` — which carry no shell verb at all. That is not
      hypothetical: `fill_plant_facts` writes the plant's `index.md` that way,
      and it is a fourth authored write into the target that the first version
      of this check could not see.

    What it does NOT cover, so nobody reads a PASS as more than it is:

    - a write inside a command substitution, `out=$(cp a b)`;
    - a write on the right of a pipe, `printf x | tee "$dest"`;
    - an interpreter other than python invoked with an inline program;
    - anything `eval`'d.

    Those are recorded in `tools/gate-registry.py` as this check's residual
    false green. A non-python heredoc body is skipped as prose, because
    scanning it read the sentence "remove it deliberately first (rm -rf
    docs/graph/legal/corpus)" inside an error MESSAGE as a write.
    """
    text = (ROOT / "install.sh").read_text(encoding="utf-8", errors="replace")
    redirect = re.compile(r'(?<![<>0-9])>>?\s*(?:""|\$|/|[A-Za-z_])')
    command = re.compile(r'^(cp|mv|ln|rm|tee|touch|install|rsync|dd|sed|mkdir|:)\s')
    # Leading keywords, stripped so a guarded write is still a write. `command`
    # is here because `command cp a b` is the documented way to bypass a shell
    # function of the same name — the one shape whose whole purpose is evasion.
    prefix = re.compile(r'^(?:if|elif|while|until|then|else|do|done|fi|esac|!|command)\s+')
    # A line is SPLIT on shell separators and every segment is tested. Anchoring
    # to the start of the LINE was the perimeter: twelve writes into the target
    # were invisible, each valid bash and several of them claimed covered —
    #   case "$x" in *) cp a b ;; esac      { cp a b; }        ( cp a b )
    #   for x in 1; do cp a b; done         cmd && cp a b      if c; then cp a b; fi
    # The strongest demonstration was that the scanner could not see place_file's
    # OWN writes, because they sit in `symlink) ln -s ... ;;` case branches — so
    # a bypass written in the canonical writer's own idiom was invisible.
    separators = re.compile(r'&&|\|\||[;|(){}]|(?<=\))\s')
    embedded = re.compile(r'\.write_text\s*\(|\.write_bytes\s*\(|'
                          r'\bopen\s*\([^)]*[\'"][wa]b?[\'"]|\bshutil\.(?:copy|move)')
    sites: dict = {}
    current = "<main>"
    in_string = False
    heredoc = None
    for lineno, line in enumerate(text.splitlines(), 1):
        if heredoc is not None:
            if line.strip() == heredoc[0]:
                heredoc = None
                continue
            if not heredoc[1]:
                continue
        elif line.lstrip().startswith("#"):
            # A comment is not a heredoc opener. Searching every line before the
            # comment skip made `<<` a BLINDING PRIMITIVE: a comment mentioning
            # `<<NOTES`, a string saying "pipe it with <<EOF", or the arithmetic
            # `$(( 1 << shift ))` opened a phantom heredoc, and every remaining
            # line of install.sh was discarded as prose — to end of file, since
            # no line ever equals the phantom delimiter. Three variants verified,
            # all silently blinding.
            continue
        else:
            # Searched on the BLANKED line so a quoted `<<EOF` cannot open one,
            # and required to be a real redirection: preceded by start-of-line,
            # whitespace, or a `-` flag argument, never by a digit or `<`.
            _hd = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)
            opener = re.search(r"(?:^|[\s;&|])<<-?\s*'?([A-Za-z_][A-Za-z0-9_]*)'?", _hd)
            if opener:
                # `python3 - "$a" "$b" \` then the heredoc on the NEXT line: the
                # interpreter is not on the opener. Walk back over continuations
                # to find the command this heredoc is actually fed to — install_codex
                # writes that way, and reading its body as prose hid the write.
                joined = line
                probe = lineno - 2
                while probe >= 0 and text.splitlines()[probe].rstrip().endswith("\\"):
                    joined = text.splitlines()[probe] + " " + joined
                    probe -= 1
                heredoc = (opener.group(1), "python" in joined)

        opened = re.match(r"^(?:function\s+([a-z_][a-z0-9_]*)\s*(?:\(\))?|"
                          r"([a-z_][a-z0-9_]*)\s*\(\))\s*\{", line)
        if opened:
            current = opened.group(1) or opened.group(2)
            line = line[opened.end():]        # scan the rest of a one-liner
        if line == "}":
            current = "<main>"
            continue
        if line.lstrip().startswith("#"):
            continue

        # Split the BLANKED line, and skip a continuation line of a multi-line
        # string entirely. `log "Next step (the HAND OFF phase): open ..."` is
        # prose, and splitting the RAW line on `(`/`)` exposed `: open ...` as a
        # truncate; the same parens exposed "remove it deliberately first (rm -rf
        # docs/graph/legal/corpus)" inside a multi-line `die`. Widening the
        # perimeter widened what counts as code, so the blanking has to widen
        # with it.
        # A MESSAGE string that spans lines is prose. Narrow on purpose: only a
        # `die`/`warn`/`log`/`fail` call whose quote is left open starts one, and
        # it ends at the next line carrying a quote. General quote-parity
        # tracking was tried and is not safe here — `$(basename "$x")` inside a
        # string flips it, and one bad flip swallowed every real write until the
        # next odd line.
        if in_string:
            # ESCAPED quotes do not close it. The message that exposed this
            # carries `Recording \"no\" would make ...` four lines in, so a naive
            # test ended the string early and scanned the remaining prose as
            # code — which is how `(rm -rf docs/graph/legal/corpus)`, inside a
            # sentence telling the owner what to do, read as a write.
            if '"' in re.sub(r'\\.', '', line):
                in_string = False
            continue
        if (re.match(r'^\s*(?:die|warn|log|fail)\s+"', line)
                and re.sub(r'\\.', '', line).count('"') % 2 == 1):
            in_string = True
            continue
        blanked = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)

        segments = []
        for seg in separators.split(blanked):
            if seg is None:
                continue
            seg = seg.strip()
            # a case-branch label: `symlink) ln -s "$src" "$dest" ;;`
            seg = re.sub(r'^[^\s()]*\)\s+', '', seg)
            while True:
                m = prefix.match(seg)
                if not m:
                    break
                seg = seg[m.end():].lstrip()
            if seg:
                segments.append(seg)
        stripped = segments[0] if segments else ""

        blanked = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)
        word = None
        if embedded.search(line) and heredoc is not None and heredoc[1]:
            word = "embedded"
        else:
            cmd = None
            for seg in segments:
                cmd = command.match(seg)
                if cmd:
                    break
            if cmd:
                word = cmd.group(1)
                if word == "sed" and " -i" not in line and "--in-place" not in line:
                    word = None               # sed without -i writes to stdout
            elif redirect.search(blanked):
                if re.search(r'>>?\s*&?\s*/dev/null', line):
                    word = None               # a discard, not a destination
                else:
                    word = "cat" if re.match(r'^cat\s', stripped) else (
                        ">>" if ">>" in blanked else ">")
        if word:
            sites.setdefault((current, word), []).append(lineno)
    if heredoc is not None:
        fail(f"seed-lint: install.sh ends with heredoc '{heredoc[0]}' still open, "
             f"so every line after it was discarded as prose and this check "
             f"reported on a truncated file. A clean result here would be a lie.")
    return sites


_prevents_by_node: dict[str, str] = {}


def check_prevents_are_distinct() -> None:
    """No two nodes may claim the same failure as the one they prevent.

    `CLAUDE.md` says why a component is on the roster lives in its own
    `prevents:`, and the review brief has asked five rounds running for a
    "pairwise `prevents:` overlap across all 60 lines, reported with scores".
    That was asked of REVIEWERS because nothing did it: the only ratio in this
    file compares a node's `prevents:` to its OWN `description:`. Copying
    `agent.implementer`'s `prevents:` byte-for-byte into `agent.reviewer` passed
    seed-lint, passed `roster-justification.py --gaps`, and passed the gate —
    verified.

    That gap is the whole "moved collisions" defect class: rewriting a
    `prevents:` to clear a duplicate RELOCATED it, and `agent.implementer`
    collided three times across three rounds and came back to where it started,
    because every check of it was a human reading pairs by hand.

    The measure is Jaccard over distinctive words, symmetric so neither node is
    privileged, and it names both nodes and the score so the report is
    actionable rather than a verdict.
    """
    import re as _re
    norm = lambda s: {w for w in _re.findall(r"[a-z][a-z-]{3,}", s.lower())
                      if w not in _PREVENTS_STOP}
    words = {rel: norm(p) for rel, p in _prevents_by_node.items()}
    # A node whose normalised set is too small to compare is a FINDING, never a
    # silent drop. Dropping it was an exploitable hole in this very check: a
    # byte-identical `prevents:` planted on two agents, each written so its
    # distinctive vocabulary fell under the floor, left both victims excluded,
    # `nodes_compared=58`, `seed lint: PASS`, and the whole gate rc=0 — the exact
    # byte-copy this check exists to catch, defeated by two words. The floor
    # below did not fire either, because 58 is still >= 40.
    thin = {rel: len(w) for rel, w in words.items() if len(w) < PREVENTS_MIN_WORDS}
    for rel, n in sorted(thin.items()):
        fail(f"{rel}: prevents: normalises to {n} distinctive word(s), below "
             f"{PREVENTS_MIN_WORDS}. Too thin to compare against any other node, "
             f"so it would be silently excluded from the pairwise sweep — which "
             f"is how a duplicate hides. Say what breaks without this node in "
             f"words the other 59 do not all share.")
    words = {rel: w for rel, w in words.items() if len(w) >= PREVENTS_MIN_WORDS}
    nodes = sorted(words)
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            wa, wb = words[a], words[b]
            union = wa | wb
            if not union:
                continue
            score = len(wa & wb) / len(union)
            if score >= PREVENTS_OVERLAP_CEILING:
                shared = sorted(wa & wb)[:10]
                fail(f"{a} and {b} claim the same failure: their prevents: "
                     f"lines overlap at {score:.0%} (ceiling "
                     f"{PREVENTS_OVERLAP_CEILING:.0%}). Two nodes preventing one "
                     f"failure means one of them is not earning its place, or "
                     f"the boundary between them is not where the lines say it "
                     f"is. Rewrite the line about the node's OWN owned fact — "
                     f"rewriting it about the failure moves the collision "
                     f"instead of closing it (shared: {shared})")
    if len(words) != len(_prevents_by_node):
        fail(f"seed-lint: the pairwise prevents: pass compared "
             f"{len(words)} of {len(_prevents_by_node)} collected nodes. Every "
             f"node must be compared or named above; a node that is neither is "
             f"a hiding place. (The roster size was written here as a literal "
             f"60 — a count in prose inside the check that exists to notice the "
             f"roster changing.)")


def _spec_green_rows() -> list:
    """Every §10 row marked `green`, as (spec, slug, test-name, cited-file)."""
    out = []
    specs = ROOT / "docs" / "specs"
    if not specs.is_dir():
        return out
    for spec in sorted(specs.glob("SPEC-*.md")):
        text = spec.read_text(encoding="utf-8", errors="replace")
        if "## 10." not in text:
            continue
        section = text.split("## 10.")[1].split("\n## ")[0]
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
            if len(cells) >= 5 and cells[4] == "green":
                out.append((spec.name, cells[0], cells[1], cells[2]))
    return out


_ASSERTION = re.compile(r"\b(?:assert\w*|self\.assert\w+|fail|raise|sys\.exit)\s*\(")


def _scope_asserts(scope: str, module_body: str) -> bool:
    """Does this test assert anything, directly or through one helper?

    Direct assertions are the common case. Delegation is the other one:
    `test_agent_roster_collisions_are_reviewed` builds a vocabulary and hands it
    to `self._check(...)`, which holds the assertion — a perfectly ordinary
    shape, and a check that could not see it would have flagged two honest
    tests and taught the next author to inline assertions to satisfy a linter.
    So one level of delegation is resolved: a helper defined in the same module
    whose own body asserts counts.
    """
    if _ASSERTION.search(scope):
        return True
    for call in set(re.findall(r"(?:self\.)?(_[a-z0-9_]+)\s*\(", scope)):
        m = re.search(rf"^\s*def {re.escape(call)}\b", module_body, re.M)
        if not m:
            continue
        rest = module_body[m.start():]
        nxt = re.search(r"\n\s*(?:def |class )", rest[1:])
        helper_scope = rest[:nxt.start() + 1] if nxt else rest
        if _ASSERTION.search(helper_scope):
            return True
    return False


def check_spec_rows_name_their_contract() -> None:
    """A `green` §10 row must cite a test that NAMES the contract it certifies.

    Binding the row to the FILE and to a `def` was not enough: neither says the
    test asserts this contract rather than something adjacent in the same file.
    The slug is the cheapest thing that does say it. Note this is STRICTER than
    `spec-lint`'s coverage pass, deliberately: that one greps the slug anywhere
    under `tests/` and finds 7 of 30 contracts; this one requires it in the test
    the row actually cites, and finds 2 of 50 rows. The two numbers measure
    different things and both are honest — "somebody tests this" versus "THIS
    row's test tests this". Before either existed the table said green 50 times
    and they disagreed about 21 contracts with nothing comparing them.

    Enumerated debt, ratcheted: a NEW row must bind from the day it is written,
    the existing ones may be paid down at any pace, and the count may only fall.
    """
    rows = _spec_green_rows()
    if not rows:
        return
    unbound = []
    unasserted = []
    for spec, slug, test, rel in rows:
        f = ROOT / rel
        if not f.is_file():
            continue                 # the cited-file check owns this case
        body = f.read_text(encoding="utf-8", errors="replace")
        # `[ \t]*`, not `\s*`: under re.M a `\s*` crosses the blank lines above
        # a top-level def, the match starts on the first of them, and the
        # scope below collapses to one newline, so no top-level function could
        # bind a row (found at SPEC-0003 RED; pinned by
        # case_spec_row_toplevel_def in tests/test-seed-lint.sh).
        m = re.search(rf"^[ \t]*def {re.escape(test)}\b", body, re.M)
        if m:
            rest = body[m.start():]
            nxt = re.search(r"\n\s*(?:def |class )", rest[1:])
            scope = rest[:nxt.start() + 1] if nxt else rest
        else:
            scope = body          # a shell case label: bind against the file
        if slug not in scope:
            unbound.append(f"{spec} §10 `{slug}` -> {test} ({rel})")
            continue
        # The slug being present is not the same as the test asserting
        # anything. Replacing a cited test's BODY with `pass` — keeping only
        # the docstring line that names two contracts — left spec-lint's
        # coverage at 0 uncovered, this check green, the suite green and the
        # whole gate at EXIT=0, over the gate `--eval` exists for. A contract
        # bound to a test with no assertion is bound to nothing.
        if m and not _scope_asserts(scope, body):
            unasserted.append(f"{spec} §10 `{slug}` -> {test} ({rel})")

    if unasserted:
        fail(f"{len(unasserted)} green §10 row(s) cite a test that NAMES their "
             f"contract and asserts nothing — no assert, no fail, no raise "
             f"anywhere in its scope. The slug in a docstring is a claim, not "
             f"a check:\n    " + "\n    ".join(unasserted[:5]))

    n = len(unbound)
    if n > SPEC_ROW_UNBOUND_BUDGET:
        fail(f"{n} green §10 row(s) cite a test that does not name their "
             f"contract, against a recorded budget of "
             f"{SPEC_ROW_UNBOUND_BUDGET}. A row that names no slug certifies "
             f"nothing a reader can check: name the contract in the asserting "
             f"test. New:\n    " + "\n    ".join(unbound[:5]))
    elif n < SPEC_ROW_UNBOUND_BUDGET:
        fail(f"{n} green §10 row(s) are unbound and the recorded budget is "
             f"{SPEC_ROW_UNBOUND_BUDGET}. The debt SHRANK and the record did "
             f"not — lower SPEC_ROW_UNBOUND_BUDGET to {n} and re-bless, or the "
             f"next row to lose its binding is absorbed silently.")


FRONTMATTER_COPIES = (
    "templates/knowledge-graph/frontmatter.py",   # canonical; ships into plants
    "integrations/claude-code/frontmatter.py",
    "tests/frontmatter.py",
    "tools/frontmatter.py",
)


def check_frontmatter_is_portable_yaml() -> None:
    """Every SHIPPED node's frontmatter is also a strict-YAML document.

    The seed's reader (`tests/frontmatter.py`, and its byte-identical copies)
    is deliberately NOT a YAML library: it splits a `key: value` on the FIRST
    colon and keeps the rest verbatim, so an unquoted value carrying an inner
    `: ` (colon-space) reads fine. Claude Code's integration uses that same
    lenient reader, so it loads such a header without complaint. Prime Agent's
    skill loader parses SKILL.md frontmatter as STRICT YAML, which reads the
    inner `: ` as a nested mapping and REJECTS the whole block ("Nested mappings
    are not allowed in compact mappings") — the skill is silently dropped on one
    of two supported hosts. This check keeps the two readers on their overlap:
    an unquoted, non-list scalar value must not contain `: ` (nor end in a bare
    `:`). Quote the value or reword the clause.

    Scoped to the nodes install.sh ships — protocols, method, agents, skills —
    the same set `machinery_nodes()` walks. Templates and corpora are OUT: a
    `templates/docs/nodes/_expertise.template.md` carries `{{ ... }}`
    placeholders that are not YAML and are never loaded as a skill, and a
    `_schema.md` is authored prose, not a routed header a strict loader opens.
    """
    node_paths = []
    for sub in ("protocols", "core/method", "agents"):
        node_paths += [f for f in sorted((ROOT / sub).glob("*.md"))
                       if not f.name.startswith("_")]
    for d in sorted((ROOT / "skills").iterdir()):
        f = d / "SKILL.md"
        if f.is_file():
            node_paths.append(f)
    for path in node_paths:
        for line in frontmatter_block(path).split("\n"):
            if not line or line[:1] in " \t#":     # nested / comment / blank
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            value = value.strip()
            if not value or value[:1] in "\"'[":    # list/mapping opener, quoted, inline list
                continue
            scalar_value = value.split("  #", 1)[0].rstrip()   # reader strips '  #comment'
            if re.search(r":(?:\s|$)", scalar_value):
                fail(f"{path.relative_to(ROOT)}: frontmatter {key.strip()!r} value "
                     f"carries an inner ': ' ({scalar_value!r}) — the lenient reader "
                     f"keeps it but a strict-YAML skill loader (Prime Agent) reads it "
                     f"as a nested mapping and drops the node. Quote it or reword the "
                     f"clause.")


def check_frontmatter_reader_is_one_reader() -> None:
    """Every copy of the frontmatter reader is byte-identical to the canonical one.

    Seven programs each grew their own reader for the same `---` block, and the
    disagreement was invisible until someone wrote a two-line description: two
    rejected the file, three silently kept the first line and dropped the rest.
    Consolidating to one reader only helps if the copies cannot drift, and they
    must be copies — graph-lint, spec-lint, grill-lint and legal-lint ship into
    plants as standalone files with no package to import from.

    Byte-identity is the same mechanism this file already applies to the
    routers' canonical stopword block, for the same reason.
    """
    canon = ROOT / FRONTMATTER_COPIES[0]
    if not canon.is_file():
        fail(f"{FRONTMATTER_COPIES[0]} is missing — it is the canonical "
             f"frontmatter reader every other copy is checked against")
        return
    want = canon.read_bytes()
    for rel in FRONTMATTER_COPIES[1:]:
        p = ROOT / rel
        if not p.is_file():
            fail(f"{rel}: missing copy of the frontmatter reader. It is a COPY "
                 f"by necessity — the linters that ship into plants have no "
                 f"package to import from — so every consumer needs one beside it.")
        elif p.read_bytes() != want:
            fail(f"{rel} has drifted from {FRONTMATTER_COPIES[0]}. One reader, "
                 f"byte-identical: seven divergent readers is what this replaced.")


def check_shell_floor_claim_matches_the_shebang() -> None:
    """A spec's stated shell floor is the one its code actually holds.

    SPEC-0001 §5 read "POSIX shell and `python3` only" over a tree whose 30
    shell files every one declare `#!/usr/bin/env bash`, and whose installer
    uses `set -euo pipefail` — a `set` option POSIX does not define. Nothing
    compared the claim with the shebang, so a reader who believed it would
    write POSIX-only shell into a bash tree and learn otherwise at runtime.

    What is forbidden is the CLAIM, not the word. §5 now records that it
    claimed a POSIX floor until 2026-09-16 and §12 quotes the old wording in
    full, so a check that grepped the file for the phrase would fail the tree
    on its own correction history. This reads the floor where a spec STATES
    it — the first sentence of the `**Compatibility:**` bullet — and leaves
    every sentence that discusses the distinction, or records what the line
    used to say, alone.
    """
    specs = ROOT / "docs" / "specs"
    install = ROOT / "install.sh"
    if not specs.is_dir() or not install.is_file():
        return
    shebang = install.read_text(encoding="utf-8").splitlines()[0]
    if "bash" not in shebang:
        # A POSIX claim over a POSIX shebang is true, and this check has
        # nothing to say about it.
        return
    for path in sorted(specs.rglob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            m = re.match(r"\s*-\s*\*\*Compatibility:?\*\*:?\s*(.*)$", line)
            if not m:
                continue
            # The bullet as one paragraph, then its first sentence: the floor
            # is stated there, and what follows is commentary about it.
            claim = [m.group(1)]
            for nxt in lines[i:]:
                if not nxt.strip() or re.match(r"\s*[-*]\s|#", nxt):
                    break
                claim.append(nxt.strip())
            stated = re.split(r"(?<=\.)\s", " ".join(claim), maxsplit=1)[0]
            if "POSIX" in stated and re.search(r"\bsh(ell)?\b", stated):
                fail(f"{path.relative_to(ROOT).as_posix()}:{i}: the "
                     f"**Compatibility:** bullet claims a POSIX shell floor, "
                     f"and install.sh:1 declares `{shebang}`. A spec states "
                     f"the floor its code holds; the bash-versus-POSIX "
                     f"distinction itself is owned by a grown plant's "
                     f"docs/graph/best-practices/bash.md §\"Two floors, not "
                     f"one\" and is linked, not restated.")


def _case_arms(src: str, header: str) -> list | None:
    """The arms of the first bash `case … in … esac` whose opening line matches `header`.

    Returns [(patterns, body)] for each arm at the block's own depth, or None
    when no line matches. An arm is what bash reads: a pattern list up to the
    first `)`, alternatives split on `|`, then a body up to `;;`, `;&` or
    `;;&`. Full-line comments are dropped first; a nested `case` inside an arm
    is carried whole in that arm's body. The labels come back verbatim, so a
    caller can refuse a quoted or globbed label instead of guessing at it.
    """
    lines = src.splitlines()
    start = next((i for i, ln in enumerate(lines) if re.search(header, ln)),
                 None)
    if start is None:
        return None
    opener = re.compile(r"(?:^|[\s;(])case\s+\S.*?\s+in(?:\s|$)")
    closer = re.compile(r"(?:^|[\s;])esac(?:\s|;|$)")
    head = lines[start]
    rest = head[opener.search(head).end():] if opener.search(head) else ""
    depth, text = 0, []
    for ln in [rest] + lines[start + 1:]:
        if ln.lstrip().startswith("#"):
            continue
        opens, closes = len(opener.findall(ln)), len(closer.findall(ln))
        if depth == 0 and closes > opens:
            text.append(ln[:closer.search(ln).start()])
            break
        depth += opens - closes
        text.append(ln)
    arms: list = []
    chunks = re.split(r";;&|;;|;&", "\n".join(text)) if depth == 0 else []
    for chunk in chunks:
        m = re.match(r"\s*\(?\s*([^)]*?)\s*\)(.*)\Z", chunk, re.S)
        if m:
            arms.append(([a.strip() for a in m.group(1).split("|")],
                         m.group(2)))
    return arms


def check_host_tiers() -> None:
    """The published tier table is the installer's tier arrays, and `all` is the maintained two.

    ADR-0009 gives the host support tiers one home: FIRST_CLASS_TOOLS,
    SUPPORTED_TOOLS and FROZEN_TOOLS in install.sh. The deprecation notice reads
    FROZEN_TOOLS; `all` is a separate literal, held to the arrays here.
    documentation/host-capability-matrix.md publishes the same assignment under
    its "Support tiers" heading for a reader who never opens the installer. A
    published copy nothing compares is a second home, and the first edit to
    either one is the drift: moving a host between tiers in the matrix alone
    would tell every reader a maintenance commitment the installer does not act
    on.

    Six things are held. Each host sits in one tier only, in the arrays and in
    the table, and the table has one row per tier. The matrix table names the
    same hosts per tier as the arrays. `all` installs exactly the first-class
    and supported hosts, since the installer writes that list out rather than
    deriving it (the derivation would reorder install). The three arrays
    together are exactly the labels of the adapter dispatch `case "$tool"`
    block, read arm by arm, so no installable host sits in no tier. The
    argument parser's `case "$1"` arms that append to TOOLS accept exactly
    those hosts plus `all`. And each suite that keeps every adapter
    under regression names that same set in its EVERY_HOST literal, so a suite
    that drops a host stops covering it out loud rather than silently.
    """
    install = ROOT / "install.sh"
    matrix = ROOT / "documentation" / "host-capability-matrix.md"
    if not install.is_file() or not matrix.is_file():
        return
    where = "documentation/host-capability-matrix.md and install.sh"
    src = install.read_text(encoding="utf-8")
    arrays: dict[str, list[str]] = {}
    for tier, var in (("first-class", "FIRST_CLASS_TOOLS"),
                      ("supported", "SUPPORTED_TOOLS"),
                      ("frozen", "FROZEN_TOOLS")):
        m = re.search(rf"^{var}=\(([^)]*)\)", src, re.M)
        if not m:
            fail(f"install.sh: no {var}=(...) array. The tier assignment has "
                 f"lost its one home, so {where} can no longer be compared")
            return
        arrays[tier] = m.group(1).split()
    seen: dict[str, str] = {}
    for tier, hosts in arrays.items():
        for host in hosts:
            if host in seen:
                fail(f"install.sh: {host} is in both the {seen[host]} and the "
                     f"{tier} tier; a host has one tier (ADR-0009)")
            seen.setdefault(host, tier)
    maintained = arrays["first-class"] + arrays["supported"]
    m = re.search(r"^\s*all\)\s*expanded\+=\(([^)]*)\)", src, re.M)
    if not m:
        fail("install.sh: no `all) expanded+=(...)` line, so what `all` "
             "installs cannot be held to the tier arrays")
    elif sorted(m.group(1).split()) != sorted(maintained):
        fail(f"install.sh: `all` expands to {m.group(1).split()}, and the "
             f"first-class and supported tiers are {sorted(maintained)}. `all` "
             f"installs the maintained hosts and no other (ADR-0009)")

    # The dispatch universe is every label of the `case "$tool"` block that
    # installs `expanded`, whatever each arm's command looks like: a
    # line-shaped regex missed `cursor) install_cursor || true ;;` (review m1).
    # A label that is not a bare tool name is refused, not guessed at.
    dispatched: list[str] = []
    arms = _case_arms(src, r'^\s*case\s+"\$tool"\s+in\b')
    if not arms:
        fail("install.sh: no `case \"$tool\" in … esac` adapter dispatch, so "
             "the tools it installs cannot be held to the tier arrays")
    else:
        for labels, _ in arms:
            for label in labels:
                if label == "*":
                    continue
                if not re.fullmatch(r"[a-z][a-z-]*", label):
                    fail(f"install.sh: the adapter dispatch has the label "
                         f"{label!r}, which is not a bare tool name, so the "
                         f"tool it installs cannot be held to the tier arrays")
                    continue
                dispatched.append(label)
        dispatched = sorted(set(dispatched))
    if arms and sorted(seen) != dispatched:
        fail(f"install.sh: the tier arrays hold {sorted(seen)}, and the "
             f"adapter dispatch installs {dispatched}. Every tool install.sh "
             f"installs sits in exactly one tier (ADR-0009): "
             f"untiered {sorted(set(dispatched) - set(seen))}, "
             f"tiered but not installable {sorted(set(seen) - set(dispatched))}")

    # The argument parser's accepted-tool pattern is the third literal host
    # list: every arm of `case "$1"` that appends to TOOLS. It accepts the
    # tiered hosts plus `all`, and nothing else.
    parser = _case_arms(src, r'^\s*case\s+"\$1"\s+in\b')
    accepted = sorted({label for labels, body in (parser or [])
                       if re.search(r"\bTOOLS\+=", body) for label in labels})
    if not accepted:
        fail("install.sh: no `case \"$1\"` arm appends to TOOLS, so the tools "
             "the argument parser accepts cannot be held to the tier arrays")
    elif accepted != sorted(set(seen) | {"all"}):
        want = set(seen) | {"all"}
        fail(f"install.sh: the argument parser accepts {accepted}, and the "
             f"tier arrays plus `all` are {sorted(want)}. The command line "
             f"takes a host only if a tier holds it (ADR-0009): "
             f"untiered {sorted(set(accepted) - want)}, "
             f"tiered but refused {sorted(want - set(accepted))}")
    for suite in ("test-full-install.sh", "test-install-placement.sh",
                  "test-unified-graph-install.sh"):
        path = ROOT / "tests" / suite
        if not path.is_file():
            continue
        m = re.search(r'^EVERY_HOST="([^"]*)"', path.read_text(encoding="utf-8"),
                      re.M)
        if not m:
            fail(f"tests/{suite}: no EVERY_HOST=\"...\" literal, so nothing "
                 f"says which adapters this suite keeps under regression")
        elif dispatched and sorted(m.group(1).split()) != dispatched:
            fail(f"tests/{suite}: EVERY_HOST is {sorted(m.group(1).split())}, "
                 f"and install.sh dispatches {dispatched}. The suite keeps "
                 f"every adapter under regression, frozen ones included "
                 f"(ADR-0009), so it names every dispatchable tool")

    lines = matrix.read_text(encoding="utf-8").splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if re.match(r"^#+\s.*Support tiers", ln)), None)
    if start is None:
        fail("documentation/host-capability-matrix.md: no 'Support tiers' "
             "section, so the tier arrays in install.sh are published nowhere")
        return
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    published: dict[str, list[str]] = {}
    rows = 0
    for ln in lines[start + 1:]:
        if re.match(rf"^#{{1,{level}}}\s", ln):
            break
        if not ln.lstrip().startswith("|"):
            if rows:
                break                     # the section's first table only
            continue
        rows += 1
        if rows <= 2:
            continue                      # header and separator
        cells = ln.split("|")
        if len(cells) < 4:
            continue
        tier = cells[1].strip().strip("`").strip().lower()
        hosts = [h.strip().strip("`").strip()
                 for h in cells[2].split(",") if h.strip()]
        if tier in published:
            fail(f"documentation/host-capability-matrix.md: the Support tiers "
                 f"table has a second {tier} row; a tier has one row, and a "
                 f"second one lets the table say two things at once")
        for host in hosts:
            other = next((t for t, hs in published.items() if host in hs), None)
            if other is not None and other != tier:
                fail(f"documentation/host-capability-matrix.md: {host} is in "
                     f"both the {other} and the {tier} row of the Support "
                     f"tiers table; a host has one tier (ADR-0009)")
        published.setdefault(tier, []).extend(hosts)
    for tier in sorted(set(arrays) | set(published)):
        want = sorted(arrays.get(tier, []))
        got = sorted(published.get(tier, []))
        if want != got:
            fail(f"{where} disagree on the {tier} tier: the matrix's Support "
                 f"tiers table says {got}, the {tier} array in install.sh says "
                 f"{want}. install.sh is the one home; correct the table, or "
                 f"move the host in the array through an ADR")


def check_install_write_sites() -> None:
    """SINGLE_WRITER is true of the four placers and a NAMED, COUNTED set of exceptions.

    `install.sh` has always had writes that bypass `place_file` and friends —
    the migration note is authored rather than copied, `place_kernel` lays the
    sibling link by hand because the link is project-local and relative, and
    `fill_plant_facts` merges the plant's own facts into `index.md` in place.
    SPEC-0001 said "the write passes through one of four named operations" with
    no exceptions, and the M7 sweep it cites observes RECOVERABILITY, not
    mechanism, so the row was green against a contract that was false.

    The honest contract names its exceptions. The honest CHECK derives them AND
    counts them: keyed on (function, verb) alone, every pair already in the
    table was an open licence for one more write of the same shape.
    """
    sites = install_write_sites()
    # `ensure_dir` used to be exempted WHOLESALE — not a placer, not in the
    # exception table, not in SPEC-0001 §4, and any number of writes of any verb
    # inside it were dropped. The check's own docstring calls an already-present
    # key "an open licence for one more write of the same shape"; that was an
    # open licence for every shape, for ever. It is a counted row now like
    # everything else.
    expectations = {**INSTALL_WRITE_EXCEPTIONS, **PLACER_WRITES}
    for key in sorted(sites):
        fn, word = key
        lines = sites[key]
        if key not in expectations:
            fail(f"install.sh:{lines[0]}: `{word}` in {fn}() writes without going "
                 f"through one of the four named placement operations, and "
                 f"SPEC-0001 SINGLE_WRITER does not record it as an exception. "
                 f"Route it through a placer, or add it to "
                 f"INSTALL_WRITE_EXCEPTIONS and to SPEC-0001 §4.")
            continue
        expected = expectations[key][0]
        if len(lines) != expected:
            fail(f"install.sh: `{word}` in {fn}() now appears {len(lines)} time(s) "
                 f"at {lines}, and INSTALL_WRITE_EXCEPTIONS records {expected}. "
                 f"An exception is a specific write, not a licence for the shape: "
                 f"say what the new one is, in the table and in SPEC-0001 §4, or "
                 f"route it through a placer.")
    for key in sorted(expectations):
        if key not in sites:
            fn, word = key
            table = ("PLACER_WRITES" if key in PLACER_WRITES
                     else "INSTALL_WRITE_EXCEPTIONS")
            fail(f"seed-lint: {table} records `{word}` in "
                 f"{fn}() and install.sh no longer has it. Strike the row, and "
                 f"strike it from SPEC-0001 §4 — an "
                 f"exception nobody needs is a licence nobody revoked.")
    if not any(k[0] in NAMED_PLACERS for k in sites):
        fail("seed-lint: install.sh has no writes inside place_file/"
             "place_state/place_if_missing/place_generated — the attribution "
             "in install_write_sites() has stopped binding, so every finding "
             "above and below it is meaningless.")
    # The count SPEC-0001 §4 states about itself, bound to the table that
    # derives it. It read "three writes" while the table held six target-side
    # rows and §4 described a seventh it did not hold.
    spec = ROOT / "docs" / "specs" / "SPEC-0001-install-placement.md"
    if spec.is_file():
        # sum the per-row COUNTS, not the rows. Counting rows made "8 writes"
        # true only by the coincidence that every row held exactly 1: adding a
        # second write to an existing row moved the real total and left the
        # number in SPEC-0001 §4 standing.
        for key, value in sorted(INSTALL_WRITE_EXCEPTIONS.items()):
            if len(value) != 3 or value[1] not in ("target", "temp"):
                fail(f"seed-lint: INSTALL_WRITE_EXCEPTIONS row {key} does not "
                     f"declare whether it writes into the TARGET or into a TEMP "
                     f"tree. Undeclared used to mean temp-side, which is how an "
                     f"eleventh write into the plant passed while SPEC-0001 §4 "
                     f"still said ten.")
        text = spec.read_text(encoding="utf-8", errors="replace")
        if f"{TARGET_SIDE_WRITE_EXCEPTIONS} writes into the target" not in text:
            fail(f"SPEC-0001 §4 must say '{TARGET_SIDE_WRITE_EXCEPTIONS} writes "
                 f"into the target' — that is what INSTALL_WRITE_EXCEPTIONS "
                 f"currently holds. It said 'three' while the table held six, "
                 f"which is how a derived claim goes stale in prose.")


def check_published_body_figures() -> None:
    """The body-size claims derive from the same measurement the ceilings do,
    and they have one required home, BODY_FIGURE_HOME.

    U-15 was "README claimed `<500`-line bodies while three protocols sat
    between 658 and 931". The repair replaced `<500` with `1 384`, `median of
    166`, `1 000` and `2 500` — four numbers, all true on the day, and NONE of
    them derived. Appending sixty lines to `protocols/graft.md` left seed-lint
    PASS with the page still saying 1 384; tightening MACHINERY_BODY_CEILING
    to 900 left it still saying 1 000. That is U-15's own class — a reader-facing
    body-size number that nothing derives — reopened by its own fix.

    The figures used to live in README, and this check returned silently when
    README was absent, so moving the text would have left the fact held by
    nothing. SPEC-0004 (C5) moved them to BODY_FIGURE_HOME and made an absent
    home, or a home missing any of the four, a finding.

    `EAGER_EXEMPTIONS` gets the same treatment: a page that says the dict is
    "empty" or the budget has "no slack" fails when an exemption is re-added
    with the documented `--bless` signature. The phrase rules read every
    front-door file, not one page, so the sentence cannot move out of reach.
    """
    home = ROOT / BODY_FIGURE_HOME
    if not home.is_file():
        fail(f"{BODY_FIGURE_HOME} is missing, and it is the one home of the four "
             f"body-size figures (SPEC-0004 BODY_FIGURE_HOME)")
    else:
        text = home.read_text(encoding="utf-8", errors="replace")
        for value, what, largest_label in routable_body_figures():
            if not any(form in text for form in grouped_forms(value)):
                fail(f"{BODY_FIGURE_HOME} states no figure matching {what} ({value}). "
                     f"These four numbers are the ones U-15 was about, and the fix that "
                     f"replaced `<500` left them derived by nothing — correct the "
                     f"claim in their one home (largest is {largest_label})")

    for rel in fd_front_door_files():
        page = ROOT / rel
        if not page.is_file():
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        empty_claim = any(p in text for p in EAGER_EMPTY_PHRASES)
        if empty_claim and EAGER_EXEMPTIONS:
            fail(f"{rel} says EAGER_EXEMPTIONS is 'consequently empty' and it "
                 f"holds {sorted(EAGER_EXEMPTIONS)}. An exemption is a debt; the "
                 f"page that says there is none has to fail when one is added")
        if EAGER_NO_SLACK_PHRASE in text and EAGER_EXEMPTIONS:
            fail(f"{rel} claims the EAGER_BUDGET ratchet has 'no slack' while "
                 f"EAGER_EXEMPTIONS is non-empty")


# The two phrases that claim EAGER_EXEMPTIONS holds nothing. One home, because
# check_published_body_figures and SPEC-0004's BODY_FIGURES_HAVE_A_REQUIRED_HOME
# both hold them in every front-door file.
EAGER_EMPTY_PHRASES = ("consequently **empty**", "is consequently empty")
EAGER_NO_SLACK_PHRASE = "no slack"


def grouped_forms(n: int) -> tuple:
    """Every spelling the prose actually uses. The page groups thousands
    with a NARROW NO-BREAK SPACE (U+202F), and a check that only knew about
    an ordinary space reported the figure missing while it was on screen."""
    plain = f"{n:,}"
    return (str(n), plain.replace(",", " "), plain.replace(",", "\u202f"),
            plain.replace(",", "\u2009"), plain.replace(",", "\u00a0"))


def routable_body_figures() -> list:
    """The four body-size figures a reader is shown, as (value, what, largest
    node): the largest and median routable body, measured here, and the two
    ceilings that bound them. One computation for every page that prints them."""
    sizes = sorted((len(body.strip("\n").splitlines()), label)
                   for label, _fm, body in machinery_nodes())
    largest, largest_label = sizes[-1]
    mid = len(sizes) // 2
    median = (sizes[mid][0] if len(sizes) % 2
              else (sizes[mid - 1][0] + sizes[mid][0]) // 2)
    return [(largest, "the largest routable body", largest_label),
            (median, "the median routable body", largest_label),
            (MACHINERY_BODY_CEILING, "MACHINERY_BODY_CEILING", largest_label),
            (LIFECYCLE_BODY_CEILING, "LIFECYCLE_BODY_CEILING", largest_label)]


def check_ci_workflow() -> None:
    """The CI that the seed's own-gate row (DOCUMENTATION.md#enf-seed-gate) and
    DOCUMENTATION §14 say runs this gate actually exists and runs it.

    U-25 was closed by adding `.github/workflows/gate.yml`, and nothing in the
    gate asserted it: deleting the file left all 42 steps green while the front
    door went on saying the seed runs its own gate in CI. A claim about a mechanism,
    with the mechanism unpinned, is the shape this release spent eighteen slices
    on.

    What this can NOT assert is that a run has ever gone green — the workflow is
    untracked as of 7.16.0 and has never executed. `gate-registry.py` records
    that, under NON_STEP_GUARDS.
    """
    wf = ROOT / ".github" / "workflows" / "gate.yml"
    if not wf.is_file():
        fail(".github/workflows/gate.yml is missing — the enf-seed-gate row "
             "(DOCUMENTATION.md#enf-seed-gate) says the seed runs its own gate in "
             "CI, and nothing else in this suite would notice its absence")
        return
    raw = wf.read_text(encoding="utf-8", errors="replace")
    # Comments stripped before the content checks: the file's own comment
    # explains that there is NO `pip install` step, and matching the word in
    # that sentence made this check fail on a workflow that is exactly right.
    text = "\n".join(re.sub(r"#.*$", "", line) for line in raw.splitlines())
    if "tests/run.sh" not in text:
        fail(".github/workflows/gate.yml does not run tests/run.sh — CI that "
             "runs a subset is not 'the same gate'")
    if "pip install" in text:
        fail(".github/workflows/gate.yml has a `pip install` step. The gate must "
             "run on a bare python3: that is what stops a third-party import "
             "passing locally and failing for an adopter, and it is why "
             "test_agent_lint.py was ported off pytest")
    for platform in ("ubuntu", "macos"):
        if platform not in raw:
            fail(f".github/workflows/gate.yml no longer names {platform}; the "
                 f"enf-seed-gate row (DOCUMENTATION.md#enf-seed-gate) and §14 claim "
                 f"both platforms, and a claim about a matrix needs the matrix")


def check_release_workflow() -> None:
    """`.github/workflows/release.yml` still points at what it promises.

    Syntactic, like `check_ci_workflow` beside it: this cannot prove the
    workflow actually publishes a correct release, only that the pieces
    CLAUDE.md's Release section and `tools/prepare-release.py` describe are
    still wired together — the tag pattern, the write permission the release
    API needs, the staged-notes path both files agree on, and the manifest
    version it must not diverge from.
    """
    wf = ROOT / ".github" / "workflows" / "release.yml"
    if not wf.is_file():
        fail(".github/workflows/release.yml is missing — CLAUDE.md's Release "
             "section and tools/prepare-release.py both describe a tag-triggered "
             "publish workflow that would no longer exist")
        return
    text = "\n".join(re.sub(r"#.*$", "", line)
                      for line in wf.read_text(encoding="utf-8", errors="replace").splitlines())
    if not re.search(r"tags:\s*\[.*v\[0-9\]\+\.\[0-9\]\+\.\[0-9\]\+.*\]", text):
        fail(".github/workflows/release.yml no longer triggers on a vX.Y.Z tag "
             "push — tools/prepare-release.py's printed next-step tags exactly "
             "that pattern")
    if "contents: write" not in text:
        fail(".github/workflows/release.yml lost `contents: write` — "
             "`gh release create` needs it")
    if ".github/RELEASE_NOTES.md" not in text:
        fail(".github/workflows/release.yml no longer reads "
             ".github/RELEASE_NOTES.md — that path is the one "
             "tools/prepare-release.py stages")
    if "manifest.json" not in text:
        fail(".github/workflows/release.yml dropped its manifest.json version "
             "check — the guard against a stray tag publishing the wrong notes")
    if "gh release create" not in text:
        fail(".github/workflows/release.yml no longer calls `gh release create`")


def check_body_ceiling() -> None:
    """No routable node grows without a limit.

    graph-lint.py's 170-line ceiling exempts machinery (`not n.is_machinery`),
    which is why it bound none of the nodes that had actually grown large, and
    README.md claimed `<500`-line bodies while three protocols sat between 658
    and 931 lines. A claim is not a budget either.

    The FRONTMATTER is bounded too, and separately. A node is loaded whole —
    ADR-0004 and ADR-0007 both say so — and this check counted only the half
    that is cheap to count: 2 000 frontmatter lines and 223 KB were appended to
    `protocols/canonize.md`, the body untouched, and all 42 gates passed. The
    ceiling bounded the cheap half of a file whose expensive half is the same
    file. Measured when the bound was set: 60 nodes, largest 50 lines / 1 826
    bytes (`agents/00-orchestrator.md`), so this is roughly 2x headroom and is
    ratcheted like every other limit.
    """
    for label, _fm, body in machinery_nodes():
        # From the FILE, not from the parsed dict: the parsed form loses the
        # thing being bounded (how much text the harness loads), and a dict with
        # few keys can carry megabytes in one value.
        raw = (ROOT / label).read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
        fm_lines = len(m.group(1).splitlines()) if m else 0
        if fm_lines > FRONTMATTER_CEILING:
            fail(f"{label}: frontmatter is {fm_lines} lines, over the "
                 f"{FRONTMATTER_CEILING}-line ceiling. A node is loaded whole, "
                 f"so metadata is context too — this is not the place to put a "
                 f"body the body ceiling would have refused")
        lines = len(body.strip("\n").splitlines())
        lifecycle = label in LIFECYCLE_NODES
        ceiling = LIFECYCLE_BODY_CEILING if lifecycle else MACHINERY_BODY_CEILING
        if lines > ceiling:
            which = ("cross-project meta-loop" if lifecycle
                     else "machinery")
            fail(f"{label}: body is {lines} lines, over the "
                 f"{ceiling}-line {which} ceiling — split it "
                 f"along a declared `owns:` fact, or raise the ceiling with a "
                 f"recorded owner decision (never to fit new text)")


def description_of(fm: dict) -> str:
    d = fm.get("description")
    return d if isinstance(d, str) else ""


def check_eager_surface(kernel_bytes: int) -> None:
    """Bound what each harness loads on EVERY session, before any routing.

    The kernel is not the whole always-loaded surface — it is the part the seed
    happened to be counting. Each harness also enumerates roster and skill
    metadata at start-up, and github-copilot applies whole skill BODIES via
    `applyTo: '**'`. Measured here from the seed sources the projections are
    taken from, so the number cannot drift from what install.sh places.
    """
    surfaces = eager_surfaces(kernel_bytes)
    # SPEC-0003 PRIME_EAGER_SURFACE_WITHIN_BUDGET: the prime-agent surface counts
    # the whole overlay, so the `## Surfaced nodes` section is paid here on every
    # Prime Agent session and held to EAGER_BUDGET like every other harness.
    for harness, measured in sorted(surfaces.items()):
        if harness in EAGER_EXEMPTIONS:
            allowed, reason = EAGER_EXEMPTIONS[harness]
            # A recorded exemption may shrink, never grow. This is the one
            # direction that keeps enumerated debt honest.
            if measured > allowed:
                fail(f"eager surface [{harness}]: {measured} bytes exceeds its "
                     f"RECORDED exemption of {allowed} ({reason}). An exemption "
                     f"is a debt that may only shrink — do not raise it to fit "
                     f"new text; reduce the surface or take it to the owner")
            continue
        if measured > EAGER_BUDGET:
            fail(f"eager surface [{harness}]: {measured} bytes exceeds the "
                 f"{EAGER_BUDGET}-byte budget — this is paid on every session "
                 f"of every plant before any routing happens")
    check_published_eager_figures(surfaces)


def eager_surfaces(kernel_bytes: int) -> dict:
    """What each harness loads on every session, in bytes, measured from the
    seed sources the projections are taken from (check_eager_surface's
    computation, and the one home of the figures every page publishes)."""
    agent_desc = sum(
        len(description_of(fm))
        for label, fm, _b in machinery_nodes() if label.startswith("agents/"))
    skill_desc = sum(
        len(description_of(fm))
        for label, fm, _b in machinery_nodes() if label.startswith("skills/"))
    skill_bodies = sum(
        len(b) for label, _fm, b in machinery_nodes() if label.startswith("skills/"))
    overlay = ROOT / "integrations/prime-agent/APPEND_SYSTEM.md"
    overlay_bytes = overlay.stat().st_size if overlay.exists() else 0

    # What each harness pays before it has routed anything. install.sh's
    # per-adapter installers are the source of truth for these shapes;
    # prime-agent enumerates no static roster (delegation is a runtime rlm()
    # spawn), and copilot's instruction files are always-applied.
    # All five stay here on purpose, the two frozen hosts included: a plant that
    # names one still pays its surface on every session. A frozen host alone
    # over budget is a removal trigger under ADR-0009, taken to the owner, and
    # never an EAGER_EXEMPTIONS entry.
    surfaces = {
        "claude-code": kernel_bytes + agent_desc + skill_desc,
        "opencode": kernel_bytes + agent_desc + skill_desc,
        "codex": kernel_bytes + agent_desc + skill_desc,
        "prime-agent": kernel_bytes + skill_desc + overlay_bytes,
        # Copilot was `+ skill_bodies` until 7.16.0, because its skill
        # projections carried `applyTo: '**'` — every skill BODY always applied,
        # 138 535 bytes against what every other harness pays. They are
        # pointers now:
        # the description that lets a session decide whether a skill applies,
        # and the path to the node that holds the discipline. So it is modelled
        # like every other harness, plus the pointer boilerplate each file adds.
        "github-copilot": kernel_bytes + agent_desc + skill_desc + COPILOT_POINTER_OVERHEAD,
    }
    return surfaces


def check_published_eager_figures(surfaces: dict) -> None:
    """Every published copy of these numbers agrees with the computation.

    This function was described, in the document that publishes them, as "their
    one home … the table above is held against it by the gate". It was not:
    changing 31 893 to 99 999 in the matrix left the whole suite green, and the
    figures went stale twice in one release — once when consolidating the
    frontmatter readers moved four of the five by 6 bytes, and again when a
    ten-byte kernel edit moved all five while the corrected numbers were being
    written down. Chasing them is the wrong repair; a reader-facing number
    either derives from the computation or it should not be printed.

    The published form is `NN NNN` (thin-space grouped) or `NNNNN`, so both are
    matched, and a figure that appears nowhere is not an error — this holds the
    copies that exist, it does not require any. It reads every front-door file
    (SPEC-0004 C5), not only the EAGER_PUBLISHED pair, so a figure moved anywhere
    in the front door stays held.

    Being some live figure is not enough on a line that names one harness: the
    figure must be that harness's own. README's Claude Code figure once carried
    the Prime Agent number and passed, because any computed value did.
    """
    live = set(surfaces.values()) | {EAGER_BUDGET}
    for rel in fd_front_door_files():
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for _n, m, value in stale_eager_figures(text, live):
            closest = min(live, key=lambda v: abs(v - value))
            fail(f"{rel}: publishes {m.group(1)} bytes as an always-loaded "
                 f"surface, and check_eager_surface computes no such figure "
                 f"(nearest: {closest}). These numbers have one home and it "
                 f"is not this page — correct it, mark it as historical, or "
                 f"stop printing a figure nothing derives")
        for n, m, value, harness in misattributed_eager_figures(text, surfaces):
            fail(f"{rel}:{n}: publishes {m.group(1)} bytes for {harness}, and "
                 f"check_eager_surface computes {surfaces[harness]} for that "
                 f"harness. A line that names one harness prints that harness's "
                 f"figure")


# The pages check_published_eager_figures held before SPEC-0004 widened it to
# every front-door file. EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED never lets
# FRONT_DOOR_PENDING hold a finding on these two.
EAGER_PUBLISHED = ("README.md", "documentation/host-capability-matrix.md")
# A five-digit figure in a byte context is a claim about the always-loaded
# surface, and must equal what the computation produces. `was`/`before`/
# `historical`/`budget`/`ceiling`/`max` on the same line mark a figure that is
# deliberately NOT current — the 138 535 bytes Copilot used to pay, for
# instance — and those are left alone.
EAGER_FIGURE = re.compile(r"\b(\d{2}[  \u2009]?\d{3})\s*(?:B\b|bytes\b)")
EAGER_HISTORICAL = re.compile(r"\b(was|were|before|until|historical|budget|ceiling"
                              r"|max|limit|previously)\b", re.I)


def stale_eager_figures(text: str, live: set) -> list:
    """(line number, match, value) for each always-loaded byte figure in the
    text that the computation does not produce, historical lines skipped."""
    stale = []
    for n, line in enumerate(text.splitlines(), 1):
        if EAGER_HISTORICAL.search(line):
            continue
        for m in EAGER_FIGURE.finditer(line):
            value = int(re.sub(r"[  \u2009]", "", m.group(1)))
            if value not in live:
                stale.append((n, m, value))
    return stale


# How a front-door line names each harness whose eager surface is computed.
EAGER_HARNESS_NAMES = {"claude-code": "Claude Code", "opencode": "opencode",
                       "codex": "Codex", "prime-agent": "Prime Agent",
                       "github-copilot": "Copilot"}


def misattributed_eager_figures(text: str, surfaces: dict) -> list:
    """(line number, match, value, harness) for each always-loaded byte figure
    on a line that names exactly one harness and differs from that harness's
    computed surface, historical lines skipped. A line naming several harnesses,
    such as a matrix header row, is left to stale_eager_figures."""
    wrong = []
    for n, line in enumerate(text.splitlines(), 1):
        if EAGER_HISTORICAL.search(line):
            continue
        named = [h for h, name in EAGER_HARNESS_NAMES.items()
                 if h in surfaces and re.search(rf"\b{re.escape(name)}\b", line, re.I)]
        if len(named) != 1:
            continue
        for m in EAGER_FIGURE.finditer(line):
            value = int(re.sub(r"[  \u2009]", "", m.group(1)))
            if value != surfaces[named[0]]:
                wrong.append((n, m, value, named[0]))
    return wrong


def check_agent_spawn_grants(agents: dict) -> None:
    """The delegator invariant: can_delegate == (spawn tool in tools).

    The grant is read by agent-lint's own `grants_spawn`, so the seed and every
    plant hold one reading: `Agent` or its alias `Task`, bare or parenthesized.
    This copy once matched the literal `Task` only, and read an omitted
    `tools:` line as "no Task", while the host gives an agent without that line
    every tool, the spawn tool included.
    """
    grants_spawn = load_tool("integrations/claude-code/agent-lint.py").grants_spawn
    for a in agents.values():
        fm, rel = a["fm"], a["path"].relative_to(ROOT).as_posix()
        declares = str(fm.get("can_delegate", "false")).lower() == "true"
        if "tools" not in fm:
            fail(f"{rel}: omits its tools: line, so it inherits every tool, the "
                 f"spawn tool included; list the tools it may use")
        elif grants_spawn(fm["tools"]) != declares:
            fail(f"{rel}: can_delegate={str(declares).lower()} but the spawn tool "
                 f"(`Agent`, alias `Task`) {'is not' if declares else 'is'} in tools")
        if declares:
            if "max_spawn_depth" not in fm:
                fail(f"{rel}: delegator without max_spawn_depth")
            for target in fm.get("delegates_to", []):
                if target not in agents:
                    fail(f"{rel}: delegates_to unknown agent '{target}'")


def check() -> None:
    # -- gather ground truth from agents/ frontmatter -------------------
    agent_files = sorted(p for p in (ROOT / "agents").glob("*.md"))
    agents = {}
    for p in agent_files:
        fm = parse_frontmatter(p)
        name = fm.get("name")
        if not name:
            fail(f"{p}: frontmatter has no name")
            continue
        agents[name] = {"path": p, "fm": fm}

    check_agent_spawn_grants(agents)
    delegators = {name for name, a in agents.items()
                  if str(a["fm"].get("can_delegate", "false")).lower() == "true"}

    # -- manifest <-> disk ----------------------------------------------
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest_agents = {a["name"] for a in manifest.get("agents", [])}
    for name in agents:
        if name not in manifest_agents:
            fail(f"manifest.json: agents[] is missing '{name}'")
    for name in manifest_agents:
        if name not in agents:
            fail(f"manifest.json: agents[] lists '{name}' with no file in agents/")
    for section in ("agents", "protocols", "skills"):
        for entry in manifest.get(section, []):
            if not (ROOT / entry["file"]).exists():
                fail(f"manifest.json: {section} file does not exist: {entry['file']}")
    for entry in manifest.get("templates", []):
        if not (ROOT / entry["file"]).exists():
            fail(f"manifest.json: template file does not exist: {entry['file']}")

    # ...and the other direction. Everything above asks "does what the manifest
    # claims exist?"; nothing asked "is what exists claimed?", so a file could be
    # added to the tree and never cataloged. Two top-level templates
    # (agent.template.md, skill.template.md) sat uncataloged that way while
    # README, the orchestrator charter, delegation.md and three reference
    # documents all told a reader to use them. The agents[] section has had this
    # check both ways from the start; the rest inherit it now.
    # Only the TOP level of templates/ is compared: templates/docs/** is a
    # scaffold tree the manifest catalogs as one directory entry on purpose, and
    # enumerating its ~28 leaves here would be a second home for that list.
    disk_sections = {
        "protocols": sorted(p.as_posix() for p in (ROOT / "protocols").glob("*.md")),
        "skills": sorted((d / "SKILL.md").as_posix()
                         for d in sorted((ROOT / "skills").iterdir())
                         if (d / "SKILL.md").is_file()),
        "templates": sorted(p.as_posix() for p in (ROOT / "templates").glob("*.md")),
    }
    for section, disk_files in disk_sections.items():
        cataloged = {e["file"] for e in manifest.get(section, [])}
        for f in disk_files:
            rel = str(pathlib.PurePosixPath(f).relative_to(ROOT.as_posix()))
            if rel not in cataloged:
                fail(f"manifest.json: {section}[] does not catalog '{rel}' — it is "
                     f"on disk and shipped, so a reader can be pointed at a file "
                     f"the manifest says nothing about")

    # -- version single source: manifest == CHANGELOG top entry ---------
    # The version is the repo's most fundamental state fact; the CLAUDE.md
    # convention "behavior change ⇒ bump manifest + CHANGELOG" is only real
    # if the two cannot silently diverge.
    mver = manifest.get("version", "")
    changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    cm = re.search(r"^##\s+(\d+\.\d+\.\d+)\b", changelog_text, re.MULTILINE)
    if not cm:
        fail("CHANGELOG.md: no '## X.Y.Z' version heading found")
    elif cm.group(1) != mver:
        fail(f"version drift: manifest.json is {mver!r} but the top CHANGELOG "
             f"entry is {cm.group(1)!r} — bump both together")

    # -- kernel roster table, anchors, budget, canonical reference ------
    kernel_text = KERNEL.read_text(encoding="utf-8")
    for name in agents:
        if f"`{name}`" not in kernel_text:
            fail(f"core/AGENTS.md: §1 roster does not mention `{name}`")
    for n in range(1, 9):
        if not re.search(rf"^### 3\.{n} ", kernel_text, re.MULTILINE):
            fail(f"core/AGENTS.md: stable anchor §3.{n} heading is missing")
    size = KERNEL.stat().st_size
    if size > KERNEL_BUDGET:
        fail(f"core/AGENTS.md: {size} bytes exceeds the {KERNEL_BUDGET}-byte budget "
             f"(every session of every plant pays this file)")
    check_body_ceiling()
    check_eager_surface(size)
    check_spec_test_mapping()
    check_spec_rows_name_their_contract()
    check_frontmatter_reader_is_one_reader()
    check_frontmatter_is_portable_yaml()
    check_install_write_sites()
    check_shell_floor_claim_matches_the_shebang()
    check_host_tiers()
    check_plan_ledgers()
    check_protocol_reference()
    check_gate_single_home()
    check_file_endings()
    check_canonical_router_blocks()
    check_canonical_plant_root_boundary()
    check_hook_text_restates_no_kernel_rule()
    check_hook_reach_phrases()
    check_published_body_figures()
    check_ci_workflow()
    check_release_workflow()
    check_charter_vocabulary()
    check_agents_reference()
    check_skills_reference()
    check_reference_second_views()
    if "graph-session-bootstrap.md" not in kernel_text:
        fail("core/AGENTS.md: does not reference the canonical "
             "templates/prompts/graph-session-bootstrap.md block")
    canonical = ROOT / "templates/prompts/graph-session-bootstrap.md"
    if not canonical.exists():
        fail("templates/prompts/graph-session-bootstrap.md: canonical block missing")
    else:
        # the fenced block is the one home; embedding templates must carry
        # it byte-identical (the deliberate runtime-brief exception)
        # SPEC-0003 BRIEF_TEMPLATES_BYTE_IDENTICAL (I-2): spawned workers see
        # exactly what they saw before. This identity check is its gate half;
        # the other half is the verify record `git diff --quiet ac61a3f --
        # templates/prompts/graph-session-bootstrap.md
        # templates/prompts/handback-payload.md` (SPEC-0003 §10).
        m = re.search(r"```\n(GRAPH DISCIPLINE.*?)```", canonical.read_text(encoding="utf-8"), re.DOTALL)
        if not m:
            fail(f"{canonical}: no fenced GRAPH DISCIPLINE block found")
        else:
            block = m.group(1)
            for rel in ("templates/prompts/investigation-brief.md",
                        "templates/prompts/node-authoring-brief.md",
                        "templates/prompts/growth-scout-brief.md",
                        "templates/prompts/growth-author-brief.md",
                        "templates/prompts/clean-context-validation-brief.md"):
                p = ROOT / rel
                if not p.exists():
                    fail(f"{rel}: embedding template missing")
                elif block not in p.read_text(encoding="utf-8"):
                    fail(f"{rel}: embedded GRAPH DISCIPLINE block has drifted from "
                         f"the canonical copy in {canonical.name} — sync it verbatim")

    # -- spawn tracing contract: every delegation brief carries the
    # caller-minted spawn_id and the handback payload echoes it
    # (delegation.tracing — the correlation chain only works if no
    # template drops the field)
    for rel in ("templates/prompts/handback-payload.md",
                "templates/prompts/investigation-brief.md",
                "templates/prompts/node-authoring-brief.md",
                "templates/prompts/growth-scout-brief.md",
                "templates/prompts/growth-author-brief.md",
                "templates/prompts/clean-context-validation-brief.md"):
        p = ROOT / rel
        if p.exists() and "spawn_id" not in p.read_text(encoding="utf-8"):
            fail(f"{rel}: no spawn_id field — the delegation trace chain "
                 f"(delegation.tracing) breaks at this template")

    # -- machinery nodes: the seed's method surface is graph content ----
    # Every protocol, skill, agent, and method file installs into a
    # plant's docs/graph/ as a routable node; its frontmatter must carry
    # the node contract, owns keys must be globally unique, and the
    # eight rule fact-keys must live in exactly their mapped homes.
    machinery: list[tuple[Path, str, str | None]] = []   # (path, kind, expected-name)
    for p in sorted((ROOT / "protocols").glob("*.md")):
        machinery.append((p, "protocol", p.stem))
    for d in sorted((ROOT / "skills").iterdir()):
        if (d / "SKILL.md").exists():
            machinery.append((d / "SKILL.md", "skill", d.name))
    for p in sorted((ROOT / "agents").glob("*.md")):
        machinery.append((p, "agent", None))      # agents: name from frontmatter
    for p in sorted((ROOT / "core" / "method").glob("*.md")):
        machinery.append((p, "method", p.stem))

    owns_home: dict[str, Path] = {}
    command_protocols: set[str] = set()
    node_ids: set[str] = set()
    requires_adj: dict[str, list[str]] = {}
    edge_refs: list[tuple[Path, str, str, str]] = []   # (rel, src-id, edge-type, target-id)
    for p, kind, expected in machinery:
        fm = parse_frontmatter(p)
        if not fm:
            continue
        rel = p.relative_to(ROOT)
        name = expected if expected is not None else fm.get("name")
        want_id = f"{kind}.{name}"
        if fm.get("id") != want_id:
            fail(f"{rel}: id must be {want_id!r} (got {fm.get('id')!r})")
        if fm.get("kind") != kind:
            fail(f"{rel}: kind must be {kind!r}")
        if str(fm.get("tier")) != "2":
            fail(f"{rel}: tier must be 2")
        if fm.get("origin") != "seed":
            fail(f"{rel}: origin must be 'seed' (graft ownership marker)")
        for key in ("title", "owns", "est_tokens", "prevents"):
            if not fm.get(key):
                fail(f"{rel}: machinery node missing {key!r}")
        # `prevents:` is the counterfactual — what goes wrong in this node's
        # ABSENCE — and it exists because HANDOFF Decision C (U-40) asked what a
        # justification owes per component and this was the only owed item with
        # no home. It is the one column of that justification the seed can
        # actually source; evidence-of-use and class need a grown plant, and
        # `tools/roster-justification.py` says so rather than guessing them.
        #
        # The cheap failure is restating `title:`/`description:` in the future
        # tense, which reads like a justification and carries no new fact. That
        # is caught below. What is NOT caught is a well-formed `prevents:` that
        # is simply untrue — no linter can reach that, and the gate registry
        # records it as this step's semantic false green.
        prevents = str(fm.get("prevents", ""))
        if prevents:
            _prevents_by_node[str(rel)] = prevents
            if len(prevents) < 60:
                fail(f"{rel}: prevents: too short to name a failure ({len(prevents)} chars)")
            title_tail = str(fm.get("title", "")).split("—")[-1].strip().lower()
            if title_tail and title_tail in prevents.lower():
                fail(f"{rel}: prevents: restates title: rather than naming the "
                     f"failure the node's absence produces")
            desc = str(fm.get("description", ""))
            if desc:
                # Comparing the first 60 characters was defeated by a preamble:
                # `prevents: Without this node, the following would not happen:
                # <description verbatim>` passed, because the shifted prefix no
                # longer occurred in the description. Compare CONTENT instead —
                # any run of 10 consecutive words shared with the description is
                # the description restated, wherever it starts.
                # An n-gram test dies to one filler word every eight: inserting
                # "indeed" through a verbatim copy of the description left no
                # 10-word run and passed. Compare CONTENT OVERLAP instead —
                # what fraction of the prevents line's distinctive vocabulary
                # the description already contains. Padding cannot lower that;
                # it can only add words that are not in the description, which
                # is what actually saying something different looks like.
                import re as _re
                norm = lambda t: [w for w in _re.findall(r"[a-z][a-z-]{3,}", t.lower())
                                  if w not in _PREVENTS_STOP]
                pw, dw = norm(prevents), set(norm(desc))
                if len(pw) >= 8:
                    ratio = sum(1 for w in pw if w in dw) / len(pw)
                    if ratio >= PREVENTS_RESTATEMENT_CEILING:
                        shared = sorted({w for w in pw if w in dw})[:8]
                        fail(f"{rel}: prevents: restates description: — "
                             f"{ratio:.0%} of its distinctive words are already "
                             f"in description:. It must name what breaks WITHOUT "
                             f"this node, not what it does (shared: {shared})")
        if kind != "agent" and not fm.get("load_when"):
            fail(f"{rel}: machinery node missing 'load_when'")
        if kind == "agent" and not fm.get("routing_triggers"):
            fail(f"{rel}: agent node needs routing_triggers (its load_when source)")
        est = str(fm.get("est_tokens", ""))
        if not est.isdigit():
            fail(f"{rel}: est_tokens must be an integer (got {est!r})")
        else:
            # Every machinery node installs into a plant, where graph-lint.py's
            # check_budget enforces est_tokens within 2x of the WHOLE FILE —
            # `len(text.split()) * TOKENS_PER_WORD`, frontmatter included,
            # because a loader pays for the routing surface it opens as well as
            # the prose. The seed never checked it, so it could ship a node that
            # fails the very linter it also ships. Mirrored here with the same
            # metric. It was measured on the body alone until 2026-09-17, which
            # made this mirror WEAKER than the thing it mirrors: a node whose
            # frontmatter pushes the file out of band passed here and failed
            # graph-lint the moment it was installed. Measured with a probe node
            # (71-word body, 14-entry load_when): silent here, rejected there at
            # est_tokens=95 against a file measuring ~437.
            measured = int(len(p.read_text(encoding="utf-8").split()) * 1.35)
            declared = int(est)
            if measured > 2 * declared or declared > 2 * max(measured, 1):
                fail(f"{rel}: est_tokens={declared} but the file measures "
                     f"~{measured} (frontmatter and body) — graph-lint.py would "
                     f"reject this node once installed (must be within 2x)")
        for fact in fm.get("owns", []) or []:
            if fact in owns_home:
                fail(f"{rel}: fact-key {fact!r} already owned by "
                     f"{owns_home[fact].relative_to(ROOT)} — one home per fact")
            owns_home[fact] = p
        # `command: true` marks a protocol as a user-facing slash command;
        # install.sh generates every harness's command file from this field
        # (one home, projected — no authored command tree). It is protocol-only.
        cmd = fm.get("command")
        if kind == "protocol":
            if cmd == "true":
                command_protocols.add(name)
        elif cmd is not None:
            fail(f"{rel}: 'command:' is a protocol-only field (found on a {kind} node)")
        # Collect the graph edges for the in-source graph validation below.
        node_ids.add(want_id)
        req = fm.get("requires") or []
        requires_adj[want_id] = list(req)
        for target in req:
            edge_refs.append((rel, want_id, "requires", target))
        for target in fm.get("peers", []) or []:
            edge_refs.append((rel, want_id, "peers", target))
    for rule, home in RULE_HOMES.items():
        owner = owns_home.get(rule)
        if owner is None:
            fail(f"{home}: does not own {rule!r} — the kernel anchor points at it")
        elif owner != ROOT / home:
            fail(f"{rule}: owned by {owner.relative_to(ROOT)}, expected {home}")

    # -- harness registration: one home, and every referrer still points ----
    reg_owner = owns_home.get(REGISTRATION_FACT)
    if reg_owner is None:
        fail(f"{REGISTRATION_HOME}: does not own {REGISTRATION_FACT!r} — the "
             f"install and dispatch surfaces all point at it")
    elif reg_owner != ROOT / REGISTRATION_HOME:
        fail(f"{REGISTRATION_FACT}: owned by {reg_owner.relative_to(ROOT)}, "
             f"expected {REGISTRATION_HOME}")
    for rel in REGISTRATION_REFERRERS:
        p = ROOT / rel
        if not p.exists():
            fail(f"{rel}: registration referrer is missing from disk")
        elif REGISTRATION_FACT not in p.read_text(encoding="utf-8"):
            fail(f"{rel}: dispatches specialists by name (or installs the "
                 f"projection they come from) but never points at "
                 f"{REGISTRATION_FACT!r} — the 'installed but not spawnable' "
                 f"trap re-opens silently")

    # -- command roster: user-sovereign protocols are never slash commands --
    # Slash commands are generated projections of the protocol nodes that
    # declare `command: true`. The cross-project meta-loop (graft/grow/harvest)
    # is user-sovereign, and the durable-tool doctrine (toolcraft) folds into
    # canonize — none may become a routine slash command on any harness. This
    # guards that invariant; it does not re-declare the roster (the nodes do).
    # `toolcraft` was in this list until 7.16.0, when it stopped being a
    # protocol at all. Checking it here became vacuously true — the set is
    # built only from protocols/*.md frontmatter, so a name with no protocol
    # can never appear in it, and the failure message would have cited a file
    # that does not exist. A guard that cannot fire is not a guard.
    for sovereign in ("graft", "grow", "harvest"):
        if not (ROOT / "protocols" / f"{sovereign}.md").is_file():
            fail(f"protocols/{sovereign}.md is missing — the user-sovereign "
                 f"guard below would pass vacuously without it")
        if sovereign in command_protocols:
            fail(f"protocols/{sovereign}.md: must not declare 'command: true' — "
                 f"{sovereign} is user-sovereign, a slash command on no harness")
    if not command_protocols:
        fail("no protocol declares 'command: true' — the slash-command surface would be empty")

    # -- machinery graph edges: resolve + acyclic (the seed IS a graph) -----
    # In-source validation of the node graph the seed installs: every
    # requires:/peers: target resolves to a real machinery node, and the
    # requires: relation is acyclic. graph-lint.py enforces this too, but only
    # after an install reconstitutes docs/graph/; asserting it here makes the
    # seed a validated navigable graph at source, and names the failing seed
    # file directly instead of surfacing late as an install-test side effect.
    for rel, src, etype, target in edge_refs:
        if target not in node_ids:
            fail(f"{rel}: {etype} → unknown machinery node {target!r}")
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in requires_adj}

    def _visit(n: str, stack: list[str]) -> None:
        colour[n] = GREY
        for m in requires_adj.get(n, []):
            if m not in colour:          # unresolved target already reported
                continue
            if colour[m] == GREY:
                cyc = " → ".join(stack[stack.index(m):] + [m])
                fail(f"requires cycle in machinery graph: {cyc}")
            elif colour[m] == WHITE:
                _visit(m, stack + [m])
        colour[n] = BLACK

    for n in list(requires_adj):
        if colour[n] == WHITE:
            _visit(n, [n])

    # -- per-session instruction budget (every always-loaded file) ------
    # A tool that loads more than the kernel every session re-creates the
    # tax this lint exists to prevent. Budget covers the SUM of a tool's
    # always-loaded instruction files.
    SESSION_BUDGET = 10_000  # bytes; bootstrap kernel (~7 KB) + small overlay headroom
    oc = ROOT / "integrations/opencode/opencode.json"
    if oc.exists():
        cfg = json.loads(oc.read_text(encoding="utf-8"))
        # opencode auto-loads the project's AGENTS.md (which IS the kernel), so
        # the always-loaded total starts there and grows with anything the
        # config declares on top. Re-declaring AGENTS.md in `instructions`
        # would load the kernel twice per session — the exact tax this budget
        # exists to prevent, so it fails as a duplicate rather than as size.
        instructions = cfg.get("instructions", [])
        total = KERNEL.stat().st_size
        for rel in instructions:
            if rel in ("AGENTS.md", "CLAUDE.md"):
                fail(f"opencode.json: instructions re-declares {rel!r}, which "
                     f"opencode already auto-loads — the kernel would load twice")
                continue
            p = ROOT / rel
            if not p.exists():
                fail(f"opencode.json: instructions file not found: {rel}")
            else:
                total += p.stat().st_size
        if total > SESSION_BUDGET:
            fail(f"opencode.json: always-loaded instructions total {total} bytes "
                 f"> {SESSION_BUDGET} budget (auto-loaded AGENTS.md + {instructions})")

        # -- opencode config validity (upstream contract, verified 2026-08-05) --
        # The live schema at https://opencode.ai/config.json sets
        # additionalProperties: false, so an unknown key is a REJECTED config,
        # not a harmless hint — the seed shipped `agents`/`commands`/`skills`
        # directory keys that no release ever accepted, against a $schema URL
        # that now 404s. Keys are pinned here rather than fetched: a gate that
        # needs the network is a gate that fails offline.
        OC_SCHEMA_URL = "https://opencode.ai/config.json"
        OC_VALID_KEYS = {
            "$schema", "agent", "attachment", "autoupdate", "command",
            "compaction", "default_agent", "disabled_providers",
            "enabled_providers", "enterprise", "experimental", "formatter",
            "instructions", "logLevel", "lsp", "mcp", "model", "permission",
            "plugin", "provider", "references", "server", "share", "shell",
            "skills", "small_model", "snapshot", "subagent_depth",
            "tool_output", "tools", "username", "watcher",
        }
        if cfg.get("$schema") != OC_SCHEMA_URL:
            fail(f"opencode.json: $schema must be {OC_SCHEMA_URL!r} "
                 f"(got {cfg.get('$schema')!r}; the old config-schema.json URL 404s)")
        for key in sorted(set(cfg) - OC_VALID_KEYS):
            fail(f"opencode.json: {key!r} is not a key in opencode's config "
                 f"schema, which sets additionalProperties:false — the whole "
                 f"config is rejected, not just this key")
        # The seed's deepest legal delegation chain must be executable on
        # opencode. Its subagent_depth defaults to 1 ("prevents subagents from
        # launching subagents"), which silently caps every coordinator.
        depths = [int(a["fm"]["max_spawn_depth"]) for a in agents.values()
                  if str(a["fm"].get("max_spawn_depth", "")).isdigit()]
        if depths and cfg.get("subagent_depth") != max(depths):
            fail(f"opencode.json: subagent_depth={cfg.get('subagent_depth')!r} "
                 f"but the roster's deepest max_spawn_depth is {max(depths)} — "
                 f"the seed's delegation topology would be capped on opencode")

    # -- numeric claims in prose ----------------------------------------
    def num(tok: str) -> int:
        return int(tok) if tok.isdigit() else WORD_NUMS[tok.lower()]

    n_skills = sum(1 for _, k, _ in machinery if k == "skill")
    word_alt = "|".join(WORD_NUMS)  # word-number alternates for the count regexes
    manifest_version = json.loads(
        (ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]
    # Every shipped prose surface, including the integration READMEs and the
    # manifest — the declarative rim where roster/skill counts drift (the
    # "eight skills" / phantom-command-home class) if left unscanned.
    prose_files = ["README.md", "core/AGENTS.md", "INSTALL.md", "manifest.json"]
    prose_files += sorted(str(p.relative_to(ROOT))
                          for p in ROOT.glob("integrations/*/README.md"))
    # the companion documentation tree drifted a whole release once
    # (17 agents, no ui-ux-designer) because no gate ever read it
    prose_files += ["DOCUMENTATION.md"]
    prose_files += sorted(str(p.relative_to(ROOT))
                          for p in ROOT.glob("documentation/*.md"))
    prose = {p: (ROOT / p).read_text(encoding="utf-8")
             for p in prose_files if (ROOT / p).exists()}
    for path, text in prose.items():
        for m in re.finditer(rf"\b(\d+|{word_alt})[- ]agent team\b", text, re.I):
            if num(m.group(1)) != len(agents):
                fail(f"{path}: claims a {m.group(1)}-agent team; agents/ has {len(agents)}")
        # same fact, second phrasing — README's layout block said "17
        # specialist agents" and DOCUMENTATION.md "17 named specialist
        # agents" for a release while README line 40 said 18; up to two
        # qualifier words are allowed between the number and the noun
        for m in re.finditer(
                rf"\b(\d+|{word_alt})\s+(?:[a-z-]+\s+){{0,2}}specialist agents\b",
                text, re.I):
            if num(m.group(1)) != len(agents):
                fail(f"{path}: claims {m.group(0)!r}; "
                     f"agents/ has {len(agents)}")
        # the documented-version pins drifted a whole release unnoticed:
        # "Version documented: 6.8.0" / "(version 6.8.0)" vs manifest
        for m in re.finditer(r"[Vv]ersion(?: documented)?[:*\s]+\**(\d+\.\d+\.\d+)",
                             text):
            if path in ("DOCUMENTATION.md", "documentation/README.md") \
                    and m.group(1) != manifest_version:
                fail(f"{path}: documents version {m.group(1)}; "
                     f"manifest.json is {manifest_version}")
        for m in re.finditer(rf"\b(\d+|{word_alt})\s+(?:opus\s+)?coordinator",
                             text, re.I):
            if num(m.group(1)) != len(delegators):
                fail(f"{path}: claims {m.group(1)} coordinators; frontmatter has "
                     f"{len(delegators)}: {sorted(delegators)}")
        for m in re.finditer(rf"\b(\d+|{word_alt})\s+skills\b", text, re.I):
            if num(m.group(1)) != n_skills:
                fail(f"{path}: claims {m.group(1)} skills; skills/ has {n_skills}")

    # -- growth intake parity: the seed's collections, grow's phases, and the
    # roster's declared appetites are three views of ONE list ----------------
    # This is the check that would have caught the defect it was written for.
    # `design/` shipped in templates/docs/ from 6.9.0 and `legal/` from
    # 6.12.0, but neither was ever added to grow's unified-shape diagram, its
    # Phase 4 authoring list, or the cross-cutting scout assignment — so no
    # scout gathered the evidence, no author wrote the leaves, and no gate
    # noticed. Every plant grown in that window carries a ui-ux-designer with
    # nothing to read. A collection the installer creates must be a collection
    # growth is told to author.
    # The set of collections is ONE fact, and its home is the audit tool that
    # holds every plant to it — re-deriving it here with a second walk of
    # templates/docs/ was a second home that had already drifted: this arm
    # skipped root-level leaves the tool makes required rows, so a new
    # templates/docs/glossary.md would pass lint while opening an unanswerable
    # row in every plant.
    audit = load_tool("growth-audit.py")
    tdocs = ROOT / "templates" / "docs"
    # The audit rows are per-artifact: each runbook is its own procedure to
    # cover, and a root leaf (changelog.md) is a row of its own. grow.md speaks
    # at collection granularity, so the prose arms match on the prefix while
    # the roster arm accepts either — an agent reads `runbooks/`, the audit
    # answers for `runbooks/rollback.md`.
    rows = audit.required_collections(ROOT)
    collections = sorted({r.split("/")[0] + "/" if "/" in r else r for r in rows})
    grow_text = (ROOT / "protocols" / "grow.md").read_text(encoding="utf-8")
    shape = grow_text.split("## Unified knowledge shape", 1)[-1].split("```", 2)
    shape_block = shape[1] if len(shape) > 2 else ""
    phase4 = grow_text.split("## Phase 4", 1)[-1].split("## Phase 5", 1)[0]
    for c in collections:
        if c not in shape_block:
            fail(f"protocols/grow.md: the unified-shape diagram omits {c!r}, "
                 f"which install.sh creates in every plant")
        # Phase 4 names a collection in whatever form its instruction takes:
        # its own bullet (`design/`), a shared one (`prompts/` and
        # `evaluations/`), a specific leaf (`plans/grill.md`), or a sentence
        # (the `specs/` index). Requiring a bullet each would fail three
        # collections that ARE instructed, so the rule is a backticked mention
        # here — with the shape diagram above as the strict arm, since a
        # collection deleted from the seed's shape is the failure that matters.
        if f"`{c}" not in phase4:
            fail(f"protocols/grow.md: Phase 4 never tells an author to write "
                 f"{c!r}, so no plant ever grows it")
    # The intake arm. A collection with no section in the evidence-ledger
    # schema is a collection no scout ever gathers evidence for, which is
    # exactly how design/ and legal/ stayed empty from 6.9.0 to 7.2.1 while
    # their agents shipped in every plant: the shape and the phases can name a
    # collection an author is told to write, and the author still has nothing
    # to write it from. Four collections are legitimately not scouted — they
    # are outputs of the growth run rather than findings about the source:
    #   sources/     provenance of the external pass, written as it retrieves
    #   tools/       withdrawn from tool-corpus / authored from §10 operations
    #   plans/       the growth's own plan of record
    #   changelog.md the growth's own provenance entry
    UNSCOUTED = {"sources/", "tools/", "plans/", "changelog.md"}
    ledger = (ROOT / "templates" / "prompts" / "growth-evidence-ledger.md"
              ).read_text(encoding="utf-8")
    headings = "\n".join(l for l in ledger.splitlines() if l.startswith("## "))
    for c in collections:
        if c in UNSCOUTED:
            continue
        if c not in headings:
            fail(f"templates/prompts/growth-evidence-ledger.md: no section "
                 f"feeds {c!r}, so no scout gathers the evidence an author "
                 f"would write it from")

    # -- the node contract and its linter are two views of ONE fact ---------
    # `_schema.md` is what an author reads; `graph-lint.py` is what holds them
    # to it. When 7.5.0 added the `expertise` kind and the `composes` edge, the
    # failure to guard against was shipping one without the other: a kind the
    # linter accepts and the contract never describes is a shape nobody knows
    # how to author, and an edge the contract promises and the linter ignores
    # is a rule that is not one. Both directions, so neither side can drift.
    engine = load_tool("templates/knowledge-graph/graph-lint.py")
    schema = (ROOT / "templates" / "knowledge-graph" / "_schema.md").read_text(
        encoding="utf-8")
    for key in sorted(engine.LIST_KEYS):
        if f"`{key}`" not in schema:
            fail(f"templates/knowledge-graph/_schema.md: never describes the "
                 f"{key!r} key, which graph-lint.py parses and enforces")
    # The kinds list in the schema's "### Node kinds" section, read the way a
    # reader reads it: the backticked first token of each bullet.
    section = schema.split("### Node kinds", 1)[-1].split("\n## ", 1)[0]
    documented = set(re.findall(r"^-\s+`([a-z]+)`", section, re.M))
    reserved = set(engine.MACHINERY_KINDS)
    for kind in sorted(engine.KINDS - documented - reserved - {"root"}):
        fail(f"templates/knowledge-graph/_schema.md: graph-lint.py accepts "
             f"kind {kind!r} and the contract never describes it")
    for kind in sorted(documented - engine.KINDS):
        fail(f"templates/knowledge-graph/graph-lint.py: _schema.md describes "
             f"kind {kind!r} and KINDS does not accept it")

    # The record's schema documents the inventory kinds and what each owes the
    # graph; the tool enforces them. Two homes for one fact, so keep them
    # honest — a kind the tool plans for that the schema never describes is a
    # rule an orchestrator cannot follow.
    record_doc = (ROOT / "templates" / "prompts" / "growth-coverage-record.md"
                  ).read_text(encoding="utf-8")
    for kind in audit.KIND_PLAN:
        if f"`{kind}`" not in record_doc:
            fail(f"templates/prompts/growth-coverage-record.md: inventory kind "
                 f"{kind!r} is planned by tools/growth-audit.py but never "
                 f"described here")
    # The table's "expertise node" column is the same fact as KIND_PLAN's third
    # element, written for a reader. Checking only that the kind is MENTIONED
    # let the column drift from the tool silently, which is how an orchestrator
    # ends up planning an artifact the gate does not want, or omitting one it
    # does. Each row is read where it is declared.
    for line in record_doc.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4 or not cells[0].startswith("`"):
            continue
        if "incidental" in cells[0]:
            continue        # a significance sub-case, not the kind's own rule
        kinds = re.findall(r"`([a-z-]+)`", cells[0])
        documented = not cells[2].lower().startswith("no")
        for kind in kinds:
            if kind in audit.KIND_PLAN and audit.KIND_PLAN[kind][2] != documented:
                fail(f"templates/prompts/growth-coverage-record.md: the kind "
                     f"table says {kind!r} "
                     f"{'owes' if documented else 'does not owe'} an expertise "
                     f"node; tools/growth-audit.py plans the opposite")

    # The verdict vocabularies have one home each, and the protocols quote from
    # them for their own readers. A protocol naming a verdict no tool can emit
    # promises a check that does not exist — the same class of lie as a gate
    # that asserts nothing.
    #
    # Scoped PER TOOL, and that scoping is the whole correctness of this check.
    # It once held both protocols to growth-audit's vocabulary alone, so
    # `protocols/graft.md` could not name `GENERATED` or `UNMAPPED` — which are
    # graft-audit's own classifications, for the audit graft actually runs. The
    # effect was not a caught defect: the author described the classification in
    # words rather than naming it, so the check bent the prose it was meant to
    # keep honest. A vocabulary check that spans tools is a vocabulary check
    # that is wrong about which tool is speaking.
    graft_audit_verdicts = _classification_names(ROOT / "tools" / "graft-audit.py")
    growth_verdicts = set(audit.VERDICTS) | set(audit.STATUSES)
    vocab = {
        "protocols/grow.md": growth_verdicts | {"KINDS"},
        # graft runs BOTH audits: growth-audit for the coverage gate, and
        # graft-audit for backups, kernel, engine, schema and scaffolds.
        "protocols/graft.md": growth_verdicts | graft_audit_verdicts | {"KINDS"},
    }
    for proto, known in vocab.items():
        path = ROOT / proto
        if not path.is_file():
            # A missing protocol used to raise FileNotFoundError here, which
            # aborts the whole run: every finding already collected goes
            # unprinted, and the operator sees a traceback instead of the reason.
            # A linter that crashes on the tree it is linting reports nothing
            # about the tree.
            fail(f"{proto} is missing — a protocol the seed's own checks name "
                 f"cannot be absent")
            continue
        text = path.read_text(encoding="utf-8")
        for tok in sorted(set(re.findall(r"`([A-Z][A-Z-]{3,})`", text))):
            if tok not in known:
                fail(f"{proto}: names `{tok}`, which no audit tool emits — a "
                     f"promised check that does not exist")

    # An expert growth authors is only spawnable once it is PROJECTED into the
    # harness directory the host reads its roster from. That mapping has ONE
    # home — `agent_projection_for` in install.sh, recorded into each plant's
    # stamp — and the audit reads it from the stamp rather than keeping a copy.
    # What can still rot is an adapter the installer accepts and forgets to map:
    # its plants would carry experts nothing ever checks are spawnable.
    install = (ROOT / "install.sh").read_text(encoding="utf-8")
    accepted = re.search(r"^\s*([a-z|-]*claude-code[a-z|-]*)\)\s*TOOLS\+=",
                         install, re.M)
    if not accepted:
        fail("install.sh: cannot find the adapter list it accepts on the "
             "command line; the projection-mapping check cannot run")
    else:
        mapped = re.search(r"agent_projection_for\(\)\s*\{(.*?)\n\}",
                           install, re.S)
        body = mapped.group(1) if mapped else ""
        for adapter in accepted.group(1).split("|"):
            if adapter == "all":
                continue
            if not re.search(rf"^\s*{re.escape(adapter)}\)", body, re.M):
                fail(f"install.sh: accepts the {adapter!r} adapter but "
                     f"agent_projection_for maps no agent directory for it, so "
                     f"a plant installed with it would never be checked for a "
                     f"spawnable expert")

    # The template a plant authors an expert FROM has to be able to satisfy the
    # gate that expert will be held to. Without `origin: project` a graft cannot
    # tell the plant's own work from seed machinery; without `plant_knowledge:`
    # the one agent written for this project's surface is the only one exempt
    # from the check that asks whether it has anything to read.
    # Two artifact classes are authored from a form that lives nowhere near
    # them, so the form is the only thing that can carry the keys the gate will
    # ask its offspring for. Line-anchored: a header comment EXPLAINS these
    # keys in prose, and a substring test would be satisfied by the explanation
    # while the frontmatter that has to carry them stayed empty.
    for rel, keys in (
        ("templates/agent.template.md",
         (r"origin: project", r"plant_knowledge:", r"id: agent\.", r"kind: agent")),
        # An expertise node owes the same answerability: `libraries:` is the
        # edge to its pin home, `composes:` the menu the router descends, and
        # without them the node routes to nothing.
        ("templates/docs/nodes/_expertise.template.md",
         (r"id: expertise\.", r"kind: expertise", r"origin: project",
          r"composes:", r"libraries:")),
    ):
        # The FRONTMATTER only. A template's worked example carries the same
        # keys at column 0, so matching the whole file let an emptied
        # frontmatter pass on the strength of the example that merely shows
        # what it should have said. Line-anchoring alone was not enough; the
        # anchor has to be scoped to the block that has to carry the keys.
        # A template may open with an HTML header comment, so the block is
        # found rather than assumed to start the file.
        head = frontmatter_block(ROOT / rel)
        for key in keys:
            if not re.search(rf"^{key}", head, re.M):
                fail(f"{rel}: its frontmatter carries no {key!r}, so a node "
                     f"authored from it cannot answer the coverage gate")

    # The staffing decision has two homes — the tool that requires it and the
    # schema an orchestrator fills — so keep them honest.
    for token in ("**experts**", "warranted", "motivated_by", "needs"):
        if token not in record_doc:
            fail(f"templates/prompts/growth-coverage-record.md: never "
                 f"describes {token!r}, which tools/growth-audit.py requires")
    for kind in audit.STAFFED_KINDS:
        if f"`{kind}`" not in record_doc:
            fail(f"templates/prompts/growth-coverage-record.md: {kind!r} must "
                 f"answer the staffing question and the schema never says so")

    # Every collection an agent declares it must read has to be one the seed
    # actually installs — a typo here would make an agent row permanently
    # uncoverable, and the audit would blame the plant for the seed's mistake.
    for name, meta in agents.items():
        for want in meta["fm"].get("plant_knowledge", []) or []:
            if want not in collections and want not in rows and not (tdocs / want).is_file():
                fail(f"agents/: {name} declares plant_knowledge {want!r}, "
                     f"which is not a collection the seed installs")

    # -- corpus agnosticism + cross-reference scan (mechanical floor) ----
    # Catches the OBJECTIVE plant-identifier leak class the harvest
    # agnosticism gate promises — a real host IP, a pinned CVE, an absolute
    # operator home path, a dangling corpus/template link — over the
    # seed's shipped prose. Subtler
    # fingerprints (a project name, a stack combo) remain human judgment:
    # the seed cannot hardcode plant names to blocklist without itself
    # leaking them — which is why the shared tool takes them as --forbid
    # and the seed passes none. Loopback/unspecified/doc IPs are allowed.
    agn_roots = ("core", "agents", "protocols", "skills", "templates",
                 "library-corpus", "legal-corpus", "tool-corpus",
                 "agent-corpus", "skill-corpus")
    scan = [ROOT / r for r in agn_roots]
    scan += [ROOT / f for f in ("manifest.json", "README.md", "CHANGELOG.md")
             if (ROOT / f).exists()]
    agn = load_agnosticism_lint()
    # The agnosticism scan reaches BEYOND the corpus roots above, to the trees
    # and file types where an operator leak actually lands: the dev-plans, the
    # tooling, the installer and the top-level docs, and *.py/*.sh there as well
    # as *.md. A hardcoded path in a script or a scratch note in a plan is
    # exactly the leak the *.md-only corpus scan never looked at. tests/ stays
    # OUT — its own deliberate violation fixtures live there. The
    # dangling-reference arm below keeps its own narrower *.md corpus walk: it is
    # link integrity, not agnosticism, and its scope is unchanged.
    agn_scan = list(scan)
    agn_scan += [ROOT / r for r in ("docs/plans", "tools") if (ROOT / r).is_dir()]
    agn_scan += [ROOT / f for f in ("install.sh", "DOCUMENTATION.md", "INSTALL.md")
                 if (ROOT / f).exists()]
    for finding in agn.scan(agn_scan, globs=("*.md", "*.py", "*.sh"),
                            relative_to=ROOT):
        fail(f"{finding.path}: {finding.message}")
    # The dangling-reference arm is link integrity, not agnosticism, so it
    # stays here — but it walks the same file set, through the same iterator.
    ref_re = re.compile(r"\b(?:library-corpus|legal-corpus|tool-corpus|"
                        r"agent-corpus|skill-corpus|templates)/[A-Za-z0-9_./-]+\.md\b")
    for p in agn.iter_files(scan):
        rel = p.relative_to(ROOT)
        # CHANGELOG.md is append-only history: it names files as they stood
        # when the entry was written, so a later rename necessarily leaves a
        # reference behind that no longer resolves. Rewriting the entry to fix
        # the link would falsify the record ("supersede, don't rewrite"), and
        # keeping a tombstone under templates/ would ship a dead file into
        # every plant. Link integrity is a claim about live pointers; a dated
        # record's pointers are not live. The agnosticism arm above still
        # scans it — a leaked host IP is wrong in history too.
        if rel.as_posix() == "CHANGELOG.md":
            continue
        for ref in ref_re.findall(p.read_text(encoding="utf-8")):
            if "<" in ref or "*" in ref or "{" in ref:
                continue
            if not (ROOT / ref).exists():
                fail(f"{rel}: dangling corpus/template reference '{ref}'")


# --- SPEC-0004: the front door ------------------------------------------------
# README.md, DOCUMENTATION.md (its glossary and enforcement regions), the
# references in documentation/, INSTALL.md and each integrations/*/README.md are
# read by one parser and held by one check_fd_* per SPEC-0004 §4 contract. Every
# finding goes through fd_fail, which reports it or, while its slug is in
# FRONT_DOOR_PENDING, holds it for that slug's PENDING line; every check runs
# inside fd_guard, so a check that raises is reported and fails the run instead
# of taking the other checks down with it. The §6 data shapes below are the
# spec's, restated only as far as code has to hold them.

FD_LEDGER_SLUG = "PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS"
FD_README_HEADINGS = (
    "## What CYPRESS is",
    "## Who it is for and not for",
    "## What installing does to your repository",
    "## What it costs",
    "## Try it",
    "## How it works",
    "## Why it is built this way",
    "## What it does not do",
    "## Where to go next",
)
FD_INSTALL_SECTION = FD_README_HEADINGS[2]
FD_COST_SECTION = FD_README_HEADINGS[3]
FD_TRY_SECTION = FD_README_HEADINGS[4]
FD_LIMITS_SECTION = FD_README_HEADINGS[7]
FD_WHERE_SECTION = FD_README_HEADINGS[8]
FD_RETIRED_HEADING = "## What you get"
FD_CAPS = (("FIRST_HEADING_MAX_LINE", "FIRST_HEADING_CAP"),
           ("FIRST_SCREEN_MAX_LINES", "FIRST_SCREEN_CAP"),
           ("FIRST_COMMAND_LINE", "FIRST_COMMAND_CAP"))
FD_INSTALL_TARGETS = ("CLAUDE.md", "AGENTS.md", ".claude/", "docs/graph/", ".cypress/seed.json")
FD_BACKUP_ROW = "enf-backup-before-replace"
FD_SEED_SOURCE_PREFIXES = ("core/", "agents/", "skills/", "integrations/", "protocols/",
                           "templates/", "tools/", "tests/")
FD_WHERE_NEXT = ("DOCUMENTATION.md", "DOCUMENTATION.md#glossary", "DOCUMENTATION.md#enforcement",
                 "documentation/agents-reference.md", "documentation/protocols-reference.md",
                 "documentation/skills-and-templates-reference.md",
                 "documentation/host-capability-matrix.md", "docs/decisions/index.md", "INSTALL.md")

FD_GLOSSARY_HEADING = "## 15. Glossary"
FD_ENFORCEMENT_HEADING = "## 17. What is enforced, and how"
FD_FIELDS = ("Forms", "Here", "Field", "Implemented at", "Enforcement", "Divergence", "Why")
FD_CLASS_ORDER = ("hard", "soft", "detective", "judgment", "not a control")  # strongest first
FD_NOT_A_CONTROL = FD_CLASS_ORDER[-1]
FD_DIVERGENCES = ("same", "narrower", "broader", "different", "no standard meaning")
FD_WHY = re.compile(r"\bADR-\d{4}\b|\bSPEC-\d{4}\b|docs/plans/\S+|`[0-9a-f]{7,40}`"
                    r"|\S+\.[a-z]{1,4}:\d+|kernel §\d+(\.\d+)?|^not recorded$")
FD_REQUIRED_TERMS = {
    "agent": "term-agent", "subagent": "term-subagent", "orchestrator": "term-orchestrator",
    "workflow": "term-workflow", "skill": "term-skill", "tool": "term-tool", "hook": "term-hook",
    "kernel": "term-kernel", "context window": "term-context-window",
    "progressive disclosure": "term-progressive-disclosure",
    "knowledge graph": "term-knowledge-graph", "node": "term-node", "router": "term-router",
    "routing": "term-routing", "specification": "term-specification",
    "test-first development": "term-test-first", "gate": "term-gate", "linter": "term-linter",
    "harness": "term-harness", "seed": "term-seed", "plant": "term-plant", "growth": "term-growth",
    "graft": "term-graft", "harvest": "term-harvest", "canonize": "term-canonize",
    "tier": "term-tier", "protocol": "term-protocol", "corpus": "term-corpus",
    "handback": "term-handback", "coordinator": "term-coordinator", "leaf": "term-leaf",
    "specialist": "term-specialist", "expert": "term-expert", "steward": "term-steward",
    "one home per fact": "term-one-home-per-fact", "turn": "term-turn",
    "toolcraft": "term-toolcraft", "machinery": "term-machinery", "brief": "term-brief",
    "reverse loop": "term-reverse-loop",
}
FD_REQUIRED_ROWS = (
    "enf-kernel-load", "enf-kernel-budget", "enf-tool-allowlist", "enf-leaf-cannot-spawn",
    "enf-delegation-frontmatter", "enf-route-hook", "enf-status-hook", "enf-pre-bash-guard",
    "enf-injection-dedup", "enf-backup-before-replace", "enf-plant-files-kept",
    "enf-install-preflight", "enf-install-stamp", "enf-registration-notice", "enf-graph-lint",
    "enf-spec-lint", "enf-grill-lint", "enf-agent-lint", "enf-prose-lint",
    "enf-agnosticism-lint", "enf-status-register", "enf-growth-audit", "enf-graft-audit",
    "enf-tier-classification", "enf-protocol-order", "enf-spec-before-code",
    "enf-test-before-code", "enf-verify-gates", "enf-canonize", "enf-attribution",
    "enf-brief-block", "enf-charter-duties", "enf-lifecycle-gate-rows", "enf-steward-only",
    "enf-seed-gate", "enf-ratchets",
)
# Row-specific residuals security named (§6): each What it can miss pattern with
# the words a finding shows, and the class rule the row's Class cell meets.
FD_PRE_BASH_HARD = "**hard** for a matched command on a host that fires the hook"
FD_ROW_RESIDUALS = {
    "enf-tool-allowlist": ([(r"\bBash\b", "Bash"), (r"role emulation", "role emulation"),
                            (r"`?tools:`?", "an omitted `tools:` line")], "not-hard"),
    "enf-leaf-cannot-spawn": ([(r"spawn[- ]tool", "another name for the spawn tool"),
                               (r"role emulation", "role emulation"),
                               (r"`?tools:`?", "an omitted `tools:` line")], "not-hard"),
    "enf-pre-bash-guard": ([(r"fails? open", "fails open"),
                            (r"(indirection|evasion|evade)", "indirection or evasion"),
                            (r"\bhosts?\b", "hosts")], "not-hard-scoped"),
    "enf-backup-before-replace": ([(r"`?\.cypress/seed\.json`?", ".cypress/seed.json")], None),
    "enf-route-hook": ([], "not-a-control"),
    "enf-status-hook": ([], "not-a-control"),
}
FD_MATRIX = "documentation/host-capability-matrix.md"
FD_REFERENCE_OPENERS = (
    ("documentation/agents-reference.md", r"^An agent is\b", "An agent is",
     "../DOCUMENTATION.md#term-skill"),
    ("documentation/skills-and-templates-reference.md", r"^A skill is\b", "A skill is",
     "../DOCUMENTATION.md#term-skill"),
    ("documentation/protocols-reference.md", r"^A protocol( node)? is\b", "A protocol is",
     "../DOCUMENTATION.md#term-protocol"),
)
FD_MECHANISM_VERB = re.compile(
    r"(?i)\b(enforc\w*|ensur\w*|prevent\w*|requir\w*|block\w*|guarantee\w*|gates?|gated"
    r"|gating|refus\w*|reject\w*|forbid\w*|guard\w*|stops?|cannot|can't|never|hard"
    r"|prove[ns]?|proven)\b")
FD_STRONG_CLAIM = re.compile(
    r"(?i)\b(hard|cannot|can't|guarantee\w*|ensur\w*|prevent\w*|block\w*|refus\w*|stops?)\b")
FD_NEGATORS = frozenset({"not", "no", "nothing", "none", "never", "without"})
FD_GUARD_MISNOMER = re.compile(r"(?i)\b(secur\w*|sandbox\w*|protect\w*)\b")
FD_PRE_BASH_ROW = "enf-pre-bash-guard"
FD_ADR_RANGE = re.compile(r"(?i)\badr-?\d{4}\s*(?:\.\.|–|—|to|through)\s*(?:adr-?)?\d{4}\b")
_FD_NUM = r"\d{1,3}(?:[    ,]\d{3})+|\d+(?:\.\d+)?"
FD_FIGURE = re.compile(rf"(?<![\w.])({_FD_NUM})(?:\s*(?:to|–|-)\s*({_FD_NUM}))?"
                       r"\s*-?\s*(bytes?\b|B\b|KB\b|KiB\b|tokens?\b|%)")
FD_LINE_FIGURE = re.compile(r"(?<![\w.])\d[\d    ,]*\s*-?\s*lines?\b")
FD_MEASUR_WORD = re.compile(r"(?i)(?<!\bnot )(?<!\bnot yet )(?<!\bnever )"
                            r"\bmeasur(?:ed|es|ing|ement|ements|e)?\b")
FD_MEASURED_CLAIM = re.compile(r"(?i)measured (?:once|\d{4}-\d{2}-\d{2})")
FD_SCOPE_MARKERS = ("per session", "per task", "per prompt", "per spawn", "one-time",
                    "Claude Code", "Prime Agent", "opencode", "Codex", "GitHub Copilot",
                    "budget", "ceiling")
FD_LIMIT_WORDS = re.compile(r"(?i)\b(budget|ceiling|limit)\b")
FD_UNMEASURED_PHRASES = ("not recorded", "not measured", "measured once")
FD_LIMITS_SUBSECTIONS = ("### Requested, not enforced", "### Not yet measured")
FD_LIMITS_REQUIRED_ROWS = ("enf-tier-classification", "enf-spec-before-code",
                           "enf-test-before-code")
FD_GENERIC_LINK_TEXTS = frozenset({"here", "this", "link", "click here", "this link",
                                   "read more", "more"})
FD_STOPWORDS = frozenset("""
a an the and or of to in on for by with as at from is are was were be been it its
this that these those which who whose not no but if then so than into per each
every any one""".split())

FD_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FD_ATX = re.compile(r"^(#{1,6})(?:\s|$)")
FD_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FD_TABLE_SEP = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
FD_ANCHOR_TAG = re.compile(r'<a id="([^"]*)"></a>')
FD_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
FD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^()\s]*)\)")
FD_BOLD = re.compile(r"\*\*(.+?)\*\*")
FD_FIELD_LINE = re.compile(r"^- \*\*([^*]+?):\*\*\s?(.*)$")
FD_SENTENCE_END = re.compile(r"[.!?](?=\s+[A-Z\[`*(])")
FD_NO_SPLIT_AFTER = ("e.g.", "i.e.", "etc.", "vs.")

_fd_texts: dict = {}
_fd_docs: dict = {}
_fd_ran: list = []
_fd_raised: set = set()
_fd_observed: dict = {}
_fd_held: dict = {}


def fd_fail(slug: str, path: str, line: int, message: str, pendable: bool = True) -> None:
    """The one reporting path for SPEC-0004. A finding is enforced unless its
    slug is in FRONT_DOOR_PENDING, when it is held for that slug's PENDING line.
    The ledger's own slug is never held, nor is a finding its contract says the
    ledger may not hold (`pendable=False`).

    The assertions are the fd_fail() sites inside the check_fd_* functions,
    plus ten required-input findings raised from the fd_* helpers (fd_text,
    fd_rows, fd_glossary, fd_section, fd_link_scopes) when an input the
    contracts read is missing or unshaped. It appends to `findings` rather
    than calling fail() because the coverage binder counts fail() sites
    outside named checks as inline assertion debt, and a reporting path is not
    an assertion. The binder does not count fd_fail() sites at all (grill
    §12)."""
    text = f"{path}:{line}: {message}"
    _fd_observed.setdefault(slug, []).append(text)
    if pendable and slug in FRONT_DOOR_PENDING and slug != FD_LEDGER_SLUG:
        _fd_held.setdefault(slug, []).append(text)
    else:
        findings.append(f"front-door: {slug}: {text}")


@contextlib.contextmanager
def fd_guard(slug: str):
    """Run one front-door check. An exception is reported as
    `front-door: <SLUG>: RAISED <type>: <message>` and fails the run whether or
    not the slug is pending, because a check that could not run observed
    nothing; the ledger then counts the slug as neither stale nor failing."""
    _fd_ran.append(slug)
    _fd_observed.setdefault(slug, [])
    try:
        yield
    except Exception as e:                       # noqa: BLE001 — reported, never swallowed
        _fd_raised.add(slug)
        findings.append(f"front-door: {slug}: RAISED {type(e).__name__}: {e}")


def fd_text(slug: str, rel: str, what: str = "") -> str | None:
    """A front-door input's text, or None after a line-0 finding under `slug`
    naming why it could not be read. Absence and undecodable bytes are
    findings, never a skip."""
    if rel not in _fd_texts:
        path = ROOT / rel
        try:
            _fd_texts[rel] = ("ok", path.read_bytes().decode("utf-8"))
        except FileNotFoundError:
            _fd_texts[rel] = ("missing", None)
        except UnicodeDecodeError as e:
            _fd_texts[rel] = ("utf8", f"{e.reason} at byte {e.start}")
        except OSError as e:
            _fd_texts[rel] = ("oserror", f"{type(e).__name__}: {e}")
    state, value = _fd_texts[rel]
    if state == "ok":
        return value
    if state == "missing":
        fd_fail(slug, rel, 0, f"missing required input: {what or rel} does not exist")
    elif state == "utf8":
        fd_fail(slug, rel, 0, f"cannot be read as UTF-8 ({value}); an unreadable "
                              f"input is a finding, never a skip")
    else:
        fd_fail(slug, rel, 0, f"cannot be read ({value})")
    return None


def fd_doc(slug: str, rel: str, what: str = ""):
    """(lines, kinds) for a front-door file: kinds marks each line `body`,
    `blank`, `fence`, `heading`, `comment` or `anchor` (SPEC-0004 §6 body
    text). None after fd_text's finding."""
    text = fd_text(slug, rel, what)
    if text is None:
        return None
    if rel not in _fd_docs:
        lines = text.splitlines()
        kinds, fence, comment = [], None, False
        for line in lines:
            stripped = line.strip()
            if fence:
                kinds.append("fence")
                m = FD_FENCE.match(line)
                if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                        and not m.group(2).strip():
                    fence = None
            elif FD_FENCE.match(line):
                fence = FD_FENCE.match(line).group(1)
                kinds.append("fence")
            elif comment or stripped.startswith("<!--"):
                kinds.append("comment")
                comment = "-->" not in stripped
            elif FD_ANCHOR_TAG.fullmatch(stripped):
                kinds.append("anchor")
            elif FD_ATX.match(line):
                kinds.append("heading")
            else:
                kinds.append("body" if stripped else "blank")
        _fd_docs[rel] = (lines, kinds)
    return _fd_docs[rel]


def fd_units(doc, lo: int = 0, hi: int | None = None) -> list:
    """[(line, text)] of body text between line indexes lo and hi: a paragraph
    runs over non-blank body lines; a list item and a table row each start
    their own unit, and a table's delimiter row is none."""
    lines, kinds = doc
    hi = len(lines) if hi is None else hi
    units, cur, cur_row = [], None, False
    for i in range(lo, hi):
        if kinds[i] != "body":
            cur = None
            continue
        line = lines[i]
        row = line.lstrip().startswith("|")
        if row and FD_TABLE_SEP.match(line.strip()):
            cur = None
            continue
        if cur is None or row or cur_row or FD_LIST_ITEM.match(line):
            cur = [i + 1, [line]]
            units.append(cur)
        else:
            cur[1].append(line)
        cur_row = row
    return [(n, "\n".join(ls)) for n, ls in units]


def fd_code_spans(text: str) -> list:
    return [(m.start(), m.end(), m.group(2)) for m in FD_CODE_SPAN.finditer(text)]


def fd_links(text: str) -> list:
    """[(text, target, start, end, text_start, text_end)] for every inline link
    outside a code span. Reference-style links are not links here."""
    spans = fd_code_spans(text)
    out = []
    for m in FD_LINK.finditer(text):
        if any(a <= m.start() < b for a, b, _c in spans):
            continue
        out.append((m.group(1), m.group(2), m.start(), m.end(), m.start(1), m.end(1)))
    return out


def fd_mask(text: str) -> str:
    """Code spans, link targets and anchor tags blanked, positions kept."""
    chars = list(text)

    def blank(a, b):
        for k in range(a, b):
            if chars[k] != "\n":
                chars[k] = " "
    for a, b, _c in fd_code_spans(text):
        blank(a, b)
    for _t, _g, _a, end, _ts, text_end in fd_links(text):
        blank(text_end + 1, end)
    for m in FD_ANCHOR_TAG.finditer(text):
        blank(m.start(), m.end())
    return "".join(chars)


def fd_line_of(unit_line: int, text: str, pos: int) -> int:
    return unit_line + text.count("\n", 0, pos)


def fd_resolve(from_rel: str, target: str):
    """(file relative to the seed root, fragment) a link target names, or None
    for an external link. An empty path is the linking file itself."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
        return None
    path, _, frag = target.partition("#")
    if not path:
        return from_rel, frag
    base = pathlib.PurePosixPath(from_rel).parent
    parts = []
    for part in (base / path).parts:
        if part == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            else:
                parts.append(part)
        elif part != ".":
            parts.append(part)
    return "/".join(parts), frag


def fd_row_links(from_rel: str, text: str) -> list:
    """The `enf-` row ids a unit links, in order."""
    ids = []
    for _t, target, *_r in fd_links(text):
        hit = fd_resolve(from_rel, target)
        if hit and hit[0] == "DOCUMENTATION.md" and hit[1].startswith("enf-"):
            ids.append(hit[1])
    return ids


def fd_region(doc, heading: str):
    """(first, end) line indexes of the region from `heading` to the next `##`."""
    lines, kinds = doc
    at = [i for i, line in enumerate(lines) if line.rstrip() == heading and kinds[i] == "heading"]
    if not at:
        return None
    end = next((j for j in range(at[0] + 1, len(lines))
                if kinds[j] == "heading" and lines[j].startswith("## ")), len(lines))
    return at[0], end


def fd_headings(doc) -> list:
    """[(line, level, line text)] of ATX headings outside fenced blocks."""
    lines, kinds = doc
    return [(i + 1, len(FD_ATX.match(line).group(1)), line.rstrip())
            for i, line in enumerate(lines) if kinds[i] == "heading"]


def fd_anchors(doc) -> dict:
    """{id: [lines]} of the explicit anchors outside fenced blocks."""
    lines, kinds = doc
    out: dict = {}
    for i, line in enumerate(lines):
        if kinds[i] != "fence":
            for m in FD_ANCHOR_TAG.finditer(line):
                out.setdefault(m.group(1), []).append(i + 1)
    return out


def fd_cells(line: str) -> list:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def fd_tables(doc, lo: int = 0, hi: int | None = None) -> list:
    """[(header line, header cells, [(line, cells)])] per table: consecutive
    lines beginning `|` whose second line is a delimiter row."""
    lines, kinds = doc
    hi = len(lines) if hi is None else hi
    tables, i = [], lo
    while i < hi:
        if kinds[i] == "body" and lines[i].lstrip().startswith("|"):
            j = i
            while j < hi and kinds[j] == "body" and lines[j].lstrip().startswith("|"):
                j += 1
            if j - i >= 2 and FD_TABLE_SEP.match(lines[i + 1].strip()):
                tables.append((i + 1, fd_cells(lines[i]),
                               [(k + 1, fd_cells(lines[k])) for k in range(i + 2, j)]))
            i = j
        else:
            i += 1
    return tables


def fd_bold(text: str) -> list:
    return [b.strip() for b in FD_BOLD.findall(text)]


def fd_weakest(classes) -> str | None:
    ranked = [c for c in classes if c in FD_CLASS_ORDER]
    return max(ranked, key=FD_CLASS_ORDER.index) if ranked else None


def fd_strip_markup(text: str) -> str:
    return re.sub(r"[*_`]", "", text).strip()


def fd_path_like(token: str) -> bool:
    bare = re.sub(r":\d+(?:-\d+)?$", "", token)
    return "/" in bare or bare.endswith((".md", ".py", ".sh", ".json", ".ts", ".tsv",
                                         ".yml", ".toml"))


def fd_seed_path_problem(token: str) -> str | None:
    """Why a seed path does not resolve under the seed root (§6 seed-path
    rule), or None: `<...>` reads as `*`, one level of `{a,b}` is expanded,
    and a `:N` or `:N-M` suffix must lie within the file."""
    m = re.match(r"^(.*?)(?::(\d+)(?:-(\d+))?)?$", token)
    path, lo, hi = m.group(1), m.group(2), m.group(3)
    pattern = re.sub(r"<[^>]*>", "*", path).strip("/") or "."
    brace = re.search(r"\{([^{}]*)\}", pattern)
    expansions = ([pattern[:brace.start()] + alt + pattern[brace.end():]
                   for alt in brace.group(1).split(",")] if brace else [pattern])
    for exp in expansions:
        hits = sorted(ROOT.glob(exp)) if any(c in exp for c in "*?[") else (
            [ROOT / exp] if (ROOT / exp).exists() else [])
        if not hits:
            return f"`{token}` does not resolve under the seed root"
        if lo is not None:
            if not hits[0].is_file():
                return f"`{token}` names lines of something that is not a file"
            count = len(hits[0].read_text(encoding="utf-8", errors="replace").splitlines())
            n, top = int(lo), int(hi or lo)
            if not (n <= top <= count):
                return f"`{token}` names lines outside the file ({count} lines)"
    return None


def fd_install_literal_problem(token: str, install: str) -> str | None:
    """Why a target path is not the installer's (§6 install-literal rule)."""
    prefix = re.split(r"[<*{]", token, maxsplit=1)[0]
    prefix = prefix[2:] if prefix.startswith("./") else prefix
    if len(prefix) < 4:
        return f"`{token}` has a literal prefix shorter than 4 characters"
    if prefix not in install:
        return f"`{token}` does not occur in install.sh"
    return None


def fd_sentences(text: str) -> list:
    """[(start, sentence)] split at [.!?] + whitespace + [A-Z [ ` * (]."""
    out, start = [], 0
    for m in FD_SENTENCE_END.finditer(text):
        if text[:m.end()].endswith(FD_NO_SPLIT_AFTER):
            continue
        out.append((start, text[start:m.end()].strip()))
        start = m.end()
    tail = text[start:].strip()
    if tail:
        out.append((start, tail))
    return out


def fd_front_door_files() -> list:
    """SPEC-0004 §2: README.md, DOCUMENTATION.md, documentation/*.md,
    INSTALL.md and integrations/*/README.md."""
    rels = ["README.md", "DOCUMENTATION.md"]
    rels += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "documentation").glob("*.md"))
    rels += ["INSTALL.md"]
    rels += sorted(p.relative_to(ROOT).as_posix()
                   for p in (ROOT / "integrations").glob("*/README.md"))
    return rels


def fd_section(slug: str, doc, heading: str):
    """A README section's (first, end) line indexes, or None after a line-0
    finding naming the heading."""
    region = fd_region(doc, heading)
    if region is None:
        fd_fail(slug, "README.md", 0, f"missing required input: no section `{heading}`")
    return region


def fd_glossary(slug: str):
    """(DOCUMENTATION doc, region, entries) with a line-0 finding when the
    region is missing or parses to no entries; None when DOCUMENTATION.md
    cannot be read. Each entry is a dict: head, line, anchor (id, line) or
    None, fields [(label, value, line)], and the derived id, forms, field()."""
    doc = fd_doc(slug, "DOCUMENTATION.md")
    if doc is None:
        return None
    lines, kinds = doc
    region = fd_region(doc, FD_GLOSSARY_HEADING)
    if region is None:
        fd_fail(slug, "DOCUMENTATION.md", 0,
                f"missing required input: no glossary region `{FD_GLOSSARY_HEADING}`")
        return doc, None, []
    entries, cur, field = [], None, None
    for i in range(region[0] + 1, region[1]):
        line = lines[i]
        if kinds[i] == "heading" and line.startswith("### "):
            cur = {"head": line[4:].strip(), "line": i + 1, "anchor": None,
                   "anchor_next": False, "fields": []}
            entries.append(cur)
            field = None
            continue
        if cur is None or kinds[i] == "fence":
            continue
        m = FD_ANCHOR_TAG.fullmatch(line.strip())
        if m and cur["anchor"] is None and not cur["fields"]:
            cur["anchor"] = (m.group(1), i + 1)
            cur["anchor_next"] = i == cur["line"]
            continue
        m = FD_FIELD_LINE.match(line)
        if m:
            field = [m.group(1).strip(), m.group(2).strip(), i + 1]
            cur["fields"].append(field)
        elif field is not None and line[:1] in (" ", "\t") and line.strip():
            field[1] = (field[1] + " " + line.strip()).strip()   # an indented continuation
        elif line.strip():
            field = None
    for e in entries:
        e["id"] = e["anchor"][0] if e["anchor"] else None
        values = {}
        for label, value, n in e["fields"]:
            values.setdefault(label, (value, n))
        e["values"] = values
        forms = values.get("Forms", ("", 0))[0]
        e["forms"] = [f.strip() for f in forms.split(",") if f.strip()]
    if not entries:
        fd_fail(slug, "DOCUMENTATION.md", 0,
                "missing required input: the glossary region parses to no entries "
                "(`### <headword>` with its seven labelled fields)")
    return doc, region, entries


def fd_field(entry: dict, label: str):
    return entry["values"].get(label, ("", entry["line"]))


def fd_rows(slug: str, required: bool = True):
    """(DOCUMENTATION doc, region, {id: row}, [rows]) for the enforcement
    region, with line-0 findings for a missing region, table or body row when
    the region is one of the check's required inputs; None when
    DOCUMENTATION.md cannot be read. A row is (line, cells, id)."""
    doc = fd_doc(slug, "DOCUMENTATION.md")
    if doc is None:
        return None
    region = fd_region(doc, FD_ENFORCEMENT_HEADING)
    if region is None:
        if required:
            fd_fail(slug, "DOCUMENTATION.md", 0, f"missing required input: no enforcement "
                                                 f"region `{FD_ENFORCEMENT_HEADING}`")
        return doc, None, {}, []
    tables = fd_tables(doc, region[0] + 1, region[1])
    if not tables:
        if required:
            fd_fail(slug, "DOCUMENTATION.md", region[0] + 1,
                    "missing required input: the enforcement region holds no table")
        return doc, region, {}, []
    rows = []
    for n, cells in tables[0][2]:
        m = FD_ANCHOR_TAG.match(cells[0]) if cells else None
        rid = m.group(1) if m and m.group(1).startswith("enf-") else None
        rows.append((n, cells, rid))
    if not rows and required:
        fd_fail(slug, "DOCUMENTATION.md", tables[0][0],
                "missing required input: the enforcement table has no body row")
    return doc, region, {r[2]: r for r in rows if r[2]}, rows


def fd_row_class(row) -> list:
    return fd_bold(row[1][2]) if len(row[1]) > 2 else []


def fd_term_matcher(entries: list):
    """(regex, {form: entry}) matching every entry's forms, longest first, so
    at one position the longest form wins and a nested form is no occurrence."""
    by_form = {}
    for e in entries:
        for f in e["forms"]:
            by_form.setdefault(re.sub(r"\s+", " ", f.lower()), e)
    if not by_form:
        return None, by_form
    alts = sorted(by_form, key=len, reverse=True)
    rx = re.compile(r"(?<![A-Za-z0-9_-])(?:"
                    + "|".join(re.escape(f).replace(r"\ ", r"\s+") for f in alts)
                    + r")(?![A-Za-z0-9_-])", re.I)
    return rx, by_form


def fd_occurrences(rx, by_form: dict, masked: str) -> list:
    """[(start, end, entry)] of term occurrences in masked text."""
    if rx is None:
        return []
    return [(m.start(), m.end(), by_form[re.sub(r"\s+", " ", m.group(0).lower())])
            for m in rx.finditer(masked)]


def fd_linked_to(text: str, pos: int, from_rel: str):
    """The resolved (file, fragment) of the link whose text holds `pos`."""
    for _t, target, _s, _e, ts, te in fd_links(text):
        if ts <= pos < te:
            return fd_resolve(from_rel, target) or ("", "")
    return None


def fd_content_tokens(text: str) -> list:
    text = FD_LINK.sub(lambda m: m.group(1), text)
    text = FD_CODE_SPAN.sub(lambda m: m.group(2), text)
    text = re.sub(r"[*_`]", "", text).lower()
    return [t for t in re.findall(r"[a-z0-9]+", text) if t not in FD_STOPWORDS]


def fd_overlap(definition: list, candidate: list) -> float:
    """Containment of a definition's shingles in a candidate (§6 metric)."""
    if len(definition) < DEFINITION_MIN_TOKENS:
        n = len(definition)
        return 1.0 if n and any(candidate[k:k + n] == definition
                                for k in range(len(candidate) - n + 1)) else 0.0
    k = DEFINITION_SHINGLE
    dset = {tuple(definition[i:i + k]) for i in range(len(definition) - k + 1)}
    cset = {tuple(candidate[i:i + k]) for i in range(len(candidate) - k + 1)}
    return len(dset & cset) / len(dset)


def fd_assignment_line(name: str) -> int:
    """The line of `name`'s top-level assignment in this file."""
    src = Path(__file__).read_text(encoding="utf-8")
    m = re.search(rf"(?m)^{name}\s*(?::[^=\n]+)?=", src)
    return src.count("\n", 0, m.start()) + 1 if m else 0


def fd_version(text: str):
    return tuple(int(p) for p in text.split("."))


def fd_negated(masked: str, pos: int) -> bool:
    """A strong-claim word with a negator among the three words before it."""
    before = re.findall(r"[A-Za-z']+", masked[:pos])[-3:]
    return any(w.lower() in FD_NEGATORS or w.lower().endswith("n't") for w in before)


def check_fd_first_screen_order() -> None:
    """SPEC-0004 FIRST_SCREEN_ORDER: the first screen answers what, for whom,
    what it writes, what it costs and how to try it, in that order and within
    its line budgets, and those budgets stay under the spec's caps."""
    slug = "FIRST_SCREEN_ORDER"
    spec = fd_text(slug, FRONT_DOOR_SPEC)
    if spec is not None:
        for const, cap_name in FD_CAPS:
            caps = re.findall(rf"(?m)^\| `{cap_name}` \| (\d+) \|", spec)
            if len(caps) != 1:
                fd_fail(slug, FRONT_DOOR_SPEC, 0,
                        f"missing required input: the §6 constants table has "
                        f"{len(caps)} rows for {cap_name}, not one")
                continue
            value, cap = globals()[const], int(caps[0])
            if value > cap:
                fd_fail(slug, "tests/seed-lint.py", fd_assignment_line(const),
                        f"{const} {value} exceeds {cap_name} {cap}; a ratchet raised "
                        f"with its lock is refused until the spec's cap changes first")
    doc = fd_doc(slug, "README.md")
    if doc is None:
        return
    lines, kinds = doc
    level2 = [(n, text) for n, level, text in fd_headings(doc) if level == 2]
    if not level2:
        fd_fail(slug, "README.md", 0, "missing required input: README has no `##` heading")
    first = FD_README_HEADINGS[:5]
    for k, (n, text) in enumerate(level2[:5]):
        if text == first[k]:
            continue
        if text in first:
            fd_fail(slug, "README.md", n, f"`{text}` is out of order: position {k + 1} "
                                          f"of the first screen is `{first[k]}`")
        else:
            fd_fail(slug, "README.md", n, f"`{text}` sits among the first-screen headings; "
                                          f"position {k + 1} is `{first[k]}`")
    for k in range(len(level2), 5):
        fd_fail(slug, "README.md", 0, f"the first screen lacks `{first[k]}`")
    if level2 and level2[0][0] > FIRST_HEADING_MAX_LINE:
        fd_fail(slug, "README.md", level2[0][0],
                f"the first `##` heading sits on line {level2[0][0]}, past "
                f"FIRST_HEADING_MAX_LINE {FIRST_HEADING_MAX_LINE}")
    markers = [i + 1 for i, line in enumerate(lines) if line == FIRST_SCREEN_MARKER]
    if not markers:
        fd_fail(slug, "README.md", 0, f"no `{FIRST_SCREEN_MARKER}` line ends the first screen")
    for extra in markers[1:]:
        fd_fail(slug, "README.md", extra, f"a second `{FIRST_SCREEN_MARKER}` line; "
                                          f"exactly one ends the first screen")
    if markers:
        mark = markers[0]
        fifth = level2[4][0] if len(level2) >= 5 else None
        if fifth is None or mark < fifth or any(fifth < n < mark for n, _t in level2):
            fd_fail(slug, "README.md", mark, f"`{FIRST_SCREEN_MARKER}` must sit after the "
                                             f"fifth `##` heading and before the next one")
        if mark > FIRST_SCREEN_MAX_LINES:
            fd_fail(slug, "README.md", mark, f"`{FIRST_SCREEN_MARKER}` sits on line {mark}, "
                                             f"past FIRST_SCREEN_MAX_LINES {FIRST_SCREEN_MAX_LINES}")
        later = [(n, t) for n, t in level2 if n > mark]
        firsts = []
        for heading in FD_README_HEADINGS[5:]:
            at = [n for n, t in later if t == heading]
            if not at:
                fd_fail(slug, "README.md", 0, f"`{heading}` is missing after the first screen")
                continue
            for dup in at[1:]:
                fd_fail(slug, "README.md", dup, f"`{heading}` appears {len(at)} times; "
                                                f"exactly once after the first screen")
            firsts.append((at[0], heading))
        for (n_a, h_a), (n_b, h_b) in zip(firsts, firsts[1:]):
            if n_b < n_a:
                fd_fail(slug, "README.md", n_b, f"`{h_b}` is out of order: it must follow `{h_a}`")
    fence, inside = None, False
    for i, line in enumerate(lines):
        opener = FD_FENCE.match(line) if kinds[i] == "fence" else None
        if kinds[i] != "fence":
            inside = False
        elif not inside:
            inside = True
            if opener and opener.group(2).strip() == "sh":
                fence = i
                break
        elif opener and not opener.group(2).strip():
            inside = False
    if fence is None:
        fd_fail(slug, "README.md", 0, f"no fenced `sh` block opens under `{FD_TRY_SECTION}`")
    else:
        under = next((t for n, t in reversed(level2) if n < fence + 1), None)
        if under != FD_TRY_SECTION:
            fd_fail(slug, "README.md", fence + 1, f"the first fenced `sh` block opens under "
                                                  f"`{under}`, not `{FD_TRY_SECTION}`")
        cmd = next((j for j in range(fence + 1, len(lines))
                    if kinds[j] == "fence" and "install.sh" in lines[j]), None)
        if cmd is None:
            fd_fail(slug, "README.md", fence + 1, "the first fenced `sh` block runs no install.sh")
        elif cmd + 1 > FIRST_COMMAND_LINE:
            fd_fail(slug, "README.md", cmd + 1, f"the first install.sh command sits on line "
                                                f"{cmd + 1}, past FIRST_COMMAND_LINE {FIRST_COMMAND_LINE}")
    for n, _l, text in fd_headings(doc):
        if text == FD_RETIRED_HEADING:
            fd_fail(slug, "README.md", n, f"`{FD_RETIRED_HEADING}` is a retired heading")


def check_fd_install_section_names_target_paths() -> None:
    """SPEC-0004 INSTALL_SECTION_NAMES_TARGET_PATHS: the install section names
    what lands in a project, by the installer's own paths, and never the
    seed's source tree."""
    slug = "INSTALL_SECTION_NAMES_TARGET_PATHS"
    install = fd_text(slug, "install.sh")
    doc = fd_doc(slug, "README.md")
    if doc is None:
        return
    region = fd_section(slug, doc, FD_INSTALL_SECTION)
    if region is None:
        return
    units = fd_units(doc, region[0] + 1, region[1])
    tokens = [(fd_line_of(n, t, a), c.strip()) for n, t in units for a, _b, c in fd_code_spans(t)]
    names = {c for _n, c in tokens}
    for target in FD_INSTALL_TARGETS:
        if target not in names:
            fd_fail(slug, "README.md", region[0] + 1, f"does not name the target `{target}`")
    for n, token in tokens:
        if token.startswith(FD_SEED_SOURCE_PREFIXES):
            prefix = next(p for p in FD_SEED_SOURCE_PREFIXES if token.startswith(p))
            fd_fail(slug, "README.md", n, f"`{token}` is a seed-source path ({prefix}); "
                                          f"the section names what lands in a project")
        elif install is not None and token != "install.sh" and fd_path_like(token):
            problem = fd_install_literal_problem(token, install)
            if problem:
                fd_fail(slug, "README.md", n, problem)
    if not any(".cypress/seed.json" in t and any(
            (fd_resolve("README.md", g) or ("", ""))[0] == "DOCUMENTATION.md"
            and (fd_resolve("README.md", g) or ("", ""))[1] == FD_BACKUP_ROW
            for _x, g, *_r in fd_links(t)) for _n, t in units):
        fd_fail(slug, "README.md", region[0] + 1,
                f"no unit names `.cypress/seed.json` and links "
                f"`DOCUMENTATION.md#{FD_BACKUP_ROW}`")


def check_fd_where_next_links_the_references() -> None:
    """SPEC-0004 WHERE_NEXT_LINKS_THE_REFERENCES: the closing section links
    every reference a reader continues to, and every link resolves."""
    slug = "WHERE_NEXT_LINKS_THE_REFERENCES"
    doc = fd_doc(slug, "README.md")
    if doc is None:
        return
    region = fd_section(slug, doc, FD_WHERE_SECTION)
    if region is None:
        return
    seen = set()
    for n, text in fd_units(doc, region[0] + 1, region[1]):
        for _t, target, start, *_r in fd_links(text):
            seen.add(target)
            line = fd_line_of(n, text, start)
            hit = fd_resolve("README.md", target)
            if hit is None:
                continue
            path, frag = hit
            if not (ROOT / path).exists():
                fd_fail(slug, "README.md", line, f"`{target}` does not resolve under the seed root")
            elif frag:
                target_doc = fd_doc(slug, path)
                if target_doc is not None and len(fd_anchors(target_doc).get(frag, [])) != 1:
                    fd_fail(slug, "README.md", line,
                            f"`{target}`: #{frag} names no single explicit anchor in {path}")
    for target in FD_WHERE_NEXT:
        if target not in seen:
            fd_fail(slug, "README.md", region[0] + 1, f"no link to `{target}`")


def check_fd_glossary_entry_complete() -> None:
    """SPEC-0004 GLOSSARY_ENTRY_COMPLETE: every entry carries its anchor and
    its seven fields in order, with closed-set values, and every required
    headword has one."""
    slug = "GLOSSARY_ENTRY_COMPLETE"
    parsed = fd_glossary(slug)
    if parsed is None or parsed[1] is None or not parsed[2]:
        return
    _doc, _region, entries = parsed
    for e in entries:
        head, hl = e["head"], e["line"]
        if e["anchor"] is None:
            fd_fail(slug, "DOCUMENTATION.md", hl, f"`### {head}` has no `term-` anchor")
        elif not e["anchor_next"]:
            fd_fail(slug, "DOCUMENTATION.md", hl, f"anchor `{e['id']}` must sit on the line "
                                                  f"after `### {head}`")
        if e["id"] is not None and not re.fullmatch(r"term-[a-z0-9]+(-[a-z0-9]+)*", e["id"]):
            fd_fail(slug, "DOCUMENTATION.md", hl, f"anchor `{e['id']}` is not a `term-` id")
        labels = [f[0] for f in e["fields"]]
        for label in FD_FIELDS:
            count = labels.count(label)
            if count != 1:
                fd_fail(slug, "DOCUMENTATION.md", hl,
                        f"`{head}` has {count} {label} fields; exactly one is required")
        known = [lab for lab in labels if lab in FD_FIELDS]
        if known != [lab for lab in FD_FIELDS if lab in known] or \
                any(lab not in FD_FIELDS for lab in labels):
            fd_fail(slug, "DOCUMENTATION.md", hl, f"`{head}` fields are out of order or "
                                                  f"unknown: {labels}; the order is {list(FD_FIELDS)}")
        for label, value, n in e["fields"]:
            if not value:
                fd_fail(slug, "DOCUMENTATION.md", n, f"`{head}` {label} is empty")
        if e["forms"] and head.lower() not in [f.lower() for f in e["forms"]]:
            fd_fail(slug, "DOCUMENTATION.md", hl, f"`{head}` Forms does not include the headword")
        enf, en = fd_field(e, "Enforcement")
        classes = fd_bold(enf)
        if "Enforcement" in e["values"] and not classes:
            fd_fail(slug, "DOCUMENTATION.md", en, f"`{head}` Enforcement carries no bolded class")
        for c in classes:
            if c not in FD_CLASS_ORDER:
                fd_fail(slug, "DOCUMENTATION.md", en,
                        f"`{head}` Enforcement value **{c}** is not in the class set")
        div, dn = fd_field(e, "Divergence")
        values = fd_bold(div)
        if "Divergence" in e["values"] and not values:
            fd_fail(slug, "DOCUMENTATION.md", dn, f"`{head}` Divergence carries no bolded value")
        for v in values:
            if v not in FD_DIVERGENCES:
                fd_fail(slug, "DOCUMENTATION.md", dn,
                        f"`{head}` Divergence value **{v}** is not in the divergence set")
        field, fn = fd_field(e, "Field")
        if "Field" in e["values"]:
            statuses = re.findall(r"status: (verified|secondhand|not recorded)", field)
            if "no standard meaning" not in field and not statuses:
                fd_fail(slug, "DOCUMENTATION.md", fn,
                        f"`{head}` Field says neither `no standard meaning` nor a status")
            if "verified" in statuses and not (re.search(r"https://\S+", field)
                                              and re.search(r"\b\d{4}-\d{2}-\d{2}\b", field)):
                fd_fail(slug, "DOCUMENTATION.md", fn, f"`{head}` Field says status: verified "
                                                      f"without an https:// URL and a date")
        why, wn = fd_field(e, "Why")
        if "Why" in e["values"] and not FD_WHY.search(why.strip()):
            fd_fail(slug, "DOCUMENTATION.md", wn,
                    f"`{head}` Why names no ADR, spec, plan, commit, path:line or `not recorded`")
    by_head = {e["head"]: e for e in entries}
    for head, rid in FD_REQUIRED_TERMS.items():
        if head not in by_head:
            fd_fail(slug, "DOCUMENTATION.md", 0, f"no entry for required headword '{head}'")
        elif by_head[head]["id"] not in (None, rid):
            fd_fail(slug, "DOCUMENTATION.md", by_head[head]["line"],
                    f"required headword '{head}' must carry anchor `{rid}`")


def check_fd_glossary_paths_exist() -> None:
    """SPEC-0004 GLOSSARY_PATHS_EXIST: every Implemented at path resolves in
    the seed, and every install target and function is the installer's."""
    slug = "GLOSSARY_PATHS_EXIST"
    parsed = fd_glossary(slug)
    install = fd_text(slug, "install.sh")
    if parsed is None or not parsed[2]:
        return
    functions = set(re.findall(r"(?m)^([a-z_][a-z0-9_]*)\(\)", install or ""))
    for e in parsed[2]:
        value, n = fd_field(e, "Implemented at")
        if "Implemented at" not in e["values"]:
            continue
        masked = fd_mask(value)
        clause = masked.find("An install produces")
        clause_end = len(value)
        if clause >= 0:
            end = re.search(r"[.!?](?=\s+[A-Z\[`*(]|\s*$)", masked[clause:])
            clause_end = clause + end.end() if end else len(value)
        spans = fd_code_spans(value)
        if not any(fd_path_like(c.strip()) for _a, _b, c in spans) and \
                not value.startswith("n/a"):
            fd_fail(slug, "DOCUMENTATION.md", n,
                    f"`{e['head']}` Implemented at names no path and does not begin `n/a`")
        for a, _b, code in spans:
            token = code.strip()
            inside = clause >= 0 and clause <= a < clause_end
            if inside and fd_path_like(token):
                if install is not None:
                    problem = fd_install_literal_problem(token, install)
                    if problem:
                        fd_fail(slug, "DOCUMENTATION.md", n, f"`{e['head']}`: {problem}")
            elif inside and re.fullmatch(r"[a-z_][a-z0-9_]*", token):
                if install is not None and token not in functions:
                    fd_fail(slug, "DOCUMENTATION.md", n,
                            f"`{e['head']}`: `{token}` is not a function install.sh defines")
            elif not inside and fd_path_like(token):
                problem = fd_seed_path_problem(token)
                if problem:
                    fd_fail(slug, "DOCUMENTATION.md", n, f"`{e['head']}`: {problem}")


def check_fd_no_unlinked_project_term_in_definition() -> None:
    """SPEC-0004 NO_UNLINKED_PROJECT_TERM_IN_DEFINITION: a definition that
    uses another coined term links that term's entry at its first use."""
    slug = "NO_UNLINKED_PROJECT_TERM_IN_DEFINITION"
    parsed = fd_glossary(slug)
    if parsed is None or not parsed[2]:
        return
    entries = parsed[2]
    project = [e for e in entries if "**no standard meaning**" in fd_field(e, "Divergence")[0]]
    if not project:
        fd_fail(slug, "DOCUMENTATION.md", 0,
                "missing required input: no entry's Divergence is **no standard meaning**")
        return
    rx, by_form = fd_term_matcher(project)
    for e in entries:
        here, n = fd_field(e, "Here")
        seen = set()
        for start, _end, other in fd_occurrences(rx, by_form, fd_mask(here)):
            if other is e or other["head"] in seen:
                continue
            seen.add(other["head"])
            hit = fd_linked_to(here, start, "DOCUMENTATION.md")
            want = ("DOCUMENTATION.md", other["id"])
            if hit != want:
                got = f"links #{hit[1]}" if hit else "is not linked"
                fd_fail(slug, "DOCUMENTATION.md", n,
                        f"`{e['head']}` Here: the first '{here[start:_end]}' {got}; "
                        f"it must link #{other['id']}")


def check_fd_term_linked_on_first_use() -> None:
    """SPEC-0004 TERM_LINKED_ON_FIRST_USE: README links a term whose meaning
    departs from the field's the first time it uses it."""
    slug = "TERM_LINKED_ON_FIRST_USE"
    parsed = fd_glossary(slug)
    doc = fd_doc(slug, "README.md")
    if parsed is None or not parsed[2]:
        return
    checked = [e for e in parsed[2] if fd_field(e, "Divergence")[0].strip() != "**same**"]
    if not checked:
        fd_fail(slug, "DOCUMENTATION.md", 0,
                "missing required input: no glossary entry diverges from its field meaning")
        return
    if doc is None:
        return
    rx, by_form = fd_term_matcher(checked)
    done = set()
    for n, text in fd_units(doc):
        for start, end, e in fd_occurrences(rx, by_form, fd_mask(text)):
            if e["head"] in done:
                continue
            done.add(e["head"])
            hit = fd_linked_to(text, start, "README.md")
            if hit != ("DOCUMENTATION.md", e["id"]):
                got = f"links #{hit[1]}" if hit else "is not linked"
                fd_fail(slug, "README.md", fd_line_of(n, text, start),
                        f"the first '{text[start:end]}' {got}; it must link "
                        f"DOCUMENTATION.md#{e['id']}")


def check_fd_definition_has_one_home() -> None:
    """SPEC-0004 DEFINITION_HAS_ONE_HOME: no front-door unit outside the
    glossary restates an entry's definition."""
    slug = "DEFINITION_HAS_ONE_HOME"
    parsed = fd_glossary(slug)
    if parsed is None or not parsed[2]:
        return
    entries, region = parsed[2], parsed[1]
    defs = []
    for e in entries:
        for _s, sentence in fd_sentences(fd_field(e, "Here")[0]):
            tokens = fd_content_tokens(sentence)
            if tokens:
                defs.append((e, tokens))
    if not defs:
        fd_fail(slug, "DOCUMENTATION.md", 0,
                "missing required input: no glossary entry has a Here sentence")
        return
    rx, by_form = fd_term_matcher(entries)
    for rel in fd_front_door_files():
        doc = fd_doc(slug, rel)
        if doc is None:
            continue
        for n, text in fd_units(doc):
            if rel == "DOCUMENTATION.md" and region[0] < n <= region[1]:
                continue
            present = {id(e) for _a, _b, e in fd_occurrences(rx, by_form, fd_mask(text))}
            if not present:
                continue
            candidate = fd_content_tokens(text)
            worst = {}
            for e, tokens in defs:
                if id(e) in present:
                    worst[e["head"]] = max(worst.get(e["head"], 0.0), fd_overlap(tokens, candidate))
            for head, ov in worst.items():
                if ov >= DEFINITION_OVERLAP_CEILING:
                    fd_fail(slug, rel, n, f"restates the glossary definition of '{head}' "
                                          f"(overlap {ov:.2f}, ceiling "
                                          f"{DEFINITION_OVERLAP_CEILING:.2f})")


def check_fd_reference_opens_with_its_definition() -> None:
    """SPEC-0004 REFERENCE_OPENS_WITH_ITS_DEFINITION: each reference says
    what its subject is before its tables, and links the glossary entry."""
    slug = "REFERENCE_OPENS_WITH_ITS_DEFINITION"
    for rel, pattern, words, link in FD_REFERENCE_OPENERS:
        doc = fd_doc(slug, rel)
        if doc is None:
            continue
        titles = [n for n, level, _t in fd_headings(doc) if level == 1]
        if not titles:
            fd_fail(slug, rel, 0, "missing required input: no `#` title")
            continue
        unit = next(((n, t) for n, t in fd_units(doc) if n > titles[0]), None)
        if unit is None:
            fd_fail(slug, rel, 0, "missing required input: no paragraph after the `#` title")
            continue
        n, text = unit
        sentences = fd_sentences(text)
        if not sentences or not re.search(pattern, sentences[0][1]):
            fd_fail(slug, rel, n, f"the first paragraph does not open with `{words}`")
        if link not in [target for _t, target, *_r in fd_links(text)]:
            fd_fail(slug, rel, n, f"the first paragraph does not link `{link}`")


def check_fd_enforcement_row_complete() -> None:
    """SPEC-0004 ENFORCEMENT_ROW_COMPLETE: every row names its mechanism,
    artifact, class and residual; the required rows exist; the rows security
    named state their residuals and class rules; and the matrix's class table
    cannot map a hook that only injects text to `hard`."""
    slug = "ENFORCEMENT_ROW_COMPLETE"
    parsed = fd_rows(slug)
    matrix = fd_doc(slug, FD_MATRIX)
    if matrix is not None:
        row = next(((n, cells) for _h, _c, body in fd_tables(matrix) for n, cells in body
                    if cells and cells[0] == "**mechanically enforced**"), None)
        if row is None:
            fd_fail(slug, FD_MATRIX, 0, "missing required input: no class-table row whose "
                                        "first cell is `**mechanically enforced**`")
        else:
            n, cells = row
            if len(cells) < 2 or "injects" not in cells[1]:
                fd_fail(slug, FD_MATRIX, n, "the `**mechanically enforced**` Meaning cell does "
                                            "not say a hook that only injects text holds nothing")
            if len(cells) < 3 or "not a control" not in cells[2]:
                fd_fail(slug, FD_MATRIX, n, "the `**mechanically enforced**` ADR-0003 cell does "
                                            "not class an inject-only hook `not a control`")
    if parsed is None or parsed[1] is None:
        return
    _doc, _region, by_id, rows = parsed
    for n, cells, rid in rows:
        name = rid or "a row"
        if len(cells) != 5:
            fd_fail(slug, "DOCUMENTATION.md", n, f"{name} has {len(cells)} cells, not 5")
            continue
        for label, cell in zip(("Mechanism", "Artifact", "Class", "What it can miss",
                                "Detail"), cells):
            if not FD_ANCHOR_TAG.sub("", cell).strip():
                fd_fail(slug, "DOCUMENTATION.md", n, f"{name}: the {label} cell is empty")
        if rid is None:
            fd_fail(slug, "DOCUMENTATION.md", n, "the row's first cell does not begin with "
                                                 "an `enf-` anchor")
        classes = fd_bold(cells[2])
        if not classes:
            fd_fail(slug, "DOCUMENTATION.md", n, f"{name}: the Class cell carries no bolded class")
        for c in classes:
            if c not in FD_CLASS_ORDER:
                fd_fail(slug, "DOCUMENTATION.md", n, f"{name}: Class **{c}** is not in the class set")
        artifacts = [c.strip() for _a, _b, c in fd_code_spans(cells[1]) if fd_path_like(c.strip())]
        if not artifacts:
            fd_fail(slug, "DOCUMENTATION.md", n, f"{name}: the Artifact cell names no seed path")
        for token in artifacts:
            problem = fd_seed_path_problem(token)
            if problem:
                fd_fail(slug, "DOCUMENTATION.md", n, f"{name}: {problem}")
        patterns, rule = FD_ROW_RESIDUALS.get(rid, ([], None))
        for pattern, words in patterns:
            if not re.search(pattern, cells[3], re.I):
                fd_fail(slug, "DOCUMENTATION.md", n,
                        f"{rid}: What it can miss does not name {words}")
        weakest = fd_weakest(classes)
        if rule in ("not-hard", "not-hard-scoped") and weakest == "hard":
            fd_fail(slug, "DOCUMENTATION.md", n,
                    f"{rid}: weakest class is hard; this row's weakest class must not be hard")
        if rule == "not-hard-scoped" and \
                cells[2].count("**hard**") != cells[2].count(FD_PRE_BASH_HARD):
            fd_fail(slug, "DOCUMENTATION.md", n,
                    f"{rid}: **hard** appears only as `{FD_PRE_BASH_HARD}`")
        if rule == "not-a-control" and f"**{FD_NOT_A_CONTROL}**" not in cells[2]:
            fd_fail(slug, "DOCUMENTATION.md", n,
                    f"{rid}: a hook that only injects text is **{FD_NOT_A_CONTROL}**")
    for rid in FD_REQUIRED_ROWS:
        if rid not in by_id:
            fd_fail(slug, "DOCUMENTATION.md", 0, f"no required row `{rid}`")


def check_fd_mechanism_claims_traced() -> None:
    """SPEC-0004 MECHANISM_CLAIMS_TRACED: a mechanism claim on a traced
    surface links the row that holds it; a strong claim that links rows links
    only hard ones; a glossary class agrees with its rows; and nothing that
    links the command guard calls it security."""
    slug = "MECHANISM_CLAIMS_TRACED"
    rows = fd_rows(slug)
    glossary = fd_glossary(slug)
    by_id = rows[2] if rows else {}
    region = rows[1] if rows else None
    entries = glossary[2] if glossary else []
    hosts = sorted(p.relative_to(ROOT).as_posix()
                   for p in (ROOT / "integrations").glob("*/README.md"))
    if not hosts:
        fd_fail(slug, "integrations", 0, "missing required input: no integrations/*/README.md")
    traced_fields = {e["values"][label][1] for e in entries
                     for label in ("Here", "Enforcement") if label in e["values"]}
    for rel in fd_front_door_files():
        doc = fd_doc(slug, rel)
        if doc is None:
            continue
        traced = rel in ("README.md", "INSTALL.md") or rel in hosts
        for n, text in fd_units(doc):
            in_region = rel == "DOCUMENTATION.md" and region is not None and \
                region[0] < n <= region[1]
            masked = fd_mask(text)
            linked = fd_row_links(rel, text)
            if rel == "DOCUMENTATION.md" and n in traced_fields:
                # A glossary field's own label (`**Enforcement:**`) is no claim.
                label = FD_FIELD_LINE.match(text)
                masked = " " * label.start(2) + masked[label.start(2):] if label else masked
                trace = True
            else:
                trace = traced
            verbs = list(FD_MECHANISM_VERB.finditer(masked))
            if verbs and trace:
                unknown = [r for r in linked if r not in by_id]
                if unknown:
                    fd_fail(slug, rel, n, f"links {', '.join(unknown)}, which is no "
                                          f"enforcement row")
                elif not linked:
                    said = ", ".join(dict.fromkeys(f"'{v.group(0)}'" for v in verbs))
                    fd_fail(slug, rel, fd_line_of(n, text, verbs[0].start()),
                            f"{said}: a mechanism claim that links no enforcement row")
            if not in_region and linked:
                strong = [m for m in FD_STRONG_CLAIM.finditer(masked)
                          if not fd_negated(masked, m.start())]
                if strong:
                    weak = [(r, fd_weakest(fd_row_class(by_id[r]))) for r in linked if r in by_id]
                    weak = [(r, c) for r, c in weak if c != "hard"]
                    if weak:
                        fd_fail(slug, rel, n, f"overclaim: says '{strong[0].group(0)}' and links "
                                              + ", ".join(f"{r} (weakest class: {c})"
                                                          for r, c in weak))
            if FD_PRE_BASH_ROW in linked:
                bad = FD_GUARD_MISNOMER.search(masked)
                if bad:
                    fd_fail(slug, rel, n, f"links {FD_PRE_BASH_ROW} and calls it "
                                          f"'{bad.group(0)}'; a pattern hook is no security "
                                          f"control, sandbox or protection")
    for e in entries:
        if "Enforcement" not in e["values"]:
            continue
        value, n = fd_field(e, "Enforcement")
        classes = [c for c in fd_bold(value) if c in FD_CLASS_ORDER]
        links = fd_row_links("DOCUMENTATION.md", value)
        known = [r for r in links if r in by_id]
        if any(c != FD_NOT_A_CONTROL for c in classes) and not links:
            fd_fail(slug, "DOCUMENTATION.md", n, f"`{e['head']}` Enforcement names a class "
                                                 f"and links no `enf-` row")
        for c in classes:
            if known and not any(c in fd_row_class(by_id[r]) for r in known):
                fd_fail(slug, "DOCUMENTATION.md", n, f"`{e['head']}` Enforcement says **{c}**, "
                                                     f"which no row it links carries")
        if "hard" in classes and known and not any(
                fd_weakest(fd_row_class(by_id[r])) == "hard" for r in known):
            fd_fail(slug, "DOCUMENTATION.md", n, f"`{e['head']}` Enforcement says **hard** and "
                                                 f"links no row whose weakest class is hard")


def check_fd_limits_section_present() -> None:
    """SPEC-0004 LIMITS_SECTION_PRESENT: README says what is only requested,
    each item linking a row that is not hard, and what is not yet measured."""
    slug = "LIMITS_SECTION_PRESENT"
    doc = fd_doc(slug, "README.md")
    if doc is None:
        return
    region = fd_section(slug, doc, FD_LIMITS_SECTION)
    if region is None:
        return
    lines, kinds = doc
    subs = [(i, lines[i].rstrip()) for i in range(region[0] + 1, region[1])
            if kinds[i] == "heading" and lines[i].startswith("### ")]
    if [t for _i, t in subs] != list(FD_LIMITS_SUBSECTIONS):
        fd_fail(slug, "README.md", region[0] + 1,
                f"the section must hold exactly `{FD_LIMITS_SUBSECTIONS[0]}` then "
                f"`{FD_LIMITS_SUBSECTIONS[1]}`; it holds {[t for _i, t in subs]}")
    parsed = fd_rows(slug, required=False)
    by_id = parsed[2] if parsed else {}
    bounds = [i for i, _t in subs] + [region[1]]
    for k, (i, title) in enumerate(subs):
        items = [(n, t) for n, t in fd_units(doc, i + 1, bounds[k + 1])
                 if FD_LIST_ITEM.match(t)]
        if title == FD_LIMITS_SUBSECTIONS[0]:
            if len(items) < LIMITS_MIN_REQUESTED:
                fd_fail(slug, "README.md", i + 1, f"`{title}` holds {len(items)} items; "
                                                  f"LIMITS_MIN_REQUESTED is {LIMITS_MIN_REQUESTED}")
            linked_all = set()
            for n, text in items:
                ids = fd_row_links("README.md", text)
                linked_all.update(ids)
                known = [r for r in ids if r in by_id]
                if not known:
                    fd_fail(slug, "README.md", n, "the item links no existing `enf-` row")
                elif not any(c != "hard" for r in known for c in fd_row_class(by_id[r])):
                    fd_fail(slug, "README.md", n, f"the item links only rows classed **hard** "
                                                  f"({', '.join(known)}); a requested limit is "
                                                  f"held by a row that is not hard")
            for rid in FD_LIMITS_REQUIRED_ROWS:
                if rid not in linked_all:
                    fd_fail(slug, "README.md", i + 1, f"no `{title}` item links `{rid}`")
        elif title == FD_LIMITS_SUBSECTIONS[1]:
            if len(items) < LIMITS_MIN_UNMEASURED:
                fd_fail(slug, "README.md", i + 1, f"`{title}` holds {len(items)} items; "
                                                  f"LIMITS_MIN_UNMEASURED is {LIMITS_MIN_UNMEASURED}")
            for n, text in items:
                if not any(p in text.lower() for p in FD_UNMEASURED_PHRASES):
                    fd_fail(slug, "README.md", n, "the item says none of 'not recorded', "
                                                  "'not measured' or 'measured once'")


def check_fd_catalogs_out_of_readme() -> None:
    """SPEC-0004 CATALOGS_OUT_OF_README: README names a few examples per
    category, never the catalog, and no front-door file prints an ADR range."""
    slug = "CATALOGS_OUT_OF_README"
    agent_files = {}
    for p in sorted((ROOT / "agents").glob("*.md")):
        m = re.search(r"(?m)^name:\s*(\S+)", frontmatter_block(p))
        if m:
            agent_files[p.stem] = m.group(1).strip("'\"")
    sets = {
        "agents": set(agent_files.values()),
        "protocols": {p.stem for p in (ROOT / "protocols").glob("*.md")},
        "skills": {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")},
        "templates": {p.name for p in (ROOT / "templates").glob("*.template.md")},
        "adrs": {m.group(1) for p in (ROOT / "docs" / "decisions").glob("*.md")
                 for m in [re.match(r"(?i)adr-(\d{4})", p.name)] if m},
    }
    for cat, names in sets.items():
        if not names:
            fd_fail(slug, cat, 0, f"missing required input: no {cat} name on disk")
    doc = fd_doc(slug, "README.md")
    if doc is not None:
        found = {cat: {} for cat in sets}

        def add(cat, name, line):
            if name in sets[cat]:
                found[cat].setdefault(name, line)
        for n, text in fd_units(doc):
            bare = list(text)
            for _t, _g, _s, end, _ts, te in fd_links(text):
                bare[te + 1:end] = " " * (end - te - 1)
            bare = "".join(bare)
            for a, _b, code in fd_code_spans(text):
                for cat in ("agents", "protocols", "skills"):
                    add(cat, code.strip(), fd_line_of(n, text, a))
            for m in re.finditer(r"\b(agent|protocol|skill)\.([A-Za-z0-9_-]+)", bare):
                add(m.group(1) + "s", m.group(2), fd_line_of(n, text, m.start()))
            for m in re.finditer(r"(?<![\w/.-])agents/([\w.-]+)\.md", bare):
                add("agents", agent_files.get(m.group(1), ""), fd_line_of(n, text, m.start()))
            for m in re.finditer(r"(?<![\w/.-])protocols/([\w.-]+)\.md", bare):
                add("protocols", m.group(1), fd_line_of(n, text, m.start()))
            for m in re.finditer(r"(?<![\w/.-])skills/([\w.-]+)/", bare):
                add("skills", m.group(1), fd_line_of(n, text, m.start()))
            for name in sets["templates"]:
                for m in re.finditer(re.escape(name), bare):
                    add("templates", name, fd_line_of(n, text, m.start()))
            for m in re.finditer(r"(?i)\badr-(\d{4})\b", bare):
                add("adrs", m.group(1), fd_line_of(n, text, m.start()))
        for cat, named in found.items():
            if len(named) > README_CATALOG_CEILING:
                at = sorted(named.values())[README_CATALOG_CEILING]
                fd_fail(slug, "README.md", at,
                        f"names {len(named)} {cat} ({', '.join(sorted(named))}); "
                        f"README_CATALOG_CEILING is {README_CATALOG_CEILING} per category, "
                        f"and the catalog lives in the references")
    for rel in fd_front_door_files():
        text = fd_text(slug, rel)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for m in FD_ADR_RANGE.finditer(line):
                fd_fail(slug, rel, n, f"`{m.group(0)}` is an ADR range; a range goes stale "
                                      f"with the next decision, so link the decision index")


def fd_number(text: str) -> float:
    return float(re.sub(r"[    ,]", "", text))


def fd_figure_form(number: str, unit: str) -> str:
    """A figure as §6 normalization writes it: `11%`, `8000 bytes`, `5 tokens`."""
    digits = re.sub(r"[    ,]", "", number)
    if unit == "%":
        return f"{digits}%"
    if unit in ("B", "byte", "bytes"):
        return f"{digits} bytes"
    if unit.startswith("token"):
        return f"{digits} tokens"
    return f"{digits} {unit}"


def fd_record_holds(record: str, form: str) -> bool:
    norm = re.sub(r"(?<=\d)[    ,](?=\d)", "", record)
    norm = re.sub(r"(\d)\s*(?:bytes?|B)\b", r"\1 bytes", norm)
    norm = re.sub(r"(\d)\s*tokens?\b", r"\1 tokens", norm)
    norm = re.sub(r"(\d)\s+%", r"\1%", norm)
    return form in norm or form.replace(" ", "") in norm


def check_fd_cost_figures_scoped() -> None:
    """SPEC-0004 COST_FIGURES_SCOPED: every cost figure in README says what
    it covers, and is either computed by this gate or measured with an
    evidence record that holds it."""
    slug = "COST_FIGURES_SCOPED"
    doc = fd_doc(slug, "README.md")
    if doc is None:
        return
    region = fd_section(slug, doc, FD_COST_SECTION)
    kernel = KERNEL.stat().st_size
    limits = {EAGER_BUDGET, KERNEL_BUDGET, MACHINERY_BODY_CEILING, LIFECYCLE_BODY_CEILING}
    derived = (set(eager_surfaces(kernel).values()) | limits | {kernel}
               | {value for value, _w, _l in routable_body_figures()})
    derived_in_section = 0
    for n, text in fd_units(doc):
        in_section = region is not None and region[0] < n <= region[1]
        masked = fd_mask(text)
        evidence = []
        for _t, target, *_r in fd_links(text):
            hit = fd_resolve("README.md", target)
            if hit and hit[0].startswith("docs/") and (ROOT / hit[0]).is_file():
                evidence.append(hit[0])
        unit_derived = False
        for m in FD_FIGURE.finditer(masked):
            unit = m.group(3)
            ends = [m.group(1)] + ([m.group(2)] if m.group(2) else [])
            line = fd_line_of(n, text, m.start())
            shown = re.sub(r"\s+", " ", m.group(0)).strip()
            if not any(k.lower() in masked.lower() for k in FD_SCOPE_MARKERS):
                fd_fail(slug, "README.md", line, f"figure '{shown}' names no scope "
                                                 f"(per session, per task, a host, budget, ...)")
            if unit in ("B", "byte", "bytes") and all(
                    (fd_number(e) in derived and re.search(r"(?i)\bcomputed\b", masked))
                    or (fd_number(e) in limits and FD_LIMIT_WORDS.search(masked)) for e in ends):
                unit_derived = True
                derived_in_section += in_section
                continue
            if FD_MEASURED_CLAIM.search(masked):
                if not evidence:
                    fd_fail(slug, "README.md", line, f"figure '{shown}' is called measured and "
                                                     f"links no evidence record under docs/")
                for record in evidence:
                    body = fd_text(slug, record)
                    for e in ends:
                        form = fd_figure_form(e, unit)
                        if body is not None and not fd_record_holds(body, form):
                            fd_fail(slug, "README.md", line, f"'{form}' does not occur in {record}")
                continue
            fd_fail(slug, "README.md", line,
                    f"figure '{shown}' is neither derived (a value this gate computes, said "
                    f"to be computed, or a limit said to be one) nor measured with an "
                    f"evidence record")
        measur = FD_MEASUR_WORD.search(masked)
        if unit_derived and measur:
            fd_fail(slug, "README.md", fd_line_of(n, text, measur.start()),
                    f"'{measur.group(0)}' in a unit holding a derived figure; a derived "
                    f"figure is computed, not measured")
        if in_section and measur and not evidence:
            fd_fail(slug, "README.md", fd_line_of(n, text, measur.start()),
                    f"'{measur.group(0)}' with no evidence record in this unit")
    if region is not None and not derived_in_section:
        fd_fail(slug, "README.md", 0, f"missing required input: `{FD_COST_SECTION}` holds no "
                                      f"derived figure")


def check_fd_eager_figures_checked_wherever_published() -> None:
    """SPEC-0004 EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED: an always-loaded
    figure is computed wherever the front door prints it. The pair
    check_published_eager_figures has always held is never pending."""
    slug = "EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED"
    live = set(eager_surfaces(KERNEL.stat().st_size).values()) | {EAGER_BUDGET}
    for rel in fd_front_door_files():
        text = fd_text(slug, rel)
        if text is None:
            continue
        for n, m, value in stale_eager_figures(text, live):
            closest = min(live, key=lambda v: abs(v - value))
            fd_fail(slug, rel, n, f"publishes {m.group(1)} bytes as an always-loaded surface, "
                                  f"and check_eager_surface computes no such figure "
                                  f"(nearest: {closest})", pendable=rel not in EAGER_PUBLISHED)


def check_fd_body_figures_have_a_required_home() -> None:
    """SPEC-0004 BODY_FIGURES_HAVE_A_REQUIRED_HOME: the body-size figures have
    one required home, the EAGER_EXEMPTIONS phrases hold on every front-door
    page, and the project-node exemption stays bound to graph-lint.py."""
    slug = "BODY_FIGURES_HAVE_A_REQUIRED_HOME"
    home = fd_text(slug, BODY_FIGURE_HOME)
    if home is not None:
        for value, what, _label in routable_body_figures():
            if not any(re.search(rf"(?<![\d.]){re.escape(form)}(?!\d)", home)
                       for form in grouped_forms(value)):
                fd_fail(slug, BODY_FIGURE_HOME, 0, f"missing required input: states no figure "
                                                   f"matching {what} ({value})")
    graph_lint = "templates/knowledge-graph/graph-lint.py"
    source = fd_text(slug, graph_lint)
    if source is not None:
        for value in sorted(PROJECT_NODE_LINE_FIGURES):
            if not re.search(rf"(?<![\w.]){value}(?![\w.])", source):
                fd_fail(slug, graph_lint, 0, f"holds no {value} literal, so "
                                             f"PROJECT_NODE_LINE_FIGURES exempts a ceiling that "
                                             f"no longer exists")
    for rel in fd_front_door_files():
        doc = fd_doc(slug, rel)
        if doc is None:
            continue
        for n, line in enumerate(doc[0], 1):
            if EAGER_EXEMPTIONS and any(p in line for p in EAGER_EMPTY_PHRASES):
                fd_fail(slug, rel, n, f"says EAGER_EXEMPTIONS is consequently empty, and it "
                                      f"holds {sorted(EAGER_EXEMPTIONS)}")
            if EAGER_EXEMPTIONS and EAGER_NO_SLACK_PHRASE in line:
                fd_fail(slug, rel, n, "says the EAGER_BUDGET ratchet has 'no slack' while "
                                      "EAGER_EXEMPTIONS is non-empty")
        if rel == BODY_FIGURE_HOME:
            continue
        for n, text in fd_units(doc):
            masked = fd_mask(text)
            if not re.search(r"(?i)\bbod(?:y|ies)\b", masked):
                continue
            for m in FD_LINE_FIGURE.finditer(masked):
                if int(re.sub(r"\D", "", m.group(0))) not in PROJECT_NODE_LINE_FIGURES:
                    fd_fail(slug, rel, fd_line_of(n, text, m.start()),
                            f"a body figure '{m.group(0).strip()}' outside {BODY_FIGURE_HOME}, "
                            f"its one home")


def check_fd_front_door_anchors_resolve() -> None:
    """SPEC-0004 FRONT_DOOR_ANCHORS_RESOLVE: every term, row and region link
    lands on exactly one explicit anchor, and README's relative links resolve."""
    slug = "FRONT_DOOR_ANCHORS_RESOLVE"
    docu = fd_doc(slug, "DOCUMENTATION.md")
    if docu is not None:
        anchors = fd_anchors(docu)
        for rid in ("glossary", "enforcement"):
            if rid not in anchors:
                fd_fail(slug, "DOCUMENTATION.md", 0,
                        f"missing required input: no explicit anchor `{rid}` for the {rid} region")
        for aid, at in sorted(anchors.items()):
            for dup in at[1:]:
                fd_fail(slug, "DOCUMENTATION.md", dup,
                        f"anchor id `{aid}` is not unique (first at line {at[0]})")
    for rel in fd_front_door_files():
        doc = fd_doc(slug, rel)
        if doc is None:
            continue
        for n, text in fd_units(doc):
            for _t, target, start, *_r in fd_links(text):
                hit = fd_resolve(rel, target)
                if hit is None:
                    continue
                path, frag = hit
                line = fd_line_of(n, text, start)
                if rel == "README.md" and not (ROOT / path).exists():
                    fd_fail(slug, rel, line, f"`{target}` does not resolve to a file under the "
                                             f"seed root")
                    continue
                if frag.startswith(("term-", "enf-")) or frag in ("glossary", "enforcement"):
                    target_doc = fd_doc(slug, path) if (ROOT / path).is_file() else None
                    count = len(fd_anchors(target_doc).get(frag, [])) if target_doc else 0
                    if count != 1:
                        fd_fail(slug, rel, line, f"`{target}`: #{frag} names {count} explicit "
                                                 f"anchors in {path}, not one")


def check_fd_front_door_headings_well_formed() -> None:
    """SPEC-0004 FRONT_DOOR_HEADINGS_WELL_FORMED: one level-1 title first,
    and no heading level skipped on the way down."""
    slug = "FRONT_DOOR_HEADINGS_WELL_FORMED"
    for rel in ("README.md", "DOCUMENTATION.md") + tuple(r for r, *_x in FD_REFERENCE_OPENERS):
        doc = fd_doc(slug, rel)
        if doc is None:
            continue
        heads = fd_headings(doc)
        if not heads:
            fd_fail(slug, rel, 0, "missing required input: no ATX heading")
            continue
        if heads[0][1] != 1:
            fd_fail(slug, rel, heads[0][0], f"the first heading is level {heads[0][1]}; the "
                                            f"first heading is the one level-1 title")
        for n, level, text in heads[1:]:
            if level == 1:
                fd_fail(slug, rel, n, f"`{text}` is a second level-1 heading")
        if not any(level == 1 for _n, level, _t in heads):
            fd_fail(slug, rel, 0, "no level-1 heading")
        for (_pn, prev, _pt), (n, level, _t) in zip(heads, heads[1:]):
            if level > prev + 1:
                fd_fail(slug, rel, n, f"heading level jumps from {prev} to {level}")


def fd_link_scopes(slug: str) -> list:
    """(file, doc, first, end) for README and the glossary and enforcement
    regions, with a line-0 finding for a missing region."""
    scopes = []
    readme = fd_doc(slug, "README.md")
    if readme is not None:
        scopes.append(("README.md", readme, 0, len(readme[0])))
    docu = fd_doc(slug, "DOCUMENTATION.md")
    if docu is not None:
        for heading, name in ((FD_GLOSSARY_HEADING, "glossary"),
                              (FD_ENFORCEMENT_HEADING, "enforcement")):
            region = fd_region(docu, heading)
            if region is None:
                fd_fail(slug, "DOCUMENTATION.md", 0,
                        f"missing required input: no {name} region `{heading}`")
            else:
                scopes.append(("DOCUMENTATION.md", docu, region[0] + 1, region[1]))
    return scopes


def check_fd_link_text_stands_alone() -> None:
    """SPEC-0004 LINK_TEXT_STANDS_ALONE: a link's text says where it goes."""
    slug = "LINK_TEXT_STANDS_ALONE"
    for rel, doc, lo, hi in fd_link_scopes(slug):
        for n, text in fd_units(doc, lo, hi):
            for t, _g, start, *_r in fd_links(text):
                shown = fd_strip_markup(t)
                line = fd_line_of(n, text, start)
                if not shown:
                    fd_fail(slug, rel, line, "link text is empty")
                elif shown.lower() in FD_GENERIC_LINK_TEXTS:
                    fd_fail(slug, rel, line, f"link text '{shown}' does not say where it goes")
                elif shown.lower().startswith(("http://", "https://", "www.")):
                    fd_fail(slug, rel, line, f"link text '{shown}' is a bare URL")


def check_fd_tables_have_header_rows() -> None:
    """SPEC-0004 TABLES_HAVE_HEADER_ROWS: every table names its columns."""
    slug = "TABLES_HAVE_HEADER_ROWS"
    for rel, doc, lo, hi in fd_link_scopes(slug):
        for n, header, _body in fd_tables(doc, lo, hi):
            for k, cell in enumerate(header, 1):
                if not fd_strip_markup(cell):
                    fd_fail(slug, rel, n, f"header cell {k} of the table is empty")


def check_fd_pending_ledger_holds_only_failing_contracts() -> None:
    """SPEC-0004 PENDING_LEDGER_HOLDS_ONLY_FAILING_CONTRACTS: the ledger holds
    only contracts observed failing, is mirrored in tests/ratchets.json, and is
    empty once SPEC-0004 is implemented or the release carries the front door.
    Runs last: it reads what every other front-door check observed."""
    slug = FD_LEDGER_SLUG
    at = fd_assignment_line("FRONT_DOOR_PENDING")
    spec = fd_text(slug, FRONT_DOOR_SPEC)
    contracts = set(re.findall(r"(?m)^### Contract: ([A-Z0-9_]+)\s*$", spec or ""))
    if spec is not None and not contracts:
        fd_fail(slug, FRONT_DOOR_SPEC, 0, "missing required input: no `### Contract:` heading")
    for member in sorted(FRONT_DOOR_PENDING):
        if member == slug:
            fd_fail(slug, "tests/seed-lint.py", at, f"{member} is this contract's own slug and "
                                                    f"cannot be pending")
        elif member not in contracts or member not in _fd_ran:
            fd_fail(slug, "tests/seed-lint.py", at, f"{member} is not a `### Contract:` slug of "
                                                    f"SPEC-0004 that seed-lint checks")
        elif member not in _fd_raised and not _fd_observed.get(member):
            fd_fail(slug, "tests/seed-lint.py", at, f"{member}: stale pending entry: remove it "
                                                    f"(its check found nothing)")
    lock = fd_text(slug, "tests/ratchets.json")
    if lock is not None:
        mirror = json.loads(lock).get("ratchets", {}).get("FRONT_DOOR_PENDING")
        if mirror is None:
            fd_fail(slug, "tests/seed-lint.py", at, "FRONT_DOOR_PENDING is not mirrored in "
                                                    "tests/ratchets.json")
        else:
            for member in sorted(set(FRONT_DOOR_PENDING) ^ set(mirror)):
                fd_fail(slug, "tests/seed-lint.py", at, f"{member} is in one of FRONT_DOOR_PENDING "
                                                        f"and its tests/ratchets.json mirror only")
    status = (parse_frontmatter(ROOT / FRONT_DOOR_SPEC).get("status") if spec is not None
              else None)
    if status == "implemented" and FRONT_DOOR_PENDING:
        fd_fail(slug, "tests/seed-lint.py", at, f"ledger must be empty once SPEC-0004 is "
                                                f"implemented; it holds {sorted(FRONT_DOOR_PENDING)}")
    manifest = fd_text(slug, "manifest.json")
    if manifest is not None:
        version = str(json.loads(manifest).get("version", ""))
        try:
            released = fd_version(version) >= fd_version(FRONT_DOOR_RELEASE)
        except ValueError:
            fd_fail(slug, "manifest.json", 0, f"version {version!r} is not X.Y.Z")
            released = False
        if released and FRONT_DOOR_PENDING:
            fd_fail(slug, "tests/seed-lint.py", at, f"ledger must be empty from "
                                                    f"{FRONT_DOOR_RELEASE}; manifest.json is "
                                                    f"{version} and it holds "
                                                    f"{sorted(FRONT_DOOR_PENDING)}")
    for member in sorted(FRONT_DOOR_PENDING):
        held = _fd_held.get(member, [])
        if held and member not in _fd_raised:
            print(f"front-door: PENDING {member}: {len(held)} finding(s); first: {held[0]}")


def front_door_checks() -> None:
    """SPEC-0004's dispatcher: one guarded call per contract, each on its own
    line so the coverage binder sees every check live, and the ledger last."""
    with fd_guard("FIRST_SCREEN_ORDER"):
        check_fd_first_screen_order()
    with fd_guard("INSTALL_SECTION_NAMES_TARGET_PATHS"):
        check_fd_install_section_names_target_paths()
    with fd_guard("WHERE_NEXT_LINKS_THE_REFERENCES"):
        check_fd_where_next_links_the_references()
    with fd_guard("GLOSSARY_ENTRY_COMPLETE"):
        check_fd_glossary_entry_complete()
    with fd_guard("GLOSSARY_PATHS_EXIST"):
        check_fd_glossary_paths_exist()
    with fd_guard("NO_UNLINKED_PROJECT_TERM_IN_DEFINITION"):
        check_fd_no_unlinked_project_term_in_definition()
    with fd_guard("TERM_LINKED_ON_FIRST_USE"):
        check_fd_term_linked_on_first_use()
    with fd_guard("DEFINITION_HAS_ONE_HOME"):
        check_fd_definition_has_one_home()
    with fd_guard("REFERENCE_OPENS_WITH_ITS_DEFINITION"):
        check_fd_reference_opens_with_its_definition()
    with fd_guard("ENFORCEMENT_ROW_COMPLETE"):
        check_fd_enforcement_row_complete()
    with fd_guard("MECHANISM_CLAIMS_TRACED"):
        check_fd_mechanism_claims_traced()
    with fd_guard("LIMITS_SECTION_PRESENT"):
        check_fd_limits_section_present()
    with fd_guard("CATALOGS_OUT_OF_README"):
        check_fd_catalogs_out_of_readme()
    with fd_guard("COST_FIGURES_SCOPED"):
        check_fd_cost_figures_scoped()
    with fd_guard("EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED"):
        check_fd_eager_figures_checked_wherever_published()
    with fd_guard("BODY_FIGURES_HAVE_A_REQUIRED_HOME"):
        check_fd_body_figures_have_a_required_home()
    with fd_guard("FRONT_DOOR_ANCHORS_RESOLVE"):
        check_fd_front_door_anchors_resolve()
    with fd_guard("FRONT_DOOR_HEADINGS_WELL_FORMED"):
        check_fd_front_door_headings_well_formed()
    with fd_guard("LINK_TEXT_STANDS_ALONE"):
        check_fd_link_text_stands_alone()
    with fd_guard("TABLES_HAVE_HEADER_ROWS"):
        check_fd_tables_have_header_rows()
    with fd_guard(FD_LEDGER_SLUG):
        check_fd_pending_ledger_holds_only_failing_contracts()


def main() -> int:
    # A missing or unreadable file used to abort the run with a traceback, and
    # every finding already collected went unprinted — so the operator saw a
    # Python stack instead of the reason, and the lint reported nothing at all
    # about the tree it was linting. Found when a test renamed a node to prove a
    # check binds: the check did bind, and the crash hid its finding. The
    # failure is still a failure; it is just reported as one, after everything
    # that DID run has had its say.
    #
    # The tuple used to be (OSError, KeyError, ValueError), and that was this
    # same defect half-fixed: `agent-lint.py` is exec'd into this module and
    # raises its own `LintError`, which inherits from none of the three. A
    # malformed frontmatter list anywhere in agents/ therefore threw past the
    # handler and every finding already collected went unprinted — verified
    # with a genuine unrelated finding standing, which vanished. A bare
    # `Exception` is deliberate: the point is that NOTHING may swallow the
    # findings, whatever it is.
    try:
        check()
        # AFTER check(), because the machinery-node sweep inside it is what
        # populates _prevents_by_node. Calling it before compared zero nodes,
        # and the pass's own floor said so rather than reporting clean.
        check_prevents_are_distinct()
    except Exception as e:                       # noqa: BLE001 — see below
        findings.append(f"seed-lint could not complete: {type(e).__name__}: {e} "
                        f"— the findings above are everything that ran before it")
    # SPEC-0004's front door runs after the checks above and outside their
    # handler, so a check that raised on a front-door file (an undecodable
    # INSTALL.md, say) cannot stop it; each of its checks is guarded on its own.
    front_door_checks()
    if findings:
        print(f"seed lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("seed lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
