#!/usr/bin/env bash
# install.sh — CYPRESS installer
#
# Usage:
#   install.sh <tool> [--project-dir PATH] [--symlink|--copy] [--force]
#                     [--print-config]
#                     [--environment-class ephemeral-test|staging|real-production|mixed]
#                     [--commit-attribution none|<trailer>] [--deliverable-language <bcp47>]
#                     [--comment-language <bcp47>] [--legal-corpus yes|no]
#                     [--legal-jurisdiction <iso-3166-1-alpha-2>]
#
# <tool> is one of:
#   claude-code        — Drop CLAUDE.md + .claude/ into the project.
#   opencode           — Drop AGENTS.md + .opencode/ + opencode.json.
#                         (one config file; opencode auto-discovers
#                          .opencode/{agents,commands,skills}/ by convention)
#   codex              — DEPRECATED (frozen, ADR-0009). Drop AGENTS.md + .codex/;
#                         print ~/.codex/config.toml hints.
#   github-copilot     — DEPRECATED (frozen, ADR-0009). Generate .github/ from
#                         sources (transformed; not symlinked).
#   prime-agent        — Drop AGENTS.md + .prime/agent/ (skills, prompts, agents,
#                         route-extension, settings).
#   all                — Run claude-code, opencode and prime-agent. Name codex or
#                         github-copilot as well to install a frozen host.
#
# Hosts sit in three support tiers (docs/decisions/adr-0009-host-support-tiers.md):
# first-class claude-code, prime-agent; supported opencode; frozen codex,
# github-copilot. A frozen host still installs when named and prints a
# DEPRECATED notice on stderr.
#
# Options:
#   --project-dir PATH   Target project directory (default: $PWD).
#   --symlink            Symlink files into the project (opt-in; edits to a
#                         placed file write back into the seed).
#   --copy               Copy files into the project (default; keeps the seed
#                         isolated from project edits).
#   --force              Replace differing target files without the per-file
#                        backup warning. The backup itself is always made.
#   --environment-class, --commit-attribution, --deliverable-language,
#   --comment-language   The four plant facts (docs/graph/_schema.md §"The
#                        plant: block"), the owner's explicit choices. Each fills
#                        its placeholder in docs/graph/index.md; a value the plant
#                        already declares is never overwritten. Unset facts are
#                        named as a NEXT STEP.
#   --legal-corpus yes|no  Whether this plant carries the seed's legal-corpus/,
#                        placed WHOLE under docs/graph/legal/corpus/. It is a
#                        reference wiki, not a reading list: `yes` brings every
#                        page, `no` brings none, and there is no third option —
#                        an agent that can only refuse without a corpus must not
#                        also be given a pre-filtered one. Which instruments bear
#                        on this project is an INSTRUCTION to agent.legal,
#                        recorded in docs/graph/legal/index.md and revised as the
#                        project evolves — never an import filter. Unset is named
#                        as a NEXT STEP and nothing is placed.
#   --legal-jurisdiction <cc>  Which national law this plant is established
#                        under, as a two-letter country code. The corpus's EU
#                        and international layers are jurisdiction-neutral and
#                        always come with it; its NATIONAL layer is only as wide
#                        as what has been ingested (today: Italy). Naming a code
#                        the corpus does not carry is not an error — it records
#                        the gap so a research-scout ingest can close it, because
#                        another country's statute is retrieved, never assumed
#                        from a neighbouring one.
#   --print-config       For `codex`: print the config.toml lines with
#                         resolved paths instead of editing anything.
#   --check              For `github-copilot`: verify the generated .github/
#                         views are in sync with the seed sources; write
#                         nothing; exit non-zero if stale (CI drift gate).
#   -h, --help           Show this help.
#
# The seed system's source files are not modified. The installer
# copies them by default so project edits never write back into the
# seed; --symlink instead links to them (edits then propagate both
# ways). To uninstall, delete the dropped files and directories from
# the project.

set -euo pipefail

SEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$PWD"
LINK_MODE="copy"   # copy by default; --symlink opts into live seed links
FORCE=0
PRINT_CONFIG=0
CHECK=0
TOOLS=()
# D2 state (see place_file and place_graph_machinery below): TRACK_RECREATION
# is armed only while place_graph_machinery is placing seed-owned graph nodes;
# PRIOR_INSTALL is snapshotted once, before this run writes anything, from the
# one reliable signal that a plant carried the seed before this run —
# .cypress/seed.json already on disk. Together they tell "this destination did
# not exist" apart from "this plant never had it" (silence — a fresh install)
# vs. "this plant had it and lost it" (worth naming).
TRACK_RECREATION=0
PRIOR_INSTALL=0
RECREATED_NODES=()

# --- helpers ---------------------------------------------------------

die() { printf "ERROR: %s\n" "$*" >&2; exit 1; }
log() { printf "[seed] %s\n" "$*"; }
warn() { printf "[seed] WARNING: %s\n" "$*" >&2; }
# deprecated TOOL — the one notice a frozen host's install carries. On stderr,
# like warn, so `codex --print-config` keeps a stdout a user can paste.
deprecated() {
    printf "[seed] DEPRECATED: %s is a frozen host (docs/decisions/adr-0009-host-support-tiers.md). It still installs and gets no new features.\n" "$1" >&2
}

# One scratch directory for the whole run, reclaimed on every exit path.
# Generated content is built HERE and then placed, so a destination is never
# a half-written file: generation either completes and replaces, or fails and
# leaves the previous body untouched.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
# stage NAME — print a scratch path for generated content named NAME.
stage() { mkdir -p "$STAGE/$(dirname "$1")"; printf '%s\n' "$STAGE/$1"; }

# log_registration_notice AGENT_DIR
# When a host sees an agent file written mid-session is host-dependent. Claude
# Code uses a file added to an agent directory it already watches for the next
# delegation, but not the first file in a directory that is new in that
# session, and a first install creates that directory; other hosts are not
# recorded. So the session that ran this installer may not spawn the roster by
# name: the "installed but not spawnable" trap that stalls a first growth. One
# home for the rule: core/method/delegation.md, fact
# delegation.harness-registration; this is only its install-time notice.
log_registration_notice() {
    local agent_dir="$1"
    log ""
    log "NEXT STEP — placed, but the session that ran this installer may not"
    log "  spawn the roster in $agent_dir by name yet: whether a host sees an"
    log "  agent directory written mid-session is host-dependent, and a first"
    log "  install creates it. On a first install, before running grow/graft or"
    log "  dispatching a specialist by name, start a NEW agent session rooted at:"
    log "    $PROJECT_DIR"
    log "  (the plant — never the seed directory). The preflight that checks"
    log "  registration, and the role-emulation fallback when a restart is"
    log "  impossible, are in docs/graph/method/delegation.md"
    log "  (delegation.harness-registration)."
}

# stamp_field STAMP KEY — read one scalar string field out of an existing stamp.
#
# Through a JSON parser, not a regex. This used to be a `sed` capture, and the
# JSON parser further down was only ever a validity ORACLE — it asked whether
# the file parsed and then read every value with the regex anyway. Three shapes
# defeated that, all of them silent, all verified: a zero-byte stamp (the exact
# outcome of the interrupted truncate-in-place write that `place_state` exists
# to prevent), a stamp of garbage, and a stamp that is VALID JSON with a wrong
# type (`"tools": ["claude-code"]`, `"legal_corpus": true`). In each case the
# regex returned empty, empty read as "never set", and a recorded `yes` became
# `undecided` over a corpus still on disk.
#
# A missing stamp is silence and returns empty. A stamp that EXISTS and cannot
# be read is refused by preflight_state_record() before any byte is written, so
# this function is only ever reached with a stamp it can read.
stamp_field() {
    # Not through a link. A symlinked stamp's referent is a file outside the
    # target that this plant does not own; `place_state` replaces the link
    # OBJECT by rename, so the referent is never written — but reading it would
    # let an outside file decide what this plant's record says.
    [[ -f "$1" && ! -L "$1" ]] || return 0
    STAMP_PATH="$1" STAMP_KEY="$2" python3 - <<'PYEOF' 2>/dev/null || true
import json, os, sys
try:
    with open(os.environ["STAMP_PATH"], encoding="utf-8") as fh:
        data = json.load(fh)
except Exception:
    sys.exit(0)
if not isinstance(data, dict):
    sys.exit(0)
value = data.get(os.environ["STAMP_KEY"])
if isinstance(value, str):
    sys.stdout.write(value)
PYEOF
}

# preflight_state_record — refuse an unreadable record BEFORE the first write.
#
# An unreadable record is not a fresh plant. The previous guard ran inside
# write_seed_stamp, i.e. after the entire install, and said "Nothing has been
# written" while a complete adapter sat on disk; and it keyed the refusal on
# whether certain key NAMES survived in the raw bytes, so corruption that
# destroyed the names took the "records no owner decisions" path and reset them.
# Here the question is only: does a stamp exist, and can every field this
# installer will read be read? If not, nothing happens at all.
preflight_state_record() {
    local stamp="$PROJECT_DIR/.cypress/seed.json"
    # A link is not this plant's record: `place_state` replaces the link object
    # by rename and the referent outside the target is left alone, which is the
    # contract test-install-placement.sh's M2 pins. Judging its content here
    # would refuse an install because of a file the plant does not own.
    [[ -f "$stamp" && ! -L "$stamp" ]] || return 0
    local problem
    problem="$(STAMP_PATH="$stamp" python3 - <<'PYEOF'
import json, os
path = os.environ["STAMP_PATH"]
try:
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
except OSError as exc:
    print(f"cannot be read ({exc.strerror})")
    raise SystemExit(0)
if not raw.strip():
    print("is empty — the shape an interrupted write leaves behind")
    raise SystemExit(0)
try:
    data = json.loads(raw)
except ValueError as exc:
    print(f"is not valid JSON ({exc})")
    raise SystemExit(0)
if not isinstance(data, dict):
    print(f"is a JSON {type(data).__name__}, not an object")
    raise SystemExit(0)
for key in ("seed", "version", "tools", "legal_corpus", "legal_jurisdiction",
            "installed_at", "installed_from"):
    if key in data and not isinstance(data[key], str):
        print(f"records {key!r} as a JSON {type(data[key]).__name__}, "
              f"not a string")
        raise SystemExit(0)
PYEOF
)"
    [[ -z "$problem" ]] && return 0
    die "refusing to install: .cypress/seed.json $problem.

  This file is the plant's record of decisions its owner made — which adapters
  are installed, whether the legal corpus is carried, under which jurisdiction.
  Re-deriving those from this run would overwrite what it records with this
  run's defaults, and a record that cannot be read is not a record that says
  nothing.

  Repair the file, or delete it and re-state the decisions with their flags
  (--legal-corpus, --legal-jurisdiction). Nothing has been written."
}

# link_count PATH — how many names point at this inode, portably.
#
# `stat -c %h` is GNU; macOS ships BSD stat, where the spelling is `stat -f %l`,
# and this ran with `|| echo 1` — so on the platform the CI matrix declares, the
# hardlink guard below silently answered "not a hardlink" for every file. The
# guard exists because `cat >` and `>>` write the INODE: a note hardlinked to a
# file outside the target had the migration ledger appended into that outside
# file, at exit 0, and `-L` is false for a hardlink.
link_count() {
    stat -c %h "$1" 2>/dev/null || stat -f %l "$1" 2>/dev/null || echo 1
}

# ensure_dir PATH
# `mkdir -p` for a destination directory, with this tool's own error instead of
# the shell's. preflight_destinations() refuses the common shapes before any
# write, but it works from a hand-written list of directories per adapter, and a
# list like that is incomplete by construction: it missed `.github/hooks` on the
# release that introduced it, and it does not enumerate the per-skill
# leaves under `.claude/skills/`. So the preflight is the early warning, and
# this is the floor underneath it — whatever the list forgets still fails with a
# named path and a reason rather than a raw `mkdir: Not a directory` from three
# frames deep inside place_tree.
ensure_dir() {
    local d="$1"
    if [[ -d "$d" ]]; then
        # Existing is not the same as usable. Returning here on existence alone
        # let a read-only SUBDIRECTORY through — preflight only checks that
        # PROJECT_DIR itself is writable — and the install then died several
        # placements later on a raw `cp: Permission denied`, leaving a target
        # with a kernel and half a graph. The point of this helper is that a
        # blocked destination is this tool's error, at any depth.
        [[ -w "$d" ]] || die "cannot write into $d: the directory exists but is
  not writable. Fix its permissions and re-run. (Nothing further was written.)"
        return 0
    fi
    mkdir -p "$d" 2>/dev/null && return 0
    if [[ -e "$d" || -L "$d" ]]; then
        die "cannot create $d: a non-directory already exists there.
  Remove or rename it and re-run. (The install stopped here; what was written
  before this point is listed above.)"
    fi
    die "cannot create $d (permission denied, or a parent is not a directory)."
}

# place_file SOURCE DEST
# THE canonical destination writer. Every byte this installer puts into a
# target passes through here, so the safety properties are properties of the
# installer rather than of whichever call site remembered them:
#   - an already-correct destination is left alone (no churn, no backup)
#   - a divergent destination is backed up to a timestamped sibling FIRST
#   - the backup is taken with `mv`, which moves the LINK OBJECT: a
#     destination symlinked at a file outside the target is replaced, never
#     followed
#   - --symlink is honoured uniformly
#
# CONTAINMENT, and the scope of that third bullet. "An install cannot modify
# anything outside PROJECT_DIR" is a property of the WHOLE installer, and the
# `mv` argument above establishes it for `place_file` alone. It was stated here
# as if it covered everything, and three writers reached the filesystem past it
# — each found by review, each reproduced before it was closed, each now pinned
# by M10 in tests/test-install-placement.sh. Every write site was then swept,
# and this is the complete account of why each is contained:
#   place_file             `mv` moves the link object                (bullet 3)
#   place_generated        calls place_file
#   place_tree             calls place_file
#   place_state            writes a temp file, then `mv -f` over the dest
#   place_if_missing       returns early on `-e` OR `-L`; never replaces
#   place_kernel           `rm -f "$other"` runs before the `cp` fallback, so
#                          there is no link left to follow
#   record_instruction_migration   moves a symlink at the note path aside as a
#                          `.bak-` first; `! -e` alone was FALSE for a dangling
#                          link and `cat >` followed it                [M10 (1)]
#   preflight_destinations refuses a destination directory whose symlink
#                          resolves outside the target; `( -e || -L ) && ! -d`
#                          waved a symlink-to-a-directory through      [M10 (2)]
#   fill_plant_facts       refuses to write the plant facts through an
#                          index.md symlink leaving the target; it rewrites in
#                          place, being the one destination not reached through
#                          place_file, and write_text() follows a link [M10 (4)]
#   the generated-view python blocks   write to a staged temp path, never to a
#                          destination
# A link that stays INSIDE the target keeps working throughout: the rule is
# about leaving the target, not about links. Adding a writer means adding a row
# here and a case to M10, or the claim above quietly stops being true again.
# Until 7.16.0 seventeen destinations reached the filesystem directly through
# `cp`, `cat >`, `sed >` and Python `open(..., "w")` — 86 files in an
# `install.sh all`. Each one silently destroyed plant edits, left no backup
# for graft-audit to classify, wrote through destination symlinks, and ignored
# --symlink. The second path is removed rather than guarded; place_generated
# below is how generated content reaches this same writer.
# bak_path DEST — a backup path that cannot collide with an existing one.
#
# `${dest}.bak-$(date +%Y%m%d-%H%M%S)` is unique only to the SECOND, and `mv`
# clobbers. Two replacements of one destination inside one second therefore left
# ONE backup holding the second body, with the first silently destroyed —
# verified: BODY-ONE unrecoverable, exit 0, no warning, against a contract whose
# only stated exception is .cypress/seed.json. M7 never replaces a destination
# twice inside a second, so the suite stayed green.
#
# The suffix stays all-digits because tools/graft-audit.py parses
# `\.bak-(\d{8})-\d+$`; a `-2` suffix would make every backup unclassifiable.
# Local time throughout, matching place_file and place_kernel: the note writers
# used `date -u`, so one install could stamp two different dates and
# graft-audit's single `--date` would audit only one of them.
bak_path() {
    local dest="$1" base cand n
    base="${dest}.bak-$(date +%Y%m%d-%H%M%S)"
    if [[ ! -e "$base" && ! -L "$base" ]]; then
        printf '%s' "$base"
        return 0
    fi
    n=1
    while [[ $n -lt 100 ]]; do
        cand="$(printf '%s%02d' "$base" "$n")"
        if [[ ! -e "$cand" && ! -L "$cand" ]]; then
            printf '%s' "$cand"
            return 0
        fi
        n=$((n + 1))
    done
    die "cannot find a free backup name for $dest after 100 attempts"
}

