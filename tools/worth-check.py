#!/usr/bin/env python3
"""worth-check.py: flag a test whose only assertions read back a literal the
same change adds (SPEC-0009).

Placed in a plant as docs/graph/worth-check.py and run from the plant root:

    python3 docs/graph/worth-check.py [--root DIR] [--baseline FILE]
                                      [--write-baseline] [--json] [PATH...]
    python3 docs/graph/worth-check.py --removal-list [--spec SPEC-NNNN]

A read-back test is red while a line is absent and green once it is present,
so it catches nothing the change itself does not already show (ADR-0034). The
check reads each test's assertions and flags a test only when every assertion
compares a literal with a value the test reads back unchanged: a declared
constant, a config entry, or text read from a file. It is a heuristic, static
and without a model, and it errs toward sparing. It spares:

  - a test that feeds inputs to logic: any call into the code under test, a
    pattern, a condition, an order of precedence or a computed value;
  - a regression test for a bug: a comment, docstring or name that names the
    bug, the issue or the regression;
  - a security negative control: an assertion that something is refused or
    absent (`not in`, `!=`, `is False`, `.not.`), or a test about security;
  - a test with no assertion it can read.

It never flags by a test's name or length, and it never removes or edits a
test.

The test layout is TEST_GLOBS and SKIP_DIRS in docs/graph/spec-lint.py, the
same source docs/graph/source-index.py reads; the file is read, never
imported. It reads Python (with ast) and TypeScript or JavaScript. Every other
test file is listed as `not checked (<language>)`, and a file that does not
parse is `not checked` with the reason: an unread file is never reported as
passing. A plant whose spec-lint.py is missing or sets no TEST_GLOBS gets one
line saying the check is not configured, and exit 0.

Keep a test that earns its place with a comment line directly above it (any
comment syntax), for example:

    # worth-check: keep — the label is a contract with the mobile client

The report prints each kept test with its reason. A keep line without a reason
keeps nothing.

The baseline is the plant's file docs/graph/worth-baseline.txt, tracked in
Git, one `path::name` per line: the tests flagged on the day it was recorded,
for a project adopted with an existing suite. A flagged test in the baseline
is reported and does not fail; a baseline entry that no longer flags is
reported as shrinkable. --write-baseline records today's flags; the first
write is free, and every later write may only shrink the file, so it refuses
to add a test. No baseline file is an empty baseline.

--removal-list prints the flagged tests as one numbered batch for the owner's
confirmation: each test, why it is flagged, its §10 row and origin read from
docs/graph/specs/, and the contract it would leave without evidence. A test of
origin `bug`, a security control, and a test no §10 row maps print NOT
REMOVABLE AUTOMATICALLY. --spec SPEC-NNNN narrows the batch to the tests that
spec's §10 maps, its baseline tests included: the listing a reopened spec owes.
The list is read-only and exits 0; a test leaves the suite only when the owner
names it in the chat (protocol.test-first, Removing a test that catches nothing).

In the gate: a newly written test the check flags fails the plant's gate
unless it is kept. A plant puts the check in its verification runbook
(docs/graph/runbooks/verification.md) as the gate row
`python3 docs/graph/worth-check.py`, expected exit 0, once TEST_GLOBS names
its test layout (grow.gate.spec-wired); until then the row prints the
not-configured line and passes.

Exit codes: 0 nothing new is flagged, or the plant is not configured;
1 a flagged test is neither kept nor in the baseline, or --write-baseline was
refused; 2 a usage error or an input it cannot read (the path and the reason
are named).
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import sys
import tokenize
from pathlib import Path

sys.dont_write_bytecode = True

# --- constants and texts (SPEC-0009 §6): this file is their one home --------
SCHEMA = "cypress.worth-check/1"
TEST_DECLARATION = "docs/graph/spec-lint.py"     # TEST_GLOBS and SKIP_DIRS
BASELINE = "docs/graph/worth-baseline.txt"
NOT_CONFIGURED = ("worth-check: not configured for this plant "
                  "(set TEST_GLOBS in docs/graph/spec-lint.py)")
BASELINE_HEADER = ("# worth-check baseline: tests flagged when it was recorded. "
                   "It only shrinks: python3 docs/graph/worth-check.py --write-baseline")
# spec-lint.py's SKIP_DIRS serves when the plant declares none.
DEFAULT_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
                     "dist", "build", "target", ".next"}

LANGUAGES = {".py": "python",
             ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
             ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript"}
OTHER_LANGUAGES = {".sh": "shell", ".bash": "shell", ".zsh": "shell", ".bats": "shell",
                   ".go": "go", ".rb": "ruby", ".rs": "rust", ".java": "java", ".kt": "kotlin",
                   ".kts": "kotlin", ".swift": "swift", ".cs": "csharp", ".php": "php",
                   ".ex": "elixir", ".exs": "elixir", ".scala": "scala", ".c": "c", ".cc": "c++",
                   ".cpp": "c++", ".dart": "dart", ".lua": "lua", ".pl": "perl", ".r": "r"}
COMMENT = {"python": "#", "typescript": "//", "javascript": "//"}

KEEP_RE = re.compile(r"worth-check:\s*keep\b\s*[—–:-]*\s*(.*?)\s*(?:\*/)?\s*$")
# A comment, docstring, name or title naming a bug spares the test (ADR-0034:
# a bug reproduction is always written and stays).
REGRESSION_RE = re.compile(r"\b(?:regress\w*|bugs?|issues?|reproduc\w*|hotfix\w*|incidents?)\b"
                           r"|#\d+", re.I)
TICKET_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
# Words that make a test a security control; read over the test's whole text
# with identifiers split into words.
SECURITY_RE = re.compile(
    r"\b(?:secur\w*|auth\w*|csrf|xsrf|xss|inject\w*|travers\w*|secrets?|passw\w*|tokens?|"
    r"permission\w*|forbid\w*|denied|deny|sanitiz\w*|escap\w*|privileg\w*|csp|cors|tls|ssl|"
    r"https|cookies?|session\w*|admin\w*|login|logout|credential\w*|encrypt\w*|decrypt\w*|"
    r"nonce|unsafe|untrusted|malicious|attack\w*|exploit\w*)\b", re.I)

# Python: the calls that read a value back rather than compute one.
PY_READ_FUNCS = {"open", "Path", "PurePath", "PurePosixPath", "len", "str", "bytes", "list",
                 "tuple", "set", "frozenset", "sorted", "getattr", "repr"}
PY_READ_DOTTED = {"pathlib.Path", "os.path.join", "os.path.dirname", "os.path.abspath",
                  "os.path.realpath", "os.path.normpath", "os.fspath", "io.open", "codecs.open",
                  "json.load", "json.loads", "tomllib.load", "tomllib.loads", "yaml.safe_load",
                  "importlib.import_module"}
PY_RE_FUNCS = {"re.search", "re.match", "re.fullmatch", "re.findall"}   # literal pattern first
PY_READ_METHODS = {"read", "read_text", "read_bytes", "readlines", "readline", "decode", "strip",
                   "lstrip", "rstrip", "lower", "upper", "casefold", "splitlines", "split",
                   "joinpath", "resolve", "absolute", "with_name", "with_suffix", "get", "keys",
                   "values", "items", "count", "find", "index", "startswith", "endswith", "open"}
PY_POSITIVE = {"assertEqual", "assertEquals", "assertIn", "assertRegex", "assertRegexpMatches",
               "assertCountEqual", "assertListEqual", "assertDictEqual", "assertSetEqual",
               "assertTupleEqual", "assertSequenceEqual", "assertMultiLineEqual", "assertIs",
               "assertAlmostEqual"}
PY_NEGATIVE = {"assertNotEqual", "assertNotEquals", "assertNotIn", "assertFalse", "assertIsNone",
               "assertIsNot", "assertNotRegex", "assertNotAlmostEqual"}

# TypeScript and JavaScript.
JS_READ_CALLS = {"readFileSync", "fs.readFileSync", "fs.promises.readFile", "promises.readFile",
                 "fsp.readFile", "readFile", "path.join", "path.resolve", "path.dirname", "join",
                 "resolve", "dirname", "fileURLToPath", "url.fileURLToPath", "JSON.parse",
                 "String", "URL", "require", "expect", "assert"}
JS_READ_METHODS = {"toString", "trim", "trimStart", "trimEnd", "split", "toLowerCase",
                   "toUpperCase", "includes", "startsWith", "endsWith", "indexOf", "match"}
JS_POSITIVE = {"toBe", "toEqual", "toStrictEqual", "toContain", "toMatch", "toContainEqual",
               "toHaveLength", "toMatchObject", "toHaveProperty", "toBeCloseTo"}
JS_NO_LITERAL = {"toBeTruthy", "toBeDefined"}
JS_NEGATIVE = {"toBeFalsy", "toBeNull", "toBeUndefined", "toBeNaN"}
NODE_POSITIVE = {"equal", "strictEqual", "deepEqual", "deepStrictEqual", "match", "ok"}
NODE_NEGATIVE = {"notEqual", "notStrictEqual", "notDeepEqual", "notDeepStrictEqual",
                 "doesNotMatch"}
JS_KEYWORDS = {"break", "case", "catch", "class", "const", "continue", "debugger", "default",
               "delete", "do", "else", "export", "extends", "finally", "for", "function", "if",
               "import", "in", "instanceof", "let", "new", "return", "super", "switch", "throw",
               "try", "typeof", "var", "void", "while", "with", "yield", "await", "async", "of",
               "static", "as", "from", "type", "interface", "enum", "satisfies"}
JS_LITERAL_WORDS = {"true", "false", "null", "undefined", "NaN", "Infinity"}
JS_GLOBALS = {"__dirname", "__filename", "JSON", "String", "Number", "Boolean", "URL", "import",
              "meta", "expect", "assert", "require", "string", "number", "boolean", "any",
              "unknown", "never", "object", "Record", "Array", "Promise", "const"}
JS_PUNCT = sorted([">>>=", "...", "===", "!==", "**=", "<<=", ">>=", ">>>", "=>", "?.", "??",
                   "==", "!=", "<=", ">=", "&&", "||", "++", "--", "+=", "-=", "*=", "/=", "%=",
                   "&=", "|=", "^=", "**", "<<", ">>"], key=len, reverse=True)
JS_REGEX_AFTER = set("(,=:[!&|?{};+-*%<>~^") | {"=>", "&&", "||", "??", "==", "===", "!=",
                                                "!==", "return", "typeof", "case", "do", "else",
                                                "in", "of", "new", "delete", "void", "throw",
                                                "yield", "await"}


class Unreadable(Exception):
    """An input the check cannot read; exit 2 with the path and reason."""


class NotParsed(Exception):
    """A test file that does not parse: listed as not checked, never read."""


# --- the plant's test declaration --------------------------------------------
def read_test_declaration(root: Path) -> dict:
    """TEST_GLOBS (a list of strings) and SKIP_DIRS (a set or list of strings),
    each read with ast.literal_eval from its top-level assignment in the
    plant's spec-lint.py, as source-index.py reads them."""
    path = root / TEST_DECLARATION
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError, RecursionError):
        return {}
    kinds = {"TEST_GLOBS": (list,), "SKIP_DIRS": (set, list)}
    found = {}
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) and node.value else [])
        for name in [t.id for t in targets if isinstance(t, ast.Name) and t.id in kinds]:
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError, RecursionError):
                continue
            if isinstance(value, kinds[name]) and all(isinstance(g, str) for g in value):
                found[name] = value
    return found


