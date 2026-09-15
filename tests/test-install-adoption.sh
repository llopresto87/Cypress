#!/usr/bin/env bash
# Adoption contract: install.sh meeting a project that already has its OWN
# files, and a plant that already carries the seed. Two ledger defects
# (U-12) drove this:
#   D1  asserts SPEC-0001 PREFLIGHT_REFUSES_BEFORE_WRITING,
#       SPEC-0001 DESTINATION_PATH_OCCUPIED and SPEC-0001 TARGET_NOT_WRITABLE.
#       A destination directory that already existed as a REGULAR FILE (or a
#       symlink to one) let place_kernel and the whole docs/graph/ scaffold
#       run to completion and then die on a raw `mkdir: ... Not a directory`
#       — never this tool's own die() — leaving the target half-installed.
#   D2  deleting a seed-owned node from an installed plant and re-installing
#       silently restored it: correct behaviour (the seed owns its
#       machinery), announced nowhere, so a deliberate deletion was reverted
#       with no trace and no way to tell "restored" from "always there".
# Alongside those: the ADOPTION cases place_kernel and place_file already
# handle correctly (a hand-written kernel backed up, a plant-authored graph
# leaf left alone) are pinned here too, so a future change to either cannot
# regress them unnoticed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
# chmod BEFORE rm: case 6 below leaves a target chmod 555'd, and an untouched
# trap would fail to remove it and leak a read-only directory into /tmp.
trap 'chmod -R u+w "$WORK" 2>/dev/null; rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "$1 — OK"; }

# ---------------------------------------------------------------------------
# 1. A pre-existing hand-written AGENTS.md is backed up, and the warning
#    names the backup. (claude-code's kernel dest is CLAUDE.md; place_kernel
#    finds no CLAUDE.md but an existing real AGENTS.md, so AGENTS.md becomes
#    the fast-forwarded "realfile" — this is the codepath that exercises it.)
# ---------------------------------------------------------------------------
T="$WORK/agents-only"; mkdir -p "$T"
printf '# hand-written AGENTS.md\nmy own project instructions\n' > "$T/AGENTS.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
    || fail "install over hand-written AGENTS.md failed: $out"
bak="$(ls -1dt "$T"/AGENTS.md.bak-* 2>/dev/null | head -1)"
[[ -n "$bak" ]] || fail "hand-written AGENTS.md was not backed up: $out"
grep -q "my own project instructions" "$bak" \
    || fail "AGENTS.md backup does not carry the original body"
grep -qF "$bak" <<<"$out" || fail "warning does not name the AGENTS.md backup: $out"
ok "pre-existing AGENTS.md backed up and named"

# ---------------------------------------------------------------------------
# 2. A pre-existing hand-written CLAUDE.md likewise.
# ---------------------------------------------------------------------------
T="$WORK/claude-only"; mkdir -p "$T"
printf '# hand-written CLAUDE.md\nmy other project instructions\n' > "$T/CLAUDE.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
    || fail "install over hand-written CLAUDE.md failed: $out"
bak="$(ls -1dt "$T"/CLAUDE.md.bak-* 2>/dev/null | head -1)"
[[ -n "$bak" ]] || fail "hand-written CLAUDE.md was not backed up: $out"
grep -q "my other project instructions" "$bak" \
    || fail "CLAUDE.md backup does not carry the original body"
grep -qF "$bak" <<<"$out" || fail "warning does not name the CLAUDE.md backup: $out"
ok "pre-existing CLAUDE.md backed up and named"

# ---------------------------------------------------------------------------
# 3. BOTH pre-existing with DIFFERENT bodies: neither body is lost without a
#    recoverable .bak.
# ---------------------------------------------------------------------------
T="$WORK/both-different"; mkdir -p "$T"
printf '# CLAUDE.md body\nCLAUDE-SENTINEL-ONE\n' > "$T/CLAUDE.md"
printf '# AGENTS.md body\nAGENTS-SENTINEL-TWO\n' > "$T/AGENTS.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
    || fail "install over two differing hand-written kernels failed: $out"
