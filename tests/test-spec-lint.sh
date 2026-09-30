#!/usr/bin/env bash
# spec-lint contract. COVERAGE: an uncovered live contract fails, a covered one
# passes, superseded specs are ignored, and zero matching test files is a
# green-lie FAIL. SHAPE: duplicate slugs, a §9 criterion mapping to no
# contract, a signed or live spec missing a §10 row, a live spec nobody signed,
# an implemented spec with a red row; a draft is shape-checked, never counted
# for coverage. Status is read from frontmatter. HEADLINE: names every draft it
# did not coverage-check; a draft whose slugs tests carry is a promotion WARN.
# SLICE: --slice prints one contract's block, its §10 rows and, with --refs,
# pointers. ROW CELLS: a §10 row's cell count must match its header.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/tests/helpers/lintcase.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# One harness. run_rc <want> <cmd...> runs cmd, keeps its output in $out and
# fails unless it exits <want>; has/hasnt take grep flags and a pattern.
CASE=""
fail() { echo "FAIL ${CASE:+[$CASE] }$1" >&2; [ -n "${out:-}" ] && echo "$out" >&2; exit 1; }
run_rc() {
  local want="$1"; shift
  out="$("$@" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq $want ]] || fail "exit $rc, want $want: $*"
}
has() { grep -q "$@" <<<"$out" || fail "output lacks: ${*: -1}"; }
hasnt() { if grep -q "$@" <<<"$out"; then fail "output holds: ${*: -1}"; fi; }

mkdir -p "$TMP/docs/graph/specs" "$TMP/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$TMP/docs/graph/"
lint() { python3 "$TMP/docs/graph/spec-lint.py" "$@"; }
SPECS="$TMP/docs/graph/specs"

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
  } > "$SPECS/$name.md"
}

# ---- COVERAGE -----------------------------------------------------------------
spec SPEC-0001-forms active y "SUBMIT_VALID_FORM:green REJECT_BAD_SCHEMA:red"
spec SPEC-0002-old superseded y "OLD_RETIRED_THING:green"
printf 'def test_submit():  # SUBMIT_VALID_FORM\n    pass\n' > "$TMP/tests/test_forms.py"

# 1. uncovered live contract -> exit 1, names the slug, not the retired one
CASE=1; run_rc 1 lint
has REJECT_BAD_SCHEMA
hasnt OLD_RETIRED_THING

# 2. --warn reports but exits 0
CASE=2; run_rc 0 lint --warn

# 3. covered -> PASS
printf 'def test_reject():  # REJECT_BAD_SCHEMA\n    pass\n' >> "$TMP/tests/test_forms.py"
CASE=3; run_rc 0 lint

# 4. zero test files with live contracts -> green-lie FAIL
rm "$TMP/tests/test_forms.py"
CASE=4; run_rc 1 lint
has -i 'green lie'

# 5. prefix slugs: the covered PARSE_JSON_STRICT must not credit PARSE_JSON.
spec SPEC-0003-parse active y "PARSE_JSON:pending PARSE_JSON_STRICT:green"
rm "$SPECS/SPEC-0001-forms.md"
printf 'def test_strict():  # PARSE_JSON_STRICT\n    pass\n' > "$TMP/tests/test_parse.py"
CASE=5; run_rc 1 lint
has -- '- PARSE_JSON '
hasnt -- '- PARSE_JSON_STRICT'
# 5b. an unregistered extension slug (PARSE_JSON_V2) must not credit its prefix.
printf 'def test_v2():  # PARSE_JSON_V2\n    pass\n' > "$TMP/tests/test_parse.py"
CASE=5b; run_rc 1 lint
has -- '- PARSE_JSON '
rm "$SPECS/SPEC-0003-parse.md" "$TMP/tests/test_parse.py"

# 6. frontmatter status decides liveness; the body "see frontmatter" is not a
#    status.
spec SPEC-0004-front active y "FRONT_ONLY:pending"
printf 'def test_other():  # NOTHING_HERE\n    pass\n' > "$TMP/tests/test_other.py"
CASE=6; run_rc 1 lint
has -- '- FRONT_ONLY '
rm "$SPECS/SPEC-0004-front.md" "$TMP/tests/test_other.py"

# ---- SHAPE ----------------------------------------------------------------
printf 'def test_a():  # SHAPE_A\n    pass\ndef test_b():  # SHAPE_B\n    pass\n' > "$TMP/tests/test_shape.py"
DRAFT="$SPECS/SPEC-0005-draft.md"

