#!/usr/bin/env bash
# Adoption contract (SPEC-0001): install.sh meeting a project that already has
# its own files, or a plant that already carries the seed. Labels: D1 preflight,
# D3/D4 `all --check` scoping, D5 recreated-nodes list, D6 preflight scope.
# Each case_* runs in its own process with its own temp target; main dispatches
# them through the gate's shared pool (tests/gate_pool.py).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$ROOT/tests/test-install-adoption.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "  $1 — OK"; }
tmpw() { W="$(mktemp -d)"; trap 'chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"' EXIT; }

assert_clean_refusal() {   # $1=label $2=target $3=blocked relpath $4=adapter $5=expect-empty
    local label="$1" tgt="$2" rel="$3" tool="$4" empty="$5" out rc
    mkdir -p "$tgt/$(dirname "$rel")"
    printf 'not a directory\n' >"$tgt/$rel"
    out="$("$ROOT/install.sh" "$tool" --project-dir "$tgt" 2>&1)" && rc=0 || rc=$?
    [[ $rc -ne 0 ]] || fail "$label: a file at '$rel' must refuse the install"
    grep -q "^ERROR:" <<<"$out" \
        || fail "$label: must fail with the tool's own ERROR, not a raw shell message. Got: $(tail -2 <<<"$out")"
    grep -qF "$rel" <<<"$out" || fail "$label: the error must name '$rel'"
    if [[ "$empty" == "empty" ]]; then
        local n; n="$(find "$tgt" -type f -not -name "$(basename "$rel")" | wc -l | tr -d ' ')"
        [[ "$n" -eq 0 ]] || fail "$label: refusal must write NOTHING, found $n file(s)"
    fi
}

case_both() {
  tmpw; T="$W/both-different"; mkdir -p "$T"
  printf '# CLAUDE.md body\nCLAUDE-SENTINEL-ONE\n' > "$T/CLAUDE.md"
  printf '# AGENTS.md body\nAGENTS-SENTINEL-TWO\n' > "$T/AGENTS.md"
  out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
      || fail "install over two differing hand-written kernels failed: $out"
  for k in CLAUDE:ONE AGENTS:TWO; do
      bak="$(ls -1dt "$T/${k%%:*}.md".bak-* 2>/dev/null | head -1)"
      [[ -n "$bak" ]] || fail "${k%%:*}.md body lost with no .bak: $out"
      grep -q "${k%%:*}-SENTINEL-${k##*:}" "$bak" || fail "${k%%:*}.md's own body is not in its backup"
      grep -qF "$bak" <<<"$out" || fail "the warning does not name the ${k%%:*}.md backup: $out"
  done
  ok "both differing pre-existing kernels recoverable from distinct, named backups"
}

# D1 PREFLIGHT_REFUSES_BEFORE_WRITING, DESTINATION_PATH_OCCUPIED (here) and
# TARGET_NOT_WRITABLE (case_block_readonly): refuse before any write.
case_block_declared() {
  tmpw
  P1="$W/block-declared"; mkdir -p "$P1"
  assert_clean_refusal "preflight/.claude" "$P1" ".claude" claude-code empty
  P2="$W/block-hooks"; mkdir -p "$P2"
  assert_clean_refusal "preflight/.github/hooks" "$P2" ".github/hooks" github-copilot empty
  ok "a file at a declared destination refuses before writing anything"
}

case_block_deep() {
  tmpw; P3="$W/block-deep"; mkdir -p "$P3"
  assert_clean_refusal "ensure_dir/skill leaf" "$P3" ".claude/skills/adopt-existing" claude-code late
  ok "a file at a depth no list enumerates still fails cleanly and names it"
}

case_block_readonly() {  # D1: a read-only target, or a read-only directory deeper than adapter_dirs() reaches
  tmpw
  for deep in . .claude/skills/library-wiki docs/graph/protocols; do
      P="$W/ro-$(basename "$deep")"; mkdir -p "$P/$deep"
      chmod 555 "$P/$deep"
      out="$("$ROOT/install.sh" claude-code --project-dir "$P" --copy --force 2>&1)" && rc=0 || rc=$?
      chmod -R u+w "$P" 2>/dev/null || true
      name="$deep"; [[ "$deep" == "." ]] && name="$P"
      [[ $rc -ne 0 ]] || fail "a read-only '$deep' must refuse the install"
      grep -qF "$name" <<<"$out" || fail "the refusal must name '$name': $out"
      n="$(find "$P" -type f | wc -l | tr -d ' ')"
      [[ "$n" -eq 0 ]] || fail "a read-only '$deep' must write NOTHING, found $n file(s)"
  done
  ok "a read-only target or directory at any depth refuses before writing anything"
}

