#!/usr/bin/env bash
# Persistent plant state contract (.cypress/seed.json).
#
# The stamp is the plant's record of what it CARRIES — not a log of the last
# command typed. Every invariant below was violated at some point by a stamp
# that was rebuilt from the current invocation instead of merged into:
#   S1  an invocation that does not explicitly alter an owner decision keeps it
#       — asserts SPEC-0001 DECISIONS_SURVIVE_SILENCE
#   S2  installed adapters accumulate unless explicitly removed
#       — asserts SPEC-0001 ADAPTERS_ACCUMULATE
#   S3  recorded state corresponds to actual installed topology
#   S4  undecided / no / yes stay distinct
#   S5  agent_projections is DERIVED from the adapter list, never maintained
#   S6  yes => corpus complete on disk; no => corpus absent
#       — asserts SPEC-0001 RECORD_AGREES_WITH_DISK,
#         SPEC-0001 CORPUS_IS_WHOLE_OR_ABSENT and
#         SPEC-0001 CONTRADICTORY_CORPUS_TRANSITION
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$ROOT/tests/test-plant-state.sh"
export ROOT

fail() { echo "FAIL: $*" >&2; exit 1; }
# The oracle must not be the mechanism under test. This was a `sed` capture
# byte-identical in shape to install.sh's own reader, so every defect in that
# reader was invisible here by construction: the suite and the code agreed
# because they were the same code. A real JSON parse disagrees where it should.
field() {
    STAMP_PATH="$1" STAMP_KEY="$2" python3 - <<'PYEOF'
import json, os, sys
with open(os.environ["STAMP_PATH"], encoding="utf-8") as fh:
    data = json.load(fh)
value = data.get(os.environ["STAMP_KEY"], "")
sys.stdout.write(value if isinstance(value, str) else repr(value))
PYEOF
}
# `-type f -o -type l`, dormant footgun otherwise: under --symlink the corpus is
# a tree of links, and a bare `-type f` counts none of them. That exact mistake
# in install.sh made `--legal-corpus yes --symlink` die every time. No caller
# here passes a symlink install today, which is precisely why the wrong shape
# should not sit in the file that records the incident.
pages() {
    [[ -d "$1/docs/graph/legal/corpus" ]] || { printf '0\n'; return 0; }
    find "$1/docs/graph/legal/corpus" \( -type f -o -type l \) -name '*.md' \
        -not -name '*.bak-*' | wc -l | tr -d ' '
}


