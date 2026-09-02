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
subtrees docs/graph/{protocols,skills,agents,method,templates}/ and the shared
scripts (graph-lint.py, spec-lint.py, agent-lint.py) are machinery, expected to
be fast-forwarded — but only where a seed source actually backs the path: a
plant-authored project skill under docs/graph/skills/ is plant knowledge.
_schema.md and index.md are project-instantiated and always the plant's own,
like everything else under docs/graph/. Given the
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
    """Accept --flag=value AND --flag value. The old =-only parser
    silently dropped a space-separated value into the positional list:
    `--tokens acme` audited with DEFAULT tokens and could print "clean"
    for a graft that buried a real customization — the exact false-pass
    this gate exists to prevent. Unknown extra positionals now fail
    loudly instead of being ignored."""
    a = sys.argv[1:]
    pos, opt, i = [], {}, 0
    def _set(key, raw):
        if key == "tokens":
            opt["tokens"] = [t.strip().lower() for t in raw.split(",") if t.strip()]
        else:
            opt[key] = raw
    while i < len(a):
        x = a[i]
        if x.startswith("--"):
            body = x[2:]
            key, eq, val = body.partition("=")
            if key not in ("date", "tokens", "engine"):
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
    return pos, opt


# seed-owned machinery under the plant's docs/graph/ (6.0.0 layout): these
# subtrees + the engine scripts are the seed's to fast-forward; everything
# else under docs/graph/ is plant-authored knowledge. _schema.md and
# index.md are deliberately NOT here: they are project-instantiated
# (graft.md — "copying the seed template would regress placeholders and
# wipe the authored router"), so a backup over them IS a knowledge
# overwrite worth alarming on.
MACHINERY_SUBTREES = ("protocols/", "skills/", "agents/", "method/", "templates/")
SCAFFOLD_FILES = ("graph-lint.py", "spec-lint.py", "agent-lint.py")


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
        if sub == "agent-lint.py":
            return seed / "integrations/claude-code/agent-lint.py"
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
        if sub in SCAFFOLD_FILES:
            return seed / "templates/knowledge-graph" / sub
        return None  # plant-authored graph content — never seed-mapped
    for adapter in (".claude/", ".codex/", ".opencode/", ".prime/agent/"):
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
    # A vacuous audit must not read as a clean one: a wrong plant root
    # finds zero backups and would otherwise print the same "clean" line
    # a real audit earns. A plant always has docs/graph/ — refuse anything
    # that does not.
    if not (plant / "docs" / "graph").is_dir():
        print(f"  !! {plant} has no docs/graph/ — not a plant root; "
              f"refusing a vacuous audit")
        return 1
    tokens = opt.get("tokens", []) + [t.lower() for t in GENERIC_SIGNALS]

    date = opt.get("date")
    if not date:
        stamps = sorted(re.findall(r"\.bak-(\d{8})-\d+",
                        " ".join(p.name for p in plant.rglob("*.bak-*"))))
        date = stamps[-1] if stamps else "00000000"

    baks = [p for p in plant.rglob(f"*.bak-{date}-*") if p.is_file() and not p.is_symlink()]
    counts = {"IDENTICAL": 0, "DELTA": 0, "CUSTOMIZED": 0, "UNMAPPED": 0}
    customized, knowledge_hits, unmapped = [], [], []
    for b in baks:
        rel = plant_rel(b, plant, date)
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
            counts["UNMAPPED"] += 1
            unmapped.append(b.relative_to(plant).as_posix())
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
    if unmapped:
        print(f"  !! {len(unmapped)} UNMAPPED backup(s) — no seed source; "
              f"inspect by hand:")
        for u in unmapped[:20]:
            print(f"       {u}")
    if not baks:
        # Idempotent installs make zero-backup grafts the NORMAL no-op
        # case — but only when no backups exist at all. Backups under
        # OTHER date stamps mean the requested date audited nothing
        # while the real fast-forward went unexamined: fail, do not
        # print the same "clean" verdict a real audit earns.
        other = sorted({m.group(1) for p in plant.rglob("*.bak-*")
                        for m in [re.search(r"\.bak-(\d{8})-\d+$", p.name)]
                        if m and m.group(1) != date})
        if other:
            print(f"  !! zero backups for date {date}, but backups exist "
                  f"for {', '.join(other)} — wrong --date? refusing a "
                  f"vacuous audit")
            return 1
        print("  note: zero backup files — nothing was overwritten; "
              "the audit had nothing to prove")
    _kernel_currency(plant, seed)
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


def _kernel_currency(plant: Path, seed: Path):
    """The kernel body is seed-owned machinery loaded on every session. A graft
    that only re-points the CLAUDE.md<->AGENTS.md symlink and leaves a STALE
    kernel body is a silent, high-impact miss (install.sh place_kernel once did
    exactly this, and left no .bak for the backup-scan to catch). Compare the
    plant's live kernel file(s) — resolving the shared symlink — against the
    seed's current core/AGENTS.md directly, independent of any backup."""
    sk = seed / "core/AGENTS.md"
    if not sk.exists():
        return
    seed_txt = sk.read_text(errors="replace")
    stale = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        f = plant / name
        if not f.exists():
            continue
        if f.read_text(errors="replace") != seed_txt:
            stale.append(name)
    if stale:
        print(f"  !! KERNEL STALE: {', '.join(stale)} differ(s) from the seed "
              f"core/AGENTS.md — the graft left the plant on an old kernel; "
              f"fast-forward the kernel body (re-run install / place_kernel)")
    else:
        print("  kernel: current (plant AGENTS.md/CLAUDE.md == seed core/AGENTS.md)")


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
