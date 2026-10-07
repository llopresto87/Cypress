#!/usr/bin/env bash
# SPEC-0003 code anchor: tools/code-anchor.py (X152-X160, X176).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() { echo "FAIL: $*" >&2; exit 1; }

FO="$(mktemp -d)"
trap 'rm -rf "$FO"' EXIT

# `docs/graph/code-anchor.py` records the branch, commit and uncommitted work of
# every governed repository at canonize (`--record`, into `.cypress/anchor.json`)
# and compares it once per session (`--compare`). One case per contract of
# SPEC-0003 §4 "Code anchor" and per tested failure of §7, each against Git
# repositories built here from synthetic files. The seed's `tools/code-anchor.py`
# is copied to where the installer places it, `<plant>/docs/graph/`, and run
# from the plant root as the contract says. Git runs with a HOME of its own, so
# no user or system configuration reaches a fixture. Every case runs; the block
# fails if any did. `ANCHOR_ONLY=X152,X159` runs a subset.
ANCHOR_RC=0
mkdir -p "$FO/anchor"
python3 - "$ROOT" "$FO/anchor" <<'PY' || ANCHOR_RC=1
import hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile, time, traceback
from pathlib import Path

SEED = Path(sys.argv[1])
WORK = Path(sys.argv[2])
TOOL = SEED / "tools" / "code-anchor.py"
READER = SEED / "templates" / "knowledge-graph" / "frontmatter.py"
HELPER = SEED / "tools" / "source_paths.py"
ONLY = {s.strip() for s in os.environ.get("ANCHOR_ONLY", "").split(",") if s.strip()}
os.umask(0o022)

# §6 constants and texts, used by value; tools/code-anchor.py is their one home.
ANCHOR_QUIET_MAX_BYTES = 160
ANCHOR_MAX_PATHS = 20
ANCHOR_MAX_BYTES = 2048
QUIET = ("Code anchor: no code changed since the last canonize (repositories: {n}). "
         "The graph's facts about code are current.")
MOVED_HEADER = ("Code anchor: code changed since the last canonize. Facts about the paths "
                "below may be stale; check them against the code. Every other fact stands "
                "as the graph states it.")
MORE_RE = re.compile(r"^- and (\d+) more path\(s\): python3 docs/graph/code-anchor\.py --compare --all$")
NOT_RECORDED_RE = re.compile(r"^Code anchor: not recorded \((.+)\)\. Facts about code in the graph are "
                             r"unverified until the next canonize records one; settled facts stay settled\.$")
