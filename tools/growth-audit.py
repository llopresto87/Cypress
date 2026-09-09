#!/usr/bin/env python3
"""growth-audit: prove a growth or a graft actually GREW what it planned to grow.

THE PROBLEM THIS CLOSES

`grow` and `graft` both promise coverage and neither could be held to it. The
growth completeness ledger was prose an orchestrating model filled in about its
own work, written to gitignored scratch and discarded when the run ended — so a
plant carried no durable answer to "what did growth cover, and what did it
deliberately leave alone?". A later session, and the next graft, could not tell
a collection that is empty because the source has no such evidence from one
that is empty because nobody ever looked. `graft-audit.py --unfilled` catches
only the narrow case of a leaf still byte-identical to its template; a one-word
edit passes it, and a collection with no template leaf at all is invisible to
it. The result is the failure this tool exists to make impossible: plants whose
design/, legal/, or library pages were never grown, reported as grown.

THE PIPELINE

    inventory  ->  plan  ->  growth/graft  ->  lint --+
    (what the     (what      (author it)      (this tool:  |
     project       growth                      did every   |
     is made of)   owes it)                    planned     |
        ^                                      artifact    |
        |                                      appear?)    |
        +----------- repeat while findings remain ---------+

The loop is the point. A finding is not a report the run ends on — it names a
row that is still owed, so the run goes back: an item the scouts missed extends
the INVENTORY, an artifact nobody owed extends the PLAN, an artifact that was
owed and never written sends an author back to write it, and the lint runs
again. The gate is green or the cycle turns; there is no third outcome and no
budget at which a red gate becomes acceptable.

INVENTORY is what the growth scouts found the project to actually be made of:
each language and its version, each runtime and framework, each direct
dependency, the infrastructure it runs on, its data stores, the external and AI
services it calls, its design surface, its regulatory exposure. One row per
item, each anchored to the source path that proves it.

PLAN turns each inventory item into the artifacts growth owes it — a library
page for a framework, a best-practices page stating the external standard that
framework is held to, a legal page for a regulatory exposure, a design leaf for
a screen surface — and records whether the item requires EXTERNAL GROUNDING:
upstream documentation retrieved from the open web this run by a research-scout
and normalized under docs/graph/sources/. `--plan` writes those defaults; the
orchestrator edits and extends them. Planning is a recorded stage, not a
decision a model makes silently in its own head.

LINT (the default mode) reads the plan back after the work and checks, per row,
that every planned artifact exists, is substantive rather than a scaffold, and
that every grounding obligation resolves to a real retrieved source. What is
genuinely absent must say so with a reason and the paths that were searched.
Nothing here is a matter of judgment: a planned artifact is present or it is
not.

THE RECORD

    <plant>/.cypress/coverage.json

Tracked, beside the plant's `.cypress/seed.json` stamp — NOT under
`.cypress/growth/`, which is the run's transient scratch, and not under
`docs/graph/`, which is the plant's own knowledge. The coverage record is a
fact about the seed's work on the plant, so it lives with the seed's other
plant-side state and survives the run that wrote it.

WHAT MAKES IT DETERMINISTIC

Three of the four sets of required rows are derived from something other than
the record itself, so a row cannot go missing by being left out:

  * one COLLECTION row per knowledge collection the installer creates
    (every top-level directory and leaf of the seed's templates/docs/**),
  * one AGENT row per roster agent that declares `plant_knowledge:` — the
    collections that agent must be able to read to do its job at all,
  * one EXPERT row per project-specific expert the PLANT's own graph carries
    (anything under docs/graph/agents/ that is not `origin: seed`), which is
    the supply side of the staffing question,
  * one INVENTORY row per item the scouts found, each carrying its own
    planned artifacts and — where the item is a dominant domain or a core
    part of the stack — its own staffing decision, the demand side.

A graft to a newer seed that adds a collection or an agent therefore adds
required rows the plant does not yet answer, and they surface as MISSING until
the graft grows them. That is the "grafted is not grown" gap, made mechanical.

VERDICTS (a row fails the gate unless noted)

  MISSING      a required row is absent from the record entirely
  BLANK        the row exists with no status — growth never reached it
  UNGROWN      a planned artifact does not exist in the plant
  HOLLOW       a planned artifact exists but is not one: byte-identical to
               its seed template (for an expert, to the agent template or to a
               seed agent), still carrying {{placeholders}}, too small to carry
               a fact, or — for an expert — missing the frontmatter that makes
               it a node the graph and the harness can use
  UNGROUNDED   an item requiring external grounding cites no retrieved source
               that resolves under docs/graph/sources/
  DANGLING     a COVERED row cites evidence paths that do not exist
  UNJUSTIFIED  an ABSENT row gives no reason, or no paths it searched
  CONTRADICTED a collection is claimed COVERED but holds only scaffolds or
               `.unfilled.md` markers — the plant's own files disagree
  UNSTAFFED    a surface that has to answer the staffing question records no
               decision, answers it with something other than a boolean,
               gives no reason, or names a project-specific expert the plant
               does not carry. Deliberately its own verdict rather than BLANK
               or UNJUSTIFIED: those speak about a ROW that was left unfilled,
               while this speaks about the PROJECT — a surface with nobody
               assigned to it. The row itself may be complete and correct.
  STALE        the record was written against an older seed than the plant now
               carries; re-plan before trusting it
  UNKNOWN      an honest blocker, named. Reported always, never a failure —
               the one legitimate way a row stays uncovered.

Usage:
  growth-audit.py <plant-root> <seed-root>            lint (the gate)
  growth-audit.py <plant-root> <seed-root> --plan     create/refresh the plan
  growth-audit.py <plant-root> <seed-root> --agents   agent + expert rows only
        (the inventory's staffing decisions are part of the full lint, not this)
  growth-audit.py <plant-root> <seed-root> --json     machine-readable findings

Exit 0 when every required row is answered and every planned artifact is
present and substantive; 1 on any failing verdict; 2 on a malformed command
line or an unreadable record. Dependency-free.
"""
import json
import re
import sys
from pathlib import Path

SCHEMA = "cypress.coverage/1"
RECORD_REL = ".cypress/coverage.json"
STAMP_REL = ".cypress/seed.json"
GRAPH_HOME = "docs/graph"
TEMPLATE_DOCS = "templates/docs"
UNFILLED_SUFFIX = ".unfilled.md"

STATUSES = ("COVERED", "ABSENT", "UNKNOWN")
# Every verdict this tool can emit. The protocols quote from this set for their
# own readers; seed-lint holds them to it, so a protocol cannot promise a check
# that no longer exists.
VERDICTS = ("MISSING", "BLANK", "UNGROWN", "HOLLOW", "UNGROUNDED", "DANGLING",
            "UNJUSTIFIED", "CONTRADICTED", "UNSTAFFED", "STALE", "UNKNOWN")

