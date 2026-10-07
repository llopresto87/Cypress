#!/usr/bin/env python3
"""source-index.py: what depends on what in a plant's code, derived without a model.

The tool inventories the code of every governed repository (the plant root
when it is a Git work tree, plus each nested work tree a node names in
`repo:`) and reads file-to-file links from it: Python imports and loads by
file path (read with `ast`, never imported or run), shell and Python
invocations, quoted path and directory literals, and TypeScript/JavaScript
import and require specifiers resolved through `tsconfig`/`jsconfig` paths.
Each link is `certain` or `maybe`, with the reason; a file whose references
cannot be pinned is an `opaque` record, and an import or invoke naming no
file is an `unresolved` record (SPEC-0007 §6).

Placed in a plant as `docs/graph/source-index.py` and run from the plant root:

    python3 docs/graph/source-index.py build [--json]
    python3 docs/graph/source-index.py impact         [--depth N] [--all] [--json] <path>... | -
    python3 docs/graph/source-index.py affected-tests [--depth N] [--all] [--json] <path>... | -
    python3 docs/graph/source-index.py anchors                  [--all] [--json] <path>... | -

The path rules (what is code, the governed repositories, the Git boundary,
the blob hash, the atomic write) are `source_paths.py`'s, the plant edge is
`plant_walk.py`'s, and node frontmatter is read by `frontmatter.py`; all three
sit beside this file and are loaded by file path. The tests are the plant's
`TEST_GLOBS` in `docs/graph/spec-lint.py`; `docs/graph/source-index.json` may
set `exclude`, `always_run` and `global_inputs`.

The index is derived scratch (ADR-0029): kept in `.cypress/source-index/`
beside an inner `.gitignore` of `*`, rebuilt whenever its key changes (the
Python major.minor, this tool and its siblings, the config and `TEST_GLOBS`,
each repository's HEAD and uncommitted code), never committed. The tool reads
only inventory files, graph pages, the config and `spec-lint.py`, each through
a bounded, non-following open; a path taken from file content is text matched
against the inventory, never opened. Every query exits 0 with an answer; what
it cannot answer it lists as `incomplete`.
"""

import argparse
import ast
import hashlib
import json
import os
import posixpath
import re
import stat
import sys
from fnmatch import fnmatchcase
from pathlib import Path
import importlib.util as _ilu


def _sibling(name, module):
    spec = _ilu.spec_from_file_location(module, Path(__file__).resolve().parent / name)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


source_paths = _sibling("source_paths.py", "cypress_source_paths")
plant_walk = _sibling("plant_walk.py", "cypress_plant_walk")

# --- constants and texts (SPEC-0007 §6): this file is their one home, except
# the path rules, whose home is source_paths.py. ---
INDEX_SCHEMA = "cypress.source-index/1"
ANSWER_SCHEMA = "cypress.source-index.answer/1"
DEFAULT_DEPTH = 3
MAX_DEPTH = 5
TEXT_MAX_ROWS = 40
LITERAL_MAX = 255
JOIN_MAX = 3
FILE_MAX_BYTES = 1048576
DIR_LINK_MAX = 200
EXTENDS_MAX = 16
CACHE_MAX_BYTES = 67108864
CACHE_DIR = ".cypress/source-index"
CACHE_NAME = "index.json"
CACHE_IGNORE = "*\n"
CONFIG_PATH = "docs/graph/source-index.json"
TEST_DECLARATION = "docs/graph/spec-lint.py: TEST_GLOBS"
SIBLINGS = ["source_paths.py", "plant_walk.py", "frontmatter.py"]
TEMP_PREFIX = ".tmp-source-index-"
FLOOR_LINE = "Floor: {n} maybe row(s) every input reaches (opaque holders and their dependents):"
RECOMMEND_LINE = ("Recommendation only: the tests above and the always-run set, never only these; "
                  "verify decides what runs.")
ACTION_LINE = {
    "build": "Incomplete: check by hand ({reasons}).",
    "impact": "Incomplete: check by hand ({reasons}).",
    "affected-tests": "Incomplete: run the full suite ({reasons}).",
    "anchors": "Incomplete: review by hand ({reasons}).",
}
CONFIG_DEFAULTS = {
    "exclude": [],
    "always_run": [],
    "global_inputs": [
        "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
        "tsconfig*.json", "jsconfig*.json", "vitest.config.*", "vite.config.*",
        "jest.config.*", "playwright.config.*", "next.config.*", "pytest.ini",
        "pyproject.toml", "setup.cfg", "tox.ini", "conftest.py",
        "requirements*.txt", "uv.lock"],
}
# spec-lint's `test_files` semantics, whose home is spec-lint.py (SPEC-0007 §6
# "Inventory record"): no file under one of these directories is a test.
TEST_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
                  "dist", "build", "target", ".next"}

LANGUAGES = {".py": "python", ".sh": "shell", ".bash": "shell",
             ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
             ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
             ".json": "json"}
LINK_BEARING = ("python", "shell", "typescript", "javascript")
TS_PROBE = (".ts", ".tsx", ".d.ts", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".json")
JS_WRITTEN = (".js", ".jsx", ".mjs", ".cjs")
JS_TO_TS = (".ts", ".tsx", ".mts", ".cts")
ASSETS = (".css", ".scss", ".sass", ".less", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp",
          ".ico", ".woff", ".woff2", ".html", ".md")
INTERPRETERS = {"python3", "python", "bash", "sh"}
PY_ARG_OPTIONS = {"-X", "-W"}          # interpreter options that take the next word
PY_WALKS = {"os.walk", "os.scandir", "os.listdir", "glob.glob"}

ENUMS = {
    "language": {"python", "shell", "typescript", "javascript", "json", "other"},
    "test": {"test", "code"},
    "kind": {"import", "invoke", "path-literal"},
    "link": {"certain", "maybe"},
    "found": {"exact", "resolved", "path-literal", "directory", "ambiguous", "workspace-package"},
    "opaque": {"dynamic-nonliteral", "walks-tree", "unreadable", "alias-config-unavailable"},
    "unresolved": {"relative-no-file", "alias-no-file", "outside-repository", "generated", "asset"},
}
SHAPE = {
    "inventory": {"path", "repo", "hash", "language", "test"},
    "links": {"holder", "target", "kind", "link", "found", "line"},
    "opaque": {"holder", "line", "reference", "reason"},
    "unresolved": {"holder", "line", "kind", "reference", "reason", "base"},
}
NPM_NAME = re.compile(r"^(?:node:.+|(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*(?:/.*)?)$")
VARIABLE = re.compile(r"^\$(?:\{[^}]*\}|[A-Za-z_][A-Za-z0-9_]*|[@*#?$!0-9])$")
OPEN_CALL = re.compile(r"(?:(?<![\w$.])import|(?<![\w$.])require|(?<![\w$])vi\.mock)\s*\(\s*$")
TS_FROM = re.compile(r"(?<![\w$.])from\s*(['\"])([^'\"\n]*)\1")
TS_BARE_IMPORT = re.compile(r"(?<![\w$.])import\s*(['\"])([^'\"\n]*)\1")
TS_CALL = re.compile(r"(?:(?<![\w$.])import|(?<![\w$.])require|(?<![\w$])vi\.mock)\s*\(\s*")
TS_LITERAL_ARG = re.compile(r"(['\"`])([^'\"`\n$]*)\1\s*[,)]")
TS_WALK = re.compile(r"(?<![\w$])(?:readdirSync|readdir)\s*\(\s*")
TS_STRING = re.compile(r"'([^'\\\n]*)'|\"([^\"\\\n]*)\"|`([^`\\\n$]*)`")


