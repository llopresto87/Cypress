#!/usr/bin/env bash
# spec-lint contract, two passes. COVERAGE: fails on an uncovered live
# contract, passes when covered, ignores superseded specs, and FAILS (not
# passes) when contracts exist but zero test files match — the green-lie
# guard. SHAPE: every spec on disk — duplicate slugs, a §9 criterion mapping
# to no contract, a signed or live spec missing a §10 row, a live spec
# nobody signed, an implemented spec with a row still red — each named,
# with a draft shape-checked but never counted for coverage. Status is read
# from frontmatter; the template's body "see frontmatter" is not a status.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/docs/graph/specs" "$TMP/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$TMP/docs/graph/"
lint() { python3 "$TMP/docs/graph/spec-lint.py" "$@"; }

# spec NAME STATUS SIGNED(y/n) "SLUG[:rowstatus] ..." [extra-body]
# Shape-conformant by default: frontmatter status, a body "see frontmatter"
# line (the template's form), §0 sign-offs, one §4 contract per slug, a §7
# failure, a §9 criterion per slug, a §10 row per slug with its status.
spec() {
  local name="$1" status="$2" signed="$3" slugs="$4" extra="${5:-}"
  local tick="[ ]"; [[ $signed == y ]] && tick="[x]"
  {
    printf -- '---\nstatus: %s\nstatus_date: 2026-09-09\n---\n\n# %s\n\n## 0. Metadata\n' "$status" "$name"
    printf -- '- **Status:** see frontmatter (single home)\n- **Sign-offs:** product %s · architect %s · tester %s · security [ ]\n\n' "$tick" "$tick" "$tick"
    printf '## 4. Functional contracts\n\n'
    for s in $slugs; do printf '### Contract: %s\n- **Given:** a\n- **When:** b\n- **Then:** c\n\n' "${s%%:*}"; done
    printf '## 7. Failure modes\n\n### Failure: THING_FAILS\n- **Trigger:** x\n\n## 9. Acceptance criteria\n\n'
    local i=1; for s in $slugs; do printf -- '- [ ] AC-%d: does the thing — maps to %s\n' "$i" "${s%%:*}"; i=$((i+1)); done
    printf '\n## 10. Test mapping\n\n| Contract / Failure | Test name | Test file | Level | Status |\n|---|---|---|---|---|\n'
    for s in $slugs; do
      local slug="${s%%:*}" st="pending"; [[ $s == *:* ]] && st="${s#*:}"
      printf '| %s | test_%s | tests/test_forms.py | unit | %s |\n' "$slug" "$(tr 'A-Z' 'a-z' <<<"$slug")" "$st"
    done
    printf '%s\n' "$extra"
  } > "$TMP/docs/graph/specs/$name.md"
}
expect_fail() {  # $1 = pattern the report must name, $2 = why
  local out rc
  out="$(lint 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 1 ]] || { echo "expected exit 1 ($2), got $rc" >&2; echo "$out" >&2; exit 1; }
  grep -q -- "$1" <<<"$out" || { echo "report does not name it ($2): want /$1/" >&2; echo "$out" >&2; exit 1; }
}

spec SPEC-0001-forms active y "SUBMIT_VALID_FORM:green REJECT_BAD_SCHEMA:red"
spec SPEC-0002-old superseded y "OLD_RETIRED_THING:green"
printf 'def test_submit():  # SUBMIT_VALID_FORM\n    pass\n' > "$TMP/tests/test_forms.py"

# 1. uncovered live contract -> exit 1, names the slug, not the retired one
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected exit 1 on uncovered contract, got $rc" >&2; exit 1; }
grep -q 'REJECT_BAD_SCHEMA' <<<"$out" || { echo "uncovered live slug not named" >&2; exit 1; }
# NOT `! grep` — bash exempts `!`-negated commands from errexit, so a
# leaked retired slug would have sailed straight past this check.
if grep -q 'OLD_RETIRED_THING' <<<"$out"; then
  echo "retired (superseded) contract leaked into the report" >&2; exit 1
fi

# 2. --warn reports but exits 0
lint --warn >/dev/null

# 3. covered -> PASS
printf 'def test_reject():  # REJECT_BAD_SCHEMA\n    pass\n' >> "$TMP/tests/test_forms.py"
lint >/dev/null

# 4. zero test files with live contracts -> green-lie FAIL
rm "$TMP/tests/test_forms.py"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected green-lie exit 1 on zero test files, got $rc" >&2; exit 1; }
grep -qi 'green lie' <<<"$out"

# 5. REGRESSION — prefix slugs: alternation is leftmost-first, so PARSE_JSON
# once stole the match from PARSE_JSON_STRICT; the covered longer slug was
# reported uncovered while the uncovered shorter one silently earned credit.
spec SPEC-0003-parse active y "PARSE_JSON:pending PARSE_JSON_STRICT:green"
rm "$TMP/docs/graph/specs/SPEC-0001-forms.md"
printf 'def test_strict():  # PARSE_JSON_STRICT\n    pass\n' > "$TMP/tests/test_parse.py"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected exit 1: PARSE_JSON is uncovered, got $rc" >&2; echo "$out" >&2; exit 1; }
grep -q -- '- PARSE_JSON ' <<<"$out" || { echo "uncovered PARSE_JSON not named" >&2; echo "$out" >&2; exit 1; }
if grep -q -- '- PARSE_JSON_STRICT' <<<"$out"; then
  echo "covered PARSE_JSON_STRICT wrongly reported uncovered (prefix steal)" >&2; echo "$out" >&2; exit 1
