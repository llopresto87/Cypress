#!/usr/bin/env bash
# Kernel placement contract: install.sh's place_kernel collapses CLAUDE.md and
# AGENTS.md to ONE real body plus a project-local relative symlink, so a
# single plant runs Claude Code and Prime Agent off byte-identical
# instructions. Three fixes here were pinned once by a manual probe and never
# by a permanent test:
#   - --symlink used to place the kernel as a FROZEN COPY while every sibling
#     file was correctly linked (K3) — a seed change never reached the plant
#     though the flag promised it would.
#   - --copy was never asserted to actually ISOLATE the plant from a live seed
#     edit (K2) — the flag's whole point, unverified.
#   - installing claude-code then prime-agent (or the reverse) used to
#     ping-pong the kernel file into fresh .bak churn on every re-run (K5).
# Losing any of these regresses silently: install still exits 0, the kernel
# file still exists, and only a byte-level or live-update check would notice.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"

# The real seed's kernel must be byte-identical before and after this suite:
# every case below writes sentinels into $SEEDCOPY, and a path bug that wrote
# into $ROOT instead would corrupt the kernel of the repository under test.
#
# This runs from the EXIT trap, not inline. An inline check placed after the
# last *known* installer call is only as good as the reading of what comes
# after it: an earlier version sat at line 107 while K5 and K6 both invoked
# $ROOT/install.sh below it, so a place_kernel() that appended to the seed's
# own kernel during K6 left the suite green and the repo corrupted. The trap
# fires wherever the script ends, including on an early `fail`.
KERNEL_BEFORE="$(cksum < "$ROOT/core/AGENTS.md")"
_cleanup() {
    local rc=$?
    rm -rf "$WORK"
    if [[ "$(cksum < "$ROOT/core/AGENTS.md")" != "$KERNEL_BEFORE" ]]; then
        echo "FAIL: the real seed's core/AGENTS.md changed during this run —" \
             "this test must only ever touch SEEDCOPY" >&2
        exit 1
    fi
    exit $rc
}
trap _cleanup EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }


