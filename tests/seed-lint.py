#!/usr/bin/env python3
"""seed-lint: one-home-per-fact enforcement for the seed's OWN meta-facts.

graph-lint.py guards a grown plant's docs/graph/; nothing guarded the
seed's meta-documentation, and its duplicated facts drifted (README said
5 coordinators and a 9 KB kernel while frontmatter said six and 27 KB).
This linter makes that failure class deterministic to catch:

  1. roster: agents/ frontmatter <-> manifest.json <-> kernel §1 table
  2. delegator invariant: can_delegate == (Task in tools); allowlists resolve
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

Dependency-free; exit 0 clean, 1 with findings.
"""
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
# enumerates at start-up. 32 000 bytes (~8k tokens) is four times the kernel's
# own budget, which is the room the roster and skill descriptions need at the
# current roster size.
EAGER_BUDGET = 32_000

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
        m = re.search(rf"^\s*def {re.escape(test)}\b", body, re.M)
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
    """The body-size claims in README derive from the same measurement the
    ceilings do, or they are not printed.

    U-15 was "README claimed `<500`-line bodies while three protocols sat
    between 658 and 931". The repair replaced `<500` with `1 384`, `median of
    166`, `1 000` and `2 500` — four numbers, all true on the day, and NONE of
    them derived. Appending sixty lines to `protocols/graft.md` left seed-lint
    PASS with the README still saying 1 384; tightening MACHINERY_BODY_CEILING
    to 900 left it still saying 1 000. That is U-15's own class — a reader-facing
    body-size number that nothing derives — reopened by its own fix.

    `EAGER_EXEMPTIONS` gets the same treatment: README says the dict is "empty"
    and the budget has "no slack", and re-adding an exemption with the
    documented `--bless` signature left both sentences standing and the full
    gate green.
    """
    readme = ROOT / "README.md"
    if not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8", errors="replace")

    sizes = []
    for label, _fm, body in machinery_nodes():
        sizes.append((len(body.strip("\n").splitlines()), label))
    sizes.sort()
    largest, largest_label = sizes[-1]
    mid = len(sizes) // 2
    median = (sizes[mid][0] if len(sizes) % 2
              else (sizes[mid - 1][0] + sizes[mid][0]) // 2)

    def grouped(n: int) -> tuple:
        """Every spelling the prose actually uses. The page groups thousands
        with a NARROW NO-BREAK SPACE (U+202F), and a check that only knew about
        an ordinary space reported the figure missing while it was on screen."""
        plain = f"{n:,}"
        return (str(n), plain.replace(",", " "), plain.replace(",", "\u202f"),
                plain.replace(",", "\u2009"), plain.replace(",", "\u00a0"))

    for value, what in ((largest, "the largest routable body"),
                        (median, "the median routable body"),
                        (MACHINERY_BODY_CEILING, "MACHINERY_BODY_CEILING"),
                        (LIFECYCLE_BODY_CEILING, "LIFECYCLE_BODY_CEILING")):
        if not any(form in text for form in grouped(value)):
            fail(f"README.md states no figure matching {what} ({value}). These "
                 f"four numbers are the ones U-15 was about, and the fix that "
                 f"replaced `<500` left them derived by nothing — correct the "
                 f"claim, or stop printing a number the gate does not hold "
                 f"(largest is {largest_label})")

    empty_claim = "consequently **empty**" in text or "is consequently empty" in text
    if empty_claim and EAGER_EXEMPTIONS:
        fail(f"README.md says EAGER_EXEMPTIONS is 'consequently empty' and it "
             f"holds {sorted(EAGER_EXEMPTIONS)}. An exemption is a debt; the "
             f"page that says there is none has to fail when one is added")
    if "no slack" in text and EAGER_EXEMPTIONS:
        fail("README.md claims the EAGER_BUDGET ratchet has 'no slack' while "
             "EAGER_EXEMPTIONS is non-empty")


def check_ci_workflow() -> None:
    """The CI that the README says runs this gate actually exists and runs it.

    U-25 was closed by adding `.github/workflows/gate.yml`, and nothing in the
    gate asserted it: deleting the file left all 42 steps green while README
    went on saying the seed runs its own gate in CI. A claim about a mechanism,
    with the mechanism unpinned, is the shape this release spent eighteen slices
    on.

    What this can NOT assert is that a run has ever gone green — the workflow is
    untracked as of 7.16.0 and has never executed. `gate-registry.py` records
    that, under NON_STEP_GUARDS.
    """
    wf = ROOT / ".github" / "workflows" / "gate.yml"
    if not wf.is_file():
        fail(".github/workflows/gate.yml is missing — README says the seed runs "
             "its own gate in CI, and nothing else in this suite would notice "
             "its absence")
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
                 f"README claims both platforms, and a claim about a matrix "
                 f"needs the matrix")


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
    copies that exist, it does not require any.
    """
    published = ("README.md", "documentation/host-capability-matrix.md")
    live = set(surfaces.values()) | {EAGER_BUDGET}
    # A five-digit figure in a byte context on these pages is a claim about the
    # always-loaded surface, and must equal what the computation above produces.
    # `was`/`before`/`historical`/`budget`/`ceiling`/`max` on the same line mark
    # a figure that is deliberately NOT current — the 138 535 bytes Copilot used
    # to pay, for instance — and those are left alone.
    figure = re.compile(r"\b(\d{2}[  \u2009]?\d{3})\s*(?:B\b|bytes\b)")
    historical = re.compile(r"\b(was|were|before|until|historical|budget|ceiling"
                            r"|max|limit|previously)\b", re.I)
    for rel in published:
        path = ROOT / rel
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if historical.search(line):
                continue
            for m in figure.finditer(line):
                value = int(re.sub(r"[  \u2009]", "", m.group(1)))
                if value in live:
                    continue
                closest = min(live, key=lambda v: abs(v - value))
                fail(f"{rel}: publishes {m.group(1)} bytes as an always-loaded "
                     f"surface, and check_eager_surface computes no such figure "
                     f"(nearest: {closest}). These numbers have one home and it "
                     f"is not this page — correct it, mark it as historical, or "
                     f"stop printing a figure nothing derives")


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

    delegators = set()
    for name, a in agents.items():
        fm = a["fm"]
        tools = fm.get("tools", "")
        has_task = "Task" in tools if isinstance(tools, str) else "Task" in tools
        declares = str(fm.get("can_delegate", "false")).lower() == "true"
        if has_task != declares:
            fail(f"{a['path']}: can_delegate={declares} but Task-in-tools={has_task}")
        if declares:
            delegators.add(name)
            if "max_spawn_depth" not in fm:
                fail(f"{a['path']}: delegator without max_spawn_depth")
            for target in fm.get("delegates_to", []):
                if target not in agents:
                    fail(f"{a['path']}: delegates_to unknown agent '{target}'")

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
    check_install_write_sites()
    check_plan_ledgers()
    check_protocol_reference()
    check_gate_single_home()
    check_file_endings()
    check_canonical_router_blocks()
    check_canonical_plant_root_boundary()
    check_published_body_figures()
    check_ci_workflow()
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
            # check_budget enforces est_tokens within 2x of the measured body
            # (words * BODY_TOKENS_PER_WORD). The seed never checked it, so it
            # could ship a node that fails the very linter it also ships.
            # Mirrored here with the same metric.
            body = p.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
            measured = int(len(body.split()) * 1.35)
            declared = int(est)
            if measured > 2 * declared or declared > 2 * max(measured, 1):
                fail(f"{rel}: est_tokens={declared} but body measures ~{measured} "
                     f"— graph-lint.py would reject this node once installed "
                     f"(must be within 2x)")
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
    # agnosticism gate promises — a real host IP, a pinned CVE, a dangling
    # corpus/template link — over the seed's shipped prose. Subtler
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
    for finding in agn.scan(scan, relative_to=ROOT):
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
    if findings:
        print(f"seed lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("seed lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