place_file() {
    local src="$1" dest="$2"
    [[ -e "$src" ]] || die "missing source: $src"
    ensure_dir "$(dirname "$dest")"
    # Captured BEFORE the backup branch below can move dest out of the way —
    # this is the one bit place_graph_machinery needs afterward to tell a
    # RE-creation (dest was absent) from an in-place fast-forward (dest was
    # present). See the tracking block after the write, and D2 in CHANGELOG.
    local pre_existing=0
    [[ -e "$dest" || -L "$dest" ]] && pre_existing=1
    if [[ -e "$dest" || -L "$dest" ]]; then
        # an already-correct destination needs no backup and no rewrite:
        # backing up byte-identical files buries the graft-audit signal
        # under hundreds of no-op .bak entries on every re-run
        case "$LINK_MODE" in
            copy)    [[ -f "$dest" && ! -L "$dest" ]] && cmp -s "$src" "$dest" && return 0 ;;
            symlink) [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]] && return 0 ;;
        esac
        # --force suppresses the per-file WARNING below, never the backup:
        # graft Phase 7's safety net is this backup, and the customization
        # audit reads it. Destroying a replaced file leaves a graft with
        # nothing to audit and no way back. (Nothing here ever prompted; the
        # help text said "without prompting" for a prompt that never existed,
        # which is how "--force means no backup" became folklore and then got
        # implemented that way in place_kernel's sibling branch.)
        local bak; bak="$(bak_path "$dest")"
        mv "$dest" "$bak"
        [[ $FORCE -eq 1 ]] || warn "backed up existing $dest -> $bak"
    fi
    case "$LINK_MODE" in
        symlink) ln -s "$src" "$dest" ;;
        copy)    cp "$src" "$dest" ;;
        *)       die "unknown link mode: $LINK_MODE" ;;
    esac
    # D2 — SILENT RESTORE. A seed-owned graph node (protocol/skill/agent/
    # method) that did not exist and gets placed here is either this plant's
    # first install (PRIOR_INSTALL=0 — stay quiet) or a plant that already
    # carried the seed and was MISSING this node (PRIOR_INSTALL=1 — worth
    # naming, because the plant cannot otherwise tell "fast-forward re-created
    # this" from "this was always here"). TRACK_RECREATION is armed only by
    # place_graph_machinery, so an ordinary first-time placement elsewhere
    # (settings.json, a hook, a new adapter's own tree) is never swept in.
    if [[ "$TRACK_RECREATION" -eq 1 && "$pre_existing" -eq 0 && "$PRIOR_INSTALL" -eq 1 ]]; then
        RECREATED_NODES+=("${dest#"$PROJECT_DIR"/}")
    fi
}

# place_state SOURCE DEST
# The installer's OWN derived state — `.cypress/seed.json`. It carries a fresh
# `installed_at` on every run, so it is never byte-identical to what it
# replaces, and routing it through place_file's backup policy would leave one
# `.bak` sibling per install for ever: precisely the churn that "buries the
# graft-audit signal under hundreds of no-op .bak entries". It also has no
# recovery value, because the next stamp is DERIVED from this one plus the
# run's flags rather than authored by hand. So it is replaced without a
# backup — the one recorded exception to M7 — but still atomically and still
# safely: the content is staged, copied to a sibling of the destination, and
# renamed onto it. rename(2) replaces the destination NAME, so a destination
# symlinked outside the target is replaced rather than written through.
place_state() {
    local src="$1" dest="$2" tmp
    ensure_dir "$(dirname "$dest")"
    tmp="$(mktemp "$(dirname "$dest")/.$(basename "$dest").XXXXXX")"
    cp "$src" "$tmp"
    mv -f "$tmp" "$dest"
}

# place_if_missing SOURCE DEST
# The add-if-missing class: scaffold leaves and the graph engines, which the
# plant OWNS once placed (graft-graph-engine.py reconciles them), so a re-run
# must never touch an existing one. `-e` alone was not enough: it is false for
# a DANGLING symlink, and `cp` then writes through the link and creates a file
# OUTSIDE the target. Testing -L as well keeps the whole class inside
# PROJECT_DIR. These destinations stay real files under --symlink by design —
# a plant-owned file must not be a link into the seed.
place_if_missing() {
    local src="$1" dest="$2"
    [[ -e "$dest" || -L "$dest" ]] && return 0
    ensure_dir "$(dirname "$dest")"
    cp "$src" "$dest"
}

# place_generated SOURCE DEST
# place_file's contract for content GENERATED per target — slash commands, the
# transformed Copilot views, the Codex snippet, the seed stamp. Such content
# has no seed original, so the destination is a real file in BOTH link modes:
# a link would have to point at this run's scratch directory. That is the one
# recorded exception to M9 (every placed file is a link under --symlink), and
# it is the reason the exception exists rather than an oversight.
place_generated() {
    local src="$1" dest="$2" saved="$LINK_MODE"
    LINK_MODE="copy"
    place_file "$src" "$dest"
    LINK_MODE="$saved"
}

# record_instruction_migration KERNEL_PATH BACKUP_PATH
# The seed kernel OWNS the repo-root instruction file, so a project that already
# had one has it overwritten. That is correct — the kernel is seed-owned, and a
# plant running two sets of always-loaded instructions has no coherent identity.
# What was NOT correct is what happened next: nothing. The file survived as a
# `.bak` and the team's rules stopped being in force, with no record that they
# ever existed. A backup is recovery evidence, not operational preservation.
#
# So the content becomes WORK, addressed to the one agent that owns the graph.
# This installer does not parse it: reading somebody's instructions and deciding
# what they meant is exactly the judgement `docs-librarian` exists for, and a
# shell script guessing at it would be the "overwrite existing instructions
# without semantic migration" failure wearing an automation costume. The task is
# written down, durably, where the growth flow will find it.
record_instruction_migration() {
    local kernel="$1" backup="$2"
    [[ -n "$backup" && -f "$backup" ]] || return 0
    local dir="$PROJECT_DIR/docs/graph/plans"
    ensure_dir "$dir"
    local note="$dir/adopted-instructions.md"
    local rel_bak="${backup#"$PROJECT_DIR"/}"
    # `! -e` alone is FALSE for a dangling symlink, so the write branch was
    # taken and `cat >` FOLLOWED the link — writing outside PROJECT_DIR and
    # falsifying this file's own invariant at the top: "an install cannot
    # modify anything outside PROJECT_DIR". Reproduced, not theorised. A
    # symlink here is a destination to replace, exactly as `place_file` treats
    # one: move the LINK OBJECT aside, never write through it.
    # A HARDLINK is the same escape wearing different clothes: `cat >` and `>>`
    # both write the inode, so a note hardlinked to a file outside the target
    # had the migration ledger appended into that outside file, exit 0. `-L` is
    # false for it. Moving it aside is the same answer the symlink gets.
    if [[ -e "$note" && ! -L "$note" ]] && [[ "$(link_count "$note")" -gt 1 ]]; then
        local hard_bak; hard_bak="$(bak_path "$note")"
        mv "$note" "$hard_bak"
        warn "  docs/graph/plans/adopted-instructions.md was a hard link to a file"
        warn "    outside the target; moved it to $(basename "$hard_bak") rather than"
        warn "    appending the migration ledger through it"
    fi
    if [[ -L "$note" ]]; then
        local link_bak; link_bak="$(bak_path "$note")"
        mv "$note" "$link_bak"
        warn "  a symlink stood at docs/graph/plans/adopted-instructions.md;"
        warn "    moved it to $(basename "$link_bak") rather than writing through it"
    fi
    if [[ ! -e "$note" ]]; then
        cat > "$note" <<'HEADER'
# Adopted instructions — awaiting migration into the graph

This project had its own root instruction file before CYPRESS was installed.
The seed kernel owns that path, so the previous body was replaced and preserved
as a timestamped backup. Its CONTENT has not been migrated: it is on disk and
out of force until someone puts it where the graph can route to it.

**Owner: `docs-librarian`.** For each entry below, read the backup and place
each instruction in the node that owns that kind of fact, then strike the row:

| The instruction is | Its home |
|---|---|
| a project fact (stack, layout, deployment, domain) | `docs/graph/nodes/` |
| a behavioural rule (how work is done here) | the owning `method/` node, or a deviation record |
| a workflow rule (branching, review, release) | `docs/graph/runbooks/` |
| a host requirement (a tool must be run a certain way) | the harness projection, and `method/delegation.md` if it bears on dispatch |
| obsolete | struck, with a line saying why |
| a duplicate of something the seed already says | struck, naming what it duplicates |
| in conflict with the seed | an open question for the owner — never silently resolved |

Nothing here is migrated automatically. An instruction someone wrote on purpose
deserves a reader, and guessing at its intent is how a project quietly loses the
rule it cared about most.

## Entries

HEADER
    fi
    # The row says when the replacement HAPPENED, never when the row was
    # written. `sweep_orphaned_instruction_backups` re-files backups taken on
    # runs long past, and stamping those with this run's date puts a false claim
    # in front of the librarian by exactly the mechanism that function's own
    # guard exists to stop — while the true value sits in the filename the guard
    # already matched. Evidence that carries its own timestamp is read, not
    # re-dated; a live replacement's backup was made seconds ago, so the two
    # agree there and only the re-filed rows change.
    local when="${rel_bak##*.bak-}"
    if [[ "$when" =~ ^([0-9]{4})([0-9]{2})([0-9]{2})-[0-9]{6}$ ]]; then
        when="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}"
    else
        when="$(date -u +%Y-%m-%d)"
    fi
    if ! grep -qF "$rel_bak" "$note" 2>/dev/null; then
        printf -- '- [ ] `%s` — replaced %s on %s; not yet migrated.\n' \
               "$rel_bak" "$(basename "$kernel")" "$when" >> "$note"
    fi
    warn "  its content is NOT migrated. Recorded as work for docs-librarian in:"
    warn "    docs/graph/plans/adopted-instructions.md"
}

# sweep_orphaned_instruction_backups
# A kernel backup with no ledger entry is a project's own instructions, on
# disk, with nothing anywhere saying they exist. It happened once for a real
# reason — the note write failed after the kernel was already replaced, and the
# next run saw a kernel that matched the seed and therefore no deviation to
# report. The preflight now prevents that particular sequence; this catches the
# general case, because "the record was never written" has more causes than the
# one that was found, and the cost of missing it is permanent.
sweep_orphaned_instruction_backups() {
    [[ $PRIOR_INSTALL -eq 1 ]] || return 0
    local f
    for f in "$PROJECT_DIR"/CLAUDE.md.bak-* "$PROJECT_DIR"/AGENTS.md.bak-* \
             "$PROJECT_DIR"/.github/copilot-instructions.md.bak-*; do
        [[ -f "$f" ]] || continue
        # Only backups THIS installer made: the suffix is `.bak-YYYYMMDD-HHMMSS`.
        # An unanchored glob swept up anything a person happened to name
        # `CLAUDE.md.bak-notes-from-monday` and filed their scratch note as
        # replaced kernel body — a false claim put in front of the librarian as
        # if it were real work.
        [[ "$f" =~ \.bak-[0-9]{8}-[0-9]{6}$ ]] || continue
        # A backup of the seed kernel itself carries nothing the plant wrote.
        cmp -s "$SEED_ROOT/core/AGENTS.md" "$f" && continue
        local kernel="${f%%.bak-*}"
        record_instruction_migration "$kernel" "$f"
    done
}

