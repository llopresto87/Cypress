#!/usr/bin/env bash
# test-delivery-rules.sh — SPEC-0001 MUST_REACH_RULE_IS_IN_EACH_NAMED_ROLE_PROMPT
# and COMPOSER_SELECTS_A_SECTION_BY_SLUG: a rule that must reach a role is in
# that role's loaded prompt after an install, a prompt that lacks it is named
# by role and rule, and install.sh --check says so in a plant.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }
PY=python3

# X524 MUST_REACH_RULE_IS_IN_EACH_NAMED_ROLE_PROMPT: installed prompts carry the rule
mkdir "$T/plant"; ( cd "$T/plant" && git init -q && bash "$ROOT/install.sh" claude-code >/dev/null 2>&1 )
"$PY" "$ROOT/tools/delivery_rules.py" "$T/plant/.claude/agents" || fail "installed prompts lack the rule"
echo "  X524 MUST_REACH_RULE_IS_IN_EACH_NAMED_ROLE_PROMPT: installed roles carry the rule — OK"

# the lint names the role and the rule when one prompt lacks it
for role in 01-architect 03-reviewer 04-tester 00-orchestrator; do
  cp -R "$T/plant/.claude/agents" "$T/agents-$role"
  "$PY" - "$T/agents-$role/$role.md" <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
assert "Nothing to get wrong, no new test." in s
open(p, "w").write(s.replace("Nothing to get wrong, no new test.", ""))
PYEOF
  out="$("$PY" "$ROOT/tools/delivery_rules.py" "$T/agents-$role" 2>&1)" && fail "$role: lint passed without the rule"
  grep -q "test-first.proportionate-checks" <<<"$out" || fail "$role: rule not named ($out)"
  grep -q "${role#*-}" <<<"$out" || fail "$role: role not named ($out)"
done
echo "  a prompt without the rule fails naming role and rule — OK"

# a plant check reports it
cp -R "$T/agents-04-tester/." "$T/plant/.claude/agents/"
out="$(cd "$T/plant" && bash "$ROOT/install.sh" claude-code --check 2>&1)" && rc=0 || rc=$?
grep -q "lacks rule test-first.proportionate-checks" <<<"$out" || fail "--check silent about the gap ($out)"
echo "  install.sh --check reports the missing rule — OK"

# X523 COMPOSER_SELECTS_A_SECTION_BY_SLUG: a slug picks one section, no preamble; an unknown slug is a named error
"$PY" - "$ROOT" <<'PYEOF'
import sys
sys.path.insert(0, sys.argv[1] + "/tools"); sys.path.insert(0, sys.argv[1] + "/templates/knowledge-graph")
from agent_compose import ComposeError, sections
body = "Preamble.\n\n## One (`a.one`)\n\nfirst\n\n## Two (`a.two`)\n\nsecond\n"
home = {"n.x": body}
out = sections({"always_loads": ["n.x#a.two"]}, "t.md", home)[0]
assert "second" in out and "first" not in out and "Preamble" not in out, out
try:
    sections({"always_loads": ["n.x#a.nope"]}, "t.md", home)
except ComposeError as e:
    assert "a.nope" in str(e)
else:
    raise SystemExit("unknown slug accepted")
PYEOF
echo "  X523 COMPOSER_SELECTS_A_SECTION_BY_SLUG: a slug picks one section — OK"