def glob_regex(pattern: str):
    """A pathlib glob from the plant root as a regex over a plant-relative path:
    `**` is any number of directories, any other segment one directory level."""
    def segment(seg: str) -> str:
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
    segs = [s for s in pattern.split("/") if s not in ("", ".")]
    parts = []
    for k, seg in enumerate(segs):
        last = k == len(segs) - 1
        if seg == "**":
            parts.append("(?:[^/]+/)*" + ("[^/]+" if last else ""))
        else:
            parts.append(segment(seg) + ("" if last else "/"))
    return re.compile("".join(parts) + r"\Z", re.S)


def walk(root: Path, base: Path, skip: set):
    """Every file under base, plant-relative, skipping SKIP_DIRS and symlinked
    directories."""
    for here, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in skip and not os.path.islink(os.path.join(here, d)))
        for f in sorted(files):
            yield Path(here, f).relative_to(root).as_posix()


def language(rel: str, root: Path) -> str:
    ext = os.path.splitext(rel)[1].lower()
    if ext in LANGUAGES:
        return LANGUAGES[ext]
    if ext:
        return OTHER_LANGUAGES.get(ext, ext[1:])
    try:
        with open(root / rel, "rb") as fh:
            first = fh.readline(200)
    except OSError:
        return "no extension"
    if first.startswith(b"#!"):
        words = first[2:].decode("utf-8", "replace").split()
        if words and os.path.basename(words[0]) == "env":
            words = [w for w in words[1:] if not w.startswith("-")]
        interp = os.path.basename(words[0]) if words else ""
        if interp.startswith("python"):
            return "python"
        if interp in ("bash", "sh", "zsh"):
            return "shell"
        if interp in ("node", "deno", "bun"):
            return "javascript"
    return "no extension"


def read_source(root: Path, rel: str) -> str:
    try:
        data = (root / rel).read_bytes()
    except OSError as e:
        raise Unreadable(f"cannot read {rel}: {e.strerror or e}") from None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise Unreadable(f"cannot read {rel}: it is not UTF-8 (byte 0x{data[e.start]:02x} at "
                         f"offset {e.start}); save it as UTF-8, or leave it out of TEST_GLOBS "
                         f"in {TEST_DECLARATION}") from None


