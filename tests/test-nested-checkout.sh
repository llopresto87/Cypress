#!/usr/bin/env bash
# A plant checked out inside another checkout must never read the ancestor's
# artifacts. route-hook's linter, status-hook's register and agent-lint's
# roster each walk UP to find a plant artifact. seed-lint holds the three
# boundary blocks byte-identical; this asserts the behaviour, both ways:
#   (1) the ancestor's artifact is NOT selected from a nested plant, and
#   (2) the plant's own artifact, at its own repo root, still IS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Resolved, so every path compared below is the same spelling.
WORK="$(cd "$(mktemp -d)" && pwd -P)"
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

# status-hook.py now loads its sibling route-hook.py for the SPEC-0003 ledger
# reset (STATUS_HOOK_RESET_OWNS_NO_PATH_RULE), so its reach is route-hook's: the
# reset must land in the NESTED plant's own `.cypress/session/`, never in the
# ancestor's. Identical ledgers in both; only the plant's may change.
printf 'print("task: x")\n' > "$WORK/outer/sub/child/docs/graph/graph-lint.py"
sid="nested-checkout-session"
for d in "$WORK/outer" "$WORK/outer/sub/child"; do
  mkdir -p "$d/.cypress/session"
  chmod 700 "$d/.cypress/session"
  printf '*\n' > "$d/.cypress/session/.gitignore"
  printf '{"version": 1, "session_id": "%s", "prompt_count": 3, "surfaced": ["root"], "peers_seen": [], "last_reset": null}' \
    "$sid" > "$d/.cypress/session/$sid.json"
  chmod 600 "$d/.cypress/session/$sid.json"
done
ancestor_before=$(cat "$WORK/outer/.cypress/session/$sid.json")
printf '{"hook_event_name": "SessionStart", "session_id": "%s", "source": "startup"}' "$sid" \
  | python3 ../../../.claude/status-hook.py >/dev/null 2>&1 || true
if [[ "$(cat "$WORK/outer/.cypress/session/$sid.json")" != "$ancestor_before" ]]; then
  fail "status-hook's sibling reset crossed the .git boundary into the ANCESTOR's ledger"
fi
if ! python3 - "$WORK/outer/sub/child/.cypress/session/$sid.json" <<'PY'
import json, sys
sys.exit(0 if json.load(open(sys.argv[1])).get("prompt_count") == 0 else 1)
PY
then
  fail "status-hook's sibling load did not resolve inside the plant: the nested plant's ledger was not reset"
fi

# ===========================================================================
# The fourth upward walk: tests/test_agent_lint.py's roster lookup. Its
# default is <seed>/agents whatever sits above the seed; a host projection
# with an extra agent must not leak in, and the seed gate's verdict must not
# depend on where the seed is checked out.
# ===========================================================================
RWORK="$WORK/roster"
mkdir -p "$RWORK"

mk_seedlet() {
  local s="$1"
  mkdir -p "$s/tests" "$s/integrations/claude-code"
  cp -a "$ROOT/agents" "$s/agents"
  cp "$ROOT/tests/test_agent_lint.py" "$s/tests/"
  cp "$ROOT/integrations/claude-code/"*.py "$s/integrations/claude-code/"
}

# A host plant with the seed nested at Cypress/; its .claude/agents projects
# the seed roster plus, unless $2 is "none", one agent the seed lacks.
mk_host() {
  local h="$1" extra="${2:-plant-only-agent}"
  mkdir -p "$h/.claude/agents"
  cp -a "$ROOT/agents/." "$h/.claude/agents/"
  if [[ "$extra" != "none" ]]; then
    cat > "$h/.claude/agents/$extra.md" <<AGENT
---
name: $extra
description: An agent this plant authored that the seed's roster does not hold.
---
body
AGENT
  fi
  mk_seedlet "$h/Cypress"
}

# Import the suite in the fixture; print the roster it resolved and its names.
roster_probe() {
  CYPRESS_ROSTER_DIR="${2:-}" python3 - "$1" <<'PY' 2>&1 || true
import importlib.util, sys
spec = importlib.util.spec_from_file_location("t", sys.argv[1] + "/tests/test_agent_lint.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("ROSTER=" + str(mod.ROSTER))
print("NAMES=" + ",".join(sorted(mod.ALL_AGENTS)))
PY
}

caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED() {
  local h="$RWORK/default" t="$RWORK/twin" e="$RWORK/elsewhere/agents" out
  mk_host "$h"
  out="$(roster_probe "$h/Cypress")"
  grep -qxF "ROSTER=$h/Cypress/agents" <<<"$out" \
    || fail "the suite's default roster is not the seed's own agents/: $out"
  if grep -q "^NAMES=.*plant-only-agent" <<<"$out"; then
    fail "the derived agent-name set holds an agent absent from <seed>/agents/"
  fi
  # A byte-identical host projection must not displace it either.
  mk_host "$t" none
  out="$(roster_probe "$t/Cypress")"
  grep -qxF "ROSTER=$t/Cypress/agents" <<<"$out" \
    || fail "a byte-identical host projection displaced the seed's own roster: $out"
  # CYPRESS_ROSTER_DIR (DOCUMENTATION.md) names a third directory, used verbatim.
  mkdir -p "$e"
  printf -- '---\nname: elsewhere-only\ndescription: x\n---\nbody\n' > "$e/00-elsewhere.md"
  out="$(roster_probe "$h/Cypress" "$e")"
  grep -qxF "ROSTER=$e" <<<"$out" && grep -qxF "NAMES=elsewhere-only" <<<"$out" \
    || fail "CYPRESS_ROSTER_DIR was not honoured verbatim: $out"
}

# The suite's verdict nested in a plant equals its verdict standing alone.
caseROSTER_NESTED_SEED_GATE_MATCHES_A_STANDALONE_COPY() {
  local h="$RWORK/default" s="$RWORK/solo" nrc=0 src=0 nout sout
  mkdir -p "$s"; mk_seedlet "$s/Cypress"
  nout="$(cd "$h/Cypress" && python3 tests/test_agent_lint.py GoldenCorpusTests 2>&1)" || nrc=$?
  sout="$(cd "$s/Cypress" && python3 tests/test_agent_lint.py GoldenCorpusTests 2>&1)" || src=$?
  [[ "$nrc" == "$src" ]] \
    || fail "the nested run exited $nrc where the standalone control exited $src"
  if grep -q "plant-only-agent" <<<"$nout$sout"; then
    fail "an assertion named an agent absent from <seed>/agents/"
  fi
}

caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED
caseROSTER_NESTED_SEED_GATE_MATCHES_A_STANDALONE_COPY

if (( fails )); then
  echo "nested-checkout: FAIL — $fails finding(s)" >&2
  exit 1
fi
echo "nested-checkout: OK — the ancestor is denied, the plant's own root is found"
