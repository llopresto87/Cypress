#!/usr/bin/env bash
# test-graft-tools.sh — the graft support tools do what graft.md relies on:
#   graft-graph-engine.py  reconciles an engine: adopts the seed body, keeps the
#                          plant config, detects a plant superset.
#   graft-audit.py         classifies backups, gates buried customizations and
#                          knowledge overwrites, and reports unfilled scaffolds.
#   graft-ledger.py        classifies each seed-owned file and finds the base.
#   graft-run.py           drives a graft in a stage and prints the gate table.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE="$ROOT/tools/graft-graph-engine.py"
AUDIT="$ROOT/tools/graft-audit.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

# collect_case (tests/helpers/lintcase.sh) runs each case; a case that starts
# with `set -e` (the older GT cases) ends in `return 0`, so a closing
# `grep ... && fail` that finds nothing is a pass.
. "$ROOT/tests/helpers/lintcase.sh"

# ---- graft-graph-engine.py ------------------------------------------------
# seed engine: new helper line + default KINDS + KIND_PREFIX
case_engine_merge_adopts_body_unions_kinds() {
  # GT01
  set -e
  cat > "$TMP/seed-lint.py" <<'PY'
ROOT_ID = "root"
KINDS = {"root", "subsystem", "stack"}
KIND_PREFIX = {}
def new_helper():  # engine improvement absent from the old plant
    return 1
def check():
    return new_helper()
PY
  # plant engine: OLD (no new_helper), custom KINDS (adds 'devops', LACKS the
  # seed's newer 'stack'), no KIND_PREFIX at all
  cat > "$TMP/plant-lint.py" <<'PY'
ROOT_ID = "root"
KINDS = {"root", "subsystem", "devops"}
def check():
    return 0
PY
  python3 "$ENGINE" "$TMP/plant-lint.py" "$TMP/seed-lint.py" >"$TMP/out" 2>&1 || fail "engine merge exit"
  grep -q "new_helper" "$TMP/plant-lint.py" || fail "engine body not adopted"
  # KINDS is an additive-vocabulary set: the union must keep the plant's own
  # 'devops' AND gain the seed's newer 'stack' — keeping the plant's set
  # wholesale would drop 'stack' and every node of that kind would fail lint.
  grep -q 'KINDS = {"root", "subsystem", "stack", "devops"}' "$TMP/plant-lint.py" || fail "plant KINDS not unioned with the seed's new members"
  grep -q "KIND_PREFIX = {}" "$TMP/plant-lint.py" || fail "seed-default KIND_PREFIX not adopted"
  return 0
}
collect_case GT01 case_engine_merge_adopts_body_unions_kinds "engine merge: adopted body, UNIONED KINDS (kept plant + gained seed), adopted default KIND_PREFIX"

# superset: plant already has everything seed has, plus extra -> KEEP-PLANT
case_engine_merge_superset_keep_plant() {
  # GT03
  set -e
  cat > "$TMP/super.py" <<'PY'
ROOT_ID = "root"
KINDS = {"root", "subsystem", "stack"}
KIND_PREFIX = {}
def new_helper():
    return 1
def check():
    return new_helper()
def extra_capability():
    return 2
PY
  python3 "$ENGINE" "$TMP/super.py" "$TMP/seed-lint.py" 2>&1 | grep -q "KEEP-PLANT" || fail "superset not detected"
  grep -q "extra_capability" "$TMP/super.py" || fail "superset engine mutated (must be untouched)"
  return 0
}
collect_case GT03 case_engine_merge_superset_keep_plant "superset detection (KEEP-PLANT, unchanged)"

# a preserved config value keeps the comment that explains it; the backward
# walk stops at a blank line, so an unrelated module note does not travel.
case_engine_merge_config_keeps_its_comment() {
  # GT04; its second pass holds GT02 (a current engine is a no-op)
  set -e
  cat > "$TMP/cseed.py" <<'PY'
# a module note about the engine as a whole, not about any one knob

ROOT_ID = "root"
KINDS = {"root", "subsystem", "stack"}
KIND_PREFIX = {}
def check():
    return 1
PY
  cat > "$TMP/cplant.py" <<'PY'
# a module note about the engine as a whole, not about any one knob

# the root id is the deploy name rather than the repo name: the router keys on it
ROOT_ID = "app"
# 'operator' is this project's own kind; the seed does not ship it
KINDS = {"root", "subsystem", "operator"}
KIND_PREFIX = {}
PY
  python3 "$ENGINE" "$TMP/cplant.py" "$TMP/cseed.py" >"$TMP/cout" 2>&1 || fail "commented config merge exit"
  grep -q "def check" "$TMP/cplant.py" || fail "engine body not adopted alongside commented config"
  grep -A1 "the root id is the deploy name" "$TMP/cplant.py" | grep -q '^ROOT_ID = "app"$' \
    || { cat "$TMP/cplant.py"; fail "the comment explaining a kept value did not travel with it"; }
  grep -A1 "own kind; the seed does not ship it" "$TMP/cplant.py" | grep -q '^KINDS = {"root", "subsystem", "stack", "operator"}$' \
    || { cat "$TMP/cplant.py"; fail "the comment explaining a unioned value did not travel with it"; }
  [ "$(grep -c "a module note about the engine" "$TMP/cplant.py")" -eq 1 ] \
    || { cat "$TMP/cplant.py"; fail "an unrelated module comment was swallowed by the backward walk"; }
  cp "$TMP/cplant.py" "$TMP/cplant.before"
  python3 "$ENGINE" "$TMP/cplant.py" "$TMP/cseed.py" 2>&1 | grep -q "already current" || fail "commented merge not idempotent"
  cmp -s "$TMP/cplant.py" "$TMP/cplant.before" || fail "a second pass rewrote a file it called current"
  return 0
}
collect_case GT04 case_engine_merge_config_keeps_its_comment "preserved config carries its comment; unrelated module comment untouched"

# ---- graft-audit.py -------------------------------------------------------
# 6.0.0 plant layout: machinery home is docs/graph/{protocols,skills,agents,
# method,templates}/ (seed-owned); tool dirs hold only agent/skill projections;
# everything else under docs/graph/ is plant-authored knowledge.
DATE=20260101
case_audit_classifies_and_gates_buried_customization() {
  # GT05
  set -e
  mkdir -p "$TMP/seed/agents" "$TMP/seed/skills/foo" \
           "$TMP/plant/docs/graph/agents" "$TMP/plant/docs/graph/skills" \
           "$TMP/plant/.claude/agents"
  echo "seed body line one"                      > "$TMP/seed/agents/a.md"   # -> IDENTICAL
  printf 'seed body\ngeneric seed line\n'         > "$TMP/seed/agents/b.md"   # generic seed content
  printf 'seed body v2\nmore generic seed prose\n' > "$TMP/seed/agents/c.md"
  printf 'seed skill body\n'                       > "$TMP/seed/skills/foo/SKILL.md"

  # plant live files (post-FF = seed copies) + backups (pre-FF = what was replaced)
  cp "$TMP/seed/agents/a.md" "$TMP/plant/docs/graph/agents/a.md"
  cp "$TMP/seed/agents/a.md" "$TMP/plant/docs/graph/agents/a.md.bak-$DATE-000000"  # IDENTICAL
  # b.bak = seed content PLUS a plant customization line unique to the backup
  # (token 'widgetco' + generic 'this project') -> CUSTOMIZED
  printf 'seed body\ngeneric seed line\nplant added: this project uses widgetco\n' > "$TMP/plant/docs/graph/agents/b.md.bak-$DATE-000000"
  # c.bak is just an older seed version, no plant signal -> DELTA
  printf 'seed body v1\nolder generic seed prose\n' > "$TMP/plant/docs/graph/agents/c.md.bak-$DATE-000000"
  # flattened skill (docs/graph/skills/foo.md <- seed skills/foo/SKILL.md) -> IDENTICAL
  cp "$TMP/seed/skills/foo/SKILL.md" "$TMP/plant/docs/graph/skills/foo.md.bak-$DATE-000000"
  # harness projection (.claude/agents/ <- seed agents/) -> IDENTICAL
  cp "$TMP/seed/agents/a.md" "$TMP/plant/.claude/agents/a.md.bak-$DATE-000000"

  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout" 2>&1
  rc=$?
  set -e
  grep -q "'CUSTOMIZED': 1" "$TMP/aout" || { cat "$TMP/aout"; fail "did not flag the one customization"; }
  grep -q "'DELTA': 1" "$TMP/aout" || { cat "$TMP/aout"; fail "did not classify the version delta"; }
  grep -q "'IDENTICAL': 3" "$TMP/aout" || { cat "$TMP/aout"; fail "did not map graph home + flattened skill + projection to their seed sources"; }
  grep -q "knowledge overwrite" "$TMP/aout" && { cat "$TMP/aout"; fail "seed-owned machinery under docs/graph/ wrongly flagged as knowledge"; }
  [ "$rc" -eq 1 ] || fail "audit must exit 1 when a customization is buried (got $rc)"
  return 0
}
collect_case GT05 case_audit_classifies_and_gates_buried_customization "audit classification + gate exit(1) on buried customization"

# clean FF (no customization): exit 0
case_audit_clean_fast_forward_exits_0() {
  # GT06
  set -e
  rm -f "$TMP/plant/docs/graph/agents/b.md.bak-$DATE-000000"
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout2" 2>&1
  rc2=$?
  set -e
  [ "$rc2" -eq 0 ] || { cat "$TMP/aout2"; fail "clean FF must exit 0 (got $rc2)"; }
  return 0
}
collect_case GT06 case_audit_clean_fast_forward_exits_0 "audit passes a clean fast-forward (exit 0)"

# a backup over plant-authored graph content is a knowledge overwrite, exit 1:
# a node, the plant-instantiated _schema.md, a plant skill with no seed source.
case_audit_flags_plant_graph_overwrite() {
  # GT07; GT12 is its _schema.md row, GT13 its skills/ row
  local rel rc
  for rel in nodes/api.md _schema.md skills/deploy-widgetco.md; do
    mkdir -p "$(dirname "$TMP/plant/docs/graph/$rel")"
    printf 'plant-authored content\n' > "$TMP/plant/docs/graph/$rel.bak-$DATE-000000"
    python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout3" 2>&1 && rc=0 || rc=$?
    rm -f "$TMP/plant/docs/graph/$rel.bak-$DATE-000000"
    grep -q "knowledge overwrite" "$TMP/aout3" && [ "$rc" -eq 1 ] \
      || { cat "$TMP/aout3"; fail "a $rel overwrite was not flagged as knowledge with exit 1 (got $rc)"; }
  done
  grep -q "UNMAPPED backup" "$TMP/aout3" || { cat "$TMP/aout3"; fail "the plant skill's unmapped backup is not listed"; }
  return 0
}
collect_case GT07 case_audit_flags_plant_graph_overwrite "audit flags node, _schema.md and plant-skill overwrites as knowledge, exit 1"

# a wrong plant root must not read as a clean audit: auditing nothing proves nothing.
case_audit_refuses_non_plant_root() {
  # GT08
  set -e
  mkdir -p "$TMP/notaplant"
  set +e
  python3 "$AUDIT" "$TMP/notaplant" "$TMP/seed" --date=$DATE >"$TMP/aout4" 2>&1
  rc4=$?
  set -e
  grep -q "not a plant root" "$TMP/aout4" || { cat "$TMP/aout4"; fail "wrong root not refused"; }
  [ "$rc4" -eq 1 ] || fail "audit must exit 1 on a non-plant root (got $rc4)"
  return 0
}
collect_case GT08 case_audit_refuses_non_plant_root "audit refuses a vacuous run against a non-plant root (exit 1)"

