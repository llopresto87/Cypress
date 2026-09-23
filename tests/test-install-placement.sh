#!/usr/bin/env bash
# Destination-placement contract: EVERY byte install.sh puts into a target
# goes through one canonical writer, so every destination is recoverable,
# symlink-safe, idempotent and auditable.
#
# The destination set is DISCOVERED from a real install rather than listed
# here. A hardcoded list is exactly how this class of defect survived: the
# installer grew destinations (four bare `cp`s, a `cat >`, a `sed >`, three
# embedded-Python `open(..., "w")` writes) that no list was updated to cover.
# Discovering the set means a destination added tomorrow is held to the same
# contract without anyone remembering to add it here.
#
# Invariants pinned (docs/plans/grill-7.15.0-remediation.md):
#   M2  a destination symlink never authorizes a write to its referent
#   M3  identical reruns are idempotent — no backup churn
#   M7  every written file is recoverable from a timestamped sibling
#       unless byte-identical to what replaced it
#   M9  under --symlink every placed file is a link or a recorded exception
#   M10 no write escapes PROJECT_DIR, by any writer, through any symlink
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Every host the installer can place, named explicitly (ADR-0009). A call that
# exists to cover the complete destination set, or that asserts a frozen host's
# files, installs these five by name so the frozen adapters stay under
# regression; `all` names only the maintained hosts. Unquoted at each call on
# purpose: it word-splits into five positional tool arguments.
EVERY_HOST="claude-code opencode codex github-copilot prime-agent"
WORK="$(mktemp -d)"
trap 'chmod -R u+w "$WORK" 2>/dev/null; rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# The installer's OWN derived state (place_state): a fresh `installed_at` every
# run means it is never byte-identical, so backing it up would leave one .bak
# per install for ever, and the next stamp is derived from this one rather than
# authored, so a backup carries no recovery value. The one recorded M7
# exception — it is still replaced atomically and still symlink-safe.
is_installer_state() {
    [[ "$1" == ".cypress/seed.json" ]]
}

# Destinations the installer places ONCE and the plant then owns: scaffold
# leaves, the graph engines reconciled by graft-graph-engine.py, and the
# router index. They are add-if-missing by design, so a plant edit SURVIVES a
# re-run (rather than being replaced-with-backup), and they are copies even
# under --symlink because a plant-owned file must not be a link into the seed.
# This is the M9 exception list; anything else claiming exception is a defect.
is_plant_owned() {
    local rel="$1"
    case "$rel" in
        docs/graph/_schema.md|docs/graph/index.md) return 0 ;;
        docs/graph/graph-lint.py|docs/graph/spec-lint.py|docs/graph/grill-lint.py) return 0 ;;
    esac
    # every templates/docs/** leaf is mirrored into docs/graph/ add-if-missing
    [[ -e "$ROOT/templates/docs/${rel#docs/graph/}" ]] && return 0
    return 1
}

