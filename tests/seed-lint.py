#!/usr/bin/env python3
"""seed-lint: one home per fact for the seed's OWN meta-facts.

graph-lint.py guards a grown plant's docs/graph/; this guards the seed tree:
the roster and manifest, the machinery graph, budgets and ceilings, published
figures, rule homes, reference tables, the installer's writes and tiers, the
spec §10 bindings, and the front door (SPEC-0004). Each check_* appends to
`findings` through fail(); tests/test-seed-lint.sh plants one violation per row.

Dependency-free; exit 0 clean, 1 with findings.
"""
import importlib.util
import json
import pathlib
import posixpath
import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The one frontmatter reader, loaded from its canonical home.
_fm_spec = importlib.util.spec_from_file_location(
    "cypress_frontmatter", ROOT / "templates" / "knowledge-graph" / "frontmatter.py")
_frontmatter = importlib.util.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)

KERNEL = ROOT / "core" / "AGENTS.md"
KERNEL_BUDGET = 8_000            # bytes; every session of every plant pays the kernel

# Body ceilings, counted as body_lines() counts them. Raising one is an owner
# decision with a recorded reason; ratchet-lint refuses a silent raise.
MACHINERY_BODY_CEILING = 1_000   # any routable node
LIFECYCLE_BODY_CEILING = 2_500   # graft, grow, harvest (ADR-0007)
LEAF_BODY_CEILING = 170          # SPEC-0005 leaf rule: method, protocols, skills
FRONTMATTER_CEILING = 100        # lines of frontmatter on a routable node

# Every in-scope leaf over LEAF_BODY_CEILING when the check landed. Membership
# is frozen: ratchet-lint refuses a new member, so the set only shrinks.
OVERSIZED_LEAVES = frozenset({
    "core/method/contract-posture.md",
    "core/method/design-posture.md",
    "core/method/engineering-posture.md",
    "core/method/prose-posture.md",
    "core/method/release-posture.md",
    "protocols/canonize.md",
    "protocols/deliver.md",
    "protocols/from-scratch.md",
    "protocols/graft.md",
    "protocols/grill.md",
    "protocols/grow.md",
    "protocols/harvest.md",
    "protocols/test-first.md",
    "protocols/verify.md",
    "skills/adr-writer/SKILL.md",
    "skills/context-router/SKILL.md",
    "skills/holistic-editing/SKILL.md",
    "skills/humanizer/SKILL.md",
    "skills/knowledge-graph/SKILL.md",
    "skills/research-and-ingest/SKILL.md",
    "skills/spec-author/SKILL.md",
})

# How many live contracts in the seed's specs carry no test naming their slug.
# Derived by `spec-lint.py --specs docs/specs --uncovered-budget`, never by hand.
SPEC_UNCOVERED_BUDGET = 1
# How many `green` §10 rows cite a test that does not NAME their contract.
SPEC_ROW_UNBOUND_BUDGET = 0

# The cross-project meta-loop, a closed set fixed by what the three do.
LIFECYCLE_NODES = frozenset({
    "protocols/graft.md",
    "protocols/grow.md",
    "protocols/harvest.md",
})

# What a harness loads on every session before any routing (check_eager_surface).
EAGER_BUDGET = 41_600
# Per-skill boilerplate in a Copilot instruction file, measured from an install.
COPILOT_POINTER_OVERHEAD = 5_644
# Harness -> (recorded bytes, reason). A debt that may only shrink.
EAGER_EXEMPTIONS: dict[str, tuple[int, str]] = {
}

# SPEC-0003 HOOK_TEXT_RESTATES_NO_KERNEL_RULE: bytes of the fixed text
# route-hook.py injects (its "injected text" block). A ceiling that may only fall.
HOOK_TEXT = "integrations/claude-code/route-hook.py"
HOOK_TEXT_MAX_BYTES = 802   # 7.37.0: 724 -> 802, a signed loosening: ENGINE_OLDER is a new literal SPEC-0003 §7 requires (ENGINE_OLDER_THAN_HOOK_IS_NAMED)

# The eight rules' full statements live in exactly these machinery nodes.
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
# "Installed but not spawnable": one home, and every surface that dispatches a
# specialist by name or installs the projection points at the fact key.
REGISTRATION_FACT = "delegation.harness-registration"
REGISTRATION_HOME = "core/method/delegation-bounds.md"
REGISTRATION_REFERRERS = (
    "protocols/grow.md",
    "protocols/graft.md",
    "protocols/from-scratch.md",
    "protocols/initialize.md",
    "protocols/specify.md",
    "protocols/canonize.md",
    "protocols/recover.md",      # the node a failed dispatch actually lands on
    "protocols/deliver.md",      # the gate that must see a declared emulation
    "agents/00-orchestrator.md",
    "agents/growth-orchestrator.md",
    "agents/seed-installer.md",
    "templates/prompts/handback-payload.md",
    "INSTALL_PROMPT.md",
    "GRAFT_PROMPT.md",
    "INSTALL.md",
    "README.md",
    "install.sh",
    "integrations/claude-code/README.md",
    "integrations/claude-code/agent-lint.py",
    "integrations/opencode/README.md",
    "integrations/codex/README.md",
    "integrations/github-copilot/README.md",
    "integrations/prime-agent/README.md",
)
DELEGATION_HUB = "core/method/delegation.md"
# SPEC-0005 §6 "Adopted rule homes" and "Delegation leaves": each key is owned
# by exactly this file and no other node.
ADOPTED_RULE_HOMES = {
    "delegation.roster": DELEGATION_HUB,
    "delegation.routing": DELEGATION_HUB,
    "delegation.spec-authoring": DELEGATION_HUB,
    "delegation.model-classes": "core/method/delegation-model-classes.md",
    "delegation.light-variants": "core/method/delegation-model-classes.md",
    "delegation.step-scope": "core/method/delegation-cycle-economy.md",
    "delegation.briefs": "core/method/delegation-briefs.md",
    "delegation.sequencing": "core/method/delegation-sequencing.md",
    "delegation.lanes": "core/method/delegation-sequencing.md",
    "delegation.bounds": REGISTRATION_HOME,
    REGISTRATION_FACT: REGISTRATION_HOME,
    "delegation.turn": REGISTRATION_HOME,
    "delegation.tracing": REGISTRATION_HOME,
    "delegation.effort": "core/method/delegation-model-classes.md",
    "delegation.model-map": "core/method/delegation-model-classes.md",
    "delegation.effort-scale": "core/method/delegation-cycle-economy.md",
    "delegation.green-self-test": "core/method/delegation-cycle-economy.md",
    "delegation.tip-cadence": "core/method/delegation-cycle-economy.md",
    "delegation.mutation-at-end": "core/method/delegation-cycle-economy.md",
    "delegation.question-file": "core/method/delegation-cycle-economy.md",
    "delegation.ruling-amendment": "core/method/delegation-cycle-economy.md",
    "specify.design-latitude": "protocols/specify-joint-pass.md",
    "specify.joint-pass": "protocols/specify-joint-pass.md",
    "engineering-posture.no-write-inspection": "core/method/host-parity.md",
    "context-router.menu": "skills/context-router/SKILL.md",
    "context-router.graph-over-harness": "skills/context-router/SKILL.md",
    "knowledge-graph.branch-shape": "skills/knowledge-graph/SKILL.md",
    "test-first.no-lint-only-tests": "skills/test-first/SKILL.md",
    "delegation.waves": "core/method/delegation-sequencing.md",
    "stewardship-posture.session-record": "core/method/stewardship-posture.md",
    "canonize.session-record": "protocols/canonize.md",
}
# The trees a plant receives; the text rules read their Markdown.
SHIPPED_RULE_ROOTS = ("core", "agents", "protocols", "skills", "templates",
                      "integrations")
# SPEC-0005 §6 "Bootstrap step 2", compared with whitespace collapsed.
BOOTSTRAP_STEP2 = """2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped."""
# SPEC-0005 §6 "Pending phrases": wording that left an adopted rule reading as
# a proposal. Matched case-insensitively with whitespace collapsed.
PENDING_PHRASES = (
    "recommended rather than required",
    "pending the owner's confirmation",
    "pending the seed owner's confirmation",
    "until it is confirmed",
    "recommends naming the stack expertise",
)
WORD_NUMS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
             "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
             "sixteen": 16, "seventeen": 17}

# SPEC-0004 §6 constants.
BODY_FIGURE_HOME = "DOCUMENTATION.md"
# The project-node body ceiling in templates/knowledge-graph/graph-lint.py; each
# value must still occur there, so the exemption cannot outlive the ceiling.
PROJECT_NODE_LINE_FIGURES = frozenset({150, 170})

findings: list[str] = []


def fail(msg: str) -> None:
    findings.append(msg)


def load_tool(filename: str):
    """Import a seed tool as a module, so a rule has one home. A bare filename
    names a tool under `tools/`; a path is read relative to the seed root."""
    path = ROOT / filename if "/" in filename else ROOT / "tools" / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod          # a @dataclass looks itself up while loading
    spec.loader.exec_module(mod)
    return mod


def load_agent_lint(name: str = "_seedlint_agent_lint"):
    """agent-lint.py exec'd as a module (it is named as a CLI)."""
    path = ROOT / "integrations/claude-code/agent-lint.py"
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), mod.__dict__)
    return mod


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


def parse_frontmatter(path: Path) -> dict:
    """The one frontmatter reader's result, with the body under `_body`."""
    try:
        meta, body = _frontmatter.parse(path.read_text(encoding="utf-8"), path)
    except _frontmatter.FrontmatterError as e:
        fail(str(e))
        return {}
    meta["_body"] = body
    return meta


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


def body_lines(body: str) -> int:
    """A body's line count as every body ceiling reads it: `wc -l` minus the
    frontmatter, with the body's trailing newlines stripped. One count, so the
    number a reader compares against is the one each check uses."""
    return len(body.strip("\n").splitlines())


def description_of(fm: dict) -> str:
    d = fm.get("description")
    return d if isinstance(d, str) else ""


def load_agents() -> dict:
    """name -> {"path", "fm"} for every agents/*.md."""
    agents = {}
    for p in sorted((ROOT / "agents").glob("*.md")):
        fm = parse_frontmatter(p)
        if not fm.get("name"):
            fail(f"{p}: frontmatter has no name")
            continue
        agents[fm["name"]] = {"path": p, "fm": fm}
    return agents

