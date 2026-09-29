#!/usr/bin/env bash
# Unified graph install: every knowledge artifact lands under one docs/graph/
# root, and the harness projections are projections of the plant's graph.
# Each case_* runs in its own process (bash "$SELF" __case case_x) under the
# gate's shared pool; the EXIT trap cleans that process's temp dirs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$ROOT/tests/test-unified-graph-install.sh"
# Every host the installer can place, frozen ones included (ADR-0009); `all`
# names only the maintained hosts. Unquoted at each call: it word-splits.
EVERY_HOST="claude-code opencode codex github-copilot prime-agent"

_CLEAN=()
_cleanup() { [ ${#_CLEAN[@]} -eq 0 ] || rm -rf "${_CLEAN[@]}"; }
trap _cleanup EXIT

# The machinery-only graph lays down every required artifact, keeps a
# target-owned README, and lints clean out of the box.
case_required() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  mkdir -p "$TARGET/docs/graph"
  cp "$ROOT/tests/fixtures/target-owned-README.md" "$TARGET/docs/graph/README.md"
  "$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force >/dev/null

  grep -qx 'target-owned graph readme' "$TARGET/docs/graph/README.md"
  [[ -f "$TARGET/EXPERT_SEED_INSTALL_PROMPT.md" ]]
  local g=docs/graph path
  for path in $g/README.md $g/index.md $g/_schema.md $g/graph-lint.py \
      $g/agnosticism-lint.py $g/prose-lint.py $g/status-register.py $g/nodes \
      $g/libraries/index.md $g/sources/index.md $g/plans/grill.md $g/specs/index.md \
      $g/decisions/README.md $g/runbooks/verification.md $g/product/README.md \
      $g/architecture/README.md $g/api/README.md $g/data/README.md \
      $g/evaluations/README.md $g/prompts/README.md $g/best-practices/README.md \
      $g/tools/index.md $g/changelog.md $g/protocols/grow.md $g/protocols/recover.md \
      $g/skills/context-router.md $g/agents/00-orchestrator.md $g/method/tiers.md \
      $g/method/delegation.md $g/nodes/_expertise.template.md \
      $g/templates/prompts/graph-session-bootstrap.md $g/templates/spec.template.md; do
    [[ -e "$TARGET/$path" ]] || { echo "missing unified graph artifact: $path" >&2; exit 1; }
  done
  [[ ! -e "$TARGET/.codex/protocols" ]]   # protocols are graph-only, no tool-dir copy
  python3 "$TARGET/docs/graph/graph-lint.py" >/dev/null
}

# A `<name>.unfilled.md` marker stops the add-if-missing pass re-creating the blank leaf.
case_unfilled() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  "$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force >/dev/null
  mv "$TARGET/docs/graph/runbooks/rollback.md" "$TARGET/docs/graph/runbooks/rollback.unfilled.md"
  "$ROOT/install.sh" claude-code --project-dir "$TARGET" --copy --force >/dev/null
  if [[ -e "$TARGET/docs/graph/runbooks/rollback.md" ]]; then
    echo "install re-created runbooks/rollback.md despite the .unfilled.md marker" >&2; exit 1
  fi
  echo "  .unfilled.md marker suppresses scaffold re-creation — OK"
}

# A plant-authored agent or skill reaches every harness, or it is unspawnable.
case_plant_authored() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  "$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force >/dev/null
  printf -- '---\nname: plant-authored\ndescription: an agent this plant commissioned for itself\n---\n# plant-authored\n' \
    > "$TARGET/docs/graph/agents/90-plant-authored.md"
  printf -- '---\nname: plant-authored-skill\ndescription: a procedure this plant authored for itself\n---\n# plant-authored-skill\n' \
    > "$TARGET/docs/graph/skills/plant-authored-skill.md"
  for tool in $EVERY_HOST; do
    "$ROOT/install.sh" "$tool" --project-dir "$TARGET" --copy --force >/dev/null 2>&1
  done
  for projected in \
    .claude/agents/90-plant-authored.md \
    .opencode/agents/90-plant-authored.md \
    .codex/agents/90-plant-authored.md \
    .prime/agent/agents/90-plant-authored.md \
    .github/agents/plant-authored.agent.md \
    .claude/skills/plant-authored-skill/SKILL.md \
    .opencode/skills/plant-authored-skill/SKILL.md \
    .codex/skills/plant-authored-skill/SKILL.md \
    .prime/agent/skills/plant-authored-skill/SKILL.md \
    .claude/agents/00-orchestrator.md \
    .opencode/skills/context-router/SKILL.md ; do
    [[ -e "$TARGET/$projected" ]] || { echo "node not projected: $projected" >&2; exit 1; }
  done
  echo "  plant-authored agents and skills reach every harness projection — OK"
}

