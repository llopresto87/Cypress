#!/usr/bin/env bash
# test-delivery-rules.sh — SPEC-0005 MUST_REACH_RULE_IS_IN_EACH_NAMED_ROLE_PROMPT,
# FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT, FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE
# and COMPOSER_SELECTS_A_SECTION_BY_SLUG: a rule that must reach a role is in
# that role's loaded prompt after an install, a retired sentence is in none,
# a prompt that breaks either is named by role, and install.sh --check says so
# in a plant.
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
for role in 01-architect 03-reviewer 04-tester; do
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

# X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: the opencode projection names
# each agent file by its callable name (tester.md, not 04-tester.md); one table
# finds the role in either directory, and install.sh opencode --check runs it.
mkdir "$T/oc"; bash "$ROOT/install.sh" opencode --project-dir "$T/oc" >/dev/null 2>&1
out="$("$PY" "$ROOT/tools/delivery_rules.py" "$T/oc/.opencode/agents" 2>&1)" \
  || fail "X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: installed opencode prompts read as lacking the rule ($out)"
out="$(bash "$ROOT/install.sh" opencode --check --project-dir "$T/oc" 2>&1)" \
  || fail "X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: --check failed a fresh opencode plant ($out)"
grep -q "opencode agents carry every must-reach rule" <<<"$out" \
  || fail "X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: --check does not say it read the must-reach rules ($out)"
"$PY" - "$T/oc/.opencode/agents/tester.md" <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
assert "Nothing to get wrong, no new test." in s
open(p, "w").write(s.replace("Nothing to get wrong, no new test.", ""))
PYEOF
out="$(bash "$ROOT/install.sh" opencode --check --project-dir "$T/oc" 2>&1)" \
  && fail "X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: --check passed an opencode tester without the rule"
grep -q "the loaded prompt of tester lacks rule test-first.proportionate-checks" <<<"$out" \
  || fail "X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: --check does not name the opencode tester ($out)"
! grep -q "of architect lacks\|of reviewer lacks" <<<"$out" \
  || fail "X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: roles that carry the rule were named ($out)"
echo "  X662 OPENCODE_CHECK_HOLDS_THE_MUST_REACH_RULES: opencode agents are read by callable name; --check names the role that lacks the rule — OK"

# X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: FORBIDDEN holds the retired
# sentences of the rule before 8.5.0; a fresh install's prompts (claude-code and
# opencode) carry none; one restored sentence is named by role and sentence, by
# the tool and by install.sh <host> --check.
"$PY" - "$ROOT" <<'PYEOF' || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: the table lacks a retired sentence"
import sys
sys.path.insert(0, sys.argv[1] + "/tools")
import delivery_rules as d
have = {s for s, _why, _roles in d.FORBIDDEN}
for want in ("is written only when a failing test asks for it", "the test name names the contract",
             "writes only production files", "the rule loaded above", "every increment begins with"):
    assert want in have, want
for s, why, roles in d.FORBIDDEN:
    assert why.strip() and (roles == "any" or (roles and all(isinstance(r, str) for r in roles))), s
PYEOF
mkdir "$T/ocf"; bash "$ROOT/install.sh" opencode --project-dir "$T/ocf" >/dev/null 2>&1
out="$("$PY" "$ROOT/tools/delivery_rules.py" "$T/ocf/.opencode/agents" 2>&1)" \
  || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: a fresh opencode install carries a retired sentence ($out)"
mkdir "$T/plant2"; ( cd "$T/plant2" && git init -q && bash "$ROOT/install.sh" claude-code >/dev/null 2>&1 )
out="$("$PY" "$ROOT/tools/delivery_rules.py" "$T/plant2/.claude/agents" 2>&1)" \
  || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: a fresh install carries a retired sentence ($out)"
restore() {  # $1 file: put one retired sentence back, wrapped across a line as a node holds it
  "$PY" - "$1" <<'PYEOF'
import sys
p = sys.argv[1]
try:
    s = open(p).read()
except FileNotFoundError:
    s = ""
open(p, "w").write(s + "\nProduction code is written only when a failing test\nasks for it.\n")
PYEOF
}
cp -R "$T/plant2/.claude/agents" "$T/agents-forbidden"; restore "$T/agents-forbidden/03-reviewer.md"
out="$("$PY" "$ROOT/tools/delivery_rules.py" "$T/agents-forbidden" 2>&1)" \
  && fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: a restored retired sentence passed"
grep -q "of reviewer carries the retired sentence 'is written only when a failing test asks for it'" <<<"$out" \
  || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: role or sentence not named ($out)"
! grep -q "of tester\|of architect" <<<"$out" \
  || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: a clean role was named ($out)"
restore "$T/plant2/.claude/agents/03-reviewer.md"
out="$(cd "$T/plant2" && bash "$ROOT/install.sh" claude-code --check 2>&1)" \
  && fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: claude-code --check passed a retired sentence"
grep -q "of reviewer carries the retired sentence" <<<"$out" \
  || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: claude-code --check silent ($out)"
restore "$T/ocf/.opencode/agents/tester.md"
out="$(bash "$ROOT/install.sh" opencode --check --project-dir "$T/ocf" 2>&1)" \
  && fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: opencode --check passed a retired sentence"
grep -q "of tester carries the retired sentence" <<<"$out" \
  || fail "X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: opencode --check does not name the tester ($out)"
echo "  X910 FORBIDDEN_SENTENCE_IS_IN_NO_COMPOSED_PROMPT: fresh prompts carry no retired sentence; a restored one is named by role, in the tool and both --check runs — OK"

# X911 FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE: the seed's method surface
# (agents/, protocols/, skills/, core/, templates/) holds no retired sentence,
# so a node no role composes today cannot carry one into the next composition.
out="$("$PY" "$ROOT/tools/delivery_rules.py" --tree "$ROOT" 2>&1)" \
  || fail "X911 FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE: ($out)"
mkdir -p "$T/tree/core/method"; restore "$T/tree/core/method/x.md"
out="$("$PY" "$ROOT/tools/delivery_rules.py" --tree "$T/tree" 2>&1)" \
  && fail "X911 FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE: a retired sentence in a node passed"
grep -q "core/method/x.md: carries the retired sentence 'is written only when a failing test asks for it'" <<<"$out" \
  || fail "X911 FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE: file or sentence not named ($out)"
echo "  X911 FORBIDDEN_SENTENCE_IS_IN_NO_METHOD_SOURCE: the method surface holds no retired sentence; a planted one is named by file — OK"

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