# zero backups for the requested date while other dates have some is a wrong --date.
case_audit_refuses_wrong_date() {
  # GT09
  set -e
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=19990101 --tokens=widgetco >"$TMP/aout5" 2>&1
  rc5=$?
  set -e
  grep -q "wrong --date" "$TMP/aout5" || { cat "$TMP/aout5"; fail "wrong --date not flagged"; }
  [ "$rc5" -eq 1 ] || fail "audit must exit 1 on a date that audited nothing while backups exist (got $rc5)"
  return 0
}
collect_case GT09 case_audit_refuses_wrong_date "audit refuses a vacuous audit under a wrong --date (exit 1)"

# --date is a prefix of the YYYYMMDD-HHMMSS stamp, so two same-day passes separate.
case_audit_date_is_stamp_prefix() {
  # GT10
  set -e
  PD=20260601
  printf 'seed body v1\nolder generic seed prose\n' > "$TMP/plant/docs/graph/agents/c.md.bak-$PD-160000"
  printf 'seed body v1\nolder generic seed prose\n' > "$TMP/plant/docs/graph/agents/c.md.bak-$PD-170000"
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$PD --tokens=widgetco >"$TMP/dout1" 2>&1; drc1=$?
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$PD-16 --tokens=widgetco >"$TMP/dout2" 2>&1; drc2=$?
  set -e
  grep -q "backups audited: 2" "$TMP/dout1" || { cat "$TMP/dout1"; fail "the day form must still audit the whole day"; }
  grep -q "backups audited: 1" "$TMP/dout2" || { cat "$TMP/dout2"; fail "a stamp prefix must narrow to the one pass"; }
  [ "$drc1" -eq 0 ] && [ "$drc2" -eq 0 ] || { cat "$TMP/dout2"; fail "a clean audit under either form must exit 0 ($drc1/$drc2)"; }
  rm -f "$TMP/plant/docs/graph/agents/c.md.bak-$PD-"*
  return 0
}
collect_case GT10 case_audit_date_is_stamp_prefix "audit --date accepts the stamp at the granularity the filename records"

# space-form options behave as the = form; a token-only line makes the token load-bearing.
case_audit_space_form_flags_and_stray_positional() {
  # GT11
  set -e
  printf 'seed body\ngeneric seed line\nwidgetco special retention rule\n' > "$TMP/plant/docs/graph/agents/b.md.bak-$DATE-000000"
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date "$DATE" --tokens widgetco >"$TMP/aout6" 2>&1
  rc6=$?
  set -e
  grep -q "CUSTOMIZED': 1" "$TMP/aout6" || { cat "$TMP/aout6"; fail "space-form --tokens not honored"; }
  [ "$rc6" -eq 1 ] || fail "space-form flags must classify identically (got $rc6)"
  rm -f "$TMP/plant/docs/graph/agents/b.md.bak-$DATE-000000"
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" stray-arg --date=$DATE >"$TMP/aout7" 2>&1
  rc7=$?
  set -e
  [ "$rc7" -eq 2 ] || { cat "$TMP/aout7"; fail "stray positional must exit 2 (got $rc7)"; }
  return 0
}
collect_case GT11 case_audit_space_form_flags_and_stray_positional "audit accepts --flag value form; stray positionals fail loudly"

# REGRESSION — a flag must never swallow a flag: `--tokens --engine=x` once
# consumed "--engine=x" as the token value and audited with defaults.
case_audit_rejects_flag_swallowing_flag() {
  # GT14
  set -e
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --tokens --engine=x >"$TMP/aout10" 2>&1
  rc10=$?
  set -e
  [ "$rc10" -eq 2 ] || { cat "$TMP/aout10"; fail "flag-swallowed-flag must exit 2 (got $rc10)"; }
  return 0
}
collect_case GT14 case_audit_rejects_flag_swallowing_flag "audit rejects a flag consumed as a value (exit 2)"

# ---- delivered-tool registry: status-register.py ---------------------------
# install.sh delivers tools/status-register.py as docs/graph/status-register.py;
# a fast-forward of it must map to that seed source, not read as knowledge.
case_audit_status_register_is_registered() {
  # GT15
  set -e
  mkdir -p "$TMP/seed/tools"
  printf 'seed status register body\n' > "$TMP/seed/tools/status-register.py"
  cp "$TMP/seed/tools/status-register.py" "$TMP/plant/docs/graph/status-register.py.bak-$DATE-000000"
  set +e
  python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout11" 2>&1
  rc11=$?
  set -e
  grep -q "'IDENTICAL': 4" "$TMP/aout11" || { cat "$TMP/aout11"; fail "status-register.py backup not mapped to tools/status-register.py"; }
  grep -q "knowledge overwrite" "$TMP/aout11" && { cat "$TMP/aout11"; fail "status-register.py fast-forward wrongly flagged as knowledge"; }
  [ "$rc11" -eq 0 ] || { cat "$TMP/aout11"; fail "identical status-register.py backup must audit clean (got $rc11)"; }
  rm -f "$TMP/plant/docs/graph/status-register.py.bak-$DATE-000000"
  return 0
}
collect_case GT15 case_audit_status_register_is_registered "an identical status-register.py backup maps to its seed source and audits clean"

# ---- --unfilled: template scaffolds never filled (D-SCAFFOLD, 7.0.0) --------
# install.sh copies templates/docs/<rel> to docs/graph/<rel> when missing; a
# leaf still BYTE-IDENTICAL to its template at grow Phase 6 / graft Phase 7
# was never filled. Fixture: rollback.md identical (unfilled), release.md
# filled, a plant node with no counterpart, api/README.md absent in the plant.
FIX="$ROOT/tests/fixtures/graft"
unfilled_plant() { rm -rf "$TMP/uplant"; cp -R "$FIX/plant" "$TMP/uplant"; }
case_unfilled_reports_identical_scaffold() {
  # GT16
  set -e

  # report only: exactly the identical leaf, exit 1 (a gate), nothing touched
  unfilled_plant
  set +e
  python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --unfilled >"$TMP/uout1" 2>&1
  urc1=$?
  set -e
  grep -q "^  UNFILLED docs/graph/runbooks/rollback.md" "$TMP/uout1" || { cat "$TMP/uout1"; fail "identical scaffold not reported UNFILLED"; }
  [ "$(grep -c '^  UNFILLED ' "$TMP/uout1")" -eq 1 ] || { cat "$TMP/uout1"; fail "expected exactly one UNFILLED line"; }
  grep -q "unfilled scaffolds: 1 reported" "$TMP/uout1" || { cat "$TMP/uout1"; fail "summary count missing"; }
  [ "$urc1" -eq 1 ] || { cat "$TMP/uout1"; fail "--unfilled must exit 1 while unfilled scaffolds remain (got $urc1)"; }
  [ -f "$TMP/uplant/docs/graph/runbooks/rollback.md" ] || fail "report-only run must not touch the plant"
  [ ! -e "$TMP/uplant/docs/graph/runbooks/rollback.unfilled.md" ] || fail "report-only run must not rename"
  return 0
}
collect_case GT16 case_unfilled_reports_identical_scaffold "--unfilled reports exactly the byte-identical scaffold, exit 1, plant untouched"

# --rename: <name>.unfilled.md, exit 0; a second pass finds nothing
case_unfilled_rename() {
  # GT17
  set -e
  set +e
  python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --unfilled --rename >"$TMP/uout2" 2>&1
  urc2=$?
  set -e
  [ "$urc2" -eq 0 ] || { cat "$TMP/uout2"; fail "--unfilled --rename must exit 0 (got $urc2)"; }
  [ -f "$TMP/uplant/docs/graph/runbooks/rollback.unfilled.md" ] || { cat "$TMP/uout2"; fail "unfilled scaffold not renamed to rollback.unfilled.md"; }
  [ ! -e "$TMP/uplant/docs/graph/runbooks/rollback.md" ] || fail "original left behind after --rename"
  cmp -s "$TMP/uplant/docs/graph/runbooks/rollback.unfilled.md" "$FIX/seed/templates/docs/runbooks/rollback.md" || fail "rename altered the file body"
  cmp -s "$TMP/uplant/docs/graph/runbooks/release.md" "$FIX/plant/docs/graph/runbooks/release.md" || fail "filled runbook must be untouched"
  [ -f "$TMP/uplant/docs/graph/nodes/acme-api.md" ] || fail "plant node with no template counterpart must be untouched"
  grep -q "unfilled scaffolds: 1 renamed" "$TMP/uout2" || { cat "$TMP/uout2"; fail "rename summary missing"; }
  set +e
  python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --unfilled >"$TMP/uout3" 2>&1
  urc3=$?
  set -e
  [ "$urc3" -eq 0 ] || { cat "$TMP/uout3"; fail "after --rename a report-only pass must be clean (got $urc3)"; }
  grep -q "unfilled scaffolds: 0" "$TMP/uout3" || { cat "$TMP/uout3"; fail "clean pass must report a zero count"; }
  return 0
}
collect_case GT17 case_unfilled_rename "--unfilled --rename -> <name>.unfilled.md, exit 0, filled + plant files untouched"

# --prune: removed outright, exit 0
case_unfilled_prune() {
  # GT18
  set -e
  unfilled_plant
  set +e
  python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --unfilled --prune >"$TMP/uout4" 2>&1
  urc4=$?
  set -e
  [ "$urc4" -eq 0 ] || { cat "$TMP/uout4"; fail "--unfilled --prune must exit 0 (got $urc4)"; }
  [ ! -e "$TMP/uplant/docs/graph/runbooks/rollback.md" ] || fail "--prune left the unfilled scaffold"
  [ ! -e "$TMP/uplant/docs/graph/runbooks/rollback.unfilled.md" ] || fail "--prune must remove, not rename"
  [ -f "$TMP/uplant/docs/graph/runbooks/release.md" ] || fail "--prune removed a filled runbook"
  grep -q "unfilled scaffolds: 1 removed" "$TMP/uout4" || { cat "$TMP/uout4"; fail "prune summary missing"; }
  return 0
}
collect_case GT18 case_unfilled_prune "--unfilled --prune removes the scaffold, exit 0"