cbak="$(ls -1dt "$T"/CLAUDE.md.bak-* 2>/dev/null | head -1)"
abak="$(ls -1dt "$T"/AGENTS.md.bak-* 2>/dev/null | head -1)"
[[ -n "$cbak" ]] || fail "CLAUDE.md body lost with no .bak: $out"
[[ -n "$abak" ]] || fail "AGENTS.md body lost with no .bak: $out"
grep -q "CLAUDE-SENTINEL-ONE" "$cbak" || fail "CLAUDE.md's own body is not in its backup"
grep -q "AGENTS-SENTINEL-TWO" "$abak" || fail "AGENTS.md's own body is not in its backup"
ok "both differing pre-existing kernels recoverable from distinct backups"

# ---------------------------------------------------------------------------
# 4. A plant-authored docs/graph/index.md survives a re-install untouched
#    (add-if-missing).
# ---------------------------------------------------------------------------
T="$WORK/index-survives"; mkdir -p "$T"
"$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "baseline install for index-survives failed"
printf '\n<!-- PLANT-AUTHORED-SENTINEL: do not touch -->\n' >> "$T/docs/graph/index.md"
before="$(cat "$T/docs/graph/index.md")"
"$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "re-install for index-survives failed"
after="$(cat "$T/docs/graph/index.md")"
[[ "$before" == "$after" ]] || fail "docs/graph/index.md changed on a re-install with no new plant facts"
compgen -G "$T/docs/graph/index.md.bak-*" >/dev/null \
    && fail "docs/graph/index.md should never be backed up (add-if-missing, plant-owned)"
ok "plant-authored docs/graph/index.md survives a re-install untouched"

# ---------------------------------------------------------------------------
# 5. D1 — a target where .claude is a regular FILE fails with a non-zero
#    exit, a message NAMING that path, and writes NOTHING into the target.
# ---------------------------------------------------------------------------
T="$WORK/d1-file"; mkdir -p "$T"
touch "$T/.claude"
rc=0
out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" || rc=$?
[[ $rc -ne 0 ]] || fail "D1: install over a .claude FILE did not fail: $out"
grep -qF "$T/.claude" <<<"$out" || fail "D1: failure message does not name $T/.claude: $out"
[[ -e "$T/CLAUDE.md" ]] && fail "D1: CLAUDE.md was written despite the preflight failure"
[[ -e "$T/docs/graph" ]] && fail "D1: docs/graph/ was written despite the preflight failure"
[[ -f "$T/.claude" ]] || fail "D1: the offending .claude file itself should be left alone"
ok "D1: .claude-as-a-regular-file refuses before any write"

# ---------------------------------------------------------------------------
# 6. D1 — a read-only target (chmod 555) fails cleanly naming the path and
#    writes nothing.
# ---------------------------------------------------------------------------
T="$WORK/d1-readonly"; mkdir -p "$T"
chmod 555 "$T"
rc=0
out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" || rc=$?
chmod u+w "$T"
[[ $rc -ne 0 ]] || fail "D1: install into a read-only target did not fail: $out"
grep -qF "$T" <<<"$out" || fail "D1: read-only failure message does not name $T: $out"
[[ -e "$T/CLAUDE.md" ]] && fail "D1: CLAUDE.md was written despite the read-only target"
[[ -e "$T/docs" ]] && fail "D1: docs/ was written despite the read-only target"
ok "D1: read-only target refuses before any write"

