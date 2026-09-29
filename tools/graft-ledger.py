#!/usr/bin/env python3
"""graft-ledger: the three-way table a graft starts from, and the base it rests on.

A graft compares three versions of every seed-owned machinery file: the BASE
(the seed the plant was installed from), the SEED (the checkout being grafted
on) and the PLANT (what the plant carries now). This tool prints that table,
one row per file, and the base it used, so a steward reads the classes instead
of working them out by hand.

Classes, first match wins:

  CURRENT       the plant's bytes equal the seed's
  FAST-FORWARD  the plant equals the base and the seed differs: the installer
                may replace it, nothing of the plant's is lost
  KEEP-PLANT    the seed equals the base and the plant differs: the seed has
                nothing new here, the plant's edit stands
  SEED-NEW      the seed has the file and neither the base nor the plant does
  HARVESTED     all three differ, every line the plant added over the base
                is already in the seed's version (a harvest carried it back),
                and no line the plant removed is still in it
  MERGE         all three differ otherwise: reconcile by hand before the
                installer overwrites the plant's version

A row is one line: the class, the plant path, and the seed path it installs
from. Rows cover the files the seed carries now: the method surface under
docs/graph/ (protocols, method, agents, skills, templates, the delivered tools
and the engines; the legal corpus only when the stamp says it was placed),
plus the kernel and the harness adapter files the plant carries. A plant's own
node gets no row, and neither does a file the seed no longer ships. The plant
is walked through tools/plant_walk.py, so a nested plant copy and a symlinked
directory are not read as this plant's; the plant-to-seed path map is
graft-audit.py's own.

THE BASE

The plant's .cypress/seed.json names the version it was installed from. When
the seed checkout has that version's tag (v<version> or <version>), the tag is
the base. Most releases carry no tag, so otherwise the base is inferred by
content lineage: the seed commit, among those reachable from HEAD, at which
the most plant machinery files are byte-equal to the seed's version of them.
The number that matched is printed with it. A tie goes to a commit whose
manifest.json carries the stamped version, then to the newest, and the tie is
reported. Both are read from the object store: the tool runs no Git command
that writes, in the seed or anywhere else.

Usage:
  graft-ledger.py <plant-root> <seed-root>          the base, then the table
  graft-ledger.py <plant-root> <seed-root> --base   the base only
The seed root must be a Git work tree (the base lives in its history).
Exit 0 when the table (or the base) was printed; 1 when the plant has no
docs/graph/, the seed root is not a seed checkout (protocols/ and
manifest.json), or no base could be found;
2 on a malformed command line. It writes nothing. Dependency-free.
"""
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# graft-audit.py owns the plant-to-seed path map and loads the shared walk;
# neither is a package to import from, so both come from beside this file.
import importlib.util as _ilu
sys.dont_write_bytecode = True  # "it writes nothing" covers a __pycache__ too
_ga_spec = _ilu.spec_from_file_location(
    "cypress_graft_audit", Path(__file__).resolve().parent / "graft-audit.py")
graft_audit = _ilu.module_from_spec(_ga_spec)
_ga_spec.loader.exec_module(graft_audit)
plant_walk = graft_audit.plant_walk

GRAPH_HOME = graft_audit.GRAPH_HOME
STAMP_REL = plant_walk.STAMP_REL
CLASSES = ("CURRENT", "FAST-FORWARD", "KEEP-PLANT", "SEED-NEW", "HARVESTED", "MERGE")
KERNEL_FILES = ("CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md")
# install.sh place_graph_machinery (and place_legal_corpus): the seed trees
# placed under docs/graph/, as (seed subtree, plant subtree, name glob)
SEED_TREES = (
    ("protocols", "protocols", "*.md"),
    ("core/method", "method", "*.md"),
    ("agents", "agents", "*.md"),
    ("templates", "templates", "*"),
)
LEGAL_TREE = ("legal-corpus", "legal/corpus", "*")
LEGAL_TOOL = "legal-lint.py"


def parse_args(argv):
    pos, base_only = [], False
    for a in argv:
        if a in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        if a == "--base":
            base_only = True
        elif a.startswith("-"):
            print(f"  !! unknown option {a}")
            sys.exit(2)
        else:
            pos.append(a)
    if len(pos) != 2:
        print("  !! want <plant-root> <seed-root> [--base]")
        sys.exit(2)
    return Path(pos[0]), Path(pos[1]), base_only


def git(seed: Path, *args, text=True):
    """A read-only Git query against the seed checkout, or None when it fails."""
    try:
        r = subprocess.run(["git", "-C", str(seed), *args], capture_output=True, text=text)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


