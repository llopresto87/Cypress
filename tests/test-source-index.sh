#!/usr/bin/env bash
# SPEC-0007 source index: tools/source-index.py (X425-X467, X470).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() { echo "FAIL: $*" >&2; exit 1; }

FO="$(mktemp -d)"
trap 'rm -rf "$FO"' EXIT

# `docs/graph/source-index.py` inventories a plant's code, links it, and walks
# those links in reverse to answer `impact`, `affected-tests` and `anchors`,
# reads definitions for `symbols`,
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
INDEX_SCHEMA = "cypress.source-index/2"
ANSWER_SCHEMA = "cypress.source-index.answer/1"
FILE_MAX_BYTES = 1048576
DIR_LINK_MAX = 200
CACHE_IGNORE = b"*\n"
CONFIG_PATH = "docs/graph/source-index.json"
FLOOR_LINE = "Floor: {n} maybe row(s) every input reaches (opaque holders and their dependents):"
RECOMMEND_LINE = ("Recommendation only: the tests above and the always-run set, never only these; "
                  "verify decides what runs.")
ACTION = {"build": "Incomplete: {n} setup item(s) above, each with its fix (", "impact": "Incomplete: check by hand (",
          "affected-tests": "Incomplete: run the full suite (", "anchors": "Incomplete: review by hand (",
          "symbols": "Incomplete: search by hand ("}

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
    # m4: a tracked directory replaced by a symlink to outside files; the plant's code does not change
    # when those files do, so the key holds.
    m4 = Plant(base, "symlinked", files={"d/a.py": "A = 1\n", "src/b.py": "B = 1\n"})
    outside = Path(base) / "m4-outside"
    write(outside, "a.py", "A = 2\n")
    shutil.rmtree(m4.dir / "d")
    (m4.dir / "d").symlink_to(outside)
    query(m4, "impact", "src/b.py")
    write(outside, "a.py", "A = 3\n")
    d4 = query(m4, "impact", "src/b.py")
    check(status(d4) == "reused", f"m4: after an edit beyond a symlinked directory the cache status is "
                                  f"{d4.get('cache')!r}, not reused")
    return ("the second query reuses the cache; index.json bytes and mtime unchanged; an edit beyond a "
            "symlinked directory leaves the key alone")


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
    inst = subprocess.run(["bash", str(SEED / "install.sh"), "all", "--project-dir", str(t), "--copy"],
                          capture_output=True, text=True, timeout=600, env=ENV)
    if inst.returncode != 0:
        raise HarnessFail(f"the re-install exited {inst.returncode}: {inst.stderr[-600:]}")
    check(placed.read_bytes() == TOOL.read_bytes(), "the re-install did not place the seed's tool")
    check("Cache: rebuilt (build forced)" in inst.stdout,
          f"the re-install's output holds no `Cache: rebuilt (build forced)`: {inst.stdout[-900:]!r}")
    d = query(P, "impact", "src/a.py")
    check(status(d) == "reused", f"after the install the cache status is {d.get('cache')!r}, not reused")
    return "an install over an older tool's cache rebuilds it with the seed's tool; the next query reuses it"


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


PY_J = """import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
U = ROOT / "tools" / "u.py"
V = os.path.join(ROOT, "tools", "v.py")


def kit(name):
    return ROOT / "templates" / "k" / name
"""
PY_JW = """from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = sorted((ROOT / "templates" / "k").glob("*.json"))
"""
SH_J = """#!/usr/bin/env bash
SEED="$1"
TMP="$2"
cp "$SEED"/tools/v.py "$TMP"
python3 - "$SEED" <<'EOF'
import sys
from pathlib import Path
SEED = Path(sys.argv[1])
TOOL = SEED / "tools" / "u.py"
EOF
"""
TS_E = """import path from "node:path";

export function where(root: string) {
  const hooks = path.join(__dirname, "..", "hooks");
  return [hooks, path.resolve(root, "tools", "u.py")];
}
"""


