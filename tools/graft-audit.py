#!/usr/bin/env python3
"""graft-audit: prove a graft's fast-forward buried no plant customization,
and report the template scaffolds a plant never filled.

MODE 1 — backup audit (default)

install.sh fast-forwards seed-owned machinery with a per-file backup, but it
does NOT check whether the file it overwrites carried a plant-authored
customization first. graft's promise is "reconcile a divergence before
overwriting it" — a promise the blind installer cannot keep on its own. This
tool is the gate that keeps it: run it AFTER an install/graft over a plant and
it maps every fresh backup back to the seed source that replaced it, then
classifies:

  IDENTICAL   backup == current seed  -> the plant file was already current; FF lost nothing
  DELTA       differs, no plant-signal -> normal version advance (older machinery); safe
  CUSTOMIZED  differs AND carries plant-signal content -> a divergence the FF overwrote;
              it must be RE-INTEGRATED into the FF'd file or ratified, never left buried
  GENERATED   a harness view generated from a seed node, with no plant-signal content
  PLANT-OWNED the harness projection of the plant's own `origin: project` agent or skill
              node (its skill projection and Copilot agent view included); the installer
              re-projected it from the graph, so no seed file backs it
  RETIRED     a harness entry projected from an `origin: seed` node the running seed no
              longer ships (MODE 4); reported, never a gate
  ORPHAN      a harness entry with no graph home that is not an `origin: seed` entry
              (MODE 4); reported, never a gate
  CORPUS-PLACED  a page `install.sh --expertise` placed from a corpus (its first line
              is `<!-- origin: corpus@<version> id: <corpus id> -->`, or its frontmatter
              says `origin: corpus@<version>`), or a harness projection of such a
              skill node: neither seed-owned nor plant-authored; the installer
              refreshes it only while its bytes equal the recorded hash, so a backup
              of it holds the corpus's earlier layer (SPEC-0001
              PLACED_PAGE_CARRIES_ITS_PROVENANCE)

A backup line counts as plant content only when the seed does not carry it. With
`--base <rev>` the seed at that revision counts too, so a backup byte-identical
to the seed the plant was installed from is DELTA: it carries nothing the plant
authored. The revision is the steward's to supply; without it the audit compares
with the seed as it stands, which is the conservative reading. An engine backup
(graph-lint.py, spec-lint.py, grill-lint.py) is also read against the plant's
current engine of the same name: graft-graph-engine.py carries the plant's
config and comments into the new body, so a line that survives there was
preserved, not lost.

The walk for backups covers this plant only. A directory holding its own
.cypress/seed.json is another plant (a scratch copy, a nested seed workspace),
and a symlinked directory is another tree; neither is walked, and neither
chooses the default --date (tools/plant_walk.py).

It also flags any backup over PLANT-AUTHORED docs/graph/ content (a knowledge
overwrite — should be none; knowledge is add-if-missing). The seed-owned graph
subtrees docs/graph/{protocols,skills,agents,method,templates}/ and the shared
scripts (graph-lint.py, spec-lint.py, grill-lint.py, agent-lint.py, agnosticism-lint.py,
prose-lint.py, status-register.py, session-metrics.py, code-anchor.py) are machinery, expected to be fast-forwarded — but only
where a seed source actually backs the path: a plant-authored project skill
under docs/graph/skills/ is plant knowledge. _schema.md and index.md are
project-instantiated and always the plant's own, like everything else under
docs/graph/. Given a plant engine and the seed's as an --engine pair, it also
warns if the plant engine is STALE (missing engine lines the seed has).

"Plant-signal" = the plant's own name/paths PLUS generic self-reference that a
customization uses without naming the plant ("this project's", "this program",
"our stack"). Pass the plant's known tokens with --tokens; each is matched at
word boundaries, because a short token is a substring of ordinary words before
it is a name.

MODE 2 — unfilled scaffolds (--unfilled)

The kernel body (AGENTS.md / CLAUDE.md) is compared with the seed's
core/AGENTS.md and gates the exit code: an OLD body (a seed line missing) is
`KERNEL STALE`; a seed-current body plus plant-authored lines is
`KERNEL EXTENDED` unless a standing `deviation.*` node with
`departs_from: kernel.body` records that boundary, in which case the audit
reports the deviation and its `ends_when` and passes.

install.sh copies every leaf of the seed's templates/docs/<rel> to the plant's
docs/graph/<rel> when missing. A leaf still BYTE-IDENTICAL to its template at
grow Phase 6 / graft Phase 7 was never filled: it is a scaffold posing as
knowledge, and a fresh agent routed to it reads placeholders as facts. Each one
is reported as `UNFILLED docs/graph/<rel>`; --rename moves it to
`<name>.unfilled.md` (the body survives, the router stops trusting it) and
--prune removes it. docs/graph/models.md, the plant's model map, is the one
leaf reported as `DISCLOSED docs/graph/<rel>` instead: an unfilled map means
every agent runs on its caller's model, which the plant has chosen, so it is
named, left out of the count and the exit code, and neither renamed nor
removed. docs/graph/runbooks/verification.md is exempt only when it
carries at least one gate row marked `executed` (verify.md's gate-state
vocabulary: executed | discovered | absent); byte-identity stays the trigger,
so a verification runbook identical to its template and carrying no executed
gate is unfilled like any other scaffold.

MODE 3 — kept deltas (--record <file>)

A graft record lists the files the graft merged keeping plant intent and the
files it kept as the plant's. A later installer run (a remedy, or a second
plain run) overwrites them again with a backup and no question, and the
record goes on claiming them kept. This mode reads the newest graft entry of
the record (a `# Graft` heading at any level; the latest date it carries, the
last one in the file on a tie) and its `Merged` and `Kept as the plant's`
sections. Each bullet's first backticked path, or its first word, names a
file, relative to docs/graph/ or to the plant root, with one `{a,b}` group
expanded. Each file is then checked for its plant delta:

  KEPT        the plant's file differs from the seed source it installs from
  LOST        the plant's file is byte-equal to the seed source: the delta the
              record claims is gone
  MISSING     the record names a file the plant no longer carries
  UNMAPPED    no seed source backs the path, so there is no delta to measure

LOST and MISSING fail the run (exit 1), and so does an entry that names no
file at all, or a record with no graft entry: a re-check of nothing is not a
pass. UNMAPPED is reported and does not gate. Run it last in Phase 7, after
every remedy that re-ran the installer.

MODE 4 — harness homes (--harness)

An agent or skill in a harness directory (`<adapter>/agents/<name>.md`,
`<adapter>/skills/<name>/SKILL.md`, `.github/agents/<name>.agent.md`) is
reached by its harness alone unless the graph carries its node. Two shapes
have no live home, and each is named on one line (SPEC-0001
CHECK_FLAGS_RETIRED_HARNESS_ENTRY, CHECK_FLAGS_ORPHAN_HARNESS_ENTRY):

  RETIRED     an `origin: seed` agent or skill the running seed no longer
              ships: its graph node, each projection of it, and an entry with
              no node whose own frontmatter says `origin: seed`
  ORPHAN      an entry with no graph node that is not an `origin: seed` entry:
              the plant authored it into the harness directory, where the
              router and every other harness cannot see it

Both are flags, never failures, and nothing is deleted: deleting one is the
owner's act, and relocating an ORPHAN into docs/graph/ is graft migration (c).
The backup audit prints the same lines after its verdicts; `install.sh
--check` runs this mode and prefixes each line with `[seed] --check: `. Exit 0,
with one line saying every harness entry has a graph home when none is flagged.

Usage:
  graft-audit.py <plant-root> <seed-root> [--date YYYYMMDD[-HHMMSS]]
                 [--tokens t1,t2,...] [--base <rev>]
                 [--engine <plant-engine>:<seed-engine>]...
  graft-audit.py <plant-root> <seed-root> --unfilled [--rename | --prune]
  graft-audit.py <plant-root> <seed-root> --record <docs/graph/changelog.md>
  graft-audit.py <plant-root> <seed-root> --harness
--date is a PREFIX of the backup stamp install.sh writes (YYYYMMDD-HHMMSS), so
`--date 20260101` audits a whole day and `--date 20260101-1632` audits the one
pass — a graft and the remedy it triggers land on the same day more often than
not. It defaults to the newest day a .bak stamp in the plant carries.
--engine is the one option that repeats: a graft passes one pair per engine
(graph-lint.py, spec-lint.py, grill-lint.py), and every pair is checked and
reported on its own line.
--base names a revision of the seed checkout (a tag or a commit); the seed root
must be a Git work tree for it, and a revision Git cannot resolve is refused
(exit 1).
Backup audit: exit 0 if clean/only-DELTA; 1 if any CUSTOMIZED or docs
overwrite (a gate hit). Unfilled: exit 1 while unfilled scaffolds remain and
neither --rename nor --prune was requested (a gate); 0 once none remain or
after they were renamed/removed. Exit 2 on a malformed command line.
Dependency-free.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

# The walk that stops at this plant's edge, from beside this file (graft-audit
# and growth-audit share it; neither is a package to import from).
import importlib.util as _ilu
_pw_spec = _ilu.spec_from_file_location(
    "cypress_plant_walk", Path(__file__).resolve().parent / "plant_walk.py")
plant_walk = _ilu.module_from_spec(_pw_spec)
_pw_spec.loader.exec_module(plant_walk)

GENERIC_SIGNALS = ("this project's", "this program", "our stack", "our program",
                   "this plant", "our deploy", "in this program")

VALUE_OPTIONS = ("date", "tokens", "engine", "base", "record")
FLAG_OPTIONS = ("unfilled", "rename", "prune", "harness")


def parse_args():
    """Accept --flag=value AND --flag value. The old =-only parser
    silently dropped a space-separated value into the positional list:
    `--tokens acme` audited with DEFAULT tokens and could print "clean"
    for a graft that buried a real customization — the exact false-pass
    this gate exists to prevent. Unknown extra positionals now fail
    loudly instead of being ignored. Boolean flags take no value; the
    remediation flags (--rename/--prune) act only on --unfilled findings
    and exclude each other, so a typo can never delete what a report-only
    run would merely have listed."""
    a = sys.argv[1:]
    pos, opt, i = [], {}, 0
    def _set(key, raw):
        if key == "tokens":
            opt["tokens"] = [t.strip().lower() for t in raw.split(",") if t.strip()]
        elif key == "engine":
            opt.setdefault("engine", []).append(raw)
        else:
            opt[key] = raw
    while i < len(a):
        x = a[i]
        if x in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        if x.startswith("--"):
            body = x[2:]
            key, eq, val = body.partition("=")
            if key in FLAG_OPTIONS:
                if eq:
                    print(f"  !! --{key} takes no value")
                    sys.exit(2)
                opt[key] = True
                i += 1
                continue
            if key not in VALUE_OPTIONS:
                print(f"  !! unknown option --{key}")
                sys.exit(2)
            if not eq:
                i += 1
                if i >= len(a):
                    print(f"  !! --{key} needs a value")
                    sys.exit(2)
                val = a[i]
            if val.startswith("--"):
                print(f"  !! --{key} got {val!r} as its value — a flag "
                      f"swallowed a flag; write --{key}=<value>")
                sys.exit(2)
            _set(key, val)
            if key == "tokens" and not opt["tokens"]:
                print("  !! --tokens list is empty — only the generic "
                      "plant signals will be scanned")
        else:
            pos.append(x)
        i += 1
    if len(pos) > 2:
        print(f"  !! unexpected extra arguments: {pos[2:]} — "
              f"did an option value go astray?")
        sys.exit(2)
    if (opt.get("rename") or opt.get("prune")) and not opt.get("unfilled"):
        print("  !! --rename/--prune act on --unfilled findings; add --unfilled")
        sys.exit(2)
    if opt.get("rename") and opt.get("prune"):
        print("  !! --rename and --prune exclude each other; pick one")
        sys.exit(2)
    return pos, opt


# seed-owned machinery under the plant's docs/graph/ (6.0.0 layout): these
# subtrees + the engine scripts are the seed's to fast-forward; everything
# else under docs/graph/ is plant-authored knowledge. _schema.md and
# index.md are deliberately NOT here: they are project-instantiated
# (graft.md — "copying the seed template would regress placeholders and
# wipe the authored router"), so a backup over them IS a knowledge
# overwrite worth alarming on.
# `legal/corpus/` is seed-owned like the rest: install.sh places legal-corpus/
# WHOLE under it on `--legal-corpus yes`, and place_tree fast-forwards it on
# every later run. It was missing here, so editing any of its 16 pages produced
# a backup that classified UNMAPPED *and* was reported as a plant knowledge
# overwrite — the exact false positive this module's header says it exists to
# avoid, on a first-class documented feature.
# `legal/index.md` is deliberately NOT included: that one IS plant-authored (it
# is where the owner scopes which instruments bear on the project), so a backup
# over it is a real knowledge overwrite and must keep alarming.
MACHINERY_SUBTREES = ("protocols/", "skills/", "agents/", "method/", "templates/",
                      "legal/corpus/")
# config-free tools install.sh delivers into docs/graph/ from a seed home
# outside templates/knowledge-graph/ (the agent-lint class: fast-forwarded,
# never add-if-missing). plant path under docs/graph/ -> seed-relative source.
DELIVERED_TOOLS = {
    "agent-lint.py": "integrations/claude-code/agent-lint.py",
    # the frontmatter reader every engine beside it imports. A new placed file
    # the audit cannot map is UNMAPPED, and three of them turned up the moment
    # it started shipping — which is what this table is for.
    "frontmatter.py": "templates/knowledge-graph/frontmatter.py",
    # placed only when --legal-corpus yes; the corpus travels with its checker
    "legal-lint.py": "tests/legal-lint.py",
    "agnosticism-lint.py": "tools/agnosticism-lint.py",
    "prose-lint.py": "tools/prose-lint.py",
    "status-register.py": "tools/status-register.py",
    "session-metrics.py": "tools/session-metrics.py",
    "code-anchor.py": "tools/code-anchor.py",
}
# the graph engines: placed add-if-missing, then reconciled by
# graft-graph-engine.py, which keeps the plant's config and comments
ENGINE_FILES = ("graph-lint.py", "spec-lint.py", "grill-lint.py")
ENGINE_PATHS = tuple("docs/graph/" + e for e in ENGINE_FILES)
SCAFFOLD_FILES = ENGINE_FILES + tuple(DELIVERED_TOOLS)

# Seed machinery the installer places OUTSIDE docs/graph/, into the harness
# adapter directories: hooks, extensions, settings, the system-prompt overlay,
# the tool-neutral entry prompt. Verbatim copies of a seed file, so a backup
# over one is byte-comparable exactly like a docs/graph/ node.
# Until 7.16.0 install.sh wrote every one of these with a bare `cp`, so none
# ever produced a backup and this table had nothing to classify — the audit
# reported "clean" over destroyed plant customizations. The writer now backs
# them up; this is what makes them legible instead of UNMAPPED.
ADAPTER_MACHINERY = {
    ".claude/route-hook.py": "integrations/claude-code/route-hook.py",
    ".claude/status-hook.py": "integrations/claude-code/status-hook.py",
    ".claude/bound-hook.py": "integrations/claude-code/bound-hook.py",
    ".claude/agent-lint.py": "integrations/claude-code/agent-lint.py",
    ".claude/frontmatter.py": "templates/knowledge-graph/frontmatter.py",
    ".claude/settings.json": "integrations/claude-code/settings.json",
    ".github/hooks/route-hook.py": "integrations/claude-code/route-hook.py",
    ".github/hooks/status-hook.py": "integrations/claude-code/status-hook.py",
    ".github/hooks/route.json": "integrations/github-copilot/hooks/route.json",
    ".github/hooks/status.json": "integrations/github-copilot/hooks/status.json",
    ".prime/agent/hooks/route-hook.py": "integrations/claude-code/route-hook.py",
    ".prime/agent/hooks/status-hook.py": "integrations/claude-code/status-hook.py",
    ".prime/agent/settings.json": "integrations/prime-agent/settings.json",
    ".prime/agent/APPEND_SYSTEM.md": "integrations/prime-agent/APPEND_SYSTEM.md",
    ".prime/agent/extensions/route-extension.ts":
        "integrations/prime-agent/route-extension.ts",
    ".prime/agent/extensions/status-extension.ts":
        "integrations/prime-agent/status-extension.ts",
    "opencode.json": "integrations/opencode/opencode.json",
    "EXPERT_SEED_INSTALL_PROMPT.md": "INSTALL_PROMPT.md",
}

# Harness views GENERATED from a seed node at install time — slash commands,
# the transformed Copilot agent/prompt/instruction files, the Codex snippet.
# They are seed-owned (never plant knowledge), but they are NOT byte-comparable
# with the node they came from, so claiming IDENTICAL or DELTA over them would
# be a measurement the audit cannot make. They get their own verdict.
GENERATED_VIEWS = (
    ".claude/commands/", ".opencode/commands/", ".prime/agent/prompts/",
    ".github/agents/", ".github/prompts/", ".github/instructions/",
)
GENERATED_FILES = (".codex/codex-config-snippet.toml",)
# `.cypress/seed.json` is the installer's own derived state, replaced without a
# backup by design (place_state), so it never reaches this audit.


def generator_for(rel: str, seed: Path):
    """The seed node a generated harness view was projected FROM, or None."""
    if rel in GENERATED_FILES:
        return seed / "integrations/codex/config.toml.example"
    if not rel.startswith(GENERATED_VIEWS):
        return None
    stem = Path(rel).name
    for suffix in (".agent.md", ".prompt.md", ".instructions.md", ".md"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    if rel.startswith(".github/instructions/"):
        stem = stem[:-len("-skill")] if stem.endswith("-skill") else stem
        cand = seed / "skills" / stem / "SKILL.md"
        return cand if cand.exists() else None
    if rel.startswith((".github/agents/",)):
        for c in sorted((seed / "agents").glob("*.md")):
            if re.sub(r"^\d+-", "", c.stem) == stem:
                return c
        return None
    cand = seed / "protocols" / f"{stem}.md"
    return cand if cand.exists() else None

# the scaffold mirror: install.sh place_docs_skeleton copies the seed's
# templates/docs/<rel> to the plant's docs/graph/<rel> when missing.
TEMPLATE_DOCS = "templates/docs"
GRAPH_HOME = "docs/graph"
VERIFICATION_RUNBOOK = "runbooks/verification.md"
UNFILLED_SUFFIX = ".unfilled.md"
# The plant's model map (ADR-0022). An unfilled row already means "inherit the
# caller's model, and say so", so a map still identical to its template is a
# choice the plant has made: --unfilled discloses it, outside the blocking
# count, and --rename and --prune leave it in place.
MODEL_MAP = "models.md"
# verify.md gate-state vocabulary: executed | discovered | absent. A row is
# "marked executed" when it carries the token as a whole word and not as a
# negation ("not executed", "never executed", "un-executed").
EXECUTED_TOKEN = re.compile(r"(?<!not )(?<!never )(?<!un-)\bexecuted\b", re.IGNORECASE)
GATE_ROW = re.compile(r"^(\||[-*+]\s|\d+\.\s)")


BAK_STAMP = re.compile(r"\.bak-(\d{8}-\d+)")


def bak_stamp(bak: Path) -> str:
    """The `YYYYMMDD-HHMMSS` stamp install.sh wrote into a backup's name, whole.
    The time is the finest distinction a later audit can make, so it is read at
    the granularity the filename records it and narrowed by the caller, never
    thrown away here."""
    m = BAK_STAMP.search(bak.name)
    return m.group(1) if m else ""


def plant_rel(bak: Path, plant: Path) -> str:
    rel = bak.relative_to(plant).as_posix()
    return re.sub(r"\.bak-\d{8}-\d+$", "", rel)


def seed_source_for(rel: str, seed: Path):
    """Map a plant-relative machinery path to the seed source it installs from
    (6.0.0 layout: machinery home is docs/graph/, tool dirs hold projections)."""
    if rel in ("CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"):
        return seed / "core/AGENTS.md"
    if rel.startswith("docs/graph/"):
        sub = rel[len("docs/graph/"):]
        if sub in DELIVERED_TOOLS:
            return seed / DELIVERED_TOOLS[sub]
        if sub == "agents/_routes.golden.tsv":
            return seed / "agents/_routes.golden.tsv"
        if sub.startswith("protocols/"):
            return seed / "protocols" / sub[len("protocols/"):]
        if sub.startswith("method/"):
            return seed / "core/method" / sub[len("method/"):]
        if sub.startswith("agents/"):
            return seed / "agents" / sub[len("agents/"):]
        if sub.startswith("skills/"):
            # flattened in the plant: docs/graph/skills/<name>.md
            return seed / "skills" / Path(sub).stem / "SKILL.md"
        if sub.startswith("templates/"):
            return seed / "templates" / sub[len("templates/"):]
        if sub.startswith("legal/corpus/"):
            return seed / "legal-corpus" / sub[len("legal/corpus/"):]
        if sub in SCAFFOLD_FILES:
            return seed / "templates/knowledge-graph" / sub
        return None  # plant-authored graph content — never seed-mapped
    if rel in ADAPTER_MACHINERY:
        return seed / ADAPTER_MACHINERY[rel]
    sub = projected_sub(rel)
    # a projection keeps the seed's agents/<name>.md and skills/<name>/SKILL.md shape
    return seed / sub if sub else None


# The harness directories install.sh projects docs/graph/{agents,skills}/ into.
ADAPTER_HOMES = (".claude/", ".codex/", ".opencode/", ".prime/agent/")


def projected_sub(rel: str):
    """The adapter-relative path of a harness projection of the graph's roster
    or skill set (`agents/<name>.md`, `skills/<name>/SKILL.md`), or None."""
    for adapter in ADAPTER_HOMES:
        if rel.startswith(adapter):
            sub = rel[len(adapter):]
            return sub if sub.startswith(("agents/", "skills/")) else None
    return None


def plant_owned_node(rel: str, plant: Path):
    """The plant's own node a harness projection was taken from, or None.
    install.sh projects the roster and the skill set FROM the graph, so an
    agent or skill the plant authored (`origin: project`) reaches every harness
    directory with no seed file behind it: `<adapter>/agents/<name>.md` from
    `docs/graph/agents/<name>.md`, `<adapter>/skills/<name>/SKILL.md` from
    `docs/graph/skills/<name>.md`, and the Copilot view
    `.github/agents/<name>.agent.md` from `docs/graph/agents/<name>.md`. A
    backup of that projection is the plant's own content, replaced by a fresh
    projection of the plant's own node: a named exclusion, not a backup nobody
    can classify."""
    sub = projected_sub(rel)
    parts = Path(sub).parts if sub else ()
    if parts[:1] == ("agents",):
        node = plant / GRAPH_HOME / sub
    elif len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
        node = plant / GRAPH_HOME / "skills" / f"{parts[1]}.md"
    elif rel.startswith(".github/agents/") and rel.endswith(".agent.md") \
            and "/" not in rel[len(".github/agents/"):]:
        node = plant / GRAPH_HOME / "agents" / (Path(rel).name[:-len(".agent.md")] + ".md")
    else:
        return None
    if node.is_file() and _fm_value(_frontmatter(node), "origin") == "project":
        return node
    return None


# A page the selective placement wrote (SPEC-0001 §6): a library or tool page
# opens with the provenance line, a skill node says `origin: corpus@<version>`.
CORPUS_PROVENANCE = re.compile(r"^<!-- origin: corpus@\S+ id: \S+ -->$")


def corpus_placed_text(text: str) -> bool:
    if CORPUS_PROVENANCE.match(text.split("\n", 1)[0]):
        return True
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return bool(m) and _fm_value(m.group(1), "origin").startswith("corpus@")


def corpus_placed(bak: Path, rel: str, plant: Path) -> bool:
    """Whether a backup is of a corpus-placed page: the backup carries the
    provenance itself, or it is a harness projection of a skill node that does."""
    if corpus_placed_text(bak.read_text(errors="replace")):
        return True
    sub = projected_sub(rel)
    parts = Path(sub).parts if sub else ()
    if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
        node = plant / GRAPH_HOME / "skills" / f"{parts[1]}.md"
        return node.is_file() and corpus_placed_text(node.read_text(errors="replace"))
    return False


# The harness entries (SPEC-0001 §6): what the roster and skill projections
# write, in every harness directory the plant carries. An entry with no graph
# home is invisible to the router and to every other harness, and an
# `origin: seed` one the seed stopped shipping goes on loading in its harness
# long after the seed folded it away. Both are flagged, never deleted: the
# deletion is the owner's act (the owner's decision).
COPILOT_AGENTS = ".github/agents/"
NOT_AN_ENTRY = re.compile(r"^(_|index$|README$)")
NUMBER_PREFIX = re.compile(r"^\d+-")


def harness_entries(plant: Path):
    """(target-relative entry, 'agents' or 'skills', name) for every agent and
    skill a harness directory of the plant carries; backups are not entries."""
    found = []
    for adapter in ADAPTER_HOMES:
        for p in sorted((plant / adapter / "agents").glob("*.md")):
            found.append((p, "agents", p.stem))
        for p in sorted((plant / adapter / "skills").glob("*/SKILL.md")):
            found.append((p, "skills", p.parent.name))
    for p in sorted((plant / COPILOT_AGENTS).glob("*.agent.md")):
        found.append((p, "agents", p.name[:-len(".agent.md")]))
    return [(p.relative_to(plant).as_posix(), kind, name) for p, kind, name in found
            if p.is_file() and not NOT_AN_ENTRY.match(name)]


def graph_home(rel: str, kind: str, name: str, plant: Path) -> Path:
    """The graph node a harness entry is the projection of. A Copilot agent view
    drops the node's `<digits>-` prefix, so its home is found by that name."""
    home = plant / GRAPH_HOME / kind / f"{name}.md"
    if rel.startswith(COPILOT_AGENTS) and not home.is_file():
        for n in sorted((plant / GRAPH_HOME / "agents").glob("*.md")):
            if NUMBER_PREFIX.sub("", n.stem) == name:
                return n
    return home