case_unrelated_trees() {  # D6 PREFLIGHT_SCOPED_TO_WRITTEN_TREES: Docker-owned trees must not block a graft
  tmpw; P="$W/unrelated"; mkdir -p "$P"
  for d in node_modules/pkg/lib .next/server/app .vivid-data/pglite/base test-results vivid/.cypress; do
      mkdir -p "$P/$d"; printf 'x\n' >"$P/$d/keep"
  done
  ln -s "$W" "$P/node_modules/pkg/outside"          # a directory link leaving the target
  trees="node_modules .next .vivid-data test-results vivid"
  before="$(cd "$P" && find $trees | LC_ALL=C sort)"
  for d in $trees; do chmod -R a-w "$P/$d"; done
  out="$("$ROOT/install.sh" claude-code --project-dir "$P" 2>&1)" && rc=0 || rc=$?
  chmod -R u+w "$P" 2>/dev/null || true
  [[ $rc -eq 0 ]] || fail "unwritable trees the installer never writes must not refuse the install: $(tail -3 <<<"$out")"
  [[ -f "$P/.cypress/seed.json" ]] || fail "the install did not complete: no seed stamp"
  after="$(cd "$P" && find $trees | LC_ALL=C sort)"
  [[ "$before" == "$after" ]] || fail "the install touched a tree it does not own"
  ok "unwritable trees outside the written set do not block the install, and stay untouched"
}

case_adopted() {
  tmpw; MIG="$W/adopted"; mkdir -p "$MIG"
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
  "$ROOT/install.sh" opencode --project-dir "$MIG" >/dev/null 2>&1
  entry="$(grep -c '^- \[ \]' "$NOTE" | tr -d ' ')"
  [[ "$entry" -eq 1 ]] || fail "a re-install duplicated the migration entry ($entry)"
  FRESH="$W/adopted-fresh"; mkdir -p "$FRESH"
  "$ROOT/install.sh" claude-code --project-dir "$FRESH" >/dev/null 2>&1
  [[ ! -f "$FRESH/docs/graph/plans/adopted-instructions.md" ]] \
      || fail "a fresh plant must not get a migration note"
  ok "a replaced instruction file becomes recorded work for docs-librarian"
}

case_adapter_dirs() {
  tmpw
  for tool in claude-code opencode codex github-copilot prime-agent; do
      D="$W/dirs-$tool"; mkdir -p "$D"
      "$ROOT/install.sh" "$tool" --project-dir "$D" >/dev/null 2>&1 \
          || fail "adapter_dirs: baseline install of $tool failed"
      while IFS= read -r dec; do
          [[ -z "$dec" ]] && continue
          case "$dec" in docs|docs/graph|.cypress) continue ;; esac
          [[ -d "$D/$dec" ]] || fail "adapter_dirs($tool) declares '$dec', which installing $tool \
does not create, so the preflight would refuse over a path the adapter never touches"
      done < <(bash -c 'source /dev/stdin <<<"$(sed -n "/^adapter_dirs()/,/^}/p" "$0")"; adapter_dirs "$1"' \
               "$ROOT/install.sh" "$tool" 2>/dev/null)
  done
  ok "every directory adapter_dirs declares is one the adapter really creates"
}

