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
constant, a config entry, or text read from a file. A literal built only from
literals ("Se" + "nd", "".join([...]), [...].join("")) is a literal, and so is
the text of toMatchInlineSnapshot. It is a heuristic, static and without a
model, and it errs toward sparing.

What it reads. The test layout is TEST_GLOBS and SKIP_DIRS in
docs/graph/spec-lint.py, the same source docs/graph/source-index.py reads; the
file is read, never imported. It reads Python (with ast) and TypeScript or
JavaScript. It reads the plant's declarations too: the §10 rows of
docs/graph/specs/SPEC-*.md (as text) and the trust paths, the `kind: crosscut`
nodes of docs/graph/nodes/ marked `trust: true`. For the trust paths it runs
the plant's own tools: docs/graph/source-index.py build lists the files,
docs/graph/graph-lint.py --trust-claims names those a trust node claims, and
docs/graph/source-index.py affected-tests names the test files whose links
reach them. Those runs only happen when the plant marks a trust path and a test
reads back a literal; the source index keeps its derived cache under
.cypress/source-index/ (ADR-0029).

What it spares, and why. The plant's declarations decide first (the owner
decided on 2026-11-11 that the check spares by declaration, not vocabulary):

  - a test a §10 row maps with origin `bug` or `security control`: a bug
    reproduction stays, and a security control is never removed to clear a
    flag. A row with another recorded origin decides alone, so no name and no
    word spares its test; a legacy row that records no origin decides nothing;
  - a test whose file reads or imports a file on a marked trust path, read
    through the source index (its floor included: a test whose references the
    index cannot pin may reach one);
  - where no §10 row decides: a test whose name or title, decorator or marker,
    comment above or inside, or docstring names the bug, the issue, the
    regression or a ticket (`#412` counts, except on a line about a colour); a
    test that uses as a key a string shaped like an HTTP header name
    (X-Frame-Options, Cache-Control); and, only when the plant marks no trust
    path or its trust paths could not be read in full, a test whose
    declarations, identifiers or keys hold a word of the security list (auth,
    csrf, session, token, debug, the standard security header names, and the
    stopgap words role, lockout, origin, allowed and jwt). A key names a thing
    as an identifier does: a subscript (SETTINGS["X"]), a dict or object key,
    the name a lookup reads (.get("X"), getattr(obj, "x"),
    toHaveProperty("X")), and the names a setUp attribute or a describe-body
    const was read from. Words in a value the test compares against never
    count, and a URL in a comment is read without its scheme.

Whatever the declarations, it spares what its reading shows is no read-back:

  - a test that feeds inputs to logic: any call into the code under test, a
    pattern, a condition, an order of precedence or a computed value. An
    imported TypeScript or JavaScript name is code under test whatever it is
    called (an imported resolve() or router.match()); only a name from a Node
    built-in module (fs, path, url) or a global reads a value, and a string
    method reads a value only on a value already read or an imported constant
    written in upper case;
  - a test that reads a file a setup hook in its scope had code write: a
    unittest setUp, setUpClass or asyncSetUp, a pytest setup_* function, an
    autouse fixture in the file or in a conftest.py under the plant root, a
    beforeAll, beforeEach or before in the test's block or at the file's top.
    A setUp that only binds attributes to values it reads, and a const a
    describe body only reads, are reads like a module-level constant; a call
    into code in either, a let, or a base class the check cannot see keeps
    them logic;
  - a negative control: an assertion that a named value is absent or refused
    (`"/admin" not in nav`, `.not.toContain("/admin")`, an expected exception);
  - a test whose only assertions are guards: a value is set or not empty
    (`!= ""`, `is not None`, a bare `assert x`, toBeTruthy, toBeDefined,
    toBeFalsy, toBeNull, assertIsNone, assertFalse(x)). A guard beside a
    read-back spares nothing, and a False, None, false or null literal compared
    for equality (`is False`, toBe(false)) is a read-back like any other;
  - a test with no assertion it can read.

What it does not judge. A test that calls a helper in its file that asserts, a
test that compares with a golden file (a path under a golden, snapshots or
expected directory, or a .snap or .golden file), and a test that compares with
a snapshot (toMatchSnapshot, a snapshot fixture) are listed as
`path::name  not judged (<kind>)`: the assertion is out of the check's sight,
so it neither flags nor spares them. They count with the not checked.

It never flags by a test's name or length, and it never removes or edits a
test.

Every other test file is listed as `not checked (<language>)`, and a file that
does not parse is `not checked` with the reason: an unread file is never
reported as passing. A parametrized test (pytest parametrize, test.each,
it.each) is read with each parameter taking the literal values of its table;
one whose table is not written as literals (a computed table, a tagged
template, object rows) is listed as `path::name  not checked (parametrized)`,
and a test whose title is computed as `path::line N  not checked (computed
title)`. The summary reads `K files read, U not checked (languages: ...;
parametrized: N test(s); not judged: M test(s))`, U counting the unread files,
the unread tests and the tests not judged. A plant whose spec-lint.py is
missing or sets no TEST_GLOBS gets one line saying the check is not
configured, and exit 0.

The trust paths get one line each run: the plant marks none; consulted, with
how many files and test files; consulted in part, when the source index
answers incomplete (the word list then still applies); or
`trust paths not consulted: <reason>`, when the source index or graph-lint.py
is missing, older, or does not answer. A plant that cannot be consulted reads
as one that marks no trust path: nothing is spared for a trust path, and the
word list applies.

Known limits. These read-backs are spared, since a miss costs nothing and a
false flag costs an author a test: a fixture parameter's value; a test inside
describe.each, whose parameters read as logic; a key that names a security
subject for an unrelated reason (ROUTES["/login"]); a read-back under any
header-shaped key (a plain HEADERS["Content-Type"] check); a setUp or describe
body that runs any code beside a read; a test on a trust path or with a
sparing §10 origin that reads back a literal anyway.
Two limits can flag a good test. A setup file named only in the runner's
configuration (jest globalSetup, vitest setupFiles) is not read, so a file it
builds reads as a literal; keep such a test with a keep line naming the setup
file. And in a plant that marks trust paths, a security test off them that no
§10 row maps is judged by its reading alone: record its §10 row with origin
`security control`, or keep it with a keep line and its reason.

Keep a test that earns its place with a comment line directly above it (any
comment syntax), for example:

    # worth-check: keep — the label is a contract with the mobile client

The report prints each kept test with its reason. A keep line without a reason
keeps nothing.

The baseline is the plant's file docs/graph/worth-baseline.txt, tracked in
Git, one `path::name` per line: the tests flagged on the day it was recorded,
for a project adopted with an existing suite. A flagged test in the baseline
is reported and does not fail; a baseline entry that no longer flags is
reported as shrinkable, and an entry not read or not judged stays as it was.
--write-baseline records today's flags; the first write is free, and every
later write may only shrink the file, so it refuses to add a test. No baseline
file is an empty baseline.

--removal-list prints the flagged tests as one numbered batch for the owner's
confirmation: each test, why it is flagged, its §10 row and origin read from
docs/graph/specs/, and the contract it would leave without evidence. A test
whose §10 origin is bug or security control is spared, so it never reaches the
batch; a test in a legacy row with no origin, and a test no §10 row maps, print
NOT REMOVABLE AUTOMATICALLY. --spec SPEC-NNNN narrows the batch to the tests
that spec's §10 maps, its baseline tests included: the listing a reopened spec
owes. The list is read-only and exits 0; a test leaves the suite only when the
owner names it in the chat (protocol.test-first, Removing a test that catches
nothing).

In the gate: a newly written test the check flags fails the plant's gate
unless it is kept. The failing line names the remedies: keep the test with a
reason, or strengthen it so it feeds inputs to the logic it guards; a test on a
trust path, of §10 origin bug, or a security control is never removed to clear
a flag. A plant puts the check in its verification runbook
(docs/graph/runbooks/verification.md) as the gate row
`python3 docs/graph/worth-check.py`, expected exit 0, once TEST_GLOBS names
its test layout (grow.gate.spec-wired); until then the row prints the
not-configured line and passes.

