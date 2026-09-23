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
#   D3  asserts SPEC-0001 CHECK_WITHOUT_COPILOT_SAYS_SO: `all --check` on a
#       target whose record lacks github-copilot says it checked nothing.
#   D4  asserts SPEC-0001 ALL_CHECK_INCLUDES_RECORDED_COPILOT: `all --check`
#       checks the Copilot views a plant records, and drift exits non-zero.
# Alongside those: the ADOPTION cases place_kernel and place_file already
# handle correctly (a hand-written kernel backed up, a plant-authored graph
# leaf left alone) are pinned here too, so a future change to either cannot
# regress them unnoticed.
set -euo pipefail
#
# PARALLEL: every banner section above is an independent non-pristine-target
# scenario with its OWN mktemp target. Each is a self-contained case_* function
# that builds its own temp tree and runs its ORIGINAL asserts verbatim; main
# emits one scenario line per case and dispatches them concurrently through the
# gate's ONE shared budget (tests/gate_pool.py, $GATE_JOBS / $GATE_POOL_DIR).
# ~30 serial install.sh calls were the floor here; now they run under one
# clamped pool. Every assertion is byte-for-byte what it was — the only
# structural change is a per-case `mktemp -d` (replacing the single shared
# $WORK) plus the __case re-invocation dispatch, so a red scenario still fails
# the whole gate exactly as before.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$ROOT/tests/test-install-adoption.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "$1 — OK"; }

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

case_agents() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/agents-only"; mkdir -p "$T"
  printf '# hand-written AGENTS.md\nmy own project instructions\n' > "$T/AGENTS.md"
  out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
      || fail "install over hand-written AGENTS.md failed: $out"
  bak="$(ls -1dt "$T"/AGENTS.md.bak-* 2>/dev/null | head -1)"
  [[ -n "$bak" ]] || fail "hand-written AGENTS.md was not backed up: $out"
  grep -q "my own project instructions" "$bak" \
      || fail "AGENTS.md backup does not carry the original body"
  grep -qF "$bak" <<<"$out" || fail "warning does not name the AGENTS.md backup: $out"
  ok "pre-existing AGENTS.md backed up and named"
}

case_claude() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/claude-only"; mkdir -p "$T"
  printf '# hand-written CLAUDE.md\nmy other project instructions\n' > "$T/CLAUDE.md"
  out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
      || fail "install over hand-written CLAUDE.md failed: $out"
  bak="$(ls -1dt "$T"/CLAUDE.md.bak-* 2>/dev/null | head -1)"
  [[ -n "$bak" ]] || fail "hand-written CLAUDE.md was not backed up: $out"
  grep -q "my other project instructions" "$bak" \
      || fail "CLAUDE.md backup does not carry the original body"
  grep -qF "$bak" <<<"$out" || fail "warning does not name the CLAUDE.md backup: $out"
  ok "pre-existing CLAUDE.md backed up and named"
}

case_both() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/both-different"; mkdir -p "$T"
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
}

case_index() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/index-survives"; mkdir -p "$T"
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
}

case_d1_file() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/d1-file"; mkdir -p "$T"
  touch "$T/.claude"
  rc=0
  out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" || rc=$?
  [[ $rc -ne 0 ]] || fail "D1: install over a .claude FILE did not fail: $out"
  grep -qF "$T/.claude" <<<"$out" || fail "D1: failure message does not name $T/.claude: $out"
  [[ -e "$T/CLAUDE.md" ]] && fail "D1: CLAUDE.md was written despite the preflight failure"
  [[ -e "$T/docs/graph" ]] && fail "D1: docs/graph/ was written despite the preflight failure"
  [[ -f "$T/.claude" ]] || fail "D1: the offending .claude file itself should be left alone"
  ok "D1: .claude-as-a-regular-file refuses before any write"
}

case_d1_ro() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/d1-readonly"; mkdir -p "$T"
  chmod 555 "$T"
  rc=0
  out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" || rc=$?
  chmod u+w "$T"
  [[ $rc -ne 0 ]] || fail "D1: install into a read-only target did not fail: $out"
  grep -qF "$T" <<<"$out" || fail "D1: read-only failure message does not name $T: $out"
  [[ -e "$T/CLAUDE.md" ]] && fail "D1: CLAUDE.md was written despite the read-only target"
  [[ -e "$T/docs" ]] && fail "D1: docs/ was written despite the read-only target"
  ok "D1: read-only target refuses before any write"
}

