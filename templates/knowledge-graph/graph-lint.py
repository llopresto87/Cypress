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
    python3 graph-lint.py --warn          # report every error, always exit 0
    python3 graph-lint.py --graph         # print the edges (-> requires, ~> composes)
    python3 graph-lint.py --plan "TASK"   # dry-run the context router:
                                          # what loads, what does not, and why
    python3 graph-lint.py --plan-json=TASK  # the same route as one
                                          # `cypress.plan/1` JSON document, for
                                          # programs (the route hooks)
    python3 graph-lint.py --show ID...    # read routed nodes: each pointer
                                          # resolved in a header, then the body
    python3 graph-lint.py --eval TSV      # route a node-route corpus; per class,
                                          # gated on the GRAPH_* ratchets

Contract: docs/graph/_schema.md
No third-party dependencies: it must run on a bare python3.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import NamedTuple
import importlib.util as _ilu
from pathlib import Path
from pathlib import Path as _Path

# The one frontmatter reader, loaded from beside this file. A COPY sits next to
# every consumer because the linters that ship into plants are standalone files
# with no package to import from; seed-lint enforces byte-identity across them.
# Neither this load nor tier 2's helper load writes a __pycache__ into docs/graph/.
sys.dont_write_bytecode = True
_fm_spec = _ilu.spec_from_file_location(
    "cypress_frontmatter", _Path(__file__).resolve().parent / "frontmatter.py")
_frontmatter = _ilu.module_from_spec(_fm_spec)
_fm_spec.loader.exec_module(_frontmatter)


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
# The owner-declared plant facts in index.md's `plant:` block, in the order the
# full `--plan` prints them (SPEC-0003 PLAN_PRINTS_PLANT_BLOCK).
PLANT_KEYS = ("environment_class", "commit_attribution", "deliverable_language", "comment_language")
ENVIRONMENT_CLASSES = {"ephemeral-test", "staging", "real-production", "mixed"}
STATUS_LINE_RE = re.compile(r"^##\s+Status\s*$", re.M)
_ALL_STATUS_WORDS = STATUS_BASE | set().union(*STATUS_EXT.values())

# A release identifier: 2.7.2, v2.7.2, ^15.0.0, ~4.8.2, 0.0.13-SNAPSHOT, 8.0.31
# — and the undotted forms a standard is named by, draft-07, RFC 8259, STD 90.
# A version with no dotted-numeric core is still a version: `the wire format is
# RFC 8259` is the same assertion as `json 2.7.2`, made in the vocabulary the
# standards bodies use, and it went unseen for as long as the core was required.
# The lookbehind excludes `§5.4` (a section reference) and any digit/word/
# path character so `docs/v2.1` and `1.2.3` inside a word don't match; the
# optional leading v is part of the match so `v2.7.2` cannot hide behind it.
VERSION_RE = re.compile(r"(?<![\w./§-])(?:[vV]?[\^~]?\d+\.\d+(?:\.\d+)?(?:-[A-Za-z0-9]+)?|[Dd]raft-\d+|RFC \d+|STD \d+)(?![\w.])")
# A project-artifact identifier directly before a version token: the token is a
# revision citation, not a library pin.
ARTIFACT_REVISION_RE = re.compile(r"(?:SPEC|ADR|RFC|PRD|RUNBOOK|ISSUE|PR)[-_ ]?\d+\s*$", re.I)
# Words -> tokens, applied to the whole file and not to the half of it below
# the fence: a loader pays for the frontmatter it opens too, and a node with
# sixty `load_when` triggers costs those tokens on every read, so the budget
# counts the whole file.
TOKENS_PER_WORD = 1.35
# STEM is the LAST-RESORT prefix fold, not the inflection rule. The inflection
# rule is `_stems()` in the canonical stemmer block below, which reduces both
# sides of the comparison; this only catches long words that share a six-letter
# prefix without sharing a stem (`documentation` / `documented`). Until 7.16.0
# this line read "prefix length for the singular/plural fold (test/tests,
# node/nodes)" and handled neither: the test is one-sided, requiring the TASK's
# word to PREFIX a roster word, and a plural never prefixes its own singular.
STEM = 6

# --- canonical stopwords ---------------------------------------------------
# Byte-identical in agent-lint.py and graph-lint.py; seed-lint's
# check_canonical_router_blocks enforces that.
#
# Filler words that carry no routing signal. The pronouns are here because they
# were NOT, and three shipped triggers already wrote "we" ("review the pull
# request before we merge", "do we need an ingest", "which protocol should we
# enter"). That made `we` a scoreable term at df=3, so every task phrased "we
# need X" paid three agents a weight-2 match for saying "we". A fourth trigger
# writing "our" took it further: df=1 earned the RARE-term bonus, and the task
# "our chain of language-model calls loops forever" routed HIGH to `security`
# on the strength of the word "our". A word every task writes cannot select
# between the agents every task is scored against.
STOPWORDS = frozenset(
    "the and for add new from that this with why how are was not you its "
    "change what where when does did into out about a an of to in on it "
    "over via using use onto off around per which while would could should "
    "want need make made get got run see tell show give take find "
    "there any some someone goes going tells told anyone something "
    "stack whole "
    # `down` and `up` were the only directional particles missing while
    # `out`, `off`, `on`, `onto`, `over` and `around` were all present, and
    # the gap cost the same way the pronouns did: a trigger added in 7.16.0
    # ("record what is not written down") made `down` df=1 scoreable
    # vocabulary owned by ONE agent, so "the checkout page went down for
    # nine minutes and we only found out from twitter" routed HIGH to the
    # documentation agent, score 24 against a runner-up of 2. Third instance
    # of one class -- `our`, then the reflexives, then this -- in the
    # release that closed it twice.
    "down up "
    "i me my mine we us our ours he him his she her hers they them their "
    "theirs your yours "
    # The reflexives were missing while every other person was present, and the
    # gap is not cosmetic: a probe agent carrying "yourself" as a trigger took
    # the whole band on "can you deploy this yourself" — df=1, so the pronoun
    # earned the RARE-term bonus and contributed 12 of 20 points. That is the
    # `our` incident above, reproduced with a reflexive, after the fix that was
    # supposed to close the class.
    "myself ourselves yourself yourselves himself herself itself themselves".split()
)
# --- end canonical stopwords -----------------------------------------------


class LintError(Exception):
    pass


@dataclass
class Node:
    path: Path
    meta: dict
    body: str
    text: str                     # the file as written: fences, frontmatter and body
    dir_kind: str | None = None   # set for machinery nodes: the kind their dir implies

    @property
    def id(self) -> str:
        return self.meta.get("id", "")

    @property
    def is_machinery(self) -> bool:
        return self.dir_kind is not None

    @property
    def words(self) -> int:
        """Every word in the file, frontmatter included — what a read costs.

        `est_tokens` is a budget for the file a loader opens, so the figure it
        is judged against has to be the whole of that file. Measured on the
        body alone, a node could carry a routing surface several times the
        size of its prose and stay in band on a number describing less than
        half of what it costs.
        """
        return len(self.text.split())

    @property
    def measured_tokens(self) -> int:
        return int(self.words * TOKENS_PER_WORD)

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
        """A composed child's trigger vocabulary as `check_composition_triggers`
        reads it: the node's own `load_when` tokens plus its slug kept WHOLE.
        The slug is not tokenized: `ef-core` split into `ef` and `core` would
        report `core` as family vocabulary it never wrote. Title and repo words
        stay out: they belong to seed scoring, and a title like "ef-core — the
        persistence expertise" would put `expertise` in every sibling's
        vocabulary. Descent itself matches whole trigger phrases (`resolve`)."""
        return _tokens(" ".join(self.get_list("load_when"))) | {self.id.split(".", 1)[-1]}


def parse_frontmatter(text: str, path: Path):
    """Delegates to the one frontmatter reader (see frontmatter.py).

    This function used to hold its own copy of the parsing rules. Seven
    programs held seven copies, and they disagreed: a description spilling
    onto a second line was rejected by two and silently truncated by three.
    The reader beside this file is this one, promoted verbatim, plus one
    level of nesting for the plant: block.
    """
    try:
        return _frontmatter.parse(text, path)
    except _frontmatter.FrontmatterError as e:
        raise LintError(str(e)) from None


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
            text = p.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text, p)
            nodes.append(Node(p, meta, body, text, dir_kind))
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


def plant_block(text: str) -> dict:
    """The `key: value` pairs of index.md's `plant:` frontmatter block, as
    written less any inline `# comment` tail, as YAML reads it; empty when
    there is no frontmatter or no block. `plant:` is a
    nested map the frontmatter subset stores as an empty list marker, and its
    indented lines are not list items, so the block is read by line rather
    than through parse_frontmatter."""
    if not text.startswith("---\n"):
        return {}
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
                block[k.strip()] = re.sub(r"(^|\s)#.*$", "", v).strip()
    return block


def _unfilled(value: str) -> bool:
    """A template placeholder such as `<bcp47>`, not an owner's answer."""
    return value.startswith("<") and value.endswith(">")