class Unreadable(Exception):
    """A file the tool will not read: not a regular file, outside its
    repository, too large, or not UTF-8."""


class Usage(Exception):
    pass


# --- bounded reads -----------------------------------------------------------
def read_bytes(top: Path, rel: str, limit: int = FILE_MAX_BYTES) -> bytes:
    """The bytes of <top>/<rel>, opened without following a symlink or
    blocking on a FIFO, read only when `fstat` shows a regular file of at most
    `limit` bytes whose real path lies inside `top`. Unreadable otherwise;
    FileNotFoundError when nothing is there."""
    path = top / rel
    real_top = os.path.realpath(top)
    if not os.path.realpath(path).startswith(real_top.rstrip("/") + "/"):
        raise Unreadable("outside its repository")
    try:
        opened = source_paths.open_regular(path)
    except FileNotFoundError:
        raise
    except OSError as e:
        raise Unreadable(e.strerror or type(e).__name__) from None
    if opened is None:
        raise Unreadable("not a regular file")
    fd, size = opened
    try:
        if size > limit:
            raise Unreadable("too large")
        data = b""
        while len(data) < size and (chunk := os.read(fd, size - len(data))):
            data += chunk
    finally:
        os.close(fd)
    return data


def read_text(top: Path, rel: str, limit: int = FILE_MAX_BYTES) -> str:
    try:
        return read_bytes(top, rel, limit).decode("utf-8")
    except UnicodeDecodeError:
        raise Unreadable("not UTF-8") from None


