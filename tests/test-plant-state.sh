#!/usr/bin/env bash
# Persistent plant state contract (.cypress/seed.json): the stamp records what
# the plant carries, merged into, never rebuilt from the current invocation.
#   S1  an invocation that does not alter an owner decision keeps it
#       (SPEC-0001 DECISIONS_SURVIVE_SILENCE)
#   S2  installed adapters accumulate unless explicitly removed
#       (SPEC-0001 ADAPTERS_ACCUMULATE)
#   S4  undecided / no / yes stay distinct (held in case_drift)
#   S5  agent_projections is derived from the adapter list
#   S6  yes => corpus whole on disk; no => corpus absent
#       (SPEC-0001 RECORD_AGREES_WITH_DISK, CORPUS_IS_WHOLE_OR_ABSENT,
#        CONTRADICTORY_CORPUS_TRANSITION)
#   S7  an unreadable record is refused before the first write
#   S8  a frozen host skipped by `all` is named in a WARNING, left byte-identical
#       (SPEC-0001 ALL_NAMES_SKIPPED_FROZEN_HOSTS)
#   S9  the session-record form is placed; a re-install keeps the plant's
#       records and its edited form (SPEC-0001 SESSION_RECORD_FORM_IS_PLACED)
#   S10 a re-install leaves a plant's older engine alone
#       (SPEC-0001 EXISTING_PLANT_RECEIVES_CURRENT_ENGINES; graft half in
#        test-graft-tools.sh X383-X387)
#   S11 unknown stamp keys survive; a non-object stamp is backed up and named
#       (SPEC-0001 UNKNOWN_STAMP_KEYS_SURVIVE, STAMP_NOT_AN_OBJECT)
#   S12 a stamp cut off inside a field, or not UTF-8, takes the preflight
#       refusal, not the STAMP_NOT_AN_OBJECT backup (held in case_s7)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$ROOT/tests/test-plant-state.sh"
export ROOT

fail() { echo "FAIL: $*" >&2; exit 1; }
# A real JSON parse, not a copy of install.sh's own reader.
field() {
    STAMP_PATH="$1" STAMP_KEY="$2" python3 - <<'PYEOF'
import json, os, sys
with open(os.environ["STAMP_PATH"], encoding="utf-8") as fh:
    data = json.load(fh)
value = data.get(os.environ["STAMP_KEY"], "")
sys.stdout.write(value if isinstance(value, str) else repr(value))
PYEOF
}
# Files and links: under --symlink the corpus is a tree of links.
pages() {
    [[ -d "$1/docs/graph/legal/corpus" ]] || { printf '0\n'; return 0; }
    find "$1/docs/graph/legal/corpus" \( -type f -o -type l \) -name '*.md' \
        -not -name '*.bak-*' | wc -l | tr -d ' '
}
seed_pages() { find "$ROOT/legal-corpus" -type f -not -name '*.bak-*' | wc -l | tr -d ' '; }


case_s1_s2_s5() {
local WORK; WORK="$(mktemp -d)"
T="$WORK/seq"; mkdir -p "$T"
"$ROOT/install.sh" claude-code --legal-corpus yes --legal-jurisdiction it \
    --project-dir "$T" >/dev/null 2>&1 || fail "first install failed"
S="$T/.cypress/seed.json"
[[ "$(field "$S" legal_corpus)" == "yes" ]] || fail "first install did not record the corpus decision"

"$ROOT/install.sh" prime-agent --force --project-dir "$T" >/dev/null 2>&1 \
    || fail "second (unrelated) install failed"
got="$(field "$S" tools)"
[[ "$got" == *claude-code* ]] || fail "S2: installing prime-agent FORGOT claude-code (tools=$got)"
[[ "$got" == *prime-agent* ]] || fail "S2: prime-agent was not recorded (tools=$got)"
[[ "$(field "$S" legal_corpus)" == "yes" ]] \
    || fail "S1: a run passing no legal flag RESET the owner's corpus decision"
[[ "$(field "$S" legal_jurisdiction)" == "it" ]] \
    || fail "S1: a run passing no jurisdiction flag RESET the owner's jurisdiction"
grep -q '"tool": "claude-code"' "$S" || fail "S5: claude-code projection missing"
grep -q '"tool": "prime-agent"' "$S" || fail "S5: prime-agent projection missing"

# Order independence: the reverse sequence must reach the same adapter set.
R="$WORK/rev"; mkdir -p "$R"
"$ROOT/install.sh" prime-agent --project-dir "$R" >/dev/null 2>&1
"$ROOT/install.sh" claude-code --project-dir "$R" >/dev/null 2>&1
for a in claude-code prime-agent; do
    grep -q "\"tool\": \"$a\"" "$R/.cypress/seed.json" \
        || fail "order dependence: $a absent when installed in the reverse order"
done
rm -rf "$WORK"
}

