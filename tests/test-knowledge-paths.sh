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
# `specs` is in the PLANT-FACING pattern and deliberately NOT in the seed's own
# — the split below. A protocol or agent that tells a plant to write to a bare
# `docs/specs/` is the violation this guard exists for, and it stays caught. The
# seed itself now keeps two specs of its own at top-level `docs/specs/`
# (SPEC-0001 install-placement, SPEC-0002 routing-contract): kernel §3.1 says
# code without a spec is in remediation mode, the seed has no `docs/graph/` of
# its own to put them under (CLAUDE.md), and they are self-docs in exactly the
# sense `docs/decisions/` and `docs/plans/` already are. So the seed's own
# documents may name them; the machinery it ships may not.
PAT='docs/(libraries|sources|specs|runbooks|product|architecture|api|data|evaluations|prompts|best-practices|tools)/'
SELF_DOC_PAT='docs/(libraries|sources|runbooks|product|architecture|api|data|evaluations|prompts|best-practices|tools)/'
set +e
matches="$(
  # The machinery the seed SHIPS into a plant: full pattern, `specs` included.
  grep -rnE "$PAT" \
    --include='*.md' --include='*.json' --include='*.py' --include='*.sh' \
    "$ROOT/core" "$ROOT/agents" "$ROOT/protocols" "$ROOT/skills" \
    "$ROOT/templates" "$ROOT/integrations"
  rc1=$?; [[ $rc1 -le 1 ]] || exit $rc1
  # The seed's OWN documents: same pattern minus `specs`, which it legitimately
  # keeps at top level. Everything else stays denied here too, so a plan that
  # tells a plant to use a bare `docs/runbooks/` is still caught.
  grep -rnE "$SELF_DOC_PAT" \
    --include='*.md' --include='*.json' --include='*.py' --include='*.sh' \
    "$ROOT/docs"
  rc1b=$?; [[ $rc1b -le 1 ]] || exit $rc1b
  # Plant-facing root files: full pattern.
  grep -nE "$PAT" \
    "$ROOT/manifest.json" "$ROOT/README.md" "$ROOT/INSTALL.md"
  rc2=$?; [[ $rc2 -le 1 ]] || exit $rc2
  # CHANGELOG.md is the seed's own append-only record of itself — the same
  # category as docs/plans and docs/decisions, and it must be able to say that
  # the seed keeps specs of its own. It is also append-only, so an entry that
  # named a collection could never be corrected anyway; denying the word here
  # would only push a true sentence out of the history.
  grep -nE "$SELF_DOC_PAT" "$ROOT/CHANGELOG.md"
  rc2b=$?; [[ $rc2b -le 1 ]] || exit $rc2b
)"
rc=$?
set -e
[[ $rc -eq 0 ]] || { echo "grep itself failed (rc=$rc) — the check did not run" >&2; exit 1; }

if [[ -n "$matches" ]]; then
  printf 'legacy knowledge paths remain outside docs/graph:\n%s\n' "$matches" >&2
  exit 1
fi

printf 'knowledge path consistency: PASS\n'