def plant_facts():
    """The four plant facts in PLANT_KEYS order, or None unless index.md
    declares every one of them (present, non-empty, no placeholder): the
    `plant` of a `--plan-json` document and the `plant:` line of `--plan`
    (SPEC-0003 PLAN_PRINTS_PLANT_BLOCK, ADR-0027). A missing or unfilled
    block is rule 14's finding, not the plan's."""
    if not INDEX.exists():
        return None
    block = plant_block(INDEX.read_text(encoding="utf-8"))
    if not all(block.get(k) and not _unfilled(block[k]) for k in PLANT_KEYS):
        return None
    return {k: block[k] for k in PLANT_KEYS}


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
    block = plant_block(text)
    if not block:
        sink.append("index.md: missing `plant:` block (environment_class, commit_attribution, "
                    "deliverable_language, comment_language) — the owner-declared facts")
        return
    unfilled = {k for k, v in block.items() if _unfilled(v)}
    missing = (set(PLANT_KEYS) - {k for k, v in block.items() if v}) | unfilled
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
    composed children. Descent needs a trigger phrase the child writes and its
    parent does not, so a term the siblings share is family vocabulary that
    belongs one level up, and a term half the graph carries makes a one-word
    phrase that descends on tasks that are not about this child at all. Tokens
    under three characters are ignored: `_words` drops them from every task,
    so `0` out of `net8.0` can never match and must never be reported."""
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
    rooted = ROOT_ID in by_id
    # Pre-growth grace: a fresh install carries only machinery nodes. The root
    # becomes mandatory the moment the first project node lands.
    if not rooted and any(not n.is_machinery for n in nodes):
        errs.append(f"missing root node {ROOT_ID!r}")
        return
    index_text = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    # Boundary match: a plain substring test lets an orphan pass whenever its
    # id merely prefixes an unrelated longer id — including a dotted child
    # (`x.orphan` vs `x.orphan.child`); a trailing sentence period
    # (`x.orphan.`) still counts.
    listed = {n.id for n in nodes if re.search(
        rf"(?<![\w.-]){re.escape(n.id)}(?![\w-])(?!\.[\w-])", index_text)}
    # ONE real traversal, seeded by the root and every index-listed node: a
    # listed node is an entry point, so what its edges reach is reachable too
    # (a plant-owned index that lists a node but not the siblings it points
    # at). Only listed nodes' edges are followed, never every node's: the old
    # rootless version unioned all outgoing edges into `seen`, so two
    # mutually-peering ghost nodes marked each other reachable (an orphan
    # island always passed).
    seen, stack = set(), [*listed, *([ROOT_ID] if rooted else [])]
    while stack:
        cur = stack.pop()
        if cur in seen or cur not in by_id:
            continue
        seen.add(cur)
        stack.extend(by_id[cur].out_edges())
    why = (f"unreachable from {ROOT_ID!r} and unlisted in index.md" if rooted else
           "unreachable — no root yet, not listed in index.md, and no listed node reaches it")
    for n in nodes:
        if n.id not in seen:
            errs.append(f"{n.id}: {why}")


LIB_PIN_ROW_RE = re.compile(r"^\|\s*[^|]*\|\s*([^|]*)\|", re.M)
LIB_REVIEWED_RE = re.compile(r"\*\*Last reviewed:\*\*\s*(\S+)")
LIB_PLACEHOLDER_RE = re.compile(r"^\s*(<[^>]*>|YYYY-MM-DD|latest|)\s*$", re.I)
# A markdown link/image destination, or a reference definition's target.
LIB_LINK_RE = re.compile(r"\]\(\s*<?([^)>\s]+)|^\s*\[[^\]]+\]:\s*<?([^\s>]+)", re.M)
LIB_CELL_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _cell_text(cell: str) -> str:
    """A table cell reduced to the words it shows, case-folded: link text
    instead of link syntax, without inline code, emphasis, or padding.

    Folded because an index is prose a person writes, and a row that titles the
    library the way its own docs do — capitalised — is the same row. Comparing
    it case-sensitively reported no row where one plainly existed, which is the
    substring hazard `index_registers` guards against arriving as its mirror
    image: a false RED instead of a false green, and the two are equally good at
    teaching a reader to stop believing the check."""
    return LIB_CELL_LINK_RE.sub(r"\1", cell).strip().strip("`*_ ").strip().lower()


# Headings under which a row records that a page has NOT been written. The
# vocabulary is a contract, not this file's invention: `_schema.md` states the
# same list where an author reads it, and `tests/test_graph_lint.py` holds the
# two together.
PENDING_HEADINGS = ("pending", "planned", "unwritten", "not yet", "to ingest",
                    "backlog", "todo")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")


def _is_pending_heading(text: str) -> bool:
    low = text.lower()
    return any(w in low for w in PENDING_HEADINGS)


def _is_rule_row(line: str) -> bool:
    """A table's `|---|---|` separator, which is punctuation, not content."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return len(cells) > 1 and all(c and set(c) <= set("-:") for c in cells)


def index_registers(index_text: str, page: Path) -> bool:
    """True when libraries/index.md actually *references* `page`.

    Deliberately not a substring test. A short stem sits inside a longer
    sibling's row, inside a column header, inside any sentence of prose — so
    asking `stem in index_text` reports a row where none exists, and the gate
    goes green on precisely the omission it exists to catch. Two things count
    as a reference:

      1. a markdown link (or reference definition) whose *target* resolves to
         the page's file — the link text is free, so an index may title the
         row however it likes, and may reach the page through a folder;
      2. a table cell that is the page's name or stem *whole* — an index that
         names the library in its own column without linking it is thin, but
         it is still a row.

    Separator rows and header rows are excluded from (2): a header is the
    table's vocabulary, never a statement about a page.

    And both are read SECTION by section, because an index has sections that
    mean opposite things. A row under a pending heading exists to record that
    the page has not been written, so counting it as registration makes the
    gate green on precisely the omission it exists to catch — the same failure
    the substring test produces, arriving through the structure instead of the
    string. `PENDING_HEADINGS` names those sections, `_schema.md` states the
    same list where an author reads it, and nothing else is skipped: an index
    with no headings at all registers exactly as it always did.
    """
    targets = {page.name.lower(), page.stem.lower()}
    pending = False
    lines = index_text.splitlines()
    for i, line in enumerate(lines):
        head = HEADING_RE.match(line)
        if head:
            pending = _is_pending_heading(head.group(1))
            continue
        if pending:
            continue
        for m in LIB_LINK_RE.finditer(line):
            dest = (m.group(1) or m.group(2) or "").split("#", 1)[0].split("?", 1)[0]
            if dest.rsplit("/", 1)[-1].lower() in targets:
                return True
        if "|" not in line or _is_rule_row(line):
            continue
        nxt = next((s for s in lines[i + 1:] if s.strip()), "")
        if _is_rule_row(nxt):                    # this line is the header row
            continue
        if any(_cell_text(c) in targets for c in line.strip().strip("|").split("|")):
            return True
    return False


