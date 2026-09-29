#!/usr/bin/env bash
# Destination placement: every byte install.sh puts into a target goes through
# one canonical writer, so every destination is recoverable, symlink-safe,
# idempotent and auditable. The destination set is DISCOVERED from a real
# install, so a destination added later is held to the same contract.
#   M2  a destination symlink never authorizes a write to its referent
#   M3  identical reruns make no backup churn
#   M7  every written file is recoverable from a timestamped sibling
#   M9  under --symlink every placed file is a link or a recorded exception
#   M10 no write escapes PROJECT_DIR
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Every host by name (ADR-0009): `all` names only the maintained hosts. Unquoted
# at each call on purpose, so it splits into five tool arguments.
EVERY_HOST="claude-code opencode codex github-copilot prime-agent"
WORK="$(mktemp -d)"
trap 'chmod -R u+w "$WORK" 2>/dev/null; rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# The installer's own derived state: the recorded M7 exception (never
# byte-identical, no recovery value). Still atomic and symlink-safe.
is_installer_state() {
    [[ "$1" == ".cypress/seed.json" || "$1" == ".cypress/recreated-nodes.txt" ]]
}

# Add-if-missing destinations the plant then owns: a plant edit survives a
# re-run, and they are copies even under --symlink. The M9 exception list.
is_plant_owned() {
    local rel="$1"
    case "$rel" in
        docs/graph/_schema.md|docs/graph/index.md) return 0 ;;
        docs/graph/graph-lint.py|docs/graph/spec-lint.py|docs/graph/grill-lint.py) return 0 ;;
    esac
    [[ -e "$ROOT/templates/docs/${rel#docs/graph/}" ]] && return 0
    return 1
}

