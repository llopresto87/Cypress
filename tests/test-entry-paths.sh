#!/usr/bin/env bash
# Every way into the seed reaches the protocol that fits the repository.
#
# `protocols/from-scratch.md` is a complete nine-phase new-project procedure
# that, at d7588e2, nothing routed to: the kernel never named it, install.sh
# told every target — empty or not — to run /initialize, and /initialize
# forwarded unconditionally to `grow`, the protocol for the opposite case.
#
# WHY THIS SUITE INSTALLS A PLANT INSTEAD OF GREPPING.
# Its first version was entirely substring presence/absence over the source
# files, and an adversarial pass restored ALL FOUR original regressions while
# it stayed green: a comma defeated one literal ("discover the project, and
# grow"), dropped backticks defeated another, a parenthetical "(Historical
# note: an earlier draft named from-scratch here.)" satisfied the kernel
# check, and `initialize`'s entire fork body was replaced with "Forward
# unconditionally to protocol.grow" without either this suite or seed-lint
# noticing — the frontmatter alone carried every assertion.
#
# A grep cannot tell a rule from a disclaimer that quotes it. So the
# load-bearing checks below install a real plant and ask the plant's own
# router where a task goes. A node that says the right words but does not
# route is caught; a node that routes correctly cannot be faked by prose.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fails=0
fail() { echo "  FAIL: $*"; fails=$((fails + 1)); }

# -- structural: the absorbed skill is gone and nothing points at it ---------
#    (a dangling edge is a resolution failure, not a wording question)
if [[ -e "$ROOT/skills/from-scratch-bootstrap" ]]; then
  fail "skills/from-scratch-bootstrap still exists — slice 1 absorbs it into from-scratch"
fi
# every extension that can carry a live pointer, including install INPUT such
# as .toml.example — an earlier --include list omitted it and a deleted skill
# shipped in the Codex config snippet for a whole release.
refs="$(grep -rl "from-scratch-bootstrap" "$ROOT" \
          --include='*.md' --include='*.json' --include='*.sh' --include='*.py' \
          --include='*.toml' --include='*.example' --include='*.yml' \
          --include='*.yaml' --include='*.ts' --include='*.toml.example' \
          2>/dev/null | grep -v '/docs/plans/' | grep -v '/CHANGELOG.md' \
                      | grep -v 'test-entry-paths.sh' || true)"
if [[ -n "$refs" ]]; then
  fail "from-scratch-bootstrap is still referenced by:"$'\n'"$(echo "$refs" | sed 's/^/          /')"
fi

# -- structural: the absorbed discipline survived the fold ------------------
fs="$ROOT/protocols/from-scratch.md"
grep -q "from-scratch.entry" "$fs" \
  || fail "from-scratch.md does not own 'from-scratch.entry' (the absorbed skill's fact)"
for phrase in "clean checkout" "never memory" "actually loads"; do
  grep -qi "$phrase" "$fs" \
    || fail "from-scratch.md lost the absorbed honesty rule matching: $phrase"
done
# ...and was not merely re-added inside a comment saying it was dropped
if grep -qiE "<!--|was dropped|an earlier draft" "$fs"; then
  fail "from-scratch.md carries a disclaimer or commented-out block where a rule should be"
fi

# -- structural: the fork BODY exists, not just its frontmatter -------------
init="$ROOT/protocols/initialize.md"
body="$(sed -n '/^---$/,$p' "$init" | sed -n '/^# /,$p')"
for banned in "forward unconditionally" "delegates unchanged to .protocol.grow" "an earlier draft"; do
  if echo "$body" | grep -qiE "$banned"; then
    fail "initialize.md body says '$banned' — the fork was removed and the frontmatter left behind"
  fi
done
echo "$body" | grep -q "from-scratch" || fail "initialize.md body never names the from-scratch arm"
echo "$body" | grep -q "grow"         || fail "initialize.md body never names the grow arm"
echo "$body" | grep -qi "executable project evidence" \
  || fail "initialize.md body states no test for choosing an arm"
# The fork is a two-row table and each arm must name ITS OWN destination in
# its own row. Asserting that both protocol names appear somewhere in the body
# was invertible: swapping the two destinations, or adding a sentence saying
# the fork does not apply, left every token in place. A table cell cannot be
# negated by prose elsewhere.
present_row="$(echo "$body" | grep -E '^\| \*\*present\*\*' || true)"
absent_row="$(echo "$body" | grep -E '^\| \*\*absent\*\*' || true)"
[[ -n "$present_row" ]] || fail "initialize.md fork table has no **present** arm row"
[[ -n "$absent_row"  ]] || fail "initialize.md fork table has no **absent** arm row"
grep -q 'protocol\.grow' <<<"$present_row" \
  || fail "initialize.md: the evidence-PRESENT arm does not route to protocol.grow — got: $present_row"