def check_libraries(nodes: list, errs: list) -> None:
    """Every `libraries:` edge resolves to a page, and every page that follows
    the template's form owes the ingest pass its exit: a filled §0 pin (an
    exact version, never a placeholder or "latest"), a dated `Last reviewed`,
    and a row in libraries/index.md that references it (`index_registers`)
    when the index exists. A page with no
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
        if index is not None and not index_registers(index, page):
            errs.append(f"libraries/{page.name}: no row in libraries/index.md "
                        f"outside its pending sections — the close-out "
                        f"librarian registers every drafted page")


def check_artifacts(nodes: list, errs: list) -> None:
    """Artifact edges resolve inside the unified graph and cannot escape it.

    Containment is lexical: the joined path is normalised with no link
    followed. A `--symlink` install places the seed's files as links, so
    `templates/...` resolves into the seed on disk while its path is inside
    the graph; resolving it reported every such edge as an escape. Only the
    existence test follows links, so a dangling link still fails as missing.
    """
    root = os.path.normpath(str(ARTIFACTS_DIR))
    for n in nodes:
        for artifact in n.get_list("artifacts"):
            if not isinstance(artifact, str) or not artifact.strip():
                errs.append(f"{n.id}: artifacts entries must be non-empty paths")
                continue
            joined = os.path.normpath(os.path.join(root, artifact))
            if os.path.commonpath([root, joined]) != root:
                errs.append(f"{n.id}: artifacts → path escapes docs/graph/: {artifact!r}")
                continue
            target = Path(joined)
            if not target.exists():
                errs.append(f"{n.id}: artifacts → missing docs/graph/{artifact}")


# Where in the frontmatter a version token is an ASSERTION rather than a
# routing handle. ASSERTION_KEYS below enumerates those positions; the rule it
# makes checkable is the router's own (docs/graph/index.md): the fact lives in
# docs/graph/libraries/, and a release identifier may appear in a node's
# routing surface without the node claiming anything. `load_when: draft-07` is
# a keyword a task is matched against; `title: the JSON surface, RFC 8259` is
# the node saying which release this project uses.
#
# A key nobody has classified defaults to ROUTING. That residual is disclosed
# here, not caught as a defect — it is the price of a linter that does not
# break on the next key somebody adds.
ASSERTION_KEYS = ("title", "description", "prevents", "reason", "scope", "ends_when")


def check_version_leakage(nodes: list, errs: list) -> None:
    """Version pins live in docs/graph/libraries/ unless the node owns *.versions.

    The rule does not stop at the frontmatter fence: it reads the assertion
    positions of ASSERTION_KEYS as well as the body, because moving a pin up
    three lines was a way to make this check stop seeing it.

    Fenced code and inline code are exempt: quoting a real config line is
    not restating a fact.
    """
    for n in nodes:
        if n.is_machinery:
            continue
        if any(f.endswith(".version") or f.endswith(".versions") for f in n.get_list("owns")):
            continue
        for key in ASSERTION_KEYS:
            for value in n.get_list(key):
                if not isinstance(value, str):
                    continue
                for m in VERSION_RE.finditer(value):
                    if ARTIFACT_REVISION_RE.search(value[max(0, m.start() - 24): m.start()]):
                        continue
                    errs.append(
                        f"{n.id}: version pin {m.group(0)!r} (frontmatter key `{key}`) — versions belong in docs/graph/libraries/; link instead"
                    )
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
            errs.append(
                f"{n.id}: est_tokens={est} but the file measures ~{measured} "
                f"(frontmatter and body; must be within 2x)"
            )
        if not n.is_machinery and len(n.body.strip("\n").splitlines()) > 170:
            errs.append(f"{n.id}: body is {n.body.count(chr(10))} lines — over the 170-line ceiling (aim ~150); split it")


# --- router dry-run ---------------------------------------------------


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


# --- canonical stemmer -----------------------------------------------------
# This block is byte-identical in agent-lint.py and graph-lint.py and
# `seed-lint.py`'s check_canonical_router_blocks enforces that. (It read
# `check_stemmer_sync` for a release: a function of that name has never
# existed, in a comment shipped into every plant.) The two routers already
# carried one copied scorer; the copy is why the compound-fragment fix reached
# only one of them, and why a `STEM = 6` fold documented as handling
# "test/tests, node/nodes" handled neither, in both files, for four releases.

# Words whose trailing -s is not a plural, or whose -ed/-ing tail is not an
# inflection. Reducing these merges unrelated routing vocabulary.
STEM_KEEP = frozenset("""
access address always analysis axis basis bias bus business class cross css
devops focus gross https its less loss miss news ops pass plus press process
progress status this
""".split())

# Irregulars the suffix rules cannot reach. Deliberately tiny: every entry is a
# word shape this roster or a plant's node vocabulary actually uses, not a
# general English lexicon, which is a dependency this file may not have.
STEM_IRREGULAR = {
    "analyses": "analysis", "indices": "index", "matrices": "matrix",
    "vertices": "vertex", "criteria": "criterion", "schemas": "schema",
    "schemata": "schema", "aliases": "alias",
}

# INVARIANT, relied on by both `_match` implementations as a prefilter and
# asserted by tests/test_router_reach.py: every form `_stems(w)` returns starts
# with the same three characters as `w`. Every rule here either strips a suffix
# (leaving a prefix), appends `e` to a prefix, swaps a `-ies` tail for `y`, or
# maps an irregular that shares its first three letters. Anything added that
# breaks this makes the prefilter skip a real match, so the test is the price of
# the optimisation.
STEM_PREFIX = 3

# (suffix, characters to drop, minimum word length). First match wins, so the
# longer and more specific endings are listed first.
STEM_RULES = (
    ("ies", 3, 5), ("sses", 2, 6), ("ches", 2, 6), ("shes", 2, 6),
    ("xes", 2, 5), ("ing", 3, 6), ("ed", 2, 5), ("es", 1, 5), ("s", 1, 4),
)


@lru_cache(maxsize=4096)
def _stems(word: str) -> frozenset:
    """The canonical forms of one word, for comparison against another word's.

    A frozenset rather than a string because English drops a silent -e before
    -ing and -ed: `routing` reduces to `rout`, but the word it inflects is
    `route`. Both candidates are returned and a match is a non-empty
    intersection, which keeps this function free of any vocabulary and
    therefore symmetric — the task side and the roster side are reduced by
    exactly the same rule, which the previous one-sided prefix probe was not.
    """
    if word in STEM_IRREGULAR:
        return frozenset({STEM_IRREGULAR[word]})
    if word in STEM_KEEP or len(word) < 4:
        return frozenset({word})
    for suf, cut, minlen in STEM_RULES:
        if word.endswith(suf) and len(word) >= minlen:
            base = word[:-3] + "y" if suf == "ies" else word[:-cut]
            if suf in ("ing", "ed"):
                # Undouble only a base longer than three letters. `planning`
                # reduces to `plann` and must lose the doubled consonant, but
                # `added` reduces to `add`, whose double IS the word — taking it
                # to `ad` is wrong, and it also broke the three-character stem
                # prefix the `_match` prefilter depends on. Same for `ebbed`,
                # `egged`, `adding`.
                if len(base) > 3 and base[-1] == base[-2]:
                    return frozenset({base[:-1]})          # planning -> plan
                return frozenset({base, base + "e"})       # routing -> rout|route
            if suf in ("sses", "ches", "shes", "xes"):
                # -ches is the plural of -ch AND of -che, and nothing in the
                # word says which: batches -> batch, caches -> cache. Offer
                # both rather than guess, the same way -ing does.
                return frozenset({base, word[:-1]})        # batch|batche
            return frozenset({base})
    return frozenset({word})
# --- end canonical stemmer -------------------------------------------------


def _match(term: str, toks: set) -> int:
    """Token-match strength: 2 exact, 1 prefix-fold, 0 none. Never substring.

    Whole-token matching only (so `field` does not match "greenfield"). An
    exact hit outranks a morphological near-match, so a fuzzy name-fold
    can't outrank an exact trigger.
    """
    if term in toks:
        return 2
    st = _stems(term)
    # Prefilter on the shared three-character prefix before reducing each token;
    # sound by the STEM_PREFIX invariant above, and the reason routing did not
    # get 2.9x slower.
    pre = {s[:STEM_PREFIX] for s in st}
    if any(k[:STEM_PREFIX] in pre and _stems(k) & st for k in toks):
        return 2
    if len(term) >= STEM and any(k.startswith(term[:STEM]) for k in toks):
        return 1
    return 0


def _split_terms(text: str, keep_path_segments: bool = False) -> tuple:
    """(whole, fragment) — a hyphen fragment does not speak for its compound.

    `agent-lint.py` learned this at 7.15.0 and this router received it at
    7.16.0 -- through THIS function, not through `_tokens`, which still reads a
    compound as two ordinary words and survives only as `Node.routable_terms`,
    which nothing calls. A test asserted the divergence, compared `_tokens`
    against agent-lint's live path, and passed while being false; it now asserts
    convergence on the entry point `resolve()` actually scores with.
    Splitting on hyphens and keeping the pieces as first-class tokens made
    `chain`, out of `agent.security`'s trigger "assess the supply-chain and
    secrets handling risk", score exactly like a standalone word — so "our chain
    of language-model calls loops forever" routed to `security` at HIGH. That
    row was still here, verbatim, in the router installed into every plant.

    Measured on a real plant before this change: 60 nodes, 44 hyphenated trigger
    compounds, 71 fragments matching their owner at FULL strength. Eighteen of
    those are df==1, so they also took the rare-term bonus at weight 3 —
    `chain` <- `supply-chain`, `clean` <- `clean-context`, `false` <-
    `false-premise`, `proof` <- `proof-of-concept`, `dry` <- `dry-run`.

    The compound stays whole and a fragment still matches at the near-match
    tier, so "supply chain" written without the hyphen is not lost.
    """
    whole, frag = set(), set()
    for w in re.findall(r"[a-z0-9_/*.-]+", text.lower()):
        cleaned = w.strip("_")
        if len(cleaned) >= 3 and cleaned not in STOPWORDS:
            whole.add(cleaned)
        # Every separator, not just the hyphen. `/` and `.` pieces used to land
        # in `whole` at full strength, so `docs/graph` in `protocol.grow`'s
        # load_when made `graph` speak for it exactly as `supply-chain` once
        # made `chain` speak for `agent.security`. Measured: 13 shipped path
        # compounds across load_when and routing_triggers, and
        # `templates/knowledge-graph/node.template.md` ships
        # `"editing {{repo-or-path}}/**"`, so every plant is taught to write
        # more of them.
        # Path segments first (`/`, `.`, `*`), then hyphen pieces of each.
        # `keep_path_segments` decides only where the PATH segments land: in a
        # node's own id they are its name (`expertise.ef-core` IS `ef-core`),
        # and inside a load_when phrase they are a fragment (`docs/graph` must
        # not let `graph` speak for `protocol.grow`). Hyphen pieces are always
        # fragments, in both cases.
        for seg in re.split(r"[/*.]+", w):
            seg = seg.strip("_")
            if len(seg) >= 3 and seg not in STOPWORDS:
                (whole if keep_path_segments else frag).add(seg)
            for part in seg.split("-"):
                part = part.strip("_")
                if len(part) >= 3 and part not in STOPWORDS and part != seg:
                    frag.add(part)
    return whole, frag - whole


def _strength(term: str, whole: set, frag: set) -> int:
    """Full strength against a whole token; capped at the fragment tier otherwise."""
    m = _match(term, whole)
    return m if m else min(1, _match(term, frag))


def _words(text: str) -> list:
    """The content words of `text`, in order: lowercased, `_` and a trailing
    `.` trimmed, three characters or more, no stopword. One rule for both sides
    of every comparison the router makes: a task's words and a trigger
    phrase's tokens. The regex keeps `-`, `.`, `/` and `*` inside a word, so a
    compound, a dotted name and a path each stay one word; `,`, `:`, `;`,
    `?`, `!` and `)` already end a word, and the trailing `.` is the one mark
    the regex would keep (SPEC-0002 PUNCTUATION_DOES_NOT_CHANGE_A_TERM:
    `prompt.` was a second term beside `prompt`)."""
    out = []
    for w in re.findall(r"[a-z0-9_/*.-]+", text.lower()):
        w = w.strip("_").rstrip(".").strip("_")
        if len(w) >= 3 and w not in STOPWORDS:
            out.append(w)
    return out


def _same(a: str, b: str) -> bool:
    """Two words are one term at the standalone tier: equal, or one
    inflection of the other (`_stems`). A prefix fold is not the same word."""
    return a == b or bool(_stems(a) & _stems(b))


# --- the tier ladder (SPEC-0002 §6, ADR-0026) --------------------------------
# `resolve()` takes its entries from the first tier that hits: a node id the
# task names, a path the task names, a trigger phrase the task holds whole, and
# only then the lexical score. A named id or path is the user telling the
# router which node; words are the router guessing.
#
# A tier-1 or tier-2 hit on more nodes than this is no hit: a task naming a
# dozen ids is a list, not a pointer, and on the round's longest brief the
# strong tiers alone loaded the wrong kind of node.
STRONG_TIER_CAP = 3
# A tier-2 route adds at most this many seed skills whose phrase the task
# holds (SPEC-0002 §6, ADR-0026 amendment 8.1.2); over it none is added, so
# naming a file never floods the session.
PATH_TIER_SKILL_CAP = 2
# A lexical entry needs this many distinct confident terms (whole words at the
# standalone tier). One rare word was enough before: `have` seeded the legal
# corpus node, and `the payroll` would seed payroll.
LEXICAL_MIN_TERMS = 2
# A task with more distinct content words than this is not routed. Lexical
# scoring has no length normalization, so a pasted brief matches everything:
# 1,586 distinct terms scored all 116 nodes of the steward plant and loaded 28.
# Measured with `_words` over the round's prompts: the longest owner prompt
# carries 66 distinct words, a delegation task line 24, the pasted brief 1,332,
# and no row of the seed's corpus more than 20 (SPEC-0002 §6). 100 sits over
# every prompt a person typed and an order of magnitude under a brief.
LONG_TASK_TERMS = 100
NO_SIGNAL_TEXT = "no node matches this task; route a sharper task line, or enter a protocol:"
LONG_TASK_TEXT = "task too long to route ({} terms); run --plan on the task line"

# A path the task names (tier 2) is untrusted input: the route hook feeds every
# prompt through `--plan-json`, so a path is only ever the NAME given to
# `fnmatchcase`, never a pattern, and never touches the filesystem; only the
# graph's own `repo:` values are looked up on disk (`repo_kind`).
PATH_TOKEN_MAX = 256        # a longer whitespace token is skipped, uncounted
PATH_TOKENS_MAX = 64        # path-like tokens considered, in task order
PATH_ECHO_MAX = 80          # characters of a path echoed on a LOAD line
PATH_STRIP = "`'\"()[]<>,;:"
PATH_LIKE_RE = re.compile(r"[A-Za-z0-9_.-]*\.[A-Za-z0-9]{1,10}")
PATH_ECHO_UNSAFE_RE = re.compile(r"[^a-z0-9_./~+-]")


def _is_path(word: str) -> bool:
    """A word the task wrote as a path: it holds `/` or `*`, or it looks like
    a file name (`main.tf`). Neither it nor its segments is a lexical term."""
    return "/" in word or "*" in word or bool(PATH_LIKE_RE.fullmatch(word))


def _load_when_pieces(n) -> tuple:
    """(phrases, patterns) — a node's `load_when` split on commas.

    A piece with no whitespace holding `*` or `/` is a file pattern and is
    never also a phrase, so a task repeating `**/package-lock.json` as words
    holds no phrase. Any other piece is a trigger phrase: `(piece, tokens)`,
    its tokens the piece's content words in order (`_words`), so a dotted or
    hyphenated word stays one token and must be named whole — `target net10`
    does not hit `net10.0`, as `chain` does not speak for `supply-chain`. A
    piece with no tokens is ignored. Brace expansion is not a thing here:
    `*.{ts,tsx}` is the pattern `*.{ts` and the phrase `tsx}`."""
    phrases, patterns = [], []
    for entry in n.get_list("load_when"):
        for piece in str(entry).split(","):
            piece = piece.strip()
            if len(piece.split()) == 1 and ("*" in piece or "/" in piece):
                patterns.append(piece)
                continue
            toks = tuple(_words(piece))
            if toks:
                phrases.append((piece, toks))
    return phrases, patterns


def _holds(seq: list, toks: tuple) -> bool:
    """The task's word sequence holds a phrase's tokens consecutively and in
    order, each the same word at the standalone tier."""
    k = len(toks)
    return any(all(_same(seq[i + j], toks[j]) for j in range(k))
               for i in range(len(seq) - k + 1))


def _held_piece(phrases: list, seq: list, words: set, min_tokens: int = 1,
                exclude: frozenset = frozenset()):
    """The first trigger phrase of at least `min_tokens` tokens the task
    holds, or None. A phrase of two or more tokens must be held contiguous; a
    one-token phrase only as a whole task word equal to it, never a fragment
    or an inflection of another word. Tier 3 reads two tokens and up; a
    one-token piece is read by composition descent alone, inside a parent
    already loaded (SPEC-0002 PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE). Of every
    `load_when` piece, 51% reduced to one token, and as a seed one generic
    word loaded a whole expertise and its closure: `json`, `engine`,
    `workflow`."""
    for piece, toks in phrases:
        if len(toks) < min_tokens or toks in exclude:
            continue
        if (toks[0] in words) if len(toks) == 1 else _holds(seq, toks):
            return piece
    return None


def _task_paths(task: str) -> list:
    """The task's path-like tokens, normalized, in task order, at most
    PATH_TOKENS_MAX of them. The length skip comes before the count, so a
    flood of over-long tokens cannot use the cap up."""
    paths = []
    for tok in task.split():
        if len(tok) > PATH_TOKEN_MAX:
            continue
        # One pass is not enough: `(infra/main.tf).` needs the `.` gone before
        # the `)` is trailing.
        prev = None
        while tok != prev:
            prev = tok
            tok = tok.strip(PATH_STRIP).rstrip(".")
        if "://" in tok or not ("/" in tok or PATH_LIKE_RE.fullmatch(tok)):
            continue
        if len(paths) == PATH_TOKENS_MAX:
            break
        path = tok.lower().replace("\\", "/")
        paths.append(path[2:] if path.startswith("./") else path)
    return paths


class HelperUnavailable(Exception):
    """`source_paths.py` beside this file is absent, fails to load, or lacks
    a tier-2 function (an older copy). Raised inside tier 2, where the route
    catches it as the `inference_skipped` notice (SPEC-0007 §7
    HELPER_ABSENT_BESIDE_GRAPH_LINT)."""


_HELPER: list = []                 # the loaded helper, once per run
_REPO_KINDS: dict = {}             # repo: value as written -> (kind, name), once per run


def _helper():
    """The path-rule helper, `source_paths.py`, loaded by file path from
    beside this file the first time tier 2 reads a task path, so a lint run
    never loads it. Its `repo_kind`, `repo_claim` and `path_matches` are the
    one home of tier 2's `repo:` claim and file-pattern rules."""
    if not _HELPER:
        try:
            spec = _ilu.spec_from_file_location(
                "cypress_source_paths", _Path(__file__).resolve().parent / "source_paths.py")
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:     # absent, unreadable or broken: tier 2 alone pays
            raise HelperUnavailable(str(e)) from e
        if not all(callable(getattr(mod, f, None)) for f in ("repo_kind", "repo_claim", "path_matches")):
            raise HelperUnavailable("source_paths.py lacks repo_kind, repo_claim or path_matches")
        _HELPER.append(mod)
    return _HELPER[0]


