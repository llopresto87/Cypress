#!/usr/bin/env bash
# Full-install contract: every adapter delivers the v5 runtime machinery —
# the kernel, the runtime templates (briefs/bootstrap/handback), the recover
# protocol, spec-lint, and the tool-specific surfaces. Guards the class of
# defect where plant-facing prose references files the installer never
# placed (the pre-v5 templates/ hole).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Every host the installer can place, named explicitly (ADR-0009). A call that
# exists to cover the complete destination set, or that asserts a frozen host's
# files, installs these five by name so the frozen adapters stay under
# regression; `all` names only the maintained hosts. Unquoted at each call on
# purpose: it word-splits into five positional tool arguments.
EVERY_HOST="claude-code opencode codex github-copilot prime-agent"

need() { [[ -e "$1" ]] || { echo "MISSING after $2 install: $1" >&2; exit 1; }; }

# The slash-command roster is a GENERATED projection of the protocol nodes
# that declare `command: true`. Compute the expected set straight from that
# frontmatter (the single home) so this test also pins install.sh's own awk
# parser to it — and assert every harness emits exactly that set, never the
# user-sovereign meta-loop (graft/grow/harvest)
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
  # `toolcraft` was in this list until 7.16.0, when it stopped being a
  # protocol; asserting the absence of a file that cannot exist proves
  # nothing, so it is gone rather than left as a vacuous pass.
  for s in graft grow harvest; do
    [[ ! -e "$dir/$s$suffix" ]] || { echo "$label: sovereign '$s' leaked as a command" >&2; exit 1; }
  done
}

# Is $2 a faithful projection of the roster home $1? SPEC-0001 §6's predicate,
# and it is a function rather than an inline `cmp` so it can be pointed at a
# directory — a check nobody can aim at a known-bad tree is a check nobody can
# tell from a check that compares one file. Three conditions, all required:
# the set of non-underscore `*.md` filenames equal in BOTH directions, the
# golden corpus present in both, and every filename they share byte-identical.
#
# Both directions is the load-bearing half. A one-way rule — every seed file
# present and identical in the host — accepts a host that has ADDED an agent,
# which is the live shape of every grown plant and exactly the case that took
# the nested gate down. Silent, because `cmp`ing `_routes.golden.tsv` alone
# never opened the agent files that corpus is a projection of.
projection_parity() {
  local home="$1" proj="$2" f
  local -a shared=()
  for f in _routes.golden.tsv; do
    [[ -f "$home/$f" && -f "$proj/$f" ]] || { echo "projection_parity: $f missing from $home or $proj" >&2; return 1; }
    shared+=("$f")
  done
  local home_set proj_set
  # `|| true`: an empty directory makes both `ls` and `grep` exit non-zero, and
  # an absent projection is a verdict this function owes, not an abort.
  home_set="$(cd "$home" && ls -1 *.md 2>/dev/null | grep -v '^_' | LC_ALL=C sort || true)"
  proj_set="$(cd "$proj" && ls -1 *.md 2>/dev/null | grep -v '^_' | LC_ALL=C sort || true)"
  if [[ "$home_set" != "$proj_set" ]]; then
    echo "projection_parity: agent set differs between $home and $proj" >&2
    diff <(printf '%s\n' "$home_set") <(printf '%s\n' "$proj_set") >&2 || true
    return 1
  fi
  [[ -n "$home_set" ]] || { echo "projection_parity: neither $home nor $proj holds an agent file — the comparison would be vacuous" >&2; return 1; }
  while IFS= read -r f; do shared+=("$f"); done <<< "$home_set"
  for f in "${shared[@]}"; do
    cmp -s "$home/$f" "$proj/$f" || { echo "projection_parity: $f differs between $home and $proj" >&2; return 1; }
  done
  return 0
}

# E2 LEGACY_INSTALL_PRINTS_DEPRECATED: $1 is a captured stderr, $2 the frozen tool.
# Exactly one DEPRECATED line, and that line names both the tool and ADR-0009.
assert_one_deprecated_line() {
  local err="$1" tool="$2" n line
  n="$(grep -c 'DEPRECATED' "$err" || true)"
  [[ "$n" -eq 1 ]] || { echo "LEGACY_INSTALL_PRINTS_DEPRECATED: install.sh $tool printed $n DEPRECATED line(s) on stderr, expected exactly 1:" >&2; cat "$err" >&2; exit 1; }
  line="$(grep 'DEPRECATED' "$err")"
  grep -qF -- "$tool" <<<"$line" \
    || { echo "LEGACY_INSTALL_PRINTS_DEPRECATED: the DEPRECATED line does not name $tool: $line" >&2; exit 1; }
  grep -qi 'adr-0009' <<<"$line" \
    || { echo "LEGACY_INSTALL_PRINTS_DEPRECATED: the DEPRECATED line does not name ADR-0009: $line" >&2; exit 1; }
}

# --- independent scenarios, each self-contained in its own temp target ----
# Every case below sets up its OWN mktemp target and runs its OWN asserts,
# verbatim from the original serial script. main() emits one scenario line
# per case and runs them concurrently under the gate's ONE shared budget via
# tests/gate_pool.py (a red scenario still fails the whole suite).