def words(text: str) -> str:
    """Identifiers split into words, so `SESSION_COOKIE_SECURE` reads as three."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text.replace("_", " "))


def keep_reason(lines: list[str], first: int, prefixes: tuple) -> tuple[bool, str | None]:
    """(a keep line is there, its reason) from the comment lines directly above
    1-based line `first`."""
    n = first - 2
    while n >= 0:
        s = lines[n].strip()
        if not s.startswith(prefixes):
            break
        m = KEEP_RE.search(s)
        if m:
            return True, (m.group(1).strip() or None)
        n -= 1
    return False, None


def comments_above(lines: list[str], first: int, prefixes: tuple) -> str:
    out, n = [], first - 2
    while n >= 0 and lines[n].strip().startswith(prefixes):
        out.append(lines[n].strip())
        n -= 1
    return "\n".join(reversed(out))


# --- Python -------------------------------------------------------------------
LIT, DECL, READ, LOGIC = "literal", "declared", "read", "logic"


def combine(kinds) -> str:
    kinds = set(kinds)
    for k in (LOGIC, READ, DECL):
        if k in kinds:
            return k
    return LIT


def dotted(node) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


class PyTest:
    """One Python test function, read statement by statement."""

    def __init__(self, fn, module_env: dict):
        self.module_env = module_env
        self.env: dict = {}
        self.logic = False
        self.assertions: list[tuple[str, list]] = []   # (status, literal nodes)
        a = fn.args
        for arg in a.posonlyargs + a.args + a.kwonlyargs + [x for x in (a.vararg, a.kwarg) if x]:
            self.env[arg.arg] = LOGIC
        self.block(fn.body, top=True)

    def name(self, n: str) -> str:
        if n in self.env:
            return self.env[n]
        if n in self.module_env:
            return self.module_env[n]
        if n in ("__file__", "__name__"):
            return READ
        return LOGIC

    def ev(self, e) -> str:
        if isinstance(e, ast.Constant):
            return LIT
        if isinstance(e, ast.JoinedStr):
            return combine(self.ev(v.value) for v in e.values if isinstance(v, ast.FormattedValue))
        if isinstance(e, (ast.List, ast.Tuple, ast.Set)):
            return combine(self.ev(x) for x in e.elts)
        if isinstance(e, ast.Dict):
            return combine(self.ev(x) for x in list(e.values) + [k for k in e.keys if k])
        if isinstance(e, ast.Name):
            return self.name(e.id)
        if isinstance(e, ast.Attribute):
            k = self.ev(e.value)
            return READ if k == LIT else k
        if isinstance(e, ast.Subscript):
            return combine([self.ev(e.value), self.ev(e.slice)])
        if isinstance(e, ast.Slice):
            return combine(self.ev(x) for x in (e.lower, e.upper, e.step) if x)
        if isinstance(e, ast.BinOp):
            return combine([self.ev(e.left), self.ev(e.right)])
        if isinstance(e, ast.UnaryOp):
            return self.ev(e.operand)
        if isinstance(e, ast.BoolOp):
            return combine(self.ev(v) for v in e.values)
        if isinstance(e, ast.Compare):
            return combine([self.ev(e.left)] + [self.ev(c) for c in e.comparators])
        if isinstance(e, ast.IfExp):
            return combine([self.ev(e.test), self.ev(e.body), self.ev(e.orelse)])
        if isinstance(e, ast.Starred):
            return self.ev(e.value)
        if isinstance(e, ast.Call):
            return self.call(e)
        return LOGIC

    def call(self, e: ast.Call) -> str:
        args = combine([self.ev(a) for a in e.args] + [self.ev(k.value) for k in e.keywords])
        if args == LOGIC:
            return LOGIC
        f = e.func
        if isinstance(f, ast.Name):
            return READ if f.id in PY_READ_FUNCS and f.id not in self.env else LOGIC
        if isinstance(f, ast.Attribute):
            name = dotted(f)
            if name in PY_READ_DOTTED:
                return READ
            if name in PY_RE_FUNCS:
                first = e.args[0] if e.args else None
                return READ if isinstance(first, ast.Constant) else LOGIC
            if f.attr in PY_READ_METHODS and self.ev(f.value) in (READ, LIT):
                return READ
        return LOGIC

    def bind(self, target, kind: str) -> None:
        if isinstance(target, ast.Name):
            self.env[target.id] = kind
        elif isinstance(target, (ast.Tuple, ast.List)):
            for t in target.elts:
                self.bind(t, kind)
        elif isinstance(target, ast.Starred):
            self.bind(target.value, kind)
        else:
            self.logic = True

    def block(self, body, top=False) -> None:
        for i, st in enumerate(body):
            if top and i == 0 and isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant):
                continue                                   # the docstring
            self.statement(st)

    def statement(self, st) -> None:
        if isinstance(st, ast.Assert):
            self.assertions.append(self.judge(st.test))
        elif isinstance(st, ast.Expr):
            if self.assertion_call(st.value):
                return
            if self.ev(st.value) == LOGIC:
                self.logic = True
        elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            if st.value is None:
                return
            k = self.ev(st.value)
            if k == LOGIC:
                self.logic = True
            for t in (st.targets if isinstance(st, ast.Assign) else [st.target]):
                self.bind(t, k)
        elif isinstance(st, (ast.With, ast.AsyncWith)):
            for item in st.items:
                k = self.ev(item.context_expr)
                if k == LOGIC:
                    self.logic = True
                if item.optional_vars is not None:
                    self.bind(item.optional_vars, k)
            self.block(st.body)
        elif isinstance(st, (ast.For, ast.AsyncFor)):
            k = self.ev(st.iter)
            if k == LOGIC:
                self.logic = True
            self.bind(st.target, k)
            self.block(st.body)
            self.block(st.orelse)
        elif isinstance(st, ast.If):
            if self.ev(st.test) == LOGIC:
                self.logic = True
            self.block(st.body)
            self.block(st.orelse)
        elif isinstance(st, (ast.Import, ast.ImportFrom)):
            for a in st.names:
                self.env[(a.asname or a.name).split(".")[0]] = DECL
        elif isinstance(st, ast.Pass) or (isinstance(st, ast.Return) and st.value is None):
            return
        else:
            self.logic = True

    def assertion_call(self, e) -> bool:
        """A unittest assertion method: recorded, True; anything else False."""
        if not (isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute)
                and e.func.attr.startswith("assert")):
            return False
        attr = e.func.attr
        if attr == "assertTrue" and e.args:
            self.assertions.append(self.judge(e.args[0]))
        elif attr in PY_NEGATIVE:
            self.assertions.append(("negative", []))
        elif attr in PY_POSITIVE:
            self.assertions.append(self.operands(e.args[:2], negative=False))
        else:
            self.assertions.append((LOGIC, []))
        return True

    def operands(self, nodes, negative: bool):
        kinds = [self.ev(n) for n in nodes]
        if LOGIC in kinds:
            return LOGIC, []
        lits = [n for n, k in zip(nodes, kinds) if k == LIT]
        if negative or any(isinstance(n, ast.Constant) and (n.value is False or n.value is None)
                           for n in lits):
            return "negative", []
        if lits and any(k in (READ, DECL) for k in kinds):
            return "readback", lits
        return "no literal", []

    def judge(self, e):
        if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.Not):
            return "negative", []
        if isinstance(e, ast.Compare):
            neg = any(isinstance(op, (ast.NotEq, ast.NotIn, ast.IsNot)) for op in e.ops)
            return self.operands([e.left] + e.comparators, negative=neg)
        if isinstance(e, ast.BoolOp):
            parts = [self.judge(v) for v in e.values]
            for status in (LOGIC, "negative", "no literal"):
                if any(p[0] == status for p in parts):
                    return status, []
            return "readback", [n for p in parts for n in p[1]]
        k = self.ev(e)
        if k == LOGIC:
            return LOGIC, []
        if isinstance(e, ast.Call) and k == READ:
            lits = [a for a in e.args if isinstance(a, ast.Constant)]
            if lits:
                return "readback", lits
        return "no literal", []


def py_literal(node) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return json.dumps(node.value, ensure_ascii=False)
    return ast.unparse(node)


def py_module_env(tree) -> dict:
    env: dict = {}
    probe = PyTest.__new__(PyTest)
    probe.module_env, probe.env, probe.logic, probe.assertions = env, {}, False, []
    for st in tree.body:
        if isinstance(st, (ast.Import, ast.ImportFrom)):
            for a in st.names:
                if a.name != "*":
                    env[(a.asname or a.name).split(".")[0]] = DECL
        elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            env[st.name] = DECL
        elif isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None:
            k = probe.ev(st.value)
            for t in (st.targets if isinstance(st, ast.Assign) else [st.target]):
                for n in ast.walk(t):
                    if isinstance(n, ast.Name):
                        env[n.id] = k
    return env


def read_python(rel: str, src: str) -> list[dict]:
    try:
        tree = ast.parse(src, filename=rel)
    except SyntaxError as e:
        raise NotParsed(f"python: does not parse at line {e.lineno}: {e.msg}") from None
    except (ValueError, RecursionError) as e:
        raise NotParsed(f"python: does not parse: {e}") from None
    lines = src.splitlines()
    comments: dict[int, str] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                comments[tok.start[0]] = tok.string
    except (tokenize.TokenError, SyntaxError):
        pass
    env = py_module_env(tree)
    found = []
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name.startswith("test"):
            found.append((st.name, st))
        elif isinstance(st, ast.ClassDef):
            for m in st.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test"):
                    found.append((f"{st.name}::{m.name}", m))
    out = []
    for name, fn in found:
        first = min([fn.lineno] + [d.lineno for d in fn.decorator_list])
        last = fn.end_lineno or fn.lineno
        t = PyTest(fn, env)
        above = comments_above(lines, first, ("#",))
        inside = "\n".join(c for n, c in comments.items() if first <= n <= last)
        doc = ast.get_docstring(fn) or ""
        kept, reason = keep_reason(lines, first, ("#",))
        out.append(verdict(rel, name, first, "python", t.logic, t.assertions,
                           marker_text=f"{above}\n{inside}\n{doc}\n{words(name)}",
                           whole_text=words("\n".join(lines[first - 1:last]) + "\n" + above),
                           literal_of=py_literal, kept=kept, reason=reason))
    return out


# --- TypeScript and JavaScript ----------------------------------------------
class Tok:
    __slots__ = ("kind", "value", "line", "subst")

    def __init__(self, kind, value, line, subst=False):
        self.kind, self.value, self.line, self.subst = kind, value, line, subst

    def __repr__(self):
        return f"{self.kind}:{self.value}"


ID_RE = re.compile(r"[A-Za-z_$][\w$]*")
NUM_RE = re.compile(r"0[xXoObB][\da-fA-F_]+n?|(?:\d[\d_]*\.?\d*|\.\d+)(?:[eE][+-]?\d+)?n?")


def js_lex(src: str):
    """(tokens, comments by line) for a TypeScript or JavaScript file."""
    toks: list[Tok] = []
    comments: dict[int, str] = {}
    i, line, n = 0, 1, len(src)
    if src.startswith("#!"):
        i = src.find("\n") if "\n" in src else n
    stack: list[str] = []          # "{" for a brace, "${" for a template hole

    def prev():
        return toks[-1] if toks else None

    def regex_allowed() -> bool:
        p = prev()
        return p is None or (p.kind == "punc" and p.value in JS_REGEX_AFTER) or (
            p.kind == "id" and p.value in JS_REGEX_AFTER) or (p.kind == "punc" and p.value == "}")

    def template(j: int):
        """Scan a template literal from after its opening backtick; returns
        (end index after the closing backtick, cooked text, has a hole)."""
        nonlocal line
        buf, subst = [], False
        while j < n:
            c = src[j]
            if c == "\\":
                buf.append(src[j:j + 2])
                j += 2
                continue
            if c == "`":
                return j + 1, "".join(buf), subst
            if c == "$" and src.startswith("${", j):
                subst = True
                depth, j = 1, j + 2
                while j < n and depth:
                    c = src[j]
                    if c in "'\"":
                        j = string_end(j)
                        continue
                    if c == "`":
                        j, _, _ = template(j + 1)
                        continue
                    if c == "\n":
                        line += 1
                    depth += (c == "{") - (c == "}")
                    j += 1
                continue
            if c == "\n":
                line += 1
            buf.append(c)
            j += 1
        raise NotParsed(f"a template literal is not closed (line {line})")

    def string_end(j: int) -> int:
        q, j = src[j], j + 1
        while j < n:
            if src[j] == "\\":
                j += 2
                continue
            if src[j] == q:
                return j + 1
            if src[j] == "\n":
                break
            j += 1
        raise NotParsed(f"a string is not closed (line {line})")

    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            i += 1
        elif c.isspace():
            i += 1
        elif src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            comments[line] = src[i:j]
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            if j < 0:
                raise NotParsed(f"a comment is not closed (line {line})")
            for k, part in enumerate(src[i:j + 2].split("\n")):
                comments[line + k] = part
            line += src.count("\n", i, j)
            i = j + 2
        elif c in "'\"":
            j = string_end(i)
            toks.append(Tok("str", js_unescape(src[i + 1:j - 1]), line))
            i = j
        elif c == "`":
            start = line
            j, text, subst = template(i + 1)
            toks.append(Tok("tmpl", js_unescape(text), start, subst))
            i = j
        elif c == "/" and regex_allowed():
            j, in_class = i + 1, False
            while j < n and src[j] != "\n":
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "[":
                    in_class = True
                elif src[j] == "]":
                    in_class = False
                elif src[j] == "/" and not in_class:
                    break
                j += 1
            if j >= n or src[j] != "/":
                raise NotParsed(f"a regular expression is not closed (line {line})")
            j += 1
            while j < n and (src[j].isalpha()):
                j += 1
            toks.append(Tok("regex", src[i:j], line))
            i = j
        elif (m := ID_RE.match(src, i)):
            toks.append(Tok("id", m.group(0), line))
            i = m.end()
        elif c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            m = NUM_RE.match(src, i)
            toks.append(Tok("num", m.group(0), line))
            i = m.end()
        else:
            p = next((p for p in JS_PUNCT if src.startswith(p, i)), c)
            if p == "{":
                stack.append("{")
            elif p == "}":
                if not stack:
                    raise NotParsed(f"a closing brace has no opening one (line {line})")
                stack.pop()
            toks.append(Tok("punc", p, line))
            i += len(p)
    if stack:
        raise NotParsed(f"{len(stack)} brace(s) are not closed at the end of the file")
    return toks, comments


def js_unescape(s: str) -> str:
    simple = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "b": "\b", "f": "\f", "v": "\v"}

    def one(m):
        e = m.group(1)
        if e[0] == "u":
            return chr(int(e[1:].strip("{}"), 16))
        if e[0] == "x":
            return chr(int(e[1:], 16))
        return simple.get(e, e)
    return re.sub(r"\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", one, s, flags=re.S)


def matching(toks, i: int, open_: str, close: str) -> int:
    """Index of the token closing the one at i."""
    depth = 0
    for j in range(i, len(toks)):
        if toks[j].kind == "punc":
            if toks[j].value == open_:
                depth += 1
            elif toks[j].value == close:
                depth -= 1
                if depth == 0:
                    return j
    raise NotParsed(f"a '{open_}' at line {toks[i].line} is not closed")


def split_args(toks) -> list[list[Tok]]:
    out, cur, depth = [], [], 0
    for t in toks:
        if t.kind == "punc" and t.value in ("(", "[", "{"):
            depth += 1
        elif t.kind == "punc" and t.value in (")", "]", "}"):
            depth -= 1
        if depth == 0 and t.kind == "punc" and t.value == ",":
            out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append(cur)
    return out


def js_statement_end(toks, i: int) -> int:
    """Index after the declaration's initializer starting at i (depth 0)."""
    depth, j = 0, i
    while j < len(toks):
        t = toks[j]
        if t.kind == "punc" and t.value in ("(", "[", "{"):
            depth += 1
        elif t.kind == "punc" and t.value in (")", "]", "}"):
            if depth == 0:
                return j
            depth -= 1
        elif depth == 0 and t.kind == "punc" and t.value in (";", ","):
            return j
        elif (depth == 0 and j > i and t.line > toks[j - 1].line
              and toks[j - 1].kind in ("id", "str", "num", "tmpl", "regex", "punc")
              and (toks[j - 1].kind != "punc" or toks[j - 1].value in (")", "]", "}"))
              and not (t.kind == "punc" and t.value not in ("(", "[", "{", "!", "~"))):
            return j
        j += 1
    return j


