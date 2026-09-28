#!/usr/bin/env python3
"""graft-run: the mechanical half of a graft, run on a stage, in one command.

A graft's Phase 7 gate table has mechanical rows (a command decides) and
judgment rows (a named judge decides). The mechanical rows, and the steps that
feed them, were rebuilt by hand on every graft. This tool does them, so a
steward reads the result instead of working the procedure out again. It does
not replace the steward's ratification, and it runs no judgment gate.

WHAT IT DOES, IN ORDER

  1. copies the plant into <stage>/<plant name> (.git included; a symlink is
     copied as a link, never followed)
  2. graft-ledger.py on the copy, before anything is written: the base and the
     three-way table (ledger.txt)
  3. install.sh in the copy, once, for the adapters the stamp's `tools` names,
     with --symlink only when the plant's placed protocols are links already;
     the whole output is captured (install.log), because the re-created notice
     is printed once and stored nowhere else
  4. graft-graph-engine.py on the copy's three engines, each keeping its config
  5. graft-audit.py over this run's backups, with --tokens derived from the
     plant (its root directory's name, its own node ids, the stamp's `seed`
     value), the three --engine pairs, and --base when the stamped version has
     a tag; then --unfilled, which only reports
  6. growth-audit.py --plan on the copy, then its lint
  7. the copy's own graph-lint.py (and a representative --plan), agent-lint.py
     --lint and --eval, and status-register.py, where each is installed
  8. prints the gate table: one line per row of the Phase 7 table in
     protocols/graft.md, in its order, as the graft record's integrity-gate
     block gives it: `<gate id>: PASS / BLOCK / N-A — <evidence>`. A judgment
     row says `not run` and names its judge. A row this tool has no check for
     says BLOCK, never PASS.

Every tool's full output is kept under <stage>/graft-run-logs/.

WHAT IT NEVER DOES

It never writes inside the plant root: a stage inside the plant, or reached
through a symlink that lands inside it, is refused before anything is written,
and so is a stage that holds the plant or sits inside the seed. It runs no Git
command in the plant (the copy's status is read from the copy's own .git), and
the seed is only read. A symlink in the plant that resolves into the plant
itself would let a write in the copy land in the plant, so the run stops at
the copy when it finds one.

Usage:
  graft-run.py <plant-root> <seed-root> --stage <dir>
The stage must not exist yet, or be an empty directory. The plant must carry a
stamp (.cypress/seed.json) whose `tools` names the adapters to re-install.
Exit 0 when every mechanical gate is PASS or N-A; 1 when a gate BLOCKs or a
step could not run; 2 on a malformed command line or a refused stage.
Dependency-free.
"""
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

# graft-audit.py owns the machinery map and loads the shared walk; neither is
# a package to import from, so both come from beside this file.
import importlib.util as _ilu
sys.dont_write_bytecode = True  # nothing lands in the seed's tools/ either
_ga_spec = _ilu.spec_from_file_location(
    "cypress_graft_audit", Path(__file__).resolve().parent / "graft-audit.py")
graft_audit = _ilu.module_from_spec(_ga_spec)
_ga_spec.loader.exec_module(graft_audit)
plant_walk = graft_audit.plant_walk

GRAPH_HOME = graft_audit.GRAPH_HOME
STAMP_REL = plant_walk.STAMP_REL
ENGINE_FILES = graft_audit.ENGINE_FILES
LOGS = "graft-run-logs"
# the Phase 7 table's rows: | `graft.gate.<id>` | asserts | command | on failure | class |
GATE_ROW = re.compile(r"^\| `(graft\.gate\.[a-z-]+)` \|(.*)\| (hard|soft|detective|judgment) \|\s*$")
JUDGE = re.compile(r"Judge: ([^|]+?)\s*\|")
KERNEL_BACKUPS = ("CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md")
ADOPTED = f"{GRAPH_HOME}/plans/adopted-instructions.md"
PLAN_TASK = "graft the new seed onto this plant and run its integrity gates"