case_claude_code() {
  local T; T="$(mktemp -d)"
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
need "$T/docs/graph/grill-lint.py" claude-code
need "$T/docs/graph/graph-lint.py" claude-code
need "$T/docs/graph/agnosticism-lint.py" claude-code
need "$T/docs/graph/prose-lint.py" claude-code
need "$T/docs/graph/status-register.py" claude-code
need "$T/.claude/status-hook.py" claude-code
need "$T/.claude/bound-hook.py" claude-code
# 7.0.0: a plant's edited .claude/settings.json is BACKED UP on re-install, never
# silently overwritten — a graft must not destroy local hook config.
python3 - "$T/.claude/settings.json" <<'PY2'
import json,sys; p=sys.argv[1]; c=json.load(open(p)); c["_plant_local_marker"]="keep-me"; json.dump(c,open(p,"w"),indent=2)
PY2
"$ROOT/install.sh" claude-code --project-dir "$T" --copy >/dev/null 2>&1
ls "$T/.claude/"settings.json.bak-* >/dev/null 2>&1 \
  || { echo "re-install overwrote an edited .claude/settings.json without a backup" >&2; exit 1; }
grep -q keep-me "$T/.claude/"settings.json.bak-* \
  || { echo "settings.json backup does not carry the plant's edit" >&2; exit 1; }
# --force must still back up what it replaces. The graft protocol's Phase 7
# safety net IS the installer's backup ("rely on it and confirm the backups
# exist"), and the customization audit reads those backups: a --force install
# that destroys instead of backing up leaves a graft with nothing to audit and
# no way back. --force skips the prompt, never the backup.
python3 - "$T/.claude/settings.json" <<'PY2'
import json,sys; p=sys.argv[1]; c=json.load(open(p)); c["_forced_marker"]="keep-me-too"; json.dump(c,open(p,"w"),indent=2)
PY2
rm -f "$T/.claude/"settings.json.bak-*
"$ROOT/install.sh" claude-code --project-dir "$T" --copy --force >/dev/null 2>&1
ls "$T/.claude/"settings.json.bak-* >/dev/null 2>&1 \
  || { echo "--force install destroyed an edited settings.json with no backup" >&2; exit 1; }
grep -q keep-me-too "$T/.claude/"settings.json.bak-* \
  || { echo "--force backup does not carry the plant's edit" >&2; exit 1; }
echo "  --force backs up what it replaces (the graft's safety net) — OK"

# the status register is DELIVERED and its hook is REGISTERED: a plant surfaces
# its lifecycle debt at session start without any seed checkout or brief line.
python3 "$T/docs/graph/status-register.py" --root "$T/docs/graph" --summary >/dev/null \
  || { echo "installed status-register.py does not run in the plant" >&2; exit 1; }
grep -q '"SessionStart"' "$T/.claude/settings.json" \
  || { echo ".claude/settings.json does not register the SessionStart status hook" >&2; exit 1; }
# the agnosticism floor is DELIVERED, not merely present in the seed: a plant
# must be able to run it on its own harvest candidates without a seed checkout.
python3 "$T/docs/graph/agnosticism-lint.py" --root "$T/docs/graph/protocols" >/dev/null \
  || { echo "installed agnosticism-lint.py does not run in the plant" >&2; exit 1; }
# the prose floor is DELIVERED too: a plant runs it on its own deliverables.
python3 "$T/docs/graph/prose-lint.py" --file "$T/docs/graph/skills/humanizer.md" >/dev/null 2>&1; prc=$?
[ "$prc" -ne 2 ] || { echo "installed prose-lint.py does not run in the plant" >&2; exit 1; }
need "$T/EXPERT_SEED_INSTALL_PROMPT.md" claude-code
# 6.0.0: protocols/templates/method are graph-only — no tool-dir copies.
for gone in .claude/protocols .claude/templates .claude/core; do
  [[ ! -e "$T/$gone" ]] || { echo "STALE tool-dir surface installed: $gone" >&2; exit 1; }
done
python3 "$T/.claude/agent-lint.py" --lint >/dev/null   # roster valid in-plant
# The roster has one home (agents/); the installed .claude/agents/ is a
# projection of it. Asserted here because this is the only gate where a
# projection actually exists — tests/test_agent_lint.py used to keep a third
# copy for this purpose and it had silently drifted, and once the seed suite's
# roster is scoped to the seed (SPEC-0001 ROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED)
# its copy of this claim can no longer reach a projection at all. This is the
# claim's LAST live home, so it is decided by SPEC-0001 §6's projection
# predicate — set equality in BOTH directions plus byte identity — and not by
# comparing one file. `cmp`ing `_routes.golden.tsv` alone never opened the
# twenty agent .md files it is a projection of.
projection_parity "$ROOT/agents" "$T/.claude/agents" \
  || { echo "the install projection is not a faithful projection of the seed roster" >&2; exit 1; }
python3 "$T/docs/graph/graph-lint.py" >/dev/null       # machinery graph lints clean
assert_cmd_roster "$T/.claude/commands" .md "claude-code commands"
  rm -rf "$T"
}