case_d2() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/d2-recreate"; mkdir -p "$T"
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

  Tfresh="$W/d2-fresh"; mkdir -p "$Tfresh"
  outfresh="$("$ROOT/install.sh" claude-code --project-dir "$Tfresh" --copy 2>&1)" \
      || fail "D2: fresh install failed"
  grep -qi "re-created" <<<"$outfresh" \
      && fail "D2: a FRESH install must not emit the re-creation notice (it would be noise): $outfresh"
  ok "D2: deleted protocol nodes are restored and named; a fresh install stays quiet"
}

case_idem() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  T="$W/idempotent"; mkdir -p "$T"
  "$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
      || fail "idempotence: first install failed"
  "$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 \
      || fail "idempotence: second install failed"
  n="$(find "$T" -name '*.bak-*' | wc -l | tr -d ' ')"
  [[ "$n" -eq 0 ]] || { find "$T" -name '*.bak-*' >&2; fail "idempotence: identical re-install produced $n backup(s)"; }
  ok "identical re-install stays backup-free"
}

case_block_declared() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # Declared area -> refused before a single byte is written.
  P1="$W/block-declared"; mkdir -p "$P1"
  assert_clean_refusal "preflight/.claude" "$P1" ".claude" claude-code empty
  P2="$W/block-hooks"; mkdir -p "$P2"
  assert_clean_refusal "preflight/.github/hooks" "$P2" ".github/hooks" github-copilot empty
  echo "  a file at a declared destination refuses before writing anything — OK"
}

case_block_deep() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # Undeclared depth -> still the tool's own error, naming the path.
  P3="$W/block-deep"; mkdir -p "$P3"
  assert_clean_refusal "ensure_dir/skill leaf" "$P3" ".claude/skills/adopt-existing" claude-code late
  echo "  a file at a depth no list enumerates still fails cleanly and names it — OK"
}

case_block_readonly() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # A read-only directory DEEPER than adapter_dirs() reaches. The list gets one
  # level; a per-skill leaf or docs/graph/protocols/ is two or three, and those
  # used to fall through to ensure_dir's late check — a clean error, but only
  # after the kernel and most of the graph were already on disk. Preflight's whole
  # promise is that a refusal writes nothing.
  for deep in .claude/skills/library-wiki docs/graph/protocols; do
      P="$W/ro-$(basename "$deep")"; mkdir -p "$P/$deep"
      chmod 555 "$P/$deep"
      out="$("$ROOT/install.sh" claude-code --project-dir "$P" --copy --force 2>&1)" && rc=0 || rc=$?
      chmod -R u+w "$P" 2>/dev/null || true
      [[ $rc -ne 0 ]] || fail "a read-only '$deep' must refuse the install"
      grep -qF "$deep" <<<"$out" || fail "the refusal must name '$deep'"
      n="$(find "$P" -type f | wc -l | tr -d ' ')"
      [[ "$n" -eq 0 ]] || fail "a read-only '$deep' must write NOTHING, found $n file(s)"
  done
  echo "  a read-only directory at any depth refuses before writing anything — OK"
}

case_adopted() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  MIG="$W/adopted"; mkdir -p "$MIG"
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
  FRESH="$W/adopted-fresh"; mkdir -p "$FRESH"
  "$ROOT/install.sh" claude-code --project-dir "$FRESH" >/dev/null 2>&1
  [[ ! -f "$FRESH/docs/graph/plans/adopted-instructions.md" ]] \
      || fail "a fresh plant must not get a migration note"
  echo "  a replaced instruction file becomes recorded work for docs-librarian — OK"
}

case_adapter_dirs() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  for tool in claude-code opencode codex github-copilot prime-agent; do
      D="$W/dirs-$tool"; mkdir -p "$D"
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
}

case_check_broken() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  CHK="$W/check-broken"; mkdir -p "$CHK"
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
}

case_check_stale() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # ...and a plant that is merely out of date is still reported as STALE, or the
  # assertion above is satisfied by a tool that calls everything a crash.
  CHK2="$W/check-stale"; mkdir -p "$CHK2"
  "$ROOT/install.sh" github-copilot --project-dir "$CHK2" >/dev/null 2>&1 \
      || fail "--check stale-case setup failed"
  printf '\n<!-- drifted -->\n' >> "$CHK2/.github/copilot-instructions.md"
  stale_out="$("$ROOT/install.sh" github-copilot --check --project-dir "$CHK2" 2>&1)" || true
  grep -q "STALE" <<<"$stale_out" \
      || fail "a drifted view is no longer reported as STALE: $stale_out"
  grep -q "could not regenerate" <<<"$stale_out" \
      && fail "a drifted view was reported as a broken generator: $stale_out"
  echo "  --check tells a broken generator from a drifted view, and shows the cause — OK"
}