def check_reference_tables() -> None:
    """The three reference documents' primary tables follow the frontmatter,
    their one home: the protocol table (owns, est_tokens) and each protocol
    section's quoted load_when strings, the skills summary table (owns,
    requires, peers, est_tokens) and each agent's section in the agents
    reference (routing_triggers, golden rows, owns, requires, peers,
    delegates_to). Every node has a row, and no row names a missing node."""
    nodes = {fm.get("id"): fm for _l, fm, _b in machinery_nodes()}
    for rel, prefix, cols in (("documentation/protocols-reference.md", "protocol", ("owns",)),
                              ("documentation/skills-and-templates-reference.md", "skill",
                               ("owns", "requires", "peers"))):
        path = ROOT / rel
        if not path.is_file():
            fail(f"{rel} is missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        name = rel.split("/")[1]
        want = {i for i in nodes if i and i.startswith(prefix + ".")}
        seen = set()
        row = re.compile(rf"^\|\s*([a-z-]+)\s*\|\s*`({prefix}\.[a-z-]+)`\s*\|(.*)\|\s*(\d+)\s*\|\s*$")
        for line in text.splitlines():
            m = row.match(line)
            if not m:
                continue
            short, nid, middle, tokens = m.group(1), m.group(2), m.group(3), int(m.group(4))
            fm = nodes.get(nid)
            if fm is None:
                fail(f"{name} lists {nid}, which is not a {prefix} node")
                continue
            seen.add(nid)
            if int(fm["est_tokens"]) != tokens:
                fail(f"{name} row {short}: est_tokens {tokens}, but {nid} declares "
                     f"{fm['est_tokens']} — the node is the home")
            cells = [c.strip() for c in middle.split("|")]
            for idx, key in enumerate(cols):
                listed = {f"{short}{t}" if t.startswith(".") else t for t in
                          re.findall(r"`([a-z.][a-z0-9.-]*)`", cells[idx] if idx < len(cells) else "")}
                declared = set(fm.get(key) or [])
                if listed != declared:
                    fail(f"{name} row {short}: {key} disagrees with {nid} — missing "
                         f"{sorted(declared - listed)}, extra {sorted(listed - declared)}")
        for nid in sorted(want - seen):
            fail(f"{name} has no row for {nid}")
        if prefix == "protocol":
            for sec in re.split(r"^- \*\*id:\*\* `protocol\.", text, flags=re.M)[1:]:
                nid = f"protocol.{sec.split('`', 1)[0]}"
                for field in ("owns", "requires", "peers", "load_when"):
                    n = len(re.findall(rf"^- \*\*{field}:\*\*", sec, re.M))
                    if n > 1:
                        fail(f"{name} section for {nid}: `{field}` is stated {n} times")
                # The quoted load_when strings, in order, as the frontmatter has
                # them; the reference wraps a string across lines, so each
                # whitespace run counts as one space.
                bullet = re.search(r"^- \*\*load_when:\*\*(.*?)(?=^- \*\*|\n\n|\Z)", sec, re.M | re.S)
                if bullet and nid in nodes:
                    listed = [re.sub(r"\s+", " ", q) for q in re.findall(r'"([^"]*)"', bullet.group(1))]
                    declared = [re.sub(r"\s+", " ", str(q)) for q in nodes[nid].get("load_when") or []]
                    if listed != declared:
                        missing = [q for q in declared if q not in listed]
                        extra = [q for q in listed if q not in declared]
                        fail(f"{name} section for {nid}: load_when disagrees with the "
                             f"frontmatter — " + (f"missing {missing}, extra {extra}"
                                                  if missing or extra else "same strings, other order"))

    rel = "documentation/agents-reference.md"
    if not (ROOT / rel).is_file():
        fail(f"{rel} is missing")
        return
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    mod = load_agent_lint("_seedlint_agent_lint_ref")
    golden: dict = {}
    for task, expected, cls in mod.load_golden(ROOT / "agents")[0]:
        golden.setdefault(expected, []).append((task, cls))
    for a in mod.load_agents(ROOT / "agents"):
        i = text.find(f"*Source file: `agents/{a.path.name}`*")
        if i < 0:
            fail(f"agents-reference has no section for {a.path.name}")
            continue
        nxt = text.find("*Source file: `agents/", i + 1)
        section = text[i: nxt if nxt > 0 else len(text)]
        fm = parse_frontmatter(a.path)
        trig = re.search(r"- \*\*routing_triggers:\*\*\n((?:  - \".*\"\n)+)", section)
        listed = re.findall(r'^  - "(.*)"$', trig.group(1), re.M) if trig else []
        if listed != a.triggers:
            fail(f"agents-reference: {a.name} routing_triggers do not match "
                 f"agents/{a.path.name} ({len(listed)} listed, {len(a.triggers)} in frontmatter)")
        deleg = re.search(r"^- \*\*Delegation:\*\*(.*?)(?=^- \*\*|\n\n)", section, re.M | re.S)
        declared = {f"agent.{d}" for d in (fm.get("delegates_to") or [])}
        if deleg and "delegates_to" in deleg.group(1):
            listed = {f"agent.{n}" for n in re.findall(r"`([a-z][a-z-]+)`",
                                                        deleg.group(1).split("delegates_to", 1)[1])}
            if listed != declared:
                fail(f"agents-reference: {a.name} delegates_to disagrees with "
                     f"agents/{a.path.name} — missing {sorted(declared - listed)}, "
                     f"extra {sorted(listed - declared)}")
        elif declared:
            fail(f"agents-reference: {a.name} declares delegates_to in frontmatter "
                 f"but its Delegation bullet does not list it")
        for key in ("owns", "requires", "peers"):
            m = re.search(rf"^- \*\*{key}[^:]*:\*\*(.*?)(?=^- \*\*|\n\n)", section, re.M | re.S | re.I)
            declared = set(getattr(a, key, None) or fm.get(key) or [])
            if m is None:
                if declared:
                    fail(f"agents-reference: {a.name} has no '{key}' bullet, but "
                         f"agents/{a.path.name} declares one")
                continue
            listed = (set() if m.group(1).strip() in ("—", "-", "none", "(none)")
                      else set(re.findall(r"`([a-z][a-z0-9._-]+)`", m.group(1))))
            if listed != declared:
                fail(f"agents-reference: {a.name} {key} disagrees with agents/{a.path.name} "
                     f"— missing {sorted(declared - listed)}, extra {sorted(listed - declared)}")
        gold = re.search(r"- \*\*Golden routing tasks\*\*[^\n]*\n((?:  - \".*\"[^\n]*\n)+)", section)
        shown = re.findall(r'^  - "(.*)" — `(.*)`$', gold.group(1), re.M) if gold else []
        if shown != golden.get(a.name, []):
            fail(f"agents-reference: {a.name} golden rows do not match "
                 f"agents/_routes.golden.tsv ({len(shown)} listed, "
                 f"{len(golden.get(a.name, []))} in the corpus)")


def check_decision_index() -> None:
    """docs/decisions/index.md catalogs every ADR file, and each of its table
    rows links a file that exists."""
    ddir = ROOT / "docs" / "decisions"
    index = ddir / "index.md"
    if not index.is_file():
        fail("docs/decisions/index.md is missing")
        return
    rows = [l for l in index.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    linked = {t for l in rows for t in re.findall(r"\]\((adr-[^)\s]+\.md)\)", l)}
    files = {q.name for q in ddir.glob("adr-*.md")}
    for name in sorted(files - linked):
        fail(f"docs/decisions/index.md has no row for {name}")
    for name in sorted(linked - files):
        fail(f"docs/decisions/index.md links {name}, which is not in docs/decisions/")


def check_gate_single_home() -> None:
    """A lifecycle protocol declares each `<stem>.gate.<slug>` once, in one gate
    table whose rows agree on their column count, and every reference to a gate
    id resolves to a declared row."""
    declared: dict[str, str] = {}
    for label in sorted(LIFECYCLE_NODES):
        path = ROOT / label
        if not path.is_file():
            continue                         # check_body_ceiling walks the real files
        stem = Path(label).stem
        rows, refs, widths = set(), set(), {}
        for line in body_of(path).splitlines():
            ids = re.findall(rf"`({re.escape(stem)}\.gate\.[a-z0-9-]+)`", line)
            if ids and line.lstrip().startswith("|"):
                if ids[0] in rows:
                    fail(f"{label}: gate id `{ids[0]}` is declared twice")
                if ids[0] in declared:
                    fail(f"{label}: gate id `{ids[0]}` is also declared in {declared[ids[0]]}")
                rows.add(ids[0])
                declared.setdefault(ids[0], label)
                widths.setdefault(len(line.strip().strip("|").split("|")), []).append(ids[0])
                refs.update(ids[1:])
            else:
                refs.update(ids)
        if not rows:
            fail(f"{label}: no gate table found — a lifecycle protocol states its "
                 f"gates in one table, by id")
        modal = max(widths, key=lambda w: len(widths[w])) if widths else 0
        for w, gids in sorted(widths.items()):
            if w != modal:
                fail(f"{label}: gate row(s) {sorted(gids)} have {w} columns where the "
                     f"table has {modal} — a pipe inside a cell splits the row")
        for gid in sorted(refs - rows):
            fail(f"{label}: references gate `{gid}`, which no table row declares")



def _canonical_blocks_must_match(homes: tuple, what: str, why: str,
                           names: tuple) -> None:
    """Hold named blocks byte-identical across the files that must share them."""
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
    """One scorer, two routers, and no way for them to drift apart quietly."""
    _canonical_blocks_must_match(
        ("integrations/claude-code/agent-lint.py",
         "templates/knowledge-graph/graph-lint.py"),
        "router",
        "a router that scores differently routes differently, and the last "
        "time these two drifted it went unnoticed for four releases; copy one "
        "over the other deliberately",
        names=("stopwords", "stemmer"))


def check_canonical_plant_root_boundary() -> None:
    """One boundary rule, three walkers, none of them able to drift out of it."""
    _canonical_blocks_must_match(
        ("integrations/claude-code/route-hook.py",
         "integrations/claude-code/status-hook.py",
         "integrations/claude-code/agent-lint.py"),
        "plant-root boundary",
        "a walker without the boundary reads an ancestor repository's "
        "artifact, chosen by directory nesting; all three stop at the same "
        "place or none of them does",
        names=("plant-root boundary",))

def hook_text_bytes() -> int | None:
    """Bytes of route-hook.py's `# --- injected text` block, to the next `# --- `."""
    path = ROOT / HOOK_TEXT
    m = re.search(r"(?ms)^# --- injected text.*?(?=^# --- )",
                  path.read_text(encoding="utf-8")) if path.is_file() else None
    return len(m.group(0).encode("utf-8")) if m else None


def check_hook_text_restates_no_kernel_rule() -> None:
    """SPEC-0003 HOOK_TEXT_RESTATES_NO_KERNEL_RULE: the per-prompt text points at
    the kernel, and its fixed text stays under a byte ceiling that may only fall,
    so a restated kernel rule cannot grow it unseen."""
    size = hook_text_bytes()
    if size is None:
        fail(f"HOOK_TEXT_RESTATES_NO_KERNEL_RULE: {HOOK_TEXT} has no "
             f"`# --- injected text` block, so its fixed text cannot be measured")
    elif size > HOOK_TEXT_MAX_BYTES:
        fail(f"HOOK_TEXT_RESTATES_NO_KERNEL_RULE: {HOOK_TEXT}'s injected text is "
             f"{size} bytes, over HOOK_TEXT_MAX_BYTES ({HOOK_TEXT_MAX_BYTES}). "
             f"Point at the kernel instead of copying it (SPEC-0003 I-8)")



def check_spec_test_mapping() -> None:
    """Every test a spec's §10 cites must exist."""
    specs = ROOT / "docs" / "specs"
    if not specs.is_dir():
        return
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
    """Does this test assert anything, directly or through one helper?"""
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
    """A `green` §10 row must cite a test that NAMES the contract it certifies."""
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
    "tools/frontmatter.py",
)


def check_frontmatter_is_portable_yaml() -> None:
    """Every SHIPPED node's frontmatter is also a strict-YAML document."""
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
    """Every copy of the frontmatter reader is byte-identical to the canonical one."""
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


# SPEC-0001 SINGLE_WRITER: every raw write in install.sh that does not go through
# one of the four named placers, keyed (function, verb): (count, side, why).
# Derived from the script on every run: a new write fails, a removed one is stale.
INSTALL_WRITE_EXCEPTIONS = {
    ("record_instruction_migration", "mv"): (2, "target",
        "moves a symlink or hard link at the note path aside before writing"),
    ("record_instruction_migration", "cat"): (1, "target",
        "writes the migration note's header; no seed-side source to place"),
    ("record_instruction_migration", ">>"): (1, "target",
        "appends one ledger row per replaced kernel"),
    ("place_kernel", "mv"): (1, "target", "backs up the sibling kernel"),
    ("place_kernel", "rm"): (1, "target", "removes the sibling before `ln -s`"),
    ("place_kernel", "ln"): (1, "target", "lays the project-local relative sibling link"),
    ("place_kernel", "cp"): (1, "target", "the no-symlink fallback kernel copy"),
    ("fill_plant_facts", "embedded"): (1, "target",
        "merges the plant's facts into docs/graph/index.md in place"),
    ("retire_copilot_hook_duplicates", "mv"): (1, "target",
        "moves a superseded .github/hooks/ file to a timestamped backup"),
    ("ensure_dir", "mkdir"): (1, "target", "creates a destination directory for a placer"),
    ("fill_plant_facts", ">"): (1, "temp", "stages the embedded heredoc's log lines"),
    ("stage", "mkdir"): (1, "temp", "creates the staging directory under $tmp"),
    ("<main>", "mkdir"): (2, "temp", "creates the verification tree under $tmp"),
    ("generate_slash_commands", "cat"): (1, "temp", "writes a command file into $tmp"),
    ("write_seed_stamp", ">"): (1, "temp", "writes the stamp into $tmp before place_state"),
    ("install_codex", "embedded"): (1, "temp", "renders the config snippet into $tmp"),
    ("render_opencode_agents", "embedded"): (1, "temp",
        "renders each opencode agent with its map model: line into $tmp, then placed"),
    ("install_github_copilot", "embedded"): (4, "temp",
        "renders the four Copilot projections into $tmp, each then placed"),
    ("<main>", "cp"): (1, "temp", "copies the graph into the verification tree under $tmp"),
    ("<main>", ":"): (1, "temp", "truncates a settings file inside $tmp"),
    ("<main>", ">"): (1, "temp", "captures a generator's output into a log under $tmp"),
    ("<main>", "rm"): (2, "temp", "removes the verification tree under $tmp"),
}
TARGET_SIDE_WRITE_EXCEPTIONS = sum(
    n for (n, side, _why) in INSTALL_WRITE_EXCEPTIONS.values() if side == "target")
NAMED_PLACERS = ("place_file", "place_generated", "place_if_missing", "place_state")
# The writes the placers themselves perform, counted like every other write.
PLACER_WRITES = {
    ("place_file", "mv"): (1, "moves the existing destination aside as the backup"),
    ("place_file", "ln"): (1, "creates the seed link under --symlink"),
    ("place_file", "cp"): (1, "copies the seed file into place under --copy"),
    ("place_if_missing", "cp"): (1, "first placement of a file the plant then owns"),
    ("place_state", "cp"): (1, "stages the new stamp beside its destination"),
    ("place_state", "mv"): (1, "renames the staged stamp onto the destination name"),
}


def install_write_sites() -> dict:
    """Derive every raw write in install.sh, attributed to the function holding it."""
    text = (ROOT / "install.sh").read_text(encoding="utf-8", errors="replace")
    redirect = re.compile(r'(?<![<>0-9])>>?\s*(?:""|\$|/|[A-Za-z_])')
    command = re.compile(r'^(cp|mv|ln|rm|tee|touch|install|rsync|dd|sed|mkdir|:)\s')
    prefix = re.compile(r'^(?:if|elif|while|until|then|else|do|done|fi|esac|!|command)\s+')
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
            continue
        else:
            _hd = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)
            opener = re.search(r"(?:^|[\s;&|])<<-?\s*'?([A-Za-z_][A-Za-z0-9_]*)'?", _hd)
            if opener:
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

        if in_string:
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