case_plant_facts_flags() {
# 7.2.1: the plant facts are an explicit owner choice at install time. With the
# four flags the router's plant: block is filled; without them the placeholders
# stay and the installer names the missing facts as a NEXT STEP.
P="$(mktemp -d)"
"$ROOT/install.sh" claude-code --project-dir "$P" --copy --force \
  --environment-class staging --commit-attribution none \
  --deliverable-language en --comment-language en >/dev/null
grep -q '^  environment_class: staging$' "$P/docs/graph/index.md" || { echo "plant facts: environment_class not written" >&2; exit 1; }
grep -q '^  commit_attribution: none$' "$P/docs/graph/index.md" || { echo "plant facts: commit_attribution not written" >&2; exit 1; }
grep -q '^  comment_language: en$' "$P/docs/graph/index.md" || { echo "plant facts: comment_language not written" >&2; exit 1; }
"$ROOT/install.sh" claude-code --project-dir "$P" --copy --force --environment-class production >/dev/null 2>&1 && { echo "plant facts: invalid environment_class accepted" >&2; exit 1; }
grep -q '^  environment_class: staging$' "$P/docs/graph/index.md" || { echo "plant facts: a filled value was overwritten" >&2; exit 1; }
Q="$(mktemp -d)"
OUT="$("$ROOT/install.sh" claude-code --project-dir "$Q" --copy --force 2>&1)"
grep -q 'environment_class: <' "$Q/docs/graph/index.md" || { echo "plant facts: placeholder should remain without flags" >&2; exit 1; }
grep -q 'plant facts' <<<"$OUT" || { echo "plant facts: installer must name the missing facts" >&2; exit 1; }
rm -rf "$P" "$Q"
echo "  plant facts: filled by flags, validated, never overwritten, named when missing — OK"
}

case_opencode() {
  local T; T="$(mktemp -d)"
  local ERR; ERR="$(mktemp)"
"$ROOT/install.sh" opencode --project-dir "$T" --copy --force >/dev/null 2>"$ERR"
# LEGACY_INSTALL_PRINTS_DEPRECATED (negative arm): a maintained host is not
# deprecated, so its install carries no notice (ADR-0009).
if grep -q 'DEPRECATED' "$ERR"; then
  echo "LEGACY_INSTALL_PRINTS_DEPRECATED: install.sh opencode printed a DEPRECATED notice; opencode is a supported host:" >&2
  cat "$ERR" >&2; exit 1
fi
rm -f "$ERR"
# 7.0.0: an edited opencode.json is backed up on re-install, never silently overwritten.
python3 - "$T/opencode.json" <<'PY2'
import json,sys; p=sys.argv[1]; c=json.load(open(p)); c["_plant_local_marker"]="keep-me"; json.dump(c,open(p,"w"),indent=2)
PY2
"$ROOT/install.sh" opencode --project-dir "$T" --copy >/dev/null 2>&1
ls "$T/"opencode.json.bak-* >/dev/null 2>&1 \
  || { echo "re-install overwrote an edited opencode.json without a backup" >&2; exit 1; }
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
  rm -rf "$T"
}

case_codex() {
  local T; T="$(mktemp -d)"
  local ERR; ERR="$(mktemp)"
# E3 LEGACY_INSTALL_STILL_SUCCEEDS: a frozen host named explicitly still installs
# and exits 0 (ADR-0009).
"$ROOT/install.sh" codex --project-dir "$T" --copy --force >/dev/null 2>"$ERR" \
  || { echo "LEGACY_INSTALL_STILL_SUCCEEDS: install.sh codex exited non-zero:" >&2; cat "$ERR" >&2; exit 1; }
# LEGACY_INSTALL_PRINTS_DEPRECATED: exactly one DEPRECATED line on stderr,
# naming the tool and ADR-0009.
assert_one_deprecated_line "$ERR" codex
# LEGACY_INSTALL_STILL_SUCCEEDS: its destinations are placed as at 7.26.0.
need "$T/.codex/agents/00-orchestrator.md" codex
need "$T/docs/graph/templates/prompts/handback-payload.md" codex
[[ ! -e "$T/.codex/protocols" ]] || { echo "STALE .codex/protocols" >&2; exit 1; }
grep -q "context-router" "$T/.codex/codex-config-snippet.toml"
grep -q "validate-knowledge" "$T/.codex/codex-config-snippet.toml"
# LEGACY_INSTALL_STILL_SUCCEEDS: `codex --print-config` stdout is config a user
# pastes, so the notice must not reach it. The notice must still reach stderr
# in the same run, or "stdout carries no DEPRECATED" would hold vacuously.
local OUT; OUT="$(mktemp)"
"$ROOT/install.sh" codex --project-dir "$T" --print-config >"$OUT" 2>"$ERR" \
  || { echo "LEGACY_INSTALL_STILL_SUCCEEDS: install.sh codex --print-config exited non-zero:" >&2; cat "$ERR" >&2; exit 1; }
if grep -q 'DEPRECATED' "$OUT"; then
  echo "LEGACY_INSTALL_STILL_SUCCEEDS: codex --print-config wrote the DEPRECATED notice to stdout:" >&2
  grep 'DEPRECATED' "$OUT" >&2; exit 1
fi
grep -q 'DEPRECATED' "$ERR" \
  || { echo "LEGACY_INSTALL_STILL_SUCCEEDS: codex --print-config printed no DEPRECATED notice on stderr, so its clean stdout proves nothing:" >&2; cat "$ERR" >&2; exit 1; }
  rm -rf "$T" "$ERR" "$OUT"
}

