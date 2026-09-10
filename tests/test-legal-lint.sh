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
# "121/121" for weeks. The real census then was 128 (129 as of 6.9.2).
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
expect_fail "graded \`verbatim\` (in whole or per id) but its text" "verbatim-without-quotation"
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

# 6. REGRESSION — `text_form` must not satisfy `text`. has_field() once
# matched `**text_form:**` for the field `text` (the `[^:]*` gap swallowed
# `_form`), so an entry carrying only the grade — not the words — passed as
# citable. Remove the text bullet, keep text_form: the lint must fail.
python3 - "$TMP/legal-corpus/eu/nis2.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
assert "- **text:** per its official title above" in t
open(p,'w').write(t.replace("- **text:** per its official title above",
                            "- **gone:** per its official title above", 1))
PY
expect_fail "has no \`text\`" "text_form-does-not-satisfy-text"
restore legal-corpus/eu/nis2.md

# 7. REGRESSION — a COMPOUND per-id grade must not disable grade honesty.
# The check was once start-anchored (`re.match`), so any prefix before
# `verbatim` — e.g. the "per id, not uniform" house style 6.9.2 introduced —
# skipped the falsification gate entirely: a backticked `verbatim` grade over
# a quoteless paraphrase passed.
cat > "$TMP/legal-corpus/eu/zz-fixture.md" <<'EOF'
# Fixture page

### `eu.zz-fixture` — planted compound false grade

- **instrument:** Regulation (EU) 2024/2847 (CRA)
- **provision:** Article 14
- **text_form:** **per id, not uniform** — `normalized summary` for none;
  `verbatim` for `eu.zz-fixture`, reproduced exactly from the OJ.
- **text:** a fully paraphrased restatement with no quotation anywhere.
- **official_url:** https://example.org
- **consulted:** x — **verification_grade:** proxy-sourced
- **language_version:** EN · **verified:** 2026-01-01 · **legal_status:** in force
EOF
expect_fail "graded \`verbatim\` (in whole or per id)" "compound-grade-honesty"
rm "$TMP/legal-corpus/eu/zz-fixture.md"

# 8. After all restores, the copy lints clean again.
lint >/dev/null || { echo "legal-lint did not return to PASS after restores" >&2; exit 1; }

printf 'legal-lint contract: PASS\n'

# --- the corpus reaches a plant, whole or not at all -----------------------
# 7.11.0: install.sh never placed legal-corpus/ in a plant at all, so the one
# agent built around it — no web access, `no corpus entry -> no claim` — could
# reach no law and could only ever refuse. Three properties are pinned here:
# it arrives on the owner's yes, it stays away on their no, and it is never a
# subset (a page missing from disk is indistinguishable, to that agent, from an
# instrument that does not exist, which turns an import filter into a silent
# "this does not apply").
CTMP="$(mktemp -d)"; trap 'rm -rf "$CTMP"' EXIT
mkdir -p "$CTMP"/{yes,no,undecided,partial}
want="$(find "$ROOT/legal-corpus" -type f | wc -l | tr -d ' ')"

bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/yes" --legal-corpus yes >/dev/null 2>&1
have="$(find "$CTMP/yes/docs/graph/legal/corpus" -type f 2>/dev/null | wc -l | tr -d ' ')"
[[ "$have" == "$want" ]] \
    || { echo "legal-lint: FAIL — --legal-corpus yes placed $have of $want pages" >&2; exit 1; }
# byte-identical: a plant's copy is a projection, not a fork
diff -r "$ROOT/legal-corpus" "$CTMP/yes/docs/graph/legal/corpus" >/dev/null \
    || { echo "legal-lint: FAIL — the placed corpus differs from the seed's" >&2; exit 1; }
grep -q '"legal_corpus": "yes"' "$CTMP/yes/.cypress/seed.json" \
    || { echo "legal-lint: FAIL — the stamp did not record the owner's yes" >&2; exit 1; }

bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/no" --legal-corpus no >/dev/null 2>&1
[[ ! -d "$CTMP/no/docs/graph/legal/corpus" ]] \
    || { echo "legal-lint: FAIL — --legal-corpus no still placed a corpus" >&2; exit 1; }
grep -q '"legal_corpus": "no"' "$CTMP/no/.cypress/seed.json" \
    || { echo "legal-lint: FAIL — the stamp did not record the owner's no" >&2; exit 1; }

# Unset is neither yes nor no: nothing placed, and the plant says it was never
# asked, so a graft can tell a declining owner from an unasked one.
out="$(bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/undecided" 2>&1)"
[[ ! -d "$CTMP/undecided/docs/graph/legal/corpus" ]] \
    || { echo "legal-lint: FAIL — an unasked owner got a corpus anyway" >&2; exit 1; }
grep -q '"legal_corpus": "undecided"' "$CTMP/undecided/.cypress/seed.json" \
    || { echo "legal-lint: FAIL — the stamp did not record 'undecided'" >&2; exit 1; }
grep -q "NEXT STEP — legal corpus undecided" <<<"$out" \
    || { echo "legal-lint: FAIL — an undecided corpus was not surfaced as a NEXT STEP" >&2; exit 1; }

# A subset is refused, not silently accepted.
bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/partial" --legal-corpus foo >/dev/null 2>&1 \
    && { echo "legal-lint: FAIL — --legal-corpus took a value other than yes/no" >&2; exit 1; }

printf 'legal corpus placement: PASS — %s pages, whole or none\n' "$want"
