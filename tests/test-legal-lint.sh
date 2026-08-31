#!/usr/bin/env bash
# legal-lint contract: the citability linter must FAIL (exit 1, named message)
# on each violation class it claims to guard — not merely pass on good input.
# Mirrors test-seed-lint.sh's plant-a-violation discipline.
#
# The regression that motivates case 5 is real and shipped: an earlier ad-hoc
# audit selected pages by FILENAME and skipped every `index.md`, silently
# excluding case-law/index.md's seven entries — the `case-law` /
# `regulator-decision` kind that `_schema.md` itself calls the highest-risk
# thing in a compliance document after a number. The audit reported a clean
# "121/121" for weeks. The real census is 128.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hermetic copy (legal-lint resolves ROOT from its own location).
( cd "$ROOT" && tar --exclude=.git --exclude=__pycache__ --exclude='*.pyc' \
    --exclude=.pytest_cache -cf - . ) | ( cd "$TMP" && tar -xf - )

lint() { python3 "$TMP/tests/legal-lint.py" 2>&1; }
restore() { cp "$ROOT/$1" "$TMP/$1"; }

expect_fail() {  # $1=grep-pattern  $2=label
  local out rc
  out="$(lint)" && rc=0 || rc=$?
  [[ $rc -eq 1 ]] || { echo "[$2] expected exit 1, got $rc" >&2; echo "$out" >&2; exit 1; }
  grep -q "$1" <<<"$out" || { echo "[$2] missing expected message: /$1/" >&2; echo "$out" >&2; exit 1; }
}

# 0. Baseline: the pristine copy lints clean.
lint >/dev/null || { echo "baseline legal-lint did not pass on a clean copy" >&2; exit 1; }

# 1. A missing required field makes the entry non-citable. `_schema.md` is
# categorical about this: "no partial credit and no 'good enough for a draft'".
python3 - "$TMP/legal-corpus/national/it-codice-privacy.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("**legal_status:**", "**gone:**", 1))
PY
expect_fail "has no \`legal_status\`" "missing-required-field"
restore legal-corpus/national/it-codice-privacy.md

# 2. A never-inheritable field must be inline — a page header cannot supply
# `provision`, `text_form` or `text` on an entry's behalf.
python3 - "$TMP/legal-corpus/national/it-workers-statute.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("**provision:**", "**gone:**", 1))
PY
expect_fail "is never inherited" "never-inheritable-inline"
restore legal-corpus/national/it-workers-statute.md

# 3. GRADE HONESTY — the falsification the schema's two "never soften" fields
# exist to prevent. This has shipped before: 18 entries arrived from a donor
# graded `verbatim` while carrying a paraphrase.
python3 - "$TMP/legal-corpus/eu/eprivacy-directive.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
# keep every `verbatim` grade, remove every quotation those grades promise
t=re.sub(r'(?m)^\s*>.*\n', '', t)                      # blockquoted wording
for ch in ['"', '“', '”', '«', '»']:
    t=t.replace(ch, '')
open(p,'w').write(t)
PY
expect_fail "graded \`verbatim\` but its text" "verbatim-without-quotation"
restore legal-corpus/eu/eprivacy-directive.md

# 4. Controlled vocabulary: an invented text_form or legal_status is rejected.
python3 - "$TMP/legal-corpus/eu/scc-2021-914.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(re.sub(r"\*\*legal_status:\*\*[^\n]*", "**legal_status:** `probably fine`", t, count=1))
PY
expect_fail "legal_status is not a schema value" "invalid-vocabulary"
restore legal-corpus/eu/scc-2021-914.md

# 5. REGRESSION — pages are selected by CONTENT, never by filename. A content
# page named `index.md` must be scanned like any other. If this ever stops
# failing, the linter has gone blind to an entire instrument kind again.
python3 - "$TMP/legal-corpus/case-law/index.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("**verified:**", "**gone:**", 1))
PY
expect_fail "case-law/index.md" "index-named-page-is-scanned"
restore legal-corpus/case-law/index.md

# 6. After all restores, the copy lints clean again.
lint >/dev/null || { echo "legal-lint did not return to PASS after restores" >&2; exit 1; }

printf 'legal-lint contract: PASS\n'
