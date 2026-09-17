#!/usr/bin/env bash
# test-status-register.sh — the lifecycle-status register does what a plant's
# CI, session-start hook and canonize close-out rely on:
#   a clean tree PASSES: every base status with its companions, the three
#     kind extensions, a body "## Status" pointer, and files that carry no
#     lifecycle at all (ordinary nodes, legal_status, no frontmatter);
#   each D-STATUS violation class FAILS with file:line and the reason — bad
#     vocabulary; closed/superseded/deferred/open/standing without their
#     companion; a missing or malformed status_date; a body value that
#     contradicts the frontmatter (both values named);
#   kind extensions are per kind: an ADR may be `accepted`, a spec may not,
#     and the finding says the kind was inferred from the directory;
#   --strict-unknown turns "no status at all" into a finding for the kinds
#     that must carry one, and nothing else — the default stays silent so
#     adoption is incremental;
#   the query role never fails on content: --open/--hotfix/... list
#     oldest-first, --since/--by-kind filter, --summary is one short
#     paragraph, --json is the same result for tooling;
#   scan()/lint() are importable, which is how a hook and a host linter
#     call it in-process instead of keeping a second copy.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REG="$ROOT/tools/status-register.py"
FIX="$ROOT/tests/fixtures/status"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
CASE=""     # the contract slug the current case carries, named in every failure
fail() { echo "FAIL: ${CASE:+[$CASE] }$*" >&2; [ -f "$TMP/out" ] && cat "$TMP/out" >&2; exit 1; }

# run <expected-rc> <args...> -> output in $TMP/out
run() {
  local want="$1"; shift
  local rc=0
  python3 "$REG" "$@" >"$TMP/out" 2>&1 || rc=$?
  [ "$rc" -eq "$want" ] || fail "expected exit $want, got $rc (args: $*)"
}

# run_at <dir> <expected-rc> <args...> -> output in $TMP/out
# The tool run FROM <dir>, which is the only way to exercise what it does when
# nobody passes --root. `run` above always names one, so every case written
# with it says nothing about the scope the tool picks for itself.
run_at() {
  local dir="$1" want="$2"; shift 2
  local rc=0
  ( cd "$dir" && python3 "$REG" "$@" ) >"$TMP/out" 2>&1 || rc=$?
  [ "$rc" -eq "$want" ] || fail "expected exit $want, got $rc (cwd: $dir, args: $*)"
}

# clean_item <path> — a markdown file this linter has nothing to say about.
clean_item() {
  mkdir -p "$(dirname "$1")"
  cat >"$1" <<'CLEANITEM'
---
id: adr.clean
kind: adr
title: a decision with nothing wrong with it
status: accepted
status_date: 2026-09-16
---

# a decision with nothing wrong with it
CLEANITEM
}

# 1. A clean tree passes: every base status with its companion, an ADR
#    `accepted` (kind inferred from decisions/), a spec `active` with a
#    "see frontmatter" metadata bullet, a deviation `standing` with ends_when,
#    a body "## Status" pointer, and files that carry no lifecycle at all.
run 0 --root "$FIX/clean"
grep -q "status register: PASS" "$TMP/out" || fail "clean tree did not report PASS"
grep -q "12 file(s) scanned, 9 status-carrying" "$TMP/out" \
  || fail "clean tree counted wrong (no-status nodes / plain files must be scanned, not carrying)"
echo "  clean tree passes; pointers and status-less files are not findings — OK"

# 2. Every violation class fails, each naming its file, line and reason. One
#    run over the planted tree, one assertion per fixture, and an exact total
#    so no fixture can pass silently.
run 1 --root "$FIX/violations"
grep -q "bad-vocabulary.md:5: status 'wip' is not in the vocabulary for kind risk" "$TMP/out" \
  || fail "bad vocabulary not reported"
grep -q "closed-no-evidence.md:5: status 'closed' requires \`status_evidence\`" "$TMP/out" \
  || fail "closed without status_evidence not reported"
grep -q "superseded-no-target.md:5: status 'superseded' requires \`superseded_by\`" "$TMP/out" \
  || fail "superseded without superseded_by not reported"
grep -q "deferred-no-reopen.md:5: status 'deferred' requires \`reopen_when\`" "$TMP/out" \
  || fail "deferred without reopen_when not reported"
grep -q "open-no-owner.md:5: status 'open' requires \`owner\`" "$TMP/out" \
  || fail "open without owner not reported"
grep -q "standing-no-ends-when.md:5: status 'standing' requires \`ends_when\`" "$TMP/out" \
  || fail "standing without ends_when not reported"
