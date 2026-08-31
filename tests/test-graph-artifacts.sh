#!/usr/bin/env bash
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
