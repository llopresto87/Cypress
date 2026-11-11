#!/usr/bin/env bash
# test-worth-check.sh — tools/worth-check.py, placed in a plant as
# docs/graph/worth-check.py (SPEC-0009): it flags a test whose only assertions
# read back a literal the same change adds, and spares a test that feeds inputs
# to logic, a bug regression and a security negative control. Each case runs
# the copy one fresh install placed, over a temp plant that holds the fixture
# suite of tests/fixtures/worth/ under tests/; the verdict each fixture test is
# owed is tests/fixtures/worth/expected.tsv, written by hand before the tool.
# X800 to X806 add an independent tester's adversarial tree and its verdict
# table (adversarial.tsv), with the documented limits of known-gaps.tsv held at
# the verdict that file records; X810 to X812 gate the tester's round-two rows
# on keyed security settings, a setUp that only reads and a read in a describe
# body, each with a plant of its own cases besides. The check never runs over this repository's own suite, whose tests assert
# documentation text on purpose.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
FX="$ROOT/tests/fixtures/worth"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0; ok() { echo "  $1 — OK"; }; bad() { echo "  $1 — FAIL: $2"; fail=1; }

mkdir "$T/base"
bash "$ROOT/install.sh" claude-code --project-dir "$T/base" >/dev/null 2>&1 || true
W="$T/base/docs/graph/worth-check.py"
NOT_CONFIGURED='worth-check: not configured for this plant (set TEST_GLOBS in docs/graph/spec-lint.py)'

# A plant: the fixture suite under tests/ and a spec-lint.py that declares it.
plant() {
  mkdir -p "$1/docs/graph" "$1/tests"
  cp -R "$FX/python" "$FX/ts" "$FX/js" "$FX/other" "$1/tests/"
  printf 'TEST_GLOBS = ["tests/**/*.*"]\nSKIP_DIRS = {".git", "node_modules"}\n' > "$1/docs/graph/spec-lint.py"
}
WC() { local d="$1"; shift; (cd "$d" && "$PY" "$W" "$@"); }
digest() { "$PY" -c 'import hashlib,pathlib,sys
h = hashlib.sha256()
for p in sorted(pathlib.Path(sys.argv[1]).rglob("*")):
    if p.is_file():
        h.update(str(p).encode()); h.update(p.read_bytes())
print(h.hexdigest())' "$1"; }

# X592 WORTH_CHECK_IS_PLACED
if [[ -f "$W" ]] && cmp -s "$ROOT/tools/worth-check.py" "$W"; then
  rc=0; out="$(cd "$T/base" && "$PY" docs/graph/worth-check.py --help 2>&1)" || rc=$?
  [[ $rc -eq 0 ]] && grep -q 'worth-check: keep' <<<"$out" && grep -q 'verification' <<<"$out" \
    && ok "X592 WORTH_CHECK_IS_PLACED: docs/graph/worth-check.py is the seed's file and answers --help" \
    || bad "X592 WORTH_CHECK_IS_PLACED" "--help rc $rc: ${out:0:300}"
  rc=0; out="$(cd "$T/base" && "$PY" docs/graph/worth-check.py 2>&1)" || rc=$?
  [[ $rc -eq 0 ]] && grep -q '^worth-check: 0 flagged (0 in baseline), 0 files read, 0 not checked' <<<"$out" \
    && ok "X592 WORTH_CHECK_IS_PLACED: a fresh plant with no tests reads nothing and passes" \
    || bad "X592 WORTH_CHECK_IS_PLACED" "fresh plant rc $rc: ${out:0:300}"
else
  bad "X592 WORTH_CHECK_IS_PLACED" "the install placed no docs/graph/worth-check.py equal to tools/worth-check.py"
fi
[[ -f "$W" ]] || W="$ROOT/tools/worth-check.py"

# SPEC-0008 X603 WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING: the installed
# tester and implementer point at the removal section, and the pointer
# resolves to a section of the installed protocol that holds each rule.
TF="$T/base/docs/graph/protocols/test-first.md"
sect="$(awk '/^### Removing a test that catches nothing$/{on=1;next} on&&/^##/{exit} on' "$TF" 2>/dev/null | tr '\n' ' ' | tr -s ' ')"
missing=""
for a in 02-implementer 04-tester; do
  tr '\n' ' ' < "$T/base/.claude/agents/$a.md" 2>/dev/null | tr -s ' ' | grep -qF '(`protocol.test-first`, Removing a test)' || missing="$missing $a-pointer"
done
for want in 'class of worker that wrote it' 'removed: <reason>' 'settles that contract'"'"'s kind again' \
            'confirms its removal in the chat with a reply that names it (kernel §4)' '--removal-list' \
            'A reopened spec' '--spec SPEC-NNNN' '`bug`, a security control, and a test no §10 row maps' \
            'kills no mutant is a finding for `security`' 'Graft and grow leave every test in place'; do
  grep -qF -- "$want" <<<"$sect" || missing="$missing [$want]"
done
[[ -z "$missing" ]] \
  && ok "X603 WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING: the installed charters point at the removal section, which holds each rule" \
  || bad "X603 WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING" "missing:$missing"

# SPEC-0008 X604 MUTATION_PASS_REPORTS_EACH_TEST: the installed mutation-at-end
# section asks for a line per test and keeps the classes it is mandatory for.
mut="$(awk '/delegation.mutation-at-end`\)$/{on=1;next} on&&/^## /{exit} on' "$T/base/docs/graph/method/delegation-cycle-economy.md" 2>/dev/null | tr '\n' ' ' | tr -s ' ')"
grep -qF 'one line per test of the spec it covers, `killed <path::name>` or `survived-all <path::name>`' <<<"$mut" \
  && grep -qF 'It is mandatory for security, data-integrity and money contracts' <<<"$mut" \
  && grep -qF 'Elsewhere mutation runs only on a named sample the owner adds' <<<"$mut" \
  && ok "X604 MUTATION_PASS_REPORTS_EACH_TEST: the pass reports killed or survived-all per test, mandatory where it was and nowhere else" \
  || bad "X604 MUTATION_PASS_REPORTS_EACH_TEST" "section: ${mut:0:400}"

P="$T/p"; plant "$P"
BEFORE="$(digest "$P/tests")"

# X580 to X584: every fixture test gets the verdict expected.tsv owes it, and
# every one of them is read (a spared test is a test that was read).
rc=0; WC "$P" --json >"$T/report.json" 2>"$T/json.err" || rc=$?
verdicts="$("$PY" - "$FX/expected.tsv" "$T/report.json" 2>&1 <<'PY' || true
import json, sys
try:
    report = json.load(open(sys.argv[2], encoding="utf-8"))
except ValueError as e:
    print(f"JSON\tnone\tnone\tthe --json report does not parse: {e}"); sys.exit(0)
got = {t["test"]: t["verdict"] for t in report.get("tests", [])}
for line in open(sys.argv[1], encoding="utf-8"):
    if line.startswith("#") or not line.strip():
        continue
    test, verdict, what = line.rstrip("\n").split("\t")
    have = got.get(test, "not read")
    print(f"{'OK' if have == verdict else 'BAD'}\t{verdict}\t{what}\t{test}: owed {verdict}, got {have}")
PY
)"
check_kind() {   # label contract verdict pattern-on-what
  local rows; rows="$(awk -F'\t' -v v="$3" -v k="$4" '($2 == v || v == "any" || $1 == "JSON") && $3 ~ k' <<<"$verdicts")"
  if [[ -z "$rows" ]] || grep -q '^BAD\|^JSON' <<<"$rows"; then
    bad "$1 $2" "$(grep -v '^OK' <<<"${rows:-JSON	none	none	no fixture row matched $4}" | cut -f4 | tr '\n' ';')"
  else
    ok "$1 $2: $(wc -l <<<"$rows" | tr -d ' ') fixture test(s) get the verdict expected.tsv owes ($4)"
  fi
}
check_kind X580 WORTH_FLAGS_A_READ_BACK_TEST flagged '.'
check_kind X581 WORTH_SPARES_LOGIC_TESTS spared 'pattern|condition|precedence|computed|wrote|rendered|two homes'
check_kind X582 WORTH_SPARES_BUG_REGRESSIONS spared 'regression'
check_kind X583 WORTH_SPARES_SECURITY_CONTROLS spared 'security'
check_kind X584 WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH any 'promises logic|length is no criterion|same name|same title'
[[ $rc -eq 1 ]] && ok "X580 WORTH_FLAGS_A_READ_BACK_TEST: --json exits 1 on flagged tests outside a baseline" \
  || bad "X580 WORTH_FLAGS_A_READ_BACK_TEST" "--json exit $rc, owed 1: $(head -c 300 "$T/json.err")"