grep -q "missing-status-date.md:5: \`status_date\` is required" "$TMP/out" \
  || fail "missing status_date not reported"
grep -q "bad-status-date.md:6: \`status_date\` '2026-1-7' is not a YYYY-MM-DD date" "$TMP/out" \
  || fail "malformed status_date not reported at its own line"
grep -q "body-disagrees.md:12: body states status 'proposed' but frontmatter says 'accepted'" "$TMP/out" \
  || fail "body/frontmatter disagreement not reported with both values"
grep -q "FAIL (9 finding(s))" "$TMP/out" || fail "expected exactly 9 findings"
echo "  nine violation classes fail with file:line + reason — OK"

# 3. A lifecycle word used in an ordinary sentence is not a stated status.
#    Every status word is also an English word, so scanning a "## Status"
#    section for any occurrence made a correct pointer plus its explanation
#    fail — and, the check being fail-closed, taught stewards to reword true
#    prose until the linter was happy. A value still fails when it is stated;
#    prose that merely uses the word does not.
run 0 --root "$FIX/prose"
grep -q "status register: PASS" "$TMP/out" \
  || fail "a Status section that points at frontmatter and then explains itself was flagged"
grep -q "2 file(s) scanned, 2 status-carrying" "$TMP/out" \
  || fail "prose tree counted wrong"
grep -q "body states status" "$TMP/out" \
  && fail "a lifecycle word inside a sentence was read as a stated status"
#    …and the genuine second home it exists to catch still fails (case 2 above
#    asserts the finding; assert here that the fix did not silence it).
run 1 --root "$FIX/violations"
grep -q "body-disagrees.md:12: body states status 'proposed' but frontmatter says 'accepted'" "$TMP/out" \
  || fail "a bare restated value stopped being reported"
echo "  prose that uses a lifecycle word passes; a restated value still fails — OK"

# 4. Kind extensions are per kind. The same value `accepted` passes on an ADR
#    and fails on a spec; both kinds come from the directory name, and the
#    spec finding says so and names the kind the value belongs to.
run 0 --root "$FIX/kind-extension/decisions"
run 1 --root "$FIX/kind-extension/specs"
grep -q "SPEC-0002-extension.md:4: status 'accepted' is not in the vocabulary for kind spec, inferred from the directory name" "$TMP/out" \
  || fail "spec `accepted` not rejected, or inference not stated"
grep -q "'accepted' belongs to kind adr" "$TMP/out" || fail "owning kind not named"
grep -q "FAIL (1 finding(s))" "$TMP/out" || fail "expected exactly 1 finding"
echo "  ADR accepted passes, spec accepted fails, inference stated — OK"

# 5. --strict-unknown: a status-less ADR is silent by default and a finding
#    under strict; an ordinary node stays silent either way.
run 0 --root "$FIX/strict"
grep -q "0 status-carrying" "$TMP/out" || fail "strict tree should carry no status"
run 1 --root "$FIX/strict" --strict-unknown
grep -q "adr-0003-no-status.md:1: no \`status:\` in frontmatter (kind adr, inferred from the directory name" "$TMP/out" \
  || fail "status-less ADR not reported under --strict-unknown"
grep -q "subsystem.no-status" "$TMP/out" && fail "an ordinary node was asked for a status"
grep -q "FAIL (1 finding(s))" "$TMP/out" || fail "expected exactly 1 strict finding"
echo "  --strict-unknown flags only the kinds that must carry a status — OK"

# 6. A lint over no markdown at all is refused (exit 2, not a PASS); a
#    missing root likewise. A query over the same empty tree is NOT refused —
#    a fresh plant owes nothing yet, and the hook must still run.
mkdir -p "$TMP/empty"
run 2 --root "$TMP/empty"
grep -q "refusing a vacuous pass" "$TMP/out" || fail "empty lint not refused"
run 2 --root "$FIX/does-not-exist"
grep -q "no such path" "$TMP/out" || fail "missing root not refused"
run 0 --root "$TMP/empty" --open
[ ! -s "$TMP/out" ] || fail "empty --open should print nothing"
run 0 --root "$TMP/empty" --summary
grep -q "no status-carrying files under" "$TMP/out" || fail "empty --summary should say so"
run 2 --root "$FIX/query" --since 2026-13-40
grep -q -- "--since wants YYYY-MM-DD" "$TMP/out" || fail "bad --since not refused"
echo "  vacuous lint refused, empty query allowed, bad --since refused — OK"

