#!/usr/bin/env bash
# Full-install contract: every adapter delivers its runtime surfaces, and the
# plant's own router, linters and hooks run in the installed tree.
# E family (SPEC-0001, ADR-0009 host tiers): E1-E3, E5 and E6 here; E4 is in test-seed-lint.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/tests/helpers/plant.sh"

# Every host the installer can place, named explicitly (ADR-0009); `all` names
# only the maintained hosts. Unquoted at each call: it splits into five tools.
EVERY_HOST="claude-code opencode codex github-copilot prime-agent"

need() { [[ -e "$1" ]] || { echo "MISSING after $2 install: $1" >&2; exit 1; }; }
die() { echo "$*" >&2; exit 1; }

# fresh_copy <dst> <hosts> [flags]: a copy of the suite's shared base install.
fresh_copy() { local dst="$1"; shift; plant_base "$@"; plant_copy "$dst"; }

# The slash-command roster is generated from protocols with `command: true`;
# no harness may emit the user-sovereign graft/grow/harvest.
EXPECTED_CMDS="$(grep -l '^command: true' "$ROOT"/protocols/*.md \
  | while read -r f; do b="$(basename "$f")"; echo "${b%.md}"; done | sort)"
[[ -n "$EXPECTED_CMDS" ]] || die "no command:true protocols found"

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
  for s in graft grow harvest; do
    [[ ! -e "$dir/$s$suffix" ]] || die "$label: sovereign '$s' leaked as a command"
  done
}

# SPEC-0001 §6 projection predicate: the non-underscore *.md sets equal in both
# directions, the golden corpus in both, every shared file byte-identical.
projection_parity() {
  local home="$1" proj="$2" f home_set proj_set
  local -a shared=(_routes.golden.tsv)
  [[ -f "$home/_routes.golden.tsv" && -f "$proj/_routes.golden.tsv" ]] \
    || { echo "projection_parity: _routes.golden.tsv missing from $home or $proj" >&2; return 1; }
  home_set="$(cd "$home" && ls -1 *.md 2>/dev/null | grep -v '^_' | LC_ALL=C sort || true)"
  proj_set="$(cd "$proj" && ls -1 *.md 2>/dev/null | grep -v '^_' | LC_ALL=C sort || true)"
  if [[ "$home_set" != "$proj_set" ]]; then
    echo "projection_parity: agent set differs between $home and $proj" >&2
    diff <(printf '%s\n' "$home_set") <(printf '%s\n' "$proj_set") >&2 || true
    return 1
  fi
  [[ -n "$home_set" ]] || { echo "projection_parity: no agent file in $home or $proj" >&2; return 1; }
  while IFS= read -r f; do shared+=("$f"); done <<< "$home_set"
  for f in "${shared[@]}"; do
    cmp -s "$home/$f" "$proj/$f" || { echo "projection_parity: $f differs between $home and $proj" >&2; return 1; }
  done
}

# E2 LEGACY_INSTALL_PRINTS_DEPRECATED: exactly one DEPRECATED line on stderr
# ($1), naming the frozen tool ($2) and ADR-0009.
assert_one_deprecated_line() {
  local err="$1" tool="$2" n line
  n="$(grep -c 'DEPRECATED' "$err" || true)"
  [[ "$n" -eq 1 ]] || { echo "LEGACY_INSTALL_PRINTS_DEPRECATED: install.sh $tool printed $n DEPRECATED line(s), expected 1:" >&2; cat "$err" >&2; exit 1; }
  line="$(grep 'DEPRECATED' "$err")"
  grep -qF -- "$tool" <<<"$line" || die "LEGACY_INSTALL_PRINTS_DEPRECATED: the DEPRECATED line does not name $tool: $line"
  grep -qi 'adr-0009' <<<"$line" || die "LEGACY_INSTALL_PRINTS_DEPRECATED: the DEPRECATED line does not name ADR-0009: $line"
}