# X580: the line a reader acts on names the test, why, and what to do.
rc=0; out="$(WC "$P" 2>&1)" || rc=$?
line="$(grep -F 'tests/python/test_readback.py::test_page_carries_the_label  ' <<<"$out" || true)"
want='tests/python/test_readback.py::test_page_carries_the_label  reads back "value=\"Send\"" that the same file/change adds; only assertion(s): 1; keep it with a line "# worth-check: keep — <reason>" above the test if it earns its place'
[[ $rc -eq 1 && "$line" == "$want" ]] \
  && ok "X580 WORTH_FLAGS_A_READ_BACK_TEST: the Python line names the test, the literal, the count and the keep line" \
  || bad "X580 WORTH_FLAGS_A_READ_BACK_TEST" "rc $rc; line: ${line:-none}"
grep -qF 'tests/ts/readback.test.ts::names the route  reads back /\/submit/, "submit_form" that the same file/change adds; only assertion(s): 2; keep it with a line "// worth-check: keep — <reason>" above the test if it earns its place' <<<"$out" \
  && ok "X580 WORTH_FLAGS_A_READ_BACK_TEST: the TypeScript line carries the language's comment syntax" \
  || bad "X580 WORTH_FLAGS_A_READ_BACK_TEST" "no TypeScript line for 'names the route': $(grep -F 'names the route' <<<"$out" || echo none)"
grep -qx 'worth-check: 9 flagged (0 in baseline), 9 files read, 2 not checked (languages: go, shell)' <<<"$out" \
  && grep -q '^worth-check: FAIL — 9 flagged test(s) are not in the baseline.*remove.*inputs.*keep' <<<"$out" \
  && ok "X580 WORTH_FLAGS_A_READ_BACK_TEST: the summary counts and the failing line says what to do" \
  || bad "X580 WORTH_FLAGS_A_READ_BACK_TEST" "summary/footer: $(tail -3 <<<"$out")"

# X584: a test with no assertion is never flagged; it is reported as read.
mkdir -p "$T/q"; plant "$T/q"; rm -rf "$T/q/tests/"*
printf 'from app import LABEL\n\n\ndef test_label_is_imported():\n    LABEL\n' > "$T/q/tests/test_bare.py"
rc=0; out="$(WC "$T/q" 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -qx 'worth-check: 0 flagged (0 in baseline), 1 files read, 0 not checked' <<<"$out" \
  && ok "X584 WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH: a test with no assertion to read is not flagged" \
  || bad "X584 WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH" "rc $rc: $out"