# 7. --open lists oldest-first, an undated item last; --open --hotfix merges
#    the two in date order; the query role exits 0 over a tree whose lint
#    would fail (the violations tree) — a query never fails on content.
run 0 --root "$FIX/query" --open
diff <(awk '{print $1, $2, $3}' "$TMP/out") - <<'EOF' >/dev/null \
  || fail "--open order wrong: $(tr '\n' '|' <"$TMP/out")"
open spec spec.oldest-open
open adr adr.newer-open
open risk risk.undated-open
EOF
grep -q "^open  spec  spec.oldest-open  product  2025-11-15$" "$TMP/out" \
  || fail "--open line shape is not 'status  kind  id  owner  status_date'"
run 0 --root "$FIX/query" --open --hotfix
[ "$(awk 'NR==2 {print $1}' "$TMP/out")" = "hotfix" ] \
  || fail "--open --hotfix did not merge by date (hotfix 2026-01-10 should be second)"
grep -q "deferred\|closed\|rejected\|standing" "$TMP/out" && fail "--open --hotfix leaked other statuses"
run 0 --root "$FIX/violations" --open
echo "  --open oldest-first, --open --hotfix merged, never fails on content — OK"

# 8. --since and --by-kind filter; the companion column shows the key the
#    status requires (reopen_when for deferred, status_evidence for closed).
run 0 --root "$FIX/query" --since 2026-02-01
[ "$(wc -l <"$TMP/out" | tr -d ' ')" = "3" ] || fail "--since 2026-02-01 should keep 3 dated items"
grep -q "^deferred  risk  risk.parked  platform  2026-02-02  reopen_when=the second region goes live$" "$TMP/out" \
  || fail "deferred line lacks its reopen_when companion"
grep -q "status_evidence=gate green on 2026-04-04" "$TMP/out" || fail "closed line lacks its evidence"
grep -q "undated-open" "$TMP/out" && fail "--since kept an undated item"
run 0 --root "$FIX/query" --by-kind risk --deferred --rejected
[ "$(wc -l <"$TMP/out" | tr -d ' ')" = "2" ] || fail "--by-kind risk --deferred --rejected should keep 2"
run 0 --root "$FIX/query" --by-kind adr
grep -q "^open  adr  adr.newer-open" "$TMP/out" || fail "--by-kind adr lost the inferred-kind ADR"
[ "$(wc -l <"$TMP/out" | tr -d ' ')" = "1" ] || fail "--by-kind adr should keep exactly 1"
echo "  --since / --by-kind filter; companion column follows the status — OK"

# 9. --summary is one paragraph a session-start hook can inject: one line,
#    under 400 characters, counts per status, the three oldest open/hotfix in
#    date order, and it reads as prose (no undated item claims age).
run 0 --root "$FIX/query" --summary
[ "$(wc -l <"$TMP/out" | tr -d ' ')" = "1" ] || fail "--summary must be a single line"
[ "$(wc -c <"$TMP/out" | tr -d ' ')" -lt 400 ] || fail "--summary over 400 characters"
grep -q "^Status register: 8 tracked — 1 hotfix, 3 open, 1 deferred, 1 standing, 1 rejected, 1 closed\." "$TMP/out" \
  || fail "--summary counts wrong or out of order"
grep -q "Oldest needing attention: spec.oldest-open (open since 2025-11-15, owner product); risk.hot (hotfix since 2026-01-10, owner on-call); adr.newer-open (open since 2026-03-01, owner architect)\.$" "$TMP/out" \
  || fail "--summary oldest-three wrong"
run 0 --root "$FIX/query/nodes" --by-kind deviation --summary
grep -q "Nothing open or hotfix" "$TMP/out" \
  && fail "--summary is over the whole tree; --by-kind must not narrow it"
echo "  --summary: one line, <400 chars, counts + three oldest — OK"

# 10. --json emits the same result for tooling: the list and the summary.
run 0 --root "$FIX/query" --open --json
python3 - "$TMP/out" <<'PY' || fail "--open --json shape"
import json, sys
rows = json.load(open(sys.argv[1]))
assert [r["id"] for r in rows] == ["spec.oldest-open", "adr.newer-open", "risk.undated-open"], rows
assert rows[0]["owner"] == "product" and rows[0]["status_date"] == "2025-11-15", rows[0]
assert rows[2]["status_date"] is None, rows[2]
assert set(rows[0]) >= {"path", "id", "kind", "status", "owner", "status_date",
                        "status_evidence", "superseded_by", "reopen_when", "ends_when"}