def seed_ships(kind: str, name: str, seed: Path) -> bool:
    """Whether the running seed still carries the agent or skill `name`, by the
    node name or, for an agent, by the name its Copilot view uses."""
    if kind == "skills":
        return (seed / "skills" / name / "SKILL.md").is_file()
    return any(a.stem == name or NUMBER_PREFIX.sub("", a.stem) == name
               for a in (seed / "agents").glob("*.md"))


def _is_seed_origin(path: Path) -> bool:
    return _fm_value(_frontmatter(path), "origin") == "seed"


def harness_flags(plant: Path, seed: Path) -> list:
    """(verdict, target-relative path, graph home) for every graph node and
    harness entry with no live home: RETIRED for an `origin: seed` node, or a
    projection of one, the running seed does not ship; ORPHAN for an entry
    with no graph node that is not an `origin: seed` entry."""
    flags, retired = [], set()
    for kind in ("agents", "skills"):
        for node in sorted((plant / GRAPH_HOME / kind).glob("*.md")):
            if node.is_file() and not NOT_AN_ENTRY.match(node.stem) \
                    and _is_seed_origin(node) and not seed_ships(kind, node.stem, seed):
                retired.add(node.resolve())
                flags.append(("RETIRED", node.relative_to(plant).as_posix(), ""))
    for rel, kind, name in harness_entries(plant):
        home = graph_home(rel, kind, name, plant)
        home_rel = home.relative_to(plant).as_posix()
        if home.is_file():
            if home.resolve() in retired:
                flags.append(("RETIRED", rel, home_rel))
        elif _is_seed_origin(plant / rel):
            if not seed_ships(kind, name, seed):
                flags.append(("RETIRED", rel, home_rel))
        else:
            flags.append(("ORPHAN", rel, home_rel))
    return flags


