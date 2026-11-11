---
status: implemented
status_date: 2026-11-11
owner: architect
status_evidence: tests/test-worth-check.sh (X580 to X592, X600 to X602, X800 to X806, X810 to X812, X820), wired into tests/run.sh, every §10 row green over the 26 contracts; each case was seen failing first on the missing tool or the unfixed heuristic, then passing against the fixture suite of tests/fixtures/worth/, its hand-written verdict table and the independent tester's adversarial table
---

# SPEC-0009: the worth check

## 0. Metadata

- **Identifier:** SPEC-0009-worth-check
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-10
- **Last reviewed:** 2026-11-11
- **Related grill section:** docs/plans/grill-8.5.0-tester-surfaces.md, step T10
  (the worth check)
- **Related ADRs:** adr-0034-a-test-is-owed-only-where-it-can-catch-something
  (OD3: a test that catches nothing is removed, and graft and grow never remove
  a test); adr-0003-enforcement-layering-honesty (the check is detective, a
  heuristic that errs toward sparing); adr-0021 (the tools `install.sh` places
  are held against `manifest.json`)
- **Related specs:** SPEC-0001-install-placement (its placement contracts and
  destination sweep hold every file `install.sh` writes, this tool's copy
  included); SPEC-0007-source-index (the same `TEST_GLOBS` declaration, read the
  same way)
- **Related wiki pages:** none (stdlib Python only)
- **Design latitude:** balanced. The owner decided on 2026-11-10 that the
  check reads Python and TypeScript or JavaScript and reports every other
  language as not checked, and that a grafted plant's baseline is decided per
  plant after the owner sees it. The owner decided on 2026-11-11 that the
  check keeps Python and TypeScript or JavaScript only
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [x] · architect [x] · tester [x]
  Product 2026-11-10: the owner's decisions of 2026-11-10 on the languages read
  and on the baseline of a grafted plant, as the round's surface definition
  states them. Architect 2026-11-10: the round's surface definition of the worth
  check, which this spec transcribes in §3, §4 and §6. Tester 2026-11-10: the
  fixture suite and its verdict table were written before the tool and every
  case was seen failing on the missing tool first; an independent tester's
  review of the fixtures is the open item of §11. Tester (independent)
  2026-11-11: four rounds of adversarial cases, verdicts written first; no
  false positive remains on a test whose shape declares security (a header key,
  a security word in its declarations, identifiers or keys, an absence or a
  refusal); the remaining false positives are vocabulary edges that §7 names,
  with the keep-line remedy, listed as limits in `known-gaps.tsv`.

## 1. Summary

ADR-0034 says a test that catches nothing is removed. The commonest such test
reads back a literal the same change adds: it is red while the line is absent
and green once it is present, so it proves only that the change is there. The
worth check, `tools/worth-check.py`, placed in every plant at
`docs/graph/worth-check.py`, reads a plant's tests and flags each one whose only
assertions read back a literal that way. It spares a test that feeds inputs to
logic, a regression test for a bug and a security negative control. It never
removes or edits a test: a flagged test is the owner's to remove, keep with a
reason, or leave in the plant's baseline. Its `--removal-list` prints the
flagged tests as one numbered batch the owner confirms by naming them, and
removes nothing itself.

## 2. Scope

In scope: the tool, its placement, the baseline file it writes, the keep line it
reads, the gate row a plant adds to its verification runbook, and the removal
list it prints for the owner.

Out of scope: removing a test (ADR-0034 OD3 gives that to the unit of work that
created it, or to a batch the owner confirms, `protocol.test-first`, Removing a
test that catches nothing); any language beyond Python and
TypeScript or JavaScript; running the check over this repository's own suite,
whose tests assert documentation text on purpose.

## 3. User-facing behavior

A plant runs `python3 docs/graph/worth-check.py` from its root. Each flagged
test is one line that names the test, the literal it reads back, how many
assertions it has, and the keep line to add if the test earns its place. A
summary line counts the flagged tests, the ones in the baseline, the files read
and the files not checked with their languages, and the tests not checked with
their reasons. When a flagged test is neither
kept nor in the baseline, a closing line says the run failed and what to do with
each test, and the exit code is 1. A plant whose `docs/graph/spec-lint.py` is
missing or sets no `TEST_GLOBS` gets one line saying the check is not
configured, and exit 0.

## 4. Functional contracts

### Contract: WORTH_FLAGS_A_READ_BACK_TEST
- **Given:** a Python, TypeScript or JavaScript test whose every assertion
  compares a literal with a value the test reads back unchanged: a declared
  constant, a config entry, or text read from a file
- **When:** the worth check reads it
- **Then:** the test is flagged with the line
  `path::name  reads back <literal> that the same file/change adds; only assertion(s): <n>; keep it with a line "<comment> worth-check: keep — <reason>" above the test if it earns its place`,
  where `<comment>` is the file's own comment syntax
- **And:** a flagged test that is neither kept nor in the baseline makes the run
  exit 1, and the closing line says to remove it, make it feed inputs to the
  logic it guards, or keep it with a reason

### Contract: WORTH_SPARES_LOGIC_TESTS
- **Given:** a test that calls the code under test, or exercises a pattern, a
  condition, an order of precedence or a computed value, or reads a file the code
  under test wrote, or compares two values with no literal between them
- **When:** the worth check reads it
- **Then:** the test is not flagged, and the `--json` report lists it as read,
  with verdict `spared` and the reason

### Contract: WORTH_SPARES_BUG_REGRESSIONS
- **Given:** a test whose comment directly above, comment inside, docstring,
  name, title, decorator or marker names a bug, an issue, a regression or a
  ticket
- **When:** the worth check reads it, even with the shape of a read-back
- **Then:** the test is not flagged: a bug reproduction is always written and
  stays (ADR-0034)

