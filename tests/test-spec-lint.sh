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
grep -q 'REJECT_BAD_SCHEMA' <<<"$out"
! grep -q 'OLD_RETIRED_THING' <<<"$out"

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

# 5. no specs dir at all -> SKIP, exit 0
rm -rf "$TMP/docs/graph/specs"
python3 "$TMP/docs/graph/spec-lint.py" >/dev/null

printf 'spec lint contract: PASS\n'