class JsFile:
    def __init__(self, rel: str, src: str, lang: str):
        self.rel, self.lang = rel, lang
        self.toks, self.comments = js_lex(src)
        self.lines = src.splitlines()
        self.top: dict = {}          # top-level name -> DECL | READ | LOGIC
        self.module_scan()

    def call_kind(self, toks, j: int, params: set, local: set) -> str:
        """READ when the call opening at toks[j] ('(') reads a value, else LOGIC."""
        p = toks[j - 1] if j else None
        if p is None or p.kind != "id":
            return LOGIC
        chain, k = [p.value], j - 1
        while k >= 2 and toks[k - 1].kind == "punc" and toks[k - 1].value in (".", "?."):
            if toks[k - 2].kind == "id":
                chain.append(toks[k - 2].value)
                k -= 2
            else:
                chain.append(")")               # a method on a call's result
                break
        chain.reverse()
        name = ".".join(chain)
        if chain[0] == ")":
            if chain[-1] in JS_READ_METHODS or chain[-1].startswith("to") or chain[-1] == "not":
                return READ
            return LOGIC
        root = chain[0]
        if root in params:
            return LOGIC
        if name in JS_READ_CALLS or (root == "assert" and len(chain) == 2):
            return READ
        if len(chain) > 1 and chain[-1] in JS_READ_METHODS and (
                root in local or self.top.get(root) in (READ, DECL)):
            return READ
        return LOGIC

    def module_scan(self) -> None:
        toks, depth, i = self.toks, 0, 0
        while i < len(toks):
            t = toks[i]
            if t.kind == "punc" and t.value in ("(", "[", "{"):
                depth += 1
            elif t.kind == "punc" and t.value in (")", "]", "}"):
                depth -= 1
            elif depth == 0 and t.kind == "id" and t.value == "import":
                j = i + 1
                while j < len(toks) and not (toks[j].kind in ("str",) or toks[j].value in ("from", ";")):
                    if toks[j].kind == "id" and toks[j].value not in ("type", "as"):
                        self.top[toks[j].value] = DECL
                    j += 1
                i = j
                continue
            elif depth == 0 and t.kind == "id" and t.value in ("const", "let", "var"):
                j = i + 1
                names = []
                while j < len(toks) and not (toks[j].kind == "punc" and toks[j].value in ("=", ";")):
                    if toks[j].kind == "id" and toks[j].value not in JS_GLOBALS:
                        names.append(toks[j].value)
                    if toks[j].kind == "punc" and toks[j].value == ":" and not names:
                        break
                    j += 1
                if j < len(toks) and toks[j].value == "=":
                    end = js_statement_end(toks, j + 1)
                    rhs = toks[j + 1:end]
                    kind = READ
                    if any(r.kind == "id" and r.value == "require" for r in rhs):
                        kind = DECL
                    for k in range(j + 1, end):
                        if toks[k].kind == "punc" and toks[k].value == "(" and \
                                self.call_kind(toks, k, set(), set()) == LOGIC:
                            kind = LOGIC
                        if toks[k].kind == "tmpl" and toks[k].subst:
                            kind = LOGIC
                    for nm in names:
                        self.top[nm] = kind
                    i = end
                    continue
                for nm in names:
                    self.top[nm] = LOGIC                 # declared, assigned elsewhere
            elif depth == 0 and t.kind == "id" and t.value in ("function", "class") and \
                    i + 1 < len(toks) and toks[i + 1].kind == "id":
                self.top[toks[i + 1].value] = DECL
            i += 1

    def tests(self) -> list[dict]:
        toks, out = self.toks, []
        for i, t in enumerate(toks):
            if t.kind != "id" or t.value not in ("test", "it"):
                continue
            if i and toks[i - 1].kind == "punc" and toks[i - 1].value in (".", "?."):
                continue
            j = i + 1
            if j + 1 < len(toks) and toks[j].value == "." and toks[j + 1].value == "only":
                j += 2
            if j >= len(toks) or toks[j].value != "(" or toks[j].kind != "punc":
                continue
            close = matching(toks, j, "(", ")")
            args = split_args(toks[j + 1:close])
            if len(args) < 2 or len(args[0]) != 1 or args[0][0].kind not in ("str", "tmpl") \
                    or args[0][0].subst:
                continue
            out.append(self.one(args[0][0].value, t.line, args[1]))
        return out

    def one(self, title: str, line: int, fn: list[Tok]) -> dict:
        params: set = set()
        k = 0
        if k < len(fn) and fn[k].value == "async":
            k += 1
        if k < len(fn) and fn[k].value == "function":
            k += 1
            if k < len(fn) and fn[k].kind == "id":
                k += 1
        if k < len(fn) and fn[k].value == "(":
            end = matching(fn, k, "(", ")")
            params = {x.value for x in fn[k + 1:end] if x.kind == "id"} - JS_GLOBALS
            k = end + 1
        elif k < len(fn) and fn[k].kind == "id":
            params = {fn[k].value}
            k += 1
        if k < len(fn) and fn[k].value == "=>":
            k += 1
        if k < len(fn) and fn[k].value == "{":
            end = matching(fn, k, "{", "}")
            body = fn[k + 1:end]
        else:
            body = fn[k:]
        logic, assertions = self.read_body(body, params)
        first_line = line
        kept, reason = keep_reason(self.lines, first_line, ("//", "/*", "*"))
        above = comments_above(self.lines, first_line, ("//", "/*", "*"))
        last = max([x.line for x in fn] or [line])
        inside = "\n".join(c for n, c in self.comments.items() if line <= n <= last)
        text = " ".join(x.value for x in body if x.kind in ("id", "str", "tmpl"))
        return verdict(self.rel, title, line, self.lang, logic, assertions,
                       marker_text=f"{above}\n{inside}\n{title}",
                       whole_text=words(f"{above}\n{title}\n{text}"),
                       literal_of=js_literal, kept=kept, reason=reason)

    def read_body(self, body: list[Tok], params: set):
        local = set()
        for i, t in enumerate(body):
            if t.kind == "id" and t.value in ("const", "let", "var"):
                j = i + 1
                while j < len(body) and body[j].value not in ("=", ";"):
                    if body[j].kind == "id":
                        local.add(body[j].value)
                    j += 1
        logic = False
        for i, t in enumerate(body):
            if (t.kind == "tmpl" and t.subst) or (t.kind == "punc" and t.value == "=>") or \
                    (t.kind == "id" and t.value in ("function", "this", "class")):
                logic = True
            elif t.kind == "punc" and t.value == "(" and i and body[i - 1].kind == "id" \
                    and body[i - 1].value not in JS_KEYWORDS:
                if self.call_kind(body, i, params, local) == LOGIC:
                    logic = True
            elif t.kind == "punc" and t.value == "(" and i and body[i - 1].kind == "punc" \
                    and body[i - 1].value in (")", "]"):
                logic = True
            elif t.kind == "id" and t.value == "new":
                if not (i + 1 < len(body) and body[i + 1].value == "URL"):
                    logic = True
            elif t.kind == "id" and t.value not in JS_KEYWORDS | JS_LITERAL_WORDS | JS_GLOBALS:
                prop = i and body[i - 1].kind == "punc" and body[i - 1].value in (".", "?.")
                key = i + 1 < len(body) and body[i + 1].kind == "punc" and body[i + 1].value == ":"
                if prop or key:
                    continue
                if t.value in params or (t.value not in local and self.top.get(t.value) not in (READ, DECL)):
                    logic = True
        return logic, self.assertions(body)

    def assertions(self, body: list[Tok]) -> list:
        out = []
        for i, t in enumerate(body):
            if t.kind != "id" or (i and body[i - 1].kind == "punc" and body[i - 1].value in (".", "?.")):
                continue
            if t.value == "expect" and i + 1 < len(body) and body[i + 1].value == "(":
                close = matching(body, i + 1, "(", ")")
                subject = body[i + 2:close]
                j, negative, matcher, margs = close + 1, False, None, []
                while j + 1 < len(body) and body[j].value == "." and body[j + 1].kind == "id":
                    word = body[j + 1].value
                    j += 2
                    if word == "not":
                        negative = True
                    elif word in ("resolves", "rejects"):
                        matcher = "logic"
                    elif j < len(body) and body[j].value == "(":
                        end = matching(body, j, "(", ")")
                        matcher, margs = (matcher or word), body[j + 1:end]
                        j = end + 1
                        break
                out.append(self.expect(subject, matcher, margs, negative))
            elif t.value == "assert":
                if i + 1 < len(body) and body[i + 1].value == "(":
                    method, at = "ok", i + 1
                elif i + 3 < len(body) and body[i + 1].value == "." and body[i + 3].value == "(":
                    method, at = body[i + 2].value, i + 3
                else:
                    continue
                end = matching(body, at, "(", ")")
                out.append(self.node_assert(method, split_args(body[at + 1:end])))
        return out

    @staticmethod
    def operand_status(groups: list[list[Tok]], negative: bool):
        flat = [t for g in groups for t in g]
        if negative or any(t.kind == "punc" and t.value == "!" for t in flat[:1]):
            return "negative", []
        bools = [t for t in flat if t.kind == "id" and t.value in ("false", "null", "undefined")]
        if bools:
            return "negative", []
        lits = [t for t in flat if t.kind in ("str", "num", "regex") or (t.kind == "tmpl" and not t.subst)]
        trues = [t for t in flat if t.kind == "id" and t.value == "true"]
        names = [t for t in flat if t.kind == "id" and t.value not in JS_LITERAL_WORDS]
        if (lits or trues) and names:
            return "readback", lits or trues
        return "no literal", []

    def expect(self, subject, matcher, margs, negative):
        if matcher in JS_NEGATIVE:
            return "negative", []
        if matcher in JS_NO_LITERAL or matcher is None:
            return ("negative", []) if negative else ("no literal", [])
        if matcher not in JS_POSITIVE:
            return LOGIC, []
        return self.operand_status([subject, margs], negative)

    def node_assert(self, method, args):
        if method in NODE_NEGATIVE:
            return "negative", []
        if method not in NODE_POSITIVE:
            return LOGIC, []
        return self.operand_status(args[:1] if method == "ok" else args[:2], False)