# Content GENERATED per target (place_generated): slash commands, the
# transformed Copilot views, the Codex snippet. It has no seed original, so
# under --symlink there is nothing to link to and it is correctly a real file.
is_generated() {
    case "$1" in
        .claude/commands/*|.opencode/commands/*|.prime/agent/prompts/*) return 0 ;;
        .github/agents/*|.github/prompts/*|.github/instructions/*)      return 0 ;;
        .codex/codex-config-snippet.toml)                               return 0 ;;
    esac
    return 1
}

# placed_files DIR -> every regular file the installer put in DIR, target-relative.
# Backups and the transient growth scratch are not placements.
placed_files() {
    ( cd "$1" && find . -type f \
        -not -name '*.bak-*' -not -path './.cypress/growth/*' \
        -not -name '*.pyc' -not -path '*/__pycache__/*' \
        | sed 's|^\./||' | sort )
}

SELF="$ROOT/tests/test-install-placement.sh"

# Load FILES from an '$EVERY_HOST --copy --legal-corpus yes' tree (read-only discovery),
# so a case running in its own process re-derives the same set main did.
load_files() {
    FILES=(); while IFS= read -r _l; do FILES+=("$_l"); done < <(placed_files "$1")
}
# Load COND_FILES (the conditional destinations) from a 'github-copilot --copy'
# tree; FILES must already be loaded so the shared set can be subtracted.
load_cond() {
    COND_FILES=()
    while IFS= read -r _l; do
        case " ${FILES[*]} " in *" $_l "*) ;; *) COND_FILES+=("$_l") ;; esac
    done < <(placed_files "$1")
}

# ---------------------------------------------------------------------------
# M7 + M3: recoverability and idempotence over the COMPLETE destination set.
# Asserts SPEC-0001 SINGLE_WRITER (the recoverability half), SPEC-0001
# BACKUP_BEFORE_REPLACE, SPEC-0001 IDENTICAL_RERUN_IS_INERT.
# ---------------------------------------------------------------------------
case_recover() {
    local T; T="$WORK/recover"; mkdir -p "$T"
    "$ROOT/install.sh" $EVERY_HOST --project-dir "$T" --copy --legal-corpus yes >/dev/null 2>&1 \
        || fail "baseline install \$EVERY_HOST --copy did not succeed"
    FILES=(); while IFS= read -r _l; do FILES+=("$_l"); done < <(placed_files "$T")
    [[ ${#FILES[@]} -gt 100 ]] || fail "discovered only ${#FILES[@]} placed files — discovery is broken"
# M3 first: an identical re-run must not churn a single backup.
"$ROOT/install.sh" $EVERY_HOST --project-dir "$T" --copy --legal-corpus yes >/dev/null 2>&1 \
    || fail "idempotent re-run did not succeed"
# Name the churned files, never just count them. An idempotence failure that
# reports only a number is unreproducible by construction: it was observed once
# during the 7.15.0 audit and could not be pinned down afterwards because
# nothing recorded WHICH file churned.
CHURN=(); while IFS= read -r _l; do CHURN+=("$_l"); done \
    < <(find "$T" -name '*.bak-*' | sed "s|^$T/||" | sort)
if [[ ${#CHURN[@]} -gt 0 ]]; then
    echo "M3 VIOLATED — an identical re-run backed up ${#CHURN[@]} file(s):" >&2
    printf '  %s\n' "${CHURN[@]}" >&2
    fail "backup churn buries the graft-audit signal under no-op .bak entries"
fi
# Now mark every placed file and re-run once. Symlinks are skipped: appending
# through one would write into the seed, and link placement is M9's business.
SENTINEL='CYPRESS-PLANT-SENTINEL-DO-NOT-LOSE'
marked=0
for rel in "${FILES[@]}"; do
    [[ -L "$T/$rel" ]] && continue
    # ...but never the installer's own derived state. A `# SENTINEL` line makes
    # .cypress/seed.json unparseable, and the installer now REFUSES to re-derive
    # an unreadable stamp that names owner decisions rather than silently
    # resetting them to defaults — which is the fix for a real data-loss defect
    # (a recorded `legal_corpus: yes` became `undecided` with 16 corpus pages on
    # disk). Marking it here was never testing anything: the recovery branch 40
    # lines below already skips it as the one recorded exception to
    # recoverability, so the sweep only ever corrupted it and threw the result
    # away.
    is_installer_state "$rel" && continue
    # Marked at the HEAD as well as the tail. An appended-only sentinel is the
    # part any tail-truncation preserves: replacing place_file's `mv` with
    # `tail -2 "$dest" > "$bak"; rm -f "$dest"` left a 194-line node's backup
    # holding 2 lines and this suite still printed "387 destinations
    # recoverable". A backup that kept 1% of the body is not a recovery.
    printf '# %s\n%s' "$SENTINEL" "$(cat "$T/$rel")" > "$T/$rel.marked" \
        && mv "$T/$rel.marked" "$T/$rel"
    printf '\n# %s\n' "$SENTINEL" >> "$T/$rel" && marked=$((marked + 1))
done
[[ "$marked" -gt 100 ]] || fail "marked only $marked files — the sweep is not covering the install"

"$ROOT/install.sh" $EVERY_HOST --project-dir "$T" --copy --legal-corpus yes >"$WORK/m7-rerun.log" 2>&1 \
    || { tail -25 "$WORK/m7-rerun.log" >&2; fail "re-run over a customized plant did not succeed"; }

lost=(); unmaintained=(); unrecoverable=()
for rel in "${FILES[@]}"; do
    [[ -L "$T/$rel" ]] && continue
    if grep -q "$SENTINEL" "$T/$rel" 2>/dev/null; then
        # Edit intact. Correct ONLY for the add-if-missing set. For anything
        # else it means the installer silently stopped maintaining a file it
        # owns, which is a defect this sweep is the only thing positioned to
        # notice — and it went unnoticed, because this branch used to read
        # `is_plant_owned "$rel" || true` and then `continue` regardless. The
        # comment described a check the code did not perform: patching
        # place_file to skip one machinery file left the whole suite green.
        if ! is_plant_owned "$rel"; then
            unmaintained+=("$rel")
        fi
        continue
    fi
    # Replaced. M7 demands the previous body be RECOVERABLE beside it, and
    # `compgen -G` only ever proved a NAME exists. Replacing place_file's
    # `mv "$dest" "$bak"` with `: > "$bak"; rm -f "$dest"` — every replaced
    # body destroyed, a zero-byte backup left in its place — kept this suite
    # green and printed "387 destinations recoverable". The sentinel is the
    # only thing that makes recovery checkable: it was in the body before the
    # re-run, so it must be in the backup after it.
    is_installer_state "$rel" && continue
    if ! compgen -G "$T/$rel.bak-*" >/dev/null; then
        lost+=("$rel")
    elif [[ "$(grep -cs "$SENTINEL" "$T/$rel".bak-* | awk -F: '{s+=$NF} END {print s+0}')" -lt 2 ]]; then
        # BOTH ends, so a truncation from either direction is caught.
        unrecoverable+=("$rel")
    fi
done

if [[ ${#unrecoverable[@]} -gt 0 ]]; then
    echo "M7 VIOLATED — ${#unrecoverable[@]} destination(s) have a .bak-* that does" >&2
    echo "NOT carry the body it replaced, so the backup is a name and not a" >&2
    echo "recovery. The plant edit is gone:" >&2
    printf '  %s\n' "${unrecoverable[@]}" >&2
    fail "a backup must carry the previous body, not merely exist"
fi

if [[ ${#unmaintained[@]} -gt 0 ]]; then
    echo "M1 VIOLATED — ${#unmaintained[@]} seed-owned destination(s) kept a plant" >&2
    echo "edit through a re-install, so the installer has silently stopped" >&2
    echo "maintaining them (they are not in the add-if-missing exception list):" >&2
    printf '  %s\n' "${unmaintained[@]}" >&2
    fail "a destination the seed owns must be fast-forwarded, not abandoned"
fi

if [[ ${#lost[@]} -gt 0 ]]; then
    echo "M7 VIOLATED — ${#lost[@]} destination(s) replaced a plant edit with NO recoverable backup:" >&2
    printf '  %s\n' "${lost[@]}" >&2
    fail "every installer destination must be recoverable (one canonical writer)"
fi
}

case_symchurn() {
# ...and again under --symlink, because this check ran only in copy mode and a
# real churn bug lived in the other one: `place_kernel` decided which of
# CLAUDE.md/AGENTS.md held the kernel by testing for a plain regular file, which
# is never true under --symlink, so each of the five adapters claimed its own
# destination and the pair flipped back and forth. Backups grew 1, 3, 5 on
# successive identical re-runs while the CONTENT stayed byte-identical — a
# defect only `ls -la` could see, and one an all-copy test never could.
SYM="$WORK/idem-symlink"; mkdir -p "$SYM"
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
}

case_m2() {
    load_files "$BASE"
# ---------------------------------------------------------------------------
# M2: a destination symlink must never authorize a write to its referent.
# Asserts SPEC-0001 SYMLINK_IS_REPLACED_NOT_FOLLOWED.
# ---------------------------------------------------------------------------
A="$WORK/attack"; OUT="$WORK/outside"; mkdir -p "$A" "$OUT"
for rel in "${FILES[@]}"; do
    victim="$OUT/$(printf '%s' "$rel" | tr '/' '_')"
    printf 'PRECIOUS-REFERENT %s\n' "$rel" > "$victim"
    mkdir -p "$A/$(dirname "$rel")"
    ln -s "$victim" "$A/$rel"
done
# The contract says the referent is UNCHANGED; grepping for one line only ever
# said a line SURVIVED. Appending through every destination symlink modified
# 355 files outside --project-dir and this suite still printed "symlink-safe,
# target-contained" and exited 0. A digest taken before the attack is what
# makes "unchanged" checkable.
( cd "$OUT" && find . -type f | sort | xargs cksum ) > "$WORK/victims.before"

# The attack has to REACH every destination before "no victim was clobbered"
# means anything. It did not: the installer refuses a symlink that leaves the
# target when it writes the plant facts, exits 1, and `|| true` swallowed it —
# so 382 of 387 destinations kept the attacker's link, were never written at
# all, and the sweep below reported green over five of them.
#
# Refusing is compliant: it is the other safe answer to a hostile destination.
# So refusals are recorded, the blocked link is replaced with a real file, and
# the install is re-run until it completes, which is what exercises the rest.
# An abort for any OTHER reason is a failure, not a lap of this loop.
refused=()
attempts=0
while :; do
    attempts=$((attempts + 1))
    "$ROOT/install.sh" $EVERY_HOST --project-dir "$A" --copy --legal-corpus yes >"$WORK/m2.log" 2>&1 && break
    [[ $attempts -le 40 ]] || fail "M2: the installer never completed against a hostile target in $attempts attempts"
    # `|| true`: under `set -o pipefail` a non-matching grep makes the whole
    # assignment exit 1, and `set -e` kills the script HERE — before the branch
    # below that prints the log and says why. The guard that this loop depends
    # on could never fire; CI saw a naked exit 1 and an empty log.
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

clobbered=()
for rel in "${FILES[@]}"; do
    victim="$OUT/$(printf '%s' "$rel" | tr '/' '_')"
    grep -q "PRECIOUS-REFERENT $rel" "$victim" 2>/dev/null || clobbered+=("$rel")
done

( cd "$OUT" && find . -type f | sort | xargs cksum ) > "$WORK/victims.after"
if ! diff -q "$WORK/victims.before" "$WORK/victims.after" >/dev/null; then
    echo "M2 VIOLATED — the referents outside the target are not byte-identical" >&2
    echo "after the install. A destination symlink was followed, or a file was" >&2
    echo "appended to rather than replaced:" >&2
    diff "$WORK/victims.before" "$WORK/victims.after" >&2 || true
    fail "an install must not modify any file outside --project-dir"
fi
# The digest above proves nothing if the attack never created any victims.
[[ $(wc -l < "$WORK/victims.before") -eq ${#FILES[@]} ]] \
    || fail "M2: digested $(wc -l < "$WORK/victims.before") referents for ${#FILES[@]} destinations — the sweep is not covering the attack"

if [[ ${#clobbered[@]} -gt 0 ]]; then
    echo "M2 VIOLATED — ${#clobbered[@]} destination(s) were written THROUGH a symlink," >&2
    echo "modifying a file OUTSIDE the target directory:" >&2
    printf '  %s\n' "${clobbered[@]}" >&2
    fail "a destination symlink must be replaced as a link object, never followed"
fi

# Coverage, asserted rather than assumed. Every destination must end in exactly
# one of three states, and the unexplained state is the finding: a destination
# still holding the attacker's link that is NOT add-if-missing was skipped, and
# a skipped destination proves nothing about following a symlink.
was_refused() { local r; for r in ${refused[@]+"${refused[@]}"}; do [[ "$r" == "$1" ]] && return 0; done; return 1; }
replaced=0; skipped=()
for rel in "${FILES[@]}"; do
    was_refused "$rel" && continue
    if [[ -L "$A/$rel" ]]; then
        is_plant_owned "$rel" || skipped+=("$rel")
    else
        replaced=$((replaced + 1))
    fi
done

if [[ ${#skipped[@]} -gt 0 ]]; then
    echo "M2 VIOLATED — ${#skipped[@]} destination(s) still hold the attacker's" >&2
    echo "symlink and are not add-if-missing, so the attack never reached them:" >&2
    printf '  %s\n' "${skipped[@]}" >&2
    fail "M2 must exercise every destination it reports on"
fi

# A floor, because the three classes above are satisfiable by putting every
# destination in the third one. This number is the size of the set the contract
# is actually tested over; it may rise, and a fall is a coverage regression.
[[ $replaced -ge 300 ]] || fail "M2 exercised only $replaced destinations of ${#FILES[@]} (floor 300, ${#refused[@]} refused)"
echo "  M2: $replaced destinations had the link object replaced, ${#refused[@]} refused, $(( ${#FILES[@]} - replaced - ${#refused[@]} )) add-if-missing"
}

case_m9() {
# ---------------------------------------------------------------------------
# M9: under --symlink every placed file is a link, or a recorded exception.
# Asserts SPEC-0001 SYMLINK_MODE_IS_UNIFORM.
# ---------------------------------------------------------------------------
S="$WORK/linked"; mkdir -p "$S"
"$ROOT/install.sh" $EVERY_HOST --project-dir "$S" --symlink >/dev/null 2>&1 \
    || fail "install \$EVERY_HOST --symlink did not succeed"

not_linked=()
while IFS= read -r rel; do
    [[ -L "$S/$rel" ]] && continue
    is_plant_owned "$rel" && continue
    is_installer_state "$rel" && continue
    is_generated "$rel" && continue
    not_linked+=("$rel")
done < <(placed_files "$S")

if [[ ${#not_linked[@]} -gt 0 ]]; then
    echo "M9 VIOLATED — ${#not_linked[@]} file(s) placed as copies under --symlink" >&2
    echo "and not in the recorded add-if-missing exception list:" >&2
    printf '  %s\n' "${not_linked[@]}" >&2
    fail "--symlink must place links, or the exception must be recorded in is_plant_owned()"
fi
}

case_m4() {
# ---------------------------------------------------------------------------
# M4: --force suppresses the per-file WARNING and never the backup.
# Asserts SPEC-0001 FORCE_SUPPRESSES_WARNING_NOT_BACKUP.
#
# The help text used to promise "without prompting" for a prompt that never
# existed, and that folklore had since been IMPLEMENTED: place_kernel's sibling
# branch skipped the backup under --force. So the one flag a steward reaches for
# when re-installing over a customized plant was the flag that destroyed the
# body it was about to replace, leaving graft-audit nothing to classify.
# ---------------------------------------------------------------------------
F="$WORK/forced"; mkdir -p "$F"
"$ROOT/install.sh" claude-code --project-dir "$F" --copy >/dev/null 2>&1 \
    || fail "M4 baseline install failed"
printf '\n# PLANT EDIT UNDER FORCE\n' >> "$F/.claude/settings.json"
printf '# a deliberate kernel deviation\n' >> "$F/CLAUDE.md"
# The sibling kernel file is the site that actually regressed; make it a real
# file carrying its own body so the sibling branch has something to lose.
rm -f "$F/AGENTS.md"; printf '# our own AGENTS body\n' > "$F/AGENTS.md"

"$ROOT/install.sh" claude-code --project-dir "$F" --copy --force >/dev/null 2>&1 \
    || fail "M4: --force install failed"

for victim in .claude/settings.json CLAUDE.md AGENTS.md; do
    compgen -G "$F/$victim.bak-*" >/dev/null \
        || fail "M4 VIOLATED: --force replaced $victim with no backup — the flag \
that exists to skip the CHATTER destroyed the only copy of what was there"
done

# The half the title promised and the block did not check. place_kernel's own
# four warning lines ignored --force entirely, and this is the test whose name
# said it would notice: it asserted only that backups existed, and the
# suppression assertion below ran on a different directory and a different file.
# One warning class deliberately outranks --force: the kernel DEVIATION notice,
# which says a recorded deviation on the always-loaded file is gone. That is not
# chatter, and tests/test-unified-graph-install.sh pins it. Everything else —
# "backed up existing X" — is what --force exists to quieten.
forced_warnings="$("$ROOT/install.sh" claude-code --project-dir "$F" --copy --force 2>&1 >/dev/null || true)"
# Two warning classes outrank --force, and both say the same kind of thing:
# something the plant decided is no longer in force. The kernel DEVIATION notice
# ("your recorded deviation is not in the new body") and the adopted-instruction
# notice ("your own instructions were replaced and are not migrated"). Neither
# is "backed up existing X", which is what --force exists to quieten.
forced_chatter="$(grep "WARNING" <<<"$forced_warnings" \
                  | grep -v "OVERWRITTEN" | grep -v "deviation" \
                  | grep -v "previous body" | grep -v "diff the backup" \
                  | grep -v "NOT migrated" | grep -v "adopted-instructions" || true)"
if [[ -n "$forced_chatter" ]]; then
    forced_warnings="$forced_chatter"
    echo "M4: --force still warned on:" >&2
    grep "WARNING" <<<"$forced_warnings" | sed 's/^/  /' >&2
    fail "--force suppresses the per-file warning, on EVERY destination — the \
kernel files included, which are the two a steward is most likely to have edited"
fi

# ...and it really is quieter: the same replacement without --force warns.
G="$WORK/unforced"; mkdir -p "$G"
"$ROOT/install.sh" claude-code --project-dir "$G" --copy >/dev/null 2>&1
printf '\n# edit\n' >> "$G/.claude/settings.json"
warn_out="$("$ROOT/install.sh" claude-code --project-dir "$G" --copy 2>&1 >/dev/null || true)"
grep -q "backed up existing" <<<"$warn_out" \
    || fail "M4: without --force the backup must be announced, and was not"
}

case_m8() {
# ---------------------------------------------------------------------------
# M8: every backup the writer produces is classifiable by graft-audit.py.
# Asserts SPEC-0001 EVERY_BACKUP_IS_CLASSIFIABLE.
# A backup nobody can map to a seed source is a file a steward is told to
# "inspect by hand" with no hint what it should contain — and graft Phase 7
# ratifies on this report, so an unclassifiable row is how a buried
# customization gets ratified.
# ---------------------------------------------------------------------------
AUD="$WORK/audit"; mkdir -p "$AUD"
"$ROOT/install.sh" $EVERY_HOST --project-dir "$AUD" --copy --legal-corpus yes >/dev/null 2>&1 \
    || fail "audit-totality install did not succeed"
while IFS= read -r rel; do
    [[ -L "$AUD/$rel" ]] && continue
    is_installer_state "$rel" && continue
    is_plant_owned "$rel" && continue
    printf '\n# edited by the plant\n' >> "$AUD/$rel"
done < <(placed_files "$AUD")
"$ROOT/install.sh" $EVERY_HOST --project-dir "$AUD" --copy --legal-corpus yes >/dev/null 2>&1 \
    || fail "audit-totality re-run did not succeed"

# The exit code is the contract's **And** — "an unclassifiable backup makes the
# audit exit non-zero rather than report clean". `|| true` discarded it, so an
# audit that printed a plausible report and exited 0 on an UNMAPPED backup
# passed. Captured, asserted, and guarded against the wrong reason below.
# `if var="$(cmd)"` and not `var="$(cmd)"; rc=$?` — under `set -e` a command
# substitution that exits non-zero kills the script AT THE ASSIGNMENT, before
# the next line can read $?. That is how M2's wrong-reason guard became dead
# code, and this file reproduced it in the M8 probe below on the same day the
# other one was fixed. The `if` form is the one that survives `set -e`.
if report="$(python3 "$ROOT/tools/graft-audit.py" "$AUD" "$ROOT" 2>&1)"; then audit_rc=0; else audit_rc=$?; fi
if grep -q "UNMAPPED backup" <<<"$report"; then
    echo "M8 VIOLATED — graft-audit.py cannot classify backups the writer produced:" >&2
    grep -A 20 "UNMAPPED backup" <<<"$report" >&2
    fail "every installer destination must map to a seed source or a named class"
fi
grep -q "backups audited: [1-9]" <<<"$report" \
    || fail "M8: the audit saw no backups at all — it cannot be certifying anything"
# A wrong-reason guard, because the two assertions above are about the REPORT
# and this one is about the EXIT: a clean audit must exit 0, and the run that
# proves the non-zero path is the UNMAPPED branch above, which fails first.
[[ $audit_rc -eq 0 ]] \
    || fail "M8: graft-audit.py exited $audit_rc on a plant whose backups it classified without complaint — the exit and the report disagree"

# ...and the NON-zero path, which had no RED at all. The clean case above only
# ever proved exit 0 when nothing is wrong; the contract's **And** is that an
# unclassifiable backup makes the audit exit non-zero RATHER THAN report clean,
# and nothing exercised it. Verified what that cost: deleting graft-audit.py's
# `return 1` left this suite green while the audit printed BOTH
# "!! 1 UNMAPPED backup(s)" and "clean — no plant knowledge overwritten".
#
# The planted backup sits OUTSIDE docs/graph/ so the knowledge-overwrite branch
# is not what discriminates — the UNMAPPED classification is.
# The audit scopes to ONE date, taken from the newest .bak- stamp it finds, so
# the planted backup has to carry that same date or it is simply out of scope —
# a 1970 stamp made this assertion fail for the wrong reason on its first run.
aud_date="$(find "$AUD" -name '*.bak-*' | sed -n 's/.*\.bak-\([0-9]\{8\}\)-.*/\1/p' | sort | tail -1)"
[[ -n "$aud_date" ]] || fail "M8: no .bak- stamp to derive the audit date from"
unmapped="$AUD/.claude/never-a-seed-file.json.bak-${aud_date}-000000"
printf '{"not":"a seed file"}\n' > "$unmapped"
if unmapped_report="$(python3 "$ROOT/tools/graft-audit.py" "$AUD" "$ROOT" 2>&1)"; then
    unmapped_rc=0
else
    unmapped_rc=$?
fi
rm -f "$unmapped"
[[ $unmapped_rc -ne 0 ]] \
    || fail "M8: graft-audit.py exited 0 over an UNMAPPED backup — the contract says an unclassifiable backup makes it exit non-zero rather than report clean"
grep -q "UNMAPPED" <<<"$unmapped_report" \
    || fail "M8: the audit exited non-zero over an unmapped backup without naming it UNMAPPED — right exit, wrong reason"
echo "  M8: an unclassifiable backup makes the audit exit non-zero, naming it — OK"
}

