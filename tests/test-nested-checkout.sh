#!/usr/bin/env bash
# A plant checked out inside another checkout must never read the ancestor's
# artifacts. Three shipped scripts resolve a plant artifact by walking UP from
# the cwd and from their own location: route-hook's linter, status-hook's
# register, agent-lint's roster. Bounding one of the three closed the instance
# and left the class — from a git repo at `outer/sub/child` with no roster of
# its own, `agent-lint.py --route` returned the ANCESTOR repository's agent at
# HIGH confidence, score 36, and `--lint` printed `OK` over that foreign roster.
#
# `seed-lint`'s canonical-block check holds the boundary byte-identical across
# the three. That catches drift and cannot catch a wrong rule copied three
# times, so this asserts the BEHAVIOUR, in both directions:
#   (1) the ancestor's artifact is NOT selected from a nested plant, and
#   (2) the plant's own artifact, at its own repo root, still IS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fails=0
fail() { echo "FAIL: $*" >&2; fails=$((fails + 1)); }

# --- the fixture: an ancestor repo that owns artifacts, a nested plant that does not
mkdir -p "$WORK/outer/docs/graph/agents" "$WORK/outer/tools"
git -C "$WORK/outer" init -q .
cat > "$WORK/outer/docs/graph/agents/99-ancestor.md" <<'AGENT'
---
name: ancestor-owned
description: An agent belonging to a repository the plant does not own.
routing_triggers:
  - "anything at all please"
model: opus
tools: [Read]
can_delegate: false
prevents: nothing
---
body
AGENT
printf 'print("ANCESTOR REGISTER RAN")\n' > "$WORK/outer/docs/graph/status-register.py"
printf 'print("ANCESTOR LINT RAN")\n' > "$WORK/outer/docs/graph/graph-lint.py"

mkdir -p "$WORK/outer/sub/child/.claude"
git -C "$WORK/outer/sub/child" init -q .
for f in agent-lint.py status-hook.py route-hook.py frontmatter.py; do
  cp "$ROOT/integrations/claude-code/$f" "$WORK/outer/sub/child/.claude/$f"
done

# --- (1) the ancestor must be unreachable from the nested plant
cd "$WORK/outer/sub/child"

if out=$(python3 .claude/agent-lint.py --route "anything at all please" 2>&1); then
  if grep -q "ancestor-owned" <<<"$out"; then
    fail "agent-lint --route resolved the ANCESTOR repository's roster"
  fi
fi
if out=$(python3 .claude/agent-lint.py --lint 2>&1); then
  fail "agent-lint --lint reported on a roster the plant does not own: $out"
fi

for probe in "status-hook.py:find_register" "route-hook.py:find_lint"; do
  script="${probe%%:*}"; fn="${probe##*:}"
  found=$(python3 - "$script" "$fn" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("probe", f".claude/{sys.argv[1]}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
got = getattr(mod, sys.argv[2])()
print(got[0] if isinstance(got, tuple) else got)
PY
)
  if [[ "$found" != "None" ]]; then
    fail "$script:$fn crossed the .git boundary and selected $found"
  fi
done

# --- (2) the plant's OWN artifact, at its own repo root, must still be found
mkdir -p docs/graph/agents
cp "$ROOT/agents/03-reviewer.md" docs/graph/agents/
printf 'print("PLANT REGISTER")\n' > docs/graph/status-register.py
mkdir -p deep/nested/dir
cd deep/nested/dir
found=$(python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location("probe", "../../../.claude/status-hook.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(mod.find_register()[0])
PY
)
if [[ "$found" == "None" ]]; then
  fail "the boundary also denied the plant its OWN status-register.py — the \
walk must stop AT the root, not before it"
fi
# --lint exits non-zero here (the lone roster has unresolved peers), which is
# not what is under test: what matters is that it READ the plant's own roster.
lint_out=$(python3 ../../../.claude/agent-lint.py --lint 2>&1 || true)
if ! grep -q "03-reviewer" <<<"$lint_out"; then
  fail "the boundary denied the plant its own roster at its own repo root: $lint_out"
fi

if (( fails )); then
  echo "nested-checkout: FAIL — $fails finding(s)" >&2
  exit 1
fi
echo "nested-checkout: OK — the ancestor is denied, the plant's own root is found"