def flag_line(verdict: str, rel: str, home: str) -> str:
    if verdict == "RETIRED":
        return (f"RETIRED {rel}: an origin: seed node or projection the running seed "
                f"does not ship; the owner decides its deletion")
    return (f"ORPHAN {rel}: no graph home ({home}); propose relocating it into the "
            f"graph, graft migration (c)")


def audit_harness(plant: Path, seed: Path) -> int:
    """--harness: name every RETIRED and ORPHAN entry, one line each, or say
    there is none. A flag, never a failure, and nothing is written."""
    flags = harness_flags(plant, seed)
    for verdict, rel, home in flags:
        print(flag_line(verdict, rel, home))
    if not flags:
        print("every harness entry has a graph home.")
    return 0


def is_seed_owned_graph_path(rel: str) -> bool:
    if not rel.startswith("docs/graph/"):
        return False
    sub = rel[len("docs/graph/"):]
    return sub.startswith(MACHINERY_SUBTREES) or sub in SCAFFOLD_FILES


def scaffold_pairs(plant: Path, seed: Path):
    """(rel, plant leaf, seed template) for every templates/docs/** leaf the
    plant carries at its mirrored docs/graph/<rel>. Walking the templates,
    not the plant, keeps plant-authored content and the fast-forwarded
    docs/graph/templates/ machinery copy out of the comparison by construction."""
    troot = seed / TEMPLATE_DOCS
    for t in sorted(p for p in troot.rglob("*") if p.is_file()):
        rel = t.relative_to(troot).as_posix()
        f = plant / GRAPH_HOME / rel
        if f.is_file() and not f.is_symlink():
            yield rel, f, t