def _outside_strings(text: str, keep):
    """`text` rebuilt chunk by chunk: each JSON string literal is kept whole,
    and `keep(text, i)` decides every other position, returning (piece, next)."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        else:
            piece, i = keep(text, i)
            out.append(piece)
    return "".join(out)


def _drop_comment(text, i):
    if text.startswith("//", i):
        j = text.find("\n", i)
        return "", len(text) if j < 0 else j
    if text.startswith("/*", i):
        j = text.find("*/", i + 2)
        return " ", len(text) if j < 0 else j + 2
    return text[i], i + 1


def _drop_trailing_comma(text, i):
    if text[i] == ",":
        j = i + 1
        while j < len(text) and text[j] in " \t\r\n":
            j += 1
        if j < len(text) and text[j] in "}]":
            return "", i + 1
    return text[i], i + 1


def jsonc(text: str):
    """A JSON value read the way tsconfig is written: `//` and `/* */`
    comments, then trailing commas, are dropped outside string literals, so
    `"@/*"` survives. ValueError (or RecursionError) when it is no JSON then."""
    return json.loads(_outside_strings(_outside_strings(text, _drop_comment), _drop_trailing_comma))


# --- the plant's test declaration and config ---------------------------------
def read_test_globs(root: Path):
    """The plant's `TEST_GLOBS`: the list of strings the top-level assignment
    in `docs/graph/spec-lint.py` holds, or None when there is none to read."""
    try:
        tree = ast.parse(read_text(root, "docs/graph/spec-lint.py"))
    except (OSError, Unreadable, SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) and node.value else [])
        if any(isinstance(t, ast.Name) and t.id == "TEST_GLOBS" for t in targets):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError, RecursionError, MemoryError):
                return None
            ok = isinstance(value, list) and all(isinstance(g, str) for g in value)
            return value if ok else None
    return None


def read_config(root: Path):
    """(config, raw bytes, refusal): the plant config over the defaults, each
    key it sets replacing that key's default whole. A file that is not JSON,
    or holds an unknown key, a non-list value or a non-string item, is refused
    whole: the defaults apply and the refusal says why."""
    try:
        raw = read_bytes(root, CONFIG_PATH)
    except FileNotFoundError:
        return dict(CONFIG_DEFAULTS), b"", None
    except (OSError, Unreadable) as e:
        return dict(CONFIG_DEFAULTS), b"", f"unreadable: {e}"
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, RecursionError, MemoryError):
        return dict(CONFIG_DEFAULTS), raw, "not JSON"
    if not isinstance(doc, dict):
        return dict(CONFIG_DEFAULTS), raw, "not a JSON object"
    for key, value in doc.items():
        if key not in CONFIG_DEFAULTS:
            return dict(CONFIG_DEFAULTS), raw, f"unknown key {key!r}"
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return dict(CONFIG_DEFAULTS), raw, f"{key!r} is not a list of strings"
    return {**CONFIG_DEFAULTS, **doc}, raw, None


def config_matches(path: str, pattern: str) -> bool:
    """A config pattern with no `/` matches the last path segment; one with
    `/` drops its leading `**/` and matches the whole plant-relative path or
    any tail of it (graph-lint's `_path_matches` rule, case-sensitive here)."""
    if "/" not in pattern:
        return fnmatchcase(path.rsplit("/", 1)[-1], pattern)
    while pattern.startswith("**/"):
        pattern = pattern[3:]
    return fnmatchcase(path, pattern) or fnmatchcase(path, "*/" + pattern)


def _glob_segment(seg: str) -> str:
    out, i = [], 0
    while i < len(seg):
        c, close = seg[i], seg.find("]", i + 2)
        if c == "*":
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "[" and close > 0:
            body = seg[i + 1:close]
            body = "^" + body[1:] if body.startswith("!") else body
            out.append("[" + body.replace("\\", "\\\\") + "]")
            i = close
        else:
            out.append(re.escape(c))
        i += 1
    return "".join(out)


def glob_regex(pattern: str):
    """A `pathlib` glob from the plant root as a regex over a plant-relative
    path: `**` is any number of directories, every other segment is matched
    inside one directory level."""
    segs = [s for s in pattern.split("/") if s not in ("", ".")]
    parts = []
    for k, seg in enumerate(segs):
        last = k == len(segs) - 1
        if seg == "**":
            parts.append("(?:[^/]+/)*" + ("[^/]+" if last else ""))
        else:
            parts.append(_glob_segment(seg) + ("" if last else "/"))
    return re.compile("".join(parts) + r"\Z", re.S)


def test_class(path: str, test_globs, exclude) -> str:
    """`test` when a TEST_GLOBS pattern matches the path, no directory on its
    way is one spec-lint skips, and no `exclude` pattern matches; else `code`."""
    dirs = path.split("/")[:-1]
    if (not test_globs or TEST_SKIP_DIRS.intersection(dirs)
            or any(config_matches(path, p) for p in exclude)):
        return "code"
    return "test" if any(rx.match(path) for rx in test_globs) else "code"


# --- the inventory -----------------------------------------------------------
def language_of(name: str, data) -> str:
    """By extension; an extensionless file by its shebang (python*, bash, sh)."""
    base = name.rsplit("/", 1)[-1]
    ext = posixpath.splitext(base)[1]
    if ext:
        return LANGUAGES.get(ext, "other")
    if data is None or not data.startswith(b"#!"):
        return "other"
    words = data[2:].split(b"\n", 1)[0].decode("utf-8", "replace").split()
    if words and posixpath.basename(words[0]) == "env":
        words = [w for w in words[1:] if not w.startswith("-")]
    interp = posixpath.basename(words[0]) if words else ""
    if interp.startswith("python"):
        return "python"
    return "shell" if interp in ("bash", "sh") else "other"


def listed(repo: Path) -> list:
    """The tracked and the untracked, non-ignored paths Git lists in `repo`."""
    out = source_paths.git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted({p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p})


class Plant:
    """One plant: its root, governed repositories, test declaration, config,
    and the inventory Git and the path rules give."""

    def __init__(self, root: Path):
        self.root = root
        self.config, self.config_raw, self.config_refused = read_config(root)
        self.test_globs = read_test_globs(root)
        self.repos = source_paths.governed_repositories(root)
        self._foreign = {}

    def repo_of(self, path: str) -> str:
        """The governed repository (the nearest) a plant path lies in, or None."""
        best = "." if "." in self.repos else None
        for r in self.repos:
            if r != "." and (path == r or path.startswith(r + "/")) and (
                    best in (None, ".") or len(r) > len(best)):
                best = r
        return best

    def foreign(self, path: str) -> bool:
        """True when a directory on the way to `path` is foreign by plant_walk."""
        parts = path.split("/")[:-1]
        for k in range(1, len(parts) + 1):
            d = "/".join(parts[:k])
            if d not in self._foreign:
                self._foreign[d] = plant_walk.is_foreign(self.root / d)
            if self._foreign[d]:
                return True
        return False

    def key_repositories(self, problems: list) -> list:
        """Each readable repository's HEAD and the digest of its uncommitted
        code; a repository Git cannot read is a `repository-unreadable`
        record and is left out. GitMissing passes through."""
        entries = []
        for rel in self.repos:
            repo = self.root / rel
            try:
                head = source_paths.git(repo, "rev-parse", "--verify", "-q", "HEAD^{commit}",
                                        ok=(0, 1)).decode().strip()
                dirty = hashlib.sha256()
                for p in sorted(p for p in source_paths.uncommitted(repo) if source_paths.is_code(rel, p)):
                    state = source_paths.content_state(repo, p) or ""
                    dirty.update(p.encode("utf-8", "surrogateescape") + b"\0" + state.encode() + b"\n")
            except source_paths.GitFailed as e:
                problems.append(incomplete("repository-unreadable", rel, detail=str(e)))
                continue
            entries.append({"path": rel, "head": head, "dirty": dirty.hexdigest()})
        return entries

    def inventory(self, repos: list) -> dict:
        """path -> record for the code of the readable repositories: what Git
        lists, kept when the code-path rule holds and no directory on the way
        is foreign, the files of a nested repository taken from it alone."""
        nested = [r for r in repos if r != "."]
        rx = [glob_regex(g) for g in self.test_globs or []]
        records = {}
        for rel in repos:
            for p in listed(self.root / rel):
                path = source_paths.plant_path(rel, p)
                if (p.endswith("/") or not source_paths.is_code(rel, p) or self.foreign(path)
                        or rel == "." and any(path.startswith(n + "/") for n in nested)):
                    continue
                try:
                    st = os.lstat(self.root / path)
                except OSError:
                    continue                 # deleted from the work tree: not there to index
                if os.path.isdir(self.root / path) and not os.path.islink(self.root / path):
                    continue                 # a gitlink or a nested work tree
                records[path] = {"path": path, "repo": rel,
                                 "hash": source_paths.content_state(self.root / rel, p) or "",
                                 "language": None,
                                 "test": test_class(path, rx, self.config["exclude"]),
                                 "symlink": stat.S_ISLNK(st.st_mode)}
        return records


# --- links -------------------------------------------------------------------
def inside(path: str):
    """`path` normalized, or None when it is absolute or leaves the plant."""
    if not path or path.startswith("/"):
        return None
    p = posixpath.normpath(path)
    return None if p == ".." or p.startswith("../") else p


def joined(base: str, rel: str):
    return inside(rel if base in ("", ".") else base + "/" + rel)


def named(seg: str) -> bool:
    """A segment that names something: not empty, `.`, `..` or a bare variable."""
    return seg not in ("", ".", "..") and not VARIABLE.match(seg)


class Extract:
    """Reads the links, opaque and unresolved records of every link-bearing
    inventory file. Paths from file content are text matched against the
    inventory; nothing here opens a path built from such text."""

    def __init__(self, plant: Plant, records: dict):
        self.plant, self.records = plant, records
        self.files = set(records)
        self.by_name = {}
        self.under = {}                      # directory -> inventory files below it
        for path in sorted(records):
            self.by_name.setdefault(path.rsplit("/", 1)[-1], []).append(path)
            parts = path.split("/")
            for k in range(1, len(parts)):
                self.under.setdefault("/".join(parts[:k]), []).append(path)
        self.links, self.opaque, self.unresolved = set(), [], []
        self._tsconfig, self._packages = {}, None

    # -- recording
    def link(self, holder, target, kind, found, line):
        if target != holder:
            link = "certain" if found in ("exact", "resolved") else "maybe"
            self.links.add((holder, target, kind, link, found, line))

    def opaque_at(self, holder, line, reference, reason):
        self.opaque.append({"holder": holder, "line": line, "reference": reference[:LITERAL_MAX],
                            "reason": reason})

    def unresolved_at(self, holder, line, kind, reference, reason, base):
        self.unresolved.append({"holder": holder, "line": line, "kind": kind,
                                "reference": reference[:LITERAL_MAX], "reason": reason,
                                "base": base if reason != "outside-repository" else None})

    def missing(self, holder, line, kind, reference, base, reason="relative-no-file"):
        """A reference naming a path no inventory file holds."""
        if base is None or self.plant.repo_of(base) is None:
            self.unresolved_at(holder, line, kind, reference, "outside-repository", None)
        else:
            self.unresolved_at(holder, line, kind, reference, reason, base)

    def run(self):
        for path, rec in sorted(self.records.items()):
            data = None
            if not rec["symlink"]:
                try:
                    data = read_bytes(self.plant.root / rec["repo"],
                                      posixpath.relpath(path, rec["repo"]) if rec["repo"] != "." else path)
                except (OSError, Unreadable):
                    data = None
            rec["language"] = language_of(path, data) if not rec["symlink"] else language_of(path, b"")
            if rec["language"] not in LINK_BEARING or rec["symlink"]:
                continue
            try:
                if data is None:
                    raise Unreadable("unreadable")
                text = data.decode("utf-8")
                {"python": self.python, "shell": self.shell}.get(rec["language"], self.script)(rec, text)
            except (Unreadable, UnicodeDecodeError, SyntaxError, ValueError, RecursionError, MemoryError):
                self.opaque = [o for o in self.opaque if o["holder"] != path]
                self.unresolved = [u for u in self.unresolved if u["holder"] != path]
                self.links = {l for l in self.links if l[0] != path}
                self.opaque_at(path, None, "", "unreadable")
        self.mark_generated()

    # -- resolution
    def resolve_text(self, holder: str, text: str, directories: bool):
        """A shell argument or path literal: holder-directory-relative, then
        each `/`-suffix of the string, longest first, relative to the holder's
        repository and then to the plant root. ("file", path, exact) for a
        file, exact when the whole string names it from the holder or its
        repository root; ("dir", files) for a directory, only when
        `directories` and the string holds a `/`; None when it names nothing.
        A string with no named segment ("/", "./", "$ROOT/") never resolves."""
        segs = text.rstrip("/").split("/")
        if not any(named(s) for s in segs):
            return None
        hdir = posixpath.dirname(holder)
        repo = self.records[holder]["repo"]
        tries = [(joined(hdir, text), True)]
        for k in range(len(segs)):
            if not any(named(s) for s in segs[k:]):
                break
            suffix = "/".join(segs[k:])
            tries.append((joined(repo, suffix), k == 0))
            if repo != ".":
                tries.append((inside(suffix), False))
        for cand, exact in tries:
            if cand in (None, "."):
                continue
            if cand in self.files:
                return ("file", cand, exact)
            if directories and "/" in text and cand in self.under:
                return ("dir", self.under[cand])
        return None

    def path_literal(self, holder, text, line):
        """A quoted string read as a path: a `maybe` link to the file, or to
        each file under the directory, it names; nothing when it names none."""
        if not text or len(text) > LITERAL_MAX or "://" in text or any(c.isspace() for c in text):
            return False
        hit = self.resolve_text(holder, text, directories=True)
        if hit is None:
            return False
        self.literal_hit(holder, hit, line)
        return True

    def literal_hit(self, holder, hit, line):
        if hit[0] == "file":
            self.link(holder, hit[1], "path-literal", "path-literal", line)
        elif len(hit[1]) > DIR_LINK_MAX:
            self.opaque_at(holder, line, "", "walks-tree")
        else:
            for target in hit[1]:
                self.link(holder, target, "path-literal", "directory", line)

    def pick(self, *cands):
        return next((c for c in cands if c in self.files), None)

    def module_hits(self, base: str, parts, names) -> list:
        """The module at `base` itself; else each imported name that is a
        module beside it."""
        if parts:
            hit = self.pick(base + ".py", base + "/__init__.py")
            if hit:
                return [hit]
        prefix = "" if base in ("", ".") else base + "/"
        return [h for n in names if (h := self.pick(f"{prefix}{n}.py", f"{prefix}{n}/__init__.py"))]

    def module(self, holder, dotted, names=(), level=0, line=0, kind="import", reference=None):
        """The Python module rule: relative imports from the holder's package
        (`exact`); else the holder's directory, then its repository root, then
        the inventory files ending in the module's path: one is `resolved`,
        several `ambiguous`, none external."""
        parts = [p for p in (dotted or "").split(".") if p]
        names = [n for n in names if n != "*"]
        hdir = posixpath.dirname(holder)
        if level:
            pkg = joined(hdir, "/".join([".."] * (level - 1))) if level > 1 else (hdir or ".")
            base = joined(pkg, "/".join(parts)) if pkg is not None and parts else pkg
            ref = reference or "." * level + (dotted or "")
            if base is None:
                self.missing(holder, line, kind, ref, None)
                return
            hits = self.module_hits(base, parts, names)
            if not hits and not parts:
                hits = [h for h in [self.pick(joined(pkg, "__init__.py"))] if h]
            if not hits:
                self.missing(holder, line, kind, ref, joined(base, names[0]) if names and not parts else base)
            for h in hits:
                self.link(holder, h, kind, "exact", line)
            return
        if not parts:
            return
        rel = "/".join(parts)
        for d in (hdir, self.records[holder]["repo"]):
            base = joined(d, rel)
            hits = self.module_hits(base, parts, names) if base else []
            if hits:
                for h in hits:
                    self.link(holder, h, kind, "resolved", line)
                return
        ends = (rel + ".py", rel + "/__init__.py")
        found = sorted({p for e in ends for p in self.by_name.get(e.rsplit("/", 1)[-1], [])
                        if p == e or p.endswith("/" + e)})
        for target in found:
            self.link(holder, target, kind, "resolved" if len(found) == 1 else "ambiguous", line)

    # -- Python, read by ast
    def python(self, rec, text):
        holder = rec["path"]
        tree = ast.parse(text)
        names = {}                            # a bound name -> the dotted thing it names
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.asname:
                        names[a.asname] = a.name
                    else:
                        names[a.name.split(".")[0]] = a.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                for a in node.names:
                    names[a.asname or a.name] = f"{node.module}.{a.name}"

        def qual(f):
            if isinstance(f, ast.Name):
                return names.get(f.id, f.id)
            if isinstance(f, ast.Attribute):
                inner = qual(f.value)
                return f"{inner}.{f.attr}" if inner else ""
            return ""

        def is_file(n):
            return isinstance(n, ast.Name) and n.id == "__file__"

        def anchored(arg):
            """(levels up from the holder's directory, the literal operands)
            of a path anchored at __file__ in one of the two shapes, or None."""
            lits, n = [], arg
            while isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div) and \
                    isinstance(n.right, ast.Constant) and isinstance(n.right.value, str):
                lits.insert(0, n.right)
                n = n.left
            ups = 0
            while lits and isinstance(n, ast.Attribute) and n.attr == "parent":
                ups, n = ups + 1, n.value
            if ups and isinstance(n, ast.Call) and not n.args and not n.keywords and \
                    isinstance(n.func, ast.Attribute) and n.func.attr in ("resolve", "absolute"):
                n = n.func.value
            if ups and isinstance(n, ast.Call) and qual(n.func) == "pathlib.Path" and \
                    len(n.args) == 1 and not n.keywords and is_file(n.args[0]):
                return ups - 1, lits
            if isinstance(arg, ast.Call) and qual(arg.func) == "os.path.join" and len(arg.args) >= 2 and \
                    all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in arg.args[1:]):
                d, k = arg.args[0], 0
                while isinstance(d, ast.Call) and qual(d.func) == "os.path.dirname" and len(d.args) == 1:
                    d, k = d.args[0], k + 1
                if k and (is_file(d) or isinstance(d, ast.Call) and len(d.args) == 1 and is_file(d.args[0])
                          and qual(d.func) in ("os.path.abspath", "os.path.realpath")):
                    return k - 1, list(arg.args[1:])
            return None

        consumed = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                consumed.update(id(v) for v in node.values)
        hdir = posixpath.dirname(holder)

        def literal_resolves(arg):
            return any(isinstance(c, ast.Constant) and isinstance(c.value, str)
                       and self.resolve_text(holder, c.value, True) for c in ast.walk(arg))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.module(holder, a.name, line=node.lineno)
            elif isinstance(node, ast.ImportFrom):
                if node.module != "__future__":
                    self.module(holder, node.module, [a.name for a in node.names], node.level, node.lineno)
            elif isinstance(node, ast.Call):
                q = qual(node.func)
                last = node.func.attr if isinstance(node.func, ast.Attribute) else \
                    node.func.id if isinstance(node.func, ast.Name) else ""
                last = q.rsplit(".", 1)[-1] if q else last
                kw = {k.arg: k.value for k in node.keywords}
                if last == "import_module":
                    arg = node.args[0] if node.args else kw.get("name")
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        consumed.add(id(arg))
                        self.module(holder, arg.value.lstrip("."), (), len(arg.value) - len(arg.value.lstrip(".")),
                                    node.lineno, reference=arg.value)
                    elif arg is not None and not literal_resolves(arg):
                        self.opaque_at(holder, node.lineno, ast.unparse(arg), "dynamic-nonliteral")
                elif last in ("spec_from_file_location", "run_path"):
                    pos, key = (1, "location") if last == "spec_from_file_location" else (0, "path_name")
                    arg = node.args[pos] if len(node.args) > pos else kw.get(key)
                    if arg is None:
                        continue
                    shape = anchored(arg)
                    if shape is None:
                        if not (isinstance(arg, ast.Constant) or literal_resolves(arg)):
                            self.opaque_at(holder, node.lineno, ast.unparse(arg), "dynamic-nonliteral")
                        continue
                    ups, lits = shape
                    consumed.update(id(c) for c in lits)
                    target = joined(hdir, "/".join([".."] * ups + [c.value for c in lits]))
                    if target in self.files:
                        self.link(holder, target, "import", "exact", arg.lineno)
                    else:
                        self.missing(holder, arg.lineno, "import", "/".join(c.value for c in lits), target)
                elif q in PY_WALKS or last in ("glob", "rglob") and q != "glob.glob" and \
                        isinstance(node.func, ast.Attribute):
                    root = (node.args[0] if node.args else None) if q in PY_WALKS else node.func.value
                    if isinstance(root, ast.Call) and len(root.args) == 1 and not root.keywords:
                        root = root.args[0] if qual(root.func) == "pathlib.Path" else root
                    if not (isinstance(root, ast.Constant) and isinstance(root.value, str)):
                        self.opaque_at(holder, node.lineno, ast.unparse(root) if root is not None else q,
                                       "walks-tree")
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in consumed:
                self.path_literal(holder, node.value, node.lineno)

    # -- shell, read a line at a time
    @staticmethod
    def shell_words(line: str) -> list:
        """The words of one shell line, comments dropped: each a pair of its
        text with quotes removed and the quoted strings it holds; None marks
        a command separator."""
        words, text, quoted, started, i, n = [], [], [], False, 0, len(line)

        def end():
            nonlocal text, quoted, started
            if started:
                words.append(("".join(text), quoted))
            text, quoted, started = [], [], False

        while i < n:
            c = line[i]
            if c in " \t\r":
                end()
            elif c == "#" and not started:
                break
            elif c in ";|&()`":
                end()
                words.append(None)
            elif c in "<>":
                end()
            elif c == "\\":
                text.append(line[i + 1:i + 2])
                started, i = True, i + 1
            elif c in "'\"":
                j = line.find(c, i + 1)
                while c == '"' and j > 0 and line[j - 1] == "\\":
                    j = line.find(c, j + 1)
                j = n if j < 0 else j
                text.append(line[i + 1:j])
                quoted.append(line[i + 1:j])
                started, i = True, j
            else:
                text.append(c)
                started = True
            i += 1
        end()
        return words

    def invoke(self, holder, word, line):
        """An invoke argument: a link to the file it names, a pure variable
        or a variable past its leading segments `dynamic-nonliteral`, else an
        unresolved `relative-no-file` (`outside-repository`)."""
        if not word or VARIABLE.match(word.strip('"')):
            if word:
                self.opaque_at(holder, line, word, "dynamic-nonliteral")
            return
        segs = word.split("/")
        lead = 0
        while lead < len(segs) - 1 and "$" in segs[lead]:
            lead += 1
        if any("$" in s for s in segs[lead:]):
            self.opaque_at(holder, line, word, "dynamic-nonliteral")
            return
        hit = self.resolve_text(holder, word, directories=False)
        if hit:
            self.link(holder, hit[1], "invoke", "exact" if hit[2] else "resolved", line)
        elif lead:
            self.missing(holder, line, "invoke", word,
                         joined(self.records[holder]["repo"], "/".join(segs[lead:])))
        else:
            self.missing(holder, line, "invoke", word, joined(posixpath.dirname(holder), word))

    def shell(self, rec, text):
        holder = rec["path"]
        for lineno, line in enumerate(text.split("\n"), 1):
            words = self.shell_words(line)
            used = set()
            command = True
            for k, w in enumerate(words):
                if w is None:
                    command = True
                    continue
                t, at_command = w[0], command
                command = t in ("then", "do", "else", "!", "if", "while", "until", "exec", "time",
                                "command", "env", "sudo") or "=" in t and not t.startswith("-") \
                    and at_command
                rest = [x for x in words[k + 1:]]
                follow = rest[:rest.index(None)] if None in rest else rest
                if posixpath.basename(t) in INTERPRETERS:
                    j = 0
                    while j < len(follow) and follow[j][0].startswith("-") and follow[j][0] not in ("-", "-c", "-m"):
                        j += 2 if follow[j][0] in PY_ARG_OPTIONS else 1
                    if j >= len(follow) or follow[j][0] in ("-", "-c"):
                        continue
                    if follow[j][0] == "-m":
                        if j + 1 < len(follow):
                            used.update(map(id, [follow[j + 1]]))
                            self.module(holder, follow[j + 1][0], line=lineno, kind="invoke")
                        continue
                    used.add(id(follow[j]))
                    self.invoke(holder, follow[j][0], lineno)
                elif at_command and t in ("source", ".") and follow:
                    used.add(id(follow[0]))
                    self.invoke(holder, follow[0][0], lineno)
                elif at_command and (t == "find" or t == "git" and follow and follow[0][0] == "ls-files"):
                    roots = [x for x in follow[:1] if t == "find" and not x[0].startswith("-")]
                    if roots and roots[0][0] and "$" not in roots[0][0]:
                        hit = self.resolve_text(holder, roots[0][0].rstrip("/") + "/", True)
                        if hit:
                            used.add(id(roots[0]))
                            self.literal_hit(holder, hit, lineno)
                    else:
                        self.opaque_at(holder, lineno, roots[0][0] if roots else t, "walks-tree")
            for w in words:
                if w is not None and id(w) not in used:
                    for q in w[1]:
                        self.path_literal(holder, q, lineno)

    # -- TypeScript and JavaScript, comment-stripped, a line at a time
    @staticmethod
    def strip_comments(text: str) -> str:
        """`text` with `//` and `/* */` comments blanked outside string
        literals; every newline kept, so line numbers stand."""
        out, i, n = [], 0, len(text)
        while i < n:
            c = text[i]
            if c in "'\"`":
                j = i + 1
                while j < n and text[j] != c and (c == "`" or text[j] != "\n"):
                    j += 2 if text[j] == "\\" else 1
                out.append(text[i:j + 1])
                i = j + 1
            elif text.startswith("//", i):
                j = text.find("\n", i)
                i = n if j < 0 else j
            elif text.startswith("/*", i):
                j = text.find("*/", i + 2)
                j = n if j < 0 else j + 2
                out.append("".join(ch if ch == "\n" else " " for ch in text[i:j]))
                i = j
            else:
                out.append(c)
                i += 1
        return "".join(out)

    def script(self, rec, text):
        holder = rec["path"]
        lines = self.strip_comments(text).split("\n")
        i = 0
        while i < len(lines):
            line, lineno, nxt = lines[i], i + 1, i + 1
            if OPEN_CALL.search(line):
                j, taken, parts = i + 1, 0, [line]
                while j < len(lines) and taken < JOIN_MAX:
                    if lines[j].strip():
                        parts.append(lines[j])
                        taken += 1
                    j += 1
                    if ")" in parts[-1] and len(parts) > 1:
                        line, nxt = " ".join(parts), j
                        break
            self.script_line(holder, line, lineno)
            i = nxt

    def script_line(self, holder, line, lineno):
        spans = []
        for m in TS_FROM.finditer(line):
            spans.append(m.span(2))
            self.specifier(holder, m.group(2), lineno)
        for m in TS_BARE_IMPORT.finditer(line):
            spans.append(m.span(2))
            self.specifier(holder, m.group(2), lineno)
        for m in TS_CALL.finditer(line):
            arg = TS_LITERAL_ARG.match(line, m.end())
            if arg:
                spans.append(arg.span(2))
                self.specifier(holder, arg.group(2), lineno)
            elif not self.ts_literal(holder, line[m.end():], lineno, dry=True):
                self.opaque_at(holder, lineno, line[m.end():].split(")")[0].strip(), "dynamic-nonliteral")
        for m in TS_WALK.finditer(line):
            if line[m.end():m.end() + 1] not in ("'", '"', "`"):
                self.opaque_at(holder, lineno, line[m.end():].split(")")[0].strip(), "walks-tree")
        for m in TS_STRING.finditer(line):
            k = next(g for g in (1, 2, 3) if m.group(g) is not None)
            if not any(a <= m.start(k) < b or m.start(k) == a for a, b in spans):
                self.ts_literal(holder, m.group(k), lineno)

    def ts_literal(self, holder, text, lineno, dry=False):
        """A TS/JS path literal: only a relative or alias-prefixed string, by
        the specifier rules, as a `maybe` link. With `dry`, whether the first
        string of an argument resolves, recording nothing."""
        if dry:
            m = TS_STRING.match(text.lstrip())
            text = next((g for g in m.groups() if g is not None), "") if m else ""
        if not text or len(text) > LITERAL_MAX or any(c.isspace() for c in text) or "://" in text:
            return False
        hit = self.ts_target(holder, text, literal=True)
        if hit and not dry:
            self.literal_hit(holder, ("file", hit[0], False) if isinstance(hit[0], str) else ("dir", hit[0]),
                             lineno)
        return bool(hit)

    def probe(self, base):
        """(file, exact) for a TS/JS base path probed as written, then a
        written .js as .ts, then with each extension, then as an index."""
        if base is None:
            return None
        if base in self.files:
            return base, True
        ext = posixpath.splitext(base)[1]
        cands = [base[:-len(ext)] + e for e in JS_TO_TS] if ext in JS_WRITTEN else []
        cands += [base + e for e in TS_PROBE] + [base + "/index" + e for e in TS_PROBE]
        hit = self.pick(*cands)
        return (hit, False) if hit else None

    def tsconfig(self, holder):
        """The nearest tsconfig.json or jsconfig.json up from the holder inside
        its repository, read with its `extends` chain: a dict of `paths`
        (pattern, targets) and `base_url`, None when there is none, or
        "unavailable" when the chain cannot be read."""
        repo = self.records[holder]["repo"]
        d = posixpath.dirname(holder)
        while True:
            cfg = self.pick(*(joined(d, n) for n in ("tsconfig.json", "jsconfig.json")))
            if cfg:
                if cfg not in self._tsconfig:
                    self._tsconfig[cfg] = self.read_tsconfig(cfg)
                return self._tsconfig[cfg]
            if d in ("", ".", repo):
                return None
            d = posixpath.dirname(d)

    def read_tsconfig(self, top):
        layers, chain, count = [], [], [0]

        def follow(path):
            if path in chain or count[0] >= EXTENDS_MAX:
                raise ValueError("extends cycle or chain too long")
            count[0] += 1
            chain.append(path)
            rec = self.records[path]
            data = jsonc(read_text(self.plant.root / rec["repo"], posixpath.relpath(path, rec["repo"])))
            if not isinstance(data, dict):
                raise ValueError("not an object")
            ext = data.get("extends")
            exts = [ext] if isinstance(ext, str) else ext if isinstance(ext, list) else []
            if ext is not None and not all(isinstance(e, str) for e in exts) or \
                    not isinstance(ext, (str, list, type(None))):
                raise ValueError("extends is not a string")
            for e in exts:
                if e.startswith(("./", "../")):
                    base = joined(posixpath.dirname(path), e)
                    parent = self.pick(base, (base or "") + ".json") if base else None
                    if not parent:
                        raise ValueError(f"extends names {e!r}, which the inventory lacks")
                    follow(parent)
            chain.pop()
            layers.append((path, data))

        try:
            follow(top)
        except (ValueError, RecursionError, MemoryError, OSError, Unreadable):
            return "unavailable"
        paths, paths_dir, base_url = None, None, None
        for path, data in layers:
            co = data.get("compilerOptions", {})
            if not isinstance(co, dict):
                return "unavailable"
            here = posixpath.dirname(path)
            if "baseUrl" in co:
                if not isinstance(co["baseUrl"], str):
                    return "unavailable"
                base_url = joined(here, co["baseUrl"]) or "."
            if "paths" in co:
                p = co["paths"]
                if not isinstance(p, dict) or not all(
                        isinstance(v, list) and all(isinstance(t, str) for t in v) for v in p.values()):
                    return "unavailable"
                paths, paths_dir = p, here
        root = base_url if base_url is not None else paths_dir
        return {"paths": [(k, v) for k, v in (paths or {}).items()], "root": root, "base_url": base_url}

    @staticmethod
    def alias_bases(cfg, spec):
        """The base paths the best-matching `paths` pattern maps `spec` to,
        or None when no pattern matches."""
        best, star, targets = -1, "", None
        for pattern, ts in cfg["paths"]:
            if "*" in pattern:
                pre, suf = pattern.split("*", 1)
                if spec.startswith(pre) and spec.endswith(suf) and len(spec) >= len(pre) + len(suf) \
                        and len(pre) > best:
                    best, star, targets = len(pre), spec[len(pre):len(spec) - len(suf)], ts
            elif pattern == spec and len(pattern) > best:
                best, star, targets = len(pattern), "", ts
        if targets is None:
            return None
        return [joined(cfg["root"] or "", t.replace("*", star, 1)) for t in targets]

    def packages(self):
        """Workspace package name -> its directory, from each package.json."""
        if self._packages is None:
            self._packages = {}
            for path in self.by_name.get("package.json", []):
                rec = self.records[path]
                try:
                    name = json.loads(read_text(self.plant.root / rec["repo"],
                                                posixpath.relpath(path, rec["repo"]))).get("name")
                except (OSError, Unreadable, ValueError, RecursionError, MemoryError, AttributeError):
                    continue
                if isinstance(name, str):
                    self._packages.setdefault(name, posixpath.dirname(path))
        return self._packages

    def specifier(self, holder, spec, line):
        """One TS/JS import specifier, by the one resolution order."""
        path_part = spec.split("?", 1)[0]
        asset = "?" in spec or posixpath.splitext(path_part)[1].lower() in ASSETS
        if path_part.startswith(("./", "../")) or path_part in (".", ".."):
            self.target(holder, spec, line, [joined(posixpath.dirname(holder), path_part)], asset,
                        "relative-no-file")
            return
        cfg = self.tsconfig(holder)
        package = bool(NPM_NAME.match(spec))
        if cfg == "unavailable":
            if not package:
                self.opaque_at(holder, line, spec, "alias-config-unavailable")
            else:
                self.workspace(holder, spec, line)
            return
        if cfg:
            bases = self.alias_bases(cfg, path_part)
            if bases is not None and (asset or any(self.probe(b) for b in bases) or not package):
                self.target(holder, spec, line, bases, asset, "alias-no-file", relative=False)
                return
            if cfg["base_url"] is not None:
                hit = self.probe(joined(cfg["base_url"], path_part))
                if hit:
                    self.link(holder, hit[0], "import", "resolved", line)
                    return
        if package:
            self.workspace(holder, spec, line)

    def target(self, holder, spec, line, bases, asset, missing, relative=True):
        """Link a relative or alias specifier to the first base that probes
        to a file; an asset is never probed; else an unresolved record."""
        if not bases or bases[0] is None:
            self.missing(holder, line, "import", spec, None)
            return
        if asset:
            if bases[0] in self.files:
                self.link(holder, bases[0], "import", "exact", line)
            else:
                self.unresolved_at(holder, line, "import", spec, "asset", bases[0])
            return
        for b in bases:
            hit = self.probe(b)
            if hit:
                self.link(holder, hit[0], "import", "exact" if hit[1] and relative else "resolved", line)
                return
        self.missing(holder, line, "import", spec, bases[0], missing)

    def workspace(self, holder, spec, line):
        d = self.packages().get(spec)
        if d is None:
            return
        files = [f for f in (self.under.get(d, []) if d else sorted(self.files)) if f != holder]
        if len(files) > DIR_LINK_MAX:
            self.opaque_at(holder, line, spec, "walks-tree")
        for f in files if len(files) <= DIR_LINK_MAX else []:
            self.link(holder, f, "import", "workspace-package", line)

    def ts_target(self, holder, text, literal=True):
        """A TS/JS path literal's file, as (file,), or its directory's files,
        as (files,); None unless it is relative or alias-prefixed."""
        if text.startswith(("./", "../")):
            bases = [joined(posixpath.dirname(holder), text)]
        else:
            cfg = self.tsconfig(holder)
            bases = self.alias_bases(cfg, text) if isinstance(cfg, dict) else None
        for b in bases or []:
            hit = self.probe(b)
            if hit:
                return (hit[0],)
            if b and "/" in text and b.rstrip("/") in self.under:
                return (self.under[b.rstrip("/")],)
        return None

    def mark_generated(self):
        """Ask Git, once per repository, which unresolved bases it ignores:
        those are `generated`. Paths go on stdin as `./<path>`, never argv."""
        asks = {}
        for u in self.unresolved:
            if u["reason"] in ("relative-no-file", "alias-no-file") and u["base"]:
                repo = self.plant.repo_of(u["base"])
                asks.setdefault(repo, []).append(u)
        for repo, recs in sorted(asks.items()):
            rel = {id(u): u["base"] if repo == "." else posixpath.relpath(u["base"], repo) for u in recs}
            stdin = b"".join(b"./" + rel[id(u)].encode("utf-8", "surrogateescape") + b"\0" for u in recs)
            try:
                out = source_paths.git(self.plant.root / repo, "check-ignore", "--stdin", "-z",
                                       input=stdin, ok=(0, 1))
            except source_paths.GitFailed:
                continue          # no answer: the records keep their reason
            ignored = {p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p}
            for u in recs:
                if "./" + rel[id(u)] in ignored:
                    u["reason"] = "generated"