case_github_copilot() {
  local T; T="$(mktemp -d)"
  local ERR; ERR="$(mktemp)"
# LEGACY_INSTALL_STILL_SUCCEEDS: a frozen host named explicitly still installs
# and exits 0 (ADR-0009).
"$ROOT/install.sh" github-copilot --project-dir "$T" --copy --force >/dev/null 2>"$ERR" \
  || { echo "LEGACY_INSTALL_STILL_SUCCEEDS: install.sh github-copilot exited non-zero:" >&2; cat "$ERR" >&2; exit 1; }
# LEGACY_INSTALL_PRINTS_DEPRECATED: exactly one DEPRECATED line on stderr,
# naming the tool and ADR-0009.
assert_one_deprecated_line "$ERR" github-copilot
rm -f "$ERR"
# LEGACY_INSTALL_STILL_SUCCEEDS: its destinations are placed as at 7.26.0.
need "$T/.github/copilot-instructions.md" github-copilot
need "$T/docs/graph/templates/prompts/graph-session-bootstrap.md" github-copilot
need "$T/.github/prompts/recover.prompt.md" github-copilot
[[ ! -e "$T/.github/templates" ]] || { echo "STALE .github/templates" >&2; exit 1; }
assert_cmd_roster "$T/.github/prompts" .prompt.md "github-copilot prompts"

# COPILOT_POINTER_OVERHEAD must not sit BELOW what this install just wrote.
# The constant models the boilerplate each .github/instructions/ pointer adds on
# top of the skill description it carries, and check_eager_surface adds it to
# the modelled github-copilot eager surface. It was typed at 5_300 with a
# comment saying "measured from an install, not guessed"; a real install writes
# 5_638, so the modelled surface sat 338 bytes below what ships — the one
# direction that comment exists to prevent. Three careful hand-derivations of
# this number produced 5 606, 5 612 and 5 638, each differing only in how the
# deriver defined `skill_desc`. So it is measured HERE, against the install
# that just ran, using seed-lint's own definition of the terms it feeds.
python3 - "$T" "$ROOT" <<'PYEOF'
import importlib.util, pathlib, sys
target, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("sl", root / "tests" / "seed-lint.py")
sl = importlib.util.module_from_spec(spec); sys.modules["sl"] = sl
spec.loader.exec_module(sl)
skill_desc = sum(len(sl.description_of(fm))
                 for label, fm, _b in sl.machinery_nodes()
                 if label.startswith("skills/"))
shipped = sum(f.stat().st_size for f in (target / ".github/instructions").glob("*"))
if not shipped:
    print("FAIL: no .github/instructions/ files to measure — the probe is vacuous",
          file=sys.stderr); sys.exit(1)
measured = shipped - skill_desc
if measured > sl.COPILOT_POINTER_OVERHEAD:
    print(f"FAIL: COPILOT_POINTER_OVERHEAD is {sl.COPILOT_POINTER_OVERHEAD} and a "
          f"real install writes {measured} bytes of pointer boilerplate "
          f"({shipped} in .github/instructions/ minus {skill_desc} of skill "
          f"description). The modelled eager surface is then "
          f"{measured - sl.COPILOT_POINTER_OVERHEAD} bytes BELOW what ships, "
          f"which is the one direction the constant exists to prevent.",
          file=sys.stderr)
    sys.exit(1)
slack = sl.COPILOT_POINTER_OVERHEAD - measured
if slack > 512:
    print(f"FAIL: COPILOT_POINTER_OVERHEAD is {sl.COPILOT_POINTER_OVERHEAD} and a "
          f"real install writes {measured} — {slack} bytes of slack. A modelled "
          f"figure that overstates by more than half a kilobyte is not a "
          f"measurement; lower it to {measured}.", file=sys.stderr)
    sys.exit(1)
print(f"  copilot pointer overhead: modelled {sl.COPILOT_POINTER_OVERHEAD}, "
      f"measured {measured} ({slack} B slack)")
PYEOF
  rm -rf "$T"
}

case_prime_agent() {
  local T; T="$(mktemp -d)"
"$ROOT/install.sh" prime-agent --project-dir "$T" --copy --force >/dev/null
need "$T/AGENTS.md" prime-agent
need "$T/.prime/agent/agents/00-orchestrator.md" prime-agent
need "$T/.prime/agent/agents/_routes.golden.tsv" prime-agent
need "$T/.prime/agent/skills/context-router/SKILL.md" prime-agent
need "$T/.prime/agent/prompts/recover.md" prime-agent
need "$T/.prime/agent/extensions/route-extension.ts"
need "$T/.prime/agent/extensions/status-extension.ts" prime-agent
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
  rm -rf "$T"
}

_coexist() {
  local order="$1"
# --- Interchangeable Claude Code + Prime Agent in ONE plant --------------
# The two first-class harnesses must coexist in a single plant off a shared,
# non-drifting kernel. Install both into a FRESH dir and assert one kernel file
# is the source of truth (the other a symlink to it), both harness trees exist,
# and the knowledge graph is shared. Both install orders must converge.
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
}

case_graft_stale_kernel() {
# REGRESSION — GRAFT over a STALE kernel must fast-forward the kernel BODY,
# not merely re-point the CLAUDE.md<->AGENTS.md symlink. place_kernel once
# symlinked one kernel file to the other and left the underlying STALE body
# untouched — AND made no .bak — so a graft silently left the plant on an OLD
# kernel (loaded on every session of every adapter) and graft-audit was blind
# to it. A copy-mode (no --force) install over pre-existing stale kernels must
# bring BOTH files to the current seed kernel and leave a backup behind.
D="$(mktemp -d)"
printf '# OLD STALE KERNEL 5.x\nstale body\n' > "$D/AGENTS.md"
printf '# OLD STALE KERNEL 5.x\nstale body\n' > "$D/CLAUDE.md"
"$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null
diff -q "$D/AGENTS.md" "$ROOT/core/AGENTS.md" >/dev/null \
  || { echo "stale-kernel graft: AGENTS.md not fast-forwarded to the seed kernel" >&2; exit 1; }
diff -q "$D/CLAUDE.md" "$ROOT/core/AGENTS.md" >/dev/null \
  || { echo "stale-kernel graft: CLAUDE.md not fast-forwarded to the seed kernel" >&2; exit 1; }
[[ -n "$(find "$D" -maxdepth 1 -name '*.bak-*')" ]] \
  || { echo "stale-kernel graft: no .bak left — graft-audit would be blind to the kernel overwrite" >&2; exit 1; }
rm -rf "$D"
echo "  graft over stale kernel: body fast-forwarded + backup left — OK"
}