# 7. a draft nobody signed is shape-checked but owes no §10 rows and no coverage
spec SPEC-0005-draft draft n "SHAPE_A SHAPE_B"
python3 - "$DRAFT" <<'PY'
import sys, re; p = sys.argv[1]; s = open(p).read()
s = re.sub(r"## 10\. Test mapping.*", "## 10. Test mapping\n", s, flags=re.S); open(p, "w").write(s)
PY
CASE=7; run_rc 0 lint

# 8. ...but a SIGNED draft owes a §10 row per contract (the specify exit condition)
spec SPEC-0005-draft draft y "SHAPE_A SHAPE_B"
python3 - "$DRAFT" <<'PY'
import sys; p = sys.argv[1]; s = open(p).read()
open(p, "w").write("\n".join(ln for ln in s.splitlines() if not ln.startswith("| SHAPE_B")) + "\n")
PY
CASE=8; run_rc 1 lint
has -- 'contract SHAPE_B has no §10 test-mapping row (signed'

# 9. a live spec nobody signed is a promotion nobody signed
spec SPEC-0005-draft active n "SHAPE_A SHAPE_B"
CASE=9; run_rc 1 lint
has -- 'status active but unsigned by product, architect, tester'

# 10. duplicate slug
spec SPEC-0005-draft draft n "SHAPE_A SHAPE_A"
CASE=10; run_rc 1 lint
has -- 'contract SHAPE_A is declared twice'

# 11. §9 maps to a slug the spec does not declare
spec SPEC-0005-draft draft n "SHAPE_A" $'\n- [ ] AC-9: ghost — maps to SHAPE_GHOST\n'
python3 - "$DRAFT" <<'PY'
import sys; p = sys.argv[1]; s = open(p).read()
# move the extra AC line into §9 (it was appended after §10)
extra = "- [ ] AC-9: ghost — maps to SHAPE_GHOST"
s = s.replace(extra + "\n", "").replace("## 10. Test mapping", extra + "\n\n## 10. Test mapping")
open(p, "w").write(s)
PY
CASE=11; run_rc 1 lint
has -- '§9 maps to SHAPE_GHOST, which is not a'

# 12. implemented with a row still red
spec SPEC-0005-draft implemented y "SHAPE_A:green SHAPE_B:red"
CASE=12; run_rc 1 lint
has -- 'implemented, but §10 row SHAPE_B is `red`'
spec SPEC-0005-draft implemented y "SHAPE_A:green SHAPE_B:green"
run_rc 0 lint