# ---- the model map is disclosed, not blocked on (S4, ADR-0022) ------------
# A plant whose docs/graph/models.md is still the seed's template has chosen
# "inherit the caller's model"; --unfilled names it on a DISCLOSED line and
# neither gates nor renames it. Fixture: the graft fixture plus the real map
# template; rollback.md is filled in (a), left identical in (b).
map_plant() {  # map_plant <dir> <fill rollback: yes|no>
  rm -rf "$1" "$TMP/mseed"; cp -R "$FIX/plant" "$1"; cp -R "$FIX/seed" "$TMP/mseed"
  cp "$ROOT/templates/docs/models.md" "$TMP/mseed/templates/docs/models.md"
  cp "$ROOT/templates/docs/models.md" "$1/docs/graph/models.md"
  [ "$2" = no ] || printf '\nA filled rollback step.\n' >> "$1/docs/graph/runbooks/rollback.md"
}
case_unfilled_model_map_disclosed() {
  local why=() mrc
  # (a) the map is the only template-identical leaf: exit 0, disclosed, not counted
  map_plant "$TMP/mplant" yes
  python3 "$AUDIT" "$TMP/mplant" "$TMP/mseed" --unfilled >"$TMP/mout1" 2>&1 && mrc=0 || mrc=$?
  [ "$mrc" -eq 0 ] || why+=("(a) exit $mrc, want 0")
  [ "$(grep -cE '^ *DISCLOSED .*docs/graph/models\.md' "$TMP/mout1")" -eq 1 ] || why+=("(a) no single DISCLOSED line names docs/graph/models.md")
  ! grep -qE '^ *UNFILLED .*models\.md' "$TMP/mout1" || why+=("(a) an UNFILLED line names models.md")
  grep -q "unfilled scaffolds: 0 reported" "$TMP/mout1" || why+=("(a) summary is not 'unfilled scaffolds: 0 reported'")
  # (b) guard: rollback.md unfilled too still gates, on rollback only
  map_plant "$TMP/mplant2" no
  python3 "$AUDIT" "$TMP/mplant2" "$TMP/mseed" --unfilled >"$TMP/mout2" 2>&1 && mrc=0 || mrc=$?
  [ "$mrc" -eq 1 ] || why+=("(b) exit $mrc, want 1")
  grep -qE '^ *UNFILLED .*runbooks/rollback\.md' "$TMP/mout2" || why+=("(b) no UNFILLED line names rollback.md")
  ! grep -qE '^ *UNFILLED .*models\.md' "$TMP/mout2" || why+=("(b) an UNFILLED line names models.md")
  grep -qE '^ *DISCLOSED .*docs/graph/models\.md' "$TMP/mout2" || why+=("(b) the DISCLOSED line is not printed")
  # (c) --rename leaves the disclosed map in place
  map_plant "$TMP/mplant" yes
  python3 "$AUDIT" "$TMP/mplant" "$TMP/mseed" --unfilled --rename >"$TMP/mout3" 2>&1 || true
  [ -f "$TMP/mplant/docs/graph/models.md" ] || why+=("(c) --rename moved docs/graph/models.md")
  [ ! -e "$TMP/mplant/docs/graph/models.unfilled.md" ] || why+=("(c) --rename wrote models.unfilled.md")
  [ ${#why[@]} -eq 0 ] || { cat "$TMP/mout1" "$TMP/mout2"; fail "$(printf '%s; ' "${why[@]}")"; }
}
collect_case GT-MAP case_unfilled_model_map_disclosed "an unfilled model map is DISCLOSED: exit 0, not counted, not renamed; rollback still gates"

# verification.md: byte-identical is unfilled unless it carries an executed gate row.
case_unfilled_verification_exemption() {
  # GT19
  set -e
  rm -rf "$TMP/vplant"; mkdir -p "$TMP/vplant/docs/graph/runbooks"
  cp "$FIX/seed/templates/docs/runbooks/verification.md" "$TMP/vplant/docs/graph/runbooks/verification.md"
  set +e
  python3 "$AUDIT" "$TMP/vplant" "$FIX/seed" --unfilled >"$TMP/uout5" 2>&1
  urc5=$?
  set -e
  grep -q "^  UNFILLED docs/graph/runbooks/verification.md" "$TMP/uout5" || { cat "$TMP/uout5"; fail "verification.md with no executed gate not reported"; }
  [ "$urc5" -eq 1 ] || { cat "$TMP/uout5"; fail "verification.md without an executed row must gate (got $urc5)"; }
  cp "$FIX/seed-executed/templates/docs/runbooks/verification.md" "$TMP/vplant/docs/graph/runbooks/verification.md"
  set +e
  python3 "$AUDIT" "$TMP/vplant" "$FIX/seed-executed" --unfilled >"$TMP/uout6" 2>&1
  urc6=$?
  set -e
  grep -q "UNFILLED" "$TMP/uout6" && { cat "$TMP/uout6"; fail "verification.md carrying an executed gate row must be exempt"; }
  [ "$urc6" -eq 0 ] || { cat "$TMP/uout6"; fail "exempt verification.md must not gate (got $urc6)"; }
  return 0
}
collect_case GT19 case_unfilled_verification_exemption "verification.md: unfilled without an executed gate row, exempt with one"

# the real seed layout: templates/docs/<rel> mirrors docs/graph/<rel>
case_unfilled_real_seed_layout() {
  # GT20
  set -e
  rm -rf "$TMP/rplant"; mkdir -p "$TMP/rplant/docs/graph/runbooks"
  cp "$ROOT/templates/docs/runbooks/rollback.md" "$TMP/rplant/docs/graph/runbooks/rollback.md"
  set +e
  python3 "$AUDIT" "$TMP/rplant" "$ROOT" --unfilled >"$TMP/uout7" 2>&1
  urc7=$?
  set -e
  grep -q "^  UNFILLED docs/graph/runbooks/rollback.md" "$TMP/uout7" || { cat "$TMP/uout7"; fail "real seed template not mirrored to docs/graph/"; }
  [ "$urc7" -eq 1 ] || { cat "$TMP/uout7"; fail "real-seed unfilled scaffold must gate (got $urc7)"; }
  return 0
}
collect_case GT20 case_unfilled_real_seed_layout "--unfilled mirrors the real seed's templates/docs/ onto docs/graph/"

# flag discipline: --rename/--prune act only on --unfilled findings, and never both
case_unfilled_flag_discipline() {
  # GT21
  set -e
  set +e
  python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --prune >"$TMP/uout8" 2>&1; urc8=$?
  python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --unfilled --rename --prune >"$TMP/uout9" 2>&1; urc9=$?
  python3 "$AUDIT" "$TMP/uplant" "$TMP/notaplant" --unfilled >"$TMP/uout10" 2>&1; urc10=$?
  set -e
  [ "$urc8" -eq 2 ] || { cat "$TMP/uout8"; fail "--prune without --unfilled must exit 2 (got $urc8)"; }
  [ "$urc9" -eq 2 ] || { cat "$TMP/uout9"; fail "--rename with --prune must exit 2 (got $urc9)"; }
  [ "$urc10" -eq 1 ] || { cat "$TMP/uout10"; fail "a seed root without templates/docs/ must be refused (got $urc10)"; }
  grep -q "templates/docs" "$TMP/uout10" || { cat "$TMP/uout10"; fail "seed-root refusal must name templates/docs/"; }
  return 0
}
collect_case GT21 case_unfilled_flag_discipline "--unfilled flag discipline (prune needs unfilled; rename xor prune; seed root checked)"

# ---- kernel currency: STALE vs plant-extended vs standing deviation ---------
# an old body is STALE; seed-current plus plant lines is EXTENDED unless a deviation records it.
KD="20260907"
kaudit() { set +e; python3 "$AUDIT" "$TMP/kplant" "$TMP/kseed" --date=$KD --tokens=widgetco >"$TMP/kout" 2>&1; krc=$?; set -e; }
case_audit_kernel_currency() {
  # GT22
  set -e
  rm -rf "$TMP/kseed" "$TMP/kplant"
  mkdir -p "$TMP/kseed/core" "$TMP/kseed/templates/docs" "$TMP/kplant/docs/graph/nodes"
  printf '# kernel\nline one\nline two\nline three\n' > "$TMP/kseed/core/AGENTS.md"
  # identical -> current, exit 0
  cp "$TMP/kseed/core/AGENTS.md" "$TMP/kplant/AGENTS.md"
  kaudit; [ "$krc" -eq 0 ] && grep -q "kernel: current" "$TMP/kout" || { cat "$TMP/kout"; fail "identical kernel must read current, exit 0 (got $krc)"; }
  # old body (a seed line missing) -> STALE, exit 1
  printf '# kernel\nline one\nline three\n' > "$TMP/kplant/AGENTS.md"
  kaudit; [ "$krc" -eq 1 ] && grep -q "KERNEL STALE" "$TMP/kout" || { cat "$TMP/kout"; fail "old kernel body must be STALE and exit 1 (got $krc)"; }
  # seed body + 2 plant lines, no deviation -> EXTENDED, exit 1, never STALE
  printf '# kernel\nline one\nline two\nline three\n- plant rule a\n- plant rule b\n' > "$TMP/kplant/AGENTS.md"
  kaudit; [ "$krc" -eq 1 ] && grep -q "KERNEL EXTENDED" "$TMP/kout" && ! grep -q "KERNEL STALE" "$TMP/kout" \
    || { cat "$TMP/kout"; fail "extended kernel without a deviation must be EXTENDED (not STALE), exit 1 (got $krc)"; }
  grep -q "2 plant-authored line" "$TMP/kout" || { cat "$TMP/kout"; fail "EXTENDED must count the plant lines"; }
  # a deviation node that is NOT standing, or covers another fact -> still EXTENDED
  cat > "$TMP/kplant/docs/graph/nodes/deviation.kernel-boundary.md" <<'MD'
---
id: deviation.kernel-boundary
kind: deviation
status: closed
departs_from: kernel.body
ends_when: the lines have a graph home
---
MD
  kaudit; [ "$krc" -eq 1 ] && grep -q "KERNEL EXTENDED" "$TMP/kout" || { cat "$TMP/kout"; fail "a closed deviation must not cover the kernel (got $krc)"; }
  sed -i.bak 's/^status: closed$/status: standing/; s/^departs_from: kernel.body$/departs_from: secrets-posture.lifetime/' "$TMP/kplant/docs/graph/nodes/deviation.kernel-boundary.md" && rm -f "$TMP/kplant/docs/graph/nodes/deviation.kernel-boundary.md.bak"
  kaudit; [ "$krc" -eq 1 ] && grep -q "KERNEL EXTENDED" "$TMP/kout" || { cat "$TMP/kout"; fail "a deviation on another fact must not cover the kernel (got $krc)"; }
  # standing deviation on kernel.body -> recognised, exit 0, no !! line
  sed -i.bak 's/^departs_from: .*$/departs_from: kernel.body   # the plant kernel carries lines the seed does not/' "$TMP/kplant/docs/graph/nodes/deviation.kernel-boundary.md" && rm -f "$TMP/kplant/docs/graph/nodes/deviation.kernel-boundary.md.bak"
  kaudit; [ "$krc" -eq 0 ] && grep -q "standing deviation deviation.kernel-boundary" "$TMP/kout" && ! grep -q "!! KERNEL" "$TMP/kout" \
    || { cat "$TMP/kout"; fail "standing kernel.body deviation must clear the kernel check, exit 0 (got $krc)"; }
  grep -q "ends_when: the lines have a graph home" "$TMP/kout" || { cat "$TMP/kout"; fail "the recognised deviation must surface its ends_when"; }
  # the deviation covers ADDITIONS only: an old body stays STALE even with the node
  printf '# kernel\nline one\nline three\n- plant rule a\n' > "$TMP/kplant/AGENTS.md"
  kaudit; [ "$krc" -eq 1 ] && grep -q "KERNEL STALE" "$TMP/kout" || { cat "$TMP/kout"; fail "a deviation must not excuse an old kernel body (got $krc)"; }
  # a blank form (_deviation.template.md) never counts as a deviation
  printf '# kernel\nline one\nline two\nline three\n- plant rule a\n' > "$TMP/kplant/AGENTS.md"
  mv "$TMP/kplant/docs/graph/nodes/deviation.kernel-boundary.md" "$TMP/kplant/docs/graph/nodes/_deviation.template.md"
  kaudit; [ "$krc" -eq 1 ] && grep -q "KERNEL EXTENDED" "$TMP/kout" || { cat "$TMP/kout"; fail "a blank template must not read as a deviation (got $krc)"; }
  return 0
}
collect_case GT22 case_audit_kernel_currency "kernel currency: STALE blocks, EXTENDED blocks, standing kernel.body deviation clears"

# ---- engine currency: a multi-line config assignment is not a stale line ----
# config assignments are plant-specific and excluded, continuation lines too.
case_audit_engine_currency_multiline_config() {
  # GT23
  set -e
  rm -rf "$TMP/ec"; mkdir -p "$TMP/ec"
  cat > "$TMP/ec/seed.py" <<'PY2'
ROOT_ID = "root"
KINDS = {"root", "subsystem",
         "deviation", "method"}
def shared():
    return 1
PY2
  cat > "$TMP/ec/plant.py" <<'PY2'
ROOT_ID = "app"
KINDS = {"root", "subsystem", "deviation", "method", "operator"}
def shared():
    return 1
PY2
  python3 - "$AUDIT" "$TMP/ec" <<'PY2'
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("ga", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = Path(sys.argv[2])
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    m._engine_currency(f"{d}/plant.py:{d}/seed.py")
out = buf.getvalue()
assert "current" in out and "STALE" not in out, f"multi-line config read as stale: {out!r}"
# a real engine improvement absent from the plant still reports STALE
(d / "seed.py").write_text((d / "seed.py").read_text() + "def added_helper():\n    return 2\n")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    m._engine_currency(f"{d}/plant.py:{d}/seed.py")
out = buf.getvalue()
assert "STALE" in out and "2 seed engine line" in out, f"real drift not reported: {out!r}"
PY2
  return 0
}
collect_case GT23 case_audit_engine_currency_multiline_config "engine currency: multi-line config excluded, real drift still STALE"

# ---- the customization audit must not cry wolf on a pristine file ---------
# a generic phrase the seed itself writes is not a plant customization.
case_audit_generic_seed_phrase_is_not_signal() {
  # GT24
  set -e
  rm -rf "$TMP/sig"; mkdir -p "$TMP/sig/seedroot/protocols" "$TMP/sig/plant/docs/graph/protocols"
  cat > "$TMP/sig/seedroot/protocols/alpha.md" <<'MD'
# Alpha
Write in this project's idiom; the pins are often old on purpose.
A brand new seed sentence that the old body did not have.
MD
  # the backup: the SAME generic phrase, differently worded around it, and no
  # plant-specific content whatsoever.
  cat > "$TMP/sig/plant/docs/graph/protocols/alpha.md.bak-20260101-000000" <<'MD'
# Alpha
Write in this project's idiom — the pins are often old on purpose.
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" || true
  grep -q "FF-overwritten plant customization" <<<"$out" \
      && { printf '%s\n' "$out" >&2; fail "a phrase the seed itself ships was read as plant signal"; }
  return 0
}
collect_case GT24 case_audit_generic_seed_phrase_is_not_signal "a generic phrase the seed also ships is not plant signal"

# the true positives must still fire: an explicit --tokens match, and a generic
# phrase that appears in the backup but NOT in the seed source.
case_audit_true_signals_still_fire() {
  # GT25
  set -e
  cat > "$TMP/sig/plant/docs/graph/protocols/alpha.md.bak-20260102-000000" <<'MD'
# Alpha
Write in this project's idiom; the pins are often old on purpose.
A brand new seed sentence that the old body did not have.
Deploy notes for zamber-corp live beside this file.
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260102 --tokens=zamber-corp 2>&1)" || true
  grep -q "FF-overwritten plant customization" <<<"$out" \
      || { printf '%s\n' "$out" >&2; fail "an explicit plant token stopped being reported"; }
  cat > "$TMP/sig/plant/docs/graph/protocols/alpha.md.bak-20260103-000000" <<'MD'
# Alpha
Write in this project's idiom; the pins are often old on purpose.
A brand new seed sentence that the old body did not have.
Our stack pins the broker one minor behind on purpose.
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260103 2>&1)" || true
  grep -q "FF-overwritten plant customization" <<<"$out" \
      || { printf '%s\n' "$out" >&2; fail "a generic phrase absent from the seed source stopped being reported"; }
  return 0
}
collect_case GT25 case_audit_true_signals_still_fire "explicit tokens and seed-absent generic phrases still fire"

# ...and a short explicit token matches only at word edges.
case_audit_token_matches_at_word_edges() {
  # GT26
  set -e
  cat > "$TMP/sig/plant/docs/graph/protocols/alpha.md.bak-20260104-000000" <<'MD'
# Alpha
Write in this project's idiom; the pins are often old on purpose.
A brand new seed sentence that the old body did not have.
The rollback step is replaced during a release.
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260104 --tokens=ace 2>&1)" || true
  grep -q "FF-overwritten plant customization" <<<"$out" \
      && { printf '%s\n' "$out" >&2; fail "a token matched inside an ordinary word was reported as a buried customization"; }
  cat > "$TMP/sig/plant/docs/graph/protocols/alpha.md.bak-20260105-000000" <<'MD'
# Alpha
Write in this project's idiom; the pins are often old on purpose.
A brand new seed sentence that the old body did not have.
The ace gateway is pinned one minor behind.
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260105 --tokens=ace 2>&1)" || true
  grep -q "FF-overwritten plant customization" <<<"$out" \
      || { printf '%s\n' "$out" >&2; fail "a token standing as its own word stopped being reported"; }
  grep -q "signal: ace" <<<"$out" \
      || { printf '%s\n' "$out" >&2; fail "the finding must name the token that matched"; }
  return 0
}
collect_case GT26 case_audit_token_matches_at_word_edges "an explicit token matches at word edges, not inside a word"