case_claude_code() {
  local T; T="$(mktemp -d)"
  fresh_copy "$T" claude-code --copy
  python3 "$T/docs/graph/status-register.py" --root "$T/docs/graph" --summary >/dev/null \
    || die "installed status-register.py does not run in the plant"
  grep -q '"SessionStart"' "$T/.claude/settings.json" \
    || die ".claude/settings.json does not register the SessionStart status hook"
  python3 "$T/docs/graph/agnosticism-lint.py" --root "$T/docs/graph/protocols" >/dev/null \
    || die "installed agnosticism-lint.py does not run in the plant"
  local prc=0   # prose-lint findings (exit 1) are the tool working; exit 2 is not
  python3 "$T/docs/graph/prose-lint.py" --file "$T/docs/graph/skills/humanizer.md" >/dev/null 2>&1 || prc=$?
  [ "$prc" -ne 2 ] || die "installed prose-lint.py does not run in the plant"
  python3 "$T/.claude/agent-lint.py" --lint >/dev/null
  projection_parity "$ROOT/agents" "$T/.claude/agents" \
    || die "the install projection is not a faithful projection of the seed roster"
  (cd "$T" && python3 docs/graph/graph-lint.py >/dev/null) || die "the installed plant's graph does not lint clean"
  assert_cmd_roster "$T/.claude/commands" .md "claude-code commands"
  # The installed router SELECTS each entry arm (the LOAD block, not the NOT LOADED peers).
  selected() {
    (cd "$T" && python3 docs/graph/graph-lint.py --plan "$1" 2>/dev/null) \
      | awk '/^LOAD \(/{b=1; next} /^NOT LOADED/{b=0} b && /^  [a-z]+\./{print $1}'
  }
  assert_routes() {  # <task> <node-id>
    selected "$1" | grep -qx "$2" || die "routing: '$1' does not SELECT $2 (selected: $(selected "$1" | tr '\n' ' '))"
  }
  assert_routes "start a new project from nothing, the repo is empty" protocol.from-scratch
  assert_routes "just installed the seed, which protocol do I enter" protocol.initialize
  assert_routes "mkdir a new project and cd into it" protocol.from-scratch
  assert_routes "adopt this existing codebase into the graph by subsystem" protocol.grow
  local gone
  for gone in protocols/toolcraft.md skills/from-scratch-bootstrap.md; do
    [[ ! -e "$T/docs/graph/$gone" ]] || die "retired node still installed: $gone"
  done
  rm -rf "$T"
}

case_plant_facts_flags() {
  local P Q OUT; P="$(mktemp -d)"; Q="$(mktemp -d)"
  "$ROOT/install.sh" claude-code --project-dir "$P" --copy --force \
    --environment-class staging --commit-attribution none \
    --deliverable-language en --comment-language en >/dev/null
  local k
  for k in 'environment_class: staging' 'commit_attribution: none' 'comment_language: en'; do
    grep -q "^  $k\$" "$P/docs/graph/index.md" || die "plant facts: '$k' not written"
  done
  "$ROOT/install.sh" claude-code --project-dir "$P" --copy --force --environment-class production >/dev/null 2>&1 \
    && die "plant facts: invalid environment_class accepted"
  grep -q '^  environment_class: staging$' "$P/docs/graph/index.md" || die "plant facts: a filled value was overwritten"
  OUT="$("$ROOT/install.sh" claude-code --project-dir "$Q" --copy --force 2>&1)"
  grep -q '^  environment_class: <' "$Q/docs/graph/index.md" || die "plant facts: placeholder should remain without flags"
  grep -q "plant facts still unset in docs/graph/index.md: environment_class commit_attribution deliverable_language comment_language" <<<"$OUT" \
    || { printf '%s\n' "$OUT" >&2; die "NEXT STEP did not name every unset plant fact"; }
  rm -rf "$P" "$Q"
}