def parse_args(argv):
    pos, stage = [], None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        if a == "--stage":
            if i + 1 >= len(argv):
                print("  !! --stage needs a directory")
                sys.exit(2)
            stage, i = argv[i + 1], i + 2
            continue
        if a.startswith("--stage="):
            stage = a[len("--stage="):]
        elif a.startswith("-"):
            print(f"  !! unknown option {a}")
            sys.exit(2)
        else:
            pos.append(a)
        i += 1
    if len(pos) != 2 or not stage:
        print("  !! want <plant-root> <seed-root> --stage <dir>")
        sys.exit(2)
    return Path(pos[0]), Path(pos[1]), Path(stage)


def within(path: str, root: str) -> bool:
    """True when `path` is `root` or below it, by path components (a sibling
    whose name extends the root's is not below it)."""
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:  # different drives
        return False


def same_or_below(stage: str, root: str) -> bool:
    """`within` on resolved paths, and on file identity for every existing
    ancestor of the stage, so a case-insensitive or bind-mounted spelling of
    the root is caught as well."""
    if within(stage, root):
        return True
    p = Path(stage)
    for anc in (p, *p.parents):
        try:
            if anc.exists() and os.path.samefile(anc, root):
                return True
        except OSError:
            continue
    return False


def refuse_stage(plant: str, seed: str, stage: str):
    """The reason this stage is refused, or None. Paths are resolved."""
    if same_or_below(stage, plant):
        return f"the stage {stage} is inside the plant {plant}; a graft run never writes inside the plant root"
    if within(plant, stage):
        return f"the stage {stage} holds the plant {plant}; the stage must sit outside it"
    if same_or_below(stage, seed):
        return f"the stage {stage} is inside the seed {seed}; the seed is only read"
    if os.path.lexists(stage):
        if not os.path.isdir(stage) or os.listdir(stage):
            return f"the stage {stage} exists and is not an empty directory; name a new one"
    return None