case_migration_date() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # A ledger row states when the replacement HAPPENED, not when the row was
  # written. The orphan sweep re-files backups taken on runs long past, and
  # stamping those with the sweep's own date makes recoverable history
  # unrecoverable — a false claim put in front of the librarian by the same
  # mechanism the sweep's own suffix guard exists to stop, with the true value
  # sitting in the filename the guard already matched.
  D="$W/migdate"; mkdir -p "$D"
  printf '# Our team rules\n\nAlways rebase, never merge.\n' >"$D/AGENTS.md"
  "$ROOT/install.sh" claude-code --project-dir "$D" >/dev/null 2>&1 \
      || fail "migration-date setup install failed"
  NOTE="$D/docs/graph/plans/adopted-instructions.md"
  [[ -f "$NOTE" ]] || fail "migration-date: setup produced no migration note"
  # An orphaned backup from a run long past: on disk, with no ledger row.
  OLD="AGENTS.md.bak-20240102-030405"
  printf '# Rules from a much earlier run\n' >"$D/$OLD"
  "$ROOT/install.sh" opencode --project-dir "$D" >/dev/null 2>&1 \
      || fail "migration-date: the sweeping re-install failed"
  row="$(grep -F "$OLD" "$NOTE" || true)"
  [[ -n "$row" ]] || fail "migration-date: the orphaned backup was never re-filed"
  grep -qF "on 2024-01-02" <<<"$row" \
      || fail "migration-date: the row must carry the backup's own date, not the \
sweep's. Got: $row"
  TODAY="$(date -u +%Y-%m-%d)"
  grep -qF "$TODAY" <<<"$row" \
      && fail "migration-date: the re-filed row was stamped with this run's date \
($TODAY), which is the false claim. Got: $row"
  # ...and a LIVE replacement still records the day it happened, which is today.
  F="$W/migdate-live"; mkdir -p "$F"
  printf '# Our team rules\n' >"$F/AGENTS.md"
  "$ROOT/install.sh" claude-code --project-dir "$F" >/dev/null 2>&1 \
      || fail "migration-date: live-replacement install failed"
  grep -qF "on $TODAY" "$F/docs/graph/plans/adopted-instructions.md" \
      || fail "migration-date: a replacement made now must be dated now"
  echo "  a re-filed migration row carries the backup's date, not the sweep's — OK"
}

case_check_backups() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # A drift check compares what a run would generate against what is on disk,
  # so everything on disk the run does not generate has to be excluded — the
  # installer's own backups included. Without that, a target reads STALE from
  # its second install onward whatever the views say, and no re-run clears it.
  B="$W/check-baks"; mkdir -p "$B"
  "$ROOT/install.sh" github-copilot --project-dir "$B" >/dev/null 2>&1 \
      || fail "--check backup-case setup failed"
  victim="$(find "$B/.github/prompts" -name '*.prompt.md' | head -1)"
  [[ -n "$victim" ]] || fail "--check backup case: no generated prompt to edit"
  printf '\n<!-- edited by hand -->\n' >> "$victim"
  "$ROOT/install.sh" github-copilot --project-dir "$B" --force >/dev/null 2>&1 \
      || fail "--check backup case: the regenerating re-install failed"
  n="$(find "$B/.github" -name '*.bak-*' | wc -l | tr -d ' ')"
  [[ "$n" -ge 1 ]] || fail "--check backup case: the re-install left no backup \
under .github/, so this case is asserting nothing"
  out="$("$ROOT/install.sh" github-copilot --check --project-dir "$B" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] || fail "--check must exit 0 over its own backups; got $rc: $out"
  grep -q "up to date" <<<"$out" \
      || fail "--check reported drift over backups it wrote itself: $out"
  echo "  --check ignores the backups the installer itself leaves behind — OK"
}