Exit codes: 0 nothing new is flagged, or the plant is not configured;
1 a flagged test is neither kept nor in the baseline, or --write-baseline was
refused; 2 a usage error or an input it cannot read (the path and the reason
are named). A trust path the check cannot consult changes no exit code.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import subprocess
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
# The regression and security spares read what the author declared about the
# test: its name or title, its decorators or markers, the comments above and
# inside it, its docstring and (security only) the identifiers it reads. They
# never read the words inside a string literal, so a URL, a colour code or a
# line of banner copy spares nothing.
# A declaration naming a bug spares the test (ADR-0034: a bug reproduction is
# always written and stays).
REGRESSION_RE = re.compile(r"\b(?:regress\w*|bugs?|issues?|reproduc\w*|hotfix\w*|incidents?)\b", re.I)
TICKET_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
# `#412` names an issue, except on a line about a colour, where `#112233` is a
# colour code; a token with hex letters (`#0055ff`) never matches.
ISSUE_REF_RE = re.compile(r"(?<![\w#&])#\d+\b")
COLOUR_RE = re.compile(r"\b(?:colou?rs?|hex|rgba?|palette|css)\b", re.I)
URL_RE = re.compile(r"\b[a-z][a-z0-9+.-]*://\S*", re.I)
# Words that make a test a security control. `debug` is here because a debug
# mode left on in production leaks internals; `cookie` is not, because banner
# copy names cookies (a session cookie names its session).
SECURITY_RE = re.compile(
    r"\b(?:secur\w*|auth\w*|csrf|xsrf|xss|inject\w*|travers\w*|secrets?|passw\w*|tokens?|"
    r"permission\w*|forbid\w*|denied|deny|sanitiz\w*|escap\w*|privileg\w*|csp|cors|tls|ssl|"
    r"https|session\w*|admin\w*|login|logout|credential\w*|encrypt\w*|decrypt\w*|debug|"
    r"nonce|unsafe|untrusted|malicious|attack\w*|exploit\w*|hsts|"
    # A stopgap the owner decided on 2026-11-11 for settings named for their
    # effect; the declarations (a §10 origin, a marked trust path) come first.
    r"roles?|lockouts?|origins?|allowed|jwts?|"
    # The standard security response headers, as an identifier names one once
    # words() has split it: X_FRAME_OPTIONS, xContentTypeOptions, referrerPolicy.
    r"x[\s-]*frame[\s-]*options|x[\s-]*content[\s-]*type[\s-]*options|"
    r"strict[\s-]*transport\w*|referrer[\s-]*policy|permissions?[\s-]*policy|"
    r"cross[\s-]*origin[\s-]*(?:opener|embedder|resource)[\s-]*policy|"
    r"frame[\s-]*ancestors|x[\s-]*xss[\s-]*protection)\b", re.I)
# A string key shaped like an HTTP header name (capitalised words joined by
# hyphens: X-Frame-Options, Cache-Control, Strict-Transport-Security) declares
# a security control by its shape, so no word list has to name every header.
# It is deliberately broad: a plain Content-Type read-back is spared with it,
# since a missed flag costs nothing and a flagged security test costs a gate.
# Only a key counts; a header name used as a compared value is content.
HEADER_KEY_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$")
# A string used as a key names a thing, as an identifier does, so the security
# spare reads it: a subscript (`SETTINGS["SESSION_COOKIE_SECURE"]`), a dict or
# object key, and the first argument of a lookup by name. A string compared
# against is content and never counts. In Python the name is the second
# argument of getattr and hasattr.
PY_KEY_METHODS = {"get", "getenv", "setdefault", "pop", "getlist", "get_all"}
PY_KEY_FUNCS = {"getattr", "hasattr"}
JS_KEY_METHODS = {"get", "getItem", "has", "getHeader", "getAttribute", "header",
                  "hasOwnProperty", "toHaveProperty"}
# What the check cannot see is reported `not judged`, never spared or flagged:
# a golden file (a path with a golden, snapshots or expected directory, or a
# .snap or .golden file), and a snapshot fixture by its conventional names.
GOLDEN_PATH_RE = re.compile(r"(?:^|[/\\])(?:goldens?|snapshots?|__snapshots__|approved|expected)[/\\]"
                            r"|[._-](?:golden|snap|snapshot|approved|expected)\.\w+$|\.(?:snap|golden)$",
                            re.I)
SNAPSHOT_PARAM_RE = re.compile(r"^(?:snapshot\w*|\w+_snapshot|snap|golden\w*|\w+_regression)$")
# The declarations the plant makes: its specs' §10 rows (an origin of bug or
# security control spares the test) and its trust paths (a `kind: crosscut`
# node marked `trust: true`, whose claims graph-lint.py answers and whose
# reach source-index.py answers).
SPARING_ORIGINS = {"bug": "a bug reproduction stays", "security control": "a security control stays"}
NODES = "docs/graph/nodes"
SOURCE_INDEX = "docs/graph/source-index.py"
GRAPH_LINT = "docs/graph/graph-lint.py"
TRUST_TIMEOUT = 300                  # seconds per call to a plant tool
CLAIMS_CHUNK = 1000                  # paths per graph-lint.py --trust-claims call
NO_INVENTORY = {"git-unavailable", "no-repository"}
# Setup hooks: a hook that runs code makes a file the test then reads output of
# that code, not a literal the change adds.
PY_HOOKS = {"setUp", "setUpClass", "asyncSetUp", "setup_method", "setup_class", "setup",
            "setup_function", "setup_module", "setUpModule", "pytest_sessionstart"}
PY_FILE_READS = {"read_text", "read_bytes", "open"}
PY_TESTCASE_BASES = {"object", "TestCase", "unittest.TestCase", "IsolatedAsyncioTestCase",
                     "unittest.IsolatedAsyncioTestCase"}
JS_HOOKS = {"beforeAll", "beforeEach", "before"}
JS_FILE_READS = {"readFileSync", "readFile"}
# A str method over literals with literal arguments is folded into a literal.
FOLD_STR_METHODS = {"join", "upper", "lower", "strip", "lstrip", "rstrip", "replace", "format",
                    "casefold", "title", "capitalize"}

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
PY_NEGATIVE = {"assertNotEqual", "assertNotEquals", "assertNotIn", "assertIsNot", "assertNotRegex",
               "assertNotAlmostEqual"}
PY_GUARDS = {"assertIsNone", "assertIsNotNone"}

# TypeScript and JavaScript. A read call counts as a read only when its root
# is a global, an assertion, or a name imported or required from a Node
# built-in module; an imported name from anywhere else is code under test.
JS_READ_CALLS = {"readFileSync", "fs.readFileSync", "fs.promises.readFile", "promises.readFile",
                 "fsp.readFile", "readFile", "path.join", "path.resolve", "path.dirname", "join",
                 "resolve", "dirname", "fileURLToPath", "url.fileURLToPath", "JSON.parse",
                 "String", "URL", "require", "expect", "assert"}
JS_ALWAYS_READ = {"expect", "assert", "JSON", "String", "URL", "require"}
NODE_BUILTINS = {"fs", "node:fs", "fs/promises", "node:fs/promises", "path", "node:path",
                 "path/posix", "node:path/posix", "url", "node:url"}
JS_READ_METHODS = {"toString", "trim", "trimStart", "trimEnd", "split", "toLowerCase",
                   "toUpperCase", "includes", "startsWith", "endsWith", "indexOf", "match", "join"}
CONST_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]*")
JS_POSITIVE = {"toBe", "toEqual", "toStrictEqual", "toContain", "toMatch", "toContainEqual",
               "toHaveLength", "toMatchObject", "toHaveProperty", "toBeCloseTo",
               "toMatchInlineSnapshot"}
JS_SNAPSHOT_FILE = {"toMatchSnapshot", "toMatchFileSnapshot"}
JS_NO_LITERAL = {"toBeTruthy", "toBeDefined"}
JS_NEGATIVE = {"toBeFalsy", "toBeNull", "toBeUndefined", "toBeNaN"}
JS_TEST_MODIFIERS = {"only", "concurrent", "each", "fails", "sequential"}
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


def names_a_bug(declared: str) -> bool:
    """A name, title, marker, comment or docstring that names a bug, an issue,
    a regression or a ticket. A bare `#<digits>` counts on a line that is not
    about a colour."""
    for line in declared.splitlines():
        if REGRESSION_RE.search(line) or TICKET_RE.search(line):
            return True
        if ISSUE_REF_RE.search(line) and not COLOUR_RE.search(line):
            return True
    return False