# ---- --engine refuses to report a check it did not run --------------------
case_audit_malformed_engine_fails_loudly() {
  # GT27
  set -e
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 \
          --engine="$TMP/sig/seedroot/protocols/alpha.md" 2>&1)" && rc=0 || rc=$?
  [ "${rc:-0}" -ne 0 ] || fail "a malformed --engine did not fail"
  grep -q -- "--engine wants <plant-file>:<seed-file>" <<<"$out" \
      || { printf '%s\n' "$out" >&2; fail "a malformed --engine did not say what was wrong"; }
  grep -q "engine check skipped" <<<"$out" \
      && fail "a malformed --engine still announced itself as a skip"
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 \
          --engine="$TMP/nope.py:$TMP/also-nope.py" 2>&1)" && rc=0 || rc=$?
  [ "${rc:-0}" -ne 0 ] || fail "an --engine naming a missing file did not fail"
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" || true
  grep -qi "graph engine" <<<"$out" && fail "--engine omitted still reported an engine verdict"
  return 0
}
collect_case GT27 case_audit_malformed_engine_fails_loudly "malformed --engine fails loudly; omitted stays silent"

# ---- the node schema is machinery too, and can cross a graft stale --------
case_audit_schema_currency() {
  # GT28
  set -e
  mkdir -p "$TMP/sig/seedroot/templates/knowledge-graph"
  cat > "$TMP/sig/seedroot/templates/knowledge-graph/_schema.md" <<'MD'
# Schema

## Frontmatter

Every node begins with YAML frontmatter.

```yaml
id: {{kind}}.{{name}}
kind: {{kind}}
status: open
```

## Lifecycle status

Anything that can be open carries its status in frontmatter, never in prose.

| value | means |
|---|---|
| `open` | live, unresolved |
| `closed` | resolved with evidence |
MD
  cp "$TMP/sig/seedroot/templates/knowledge-graph/_schema.md" "$TMP/sig/plant/docs/graph/_schema.md"
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" || true
  grep -q "node schema: current" <<<"$out" || { printf '%s\n' "$out" >&2; fail "a current schema was not reported current"; }
  printf '# Schema\n' > "$TMP/sig/plant/docs/graph/_schema.md"
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" || true
  grep -q "node schema STALE" <<<"$out" || { printf '%s\n' "$out" >&2; fail "a stale schema was not reported"; }
  # a plant that EXTENDS the schema is not stale, and staleness does not gate
  { cat "$TMP/sig/seedroot/templates/knowledge-graph/_schema.md"; printf 'A line this plant added.\n'; } \
    > "$TMP/sig/plant/docs/graph/_schema.md"
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" && rc=0 || rc=$?
  grep -q "node schema: current" <<<"$out" || fail "a plant extension was misread as staleness"
  [ "${rc:-0}" -eq 0 ] || fail "schema currency must report, not gate"
  return 0
}
collect_case GT28 case_audit_schema_currency "schema currency: current / STALE / extended, reports without gating"

# a contract is what it requires, not the sentences it is written in.
case_audit_schema_currency_by_contract_terms() {
  # GT29
  set -e
  cat > "$TMP/sig/plant/docs/graph/_schema.md" <<'MD'
# This project's node contract

## Frontmatter

Each node opens with a small YAML header, keys only — no nested maps:

```yaml
id: subsystem.billing
kind: subsystem
status: open
```

## Lifecycle status

We keep the state in the header and never in the body, so an agent reads a
field instead of inferring one.

| value | what it means here |
|---|---|
| `open` | somebody still owes work on it |
| `closed` | done, with the evidence named |
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" || true
  grep -q "node schema: current" <<<"$out" \
    || { printf '%s\n' "$out" >&2; fail "a re-integrated schema keeping every contract term was reported stale"; }
  # ...and a term the contract genuinely lost is named, not counted
  cat > "$TMP/sig/plant/docs/graph/_schema.md" <<'MD'
# This project's node contract

## Frontmatter

Each node opens with a small YAML header:

```yaml
id: subsystem.billing
kind: subsystem
```

## Lifecycle status

| value | what it means here |
|---|---|
| `open` | somebody still owes work on it |
MD
  out="$(python3 "$AUDIT" "$TMP/sig/plant" "$TMP/sig/seedroot" --date 20260101 2>&1)" || true
  grep -q "node schema STALE" <<<"$out" || { printf '%s\n' "$out" >&2; fail "a genuinely missing contract term was not reported"; }
  grep -q "status" <<<"$out" && grep -q "closed" <<<"$out" \
    || { printf '%s\n' "$out" >&2; fail "the missing terms must be named, not counted"; }
  return 0
}
collect_case GT29 case_audit_schema_currency_by_contract_terms "schema currency compares what the contract names, not its sentences"

# ---- every graph engine is reconciled with its own config -----------------
# the plants are built from the seed's real engines.
KG="$ROOT/templates/knowledge-graph"
EW="$TMP/engines"; mkdir -p "$EW"
# a graph-lint.py whose config the plant changed (ROOT_ID, KIND_PREFIX), body current
configured_graph_lint() {
  sed -e 's/^ROOT_ID = "root"$/ROOT_ID = "app"/' \
      -e 's/^KIND_PREFIX = {}$/KIND_PREFIX = {"operator": "op."}/' "$KG/graph-lint.py" > "$1"
  grep -qx 'ROOT_ID = "app"' "$1" && grep -qx 'KIND_PREFIX = {"operator": "op."}' "$1" \
    || { echo "fixture: the seed's graph-lint.py no longer carries ROOT_ID = \"root\" and KIND_PREFIX = {}"; return 1; }
}