# place_kernel DEST
# Place the bootstrap kernel at DEST, where DEST is a repo-root kernel file:
# CLAUDE.md (read by Claude Code) or AGENTS.md (read by Prime Agent, opencode,
# and Codex; AGENTS.md wins over CLAUDE.md within a directory). To let ONE plant
# run Claude Code and Prime Agent INTERCHANGEABLY off byte-identical project
# instructions, the two kernel files are collapsed to a single source of truth:
# the first one placed is a real file (a seed copy by default, or a seed symlink
# under --symlink), and the second becomes a PROJECT-LOCAL relative symlink to
# the first. The link is between the two project files, never to the seed, so
# copy-mode isolation from the seed is preserved. Editing the kernel then updates
# both harnesses at once — no drift. On a platform without symlinks the second
# file degrades to an independent copy (identical at install; may drift on edit).
place_kernel() {
    local dest="$1" name sibling seed_kernel
    name="$(basename "$dest")"
    seed_kernel="$SEED_ROOT/core/AGENTS.md"
    case "$name" in
        CLAUDE.md) sibling="$PROJECT_DIR/AGENTS.md" ;;
        AGENTS.md) sibling="$PROJECT_DIR/CLAUDE.md" ;;
        *)         place_file "$seed_kernel" "$dest"; return ;;
    esac

    # ONE real file holds the kernel; the other is a PROJECT-LOCAL relative
    # symlink to it, so Claude Code (CLAUDE.md) and Prime Agent / opencode /
    # Codex (AGENTS.md) run off byte-identical instructions. The real file's
    # BODY is ALWAYS brought to the current seed kernel: a graft that merely
    # re-points the symlink and leaves a STALE kernel body is the exact bug this
    # guards against (it also left no .bak, so graft-audit could not see it).
    # A stale body is fast-forwarded WITH a per-file .bak; a pristine body is
    # left untouched (idempotent, no backup churn).
    # Which of the two files HOLDS the kernel. Under --copy that is whichever
    # is a plain regular file; under --symlink it is whichever is a link to the
    # SEED kernel (the sibling is a link to it, not to the seed).
    #
    # Testing only for a regular file was a silent disaster in symlink mode:
    # neither name is ever `-f && ! -L` there, so BOTH tests failed and the
    # `else` made each adapter claim its OWN destination as the real file. Five
    # adapters therefore flipped the pair back and forth within a single
    # `install.sh all`, and every re-run produced two more backups than the last
    # — 1, then 3, then 5, for ever — while the CONTENT stayed byte-identical,
    # so nothing but `ls -la` could see it happening.
    local realfile
    if [[ -L "$dest" && "$(readlink "$dest")" == "$seed_kernel" ]]; then
        realfile="$dest"
    elif [[ -L "$sibling" && "$(readlink "$sibling")" == "$seed_kernel" ]]; then
        realfile="$sibling"
    elif [[ -f "$dest" && ! -L "$dest" ]]; then
        realfile="$dest"
    elif [[ -f "$sibling" && ! -L "$sibling" ]]; then
        realfile="$sibling"
    else
        realfile="$dest"
    fi

    # 1) Fast-forward the canonical real file to the current seed kernel.
    # The PLACEMENT is place_file's job — it already owns the identical-check
    # per link mode, the timestamped backup, and link-object replacement. Doing
    # it here by hand is what left the kernel a COPY under --symlink (so a seed
    # kernel change never reached the plant, though the flag promised it would)
    # while every sibling file was correctly linked.
    # What is NOT place_file's job is what the kernel MEANS: it is the one
    # artifact loaded on EVERY session, so a plant that recorded a deliberate
    # deviation has it only here, and the fast-forward discards it. The
    # overwrite still happens — a stale kernel is the worse failure, and the
    # seed owns the kernel — but it is announced in the kernel's own terms,
    # with the backup named as the recovery path.
    # `deviated` asks one question: is the plant about to lose a kernel body it
    # does not have anywhere else? A plain file that differs is the obvious
    # case. A kernel file symlinked at some OTHER file is the same loss wearing
    # a different shape — and it used to slip through, because the test required
    # `! -L`. The two links this installer makes on purpose (to the seed kernel,
    # or to the sibling) are not deviations and are excluded by name.
    local deviated=0
    if [[ -f "$realfile" && ! -L "$realfile" ]]; then
        cmp -s "$seed_kernel" "$realfile" || deviated=1
    elif [[ -L "$realfile" ]]; then
        local _points; _points="$(readlink "$realfile")"
        if [[ "$_points" != "$seed_kernel" && "$_points" != "$(basename "$sibling")" ]]; then
            cmp -s "$seed_kernel" "$realfile" 2>/dev/null || deviated=1
        fi
    fi
    place_file "$seed_kernel" "$realfile"
    # This announcement deliberately IGNORES --force, and it is the one place
    # that should. --force silences backup CHATTER ("backed up existing X"),
    # which is noise a steward re-installing on purpose already expects. This is
    # not that: it says a deviation the plant deliberately recorded on the one
    # file loaded by every session is GONE from the new body. A flag meaning
    # "yes, overwrite, stop asking" must not also mean "and don't mention what
    # you destroyed" — the louder the re-install, the more this line is needed.
    # Pinned by tests/test-unified-graph-install.sh, which asserts the notice
    # survives --force and names the deviation.
    if [[ $deviated -eq 1 ]]; then
        local _bak; _bak="$(ls -1dt "$realfile".bak-* 2>/dev/null | head -1)"
        warn "kernel: $(basename "$realfile") differed from the seed kernel and was OVERWRITTEN"
        warn "  previous body: $_bak"
        warn "  any recorded deviation on the kernel body is NOT in the new body."
        record_instruction_migration "$realfile" "$_bak"
    fi
    log "kernel: $(basename "$realfile") is current with the seed kernel"

    # 2) Point the OTHER kernel file at the real file via a project-local symlink.
    local other
    if [[ "$realfile" == "$dest" ]]; then other="$sibling"; else other="$dest"; fi
    if [[ -L "$other" && "$(readlink "$other")" == "$(basename "$realfile")" ]]; then
        log "kernel: $(basename "$other") -> $(basename "$realfile") (shared kernel — interchangeable Claude Code / Prime Agent)"
        return
    fi
    # --force suppresses the PROMPT, never the backup — the same contract
    # place_file states and graft Phase 7's safety net depends on. This branch
    # used to read `$FORCE -ne 1`, so the one flag a steward reaches for when
    # re-installing over a customized plant was also the flag that destroyed
    # the body it was about to replace, with nothing left for graft-audit to
    # classify. The `mv` (not `cp`) also means a destination symlinked outside
    # the target has its LINK OBJECT moved aside, never its referent rewritten.
    if [[ -e "$other" || -L "$other" ]] && ! cmp -s "$seed_kernel" "$other"; then
        local bak2; bak2="$(bak_path "$other")"
        mv "$other" "$bak2"
        [[ $FORCE -eq 1 ]] || warn "backed up existing $other -> $bak2"
        # The SIBLING kernel file carries a body too, and when a project had
        # both CLAUDE.md and AGENTS.md with different content, only the first
        # was recorded as migration work. The second survived as a .bak and
        # vanished from the ledger — the precise failure this feature exists to
        # prevent, for exactly one of the two files.
        record_instruction_migration "$other" "$bak2"
    fi
    rm -f "$other"
    if ln -s "$(basename "$realfile")" "$other" 2>/dev/null; then
        log "kernel: $(basename "$other") -> $(basename "$realfile") (shared kernel — interchangeable Claude Code / Prime Agent)"
    else
        cp "$seed_kernel" "$other"
        warn "symlink unavailable; placing $(basename "$other") as an independent kernel copy (may drift on edit)"
    fi
}
# place_tree SRC_DIR DEST_DIR [PATTERN]
# Mirrors every file matching PATTERN (default *) from SRC_DIR into
# DEST_DIR by calling place_file for each.
place_tree() {
    local src="$1" dest="$2" pattern="${3:-*}"
    [[ -d "$src" ]] || die "missing source dir: $src"
    ensure_dir "$dest"
    local f
    # `-type l` is not optional. Under --symlink the graph home is a tree of
    # SYMLINKS into the seed, and a projection taken FROM the graph therefore
    # reads symlinks. A bare `-type f` matches none of them, so every adapter
    # that projects the roster silently placed an EMPTY roster — the exact
    # "present in the graph, absent from the roster the session enumerates"
    # failure the projection change exists to prevent, moved into the other
    # link mode. Python bytecode is never seed content. It is gitignored here, so it is
    # invisible to any check that reads the tree through Git, but it sits on
    # disk the moment someone runs a linter before installing — and the default
    # `*` pattern shipped it into the plant, where it landed as a tracked file
    # in a directory the plant's own .gitignore only covers going forward. A
    # plant then carried one installer's interpreter version as data.
    while IFS= read -r -d '' f; do
        local rel="${f#"$src"/}"   # quoted: an unquoted $src is a glob pattern
        place_file "$f" "$dest/$rel"
    done < <(find "$src" \( -type f -o -type l \) -name "$pattern" \
                  -not -name '*.pyc' -not -path '*/__pycache__/*' -print0)
}

# project_agents DEST_DIR
# project_skills DEST_DIR
# The harness projections of the graph's roster and skill set. `docs/graph/`
# is the ONE home of both (place_graph_machinery fast-forwards the seed's own
# nodes into it); a tool directory is a projection the harness reads because it
# spawns agents and loads skills from fixed locations. So the projection is
# taken FROM THE GRAPH, never from the seed: a plant that authored an agent or
# a skill of its own has it in the graph, and sourcing the projection from the
# seed instead silently leaves every plant-authored node unspawnable on every
# harness — present in the graph, absent from the roster the session enumerates.
# The graph home is established first (each adapter calls place_docs_skeleton
# before projecting), so these read a tree that already carries the current seed
# plus whatever the plant authored.
# Both project the home's TOP LEVEL only, and skip the files that are not
# nodes. A harness reads its roster by listing a directory, so anything placed
# there becomes a spawnable entry: recursing would turn a plant's scratch note
# at `agents/notes/todo.md` into a phantom agent, and an `index.md` beside the
# nodes into a phantom skill. `_`-prefixed files are the graph's own
# conventions (templates, the routing corpus) and are handled explicitly or
# not at all.
project_agents() {
    local dest="$1" home="$PROJECT_DIR/docs/graph/agents" f name
    for f in "$home"/*.md; do
        [[ -f "$f" ]] || continue           # -f follows a symlinked home
        name="$(basename "$f")"
        case "$name" in _*|index.md|README.md) continue ;; esac
        place_file "$f" "$dest/$name"
    done
    # the golden routing corpus rides with the roster (not a *.md, so the loop
    # skips it) so agent-lint.py --eval can score the roster on EVERY harness
    [[ -f "$home/_routes.golden.tsv" ]] && \
        place_file "$home/_routes.golden.tsv" "$dest/_routes.golden.tsv"
}
project_skills() {
    local dest="$1" home="$PROJECT_DIR/docs/graph/skills" f name
    for f in "$home"/*.md; do
        [[ -f "$f" ]] || continue
        name="$(basename "$f" .md)"
        case "$name" in _*|index|README) continue ;; esac
        place_file "$f" "$dest/$name/SKILL.md"
    done
}

# place_docs_skeleton: install every knowledge artifact beneath the one
# docs/graph/ root. Plant-authored content is preserved: scaffold files
# and template leaves are added only when missing. The seed-owned
# machinery subtrees (protocols/skills/agents/method/templates) are
# fast-forwarded to the current seed — identical files untouched,
# changed files backed up for graft-audit to inspect (--force suppresses
# the per-file warning, never the backup).
place_docs_skeleton() {
    place_graph_scaffold
    place_graph_machinery
    [[ "${LEGAL_CORPUS:-}" == "yes" ]] && place_legal_corpus
    local src="$SEED_ROOT/templates/docs" dest="$PROJECT_DIR/docs/graph" f rel
    log "populating missing unified-graph leaves in docs/graph/"
    while IFS= read -r -d '' f; do
        rel="${f#"$src"/}"         # quoted: an unquoted $src is a glob pattern
        # A `<name>.unfilled.md` beside the target is the plant's recorded
        # verdict (graft-audit --unfilled --rename): it looked at this scaffold
        # and declined it. Honour the marker — re-creating the blank leaf would
        # re-shadow the authored one a cold agent needs (D-SCAFFOLD).
        if [[ -e "$dest/${rel%.md}.unfilled.md" ]]; then
            continue
        fi
        place_if_missing "$f" "$dest/$rel"
    done < <(find "$src" -type f -print0)
}

# place_graph_machinery: the seed's method surface — protocols, skills
# (flattened <name>.md), agents, method/posture nodes, and the Tier-3
# template artifacts — lives INSIDE the graph as seed-owned routable
# nodes (kind protocol/skill/agent/method, origin: seed). This is the
# single home; any tool-dir copies are harness projections of it.
place_graph_machinery() {
    local g="$PROJECT_DIR/docs/graph"
    log "installing the method surface into docs/graph/ (protocols, skills, agents, method, templates)"
    # D2: every place_file below (place_tree calls through to it too) is now
    # tracked for RE-creation — see place_file. These are exactly the
    # seed-owned nodes fast-forwarded on EVERY install, regardless of adapter,
    # so a re-appearance here after PRIOR_INSTALL is meaningful, never noise.
    TRACK_RECREATION=1
    place_tree "$SEED_ROOT/protocols"   "$g/protocols" "*.md"
    place_tree "$SEED_ROOT/core/method" "$g/method"    "*.md"
    place_tree "$SEED_ROOT/agents"      "$g/agents"    "*.md"
    # the golden routing corpus rides with the roster so the kernel-
    # mandated router can run --eval (a graft exit gate) on EVERY harness,
    # not only where .claude/agents/ exists
    place_file "$SEED_ROOT/agents/_routes.golden.tsv" "$g/agents/_routes.golden.tsv"
    local d name
    for d in "$SEED_ROOT/skills"/*/; do
        name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$g/skills/$name.md"
    done
    place_tree "$SEED_ROOT/templates" "$g/templates"
    TRACK_RECREATION=0
}

# corpus_pages DIR [NAME_GLOB] — count corpus pages in DIR.
#
# `-type f -o -type l`, never `-type f` alone, and place_tree learned this first:
# "under --symlink the graph home is a tree of SYMLINKS into the seed, so a bare
# `-type f` matches none of them". The completeness check below repeated the
# mistake on its own terms, and the result was that `--legal-corpus yes
# --symlink` ALWAYS died with "placed partially (0 of 16 pages)" while all
# sixteen pages sat there, correct, as links. The check written to prevent a
# partial corpus was the only thing preventing a whole one.
# Backups are excluded because they are not pages — counting them is what let a
# shortfall hide behind `.bak-*` siblings.
corpus_pages() {
    local dir="$1" glob="${2:-*}"
    [[ -d "$dir" ]] || { printf '0\n'; return 0; }
    find "$dir" \( -type f -o -type l \) -name "$glob" -not -name '*.bak-*' \
        | wc -l | tr -d ' '
}

# place_legal_corpus: the seed's legal-corpus/, placed WHOLE under the plant's
# docs/graph/legal/corpus/ on the owner's explicit `--legal-corpus yes`.
#
# Whole, and the word is load-bearing. `agent.legal` runs without WebSearch,
# WebFetch or Bash: this corpus plus the plant's own legal leaf is the ONLY law
# it can reach, and its charter turns a corpus gap into a refusal rather than a
# reconstructed citation. That design is what makes a PARTIAL corpus worse than
# none — a missing page reads to the analyst exactly like an instrument that
# does not exist, so a well-meaning import filter silently converts "nobody
# copied this" into "this does not apply", which is the one answer the refusal
# rule exists to prevent. Relevance is expressed downstream, as an instruction
# in docs/graph/legal/index.md that the owner revises as the project evolves.
#
# Until 7.11.0 nothing placed it at all: the corpus lived in the seed, the
# analyst read only the plant, and every plant's legal/ held one empty scaffold.
place_legal_corpus() {
    local src="$SEED_ROOT/legal-corpus" dest="$PROJECT_DIR/docs/graph/legal/corpus"
    [[ -d "$src" ]] || die "missing legal-corpus/ in the seed: $src"
    log "installing legal-corpus/ WHOLE into docs/graph/legal/corpus/"
    place_tree "$src" "$dest"
    local want have
    want="$(corpus_pages "$src")"
    have="$(corpus_pages "$dest")"
    # A partial corpus is the failure mode this whole feature exists to avoid,
    # so it is checked rather than assumed — and the check counts CORPUS PAGES.
    # `find -type f` counted the `.bak-*` siblings a re-install leaves behind,
    # so every backup raised `have` by one and masked a real shortfall; with
    # four backups present, twelve pages of a sixteen-page corpus satisfied it.
    # A SHORTFALL is the failure; a surplus is not. `-eq` treated both the same
    # and the message said "placed partially" for either, so a plant that did
    # exactly what the notice below tells it to do — run a research-scout ingest
    # and land its own national statute under this directory — got
    # "placed partially (17 of 16 pages)" and could never install again. The
    # installer bricked a plant for following its own printed instruction.
    #
    # `-lt` is the die: a missing page is indistinguishable from an instrument
    # that does not apply, which is what this whole feature exists to prevent.
    # A surplus is the plant's own ingest, it is named rather than counted
    # silently, and it is NOT a reason to refuse — the seed does not own that
    # directory exclusively once a plant has reasoned from it.
    if [[ "$have" -lt "$want" ]]; then
        die "legal corpus placed partially ($have of $want pages) — a subset makes a\
 missing page indistinguishable from an instrument that does not apply"
    fi
    if [[ "$have" -gt "$want" ]]; then
        # NAME them. `agent.legal` runs without WebSearch or Bash and reads this
        # directory as the only law it can reach, so a stray note dropped here is
        # announced as "a plant ingest" and then read as an INSTRUMENT. Saying
        # how many is not enough; the owner has to be able to see which.
        log "  docs/graph/legal/corpus/ carries $((have - want)) page(s) beyond the"
        log "  $want the seed ships — a plant ingest, left in place:"
        while IFS= read -r _extra; do
            [[ -n "$_extra" ]] && log "    ${_extra#"$dest/"}"
        done < <(comm -13 \
                   <(cd "$src" && find . -name '*.md' | sort) \
                   <(cd "$dest" && find . -name '*.md' -not -name '*.bak-*' | sort) \
                 | sed "s|^\./|$dest/|")
        log "  agent.legal reads this directory as law — check that each is an"
        log "  instrument and not a note."
    fi
    local _instruments
    _instruments="$(cd "$dest" && find . -name '*.md' -not -name 'README.md' \
                      -not -name '_schema.md' -not -name 'index.md' | wc -l | tr -d ' ')"
    log "  docs/graph/legal/corpus/  ($want files, of which $_instruments are instruments —"
    log "  the rest are README/_schema/index scaffolding. The whole corpus; scope it in"
    log "  legal/index.md, never by deleting pages)"

    # The corpus travels with its CHECKER. A plant received
    # legal-corpus/_schema.md — the contract a corpus page must satisfy — and no
    # instrument to check anything against it, while seven other linters did
    # travel. agent.legal reads this directory as the only law it can reach and
    # runs without WebSearch or Bash, so a plant that ingests its own national
    # statute had the contract, the reader, and no way to tell a malformed entry
    # from a good one. An entry missing `verified` still LOOKS like an entry, so
    # the refusal that discipline depends on never fires.
    #
    # Conditional on purpose: it ships when the corpus does, and only then. A
    # plant with `--legal-corpus no` has nothing for it to lint.
    place_file "$SEED_ROOT/tests/legal-lint.py" "$PROJECT_DIR/docs/graph/legal-lint.py"
    log "  docs/graph/legal-lint.py  (the corpus travels with its checker)"

    # The EU and international layers are jurisdiction-neutral. The national
    # layer is only as wide as what has been ingested, and the gap is a fact
    # worth stating loudly: an analyst that cannot see a national instrument
    # cannot tell it was never ingested from its not existing, and the nearest
    # neighbour's statute is not a substitute for it.
    local have; have="$(corpus_jurisdictions | tr '\n' ' ')"
    if [[ -z "${LEGAL_JURISDICTION:-}" ]]; then
        log "  national layer carried: ${have:-none} — no --legal-jurisdiction given, so"
        log "  nothing says which of these (if any) is this plant's. Name it."
    elif corpus_jurisdictions | grep -qx "$LEGAL_JURISDICTION"; then
        log "  national layer: '$LEGAL_JURISDICTION' is carried by the corpus"
    else
        log ""
        log "  NATIONAL LAYER MISSING for '$LEGAL_JURISDICTION' — the corpus carries ${have:-none}."
        log "  The EU and international pages still apply; the national statutes of"
        log "  '$LEGAL_JURISDICTION' are NOT in the corpus and must not be inferred from a"
        log "  neighbouring jurisdiction's. Record them in docs/graph/legal/index.md"
        log "  under 'Not in the corpus at all' and run a research-scout ingest"
        log "  (protocols/ingest-library.md flow, legal-corpus/_schema.md contract);"
        log "  agent.legal correctly refuses on them until it lands."
    fi
}