# --check on github-copilot views: one install, copied into each sub-case.
check_broken() {
  set -e; CHK="$W/check-broken"; plant_copy "$CHK"
  python3 -c "
open('$CHK/docs/graph/agents/50-plant-expert.md','wb').write(
    '---\ndescription: caf\xe9 domain expert\ntools: [Read]\n---\nbody\n'.encode('latin-1'))"
  out="$("$ROOT/install.sh" github-copilot --check --project-dir "$CHK" 2>&1)" && rc=0 || rc=$?
  [[ $rc -ne 0 ]] || fail "--check returned 0 over a generator that cannot run"
  grep -q "could not regenerate" <<<"$out" \
      || fail "--check did not say the generation FAILED (not STALE): $out"
  grep -qi "UnicodeDecodeError" <<<"$out" \
      || fail "--check named the failure but swallowed its cause: $out"
}
check_stale() {
  set -e; CHK2="$W/check-stale"; plant_copy "$CHK2"
  printf '\n<!-- drifted -->\n' >> "$CHK2/.github/copilot-instructions.md"
  out="$("$ROOT/install.sh" github-copilot --check --project-dir "$CHK2" 2>&1)" || true
  grep -q "STALE" <<<"$out" || fail "a drifted view is no longer reported as STALE: $out"
  grep -q "could not regenerate" <<<"$out" \
      && fail "a drifted view was reported as a broken generator: $out"
  return 0
}
check_backups() {  # the installer's own backups are not drift
  set -e; B="$W/check-baks"; plant_copy "$B"
  victim="$(find "$B/.github/prompts" -name '*.prompt.md' | head -1)"
  [[ -n "$victim" ]] || fail "no generated prompt to edit"
  printf '\n<!-- edited by hand -->\n' >> "$victim"
  "$ROOT/install.sh" github-copilot --project-dir "$B" --force >/dev/null 2>&1 \
      || fail "the regenerating re-install failed"
  n="$(find "$B/.github" -name '*.bak-*' | wc -l | tr -d ' ')"
  [[ "$n" -ge 1 ]] || fail "the re-install left no backup under .github/, so this case asserts nothing"
  out="$("$ROOT/install.sh" github-copilot --check --project-dir "$B" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] || fail "--check must exit 0 over its own backups; got $rc: $out"
  grep -q "up to date" <<<"$out" || fail "--check reported drift over backups it wrote itself: $out"
}
case_check() {
  tmpw; export PLANT_CACHE="$W/cache"
  source "$ROOT/tests/helpers/plant.sh"; source "$ROOT/tests/helpers/lintcase.sh"
  plant_base github-copilot || fail "--check setup install failed"
  collect_case case_check_broken  check_broken  "--check names a broken generator and its cause"
  collect_case case_check_stale   check_stale   "--check reports a drifted view as STALE"
  collect_case case_check_backups check_backups "--check ignores the installer's own backups"
  return "$CASE_FAILED"
}

case_migration_date() {  # a re-filed orphan row carries the backup's date, not the sweep's
  tmpw; export TZ=UTC   # install.sh stamps in local time; pin it to this case's clock
  D="$W/migdate"; mkdir -p "$D"
  printf '# Our team rules\n\nAlways rebase, never merge.\n' >"$D/AGENTS.md"
  "$ROOT/install.sh" claude-code --project-dir "$D" >/dev/null 2>&1 \
      || fail "migration-date setup install failed"
  NOTE="$D/docs/graph/plans/adopted-instructions.md"
  [[ -f "$NOTE" ]] || fail "migration-date: setup produced no migration note"
  OLD="AGENTS.md.bak-20240102-030405"     # an orphaned backup: on disk, no ledger row
  printf '# Rules from a much earlier run\n' >"$D/$OLD"
  "$ROOT/install.sh" opencode --project-dir "$D" >/dev/null 2>&1 \
      || fail "migration-date: the sweeping re-install failed"
  row="$(grep -F "$OLD" "$NOTE" || true)"
  [[ -n "$row" ]] || fail "migration-date: the orphaned backup was never re-filed"
  grep -qF "on 2024-01-02" <<<"$row" \
      || fail "migration-date: the row must carry the backup's own date, not the sweep's. Got: $row"
  SWEEP_DAY="$(date +%Y-%m-%d)"
  grep -qF "$SWEEP_DAY" <<<"$row" \
      && fail "migration-date: the re-filed row was stamped with this run's date ($SWEEP_DAY). Got: $row"
  ok "a re-filed migration row carries the backup's date, not the sweep's"
}