case_s1_s2_s5() {
local WORK; WORK="$(mktemp -d)"
# --- S1/S2/S5: an unrelated install must not narrow the record -------------
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

case_s4() {
local WORK; WORK="$(mktemp -d)"
# --- S4: silence on a FRESH plant is `undecided`, not `no` -----------------
U="$WORK/undecided"; mkdir -p "$U"
"$ROOT/install.sh" claude-code --project-dir "$U" >/dev/null 2>&1
[[ "$(field "$U/.cypress/seed.json" legal_corpus)" == "undecided" ]] \
    || fail "S4: an unasked corpus decision must read 'undecided', never 'no'"

rm -rf "$WORK"
}

case_s6() {
local WORK; WORK="$(mktemp -d)"
# --- S6: the record can never contradict the disk -------------------------
L="$WORK/legal"; mkdir -p "$L"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$L" >/dev/null 2>&1 \
    || fail "S6: recording 'no' on a plant with no corpus must be allowed"
[[ "$(pages "$L")" -eq 0 ]] || fail "S6: 'no' was recorded but corpus pages exist"

"$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$L" >/dev/null 2>&1 \
    || fail "S6: no -> yes must be allowed"
want="$(find "$ROOT/legal-corpus" -type f -not -name '*.bak-*' | wc -l | tr -d ' ')"
# -ge, not -eq: the contract is that no seed page is MISSING. A plant that
# ingests its own national statute under legal/corpus/ — which the installer's
# own notice tells it to do — carries more than the seed ships, and `-eq`
# reported that as "placed partially (17 of 16 pages)" and made the plant
# uninstallable. The shortfall direction is what this asserts.
[[ "$(pages "$L")" -ge "$want" ]] \
    || fail "S6: 'yes' must place the WHOLE corpus ($(pages "$L") of $want)"

# yes -> no while the corpus is on disk is a DESTRUCTIVE transition. It must be
# refused, and the refusal must leave both the disk and the record untouched.
if "$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$L" >/dev/null 2>&1; then
    fail "S6: 'no' was accepted while $(pages "$L") corpus pages sit on disk — the record now lies"
fi
[[ "$(field "$L/.cypress/seed.json" legal_corpus)" == "yes" ]] \
    || fail "S6: a REFUSED transition still changed the record"
[[ "$(pages "$L")" -eq "$want" ]] \
    || fail "S6: a refused transition deleted corpus pages — it must never delete"

# The deliberate route out stays open.
rm -rf "$L/docs/graph/legal/corpus"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$L" >/dev/null 2>&1 \
    || fail "S6: after a deliberate removal, recording 'no' must be allowed"
[[ "$(field "$L/.cypress/seed.json" legal_corpus)" == "no" ]] \
    || fail "S6: deliberate removal then 'no' did not record 'no'"

rm -rf "$WORK"
}

case_plan_records() {
local WORK; WORK="$(mktemp -d)"
# --- a plant's own plan records are never touched by the seed --------------
# The plan-of-record and its ledger files hold the plant's decisions: why a
# thing was built, what was rejected, what a steward ratified. They are the one
# artifact a project cannot reconstruct. The seed ships an empty grill.md
# scaffold into plans/ and nothing else, `plans/` is deliberately absent from
# graft-audit's MACHINERY_SUBTREES so it counts as plant knowledge, and an
# install must leave every byte of it alone — including the ledger children,
# which are new and which nothing in the seed knows the names of.
P="$WORK/plan-records"; mkdir -p "$P"
"$ROOT/install.sh" claude-code --project-dir "$P" >/dev/null 2>&1 \
    || fail "baseline install failed"
mkdir -p "$P/docs/graph/plans/grill"
printf '# grill — this plant\n\n## 9. Implementation Plan\n\n| # | Increment | Status | Detail |\n|---|---|---|---|\n| 1 | Ours | done | `plans/grill/increment-01-ours.md` |\n' \
    >"$P/docs/graph/plans/grill.md"
printf '### Increment 1 — Ours\nPLANT-DECISION-RECORD\n' \
    >"$P/docs/graph/plans/grill/increment-01-ours.md"
printf 'a decision the plant made\n' >"$P/docs/graph/plans/our-other-plan.md"
plan_sum="$(cat "$P/docs/graph/plans/grill.md" \
                "$P/docs/graph/plans/grill/increment-01-ours.md" \
                "$P/docs/graph/plans/our-other-plan.md" | cksum)"

"$ROOT/install.sh" all --project-dir "$P" >/dev/null 2>&1 || fail "re-install failed"
"$ROOT/install.sh" all --project-dir "$P" --symlink >/dev/null 2>&1 || true

after="$(cat "$P/docs/graph/plans/grill.md" \
             "$P/docs/graph/plans/grill/increment-01-ours.md" \
             "$P/docs/graph/plans/our-other-plan.md" | cksum)"
[[ "$plan_sum" == "$after" ]] \
    || fail "an install CHANGED the plant's own plan records — the one artifact \
a project cannot reconstruct"
[[ "$(find "$P/docs/graph/plans" -name '*.bak-*' | wc -l | tr -d ' ')" -eq 0 ]] \
    || fail "an install backed up (therefore replaced) a plant plan record"
# ...and nothing from the seed's own eighteen plans came along.
for leaked in $(ls "$P/docs/graph/plans"); do
    case "$leaked" in
        grill|grill.md|our-other-plan.md|adopted-instructions.md) ;;
        *) fail "the seed leaked '$leaked' into the plant's plans/ — the seed's own \
plan records must never reach a plant" ;;
    esac
done
echo "  a plant's plan records and ledger children survive every install — OK"

rm -rf "$WORK"
}

case_corpus_linkmodes() {
local WORK; WORK="$(mktemp -d)"
# --- the corpus works in BOTH link modes ----------------------------------
# `--legal-corpus yes --symlink` died with "placed partially (0 of 16 pages)"
# while all sixteen pages were present and correct as symlinks: the completeness
# check counted `-type f` only. The check written to prevent a partial corpus
# was the only thing preventing a whole one, and no test had ever combined the
# corpus flag with a link mode.
for mode in --copy --symlink; do
    M="$WORK/corpus$mode"; mkdir -p "$M"
    "$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$M" "$mode" \
        >/dev/null 2>&1 || fail "S6: --legal-corpus yes failed under $mode"
    got="$(find "$M/docs/graph/legal/corpus" \( -type f -o -type l \) \
           -not -name '*.bak-*' | wc -l | tr -d ' ')"
    seed_pages="$(find "$ROOT/legal-corpus" \( -type f -o -type l \) \
                  -not -name '*.bak-*' | wc -l | tr -d ' ')"
    [[ "$got" -ge "$seed_pages" ]] \
        || fail "S6: $mode placed $got of $seed_pages corpus pages"
done
echo "  the whole corpus lands under --copy AND --symlink — OK"

rm -rf "$WORK"
}