def py_keys(nodes) -> list[str]:
    """The strings the given statements use as keys: a subscript, a dict key,
    the name a lookup reads (`.get("X")`, `getattr(obj, "x")`)."""
    out = []

    def text(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    for st in nodes:
        for n in ast.walk(st):
            if isinstance(n, ast.Subscript):
                text(n.slice)
            elif isinstance(n, ast.Dict):
                for k in n.keys:
                    text(k)
            elif isinstance(n, ast.Call) and n.args:
                if isinstance(n.func, ast.Attribute) and n.func.attr in PY_KEY_METHODS:
                    text(n.args[0])
                elif isinstance(n.func, ast.Name) and n.func.id in PY_KEY_FUNCS and len(n.args) > 1:
                    text(n.args[1])
    return out


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


class NoFold(Exception):
    """An expression that is not a constant built from literals."""


class NotReadable(Exception):
    """A parametrize table the check cannot read as literals."""


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


def substantive(value) -> bool:
    """A literal that names something: not empty, zero, None or False."""
    if value is None or value is False or isinstance(value, (list, tuple, dict, set)) and not value:
        return False
    return not (isinstance(value, (int, float, str, bytes)) and not value)


class PyTest:
    """One Python test function, read statement by statement. `params` maps a
    parametrized argument to the literal values its table gives it; `hooked`
    says a setup hook in scope runs code, so a file the test reads is output of
    that code."""

    def __init__(self, fn, module_env: dict, params: dict | None = None, hooked: bool = False,
                 attrs: dict | None = None, helpers=frozenset(), methods=frozenset(),
                 golden=frozenset()):
        self.module_env = module_env
        self.attrs: dict = dict(attrs or {})      # self.<attr> a setUp that only reads bound
        self.receiver = None
        self.env: dict = {}
        self.params: dict = dict(params or {})
        self.values: dict = {}                    # a local bound to a folded literal
        self.hooked = hooked
        self.logic = False
        self.assertions: list[tuple[str, list]] = []   # (status, literal nodes)
        # What the check cannot see: a helper in the file that asserts, a
        # golden file, a snapshot fixture. A test that reaches one is not judged.
        self.helpers, self.methods, self.golden = helpers, methods, golden
        self.snapshots: set = set()
        self.helper_called = False
        self.first = None
        if fn is None:
            return
        a = fn.args
        for arg in a.posonlyargs + a.args + a.kwonlyargs + [x for x in (a.vararg, a.kwarg) if x]:
            if arg.arg in self.params:
                self.env[arg.arg] = LIT
            elif SNAPSHOT_PARAM_RE.match(arg.arg):
                self.env[arg.arg] = READ
                self.snapshots.add(arg.arg)
            else:
                self.env[arg.arg] = LOGIC
        if a.posonlyargs + a.args:
            self.first = (a.posonlyargs + a.args)[0].arg
        if self.attrs and (a.posonlyargs + a.args):
            self.receiver = (a.posonlyargs + a.args)[0].arg
        self.block(fn.body, top=True)

    def unseen(self, nodes) -> str | None:
        """`snapshot` or `golden` when an operand reaches a snapshot fixture or
        a golden file, which the check does not open."""
        for n in nodes:
            for x in ast.walk(n):
                if isinstance(x, ast.Name) and x.id in self.snapshots:
                    return "snapshot"
        for n in nodes:
            for x in ast.walk(n):
                if isinstance(x, ast.Name) and x.id in self.golden and x.id not in self.env:
                    return "golden"
                if isinstance(x, ast.Constant) and isinstance(x.value, str) and GOLDEN_PATH_RE.search(x.value):
                    return "golden"
        return None

    def snapshot_call(self, e) -> bool:
        """A method call on a snapshot fixture (`snapshot.assert_match(x)`,
        `data_regression.check(x)`)."""
        return isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute) \
            and (dotted(e.func) or "").split(".")[0] in self.snapshots

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
            if isinstance(e.value, ast.Name) and e.value.id == self.receiver \
                    and self.env.get(e.value.id) == LOGIC and e.attr in self.attrs:
                return self.attrs[e.attr][0]
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
            if f.id in self.helpers and f.id not in self.env:
                self.helper_called = True           # its assertion is out of sight
                return READ
            if self.hooked and f.id == "open":
                return LOGIC
            return READ if f.id in PY_READ_FUNCS and f.id not in self.env else LOGIC
        if isinstance(f, ast.Attribute):
            if isinstance(f.value, ast.Name) and f.value.id == self.first and f.attr in self.methods:
                self.helper_called = True
                return READ
            name = dotted(f)
            if self.hooked and (name in ("io.open", "codecs.open") or f.attr in PY_FILE_READS):
                return LOGIC
            if name in PY_READ_DOTTED:
                return READ
            if name in PY_RE_FUNCS:
                first = e.args[0] if e.args else None
                return READ if isinstance(first, ast.Constant) else LOGIC
            base = self.ev(f.value)
            if f.attr in FOLD_STR_METHODS and base == LIT and args == LIT:
                return LIT                          # "".join(["Se", "nd"]) is a literal
            if f.attr in PY_READ_METHODS and base in (READ, LIT):
                return READ
        return LOGIC

    def fold(self, e):
        """The value of a constant built from literals; NoFold otherwise."""
        if isinstance(e, ast.Constant):
            return e.value
        if isinstance(e, ast.Name) and e.id in self.values:
            return self.values[e.id]
        if isinstance(e, (ast.List, ast.Tuple)):
            return [self.fold(x) for x in e.elts]
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Add, ast.Mult)):
            left, right = self.fold(e.left), self.fold(e.right)
            try:
                return left + right if isinstance(e.op, ast.Add) else left * right
            except (TypeError, OverflowError, MemoryError):
                raise NoFold from None
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute) \
                and e.func.attr in FOLD_STR_METHODS and not e.keywords:
            base = self.fold(e.func.value)
            if isinstance(base, str):
                try:
                    return getattr(base, e.func.attr)(*[self.fold(a) for a in e.args])
                except (TypeError, ValueError, IndexError, KeyError):
                    raise NoFold from None
        raise NoFold

    def shown(self, nodes) -> list:
        """The literals an assertion reads back: a parametrized argument shows
        the values of its table, and a constant built from literals shows the
        one literal it folds into."""
        out = []
        for n in nodes:
            if isinstance(n, ast.Name) and n.id in self.params:
                out += [ast.Constant(v) for v in self.params[n.id]]
                continue
            try:
                v = self.fold(n)
            except (NoFold, RecursionError):
                out.append(n)
                continue
            out.append(n if isinstance(n, ast.Constant) else ast.Constant(v))
        return out

    def bind(self, target, kind: str, value=None) -> None:
        if isinstance(target, ast.Name):
            self.env[target.id] = kind
            self.values.pop(target.id, None)
            self.params.pop(target.id, None)
            if kind == LIT and value is not None:
                try:
                    self.values[target.id] = self.fold(value)
                except (NoFold, RecursionError):
                    pass
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
            if self.snapshot_call(st.value):
                args = [self.ev(a) for a in st.value.args] + [self.ev(k.value) for k in st.value.keywords]
                self.assertions.append((LOGIC, []) if LOGIC in args else ("snapshot", []))
                return
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
            if isinstance(st, ast.AugAssign):
                self.bind(st.target, k)
                return
            for t in (st.targets if isinstance(st, ast.Assign) else [st.target]):
                self.bind(t, k, st.value)
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
        elif attr == "assertFalse" and e.args:
            self.assertions.append(self.judge(ast.UnaryOp(op=ast.Not(), operand=e.args[0])))
        elif attr in PY_GUARDS and e.args:
            self.assertions.append((LOGIC, []) if self.ev(e.args[0]) == LOGIC else ("guard", []))
        elif attr in PY_NEGATIVE:
            self.assertions.append(self.operands(e.args[:2], negative=True))
        elif attr in PY_POSITIVE:
            self.assertions.append(self.operands(e.args[:2], negative=False))
        else:
            self.assertions.append((LOGIC, []))
        return True

    def operands(self, nodes, negative: bool):
        """An assertion's status from its operands. With negative polarity it
        is a negative control when it names a value that must be absent, and a
        guard, which spares nothing, when that value is empty, zero, None or
        False. A False or None literal compared for equality is a literal like
        any other."""
        kinds = [self.ev(n) for n in nodes]
        if LOGIC in kinds:
            return LOGIC, []
        lits = [n for n, k in zip(nodes, kinds) if k == LIT]
        if negative:
            return ("negative", []) if self.names_a_value(lits) else ("guard", [])
        unseen = self.unseen(nodes)
        if unseen == "snapshot":
            return "snapshot", []
        if lits and any(k in (READ, DECL) for k in kinds):
            return "readback", self.shown(lits)
        return (unseen, []) if unseen else ("no literal", [])

    def names_a_value(self, nodes) -> bool:
        for n in nodes:
            if isinstance(n, ast.Name) and n.id in self.params:
                if any(substantive(v) for v in self.params[n.id]):
                    return True
            elif isinstance(n, ast.Name) and n.id in self.values:
                if substantive(self.values[n.id]):
                    return True
            elif any(isinstance(c, ast.Constant) and substantive(c.value) for c in ast.walk(n)):
                return True
        return False

    def judge(self, e):
        if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.Not):
            if self.ev(e.operand) == LOGIC:
                return LOGIC, []
            return ("negative", []) if self.names_a_value([e.operand]) else ("guard", [])
        if isinstance(e, ast.Compare):
            neg = any(isinstance(op, (ast.NotEq, ast.NotIn, ast.IsNot)) for op in e.ops)
            return self.operands([e.left] + e.comparators, negative=neg)
        if isinstance(e, ast.BoolOp):
            parts = [self.judge(v) for v in e.values]
            for status in (LOGIC, "negative", "no literal"):
                if any(p[0] == status for p in parts):
                    return status, []
            if any(p[0] == "readback" for p in parts):
                return "readback", [n for p in parts for n in p[1]]
            return "guard", []
        k = self.ev(e)
        if k == LOGIC:
            return LOGIC, []
        if isinstance(e, ast.Call) and k == READ:
            lits = [a for a in e.args if isinstance(a, ast.Constant)]
            if lits:
                return "readback", self.shown(lits)
        if isinstance(e, (ast.Name, ast.Attribute, ast.Subscript)):
            return "guard", []                      # the truthiness of a value read back
        return "no literal", []


def py_literal(node) -> str:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return json.dumps(node.value, ensure_ascii=False)
        return repr(node.value)
    return ast.unparse(node)


def py_module_env(tree) -> dict:
    env: dict = {}
    probe = PyTest(None, env)
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


def setup_reads(cls, env: dict, hooked: bool) -> dict:
    """attr -> (kind, the identifiers and keys it was built from) for each
    `self.<attr> = <value>` of a setup method in the class, when every setup
    method only binds attributes to values it reads (a constant, a config
    entry, a file read with no hook in scope that runs code), the class has
    only bases the check knows, and no other method of the class stores the
    attribute. Anything else binds nothing, so the attribute stays logic."""
    if any((dotted(b) or "") not in PY_TESTCASE_BASES for b in cls.bases):
        return {}
    hooks = [m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
             and m.name in PY_HOOKS]
    out: dict = {}
    for h in hooks:
        a = h.args.posonlyargs + h.args.args
        if not a:
            return {}
        recv = a[0].arg
        probe = PyTest(None, env, hooked=hooked)
        probe.env[recv] = LOGIC
        for i, st in enumerate(h.body):
            if isinstance(st, ast.Pass) or (i == 0 and isinstance(st, ast.Expr)
                                            and isinstance(st.value, ast.Constant)):
                continue
            t = st.targets[0] if isinstance(st, ast.Assign) and len(st.targets) == 1 else None
            if not (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                    and t.value.id == recv):
                return {}
            kind = probe.ev(st.value)
            if kind == LOGIC:
                return {}
            ids = [n.id for n in ast.walk(st.value) if isinstance(n, ast.Name)] \
                + [n.attr for n in ast.walk(st.value) if isinstance(n, ast.Attribute)]
            out[t.attr] = (kind, " ".join(words(x) for x in ids + py_keys([st.value])))
    for m in cls.body:
        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m not in hooks:
            for n in ast.walk(m):
                if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                    out.pop(n.attr, None)
    return out