case_m10() {
# ---------------------------------------------------------------------------
# M10: no write escapes PROJECT_DIR.
# Asserts SPEC-0001 §5's Security NFR and §9 AC-2 — no install modifies a
# file outside --project-dir.
#
# install.sh states the invariant at the top of place_file — "an install cannot
# modify anything outside PROJECT_DIR" — on the strength of `mv` moving the LINK
# OBJECT rather than following it. That argument covers place_file and nothing
# else, and two destinations reached the filesystem by other means:
#
#   1. record_instruction_migration guarded on `[[ ! -e "$note" ]]`. For a
#      DANGLING symlink `-e` is false, so the write branch was taken and
#      `cat >` followed the link, creating the file at the link's target.
#   2. preflight_destinations tested `( -e || -L ) && ! -d`. A symlink TO A
#      DIRECTORY satisfies -e and -d, so nothing flagged it; `mkdir -p`
#      succeeded and every later write went through it. `.cypress` symlinked
#      out put seed.json outside the plant.
#
# Both were found by review and reproduced before they were fixed. A symlink
# that stays INSIDE the target is legitimate and must keep working — the
# invariant is about leaving the target, not about links.
# ---------------------------------------------------------------------------
ESC="$WORK/escape"
OUTSIDE="$ESC/outside"
mkdir -p "$OUTSIDE"

# (1) a dangling symlink at the note path must not be written through
P1="$ESC/plant1"
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

# (2) a destination symlink that leaves the target must be refused BEFORE any write
P2="$ESC/plant2"
mkdir -p "$P2" "$OUTSIDE/realdir"
ln -s "$OUTSIDE/realdir" "$P2/.cypress"
if "$ROOT/install.sh" claude-code --project-dir "$P2" >"$ESC/log2" 2>&1; then
    fail "M10 VIOLATED — an install through a destination symlink leaving the target succeeded"
fi
grep -q "symlink leaving the target" "$ESC/log2" \
    || { cat "$ESC/log2" >&2; fail "M10: refused, but not for the stated reason"; }
[[ -e "$OUTSIDE/realdir/seed.json" ]] \
    && fail "M10 VIOLATED — seed.json landed outside the plant"
[[ -e "$P2/docs" ]] \
    && fail "M10: the refusal was not a preflight — the graph was already on disk"
echo "  M10 (2): a destination symlink leaving the target is refused before the first byte — OK"

# (3) ...and a symlink that stays INSIDE the target still works.
P3="$ESC/plant3"
mkdir -p "$P3/real-cypress"
ln -s "real-cypress" "$P3/.cypress"
"$ROOT/install.sh" claude-code --project-dir "$P3" >/dev/null 2>&1 \
    || fail "M10: an internal destination symlink was refused; the rule is about leaving the target"
[[ -f "$P3/real-cypress/seed.json" ]] \
    || fail "M10: an internal destination symlink did not receive the write"
echo "  M10 (3): a destination symlink that stays inside the target still works — OK"

# (4) ...and the third escape, found by a review that died before reporting it.
# `fill_plant_facts` rewrites docs/graph/index.md IN PLACE — the one destination
# the installer does not reach through place_file — and `Path.write_text()`
# follows a symlink. An index.md linked outside the target had the plant fact
# written into that outside file: exit 0, no warning, and no backup anywhere to
# find it by. Same rule as (2): inside the target is the plant's business,
# leaving it is refused.
P4="$ESC/plant4"
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

# ...and an index.md symlinked INSIDE the target still receives its facts.
P5="$ESC/plant5"
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

# ---------------------------------------------------------------------------
# M10 (6): a symlinked DIRECTORY anywhere under the target, pointing outside it,
# is refused before the first byte — at any depth, whether or not anyone listed
# that path.
#
# preflight_destinations refused these only for the hand-written adapter_dirs()
# list, which stops at one level and names no docs/graph/ subtree. Its deep
# sweep is `find -type d`, which does not follow symlinks, so an escaping link
# was never visited. Pointing docs/graph/protocols at an outside directory
# therefore wrote 14 protocol nodes there, REPLACED a file that was already
# outside, left a .bak outside too, and exited 0 — with this suite green.
# The control is the last case: a link that stays INSIDE the target is the
# plant's own business and must keep working.
# ---------------------------------------------------------------------------
for rel in ".claude/skills/library-wiki" "docs/graph/protocols" "docs/graph/method" \
           "docs/graph/agents" "docs/graph/skills" "docs/graph/legal/corpus"; do
    esc_out="$WORK/esc-out-$(basename "$rel")"; esc_tgt="$WORK/esc-tgt-$(basename "$rel")"
    rm -rf "$esc_out" "$esc_tgt"; mkdir -p "$esc_out" "$esc_tgt/$(dirname "$rel")"
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
echo "  M10 (6): a symlinked directory leaving the target is refused at any depth — OK"

# M10 (7): ...and a symlinked directory that stays INSIDE the target still works.
ins_tgt="$WORK/esc-inside"; rm -rf "$ins_tgt"
mkdir -p "$ins_tgt/docs/graph" "$ins_tgt/elsewhere"
ln -s "$ins_tgt/elsewhere" "$ins_tgt/docs/graph/protocols"
"$ROOT/install.sh" claude-code --project-dir "$ins_tgt" --copy >/dev/null 2>&1 \
    || fail "M10 (7): a symlink that stays inside the target was refused — the check cannot tell inside from outside"
[[ "$(find "$ins_tgt/elsewhere" -name '*.md' | wc -l)" -gt 5 ]] \
    || fail "M10 (7): nothing was placed through the inside-the-target symlink"
echo "  M10 (7): a symlinked directory that stays inside the target still receives its nodes — OK"
}

