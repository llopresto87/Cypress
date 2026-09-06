#!/usr/bin/env bash
# test-graft-tools.sh — the graft support tools do what graft.md relies on:
#   graft-graph-engine.py  adopts the seed engine body, preserves plant config,
#                          detects a plant superset, and no-ops when current.
#   graft-audit.py         classifies backups IDENTICAL / DELTA / CUSTOMIZED,
#                          flags a buried customization (exit 1), passes a clean FF,
#                          maps every delivered tool (status-register.py included)
#                          to its seed source, and with --unfilled reports the
#                          template scaffolds a plant never filled (byte-identical
#                          to templates/docs/**), renaming (--rename) or removing
#                          (--prune) them on request; verification.md is exempt
#                          only when it carries an executed gate row.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE="$ROOT/tools/graft-graph-engine.py"
AUDIT="$ROOT/tools/graft-audit.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

# ---- graft-graph-engine.py ------------------------------------------------
# seed engine: new helper line + default KINDS + KIND_PREFIX
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
echo "  engine merge: adopted body, UNIONED KINDS (kept plant + gained seed), adopted default KIND_PREFIX — OK"

# idempotent: second run is a no-op
python3 "$ENGINE" "$TMP/plant-lint.py" "$TMP/seed-lint.py" 2>&1 | grep -q "already current" || fail "engine merge not idempotent"
echo "  engine merge idempotent — OK"

# superset: plant already has everything seed has, plus extra -> KEEP-PLANT
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
echo "  superset detection (KEEP-PLANT, unchanged) — OK"

# ---- graft-audit.py -------------------------------------------------------
# 6.0.0 plant layout: machinery home is docs/graph/{protocols,skills,agents,
# method,templates}/ (seed-owned); tool dirs hold only agent/skill projections;
# everything else under docs/graph/ is plant-authored knowledge.
DATE=20260101
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
echo "  audit classification + gate exit(1) on buried customization — OK"

# clean FF (no customization): exit 0
rm -f "$TMP/plant/docs/graph/agents/b.md.bak-$DATE-000000"
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout2" 2>&1
rc2=$?
set -e
[ "$rc2" -eq 0 ] || { cat "$TMP/aout2"; fail "clean FF must exit 0 (got $rc2)"; }
echo "  audit passes a clean fast-forward (exit 0) — OK"

# plant-authored graph content overwritten (backup outside the machinery
# subtrees, e.g. nodes/) -> knowledge overwrite, exit 1
mkdir -p "$TMP/plant/docs/graph/nodes"
printf 'plant-authored node fact\n' > "$TMP/plant/docs/graph/nodes/api.md.bak-$DATE-000000"
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout3" 2>&1
rc3=$?
set -e
grep -q "knowledge overwrite" "$TMP/aout3" || { cat "$TMP/aout3"; fail "plant-authored graph overwrite not flagged"; }
[ "$rc3" -eq 1 ] || fail "audit must exit 1 on a plant-authored knowledge overwrite (got $rc3)"
echo "  audit flags plant-authored docs/graph/ overwrite (seed-owned vs plant-owned) — OK"

# REGRESSION — a wrong plant root must not read as a clean audit. Zero backups
# under a directory with no docs/graph/ once printed the same "clean" line and
# exit 0 a real audit earns; auditing nothing proves nothing.
mkdir -p "$TMP/notaplant"
set +e
python3 "$AUDIT" "$TMP/notaplant" "$TMP/seed" --date=$DATE >"$TMP/aout4" 2>&1
rc4=$?
set -e
grep -q "not a plant root" "$TMP/aout4" || { cat "$TMP/aout4"; fail "wrong root not refused"; }
[ "$rc4" -eq 1 ] || fail "audit must exit 1 on a non-plant root (got $rc4)"
echo "  audit refuses a vacuous run against a non-plant root (exit 1) — OK"

# REGRESSION — zero backups for the REQUESTED date while backups exist for
# another date is a wrong --date, not a clean graft: the real fast-forward
# went unexamined. (Zero backups anywhere stays a legitimate no-op graft —
# idempotent installs make that the normal case.)
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=19990101 --tokens=widgetco >"$TMP/aout5" 2>&1
rc5=$?
set -e
grep -q "wrong --date" "$TMP/aout5" || { cat "$TMP/aout5"; fail "wrong --date not flagged"; }
[ "$rc5" -eq 1 ] || fail "audit must exit 1 on a date that audited nothing while backups exist (got $rc5)"
echo "  audit refuses a vacuous audit under a wrong --date (exit 1) — OK"

