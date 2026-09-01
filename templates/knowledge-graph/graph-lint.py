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
    python3 graph-lint.py --graph         # print requires-DAG
    python3 graph-lint.py --plan "TASK"   # dry-run the context router

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
         "protocol", "skill", "agent", "method"}
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
LIST_KEYS = {"owns", "requires", "peers", "libraries", "artifacts", "load_when"}

# A version pin: 2.7.2, v2.7.2, ^15.0.0, ~4.8.2, 0.0.13-SNAPSHOT, 8.0.31.
# The lookbehind excludes `§5.4` (a section reference) and any digit/word/
# path character so `docs/v2.1` and `1.2.3` inside a word don't match; the
# optional leading v is part of the match so `v2.7.2` cannot hide behind it.
VERSION_RE = re.compile(r"(?<![\w./§-])[vV]?[\^~]?\d+\.\d+(\.\d+)?(-[A-Za-z0-9]+)?(?![\w.])")
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
    ids = {n.id for n in nodes}
    for n in nodes:
        for key in ("requires", "peers"):
            for target in n.get_list(key):
                if target not in ids:
                    errs.append(f"{n.id}: {key} → unknown node {target!r}")
                if target == n.id:
                    errs.append(f"{n.id}: {key} → itself")


def check_acyclic(nodes: list, errs: list) -> None:
    graph = {n.id: list(n.get_list("requires")) for n in nodes}
    WHITE, GREY, BLACK = 0, 1, 2
    colour = dict.fromkeys(graph, WHITE)

    def visit(u: str, stack: list) -> None:
        colour[u] = GREY
        for v in graph.get(u, []):
            if v not in colour:
                continue
            if colour[v] == GREY:
                cyc = " → ".join(stack[stack.index(v):] + [v])
                errs.append(f"requires cycle: {cyc}")
            elif colour[v] == WHITE:
                visit(v, stack + [v])
        colour[u] = BLACK

    for nid in graph:
        if colour[nid] == WHITE:
            visit(nid, [nid])


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
                stack2.extend(by[cur].get_list("requires") + by[cur].get_list("peers"))
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
        stack.extend(by_id[cur].get_list("requires") + by_id[cur].get_list("peers"))
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


def check_libraries(nodes: list, errs: list) -> None:
    for n in nodes:
        for lib in n.get_list("libraries"):
            if not (LIBS_DIR / f"{lib}.md").exists():
                errs.append(f"{n.id}: libraries → missing page docs/graph/libraries/{lib}.md")


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

    Scoring is IDF-weighted: a term in many nodes (generic) is worth
    little; a term in one or two (distinctive) dominates.
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
    seeds = [n for s, n in entries[:3] if s >= floor] or [by_id[ROOT_ID]]

    loaded = {}
    stack = list(seeds)
    while stack:
        n = stack.pop()
        if n.id in loaded:
            continue
        loaded[n.id] = n
        for r in n.get_list("requires"):
            if r in by_id:
                stack.append(by_id[r])

    skipped = {
        p: by_id[p]
        for n in loaded.values()
        for p in n.get_list("peers")
        if p in by_id and p not in loaded
    }
    return list(loaded.values()), list(skipped.values())


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
        loaded, skipped = resolve(nodes, args.plan)
        total = sum(n.meta.get("est_tokens", 0) for n in loaded)
        print(f"task: {args.plan}\n")
        print(f"LOAD ({len(loaded)} nodes, ~{total} tokens):")
        for n in sorted(loaded, key=lambda x: x.id):
            print(f"  {n.id:<28} {n.meta.get('title','')}")
        if skipped:
            print("\nNOT LOADED (peers — cross only if the task requires it):")
            for n in sorted(skipped, key=lambda x: x.id):
                print(f"  {n.id:<28} {n.meta.get('title','')}")
        return 0

    if args.graph:
        for n in sorted(nodes, key=lambda x: x.id):
            for r in n.get_list("requires"):
                print(f"{n.id} -> {r}")
        return 0

    errs: list = []
    for n in nodes:
        check_schema(n, errs)
    check_unique_ids(nodes, errs)
    check_unique_ownership(nodes, errs)
    check_edges(nodes, errs)
    check_acyclic(nodes, errs)
    check_reachability(nodes, errs)
    check_libraries(nodes, errs)
    check_artifacts(nodes, errs)
    check_version_leakage(nodes, errs)
    check_budget(nodes, errs)

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
