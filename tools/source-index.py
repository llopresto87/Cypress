#!/usr/bin/env python3
"""source-index.py: what depends on what in a plant's code, derived without a model.

The tool inventories the code of every governed repository (the plant root
when it is a Git work tree, plus each nested work tree a node names in
`repo:`) and reads file-to-file links from it: Python imports and loads by
file path (read with `ast`, never imported or run), shell and Python
invocations, quoted path and directory literals (whole, or joined from
segments as in `ROOT / "tools" / "x.py"`), and TypeScript/JavaScript
import and require specifiers resolved through `tsconfig`/`jsconfig` paths.
Each link is `certain` or `maybe`, with the reason; a file whose references
cannot be pinned is an `opaque` record, and an import or invoke naming no
file is an `unresolved` record (SPEC-0007 §6).

Placed in a plant as `docs/graph/source-index.py` and run from the plant root:

    python3 docs/graph/source-index.py build [--json]
    python3 docs/graph/source-index.py impact         [--depth N] [--history] [--all] [--json] <path>... | -
    python3 docs/graph/source-index.py affected-tests [--depth N] [--history] [--all] [--json] <path>... | -
    python3 docs/graph/source-index.py anchors                  [--all] [--json] <path>... | - | --moved
    python3 docs/graph/source-index.py symbols                  [--all] [--json] <name>... | -

The same pass that reads the links reads each file's definitions for
`symbols`: Python's by `ast` (certain), shell functions and top-level or
exported TS/JS declarations by line-reading (maybe). `--history` adds the
files that changed together with an input in past commits, as a `maybe`
list of their own (SPEC-0007 §6 "Definitions", "History links"). `anchors
--moved` takes its inputs from the moved list of `code-anchor.py` beside this
file, so canonize needs no copied paths (SPEC-0007 §6 "Moved list").

The path rules (what is code, the governed repositories, the `repo:` claim
rule, the config's path patterns, the Git boundary, the blob hash, the atomic
write) are `source_paths.py`'s, the plant edge is
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
import time
from pathlib import Path
import importlib.util as _ilu
sys.dont_write_bytecode = True  # a query writes only under .cypress/source-index/: no __pycache__


def _loaded(spec):
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Each sibling is loaded in the anchored shape of SPEC-0007 §6 "Links", so the
# tool's own loads are certain links in the index it builds over the seed.
source_paths = _loaded(_ilu.spec_from_file_location(
    "cypress_source_paths", Path(__file__).resolve().parent / "source_paths.py"))
plant_walk = _loaded(_ilu.spec_from_file_location(
    "cypress_plant_walk", Path(__file__).resolve().parent / "plant_walk.py"))
frontmatter = _loaded(_ilu.spec_from_file_location(
    "cypress_frontmatter", Path(__file__).resolve().parent / "frontmatter.py"))

# --- constants and texts (SPEC-0007 §6): this file is their one home, except
# the path rules, whose home is source_paths.py. ---
INDEX_SCHEMA = "cypress.source-index/2"
ANSWER_SCHEMA = "cypress.source-index.answer/1"
DEFAULT_DEPTH = 3
MAX_DEPTH = 5
TEXT_MAX_ROWS = 40
LITERAL_MAX = 255
JOIN_MAX = 3
FILE_MAX_BYTES = 1048576
DIR_LINK_MAX = 200
EXTENDS_MAX = 16
CACHE_MAX_BYTES = 205520896        # 196 MiB
HISTORY_COMMITS = 500
HISTORY_MAX_FILES = 40
_NAME = r"[A-Za-z_$][A-Za-z0-9_$-]*"      # one name segment; shell and TS/JS definitions read it undotted
NAME_RE = re.compile(rf"{_NAME}(\.{_NAME})*")
CACHE_DIR = ".cypress/source-index"
CACHE_NAME = "index.json"
CACHE_IGNORE = "*\n"
CONFIG_PATH = "docs/graph/source-index.json"
TEST_DECLARATION = "docs/graph/spec-lint.py"     # TEST_GLOBS and SKIP_DIRS
SIBLINGS = ["source_paths.py", "plant_walk.py", "frontmatter.py"]
CODE_ANCHOR = "code-anchor.py"   # loaded beside the tool by `anchors --moved` alone; it shapes no index
TEMP_PREFIX = ".tmp-source-index-"
FLOOR_LINE = "Floor: {n} maybe row(s) every input reaches (opaque holders and their dependents):"
HISTORY_LINE = "History: {n} maybe row(s), files that changed together with an input (--history):"
MOVED_NONE_LINE = "Moved: no code moved since the code anchor."
UNDEFINED_LINE = ("{name}: no definition (read: Python definitions, shell functions, TS/JS declarations; "
                  "not read: {not_read}, which are not code)")   # {not_read}: the answer's not_read
BUILD_TIME_LINE = "Built in {seconds:.2f} s."
RECOMMEND_LINE = ("Recommendation only: the tests above and the always-run set, never only these; "
                  "verify decides what runs.")
ACTION_LINE = {
    "build": "Incomplete: {n} setup item(s) above, each with its fix ({reasons}).",
    "impact": "Incomplete: check by hand ({reasons}).",
    "affected-tests": "Incomplete: run the full suite ({reasons}).",
    "anchors": "Incomplete: review by hand ({reasons}).",
    "symbols": "Incomplete: search by hand ({reasons}).",
}
# §6 "Build report": the setup report `build` alone prints.
FIX_PREFIX = "  fix: "
BUILD_FIX = {               # one line under each record of that reason; every reason a build can give
    "git-unavailable": "install Git, then run from the plant root: python3 docs/graph/source-index.py build",
    "no-repository": ("the plant root is not a Git work tree and no node's repo: names a repository: if the "
                      "code lives in repositories below the plant root, let grow write the nodes whose repo: "
                      "names each (or write them); if the plant root is the code, run git init there and "
                      "commit; then run python3 docs/graph/source-index.py build"),
    "repository-unreadable": ("repair the repository the record names (git status must succeed in it), then run "
                              "python3 docs/graph/source-index.py build"),
    "config-refused": ("fix docs/graph/source-index.json: only the keys exclude, always_run and global_inputs, "
                       "each a list of strings; or delete the file to use the defaults"),
    "no-test-declaration": ("set TEST_GLOBS in docs/graph/spec-lint.py to a list of the plant's test-file "
                            "patterns (the owner confirms it; grow asks it with the plant facts)"),
    "no-test-files": ("TEST_GLOBS in docs/graph/spec-lint.py matches no file: set it to the folders that hold "
                      "the tests; while the plant has no tests, nothing to do"),
    "repo-unresolved": ("set the node's repo: to one plant-relative path that exists (a repository, a folder "
                        "or a file), or remove the line"),
    "repository-unnamed": ("write (or let grow write) a node whose repo: names this repository; if it is not "
                           "this plant's code, list it in the .gitignore of the repository that holds it; then "
                           "run python3 docs/graph/source-index.py build"),
}
TEST_NAME_PATTERNS = ["test_*.py", "*_test.py", "test_*.sh", "test-*.sh", "*_test.sh",
                      "*_test.go", "*.test.*", "*.spec.*", "*_spec.rb",
                      "*Test.java", "*Tests.java", "*Test.kt", "*Tests.kt",
                      "*Test.cs", "*Tests.cs", "*Test.php"]     # basenames, by the helper's path_matches
HINT_MAX_PATHS = 5
HINT_LINE = {               # in the order hints are listed
    "tests-outside-class": ("Hint: {count} file(s) named like tests are outside TEST_GLOBS, e.g. {paths}. Add "
                            "their folders to TEST_GLOBS in docs/graph/spec-lint.py, or list them under "
                            "\"exclude\" in docs/graph/source-index.json if they are not tests."),
    "class-holds-non-tests": ("Hint: {count} file(s) in the test class are not named like tests, e.g. {paths}. "
                              "List the ones that are not tests under \"exclude\" in "
                              "docs/graph/source-index.json; an \"exclude\" key, even [], ends this hint."),
    "config-pattern-unmatched": "Hint: {count} pattern(s) in docs/graph/source-index.json match no file: {patterns}.",
}
HINT_FIX = {                # under a hint of that kind; the other hints carry their fix in HINT_LINE
    "config-pattern-unmatched": (
        "correct each pattern in docs/graph/source-index.json to the files it means (a pattern with no \"/\" "
        "matches a file name, one with \"/\" a plant-relative path), or remove it; then run python3 "
        "docs/graph/source-index.py build"),
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
# "Plant test declaration"): no file under one of these directories is a test.
# The plant's `SKIP_DIRS` is read from spec-lint.py; this copy serves only when
# that assignment is absent or not strings.
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
    "opaque": {"dynamic-nonliteral", "walks-tree", "unreadable", "alias-config-unavailable",
               "unmapped-specifier"},
    "unresolved": {"relative-no-file", "alias-no-file", "outside-repository", "generated", "asset"},
    "symbol": {"function", "class", "variable", "type"},
    "read": {"ast": "certain", "line-reading": "maybe"},      # how a definition was found -> its link
}
SHAPE = {
    "inventory": {"path", "repo", "hash", "language", "test"},
    "links": {"holder", "target", "kind", "link", "found", "line"},
    "opaque": {"holder", "line", "reference", "reason"},
    "unresolved": {"holder", "line", "kind", "reference", "reason", "base"},
    "symbols": {"name", "path", "line", "kind", "link", "found"},
}
NPM_NAME = re.compile(r"^(?:node:.+|(?:@[a-z0-9-][a-z0-9._~-]*/)?[a-z0-9-][a-z0-9._~-]*(?:/.*)?)$")
SCHEME_LED = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")          # node:fs, bun:test, virtual:pwa
VARIABLE = re.compile(r"^\$(?:\{[^}]*\}|[A-Za-z_][A-Za-z0-9_]*|[@*#?$!0-9])$")
OPEN_CALL = re.compile(r"(?:(?<![\w$.])import|(?<![\w$.])require|(?<![\w$])vi\.mock"
                       r"|(?<![\w$])path\.(?:join|resolve))\s*\(\s*$")
JOIN_CALL = re.compile(r"(?<![\w$.])(?:os\.path\.join|path\.join|path\.resolve)\s*\(")
SHELL_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
TS_FROM = re.compile(r"(?<![\w$.])from\s*(['\"])([^'\"\n]*)\1")
TS_BARE_IMPORT = re.compile(r"(?<![\w$.])import\s*(['\"])([^'\"\n]*)\1")
TS_CALL = re.compile(r"(?:(?<![\w$.])import|(?<![\w$.])require|(?<![\w$])vi\.mock)\s*\(\s*")
TS_LITERAL_ARG = re.compile(r"(['\"`])([^'\"`\n$]*)\1\s*[,)]")
TS_WALK = re.compile(r"(?<![\w$])(?:readdirSync|readdir)\s*\(\s*")
TS_STRING = re.compile(r"'([^'\\\n]*)'|\"([^\"\\\n]*)\"|`([^`\\\n$]*)`")
GRAPH = "docs/graph"
HISTORY = ("docs/graph/plans/", "docs/graph/specs/", "docs/graph/decisions/")
FENCE = re.compile(r"^\s*(?:```|~~~)")
SPAN = re.compile(r"(`+)(.+?)\1")
# Definitions read a line at a time (SPEC-0007 §6 "Definitions"): each anchored
# at the line's start, the name NAME_RE without dots (_NAME).
SH_DEF = re.compile(rf"[ \t]*(?:function[ \t]+({_NAME})(?=[ \t({{;]|$)|({_NAME})[ \t]*\(\))")
TS_DEF = re.compile(r"(?:[ \t]+(?=export[ \t]))?(?:export[ \t]+)?(?:default[ \t]+)?(?:declare[ \t]+)?"
                    r"(?:abstract[ \t]+)?(?:async[ \t]+)?"
                    r"(function(?:[ \t]*\*[ \t]*|[ \t]+)|class[ \t]+|interface[ \t]+|type[ \t]+"
                    rf"|(?:const[ \t]+)?enum[ \t]+|const[ \t]+|let[ \t]+|var[ \t]+)({_NAME})")
TS_DEF_KIND = {"function": "function", "class": "class", "interface": "type", "type": "type", "enum": "type",
               "const": "variable", "let": "variable", "var": "variable"}   # by the declaration's last keyword


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
def read_test_declaration(root: Path) -> dict:
    """The plant's `TEST_GLOBS` (a list of strings) and `SKIP_DIRS` (a set or
    list of strings), each read with `ast.literal_eval` from its top-level
    assignment in `docs/graph/spec-lint.py`: name -> value, a name absent when
    there is none to read."""
    try:
        tree = ast.parse(read_text(root, TEST_DECLARATION))
    except (OSError, Unreadable, SyntaxError, ValueError, RecursionError, MemoryError):
        return {}
    kinds = {"TEST_GLOBS": (list,), "SKIP_DIRS": (set, list)}
    found = {}
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) and node.value else [])
        for name in [t.id for t in targets if isinstance(t, ast.Name) and t.id in kinds]:
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError, RecursionError, MemoryError):
                continue
            if isinstance(value, kinds[name]) and all(isinstance(g, str) for g in value):
                found[name] = value
    return found


def read_config(root: Path):
    """(config, raw bytes, refusal, set): the plant config over the defaults,
    each key it sets replacing that key's default whole, and what the file
    sets, in its own order (None when there is no file or it is refused). A
    file that is not JSON, or holds an unknown key, a non-list value or a
    non-string item, is refused whole: the defaults apply and the refusal
    says why."""
    try:
        raw = read_bytes(root, CONFIG_PATH)
    except FileNotFoundError:
        return dict(CONFIG_DEFAULTS), b"", None, None
    except (OSError, Unreadable) as e:
        return dict(CONFIG_DEFAULTS), b"", f"unreadable: {e}", None
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, RecursionError, MemoryError):
        return dict(CONFIG_DEFAULTS), raw, "not JSON", None
    if not isinstance(doc, dict):
        return dict(CONFIG_DEFAULTS), raw, "not a JSON object", None
    for key, value in doc.items():
        if key not in CONFIG_DEFAULTS:
            return dict(CONFIG_DEFAULTS), raw, f"unknown key {key!r}", None
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return dict(CONFIG_DEFAULTS), raw, f"{key!r} is not a list of strings", None
    return {**CONFIG_DEFAULTS, **doc}, raw, None, doc


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


def test_class(path: str, test_globs, skip_dirs, exclude) -> str:
    """`test` when a TEST_GLOBS pattern matches the path, no directory on its
    way is one spec-lint skips, and no `exclude` pattern matches; else `code`."""
    dirs = path.split("/")[:-1]
    if (not test_globs or skip_dirs.intersection(dirs)
            or any(source_paths.path_matches(path, p) for p in exclude)):
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


def changed_together(root: Path, rel: str):
    """(the plant paths each read commit of repository `rel` changed, whether
    the repository may be shallow): the newest HISTORY_COMMITS non-merge
    commits from HEAD, renames not followed, each commit's paths after a
    `/<parents>` marker no Git path can equal. A commit with no parent (the
    root, or a shallow clone's boundary, which Git shows as changing every
    file it holds) is not read. GitFailed for a repository with no commit."""
    probe = source_paths.git(root / rel, "rev-parse", "--is-shallow-repository")
    out = source_paths.git(root / rel, "log", "--no-merges", "--no-renames", "--no-show-signature", "--no-color",
                           "-n", str(HISTORY_COMMITS), "--name-only", "-z", "--format=/%P")
    commits, paths, marker = [], None, False
    for tok in out.split(b"\0"):
        tok = tok[1:] if marker and tok.startswith(b"\n") else tok   # the newline after a marker
        marker = tok.startswith(b"/")
        if marker:
            paths = set() if tok[1:].split() else None
            if paths is not None:
                commits.append(paths)
        elif tok and paths is not None:
            paths.add(source_paths.plant_path(rel, tok.decode("utf-8", "surrogateescape")))
    return commits, probe.decode("utf-8", "replace").strip() != "false"


class Plant:
    """One plant: its root, governed repositories, test declaration, config,
    and the inventory Git and the path rules give."""

    def __init__(self, root: Path):
        self.root = root
        self.config, self.config_raw, self.config_refused, self.config_set = read_config(root)
        declared = read_test_declaration(root)
        self.test_globs = declared.get("TEST_GLOBS")
        self.skip_dirs = set(declared.get("SKIP_DIRS", TEST_SKIP_DIRS))
        self.repos = source_paths.governed_repositories(root)
        self.unnamed = []          # nested work trees no `repo:` governs, found by the inventory
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

    def askable(self, path: str) -> bool:
        """Whether Git can be asked about `path` in its repository: no foreign
        directory on the way, and no nested work tree that no `repo:` governs
        (Git answers such a path with exit 128 for the whole call)."""
        if self.foreign(path):
            return False
        repo = self.repo_of(path)
        parts = path.split("/")[:-1]
        start = 0 if repo in (None, ".") else len(repo.split("/"))
        return not any(os.path.lexists(self.root / "/".join(parts[:k]) / ".git")
                       for k in range(start + 1, len(parts) + 1))

    def key_repositories(self, problems: list) -> list:
        """Each readable repository's HEAD and the digest of its uncommitted
        code (the paths the inventory keeps); a repository Git cannot read is a `repository-unreadable`
        record and is left out. GitMissing passes through."""
        entries = []
        for rel in self.repos:
            repo = self.root / rel
            try:
                head = source_paths.git(repo, "rev-parse", "--verify", "-q", "HEAD^{commit}",
                                        ok=(0, 1)).decode().strip()
                dirty = hashlib.sha256()
                for p in sorted(p for p in source_paths.uncommitted(repo) if source_paths.is_code(rel, p)
                                and not self.foreign(source_paths.plant_path(rel, p))):
                    state = source_paths.content_state(repo, p) or ""
                    dirty.update(p.encode("utf-8", "surrogateescape") + b"\0" + state.encode() + b"\n")
            except source_paths.GitFailed as e:
                problems.append(incomplete("repository-unreadable", rel, detail=str(e)))
                continue
            entries.append({"path": rel, "head": head, "dirty": dirty.hexdigest()})
        return entries

    def inventory(self, repos: list, problems: list) -> dict:
        """path -> record for the code of the readable repositories: what Git
        lists, kept when the code-path rule holds and no directory on the way
        is foreign, the files of a nested repository taken from it alone. A
        repository whose listing fails is a `repository-unreadable` record and
        is left out; the others answer. A nested work tree the listing holds
        that no `repo:` governs goes to `unnamed`, its files to no record."""
        nested = [r for r in repos if r != "."]
        rx = [glob_regex(g) for g in self.test_globs or []]
        records = {}
        for rel in repos:
            try:
                paths = listed(self.root / rel)
            except source_paths.GitFailed as e:
                problems.append(incomplete("repository-unreadable", rel, detail=str(e)))
                continue
            for p in paths:
                path = source_paths.plant_path(rel, p.rstrip("/"))
                if self.foreign(path) or rel == "." and any(path.startswith(n + "/") for n in nested):
                    continue
                try:
                    st = os.lstat(self.root / path)
                except OSError:
                    continue                 # deleted from the work tree: not there to index
                if p.endswith("/") or stat.S_ISDIR(st.st_mode):
                    # a nested work tree (Git lists an untracked one as `<path>/`) or a gitlink
                    if path not in self.repos and os.path.lexists(self.root / path / ".git"):
                        self.unnamed.append(path)
                    continue
                if not source_paths.is_code(rel, p):
                    continue
                records[path] = {"path": path, "repo": rel,
                                 "hash": source_paths.content_state(self.root / rel, p) or "",
                                 "language": None,
                                 "test": test_class(path, rx, self.skip_dirs, self.config["exclude"]),
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


def probe_order(base: str) -> list:
    """The TS/JS probe rule: `base` as written, then a written .js as .ts,
    then with each extension, then as an index (SPEC-0007 §6 "Links")."""
    ext = posixpath.splitext(base)[1]
    cands = [base] + ([base[:-len(ext)] + e for e in JS_TO_TS] if ext in JS_WRITTEN else [])
    return cands + [base + e for e in TS_PROBE] + [base + "/index" + e for e in TS_PROBE]


def named(seg: str) -> bool:
    """A segment that names something: not empty, `.`, `..` or a bare variable."""
    return seg not in ("", ".", "..") and not VARIABLE.match(seg)


def variable_lead(segs: list) -> int:
    """How many leading segments of a shell path are variables (`$DIR`,
    `$(dirname "$0")`), the last segment never counted."""
    lead = 0
    while lead < len(segs) - 1 and "$" in segs[lead]:
        lead += 1
    return lead


def as_variable(word: str) -> str:
    """A non-literal join segment written as a variable: `$name` for a name,
    the word itself when it is one already, else `$_`."""
    if VARIABLE.match(word):
        return word
    return "$" + (word if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", word) else "_")


def call_args(line: str, pos: int):
    """(the arguments, stripped, of the call whose `(` ends at `pos`; the index
    past its `)`), or None when that `)` is not on the line."""
    args, depth, start, i, n = [], 0, pos, pos, len(line)
    while i < n:
        c = line[i]
        if c in "'\"`":
            i += 1
            while i < n and line[i] != c:
                i += 2 if line[i] == "\\" else 1
        elif c in "([{":
            depth += 1
        elif c in ")]}" and depth:
            depth -= 1
        elif c == ")" or c == "," and not depth:
            args.append(line[start:i].strip())
            if c == ")":
                return [a for a in args if a], i + 1
            start = i + 1
        elif c in "]}":
            return None
        i += 1
    return None


def call_join(line: str, m):
    """A path join written as a call (`path.join(`, `path.resolve(`,
    `os.path.join(`) at the JOIN_CALL match `m`, read as one path literal:
    (its segments joined by `/`, each non-literal one as a variable; the index
    past the call), or None when no segment after the first is a literal."""
    got = call_args(line, m.end())
    if got is None:
        return None
    args, end = got
    segs, literal = [], False
    for k, a in enumerate(args):
        quoted, inner = TS_STRING.fullmatch(a), JOIN_CALL.match(a)
        nested = call_join(a, inner) if inner else None
        if quoted:
            segs.append(next(g for g in quoted.groups() if g is not None))
        elif nested and nested[1] == len(a):
            segs.append(nested[0])
        else:
            segs.append(as_variable(a))
            continue
        literal = literal or k > 0
    return ("/".join(segs), end) if literal else None


def call_joins(line: str) -> list:
    """Each path join call on one line, outermost only: (start, end, reading)."""
    out = []
    for m in JOIN_CALL.finditer(line):
        if out and m.start() < out[-1][1]:
            continue
        got = call_join(line, m)
        if got:
            out.append((m.start(), got[1], got[0]))
    return out


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
        self.links, self.opaque, self.unresolved, self.symbols = set(), [], [], []
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

    def define(self, path, name, line, kind, found):
        """One definition; its link is the one its reading gives (ast: certain)."""
        self.symbols.append({"name": name[:LITERAL_MAX], "path": path, "line": line, "kind": kind,
                             "link": ENUMS["read"][found], "found": found})

    def missing(self, holder, line, kind, reference, base, reason="relative-no-file"):
        """A reference naming a path no inventory file holds."""
        if base is None or self.plant.repo_of(base) is None:
            self.unresolved_at(holder, line, kind, reference, "outside-repository", None)
        else:
            self.unresolved_at(holder, line, kind, reference, reason, base)

    def run(self):
        for path, rec in sorted(self.records.items()):
            data = None
            ext = posixpath.splitext(path.rsplit("/", 1)[-1])[1]
            if not rec["symlink"] and (not ext or LANGUAGES.get(ext) in LINK_BEARING):
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
                self.symbols = [s for s in self.symbols if s["path"] != path]
                self.opaque_at(path, None, "", "unreadable")
        self.mark_generated()

    # -- resolution
    def resolve_text(self, holder: str, text: str, directories: bool):
        """A shell argument or path literal: holder-directory-relative, then
        each `/`-suffix of the string, longest first, relative to the holder's
        repository and then to the plant root; when the leading segments are
        variables (`$DIR/lib.sh`), each suffix after them is tried from the
        holder's directory first. ("file", path, exact) for a file, exact when
        the whole string names it from the holder or its repository root;
        ("dir", files) for a directory, only when `directories` and the string
        holds a `/`; None when it names nothing. A string with no named
        segment ("/", "./", "$ROOT/") never resolves."""
        segs = text.rstrip("/").split("/")
        if not any(named(s) for s in segs):
            return None
        hdir = posixpath.dirname(holder)
        repo = self.records[holder]["repo"]
        lead = variable_lead(segs)
        tries = [(joined(hdir, "/".join(segs[k:])), False) for k in range(lead, len(segs) if lead else 0)
                 if any(named(s) for s in segs[k:])]
        tries.append((joined(hdir, text), True))
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

    @staticmethod
    def literal_text(text):
        """A quoted string or path join as the path it is read as: None when it
        is no candidate (empty, longer than LITERAL_MAX, holding whitespace or
        `://`); one holding a variable after its leading segments is cut to the
        directory literal before that variable (`$A/x/$B` reads `$A/x/`)."""
        if not text or len(text) > LITERAL_MAX or "://" in text or any(c.isspace() for c in text):
            return None
        segs = text.split("/")
        cut = next((k for k in range(variable_lead(segs), len(segs)) if "$" in segs[k]), None)
        return text if cut is None else "/".join(segs[:cut]) + "/"

    def literal_resolves(self, holder, text) -> bool:
        """Whether a string or join reading names an inventory file or directory."""
        lit = self.literal_text(text) if text else None
        return bool(lit and self.resolve_text(holder, lit, directories=True))

    def path_literal(self, holder, text, line):
        """A quoted string or path join read as a path: a `maybe` link to the
        file, or to each file under the directory, it names; nothing when it
        names none."""
        lit = self.literal_text(text)
        hit = self.resolve_text(holder, lit, directories=True) if lit else None
        if hit is None:
            return False
        self.literal_hit(holder, hit, line, text)
        return True

    def literal_hit(self, holder, hit, line, reference):
        if hit[0] == "file":
            self.link(holder, hit[1], "path-literal", "path-literal", line)
        elif len(hit[1]) > DIR_LINK_MAX:
            self.opaque_at(holder, line, reference, "walks-tree")
        else:
            for target in hit[1]:
                self.link(holder, target, "path-literal", "directory", line)

    def walk_root_links(self, holder, root) -> bool:
        """Whether a walk call's root, a literal or a path join, makes
        `directory` links by the path-literal rule; a walk whose root makes
        none is `opaque` `walks-tree` (SPEC-0007 §6 "Links"), so no walk is
        dropped in silence."""
        lit = self.literal_text(root) if root else None
        hit = self.resolve_text(holder, lit, directories=True) if lit else None
        return bool(hit) and hit[0] == "dir"

    def pick(self, *cands):
        return next((c for c in cands if c in self.files), None)

    def module_hits(self, base: str, package: bool, names) -> list:
        """The module file at `base` (`base.py` or `base/__init__.py`; with
        `package`, `base` is the package directory itself) and each imported
        name's submodule file below it the inventory holds, because an
        imported name may be a submodule (SPEC-0007 §6 "Resolution")."""
        prefix = "" if base in ("", ".") else base + "/"
        cands = [prefix + "__init__.py"] if package else [base + ".py", base + "/__init__.py"]
        for n in names:
            cands += [f"{prefix}{n}.py", f"{prefix}{n}/__init__.py"]
        return [c for c in dict.fromkeys(cands) if c in self.files]

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
            hits = self.module_hits(base, not parts, names)
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
            hits = self.module_hits(base, False, names) if base else []
            if hits:
                for h in hits:
                    self.link(holder, h, kind, "resolved", line)
                return
        # the suffix fallback: each base whose module or submodule files end
        # in the module's path is one candidate
        ends = [rel + ".py", rel + "/__init__.py"] + [f"{rel}/{n}{t}" for n in names
                                                      for t in (".py", "/__init__.py")]
        bases = sorted({p[:len(p) - len(e)] + rel for e in ends
                        for p in self.by_name.get(e.rsplit("/", 1)[-1], [])
                        if p == e or p.endswith("/" + e)})
        for base in bases:
            for target in self.module_hits(base, False, names):
                self.link(holder, target, kind, "resolved" if len(bases) == 1 else "ambiguous", line)

    # -- Python, read by ast
    def python(self, rec, text):
        holder = rec["path"]
        tree = ast.parse(text)
        self.python_definitions(holder, tree)
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

        def is_str(n):
            return isinstance(n, ast.Constant) and isinstance(n.value, str)

        def join_of(n):
            """A path join (a `/` chain or `os.path.join`, a string literal after
            its base) as (its reading, the nodes it reads), or None."""
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
                ops, nodes = [], [n]
                while isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
                    ops.insert(0, n.right)
                    n = n.left
                    nodes.append(n)
                ops.insert(0, n)
            elif isinstance(n, ast.Call) and qual(n.func) == "os.path.join" and n.args and not n.keywords:
                ops, nodes = list(n.args), [n]
            else:
                return None
            if not any(is_str(o) for o in ops[1:]):
                return None
            segs = []
            for o in ops:
                inner = join_of(o)
                if is_str(o):
                    segs.append(o.value)
                elif isinstance(o, ast.Call) and qual(o.func) == "pathlib.Path" and len(o.args) == 1 \
                        and not o.keywords and is_str(o.args[0]):
                    segs.append(o.args[0].value)
                    o = o.args[0]
                elif inner:
                    segs.append(inner[0])
                    nodes += inner[1]
                    continue
                else:
                    segs.append(as_variable(o.id if isinstance(o, ast.Name) else ""))
                    continue
                nodes.append(o)
            return "/".join(segs), nodes

        def literal_of(n):
            """The reading of a string literal or a path join, or None."""
            return n.value if is_str(n) else (join_of(n) or (None,))[0]

        consumed = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                consumed.update(id(v) for v in node.values)
        hdir = posixpath.dirname(holder)

        def literal_resolves(arg):
            return any(self.literal_resolves(holder, t) for c in ast.walk(arg)
                       for t in [literal_of(c)] if t is not None)

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
                    consumed.update(map(id, ast.walk(arg)))
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
                    if not (root is not None and self.walk_root_links(holder, literal_of(root))):
                        self.opaque_at(holder, node.lineno, ast.unparse(root) if root is not None else q,
                                       "walks-tree")
        # every path literal, whole or a join (read once, outermost first,
        # its segments read as part of it only)
        for node in ast.walk(tree):
            if id(node) in consumed:
                continue
            join = join_of(node)
            if join:
                consumed.update(map(id, join[1]))
                self.path_literal(holder, join[0], node.lineno)
            elif is_str(node):
                self.path_literal(holder, node.value, node.lineno)

    def python_definitions(self, holder, tree):
        """The module's definitions, read over statement bodies and assignment
        targets with an explicit stack, never into an expression: every def
        and class at any depth, qualified by the classes and functions that
        enclose it, and every name an assignment, annotated assignment or
        `type` statement binds where the nearest enclosing scope is the module
        or a class body. A function's locals, imports, parameters and
        attribute targets define nothing."""
        stack = [(tree.body, "", False)]          # (statements, qualifying prefix, inside a function)
        while stack:
            body, prefix, local = stack.pop()
            for node in body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    is_class = isinstance(node, ast.ClassDef)
                    self.define(holder, prefix + node.name, node.lineno, "class" if is_class else "function", "ast")
                    stack.append((node.body, prefix + node.name + ".", not is_class))
                    continue
                if local:
                    targets = []
                elif isinstance(node, getattr(ast, "TypeAlias", ())):
                    self.define(holder, prefix + node.name.id, node.lineno, "type", "ast")
                    targets = []
                else:
                    targets = list(node.targets) if isinstance(node, ast.Assign) else \
                        [node.target] if isinstance(node, ast.AnnAssign) else []
                while targets:
                    t = targets.pop()
                    if isinstance(t, ast.Name):
                        self.define(holder, prefix + t.id, node.lineno, "variable", "ast")
                    elif isinstance(t, (ast.Tuple, ast.List)):
                        targets.extend(t.elts)
                    elif isinstance(t, ast.Starred):
                        targets.append(t.value)
                # the blocks of if, for, while, with, try and match share the enclosing scope
                stack += [(b, prefix, local) for b in (getattr(node, f, None) for f in ("body", "orelse", "finalbody"))
                          if isinstance(b, list)]
                stack += [(h.body, prefix, local) for h in getattr(node, "handlers", []) + getattr(node, "cases", [])]

    # -- shell, read a line at a time
    @staticmethod
    def shell_words(line: str) -> list:
        """The words of one shell line, comments dropped: each its text with
        quotes removed, the quoted strings it holds, the index it starts at,
        and whether it holds unquoted parts too; None marks a command
        separator."""
        words, text, quoted, start, bare, i, n = [], [], [], None, False, 0, len(line)

        def end():
            nonlocal text, quoted, start, bare
            if start is not None:
                words.append(("".join(text), quoted, start, bare))
            text, quoted, start, bare = [], [], None, False

        while i < n:
            c = line[i]
            if c in " \t\r":
                end()
            elif c == "#" and start is None:
                break
            elif c in ";|&()`":
                end()
                words.append(None)
            elif c in "<>":
                end()
            elif c in "'\"":
                j = line.find(c, i + 1)
                while c == '"' and j > 0 and line[j - 1] == "\\":
                    j = line.find(c, j + 1)
                j = n if j < 0 else j
                text.append(line[i + 1:j])
                quoted.append(line[i + 1:j])
                start, i = i if start is None else start, j
            else:
                text.append(line[i + 1:i + 2] if c == "\\" else c)
                start, bare, i = i if start is None else start, True, i + (c == "\\")
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
        lead = variable_lead(segs)
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
            fn = SH_DEF.match(line)
            if fn:
                self.define(holder, fn.group(1) or fn.group(2), lineno, "function", "line-reading")
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
                    root = roots[0][0].rstrip("/") + "/" if roots and roots[0][0] else ""
                    if root and "$" not in root and self.walk_root_links(holder, root):
                        used.add(id(roots[0]))
                        self.literal_hit(holder, self.resolve_text(holder, root, True), lineno, roots[0][0])
                    else:
                        self.opaque_at(holder, lineno, roots[0][0] if roots else t, "walks-tree")
            self.shell_joins(holder, line, words, used, lineno)
            for w in words:
                if w is not None and id(w) not in used:
                    # a word joining quoted and unquoted parts is one string,
                    # an assignment's the value after its `=`
                    value = SHELL_ASSIGN.sub("", w[0], count=1) if w[3] else w[0]
                    for q in [value] if w[3] and w[1] and value != "".join(w[1]) else w[1]:
                        self.path_literal(holder, q, lineno)

    def shell_joins(self, holder, line, words, used, lineno):
        """The path joins of one shell line, each read as one path literal and
        its words marked used: the join calls, then each run of words joined
        by `/` words with a quoted word after the first (the form a Python
        here-document writes, `SEED / "tools" / "x.py"`)."""
        for a, b, reading in call_joins(line):
            inside_call = [w for w in words if w is not None and a <= w[2] < b]
            if inside_call and not any(id(w) in used for w in inside_call):
                used.update(map(id, inside_call))
                self.path_literal(holder, reading, lineno)

        def slash(w):
            return w is not None and w[0] == "/" and not w[1]

        k = 0
        while k < len(words):
            j = k
            while words[j] is not None and j + 2 < len(words) and slash(words[j + 1]) \
                    and words[j + 2] is not None and not slash(words[j + 2]):
                j += 2
            run = words[k:j + 1:2]
            if len(run) > 1 and any(w[1] and not w[3] for w in run[1:]) \
                    and not any(id(w) in used for w in run):
                used.update(map(id, words[k:j + 1]))
                self.path_literal(holder, "/".join(w[0] if w[1] else as_variable(w[0]) for w in run), lineno)
                k = j + 1
            else:
                k += 1

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
        for lineno, line in enumerate(lines, 1):
            decl = TS_DEF.match(line)
            if decl:
                self.define(holder, decl.group(2), lineno,
                            TS_DEF_KIND[decl.group(1).replace("*", " ").split()[-1]], "line-reading")
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
        for a, b, reading in call_joins(line):
            spans.append((a, b))
            self.path_literal(holder, reading, lineno)
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
            elif not (self.ts_literal(holder, line[m.end():], lineno, dry=True)
                      or self.literal_resolves(holder, self.join_at(line, m.end()))):
                self.opaque_at(holder, lineno, line[m.end():].split(")")[0].strip(), "dynamic-nonliteral")
        for m in TS_WALK.finditer(line):
            root = TS_STRING.match(line, m.end())
            text = next((g for g in root.groups() if g is not None), "") if root else ""
            hit = self.ts_target(holder, text) if text and "/" in text else None
            if not (hit and not isinstance(hit[0], str) or self.walk_root_links(holder, self.join_at(line, m.end()))):
                self.opaque_at(holder, lineno, line[m.end():].split(")")[0].strip(), "walks-tree")
        for m in TS_STRING.finditer(line):
            k = next(g for g in (1, 2, 3) if m.group(g) is not None)
            if not any(a <= m.start(k) < b or m.start(k) == a for a, b in spans):
                self.ts_literal(holder, m.group(k), lineno)

    @staticmethod
    def join_at(line, pos):
        """The reading of the path join call that starts at `pos`, or None."""
        m = JOIN_CALL.match(line, pos)
        got = call_join(line, m) if m else None
        return got[0] if got else None

    def ts_literal(self, holder, text, lineno, dry=False):
        """A TS/JS path literal: only a relative or alias-prefixed string, by
        the specifier rules, as a `maybe` link. With `dry`, whether the first
        string of an argument resolves, recording nothing."""
        if dry:
            m = TS_STRING.match(text.lstrip())
            text = next((g for g in m.groups() if g is not None), "") if m else ""
        if not text or len(text) > LITERAL_MAX or any(c.isspace() for c in text) or "://" in text:
            return False
        hit = self.ts_target(holder, text)
        if hit and not dry:
            self.literal_hit(holder, ("file", hit[0], False) if isinstance(hit[0], str) else ("dir", hit[0]),
                             lineno, text)
        return bool(hit)

    def probe(self, base):
        """(file, exact) for the first path of `probe_order(base)` the
        inventory holds; exact only when it is `base` as written."""
        if base is None:
            return None
        hit = self.pick(*probe_order(base))
        return (hit, hit == base) if hit else None

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
        package = bool(NPM_NAME.match(spec) or SCHEME_LED.match(spec))   # a name led by a scheme is external too
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
        if path_part.startswith("/"):
            self.missing(holder, line, "import", spec, None)
            return
        if cfg and cfg["base_url"] is not None:
            hit = self.probe(joined(cfg["base_url"], path_part))
            if hit:
                self.link(holder, hit[0], "import", "resolved", line)
                return
        if package:
            self.workspace(holder, spec, line)
        else:
            # no rule maps it (`~/x` with no `~` alias, `#internal`, a baseUrl
            # miss): a config this tool does not read may name any file
            self.opaque_at(holder, line, spec, "unmapped-specifier")

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
        """A bare specifier against the workspace packages: the longest
        `name` equal to it or followed in it by `/`. A subpath that probes to
        a file under the package directory is one `resolved` link; otherwise
        each file of the package is a `maybe` `workspace-package` link."""
        names = [n for n in self.packages() if spec == n or spec.startswith(n + "/")]
        if not names:
            return
        name = max(names, key=len)
        d = self.packages()[name]
        if spec != name:
            hit = self.probe(joined(d, spec[len(name) + 1:]))
            if hit:
                self.link(holder, hit[0], "import", "resolved", line)
                return
        files = [f for f in (self.under.get(d, []) if d else sorted(self.files)) if f != holder]
        if len(files) > DIR_LINK_MAX:
            self.opaque_at(holder, line, spec, "walks-tree")
        for f in files if len(files) <= DIR_LINK_MAX else []:
            self.link(holder, f, "import", "workspace-package", line)

    def ts_target(self, holder, text):
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
        those are `generated`. Paths go on stdin as `./<path>`, never argv; a
        base Git cannot be asked about keeps its reason."""
        asks = {}
        for u in self.unresolved:
            if u["reason"] in ("relative-no-file", "alias-no-file") and u["base"] and \
                    self.plant.askable(u["base"]):
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
        h.update(len(c).to_bytes(8, "big") + c)
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