# place_graph_scaffold: drop the knowledge-graph home (schema, linter,
# router index, empty nodes/) into docs/graph/. Add missing files only.
place_graph_scaffold() {
    local g="$PROJECT_DIR/docs/graph"
    log "ensuring unified knowledge graph in docs/graph/"
    ensure_dir "$g/nodes"
    place_if_missing "$SEED_ROOT/templates/knowledge-graph/_schema.md" "$g/_schema.md"
    # The frontmatter reader the graph engines share. NOT add-if-missing: it is
    # seed-owned code that every engine beside it imports, and a plant holding a
    # stale copy while the engines expect the current one is a crash, not a
    # customization. `place_file` fast-forwards it with a backup like any other
    # seed-owned file.
    place_file "$SEED_ROOT/templates/knowledge-graph/frontmatter.py" "$g/frontmatter.py"
    place_if_missing "$SEED_ROOT/templates/knowledge-graph/graph-lint.py" "$g/graph-lint.py"
    place_if_missing "$SEED_ROOT/templates/knowledge-graph/spec-lint.py" "$g/spec-lint.py"
    place_if_missing "$SEED_ROOT/templates/knowledge-graph/grill-lint.py" "$g/grill-lint.py"
    # the agent router is kernel-mandated on EVERY harness ("python3
    # docs/graph/agent-lint.py --route"); claude-code additionally projects
    # it to .claude/agent-lint.py. Unlike the graph engines (add-if-missing,
    # reconciled by graft-graph-engine.py), the router carries NO project
    # config, so it fast-forwards like machinery: identical -> untouched,
    # changed -> backed up and replaced (graft-audit inspects the backup).
    place_file "$SEED_ROOT/integrations/claude-code/agent-lint.py" "$g/agent-lint.py"
    # ...and the reader it imports, beside it. Every copy of an engine needs one:
    # they are standalone scripts, so the import resolves next to the script.
    # the agnosticism floor travels with the graph for the same reason: it
    # carries NO project config (forbidden tokens are --forbid at call time,
    # never baked in), so it fast-forwards like the router. It is available,
    # not mandatory -- it applies to artifacts a plant intends to be reusable
    # (a harvest candidate, a shared component), never to the plant's own
    # project-specific knowledge, where naming the project is correct.
    place_file "$SEED_ROOT/tools/agnosticism-lint.py" "$g/agnosticism-lint.py"
    # the prose floor under the humanizer skill: detectable AI-writing tells
    # plus the fact-preservation check (--against <rev>). Config-free, so it
    # fast-forwards like the router; it applies to prose a person reads.
    place_file "$SEED_ROOT/tools/prose-lint.py" "$g/prose-lint.py"
    # the lifecycle status register: lint + query over every status-bearing
    # artifact. Config-free (vocabulary is the schema's), so it fast-forwards
    # like the router. A session-start hook injects its --summary once.
    place_file "$SEED_ROOT/tools/status-register.py" "$g/status-register.py"
    place_if_missing "$SEED_ROOT/templates/knowledge-graph/index.md" "$g/index.md"
    fill_plant_facts "$g/index.md"
    log "  run /initialize — it forks on whether this target has source to scout:"
    log "    source present -> protocol.grow (author the graph from that evidence)"
    log "    empty repo     -> protocol.from-scratch (nine-phase bootstrap)"
}

# fill_plant_facts INDEX
# The router's `plant:` block holds the four facts only the owner can assert
# (schema §"The plant: block"). A value passed on the command line replaces a
# PLACEHOLDER line only — a value the plant already declares is never
# overwritten. Whatever is still a placeholder afterwards is named as a NEXT
# STEP, because an agent otherwise re-asks or guesses it.
fill_plant_facts() {
    local idx="$1" out_log
    out_log="$(stage "plant-facts.log")"
    # Three states, not two. A project grown before the `plant:` block existed
    # has no block at all — no placeholder line to match — and the old code
    # read that as "already declared", suppressed the write AND the NEXT STEP
    # warning, and left the block missing. "Absent" and "already declared" are
    # opposite states. The canonical block shape is read from the index
    # template so it keeps one home.
    #
    # Writes to a staged file rather than capturing via `$(...)` around its own
    # heredoc: bash 3.2 (macOS's system bash, the gate's other CI leg) misparses
    # a heredoc nested inside a command substitution once another heredoc
    # follows later in the same script — install_github_copilot's skill loop,
    # ~400 lines down, was read as shell text instead of heredoc data.
    # Reproduced under bash 3.2.25 and 3.2.57 with `bash -n`; gone the moment
    # this heredoc's `$(...)` wrapper is removed.
    PLANT_ENV="${PLANT_ENV:-}" PLANT_ATTR="${PLANT_ATTR:-}" \
        PLANT_DLANG="${PLANT_DLANG:-}" PLANT_CLANG="${PLANT_CLANG:-}" \
        PROJECT_DIR="$PROJECT_DIR" \
        python3 - "$idx" "$SEED_ROOT/templates/knowledge-graph/index.md" \
        > "$out_log" <<'PYEOF' || die "could not write the plant: block into $idx"
import os, re, sys
from pathlib import Path

KEYS = ("environment_class", "commit_attribution",
        "deliverable_language", "comment_language")
VALUES = dict(zip(KEYS, (os.environ.get(v, "").strip() for v in
                         ("PLANT_ENV", "PLANT_ATTR", "PLANT_DLANG", "PLANT_CLANG"))))

idx, template = Path(sys.argv[1]), Path(sys.argv[2])

# docs/graph/index.md is PLANT-OWNED, and this is the one place the installer
# rewrites it in place rather than through place_file. write_text() FOLLOWS a
# symlink, so an index.md linked outside the target had the plant fact written
# into that outside file — reproduced, exit 0, no warning, and no backup to
# find it by. Same rule the preflight applies to destination directories: a
# link that stays inside the target is the plant's business, a link that leaves
# it is refused.
if idx.is_symlink():
    root = Path(os.environ["PROJECT_DIR"]).resolve()
    try:
        inside = idx.resolve().is_relative_to(root)
    except (OSError, ValueError):
        inside = False
    if not inside:
        print(f"docs/graph/index.md is a symlink leaving the target "
              f"({os.readlink(idx)}); refusing to write the plant facts through "
              f"it. Replace the link with a real file, or point it inside the "
              f"project, then re-run.", file=sys.stderr)
        sys.exit(3)

text = idx.read_text(encoding="utf-8")
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def block_from_template():
    """The canonical `plant:` block, taken from the index template so the
    placeholder vocabulary is not restated here."""
    m = FM.search(template.read_text(encoding="utf-8")) if template.is_file() else None
    if m:
        b = re.search(r"^plant:\n(?:[ \t]+\S.*\n)+", m.group(1) + "\n", re.M)
        if b:
            return b.group(0)
    return ("plant:\n"
            "  environment_class: <ephemeral-test | staging | real-production | mixed>\n"
            "  commit_attribution: <none | trailer text>\n"
            "  deliverable_language: <bcp47>\n"
            "  comment_language: <bcp47>\n")


log = []
m = FM.search(text)
if m is None:
    front, body, had_fm = "", text, False
else:
    front, body, had_fm = m.group(1) + "\n", text[m.end():], True

if not re.search(r"^plant:\s*$", front, re.M):
    front = front.rstrip("\n") + "\n" if front.strip() else ""
    if not re.search(r"^grown:", front, re.M):
        front = "grown: false\n" + front
    front += block_from_template()
    log.append("  plant: block was missing — created it in docs/graph/index.md")

still_unset = []
for key in KEYS:
    want = VALUES[key]
    km = re.search(rf"^(\s+){key}:[ \t]*(.*)$", front, re.M)
    if km is None:
        # The block predates this key. Append it in the template's own words,
        # after the last key already present, so the block keeps the canonical
        # shape instead of gaining an invented placeholder in an odd place.
        tpl = re.search(rf"^\s+{key}:[ \t]*(.*)$", block_from_template(), re.M)
        ph = tpl.group(1).strip() if tpl else "<unset>"
        last = None
        for prior in KEYS:
            pm = re.search(rf"^\s+{prior}:[ \t]*.*$", front, re.M)
            if pm:
                last = pm
        at = last.end() if last else re.search(r"^plant:[ \t]*$", front, re.M).end()
        front = front[:at] + f"\n  {key}: {ph}" + front[at:]
        km = re.search(rf"^(\s+){key}:[ \t]*(.*)$", front, re.M)
    current = km.group(2).strip()
    placeholder = current.startswith("<") or current == ""
    if want and placeholder:
        front = front[:km.start()] + f"{km.group(1)}{key}: {want}" + front[km.end():]
        log.append(f"  plant fact {key} set to {want}")
    elif want:
        log.append(f"  plant fact {key} already declared as {current}; "
                   f"--{key.replace('_', '-')} ignored")
    elif placeholder:
        still_unset.append(key)

new = ("---\n" + front.rstrip("\n") + "\n---\n" +
       ("" if had_fm or body.startswith("\n") else "\n") + body)
if new != text:
    # os.replace, never write_text: an in-place write follows a HARDLINK, and a
    # hardlink is not a symlink so the is_symlink() guard above never sees it.
    # Verified: `ln /outside/secret.md <target>/docs/graph/index.md` then a
    # re-install wrote the plant-facts block into the outside file, exit 0, no
    # warning. Renaming a staged file onto the path breaks the link instead —
    # which is why place_file, whose idiom is mv-then-cp, was never vulnerable.
    # An INTERNAL symlink is the plant's own business and must still receive the
    # facts in the real file behind it, so resolve it first (the escaping case
    # already died above). A HARDLINK is not a symlink, so this leaves `target`
    # as the path itself and os.replace gives it a fresh inode — which is what
    # stops the write reaching a file outside the target.
    _target = idx.resolve() if idx.is_symlink() else idx
    _tmp = _target.with_name(_target.name + ".plantfacts.tmp")
    _tmp.write_text(new, encoding="utf-8")
    os.replace(_tmp, _target)

if still_unset:
    log.append("")
    log.append("NEXT STEP — plant facts still unset in docs/graph/index.md: "
               + " ".join(still_unset))
    log.append("  These are the owner's explicit choices, never an agent's guess. Pass them")
    log.append("  now (--environment-class, --commit-attribution, --deliverable-language,")
    log.append("  --comment-language) or fill the plant: block before grow or graft.")
print("\n".join(log))
PYEOF
    while IFS= read -r line; do log "$line"; done < "$out_log"
}