# --- the index and its cache -------------------------------------------------
def incomplete(reason, subject, candidates=(), detail=None):
    return {"reason": reason, "subject": subject, "candidates": sorted(candidates), "detail": detail}


def digest(*chunks: bytes) -> str:
    h = hashlib.sha256()
    for c in chunks:
        h.update(c)
    return h.hexdigest()


def tool_digest() -> str:
    """This tool's bytes, then each sibling's, in SIBLINGS order."""
    here = Path(__file__).resolve().parent
    chunks = [Path(__file__).resolve().read_bytes()]
    for name in SIBLINGS:
        try:
            chunks.append((here / name).read_bytes())
        except OSError:
            chunks.append(b"")
    return digest(*chunks)


def derive(plant: Plant, repos: list) -> dict:
    """The index body: inventory, links, opaque and unresolved records, each
    sorted, holding plant-relative paths only."""
    records = plant.inventory(repos)
    ex = Extract(plant, records)
    ex.run()
    inventory = [{k: r[k] for k in SHAPE["inventory"]} for _, r in sorted(records.items())]
    links = [dict(zip(("holder", "target", "kind", "link", "found", "line"), l))
             for l in sorted(ex.links, key=lambda l: (l[0], l[1], l[2], l[5], l[4]))]
    opaque = sorted(ex.opaque, key=lambda o: (o["holder"], -1 if o["line"] is None else o["line"],
                                              o["reason"], o["reference"]))
    unresolved = sorted(ex.unresolved, key=lambda u: (u["holder"], u["line"], u["reference"], u["reason"]))
    return {"inventory": inventory, "links": links, "opaque": opaque, "unresolved": unresolved}