case_engine_reconcile_stale_grill_lint() {
  # X383 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE
  # Asserts SPEC-0001 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE.
  local d="$EW/x383" rc
  mkdir -p "$d"
  grep -v waves "$KG/grill-lint.py" > "$EW/x383.stale"
  cmp -s "$EW/x383.stale" "$KG/grill-lint.py" && { echo "fixture: the stale body equals the seed's"; return 1; }
  cp "$EW/x383.stale" "$d/grill-lint.py"
  python3 "$ENGINE" "$d/grill-lint.py" "$KG/grill-lint.py" >"$EW/x383.out" 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "a stale grill-lint.py reconciled with no --preserve exited $rc: $(tr '\n' ' ' <"$EW/x383.out")"; return 1; }
  cmp -s "$d/grill-lint.py" "$KG/grill-lint.py" || { echo "grill-lint.py is not byte-identical to the seed's after the reconcile"; return 1; }
  [ "$(ls "$d" | grep -c '^grill-lint\.py\.bak-')" -eq 1 ] || { echo "expected exactly one grill-lint.py.bak-*, found: $(ls "$d" | tr '\n' ' ')"; return 1; }
  cmp -s "$d"/grill-lint.py.bak-* "$EW/x383.stale" || { echo "the backup does not hold the older body"; return 1; }
}

case_engine_reconcile_spec_lint_keeps_test_globs() {
  # X384 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE
  # Asserts SPEC-0001 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE.
  local d="$EW/x384" rc
  mkdir -p "$d"
  # the plant's own TEST_GLOBS, and a body older than the seed's (every line
  # naming KNOWN_STATUSES gone), so the reconcile has a body to adopt
  python3 - "$KG/spec-lint.py" "$d/spec-lint.py" <<'PY' || { echo "fixture: the seed's spec-lint.py has no multi-line TEST_GLOBS or no KNOWN_STATUSES"; return 1; }
import re, sys
src = open(sys.argv[1]).read()
new, n = re.subn(r"^TEST_GLOBS = \[.*?\n\]", 'TEST_GLOBS = ["checks/**/*.py"]', src, count=1, flags=re.S | re.M)
assert n == 1 and "KNOWN_STATUSES" in new
open(sys.argv[2], "w").write("".join(l for l in new.splitlines(True) if "KNOWN_STATUSES" not in l))
PY
  python3 "$ENGINE" "$d/spec-lint.py" "$KG/spec-lint.py" >"$EW/x384.out" 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "a spec-lint.py reconciled with no --preserve exited $rc: $(tr '\n' ' ' <"$EW/x384.out")"; return 1; }
  grep -qx 'TEST_GLOBS = \["checks/\*\*/\*\.py"\]' "$d/spec-lint.py" && ! grep -q '"spec/\*\*/\*\.\*"' "$d/spec-lint.py" \
    || { echo "the plant's TEST_GLOBS was not kept"; return 1; }
  grep -q "KNOWN_STATUSES" "$d/spec-lint.py" || { echo "the seed's spec-lint.py body was not adopted"; return 1; }
}

case_engine_reconcile_explicit_preserve_wins() {
  # X385 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE (guard: passes on the unmodified tool)
  # Asserts SPEC-0001 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE.
  local d="$EW/x385" rc
  mkdir -p "$d"
  configured_graph_lint "$d/graph-lint.py" || return 1
  python3 "$ENGINE" "$d/graph-lint.py" "$KG/graph-lint.py" --preserve=ROOT_ID >"$EW/x385.out" 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "--preserve=ROOT_ID on graph-lint.py exited $rc: $(tr '\n' ' ' <"$EW/x385.out")"; return 1; }
  grep -qx 'ROOT_ID = "app"' "$d/graph-lint.py" || { echo "--preserve=ROOT_ID did not keep the plant's ROOT_ID"; return 1; }
  grep -qx 'KIND_PREFIX = {}' "$d/graph-lint.py" && ! grep -q '"operator": "op."' "$d/graph-lint.py" \
    || { echo "--preserve=ROOT_ID still kept the plant's KIND_PREFIX: the per-engine set won over the explicit one"; return 1; }
}

case_engine_reconcile_other_name_takes_graph_lint_set() {
  # X386 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE (guard: passes on the unmodified tool)
  # Asserts SPEC-0001 ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE.
  local d="$EW/x386" rc
  mkdir -p "$d"
  configured_graph_lint "$d/project-lint.py" || return 1
  python3 "$ENGINE" "$d/project-lint.py" "$KG/graph-lint.py" >"$EW/x386.out" 2>&1; rc=$?
  [ "$rc" -eq 0 ] || { echo "a project-lint.py reconciled with no --preserve exited $rc: $(tr '\n' ' ' <"$EW/x386.out")"; return 1; }
  grep -qx 'ROOT_ID = "app"' "$d/project-lint.py" && grep -qx 'KIND_PREFIX = {"operator": "op."}' "$d/project-lint.py" \
    || { echo "an engine under another name lost its ROOT_ID or KIND_PREFIX: it did not take the graph-lint.py set"; return 1; }
}

# the audit fixture for X387-X389: a current graph-lint.py and a stale grill-lint.py
AP="$EW/audit"; mkdir -p "$AP/plant/docs/graph" "$AP/seed"
cp "$KG/graph-lint.py" "$AP/plant/docs/graph/graph-lint.py"
grep -v waves "$KG/grill-lint.py" > "$AP/plant/docs/graph/grill-lint.py"
PAIR_CURRENT="$AP/plant/docs/graph/graph-lint.py:$KG/graph-lint.py"
PAIR_STALE="$AP/plant/docs/graph/grill-lint.py:$KG/grill-lint.py"
PAIR_MALFORMED="$AP/plant/docs/graph/grill-lint.py"

case_engine_audit_one_line_per_pair() {
  # X387 ENGINE_AUDIT_CHECKS_EVERY_PAIR, ENGINE_LEFT_STALE_BY_GRAFT
  # Asserts SPEC-0001 ENGINE_AUDIT_CHECKS_EVERY_PAIR.
  local out n
  out="$(python3 "$AUDIT" "$AP/plant" "$AP/seed" --engine="$PAIR_CURRENT" --engine="$PAIR_STALE" 2>&1)" || true
  n="$(grep -c "graph engine" <<<"$out")" || true
  [ "$n" -eq 2 ] || { echo "two --engine pairs printed $n engine-currency line(s): $(tr '\n' ' ' <<<"$out")"; return 1; }
  grep "graph engine" <<<"$out" | grep "graph-lint.py" | grep -q "current" \
    || { echo "no current line naming the plant's graph-lint.py: $(tr '\n' ' ' <<<"$out")"; return 1; }
  grep "graph engine STALE" <<<"$out" | grep -q "grill-lint.py" \
    || { echo "no graph engine STALE line naming the plant's grill-lint.py: $(tr '\n' ' ' <<<"$out")"; return 1; }
}

case_engine_audit_malformed_first_pair_fails() {
  # X389 ENGINE_AUDIT_CHECKS_EVERY_PAIR; X388 is its malformed-second row
  # Asserts SPEC-0001 ENGINE_AUDIT_CHECKS_EVERY_PAIR.
  local out rc order
  python3 "$AUDIT" "$AP/plant" "$AP/seed" --engine="$PAIR_CURRENT" >"$EW/x389.ctl" 2>&1 \
    || { echo "control: the current pair alone did not exit 0: $(tr '\n' ' ' <"$EW/x389.ctl")"; return 1; }
  for order in first second; do
    if [ "$order" = first ]; then set -- "$PAIR_MALFORMED" "$PAIR_CURRENT"; else set -- "$PAIR_CURRENT" "$PAIR_MALFORMED"; fi
    out="$(python3 "$AUDIT" "$AP/plant" "$AP/seed" --engine="$1" --engine="$2" 2>&1)" && rc=0 || rc=$?
    [ "$rc" -ne 0 ] || { echo "a malformed $order --engine pair exited 0: the check it asked for did not run"; return 1; }
    grep -q -- "--engine wants <plant-file>:<seed-file>" <<<"$out" \
      || { echo "a malformed $order --engine pair did not say what was wrong: $(tr '\n' ' ' <<<"$out")"; return 1; }
  done
}

collect_case X383 case_engine_reconcile_stale_grill_lint "a stale grill-lint.py adopts the seed's body with no --preserve, one backup"
collect_case X384 case_engine_reconcile_spec_lint_keeps_test_globs "spec-lint.py keeps the plant's TEST_GLOBS with no --preserve"
collect_case X385 case_engine_reconcile_explicit_preserve_wins "an explicit --preserve wins over the per-engine set"
collect_case X386 case_engine_reconcile_other_name_takes_graph_lint_set "an engine under another name takes the graph-lint.py set"
collect_case X387 case_engine_audit_one_line_per_pair "two --engine pairs print two lines, each naming its plant file"
collect_case X389 case_engine_audit_malformed_first_pair_fails "a malformed first or second (X388) --engine pair exits non-zero"

# ---- round 7.32.0: graft-audit false alarms, graft ledger, graft run -------
# Labels: GA-C1..GA-C4 are graft-audit's four false alarms
# (GA-C3 runs under X390, with X391 and X392 as its rows, and asserts SPEC-0001
# EVERY_BACKUP_IS_CLASSIFIABLE; the others are contained, no spec owns them); GL-a..GL-d are tools/graft-ledger.py;
# GR-a..GR-g are tools/graft-run.py. Every fixture is synthetic.
LEDGER="$ROOT/tools/graft-ledger.py"
RUN="$ROOT/tools/graft-run.py"
RW="$TMP/round"; mkdir -p "$RW"
flat() { tr '\n' ' ' <"$1"; }
# git for the synthetic repositories only: no user or system config, no background gc.
sgit() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -c user.name=fixture \
           -c user.email=fixture@example.invalid -c init.defaultBranch=main \
           -c maintenance.auto=false -c gc.auto=0 \
           -c commit.gpgsign=false -c tag.gpgsign=false "$@"; }