case_corpus_surplus() {
local WORK; WORK="$(mktemp -d)"
# A plant ingest ON TOP of the whole corpus must not be reported as partial, and
# must not make the plant uninstallable. Untested in both directions until now:
# the code moved from -eq to -lt, the contract's Then kept saying "equals", and
# the cited test asserted -eq — three homes, two of them falsified.
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
want="$(find "$ROOT/legal-corpus" -type f -not -name '*.bak-*' | wc -l | tr -d ' ')"
# --- the record cannot drift from the disk WITHOUT a wrong flag -----------
# S6 was only ever enforced on an explicit `--legal-corpus no`. A plant that
# decided `yes`, then lost the corpus out-of-band, then had a second adapter
# installed with no legal flag at all, kept a stamp reading `yes` over an empty
# directory — the exact contradiction the feature exists to prevent, reached
# without the owner typing anything wrong. The recorded decision now drives
# placement, so the corpus is restored to match what the plant says it carries.
D="$WORK/drift"; mkdir -p "$D"
"$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$D" >/dev/null 2>&1 \
    || fail "S6/drift: baseline yes-install failed"
rm -rf "$D/docs/graph/legal/corpus"
out="$("$ROOT/install.sh" opencode --project-dir "$D" 2>&1)" \
    || fail "S6/drift: a later adapter install must still succeed"
[[ "$(field "$D/.cypress/seed.json" legal_corpus)" == "yes" ]] \
    || fail "S6/drift: the recorded decision must survive"
[[ "$(pages "$D")" -eq "$want" ]] \
    || fail "S6/drift: the record says yes, so the corpus must be restored to \
match it — found $(pages "$D") of $want pages"
grep -q "records" <<<"$out" \
    || fail "S6/drift: restoring pages a plant may have deleted on purpose must \
be ANNOUNCED, not silent (the D2 rule)"

# ...and the other two decisions are untouched by that inheritance.
N="$WORK/drift-no"; mkdir -p "$N"
"$ROOT/install.sh" claude-code --legal-corpus no --project-dir "$N" >/dev/null 2>&1
"$ROOT/install.sh" opencode --project-dir "$N" >/dev/null 2>&1
[[ "$(pages "$N")" -eq 0 ]] || fail "S6/drift: a plant recorded 'no' must not acquire a corpus"
U="$WORK/drift-undecided"; mkdir -p "$U"
"$ROOT/install.sh" claude-code --project-dir "$U" >/dev/null 2>&1
"$ROOT/install.sh" opencode --project-dir "$U" >/dev/null 2>&1
[[ "$(field "$U/.cypress/seed.json" legal_corpus)" == "undecided" ]] \
    || fail "S6/drift: an undecided plant must stay undecided"
[[ "$(pages "$U")" -eq 0 ]] || fail "S6/drift: an undecided plant must not acquire a corpus"

rm -rf "$WORK"
}

case_edited() {
local WORK; WORK="$(mktemp -d)"
want="$(find "$ROOT/legal-corpus" -type f -not -name '*.bak-*' | wc -l | tr -d ' ')"
# --- a re-install over an EDITED corpus still leaves it whole --------------
# What this pins: after a re-install that backs up four edited pages, the plant
# holds the complete corpus AND four .bak siblings beside it.
#
# What it does NOT pin, stated so nobody reads more into it: install.sh's own
# completeness check was `-ge` over `find -type f`, which counts `.bak-*`
# siblings as corpus pages, so four backups would let a twelve-page corpus
# satisfy a sixteen-page check. That is now `-eq` over pages only. The fix is
# unreachable from here because `place_tree` never actually fails to place a
# page, so no public-interface sequence produces the partial corpus the old
# check would have waved through. It is a correction to what the check
# MEASURES, carried without a behavioural regression; it becomes testable the
# day placement can fail partway (an ENOSPC or permission fault mid-tree).
C="$WORK/count"; mkdir -p "$C"
"$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$C" >/dev/null 2>&1
D="$C/docs/graph/legal/corpus"
for f in $(find "$D" -name '*.md' | head -4); do printf '\n<!-- edited -->\n' >> "$f"; done
"$ROOT/install.sh" claude-code --legal-corpus yes --project-dir "$C" >/dev/null 2>&1 \
    || fail "re-install over an edited corpus failed"
[[ "$(find "$D" -name '*.bak-*' | wc -l | tr -d ' ')" -eq 4 ]] \
    || fail "expected 4 corpus backups to set up the counting case"
[[ "$(pages "$C")" -eq "$want" ]] \
    || fail "corpus page count must ignore .bak siblings (got $(pages "$C") want $want)"

rm -rf "$WORK"
}