# A leaf smaller than this carries a heading and nothing else. It is the floor
# for "a file that states a fact", not a quality bar — quality is the
# reviewer's job, presence is this tool's.
#
# The measurement is of the AUTHORED body: the lines this plant added on top of
# whatever the seed's template at that path already said. Byte-difference alone
# was the first version of this check and it was worthless — appending one
# character to the seed's own `design/README.md` or `legal/index.md` made those
# collections read as covered, which is precisely the "a one-word edit passes"
# failure this tool exists to close. A leaf that inherits its whole body from
# the template has been touched, not filled.
MIN_SUBSTANTIVE_BYTES = 400
# `${{ ... }}` is a GitHub Actions expression, not an unfilled placeholder, and
# a runbook authored from real CI evidence is full of them. Same for anything
# that looks like an expression rather than a prompt to the author.
PLACEHOLDER = re.compile(r"(?<!\$)\{\{\s*([^}]*?)\s*\}\}")
PLACEHOLDER_PROSE = re.compile(r"^[A-Za-z][A-Za-z0-9 ,'/-]*$")

# Inventory kinds and what growth owes each. `expect` paths are templates
# resolved against the item's slug; `grounding` says whether the item must cite
# upstream documentation retrieved from the open web during this run. These are
# the defaults `--plan` writes — the orchestrator extends them from evidence,
# but it may not silently drop one: lint requires every item to carry at least
# one planned artifact.
#
# The third column says whether the item also owes an EXPERTISE NODE — the
# Tier-2 handle that says when this stack element is in play, what must not be
# done without it, and which sub-expertises apply under which condition. Six
# kinds owe one because they are the stack a worker writes against; the other
# four already have a routable owner for their depth (prompts/, design/,
# legal/, architecture/) and would gain a pass-through node, not a home.
KIND_PLAN = {
    "language":            (["libraries/{slug}.md", "best-practices/{slug}.md"], True, True),
    "runtime":             (["libraries/{slug}.md", "best-practices/{slug}.md"], True, True),
    "framework":           (["libraries/{slug}.md", "best-practices/{slug}.md"], True, True),
    "dependency":          (["libraries/{slug}.md"], True, True),
    "infrastructure":      (["architecture/{slug}.md", "best-practices/{slug}.md"], True, True),
    "datastore":           (["data/{slug}.md", "best-practices/{slug}.md"], True, True),
    "external-service":    (["architecture/{slug}.md"], True, False),
    "ai-provider":         (["prompts/{slug}.md", "evaluations/{slug}.md"], True, False),
    "design-surface":      (["design/{slug}.md"], True, False),
    "regulatory-exposure": (["legal/{slug}.md"], True, False),
    "domain":              ([], False, False),
}
# An incidental dependency earns an index line, not a page of its own, and
# nothing is retrieved for it. Significance is the scout's call, recorded.
SIGNIFICANCE = ("core", "significant", "incidental")
# The kinds whose expertise node must route to the item's own pin home. These
# are the ones whose depth IS a library page, so a node that does not name it
# in `libraries:` points at nothing and the version distinction has no home.
PINNED_KINDS = ("language", "runtime", "framework", "dependency")
EXPERTISE_PATH = "nodes/expertise.{slug}.md"

# The inventory kinds that must answer the staffing question. A dominant domain
# is what the evidence ledger's §9 specialist signal exists for, and a core item
# is the other place an ad-hoc expert is plausibly earned. The default answer is
# now the expertise node above, which is owed mechanically rather than decided;
# a spawnable AGENT is warranted only for what a node cannot serve, and the
# decision names which of those four it is.
STAFFED_KINDS = ("domain",)
# What an agent can do that an expertise node cannot. A staffing decision that
# says `warranted: true` names one of these, because "this surface is important"
# is not a reason to spawn: knowledge composes through the graph for free, and
# only a different tool grant, model class, stance, or context boundary needs an
# agent of its own.
SPAWN_TRIGGERS = ("tools", "model", "stance", "isolation")


class Finding:
    def __init__(self, verdict, row, detail):
        self.verdict, self.row, self.detail = verdict, row, detail

    def fatal(self):
        return self.verdict != "UNKNOWN"

    def __str__(self):
        return f"  {self.verdict:<12} {self.row}\n               {self.detail}"


def die(msg, code=2):
    print(f"  !! {msg}")
    sys.exit(code)


def parse_args():
    a, pos, opt = sys.argv[1:], [], {}
    for x in a:
        if x.startswith("--"):
            key = x[2:]
            if key not in ("plan", "agents", "json"):
                die(f"unknown option --{key}")
            opt[key] = True
        else:
            pos.append(x)
    if len(pos) != 2:
        print(__doc__)
        sys.exit(2)
    return Path(pos[0]), Path(pos[1]), opt


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name).strip().lower()).strip("-")


def majors_in_play(rec, slug):
    """The distinct major versions the inventory records for one slug. Two
    majors of the same stack running at once is the one case where
    applicability genuinely differs by version — hosting model, defaults,
    what the compiler accepts — and the only case where a version enters a
    node id at all."""
    majors = []
    for item in rec.get("inventory", []):
        if (item.get("slug") or slugify(item.get("name", ""))) != slug:
            continue
        # A major is read from the front of the version, or from a target
        # framework moniker (`net8.0`, `.NET 8`) where that is what the scouts
        # recorded — the same fact wearing the ecosystem's own spelling.
        raw = str(item.get("version") or "")
        m = re.match(r"\s*v?(\d+)", raw) or re.search(r"(\d+)", raw)
        if m and m.group(1) not in majors:
            majors.append(m.group(1))
    # Sorted as numbers: as strings, 10 sorts before 8 and the message reads
    # like the older major is the newer one.
    return sorted(majors, key=int) if len(majors) > 1 else []


def planned_artifacts(item, majors=()):
    """Everything an inventory item owes the graph, in one place: the base
    artifacts its kind implies, the incidental exception, the expertise node,
    and — where a plant runs two majors of one stack — one version-qualified
    child per major. Returns (expect rows, grounding required).

    The incidental rule is the pre-7.5.0 behaviour, unchanged: an incidental
    DEPENDENCY earns an index line and nothing retrieved, while an incidental
    item of any other kind keeps its kind's pages and its grounding. What is
    new is that no incidental item owes an expertise node — the graph gains a
    routing handle for the stack a worker writes against, not for every name
    in the lockfile."""
    kind = item.get("kind", "")
    slug = item.get("slug") or slugify(item.get("name", ""))
    paths, ground, expertise = KIND_PLAN.get(kind, ([], False, False))
    incidental = item.get("significance") == "incidental"
    if incidental and kind == "dependency":
        return [{"path": "libraries/index.md",
                 "why": f"{kind} {slug} — incidental"}], False
    rows = [{"path": p.format(slug=slug), "why": f"{kind} {slug}"} for p in paths]
    if incidental or not expertise:
        return rows, ground
    rows.append({"path": EXPERTISE_PATH.format(slug=slug),
                 "why": f"{kind} {slug} — applicability and composition"})
    for major in majors:
        rows.append({"path": EXPERTISE_PATH.format(slug=f"{slug}-{major}"),
                     "why": f"{kind} {slug} major {major} — applicability for "
                            f"this major, composed by expertise.{slug}"})
    return rows, ground


# ---------------------------------------------------------------- seed truth

