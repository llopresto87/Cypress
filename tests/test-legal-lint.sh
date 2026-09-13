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
- **language_version:** EN, original OJ text as published · **verified:** 2026-01-01 · **legal_status:** in force
EOF
expect_fail "graded \`verbatim\` (in whole or per id)" "compound-grade-honesty"
rm "$TMP/legal-corpus/eu/zz-fixture.md"

# 8. THE AMENDMENT TRAP — a new entry that does not state the EDITION of the
# text it read is non-citable. _schema.md has always said so; until this check
# nothing enforced it, and an unamended reading of an amended instrument reads
# exactly like a correct one, so the corpus could not tell them apart.
cat > "$TMP/legal-corpus/eu/zz-edition.md" <<'EOF'
# Fixture page

### `eu.zz-edition` — planted unstated edition

- **instrument:** Regulation (EU) 2024/2847 (CRA)
- **provision:** Article 14
- **text_form:** `normalized summary`
- **text:** a paraphrase of the obligation.
- **official_url:** https://example.org
- **consulted:** x — **verification_grade:** proxy-sourced
- **language_version:** English · **verified:** 2026-01-01 · **legal_status:** in force
EOF
expect_fail "does not state the EDITION" "amendment-trap"

# The same entry passes the moment it says which edition it read.
python3 - "$TMP/legal-corpus/eu/zz-edition.md" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace("**language_version:** English",
    "**language_version:** English, consolidated version as at 2024-11-20", 1))
PY
lint >/dev/null || { echo "[amendment-trap] a stated edition still failed" >&2; exit 1; }
rm "$TMP/legal-corpus/eu/zz-edition.md"

# A decision is not amended, so case-law is exempt by construction — not by a
# list that someone has to remember to extend.
cat > "$TMP/legal-corpus/case-law/zz-decision.md" <<'EOF'
# Fixture page

### `zz-decision` — a judgment states no edition, and needs none

- **instrument:** Court judgment in Case C-000/00
- **provision:** paragraph 1
- **text_form:** `normalized summary`
- **text:** a paraphrase of the holding.
- **official_url:** https://example.org
- **consulted:** x — **verification_grade:** proxy-sourced
- **language_version:** English · **verified:** 2026-01-01 · **legal_status:** in force
EOF
lint >/dev/null || { echo "[amendment-trap] case-law was not exempt" >&2; exit 1; }
rm "$TMP/legal-corpus/case-law/zz-decision.md"

# The recorded-debt ledger only shrinks: an entry on it that NOW states its
# edition must be struck, or the ledger rots into a permanent waiver.
python3 - "$TMP/legal-corpus/eu/gdpr.md" <<'PY'
import re,sys; p=sys.argv[1]; t=open(p).read()
i=t.index("### `gdpr-art-5-1-a`")
j=t.index("**language_version:**", i)
k=t.index("\n", j)
t=t[:j]+"**language_version:** English, original OJ text as published"+t[k:]
open(p,'w').write(t)
PY
expect_fail "still listed in EDITION_DEBT" "edition-debt-shrinks"
restore legal-corpus/eu/gdpr.md

# 8b. The edition marker must be an edition CLAIM, not a keyword. The field is
# named `language_version`, so prose about the LANGUAGE trips any loose match:
# both phrasings below say nothing about the edition and must still FAIL.
for phrasing in "Italian" "Italian, original-language text" \
                "the Italian version published by the OJ"; do
  python3 - "$TMP/legal-corpus/eu/nis2.md" "$phrasing" <<'PY'
import re, sys
p, value = sys.argv[1], sys.argv[2]
t = open(p).read()
i = t.index("### `nis2-dir-2022-2555`")
j = t.index("**language_version:**", i)
end = re.compile(r"\n\s*[-*]\s+\*\*").search(t, j).start()
open(p, "w").write(t[:j] + f"**language_version:** {value}" + t[end:])
PY
  expect_fail "does not state the EDITION" "edition-marker: $phrasing"
  restore legal-corpus/eu/nis2.md
done
echo "  edition markers reject language prose that states no edition — OK"

# 8c. A multi-group page states its fields PER GROUP. An entry must inherit the
# nearest preceding group's edition, never the first one on the page — or an
# entry under a later group silently borrows a claim about a different fetch of
# a different instrument.
cat > "$TMP/legal-corpus/eu/zz-groups.md" <<'EOF'
# Fixture page