case_cond() {
    load_files "$BASE"
    load_cond "$BASECOPILOT"
# M7b / M2b — the conditional destinations, held to the same two properties.
#
# One target per property, because the copilot hooks only appear while
# `.claude/settings.json` is absent and both cases have to start from that.
COND_SENTINEL="CYPRESS-COND-SENTINEL"

# M7b: a plant edit to a conditional destination survives as a backup.
TB="$WORK/cond-recover"; mkdir -p "$TB"
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
    [[ $found -eq 1 ]] || fail "M7b VIOLATED — $rel replaced a plant edit with no recoverable backup. It is a conditional destination, so no other case here sees it."
done

# M2b: a conditional destination symlinked at a file OUTSIDE the target must
# have its LINK replaced, never its referent written through.
TS="$WORK/cond-symlink"; mkdir -p "$TS"
OUT="$WORK/cond-outside"; mkdir -p "$OUT"
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


# --- main: build the two shared read-only installs once, run the read-only
#     completeness asserts serially, then dispatch every mutating/independent
#     section concurrently under the gate's ONE shared budget. -----------------
export ROOT

# The recoverability/idempotence/attack sections each need the full `$EVERY_HOST --copy
# --legal-corpus yes` destination set discovered from a real install. That set
# is read-only for M1 completeness, the conditional-destination check, M2 and
# the M7b/M2b conditional cases, so it is installed ONCE here and reused; the
# sections that MUTATE a tree (M3 re-runs, the sentinel sweep, the symlink
# attack) build their own fresh install inside their case.
BASE="$WORK/base"; mkdir -p "$BASE"
"$ROOT/install.sh" $EVERY_HOST --project-dir "$BASE" --copy --legal-corpus yes >/dev/null 2>&1 \
    || fail "baseline install \$EVERY_HOST --copy did not succeed"
T="$BASE"
FILES=(); while IFS= read -r _l; do FILES+=("$_l"); done < <(placed_files "$T")
[[ ${#FILES[@]} -gt 100 ]] || fail "discovered only ${#FILES[@]} placed files — discovery is broken"

BASECOPILOT="$WORK/base-copilot"; mkdir -p "$BASECOPILOT"
TC="$BASECOPILOT"
"$ROOT/install.sh" github-copilot --project-dir "$TC" --copy >/dev/null 2>&1 \
    || fail "baseline install github-copilot --copy did not succeed"
COND_FILES=()
while IFS= read -r _l; do
    case " ${FILES[*]} " in *" $_l "*) ;; *) COND_FILES+=("$_l") ;; esac
done < <(placed_files "$TC")
for _h in .github/hooks/route-hook.py .github/hooks/route.json \
          .github/hooks/status-hook.py .github/hooks/status.json; do
    case " ${COND_FILES[*]} " in
        *" $_h "*) ;;
        *) fail "conditional destination $_h is outside the discovered set — \
either the hooks stopped being conditional, or this leg stopped reaching them; \
either way those destinations are covered by nothing" ;;
    esac