def has_executed_gate(text: str) -> bool:
    """True when at least one gate row — a markdown table row or list item —
    is marked with verify.md's `executed` state."""
    return any(GATE_ROW.match(s) and EXECUTED_TOKEN.search(s)
               for s in (l.strip() for l in text.splitlines()))


def main() -> int:
    pos, opt = parse_args()
    if len(pos) < 2:
        print(__doc__)
        return 1
    plant, seed = Path(pos[0]), Path(pos[1])
    # A vacuous audit must not read as a clean one: a wrong plant root
    # finds zero backups (or zero scaffolds) and would otherwise print the
    # same "clean" line a real audit earns. A plant always has docs/graph/
    # — refuse anything that does not.
    if not (plant / GRAPH_HOME).is_dir():
        print(f"  !! {plant} has no {GRAPH_HOME}/ — not a plant root; "
              f"refusing a vacuous audit")
        return 1
    if opt.get("harness"):
        return audit_harness(plant, seed)
    if opt.get("unfilled"):
        action = "prune" if opt.get("prune") else "rename" if opt.get("rename") else None
        return audit_unfilled(plant, seed, action)
    if opt.get("record"):
        return audit_record(plant, seed, Path(opt["record"]))
    return audit_backups(plant, seed, opt)


GRAFT_ENTRY = re.compile(r"^(#{1,6})\s+Graft\b(.*)$")
RECORD_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
RECORD_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
KEPT_SECTIONS = ("merged", "kept as the plant")
BRACES = re.compile(r"\{([^{}]*,[^{}]*)\}")