# REGRESSION — space-form options: `--tokens acme` once silently dropped the
# value into the positionals (audited with DEFAULT tokens; a plant
# customization matching ONLY the explicit token then classified DELTA and
# the audit printed clean/exit 0). Both forms must behave identically now,
# and stray positionals must fail. Plant a token-only line (no generic
# signal words) so the explicit token is load-bearing.
rm -f "$TMP/plant/docs/graph/nodes/api.md.bak-$DATE-000000"
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
echo "  audit accepts --flag value form; stray positionals fail loudly — OK"

# REGRESSION — _schema.md and index.md are project-instantiated (plant-owned):
# a backup over docs/graph/_schema.md is a knowledge overwrite, not exempt
# machinery (graft.md: copying the seed template would regress placeholders).
printf 'plant-instantiated schema\n' > "$TMP/plant/docs/graph/_schema.md.bak-$DATE-000000"
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout8" 2>&1
rc8=$?
set -e
grep -q "knowledge overwrite" "$TMP/aout8" || { cat "$TMP/aout8"; fail "_schema.md overwrite not flagged as knowledge"; }
[ "$rc8" -eq 1 ] || fail "audit must exit 1 on a schema overwrite (got $rc8)"
rm -f "$TMP/plant/docs/graph/_schema.md.bak-$DATE-000000"
echo "  audit flags _schema.md/index.md overwrites as plant knowledge — OK"

# REGRESSION — plant-AUTHORED project skills live under docs/graph/skills/
# too; the wholesale machinery-subtree exemption hid their overwrites
# (UNMAPPED, never scanned, "clean"). A machinery-shaped path with no seed
# source is plant knowledge.
printf 'plant-authored skill body\n' > "$TMP/plant/docs/graph/skills/deploy-widgetco.md.bak-$DATE-000000"
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout9" 2>&1
rc9=$?
set -e
grep -q "knowledge overwrite" "$TMP/aout9" || { cat "$TMP/aout9"; fail "plant-authored skill overwrite not flagged"; }
grep -q "UNMAPPED backup" "$TMP/aout9" || { cat "$TMP/aout9"; fail "unmapped backups not listed"; }
[ "$rc9" -eq 1 ] || fail "audit must exit 1 on a plant-skill overwrite (got $rc9)"
rm -f "$TMP/plant/docs/graph/skills/deploy-widgetco.md.bak-$DATE-000000"
echo "  audit flags plant-authored docs/graph/skills/ overwrites; lists UNMAPPED — OK"

# REGRESSION — a flag must never swallow a flag: `--tokens --engine=x` once
# consumed "--engine=x" as the token value and audited with defaults.
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --tokens --engine=x >"$TMP/aout10" 2>&1
rc10=$?
set -e
[ "$rc10" -eq 2 ] || { cat "$TMP/aout10"; fail "flag-swallowed-flag must exit 2 (got $rc10)"; }
echo "  audit rejects a flag consumed as a value (exit 2) — OK"