# X585 WORTH_UNREAD_FILE_IS_NOT_CHECKED
rc=0; out="$(WC "$P" 2>&1)" || rc=$?
grep -qx 'tests/other/test_cli.sh  not checked (shell)' <<<"$out" \
  && grep -qx 'tests/other/label_test.go  not checked (go)' <<<"$out" \
  && ! grep -qi 'clean' <<<"$out" \
  && ok "X585 WORTH_UNREAD_FILE_IS_NOT_CHECKED: a shell and a Go test are listed as not checked, and nothing says clean" \
  || bad "X585 WORTH_UNREAD_FILE_IS_NOT_CHECKED" "$(grep -i 'not checked\|clean' <<<"$out" | head -5)"
mkdir -p "$T/r"; plant "$T/r"; rm -rf "$T/r/tests/"*
printf 'def test_broken(:\n    assert X == 1\n' > "$T/r/tests/test_broken.py"
printf 'test("unclosed", () => {\n  expect(LABEL).toBe("x");\n' > "$T/r/tests/open.test.ts"
rc=0; out="$(WC "$T/r" 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -q '^tests/test_broken.py  not checked (python: does not parse at line 1' <<<"$out" \
  && grep -q '^tests/open.test.ts  not checked (typescript: ' <<<"$out" \
  && grep -qx 'worth-check: 0 flagged (0 in baseline), 0 files read, 2 not checked (languages: python, typescript)' <<<"$out" \
  && ! grep -qi 'clean' <<<"$out" \
  && ok "X585 WORTH_UNREAD_FILE_IS_NOT_CHECKED: a file that does not parse is not checked, never read" \
  || bad "X585 WORTH_UNREAD_FILE_IS_NOT_CHECKED" "rc $rc: $out"

# X586 WORTH_UNCONFIGURED_PLANT_IS_NAMED
mkdir -p "$T/u1/tests" "$T/u2/docs/graph"; cp "$FX/python/test_readback.py" "$T/u1/tests/"
printf '# a plant engine whose test layout is not declared\nROOT_ID = "x"\n' > "$T/u2/docs/graph/spec-lint.py"
for u in u1 u2; do
  for args in "" "--json" "--write-baseline"; do
    rc=0; out="$(WC "$T/$u" $args 2>&1)" || rc=$?
    if [[ $rc -eq 0 ]] && grep -qF "$NOT_CONFIGURED" <<<"$out" && ! grep -qi 'clean' <<<"$out" \
       && [[ ! -e "$T/$u/docs/graph/worth-baseline.txt" ]]; then :; else
      bad "X586 WORTH_UNCONFIGURED_PLANT_IS_NAMED" "$u ${args:-plain}: rc $rc: $out"; continue 2
    fi
  done
  ok "X586 WORTH_UNCONFIGURED_PLANT_IS_NAMED: $u prints the not-configured line, exits 0 and writes nothing"
done

# X587 WORTH_KEEP_MARKER_KEEPS_WITH_REASON
K="$T/k"; plant "$K"; rm -rf "$K/tests/"*
cat > "$K/tests/test_kept.py" <<'EOF'
from app.settings import SUBMIT_LABEL, CANCEL_LABEL


# worth-check: keep — the label is a contract with the mobile client, which ships separately
def test_label_contract():
    assert SUBMIT_LABEL == "Send"


# worth-check: keep
def test_cancel_label():
    assert CANCEL_LABEL == "Cancel"
EOF
cat > "$K/tests/kept.test.ts" <<'EOF'
import { SUBMIT_LABEL } from "../src/labels";
// worth-check: keep — the partner portal scrapes this label
test("label contract", () => {
  expect(SUBMIT_LABEL).toBe("Send");
});
EOF
rc=0; out="$(WC "$K" 2>&1)" || rc=$?
[[ $rc -eq 1 ]] \
  && grep -qx 'worth-check: kept: tests/test_kept.py::test_label_contract — the label is a contract with the mobile client, which ships separately' <<<"$out" \
  && grep -qx 'worth-check: kept: tests/kept.test.ts::label contract — the partner portal scrapes this label' <<<"$out" \
  && grep -q '^tests/test_kept.py::test_cancel_label  reads back "Cancel"' <<<"$out" \
  && grep -q 'tests/test_kept.py::test_cancel_label.*keep line gives no reason' <<<"$out" \
  && ok "X587 WORTH_KEEP_MARKER_KEEPS_WITH_REASON: a keep line with a reason keeps the test and prints it; one without a reason keeps nothing" \
  || bad "X587 WORTH_KEEP_MARKER_KEEPS_WITH_REASON" "rc $rc: $out"

# X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS
B="$T/b"; plant "$B"
rc=0; out="$(WC "$B" --write-baseline 2>&1)" || rc=$?
n="$(grep -cv '^#' "$B/docs/graph/worth-baseline.txt" 2>/dev/null || true)"
[[ $rc -eq 0 && "$n" == 9 ]] && grep -qx 'tests/python/test_readback.py::TestFooterCopy::test_footer_text' "$B/docs/graph/worth-baseline.txt" \
  && ok "X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS: the first --write-baseline records today's 9 flags" \
  || bad "X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS" "rc $rc, $n entries: $out"
rc=0; out="$(WC "$B" 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -qx 'worth-check: 9 flagged (9 in baseline), 9 files read, 2 not checked (languages: go, shell)' <<<"$out" \
  && ok "X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS: tests in the baseline are reported and do not fail" \
  || bad "X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS" "rc $rc: $(tail -3 <<<"$out")"