def _case_arms(src: str, header: str) -> list | None:
    """The arms of the first bash `case … in … esac` whose opening line matches `header`."""
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
    """SPEC-0001 HOST_TIERS_AGREE: the tier arrays in install.sh are the one home;
    each host has one tier, `all` is the maintained two, the dispatch, the
    argument parser and each EVERY_HOST suite name exactly the tiered hosts."""
    install = ROOT / "install.sh"
    if not install.is_file():
        return
    src = install.read_text(encoding="utf-8")
    arrays: dict[str, list[str]] = {}
    for tier, var in (("first-class", "FIRST_CLASS_TOOLS"),
                      ("supported", "SUPPORTED_TOOLS"),
                      ("frozen", "FROZEN_TOOLS")):
        m = re.search(rf"^{var}=\(([^)]*)\)", src, re.M)
        if not m:
            fail(f"install.sh: no {var}=(...) array. The tier assignment has "
                 f"lost its one home")
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


def check_install_write_sites() -> None:
    """SINGLE_WRITER is true of the four placers and a NAMED, COUNTED set of exceptions."""
    sites = install_write_sites()
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
    spec = ROOT / "docs" / "specs" / "SPEC-0001-install-placement.md"
    if spec.is_file():
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

# ADR-0021: the seed's own procedures and tools, which no plant receives.
SEED_ONLY = ("tools/prepare-release.py", "docs/skills/seed-release.md")


def check_seed_only_stays_home() -> None:
    """SPEC-0001 SEED_ONLY_FILES_NEVER_PLACED: each SEED_ONLY file exists and
    neither manifest.json nor install.sh names it; install.sh sources nothing
    under $SEED_ROOT/docs; and the manifest's `tools` map holds exactly the
    tools/ and tests/ files install.sh places, so a seed-only tool cannot ship."""
    manifest = (ROOT / "manifest.json").read_text(encoding="utf-8")
    install = (ROOT / "install.sh").read_text(encoding="utf-8")
    for rel in SEED_ONLY:
        if not (ROOT / rel).is_file():
            fail(f"{rel}: listed in SEED_ONLY and missing from the seed")
        if rel in manifest:
            fail(f"manifest.json names {rel}, a seed-only file (ADR-0021)")
        if rel in install:
            fail(f"install.sh names {rel}, a seed-only file (ADR-0021)")
    for n, line in enumerate(install.splitlines(), 1):
        if re.search(r'\$\{?SEED_ROOT\}?"?/docs\b', line):
            fail(f"install.sh:{n}: sources a file under $SEED_ROOT/docs, the seed's "
                 f"own governance tree, which no plant receives (ADR-0021)")
    # Placement is a `place_file` call; a seed-side run of a tool (install.sh
    # --check executing tools/graft-audit.py from the seed) reads the seed copy
    # and places nothing, so it is not a shipped tool.
    placed = set(re.findall(r'place_file\s+"?\$\{?SEED_ROOT\}?"?/((?:tools|tests)/[^"\s]+)', install))
    listed = set(json.loads(manifest).get("tools", {}))
    if listed != placed:
        fail(f"manifest.json: the `tools` map disagrees with the tools/ and tests/ files "
             f"install.sh places — missing {sorted(placed - listed)}, "
             f"extra {sorted(listed - placed)}")


def check_eager_surface() -> None:
    """Bound what each harness loads on EVERY session, before any routing."""
    surfaces = eager_surfaces(KERNEL.stat().st_size)
    # SPEC-0003 PRIME_EAGER_SURFACE_WITHIN_BUDGET: the prime-agent surface counts
    # the whole overlay, so every section of it is paid here on every Prime
    # Agent session and held to EAGER_BUDGET like every other harness.
    for harness, measured in sorted(surfaces.items()):
        if harness in EAGER_EXEMPTIONS:
            allowed, reason = EAGER_EXEMPTIONS[harness]
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
    overlay = ROOT / "integrations/prime-agent/APPEND_SYSTEM.md"
    overlay_bytes = overlay.stat().st_size if overlay.exists() else 0

    surfaces = {
        "claude-code": kernel_bytes + agent_desc + skill_desc,
        "opencode": kernel_bytes + agent_desc + skill_desc,
        "codex": kernel_bytes + agent_desc + skill_desc,
        "prime-agent": kernel_bytes + skill_desc + overlay_bytes,
        "github-copilot": kernel_bytes + agent_desc + skill_desc + COPILOT_POINTER_OVERHEAD,
    }
    return surfaces


