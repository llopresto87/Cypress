#!/usr/bin/env bash
# graph-lint artifacts-edge contract. Installs a plant into a temp dir, drops
# in fixtures/root.md (whose `artifacts:` names architecture/README.md), and
# asserts the linter PASSES while that file exists and FAILS once it is moved
# away. Nothing here asserts anything about token budgets: the fixture's
# `est_tokens` is an INPUT, chosen so the first run is clean and the second
# run's non-zero exit is attributable to the artifacts edge alone. It was
# raised from 10 to the whole-file measure when graph-lint's budget metric
# moved from body-only to frontmatter+body under
# SPEC-0001-gate-assertion-floor (GRAPH_LINT_BUDGET_COUNTS_FRONTMATTER).
# Re-measure, do not guess, and never relax the 2x band to make a fixture fit.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(mktemp -d)"
trap 'rm -rf "$TARGET"' EXIT

"$ROOT/install.sh" codex --project-dir "$TARGET" --copy --force >/dev/null

cp "$ROOT/tests/fixtures/root.md" "$TARGET/docs/graph/nodes/root.md"

python3 "$TARGET/docs/graph/graph-lint.py" >/dev/null
mv "$TARGET/docs/graph/architecture/README.md" "$TARGET/docs/graph/architecture/README.hidden"
if python3 "$TARGET/docs/graph/graph-lint.py" >/dev/null 2>&1; then
  printf 'graph linter accepted a broken artifacts edge\n' >&2
  exit 1
fi

printf 'graph artifact edge enforcement: PASS\n'