printf '\n\ndef test_new_banner():\n    assert SUBMIT_LABEL == "Submit now"\n' >> "$B/tests/python/test_readback.py"
rc=0; out="$(WC "$B" 2>&1)" || rc=$?
[[ $rc -eq 1 ]] && grep -q '^tests/python/test_readback.py::test_new_banner  reads back "Submit now"' <<<"$out" \
  && grep -qx 'worth-check: 10 flagged (9 in baseline), 9 files read, 2 not checked (languages: go, shell)' <<<"$out" \
  && ok "X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS: a new read-back test outside the baseline fails" \
  || bad "X588 WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS" "rc $rc: $(tail -4 <<<"$out")"

# X589 WORTH_BASELINE_ONLY_SHRINKS
cp "$B/docs/graph/worth-baseline.txt" "$T/baseline.before" 2>/dev/null || : > "$T/baseline.before"
rc=0; out="$(WC "$B" --write-baseline 2>&1)" || rc=$?
[[ $rc -eq 1 ]] && cmp -s "$T/baseline.before" "$B/docs/graph/worth-baseline.txt" \
  && grep -q 'refused' <<<"$out" && grep -q 'test_new_banner' <<<"$out" \
  && ok "X589 WORTH_BASELINE_ONLY_SHRINKS: --write-baseline refuses to add a test and leaves the file as it was" \
  || bad "X589 WORTH_BASELINE_ONLY_SHRINKS" "rc $rc: $out"
"$PY" - "$B/tests/python/test_readback.py" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.split("\n\ndef test_new_banner")[0] + "\n"
s = s.replace('    assert SUBMIT_LABEL == "Send"\n', '    assert SUBMIT_LABEL != ""\n')
open(p, "w", encoding="utf-8").write(s)
PY
rc=0; out="$(WC "$B" 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -q '^worth-check: shrinkable: tests/python/test_readback.py::test_submit_button_label_is_send ' <<<"$out" \
  && ok "X589 WORTH_BASELINE_ONLY_SHRINKS: an entry that no longer flags is reported as shrinkable" \
  || bad "X589 WORTH_BASELINE_ONLY_SHRINKS" "rc $rc: $out"
rc=0; out="$(WC "$B" --write-baseline 2>&1)" || rc=$?
n="$(grep -cv '^#' "$B/docs/graph/worth-baseline.txt" || true)"
[[ $rc -eq 0 && "$n" == 8 ]] && ! grep -q 'test_submit_button_label_is_send' "$B/docs/graph/worth-baseline.txt" \
  && ok "X589 WORTH_BASELINE_ONLY_SHRINKS: --write-baseline shrinks the baseline to 8" \
  || bad "X589 WORTH_BASELINE_ONLY_SHRINKS" "rc $rc, $n entries: $out"

# X590 WORTH_BAD_INPUT_EXITS_2
rc=0; out="$(WC "$P" --frobnicate 2>&1)" || rc=$?
[[ $rc -eq 2 ]] && grep -q 'frobnicate' <<<"$out" \
  && ok "X590 WORTH_BAD_INPUT_EXITS_2: an unknown option exits 2 and names it" || bad "X590 WORTH_BAD_INPUT_EXITS_2" "unknown option rc $rc: $out"
rc=0; out="$(WC "$P" tests/no-such-dir 2>&1)" || rc=$?
[[ $rc -eq 2 ]] && grep -q 'tests/no-such-dir' <<<"$out" && grep -q 'does not exist' <<<"$out" \
  && ok "X590 WORTH_BAD_INPUT_EXITS_2: a PATH that does not exist exits 2 and names it" || bad "X590 WORTH_BAD_INPUT_EXITS_2" "missing path rc $rc: $out"
X="$T/x"; plant "$X"; printf 'def test_x():\n    assert A == "\xff\xfe"\n' > "$X/tests/test_latin.py"
rc=0; out="$(WC "$X" 2>&1)" || rc=$?
[[ $rc -eq 2 ]] && grep -q 'tests/test_latin.py' <<<"$out" && grep -q 'UTF-8' <<<"$out" \
  && ok "X590 WORTH_BAD_INPUT_EXITS_2: a test file that is not UTF-8 exits 2 with its path and reason" || bad "X590 WORTH_BAD_INPUT_EXITS_2" "undecodable rc $rc: $out"
printf 'tests/a.py::t\n' > "$X/docs/graph/worth-baseline.txt"
rc=0; out="$(WC "$X" tests/python --write-baseline 2>&1)" || rc=$?
[[ $rc -eq 2 ]] && grep -q 'write-baseline' <<<"$out" \
  && ok "X590 WORTH_BAD_INPUT_EXITS_2: --write-baseline over a part of the suite is refused" || bad "X590 WORTH_BAD_INPUT_EXITS_2" "partial baseline rc $rc: $out"
rc=0; out="$(WC "$P" tests/python/test_logic.py 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -qx 'worth-check: 0 flagged (0 in baseline), 1 files read, 0 not checked' <<<"$out" \
  && ok "X590 WORTH_BAD_INPUT_EXITS_2: a PATH narrows the read to that file" || bad "X590 WORTH_BAD_INPUT_EXITS_2" "PATH rc $rc: $out"

# X600 to X602: --removal-list prints the batch the owner confirms by naming it.
# The plant: five read-back tests, one of them older (in the baseline), mapped
# by two specs' §10 rows of origin design, bug and security control, and one
# test no row maps; a sixth flagged test, in the baseline, belongs to SPEC-0013.
R="$T/rm"; plant "$R"; rm -rf "$R/tests/"*; mkdir -p "$R/docs/graph/specs"
cat > "$R/tests/test_removal.py" <<'EOF'
from app.labels import SUBMIT_LABEL, CANCEL_LABEL, RETRY_LABEL, TITLE, FOOTER


def test_label_is_send():
    assert SUBMIT_LABEL == "Send"


