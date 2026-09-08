#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

grep -q 'primary, tool-neutral entry point' "$ROOT/INSTALL_PROMPT.md"
grep -q 'Do not perform investigation' "$ROOT/INSTALL_PROMPT.md"
grep -q 'Sonnet-class workers' "$ROOT/INSTALL_PROMPT.md"
grep -q 'Opus-class workers' "$ROOT/INSTALL_PROMPT.md"
grep -q 'canonical workflow' "$ROOT/protocols/grow.md"
grep -q 'simulate a specialist persona' "$ROOT/agents/00-orchestrator.md"
grep -q 'Tier classification' "$ROOT/agents/00-orchestrator.md"
grep -q 'T1 is defined by what it' "$ROOT/core/method/tiers.md"
grep -q 'Classify the tier' "$ROOT/core/AGENTS.md"
grep -q 'graph-session-bootstrap.md' "$ROOT/agents/00-orchestrator.md"
grep -q 'convenience adapter' "$ROOT/protocols/initialize.md"
grep -q 'Every spawned session must execute' "$ROOT/INSTALL_PROMPT.md"
grep -q 'Every spawned session executes' "$ROOT/protocols/grow.md"

# 6.8.0: the single labeled entry runs one flow in three named phases, and the
# growth is bound by grow's completeness contract. Pin both in prose so the
# refactored doctrine cannot silently regress to the old split/skeleton form.
grep -q 'single entry point' "$ROOT/INSTALL_PROMPT.md"
grep -q 'PLACE' "$ROOT/INSTALL_PROMPT.md"
grep -q 'HAND OFF' "$ROOT/INSTALL_PROMPT.md"
grep -q 'GROW IN FULL' "$ROOT/INSTALL_PROMPT.md"
grep -q 'grow.completeness-contract' "$ROOT/INSTALL_PROMPT.md"
grep -q 'The completeness contract' "$ROOT/protocols/grow.md"
grep -q 'grow.completeness-contract' "$ROOT/protocols/grow.md"
# 7.3.0: the completeness contract is mechanical — a tracked coverage record
# and a linter that reads it back, not a prose table the run discarded. Pin the
# artifact, the tool, and the loop, so the contract cannot regress to an
# assertion about itself.
grep -q 'coverage record' "$ROOT/protocols/grow.md"
grep -q '.cypress/coverage.json' "$ROOT/protocols/grow.md"
grep -q 'growth-audit.py' "$ROOT/protocols/grow.md"
grep -q 'growth-audit.py' "$ROOT/protocols/graft.md"
grep -q 'grow.stack-inventory' "$ROOT/protocols/grow.md"
grep -q 'growth-audit.py' "$ROOT/INSTALL_PROMPT.md"
# the intake list is what decides which domains ever get a scout: the two
# specialists added late to the roster must appear in it (6.9.0 ui-ux-designer,
# 6.12.0 legal), or plants keep arriving with those agents and nothing to read.
grep -q 'design surface' "$ROOT/protocols/grow.md"
grep -q 'regulatory exposure' "$ROOT/protocols/grow.md"
grep -q 'plant_knowledge' "$ROOT/agents/13-ui-ux-designer.md"
grep -q 'plant_knowledge' "$ROOT/agents/14-legal.md"
grep -q 'graph-lint.py --plan' "$ROOT/templates/prompts/investigation-brief.md"
grep -q 'graph-lint.py --plan' "$ROOT/templates/prompts/node-authoring-brief.md"
grep -q 'must run inside every spawned worker' "$ROOT/skills/context-router/SKILL.md"

# grep, not rg: ripgrep is undocumented here, and a missing rg (exit 127) was
# indistinguishable from "no match" — this guard silently stopped guarding.
set +e
sim="$(grep -rnE 'adopt(s|ing)? (the )?(specialist|persona)|one agent adopts each persona' \
  "$ROOT/core" "$ROOT/agents" "$ROOT/protocols")"
rc=$?
set -e
[[ $rc -le 1 ]] || { echo "grep itself failed (rc=$rc) — the check did not run" >&2; exit 1; }
if [[ $rc -eq 0 ]]; then
  printf 'orchestration chat still permits persona simulation:\n%s\n' "$sim" >&2
  exit 1
fi

printf 'orchestration entry and model policy: PASS\n'
