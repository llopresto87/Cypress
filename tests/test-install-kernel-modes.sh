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

echo "install-kernel-modes: OK — copy isolates, symlink is live, order is commutative, placement is byte-identical"