def newest_graft_entry(text: str):
    """(heading, body lines) of the record's newest graft entry, or None. The
    newest is the one with the latest date in its heading; on a tie, or with no
    date, the last in the file."""
    lines = text.splitlines()
    entries = []
    for i, line in enumerate(lines):
        m = GRAFT_ENTRY.match(line)
        if not m:
            continue
        level, end = len(m.group(1)), len(lines)
        for j in range(i + 1, len(lines)):
            h = RECORD_HEADING.match(lines[j])
            if h and len(h.group(1)) <= level:
                end = j
                break
        d = RECORD_DATE.findall(line)
        entries.append((d[-1] if d else "", i, line.strip(), lines[i + 1:end]))
    if not entries:
        return None
    best = max(entries, key=lambda e: (e[0], e[1]))
    return best[2], best[3]


def kept_artifacts(body) -> list:
    """[(section, raw bullet, [paths])] for the bullets of the entry's Merged
    and Kept-as-the-plant's sections."""
    out, section = [], None
    for line in body:
        h = RECORD_HEADING.match(line)
        if h:
            name = h.group(2).lower()
            section = next((s for s in KEPT_SECTIONS if name.startswith(s)), None)
            continue
        if section is None or not re.match(r"^\s*[-*+]\s+", line):
            continue
        item = re.sub(r"^\s*[-*+]\s+", "", line).strip()
        if re.match(r"^(none|n/?a)\b", item, re.I):
            continue
        head = re.split(r"\s+[—–]\s+|\s+-\s+", item, maxsplit=1)[0]
        tick = re.search(r"`([^`]+)`", head)
        word = tick.group(1) if tick else (head.split() or [""])[0]
        paths = [word]
        m = BRACES.search(word)
        if m:
            paths = [word[:m.start()] + alt.strip() + word[m.end():]
                     for alt in m.group(1).split(",")]
        out.append((section, item, [p.strip().lstrip("./") for p in paths if p.strip()]))
    return out


def audit_record(plant: Path, seed: Path, record: Path) -> int:
    """MODE 3: every file the newest graft entry lists as merged or kept still
    carries its plant delta."""
    try:
        text = record.read_text(errors="replace")
    except OSError:
        print(f"  !! cannot read the graft record {record}")
        return 1
    entry = newest_graft_entry(text)
    if entry is None:
        print(f"  !! {record} holds no graft entry (a `# Graft` heading); "
              f"nothing to re-check is not a pass")
        return 1
    heading, body = entry
    items = kept_artifacts(body)
    print(f"  record: {heading}")
    print(f"  merged or kept files listed: {sum(len(p) for _, _, p in items)}")
    bad = 0
    for section, raw, paths in items:
        if not paths:
            print(f"  NO-PATH     a {section} bullet names no file: {raw}")
            bad += 1
            continue
        for p in paths:
            rel = next((c for c in (f"{GRAPH_HOME}/{p}", p) if (plant / c).is_file()),
                       None)
            if rel is None:
                at_root = p.startswith(GRAPH_HOME + "/") or seed_source_for(p, seed)
                rel = p if at_root else f"{GRAPH_HOME}/{p}"
                print(f"  MISSING     {rel} ({section}): the plant no longer carries it")
                bad += 1
                continue
            src = seed_source_for(rel, seed)
            if src is None or not src.is_file():
                print(f"  UNMAPPED    {rel} ({section}): no seed source backs it; "
                      f"no delta to measure")
                continue
            if (plant / rel).read_bytes() == src.read_bytes():
                print(f"  LOST        {rel} ({section}): byte-equal to the seed's "
                      f"{src.relative_to(seed).as_posix()}; the plant delta the record "
                      f"claims is gone. Re-apply it from the newest backup that holds "
                      f"it, then run this again")
                bad += 1
            else:
                print(f"  KEPT        {rel} ({section})")
    if bad:
        print(f"  {bad} merged or kept file(s) lost their plant delta after the graft "
              f"recorded them")
        return 1
    print("  every merged or kept file still carries its plant delta")
    return 0