case_opencode() {
  local T; T="$(mktemp -d)"
  fresh_copy "$T" opencode --copy
  need "$T/.opencode/agents/00-orchestrator.md" opencode
  [[ ! -e "$T/opencode.jsonc" ]] || die "two opencode configs installed; precedence is unspecified"
  python3 - "$T/opencode.json" <<'EOF'
import json, sys
cfg = json.load(open(sys.argv[1]))
# opencode auto-loads AGENTS.md; the live schema sets additionalProperties:false.
assert "AGENTS.md" not in cfg.get("instructions", []), f"opencode double-load: {cfg.get('instructions')}"
assert cfg["$schema"] == "https://opencode.ai/config.json", f"stale $schema: {cfg['$schema']}"
for dead in ("agents", "commands"):
    assert dead not in cfg, f"{dead!r} is not an opencode config key"
assert cfg.get("skills", {}).keys() <= {"paths", "urls"}, f"bad skills shape: {cfg.get('skills')}"
assert cfg["subagent_depth"] == 3, f"delegation depth capped: {cfg.get('subagent_depth')}"
EOF
  assert_cmd_roster "$T/.opencode/commands" .md "opencode commands"
  rm -rf "$T"
}

# E3 LEGACY_INSTALL_STILL_SUCCEEDS and E2 for codex, into one directory whose
# name holds all seven hostile characters: space & [ ] # ' newline tab. The
# snippet is pasted into ~/.codex/config.toml, so the path must round-trip.
case_codex() {
  local W; W="$(cd "$(mktemp -d)" && pwd -P)"
  local T="$W/"$'a b&[c]#\'d\ne\tf' ERR="$W/err" OUT="$W/out"
  mkdir -p "$T"
  "$ROOT/install.sh" codex --project-dir "$T" --copy --force >/dev/null 2>"$ERR" \
    || { cat "$ERR" >&2; die "LEGACY_INSTALL_STILL_SUCCEEDS: install.sh codex exited non-zero"; }
  assert_one_deprecated_line "$ERR" codex
  need "$T/.codex/agents/00-orchestrator.md" codex
  need "$T/docs/graph/templates/prompts/handback-payload.md" codex
  local S="$T/.codex/codex-config-snippet.toml"
  grep -q "context-router" "$S"
  grep -q "validate-knowledge" "$S"
  EXPECT="$T" python3 "$ROOT/tests/helpers/codex-path-roundtrip.py" "$S" \
    || die "codex snippet does not carry the hostile target path intact"
  ! grep -q "abs/path/to/project" "$S" || die "codex snippet still holds the placeholder 'abs/path/to/project'"
  # --print-config stdout is pasted config: the notice goes to stderr only.
  "$ROOT/install.sh" codex --project-dir "$T" --print-config >"$OUT" 2>"$ERR" \
    || { cat "$ERR" >&2; die "LEGACY_INSTALL_STILL_SUCCEEDS: codex --print-config exited non-zero"; }
  ! grep -q 'DEPRECATED' "$OUT" || die "LEGACY_INSTALL_STILL_SUCCEEDS: codex --print-config wrote DEPRECATED to stdout"
  grep -q 'DEPRECATED' "$ERR" || die "LEGACY_INSTALL_STILL_SUCCEEDS: codex --print-config printed no DEPRECATED on stderr, so a clean stdout proves nothing"
  rm -rf "$W"
}

# The installer quotes its target everywhere, not only in the codex snippet.
case_claude_code_ampersand_path() {
  local W; W="$(cd "$(mktemp -d)" && pwd -P)"
  mkdir -p "$W/a&b-cc"
  "$ROOT/install.sh" claude-code --project-dir "$W/a&b-cc" >"$W/log" 2>&1 \
    || { cat "$W/log" >&2; die "claude-code install into a directory with '&' did not exit 0"; }
  rm -rf "$W"
}

case_github_copilot() {
  local T ERR; T="$(mktemp -d)"; ERR="$(mktemp)"
  "$ROOT/install.sh" github-copilot --project-dir "$T" --copy --force >/dev/null 2>"$ERR" \
    || { cat "$ERR" >&2; die "LEGACY_INSTALL_STILL_SUCCEEDS: install.sh github-copilot exited non-zero"; }
  assert_one_deprecated_line "$ERR" github-copilot
  need "$T/.github/copilot-instructions.md" github-copilot
  need "$T/.github/prompts/recover.prompt.md" github-copilot
  assert_cmd_roster "$T/.github/prompts" .prompt.md "github-copilot prompts"
  rm -rf "$T" "$ERR"
}