# The two phrases that claim EAGER_EXEMPTIONS holds nothing.
EAGER_EMPTY_PHRASES = ("consequently **empty**", "is consequently empty")
EAGER_NO_SLACK_PHRASE = "no slack"
# A five-digit figure in a byte context is a claim about the always-loaded
# surface; a historical marker on the same line leaves it alone.
EAGER_FIGURE = re.compile(r"\b(\d{2}[  \u2009]?\d{3})\s*(?:B\b|bytes\b)")
EAGER_HISTORICAL = re.compile(r"\b(was|were|before|until|historical|budget|ceiling"
                              r"|max|limit|previously)\b", re.I)


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
    sizes = sorted((body_lines(body), label)
                   for label, _fm, body in machinery_nodes())
    largest, largest_label = sizes[-1]
    mid = len(sizes) // 2
    median = (sizes[mid][0] if len(sizes) % 2
              else (sizes[mid - 1][0] + sizes[mid][0]) // 2)
    return [(largest, "the largest routable body", largest_label),
            (median, "the median routable body", largest_label),
            (MACHINERY_BODY_CEILING, "MACHINERY_BODY_CEILING", largest_label),
            (LIFECYCLE_BODY_CEILING, "LIFECYCLE_BODY_CEILING", largest_label)]


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


def check_opencode_config() -> None:
    """opencode's always-loaded instructions stay in budget and never re-load the
    kernel, its keys are in opencode's closed config schema, and its
    subagent_depth reaches the roster's deepest delegation chain."""
    oc = ROOT / "integrations/opencode/opencode.json"
    if not oc.exists():
        return
    session_budget = 10_000     # bytes: the auto-loaded kernel plus a small overlay
    cfg = json.loads(oc.read_text(encoding="utf-8"))
    instructions = cfg.get("instructions", [])
    total = KERNEL.stat().st_size
    for rel in instructions:
        if rel in ("AGENTS.md", "CLAUDE.md"):
            fail(f"opencode.json: instructions re-declares {rel!r}, which "
                 f"opencode already auto-loads — the kernel would load twice")
        elif not (ROOT / rel).exists():
            fail(f"opencode.json: instructions file not found: {rel}")
        else:
            total += (ROOT / rel).stat().st_size
    if total > session_budget:
        fail(f"opencode.json: always-loaded instructions total {total} bytes "
             f"> {session_budget} budget (auto-loaded AGENTS.md + {instructions})")
    # The schema sets additionalProperties: false; keys pinned, never fetched.
    schema_url = "https://opencode.ai/config.json"
    valid = {"$schema", "agent", "attachment", "autoupdate", "command", "compaction",
             "default_agent", "disabled_providers", "enabled_providers", "enterprise",
             "experimental", "formatter", "instructions", "logLevel", "lsp", "mcp",
             "model", "permission", "plugin", "provider", "references", "server",
             "share", "shell", "skills", "small_model", "snapshot", "subagent_depth",
             "tool_output", "tools", "username", "watcher"}
    if cfg.get("$schema") != schema_url:
        fail(f"opencode.json: $schema must be {schema_url!r} "
             f"(got {cfg.get('$schema')!r}; the old config-schema.json URL 404s)")
    for key in sorted(set(cfg) - valid):
        fail(f"opencode.json: {key!r} is not a key in opencode's config "
             f"schema, which sets additionalProperties:false — the whole "
             f"config is rejected, not just this key")
    depths = [int(a["fm"]["max_spawn_depth"]) for a in load_agents().values()
              if str(a["fm"].get("max_spawn_depth", "")).isdigit()]
    if depths and cfg.get("subagent_depth") != max(depths):
        fail(f"opencode.json: subagent_depth={cfg.get('subagent_depth')!r} "
             f"but the roster's deepest max_spawn_depth is {max(depths)} — "
             f"the seed's delegation topology would be capped on opencode")


# (file, required text, forbidden text, message key) for the two workflows;
# comments are stripped first, except for the platform names.
WORKFLOWS = (
    (".github/workflows/gate.yml", ("tests/run.sh",), ("pip install",), ("ubuntu", "macos")),
    (".github/workflows/release.yml",
     ("contents: write", ".github/RELEASE_NOTES.md", "manifest.json", "gh release create"),
     (), ()),
)


def check_workflows() -> None:
    """The CI gate workflow runs tests/run.sh on a bare python3 on both
    platforms, and the release workflow keeps its tag trigger, write permission,
    staged notes, manifest version check and `gh release create`."""
    for rel, required, forbidden, platforms in WORKFLOWS:
        path = ROOT / rel
        if not path.is_file():
            fail(f"{rel} is missing")
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = "\n".join(re.sub(r"#.*$", "", line) for line in raw.splitlines())
        for want in required:
            if want not in text:
                fail(f"{rel} does not hold `{want}`")
        for bad in forbidden:
            if bad in text:
                fail(f"{rel} has a `{bad}` step; the gate runs on a bare python3")
        for platform in platforms:
            if platform not in raw:
                fail(f"{rel} no longer names {platform}")
        if rel.endswith("release.yml") and not re.search(
                r"tags:\s*\[.*v\[0-9\]\+\.\[0-9\]\+\.\[0-9\]\+.*\]", text):
            fail(f"{rel} no longer triggers on a vX.Y.Z tag push")


def check_body_ceiling() -> None:
    """No routable node grows without a limit."""
    for label, _fm, body in machinery_nodes():
        raw = (ROOT / label).read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
        fm_lines = len(m.group(1).splitlines()) if m else 0
        if fm_lines > FRONTMATTER_CEILING:
            fail(f"{label}: frontmatter is {fm_lines} lines, over the "
                 f"{FRONTMATTER_CEILING}-line ceiling. A node is loaded whole, "
                 f"so metadata is context too — this is not the place to put a "
                 f"body the body ceiling would have refused")
        lines = body_lines(body)
        lifecycle = label in LIFECYCLE_NODES
        ceiling = LIFECYCLE_BODY_CEILING if lifecycle else MACHINERY_BODY_CEILING
        if lines > ceiling:
            which = ("cross-project meta-loop" if lifecycle
                     else "machinery")
            fail(f"{label}: body is {lines} lines, over the "
                 f"{ceiling}-line {which} ceiling — split it "
                 f"along a declared `owns:` fact, or raise the ceiling with a "
                 f"recorded owner decision (never to fit new text)")


def check_leaf_body_ceiling() -> None:
    """SPEC-0005 LEAF_BODY_CEILING_HELD: no leaf outgrows LEAF_BODY_CEILING unless
    OVERSIZED_LEAVES holds it; ratchet-lint refuses a new member."""
    for label, _fm, body in machinery_nodes():
        lines = body_lines(body)
        if not label.startswith("agents/") and lines > LEAF_BODY_CEILING \
                and label not in OVERSIZED_LEAVES:
            fail(f"{label}: body is {lines} lines, over the "
                 f"{LEAF_BODY_CEILING}-line leaf ceiling — divide it into "
                 f"sibling leaves by separable topic, moving the text verbatim; "
                 f"never shorten doctrine to fit, and never add it to "
                 f"OVERSIZED_LEAVES")


def check_adopted_rule_homes() -> None:
    """SPEC-0005 ADOPTED_RULE_HOMES and DELEGATION_SPLIT_INTO_SIBLINGS: each key
    is owned by exactly its one home and by no other node."""
    owners: dict[str, list] = {}
    for label, fm, _body in machinery_nodes():
        for key in fm.get("owns") or []:
            owners.setdefault(key, []).append(label)
    for key, home in ADOPTED_RULE_HOMES.items():
        found = owners.get(key, [])
        if len(found) > 1:
            fail(f"{key}: owned by more than one node ({', '.join(found)}) — "
                 f"its one home is {home}")
        elif found != [home]:
            fail(f"{key}: not owned by {home}, its one home under SPEC-0005 "
                 f"(owned by {found[0] if found else 'no node'})")



# The claim that hooks as a class do not reach subagents: tool hooks fire
# inside a subagent, so the sentence is false wherever it ships. A subject word
# naming one hook or a prompt or session event makes a true, narrower sentence.
HOOK_REACH_PHRASE = re.compile(
    r"(?:\b(?P<qual>[\w-]+)\s+)?\b(?P<hook>hooks?)\s+"
    r"(?:do(?:es)?\s+not|do(?:es)?n['’]t|cannot|can['’]t|never|will\s+not|won['’]t)\s+"
    r"(?:reach|fire|cross|run)(?:es|s)?\b"
    r"|\bno\s+(?P<nohook>hooks?)\s+(?:reach|fire|cross|run)(?:es|s)?\b", re.I)
HOOK_REACH_OBJECT = re.compile(r"sub-?agent|spawn\s+boundary|\bworkers?\b", re.I)
HOOK_REACH_CLAUSE_END = re.compile(r"[.;:!?)]\s|[.;:!?)]$")
# Qualifiers that make the subject the class of hooks the host runs in a subagent.
HOOK_CLASS_QUALIFIERS = {"tool", "settings", "pretooluse", "posttooluse", "subagent",
                         "sub-agent", "configured"}
# Substrings of a qualifier naming one hook or a prompt or session event.
HOOK_NAMED_QUALIFIERS = ("route", "routing", "status", "bound", "prompt", "session",
                         "inject", "stop", "this", "that", "these", "those", "one")


def _hook_reach_claim(line: str, following: str) -> str | None:
    """The matched text when LINE says hooks as a class do not reach subagents."""
    for m in HOOK_REACH_PHRASE.finditer(line):
        qual = (m.group("qual") or "").lower()
        if m.group("hook"):
            if any(w in qual for w in HOOK_NAMED_QUALIFIERS):
                continue
            if m.group("hook").lower() == "hook" and qual not in HOOK_CLASS_QUALIFIERS:
                continue
        rest = line[m.end():] + " " + following.strip()
        end = HOOK_REACH_CLAUSE_END.search(rest)
        rest = rest[:end.start()] if end else rest
        if qual in ("subagent", "sub-agent") or HOOK_REACH_OBJECT.search(rest):
            return m.group(0).strip()
    return None


def _stale_pointer(line: str, _following: str) -> str | None:
    """A line naming method/delegation.md beside a key a sibling now owns."""
    if "method/delegation.md" not in line:
        return None
    for key in re.findall(r"delegation\.[a-z][a-z-]*", line):
        if ADOPTED_RULE_HOMES.get(key, DELEGATION_HUB) != DELEGATION_HUB:
            return f"{key}; point at {ADOPTED_RULE_HOMES[key]}"
    return None


def _files(roots=(), files=(), exts=(".md",), optional=False) -> list:
    """Seed-relative paths: the named files (skipped when absent if optional),
    then every file under the roots with one of the extensions (None: any)."""
    out = [f for f in files if not optional or (ROOT / f).is_file()]
    for top in roots:
        out += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / top).rglob("*")
                      if p.is_file() and (exts is None or p.suffix in exts)
                      and "__pycache__" not in p.parts)
    return out