def audit_unfilled(plant: Path, seed: Path, action) -> int:
    """MODE 2: report (and on request rename/remove) every docs/graph/<rel>
    leaf byte-identical to the seed's templates/docs/<rel>."""
    if not (seed / TEMPLATE_DOCS).is_dir():
        print(f"  !! {seed} has no {TEMPLATE_DOCS}/ — not a seed root; "
              f"refusing a vacuous scaffold audit")
        return 1
    mirrored, unfilled, disclosed = 0, [], []
    for rel, f, t in scaffold_pairs(plant, seed):
        # a delivered blank form is byte-identical by design — it is the template
        if f.name.endswith(".template.md") or f.name.startswith("_"):
            continue
        mirrored += 1
        if f.read_bytes() != t.read_bytes():
            continue
        if rel == VERIFICATION_RUNBOOK and has_executed_gate(f.read_text(errors="replace")):
            continue
        (disclosed if rel == MODEL_MAP else unfilled).append((rel, f))
    for rel, _f in disclosed:
        print(f"  DISCLOSED {GRAPH_HOME}/{rel}  (unfilled: every agent runs on "
              f"its caller's model until the plant fills it)")
    for rel, f in unfilled:
        line = f"  UNFILLED {GRAPH_HOME}/{rel}"
        if action == "prune":
            f.unlink()
            line += "  -> removed"
        elif action == "rename":
            target = f.with_name(f.stem + UNFILLED_SUFFIX)
            f.replace(target)
            line += f"  -> {target.name}"
        print(line)
    verb = {"prune": "removed", "rename": "renamed", None: "reported"}[action]
    print(f"  unfilled scaffolds: {len(unfilled)} {verb} "
          f"(of {mirrored} template-mirrored file(s) under {GRAPH_HOME}/)")
    if not mirrored:
        print(f"  note: no {GRAPH_HOME}/ leaf mirrors a {TEMPLATE_DOCS}/ template — "
              f"nothing to compare (already pruned, or a plant with no scaffold)")
    if unfilled and action is None:
        print("  !! unfilled scaffolds remain — fill them, or re-run with "
              "--rename (keeps the body as <name>.unfilled.md) or --prune")
        return 1
    return 0


def audit_backups(plant: Path, seed: Path, opt: dict) -> int:
    """MODE 1: map every fresh .bak to its seed source and classify what the
    fast-forward replaced."""
    # Explicit --tokens are the plant's own name and paths, matched at WORD
    # BOUNDARIES: a supplied token is scanned against prose, and a short one is
    # a substring of ordinary words long before it is a name.
    # GENERIC_SIGNALS are ordinary self-reference ("this project's"), which the
    # SEED itself uses in its shipped charters — so a pristine machinery file,
    # replaced by a reworded version of itself, matched one and was reported as
    # a buried customization. A gate that cries wolf on untouched files teaches
    # a steward to ratify without looking, which is the failure the
    # reconcile-before-overwrite gate exists to prevent. A generic phrase
    # therefore counts only when no seed text carries it too: the seed source,
    # its --base version, or the generator of a harness view.
    explicit = [(t.lower(), re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) +
                                       r"(?![A-Za-z0-9])", re.I))
                for t in opt.get("tokens", [])]
    generic = [t.lower() for t in GENERIC_SIGNALS]

    def signals(text: str, seed_texts) -> list:
        """The customization signals `text` carries: every explicit token, and
        each generic phrase no seed text carries itself."""
        low, seed_low = text.lower(), [s.lower() for s in seed_texts]
        hit = [t for t, rx in explicit if rx.search(low)]
        hit += [t for t in generic if t in low and not any(t in s for s in seed_low)]
        return sorted(set(hit))[:4]

    base = None
    if opt.get("base"):
        base = _seed_revision(seed, opt["base"])
        if base is None:
            print(f"  !! --base {opt['base']!r} is not a revision of the seed "
                  f"checkout at {seed}; refusing to read backups against a "
                  f"seed version that could not be found")
            return 1

    # this plant's backups only: tools/plant_walk.py skips a nested plant
    # (its own .cypress/seed.json) and a symlinked directory, so neither is
    # counted nor chooses the default --date
    stamped = [(p, bak_stamp(p)) for p in plant_walk.files(plant, pattern="*.bak-*")]
    date = opt.get("date")
    if not date:
        # the newest DAY rather than the newest stamp: one graft writes its
        # backups over several seconds and the whole pass is one audit.
        stamps = sorted(s for _, s in stamped if s)
        date = stamps[-1][:8] if stamps else "00000000"

    baks = [p for p, s in stamped
            if p.is_file() and not p.is_symlink() and s.startswith(date)]
    counts = {"IDENTICAL": 0, "DELTA": 0, "CUSTOMIZED": 0,
              "GENERATED": 0, "PLANT-OWNED": 0, "RETIRED": 0, "ORPHAN": 0,
              "CORPUS-PLACED": 0, "UNMAPPED": 0}
    # the harness entries with no live graph home, read once: a backup of one
    # takes its verdict, and every one is named after the backup verdicts
    flags = harness_flags(plant, seed)
    flagged = {rel: verdict for verdict, rel, _ in flags}
    customized, knowledge_hits, unmapped = [], [], []
    for b in baks:
        rel = plant_rel(b, plant)
        # A corpus-placed page is neither the seed's machinery nor the plant's
        # knowledge: the installer refreshed it from the corpus because its
        # bytes still equalled the recorded hash, so the backup is the corpus's
        # earlier layer, not a plant edit (SPEC-0001 PLACED_PAGE_CARRIES_ITS_PROVENANCE).
        if corpus_placed(b, rel, plant):
            counts["CORPUS-PLACED"] += 1
            continue
        src = seed_source_for(rel, seed)
        seed_backed = bool(src and src.exists())
        # a real knowledge overwrite is a backup over PLANT-AUTHORED
        # docs/graph/ content. A machinery-shaped path is only exempt when
        # a seed source ACTUALLY backs it: a plant-authored project skill
        # lives at docs/graph/skills/<name>.md too, and exempting the
        # subtree wholesale hid exactly those overwrites.
        if rel.startswith("docs/graph/") and not (
                is_seed_owned_graph_path(rel) and seed_backed):
            knowledge_hits.append(b.relative_to(plant).as_posix())
        if not seed_backed:
            # A generated harness view has a seed GENERATOR rather than a seed
            # twin. It is still seed-owned machinery, so reporting it UNMAPPED
            # ("no seed source; inspect by hand") sent a steward hunting for a
            # file that never existed. Byte comparison is meaningless here, so
            # the one question that still has meaning is asked instead: does the
            # replaced body carry a plant customization signal?
            gen = generator_for(rel, seed)
            if gen is not None and gen.exists():
                hit = signals(b.read_text(errors="replace"),
                              [gen.read_text(errors="replace")])
                if hit:
                    counts["CUSTOMIZED"] += 1
                    customized.append((b.relative_to(plant).as_posix(), hit))
                else:
                    counts["GENERATED"] += 1
            elif plant_owned_node(rel, plant):
                counts["PLANT-OWNED"] += 1
            elif rel in flagged:
                counts[flagged[rel]] += 1
            else:
                counts["UNMAPPED"] += 1
                unmapped.append(b.relative_to(plant).as_posix())
            continue
        bt, st = b.read_text(errors="replace"), src.read_text(errors="replace")
        if bt == st:
            counts["IDENTICAL"] += 1
            continue
        # The plant authored a line only if no seed version carries it: the
        # seed as it stands, and the seed at --base, the one it was installed
        # from. It was LOST only if the file that replaced it lacks it too; an
        # engine keeps its config and comments through graft-graph-engine.py,
        # so a line still in the plant's current engine was preserved.
        seed_texts = [st] + ([_seed_text_at(seed, base, src)] if base else [])
        kept = list(seed_texts)
        if rel in ENGINE_PATHS and (plant / rel).is_file():
            kept.append((plant / rel).read_text(errors="replace"))
        hit = signals("\n".join(_added_lines(bt, kept)), seed_texts)
        if hit:
            counts["CUSTOMIZED"] += 1
            customized.append((b.relative_to(plant).as_posix(), hit))
        else:
            counts["DELTA"] += 1

    print(f"  backups audited: {len(baks)} -> {counts}")
    if unmapped:
        print(f"  !! {len(unmapped)} UNMAPPED backup(s) — no seed source; "
              f"inspect by hand:")
        for u in unmapped[:20]:
            print(f"       {u}")
    for verdict, rel, home in flags:
        print("  " + flag_line(verdict, rel, home))
    if not baks:
        # Idempotent installs make zero-backup grafts the NORMAL no-op
        # case — but only when no backups exist at all. Backups under
        # OTHER date stamps mean the requested date audited nothing
        # while the real fast-forward went unexamined: fail, do not
        # print the same "clean" verdict a real audit earns.
        other = sorted({s for _, s in stamped if s and not s.startswith(date)})
        if other:
            shown = ", ".join(other[:6]) + (" …" if len(other) > 6 else "")
            print(f"  !! zero backups for date {date}, but backups exist "
                  f"for {shown} — wrong --date? refusing a "
                  f"vacuous audit")
            return 1
        print("  note: zero backup files — nothing was overwritten; "
              "the audit had nothing to prove")
    kernel_ok = _kernel_currency(plant, seed)
    schema_ok = _schema_currency(plant, seed)
    # every pair runs, so a malformed first pair cannot hide the check of the
    # next, nor a current last pair the staleness of the ones before it
    engine_ok = all([_engine_currency(pair) for pair in opt.get("engine", [])])
    if knowledge_hits:
        print(f"  !! {len(knowledge_hits)} knowledge overwrite(s) under docs/graph/:")
        for k in knowledge_hits[:20]:
            print(f"       {k}")
    if customized:
        print(f"  !! {len(customized)} FF-overwritten plant customization(s) — RE-INTEGRATE or ratify:")
        for rel, hit in customized[:40]:
            print(f"       {rel}  [signal: {','.join(hit)}]")
        return 1
    if knowledge_hits or not kernel_ok or not engine_ok:
        return 1
    if unmapped:
        # An UNMAPPED backup is a file the audit could not classify at all.
        # Printing the warning and then "clean" told a steward both that
        # something was unexplained and that nothing was — and the second line
        # is the one that gets believed. Unknown is not green.
        print(f"  UNRESOLVED — {len(unmapped)} backup(s) the audit cannot map to "
              f"a seed source. Classify them by hand before ratifying this graft.")
        return 1
    print("  clean — no plant knowledge overwritten, no customization buried")
    return 0


