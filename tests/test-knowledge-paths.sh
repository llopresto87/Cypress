#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Guard: a grown *application's* knowledge must live under docs/graph/, never a
# bare docs/<collection>/. `decisions` and `plans` are deliberately EXCLUDED
# from this denylist: the seed keeps its own framework ADRs and design plan at
# top-level docs/decisions/ and docs/plans/ — its self-docs, deliberately not
# under docs/graph/ (see docs/decisions/index.md). Those two collection names
# are legitimately bare in the seed, so flagging them here is a false positive.
# grep, not rg: ripgrep is not a documented dependency of this repo, and the
# old `rg ... || true` turned "rg is not installed" (exit 127) into the same
# empty string as "no match" — the suite went green without checking anything.
# grep is POSIX; rc 0/1 = match/no-match, anything else is a real error.
PAT='docs/(libraries|sources|specs|runbooks|product|architecture|api|data|evaluations|prompts|best-practices|tools)/'
set +e
matches="$(
  grep -rnE "$PAT" \
    --include='*.md' --include='*.json' --include='*.py' --include='*.sh' \
    "$ROOT/core" "$ROOT/agents" "$ROOT/protocols" "$ROOT/skills" \
    "$ROOT/templates" "$ROOT/integrations" "$ROOT/docs"
  rc1=$?; [[ $rc1 -le 1 ]] || exit $rc1
  grep -nE "$PAT" \
    "$ROOT/manifest.json" "$ROOT/README.md" "$ROOT/INSTALL.md" "$ROOT/CHANGELOG.md"
  rc2=$?; [[ $rc2 -le 1 ]] || exit $rc2
)"
rc=$?
set -e
[[ $rc -eq 0 ]] || { echo "grep itself failed (rc=$rc) — the check did not run" >&2; exit 1; }

if [[ -n "$matches" ]]; then
  printf 'legacy knowledge paths remain outside docs/graph:\n%s\n' "$matches" >&2
  exit 1
fi

printf 'knowledge path consistency: PASS\n'