def is_autouse(fn) -> bool:
    for d in fn.decorator_list:
        if isinstance(d, ast.Call) and (dotted(d.func) or "").split(".")[-1] == "fixture" and any(
                k.arg == "autouse" and isinstance(k.value, ast.Constant) and k.value.value
                for k in d.keywords):
            return True
    return False


def runs_code(fn, env: dict) -> bool:
    """A hook body that calls anything but a read: a build, a write, a client."""
    probe = PyTest(None, env)
    a = fn.args
    for arg in a.posonlyargs + a.args + a.kwonlyargs:
        probe.env[arg.arg] = LOGIC
    return any(isinstance(node, ast.Call) and probe.call(node) == LOGIC
               for st in fn.body for node in ast.walk(st))


def hooks_run_code(body, env: dict) -> bool:
    """A setup hook among one scope's statements, an autouse fixture included,
    that runs code."""
    return any(isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))
               and (st.name in PY_HOOKS or is_autouse(st)) and runs_code(st, env) for st in body)


_CONFTEST: dict = {}


def conftest_hooked(root: Path | None, rel: str) -> bool:
    """A conftest.py between the plant root and the test file holds an autouse
    fixture or a session hook that runs code."""
    if root is None:
        return False
    d = Path(rel).parent
    while True:
        p = root / d / "conftest.py"
        if p not in _CONFTEST:
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
                _CONFTEST[p] = hooks_run_code(tree.body, py_module_env(tree))
            except (OSError, SyntaxError, ValueError, UnicodeDecodeError, RecursionError):
                _CONFTEST[p] = False
        if _CONFTEST[p]:
            return True
        if d == d.parent:
            return False
        d = d.parent


def py_parametrize(decorators) -> dict:
    """Each parametrized argument -> the literal values its table gives it.
    An indirect table feeds fixtures, which stay logic; a table that is not
    written as literals raises NotReadable."""
    out: dict = {}
    for d in decorators:
        if not (isinstance(d, ast.Call) and (dotted(d.func) or "").endswith("parametrize")):
            continue
        kw = {k.arg: k.value for k in d.keywords}
        if "indirect" in kw:
            continue
        names_node = d.args[0] if d.args else kw.get("argnames")
        values_node = d.args[1] if len(d.args) > 1 else kw.get("argvalues")
        try:
            names = ast.literal_eval(names_node)
        except (ValueError, TypeError, SyntaxError, RecursionError):
            raise NotReadable from None
        names = [n.strip() for n in names.split(",")] if isinstance(names, str) else list(names)
        if not isinstance(values_node, (ast.List, ast.Tuple)) or not all(
                isinstance(n, str) for n in names):
            raise NotReadable
        rows = []
        for elt in values_node.elts:
            if isinstance(elt, ast.Call) and (dotted(elt.func) or "").endswith("param"):
                elt = elt.args[0] if len(elt.args) == 1 else ast.Tuple(elts=list(elt.args), ctx=ast.Load())
            try:
                row = ast.literal_eval(elt)
            except (ValueError, TypeError, SyntaxError, RecursionError):
                raise NotReadable from None
            if len(names) > 1:
                if not isinstance(row, (tuple, list)) or len(row) != len(names):
                    raise NotReadable
                rows.append(list(row))
            else:
                rows.append([row])
        for k, n in enumerate(names):
            out[n] = [r[k] for r in rows]
    return out


def mark_text(d) -> str:
    """A decorator as the declaration it makes: a parametrize table's values
    are data, so only its name counts."""
    name = dotted(d.func if isinstance(d, ast.Call) else d) or ""
    return name if name.endswith("parametrize") else ast.unparse(d)


def read_python(rel: str, src: str, root: Path | None = None):
    """(the tests read, the tests listed as not checked) of one Python file."""
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
    classes = {st.name: st for st in tree.body if isinstance(st, ast.ClassDef)}

    def class_hooked(cls, seen=()) -> bool:
        if hooks_run_code(cls.body, env):
            return True
        for b in cls.bases:
            name = dotted(b) or ""
            if name in classes and name not in seen:
                if class_hooked(classes[name], seen + (cls.name,)):
                    return True
            elif name not in PY_TESTCASE_BASES:
                return True                 # a base the check cannot see: its setUp may build
        return False

    module_hooked = hooks_run_code(tree.body, env) or conftest_hooked(root, rel)
    helpers = py_helpers(tree.body)
    golden = {t.id for st in tree.body if isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None
              and any(isinstance(c, ast.Constant) and isinstance(c.value, str) and GOLDEN_PATH_RE.search(c.value)
                      for c in ast.walk(st.value))
              for tg in (st.targets if isinstance(st, ast.Assign) else [st.target])
              for t in ast.walk(tg) if isinstance(t, ast.Name)}
    found = []
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name.startswith("test"):
            found.append((st.name, st, [], module_hooked, {}, frozenset()))
        elif isinstance(st, ast.ClassDef):
            hooked = module_hooked or class_hooked(st)
            attrs = setup_reads(st, env, hooked)
            methods = py_helpers(st.body)
            for m in st.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test"):
                    found.append((f"{st.name}::{m.name}", m, st.decorator_list, hooked, attrs, methods))
    out, unread = [], []
    for name, fn, outer, hooked, attrs, methods in found:
        decorators = list(outer) + fn.decorator_list
        try:
            params = py_parametrize(decorators)
        except NotReadable:
            unread.append({"path": f"{rel}::{name}", "reason": "parametrized", "language": "python"})
            continue
        first = min([fn.lineno] + [d.lineno for d in fn.decorator_list])
        last = fn.end_lineno or fn.lineno
        t = PyTest(fn, env, params, hooked, attrs, helpers=helpers, methods=methods, golden=golden)
        above = comments_above(lines, first, ("#",))
        inside = "\n".join(c for n, c in comments.items() if first <= n <= last)
        doc = ast.get_docstring(fn) or ""
        marks = "\n".join(mark_text(d) for d in decorators)
        ids = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)} \
            | {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)} \
            | {a.arg for a in ast.walk(fn.args) if isinstance(a, ast.arg)}
        # Keys name things as identifiers do, and an attribute a setUp bound
        # carries the names of what it was bound to.
        keys = py_keys(fn.body)
        named = sorted(ids) + keys + [attrs[n.attr][1] for n in ast.walk(fn)
                                                  if isinstance(n, ast.Attribute) and n.attr in attrs]
        declared = f"{above}\n{inside}\n{doc}\n{words(name)}\n{words(marks)}"
        kept, reason = keep_reason(lines, first, ("#",))
        out.append(verdict(rel, name, first, "python", t.logic, t.assertions,
                           declared=declared, security_text=declared + "\n" + " ".join(named),
                           keys=keys, helper=t.helper_called,
                           literal_of=py_literal, kept=kept, reason=reason))
    return out, unread