case_s7() {
local WORK; WORK="$(mktemp -d)"
# S7 — an unreadable record is refused BEFORE the first write.
#
# This whole class shipped with no regression at all: the guard could be deleted
# outright and the full gate stayed green, while a zero-byte stamp — the exact
# outcome of the interrupted write `place_state` exists to prevent — narrowed
# `tools` to the adapter of the moment and reset a recorded `yes` to `undecided`
# over a corpus still on disk, at exit 0 with no warning.
#
# Four shapes, because the old guard keyed on which BYTES survived and so
# behaved differently for each: empty, garbage, and two that are valid JSON with
# a wrong type. The assertion is the same for all four — exit 1, and the plant
# is byte-for-byte what it was.
S="$WORK/unreadable"; mkdir -p "$S"
"$ROOT/install.sh" claude-code --legal-corpus yes --legal-jurisdiction it \
    --project-dir "$S" >/dev/null 2>&1 || fail "S7 setup install failed"

corrupt_zero()    { : > "$1"; }
corrupt_garbage() { printf 'this is not json at all\n' > "$1"; }
corrupt_array()   { python3 -c "
import json,sys; p=sys.argv[1]; d=json.load(open(p))
d['tools']=d['tools'].split(); open(p,'w').write(json.dumps(d,indent=2))" "$1"; }
corrupt_bool()    { python3 -c "
import json,sys; p=sys.argv[1]; d=json.load(open(p))
d['legal_corpus']=True; open(p,'w').write(json.dumps(d,indent=2))" "$1"; }

for shape in zero garbage array bool; do
    T="$WORK/unreadable-$shape"
    cp -a "$S" "$T"
    "corrupt_$shape" "$T/.cypress/seed.json"
    # A sorted listing, not a checksum: macOS has no `md5sum` (it has `md5`),
    # and this suite runs on the mac leg of the CI matrix. The listing is what
    # the assertion is actually about — did the refusal write anything.
    before="$(find "$T" \( -type f -o -type l \) | sort)"
    if "$ROOT/install.sh" codex --project-dir "$T" >/dev/null 2>&1; then
        fail "S7/$shape: an unreadable .cypress/seed.json was accepted (exit 0). \
A record that cannot be read is not a record that says nothing — re-deriving \
it overwrites decisions the owner made with this run's defaults."
    fi
    after="$(find "$T" \( -type f -o -type l \) | sort)"
    [[ "$before" == "$after" ]] \
        || fail "S7/$shape: the refusal wrote to the plant. It says \
'Nothing has been written', and that has to be true — it is a preflight."
done

# ...and the readable stamp is still read, or the refusal above is just a tool
# that always fails.
T="$WORK/unreadable-control"; cp -a "$S" "$T"
"$ROOT/install.sh" codex --project-dir "$T" >/dev/null 2>&1 \
    || fail "S7 control: a VALID stamp was refused"
[[ "$(field "$T/.cypress/seed.json" legal_corpus)" == "yes" ]] \
    || fail "S7 control: the recorded decision did not survive a normal re-run"
[[ "$(field "$T/.cypress/seed.json" tools)" == "claude-code codex" ]] \
    || fail "S7 control: adapters did not accumulate"

rm -rf "$WORK"
}

# --- one-case subcommand, run by the parallel dispatcher ---------------------
if [ "${1:-}" = "__case" ]; then
  "$2"
  exit $?
fi

# --- main: dispatch every INDEPENDENT scenario in parallel -------------------
# Each S-section is a self-contained scenario over its OWN mktemp target. The
# sequential-dependency sections (an install SEQUENCE into one plant: S6's
# no->yes->refuse->remove->no, S7's setup->corrupt->refuse->control) stay whole
# inside a single scenario; DIFFERENT S-sections are independent and run
# concurrently under the gate's ONE shared budget (tests/gate_pool.py,
# $GATE_JOBS / $GATE_POOL_DIR). Every assertion is byte-for-byte what it was.
SCN="$(mktemp)"
for c in case_s1_s2_s5 case_s4 case_s6 case_plan_records case_corpus_linkmodes case_corpus_surplus case_drift case_edited case_s7; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"

[ "$rc" -eq 0 ] || { echo "plant-state: FAIL — a scenario failed" >&2; exit "$rc"; }
echo "plant-state: OK — decisions preserved, adapters accumulate, projections derived, record agrees with disk, an unreadable record is refused before any write"