done

# M1 completeness: every machinery node the SEED owns must arrive in the plant.
#
# The sentinel sweep below cannot catch this, and the reason is worth stating:
# it discovers its file set from what the install PRODUCED, so a destination the
# installer silently stopped writing is simply absent from the set and is never
# checked. Patching place_file to skip one protocol left the entire suite green.
# Discovery is the right way to ask "is everything that got written safe"; it is
# structurally the wrong way to ask "did everything that should be written get
# written". That question needs the seed's own inventory as the source of truth.
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
# The adapter machinery too. Enumerating only graph NODES left the check
# narrower than the class it was written for: patching place_file to skip
# `.claude/bound-hook.py` — the PreToolUse guard that is the one hard-enforced
# control in the whole system — left this suite green. A destination is a
# destination, whether or not it is a routable node.
# Every adapter, not just claude-code. The first version of this list covered
# `.claude/*` and the shared graph only, so commenting out the placement of
# `.github/hooks/route.json` left the suite printing "OK — 376 destinations".
# A machinery file dropped from github-copilot or prime-agent is the same defect
# as one dropped from claude-code; it was simply invisible to the check.
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
# ...and the template subtree, which is placed wholesale by place_tree and so
# disappears wholesale if that call is ever dropped.
tmpl_seed="$(find "$ROOT/templates" -name '*.md' -not -name '*.pyc' | wc -l | tr -d ' ')"
# `[[ -d ]]` first: `find` on a MISSING directory fails the pipeline under
# `pipefail`, and `set -e` then killed this script before it could print the
# very diagnostic it exists to print — the templates-dropped regression exited
# 1 with completely empty output.
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
    fail "a machinery node the installer stopped placing is invisible to any \
check that enumerates what WAS placed"
fi