### Contract: WORTH_SPARES_SECURITY_CONTROLS
- **Given:** a test that asserts a named value is refused or absent
  (`"/admin" not in nav`, `.not.toContain("/admin")`, an expected exception),
  or whose name, title, decorator, marker, comment, docstring, an identifier
  it reads or a string it uses as a key (WORTH_SECURITY_KEY_IS_A_DECLARATION)
  names a security subject, or a string it uses as a key is shaped like an
  HTTP header name (WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION)
- **When:** the worth check reads it
- **Then:** the test is not flagged

### Contract: WORTH_SETUP_OUTPUT_IS_NOT_A_LITERAL
- **Given:** a test that reads a file, in the scope of a setup hook that runs
  code: a unittest `setUp`, `setUpClass` or `asyncSetUp`, a pytest `setup_*`
  function, an autouse fixture in the file or in a `conftest.py` between the
  plant root and the test, a base class the check cannot see, or a
  `beforeAll`, `beforeEach` or `before` in the test's block or at the top of
  its file
- **When:** the worth check reads it
- **Then:** the file the test reads counts as output of that code, and the test
  is spared as feeding inputs to logic
- **And:** a test outside the hook's block, and a test that reads only a
  declared constant, is read as before

### Contract: WORTH_IMPORTED_CALL_IS_CODE_UNDER_TEST
- **Given:** a TypeScript or JavaScript test that calls a name imported from a
  module of the plant, whatever the name (`resolve(...)`), or a method on an
  imported object (`router.match(...)`)
- **When:** the worth check reads it
- **Then:** the call is code under test and the test is spared
- **And:** a read call keeps counting as a read only when its name is a global,
  an assertion, or comes from a Node built-in module (`fs`, `path`, `url`), and
  a string method counts as a read only on a value already read or on an
  imported constant written in upper case

### Contract: WORTH_UNREAD_TEST_IS_NOT_CHECKED
- **Given:** a parametrized test (pytest `parametrize`, `test.each`, `it.each`),
  or a test whose title is computed
- **When:** the worth check reads its file
- **Then:** a table written as literals is read, each parameter taking the
  values of its table, and a flagged line shows those values
- **And:** a table that is not written as literals (a computed table, a tagged
  template, object rows) is listed as `path::name  not checked (parametrized)`,
  a computed title as `path::line N  not checked (computed title)`, the summary
  counts each under `not checked (<reason>: N test(s))`, and no output calls
  the test or the run clean

### Contract: WORTH_SPARING_READS_DECLARATIONS_NOT_CONTENT
- **Given:** a read-back test whose string literal holds a URL (`https://...`),
  a word such as cookies, or whose comment or title holds a colour code
  (`#112233`, `#0055ff`)
- **When:** the worth check reads it
- **Then:** the test is flagged: the regression and security spares read the
  test's name or title, decorators or markers, comments, docstring and (for
  security) the identifiers it reads and the strings it uses as keys, never the
  words inside a value the test compares against;
  a bare `#<digits>` names an issue except on a comment line about a colour, and
  a URL in a comment is read without its scheme

### Contract: WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK
- **Given:** a test whose assertions are a guard beside a read-back: `!= ""`,
  `is not None`, a bare `assert x`, `assertFalse(x)`, `assertIsNone(x)`,
  `toBeTruthy`, `toBeDefined`, `toBeFalsy`, `toBeNull`, `toBeUndefined`, or a
  negated assertion over an empty, zero, null or false value; and a test that
  compares a read value with a `False`, `None`, `false` or `null` literal
- **When:** the worth check reads them
- **Then:** the guard spares nothing and the test is flagged, and a `False` or
  `null` literal compared for equality is a read-back like any other literal
- **And:** a test whose only assertions are guards is spared, and an assertion
  that a named value is absent stays a negative control
  (WORTH_SPARES_SECURITY_CONTROLS)

### Contract: WORTH_LITERAL_BUILT_FROM_LITERALS_IS_A_LITERAL
- **Given:** a read-back against a value built only from literals
  (`"Se" + "nd"`, `"".join(["Se", "nd"])`, `["Se", "nd"].join("")`), a string
  method chain on an imported constant (`SUBMIT_LABEL.trim()`), or a
  `toMatchInlineSnapshot` whose text sits in the test
- **When:** the worth check reads it
- **Then:** the test is flagged, and the line shows the folded literal
  (`"Send"`)

### Contract: WORTH_SECURITY_KEY_IS_A_DECLARATION
- **Given:** a read-back test whose security setting is held under a string
  key: a subscript (`HEADERS["Content-Security-Policy"]`,
  `SETTINGS["SESSION_COOKIE_SECURE"]`), a dict or object key, the name a lookup
  reads (`.get("X")`, `getattr(obj, "x")`, `.toHaveProperty("X")`), or an
  attribute a setUp copied from a security constant
- **When:** the worth check reads it
- **Then:** the key names a thing as an identifier does, so the test is spared
  as a security control, with the same verdict it gets when the setting is a
  constant (`SESSION_COOKIE_SECURE is True`)
- **And:** a security word in the value the test compares against spares
  nothing: `COPY["banner_title"] == "Your session cookies keep you logged in"`
  is flagged