caseCHECK_WITHOUT_COPILOT_SAYS_SO() {  # D3: silence would read as "in sync" in CI
  tmpw
  E="$W/check-no-copilot"; mkdir -p "$E"             # (1) no record at all
  out="$("$ROOT/install.sh" all --check --project-dir "$E" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] || fail "D3: all --check with no generated views in scope must exit 0; got $rc: $out"
  grep -qi 'no generated views' <<<"$out" || fail "D3: all --check did not say no generated views are in scope: $out"
  F="$W/check-codex-only"; mkdir -p "$F"             # (2) a record without github-copilot
  "$ROOT/install.sh" all codex --project-dir "$F" >/dev/null 2>&1 || fail "D3: setup install.sh all codex failed"
  grep -q 'github-copilot' "$F/.cypress/seed.json" \
      && fail "D3: setup record carries github-copilot, so this arm asserts nothing"
  out="$("$ROOT/install.sh" all --check --project-dir "$F" 2>&1)" && rc=0 || rc=$?
  [[ $rc -eq 0 ]] || fail "D3: all --check on a codex-only plant must exit 0; got $rc: $out"
  grep -qi 'no generated views' <<<"$out" \
      || fail "D3: all --check on a plant without github-copilot recorded did not say no generated views are in scope: $out"
  ok "CHECK_WITHOUT_COPILOT_SAYS_SO: all --check without github-copilot recorded says so"
}

caseALL_CHECK_INCLUDES_RECORDED_COPILOT() {  # D4: a recorded Copilot host is checked by `all --check`
  tmpw; P="$W/copilot-plant"; mkdir -p "$P"
  "$ROOT/install.sh" all github-copilot --project-dir "$P" >/dev/null 2>&1 \
      || fail "D4: setup install.sh all github-copilot failed"
  grep -q 'github-copilot' "$P/.cypress/seed.json" || fail "D4: setup record does not carry github-copilot"
  out="$("$ROOT/install.sh" all --check --project-dir "$P" 2>&1)" && rc=0 || rc=$?      # (1) in sync
  [[ $rc -eq 0 ]] || fail "D4: all --check on an in-sync Copilot plant must exit 0; got $rc: $out"
  grep -qi 'no generated views' <<<"$out" && fail "D4: the recorded Copilot views were not checked: $out"
  grep -q 'Copilot views up to date' <<<"$out" || fail "D4: in-sync views not reported as up to date: $out"
  grep -qi 'not refreshed' <<<"$out" && fail "D4: the not-refreshed warning fired for a host it checks: $out"
  victim="$(find "$P/.github/agents" -name '*.agent.md' | head -1)"                        # (2) drifted
  [[ -n "$victim" ]] || fail "D4: setup has no .github/agents view to drift"
  printf '\n<!-- drifted by hand -->\n' >> "$victim"
  own="$("$ROOT/install.sh" github-copilot --check --project-dir "$P" 2>&1)" && own_rc=0 || own_rc=$?
  [[ $own_rc -ne 0 ]] || fail "D4: setup github-copilot --check does not see the drift: $own"
  out="$("$ROOT/install.sh" all --check --project-dir "$P" 2>&1)" && rc=0 || rc=$?
  [[ $rc -ne 0 ]] || fail "D4: all --check exited 0 on a drifted Copilot plant (github-copilot --check exits $own_rc): $out"
  grep -q 'STALE' <<<"$out" || fail "D4: all --check failed on a drifted plant without naming the drift (STALE): $out"
  grep -qi 'not refreshed' <<<"$out" && fail "D4: the not-refreshed warning fired on a drifted plant it checks: $out"
  ok "ALL_CHECK_INCLUDES_RECORDED_COPILOT: all --check checks recorded Copilot views, drift exits non-zero"
}