# M11: every path the route resolvers may SELECT is a path the installer writes.
#
# M1 above asks whether everything the seed owns arrived. This asks the mirror
# question of the two resolvers that go looking: a candidate list is a claim
# about where an artifact is written, so a candidate no writer produces is not a
# fallback. The only file it could ever select is one this project did not put
# there — the unbounded reach the plant-root boundary exists to close, arriving
# through the list instead of through the walk. Derived from the resolvers' own
# source against the discovered install, so a candidate re-added without a
# writer fails here rather than on some plant's next prompt.
stray_candidates=()
while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    [[ -e "$T/$rel" || -L "$T/$rel" ]] || stray_candidates+=("$rel")
done < <(python3 - "$ROOT" <<'PY'
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
seen = []


def emit(parts):
    rel = "/".join(parts)
    if rel and rel not in seen:
        seen.append(rel)


hook = (root / "integrations" / "claude-code" / "route-hook.py").read_text(
    encoding="utf-8")
m = re.search(r"^CANDIDATES\s*=\s*\((.*?)\)\s*$", hook, re.M | re.S)
if not m:
    sys.exit("route-hook.py: no CANDIDATES tuple to read — the resolver moved "
             "and this check is asserting nothing")
for element in m.group(1).split(","):
    emit(re.findall(r'"([^"]+)"', element))

ext = (root / "integrations" / "prime-agent" / "route-extension.ts").read_text(
    encoding="utf-8")
m = re.search(r"^const CANDIDATES\s*=\s*\[(.*?)\];\s*$", ext, re.M | re.S)
if not m:
    sys.exit("route-extension.ts: no CANDIDATES array to read — the resolver "
             "moved and this check is asserting nothing")
for element in re.findall(r"\[([^\]]*)\]", m.group(1)):
    emit(re.findall(r'"([^"]+)"', element))

if not seen:
    sys.exit("neither resolver yielded a candidate path — a vacuous pass")
print("\n".join(seen))
PY
) || fail "could not read the route resolvers' candidate lists"
if [[ ${#stray_candidates[@]} -gt 0 ]]; then
    echo "M11 VIOLATED — ${#stray_candidates[@]} resolver candidate(s) no install produces:" >&2
    printf '  %s\n' "${stray_candidates[@]}" >&2
    fail "a resolver may select a path the installer never writes — the only \
file it could find there is one this project did not put there"
fi
echo "  M11: every route-resolver candidate is a path the installer writes — OK"

export BASE BASECOPILOT

# Dispatch the independent sections concurrently under the shared gate budget.
SCN="$(mktemp)"
for c in case_recover case_symchurn case_m2 case_m9 case_m4 case_m8 case_m10 case_cond; do
    printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"

[ "$rc" -eq 0 ] || { echo "install-placement: FAIL — a planted scenario did not pass" >&2; exit "$rc"; }

echo "install-placement: OK — ${#FILES[@]} destinations plus ${#COND_FILES[@]} conditional ones recoverable, symlink-safe, idempotent, link-uniform, audit-classifiable, target-contained"
