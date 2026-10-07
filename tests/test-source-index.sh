#!/usr/bin/env bash
# SPEC-0007 source index: tools/source-index.py (X425-X449).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() { echo "FAIL: $*" >&2; exit 1; }

FO="$(mktemp -d)"
trap 'rm -rf "$FO"' EXIT

# `docs/graph/source-index.py` inventories a plant's code, links it, and walks
# those links in reverse to answer `impact`, `affected-tests` and `anchors`,
# keeping a derived cache under `.cypress/source-index/`. One case per contract
# of SPEC-0007 §4, with the §7 failures as arms of the case whose fixture sets
# them up (§10). Each case builds Git plants from synthetic files, copies the
# seed's tool and the siblings the installer places beside it into
# `<plant>/docs/graph/`, and runs it from the plant root. Git runs with a HOME
# of its own, so no user or system configuration reaches a fixture. Every case
# runs; the block fails if any did. `SOURCE_INDEX_ONLY=X425,X431` runs a subset.
SI_RC=0
mkdir -p "$FO/si"
python3 - "$ROOT" "$FO/si" <<'PY' || SI_RC=1
import hashlib, json, os, shutil, stat, subprocess, sys, tempfile, traceback
from pathlib import Path

SEED = Path(sys.argv[1])
WORK = Path(sys.argv[2])
TOOL = SEED / "tools" / "source-index.py"
# The files install.sh places beside the tool, each loaded by file path.
SIBLINGS = {"source_paths.py": SEED / "tools" / "source_paths.py",
            "plant_walk.py": SEED / "tools" / "plant_walk.py",
            "frontmatter.py": SEED / "templates" / "knowledge-graph" / "frontmatter.py"}
ONLY = {s.strip() for s in os.environ.get("SOURCE_INDEX_ONLY", "").split(",") if s.strip()}
os.umask(0o022)

# §6 constants and texts, used by value; tools/source-index.py is their one home.
INDEX_SCHEMA = "cypress.source-index/1"
ANSWER_SCHEMA = "cypress.source-index.answer/1"
FILE_MAX_BYTES = 1048576
DIR_LINK_MAX = 200
CACHE_IGNORE = b"*\n"
CONFIG_PATH = "docs/graph/source-index.json"
FLOOR_LINE = "Floor: {n} maybe row(s) every input reaches (opaque holders and their dependents):"
RECOMMEND_LINE = ("Recommendation only: the tests above and the always-run set, never only these; "
                  "verify decides what runs.")
ACTION = {"build": "Incomplete: check by hand (", "impact": "Incomplete: check by hand (",
          "affected-tests": "Incomplete: run the full suite (", "anchors": "Incomplete: review by hand ("}

HOME = WORK / "home"
HOME.mkdir(exist_ok=True)
# A PATH that holds python3 and no git (GIT_UNAVAILABLE).
NO_GIT_PATH = WORK / "no-git-path"
NO_GIT_PATH.mkdir(exist_ok=True)
if not (NO_GIT_PATH / "python3").exists():
    (NO_GIT_PATH / "python3").symlink_to(sys.executable)
