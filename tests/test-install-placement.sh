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
#   M13 a retired seed entry is flagged RETIRED; M14 a plant-only harness entry ORPHAN
#   M15-M20 selective placement: propose, place, refuse, refresh, leave, check
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
        .opencode/agents/*)                                             return 0 ;;  # ADR-0022: projected through the model map
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
        if [[ "$blocked" == "docs/graph/models.md" ]]; then
            # A bare placeholder has no `## Map` table, so SPEC-0001
            # MODEL_MAP_UNREADABLE dies before the next attempt even starts.
            # The shipped template has a valid (if unfilled) map, so the
            # loop can keep proving the symlink-replacement contract.
            cp "$ROOT/templates/docs/models.md" "$A/$blocked"
        else
            printf 'placeholder\n' > "$A/$blocked"
        fi
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

# M12, SPEC-0001 CHECK_EXECUTES_EACH_WIRED_HOOK: `--check` runs each wired context
# hook once on the check envelope, writes nothing, and fails naming a hook
# whose script is gone. BASE wires Claude Code's two and Prime Agent's two;
# BASECOPILOT wires the Copilot pair.
tree_sig() { ( cd "$1" && find . -print0 | LC_ALL=C sort -z | xargs -0 shasum 2>/dev/null; find . | LC_ALL=C sort ) | shasum; }
case_hook_check() {
    local HC="$WORK/hookcheck" HP="$WORK/hookcheck-copilot" out rc before ev_script
    mkdir -p "$HC" "$HP" && cp -a "$BASE/." "$HC/" && cp -a "$BASECOPILOT/." "$HP/"
    before="$(tree_sig "$HC")"
    rc=0; out="$("$ROOT/install.sh" claude-code --check --project-dir "$HC" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: --check over passing hooks exited $rc: $out"
    grep -q "no generated views are in scope" <<<"$out" \
        || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: CHECK_WITHOUT_COPILOT_SAYS_SO's line is gone: $out"
    for ev_script in "UserPromptSubmit .claude/route-hook.py" "SessionStart .claude/status-hook.py" \
                     "UserPromptSubmit .prime/agent/hooks/route-hook.py" "SessionStart .prime/agent/hooks/status-hook.py"; do
        grep -q "hook ${ev_script% *} ${ev_script#* } ran" <<<"$out" \
            || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: no ran line for $ev_script: $out"
    done
    [[ "$(tree_sig "$HC")" == "$before" ]] \
        || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: --check changed the plant"
    rm "$HC/.claude/route-hook.py"
    rc=0; out="$("$ROOT/install.sh" claude-code --check --project-dir "$HC" 2>&1)" || rc=$?
    [[ $rc -ne 0 ]] || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: --check passed a plant whose route hook is gone: $out"
    grep -q "UserPromptSubmit .claude/route-hook.py" <<<"$out" \
        || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: the failure does not name the hook: $out"
    rm "$HP/.github/hooks/status-hook.py"
    rc=0; out="$("$ROOT/install.sh" github-copilot --check --project-dir "$HP" 2>&1)" || rc=$?
    [[ $rc -ne 0 ]] || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: --check passed a Copilot plant whose status hook is gone: $out"
    grep -q "SessionStart .github/hooks/status-hook.py" <<<"$out" \
        || fail "CHECK_EXECUTES_EACH_WIRED_HOOK: the Copilot failure does not name the hook: $out"
    echo "  M12 CHECK_EXECUTES_EACH_WIRED_HOOK: four hooks ran with the plant unchanged; a missing route or Copilot status script fails --check, named — OK"
}

# M13, SPEC-0001 CHECK_FLAGS_RETIRED_HARNESS_ENTRY: an origin: seed skill the
# seed no longer ships (it folded skill.from-scratch-bootstrap into
# protocol.from-scratch), still in the graph and still projected, is named
# RETIRED by --check and by graft-audit; nothing is deleted, the exit code is
# the rest of the check's, and a backup of its projection classifies RETIRED.
case_retired_flag() {
    local R="$WORK/retired" out rc before node=docs/graph/skills/from-scratch-bootstrap.md
    local proj=.claude/skills/from-scratch-bootstrap/SKILL.md lone=.claude/agents/legacy-steward.md audit_rc0
    [[ ! -e "$ROOT/skills/from-scratch-bootstrap" ]] || fail "fixture: the seed ships skills/from-scratch-bootstrap again"
    [[ ! -e "$ROOT/agents/legacy-steward.md" ]] || fail "fixture: the seed ships agents/legacy-steward.md"
    mkdir -p "$R" && cp -a "$BASE/." "$R/"
    rc=0; out="$("$ROOT/install.sh" claude-code --check --project-dir "$R" 2>&1)" || rc=$?
    grep -q "every harness entry has a graph home" <<<"$out" \
        || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: --check over a clean install does not say every harness entry has a graph home: $out"
    audit_rc0=0; python3 "$ROOT/tools/graft-audit.py" "$R" "$ROOT" >/dev/null 2>&1 || audit_rc0=$?
    printf -- '---\nname: from-scratch-bootstrap\nid: skill.from-scratch-bootstrap\nkind: skill\norigin: seed\n---\n# from-scratch-bootstrap\n' > "$R/$node"
    mkdir -p "$R/${proj%/SKILL.md}" && cp "$R/$node" "$R/$proj"
    # the Given's third arm: an origin: seed harness entry with no graph node at all
    printf -- '---\nname: legacy-steward\ndescription: a seed agent the seed folded away\norigin: seed\n---\n# legacy-steward\n' > "$R/$lone"
    rc=0; out="$(python3 "$ROOT/tools/graft-audit.py" "$R" "$ROOT" 2>&1)" || rc=$?
    [[ $rc -eq $audit_rc0 ]] || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: a RETIRED flag changed graft-audit's exit code from $audit_rc0 to $rc: $out"
    grep -q "RETIRED $lone:" <<<"$out" || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: graft-audit does not name $lone RETIRED: $out"
    before="$(tree_sig "$R")"
    rc=0; out="$("$ROOT/install.sh" claude-code --check --project-dir "$R" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: a RETIRED flag changed the exit code to $rc: $out"
    for p in "$node" "$proj" "$lone"; do
        grep -q -- "--check: RETIRED $p:" <<<"$out" \
            || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: --check does not name $p RETIRED: $out"
    done
    [[ "$(tree_sig "$R")" == "$before" ]] || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: --check changed the plant"
    printf 'a line the projection gained\n' >> "$R/$proj"
    "$ROOT/install.sh" claude-code --project-dir "$R" >/dev/null 2>&1 \
        || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: the re-install over the retired projection failed"
    rc=0; out="$(python3 "$ROOT/tools/graft-audit.py" "$R" "$ROOT" 2>&1)" || rc=$?
    grep -q "'RETIRED': 1" <<<"$out" \
        || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: graft-audit does not classify the retired projection's backup RETIRED: $out"
    grep -q "UNMAPPED backup" <<<"$out" \
        && fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: graft-audit still reports the retired projection's backup UNMAPPED: $out"
    grep -q "RETIRED $proj:" <<<"$out" \
        || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: graft-audit does not name $proj RETIRED: $out"
    [[ -f "$R/$node" && -f "$R/$proj" && -f "$R/$lone" ]] || fail "CHECK_FLAGS_RETIRED_HARNESS_ENTRY: a retired entry was deleted"
    echo "  M13 CHECK_FLAGS_RETIRED_HARNESS_ENTRY: the retired node and its projection are named RETIRED by --check and graft-audit, nothing deleted — OK"
}

# M14, SPEC-0001 CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: a skill and an agent the plant
# authored straight into harness directories, with no graph home, are named
# ORPHAN by --check and by graft-audit; nothing is written or deleted.
case_orphan_flag() {
    local O="$WORK/orphan" out rc before p audit_rc0
    mkdir -p "$O" && cp -a "$BASE/." "$O/"
    audit_rc0=0; python3 "$ROOT/tools/graft-audit.py" "$O" "$ROOT" >/dev/null 2>&1 || audit_rc0=$?
    mkdir -p "$O/.claude/skills/deploy-notes" "$O/.prime/agent/agents"
    printf -- '---\nname: deploy-notes\ndescription: how this plant deploys\n---\n# deploy-notes\n' \
        > "$O/.claude/skills/deploy-notes/SKILL.md"
    printf -- '---\nname: release-steward\ndescription: cuts releases\n---\n# release-steward\n' \
        > "$O/.prime/agent/agents/release-steward.md"
    before="$(tree_sig "$O")"
    rc=0; out="$("$ROOT/install.sh" claude-code --check --project-dir "$O" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: an ORPHAN flag changed the exit code to $rc: $out"
    for p in ".claude/skills/deploy-notes/SKILL.md: no graph home (docs/graph/skills/deploy-notes.md)" \
             ".prime/agent/agents/release-steward.md: no graph home (docs/graph/agents/release-steward.md)"; do
        grep -qF -- "--check: ORPHAN $p" <<<"$out" \
            || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: --check does not say ORPHAN ${p%%:*}: $out"
    done
    [[ "$(tree_sig "$O")" == "$before" ]] || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: --check changed the plant"
    rc=0; out="$(python3 "$ROOT/tools/graft-audit.py" "$O" "$ROOT" 2>&1)" || rc=$?
    [[ $rc -eq $audit_rc0 ]] || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: an ORPHAN flag changed graft-audit's exit code from $audit_rc0 to $rc: $out"
    grep -qF "ORPHAN .claude/skills/deploy-notes/SKILL.md:" <<<"$out" \
        || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: graft-audit does not name the orphan skill: $out"
    [[ -f "$O/.claude/skills/deploy-notes/SKILL.md" && -f "$O/.prime/agent/agents/release-steward.md" ]] \
        || fail "CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: an orphan entry was deleted"
    echo "  M14 CHECK_FLAGS_ORPHAN_HARNESS_ENTRY: two plant-authored harness entries are named ORPHAN by --check and graft-audit, nothing written — OK"
}

# --- selective placement (SPEC-0001 §6, M15 to M20) --------------------------
# Every case installs from a copy of this seed whose three corpora are replaced
# by the synthetic subset under tests/fixtures/corpus-placement/seed, into a copy
# of the synthetic manifests under tests/fixtures/corpus-placement/plant. ESEED
# is shared and read-only; a case that changes the corpus copies it first.
FIX="$ROOT/tests/fixtures/corpus-placement"
make_seed() {
    local S="$1"
    mkdir -p "$S"
    ( cd "$ROOT" && tar cf - --exclude .git --exclude __pycache__ . ) | ( cd "$S" && tar xf - )
    rm -rf "$S/library-corpus" "$S/skill-corpus" "$S/tool-corpus"
    cp -R "$FIX/seed/." "$S/"
}
seed_version() { sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$1/manifest.json" | head -1; }
fresh_plant() { mkdir -p "$1" && cp -R "$FIX/plant/." "$1/"; }
sha_of() { shasum -a 256 "$1" | awk '{print $1}'; }
# expertise_record PLANT -> "id path sha256" per recorded entry, in stamp order
expertise_record() {
    python3 - "$1/.cypress/seed.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for e in data.get("expertise", []):
    print(e["id"], e["path"], e["sha256"])
PY
}

# M15, SPEC-0001 EXPERTISE_PROPOSAL_WRITES_NOTHING and EXPERTISE_MANIFEST_UNREADABLE
case_expertise_propose() {
    local P="$WORK/xp-propose" out rc before
    fresh_plant "$P"
    before="$(tree_sig "$P")"
    rc=0; out="$("$ESEED/install.sh" claude-code --expertise propose --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "EXPERTISE_PROPOSAL_WRITES_NOTHING: propose exited $rc: $out"
    for line in "library-corpus/maven/lumen-core  pom.xml: org.example.lumen:lumen-core-starter-web" \
                "library-corpus/npm/orbit-forms  package.json: @orbit/forms" \
                "skill-corpus/maven/lumen-upgrade  stack: library-corpus/maven/lumen-core"; do
        grep -qxF "$line" <<<"$out" || fail "EXPERTISE_PROPOSAL_WRITES_NOTHING: no proposal line '$line': $out"
    done
    [[ "$(tree_sig "$P")" == "$before" ]] || fail "EXPERTISE_PROPOSAL_WRITES_NOTHING: propose changed the target"
    [[ ! -e "$P/.cypress" && ! -e "$P/CLAUDE.md" && ! -e "$P/.claude" ]] \
        || fail "EXPERTISE_PROPOSAL_WRITES_NOTHING: propose installed something"
    printf '{ not json' > "$P/package.json"
    before="$(tree_sig "$P")"
    rc=0; out="$("$ESEED/install.sh" claude-code --expertise propose --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "EXPERTISE_MANIFEST_UNREADABLE: propose over a broken package.json exited $rc: $out"
    grep -q "package.json.*not valid JSON" <<<"$out" \
        || fail "EXPERTISE_MANIFEST_UNREADABLE: the broken package.json is not named: $out"
    grep -q "^library-corpus/maven/lumen-core  " <<<"$out" \
        || fail "EXPERTISE_MANIFEST_UNREADABLE: the other manifests were not read: $out"
    [[ "$(tree_sig "$P")" == "$before" ]] || fail "EXPERTISE_MANIFEST_UNREADABLE: propose changed the target"
    echo "  M15 EXPERTISE_PROPOSAL_WRITES_NOTHING: propose prints the matches, names a broken manifest, writes nothing — OK"
}

# M16, SPEC-0001 EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST, PLACED_PAGE_CARRIES_ITS_PROVENANCE,
# PLACED_SKILL_IS_A_ROUTABLE_NODE and EXPERTISE_IS_RECORDED_IN_THE_STAMP
case_expertise_place() {
    local P="$WORK/xp-place" out rc V rel got want
    fresh_plant "$P"
    V="$(seed_version "$ESEED")"
    rc=0; out="$("$ESEED/install.sh" claude-code --project-dir "$P" --expertise \
        library-corpus/maven/lumen-core,skill-corpus/maven/lumen-upgrade,tool-corpus/ops/orbit-form-linter,library-corpus/platform/cloud-cli 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST: the install exited $rc: $out"
    got="$(cd "$P/docs/graph" && ls libraries tools | grep -v -e '^index.md$' -e ':$' -e '^$' | sort | tr '\n' ' ')"
    [[ "$got" == "cloud-cli.md lumen-core.md orbit-form-linter.md " ]] \
        || fail "EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST: libraries/ and tools/ hold '$got'"
    [[ -z "$(ls "$P/docs/graph/legal/corpus" 2>/dev/null)" ]] \
        || fail "EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST: the arm wrote under docs/graph/legal/corpus"
    [[ ! -e "$P/docs/graph/corpus-match.py" ]] \
        || fail "EXPERTISE_PROPOSAL_WRITES_NOTHING: tools/corpus-match.py was placed in the plant"
    for rel in libraries/lumen-core.md:library-corpus/maven/lumen-core tools/orbit-form-linter.md:tool-corpus/ops/orbit-form-linter; do
        [[ "$(head -1 "$P/docs/graph/${rel%%:*}")" == "<!-- origin: corpus@$V id: ${rel#*:} -->" ]] \
            || fail "PLACED_PAGE_CARRIES_ITS_PROVENANCE: ${rel%%:*} opens with '$(head -1 "$P/docs/graph/${rel%%:*}")'"
        cmp -s <(tail -n +2 "$P/docs/graph/${rel%%:*}") "$ESEED/${rel#*:}.md" \
            || fail "PLACED_PAGE_CARRIES_ITS_PROVENANCE: ${rel%%:*} differs from its corpus page after the provenance line"
    done
    grep -qx "origin: corpus@$V" "$P/docs/graph/skills/lumen-upgrade.md" \
        || fail "PLACED_SKILL_IS_A_ROUTABLE_NODE: the placed skill carries no 'origin: corpus@$V' line"
    cmp -s <(grep -vx "origin: corpus@$V" "$P/docs/graph/skills/lumen-upgrade.md") "$ESEED/skill-corpus/maven/lumen-upgrade.md" \
        || fail "PLACED_SKILL_IS_A_ROUTABLE_NODE: the placed skill differs from its corpus page beyond the origin line"
    rc=0; out="$(cd "$P" && python3 -B docs/graph/graph-lint.py --show skill.lumen-upgrade 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] && grep -q "lumen-upgrade" <<<"$out" \
        || fail "PLACED_SKILL_IS_A_ROUTABLE_NODE: graph-lint --show skill.lumen-upgrade exited $rc: $out"
    [[ -f "$P/.claude/skills/lumen-upgrade/SKILL.md" ]] \
        || fail "PLACED_SKILL_IS_A_ROUTABLE_NODE: no .claude/skills/lumen-upgrade/SKILL.md projection"
    want="library-corpus/maven/lumen-core docs/graph/libraries/lumen-core.md $(sha_of "$P/docs/graph/libraries/lumen-core.md")
library-corpus/platform/cloud-cli docs/graph/libraries/cloud-cli.md $(sha_of "$P/docs/graph/libraries/cloud-cli.md")
skill-corpus/maven/lumen-upgrade docs/graph/skills/lumen-upgrade.md $(sha_of "$P/docs/graph/skills/lumen-upgrade.md")
tool-corpus/ops/orbit-form-linter docs/graph/tools/orbit-form-linter.md $(sha_of "$P/docs/graph/tools/orbit-form-linter.md")"
    got="$(expertise_record "$P" 2>&1)" || fail "EXPERTISE_IS_RECORDED_IN_THE_STAMP: the stamp has no readable expertise key: $got"
    [[ "$got" == "$want" ]] || fail "EXPERTISE_IS_RECORDED_IN_THE_STAMP: the record reads
$got
and should read
$want"
    [[ "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$P/.cypress/seed.json")" == "$V" ]] \
        || fail "PLACED_PAGE_CARRIES_ITS_PROVENANCE: the stamp's version is not the provenance version $V"
    echo "  M16 EXPERTISE_PLACES_ONLY_THE_CONFIRMED_LIST: four confirmed pages placed with provenance, the skill routable and projected, the record exact — OK"
}

# M17, SPEC-0001 UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING, with the architect's
# condition: a listed id whose destination a different recorded id owns.
case_expertise_refused() {
    local P="$WORK/xp-refused" out rc before bad
    fresh_plant "$P"
    before="$(tree_sig "$P")"
    for bad in library-corpus/maven/lumen-cor legal-corpus/eu/gdpr agent-corpus/roles/tester \
               library-corpus/../legal-corpus/README /etc/passwd skill-corpus/generic-procedure \
               "library-corpus/pypi/swift-cache,library-corpus/container/swift-cache" \
               skill-corpus/maven/test-first library-corpus/npm/index; do
        rc=0; out="$("$ESEED/install.sh" claude-code --expertise "library-corpus/maven/lumen-core,$bad" --project-dir "$P" 2>&1)" || rc=$?
        [[ $rc -ne 0 ]] || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: '$bad' was not refused"
        grep -qF -- "${bad##*,}" <<<"$out" || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: the refusal of '$bad' does not name it: $out"
        grep -q "Traceback" <<<"$out" && fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: '$bad' raised a Python error: $out"
        [[ "$(tree_sig "$P")" == "$before" ]] || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: refusing '$bad' changed the target"
    done
    "$ESEED/install.sh" claude-code --expertise library-corpus/pypi/swift-cache --project-dir "$P" >/dev/null 2>&1 \
        || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: placing library-corpus/pypi/swift-cache failed"
    before="$(tree_sig "$P")"
    rc=0; out="$("$ESEED/install.sh" claude-code --expertise library-corpus/container/swift-cache --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -ne 0 ]] || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: an id whose destination a recorded id owns was not refused: $out"
    grep -qF "library-corpus/container/swift-cache" <<<"$out" \
        || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: the recorded-destination refusal does not name the id: $out"
    [[ "$(tree_sig "$P")" == "$before" ]] \
        || fail "UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: the recorded-destination refusal changed the plant"
    echo "  M17 UNKNOWN_EXPERTISE_ID_REFUSED_BEFORE_WRITING: ten bad lists refused by name with the target unchanged — OK"
}

# M18, SPEC-0001 EXPERTISE_SURVIVES_SILENCE and RECORDED_EXPERTISE_PAGE_WITHDRAWN,
# with IDENTICAL_RERUN_IS_INERT, UNKNOWN_STAMP_KEYS_SURVIVE and the audit clause
# of PLACED_PAGE_CARRIES_ITS_PROVENANCE over the refreshed page's backup.
case_expertise_silence() {
    local S="$WORK/xp-silence-seed" P="$WORK/xp-silence" out rc rec baks
    make_seed "$S"; fresh_plant "$P"
    "$S/install.sh" claude-code --project-dir "$P" \
        --expertise library-corpus/maven/lumen-core,library-corpus/npm/orbit-forms,skill-corpus/maven/lumen-upgrade >/dev/null 2>&1 \
        || fail "EXPERTISE_SURVIVES_SILENCE: the placing install failed"
    python3 - "$P/.cypress/seed.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8")); d["owner_note"] = {"kept": True}
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2) + "\n")
PY
    rec="$(expertise_record "$P")"
    "$S/install.sh" claude-code --project-dir "$P" >/dev/null 2>&1 || fail "EXPERTISE_SURVIVES_SILENCE: the silent re-run failed"
    baks="$(find "$P" -name '*.bak-*' | sed "s|^$P/||")"
    [[ -z "$baks" ]] || fail "IDENTICAL_RERUN_IS_INERT: the silent re-run made backups: $baks"
    [[ "$(expertise_record "$P")" == "$rec" ]] || fail "EXPERTISE_SURVIVES_SILENCE: the silent re-run changed the record"
    python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); k=list(d); assert d["owner_note"]=={"kept":True} and k[-1]=="owner_note" and k.index("expertise")<k.index("owner_note"), k' \
        "$P/.cypress/seed.json" || fail "UNKNOWN_STAMP_KEYS_SURVIVE: the unknown key did not survive after the expertise key"
    printf '\nA newer layer of the corpus page.\n' >> "$S/library-corpus/npm/orbit-forms.md"
    rc=0; out="$("$S/install.sh" claude-code --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "EXPERTISE_SURVIVES_SILENCE: the re-run over a newer corpus page exited $rc: $out"
    tail -1 "$P/docs/graph/libraries/orbit-forms.md" | grep -q "A newer layer" \
        || fail "EXPERTISE_SURVIVES_SILENCE: the newer corpus page was not placed"
    compgen -G "$P/docs/graph/libraries/orbit-forms.md.bak-*" >/dev/null \
        || fail "EXPERTISE_SURVIVES_SILENCE: the refreshed page left no backup"
    compgen -G "$P/docs/graph/libraries/lumen-core.md.bak-*" >/dev/null \
        && fail "EXPERTISE_SURVIVES_SILENCE: an unchanged page was backed up"
    grep -q "^library-corpus/npm/orbit-forms docs/graph/libraries/orbit-forms.md $(sha_of "$P/docs/graph/libraries/orbit-forms.md")$" \
        <<<"$(expertise_record "$P")" || fail "EXPERTISE_SURVIVES_SILENCE: the refreshed page's recorded hash was not updated"
    rc=0; out="$(python3 "$S/tools/graft-audit.py" "$P" "$S" 2>&1)" || rc=$?
    grep -q "'CORPUS-PLACED': 1" <<<"$out" \
        || fail "PLACED_PAGE_CARRIES_ITS_PROVENANCE: graft-audit does not classify the refreshed page's backup corpus-placed: $out"
    grep -q -e "UNMAPPED backup" -e "knowledge overwrite" <<<"$out" \
        && fail "PLACED_PAGE_CARRIES_ITS_PROVENANCE: graft-audit reads the corpus-placed backup as unmapped or plant knowledge: $out"
    rm "$P/docs/graph/libraries/lumen-core.md"
    rc=0; out="$("$S/install.sh" claude-code --project-dir "$P" 2>&1)" || rc=$?
    [[ -f "$P/docs/graph/libraries/lumen-core.md" ]] || fail "EXPERTISE_SURVIVES_SILENCE: a deleted recorded page was not placed again"
    grep -q "docs/graph/libraries/lumen-core.md" <<<"$out" \
        || fail "EXPERTISE_SURVIVES_SILENCE: the re-placed page is not named in the log: $out"
    rec="$(expertise_record "$P")"
    local page_sig; page_sig="$(sha_of "$P/docs/graph/libraries/orbit-forms.md")"
    rm "$S/library-corpus/npm/orbit-forms.md"
    rc=0; out="$("$S/install.sh" claude-code --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "RECORDED_EXPERTISE_PAGE_WITHDRAWN: a plain install exited $rc after the warning: $out"
    grep -q "WARNING.*library-corpus/npm/orbit-forms" <<<"$out" \
        || fail "RECORDED_EXPERTISE_PAGE_WITHDRAWN: no WARNING names the withdrawn id: $out"
    [[ "$(sha_of "$P/docs/graph/libraries/orbit-forms.md")" == "$page_sig" && "$(expertise_record "$P")" == "$rec" ]] \
        || fail "RECORDED_EXPERTISE_PAGE_WITHDRAWN: the placed page or its record entry changed"
    rm "$P/docs/graph/libraries/orbit-forms.md"
    rc=0; out="$("$S/install.sh" claude-code --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 && ! -e "$P/docs/graph/libraries/orbit-forms.md" && "$(expertise_record "$P")" == "$rec" ]] \
        || fail "RECORDED_EXPERTISE_PAGE_WITHDRAWN: a withdrawn page the plant deleted was not left absent with its entry kept (exit $rc): $out"
    rc=0; out="$("$S/install.sh" claude-code --check --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -ne 0 ]] && grep -q "WARNING.*library-corpus/npm/orbit-forms" <<<"$out" \
        || fail "RECORDED_EXPERTISE_PAGE_WITHDRAWN: --check did not name the withdrawn id and exit non-zero (exit $rc): $out"
    echo "  M18 EXPERTISE_SURVIVES_SILENCE: silence refreshes, re-places and keeps the record; a withdrawn page warns and is left — OK"
}

# M19, SPEC-0001 PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED and PLANT_OWNED_PAGE_IS_NEVER_REPLACED
case_expertise_plant_edits() {
    local P="$WORK/xp-edits" out rc rec page=docs/graph/libraries/lumen-core.md sig flag
    fresh_plant "$P"
    "$ESEED/install.sh" claude-code --expertise library-corpus/maven/lumen-core --project-dir "$P" >/dev/null 2>&1 \
        || fail "PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: the placing install failed"
    printf '\nThe plant observed this on its own build.\n' >> "$P/$page"
    sig="$(sha_of "$P/$page")"; rec="$(expertise_record "$P")"
    for flag in "" "--expertise library-corpus/maven/lumen-core"; do
        rc=0; out="$("$ESEED/install.sh" claude-code $flag --project-dir "$P" 2>&1)" || rc=$?
        [[ $rc -eq 0 ]] || fail "PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: the re-run '$flag' exited $rc: $out"
        [[ "$(sha_of "$P/$page")" == "$sig" ]] || fail "PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: the edited page was rewritten ('$flag')"
        compgen -G "$P/$page.bak-*" >/dev/null && fail "PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: a backup was made beside the edited page ('$flag')"
        grep -q "$page.*graft Phase 4" <<<"$out" || fail "PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: no line names $page and graft Phase 4 ('$flag'): $out"
        [[ "$(expertise_record "$P")" == "$rec" ]] || fail "PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: the record entry changed ('$flag')"
    done
    printf '# ripple\n\nThe plant ingested this page itself.\n' > "$P/docs/graph/libraries/ripple.md"
    sig="$(sha_of "$P/docs/graph/libraries/ripple.md")"
    rc=0; out="$("$ESEED/install.sh" claude-code --expertise library-corpus/npm/ripple,library-corpus/npm/orbit-forms --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "PLANT_OWNED_PAGE_IS_NEVER_REPLACED: the install exited $rc: $out"
    [[ "$(sha_of "$P/docs/graph/libraries/ripple.md")" == "$sig" ]] || fail "PLANT_OWNED_PAGE_IS_NEVER_REPLACED: the plant's page was replaced"
    compgen -G "$P/docs/graph/libraries/ripple.md.bak-*" >/dev/null && fail "PLANT_OWNED_PAGE_IS_NEVER_REPLACED: a backup was made beside the plant's page"
    grep -q "docs/graph/libraries/ripple.md.*graft Phase 4" <<<"$out" \
        || fail "PLANT_OWNED_PAGE_IS_NEVER_REPLACED: no line names the plant's page and graft Phase 4: $out"
    rec="$(expertise_record "$P")"
    grep -q "npm/ripple" <<<"$rec" && fail "PLANT_OWNED_PAGE_IS_NEVER_REPLACED: a record entry was written for the plant's page"
    grep -q "^library-corpus/npm/orbit-forms " <<<"$rec" && [[ -f "$P/docs/graph/libraries/orbit-forms.md" ]] \
        || fail "PLANT_OWNED_PAGE_IS_NEVER_REPLACED: the other id in the list was not placed and recorded"
    echo "  M19 PLANT_EDITED_PAGE_IS_LEFT_AND_NAMED: an edited page and a plant-owned page are left, named, unrecorded changes none — OK"
}

# M20, SPEC-0001 EXPERTISE_CHECK_NAMES_MISSING_OR_STALE
case_expertise_check() {
    local S="$WORK/xp-check-seed" P="$WORK/xp-check" N="$WORK/xp-check-none" out rc before
    make_seed "$S"; fresh_plant "$P"; fresh_plant "$N"
    "$S/install.sh" claude-code --project-dir "$N" >/dev/null 2>&1 || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: the plain install failed"
    rc=0; out="$("$S/install.sh" claude-code --check --project-dir "$N" 2>&1)" || rc=$?
    grep -qi "expertise" <<<"$out" && fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: a plant with no expertise key got an expertise line: $out"
    "$S/install.sh" claude-code --expertise library-corpus/maven/lumen-core,library-corpus/npm/orbit-forms --project-dir "$P" >/dev/null 2>&1 \
        || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: the placing install failed"
    before="$(tree_sig "$P")"
    rc=0; out="$("$S/install.sh" claude-code --check --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] && grep -q "expertise pages are up to date" <<<"$out" \
        || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: a current plant did not pass with the up-to-date line (exit $rc): $out"
    printf '\nA newer layer.\n' >> "$S/library-corpus/maven/lumen-core.md"
    rm "$P/docs/graph/libraries/orbit-forms.md"
    before="$(tree_sig "$P")"
    rc=0; out="$("$S/install.sh" claude-code --check --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -ne 0 ]] || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: a stale and a missing page passed --check: $out"
    grep -q "docs/graph/libraries/lumen-core.md.*stale" <<<"$out" || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: the stale page is not named: $out"
    grep -q "docs/graph/libraries/orbit-forms.md.*missing" <<<"$out" || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: the missing page is not named: $out"
    [[ "$(tree_sig "$P")" == "$before" ]] || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: --check changed the plant"
    "$S/install.sh" claude-code --project-dir "$P" >/dev/null 2>&1 || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: the refreshing install failed"
    printf '\nA plant edit.\n' >> "$P/docs/graph/libraries/lumen-core.md"
    rc=0; out="$("$S/install.sh" claude-code --check --project-dir "$P" 2>&1)" || rc=$?
    [[ $rc -eq 0 ]] || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: a plant-edited page alone failed --check (exit $rc): $out"
    grep -q "docs/graph/libraries/lumen-core.md.*graft Phase 4" <<<"$out" \
        || fail "EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: the plant-edited page is not named for graft Phase 4: $out"
    echo "  M20 EXPERTISE_CHECK_NAMES_MISSING_OR_STALE: --check names a stale, a missing and an edited page, writing nothing — OK"
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

# M11 (SPEC-0003 EVERY_RESOLVER_PATH_IS_INSTALLED): every path a route resolver
# may SELECT is a path the installer writes.
# The plant-root walk lives in the Python cores alone, so their candidates are
# read from route-hook.py CANDIDATES and status-hook.py CANDIDATES and
# ANCHOR_CANDIDATES; each Prime Agent extension walks nothing and
# runs the core at `path.join(__dirname, "..", "hooks", <script>)`, read from
# the PLACED extension and resolved against its placed directory. The reader
# runs as a plain command substitution, so its own failure fails the gate.
m11_paths="$(python3 - "$ROOT" "$T" <<'PY'
import re, sys
from pathlib import Path

root, target = Path(sys.argv[1]), Path(sys.argv[2])
seen = []
# The CANDIDATES rule (route-hook.py) binds every candidate list a core walks
# for: route-hook.py's linter, status-hook.py's register and its code anchor.
for script, names in (("route-hook.py", ("CANDIDATES",)),
                      ("status-hook.py", ("CANDIDATES", "ANCHOR_CANDIDATES"))):
    hook = (root / "integrations/claude-code" / script).read_text(encoding="utf-8")
    for name in names:
        m = re.search(rf"^{name}\s*=\s*\((.*?)\)\s*$", hook, re.M | re.S)
        if not m:
            sys.exit(f"{script}: no {name} list to read — the check would assert nothing")
        paths = ["/".join(re.findall(r'"([^"]+)"', el)) for el in re.findall(r"[^,]+", m.group(1))]
        paths = [p for p in paths if p]
        if not paths:
            sys.exit(f"{script} {name} yielded no path — a vacuous pass")
        seen.extend(p for p in paths if p not in seen)
ext_dir = Path(".prime/agent/extensions")
for name in ("route-extension.ts", "status-extension.ts"):
    placed = target / ext_dir / name
    if not placed.is_file():
        sys.exit(f"{ext_dir / name} was not placed — the check would assert nothing")
    src = placed.read_text(encoding="utf-8")
    if not re.search(r'path\.join\(\s*__dirname\s*,\s*"\.\."\s*,\s*"hooks"\s*\)', src):
        sys.exit(f"{ext_dir / name} does not locate its core at `path.join(__dirname, \"..\", \"hooks\")`")
    scripts = re.findall(r'path\.join\(\s*dir\s*,\s*"([^"]+\.py)"\s*\)', src)
    if len(scripts) != 1:
        sys.exit(f"{ext_dir / name} names {scripts} as its core script, not exactly one")
    seen.append((ext_dir.parent / "hooks" / scripts[0]).as_posix())
print("\n".join(seen))
PY
)" || fail "could not read the route resolvers' candidate paths (the reason is above)"
stray_candidates=()
while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    [[ -e "$T/$rel" || -L "$T/$rel" ]] || stray_candidates+=("$rel")
done <<< "$m11_paths"
if [[ ${#stray_candidates[@]} -gt 0 ]]; then
    echo "M11 VIOLATED — ${#stray_candidates[@]} resolver candidate(s) no install produces:" >&2
    printf '  %s\n' "${stray_candidates[@]}" >&2
    fail "a resolver may select a path the installer never writes"
fi
echo "  M11 EVERY_RESOLVER_PATH_IS_INSTALLED: every route-resolver path ($(grep -c . <<< "$m11_paths")) is a path the installer writes — OK"

# The selective-placement seed: a copy of this seed carrying the synthetic corpus.
ESEED="$WORK/expertise-seed"
make_seed "$ESEED"

export BASE BASECOPILOT ESEED
SCN="$(mktemp)"
for c in case_recover case_symchurn case_m2 case_m4 case_m8 case_m10 case_cond case_hook_check case_retired_flag case_orphan_flag \
         case_expertise_propose case_expertise_place case_expertise_refused case_expertise_silence \
         case_expertise_plant_edits case_expertise_check; do
    printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"
[ "$rc" -eq 0 ] || { echo "install-placement: FAIL — a planted scenario did not pass" >&2; exit "$rc"; }

echo "install-placement: OK — ${#FILES[@]} destinations plus ${#COND_FILES[@]} conditional ones recoverable, symlink-safe, idempotent, link-uniform, audit-classifiable, target-contained"