# command_protocols: print the basename of every protocol node that
# declares `command: true` in its frontmatter — the single home for
# "which protocols are user-facing slash commands." The user-sovereign
# meta-loop (graft/grow/harvest) carry no
# such field, so they are commands in no harness.
command_protocols() {
    local f name
    for f in "$SEED_ROOT/protocols"/*.md; do
        name="$(basename "$f" .md)"
        if awk '/^---$/{c++; next} c==1 && /^command:[[:space:]]*true[[:space:]]*$/{found=1} c>=2{exit} END{exit !found}' "$f"; then
            printf '%s\n' "$name"
        fi
    done
}

# retire_copilot_hook_duplicates — the other half of the double-injection guard.
#
# `install_github_copilot` skips `.github/hooks/` when `.claude/settings.json`
# is already there, because VS Code reads BOTH and the hook would fire twice.
# That guard only ran in one direction: install `github-copilot` first, then
# `claude-code`, and both hook sets end up wired — which is the natural order
# for a project that adopts Copilot and adds Claude Code later. Verified: two
# installs into one target, `.github/hooks/{route,status}.{py,json}` and
# `.claude/settings.json` all present.
#
# So the claude-code side retires the pair it supersedes. Not silently, and not
# irrecoverably: each file is moved to a timestamped backup beside itself, the
# same shape `place_file` produces, and the retirement is announced. A file a
# plant has edited is therefore still recoverable, and `graft-audit.py`
# classifies the backups like any other.
retire_copilot_hook_duplicates() {
    local retired=0 f bak
    for f in route-hook.py route.json status-hook.py status.json; do
        local dest="$PROJECT_DIR/.github/hooks/$f"
        [[ -e "$dest" || -L "$dest" ]] || continue
        bak="$(bak_path "$dest")"
        mv "$dest" "$bak" || die "could not retire $dest"
        retired=$((retired + 1))
        log "  retired .github/hooks/$f -> $(basename "$bak")"
    done
    [[ $retired -eq 0 ]] && return 0
    log "  (.claude/settings.json now carries these hooks, and VS Code reads it;"
    log "   leaving both wired would fire every hook twice. Backups are beside them.)"
    rmdir "$PROJECT_DIR/.github/hooks" 2>/dev/null || true
}

# generate_slash_commands DEST_DIR
# Emit one thin slash-command file per command-protocol. Each command is a
# pure PROJECTION of its protocol node: it routes the session into
# docs/graph/protocols/<name>.md, which owns the full discipline. No command
# content is authored outside the graph — the node is the single home.
generate_slash_commands() {
    local dest="$1" name tmp
    ensure_dir "$dest"
    while IFS= read -r name; do
        tmp="$(stage "command-$name.md")"
        cat > "$tmp" <<EOF
---
description: Enter the \`$name\` protocol. See docs/graph/protocols/$name.md for the full discipline.
---

<!-- GENERATED from protocols/$name.md by install.sh — do not edit here; edit the node and re-run. -->

Enter the **$name** protocol. Read \`docs/graph/protocols/$name.md\` and follow
its discipline for the current task.

Before acting, state which protocol you are entering and confirm its entry
conditions are met; if they are not, back up to the protocol that produces the
missing inputs. Then run the protocol, and end the session with
\`docs/graph/protocols/deliver.md\`.
EOF
        place_generated "$tmp" "$dest/$name.md"
    done < <(command_protocols)
}

# --- per-tool installers --------------------------------------------

install_claude_code() {
    log "installing for Claude Code in $PROJECT_DIR"
    place_kernel "$PROJECT_DIR/CLAUDE.md"
    # Harness PROJECTIONS only — the home of agents and skills is
    # docs/graph/{agents,skills}/ (place_graph_machinery); these copies
    # exist because the harness spawns agents and loads skills from
    # fixed locations. Protocols, templates, method/posture nodes have
    # no harness location and are graph-only.
    # The graph home FIRST: docs/graph/{agents,skills}/ is the one home, and the
    # harness directories below are projections of it. Projecting before the home
    # exists would project the previous run's tree.
    place_docs_skeleton
    project_agents "$PROJECT_DIR/.claude/agents"
    project_skills "$PROJECT_DIR/.claude/skills"
    # Slash commands — generated projections of the command-protocol nodes
    # (those declaring `command: true`). No authored command tree; the node
    # is the single home, the command routes into it.
    generate_slash_commands "$PROJECT_DIR/.claude/commands"
    # Settings file is placed (so the project can edit it); an edited copy is
    # backed up before replacement — a graft never destroys a plant's hook config.
    place_file "$SEED_ROOT/integrations/claude-code/settings.json" "$PROJECT_DIR/.claude/settings.json"
    retire_copilot_hook_duplicates
    # Progressive-discovery enforcement hook (referenced by settings.json).
    place_file "$SEED_ROOT/integrations/claude-code/route-hook.py" \
               "$PROJECT_DIR/.claude/route-hook.py"
    # Status-register surfacing hook (SessionStart; referenced by settings.json).
    place_file "$SEED_ROOT/integrations/claude-code/status-hook.py" \
               "$PROJECT_DIR/.claude/status-hook.py"
    # Bounded-execution guard (PreToolUse on Bash; referenced by settings.json).
    place_file "$SEED_ROOT/integrations/claude-code/bound-hook.py" \
               "$PROJECT_DIR/.claude/bound-hook.py"
    # Mechanical agent-router / roster linter / eval gate, invoked as
    # `python3 .claude/agent-lint.py` by 00-orchestrator.md, the brief
    # templates, and the deliver assertion. Scores .claude/agents/.
    place_file "$SEED_ROOT/integrations/claude-code/agent-lint.py" \
               "$PROJECT_DIR/.claude/agent-lint.py"
    place_file "$SEED_ROOT/templates/knowledge-graph/frontmatter.py" \
               "$PROJECT_DIR/.claude/frontmatter.py"
    log "Claude Code install done."
    log "  CLAUDE.md             -> core/AGENTS.md (bootstrap kernel)"
    log "  docs/graph/           -> the ONE knowledge system: method surface"
    log "                           (protocols, skills, agents, method, templates) + project graph"
    log "  .claude/agents/       (harness projection of docs/graph/agents/)"
    log "  .claude/skills/       (harness projection of docs/graph/skills/)"
    log "  .claude/commands/     (tool-specific slash commands)"
    log "  .claude/settings.json (commit to share with team)"
    log_registration_notice ".claude/agents/"
}

install_opencode() {
    log "installing for opencode in $PROJECT_DIR"
    place_kernel "$PROJECT_DIR/AGENTS.md"   # NOT raw place_file: the kernel
    # may already be the CLAUDE.md-shared file; bypassing place_kernel made
    # this call and prime-agent's ping-pong the file into fresh .bak churn
    # on every re-run
    # Harness projections of docs/graph/{agents,skills}/ (the home).
    # The graph home FIRST: docs/graph/{agents,skills}/ is the one home, and the
    # harness directories below are projections of it. Projecting before the home
    # exists would project the previous run's tree.
    place_docs_skeleton
    project_agents "$PROJECT_DIR/.opencode/agents"
    project_skills "$PROJECT_DIR/.opencode/skills"
    # Slash commands — the same generated projections as every other harness.
    generate_slash_commands "$PROJECT_DIR/.opencode/commands"
    # ONE config file only. opencode reads opencode.json OR opencode.jsonc and
    # the precedence between two files at the same tier is unspecified — the
    # seed shipped both and let the harness pick. Strict JSON is also the form
    # tests/seed-lint.py and tests/test-full-install.sh can parse; the rationale
    # for what this file does NOT declare lives in integrations/opencode/README.md.
    place_file "$SEED_ROOT/integrations/opencode/opencode.json" "$PROJECT_DIR/opencode.json"
    log "opencode install done."
    log "  AGENTS.md             -> core/AGENTS.md (bootstrap kernel)"
    log "  docs/graph/           -> the ONE knowledge system (method surface + project graph)"
    log "  .opencode/agents/     (harness projection of docs/graph/agents/)"
    log "  .opencode/skills/     (harness projection of docs/graph/skills/)"
    log "  .opencode/commands/   (tool-specific slash commands)"
    log "  opencode.json         (commit to share with team)"
    log_registration_notice ".opencode/agents/"
}

install_codex() {
    log "installing for Codex CLI in $PROJECT_DIR"
    place_kernel "$PROJECT_DIR/AGENTS.md"   # NOT raw place_file: the kernel
    # may already be the CLAUDE.md-shared file; bypassing place_kernel made
    # this call and prime-agent's ping-pong the file into fresh .bak churn
    # on every re-run
    # Harness projections of docs/graph/{agents,skills}/ (the home).
    # The graph home FIRST: docs/graph/{agents,skills}/ is the one home, and the
    # harness directories below are projections of it. Projecting before the home
    # exists would project the previous run's tree.
    place_docs_skeleton
    project_agents "$PROJECT_DIR/.codex/agents"
    project_skills "$PROJECT_DIR/.codex/skills"

    # Generate config snippet with resolved paths.
    # The path is substituted LITERALLY, in Python, not through a sed
    # replacement: `&` in a sed replacement expands to the whole match, `\`
    # escapes, and `|` closes the expression, so a project directory
    # containing any of them silently produced a corrupt path — and the
    # snippet is what the owner pastes into ~/.codex/config.toml, so the
    # corruption lands in a config file rather than failing loudly here.
    # TOML basic strings also need `\` and `"` escaped, which sed never did.
    local snippet="$PROJECT_DIR/.codex/codex-config-snippet.toml" tmp
    tmp="$(stage "codex-config-snippet.toml")"
    PROJECT_DIR="$PROJECT_DIR" python3 - \
        "$SEED_ROOT/integrations/codex/config.toml.example" "$tmp" <<'PYEOF'
import os, sys
src, dst = sys.argv[1], sys.argv[2]
# TOML basic-string escaping for the one value we substitute.
#
# `\\` and `"` are not the whole set. A TOML basic string also forbids a raw
# newline, tab or carriage return, and this file is what the owner PASTES into
# ~/.codex/config.toml — so an unescaped one lands as a corrupt config in their
# editor rather than failing loudly here. Verified: a target directory whose
# name contains a newline produced a snippet that `tomllib` refuses, at exit 0
# with no warning. That is U-08's own stated harm, one metacharacter further out
# than the five names its test set covers.
_TOML_ESCAPES = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r",
                 "\t": "\\t", "\f": "\\f", "\b": "\\b"}
path = "".join(_TOML_ESCAPES.get(ch, ch) for ch in os.environ["PROJECT_DIR"])
with open(src, encoding="utf-8") as fh:
    text = fh.read()
with open(dst, "w", encoding="utf-8") as fh:
    fh.write(text.replace("/abs/path/to/project", path))
PYEOF
    place_generated "$tmp" "$snippet"
    log "Codex install done."
    log "  AGENTS.md            -> core/AGENTS.md (bootstrap kernel)"
    log "  docs/graph/          -> the ONE knowledge system (method surface + project graph)"
    log "  .codex/agents/       (harness projection of docs/graph/agents/)"
    log "  .codex/skills/       (harness projection of docs/graph/skills/)"
    log ""
    log "ACTION NEEDED: merge this snippet into ~/.codex/config.toml:"
    log "  $snippet"
    if [[ $PRINT_CONFIG -eq 1 ]]; then
        echo "----- BEGIN ~/.codex/config.toml additions -----"
        cat "$snippet"
        echo "----- END -----"
    fi
    log_registration_notice ".codex/agents/"
}

install_github_copilot() {
    log "installing for GitHub Copilot in $PROJECT_DIR"
    # Repo-root kernel — Copilot reads both .github/copilot-instructions.md AND AGENTS.md.
    # place_file, not cp: a raw cp onto an existing symlink writes THROUGH it
    # and clobbers the target file; place_file's backup mv takes the link itself.
    ensure_dir "$PROJECT_DIR/.github"
    # Copilot reads this file on every session, so a project that already had
    # one had its own always-loaded instructions replaced — with a .bak and no
    # ledger entry, because this path goes through place_file rather than
    # place_kernel. The sweep did not reach it either (it globs the repo root),
    # so it was a permanent gap rather than a race something later closes.
    local _cop="$PROJECT_DIR/.github/copilot-instructions.md" _cop_had=0
    [[ -f "$_cop" && ! -L "$_cop" ]] && ! cmp -s "$SEED_ROOT/core/AGENTS.md" "$_cop" \
        && _cop_had=1
    place_file "$SEED_ROOT/core/AGENTS.md" "$_cop"
    if [[ $_cop_had -eq 1 ]]; then
        record_instruction_migration "$_cop" \
            "$(ls -1dt "$_cop".bak-* 2>/dev/null | head -1)"
    fi
    place_kernel "$PROJECT_DIR/AGENTS.md"   # NOT raw place_file: the kernel
    # may already be the CLAUDE.md-shared file; bypassing place_kernel made
    # this call and prime-agent's ping-pong the file into fresh .bak churn
    # on every re-run

    # Agents -> .github/agents/<name>.agent.md (transformed frontmatter)
    # The graph home FIRST: docs/graph/{agents,skills}/ is the one home, and the
    # harness directories below are projections of it. Projecting before the home
    # exists would project the previous run's tree.
    place_docs_skeleton
    ensure_dir "$PROJECT_DIR/.github/agents"
    for f in "$PROJECT_DIR/docs/graph/agents"/*.md; do
        [[ -f "$f" ]] || continue
        case "$(basename "$f")" in _*|index.md|README.md) continue ;; esac
        local name tmp; name="$(basename "$f" .md | sed -E 's/^[0-9]+-//')"
        # Strip the universal frontmatter; rewrite for Copilot. Generated into
        # the run's scratch dir and then PLACED, so a plant edit is backed up
        # and a destination symlink is replaced rather than written through.
        tmp="$(stage "copilot-agent-$name.md")"
        python3 - "$f" "$tmp" <<'PYEOF'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    open(dst, "w").write(text); sys.exit(0)
fm = m.group(1)
body = text[m.end():]
desc = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.S | re.M)
description = (desc.group(1).strip() if desc else "").replace("\n", " ").strip()
# Per-agent tool mapping — the source frontmatter's tools: allowlist IS the
# discipline; projecting one fixed superset (the old behavior) silently gave
# read-only agents editFiles/runCommands on Copilot.
tm = re.search(r"^tools:\s*\[([^\]]*)\]", fm, re.M)
src_tools = {t.strip() for t in (tm.group(1).split(",") if tm else []) if t.strip()}
# read set + runCommands always: the GRAPH DISCIPLINE bootstrap mandates
# `python3 docs/graph/graph-lint.py --plan` / agent-lint --route in EVERY
# session, so command execution is a baseline capability on Copilot even for
# Bash-less charters. Write access (editFiles) and web reach (fetch,
# githubRepo — a REMOTE GitHub search, not local) stay allowlist-derived;
# runTasks (workspace task runner) requires Bash. `Task` (subagent spawning)
# has no Copilot equivalent and is not projected.
cop = ["codebase", "search", "usages", "findTestFiles", "runCommands"]
if src_tools & {"Write", "Edit"}:
    cop.append("editFiles")
if "Bash" in src_tools:
    cop.append("runTasks")
if src_tools & {"WebSearch", "WebFetch"}:
    cop += ["fetch", "githubRepo"]
tools_line = "tools: [" + ", ".join(f"'{t}'" for t in cop) + "]"
out = (
    "---\n"
    f"description: {description}\n"
    f"{tools_line}\n"
    "---\n\n"
    f"<!-- GENERATED from {src.rsplit('/', 1)[-1]} by install.sh github-copilot — do not edit here; edit the seed source and re-run. -->\n\n"
) + body
open(dst, "w").write(out)
PYEOF
        place_generated "$tmp" "$PROJECT_DIR/.github/agents/$name.agent.md"
    done

    # Protocols -> .github/prompts/<name>.prompt.md, one per command-protocol
    # (frontmatter `command: true`). The user-sovereign meta-loop protocols
    # (graft/grow/harvest) carry no command
    # field, so they are not exposed as Copilot prompts either; the command
    # surface a user sees is the same on every harness.
    ensure_dir "$PROJECT_DIR/.github/prompts"
    local name f tmp generated=" "
    while IFS= read -r name; do
        f="$SEED_ROOT/protocols/$name.md"
        tmp="$(stage "copilot-prompt-$name.md")"
        python3 - "$f" "$tmp" <<'PYEOF'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
fm = m.group(1) if m else ""
body = text[m.end():] if m else text
desc = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.S | re.M)
description = (desc.group(1).strip() if desc else "").replace("\n", " ").strip()
out = (
    "---\n"
    "mode: 'agent'\n"
    f"description: {description}\n"
    "tools: ['codebase', 'editFiles', 'fetch', 'findTestFiles', "
    "'githubRepo', 'search', 'usages', 'runCommands']\n"
    "---\n\n"
    f"<!-- GENERATED from {src.rsplit('/', 1)[-1]} by install.sh github-copilot — do not edit here; edit the seed source and re-run. -->\n\n"
) + body
open(dst, "w").write(out)
PYEOF
        place_generated "$tmp" "$PROJECT_DIR/.github/prompts/$name.prompt.md"
        generated="$generated$name.prompt.md "
    done < <(command_protocols)
    # A prompt in that directory this run did not write is a leftover from a
    # generator that no longer produces it — a protocol that stopped carrying
    # `command: true`, or one the seed retired. It is NOT the installer's to
    # delete: this installer acts only on files it can prove it wrote, which is
    # the rule that bounds sweep_orphaned_instruction_backups too, and deleting
    # by inference is how a tool destroys work somebody meant to keep. Left
    # unmentioned, though, a stale prompt goes on being offered as a current
    # command. Name it, and leave the decision with the owner.
    local stray
    for stray in "$PROJECT_DIR/.github/prompts"/*.prompt.md; do
        [[ -f "$stray" ]] || continue
        case "$generated" in *" $(basename "$stray") "*) continue ;; esac
        warn "  .github/prompts/$(basename "$stray") is not generated by this seed;"
        warn "    left in place — remove it if the command it names is gone"
    done

    # Skills -> .github/instructions/<name>-skill.instructions.md
    ensure_dir "$PROJECT_DIR/.github/instructions"
    # From the GRAPH, like every other adapter: a skill the plant authored is
    # in docs/graph/skills/ and nowhere else, and this loop is what puts it in
    # front of the harness.
    for f in "$PROJECT_DIR/docs/graph/skills"/*.md; do
        [[ -f "$f" ]] || continue
        case "$(basename "$f")" in _*|index.md|README.md) continue ;; esac
        local name tmp; name="$(basename "$f" .md)"
        tmp="$(stage "copilot-skill-$name.md")"
        python3 - "$f" "$tmp" <<'PYEOF'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
fm = m.group(1) if m else ""
body = text[m.end():] if m else text
desc = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.S | re.M)
description = (desc.group(1).strip() if desc else "").replace("\n", " ").strip()
# A POINTER, not the body. `applyTo: '**'` applies a file to every file in
# the workspace, so shipping every skill body this way made Copilot load
# 138 535 bytes (~34 600 tokens) before any routing — over five times every other
# harness, and the exact inversion of the progressive discovery this seed is
# built on. The bodies already live in docs/graph/skills/, which is the one
# home; what belongs in an always-applied file is the description that lets a
# session decide whether to open one, and the path to open.
# The description is NOT repeated in the body: `applyTo` applies the whole
# file, frontmatter included, so restating it there would pay for it twice.
stem = src.rsplit("/", 1)[-1].rsplit(".", 1)[0]
out = (
    "---\n"
    f"description: {description}\n"
    "applyTo: '**'\n"
    "---\n\n"
    f"<!-- GENERATED from {src.rsplit('/', 1)[-1]} by install.sh github-copilot — do not edit here; edit the seed source and re-run. -->\n\n"
    f"Pointer only — this file is applied to every file in the workspace.\n"
    f"Read `docs/graph/skills/{stem}.md` in full before acting on this skill;\n"
    f"the steps, contracts and failure modes are there, not here.\n"
)
open(dst, "w").write(out)
PYEOF
        place_generated "$tmp" "$PROJECT_DIR/.github/instructions/$name-skill.instructions.md"
    done

    # Progressive-discovery enforcement hook for VS Code Agent Hooks
    # (Preview). VS Code also reads .claude/settings.json hooks, so only
    # install the .github/hooks/ config when the Claude Code hook is
    # absent — otherwise the hook would fire twice.
    if [[ -f "$PROJECT_DIR/.claude/settings.json" ]]; then
        log "  (skipping .github/hooks/ — .claude/settings.json already carries the hook, which VS Code reads)"
    else
        ensure_dir "$PROJECT_DIR/.github/hooks"
        place_file "$SEED_ROOT/integrations/claude-code/route-hook.py" \
                   "$PROJECT_DIR/.github/hooks/route-hook.py"
        place_file "$SEED_ROOT/integrations/github-copilot/hooks/route.json" \
                   "$PROJECT_DIR/.github/hooks/route.json"
        place_file "$SEED_ROOT/integrations/claude-code/status-hook.py" \
                   "$PROJECT_DIR/.github/hooks/status-hook.py"
        place_file "$SEED_ROOT/integrations/github-copilot/hooks/status.json" \
                   "$PROJECT_DIR/.github/hooks/status.json"
        log "  .github/hooks/route.json + route-hook.py (enforce progressive discovery)"
        log "  .github/hooks/status.json + status-hook.py (status register at session start)"
    fi

    log "GitHub Copilot install done."
    log "  .github/copilot-instructions.md       (bootstrap kernel)"
    log "  AGENTS.md                              (kernel mirror)"
    log "  docs/graph/                            (the ONE knowledge system: method surface + project graph)"
    log "  .github/agents/<name>.agent.md         (harness projection, transformed from docs/graph/agents/)"
    log "  .github/prompts/<name>.prompt.md       (harness projection, transformed from docs/graph/protocols/)"
    log "  .github/instructions/<name>-skill.*    (harness projection, transformed from docs/graph/skills/)"
    log_registration_notice ".github/agents/"
}


install_prime_agent() {
    log "installing for Prime Agent in $PROJECT_DIR"
    # Kernel — Prime Agent auto-loads AGENTS.md (or CLAUDE.md) from the repo
    # root (AGENTS.md wins in a directory). place_kernel shares ONE kernel file
    # with a co-installed Claude Code (CLAUDE.md), so a single plant runs both
    # harnesses interchangeably off byte-identical project instructions.
    place_kernel "$PROJECT_DIR/AGENTS.md"
    # Roster BRIEF SOURCES. Prime Agent has NO static roster enumerated at
    # session start; delegation is a runtime rlm() spawn with an inline brief.
    # So agents/*.md land as on-disk brief sources the orchestrator reads and
    # embeds into rlm() calls. The golden routing corpus rides along (place_tree
    # skips the non-*.md file) so agent-lint.py can score the roster in CI —
    # the SAME gate claude-code runs, pointed at this dir (full parity).
    # The graph home FIRST: docs/graph/{agents,skills}/ is the one home, and the
    # harness directories below are projections of it. Projecting before the home
    # exists would project the previous run's tree.
    place_docs_skeleton
    project_agents "$PROJECT_DIR/.prime/agent/agents"
    # Skills — the same Agent-Skills SKILL.md shape, no transform.
    project_skills "$PROJECT_DIR/.prime/agent/skills"
    # Slash commands — generated prompt-template projections of the
    # command-protocol nodes, the same roster as every other harness.
    generate_slash_commands "$PROJECT_DIR/.prime/agent/prompts"
    # Progressive-discovery enforcement extension (before_agent_start) — the
    # Prime Agent parity of claude-code's route-hook.py. Copied so it is editable.
    ensure_dir "$PROJECT_DIR/.prime/agent/extensions"
    place_file "$SEED_ROOT/integrations/prime-agent/route-extension.ts" \
               "$PROJECT_DIR/.prime/agent/extensions/route-extension.ts"
    # Status-register surfacing (first prompt of the session) — parity of status-hook.py.
    place_file "$SEED_ROOT/integrations/prime-agent/status-extension.ts" \
               "$PROJECT_DIR/.prime/agent/extensions/status-extension.ts"
    # Settings — placed (so the project can edit it); an edited copy is backed up.
    place_file "$SEED_ROOT/integrations/prime-agent/settings.json" "$PROJECT_DIR/.prime/agent/settings.json"
    # Native-execution overlay — APPENDED to Prime Agent's system prompt every
    # session (Claude Code never reads it). Teaches the model to run the seed's
    # discipline with Prime Agent's RLM-native primitives (recursive rlm()
    # subagents, the continual harness, agent_message handbacks, in-kernel gates)
    # instead of emulating a file-based harness. Copied so the project can edit it.
    place_file "$SEED_ROOT/integrations/prime-agent/APPEND_SYSTEM.md" \
               "$PROJECT_DIR/.prime/agent/APPEND_SYSTEM.md"
    log "Prime Agent install done."
    log "  AGENTS.md                  -> core/AGENTS.md (bootstrap kernel, auto-loaded)"
    log "  docs/graph/                -> the ONE knowledge system: method surface + project graph"
    log "  .prime/agent/agents/       (roster BRIEF SOURCES — read one, spawn an rlm() child with it)"
    log "  .prime/agent/skills/       (harness projection of docs/graph/skills/)"
    log "  .prime/agent/prompts/      (slash-command prompt templates)"
    log "  .prime/agent/extensions/   (route-extension.ts — progressive discovery; status-extension.ts — status register)"
    log "  .prime/agent/settings.json (commit to share with team)"
    log "  .prime/agent/APPEND_SYSTEM.md (RLM-native execution overlay — appended to the system prompt)"
    # Unlike claude-code/opencode, Prime Agent does NOT enumerate a roster at
    # session start, so there is no "installed but not spawnable" lag here: a
    # brief written to .prime/agent/agents/ is usable by the very next rlm()
    # call in the same session. One home for the rule and why it does not bite
    # here: core/method/delegation.md (delegation.harness-registration).
    log ""
    log "NOTE: no roster-registration restart is needed on Prime Agent — the"
    log "  briefs in .prime/agent/agents/ are usable IMMEDIATELY by rlm()"
    log "  (docs/graph/method/delegation.md, delegation.harness-registration)."
}

# --- args ------------------------------------------------------------

usage() {
    sed -n '/^# install.sh/,/^$/p' "$0" | sed -E 's/^# ?//'
    exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        claude-code|opencode|codex|github-copilot|prime-agent|all) TOOLS+=("$1"); shift ;;
        --project-dir)
            # A bare `cd` here surfaced the shell's error, not this tool's —
            # `cd: /path: No such file or directory` — which is the one thing
            # ensure_dir and preflight_destinations exist to stop happening
            # anywhere else. INSTALL.md's own example does not imply the target
            # must already exist, and every test in the suite happens to
            # `mkdir -p` first, so this was the one unexercised path.
            [[ -e "$2" ]] || die "--project-dir: no such directory: $2
  Create it first, or point at an existing project."
            [[ -d "$2" ]] || die "--project-dir: not a directory: $2"
            # `-P`, physically, on both halves. A LOGICAL pwd leaves
            # PROJECT_DIR naming the symlink the user typed, and `find` does not
            # follow a symlink given as its START path — so BOTH deep preflight
            # walks, the unwritable-directory one and the escaping-symlink one
            # added to close exactly this class, enumerated nothing:
            #     find /tmp/x/link -type d | wc -l  ->  0
            #     find /tmp/x/real -type d | wc -l  ->  68
            # Verified: a target reached through a symlink, with
            # docs/graph/protocols pointing outside it, wrote 14 protocol nodes
            # outside --project-dir, REPLACED a pre-existing file out there,
            # left a .bak beside it, and exited 0. Only the final component
            # matters — a mid-path symlink still refused — which is what made it
            # survive a six-shape sweep that always passed a real path.
            PROJECT_DIR="$(cd -P "$2" && pwd -P)"; shift 2 ;;
        --symlink) LINK_MODE="symlink"; shift ;;
        --copy)    LINK_MODE="copy";    shift ;;
        --force)   FORCE=1; shift ;;
        --print-config) PRINT_CONFIG=1; shift ;;
        --check)   CHECK=1; shift ;;
        --environment-class)   PLANT_ENV="$2";  shift 2 ;;
        --commit-attribution)  PLANT_ATTR="$2"; shift 2 ;;
        --deliverable-language) PLANT_DLANG="$2"; shift 2 ;;
        --comment-language)    PLANT_CLANG="$2"; shift 2 ;;
        --legal-corpus)        LEGAL_CORPUS="$2"; shift 2 ;;
        --legal-jurisdiction)  LEGAL_JURISDICTION="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"; shift 2 ;;
        -h|--help) usage 0 ;;
        *) die "unknown argument: $1 (try --help)" ;;
    esac
done

[[ ${#TOOLS[@]} -gt 0 ]] || die "no tool specified (try --help)"
case "${PLANT_ENV:-}" in
    ""|ephemeral-test|staging|real-production|mixed) ;;
    *) die "--environment-class must be one of ephemeral-test | staging | real-production | mixed (got: $PLANT_ENV)" ;;
esac
case "${LEGAL_CORPUS:-}" in
    ""|yes|no) ;;
    *) die "--legal-corpus must be yes or no (got: $LEGAL_CORPUS). The corpus is placed whole or not at all; a subset is not an option." ;;
esac
# `no` means "this plant carries no legal corpus". Recording it while a corpus
# is ON DISK made the stamp state a falsehood: `agent.legal` reads the corpus,
# not the stamp, so the plant kept answering from instruments its own record
# said it did not have — and the coverage audit compares the two.
# The installer will not resolve that by DELETING the corpus. Removing law a
# plant may already have reasoned from is a destructive, user-sovereign act,
# and nothing in the seed may take it silently. So the contradiction is
# refused, and the two honest ways out are named.
if [[ "${LEGAL_CORPUS:-}" == "no" ]]; then
    # `set -o pipefail` is on: `find` on a missing directory fails the whole
    # pipeline, so the directory is tested before it is counted. A fresh plant
    # recording "no corpus" is the normal case and must not be refused.
    _corpus_dir="$PROJECT_DIR/docs/graph/legal/corpus"
    _corpus_pages="$(corpus_pages "$_corpus_dir" '*.md')"
    if [[ "${_corpus_pages:-0}" -gt 0 ]]; then
        die "refusing --legal-corpus no: $_corpus_pages corpus page(s) are installed at
  docs/graph/legal/corpus/
  Recording \"no\" would make .cypress/seed.json contradict the filesystem, and
  agent.legal answers from the corpus rather than from the stamp. This installer
  does not delete law a plant may already have reasoned from.
  Either keep the corpus and re-run with --legal-corpus yes, or remove it
  deliberately first (rm -rf docs/graph/legal/corpus) and then record no."
    fi
fi
case "${LEGAL_JURISDICTION:-}" in
    ""|[a-z][a-z]) ;;
    *) die "--legal-jurisdiction must be a two-letter country code (got: $LEGAL_JURISDICTION)" ;;
esac

# Which national jurisdictions the corpus actually carries, derived from the
# filenames rather than listed here — legal-corpus/README.md fixes the
# `<cc>-<instrument>.md` convention, and a second list would drift the moment
# an ingest lands.
corpus_jurisdictions() {
    local f
    for f in "$SEED_ROOT"/legal-corpus/national/*.md; do
        [[ -e "$f" ]] || continue
        basename "$f" | sed 's/-.*//'
    done | sort -u
}

