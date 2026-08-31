#!/usr/bin/env bash
# Full-install contract: every adapter delivers the v5 runtime machinery —
# the kernel, the runtime templates (briefs/bootstrap/handback), the recover
# protocol, spec-lint, and the tool-specific surfaces. Guards the class of
# defect where plant-facing prose references files the installer never
# placed (the pre-v5 templates/ hole).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

need() { [[ -e "$1" ]] || { echo "MISSING after $2 install: $1" >&2; exit 1; }; }

# The slash-command roster is a GENERATED projection of the protocol nodes
# that declare `command: true`. Compute the expected set straight from that
# frontmatter (the single home) so this test also pins install.sh's own awk
# parser to it — and assert every harness emits exactly that set, never the
# user-sovereign meta-loop (graft/grow/harvest) or canonize-folded toolcraft
# (the 6.1.0 Copilot-leak regression this guards).
EXPECTED_CMDS="$(grep -l '^command: true' "$ROOT"/protocols/*.md \
  | while read -r f; do b="$(basename "$f")"; echo "${b%.md}"; done | sort)"
[[ -n "$EXPECTED_CMDS" ]] || { echo "no command:true protocols found" >&2; exit 1; }

assert_cmd_roster() {  # $1=dir  $2=suffix (.md | .prompt.md)  $3=label
  local dir="$1" suffix="$2" label="$3" f base got=() s
  for f in "$dir"/*"$suffix"; do
    [[ -e "$f" ]] || continue
    base="$(basename "$f")"; got+=("${base%$suffix}")
  done
  local got_sorted; got_sorted="$(printf '%s\n' "${got[@]}" | sort)"
  [[ "$got_sorted" == "$EXPECTED_CMDS" ]] || {
    echo "$label: emitted command set != command:true roster" >&2
    diff <(printf '%s\n' "$EXPECTED_CMDS") <(printf '%s\n' "$got_sorted") >&2; exit 1; }
  for s in graft grow harvest toolcraft; do
    [[ ! -e "$dir/$s$suffix" ]] || { echo "$label: sovereign '$s' leaked as a command" >&2; exit 1; }
  done
}

"$ROOT/install.sh" claude-code --project-dir "$T" --copy --force >/dev/null
need "$T/CLAUDE.md" claude-code
need "$T/docs/graph/templates/prompts/graph-session-bootstrap.md" claude-code
need "$T/docs/graph/templates/prompts/handback-payload.md" claude-code
need "$T/docs/graph/templates/spec.template.md" claude-code
need "$T/docs/graph/protocols/recover.md" claude-code
need "$T/docs/graph/skills/context-router.md" claude-code
need "$T/docs/graph/agents/00-orchestrator.md" claude-code
need "$T/docs/graph/method/tiers.md" claude-code
need "$T/.claude/commands/recover.md" claude-code
need "$T/.claude/commands/canonize.md" claude-code
need "$T/.claude/agents/00-orchestrator.md" claude-code   # harness projection
need "$T/.claude/skills/context-router/SKILL.md" claude-code
need "$T/.claude/agent-lint.py" claude-code
need "$T/docs/graph/spec-lint.py" claude-code
need "$T/docs/graph/graph-lint.py" claude-code
need "$T/EXPERT_SEED_INSTALL_PROMPT.md" claude-code
# 6.0.0: protocols/templates/method are graph-only — no tool-dir copies.
for gone in .claude/protocols .claude/templates .claude/core; do
  [[ ! -e "$T/$gone" ]] || { echo "STALE tool-dir surface installed: $gone" >&2; exit 1; }
done
python3 "$T/.claude/agent-lint.py" --lint >/dev/null   # roster valid in-plant
# The golden routing corpus has one home (agents/_routes.golden.tsv); the
# installed copy is a projection of it. Asserted here because this is the only
# gate where a projection actually exists — tests/test_agent_lint.py used to
# keep a third copy for this purpose and it had silently drifted.
cmp -s "$ROOT/agents/_routes.golden.tsv" "$T/.claude/agents/_routes.golden.tsv" \
  || { echo "golden routing corpus drifted between seed home and install projection" >&2; exit 1; }
python3 "$T/docs/graph/graph-lint.py" >/dev/null       # machinery graph lints clean
assert_cmd_roster "$T/.claude/commands" .md "claude-code commands"

"$ROOT/install.sh" opencode --project-dir "$T" --copy --force >/dev/null
need "$T/AGENTS.md" opencode
need "$T/.opencode/agents/00-orchestrator.md" opencode
need "$T/.opencode/commands/recover.md" opencode
[[ ! -e "$T/.opencode/protocols" ]] || { echo "STALE .opencode/protocols" >&2; exit 1; }
[[ ! -e "$T/.opencode/templates" ]] || { echo "STALE .opencode/templates" >&2; exit 1; }
# The seed ships exactly one opencode config (opencode.json). The .jsonc twin
# it used to also install is gone; pin that it stays gone, because two configs
# in a project root have unspecified precedence.
[[ ! -e "$T/opencode.jsonc" ]] || { echo "two opencode configs installed — precedence is unspecified" >&2; exit 1; }
python3 - "$T/opencode.json" <<'EOF'
import json, sys
cfg = json.load(open(sys.argv[1]))
# opencode auto-loads AGENTS.md; declaring it would load the kernel twice.
assert "AGENTS.md" not in cfg.get("instructions", []), \
    f"opencode double-load regressed: {cfg.get('instructions')}"
# The live schema sets additionalProperties:false — the directory keys the seed
# used to ship made the whole config invalid.
assert cfg["$schema"] == "https://opencode.ai/config.json", f"stale $schema: {cfg['$schema']}"
for dead in ("agents", "commands"):
    assert dead not in cfg, f"{dead!r} is not an opencode config key"
assert cfg.get("skills", {}).keys() <= {"paths", "urls"}, f"bad skills shape: {cfg.get('skills')}"
# The seed's deepest legal chain is depth 3; opencode defaults to 1.
assert cfg["subagent_depth"] == 3, f"delegation depth capped: {cfg.get('subagent_depth')}"
EOF
assert_cmd_roster "$T/.opencode/commands" .md "opencode commands"

"$ROOT/install.sh" codex --project-dir "$T" --copy --force >/dev/null
need "$T/.codex/agents/00-orchestrator.md" codex
need "$T/docs/graph/templates/prompts/handback-payload.md" codex
[[ ! -e "$T/.codex/protocols" ]] || { echo "STALE .codex/protocols" >&2; exit 1; }
grep -q "context-router" "$T/.codex/codex-config-snippet.toml"
grep -q "validate-knowledge" "$T/.codex/codex-config-snippet.toml"

"$ROOT/install.sh" github-copilot --project-dir "$T" --copy --force >/dev/null
need "$T/.github/copilot-instructions.md" github-copilot
need "$T/docs/graph/templates/prompts/graph-session-bootstrap.md" github-copilot
need "$T/.github/prompts/recover.prompt.md" github-copilot
[[ ! -e "$T/.github/templates" ]] || { echo "STALE .github/templates" >&2; exit 1; }
assert_cmd_roster "$T/.github/prompts" .prompt.md "github-copilot prompts"

"$ROOT/install.sh" prime-agent --project-dir "$T" --copy --force >/dev/null
need "$T/AGENTS.md" prime-agent
need "$T/.prime/agent/agents/00-orchestrator.md" prime-agent
need "$T/.prime/agent/agents/_routes.golden.tsv" prime-agent
need "$T/.prime/agent/skills/context-router/SKILL.md" prime-agent
need "$T/.prime/agent/prompts/recover.md" prime-agent
need "$T/.prime/agent/extensions/route-extension.ts" prime-agent
need "$T/.prime/agent/settings.json" prime-agent
need "$T/.prime/agent/APPEND_SYSTEM.md" prime-agent
# Prime Agent has no static roster/protocol/template tool-dirs — graph-only.
[[ ! -e "$T/.prime/agent/protocols" ]]  || { echo "STALE .prime/agent/protocols"  >&2; exit 1; }
[[ ! -e "$T/.prime/agent/templates" ]]  || { echo "STALE .prime/agent/templates"  >&2; exit 1; }
# PARITY GATE: the SAME agent-lint.py claude-code runs, pointed at the installed
# brief-source roster (--dir bypasses the .claude/agents assumption). This is
# what makes prime-agent a first-class citizen and not a doc-only integration.
python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint --dir "$T/.prime/agent/agents" >/dev/null
python3 "$ROOT/integrations/claude-code/agent-lint.py" --eval --dir "$T/.prime/agent/agents" >/dev/null
# The golden routing corpus projection must be byte-identical to its one home.
cmp -s "$ROOT/agents/_routes.golden.tsv" "$T/.prime/agent/agents/_routes.golden.tsv" \
  || { echo "golden routing corpus drifted: prime-agent projection" >&2; exit 1; }
# settings.json is valid JSON and uses BARE relative resource paths (a
# ".prime/agent/..." prefix would double-nest against the .prime/agent baseDir).
python3 - "$T/.prime/agent/settings.json" <<'EOF'
import json, sys
cfg = json.load(open(sys.argv[1]))
for key in ("extensions", "skills", "prompts"):
    for entry in cfg.get(key, []):
        assert not entry.startswith(".prime/"), \
            f"{key} entry {entry!r} is prefixed; resource paths resolve against .prime/agent/ — use a bare name"
# Recursion depth is a global/session/env dial on Prime Agent, never committed here.
assert "rlmMaxDepth" not in cfg, "rlmMaxDepth in project settings is silently ignored — do not ship it"
EOF
assert_cmd_roster "$T/.prime/agent/prompts" .md "prime-agent prompts"

# --- Interchangeable Claude Code + Prime Agent in ONE plant --------------
# The two first-class harnesses must coexist in a single plant off a shared,
# non-drifting kernel. Install both into a FRESH dir and assert one kernel file
# is the source of truth (the other a symlink to it), both harness trees exist,
# and the knowledge graph is shared. Both install orders must converge.
for order in "claude-code prime-agent" "prime-agent claude-code"; do
  D="$(mktemp -d)"
  "$ROOT/install.sh" $order --project-dir "$D" --copy --force >/dev/null
  need "$D/CLAUDE.md" "coexist($order)"
  need "$D/AGENTS.md" "coexist($order)"
  diff -q "$D/CLAUDE.md" "$D/AGENTS.md" >/dev/null \
    || { echo "coexist($order): CLAUDE.md and AGENTS.md differ — kernel would drift" >&2; exit 1; }
  links=0; [[ -L "$D/CLAUDE.md" ]] && links=$((links+1)); [[ -L "$D/AGENTS.md" ]] && links=$((links+1))
  [[ "$links" -eq 1 ]] \
    || { echo "coexist($order): expected exactly one of CLAUDE.md/AGENTS.md to be a symlink (single source of truth), got $links" >&2; exit 1; }
  # The symlink is PROJECT-LOCAL (points at its sibling basename), not into the seed.
  for k in CLAUDE.md AGENTS.md; do
    if [[ -L "$D/$k" ]]; then
      tgt="$(readlink "$D/$k")"
      [[ "$tgt" == "CLAUDE.md" || "$tgt" == "AGENTS.md" ]] \
        || { echo "coexist($order): $k symlink target '$tgt' is not the project-local sibling" >&2; exit 1; }
    fi
  done
  need "$D/.claude/agents/00-orchestrator.md" "coexist($order)"
  need "$D/.prime/agent/agents/00-orchestrator.md" "coexist($order)"
  need "$D/.claude/route-hook.py" "coexist($order)"
  need "$D/.prime/agent/extensions/route-extension.ts" "coexist($order)"
  need "$D/docs/graph/index.md" "coexist($order)"
  rm -rf "$D"
done

printf 'full five-tool install contract + CC/PA coexistence: PASS\n'