case_idempotent_rerun() {
# REGRESSION — idempotent re-run: a second identical install must create no
# backups. 6.9.0 backed up and rewrote byte-identical files (hundreds of no-op
# .bak entries per documented re-run, burying graft-audit's real signal), and
# opencode/codex/copilot placed AGENTS.md via raw place_file while prime-agent
# used place_kernel — the two ping-ponged the kernel file into fresh churn on
# every run of `install.sh all`.
D="$(mktemp -d)"
"$ROOT/install.sh" $EVERY_HOST --project-dir "$D" --copy >/dev/null
"$ROOT/install.sh" $EVERY_HOST --project-dir "$D" --copy >/dev/null
n="$(find "$D" -name '*.bak-*' | wc -l)"
[[ "$n" -eq 0 ]] || { echo "re-run churn: $n spurious .bak file(s) created by an identical re-install" >&2; exit 1; }
rm -rf "$D"
echo "  idempotent re-run: zero .bak churn — OK"
}

case_glob_metachar() {
# REGRESSION — a seed checked out under a glob-metachar path ('seed [copy]')
# must still land files at the declared destinations: the unquoted \${f#\$src/}
# prefix-strip treated \$src as a glob pattern, silently nesting every machinery
# file under the full absolute source path while reporting success.
SB="$(mktemp -d)"; S="$SB/seed [copy]"
mkdir -p "$S"
( cd "$ROOT" && tar --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache -cf - . ) \
  | ( cd "$S" && tar -xf - )
D="$(mktemp -d)"
bash "$S/install.sh" codex --project-dir "$D" --copy >/dev/null
need "$D/docs/graph/protocols/deliver.md" "glob-metachar-seed-path"
need "$D/docs/graph/method/tiers.md" "glob-metachar-seed-path"
rm -rf "$D" "$SB"
echo "  glob-metachar seed path installs to declared destinations — OK"
}

case_no_symlink_churn() {
# REGRESSION — a platform without symlinks (ln -s fails; place_kernel's own
# degradation path) must not churn: the pristine kernel copy was backed up and
# re-copied on EVERY run (5 .bak per five-host re-run pre-fix). Both kernels must
# stay byte-identical independent copies.
SHIM="$(mktemp -d)"
printf '#!/bin/sh\nexit 1\n' > "$SHIM/ln"; chmod +x "$SHIM/ln"
D="$(mktemp -d)"
PATH="$SHIM:$PATH" "$ROOT/install.sh" $EVERY_HOST --project-dir "$D" --copy >/dev/null
PATH="$SHIM:$PATH" "$ROOT/install.sh" $EVERY_HOST --project-dir "$D" --copy >/dev/null
n="$(find "$D" -name '*.bak-*' | wc -l)"
[[ "$n" -eq 0 ]] || { echo "no-symlink kernel churn: $n .bak file(s) on identical re-runs" >&2; exit 1; }
diff -q "$D/CLAUDE.md" "$D/AGENTS.md" >/dev/null \
  || { echo "no-symlink kernels drifted apart" >&2; exit 1; }
rm -rf "$D" "$SHIM"
echo "  symlink-less platform: kernel copies converge with zero churn — OK"
}

case_universal_router() {
# REGRESSION — the kernel mandates `python3 docs/graph/agent-lint.py --route`
# on EVERY harness, but the router was once placed only by the claude-code
# adapter: a single-tool opencode/codex/copilot/prime-agent plant had an
# unexecutable mandatory first routing step. Every adapter must now yield a
# working router at the universal path.
for tool in claude-code opencode codex github-copilot prime-agent; do
  D="$(mktemp -d)"
  "$ROOT/install.sh" "$tool" --project-dir "$D" --copy >/dev/null
  need "$D/docs/graph/agent-lint.py" "$tool-universal-router"
  need "$D/docs/graph/agents/_routes.golden.tsv" "$tool-golden-corpus"
  ( cd "$D" && python3 docs/graph/agent-lint.py --lint >/dev/null ) \
    || { echo "$tool: --lint failed in-plant" >&2; exit 1; }
  ( cd "$D" && python3 docs/graph/agent-lint.py --route "audit the diff against the spec" >/dev/null ) \
    || { echo "$tool: --route (the kernel-mandated step) failed in-plant" >&2; exit 1; }
  ( cd "$D" && python3 docs/graph/agent-lint.py --eval >/dev/null ) \
    || { echo "$tool: --eval (the graft exit gate) failed in-plant" >&2; exit 1; }
  rm -rf "$D"
done
echo "  universal agent router (--lint/--route/--eval) works on all five adapters — OK"
}