def py_helpers(body) -> frozenset:
    """The functions among one scope's statements that assert and are no test,
    fixture or setup hook: a test that calls one asserts out of sight."""
    out = set()
    for st in body:
        if not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) or st.name.startswith("test") \
                or st.name in PY_HOOKS or any((dotted(d.func if isinstance(d, ast.Call) else d) or "")
                                              .split(".")[-1] == "fixture" for d in st.decorator_list):
            continue
        for n in ast.walk(st):
            if isinstance(n, ast.Assert) or (isinstance(n, ast.Call) and (
                    (isinstance(n.func, ast.Attribute) and n.func.attr.startswith("assert"))
                    or (isinstance(n.func, ast.Name) and n.func.id.startswith("assert")))):
                out.add(st.name)
                break
    return frozenset(out)


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
        self.origin: dict = {}       # an imported or required name -> its module
        self.bound: dict = {}        # a name -> the literal tokens it stands for, in one test
        self.hooked = False          # a setup hook in scope of the test being read runs code
        self.scoped: dict = {}       # a const an enclosing block only reads -> the names it read
        self.blocked: set = set()    # a name an enclosing block declares any other way
        self.parent: list[int] = []  # each token's innermost enclosing "{", or -1
        self.close: dict = {}        # an opening "{" -> its closing "}"
        self.helpers: set = set()    # a top-level function that asserts: its assertion is out of sight
        self.golden: set = set()     # a top-level name whose value names a golden file
        self.helper_called = False
        stack: list[int] = []
        for k, t in enumerate(self.toks):
            self.parent.append(stack[-1] if stack else -1)
            if t.kind == "punc" and t.value == "{":
                stack.append(k)
            elif t.kind == "punc" and t.value == "}" and stack:
                self.close[stack.pop()] = k
        self.module_scan()

    def read_value(self, root: str, local: set) -> bool:
        """A value already read: a local, a top-level value read in this file,
        or an imported constant written in upper case. Any other imported name
        is code under test, so a method on it is a call into that code."""
        if root in local or self.top.get(root) == READ:
            return True
        return self.top.get(root) == DECL and bool(CONST_NAME_RE.fullmatch(root))

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
                chain.append(")")               # a method on a call's result or a literal
                break
        chain.reverse()
        name = ".".join(chain)
        if self.hooked and chain[-1] in JS_FILE_READS:
            return LOGIC                         # output of the code a setup hook ran
        if chain[0] == ")":
            if chain[-1] in JS_READ_METHODS or chain[-1].startswith("to") or chain[-1] == "not":
                return READ
            return LOGIC
        root = chain[0]
        if root in params:
            return LOGIC
        if name in JS_READ_CALLS or (root == "assert" and len(chain) == 2):
            if root in JS_ALWAYS_READ or self.origin.get(root) in NODE_BUILTINS or (
                    root not in self.top and root not in local):
                return READ
            return LOGIC                         # an imported resolve() is code under test
        if len(chain) > 1 and chain[-1] in JS_READ_METHODS and self.read_value(root, local):
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
                j, names = i + 1, []
                while j < len(toks) and not (toks[j].kind in ("str",) or toks[j].value in ("from", ";")):
                    if toks[j].kind == "id" and toks[j].value not in ("type", "as"):
                        names.append(toks[j].value)
                    j += 1
                source = toks[j + 1].value if j + 1 < len(toks) and toks[j].value == "from" \
                    and toks[j + 1].kind == "str" else None
                for nm in names:
                    self.top[nm] = DECL
                    if source is not None:
                        self.origin[nm] = source
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
                    if self.asserts(rhs) and any(r.value in ("=>", "function") for r in rhs):
                        self.helpers.update(names)
                    if any(r.kind in ("str", "tmpl") and GOLDEN_PATH_RE.search(r.value) for r in rhs):
                        self.golden.update(names)
                    kind = READ
                    for r, nxt in zip(rhs, rhs[2:]):
                        if r.kind == "id" and r.value == "require" and nxt.kind == "str":
                            kind = DECL
                            for nm in names:
                                self.origin[nm] = nxt.value
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
                b = next((k for k in range(i + 2, len(toks)) if toks[k].kind == "punc" and toks[k].value == "{"),
                         None)
                if t.value == "function" and b is not None and self.asserts(toks[b + 1:self.close.get(b, b)]):
                    self.helpers.add(toks[i + 1].value)
            i += 1

    @staticmethod
    def asserts(toks: list[Tok]) -> bool:
        """The tokens call expect( or assert, as a helper's body does."""
        return any(t.kind == "id" and t.value in ("expect", "assert") and k + 1 < len(toks)
                   and toks[k + 1].value in ("(", ".") and not (k and toks[k - 1].value in (".", "?."))
                   for k, t in enumerate(toks))

    @staticmethod
    def is_fn(arg: list[Tok]) -> bool:
        """A function literal: `function`, or an arrow at the argument's top level."""
        k = 1 if arg and arg[0].value == "async" else 0
        if k < len(arg) and arg[k].kind == "id" and arg[k].value == "function":
            return True
        depth = 0
        for t in arg:
            if t.kind == "punc" and t.value in ("(", "[", "{"):
                depth += 1
            elif t.kind == "punc" and t.value in (")", "]", "}"):
                depth -= 1
            elif depth == 0 and t.kind == "punc" and t.value == "=>":
                return True
        return False

    @staticmethod
    def fn_parts(fn: list[Tok]):
        """(parameter names in order, or None when one is destructured; the
        parameter name set; the body tokens) of a function literal."""
        order: list | None = []
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
            for part in split_args(fn[k + 1:end]):
                if not part or part[0].kind != "id":
                    order = None
                elif order is not None:
                    order.append(part[0].value)
            k = end + 1
        elif k < len(fn) and fn[k].kind == "id":
            params, order = {fn[k].value}, [fn[k].value]
            k += 1
        if k < len(fn) and fn[k].value == "=>":
            k += 1
        if k < len(fn) and fn[k].value == "{":
            end = matching(fn, k, "{", "}")
            return order, params, fn[k + 1:end]
        return order, params, fn[k:]

    def hook_scopes(self) -> list[tuple[int, int]]:
        """The token span each setup hook that runs code applies to: its
        enclosing block, or the whole file for a hook at the top."""
        toks, spans = self.toks, []
        for i, t in enumerate(toks):
            if t.kind != "id" or t.value not in JS_HOOKS or i + 1 >= len(toks) \
                    or toks[i + 1].value != "(":
                continue
            if i >= 2 and toks[i - 1].value in (".", "?.") and toks[i - 2].value not in ("test", "it"):
                continue
            close = matching(toks, i + 1, "(", ")")
            fn = next((a for a in reversed(split_args(toks[i + 2:close])) if self.is_fn(a)), None)
            if fn is None:
                continue
            _, params, body = self.fn_parts(fn)
            logic, _ = self.read_body(body, params)
            if logic:
                p = self.parent[i]
                spans.append((0, len(toks)) if p < 0 else (p, self.close.get(p, len(toks))))
        self.bound = {}
        return spans

    def tests(self):
        """(the tests read, the tests listed as not checked)."""
        toks, out, unread = self.toks, [], []
        scopes = self.hook_scopes()
        for i, t in enumerate(toks):
            if t.kind != "id" or t.value not in ("test", "it"):
                continue
            if i and toks[i - 1].kind == "punc" and toks[i - 1].value in (".", "?."):
                continue
            j, mods = i + 1, []
            while j + 1 < len(toks) and toks[j].value == "." and toks[j + 1].kind == "id":
                mods.append(toks[j + 1].value)
                j += 2
            if not set(mods) <= JS_TEST_MODIFIERS:
                continue                          # test.skip, test.describe, test.beforeAll ...
            table = None
            if "each" in mods:
                if j < len(toks) and toks[j].kind == "tmpl":
                    table, j = "tagged", j + 1
                elif j < len(toks) and toks[j].value == "(":
                    end = matching(toks, j, "(", ")")
                    table, j = toks[j + 1:end], end + 1
                else:
                    continue
            if j >= len(toks) or toks[j].value != "(" or toks[j].kind != "punc":
                continue
            close = matching(toks, j, "(", ")")
            args = split_args(toks[j + 1:close])
            fn = next((a for a in args[1:] if self.is_fn(a)), None)
            if len(args) < 2 or fn is None:
                continue
            titled = len(args[0]) == 1 and args[0][0].kind in ("str", "tmpl") and not args[0][0].subst
            if not titled:
                unread.append({"path": f"{self.rel}::line {t.line}", "reason": "computed title",
                               "language": self.lang})
                continue
            title = args[0][0].value
            bound = {}
            if table is not None:
                order, _, _ = self.fn_parts(fn)
                bound = js_each_table(table, order)
                if bound is None:
                    unread.append({"path": f"{self.rel}::{title}", "reason": "parametrized",
                                   "language": self.lang})
                    continue
            self.hooked = any(a < i < b for a, b in scopes)
            try:
                self.scoped, self.blocked = self.enclosing_reads(i)
                out.append(self.one(title, t.line, fn, bound))
            finally:
                self.hooked, self.bound, self.scoped, self.blocked = False, {}, {}, set()
        return out, unread

    def block_params(self, b: int) -> set:
        """The parameter names of the function whose body opens at toks[b]."""
        toks = self.toks
        k = b - 1
        if k >= 0 and toks[k].value == "=>":
            k -= 1
            if k >= 0 and toks[k].kind == "id":
                return {toks[k].value}
        if k >= 0 and toks[k].kind == "punc" and toks[k].value == ")":
            depth, j = 0, k
            while j >= 0:
                if toks[j].kind == "punc" and toks[j].value == ")":
                    depth += 1
                elif toks[j].kind == "punc" and toks[j].value == "(":
                    depth -= 1
                    if depth == 0:
                        return {x.value for x in toks[j + 1:k] if x.kind == "id"}
                j -= 1
        return set()

    def reads_only(self, rhs: list[Tok]) -> bool:
        """An initializer that only reads: calls that read (a Node built-in, a
        global, a string method on a value read), names declared or read at
        the top of the file. A container literal, a function, `new`, `await`,
        `this` or a template with a hole is not."""
        if not rhs or (rhs[0].kind == "punc" and rhs[0].value in ("{", "[")):
            return False
        for k, t in enumerate(rhs):
            if (t.kind == "tmpl" and t.subst) or (t.kind == "punc" and t.value == "=>") or (
                    t.kind == "id" and t.value in ("function", "class", "this", "new", "await",
                                                   "yield")):
                return False
            if t.kind == "punc" and t.value == "(" and k:
                p = rhs[k - 1]
                if p.kind == "id" and p.value not in JS_KEYWORDS:
                    if self.call_kind(rhs, k, set(), set()) != READ:
                        return False
                elif p.kind == "punc" and p.value in (")", "]"):
                    return False
            elif t.kind == "id" and t.value not in JS_KEYWORDS | JS_LITERAL_WORDS | JS_GLOBALS:
                prop = k and rhs[k - 1].kind == "punc" and rhs[k - 1].value in (".", "?.")
                if not prop and self.top.get(t.value) not in (READ, DECL):
                    return False
        return True

    def enclosing_reads(self, i: int) -> tuple[dict, set]:
        """For the test opening at toks[i]: each `const NAME = <value>` an
        enclosing block (a describe body) declares and only reads -> the names
        and keys it read; and every other name an enclosing block declares (a
        let, a var, a destructured or typed const, a parameter), which stays
        logic. The innermost declaration of a name wins."""
        toks, scoped, blocked = self.toks, {}, set()
        p = self.parent[i]
        while p >= 0:
            end = self.close.get(p, len(toks))
            here: set = set(self.block_params(p))
            for k in range(p + 1, end):
                t = toks[k]
                if self.parent[k] != p or t.kind != "id" or t.value not in ("const", "let", "var"):
                    continue
                if t.value == "const" and k + 2 < end and toks[k + 1].kind == "id" \
                        and toks[k + 2].value == "=":
                    name = toks[k + 1].value
                    rhs = toks[k + 3:js_statement_end(toks, k + 3)]
                    if name not in blocked and name not in scoped and name not in here \
                            and self.reads_only(rhs):
                        scoped[name] = " ".join(js_keys(rhs) + [words(x.value) for x in rhs
                                                                 if x.kind == "id"])
                    else:
                        here.add(name)
                    continue
                j = k + 1
                while j < end and toks[j].value not in ("=", ";"):
                    if toks[j].kind == "id":
                        here.add(toks[j].value)
                    j += 1
            blocked |= {n for n in here if n not in scoped}
            p = self.parent[p]
        return scoped, blocked

    def one(self, title: str, line: int, fn: list[Tok], bound: dict) -> dict:
        _, params, body = self.fn_parts(fn)
        self.bound = dict(bound)
        params = params - set(bound)
        self.helper_called = False
        logic, assertions = self.read_body(body, params)
        first_line = line
        kept, reason = keep_reason(self.lines, first_line, ("//", "/*", "*"))
        above = comments_above(self.lines, first_line, ("//", "/*", "*"))
        last = max([x.line for x in fn] or [line])
        inside = "\n".join(c for n, c in self.comments.items() if line <= n <= last)
        ids = " ".join(x.value for x in body if x.kind == "id")
        # Keys name things as identifiers do, and a const an enclosing block
        # read carries the names of what it read.
        keys = js_keys(body)
        named = " ".join(keys + [self.scoped[x.value] for x in body
                                          if x.kind == "id" and x.value in self.scoped])
        declared = f"{above}\n{inside}\n{title}"
        return verdict(self.rel, title, line, self.lang, logic, assertions,
                       declared=declared, security_text=f"{declared}\n{words(ids)}\n{named}",
                       keys=keys, helper=self.helper_called,
                       literal_of=js_literal, kept=kept, reason=reason)

    def read_body(self, body: list[Tok], params: set):
        local = set(self.bound) | set(self.scoped)
        for i, t in enumerate(body):
            if t.kind == "id" and t.value in ("const", "let", "var"):
                j = i + 1
                while j < len(body) and body[j].value not in ("=", ";"):
                    if body[j].kind == "id":
                        local.add(body[j].value)
                    j += 1
                if t.value == "const" and j == i + 2 and j < len(body) and body[j].value == "=":
                    folded = js_fold(body[j + 1:js_statement_end(body, j + 1)])
                    if folded is not None:
                        self.bound[body[i + 1].value] = [Tok("str", folded, body[i + 1].line)]
        logic = False
        for i, t in enumerate(body):
            if (t.kind == "tmpl" and t.subst) or (t.kind == "punc" and t.value == "=>") or \
                    (t.kind == "id" and t.value in ("function", "this", "class")):
                logic = True
            elif t.kind == "punc" and t.value == "(" and i and body[i - 1].kind == "id" \
                    and body[i - 1].value not in JS_KEYWORDS:
                if self.helper_at(body, i - 1, params, local):
                    self.helper_called = True     # its assertion is out of sight
                elif self.call_kind(body, i, params, local) == LOGIC:
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
                if prop or key or self.helper_at(body, i, params, local):
                    continue
                if t.value in params or (t.value not in local and (
                        t.value in self.blocked or self.top.get(t.value) not in (READ, DECL))):
                    logic = True
        return logic, self.assertions(body)

    def helper_at(self, body: list[Tok], k: int, params: set, local: set) -> bool:
        """body[k] names a top-level helper that asserts, called as a function."""
        t = body[k]
        return t.kind == "id" and t.value in self.helpers and t.value not in params \
            and t.value not in local and k + 1 < len(body) and body[k + 1].value == "(" \
            and not (k and body[k - 1].kind == "punc" and body[k - 1].value in (".", "?."))

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

    def expand(self, toks: list[Tok]) -> list[Tok]:
        """A name bound to literals (a test.each column, a const folded from
        literals) stands for those literals."""
        out = []
        for k, t in enumerate(toks):
            prop = k and toks[k - 1].kind == "punc" and toks[k - 1].value in (".", "?.")
            if t.kind == "id" and t.value in self.bound and not prop:
                out += self.bound[t.value]
            else:
                out.append(t)
        return out

    def operand_status(self, groups: list[list[Tok]], negative: bool):
        """An assertion's status from its operands. With negative polarity
        (`.not`, a leading `!`, a not- method) it is a negative control when it
        names a value that must be absent, and a guard, which spares nothing,
        when that value is empty, zero, null, undefined or false. A false or
        null literal compared for equality is a literal like any other."""
        flat = self.expand([t for g in groups for t in g])
        if flat[:1] and flat[0].kind == "punc" and flat[0].value == "!":
            negative = True
        if not negative and any(
                (t.kind == "id" and t.value in self.golden and not (k and flat[k - 1].value in (".", "?.")))
                or (t.kind in ("str", "tmpl") and GOLDEN_PATH_RE.search(t.value) and k >= 2
                    and flat[k - 1].value == "(" and flat[k - 2].kind == "id")
                for k, t in enumerate(flat)):
            return "golden", []                   # a golden file the check does not open
        lits = [t for t in flat if t.kind in ("str", "num", "regex")
                or (t.kind == "tmpl" and not t.subst)
                or (t.kind == "id" and t.value in ("false", "null", "undefined"))]
        trues = [t for t in flat if t.kind == "id" and t.value == "true"]
        names = [t for t in flat if t.kind == "id" and t.value not in JS_LITERAL_WORDS]
        if negative:
            return ("negative", []) if any(js_substantive(t) for t in lits + trues) else ("guard", [])
        if (lits or trues) and names:
            return "readback", lits or trues
        return "no literal", []

    @staticmethod
    def bare(toks: list[Tok]) -> bool:
        """A value read as it is, with no call: `FLAG`, `config.debug`."""
        return bool(toks) and not any(t.kind == "punc" and t.value == "(" for t in toks)

    def expect(self, subject, matcher, margs, negative):
        if matcher in JS_NEGATIVE:
            return ("guard", []) if self.bare(subject) else self.operand_status([subject], True)
        if matcher in JS_NO_LITERAL or matcher is None:
            if negative or self.bare(subject):
                return "guard", []
            return self.operand_status([subject], False)
        if matcher in JS_SNAPSHOT_FILE or (matcher == "toMatchInlineSnapshot" and not margs):
            return "snapshot", []                 # the literal is in a file the runner writes
        if matcher not in JS_POSITIVE:
            return LOGIC, []
        return self.operand_status([subject, margs], negative)

    def node_assert(self, method, args):
        if method in NODE_NEGATIVE:
            return self.operand_status(args[:2], True)
        if method not in NODE_POSITIVE:
            return LOGIC, []
        if method == "ok" and args and self.bare(args[0]):
            return "guard", []
        return self.operand_status(args[:1] if method == "ok" else args[:2], False)