_SHIPPED = SHIPPED_RULE_ROOTS
_CODE = (".md", ".json", ".py", ".sh")
_KNOWLEDGE = "libraries|sources|{}runbooks|product|architecture|api|data|evaluations|prompts|best-practices|tools"
# One row per rule: (slug, kind, files, pattern, flags). `require`: every file
# holds the pattern; `once`: exactly one line holds it; `forbid`: no line holds
# it (a callable pattern reads the line and the next). `section` narrows a file
# to the first regex match; `collapse` collapses whitespace, `flat` also lowercases.
TEXT_RULES = (
    ("REGISTRATION_POINTER", "require", lambda: _files(files=REGISTRATION_REFERRERS),
     re.escape(REGISTRATION_FACT), {}),
    ("HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP", "once",
     lambda: ["templates/prompts/handback-payload.md"], r"^- effort:",
     {"section": r"(?ms)^```[^\n]*\nHANDBACK\n.*?^```"}),
    ("HANDBACK_CARRIES_EFFORT_AND_EXPERTISE_GAP", "once",
     lambda: ["templates/prompts/handback-payload.md"], r"^- expertise_gap:",
     {"section": r"(?ms)^```[^\n]*\nHANDBACK\n.*?^```"}),
    ("BOOTSTRAP_STEP2_LOADS_A_MENU", "require",
     lambda: ["templates/prompts/graph-session-bootstrap.md"],
     re.escape(" ".join(BOOTSTRAP_STEP2.split()) + " 3. "), {"collapse": True}),
    ("KERNEL_POINTS_AT_THE_SESSION_RECORD", "require", lambda: ["core/AGENTS.md"],
     re.escape("docs/graph/plans/sessions/"), {"section": r"(?ms)^### 3\.2 .*?(?=^### |\Z)", "where": " §3.2"}),
    ("KERNEL_POINTS_AT_THE_SESSION_RECORD", "require", lambda: ["core/AGENTS.md"],
     re.escape("method.stewardship-posture"), {"section": r"(?ms)^### 3\.2 .*?(?=^### |\Z)", "where": " §3.2"}),
    ("ADOPTED_RULES_NOT_PENDING", "forbid", lambda: _files(_SHIPPED),
     "|".join(re.escape(p) for p in PENDING_PHRASES), {"flat": True}),
    ("STALE_POINTER", "forbid",
     lambda: _files(_SHIPPED, ("install.sh", "DOCUMENTATION.md", "CLAUDE.md"), None, True),
     _stale_pointer, {}),
    ("HOOK_REACH", "forbid",
     lambda: _files(("documentation",) + _SHIPPED, ("DOCUMENTATION.md",), _CODE + (".ts",)),
     _hook_reach_claim, {}),
    ("KNOWLEDGE_PATHS", "forbid",
     lambda: _files(_SHIPPED, ("manifest.json", "README.md", "INSTALL.md"), _CODE),
     r"docs/(" + _KNOWLEDGE.format("specs|") + r")/", {}),
    ("KNOWLEDGE_PATHS", "forbid", lambda: _files(("docs",), ("CHANGELOG.md",), _CODE),
     r"docs/(" + _KNOWLEDGE.format("") + r")/", {}),
)


def check_text_rules() -> None:
    """Each TEXT_RULES row, over its files. A finding names the rule, the file
    and, for a forbidden line, its number and the matched text."""
    for slug, kind, files, pattern, opt in TEXT_RULES:
        for rel in files():
            path = ROOT / rel
            if not path.is_file():
                fail(f"{slug}: {rel} is missing")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if opt.get("section"):
                m = re.search(opt["section"], text)
                text = m.group(0) if m else ""
            if opt.get("collapse") or opt.get("flat"):
                text = " ".join(text.split())
            if opt.get("flat"):
                text = text.lower()
            if kind == "require":
                if not re.search(pattern, text):
                    where = opt.get("where", "")
                    fail(f"{slug}: {rel}{where} does not hold "
                         f"{pattern.replace(chr(92), '')!r}")
                continue
            lines = text.splitlines()
            hits = []
            for n, line in enumerate(lines, 1):
                nxt = lines[n] if n < len(lines) else ""
                hit = pattern(line, nxt) if callable(pattern) else \
                    (m.group(0) if (m := re.search(pattern, line)) else None)
                if hit:
                    hits.append((n, hit))
            if kind == "once" and len(hits) != 1:
                fail(f"{slug}: {rel} has {len(hits)} lines matching {pattern!r}, expected one")
            for n, hit in hits if kind == "forbid" else []:
                fail(f"{slug}: {rel}:{n}: {hit!r}")


def check_agent_spawn_grants() -> None:
    """The delegator invariant: can_delegate == (spawn tool in tools)."""
    agents = load_agents()
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


def check_run_sh_shell_contract() -> None:
    """tests/run.sh holds `set -euo pipefail` above its first `add_step` call,
    read as bash applies the `set` lines (grouped letters, `-o name`, `+x`)."""
    path = ROOT / "tests" / "run.sh"
    if not path.is_file():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    call = next((i for i, ln in enumerate(lines, 1) if re.match(r"add_step\s", ln)),
                len(lines) + 1)
    on, last = set(), 0
    for i, ln in enumerate(lines[:call - 1], 1):
        m = re.match(r"set\s+([^#;]*)", ln)
        words = m.group(1).split() if m else []
        last = i if m else last
        while words:
            word = words.pop(0)
            if word[:1] in "-+" and word not in ("-", "--"):
                turn = on.add if word[0] == "-" else on.discard
                for letter in word[1:]:
                    turn(words.pop(0) if letter == "o" and words else
                         {"e": "errexit", "u": "nounset"}.get(letter, letter))
    for name, flag in (("errexit", "-e"), ("nounset", "-u"), ("pipefail", "pipefail")):
        if name not in on:
            fail(f"tests/run.sh:{last or call}: the shell contract above the first "
                 f"`add_step` lacks `{flag}`; without it a red gate can exit 0")



BRIEF_TEMPLATES = ("templates/prompts/investigation-brief.md",
                   "templates/prompts/node-authoring-brief.md",
                   "templates/prompts/growth-scout-brief.md",
                   "templates/prompts/growth-author-brief.md",
                   "templates/prompts/clean-context-validation-brief.md")
# The fenced blocks of graph-session-bootstrap.md every brief embeds verbatim,
# each named by the line that opens it (SPEC-0003 BRIEF_TEMPLATES_BYTE_IDENTICAL).
BRIEF_BLOCKS = ("GRAPH DISCIPLINE", "COMPANION")