# -- GA-C1: a backup byte-identical to the seed at --base <rev> is DELTA ------
case_audit_base_identical_is_delta() {
  local s="$RW/c1seed" p="$RW/c1plant" base rc
  mkdir -p "$s/protocols" "$p/docs/graph/protocols"
  printf '# Alpha\nRun the cypress checks before a release.\n' > "$s/protocols/alpha.md"
  sgit -C "$s" init -q && sgit -C "$s" add -A && sgit -C "$s" commit -q -m base \
    || { echo "fixture: the synthetic seed repository could not be committed"; return 1; }
  base="$(sgit -C "$s" rev-parse HEAD)"
  printf '# Alpha\nRun the release checks.\nA newer seed line.\n' > "$s/protocols/alpha.md"
  sgit -C "$s" commit -q -am head || { echo "fixture: second seed commit failed"; return 1; }
  cp "$s/protocols/alpha.md" "$p/docs/graph/protocols/alpha.md"
  sgit -C "$s" show "$base:protocols/alpha.md" > "$p/docs/graph/protocols/alpha.md.bak-20260301-000000"
  # without --base: today's verdict, kept (the default stays conservative)
  python3 "$AUDIT" "$p" "$s" --date=20260301 --tokens=cypress >"$RW/c1.nobase" 2>&1 && rc=0 || rc=$?
  grep -q "'CUSTOMIZED': 1" "$RW/c1.nobase" && [ "$rc" -eq 1 ] \
    || { echo "control: without --base the base-identical backup must stay CUSTOMIZED, exit 1 (got $rc): $(flat "$RW/c1.nobase")"; return 1; }
  # with --base: the backup is the seed at that revision, so the plant authored nothing in it
  python3 "$AUDIT" "$p" "$s" --date=20260301 --tokens=cypress --base "$base" >"$RW/c1.base" 2>&1 && rc=0 || rc=$?
  grep -q "'DELTA': 1" "$RW/c1.base" && grep -q "'CUSTOMIZED': 0" "$RW/c1.base" \
    || { echo "a backup byte-identical to the seed at --base was not classed DELTA: $(flat "$RW/c1.base")"; return 1; }
  [ "$rc" -eq 0 ] || { echo "a base-identical backup under --base must audit clean, exit 0 (got $rc): $(flat "$RW/c1.base")"; return 1; }
  # guard: --base is no blanket pardon; a plant line absent from the base still fires
  { sgit -C "$s" show "$base:protocols/alpha.md"; printf 'The cypress mirror lives on the build host.\n'; } \
    > "$p/docs/graph/protocols/alpha.md.bak-20260302-000000"
  python3 "$AUDIT" "$p" "$s" --date=20260302 --tokens=cypress --base "$base" >"$RW/c1.guard" 2>&1 && rc=0 || rc=$?
  grep -q "'CUSTOMIZED': 1" "$RW/c1.guard" && [ "$rc" -eq 1 ] \
    || { echo "under --base, a backup carrying a plant line the base lacks must stay CUSTOMIZED, exit 1 (got $rc): $(flat "$RW/c1.guard")"; return 1; }
}

# -- GA-C2: an engine backup whose signal lines survive in the current engine --
case_audit_engine_signal_survives() {
  local s="$RW/c2seed" p="$RW/c2plant" b rc
  mkdir -p "$s/templates/knowledge-graph" "$p/docs/graph"
  cat > "$s/templates/knowledge-graph/graph-lint.py" <<'PY'
ROOT_ID = "root"
KINDS = {"root", "subsystem"}
KIND_PREFIX = {}
def check():
    return helper()
def helper():
    return 0
PY
  # the plant's engine before the graft: an older body and a commented config
  cat > "$p/docs/graph/graph-lint.py" <<'PY'
# zamber: this plant routes on the deploy name, not the repository name
ROOT_ID = "app"
KINDS = {"root", "subsystem"}
KIND_PREFIX = {}
def check():
    return 0
PY
  python3 "$ENGINE" "$p/docs/graph/graph-lint.py" "$s/templates/knowledge-graph/graph-lint.py" >"$RW/c2.engine" 2>&1 \
    || { echo "fixture: graft-graph-engine.py did not reconcile the engine: $(flat "$RW/c2.engine")"; return 1; }
  grep -q "zamber: this plant routes" "$p/docs/graph/graph-lint.py" && grep -q "def helper" "$p/docs/graph/graph-lint.py" \
    || { echo "fixture: the reconciled engine lost its config comment or did not adopt the body"; return 1; }
  b="$(ls "$p/docs/graph/" | grep '^graph-lint\.py\.bak-' | head -1)"
  [ -n "$b" ] || { echo "fixture: the engine tool wrote no backup"; return 1; }
  python3 "$AUDIT" "$p" "$s" --date="${b#graph-lint.py.bak-}" --tokens=zamber >"$RW/c2.out" 2>&1 && rc=0 || rc=$?
  grep -q "'CUSTOMIZED': 0" "$RW/c2.out" \
    || { echo "an engine backup whose every signal line survives in the plant's current engine was classed CUSTOMIZED: $(flat "$RW/c2.out")"; return 1; }
  [ "$rc" -eq 0 ] || { echo "an engine backup with nothing lost must audit clean, exit 0 (got $rc): $(flat "$RW/c2.out")"; return 1; }
  # guard: a signal line the current engine does not carry is still a buried customization
  { cat "$p/docs/graph/$b"; printf '# zamber keeps a local retention rule here\n'; } \
    > "$p/docs/graph/graph-lint.py.bak-20260303-000000"
  python3 "$AUDIT" "$p" "$s" --date=20260303 --tokens=zamber >"$RW/c2.guard" 2>&1 && rc=0 || rc=$?
  grep -q "'CUSTOMIZED': 1" "$RW/c2.guard" && [ "$rc" -eq 1 ] \
    || { echo "an engine backup carrying a signal line the current engine lost must stay CUSTOMIZED, exit 1 (got $rc): $(flat "$RW/c2.guard")"; return 1; }
}

# -- X390 (GA-C3): the projection of a plant-owned node is classified ----------
# Rows: X390 .claude/agents, X391 .claude/skills, X392 the Copilot .github/agents.
case_audit_plant_agent_projection() {
  # Asserts SPEC-0001 EVERY_BACKUP_IS_CLASSIFIABLE.
  local row label kind node proj ghost name s p rc
  for row in \
      "X390 agent agents/billing-auditor.md .claude/agents/billing-auditor.md .claude/agents/ghost.md" \
      "X391 skill skills/billing-rules.md .claude/skills/billing-rules/SKILL.md .claude/skills/ghost/SKILL.md" \
      "X392 agent agents/billing-auditor.md .github/agents/billing-auditor.agent.md .github/agents/ghost.agent.md"; do
    set -- $row; label="$1" kind="$2" node="$3" proj="$4" ghost="$5"
    name="$(basename "$node" .md)"; s="$RW/$label-seed"; p="$RW/$label-plant"
    mkdir -p "$s/agents" "$s/skills/spec-author" "$p/docs/graph/$(dirname "$node")" \
             "$p/$(dirname "$proj")" "$p/$(dirname "$ghost")"
    printf 'seed agent body\n' > "$s/agents/05-reviewer.md"
    printf 'seed skill body\n' > "$s/skills/spec-author/SKILL.md"
    printf -- '---\nname: %s\nid: %s.%s\nkind: %s\norigin: project\n---\n# %s\n' \
      "$name" "$kind" "$name" "$kind" "$name" > "$p/docs/graph/$node"
    printf -- '---\nname: %s\n---\n# %s\n' "$name" "$name" > "$p/$proj"
    printf -- '---\nname: %s\n---\n# %s, older\n' "$name" "$name" > "$p/$proj.bak-20260304-000000"
    python3 "$AUDIT" "$p" "$s" --date=20260304 >"$RW/$label.out" 2>&1 && rc=0 || rc=$?
    grep -q "backups audited: 1" "$RW/$label.out" || { echo "$label fixture: expected one backup audited: $(flat "$RW/$label.out")"; return 1; }
    grep -q "'UNMAPPED': 0" "$RW/$label.out" && ! grep -q "UNMAPPED backup" "$RW/$label.out" && [ "$rc" -eq 0 ] \
      || { echo "$label: the $proj backup of an origin: project $kind was UNMAPPED or not exit 0 (got $rc): $(flat "$RW/$label.out")"; return 1; }
    # guard: a projection with no seed source and no plant node stays UNMAPPED, exit 1
    printf 'a projection nobody owns\n' > "$p/$ghost.bak-20260305-000000"
    python3 "$AUDIT" "$p" "$s" --date=20260305 >"$RW/$label.guard" 2>&1 && rc=0 || rc=$?
    grep -q "'UNMAPPED': 1" "$RW/$label.guard" && [ "$rc" -eq 1 ] \
      || { echo "$label: the $ghost backup with no seed source and no plant node must stay UNMAPPED, exit 1 (got $rc): $(flat "$RW/$label.guard")"; return 1; }
  done
}

# -- GA-C4: backups inside a nested plant copy are not this plant's -----------
case_audit_skips_nested_plant_copy() {
  local s="$RW/c4seed" p="$RW/c4plant" n rc
  mkdir -p "$s/agents" "$p/docs/graph/agents" "$p/.cypress"
  printf '{"seed": "cypress", "version": "1.0.0"}\n' > "$p/.cypress/seed.json"
  printf 'seed agent body\n' > "$s/agents/reviewer.md"
  cp "$s/agents/reviewer.md" "$p/docs/graph/agents/reviewer.md"
  cp "$s/agents/reviewer.md" "$p/docs/graph/agents/reviewer.md.bak-20260306-000000"
  # a scratch copy of a plant under this plant's root, with backups of its own
  n="$p/.scratch/plant-copy"
  mkdir -p "$n/.cypress" "$n/docs/graph/agents" "$n/docs/graph/nodes"
  cp "$p/.cypress/seed.json" "$n/.cypress/seed.json"
  printf 'nested copy body\n' > "$n/docs/graph/agents/other.md.bak-20260306-000000"
  printf 'nested plant fact\n' > "$n/docs/graph/nodes/api.md.bak-20260306-000000"
  printf 'nested plant fact, later\n' > "$n/docs/graph/nodes/api.md.bak-20260307-000000"
  python3 "$AUDIT" "$p" "$s" --date=20260306 >"$RW/c4.out" 2>&1 && rc=0 || rc=$?
  grep -q "backups audited: 1 " "$RW/c4.out" \
    || { echo "backups inside a directory holding its own .cypress/seed.json were counted: $(flat "$RW/c4.out")"; return 1; }
  ! grep -q "UNMAPPED backup\|knowledge overwrite" "$RW/c4.out" \
    || { echo "a nested copy's backups were classified as this plant's: $(flat "$RW/c4.out")"; return 1; }
  [ "$rc" -eq 0 ] || { echo "the plant's own clean backup must audit exit 0 (got $rc): $(flat "$RW/c4.out")"; return 1; }
  # the default --date is this plant's newest stamp, not a nested copy's
  python3 "$AUDIT" "$p" "$s" >"$RW/c4.dflt" 2>&1 && rc=0 || rc=$?
  grep -q "backups audited: 1 " "$RW/c4.dflt" && [ "$rc" -eq 0 ] \
    || { echo "with --date omitted, a nested copy's newer stamp chose the day audited (exit $rc): $(flat "$RW/c4.dflt")"; return 1; }
}