caseCHECK_WITHOUT_COPILOT_SAYS_SO() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # D3 CHECK_WITHOUT_COPILOT_SAYS_SO (SPEC-0001, ADR-0009): `--check` verifies the
  # github-copilot generated views, and `all` no longer expands to that host. A
  # CI job running `install.sh all --check` on a target whose record does NOT
  # carry github-copilot must be told it checked nothing, not handed a silent
  # exit 0 that reads as "in sync". The Given is narrowed on purpose: a target
  # whose .cypress/seed.json records github-copilot is checked, and exit 0 is
  # not blessed there (ALL_CHECK_INCLUDES_RECORDED_COPILOT, below).
  # (1) no record at all.
  E="$W/check-no-copilot"; mkdir -p "$E"
  out="$("$ROOT/install.sh" all --check --project-dir "$E" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] \
      || fail "CHECK_WITHOUT_COPILOT_SAYS_SO: all --check must exit 0 when no generated views are in scope; got $rc: $out"
  grep -qi 'no generated views' <<<"$out" \
      || fail "CHECK_WITHOUT_COPILOT_SAYS_SO: all --check did not say that no generated views are in scope — silence is the failure: $out"
  # (2) a record that carries a frozen host, but not github-copilot.
  F="$W/check-codex-only"; mkdir -p "$F"
  "$ROOT/install.sh" all codex --project-dir "$F" >/dev/null 2>&1 \
      || fail "CHECK_WITHOUT_COPILOT_SAYS_SO: setup — install.sh all codex failed"
  grep -q 'github-copilot' "$F/.cypress/seed.json" \
      && fail "CHECK_WITHOUT_COPILOT_SAYS_SO: setup — the record carries github-copilot, so this arm asserts nothing"
  out="$("$ROOT/install.sh" all --check --project-dir "$F" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] \
      || fail "CHECK_WITHOUT_COPILOT_SAYS_SO: all --check on a plant recording codex but not github-copilot must exit 0; got $rc: $out"
  grep -qi 'no generated views' <<<"$out" \
      || fail "CHECK_WITHOUT_COPILOT_SAYS_SO: all --check on a plant without github-copilot in its record did not say that no generated views are in scope: $out"
  echo "  CHECK_WITHOUT_COPILOT_SAYS_SO: all --check without github-copilot recorded says no generated views are in scope — OK"
}

caseALL_CHECK_INCLUDES_RECORDED_COPILOT() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # D4 ALL_CHECK_INCLUDES_RECORDED_COPILOT (SPEC-0001, ADR-0009, review F1): when
  # the plant's .cypress/seed.json records github-copilot, `all --check` checks
  # its generated views. Checking is read-only, so it is not a new feature on a
  # frozen host, and a CI job that ran `all --check` before 7.27.0 keeps exiting
  # non-zero on drift. Before this contract, `all --check` exited 0 ("no
  # generated views are in scope") while `github-copilot --check` on the same
  # drifted plant exited 1: a real check hidden behind a green.
  P="$W/copilot-plant"; mkdir -p "$P"
  "$ROOT/install.sh" all github-copilot --project-dir "$P" >/dev/null 2>&1 \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: setup — install.sh all github-copilot failed"
  grep -q 'github-copilot' "$P/.cypress/seed.json" \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: setup — the record does not carry github-copilot"
  # (1) In sync: the check ran and says so, and it is not the out-of-scope notice.
  out="$("$ROOT/install.sh" all --check --project-dir "$P" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check on an in-sync Copilot-recording plant must exit 0; got $rc: $out"
  grep -qi 'no generated views' <<<"$out" \
      && fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check said no generated views are in scope on a plant that records github-copilot — the Copilot views were not checked: $out"
  grep -q 'Copilot views up to date' <<<"$out" \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check on an in-sync Copilot-recording plant did not report the views as checked and up to date: $out"
  # The host IS checked, so the "not refreshed ... Refresh them with: install.sh
  # all github-copilot" warning (which names a writing command) must not fire.
  grep -qi 'not refreshed' <<<"$out" \
      && fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check printed the not-refreshed warning for github-copilot, which it checks, and advised a writing command under --check: $out"
  # (2) Drifted: the same exit a github-copilot --check gives, and the drift named.
  victim="$(find "$P/.github/agents" -name '*.agent.md' | head -1)"
  [[ -n "$victim" ]] || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: setup — no .github/agents view to drift"
  printf '\n<!-- drifted by hand -->\n' >> "$victim"
  own="$("$ROOT/install.sh" github-copilot --check --project-dir "$P" 2>&1)" && own_rc=0 || own_rc=$?
  [[ $own_rc -ne 0 ]] \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: setup — github-copilot --check does not see the drift, so this arm asserts nothing: $own"
  out="$("$ROOT/install.sh" all --check --project-dir "$P" 2>&1)" && rc=0 || rc=$?
  [[ $rc -ne 0 ]] \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check exited 0 on a drifted Copilot-recording plant (github-copilot --check exits $own_rc): $out"
  grep -q 'STALE' <<<"$out" \
      || fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check failed on a drifted plant without naming the drift (STALE): $out"
  grep -qi 'not refreshed' <<<"$out" \
      && fail "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check printed the not-refreshed warning on a drifted plant it checks: $out"
  echo "  ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check checks the Copilot views a plant records, and drift exits non-zero — OK"
}