def check() -> None:
    """The inline checks: roster and manifest, version, kernel, brief templates,
    the machinery node contract and graph, growth intake, templates, and the
    agnosticism floor."""
    agents = load_agents()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest_agents = {a["name"] for a in manifest.get("agents", [])}
    for name in sorted(set(agents) - manifest_agents):
        fail(f"manifest.json: agents[] is missing '{name}'")
    for name in sorted(manifest_agents - set(agents)):
        fail(f"manifest.json: agents[] lists '{name}' with no file in agents/")
    for section in ("agents", "protocols", "skills", "templates"):
        for entry in manifest.get(section, []):
            if not (ROOT / entry["file"]).exists():
                fail(f"manifest.json: {section} file does not exist: {entry['file']}")
    # ...and the other direction, at the top level of each shipped tree.
    disk = {"protocols": [p for p in (ROOT / "protocols").glob("*.md")],
            "skills": [d / "SKILL.md" for d in (ROOT / "skills").iterdir()
                       if (d / "SKILL.md").is_file()],
            "templates": [p for p in (ROOT / "templates").glob("*.md")]}
    for section, paths in disk.items():
        cataloged = {e["file"] for e in manifest.get(section, [])}
        for rel in sorted(p.relative_to(ROOT).as_posix() for p in paths):
            if rel not in cataloged:
                fail(f"manifest.json: {section}[] does not catalog '{rel}'")

    # -- version single source: manifest == CHANGELOG top entry ---------
    cm = re.search(r"^##\s+(\d+\.\d+\.\d+)\b",
                   (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    if not cm:
        fail("CHANGELOG.md: no '## X.Y.Z' version heading found")
    elif cm.group(1) != manifest.get("version", ""):
        fail(f"version drift: manifest.json is {manifest.get('version', '')!r} but the "
             f"top CHANGELOG entry is {cm.group(1)!r} — bump both together")

    # -- kernel: roster, anchors, budget, canonical reference ------------
    kernel_text = KERNEL.read_text(encoding="utf-8")
    for name in agents:
        if f"`{name}`" not in kernel_text:
            fail(f"core/AGENTS.md: §1 roster does not mention `{name}`")
    for n in range(1, 9):
        if not re.search(rf"^### 3\.{n} ", kernel_text, re.M):
            fail(f"core/AGENTS.md: stable anchor §3.{n} heading is missing")
    size = KERNEL.stat().st_size
    if size > KERNEL_BUDGET:
        fail(f"core/AGENTS.md: {size} bytes exceeds the {KERNEL_BUDGET}-byte budget "
             f"(every session of every plant pays this file)")
    forms = ROOT / "templates/docs/plans/sessions"
    if not (forms.is_dir() and any(p.is_file() for p in forms.iterdir())):
        fail("templates/docs/plans/sessions/: holds no file, so no plant receives "
             "the directory the kernel's §3.2 names")
    if "graph-session-bootstrap.md" not in kernel_text:
        fail("core/AGENTS.md: does not reference the canonical "
             "templates/prompts/graph-session-bootstrap.md block")
    canonical = ROOT / "templates/prompts/graph-session-bootstrap.md"
    canonical_text = canonical.read_text(encoding="utf-8") if canonical.exists() else ""
    briefs = {rel: (ROOT / rel).read_text(encoding="utf-8")
              for rel in BRIEF_TEMPLATES if (ROOT / rel).exists()}
    for rel in BRIEF_TEMPLATES:
        if rel not in briefs:
            fail(f"{rel}: embedding template missing")
    # SPEC-0003 BRIEF_TEMPLATES_BYTE_IDENTICAL (I-2): the embedding templates
    # carry each canonical block byte for byte.
    for block in BRIEF_BLOCKS:
        m = re.search(rf"```\n({re.escape(block)}.*?)```", canonical_text, re.S)
        if not m:
            fail(f"{canonical.relative_to(ROOT)}: no fenced {block} block found")
            continue
        for rel, text in briefs.items():
            if m.group(1) not in text:
                fail(f"{rel}: embedded {block} block has drifted from "
                     f"the canonical copy in {canonical.name} — sync it verbatim")
    # -- spawn tracing: every brief and the handback carry spawn_id -------
    for rel in ("templates/prompts/handback-payload.md",) + BRIEF_TEMPLATES:
        p = ROOT / rel
        if p.exists() and "spawn_id" not in p.read_text(encoding="utf-8"):
            fail(f"{rel}: no spawn_id field — the delegation trace chain "
                 f"(delegation.tracing) breaks at this template")

    # -- machinery nodes: the node contract, one home per fact, the graph --
    owns_home: dict[str, str] = {}
    command_protocols: set[str] = set()
    requires_adj: dict[str, list[str]] = {}
    edge_refs: list[tuple[str, str, str]] = []
    for rel, fm, _body in machinery_nodes():
        if not fm:
            continue
        kind = {"protocols": "protocol", "skills": "skill", "agents": "agent",
                "core": "method"}[rel.split("/")[0]]
        name = fm.get("name") if kind == "agent" else (
            rel.split("/")[1] if kind == "skill" else Path(rel).stem)
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
        prevents = str(fm.get("prevents", ""))
        if prevents and len(prevents) < 60:
            fail(f"{rel}: prevents: too short to name a failure ({len(prevents)} chars)")
        title_tail = str(fm.get("title", "")).split("—")[-1].strip().lower()
        if prevents and title_tail and title_tail in prevents.lower():
            fail(f"{rel}: prevents: restates title: rather than naming the "
                 f"failure the node's absence produces")
        if kind != "agent" and not fm.get("load_when"):
            fail(f"{rel}: machinery node missing 'load_when'")
        if kind == "agent" and not fm.get("routing_triggers"):
            fail(f"{rel}: agent node needs routing_triggers (its load_when source)")
        est = str(fm.get("est_tokens", ""))
        if not est.isdigit():
            fail(f"{rel}: est_tokens must be an integer (got {est!r})")
        else:
            # graph-lint.py's check_budget in a plant: the whole file, within 2x.
            measured = int(len((ROOT / rel).read_text(encoding="utf-8").split()) * 1.35)
            declared = int(est)
            if measured > 2 * declared or declared > 2 * max(measured, 1):
                fail(f"{rel}: est_tokens={declared} but the file measures "
                     f"~{measured} (frontmatter and body) — graph-lint.py would "
                     f"reject this node once installed (must be within 2x)")
        for fact in fm.get("owns", []) or []:
            if fact in owns_home:
                fail(f"{rel}: fact-key {fact!r} already owned by {owns_home[fact]} "
                     f"— one home per fact")
            owns_home[fact] = rel
        cmd = fm.get("command")
        if kind == "protocol" and cmd == "true":
            command_protocols.add(name)
        elif kind != "protocol" and cmd is not None:
            fail(f"{rel}: 'command:' is a protocol-only field (found on a {kind} node)")
        requires_adj[want_id] = list(fm.get("requires") or [])
        edge_refs += [(rel, "requires", t) for t in fm.get("requires") or []]
        edge_refs += [(rel, "peers", t) for t in fm.get("peers") or []]
    for rule, home in RULE_HOMES.items():
        if rule not in owns_home:
            fail(f"{home}: does not own {rule!r} — the kernel anchor points at it")
        elif owns_home[rule] != home:
            fail(f"{rule}: owned by {owns_home[rule]}, expected {home}")
    # User-sovereign protocols are never slash commands.
    for sovereign in ("graft", "grow", "harvest"):
        if not (ROOT / "protocols" / f"{sovereign}.md").is_file():
            fail(f"protocols/{sovereign}.md is missing — the user-sovereign "
                 f"guard below would pass vacuously without it")
        if sovereign in command_protocols:
            fail(f"protocols/{sovereign}.md: must not declare 'command: true' — "
                 f"{sovereign} is user-sovereign, a slash command on no harness")
    if not command_protocols:
        fail("no protocol declares 'command: true' — the slash-command surface would be empty")
    for rel, etype, target in edge_refs:
        if target not in requires_adj:
            fail(f"{rel}: {etype} → unknown machinery node {target!r}")
    colour = {n: 0 for n in requires_adj}          # 0 white, 1 grey, 2 black

    def _visit(n: str, stack: list[str]) -> None:
        colour[n] = 1
        for m in requires_adj.get(n, []):
            if colour.get(m) == 1:
                fail(f"requires cycle in machinery graph: {' → '.join(stack[stack.index(m):] + [m])}")
            elif colour.get(m) == 0:
                _visit(m, stack + [m])
        colour[n] = 2
    for n in list(requires_adj):
        if colour[n] == 0:
            _visit(n, [n])

    # -- growth intake: a collection the installer creates is one a scout gathers for
    audit = load_tool("growth-audit.py")
    rows = audit.required_collections(ROOT)
    collections = sorted({r.split("/")[0] + "/" if "/" in r else r for r in rows})
    # Outputs of the growth run, not findings about the source: never scouted.
    unscouted = {"sources/", "tools/", "plans/", "changelog.md"}
    ledger = (ROOT / "templates/prompts/growth-evidence-ledger.md").read_text(encoding="utf-8")
    headings = "\n".join(l for l in ledger.splitlines() if l.startswith("## "))
    for c in collections:
        if c not in unscouted and c not in headings:
            fail(f"templates/prompts/growth-evidence-ledger.md: no section "
                 f"feeds {c!r}, so no scout gathers the evidence an author "
                 f"would write it from")
    # The forms a plant authors an agent and an expertise node FROM carry the
    # keys the coverage gate asks for, in their frontmatter.
    for rel, keys in (
        ("templates/agent.template.md",
         (r"origin: project", r"plant_knowledge:", r"id: agent\.", r"kind: agent")),
        ("templates/docs/nodes/_expertise.template.md",
         (r"id: expertise\.", r"kind: expertise", r"origin: project",
          r"composes:", r"libraries:")),
    ):
        head = frontmatter_block(ROOT / rel)
        for key in keys:
            if not re.search(rf"^{key}", head, re.M):
                fail(f"{rel}: its frontmatter carries no {key!r}, so a node "
                     f"authored from it cannot answer the coverage gate")
    for name, meta in agents.items():
        for want in meta["fm"].get("plant_knowledge", []) or []:
            if want not in collections and want not in rows \
                    and not (ROOT / "templates/docs" / want).is_file():
                fail(f"agents/: {name} declares plant_knowledge {want!r}, "
                     f"which is not a collection the seed installs")

    # -- agnosticism floor and dangling corpus/template references --------
    agn_roots = ("core", "agents", "protocols", "skills", "templates",
                 "library-corpus", "legal-corpus", "tool-corpus",
                 "agent-corpus", "skill-corpus")
    scan = [ROOT / r for r in agn_roots]
    scan += [ROOT / f for f in ("manifest.json", "README.md", "CHANGELOG.md")
             if (ROOT / f).exists()]
    agn = load_tool("agnosticism-lint.py")
    agn_scan = list(scan)
    agn_scan += [ROOT / r for r in ("docs/plans", "docs/skills", "tools") if (ROOT / r).is_dir()]
    agn_scan += [ROOT / f for f in ("install.sh", "DOCUMENTATION.md", "INSTALL.md")
                 if (ROOT / f).exists()]
    for finding in agn.scan(agn_scan, globs=("*.md", "*.py", "*.sh"),
                            relative_to=ROOT):
        fail(f"{finding.path}: {finding.message}")
    ref_re = re.compile(r"\b(?:library-corpus|legal-corpus|tool-corpus|"
                        r"agent-corpus|skill-corpus|templates)/[A-Za-z0-9_./-]+\.md\b")
    for p in agn.iter_files(scan):
        rel = p.relative_to(ROOT)
        if rel.as_posix() == "CHANGELOG.md":
            continue                         # dated history names files as they were
        for ref in ref_re.findall(p.read_text(encoding="utf-8")):
            if "<" in ref or "*" in ref or "{" in ref:
                continue
            if not (ROOT / ref).exists():
                fail(f"{rel}: dangling corpus/template reference '{ref}'")


STACK_ID = re.compile(r"library-corpus/[^/\s]+/[^/\s]+")


def check_corpus_stack() -> None:
    """A stack-keyed page points somewhere (skill-corpus/README.md, "Stack-keyed
    pages"; tool-corpus/README.md, "The stack field"). A
    `skill-corpus/<key>/<name>.md` page sits under a key the library corpus
    defines and carries `stack:`; a `stack:` on a skill or tool page names only
    library-corpus pages that exist, each as its corpus id
    `library-corpus/<key>/<name>`. A flat skill page has no key, so it carries
    no `stack:`. One finding per page holds all of its problems."""
    lib = ROOT / "library-corpus"
    keys = {d.name for d in lib.iterdir() if d.is_dir()} if lib.is_dir() else set()
    for corpus in ("skill-corpus", "tool-corpus"):
        base = ROOT / corpus
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            parts = p.relative_to(base).parts
            if parts == ("README.md",):
                continue
            rel = p.relative_to(ROOT).as_posix()
            text = p.read_text(encoding="utf-8")
            meta = {}
            if text.startswith("---\n"):
                try:
                    meta, _ = _frontmatter.parse(text, p)
                except _frontmatter.FrontmatterError as e:
                    fail(str(e))
                    continue
            stack = meta.get("stack")
            stack = [] if stack in (None, "") else stack if isinstance(stack, list) else [stack]
            problems = []
            if corpus == "skill-corpus":
                if len(parts) > 2:
                    problems.append(f"nested {len(parts) - 1} directories deep; a stack-keyed "
                                    f"page sits one key down, at skill-corpus/<key>/<name>.md")
                if len(parts) >= 2 and parts[0] not in keys:
                    problems.append(f"its key '{parts[0]}' is not a library-corpus key "
                                    f"(library-corpus/ defines {', '.join(sorted(keys)) or 'none'})")
                if len(parts) >= 2 and not stack:
                    problems.append("carries no stack: field, so no plant's inventory can withdraw it")
                if len(parts) == 1 and stack:
                    problems.append("a flat page carries stack:; a stack-keyed page lives under its "
                                    "key, at skill-corpus/<key>/<name>.md")
            for s in stack:
                if not isinstance(s, str) or not STACK_ID.fullmatch(s):
                    problems.append(f"stack: entry {s!r} is not a library corpus id "
                                    f"library-corpus/<key>/<name>")
                elif not (ROOT / f"{s}.md").is_file():
                    problems.append(f"stack: names {s}, which is not a library-corpus page")
            if problems:
                fail(f"{rel}: " + "; ".join(problems))


# --- SPEC-0004: the front door ------------------------------------------------
# README.md, DOCUMENTATION.md, documentation/*.md, INSTALL.md and each
# integrations/*/README.md, read by one small parser (§6 "Body text and units").

FD_INSTALL_SECTION = "## What installing does to your repository"
FD_INSTALL_TARGETS = ("CLAUDE.md", "AGENTS.md", ".claude/", "docs/graph/", ".cypress/seed.json")
FD_BACKUP_ROW = "enf-backup-before-replace"
FD_SEED_SOURCE_PREFIXES = ("core/", "agents/", "skills/", "integrations/", "protocols/",
                           "templates/", "tools/", "tests/")
FD_GLOSSARY_HEADING = "## 15. Glossary"
FD_ENFORCEMENT_HEADING = "## 17. What is enforced, and how"
FD_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
FD_ANCHOR_TAG = re.compile(r'<a id="([^"]*)"></a>')
FD_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
FD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^()\s]*)\)")
FD_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FD_TABLE_SEP = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
FD_LINE_FIGURE = re.compile(r"(?<![\w.])\d[\d    ,]*\s*-?\s*lines?\b")
_fd_docs: dict = {}