# Content generated per target: no seed original, so a real file under --symlink.
is_generated() {
    case "$1" in
        .claude/commands/*|.opencode/commands/*|.prime/agent/prompts/*) return 0 ;;
        .github/agents/*|.github/prompts/*|.github/instructions/*)      return 0 ;;
        .codex/codex-config-snippet.toml)                               return 0 ;;
    esac
    return 1
}

# placed_files DIR -> every regular file the installer put in DIR, target-relative.
placed_files() {
    ( cd "$1" && find . -type f \
        -not -name '*.bak-*' -not -path './.cypress/growth/*' \
        -not -name '*.pyc' -not -path '*/__pycache__/*' \
        | sed 's|^\./||' | sort )
}

SELF="$ROOT/tests/test-install-placement.sh"

load_files() {  # FILES <- placed files of DIR
    FILES=(); while IFS= read -r _l; do FILES+=("$_l"); done < <(placed_files "$1")
}
load_cond() {  # COND_FILES <- files of a github-copilot DIR not in FILES
    COND_FILES=()
    while IFS= read -r _l; do
        case " ${FILES[*]} " in *" $_l "*) ;; *) COND_FILES+=("$_l") ;; esac
    done < <(placed_files "$1")
}

# M7 + M3 + M1-unmaintained over the COMPLETE destination set.
# Asserts SPEC-0001 SINGLE_WRITER (the recoverability half), SPEC-0001
# BACKUP_BEFORE_REPLACE, SPEC-0001 IDENTICAL_RERUN_IS_INERT.
case_recover() {
    local T="$WORK/recover"
    mkdir -p "$T"   # fresh, not a BASE copy: the codex snippet names the target path
    "$ROOT/install.sh" $EVERY_HOST --project-dir "$T" --copy --legal-corpus yes >/dev/null 2>&1 \
        || fail "baseline install \$EVERY_HOST --copy did not succeed"
    load_files "$T"
    [[ ${#FILES[@]} -gt 100 ]] || fail "discovered only ${#FILES[@]} placed files — discovery is broken"
    # M3: an identical re-run churns no backup; name the churned files.
    "$ROOT/install.sh" $EVERY_HOST --project-dir "$T" --copy --legal-corpus yes >/dev/null 2>&1 \
        || fail "idempotent re-run did not succeed"
    CHURN=(); while IFS= read -r _l; do CHURN+=("$_l"); done \
        < <(find "$T" -name '*.bak-*' | sed "s|^$T/||" | sort)
    if [[ ${#CHURN[@]} -gt 0 ]]; then
        echo "M3 VIOLATED — an identical re-run backed up ${#CHURN[@]} file(s):" >&2
        printf '  %s\n' "${CHURN[@]}" >&2
        fail "backup churn buries the graft-audit signal under no-op .bak entries"
    fi
    # M7: mark every placed file at head AND tail (a truncated backup keeps
    # one end), then re-run once. Symlinks and installer state are skipped.
    SENTINEL='CYPRESS-PLANT-SENTINEL-DO-NOT-LOSE'
    local marked=0 rel
    for rel in "${FILES[@]}"; do
        [[ -L "$T/$rel" ]] && continue
        is_installer_state "$rel" && continue
        printf '# %s\n%s' "$SENTINEL" "$(cat "$T/$rel")" > "$T/$rel.marked" \
            && mv "$T/$rel.marked" "$T/$rel"
        printf '\n# %s\n' "$SENTINEL" >> "$T/$rel" && marked=$((marked + 1))
    done
    [[ "$marked" -gt 100 ]] || fail "marked only $marked files — the sweep is not covering the install"

    "$ROOT/install.sh" $EVERY_HOST --project-dir "$T" --copy --legal-corpus yes >"$WORK/m7-rerun.log" 2>&1 \
        || { tail -25 "$WORK/m7-rerun.log" >&2; fail "re-run over a customized plant did not succeed"; }

    local lost=() unmaintained=() unrecoverable=()
    for rel in "${FILES[@]}"; do
        [[ -L "$T/$rel" ]] && continue
        if grep -q "$SENTINEL" "$T/$rel" 2>/dev/null; then
            # Edit intact: correct only for add-if-missing files.
            is_plant_owned "$rel" || unmaintained+=("$rel")
            continue
        fi
        is_installer_state "$rel" && continue
        if ! compgen -G "$T/$rel.bak-*" >/dev/null; then
            lost+=("$rel")
        elif [[ "$(grep -cs "$SENTINEL" "$T/$rel".bak-* | awk -F: '{s+=$NF} END {print s+0}')" -lt 2 ]]; then
            unrecoverable+=("$rel")   # a backup must keep BOTH sentinels
        fi
    done
    if [[ ${#unrecoverable[@]} -gt 0 ]]; then
        echo "M7 VIOLATED — ${#unrecoverable[@]} destination(s) have a .bak-* that does NOT carry the body it replaced:" >&2
        printf '  %s\n' "${unrecoverable[@]}" >&2
        fail "a backup must carry the previous body, not merely exist"
    fi
    if [[ ${#unmaintained[@]} -gt 0 ]]; then
        echo "M1 VIOLATED — ${#unmaintained[@]} seed-owned destination(s) kept a plant edit through a re-install:" >&2
        printf '  %s\n' "${unmaintained[@]}" >&2
        fail "a destination the seed owns must be fast-forwarded, not abandoned"
    fi
    if [[ ${#lost[@]} -gt 0 ]]; then
        echo "M7 VIOLATED — ${#lost[@]} destination(s) replaced a plant edit with NO recoverable backup:" >&2
        printf '  %s\n' "${lost[@]}" >&2
        fail "every installer destination must be recoverable (one canonical writer)"
    fi
}

# M3 under --symlink (place_kernel once ping-ponged there), then M9 on the same
# tree. M9 asserts SPEC-0001 SYMLINK_MODE_IS_UNIFORM.
case_symchurn() {
    local SYM="$WORK/idem-symlink" _run rel
    mkdir -p "$SYM"
    for _run in 1 2 3; do
        "$ROOT/install.sh" $EVERY_HOST --project-dir "$SYM" --symlink >/dev/null 2>&1 \
            || fail "M3: --symlink install (run $_run) did not succeed"
    done
    SYM_CHURN=(); while IFS= read -r _l; do SYM_CHURN+=("$_l"); done \
        < <(find "$SYM" -name '*.bak-*' | sed "s|^$SYM/||" | sort)
    if [[ ${#SYM_CHURN[@]} -gt 0 ]]; then
        echo "M3 VIOLATED under --symlink — ${#SYM_CHURN[@]} backup(s) after identical re-runs:" >&2
        printf '  %s\n' "${SYM_CHURN[@]}" >&2
        fail "idempotence must hold in BOTH link modes, not just the tested one"
    fi
    # M9: every placed file is a link, or a recorded exception.
    local not_linked=()
    while IFS= read -r rel; do
        [[ -L "$SYM/$rel" ]] && continue
        is_plant_owned "$rel" && continue
        is_installer_state "$rel" && continue
        is_generated "$rel" && continue
        not_linked+=("$rel")
    done < <(placed_files "$SYM")
    if [[ ${#not_linked[@]} -gt 0 ]]; then
        echo "M9 VIOLATED — ${#not_linked[@]} file(s) placed as copies under --symlink" >&2
        echo "and not in the recorded add-if-missing exception list:" >&2
        printf '  %s\n' "${not_linked[@]}" >&2
        fail "--symlink must place links, or the exception must be recorded in is_plant_owned()"
    fi
}

# M2: a destination symlink never authorizes a write to its referent.
# Asserts SPEC-0001 SYMLINK_IS_REPLACED_NOT_FOLLOWED.
case_m2() {
    load_files "$BASE"
    local A="$WORK/attack" OUT="$WORK/outside" rel victim
    mkdir -p "$A" "$OUT"
    for rel in "${FILES[@]}"; do
        victim="$OUT/$(printf '%s' "$rel" | tr '/' '_')"
        printf 'PRECIOUS-REFERENT %s\n' "$rel" > "$victim"
        mkdir -p "$A/$(dirname "$rel")"
        ln -s "$victim" "$A/$rel"
    done
    ( cd "$OUT" && find . -type f | sort | xargs cksum ) > "$WORK/victims.before"
    # Refusing a link that leaves the target is also safe: record it, replace
    # the link with a real file, and re-run until the install completes. Any
    # other abort is a failure.
    local refused=() attempts=0 blocked
    while :; do
        attempts=$((attempts + 1))
        "$ROOT/install.sh" $EVERY_HOST --project-dir "$A" --copy --legal-corpus yes >"$WORK/m2.log" 2>&1 && break
        [[ $attempts -le 40 ]] || fail "M2: the installer never completed against a hostile target in $attempts attempts"
        blocked="$(grep -oE '[^ ]+ is a symlink leaving the target' "$WORK/m2.log" \
                   | head -1 | sed 's/ is a symlink.*//' || true)"
        if [[ -z "$blocked" ]]; then
            tail -20 "$WORK/m2.log" >&2
            fail "M2: install aborted against a hostile target for a reason other than a refused symlink (see log above)"
        fi
        refused+=("$blocked")
        rm -f "$A/$blocked"
        printf 'placeholder\n' > "$A/$blocked"
    done

    local clobbered=()
    for rel in "${FILES[@]}"; do
        victim="$OUT/$(printf '%s' "$rel" | tr '/' '_')"
        grep -q "PRECIOUS-REFERENT $rel" "$victim" 2>/dev/null || clobbered+=("$rel")
    done
    ( cd "$OUT" && find . -type f | sort | xargs cksum ) > "$WORK/victims.after"
    if ! diff -q "$WORK/victims.before" "$WORK/victims.after" >/dev/null; then
        echo "M2 VIOLATED — the referents outside the target are not byte-identical after the install:" >&2
        diff "$WORK/victims.before" "$WORK/victims.after" >&2 || true
        fail "an install must not modify any file outside --project-dir"
    fi
    [[ $(wc -l < "$WORK/victims.before") -eq ${#FILES[@]} ]] \
        || fail "M2: digested $(wc -l < "$WORK/victims.before") referents for ${#FILES[@]} destinations — the sweep is not covering the attack"
    if [[ ${#clobbered[@]} -gt 0 ]]; then
        echo "M2 VIOLATED — ${#clobbered[@]} destination(s) were written THROUGH a symlink:" >&2
        printf '  %s\n' "${clobbered[@]}" >&2
        fail "a destination symlink must be replaced as a link object, never followed"
    fi

    # Coverage: each destination was refused, replaced, or is add-if-missing.
    was_refused() { local r; for r in ${refused[@]+"${refused[@]}"}; do [[ "$r" == "$1" ]] && return 0; done; return 1; }
    local replaced=0 skipped=()
    for rel in "${FILES[@]}"; do
        was_refused "$rel" && continue
        if [[ -L "$A/$rel" ]]; then
            is_plant_owned "$rel" || skipped+=("$rel")
        else
            replaced=$((replaced + 1))
        fi
    done
    if [[ ${#skipped[@]} -gt 0 ]]; then
        echo "M2 VIOLATED — ${#skipped[@]} destination(s) still hold the attacker's symlink and are not add-if-missing:" >&2
        printf '  %s\n' "${skipped[@]}" >&2
        fail "M2 must exercise every destination it reports on"
    fi
    # A floor on the set actually tested; a fall is a coverage regression.
    [[ $replaced -ge 300 ]] || fail "M2 exercised only $replaced destinations of ${#FILES[@]} (floor 300, ${#refused[@]} refused)"
    echo "  M2: $replaced destinations had the link object replaced, ${#refused[@]} refused, $(( ${#FILES[@]} - replaced - ${#refused[@]} )) add-if-missing"
}

# M4: --force suppresses the per-file warning and never the backup.
# Asserts SPEC-0001 FORCE_SUPPRESSES_WARNING_NOT_BACKUP.
case_m4() {
    local F="$WORK/forced" G="$WORK/unforced" victim out
    mkdir -p "$F" "$G"
    "$ROOT/install.sh" claude-code --project-dir "$F" --copy >/dev/null 2>&1 \
        || fail "M4 baseline install failed"
    printf '\n# PLANT EDIT UNDER FORCE\n' >> "$F/.claude/settings.json"
    printf '# a deliberate kernel deviation\n' >> "$F/CLAUDE.md"
    rm -f "$F/AGENTS.md"; printf '# our own AGENTS body\n' > "$F/AGENTS.md"
    out="$("$ROOT/install.sh" claude-code --project-dir "$F" --copy --force 2>&1 >/dev/null)" \
        || fail "M4: --force install failed"
    for victim in .claude/settings.json CLAUDE.md AGENTS.md; do
        compgen -G "$F/$victim.bak-*" >/dev/null \
            || fail "M4 VIOLATED: --force replaced $victim with no backup"
    done
    ! grep -q "backed up existing" <<<"$out" \
        || fail "M4: --force still announced a backup: $(grep 'backed up existing' <<<"$out" | head -3)"
    # ...and without --force the backup is announced.
    "$ROOT/install.sh" claude-code --project-dir "$G" --copy >/dev/null 2>&1
    printf '\n# edit\n' >> "$G/.claude/settings.json"
    out="$("$ROOT/install.sh" claude-code --project-dir "$G" --copy 2>&1 >/dev/null || true)"
    grep -q "backed up existing" <<<"$out" \
        || fail "M4: without --force the backup must be announced, and was not"
}

# M8: every backup the writer produces is classifiable by graft-audit.py.
# Asserts SPEC-0001 EVERY_BACKUP_IS_CLASSIFIABLE; the UNMAPPED exit is held by
# X390 in tests/test-graft-tools.sh.
case_m8() {
    local AUD="$WORK/audit" rel report audit_rc
    mkdir -p "$AUD" && cp -a "$BASE/." "$AUD/"
    while IFS= read -r rel; do
        [[ -L "$AUD/$rel" ]] && continue
        is_installer_state "$rel" && continue
        is_plant_owned "$rel" && continue
        printf '\n# edited by the plant\n' >> "$AUD/$rel"
    done < <(placed_files "$AUD")
    "$ROOT/install.sh" $EVERY_HOST --project-dir "$AUD" --copy --legal-corpus yes >/dev/null 2>&1 \
        || fail "audit-totality re-run did not succeed"
    if report="$(python3 "$ROOT/tools/graft-audit.py" "$AUD" "$ROOT" 2>&1)"; then audit_rc=0; else audit_rc=$?; fi
    if grep -q "UNMAPPED backup" <<<"$report"; then
        echo "M8 VIOLATED — graft-audit.py cannot classify backups the writer produced:" >&2
        grep -A 20 "UNMAPPED backup" <<<"$report" >&2
        fail "every installer destination must map to a seed source or a named class"
    fi
    grep -q "backups audited: [1-9]" <<<"$report" \
        || fail "M8: the audit saw no backups at all — it cannot be certifying anything"
    [[ $audit_rc -eq 0 ]] \
        || fail "M8: graft-audit.py exited $audit_rc on a plant whose backups it classified without complaint"
}

# M10: no write escapes PROJECT_DIR. Asserts SPEC-0001 §5's Security NFR and
# §9 AC-2. A symlink that stays INSIDE the target must keep working.
case_m10() {
    local ESC="$WORK/escape" OUTSIDE="$WORK/escape/outside" before rel
    mkdir -p "$OUTSIDE"

    # (1) a dangling symlink at the note path is not written through
    local P1="$ESC/plant1"
    mkdir -p "$P1/docs/graph/plans"
    printf 'Rule: always rebase.\n' > "$P1/CLAUDE.md"
    ln -s "$OUTSIDE/escaped-note.md" "$P1/docs/graph/plans/adopted-instructions.md"
    "$ROOT/install.sh" claude-code --project-dir "$P1" >/dev/null 2>&1 \
        || fail "M10: install into a plant with a dangling note symlink did not succeed"
    [[ -e "$OUTSIDE/escaped-note.md" ]] \
        && fail "M10 VIOLATED — the installer wrote through a dangling symlink to $OUTSIDE"
    [[ -f "$P1/docs/graph/plans/adopted-instructions.md" && ! -L "$P1/docs/graph/plans/adopted-instructions.md" ]] \
        || fail "M10: the note was not written as a real file inside the plant"
    ls "$P1"/docs/graph/plans/adopted-instructions.md.bak-* >/dev/null 2>&1 \
        || fail "M10: the displaced link object was destroyed rather than backed up"
    echo "  M10 (1): a dangling destination symlink is moved aside, never written through — OK"

    # (2) a destination symlink that leaves the target is refused BEFORE any write
    local P2="$ESC/plant2"
    mkdir -p "$P2" "$OUTSIDE/realdir"
    ln -s "$OUTSIDE/realdir" "$P2/.cypress"
    if "$ROOT/install.sh" claude-code --project-dir "$P2" >"$ESC/log2" 2>&1; then
        fail "M10 VIOLATED — an install through a destination symlink leaving the target succeeded"
    fi
    grep -q "symlink leaving the target" "$ESC/log2" \
        || { cat "$ESC/log2" >&2; fail "M10: refused, but not for the stated reason"; }
    [[ -e "$OUTSIDE/realdir/seed.json" ]] && fail "M10 VIOLATED — seed.json landed outside the plant"
    [[ -e "$P2/docs" ]] && fail "M10: the refusal was not a preflight — the graph was already on disk"
    echo "  M10 (2): a destination symlink leaving the target is refused before the first byte — OK"

    # (3) a symlink that stays inside the target still works
    local P3="$ESC/plant3"
    mkdir -p "$P3/real-cypress"
    ln -s "real-cypress" "$P3/.cypress"
    "$ROOT/install.sh" claude-code --project-dir "$P3" >/dev/null 2>&1 \
        || fail "M10: an internal destination symlink was refused; the rule is about leaving the target"
    [[ -f "$P3/real-cypress/seed.json" ]] \
        || fail "M10: an internal destination symlink did not receive the write"
    echo "  M10 (3): a destination symlink that stays inside the target still works — OK"

    # (4) fill_plant_facts rewrites index.md in place: not through a link leaving the target
    local P4="$ESC/plant4"
    mkdir -p "$P4"
    "$ROOT/install.sh" claude-code --project-dir "$P4" >/dev/null 2>&1 \
        || fail "M10(4): baseline install failed"
    cp "$P4/docs/graph/index.md" "$OUTSIDE/stolen-index.md"
    rm "$P4/docs/graph/index.md"
    ln -s "$OUTSIDE/stolen-index.md" "$P4/docs/graph/index.md"
    before="$(cksum < "$OUTSIDE/stolen-index.md")"
    "$ROOT/install.sh" claude-code --project-dir "$P4" --environment-class real-production \
        >"$ESC/log4" 2>&1 || true
    [[ "$(cksum < "$OUTSIDE/stolen-index.md")" == "$before" ]] \
        || fail "M10 VIOLATED — fill_plant_facts wrote a plant fact through a symlink to $OUTSIDE"
    grep -q "symlink leaving the target" "$ESC/log4" \
        || { cat "$ESC/log4" >&2; fail "M10(4): unchanged, but the refusal was not reported"; }
    echo "  M10 (4): plant facts are not written through an index.md symlink leaving the target — OK"

    # (5) an index.md symlinked inside the target still receives its facts
    local P5="$ESC/plant5"
    mkdir -p "$P5"
    "$ROOT/install.sh" claude-code --project-dir "$P5" >/dev/null 2>&1 \
        || fail "M10(5): baseline install failed"
    mv "$P5/docs/graph/index.md" "$P5/docs/graph/real-index.md"
    ln -s "real-index.md" "$P5/docs/graph/index.md"
    "$ROOT/install.sh" claude-code --project-dir "$P5" --environment-class staging >/dev/null 2>&1 \
        || fail "M10(5): an internal index.md symlink was refused; the rule is about leaving the target"
    grep -q "environment_class: staging" "$P5/docs/graph/real-index.md" \
        || fail "M10(5): the plant fact did not reach the real file behind an internal link"
    echo "  M10 (5): an index.md symlink that stays inside the target still receives its facts — OK"

    # (6) a symlinked DIRECTORY under the target pointing outside is refused
    # before the first byte: one adapter directory, one docs/graph subtree.
    local esc_out esc_tgt after
    for rel in ".claude/skills/library-wiki" "docs/graph/protocols"; do
        esc_out="$WORK/esc-out-$(basename "$rel")"; esc_tgt="$WORK/esc-tgt-$(basename "$rel")"
        mkdir -p "$esc_out" "$esc_tgt/$(dirname "$rel")"
        printf 'PRECIOUS-OUTSIDE %s\n' "$rel" > "$esc_out/keep.md"
        before="$(cd "$esc_out" && find . -type f | sort | xargs cksum)"
        ln -s "$esc_out" "$esc_tgt/$rel"
        if "$ROOT/install.sh" all --project-dir "$esc_tgt" --copy >/dev/null 2>&1; then
            fail "M10 (6): an install through a symlinked '$rel' leaving the target SUCCEEDED — it wrote outside --project-dir"
        fi
        after="$(cd "$esc_out" && find . -type f | sort | xargs cksum)"
        [[ "$before" == "$after" ]] \
            || fail "M10 (6): '$rel' — the directory outside the target was modified by a refused install"
        [[ "$(find "$esc_out" -type f | wc -l)" -eq 1 ]] \
            || fail "M10 (6): '$rel' — files were created outside the target"
    done
    echo "  M10 (6): a symlinked directory leaving the target is refused (adapter dir, graph subtree) — OK"

    # (7) a symlinked directory that stays inside the target still works
    local ins_tgt="$WORK/esc-inside"
    mkdir -p "$ins_tgt/docs/graph" "$ins_tgt/elsewhere"
    ln -s "$ins_tgt/elsewhere" "$ins_tgt/docs/graph/protocols"
    "$ROOT/install.sh" claude-code --project-dir "$ins_tgt" --copy >/dev/null 2>&1 \
        || fail "M10 (7): a symlink that stays inside the target was refused — the check cannot tell inside from outside"
    [[ "$(find "$ins_tgt/elsewhere" -name '*.md' | wc -l)" -gt 5 ]] \
        || fail "M10 (7): nothing was placed through the inside-the-target symlink"
    echo "  M10 (7): a symlinked directory that stays inside the target still receives its nodes — OK"
}

# M7b / M2b: the conditional destinations (copilot hooks appear only while
# .claude/settings.json is absent), held to the same two properties.
case_cond() {
    load_files "$BASE"
    load_cond "$BASECOPILOT"
    local COND_SENTINEL="CYPRESS-COND-SENTINEL" TB="$WORK/cond-recover" rel bak found
    mkdir -p "$TB"
    "$ROOT/install.sh" github-copilot --project-dir "$TB" --copy >/dev/null 2>&1 \
        || fail "M7b setup install failed"
    for rel in "${COND_FILES[@]}"; do
        printf '\n# %s\n' "$COND_SENTINEL" >> "$TB/$rel"
    done
    "$ROOT/install.sh" github-copilot --project-dir "$TB" --copy >/dev/null 2>&1 \
        || fail "M7b re-install over a customized plant failed"
    for rel in "${COND_FILES[@]}"; do
        grep -q "$COND_SENTINEL" "$TB/$rel" 2>/dev/null && continue   # untouched
        found=0
        for bak in "$TB/$rel".bak-*; do
            [[ -e "$bak" ]] || continue
            grep -q "$COND_SENTINEL" "$bak" 2>/dev/null && { found=1; break; }
        done
        [[ $found -eq 1 ]] || fail "M7b VIOLATED — $rel replaced a plant edit with no recoverable backup"
    done

    local TS="$WORK/cond-symlink" OUT="$WORK/cond-outside" victim
    mkdir -p "$TS" "$OUT"
    for rel in "${COND_FILES[@]}"; do
        victim="$OUT/$(echo "$rel" | tr '/' '_')"
        printf 'PRECIOUS-OUTSIDE-FILE\n' > "$victim"
        mkdir -p "$TS/$(dirname "$rel")"
        ln -s "$victim" "$TS/$rel"
    done
    "$ROOT/install.sh" github-copilot --project-dir "$TS" --copy >/dev/null 2>&1 || true
    for rel in "${COND_FILES[@]}"; do
        victim="$OUT/$(echo "$rel" | tr '/' '_')"
        [[ "$(cat "$victim")" == "PRECIOUS-OUTSIDE-FILE" ]] \
            || fail "M2b VIOLATED — installing wrote THROUGH the symlink at $rel and destroyed $victim, a file outside --project-dir."
    done
}

# --- one-case subcommand, run by the parallel dispatcher ---------------------
if [ "${1:-}" = "__case" ]; then
    "$2"
    exit $?
fi

# --- main: two shared read-only installs, the read-only asserts, then every
#     case concurrently under the gate's shared budget. ------------------------
export ROOT
BASE="$WORK/base"; mkdir -p "$BASE"
"$ROOT/install.sh" $EVERY_HOST --project-dir "$BASE" --copy --legal-corpus yes >/dev/null 2>&1 \
    || fail "baseline install \$EVERY_HOST --copy did not succeed"
T="$BASE"
load_files "$T"
[[ ${#FILES[@]} -gt 100 ]] || fail "discovered only ${#FILES[@]} placed files — discovery is broken"

BASECOPILOT="$WORK/base-copilot"; mkdir -p "$BASECOPILOT"
"$ROOT/install.sh" github-copilot --project-dir "$BASECOPILOT" --copy >/dev/null 2>&1 \
    || fail "baseline install github-copilot --copy did not succeed"
load_cond "$BASECOPILOT"
for _h in .github/hooks/route-hook.py .github/hooks/route.json \
          .github/hooks/status-hook.py .github/hooks/status.json; do
    case " ${COND_FILES[*]} " in
        *" $_h "*) ;;
        *) fail "conditional destination $_h is outside the discovered set — covered by nothing" ;;
    esac
done

# M1 completeness: every machinery node the SEED owns arrives in the plant.
# Discovery cannot see a destination that was never written, so this reads the
# seed's own inventory.
missing_nodes=()
for src in "$ROOT"/protocols/*.md "$ROOT"/core/method/*.md "$ROOT"/agents/*.md; do
    [[ -e "$src" ]] || continue
    base="$(basename "$src")"
    case "$base" in _*) continue ;; esac
    case "$src" in
        */protocols/*)   want="$T/docs/graph/protocols/$base" ;;
        */core/method/*) want="$T/docs/graph/method/$base" ;;
        */agents/*)      want="$T/docs/graph/agents/$base" ;;
    esac
    [[ -e "$want" || -L "$want" ]] || missing_nodes+=("${want#"$T/"}")
done
for d in "$ROOT"/skills/*/; do
    [[ -f "${d%/}/SKILL.md" ]] || continue
    want="$T/docs/graph/skills/$(basename "${d%/}").md"
    [[ -e "$want" || -L "$want" ]] || missing_nodes+=("${want#"$T/"}")
done
# Adapter machinery of every host.
for rel in .claude/route-hook.py .claude/status-hook.py .claude/bound-hook.py \
           .claude/agent-lint.py .claude/settings.json \
           opencode.json \
           .github/copilot-instructions.md \
           .prime/agent/settings.json .prime/agent/APPEND_SYSTEM.md \
           .prime/agent/extensions/route-extension.ts \
           .prime/agent/extensions/status-extension.ts \
           .codex/codex-config-snippet.toml \
           docs/graph/agent-lint.py docs/graph/graph-lint.py \
           docs/graph/_schema.md docs/graph/index.md \
           EXPERT_SEED_INSTALL_PROMPT.md .cypress/seed.json; do
    [[ -e "$T/$rel" || -L "$T/$rel" ]] || missing_nodes+=("$rel")
done
# The template subtree, placed wholesale by place_tree.
tmpl_seed="$(find "$ROOT/templates" -name '*.md' -not -name '*.pyc' | wc -l | tr -d ' ')"
tmpl_plant=0
if [[ -d "$T/docs/graph/templates" ]]; then
    tmpl_plant="$(find "$T/docs/graph/templates" \( -type f -o -type l \) -name '*.md' \
                  -not -name '*.bak-*' | wc -l | tr -d ' ')"
fi
[[ "$tmpl_plant" -ge "$tmpl_seed" ]] \
    || missing_nodes+=("docs/graph/templates/ ($tmpl_plant of $tmpl_seed template files)")
if [[ ${#missing_nodes[@]} -gt 0 ]]; then
    echo "M1 VIOLATED — ${#missing_nodes[@]} node(s) the seed owns never reached the plant:" >&2
    printf '  %s\n' "${missing_nodes[@]}" >&2
    fail "a machinery node the installer stopped placing is invisible to any check that enumerates what WAS placed"
fi

# M11: every path the route resolvers may SELECT is a path the installer writes,
# read from route-hook.py CANDIDATES and route-extension.ts CANDIDATES.
stray_candidates=()
while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    [[ -e "$T/$rel" || -L "$T/$rel" ]] || stray_candidates+=("$rel")
done < <(python3 - "$ROOT" <<'PY'
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
seen = []
sources = [
    ("integrations/claude-code/route-hook.py", r"^CANDIDATES\s*=\s*\((.*?)\)\s*$", r"[^,]+"),
    ("integrations/prime-agent/route-extension.ts", r"^const CANDIDATES\s*=\s*\[(.*?)\];\s*$", r"\[([^\]]*)\]"),
]
for rel, block, element in sources:
    m = re.search(block, (root / rel).read_text(encoding="utf-8"), re.M | re.S)
    if not m:
        sys.exit(f"{rel}: no CANDIDATES list to read — the check would assert nothing")
    for el in re.findall(element, m.group(1)):
        path = "/".join(re.findall(r'"([^"]+)"', el))
        if path and path not in seen:
            seen.append(path)
if not seen:
    sys.exit("neither resolver yielded a candidate path — a vacuous pass")
print("\n".join(seen))
PY
) || fail "could not read the route resolvers' candidate lists"
if [[ ${#stray_candidates[@]} -gt 0 ]]; then
    echo "M11 VIOLATED — ${#stray_candidates[@]} resolver candidate(s) no install produces:" >&2
    printf '  %s\n' "${stray_candidates[@]}" >&2
    fail "a resolver may select a path the installer never writes"
fi
echo "  M11: every route-resolver candidate is a path the installer writes — OK"

export BASE BASECOPILOT
SCN="$(mktemp)"
for c in case_recover case_symchurn case_m2 case_m4 case_m8 case_m10 case_cond; do
    printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"
[ "$rc" -eq 0 ] || { echo "install-placement: FAIL — a planted scenario did not pass" >&2; exit "$rc"; }

echo "install-placement: OK — ${#FILES[@]} destinations plus ${#COND_FILES[@]} conditional ones recoverable, symlink-safe, idempotent, link-uniform, audit-classifiable, target-contained"
