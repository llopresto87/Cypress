#!/usr/bin/env bash
# legal-lint contract: the citability linter FAILS (exit 1, named message) on
# each violation class it guards. Each case plants one synthetic page in a
# mini tree (the seed corpus + the linter), lints, and removes the page.
# Placement of the corpus by install.sh is tested in test-plant-state.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# shellcheck source=helpers/lintcase.sh
. "$ROOT/tests/helpers/lintcase.sh"

# legal-lint resolves ROOT from its own location; the real corpus stays in the
# tree because EDITION_DEBT rows must each name a page.
mini_tree "$TMP" legal-corpus tests/legal-lint.py
C="$TMP/legal-corpus"
lint() { python3 "$TMP/tests/legal-lint.py"; }
fails() {  # $1=label $2=needle; lint must exit 1 naming the needle
  expect_rc 1 "$2" -- lint || { echo "[$1] above" >&2; exit 1; }
}
passes() {  # $1=label
  expect_rc 0 "" -- lint || { echo "[$1] expected a clean lint" >&2; exit 1; }
}
# entry <id> [name=value | name=-]...: one valid entry, a field set or dropped.
entry() {
  python3 - "$@" <<'PY'
import sys
eid, *over = sys.argv[1:]
f = {"instrument": "Regulation (EU) 2024/2847 (CRA)", "provision": "Article 14",
     "text_form": "`normalized summary`", "text": "a paraphrase of the obligation.",
     "official_url": "https://example.org",
     "consulted": "x — **verification_grade:** proxy-sourced",
     "language_version": "English, consolidated version as at 2024-11-20",
     "verified": "2026-01-01", "legal_status": "in force"}
for o in over:
    k, v = o.split("=", 1)
    if v == "-": f.pop(k, None)
    else: f[k] = v
print(f"### `{eid}` — synthetic entry\n")
for k, v in f.items():
    print(f"- **{k}:** {v}")
print()
PY
}

# 0. Baseline: the mini tree lints clean.
passes baseline

# 1. A missing required field makes the entry non-citable.
entry eu.zz-status legal_status=- >"$C/eu/zz.md"
fails missing-required-field "has no \`legal_status\`"

# 2. A never-inheritable field must be inline, even when the header states it.
{ printf '# Fixture\n\n- **provision:** Article 1\n\n'; entry eu.zz-inline provision=-; } >"$C/eu/zz.md"
fails never-inheritable-inline "is never inherited"

# 3. Grade honesty: a `verbatim` grade with no quoted wording, whole or compound
# (a prefix before `verbatim` once disabled the check).
{ entry eu.zz-plain 'text_form=`verbatim`' 'text=a paraphrase with no quotation.'
  entry eu.zz-compound 'text_form=**per id, not uniform** — `verbatim` for `eu.zz-compound`' \
      'text=a paraphrase with no quotation.'; } >"$C/eu/zz.md"
fails verbatim-without-quotation "\`eu.zz-plain\` is graded \`verbatim\` (in whole or per id)"
fails compound-grade-honesty "\`eu.zz-compound\` is graded \`verbatim\` (in whole or per id)"

# 4. Controlled vocabulary.
entry eu.zz-vocab 'legal_status=`probably fine`' >"$C/eu/zz.md"
fails invalid-vocabulary "legal_status is not a schema value"
rm "$C/eu/zz.md"

# 5. Pages are selected by content, never by filename: an index.md is scanned.
entry eu.zz-index verified=- >"$C/eu/index.md"
fails index-named-page-is-scanned "eu/index.md"
rm "$C/eu/index.md"

# 6. `text_form` must not satisfy `text`.
entry eu.zz-text text=- >"$C/eu/zz.md"
fails text_form-does-not-satisfy-text "has no \`text\`"

# 8. The amendment trap: an entry that states no EDITION is non-citable; it
# passes once it states one; case-law is exempt by construction.
entry eu.zz-edition language_version=English >"$C/eu/zz.md"
fails amendment-trap "does not state the EDITION"
entry eu.zz-edition >"$C/eu/zz.md"
passes amendment-trap-stated-edition
rm "$C/eu/zz.md"
entry zz-decision language_version=English >"$C/case-law/zz.md"
passes amendment-trap-case-law-exempt
rm "$C/case-law/zz.md"

# 8b. The edition marker is an edition CLAIM, not a keyword: language prose fails.
for phrasing in "Italian, original-language text" "the Italian version published by the OJ"; do
  entry eu.zz-marker "language_version=$phrasing" >"$C/eu/zz.md"
  fails "edition-marker: $phrasing" "does not state the EDITION"
done
rm "$C/eu/zz.md"

# 8c. An entry inherits its own group's edition, not the page's first.
cat > "$C/eu/zz.md" <<'EOF'
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
fails edition-group-scope "\`eu.zz-group-b\` does not state the EDITION"

printf 'legal-lint contract: PASS\n'
