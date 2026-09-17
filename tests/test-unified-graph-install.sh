#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SELF="$ROOT/tests/test-unified-graph-install.sh"

# Per-process temp cleanup: every scenario runs in its own re-invocation of this
# script (bash "$SELF" __case case_x), so an EXIT trap here cleans that process's
# temp dirs whether the case passes or fails.
_CLEAN=()
_cleanup() { [ ${#_CLEAN[@]} -eq 0 ] || { for d in "${_CLEAN[@]}"; do rm -rf "$d"; done; }; }
trap _cleanup EXIT

# --- scenario: the machinery-only graph installs, lints, and lays down every
# required artifact; no legacy knowledge path; no tool-dir protocol copy.
case_required() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  mkdir -p "$TARGET/docs/graph"
  cp "$ROOT/tests/fixtures/target-owned-README.md" "$TARGET/docs/graph/README.md"
  "$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force >/dev/null

  grep -qx 'target-owned graph readme' "$TARGET/docs/graph/README.md"
  [[ -f "$TARGET/EXPERT_SEED_INSTALL_PROMPT.md" ]]

  required=(
    docs/graph/README.md
    docs/graph/index.md
    docs/graph/_schema.md
    docs/graph/graph-lint.py
    docs/graph/agnosticism-lint.py
    docs/graph/prose-lint.py
    docs/graph/status-register.py
    docs/graph/nodes
    docs/graph/libraries/index.md
    docs/graph/sources/index.md
    docs/graph/plans/grill.md
    docs/graph/specs/index.md
    docs/graph/decisions/README.md
    docs/graph/runbooks/verification.md
    docs/graph/product/README.md
    docs/graph/architecture/README.md
    docs/graph/api/README.md
    docs/graph/data/README.md
    docs/graph/evaluations/README.md
    docs/graph/prompts/README.md
    docs/graph/best-practices/README.md
    docs/graph/tools/index.md
    docs/graph/changelog.md
    docs/graph/protocols/grow.md
    docs/graph/protocols/recover.md
    docs/graph/skills/context-router.md
    docs/graph/agents/00-orchestrator.md
    docs/graph/method/tiers.md
    docs/graph/method/delegation.md
    docs/graph/nodes/_expertise.template.md
    docs/graph/templates/prompts/graph-session-bootstrap.md
    docs/graph/templates/spec.template.md
  )

  for path in "${required[@]}"; do
    [[ -e "$TARGET/$path" ]] || {
      printf 'missing unified graph artifact: %s\n' "$path" >&2
      exit 1
    }
  done

  for legacy in docs/libraries docs/sources docs/plans docs/specs docs/decisions docs/runbooks; do
    [[ ! -e "$TARGET/$legacy" ]] || {
      printf 'legacy knowledge path installed outside graph: %s\n' "$legacy" >&2
      exit 1
    }
  done

  grep -q 'artifacts' "$TARGET/docs/graph/_schema.md"
  grep -q 'ARTIFACTS_DIR\|HERE / "libraries"' "$TARGET/docs/graph/graph-lint.py"
  # 6.0.0: protocols are graph-only — no tool-dir copy may exist.
  [[ ! -e "$TARGET/.codex/protocols" ]]
  # The machinery-only graph (pre-growth) must lint clean out of the box.
  python3 "$TARGET/docs/graph/graph-lint.py" >/dev/null
  grep -q 'full-growth' "$ROOT/protocols/initialize.md"
  grep -q 'does not run application builds' "$ROOT/protocols/initialize.md"
  grep -q 'does not push' "$ROOT/protocols/initialize.md"
}

# --- scenario: 7.0.0 D-SCAFFOLD: a `<name>.unfilled.md` marker (left by
# graft-audit --unfilled --rename) must stop the add-if-missing pass from
# re-creating the blank leaf.
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

# --- scenario: 7.15.0 — the harness projections are projections OF THE GRAPH,
# not of the seed. A plant that authored an agent of its own had it in
# docs/graph/agents/ and in NO adapter directory, so every harness enumerated a
# roster missing it and the agent was unspawnable on all of them.
case_plant_authored() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  "$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force >/dev/null

  cat > "$TARGET/docs/graph/agents/90-plant-authored.md" <<'AGENT'
---
name: plant-authored
description: an agent this plant commissioned for itself
---
# plant-authored
AGENT
  cat > "$TARGET/docs/graph/skills/plant-authored-skill.md" <<'SKILL'
---
name: plant-authored-skill
description: a procedure this plant authored for itself
---
# plant-authored-skill
SKILL
  for tool in claude-code opencode codex prime-agent github-copilot; do
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
    .prime/agent/skills/plant-authored-skill/SKILL.md ; do
    [[ -e "$TARGET/$projected" ]] || {
      echo "plant-authored node not projected: $projected" >&2; exit 1; }
  done
  # the seed's own roster still reaches every harness
  [[ -e "$TARGET/.claude/agents/00-orchestrator.md" ]]
  [[ -e "$TARGET/.opencode/skills/context-router/SKILL.md" ]]
  echo "  plant-authored agents and skills reach every harness projection — OK"
}

# --- scenario: 7.15.0 — the seed stamp MERGES; a single-adapter re-run must not
# narrow it.
case_seed_stamp() {
  local TARGET; TARGET="$(mktemp -d)"; _CLEAN+=("$TARGET")
  for tool in claude-code opencode codex prime-agent github-copilot; do
    "$ROOT/install.sh" "$tool" --project-dir "$TARGET" --copy --force >/dev/null 2>&1
  done

  STAMP="$TARGET/.cypress/seed.json"
  grep -q '"tools": "[^"]*claude-code' "$STAMP"
  grep -q '"tools": "[^"]*codex' "$STAMP"
  "$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force \
      --legal-corpus no --legal-jurisdiction it >/dev/null 2>&1
  grep -q '"legal_corpus": "no"' "$STAMP"
  grep -q '"legal_jurisdiction": "it"' "$STAMP"
  # a later run that states NEITHER flag inherits both decisions and keeps every
  # adapter — the failure was a stamp rewritten with one adapter's facts, the
  # owner's corpus decisions reset to `undecided`, and `installed_from` dropped.
  "$ROOT/install.sh" opencode --project-dir "$TARGET" --copy --force >/dev/null 2>&1
  grep -q '"legal_corpus": "no"' "$STAMP" || {
    echo "stamp reset legal_corpus to undecided on a re-run that stated no flag" >&2; exit 1; }
  grep -q '"legal_jurisdiction": "it"' "$STAMP" || {
    echo "stamp reset legal_jurisdiction on a re-run that stated no flag" >&2; exit 1; }
  for t in claude-code opencode codex prime-agent github-copilot; do
    grep -q "\"tools\": \"[^\"]*$t" "$STAMP" || {
      echo "stamp narrowed: $t dropped by a single-adapter re-run" >&2; exit 1; }
    grep -q "\"tool\": \"$t\"" "$STAMP" || {
      echo "stamp narrowed: $t agent_projection dropped by a single-adapter re-run" >&2; exit 1; }
  done
  echo "  seed stamp merges rather than narrows on a single-adapter re-run — OK"
}

# --- scenario: 7.15.0 — a customized kernel body is fast-forwarded, but never
# silently: the backup is the recovery path for a recorded kernel deviation, so
# --force must not skip it, and the overwrite must say what was lost.
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
  if ! grep -rql 'deviation.kernel-body' "$TARGET"/*.bak-* 2>/dev/null; then
    echo "--force destroyed the only copy of the plant's kernel body" >&2; exit 1
  fi
  echo "  customized kernel body is backed up and the overwrite announced — OK"
}

# --- scenario: 7.15.0 — the projection must hold in BOTH link modes and under
# --check. The first version of this suite exercised --copy only, and shipped two
# defects in the paths it did not cover: under --symlink the graph home is a tree
# of symlinks, which `find -type f` does not match, so every adapter placed an
# EMPTY roster; and `--check` regenerated from a seed-only temp tree, so any
# plant with an agent of its own read STALE for ever.
case_symlink() {
  local SYM; SYM="$(mktemp -d)"; _CLEAN+=("$SYM")
  "$ROOT/install.sh" claude-code --project-dir "$SYM" --symlink --force >/dev/null 2>&1
  cat > "$SYM/docs/graph/agents/92-symlink-mode.md" <<'AGENT'
---
name: symlink-mode
description: a plant agent installed under the symlink link mode
---
# symlink-mode
AGENT
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

# --- scenario: --check regenerates the transformed views to compare them. It
# must compare against the SAME source the real install used — the plant's graph
# — or it reports drift that no re-run can clear. Then: only NODES may be placed
# in a roster home; notes and index pages are not roster entries.
case_check() {
  local CHK; CHK="$(mktemp -d)"; _CLEAN+=("$CHK")
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --copy --force >/dev/null 2>&1
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --check >/dev/null 2>&1 || {
    echo "--check reported STALE on a freshly installed target" >&2; exit 1; }
  cat > "$CHK/docs/graph/agents/93-plant-own.md" <<'AGENT'
---
name: plant-own
description: an agent this plant commissioned for itself
---
# plant-own
AGENT
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --copy --force >/dev/null 2>&1
  [[ -e "$CHK/.github/agents/plant-own.agent.md" ]] || {
    echo "the copilot view did not gain the plant-authored agent" >&2; exit 1; }
  "$ROOT/install.sh" github-copilot --project-dir "$CHK" --check >/dev/null 2>&1 || {
    echo "--check reports STALE for ever once the plant authors an agent" >&2; exit 1; }
  echo "  --check stays clean when the plant has agents of its own — OK"

  # A harness reads its roster by listing a directory, so only NODES may be
  # placed there: a scratch note under the home would become a spawnable agent,
  # and an index page beside the skills a loadable skill.
  mkdir -p "$CHK/docs/graph/agents/notes"
  printf 'working notes\n'  > "$CHK/docs/graph/agents/notes/todo.md"
  printf '# skills index\n' > "$CHK/docs/graph/skills/index.md"
  "$ROOT/install.sh" all --project-dir "$CHK" --copy --force >/dev/null 2>&1
  [[ -z "$(find "$CHK/.claude" "$CHK/.codex" "$CHK/.github" -name 'todo*' 2>/dev/null)" ]] || {
    echo "a note under the agent home was projected as a spawnable agent" >&2; exit 1; }
  [[ ! -e "$CHK/.claude/skills/index/SKILL.md" ]] || {
    echo "an index page beside the skills was projected as a skill" >&2; exit 1; }
  [[ ! -e "$CHK/.github/instructions/index-skill.instructions.md" ]] || {
    echo "an index page was projected as a copilot skill instruction" >&2; exit 1; }
  echo "  only nodes are projected — notes and index pages are not roster entries — OK"
}

# Re-invocation entrypoint: run ONE scenario in isolation, in its own process.
if [ "${1:-}" = "__case" ]; then
  "$2"
  exit $?
fi

# main: emit one scenario line per case and run them concurrently under the
# gate's ONE shared budget via the frozen helper.
SCN="$(mktemp)"
for c in case_required case_unfilled case_plant_authored case_seed_stamp case_kernel case_symlink case_check; do
  printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
done
rc=0
python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
rm -f "$SCN"
[ "$rc" -eq 0 ] || { echo "test-unified-graph-install: FAIL" >&2; exit "$rc"; }
printf 'unified graph install: PASS\n'