def test_cancel_label():
    assert CANCEL_LABEL == "Cancel"


def test_retry_label():
    assert RETRY_LABEL == "Retry"


def test_title_text():
    assert TITLE == "Welcome"


def test_footer_text():
    assert FOOTER == "Shop"
EOF
printf 'from app.labels import BANNER\n\n\ndef test_banner():\n    assert BANNER == "Hello"\n' > "$R/tests/test_other.py"
cat > "$R/docs/graph/specs/SPEC-0012-submit.md" <<'EOF'
---
status: implemented
---
# SPEC-0012: submit

## 0. Metadata

- **Contract form:** kinds

## 4. Functional contracts

### Contract: SUBMIT_BUTTON_LABEL_IS_SEND
- **Check:** test

### Contract: CANCEL_LABEL_IS_CANCEL
- **Check:** test

### Contract: RETRY_LABEL_IS_SHOWN
- **Check:** test

### Contract: TITLE_IS_WELCOME
- **Check:** test

## 10. Test design

| Risk (what breaks, for whom) | Test (file::name, lowest level) | Covers | Origin | Status |
|---|---|---|---|---|
| Cosmetic label on the submit button | tests/test_removal.py::test_label_is_send | SUBMIT_BUTTON_LABEL_IS_SEND | design | green |
| The cancel label | tests/test_removal.py::test_cancel_label | CANCEL_LABEL_IS_CANCEL | design | green |
| The cancel flow end to end | tests/e2e/cancel_test.py::test_cancel_flow | CANCEL_LABEL_IS_CANCEL | design | green |
| The retry label vanished once and customers could not retry | tests/test_removal.py::test_retry_label | RETRY_LABEL_IS_SHOWN | bug | green |
| A forged title passes the header check | tests/test_removal.py::test_title_text | TITLE_IS_WELCOME | security control | green |

## 11. Open questions
EOF
cat > "$R/docs/graph/specs/SPEC-0013-banner.md" <<'EOF'
---
status: implemented
---
# SPEC-0013: banner

## 4. Functional contracts

### Contract: BANNER_SAYS_HELLO

## 10. Test mapping

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| BANNER_SAYS_HELLO | test_banner | tests/test_other.py | unit | green |
EOF
printf '# baseline\ntests/test_removal.py::test_cancel_label\ntests/test_other.py::test_banner\n' > "$R/docs/graph/worth-baseline.txt"
RBEFORE="$(digest "$R")"
rc=0; out="$(WC "$R" --removal-list 2>&1)" || rc=$?
e1="$(grep -A3 -F '. tests/test_removal.py::test_label_is_send' <<<"$out" || true)"
[[ $rc -eq 0 ]] \
  && grep -qx 'removal batch — 6 test(s) for the owner'"'"'s confirmation (nothing is removed by this list)' <<<"$out" \
  && grep -q '^ *[0-9]\. tests/test_removal.py::test_label_is_send$' <<<"$e1" \
  && grep -q '^    flagged: only assertion reads back "Send" that the same change adds (worth-check)$' <<<"$e1" \
  && grep -q '^    §10 row: SPEC-0012 "Cosmetic label on the submit button" origin: design *-> removable on confirmation$' <<<"$e1" \
  && grep -q '^    leaves without evidence: SUBMIT_BUTTON_LABEL_IS_SEND (kind test; the architect re-settles its kind)$' <<<"$e1" \
  && grep -q '^To confirm, reply in the chat naming the tests to remove, e.g. "remove tests 1 and 4 of the batch".$' <<<"$out" \
  && ok "X600 WORTH_REMOVAL_LIST_NAMES_EACH_TEST: a design-origin test names why it is flagged, its §10 row and origin, and the contract it leaves without evidence" \
  || bad "X600 WORTH_REMOVAL_LIST_NAMES_EACH_TEST" "rc $rc: $out"
e2="$(grep -A3 -F '. tests/test_removal.py::test_cancel_label' <<<"$out" || true)"
grep -q '^    flagged: .*(worth-check; in the baseline)$' <<<"$e2" \
  && grep -q 'origin: design *-> removable on confirmation$' <<<"$e2" \
  && grep -q '^    leaves without evidence: none' <<<"$e2" \
  && ok "X600 WORTH_REMOVAL_LIST_NAMES_EACH_TEST: an older test from the baseline is listed, and a contract another row still covers is not left without evidence" \
  || bad "X600 WORTH_REMOVAL_LIST_NAMES_EACH_TEST" "older test: ${e2:-not listed}"
for pair in 'test_retry_label|origin: bug *-> NOT REMOVABLE AUTOMATICALLY (a bug reproduction stays)$' \
            'test_title_text|origin: security control *-> NOT REMOVABLE AUTOMATICALLY (a security control; one that kills no mutant is a finding for the security agent)$' \
            'test_footer_text|^    no §10 row -> NOT REMOVABLE AUTOMATICALLY'; do
  t="${pair%%|*}"; want="${pair#*|}"
  e="$(grep -A3 -F ". tests/test_removal.py::$t" <<<"$out" || true)"
  grep -q "$want" <<<"$e" \
    && ok "X601 WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS: $t" \
    || bad "X601 WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS" "$t: ${e:-not listed}"
done
e6="$(grep -A3 -F '. tests/test_other.py::test_banner' <<<"$out" || true)"
grep -q 'SPEC-0013 "BANNER_SAYS_HELLO" origin: not recorded *-> NOT REMOVABLE AUTOMATICALLY' <<<"$e6" \
  && ok "X601 WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS: a legacy row records no origin, so its test is held back" \
  || bad "X601 WORTH_REMOVAL_LIST_HOLDS_BACK_THE_NEVER_AUTOMATIC_KINDS" "legacy row: ${e6:-not listed}"