def _added_lines(bak_text: str, kept_texts) -> list:
    """Lines present in the backup and in none of `kept_texts` (a cheap set
    difference — enough to surface unique plant content for signal scanning)."""
    kept = {l for t in kept_texts for l in t.splitlines()}
    return [l for l in bak_text.splitlines() if l not in kept and l.strip()]


def _seed_revision(seed: Path, rev: str):
    """The commit `rev` names in the seed checkout, or None when Git cannot
    resolve it (no such revision, no Git work tree, no git)."""
    try:
        r = subprocess.run(["git", "-C", str(seed), "rev-parse", "--verify",
                            "--quiet", "--end-of-options", f"{rev}^{{commit}}"],
                           capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _seed_text_at(seed: Path, commit: str, src: Path) -> str:
    """The seed file `src` as it was at `commit`, or "" where it did not exist
    yet. Read from the object store, so it writes nothing, `.git/index` included."""
    r = subprocess.run(["git", "-C", str(seed), "cat-file", "blob",
                        f"{commit}:{src.relative_to(seed).as_posix()}"],
                       capture_output=True)
    return r.stdout.decode(errors="replace") if r.returncode == 0 else ""


def _strip_inline_comment(line: str) -> str:
    q = None
    for i, c in enumerate(line):
        if q:
            if c == q:
                q = None
        elif c in "'\"":
            q = c
        elif c == "#":
            return line[:i].rstrip()
    return line.rstrip()


def _code_lines(text: str) -> set:
    out = set()
    for l in text.splitlines():
        s = _strip_inline_comment(l)
        if s.strip() and not s.lstrip().startswith("#"):
            out.add(s)
    return out


KERNEL_DEVIATION_KEY = "kernel.body"  # departs_from value a deviation uses to cover the kernel


def _plant_added_lines(seed_lines, plant_lines):
    """Lines the plant ADDED to a seed-current kernel body, or None when the
    plant body is not the seed body plus additions (a seed line is missing or
    rewritten — an old or hand-edited kernel, not a boundary)."""
    added = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, seed_lines, plant_lines, autojunk=False).get_opcodes():
        if tag in ("delete", "replace"):
            return None
        if tag == "insert":
            added += j2 - j1
    return added


def _frontmatter(path: Path) -> str:
    """The text of a node's leading `---` block, or "" when it has none."""
    m = re.match(r"^---\n(.*?)\n---", path.read_text(errors="replace"), re.S)
    return m.group(1) if m else ""


def _fm_value(fm: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*?)[ \t]*$", fm, re.M)
    if not m:
        return ""
    return m.group(1).split("#", 1)[0].strip().strip("\"'")


def _standing_kernel_deviation(plant: Path):
    """The plant's standing deviation node that covers the kernel body, if any:
    docs/graph/nodes/deviation.*.md (no blank forms) with kind: deviation,
    status: standing and departs_from: kernel.body. Returns (id, ends_when)."""
    nodes = plant / GRAPH_HOME / "nodes"
    if not nodes.is_dir():
        return None
    for f in sorted(nodes.glob("deviation.*.md")):
        if f.name.startswith("_") or f.name.endswith(".template.md"):
            continue
        fm = _frontmatter(f)
        if (_fm_value(fm, "kind") == "deviation"
                and _fm_value(fm, "status") == "standing"
                and _fm_value(fm, "departs_from") == KERNEL_DEVIATION_KEY):
            return _fm_value(fm, "id") or f.stem, _fm_value(fm, "ends_when")
    return None