def required_collections(seed):
    """Every knowledge collection the installer creates, derived from the seed's
    templates/docs/** — the same walk place_docs_skeleton does. A directory is
    one collection row; a leaf that sits at the root of templates/docs (or is a
    runbook, where each file is its own procedure) is a row of its own. Deriving
    this from the seed is what stops a collection from being forgotten: adding a
    template to the seed adds a required row to every plant's next audit."""
    troot = seed / TEMPLATE_DOCS
    if not troot.is_dir():
        die(f"{seed} has no {TEMPLATE_DOCS}/ — not a seed root")
    rows = set()
    for t in sorted(p for p in troot.rglob("*") if p.is_file()):
        rel = t.relative_to(troot).as_posix()
        parts = rel.split("/")
        if len(parts) == 1:
            if parts[0] == "README.md":
                continue          # the shape's own preamble, not a collection
            rows.add(rel)         # changelog.md and friends: leaf-as-collection
        elif parts[0] == "runbooks":
            rows.add(rel)         # each runbook is its own procedure to cover
        elif parts[0] == "nodes":
            continue              # blank forms, filled per node, never as a set
        else:
            rows.add(parts[0] + "/")
    return sorted(rows)


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm, current = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+-\s+", line) and current is not None:
            fm[current].append(line.split("-", 1)[1].strip().strip('"'))
            continue
        kv = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val == "":
                fm[key], current = [], key
            else:
                fm[key], current = val, None
    return fm


def required_agents(seed):
    """One row per roster agent that declares `plant_knowledge:` — the plant
    collections it must be able to read before it can do its job on this
    project. An agent that declares one and finds nothing is the defect this
    reports.

    Not declaring is a decision, not an oversight, and three classes of agent
    make it: those that work from what their brief hands them rather than from
    standing project knowledge (`devils-advocate` attacks the artifact under
    review; `orchestrator` routes from the router, which every plant has by
    construction); those that run BEFORE a graph exists (`growth-scout`,
    `growth-orchestrator`, `seed-installer`); and those whose reads are already
    another agent's declared row, where a second row would report the same
    absence twice without adding a signal."""
    out = {}
    adir = seed / "agents"
    if not adir.is_dir():
        die(f"{seed} has no agents/ — not a seed root")
    for p in sorted(adir.glob("*.md")):
        fm = parse_frontmatter(p)
        reads = fm.get("plant_knowledge") or []
        if isinstance(reads, str):
            reads = [reads]
        if reads:
            out[str(fm.get("name") or p.stem)] = list(reads)
    return out


class Templates(dict):
    """The seed's `templates/docs/**` indexed by the plant-relative path each
    leaf installs to, and the seed root beside it.

    The seed root rides along because two artifact classes have no template at
    their own path — an agent node and an expertise node are authored from a
    form that lives nowhere near them — and `is_substantive()` is the one place
    that has to find it. Threading the seed through every lint function's
    signature instead would put a second parameter on callers that have no
    other use for it (`lint_inventory` has none at all)."""

    def __init__(self, seed):
        troot = seed / TEMPLATE_DOCS
        super().__init__(
            (p.relative_to(troot).as_posix(), p.read_bytes())
            for p in troot.rglob("*") if p.is_file())
        self.seed = seed


def template_bytes(seed):
    return Templates(seed)


def scaffold_for(seed, rel):
    """What a plant file at `rel` must not still be, when the seed ships no
    template at that same path: the form it was authored from, plus every seed
    file a copy of which would be byte-identical to it.

    Two artifact classes need this. An agent node's form is
    `templates/agent.template.md`, and a seed agent copied under a new name is
    the other way a roster entry can be a form rather than an expert. An
    expertise node's form is `templates/docs/nodes/_expertise.template.md`,
    which installs under `nodes/` beside the node itself but with a leading
    underscore, so the same-path lookup never finds it. Without this, the
    form's own instructional prose counts as the plant's authored content and
    a filled-in scaffold reads as knowledge — the hole this tool exists to
    close, reopened once per template-less artifact.

    Returns (template text or None, the set of byte-identical scaffolds)."""
    if rel.startswith("agents/"):
        tmpl = seed / "templates" / "agent.template.md"
        blobs = {p.read_bytes() for p in (seed / "agents").glob("*.md")}
    elif re.match(r"^nodes/expertise\.[a-z0-9.-]+\.md$", rel):
        tmpl = seed / "templates" / "docs" / "nodes" / "_expertise.template.md"
        blobs = set()
    else:
        return None, set()
    text = None
    if tmpl.is_file():
        blobs.add(tmpl.read_bytes())
        text = tmpl.read_text(encoding="utf-8", errors="replace")
    return text, blobs


# ------------------------------------------------------------ plant material

def _body(text):
    return text.split("\n---\n", 1)[-1] if text.startswith("---\n") else text


def _norm(line):
    """A template line and the same line with its placeholder braces rubbed off
    are the same inherited line. Deleting `{{` and `}}` was the cheapest way to
    make a template stop looking like one — every line then differed from its
    source and the whole form read as authored content."""
    return re.sub(r"\s+", " ", line.replace("{{", "").replace("}}", "")).strip()


def authored_bytes(text, template_text):
    """Bytes of non-blank lines the leaf holds that its seed template does not.
    A leaf at a path the seed ships a template for (a collection README, an
    index, a runbook) is only as grown as the lines the plant added; a leaf the
    seed has no template for is authored in full."""
    inherited = {_norm(ln) for ln in _body(template_text).splitlines() if _norm(ln)}
    return sum(len(ln.strip()) for ln in _body(text).splitlines()
               if _norm(ln) and _norm(ln) not in inherited)


def is_substantive(plant, rel, templates):
    """A file states a fact when it exists, keeps no unfilled {{placeholder}},
    and carries enough of its OWN content — measured against the seed template
    it was authored from — to hold one. Deliberately mechanical: this asks
    whether growth reached the file, not whether what it wrote is good.

    The template is normally the seed's file at the SAME path; where the seed
    ships none there, `scaffold_for()` resolves the form the artifact was
    authored from (an agent node, an expertise node) and the seed files a copy
    would be identical to. Without that resolution the form's own instructional
    prose counts as this plant's authored content and a filled-in scaffold
    reads as knowledge."""
    f = plant / GRAPH_HOME / rel
    if not f.is_file():
        return False, "does not exist"
    raw = f.read_bytes()
    template = templates.get(rel)
    if template is None:
        # No template at this path: resolve the form the artifact was authored
        # from. `blobs` already contains that form's bytes, so the identity
        # test below is subsumed and only the same-path case still needs it.
        text_t, blobs = scaffold_for(templates.seed, rel)
        if raw in blobs:
            return False, ("byte-identical to the form it was authored from, "
                           "or to a seed file copied as a starting point")
        template = text_t.encode("utf-8") if text_t is not None else None
    elif template == raw:
        return False, "byte-identical to its seed template (an unfilled scaffold)"
    text = raw.decode("utf-8", errors="replace")
    for m in PLACEHOLDER.finditer(_body(text)):
        if PLACEHOLDER_PROSE.match(m.group(1)):
            return False, f"still carries the template placeholder {m.group(0)}"
    written = authored_bytes(text, (template or b"").decode("utf-8", errors="replace"))
    if written < MIN_SUBSTANTIVE_BYTES:
        detail = (f"holds {written} bytes this plant wrote — under the "
                  f"{MIN_SUBSTANTIVE_BYTES}-byte floor for a leaf that states "
                  f"a fact")
        if template is not None:
            detail += " (the rest is inherited from its seed template)"
        return False, detail
    return True, ""