PY
run 0 --root "$FIX/query" --summary --json
python3 - "$TMP/out" <<'PY' || fail "--summary --json shape"
import json, sys
s = json.load(open(sys.argv[1]))
assert s["tracked"] == 8 and s["counts"]["open"] == 3 and s["counts"]["hotfix"] == 1, s
assert [d["id"] for d in s["oldest_attention"]] == ["spec.oldest-open", "risk.hot", "adr.newer-open"], s
PY
echo "  --json for the list and the summary — OK"

# 11. The reuse contract: a hook or host linter imports this file by path and
#     calls scan()/lint() in-process. If they move or change shape, the
#     session-start summary and seed-lint's check go silently missing.
python3 - "$REG" "$FIX" <<'PY' >"$TMP/out" 2>&1 || fail "import contract broken"
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("status_register", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fix = Path(sys.argv[2])
items = mod.scan([fix / "clean"], relative_to=fix)
assert len(items) == 11, [i.path for i in items]          # plain.md has no frontmatter
assert sum(1 for i in items if i.status) == 9
assert mod.lint(items) == []
bad = mod.lint(mod.scan([fix / "violations"], relative_to=fix))
assert sorted({f.rule for f in bad}) == ["body-status", "companion", "status-date", "vocabulary"], bad
assert [(f.path, f.line) for f in bad if f.rule == "body-status"] == [("violations/body-disagrees.md", 12)], bad
strict = mod.lint(mod.scan([fix / "strict"]), strict_unknown=True)
assert [f.rule for f in strict] == ["missing-status"], strict
text = mod.summary_text(mod.summarize(mod.scan([fix / "query"])))
assert text.startswith("Status register: 8 tracked") and len(text) < 400, text
print("import contract: OK")
PY
grep -q "import contract: OK" "$TMP/out" || fail "import contract assertions did not run"
echo "  scan()/lint()/summarize() importable — the hook reuse contract — OK"


# ==========================================================================
# SPEC-0001-gate-assertion-floor, increment 9 — the declared default scope.
#
# Cases 1-11 above every one name a --root. That is why the tool could ship
# with a default scope of `.` and nobody notice: no case in this suite had
# ever run it the way a session runs it. The four cases below are RED until
# `docs/graph/status-register.py` / `Cypress/tools/status-register.py` gain a
# default root, a default-sweep exclusion and a scoped PASS line.
#
# Each case is a shell function whose NAME is the contract slug, because
# spec-lint.py credits coverage from the slug appearing anywhere under
# Cypress/tests/ — including inside a comment. A slug that lives only in a
# comment is the `coverage` false green the census records; a slug that names
# the thing that executes is not.
# ==========================================================================

# --- 12. the default scope is the graph, not whatever the CWD contains -----
caseREGISTER_DEFAULT_ROOT_PREFERS_THE_GRAPH() {
  CASE=REGISTER_DEFAULT_ROOT_PREFERS_THE_GRAPH
  local d="$TMP/default-root"; rm -rf "$d"
  clean_item "$d/docs/graph/decisions/adr-0001-clean.md"
  # A markdown file that is somebody's business, but not this tool's: it sits
  # beside the declared graph, not in it.
  cp "$FIX/violations/open-no-owner.md" "$d/outside-the-graph.md"
  run_at "$d" 0
  grep -q "status register: PASS" "$TMP/out" \
    || fail "a tree whose docs/graph/ is clean did not pass with no --root"
  ! grep -q "outside-the-graph" "$TMP/out" \
    || fail "the default sweep reached a file outside docs/graph/"

  # And with no docs/graph/ beneath it, the default root stays the working
  # directory, exactly as today — this half must not change.
  local e="$TMP/default-root-nograph"; rm -rf "$e"; mkdir -p "$e"
  cp "$FIX/violations/open-no-owner.md" "$e/"
  run_at "$e" 1
  grep -q "open-no-owner.md:5: status 'open' requires \`owner\`" "$TMP/out" \
    || fail "with no docs/graph/ present the default root stopped being the CWD"
  CASE=""
}
caseREGISTER_DEFAULT_ROOT_PREFERS_THE_GRAPH
echo "  the default root is docs/graph/ when there is one, the CWD when there is not — OK"

# --- 13. a default sweep is not decided by somebody else's violations ------
# `tests/fixtures/` is where a linter's own counter-examples live. A tool that
# counts them as findings about the tree teaches its reader that it cries
# wolf, and a tool nobody runs asserts nothing.
caseREGISTER_DEFAULT_SWEEP_SKIPS_VIOLATION_FIXTURES() {
  CASE=REGISTER_DEFAULT_SWEEP_SKIPS_VIOLATION_FIXTURES
  local d="$TMP/sweep"; rm -rf "$d"
  clean_item "$d/decisions/adr-0001-clean.md"
  # Two depths, because the contract says "at any depth": one nested inside a
  # vendored project, one directly beneath the root being swept.
  mkdir -p "$d/Cypress/tests/fixtures/status" "$d/tests/fixtures"
  cp "$FIX/violations/open-no-owner.md" "$d/Cypress/tests/fixtures/status/"
  cp "$FIX/violations/bad-vocabulary.md" "$d/tests/fixtures/"
  run_at "$d" 0
  grep -q "status register: PASS" "$TMP/out" \
    || fail "deliberate violation fixtures decided the verdict of a default sweep"
  ! grep -q "fixtures/" "$TMP/out" \
    || fail "a finding originated inside a tests/fixtures/ subtree"
  CASE=""
}
caseREGISTER_DEFAULT_SWEEP_SKIPS_VIOLATION_FIXTURES
echo "  a default sweep skips tests/fixtures/ at any depth — OK"

# --- 14. naming a root is a declaration of scope, not a suggestion ---------
# The exclusion case 13 pins must not reach an explicit --root, or this whole
# suite stops being able to prove the linter fires: cases 2-5 aim straight at
# $FIX, which is a tests/fixtures/ path.
caseREGISTER_EXPLICIT_ROOT_IS_HONOURED_VERBATIM() {
  CASE=REGISTER_EXPLICIT_ROOT_IS_HONOURED_VERBATIM
  local d="$TMP/explicit"; rm -rf "$d"
  clean_item "$d/decisions/adr-0001-clean.md"
  mkdir -p "$d/Cypress/tests/fixtures/status"
  cp "$FIX/violations/open-no-owner.md" "$FIX/violations/bad-vocabulary.md" \
     "$d/Cypress/tests/fixtures/status/"
  # Skipped by the default sweep…
  run_at "$d" 0
  ! grep -q "open-no-owner" "$TMP/out" \
    || fail "the default sweep reported a fixture violation, so 'verbatim' has nothing to mean"
  # …and reported, every one, when the root names them.
  run 1 --root "$d/Cypress/tests/fixtures/status"
  grep -q "open-no-owner.md:5: status 'open' requires \`owner\`" "$TMP/out" \
    || fail "an explicit --root at a fixtures path stopped reporting its violations"
  grep -q "bad-vocabulary.md:5: status 'wip' is not in the vocabulary for kind risk" "$TMP/out" \
    || fail "an explicit --root at a fixtures path dropped a second violation"
  grep -q "FAIL (2 finding(s))" "$TMP/out" \
    || fail "an explicit root reported a different number of findings than it holds"
  # And the vacuous-pass refusal still fires when an explicit root matches no
  # markdown at all: honouring a root verbatim includes honouring an empty one.
  mkdir -p "$d/empty"
  run 2 --root "$d/empty"
  grep -q "refusing a vacuous pass" "$TMP/out" \
    || fail "the vacuous-pass refusal stopped firing on an explicit empty root"
  CASE=""
}
caseREGISTER_EXPLICIT_ROOT_IS_HONOURED_VERBATIM
echo "  an explicit --root is honoured verbatim, exclusion and all — OK"

# --- 15. the PASS line says what it covers ---------------------------------
# "230 file(s) scanned" reads as 230 files certified. One of them carried a
# status. The line has to say which root it read and what the verdict covers,
# or the number is an invitation to misread it.
caseREGISTER_PASS_LINE_STATES_ITS_SCOPE() {
  CASE=REGISTER_PASS_LINE_STATES_ITS_SCOPE
  run 0 --root "$FIX/clean"
  # The counts case 1 pins stay: this contract adds scope, it does not replace
  # the figures.
  grep -q "12 file(s) scanned, 9 status-carrying" "$TMP/out" \
    || fail "the k-of-n figures case 1 pins must survive the scope sentence"
  grep -q "$FIX/clean" "$TMP/out" \
    || fail "the PASS line does not name the root it actually scanned"
  grep -qi "covers" "$TMP/out" \
    || fail "the PASS line does not state that the verdict covers the status-carrying files only"
  CASE=""
}
caseREGISTER_PASS_LINE_STATES_ITS_SCOPE
echo "  the PASS line names its root and states what it covers — OK"

echo "test-status-register: PASS"
