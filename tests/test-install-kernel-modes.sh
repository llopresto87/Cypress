#!/usr/bin/env bash
# Kernel placement: install.sh's place_kernel leaves ONE real kernel body plus a
# project-local relative symlink, so Claude Code and Prime Agent load identical
# instructions. K2 pins --copy isolation, K3 pins a live --symlink kernel, K5
# pins install order (no .bak ping-pong), K7 pins earlier-kernel upgrades.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }
. "$ROOT/tests/helpers/lintcase.sh"

# assert_shared_kernel DIR LABEL: exactly one of CLAUDE.md/AGENTS.md is a
# symlink, its target a bare sibling basename, and both resolve to equal bytes.
assert_shared_kernel() {
    local d="$1" label="$2" links=0 k tgt
    [[ -e "$d/CLAUDE.md" && -e "$d/AGENTS.md" ]] || fail "$label: CLAUDE.md or AGENTS.md missing"
    [[ -L "$d/CLAUDE.md" ]] && links=$((links + 1))
    [[ -L "$d/AGENTS.md" ]] && links=$((links + 1))
    [[ "$links" -eq 1 ]] || fail "$label: expected exactly one kernel symlink, got $links"
    for k in CLAUDE.md AGENTS.md; do
        [[ -L "$d/$k" ]] || continue
        tgt="$(readlink "$d/$k")"
        [[ "$tgt" == "CLAUDE.md" || "$tgt" == "AGENTS.md" ]] \
            || fail "$label: $k symlink target '$tgt' is not a project-local sibling basename"
    done
    diff -q "$d/CLAUDE.md" "$d/AGENTS.md" >/dev/null \
        || fail "$label: CLAUDE.md and AGENTS.md content differs"
}

# --- K1/K4 (+K6) ------------------------------------------------------------
# Asserts SPEC-0001 ONE_KERNEL_BODY (K1/K4/K5), SPEC-0001 COPY_MODE_ISOLATES
# (K2) and SPEC-0001 SYMLINK_MODE_IS_UNIFORM (K3).
D="$WORK/k1"; mkdir -p "$D"
"$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null 2>&1 \
    || fail "K1/K4: claude-code install did not succeed"
assert_shared_kernel "$D" "K1/K4"
# K6: the placed kernel is byte-identical to the seed's core/AGENTS.md.
cmp -s "$ROOT/core/AGENTS.md" "$D/CLAUDE.md" \
    || fail "K6 VIOLATED — the placed kernel is not byte-identical to core/AGENTS.md"
echo "K1/K4/K6: one real kernel body + one project-local symlink, byte-identical to core/AGENTS.md — OK"

# --- K2 ----------------------------------------------------------------
# --copy isolates the plant: install from a seed copy, edit the copy's kernel,
# and the plant must not see it. The real seed is never edited.
SEEDCOPY="$WORK/seedcopy-k2"; mkdir -p "$SEEDCOPY"
(cd "$ROOT" && tar cf - --exclude=./.git .) | (cd "$SEEDCOPY" && tar xf -) \
    || fail "K2: copying the seed without .git failed"
T="$WORK/k2-plant"; mkdir -p "$T"
"$SEEDCOPY/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
    || fail "K2: install from SEEDCOPY did not succeed"
SENTINEL_K2="CYPRESS-KERNEL-SENTINEL-K2-$$"
printf '\n%s\n' "$SENTINEL_K2" >> "$SEEDCOPY/core/AGENTS.md"
grep -q "$SENTINEL_K2" "$T/CLAUDE.md" "$T/AGENTS.md" 2>/dev/null \
    && fail "K2 VIOLATED — copy mode did not isolate the plant: a seed kernel edit after install reached the plant"
echo "K2: --copy isolates the plant from a later seed kernel edit — OK"