case_router_fast_forward() {
# REGRESSION — the universal router must FAST-FORWARD: the first placement was
# add-if-missing, so a plant kept a stale router forever while the .claude
# projection refreshed — the kernel-mandated path was the stale one.
D="$(mktemp -d)"
"$ROOT/install.sh" opencode --project-dir "$D" --copy >/dev/null
printf '# STALE ROUTER v1\n' > "$D/docs/graph/agent-lint.py"
"$ROOT/install.sh" opencode --project-dir "$D" --copy >/dev/null
grep -q "STALE ROUTER" "$D/docs/graph/agent-lint.py" \
  && { echo "docs/graph/agent-lint.py not fast-forwarded on re-install" >&2; exit 1; }
n="$(find "$D/docs/graph" -name 'agent-lint.py.bak-*' | wc -l)"
[[ "$n" -eq 1 ]] || { echo "router fast-forward must back up the changed file (got $n baks)" >&2; exit 1; }
rm -rf "$D"
echo "  universal router fast-forwards with backup on re-install — OK"
}

case_copilot_projection_tools() {
# REGRESSION — Copilot agent projection once granted ONE fixed tool superset
# (editFiles/runCommands for everyone): the source allowlist is the
# discipline. Read-only-ish agents must not gain write/run tools.
D="$(mktemp -d)"
"$ROOT/install.sh" github-copilot --project-dir "$D" --copy >/dev/null
grep -q "editFiles" "$D/.github/agents/reviewer.agent.md" \
  && { echo "copilot: reviewer (no Write/Edit) was granted editFiles" >&2; exit 1; }
grep -q "runTasks" "$D/.github/agents/devils-advocate.agent.md" \
  && { echo "copilot: devils-advocate (no Bash) was granted runTasks" >&2; exit 1; }
grep -q "githubRepo" "$D/.github/agents/implementer.agent.md" \
  && { echo "copilot: implementer (no web tools) was granted githubRepo" >&2; exit 1; }
grep -q "editFiles" "$D/.github/agents/implementer.agent.md" \
  || { echo "copilot: implementer lost editFiles" >&2; exit 1; }
grep -q "runCommands" "$D/.github/agents/ui-ux-designer.agent.md" \
  || { echo "copilot: ui-ux-designer lost runCommands (its charter mandates graph-lint --plan)" >&2; exit 1; }
grep -q "githubRepo" "$D/.github/agents/devils-advocate.agent.md" \
  || { echo "copilot: devils-advocate (WebSearch) lost githubRepo" >&2; exit 1; }
rm -rf "$D"
echo "  copilot projection derives tools from each agent allowlist — OK"
}

case_seed_stamp() {
# The seed stamp: install.sh writes it, so a plant always knows which seed it
# carries. protocols/graft.md described this marker from 4.6.0 onward but
# nothing wrote it, leaving every graft to guess its own merge base and leaving
# growth-audit's stamp-vs-record cross-check permanently inert.
D="$(mktemp -d)"
"$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null
[[ -f "$D/.cypress/seed.json" ]] \
  || { echo "install: no .cypress/seed.json stamp was written" >&2; exit 1; }
python3 - "$D" "$ROOT" <<'PY'
import json, sys, pathlib
d, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
stamp = json.loads((d/".cypress/seed.json").read_text())
want = json.loads((root/"manifest.json").read_text())["version"]
assert stamp["seed"] == "cypress", stamp
assert stamp["version"] == want, f"stamp {stamp['version']} != manifest {want}"
assert "claude-code" in stamp["tools"], stamp
assert "installed_from" not in stamp, "a first install has nothing to advance from"
PY
echo "  install.sh stamps .cypress/seed.json with the manifest version — OK"

# Re-installing over an older stamp records where the plant came FROM: that is
# the base a graft's three-way merge needs.
python3 - "$D" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])/".cypress/seed.json"
s = json.loads(p.read_text()); s["version"] = "0.0.1-old"
p.write_text(json.dumps(s, indent=2) + "\n")
PY
"$ROOT/install.sh" claude-code --project-dir "$D" --copy --force >/dev/null
python3 - "$D" <<'PY'
import json, pathlib, sys
s = json.loads((pathlib.Path(sys.argv[1])/".cypress/seed.json").read_text())
assert s["installed_from"] == "0.0.1-old", s
assert s["version"] != "0.0.1-old", s
PY
echo "  re-install records installed_from — the graft's merge base — OK"
rm -rf "$D"
}

caseALL_EXCLUDES_LEGACY_HOSTS() {
# E1 ALL_EXCLUDES_LEGACY_HOSTS (SPEC-0001, ADR-0009): `all` installs the maintained
# hosts only. The frozen pair installs when named, never by default.
local D; D="$(mktemp -d)"
"$ROOT/install.sh" all --project-dir "$D" --copy >/dev/null 2>&1 \
  || { echo "ALL_EXCLUDES_LEGACY_HOSTS: install.sh all failed" >&2; exit 1; }
local d
for d in .claude .opencode .prime/agent; do
  [[ -d "$D/$d" ]] || { echo "ALL_EXCLUDES_LEGACY_HOSTS: install.sh all did not place $d/" >&2; exit 1; }
done
for d in .codex .github; do
  [[ ! -e "$D/$d" ]] || { echo "ALL_EXCLUDES_LEGACY_HOSTS: install.sh all placed $d/, which belongs to a frozen host" >&2; exit 1; }
done
python3 - "$D/.cypress/seed.json" <<'PY'
import json, sys
tools = json.load(open(sys.argv[1], encoding="utf-8"))["tools"]
want = "claude-code opencode prime-agent"
if tools != want:
    sys.exit(f"ALL_EXCLUDES_LEGACY_HOSTS: stamp tools is {tools!r}, expected exactly {want!r}")
PY
rm -rf "$D"
echo "  ALL_EXCLUDES_LEGACY_HOSTS: all installs claude-code, opencode and prime-agent only — OK"
}