def _repo_claim(value: str, path: str):
    """How a node's `repo:` value claims a task path (lowercased): the value's
    kind is read once per run on the value as written, then matched with case
    folded on both sides. An unresolved value adds no notice."""
    helper = _helper()
    if value not in _REPO_KINDS:
        _REPO_KINDS[value] = helper.repo_kind(PLANT, value)
    kind, name = _REPO_KINDS[value]
    return helper.repo_claim(name.lower(), path, kind), len(name.strip("/"))


def _echo(path: str) -> str:
    """A task path as it may appear in hook-injected context: cut, and every
    character outside a plain path alphabet shown as `?`."""
    cut = PATH_ECHO_UNSAFE_RE.sub("?", path[:PATH_ECHO_MAX])
    return cut + ("…" if len(path) > PATH_ECHO_MAX else "")


class How(NamedTuple):
    """How a node entered LOAD, in the `cypress.plan/1` terms (SPEC-0003 §6):
    the kind, its detail (the phrase or the path), and the node it came
    through. A path entry names the path the task gave, the resolved fact; the
    `load_when` glob an inferred one matched is the node's, read with --show."""
    kind: str      # named_id | named_path | inferred | phrase | scored | composed | requires
    detail: str | None = None
    via: str | None = None

    @property
    def suffix(self) -> str | None:
        """The `<- …` the text view prints after a LOAD entry, or None. The
        route hook renders the same suffix from the document (`how_suffix`)."""
        if self.kind == "inferred":
            return f'inferred from "{self.detail}"'
        if self.kind == "composed":
            return f'composed by {self.via} on "{self.detail}"'
        if self.kind == "named_path":
            return f'owns "{self.detail}"'
        if self.kind == "phrase":
            return f'phrase "{self.detail}"'
        return None