def collection_leaves(plant, name):
    """Files under a collection, split into the ones that carry knowledge and
    the `.unfilled.md` markers that record a deliberate blank."""
    if name.endswith("/"):
        d = plant / GRAPH_HOME / name.rstrip("/")
        files = sorted(p for p in d.rglob("*.md")) if d.is_dir() else []
    else:
        f = plant / GRAPH_HOME / name
        marker = f.with_name(f.stem + UNFILLED_SUFFIX)
        files = [q for q in (f, marker) if q.is_file()]
    live = [p for p in files if not p.name.endswith(UNFILLED_SUFFIX)]
    unfilled = [p for p in files if p.name.endswith(UNFILLED_SUFFIX)]
    return live, unfilled


def resolves(plant, ref):
    """A cited path resolves when it names a real file INSIDE the plant. Line
    and anchor suffixes (`path:12`, `path#section`, `path:12:5`) are stripped
    first — a citation points at a place in a file, and the file is what must
    exist. A directory is not a citation (`docs/graph/sources/` names where the
    evidence would live, not any evidence), and an absolute path is not a claim
    about this plant at all."""
    raw = str(ref).split("#", 1)[0]
    raw = re.sub(r":\d+(?::\d+)?(-\d+)?$", "", raw).strip()
    if not raw or Path(raw).is_absolute():
        return False
    target = plant / raw
    try:
        target.resolve().relative_to(plant.resolve())
    except (ValueError, OSError):
        return False
    return target.is_file()


# ------------------------------------------------------------------- record

def load_record(plant):
    f = plant / RECORD_REL
    if not f.is_file():
        return None
    try:
        rec = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{RECORD_REL} is not valid JSON: {e}")
    if not isinstance(rec, dict):
        die(f"{RECORD_REL} must hold a JSON object")
    return rec


def seed_version(seed):
    mf = seed / "manifest.json"
    if mf.is_file():
        try:
            return json.loads(mf.read_text(encoding="utf-8")).get("version")
        except json.JSONDecodeError:
            return None
    return None


def _stamp(plant):
    f = plant / STAMP_REL
    if f.is_file():
        try:
            val = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(val, dict):
                return val
        except json.JSONDecodeError:
            return {}
    return {}


def plant_seed_version(plant):
    return _stamp(plant).get("version")


def plant_projections(plant):
    """The harness directories this plant's roster is projected into, read from
    the stamp `install.sh` wrote. The installer owns that mapping because the
    installer is what creates the directories; keeping a copy here was a second
    home for one fact, and a second home drifts — a renamed directory or a
    changed filename pattern would have gone on being demanded, or stopped
    being demanded, with nothing to notice.

    Returns None when the stamp records none, which is a different answer from
    "this plant has no harnesses" and is reported as such rather than passing
    every projection check by default."""
    raw = _stamp(plant).get("agent_projections")
    if not isinstance(raw, list):
        return None
    out = []
    for entry in raw:
        if isinstance(entry, dict) and str(entry.get("path") or "").strip():
            out.append((str(entry.get("tool") or "a harness"),
                        str(entry["path"]), bool(entry.get("verbatim"))))
    return out


def plant_experts(plant, seed):
    """Every expert the PLANT authored, derived from its own graph rather than
    from the record — `docs/graph/agents/` is where 6.0.0 put every agent node,
    and anything there the SEED did not put there is this project's own.

    Seed-ness is derived from the seed's roster, never from the file's own
    `origin:`. Trusting the declaration inverted the check it was paired with:
    an expert copied from a seed agent as a starting point keeps `origin: seed`,
    and the one wrong value the `origin: project` finding exists to catch was
    the single value that made the file invisible to it.

    Keyed by FILE STEM, because that is what the installer projects by
    (`03-reviewer.md` -> `.claude/agents/03-reviewer.md`). Keying by the
    frontmatter `name` asked for a projection at a path nothing writes, and
    collapsed two files that happened to share a name into one row."""
    out = {}
    adir = plant / GRAPH_HOME / "agents"
    if not adir.is_dir():
        return out
    seeded = {p.stem for p in (seed / "agents").glob("*.md")}
    for p in sorted(adir.glob("*.md")):
        if p.stem in seeded:
            continue
        fm = parse_frontmatter(p)
        reads = fm.get("plant_knowledge") or []
        if isinstance(reads, str):
            reads = [reads]
        out[p.stem] = {"path": p, "origin": str(fm.get("origin") or "").strip(),
                       "declared_name": str(fm.get("name") or "").strip(),
                       "reads": list(reads)}
    return out


def needs_staffing(item):
    """Whether an inventory item has to answer the staffing question at all."""
    return (item.get("kind") in STAFFED_KINDS
            or item.get("significance") == "core")


def blank_row(**kw):
    row = {"status": "", "evidence": [], "reason": "", "searched": [],
           "blocker": ""}
    row.update(kw)
    return row


