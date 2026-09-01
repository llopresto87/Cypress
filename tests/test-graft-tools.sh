#!/usr/bin/env bash
# test-graft-tools.sh — the graft support tools do what graft.md relies on:
#   graft-graph-engine.py  adopts the seed engine body, preserves plant config,
#                          detects a plant superset, and no-ops when current.
#   graft-audit.py         classifies backups IDENTICAL / DELTA / CUSTOMIZED,
#                          flags a buried customization (exit 1), passes a clean FF.
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

echo "test-graft-tools: PASS"