class Skip(NamedTuple):
    """Why a node the route reached stayed out of LOAD: a peer of a loaded
    node, or a composed child whose own phrase the task does not hold."""
    kind: str                      # peer | composed
    via: str

    @property
    def order(self) -> tuple:
        """Where its group stands in the skip block: the reasons in the order
        SPEC-0003 §6 lists them (peers, then composed), then by `via`."""
        return (SKIP_KINDS.index(self.kind), self.via)

    @property
    def group(self) -> str:
        """The skip-block group line, up to its `<id>=<path>` items."""
        if self.kind == "peer":
            return f" peer of {self.via}: "
        return f" composed by {self.via}, no specific term: "


SKIP_KINDS = ("peer", "composed")


def _named_paths(nodes: list, paths: list) -> dict:
    """Tier 2: {id: How} for each path the task names, by the first rule that
    claims it: a node's own file; the longest `repo:` claim, decided by what
    the value names on disk (a repository, the plant root or a value outside
    the plant claims nothing); an expertise file pattern (`inferred`); a
    basename exactly one node file carries."""
    if not paths:
        return {}
    helper = _helper()
    files = {where(n.path).lower(): n for n in nodes}
    repos = [(r, n) for n in nodes for r in [n.meta.get("repo")] if isinstance(r, str) and r]
    patterns = [(n, _load_when_pieces(n)[1]) for n in nodes if n.meta.get("kind") == "expertise"]
    by_base: dict = {}
    for n in nodes:
        by_base.setdefault(n.path.name.lower(), []).append(n)
    found: dict = {}
    for p in paths:
        shown = _echo(p)
        owner = next((n for f, n in files.items() if p == f or p.endswith("/" + f)), None)
        if owner is None:
            under = [(size, n) for r, n in repos for claim, size in [_repo_claim(r, p)] if claim]
            owner = max(under, key=lambda x: x[0])[1] if under else None
        if owner is not None:
            found.setdefault(owner.id, How("named_path", shown))
            continue
        inferred = [n for n, pats in patterns if any(helper.path_matches(p, pat.lower()) for pat in pats)]
        for n in inferred:
            found.setdefault(n.id, How("inferred", shown))
        if inferred:
            continue
        same = by_base.get(p.rsplit("/", 1)[-1], [])
        if len(same) == 1:
            found.setdefault(same[0].id, How("named_path", shown))
    return found