def _kernel_currency(plant: Path, seed: Path) -> bool:
    """The kernel body is seed-owned machinery loaded on every session. A graft
    that only re-points the CLAUDE.md<->AGENTS.md symlink and leaves a STALE
    kernel body is a silent, high-impact miss (install.sh place_kernel once did
    exactly this, and left no .bak for the backup-scan to catch). Compare the
    plant's live kernel file(s) — resolving the shared symlink — against the
    seed's current core/AGENTS.md directly, independent of any backup.
    Three verdicts: current (byte-equal); STALE (a seed line missing — an old
    or hand-edited body; blocks); EXTENDED (seed body + plant-authored lines —
    blocks unless a standing deviation.* node with departs_from: kernel.body
    records the boundary, in which case the deviation is reported and the
    check passes). Returns True when the check passes."""
    sk = seed / "core/AGENTS.md"
    if not sk.exists():
        return True
    seed_txt = sk.read_text(errors="replace")
    seed_lines = seed_txt.splitlines()
    stale, extended = [], {}
    for name in ("AGENTS.md", "CLAUDE.md"):
        f = plant / name
        if not f.exists():
            continue
        txt = f.read_text(errors="replace")
        if txt == seed_txt:
            continue
        added = _plant_added_lines(seed_lines, txt.splitlines())
        if added is None:
            stale.append(name)
        else:
            extended[name] = added
    ok = True
    if stale:
        ok = False
        print(f"  !! KERNEL STALE: {', '.join(stale)} differ(s) from the seed "
              f"core/AGENTS.md — the graft left the plant on an old kernel; "
              f"fast-forward the kernel body (re-run install / place_kernel)")
    if extended:
        n = max(extended.values())
        dev = _standing_kernel_deviation(plant)
        if dev:
            print(f"  kernel: seed body current + {n} plant-authored line(s) in "
                  f"{', '.join(extended)} — standing deviation {dev[0]} "
                  f"(ends_when: {dev[1] or 'unstated'})")
        else:
            ok = False
            print(f"  !! KERNEL EXTENDED: {', '.join(extended)} carr(ies) {n} "
                  f"plant-authored line(s) beyond the seed core/AGENTS.md with no "
                  f"standing deviation node — record docs/graph/nodes/deviation.<slug>.md "
                  f"(kind: deviation, status: standing, departs_from: "
                  f"{KERNEL_DEVIATION_KEY}) or move the lines into a graph node "
                  f"the kernel routes to")
    if not stale and not extended:
        print("  kernel: current (plant AGENTS.md/CLAUDE.md == seed core/AGENTS.md)")
    return ok


CONFIG_KEY_RE = re.compile(r"^(ROOT_ID|KINDS|KIND_PREFIX|TEST_GLOBS)\s*=")


def _strip_config_assignments(text: str) -> str:
    """Blank out the PROJECT CONFIG assignments, continuation lines included.
    They are legitimately plant-specific, and one of them can span several
    physical lines in the seed and one in the plant (or the reverse): only the
    first line matches the config-key pattern, so a continuation line would
    read as a seed engine line missing from the plant, a false STALE on a gate
    that BLOCKS the graft. Lines are blanked rather than dropped so any later
    line-numbered report stays honest."""
    out, depth = [], 0
    for line in text.splitlines():
        if depth == 0 and not CONFIG_KEY_RE.match(line):
            out.append(line)
            continue
        code = _strip_inline_comment(line)
        depth += sum(code.count(o) for o in "([{") - sum(code.count(c) for c in ")]}")
        depth = max(depth, 0)
        out.append("")
    return "\n".join(out)


SCHEMA_HEADING_RE = re.compile(r"^#{2,6}\s+(.+?)\s*$")
SCHEMA_KEY_RE = re.compile(r"^([a-z_][a-z0-9_]*):")
SCHEMA_TERM_RE = re.compile(r"^[|-]\s*`([^`]+)`")


def _schema_names(text: str) -> dict:
    """What the node contract NAMES, as {comparable: as-written}: the sections
    it is organised into, the frontmatter keys it declares in its fenced
    example, and the vocabulary it defines in a table row or a definition
    bullet — anything whose row or bullet opens with a backticked term. Those
    are the terms every other check is written against; the prose around them
    is the plant's to re-integrate in its own words."""
    names, fenced = {}, False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            continue
        m = SCHEMA_KEY_RE.match(s) if fenced else (SCHEMA_HEADING_RE.match(s) or
                                                   SCHEMA_TERM_RE.match(s))
        if m:
            # `composes` and `composes:` are the same term named twice —
            # once as a key, once as an edge the prose defines.
            names.setdefault(m.group(1).casefold().rstrip(":"), m.group(1))
    return names


def _schema_currency(plant: Path, seed: Path) -> bool:
    """Report whether the plant's node schema still matches the seed's.

    `_schema.md` is the node CONTRACT — the vocabulary every other check is
    written against — but the installer places it add-if-missing, so a plant
    that already has one keeps it across every graft. A plant can end up
    carrying a schema several minors old, missing an entire lifecycle-status
    vocabulary that the seed's own migration tool writes values into, and
    nothing reports it.

    Reports, never rewrites, and does not gate — the same posture the engine
    check takes on staleness. The schema is the plant's own file and a plant
    may legitimately extend it; blocking would push a steward to overwrite
    authored content to clear a gate. The comparison is over what the contract
    NAMES and not over the sentences it names them in, for the same reason: a
    schema somebody re-integrated in their own words reads as hundreds of
    absent lines, and the one edit that clears that message is the verbatim
    paste this posture exists to avoid. Returns True always; the verdict is the
    output."""
    ss = seed / "templates/knowledge-graph/_schema.md"
    ps = plant / "docs/graph/_schema.md"
    if not ss.is_file() or not ps.is_file():
        return True
    seed_names = _schema_names(ss.read_text(errors="replace"))
    plant_names = _schema_names(ps.read_text(errors="replace"))
    missing = [d for n, d in seed_names.items() if n not in plant_names]
    if missing:
        shown = ", ".join(missing[:12]) + (" …" if len(missing) > 12 else "")
        print(f"  !! node schema STALE: {len(missing)} term(s) the seed contract "
              f"names have no counterpart in docs/graph/_schema.md — the plant "
              f"is linted against a contract older than the machinery it now "
              f"runs; reconcile it (the plant's own wording and extensions "
              f"stay): {shown}")
    else:
        print("  node schema: current (every term the seed contract names "
              "has a home in the plant's)")
    return True


def _engine_currency(spec: str) -> bool:
    """Compare the plant's engine against the seed's. `spec` is the PAIR
    `<plant-file>:<seed-file>`.

    A malformed spec used to be swallowed and announced as a parenthetical
    skip, so the gate simply did not run while the audit still exited on its
    other checks — the "green lie" the graft protocol forbids. A caller who
    asked for this check and did not get it must be told loudly."""
    parts = spec.split(":", 1)
    if len(parts) != 2 or not all(x.strip() for x in parts):
        print(f"  !! --engine wants <plant-file>:<seed-file>, got {spec!r} — "
              f"refusing to report an engine check that did not run")
        return False
    pf, sf = (Path(x.strip()) for x in parts)
    for f, side in ((pf, "plant"), (sf, "seed")):
        if not f.is_file():
            print(f"  !! --engine {side} file does not exist: {f} — "
                  f"refusing to report an engine check that did not run")
            return False
    try:
        pl = _code_lines(_strip_config_assignments(pf.read_text(errors="replace")))
        sl = _code_lines(_strip_config_assignments(sf.read_text(errors="replace")))
    except OSError as e:
        print(f"  !! --engine could not read a file: {e} — "
              f"refusing to report an engine check that did not run")
        return False
    missing = sl - pl
    if missing:
        print(f"  !! graph engine STALE: {pf}: {len(missing)} seed engine line(s) "
              f"absent from the plant — reconcile with graft-graph-engine.py")
    else:
        print(f"  graph engine: current: {pf} (no seed engine line missing from plant)")
    return True


if __name__ == "__main__":
    sys.exit(main())