# A customized kernel body is fast-forwarded, never silently.
case_kernel() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  "$ROOT/install.sh" claude-code --project-dir "$TARGET" --copy --force >/dev/null
  KERNEL="$TARGET/AGENTS.md"
  [[ -L "$KERNEL" ]] && KERNEL="$TARGET/CLAUDE.md"
  printf '\n<!-- deviation.kernel-body: a line this plant decided to keep -->\n' >> "$KERNEL"
  KOUT="$("$ROOT/install.sh" claude-code --project-dir "$TARGET" --copy --force 2>&1)"
  grep -q 'OVERWRITTEN' <<<"$KOUT" || {
    echo "kernel fast-forward discarded a customized body without announcing it" >&2; exit 1; }
  grep -q 'deviation' <<<"$KOUT" || {
    echo "kernel overwrite notice does not name the deviation it discarded" >&2; exit 1; }
  echo "  customized kernel overwrite announced with its deviation — OK"
}

# Under --symlink the graph home is a tree of symlinks; the roster must still project.
case_symlink() {
  local SYM; SYM="$(mktemp -d)"; _CLEAN+=("$SYM")
  "$ROOT/install.sh" claude-code --project-dir "$SYM" --symlink --force >/dev/null 2>&1
  printf -- '---\nname: symlink-mode\ndescription: a plant agent installed under the symlink link mode\n---\n# symlink-mode\n' \
    > "$SYM/docs/graph/agents/92-symlink-mode.md"
  "$ROOT/install.sh" claude-code --project-dir "$SYM" --symlink --force >/dev/null 2>&1
  sym_agents=$(ls "$SYM/.claude/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
  [[ "$sym_agents" -gt 1 ]] || {
    echo "--symlink projected $sym_agents agent file(s) — an empty roster" >&2; exit 1; }
  [[ -e "$SYM/.claude/agents/92-symlink-mode.md" ]] || {
    echo "--symlink did not project the plant-authored agent" >&2; exit 1; }
  [[ -e "$SYM/.claude/skills/context-router/SKILL.md" ]] || {
    echo "--symlink did not project skills" >&2; exit 1; }
  echo "  --symlink projects the roster, plant-authored nodes included — OK"
}

# --check regenerates from the plant's graph, not the seed's; and only nodes
# are placed in a roster home (a note or index page is not a roster entry).
case_check() {
  local CHK; CHK="$(mktemp -d)"; _CLEAN+=("$CHK")
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --copy --force >/dev/null 2>&1
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --check >/dev/null 2>&1 || {
    echo "--check reported STALE on a freshly installed target" >&2; exit 1; }
  printf -- '---\nname: plant-own\ndescription: an agent this plant commissioned for itself\n---\n# plant-own\n' \
    > "$CHK/docs/graph/agents/93-plant-own.md"
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --copy --force >/dev/null 2>&1
  [[ -e "$CHK/.github/agents/plant-own.agent.md" ]] || {
    echo "the copilot view did not gain the plant-authored agent" >&2; exit 1; }
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --check >/dev/null 2>&1 || {
    echo "--check reports STALE for ever once the plant authors an agent" >&2; exit 1; }
  echo "  --check stays clean when the plant has agents of its own — OK"

  mkdir -p "$CHK/docs/graph/agents/notes"
  printf 'working notes\n'  > "$CHK/docs/graph/agents/notes/todo.md"
  printf '# skills index\n' > "$CHK/docs/graph/skills/index.md"
  "$ROOT/install.sh" $EVERY_HOST --project-dir "$CHK" --copy --force >/dev/null 2>&1
  [[ -z "$(find "$CHK/.claude" "$CHK/.codex" "$CHK/.github" -name 'todo*' 2>/dev/null)" ]] || {
    echo "a note under the agent home was projected as a spawnable agent" >&2; exit 1; }
  [[ ! -e "$CHK/.claude/skills/index/SKILL.md" ]] || {
    echo "an index page beside the skills was projected as a skill" >&2; exit 1; }
  [[ ! -e "$CHK/.github/instructions/index-skill.instructions.md" ]] || {
    echo "an index page was projected as a copilot skill instruction" >&2; exit 1; }
  echo "  only nodes are projected — notes and index pages are not roster entries — OK"
}

if [ "${1:-}" = "__case" ]; then "$2"; exit $?; fi

SCN="$(mktemp)"
for c in case_required case_unfilled case_plant_authored case_kernel case_symlink case_check; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"
[ "$rc" -eq 0 ] || { echo "test-unified-graph-install: FAIL" >&2; exit "$rc"; }
printf 'unified graph install: PASS\n'