def _lexical(nodes: list, words: list) -> list:
    """Tier 4's scored entries: IDF-weighted, a term in many nodes (generic)
    worth little, one in one or two (distinctive) dominating — with the guards
    SPEC-0002 holds the agent router to.

    A term is a task word that is not a dotted node id, not a kind prefix,
    not a path and not a path's segment (SPEC-0002
    IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS); a hyphen piece of a task word is a
    term at the fragment tier only, the mirror of `_split_terms` on the node
    side. A kind prefix is no term on either side: in a node's name `domain`
    matched all ten `domain.*` ids at name weight, and in a task `protocol`,
    `skill` and `agent` scored any node whose `load_when` wrote them. Rarity
    amplifies only a confident match (a whole word at the standalone tier); a
    fragment or a prefix fold is capped at the common weight. A node needs
    LEXICAL_MIN_TERMS distinct confident terms to be an entry at all."""
    ids = {n.id for n in nodes if "." in n.id}
    kind_words = {i.split(".", 1)[0] for i in ids}
    terms: dict = {}
    for w in words:
        if w in ids or w in kind_words or _is_path(w):
            continue
        terms[w] = 2
        for part in w.split("-"):
            if part != w and len(part) >= 3 and part not in STOPWORDS and part not in kind_words:
                terms.setdefault(part, 1)

    buckets = {}
    for n in nodes:
        # A node's OWN id segments are its NAME, not a fragment of somebody
        # else's compound: `expertise.ef-core` is `ef-core`. Only a path
        # written inside a load_when phrase is a fragment.
        name_w, name_f = _split_terms(
            " ".join([n.id, n.meta.get("title", ""), str(n.meta.get("repo", ""))]),
            keep_path_segments=True)
        lw_w, lw_f = _split_terms(" ".join(n.get_list("load_when") + n.get_list("routing_triggers")))
        buckets[n.id] = (name_w - kind_words, name_f - kind_words, lw_w, lw_f)

    df = {t: 0 for t in terms}
    # df stays a PRESENCE count: a term that reaches a node at all is
    # documented there, and changing what counts as presence shifts every
    # weight globally. The fragment cap belongs in scoring alone.
    for name_w, name_f, lw_w, lw_f in buckets.values():
        allt = name_w | name_f | lw_w | lw_f
        for t in terms:
            if _match(t, allt):
                df[t] += 1

    def weight(t: str) -> int:
        d = df.get(t, 0)
        return 3 if d <= 1 else 2 if d <= 3 else 1

    entries = []
    for n in nodes:
        name_w, name_f, lw_w, lw_f = buckets[n.id]
        score, confident = 0, set()
        for t, ts in terms.items():
            on_name = min(ts, _strength(t, name_w, name_f))
            on_lw = min(ts, _strength(t, lw_w, lw_f))
            eff = max(2 * on_name, on_lw)
            if not eff:
                continue
            sure = max(on_name, on_lw) == 2
            score += (weight(t) if sure else min(weight(t), 2)) * eff
            if sure:
                confident.add(min(_stems(t)))
        if len(confident) >= LEXICAL_MIN_TERMS:
            entries.append((score, n))
    entries.sort(key=lambda x: (-x[0], x[1].id))
    best = entries[0][0] if entries else 0
    floor = max(3, (best + 1) // 2) if best >= 3 else best
    return [n for s, n in entries[:3] if s >= floor]


def resolve(nodes: list, task: str):
    """Mirror the traversal in skills/context-router/SKILL.md.

    The entries come from the first tier that hits (SPEC-0002 §6): a node id
    the task names (`named_id`); a path it names (`named_path`, `inferred`);
    a trigger phrase of two or more tokens it holds contiguous (`phrase`);
    else the lexical score (`scored`). A node id is a dotted one: `root` is an
    English word, named by its path. A tier-1 or tier-2 hit on more than
    STRONG_TIER_CAP nodes is no hit; tier 3 is not capped. When tier 2
    decides, each `kind: skill` node with `origin: seed` whose phrase the task
    holds, as tier 3 holds one, is added as `phrase` after the tier-2 entries
    in node-id order; over PATH_TIER_SKILL_CAP such skills none is added. A
    seed skill says how to use a seed tool, and the questions it answers
    usually name a file a plant node owns. A task over LONG_TASK_TERMS distinct
    content words loads nothing with a `long_task` notice; a task no tier
    matches loads nothing with a `no_signal` notice naming the protocol entry
    nodes. Root is never forced.

    The closure then follows `requires` eagerly — you cannot be correct
    without it — and `composes` lazily: a composed child loads only when the
    task holds a trigger phrase of the child's own, one its parent does not
    write. Loud family vocabulary therefore cannot drag a library page into
    every task about the stack, which is the whole reason the lazy edge exists.
    An entry keeps its tier's kind; the `requires` closure is followed before
    any descent, so a node it reaches is `requires`, not `composed` (SPEC-0002
    §6 how precedence).

    Returns (loaded, not_loaded, notices): `loaded` pairs each node with its
    How, `not_loaded` pairs each node with its Skip, and `notices` holds
    (code, text) pairs.
    """
    by_id = {n.id: n for n in nodes}
    seq = _words(task)
    words = set(seq)
    if len(words) > LONG_TASK_TERMS:
        return [], [], [("long_task", LONG_TASK_TEXT.format(len(words)))]
    notices: list = []
    phrases = {n.id: _load_when_pieces(n)[0] for n in nodes}

    def held_phrases(candidates) -> dict:
        held = {}
        for n in candidates:
            piece = _held_piece(phrases[n.id], seq, words, min_tokens=2)
            if piece is not None:
                held[n.id] = How("phrase", piece)
        return held

    def first_tier() -> dict:
        named = {w: How("named_id") for w in seq if "." in w and w in by_id}
        if 0 < len(named) <= STRONG_TIER_CAP:
            return named
        try:
            owned = _named_paths(nodes, _task_paths(task))
        except Exception as e:
            # Broad on purpose: the task is any str, and the route hook runs
            # this on every prompt, where a raise would cost the plant its
            # routing. Reported, not swallowed: the notice says the path tier
            # was skipped, and the route goes on to the next tier.
            owned = {}
            notices.append(("inference_skipped", f"inference skipped: {type(e).__name__}"))
        if 0 < len(owned) <= STRONG_TIER_CAP:
            skills = held_phrases(sorted(
                (n for n in nodes if n.id not in owned and n.meta.get("kind") == "skill"
                 and n.meta.get("origin") == "seed"), key=lambda n: n.id))
            if len(skills) <= PATH_TIER_SKILL_CAP:
                owned.update(skills)
            return owned
        held = held_phrases(nodes)
        if held:
            return held
        return {n.id: How("scored") for n in _lexical(nodes, seq)}

    entry_how = first_tier()
    if not entry_how:
        protocols = sorted(n.id for n in nodes if n.meta.get("kind") == "protocol")
        notices.append(("no_signal", " ".join([NO_SIGNAL_TEXT, ", ".join(protocols)]).rstrip()))
        return [], [], notices

    loaded: list = []          # [(Node, How)]
    seen: set = set()
    reasons: dict = {}         # id -> Skip, why it is NOT loaded
    # An entry is an entry however it is reached: a child entry popped through
    # its parent's closure keeps its own How, not `requires` or `composed`.
    # Descent waits until every `requires:` edge met so far is followed, so a
    # node the closure requires is `requires`, never `composed`, whichever edge
    # the walk meets first; a child that requires its composing parent back
    # leaves the parent `composed` (SPEC-0002 §6 how precedence).
    stack = [(by_id[i], how) for i, how in reversed(list(entry_how.items()))]
    descents: list = []
    while stack or descents:
        n, how = stack.pop() if stack else descents.pop()
        if n.id in seen:
            continue
        seen.add(n.id)
        loaded.append((n, entry_how.get(n.id, how)))
        for r in n.get_list("requires"):
            if r in by_id:
                stack.append((by_id[r], How("requires", via=n.id)))
        if n.meta.get("kind") != "expertise":
            continue
        kids = [by_id[c] for c in n.get_list("composes") if c in by_id]
        family = frozenset(toks for _piece, toks in phrases[n.id])
        hits = 0
        for c in kids:
            # The child's OWN phrase, held as tier 3 holds one, or its
            # one-token piece as a whole word: a word of a longer phrase is
            # not enough (SPEC-0002 COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE).
            # Descent on any single term pulled four of five host children
            # into one brief.
            piece = _held_piece(phrases[c.id], seq, words, exclude=family)
            if piece is not None:
                hits += 1
                descents.append((c, How("composed", piece, n.id)))
            else:
                reasons.setdefault(c.id, Skip("composed", n.id))
        # A single child that matches is an ordinary descent, not a symptom;
        # only a parent handing over most of a real menu says the task or the
        # triggers are too generic.
        if len(kids) > 1 and hits * 2 > len(kids):
            notices.append(("wide_descent", f"wide descent from {n.id}: {hits} of {len(kids)} "
                                            f"children — the task or the triggers are too generic"))
    for n, _ in loaded:
        for p in n.get_list("peers"):
            if p in by_id:
                reasons.setdefault(p, Skip("peer", n.id))
    not_loaded = [(by_id[i], r) for i, r in reasons.items() if i not in seen]
    return loaded, not_loaded, notices


def check_frontmatter_portable(nodes: list, errs: list) -> None:
    """Every node's frontmatter also parses under a strict-YAML loader.

    The reader beside this file (frontmatter.py) is deliberately lenient: it
    splits `key: value` on the FIRST colon and keeps the rest verbatim, so an
    unquoted value carrying an inner ': ' (colon-space) reads fine here, and a
    host that reads the graph through the same reader (Claude Code) loads it.
    A host whose loader parses frontmatter as STRICT YAML (Prime Agent) reads
    that inner ': ' as a nested mapping and REJECTS the whole block, dropping
    the node on one of two supported hosts with no error the plant ever sees.

    So a node authored into this plant — by grow, by graft, or by hand — must
    stay on the two readers' overlap: a top-level unquoted, non-list scalar
    value may not contain ': ' nor end in a bare ':'. Quote the value or reword
    the clause. Mirrors seed-lint's check_frontmatter_is_portable_yaml, which
    holds the seed's own nodes to the same rule before they are installed here.
    """
    for n in nodes:
        text = n.text
        lines = text.split("\n")
        try:
            start = lines.index("---")
            end = lines.index("---", start + 1)
        except ValueError:
            continue
        for line in lines[start + 1:end]:
            if not line or line[:1] in " \t#":          # nested / comment / blank
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            value = value.strip()
            if not value or value[:1] in "\"'[":         # list/mapping opener, quoted, inline list
                continue
            scalar_value = value.split("  #", 1)[0].rstrip()   # reader strips '  #comment'
            if re.search(r":(?:\s|$)", scalar_value):
                errs.append(
                    f"{n.id or n.path}: frontmatter `{key.strip()}` value carries an "
                    f"inner ': ' ({scalar_value!r}) — the lenient reader keeps it but a "
                    f"strict-YAML loader (e.g. Prime Agent) reads it as a nested mapping "
                    f"and drops the node. Quote it or reword the clause.")


PLAN_SCHEMA = "cypress.plan/1"
PLANT = HERE.parent.parent                       # the plant root every printed path is relative to
SKIP_HEADER = "skip (cross only if the task needs it):"   # also a literal in route-hook.py
# `--show` (SPEC-0003 §6): node edges print as bare ids, leaf entries as paths
# from the plant root, the provenance keys on one `origin:` line. The router
# and spawn keys are dropped; every other key is printed as it is.
SHOW_EDGES = ("owns", "requires", "peers", "composes", "delegates_to")
SHOW_LEAVES = ("artifacts", "libraries", "plant_knowledge")
SHOW_ORIGIN = ("origin", "repo", "status", "status_date", "owner", "ends_when", "scope",
               "reason", "recorded_in", "departs_from")
SHOW_DROPS = frozenset({"load_when", "routing_triggers", "est_tokens", "tier",
                        "kind", "name", "description", "prevents", "tools", "model", "effort",
                        "can_delegate", "max_spawn_depth", "command"})


def where(path: Path) -> str:
    """A file as the views print it: relative to the plant root, so no session
    searches for a file the router already found (SPEC-0003
    PLAN_ENTRY_NAMES_THE_NODE_FILE)."""
    try:
        return path.relative_to(PLANT).as_posix()
    except ValueError:
        return path.as_posix()


def short_title(n) -> str:
    """The title with a leading `<slug> — ` cut when the slug is the id's last
    dotted segment: the id printed before it already says it."""
    return str(n.meta.get("title", "")).removeprefix(n.id.rsplit(".", 1)[-1] + " — ")


def plan(nodes: list, task: str) -> tuple:
    """The route both views print, in their order: the notices, the plant
    facts (or None), the LOAD token total, LOAD as (node, path, How) by id
    (the seed skills a tier-2 route adds after the rest, by id: SPEC-0002 §6),
    and the skipped nodes as (node, path, Skip) in skip-block order: by
    group, then by id."""
    loaded, not_loaded, notices = resolve(nodes, task)
    total = sum(n.meta.get("est_tokens", 0) for n, _ in loaded)
    path_route = any(how.kind in ("named_path", "inferred") for _, how in loaded)
    load = [(n, where(n.path), how) for n, how in sorted(
        loaded, key=lambda x: (path_route and x[1].kind == "phrase", x[0].id))]
    skip = [(n, where(n.path), why)
            for n, why in sorted(not_loaded, key=lambda x: (x[1].order, x[0].id))]
    return notices, plant_facts(), total, load, skip


def print_plan(notices: list, plant, total: int, load: list, skip: list) -> None:
    """`--plan`, the compact grammar (SPEC-0003 §6, ADR-0025): one line each,
    no padding, the id first on every entry and every id with its path. The
    `plant:` line carries the four facts a session that never opens index.md
    would otherwise miss (ADR-0027). No line echoes the task."""
    for _code, note in notices:
        print(f"! {note}")
    if plant:
        print("plant: " + " ".join(f"{k}={v}" for k, v in plant.items()))
    print(f"LOAD {len(load)} ~{total}t")
    for n, path, how in load:
        print(f"{n.id} {path} | {short_title(n)}" + (f" <- {how.suffix}" if how.suffix else ""))
    groups: dict = {}
    for n, path, why in skip:
        groups.setdefault(why.group, []).append(f"{n.id}={path}")
    if groups:
        print(SKIP_HEADER)
    for group, items in groups.items():
        print(group + " ".join(items))


def plan_document(task: str, notices: list, plant, total: int, load: list, skip: list) -> dict:
    """`--plan-json`, the `cypress.plan/1` document (SPEC-0003 §6). It carries
    no copy of the task, only the SHA-256 of its UTF-8 bytes as received in
    argv, so a hook can bind the document to its prompt without an echo. The
    only task-derived strings are inferred paths, already cut by `_echo`."""
    return {
        "schema": PLAN_SCHEMA,
        "task_sha256": hashlib.sha256(task.encode("utf-8", "surrogateescape")).hexdigest(),
        "plant": plant,
        "notices": [{"code": code, "text": text} for code, text in notices],
        "est_tokens": total,
        "load": [{"id": n.id, "path": path, "title": str(n.meta.get("title", "")),
                  "how": {"kind": how.kind, "detail": how.detail, "via": how.via}}
                 for n, path, how in load],
        "skip": [{"id": n.id, "path": path, "kind": why.kind, "via": why.via}
                 for n, path, why in skip],
    }


def show_view(n) -> str:
    """`--show <id>`: the §6 header, one blank line, the body verbatim. The
    file stays canonical; the view is derived on every call, never cached."""
    def joined(value) -> str:
        return ", ".join(map(str, value)) if isinstance(value, list) else str(value)

    head = [f"# {n.id} {where(n.path)}: {short_title(n)}"]
    for key in SHOW_EDGES:
        if key in n.meta:
            head.append(f"{key}: {joined(n.meta[key])}")
    def leaf(key: str, entry) -> str:
        if key == "libraries":
            return where(LIBS_DIR / f"{entry}.md")
        # `Path` drops a trailing slash; a directory entry keeps it
        return where(HERE / str(entry)) + ("/" if str(entry).endswith("/") else "")

    for key in SHOW_LEAVES:
        if key in n.meta:
            head.append(f"{key}: " + ", ".join(leaf(key, v) for v in n.get_list(key)))
    origin = [f"{key}: {n.meta[key]}" for key in SHOW_ORIGIN if key in n.meta]
    if origin:
        head.append(" ".join(origin))
    shown = {"id", "title", *SHOW_EDGES, *SHOW_LEAVES, *SHOW_ORIGIN} | SHOW_DROPS
    head += [f"{key}: {joined(value)}" for key, value in n.meta.items() if key not in shown]
    return "\n".join(head) + "\n\n" + n.body.removeprefix("\n")


def show(nodes: list, ids: list) -> int:
    """Print `show_view` for each id in the order given, one blank line
    between nodes. An unknown id prints nothing and exits 2."""
    by_id = {n.id: n for n in nodes}
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        print(f"graph-lint: --show: no node has the id {', '.join(unknown)}", file=sys.stderr)
        return 2
    views = [show_view(by_id[i]) for i in ids]
    sys.stdout.write("".join(v + ("\n" if v.endswith("\n") else "\n\n") for v in views[:-1])
                     + views[-1])
    return 0


# --- `--eval`: the node-route corpus, per class (SPEC-0002) ------------------
# `--eval <tsv>` routes every row of a corpus in the §6 shape and reports each
# class on its own lines, never averaged: `contract` rows are the trigger set's
# self-consistency, `paraphrase` rows generalization, `adversarial` rows bait,
# `unknown-domain` rows the abstention.
CORPUS_CLASSES = ("contract", "paraphrase", "adversarial", "unknown-domain")
# A held-out row may not be a copy of its target's vocabulary. The ceiling
# has agent-lint.py's PARAPHRASE_MAX_OVERLAP value but is its own fact: the
# trigger side below reads piece words, which agent-lint does not, and the two
# files ship to different directories, so each is registered on its own in
# tests/ratchets.json (`max`, as HELD_OUT_PIECE_WORDS: lower is stricter). The
# target is the `load_when` of the row's required ids. Task side:
# the share of the row's content words that vocabulary holds. Trigger side:
# the share of one `load_when` piece the row holds, read only for pieces of
# HELD_OUT_PIECE_WORDS content words or more. Node pieces are often one or two
# words (`canonize`, `grill.md`), and a row naming one whole is a row about
# that node, not a row written from its triggers: read at every length, four
# of the fifteen verbatim owner prompts measured 1.0.
GRAPH_PARAPHRASE_MAX_OVERLAP = 0.50
HELD_OUT_PIECE_WORDS = 3
ROW_ECHO_MAX = 120          # characters of a corpus row a failure line repeats
# Ratchets, registered in tests/ratchets.json with their direction and set at
# the values the router measured over tests/graph-routes.golden.tsv on a fresh
# seed install when the tier ladder landed (7.37.0). A floor may only rise and
# a ceiling only fall; loosening one is an edit to tests/ratchets.json, on
# purpose.
#
# They gate only on the graph they were measured on: one whose every node
# carries `origin: MEASURED_GRAPH_ORIGIN`, the seed's own install. This file
# ships into every plant, and a plant's grown graph and its own corpus were
# never measured; a floor of eight abstentions would fail a plant with fewer
# unknown-domain rows forever. There every figure prints and one line says the
# ratchets are not gated (SPEC-0002 GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH,
# the node-router twin of agent-lint.py's MEASURED_ROSTER_ORIGIN). The corpus
# checks (malformed, vacuous, held-out) gate on every graph.
MEASURED_GRAPH_ORIGIN = "seed"
GRAPH_CONTRACT_RECALL_MIN = 1.0           # floor: required ids loaded / required ids, contract rows (8/8)
GRAPH_ADVERSARIAL_FORBIDDEN_MAX = 0       # ceiling: forbidden ids loaded, adversarial rows
GRAPH_UNKNOWN_ABSTAIN_MIN = 8             # floor: unknown-domain rows that load nothing (8 of 9)
# Ceiling per class on the share of loaded est_tokens outside the requires
# closure of the row's required ids, measured to two places and rounded up.
# No unknown-domain entry: every node such a row loads is irrelevant, so its
# share is 0 or 1 and says nothing the abstention floor above does not.
GRAPH_IRRELEVANT_SHARE_MAX = {
    "contract": (0.58, "measured 0.572"),
    "paraphrase": (0.51, "measured 0.503"),
    "adversarial": (0.43, "measured 0.430"),
}
GRAPH_PARAPHRASE_MIN_ROWS = 14            # floor: the held-out set may not be thinned
GRAPH_ADVERSARIAL_MIN_ROWS = 8            # floor: nor may the bait set


def _content_words(text: str) -> set:
    """agent-lint.py's measure of a row's words, for the overlap check."""
    return {w for w in re.findall(r"[a-z0-9_]+", text.lower())
            if len(w) >= 3 and w not in STOPWORDS}


def _overlap(task: str, targets: list) -> float:
    """How much of a held-out row is its targets' own `load_when`, measured
    both ways (HELD_OUT_STAYS_HELD_OUT); the larger side is the verdict."""
    words = _content_words(task)
    if not words:
        return 1.0
    pieces = [p for n in targets for entry in n.get_list("load_when") for p in str(entry).split(",")]
    vocab = set().union(*(_content_words(p) for p in pieces)) if pieces else set()
    side = sum(1 for w in words if w in vocab) / len(words)
    for p in pieces:
        pw = _content_words(p)
        if len(pw) >= HELD_OUT_PIECE_WORDS:
            side = max(side, sum(1 for w in pw if w in words) / len(pw))
    return side


def _echo_row(task: str) -> str:
    """A corpus row as a failure names it: one line, cut at ROW_ECHO_MAX
    characters, since an `@file:` row can be a whole brief."""
    line = " ".join(task.split())
    return line[:ROW_ECHO_MAX] + ("…" if len(line) > ROW_ECHO_MAX else "")


def _read_corpus(tsv: Path, by_id: dict) -> tuple:
    """(rows, faults): rows as (task, required, forbidden, class); a fault
    names a line that is not four tab-separated columns with a known class, an
    `@file:` that cannot be read, an id no node has, or a row that cannot
    fail: an adversarial row that baits nothing (`forbidden_ids` is `-`), yet
    counts toward GRAPH_ADVERSARIAL_MIN_ROWS, and an unknown-domain row that
    requires ids an abstention never loads (VACUOUS_CORPUS_IS_REFUSED)."""
    rows, faults = [], []
    for ln, line in enumerate(tsv.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 4 or cols[3].strip() not in CORPUS_CLASSES:
            faults.append(f"line {ln} is not task, required, forbidden, class")
            continue
        task, required, forbidden, cls = (c.strip() for c in cols)
        if task.startswith("@file:"):
            try:
                task = (tsv.parent / task[len("@file:"):]).read_text(encoding="utf-8")
            except OSError as e:
                faults.append(f"line {ln}: {task} unreadable ({e.strerror})")
                continue
        ids = [[] if s == "-" else [x.strip() for x in s.split(",") if x.strip()]
               for s in (required, forbidden)]
        unknown = [i for i in ids[0] + ids[1] if i not in by_id]
        if unknown:
            faults.append(f"line {ln} names no node: {', '.join(unknown)}")
            continue
        if cls == "adversarial" and not ids[1]:
            faults.append(f"line {ln} is vacuous: adversarial row \"{_echo_row(task)}\" "
                          f"forbids no id, so it baits nothing")
            continue
        if cls == "unknown-domain" and ids[0]:
            faults.append(f"line {ln} is vacuous: unknown-domain row \"{_echo_row(task)}\" "
                          f"requires ids, but its outcome is an abstention")
            continue
        rows.append((task, ids[0], ids[1], cls))
    return rows, faults


def evaluate(nodes: list, tsv: Path) -> int:
    """`--eval <tsv>`: every figure on a line naming its class, then the
    ratchets. Exit 1 on a held-out row that is a copy, a malformed corpus, or
    a vacuous one, and on the measured graph on a breached ratchet; 0
    otherwise."""
    by_id = {n.id: n for n in nodes}
    measured_graph = bool(nodes) and all(
        str(n.meta.get("origin", "")).strip() == MEASURED_GRAPH_ORIGIN for n in nodes)
    try:
        rows, faults = _read_corpus(tsv, by_id)
    except (OSError, UnicodeDecodeError) as e:
        print(f"graph-lint --eval: FAIL, cannot read the corpus {tsv.name}: "
              f"{getattr(e, 'strerror', None) or type(e).__name__}", file=sys.stderr)
        return 1
    if faults:
        for f in faults:
            print(f"graph-lint --eval: FAIL, {tsv.name}: {f}", file=sys.stderr)
        return 1
    if not any(required for _t, required, _f, _c in rows):
        print(f"graph-lint --eval: FAIL, {tsv.name} is vacuous: every row expects an "
              f"abstention, so no figure measures a route", file=sys.stderr)
        return 1

    def closure(ids: list) -> set:
        out, stack = set(), list(ids)
        while stack:
            i = stack.pop()
            if i not in out and i in by_id:
                out.add(i)
                stack.extend(by_id[i].get_list("requires"))
        return out

    stats = {c: {"rows": 0, "req": 0, "hit": 0, "with_req": 0, "covered": 0, "loaded": 0,
                 "est": 0, "irrelevant": 0, "forbidden": 0, "abstain": 0, "overlap": 0.0}
             for c in CORPUS_CLASSES}
    copies = []
    for task, required, forbidden, cls in rows:
        loaded = {n.id: n for n, _how in resolve(nodes, task)[0]}
        allowed = closure(required)
        b = stats[cls]
        b["rows"] += 1
        b["req"] += len(required)
        b["hit"] += sum(1 for i in required if i in loaded)
        b["with_req"] += bool(required)
        b["covered"] += bool(required) and all(i in loaded for i in required)
        b["loaded"] += len(loaded)
        b["est"] += sum(n.meta.get("est_tokens", 0) for n in loaded.values())
        b["irrelevant"] += sum(n.meta.get("est_tokens", 0) for i, n in loaded.items() if i not in allowed)
        b["forbidden"] += sum(1 for i in forbidden if i in loaded)
        b["abstain"] += not loaded
        if cls in ("paraphrase", "adversarial") and required:
            ov = _overlap(task, [by_id[i] for i in required])
            b["overlap"] = max(b["overlap"], ov)
            if ov > GRAPH_PARAPHRASE_MAX_OVERLAP:
                copies.append((cls, task, required, ov))

    def share(b: dict) -> float:
        return b["irrelevant"] / b["est"] if b["est"] else 0.0

    print(f"graph-lint --eval: {tsv.name}, per class, never averaged")
    for cls in CORPUS_CLASSES:
        b = stats[cls]
        if not b["rows"]:
            continue
        line = (f"{cls}: rows {b['rows']}, required recall {b['hit']}/{b['req']}, "
                f"covered {b['covered']}/{b['with_req']}, "
                f"mean loaded {b['loaded'] / b['rows']:.1f}, irrelevant share {share(b):.2f}, "
                f"forbidden {b['forbidden']}, abstain {b['abstain']}")
        if cls in ("paraphrase", "adversarial"):
            line += f", max overlap {b['overlap']:.2f}"
        print(line)

    failures = [f"{cls} row \"{_echo_row(task)}\" shares {ov:.2f} of its words with the load_when of "
                f"{', '.join(required)}, above GRAPH_PARAPHRASE_MAX_OVERLAP "
                f"{GRAPH_PARAPHRASE_MAX_OVERLAP}: a held-out row must stay held out; relabel it "
                f"contract or write a real one"
                for cls, task, required, ov in copies]
    breaches = []              # (ratchet, failure line)
    contract = stats["contract"]
    recall = contract["hit"] / contract["req"] if contract["req"] else 0.0
    if recall < GRAPH_CONTRACT_RECALL_MIN:
        breaches.append(("GRAPH_CONTRACT_RECALL_MIN",
                         f"contract required recall {recall:.2f} below "
                         f"GRAPH_CONTRACT_RECALL_MIN {GRAPH_CONTRACT_RECALL_MIN}"))
    if stats["adversarial"]["forbidden"] > GRAPH_ADVERSARIAL_FORBIDDEN_MAX:
        breaches.append(("GRAPH_ADVERSARIAL_FORBIDDEN_MAX",
                         f"adversarial forbidden {stats['adversarial']['forbidden']} above "
                         f"GRAPH_ADVERSARIAL_FORBIDDEN_MAX {GRAPH_ADVERSARIAL_FORBIDDEN_MAX}"))
    if stats["unknown-domain"]["abstain"] < GRAPH_UNKNOWN_ABSTAIN_MIN:
        breaches.append(("GRAPH_UNKNOWN_ABSTAIN_MIN",
                         f"unknown-domain abstain {stats['unknown-domain']['abstain']} below "
                         f"GRAPH_UNKNOWN_ABSTAIN_MIN {GRAPH_UNKNOWN_ABSTAIN_MIN}"))
    for cls, (ceiling, _what) in GRAPH_IRRELEVANT_SHARE_MAX.items():
        if share(stats[cls]) > ceiling:
            breaches.append(("GRAPH_IRRELEVANT_SHARE_MAX",
                             f"{cls} irrelevant share {share(stats[cls]):.2f} above "
                             f"GRAPH_IRRELEVANT_SHARE_MAX[{cls}] {ceiling}"))
    for cls, floor, name in (("paraphrase", GRAPH_PARAPHRASE_MIN_ROWS, "GRAPH_PARAPHRASE_MIN_ROWS"),
                             ("adversarial", GRAPH_ADVERSARIAL_MIN_ROWS, "GRAPH_ADVERSARIAL_MIN_ROWS")):
        if stats[cls]["rows"] < floor:
            breaches.append((name, f"{cls} rows {stats[cls]['rows']} below {name} {floor}: deleting "
                                   f"the rows the router fails is not the router improving"))
    if measured_graph:
        failures += [line for _name, line in breaches]
    else:
        # One line, no digit: it names no figure, so it needs no class.
        over = list(dict.fromkeys(name for name, _line in breaches))
        print(f"graph-lint --eval: GRAPH_* ratchets reported, not gated: a node of this graph "
              f"is not origin {MEASURED_GRAPH_ORIGIN}, and they were measured on the seed's own "
              f"graph" + (f"; past a ratchet here: {', '.join(over)}" if over else ""))
    for f in failures:
        print(f"graph-lint --eval: FAIL, {f}", file=sys.stderr)
    if failures:
        return 1
    print("graph-lint --eval: OK, every ratchet holds" if measured_graph
          else "graph-lint --eval: OK, the corpus checks hold")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--graph", action="store_true", help="print the requires-DAG")
    ap.add_argument("--warn", action="store_true",
                    help="report every error but exit 0 — the staged-adoption "
                         "mode a plant runs while it closes findings a newly "
                         "installed check surfaced")
    ap.add_argument("--plan", metavar="TASK", help="dry-run the context router for TASK")
    ap.add_argument("--plan-json", metavar="TASK",
                    help="the same route as one cypress.plan/1 JSON document; pass "
                         "the task as one --plan-json=TASK element")
    ap.add_argument("--show", nargs="+", metavar="ID",
                    help="print each node: a header with every pointer resolved, then its body")
    ap.add_argument("--eval", metavar="TSV", type=Path,
                    help="route every row of a node-route corpus and gate each class on its ratchets")
    args = ap.parse_args()

    try:
        nodes = load_nodes()
    except LintError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    if args.show:
        return show(nodes, args.show)
    if args.eval:
        return evaluate(nodes, args.eval)
    if args.plan:
        print_plan(*plan(nodes, args.plan))
        return 0
    if args.plan_json is not None:
        print(json.dumps(plan_document(args.plan_json, *plan(nodes, args.plan_json))))
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
    check_frontmatter_portable(nodes, errs)
    check_budget(nodes, errs)

    for w in warns:
        print(f"  ! warning: {w}", file=sys.stderr)
    if errs:
        # `--warn` prints the same findings and exits 0. A machinery upgrade can
        # install a check the plant has never run, and a plant that was green
        # the day before goes red on work it has not been asked for yet. The
        # honest handling is a staged window, not a quieter check: the findings
        # are printed in full either way, and only the exit code moves. This
        # mirrors grill-lint's own `--warn`, so a plant has ONE adoption mode
        # across both linters rather than a different answer per tool.
        label = "warning" if args.warn else "error"
        print(f"graph-lint: {len(errs)} {label}(s) in {len(nodes)} node(s)\n", file=sys.stderr)
        for e in errs:
            print(f"  {'!' if args.warn else '✗'} {e}", file=sys.stderr)
        if args.warn:
            print("graph-lint: --warn — reported, not enforced", file=sys.stderr)
        return 0 if args.warn else 1

    total = sum(n.meta.get("est_tokens", 0) for n in nodes)
    print(f"graph-lint: OK — {len(nodes)} nodes, ~{total} tokens if fully loaded")
    print("(no task should ever load them all; see docs/graph/index.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