# ---- WHAT THE HEADLINE LEAVES OUT ------------------------------------------
rm -f "$SPECS"/*.md "$TMP"/tests/*

# 14. headline_names_unchecked_drafts: a draft-only tree names the draft
spec SPEC-0006-onlydraft draft y "DRAFT_ONLY_THING"
CASE=14; run_rc 0 lint
has 'not coverage-checked'
has SPEC-0006-onlydraft

# 14b. mixed tree: a covered live spec's PASS headline still names the draft
spec SPEC-0007-live active y "LIVE_COVERED:green"
printf 'def test_live():  # LIVE_COVERED\n    pass\n' > "$TMP/tests/test_live.py"
CASE=14b; run_rc 0 lint
out="$(grep '^spec lint: PASS' <<<"$out" || true)"
has 'not coverage-checked'
has SPEC-0006-onlydraft
rm "$SPECS/SPEC-0007-live.md" "$TMP/tests/test_live.py"

# 15. draft_with_tested_slugs_warns: WARN naming the draft, exit 0, not a defect
printf 'def test_draft():  # DRAFT_ONLY_THING\n    pass\n' > "$TMP/tests/test_draft.py"
CASE=15; run_rc 0 lint
has 'WARN.*SPEC-0006-onlydraft.*draft'
has -i promot
hasnt -- '^  - .*SPEC-0006-onlydraft'

# 15b. the WARN leaves the ratchet step's exit alone: a live spec inside its
#      uncovered budget still exits 0 with the promotion WARN beside it
spec SPEC-0008-debt active y "DEBT_UNTESTED:pending"
CASE=15b; run_rc 0 lint --uncovered-budget 1
has -i promot
rm "$SPECS/SPEC-0008-debt.md"

# 16. control: the same spec active and covered -> no promotion WARN, PASS
spec SPEC-0006-onlydraft active y "DRAFT_ONLY_THING:green"
CASE=16; run_rc 0 lint
hasnt -i promot
has '^spec lint: PASS — 1 live contract(s) covered'

# 16b. draft_sharing_a_live_slug_does_not_warn: the live spec's test proves the
#      live contract, not a draft re-declaring its slug.
spec SPEC-0009-sharedraft draft y "DRAFT_ONLY_THING"
CASE=16b; run_rc 0 lint
hasnt -i promot
rm -f "$SPECS"/*.md "$TMP"/tests/*

# 13. no specs dir at all -> SKIP, exit 0
rm -rf "$SPECS"
CASE=13; run_rc 0 lint

# ---- SLICE ------------------------------------------------------------------
# `--slice SLUG...` prints a `### Contract:`/`### Failure:` block up to the next
# heading of the same or higher level (fenced headings are text), its §10
# row(s) each under its table header, and with --refs file:line pointers to the
# §6/§7 headings it cites. --lines prints ranges. Exit 0 all found, 1 any
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

# Block bounds (17 slice_block_runs_to_next_same_or_higher_heading, 19
# slice_failure_slug_is_sliced_like_a_contract, 23b
# slice_fence_closes_only_on_its_own_marker).
CASE=slice-block; run_rc 0 slice ALPHA_HOLDS
has -F 'Alpha body'
has -F '#### A sub-heading inside the block'
hasnt -F 'Gamma body'
ALPHA_OUT="$out"
run_rc 0 slice BETA_BREAKS
has -F 'Beta body.'
hasnt -F '## 10.'
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
run_rc 1 slice HIDDEN_EXAMPLE
run_rc 0 slice AFTER_FENCE
has -F 'After body.'
rm "$FENCEF"

# §10 rows and pointers (18 slice_rows_come_from_10_only_each_under_its_header,
# 20 slice_refs_are_pointers_never_text, 21
# slice_lines_prints_ranges_for_several_slugs).
CASE=slice-rows; out="$ALPHA_OUT"
has -F '| ALPHA_HOLDS | unit | green |'
has -F '| `ALPHA_HOLDS` | structural | green |'
hasnt -F 'not in the mapping'
[[ "$(grep -c -F '| Slug | Level | Status |' <<<"$out")" -eq 2 ]] \
  || fail "each row must sit under its own table header (want 2)"
hasnt -F 'GAMMA_HOLDS | unit'
run_rc 0 slice ALPHA_HOLDS --refs
for h in '### 6.2 The record' '#### 6.3.1 The detail' '## 7. Failure modes'; do
  has -F "SPEC-9999-slice.md:$(line_of "$h")	$h"
done
hasnt -F 'Record text.'
hasnt -F '## 5.'
run_rc 0 slice --lines ALPHA_HOLDS BETA_BREAKS
a="$(line_of '### Contract: ALPHA_HOLDS')"; b="$(line_of '### Failure: BETA_BREAKS')"
has -F "SPEC-9999-slice.md:$a-$((a + 5))	ALPHA_HOLDS contract block"
has -F "SPEC-9999-slice.md:$b-$((b + 1))	BETA_BREAKS failure block"
[[ "$(grep -c -F '§10 row' <<<"$out")" -eq 3 ]] || fail "--lines: want 3 '§10 row' ranges"
hasnt -F 'Alpha body'

# Exit codes and stderr (22 slice_unknown_slug_exits_one_and_prints_the_known_ones,
# 23 slice_fenced_heading_is_not_a_slug, 23c
# slice_slug_in_two_specs_notes_both_files, 24 slice_without_slugs_is_a_usage_error).
CASE=slice-exit; errf="$TMP/slice.err"
out="$(slice NOPE_MISSING GAMMA_HOLDS 2>"$errf")" && rc=0 || rc=$?
[[ $rc -eq 1 ]] || fail "unknown slug: exit $rc, want 1"
has -F 'Gamma body.'
out="$(cat "$errf")"; has -F NOPE_MISSING
run_rc 1 slice NOT_A_HEADING_IN_A_FENCE
for f in SPEC-9996-share-a SPEC-9997-share-b; do
  printf -- '---\nstatus: draft\n---\n# fixture\n## 4. Functional contracts\n### Contract: SHARED_TWICE\nShared body.\n' \
    > "$SL/docs/graph/specs/$f.md"
done
out="$(slice SHARED_TWICE 2>"$errf")" && rc=0 || rc=$?
[[ $rc -eq 0 ]] || fail "slug in two specs: exit $rc, want 0"
out="$(cat "$errf")"
has -F SHARED_TWICE
has -F SPEC-9996-share-a.md
has -F SPEC-9997-share-b.md
run_rc 2 slice
CASE=""

# ---- ROW CELLS ------------------------------------------------------------
# A §10 row whose cell count differs from its header reads its status from the
# wrong column. Cases run through collect_case, so no case hides another.
CL="$TMP/cells"
mkdir -p "$CL/docs/graph/specs" "$CL/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$CL/docs/graph/"
printf 'def test_cells():  # CELL_ALPHA CELL_BETA\n    pass\n' > "$CL/tests/test_cells.py"
cells_lint() { python3 "$CL/docs/graph/spec-lint.py"; }
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
cline() { grep -n -F -x -- "$1" "$CSPEC" | head -1 | cut -d: -f1; }
# one output line holds the spec name, the line number and both counts
cells_named() {  # $1=spec file name $2=line $3=header count $4=row count
  python3 -c '
import re, sys
name, line, h, r, out = sys.argv[1:6]
word = lambda n, s: re.search(r"(?<!\d)" + n + r"(?!\d)", s)
sys.exit(0 if any(name in l and word(line, l) and word(h, l) and word(r, l)
                  for l in out.splitlines()) else 1)' "$1" "$2" "$3" "$4" "$out" \
    || fail "no finding line naming $1, line $2, $3 and $4 cells"
}
GOOD_A='| CELL_ALPHA | test_cells | tests/test_cells.py | unit | red |'

case_row_one_cell_fewer() {
  # G2a: one cell fewer fails, naming spec, line and both counts (5 and 4).
  # G2b (folded): one cell more fails the same way (5 and 6).
  local row n
  row='| CELL_BETA | test_cells | tests/test_cells.py | red |'
  cells_spec SPEC-0101-cells "$GOOD_A" "$row"; n="$(cline "$row")"
  run_rc 1 cells_lint; cells_named SPEC-0101-cells.md "$n" 5 4
  row='| CELL_BETA | test_cells | tests/test_cells.py | unit | red | extra |'
  cells_spec SPEC-0102-cells "$GOOD_A" "$row"; n="$(cline "$row")"
  run_rc 1 cells_lint; cells_named SPEC-0102-cells.md "$n" 5 6
}
case_row_escaped_pipe_is_one_cell() {
  # G2c (guard): an escaped pipe `\|` is one cell.
  # G2d (guard, folded): outer pipes are optional, as GFM allows; the table
  # after §10's is a second table whose rows drop them.
  cells_spec SPEC-0103-cells "$GOOD_A" '| CELL_BETA | test_a\|b | tests/test_cells.py | unit | red |'
  run_rc 0 cells_lint
  cells_spec SPEC-0104-cells "$GOOD_A" '| CELL_BETA | test_cells | tests/test_cells.py | unit | red'
  printf '\n| Note | Detail |\n|---|---|\nfirst | one\n| second | two\nthird | three |\n' >> "$CSPEC"
  run_rc 0 cells_lint
}
collect_case G2a+G2b case_row_one_cell_fewer "a row with a cell count off its header fails, named"
collect_case G2c+G2d case_row_escaped_pipe_is_one_cell "escaped pipes and optional outer pipes are not miscounted"
[ "$CASE_FAILED" -eq 0 ] || { printf 'spec lint contract: FAIL — the row-cell block has failing cases (above)\n'; exit 1; }

# ---- PROVED BY A RUN ----------------------------------------------------------
# P1: a plan increment reading `Tests to write (RED): none — <why>; proved by
# <run>` covers the contracts it names (grill.increment-shape); `none —
# consolidation` covers nothing.
PR="$TMP/proved"
mkdir -p "$PR/docs/graph/specs" "$PR/docs/graph/plans" "$PR/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$PR/docs/graph/"
printf 'def test_sel():  # SELECT_TESTED\n    pass\n' > "$PR/tests/test_sel.py"
SPECS="$PR/docs/graph/specs"
spec SPEC-0201-select active y "SELECT_TESTED:green SELECT_BY_LABEL:green"
pr_plan() { printf '## 9. Increments\n\n### Increment 1 — Add the selector\n- Spec contracts: SPEC-0201/SELECT_BY_LABEL\n- Tests to write (RED): %s\n' "$1" > "$PR/docs/graph/plans/grill.md"; }
pr_plan 'none — a declarative selector; proved by `pipeline --dry-run`'
CASE=P1; run_rc 0 python3 "$PR/docs/graph/spec-lint.py"
has 'proved by a run.*SELECT_BY_LABEL'
pr_plan 'none — consolidation'
run_rc 1 python3 "$PR/docs/graph/spec-lint.py"
has -- '- SELECT_BY_LABEL '
CASE=""

printf 'spec lint contract: PASS\n'