class Blobs:
    """Git object ids for bytes on disk, and the tree of any seed commit. Every
    comparison is by object id, so a commit's files are never checked out."""

    def __init__(self, seed: Path):
        self.seed = seed
        fmt = (git(seed, "rev-parse", "--show-object-format") or "sha1").strip()
        self.algo = fmt if fmt in ("sha1", "sha256") else "sha1"
        self._trees = {}

    def of_file(self, path: Path):
        try:
            data = path.read_bytes()
        except OSError:
            return None
        return hashlib.new(self.algo, b"blob %d\0" % len(data) + data).hexdigest()

    def tree(self, commit: str) -> dict:
        if commit not in self._trees:
            out = git(self.seed, "ls-tree", "-r", "-z", "--full-tree", commit) or ""
            t = {}
            for entry in out.split("\0"):
                meta, tab, path = entry.partition("\t")
                parts = meta.split()
                if tab and len(parts) == 3 and parts[1] == "blob":
                    t[path] = parts[2]
            self._trees[commit] = t
        return self._trees[commit]

    def text(self, oid: str) -> str:
        out = git(self.seed, "cat-file", "blob", oid, text=False)
        return out.decode(errors="replace") if out is not None else ""


def read_stamp(plant: Path) -> dict:
    try:
        data = json.loads((plant / STAMP_REL).read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def inside_plant(plant: Path, rel: str) -> bool:
    """True when no directory on the way to `rel` is foreign (plant_walk's rule)."""
    d = plant
    for part in Path(rel).parent.parts:
        d = d / part
        if plant_walk.is_foreign(d):
            return False
    return True


def machinery(plant: Path, seed: Path, stamp: dict) -> dict:
    """{plant path: seed path}, both relative, for every seed-owned machinery
    file the seed carries now. The seed side is what the installer places; the
    plant side is walked, and mapped back through graft-audit's map."""
    legal = stamp.get("legal_corpus") == "yes"
    pairs = {}
    for src, dst, pattern in SEED_TREES + ((LEGAL_TREE,) if legal else ()):
        top = seed / src
        for f in sorted(p for p in top.rglob(pattern) if p.is_file()) if top.is_dir() else ():
            rest = f.relative_to(top).as_posix()
            # install.sh place_tree never ships bytecode; neither is a backup seed content
            if not (graft_audit.BAK_STAMP.search(rest) or f.suffix == ".pyc"
                    or "__pycache__" in f.parts):
                pairs[f"{GRAPH_HOME}/{dst}/{rest}"] = f"{src}/{rest}"
    golden = "agents/_routes.golden.tsv"
    if (seed / golden).is_file():
        pairs[f"{GRAPH_HOME}/{golden}"] = golden
    for skill in sorted((seed / "skills").glob("*/SKILL.md")):
        pairs[f"{GRAPH_HOME}/skills/{skill.parent.name}.md"] = skill.relative_to(seed).as_posix()
    tools = dict(graft_audit.DELIVERED_TOOLS)
    if not legal:
        tools.pop(LEGAL_TOOL, None)
    tools.update({e: f"templates/knowledge-graph/{e}" for e in graft_audit.ENGINE_FILES})
    for name, src in tools.items():
        if (seed / src).is_file():
            pairs[f"{GRAPH_HOME}/{name}"] = src
    # the plant side: what it carries under docs/graph/, this plant's only
    for f in plant_walk.files(plant, GRAPH_HOME):
        rel = f.relative_to(plant).as_posix()
        if rel in pairs or graft_audit.BAK_STAMP.search(f.name):
            continue
        if not graft_audit.is_seed_owned_graph_path(rel):
            continue
        src = graft_audit.seed_source_for(rel, seed)
        if src is not None and src.is_file():
            pairs[rel] = src.relative_to(seed).as_posix()
    # the kernel and the adapter files: placed per harness, so only the ones
    # the plant carries (a harness it did not choose is not SEED-NEW)
    for rel in KERNEL_FILES + tuple(graft_audit.ADAPTER_MACHINERY):
        if (plant / rel).is_file() and inside_plant(plant, rel):
            src = graft_audit.seed_source_for(rel, seed)
            if src is not None and src.is_file():
                pairs[rel] = src.relative_to(seed).as_posix()
    return pairs


def find_tag(seed: Path, version: str):
    for tag in (f"v{version}", version):
        oid = git(seed, "rev-parse", "--verify", "--quiet", "--end-of-options",
                  f"refs/tags/{tag}^{{commit}}")
        if oid:
            return tag, oid.strip()
    return None


def manifest_version(blobs: Blobs, commit: str) -> str:
    oid = blobs.tree(commit).get("manifest.json")
    try:
        return str(json.loads(blobs.text(oid)).get("version", "")) if oid else ""
    except (ValueError, AttributeError):
        return ""


def infer_base(plant: Path, pairs: dict, blobs: Blobs, version: str):
    """(commit, matched, of, tied, by_manifest) for the seed commit at which the most plant
    machinery files are byte-equal to the seed's version, or None."""
    here = {s: blobs.of_file(plant / p) for p, s in pairs.items() if (plant / p).is_file()}
    commits = (git(blobs.seed, "rev-list", "HEAD") or "").split()
    scored = []
    for c in commits:  # newest first
        tree = blobs.tree(c)
        scored.append((sum(1 for s, oid in here.items() if tree.get(s) == oid), c))
    best = max((n for n, _ in scored), default=0)
    if best == 0:
        return None
    tied = [c for n, c in scored if n == best]
    stamped = [c for c in tied if version and manifest_version(blobs, c) == version]
    return (stamped or tied)[0], best, len(here), len(tied), bool(stamped)


def classify(plant_oid, seed_oid, base_oid, texts) -> str:
    """The first class whose condition holds (the table in the header)."""
    if plant_oid == seed_oid:
        return "CURRENT"
    # an equality holds between two files that exist: a file the plant and
    # the base both lack is the SEED-NEW case below, not a fast-forward
    if plant_oid is not None and plant_oid == base_oid:
        return "FAST-FORWARD"
    if seed_oid == base_oid:
        return "KEEP-PLANT"
    if base_oid is None and plant_oid is None:
        return "SEED-NEW"
    base_lines, plant_lines, seed_lines = (t().splitlines() for t in texts)
    added, removed = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, base_lines, plant_lines, autojunk=False).get_opcodes():
        if tag in ("delete", "replace"):
            removed += base_lines[i1:i2]
        if tag in ("insert", "replace"):
            added += plant_lines[j1:j2]
    # a plant that added nothing (it only removed lines) has no addition the
    # seed could have carried back: that is a divergence, not a harvest. A plant
    # that removed a line the seed still carries has diverged too, whatever it
    # added: adopting the seed would put the line back
    seed_set = set(seed_lines)
    if (added and all(l in seed_set for l in added)
            and not any(l in seed_set for l in removed)):
        return "HARVESTED"
    return "MERGE"