def do_plan(plant, seed, opt):
    """Create or refresh the plan. Required collection and agent rows come from
    the seed, so a seed that grew a new collection gives every plant a new blank
    row to answer. Rows already filled are preserved verbatim — planning never
    overwrites a verdict growth earned. Each inventory item gets its planned
    artifacts and its grounding obligation filled in from its kind where they
    are empty."""
    rec = load_record(plant) or {}
    rec["schema"] = SCHEMA
    rec.setdefault("run", "grow")
    rec["seed_version"] = seed_version(seed)
    rec.setdefault("inventory", [])

    added = []
    cols = {c.get("name"): c for c in rec.get("collections", []) if c.get("name")}
    for name in required_collections(seed):
        if name not in cols:
            cols[name] = blank_row(name=name, leaves=0)
            added.append(f"collection {name}")
    rec["collections"] = [cols[k] for k in sorted(cols)]

    ags = {a.get("name"): a for a in rec.get("agents", []) if a.get("name")}
    for name, reads in required_agents(seed).items():
        if name not in ags:
            ags[name] = blank_row(name=name, reads=reads, artifacts=[])
            added.append(f"agent {name}")
        else:
            ags[name]["reads"] = reads      # the seed owns this fact, not the record
    rec["agents"] = [ags[k] for k in sorted(ags)]

    # The expert set comes from the plant's own graph, so an expert authored in
    # Phase 4 becomes a required row on the next plan — and stays one.
    exs = {e.get("name"): e for e in rec.get("experts", []) if e.get("name")}
    for name, info in plant_experts(plant, seed).items():
        if name not in exs:
            exs[name] = blank_row(name=name, motivated_by=[],
                                  home=f"{GRAPH_HOME}/agents/{name}.md")
            added.append(f"expert {name}")
        exs[name]["reads"] = info["reads"]   # the agent file owns this fact
    rec["experts"] = [exs[k] for k in sorted(exs)]

    majors = {}
    for item in rec["inventory"]:
        slug = item.get("slug") or slugify(item.get("name", ""))
        item["slug"] = slug
        # Computed once per slug: it walks the whole inventory, and the hint
        # loop below asks the same question of the same rows.
        if slug not in majors:
            majors[slug] = majors_in_play(rec, slug)
        expect, ground = planned_artifacts(item, majors[slug])
        if not item.get("expect"):
            item["expect"] = expect
        item.setdefault("grounding", {})
        item["grounding"].setdefault("required", ground)
        item["grounding"].setdefault("sources", [])
        if needs_staffing(item):
            item.setdefault("expert", {})

    out = plant / RECORD_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    # A `domain` item has no mechanical mapping — what a dominant domain owes
    # the graph is whatever its evidence names. Say so here rather than letting
    # the lint reject, as an unexplained BLANK, the very plan this just wrote.
    handwritten = [i.get("name") for i in rec["inventory"]
                   if i.get("kind") == "domain" and not i.get("expect")]
    blank = [c["name"] for c in rec["collections"] if not c.get("status")]
    blank += [f"agent:{a['name']}" for a in rec["agents"] if not a.get("status")]
    print(f"  planned {out}")
    print(f"  collections: {len(rec['collections'])}   "
          f"agents: {len(rec['agents'])}   experts: {len(rec['experts'])}   "
          f"inventory items: {len(rec['inventory'])}")
    for a in added:
        print(f"  NEW ROW      {a}")
    if not rec["inventory"]:
        print("  !! the inventory is empty — growth has nothing to be held to. "
              "Fill it from the scouts' reconciled ledgers (one row per "
              "language, runtime, framework, dependency, infrastructure "
              "component, datastore, external/AI service, design surface, and "
              "regulatory exposure the source shows) and re-run --plan.")
        return 1
    for name in handwritten:
        print(f"  NEEDS EXPECT domain {name} — name the artifacts this domain "
              f"owes the graph; the tool cannot derive them")
    for item in rec["inventory"]:
        slug = item.get("slug", "")
        if majors.get(slug) and KIND_PLAN.get(item.get("kind", ""), ((), False, False))[2]:
            print(f"  NEEDS COMPOSITION {slug} runs majors "
                  f"{', '.join(majors[slug])} — expertise.{slug} composes one child "
                  f"per major, and each child's load_when carries that "
                  f"target's own tokens")
        if needs_staffing(item) and "warranted" not in (item.get("expert") or {}):
            print(f"  NEEDS EXPERT {item.get('kind', 'item')} "
                  f"{item.get('name', '?')} — this surface owes an expertise "
                  f"node either way; record whether it ALSO warrants an agent "
                  f"of its own, and which of {', '.join(SPAWN_TRIGGERS)} that "
                  f"agent needs which a node cannot serve")
    if blank:
        print(f"  {len(blank)} row(s) still unanswered — that is the work, "
              f"not a defect, until growth declares itself done.")
    return 0


# --------------------------------------------------------------------- lint

def check_row_shape(label, row, findings):
    """Every answered row keeps the promise its status makes: COVERED cites
    evidence, ABSENT names a reason and where it looked, UNKNOWN names its
    blocker. A status outside the vocabulary is not a lesser answer, it is no
    answer."""
    status = (row.get("status") or "").strip().upper()
    if not status:
        findings.append(Finding("BLANK", label,
                                "no status — growth never reached this row"))
        return None
    if status not in STATUSES:
        findings.append(Finding("BLANK", label,
                                f"status {status!r} is not one of "
                                f"{', '.join(STATUSES)}"))
        return None
    if status == "ABSENT":
        if not (row.get("reason") or "").strip():
            findings.append(Finding("UNJUSTIFIED", label,
                                    "ABSENT with no reason — an absence is a "
                                    "fact only when it is established"))
        elif not row.get("searched"):
            findings.append(Finding("UNJUSTIFIED", label,
                                    "ABSENT with a reason but no searched "
                                    "paths — name where you looked"))
    if status == "UNKNOWN" and not (row.get("blocker") or "").strip():
        findings.append(Finding("UNJUSTIFIED", label,
                                "UNKNOWN with no named blocker"))
    return status


def lint_collections(plant, seed, rec, templates, findings):
    have = {c.get("name"): c for c in rec.get("collections", []) if c.get("name")}
    for name in required_collections(seed):
        label = f"collection {name}"
        row = have.get(name)
        if row is None:
            findings.append(Finding("MISSING", label,
                                    "the seed installs this collection and the "
                                    "record does not answer for it — re-run "
                                    "--plan, then cover it or establish its "
                                    "absence"))
            continue
        status = check_row_shape(label, row, findings)
        if status is None:
            continue
        live, unfilled = collection_leaves(plant, name)
        if status == "COVERED":
            substantive = [p for p in live
                           if is_substantive(
                               plant,
                               p.relative_to(plant / GRAPH_HOME).as_posix(),
                               templates)[0]]
            if not substantive:
                detail = ("claimed COVERED but holds no leaf that states a "
                          "fact")
                if unfilled:
                    detail += (f" — {len(unfilled)} leaf/leaves are "
                               f"`.unfilled.md`, the plant's own record that "
                               f"it declined to fill them")
                findings.append(Finding("CONTRADICTED", label, detail))
            for ref in row.get("evidence", []):
                if not resolves(plant, ref):
                    findings.append(Finding("DANGLING", label,
                                            f"cites {ref!r}, which does not "
                                            f"exist in the plant"))
        if status == "ABSENT" and live:
            authored, scaffolds = [], []
            for q in live:
                qrel = q.relative_to(plant / GRAPH_HOME).as_posix()
                (scaffolds if qrel in templates else authored).append(q.name)
            if authored:
                findings.append(Finding("CONTRADICTED", label,
                                        f"claimed ABSENT but the collection "
                                        f"holds {len(authored)} authored "
                                        f"leaf/leaves ({', '.join(authored[:3])})"))
            elif scaffolds:
                # The seed's own README/index sitting in an honestly-empty
                # collection is not a contradiction — it is a scaffold the
                # steward has not disposed of yet.
                findings.append(Finding("CONTRADICTED", label,
                                        f"claimed ABSENT but still carries the "
                                        f"seed's unfilled scaffold "
                                        f"({', '.join(scaffolds[:3])}) — rename "
                                        f"it with `graft-audit.py <plant> "
                                        f"<seed> --unfilled --rename` so the "
                                        f"router stops reading it as knowledge"))


NODE_REF_RE = re.compile(r"^[a-z][a-z0-9-]*\.[a-z0-9.-]+$")


