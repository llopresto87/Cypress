#!/usr/bin/env bash
set -euo pipefail

# 7.14.0 — T2's contained lane.
#
# Before this, the T2 edge read "no active spec contract means T3, however
# small it looks", and T1 was defined by touching no behavior at all. A
# three-line defect fix in code no spec covered therefore fell through both
# and bought a specify pass plus a grill pass to authorize itself. Paid often
# enough, that is how a funnel stops being believed.
#
# The lane makes the authorization proportional — a RED test plus a recorded
# why instead of a spec document — and the danger of that trade is that it
# erodes into a skip. These greps pin both halves: that the lane exists with
# exactly one home and every surface points at it, and that it never bought
# its way out of the test, the review, the gates, or the record.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() { echo "FAIL: $*" >&2; exit 1; }

# -- one home -----------------------------------------------------------
owners=$(grep -rl '^  - tiers.contained-lane$' "$ROOT"/{core,protocols,skills,agents,templates} 2>/dev/null | wc -l)
[ "$owners" -eq 1 ] || fail "tiers.contained-lane must be owned exactly once, found $owners owners"
grep -q '^  - tiers.contained-lane$' "$ROOT/core/method/tiers.md" \
  || fail "method.tiers must own tiers.contained-lane"
grep -q '^  - canonize.why-record$' "$ROOT/protocols/canonize.md" \
  || fail "protocol.canonize must own canonize.why-record"

# -- the five conditions live in the home, all of them -------------------
for cond in 'One surface' 'No new dependency' 'Reversible' 'No spec owns the surface' 'The intent fits in a decision note'; do
  grep -q "$cond" "$ROOT/core/method/tiers.md" || fail "tiers.md lost the '$cond' condition"
done
grep -q 'unanimous' "$ROOT/core/method/tiers.md" || fail "tiers.md must state the lane is unanimous"
grep -q 'Three edges keep the tiers honest' "$ROOT/core/method/tiers.md" \
  || fail "tiers.md must carry three hard edges, not two"

# -- the lane never waives the cycle, the review, or the gates -----------
grep -q 'substitutes, it does not waive' "$ROOT/protocols/test-first.md" \
  || fail "test-first must say the contained lane substitutes rather than waives"
grep -q 'the grill pass, never out of' "$ROOT/protocols/test-first.md" \
  || fail "test-first must deny the lane any exit from RED-GREEN-REFACTOR"
grep -q 'tier does not pick the row; the blast radius does' "$ROOT/protocols/verify.md" \
  || fail "verify must deny the lane any gate discount"
grep -q 'reviewer audit' "$ROOT/core/method/tiers.md" \
  || fail "tiers.md must keep the independent reviewer audit on both lanes"

# -- the why-record is owed, and is not allowed to grow into a spec ------
grep -q 'Why-record' "$ROOT/protocols/canonize.md" || fail "canonize lost the why-record"
grep -q 'never a spec' "$ROOT/protocols/canonize.md" \
  || fail "canonize must forbid the why-record becoming a spec"
grep -q 'all five are done' "$ROOT/protocols/canonize.md" \
  || fail "canonize's completeness claim must count the why-record"
grep -q 'contained-lane' "$ROOT/skills/adr-writer/SKILL.md" \
  || fail "adr-writer must describe the short form the lane calls for"

# -- the spec rule's own home carries the exception ---------------------
# rule.spec lives in protocols/specify.md. If the exception is not written
# there, the seed asserts "no code without a spec" in the owning node while
# the tier table routes small behavior changes around it — a contradiction
# in the always-loaded surface, which is worse than either rule alone.
grep -q 'The one exception, and its price' "$ROOT/protocols/specify.md" \
  || fail "specify (rule.spec's home) must carry the contained-lane exception"
grep -q 'is not one of the conditions' "$ROOT/protocols/specify.md" \
  || fail "specify must deny line count as an entry condition for the lane"
grep -q 'contained' "$ROOT/core/AGENTS.md" \
  || fail "kernel §3.1 must carry the exception; the kernel is always loaded"

# -- every surface that routes a task knows the lane exists -------------
# The per-prompt hooks (integrations/claude-code/route-hook.py and
# integrations/prime-agent/route-extension.ts) are not on this list: their text
# points at kernel §0 and restates none of it (SPEC-0003
# HOOK_TEXT_RESTATES_NO_KERNEL_RULE, I-8), so they no longer name the lane. The
# kernel, which they point at, is asserted to carry it at the grep above.
# README.md left this list in 7.29.0 (SPEC-0004 C4): it no longer restates the
# tier rules and links the manual instead, whose §4.1 is the lane's reader-facing
# home: the loop below holds DOCUMENTATION.md, and the grep after it holds §4.1's
# heading, so the lane cannot survive only as a passing mention elsewhere.
for f in core/AGENTS.md \
         agents/00-orchestrator.md \
         agents/02-implementer.md \
         agents/04-tester.md \
         protocols/deliver.md \
         protocols/grill.md \
         manifest.json \
         DOCUMENTATION.md \
         documentation/protocols-reference.md; do
  grep -qi 'contained' "$ROOT/$f" || fail "$f never mentions the contained lane"
done
grep -qF "### 4.1 T2's contained lane" "$ROOT/DOCUMENTATION.md" \
  || fail "DOCUMENTATION.md lost its §4.1 heading, the contained lane's reader-facing home"

# -- the superseded absolutist edge is gone from shipped prose ----------
if grep -rn 'however small it looks' "$ROOT"/{core,protocols,agents,skills,templates,integrations,documentation} \
     README.md DOCUMENTATION.md manifest.json >/dev/null 2>&1; then
  fail "the superseded 'no covering spec means T3, however small it looks' edge survives"
fi

echo "tier lanes: PASS"