# Sanity: refuse to install into the seed itself.
[[ "$PROJECT_DIR" != "$SEED_ROOT" ]] || die \
    "refusing to install the seed system into itself; pass --project-dir"

# Host support tiers — the one home of the assignment (ADR-0009,
# docs/decisions/adr-0009-host-support-tiers.md). documentation/host-capability-matrix.md
# publishes it, and tests/seed-lint.py (check_host_tiers) holds that table to
# these arrays and `all` to the first two. `all` below is written out rather
# than concatenated from them: the concatenation would put prime-agent ahead of
# opencode and change install order for no reason.
FIRST_CLASS_TOOLS=(claude-code prime-agent)
SUPPORTED_TOOLS=(opencode)
FROZEN_TOOLS=(codex github-copilot)

# Expand 'all'
expanded=()
for t in "${TOOLS[@]}"; do
    case "$t" in
        all) expanded+=(claude-code opencode prime-agent) ;;
        *)   expanded+=("$t") ;;
    esac
done

# `all --check` also checks the Copilot views of a plant whose record carries
# github-copilot (SPEC-0001, ALL_CHECK_INCLUDES_RECORDED_COPILOT). Checking
# writes nothing, so it is no new feature on a frozen host, and a CI job that
# ran `all --check` before ADR-0009 keeps failing on drift instead of turning
# green because `all` stopped naming the only host --check can check.
_recorded_tools=" $(stamp_field "$PROJECT_DIR/.cypress/seed.json" tools) "
if [[ $CHECK -eq 1 && " ${TOOLS[*]} " == *" all "* \
      && " ${expanded[*]} " != *" github-copilot "* \
      && "$_recorded_tools" == *" github-copilot "* ]]; then
    expanded+=(github-copilot)
fi

# Frozen hosts, announced once each, here and not inside install_codex /
# install_github_copilot: this point is ahead of the --check branch, so the
# notice reaches every run that acts on a frozen host, a --check included, and
# the frozen adapters stay byte-unchanged. A plant whose record carries a frozen
# host that `all` no longer names would otherwise keep that host's projections
# at the old seed version unannounced (SPEC-0001, FROZEN_PROJECTION_LEFT_STALE);
# its tree is left exactly as it is.
for t in "${FROZEN_TOOLS[@]}"; do
    if [[ " ${expanded[*]} " == *" $t "* ]]; then
        deprecated "$t"
    elif [[ " ${TOOLS[*]} " == *" all "* && "$_recorded_tools" == *" $t "* ]]; then
        warn "$t not refreshed: .cypress/seed.json records it, and \`all\` no longer installs a frozen host (ADR-0009), so its files stay as they were. Refresh them with: install.sh all $t"
    fi
done

# PRIOR_INSTALL — snapshotted HERE, before this run places a single byte, so
# write_seed_stamp (which creates .cypress/seed.json on a fresh install) can
# never make a fresh install look like a re-install to place_file's D2 check.
#
# From more than one signal, because the stamp alone was too fragile to carry
# three mechanisms. `.cypress/` is gitignored by this very repository, so a
# plant that commits its seed and is then freshly cloned arrives with the whole
# graph on disk and no stamp — and everything keyed on PRIOR_INSTALL went quiet:
# the D2 re-creation notice was suppressed while nodes were silently restored,
# `sweep_orphaned_instruction_backups` returned at its first line so a backup of
# the team's own CLAUDE.md was never filed as work, and the recorded corpus and
# jurisdiction decisions were reset. Absence of the record is not absence of the
# plant. A populated machinery directory says so just as well.
if [[ -f "$PROJECT_DIR/.cypress/seed.json" ]]; then
    PRIOR_INSTALL=1
elif [[ -d "$PROJECT_DIR/docs/graph/protocols" ]] \
     && [[ -n "$(find "$PROJECT_DIR/docs/graph/protocols" -name '*.md' -print -quit 2>/dev/null)" ]]; then
    PRIOR_INSTALL=1
    warn "this target carries docs/graph/protocols/ but no .cypress/seed.json."
    warn "  Treating it as an existing plant whose record is missing (the seed's"
    warn "  own .gitignore carries .cypress/, so a fresh clone arrives this way)."
    warn "  Owner decisions it recorded — the legal corpus and its jurisdiction —"
    warn "  cannot be recovered from disk; re-state them with their flags if they"
    warn "  applied."
fi