grep -q 'protocol\.from-scratch' <<<"$absent_row" \
  || fail "initialize.md: the evidence-ABSENT arm does not route to protocol.from-scratch — got: $absent_row"
grep -q 'protocol\.from-scratch' <<<"$present_row" \
  && fail "initialize.md: the PRESENT arm names from-scratch — the arms are swapped or merged"
grep -q 'protocol\.grow' <<<"$absent_row" \
  && fail "initialize.md: the ABSENT arm names grow — the arms are swapped or merged"

# -- structural: no SURFACE may call initialize a mere adapter -------------
# The fork landed in protocols/initialize.md, core/AGENTS.md, install.sh:770 and
# protocols/grow.md, and those four are asserted above. It did NOT land in eight
# other views of the same fact, and each kept saying "/initialize is only a tool
# adapter" — including integrations/claude-code/route-hook.py and the Prime Agent
# twin, which emit that sentence EXACTLY when docs/graph/ is absent. That is the
# empty-repo case: the one moment the from-scratch arm exists for, and the
# message sent there named only grow.
#
# The assertion is co-occurrence on a single LINE, which is what survives
# rewording: any surface allowed to describe /initialize as an adapter must say
# in the same breath what it forks to. A banned-phrase list would not — there
# are unbounded ways to write "only an adapter".
adapter_sites=(
  "$ROOT/manifest.json"
  "$ROOT/DOCUMENTATION.md"
  "$ROOT/INSTALL.md"
  "$ROOT/core/AGENTS.md"
  "$ROOT/install.sh"
  "$ROOT/templates/knowledge-graph/index.md"
  "$ROOT/integrations/claude-code/route-hook.py"
  "$ROOT/integrations/prime-agent/route-extension.ts"
  "$ROOT/documentation/protocols-reference.md"
)
bare_adapter=0
for f in "${adapter_sites[@]}"; do
  [[ -f "$f" ]] || fail "entry-fork sweep names $f, which does not exist — the list is stale"
  # Every line calling initialize an adapter, that does not also name the fork.
  while IFS= read -r hit; do
    lineno="${hit%%:*}"
    text="${hit#*:}"
    grep -qiE 'from-scratch|entry fork|forks? to' <<<"$text" && continue
    # the two arms may legitimately sit on the following line in wrapped prose
    nxt="$(sed -n "$((lineno + 1))p" "$f")"
    grep -qiE 'from-scratch|entry fork|forks? to' <<<"$nxt" && continue
    echo "  $f:$lineno: $text" >&2
    bare_adapter=$((bare_adapter + 1))
  done < <(grep -niE '(tool|coding-tool) adapter' "$f" || true)
done
if [[ $bare_adapter -gt 0 ]]; then
  fail "$bare_adapter surface(s) call /initialize an adapter without naming the fork it carries — the fix landed in one view and not the others"
fi

# -- structural: the kernel names the second entry protocol ----------------
kline="$(grep -n 'from-scratch' "$ROOT/core/AGENTS.md" || true)"
[[ -n "$kline" ]] \
  || fail "core/AGENTS.md never names from-scratch — a session cannot route to a protocol it is not told exists"
if grep -qiE "historical note|an earlier draft" "$ROOT/core/AGENTS.md"; then
  fail "core/AGENTS.md mentions from-scratch only in a historical aside"
fi
# and it must name it as a DESTINATION, not as something unreachable
if grep -qiE 'from-scratch[^\n]*(is unreachable|not entered|never entered|no longer)' "$ROOT/core/AGENTS.md"; then
  fail "core/AGENTS.md names from-scratch only to say it is not reachable"
fi
grep -qE 'from-scratch.{0,40}empty|empty.{0,40}from-scratch' "$ROOT/core/AGENTS.md" \
  || fail "core/AGENTS.md does not tie from-scratch to the empty-repository case — naming it is not routing to it"

# -- structural: the installer's post-install line names BOTH arms ---------
#    (asserting the absence of one phrasing is defeated by a comma; assert the
#     presence of what must be there instead)
# Assert the MAPPING, not the presence of two words. "every target, empty or
# not, goes to protocol.grow; protocol.from-scratch is not entered from here"
# names both arms and inverts the fork — it passed a presence check.
post="$(grep -A4 'run /initialize' "$ROOT/install.sh" || true)"
empty_line="$(echo "$post" | grep -i 'empty' || true)"
[[ -n "$empty_line" ]] || fail "install.sh's post-install line does not mention the empty-repo case"
if [[ -n "$empty_line" ]]; then
  grep -q 'from-scratch' <<<"$empty_line" \
    || fail "install.sh: the line naming the EMPTY case does not send it to from-scratch — got: $empty_line"
  grep -qE 'empty[^\n]*->[^\n]*grow|empty[^\n]*goes to[^\n]*grow' <<<"$empty_line" \
    && fail "install.sh: the EMPTY case is routed to grow — the fork is inverted"