case_stray_prompt() {  # a leftover prompt is named, never deleted by inference
  tmpw; S="$W/stray"; mkdir -p "$S/.github/prompts"
  printf -- '---\nmode: %s\n---\n\nbody\n' "'agent'" >"$S/.github/prompts/retired-command.prompt.md"
  out="$("$ROOT/install.sh" github-copilot --project-dir "$S" 2>&1)" || fail "stray-prompt install failed"
  [[ -f "$S/.github/prompts/retired-command.prompt.md" ]] \
      || fail "the installer DELETED a prompt it did not write; it may only name it"
  grep -qF "retired-command.prompt.md" <<<"$out" \
      || fail "a prompt this run did not generate must be named in the output: $out"
  live="$(basename "$(find "$S/.github/prompts" -name '*.prompt.md' -not -name 'retired-command.prompt.md' | head -1)")"
  [[ -n "$live" ]] || fail "stray-prompt: the run generated no prompts at all"
  out2="$("$ROOT/install.sh" github-copilot --project-dir "$S" 2>&1)" || fail "stray-prompt re-install failed"
  grep -E "not generated by this seed" <<<"$out2" | grep -qF "$live" \
      && fail "a prompt this run generated was reported as a leftover: $out2"
  ok "a prompt the run did not generate is named and left in place"
}

case_hook_order() {  # VS Code reads both .github/hooks and .claude/settings.json
  tmpw
  for order in "github-copilot claude-code" "claude-code github-copilot"; do
      H="$W/hookorder-$(echo "$order" | tr ' ' '-')"; mkdir -p "$H"
      for tool in $order; do
          "$ROOT/install.sh" "$tool" --project-dir "$H" >/dev/null 2>&1 || fail "hook-order setup: install $tool failed"
      done
      live=0
      for f in route-hook.py route.json status-hook.py status.json; do
          [[ -e "$H/.github/hooks/$f" ]] && live=$((live + 1))
      done
      [[ -f "$H/.claude/settings.json" ]] || fail "hook-order [$order]: .claude/settings.json is missing"
      [[ $live -eq 0 ]] || fail "hook-order [$order]: $live .github/hooks/ file(s) still wired alongside \
.claude/settings.json, so every hook fires twice"
  done
  ok "the Copilot/Claude-Code hook guard holds in both install orders"
}

case_hook_retire() {
  tmpw; HR="$W/hookorder-retire"; mkdir -p "$HR"
  "$ROOT/install.sh" github-copilot --project-dir "$HR" >/dev/null 2>&1 || fail "retire setup failed"
  printf '\n# PLANT-EDIT\n' >> "$HR/.github/hooks/route-hook.py"
  log="$("$ROOT/install.sh" claude-code --project-dir "$HR" 2>&1)" || fail "retire install failed"
  grep -q "retired .github/hooks/route-hook.py" <<<"$log" || fail "the hook retirement was not announced"
  grep -lq "PLANT-EDIT" "$HR/.github/hooks/route-hook.py".bak-* 2>/dev/null \
      || fail "a retired hook carrying a plant edit is not recoverable"
  ok "a retired Copilot hook is announced and its plant edit recoverable"
}

case_nostamp() {  # absence of the record is not absence of the plant
  tmpw; NS="$W/nostamp"; mkdir -p "$NS"
  "$ROOT/install.sh" claude-code --project-dir "$NS" >/dev/null 2>&1 || fail "no-stamp setup install failed"
  rm -f "$NS/.cypress/seed.json" "$NS/docs/graph/protocols/grill.md"
  log="$("$ROOT/install.sh" claude-code --project-dir "$NS" 2>&1)" || fail "install over a stamp-less plant failed"
  grep -qi "RE-CREATED" <<<"$log" || fail "a node was restored into a stamp-less plant with no notice"
  grep -q "no .cypress/seed.json" <<<"$log" || fail "the missing record was not announced"
  [[ -f "$NS/docs/graph/protocols/grill.md" ]] || fail "the missing node was not restored"
  ok "a plant whose .cypress/seed.json is missing is still treated as a plant"
}

case_freshquiet() {
  tmpw; FRESH="$W/freshquiet"; mkdir -p "$FRESH"
  log="$("$ROOT/install.sh" claude-code --project-dir "$FRESH" 2>&1)" || fail "fresh install failed"
  grep -qi "RE-CREATED" <<<"$log" && fail "a FIRST install announced re-created nodes: $log"
  grep -q "no .cypress/seed.json" <<<"$log" && fail "a first install warned about a missing record it was about to write"
  ok "a first install announces no re-creation and no missing record"
}