## Group A — first fetch

- **instrument:** Regulation (EU) 2024/2847 (CRA)
- **official_url:** https://example.org
- **consulted:** x — **verification_grade:** proxy-sourced
- **language_version:** English, consolidated version as at 2024-11-20
- **verified:** 2026-01-01 · **legal_status:** in force

### `eu.zz-group-a` — inherits Group A, which states an edition

- **provision:** Article 13
- **text_form:** `normalized summary`
- **text:** a paraphrase.

## Group B — second fetch, states no edition

- **instrument:** Regulation (EU) 2024/2847 (CRA)
- **official_url:** https://example.org
- **consulted:** y — **verification_grade:** proxy-sourced
- **language_version:** English
- **verified:** 2026-01-01 · **legal_status:** in force

### `eu.zz-group-b` — must NOT inherit Group A's edition

- **provision:** Article 14
- **text_form:** `normalized summary`
- **text:** a paraphrase.
EOF
expect_fail "\`eu.zz-group-b\` does not state the EDITION" "edition-group-scope"
rm "$TMP/legal-corpus/eu/zz-groups.md"
echo "  an entry inherits its own group's edition, not the page's first — OK"

# 9. After all restores, the copy lints clean again.
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

# --- the national layer is named, and its absence is a request -------------
# The EU pages are jurisdiction-neutral; the national ones are only as wide as
# what has been ingested. A plant established outside that set must be told so
# loudly: the analyst cannot distinguish "never ingested" from "does not exist",
# and the failure mode is reading a neighbouring country's statute across.
mkdir -p "$CTMP"/{jit,jde,jnone}
carried="$(ls "$ROOT"/legal-corpus/national/*.md | sed 's|.*/||; s|-.*||' | sort -u | head -1)"
bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/jit" --legal-corpus yes \
    --legal-jurisdiction "$carried" >"$CTMP/o-jit" 2>&1
grep -q "national layer: '$carried' is carried" "$CTMP/o-jit" \
    || { echo "legal-lint: FAIL — a carried jurisdiction was not confirmed" >&2; exit 1; }
grep -q "\"legal_jurisdiction\": \"$carried\"" "$CTMP/jit/.cypress/seed.json" \
    || { echo "legal-lint: FAIL — the stamp did not record the jurisdiction" >&2; exit 1; }

# An uncarried code is a recorded request, never an error, and the corpus still
# arrives whole — the EU layer applies regardless of establishment.
bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/jde" --legal-corpus yes \
    --legal-jurisdiction zz >"$CTMP/o-jde" 2>&1 \
    || { echo "legal-lint: FAIL — an uncarried jurisdiction was treated as an error" >&2; exit 1; }
grep -q "NATIONAL LAYER MISSING for 'zz'" "$CTMP/o-jde" \
    || { echo "legal-lint: FAIL — a missing national layer was not surfaced" >&2; exit 1; }
grep -q "research-scout ingest" "$CTMP/o-jde" \
    || { echo "legal-lint: FAIL — the missing layer named no remedy" >&2; exit 1; }
[[ -f "$CTMP/jde/docs/graph/legal/corpus/eu/gdpr.md" ]] \
    || { echo "legal-lint: FAIL — an uncarried jurisdiction lost the EU layer too" >&2; exit 1; }

# Unset is its own answer: nothing claimed about establishment.
bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/jnone" --legal-corpus yes >"$CTMP/o-jn" 2>&1
grep -q '"legal_jurisdiction": "undecided"' "$CTMP/jnone/.cypress/seed.json" \
    || { echo "legal-lint: FAIL — an unnamed jurisdiction was not recorded undecided" >&2; exit 1; }
grep -q "NEXT STEP — national jurisdiction undecided" "$CTMP/o-jn" \
    || { echo "legal-lint: FAIL — an unnamed jurisdiction was not surfaced" >&2; exit 1; }
# A malformed code is refused.
bash "$ROOT/install.sh" claude-code --project-dir "$CTMP/jnone" --legal-jurisdiction italy >/dev/null 2>&1 \
    && { echo "legal-lint: FAIL — --legal-jurisdiction took a non-country-code" >&2; exit 1; }

printf 'legal jurisdiction: PASS — carried=%s, uncarried is an ingest request\n' "$carried"