fi
echo "$post" | grep -q "source present\|protocol.grow" || fail "install.sh's post-install line never names the grow arm"

# -- structural: grow hands off rather than expecting a return -------------
# from-scratch ends at `deliver`; nothing that calls it gets control back.
# The concept, not one phrasing: 'as a sub-step and come back to Phase 2'
# evaded a check banning 'route through ... for' and 'then return here'.
if grep -qiE 'from-scratch[^.]{0,80}(sub-step|subroutine|come back|comes back|returns here|return here|and resume|then resume)' "$ROOT/protocols/grow.md"; then
  fail "grow.md treats from-scratch as a sub-step that returns — it is a whole workflow ending at deliver"
fi
grep -qiE 'hand off to|do not resume here' "$ROOT/protocols/grow.md" \
  || fail "grow.md no longer states that it hands off to from-scratch without resuming"

# -- BEHAVIOURAL: a real plant's router reaches both arms ------------------
# This is the half a grep cannot fake. Install, then ask the installed router.
PLANT="$WORK/plant"
mkdir -p "$PLANT"
if ! "$ROOT/install.sh" claude-code --project-dir "$PLANT" >/dev/null 2>&1; then
  fail "install.sh failed; cannot verify routing"
else
  # Parse ONLY the LOAD block. The --plan output also prints a "NOT LOADED
  # (peer of ...)" section, and grepping the whole thing was a false green:
  # an adversarial pass replaced from-scratch's load_when triggers with
  # unrelated phrasings, so the router selected only `protocol.initialize` and
  # listed from-scratch as a mere peer — restoring the exact d7588e2 regression
  # (a nine-phase protocol nothing routes to) while this suite reported OK.
  # A node the router SELECTED is the property; a node it merely names is not.
  selected() {
    (cd "$PLANT" && python3 docs/graph/graph-lint.py --plan "$1" 2>/dev/null) \
      | awk '/^LOAD \(/{inblock=1; next} /^NOT LOADED/{inblock=0} inblock && /^  [a-z]+\./{print $1}'
  }
  assert_routes() {  # assert_routes "<task>" <node-id> <label>
    local got; got="$(selected "$1")"
    if [[ -z "$got" ]]; then
      fail "routing [$3]: '$1' selected NO nodes — the LOAD block did not parse"
    elif ! grep -qx "$2" <<<"$got"; then
      fail "routing [$3]: '$1' does not SELECT $2 (selected: $(tr '\n' ' ' <<<"$got"))"
    fi
  }
  assert_routes "start a new project from nothing, the repo is empty" \
                "protocol.from-scratch" "empty repo -> from-scratch"
  assert_routes "just installed the seed, which protocol do I enter" \
                "protocol.initialize" "entry question -> the fork"
  assert_routes "mkdir a new project and cd into it" \
                "protocol.from-scratch" "the mkdir entry point"
  assert_routes "adopt this existing codebase into the graph by subsystem" \
                "protocol.grow" "existing source -> grow"
  # the retired nodes must not be installed
  for gone in "protocols/toolcraft.md" "skills/from-scratch-bootstrap.md"; do
    [[ -e "$PLANT/docs/graph/$gone" ]] && fail "retired node still installed: $gone"
  done
  # the plant's own graph must lint clean with the new node set
  (cd "$PLANT" && python3 docs/graph/graph-lint.py >/dev/null 2>&1) \
    || fail "the installed plant's graph does not lint clean"
fi

# -- the kernel edits fit ---------------------------------------------------
# The budget is READ from its one home, not repeated here. This was a bare
# `8000` whose own failure message called it KERNEL_BUDGET: tightening
# seed-lint's constant to 7_000 left `ratchet-lint` reporting "none loosened; 1
# tightened" while this file went on admitting 8000, and the two homes
# disagreed with nothing to say so. (The message also cited ADR-0007, which
# governs the lifecycle BODY ceiling, not the kernel budget.)
size=$(wc -c < "$ROOT/core/AGENTS.md")
budget=$(python3 -c "
import re, pathlib
src = pathlib.Path('$ROOT/tests/seed-lint.py').read_text()
print(re.search(r'^KERNEL_BUDGET = ([0-9_]+)', src, re.M).group(1).replace('_', ''))
")
if (( size > budget )); then
  fail "core/AGENTS.md is ${size} bytes, over KERNEL_BUDGET (${budget}, from tests/seed-lint.py) — the slice is wrong, not the budget"
fi

if (( fails > 0 )); then
  echo "entry-paths: FAIL — ${fails} finding(s)"
  exit 1
fi
echo "entry-paths: OK — the fork is named in the kernel, the adapter, the installer and grow, and an installed plant routes both arms (${size}-byte kernel)"
