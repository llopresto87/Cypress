#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(mktemp -d)"
trap 'rm -rf "$TARGET"' EXIT

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

printf 'unified graph install: PASS\n'