def read_target(plant, entry):
    """The files one `plant_knowledge:` entry stands for.

    Three forms, one question — "does this hold anything this plant wrote?".
    A collection (`design/`) stands for its leaves; a single row
    (`runbooks/rollback.md`) for that file; a PROJECT node id
    (`expertise.dotnet`) for `nodes/<id>.md`, where the filename equals the id.
    Machinery ids are deliberately not a form: they keep NN-prefixed natural
    names the id does not encode, and a plant expert declares what project
    knowledge it reads, not which seed protocol it obeys."""
    if entry.endswith("/") or entry.endswith(".md"):
        return collection_leaves(plant, entry)[0]
    if NODE_REF_RE.match(entry):
        f = plant / GRAPH_HOME / "nodes" / f"{entry}.md"
        return [f] if f.is_file() else []
    return []


def empty_reads(plant, reads, templates):
    """Which of the things an agent declares it must read hold nothing this
    plant wrote. All-of, never any-of: pooling them let one `best-practices/`
    page written for the implementer mark the ui-ux-designer covered with an
    empty `design/` — the row would pass on exactly the plant it was built to
    catch. Shared by the roster arm and the expert arm, which ask the same
    question of two different row sets."""
    out = []
    for entry in reads:
        live = read_target(plant, entry)
        if not any(is_substantive(
                plant, q.relative_to(plant / GRAPH_HOME).as_posix(),
                templates)[0] for q in live):
            out.append(entry)
    return out


def lint_agents(plant, seed, rec, templates, findings):
    """The question the plant could not previously answer: can each agent on
    the roster read anything project-specific in its own domain? An agent
    declares the collections it needs; a COVERED row must point at real, filled
    leaves inside them."""
    have = {a.get("name"): a for a in rec.get("agents", []) if a.get("name")}
    for name, reads in sorted(required_agents(seed).items()):
        label = f"agent {name}"
        row = have.get(name)
        if row is None:
            findings.append(Finding("MISSING", label,
                                    f"reads {', '.join(reads)} and the record "
                                    f"does not answer whether the plant holds "
                                    f"any of it"))
            continue
        status = check_row_shape(label, row, findings)
        if status != "COVERED":
            continue
        empty = empty_reads(plant, reads, templates)
        if empty:
            findings.append(Finding("CONTRADICTED", label,
                                    f"claimed COVERED but "
                                    f"{', '.join(empty)} "
                                    f"{'holds' if len(empty) == 1 else 'hold'} "
                                    f"no filled leaf — this agent would "
                                    f"work on this project with nothing "
                                    f"project-specific to read there"))
        for ref in row.get("artifacts", []):
            if not resolves(plant, ref):
                findings.append(Finding("DANGLING", label,
                                        f"names {ref!r}, which does not exist"))


def lint_experts(plant, seed, rec, templates, findings):
    """The staffing question from the supply side.

    Growth is supposed to end with experts this project needs and the base
    roster does not carry — the evidence ledger's §9 signal, turned into an
    agent. Through 7.3.x nothing checked that it happened, and worse, nothing
    checked that it took: an expert authored into `docs/graph/agents/` and
    never projected into the harness is on disk and unspawnable, because the
    host reads its roster from the projection directory when a session starts.
    Growth would report a specialist the plant could never call.

    Every expert the plant's graph carries, plus every expert an inventory row
    names, answers here: it is a real node rather than a filled-in template, it
    is marked as the plant's own, it cites what motivated it, it can read
    something in the collections it declares, and it is projected into every
    harness this plant was installed with."""
    have = {e.get("name"): e for e in rec.get("experts", []) if e.get("name")}
    on_disk = plant_experts(plant, seed)
    projections = plant_projections(plant)
    named = {}
    for item in rec.get("inventory", []):
        ex = item.get("expert") or {}
        nm = str(ex.get("name") or "").strip()
        if ex.get("warranted") is True and nm:
            named.setdefault(nm, item.get("name") or item.get("slug") or "an item")
    if on_disk and projections is None:
        findings.append(Finding("STALE", STAMP_REL,
                                "records no `agent_projections`, so nothing "
                                "says where this plant's roster has to be "
                                "spawnable from and every expert would pass "
                                "the registration check by default — re-run "
                                "the installer for each adapter this plant "
                                "uses, then re-audit"))
    for name in sorted(set(on_disk) | set(named)):
        label = f"expert {name}"
        row, info = have.get(name), on_disk.get(name)
        if row is None:
            findings.append(Finding(
                "MISSING", label,
                (f"the plant's graph carries this expert"
                 if info else
                 f"the inventory item {named[name]!r} is staffed with it")
                + " and the record does not answer for it — re-run --plan"))
            continue
        status = check_row_shape(label, row, findings)
        if status is None or status == "UNKNOWN":
            continue
        if info is None:
            findings.append(Finding("UNSTAFFED", label,
                                    f"{named.get(name, 'an item')!r} names this "
                                    f"expert and {GRAPH_HOME}/agents/{name}.md "
                                    f"does not exist — the surface was staffed "
                                    f"on paper only"))
            continue
        if status == "ABSENT":
            findings.append(Finding("CONTRADICTED", label,
                                    f"claimed ABSENT while "
                                    f"{info['path'].relative_to(plant).as_posix()} "
                                    f"exists — an expert on disk is a fact "
                                    f"about this plant, so answer for it"))
            continue
        rel = info["path"].relative_to(plant / GRAPH_HOME).as_posix()
        ok, why = is_substantive(plant, rel, templates)
        if not ok:
            findings.append(Finding("HOLLOW", label,
                                    f"{GRAPH_HOME}/{rel} — {why}"))
        if info["declared_name"] and info["declared_name"] != name:
            findings.append(Finding("HOLLOW", label,
                                    f"its frontmatter name is "
                                    f"{info['declared_name']!r} while the file "
                                    f"is {name}.md — the harness projects and "
                                    f"spawns by filename, so a disagreement "
                                    f"names an agent nobody can call"))
        if info["origin"] != "project":
            findings.append(Finding("HOLLOW", label,
                                    "carries no `origin: project`, so a graft "
                                    "cannot tell this plant's own expert from "
                                    "the seed machinery it replaces"))
        if not info["reads"]:
            findings.append(Finding("HOLLOW", label,
                                    "declares no `plant_knowledge:` — the one "
                                    "agent authored FOR this project's surface "
                                    "would be the only one exempt from the "
                                    "check that asks whether it has anything "
                                    "project-specific to read"))
        else:
            # An entry that stands for nothing at all is a dangling
            # declaration, not an empty collection — the expert names a place
            # that does not exist, and "holds nothing this plant wrote" would
            # send the reader looking for a directory that was never there.
            # This covers a node the graph does not carry AND a mistyped or
            # slash-less collection, which is the same defect wearing a
            # different name.
            resolvable = []
            for entry in info["reads"]:
                if read_target(plant, entry):
                    resolvable.append(entry)
                    continue
                kind = ("node" if NODE_REF_RE.match(entry) and
                        not entry.endswith((".md", "/")) else "collection")
                findings.append(Finding("DANGLING", label,
                                        f"declares it reads {kind} {entry!r}, "
                                        f"which this plant does not carry — a "
                                        f"declaration that stands for nothing "
                                        f"cannot be answered either way"))
            empty = empty_reads(plant, resolvable, templates)
            if empty:
                findings.append(Finding("CONTRADICTED", label,
                                        f"declares it reads "
                                        f"{', '.join(info['reads'])}, and "
                                        f"{', '.join(empty)} "
                                        f"{'holds' if len(empty) == 1 else 'hold'} "
                                        f"nothing this plant wrote"))
        if not row.get("motivated_by"):
            findings.append(Finding("UNJUSTIFIED", label,
                                    "cites nothing that motivated it — an "
                                    "expert is a claim about the source (a "
                                    "dominant domain, a high-risk surface, a "
                                    "recurring task shape), never a preference"))
        for ref in list(row.get("motivated_by") or []) + list(row.get("evidence") or []):
            if not resolves(plant, ref):
                findings.append(Finding("DANGLING", label,
                                        f"cites {ref!r}, which does not exist "
                                        f"in the plant"))
            elif str(ref).replace("\\", "/").startswith(f"{GRAPH_HOME}/agents/"):
                # An expert citing itself, or a sibling expert, is a roster
                # justifying its own existence. The citation has to point at
                # the SOURCE that earned it.
                findings.append(Finding("UNJUSTIFIED", label,
                                        f"cites {ref!r} — an agent file, not "
                                        f"the source that earned this expert; "
                                        f"a roster cannot be its own evidence"))
        for tool, pattern, verbatim in (projections or []):
            projected = pattern.replace("{name}", name)
            proj = plant / projected
            if Path(projected).is_absolute() or ".." in Path(projected).parts:
                continue          # a stamp is plant-written; never follow it out
            if not proj.is_file():
                findings.append(Finding("UNGROWN", label,
                                        f"{projected} — authored into the "
                                        f"graph and never projected, so no "
                                        f"{tool} session can spawn it: the "
                                        f"host reads its roster from there when "
                                        f"a session starts"))
            elif verbatim and proj.read_bytes() != info["path"].read_bytes():
                findings.append(Finding("CONTRADICTED", label,
                                        f"{projected} has drifted from its "
                                        f"home in {GRAPH_HOME}/agents/ — a "
                                        f"projection is a copy, not a second "
                                        f"home; re-project it"))