def js_literal(tok: Tok) -> str:
    if tok.kind in ("str", "tmpl"):
        return json.dumps(tok.value, ensure_ascii=False)
    return tok.value


def read_js(rel: str, src: str, lang: str) -> list[dict]:
    try:
        return JsFile(rel, src, lang).tests()
    except NotParsed as e:
        raise NotParsed(f"{lang}: does not parse: {e}") from None


# --- the verdict --------------------------------------------------------------
def verdict(path, name, line, lang, logic, assertions, marker_text, whole_text,
            literal_of, kept, reason) -> dict:
    rec = {"test": f"{path}::{name}", "path": path, "name": name, "line": line,
           "language": lang, "verdict": "spared", "why": "", "literals": [],
           "assertions": len(assertions), "keep_without_reason": False}
    statuses = {s for s, _ in assertions}
    if logic or LOGIC in statuses:
        rec["why"] = "feeds inputs to logic"
    elif not assertions:
        rec["why"] = "no assertion to read"
    elif "negative" in statuses:
        rec["why"] = "asserts an absence or a refusal: a negative control"
    elif "no literal" in statuses:
        rec["why"] = "an assertion reads back no literal"
    elif REGRESSION_RE.search(marker_text) or TICKET_RE.search(marker_text):
        rec["why"] = "a regression test for a bug"
    elif SECURITY_RE.search(whole_text):
        rec["why"] = "a security control"
    else:
        lits, seen = [], set()
        nodes = [n for _, ns in assertions for n in ns]
        plain = [n for n in nodes if literal_of(n) not in ("True", "true")] or nodes
        for n in plain:
            s = literal_of(n)
            if s not in seen:
                seen.add(s)
                lits.append(s)
        rec["literals"] = lits
        if kept and reason:
            rec["verdict"], rec["why"] = "kept", reason
        else:
            rec["verdict"], rec["why"] = "flagged", "reads back a literal"
            rec["keep_without_reason"] = kept
    return rec