# -- GL: the graft ledger ------------------------------------------------------
# A synthetic seed repository with three tagged releases, and a plant stamped at
# the second. Each seed file is set so that one class is the only right answer:
#   file                        v1.0.0   v1.1.0 (base)  v1.2.0 (seed)   plant
#   protocols/ff.md             ff1      ff2            ff3             ff2            FAST-FORWARD
#   protocols/ff2.md            gg1      gg2            gg3             gg2            FAST-FORWARD
#   protocols/keep.md           k1       k1             k1              k1 + plant     KEEP-PLANT
#   protocols/merge.md          m1       m1             m1 + seed       m1 + plant     MERGE
#   protocols/current.md        c1       c1             c1              c1             CURRENT
#   core/method/moved.md        v1       v1             v2              v2             CURRENT
#   protocols/new.md            -        -              n1              -              SEED-NEW
#   agents/harvested.md         h1       h1             h1 + plant + s  h1 + plant     HARVESTED
#   agents/deleted.md           d1 d2 d3 d1 d2 d3       d1 d2 d3 + p + s d1 d3 + p     MERGE
# agents/deleted.md: the plant deleted d2 the seed still carries; adopting the
# seed would bring d2 back, so it is MERGE (GL-b2), not HARVESTED (GL-b).
# docs/graph/nodes/own.md is the plant's own node: no row. Byte-equal files at
# v1.1.0: ff.md, ff2.md, current.md (3); at v1.2.0: current.md, moved.md (2);
# at v1.0.0: current.md, moved.md (2). So content lineage finds v1.1.0, from 3.
GL_SEED="$RW/glseed"; GL_PLANT="$RW/glplant"
gl_release() {  # $1 version; the files are written by the caller
  printf '{"name": "cypress", "version": "%s"}\n' "$1" > "$GL_SEED/manifest.json"
  sgit -C "$GL_SEED" add -A && sgit -C "$GL_SEED" commit -q -m "release $1" && sgit -C "$GL_SEED" tag "v$1"
}
gl_fixture() {
  [ -f "$RW/gl.ready" ] && return 0
  local s="$GL_SEED" p="$GL_PLANT"
  mkdir -p "$s/protocols" "$s/core/method" "$s/agents"
  sgit -C "$s" init -q || { echo "fixture: git init failed"; return 1; }
  printf 'ff1\n' > "$s/protocols/ff.md"; printf 'gg1\n' > "$s/protocols/ff2.md"
  printf 'k1\n' > "$s/protocols/keep.md"; printf 'm1\n' > "$s/protocols/merge.md"
  printf 'c1\n' > "$s/protocols/current.md"; printf 'v1\n' > "$s/core/method/moved.md"
  printf 'h1\n' > "$s/agents/harvested.md"
  printf 'd1\nd2\nd3\n' > "$s/agents/deleted.md"
  gl_release 1.0.0 || { echo "fixture: release 1.0.0 failed"; return 1; }
  printf 'ff2\n' > "$s/protocols/ff.md"; printf 'gg2\n' > "$s/protocols/ff2.md"
  gl_release 1.1.0 || { echo "fixture: release 1.1.0 failed"; return 1; }
  # the plant, as the v1.1.0 install left it, then edited by the plant
  mkdir -p "$p/.cypress" "$p/docs/graph/protocols" "$p/docs/graph/method" "$p/docs/graph/agents" "$p/docs/graph/nodes"
  printf '{"seed": "cypress", "version": "1.1.0", "tools": "claude-code"}\n' > "$p/.cypress/seed.json"
  for f in ff ff2 keep merge current; do cp "$s/protocols/$f.md" "$p/docs/graph/protocols/$f.md"; done
  cp "$s/agents/harvested.md" "$p/docs/graph/agents/harvested.md"
  printf 'd1\nd3\na plant line the seed later harvests\n' > "$p/docs/graph/agents/deleted.md"
  printf 'k1\na plant rule\n' > "$p/docs/graph/protocols/keep.md"
  printf 'm1\na plant merge line\n' > "$p/docs/graph/protocols/merge.md"
  printf 'h1\na plant addition\n' > "$p/docs/graph/agents/harvested.md"
  printf 'v2\n' > "$p/docs/graph/method/moved.md"
  printf -- '---\nid: subsystem.own\n---\n# own\n' > "$p/docs/graph/nodes/own.md"
  # v1.2.0: the seed moves on, and harvests the plant's addition
  printf 'ff3\n' > "$s/protocols/ff.md"; printf 'gg3\n' > "$s/protocols/ff2.md"
  printf 'm1\na seed merge line\n' > "$s/protocols/merge.md"
  printf 'v2\n' > "$s/core/method/moved.md"; printf 'n1\n' > "$s/protocols/new.md"
  printf 'h1\na plant addition\na later seed line\n' > "$s/agents/harvested.md"
  printf 'd1\nd2\nd3\na plant line the seed later harvests\na later seed line\n' > "$s/agents/deleted.md"
  gl_release 1.2.0 || { echo "fixture: release 1.2.0 failed"; return 1; }
  touch "$RW/gl.ready"
}
gl_need() { [ -f "$LEDGER" ] || { echo "tools/graft-ledger.py does not exist"; return 1; }; }
# the one class on the one row that names a file (its plant path, or its seed path)
gl_class_of() {  # $1 output file, $2 plant path, $3 seed path
  python3 - "$1" "$2" "$3" <<'PY'
import re, sys
text = open(sys.argv[1]).read().splitlines()
want = {sys.argv[2], sys.argv[3]}
classes = re.compile(r"(?<![A-Z-])(FAST-FORWARD|KEEP-PLANT|MERGE|CURRENT|SEED-NEW|HARVESTED)(?![A-Z-])")
rows = [l for l in text if want & set(re.split(r"[\s|,`]+", l))]
if len(rows) != 1:
    print(f"{len(rows)} rows name {sys.argv[2]}"); sys.exit(1)
found = classes.findall(rows[0])
if len(found) != 1:
    print(f"the row for {sys.argv[2]} carries {len(found)} classes: {rows[0]!r}"); sys.exit(1)
print(found[0])
PY
}

case_ledger_classifies_three_ways() {
  local rc got want row path seedpath
  gl_need || return 1; gl_fixture || return 1
  python3 "$LEDGER" "$GL_PLANT" "$GL_SEED" >"$RW/gla.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] || { echo "graft-ledger.py exited $rc: $(flat "$RW/gla.out")"; return 1; }
  for row in \
      "docs/graph/protocols/ff.md protocols/ff.md FAST-FORWARD" \
      "docs/graph/protocols/ff2.md protocols/ff2.md FAST-FORWARD" \
      "docs/graph/protocols/keep.md protocols/keep.md KEEP-PLANT" \
      "docs/graph/protocols/merge.md protocols/merge.md MERGE" \
      "docs/graph/protocols/current.md protocols/current.md CURRENT" \
      "docs/graph/method/moved.md core/method/moved.md CURRENT" \
      "docs/graph/protocols/new.md protocols/new.md SEED-NEW" \
      "docs/graph/agents/harvested.md agents/harvested.md HARVESTED" \
      "docs/graph/agents/deleted.md agents/deleted.md MERGE"; do
    set -- $row; path="$1"; seedpath="$2"; want="$3"
    got="$(gl_class_of "$RW/gla.out" "$path" "$seedpath")" || { echo "$got: $(flat "$RW/gla.out")"; return 1; }
    [ "$got" = "$want" ] || { echo "$path classed $got, want $want: $(flat "$RW/gla.out")"; return 1; }
  done
  ! grep -q "nodes/own\.md" "$RW/gla.out" || { echo "the plant's own node got a machinery row: $(flat "$RW/gla.out")"; return 1; }
}

case_ledger_base_from_tag() {
  local rc
  gl_need || return 1; gl_fixture || return 1
  python3 "$LEDGER" "$GL_PLANT" "$GL_SEED" --base >"$RW/glc.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] || { echo "graft-ledger.py --base exited $rc: $(flat "$RW/glc.out")"; return 1; }
  grep -q "v1\.1\.0" "$RW/glc.out" || { echo "--base did not print the stamped version's tag v1.1.0: $(flat "$RW/glc.out")"; return 1; }
  grep -qi "tag" "$RW/glc.out" && ! grep -qi "inferred" "$RW/glc.out" \
    || { echo "--base did not say the base came from the tag: $(flat "$RW/glc.out")"; return 1; }
}

case_ledger_base_inferred_by_lineage() {
  local rc s="$RW/glseed-untagged" want other
  gl_need || return 1; gl_fixture || return 1
  rm -rf "$s"; cp -R "$GL_SEED" "$s"
  sgit -C "$s" tag -d v1.1.0 >/dev/null || { echo "fixture: could not delete the tag in the copy"; return 1; }
  want="$(sgit -C "$s" rev-parse 'HEAD~1')"
  python3 "$LEDGER" "$GL_PLANT" "$s" --base >"$RW/gld.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] || { echo "graft-ledger.py --base with the tag gone exited $rc: $(flat "$RW/gld.out")"; return 1; }
  python3 - "$RW/gld.out" "$want" "$(sgit -C "$s" rev-parse HEAD)" "$(sgit -C "$s" rev-parse 'HEAD~2')" <<'PY' || return 1
import re, sys
out = open(sys.argv[1]).read()
want, others = sys.argv[2], sys.argv[3:]
hexes = set(re.findall(r"\b[0-9a-f]{7,40}\b", out))
if not any(want.startswith(h) for h in hexes):
    print(f"the commit content lineage finds ({want[:12]}) is not printed: {out!r}"); sys.exit(1)
if any(o.startswith(h) for h in hexes for o in others):
    print(f"another release's commit is printed as the base: {out!r}"); sys.exit(1)
if not re.search(r"\binferred\b", out, re.I):
    print(f"the base is not said to be inferred: {out!r}"); sys.exit(1)
if not any(re.search(r"\b3\b", l) and re.search(r"match", l, re.I) for l in out.splitlines()):
    print(f"the number of files that matched (3) is not printed on a line about matching: {out!r}"); sys.exit(1)
PY
}

# -- GR: the graft run driver ---------------------------------------------------
# A plant installed from this seed, then edited so a graft has mechanical work:
# a stale grill-lint.py, a graph-lint.py whose KIND_PREFIX the plant set, a
# seed protocol node deleted (the installer re-creates it), and a plant node of
# its own. It is a Git repository, so the checksum covers .git as well. The
# stage for a normal run is a SIBLING whose name extends the plant's, so a
# refusal that compared path strings by prefix would refuse it.
GR="$RW/gr"; GR_PLANT="$GR/zephyrplant"; GR_STAGE="$GR/zephyrplant-stage"
gr_need() { [ -f "$RUN" ] || { echo "tools/graft-run.py does not exist"; return 1; }; }
gr_sum() {  # a checksum of every entry under $1, .git included, symlinks not followed
  python3 - "$1" <<'PY'
import hashlib, os, sys
root, h = sys.argv[1], hashlib.sha256()
for d, dirs, files in os.walk(root, followlinks=False):
    dirs.sort()
    for n in sorted(dirs + files):
        p = os.path.join(d, n); rel = os.path.relpath(p, root)
        if os.path.islink(p):
            h.update(b"L" + rel.encode() + b"\0" + os.readlink(p).encode() + b"\0")
        elif os.path.isfile(p):
            h.update(b"F" + rel.encode() + b"\0" + open(p, "rb").read() + b"\0")
        else:
            h.update(b"D" + rel.encode() + b"\0")
print(h.hexdigest())
PY
}
gr_fixture() {
  [ -f "$GR/ready" ] && return 0
  local p="$GR_PLANT"
  mkdir -p "$p"
  bash "$ROOT/install.sh" claude-code --project-dir "$p" >"$GR/fixture-install.log" 2>&1 \
    || { echo "fixture: install.sh into the synthetic plant failed: $(tail -3 "$GR/fixture-install.log" | tr '\n' ' ')"; return 1; }
  grep -v waves "$KG/grill-lint.py" > "$p/docs/graph/grill-lint.py"
  sed -e 's/^KIND_PREFIX = {}$/KIND_PREFIX = {"operator": "op."}/' "$KG/graph-lint.py" > "$p/docs/graph/graph-lint.py"
  grep -qx 'KIND_PREFIX = {"operator": "op."}' "$p/docs/graph/graph-lint.py" \
    || { echo "fixture: the seed's graph-lint.py no longer carries KIND_PREFIX = {}"; return 1; }
  [ -f "$p/docs/graph/protocols/brainstorm.md" ] || { echo "fixture: no docs/graph/protocols/brainstorm.md placed"; return 1; }
  rm -f "$p/docs/graph/protocols/brainstorm.md"
  mkdir -p "$p/docs/graph/nodes"
  printf -- '---\nid: subsystem.quokka-ledger\nkind: subsystem\n---\n# Quokka ledger\n' \
    > "$p/docs/graph/nodes/subsystem.quokka-ledger.md"
  # a version with no tag, so graft-ledger infers the base by lineage (GR-h)
  python3 -c 'import json,sys; f=sys.argv[1]; d=json.load(open(f)); d["version"]="0.0.0"; open(f,"w").write(json.dumps(d, indent=2)+"\n")' "$p/.cypress/seed.json"
  sgit -C "$p" init -q && sgit -C "$p" add -A && sgit -C "$p" commit -q -m plant \
    || { echo "fixture: the synthetic plant could not be committed"; return 1; }
  gr_sum "$p" > "$GR/sum.before"
  touch "$GR/ready"
}
gr_run_once() {  # one run for GR-b..GR-f; stdout and stderr kept apart
  [ -f "$GR/run.rc" ] && return 0
  python3 "$RUN" "$GR_PLANT" "$ROOT" --stage "$GR_STAGE" >"$GR/run.out" 2>"$GR/run.err" && echo 0 >"$GR/run.rc" || echo $? >"$GR/run.rc"
  gr_sum "$GR_PLANT" > "$GR/sum.after"
}
gr_copy() {  # the plant copy inside the stage: the directory holding the plant's own node
  find "$GR_STAGE" -path '*/docs/graph/nodes/subsystem.quokka-ledger.md' 2>/dev/null | head -1 | sed 's#/docs/graph/nodes/subsystem.quokka-ledger.md$##'
}