def main() -> int:
    plant, seed, base_only = parse_args(sys.argv[1:])
    if not (plant / GRAPH_HOME).is_dir():
        print(f"  !! {plant} has no {GRAPH_HOME}/: not a plant root")
        return 1
    if not ((seed / "protocols").is_dir() and (seed / "manifest.json").is_file()):
        print(f"  !! {seed} has no protocols/ and manifest.json: not a seed checkout")
        return 1
    if git(seed, "rev-parse", "--verify", "--quiet", "HEAD") is None:
        print(f"  !! {seed} is not a Git work tree with a commit; the base lives "
              f"in its history")
        return 1
    stamp = read_stamp(plant)
    version = str(stamp.get("version") or "")
    blobs = Blobs(seed)
    pairs = machinery(plant, seed, stamp)

    tagged = find_tag(seed, version) if version else None
    if tagged:
        base = tagged[1]
        print(f"base: {tagged[0]} (from the tag of the stamped version {version})")
    else:
        why = (f"the stamped version {version} has no tag" if version
               else f"the plant has no stamped version in {STAMP_REL}")
        found = infer_base(plant, pairs, blobs, version)
        if found is None:
            print(f"  !! base: not found ({why}, and no seed commit matches any "
                  f"plant machinery file byte for byte)")
            return 1
        base, matched, of, tied, by_manifest = found
        print(f"base: {base} (inferred by content lineage; {why})")
        print(f"matched: {matched} of {of} plant machinery files are byte-equal "
              f"to the seed at that commit")
        if tied > 1:
            how = ("the newest whose manifest.json carries the stamped version"
                   if by_manifest else "the newest")
            print(f"note: {tied} commits tie at that count; the one shown is {how}")
    if base_only:
        return 0

    tree = blobs.tree(base)
    counts = dict.fromkeys(CLASSES, 0)
    rows = []
    for rel, src in sorted(pairs.items()):
        pf, sf = plant / rel, seed / src
        p_oid = blobs.of_file(pf) if pf.is_file() else None
        s_oid, b_oid = blobs.of_file(sf), tree.get(src)
        texts = (lambda: blobs.text(b_oid) if b_oid else "",
                 lambda: pf.read_text(errors="replace") if p_oid else "",
                 lambda: sf.read_text(errors="replace"))
        cls = classify(p_oid, s_oid, b_oid, texts)
        counts[cls] += 1
        rows.append(f"  {cls:<12}  {rel}  <- {src}")
    print(f"ledger: {len(rows)} seed-owned machinery file(s)")
    for r in rows:
        print(r)
    print("totals: " + ", ".join(f"{c} {n}" for c, n in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