# assert_shared_kernel DIR LABEL — the collapsed-kernel invariant common to
# every case below: exactly one of CLAUDE.md/AGENTS.md is a real file, the
# other a project-local relative symlink (bare basename, never an absolute
# path into the seed), and both resolve to identical bytes.
assert_shared_kernel() {
    local d="$1" label="$2" links=0
    [[ -e "$d/CLAUDE.md" ]] || fail "$label: CLAUDE.md missing"
    [[ -e "$d/AGENTS.md" ]] || fail "$label: AGENTS.md missing"
    [[ -L "$d/CLAUDE.md" ]] && links=$((links + 1))
    [[ -L "$d/AGENTS.md" ]] && links=$((links + 1))
    [[ "$links" -eq 1 ]] \
        || fail "$label: expected exactly one of CLAUDE.md/AGENTS.md to be a symlink (single source of truth), got $links"
    local k tgt
    for k in CLAUDE.md AGENTS.md; do
        if [[ -L "$d/$k" ]]; then
            tgt="$(readlink "$d/$k")"
            [[ "$tgt" == "CLAUDE.md" || "$tgt" == "AGENTS.md" ]] \
                || fail "$label: $k symlink target '$tgt' is not a bare project-local sibling basename (must never be an absolute seed path)"
            [[ "$tgt" != /* ]] || fail "$label: $k symlink target '$tgt' is absolute"
        fi
    done
    diff -q "$d/CLAUDE.md" "$d/AGENTS.md" >/dev/null \
        || fail "$label: CLAUDE.md and AGENTS.md content differs — the kernel would drift"
}

# --- K1/K4 -----------------------------------------------------------------
# Asserts SPEC-0001 ONE_KERNEL_BODY (K1/K4/K5), SPEC-0001 COPY_MODE_ISOLATES
# (K2) and SPEC-0001 SYMLINK_MODE_IS_UNIFORM (K3).
# After a plain claude-code install, the collapsed-kernel invariant holds.
D="$WORK/k1"; mkdir -p "$D"
"$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null 2>&1 \
    || fail "K1/K4: claude-code install did not succeed"
assert_shared_kernel "$D" "K1/K4"
echo "K1/K4: one real kernel body + one project-local symlink, identical content — OK"

# --- K2 ----------------------------------------------------------------
# Copy mode must ISOLATE the plant from the seed. Simulate a seed kernel
# change WITHOUT touching the real seed: work from a full copy of the seed
# (SEEDCOPY), install from there, then edit SEEDCOPY's kernel and confirm the
# already-installed plant does not see it.
SEEDCOPY="$WORK/seedcopy-k2"
# `cp -R`, not `cp -a`: -a is GNU-spelled and BSD/macOS cp has only
# recently grown it. -R copies the tree and preserves symlinks as symlinks,
# which is all this copy needs (the seed kernel is edited in the COPY so the
# real one is never touched).
cp -R "$ROOT" "$SEEDCOPY"
T="$WORK/k2-plant"; mkdir -p "$T"
"$SEEDCOPY/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "K2: install from SEEDCOPY did not succeed"
SENTINEL_K2="CYPRESS-KERNEL-SENTINEL-K2-$$"
printf '\n%s\n' "$SENTINEL_K2" >> "$SEEDCOPY/core/AGENTS.md"
grep -q "$SENTINEL_K2" "$T/CLAUDE.md" 2>/dev/null \
    && fail "K2 VIOLATED — copy mode did not isolate the plant: a seed kernel edit after install reached the plant"
grep -q "$SENTINEL_K2" "$T/AGENTS.md" 2>/dev/null \
    && fail "K2 VIOLATED — copy mode did not isolate the plant (AGENTS.md side)"
echo "K2: --copy isolates the plant from a later seed kernel edit — OK"

# --- K3 ----------------------------------------------------------------
# Symlink mode must be LIVE. This is the exact bug the fix closed: --symlink
# used to place the kernel as a frozen copy while every sibling was correctly
# linked. Install from SEEDCOPY with --symlink and confirm a later seed edit
# is visible WITHOUT reinstalling.
T2="$WORK/k3-plant"; mkdir -p "$T2"
"$SEEDCOPY/install.sh" claude-code --project-dir "$T2" --symlink >/dev/null 2>&1 \
    || fail "K3: install from SEEDCOPY --symlink did not succeed"
[[ -L "$T2/CLAUDE.md" || -L "$T2/AGENTS.md" ]] \
    || fail "K3 VIOLATED — neither kernel file is a symlink under --symlink mode"
SENTINEL_K3="CYPRESS-KERNEL-SENTINEL-K3-$$"
printf '\n%s\n' "$SENTINEL_K3" >> "$SEEDCOPY/core/AGENTS.md"
grep -q "$SENTINEL_K3" "$T2/CLAUDE.md" \
    || fail "K3 VIOLATED — --symlink kernel is frozen: a seed edit after install did not reach the plant without reinstalling"
grep -q "$SENTINEL_K3" "$T2/AGENTS.md" \
    || fail "K3 VIOLATED — --symlink kernel is frozen (AGENTS.md side)"
echo "K3: --symlink kernel is live — a seed edit reaches the plant with no reinstall — OK"

# --- K5 ----------------------------------------------------------------
# Installation ORDER must not change kernel semantics — the ping-pong
# regression where claude-code and prime-agent each called place_kernel and
# churned fresh .bak siblings off each other on every re-run.
for order in "claude-code prime-agent" "prime-agent claude-code"; do
    D="$WORK/k5-$(tr ' ' '-' <<<"$order")"; mkdir -p "$D"
    "$ROOT/install.sh" $order --project-dir "$D" --copy --force >/dev/null 2>&1 \
        || fail "K5 ($order): install did not succeed"
    assert_shared_kernel "$D" "K5 ($order)"
    n="$(find "$D" -maxdepth 1 -name '*.bak-*' | wc -l | tr -d ' ')"
    [[ "$n" -eq 0 ]] \
        || fail "K5 ($order): $n .bak file(s) churned at the project root from the second adapter's kernel placement (the ping-pong regression)"
done
# Both orders must converge on identical kernel content.
diff -q "$WORK/k5-claude-code-prime-agent/CLAUDE.md" \
        "$WORK/k5-prime-agent-claude-code/CLAUDE.md" >/dev/null \
    || fail "K5: the two install orders produced different kernel content"
echo "K5: install order (claude-code<->prime-agent) does not change kernel semantics, no .bak churn — OK"

# --- K6 ----------------------------------------------------------------
# The placed kernel is byte-identical to the seed's own core/AGENTS.md — the
# bootstrap kernel is not transformed or truncated on its way into a plant.
D="$WORK/k6"; mkdir -p "$D"
"$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null 2>&1 \
    || fail "K6: install did not succeed"
cmp -s "$ROOT/core/AGENTS.md" "$D/CLAUDE.md" \
    || fail "K6 VIOLATED — the placed kernel is not byte-identical to core/AGENTS.md"
echo "K6: placed kernel is byte-identical to core/AGENTS.md — OK"

# --- K7: an earlier seed kernel is not a migration (7.32.0) -------------------
# Asserts SPEC-0001 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION and SPEC-0001
# SEED_HISTORY_UNAVAILABLE. A target whose kernel is byte-identical to
# core/AGENTS.md at an earlier commit of the seed holds no instruction of the
# plant's own, so replacing it is a fast-forward: one backup, no row in
# adopted-instructions.md, no OVERWRITTEN line. A kernel with one plant line
# added is still filed (guard). A seed with no Git history falls back to the
# comparison with the current kernel only, and says so in one line.
#
# The seed under test is a temp clone of the real seed (`git clone --local
# --no-hardlinks`: a hard link fails when the temp directory is on another
# device),
# with the real seed's working tree laid over it, so the installer run is the
# one on disk and its history is the real seed's. A shallow checkout (CI) has
# no earlier kernel in its history; the clone then gains one commit holding an
# earlier body and one restoring the current body, so the history the
# installer walks still holds an earlier kernel. One collecting block: each
# case prints `FAIL <label>: <why>` and the block exits 1 at its end, so one
# red case never hides the next.
K7_FAILED=0
k7_case() {  # $1 label, $2 case function, $3 what an OK run shows
    local why
    if why="$("$2" 2>&1)"; then
        echo "$1: $3 — OK"
    else
        echo "FAIL $1: $why" >&2
        K7_FAILED=1
    fi
}
# The rows of the plant's adopted-instructions.md that name a backup, or
# nothing when the file or the row is absent.
k7_rows_for() {  # $1 plant, $2 backup basename
    local note="$1/docs/graph/plans/adopted-instructions.md"
    [[ -f "$note" ]] || return 0
    grep -F -- "$2" "$note" || true
}

K7_SEED="$WORK/k7-seed"
K7_PRIOR="$WORK/k7-prior-kernel.md"
k7_fixture() {
    git clone --local --no-hardlinks --quiet "$ROOT" "$K7_SEED" >/dev/null 2>&1 \
        || { echo "fixture: git clone --local of the seed failed"; return 1; }
    (cd "$ROOT" && tar cf - --exclude=./.git .) | (cd "$K7_SEED" && tar xf -) \
        || { echo "fixture: laying the seed's working tree over the clone failed"; return 1; }
    local rev
    for rev in $(git -C "$K7_SEED" log --format=%H -- core/AGENTS.md); do
        git -C "$K7_SEED" show "$rev:core/AGENTS.md" > "$K7_PRIOR" 2>/dev/null || continue
        cmp -s "$K7_PRIOR" "$K7_SEED/core/AGENTS.md" || return 0
    done
    # Shallow history: record an earlier body, then the current one, in the clone.
    sed '$d' "$K7_SEED/core/AGENTS.md" > "$K7_PRIOR"
    cmp -s "$K7_PRIOR" "$K7_SEED/core/AGENTS.md" \
        && { echo "fixture: could not derive an earlier kernel body"; return 1; }
    local cur="$WORK/k7-current-kernel.md"
    cp "$K7_SEED/core/AGENTS.md" "$cur"
    cp "$K7_PRIOR" "$K7_SEED/core/AGENTS.md"
    git -C "$K7_SEED" -c user.name=k7 -c user.email=k7@example.invalid \
        commit --quiet --no-verify -m "k7: earlier kernel" -- core/AGENTS.md >/dev/null 2>&1 \
        || { echo "fixture: could not commit an earlier kernel in the clone"; return 1; }
    cp "$cur" "$K7_SEED/core/AGENTS.md"
    git -C "$K7_SEED" -c user.name=k7 -c user.email=k7@example.invalid \
        commit --quiet --no-verify -m "k7: current kernel" -- core/AGENTS.md >/dev/null 2>&1 \
        || { echo "fixture: could not commit the current kernel in the clone"; return 1; }
}

case_k7_prior_kernel_fast_forwards() {
    # K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION: the first run, then a second run.
    local t="$WORK/k7-prior" out rc baks
    mkdir -p "$t"
    cp "$K7_PRIOR" "$t/CLAUDE.md"
    out="$("$K7_SEED/install.sh" claude-code --project-dir "$t" --copy 2>&1)"; rc=$?
    [[ $rc -eq 0 ]] || { echo "install over an earlier seed kernel exited $rc: $(tail -3 <<<"$out")"; return 1; }
    baks="$(find "$t" -maxdepth 1 -name 'CLAUDE.md.bak-*' | wc -l | tr -d ' ')"
    [[ "$baks" -eq 1 ]] || { echo "expected exactly one CLAUDE.md.bak-*, found $baks"; return 1; }
    local bak; bak="$(basename "$(find "$t" -maxdepth 1 -name 'CLAUDE.md.bak-*')")"
    [[ -z "$(k7_rows_for "$t" "$bak")" ]] \
        || { echo "adopted-instructions.md gained a row for $bak, whose body is an earlier seed kernel: $(k7_rows_for "$t" "$bak")"; return 1; }
    grep -q OVERWRITTEN <<<"$out" \
        && { echo "the install printed an OVERWRITTEN line for an earlier seed kernel: $(grep OVERWRITTEN <<<"$out")"; return 1; }
    grep -qi "earlier seed kernel" <<<"$out" \
        || { echo "the log does not name the replacement as a fast-forward from an earlier seed kernel"; return 1; }
    cmp -s "$t/CLAUDE.md" "$K7_SEED/core/AGENTS.md" \
        || { echo "the kernel was not brought to the current seed kernel"; return 1; }
    cmp -s "$t/$bak" "$K7_PRIOR" || { echo "the backup does not hold the earlier kernel"; return 1; }
    out="$("$K7_SEED/install.sh" claude-code --project-dir "$t" --copy 2>&1)"; rc=$?
    [[ $rc -eq 0 ]] || { echo "the second run exited $rc: $(tail -3 <<<"$out")"; return 1; }
    [[ -z "$(k7_rows_for "$t" "$bak")" ]] \
        || { echo "the second run filed a row for $bak: $(k7_rows_for "$t" "$bak")"; return 1; }
    return 0
}

case_k7_sweep_skips_prior_kernel_backup() {
    # K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION: a later run's orphan sweep.
    local t="$WORK/k7-sweep" out rc bak="CLAUDE.md.bak-20260101-000000"
    mkdir -p "$t"
    "$K7_SEED/install.sh" claude-code --project-dir "$t" --copy >/dev/null 2>&1 \
        || { echo "fixture: the first install failed"; return 1; }
    cp "$K7_PRIOR" "$t/$bak"
    out="$("$K7_SEED/install.sh" claude-code --project-dir "$t" --copy 2>&1)"; rc=$?
    [[ $rc -eq 0 ]] || { echo "the re-run exited $rc: $(tail -3 <<<"$out")"; return 1; }
    [[ -z "$(k7_rows_for "$t" "$bak")" ]] \
        || { echo "the orphan sweep filed a row for $bak, whose body is an earlier seed kernel: $(k7_rows_for "$t" "$bak")"; return 1; }
    return 0
}

case_k7_plant_line_is_still_filed() {
    # K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, guard: a body that matches no
    # seed kernel is filed exactly as today.
    local t="$WORK/k7-plant-line" out rc bak
    mkdir -p "$t"
    { cat "$K7_PRIOR"; printf '%s\n' "- K7 plant rule: run the linter before every commit."; } > "$t/CLAUDE.md"
    out="$("$K7_SEED/install.sh" claude-code --project-dir "$t" --copy 2>&1)"; rc=$?
    [[ $rc -eq 0 ]] || { echo "install exited $rc: $(tail -3 <<<"$out")"; return 1; }
    bak="$(basename "$(find "$t" -maxdepth 1 -name 'CLAUDE.md.bak-*' | head -1)")"
    [[ "$bak" == CLAUDE.md.bak-* ]] || { echo "no CLAUDE.md.bak-* was left"; return 1; }
    [[ -n "$(k7_rows_for "$t" "$bak")" ]] \
        || { echo "a kernel carrying a plant line was not filed in adopted-instructions.md"; return 1; }
    grep -q OVERWRITTEN <<<"$out" \
        || { echo "a kernel carrying a plant line was replaced with no OVERWRITTEN line"; return 1; }
    return 0
}

case_k7_no_history_falls_back() {
    # K7 SEED_HISTORY_UNAVAILABLE: a seed copy with no .git files the row as
    # before 7.32.0, and the log says so in one line.
    local seed="$WORK/k7-nogit-seed" t="$WORK/k7-nogit" out rc bak n
    mkdir -p "$seed" "$t"
    (cd "$ROOT" && tar cf - --exclude=./.git .) | (cd "$seed" && tar xf -) \
        || { echo "fixture: copying the seed without .git failed"; return 1; }
    [[ ! -e "$seed/.git" ]] || { echo "fixture: the seed copy still has .git"; return 1; }
    cp "$K7_PRIOR" "$t/CLAUDE.md"
    out="$("$seed/install.sh" claude-code --project-dir "$t" --copy 2>&1)"; rc=$?
    [[ $rc -eq 0 ]] || { echo "install from a seed with no history exited $rc: $(tail -3 <<<"$out")"; return 1; }
    bak="$(basename "$(find "$t" -maxdepth 1 -name 'CLAUDE.md.bak-*' | head -1)")"
    [[ -n "$(k7_rows_for "$t" "$bak")" ]] \
        || { echo "with no seed history the earlier kernel was not filed for migration"; return 1; }
    n="$(grep -ci 'history' <<<"$out" || true)"
    [[ "$n" -eq 1 ]] \
        || { echo "expected one log line saying the seed history is unavailable (a line naming 'history'), found $n"; return 1; }
    return 0
}

if why="$(k7_fixture 2>&1)"; then
    k7_case "K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION" case_k7_prior_kernel_fast_forwards \
        "an earlier seed kernel is replaced with one backup, no row, no OVERWRITTEN line, and a re-run files none"
    k7_case "K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION (sweep)" case_k7_sweep_skips_prior_kernel_backup \
        "the orphan sweep files no row for a backup holding an earlier seed kernel"
    k7_case "K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION (guard)" case_k7_plant_line_is_still_filed \
        "a kernel with one plant line added is filed and announced as before"
    k7_case "K7 SEED_HISTORY_UNAVAILABLE" case_k7_no_history_falls_back \
        "a seed with no Git history files the row and says so in one line"
else
    echo "FAIL K7 fixture: $why" >&2
    K7_FAILED=1
fi
[[ $K7_FAILED -eq 0 ]] || fail "K7: one or more cases above failed"

echo "install-kernel-modes: OK — copy isolates, symlink is live, order is commutative, placement is byte-identical"