rc=0; out="$(WC "$R" --removal-list --spec SPEC-0013 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -qx 'removal batch for SPEC-0013 — 1 test(s) for the owner'"'"'s confirmation (nothing is removed by this list)' <<<"$out" \
  && grep -q '^ *1\. tests/test_other.py::test_banner$' <<<"$out" && grep -q '(worth-check; in the baseline)' <<<"$out" \
  && ! grep -q 'test_removal.py' <<<"$out" \
  && ok "X602 WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC: --spec lists the spec's own tests, its baseline tests included, and no other" \
  || bad "X602 WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC" "rc $rc: $out"
rc=0; out="$(WC "$R" --removal-list --spec SPEC-0099 2>&1)" || rc=$?
[[ $rc -eq 2 ]] && grep -q 'SPEC-0099' <<<"$out" \
  && ok "X602 WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC: a spec the plant does not hold exits 2 and names it" \
  || bad "X602 WORTH_REMOVAL_LIST_FOR_A_REOPENED_SPEC" "unknown spec rc $rc: $out"
rc=0; out="$(WC "$P" --removal-list 2>&1)" || rc=$?
[[ $rc -eq 0 && "$(digest "$R")" == "$RBEFORE" ]] && grep -q '^removal batch — 9 test(s)' <<<"$out" \
  && ok "X591 WORTH_NEVER_EDITS_A_TEST: --removal-list exits 0 with tests flagged and leaves every file of the plant as it was" \
  || bad "X591 WORTH_NEVER_EDITS_A_TEST" "removal list rc $rc, plant changed: $([[ "$(digest "$R")" == "$RBEFORE" ]] && echo no || echo yes)"

# X800 to X806: the independent tester's adversarial cases. The tree is
# tests/fixtures/worth/adversarial/ and the verdict each case is owed is
# adversarial.tsv, both written before the tool ran over them. A row of
# known-gaps.tsv is a documented limit of the heuristic: it is held at the
# verdict that file records, so a fix shows here and its row moves to the gate.
A="$T/adv"; mkdir -p "$A/docs/graph" "$A/tests"; cp -R "$FX/adversarial" "$A/tests/"
printf 'TEST_GLOBS = ["tests/**/*.*"]\n' > "$A/docs/graph/spec-lint.py"
ABEFORE="$(digest "$A/tests")"
rc=0; WC "$A" --json >"$T/adv.json" 2>"$T/adv.err" || rc=$?
adv="$("$PY" - "$FX/adversarial.tsv" "$FX/known-gaps.tsv" "$T/adv.json" 2>&1 <<'PY' || true
import json, sys
try:
    report = json.load(open(sys.argv[3], encoding="utf-8"))
except ValueError as e:
    print(f"JSON\tnone\tnone\tnone\tthe --json report does not parse: {e}"); sys.exit(0)
got = {t["test"]: t["verdict"] for t in report.get("tests", [])}
got.update({n["path"]: "not checked" for n in report.get("not_checked", []) if "::" in n["path"]})
rows = lambda p: [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8")
                  if l.strip() and not l.startswith("#")]
gaps = {r[0]: r for r in rows(sys.argv[2])}
owed = {r[0]: r for r in rows(sys.argv[1])}
for test in gaps:
    if test not in owed:
        print(f"BAD\tnone\tnone\tgap\t{test}: a known gap that adversarial.tsv does not hold")
for test, (_, verdict, what) in owed.items():
    kind, want = ("gap", gaps[test][2]) if test in gaps else ("gated", verdict)
    have = got.get(test, "not read")
    print(f"{'OK' if have == want else 'BAD'}\t{verdict}\t{what}\t{kind}\t{test}: "
          f"{'held at' if kind == 'gap' else 'owed'} {want}, got {have}")
PY
)"
check_adv() {   # label contract pattern-on-what
  local rows; rows="$(awk -F'\t' -v k="$3" '$1 == "JSON" || ($4 == "gated" && $3 ~ k)' <<<"$adv")"
  if [[ -z "$rows" ]] || grep -q '^BAD\|^JSON' <<<"$rows"; then
    bad "$1 $2" "$(grep -v '^OK' <<<"${rows:-JSON	none	none	none	no adversarial row matched $3}" | cut -f5 | tr '\n' ';')"
  else
    ok "$1 $2: $(wc -l <<<"$rows" | tr -d ' ') adversarial test(s) get the verdict adversarial.tsv owes ($3)"
  fi
}
check_adv X800 WORTH_SETUP_OUTPUT_IS_NOT_A_LITERAL 'setUp|beforeAll'
check_adv X801 WORTH_IMPORTED_CALL_IS_CODE_UNDER_TEST 'named (resolve|match|get|find)'
check_adv X802 WORTH_UNREAD_TEST_IS_NOT_CHECKED 'parametrize|test[.]each'
check_adv X803 WORTH_SPARING_READS_DECLARATIONS_NOT_CONTENT 'https|hex colour|cookies|security test'
check_adv X804 WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK 'False flag|false flag|non-empty guard'
check_adv X805 WORTH_LITERAL_BUILT_FROM_LITERALS_IS_A_LITERAL 'joined|concatenated|inline snapshot|string methods only'
check_adv X806 WORTH_FLAGS_A_READ_BACK_TEST '.'
check_adv X810 WORTH_SECURITY_KEY_IS_A_DECLARATION 'key is a string'
check_adv X811 WORTH_SETUP_THAT_ONLY_READS_IS_A_READ 'setUp only copies'
check_adv X812 WORTH_DESCRIBE_BODY_READ_IS_A_READ 'read in the describe body'
gaps="$(awk -F'\t' '$1 == "JSON" || $4 == "gap"' <<<"$adv")"
[[ -n "$gaps" ]] && ! grep -q '^BAD\|^JSON' <<<"$gaps" \
  && ok "X806 HEURISTIC_SPARES_A_READ_BACK: the $(wc -l <<<"$gaps" | tr -d ' ') documented limit(s) of known-gaps.tsv keep the verdict that file records" \
  || bad "X806 HEURISTIC_SPARES_A_READ_BACK" "$(grep -v '^OK' <<<"${gaps:-JSON	none	none	none	known-gaps.tsv holds no row}" | cut -f5 | tr '\n' ';')"