# The owner's RECORDED corpus decision drives placement, not just this run's
# flag. Without this, a plant that decided `yes` and then lost the corpus
# out-of-band kept a stamp saying `yes` over an empty directory, reachable by an
# entirely ordinary sequence: decide yes, delete the corpus, later add a second
# adapter with no legal flag at all. The refusal path only ever fired on an
# explicit `--legal-corpus no`, so nothing re-checked the recorded decision
# against the disk, and S6 ("the record cannot contradict the filesystem") had a
# hole that never required the owner to type anything wrong.
# Inheriting the decision here closes it at the source: the corpus is restored
# to match what the plant says it carries. Restoring is announced rather than
# silent, because a plant that deleted those pages on purpose deserves to be
# told the fast-forward brought them back — the same rule as D2.
if [[ -z "${LEGAL_CORPUS:-}" && $PRIOR_INSTALL -eq 1 ]]; then
    _recorded="$(stamp_field "$PROJECT_DIR/.cypress/seed.json" legal_corpus)"
    if [[ "$_recorded" == "yes" ]]; then
        LEGAL_CORPUS="yes"
        _corpus_dir="$PROJECT_DIR/docs/graph/legal/corpus"
        _have="$(corpus_pages "$_corpus_dir" '*.md')"
        # Guarded like the rest: an absent seed corpus made `find` fail the
        # pipeline under `pipefail` and killed the run with a raw shell error,
        # never reaching place_legal_corpus's own graceful die.
        # '*.md' on BOTH sides. `_have` counted '*.md' and `_want` the default
        # '*', balancing only because every seed corpus file happens to be .md
        # today. One ingest artifact — a .csv of retention periods, a .json
        # index — and a plant carrying the COMPLETE corpus is told "16 of 17
        # pages" on every install, for ever, with destructive advice attached.
        _want="$(corpus_pages "$SEED_ROOT/legal-corpus" '*.md')"
        if [[ "${_have:-0}" -lt "$_want" ]]; then
            warn "legal corpus: this plant records \`legal_corpus: yes\` but carries"
            warn "  ${_have:-0} of $_want pages. Restoring the whole corpus to match the"
            warn "  record. If those pages were removed deliberately, re-run with"
            warn "  --legal-corpus no AFTER removing them again, so the record agrees."
        fi
    elif [[ "$_recorded" == "undecided" || -z "$_recorded" ]]; then
        # The third arm, and it was missing. `yes` and `no` each re-check the
        # disk; `undecided` — the DEFAULT, and the state the installer's own
        # NEXT STEP tells the owner to sit in while deciding — had none. So an
        # ingest could land pages under legal/corpus/ and every later install
        # exited 0 with the record still saying `undecided` over 8 statutes on
        # disk, which agent.legal answers from. RECORD_AGREES_WITH_DISK covers
        # one of three enum values without this.
        _corpus_dir="$PROJECT_DIR/docs/graph/legal/corpus"
        _have="$(corpus_pages "$_corpus_dir" '*.md')"
        if [[ "${_have:-0}" -gt 0 ]]; then
            warn "legal corpus: this plant records \`legal_corpus: undecided\` and carries"
            warn "  ${_have:-0} page(s) at docs/graph/legal/corpus/. agent.legal answers from"
            warn "  the corpus, not the stamp, so the record understates what it can reach."
            warn "  Re-run with --legal-corpus yes to record what is there, or remove the"
            warn "  pages and re-run with --legal-corpus no."
        fi
    elif [[ "$_recorded" == "no" ]]; then
        # The symmetric half, and it was missing. RECORD_AGREES_WITH_DISK says
        # the stamp cannot contradict the filesystem, and the check above only
        # ever ran for `yes`. So: install with --legal-corpus no, let an ingest
        # land pages under legal/corpus/, re-install silently — exit 0, no
        # warning, and the record says `no` over statutes that are on disk and
        # that agent.legal will answer from. The flag path at :1381 refuses
        # exactly this; silence did not.
        _corpus_dir="$PROJECT_DIR/docs/graph/legal/corpus"
        _have="$(corpus_pages "$_corpus_dir" '*.md')"
        if [[ "${_have:-0}" -gt 0 ]]; then
            die "this plant records \`legal_corpus: no\` and carries ${_have:-0} corpus\
 page(s) at docs/graph/legal/corpus/. The record would contradict the filesystem, and\
 agent.legal answers from the corpus rather than from the stamp. Either re-run with\
 --legal-corpus yes to record what is there, or remove those pages and re-run."
        fi
    fi
fi

# adapter_dirs TOOL — the destination directories (relative to PROJECT_DIR)
#
# This list is a SECOND HOME for something the install_* functions already know,
# and it drifted within one release of being written: `.github/hooks` was
# missing, so a target carrying a FILE at that path still wrote 195 files and
# then died on the same raw `mkdir` error the preflight exists to replace.
# tests/test-install-adoption.sh now derives the real directory set from an
# actual install of every adapter and fails when this list does not cover it —
# the list stays hand-written, but it can no longer be quietly incomplete.
# that installing TOOL will create. Read by preflight_destinations below so a
# `claude-code`-only run is never refused over an unrelated `.github` file it
# will never touch (D1) — the check is derived from the SELECTED adapters,
# not a hardcoded list of all five integrations.
adapter_dirs() {
    case "$1" in
        claude-code)    printf '%s\n' docs docs/graph \
                             .claude .claude/agents .claude/skills .claude/commands ;;
        opencode)       printf '%s\n' docs docs/graph \
                             .opencode .opencode/agents .opencode/skills .opencode/commands ;;
        codex)          printf '%s\n' docs docs/graph \
                             .codex .codex/agents .codex/skills ;;
        github-copilot) printf '%s\n' docs docs/graph \
                             .github .github/agents .github/prompts \
                             .github/instructions .github/hooks ;;
        prime-agent)    printf '%s\n' docs docs/graph .prime .prime/agent \
                             .prime/agent/agents .prime/agent/skills \
                             .prime/agent/prompts .prime/agent/extensions ;;
    esac
}