# D5 RECREATED_LIST_IS_COMPLETE: the console stops at ten paths, so the whole
# list goes to .cypress/recreated-nodes.txt under the SPEC-0001 §6 header.
d5_assert_header() {  # $1=label $2=first line of the list file; checked by prefix
  local v; v="$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$ROOT/manifest.json" | head -1)"
  [[ "$2" == "# install.sh $v "* ]] \
      || fail "$1: the first line of .cypress/recreated-nodes.txt is not the §6 header for $v: $2"
}

case_d5_recreated_list() {  # one plant, three checks, each in a subshell so one red hides no other
  tmpw; T="$W/d5-twelve"; mkdir -p "$T"
  "$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 || fail "D5: baseline install failed"
  list="$T/.cypress/recreated-nodes.txt"
  local bad=0
  (   # D5 case_d5_fresh_list: a first install lists the header alone
    [[ -f "$list" ]] || fail "D5 (fresh): a first install wrote no .cypress/recreated-nodes.txt"
    [[ "$(wc -l < "$list" | tr -d ' ')" -eq 1 ]] \
        || fail "D5 (fresh): a first install listed nodes as re-created: $(head -4 "$list" | tr '\n' ' ')"
    d5_assert_header "D5 (fresh)" "$(head -1 "$list")"
    ok "D5: a first install writes the list file with the header alone"
  ) || bad=1
  deleted=(); while IFS= read -r _l; do deleted+=("${_l#"$T"/}"); done \
      < <(ls "$T"/docs/graph/protocols/*.md | sort | head -12)
  [[ ${#deleted[@]} -eq 12 ]] || fail "D5: could not find 12 seed-owned protocol nodes to delete"
  for rel in "${deleted[@]}"; do rm -f "$T/$rel"; done
  (
    out="$("$ROOT/install.sh" claude-code --project-dir "$T" --copy 2>&1)" \
        || fail "D5: re-install after deleting twelve nodes did not exit 0: $out"
    [[ -f "$list" ]] || fail "D5: .cypress/recreated-nodes.txt is absent after a run that re-created twelve nodes"
    d5_assert_header "D5" "$(head -1 "$list")"
    got="$(tail -n +2 "$list")"
    [[ "$got" == "$(printf '%s\n' "${deleted[@]}" | sort -u)" ]] \
        || fail "D5: the list file does not hold exactly the twelve re-created paths, sorted and unique. Got: $got"
    shown=0; plain="$(sed 's/^\[seed\] //' <<<"$out")"   # strip the installer's log prefix
    for rel in "${deleted[@]}"; do grep -qxF "  $rel" <<<"$plain" && shown=$((shown + 1)); done
    [[ $shown -eq 10 ]] || fail "D5: the console notice printed $shown of the twelve paths, expected ten"
    grep -qF ".cypress/recreated-nodes.txt" <<<"$out" \
        || fail "D5: the console notice does not name .cypress/recreated-nodes.txt"
    ok "D5: twelve re-created nodes are all in the list file; the console shows ten and names the file"
  ) || bad=1
  (   # D5 case_d5_clean_rewrite: a run that re-creates nothing leaves the header alone
    "$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1 || fail "D5 (clean): the clean re-install failed"
    [[ -f "$list" ]] || fail "D5 (clean): a clean re-install removed .cypress/recreated-nodes.txt"
    [[ "$(wc -l < "$list" | tr -d ' ')" -eq 1 ]] \
        || fail "D5 (clean): a re-install that re-created nothing left more than the header: $(cat "$list")"
    d5_assert_header "D5 (clean)" "$(head -1 "$list")"
    ok "D5: a re-install that re-creates nothing rewrites the list file with the header alone"
  ) || bad=1
  return "$bad"
}

if [ "${1:-}" = "__case" ]; then "$2"; exit $?; fi

export ROOT
SCN="$(mktemp)"
for c in case_both case_block_declared case_block_deep case_block_readonly case_unrelated_trees case_adopted case_adapter_dirs case_check case_migration_date caseCHECK_WITHOUT_COPILOT_SAYS_SO caseALL_CHECK_INCLUDES_RECORDED_COPILOT case_stray_prompt case_hook_order case_hook_retire case_nostamp case_freshquiet case_d5_recreated_list; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"
[ "$rc" -eq 0 ] || { echo "install-adoption: FAIL — a scenario failed" >&2; exit "$rc"; }
echo "install-adoption: OK"