case_prime_agent() {
  local T; T="$(mktemp -d)"
  fresh_copy "$T" prime-agent --copy
  need "$T/.prime/agent/extensions/route-extension.ts" prime-agent
  need "$T/.prime/agent/APPEND_SYSTEM.md" prime-agent
  python3 - "$T/.prime/agent/settings.json" <<'EOF'
import json, sys
cfg = json.load(open(sys.argv[1]))
# resource paths resolve against .prime/agent/, so a ".prime/" prefix double-nests
for key in ("extensions", "skills", "prompts"):
    for entry in cfg.get(key, []):
        assert not entry.startswith(".prime/"), f"{key} entry {entry!r} is prefixed; use a bare name"
assert "rlmMaxDepth" not in cfg, "rlmMaxDepth in project settings is silently ignored"
EOF
  assert_cmd_roster "$T/.prime/agent/prompts" .md "prime-agent prompts"
  rm -rf "$T"
}

# A copy-mode install over stale kernels fast-forwards BOTH bodies and leaves a
# backup, so graft-audit sees the overwrite.
case_graft_stale_kernel() {
  local D; D="$(mktemp -d)"
  printf '# OLD STALE KERNEL 5.x\nstale body\n' > "$D/AGENTS.md"
  printf '# OLD STALE KERNEL 5.x\nstale body\n' > "$D/CLAUDE.md"
  "$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null
  cmp -s "$D/AGENTS.md" "$ROOT/core/AGENTS.md" || die "stale-kernel graft: AGENTS.md not fast-forwarded"
  cmp -s "$D/CLAUDE.md" "$ROOT/core/AGENTS.md" || die "stale-kernel graft: CLAUDE.md not fast-forwarded"
  [[ -n "$(find "$D" -maxdepth 1 -name '*.bak-*')" ]] || die "stale-kernel graft: no .bak left"
  rm -rf "$D"
}

# A seed under a glob-metachar path lands files at the declared destinations.
# A symlink named 'seed [copy]' gives install.sh that path without copying the tree.
case_glob_metachar() {
  local SB D; SB="$(mktemp -d)"; D="$(mktemp -d)"
  ln -s "$ROOT" "$SB/seed [copy]"
  bash "$SB/seed [copy]/install.sh" codex --project-dir "$D" --copy >/dev/null 2>&1
  need "$D/docs/graph/protocols/deliver.md" "glob-metachar-seed-path"
  need "$D/docs/graph/method/tiers.md" "glob-metachar-seed-path"
  rm -rf "$D" "$SB"
}

# Without ln -s the kernel copies converge and identical re-runs make no backup.
case_no_symlink_churn() {
  local SHIM D n; SHIM="$(mktemp -d)"; D="$(mktemp -d)"
  printf '#!/bin/sh\nexit 1\n' > "$SHIM/ln"; chmod +x "$SHIM/ln"
  PATH="$SHIM:$PATH" "$ROOT/install.sh" $EVERY_HOST --project-dir "$D" --copy >/dev/null
  PATH="$SHIM:$PATH" "$ROOT/install.sh" $EVERY_HOST --project-dir "$D" --copy >/dev/null
  n="$(find "$D" -name '*.bak-*' | wc -l)"
  [[ "$n" -eq 0 ]] || die "no-symlink kernel churn: $n .bak file(s) on identical re-runs"
  cmp -s "$D/CLAUDE.md" "$D/AGENTS.md" || die "no-symlink kernels drifted apart"
  rm -rf "$D" "$SHIM"
}

# The kernel mandates docs/graph/agent-lint.py --route on every harness.
case_universal_router() {
  local tool D
  for tool in $EVERY_HOST; do
    D="$(mktemp -d)"; fresh_copy "$D" "$tool" --copy
    (cd "$D" && python3 docs/graph/agent-lint.py --lint >/dev/null) || die "$tool: --lint failed in-plant"
    (cd "$D" && python3 docs/graph/agent-lint.py --route "audit the diff against the spec" >/dev/null) \
      || die "$tool: --route failed in-plant"
    (cd "$D" && python3 docs/graph/agent-lint.py --eval >/dev/null) || die "$tool: --eval failed in-plant"
    rm -rf "$D"
  done
}

