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

# This gate reads a verdict out of a `unittest` subprocess's own output, so the
# FORMAT of that output is one of its inputs — and an input it must own rather
# than inherit. Python 3.13+ colorizes `unittest` and traceback output, and
# obeys an ambient `FORCE_COLOR` even when stdout is a pipe: with `FORCE_COLOR`
# exported in the operator's shell, `FAILED (failures=1)` arrives as
# `\e[1;31mFAILED\e[0m (\e[1;31mfailures=1\e[0m)` and every `^`-anchored match
# over it silently stops matching. That is `gate-honesty.input-set-principle`
# in miniature: a verdict that depends on a variable nobody declared. Pin it,
# and strip anything a future interpreter colorizes anyway, so the gate is
# neither falsely red in a colored terminal nor parsing escape codes by luck.
export PYTHON_COLORS=0
plain() { sed -e 's/\x1b\[[0-9;]*[A-Za-z]//g'; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# The same principle, one input further along. `mktemp -d` may hand back a
# route through a symlink, and the tool under test resolves whatever path it
# is handed, so a fixture root that was never resolved compares two spellings
# of one directory and reads as a roster the seed does not own. Resolve it
# where it is created and every assertion below is against the same string.
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

# ===========================================================================
# The FOURTH upward walk: the seed's own test harness.
# ===========================================================================
# `tools/gate-registry.py` records this file's own residual — "it exercises the
# three walkers that exist, so a fourth upward walk added later is covered by
# nothing until someone adds it here". `tests/test_agent_lint.py:61`,
# `REPO = SEED.parent`, is that fourth walk: it is the only line in the whole
# seed suite that reaches above the seed root, and from it the suite resolved
# its roster, its golden-corpus copies and the tool it exercises out of the
# HOST plant's `.claude/`. Checked out inside a plant that adds one agent of
# its own, `bash tests/run.sh` aborted at `run.sh:213` with "golden corpus does
# not cover: ['<the plant's agent>']" and left every step from `:214` to `:252`
# unrun — a partial gate that reads like an ordinary red.
#
# SPEC-0001's six ROSTER_* contracts close it, and they are asserted HERE
# because this file already owns the class. The rule they state is STRICTER
# than the boundary walk above rather than in tension with it: the suite's
# default never looks above `<seed>` at all, so there is no ancestor to deny.
# Same fixture discipline as everything above — a tree this script builds,
# never the checkout it is running in.

RWORK="$WORK/roster"
mkdir -p "$RWORK"

# A seed-shaped fixture holding exactly what test_agent_lint.py resolves at
# import: its own tests/, the roster home, and the seed copy of the tool.
mk_seedlet() {
  local s="$1"
  mkdir -p "$s/tests" "$s/integrations/claude-code"
  cp -a "$ROOT/agents" "$s/agents"
  cp "$ROOT/tests/test_agent_lint.py" "$s/tests/"
  cp "$ROOT/integrations/claude-code/"*.py "$s/integrations/claude-code/"
}

# A host plant with the seed nested inside it: `.claude/agents` is a faithful
# projection of the seed roster PLUS one agent the seed does not have, which is
# the shape of every plant that has CYPRESS installed and has grown since.
mk_host() {
  local h="$1" extra="${2:-plant-only-agent}"
  mkdir -p "$h/.claude/agents"
  cp -a "$ROOT/agents/." "$h/.claude/agents/"
  if [[ "$extra" != "none" ]]; then
    cat > "$h/.claude/agents/$extra.md" <<AGENT
---
name: $extra
description: An agent this plant authored that the seed's roster does not hold.
routing_triggers:
  - "something only this plant does"
model: opus
tools: [Read]
can_delegate: false
---
body
AGENT
  fi
  # a host copy of the tool that is deliberately NOT the seed's bytes
  cp "$ROOT/integrations/claude-code/agent-lint.py" "$h/.claude/agent-lint.py"
  printf '\n# host copy — deliberately not byte-identical to the seed source\n' \
    >> "$h/.claude/agent-lint.py"
  mk_seedlet "$h/Cypress"
}

# Import the suite in the fixture and report what it resolved. Same probe idiom
# the three walkers above are checked with: the question is which artifact was
# selected, and the answer is only observable from inside the module.
# $1 = seedlet dir, $2 = explicit roster override or "" for the default.
roster_probe() {
  local s="$1" explicit="${2:-}"
  CYPRESS_ROSTER_DIR="$explicit" python3 - "$s" <<'PY' 2>&1 || true
import importlib.util, sys
spec = importlib.util.spec_from_file_location("t", sys.argv[1] + "/tests/test_agent_lint.py")
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except SystemExit as e:
    print("REFUSED=" + str(e))
    raise SystemExit(0)
print("ROSTER=" + str(mod.ROSTER))
print("TOOL=" + str(mod._locate_agent_lint()))
print("NAMES=" + ",".join(sorted(mod.ALL_AGENTS)))
PY
}

# --- the default roster is the seed's own agents/, whatever sits above it ---
caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED() {
  local h="$RWORK/default" out
  mk_host "$h"
  out="$(roster_probe "$h/Cypress")"
  grep -qxF "ROSTER=$h/Cypress/agents" <<<"$out" \
    || fail "the suite's default roster is not the seed's own agents/: $(grep '^ROSTER=' <<<"$out")"
  if grep -q "^NAMES=.*plant-only-agent" <<<"$out"; then
    fail "the derived agent-name set holds an agent absent from <seed>/agents/"
  fi
  # …and the same when the host projection is byte-identical to the seed's own
  # roster. The default may not depend on what is above the seed AT ALL: a
  # directory that satisfies the projection predicate exercises nothing the
  # seed home does not, so preferring it buys nothing and costs this defect.
  local t="$RWORK/twin"
  mk_host "$t" none
  out="$(roster_probe "$t/Cypress")"
  grep -qxF "ROSTER=$t/Cypress/agents" <<<"$out" \
    || fail "a byte-identical host projection still displaced the seed's own roster: $(grep '^ROSTER=' <<<"$out")"
}

# --- the tool under test is the seed's copy, not the host's -----------------
caseROSTER_TOOL_UNDER_TEST_IS_THE_SEED_COPY() {
  local h="$RWORK/default" out
  out="$(roster_probe "$h/Cypress")"
  grep -qxF "TOOL=$h/Cypress/integrations/claude-code/agent-lint.py" <<<"$out" \
    || fail "the suite exercises the HOST's agent-lint.py, not the seed's: $(grep '^TOOL=' <<<"$out")"
}

# --- an explicit roster directory is honoured verbatim ----------------------
# Scoping the default to the seed must not make any other roster unreachable;
# that is the same hazard the register's fixtures exclusion carries. The target
# is a THIRD directory — neither the seed home nor the host projection — so
# that today's answer cannot satisfy this case by coincidence.
caseROSTER_EXPLICIT_DIR_IS_HONOURED_VERBATIM() {
  local h="$RWORK/default" e="$RWORK/elsewhere/agents" out
  mkdir -p "$e"
  cat > "$e/00-elsewhere.md" <<'AGENT'
---
name: elsewhere-only
description: An agent that lives only in the directory the caller named.
---
body
AGENT
  out="$(roster_probe "$h/Cypress" "$e")"
  grep -qxF "ROSTER=$e" <<<"$out" \
    || fail "an explicit roster directory was not honoured verbatim: $(grep -E '^(ROSTER|REFUSED)=' <<<"$out")"
  grep -qxF "NAMES=elsewhere-only" <<<"$out" \
    || fail "the explicit roster's names were not the ones derived: $(grep '^NAMES=' <<<"$out")"
  # The two refusal guards keep their meaning against an explicit target: a
  # directory yielding no name, and one yielding fewer names than it holds
  # files, are refused rather than silently falling back to the seed home.
  local n="$RWORK/noname/agents" p="$RWORK/partial/agents"
  mkdir -p "$n" "$p"
  printf 'no frontmatter at all\n' > "$n/00-x.md"
  cp "$e/00-elsewhere.md" "$p/"
  printf 'no frontmatter at all\n' > "$p/01-y.md"
  grep -q "^REFUSED=" <<<"$(roster_probe "$h/Cypress" "$n")" \
    || fail "an explicit roster yielding NO agent name was not refused — it fell back instead"
  grep -q "^REFUSED=" <<<"$(roster_probe "$h/Cypress" "$p")" \
    || fail "an explicit roster yielding fewer names than files was not refused — it fell back instead"
}

# --- every run names the roster it resolved, and by which rule --------------
# A green that does not say which roster it read is a green about a roster the
# reader has not identified — the same reason the status register's pass line
# had to state its scope.
caseROSTER_RESOLVED_SCOPE_IS_STATED_IN_THE_OUTPUT() {
  local h="$RWORK/default" out
  out="$(cd "$h/Cypress" && python3 tests/test_agent_lint.py GoldenCorpusTests 2>&1 || true)"
  grep -F "$h/Cypress/agents" <<<"$out" | grep -Eqi 'default|explicit' \
    || fail "no line of the run names the resolved roster directory and the rule that produced it"
  # …and a FAILING assertion about roster contents names that directory in its
  # own message, so the reader of a red knows which roster it is about. The
  # import banner names it too, so the banner is EXCLUDED from what may satisfy
  # this: a check a banner can satisfy is a check that still passes with the
  # assertion messages reverted, which is a green surviving the defect it
  # claims to pin. Two reds, one per widened message — a roster the corpus
  # OVER-covers (fires `unknown`) and one it UNDER-covers (fires `missing`) —
  # and both need a loadable corpus in the named directory, because without one
  # `load_corpus()` raises FileNotFoundError first and no roster assertion runs
  # at all. `failures=1`, not merely FAILED, is what distinguishes the two.
  local e="$RWORK/elsewhere/agents" m="$RWORK/undercovered/agents" dir
  cp "$ROOT/agents/_routes.golden.tsv" "$e/"
  mkdir -p "$m"
  cp -a "$ROOT/agents/." "$m/"
  cat > "$m/99-uncovered.md" <<'AGENT'
---
name: uncovered-agent
description: A roster agent no row of the golden corpus routes to.
---
body
AGENT
  for dir in "$e" "$m"; do
    out="$(cd "$h/Cypress" && CYPRESS_ROSTER_DIR="$dir" python3 tests/test_agent_lint.py \
             GoldenCorpusTests.test_golden_corpus_is_wellformed_and_covers_the_roster 2>&1 \
             | plain || true)"
    grep -q '^FAILED (failures=1)' <<<"$out" \
      || fail "no roster-contents assertion FAILED against $dir, so nothing pinned its message: $out"
    grep -v '^roster: ' <<<"$out" | grep -F "$dir" | grep -Eqi 'default|explicit' \
      || fail "the failing roster-contents assertion did not name the roster it read in its own message — only the import banner did: $out"
  done
}

# --- nested and standalone must agree -------------------------------------
# The whole-gate form of this is SPEC-0001 AC-16 and is run by the session, not
# from inside a gate step: `bash tests/run.sh` cannot invoke itself. This is the
# lowest level that exercises the behaviour — the one suite whose abort took the
# run down — run once nested and once from a checkout whose parent holds no
# `.claude/`, with the exit codes compared.
caseROSTER_NESTED_SEED_GATE_MATCHES_A_STANDALONE_COPY() {
  local h="$RWORK/default" s="$RWORK/solo" nrc=0 src=0 nout sout
  mkdir -p "$s"; mk_seedlet "$s/Cypress"
  nout="$(cd "$h/Cypress" && python3 tests/test_agent_lint.py GoldenCorpusTests 2>&1)" || nrc=$?
  sout="$(cd "$s/Cypress" && python3 tests/test_agent_lint.py GoldenCorpusTests 2>&1)" || src=$?
  [[ "$nrc" == "$src" ]] \
    || fail "the nested run exited $nrc where the standalone control exited $src — the gate's verdict depends on what the seed is checked out inside"
  if grep -q "plant-only-agent" <<<"$nout$sout"; then
    fail "an assertion named an agent absent from <seed>/agents/"
  fi
}

# --- the parity claim is relocated, not retired ----------------------------
# Scoping the suite's inputs to the seed removes the second copy the byte
# identity check compares, so that check can never execute here again. It must
# SKIP with its reason named: a vacuous green there would retire the claim while
# looking like coverage, which is the census's own subject matter. Today, in a
# nested checkout, it reports `ok` — against the HOST's copy.
caseROSTER_PROJECTION_PARITY_SKIPS_EVERYWHERE() {
  local h="$RWORK/default" out
  out="$(cd "$h/Cypress" && python3 tests/test_agent_lint.py \
           GoldenCorpusTests.test_golden_corpus_copies_are_byte_identical 2>&1 || true)"
  grep -q "skipped" <<<"$out" \
    || fail "the golden-corpus parity check did not skip in a seed that holds one copy — it ran against a copy outside the seed: $out"
  grep -qi "copies present to compare" <<<"$out" \
    || fail "the parity skip did not print the reason it skipped: $out"
}

caseROSTER_DEFAULT_RESOLVES_INSIDE_THE_SEED
caseROSTER_TOOL_UNDER_TEST_IS_THE_SEED_COPY
caseROSTER_EXPLICIT_DIR_IS_HONOURED_VERBATIM
caseROSTER_RESOLVED_SCOPE_IS_STATED_IN_THE_OUTPUT
caseROSTER_NESTED_SEED_GATE_MATCHES_A_STANDALONE_COPY
caseROSTER_PROJECTION_PARITY_SKIPS_EVERYWHERE

if (( fails )); then
  echo "nested-checkout: FAIL — $fails finding(s)" >&2
  exit 1
fi
echo "nested-checkout: OK — the ancestor is denied, the plant's own root is found"