def lint_inventory(plant, rec, templates, findings):
    """The heart of it: every item the scouts found the project to be made of
    names the artifacts growth owed it, and each one is present or it is not."""
    for item in rec.get("inventory", []):
        name = item.get("name") or item.get("slug") or "<unnamed>"
        kind = item.get("kind", "")
        label = f"{kind or 'item'} {name}"
        if kind not in KIND_PLAN:
            findings.append(Finding("BLANK", label,
                                    (f"kind {kind!r} is not one of "
                                     if kind else
                                     "carries no kind, so nothing decides what "
                                     "it owes the graph or whether it has to "
                                     "answer the staffing question — give it "
                                     "one of ")
                                    + f"{', '.join(sorted(KIND_PLAN))}"))
        sig = item.get("significance")
        if sig and sig not in SIGNIFICANCE:
            findings.append(Finding("BLANK", label,
                                    f"significance {sig!r} is not one of "
                                    f"{', '.join(SIGNIFICANCE)}"))
        if not item.get("evidence"):
            findings.append(Finding("UNJUSTIFIED", label,
                                    "no evidence path — an inventory item is a "
                                    "finding about the source, not a guess"))
        else:
            for ref in item["evidence"]:
                if not resolves(plant, ref):
                    findings.append(Finding("DANGLING", label,
                                            f"evidence {ref!r} does not exist "
                                            f"in the plant"))
        status = (item.get("status") or "").strip().upper()
        if status in ("UNKNOWN", "ABSENT"):
            # An inventory row closes on the same terms as a collection or an
            # agent row: an absence names its reason and where it looked, a
            # blocker is named. Waving one through with a bare `UNKNOWN` was
            # how a design surface or a regulatory exposure could leave the
            # inventory without ever being answered.
            if (check_row_shape(label, item, findings) == "UNKNOWN"
                    and (item.get("blocker") or "").strip()):
                findings.append(Finding("UNKNOWN", label, item["blocker"]))
            continue
        expect = item.get("expect") or []
        # What this item owes, asked of the one function that owns the answer.
        # The orchestrator may extend a plan from evidence, so `expect` is not
        # required to equal this — but an expertise node it does not owe is
        # over-growth, and that judgment belongs here rather than in a second
        # copy of the rule.
        owed = {row["path"] for row in
                planned_artifacts(item, majors_in_play(rec, item.get("slug", "")))[0]}
        if not expect:
            findings.append(Finding("BLANK", label,
                                    "no planned artifacts — every inventory "
                                    "item owes the graph something, or says "
                                    "ABSENT with a reason"))
        for planned in expect:
            rel = planned.get("path", "") if isinstance(planned, dict) else str(planned)
            rel = rel[len(GRAPH_HOME) + 1:] if rel.startswith(GRAPH_HOME + "/") else rel
            if not rel:
                findings.append(Finding("BLANK", label,
                                        "a planned artifact with no path — "
                                        "name the file this item owes the "
                                        "graph, or drop the entry"))
                continue
            if rel.startswith("nodes/expertise.") and rel not in owed:
                # Over-growth is a finding too, and what is owed has one home:
                # this asks `planned_artifacts` rather than re-deriving the
                # incidental rule beside it, so the two cannot disagree.
                findings.append(Finding("BLANK", label,
                                        f"plans {GRAPH_HOME}/{rel}, which this "
                                        f"item does not owe — an expertise node "
                                        f"is for the stack a worker writes "
                                        f"against, not for every name in the "
                                        f"lockfile"))
                continue
            ok, why = is_substantive(plant, rel, templates)
            if not ok:
                verdict = "UNGROWN" if why == "does not exist" else "HOLLOW"
                findings.append(Finding(verdict, label,
                                        f"{GRAPH_HOME}/{rel} — {why}"))
                continue
            if rel.startswith("nodes/expertise.") and kind in PINNED_KINDS:
                # The node owns applicability, never the pin. If it does not
                # route to this item's own library page, the version
                # distinction has nowhere to live and the node is the second
                # home it was designed not to be.
                fm = parse_frontmatter(plant / GRAPH_HOME / rel)
                libs = fm.get("libraries") or []
                if isinstance(libs, str):
                    libs = [libs]
                if item["slug"] not in libs:
                    findings.append(Finding("HOLLOW", label,
                                            f"{GRAPH_HOME}/{rel} names no "
                                            f"`libraries: {item['slug']}` — an "
                                            f"expertise node routes to the pin "
                                            f"home rather than restating it, so "
                                            f"without that edge it routes to "
                                            f"nothing"))
        if needs_staffing(item):
            # The decision ledger §9 was always supposed to force, recorded
            # where it survives the run. A dominant domain or a core part of
            # the stack either earns a project-specific expert or is recorded
            # as not earning one; what it may not do is leave the question
            # unasked, which is indistinguishable from never having read §9.
            ex = item.get("expert")
            if not isinstance(ex, dict) or "warranted" not in ex:
                findings.append(Finding("UNSTAFFED", label,
                                        "records no staffing decision — say "
                                        "whether this surface warrants a "
                                        "project-specific expert, and why"))
            elif not isinstance(ex.get("warranted"), bool):
                # `"no"`, `"false"` and `0` are all truthy-or-falsy by accident.
                # A decision is a boolean; anything else is a note to self.
                findings.append(Finding("UNSTAFFED", label,
                                        f"`warranted` is "
                                        f"{ex.get('warranted')!r}, not true or "
                                        f"false — a staffing decision is a "
                                        f"boolean, not a remark"))
            elif ex["warranted"] is False:
                if not str(ex.get("why") or "").strip():
                    findings.append(Finding("UNSTAFFED", label,
                                            "`warranted: false` with no reason "
                                            "— declining to staff a surface is "
                                            "a decision, and a decision carries "
                                            "its why"))
            else:
                if not str(ex.get("name") or "").strip():
                    findings.append(Finding("UNSTAFFED", label,
                                            "warrants a project-specific expert "
                                            "and names none"))
                if not str(ex.get("why") or "").strip():
                    findings.append(Finding("UNSTAFFED", label,
                                            "warrants a project-specific expert "
                                            "and gives no reason — the why is "
                                            "what the expert's charter is "
                                            "written from"))
                if ex.get("needs") not in SPAWN_TRIGGERS:
                    # Every surface already owes an expertise node, which the
                    # router composes in for free. Spawning on top of that is
                    # warranted only by something a node cannot be — so the
                    # decision names which.
                    findings.append(Finding("UNSTAFFED", label,
                                            f"`needs` is {ex.get('needs')!r} — "
                                            f"name which of "
                                            f"{', '.join(SPAWN_TRIGGERS)} this "
                                            f"agent needs that its expertise "
                                            f"node cannot serve; knowledge "
                                            f"alone composes through the graph "
                                            f"without a spawn"))
        ground = item.get("grounding") or {}
        if ground.get("required"):
            # The citation has to be a real, filled file under sources/ — the
            # place research-scout normalizes what it retrieved. Accepting any
            # path that merely existed let `docs/graph/sources/` itself, or the
            # seed's own untouched sources README, stand in for retrieval, and
            # UNGROUNDED is the only thing between a library page and model
            # memory.
            grounded = False
            for ref in ground.get("sources", []):
                if not resolves(plant, ref):
                    continue
                rel = re.sub(r":\d+(?::\d+)?(-\d+)?$", "",
                             str(ref).split("#", 1)[0]).strip()
                rel = rel[len(GRAPH_HOME) + 1:] if rel.startswith(GRAPH_HOME + "/") else rel
                if rel.startswith("sources/") and is_substantive(plant, rel, templates)[0]:
                    grounded = True
                    break
            if not grounded:
                findings.append(Finding("UNGROUNDED", label,
                                        "requires external grounding and cites "
                                        "no retrieved source that resolves to a "
                                        "filled file under docs/graph/sources/ "
                                        "— dispatch a research-scout for the "
                                        "upstream documentation and normalize "
                                        "it there"))


