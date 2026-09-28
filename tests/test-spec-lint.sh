#!/usr/bin/env bash
# spec-lint contract, two passes. COVERAGE: fails on an uncovered live
# contract, passes when covered, ignores superseded specs, and FAILS (not
# passes) when contracts exist but zero test files match — the green-lie
# guard. SHAPE: every spec on disk — duplicate slugs, a §9 criterion mapping
# to no contract, a signed or live spec missing a §10 row, a live spec
# nobody signed, an implemented spec with a row still red — each named,
# with a draft shape-checked but never counted for coverage. Status is read
# from frontmatter; the template's body "see frontmatter" is not a status.
# HEADLINE: names every draft it did not coverage-check; a draft whose slugs
# tests already carry is a promotion WARN (never a FAIL). SLICE: --slice
# prints one contract's block, its §10 rows and, with --refs, pointers.
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

# ---- WHAT THE HEADLINE LEAVES OUT ------------------------------------------
# REGRESSION — a draft is shape-checked only, and the headline used to say so
# by omission: "PASS — no live contracts to cover (0 live spec(s))" over a
# spec already in implementation, which a report then quoted as 0 findings.
# The headline names every spec it did not coverage-check, and a draft whose
# slugs tests already carry is a WARN: its RED landed, the promotion did not.
rm -f "$TMP"/docs/graph/specs/*.md "$TMP"/tests/*

# 14. draft-only tree: the headline names the draft as not coverage-checked
spec SPEC-0006-onlydraft draft y "DRAFT_ONLY_THING"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || { echo "draft-only tree must still pass, got $rc" >&2; echo "$out" >&2; exit 1; }
grep -q 'not coverage-checked' <<<"$out" && grep -q 'SPEC-0006-onlydraft' <<<"$out" || {
  echo "headline_names_unchecked_drafts: draft-only headline does not name SPEC-0006-onlydraft as not coverage-checked" >&2
  echo "$out" >&2; exit 1; }

# 14b. mixed tree: a covered live spec's PASS headline still names the draft
spec SPEC-0007-live active y "LIVE_COVERED:green"
printf 'def test_live():  # LIVE_COVERED\n    pass\n' > "$TMP/tests/test_live.py"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || { echo "covered live + draft must pass, got $rc" >&2; echo "$out" >&2; exit 1; }
headline="$(grep '^spec lint: PASS' <<<"$out" || true)"
grep -q 'not coverage-checked' <<<"$headline" && grep -q 'SPEC-0006-onlydraft' <<<"$headline" || {
  echo "headline_names_unchecked_drafts: PASS headline over a live spec omits the draft it skipped" >&2
  echo "$out" >&2; exit 1; }
rm "$TMP/docs/graph/specs/SPEC-0007-live.md" "$TMP/tests/test_live.py"

# 15. a draft whose slug a test already carries -> WARN naming it, exit 0
printf 'def test_draft():  # DRAFT_ONLY_THING\n    pass\n' > "$TMP/tests/test_draft.py"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || { echo "draft_with_tested_slugs_warns: must WARN, not FAIL; got exit $rc" >&2; echo "$out" >&2; exit 1; }
grep -q 'WARN.*SPEC-0006-onlydraft.*draft' <<<"$out" && grep -qi 'promot' <<<"$out" || {
  echo "draft_with_tested_slugs_warns: no promotion WARN naming SPEC-0006-onlydraft" >&2
  echo "$out" >&2; exit 1; }
if grep -q -- '^  - .*SPEC-0006-onlydraft' <<<"$out"; then
  echo "draft_with_tested_slugs_warns: the promotion miss was filed as a defect, not a WARN" >&2
  echo "$out" >&2; exit 1
fi

# 15b. the WARN leaves the ratchet step's exit alone: a live spec inside its
# uncovered budget still exits 0 with the promotion WARN printed beside it
spec SPEC-0008-debt active y "DEBT_UNTESTED:pending"
out="$(lint --uncovered-budget 1 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || { echo "promotion WARN changed the budgeted run's exit: got $rc" >&2; echo "$out" >&2; exit 1; }
grep -qi 'promot' <<<"$out" || { echo "budgeted run dropped the promotion WARN" >&2; echo "$out" >&2; exit 1; }
rm "$TMP/docs/graph/specs/SPEC-0008-debt.md"

# 16. control: the same spec active and covered -> no promotion WARN, PASS
spec SPEC-0006-onlydraft active y "DRAFT_ONLY_THING:green"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || { echo "active covered control must pass, got $rc" >&2; echo "$out" >&2; exit 1; }
if grep -qi 'promot' <<<"$out"; then
  echo "an active spec was told to promote itself" >&2; echo "$out" >&2; exit 1
fi
grep -q '^spec lint: PASS — 1 live contract(s) covered' <<<"$out" || {
  echo "active control headline changed" >&2; echo "$out" >&2; exit 1; }

# 16b. REGRESSION — draft_sharing_a_live_slug_does_not_warn: hits were keyed by
# slug alone, so a draft that re-declares a slug a live spec already owns was
# told to promote itself on the live spec's test. The test proves the live
# contract, not the draft; no promotion WARN.
spec SPEC-0009-sharedraft draft y "DRAFT_ONLY_THING"
out="$(lint 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || { echo "draft_sharing_a_live_slug_does_not_warn: expected exit 0, got $rc" >&2; echo "$out" >&2; exit 1; }
if grep -qi 'promot' <<<"$out"; then
  echo "draft_sharing_a_live_slug_does_not_warn: a draft was told to promote on a live spec's test" >&2
  echo "$out" >&2; exit 1
fi
rm -f "$TMP"/docs/graph/specs/*.md "$TMP"/tests/*

# ---- SLICE ------------------------------------------------------------------
# `--slice SLUG...` prints only what one contract needs: its `### Contract:` or
# `### Failure:` block up to the next heading of the same or higher level
# (headings inside fences are text), its §10 row(s) each under its table
# header, and with --refs file:line pointers to the §6/§7 headings the block
# cites, never their text. --lines prints ranges. Exit 0 all found, 1 any
# missing (found ones still printed), 2 usage error.
SL="$TMP/slice"
mkdir -p "$SL/docs/graph/specs"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$SL/docs/graph/"
slice() { python3 "$SL/docs/graph/spec-lint.py" --slice "$@"; }
SPECF="$SL/docs/graph/specs/SPEC-9999-slice.md"
cat > "$SPECF" <<'MD'
---
status: draft
---
# SPEC-9999 slice fixture
## 4. Functional contracts
### 4.1 Group A
### Contract: ALPHA_HOLDS
Alpha body, see §6.2 and §6.3.1 and §7 `BETA_BREAKS`, not §5.
```
### Contract: NOT_A_HEADING_IN_A_FENCE
```
#### A sub-heading inside the block

### Contract: GAMMA_HOLDS
Gamma body.
## 6. Data shapes
### 6.2 The record
Record text.
### 6.3 The run
#### 6.3.1 The detail
## 7. Failure modes
### Failure: BETA_BREAKS
Beta body.
## 10. Test mapping
### Contracts

| Slug | Level | Status |
|---|---|---|
| ALPHA_HOLDS | unit | green |
| GAMMA_HOLDS | unit | pending |

### Failure modes

| Slug | Level | Status |
|---|---|---|
| BETA_BREAKS | unit | green |
| `ALPHA_HOLDS` | structural | green |
## 11. Open questions
| ALPHA_HOLDS | not in the mapping | x |
MD
line_of() { grep -n -F -x -- "$1" "$SPECF" | head -1 | cut -d: -f1; }
sfail() { echo "$1" >&2; echo "$2" >&2; exit 1; }

# 17. slice_block_runs_to_next_same_or_higher_heading (deeper ones kept)
out="$(slice ALPHA_HOLDS 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || sfail "slice ALPHA_HOLDS: expected exit 0, got $rc" "$out"
grep -q -F 'Alpha body' <<<"$out" || sfail "slice: contract block text missing" "$out"
grep -q -F '#### A sub-heading inside the block' <<<"$out" || sfail "slice: deeper heading cut from the block" "$out"
if grep -q -F 'Gamma body' <<<"$out"; then sfail "slice: block ran past the next same-level heading" "$out"; fi

# 18. slice_rows_come_from_10_only_each_under_its_header
grep -q -F '| ALPHA_HOLDS | unit | green |' <<<"$out" || sfail "slice: §10 contract row missing" "$out"
grep -q -F '| `ALPHA_HOLDS` | structural | green |' <<<"$out" || sfail "slice: backticked §10 row missing" "$out"
if grep -q -F 'not in the mapping' <<<"$out"; then sfail "slice: a row outside §10 leaked in" "$out"; fi
[[ "$(grep -c -F '| Slug | Level | Status |' <<<"$out")" -eq 2 ]] || sfail "slice: each row must sit under its own table header (want 2)" "$out"
if grep -q -F 'GAMMA_HOLDS | unit' <<<"$out"; then sfail "slice: another slug's row leaked in" "$out"; fi

# 19. slice_failure_slug_is_sliced_like_a_contract
out="$(slice BETA_BREAKS 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || sfail "slice BETA_BREAKS: expected exit 0, got $rc" "$out"
grep -q -F 'Beta body.' <<<"$out" || sfail "slice: failure block missing" "$out"
if grep -q -F '## 10.' <<<"$out"; then sfail "slice: failure block ran into §10" "$out"; fi

# 20. slice_refs_are_pointers_never_text
out="$(slice ALPHA_HOLDS --refs 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || sfail "slice --refs: expected exit 0, got $rc" "$out"
for h in '### 6.2 The record' '#### 6.3.1 The detail' '## 7. Failure modes'; do
  grep -q -F "SPEC-9999-slice.md:$(line_of "$h")	$h" <<<"$out" || sfail "slice --refs: no pointer to '$h'" "$out"
done
if grep -q -F 'Record text.' <<<"$out"; then sfail "slice --refs: printed a cited section's text" "$out"; fi
if grep -q -F '## 5.' <<<"$out"; then sfail "slice --refs: pointed outside §6/§7" "$out"; fi

# 21. slice_lines_prints_ranges_for_several_slugs
out="$(slice --lines ALPHA_HOLDS BETA_BREAKS 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || sfail "slice --lines: expected exit 0, got $rc" "$out"
a="$(line_of '### Contract: ALPHA_HOLDS')"; b="$(line_of '### Failure: BETA_BREAKS')"
grep -q -F "SPEC-9999-slice.md:$a-$((a + 5))	ALPHA_HOLDS contract block" <<<"$out" || sfail "slice --lines: wrong ALPHA_HOLDS range" "$out"
grep -q -F "SPEC-9999-slice.md:$b-$((b + 1))	BETA_BREAKS failure block" <<<"$out" || sfail "slice --lines: wrong BETA_BREAKS range" "$out"
[[ "$(grep -c -F '§10 row' <<<"$out")" -eq 3 ]] || sfail "slice --lines: want 3 '§10 row' ranges" "$out"
if grep -q -F 'Alpha body' <<<"$out"; then sfail "slice --lines: printed text instead of ranges" "$out"; fi

# 22. slice_unknown_slug_exits_one_and_prints_the_known_ones
errf="$TMP/slice.err"
out="$(slice NOPE_MISSING GAMMA_HOLDS 2>"$errf")" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || sfail "slice unknown slug: expected exit 1, got $rc" "$out"
grep -q -F 'NOPE_MISSING' "$errf" || sfail "slice unknown slug: stderr does not name it" "$(cat "$errf")"
grep -q -F 'Gamma body.' <<<"$out" || sfail "slice unknown slug: the found slug was not printed" "$out"

# 23. slice_fenced_heading_is_not_a_slug
out="$(slice NOT_A_HEADING_IN_A_FENCE 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || sfail "slice: a heading inside a fence was sliced (exit $rc)" "$out"

# 23b. REGRESSION — slice_fence_closes_only_on_its_own_marker: a fence line
# once toggled the state whatever its marker, so a `~~~` inside a ``` block
# closed it early. The fenced example heading got sliced and the real heading
# after the fence became unsliceable. CommonMark: a fence closes only on the
# same character, at least as long as the opener.
FENCEF="$SL/docs/graph/specs/SPEC-9998-fence.md"
cat > "$FENCEF" <<'MD'
---
status: draft
---
# SPEC-9998 fence fixture
## 4. Functional contracts
### Contract: BEFORE_FENCE
An example of a spec, fenced:
```markdown
~~~ an unclosed tilde line is fence text, not a fence
### Contract: HIDDEN_EXAMPLE
```
### Contract: AFTER_FENCE
After body.
## 10. Test mapping
MD
out="$(slice HIDDEN_EXAMPLE 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || sfail "slice_fence_closes_only_on_its_own_marker: a heading inside a \`\`\` fence was sliced (exit $rc)" "$out"
out="$(slice AFTER_FENCE 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || sfail "slice_fence_closes_only_on_its_own_marker: the real heading after the fence is unsliceable (exit $rc)" "$out"
grep -q -F 'After body.' <<<"$out" || sfail "slice_fence_closes_only_on_its_own_marker: AFTER_FENCE block text missing" "$out"
rm "$FENCEF"

# 23c. slice_slug_in_two_specs_notes_both_files: a slug declared in two specs
# is sliced from each, and stderr says so, naming both files, so a reader
# does not take one spec's block for the only one.
SHAREA="$SL/docs/graph/specs/SPEC-9996-share-a.md"
SHAREB="$SL/docs/graph/specs/SPEC-9997-share-b.md"
for f in "$SHAREA" "$SHAREB"; do
  printf -- '---\nstatus: draft\n---\n# fixture\n## 4. Functional contracts\n### Contract: SHARED_TWICE\nShared body.\n' > "$f"
done
out="$(slice SHARED_TWICE 2>"$errf")" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || sfail "slice_slug_in_two_specs_notes_both_files: expected exit 0, got $rc" "$out$(cat "$errf")"
grep -q -F 'SHARED_TWICE' "$errf" && grep -q -F 'SPEC-9996-share-a.md' "$errf" && grep -q -F 'SPEC-9997-share-b.md' "$errf" || \
  sfail "slice_slug_in_two_specs_notes_both_files: stderr does not name the slug and both files" "stderr: $(cat "$errf")"
rm "$SHAREA" "$SHAREB"

# 24. slice_without_slugs_is_a_usage_error
out="$(slice 2>&1)" && rc=0 || rc=$?
[[ $rc -eq 2 ]] || sfail "slice with no SLUG: expected usage exit 2, got $rc" "$out"

# 13. no specs dir at all -> SKIP, exit 0
rm -rf "$TMP/docs/graph/specs"
lint >/dev/null


# ---- ROW CELLS (plan increment 5) ------------------------------------------
# A §10 row whose cell count differs from its header reads its status from the
# wrong column and nothing says so. A collecting block: each case prints
# `FAIL <label>: <why>` and the suite exits 1 after the last one, so no case
# hides another. No spec owns spec-lint's table parsing (plan increment 5).
set +e
CELLS_FAILED=0
CL="$TMP/cells"
mkdir -p "$CL/docs/graph/specs" "$CL/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$CL/docs/graph/"
printf 'def test_cells():  # CELL_ALPHA CELL_BETA\n    pass\n' > "$CL/tests/test_cells.py"
cfail() { printf 'FAIL %s: %s\n' "$1" "$2"; CELLS_FAILED=1; }
crun() { COUT="$(python3 "$CL/docs/graph/spec-lint.py" 2>&1)"; CRC=$?; }
# cells_spec NAME ROW_ALPHA ROW_BETA: a signed draft (it owes a §10 row per
# contract) with a five-cell header and the two rows given verbatim.
cells_spec() {
  local f="$CL/docs/graph/specs/$1.md"
  rm -f "$CL"/docs/graph/specs/*.md
  {
    printf -- '---\nstatus: draft\nstatus_date: 2026-09-28\n---\n\n# %s\n\n## 0. Metadata\n' "$1"
    printf -- '- **Status:** see frontmatter (single home)\n- **Sign-offs:** product [x] · architect [x] · tester [x] · security [ ]\n\n'
    printf '## 4. Functional contracts\n\n### Contract: CELL_ALPHA\n- **Given:** a\n\n### Contract: CELL_BETA\n- **Given:** b\n\n'
    printf '## 7. Failure modes\n\n### Failure: CELL_FAILS\n- **Trigger:** x\n\n'
    printf '## 9. Acceptance criteria\n\n- [ ] AC-1: a — maps to CELL_ALPHA\n- [ ] AC-2: b — maps to CELL_BETA\n\n'
    printf '## 10. Test mapping\n\n| Contract / Failure | Test name | Test file | Level | Status |\n|---|---|---|---|---|\n'
    printf '%s\n%s\n' "$2" "$3"
  } > "$f"
  CSPEC="$f"
}
# the 1-based line of the file that holds $1 exactly
cline() { grep -n -F -x -- "$1" "$CSPEC" | head -1 | cut -d: -f1; }
# one output line holds the spec name, the line number and both counts
cells_named() {  # $1=spec file name $2=line $3=header count $4=row count
  python3 -c '
import re, sys
name, line, h, r, out = sys.argv[1:6]
word = lambda n, s: re.search(r"(?<!\d)" + n + r"(?!\d)", s)
sys.exit(0 if any(name in l and word(line, l) and word(h, l) and word(r, l)
                  for l in out.splitlines()) else 1)' "$1" "$2" "$3" "$4" "$COUT"
}
GOOD_A='| CELL_ALPHA | test_cells | tests/test_cells.py | unit | red |'

case_row_one_cell_fewer() {
  # G2a (increment 5a): a §10 row with one cell fewer than its header fails,
  # and the finding names the spec, the line and both counts (5 and 4).
  local L=G2a row='| CELL_BETA | test_cells | tests/test_cells.py | red |' n
  cells_spec SPEC-0101-cells "$GOOD_A" "$row"; n="$(cline "$row")"
  crun
  [ "$CRC" -eq 1 ] || { cfail $L "expected exit 1, got $CRC"; return; }
  cells_named SPEC-0101-cells.md "$n" 5 4 || cfail $L "no finding line naming SPEC-0101-cells.md, line $n, 5 and 4 cells"
}
case_row_one_cell_more() {
  # G2b (increment 5b): one cell more fails the same way (5 and 6).
  local L=G2b row='| CELL_BETA | test_cells | tests/test_cells.py | unit | red | extra |' n
  cells_spec SPEC-0102-cells "$GOOD_A" "$row"; n="$(cline "$row")"
  crun
  [ "$CRC" -eq 1 ] || { cfail $L "expected exit 1, got $CRC"; return; }
  cells_named SPEC-0102-cells.md "$n" 5 6 || cfail $L "no finding line naming SPEC-0102-cells.md, line $n, 5 and 6 cells"
}
case_row_escaped_pipe_is_one_cell() {
  # G2c (increment 5c, guard): a cell holding an escaped pipe `\|` is one cell.
  local L=G2c
  cells_spec SPEC-0103-cells "$GOOD_A" '| CELL_BETA | test_a\|b | tests/test_cells.py | unit | red |'
  crun
  [ "$CRC" -eq 0 ] || cfail $L "an escaped pipe was counted as a cell boundary (exit $CRC): $(grep -m1 -- '  - ' <<<"$COUT")"
}
case_row_outer_pipes_optional() {
  # G2d (increment 5d, guard): leading and trailing pipes are optional, as GFM
  # allows. The table after §10's is a second table whose rows drop them.
  local L=G2d
  cells_spec SPEC-0104-cells "$GOOD_A" '| CELL_BETA | test_cells | tests/test_cells.py | unit | red'
  printf '\n| Note | Detail |\n|---|---|\nfirst | one\n| second | two\nthird | three |\n' >> "$CSPEC"
  crun
  [ "$CRC" -eq 0 ] || cfail $L "a row without an outer pipe was refused (exit $CRC): $(grep -m1 -- '  - ' <<<"$COUT")"
}
for c in case_row_one_cell_fewer case_row_one_cell_more \
         case_row_escaped_pipe_is_one_cell case_row_outer_pipes_optional; do
  "$c"
done
set -e
if [ "$CELLS_FAILED" -ne 0 ]; then
  printf 'spec lint contract: FAIL — the row-cell block has failing cases (above)\n'
  exit 1
fi

printf 'spec lint contract: PASS\n'
