#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Guard: a grown *application's* knowledge must live under docs/graph/, never a
# bare docs/<collection>/. `decisions` and `plans` are deliberately EXCLUDED
# from this denylist: the seed keeps its own framework ADRs and design plan at
# top-level docs/decisions/ and docs/plans/ — its self-docs, deliberately not
# under docs/graph/ (see docs/decisions/index.md). Those two collection names
# are legitimately bare in the seed, so flagging them here is a false positive.
matches="$(rg -n 'docs/(libraries|sources|specs|runbooks|product|architecture|api|data|evaluations|prompts|best-practices|tools)/' \
  "$ROOT/core" "$ROOT/agents" "$ROOT/protocols" "$ROOT/skills" "$ROOT/templates" "$ROOT/integrations" \
  "$ROOT/docs" "$ROOT/manifest.json" "$ROOT/README.md" "$ROOT/INSTALL.md" "$ROOT/CHANGELOG.md" \
  -g '*.md' -g '*.json' -g '*.py' -g '*.sh' || true)"

if [[ -n "$matches" ]]; then
  printf 'legacy knowledge paths remain outside docs/graph:\n%s\n' "$matches" >&2
  exit 1
fi

printf 'knowledge path consistency: PASS\n'