def js_keys(toks: list[Tok]) -> list[str]:
    """The strings the tokens use as keys: a subscript (`HEADERS["X"]`), an
    object key (`{ "X": 1 }`), the name a lookup reads (`.get("X")`,
    `.toHaveProperty("X")`)."""
    out = []
    for k, t in enumerate(toks):
        if t.kind != "str" and not (t.kind == "tmpl" and not t.subst):
            continue
        prev = toks[k - 1] if k else None
        nxt = toks[k + 1] if k + 1 < len(toks) else None
        if prev is None or nxt is None or prev.kind != "punc":
            continue
        if prev.value == "[" and nxt.value == "]" and k >= 2 and (
                toks[k - 2].kind == "id" or toks[k - 2].value in (")", "]", "?.")):
            out.append(t.value)
        elif prev.value in ("{", ",") and nxt.kind == "punc" and nxt.value == ":":
            out.append(t.value)
        elif prev.value == "(" and k >= 3 and toks[k - 2].kind == "id" \
                and toks[k - 2].value in JS_KEY_METHODS and toks[k - 3].value in (".", "?."):
            out.append(t.value)
    return out


def js_substantive(tok: Tok) -> bool:
    if tok.kind in ("str", "tmpl"):
        return tok.value != ""
    if tok.kind == "num":
        return tok.value.rstrip("n").strip("0.") != ""
    if tok.kind == "id":
        return tok.value == "true"
    return True