case_run_refuses_stage_inside_plant() {
  local rc before
  gr_need || return 1; gr_fixture || return 1
  before="$(cat "$GR/sum.before")"
  python3 "$RUN" "$GR_PLANT" "$ROOT" --stage "$GR_PLANT/.graft-stage" >"$GR/a1.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 2 ] || { echo "a stage inside the plant exited $rc, want 2: $(flat "$GR/a1.out")"; return 1; }
  grep -qi "inside" "$GR/a1.out" || { echo "the refusal does not say the stage is inside the plant: $(flat "$GR/a1.out")"; return 1; }
  [ ! -e "$GR_PLANT/.graft-stage" ] && [ "$(gr_sum "$GR_PLANT")" = "$before" ] \
    || { echo "a refused run wrote into the plant"; return 1; }
  # a stage path that reaches the plant through a symlink is inside it too
  ln -s "$GR_PLANT" "$GR/plant-link"
  python3 "$RUN" "$GR_PLANT" "$ROOT" --stage "$GR/plant-link/stage" >"$GR/a2.out" 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 2 ] || { echo "a stage reaching the plant through a symlink exited $rc, want 2: $(flat "$GR/a2.out")"; return 1; }
  [ ! -e "$GR_PLANT/stage" ] && [ "$(gr_sum "$GR_PLANT")" = "$before" ] \
    || { echo "a refused run (symlinked stage) wrote into the plant"; return 1; }
}

case_run_leaves_plant_byte_identical() {
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  [ "$(cat "$GR/run.rc")" != 2 ] || { echo "a stage outside the plant (a sibling whose name extends the plant's) was refused: $(flat "$GR/run.err")"; return 1; }
  [ -d "$GR_STAGE" ] || { echo "the run made no stage at $GR_STAGE: $(flat "$GR/run.err")"; return 1; }
  cmp -s "$GR/sum.before" "$GR/sum.after" || { echo "the plant tree (.git included) changed during the run"; return 1; }
}

case_run_stage_holds_installed_copy_and_log() {
  local c
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  c="$(gr_copy)"
  [ -n "$c" ] || { echo "no copy of the plant (its node subsystem.quokka-ledger.md) in the stage: $(flat "$GR/run.err")"; return 1; }
  cmp -s "$c/docs/graph/protocols/brainstorm.md" "$ROOT/protocols/brainstorm.md" \
    || { echo "the installer did not run in the stage copy: docs/graph/protocols/brainstorm.md was not re-placed"; return 1; }
  grep -rlq '^\[seed\] done\.' "$GR_STAGE" 2>/dev/null \
    || { echo "no captured install log (the installer's '[seed] done.' line) in the stage"; return 1; }
}

case_run_reconciles_three_engines() {
  local c e pairs
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  c="$(gr_copy)"; [ -n "$c" ] || { echo "no copy of the plant in the stage"; return 1; }
  pairs=""
  for e in graph-lint.py spec-lint.py grill-lint.py; do pairs="$pairs --engine=$c/docs/graph/$e:$KG/$e"; done
  python3 "$AUDIT" "$c" "$ROOT" $pairs >"$GR/d.out" 2>&1 || true
  [ "$(grep -c "graph engine: current" "$GR/d.out")" -eq 3 ] \
    || { echo "the three engines in the stage are not all current: $(grep "graph engine" "$GR/d.out" | tr '\n' ' ')"; return 1; }
  grep -qx 'KIND_PREFIX = {"operator": "op."}' "$c/docs/graph/graph-lint.py" \
    || { echo "the plant's KIND_PREFIX was not preserved by the reconcile"; return 1; }
}

case_run_derives_tokens_from_plant() {
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  python3 - "$GR/run.out" <<'PY' || return 1
import re, sys
out = open(sys.argv[1]).read()
m = re.findall(r"--tokens[= ]([^\s]+)", out)
if not m:
    print(f"no --tokens list printed: {out[-600:]!r}"); sys.exit(1)
toks = {t.strip("'\"").lower() for x in m for t in x.split(",")}
miss = [w for w, alts in (("the plant's name", {"zephyrplant"}),
                          ("a node id", {"subsystem.quokka-ledger", "quokka-ledger"}),
                          ("the stamp's seed name", {"cypress"}))
        if not toks & alts]
if miss:
    print(f"the --tokens list lacks {', '.join(miss)}: {sorted(toks)}"); sys.exit(1)
PY
}

case_run_prints_gate_table() {
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  python3 - "$GR/run.out" "$ROOT/protocols/graft.md" <<'PY' || return 1
import re, sys
out = [l for l in open(sys.argv[1]).read().splitlines() if l.strip()]
gates = []
for l in open(sys.argv[2]).read().splitlines():
    m = re.match(r"\| `(graft\.gate\.[a-z-]+)` \|.*\| (hard|soft|detective|judgment) \|\s*$", l)
    if m:
        gates.append(m.groups())
if len(gates) < 10:
    print(f"fixture: only {len(gates)} gate rows parsed from protocols/graft.md"); sys.exit(1)
tail = out[-len(gates):]
if len(tail) < len(gates):
    print(f"stdout has {len(out)} lines, fewer than the {len(gates)} gate rows"); sys.exit(1)
for (gid, cls), line in zip(gates, tail):
    if not line.strip().startswith(gid + ":"):
        print(f"stdout does not end with the gate table in its order: want {gid!r}, got {line!r}"); sys.exit(1)
    rest = line.strip()[len(gid) + 1:].strip()
    if cls == "judgment":
        if not re.search(r"not run", rest, re.I) or rest.startswith("PASS"):
            print(f"judgment gate {gid} is not marked as not run by the tool: {line!r}"); sys.exit(1)
    elif not re.match(r"(PASS|BLOCK|N-A)\b", rest):
        print(f"mechanical gate {gid} carries no PASS / BLOCK / N-A: {line!r}"); sys.exit(1)
PY
}

case_run_exits_1_when_a_gate_blocks() {
  # the fixture deletes a seed node the install re-creates, so the gate table holds a BLOCK.
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  grep -Eq '^[[:space:]]*graft\.gate\.[a-z-]+:[[:space:]]*BLOCK' "$GR/run.out" \
    || { echo "fixture: no gate row of the run says BLOCK: $(tail -5 "$GR/run.out" | tr '\n' ' ')"; return 1; }
  [ "$(cat "$GR/run.rc")" = 1 ] \
    || { echo "a run whose gate table holds a BLOCK exited $(cat "$GR/run.rc"), want 1"; return 1; }
}

case_run_passes_inferred_base_to_audit() {
  # the fixture plant is stamped 0.0.0 (no tag), so graft-ledger infers the base.
  gr_need || return 1; gr_fixture || return 1; gr_run_once
  python3 - "$GR/run.out" <<'PY' || return 1
import re, sys
out = open(sys.argv[1]).read()
m = re.search(r"base: ([0-9a-f]{7,64}) \(inferred", out)
if not m:
    print(f"fixture: the run did not print a base inferred by content lineage: {out[:600]!r}"); sys.exit(1)
rev = m.group(1)
audit = [l for l in out.splitlines() if l.startswith("audit: --date=")]
if len(audit) != 1:
    print(f"fixture: want one `audit: --date=` line, got {len(audit)}: {out[:600]!r}"); sys.exit(1)
b = re.search(r"--base=([0-9A-Za-z._/-]+)", audit[0])
if not b or not (rev.startswith(b.group(1)) or b.group(1).startswith(rev)):
    print(f"the inferred base {rev[:12]} was not passed to graft-audit as --base: {audit[0]!r}"); sys.exit(1)
row = [l for l in out.splitlines() if l.strip().startswith("graft.gate.customization:")]
if not row or f"--base={b.group(1)}" not in row[0]:
    print(f"the customization gate row does not name --base={b.group(1)}: {row!r}"); sys.exit(1)
PY
}

collect_case GA-C1 case_audit_base_identical_is_delta "a backup byte-identical to the seed at --base is DELTA; without --base it stays CUSTOMIZED"
collect_case GA-C2 case_audit_engine_signal_survives "an engine backup whose signal lines survive in the current engine is not CUSTOMIZED"
collect_case X390 case_audit_plant_agent_projection "GA-C3: a plant-owned node's agent, skill (X391) and Copilot (X392) projection backups are classified, exit 0"
collect_case GA-C4 case_audit_skips_nested_plant_copy "backups under a nested .cypress/seed.json directory are not counted"
collect_case GL-a case_ledger_classifies_three_ways "the ledger prints one class per seed-owned machinery file (HARVESTED, a plant deletion MERGE)"
collect_case GL-c case_ledger_base_from_tag "--base prints the stamped version's tag, from the tag"
collect_case GL-d case_ledger_base_inferred_by_lineage "--base with no tag prints the lineage commit, its match count, inferred"
collect_case GR-a case_run_refuses_stage_inside_plant "a stage inside the plant is refused, exit 2, nothing written"
collect_case GR-b case_run_leaves_plant_byte_identical "the plant tree is byte-identical after a run"
collect_case GR-c case_run_stage_holds_installed_copy_and_log "the stage holds an installed copy of the plant and the install log"
collect_case GR-d case_run_reconciles_three_engines "the three engines in the stage are reconciled"
collect_case GR-e case_run_derives_tokens_from_plant "the --tokens list is derived from the plant"
collect_case GR-f case_run_prints_gate_table "stdout ends with the Phase 7 gate table"
collect_case GR-g case_run_exits_1_when_a_gate_blocks "a run whose gate table holds a BLOCK exits 1"
collect_case GR-h case_run_passes_inferred_base_to_audit "an inferred base is passed to graft-audit as --base"
[ "$CASE_FAILED" -eq 0 ] \
  || { echo "test-graft-tools: FAIL — failing cases (above)" >&2; exit 1; }

echo "test-graft-tools: PASS"
