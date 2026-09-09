#!/usr/bin/env python3
"""graph-lint.py — enforce the knowledge-graph contract.

The graph under docs/graph/nodes/ is what lets an agent load a few
files instead of the whole codebase. It only works if the invariants
hold, so they are checked mechanically rather than trusted to
discipline.

On install/adoption, copy this file to docs/graph/ (next to index.md
and the nodes/ directory) and set the PROJECT CONFIG block below to the
project's own node kinds and root id.

Usage:
    python3 graph-lint.py                 # lint; exit 1 on error
    python3 graph-lint.py --graph         # print the edges (-> requires, ~> composes)
    python3 graph-lint.py --plan "TASK"   # dry-run the context router:
                                          # what loads, what does not, and why

Contract: docs/graph/_schema.md
No third-party dependencies: it must run on a bare python3.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ----------------------------- PROJECT CONFIG -----------------------------
# The single root node's id (its id == this string; every other node's id
# is prefixed by its kind).
ROOT_ID = "root"
# The node kinds this project uses. An id must be "<kind>.<name>" for its
# declared kind — except the root node, whose id is exactly ROOT_ID.
KINDS = {"root", "subsystem", "stack", "platform", "data", "crosscut", "domain",
         "expertise", "deviation", "protocol", "skill", "agent", "method"}
# Optional: kinds whose node ids carry a shorter, different id-prefix than the
# kind name itself. Maps a kind → the prefix its ids must start with, so a
# verbose kind can live in a terse id namespace (its ids must then be
# "<mapped-prefix>.<name>"). A kind absent from this map keeps the identity
# rule — its ids must start with "<kind>." Defaults to {} so every existing
# project lints exactly as before.
KIND_PREFIX = {}
# Machinery: the seed's method surface lives INSIDE the graph as routable
# nodes — docs/graph/<dir>/*.md with kind <dir_kind>. These are doctrine,
# not project facts, so two project-fact checks (version leakage, the
# ~150-line body ceiling) do not apply to them; everything else — unique
# fact ownership, resolvable acyclic edges, honest est_tokens, routability
# via --plan — binds identically. `origin: seed` marks graft ownership.
MACHINERY_DIRS = {"protocols": "protocol", "skills": "skill",
                  "agents": "agent", "method": "method"}
MACHINERY_KINDS = set(MACHINERY_DIRS.values())
# --------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent          # docs/graph/
NODES_DIR = HERE / "nodes"
LIBS_DIR = HERE / "libraries"                   # docs/graph/libraries/
ARTIFACTS_DIR = HERE                            # all knowledge lives below docs/graph/
INDEX = HERE / "index.md"

REQUIRED_KEYS = {"id", "tier", "kind", "title", "owns", "requires", "load_when", "est_tokens"}
LIST_KEYS = {"owns", "requires", "peers", "composes", "libraries", "artifacts", "load_when"}
# The edges a traversal follows out of a node. `requires` is the eager closure,
# `peers` the boundary a task may cross deliberately, `composes` the lazy menu
# an expertise node offers. Reachability follows all three; the router follows
# `requires` always and `composes` conditionally (see resolve()).
TRAVERSAL_EDGES = ("requires", "peers", "composes")
# An expertise id may carry a major-version suffix ONLY as a child composed by
# the unversioned node (schema rule 19): a plant running two majors at once
# splits applicability, and that is the single place a version enters a slug.
VERSIONED_SLUG_RE = re.compile(r"^(?P<base>expertise\.[a-z0-9-]+?)-(?P<major>\d+)$")

# Lifecycle status (schema §"Lifecycle status"). One base vocabulary for every
# kind; extensions only where the base cannot express a real state. Companion
# keys make a status mean something: `closed` without evidence is a green lie,
# `deferred` without a reopen condition is a quiet abandonment.
STATUS_BASE = {"open", "deferred", "hotfix", "rejected", "superseded", "closed"}
STATUS_EXT = {
    "adr": {"proposed", "accepted"},
    "spec": {"draft", "active", "implemented", "back-written"},
    "deviation": {"standing"},
}
STATUS_COMPANIONS = {
    "open": ("owner",), "hotfix": ("owner",), "deferred": ("owner", "reopen_when"),
    "superseded": ("superseded_by",), "closed": ("status_evidence",),
    "standing": ("ends_when",),
}
DEVIATION_KEYS = {"departs_from", "reason", "scope", "ends_when", "recorded_in"}
PLANT_KEYS = {"environment_class", "commit_attribution", "deliverable_language", "comment_language"}
ENVIRONMENT_CLASSES = {"ephemeral-test", "staging", "real-production", "mixed"}
STATUS_LINE_RE = re.compile(r"^##\s+Status\s*$", re.M)
_ALL_STATUS_WORDS = STATUS_BASE | set().union(*STATUS_EXT.values())

# A version pin: 2.7.2, v2.7.2, ^15.0.0, ~4.8.2, 0.0.13-SNAPSHOT, 8.0.31.
# The lookbehind excludes `§5.4` (a section reference) and any digit/word/
# path character so `docs/v2.1` and `1.2.3` inside a word don't match; the
# optional leading v is part of the match so `v2.7.2` cannot hide behind it.
VERSION_RE = re.compile(r"(?<![\w./§-])[vV]?[\^~]?\d+\.\d+(\.\d+)?(-[A-Za-z0-9]+)?(?![\w.])")
# A project-artifact identifier directly before a version token: the token is a
# revision citation, not a library pin.
ARTIFACT_REVISION_RE = re.compile(r"(?:SPEC|ADR|RFC|PRD|RUNBOOK|ISSUE|PR)[-_ ]?\d+\s*$", re.I)
BODY_TOKENS_PER_WORD = 1.35
STEM = 6  # prefix length for the singular/plural fold (order/orders, node/nodes)

# Filler words that appear in many nodes' searchable text without carrying
# routing signal.
STOPWORDS = frozenset(
    "the and for add new from that this with why how are was not you its "
    "change what where when does did into out about a an of to in on it "
    "over via using use onto off around per which while would could should "
    "want need make made get got run see tell show give take find "
    "there any some someone goes going tells told anyone something "
    "stack whole".split()
)


class LintError(Exception):
    pass


@dataclass
class Node:
    path: Path
    meta: dict
    body: str
    dir_kind: str | None = None   # set for machinery nodes: the kind their dir implies

    @property
    def id(self) -> str:
        return self.meta.get("id", "")

    @property
    def is_machinery(self) -> bool:
        return self.dir_kind is not None

    @property
    def words(self) -> int:
        return len(self.body.split())

    @property
    def measured_tokens(self) -> int:
        return int(self.words * BODY_TOKENS_PER_WORD)

    def get_list(self, key: str) -> list:
        v = self.meta.get(key, [])
        return v if isinstance(v, list) else [v]

    def out_edges(self) -> list:
        """Every id this node points at. One home for "the edges a traversal
        follows": reachability walked `requires + peers` from two hand-written
        lists, so a third edge would have been reachable in one walk and not
        the other."""
        return [t for key in TRAVERSAL_EDGES for t in self.get_list(key)]

    @property
    def triggers(self) -> set:
        """The vocabulary descent matches a task against: the node's own
        `load_when` tokens plus its slug kept WHOLE. The slug is not tokenized
        — `ef-core` split into `ef` and `core` would let a task saying "the
        core module" DESCEND the persistence expertise off a word that names
        nothing about it. (Seeding is a separate question and is unchanged: it
        scores id and title tokens, so such a task may still load the node on
        its own merits, and the absence of a composed-by line is what says
        so.) Title and repo words stay out of this set: they belong to seed
        scoring, and a title like "ef-core — the persistence expertise" would
        put `expertise` in every sibling's vocabulary."""
        # STOPWORDS are not stripped here and need not be: `_terms` drops them
        # from every task, so a filler word sitting in a child's triggers can
        # never be the term that descends it.
        return _tokens(" ".join(self.get_list("load_when"))) | {self.id.split(".", 1)[-1]}