def flag_line(rec: dict) -> str:
    lits = rec["literals"]
    shown = ", ".join(lits[:3]) + (f" and {len(lits) - 3} more" if len(lits) > 3 else "")
    mark = COMMENT.get(rec["language"], "#")
    return (f"{rec['test']}  reads back {shown} that the same file/change adds; "
            f"only assertion(s): {rec['assertions']}; keep it with a line "
            f"\"{mark} worth-check: keep — <reason>\" above the test if it earns its place")


# --- the run -----------------------------------------------------------------
def read_baseline(path: Path) -> list[str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable(f"cannot read the baseline {path}: {e}") from None
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def collect(root: Path, paths: list[str], globs, skip) -> list[str]:
    rx = [glob_regex(g) for g in globs]
    if not paths:
        return [r for r in walk(root, root, skip) if any(x.match(r) for x in rx)]
    out = []
    for p in paths:
        full = (root / p) if not os.path.isabs(p) else Path(p)
        if not full.exists():
            raise Unreadable(f"{p} does not exist under the plant root ({root}); name a test "
                             f"file or directory")
        try:
            rel = full.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            raise Unreadable(f"{p} is outside the plant root ({root})") from None
        if full.is_dir():
            out += [r for r in walk(root, full, skip) if any(x.match(r) for x in rx)]
        else:
            out.append(rel)
    return sorted(set(out))


def run(args) -> int:
    root = Path(args.root)
    if not root.is_dir():
        raise Unreadable(f"--root {args.root} is not a directory")
    declared = read_test_declaration(root)
    globs = declared.get("TEST_GLOBS")
    if not globs:
        if args.json:
            print(json.dumps({"schema": SCHEMA, "configured": False, "message": NOT_CONFIGURED}))
        else:
            print(NOT_CONFIGURED)
        return 0
    if args.write_baseline and args.paths:
        raise Unreadable("--write-baseline records the whole suite; run it without a PATH")
    if args.removal_list and (args.write_baseline or args.json):
        raise Unreadable("--removal-list prints the batch alone; run it without --write-baseline or --json")
    if args.spec and not args.removal_list:
        raise Unreadable("--spec narrows --removal-list; pass both")
    skip = set(declared.get("SKIP_DIRS", DEFAULT_SKIP_DIRS))
    base_path = root / (args.baseline or BASELINE)
    baseline = read_baseline(base_path)
    base_set = set(baseline or [])

    tests, not_checked, read = [], [], []
    for rel in collect(root, args.paths, globs, skip):
        lang = language(rel, root)
        if lang not in ("python", "typescript", "javascript"):
            not_checked.append({"path": rel, "reason": lang, "language": lang})
            continue
        src = read_source(root, rel)
        try:
            tests += read_python(rel, src) if lang == "python" else read_js(rel, src, lang)
        except NotParsed as e:
            not_checked.append({"path": rel, "reason": str(e), "language": lang})
            continue
        read.append(rel)

    flagged = [t for t in tests if t["verdict"] == "flagged"]
    for t in tests:
        t["in_baseline"] = t["verdict"] == "flagged" and t["test"] in base_set
    new = [t for t in flagged if not t["in_baseline"]]
    old = [t for t in flagged if t["in_baseline"]]
    now = {t["test"] for t in flagged}
    read_set = set(read)
    shrinkable = sorted(e for e in base_set - now
                        if not args.paths or e.split("::", 1)[0] in read_set)
    languages = sorted({n["language"] for n in not_checked})

    if args.removal_list:
        return removal_list(root, flagged, args.spec)
    rc = 1 if new else 0
    messages = []
    if args.write_baseline:
        grow = sorted(now - base_set) if baseline is not None else []
        if grow:
            messages.append(
                f"worth-check: --write-baseline refused: the baseline only shrinks, and "
                f"{len(grow)} flagged test(s) are not in it: {', '.join(grow)}. Remove each, "
                f"make it feed inputs to the logic it guards, or keep it with a "
                f"\"worth-check: keep — <reason>\" line above it; then write again. "
                f"{base_path.relative_to(root) if base_path.is_relative_to(root) else base_path} "
                f"is unchanged.")
            rc = 1
        else:
            keep = sorted(now)
            base_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = base_path.with_name(base_path.name + ".tmp")
            tmp.write_text(BASELINE_HEADER + "\n" + "".join(f"{e}\n" for e in keep), encoding="utf-8")
            os.replace(tmp, base_path)
            was = "no file" if baseline is None else f"{len(baseline)}"
            messages.append(f"worth-check: baseline written: {base_path.relative_to(root) if base_path.is_relative_to(root) else base_path} "
                            f"holds {len(keep)} test(s) (before: {was})")
            for t in new:
                t["in_baseline"] = True
            old, new, shrinkable, rc = old + new, [], [], 0

    summary = (f"worth-check: {len(flagged)} flagged ({len(old)} in baseline), {len(read)} files "
               f"read, {len(not_checked)} not checked"
               + (f" (languages: {', '.join(languages)})" if languages else ""))
    if args.json:
        print(json.dumps({"schema": SCHEMA, "configured": True, "tests": tests,
                          "not_checked": not_checked, "shrinkable": shrinkable,
                          "files_read": len(read), "flagged": len(flagged),
                          "in_baseline": len(old), "messages": messages, "exit": rc}, indent=1))
        return rc
    for t in new:
        print(flag_line(t))
        if t["keep_without_reason"]:
            print(f"worth-check: {t['test']}: its keep line gives no reason, so it keeps "
                  f"nothing; write \"worth-check: keep — <reason>\"")
    if old:
        print(f"worth-check: in the baseline {BASELINE if not args.baseline else args.baseline} "
              f"(reported, not failing; the baseline only shrinks):")
        for t in old:
            print(flag_line(t))
    for t in tests:
        if t["verdict"] == "kept":
            print(f"worth-check: kept: {t['test']} — {t['why']}")
    for e in shrinkable:
        print(f"worth-check: shrinkable: {e} is in the baseline and no longer flags; "
              f"run --write-baseline to drop it")
    for n in not_checked:
        print(f"{n['path']}  not checked ({n['reason']})")
    for m in messages:
        print(m)
    print(summary)
    if new:
        print(f"worth-check: FAIL — {len(new)} flagged test(s) are not in the baseline. For each: "
              f"remove it if a run or a review already proves what it reads back, make it feed "
              f"inputs to the logic it guards, or keep it with a \"worth-check: keep — <reason>\" "
              f"line directly above it. The check never edits a test.")
    return rc


# --- the removal list (ADR-0034 OD3; protocol.test-first, Removing a test) ----
SPECS = "docs/graph/specs"
SECTION_RE = re.compile(r"^##\s+(\d+)\.", re.M)
CONTRACT_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
CHECK_RE = re.compile(r"^- \*\*Check:\*\*[ \t]*(\w+)", re.M)
SLUG_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
CELL_RE = re.compile(r"(?<!\\)\|")
HELD = {"bug": "a bug reproduction stays",
        "security control": "a security control; one that kills no mutant is a finding "
                            "for the security agent",
        "": "origin not recorded; the architect records it on the row first"}


def cells(line: str) -> list[str]:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().strip("`").strip() for c in CELL_RE.split(s)]