# Copilot agent tools derive from each agent's allowlist, not one superset.
case_copilot_projection_tools() {
  local D; D="$(mktemp -d)"; fresh_copy "$D" github-copilot --copy
  local A="$D/.github/agents"
  ! grep -q "editFiles" "$A/reviewer.agent.md" || die "copilot: reviewer (no Write/Edit) was granted editFiles"
  ! grep -q "runTasks" "$A/devils-advocate.agent.md" || die "copilot: devils-advocate (no Bash) was granted runTasks"
  ! grep -q "githubRepo" "$A/implementer.agent.md" || die "copilot: implementer (no web tools) was granted githubRepo"
  grep -q "editFiles" "$A/implementer.agent.md" || die "copilot: implementer lost editFiles"
  grep -q "runCommands" "$A/ui-ux-designer.agent.md" || die "copilot: ui-ux-designer lost runCommands"
  grep -q "githubRepo" "$A/devils-advocate.agent.md" || die "copilot: devils-advocate (WebSearch) lost githubRepo"
  rm -rf "$D"
}

# The stamp carries the manifest version, and a re-install over an older one
# records installed_from: the base a graft's three-way merge needs.
case_seed_stamp() {
  local D; D="$(mktemp -d)"; fresh_copy "$D" claude-code --copy
  python3 - "$D/.cypress/seed.json" "$ROOT/manifest.json" <<'PY'
import json, sys
stamp, want = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))["version"]
assert stamp["seed"] == "cypress" and stamp["version"] == want, f"stamp {stamp} != manifest {want}"
assert "installed_from" not in stamp, "a first install has nothing to advance from"
stamp["version"] = "0.0.1-old"
open(sys.argv[1], "w").write(json.dumps(stamp, indent=2) + "\n")
PY
  "$ROOT/install.sh" claude-code --project-dir "$D" --copy --force >/dev/null
  python3 - "$D/.cypress/seed.json" <<'PY'
import json, sys
s = json.load(open(sys.argv[1]))
assert s["installed_from"] == "0.0.1-old" and s["version"] != "0.0.1-old", s
PY
  rm -rf "$D"
}

# E1 ALL_EXCLUDES_LEGACY_HOSTS: `all` installs the maintained hosts only, names
# no frozen host as deprecated, and stamps exactly those three.
caseALL_EXCLUDES_LEGACY_HOSTS() {
  local D d; D="$(mktemp -d)"; fresh_copy "$D" all --copy
  ! grep -q 'DEPRECATED' "$PLANT_BASE.log" || die "ALL_EXCLUDES_LEGACY_HOSTS: install.sh all printed a DEPRECATED line"
  for d in .claude .opencode .prime/agent; do
    [[ -d "$D/$d" ]] || die "ALL_EXCLUDES_LEGACY_HOSTS: install.sh all did not place $d/"
  done
  for d in .codex .github; do
    [[ ! -e "$D/$d" ]] || die "ALL_EXCLUDES_LEGACY_HOSTS: install.sh all placed $d/, a frozen host's"
  done
  python3 -c 'import json,sys; t=json.load(open(sys.argv[1]))["tools"]; sys.exit(None if t == "claude-code opencode prime-agent" else f"ALL_EXCLUDES_LEGACY_HOSTS: stamp tools is {t!r}")' \
    "$D/.cypress/seed.json"
  rm -rf "$D"
}