[[ "$(digest "$A/tests")" == "$ABEFORE" ]] \
  && ok "X591 WORTH_NEVER_EDITS_A_TEST: the adversarial run changed no test file" \
  || bad "X591 WORTH_NEVER_EDITS_A_TEST" "the adversarial tree changed under the check"

# X802 WORTH_UNREAD_TEST_IS_NOT_CHECKED: a parametrized test whose table is not
# written as literals, and a test whose title is computed, are each named and
# counted as not checked, never read as clean and never left out.
N="$T/n"; mkdir -p "$N/docs/graph" "$N/tests"
printf 'TEST_GLOBS = ["tests/**/*.*"]\n' > "$N/docs/graph/spec-lint.py"
cat > "$N/tests/test_param.py" <<'EOF'
import pytest

from app.data import CASES
from app.settings import NAV, ROUTES, SUBMIT_LABEL


@pytest.mark.parametrize("path,handler", CASES)
def test_routes_from_a_computed_table(path, handler):
    assert ROUTES[path] == handler


def test_nav_links():
    assert "/private" not in NAV
    assert "/home" in NAV


def test_label_is_set():
    assert SUBMIT_LABEL != ""


def test_label_is_truthy_and_send():
    assert SUBMIT_LABEL
    assert SUBMIT_LABEL == "Send"
EOF
cat > "$N/tests/each.test.ts" <<'EOF'
import { expect, test } from "vitest";
import { CASES } from "../src/cases";
import { SUBMIT_LABEL } from "../src/labels";

test.each(CASES)("label is %s", (want) => {
  expect(SUBMIT_LABEL).toBe(want);
});

test.each`
  want
  ${"Send"}
`("tagged label is $want", ({ want }) => {
  expect(SUBMIT_LABEL).toBe(want);
});

for (const want of ["Send"]) {
  test(`label is ${want}`, () => {
    expect(SUBMIT_LABEL).toBe(want);
  });
}
EOF
rc=0; out="$(WC "$N" 2>&1)" || rc=$?
grep -qx 'tests/test_param.py::test_routes_from_a_computed_table  not checked (parametrized)' <<<"$out" \
  && grep -qx 'tests/each.test.ts::label is %s  not checked (parametrized)' <<<"$out" \
  && grep -qx 'tests/each.test.ts::tagged label is $want  not checked (parametrized)' <<<"$out" \
  && grep -qx 'tests/each.test.ts::line 17  not checked (computed title)' <<<"$out" \
  && grep -qx 'worth-check: 1 flagged (0 in baseline), 2 files read, 4 not checked (computed title: 1 test(s); parametrized: 3 test(s))' <<<"$out" \
  && ! grep -qi 'clean' <<<"$out" \
  && ok "X802 WORTH_UNREAD_TEST_IS_NOT_CHECKED: a parametrized test with a computed table and a test with a computed title are named and counted as not checked" \
  || bad "X802 WORTH_UNREAD_TEST_IS_NOT_CHECKED" "rc $rc: $out"

# X804 WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK: a truthiness or non-empty guard
# beside a read-back spares nothing, a guard alone spares, and the absence of a
# named value stays a negative control.
rc=0; WC "$N" --json >"$T/n.json" 2>&1 || rc=$?
v="$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1])); print(" ".join(t["name"]+"="+t["verdict"] for t in r["tests"]))' "$T/n.json" 2>&1 || true)"
[[ "$v" == "test_nav_links=spared test_label_is_set=spared test_label_is_truthy_and_send=flagged" ]] \
  && ok "X804 WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK: a guard beside a read-back spares nothing; a guard alone and a named absence spare the test" \
  || bad "X804 WORTH_GUARD_DOES_NOT_SPARE_A_READ_BACK" "got: $v"

# X810 to X812: a plant of cases beside the tester's round-two rows. A string
# used as a key names a thing, so the security spare reads it; a string compared
# against is content and spares nothing. A setUp that only reads, and a const a
# describe body only reads, are reads; any code they run keeps them logic.
K="$T/k"; mkdir -p "$K/docs/graph" "$K/tests"
printf 'TEST_GLOBS = ["tests/**/*.*"]\n' > "$K/docs/graph/spec-lint.py"
cat > "$K/tests/test_keys.py" <<'EOF'
import unittest
from pathlib import Path

from app.base import BaseCase
from app.build import build_site
from app.settings import COPY, HEADERS, SESSION_COOKIE_SECURE, SETTINGS, SUBMIT_LABEL


def test_cookie_flag_as_a_constant():
    assert SESSION_COOKIE_SECURE is True


def test_cookie_flag_under_a_key():
    assert SETTINGS["SESSION_COOKIE_SECURE"] is True


def test_cookie_flag_through_get():
    assert SETTINGS.get("SESSION_COOKIE_SECURE") is True


def test_policy_through_getattr():
    assert getattr(SETTINGS, "csp_policy") == "default-src 'self'"


def test_policy_in_a_dict_literal():
    assert HEADERS == {"Content-Security-Policy": "default-src 'self'"}