def cache_problem(doc, key) -> str:
    """Why `doc` is not a usable index for `key`, or None. The cache is
    untrusted: every path must be clean and relative, every endpoint an
    inventory path, every enum one SPEC-0007 §6 lists."""
    if not isinstance(doc, dict) or set(doc) != {"schema", "key", "inventory", "links", "opaque", "unresolved"}:
        return "cache unreadable: not an index document"
    if doc["schema"] != INDEX_SCHEMA:
        return "cache unreadable: another schema"

    def clean(p):
        return isinstance(p, str) and p not in ("", ".") and "\0" not in p and source_paths.relative(p)

    paths = set()
    for part, fields in SHAPE.items():
        rows = doc[part]
        if not isinstance(rows, list) or not all(isinstance(r, dict) and set(r) == fields for r in rows):
            return f"cache unreadable: bad {part}"
    for r in doc["inventory"]:
        if not (clean(r["path"]) and (r["repo"] == "." or clean(r["repo"])) and isinstance(r["hash"], str)
                and r["language"] in ENUMS["language"] and r["test"] in ENUMS["test"]):
            return "cache unreadable: bad inventory record"
        paths.add(r["path"])

    def line_ok(v, nullable=False):
        return v is None and nullable or type(v) is int and v > 0

    for r in doc["links"]:
        if not (r["holder"] in paths and r["target"] in paths and r["kind"] in ENUMS["kind"]
                and r["link"] in ENUMS["link"] and r["found"] in ENUMS["found"] and line_ok(r["line"])):
            return "cache unreadable: bad link"
    for r in doc["opaque"]:
        if not (r["holder"] in paths and r["reason"] in ENUMS["opaque"] and isinstance(r["reference"], str)
                and line_ok(r["line"], True)):
            return "cache unreadable: bad opaque record"
    for r in doc["unresolved"]:
        if not (r["holder"] in paths and r["reason"] in ENUMS["unresolved"] and isinstance(r["reference"], str)
                and r["kind"] in ("import", "invoke") and line_ok(r["line"])
                and (r["base"] is None or clean(r["base"]))):
            return "cache unreadable: bad unresolved record"
    return None if doc["key"] == key else "key changed"