def spec_rows(path: Path) -> list[dict]:
    """Every §10 row of one spec that names a test: the risk-based table
    (`| Risk ... | Test ... | Covers | Origin | Status |`) or the legacy one
    (`| Contract / Failure | Test name | Test file | Level | Status |`)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    sid = (re.match(r"SPEC-\d+", path.name) or [path.stem])[0]
    kinds = {}
    for m in CONTRACT_RE.finditer(text):
        nxt = re.search(r"^#{1,3}\s", text[m.end():], re.M)
        c = CHECK_RE.search(text[m.end():m.end() + (nxt.start() if nxt else len(text))])
        kinds[m.group(1)] = c.group(1).lower() if c else "test"
    heads = list(SECTION_RE.finditer(text))
    body = next((text[h.end():heads[i + 1].start() if i + 1 < len(heads) else len(text)]
                 for i, h in enumerate(heads) if h.group(1) == "10"), "")
    rows, head = [], None
    for line in body.splitlines():
        if "|" not in line:
            head = None
            continue
        c = cells(line)
        if head is None:
            head = [x.lower() for x in c]
            continue
        if all(set(x) <= set("-: ") for x in c):
            continue
        get = lambda key: next((c[j] for j, h in enumerate(head) if h.startswith(key) and j < len(c)), "")
        if head[0].startswith("risk"):
            test, status = get("test"), get("status")
            if "::" not in test or re.search(r"\b(?:dropped:|merged into|removed:)", status):
                continue
            path_, name = test.split("::", 1)
            rows.append({"spec": sid, "text": c[0], "path": path_, "name": name,
                         "covers": SLUG_RE.findall(get("covers")), "origin": get("origin").lower()})
        elif head[0].startswith("contract"):
            rows.append({"spec": sid, "text": c[0], "path": get("test file"), "name": get("test name"),
                         "covers": SLUG_RE.findall(c[0]), "origin": ""})
    for r in rows:
        r["kinds"] = kinds
    return rows


def row_matches(row: dict, rec: dict) -> bool:
    return row["path"] == rec["path"] and (row["name"] == rec["name"]
                                           or row["name"] == rec["name"].rsplit("::", 1)[-1])


def removal_list(root: Path, flagged: list[dict], spec: str | None) -> int:
    """Print the batch of flagged tests for the owner's confirmation. Read-only:
    it removes no file and edits no test."""
    specs = sorted((root / SPECS).glob("SPEC-*.md")) if (root / SPECS).is_dir() else []
    if spec and not any(p.name == spec or p.name.startswith(spec + "-") for p in specs):
        raise Unreadable(f"--spec {spec}: no {SPECS}/{spec}-*.md in this plant; name a spec it holds")
    rows = [r for p in specs for r in spec_rows(p)]
    batch = []
    for rec in flagged:
        mine = [r for r in rows if row_matches(r, rec)]
        if spec and not any(r["spec"] == spec for r in mine):
            continue
        batch.append((rec, mine))
    in_batch = {(rec["path"], rec["name"]) for rec, _ in batch}
    where = f" for {spec}" if spec else ""
    print(f"removal batch{where} — {len(batch)} test(s) for the owner's confirmation "
          f"(nothing is removed by this list)")
    for n, (rec, mine) in enumerate(batch, 1):
        lits = ", ".join(rec["literals"][:3])
        one = rec["assertions"] == 1
        print(f" {n}. {rec['test']}")
        print(f"    flagged: {'only assertion reads' if one else 'all %d assertions read' % rec['assertions']} "
              f"back {lits} that the same change adds "
              f"(worth-check{'; in the baseline' if rec.get('in_baseline') else ''})")
        if not mine:
            print("    no §10 row -> NOT REMOVABLE AUTOMATICALLY (no spec maps it; the architect "
                  "maps it to a contract, or records why it has none, first)")
            continue
        held = next((HELD[r["origin"]] for r in mine if r["origin"] in HELD), None)
        for k, r in enumerate(mine):
            verdict = "" if k < len(mine) - 1 else (
                f"  -> NOT REMOVABLE AUTOMATICALLY ({held})" if held else "  -> removable on confirmation")
            text = r["text"] if len(r["text"]) <= 60 else r["text"][:57] + "..."
            print(f"    §10 row: {r['spec']} \"{text}\" origin: {r['origin'] or 'not recorded'}{verdict}")
        if held:
            continue                       # it stays, so it leaves no contract
        left = []
        for r in mine:
            for slug in r["covers"]:
                kind = r["kinds"].get(slug, "test")
                other = [o for o in rows if o["spec"] == r["spec"] and slug in o["covers"]
                         and (o["path"], o["name"]) not in in_batch
                         and not any(row_matches(o, b) for b, _ in batch)]
                if kind == "test" and not other and slug not in [s for s, _ in left]:
                    left.append((slug, kind))
        print("    leaves without evidence: " + (", ".join(
            f"{s} (kind {k}; the architect re-settles its kind)" for s, k in left)
            if left else "none (each contract it covers has other evidence)"))
    if batch:
        print('To confirm, reply in the chat naming the tests to remove, e.g. '
              '"remove tests 1 and 4 of the batch".')
    return 0


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"worth-check: {message}", file=sys.stderr)
        sys.exit(2)


def main(argv=None) -> int:
    ap = Parser(prog="worth-check.py", description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="the plant root (default: the current directory)")
    ap.add_argument("--baseline", help=f"the baseline file, from the root (default: {BASELINE})")
    ap.add_argument("--write-baseline", action="store_true",
                    help="record today's flagged tests; the first write is free, later ones only shrink")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--removal-list", action="store_true",
                    help="print the flagged tests as a batch for the owner's confirmation, each with "
                         "its §10 row, origin and the contract it would leave without evidence; "
                         "read-only, it removes nothing")
    ap.add_argument("--spec", metavar="SPEC-NNNN",
                    help="with --removal-list: only the tests a §10 row of this spec maps, its "
                         "baseline tests included (a reopened spec, clean as you touch)")
    ap.add_argument("paths", nargs="*", metavar="PATH",
                    help="test files or directories to read instead of the whole TEST_GLOBS layout")
    args = ap.parse_args(argv)
    if args.spec and (m := re.match(r"SPEC-\d+", args.spec)):
        args.spec = m.group(0)
    try:
        return run(args)
    except Unreadable as e:
        print(f"worth-check: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