def test_banner_copy_under_a_plain_key():
    assert COPY["banner_title"] == "Your session cookies keep you logged in"


class TestCopiesASecuritySetting(unittest.TestCase):
    def setUp(self):
        self.flag = SESSION_COOKIE_SECURE

    def test_flag_copied_in_set_up(self):
        assert self.flag is True


class TestReadsInSetUp(unittest.TestCase):
    def setUp(self):
        self.page = Path("web/submit.html").read_text(encoding="utf-8")

    def test_page_read_in_set_up(self):
        self.assertIn('value="Send"', self.page)


class TestBuildsInSetUp(unittest.TestCase):
    def setUp(self):
        self.label = SUBMIT_LABEL
        build_site(out="dist")

    def test_label_beside_a_build(self):
        self.assertEqual(self.label, "Send")


class TestUnderAnUnseenBase(BaseCase):
    def setUp(self):
        self.label = SUBMIT_LABEL

    def test_label_under_an_unseen_base(self):
        self.assertEqual(self.label, "Send")
EOF
cat > "$K/tests/keys.test.ts" <<'EOF'
import { readFileSync } from "node:fs";
import { beforeAll, describe, expect, test } from "vitest";
import { renderPage } from "../src/forms";
import { COPY, HEADERS, SETTINGS } from "../src/settings";

test("policy header as a property", () => {
  expect(HEADERS).toHaveProperty("Content-Security-Policy", "default-src 'self'");
});

test("cookie flag in an object literal", () => {
  expect(SETTINGS).toEqual({ "SESSION_COOKIE_SECURE": true });
});

test("banner copy under a plain key", () => {
  expect(COPY["bannerTitle"]).toBe("Your session cookies keep you logged in");
});

describe("read in a describe body", () => {
  const nav = readFileSync("web/nav.html", "utf8").trim();

  test("nav read in the describe body carries help", () => {
    expect(nav).toContain("/help");
  });
});

describe("read beside a build hook", () => {
  const page = readFileSync("web/submit.html", "utf8");
  beforeAll(() => {
    renderPage("submit");
  });

  test("page read beside a build hook carries the label", () => {
    expect(page).toContain('value="Send"');
  });
});

describe("a let in the describe body", () => {
  let html = readFileSync("web/submit.html", "utf8");

  test("html held in a let carries the label", () => {
    expect(html).toContain('value="Send"');
  });
});
EOF
rc=0; WC "$K" --json >"$T/k.json" 2>&1 || rc=$?
kv() {   # the verdicts of the named tests, in order
  "$PY" -c 'import json,sys; r={t["name"]: t["verdict"] for t in json.load(open(sys.argv[1]))["tests"]}
print(" ".join(r.get(n, "not-read") for n in sys.argv[2:]))' "$T/k.json" "$@" 2>&1 || true; }
v="$(kv test_cookie_flag_as_a_constant test_cookie_flag_under_a_key test_cookie_flag_through_get \
  test_policy_through_getattr test_policy_in_a_dict_literal 'policy header as a property' \
  'cookie flag in an object literal' TestCopiesASecuritySetting::test_flag_copied_in_set_up)"
w="$(kv test_banner_copy_under_a_plain_key 'banner copy under a plain key')"
[[ "$v" == "spared spared spared spared spared spared spared spared" && "$w" == "flagged flagged" ]] \
  && ok "X810 WORTH_SECURITY_KEY_IS_A_DECLARATION: a security setting gets one verdict as a constant, under a subscript, get, getattr, a dict or object key, toHaveProperty or a setUp copy; a security word in the compared value spares nothing" \
  || bad "X810 WORTH_SECURITY_KEY_IS_A_DECLARATION" "spared expected: $v; flagged expected: $w"
v="$(kv TestReadsInSetUp::test_page_read_in_set_up TestBuildsInSetUp::test_label_beside_a_build \
  TestUnderAnUnseenBase::test_label_under_an_unseen_base)"
[[ "$v" == "flagged spared spared" ]] \
  && ok "X811 WORTH_SETUP_THAT_ONLY_READS_IS_A_READ: a setUp that only reads makes its attribute a read; a setUp that runs code, or under a base the check cannot see, stays logic" \
  || bad "X811 WORTH_SETUP_THAT_ONLY_READS_IS_A_READ" "want flagged spared spared, got: $v"
v="$(kv 'nav read in the describe body carries help' 'page read beside a build hook carries the label' \
  'html held in a let carries the label')"
[[ "$v" == "flagged spared spared" ]] \
  && ok "X812 WORTH_DESCRIBE_BODY_READ_IS_A_READ: a const a describe body only reads is a read; beside a hook that runs code, or held in a let, it stays logic" \
  || bad "X812 WORTH_DESCRIBE_BODY_READ_IS_A_READ" "want flagged spared spared, got: $v"

# X591 WORTH_NEVER_EDITS_A_TEST: every run above left the fixture suite's bytes as they were.
[[ "$(digest "$P/tests")" == "$BEFORE" ]] \
  && ok "X591 WORTH_NEVER_EDITS_A_TEST: no run changed a test file" \
  || bad "X591 WORTH_NEVER_EDITS_A_TEST" "the fixture suite changed under the check"
find "$T/p" -name '*.bak*' -o -name '*.orig' | grep -q . \
  && bad "X591 WORTH_NEVER_EDITS_A_TEST" "a run left a backup beside a test" \
  || ok "X591 WORTH_NEVER_EDITS_A_TEST: no run wrote beside a test"

[[ "$fail" == 0 ]] && echo "test-worth-check: PASS" || { echo "test-worth-check: FAIL"; exit 1; }