# E5 PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX (ADR-0017): one delimited
# block in the placeholder index, a kernel naming neither pointer, and (guard) a
# re-install leaves a plant-owned index with no block byte-identical.
case_pre_growth_pointer() {
  local D name; D="$(mktemp -d)"; fresh_copy "$D" claude-code --copy
  # E5 case_pre_growth_block_in_index
  python3 - "$D/docs/graph/index.md" <<'PY'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
opens = [i for i, l in enumerate(lines) if l == "<!-- pre-growth: grow removes this block -->"]
closes = [i for i, l in enumerate(lines) if l == "<!-- /pre-growth -->"]
if len(opens) != 1 or len(closes) != 1 or closes[0] < opens[0]:
    sys.exit(f"E5: index.md holds {len(opens)} pre-growth opening and {len(closes)} closing line(s)")
block = "\n".join(lines[opens[0] + 1:closes[0]])
for name in ("EXPERT_SEED_INSTALL_PROMPT.md", "protocol.initialize"):
    if name not in block:
        sys.exit(f"E5: the pre-growth block does not name {name}")
PY
  # E5 case_pre_growth_kernel_names_neither
  for name in EXPERT_SEED_INSTALL_PROMPT.md protocol.initialize; do
    ! grep -qF "$name" "$D/CLAUDE.md" || die "E5 (kernel): the placed CLAUDE.md names $name"
  done
  # E5 case_pre_growth_index_is_plant_owned (guard)
  awk '/^<!-- pre-growth: grow removes this block -->$/{s=1} !s{print} /^<!-- \/pre-growth -->$/{s=0}' \
    "$D/docs/graph/index.md" > "$D/index.before"
  printf '\nA grown plant router line.\n' >> "$D/index.before"
  cp "$D/index.before" "$D/docs/graph/index.md"
  "$ROOT/install.sh" claude-code --project-dir "$D" --copy >/dev/null 2>&1 || die "E5 (re-install): the re-install failed"
  cmp -s "$D/index.before" "$D/docs/graph/index.md" \
    || die "E5 (re-install): a re-install changed a plant-owned index.md that has no pre-growth block"
  rm -rf "$D"
}

# E6 CODE_ANCHOR_TOOL_IS_PLACED (ADR-0018): the tool the session hooks call is
# placed byte-identical, and the installer writes no anchor.
case_code_anchor_tool() {
  local D; D="$(mktemp -d)"; fresh_copy "$D" all --copy
  cmp -s "$ROOT/tools/code-anchor.py" "$D/docs/graph/code-anchor.py" \
    || die "E6: docs/graph/code-anchor.py is missing or differs from tools/code-anchor.py"
  [[ ! -e "$D/.cypress/anchor.json" ]] || die "E6: install.sh wrote .cypress/anchor.json; only canonize records one"
  rm -rf "$D"
}

# An index with no frontmatter is not "already declared": it gains the block.
case_plant_facts_index_no_fm() {
  local D out; D="$(mktemp -d)"; mkdir -p "$D/docs/graph"
  printf '<!--\ntemplate note\n-->\n\n# The router\n' > "$D/docs/graph/index.md"
  out="$("$ROOT/install.sh" claude-code --project-dir "$D" --copy --force \
          --environment-class staging --commit-attribution none \
          --deliverable-language en --comment-language en 2>&1)"
  ! grep -q "already declared" <<<"$out" || { printf '%s\n' "$out" >&2; die "an ABSENT plant fact was reported as already declared"; }
  python3 - "$D/docs/graph/index.md" <<'PY'
import re, sys
t = open(sys.argv[1]).read()
m = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
assert m, "no frontmatter was created over an index that had none"
for k, v in (("environment_class", "staging"), ("commit_attribution", "none"),
             ("deliverable_language", "en"), ("comment_language", "en")):
    assert re.search(rf"^  {k}: {v}$", m.group(1), re.M), f"{k} not written: {m.group(1)!r}"
assert "# The router" in t, "the index body was lost"
PY
  rm -rf "$D"
}

# A declared value is never overwritten, and a re-run is idempotent.
case_plant_facts_declared() {
  local D out; D="$(mktemp -d)"; mkdir -p "$D/docs/graph"
  printf -- '---\ngrown: true\nplant:\n  environment_class: real-production\n  commit_attribution: none\n  deliverable_language: it\n  comment_language: it\n---\n\n# The router\n' \
    > "$D/docs/graph/index.md"
  out="$("$ROOT/install.sh" claude-code --project-dir "$D" --copy --force --environment-class staging 2>&1)"
  grep -q "already declared as real-production" <<<"$out" || { printf '%s\n' "$out" >&2; die "a declared value was not reported as declared"; }
  grep -q '^  environment_class: real-production$' "$D/docs/graph/index.md" || die "a declared plant fact was overwritten by a flag"
  "$ROOT/install.sh" claude-code --project-dir "$D" --copy --force --environment-class staging >/dev/null 2>&1
  [ "$(grep -c '^plant:' "$D/docs/graph/index.md")" = 1 ] || die "a re-run duplicated the plant: block"
  [ "$(grep -c '^---$' "$D/docs/graph/index.md")" = 2 ] || die "a re-run duplicated the frontmatter fence"
  rm -rf "$D"
}