def read_cache(root: Path, key):
    """(index, None) when the cache holds a usable index for `key`; else
    (None, why): None when there is no cache at all, else the reason."""
    try:
        dir_fd = source_paths.open_dir(root, *CACHE_DIR.split("/"))
    except FileNotFoundError:
        return None, None
    except OSError as e:
        return None, f"cache unreadable: {CACHE_DIR}/ is unusable ({e.strerror or type(e).__name__})"
    try:
        opened = source_paths.open_regular(CACHE_NAME, dir_fd=dir_fd)
    except FileNotFoundError:
        return None, None
    except OSError as e:
        return None, f"cache unreadable: {e.strerror or type(e).__name__}"
    finally:
        os.close(dir_fd)
    if opened is None:
        return None, "cache unreadable: not a regular file"
    fd, size = opened
    try:
        if size > CACHE_MAX_BYTES:
            return None, "cache unreadable: too large"
        with os.fdopen(fd, "rb", closefd=False) as f:
            raw = f.read(CACHE_MAX_BYTES + 1)
    finally:
        os.close(fd)
    try:
        doc = json.loads(raw)
    except (ValueError, RecursionError, MemoryError):
        return None, "cache unreadable: not JSON"
    problem = cache_problem(doc, key)
    return (doc, None) if problem is None else (None, problem)