case_plant_facts_index_no_fm() {
# ---- the plant: block: absent is not "already declared" -------------------
# A project grown before the block existed has no block at all, so no
# placeholder line matched, and the installer took its else-branch and
# announced all four facts as already declared — suppressing the write AND the
# NEXT STEP warning that was supposed to catch it. The block stayed missing,
# which is the exact state it exists to prevent.
  local B; B="$(mktemp -d)"; local D="$B/plantfacts"; mkdir -p "$D/docs/graph"
printf '<!--\ntemplate note\n-->\n\n# The router\n' > "$D/docs/graph/index.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$D" --copy --force \
        --environment-class staging --commit-attribution none \
        --deliverable-language en --comment-language en 2>&1)"
grep -q "already declared" <<<"$out" \
  && { printf '%s\n' "$out" >&2; echo "an ABSENT plant fact was reported as already declared" >&2; exit 1; }
python3 - "$D" <<'PY'
import re, sys, pathlib
t = (pathlib.Path(sys.argv[1])/"docs/graph/index.md").read_text()
m = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
assert m, "no frontmatter was created over an index that had none"
fm = m.group(1)
for k, v in (("environment_class","staging"), ("commit_attribution","none"),
             ("deliverable_language","en"), ("comment_language","en")):
    assert re.search(rf"^  {k}: {v}$", fm, re.M), f"{k} not written: {fm!r}"
assert "# The router" in t, "the index body was lost"
PY
echo "  an index with no frontmatter gains the plant: block with the passed values — OK"
  rm -rf "$B"
}

case_plant_facts_bare() {
# no flags: the block still appears, with placeholders, and NEXT STEP names them
  local B; B="$(mktemp -d)"; local D="$B/plantfacts-bare"; mkdir -p "$D/docs/graph"
printf '<!--\nx\n-->\n\n# The router\n' > "$D/docs/graph/index.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$D" --copy --force 2>&1)"
grep -q "plant facts still unset in docs/graph/index.md: environment_class commit_attribution deliverable_language comment_language" <<<"$out" \
  || { printf '%s\n' "$out" >&2; echo "NEXT STEP did not name every unset plant fact" >&2; exit 1; }
grep -qE '^  environment_class: <' "$D/docs/graph/index.md" \
  || { echo "no placeholder block was written without flags" >&2; exit 1; }
  rm -rf "$B"
}

case_plant_facts_declared() {
# a declared value is never overwritten, and a re-run is idempotent
  local B; B="$(mktemp -d)"; local D="$B/plantfacts-declared"; mkdir -p "$D/docs/graph"
printf -- '---\ngrown: true\nplant:\n  environment_class: real-production\n  commit_attribution: none\n  deliverable_language: it\n  comment_language: it\n---\n\n# The router\n' \
  > "$D/docs/graph/index.md"
out="$("$ROOT/install.sh" claude-code --project-dir "$D" --copy --force --environment-class staging 2>&1)"
grep -q "already declared as real-production" <<<"$out" \
  || { printf '%s\n' "$out" >&2; echo "a declared value was not reported as declared" >&2; exit 1; }
grep -q '^  environment_class: real-production$' "$D/docs/graph/index.md" \
  || { echo "a declared plant fact was overwritten by a flag" >&2; exit 1; }
"$ROOT/install.sh" claude-code --project-dir "$D" --copy --force --environment-class staging >/dev/null 2>&1
[ "$(grep -c '^plant:' "$D/docs/graph/index.md")" = 1 ] \
  || { echo "a re-run duplicated the plant: block" >&2; exit 1; }
[ "$(grep -c '^---$' "$D/docs/graph/index.md")" = 2 ] \
  || { echo "a re-run duplicated the frontmatter fence" >&2; exit 1; }
  rm -rf "$B"
}

case_plant_facts_partial() {
# a block that predates one key gains it, in the template's words and in order
  local B; B="$(mktemp -d)"; local D="$B/plantfacts-partial"; mkdir -p "$D/docs/graph"
printf -- '---\ngrown: false\nplant:\n  environment_class: mixed\n  commit_attribution: none\n---\n\n# The router\n' \
  > "$D/docs/graph/index.md"
"$ROOT/install.sh" claude-code --project-dir "$D" --copy --force --deliverable-language en >/dev/null 2>&1
python3 - "$D" <<'PY'
import re, sys, pathlib
fm = re.match(r"\A---\n(.*?)\n---\n", (pathlib.Path(sys.argv[1])/"docs/graph/index.md").read_text(), re.S).group(1)
keys = re.findall(r"^  (environment_class|commit_attribution|deliverable_language|comment_language):", fm, re.M)
assert keys == ["environment_class", "commit_attribution", "deliverable_language", "comment_language"], keys
assert re.search(r"^  comment_language: <bcp47>$", fm, re.M), fm
PY
echo "  declared values survive, re-runs are idempotent, a missing key is appended in order — OK"
  rm -rf "$B"
}