def parse_frontmatter(text: str, path: Path):
    """Parse the small YAML subset the node contract permits."""
    if not text.startswith("---\n"):
        raise LintError(f"{path.name}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise LintError(f"{path.name}: unterminated frontmatter")
    raw, body = text[4:end], text[end + 5 :]

    meta: dict = {}
    current = None
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            item = line.strip()
            if not item.startswith("- "):
                # One nested map is permitted: the router's `plant:` block
                # (schema §"The plant: block"). Its keys are read by
                # check_plant_block by line; here they only must not break.
                if current == "plant" and ":" in item:
                    continue
                raise LintError(f"{path.name}:{lineno}: expected '- item', got {line!r}")
            if current is None:
                raise LintError(f"{path.name}:{lineno}: list item before any key")
            meta.setdefault(current, []).append(_scalar(item[2:]))
            continue
        if ":" not in line:
            raise LintError(f"{path.name}:{lineno}: expected 'key: value', got {line!r}")
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value:
            meta[key] = _scalar(value)
            current = None
        else:
            meta[key] = []
            current = key
    return meta, body


def _scalar(v: str):
    v = v.strip()
    if v and v[0] in "\"'" and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if "  #" in v:
        v = v.split("  #", 1)[0].strip()
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def load_nodes() -> list:
    if not NODES_DIR.is_dir():
        raise LintError(f"missing nodes dir: {NODES_DIR}")
    nodes = []
    scan = [(NODES_DIR, None)] + [
        (HERE / d, k) for d, k in sorted(MACHINERY_DIRS.items()) if (HERE / d).is_dir()
    ]
    for directory, dir_kind in scan:
        for p in sorted(directory.glob("*.md")):
            if p.name.startswith("_") or p.name == "index.md":
                continue
            meta, body = parse_frontmatter(p.read_text(encoding="utf-8"), p)
            nodes.append(Node(p, meta, body, dir_kind))
    if not nodes:
        raise LintError("no nodes found")
    return nodes


# --- checks -----------------------------------------------------------


def kind_prefix(kind) -> str:
    """The id-prefix a kind's nodes must carry: the mapped prefix if the kind
    is listed in KIND_PREFIX, else the kind name itself (identity)."""
    return KIND_PREFIX.get(kind, str(kind))


def check_schema(n: Node, errs: list) -> None:
    missing = REQUIRED_KEYS - n.meta.keys()
    # Agent nodes carry the harness key routing_triggers; it IS their
    # load_when (one home per fact — do not duplicate the list).
    if n.meta.get("kind") == "agent" and "routing_triggers" in n.meta:
        missing -= {"load_when"}
    if missing:
        errs.append(f"{n.path.name}: missing required key(s): {', '.join(sorted(missing))}")
    for k in LIST_KEYS & n.meta.keys():
        if not isinstance(n.meta[k], list):
            errs.append(f"{n.path.name}: '{k}' must be a list")
    if n.meta.get("tier") != 2:
        errs.append(f"{n.path.name}: tier must be 2 (got {n.meta.get('tier')!r})")
    kind = n.meta.get("kind")
    if kind not in KINDS:
        errs.append(f"{n.path.name}: kind {kind!r} not in {sorted(KINDS)}")
    elif n.id and n.id != ROOT_ID:
        prefix = kind_prefix(kind)
        if not n.id.startswith(prefix + "."):
            errs.append(
                f"{n.path.name}: id {n.id!r} does not match kind {kind!r} "
                f"(expected id prefix {prefix + '.'!r})"
            )
    if n.is_machinery:
        if kind != n.dir_kind:
            errs.append(
                f"{n.path.name}: kind {kind!r} does not match its directory "
                f"(docs/graph/ machinery dir implies kind {n.dir_kind!r})"
            )
        # Machinery filenames keep their natural names; the id's <name>
        # part must equal the stem with any NN- ordering prefix stripped.
        expected = n.id.split(".", 1)[1] if "." in n.id else n.id
        if re.sub(r"^\d+-", "", n.path.stem) != expected:
            errs.append(
                f"{n.path.name}: id {n.id!r} does not match filename "
                f"(expected id name part {re.sub(r'^\\d+-', '', n.path.stem)!r})"
            )
    elif n.id and n.path.stem != n.id:
        errs.append(f"{n.path.name}: filename must equal id ({n.id}.md)")
    if not n.get_list("owns"):
        errs.append(f"{n.path.name}: node owns no facts — link farm, delete or merge it")


def status_vocabulary(kind) -> set:
    return STATUS_BASE | STATUS_EXT.get(str(kind), set())


def check_status(n: Node, errs: list) -> None:
    """Rule 12: status is a vocabulary value with its companions, and the body
    never carries a competing value. Optional on most kinds; a deviation must
    carry one (rule 13)."""
    status = n.meta.get("status")
    kind = n.meta.get("kind")
    if status is None:
        if kind == "deviation":
            errs.append(f"{n.id}: deviation node must carry status: standing")
        return
    vocab = status_vocabulary(kind)
    if status not in vocab:
        errs.append(f"{n.id}: status {status!r} not in {sorted(vocab)} for kind {kind!r}")
    for key in STATUS_COMPANIONS.get(str(status), ()):
        if not n.meta.get(key):
            errs.append(f"{n.id}: status {status!r} requires {key!r}")
    sd = str(n.meta.get("status_date", ""))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", sd):
        errs.append(f"{n.id}: status_date must be YYYY-MM-DD (got {sd!r})")
    m = STATUS_LINE_RE.search(n.body)
    if m:
        after = n.body[m.end():].strip().split("\n", 1)[0].strip().strip("`").lower()
        first = after.split()[0].strip("`*:") if after else ""
        if first in _ALL_STATUS_WORDS and first != str(status):
            errs.append(f"{n.id}: body '## Status' says {first!r} but frontmatter says {status!r} — one home")


def check_deviation(n: Node, errs: list) -> None:
    """Rule 13: a deviation is a standing departure with reason, scope, end."""
    if n.meta.get("kind") != "deviation":
        return
    if n.meta.get("status") != "standing":
        errs.append(f"{n.id}: deviation status must be 'standing' (got {n.meta.get('status')!r})")
    missing = DEVIATION_KEYS - {k for k, v in n.meta.items() if v not in (None, "", [])}
    if missing:
        errs.append(f"{n.id}: deviation missing {', '.join(sorted(missing))}")


def check_plant_block(errs: list, warns: list) -> None:
    """Rule 14: index.md carries the owner-declared plant facts. A grown plant
    (coverage record present, or `grown: true` in index.md) FAILS without
    them; an adopted plant only warns, so adoption is never blocked on day one."""
    if not INDEX.exists():
        return
    text = INDEX.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        meta = {}
    else:
        try:
            meta, _ = parse_frontmatter(text, INDEX)
        except LintError as e:
            errs.append(str(e))
            return
    # A plant is "grown" when index.md says so, or when the coverage record
    # exists — the latter only trusted when this graph really sits at
    # <plant>/docs/graph, so a graph parked elsewhere (tests, scratch) never
    # inherits a neighbour's record. Through 7.2.1 this looked for the growth
    # completeness ledger under .cypress/growth/, which was gitignored scratch
    # the run discarded: a plant that HAD been grown stopped looking grown the
    # moment that scratch was cleaned, and silently dropped back to warnings.
    at_docs_graph = HERE.name == "graph" and HERE.parent.name == "docs"
    record = HERE.parent.parent / ".cypress" / "coverage.json"
    flag = str(meta.get("grown", "")).strip().lower()
    grown = flag in ("true", "yes", "1") or (at_docs_graph and record.exists())
    sink = errs if grown else warns
    # `plant:` is a nested map; the frontmatter subset stores it as an empty
    # list marker and the indented `key: value` lines are not list items, so
    # read the block by line rather than through parse_frontmatter.
    block = {}
    in_block = False
    for line in text[4:text.find("\n---\n")].split("\n"):
        if re.match(r"^plant:\s*$", line):
            in_block = True
            continue
        if in_block:
            if not line.startswith(" "):
                break
            k, _, v = line.strip().partition(":")
            if k:
                block[k.strip()] = v.strip()
    if not block:
        sink.append("index.md: missing `plant:` block (environment_class, commit_attribution, "
                    "deliverable_language, comment_language) — the owner-declared facts")
        return
    unfilled = {k for k, v in block.items() if v.startswith("<") and v.endswith(">")}
    missing = (PLANT_KEYS - {k for k, v in block.items() if v}) | unfilled
    if missing:
        sink.append(f"index.md: plant block not yet declared for {', '.join(sorted(missing))} "
                    f"— the owner answers these once (grow Phase 1 / adopt-existing)")
    ec = block.get("environment_class", "")
    if ec and "environment_class" not in unfilled and ec not in ENVIRONMENT_CLASSES:
        sink.append(f"index.md: plant.environment_class {ec!r} not in {sorted(ENVIRONMENT_CLASSES)}")


def check_unique_ownership(nodes: list, errs: list) -> None:
    """The dedup invariant. A fact has exactly one home."""
    home = {}
    for n in nodes:
        for fact in n.get_list("owns"):
            if fact in home:
                errs.append(
                    f"duplicate fact-key {fact!r} owned by both {home[fact]} and {n.id} — extract to a shared node"
                )
            else:
                home[fact] = n.id


def check_unique_ids(nodes: list, errs: list) -> None:
    """_schema.md rule 2 promises id uniqueness; a set silently erased
    collisions and resolve() let the later file win — a duplicate id
    split the routing authority invisibly."""
    byid = {}
    for n in nodes:
        byid.setdefault(n.id, []).append(n)
    for nid, ns in byid.items():
        if len(ns) > 1:
            files = ", ".join(str(x.path.relative_to(HERE)) for x in ns)
            errs.append(f"{nid}: declared by {len(ns)} files ({files}) — "
                        f"ids are unique project-wide (_schema.md rule 2)")


def check_edges(nodes: list, errs: list) -> None:
    by_id = {n.id: n for n in nodes}
    for n in nodes:
        for key in TRAVERSAL_EDGES:
            for target in n.get_list(key):
                if target not in by_id:
                    errs.append(f"{n.id}: {key} → unknown node {target!r}")
                    continue
                if target == n.id:
                    errs.append(f"{n.id}: {key} → itself")
                # `composes` is expertise-to-expertise only (rule 15). A
                # subsystem that needs a stack's depth `requires` its
                # expertise node and lets descent do the rest; letting any
                # kind compose would make "what will --plan load" unanswerable
                # without reading the whole graph.
                if key == "composes":
                    for side, node in (("composes from", n), ("composes to", by_id[target])):
                        if node.meta.get("kind") != "expertise":
                            errs.append(
                                f"{n.id}: {side} {node.id} of kind "
                                f"{node.meta.get('kind')!r} — composes joins "
                                f"expertise nodes only")


def check_acyclic(nodes: list, errs: list, key: str = "requires",
                  arrow: str = " → ") -> None:
    """`requires` and `composes` are each acyclic on their own.

    Their UNION is deliberately not checked: `parent composes child` together
    with `child requires parent` is the intended shape — the eager edge points
    up to what you cannot be correct without, the lazy one points down to what
    the task may not need — and the router's loaded-set makes termination
    trivial either way.
    """
    graph = {n.id: list(n.get_list(key)) for n in nodes}
    WHITE, GREY, BLACK = 0, 1, 2
    colour = dict.fromkeys(graph, WHITE)

    def visit(u: str, stack: list) -> None:
        colour[u] = GREY
        for v in graph.get(u, []):
            if v not in colour:
                continue
            if colour[v] == GREY:
                cyc = arrow.join(stack[stack.index(v):] + [v])
                errs.append(f"{key} cycle: {cyc}")
            elif colour[v] == WHITE:
                visit(v, stack + [v])
        colour[u] = BLACK

    for nid in graph:
        if colour[nid] == WHITE:
            visit(nid, [nid])


def check_expertise(n: Node, errs: list, by_id: dict) -> None:
    """Rules 17–19: an expertise node routes somewhere, its children's upward
    `requires` is mirrored by its own `composes`, and a version suffix exists
    only under the unversioned node that composes it."""
    if n.meta.get("kind") != "expertise":
        return
    if not (n.get_list("libraries") or n.get_list("artifacts")):
        errs.append(f"{n.id}: expertise node with no libraries/artifacts edge — "
                    f"it owns applicability and composition, so with no depth "
                    f"to route to it routes to nothing")
    for target in n.get_list("requires"):
        parent = by_id.get(target)
        if (parent is not None and parent.meta.get("kind") == "expertise"
                and n.id not in parent.get_list("composes")):
            errs.append(f"{n.id}: requires {target} but {target} does not "
                        f"compose it — add '  - {n.id}' under composes: in "
                        f"{parent.path.name}")
    m = VERSIONED_SLUG_RE.match(n.id)
    if m:
        base = by_id.get(m.group("base"))
        if base is None or n.id not in base.get_list("composes"):
            errs.append(f"{n.id}: a version-qualified expertise slug is legal "
                        f"only as a child composed by {m.group('base')!r} — "
                        f"the pin's home is docs/graph/libraries/, not an id")


def check_composition_triggers(nodes: list, warns: list) -> None:
    """The `load_when` analogue of agent-lint's routing-trigger warning, for
    composed children. Descent matches a task term against what a child knows
    and its parent does not, so a term the siblings share is family vocabulary
    that belongs one level up, and a term half the graph carries descends on
    tasks that are not about this child at all. Tokens under three characters
    are ignored: `_terms` drops them from every task, so `0` out of `net8.0`
    can never match and must never be reported."""
    by_id = {n.id: n for n in nodes}
    seen = {}
    for n in nodes:
        for t in n.triggers:
            if len(t) >= 3:
                seen[t] = seen.get(t, 0) + 1
    for n in nodes:
        kids = [by_id[c] for c in n.get_list("composes") if c in by_id]
        if not kids:
            continue
        own = {c.id: {t for t in c.triggers - n.triggers if len(t) >= 3} for c in kids}
        for c in kids:
            for t in sorted(own[c.id]):
                shared = [o.id for o in kids if o.id != c.id and t in own[o.id]]
                if shared:
                    warns.append(f"{c.id}: trigger {t!r} is shared with "
                                 f"{', '.join(sorted(shared))} — family "
                                 f"vocabulary belongs on {n.id}, where it "
                                 f"cannot descend a child")
                elif seen.get(t, 0) > 3:
                    warns.append(f"{c.id}: trigger {t!r} appears in "
                                 f"{seen[t]} nodes — too generic to say this "
                                 f"child is what the task is about; sharpen it")


def check_reachability(nodes: list, errs: list) -> None:
    by_id = {n.id: n for n in nodes}
    if ROOT_ID not in by_id:
        # Pre-growth grace: a fresh install carries only machinery nodes.
        # The root becomes mandatory the moment the first project node lands.
        if any(not n.is_machinery for n in nodes):
            errs.append(f"missing root node {ROOT_ID!r}")
        else:
            index_text = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
            # same boundary rule as the root branch below, then a REAL
            # traversal seeded by the index-listed nodes: the old version
            # unioned EVERY node's outgoing edges into `seen`, so two
            # mutually-peering ghost nodes marked each other reachable
            # (an orphan island always passed)
            listed = {n.id for n in nodes if re.search(
                rf"(?<![\w.-]){re.escape(n.id)}(?![\w-])(?!\.[\w-])", index_text)}
            by = {n.id: n for n in nodes}
            seen, stack2 = set(), list(listed)
            while stack2:
                cur = stack2.pop()
                if cur in seen or cur not in by:
                    continue
                seen.add(cur)
                stack2.extend(by[cur].out_edges())
            for n in nodes:
                if n.id not in seen:
                    errs.append(f"{n.id}: unreachable — no root yet, not listed in index.md, and no listed node reaches it")
        return
    seen = set()
    stack = [ROOT_ID]
    while stack:
        cur = stack.pop()
        if cur in seen or cur not in by_id:
            continue
        seen.add(cur)
        stack.extend(by_id[cur].out_edges())
    if INDEX.exists():
        index_text = INDEX.read_text(encoding="utf-8")
        for n in nodes:
            # boundary match: a plain substring test lets an orphan pass
            # whenever its id merely prefixes an unrelated longer id —
            # including a dotted child (`x.orphan` vs `x.orphan.child`);
            # a trailing sentence period (`x.orphan.`) still counts
            if re.search(rf"(?<![\w.-]){re.escape(n.id)}(?![\w-])(?!\.[\w-])",
                         index_text):
                seen.add(n.id)
    for n in nodes:
        if n.id not in seen:
            errs.append(f"{n.id}: unreachable from {ROOT_ID!r} and unlisted in index.md")


LIB_PIN_ROW_RE = re.compile(r"^\|\s*[^|]*\|\s*([^|]*)\|", re.M)
LIB_REVIEWED_RE = re.compile(r"\*\*Last reviewed:\*\*\s*(\S+)")
LIB_PLACEHOLDER_RE = re.compile(r"^\s*(<[^>]*>|YYYY-MM-DD|latest|)\s*$", re.I)


def check_libraries(nodes: list, errs: list) -> None:
    """Every `libraries:` edge resolves to a page, and every page that follows
    the template's form owes the ingest pass its exit: a filled §0 pin (an
    exact version, never a placeholder or "latest"), a dated `Last reviewed`,
    and a row in libraries/index.md when the index exists. A page with no
    `## 0. Pin` heading is not template-shaped and owes nothing here —
    the growth audit judges a bare page, this check judges an ingested one."""
    for n in nodes:
        for lib in n.get_list("libraries"):
            if not (LIBS_DIR / f"{lib}.md").exists():
                errs.append(f"{n.id}: libraries → missing page docs/graph/libraries/{lib}.md")
    if not LIBS_DIR.is_dir():
        return
    index_path = LIBS_DIR / "index.md"
    index = index_path.read_text(encoding="utf-8", errors="replace") if index_path.exists() else None
    for page in sorted(LIBS_DIR.glob("*.md")):
        if page.name == "index.md":
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^## 0\. Pin\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
        if not m:
            continue
        pin = m.group(1)
        rows = [r for r in LIB_PIN_ROW_RE.findall(pin)
                if not set(r.strip()) <= set("-: ") and r.strip().lower() != "exact version"]
        if not rows or all(LIB_PLACEHOLDER_RE.match(r) for r in rows):
            errs.append(f"libraries/{page.name}: §0 pin table has no exact version — "
                        f"the ingest pass exits on a pinned page, never a placeholder")
        rv = LIB_REVIEWED_RE.search(pin)
        if not rv or not re.match(r"\d{4}-\d{2}-\d{2}$", rv.group(1)):
            errs.append(f"libraries/{page.name}: §0 `Last reviewed` is not a date")
        if index is not None and page.name not in index and page.stem not in index:
            errs.append(f"libraries/{page.name}: no row in libraries/index.md — "
                        f"the close-out librarian registers every drafted page")


def check_artifacts(nodes: list, errs: list) -> None:
    """Artifact edges resolve inside the unified graph and cannot escape it."""
    root = ARTIFACTS_DIR.resolve()
    for n in nodes:
        for artifact in n.get_list("artifacts"):
            if not isinstance(artifact, str) or not artifact.strip():
                errs.append(f"{n.id}: artifacts entries must be non-empty paths")
                continue
            target = (ARTIFACTS_DIR / artifact).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                errs.append(f"{n.id}: artifacts → path escapes docs/graph/: {artifact!r}")
                continue
            if not target.exists():
                errs.append(f"{n.id}: artifacts → missing docs/graph/{artifact}")


def check_version_leakage(nodes: list, errs: list) -> None:
    """Version pins live in docs/graph/libraries/ unless the node owns *.versions.

    Fenced code and inline code are exempt: quoting a real config line is
    not restating a fact.
    """
    for n in nodes:
        if n.is_machinery:
            continue
        if any(f.endswith(".version") or f.endswith(".versions") for f in n.get_list("owns")):
            continue
        body = re.sub(r"```.*?```", "", n.body, flags=re.S)
        body = re.sub(r"`[^`\n]*`", "", body)
        body = re.sub(r"^\s*[-*]?\s*\[[^\]]+\]\([^)]*\)", "", body, flags=re.M)
        for m in VERSION_RE.finditer(body):
            # A revision of a project artifact (SPEC-0002 v0.2.0, ADR-0007 v1.1)
            # is a citation, not a dependency pin.
            if ARTIFACT_REVISION_RE.search(body[max(0, m.start() - 24): m.start()]):
                continue
            line = body[: m.start()].count("\n") + 1
            errs.append(
                f"{n.id}: version pin {m.group(0)!r} (body line ~{line}) — versions belong in docs/graph/libraries/; link instead"
            )


def check_budget(nodes: list, errs: list) -> None:
    for n in nodes:
        est = n.meta.get("est_tokens")
        if not isinstance(est, int):
            errs.append(f"{n.id}: est_tokens must be an integer")
            continue
        measured = n.measured_tokens
        if measured > 2 * est or est > 2 * max(measured, 1):
            errs.append(f"{n.id}: est_tokens={est} but body measures ~{measured} (must be within 2x)")
        if not n.is_machinery and len(n.body.strip("\n").splitlines()) > 170:
            errs.append(f"{n.id}: body is {n.body.count(chr(10))} lines — over the 170-line ceiling (aim ~150); split it")


# --- router dry-run ---------------------------------------------------


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def _match(term: str, toks: set) -> int:
    """Token-match strength: 2 exact, 1 prefix-fold, 0 none. Never substring.

    Whole-token matching only (so `field` does not match "greenfield"). An
    exact hit outranks a morphological near-match, so a fuzzy name-fold
    can't outrank an exact trigger.
    """
    if term in toks:
        return 2
    if len(term) >= STEM and any(k.startswith(term[:STEM]) for k in toks):
        return 1
    return 0


def _terms(task: str) -> set:
    """Extract match terms, keeping paths whole and split (`/api/x` → `x`)."""
    out = set()
    for w in re.findall(r"[a-z0-9_/*.-]+", task.lower()):
        for part in [w, *re.split(r"[/*.-]+", w)]:
            part = part.strip("_")
            if len(part) >= 3 and part not in STOPWORDS:
                out.add(part)
    return out


def resolve(nodes: list, task: str):
    """Mirror the traversal in skills/context-router/SKILL.md.

    Seeds are scored IDF-weighted: a term in many nodes (generic) is worth
    little; a term in one or two (distinctive) dominates. The closure then
    follows `requires` eagerly — you cannot be correct without it — and
    `composes` lazily: a composed child loads only when the task names,
    exactly, a term the child knows and its parent does not. Loud family
    vocabulary therefore cannot drag a library page into every task about
    the stack, which is the whole reason the lazy edge exists.

    Returns (loaded, not_loaded, notices): `loaded` pairs each node with how
    it got there, `not_loaded` pairs each node with why it stayed out, and
    `notices` carries the wide-descent warnings.
    """
    by_id = {n.id: n for n in nodes}
    terms = _terms(task)

    buckets = {}
    for n in nodes:
        name_toks = _tokens(" ".join([n.id, n.meta.get("title", ""), str(n.meta.get("repo", ""))]))
        lw_toks = _tokens(" ".join(n.get_list("load_when") + n.get_list("routing_triggers")))
        buckets[n.id] = (name_toks, lw_toks)

    df = {t: 0 for t in terms}
    for name_toks, lw_toks in buckets.values():
        allt = name_toks | lw_toks
        for t in terms:
            if _match(t, allt):
                df[t] += 1

    def weight(t: str) -> int:
        d = df.get(t, 0)
        return 3 if d <= 1 else 2 if d <= 3 else 1

    entries = []
    for n in nodes:
        name_toks, lw_toks = buckets[n.id]
        score = 0
        for t in terms:
            w = weight(t)
            score += w * max(2 * _match(t, name_toks), _match(t, lw_toks))
        if score:
            entries.append((score, n))
    entries.sort(key=lambda x: (-x[0], x[1].id))

    best = entries[0][0] if entries else 0
    floor = max(3, (best + 1) // 2) if best >= 3 else best
    # pre-growth graphs have no root yet: fall back to nothing rather than crash
    seeds = [n for s, n in entries[:3] if s >= floor] or ([by_id[ROOT_ID]] if ROOT_ID in by_id else [])

    loaded: list = []          # [(Node, how)] — how: entry / requires / composed
    seen: set = set()
    reasons: dict = {}         # id -> why it is NOT loaded
    notices: list = []
    # A seed is a seed however it is reached. The stack is LIFO over seeds
    # sorted best-first, so a child that outscores its own subsystem is popped
    # through the parent chain and would otherwise be reported as composed —
    # a true load set with a false account of why.
    entry_ids = {n.id for n in seeds}
    stack = [(n, "entry") for n in seeds]
    while stack:
        n, how = stack.pop()
        if n.id in seen:
            continue
        seen.add(n.id)
        loaded.append((n, "entry" if n.id in entry_ids else how))
        for r in n.get_list("requires"):
            if r in by_id:
                stack.append((by_id[r], f"requires of {n.id}"))
        if n.meta.get("kind") != "expertise":
            continue
        kids = [by_id[c] for c in n.get_list("composes") if c in by_id]
        hits = 0
        for c in kids:
            # The child's OWN vocabulary: what it knows that its parent does
            # not. An exact hit only — a prefix fold would let "migrating the
            # CI runner" pull in the schema-migration expertise.
            own = c.triggers - n.triggers
            term = next((t for t in sorted(terms) if _match(t, own) == 2), None)
            if term:
                hits += 1
                stack.append((c, f'composed by {n.id} on "{term}"'))
            else:
                reasons.setdefault(
                    c.id, f"composed by {n.id}; no task term specific to it")
        # A single child that matches is an ordinary descent, not a symptom;
        # only a parent handing over most of a real menu says the task or the
        # triggers are too generic.
        if len(kids) > 1 and hits * 2 > len(kids):
            notices.append(f"wide descent from {n.id}: {hits} of {len(kids)} "
                           f"children — the task or the triggers are too generic")
    for n, _ in loaded:
        for p in n.get_list("peers"):
            if p in by_id:
                reasons.setdefault(
                    p, f"peer of {n.id} — cross only if the task requires it")
    not_loaded = [(by_id[i], r) for i, r in reasons.items() if i not in seen]
    return loaded, not_loaded, notices


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--graph", action="store_true", help="print the requires-DAG")
    ap.add_argument("--plan", metavar="TASK", help="dry-run the context router for TASK")
    args = ap.parse_args()

    try:
        nodes = load_nodes()
    except LintError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    if args.plan:
        loaded, not_loaded, notices = resolve(nodes, args.plan)
        total = sum(n.meta.get("est_tokens", 0) for n, _ in loaded)
        print(f"task: {args.plan}\n")
        for note in notices:
            print(f"  ! {note}")
        if notices:
            print()
        print(f"LOAD ({len(loaded)} nodes, ~{total} tokens):")
        for n, how in sorted(loaded, key=lambda x: x[0].id):
            line = f"  {n.id:<28} {n.meta.get('title','')}"
            if how.startswith("composed by"):
                line += f"   <- {how}"
            print(line)
        if not_loaded:
            print("\nNOT LOADED (with the reason; cross only if the task requires it):")
            for n, reason in sorted(not_loaded, key=lambda x: x[0].id):
                print(f"  {n.id:<28} {reason}")
        return 0

    if args.graph:
        for n in sorted(nodes, key=lambda x: x.id):
            for r in n.get_list("requires"):
                print(f"{n.id} -> {r}")
            for c in n.get_list("composes"):
                print(f"{n.id} ~> {c}")
        return 0

    errs: list = []
    warns: list = []
    by_id = {n.id: n for n in nodes}
    for n in nodes:
        check_schema(n, errs)
        check_status(n, errs)
        check_deviation(n, errs)
        check_expertise(n, errs, by_id)
    check_plant_block(errs, warns)
    check_unique_ids(nodes, errs)
    check_unique_ownership(nodes, errs)
    check_edges(nodes, errs)
    check_acyclic(nodes, errs)
    check_acyclic(nodes, errs, "composes", " ~> ")
    check_composition_triggers(nodes, warns)
    check_reachability(nodes, errs)
    check_libraries(nodes, errs)
    check_artifacts(nodes, errs)
    check_version_leakage(nodes, errs)
    check_budget(nodes, errs)

    for w in warns:
        print(f"  ! warning: {w}", file=sys.stderr)
    if errs:
        print(f"graph-lint: {len(errs)} error(s) in {len(nodes)} node(s)\n", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    total = sum(n.meta.get("est_tokens", 0) for n in nodes)
    print(f"graph-lint: OK — {len(nodes)} nodes, ~{total} tokens if fully loaded")
    print("(no task should ever load them all; see docs/graph/index.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