def write_cache(root: Path, doc: dict):
    """Write the index under `.cypress/source-index/`, never creating
    `.cypress/` or following a symlink: the inner `.gitignore` first, then
    `index.json`, each by exclusive temp file and atomic replace. The reason
    nothing was written, or None."""
    data = (json.dumps(doc, sort_keys=True, indent=1, ensure_ascii=True) + "\n").encode("ascii")
    if len(data) > CACHE_MAX_BYTES:
        return "the index is larger than CACHE_MAX_BYTES"
    try:
        dir_fd = source_paths.open_dir(root, *CACHE_DIR.split("/"), create=True)
    except FileNotFoundError:
        return "no .cypress/ directory; this tool never creates it"
    except OSError as e:
        return (f"{CACHE_DIR}/ is unusable ({e.strerror or type(e).__name__}); "
                f"a symlink is never followed")
    try:
        ignore = CACHE_IGNORE.encode()
        try:
            opened = source_paths.open_regular(".gitignore", dir_fd=dir_fd)
        except FileNotFoundError:
            opened = None
        current = None
        if opened:
            fd, size = opened
            try:
                current = os.read(fd, len(ignore) + 1)
            finally:
                os.close(fd)
        if current != ignore:
            source_paths.atomic_write(dir_fd, ".gitignore", ignore, TEMP_PREFIX, f"{CACHE_DIR}/.gitignore")
        source_paths.atomic_write(dir_fd, CACHE_NAME, data, TEMP_PREFIX, f"{CACHE_DIR}/{CACHE_NAME}")
    except source_paths.Refused as e:
        return str(e)
    except OSError as e:
        return f"{CACHE_DIR}/ not written ({e.strerror or type(e).__name__})"
    finally:
        os.close(dir_fd)
    return None