def fd_fail(slug: str, path: str, line: int, message: str) -> None:
    findings.append(f"front-door: {slug}: {path}:{line}: {message}")


def fd_text(slug: str, rel: str) -> str | None:
    """A front-door input's text, or None after a line-0 finding."""
    try:
        return (ROOT / rel).read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        fd_fail(slug, rel, 0, f"missing required input: cannot read it ({type(e).__name__})")
        return None


def fd_doc(slug: str, rel: str):
    """(lines, kinds): each line `body`, `blank`, `fence`, `heading`, `comment`
    or `anchor`. None after fd_text's finding."""
    if rel not in _fd_docs:
        text = fd_text(slug, rel)
        if text is None:
            return None
        lines, kinds, fence, comment = text.splitlines(), [], None, False
        for line in lines:
            s, m = line.strip(), FD_FENCE.match(line)
            if fence:
                kinds.append("fence")
                fence = None if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line[m.end():].strip() else fence
            elif m:
                fence = m.group(1)
                kinds.append("fence")
            elif comment or s.startswith("<!--"):
                kinds.append("comment")
                comment = "-->" not in s
            elif FD_ANCHOR_TAG.fullmatch(s):
                kinds.append("anchor")
            else:
                kinds.append("heading" if re.match(r"#{1,6}(\s|$)", line) else
                             "body" if s else "blank")
        _fd_docs[rel] = (lines, kinds)
    return _fd_docs[rel]


def fd_units(doc, lo: int = 0, hi: int | None = None) -> list:
    """[(line, text)]: a paragraph, a list item or one table body row."""
    lines, kinds = doc
    units, cur, cur_row = [], None, False
    for i in range(lo, len(lines) if hi is None else hi):
        if kinds[i] != "body" or FD_TABLE_SEP.match(lines[i].strip()):
            cur = None
            continue
        row = lines[i].lstrip().startswith("|")
        if cur is None or row or cur_row or FD_LIST_ITEM.match(lines[i]):
            cur = [i + 1, [lines[i]]]
            units.append(cur)
        else:
            cur[1].append(lines[i])
        cur_row = row
    return [(n, "\n".join(ls)) for n, ls in units]


def fd_code_spans(text: str) -> list:
    return [(m.start(), m.end(), m.group(2)) for m in FD_CODE_SPAN.finditer(text)]


def fd_links(text: str) -> list:
    """[(target, start, text_end, end)] per inline link outside a code span."""
    spans = fd_code_spans(text)
    return [(m.group(2), m.start(), m.end(1), m.end()) for m in FD_LINK.finditer(text)
            if not any(a <= m.start() < b for a, b, _c in spans)]


def fd_mask(text: str) -> str:
    """Code spans and link targets blanked, positions kept."""
    chars = list(text)
    cuts = [(a, b) for a, b, _c in fd_code_spans(text)] + \
        [(te + 1, e) for _t, _s, te, e in fd_links(text)]
    for a, b in cuts:
        chars[a:b] = [c if c == "\n" else " " for c in chars[a:b]]
    return "".join(chars)


def fd_line_of(unit_line: int, text: str, pos: int) -> int:
    return unit_line + text.count("\n", 0, pos)


def fd_resolve(from_rel: str, target: str):
    """(file relative to the seed root, fragment), or None for an external link."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
        return None
    path, _, frag = target.partition("#")
    if not path:
        return from_rel, frag
    return posixpath.normpath(posixpath.join(posixpath.dirname(from_rel), path)), frag


def fd_region(doc, heading: str):
    """(first, end) line indexes from `heading` to the next `##`, or None."""
    lines, kinds = doc
    at = [i for i, line in enumerate(lines) if line.rstrip() == heading and kinds[i] == "heading"]
    if not at:
        return None
    return at[0], next((j for j in range(at[0] + 1, len(lines))
                        if kinds[j] == "heading" and lines[j].startswith("## ")), len(lines))


def fd_anchors(doc) -> dict:
    """{id: [lines]} of the explicit anchors outside fenced blocks."""
    out: dict = {}
    for i, line in enumerate(doc[0]):
        if doc[1][i] != "fence":
            for m in FD_ANCHOR_TAG.finditer(line):
                out.setdefault(m.group(1), []).append(i + 1)
    return out


def fd_path_like(token: str) -> bool:
    bare = re.sub(r":\d+(?:-\d+)?$", "", token)
    return "/" in bare or bare.endswith((".md", ".py", ".sh", ".json", ".ts", ".tsv",
                                         ".yml", ".toml"))


def fd_seed_path_problem(token: str) -> str | None:
    """Why a seed path does not resolve (§6 seed-path rule), or None."""
    m = re.match(r"^(.*?)(?::(\d+)(?:-(\d+))?)?$", token)
    path, lo, hi = m.group(1), m.group(2), m.group(3)
    pattern = re.sub(r"<[^>]*>", "*", path).strip("/") or "."
    brace = re.search(r"\{([^{}]*)\}", pattern)
    for exp in ([pattern[:brace.start()] + alt + pattern[brace.end():]
                 for alt in brace.group(1).split(",")] if brace else [pattern]):
        hits = sorted(ROOT.glob(exp)) if any(c in exp for c in "*?[") else (
            [ROOT / exp] if (ROOT / exp).exists() else [])
        if not hits:
            return f"`{token}` does not resolve under the seed root"
        if lo is not None:
            if not hits[0].is_file():
                return f"`{token}` names lines of something that is not a file"
            count = len(hits[0].read_text(encoding="utf-8", errors="replace").splitlines())
            if not (int(lo) <= int(hi or lo) <= count):
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


def fd_front_door_files() -> list:
    """SPEC-0004 §2: README.md, DOCUMENTATION.md, documentation/*.md,
    INSTALL.md and integrations/*/README.md."""
    return (["README.md", "DOCUMENTATION.md"]
            + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "documentation").glob("*.md"))
            + ["INSTALL.md"]
            + sorted(p.relative_to(ROOT).as_posix()
                     for p in (ROOT / "integrations").glob("*/README.md")))


def check_fd_install_section_names_target_paths() -> None:
    """SPEC-0004 INSTALL_SECTION_NAMES_TARGET_PATHS: the install section names
    what lands in a project, by the installer's own paths, and never the
    seed's source tree."""
    slug = "INSTALL_SECTION_NAMES_TARGET_PATHS"
    install = fd_text(slug, "install.sh")
    doc = fd_doc(slug, "README.md")
    region = fd_region(doc, FD_INSTALL_SECTION) if doc else None
    if region is None:
        if doc:
            fd_fail(slug, "README.md", 0, f"missing required input: no section `{FD_INSTALL_SECTION}`")
        return
    units = fd_units(doc, region[0] + 1, region[1])
    tokens = [(fd_line_of(n, t, a), c.strip()) for n, t in units for a, _b, c in fd_code_spans(t)]
    for target in FD_INSTALL_TARGETS:
        if target not in {c for _n, c in tokens}:
            fd_fail(slug, "README.md", region[0] + 1, f"does not name the target `{target}`")
    for n, token in tokens:
        if token.startswith(FD_SEED_SOURCE_PREFIXES):
            fd_fail(slug, "README.md", n, f"`{token}` is a seed-source path; "
                                          f"the section names what lands in a project")
        elif install is not None and token != "install.sh" and fd_path_like(token):
            problem = fd_install_literal_problem(token, install)
            if problem:
                fd_fail(slug, "README.md", n, problem)
    if not any(".cypress/seed.json" in t and any(
            fd_resolve("README.md", g) == ("DOCUMENTATION.md", FD_BACKUP_ROW)
            for g, *_r in fd_links(t)) for _n, t in units):
        fd_fail(slug, "README.md", region[0] + 1, f"no unit names `.cypress/seed.json` and "
                                                  f"links `DOCUMENTATION.md#{FD_BACKUP_ROW}`")


def check_fd_front_door_anchors_resolve() -> None:
    """SPEC-0004 FRONT_DOOR_ANCHORS_RESOLVE: every term, row and region link
    lands on exactly one explicit anchor, and README's relative links resolve.
    Two rows ride with it: GLOSSARY_PATHS_EXIST (Implemented at paths) and
    MECHANISM_CLAIMS_TRACED (each enforcement row's Artifact paths exist)."""
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
        for n, text in fd_units(doc) if doc else []:
            for target, start, *_r in fd_links(text):
                hit = fd_resolve(rel, target)
                if hit is None:
                    continue
                path, frag = hit
                line = fd_line_of(n, text, start)
                if rel == "README.md" and not (ROOT / path).exists():
                    fd_fail(slug, rel, line, f"`{target}` does not resolve to a file under the "
                                             f"seed root")
                elif frag.startswith(("term-", "enf-")) or frag in ("glossary", "enforcement"):
                    target_doc = fd_doc(slug, path) if (ROOT / path).is_file() else None
                    count = len(fd_anchors(target_doc).get(frag, [])) if target_doc else 0
                    if count != 1:
                        fd_fail(slug, rel, line, f"`{target}`: #{frag} names {count} explicit "
                                                 f"anchors in {path}, not one")
    if docu is not None:
        fd_glossary_paths_exist(docu)
        fd_mechanism_paths_exist(docu)