caseALL_NAMES_SKIPPED_FROZEN_HOSTS() {
local WORK; WORK="$(mktemp -d)"
# S8 (SPEC-0001, ADR-0009); the WARNING is FROZEN_PROJECTION_LEFT_STALE.
P="$WORK/frozen"; mkdir -p "$P"
"$ROOT/install.sh" codex --project-dir "$P" >/dev/null 2>&1 || fail "codex install failed"
[[ "$(field "$P/.cypress/seed.json" tools)" == *codex* ]] \
    || fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: setup — the stamp does not record codex"
[[ -d "$P/.codex" ]] || fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: setup — no .codex/ to compare"
tree_sum() { (cd "$1" && find . | LC_ALL=C sort && find . -type f -exec cksum {} + | LC_ALL=C sort); }
before="$(tree_sum "$P/.codex")"
err="$WORK/all.err"
"$ROOT/install.sh" all --project-dir "$P" >/dev/null 2>"$err" \
    || { cat "$err" >&2; fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: install.sh all failed"; }
grep -i 'not refreshed' "$err" | grep -qF 'codex' \
    || { cat "$err" >&2; fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: stderr does not name codex as not refreshed"; }
grep -qF 'install.sh all codex' "$err" \
    || { cat "$err" >&2; fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: stderr does not name the command that refreshes codex (install.sh all codex)"; }
grep -i 'not refreshed' "$err" | grep -qF 'WARNING' \
    || { cat "$err" >&2; fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: the skip is not printed as a WARNING"; }
! grep -q 'DEPRECATED' "$err" \
    || { cat "$err" >&2; fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: the skip path printed the DEPRECATED notice for a host that all did not install"; }
[[ "$before" == "$(tree_sum "$P/.codex")" ]] \
    || fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: install.sh all changed .codex/, which it no longer installs"
[[ " $(field "$P/.cypress/seed.json" tools) " == *" codex "* ]] \
    || fail "ALL_NAMES_SKIPPED_FROZEN_HOSTS: the stamp forgot codex (ADAPTERS_ACCUMULATE)"
echo "  ALL_NAMES_SKIPPED_FROZEN_HOSTS: all names the skipped frozen host and leaves it untouched — OK"
rm -rf "$WORK"
}

case_s6() {
local WORK; WORK="$(mktemp -d)"
# S6: the record never contradicts the disk.
L="$WORK/legal"; mkdir -p "$L"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$L" >/dev/null 2>&1 \
    || fail "S6: recording 'no' on a plant with no corpus must be allowed"
[[ ! -d "$L/docs/graph/legal/corpus" ]] || fail "S6: 'no' was recorded but a corpus was placed"
[[ "$(field "$L/.cypress/seed.json" legal_corpus)" == "no" ]] || fail "S6: the stamp did not record 'no'"

"$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$L" >/dev/null 2>&1 \
    || fail "S6: no -> yes must be allowed"
want="$(seed_pages)"
[[ "$(pages "$L")" -ge "$want" ]] \
    || fail "S6: 'yes' must place the WHOLE corpus ($(pages "$L") of $want)"
diff -r "$ROOT/legal-corpus" "$L/docs/graph/legal/corpus" >/dev/null \
    || fail "S6: the placed corpus is not byte-identical to the seed's"

# yes -> no while the corpus is on disk is refused; disk and record untouched.
if "$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$L" >/dev/null 2>&1; then
    fail "S6: 'no' was accepted while $(pages "$L") corpus pages sit on disk"
fi
[[ "$(field "$L/.cypress/seed.json" legal_corpus)" == "yes" ]] \
    || fail "S6: a REFUSED transition still changed the record"
[[ "$(pages "$L")" -eq "$want" ]] \
    || fail "S6: a refused transition deleted corpus pages"

# The deliberate route out stays open.
rm -rf "$L/docs/graph/legal/corpus"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$L" >/dev/null 2>&1 \
    || fail "S6: after a deliberate removal, recording 'no' must be allowed"
[[ "$(field "$L/.cypress/seed.json" legal_corpus)" == "no" ]] \
    || fail "S6: deliberate removal then 'no' did not record 'no'"

# A value outside yes/no, or a jurisdiction that is not a country code, is refused.
B="$WORK/bad"; mkdir -p "$B"
"$ROOT/install.sh" claude-code --project-dir "$B" --legal-corpus foo >/dev/null 2>&1 \
    && fail "S6: --legal-corpus took a value other than yes/no"
"$ROOT/install.sh" claude-code --project-dir "$B" --legal-jurisdiction italy >/dev/null 2>&1 \
    && fail "S6: --legal-jurisdiction took a non-country-code"
rm -rf "$WORK"
}

case_plan_records() {
local WORK; WORK="$(mktemp -d)"
# A plant's own plan records are never touched by the seed. The seed ships two
# leaves into plans/: an empty grill.md scaffold and the session-record form (S9).
local FORM="docs/graph/plans/sessions/_session-record.template.md"
local SEED_FORM="$ROOT/templates/docs/plans/sessions/_session-record.template.md"
local REC="docs/graph/plans/sessions/2026-01-01-example.md"
P="$WORK/plan-records"; mkdir -p "$P"
"$ROOT/install.sh" claude-code --project-dir "$P" >/dev/null 2>&1 \
    || fail "baseline install failed"
[[ -f "$P/$FORM" ]] || fail "S9: a fresh install holds no $FORM"
cmp -s "$SEED_FORM" "$P/$FORM" \
    || fail "S9: the placed $FORM is not byte-identical to the seed's form"

mkdir -p "$P/docs/graph/plans/grill"
printf '# grill — this plant\n\n## 9. Implementation Plan\n\n| # | Increment | Status | Detail |\n|---|---|---|---|\n| 1 | Ours | done | `plans/grill/increment-01-ours.md` |\n' \
    >"$P/docs/graph/plans/grill.md"
printf '### Increment 1 — Ours\nPLANT-DECISION-RECORD\n' \
    >"$P/docs/graph/plans/grill/increment-01-ours.md"
printf 'a decision the plant made\n' >"$P/docs/graph/plans/our-other-plan.md"
printf '# Session record: 2026-01-01, example\nA synthetic record.\n' >"$P/$REC"
printf '\n<!-- edited by the plant -->\n' >>"$P/$FORM"
records() { (cd "$P" && cat docs/graph/plans/grill.md docs/graph/plans/grill/increment-01-ours.md \
    docs/graph/plans/our-other-plan.md "$REC" "$FORM" | cksum); }
plan_sum="$(records)"

"$ROOT/install.sh" all --project-dir "$P" >/dev/null 2>&1 || fail "re-install failed"
"$ROOT/install.sh" all --project-dir "$P" --symlink >/dev/null 2>&1 || true

[[ "$plan_sum" == "$(records)" ]] \
    || fail "an install CHANGED the plant's plan records, a session record (S9) or the edited form"
[[ "$(find "$P/docs/graph/plans" -name '*.bak-*' | wc -l | tr -d ' ')" -eq 0 ]] \
    || fail "an install backed up (therefore replaced) a plant plan or session record"
# ...and none of the seed's own plans came along.
for leaked in $(ls "$P/docs/graph/plans"); do
    case "$leaked" in
        grill|grill.md|our-other-plan.md|adopted-instructions.md|sessions) ;;
        *) fail "the seed leaked '$leaked' into the plant's plans/" ;;
    esac
done
echo "  a plant's plan and session records and the edited form survive every install (S9) — OK"
rm -rf "$WORK"
}

case_corpus_linkmodes() {
local WORK; WORK="$(mktemp -d)"
# The corpus lands whole under --symlink (the copy mode is case_s6).
M="$WORK/corpus-symlink"; mkdir -p "$M"
"$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$M" --symlink \
    >/dev/null 2>&1 || fail "S6: --legal-corpus yes failed under --symlink"
[[ "$(pages "$M")" -ge "$(seed_pages)" ]] \
    || fail "S6: --symlink placed $(pages "$M") of $(seed_pages) corpus pages"
echo "  the whole corpus lands under --symlink — OK"
rm -rf "$WORK"
}

case_corpus_surplus() {
local WORK; WORK="$(mktemp -d)"
# A plant ingest beside the whole corpus is named, kept, and not refused.
SUR="$WORK/surplus"; mkdir -p "$SUR"
"$ROOT/install.sh" claude-code --project-dir "$SUR" --copy --legal-corpus yes >/dev/null 2>&1 \
    || fail "S6 surplus: the baseline install with --legal-corpus yes failed"
printf -- '---\ntitle: a locally ingested statute\n---\nbody\n' \
    > "$SUR/docs/graph/legal/corpus/national/zz-plant-ingest.md"
"$ROOT/install.sh" codex --project-dir "$SUR" --copy >"$WORK/surplus.log" 2>&1 \
    || { tail -5 "$WORK/surplus.log" >&2
         fail "S6 surplus: a plant ingest beside the whole corpus must not refuse the install"; }
grep -q "beyond the" "$WORK/surplus.log" \
    || fail "S6 surplus: the extra page must be NAMED in the log, not absorbed silently"
[[ -f "$SUR/docs/graph/legal/corpus/national/zz-plant-ingest.md" ]] \
    || fail "S6 surplus: the plant's own ingest was deleted by a re-install"
echo "  a plant ingest beside the whole corpus is named, kept, and not refused — OK"
rm -rf "$WORK"
}

case_drift() {
local WORK; WORK="$(mktemp -d)"
want="$(seed_pages)"
# A recorded yes over a corpus lost out-of-band is restored, and announced.
# The baseline names an uncarried jurisdiction: a request, never an error.
D="$WORK/drift"; mkdir -p "$D"
out="$("$ROOT/install.sh" claude-code --legal-corpus yes --legal-jurisdiction zz \
    --project-dir "$D" 2>&1)" \
    || fail "S6/drift: an uncarried jurisdiction was treated as an error"
grep -q "NATIONAL LAYER MISSING for 'zz'" <<<"$out" \
    || fail "S6/drift: a missing national layer was not surfaced"
grep -q "research-scout ingest" <<<"$out" || fail "S6/drift: the missing layer named no remedy"
[[ -f "$D/docs/graph/legal/corpus/eu/gdpr.md" ]] \
    || fail "S6/drift: an uncarried jurisdiction lost the EU layer too"
rm -rf "$D/docs/graph/legal/corpus"
out="$("$ROOT/install.sh" opencode --project-dir "$D" 2>&1)" \
    || fail "S6/drift: a later adapter install must still succeed"
[[ "$(field "$D/.cypress/seed.json" legal_corpus)" == "yes" ]] \
    || fail "S6/drift: the recorded decision must survive"
[[ "$(pages "$D")" -eq "$want" ]] \
    || fail "S6/drift: the record says yes, so the corpus must be restored — found $(pages "$D") of $want pages"
grep -q "records" <<<"$out" \
    || fail "S6/drift: restoring pages a plant may have deleted on purpose must be ANNOUNCED"

# ...and the other two decisions are untouched by that inheritance.
N="$WORK/drift-no"; mkdir -p "$N"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$N" >/dev/null 2>&1
"$ROOT/install.sh" opencode --project-dir "$N" >/dev/null 2>&1
[[ "$(pages "$N")" -eq 0 ]] || fail "S6/drift: a plant recorded 'no' must not acquire a corpus"
# S4: silence on a fresh plant is undecided, for the corpus and the jurisdiction.
U="$WORK/drift-undecided"; mkdir -p "$U"
out="$("$ROOT/install.sh" claude-code --project-dir "$U" 2>&1)"
[[ "$(field "$U/.cypress/seed.json" legal_corpus)" == "undecided" ]] \
    || fail "S4: an unasked corpus decision must read 'undecided', never 'no'"
grep -q "NEXT STEP — legal corpus undecided" <<<"$out" \
    || fail "S4: an undecided corpus was not surfaced as a NEXT STEP"
[[ "$(field "$U/.cypress/seed.json" legal_jurisdiction)" == "undecided" ]] \
    || fail "S4: an unnamed jurisdiction was not recorded undecided"
grep -q "NEXT STEP — national jurisdiction undecided" <<<"$out" \
    || fail "S4: an unnamed jurisdiction was not surfaced"
"$ROOT/install.sh" opencode --project-dir "$U" >/dev/null 2>&1
[[ "$(field "$U/.cypress/seed.json" legal_corpus)" == "undecided" ]] \
    || fail "S6/drift: an undecided plant must stay undecided"
[[ "$(pages "$U")" -eq 0 ]] || fail "S6/drift: an undecided plant must not acquire a corpus"
rm -rf "$WORK"
}

case_s7() {
local WORK; WORK="$(mktemp -d)"
# S7/S12: an unreadable record is refused BEFORE the first write. Each shape
# must exit non-zero with the preflight's refusal line, leave the stamp
# byte-identical and the file listing unchanged (so no seed.json.bak-*).
# truncated and not-utf8 are S12: they take this refusal, not the
# STAMP_NOT_AN_OBJECT backup.
S="$WORK/unreadable"; mkdir -p "$S"
"$ROOT/install.sh" claude-code --legal-corpus yes --legal-jurisdiction it \
    --project-dir "$S" >/dev/null 2>&1 || fail "S7 setup install failed"

corrupt_zero()      { : > "$1"; }
corrupt_garbage()   { printf 'this is not json at all\n' > "$1"; }
corrupt_array()     { python3 -c "
import json,sys; p=sys.argv[1]; d=json.load(open(p))
d['tools']=d['tools'].split(); open(p,'w').write(json.dumps(d,indent=2))" "$1"; }
corrupt_bool()      { python3 -c "
import json,sys; p=sys.argv[1]; d=json.load(open(p))
d['legal_corpus']=True; open(p,'w').write(json.dumps(d,indent=2))" "$1"; }
corrupt_truncated() { printf '{"seed": "cypress", "legal_corpus": "ye' > "$1"; }
corrupt_not_utf8()  { printf '{"seed": "cypress", "legal_corpus": "yes", "note": "caf\351"}\n' > "$1"; }

local bad=0 shape
for shape in zero garbage array bool truncated not_utf8; do
  (
    T="$WORK/unreadable-$shape"
    cp -a "$S" "$T"
    "corrupt_$shape" "$T/.cypress/seed.json"
    cp "$T/.cypress/seed.json" "$WORK/stamp-$shape"
    before="$(find "$T" \( -type f -o -type l \) | sort)"
    rc=0
    out="$("$ROOT/install.sh" codex --project-dir "$T" 2>&1)" || rc=$?
    [[ $rc -ne 0 ]] || fail "S7/$shape: an unreadable .cypress/seed.json was accepted (exit 0)"
    [[ "$before" == "$(find "$T" \( -type f -o -type l \) | sort)" ]] \
        || fail "S7/$shape: the refusal wrote to the plant"
    cmp -s "$T/.cypress/seed.json" "$WORK/stamp-$shape" \
        || fail "S7/$shape: the stamp's bytes changed; it is refused, not rewritten"
    grep -qF 'refusing to install: .cypress/seed.json' <<<"$out" \
        || fail "S7/$shape: no preflight refusal line. Output ends: $(tail -3 <<<"$out" | tr '\n' ' ')"
  ) || bad=1
done
[[ $bad -eq 0 ]] || exit 1

# ...and the readable stamp is still read.
T="$WORK/unreadable-control"; cp -a "$S" "$T"
"$ROOT/install.sh" codex --project-dir "$T" >/dev/null 2>&1 \
    || fail "S7 control: a VALID stamp was refused"
[[ "$(field "$T/.cypress/seed.json" legal_corpus)" == "yes" ]] \
    || fail "S7 control: the recorded decision did not survive a normal re-run"
[[ "$(field "$T/.cypress/seed.json" tools)" == "claude-code codex" ]] \
    || fail "S7 control: adapters did not accumulate"
rm -rf "$WORK"
}

case_engine_upgrade() {
local WORK; WORK="$(mktemp -d)"
# S10: a re-install never overwrites a placed engine (plant-owned, ADR-0014).
local KG="$ROOT/templates/knowledge-graph" G="docs/graph" OLD="$WORK/grill-lint.older.py"
P="$WORK/engines"; mkdir -p "$P"
"$ROOT/install.sh" claude-code --project-dir "$P" >/dev/null 2>&1 \
    || fail "S10: the fresh claude-code install failed"
grep -v waves "$KG/grill-lint.py" >"$OLD" || true
cmp -s "$OLD" "$KG/grill-lint.py" && fail "S10: setup — the older body equals the seed's grill-lint.py"
cp "$OLD" "$P/$G/grill-lint.py"
"$ROOT/install.sh" claude-code --project-dir "$P" >/dev/null 2>&1 \
    || fail "S10: the re-install over the plant failed"
cmp -s "$OLD" "$P/$G/grill-lint.py" \
    || fail "S10: the re-install changed the plant's grill-lint.py; the engines are plant-owned (ADR-0014)"
[[ "$(find "$P/$G" -maxdepth 1 -name 'grill-lint.py.bak-*' | wc -l | tr -d ' ')" -eq 0 ]] \
    || fail "S10: the re-install wrote a grill-lint.py backup, so it replaced the engine"
echo "  S10: a re-install keeps the older engine — OK"
rm -rf "$WORK"
}

case_stamp_keys() {
local WORK; WORK="$(mktemp -d)"
# S11: a key the installer does not own is carried forward: JSON-equal value,
# original order, after the installer's own keys. `zz_note` sits before the
# installer's keys and `aa_annotation` after, so neither sorting nor the
# fixture's own position passes by accident.
local T="$WORK/stamp-keys"; mkdir -p "$T"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$T" >/dev/null 2>&1 \
    || fail "S11 setup install failed"
python3 - "$T/.cypress/seed.json" <<'PY' || fail "S11: could not write the stamp fixture"
import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
out = {"zz_note": "kept by the plant owner"}
out.update(d)
out["aa_annotation"] = {"reviewed_by": "owner", "rounds": [1, 2], "ok": True}
open(p, "w", encoding="utf-8").write(json.dumps(out, indent=2) + "\n")
PY
"$ROOT/install.sh" all --project-dir "$T" >/dev/null 2>&1 \
    || fail "S11: install.sh all over a stamp carrying two unknown keys failed"
python3 - "$T/.cypress/seed.json" <<'PY' || fail "S11 UNKNOWN_STAMP_KEYS_SURVIVE: see the line above"
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
keys = list(d)
own = {"seed", "version", "installed_at", "installed_from", "tools",
       "legal_corpus", "legal_jurisdiction", "agent_projections"}
carried = [k for k in keys if k not in own]
if carried != ["zz_note", "aa_annotation"]:
    sys.exit(f"S11: the keys the installer does not own are {carried!r} after the run, "
             f"expected ['zz_note', 'aa_annotation'] in their original order (keys: {keys!r})")
if keys[-2:] != carried:
    sys.exit(f"S11: the carried keys are not after the installer's own keys: {keys!r}")
if d["zz_note"] != "kept by the plant owner":
    sys.exit(f"S11: zz_note changed: {d['zz_note']!r}")
if d["aa_annotation"] != {"reviewed_by": "owner", "rounds": [1, 2], "ok": True}:
    sys.exit(f"S11: aa_annotation changed: {d['aa_annotation']!r}")
if d.get("legal_corpus") != "no":
    sys.exit(f"S11: the owner's legal_corpus decision did not survive: {d.get('legal_corpus')!r}")
if d.get("tools", "").split()[:1] != ["claude-code"]:
    sys.exit(f"S11: the installed adapters did not accumulate: {d.get('tools')!r}")
PY
# STAMP_NOT_AN_OBJECT: a JSON array stamp is moved to a .bak-<ts> sibling, a
# stamp is written from the installer's own keys, one warning names the backup.
local N="$WORK/stamp-array"; mkdir -p "$N"
"$ROOT/install.sh" claude-code --project-dir "$N" >/dev/null 2>&1 \
    || fail "S11 STAMP_NOT_AN_OBJECT setup install failed"
printf '["cypress", {"zz_note": "kept by the plant owner"}]\n' > "$N/.cypress/seed.json"
local out rc=0
out="$("$ROOT/install.sh" all --project-dir "$N" 2>&1)" || rc=$?
[[ $rc -eq 0 ]] || fail "S11 STAMP_NOT_AN_OBJECT: install over a stamp that is not a JSON object exited $rc: $(tail -3 <<<"$out")"
local bak; bak="$(find "$N/.cypress" -maxdepth 1 -name 'seed.json.bak-*' | head -1)"
[[ -n "$bak" ]] || fail "S11 STAMP_NOT_AN_OBJECT: the stamp was not moved to a seed.json.bak-* sibling"
grep -q 'zz_note' "$bak" || fail "S11 STAMP_NOT_AN_OBJECT: the backup does not hold the old stamp"
[[ "$(field "$N/.cypress/seed.json" seed)" == "cypress" ]] \
    || fail "S11 STAMP_NOT_AN_OBJECT: no stamp was written from the installer's own keys"
[[ "$(grep -c "$(basename "$bak")" <<<"$out")" -eq 1 ]] \
    || fail "S11 STAMP_NOT_AN_OBJECT: expected one warning naming $(basename "$bak")"
echo "  S11: unknown keys survive in order after the installer's own; a non-object stamp is backed up and named — OK"
rm -rf "$WORK"
}

# --- one-case subcommand, run by the parallel dispatcher ---------------------
if [ "${1:-}" = "__case" ]; then
  "$2"
  exit $?
fi

# Each case owns its mktemp target, so cases run concurrently under the gate's
# shared budget (tests/gate_pool.py).
SCN="$(mktemp)"
for c in case_s1_s2_s5 caseALL_NAMES_SKIPPED_FROZEN_HOSTS case_s6 case_plan_records case_corpus_linkmodes case_corpus_surplus case_drift case_s7 case_engine_upgrade case_stamp_keys; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"

[ "$rc" -eq 0 ] || { echo "plant-state: FAIL — a scenario failed" >&2; exit "$rc"; }
echo "plant-state: OK — decisions preserved, adapters accumulate, projections derived, record agrees with disk, an unreadable record is refused before any write"