# ---------------------------------------------------------------------------
# 7. D2 — install, delete 3 protocol files, re-install: exit 0, files
#    restored, AND the output names them as re-created. A FRESH install must
#    NOT emit that notice.
# ---------------------------------------------------------------------------
T="$WORK/d2-recreate"; mkdir -p "$T"
"$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "D2: baseline install failed"
# bash 3.2 (macOS) has no `mapfile`; read the list portably.
deleted=(); while IFS= read -r _l; do deleted+=("$_l"); done \
    < <(ls "$T"/docs/graph/protocols/*.md | head -3)
[[ ${#deleted[@]} -eq 3 ]] || fail "D2: could not find 3 protocol files to delete"
rm -f "${deleted[@]}"
out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)"; rc=$?
[[ $rc -eq 0 ]] || fail "D2: re-install after deleting protocol files did not exit 0: $out"
for f in "${deleted[@]}"; do
    [[ -f "$f" ]] || fail "D2: $f was not restored"
    grep -qF "$(basename "$f")" <<<"$out" \
        || fail "D2: output does not name the re-created file $(basename "$f"): $out"
done
grep -qi "re-created" <<<"$out" || fail "D2: output does not announce the re-creation: $out"

Tfresh="$WORK/d2-fresh"; mkdir -p "$Tfresh"
outfresh="$("$ROOT/install.sh" claude-code --project-dir "$Tfresh" --copy 2>&1)" \
    || fail "D2: fresh install failed"
grep -qi "re-created" <<<"$outfresh" \
    && fail "D2: a FRESH install must not emit the re-creation notice (it would be noise): $outfresh"
ok "D2: deleted protocol nodes are restored and named; a fresh install stays quiet"

# ---------------------------------------------------------------------------
# 8. A normal install and an identical re-install still produce ZERO
#    .bak-* files (idempotence must not have regressed).
# ---------------------------------------------------------------------------
T="$WORK/idempotent"; mkdir -p "$T"
"$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "idempotence: first install failed"
"$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "idempotence: second install failed"
n="$(find "$T" -name '*.bak-*' | wc -l | tr -d ' ')"
[[ "$n" -eq 0 ]] || { find "$T" -name '*.bak-*' >&2; fail "idempotence: identical re-install produced $n backup(s)"; }
ok "identical re-install stays backup-free"


# ---------------------------------------------------------------------------
# A path in the way NEVER produces a raw shell error, at any depth.
#
# Two layers, and the test asserts what each one really guarantees.
# preflight_destinations() refuses before ANY write, but it works from
# adapter_dirs() — a hand-written list that is a second home for what install_*
# already knows, and that drifted immediately: `.github/hooks` was missing, so a
# target holding a file there still wrote 195 files before dying on a raw
# `mkdir: Not a directory`. The list also does not enumerate the fourteen
# per-skill leaves under `.claude/skills/`, and never could without restating
# the skill roster.
#
# So the contract is layered: the declared areas fail EARLY and clean with
# nothing written, and everything else fails LATE but still clean, naming the
# path. What must never happen is a raw shell error from inside place_tree.
# ---------------------------------------------------------------------------
assert_clean_refusal() {   # $1=label $2=target $3=blocked relpath $4=adapter $5=expect-empty
    local label="$1" tgt="$2" rel="$3" tool="$4" empty="$5" out rc
    mkdir -p "$tgt/$(dirname "$rel")"
    printf 'not a directory\n' >"$tgt/$rel"
    out="$("$ROOT/install.sh" "$tool" --project-dir "$tgt" 2>&1)" && rc=0 || rc=$?
    [[ $rc -ne 0 ]] || fail "$label: a file at '$rel' must refuse the install"
    grep -q "^ERROR:" <<<"$out" \
        || fail "$label: must fail with the tool's own ERROR, not a raw shell \
message. Got: $(tail -2 <<<"$out")"
    grep -qF "$rel" <<<"$out" || fail "$label: the error must name '$rel'"
    if [[ "$empty" == "empty" ]]; then
        local n; n="$(find "$tgt" -type f -not -name "$(basename "$rel")" | wc -l | tr -d ' ')"
        [[ "$n" -eq 0 ]] || fail "$label: refusal must write NOTHING, found $n file(s)"
    fi
}

# Declared area -> refused before a single byte is written.
P1="$WORK/block-declared"; mkdir -p "$P1"
assert_clean_refusal "preflight/.claude" "$P1" ".claude" claude-code empty
P2="$WORK/block-hooks"; mkdir -p "$P2"
assert_clean_refusal "preflight/.github/hooks" "$P2" ".github/hooks" github-copilot empty
echo "  a file at a declared destination refuses before writing anything — OK"

# Undeclared depth -> still the tool's own error, naming the path.
P3="$WORK/block-deep"; mkdir -p "$P3"
assert_clean_refusal "ensure_dir/skill leaf" "$P3" ".claude/skills/adopt-existing" claude-code late
echo "  a file at a depth no list enumerates still fails cleanly and names it — OK"

# A read-only directory DEEPER than adapter_dirs() reaches. The list gets one
# level; a per-skill leaf or docs/graph/protocols/ is two or three, and those
# used to fall through to ensure_dir's late check — a clean error, but only
# after the kernel and most of the graph were already on disk. Preflight's whole
# promise is that a refusal writes nothing.
for deep in .claude/skills/library-wiki docs/graph/protocols; do
    P="$WORK/ro-$(basename "$deep")"; mkdir -p "$P/$deep"
    chmod 555 "$P/$deep"
    out="$("$ROOT/install.sh" claude-code --project-dir "$P" --copy --force 2>&1)" && rc=0 || rc=$?
    chmod -R u+w "$P" 2>/dev/null || true
    [[ $rc -ne 0 ]] || fail "a read-only '$deep' must refuse the install"
    grep -qF "$deep" <<<"$out" || fail "the refusal must name '$deep'"
    n="$(find "$P" -type f | wc -l | tr -d ' ')"
    [[ "$n" -eq 0 ]] || fail "a read-only '$deep' must write NOTHING, found $n file(s)"
done
echo "  a read-only directory at any depth refuses before writing anything — OK"

# A project's own instructions become WORK, not just a backup.
# The seed kernel owns the root instruction path, so a pre-existing one is
# replaced. It used to survive only as a `.bak`: on disk, out of force, and
# unrecorded. The content is now addressed to docs-librarian as a task, because
# deciding what somebody's rules meant is judgement, not a shell script's job.
MIG="$WORK/adopted"; mkdir -p "$MIG"
printf '# Our team rules\n\nAlways rebase, never merge.\n' >"$MIG/AGENTS.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$MIG" 2>&1)" \
    || fail "install over a project with its own AGENTS.md failed"
NOTE="$MIG/docs/graph/plans/adopted-instructions.md"
[[ -f "$NOTE" ]] || fail "a replaced instruction file must be recorded as migration work"
grep -q "docs-librarian" "$NOTE" || fail "the migration note must name its owner"
grep -qF "adopted-instructions.md" <<<"$out" \
    || fail "the install must say where the migration work was recorded"
entry="$(grep -c '^- \[ \]' "$NOTE" | tr -d ' ')"
[[ "$entry" -eq 1 ]] || fail "expected exactly one migration entry, got $entry"
grep -rqF "Always rebase" "$MIG"/*.bak-* \
    || fail "the original instructions must remain recoverable"

# A second install must not file the same backup twice.
"$ROOT/install.sh" opencode --project-dir "$MIG" >/dev/null 2>&1
entry="$(grep -c '^- \[ \]' "$NOTE" | tr -d ' ')"
[[ "$entry" -eq 1 ]] || fail "a re-install duplicated the migration entry ($entry)"

# ...and a project that never had its own instructions gets no note at all,
# or the notice is noise on every first install.
FRESH="$WORK/adopted-fresh"; mkdir -p "$FRESH"
"$ROOT/install.sh" claude-code --project-dir "$FRESH" >/dev/null 2>&1
[[ ! -f "$FRESH/docs/graph/plans/adopted-instructions.md" ]] \
    || fail "a fresh plant must not get a migration note"
echo "  a replaced instruction file becomes recorded work for docs-librarian — OK"

# And every directory adapter_dirs DOES declare must really be one the adapter
# creates, or the preflight is refusing over paths that do not matter.
for tool in claude-code opencode codex github-copilot prime-agent; do
    D="$WORK/dirs-$tool"; mkdir -p "$D"
    "$ROOT/install.sh" "$tool" --project-dir "$D" >/dev/null 2>&1 \
        || fail "adapter_dirs: baseline install of $tool failed"
    while IFS= read -r dec; do
        [[ -z "$dec" ]] && continue
        case "$dec" in docs|docs/graph|.cypress) continue ;; esac
        [[ -d "$D/$dec" ]] || fail "adapter_dirs($tool) declares '$dec', which \
installing $tool does not create — the preflight would refuse over a path the \
adapter never touches"
    done < <(bash -c 'source /dev/stdin <<<"$(sed -n "/^adapter_dirs()/,/^}/p" "$0")"; adapter_dirs "$1"' \
             "$ROOT/install.sh" "$tool" 2>/dev/null)
done
echo "  every directory adapter_dirs declares is one the adapter really creates — OK"

# `--check` must tell a BROKEN generator from a DRIFTED view, and show which.
#
# This had no regression, and the branch that does the telling was unreachable:
# on the left of `||` bash disables errexit inside the function, so a failing
# generator ran on to `die`, and `die` exits the whole installer before
# `|| gen_rc=$?` can run. The log went to a file under $STAGE, which the EXIT
# trap deleted. Net effect at HEAD, with no seed mutation: `--check` exited 1
# having printed nothing at all — strictly worse than the "views are STALE" it
# replaced. The trigger needs no special privilege: one plant-authored node that
# is not UTF-8.
CHK="$WORK/check-broken"; mkdir -p "$CHK"
"$ROOT/install.sh" github-copilot --project-dir "$CHK" >/dev/null 2>&1 \
    || fail "--check setup install failed"
python3 -c "
open('$CHK/docs/graph/agents/50-plant-expert.md','wb').write(
  '---\ndescription: caf\xe9 domain expert\ntools: [Read]\n---\nbody\n'.encode('latin-1'))"

chk_out="$("$ROOT/install.sh" github-copilot --check --project-dir "$CHK" 2>&1)" && chk_rc=0 || chk_rc=$?
[[ $chk_rc -ne 0 ]] || fail "--check returned 0 over a generator that cannot run"
[[ -n "$chk_out" ]] || fail "--check failed with EMPTY output. A drift gate that \
exits non-zero and says nothing is indistinguishable from one that found drift, \
and the operator has nothing to act on."
grep -q "could not regenerate" <<<"$chk_out" \
    || fail "--check did not say the generation FAILED (it must not be reported \
as 'STALE' — those are different findings): $chk_out"
grep -qi "UnicodeDecodeError" <<<"$chk_out" \
    || fail "--check named the failure but swallowed its cause; the generator's \
own error has to reach the operator: $chk_out"

# ...and a plant that is merely out of date is still reported as STALE, or the
# assertion above is satisfied by a tool that calls everything a crash.
CHK2="$WORK/check-stale"; mkdir -p "$CHK2"
"$ROOT/install.sh" github-copilot --project-dir "$CHK2" >/dev/null 2>&1 \
    || fail "--check stale-case setup failed"
printf '\n<!-- drifted -->\n' >> "$CHK2/.github/copilot-instructions.md"
stale_out="$("$ROOT/install.sh" github-copilot --check --project-dir "$CHK2" 2>&1)" || true
grep -q "STALE" <<<"$stale_out" \
    || fail "a drifted view is no longer reported as STALE: $stale_out"
grep -q "could not regenerate" <<<"$stale_out" \
    && fail "a drifted view was reported as a broken generator: $stale_out"
echo "  --check tells a broken generator from a drifted view, and shows the cause — OK"

# The Copilot/Claude-Code hook guard holds in BOTH install orders.
#
# VS Code reads `.claude/settings.json` and `.github/hooks/*.json`, so a plant
# carrying both fires every hook twice. `install_github_copilot` skipped its
# hooks when settings.json was already there — and that was the only direction
# guarded. Adopt Copilot first and add Claude Code later, which is the ordinary
# way a project arrives here, and both sets ended up wired.
for order in "github-copilot claude-code" "claude-code github-copilot"; do
    H="$WORK/hookorder-$(echo "$order" | tr ' ' '-')"; mkdir -p "$H"
    for tool in $order; do
        "$ROOT/install.sh" "$tool" --project-dir "$H" >/dev/null 2>&1 \
            || fail "hook-order setup: install $tool failed"
    done
    live=0
    for f in route-hook.py route.json status-hook.py status.json; do
        [[ -e "$H/.github/hooks/$f" ]] && live=$((live + 1))
    done
    [[ -f "$H/.claude/settings.json" ]] \
        || fail "hook-order [$order]: .claude/settings.json is missing"
    [[ $live -eq 0 ]] || fail "hook-order [$order]: $live .github/hooks/ file(s) \
are still wired alongside .claude/settings.json — VS Code reads both, so every \
hook fires twice. The guard only held in one direction."
done

# ...and retiring them is recoverable and announced, not a silent delete.
HR="$WORK/hookorder-retire"; mkdir -p "$HR"
"$ROOT/install.sh" github-copilot --project-dir "$HR" >/dev/null 2>&1 || fail "retire setup failed"
printf '\n# PLANT-EDIT\n' >> "$HR/.github/hooks/route-hook.py"
retire_log="$("$ROOT/install.sh" claude-code --project-dir "$HR" 2>&1)" \
    || fail "retire install failed"
grep -q "retired .github/hooks/route-hook.py" <<<"$retire_log" \
    || fail "the retirement was not announced: a plant loses a file it may have \
edited and is told nothing"
found=0
for bak in "$HR/.github/hooks/route-hook.py".bak-*; do
    [[ -e "$bak" ]] || continue
    grep -q "PLANT-EDIT" "$bak" 2>/dev/null && { found=1; break; }
done
[[ $found -eq 1 ]] || fail "a retired hook carrying a plant edit is not recoverable"
echo "  the Copilot/Claude-Code hook guard holds in both install orders — OK"

# A plant whose RECORD is missing is still a plant.
#
# `PRIOR_INSTALL` was snapshotted from one file, and three mechanisms hung off
# it: the D2 re-creation notice, `sweep_orphaned_instruction_backups`, and the
# recorded corpus/jurisdiction reconciliation. Delete `.cypress/seed.json` —
# which the seed's OWN .gitignore causes for any plant that commits its graph
# and is then freshly cloned — and all three went quiet: nodes were silently
# restored with no notice, and a backup of the team's own instructions was never
# filed as work.
NOSTAMP="$WORK/nostamp"; mkdir -p "$NOSTAMP"
"$ROOT/install.sh" claude-code --project-dir "$NOSTAMP" >/dev/null 2>&1 \
    || fail "no-stamp setup install failed"
rm -f "$NOSTAMP/.cypress/seed.json"
rm -f "$NOSTAMP/docs/graph/protocols/grill.md"
nostamp_log="$("$ROOT/install.sh" claude-code --project-dir "$NOSTAMP" 2>&1)" \
    || fail "install over a stamp-less plant failed"
grep -qi "RE-CREATED" <<<"$nostamp_log" \
    || fail "a node was restored into an existing plant with no notice, because \
the plant's RECORD was missing. Absence of the record is not absence of the plant."
grep -q "no .cypress/seed.json" <<<"$nostamp_log" \
    || fail "the missing record was not announced; the owner decisions it held \
cannot be recovered from disk and the owner has to be told"
[[ -f "$NOSTAMP/docs/graph/protocols/grill.md" ]] \
    || fail "the missing node was not restored"

# ...and a genuinely fresh target is still quiet, or the assertion above is
# satisfied by an installer that shouts on every first install.
FRESH="$WORK/freshquiet"; mkdir -p "$FRESH"
fresh_log="$("$ROOT/install.sh" claude-code --project-dir "$FRESH" 2>&1)" \
    || fail "fresh install failed"
grep -qi "RE-CREATED" <<<"$fresh_log" \
    && fail "a FIRST install announced re-created nodes: $fresh_log"
grep -q "no .cypress/seed.json" <<<"$fresh_log" \
    && fail "a first install warned about a missing record it was about to write"
echo "  a plant whose .cypress/seed.json is missing is still treated as a plant — OK"

echo "install-adoption: OK — kernel adoption, plant-owned survival, D1 preflight, D2 announcement, idempotence, --check diagnostics, hook-order guard, stamp-less adoption"