# A block that predates one key gains it, in the template's words and in order.
case_plant_facts_partial() {
  local D; D="$(mktemp -d)"; mkdir -p "$D/docs/graph"
  printf -- '---\ngrown: false\nplant:\n  environment_class: mixed\n  commit_attribution: none\n---\n\n# The router\n' \
    > "$D/docs/graph/index.md"
  "$ROOT/install.sh" claude-code --project-dir "$D" --copy --force --deliverable-language en >/dev/null 2>&1
  python3 - "$D/docs/graph/index.md" <<'PY'
import re, sys
fm = re.match(r"\A---\n(.*?)\n---\n", open(sys.argv[1]).read(), re.S).group(1)
keys = re.findall(r"^  (environment_class|commit_attribution|deliverable_language|comment_language):", fm, re.M)
assert keys == ["environment_class", "commit_attribution", "deliverable_language", "comment_language"], keys
assert re.search(r"^  comment_language: <bcp47>$", fm, re.M), fm
PY
  rm -rf "$D"
}

SELF="$ROOT/tests/test-full-install.sh"

# Re-invoke self to run ONE scenario (a child bash spawned by gate_pool).
if [ "${1:-}" = "__case" ]; then
  shift
  "$@"
  exit $?
fi

main() {
  local c h rc=0
  PLANT_CACHE="$(mktemp -d)"; export PLANT_CACHE
  SCN="$(mktemp)"; BTMP="$(mktemp -d)"
  trap 'rm -rf "$PLANT_CACHE" "$SCN" "$BTMP"' EXIT
  # Shared bases, built once before the pool so concurrent cases only copy them.
  for h in $EVERY_HOST all; do plant_base "$h" --copy; done
  for c in \
    case_claude_code case_plant_facts_flags case_opencode case_codex \
    case_claude_code_ampersand_path case_github_copilot case_prime_agent \
    case_graft_stale_kernel case_glob_metachar case_no_symlink_churn \
    case_universal_router case_copilot_projection_tools case_seed_stamp \
    caseALL_EXCLUDES_LEGACY_HOSTS case_pre_growth_pointer case_code_anchor_tool \
    case_plant_facts_index_no_fm case_plant_facts_declared case_plant_facts_partial; do
    printf '%s\t%s\n' "$c" "bash \"$SELF\" __case $c" >> "$SCN"
  done
  python3 "$ROOT/tests/gate_pool.py" run "$SCN" || rc=$?

  # Serial tail: interpreter bytecode under templates/ never reaches a plant.
  # It writes a fixture into the seed, so it runs alone after the pool.
  mkdir -p "$ROOT/templates/knowledge-graph/__pycache__"
  printf 'fake bytecode\n' > "$ROOT/templates/knowledge-graph/__pycache__/zz-fixture.cpython-999.pyc"
  bash "$ROOT/install.sh" claude-code --project-dir "$BTMP" >/dev/null 2>&1 || rc=1
  rm -f "$ROOT/templates/knowledge-graph/__pycache__/zz-fixture.cpython-999.pyc"
  local found; found="$(find "$BTMP" \( -name '*.pyc' -o -name '__pycache__' \) | wc -l | tr -d ' ')"
  [[ "$found" == "0" ]] || { echo "test-full-install: FAIL: $found bytecode path(s) placed into the plant" >&2; rc=1; }

  [ "$rc" -eq 0 ] || { echo "test-full-install: FAIL" >&2; exit "$rc"; }
  printf 'full install contract: PASS\n'
}

main