def derive(plant: Plant, repos: list, problems: list) -> dict:
    """The index body: inventory, links, opaque and unresolved records and
    definitions, each sorted, holding plant-relative paths only."""
    records = plant.inventory(repos, problems)
    ex = Extract(plant, records)
    ex.run()
    inventory = [{k: r[k] for k in SHAPE["inventory"]} for _, r in sorted(records.items())]
    links = [dict(zip(("holder", "target", "kind", "link", "found", "line"), l))
             for l in sorted(ex.links, key=lambda l: (l[0], l[1], l[2], l[5], l[4]))]
    opaque = sorted(ex.opaque, key=lambda o: (o["holder"], -1 if o["line"] is None else o["line"],
                                              o["reason"], o["reference"]))
    unresolved = sorted(ex.unresolved, key=lambda u: (u["holder"], u["line"], u["reference"], u["reason"]))
    symbols = sorted(ex.symbols, key=lambda s: (s["path"], s["line"], s["name"], s["kind"]))
    return {"inventory": inventory, "links": links, "opaque": opaque, "unresolved": unresolved, "symbols": symbols}


def cache_problem(doc, key) -> str:
    """Why `doc` is not a usable index for `key`, or None. The cache is
    untrusted: every path must be clean and relative, every endpoint an
    inventory path, every enum one SPEC-0007 §6 lists."""
    if not isinstance(doc, dict) or set(doc) != {"schema", "key", *SHAPE}:
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
    for r in doc["symbols"]:
        if not (r["path"] in paths and line_ok(r["line"]) and isinstance(r["name"], str)
                and len(r["name"]) <= LITERAL_MAX and "\0" not in r["name"] and r["kind"] in ENUMS["symbol"]
                and r["found"] in ENUMS["read"] and r["link"] == ENUMS["read"][r["found"]]):
            return "cache unreadable: bad symbols record"
    return None if doc["key"] == key else "key changed"