HOME = WORK / "home"
HOME.mkdir(exist_ok=True)
EMPTY_PATH = WORK / "empty-path"
EMPTY_PATH.mkdir(exist_ok=True)
ENV = {k: v for k, v in os.environ.items()
       if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
ENV.update(HOME=str(HOME), XDG_CONFIG_HOME=str(HOME / ".config"), GIT_CONFIG_NOSYSTEM="1",
           GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
WRAPPER = WORK / "replace-fault.py"
WRAPPER.write_text(r"""
import errno, os, runpy, sys
def _refuse(*a, **k):
    raise OSError(errno.EIO, "injected by the code-anchor fault wrapper")
os.replace = _refuse
os.rename = _refuse
tool = sys.argv[1]
sys.argv = [tool] + sys.argv[2:]
runpy.run_path(tool, run_name="__main__")
""")


class CaseFail(Exception):
    pass


class HarnessFail(Exception):
    pass


def check(cond, msg):
    if not cond:
        raise CaseFail(msg)


# The fixture's own Git calls start no background maintenance or gc, whose
# lock could land under the plant while X159 snapshots it. ENV stays as it is:
# the tool runs under ENV, so X159 still sees any write the tool itself causes.
FIXTURE_GIT = ("-c", "maintenance.auto=false", "-c", "gc.auto=0")


def git(cwd, *args):
    r = subprocess.run(["git", *FIXTURE_GIT, *args], cwd=str(cwd), capture_output=True, text=True, timeout=30,
                       env=ENV)
    if r.returncode != 0:
        raise HarnessFail(f"git {' '.join(args)} in {cwd}: exit {r.returncode}: {r.stderr.strip()}")
    return r.stdout


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def init_repo(d, branch):
    d.mkdir(parents=True, exist_ok=True)
    git(d, "init", "-q")
    git(d, "symbolic-ref", "HEAD", f"refs/heads/{branch}")


def node(nid, repo=None):
    return (f"---\nid: {nid}\ntier: 2\nkind: subsystem\ntitle: {nid} node\nowns: [{nid}.core]\n"
            f"requires: [root]\n" + (f"repo: {repo}\n" if repo else "")
            + "load_when: [\"widgets\"]\nest_tokens: 100\n---\n# node\n")


class Plant:
    """A plant that is a Git work tree on `main` with one commit: synthetic code
    under `src/`, a graph under `docs/graph/` holding the copied tool, and a
    committed `.cypress/seed.json`. With `nested`, `vendor/lib` is a second work
    tree on `trunk` (ignored by the plant's own repository) that one node names
    in `repo:`, and another node names a `repo:` that resolves to nothing."""

    def __init__(self, base, name="plant", nested=False, cypress=True):
        self.dir = base / name
        init_repo(self.dir, "main")
        write(self.dir, "src/a.py", "A = 1\n")
        write(self.dir, "src/b.py", "B = 1\n")
        write(self.dir, "README.md", "# a synthetic plant\n")
        write(self.dir, "docs/graph/nodes/x.md", node("subsystem.x"))
        write(self.dir, "docs/graph/nodes/root.md", node("root").replace("requires: [root]\n", "requires: []\n"))
        if cypress:
            write(self.dir, ".cypress/seed.json", "{}\n")
        if nested:
            write(self.dir, ".gitignore", "/vendor/\n")
            write(self.dir, "docs/graph/nodes/subsystem.lib.md", node("subsystem.lib", repo="vendor/lib"))
            write(self.dir, "docs/graph/nodes/subsystem.gone.md", node("subsystem.gone", repo="vendor/gone"))
            lib = self.dir / "vendor" / "lib"
            init_repo(lib, "trunk")
            write(lib, "lib.py", "L = 1\n")
            git(lib, "add", "-A")
            git(lib, "commit", "-qm", "nested fixture")
        check(TOOL.is_file(), f"tools/code-anchor.py does not exist in the seed ({TOOL})")
        shutil.copy(TOOL, self.dir / "docs" / "graph" / "code-anchor.py")
        # install.sh places the canonical frontmatter reader beside the tool.
        check(READER.is_file(), f"the seed's frontmatter reader does not exist ({READER})")
        shutil.copy(READER, self.dir / "docs" / "graph" / "frontmatter.py")
        # install.sh places the shared path helper beside the tool too.
        check(HELPER.is_file(), f"the seed's path helper does not exist ({HELPER})")
        shutil.copy(HELPER, self.dir / "docs" / "graph" / "source_paths.py")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "fixture")

    @property
    def anchor(self):
        return self.dir / ".cypress" / "anchor.json"

    def head(self, rel="."):
        return git(self.dir / rel, "rev-parse", "HEAD").strip()

    def blob(self, rel):
        return git(self.dir, "hash-object", rel).strip()

    def commit(self, *paths, msg="change"):
        git(self.dir, "add", "--", *paths)
        git(self.dir, "commit", "-qm", msg)


class Run:
    def __init__(self, rc, out, err):
        self.rc, self.out, self.err = rc, out, err

    def lines(self):
        return self.out.rstrip("\n").split("\n") if self.out else []

    def ctx(self):
        return f"exit {self.rc}; stdout {self.out[:900]!r}; stderr {self.err[:600]!r}"


def tool(plant, *args, env=None, wrapper=False):
    cmd = [sys.executable, "docs/graph/code-anchor.py", *args]
    if wrapper:
        cmd = [sys.executable, str(WRAPPER), "docs/graph/code-anchor.py", *args]
    r = subprocess.run(cmd, cwd=str(plant.dir), capture_output=True, text=True, timeout=60,
                       env=env or ENV)
    return Run(r.returncode, r.stdout, r.stderr)


def record(plant):
    r = tool(plant, "--record")
    check(r.rc == 0, f"--record must exit 0 on a usable plant — {r.ctx()}")
    check(plant.anchor.is_file(), f"--record wrote no .cypress/anchor.json — {r.ctx()}")
    return r


def one_err_line(r):
    return r.err.count("\n") == 1 and r.err.endswith("\n")


def snapshot(root):
    snap = {}
    for dp, dns, fns in os.walk(root, followlinks=False):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for n in dns + fns:
            p = os.path.join(dp, n)
            rel = os.path.relpath(p, root)
            st = os.lstat(p)
            if stat.S_ISREG(st.st_mode):
                snap[rel] = ("f", stat.S_IMODE(st.st_mode), hashlib.sha256(Path(p).read_bytes()).hexdigest(),
                             st.st_mtime_ns)
            elif stat.S_ISLNK(st.st_mode):
                snap[rel] = ("l", os.readlink(p))
            else:
                snap[rel] = ("d", stat.S_IMODE(st.st_mode))
    return snap


def snap_diff(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def repo_lines(r):
    return [l for l in r.lines() if l.startswith("- ") and not MORE_RE.match(l)]


def named_paths(line):
    """The paths of a §6 repository line: everything after its last `: `."""
    return [p.strip() for p in line.rsplit(": ", 1)[-1].split(",") if p.strip()]


def anchor_doc(plant, commit=None, version=1, branch="main"):
    return {"version": version, "recorded_at": "2026-09-28T00:00:00Z",
            "repositories": [{"path": ".", "branch": branch, "commit": commit or plant.head(),
                              "dirty": {}, "dirty_overflow": False}]}


CASES = []


def case(label, slug):
    def deco(fn):
        CASES.append((label, slug, fn))
        return fn
    return deco


@case("X152", "ANCHOR_RECORD_NAMES_EVERY_REPOSITORY")
def x152(base):
    p = Plant(base, nested=True)
    write(p.dir, "src/a.py", "A = 2  # uncommitted work\n")
    r = tool(p, "--record")
    check(r.rc == 0, f"--record must exit 0 — {r.ctx()}")
    check(p.anchor.is_file() and not p.anchor.is_symlink(), f"no regular .cypress/anchor.json — {r.ctx()}")
    repos = json.loads(p.anchor.read_text())["repositories"]
    by = {e.get("path"): e for e in repos}
    check(sorted(by) == [".", "vendor/lib"] and len(repos) == 2,
          f"expected one entry each for `.` and `vendor/lib` (and none for a repo: that resolves to "
          f"nothing), got paths {[e.get('path') for e in repos]}")
    root, lib = by["."], by["vendor/lib"]
    check(root["branch"] == "main" and root["commit"] == p.head(),
          f"`.`: branch/commit {root['branch']!r}/{root['commit']!r} != main/{p.head()}")
    check(lib["branch"] == "trunk" and lib["commit"] == p.head("vendor/lib"),
          f"`vendor/lib`: branch/commit {lib['branch']!r}/{lib['commit']!r} != trunk/{p.head('vendor/lib')}")
    code = {k: v for k, v in root["dirty"].items() if not k.startswith(("docs/graph/", ".cypress/"))}
    check(code == {"src/a.py": p.blob("src/a.py")},
          f"`.`: uncommitted code {code!r} != src/a.py with its blob hash {p.blob('src/a.py')}")
    check(lib["dirty"] == {} and root["dirty_overflow"] is False and lib["dirty_overflow"] is False,
          f"dirty/dirty_overflow wrong: {repos!r}")
    lines = r.lines()
    check(len(lines) == 1 and lines[0].startswith("Code anchor recorded "),
          f"stdout is not the one §6 record line — {r.ctx()}")
    for want in (f". main@{p.head()[:7]} (1 uncommitted)",
                 f"vendor/lib trunk@{p.head('vendor/lib')[:7]} (0 uncommitted)"):
        check(want in lines[0], f"the record line lacks {want!r} — {r.ctx()}")
    return "both governed repositories named, the uncommitted path hashed; one record line; exit 0"


@case("X153", "ANCHOR_QUIET_WHEN_NOTHING_MOVED")
def x153(base):
    p = Plant(base, nested=True)
    write(p.dir, "src/a.py", "A = 2  # uncommitted work\n")
    record(p)
    r = tool(p, "--compare")
    check(r.out.rstrip("\n") == QUIET.format(n=2) and len(r.lines()) == 1,
          f"expected exactly the quiet line for two repositories — {r.ctx()}")
    n = len(r.out.rstrip("\n").encode("utf-8"))
    check(n <= ANCHOR_QUIET_MAX_BYTES, f"the quiet line is {n} B, over ANCHOR_QUIET_MAX_BYTES")
    return f"nothing moved: exactly the quiet line ({n} B)"


@case("X154", "ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED")
def x154(base):
    p = Plant(base)
    record(p)
    old = p.head()
    write(p.dir, "src/a.py", "A = 3\n")
    write(p.dir, "docs/graph/nodes/x.md", node("subsystem.x") + "\nA graph edit.\n")
    p.commit("src/a.py", "docs/graph/nodes/x.md")
    new = p.head()
    r = tool(p, "--compare")
    lines = r.lines()
    check(lines[:1] == [MOVED_HEADER], f"the first line is not the moved header — {r.ctx()}")
    rl = repo_lines(r)
    check(len(rl) == 1, f"expected one repository line — {r.ctx()}")
    check(rl[0].startswith(f"- .: commit {old[:7]}..{new[:7]}: "),
          f"the repository line does not name `commit {old[:7]}..{new[:7]}` — {r.ctx()}")
    check(named_paths(rl[0]) == ["src/a.py"], f"the line names {named_paths(rl[0])}, not src/a.py alone")
    check(not any("docs/graph/nodes/x.md" in l for l in lines), f"a line names the graph file — {r.ctx()}")
    return "a new commit: the moved header, `commit old..new: src/a.py`, the graph edit unnamed"


@case("X155", "ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED")
def x155(base):
    p = Plant(base)
    record(p)
    git(p.dir, "checkout", "-q", "-b", "topic")
    write(p.dir, "src/b.py", "B = 2\n")
    p.commit("src/b.py")
    r = tool(p, "--compare")
    rl = repo_lines(r)
    check(any(l.startswith("- .: ") and "branch main -> topic" in l and "src/b.py" in named_paths(l)
              for l in rl),
          f"no repository line names `branch main -> topic` and src/b.py — {r.ctx()}")
    return "a checkout of `topic`: the line names `main -> topic` and src/b.py"


@case("X156", "ANCHOR_NAMES_NEW_UNCOMMITTED_WORK")
def x156(base):
    p = Plant(base, name="edited")
    write(p.dir, "src/a.py", "A = 2  # uncommitted at the anchor\n")
    record(p)
    write(p.dir, "src/a.py", "A = 3  # edited again since\n")
    write(p.dir, "src/c.py", "C = 1\n")
    r = tool(p, "--compare")
    rl = [l for l in repo_lines(r) if l.startswith("- .: uncommitted: ")]
    check(rl, f"no `- .: uncommitted: ` line — {r.ctx()}")
    got = named_paths(rl[0])
    check("src/a.py" in got and "src/c.py" in got, f"the uncommitted line names {got}, not src/a.py and src/c.py")
    q = Plant(base, name="committed")
    write(q.dir, "src/a.py", "A = 2  # uncommitted at the anchor\n")
    record(q)
    q.commit("src/a.py", msg="commit the anchored work unchanged")
    r2 = tool(q, "--compare")
    check("src/a.py" not in r2.out, f"src/a.py, committed unchanged since the anchor, is named — {r2.ctx()}")
    return "new work on src/a.py and a new src/c.py are named; the same content committed is not"


@case("X157", "ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION; failures ANCHOR_UNUSABLE, ANCHOR_COMMIT_UNREACHABLE")
def x157(base):
    problems, reasons = [], {}
    variants = ["no anchor", "not JSON", "unknown version", "commit not in this clone", "git absent from PATH"]
    for i, what in enumerate(variants):
        p = Plant(base, name=f"plant{i}")
        env = None
        if what == "not JSON":
            p.anchor.write_text("{not json")
        elif what == "unknown version":
            p.anchor.write_text(json.dumps(anchor_doc(p, version=2)))
        elif what == "commit not in this clone":
            p.anchor.write_text(json.dumps(anchor_doc(p, commit="deadbeef" * 5)))
        elif what == "git absent from PATH":
            p.anchor.write_text(json.dumps(anchor_doc(p)))
            env = dict(ENV, PATH=str(EMPTY_PATH))
        before = snapshot(p.dir)
        r = tool(p, "--compare", env=env)
        if r.rc != 0:
            problems.append(f"{what}: exit {r.rc}, not 0 — {r.ctx()}")
        if what == "commit not in this clone":
            if not any(l.startswith("- .: ") and "unverified" in l for l in r.lines()):
                problems.append(f"{what}: no `- .: ` line saying its code facts are unverified — {r.ctx()}")
        else:
            m = NOT_RECORDED_RE.match(r.out.rstrip("\n")) if len(r.lines()) == 1 else None
            if not m:
                problems.append(f"{what}: stdout is not the one not-recorded line of §6 — {r.ctx()}")
            else:
                reasons[what] = m.group(1)
        diff = snap_diff(before, snapshot(p.dir))
        if diff:
            problems.append(f"{what}: files were written: {diff}")
    if len(reasons) == 4 and len(set(reasons.values())) != 4:
        problems.append(f"the not-recorded reasons do not tell the four causes apart: {reasons}")
    check(not problems, " || ".join(problems))
    return "missing, not JSON, version 2, unreachable commit, no git: the not-recorded or unverified line, exit 0, nothing written"


@case("X158", "ANCHOR_OUTPUT_WITHIN_BUDGET")
def x158(base):
    p = Plant(base)
    record(p)
    names = [f"src/gen/f{i:03d}.py" for i in range(300)]
    for n in names:
        write(p.dir, n, f"G = {n!r}\n")
    p.commit("src/gen")
    r = tool(p, "--compare")
    size = len(r.out.encode("utf-8"))
    check(size <= ANCHOR_MAX_BYTES, f"--compare printed {size} B, over ANCHOR_MAX_BYTES — {r.ctx()}")
    shown = [n for n in names if n in r.out]
    check(len(shown) <= ANCHOR_MAX_PATHS, f"--compare names {len(shown)} paths, over ANCHOR_MAX_PATHS")
    m = MORE_RE.match(r.lines()[-1]) if r.lines() else None
    check(m, f"the output does not end with the more-paths line — {r.ctx()}")
    check(int(m.group(1)) + len(shown) == 300, f"{len(shown)} named plus {m.group(1)} more is not 300")
    a = tool(p, "--compare", "--all")
    missing = [n for n in names if n not in a.out]
    check(not missing, f"--compare --all leaves {len(missing)} of 300 paths unnamed, e.g. {missing[:3]}")
    return f"300 changed paths: {size} B, {len(shown)} named, the more-paths line; --all names all 300"


@case("X176", "ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE")
def x176(base):
    noise = ["src/__pycache__/a.cpython-312.pyc", "src/b.pyc", "src/c.py.bak",
             "src/d.py.bak-20261001-091322"]
    # one real path, then enough that the more-paths line shows and must count after the filter
    for label, real in (("one path", ["src/e.py"]),
                        ("over the cap", ["src/e.py"] + [f"src/f{i:02d}.py" for i in range(ANCHOR_MAX_PATHS)])):
        p = Plant(base, name=label.replace(" ", "-"))
        record(p)
        for n in noise + real:
            write(p.dir, n, f"# {n}\n")
        for args in (("--compare",), ("--compare", "--all")):
            r = tool(p, *args)
            what = f"{label}, {' '.join(args)}"
            check(r.rc == 0, f"{what}: exited {r.rc} — {r.ctx()}")
            named = [q for l in repo_lines(r) for q in named_paths(l)]
            check("src/e.py" in named, f"{what}: src/e.py is not named — {r.ctx()}")
            leaked = [n for n in noise if n in r.out]
            check(not leaked, f"{what}: build or backup noise is named: {leaked} — {r.ctx()}")
            more = [int(m.group(1)) for m in map(MORE_RE.match, r.lines()) if m]
            shown = [q for q in real if q in named]
            check(len(shown) + sum(more) == len(real),
                  f"{what}: {len(shown)} named plus more-paths {more} is not the {len(real)} real paths — {r.ctx()}")
            if "--all" in args:
                check(len(shown) == len(real) and not more, f"{what}: --all does not name every real path — {r.ctx()}")
    return "build and backup files beside real ones: only the real paths are named, and the more-paths count is theirs"


@case("X176", "ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE; the backup filter is the installer's suffixes only")
def x176_narrow(base):
    # Only `*.bak` and `*.bak-<digit>...` (the timestamped backup the installer
    # writes) are backups. A name that merely holds `.bak-` before other text,
    # and a directory named `*.bak`, are code a fact may describe.
    code = ["src/x.bak-config.yaml", "src/config.bak/settings.py"]
    noise = ["src/y.py.bak-20260928-163636"]
    p = Plant(base, name="narrow")
    record(p)
    for n in code + noise:
        write(p.dir, n, f"# {n}\n")
    problems = []
    for args in (("--compare",), ("--compare", "--all")):
        r = tool(p, *args)
        what = " ".join(args)
        if r.rc != 0:
            problems.append(f"{what}: exited {r.rc} — {r.ctx()}")
            continue
        named = [q for l in repo_lines(r) for q in named_paths(l)]
        missed = [n for n in code if n not in named]
        if missed:
            problems.append(f"{what}: code paths taken for backups and not named: {missed} — {r.ctx()}")
        leaked = [n for n in noise if n in r.out]
        if leaked:
            problems.append(f"{what}: an installer backup is named: {leaked} — {r.ctx()}")
    check(not problems, " || ".join(problems))
    return "x.bak-config.yaml and config.bak/ are named as code; y.py.bak-20260928-163636 is not"


@case("X159", "ANCHOR_COMPARE_WRITES_NOTHING")
def x159(base):
    problems = []
    states = ["quiet", "commit moved", "new uncommitted work", "no anchor", "not JSON"]
    for i, what in enumerate(states):
        p = Plant(base, name=f"plant{i}")
        if what != "no anchor":
            record(p)
        if what == "commit moved":
            write(p.dir, "src/a.py", "A = 3\n")
            p.commit("src/a.py")
        elif what == "new uncommitted work":
            write(p.dir, "src/c.py", "C = 1\n")
        elif what == "not JSON":
            p.anchor.write_text("{not json")
        # A stale stat cache: `git status` without --no-optional-locks would
        # rewrite the index here, which is the write this contract forbids.
        t = time.time() + 5
        os.utime(p.dir / "src" / "b.py", (t, t))
        index = (p.dir / ".git" / "index").read_bytes()
        before = snapshot(p.dir)
        r = tool(p, "--compare")
        if (p.dir / ".git" / "index").read_bytes() != index:
            problems.append(f"{what}: the Git index changed — {r.ctx()}")
        diff = snap_diff(before, snapshot(p.dir))
        if diff:
            problems.append(f"{what}: files under the plant root were created or modified: {diff[:6]}")
        if not r.out.strip():
            problems.append(f"{what}: --compare printed nothing — {r.ctx()}")
    check(not problems, " || ".join(problems))
    return "five plant states with a stale index: --compare writes no file and leaves the index byte-identical"


@case("X160", "ANCHOR_RECORD_REFUSES_A_SYMLINK")
def x160(base):
    problems = []
    p = Plant(base, name="linked")
    outside = base / "outside.json"
    outside.write_text('{"zq-sentinel-0160": "outside the plant"}\n')
    before = outside.read_bytes()
    p.anchor.symlink_to(outside)
    r = tool(p, "--record")
    if r.rc == 0:
        problems.append(f"symlinked anchor: --record exited 0 — {r.ctx()}")
    if not one_err_line(r):
        problems.append(f"symlinked anchor: stderr is not one line — {r.ctx()}")
    if outside.read_bytes() != before:
        problems.append("symlinked anchor: the file outside the plant changed")
    if not p.anchor.is_symlink() or os.readlink(p.anchor) != str(outside):
        problems.append("symlinked anchor: the link was not left as it was")
    q = Plant(base, name="no-cypress", cypress=False)
    r = tool(q, "--record")
    if r.rc == 0:
        problems.append(f"no .cypress/: --record exited 0 — {r.ctx()}")
    if not one_err_line(r):
        problems.append(f"no .cypress/: stderr is not one line — {r.ctx()}")
    if (q.dir / ".cypress").exists():
        problems.append("no .cypress/: --record created .cypress/")
    d = Plant(base, name="dir-anchor")             # X166: a directory at the anchor name
    d.anchor.mkdir()
    r = tool(d, "--record")
    if r.rc == 0 or not one_err_line(r) or "not a regular file" not in r.err:
        problems.append(f"directory at the anchor name: not refused as not a regular file — {r.ctx()}")
    if os.listdir(d.anchor):
        problems.append("directory at the anchor name: something was written into it")
    f = Plant(base, name="faulted")
    record(f)
    old = f.anchor.read_bytes()
    write(f.dir, "src/a.py", "A = 9  # new work before a record whose replace fails\n")
    r = tool(f, "--record", wrapper=True)
    if f.anchor.read_bytes() != old:
        problems.append(f"a record whose replace fails changed the anchor — {r.ctx()}")
    check(not problems, " || ".join(problems))
    return "a symlinked anchor, a missing .cypress/ and a directory are refused; a failed replace keeps the anchor"


failed = []
for label, slug, fn in CASES:
    if ONLY and label not in ONLY:
        continue
    base = Path(tempfile.mkdtemp(prefix=f"{label}-", dir=WORK))
    try:
        note = fn(base)
        print(f"  {label} {slug}: {note} \u2014 OK")
    except CaseFail as e:
        failed.append(label)
        print(f"FAIL: {label} {slug}: {e}", file=sys.stderr)
    except Exception:                               # noqa: BLE001 — a harness bug, said as one
        failed.append(label)
        print(f"HARNESS ERROR: {label} {slug}:\n{traceback.format_exc()}", file=sys.stderr)
if failed:
    print(f"SPEC-0003 code-anchor cases: FAIL — {len(failed)} case(s): {', '.join(failed)}", file=sys.stderr)
    sys.exit(1)
PY

[[ "$ANCHOR_RC" == 0 ]] || fail "SPEC-0003 code anchor: the case(s) named above failed"

echo "test-code-anchor: PASS"