def js_fold(rhs: list[Tok]) -> str | None:
    """The string a const initializer built only from literals folds into:
    "Se" + "nd", or ["Se", "nd"].join("")."""
    def lit(t):
        return t.kind == "str" or (t.kind == "tmpl" and not t.subst)
    if rhs and all(lit(t) if k % 2 == 0 else (t.kind == "punc" and t.value == "+")
                   for k, t in enumerate(rhs)) and len(rhs) % 2 == 1:
        return "".join(t.value for t in rhs[::2])
    if len(rhs) >= 6 and rhs[0].value == "[" and rhs[0].kind == "punc":
        try:
            end = matching(rhs, 0, "[", "]")
        except NotParsed:
            return None
        items = split_args(rhs[1:end])
        tail = rhs[end + 1:]
        if not all(len(x) == 1 and lit(x[0]) for x in items):
            return None
        if [t.value for t in tail[:3]] == [".", "join", "("] and tail[-1].value == ")":
            sep = tail[3:-1]
            if not sep:
                return ",".join(x[0].value for x in items)
            if len(sep) == 1 and lit(sep[0]):
                return sep[0].value.join(x[0].value for x in items)
    return None


def js_each_table(table, order) -> dict | None:
    """Each parameter of a test.each / it.each -> the literal tokens its table
    gives it, or None when the table is not an array of literal rows (a tagged
    template, a computed table, objects, destructured parameters)."""
    if table == "tagged" or order is None or not table:
        return None
    if not (table[0].kind == "punc" and table[0].value == "[") or \
            matching(table, 0, "[", "]") != len(table) - 1:
        return None

    def literal(part):
        if len(part) == 1 and (part[0].kind in ("str", "num") or (part[0].kind == "tmpl" and not part[0].subst)
                               or (part[0].kind == "id" and part[0].value in JS_LITERAL_WORDS)):
            return part[0]
        if len(part) == 2 and part[0].value == "-" and part[1].kind == "num":
            return Tok("num", "-" + part[1].value, part[1].line)
        return None
    rows = []
    for row in split_args(table[1:-1]):
        if row and row[0].kind == "punc" and row[0].value == "[" and row[-1].value == "]":
            cells = [literal(c) for c in split_args(row[1:-1])]
        else:
            cells = [literal(row)]
        if not cells or any(c is None for c in cells):
            return None
        rows.append(cells)
    if not rows:
        return None
    out = {}
    for k, name in enumerate(order):
        if any(k >= len(r) for r in rows):
            return None
        out[name] = [r[k] for r in rows]
    return out


def js_literal(tok: Tok) -> str:
    if tok.kind in ("str", "tmpl"):
        return json.dumps(tok.value, ensure_ascii=False)
    return tok.value


def read_js(rel: str, src: str, lang: str):
    try:
        return JsFile(rel, src, lang).tests()
    except NotParsed as e:
        raise NotParsed(f"{lang}: does not parse: {e}") from None


# --- the verdict --------------------------------------------------------------
def verdict(path, name, line, lang, logic, assertions, declared, security_text,
            literal_of, kept, reason, keys=(), helper=False) -> dict:
    """The verdict the test's own reading gives. `declared` is the test's name
    or title, markers, comments and docstring; `security_text` adds the
    identifiers it reads. Neither holds a literal. `keys` are the strings the
    test uses as keys; `helper` says it calls a helper in its file that
    asserts. A read-back leaves with the verdict `read-back` and what it
    declares, and settle() decides it against the plant's declarations."""
    rec = {"test": f"{path}::{name}", "path": path, "name": name, "line": line,
           "language": lang, "verdict": "spared", "why": "", "literals": [],
           "assertions": len(assertions), "keep_without_reason": False}
    statuses = {s for s, _ in assertions}
    if logic or LOGIC in statuses:
        rec["why"] = "feeds inputs to logic"
    elif "negative" in statuses:
        rec["why"] = "asserts an absence or a refusal: a negative control"
    elif helper or statuses & {"snapshot", "golden"}:
        rec["verdict"] = "not judged"
        rec["why"] = ("helper assertion" if helper else "snapshot" if "snapshot" in statuses
                      else "golden file")
    elif not assertions:
        rec["why"] = "no assertion to read"
    elif "no literal" in statuses:
        rec["why"] = "an assertion reads back no literal"
    elif "readback" not in statuses:
        rec["why"] = "only guards that a value is set or empty; no literal is read back"
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
        rec["verdict"] = "read-back"
        rec["_declares"] = {
            "bug": names_a_bug(declared),
            "header": any(HEADER_KEY_RE.match(k) for k in keys),
            "words": bool(SECURITY_RE.search(words(URL_RE.sub(" ", security_text)))),
            "kept": kept, "reason": reason}
    return rec


def norm_origin(origin: str) -> str:
    return re.sub(r"[\s_-]+", " ", origin.strip().lower())


def settle(rec: dict, rows: list[dict], trust: dict, words_apply: bool) -> None:
    """Decide a read-back by what the plant declares (the owner's decision of
    2026-11-11: the check spares by declaration, not vocabulary). A §10 row of
    origin bug or security control spares it; so does a test file that reaches
    a file on a marked trust path. A §10 row with any other recorded origin
    decides alone: no name and no word spares its test. With no such row, a
    name that names a bug and a header-shaped key spare it, and the security
    word list spares it only when `words_apply` (the plant marks no trust path,
    or its trust paths could not be read in full)."""
    if rec["verdict"] != "read-back":
        return
    d = rec.pop("_declares")
    deciding = [r for r in rows if r["origin"] and row_matches(r, rec)]
    held = [r for r in deciding if norm_origin(r["origin"]) in SPARING_ORIGINS]
    why = None
    if held:
        o = norm_origin(held[0]["origin"])
        why = f"§10 origin {o} ({held[0]['spec']}): {SPARING_ORIGINS[o]}"
    elif rec["path"] in trust:
        why = f"reads or imports a file on a marked trust path ({trust[rec['path']]})"
    elif not deciding:
        if d["bug"]:
            why = "a regression test for a bug"
        elif d["header"]:
            why = "a security control: a key shaped like an HTTP header name"
        elif d["words"] and words_apply:
            why = "a security control: its declarations name a security subject"
    if why:
        rec["verdict"], rec["why"] = "spared", why
    elif d["kept"] and d["reason"]:
        rec["verdict"], rec["why"] = "kept", d["reason"]
    else:
        rec["verdict"], rec["why"] = "flagged", "reads back a literal"
        rec["keep_without_reason"] = d["kept"]


# --- the plant's trust paths --------------------------------------------------
class TrustUnread(Exception):
    """The trust paths cannot be read; the reason names what to repair."""


def marked_trust(root: Path) -> bool:
    """True when a `kind: crosscut` node of docs/graph/nodes/ is marked
    `trust: true`. A node that cannot be read, or a marked crosscut below
    nodes/ (where graph-lint.py reads no node), raises TrustUnread."""
    nodes = root / NODES
    if not nodes.is_dir():
        return False
    marked = False
    for p in sorted(nodes.rglob("*.md")):
        if p.name.startswith("_") or p.name == "index.md":
            continue
        rel = p.relative_to(root).as_posix()
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise TrustUnread(f"{rel} does not open ({getattr(e, 'strerror', None) or e.__class__.__name__})") \
                from None
        if not text.startswith("---"):
            continue
        end = re.search(r"^---\s*$", text[3:], re.M)
        head = text[3:3 + end.start()] if end else text
        if not (re.search(r"^kind:\s*['\"]?crosscut['\"]?\s*$", head, re.M | re.I)
                and re.search(r"^trust:\s*['\"]?true['\"]?\s*$", head, re.M | re.I)):
            continue
        if end is None:
            raise TrustUnread(f"{rel} has unterminated frontmatter")
        if p.parent != nodes:
            raise TrustUnread(f"{rel} sits below {NODES}/, where graph-lint.py reads no node")
        marked = True
    return marked