def read_ignore(dir_fd):
    """The first bytes of the cache's inner `.gitignore` (one more than
    CACHE_IGNORE holds, so a longer file differs), or None when it is absent
    or not a regular file."""
    try:
        opened = source_paths.open_regular(".gitignore", dir_fd=dir_fd)
    except FileNotFoundError:
        return None
    if opened is None:
        return None
    fd, _ = opened
    try:
        return os.read(fd, len(CACHE_IGNORE) + 1)
    finally:
        os.close(fd)


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
        if opened is not None and read_ignore(dir_fd) != CACHE_IGNORE.encode():
            os.close(opened[0])
            return None, "cache unreadable: ignore altered"
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
    data = (json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")
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
        if read_ignore(dir_fd) != ignore:
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
    empty = {part: [] for part in SHAPE}
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
        existed = cached is not None or why is not None
        del cached                               # the derive holds no parsed cache (SPEC-0007 §5)
        body = derive(plant, readable, problems)
    except source_paths.GitMissing:
        problems = [p for p in problems if p["reason"] == "config-refused"]
        problems.append(incomplete("git-unavailable", "git"))
        return plant, empty, {"status": "not-written", "reason": "git is not on PATH"}, problems
    except source_paths.GitFailed as e:
        problems.append(incomplete("repository-unreadable", ".", detail=str(e)))
        return plant, empty, {"status": "not-written", "reason": str(e)}, problems
    if any(p["reason"] == "repository-unreadable" for p in problems):
        return plant, body, {"status": "not-written", "reason": "a repository is unreadable"}, problems
    failed = write_cache(root, {"schema": INDEX_SCHEMA, "key": key, **body})
    if failed:
        return plant, body, {"status": "not-written", "reason": failed}, problems
    reason = "build forced" if force and existed else why
    return plant, body, {"status": "rebuilt" if existed else "built", "reason": reason}, problems


# --- inputs ------------------------------------------------------------------
def plant_relative(root: Path, text: str):
    """An input made plant-relative, lexically: posix, `./` dropped, an
    absolute path inside the plant (as given or as resolved) taken from the
    root; None when the result is not the helper's clean relative path."""
    p = text
    if p.startswith("/"):
        for top in dict.fromkeys((str(root), os.path.realpath(root))):
            if p == top or p.startswith(top.rstrip("/") + "/"):
                p = p[len(top):].lstrip("/") or "."
                break
        else:
            return None
    p = posixpath.normpath(p) if p else p
    return p if source_paths.relative(p) else None


def moved_inputs(root: Path):
    """(paths, incomplete records): the plant paths code-anchor's moved list
    names, each joined to its repository. The load and the call of
    `moved_list` sit in one guard, so no failure of code-anchor crashes the
    query; it catches code-anchor's own classes, never this tool's."""
    tool = Path(__file__).resolve().parent / CODE_ANCHOR
    shown = f"docs/graph/{CODE_ANCHOR}"
    if not tool.is_file():
        return [], [incomplete("moved-unavailable", shown, detail="absent")]
    missing = unrecorded = ()                    # code-anchor's classes, once it has loaded
    subject = ".cypress/anchor.json"             # an Unrecorded record's subject, unless code-anchor names it
    paths, problems = [], []
    try:
        anchor = _loaded(_ilu.spec_from_file_location("cypress_code_anchor", tool))
        missing, unrecorded = anchor.source_paths.GitMissing, anchor.Unrecorded
        where = getattr(anchor, "ANCHOR_DIR", None), getattr(anchor, "ANCHOR_NAME", None)
        if all(isinstance(w, str) for w in where):
            subject = "/".join(where)
        for repo, pairs in anchor.moved_list(root):
            if not source_paths.relative(repo):
                raise ValueError(f"moved_list named the repository {repo!r}, not a clean plant path")
            pairs = list(pairs)
            for label, moved in pairs:
                if not (isinstance(label, str) and isinstance(moved, (list, tuple))
                        and all(isinstance(p, str) for p in moved)):
                    raise ValueError(f"moved_list gave a {type(label).__name__} label and "
                                     f"{type(moved).__name__} paths, not a string and a list of strings")
            if len(pairs) == 1 and pairs[0][0].startswith("unverified") and not pairs[0][1]:
                problems.append(incomplete("moved-unverified", repo, detail=pairs[0][0]))
                continue
            for _, moved in pairs:
                for p in moved:
                    joined = source_paths.plant_path(repo, p)
                    if not source_paths.relative(joined):
                        raise ValueError(f"moved_list named {joined!r}, not a clean plant path")
                    paths.append(joined)
    except missing:
        return [], []                            # the answer already holds git-unavailable
    except unrecorded as e:
        return [], [incomplete("moved-unavailable", subject, detail=str(e))]
    except (Exception, SystemExit) as e:         # noqa: BLE001 — any failure of code-anchor is a record
        return [], [incomplete("moved-unavailable", shown, detail=f"{type(e).__name__}: {e}")]
    return paths, problems


# --- the graph pages -----------------------------------------------------------
def graph_pages(root: Path):
    """Each readable graph page as (page, text, kind, name): its `repo:` value
    read once per distinct value through the helper's `repo_kind`, kind and
    name None when the page sets none."""
    kinds = {}                 # repo: value as written -> (kind, name)
    for page in plant_walk.files(root, GRAPH, "*.md"):
        rel = page.relative_to(root).as_posix()
        try:
            text = read_text(root, rel)
        except (OSError, Unreadable):
            continue
        try:
            repo = frontmatter.parse(text, rel)[0].get("repo")
        except frontmatter.FrontmatterError:
            repo = None
        if not (isinstance(repo, str) and repo):
            yield rel, text, None, None
            continue
        if repo not in kinds:
            kinds[repo] = source_paths.repo_kind(root, repo)
        yield (rel, text, *kinds[repo])


def repo_unresolved(page: str, value: str) -> dict:
    """The `repo-unresolved` record of a page whose `repo:` names nothing."""
    return incomplete("repo-unresolved", page, detail=safe(source_paths.REPO_UNRESOLVED_DETAIL.format(value=value)))


# --- the walk ------------------------------------------------------------------
def by_link(r):
    return (r["link"] != "certain", r["depth"], r["path"])


def by_depth(r):
    return (r["depth"], r["path"])


class Index:
    """The query side of one index body: input forms, the one reverse walk
    and the citation join (SPEC-0007 §6 "Inputs", "Walk", "Query answer")."""

    def __init__(self, plant: Plant, body: dict, usable: bool):
        self.plant, self.usable = plant, usable
        self.records = {r["path"]: r for r in body["inventory"]}
        self.steps = {}                    # a file -> each (holder, kind, link, found, line) naming it
        for l in body["links"]:
            self.steps.setdefault(l["target"], []).append(
                (l["holder"], l["kind"], l["link"], l["found"], l["line"]))
        self.named = set()                 # paths no inventory file holds that a reference names
        for u in body["unresolved"]:
            if u["base"] is None:
                continue
            names = [u["base"]] if u["reason"] == "asset" else probe_order(u["base"])
            if (self.records.get(u["holder"]) or {}).get("language") == "python":
                names += [u["base"] + ".py", u["base"] + "/__init__.py"]
            for n in dict.fromkeys(names):
                if n not in self.records:
                    self.named.add(n)
                    self.steps.setdefault(n, []).append((u["holder"], u["kind"], "certain", "named", u["line"]))
        self.opaque = {}                   # holder -> its first opaque record
        for o in body["opaque"]:
            self.opaque.setdefault(o["holder"], o)
        self.links = body["links"]
        self.symbols = body["symbols"]
        self.unreadable = sorted({o["holder"] for o in body["opaque"] if o["reason"] == "unreadable"})
        self.rx = [glob_regex(g) for g in plant.test_globs or []]

    # -- inputs
    def status_of(self, path):
        if path in self.records or path in self.named:
            return "walked"
        return None if source_paths.is_code(".", path) else "not-code"

    def inputs(self, texts, query):
        """(inputs, incomplete records): each input once, by the forms of
        §6 "Inputs"; `global-input` for each that matches `global_inputs`."""
        found, problems = {}, []
        for text in texts:
            path = plant_relative(self.plant.root, text)
            if path is None:
                problems.append(incomplete("outside-plant", text))
                continue
            status = self.status_of(path)
            if status is None and self.usable:
                hits = [q for r in self.plant.repos if r != "."
                        for q in [posixpath.join(r, path)] if self.status_of(q) == "walked"]
                if len(hits) > 1:
                    problems.append(incomplete("ambiguous-input", path, hits))
                    continue
                if hits:
                    path, status = hits[0], "walked"
            if any(source_paths.path_matches(path, g) for g in self.plant.config["global_inputs"]):
                problems.append(incomplete("global-input", path))
            if status is None and query != "anchors":
                if self.usable:
                    problems.append(incomplete("input-not-found", path))
                continue
            found[path] = status or "not-found"
        unique = {(r["reason"], r["subject"]): r for r in problems}
        return [{"path": p, "status": found[p]} for p in sorted(found)], list(unique.values())

    def test(self, path):
        rec = self.records.get(path)
        return rec["test"] if rec else test_class(path, self.rx, self.plant.skip_dirs, self.plant.config["exclude"])

    # -- the one reverse walk
    def walk(self, starts, cap):
        """Every file the steps reach from `starts` (rows of one depth), each
        once at its nearest depth: a certain chain over a maybe one, then the
        smaller `from`; a row is as strong as its weakest link and carries the
        maybe link nearest its start."""
        reached = {r["path"]: r for r in starts}
        level = sorted(starts, key=by_depth)
        while level and level[0]["depth"] < cap:
            best = {}
            for parent in level:
                for holder, kind, link, found, line in self.steps.get(parent["path"], []):
                    if holder in reached:
                        continue
                    chain = "certain" if parent["link"] == link == "certain" else "maybe"
                    rank = (chain != "certain", parent["path"], link != "certain", line, kind, found)
                    if holder in best and best[holder][0] <= rank:
                        continue
                    maybe = parent["maybe"] or (
                        {"reason": found, "holder": holder, "line": line} if link == "maybe" else None)
                    best[holder] = (rank, {"path": holder, "depth": parent["depth"] + 1, "link": chain,
                                           "from": parent["path"], "kind": kind, "found": found,
                                           "line": line, "maybe": maybe, "via": parent["via"] + [holder]})
            level = sorted((r for _, r in best.values()), key=by_depth)
            reached.update((r["path"], r) for r in level)
        return reached

    def reach(self, inputs, cap):
        """(input rows, floor rows, depth-cap records): the input part from the
        walked inputs at depth 0, cut at `cap`; the floor part, when an input
        is walked, from every opaque holder at depth 1 with no depth bound
        (the floor is the index's, not the input's), less what the input part
        takes. Only a cut in the input part makes a depth-cap record."""
        walked = [i["path"] for i in inputs if i["status"] == "walked"]
        rows = self.walk([{"path": p, "depth": 0, "link": "certain", "from": None, "kind": None,
                           "found": None, "line": None, "maybe": None, "via": [p]} for p in walked], cap)
        floor = {}
        if walked:
            floor = self.walk([{"path": h, "depth": 1, "link": "maybe", "from": None, "kind": "opaque",
                                "found": o["reason"], "line": o["line"],
                                "maybe": {"reason": o["reason"], "holder": h, "line": o["line"]}, "via": [h]}
                               for h, o in sorted(self.opaque.items())], float("inf"))
        floor = {p: r for p, r in floor.items() if p not in rows}
        seen = set(rows) | set(floor)
        capped = sorted({r["path"] for r in rows.values() if r["depth"] == cap
                         and any(h not in seen for h, *_ in self.steps.get(r["path"], []))})
        return list(rows.values()), list(floor.values()), [incomplete("depth-cap", p) for p in capped]

    def always_run(self, taken):
        """The tests no list before takes: `declared` by the plant's
        `always_run`, else `no-code-edge` for a link-bearing test holding no
        link to code and no opaque record."""
        to_code = {l["holder"] for l in self.links if self.test(l["target"]) == "code"}
        out = []
        for path, rec in sorted(self.records.items()):
            if rec["test"] != "test" or path in taken:
                continue
            if any(source_paths.path_matches(path, g) for g in self.plant.config["always_run"]):
                out.append({"path": path, "reason": "declared"})
            elif rec["language"] in LINK_BEARING and path not in to_code and path not in self.opaque:
                out.append({"path": path, "reason": "no-code-edge"})
        return out

    def history(self, doc, tests_only):
        """(history rows, incomplete records): for each repository holding a
        walked input, the inventory files that changed together with an input
        in its read commits, from the input with the highest count; a commit
        keeping more than HISTORY_MAX_FILES inventory paths is not read. A file
        another list of the answer holds is no history row, so history only
        adds (SPEC-0007 §6 "History links")."""
        walked = [i["path"] for i in doc["inputs"] if i["status"] == "walked"]
        taken = set(walked) | {r["path"] for key in ("dependents", "tests", "always_run", "floor")
                               for r in doc.get(key, [])}
        best, problems = {}, []
        for repo in sorted({self.plant.repo_of(p) for p in walked} - {None}):
            try:
                commits, shallow = changed_together(self.plant.root, repo)
            except (source_paths.GitFailed, source_paths.GitMissing) as e:
                problems.append(incomplete("history-unavailable", repo, detail=str(e) or "git is not on PATH"))
                continue
            if shallow:
                problems.append(incomplete("history-shallow", repo,
                                           detail="a shallow clone: its oldest commit is not read"))
            read = [c for c in ({p for p in c if p in self.records} for c in commits)
                    if len(c) <= HISTORY_MAX_FILES]
            for i in (p for p in walked if self.plant.repo_of(p) == repo):
                mine = [c for c in read if i in c]
                count = {}
                for p in (p for c in mine for p in c if p != i):
                    count[p] = count.get(p, 0) + 1
                for p, n in count.items():
                    rank = (-n, len(mine), i)
                    if p not in best or rank < best[p][0]:
                        best[p] = (rank, {"path": p, "depth": 1, "link": "maybe", "from": i, "kind": "history",
                                          "found": "history", "line": None,
                                          "maybe": {"reason": "history", "holder": i, "line": None},
                                          "via": [i, p], "together": {"count": n, "of": len(mine)}})
        rows = [r for p, (_, r) in best.items()
                if p not in taken and (not tests_only or self.test(p) == "test")]
        return sorted(rows, key=lambda r: (-r["together"]["count"], r["path"])), problems

    # -- definitions
    def definitions(self, names):
        """(names, incomplete records): each name's definitions, a name
        holding a `.` matching a qualified name whole, another also its last
        segment; one `unreadable-file` record per file whose definitions the
        build could not read, because it may define the name."""
        by_full, by_last = {}, {}
        for s in self.symbols:
            by_full.setdefault(s["name"], []).append(s)
            by_last.setdefault(s["name"].rsplit(".", 1)[-1], []).append(s)
        out = []
        for name in sorted(set(names)):
            found = sorted((by_full if "." in name else by_last).get(name, []),
                           key=lambda s: (s["link"] != "certain", s["path"], s["line"]))
            out.append({"name": name, "definitions": found, "undefined": not found})
        return out, [incomplete("unreadable-file", p) for p in self.unreadable]

    # -- the citation join
    @staticmethod
    def citations(text):
        """Each citation of a page: the inline backtick spans outside fenced
        blocks, a span whole when the citation grammar parses it, else each of
        its whitespace-separated tokens holding a `/`."""
        fenced = False
        for line in text.split("\n"):
            if FENCE.match(line):
                fenced = not fenced
                continue
            for m in () if fenced else SPAN.finditer(line):
                span = m.group(2).strip()
                if source_paths.CITATION_RE.fullmatch(span):
                    yield span
                else:
                    yield from (t for t in span.split() if "/" in t)

    def anchors(self, inputs, every):
        """(files, incomplete records): for each input, the pages citing it, by
        backtick citation or `repo:` claim; each page whose `repo:` names
        nothing on disk is a `repo-unresolved` record."""
        root = self.plant.root
        known = set(self.records) | {i["path"] for i in inputs}
        wanted = {i["path"] for i in inputs}
        nested = [r for r in self.plant.repos if r != "."]
        facts = {p: set() for p in wanted}
        history = {p: set() for p in wanted}
        problems = {}
        for rel, text, kind, name in graph_pages(root):
            is_history = rel.startswith(HISTORY)

            def claim(path, line, form, link, found):
                if path in wanted:
                    (history[path].add(rel) if is_history else
                     facts[path].add((rel, line, form, link, found)))

            for ref in self.citations(text):
                targets, line, found, _ = source_paths.resolve_citation(root, ref, known, rel, nested)
                if found == "exact" or found == "basename" and len(targets) == 1:
                    claim(targets[0], line, "backtick", "certain" if found == "exact" else "maybe", found)
                elif found == "basename" and wanted.intersection(targets):
                    problems[(rel, ref)] = incomplete("ambiguous-citation", rel, targets, detail=ref)
            if kind == "unresolved":
                problems[(rel, None)] = repo_unresolved(rel, name)
            if kind:
                for path in wanted:
                    how = source_paths.repo_claim(name, path, kind)
                    if how:
                        claim(path, None, "repo", "certain" if how == "exact" else "maybe",
                              "exact" if how == "exact" else "repo-prefix")
        files = []
        for path in sorted(wanted):
            fs = sorted(facts[path], key=lambda f: (f[3] != "certain", f[0], f[1] is not None, f[1] or 0,
                                                    f[2], f[4]))
            files.append({"path": path,
                          "facts": [dict(zip(("page", "line", "form", "link", "found"), f)) for f in fs],
                          "history": {"count": len(history[path]),
                                      "pages": sorted(history[path]) if every else []},
                          "uncited": not fs and not history[path]})
        return files, list(problems.values())


# --- answers -----------------------------------------------------------------
def safe(text) -> str:
    """Text for the text view: every character outside printable ASCII is `?`."""
    return "".join(c if " " <= c <= "~" else "?" for c in str(text))


def test_records(plant: Plant, inventory: list) -> list:
    """The `no-test-declaration` or `no-test-files` record, or none."""
    if plant.test_globs is None:
        return [incomplete("no-test-declaration", TEST_DECLARATION)]
    if not any(r["test"] == "test" for r in inventory):
        return [incomplete("no-test-files", TEST_DECLARATION)]
    return []


def hints(plant: Plant, inventory: list) -> list:
    """The build's advice about the plant's test class and config, in the
    order of HINT_LINE (SPEC-0007 §6 "Build report"); never a gap."""
    def named_like_test(path):
        return any(source_paths.path_matches(path, p) for p in TEST_NAME_PATTERNS)

    def hint(kind, subject, paths, patterns=None):
        out = {"hint": kind, "subject": subject, "count": len(patterns if patterns else paths),
               "paths": sorted(paths)}
        return out if patterns is None else {**out, "patterns": patterns}

    found = []
    if plant.test_globs is not None:
        paths = [r["path"] for r in inventory if r["test"] == "code" and named_like_test(r["path"])
                 and not any(source_paths.path_matches(r["path"], e) for e in plant.config["exclude"])]
        if paths:
            found.append(hint("tests-outside-class", TEST_DECLARATION, paths))
    if not plant.config_refused and "exclude" not in (plant.config_set or {}):
        paths = [r["path"] for r in inventory if r["test"] == "test" and not named_like_test(r["path"])]
        if paths:
            found.append(hint("class-holds-non-tests", CONFIG_PATH, paths))
    patterns = [f"{key}: {p}" for key, ps in (plant.config_set or {}).items() for p in ps
                if not any(source_paths.path_matches(r["path"], p) for r in inventory)]
    if patterns:
        found.append(hint("config-pattern-unmatched", CONFIG_PATH, [], patterns))
    return found


def answer(query: str, args, root: Path) -> dict:
    started = time.perf_counter()
    plant, body, cache, problems = load_index(root, force=query == "build")
    doc = {"schema": ANSWER_SCHEMA, "query": query, "inputs": [], "cache": cache, "incomplete": problems}
    usable = not any(p["reason"] in ("git-unavailable", "no-repository") for p in problems)
    if query == "build":
        doc.update(body)
        problems += test_records(plant, body["inventory"])
        problems += [repo_unresolved(rel, name) for rel, _, kind, name in graph_pages(root) if kind == "unresolved"]
        problems += [incomplete("repository-unnamed", p) for p in sorted(set(plant.unnamed))]
        doc["hints"] = hints(plant, body["inventory"]) if usable else []   # no inventory to match against
        doc["seconds"] = time.perf_counter() - started
    else:
        query_answer(doc, args, root, plant, body, usable)
    problems.sort(key=lambda r: (r["reason"], r["subject"], r["candidates"], r["detail"] or ""))
    return doc


def query_answer(doc: dict, args, root: Path, plant: Plant, body: dict, usable: bool):
    """The answer of a query, added to `doc`: the inputs, the walk or the
    citation join or the definitions, and their incomplete records."""
    query, problems = doc["query"], doc["incomplete"]
    index = Index(plant, body, usable)
    if query == "symbols":
        doc["not_read"] = list(source_paths.NOT_CODE)   # the code-path rule bounds definitions
        doc["names"], more = index.definitions(args.names)
        # the config shapes the test class alone, so it cannot make a definition answer incomplete
        problems[:] = [p for p in problems + more if p["reason"] != "config-refused"]
    else:
        paths = args.paths
        if getattr(args, "moved", False):
            paths, more = moved_inputs(root)
            problems += more
        doc["inputs"], more = index.inputs(paths, query)
        problems += more
        if query == "anchors":
            doc["files"], more = index.anchors(doc["inputs"], args.all)
            problems += more
        else:
            doc["depth"] = args.depth
            rows, floor, more = index.reach(doc["inputs"], args.depth)
            problems += more
            if query == "impact":
                doc["dependents"] = sorted((r for r in rows if r["depth"]), key=by_link)
            else:
                problems += test_records(plant, body["inventory"])
                doc["tests"] = sorted((r for r in rows if index.test(r["path"]) == "test"), key=by_link)
                doc["always_run"] = index.always_run({r["path"] for r in doc["tests"]})
                taken = {r["path"] for r in doc["tests"]} | {r["path"] for r in doc["always_run"]}
                floor = [r for r in floor if index.test(r["path"]) == "test" and r["path"] not in taken]
            doc["floor"] = sorted(floor, key=by_depth)
            if args.history:
                doc["history"], more = index.history(doc, query == "affected-tests")
                problems += more


def row_text(r) -> str:
    """`<depth> <link> <path>  <- <from> [<kind> <found>:<line>]`, a maybe row
    adding `maybe: <reason> at <holder>:<line>`."""
    out = f"{r['depth']} {r['link']} {r['path']}"
    if r["depth"]:
        out += f"  <- {r['from'] or '-'} [{r['kind']} {r['found']}:{r['line'] or '-'}]"
    if r["maybe"]:
        m = r["maybe"]
        out += f" maybe: {m['reason']} at {m['holder']}:{m['line'] or '-'}"
    return out


def capped(lines, every) -> list:
    """One list of the text view, cut at TEXT_MAX_ROWS with a more-line."""
    if every or len(lines) <= TEXT_MAX_ROWS:
        return lines
    return lines[:TEXT_MAX_ROWS] + [f"... {len(lines) - TEXT_MAX_ROWS} more; --all lists every row"]


def text_view(doc: dict, every: bool = False, moved: bool = False) -> list:
    cache = doc["cache"]
    out = [f"Cache: {cache['status']}" + (f" ({cache['reason']})" if cache["reason"] else "")]
    if doc["query"] == "build":
        links = doc["links"]
        certain = sum(1 for l in links if l["link"] == "certain")
        out.append(f"Index: {len(doc['inventory'])} file(s), "
                   f"{sum(1 for r in doc['inventory'] if r['test'] == 'test')} test(s), "
                   f"{certain} certain and {len(links) - certain} maybe link(s), "
                   f"{len(doc['opaque'])} opaque and {len(doc['unresolved'])} unresolved record(s), "
                   f"{len(doc['symbols'])} definition(s)")
        out.append(BUILD_TIME_LINE.format(seconds=doc["seconds"]))
    out += [f"Input: {i['path']} ({i['status']})" for i in doc["inputs"]]
    if doc["query"] == "anchors":
        if moved and not doc["inputs"] and not doc["incomplete"]:
            out.append(MOVED_NONE_LINE)
        for f in doc["files"]:
            h = f["history"]
            out.append(f"{f['path']}: uncited" if f["uncited"] else
                       f"{f['path']}: {len(f['facts'])} fact(s), {h['count']} history page(s)")
            out += capped([f"  {x['link']} {x['form']} {x['page']}" + (f":{x['line']}" if x["line"] else "")
                           + f" ({x['found']})" for x in f["facts"]], every)
            out += capped([f"  history: {p}" for p in h["pages"]], every)
    for n in doc.get("names", []):
        out.append(f"{n['name']}: {len(n['definitions'])} definition(s)" if n["definitions"] else
                   UNDEFINED_LINE.format(name=n["name"], not_read=", ".join(doc["not_read"])))
        out += capped([f"  {s['link']} {s['kind']} {s['path']}:{s['line']} {s['name']} ({s['found']})"
                       for s in n["definitions"]], every)
    if "dependents" in doc or "tests" in doc:
        out += capped([row_text(r) for r in doc.get("dependents", doc.get("tests"))], every)
    if "history" in doc:
        out.append(HISTORY_LINE.format(n=len(doc["history"])))
        out += capped([f"1 maybe {r['path']}  <- {r['from']} [history {r['together']['count']}/"
                       f"{r['together']['of']}]" for r in doc["history"]], every)
    out += capped([f"Always run: {r['path']} ({r['reason']})" for r in doc.get("always_run", [])], every)
    if doc.get("floor"):
        out.append(FLOOR_LINE.format(n=len(doc["floor"])))
        out += capped([row_text(r) for r in doc["floor"]], every)
    # each record, and for `build` its fix line under it (§6 "Build report"); the cap counts records
    records = capped([[f"- incomplete: {r['reason']}: {r['subject']}" + (f" ({r['detail']})" if r["detail"] else "")]
                      + ([FIX_PREFIX + BUILD_FIX[r["reason"]]] if doc["query"] == "build" else [])
                      for r in doc["incomplete"]], every)
    out += [l for group in records for l in ([group] if isinstance(group, str) else group)]
    for h in doc.get("hints", []):
        shown = ", ".join(h.get("patterns", h["paths"])[:HINT_MAX_PATHS])
        out.append(HINT_LINE[h["hint"]].format(count=h["count"], paths=shown, patterns=shown))
        out += [FIX_PREFIX + HINT_FIX[h["hint"]]] if h["hint"] in HINT_FIX else []
    if doc["incomplete"]:
        out.append(ACTION_LINE[doc["query"]].format(
            n=len(doc["incomplete"]),
            reasons=", ".join(f"{r['reason']}: {r['subject']}" for r in doc["incomplete"])))
    elif doc["query"] == "affected-tests":
        out.append(RECOMMEND_LINE)
    return [safe(l) for l in out]


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
            q.add_argument("--history", action="store_true",
                           help="add the files that changed together with an input in past commits")
        else:
            q.add_argument("--moved", action="store_true",
                           help="take the inputs from code-anchor's moved list; no path beside it")
        q.add_argument("--all", action="store_true", help="every row, and the history pages named")
        q.add_argument("--json", action="store_true", help="print the answer as JSON")
        q.add_argument("paths", nargs="*" if name == "anchors" else "+",
                       help="plant paths, or - to read one per stdin line")
    s = sub.add_parser("symbols", help="where each name is defined")
    s.add_argument("--all", action="store_true", help="every definition")
    s.add_argument("--json", action="store_true", help="print the answer as JSON")
    s.add_argument("names", nargs="+", help="names (a dotted name matches a qualified one whole), or - for stdin")
    args = ap.parse_args(argv)
    if getattr(args, "depth", 1) is not None and not 1 <= getattr(args, "depth", 1) <= MAX_DEPTH:
        raise Usage(f"--depth takes 1 to {MAX_DEPTH}")
    if getattr(args, "moved", False) and args.paths:
        raise Usage("--moved takes no path and no -")
    if args.query == "anchors" and not args.moved and not args.paths:
        raise Usage("anchors takes a path, - or --moved")
    field = "names" if args.query == "symbols" else "paths"
    if getattr(args, field, None) == ["-"]:
        setattr(args, field, [l for l in sys.stdin.buffer.read().decode("utf-8", "surrogateescape").split("\n")
                              if l])
    refused = next((n for n in getattr(args, "names", []) if not NAME_RE.fullmatch(n)), None)
    if refused is not None:
        raise Usage(f"{refused!r} is not a name")
    return args


def main(argv=None) -> int:
    try:
        args = parse(sys.argv[1:] if argv is None else argv)
    except Usage as e:
        print(f"usage: source-index.py {{build|impact|affected-tests|anchors|symbols}} ...: {safe(e)}",
              file=sys.stderr)
        return 2
    doc = answer(args.query, args, Path.cwd())
    if args.json:
        sys.stdout.write(json.dumps(doc, sort_keys=True, indent=1, ensure_ascii=True) + "\n")
    else:
        sys.stdout.write("\n".join(text_view(doc, getattr(args, "all", False), getattr(args, "moved", False)))
                         + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