caseROSTER_PROJECTION_PARITY_KEEPS_A_LIVE_HOME() {
# --- the parity claim is relocated, not retired ---------------------------
# SPEC-0001 ROSTER_PROJECTION_PARITY_KEEPS_A_LIVE_HOME. The predicate has to be
# a thing that can be pointed at a directory, or the claim above cannot be
# exercised against anything but the one projection the gate happens to build,
# and nobody can tell a working check from a check that compares one file.
# Equality in BOTH directions is the load-bearing half: a one-way rule — every
# seed file present and identical in the host — is satisfied by a host that has
# ADDED an agent, and a host that has added an agent is exactly the case that
# took the gate down.
  local T; T="$(mktemp -d)"
  "$ROOT/install.sh" claude-code --project-dir "$T" --copy --force >/dev/null
  declare -F projection_parity >/dev/null \
    || { echo "test-full-install: FAIL — projection_parity() is not defined; the parity claim has no callable home" >&2; exit 1; }
  # the real projection the gate just built must satisfy it
  projection_parity "$ROOT/agents" "$T/.claude/agents" \
    || { echo "test-full-install: FAIL — the install's own projection was rejected by the predicate" >&2; exit 1; }
  local M
  # superset: the host holds a file the seed does not. `cmp` of one file
  # accepts this, and this is the live shape of every grown plant.
  M="$(mktemp -d)"; cp -a "$T/.claude/agents/." "$M/"
  printf -- '---\nname: host-only\n---\nbody\n' > "$M/99-host-only.md"
  if projection_parity "$ROOT/agents" "$M"; then
    rm -rf "$M"; echo "test-full-install: FAIL — a projection holding an agent the seed does not have was accepted" >&2; exit 1
  fi
  rm -rf "$M"
  # stale: the seed holds a file the host does not
  M="$(mktemp -d)"; cp -a "$T/.claude/agents/." "$M/"; rm -f "$M/03-reviewer.md"
  if projection_parity "$ROOT/agents" "$M"; then
    rm -rf "$M"; echo "test-full-install: FAIL — a projection missing one of the seed's agents was accepted" >&2; exit 1
  fi
  rm -rf "$M"
  # forked: a shared filename differs by a byte
  M="$(mktemp -d)"; cp -a "$T/.claude/agents/." "$M/"; printf '\n' >> "$M/03-reviewer.md"
  if projection_parity "$ROOT/agents" "$M"; then
    rm -rf "$M"; echo "test-full-install: FAIL — a projection whose agent file drifted by a byte was accepted" >&2; exit 1
  fi
  rm -rf "$M"
  echo "  the roster projection is decided by set equality both ways plus byte identity — OK"
  rm -rf "$T"
}

SELF="$ROOT/tests/test-full-install.sh"

# Re-invoke self to run ONE scenario in isolation (reached in a child bash
# spawned by gate_pool). Every top-level helper and case_* function above is
# defined before this point, so the child has them all.
if [ "${1:-}" = "__case" ]; then
  shift
  "$@"
  exit $?
fi

main() {
  local SCN; SCN="$(mktemp)"
  local c
  for c in \
    case_claude_code case_plant_facts_flags case_opencode case_codex \
    case_github_copilot case_prime_agent case_graft_stale_kernel \
    case_idempotent_rerun case_glob_metachar case_no_symlink_churn \
    case_universal_router case_router_fast_forward \
    case_copilot_projection_tools case_seed_stamp caseALL_EXCLUDES_LEGACY_HOSTS \
    case_plant_facts_index_no_fm case_plant_facts_bare \
    case_plant_facts_declared case_plant_facts_partial \
    caseROSTER_PROJECTION_PARITY_KEEPS_A_LIVE_HOME; do
    printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
  done
  # both CC/PA install orders (parametrized case)
  local o
  for o in "claude-code prime-agent" "prime-agent claude-code"; do
    printf '%s\t%s\n' "coexist($o)" "bash \"$SELF\" __case _coexist \"$o\"" >> "$SCN"
  done

  local rc=0
  python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?
  rm -f "$SCN"

  # --- serial tail: writes into the seed, runs alone after the pool ----------
# --- bytecode is never seed content ---------------------------------------
# `place_tree`'s default `*` pattern copied everything under templates/,
# including a __pycache__/ that appears the moment anyone runs a linter in the
# seed before installing. It is gitignored here, so no Git-based check saw it,
# and it landed in the plant as a tracked file — one installer's interpreter
# version shipped as plant data.
# This scenario WRITES a fixture under $ROOT, so it must run alone — never
# inside the concurrent pool above. It runs serially here, after the pool has
# drained, when no other install is touching the seed.
BTMP="$(mktemp -d)"; trap 'rm -rf "$BTMP"' EXIT
mkdir -p "$ROOT/templates/knowledge-graph/__pycache__"
printf 'fake bytecode\n' > "$ROOT/templates/knowledge-graph/__pycache__/zz-fixture.cpython-999.pyc"
bash "$ROOT/install.sh" claude-code --project-dir "$BTMP" >/dev/null 2>&1
rm -f "$ROOT/templates/knowledge-graph/__pycache__/zz-fixture.cpython-999.pyc"
found="$(find "$BTMP" \( -name '*.pyc' -o -name '__pycache__' \) | wc -l | tr -d ' ')"
[[ "$found" == "0" ]] \
    || { find "$BTMP" \( -name '*.pyc' -o -name '__pycache__' \) >&2
         echo "test-full-install: FAIL — $found bytecode path(s) placed into the plant" >&2; exit 1; }
echo "  bytecode never reaches the plant — OK"

  [ "$rc" -eq 0 ] || { echo "test-full-install: FAIL" >&2; exit "$rc"; }
  printf 'full five-tool install contract + CC/PA coexistence: PASS\n'
}

main