# ---- delivered-tool registry: status-register.py (7.0.0) -------------------
# install.sh delivers tools/status-register.py as docs/graph/status-register.py
# (config-free fast-forward machinery, the agent-lint class). The audit must
# map that path to its seed source, or every fast-forward of it reads as an
# UNMAPPED knowledge overwrite of docs/graph/.
mkdir -p "$TMP/seed/tools"
printf 'seed status register body\n' > "$TMP/seed/tools/status-register.py"
python3 - "$AUDIT" "$TMP/seed" <<'PY'
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("graft_audit", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
seed = Path(sys.argv[2])
got = m.seed_source_for("docs/graph/status-register.py", seed)
want = seed / "tools/status-register.py"
assert got == want, f"seed_source_for -> {got!r}, want {want!r}"
assert "status-register.py" in m.SCAFFOLD_FILES, m.SCAFFOLD_FILES
assert m.is_seed_owned_graph_path("docs/graph/status-register.py")
PY
cp "$TMP/seed/tools/status-register.py" "$TMP/plant/docs/graph/status-register.py.bak-$DATE-000000"
set +e
python3 "$AUDIT" "$TMP/plant" "$TMP/seed" --date=$DATE --tokens=widgetco >"$TMP/aout11" 2>&1
rc11=$?
set -e
grep -q "'IDENTICAL': 4" "$TMP/aout11" || { cat "$TMP/aout11"; fail "status-register.py backup not mapped to tools/status-register.py"; }
grep -q "knowledge overwrite" "$TMP/aout11" && { cat "$TMP/aout11"; fail "status-register.py fast-forward wrongly flagged as knowledge"; }
[ "$rc11" -eq 0 ] || { cat "$TMP/aout11"; fail "identical status-register.py backup must audit clean (got $rc11)"; }
rm -f "$TMP/plant/docs/graph/status-register.py.bak-$DATE-000000"
echo "  status-register.py registered: seed_source_for + SCAFFOLD_FILES + clean FF — OK"

# ---- --unfilled: template scaffolds never filled (D-SCAFFOLD, 7.0.0) --------
# install.sh copies templates/docs/<rel> to docs/graph/<rel> when missing; a
# leaf still BYTE-IDENTICAL to its template at grow Phase 6 / graft Phase 7
# was never filled. Fixture: rollback.md identical (unfilled), release.md
# filled, a plant node with no counterpart, api/README.md absent in the plant.
FIX="$ROOT/tests/fixtures/graft"
unfilled_plant() { rm -rf "$TMP/uplant"; cp -R "$FIX/plant" "$TMP/uplant"; }

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
echo "  --unfilled reports exactly the byte-identical scaffold, exit 1, plant untouched — OK"

# --rename: <name>.unfilled.md, exit 0; a second pass finds nothing
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
echo "  --unfilled --rename -> <name>.unfilled.md, exit 0, filled + plant files untouched — OK"

# --prune: removed outright, exit 0
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
echo "  --unfilled --prune removes the scaffold, exit 0 — OK"

# verification.md exemption, both ways: byte-identical WITHOUT an executed
# gate row is unfilled like any scaffold; byte-identical WITH one (the seed
# template itself carries a `**executed <date>**` row) is exempt.
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
echo "  verification.md: unfilled without an executed gate row, exempt with one — OK"

# the real seed layout: templates/docs/<rel> mirrors docs/graph/<rel>
rm -rf "$TMP/rplant"; mkdir -p "$TMP/rplant/docs/graph/runbooks"
cp "$ROOT/templates/docs/runbooks/rollback.md" "$TMP/rplant/docs/graph/runbooks/rollback.md"
set +e
python3 "$AUDIT" "$TMP/rplant" "$ROOT" --unfilled >"$TMP/uout7" 2>&1
urc7=$?
set -e
grep -q "^  UNFILLED docs/graph/runbooks/rollback.md" "$TMP/uout7" || { cat "$TMP/uout7"; fail "real seed template not mirrored to docs/graph/"; }
[ "$urc7" -eq 1 ] || { cat "$TMP/uout7"; fail "real-seed unfilled scaffold must gate (got $urc7)"; }
echo "  --unfilled mirrors the real seed's templates/docs/ onto docs/graph/ — OK"

# flag discipline: --rename/--prune act only on --unfilled findings, and never both
set +e
python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --prune >"$TMP/uout8" 2>&1; urc8=$?
python3 "$AUDIT" "$TMP/uplant" "$FIX/seed" --unfilled --rename --prune >"$TMP/uout9" 2>&1; urc9=$?
python3 "$AUDIT" "$TMP/uplant" "$TMP/notaplant" --unfilled >"$TMP/uout10" 2>&1; urc10=$?
set -e
[ "$urc8" -eq 2 ] || { cat "$TMP/uout8"; fail "--prune without --unfilled must exit 2 (got $urc8)"; }
[ "$urc9" -eq 2 ] || { cat "$TMP/uout9"; fail "--rename with --prune must exit 2 (got $urc9)"; }
[ "$urc10" -eq 1 ] || { cat "$TMP/uout10"; fail "a seed root without templates/docs/ must be refused (got $urc10)"; }
grep -q "templates/docs" "$TMP/uout10" || { cat "$TMP/uout10"; fail "seed-root refusal must name templates/docs/"; }
echo "  --unfilled flag discipline (prune needs unfilled; rename xor prune; seed root checked) — OK"

echo "test-graft-tools: PASS"
