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

Three sets of required rows are derived from the SEED, never from the record
itself, so a row cannot go missing by being left out:

  * one COLLECTION row per knowledge collection the installer creates
    (every top-level directory and leaf of the seed's templates/docs/**),
  * one AGENT row per roster agent that declares `plant_knowledge:` — the
    collections that agent must be able to read to do its job at all,
  * one INVENTORY row per item the scouts found, each carrying its own
    planned artifacts.

A graft to a newer seed that adds a collection or an agent therefore adds
required rows the plant does not yet answer, and they surface as MISSING until
the graft grows them. That is the "grafted is not grown" gap, made mechanical.

VERDICTS (a row fails the gate unless noted)

  MISSING      a required row is absent from the record entirely
  BLANK        the row exists with no status — growth never reached it
  UNGROWN      a planned artifact does not exist in the plant
  HOLLOW       a planned artifact exists but is a scaffold: byte-identical to
               its seed template, still carrying {{placeholders}}, or too
               small to carry a fact
  UNGROUNDED   an item requiring external grounding cites no retrieved source
               that resolves under docs/graph/sources/
  DANGLING     a COVERED row cites evidence paths that do not exist
  UNJUSTIFIED  an ABSENT row gives no reason, or no paths it searched
  CONTRADICTED a collection is claimed COVERED but holds only scaffolds or
               `.unfilled.md` markers — the plant's own files disagree
  STALE        the record was written against an older seed than the plant now
               carries; re-plan before trusting it
  UNKNOWN      an honest blocker, named. Reported always, never a failure —
               the one legitimate way a row stays uncovered.

Usage:
  growth-audit.py <plant-root> <seed-root>            lint (the gate)
  growth-audit.py <plant-root> <seed-root> --plan     create/refresh the plan
  growth-audit.py <plant-root> <seed-root> --agents   agent coverage only
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
            "UNJUSTIFIED", "CONTRADICTED", "STALE", "UNKNOWN")

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
KIND_PLAN = {
    "language":            (["libraries/{slug}.md", "best-practices/{slug}.md"], True),
    "runtime":             (["libraries/{slug}.md", "best-practices/{slug}.md"], True),
    "framework":           (["libraries/{slug}.md", "best-practices/{slug}.md"], True),
    "dependency":          (["libraries/{slug}.md"], True),
    "infrastructure":      (["architecture/{slug}.md", "best-practices/{slug}.md"], True),
    "datastore":           (["data/{slug}.md", "best-practices/{slug}.md"], True),
    "external-service":    (["architecture/{slug}.md"], True),
    "ai-provider":         (["prompts/{slug}.md", "evaluations/{slug}.md"], True),
    "design-surface":      (["design/{slug}.md"], True),
    "regulatory-exposure": (["legal/{slug}.md"], True),
    "domain":              ([], False),
}
# An incidental dependency earns an index line, not a page of its own, and
# nothing is retrieved for it. Significance is the scout's call, recorded.
SIGNIFICANCE = ("core", "significant", "incidental")


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


def template_bytes(seed):
    troot = seed / TEMPLATE_DOCS
    return {rel: p.read_bytes()
            for p in troot.rglob("*") if p.is_file()
            for rel in [p.relative_to(troot).as_posix()]}


# ------------------------------------------------------------ plant material

def _body(text):
    return text.split("\n---\n", 1)[-1] if text.startswith("---\n") else text


def authored_bytes(text, template_text):
    """Bytes of non-blank lines the leaf holds that its seed template does not.
    A leaf at a path the seed ships a template for (a collection README, an
    index, a runbook) is only as grown as the lines the plant added; a leaf the
    seed has no template for is authored in full."""
    inherited = {ln.strip() for ln in _body(template_text).splitlines() if ln.strip()}
    return sum(len(ln.strip()) for ln in _body(text).splitlines()
               if ln.strip() and ln.strip() not in inherited)


def is_substantive(plant, rel, templates):
    """A file states a fact when it exists, keeps no unfilled {{placeholder}},
    and carries enough of its OWN content — measured against the seed template
    at the same path — to hold one. Deliberately mechanical: this asks whether
    growth reached the file, not whether what it wrote is good."""
    f = plant / GRAPH_HOME / rel
    if not f.is_file():
        return False, "does not exist"
    raw = f.read_bytes()
    template = templates.get(rel)
    if template == raw:
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


def plant_seed_version(plant):
    f = plant / STAMP_REL
    if f.is_file():
        try:
            return json.loads(f.read_text(encoding="utf-8")).get("version")
        except json.JSONDecodeError:
            return None
    return None


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

    for item in rec["inventory"]:
        kind = item.get("kind", "")
        slug = item.get("slug") or slugify(item.get("name", ""))
        item["slug"] = slug
        paths, ground = KIND_PLAN.get(kind, ([], False))
        if kind == "dependency" and item.get("significance") == "incidental":
            paths, ground = ["libraries/index.md"], False
        if not item.get("expect"):
            item["expect"] = [{"path": p.format(slug=slug), "why": f"{kind} {slug}"}
                              for p in paths]
        item.setdefault("grounding", {})
        item["grounding"].setdefault("required", ground)
        item["grounding"].setdefault("sources", [])

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
          f"agents: {len(rec['agents'])}   inventory items: {len(rec['inventory'])}")
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
        # Every declared collection, not any of them. Pooling them let one
        # `best-practices/` page written for the implementer mark the
        # ui-ux-designer covered with an empty `design/` — the row would pass
        # on exactly the plant it was built to catch.
        empty = []
        for coll in reads:
            live, _ = collection_leaves(plant, coll)
            if not any(is_substantive(
                    plant, q.relative_to(plant / GRAPH_HOME).as_posix(),
                    templates)[0] for q in live):
                empty.append(coll)
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


def lint_inventory(plant, rec, templates, findings):
    """The heart of it: every item the scouts found the project to be made of
    names the artifacts growth owed it, and each one is present or it is not."""
    for item in rec.get("inventory", []):
        name = item.get("name") or item.get("slug") or "<unnamed>"
        kind = item.get("kind", "")
        label = f"{kind or 'item'} {name}"
        if kind and kind not in KIND_PLAN:
            findings.append(Finding("BLANK", label,
                                    f"kind {kind!r} is not one of "
                                    f"{', '.join(sorted(KIND_PLAN))}"))
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
            ok, why = is_substantive(plant, rel, templates)
            if ok:
                continue
            verdict = "UNGROWN" if why == "does not exist" else "HOLLOW"
            findings.append(Finding(verdict, label,
                                    f"{GRAPH_HOME}/{rel} — {why}"))
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
    """The record's three arrays, validated once so every reader below can
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
                       ("inventory", "inventory")):
        rows(rec, key, label)

    templates = template_bytes(seed)
    if opt.get("agents"):
        lint_agents(plant, seed, rec, templates, findings)
    else:
        lint_collections(plant, seed, rec, templates, findings)
        lint_agents(plant, seed, rec, templates, findings)
        lint_inventory(plant, rec, templates, findings)

    if opt.get("json"):
        print(json.dumps([{"verdict": f.verdict, "row": f.row,
                           "detail": f.detail} for f in findings], indent=2))
    else:
        for f in findings:
            print(f)
        fatal = [f for f in findings if f.fatal()]
        unknown = [f for f in findings if not f.fatal()]
        scope = ("agent coverage" if opt.get("agents")
                 else f"{len(rec.get('collections', []))} collection(s), "
                      f"{len(rec.get('agents', []))} agent(s), "
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