case_stray_prompt() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  # An installer that generates a directory owns the files it wrote and nothing
  # else. A leftover from a generator that no longer runs is not its to delete
  # — deleting by inference destroys work somebody meant to keep — but leaving
  # it unmentioned lets a stale command surface go on being offered as current.
  S="$W/stray"; mkdir -p "$S/.github/prompts"
  printf -- '---\nmode: %s\n---\n\nbody\n' "'agent'" \
      >"$S/.github/prompts/retired-command.prompt.md"
  out="$("$ROOT/install.sh" github-copilot --project-dir "$S" 2>&1)" \
      || fail "stray-prompt install failed"
  [[ -f "$S/.github/prompts/retired-command.prompt.md" ]] \
      || fail "the installer DELETED a prompt it did not write — it may only name it"
  grep -qF "retired-command.prompt.md" <<<"$out" \
      || fail "a prompt this run did not generate must be named in the output: $out"
  # ...and a prompt this run DID generate is never named as a leftover.
  live="$(basename "$(find "$S/.github/prompts" -name '*.prompt.md' \
         -not -name 'retired-command.prompt.md' | head -1)")"
  [[ -n "$live" ]] || fail "stray-prompt: the run generated no prompts at all"
  out2="$("$ROOT/install.sh" github-copilot --project-dir "$S" 2>&1)" \
      || fail "stray-prompt re-install failed"
  grep -E "not generated by this seed" <<<"$out2" | grep -qF "$live" \
      && fail "a prompt this run generated was reported as a leftover: $out2"
  echo "  a prompt the run did not generate is named and left in place — OK"
}

case_hook_order() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  for order in "github-copilot claude-code" "claude-code github-copilot"; do
      H="$W/hookorder-$(echo "$order" | tr ' ' '-')"; mkdir -p "$H"
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
}

case_hook_retire() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  HR="$W/hookorder-retire"; mkdir -p "$HR"
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
}

case_nostamp() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  NOSTAMP="$W/nostamp"; mkdir -p "$NOSTAMP"
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
}

case_freshquiet() {
  W="$(mktemp -d)"
  trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT
  FRESH="$W/freshquiet"; mkdir -p "$FRESH"
  fresh_log="$("$ROOT/install.sh" claude-code --project-dir "$FRESH" 2>&1)" \
      || fail "fresh install failed"
  grep -qi "RE-CREATED" <<<"$fresh_log" \
      && fail "a FIRST install announced re-created nodes: $fresh_log"
  grep -q "no .cypress/seed.json" <<<"$fresh_log" \
      && fail "a first install warned about a missing record it was about to write"
  echo "  a plant whose .cypress/seed.json is missing is still treated as a plant — OK"
}

# --- one-case subcommand, run by the parallel dispatcher ---------------------
if [ "${1:-}" = "__case" ]; then
  "$2"
  exit $?
fi

# --- main: dispatch every independent scenario in parallel -------------------
export ROOT
SCN="$(mktemp)"
for c in case_agents case_claude case_both case_index case_d1_file case_d1_ro case_d2 case_idem case_block_declared case_block_deep case_block_readonly case_adopted case_adapter_dirs case_check_broken case_check_stale case_migration_date case_check_backups caseCHECK_WITHOUT_COPILOT_SAYS_SO caseALL_CHECK_INCLUDES_RECORDED_COPILOT case_stray_prompt case_hook_order case_hook_retire case_nostamp case_freshquiet; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"

[ "$rc" -eq 0 ] || { echo "install-adoption: FAIL — a scenario failed" >&2; exit "$rc"; }
echo "install-adoption: OK — kernel adoption, plant-owned survival, D1 preflight, D2 announcement, idempotence, --check diagnostics, hook-order guard, stamp-less adoption"