def plant_tool(root: Path, rel: str, args: list, label: str, stdin: str | None = None) -> dict:
    """The JSON a plant tool prints, run from the plant root; TrustUnread when
    it is missing, fails, or prints no JSON object."""
    if not (root / rel).is_file():
        raise TrustUnread(f"{rel} is missing")
    try:
        r = subprocess.run([sys.executable, str(root / rel), *args], cwd=root, input=stdin,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=TRUST_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise TrustUnread(f"{rel} {label} did not answer within {TRUST_TIMEOUT} s") from None
    except OSError as e:
        raise TrustUnread(f"{rel} {label} did not start ({e.strerror or e})") from None
    if r.returncode != 0:
        last = (r.stderr.strip().splitlines() or [""])[-1][:200]
        raise TrustUnread(f"{rel} {label} did not answer (exit {r.returncode}: {last})")
    try:
        doc = json.loads(r.stdout)
    except ValueError:
        raise TrustUnread(f"{rel} {label} printed no JSON") from None
    if not isinstance(doc, dict):
        raise TrustUnread(f"{rel} {label} printed JSON this check does not read")
    return doc


def trust_reach(root: Path) -> tuple[dict, list[str], int]:
    """({test file: the trust-path file it reaches}, the incomplete records of
    the answer, how many files the trust paths claim). The plant's own tools
    answer: source-index.py build lists the files, graph-lint.py --trust-claims
    names the ones a trust crosscut claims, source-index.py affected-tests
    names the test files whose links reach them (its floor included: a test
    the index cannot pin may reach them)."""
    built = plant_tool(root, SOURCE_INDEX, ["build", "--json"], "build")
    inventory = built.get("inventory")
    if not str(built.get("schema", "")).startswith("cypress.source-index.answer/") \
            or not isinstance(inventory, list):
        raise TrustUnread(f"{SOURCE_INDEX} build answered in a shape this check does not read "
                          f"(no inventory)")
    for rec in built.get("incomplete") or []:
        if isinstance(rec, dict) and rec.get("reason") in NO_INVENTORY:
            raise TrustUnread(f"the source index holds no inventory ({rec['reason']}: {rec.get('subject')})")
    paths = sorted({r["path"] for r in inventory if isinstance(r, dict) and isinstance(r.get("path"), str)})
    claimed: dict = {}
    for k in range(0, len(paths), CLAIMS_CHUNK):
        doc = plant_tool(root, GRAPH_LINT, ["--trust-claims", *paths[k:k + CLAIMS_CHUNK]], "--trust-claims")
        if not isinstance(doc.get("claims"), dict):
            raise TrustUnread(f"{GRAPH_LINT} --trust-claims answered in a shape this check does not read")
        claimed.update(doc["claims"])
    if not claimed:
        raise TrustUnread("the marked trust paths claim no file the source index holds; name their "
                          "paths in the crosscut's load_when or repo:")
    files = sorted(claimed)
    doc = plant_tool(root, SOURCE_INDEX, ["affected-tests", "--json", "-"], "affected-tests",
                     stdin="".join(f"{p}\n" for p in files))
    if not isinstance(doc.get("tests"), list):
        raise TrustUnread(f"{SOURCE_INDEX} affected-tests answered in a shape this check does not read")
    reach: dict = {p: p for p in files}          # a test file on a trust path reaches itself
    for row in doc["tests"] + [r for r in doc.get("floor") or [] if isinstance(r, dict)]:
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            via = row.get("via") if isinstance(row.get("via"), list) and row.get("via") else [row.get("from")]
            reach.setdefault(row["path"], str(via[0]))
    gaps = sorted({f"{r.get('reason')}: {r.get('subject')}" for r in doc.get("incomplete") or []
                   if isinstance(r, dict)})
    return reach, gaps, len(files)


def read_trust(root: Path, needed: bool) -> dict:
    """{"state", "message", "tests", "words_apply"}: what the plant's trust
    paths spare, and whether the security word list still applies. The state
    is `none` (the plant marks no trust path), `consulted`, `partial` (the
    source index answered incomplete), `not consulted` (with the reason), or
    `not needed` (no test reads back a literal, so no tool was run)."""
    try:
        marked = marked_trust(root)
    except TrustUnread as e:
        return {"state": "not consulted", "tests": {}, "words_apply": True,
                "message": f"worth-check: trust paths not consulted: {e}; no test is spared for a trust "
                           f"path, and the security word list applies to a test no §10 row maps"}
    if not marked:
        return {"state": "none", "tests": {}, "words_apply": True,
                "message": "worth-check: trust paths: the plant marks none, so the security word list "
                           "applies to a test no §10 row maps"}
    if not needed:
        return {"state": "not needed", "tests": {}, "words_apply": False,
                "message": "worth-check: trust paths: marked; no test reads back a literal, so the "
                           "source index was not asked"}
    try:
        reach, gaps, n = trust_reach(root)
    except TrustUnread as e:
        return {"state": "not consulted", "tests": {}, "words_apply": True,
                "message": f"worth-check: trust paths not consulted: {e}; no test is spared for a trust "
                           f"path, and the security word list applies to a test no §10 row maps"}
    tests = reach                                 # a claimed file maps to itself
    counted = len([p for p, f in reach.items() if p != f])
    if gaps:
        shown = "; ".join(gaps[:5]) + (f" and {len(gaps) - 5} more" if len(gaps) > 5 else "")
        return {"state": "partial", "tests": tests, "words_apply": True,
                "message": f"worth-check: trust paths consulted in part: {n} file(s) on the marked trust "
                           f"paths, {counted} test file(s) reach them; the source index answered "
                           f"incomplete ({shown}), so the security word list still applies to a test "
                           f"no §10 row maps"}
    return {"state": "consulted", "tests": tests, "words_apply": False,
            "message": f"worth-check: trust paths consulted: {n} file(s) on the marked trust paths, "
                       f"{counted} test file(s) reach them ({SOURCE_INDEX}); a test no §10 row maps is "
                       f"spared by a declaration only"}


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
            found, unread = read_python(rel, src, root) if lang == "python" else read_js(rel, src, lang)
        except NotParsed as e:
            not_checked.append({"path": rel, "reason": str(e), "language": lang})
            continue
        tests += found
        not_checked += [dict(n, test=True) for n in unread]
        read.append(rel)

    # The plant's declarations decide each read-back: its §10 rows, then its
    # trust paths, then (where neither speaks) the test's own declarations.
    specs = sorted((root / SPECS).glob("SPEC-*.md")) if (root / SPECS).is_dir() else []
    if args.spec and not any(p.name == args.spec or p.name.startswith(args.spec + "-") for p in specs):
        raise Unreadable(f"--spec {args.spec}: no {SPECS}/{args.spec}-*.md in this plant; name a spec it holds")
    rows, row_notes = [], []
    for p in specs:
        try:
            rows += spec_rows(p)
        except OSError as e:
            row_notes.append(f"worth-check: §10 rows not read: {SPECS}/{p.name} does not open "
                             f"({e.strerror or e}); its tests read as if no row maps them")
    trust = read_trust(root, needed=any(t["verdict"] == "read-back" for t in tests))
    for t in tests:
        settle(t, rows, trust["tests"], trust["words_apply"])

    flagged = [t for t in tests if t["verdict"] == "flagged"]
    unjudged = [t for t in tests if t["verdict"] == "not judged"]
    for t in tests:
        t["in_baseline"] = t["verdict"] == "flagged" and t["test"] in base_set
    new = [t for t in flagged if not t["in_baseline"]]
    old = [t for t in flagged if t["in_baseline"]]
    now = {t["test"] for t in flagged}
    read_set = set(read)
    # a test the check did not read or did not judge stays in the baseline as it was
    unread_tests = {n["path"] for n in not_checked if n.get("test")} | {t["test"] for t in unjudged}
    shrinkable = sorted(e for e in base_set - now - unread_tests
                        if not args.paths or e.split("::", 1)[0] in read_set)
    languages = sorted({n["language"] for n in not_checked if not n.get("test")})
    unread_reasons: dict = {}
    for n in not_checked:
        if n.get("test"):
            unread_reasons[n["reason"]] = unread_reasons.get(n["reason"], 0) + 1

    if args.removal_list:
        return removal_list(rows, flagged, args.spec)
    rc = 1 if new else 0
    messages = []
    if args.write_baseline:
        grow = sorted(now - base_set) if baseline is not None else []
        if grow:
            messages.append(
                f"worth-check: --write-baseline refused: the baseline only shrinks, and "
                f"{len(grow)} flagged test(s) are not in it: {', '.join(grow)}. Keep each with a "
                f"\"worth-check: keep — <reason>\" line above it, or strengthen it so it feeds "
                f"inputs to the logic it guards; a trust-path, bug-origin or security-control test "
                f"is never removed to clear a flag. Then write again. "
                f"{base_path.relative_to(root) if base_path.is_relative_to(root) else base_path} "
                f"is unchanged.")
            rc = 1
        else:
            keep = sorted(now | (base_set & unread_tests))   # an unread test stays as it was
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

    # U counts the unread files, the unread tests and the tests not judged.
    summary = (f"worth-check: {len(flagged)} flagged ({len(old)} in baseline), {len(read)} files "
               f"read, {len(not_checked) + len(unjudged)} not checked")
    parts = ([f"languages: {', '.join(languages)}"] if languages else []) + [
        f"{reason}: {n} test(s)" for reason, n in sorted(unread_reasons.items())] + (
        [f"not judged: {len(unjudged)} test(s)"] if unjudged else [])
    summary += f" ({'; '.join(parts)})" if parts else ""
    messages = row_notes + messages
    if args.json:
        print(json.dumps({"schema": SCHEMA, "configured": True, "tests": tests,
                          "not_checked": not_checked, "not_judged": len(unjudged),
                          "shrinkable": shrinkable, "files_read": len(read), "flagged": len(flagged),
                          "in_baseline": len(old),
                          "trust": {"state": trust["state"], "message": trust["message"]},
                          "messages": messages, "exit": rc}, indent=1))
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
    for t in unjudged:
        print(f"{t['test']}  not judged ({t['why']})")
    print(trust["message"])
    for m in messages:
        print(m)
    print(summary)
    if new:
        print(f"worth-check: FAIL — {len(new)} flagged test(s) are not in the baseline. For each: "
              f"keep it with a \"worth-check: keep — <reason>\" line directly above it if it earns "
              f"its place, or strengthen it so it feeds inputs to the logic it guards. A test on a "
              f"trust path, a test whose §10 origin is bug and a security-control test are never "
              f"removed to clear a flag: keep it with its reason or strengthen it. Any other test "
              f"leaves the suite only when the owner confirms it by name (--removal-list). The "
              f"check never edits a test.")
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


def removal_list(rows: list[dict], flagged: list[dict], spec: str | None) -> int:
    """Print the batch of flagged tests for the owner's confirmation. Read-only:
    it removes no file and edits no test. A test whose §10 origin is bug or
    security control is spared before the batch is drawn; the hold-back below
    stays as a second guard."""
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