### Contract: WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION
- **Given:** a read-back test that uses as a key a string shaped like an HTTP
  header name, capitalised words joined by hyphens
  (`^[A-Z][A-Za-z0-9]*(-[A-Za-z0-9]+)+$`: `X-Frame-Options`,
  `X-Content-Type-Options`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`,
  `Cache-Control`), under a subscript, as a dict or object key, or as the name
  a lookup reads (`.get`, `headers.get`, `toHaveProperty`, `Map.get`); or a
  test that reads an identifier named for a standard security response header
  (`X_CONTENT_TYPE_OPTIONS`, `referrerPolicy`)
- **When:** the worth check reads it
- **Then:** the test is spared as a security control: the shape of the key is
  the declaration, so no word list has to name every security header. The rule
  is conservative by design: a plain header read-back under such a key
  (`HEADERS["Content-Type"] == "text/html"`) is spared too, since a missed flag
  costs nothing and a flagged security test costs a gate
- **And:** a header-shaped string the test compares against is content and
  spares nothing: `LABELS["header_hint"] == "X-Frame-Options"` is flagged

### Contract: WORTH_SETUP_THAT_ONLY_READS_IS_A_READ
- **Given:** a unittest class with only bases the check knows, whose setup
  methods only bind `self.<attr>` to values they read (a constant, a config
  entry, a file read with no hook in scope that runs code), and whose other
  methods store no such attribute
- **When:** the worth check reads a test of the class that asserts on the
  attribute
- **Then:** the attribute reads as the value it was bound to, so a test that
  reads back a copied constant is flagged as a module-level constant is
- **And:** a setup method that runs any other statement, and a class with a
  base the check cannot see, leave the attribute logic and the test spared

### Contract: WORTH_DESCRIBE_BODY_READ_IS_A_READ
- **Given:** a TypeScript or JavaScript test inside a block (a `describe`
  body) that declares `const NAME = <value>`, where the value only reads: a
  call from a Node built-in module or a global, a string method on a value
  read, names declared at the top of the file
- **When:** the worth check reads the test
- **Then:** `NAME` reads as that value, so a test that reads back a literal
  from a file read in the describe body is flagged as the same read at the top
  of the file is
- **And:** a `let` or `var`, a destructured or typed `const`, a container
  literal, a parameter of the enclosing function, a call into code under test,
  and a hook in scope that runs code each leave the name logic and the test
  spared; the innermost declaration of a name wins

### Contract: WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH
- **Given:** a test whose name promises logic and whose body reads a value back,
  a read-back test with many assertions, a logic test that shares its name with
  a read-back, and a test with no assertion
- **When:** the worth check reads them
- **Then:** the verdict follows the assertions alone: the first two are
  flagged, the last two are not, and a test is never flagged without its
  assertions being read

### Contract: WORTH_UNREAD_FILE_IS_NOT_CHECKED
- **Given:** a test file in a language the check does not read, or a Python,
  TypeScript or JavaScript file that does not parse
- **When:** the worth check runs
- **Then:** the file is listed as `<path>  not checked (<language or reason>)`,
  the summary counts it under `not checked (languages: ...)`, and no output calls
  it or the run clean

### Contract: WORTH_UNCONFIGURED_PLANT_IS_NAMED
- **Given:** a plant with no `docs/graph/spec-lint.py`, or one that sets no
  `TEST_GLOBS`
- **When:** the worth check runs, with or without `--json` or `--write-baseline`
- **Then:** it prints
  `worth-check: not configured for this plant (set TEST_GLOBS in docs/graph/spec-lint.py)`,
  exits 0, writes nothing, and never prints the word clean

### Contract: WORTH_KEEP_MARKER_KEEPS_WITH_REASON
- **Given:** a comment line `worth-check: keep — <reason>`, in any comment
  syntax, directly above a test the check would flag
- **When:** the worth check runs
- **Then:** the test does not fail the run and the report prints
  `worth-check: kept: path::name — <reason>`
- **And:** a keep line with no reason keeps nothing, and the report says so on
  the test's own line

### Contract: WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS
- **Given:** a plant whose `docs/graph/worth-baseline.txt` holds the tests
  flagged on the day it was recorded
- **When:** the worth check runs
- **Then:** the tests in the baseline are reported and do not fail the run, and
  a newly flagged test outside it fails the run with exit 1
- **And:** the first `--write-baseline` records every test flagged that day,
  and a plant with no baseline file has an empty baseline

### Contract: WORTH_BASELINE_ONLY_SHRINKS
- **Given:** a baseline file exists
- **When:** `--write-baseline` would add a test to it
- **Then:** the write is refused with exit 1, the message names each test it
  would add and what to do with it, and the file is unchanged
- **And:** an entry that no longer flags is reported as shrinkable, and
  `--write-baseline` then drops it

### Contract: WORTH_BAD_INPUT_EXITS_2
- **Given:** an unknown option, a PATH that does not exist, a test file that is
  not UTF-8, or `--write-baseline` with a PATH
- **When:** the worth check runs
- **Then:** it exits 2 and names the option or path and the reason
- **And:** a PATH that exists narrows the read to that file or directory

### Contract: WORTH_REMOVAL_LIST_NAMES_EACH_TEST
- **Given:** a plant whose flagged tests include one written now and one in
  the baseline, mapped by §10 rows of the plant's `docs/graph/specs/`
- **When:** `worth-check.py --removal-list` runs
- **Then:** it prints `removal batch — N test(s) for the owner's confirmation
  (nothing is removed by this list)`, then per test a numbered line naming it,
  a `flagged:` line with the literal it reads back and `(worth-check)` or
  `(worth-check; in the baseline)`, a `§10 row:` line per row with its spec,
  risk text and origin, ending `-> removable on confirmation` for origin
  `design`, and a `leaves without evidence:` line naming each `test`-kind
  contract no other row's test still covers, or `none`
- **And:** it closes with `To confirm, reply in the chat naming the tests to
  remove, e.g. "remove tests 1 and 4 of the batch".` and exits 0

### Contract: WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS
- **Given:** a flagged test whose §10 origin is `bug`, one whose origin is
  `security control`, one in a legacy §10 table that records no origin, and
  one no §10 row maps
- **When:** `--removal-list` runs
- **Then:** each is listed with `NOT REMOVABLE AUTOMATICALLY` and its reason:
  a bug reproduction stays; a security control that kills no mutant is a
  finding for the security agent; the architect records the origin first; the
  architect maps it to a contract first

### Contract: WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC
- **Given:** a reopened spec, and a baseline holding tests its §10 maps
- **When:** `--removal-list --spec SPEC-NNNN` runs
- **Then:** the batch, headed `removal batch for SPEC-NNNN`, lists only the
  tests that spec's §10 maps, its baseline tests included
- **And:** a spec the plant does not hold exits 2 and names it

### Contract: WORTH_NEVER_EDITS_A_TEST
- **Given:** any run of the worth check, `--removal-list` included
- **When:** it finishes
- **Then:** every test file is byte for byte as it was, and nothing was written
  beside it; the only file the tool writes is the baseline

### Contract: WORTH_CHECK_IS_PLACED
- **Given:** a fresh install of any host
- **When:** the install finishes
- **Then:** `docs/graph/worth-check.py` is byte-identical to the seed's
  `tools/worth-check.py`, answers `--help` with the keep line and the gate row of
  the verification runbook, and in a plant with no tests reads nothing and exits 0

## 5. Non-functional requirements

Stdlib Python on the seed's Python floor, no third-party parser and no model.
The tool reads `TEST_GLOBS` and `SKIP_DIRS` with `ast.literal_eval` from the
plant's `spec-lint.py`, as `source-index.py` does, and never imports it. It
adds no configuration of its own to any graph engine; the table in
`tools/graft-graph-engine.py` keeps the plant's `TEST_GLOBS` and `SKIP_DIRS`. It adds nothing to the kernel or to any always-loaded
prompt.

## 6. Data shapes

### Command line

`worth-check.py [--root DIR] [--baseline FILE] [--write-baseline] [--json] [--help] [PATH...]`,
and `worth-check.py --removal-list [--spec SPEC-NNNN]`, which takes neither
`--write-baseline` nor `--json`.
`--root` defaults to the current directory; `--baseline` is read from the root
and defaults to `docs/graph/worth-baseline.txt`.

### What counts as a read-back

A Python test is a function named `test*` at module level or in a class; a
TypeScript or JavaScript test is a `test(` or `it(` call, with `.only`,
`.concurrent`, `.each`, `.fails` or `.sequential`, whose first argument is a
literal title and which takes a function literal. A test is flagged when all of
these hold:

- every call in its body reads a value rather than computing one: a file read
  with no setup hook in scope that runs code, a path join, a JSON parse, a
  string method on text already read, or the assertion itself; in TypeScript or
  JavaScript a read call comes from a global or a Node built-in module, and any
  other imported name is code under test;
- every name it reads is declared in the file or imported, a parameter whose
  parametrize or `.each` table gives it literals, a local built only from
  literals, an attribute a setup method only bound to a value it reads, or a
  const an enclosing describe body only reads; never a fixture of the test and
  never a value code set up elsewhere;
- at least one assertion compares a literal with such a value with positive
  polarity (a `False`, `None`, `false` or `null` literal included); every other
  assertion is such a read-back or a guard (a value is set or not empty);
- no assertion names a value that must be absent or refused;
- no name, title, decorator, marker, comment or docstring marks it as a bug
  regression, and none of them, nor an identifier it reads, nor a string it
  uses as a key, names a security subject; no string it uses as a key is
  shaped like an HTTP header name; the words of a value it compares against
  never count, a header name among them;
- no keep line with a reason sits directly above it.

A parametrized test whose table is not written as literals, and a test whose
title is computed, are not read: each is listed as not checked.

### Output and exit codes

One line per flagged test (§4), a `worth-check: kept:` line per kept test, a
`worth-check: shrinkable:` line per baseline entry that no longer flags, a
`<path>  not checked (<reason>)` line per unread file, a
`<path>::<name>  not checked (<reason>)` line per unread test, then
`worth-check: N flagged (M in baseline), K files read, U not checked (languages: ...; <reason>: T test(s))`,
where U counts the unread files and tests and the parenthesis names only what
is there. An unread test in the baseline stays in it and is never shrinkable.
Exit 0: nothing new is flagged, or the plant is not configured. Exit 1: a flagged
test is neither kept nor in the baseline, or `--write-baseline` was refused.
Exit 2: a usage error or an unreadable input. `--json` prints every test read
with its verdict (`flagged`, `spared`, `kept`) and reason.

### Removal list

It reads the plant's `docs/graph/specs/SPEC-*.md` §10 tables as text, never
importing the plant's spec lint: a risk-based row links by its `path::name`
Test cell and its Covers cell, a legacy row by its Test file and Test name
cells and its first cell. A row whose status records `dropped:`, `merged
into` or `removed:` links nothing. A contract's kind is its `Check:` line,
`test` when it has none.

### Baseline

`docs/graph/worth-baseline.txt` is plant state, tracked in Git and never placed
by the installer: one comment line, then one `path::name` per line. It only
shrinks after the first write.

## 7. Failure modes

### Failure: HEURISTIC_SPARES_A_READ_BACK
- **Trigger:** a read-back test the static reading cannot see through: an
  assertion inside a helper the test calls; a constant held equal to a golden
  file, which reads as two homes with no literal between them; a snapshot held
  in a file the runner writes (`toMatchSnapshot`, a snapshot fixture); a
  fixture parameter's value; a test inside `describe.each`; a name, marker or
  key that says regression or names a security subject for an unrelated reason
  (`ROUTES["/login"]`); a read-back under any key shaped like an HTTP header
  name (`HEADERS["Content-Type"]`), which
  WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION spares on purpose; a setup
  method or describe body that runs any code beside the read it holds; a `let`
  in a describe body.
  Each case the independent tester found is a row of
  `tests/fixtures/worth/known-gaps.tsv`
- **Response:** the test is spared; the check errs toward sparing by design
- **Recovery:** a reviewer still applies `test-first.proportionate-checks`

### Failure: SECURITY_CONTROL_OUTSIDE_THE_SPARE_IS_FLAGGED
- **Trigger:** a security test the security spare does not recognise. The
  spare is a vocabulary-and-declaration heuristic with edges: it reads a word
  list over the test's declarations, identifiers and keys, the shape of a
  header-name key, and the names of the standard security response headers. A
  control whose name, identifiers and keys hold none of these (a lower-case
  header key such as `headers["x-frame-options"]`, a setting named for its
  effect, `SETTINGS["FRAME_POLICY"]`) reads as a plain read-back
- **Response:** the test is flagged, and the plant's gate fails on it as on any
  new flag
- **Recovery:** the author keeps the test with a keep line and its reason
  (`# worth-check: keep — the clickjacking control`): the refusal at the door.
  The check never edits the test, and the residual risk is this one keep line
  per control the spare misses

### Failure: SETUP_FILE_OUTSIDE_THE_TEST_IS_NOT_READ
- **Trigger:** a test reads a file that a setup file named only in the
  runner's configuration builds (jest `globalSetup`, vitest `setupFiles`, a
  `conftest.py` outside the plant root)
- **Response:** the file reads as a literal the change adds, so the test can be
  flagged although it reads output of the code under test
- **Recovery:** the author keeps the test with a keep line naming the setup
  file; the check never edits the test

### Failure: ADOPTED_SUITE_FLAGS_ON_DAY_ONE
- **Trigger:** a project adopted with an existing suite holds many read-back
  tests
- **Response:** graft records them once as the plant's baseline and reports
  how many it holds; graft and grow remove no test
- **Recovery:** the owner decides per plant to record a baseline, keep tests
  with reasons, or leave them flagged

## 8. Examples

```
$ python3 docs/graph/worth-check.py
tests/test_labels.py::test_submit_label  reads back "Send" that the same file/change adds; only assertion(s): 1; keep it with a line "# worth-check: keep — <reason>" above the test if it earns its place
tests/e2e/smoke.sh  not checked (shell)
worth-check: 1 flagged (0 in baseline), 12 files read, 1 not checked (languages: shell)
worth-check: FAIL — 1 flagged test(s) are not in the baseline. ...
```

## 9. Acceptance criteria

- [x] AC-1: a read-back test in Python, TypeScript or JavaScript is flagged with
  a line that names it, the literal, the assertion count and the keep line;
  maps to WORTH_FLAGS_A_READ_BACK_TEST, WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH
- [x] AC-2: a logic test, a bug regression and a security negative control are
  never flagged; maps to WORTH_SPARES_LOGIC_TESTS, WORTH_SPARES_BUG_REGRESSIONS,
  WORTH_SPARES_SECURITY_CONTROLS
- [x] AC-3: an unread file is not checked and an unconfigured plant is named,
  never called clean; maps to WORTH_UNREAD_FILE_IS_NOT_CHECKED,
  WORTH_UNCONFIGURED_PLANT_IS_NAMED
- [x] AC-4: a kept test passes with its reason, the baseline holds older flags
  and only shrinks, and a new flag fails; maps to
  WORTH_KEEP_MARKER_KEEPS_WITH_REASON, WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS,
  WORTH_BASELINE_ONLY_SHRINKS
- [x] AC-5: bad input exits 2, no test is edited, and every install places the
  tool; maps to WORTH_BAD_INPUT_EXITS_2, WORTH_NEVER_EDITS_A_TEST,
  WORTH_CHECK_IS_PLACED
- [x] AC-6: the removal list names each flagged test, its row, origin and the
  contract it would leave without evidence, holds back the three kinds that
  wait for a decision of their own, and narrows to a reopened spec; maps to
  WORTH_REMOVAL_LIST_NAMES_EACH_TEST,
  WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS,
  WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC
- [x] AC-7: a logic test is never flagged because a setup hook built the file it
  reads or because an imported name looks like a read helper; maps to
  WORTH_SETUP_OUTPUT_IS_NOT_A_LITERAL, WORTH_IMPORTED_CALL_IS_CODE_UNDER_TEST
- [x] AC-8: a parametrized test is read from its literal table or named as not
  checked, never skipped; the spares read what the author declared, a guard
  beside a read-back spares nothing, and a literal built from literals is a
  literal; maps to WORTH_UNREAD_TEST_IS_NOT_CHECKED,
  WORTH_SPARING_READS_DECLARATIONS_NOT_CONTENT,
  WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK,
  WORTH_LITERAL_BUILT_FROM_LITERALS_IS_A_LITERAL
- [x] AC-9: a security setting gets one verdict whether it is a constant or
  held under a key, and a setUp or describe body that only reads is a read;
  maps to WORTH_SECURITY_KEY_IS_A_DECLARATION,
  WORTH_SETUP_THAT_ONLY_READS_IS_A_READ, WORTH_DESCRIBE_BODY_READ_IS_A_READ
- [x] AC-10: a test keyed by a header-shaped string is spared as a security
  control, and a header-shaped string compared against spares nothing; maps to
  WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION

## 10. Test mapping

(Owned by `tester`.) Each case runs the placed copy over a temp plant that holds
the fixture suite of `tests/fixtures/worth/` under `tests/`, and the verdict each
fixture test is owed is `tests/fixtures/worth/expected.tsv`, written before the
tool. Every row was `red` on the missing tool first. X800 to X806 run the same
copy over the independent tester's tree `tests/fixtures/worth/adversarial/`,
whose verdicts `adversarial.tsv` were written before the tool ran over it; they
were `red` on the heuristic as it stood on 2026-11-10, then green. X810 to
X812 gate the tester's round-two rows on keyed settings, a setUp that only
copies and a read in a describe body, with a plant of further cases in the
test file; they were `red` on the heuristic as it stood on 2026-11-11, then
green. X820 gates the two round-three header rows and twelve cases written
with their verdicts before the run (the rows marked `header-shaped` in
`adversarial.tsv`); ten of the fourteen were `red` on the heuristic as it stood
on 2026-11-11, then green. A row of `known-gaps.tsv` is a documented limit, held at the verdict
that file records.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| WORTH_FLAGS_A_READ_BACK_TEST | X580 every fixture read-back test is flagged; the Python and TypeScript lines, the summary and the closing line | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARES_LOGIC_TESTS | X581 the pattern, condition, precedence, computed-value, written-file and two-homes fixtures are read and spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARES_BUG_REGRESSIONS | X582 the regression fixtures, one with the read-back shape, are spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARES_SECURITY_CONTROLS | X583 the refusal, absence and security-setting fixtures are spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH | X584 a logic-promising name, six assertions, a shared name and a test with no assertion | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_UNREAD_FILE_IS_NOT_CHECKED | X585 a shell and a Go test, and a Python and a TypeScript file that do not parse | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_UNCONFIGURED_PLANT_IS_NAMED | X586 no spec-lint.py, and one with no TEST_GLOBS, each plain, with --json and with --write-baseline | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_KEEP_MARKER_KEEPS_WITH_REASON | X587 a Python and a TypeScript keep line with a reason, and one without | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS | X588 the first write, a run over the baseline, a new read-back test | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_BASELINE_ONLY_SHRINKS | X589 a refused growth leaves the file; shrinkable reported; the shrink written | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_BAD_INPUT_EXITS_2 | X590 unknown option, missing PATH, a non-UTF-8 file, a partial baseline; a PATH narrows the read | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_NEVER_EDITS_A_TEST | X591 the fixture suite's digest before and after every run; the removal plant's digest around --removal-list | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_CHECK_IS_PLACED | X592 a fresh install places the seed's file, which answers --help and reads an empty plant | tests/test-worth-check.sh | integration (temp install) | green |
| WORTH_REMOVAL_LIST_NAMES_EACH_TEST | X600 a design-origin test written now and an older one from the baseline, each with its row and what it leaves without evidence | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS | X601 bug, security control, a legacy row with no origin, no §10 row | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC | X602 --spec narrows to the spec's tests, baseline included; an unknown spec exits 2 | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SETUP_OUTPUT_IS_NOT_A_LITERAL | X800 a file a unittest setUp and a file a beforeAll had the code under test write are read and spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_IMPORTED_CALL_IS_CODE_UNDER_TEST | X801 an imported resolve(), router.match(), router.get() and users.find() are code under test | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_UNREAD_TEST_IS_NOT_CHECKED | X802 a parametrize table and a test.each table read as literals; a computed table, a tagged template and a computed title named and counted as not checked | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARING_READS_DECLARATIONS_NOT_CONTENT | X803 a URL, a hex colour in a comment and in a title, and banner copy about cookies flag; a csrf test spares | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK | X804 is False, toBe(false), a non-empty guard and a truthiness guard beside a read-back flag; a guard alone and a named absence spare | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_LITERAL_BUILT_FROM_LITERALS_IS_A_LITERAL | X805 a concatenated and a joined literal in each language, string methods on a constant, an inline snapshot | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_FLAGS_A_READ_BACK_TEST | X806 every row of adversarial.tsv outside known-gaps.tsv gets the verdict the independent tester owes it | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SECURITY_KEY_IS_A_DECLARATION | X810 the three keyed-setting rows of adversarial.tsv are spared; a setting under a subscript, getattr, a dict or object key, toHaveProperty and a setUp copy gets the constant's verdict; banner copy under a plain key flags in each language | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION | X820 the two round-three X-Frame-Options rows and the X-Content-Type-Options, Referrer-Policy, Permissions-Policy and Cross-Origin-Opener-Policy keys under a subscript, a dict or object key and toHaveProperty, in each language, are spared, as is a constant named for a security header; a header name used as the compared value flags in each language | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SETUP_THAT_ONLY_READS_IS_A_READ | X811 a setUp that copies a constant or reads a file flags; a setUp that also builds, and a class under an unseen base, spare | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_DESCRIBE_BODY_READ_IS_A_READ | X812 a const a describe body read from a file flags; the same read beside a build hook, and one held in a let, spare | tests/test-worth-check.sh | integration (fixture) | green |
| HEURISTIC_SPARES_A_READ_BACK | X806 each documented limit of known-gaps.tsv keeps the verdict that file records, so a fix moves its row | tests/test-worth-check.sh | integration (fixture) | green |
| SECURITY_CONTROL_OUTSIDE_THE_SPARE_IS_FLAGGED | none: a control the spare cannot recognise has no name the check could read; the keep line with its reason is the recovery | none | none | none |
| SETUP_FILE_OUTSIDE_THE_TEST_IS_NOT_READ | none: a runner's configuration is outside the test files the check reads; the keep line is the recovery | none | none | none |
| ADOPTED_SUITE_FLAGS_ON_DAY_ONE | none: graft's baseline step reports the count, and the owner decides on a cleanup | none | none | none |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should an independent tester review the fixture suite? | the fixtures and their verdicts were written by the spawn that built the tool | reviewed on 2026-11-11: the 34 rows of `expected.tsv` hold, and 29 adversarial cases (`tests/fixtures/worth/adversarial.tsv`) found the gaps of the next four rows. Closed on 2026-11-11 for the tool: the adversarial table is gated (X800 to X806), 16 of the 21 rows of `known-gaps.tsv` are fixed, and 5 stay as documented limits in `tests/fixtures/worth/known-gaps.tsv`; the independent tester's sign waits on the tester's re-review. Re-reviewed on 2026-11-11: the 5 limits are honest and §7 names each; 25 round-two cases found 3 new false positives and 2 new false negatives (next row), and the sign stays withheld on the false positives. Fixed on 2026-11-11: the 3 false positives and the 2 false negatives are gated (X810 to X812), and `known-gaps.tsv` holds the 5 first-round limits; the independent tester's sign waits on the tester's re-review of the fix | tester | the tester's re-review of X810 to X812 |
| Should a security setting held under a string key be spared? | `HEADERS["Content-Security-Policy"] == "default-src 'self'"` and `SETTINGS["SESSION_COOKIE_SECURE"] is True` (Python) and the TypeScript header form were flagged, because the security spare read identifiers and never a key, while `SESSION_COOKIE_SECURE is True` is spared in `expected.tsv`: the same control got two verdicts by how it is stored. Two false negatives beside it: a `setUp` that only copies a constant spared the test, and a `readFileSync` in a `describe` body read as logic | closed on 2026-11-11: a string used as a key names a thing and the security spare reads it, while a string compared against is content and never counts (WORTH_SECURITY_KEY_IS_A_DECLARATION, X810); a setUp that only reads binds a read (WORTH_SETUP_THAT_ONLY_READS_IS_A_READ, X811); a const a describe body only reads is a read (WORTH_DESCRIBE_BODY_READ_IS_A_READ, X812). The five rows left `known-gaps.tsv` for the gated table | architect | closed |
| Should a security header whose name holds no security word be spared? | round three of the independent tester's cases: `HEADERS["X-Frame-Options"] == "DENY"` (Python) and `expect(HEADERS["X-Frame-Options"]).toBe("DENY")` (TypeScript) are flagged, while Strict-Transport-Security and Content-Security-Policy keys are spared, because the security spare matches words and X-Frame-Options names none; X-Content-Type-Options and Referrer-Policy fall the same way, so a plant's gate fails on a clickjacking or sniffing control. Both are rows of `known-gaps.tsv`, class false-positive, held at today's verdict so the gate shows a fix | closed on 2026-11-11: a string key shaped like an HTTP header name is a security declaration by its shape, and the standard security header names join the vocabulary for identifiers (WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION, X820); the two rows left `known-gaps.tsv` for the gated table. The spare stays a heuristic with edges, and §7 names the residual risk (SECURITY_CONTROL_OUTSIDE_THE_SPARE_IS_FLAGGED) | architect | closed |
| Should the security vocabulary name roles, allow-lists, origins, lockouts and JWT? | round four of the independent tester's cases: `ROLE_REQUIRED["/billing"] == "owner"`, `LOCKOUT_THRESHOLD == 5`, `ALLOWED_ORIGINS`, `ALLOWED_HOSTS` membership and `JWT_ALGORITHMS == ["RS256"]`, in Python and TypeScript (9 cases), are flagged: settings named for their effect, whose words are outside the spare's vocabulary. They are the vocabulary edge SECURITY_CONTROL_OUTSIDE_THE_SPARE_IS_FLAGGED names, kept with a keep line and its reason, and rows of `known-gaps.tsv`; they do not block the tester's sign | flagged; kept by a keep line | architect | the words role, lockout, origin, allow-list and jwt join the vocabulary, or the limit stays as §7 states it |
| Should a test that reads a file a setup hook had the code under test write be spared? | WORTH_SPARES_LOGIC_TESTS spares a test that reads a file the code under test wrote, yet a setup hook that calls the build was not read, so the test was flagged: a false positive | closed on 2026-11-11: setup hooks are read as logic (WORTH_SETUP_OUTPUT_IS_NOT_A_LITERAL, X800). A setup file named only in the runner's configuration stays a limit (SETUP_FILE_OUTSIDE_THE_TEST_IS_NOT_READ) | architect | closed |
| Should a TypeScript call into the code under test whose name is a read helper be spared? | an imported `resolve(...)` read as `path.resolve`, and `match` on an imported object as `String.match`: two false positives | closed on 2026-11-11: an imported name is code under test unless its module is a Node built-in, and a string method reads only a value already read or an upper-case imported constant (WORTH_IMPORTED_CALL_IS_CODE_UNDER_TEST, X801) | architect | closed |
| Should `test.each` and `it.each` be read, or named as not read? | a parametrized TypeScript test was skipped with nothing in the report | closed on 2026-11-11: a literal table is read, any other table and a computed title are listed and counted as not checked, in both languages (WORTH_UNREAD_TEST_IS_NOT_CHECKED, X802) | architect | closed |
| Should the sparing heuristics narrow? | any `False`/`None`/`false` literal, one `!=` guard beside a read-back, the word `https` or `cookies` in a literal, a hex colour that matches `#<digits>`, and the word regression in a name each spared a plain read-back | closed on 2026-11-11 for all but the name: the spares read declarations, never literals (X803); a guard spares nothing beside a read-back and a `False` literal is a literal (X804); a literal built from literals is one (X805). Left as limits under HEURISTIC_SPARES_A_READ_BACK, each a row of `known-gaps.tsv`: a name that says regression (the contract spares a name), a helper's assertion, a golden file, a snapshot file and a snapshot fixture | architect | closed |
| Should a later language be read, shell first? | D4 reads Python and TypeScript or JavaScript only | every other language is listed as not checked | owner | a plant that needs it, named by the owner |

## 12. Changelog

- 2026-11-10 — created by `architect` from the round's surface definition of the
  worth check and the owner's decisions of 2026-11-10 (languages read; the
  baseline of a grafted plant decided per plant). Thirteen contracts; the
  fixture suite and its verdict table written first, every case seen failing on
  the missing tool, then green with the tool, the placement and the gate row.
- 2026-11-10 — three contracts added by the implementer of step T11 (ADR-0034
  OD3 and the owner's clean-as-you-touch decision of 2026-11-10): the removal
  list, the kinds it holds back, and its narrowing to a reopened spec;
  WORTH_NEVER_EDITS_A_TEST now covers `--removal-list`. X600 to X602 were seen
  failing on the unknown option first, then green.
- 2026-11-10: graft records the baseline once (D5, T12) instead of listing a judgment item, and `graft-graph-engine.py` keeps `SKIP_DIRS`; the two lines that said otherwise are corrected in place.
- 2026-11-11 — an independent tester reviewed `tests/fixtures/worth/`, its
  verdict table, `tools/worth-check.py` and every §10 case of
  `tests/test-worth-check.sh`. The 34 hand-written verdicts hold. The tester
  wrote 29 adversarial cases with their verdicts before running the tool
  (`tests/fixtures/worth/adversarial/` and `adversarial.tsv`, outside the
  gate): 9 match, 4 are false positives against WORTH_SPARES_LOGIC_TESTS, 15
  are false negatives and 1 is a test the reader skips, each in
  `tests/fixtures/worth/known-gaps.tsv`. The independent tester's sign is
  withheld until §11's false positives are ruled on; the sign-offs of
  2026-11-10 stay as their authors gave them.
- 2026-11-11 — the worth check fixed against the independent review. Six
  contracts added (WORTH_SETUP_OUTPUT_IS_NOT_A_LITERAL,
  WORTH_IMPORTED_CALL_IS_CODE_UNDER_TEST, WORTH_UNREAD_TEST_IS_NOT_CHECKED,
  WORTH_SPARING_READS_DECLARATIONS_NOT_CONTENT,
  WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK,
  WORTH_LITERAL_BUILT_FROM_LITERALS_IS_A_LITERAL), WORTH_SPARES_BUG_REGRESSIONS
  and WORTH_SPARES_SECURITY_CONTROLS restated in place (markers count; `is
  False` and a bare `!=` no longer spare), the failure mode
  SETUP_FILE_OUTSIDE_THE_TEST_IS_NOT_READ added, and
  HEURISTIC_SPARES_A_READ_BACK widened to name each limit left. The adversarial
  table is now gated: X800 to X806 were seen failing on the heuristic as it
  stood, then green. `known-gaps.tsv` held 21 rows, one more than the entry
  above counts (16 false negatives, not 15): the 4 false positives, the silent
  skip and 11 of the 16 false negatives are fixed, 5 stay as limits in
  `known-gaps.tsv`, and 24 of the 29 adversarial rows are gated at the verdict
  the tester owes them. The 34 rows of `expected.tsv` pass unchanged. The owner decided on 2026-11-11 that
  the check keeps Python and TypeScript or JavaScript only.
- 2026-11-11 — the independent tester re-reviewed the reworked tool. The 29
  first-round cases hold as gated, and the 5 limits are honest and named in
  §7. The tester wrote 25 round-two cases with their verdicts before the run
  (`tests/fixtures/worth/adversarial/`, rows marked `round 2` in
  `adversarial.tsv`): setup hooks of every kind, parametrized tables, local
  factories, absences and refusals without a security word, keyed settings.
  Twenty match. Three are false positives, a security setting held under a
  string key, and two are false negatives; the five are rows of
  `known-gaps.tsv` and the question of §11. The independent tester's sign is
  withheld until the false positives are ruled on.
- 2026-11-11 — the round-two findings fixed. A string the test uses as a key
  (a subscript, a dict or object key, the name `.get`, `getattr` or
  `toHaveProperty` reads) names a thing, so the security spare reads it as it
  reads an identifier; a string compared against stays content and spares
  nothing. A setUp that only binds attributes to values it reads, and a const a
  describe body only reads, are reads; any code they run keeps them logic.
  Three contracts added (WORTH_SECURITY_KEY_IS_A_DECLARATION,
  WORTH_SETUP_THAT_ONLY_READS_IS_A_READ, WORTH_DESCRIBE_BODY_READ_IS_A_READ),
  WORTH_SPARES_SECURITY_CONTROLS and WORTH_SPARING_READS_DECLARATIONS_NOT_CONTENT
  restated in place to name keys, HEURISTIC_SPARES_A_READ_BACK widened to a key
  that names a security subject for an unrelated reason and a setup that runs
  code beside its read. The 3 false positives and 2 false negatives moved from
  `known-gaps.tsv` to the gated table: X810 to X812 were seen failing on the
  heuristic as it stood, then green. All 54 rows of `adversarial.tsv` but the
  5 first-round limits are gated, and the 34 rows of `expected.tsv` pass
  unchanged. The independent tester's sign waits on the tester's re-review.
- 2026-11-11 — the independent tester's third pass. Twenty round-three cases
  with verdicts written before the run (rows marked `round 3` in
  `adversarial.tsv`): keys nested, read through `.get`, `Map.get` and a named
  constant, lower-case imports, security words in keys against words in
  values, an absent key, and setup through `asyncSetUp`, `setup_method`,
  `setup_class`, a `conftest.py` autouse fixture, a `beforeAll` inside a
  `describe` and a `node:test` `before`. Eighteen match. Two are false
  positives, the X-Frame-Options header in Python and TypeScript, rows of
  `known-gaps.tsv` and the question of §11. The independent tester's sign
  stays withheld until it is ruled on.
- 2026-11-11 — the round-three finding fixed by one rule rather than a longer
  word list: a string key shaped like an HTTP header name (capitalised words
  joined by hyphens) is a security declaration, and the standard security
  response header names (X-Frame-Options, X-Content-Type-Options,
  Strict-Transport-Security, Referrer-Policy, Permissions-Policy, the
  Cross-Origin policies) join the vocabulary read over identifiers. The rule
  is conservative: a plain header read-back under such a key is spared too.
  Contract WORTH_HEADER_NAME_KEY_IS_A_SECURITY_DECLARATION added (X820),
  WORTH_SPARES_SECURITY_CONTROLS restated in place to name it,
  HEURISTIC_SPARES_A_READ_BACK widened to a header-keyed read-back, and the
  failure mode SECURITY_CONTROL_OUTSIDE_THE_SPARE_IS_FLAGGED added: the spare
  is a vocabulary-and-declaration heuristic, and a security test it misses is
  kept with a keep line and its reason. The two false positives moved from
  `known-gaps.tsv` to the gated table beside twelve new cases whose verdicts
  were written before the run (four were reshaped after the first run, their
  verdicts unchanged, so that each reaches the key rather than a `.get` call
  read as code under test); ten of the fourteen were seen failing on the
  heuristic as it stood, then green. Every row of `adversarial.tsv` but the 5
  first-round limits is gated, and the rows of `expected.tsv` pass unchanged.
  The independent tester's sign waits on the tester's re-review.
- 2026-11-11 — the independent tester's fourth pass, and the tester's sign
  in §0. Twenty round-four cases with verdicts written first (rows marked
  `round 4` in `adversarial.tsv`): token length, role comparison, rate limit,
  lockout threshold, password-hash prefix, CORS origin list, host allow-list
  membership and absence, redirect target, CSRF cookie name and JWT algorithm
  allow-list, in Python and TypeScript. Eleven match, the computed, refused,
  absent and vocabulary-named controls among them. Nine are flagged: settings
  named for their effect whose words (role, lockout, origins, allowed, jwt)
  are outside the vocabulary, the edge §7 names with its keep-line remedy.
  They are listed as limits in `known-gaps.tsv` and §11 and do not block the
  sign. No false positive was found on a test whose shape declares security.