def load_index(root: Path, force: bool):
    """(index body or None, cache {status, reason}, incomplete records)."""
    plant = Plant(root)
    problems = []
    if plant.config_refused:
        problems.append(incomplete("config-refused", CONFIG_PATH, detail=plant.config_refused))
    empty = {"inventory": [], "links": [], "opaque": [], "unresolved": []}
    if not plant.repos:
        problems.append(incomplete("no-repository", "."))
        return plant, empty, {"status": "not-written", "reason": "no governed Git repository"}, problems
    try:
        repos = plant.key_repositories(problems)
        key = {"python": f"{sys.version_info.major}.{sys.version_info.minor}",
               "tool": tool_digest(),
               "config": digest(plant.config_raw, repr(plant.test_globs).encode()),
               "repositories": repos}
        readable = [r["path"] for r in repos]
        cached, why = read_cache(root, key)
        if cached is not None and not force:
            return plant, {k: cached[k] for k in empty}, {"status": "reused", "reason": None}, problems
        body = derive(plant, readable)
    except source_paths.GitMissing:
        problems = [p for p in problems if p["reason"] == "config-refused"]
        problems.append(incomplete("git-unavailable", "git"))
        return plant, empty, {"status": "not-written", "reason": "git is not on PATH"}, problems
    except source_paths.GitFailed as e:
        problems.append(incomplete("repository-unreadable", ".", detail=str(e)))
        return plant, empty, {"status": "not-written", "reason": str(e)}, problems
    if len(readable) < len(plant.repos):
        return plant, body, {"status": "not-written", "reason": "a repository is unreadable"}, problems
    existed = cached is not None or why is not None
    failed = write_cache(root, {"schema": INDEX_SCHEMA, "key": key, **body})
    if failed:
        return plant, body, {"status": "not-written", "reason": failed}, problems
    reason = "build forced" if force and existed else why
    return plant, body, {"status": "rebuilt" if existed else "built", "reason": reason}, problems


# --- answers -----------------------------------------------------------------
def safe(text) -> str:
    """Text for the text view: every character outside printable ASCII is `?`."""
    return "".join(c if " " <= c <= "~" else "?" for c in str(text))


def answer(query: str, args, root: Path) -> dict:
    plant, body, cache, problems = load_index(root, force=query == "build")
    doc = {"schema": ANSWER_SCHEMA, "query": query, "inputs": [], "cache": cache, "incomplete": problems}
    if query == "build":
        doc.update(body)
    elif query == "anchors":
        doc["files"] = []
    else:
        doc["depth"] = args.depth
        doc.update({"dependents": []} if query == "impact" else {"tests": [], "always_run": []})
        doc["floor"] = []
    return doc


def text_view(doc: dict) -> list:
    cache = doc["cache"]
    out = [safe(f"Cache: {cache['status']}" + (f" ({cache['reason']})" if cache["reason"] else ""))]
    if doc["query"] == "build":
        links = doc["links"]
        certain = sum(1 for l in links if l["link"] == "certain")
        out.append(f"Index: {len(doc['inventory'])} file(s), "
                   f"{sum(1 for r in doc['inventory'] if r['test'] == 'test')} test(s), "
                   f"{certain} certain and {len(links) - certain} maybe link(s), "
                   f"{len(doc['opaque'])} opaque and {len(doc['unresolved'])} unresolved record(s)")
    for r in doc["incomplete"]:
        out.append(safe(f"- incomplete: {r['reason']}: {r['subject']}"
                        + (f" ({r['detail']})" if r["detail"] else "")))
    if doc["incomplete"]:
        out.append(safe(ACTION_LINE[doc["query"]].format(
            reasons=", ".join(f"{r['reason']}: {r['subject']}" for r in doc["incomplete"]))))
    elif doc["query"] == "affected-tests":
        out.append(RECOMMEND_LINE)
    return out


# --- the command line ----------------------------------------------------------
class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Usage(message)


def parse(argv):
    ap = Parser(prog="source-index.py", description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="query", required=True, parser_class=Parser)
    b = sub.add_parser("build", help="derive the whole index and write the cache")
    b.add_argument("--json", action="store_true", help="print the answer as JSON")
    for name, helptext in (("impact", "the files that depend on the inputs"),
                           ("affected-tests", "the tests the inputs reach, and the always-run set"),
                           ("anchors", "the graph pages that cite the inputs")):
        q = sub.add_parser(name, help=helptext)
        if name != "anchors":
            q.add_argument("--depth", type=int, default=DEFAULT_DEPTH,
                           help=f"walk depth, 1 to {MAX_DEPTH} (default {DEFAULT_DEPTH})")
        q.add_argument("--all", action="store_true", help="every row, and the history pages named")
        q.add_argument("--json", action="store_true", help="print the answer as JSON")
        q.add_argument("paths", nargs="+", help="plant paths, or - to read one per stdin line")
    args = ap.parse_args(argv)
    if getattr(args, "depth", 1) is not None and not 1 <= getattr(args, "depth", 1) <= MAX_DEPTH:
        raise Usage(f"--depth takes 1 to {MAX_DEPTH}")
    return args


def main(argv=None) -> int:
    try:
        args = parse(sys.argv[1:] if argv is None else argv)
    except Usage as e:
        print(f"usage: source-index.py {{build|impact|affected-tests|anchors}} ...: {e}", file=sys.stderr)
        return 2
    doc = answer(args.query, args, Path.cwd())
    if args.json:
        sys.stdout.write(json.dumps(doc, sort_keys=True, indent=1, ensure_ascii=True) + "\n")
    else:
        sys.stdout.write("\n".join(text_view(doc)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