fi
# 5b. REGRESSION — an UNREGISTERED extension slug must not credit its prefix:
# a test mentioning only PARSE_JSON_V2 (no such contract) once satisfied
# PARSE_JSON via bare substring match.
printf 'def test_v2():  # PARSE_JSON_V2\n    pass\n' > "$TMP/tests/test_parse.py"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || { echo "expected exit 1: no registered slug is covered, got $rc" >&2; echo "$out" >&2; exit 1; }
grep -q -- '- PARSE_JSON ' <<<"$out" || { echo "PARSE_JSON wrongly credited by PARSE_JSON_V2 substring" >&2; echo "$out" >&2; exit 1; }
rm "$TMP/docs/graph/specs/SPEC-0003-parse.md" "$TMP/tests/test_parse.py"

# 6. REGRESSION — status lives in frontmatter; the template's body line reads
# "see frontmatter", which the old body-only scan took as status "see" and
# thereby dropped EVERY template-conformant spec from coverage: a live spec
# with no test passed. The fixtures above carry both; this one proves the
# frontmatter is what decides.
spec SPEC-0004-front active y "FRONT_ONLY:pending"
printf 'def test_other():  # NOTHING_HERE\n    pass\n' > "$TMP/tests/test_other.py"
expect_fail '- FRONT_ONLY ' 'frontmatter status decides liveness'
rm "$TMP/docs/graph/specs/SPEC-0004-front.md" "$TMP/tests/test_other.py"

# ---- SHAPE ----------------------------------------------------------------
printf 'def test_a():  # SHAPE_A\n    pass\ndef test_b():  # SHAPE_B\n    pass\n' > "$TMP/tests/test_shape.py"

# 7. a draft nobody signed is shape-checked but owes no §10 rows and no coverage
spec SPEC-0005-draft draft n "SHAPE_A SHAPE_B"
python3 - "$TMP/docs/graph/specs/SPEC-0005-draft.md" <<'PY'
import sys, re; p = sys.argv[1]; s = open(p).read()
s = re.sub(r"## 10\. Test mapping.*", "## 10. Test mapping\n", s, flags=re.S); open(p, "w").write(s)
PY
lint >/dev/null || { echo "an unsigned draft must not owe §10 rows" >&2; lint; exit 1; }

# 8. ...but a SIGNED draft owes a §10 row per contract (the specify exit condition)
spec SPEC-0005-draft draft y "SHAPE_A SHAPE_B"
python3 - "$TMP/docs/graph/specs/SPEC-0005-draft.md" <<'PY'
import sys; p = sys.argv[1]; s = open(p).read()
open(p, "w").write("\n".join(ln for ln in s.splitlines() if not ln.startswith("| SHAPE_B")) + "\n")
PY
expect_fail 'contract SHAPE_B has no §10 test-mapping row (signed' 'signed draft missing a §10 row'

# 9. a live spec nobody signed is a promotion nobody signed
spec SPEC-0005-draft active n "SHAPE_A SHAPE_B"
expect_fail 'status active but unsigned by product, architect, tester' 'unsigned promotion'

# 10. duplicate slug
spec SPEC-0005-draft draft n "SHAPE_A SHAPE_A"
expect_fail 'contract SHAPE_A is declared twice' 'duplicate slug'

# 11. §9 maps to a slug the spec does not declare
spec SPEC-0005-draft draft n "SHAPE_A" $'\n- [ ] AC-9: ghost — maps to SHAPE_GHOST\n'
python3 - "$TMP/docs/graph/specs/SPEC-0005-draft.md" <<'PY'
import sys; p = sys.argv[1]; s = open(p).read()
# move the extra AC line into §9 (it was appended after §10)
extra = "- [ ] AC-9: ghost — maps to SHAPE_GHOST"
s = s.replace(extra + "\n", "").replace("## 10. Test mapping", extra + "\n\n## 10. Test mapping")
open(p, "w").write(s)
PY
expect_fail '§9 maps to SHAPE_GHOST, which is not a' '§9 dangling slug'

# 12. implemented with a row still red
spec SPEC-0005-draft implemented y "SHAPE_A:green SHAPE_B:red"
expect_fail 'implemented, but §10 row SHAPE_B is `red`' 'implemented with red row'
spec SPEC-0005-draft implemented y "SHAPE_A:green SHAPE_B:green"
lint >/dev/null

# 13. no specs dir at all -> SKIP, exit 0
rm -rf "$TMP/docs/graph/specs"
lint >/dev/null

printf 'spec lint contract: PASS\n'