def rows(rec, key, label):
    """The record's four arrays, validated once so every reader below can
    assume shape. Hand-written JSON gets a null array or a bare string where an
    object belongs; that is a mistake to name, not to crash on."""
    val = rec.get(key) or []
    if not isinstance(val, list):
        die(f"{RECORD_REL}: {key!r} must be a list of {label} rows")
    for i, row in enumerate(val):
        if not isinstance(row, dict):
            die(f"{RECORD_REL}: {key}[{i}] must be an object, not "
                f"{type(row).__name__}")
    return val


def do_lint(plant, seed, opt):
    rec = load_record(plant)
    findings = []
    if rec is None:
        detail = ("this plant carries no coverage record, so nothing about it "
                  "can be said to have been grown. Run --plan, fill the "
                  "inventory from the growth ledgers, then grow.")
        if opt.get("json"):
            print(json.dumps([{"verdict": "MISSING", "row": RECORD_REL,
                               "detail": detail}], indent=2))
        else:
            print(f"  MISSING      {RECORD_REL}")
            print(f"               {detail}")
        return 1
    if rec.get("schema") != SCHEMA:
        die(f"{RECORD_REL} declares schema {rec.get('schema')!r}; "
            f"this tool speaks {SCHEMA!r}")
    want, has = seed_version(seed), rec.get("seed_version")
    stamped = plant_seed_version(plant)
    if want and not has:
        findings.append(Finding("STALE", RECORD_REL,
                                f"names no seed_version, so nothing says which "
                                f"seed's collections and agents these rows "
                                f"answer for — re-run --plan against {want}"))
    elif want and has and has != want:
        findings.append(Finding("STALE", RECORD_REL,
                                f"planned against seed {has}, audited against "
                                f"{want} — re-run --plan so the collections and "
                                f"agents this seed added become rows to answer"))
    elif stamped and has and stamped != has:
        findings.append(Finding("STALE", RECORD_REL,
                                f"the plant is stamped at seed {stamped} but "
                                f"the record was planned against {has}"))

    for key, label in (("collections", "collection"), ("agents", "agent"),
                       ("experts", "expert"), ("inventory", "inventory")):
        rows(rec, key, label)

    templates = template_bytes(seed)
    if opt.get("agents"):
        lint_agents(plant, seed, rec, templates, findings)
        lint_experts(plant, seed, rec, templates, findings)
    else:
        lint_collections(plant, seed, rec, templates, findings)
        lint_agents(plant, seed, rec, templates, findings)
        lint_experts(plant, seed, rec, templates, findings)
        lint_inventory(plant, rec, templates, findings)

    if opt.get("json"):
        print(json.dumps([{"verdict": f.verdict, "row": f.row,
                           "detail": f.detail} for f in findings], indent=2))
    else:
        for f in findings:
            print(f)
        fatal = [f for f in findings if f.fatal()]
        unknown = [f for f in findings if not f.fatal()]
        scope = ("agent and expert coverage" if opt.get("agents")
                 else f"{len(rec.get('collections', []))} collection(s), "
                      f"{len(rec.get('agents', []))} agent(s), "
                      f"{len(rec.get('experts', []))} expert(s), "
                      f"{len(rec.get('inventory', []))} inventory item(s)")
        print(f"  audited {scope}")
        if fatal:
            print(f"  !! {len(fatal)} finding(s) — growth is not complete. "
                  f"Cover each row, or establish its absence with a reason and "
                  f"the paths you searched.")
        else:
            print(f"  coverage complete"
                  + (f" ({len(unknown)} named blocker(s) carried)"
                     if unknown else ""))
    return 1 if any(f.fatal() for f in findings) else 0


def main():
    plant, seed, opt = parse_args()
    if not (plant / GRAPH_HOME).is_dir():
        die(f"{plant} has no {GRAPH_HOME}/ — not a plant root; refusing a "
            f"vacuous audit", 1)
    if not (seed / TEMPLATE_DOCS).is_dir():
        die(f"{seed} has no {TEMPLATE_DOCS}/ — not a seed root", 1)
    return do_plan(plant, seed, opt) if opt.get("plan") else do_lint(plant, seed, opt)


if __name__ == "__main__":
    sys.exit(main())