# --- K3 ----------------------------------------------------------------
# --symlink kernel is live: a later seed edit reaches the plant with no reinstall.
T2="$WORK/k3-plant"; mkdir -p "$T2"
"$SEEDCOPY/install.sh" claude-code --project-dir "$T2" --symlink >/dev/null 2>&1 \
    || fail "K3: install from SEEDCOPY --symlink did not succeed"
[[ -L "$T2/CLAUDE.md" || -L "$T2/AGENTS.md" ]] \
    || fail "K3 VIOLATED — neither kernel file is a symlink under --symlink mode"
SENTINEL_K3="CYPRESS-KERNEL-SENTINEL-K3-$$"
printf '\n%s\n' "$SENTINEL_K3" >> "$SEEDCOPY/core/AGENTS.md"
grep -q "$SENTINEL_K3" "$T2/CLAUDE.md" \
    || fail "K3 VIOLATED — --symlink kernel is frozen: a seed edit after install did not reach the plant"
grep -q "$SENTINEL_K3" "$T2/AGENTS.md" \
    || fail "K3 VIOLATED — --symlink kernel is frozen (AGENTS.md side)"
echo "K3: --symlink kernel is live — a seed edit reaches the plant with no reinstall — OK"

# --- K5 ----------------------------------------------------------------
# Install order does not change the kernel and churns no .bak at the root.
for order in "claude-code prime-agent" "prime-agent claude-code"; do
    D="$WORK/k5-$(tr ' ' '-' <<<"$order")"; mkdir -p "$D"
    "$ROOT/install.sh" $order --project-dir "$D" --copy --force >/dev/null 2>&1 \
        || fail "K5 ($order): install did not succeed"
    assert_shared_kernel "$D" "K5 ($order)"
    n="$(find "$D" -maxdepth 1 -name '*.bak-*' | wc -l | tr -d ' ')"
    [[ "$n" -eq 0 ]] || fail "K5 ($order): $n .bak file(s) churned at the project root"
done
diff -q "$WORK/k5-claude-code-prime-agent/CLAUDE.md" \
        "$WORK/k5-prime-agent-claude-code/CLAUDE.md" >/dev/null \
    || fail "K5: the two install orders produced different kernel content"
echo "K5: install order (claude-code<->prime-agent) does not change kernel semantics, no .bak churn — OK"

# --- K7: an earlier seed kernel is not a migration ---------------------------
# Asserts SPEC-0001 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION and SPEC-0001
# SEED_HISTORY_UNAVAILABLE. The seed under test is a `git clone --local
# --no-hardlinks` of the real seed with its working tree laid over it; a shallow
# clone gains two commits (an earlier body, then the current one). Each case
# prints its own result.
# Rows of the plant's adopted-instructions.md naming a backup, or nothing.
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
    # K7 SEED_HISTORY_UNAVAILABLE: with no .git the row is filed, and one log
    # line says so.
    # SEEDCOPY (K2) is the seed without .git; its kernel carries K2/K3 sentinels,
    # so K7_PRIOR is still an earlier body.
    local seed="$SEEDCOPY" t="$WORK/k7-nogit" out rc bak n
    mkdir -p "$t"
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
    collect_case "K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION" case_k7_prior_kernel_fast_forwards \
        "an earlier seed kernel is replaced with one backup, no row, no OVERWRITTEN line, and a re-run files none"
    collect_case "K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION (sweep)" case_k7_sweep_skips_prior_kernel_backup \
        "the orphan sweep files no row for a backup holding an earlier seed kernel"
    collect_case "K7 PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION (guard)" case_k7_plant_line_is_still_filed \
        "a kernel with one plant line added is filed and announced as before"
    collect_case "K7 SEED_HISTORY_UNAVAILABLE" case_k7_no_history_falls_back \
        "a seed with no Git history files the row and says so in one line"
else
    echo "FAIL K7 fixture: $why" >&2
    CASE_FAILED=1
fi
[[ $CASE_FAILED -eq 0 ]] || fail "K7: one or more cases above failed"

echo "install-kernel-modes: OK — copy isolates, symlink is live, order is commutative, placement is byte-identical"