@case("X433", "LINK_PATH_LITERAL_AND_DIRECTORY_ARE_MAYBE; failure DIRECTORY_LITERAL_TOO_WIDE")
def x433(base):
    files = {"tools/t.py": PY_T, "tools/frontmatter.py": "F = 1\n", "templates/k/lint.py": "K = 1\n",
             "templates/k/a.json": "{}\n", "notes.md": "The tool is `tools/t.py`.\n", "tools/wide.py": PY_W,
             # path joins (§6 "Links"): one path literal written in pieces
             "tools/u.py": "U = 1\n", "tools/v.py": "V = 1\n", "src/hooks/h.py": "H = 1\n",
             "tools/j.py": PY_J, "tools/w.py": PY_JW, "tests/j.sh": SH_J, "src/ext/e.ts": TS_E,
             # an assignment word joining quoted and unquoted parts reads its value
             "src/lib.sh": "L=1\n", "src/s.sh": 'X="src"/lib.sh\n'}
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
    if links_of(d, "tools/wide.py"):
        problems.append(f"tools/wide.py holds {len(links_of(d, 'tools/wide.py'))} link(s): a root-like string or a "
                        f"directory over DIR_LINK_MAX must link nothing")
    op = [(r.get("reason")) for r in records(d, "opaque", "tools/wide.py")]
    if op != ["walks-tree"]:
        problems.append(f"tools/wide.py (a directory over DIR_LINK_MAX) is not one opaque walks-tree record: {op!r}")
    # joins: each join is one maybe path-literal link (or two directory links) at the line where it starts
    lit = lambda target, line: (target, "path-literal", "maybe", "path-literal", line)
    kit = lambda line: [("templates/k/lint.py", "path-literal", "maybe", "directory", line),
                        ("templates/k/a.json", "path-literal", "maybe", "directory", line)]
    J = lambda s: line_of(PY_J, s)
    joins = {
        "tools/j.py": sorted([lit("tools/u.py", J('"u.py"')), lit("tools/v.py", J('"v.py"'))] + kit(J('"k"'))),
        "tests/j.sh": sorted([lit("tools/u.py", line_of(SH_J, '"u.py"')), lit("tools/v.py", line_of(SH_J, "v.py"))]),
        "tools/w.py": sorted(kit(line_of(PY_JW, ".glob("))),
        "src/ext/e.ts": sorted([("src/hooks/h.py", "path-literal", "maybe", "directory", line_of(TS_E, '"hooks"')),
                                lit("tools/u.py", line_of(TS_E, '"u.py"'))]),
        "src/s.sh": [lit("src/lib.sh", 1)],
    }
    for holder, want_j in joins.items():
        got_j = link_set(d, holder)
        if got_j != want_j:
            problems.append(f"joins: {holder} links {got_j!r}, want {want_j!r}")
    if records(d, "opaque", "tools/w.py"):
        problems.append(f"joins: tools/w.py, a walk whose root is a join naming a directory, is opaque: "
                        f"{records(d, 'opaque', 'tools/w.py')!r}")
    check(not problems, " || ".join(problems))
    return ("two path-literal and two directory maybe links, each at its line; Markdown links nothing; a "
            "root string links nothing and a too-wide directory makes its holder opaque walks-tree; Python, "
            "shell and TS/JS path joins are one maybe link each (or directory links) at the join's line")


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
        # R1: an unmapped specifier (no `~` alias, no baseUrl); scheme-led and empty-join files of their own
        "src/app/r5.ts": 'import "~/x";\n',
        "src/app/own.ts": 'import { test } from "bun:test";\n',
        "py/own.py": 'WORK = None\n\n\ndef f(name):\n    return WORK / "scratch" / name\n',
        # m2: bases under a symlinked directory and an ungoverned nested work tree (made below)
        "src/app/r6.ts": 'import "./lnk/missing";\n',
        "src/app/r7.ts": 'import "./sub/missing";\n',
        "py/amb.py": "import app.main\n",
        "x1/app/main.py": "M = 1\n", "x2/app/main.py": "M = 2\n",
        # GIT_PATH_ARGUMENT: paths Git would read as options, pathspec magic or globs
        "src/app/g.ts": ('import "./--exec=x";\nimport "./:(top)q";\nimport "./*";\n'
                         'import "../../../../../outside";\n'),
        # FILE_NOT_REGULAR and INPUT_EXHAUSTS_A_PARSER
        "py/fifo.py": "F = 1\n",
        "py/big.py": big,
        "py/nul.py": b"import os\nX = '\x00'\n",
        # a test file, so the build's no-test-files record (the build report's) stays out of this case
        "tests/t_test.py": "T = 1\n",
    }
    p = Plant(base, files=files)
    write(p.dir, "src/app/.next/types/routes.d.ts", "export {};\n")   # ignored by Git
    (p.dir / "py" / "fifo.py").unlink()
    os.mkfifo(p.dir / "py" / "fifo.py")                                # a tracked file replaced by a FIFO
    (Path(base) / "m2-outside").mkdir()
    (p.dir / "src" / "app" / "lnk").symlink_to(Path(base) / "m2-outside")  # a symlinked directory
    (p.dir / "src" / "app" / "sub").mkdir()
    git(p.dir / "src" / "app" / "sub", "init", "-q")                   # a nested work tree no repo: names
    d = query(p, "build")
    problems = []
    for holder, reason in (("src/dyn.ts", "dynamic-nonliteral"), ("py/walker.py", "walks-tree"),
                           ("py/globber.py", "walks-tree"), ("py/oswalker.py", "walks-tree"),
                           ("py/rglobber.py", "walks-tree"), ("sh/finder.sh", "walks-tree"),
                           ("py/broken.py", "unreadable"), ("ext/u.ts", "alias-config-unavailable"),
                           ("src/app/r5.ts", "unmapped-specifier")):
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
                                      ("src/app/r4.ts", "asset", "src/app/a.css"),
                                      ("src/app/r6.ts", "relative-no-file", "src/app/lnk/missing"),
                                      ("src/app/r7.ts", "relative-no-file", "src/app/sub/missing")):
        got = [(r.get("reason"), r.get("base"), r.get("kind"), r.get("line")) for r in records(d, "unresolved", holder)]
        if got != [(reason, base_path, "import", 1)]:
            problems.append(f"{holder}: unresolved {got!r}, not [{(reason, base_path, 'import', 1)!r}]")
        if links_of(d, holder):
            problems.append(f"{holder}: holds links {links_of(d, holder)!r}")
    for holder in ("src/app/own.ts", "py/own.py"):
        held = links_of(d, holder) + records(d, "opaque", holder) + records(d, "unresolved", holder)
        if held:
            problems.append(f"R1: {holder} (a scheme-led specifier, a join naming nothing) holds {held!r}")
    amb = sorted((l.get("target"), l.get("link"), l.get("found")) for l in links_of(d, "py/amb.py"))
    if amb != [("x1/app/main.py", "maybe", "ambiguous"), ("x2/app/main.py", "maybe", "ambiguous")]:
        problems.append(f"py/amb.py: not two maybe ambiguous links, one per candidate: {amb!r}")
    g = sorted((r.get("reason"), r.get("base")) for r in records(d, "unresolved", "src/app/g.ts"))
    want_g = sorted([("relative-no-file", "src/app/--exec=x"), ("relative-no-file", "src/app/:(top)q"),
                     ("relative-no-file", "src/app/*"), ("outside-repository", None)])
    if g != want_g:
        problems.append(f"src/app/g.ts: unresolved {g!r}, want {want_g!r}")
    # The nested work tree arm m2 needs is correctly the build report's one
    # repository-unnamed record (X462 owns it); Git-hostile paths add none.
    inc = sorted((r.get("reason"), r.get("subject")) for r in d.get("incomplete", []))
    if inc != [("repository-unnamed", "src/app/sub")]:
        problems.append(f"paths Git could misread made the build incomplete: {d.get('incomplete')!r}, "
                        f"want only the unnamed nested work tree [('repository-unnamed', 'src/app/sub')]")
    for holder in ("py/fifo.py", "py/big.py", "py/nul.py"):
        got = [(r.get("reason"), r.get("line")) for r in records(d, "opaque", holder)]
        if got != [("unreadable", None)]:
            problems.append(f"{holder}: opaque {got!r}, not [('unreadable', None)]")
    inv = {r.get("path"): r for r in d.get("inventory", [])}
    if (inv.get("py/big.py") or {}).get("hash") != p.blob("py/big.py"):
        problems.append("py/big.py (over FILE_MAX_BYTES) lacks its blob hash in the inventory")
    # baseUrl: a specifier whose baseUrl probe misses, no `paths` pattern
    # matching it and no workspace package naming it, is unmapped-specifier
    b = Plant(base, "baseurl", files={"tsconfig.json": '{"compilerOptions": {"baseUrl": ".", '
                                                       '"paths": {"@/*": ["./src/*"]}}}\n',
                                      "src/x.ts": 'import "~/gone";\nimport "#internal";\nimport "Foo/bar";\n'})
    db = query(b, "build")
    got_b = sorted((r.get("reason"), r.get("line"), r.get("reference")) for r in records(db, "opaque", "src/x.ts"))
    want_b = [("unmapped-specifier", 1, "~/gone"), ("unmapped-specifier", 2, "#internal"),
              ("unmapped-specifier", 3, "Foo/bar")]
    if got_b != sorted(want_b):
        problems.append(f"baseUrl: src/x.ts opaque {got_b!r}, want {sorted(want_b)!r}")
    held_b = links_of(db, "src/x.ts") + records(db, "unresolved", "src/x.ts")
    if held_b:
        problems.append(f"baseUrl: src/x.ts holds {held_b!r}")
    check(not problems, " || ".join(problems))
    return ("five opaque holders (an unmapped specifier among them), six unresolved references with their "
            "bases, two ambiguous maybe links; a scheme-led specifier and an empty join hold nothing; a FIFO, "
            "an oversized and a NUL-byte file opaque unreadable; Git-hostile paths and bases Git cannot be "
            "asked about stay records beside the generated one")


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
    # D4: the floor part has no depth bound; only a cut in the input part is incomplete
    d1 = query(p, "impact", "--depth", "1", "a.py")
    fl1 = [(r.get("path"), r.get("depth")) for r in d1.get("floor", [])]
    if fl1 != [("o.py", 1), ("p.py", 2)]:
        problems.append(f"D4: --depth 1 floor {fl1!r}, want [('o.py', 1), ('p.py', 2)]")
    inc1 = [(r.get("reason"), r.get("subject")) for r in d1.get("incomplete", [])]
    if inc1 != [("depth-cap", "b.py")]:
        problems.append(f"D4: --depth 1 incomplete {inc1!r}, want exactly [('depth-cap', 'b.py')]")
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
            "for a.py; z.py's floor adds q.py; the text view prints the floor after its line; --depth 1 "
            "keeps the whole floor and cuts only b.py")


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
    # (m3) repository-unreadable from the listing alone: a git on PATH that fails only `ls-files` in the
    # nested repository, so its HEAD and status read and only the inventory's listing fails.
    m3 = Plant(base, "unlisted", files=BASE_FILES, nested={"vendor/lib": {"lib.py": "L = 1\n"}})
    shim = WORK / "git-shim-m3"
    shim.mkdir(exist_ok=True)
    write(shim, "git", "#!/bin/sh\ncase \"$(/bin/pwd -P)\" in */unlisted/vendor/lib)\n"
                       "  for a in \"$@\"; do [ \"$a\" = ls-files ] && exit 128; done;;\nesac\n"
                       f"exec {shutil.which('git')} \"$@\"\n")
    (shim / "git").chmod(0o755)
    expect_incomplete(problems, "(m3)", m3, ["a.py"], "repository-unreadable", "vendor/lib", still=reach,
                      env=dict(ENV, PATH=f"{shim}{os.pathsep}{ENV.get('PATH', '')}"))
    # (k) outside-plant: an input above the plant root.
    expect_incomplete(problems, "(k)", p, ["../elsewhere.py"], "outside-plant")
    check(not problems, " || ".join(problems))
    return ("eleven reasons, each one record with its subject, rows still listed, the query's action line "
            "(a nested repository whose listing alone fails names itself, not '.'); "
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
                   ("docs/graph/nodes/r2.md", "-", "repo", "maybe", "repo-prefix"),
                   ("docs/graph/nodes/r3.md", "-", "repo", "maybe", "repo-prefix")], key=repr)
    if facts != want:
        problems.append(f"src/a.py facts {facts!r}, want {want!r} (a folder claims, slash or not)")
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
    return ("certain backtick and repo facts, `repo: src/` and `repo: src` maybe repo-prefix facts; history "
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
    refused = [(("frobnicate", "a.py"), None), (("impact", "--depth", "0", "a.py"), None),
               (("impact", "--depth", "6", "a.py"), None), (("impact",), None), (("impact", "--bogus", "a.py"), None),
               # slice 2: --history and --moved where they do not belong, --moved beside a path,
               # anchors with neither, and symbols names NAME_RE refuses whole
               (("anchors", "--history", "a.py"), None), (("symbols", "--history", "A"), None),
               (("impact", "--moved"), None), (("anchors",), None), (("anchors", "--moved", "a.py"), None),
               (("anchors", "--moved", "-"), b"a.py\n"), (("symbols", "a..b"), None), (("symbols", "A\n"), None),
               (("symbols", "-"), b"a..b\n")]
    for args, stdin in refused:
        r = tool(p, *args, stdin=stdin)
        if r.rc != 2 or r.out or r.err.count("\n") != 1:
            problems.append(f"{' '.join(args)!r}: not exit 2 with one stderr line and empty stdout — {r.ctx()}")
    if p.cache.exists():
        problems.append("a refused command line wrote the cache")
    r = tool(p, "--help")
    if r.rc != 0 or not r.out.strip():
        problems.append(f"--help does not print the usage and exit 0 — {r.ctx()}")
    check(not problems, " || ".join(problems))
    return ("an unknown query or option, --depth 0 and 6, no path, misplaced --history and --moved, a refused "
            "name: exit 2, one stderr line; --help exits 0")


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


# --- slice 2: definitions, history, the moved list --------------------------------
def slice2(plant, feature, *args, stdin=None):
    """The `--json` answer of a slice-2 query; a usage refusal names the missing feature."""
    r = tool(plant, *args, "--json", stdin=stdin)
    check(r.rc != 2, f"`source-index.py {' '.join(args)} --json` is refused as usage (exit 2): {feature} "
                     f"is not built yet — {r.ctx()}")
    return r.doc()


def slice2_text(plant, feature, *args):
    r = tool(plant, *args)
    check(r.rc == 0, f"`source-index.py {' '.join(args)}` exits {r.rc}: {feature} — {r.ctx()}")
    return r


def defs_by_name(doc):
    return {n.get("name"): n for n in doc.get("names", [])}


def one_def(by, name, problems):
    n = by.get(name)
    if n is None:
        problems.append(f"`names` holds no entry for {name!r}")
        return None
    ds = n.get("definitions") or []
    if len(ds) != 1 or n.get("undefined") is not False:
        problems.append(f"{name!r} lists {len(ds)} definition(s), undefined={n.get('undefined')!r}, "
                        f"not one: {ds!r}")
        return None
    return ds[0]


def undefined(by, names, problems):
    for name in names:
        n = by.get(name)
        if n is None or n.get("definitions") or n.get("undefined") is not True:
            problems.append(f"{name!r} is not `undefined` with no definition: {n!r}")


PY_DEFS = ("TIMEOUT = 5\n"
           "A, B = 1, 2\n"
           "type Alias = int\n"
           "from os import path\n"
           "def run():\n"
           "    x = 1\n"
           "    def inner():\n"
           "        return x\n"
           "    return inner\n"
           "async def fetch():\n"
           "    return 1\n"
           "class Store:\n"
           "    LIMIT = 3\n"
           "    def save(self):\n"
           "        return self\n")


@case("X450", "SYMBOLS_PYTHON_DEFINITIONS_CERTAIN")
def x450(base):
    deep = "deep_expr = " + "+".join(["a"] * 1000) + "\ndef deep_ok():\n    return 1\n"
    p = Plant(base, files={"pkg/a.py": PY_DEFS, "deep.py": deep, "docs/graph/tool.py": "GRAPH_ONLY = 1\n"})
    names = ["TIMEOUT", "A", "Alias", "run", "inner", "fetch", "Store", "LIMIT", "save", "Store.save", "x", "path",
             "GRAPH_ONLY"]
    d = slice2(p, "the `symbols` query", "symbols", *names)
    by = defs_by_name(d)
    problems = []
    want = {"TIMEOUT": ("variable", "TIMEOUT = 5", "TIMEOUT"), "A": ("variable", "A, B = 1, 2", "A"),
            "Alias": ("type", "type Alias", "Alias"), "run": ("function", "def run(", "run"),
            "inner": ("function", "def inner(", "run.inner"), "fetch": ("function", "async def fetch(", "fetch"),
            "Store": ("class", "class Store", "Store"), "LIMIT": ("variable", "LIMIT = 3", "Store.LIMIT"),
            "save": ("function", "def save(", "Store.save"), "Store.save": ("function", "def save(", "Store.save")}
    for name, (kind, needle, qual) in want.items():
        got = one_def(by, name, problems)
        if got is None:
            continue
        exp = {"name": qual, "path": "pkg/a.py", "line": line_of(PY_DEFS, needle), "kind": kind,
               "link": "certain", "found": "ast"}
        if {k: got.get(k) for k in exp} != exp:
            problems.append(f"{name!r}: definition {got!r}, want {exp!r}")
    if by.get("save") and by.get("Store.save") and by["save"].get("definitions") != by["Store.save"].get("definitions"):
        problems.append("`Store.save` does not list the definition `save` lists")
    undefined(by, ["x", "path"], problems)
    if d.get("incomplete"):
        problems.append(f"incomplete {d.get('incomplete')!r}, not empty")
    # arm GRAPH_ONLY (§6 "Definitions"): the code-path rule bounds definitions, and the answer says so
    undefined(by, ["GRAPH_ONLY"], problems)
    if d.get("not_read") != NOT_READ:
        problems.append(f"arm GRAPH_ONLY: not_read {d.get('not_read')!r}, not {NOT_READ!r}")
    want_line = UNDEFINED_LINE.format(name="GRAPH_ONLY", not_read=", ".join(NOT_READ))
    t = slice2_text(p, "the `symbols` query", "symbols", "GRAPH_ONLY")
    if want_line not in t.lines():
        problems.append(f"arm GRAPH_ONLY: the text view does not print {want_line!r} — {t.ctx()}")
    # arm deep (§5): the reader never descends into expressions
    dd = slice2(p, "the `symbols` query", "symbols", "deep_ok")
    got = one_def(defs_by_name(dd), "deep_ok", problems)
    if got is not None and (got.get("path"), got.get("link"), got.get("found")) != ("deep.py", "certain", "ast"):
        problems.append(f"arm deep: deep_ok {got!r}, not one certain ast definition in deep.py")
    if any(r.get("subject") == "deep.py" for r in dd.get("incomplete", [])):
        problems.append(f"arm deep: an incomplete record names deep.py: {dd.get('incomplete')!r}")
    check(not problems, " || ".join(problems))
    return ("ten names each one certain ast definition with line, kind and qualified name; x and path "
            "undefined; GRAPH_ONLY undefined with not_read naming docs/graph/ and .cypress/; "
            "a 1,000-term expression leaves deep_ok readable")


SH_DEFS = ("place_file() {\n  :\n}\n"
           "function helper {\n  :\n}\n"
           "# fake() {\n"
           "cat <<'EOF'\nfunction hx() {\nEOF\n")
TS_DEFS = ("export function a() {}\n"
           "export default class B {}\n"
           "export const c = 1;\n"
           "let d = 2;\n"
           "export interface E {}\n"
           "type F = number;\n"
           "export enum G { X }\n"
           "export async function h() {}\n"
           "function i() {\n"
           "  const local = 1;\n"
           "  function nested() {}\n"
           "  return local;\n"
           "}\n"
           "namespace N {\n"
           "  export function ns() {}\n"
           "}\n"
           "// function z() {}\n"
           "/*\nfunction y() {}\n*/\n"
           "const a1 = 1, b1 = 2;\n"
           "const s = `\nfunction tx() {\n`;\n")


@case("X451", "SYMBOLS_LINE_READ_DECLARATIONS_ARE_MAYBE; failure LINE_READ_DECLARATION_IN_TEXT")
def x451(base):
    p = Plant(base, files={"install.sh": SH_DEFS, "src/m.ts": TS_DEFS})
    want = {"place_file": ("install.sh", "function", "place_file() {"),
            "helper": ("install.sh", "function", "function helper"),
            "a": ("src/m.ts", "function", "export function a("), "B": ("src/m.ts", "class", "class B"),
            "c": ("src/m.ts", "variable", "const c ="), "d": ("src/m.ts", "variable", "let d ="),
            "E": ("src/m.ts", "type", "interface E"), "F": ("src/m.ts", "type", "type F ="),
            "G": ("src/m.ts", "type", "enum G"), "h": ("src/m.ts", "function", "function h("),
            "i": ("src/m.ts", "function", "function i("), "ns": ("src/m.ts", "function", "function ns("),
            # arm text: a here-document line and a template-literal line read like declarations
            "hx": ("install.sh", "function", "function hx("), "tx": ("src/m.ts", "function", "function tx("),
            "a1": ("src/m.ts", "variable", "const a1")}
    none = ["local", "nested", "fake", "z", "y", "b1"]
    d = slice2(p, "the `symbols` query", "symbols", *want, *none)
    by = defs_by_name(d)
    problems = []
    for name, (path, kind, needle) in want.items():
        got = one_def(by, name, problems)
        if got is None:
            continue
        text = SH_DEFS if path == "install.sh" else TS_DEFS
        exp = {"name": name, "path": path, "line": line_of(text, needle), "kind": kind,
               "link": "maybe", "found": "line-reading"}
        if {k: got.get(k) for k in exp} != exp:
            problems.append(f"{name!r}: definition {got!r}, want {exp!r}")
    undefined(by, none, problems)
    check(not problems, " || ".join(problems))
    return ("shell functions and top-level or exported TS/JS declarations are maybe line-reading rows; "
            "indented locals, comments and a second declarator define nothing; text lines that read "
            "like a declaration are maybe rows")


@case("X452", "SYMBOLS_LIST_EVERY_DEFINITION")
def x452(base):
    files = {"tools/a.py": "def parse():\n    return 1\n", "tests/b.py": "def parse():\n    return 2\n",
             "tools/c.py": "class Reader:\n    def parse(self):\n        return 3\n",
             "src/p.ts": "function parse() {}\n"}
    p = Plant(base, files=files)
    d = slice2(p, "the `symbols` query", "symbols", "parse")
    problems = []
    n = defs_by_name(d).get("parse") or {}
    got = [(x.get("link"), x.get("path"), x.get("line"), x.get("name")) for x in n.get("definitions") or []]
    want = [("certain", "tests/b.py", 1, "parse"), ("certain", "tools/a.py", 1, "parse"),
            ("certain", "tools/c.py", 2, "Reader.parse"), ("maybe", "src/p.ts", 1, "parse")]
    if got != want:
        problems.append(f"parse lists {got!r}, want the three certain ones by path then the maybe one {want!r}")
    if d.get("incomplete"):
        problems.append(f"incomplete {d.get('incomplete')!r}, not empty")
    q = slice2(p, "the `symbols` query", "symbols", "Reader.parse")
    qn = defs_by_name(q).get("Reader.parse") or {}
    qgot = [(x.get("path"), x.get("name")) for x in qn.get("definitions") or []]
    if qgot != [("tools/c.py", "Reader.parse")]:
        problems.append(f"Reader.parse lists {qgot!r}, not the method alone")
    t = slice2_text(p, "the `symbols` text view", "symbols", "parse")
    lines = t.lines()
    want_lines = ["parse: 4 definition(s)",
                  "  certain function tests/b.py:1 parse (ast)",
                  "  certain function tools/a.py:1 parse (ast)",
                  "  certain function tools/c.py:2 Reader.parse (ast)",
                  "  maybe function src/p.ts:1 parse (line-reading)"]
    at = lines.index(want_lines[0]) if want_lines[0] in lines else -1
    if at < 0 or lines[at:at + 5] != want_lines:
        problems.append(f"the text view does not print the header and one line per definition "
                        f"{want_lines!r} — {t.ctx()}")
    check(not problems, " || ".join(problems))
    return "four definitions, certain first by path; a dotted name matches whole; one text line each"


@case("X453", "SYMBOLS_UNREADABLE_FILE_MAKES_IT_INCOMPLETE; failure DEFINITIONS_UNREADABLE")
def x453(base):
    big = "function run() {}\n" + "// pad\n" * (FILE_MAX_BYTES // 7 + 10)
    p = Plant(base, files={"ok.py": "def run():\n    return 1\n", "bad.py": "def run(:\n    return\n",
                           "big.js": big})
    d = slice2(p, "the `symbols` query", "symbols", "run")
    problems = []
    n = defs_by_name(d).get("run") or {}
    paths = [x.get("path") for x in n.get("definitions") or []]
    if paths != ["ok.py"]:
        problems.append(f"run lists {paths!r}, not the definition in ok.py alone")
    recs = sorted((r.get("reason"), r.get("subject")) for r in d.get("incomplete", []))
    if recs != [("unreadable-file", "bad.py"), ("unreadable-file", "big.js")]:
        problems.append(f"incomplete {d.get('incomplete')!r}, not one unreadable-file record each for "
                        f"bad.py and big.js")
    t = slice2_text(p, "the `symbols` text view", "symbols", "run")
    want = "Incomplete: search by hand (unreadable-file: bad.py, unreadable-file: big.js)."
    if t.last() != want:
        problems.append(f"the text view ends {t.last()!r}, not {want!r}")
    check(not problems, " || ".join(problems))
    return "ok.py listed; bad.py and big.js each an unreadable-file record; the text ends search by hand"


# History fixtures commit with fixed dates, the plant's own files first and apart.
HISTORY_MAX_FILES = 40


def dated_commit(repo, n, changes, msg="history"):
    """Write `changes` (path -> text) in `repo` and commit them at fixed date n."""
    for rel, text in changes.items():
        write(repo, rel, text)
    git(repo, "add", "-A", "--", *changes)
    stamp = f"2026-01-01T00:{n:02d}:00+0000"
    env = dict(ENV, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    r = subprocess.run(["git", *FIXTURE_GIT, "commit", "-qm", msg], cwd=str(repo), capture_output=True,
                       timeout=30, env=env)
    if r.returncode != 0:
        raise HarnessFail(f"git commit in {repo}: {r.stderr.decode(errors='replace')}")


def history_row(doc, path):
    rows = [r for r in doc.get("history", []) if r.get("path") == path]
    return rows[0] if len(rows) == 1 else None


@case("X454", "HISTORY_ROWS_ARE_MAYBE_WITH_THEIR_COUNT; failure HISTORY_BULK_COMMIT")
def x454(base):
    wide = {f"w/f{i:02d}.py": f"F{i} = 0\n" for i in range(1, HISTORY_MAX_FILES)}
    files = {"a.py": "A = 0\n", "c.py": "C = 0\n", "lib.py": "L = 0\n",
             "tests/t_b.sh": "python3 lib.py\n", "tests/t_wide.sh": "python3 lib.py\n", **wide}
    p = Plant(base, files=files)
    dated_commit(p.dir, 1, {"a.py": "A = 1\n", "tests/t_b.sh": "python3 lib.py\n# 1\n"})
    dated_commit(p.dir, 2, {"a.py": "A = 2\n", "tests/t_b.sh": "python3 lib.py\n# 2\n", "c.py": "C = 2\n"})
    dated_commit(p.dir, 3, {"a.py": "A = 3\n"})
    bulk = {"a.py": "A = 4\n", "tests/t_wide.sh": "python3 lib.py\n# 4\n",
            **{k: v + "# 4\n" for k, v in wide.items()}}
    check(len(bulk) == HISTORY_MAX_FILES + 1, "fixture: the bulk commit is a.py and HISTORY_MAX_FILES others")
    dated_commit(p.dir, 4, bulk)
    problems = []
    at = slice2(p, "the `--history` option", "affected-tests", "a.py", "--history")
    hist = [(r.get("path"), r.get("depth"), r.get("link"), r.get("kind"), r.get("found"), r.get("from"),
             r.get("together")) for r in at.get("history", [])]
    want = [("tests/t_b.sh", 1, "maybe", "history", "history", "a.py", {"count": 2, "of": 3})]
    if hist != want:
        problems.append(f"affected-tests history {hist!r}, want {want!r}")
    im = slice2(p, "the `--history` option", "impact", "a.py", "--history")
    ih = [(r.get("path"), r.get("link"), r.get("together")) for r in im.get("history", [])]
    iwant = [("tests/t_b.sh", "maybe", {"count": 2, "of": 3}), ("c.py", "maybe", {"count": 1, "of": 3})]
    if ih != iwant:
        problems.append(f"impact history {ih!r}, want t_b.sh then c.py, higher count first {iwant!r}")
    for d in (at, im):
        if any(r.get("link") == "certain" for r in d.get("history", [])):
            problems.append("a history row is certain")
        for key in ("dependents", "tests", "floor", "history"):
            if "tests/t_wide.sh" in row_paths(d, key):
                problems.append(f"tests/t_wide.sh (only in the bulk commit) is in `{key}`")
        if "tests/t_wide.sh" in [x.get("path") for x in d.get("always_run", [])]:
            problems.append("tests/t_wide.sh is in `always_run`")
    check(not problems, " || ".join(problems))
    return "t_b.sh 2 of 3, c.py 1 of 3, every row maybe; the bulk commit read for no count and no of"


@case("X455", "HISTORY_ONLY_ADDS")
def x455(base):
    files = {"a.py": "A = 0\n", "b.py": "import a\n", "o.py": "import os\nfor _ in os.walk(root):\n    pass\n",
             "d.py": "D = 0\n"}
    p = Plant(base, files=files)
    for n in (1, 2):
        dated_commit(p.dir, n, {k: v + f"# {n}\n" for k, v in files.items()})
    plain = query(p, "impact", "a.py")
    hist = slice2(p, "the `--history` option", "impact", "a.py", "--history")
    problems = []
    if "history" in plain:
        problems.append(f"the plain answer holds a `history` key: {plain.get('history')!r}")
    strip = lambda doc: {k: v for k, v in doc.items() if k not in ("cache", "history")}
    if strip(plain) != strip(hist):
        problems.append(f"the --history answer differs from the plain one outside `history` and `cache`: "
                        f"plain {strip(plain)!r}, history {strip(hist)!r}")
    if row_paths(hist, "history") != ["d.py"]:
        problems.append(f"history {row_paths(hist, 'history')!r}, not d.py alone (b.py in dependents, "
                        f"o.py in floor)")
    check(not problems, " || ".join(problems))
    return "--history equals the plain answer but for history and cache; history holds d.py alone"


@case("X456", "HISTORY_SHALLOW_OR_MISSING_IS_INCOMPLETE; failures HISTORY_SHALLOW, HISTORY_UNAVAILABLE")
def x456(base):
    files = {"a.py": "A = 0\n", "lib.py": "L = 0\n",
             "tests/t_old.sh": "python3 lib.py\n", "tests/t_new.sh": "python3 lib.py\n"}
    origin = Plant(base, "origin", files=files)
    dated_commit(origin.dir, 1, {"a.py": "A = 1\n", "tests/t_old.sh": "python3 lib.py\n# 1\n"})
    dated_commit(origin.dir, 2, {"a.py": "A = 2\n"})
    dated_commit(origin.dir, 3, {"a.py": "A = 3\n", "tests/t_new.sh": "python3 lib.py\n# 3\n"})
    git(base, "clone", "-q", "--depth", "2", f"file://{origin.dir}", "shallow")
    shallow = Plant.__new__(Plant)
    shallow.dir = Path(base) / "shallow"
    check(git(shallow.dir, "rev-parse", "--is-shallow-repository").strip() == "true",
          "fixture: the file:// --depth 2 clone is not shallow")
    empty = Plant(base, "empty", files={"a.py": "A = 0\n", "lib.py": "L = 0\n",
                                        "tests/t.sh": "python3 lib.py\n"}, commit=False)
    problems = []
    for arm, plant, reason in (("a", shallow, "history-shallow"), ("b", empty, "history-unavailable")):
        try:
            d = slice2(plant, "the `--history` option", "affected-tests", "a.py", "--history")
        except CaseFail as e:
            problems.append(f"arm ({arm}): {e}")
            continue
        recs = [(r.get("reason"), r.get("subject")) for r in d.get("incomplete", [])]
        if recs != [(reason, ".")]:
            problems.append(f"arm ({arm}): incomplete {d.get('incomplete')!r}, not one {reason} record naming .")
        if arm == "a":
            h = [(r.get("path"), r.get("together")) for r in d.get("history", [])]
            if h != [("tests/t_new.sh", {"count": 1, "of": 1})]:
                problems.append(f"arm (a): history {h!r}, want t_new.sh 1 of 1 and no t_old.sh "
                                f"(the boundary commit is not read)")
        t = tool(plant, "affected-tests", "a.py", "--history")
        if t.rc != 0 or not t.last().startswith(ACTION["affected-tests"]) or reason not in t.last():
            problems.append(f"arm ({arm}): the text view does not end with the affected-tests action naming "
                            f"{reason} — {t.ctx()}")
        plain = query(plant, "affected-tests", "a.py")
        if {"history-shallow", "history-unavailable"} & set(reasons(plain)) or "history" in plain:
            problems.append(f"arm ({arm}): without --history the answer reads history: {plain!r}")
    check(not problems, " || ".join(problems))
    return ("a shallow clone is history-shallow, its boundary commit unread; no commit is "
            "history-unavailable; neither without --history")


# The moved list: the plant places the seed's code-anchor.py beside the tool.
CODE_ANCHOR = SEED / "tools" / "code-anchor.py"
MOVED_NONE_LINE = "Moved: no code moved since the code anchor."
NOT_READ = ["docs/graph/", ".cypress/"]          # source_paths.NOT_CODE, in its order
UNDEFINED_LINE = ("{name}: no definition (read: Python definitions, shell functions, TS/JS declarations; "
                  "not read: {not_read}, which are not code)")


def moved_plant(base, name="plant"):
    """The plant of ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS, its anchor recorded."""
    files = {"run.sh": "echo run\n", "docs/graph/code-anchor.py": CODE_ANCHOR.read_text(),
             "docs/graph/nodes/cx.md": node("subsystem.cx", body="See `Cypress/tools/x.py`.\n"),
             "docs/graph/nodes/cr.md": node("subsystem.cr", body="Run `run.sh`.\n")}
    p = Plant(base, name, files=files, nested={"Cypress": {"tools/x.py": "X = 1\n"}})
    record(p)
    return p


def record(plant):
    r = subprocess.run([sys.executable, "docs/graph/code-anchor.py", "--record"], cwd=str(plant.dir),
                       capture_output=True, timeout=60, env=ENV)
    if r.returncode != 0:
        raise HarnessFail(f"code-anchor.py --record: exit {r.returncode}: {r.stderr.decode(errors='replace')}")


@case("X457", "ANCHORS_MOVED_EQUALS_THE_NAMED_PATHS")
def x457(base):
    p = moved_plant(base)
    sub = p.dir / "Cypress"
    write(sub, "tools/x.py", "X = 2\n")
    git(sub, "commit", "-qam", "move x")
    write(p.dir, "run.sh", "echo moved\n")
    moved = slice2(p, "the `--moved` input", "anchors", "--moved")
    named = query(p, "anchors", "Cypress/tools/x.py", "run.sh")
    problems = []
    if without_cache(moved) != without_cache(named):
        problems.append(f"anchors --moved {without_cache(moved)!r} differs from the named paths "
                        f"{without_cache(named)!r} outside `cache`")
    if sorted(i.get("path") for i in moved.get("inputs", [])) != ["Cypress/tools/x.py", "run.sh"]:
        problems.append(f"--moved inputs {moved.get('inputs')!r}, not Cypress/tools/x.py and run.sh")
    record(p)
    none = slice2(p, "the `--moved` input", "anchors", "--moved")
    if none.get("inputs") or none.get("files") or none.get("incomplete"):
        problems.append(f"after a second --record: inputs {none.get('inputs')!r}, files {none.get('files')!r}, "
                        f"incomplete {none.get('incomplete')!r}, not all empty")
    t = tool(p, "anchors", "--moved")
    if t.rc != 0 or MOVED_NONE_LINE not in t.lines():
        problems.append(f"the text view does not print {MOVED_NONE_LINE!r} — {t.ctx()}")
    check(not problems, " || ".join(problems))
    return "--moved equals the named moved paths but for cache; after a new record, empty and complete"


@case("X458", "ANCHORS_MOVED_WITHOUT_A_LIST_IS_INCOMPLETE; failures MOVED_LIST_UNAVAILABLE, "
              "MOVED_REPOSITORY_UNVERIFIED")
def x458(base):
    problems = []

    def arm(name, plant, reason, subject, detail, inputs):
        try:
            d = slice2(plant, "the `--moved` input", "anchors", "--moved")
        except CaseFail as e:
            problems.append(f"arm ({name}): {e}")
            return
        recs = d.get("incomplete", [])
        if (len(recs) != 1 or (recs[0].get("reason"), recs[0].get("subject")) != (reason, subject)
                or detail not in str(recs[0].get("detail"))):
            problems.append(f"arm ({name}): incomplete {recs!r}, not one {reason} record naming {subject} "
                            f"with a detail holding {detail!r}")
        got = sorted(i.get("path") for i in d.get("inputs", []))
        if got != inputs or sorted(f.get("path") for f in d.get("files", [])) != inputs:
            problems.append(f"arm ({name}): inputs {got!r} or files not {inputs!r}")
        t = tool(plant, "anchors", "--moved")
        if t.rc != 0 or not t.last().startswith(ACTION["anchors"]):
            problems.append(f"arm ({name}): the text view does not end with the anchors action — {t.ctx()}")
        if "Traceback" in t.err:
            problems.append(f"arm ({name}): the query printed a traceback — {t.ctx()}")

    a = moved_plant(base, "no-anchor")
    (a.dir / ".cypress" / "anchor.json").unlink()
    arm("a", a, "moved-unavailable", ".cypress/anchor.json", "anchor.json", [])
    b = moved_plant(base, "lacks-commit")
    path = b.dir / ".cypress" / "anchor.json"
    doc = json.loads(path.read_text())
    for e in doc["repositories"]:
        if e["path"] == "Cypress":
            e["commit"] = "0123456789abcdef0123456789abcdef01234567"
    path.write_text(json.dumps(doc, indent=2) + "\n")
    write(b.dir, "run.sh", "echo edited\n")
    arm("b", b, "moved-unverified", "Cypress", "unverified", ["run.sh"])
    c = moved_plant(base, "no-code-anchor")
    (c.dir / "docs" / "graph" / "code-anchor.py").unlink()
    arm("c", c, "moved-unavailable", "docs/graph/code-anchor.py", "", [])
    d = moved_plant(base, "old-code-anchor")
    # a code-anchor placed before slice 2: no moved_list
    write(d.dir, "docs/graph/code-anchor.py", CODE_ANCHOR.read_text()
          + '\nif "moved_list" in globals():\n    del moved_list\n')
    arm("d", d, "moved-unavailable", "docs/graph/code-anchor.py", "", [])
    # (e) a malformed result: `paths` a string, never one input per character (a name with no `/` or `.`,
    # so no character is itself an unclean path)
    e = moved_plant(base, "str-paths")
    write(e.dir, "docs/graph/code-anchor.py", CODE_ANCHOR.read_text()
          + '\ndef moved_list(root):\n    return [(".", [("moved", "run")])]\n')
    arm("e", e, "moved-unavailable", "docs/graph/code-anchor.py", "", [])
    # (f) Unrecorded from a code-anchor with no ANCHOR_NAME: the subject read inside the guard, its fallback
    f = moved_plant(base, "no-anchor-name")
    write(f.dir, "docs/graph/code-anchor.py", CODE_ANCHOR.read_text()
          + '\ndef moved_list(root):\n    raise Unrecorded("no anchor here")\n'
          + '\ndel ANCHOR_NAME\n')
    arm("f", f, "moved-unavailable", ".cypress/anchor.json", "no anchor here", [])
    check(not problems, " || ".join(problems))
    return ("no anchor, a code-anchor absent, older than moved_list, with a string for paths or with no "
            "ANCHOR_NAME: moved-unavailable, no traceback; a recorded commit the clone lacks: moved-unverified "
            "with run.sh still answered; each ends review by hand")


# One claim rule: the plant places the seed's graph-lint.py beside the tool, so
# the router and `anchors` read the same `repo:` values through the helper.
GRAPH_LINT = SEED / "templates" / "knowledge-graph" / "graph-lint.py"
PLAN_SCHEMA = "cypress.plan/1"
REPO_UNRESOLVED_DETAIL = "repo: {value} names nothing on disk; correct the node's repo:"
HELPER_ABSENT_NOTICE = {"code": "inference_skipped", "text": "inference skipped: HelperUnavailable"}


def route(plant, task, timeout=30):
    """The `graph-lint.py --plan-json` document for `task`, which must exit 0 in `timeout` s."""
    try:
        r = subprocess.run([sys.executable, "docs/graph/graph-lint.py", f"--plan-json={task}"],
                           cwd=str(plant.dir), capture_output=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        raise CaseFail(f"`graph-lint.py --plan-json={task}` ran past {timeout} s")
    run = Run(r.returncode, r.stdout, r.stderr.decode("utf-8", "replace"))
    check(run.rc == 0, f"`graph-lint.py --plan-json={task}` must exit 0 — {run.ctx()}")
    try:
        d = json.loads(run.out)
    except ValueError:
        raise CaseFail(f"`graph-lint.py --plan-json={task}` printed no JSON document — {run.ctx()}")
    check(d.get("schema") == PLAN_SCHEMA, f"the plan's schema is not {PLAN_SCHEMA!r} — {run.ctx()}")
    return d


def named(doc):
    """The ids the route loads by `named_path`."""
    return sorted(e.get("id") for e in doc.get("load", []) if (e.get("how") or {}).get("kind") == "named_path")


def repo_facts(doc, path):
    f = next((f for f in doc.get("files", []) if f.get("path") == path), {})
    return sorted((x.get("page"), x.get("link"), x.get("found")) for x in f.get("facts", [])
                  if x.get("form") == "repo")


def uncited(doc, path):
    f = next((f for f in doc.get("files", []) if f.get("path") == path), {})
    return f.get("uncited") is True and not f.get("facts")


def unresolved(doc):
    return sorted((r.get("subject"), r.get("detail")) for r in doc.get("incomplete", [])
                  if r.get("reason") == "repo-unresolved")


def claim_plant(base, name, values, files, nested=None):
    """A plant holding one node per `repo:` value (`values` maps a node name to it) and the seed's
    graph-lint.py beside the tool and its siblings."""
    files = dict(files)
    for n, v in values.items():
        files[f"docs/graph/nodes/{n}.md"] = node(f"subsystem.{n}", repo=v)
    files["docs/graph/graph-lint.py"] = GRAPH_LINT.read_text()
    return Plant(base, name, files=files, nested=nested, commit=False)


@case("X459", "REPO_CLAIM_READ_ALIKE_BY_ROUTER_AND_ANCHORS; failures REPO_VALUE_UNRESOLVED, "
              "HELPER_ABSENT_BESIDE_GRAPH_LINT")
def x459(base):
    problems = []

    def arm(name, fn):
        try:
            fn()
        except CaseFail as e:
            problems.append(f"arm ({name}): {e}")

    page = "docs/graph/nodes/{}.md".format
    values = {"pfile": "src/lib/a.py", "pslash": "src/lib/", "pdir": "src", "pcmake": "CMakeLists.txt",
              "rdot": ".", "oout": "../elsewhere", "uold": "old/lib", "ugone": "gone", "ucase": "Src",
              "esub": "vendor/sub"}
    p = claim_plant(base, "plant", values,
                    {"src/lib/a.py": "A = 1\n", "src/lib/c.py": "C = 1\n", "src/b.py": "B = 1\n",
                     "CMakeLists.txt": "project(x)\n"},
                    nested={"vendor/x": {"y.py": "Y = 1\n"}})     # node subsystem.repo0, `repo: vendor/x`
    p.commit(".")
    (p.dir / "vendor" / "sub").mkdir(parents=True)        # empty, created after commit: an unresolved dir
    # Platform probe (SPEC-0007 §10): a value whose case differs from disk names
    # nothing only on a case-sensitive file system; elsewhere the case checks skip.
    probe = write(p.dir, "probe", "probe\n")
    case_sensitive = not (p.dir / "PROBE").exists()
    probe.unlink()
    if not case_sensitive:
        print("  X459: case-insensitive file system (stat of PROBE found probe): arm case and the "
              "`repo: Src` record of arm unresolved skipped")
    inputs = ("src/lib/a.py", "src/lib/c.py", "src/b.py", "CMakeLists.txt", "vendor/x/y.py")
    holder = {}

    def anchors_doc():
        if "d" not in holder:
            holder["d"] = query(p, "anchors", *inputs)
        return holder["d"]

    def path_arm():
        d = anchors_doc()
        want = {"src/lib/a.py": [(page("pfile"), "certain", "exact"), (page("pslash"), "maybe", "repo-prefix"),
                                 (page("pdir"), "maybe", "repo-prefix")],
                "src/lib/c.py": [(page("pslash"), "maybe", "repo-prefix"), (page("pdir"), "maybe", "repo-prefix")],
                "src/b.py": [(page("pdir"), "maybe", "repo-prefix")],
                "CMakeLists.txt": [(page("pcmake"), "certain", "exact")]}
        for path, w in want.items():
            got = repo_facts(d, path)
            check(got == sorted(w), f"anchors: {path} repo facts {got!r}, want {sorted(w)!r}")
        for path, ids in (("src/lib/a.py", ["subsystem.pfile"]), ("src/lib/c.py", ["subsystem.pslash"]),
                          ("src/b.py", ["subsystem.pdir"]), ("CMakeLists.txt", ["subsystem.pcmake"])):
            got = named(route(p, f"edit {path}"))
            check(got == ids, f"router: `edit {path}` loads {got!r} by named_path, want {ids!r}")

    def root_outside_arm():
        d = anchors_doc()
        check(uncited(d, "vendor/x/y.py"),
              f"anchors: vendor/x/y.py is not uncited: {repo_facts(d, 'vendor/x/y.py')!r}")
        subjects = [s for s, _ in unresolved(d)]
        for n in ("rdot", "oout", "repo0"):
            check(page(n) not in subjects, f"anchors: the {values.get(n, 'vendor/x')!r} node adds an "
                                           f"incomplete record: {d.get('incomplete')!r}")
        got = named(route(p, "edit vendor/x/y.py"))
        check(got == [], f"router: `edit vendor/x/y.py` loads {got!r} by named_path, want none")

    def unresolved_arm():
        d = anchors_doc()
        want = sorted((page(n), REPO_UNRESOLVED_DETAIL.format(value=values[n]))
                      for n in ("uold", "ugone", "ucase", "esub") if case_sensitive or n != "ucase")
        check(unresolved(d) == want, f"anchors: repo-unresolved records {unresolved(d)!r}, want {want!r}")
        t = tool(p, "anchors", *inputs)
        check(t.rc == 0 and t.last().startswith(ACTION["anchors"]),
              f"anchors: the text view does not end with the anchors action — {t.ctx()}")
        doc = route(p, "edit old/lib/z.py")
        check(named(doc) == ["subsystem.uold"], f"router: `edit old/lib/z.py` loads {named(doc)!r} by "
                                                f"named_path, want ['subsystem.uold']")
        for task in ("edit old/lib/z.py", "edit src/b.py"):
            loud = [n for n in route(p, task).get("notices", []) if n.get("code") != "no_signal"]
            check(not loud, f"router: `{task}` adds notices {loud!r}, want none for any repo: value")

    def case_arm():
        if not case_sensitive:
            return
        d = anchors_doc()
        for path in inputs:
            check(page("ucase") not in [f[0] for f in repo_facts(d, path)],
                  f"anchors: `repo: Src` claims {path}")
        got = named(route(p, "edit SRC/b.py"))
        check(got == ["subsystem.pdir"], f"router: `edit SRC/b.py` loads {got!r} by named_path, "
                                         f"want ['subsystem.pdir'] (the router folds case)")

    def helper_absent_arm():
        h = claim_plant(base, "no-helper", {"hslash": "src/lib/"}, {"src/lib/a.py": "A = 1\n"})
        (h.dir / "docs" / "graph" / "source_paths.py").unlink()
        h.commit(".")
        doc = route(h, "edit src/lib/a.py")
        check(HELPER_ABSENT_NOTICE in doc.get("notices", []),
              f"router: notices {doc.get('notices')!r} do not hold {HELPER_ABSENT_NOTICE!r}")
        check(named(doc) == [], f"router: with no helper, `edit src/lib/a.py` loads {named(doc)!r} by "
                                f"named_path, want none")

    def relative_plant_arm():
        """`repo_kind` on a relative plant ('.', run from inside it) agrees with
        the absolute call: both decide on the same resolved target (SPEC-0007's
        abspath fix for a relative root)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("source_paths_relcheck", SEED / "tools" / "source_paths.py")
        sp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sp)
        abs_kind = sp.repo_kind(p.dir, values["pdir"])
        cwd = os.getcwd()
        try:
            os.chdir(p.dir)
            rel_kind = sp.repo_kind(".", values["pdir"])
        finally:
            os.chdir(cwd)
        check(rel_kind == abs_kind, f"repo_kind('.', {values['pdir']!r}) = {rel_kind!r} from inside the "
                                    f"plant, want {abs_kind!r} (same as the absolute call)")

    # security arms (security-D): an absolute value outside, a symlink out, a FIFO
    outside = base / "outside"
    outside.mkdir()
    git(outside, "init", "-q")
    write(outside, "z.py", "Z = 1\n")
    git(outside, "add", "-A")
    git(outside, "commit", "-qm", "outside")
    s = claim_plant(base, "security", {"dproc": "/proc/self", "dlink": "link-out", "dpipe": "pipe"},
                    {"proc/self/x.py": "P = 1\n", "m.py": "M = 1\n"})
    (s.dir / "link-out").symlink_to(outside, target_is_directory=True)
    s.commit(".")
    os.mkfifo(s.dir / "pipe")
    sec = {}

    def sec_doc():
        if "d" not in sec:
            sec["d"] = query(s, "anchors", "proc/self/x.py", "m.py")
        return sec["d"]

    def d4_arm():
        d = sec_doc()
        check(uncited(d, "proc/self/x.py"), f"anchors: `repo: /proc/self` claims proc/self/x.py: "
                                            f"{repo_facts(d, 'proc/self/x.py')!r}")
        check(page("dproc") not in [x for x, _ in unresolved(d)], f"anchors: `repo: /proc/self` adds an "
                                                                 f"incomplete record: {d.get('incomplete')!r}")
        got = named(route(s, "edit proc/self/status"))
        check(got == [], f"router: `edit proc/self/status` loads {got!r} by named_path, want none "
                         f"(`/proc/self` is outside)")

    def d5_arm():
        d = sec_doc()
        check(page("dlink") not in [x for x, _ in unresolved(d)], f"anchors: `repo: link-out` adds an "
                                                                 f"incomplete record: {d.get('incomplete')!r}")
        b = query(s, "build")
        under = [r.get("path") for r in b.get("inventory", []) if str(r.get("path")).startswith("link-out/")]
        check(not under, f"build inventories {under!r} under the symlink out of the plant")
        repos = (json.loads(s.index.read_text()).get("key") or {}).get("repositories") or []
        check(all((r.get("path") if isinstance(r, dict) else r) != "link-out" for r in repos),
              f"link-out is a governed repository: {repos!r}")
        got = named(route(s, "edit link-out/z.py"))
        check(got == [], f"router: `edit link-out/z.py` loads {got!r} by named_path, want none")

    def d6_arm():
        d = sec_doc()
        want = [(page("dpipe"), REPO_UNRESOLVED_DETAIL.format(value="pipe"))]
        check(unresolved(d) == want, f"anchors: repo-unresolved records {unresolved(d)!r}, want {want!r} "
                                     f"(a FIFO names nothing)")
        route(s, "edit pipe/x.py", timeout=20)

    for name, fn in (("path", path_arm), ("root+outside", root_outside_arm), ("unresolved", unresolved_arm),
                     ("case", case_arm), ("helper-absent", helper_absent_arm),
                     ("relative-plant", relative_plant_arm), ("D4 /proc/self", d4_arm),
                     ("D5 link-out", d5_arm), ("D6 FIFO", d6_arm)):
        arm(name, fn)
    check(not problems, " || ".join(problems))
    return ("a file or non-empty folder claims, slash or not; the root, a nested repository and outside "
            "values claim nothing; a value naming nothing reads as before and is repo-unresolved; the router "
            "folds case; no helper: inference skipped; /proc/self, a symlink out and a FIFO are safe")


# --- surfacing (8.1.2) ----------------------------------------------------------
import re

# §6 "Build report" texts, used by value; tools/source-index.py, install.sh and
# the seed skill are their homes.
BUILD_TIME_RE = r"Built in \d+\.\d\d s\."
BUILD_FIX = {
    "no-repository": ("the plant root is not a Git work tree and no node's repo: names a repository: if the "
                      "code lives in repositories below the plant root, let grow write the nodes whose repo: "
                      "names each (or write them); if the plant root is the code, run git init there and "
                      "commit; then run python3 docs/graph/source-index.py build"),
    "config-refused": ("fix docs/graph/source-index.json: only the keys exclude, always_run and global_inputs, "
                       "each a list of strings; or delete the file to use the defaults"),
    "no-test-declaration": ("set TEST_GLOBS in docs/graph/spec-lint.py to a list of the plant's test-file "
                            "patterns (the owner confirms it; grow asks it with the plant facts)"),
    "repo-unresolved": ("set the node's repo: to one plant-relative path that exists (a repository, a folder "
                        "or a file), or remove the line"),
    "repository-unnamed": ("write (or let grow write) a node whose repo: names this repository; if it is not "
                           "this plant's code, list it in the .gitignore of the repository that holds it; then "
                           "run python3 docs/graph/source-index.py build"),
}
HINT_LINE = {
    "tests-outside-class": ("Hint: {count} file(s) named like tests are outside TEST_GLOBS, e.g. {paths}. Add "
                            "their folders to TEST_GLOBS in docs/graph/spec-lint.py, or list them under "
                            "\"exclude\" in docs/graph/source-index.json if they are not tests."),
    "config-pattern-unmatched": "Hint: {count} pattern(s) in docs/graph/source-index.json match no file: {patterns}.",
}
HINT_FIX = {"config-pattern-unmatched": (
    "correct each pattern in docs/graph/source-index.json to the files it means (a pattern with no \"/\" matches "
    "a file name, one with \"/\" a plant-relative path), or remove it; then run python3 "
    "docs/graph/source-index.py build")}
SKILL_ROUTE_TASKS = {
    "impact": "what depends on src/app.py before I change it",
    "affected-tests": "which tests does a change to src/app.py reach",
    "anchors": "which graph pages cite src/app.py",
    "symbols": "where is the function save_order defined",
}
SKILL_ROUTE_PHRASINGS = {   # SPEC-0007 §6 "Build report": the owner's everyday wording, routed by phrase
    "impact": "what breaks if I change src/app.py",
    "affected-tests": "which tests cover src/app.py",
    "symbols": "where is save_order defined",
}
INSTALL_BUILD_HEAD = 'source index build (advice, never a failure of the install; SPEC-0007 "Build report"):'
INSTALL_BUILD_FAILED = ("source index: the build did not finish ({why}); the install is complete. Run from the "
                        "plant root: python3 docs/graph/source-index.py build")
STAMP_LINE = "[seed]   .cypress/seed.json     (seed stamp:"
CLOSING_BANNER = "[seed] done. FILES ARE PLACED"
FIX = "  fix: "


def fix_line(reason):
    return FIX + BUILD_FIX[reason]


def hints_of(doc, kind=None):
    return [h for h in doc.get("hints", []) if kind is None or h.get("hint") == kind]


def hint_view(h):
    return (h.get("hint"), h.get("subject"), h.get("count"), h.get("paths"))


def record_line(t, reason, subject):
    """The index of the text view's line for the `reason` record of `subject`."""
    ls = t.lines()
    hits = [i for i, l in enumerate(ls) if f"{reason}: {subject}" in l and not l.startswith("Incomplete:")]
    check(len(hits) == 1, f"the build text view lists the {reason} record of {subject} {len(hits)} time(s), "
                          f"not once — {t.ctx()}")
    return hits[0]


def expect_fix_under(t, reason, subject):
    i = record_line(t, reason, subject)
    ls = t.lines()
    got = ls[i + 1] if i + 1 < len(ls) else None
    check(got == fix_line(reason), f"the line under the {reason} record is {got!r}, want {fix_line(reason)!r}")


def time_line_index(t):
    hits = [i for i, l in enumerate(t.lines()) if re.fullmatch(BUILD_TIME_RE, l)]
    check(len(hits) == 1, f"the build text view holds {len(hits)} `Built in <s> s.` line(s), not one — {t.ctx()}")
    return hits[0]


def ends_with_build_action(t, n):
    want = ACTION["build"].format(n=n)
    check(t.last().startswith(want), f"the build text view does not end with {want!r}… — {t.ctx()}")


@case("X461", "BUILD_REPORTS_ITS_TIME_AND_COUNTS")
def x461(base):
    p = inventory_plant(base)
    t = tool(p, "build")
    check(t.rc == 0, f"build must exit 0 — {t.ctx()}")
    ls = t.lines()
    check(len(ls) >= 2 and ls[0].startswith("Cache: ") and ls[1].startswith("Index: "),
          f"the build text view does not open with the cache line and the count line — {t.ctx()}")
    check(time_line_index(t) == 2, f"the time line is not the line after the count line — {t.ctx()}")
    first = p.index.read_bytes()
    d = query(p, "build")
    secs = d.get("seconds")
    check(isinstance(secs, (int, float)) and not isinstance(secs, bool) and secs >= 0,
          f"build --json `seconds` is {secs!r}, not a non-negative number")
    check(p.index.read_bytes() == first, "two builds wrote cache documents that differ (the time is in the cache)")
    check(b"seconds" not in first, "the cache document holds `seconds`")
    # no incomplete record and no hint: the time line is the last line
    write(p.dir, CONFIG_PATH, json.dumps({"exclude": []}) + "\n")
    d = query(p, "build")
    check(d.get("incomplete") == [] and d.get("hints") == [],
          f"setup: the plant with `exclude: []` is not complete and hint-free: {d.get('incomplete')!r} "
          f"{d.get('hints')!r}")
    t = tool(p, "build")
    check(t.rc == 0 and re.fullmatch(BUILD_TIME_RE, t.last()),
          f"with no record and no hint the time line is not the last line — {t.ctx()}")
    return "cache line, count line, then `Built in <s> s.`; `seconds` >= 0; no time in the cache"


@case("X462", "BUILD_NAMES_REPO_VALUES_THAT_NAME_NOTHING; failure REPOSITORY_UNNAMED")
def x462(base):
    problems = []
    page = "docs/graph/nodes/{}.md".format
    values = {"nold": "old/lib", "nlist": "src/a.py, src/b.py", "nsrc": "src"}
    files = {"src/a.py": "A = 1\n", "src/b.py": "B = 1\n", "tests/t_test.py": "T = 1\n"}
    for n, v in values.items():
        files[f"docs/graph/nodes/{n}.md"] = node(f"subsystem.{n}", repo=v)
    p = Plant(base, "repo-values", files=files, config={"exclude": []})
    try:
        d = query(p, "build")
        got = unresolved(d)
        want = sorted((page(n), REPO_UNRESOLVED_DETAIL.format(value=values[n])) for n in ("nold", "nlist"))
        check(got == want, f"build: repo-unresolved records {got!r}, want {want!r}")
        check(p.index.is_file(), "build wrote no cache beside its repo-unresolved records")
        t = tool(p, "build")
        check(t.rc == 0, f"build must exit 0 — {t.ctx()}")
        ti = time_line_index(t)
        for n in ("nold", "nlist"):
            check(record_line(t, "repo-unresolved", page(n)) > ti,
                  f"the {page(n)} record is not after the time line — {t.ctx()}")
            expect_fix_under(t, "repo-unresolved", page(n))
        ends_with_build_action(t, len(d.get("incomplete", [])))
    except CaseFail as e:
        problems.append(f"repo values: {e}")

    def unnamed_plant(name, ignore=False, named=False):
        fs = {"src/a.py": "A = 1\n", "tests/t_test.py": "T = 1\n"}
        if ignore:
            fs[".gitignore"] = "vendor/lib/\n"
        if named:
            fs["docs/graph/nodes/vlib.md"] = node("subsystem.vlib", repo="vendor/lib")
        u = Plant(base, name, files=fs, config={"exclude": []})
        sub = u.dir / "vendor" / "lib"
        sub.mkdir(parents=True)
        git(sub, "init", "-q")
        write(sub, "x.py", "X = 1\n")
        git(sub, "add", "-A")
        git(sub, "commit", "-qm", "nested")
        return u

    try:
        u = unnamed_plant("unnamed")
        d = query(u, "build")
        recs = [(r.get("reason"), r.get("subject")) for r in d.get("incomplete", [])]
        check(recs == [("repository-unnamed", "vendor/lib")],
              f"build: incomplete {d.get('incomplete')!r}, want one repository-unnamed record naming vendor/lib")
        under = [r.get("path") for r in d.get("inventory", []) if str(r.get("path")).startswith("vendor/lib/")]
        check(not under, f"build inventories {under!r} under the unnamed repository")
        t = tool(u, "build")
        expect_fix_under(t, "repository-unnamed", "vendor/lib")
        imp = query(u, "impact", "src/a.py")
        check("repository-unnamed" not in reasons(imp), f"impact holds a repository-unnamed record: "
                                                         f"{imp.get('incomplete')!r}")
    except CaseFail as e:
        problems.append(f"arm unnamed (REPOSITORY_UNNAMED): {e}")
    for name, kw in (("ignored", {"ignore": True}), ("named", {"named": True})):
        try:
            d = query(unnamed_plant(name, **kw), "build")
            check("repository-unnamed" not in reasons(d), f"build holds a repository-unnamed record: "
                                                          f"{d.get('incomplete')!r}")
        except CaseFail as e:
            problems.append(f"arm {name}: {e}")
    check(not problems, " || ".join(problems))
    return ("a missing folder and a comma list each repo-unresolved with its fix, `repo: src` none, the build "
            "action last, the cache written; an unnamed nested repository named with its fix, none when "
            "ignored or named, none in a query")


@case("X463", "BUILD_NAMES_TESTS_OUTSIDE_THE_TEST_CLASS")
def x463(base):
    problems = []
    common = {"src/lib/test_a.py": "A = 1\n", "src/b.py": "B = 1\n"}
    try:
        d = query(Plant(base, "no-globs", files=common, globs=None), "build")
        check("no-test-declaration" in reasons(d), f"(a) incomplete {d.get('incomplete')!r} holds no "
                                                   f"no-test-declaration record")
        check(d.get("hints") == [], f"(a) hints {d.get('hints')!r}, want []")
    except CaseFail as e:
        problems.append(f"(a) {e}")
    try:
        d = query(Plant(base, "no-match", files=common, globs=["checks/**/*.*"]), "build")
        check("no-test-files" in reasons(d), f"(b) incomplete {d.get('incomplete')!r} holds no no-test-files record")
        hs = hints_of(d)
        check(len(hs) == 1 and hs[0].get("hint") == "tests-outside-class"
              and "src/lib/test_a.py" in (hs[0].get("paths") or []),
              f"(b) hints {d.get('hints')!r}, want one tests-outside-class hint naming src/lib/test_a.py")
    except CaseFail as e:
        problems.append(f"(b) {e}")
    try:
        files = dict(common, **{"tests/t_test.py": "T = 1\n", "web/a.spec.ts": "export {};\n",
                                "src/old/test_x.py": "X = 1\n"})
        c = Plant(base, "outside", files=files, config={"exclude": ["src/old/test_x.py"]})
        d = query(c, "build")
        check(d.get("incomplete") == [], f"(c) incomplete {d.get('incomplete')!r}, want []")
        want = [("tests-outside-class", "docs/graph/spec-lint.py", 2, ["src/lib/test_a.py", "web/a.spec.ts"])]
        got = [hint_view(h) for h in hints_of(d)]
        check(got == want, f"(c) hints {got!r}, want {want!r} (the excluded src/old/test_x.py not counted)")
        t = tool(c, "build")
        line = HINT_LINE["tests-outside-class"].format(count=2, paths="src/lib/test_a.py, web/a.spec.ts")
        check(line in t.lines() and t.lines().index(line) > time_line_index(t),
              f"(c) the text view does not print {line!r} after the time line — {t.ctx()}")
        check(not any(l.startswith("Incomplete:") for l in t.lines()), f"(c) the text view has an action line "
                                                                        f"— {t.ctx()}")
    except CaseFail as e:
        problems.append(f"(c) {e}")
    check(not problems, " || ".join(problems))
    return ("no TEST_GLOBS: no-test-declaration, no hint; unmatched globs: no-test-files and the hint; two "
            "test-named files outside the class: one hint, its line, no action line; an excluded one not counted")


@case("X464", "BUILD_HINTS_EXCLUDE_FOR_NON_TEST_FILES")
def x464(base):
    problems = []
    files = {"tests/t_test.py": "T = 1\n", "tests/fixtures/data.json": "{}\n", "tests/helpers/util.py": "U = 1\n"}
    want = [("class-holds-non-tests", "docs/graph/source-index.json", 2,
             ["tests/fixtures/data.json", "tests/helpers/util.py"])]
    try:
        got = [hint_view(h) for h in hints_of(query(Plant(base, "no-config", files=files), "build"),
                                              "class-holds-non-tests")]
        check(got == want, f"no config: class-holds-non-tests hints {got!r}, want {want!r}")
    except CaseFail as e:
        problems.append(str(e))
    for name, config in (("exclude-empty", {"exclude": []}), ("refused", {"exclude": [], "unknown_key": []})):
        try:
            d = query(Plant(base, name, files=files, config=config), "build")
            check(hints_of(d, "class-holds-non-tests") == [], f"{name}: hints {d.get('hints')!r} hold a "
                                                              f"class-holds-non-tests hint")
            if name == "refused":
                check("config-refused" in reasons(d), f"refused: incomplete {d.get('incomplete')!r} holds no "
                                                      f"config-refused record")
        except CaseFail as e:
            problems.append(f"{name}: {e}")
    check(not problems, " || ".join(problems))
    return "no config: one class-holds-non-tests hint, count 2; `exclude: []` and a refused config: none"


@case("X465", "BUILD_RECORDS_NAME_THEIR_FIX")
def x465(base):
    problems = []
    arms = (("(a)", dict(name="no-repo", files={"a.py": "A = 1\n"}, git_init=False), "no-repository", None),
            ("(b)", dict(name="no-globs", files=BASE_FILES, globs=None), "no-test-declaration", None),
            ("(c)", dict(name="refused", files=BASE_FILES, config={"exclude": [], "unknown_key": []}),
             "config-refused", CONFIG_PATH))
    for arm, kw, reason, subject in arms:
        try:
            p = Plant(base, **kw)
            d = query(p, "build")
            recs = [r for r in d.get("incomplete", []) if r.get("reason") == reason]
            check(len(recs) == 1, f"build --json incomplete {d.get('incomplete')!r} holds no single {reason} record")
            raw = json.dumps(d)
            check(BUILD_FIX[reason] not in raw,
                  f"build --json carries the fix text: {raw[:600]!r}")
            t = tool(p, "build")
            check(t.rc == 0, f"build must exit 0 — {t.ctx()}")
            expect_fix_under(t, reason, subject if subject is not None else recs[0].get("subject"))
            ends_with_build_action(t, len(d.get("incomplete", [])))
            if arm == "(a)":
                check("no-test-files" not in reasons(d), f"(a) no governed repository: incomplete "
                                                         f"{d.get('incomplete')!r} holds a no-test-files record")
                check(d.get("hints") == [], f"(a) no governed repository: hints {d.get('hints')!r}, want []")
            if arm == "(b)":
                for q in ("impact", "affected-tests"):
                    qt = tool(p, q, "a.py")
                    check(not any(l.startswith(FIX) for l in qt.lines()),
                          f"`{q} a.py` prints a fix line — {qt.ctx()}")
        except CaseFail as e:
            problems.append(f"{arm} {e}")
    check(not problems, " || ".join(problems))
    return ("no repository, no TEST_GLOBS and a refused config: each record line followed by its fix line, the "
            "build action last; the queries print no fix; --json holds no fix text")


@case("X466", "BUILD_HINTS_CONFIG_PATTERNS_THAT_MATCH_NOTHING")
def x466(base):
    problems = []
    files = {"tests/t_test.py": "T = 1\n", "src/a.py": "A = 1\n"}
    config = {"exclude": [], "always_run": ["tests/t_test.py", "tests/smoek/**"], "global_inputs": ["package.json"]}
    try:
        p = Plant(base, "typo", files=files, config=config)
        d = query(p, "build")
        hs = hints_of(d, "config-pattern-unmatched")
        want = [("config-pattern-unmatched", CONFIG_PATH, 2,
                 ["always_run: tests/smoek/**", "global_inputs: package.json"])]
        got = [(h.get("hint"), h.get("subject"), h.get("count"), h.get("patterns")) for h in hs]
        check(got == want, f"config-pattern-unmatched hints {got!r}, want {want!r}")
        check(d.get("incomplete") == [], f"incomplete {d.get('incomplete')!r}, want []")
        check(p.index.is_file(), "the build wrote no cache")
        t = tool(p, "build")
        check(t.rc == 0, f"build must exit 0 — {t.ctx()}")
        line = HINT_LINE["config-pattern-unmatched"].format(
            count=2, patterns="always_run: tests/smoek/**, global_inputs: package.json")
        ls = t.lines()
        check(line in ls, f"the text view does not print {line!r} — {t.ctx()}")
        i = ls.index(line)
        check(i + 1 < len(ls) and ls[i + 1] == FIX + HINT_FIX["config-pattern-unmatched"],
              f"the line under the hint is not its fix line — {t.ctx()}")
        check(not any(l.startswith("Incomplete:") for l in ls), f"the text view has an action line — {t.ctx()}")
    except CaseFail as e:
        problems.append(f"typo: {e}")
    for name, cfg in (("no-config", None), ("no-global-inputs", {"exclude": [], "always_run": ["tests/t_test.py"]}),
                      ("refused", dict(config, unknown_key=[]))):
        try:
            d = query(Plant(base, name, files=files, config=cfg), "build")
            check(hints_of(d, "config-pattern-unmatched") == [],
                  f"{name}: hints {d.get('hints')!r} hold a config-pattern-unmatched hint")
            check(isinstance(d.get("hints"), list), f"{name}: build --json has no `hints` list: {sorted(d)!r}")
        except CaseFail as e:
            problems.append(f"{name}: {e}")
    check(not problems, " || ".join(problems))
    return ("two unmatched patterns in key then list order: one hint, its line, its fix line, no action line; "
            "a default pattern, an unset key and a refused file give none")


# --- surfacing at install (8.1.2): the seed skill and the installer's build ------
def install(target, *args, seed=None, timeout=600):
    r = subprocess.run(["bash", str((seed or SEED) / "install.sh"), "claude-code", "--project-dir", str(target),
                        *args], capture_output=True, timeout=timeout, env=ENV)
    return Run(r.returncode, r.stdout, r.stderr.decode("utf-8", "surrogateescape"))


def plan_load(target, task):
    """id -> how of `graph-lint.py --plan-json` for `task`, run from the target."""
    r = subprocess.run([sys.executable, "docs/graph/graph-lint.py", "--plan-json", task], cwd=str(target),
                       capture_output=True, text=True, timeout=60, env=ENV)
    check(r.returncode == 0, f"--plan-json {task!r} exited {r.returncode}: {r.stderr[-400:]}")
    return {e.get("id"): (e.get("how") or {}) for e in json.loads(r.stdout).get("load", [])}


SKILL_SRC = SEED / "skills" / "source-index" / "SKILL.md"


@case("X460", "SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS")
def x460(base):
    problems = []
    t = base / "target"
    t.mkdir()
    r = install(t)
    if r.rc != 0:
        raise HarnessFail(f"install.sh claude-code exited {r.rc}: {r.err[-600:]}")
    placed = t / "docs" / "graph" / "skills" / "source-index.md"
    proj = t / ".claude" / "skills" / "source-index" / "SKILL.md"

    def arm(name, fn):
        try:
            fn()
        except CaseFail as e:
            problems.append(f"arm ({name}): {e}")

    def placed_arm():
        check(SKILL_SRC.is_file(), f"the seed holds no skills/source-index/SKILL.md")
        check(placed.is_file() and placed.read_bytes() == SKILL_SRC.read_bytes(),
              "docs/graph/skills/source-index.md is missing or not byte-identical to the seed's skill")
        head = placed.read_text().split("\n---", 1)[0]
        check("\nid: skill.source-index\n" in head + "\n" and "\norigin: seed\n" in head + "\n",
              f"the placed skill's frontmatter lacks `id: skill.source-index` or `origin: seed`: {head[:300]!r}")
        check(proj.is_file(), ".claude/skills/source-index/SKILL.md was not projected")

    def route_arm():
        for q, task in SKILL_ROUTE_TASKS.items():
            got = plan_load(t, task)
            check("skill.source-index" in got, f"the {q} task {task!r} loads {sorted(got)!r}, "
                                               f"not skill.source-index")

    def phrasings_arm():
        for q, task in SKILL_ROUTE_PHRASINGS.items():
            got = plan_load(t, task)
            check((got.get("skill.source-index") or {}).get("kind") == "phrase",
                  f"the {q} phrasing {task!r} loads skill.source-index as {got.get('skill.source-index')!r}, "
                  f"not phrase (loads {sorted(got)!r})")

    def catalog_arm():
        tools_dir = t / "docs" / "graph" / "tools"
        got = sorted(p.relative_to(tools_dir).as_posix() for p in tools_dir.rglob("*") if p.is_file())
        check(got == ["index.md"], f"the installer wrote {got!r} under docs/graph/tools/, want ['index.md']")
        own = write(t, "docs/graph/tools/source-index.md", "# source-index\n\nThe plant's own card.\n")
        idx = tools_dir / "index.md"
        idx.write_text(idx.read_text() + "\n| source-index | the plant's own row | tools/source-index.md |\n")
        before = (own.read_bytes(), idx.read_bytes())
        r2 = install(t)
        check(r2.rc == 0, f"the re-install exited {r2.rc}: {r2.err[-400:]}")
        check((own.read_bytes(), idx.read_bytes()) == before, "the re-install changed the plant's tool card or "
                                                              "its catalog row")
        baks = sorted(p.name for p in tools_dir.iterdir() if ".bak-" in p.name)
        check(not baks, f"the re-install left backups in docs/graph/tools/: {baks!r}")

    def reinstall_arm():
        placed.unlink(missing_ok=True)
        shutil.rmtree(proj.parent, ignore_errors=True)
        r2 = install(t)
        check(r2.rc == 0, f"the re-install exited {r2.rc}: {r2.err[-400:]}")
        check(placed.is_file() and proj.is_file(), "a re-install over a plant without the skill did not place "
                                                   "docs/graph/skills/source-index.md and its projection again")

    def owned_path_arm():
        write(t, "src/app.py", "def save_order():\n    pass\n")
        write(t, "docs/graph/nodes/subsystem.app.md", node("subsystem.app", repo="src"))
        idx = t / "docs" / "graph" / "index.md"
        idx.write_text(idx.read_text() + "\n- subsystem.app\n")
        tasks = [(q, task) for q, task in SKILL_ROUTE_TASKS.items()]
        tasks += [(q, task) for q, task in SKILL_ROUTE_PHRASINGS.items()]
        for q, task in tasks:
            got = plan_load(t, task)
            if "src/app.py" in task:
                check((got.get("subsystem.app") or {}).get("kind") == "named_path",
                      f"the {q} task {task!r} loads subsystem.app as {got.get('subsystem.app')!r}, not named_path")
            check((got.get("skill.source-index") or {}).get("kind") == "phrase",
                  f"the {q} task {task!r} loads skill.source-index as {got.get('skill.source-index')!r}, "
                  f"not phrase (loads {sorted(got)!r})")

    for name, fn in (("placed", placed_arm), ("routes", route_arm), ("phrasings", phrasings_arm),
                     ("catalog", catalog_arm),
                     ("re-install", reinstall_arm), ("owned-path", owned_path_arm)):
        arm(name, fn)
    check(not problems, " || ".join(problems))
    return ("the seed skill placed byte-identical and projected, the four tasks load it; the plant's tools/ card "
            "untouched; a re-install restores it; beside a path route it loads by phrase")


def seed_copy(base, fake_tool):
    """A copy of the seed whose tools/source-index.py is `fake_tool` (Python source)."""
    dst = base / "seed-copy"
    if not dst.exists():
        shutil.copytree(SEED, dst, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", ".seed-worktrees"))
    (dst / "tools" / "source-index.py").write_text(fake_tool)
    return dst


def git_target(base, name, files=None):
    t = base / name
    t.mkdir()
    git(t, "init", "-q")
    git(t, "symbolic-ref", "HEAD", "refs/heads/main")
    for rel, text in (files or {"src/a.py": "A = 1\n"}).items():
        write(t, rel, text)
    git(t, "add", "-A")
    git(t, "commit", "-qm", "plant")
    return t


@case("X467", "INSTALL_RUNS_THE_BUILD; failure INSTALL_BUILD_FAILED")
def x467(base):
    problems = []
    head = "[seed] " + INSTALL_BUILD_HEAD

    def arm(name, fn):
        try:
            fn()
        except CaseFail as e:
            problems.append(f"arm ({name}): {e}")

    def ordered(r):
        ls = r.lines()
        check(r.rc == 0, f"the install exited {r.rc} — {r.ctx()}")
        hi = [i for i, l in enumerate(ls) if l == head]
        check(len(hi) == 1, f"the install prints {INSTALL_BUILD_HEAD!r} {len(hi)} time(s), not once — {r.ctx()}")
        si = [i for i, l in enumerate(ls) if l.startswith(STAMP_LINE)]
        bi = [i for i, l in enumerate(ls) if l.startswith(CLOSING_BANNER)]
        ni = [i for i, l in enumerate(ls) if "NEXT STEP" in l and si and i > si[0]]
        check(si and bi and si[0] < hi[0] < bi[0] and all(hi[0] < i for i in ni),
              f"the report is not after the stamp line and before the NEXT STEP notices and the banner — {r.ctx()}")
        return ls, hi[0]

    def main_arm():
        t = git_target(base, "git-plant")
        r = install(t)
        ls, h = ordered(r)
        report = []
        for l in ls[h + 1:]:
            if not l.startswith("[seed]   "):
                break
            report.append(l[len("[seed]   "):])
        check("Cache: built" in report, f"the report lines {report!r} hold no `Cache: built`")
        check(any(re.fullmatch(BUILD_TIME_RE, l) for l in report),
              f"the report lines {report!r} hold no time line")
        class P:
            dir = t
        d = query(P, "impact", "src/a.py")
        check(status(d) == "reused", f"the query after the install reports cache {d.get('cache')!r}, not reused")
        check(not (t / CONFIG_PATH).exists(), "the install wrote docs/graph/source-index.json")

    def no_repository_arm():
        t = base / "fresh"
        t.mkdir()
        r = install(t)
        ordered(r)
        check("no-repository" in r.out and ("[seed]   " + fix_line("no-repository")) in r.lines(),
              f"the report holds no no-repository record with its fix line — {r.ctx()}")
        check(not (t / ".cypress" / "source-index").exists(), "the build wrote .cypress/source-index/ in a "
                                                               "plant with no governed repository")

    def no_build_arm():
        t = git_target(base, "checked")
        r = install(t)
        check(r.rc == 0, f"setup install exited {r.rc}")
        for args in (("--check",), ("--expertise", "propose"), ("--no-such-option",)):
            r2 = install(t, *args)
            check(head not in r2.lines(), f"`install.sh claude-code {' '.join(args)}` printed the build head — "
                                          f"{r2.ctx()}")

    def security_a1_a4_arm():
        markers = base / "markers"
        markers.mkdir()
        files = {"src/a.py": "A = 1\n",
                 "docs/graph/fnmatch.py": f"open({str(markers / 'fnmatch')!r}, 'w').write('x')\n",
                 "docs/graph/json.py": f"open({str(markers / 'json')!r}, 'w').write('x')\n",
                 "docs/graph/nodes/esc.md": node("subsystem.esc", repo="old/\x1b[31mlib")}
        t = git_target(base, "hostile", files)
        r = install(t)
        ls, h = ordered(r)
        check(not os.listdir(markers), f"the install imported a module the target holds: markers "
                                       f"{sorted(os.listdir(markers))!r}")
        check(any(l.startswith("[seed]   Cache: ") for l in ls[h + 1:]), f"A1: the report's lines are not "
                                                                         f"printed — {r.ctx()}")
        check("old/?[31mlib" in r.out, f"A4: the report does not show the control byte as `?` — {r.ctx()}")
        check(b"\x1b" not in r.raw and "\x1b" not in r.err, "A4: the install's output holds the byte 0x1b")

    def non_utf8_arm():
        s = seed_copy(base, "import sys\nsys.stdout.buffer.write(b'\\xff\\xfe\\n')\nsys.exit(0)\n")
        t = git_target(base, "non-utf8")
        r = install(t, seed=s)
        ordered(r)

    def failed_arm():
        s = seed_copy(base, "import sys\nsys.stdout.write('\\x1b[2J MARK-OUT\\n')\n"
                            "sys.stderr.write('MARK-ERR \\x1b]0;x\\x07\\n')\nsys.exit(3)\n")
        t = git_target(base, "failing")
        r = install(t, seed=s)
        ls = r.lines()
        check(r.rc == 0, f"the install exited {r.rc} after a failed build — {r.ctx()}")
        want = "[seed] " + INSTALL_BUILD_FAILED.format(why="exit 3")
        check(want in ls, f"the install does not print {want!r} — {r.ctx()}")
        bi = [i for i, l in enumerate(ls) if l.startswith(CLOSING_BANNER)]
        check(bi and bi[0] > ls.index(want), f"the closing banner is not printed after the failure line — {r.ctx()}")
        both = r.out + r.err
        check("MARK-OUT" not in both and "MARK-ERR" not in both, f"A2: the build's stdout or stderr was printed "
                                                                 f"— {r.ctx()}")
        check(not any(b in r.raw for b in (b"\x1b", b"\x07")) and not any(c in r.err for c in ("\x1b", "\x07")),
              "A2: the install's output holds a byte 0x1b or 0x07")

    for name, fn in (("git plant", main_arm), ("no repository", no_repository_arm),
                     ("--check, --expertise propose, a refused run", no_build_arm), ("A1+A4 hostile target", security_a1_a4_arm),
                     ("A3 non-UTF-8 stdout", non_utf8_arm), ("INSTALL_BUILD_FAILED + A2", failed_arm)):
        arm(name, fn)
    check(not problems, " || ".join(problems))
    return ("the head and the indented report after the stamp, before the notices and banner, the cache reused; "
            "no repository: its fix, no cache; --check and propose run none; no plant module imported, ESC shown "
            "as ?; non-UTF-8 stdout and a failed build leave exit 0 and the banner, nothing of the build's printed")


# §6 constants of ACTION_LINE_NAMES_AT_MOST_TEXT_MAX_ROWS_RECORDS, used by value.
TEXT_MAX_ROWS = 40
ACTION_MORE = ", ... {k} more; --all lists every row"


def capped_action(query_name, recs, n=None):
    """The closing ACTION_LINE of the text view over `recs`, its reasons cut at TEXT_MAX_ROWS."""
    shown = ", ".join(f"{r['reason']}: {r['subject']}" for r in recs[:TEXT_MAX_ROWS])
    if len(recs) > TEXT_MAX_ROWS:
        shown += ACTION_MORE.format(k=len(recs) - TEXT_MAX_ROWS)
    line = ACTION["build"].format(n=len(recs) if n is None else n) if query_name == "build" else ACTION[query_name]
    return line + shown + ")."


@case("X470", "ACTION_LINE_NAMES_AT_MOST_TEXT_MAX_ROWS_RECORDS")
def x470(base):
    problems = []
    gone = [f"gone/f{i:02d}.py" for i in range(1, TEXT_MAX_ROWS + 2)]
    p = Plant(base, "many-missing", files={"a.py": "A = 1\n"})
    want = [{"reason": "input-not-found", "subject": g} for g in gone]
    d = query(p, "impact", *gone)
    recs = [{"reason": r.get("reason"), "subject": r.get("subject")} for r in d.get("incomplete", [])]
    check(recs == want, f"setup: impact --json incomplete is not the {len(gone)} input-not-found records in input "
                        f"order: {d.get('incomplete')!r}")
    d_all = query(p, "impact", "--all", *gone)
    if len(d_all.get("incomplete", [])) != len(gone):
        problems.append(f"--json --all: incomplete holds {len(d_all.get('incomplete', []))} records, not {len(gone)}")
    t = tool(p, "impact", *gone)
    cut = capped_action("impact", want)
    if t.rc != 0 or t.last() != cut:
        problems.append(f"text: the action line is not cut at {TEXT_MAX_ROWS} records with ACTION_MORE 1: "
                        f"want {cut[-120:]!r}, got {t.last()[-120:]!r}")
    if "... 1 more; --all lists every row" not in t.lines():
        problems.append(f"text: the record list above the action line is not cut with its more-line — {t.ctx()}")
    t = tool(p, "impact", "--all", *gone)
    whole = ACTION["impact"] + ", ".join(f"input-not-found: {g}" for g in gone) + ")."
    if t.rc != 0 or t.last() != whole:
        problems.append(f"--all: the action line does not name all {len(gone)} records and no ACTION_MORE: "
                        f"got {t.last()[-120:]!r}")
    # build: more setup items than TEXT_MAX_ROWS keep their whole count in {n}
    files = {"src/a.py": "A = 1\n"}
    for i in range(1, TEXT_MAX_ROWS + 2):
        files[f"docs/graph/nodes/n{i:02d}.md"] = node(f"subsystem.n{i:02d}", repo=f"old/lib{i:02d}")
    b = Plant(base, "many-setup", files=files, config={"exclude": []})
    d = query(b, "build")
    brecs = d.get("incomplete", [])
    check(len(brecs) > TEXT_MAX_ROWS, f"setup: build holds {len(brecs)} incomplete records, not more than "
                                      f"{TEXT_MAX_ROWS}: {brecs!r}")
    t = tool(b, "build")
    cut = capped_action("build", brecs)
    if t.rc != 0 or t.last() != cut:
        problems.append(f"build: the action line does not keep n={len(brecs)} with its reasons cut at "
                        f"{TEXT_MAX_ROWS}: want {cut[:60]!r}…{cut[-80:]!r}, got {t.last()[:60]!r}…{t.last()[-80:]!r}")
    check(not problems, " || ".join(problems))
    return (f"{len(gone)} missing inputs: the action line names {TEXT_MAX_ROWS} then ACTION_MORE 1, --all all, "
            f"--json all; build keeps n whole")


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