# Does a path resolve to somewhere still inside PROJECT_DIR? Used by the
# preflight to refuse a destination that would carry writes out of the target.
# `cd -P` resolves symlinks without needing `realpath`, which is not portable
# (BSD lacks the GNU flags, and this file supports bash 3.2).
dest_inside_target() {
    local path="$1" real root
    real="$(cd -P "$path" 2>/dev/null && pwd -P)" || return 1
    root="$(cd -P "$PROJECT_DIR" 2>/dev/null && pwd -P)" || return 1
    [[ "$real" == "$root" || "$real" == "$root"/* ]]
}

# preflight_destinations — D1 CRASH / PARTIAL INSTALL. Until this check, a
# destination directory that already existed as a REGULAR FILE (or a symlink
# to one) — e.g. a project that happens to contain a file literally named
# `.claude` — let place_kernel and the whole docs/graph/ scaffold run to
# completion and then die on a raw, unwrapped `mkdir: ... Not a directory`
# several placements later, deep inside place_tree/place_file — never this
# tool's own die(). The target was left half-installed: CLAUDE.md, AGENTS.md
# and a full docs/graph/ tree on disk, no .claude/ at all. Running this ONCE,
# before place_kernel or place_docs_skeleton ever writes anything, turns that
# into a clean refusal that names every offending path and nothing on disk.
preflight_destinations() {
    local dirs=() t d rel path bad=()
    # docs/ and .cypress/ are written on EVERY run regardless of which
    # adapters were picked (place_docs_skeleton, write_seed_stamp) so they are
    # always checked; everything else comes only from the adapters actually
    # requested this run.
    # `docs/graph/plans` is here because record_instruction_migration writes
    # into it AFTER place_kernel has already replaced the plant's own
    # instruction file. Blocked, that died cleanly — but with the kernel
    # already overwritten and no note written, and the NEXT run saw no
    # deviation (the kernel now matches the seed) so it never filed one
    # either. The original body sat in a .bak nobody would ever be told about.
    # Refusing here means the kernel is untouched when that path is in the way.
    dirs=(docs docs/graph docs/graph/plans .cypress)
    for t in "${expanded[@]}"; do
        while IFS= read -r d; do
            [[ -n "$d" ]] && dirs+=("$d")
        done < <(adapter_dirs "$t")
    done

    local seen=" "
    for rel in "${dirs[@]}"; do
        [[ "$seen" == *" $rel "* ]] && continue
        seen+="$rel "
        path="$PROJECT_DIR/$rel"
        # `-e` alone misses a DANGLING symlink (false when the referent is
        # gone) and `-d` alone follows a symlink so a symlink-to-a-file reads
        # as "not a directory" correctly; combined, this catches a plain
        # file, a symlink to one, and a dangling symlink — every shape that
        # makes `mkdir -p` fail with the raw, unwrapped error D1 named.
        if [[ ( -e "$path" || -L "$path" ) && ! -d "$path" ]]; then
            bad+=("$path")
        elif [[ -L "$path" && -d "$path" ]] && ! dest_inside_target "$path"; then
            # A symlink TO A DIRECTORY passes both tests above: -e is true and
            # -d follows the link, so `! -d` is false and nothing flagged it.
            # `mkdir -p` then succeeds and every later write goes THROUGH the
            # link, landing outside the target — reproduced with `.cypress`
            # symlinked out, which put seed.json outside the plant. An install
            # that writes outside PROJECT_DIR breaks the invariant this file
            # states at the top, so it is refused here rather than discovered
            # afterwards. A symlink that stays inside the target is fine and is
            # deliberately still allowed.
            bad+=("$path (symlink leaving the target: $(readlink "$path"))")
        elif [[ -d "$path" && ! -w "$path" ]]; then
            # A read-only destination directory is as blocking as a file in the
            # way, and catching it here is the difference between refusing and
            # half-installing.
            bad+=("$path (exists but is not writable)")
        fi
    done

    # ...and every directory that ALREADY EXISTS beneath the target, at any
    # depth. adapter_dirs() reaches one level, so a read-only leaf a level
    # deeper — a per-skill directory, or docs/graph/protocols/ — fell through to
    # ensure_dir's late check: a clean error, but only after the kernel and most
    # of the graph were already on disk. Preflight's whole promise is that a
    # refusal writes nothing, and a list-driven check cannot keep it. Walking
    # what is there can: an unwritable directory is found before the first byte
    # regardless of whether anyone remembered to list it.
    # Only EXISTING directories are walked — this is a pre-write check, so there
    # is nothing else to walk, and it costs one find over a directory the
    # installer is about to traverse anyway.
    if [[ -d "$PROJECT_DIR" ]]; then
        local existing
        # -print0 / read -d '': a path containing a NEWLINE is one path, and
        # line-wise reading split it into two. A directory literally named
        # "we\nird" was reported as two paths that do not exist — "…/we" and
        # "ird" — and the real one was never named. It refused, so it failed
        # safe; it just could not say what to fix.
        while IFS= read -r -d '' existing; do
            [[ -n "$existing" ]] || continue
            case "$existing" in *"/.git"|*"/.git/"*) continue ;; esac
            [[ -w "$existing" ]] || bad+=("$existing (exists but is not writable)")
        done < <(find "$PROJECT_DIR" -type d -not -path '*/.git/*' -print0 2>/dev/null || true)

        # ...and every existing SYMLINK-TO-A-DIRECTORY that leaves the target,
        # at any depth. The loop above is `-type d`, which does not follow
        # symlinks, so an escaping link was never visited; and the list-driven
        # check further up reaches one level and names no docs/graph/ subtree at
        # all. The result was that pointing docs/graph/protocols at a directory
        # outside the target wrote 14 protocol nodes there, REPLACED a file that
        # was already outside, left a .bak outside too, and exited 0 with no
        # warning — falsifying §5's Security NFR and AC-2 while the whole gate
        # stayed green. The same shape works for .claude/skills/<name>,
        # docs/graph/{method,agents,skills,templates} and legal/corpus.
        #
        # Walking what is there is what keeps preflight's promise; a list cannot,
        # and the control for this is that `.claude` — the one entry the list DID
        # carry — was refused correctly all along.
        local link
        while IFS= read -r -d '' link; do
            [[ -n "$link" ]] || continue
            case "$link" in *"/.git"|*"/.git/"*) continue ;; esac
            [[ -d "$link" ]] || continue          # links to files are caught above
            dest_inside_target "$link" && continue
            bad+=("$link (symlink leaving the target: $(readlink "$link"))")
        done < <(find "$PROJECT_DIR" -type l -not -path '*/.git/*' -print0 2>/dev/null || true)
    fi

    # Read-only target: a `cp` failing mid-install used to surface as a raw
    # "Permission denied" from deep inside a helper, with everything up to
    # that point already written. Checked here it is a clean die() instead.
    [[ -e "$PROJECT_DIR" && ! -w "$PROJECT_DIR" ]] && bad+=("$PROJECT_DIR (not writable)")

    [[ ${#bad[@]} -eq 0 ]] && return 0
    local msg="refusing to install — the following path(s) block a required write:"
    for path in "${bad[@]}"; do
        msg+=$'\n  '"$path"
    done
    msg+=$'\n'"Each must be either absent or an empty/writable directory. Remove or"
    msg+=$'\n'"rename the offending path(s) (or chmod the target writable) and re-run;"
    msg+=$'\n'"nothing has been written."
    die "$msg"
}
[[ ${CHECK:-0} -eq 1 ]] || preflight_state_record
[[ ${CHECK:-0} -eq 1 ]] || preflight_destinations

# report_recreated_nodes — D2 SILENT RESTORE, the announcement half. See
# place_file and place_graph_machinery for how RECREATED_NODES is filled;
# this is the one place it is read, so the tree is walked exactly once.
report_recreated_nodes() {
    [[ ${#RECREATED_NODES[@]} -eq 0 ]] && return 0
    local uniq=()
    while IFS= read -r rel; do uniq+=("$rel"); done \
        < <(printf '%s\n' "${RECREATED_NODES[@]}" | sort -u)
    log ""
    log "NOTICE — ${#uniq[@]} seed-owned graph node(s) were RE-CREATED: this plant"
    log "  already carried the seed (.cypress/seed.json predates this run) but was"
    log "  missing them. The seed owns this machinery and fast-forwards it back —"
    log "  correct behaviour — but if any of these was a DELIBERATE deletion, that"
    log "  deletion was just reverted with no other trace. Re-apply it or ratify it"
    log "  in the plant's own record; otherwise it will keep being restored."
    local n=0 total=${#uniq[@]}
    for rel in "${uniq[@]}"; do
        n=$((n + 1))
        if [[ $n -gt 10 ]]; then
            log "  ... and $((total - 10)) more"
            break
        fi
        log "  $rel"
    done
}

# --check: verify generated views are in sync, write nothing. Only the
# github-copilot views are generated (transformed) rather than symlinked,
# so they are the only ones that can drift; the others are safe by
# construction. Regenerate to a temp dir and diff. Without github-copilot in
# the run — `all` has not named it since ADR-0009, and adds it back under
# --check only when the plant records it — there is nothing to check, and a CI
# job relying on the exit 0 is told so rather than handed a silent green.
if [[ ${CHECK:-0} -eq 1 ]]; then
    if [[ " ${expanded[*]} " != *" github-copilot "* ]]; then
        log "--check: no generated views are in scope (only github-copilot generates"
        log "  views, and this run does not name it). Nothing was checked."
        exit 0
    fi
    stale=0
    for tool in "${expanded[@]}"; do
        [[ "$tool" == "github-copilot" ]] || continue
        # Inside STAGE, so the run's single trap reclaims it on every exit
        # path. A bare `mktemp -d` here leaked a full regenerated view tree
        # into /tmp whenever --check was interrupted, and a second trap would
        # only have duplicated the ownership STAGE already has.
        tmp="$(mktemp -d "$STAGE/check-XXXXXX")"; orig="$PROJECT_DIR"
        # The projections are taken FROM docs/graph/, so a regeneration that
        # starts from an empty directory regenerates from the SEED's roster
        # alone and can never match a target whose graph also carries nodes the
        # plant authored. Every such plant would read STALE for ever, with no
        # re-run able to clear it — a drift gate that is always red is a drift
        # gate nobody runs. Carry the real graph in.
        if [[ -d "$orig/docs/graph" ]]; then
            mkdir -p "$tmp/docs/graph"
            for sub_dir in agents skills; do
                [[ -d "$orig/docs/graph/$sub_dir" ]] && \
                    cp -R "$orig/docs/graph/$sub_dir" "$tmp/docs/graph/"
            done
        fi
        # Reproduce the target's multi-tool hook state. Copilot installation
        # intentionally omits .github/hooks when Claude's settings already
        # provide the same VS Code-compatible hook; an empty temp directory
        # otherwise generates hooks that can never match the real target.
        if [[ -f "$orig/.claude/settings.json" ]]; then
            mkdir -p "$tmp/.claude"
            : > "$tmp/.claude/settings.json"
        fi
        PROJECT_DIR="$tmp"; FORCE=1
        gen_rc=0
        gen_log="$(stage "check-copilot.log")"
        # In a SUBSHELL, and this is the whole of the fix. On the left of `||`,
        # bash disables errexit INSIDE the function, so a failing generator did
        # not abort it; the loop ran on to `place_generated` -> `place_file` ->
        # `die`, and `die` runs `exit`, which terminated the entire installer.
        # `|| gen_rc=$?` was therefore never reached, the branch below was
        # unreachable for every failure the generator can actually produce, and
        # both diagnostics went to $gen_log inside $STAGE, which the EXIT trap
        # then deleted. Observed at HEAD, with no seed mutation at all — a plant
        # node that is not UTF-8 is enough: `--check` exited 1 having printed
        # ZERO bytes. That is worse than the behaviour this block replaced,
        # which at least said "STALE". A subshell makes `exit` end the
        # generation instead of the run, so the status reaches the branch.
        ( install_github_copilot ) >"$gen_log" 2>&1 || gen_rc=$?
        PROJECT_DIR="$orig"
        # A generation that CRASHED used to be reported as "views are STALE":
        # the only difference a reader saw between a drift finding and a broken
        # installer was a word that named the wrong one. Say which happened,
        # and show the error rather than swallowing it.
        if [[ $gen_rc -ne 0 ]]; then
            warn "--check could not regenerate the Copilot views (exit $gen_rc):"
            sed 's/^/    /' "$gen_log" >&2
            stale=1
            rm -rf "$tmp"
            continue
        fi
        # ...and the fourth thing the regeneration does not produce is the
        # installer's OWN backups. `.bak-*` accumulates in .github/ from every
        # earlier run, so without this exclusion a target reads STALE from its
        # second install onward whatever the views actually say, and no re-run
        # clears it. `-x` matches by basename at any depth, which is the
        # intended reading of a suffix this installer is the one writing.
        if diff -rq -x '*.bak-*' "$tmp/.github" "$orig/.github" >/dev/null 2>&1 \
           && diff -q "$tmp/AGENTS.md" "$orig/AGENTS.md" >/dev/null 2>&1; then
            log "Copilot views up to date."
        else
            warn "Copilot views are STALE — re-run: install.sh github-copilot --force"
            stale=1
        fi
        rm -rf "$tmp"
    done
    exit $stale
fi

for tool in "${expanded[@]}"; do
    case "$tool" in
        claude-code)    install_claude_code ;;
        opencode)       install_opencode ;;
        codex)          install_codex ;;
        github-copilot) install_github_copilot ;;
        prime-agent)    install_prime_agent ;;
        *)              die "unknown tool: $tool" ;;
    esac
done

# D2: every adapter has now had its chance to fast-forward docs/graph/, so
# every RE-creation this run is going to produce has happened by this point.
report_recreated_nodes

# Keep the canonical tool-neutral entry discoverable from the installed
# project. This is orchestration control, not project knowledge; maintained
# project facts still live exclusively below docs/graph/.
sweep_orphaned_instruction_backups

place_file "$SEED_ROOT/INSTALL_PROMPT.md" "$PROJECT_DIR/EXPERT_SEED_INSTALL_PROMPT.md"

# The seed stamp: which seed this plant carries, written by the only step that
# knows for certain. protocols/graft.md has always described `.cypress/seed.json`
# as the provenance marker, but nothing ever wrote it — so every plant's stamp
# was whatever a graft session happened to hand-record, and the coverage audit's
# check that a plant's stamp agrees with its coverage record could never fire.
# Tracked, like the coverage record beside it; `.cypress/growth/` is the
# transient scratch and stays ignored.
# Where each adapter expects to find a SPAWNABLE agent. `docs/graph/agents/` is
# the home of every agent node; these are projections of it, and the host reads
# its roster from them, not from the graph — so an agent that exists only in
# the graph is on disk and unspawnable. This is the ONE home of that mapping:
# it is recorded into the plant's stamp below, and the growth audit reads it
# from there rather than keeping a copy that could drift.
# `{name}` is the agent file's stem; `verbatim` is false where the projection is
# transformed at install time and so cannot be compared byte-for-byte.
agent_projection_for() {
    case "$1" in
        claude-code)    printf '.claude/agents/{name}.md true' ;;
        opencode)       printf '.opencode/agents/{name}.md true' ;;
        codex)          printf '.codex/agents/{name}.md true' ;;
        prime-agent)    printf '.prime/agent/agents/{name}.md true' ;;
        github-copilot) printf '.github/agents/{name}.agent.md false' ;;
    esac
}


write_seed_stamp() {
    local stamp="$PROJECT_DIR/.cypress/seed.json" version tmp
    version="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
               "$SEED_ROOT/manifest.json" | head -1)"
    [[ -n "$version" ]] || { warn "manifest.json has no version — stamp skipped"; return; }
    ensure_dir "$PROJECT_DIR/.cypress"
    tmp="$(stage "seed.json")"
    # The stamp is the plant's record of what it CARRIES, not a log of the last
    # command typed — so a run MERGES into it and never narrows it. Installing
    # one adapter into a plant that already runs five adds that adapter; it does
    # not retract the other four, forget where the plant came from, or reset the
    # owner's corpus decisions to `undecided`. Every field below is therefore
    # "what this run states, else what the stamp already held".
    local prev prev_from prev_tools prev_corpus prev_juris
    prev="$(stamp_field "$stamp" version)"
    prev_from="$(stamp_field "$stamp" installed_from)"
    prev_tools="$(stamp_field "$stamp" tools)"
    prev_corpus="$(stamp_field "$stamp" legal_corpus)"
    prev_juris="$(stamp_field "$stamp" legal_jurisdiction)"

    # An existing stamp records where the plant came FROM; keep that as
    # `installed_from` so a graft can see the version it advanced off. A re-run
    # at the SAME version must not erase it — the plant still came from there.
    local from="$prev_from"
    [[ -n "$prev" && "$prev" != "$version" ]] && from="$prev"

    # Adapters accumulate: the union of what the plant already carried and what
    # this run installed, de-duplicated, in first-seen order.
    #
    # `${tools[@]}` is guarded on a non-empty count rather than expanded
    # directly: bash 3.2 (macOS's system bash) treats the all-elements
    # expansion of a still-empty array as an unset parameter under `set -u`
    # and dies with "tools[@]: unbound variable" on this loop's first pass —
    # fixed in bash 4.4, not present here. `${#tools[@]}` (a count, not an
    # expansion) never has this problem, which is why the guard above it
    # (`${#bad[@]}`, `${#RECREATED_NODES[@]}`) never needed one.
    local tools=() t seen
    for t in $prev_tools "${expanded[@]}"; do
        seen=0
        if [[ ${#tools[@]} -gt 0 ]]; then
            local u; for u in "${tools[@]}"; do [[ "$u" == "$t" ]] && seen=1; done
        fi
        [[ $seen -eq 0 ]] && tools+=("$t")
    done

    # The corpus and jurisdiction are the OWNER's decisions, recorded once and
    # re-stated only when the owner re-states them. A run that passes no flag
    # inherits; only `undecided` is ever overwritten by silence.
    # A stamp that exists but parses to nothing is CORRUPT, not absent. Treating
    # the two alike silently reset a plant's recorded decisions to `undecided`
    # on the next re-run — the same "record contradicts disk" failure this
    # release closed from the other direction, reached by damaging the record
    # instead of the corpus.
    # Whole-file emptiness was the only corruption this noticed. A stamp whose
    # ONE truncated field is `legal_corpus` — a crash mid-write leaving
    # `"legal_corpus": "ye` — kept version and tools intact, so the check stayed
    # silent and the decision reset to `undecided` looking exactly like a fresh
    # plant. Ask the parser instead of guessing from field emptiness.
    local stamp_ok=1
    if [[ -f "$stamp" ]]; then
        python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$stamp" \
            >/dev/null 2>&1 || stamp_ok=0
    fi
    # A warning was not enough, and the comment above claims this case is
    # closed. It is not: a single truncated field ("legal_corpus": "ye,) makes
    # the parse fail, `prev_corpus` comes back EMPTY from the sed-based reader,
    # and the line below defaults a recorded `yes` to `undecided` — verified,
    # exit 0, with 16 corpus pages still on disk and the record now contradicting
    # them. An unreadable record is not a fresh plant, and the one thing the
    # installer must never do is overwrite a decision it could not read. The
    # warning stays for the case where nothing was recorded; where a decision
    # WAS recorded and cannot be read, it refuses.
    if [[ -f "$stamp" && $stamp_ok -eq 0 ]]; then
        warn "the existing .cypress/seed.json could not be parsed."
        if grep -qE '"(legal_corpus|legal_jurisdiction|environment_class|commit_attribution)"' "$stamp" 2>/dev/null; then
            die "refusing to re-derive: .cypress/seed.json is unparseable but names owner
  decisions, and re-deriving them from this run would overwrite whatever it
  records with this run's defaults. Repair or remove the file, or re-state the
  decisions explicitly with their flags, then re-run. Nothing has been written."
        fi
        warn "  it records no owner decisions, so this run's values are being used."
    fi
    local corpus="${LEGAL_CORPUS:-${prev_corpus:-undecided}}"
    local juris="${LEGAL_JURISDICTION:-${prev_juris:-undecided}}"
    [[ -z "${LEGAL_CORPUS:-}" && -n "$prev_corpus" ]] && corpus="$prev_corpus"
    [[ -z "${LEGAL_JURISDICTION:-}" && -n "$prev_juris" ]] && juris="$prev_juris"

    # The flag domain is validated on the command line; a hand-edited stamp is
    # not, and an out-of-domain value was carried forward for ever while the
    # NEXT STEP notice below printed the hardcoded word "undecided" — the log
    # and the file disagreeing about what the record says. `agent.legal` reads
    # this field, and `yes|no|undecided` is the whole domain, so anything else
    # is repaired to `undecided` and said out loud rather than propagated.
    case "$corpus" in
        yes|no|undecided) ;;
        *) # `${corpus@Q}` would read better and is bash 4.4+; macOS ships 3.2,
           # and this file is run by the mac leg of the CI matrix. Plain quotes.
           warn "the recorded legal_corpus value '$corpus' is not yes/no/undecided;"
           warn "  resetting it to 'undecided'. Re-state the decision with"
           warn "  --legal-corpus to record it properly."
           corpus="undecided" ;;
    esac

    {
        printf '{\n'
        printf '  "seed": "cypress",\n'
        printf '  "version": "%s",\n' "$version"
        printf '  "installed_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        [[ -n "$from" ]] && printf '  "installed_from": "%s",\n' "$from"
        printf '  "tools": "%s",\n' "${tools[*]}"
        printf '  "legal_corpus": "%s",\n' "$corpus"
        printf '  "legal_jurisdiction": "%s",\n' "$juris"
        printf '  "agent_projections": [\n'
        local proj sep=""
        for t in "${tools[@]}"; do
            proj="$(agent_projection_for "$t")"
            [[ -n "$proj" ]] || continue
            printf '%s    {"tool": "%s", "path": "%s", "verbatim": %s}' \
                   "$sep" "$t" "${proj% *}" "${proj##* }"
            sep=$',\n'
        done
        printf '\n  ]\n'
        printf '}\n'
    } > "$tmp"
    # Staged, then placed atomically. A truncate-in-place write that failed
    # part way through left a stamp whose fields `stamp_field` reads back as
    # empty — indistinguishable from "never set" — so the next run would
    # silently reset the owner's corpus decisions and forget every installed
    # adapter. Rendering to scratch first makes the transition all-or-nothing.
    place_state "$tmp" "$stamp"
    log "  .cypress/seed.json     (seed stamp: cypress $version — commit it)"
}
write_seed_stamp

# The corpus decision is the owner's and it is asked BEFORE a run, not settled
# during one: an analyst with no corpus can only refuse, and a run that meets
# that refusal mid-flight either stops or invents. Say so while the installer
# still has the owner's attention.
# Gated on the RESOLVED value, not on flag silence. `-z "${LEGAL_CORPUS:-}"` is
# true on every silent re-run, so a plant that recorded `no` was told its record
# said "undecided" — the installer printing a false statement about its own
# file, which is the defect :1801 records as fixed for the out-of-domain case.
_resolved_corpus="${LEGAL_CORPUS:-}"
if [[ -z "$_resolved_corpus" && $PRIOR_INSTALL -eq 1 ]]; then
    _resolved_corpus="$(stamp_field "$PROJECT_DIR/.cypress/seed.json" legal_corpus)"
fi
if [[ -z "$_resolved_corpus" || "$_resolved_corpus" == "undecided" ]]; then
    log ""
    log "NEXT STEP — legal corpus undecided (.cypress/seed.json: \"legal_corpus\": \"undecided\")."
    if [[ "$(corpus_pages "$PROJECT_DIR/docs/graph/legal/corpus" '*.md')" -gt 0 ]]; then
        # Never claim the directory is empty while it is not. This sentence was
        # unconditional and printed over a corpus that was on disk.
        log "  docs/graph/legal/corpus/ is NOT empty — pages are there but the record"
        log "  does not say so. Decide BEFORE grow or graft — re-run with"
    else
    log "  docs/graph/legal/ holds only its scaffold, so agent.legal can do exactly"
    log "  one thing: refuse. Decide BEFORE grow or graft — re-run with"
    fi
    log "  --legal-corpus yes to place the whole corpus under legal/corpus/, or"
    log "  --legal-corpus no to record that this plant carries none."
    log "  It is placed whole or not at all. Which instruments bear on this project"
    log "  is an instruction to the analyst in docs/graph/legal/index.md, revised as"
    log "  the project evolves — never a subset of pages on disk."
fi
if [[ -z "${LEGAL_JURISDICTION:-}" ]]; then
    log ""
    log "NEXT STEP — national jurisdiction undecided (.cypress/seed.json)."
    log "  The corpus's EU and international layers are jurisdiction-neutral; its"
    log "  national layer carries: $(corpus_jurisdictions | tr '\n' ' ')."
    log "  Re-run with --legal-jurisdiction <cc>. A code the corpus does not carry"
    log "  is a recorded ingest request, not an error — another country's statute"
    log "  is retrieved by a research-scout, never assumed from a neighbour's."
fi

log "done. FILES ARE PLACED — the project is NOT grown yet."
log ""
log "Next step (the HAND OFF phase): open a NEW agent-capable chat ROOTED AT the"
log "target directory (never the seed — a first install's roster may not be"
log "registered until then, see delegation.harness-registration) and paste the"
log "one entry prompt from:"
log ""
log "    $PROJECT_DIR/EXPERT_SEED_INSTALL_PROMPT.md"
log ""
log "That prompt drives the GROW IN FULL phase: Sonnet-class scouts and"
log "Opus-class authors execute docs/graph/protocols/grow.md end to end under"
log "its completeness contract (grow.completeness-contract) — every"
log "evidence-backed node and leaf, not a skeleton. /initialize is only a"
log "coding-tool adapter to the entry fork: grow when there is source to"
    log "scout, from-scratch when the repository is empty."