def read_stamp(root: Path) -> dict:
    try:
        data = json.loads((root / STAMP_REL).read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def gate_rows(seed: Path):
    """[(gate id, class, judge)] from the seed's Phase 7 table, in its order."""
    rows = []
    try:
        lines = (seed / "protocols/graft.md").read_text().splitlines()
    except OSError:
        return rows
    for line in lines:
        m = GATE_ROW.match(line)
        if m:
            j = JUDGE.search(line)
            rows.append((m.group(1), m.group(3), j.group(1).strip() if j else "not named"))
    return rows


def copy_tree(src: Path, dst: Path):
    """The plant, byte for byte: links stay links, and anything that is not a
    regular file (a socket, a fifo) is skipped, because opening one blocks."""
    def copy(s, d):
        if stat.S_ISREG(os.lstat(s).st_mode):
            shutil.copy2(s, d)
    shutil.copytree(src, dst, symlinks=True, copy_function=copy)


def links_into(tree: Path, root: str) -> list:
    """Symlinks under `tree` whose target resolves inside `root`."""
    hits = []
    for d, dirs, files in os.walk(tree):
        for n in dirs + files:
            p = os.path.join(d, n)
            if os.path.islink(p) and within(os.path.realpath(p), root):
                hits.append(os.path.relpath(p, tree))
    return sorted(hits)


class Run:
    """The stage, its copy of the plant, and one log file per step."""

    def __init__(self, seed: Path, stage: Path, copy: Path):
        self.seed, self.stage, self.copy = seed, stage, copy
        self.logs = stage / LOGS
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_OPTIONAL_LOCKS="0",
                        GIT_CEILING_DIRECTORIES=str(stage))

    def sh(self, name: str, cmd, cwd=None):
        """Run `cmd`, keep its whole output in <logs>/<name>, return (rc, text)."""
        try:
            r = subprocess.run([str(c) for c in cmd], cwd=str(cwd or self.copy), env=self.env,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
            rc, out = r.returncode, r.stdout.decode(errors="replace")
        except OSError as e:
            rc, out = 127, f"could not run {cmd[0]}: {e}\n"
        with open(self.logs / name, "a") as f:
            f.write(f"$ {' '.join(str(c) for c in cmd)}\n{out}(exit {rc})\n\n")
        return rc, out

    def tool(self, name: str, script: str, *args):
        return self.sh(name, [sys.executable, self.seed / "tools" / script, *args])

    def git(self, *args):
        """A Git query in the COPY, through its own .git directory only."""
        gd = self.copy / ".git"
        if not gd.is_dir() or gd.is_symlink():
            return None
        try:
            r = subprocess.run(["git", f"--git-dir={gd}", f"--work-tree={self.copy}", *args],
                               cwd=str(self.copy), env=self.env, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True)
        except OSError:
            return None
        return r.stdout if r.returncode == 0 else None


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def bak_stamps(root: Path) -> dict:
    """{backup path: its stamp} for this plant's backups (plant_walk's edge)."""
    return {rel(p, root): graft_audit.bak_stamp(p) for p in plant_walk.files(root, pattern="*.bak-*")}


def common_prefix(stamps) -> str:
    s = sorted(stamps)
    a, b = s[0], s[-1]
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return a[:n]


def node_ids(root: Path, pattern="*.md"):
    ids = set()
    for f in root.rglob(pattern) if root.is_dir() else ():
        v = graft_audit._fm_value(graft_audit._frontmatter(f), "id")
        if v:
            ids.add(v)
    return ids


def derive_tokens(copy: Path, seed: Path, stamp: dict) -> list:
    """The plant's own vocabulary: its root directory's name, the ids of the
    nodes it authored (a seed-shipped id, scaffold or machinery, is the seed's
    word and not the plant's), and the stamp's `seed` value."""
    seed_ids = set()
    for sub in ("templates", "protocols", "core", "agents", "skills"):
        seed_ids |= node_ids(seed / sub)
    own = set()
    for f in plant_walk.files(copy, GRAPH_HOME, "*.md"):
        r = rel(f, copy)
        if graft_audit.is_seed_owned_graph_path(r) or graft_audit.BAK_STAMP.search(f.name):
            continue
        v = graft_audit._fm_value(graft_audit._frontmatter(f), "id")
        if v and v not in seed_ids and re.fullmatch(r"[\w.-]+", v):
            own.add(v)
    toks = [copy.name] + sorted(own)
    if str(stamp.get("seed") or "").strip():
        toks.append(str(stamp["seed"]).strip())
    out = []
    for t in toks:
        if t and "," not in t and t not in out:
            out.append(t)
    return out


def is_machinery(r: str, seed: Path) -> bool:
    """A path a graft's installer, engine tool or coverage plan may change: the
    installer's state, a mapped seed source, a generated view, a projection of
    a plant node, the instruction ledger (its own gate). index.md is not here:
    the rootstock row reads its diff by name."""
    if r.startswith(".cypress/") or r == ADOPTED:
        return True
    if graft_audit.is_seed_owned_graph_path(r):
        return True
    if graft_audit.seed_source_for(r, seed) is not None or graft_audit.generator_for(r, seed) is not None:
        return True
    if r in graft_audit.GENERATED_FILES or r.startswith(graft_audit.GENERATED_VIEWS):
        return True
    return graft_audit.projected_sub(r) is not None


def porcelain(run: Run):
    """{path: (status, content hash)} of the copy's tracked changes, or None
    when the copy is not a Git work tree of its own."""
    out = run.git("status", "--porcelain", "-z", "--untracked-files=no")
    if out is None:
        return None
    entries, parts, i = {}, out.split("\0"), 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":
            i += 1  # the rename's source follows
        f = run.copy / path
        try:
            h = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
        except OSError:
            h = None
        entries[path] = (code, h)
    return entries


def line_of(text: str, pattern: str) -> str:
    for l in text.splitlines():
        if re.search(pattern, l):
            return l.strip()
    return ""


def main() -> int:
    plant_arg, seed_arg, stage_arg = parse_args(sys.argv[1:])
    plant, seed = Path(os.path.realpath(plant_arg)), Path(os.path.realpath(seed_arg))
    stage = Path(os.path.realpath(stage_arg))
    if not plant.is_dir():
        print(f"  !! {plant_arg} is not a directory: not a plant root")
        return 2
    if not ((seed / "install.sh").is_file() and (seed / "manifest.json").is_file()
            and (seed / "protocols/graft.md").is_file()):
        print(f"  !! {seed_arg} has no install.sh, manifest.json and protocols/graft.md: not a seed checkout")
        return 2
    if plant == seed:
        print(f"  !! the plant and the seed are the same directory ({plant}); refusing")
        return 2
    why = refuse_stage(str(plant), str(seed), str(stage))
    if why:
        print(f"  !! refused: {why}")
        return 2
    stamp = read_stamp(plant)
    adapters = str(stamp.get("tools") or "").split()
    if not adapters:
        print(f"  !! the plant's {STAMP_REL} names no adapters under `tools`, so there is no "
              f"install to repeat; establish the base by hand (protocols/graft.md, Phase 1)")
        return 1
    gates = gate_rows(seed)
    if not gates:
        print("  !! no gate rows found in the seed's protocols/graft.md Phase 7 table")
        return 1

    # 1. the stage and its copy; nothing below this line reads the plant again
    copy = stage / (plant.name if plant.name != LOGS else plant.name + "-plant")
    stage.mkdir(parents=True, exist_ok=True)
    run = Run(seed, stage, copy)
    run.logs.mkdir()
    copy_tree(plant, copy)
    print(f"graft-run: plant {plant}")
    print(f"graft-run: seed {seed}")
    print(f"graft-run: stage copy {copy} (logs in {run.logs})")
    escaping = links_into(copy, str(plant))
    if escaping:
        print(f"  !! {len(escaping)} symlink(s) in the plant resolve into the plant itself, so a "
              f"write in the copy would land in the plant; stopped before any write:")
        for e in escaping[:20]:
            print(f"       {e}")
        return 1

    before = porcelain(run)
    stamps_before = bak_stamps(copy)
    agents_dir = copy / GRAPH_HOME / "agents"
    agents_before = {p.name for p in agents_dir.glob("*.md")} if agents_dir.is_dir() else set()
    prior_install = (copy / STAMP_REL).is_file()
    tokens = derive_tokens(copy, seed, stamp)

    # 2. the ledger, before the installer writes
    rc, out = run.tool("ledger.txt", "graft-ledger.py", copy, seed)
    base_line = line_of(out, r"^base: ")
    base_rev = base_line.split()[1] if base_line and "!!" not in base_line else ""
    base_tag = base_rev if "from the tag" in base_line else ""
    print(f"ledger: {line_of(out, r'^totals: ') or f'not printed (exit {rc})'}; "
          f"{base_line or 'base: not found'}")

    # 3. the installer, once, for the adapters the plant carries
    protocols = copy / GRAPH_HOME / "protocols"
    symlinked = protocols.is_dir() and any(p.is_symlink() for p in protocols.iterdir())
    cmd = ["bash", seed / "install.sh", *adapters] + (["--symlink"] if symlinked else []) \
        + ["--project-dir", copy]
    install_rc, install_out = run.sh("install.log", cmd)
    print(f"install: install.sh {' '.join(adapters)}{' --symlink' if symlinked else ''} "
          f"exited {install_rc}")

    # 4. the three engines, each keeping its config
    engines = {}
    for e in ENGINE_FILES:
        pe = copy / GRAPH_HOME / e
        if pe.is_symlink() or not pe.is_file():
            engines[e] = "not reconciled: " + ("a symlink" if pe.is_symlink() else "absent")
            continue
        erc, eout = run.tool("engines.txt", "graft-graph-engine.py", pe,
                             seed / "templates/knowledge-graph" / e)
        engines[e] = f"exit {erc}: {eout.strip().splitlines()[-1] if eout.strip() else ''}"
    print("engines: " + "; ".join(f"{e} {v}" for e, v in engines.items()))

    # 5. the audit, over this run's backups only
    stamps_after = bak_stamps(copy)
    new = {p: s for p, s in stamps_after.items() if p not in stamps_before and s}
    date = common_prefix(new.values()) if new else ""
    shared = sorted(p for p, s in stamps_before.items() if date and s.startswith(date))
    pairs = [f"--engine={copy / GRAPH_HOME / e}:{seed / 'templates/knowledge-graph' / e}"
             for e in ENGINE_FILES]
    print(f"tokens: --tokens={','.join(tokens)}")
    if date:
        args = [copy, seed, f"--date={date}", f"--tokens={','.join(tokens)}", *pairs]
        if base_tag:
            args.append(f"--base={base_tag}")
        audit_rc, audit = run.tool("audit.txt", "graft-audit.py", *args)
        print(f"audit: --date={date}{' --base=' + base_tag if base_tag else ''} exited {audit_rc}")
    else:
        # nothing was replaced: the backup half has nothing to read, and a
        # named date that matches no backup is refused as vacuous, so the
        # currency checks run on their own
        buf = io.StringIO()
        with redirect_stdout(buf):
            ok = graft_audit._kernel_currency(copy, seed)
            ok = graft_audit._schema_currency(copy, seed) and ok
            ok = all([graft_audit._engine_currency(p[len("--engine="):]) for p in pairs]) and ok
        audit_rc, audit = (0 if ok else 1), "  backups audited: 0\n" + buf.getvalue()
        with open(run.logs / "audit.txt", "a") as f:
            f.write("(no backup written by this run: currency checks only)\n" + audit)
        print("audit: this run wrote no backup; currency checks only")
    unf_rc, unfilled = run.tool("unfilled.txt", "graft-audit.py", copy, seed, "--unfilled")

    # 6. coverage: refresh the plan, then hold the plant to it
    plan_rc, _ = run.tool("coverage.txt", "growth-audit.py", copy, seed, "--plan")
    cov_rc, coverage = run.tool("coverage.txt", "growth-audit.py", copy, seed)

    # 7. the copy's own linters, run from the copy's root
    routes = []
    g = copy / GRAPH_HOME
    if (g / "graph-lint.py").is_file():
        routes.append(("graph-lint", *run.sh("routes.txt", [sys.executable, g / "graph-lint.py"])))
        prc, pout = run.sh("routes.txt", [sys.executable, g / "graph-lint.py", "--plan", PLAN_TASK])
        routes.append(("--plan", prc if "LOAD" in pout else prc or 1, pout))
    if (g / "agent-lint.py").is_file():
        routes.append(("agent-lint --lint", *run.sh("routes.txt", [sys.executable, g / "agent-lint.py", "--lint"])))
        routes.append(("agent-lint --eval", *run.sh("routes.txt", [sys.executable, g / "agent-lint.py", "--eval"])))
    reg = None
    if (g / "status-register.py").is_file():
        reg = run.sh("status-register.txt", [sys.executable, g / "status-register.py", "--root", "docs/graph"])

    after = porcelain(run)
    evidence = {
        "stamp": read_stamp(copy), "prior_install": prior_install, "date": date, "new": new,
        "shared": shared, "tokens": tokens, "base_line": base_line, "base_rev": base_rev,
        "base_tag": base_tag, "audit": (audit_rc, audit), "unfilled": (unf_rc, unfilled),
        "coverage": (plan_rc, cov_rc, coverage), "routes": routes, "register": reg,
        "before": before, "after": after, "agents_before": agents_before,
        "install": (install_rc, install_out), "engines": engines,
    }
    table = []
    for gid, cls, judge in gates:
        if cls == "judgment":
            table.append((gid, "not run", f"a judgment gate; judge: {judge}"))
            continue
        if install_rc != 0:
            table.append((gid, "BLOCK", f"not checked: install.sh exited {install_rc} "
                                        f"({run.logs / 'install.log'})"))
            continue
        check = CHECKS.get(gid)
        verdict, why = check(run, evidence) if check else (
            "BLOCK", "graft-run has no check for this gate; run its Command by hand")
        table.append((gid, verdict, why))
    blocked = any(v == "BLOCK" for _, v, _ in table)
    print("")
    print("Integrity gate (Phase 7; mechanical rows run on the stage copy, judgment rows not run):")
    for gid, verdict, why in table:
        print(f"{gid}: {verdict} — {why}")
    return 1 if blocked else 0


# -- one check per mechanical row: (verdict, evidence) -------------------------

def counts_of(audit: str) -> dict:
    m = re.search(r"backups audited: (\d+)(?: -> (\{.*\}))?", audit)
    if not m:
        return {}
    c = {"audited": int(m.group(1))}
    for k, v in re.findall(r"'([A-Z-]+)': (\d+)", m.group(2) or ""):
        c[k] = int(v)
    return c


def check_backups(run, ev):
    if not ev["date"]:
        return "N-A", "this run replaced no file (no new .bak in the stage copy)"
    rc, audit = ev["audit"]
    c = counts_of(audit)
    shared = f"; {len(ev['shared'])} earlier backup(s) share the date prefix" if ev["shared"] else ""
    if not c or "refusing" in audit:
        return "BLOCK", f"graft-audit.py exited {rc} without a classification (audit.txt){shared}"
    if c.get("UNMAPPED", 0):
        return "BLOCK", f"{c['UNMAPPED']} UNMAPPED of {c['audited']} backup(s) for --date={ev['date']}{shared}"
    return "PASS", f"backups audited: {c['audited']} for --date={ev['date']}, 0 UNMAPPED{shared}"


def check_rootstock(run, ev):
    rc, audit = ev["audit"]
    hits = re.search(r"(\d+) knowledge overwrite", audit)
    n_hits = int(hits.group(1)) if hits else 0
    if ev["before"] is None or ev["after"] is None:
        return "BLOCK", (f"{n_hits} knowledge overwrite(s); the copy is not a Git work tree of its "
                         f"own, so the status half did not run")
    changed = sorted(p for p, v in ev["after"].items()
                     if ev["before"].get(p) != v and not is_machinery(p, run.seed))
    index = f"{GRAPH_HOME}/index.md"
    others = [p for p in changed if p != index]
    parts = [f"{n_hits} knowledge overwrite(s)",
             f"{len(others)} plant-authored tracked file(s) changed"
             + (f" ({', '.join(others[:5])})" if others else "")]
    if index in changed:
        parts.append(f"{index} changed (fill_plant_facts, no backup): read `git diff {index}` "
                     f"in the stage copy before ratifying")
    return ("BLOCK" if n_hits or changed else "PASS"), "; ".join(parts)


def check_customization(run, ev):
    toks = f"--tokens={','.join(ev['tokens'])}"
    if not ev["date"]:
        return "PASS", f"no backup to read: this run overwrote nothing ({toks})"
    rc, audit = ev["audit"]
    c = counts_of(audit)
    n = c.get("CUSTOMIZED", 0)
    base = f", --base={ev['base_tag']}" if ev["base_tag"] else ", no --base (the stamped version has no tag)"
    if not c:
        return "BLOCK", f"graft-audit.py exited {rc} without a classification ({toks}, --date={ev['date']})"
    return ("BLOCK" if n else "PASS"), f"CUSTOMIZED: {n} ({toks}, --date={ev['date']}{base})"


def check_kernel(run, ev):
    rc, audit = ev["audit"]
    line = line_of(audit, r"KERNEL (STALE|EXTENDED)|kernel: ")
    ok = bool(line) and "!!" not in line
    tools = str(ev["stamp"].get("tools") or "").split()
    if "github-copilot" in tools:
        cp = run.copy / ".github/copilot-instructions.md"
        same = cp.is_file() and cp.read_bytes() == (run.seed / "core/AGENTS.md").read_bytes()
        line += f"; .github/copilot-instructions.md {'==' if same else '!='} core/AGENTS.md"
        ok = ok and same
    return ("PASS" if ok else "BLOCK"), line or "no kernel line in the audit output"


def check_schema(run, ev):
    line = line_of(ev["audit"][1], r"node schema")
    return ("PASS" if line.startswith("node schema: current") else "BLOCK"), line or "no node-schema line"


def check_engine(run, ev):
    lines = [l.strip() for l in ev["audit"][1].splitlines() if "graph engine" in l]
    current = sum(1 for l in lines if l.startswith("graph engine: current"))
    ok = current == len(ENGINE_FILES) and len(lines) == len(ENGINE_FILES)
    why = f"{current} of {len(ENGINE_FILES)} engines current"
    stale = [l for l in lines if not l.startswith("graph engine: current")]
    if stale:
        why += "; " + stale[0]
    return ("PASS" if ok else "BLOCK"), why


def check_scaffolds(run, ev):
    rc, out = ev["unfilled"]
    line = line_of(out, r"unfilled scaffolds") or f"graft-audit.py --unfilled exited {rc}"
    return ("PASS" if rc == 0 else "BLOCK"), line


def check_coverage(run, ev):
    plan_rc, rc, out = ev["coverage"]
    tail = [l.strip() for l in out.strip().splitlines() if l.strip()]
    line = tail[-1] if tail else ""
    plan = "after --plan" if plan_rc == 0 else f"after --plan exited {plan_rc}"
    return ("PASS" if rc == 0 and plan_rc == 0 else "BLOCK"), f"growth-audit.py exited {rc} {plan}: {line}"


def check_routes(run, ev):
    if not ev["routes"]:
        return "BLOCK", "no docs/graph/graph-lint.py in the stage copy"
    parts, ok = [], True
    for name, rc, out in ev["routes"]:
        tail = [l.strip() for l in out.strip().splitlines() if l.strip()]
        verdicts = [l.strip() for l in out.splitlines()
                    if re.match(r"(graph-lint|agent-lint)( --\w+)?: (OK|FAIL|PASS|\d)", l.strip())]
        first = verdicts[-1] if verdicts else (tail[0] if tail else "")
        parts.append(f"{name} exit {rc}" + (f" ({first})" if first and name != "--plan" else ""))
        ok = ok and rc == 0
    return ("PASS" if ok else "BLOCK"), "; ".join(parts)


def check_status_register(run, ev):
    if ev["register"] is None:
        return "N-A", "no docs/graph/status-register.py in the stage copy"
    rc, out = ev["register"]
    return ("PASS" if rc == 0 else "BLOCK"), line_of(out, r"status register") or f"exit {rc}"


def check_prose(run, ev):
    return "N-A", ("this run authored no node; run prose-lint.py --file on each node "
                   "Phases 4-6 write")


def check_adopted(run, ev):
    date = ev["date"]
    baks = sorted(p for p in ev["new"] if p.split(".bak-")[0] in KERNEL_BACKUPS) if date else []
    note = run.copy / ADOPTED
    text = note.read_text(errors="replace") if note.is_file() else ""
    if not baks and not text:
        return "N-A", "no kernel backup and no instruction ledger: nothing to report"
    unmatched = [b for b in baks if b not in text]
    open_rows = len(re.findall(r"^- \[ \] ", text, re.M))
    why = (f"{len(baks)} kernel backup(s), {len(unmatched)} with no ledger row"
           + (f" ({', '.join(unmatched)})" if unmatched else "")
           + f"; {open_rows} unstruck row(s) for docs-librarian")
    return ("BLOCK" if unmatched else "PASS"), why


def check_recreated(run, ev):
    if not ev["prior_install"]:
        return "N-A", "the plant had no stamp, so the installer prints no re-created notice"
    f = run.copy / ".cypress/recreated-nodes.txt"
    if f.is_file():
        nodes = [l.strip() for l in f.read_text().splitlines() if l.strip() and not l.startswith("#")]
        src = ".cypress/recreated-nodes.txt"
    else:
        nodes = re.findall(r"^\[seed\]\s+(docs/graph/\S+)\s*$", ev["install"][1], re.M)
        src = "install.log"
    if not nodes:
        return "PASS", f"no node re-created ({src}; install.log kept)"
    return "BLOCK", (f"{len(nodes)} node(s) re-created ({', '.join(nodes[:5])}"
                     f"{' ...' if len(nodes) > 5 else ''}): re-apply the deletion or ratify each "
                     f"({src}; install.log kept)")


def check_roster(run, ev):
    agents_dir = run.copy / GRAPH_HOME / "agents"
    now = {p.name for p in agents_dir.glob("*.md")} if agents_dir.is_dir() else set()
    added = sorted(now - ev["agents_before"])
    if not ev["base_rev"]:
        return "BLOCK", (f"{len(added)} specialist(s) added ({', '.join(added)}); no base, so "
                         f"renames were not checked")
    ls = subprocess.run(["git", "-C", str(run.seed), "ls-tree", "--name-only", ev["base_rev"], "agents/"],
                        capture_output=True, text=True, env=run.env)
    if ls.returncode != 0:
        return "BLOCK", f"the base {ev['base_rev']}'s roster could not be read"
    base = {Path(p).name for p in ls.stdout.split() if p.endswith(".md")}
    seed_now = {p.name for p in (run.seed / "agents").glob("*.md")}
    gone = sorted(base - seed_now)
    why = (f"{len(added)} added ({', '.join(added) or 'none'}), {len(gone)} renamed or removed since "
           f"the base {ev['base_rev']} ({', '.join(gone) or 'none'})")
    if added or gone:
        why += ": hand them to the plant's next session (delegation.harness-registration); not verified spawnable"
    return "PASS", why


def check_stamp(run, ev):
    try:
        want = str(json.loads((run.seed / "manifest.json").read_text()).get("version", ""))
    except (OSError, ValueError):
        want = ""
    got = str(ev["stamp"].get("version") or "")
    stale = line_of(ev["coverage"][2], r"\bSTALE\b")
    ok = bool(got) and got == want and not stale
    return ("PASS" if ok else "BLOCK"), (f"stamp {got or 'absent'}, seed manifest.json {want or 'absent'}"
                                         + (f"; {stale}" if stale else "; growth-audit reports no STALE"))


def check_projection(run, ev):
    projections = ev["stamp"].get("agent_projections")
    if not isinstance(projections, list) or not projections:
        return "BLOCK", "the stamp lists no agent_projections, so there is nothing to compare"
    nodes = sorted((run.copy / GRAPH_HOME / "agents").glob("*.md"))
    drift, checked = [], []
    for pr in projections:
        if not isinstance(pr, dict):
            continue
        tool, path = str(pr.get("tool", "")), str(pr.get("path", ""))
        if pr.get("verbatim") is True and "{name}" in path:
            for n in nodes:
                view = run.copy / path.replace("{name}", n.stem)
                if not (view.is_file() and view.read_bytes() == n.read_bytes()):
                    drift.append(rel(view, run.copy))
            checked.append(f"{tool} ({len(nodes)} verbatim)")
        else:
            rc, _ = run.sh("projection-check.txt", ["bash", run.seed / "install.sh", tool,
                                                    "--check", "--project-dir", run.copy])
            checked.append(f"{tool} --check exit {rc}")
            if rc != 0:
                drift.append(f"{tool} views")
    why = "; ".join(checked) + (f"; {len(drift)} drifted ({', '.join(drift[:5])})" if drift else "; none drifted")
    return ("BLOCK" if drift else "PASS"), why


CHECKS = {
    "graft.gate.backups": check_backups,
    "graft.gate.rootstock": check_rootstock,
    "graft.gate.customization": check_customization,
    "graft.gate.kernel": check_kernel,
    "graft.gate.schema": check_schema,
    "graft.gate.engine": check_engine,
    "graft.gate.scaffolds": check_scaffolds,
    "graft.gate.coverage": check_coverage,
    "graft.gate.routes": check_routes,
    "graft.gate.status-register": check_status_register,
    "graft.gate.prose": check_prose,
    "graft.gate.adopted-instructions": check_adopted,
    "graft.gate.recreated-nodes": check_recreated,
    "graft.gate.roster-delta": check_roster,
    "graft.gate.stamp": check_stamp,
    "graft.gate.projection-drift": check_projection,
}


if __name__ == "__main__":
    sys.exit(main())
