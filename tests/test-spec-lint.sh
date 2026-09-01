#!/usr/bin/env bash
# spec-lint contract: fails on an uncovered live contract, passes when
# covered, ignores superseded specs, and FAILS (not passes) when
# contracts exist but zero test files match — the green-lie guard.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/docs/graph/specs" "$TMP/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$TMP/docs/graph/"

printf -- '- **Status:** active\n\n### Contract: SUBMIT_VALID_FORM\n### Contract: REJECT_BAD_SCHEMA\n' \
  > "$TMP/docs/graph/specs/SPEC-0001-forms.md"
printf -- '- **Status:** superseded\n\n### Contract: OLD_RETIRED_THING\n' \
  > "$TMP/docs/graph/specs/SPEC-0002-old.md"
printf 'def test_submit():  # SUBMIT_VALID_FORM\n    pass\n' \
  > "$TMP/tests/test_forms.py"

# 1. uncovered live contract -> exit 1, names the slug, not the retired one
out="$(python3 "$TMP/docs/graph/spec-lint.py" 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected exit 1 on uncovered contract, got $rc" >&2; exit 1; }
grep -q 'REJECT_BAD_SCHEMA' <<<"$out" \
  || { echo "uncovered live slug not named" >&2; exit 1; }
# NOT `! grep` — bash exempts `!`-negated commands from errexit, so a
# leaked retired slug would have sailed straight past this check.
if grep -q 'OLD_RETIRED_THING' <<<"$out"; then
  echo "retired (superseded) contract leaked into the report" >&2; exit 1
fi

# 2. --warn reports but exits 0
python3 "$TMP/docs/graph/spec-lint.py" --warn >/dev/null

# 3. covered -> PASS
printf 'def test_reject():  # REJECT_BAD_SCHEMA\n    pass\n' \
  >> "$TMP/tests/test_forms.py"
python3 "$TMP/docs/graph/spec-lint.py" >/dev/null

# 4. zero test files with live contracts -> green-lie FAIL
rm "$TMP/tests/test_forms.py"
out="$(python3 "$TMP/docs/graph/spec-lint.py" 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected green-lie exit 1 on zero test files, got $rc" >&2; exit 1; }
grep -qi 'green lie' <<<"$out"

# 5. REGRESSION — prefix slugs: alternation is leftmost-first, so PARSE_JSON
# once stole the match from PARSE_JSON_STRICT; the covered longer slug was
# reported uncovered while the uncovered shorter one silently earned credit.
mkdir -p "$TMP/tests"
printf -- '- **Status:** active\n\n### Contract: PARSE_JSON\n### Contract: PARSE_JSON_STRICT\n' \
  > "$TMP/docs/graph/specs/SPEC-0003-parse.md"
rm "$TMP/docs/graph/specs/SPEC-0001-forms.md"
printf 'def test_strict():  # PARSE_JSON_STRICT\n    pass\n' \
  > "$TMP/tests/test_parse.py"
out="$(python3 "$TMP/docs/graph/spec-lint.py" 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected exit 1: PARSE_JSON is uncovered, got $rc" >&2; echo "$out" >&2; exit 1; }
grep -q -- '- PARSE_JSON ' <<<"$out" \
  || { echo "uncovered PARSE_JSON not named" >&2; echo "$out" >&2; exit 1; }
if grep -q -- '- PARSE_JSON_STRICT' <<<"$out"; then
  echo "covered PARSE_JSON_STRICT wrongly reported uncovered (prefix steal)" >&2
  echo "$out" >&2; exit 1
fi
# 5b. REGRESSION — an UNREGISTERED extension slug must not credit its prefix:
# a test mentioning only PARSE_JSON_V2 (no such contract) once satisfied
# PARSE_JSON via bare substring match.
printf 'def test_v2():  # PARSE_JSON_V2\n    pass\n' \
  > "$TMP/tests/test_parse.py"
out="$(python3 "$TMP/docs/graph/spec-lint.py" 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected exit 1: no registered slug is covered, got $rc" >&2; echo "$out" >&2; exit 1; }
grep -q -- '- PARSE_JSON ' <<<"$out" \
  || { echo "PARSE_JSON wrongly credited by PARSE_JSON_V2 substring" >&2; echo "$out" >&2; exit 1; }

rm "$TMP/docs/graph/specs/SPEC-0003-parse.md" "$TMP/tests/test_parse.py"
printf -- '- **Status:** active\n\n### Contract: SUBMIT_VALID_FORM\n### Contract: REJECT_BAD_SCHEMA\n' \
  > "$TMP/docs/graph/specs/SPEC-0001-forms.md"

# 6. no specs dir at all -> SKIP, exit 0
rm -rf "$TMP/docs/graph/specs"
python3 "$TMP/docs/graph/spec-lint.py" >/dev/null

printf 'spec lint contract: PASS\n'