def fd_glossary_paths_exist(doc) -> None:
    """GLOSSARY_PATHS_EXIST: every Implemented at path resolves in the seed;
    inside an "An install produces" clause, paths and bare identifiers are the
    installer's; a field with no path begins `n/a`."""
    slug = "GLOSSARY_PATHS_EXIST"
    lines, kinds = doc
    region = fd_region(doc, FD_GLOSSARY_HEADING)
    if region is None:
        fd_fail(slug, "DOCUMENTATION.md", 0, f"missing required input: no `{FD_GLOSSARY_HEADING}`")
        return
    install = fd_text(slug, "install.sh") or ""
    functions = set(re.findall(r"(?m)^([a-z_][a-z0-9_]*)\(\)", install))
    fields, head, cur = [], "", None
    for i in range(region[0] + 1, region[1]):
        line = lines[i]
        if kinds[i] == "heading" and line.startswith("### "):
            head, cur = line[4:].strip(), None
        elif line.startswith("- **Implemented at:**"):
            cur = [head, i + 1, line[len("- **Implemented at:**"):].strip()]
            fields.append(cur)
        elif cur is not None and line[:1] in (" ", "\t") and line.strip():
            cur[2] += " " + line.strip()
        else:
            cur = None
    for head, n, value in fields:
        masked = fd_mask(value)
        clause = masked.find("An install produces")
        end = re.search(r"[.!?](?=\s+[A-Z\[`*(]|\s*$)", masked[clause:]) if clause >= 0 else None
        clause_end = clause + end.end() if end else len(value)
        spans = fd_code_spans(value)
        if not any(fd_path_like(c.strip()) for _a, _b, c in spans) and not value.startswith("n/a"):
            fd_fail(slug, "DOCUMENTATION.md", n,
                    f"`{head}` Implemented at names no path and does not begin `n/a`")
        for a, _b, code in spans:
            token = code.strip()
            inside = 0 <= clause <= a < clause_end
            if inside and fd_path_like(token):
                problem = fd_install_literal_problem(token, install)
            elif inside and re.fullmatch(r"[a-z_][a-z0-9_]*", token):
                problem = None if token in functions else \
                    f"`{token}` is not a function install.sh defines"
            elif fd_path_like(token):
                problem = fd_seed_path_problem(token)
            else:
                problem = None
            if problem:
                fd_fail(slug, "DOCUMENTATION.md", n, f"`{head}`: {problem}")


def fd_mechanism_paths_exist(doc) -> None:
    """MECHANISM_CLAIMS_TRACED: every path-like token in an enforcement row's
    Artifact cell (the second column) resolves under the seed root."""
    slug = "MECHANISM_CLAIMS_TRACED"
    region = fd_region(doc, FD_ENFORCEMENT_HEADING)
    if region is None:
        fd_fail(slug, "DOCUMENTATION.md", 0,
                f"missing required input: no `{FD_ENFORCEMENT_HEADING}`")
        return
    lines, kinds = doc
    rows = [i for i in range(region[0] + 1, region[1])
            if kinds[i] == "body" and lines[i].lstrip().startswith("|")]
    for i in rows[2:]:                                  # past the header and delimiter rows
        cells = re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))
        for _a, _b, code in fd_code_spans(cells[1] if len(cells) > 1 else ""):
            problem = fd_path_like(code.strip()) and fd_seed_path_problem(code.strip())
            if problem:
                fd_fail(slug, "DOCUMENTATION.md", i + 1, f"Artifact: {problem}")


def front_door_checks() -> None:
    """SPEC-0004's install-section and anchors checks."""
    check_fd_install_section_names_target_paths()
    check_fd_front_door_anchors_resolve()


def check_published_figures() -> None:
    """Every figure the prose publishes derives from the tree. SPEC-0004
    EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED and BODY_FIGURES_HAVE_A_REQUIRED_HOME
    are its front-door scope rows; the roster, skill and protocol counts, the
    documented version, and each harness's own eager figure are its other rows."""
    surfaces = eager_surfaces(KERNEL.stat().st_size)
    live = set(surfaces.values()) | {EAGER_BUDGET}
    eager, body = "EAGER_FIGURES_CHECKED_WHEREVER_PUBLISHED", "BODY_FIGURES_HAVE_A_REQUIRED_HOME"
    home = fd_text(body, BODY_FIGURE_HOME)
    for value, what, _largest in routable_body_figures() if home is not None else []:
        if not any(re.search(rf"(?<![\d.]){re.escape(form)}(?!\d)", home)
                   for form in grouped_forms(value)):
            fd_fail(body, BODY_FIGURE_HOME, 0, f"missing required input: states no figure "
                                               f"matching {what} ({value})")
    graph_lint = "templates/knowledge-graph/graph-lint.py"
    source = fd_text(body, graph_lint)
    for value in sorted(PROJECT_NODE_LINE_FIGURES) if source is not None else []:
        if not re.search(rf"(?<![\w.]){value}(?![\w.])", source):
            fd_fail(body, graph_lint, 0, f"holds no {value} literal, so PROJECT_NODE_LINE_FIGURES "
                                         f"exempts a ceiling that no longer exists")
    for rel in fd_front_door_files():
        doc = fd_doc(eager, rel)
        if doc is None:
            continue
        text = "\n".join(doc[0])
        for n, m, value in stale_eager_figures(text, live):
            closest = min(live, key=lambda v: abs(v - value))
            fd_fail(eager, rel, n, f"publishes {m.group(1)} bytes as an always-loaded surface, "
                                   f"and check_eager_surface computes no such figure "
                                   f"(nearest: {closest})")
        for n, m, _value, harness in misattributed_eager_figures(text, surfaces):
            fail(f"{rel}:{n}: publishes {m.group(1)} bytes for {harness}, and "
                 f"check_eager_surface computes {surfaces[harness]} for that harness")
        for n, line in enumerate(doc[0], 1):
            if EAGER_EXEMPTIONS and any(p in line for p in EAGER_EMPTY_PHRASES):
                fd_fail(body, rel, n, f"says EAGER_EXEMPTIONS is consequently empty, and it "
                                      f"holds {sorted(EAGER_EXEMPTIONS)}")
            if EAGER_EXEMPTIONS and EAGER_NO_SLACK_PHRASE in line:
                fd_fail(body, rel, n, "says the EAGER_BUDGET ratchet has 'no slack' while "
                                      "EAGER_EXEMPTIONS is non-empty")
        for n, unit in fd_units(doc) if rel != BODY_FIGURE_HOME else []:
            masked = fd_mask(unit)
            if not re.search(r"(?i)\bbod(?:y|ies)\b", masked):
                continue
            for m in FD_LINE_FIGURE.finditer(masked):
                if int(re.sub(r"\D", "", m.group(0))) not in PROJECT_NODE_LINE_FIGURES:
                    fd_fail(body, rel, fd_line_of(n, unit, m.start()),
                            f"a body figure '{m.group(0).strip()}' outside "
                            f"{BODY_FIGURE_HOME}, its one home")
    check_published_counts()


def check_published_counts() -> None:
    """The roster, coordinator, skill and protocol counts, and the documented
    version, as the shipped prose states them."""
    agents = load_agents()
    delegators = {n for n, a in agents.items()
                  if str(a["fm"].get("can_delegate", "false")).lower() == "true"}
    n_skills = sum(1 for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").is_file())
    n_protocols = sum(1 for _p in (ROOT / "protocols").glob("*.md"))
    version = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]
    word = "|".join(WORD_NUMS)

    def num(tok: str) -> int:
        return int(tok) if tok.isdigit() else WORD_NUMS[tok.lower()]
    files = ["README.md", "core/AGENTS.md", "INSTALL.md", "manifest.json", "DOCUMENTATION.md"]
    files += sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob("integrations/*/README.md"))
    files += sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob("documentation/*.md"))
    for path in (f for f in files if (ROOT / f).exists()):
        text = (ROOT / path).read_text(encoding="utf-8")
        for m in re.finditer(rf"\b(\d+|{word})[- ]agent team\b", text, re.I):
            if num(m.group(1)) != len(agents):
                fail(f"{path}: claims a {m.group(1)}-agent team; agents/ has {len(agents)}")
        for m in re.finditer(rf"\b(\d+|{word})\s+(?:[a-z-]+\s+){{0,2}}specialist agents\b",
                             text, re.I):
            if num(m.group(1)) != len(agents):
                fail(f"{path}: claims {m.group(0)!r}; agents/ has {len(agents)}")
        for m in re.finditer(r"[Vv]ersion(?: documented)?[:*\s]+\**(\d+\.\d+\.\d+)", text):
            if path in ("DOCUMENTATION.md", "documentation/README.md") and m.group(1) != version:
                fail(f"{path}: documents version {m.group(1)}; manifest.json is {version}")
        for m in re.finditer(rf"\b(\d+|{word})\s+(?:opus\s+)?coordinator", text, re.I):
            if num(m.group(1)) != len(delegators):
                fail(f"{path}: claims {m.group(1)} coordinators; frontmatter has "
                     f"{len(delegators)}: {sorted(delegators)}")
        for m in re.finditer(rf"\b(\d+|{word})\s+skills\b", text, re.I):
            if num(m.group(1)) != n_skills:
                fail(f"{path}: claims {m.group(1)} skills; skills/ has {n_skills}")
        for m in re.finditer(rf"\b(\d+|{word})\s+protocols\b", text, re.I):
            if num(m.group(1)) != n_protocols:
                fail(f"{path}: claims {m.group(1)} protocols; protocols/ has {n_protocols}")


CHECKS = (check, check_corpus_stack, check_agent_spawn_grants, check_body_ceiling, check_leaf_body_ceiling,
          check_adopted_rule_homes, check_text_rules, check_eager_surface,
          check_opencode_config, check_spec_test_mapping, check_spec_rows_name_their_contract,
          check_frontmatter_reader_is_one_reader, check_frontmatter_is_portable_yaml,
          check_install_write_sites, check_seed_only_stays_home, check_host_tiers,
          check_reference_tables, check_decision_index, check_gate_single_home, check_canonical_router_blocks,
          check_canonical_plant_root_boundary, check_hook_text_restates_no_kernel_rule,
          check_published_figures, check_workflows, check_run_sh_shell_contract,
          front_door_checks)


def main() -> int:
    # Each check runs on its own, so one that raises (an unreadable file, a
    # LintError from exec'd agent-lint) is reported and cannot hide the rest.
    for chk in CHECKS:
        try:
            chk()
        except Exception as e:                   # noqa: BLE001 — reported, never swallowed
            findings.append(f"seed-lint: {chk.__name__} could not complete: "
                            f"{type(e).__name__}: {e}")
    if findings:
        print(f"seed lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("seed lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