ENV = {k: v for k, v in os.environ.items()
       if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
ENV.update(HOME=str(HOME), XDG_CONFIG_HOME=str(HOME / ".config"), GIT_CONFIG_NOSYSTEM="1",
           GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
FIXTURE_GIT = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", "-c", "core.quotepath=false")


class CaseFail(Exception):
    pass


class HarnessFail(Exception):
    pass


def check(cond, msg):
    if not cond:
        raise CaseFail(msg)


def git(cwd, *args):
    r = subprocess.run(["git", *FIXTURE_GIT, *args], cwd=str(cwd), capture_output=True, timeout=30, env=ENV)
    if r.returncode != 0:
        raise HarnessFail(f"git {' '.join(args)} in {cwd}: exit {r.returncode}: {r.stderr.decode(errors='replace')}")
    return r.stdout.decode("utf-8", "surrogateescape")


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text)
    return p


def node(nid, repo=None, body=""):
    return (f"---\nid: {nid}\ntier: 2\nkind: subsystem\ntitle: {nid} node\nowns: [{nid}.core]\n"
            f"requires: []\n" + (f"repo: {repo}\n" if repo else "")
            + "load_when: [\"widgets\"]\nest_tokens: 100\n---\n# node\n" + body)


def line_of(text, needle):
    """The 1-based line of the first line holding `needle` (a fixture fact)."""
    for i, l in enumerate(text.split("\n"), 1):
        if needle in l:
            return i
    raise HarnessFail(f"fixture: {needle!r} is on no line")


class Plant:
    """A Git work tree on `main`: the synthetic `files`, a `docs/graph/spec-lint.py`
    holding only `TEST_GLOBS` (`globs=None` leaves the engine out), a committed
    `.cypress/seed.json` unless `cypress=False`, and the seed's tool and its
    siblings copied into `docs/graph/`. `nested` maps a directory to the files
    of a second work tree there, which the root repository ignores and one node
    names in `repo:`. `git_init=False` leaves the plant no work tree at all."""

    def __init__(self, base, name="plant", files=None, globs=("tests/**/*.*",), cypress=True,
                 nested=None, config=None, commit=True, git_init=True):
        self.dir = Path(base) / name
        self.dir.mkdir(parents=True)
        if git_init:
            git(self.dir, "init", "-q")
            git(self.dir, "symbolic-ref", "HEAD", "refs/heads/main")
        ignore = ""
        for rel, text in (files or {}).items():
            write(self.dir, rel, text)
        if globs is not None:
            write(self.dir, "docs/graph/spec-lint.py", f"TEST_GLOBS = {list(globs)!r}\n")
        if config is not None:
            write(self.dir, CONFIG_PATH, config if isinstance(config, str) else json.dumps(config) + "\n")
        if cypress:
            write(self.dir, ".cypress/seed.json", "{}\n")
        for i, (rel, nfiles) in enumerate(sorted((nested or {}).items())):
            ignore += f"/{rel}/\n"
            write(self.dir, f"docs/graph/nodes/repo{i}.md", node(f"subsystem.repo{i}", repo=rel))
            sub = self.dir / rel
            sub.mkdir(parents=True, exist_ok=True)
            git(sub, "init", "-q")
            git(sub, "symbolic-ref", "HEAD", "refs/heads/trunk")
            for r2, t2 in nfiles.items():
                write(sub, r2, t2)
            git(sub, "add", "-A")
            git(sub, "commit", "-qm", "nested fixture")
        if ignore:
            gi = self.dir / ".gitignore"
            write(self.dir, ".gitignore", (gi.read_text() if gi.exists() else "") + ignore)
        # install.sh places the tool and the files it loads by path in docs/graph/.
        # Copied only when present: a missing tool fails the case at its first run.
        (self.dir / "docs" / "graph").mkdir(parents=True, exist_ok=True)
        if TOOL.is_file():
            shutil.copy(TOOL, self.dir / "docs" / "graph" / "source-index.py")
        for n, src in SIBLINGS.items():
            if src.is_file():
                shutil.copy(src, self.dir / "docs" / "graph" / n)
        if git_init and commit:
            git(self.dir, "add", "-A")
            git(self.dir, "commit", "-qm", "fixture")

    @property
    def cache(self):
        return self.dir / ".cypress" / "source-index"

    @property
    def index(self):
        return self.cache / "index.json"

    def blob(self, rel, repo="."):
        """Git's blob hash of what the index holds, else of the work-tree file."""
        r = self.dir / repo
        path = rel if repo == "." else os.path.relpath(self.dir / rel, r)
        out = subprocess.run(["git", *FIXTURE_GIT, "ls-files", "-s", "--", path], cwd=str(r),
                             capture_output=True, text=True, env=ENV).stdout.split()
        if out and len(out) >= 2:
            return out[1]
        return git(r, "hash-object", "--", path).strip()

    def commit(self, *paths, msg="change"):
        git(self.dir, "add", "-A", "--", *paths)
        git(self.dir, "commit", "-qm", msg)


class Run:
    def __init__(self, rc, raw, err):
        self.rc, self.raw, self.err = rc, raw, err
        self.out = raw.decode("utf-8", "surrogateescape")

    def lines(self):
        return self.out.rstrip("\n").split("\n") if self.out else []

    def last(self):
        ls = [l for l in self.lines() if l.strip()]
        return ls[-1] if ls else ""

    def ctx(self):
        return f"exit {self.rc}; stdout {self.out[:900]!r}; stderr {self.err[:600]!r}"

    def doc(self):
        check(self.rc == 0, f"the query must exit 0 — {self.ctx()}")
        try:
            d = json.loads(self.out)
        except ValueError:
            raise CaseFail(f"--json printed no JSON document — {self.ctx()}")
        check(isinstance(d, dict) and d.get("schema") == ANSWER_SCHEMA,
              f"the answer's schema is not {ANSWER_SCHEMA!r} — {self.ctx()}")
        return d


def tool(plant, *args, env=None, stdin=None, cwd=None):
    check(TOOL.is_file(), f"tools/source-index.py does not exist in the seed ({TOOL}): "
                          f"the tool this contract drives is not built yet")
    try:
        r = subprocess.run([sys.executable, "docs/graph/source-index.py", *args], cwd=str(cwd or plant.dir),
                           capture_output=True, timeout=60, env=env or ENV, input=stdin)
    except subprocess.TimeoutExpired:
        raise CaseFail(f"`source-index.py {' '.join(args)}` ran past 60 s")
    return Run(r.returncode, r.stdout, r.stderr.decode("utf-8", "replace"))


def query(plant, *args, **kw):
    """The `--json` answer of one query, which must exit 0."""
    return tool(plant, *args, "--json", **kw).doc()


def without_cache(doc):
    return {k: v for k, v in doc.items() if k != "cache"}


def from_empty_cache(plant, *args):
    """The answer a query gives after the cache directory is deleted."""
    shutil.rmtree(plant.cache, ignore_errors=True)
    return query(plant, *args)


def status(doc):
    c = doc.get("cache") or {}
    return c.get("status")


def links_of(doc, holder):
    return [l for l in doc.get("links", []) if l.get("holder") == holder]


def link_set(doc, holder):
    return sorted((l.get("target"), l.get("kind"), l.get("link"), l.get("found"), l.get("line"))
                  for l in links_of(doc, holder))


def records(doc, key, holder):
    return [r for r in doc.get(key, []) if r.get("holder") == holder]


def row_paths(doc, key):
    return [r.get("path") for r in doc.get(key, [])]


def row(doc, key, path):
    rows = [r for r in doc.get(key, []) if r.get("path") == path]
    check(len(rows) == 1, f"`{key}` lists {path} {len(rows)} time(s), not once: {doc.get(key)!r}")
    return rows[0]


def reasons(doc):
    return [r.get("reason") for r in doc.get("incomplete", [])]


def git_status(plant):
    return git(plant.dir, "status", "--porcelain=v1", "--untracked-files=all")


CASES = []


def case(label, slug):
    def deco(fn):
        CASES.append((label, slug, fn))
        return fn
    return deco


# --- index and cache ------------------------------------------------------------
def inventory_plant(base, name="plant"):
    """The plant of BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY."""
    files = {
        ".gitignore": "*.secret.py\n",
        "src/a.py": "A = 1\n",
        "src/b.py": "B = 1\n",
        "src/c.py": "import b\n",
        "scripts/run.sh": "#!/usr/bin/env bash\necho run\n",
        "bin/tool": "#!/usr/bin/env python3\nprint('tool')\n",
        "web/app.ts": "export const x = 1;\n",
        "web/app.mjs": "export const y = 1;\n",
        "conf/settings.json": "{}\n",
        "README.md": "# a synthetic plant\n",
        "tests/t.sh": "#!/usr/bin/env bash\necho test\n",
        "docs/graph/nodes/x.md": node("subsystem.x"),
        # a nested plant: its own seed stamp; none of its files is this plant's
        "scratch/.cypress/seed.json": "{}\n",
        "scratch/s.py": "S = 1\n",
    }
    p = Plant(base, name, files=files, nested={"vendor/lib": {"lib.py": "L = 1\n"}}, commit=False)
    # FILE_NOT_REGULAR: a tracked symlink is a record hashed from its link text,
    # a link target only, never a holder.
    (p.dir / "src" / "link.py").symlink_to("c.py")
    p.commit(".")
    write(p.dir, "src/new.py", "N = 1\n")                     # untracked, not ignored
    write(p.dir, "keys.secret.py", "K = 1\n")                 # ignored
    write(p.dir, "__pycache__/x.pyc", "fake bytecode\n")      # build noise
    write(p.dir, "src/y.py.bak-20261001-091322", "Y = 0\n")   # installer backup
    write(p.dir, ".cypress/state.py", "Z = 0\n")               # plant state
    write(p.dir, "vendor/lib/extra.sh", "echo extra\n")       # untracked in the nested repository
    return p


INVENTORY = {   # path -> (repo, language, test)
    ".gitignore": (".", "other", "code"),
    "src/a.py": (".", "python", "code"),
    "src/b.py": (".", "python", "code"),
    "src/c.py": (".", "python", "code"),
    "src/link.py": (".", "python", "code"),
    "src/new.py": (".", "python", "code"),
    "scripts/run.sh": (".", "shell", "code"),
    "bin/tool": (".", "python", "code"),
    "web/app.ts": (".", "typescript", "code"),
    "web/app.mjs": (".", "javascript", "code"),
    "conf/settings.json": (".", "json", "code"),
    "README.md": (".", "other", "code"),
    "tests/t.sh": (".", "shell", "test"),
    "vendor/lib/lib.py": ("vendor/lib", "python", "code"),
    "vendor/lib/extra.sh": ("vendor/lib", "shell", "code"),
}


@case("X425", "BUILD_INVENTORIES_THE_CODE_OF_EVERY_GOVERNED_REPOSITORY; failure FILE_NOT_REGULAR (a symlink)")
def x425(base):
    p = inventory_plant(base)
    # A `repo:` that resolves outside the plant root to a Git work tree governs
    # nothing: none of its files is inventoried.
    elsewhere = base / "elsewhere"
    elsewhere.mkdir()
    git(elsewhere, "init", "-q")
    write(elsewhere, "far.py", "F = 1\n")
    git(elsewhere, "add", "-A")
    git(elsewhere, "commit", "-qm", "outside")
    write(p.dir, "docs/graph/nodes/out.md", node("subsystem.out", repo="../elsewhere"))
    p.commit("docs/graph/nodes/out.md")
    d = query(p, "build")
    inv = {r.get("path"): r for r in d.get("inventory", [])}
    problems = []
    if d.get("incomplete"):
        problems.append(f"a `repo:` outside the plant root made the build incomplete: {d.get('incomplete')!r}")
    if sorted(inv) != sorted(INVENTORY):
        problems.append(f"inventory paths: missing {sorted(set(INVENTORY) - set(inv))}, "
                        f"unexpected {sorted(set(inv) - set(INVENTORY))}")
    for path, (repo, lang, test) in INVENTORY.items():
        r = inv.get(path)
        if not r:
            continue
        want_hash = p.blob(path, repo)
        got = (r.get("repo"), r.get("language"), r.get("test"), r.get("hash"))
        if got != (repo, lang, test, want_hash):
            problems.append(f"{path}: (repo, language, test, hash) {got!r} != {(repo, lang, test, want_hash)!r}")
    if links_of(d, "src/link.py"):
        problems.append(f"the symlink src/link.py holds links (a symlink is a target only): {links_of(d, 'src/link.py')!r}")
    if not any(l.get("target") == "src/b.py" for l in links_of(d, "src/c.py")):
        problems.append(f"src/c.py (`import b`) holds no link to src/b.py: {links_of(d, 'src/c.py')!r}")
    check(not problems, " || ".join(problems))
    return ("tracked and untracked code of both repositories, each with repo, blob hash, language and "
            "test class; no ignored, graph, .cypress, noise or nested-plant file; a symlink holds no link")


@case("X426", "BUILD_IS_DETERMINISTIC")
def x426(base):
    p = inventory_plant(base)
    r = tool(p, "build")
    check(r.rc == 0 and p.index.is_file(), f"build wrote no .cypress/source-index/index.json — {r.ctx()}")
    first = p.index.read_bytes()
    shutil.rmtree(p.cache)
    r = tool(p, "build")
    check(r.rc == 0 and p.index.is_file(), f"the second build wrote no index.json — {r.ctx()}")
    second = p.index.read_bytes()
    check(first == second, "two builds of one plant wrote index.json files that differ")
    for root in {str(p.dir), str(p.dir.resolve())}:
        check(root.encode() not in second, f"index.json holds the plant root's absolute path {root!r}")
    copy = base / "copied"
    shutil.copytree(p.dir, copy, symlinks=True)
    d = query(p, "impact", "src/b.py", cwd=copy)
    check(status(d) == "reused", f"a copy of the plant did not answer from its copied cache: cache {d.get('cache')!r}")
    return "two builds byte-identical, no absolute plant path, a copied plant reuses the copied cache"


@case("X427", "CACHE_WRITTEN_SELF_IGNORED; failures CYPRESS_DIR_ABSENT, CACHE_PATH_UNSAFE, CACHE_IGNORE_ALTERED")
def x427(base):
    files = {"src/a.py": "A = 1\n", "src/b.py": "import a\n"}
    problems = []
    # (a) the first query writes the cache and its inner ignore.
    p = Plant(base, "fresh", files=files)
    # Python's own bytecode switch is off, so only the tool decides what it writes.
    d = query(p, "impact", "src/a.py", env={k: v for k, v in ENV.items() if k != "PYTHONDONTWRITEBYTECODE"})
    if (p.dir / "docs" / "graph" / "__pycache__").exists():
        problems.append("(a) the query wrote docs/graph/__pycache__/ (it writes only under .cypress/source-index/)")
    if not p.index.is_file():
        problems.append("(a) no .cypress/source-index/index.json after a query")
    gi = p.cache / ".gitignore"
    if not gi.is_file() or gi.read_bytes() != CACHE_IGNORE:
        problems.append(f"(a) .cypress/source-index/.gitignore is not exactly '*\\n': "
                        f"{gi.read_bytes() if gi.is_file() else None!r}")
    st = [l for l in git_status(p).split("\n") if ".cypress/source-index" in l]
    if st:
        problems.append(f"(a) git status shows the cache: {st!r}")
    if status(d) != "built":
        problems.append(f"(a) cache status {d.get('cache')!r}, not built")
    # (b) CYPRESS_DIR_ABSENT: the answer is given, nothing is written.
    q = Plant(base, "no-cypress", files=files, cypress=False)
    d = query(q, "impact", "src/a.py")
    if status(d) != "not-written" or not (d.get("cache") or {}).get("reason"):
        problems.append(f"(b) no .cypress/: cache {d.get('cache')!r}, not not-written with a reason")
    if (q.dir / ".cypress").exists():
        problems.append("(b) the query created .cypress/")
    if row_paths(d, "dependents") != ["src/b.py"]:
        problems.append(f"(b) the in-memory answer lacks src/b.py: {d.get('dependents')!r}")
    # (c) CACHE_PATH_UNSAFE: .cypress/source-index is a symlink to a directory outside.
    s = Plant(base, "linked", files=files)
    outside = base / "outside"
    outside.mkdir()
    s.cache.symlink_to(outside)
    d = query(s, "impact", "src/a.py")
    if status(d) != "not-written" or not (d.get("cache") or {}).get("reason"):
        problems.append(f"(c) symlinked cache directory: cache {d.get('cache')!r}, not not-written with a reason")
    if os.listdir(outside):
        problems.append(f"(c) the query wrote through the symlink: {os.listdir(outside)!r}")
    if not s.cache.is_symlink() or os.readlink(s.cache) != str(outside):
        problems.append("(c) the symlink was not left as it was")
    # (d) CACHE_IGNORE_ALTERED: an inner ignore with a `!index.json` line is rewritten first.
    a = Plant(base, "altered", files=files)
    write(a.dir, ".cypress/source-index/.gitignore", "*\n!index.json\n")
    d = query(a, "impact", "src/a.py")
    gi = a.cache / ".gitignore"
    if gi.read_bytes() != CACHE_IGNORE:
        problems.append(f"(d) the altered inner .gitignore was not rewritten: {gi.read_bytes()!r}")
    st = [l for l in git_status(a).split("\n") if ".cypress/source-index" in l]
    if st:
        problems.append(f"(d) git status shows the cache: {st!r}")
    # (d) on reuse: an ignore altered beside a usable cache is never reused past.
    query(a, "impact", "src/a.py")
    write(a.dir, ".cypress/source-index/.gitignore", "*\n!index.json\n")
    d = query(a, "impact", "src/a.py")
    if gi.read_bytes() != CACHE_IGNORE:
        problems.append(f"(d) reuse: the altered inner .gitignore was left in place: {gi.read_bytes()!r}")
    if status(d) != "rebuilt":
        problems.append(f"(d) reuse: cache {d.get('cache')!r}, not rebuilt over the altered ignore")
    st = [l for l in git_status(a).split("\n") if ".cypress/source-index" in l]
    if st:
        problems.append(f"(d) reuse: git status shows the cache: {st!r}")
    check(not problems, " || ".join(problems))
    return ("index.json beside an inner '*' ignore, invisible to git, status built; no .cypress/ and a "
            "symlinked cache are not-written; an altered ignore is restored")


@case("X428", "CACHE_REUSED_WHILE_THE_KEY_HOLDS")
def x428(base):
    p = Plant(base, files={"src/a.py": "A = 1\n", "src/b.py": "import a\n"})
    query(p, "impact", "src/a.py")
    check(p.index.is_file(), "the first query wrote no index.json")
    before = (p.index.read_bytes(), p.index.stat().st_mtime_ns)
    d = query(p, "impact", "src/a.py")
    check(status(d) == "reused", f"cache status {d.get('cache')!r}, not reused")
    check((p.index.read_bytes(), p.index.stat().st_mtime_ns) == before,
          "a reusing query changed index.json's bytes or modification time")
    return "the second query reuses the cache; index.json bytes and mtime unchanged"


@case("X429", "CACHE_REBUILT_WHEN_THE_KEY_CHANGES; failure CACHE_UNREADABLE")
def x429(base):
    p = Plant(base, files={"src/a.py": "A = 1\n", "src/b.py": "import a\n", "tests/t.sh": "python3 src/b.py\n",
                           "tests/u.sh": "python3 src/a.py\n"},
              config={"exclude": []})
    args = ("affected-tests", "src/a.py")
    query(p, *args)
    problems = []

    def arm(what, change, reason=None):
        change()
        d = query(p, *args)
        if status(d) != "rebuilt":
            problems.append(f"{what}: cache {d.get('cache')!r}, not rebuilt")
        if reason and reason not in str((d.get("cache") or {}).get("reason")):
            problems.append(f"{what}: the cache reason {d.get('cache')!r} does not say {reason!r}")
        fresh = from_empty_cache(p, *args)
        if without_cache(d) != without_cache(fresh):
            problems.append(f"{what}: the rebuilt answer differs from one built from an empty cache")

    def commit_new():
        write(p.dir, "src/c.py", "import a\n")
        p.commit("src/c.py")

    def edit_python():
        idx = json.loads(p.index.read_text())
        idx["key"]["python"] = "3.0"
        p.index.write_text(json.dumps(idx, sort_keys=True, indent=1) + "\n")

    arm("(a) a new commit", commit_new)
    arm("(b) an uncommitted code edit", lambda: write(p.dir, "src/b.py", "import a\nB = 2\n"))
    arm("(c) a config edit", lambda: write(p.dir, CONFIG_PATH, json.dumps({"exclude": ["tests/u.sh"]}) + "\n"))
    arm("(d) a TEST_GLOBS edit", lambda: write(p.dir, "docs/graph/spec-lint.py", "TEST_GLOBS = ['tests/t.sh']\n"))
    arm("(e) index.json not JSON", lambda: p.index.write_text("{not json"), reason="unreadable")
    arm("(e) index.json of another schema",
        lambda: p.index.write_text(json.dumps({"schema": "cypress.source-index/0"}) + "\n"), reason="unreadable")
    arm("(f) another Python major.minor in the key", edit_python)
    check(not problems, " || ".join(problems))
    return ("a commit, an uncommitted edit, a config edit, a TEST_GLOBS edit, an unreadable cache and "
            "another Python in the key each rebuild, equal to a build from an empty cache")


@case("X430", "GRAFT_REBUILDS_THE_CACHE")
def x430(base):
    t = base / "target"
    t.mkdir()
    inst = subprocess.run(["bash", str(SEED / "install.sh"), "all", "--project-dir", str(t), "--copy"],
                          capture_output=True, text=True, timeout=600, env=ENV)
    if inst.returncode != 0:
        raise HarnessFail(f"install.sh all exited {inst.returncode}: {inst.stderr[-600:]}")
    placed = t / "docs" / "graph" / "source-index.py"
    check(placed.is_file(), "install.sh placed no docs/graph/source-index.py")
    # An older seed's tool: other bytes than tools/source-index.py.
    placed.write_bytes(placed.read_bytes() + b"\n# an older seed's source-index.py\n")
    write(t, "src/a.py", "A = 1\n")
    write(t, "src/b.py", "import a\n")
    git(t, "init", "-q")
    git(t, "add", "-A")
    git(t, "commit", "-qm", "plant")

    class P:
        dir = t
    d = query(P, "impact", "src/a.py")
    cache = t / ".cypress" / "source-index" / "index.json"
    check(cache.is_file(), f"the older tool's query wrote no cache: {d.get('cache')!r}")
    old = cache.read_bytes()
    inst = subprocess.run(["bash", str(SEED / "install.sh"), "all", "--project-dir", str(t), "--copy"],
                          capture_output=True, text=True, timeout=600, env=ENV)
    if inst.returncode != 0:
        raise HarnessFail(f"the re-install exited {inst.returncode}: {inst.stderr[-600:]}")
    check(placed.read_bytes() == TOOL.read_bytes(), "the re-install did not place the seed's tool")
    check(cache.is_file() and cache.read_bytes() == old, "the installer deleted or rewrote the cache")
    d = query(P, "impact", "src/a.py")
    check(status(d) == "rebuilt", f"after the install the cache status is {d.get('cache')!r}, not rebuilt")
    return "an install over an older tool's cache leaves it; the next query rebuilds it"


# --- links ----------------------------------------------------------------------
PY_A = """import importlib
import importlib.util
import importlib.util as _ilu
import json
import os
import runpy
from pathlib import Path

from . import b
from .sub import c
import pkg.d

importlib.import_module("pkg.e")
_ilu.spec_from_file_location("f", Path(__file__).resolve().parent / "f.py")
importlib.util.spec_from_file_location("h", Path(__file__).parent.parent / "tools" / "h.py")
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "g.py"))
"""


@case("X431", "LINK_PYTHON_IMPORT_CERTAIN")
def x431(base):
    files = {"pkg/a.py": PY_A, "pkg/b.py": "B = 1\n", "pkg/sub/c.py": "C = 1\n", "pkg/d.py": "D = 1\n",
             "pkg/e.py": "E = 1\n", "pkg/f.py": "F = 1\n", "pkg/g.py": "G = 1\n", "tools/h.py": "H = 1\n"}
    p = Plant(base, files=files)
    d = query(p, "build")
    L = lambda s: line_of(PY_A, s)
    want = sorted([
        ("pkg/b.py", "import", "certain", "exact", L("from . import b")),
        ("pkg/sub/c.py", "import", "certain", "exact", L("from .sub import c")),
        ("pkg/f.py", "import", "certain", "exact", L('"f.py"')),
        ("tools/h.py", "import", "certain", "exact", L('"h.py"')),
        ("pkg/g.py", "import", "certain", "exact", L('"g.py"')),
        ("pkg/d.py", "import", "certain", "resolved", L("import pkg.d")),
        ("pkg/e.py", "import", "certain", "resolved", L('"pkg.e"')),
    ])
    got = link_set(d, "pkg/a.py")
    check(got == want, f"the links held by pkg/a.py are not exactly the seven certain imports: "
                       f"got {got!r}, want {want!r}")
    recs = records(d, "opaque", "pkg/a.py") + records(d, "unresolved", "pkg/a.py")
    check(not recs, f"pkg/a.py holds records (json is external): {recs!r}")
    # A package with an `__init__.py`: `from pkg2 import sub` names the package
    # and its submodule, absolute and relative alike.
    q = Plant(base, "init-pkg", files={"app.py": "from pkg2 import sub\n", "pkg2/__init__.py": "",
                                       "pkg2/sub.py": "S = 1\n", "pkg2/x.py": "from . import sub\n"})
    d2 = query(q, "build")
    problems = []
    for holder in ("app.py", "pkg2/x.py"):
        got = sorted((l.get("target"), l.get("link")) for l in links_of(d2, holder))
        if got != [("pkg2/__init__.py", "certain"), ("pkg2/sub.py", "certain")]:
            problems.append(f"{holder}: links {got!r}, not certain links to pkg2/__init__.py and pkg2/sub.py")
    dep = row_paths(query(q, "impact", "pkg2/sub.py"), "dependents")
    if "app.py" not in dep:
        problems.append(f"impact pkg2/sub.py misses app.py (`from pkg2 import sub`): {dep!r}")
    check(not problems, " || ".join(problems))
    return "seven certain import links (two relative, three loads by file path exact; two resolved); json external"


SH_X = """#!/usr/bin/env bash
set -eu
python3 -B "$ROOT/tools/x.py"
bash tests/helpers/plant.sh
source "$ROOT/tests/lib.sh"
. ./common.sh
python3 -m pkg.mod
"""


@case("X432", "LINK_SHELL_INVOCATION_CERTAIN")
def x432(base):
    files = {"tests/test-x.sh": SH_X, "tools/x.py": "X = 1\n", "tests/helpers/plant.sh": "true\n",
             "tests/lib.sh": "true\n", "tests/common.sh": "true\n", "pkg/mod.py": "M = 1\n"}
    p = Plant(base, files=files)
    d = query(p, "build")
    L = lambda s: line_of(SH_X, s)
    want = {"tools/x.py": L("tools/x.py"), "tests/helpers/plant.sh": L("plant.sh"),
            "tests/lib.sh": L("lib.sh"), "tests/common.sh": L("common.sh"), "pkg/mod.py": L("pkg.mod")}
    got = links_of(d, "tests/test-x.sh")
    problems = []
    if sorted(l.get("target") for l in got) != sorted(want):
        problems.append(f"tests/test-x.sh links {sorted(l.get('target') for l in got)}, "
                        f"not exactly one to each of {sorted(want)}")
    for l in got:
        if (l.get("kind"), l.get("link"), l.get("line")) != ("invoke", "certain", want.get(l.get("target"))):
            problems.append(f"not a certain invoke link at its line: {l!r}")
    mod = [l for l in got if l.get("target") == "pkg/mod.py"]
    if mod and mod[0].get("found") != "resolved":
        problems.append(f"pkg.mod is not found `resolved` as a Python module: {mod[0]!r}")
    # A variable-led path to a sibling script resolves from the holder's directory.
    sib = 'DIR=$(cd "$(dirname "$0")" && pwd)\nsource "$DIR/lib.sh"\n. "$(dirname "$0")/common.sh"\n'
    r = Plant(base, "sibling", files={"tests/sib.sh": sib, "tests/lib.sh": "true\n", "tests/common.sh": "true\n"})
    d3 = query(r, "build")
    got3 = sorted((l.get("target"), l.get("kind"), l.get("link"), l.get("found"), l.get("line"))
                  for l in links_of(d3, "tests/sib.sh"))
    want3 = [("tests/common.sh", "invoke", "certain", "resolved", 3),
             ("tests/lib.sh", "invoke", "certain", "resolved", 2)]
    if got3 != want3:
        problems.append(f"tests/sib.sh ($DIR/lib.sh, $(dirname \"$0\")/common.sh) links {got3!r}, want {want3!r}")
    q = Plant(base, "two-repos", files={"run.sh": "python3 Cypress/tools/y.py\n"},
              nested={"Cypress": {"tools/y.py": "Y = 1\n"}})
    d2 = query(q, "build")
    got2 = [(l.get("target"), l.get("kind"), l.get("link")) for l in links_of(d2, "run.sh")]
    if got2 != [("Cypress/tools/y.py", "invoke", "certain")]:
        problems.append(f"run.sh does not hold one certain invoke link into the nested repository: {got2!r}")
    check(not problems, " || ".join(problems))
    return "five certain invoke links from the shell test (pkg.mod resolved); one across repositories"


PY_T = """from pathlib import Path

TEXT = (Path(__file__).resolve().parent / "frontmatter.py").read_text()
LINT = "$SEED_ROOT/templates/k/lint.py"
KIT = "templates/k/"
"""
PY_W = """SEP = "/"
HERE = "./"
TOP = "$ROOT/"
WIDE = "wide/"


def parts(s):
    return s.split("/")
"""


@case("X433", "LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE; failure DIRECTORY_LITERAL_TOO_WIDE")
def x433(base):
    files = {"tools/t.py": PY_T, "tools/frontmatter.py": "F = 1\n", "templates/k/lint.py": "K = 1\n",
             "templates/k/a.json": "{}\n", "notes.md": "The tool is `tools/t.py`.\n", "tools/w.py": PY_W}
    for i in range(DIR_LINK_MAX + 1):
        files[f"wide/f{i:03d}.json"] = "{}\n"
    p = Plant(base, files=files)
    d = query(p, "build")
    L = lambda s: line_of(PY_T, s)
    want = sorted([
        ("tools/frontmatter.py", "path-literal", "maybe", "path-literal", L("frontmatter.py")),
        ("templates/k/lint.py", "path-literal", "maybe", "path-literal", L("lint.py")),
        ("templates/k/lint.py", "path-literal", "maybe", "directory", L('"templates/k/"')),
        ("templates/k/a.json", "path-literal", "maybe", "directory", L('"templates/k/"')),
    ])
    problems = []
    got = link_set(d, "tools/t.py")
    if got != want:
        problems.append(f"tools/t.py links {got!r}, want {want!r}")
    if links_of(d, "notes.md"):
        problems.append(f"the Markdown file holds links: {links_of(d, 'notes.md')!r}")
    if links_of(d, "tools/w.py"):
        problems.append(f"tools/w.py holds {len(links_of(d, 'tools/w.py'))} link(s): a root-like string or a "
                        f"directory over DIR_LINK_MAX must link nothing")
    op = [(r.get("reason")) for r in records(d, "opaque", "tools/w.py")]
    if op != ["walks-tree"]:
        problems.append(f"tools/w.py (a directory over DIR_LINK_MAX) is not one opaque walks-tree record: {op!r}")
    check(not problems, " || ".join(problems))
    return ("two path-literal and two directory maybe links, each at its line; Markdown links nothing; a "
            "root string links nothing and a too-wide directory makes its holder opaque walks-tree")


TSCONFIG = """{
  // the alias the app uses
  "compilerOptions": {
    /* a block comment */
    "paths": {"@/*": ["./src/*"]},
  },
}
"""
TS_X = """import { a } from "./a";
import type { D } from "@/lib/db";
export * from "../util/u.js";
const r = require("./r");
import "node:fs";
import React from "react";

export async function load() {
  await import("./lazy");
  return await import(
    "@/lib/late"
  );
}
"""


@case("X434", "LINK_TS_SPECIFIER_CERTAIN; failure TSCONFIG_EXTENDS_CYCLE")
def x434(base):
    files = {"tsconfig.json": TSCONFIG, "src/app/x.ts": TS_X, "src/app/a.ts": "export const a = 1;\n",
             "src/lib/db/index.ts": "export type D = number;\n", "src/util/u.ts": "export const u = 1;\n",
             "src/app/r.js": "module.exports = 1;\n", "src/app/lazy.tsx": "export const l = 1;\n",
             "src/lib/late.ts": "export const late = 1;\n",
             # an `extends` cycle: tsconfig.json -> base.json -> tsconfig.json
             "cyc/tsconfig.json": '{"extends": "./base.json", "compilerOptions": {"paths": {"@/*": ["./*"]}}}\n',
             "cyc/base.json": '{"extends": "./tsconfig.json"}\n',
             "cyc/m.ts": 'import { k } from "./k";\nimport { z } from "@/z";\n',
             "cyc/k.ts": "export const k = 1;\n", "cyc/z.ts": "export const z = 1;\n"}
    p = Plant(base, files=files)
    d = query(p, "build")
    L = lambda s: line_of(TS_X, s)
    want = sorted([
        ("src/app/a.ts", "import", "certain", "resolved", L('"./a"')),
        ("src/lib/db/index.ts", "import", "certain", "resolved", L('"@/lib/db"')),
        ("src/util/u.ts", "import", "certain", "resolved", L("u.js")),
        ("src/app/r.js", "import", "certain", "resolved", L('"./r"')),
        ("src/app/lazy.tsx", "import", "certain", "resolved", L("./lazy")),
        ("src/lib/late.ts", "import", "certain", "resolved", L("return await import(")),
    ])
    problems = []
    got = link_set(d, "src/app/x.ts")
    if got != want:
        problems.append(f"src/app/x.ts links {got!r}, want {want!r}")
    recs = records(d, "opaque", "src/app/x.ts") + records(d, "unresolved", "src/app/x.ts")
    if recs:
        problems.append(f"src/app/x.ts holds records (the line join, node:fs and react external): {recs!r}")
    cyc = [(l.get("target"), l.get("link")) for l in links_of(d, "cyc/m.ts")]
    if cyc != [("cyc/k.ts", "certain")]:
        problems.append(f"under an extends cycle cyc/m.ts must keep only its relative import: {cyc!r}")
    op = [r.get("reason") for r in records(d, "opaque", "cyc/m.ts")]
    if op != ["alias-config-unavailable"]:
        problems.append(f"cyc/m.ts is not one opaque alias-config-unavailable record: {op!r}")
    # A workspace package's subpath import links the subpath's file.
    w = Plant(base, "workspace", files={"packages/ui/package.json": '{"name": "@acme/ui"}\n',
                                        "packages/ui/button.ts": "export const b = 1;\n",
                                        "packages/ui/card.ts": "export const c = 1;\n",
                                        "app/x.ts": 'import { b } from "@acme/ui/button";\n'})
    dw = query(w, "build")
    gw = [(l.get("target"), l.get("found")) for l in links_of(dw, "app/x.ts")]
    if gw != [("packages/ui/button.ts", "resolved")]:
        problems.append(f"app/x.ts (`@acme/ui/button`) links {gw!r}, not one resolved link to packages/ui/button.ts")
    check(not problems, " || ".join(problems))
    return ("six certain resolved imports through a JSONC tsconfig, the split import() joined; bare packages "
            "external; an extends cycle keeps relative imports and makes the alias holder opaque")


@case("X435", "UNPINNED_REFERENCE_RECORDED_WITH_ITS_REASON; failures TSCONFIG_UNREADABLE, FILE_NOT_REGULAR, "
              "INPUT_EXHAUSTS_A_PARSER, GIT_PATH_ARGUMENT")
def x435(base):
    big = "import os\n" + "X = 1\n" * (FILE_MAX_BYTES // 6 + 1)
    files = {
        ".gitignore": ".next/\n",
        "tsconfig.json": '{"compilerOptions": {"paths": {"@/*": ["./src/*"]}}}\n',
        "src/dyn.ts": "export async function f(name: string) {\n  return import(name);\n}\n",
        "py/walker.py": "import os\n\n\ndef f(root):\n    return list(os.walk(root))\n",
        # walks whose literal root makes no directory link (no `/`, a glob, `.`)
        "tools/a.py": "A = 1\n",
        "py/globber.py": 'import glob\nprint(glob.glob("tools/*.py"))\n',
        "py/oswalker.py": 'import os\nfor x in os.walk("tools"):\n    pass\n',
        "py/rglobber.py": 'from pathlib import Path\nprint(list(Path("tools").rglob("*.py")))\n',
        "sh/finder.sh": "find . -name '*.py'\n",
        "py/broken.py": "def (:\n",
        # TSCONFIG_UNREADABLE: an `extends` that names a file the inventory lacks
        "ext/tsconfig.json": '{"extends": "./missing-base.json", "compilerOptions": {"paths": {"@/*": ["./*"]}}}\n',
        "ext/u.ts": 'import { w } from "./w";\nimport { v } from "@/v";\n',
        "ext/w.ts": "export const w = 1;\n", "ext/v.ts": "export const v = 1;\n",
        "src/app/r1.ts": 'import "./missing";\n',
        "src/app/r2.ts": 'import "@/nope";\n',
        "src/app/r3.ts": 'import "./.next/types/routes.d.ts";\n',
        "src/app/r4.ts": 'import css from "./a.css?raw";\n',
        "py/amb.py": "import app.main\n",
        "x1/app/main.py": "M = 1\n", "x2/app/main.py": "M = 2\n",
        # GIT_PATH_ARGUMENT: paths Git would read as options, pathspec magic or globs
        "src/app/g.ts": ('import "./--exec=x";\nimport "./:(top)q";\nimport "./*";\n'
                         'import "../../../../../outside";\n'),
        # FILE_NOT_REGULAR and INPUT_EXHAUSTS_A_PARSER
        "py/fifo.py": "F = 1\n",
        "py/big.py": big,
        "py/nul.py": b"import os\nX = '\x00'\n",
    }
    p = Plant(base, files=files)
    write(p.dir, "src/app/.next/types/routes.d.ts", "export {};\n")   # ignored by Git
    (p.dir / "py" / "fifo.py").unlink()
    os.mkfifo(p.dir / "py" / "fifo.py")                                # a tracked file replaced by a FIFO
    d = query(p, "build")
    problems = []
    for holder, reason in (("src/dyn.ts", "dynamic-nonliteral"), ("py/walker.py", "walks-tree"),
                           ("py/globber.py", "walks-tree"), ("py/oswalker.py", "walks-tree"),
                           ("py/rglobber.py", "walks-tree"), ("sh/finder.sh", "walks-tree"),
                           ("py/broken.py", "unreadable"), ("ext/u.ts", "alias-config-unavailable")):
        got = [r.get("reason") for r in records(d, "opaque", holder)]
        if got != [reason]:
            problems.append(f"{holder}: opaque reasons {got!r}, not [{reason!r}]")
        certain = [l for l in links_of(d, holder) if l.get("link") == "certain" and holder != "ext/u.ts"]
        if certain:
            problems.append(f"{holder}: holds certain links {certain!r}")
    ext = [(l.get("target"), l.get("link")) for l in links_of(d, "ext/u.ts")]
    if ext != [("ext/w.ts", "certain")]:
        problems.append(f"ext/u.ts under an unreadable tsconfig keeps only its relative import: {ext!r}")
    for holder, reason, base_path in (("src/app/r1.ts", "relative-no-file", "src/app/missing"),
                                      ("src/app/r2.ts", "alias-no-file", "src/nope"),
                                      ("src/app/r3.ts", "generated", "src/app/.next/types/routes.d.ts"),
                                      ("src/app/r4.ts", "asset", "src/app/a.css")):
        got = [(r.get("reason"), r.get("base"), r.get("kind"), r.get("line")) for r in records(d, "unresolved", holder)]
        if got != [(reason, base_path, "import", 1)]:
            problems.append(f"{holder}: unresolved {got!r}, not [{(reason, base_path, 'import', 1)!r}]")
        if links_of(d, holder):
            problems.append(f"{holder}: holds links {links_of(d, holder)!r}")
    amb = sorted((l.get("target"), l.get("link"), l.get("found")) for l in links_of(d, "py/amb.py"))
    if amb != [("x1/app/main.py", "maybe", "ambiguous"), ("x2/app/main.py", "maybe", "ambiguous")]:
        problems.append(f"py/amb.py: not two maybe ambiguous links, one per candidate: {amb!r}")
    g = sorted((r.get("reason"), r.get("base")) for r in records(d, "unresolved", "src/app/g.ts"))
    want_g = sorted([("relative-no-file", "src/app/--exec=x"), ("relative-no-file", "src/app/:(top)q"),
                     ("relative-no-file", "src/app/*"), ("outside-repository", None)])
    if g != want_g:
        problems.append(f"src/app/g.ts: unresolved {g!r}, want {want_g!r}")
    if d.get("incomplete"):
        problems.append(f"paths Git could misread made the build incomplete: {d.get('incomplete')!r}")
    for holder in ("py/fifo.py", "py/big.py", "py/nul.py"):
        got = [(r.get("reason"), r.get("line")) for r in records(d, "opaque", holder)]
        if got != [("unreadable", None)]:
            problems.append(f"{holder}: opaque {got!r}, not [('unreadable', None)]")
    inv = {r.get("path"): r for r in d.get("inventory", [])}
    if (inv.get("py/big.py") or {}).get("hash") != p.blob("py/big.py"):
        problems.append("py/big.py (over FILE_MAX_BYTES) lacks its blob hash in the inventory")
    check(not problems, " || ".join(problems))
    return ("four opaque holders, four unresolved references with their bases, two ambiguous maybe links; "
            "a FIFO, an oversized and a NUL-byte file opaque unreadable; Git-hostile paths stay records")


# --- test class -----------------------------------------------------------------
@case("X436", "TESTS_ARE_THE_PLANTS_TEST_GLOBS")
def x436(base):
    p = Plant(base, files={"checks/c.sh": "echo c\n", "tests/t_test.py": "T = 1\n", "src/s.py": "S = 1\n"},
              globs=["checks/**/*.*"])
    d = query(p, "build")
    tests = sorted(r.get("path") for r in d.get("inventory", []) if r.get("test") == "test")
    check(tests == ["checks/c.sh"], f"the test-class records are {tests!r}, not ['checks/c.sh']")
    return "checks/c.sh is the one test: the plant's TEST_GLOBS decide, not a name convention"


@case("X437", "PLANT_CONFIG_REPLACES_EACH_DEFAULT_KEY")
def x437(base):
    p = Plant(base, files={"tests/experimental/e.ts": "export const e = 1;\n", "checks/walk-tree.sh": "echo walk\n",
                           "package.json": '{"name": "p"}\n', "src/s.py": "S = 1\n"},
              globs=["tests/**/*.*", "checks/**/*.*"],
              config={"exclude": ["tests/experimental/**"], "always_run": ["checks/walk-*.sh"]})
    problems = []
    b = query(p, "build")
    e = [r.get("test") for r in b.get("inventory", []) if r.get("path") == "tests/experimental/e.ts"]
    if e != ["code"]:
        problems.append(f"tests/experimental/e.ts: test class {e!r}, not ['code'] (exclude replaces its default)")
    d = query(p, "affected-tests", "package.json")
    ar = [(r.get("path"), r.get("reason")) for r in d.get("always_run", [])]
    if ("checks/walk-tree.sh", "declared") not in ar:
        problems.append(f"always_run lacks checks/walk-tree.sh as declared: {ar!r}")
    gi = [r for r in d.get("incomplete", []) if r.get("reason") == "global-input"]
    if [r.get("subject") for r in gi] != ["package.json"]:
        problems.append(f"no global-input record for package.json (global_inputs keeps its default): "
                        f"{d.get('incomplete')!r}")
    check(not problems, " || ".join(problems))
    return "exclude and always_run replace their defaults; the omitted global_inputs keeps package.json"


# --- walk -----------------------------------------------------------------------
def rowkey(r):
    return (r.get("path"), r.get("depth"), r.get("link"), r.get("from"), r.get("kind"), r.get("found"), r.get("line"))


@case("X438", "WALK_NEAREST_FIRST_ONCE")
def x438(base):
    p = Plant(base, files={"a.py": "A = 1\n", "b.py": "import a\n", "c.py": "import a\nimport b\n",
                           "d.sh": "python3 b.py\n", "e.py": 'NAME = "a.py"\n'})
    d = query(p, "impact", "a.py")
    want = [("b.py", 1, "certain", "a.py", "import", "resolved", 1),
            ("c.py", 1, "certain", "a.py", "import", "resolved", 1),
            ("d.sh", 2, "certain", "b.py", "invoke", "exact", 1),
            ("e.py", 1, "maybe", "a.py", "path-literal", "path-literal", 1)]
    got = [rowkey(r) for r in d.get("dependents", [])]
    check(got == want, f"dependents {got!r}, want (certain rows first, nearest first, c.py once) {want!r}")
    check(d.get("incomplete") == [], f"the answer is not complete: {d.get('incomplete')!r}")
    return "b.py and c.py at depth 1, d.sh at depth 2, then the maybe row; c.py once; complete"


@case("X439", "WALK_CHAIN_IS_ITS_WEAKEST_LINK")
def x439(base):
    p = Plant(base, files={"a.py": "A = 1\n", "b.py": 'NAME = "a.py"\n', "c.py": "import b\n"})
    d = query(p, "impact", "a.py")
    weakest = {"reason": "path-literal", "holder": "b.py", "line": 1}
    problems = []
    for path, depth in (("b.py", 1), ("c.py", 2)):
        r = row(d, "dependents", path)
        if (r.get("depth"), r.get("link"), r.get("maybe")) != (depth, "maybe", weakest):
            problems.append(f"{path}: (depth, link, maybe) {(r.get('depth'), r.get('link'), r.get('maybe'))!r}, "
                            f"want {(depth, 'maybe', weakest)!r}")
    if any(r.get("link") == "certain" for r in d.get("dependents", [])):
        problems.append(f"a row behind a path literal is certain: {d.get('dependents')!r}")
    check(not problems, " || ".join(problems))
    return "b.py and c.py are maybe rows carrying the path literal's reason, holder and line"


FLOOR_FILES = {
    "a.py": "A = 1\n", "b.py": "import a\n", "c.py": 'NAME = "a.py"\n', "d.py": "import b\n",
    "o.py": "import os\n\n\ndef f(root):\n    return list(os.walk(root))\n",
    "p.py": "import o\n",
    "q.py": "from importlib import import_module\nimport a\n\n\ndef f(name):\n    return import_module(name)\n",
    "z.py": "Z = 1\n",
}


@case("X449", "WALK_FLOOR_LISTED_APART_AFTER_THE_INPUT_ROWS")
def x449(base):
    p = Plant(base, files=FLOOR_FILES)
    d = query(p, "impact", "a.py")
    problems = []
    dep = [(r.get("path"), r.get("depth"), r.get("link")) for r in d.get("dependents", [])]
    want = [("b.py", 1, "certain"), ("q.py", 1, "certain"), ("d.py", 2, "certain"), ("c.py", 1, "maybe")]
    if dep != want:
        problems.append(f"a.py dependents {dep!r}, want {want!r}")
    walk = {"reason": "walks-tree", "holder": "o.py", "line": 5}
    fl = [(r.get("path"), r.get("depth"), r.get("link"), r.get("maybe")) for r in d.get("floor", [])]
    if fl != [("o.py", 1, "maybe", walk), ("p.py", 2, "maybe", walk)]:
        problems.append(f"a.py floor {fl!r}, want o.py (1) then p.py (2), maybe {walk!r}")
    z = query(p, "impact", "z.py")
    if z.get("dependents") != []:
        problems.append(f"z.py dependents {z.get('dependents')!r}, not empty")
    zf = sorted(row_paths(z, "floor"))
    if zf != ["o.py", "p.py", "q.py"]:
        problems.append(f"z.py floor {zf!r}: the floor of a.py with q.py added")
    t = tool(p, "impact", "a.py")
    lines = t.lines()
    fline = FLOOR_LINE.format(n=2)
    if fline not in lines:
        problems.append(f"the text view lacks the floor line {fline!r} — {t.ctx()}")
    else:
        i = lines.index(fline)
        named = lambda ls: [w for l in ls for w in l.split()[2:3] if l[:1].isdigit()]
        if named(lines[:i]) != ["b.py", "q.py", "d.py", "c.py"] or named(lines[i + 1:]) != ["o.py", "p.py"]:
            problems.append(f"the text view does not print the dependents, then the floor line, then the "
                            f"floor rows — {t.ctx()}")
    check(not problems, " || ".join(problems))
    return ("certain rows, then the input's maybe row; the floor (o.py, p.py) apart; q.py never a floor row "
            "for a.py; z.py's floor adds q.py; the text view prints the floor after its line")


@case("X440", "WALK_DELETED_INPUT_REACHES_ITS_NAMERS")
def x440(base):
    p = Plant(base, files={"tsconfig.json": '{"compilerOptions": {"paths": {"@/*": ["./src/*"]}}}\n',
                           "src/x.ts": 'import { v } from "@/lib/gone";\nexport const x = v;\n',
                           "tests/x.test.ts": 'import { x } from "../src/x";\n'})
    d = query(p, "affected-tests", "src/lib/gone.ts")
    problems = []
    if [(i.get("path"), i.get("status")) for i in d.get("inputs", [])] != [("src/lib/gone.ts", "walked")]:
        problems.append(f"inputs {d.get('inputs')!r}: the deleted file a reference names is not walked")
    got = [(r.get("path"), r.get("depth"), r.get("link"), r.get("via")) for r in d.get("tests", [])]
    want = [("tests/x.test.ts", 2, "certain", ["src/lib/gone.ts", "src/x.ts", "tests/x.test.ts"])]
    if got != want:
        problems.append(f"tests {got!r}, want {want!r}")
    if d.get("incomplete") != []:
        problems.append(f"the answer is not complete: {d.get('incomplete')!r}")
    check(not problems, " || ".join(problems))
    return "a deleted file reaches the test through its namer's alias-no-file record; complete"


@case("X441", "INPUT_FORMS_RESOLVED")
def x441(base):
    p = Plant(base, files={"docs/graph/nodes/n.md": node("subsystem.n"), "README.md": "# r\n"},
              nested={"Cypress": {"tools/x.py": "X = 1\n", "tools/y.py": "import x\n"}})
    absolute = str((p.dir / "Cypress" / "tools" / "x.py").resolve())
    d = query(p, "impact", "tools/x.py", absolute, "./Cypress/tools/x.py", "docs/graph/nodes/n.md")
    problems = []
    got = [(i.get("path"), i.get("status")) for i in d.get("inputs", [])]
    if got != [("Cypress/tools/x.py", "walked"), ("docs/graph/nodes/n.md", "not-code")]:
        problems.append(f"inputs {got!r}: three forms of one file, then the not-code page")
    if row_paths(d, "dependents") != ["Cypress/tools/y.py"]:
        problems.append(f"dependents {row_paths(d, 'dependents')!r}, not ['Cypress/tools/y.py']")
    if d.get("incomplete") != []:
        problems.append(f"the answer is not complete: {d.get('incomplete')!r}")
    check(not problems, " || ".join(problems))
    return "repository-relative, absolute and ./ forms are one walked file; a graph page is not-code; complete"


QUERIES_ALL = ("impact", "affected-tests", "anchors")


def expect_incomplete(problems, arm, plant, inputs, reason, subject=None, queries=QUERIES_ALL, extra=(),
                      env=None, candidates=None, still=None):
    """Each query: exit 0, one `incomplete` record of `reason` (its subject, its
    candidates), the rows `still` reached, and the text view's action line."""
    for q in queries:
        try:
            d = query(plant, q, *extra, *inputs, env=env)
        except CaseFail as e:
            problems.append(f"{arm} {q}: {e}")
            continue
        recs = [r for r in d.get("incomplete", []) if r.get("reason") == reason]
        if len(recs) != 1:
            problems.append(f"{arm} {q}: incomplete {d.get('incomplete')!r} holds no single {reason!r} record")
            continue
        r = recs[0]
        if subject is not None and r.get("subject") != subject:
            problems.append(f"{arm} {q}: the {reason} record names {r.get('subject')!r}, not {subject!r}")
        if subject is None and not r.get("subject"):
            problems.append(f"{arm} {q}: the {reason} record names no subject: {r!r}")
        if candidates is not None and sorted(r.get("candidates") or []) != sorted(candidates):
            problems.append(f"{arm} {q}: candidates {r.get('candidates')!r}, not {candidates!r}")
        if still and q in still and not set(still[q][1]) <= set(row_paths(d, still[q][0])):
            problems.append(f"{arm} {q}: the rows the walk reached are not listed: {d.get(still[q][0])!r}")
        t = tool(plant, q, *extra, *inputs, env=env)
        if t.rc != 0 or not (t.last().startswith(ACTION[q]) and reason in t.last()):
            problems.append(f"{arm} {q}: the text view does not end with {ACTION[q]!r}…{reason}… — {t.ctx()}")


BASE_FILES = {"a.py": "A = 1\n", "b.py": "import a\n", "tests/t.sh": "python3 b.py\n", "package.json": "{}\n"}


@case("X442", "WALK_INCOMPLETE_NAMES_REASON_AND_ACTION; failures GIT_UNAVAILABLE, NO_GOVERNED_REPOSITORY, "
              "REPOSITORY_UNREADABLE, PLANT_CONFIG_REFUSED, TEST_DECLARATION_UNAVAILABLE, INPUT_NOT_IN_INDEX")
def x442(base):
    problems = []
    reach = {"impact": ("dependents", ["b.py"]), "affected-tests": ("tests", ["tests/t.sh"])}
    p = Plant(base, "base", files=BASE_FILES)
    # (a) global-input: package.json is a §6 default global input.
    expect_incomplete(problems, "(a)", p, ["package.json"], "global-input", "package.json")
    # (b) input-not-found, beside an input whose rows are still listed.
    expect_incomplete(problems, "(b)", p, ["a.py", "nope.py"], "input-not-found", "nope.py",
                      queries=("impact", "affected-tests"), still=reach)
    # (c) ambiguous-input: two governed repositories hold tools/x.py.
    c = Plant(base, "two-repos", files={"README.md": "# r\n", "tests/t.sh": "echo t\n"},
              nested={"R1": {"tools/x.py": "X = 1\n"}, "R2": {"tools/x.py": "X = 2\n"}})
    expect_incomplete(problems, "(c)", c, ["tools/x.py"], "ambiguous-input", "tools/x.py",
                      candidates=["R1/tools/x.py", "R2/tools/x.py"])
    # (d) depth-cap: a chain of five files cut at depth 3, completed at depth 5.
    chain = {"f1.py": "F = 1\n", "f2.py": "import f1\n", "f3.py": "import f2\n", "f4.py": "import f3\n",
             "f5.py": "import f4\n", "tests/t.sh": "echo t\n"}
    dp = Plant(base, "chain", files=chain)
    expect_incomplete(problems, "(d)", dp, ["f1.py"], "depth-cap", "f4.py", queries=("impact", "affected-tests"),
                      extra=("--depth", "3"), still={"impact": ("dependents", ["f2.py", "f3.py", "f4.py"])})
    try:
        full = query(dp, "impact", "--depth", "5", "f1.py")
        if full.get("incomplete") != [] or "f5.py" not in row_paths(full, "dependents"):
            problems.append(f"(d) --depth 5 is not complete with f5.py: {full!r}")
    except CaseFail as e:
        problems.append(f"(d) --depth 5: {e}")
    # (e) config-refused: an unknown key refuses the whole file; the error is the detail.
    e = Plant(base, "refused", files=BASE_FILES, config={"exclude": [], "unknown_key": []})
    expect_incomplete(problems, "(e)", e, ["a.py"], "config-refused", CONFIG_PATH, still=reach)
    try:
        rec = [r for r in query(e, "impact", "a.py").get("incomplete", []) if r.get("reason") == "config-refused"]
        if rec and not rec[0].get("detail"):
            problems.append(f"(e) the config-refused record carries no error detail: {rec!r}")
    except CaseFail as ex:
        problems.append(f"(e) {ex}")
    # (f) git-unavailable: no git on PATH; an existing cache is left byte-identical.
    f = Plant(base, "no-git", files=BASE_FILES)
    try:
        query(f, "build")
        before = f.index.read_bytes() if f.index.is_file() else None
        if before is None:
            problems.append("(f) harness: the build with git wrote no cache")
        no_git = dict(ENV, PATH=str(NO_GIT_PATH))
        expect_incomplete(problems, "(f)", f, ["a.py"], "git-unavailable", env=no_git)
        if status(query(f, "impact", "a.py", env=no_git)) != "not-written":
            problems.append("(f) without git the cache status is not not-written")
        if before is not None and (not f.index.is_file() or f.index.read_bytes() != before):
            problems.append("(f) a query without git changed the existing cache")
    except CaseFail as ex:
        problems.append(f"(f) {ex}")
    # (g) no-test-declaration: no docs/graph/spec-lint.py; impact still answers.
    g = Plant(base, "no-engine", files=BASE_FILES, globs=None)
    expect_incomplete(problems, "(g)", g, ["a.py"], "no-test-declaration", queries=("affected-tests",))
    try:
        if query(g, "impact", "a.py").get("incomplete") != []:
            problems.append("(g) impact is incomplete when only the test declaration is missing")
    except CaseFail as ex:
        problems.append(f"(g) impact: {ex}")
    # (h) no-test-files: TEST_GLOBS matches no inventory file.
    h = Plant(base, "no-tests", files=BASE_FILES, globs=["nothing/**/*.*"])
    expect_incomplete(problems, "(h)", h, ["a.py"], "no-test-files", queries=("affected-tests",))
    # (i) no-repository: the plant root is no Git work tree and no repo: names one.
    i = Plant(base, "no-repo", files=BASE_FILES, git_init=False)
    expect_incomplete(problems, "(i)", i, ["a.py"], "no-repository")
    # (j) repository-unreadable: a nested repository with a corrupt index; the root still answers.
    j = Plant(base, "corrupt", files=BASE_FILES, nested={"vendor/lib": {"lib.py": "L = 1\n"}})
    (j.dir / "vendor" / "lib" / ".git" / "index").write_bytes(b"not a git index\n")
    expect_incomplete(problems, "(j)", j, ["a.py"], "repository-unreadable", "vendor/lib", still=reach)
    # (k) outside-plant: an input above the plant root.
    expect_incomplete(problems, "(k)", p, ["../elsewhere.py"], "outside-plant")
    check(not problems, " || ".join(problems))
    return ("eleven reasons, each one record with its subject, rows still listed, the query's action line; "
            "--depth 5 completes the chain --depth 3 cuts")


@case("X443", "AFFECTED_TESTS_ARE_THE_WALK_FILTERED")
def x443(base):
    p = Plant(base, files={"lib.py": "L = 1\n", "tool.py": "import lib\n", "tests/t.sh": "python3 tool.py\n",
                           "tests/lint.py": "import lib\n", "tests/test-lint.sh": "python3 tests/lint.py\n",
                           "tests/u_test.py": "U = 1\n", "tests/p_test.py": 'NAME = "lib.py"\n'})
    d = query(p, "affected-tests", "lib.py", "tests/u_test.py")
    got = [(r.get("path"), r.get("depth"), r.get("link"), r.get("via")) for r in d.get("tests", [])]
    want = [("tests/u_test.py", 0, "certain", ["tests/u_test.py"]),
            ("tests/lint.py", 1, "certain", ["lib.py", "tests/lint.py"]),
            ("tests/t.sh", 2, "certain", ["lib.py", "tool.py", "tests/t.sh"]),
            ("tests/test-lint.sh", 2, "certain", ["lib.py", "tests/lint.py", "tests/test-lint.sh"]),
            ("tests/p_test.py", 1, "maybe", ["lib.py", "tests/p_test.py"])]
    check(got == want, f"tests {got!r}, want (certain first, no non-test file) {want!r}")
    t = tool(p, "affected-tests", "lib.py", "tests/u_test.py")
    check(t.rc == 0 and t.last() == RECOMMEND_LINE, f"the text view does not end with RECOMMEND_LINE — {t.ctx()}")
    return "the walk filtered to tests, depth 0 to 2 with via paths, certain first; the recommendation line last"


@case("X444", "AFFECTED_ALWAYS_RUN_LISTED_APART")
def x444(base):
    p = Plant(base, files={"src/in.py": "I = 1\n", "src/other.py": "O = 1\n",
                           "tests/lone.sh": "echo lone\n", "tests/declared.sh": "python3 src/other.py\n",
                           "tests/both.sh": "python3 src/in.py\n",
                           "tests/opq.py": "import importlib\n\n\ndef f(n):\n    return importlib.import_module(n)\n",
                           "tests/fx.json": "{}\n", "tests/fx.md": "# fixture\n"},
              config={"always_run": ["tests/declared.sh", "tests/both.sh"]})
    d = query(p, "affected-tests", "src/in.py")
    problems = []
    if row_paths(d, "tests") != ["tests/both.sh"]:
        problems.append(f"tests {row_paths(d, 'tests')!r}: a test reached and declared is in tests only")
    ar = [(r.get("path"), r.get("reason")) for r in d.get("always_run", [])]
    if ar != [("tests/declared.sh", "declared"), ("tests/lone.sh", "no-code-edge")]:
        problems.append(f"always_run {ar!r}, want declared.sh (declared) and lone.sh (no-code-edge)")
    fl = [(r.get("path"), r.get("depth"), r.get("link"), r.get("found")) for r in d.get("floor", [])]
    if fl != [("tests/opq.py", 1, "maybe", "dynamic-nonliteral")]:
        problems.append(f"floor {fl!r}, want the opaque test at depth 1, maybe, dynamic-nonliteral")
    listed = row_paths(d, "tests") + [x[0] for x in ar] + row_paths(d, "floor")
    if {"tests/fx.json", "tests/fx.md"} & set(listed):
        problems.append(f"a JSON or Markdown fixture is listed: {listed!r}")
    check(not problems, " || ".join(problems))
    return "no-code-edge and declared tests apart, the opaque test in the floor, fixtures in no list"


# --- anchors --------------------------------------------------------------------
@case("X445", "ANCHORS_NAME_CITING_PAGES_OR_UNCITED")
def x445(base):
    src_a = "".join(f"# line {i}\n" for i in range(1, 12)) + "def run():\n    return 1\n"
    files = {"src/a.py": src_a, "lib/b.py": "B = 1\n",
             "docs/graph/nodes/n.md": node("subsystem.n", body="See `src/a.py:12` and `src/a.py#run`.\n"),
             "docs/graph/nodes/deep/leaf.md": "# leaf\n\nThe code is `../../../../src/a.py`.\n",
             "docs/graph/nodes/r1.md": node("subsystem.r1", repo="src/a.py"),
             "docs/graph/nodes/r2.md": node("subsystem.r2", repo="src/"),
             "docs/graph/nodes/r3.md": node("subsystem.r3", repo="src"),
             "docs/graph/plans/p.md": "# plan\n\nTouches `src/a.py`.\n",
             "docs/graph/specs/s.md": "# spec\n\nCovers `src/a.py`.\n",
             "docs/graph/decisions/d.md": "# decision\n\nAbout `src/a.py`.\n"}
    p = Plant(base, files=files)
    d = query(p, "anchors", "src/a.py", "lib/b.py")
    by = {f.get("path"): f for f in d.get("files", [])}
    problems = []
    a = by.get("src/a.py") or {}
    facts = sorted(((f.get("page"), f.get("line") if f.get("form") == "backtick" else "-", f.get("form"),
                     f.get("link"), f.get("found")) for f in a.get("facts", [])), key=repr)
    want = sorted([("docs/graph/nodes/n.md", 12, "backtick", "certain", "exact"),
                   ("docs/graph/nodes/n.md", None, "backtick", "certain", "exact"),
                   ("docs/graph/nodes/deep/leaf.md", None, "backtick", "certain", "exact"),
                   ("docs/graph/nodes/r1.md", "-", "repo", "certain", "exact"),
                   ("docs/graph/nodes/r2.md", "-", "repo", "maybe", "repo-prefix")], key=repr)
    if facts != want:
        problems.append(f"src/a.py facts {facts!r}, want {want!r} (r3.md, `repo: src`, claims nothing)")
    if a.get("history") != {"count": 3, "pages": []}:
        problems.append(f"src/a.py history {a.get('history')!r}, not three pages counted and none named")
    b = by.get("lib/b.py") or {}
    if b.get("uncited") is not True or b.get("facts"):
        problems.append(f"lib/b.py is not listed as uncited: {b!r}")
    try:
        al = {f.get("path"): f for f in query(p, "anchors", "--all", "src/a.py").get("files", [])}
        pages = sorted(((al.get("src/a.py") or {}).get("history") or {}).get("pages") or [])
        if pages != ["docs/graph/decisions/d.md", "docs/graph/plans/p.md", "docs/graph/specs/s.md"]:
            problems.append(f"with --all, history names {pages!r}, not the three pages")
    except CaseFail as e:
        problems.append(f"--all: {e}")
    check(not problems, " || ".join(problems))
    return ("certain backtick and repo facts, a maybe repo-prefix fact, a root repo: claims nothing; history "
            "counted, named with --all; lib/b.py uncited")


@case("X446", "ANCHORS_BASENAME_IS_MAYBE_AMBIGUOUS_IS_INCOMPLETE")
def x446(base):
    p = Plant(base, files={"a/run.py": "R = 1\n", "a/lint.py": "L = 1\n", "b/lint.py": "L = 2\n",
                           "docs/graph/nodes/nr.md": node("subsystem.nr", body="Run with `run.py`.\n"),
                           "docs/graph/nodes/nl.md": node("subsystem.nl", body="Lint with `lint.py`.\n")})
    d = query(p, "anchors", "a/run.py", "a/lint.py")
    by = {f.get("path"): f for f in d.get("files", [])}
    problems = []
    run = [(f.get("page"), f.get("link"), f.get("found")) for f in (by.get("a/run.py") or {}).get("facts", [])]
    if run != [("docs/graph/nodes/nr.md", "maybe", "basename")]:
        problems.append(f"a/run.py facts {run!r}, want the one maybe basename fact")
    lint = [f.get("page") for f in (by.get("a/lint.py") or {}).get("facts", [])]
    if "docs/graph/nodes/nl.md" in lint:
        problems.append(f"a/lint.py lists the ambiguous page: {lint!r}")
    recs = d.get("incomplete", [])
    if (len(recs) != 1 or recs[0].get("reason") != "ambiguous-citation"
            or recs[0].get("subject") != "docs/graph/nodes/nl.md"
            or sorted(recs[0].get("candidates") or []) != ["a/lint.py", "b/lint.py"]
            or "lint.py" not in str(recs[0].get("detail"))):
        problems.append(f"incomplete {recs!r}: not one ambiguous-citation record naming the page, the "
                        f"citation and both candidates")
    check(not problems, " || ".join(problems))
    return "a unique bare name is a maybe basename fact; an ambiguous one is an ambiguous-citation record"


# --- CLI and output -------------------------------------------------------------
@case("X447", "USAGE_REFUSED")
def x447(base):
    p = Plant(base, files={"a.py": "A = 1\n"})
    problems = []
    for args in (("frobnicate", "a.py"), ("impact", "--depth", "0", "a.py"), ("impact", "--depth", "6", "a.py"),
                 ("impact",), ("impact", "--bogus", "a.py")):
        r = tool(p, *args)
        if r.rc != 2 or r.out or r.err.count("\n") != 1:
            problems.append(f"{' '.join(args)}: not exit 2 with one stderr line and empty stdout — {r.ctx()}")
    if p.cache.exists():
        problems.append("a refused command line wrote the cache")
    r = tool(p, "--help")
    if r.rc != 0 or not r.out.strip():
        problems.append(f"--help does not print the usage and exit 0 — {r.ctx()}")
    check(not problems, " || ".join(problems))
    return "an unknown query or option, --depth 0 and 6, no path: exit 2, one stderr line; --help exits 0"


@case("X448", "OUTPUT_CARRIES_NO_RAW_CONTROL; failures UNSAFE_PATH_TEXT, NON_UTF8_PATH")
def x448(base):
    p = Plant(base, files={"a.py": "A = 1\n"}, commit=False)
    names = {b"esc\x1b.py": "esc\x1b.py", "rlo\u202e.py".encode(): "rlo\u202e.py", b"ff\xff.py": "ff\udcff.py"}
    for raw in names:
        with open(os.path.join(bytes(p.dir), raw), "wb") as fh:
            fh.write(b"import a\n")
    p.commit(".")
    problems = []
    t = tool(p, "impact", "a.py")
    bad = sorted({c for c in t.raw if not (32 <= c < 127 or c == 10)})
    if t.rc != 0 or bad:
        problems.append(f"the text view exits {t.rc} or carries bytes outside printable ASCII: {bad!r} — {t.ctx()}")
    for shown in ("esc?.py", "rlo?.py", "ff?.py"):
        if shown not in t.out:
            problems.append(f"the text view does not show {shown!r} — {t.ctx()}")
    j = tool(p, "impact", "a.py", "--json")
    if j.rc != 0 or any(c >= 128 for c in j.raw):
        problems.append(f"--json exits {j.rc} or is not ASCII — {j.ctx()}")
    else:
        try:
            got = sorted(row_paths(j.doc(), "dependents"))
            if got != sorted(names.values()):
                problems.append(f"--json dependents {got!r}, not the names Git reports {sorted(names.values())!r}")
        except CaseFail as e:
            problems.append(str(e))
    check(not problems, " || ".join(problems))
    return "ESC, U+202E and 0xFF names: the text view shows ?, --json escapes them to the names Git reports"


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
    print(f"SPEC-0007 source-index cases: FAIL — {len(failed)} case(s): {', '.join(failed)}", file=sys.stderr)
    sys.exit(1)
PY

[[ "$SI_RC" == 0 ]] || fail "SPEC-0007 source index: the case(s) named above failed"

echo "test-source-index: PASS"
