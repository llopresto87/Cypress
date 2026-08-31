#!/usr/bin/env python3
"""graft-audit: prove a graft's fast-forward buried no plant customization.

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

It also flags any backup over PLANT-AUTHORED docs/graph/ content (a knowledge
overwrite — should be none; knowledge is add-if-missing). The seed-owned graph
subtrees docs/graph/{protocols,skills,agents,method,templates}/ and the scaffold
(_schema.md, graph-lint.py, spec-lint.py) are machinery, expected to be
fast-forwarded; everything else under docs/graph/ is the plant's own. Given the
plant's graph-lint.py and the seed's, it also warns if the plant engine is
STALE (missing engine lines the seed has).

"Plant-signal" = the plant's own name/paths PLUS generic self-reference that a
customization uses without naming the plant ("this project's", "this program",
"our stack"). Pass the plant's known tokens with --tokens.

Usage:
  graft-audit.py <plant-root> <seed-root> [--date YYYYMMDD] [--tokens t1,t2,...]
                 [--engine <plant-graph-lint.py>:<seed-graph-lint.py>]
--date defaults to today's UTC date via the newest .bak stamp found.
Exit 0 if clean/only-DELTA; 1 if any CUSTOMIZED or docs overwrite (a gate hit).
Dependency-free.
"""
import re
import sys
from pathlib import Path

GENERIC_SIGNALS = ("this project's", "this program", "our stack", "our program",
                   "this plant", "our deploy", "in this program")


def parse_args():
    a = sys.argv[1:]
    pos = [x for x in a if not x.startswith("--")]
    opt = {}
    for x in a:
        if x.startswith("--date="):
            opt["date"] = x.split("=", 1)[1]
        elif x.startswith("--tokens="):
            opt["tokens"] = [t.strip().lower() for t in x.split("=", 1)[1].split(",") if t.strip()]
        elif x.startswith("--engine="):
            opt["engine"] = x.split("=", 1)[1]
    return pos, opt


# seed-owned machinery under the plant's docs/graph/ (6.0.0 layout): these
# subtrees + the scaffold files are the seed's to fast-forward; everything
# else under docs/graph/ is plant-authored knowledge.
MACHINERY_SUBTREES = ("protocols/", "skills/", "agents/", "method/", "templates/")
SCAFFOLD_FILES = ("_schema.md", "graph-lint.py", "spec-lint.py")


def plant_rel(bak: Path, plant: Path, date: str) -> str:
    rel = bak.relative_to(plant).as_posix()
    return re.sub(rf"\.bak-{date}-\d+$", "", rel)


def seed_source_for(rel: str, seed: Path):
    """Map a plant-relative machinery path to the seed source it installs from
    (6.0.0 layout: machinery home is docs/graph/, tool dirs hold projections)."""
    if rel in ("CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"):
        return seed / "core/AGENTS.md"
    if rel.startswith("docs/graph/"):
        sub = rel[len("docs/graph/"):]
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
        if sub in SCAFFOLD_FILES:
            return seed / "templates/knowledge-graph" / sub
        return None  # plant-authored graph content — never seed-mapped
    for adapter in (".claude/", ".codex/", ".opencode/"):
        if rel.startswith(adapter):
            sub = rel[len(adapter):]
            # harness projections of docs/graph/{agents,skills}/
            if sub.startswith("agents/"):
                return seed / "agents" / sub[len("agents/"):]
            if sub.startswith("skills/"):
                # projection keeps skills/<name>/SKILL.md shape
                return seed / "skills" / sub[len("skills/"):]
            return None
    return None


def is_seed_owned_graph_path(rel: str) -> bool:
    if not rel.startswith("docs/graph/"):
        return False
    sub = rel[len("docs/graph/"):]
    return sub.startswith(MACHINERY_SUBTREES) or sub in SCAFFOLD_FILES


def main() -> int:
    pos, opt = parse_args()
    if len(pos) < 2:
        print(__doc__)
        return 1
    plant, seed = Path(pos[0]), Path(pos[1])
    tokens = opt.get("tokens", []) + [t.lower() for t in GENERIC_SIGNALS]

    date = opt.get("date")
    if not date:
        stamps = sorted(re.findall(r"\.bak-(\d{8})-\d+",
                        " ".join(p.name for p in plant.rglob("*.bak-*"))))
        date = stamps[-1] if stamps else "00000000"

    baks = [p for p in plant.rglob(f"*.bak-{date}-*") if p.is_file() and not p.is_symlink()]
    counts = {"IDENTICAL": 0, "DELTA": 0, "CUSTOMIZED": 0, "UNMAPPED": 0}
    customized, knowledge_hits = [], []
    for b in baks:
        rel = plant_rel(b, plant, date)
        # a real knowledge overwrite is a backup over PLANT-AUTHORED docs/graph/
        # content — the seed-owned machinery subtrees and scaffold are the
        # graft's to fast-forward and are exempt
        if rel.startswith("docs/graph/") and not is_seed_owned_graph_path(rel):
            knowledge_hits.append(b.relative_to(plant).as_posix())
        src = seed_source_for(rel, seed)
        if not src or not src.exists():
            counts["UNMAPPED"] += 1
            continue
        bt, st = b.read_text(errors="replace"), src.read_text(errors="replace")
        if bt == st:
            counts["IDENTICAL"] += 1
        else:
            uniq = "\n".join(l[1:] for l in _diff_added(st, bt))
            low = uniq.lower()
            hit = [t for t in tokens if t in low]
            if hit:
                counts["CUSTOMIZED"] += 1
                customized.append((b.relative_to(plant).as_posix(), sorted(set(hit))[:4]))
            else:
                counts["DELTA"] += 1

    print(f"  backups audited: {len(baks)} -> {counts}")
    if opt.get("engine"):
        _engine_currency(opt["engine"])
    if knowledge_hits:
        print(f"  !! {len(knowledge_hits)} knowledge overwrite(s) under docs/graph/:")
        for k in knowledge_hits[:20]:
            print(f"       {k}")
    if customized:
        print(f"  !! {len(customized)} FF-overwritten plant customization(s) — RE-INTEGRATE or ratify:")
        for rel, hit in customized[:40]:
            print(f"       {rel}  [signal: {','.join(hit)}]")
        return 1
    if knowledge_hits:
        return 1
    print("  clean — no plant knowledge overwritten, no customization buried")
    return 0


def _diff_added(seed_text: str, bak_text: str):
    """Lines present in the backup but not the seed (a cheap set difference —
    enough to surface unique plant content for signal scanning)."""
    seed_lines = set(seed_text.splitlines())
    return ["+" + l for l in bak_text.splitlines() if l not in seed_lines and l.strip()]


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


def _engine_currency(spec: str):
    try:
        p, s = spec.split(":", 1)
        pl = _code_lines(Path(p).read_text())
        sl = _code_lines(Path(s).read_text())
        missing = sl - pl
        # ignore the PROJECT CONFIG assignments (legitimately plant-specific)
        missing = {m for m in missing if not re.match(r"^(ROOT_ID|KINDS|KIND_PREFIX|TEST_GLOBS)\s*=", m)}
        if missing:
            print(f"  !! graph engine STALE: {len(missing)} seed engine line(s) absent "
                  f"from the plant — reconcile with graft-graph-engine.py")
        else:
            print("  graph engine: current (no seed engine line missing from plant)")
    except Exception as e:
        print(f"  (engine check skipped: {e})")


if __name__ == "__main__":
    sys.exit(main())
