#!/usr/bin/env bash
# Two independent regressions, pinned once by manual probe and never by a
# permanent test:
#
# (a) Special-character target paths. The Codex snippet used to substitute
#     the project path through a `sed` REPLACEMENT, where `&` expands to the
#     whole match — a target directory named `a&b` silently corrupted every
#     path in the generated snippet, with exit 0. install.sh now does the
#     substitution literally in Python; this pins that a hostile-looking but
#     legal directory name never regresses back to the sed behavior.
#
# (b) tests/seed-lint.py now enforces a machinery body ceiling and a
#     per-harness eager-context budget with a zero-slack exemption ratchet,
#     plus a larger ceiling for the three cross-project meta-loop protocols.
#     A budget that cannot fail is not a budget — this proves each one
#     actually binds, without ever editing seed-lint.py itself.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# install.sh canonicalises the project directory it is given, and `mktemp -d`
# may hand back a route through a symlink, so a root resolved only on one
# side fails a round-trip the installer passed.
WORK="$(cd "$(mktemp -d)" && pwd -P)"
trap 'rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# (a) special-character target paths
# ---------------------------------------------------------------------------
HAVE_TOMLLIB=1
python3 -c "import tomllib" >/dev/null 2>&1 || HAVE_TOMLLIB=0

# The five shell metacharacters U-08 was verified against, plus the two the
# five-name set could not reach. A TOML basic string forbids a raw newline and
# tab as well as `"` and `\`, and the snippet is what the owner PASTES into
# ~/.codex/config.toml — so an unescaped one lands as a corrupt config in their
# editor instead of failing here. Verified before the escaper was widened: a
# directory whose name contains a newline produced a snippet `tomllib` refuses,
# at exit 0 with no warning.
for name in "a b" "a&b" "a[b]" "a#b" "a'b" "$(printf 'a\nb')" "$(printf 'a\tb')"; do
    D="$WORK/dirs/$name"
    mkdir -p "$D"
    OUT="$("$ROOT/install.sh" codex --project-dir "$D" >"$WORK/codex-$$.log" 2>&1; echo $?)"
    [[ "$OUT" == "0" ]] || {
        cat "$WORK/codex-$$.log" >&2
        fail "codex install into '$name' exited $OUT, expected 0"
    }
    SNIPPET="$D/.codex/codex-config-snippet.toml"
    [[ -f "$SNIPPET" ]] || fail "codex install into '$name': no snippet was generated"
    # The target path must arrive INTACT. The test is "does it round-trip",
    # not "do these bytes appear": a TOML basic string escapes a newline or a
    # tab, so grepping for the literal path asserted the ABSENCE of correct
    # escaping. Where tomllib is present the value is parsed and compared;
    # otherwise the byte check still covers the five metacharacters that need
    # no escape, which is all it ever covered.
    if [[ "$HAVE_TOMLLIB" -eq 1 ]]; then
        EXPECT="$D" python3 "$ROOT/tests/helpers/codex-path-roundtrip.py" "$SNIPPET" \
            || fail "codex snippet for '$name' does not carry the target path intact"
    else
        grep -F -- "$D" "$SNIPPET" >/dev/null \
            || fail "codex snippet for '$name' does not contain the literal target path"
    fi
    # And the placeholder must be fully substituted — no residual template text
    # anywhere in the file (the `&`-expansion bug left this behind).
    grep -q "abs/path/to/project" "$SNIPPET" \
        && fail "codex snippet for '$name' still contains the unsubstituted placeholder 'abs/path/to/project'"
    if [[ "$HAVE_TOMLLIB" -eq 1 ]]; then
        python3 -c "
import tomllib, sys
with open(sys.argv[1], 'rb') as f:
    tomllib.load(f)
" "$SNIPPET" || fail "codex snippet for '$name' does not parse as TOML"
    fi
    echo "  codex --project-dir '$name': exit 0, literal path present, no residual placeholder$( [[ $HAVE_TOMLLIB -eq 1 ]] && echo ', valid TOML' ) — OK"
done

# claude-code must also tolerate at least one such path (it has no sed-based
# substitution, but the installer as a whole must not choke on the name).
D="$WORK/dirs/a&b-cc"
mkdir -p "$D"
"$ROOT/install.sh" claude-code --project-dir "$D" >"$WORK/cc-$$.log" 2>&1 \
    || { cat "$WORK/cc-$$.log" >&2; fail "claude-code install into a special-character dir did not exit 0"; }
echo "  claude-code --project-dir with special characters: exit 0 — OK"

# ---------------------------------------------------------------------------
# (b) the budgets can fail — prove all three bind, without editing seed-lint.py
# ---------------------------------------------------------------------------
# Loaded as a module (importlib, the seed's own idiom for reusing a tool's
# rules from a test) rather than shelled out to, so the constants can be
# overridden in memory per-case and `findings` cleared between them.
run_budget_probe() {
    python3 - "$ROOT/tests/seed-lint.py" <<'PY'
import importlib.util
import pathlib
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location("seed_lint_probe", path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

# The kernel's size is MEASURED, not written down here. It was the literal
# 7564 — its byte count at d7588e2 — in five places, and the kernel is 7752
# today. This probe's own first assertion is "at the SHIPPED constants, both
# checks must be clean … a budget already tripping at HEAD proves nothing", and
# it could not see HEAD. The 188-byte blind spot was larger than the tightest
# harness's entire remaining slack, so padding the kernel to a legal 7 999
# bytes made seed-lint FAIL on the eager budget while this probe printed OK.
KERNEL_BYTES = (pathlib.Path(path).resolve().parent.parent
                / "core" / "AGENTS.md").stat().st_size

failures = []
shipped_eager_budget = mod.EAGER_BUDGET
shipped_ceiling = mod.MACHINERY_BODY_CEILING
shipped_lifecycle = mod.LIFECYCLE_BODY_CEILING

# -- baseline: at the SHIPPED constants, both checks must be clean. If they
# are not, this test is measuring nothing (a budget already tripping at HEAD
# proves nothing about whether the mechanism can fail on purpose).
mod.findings.clear()
mod.check_body_ceiling()
if mod.findings:
    failures.append(f"baseline check_body_ceiling() is not clean at shipped "
                     f"MACHINERY_BODY_CEILING={mod.MACHINERY_BODY_CEILING} / "
                     f"LIFECYCLE_BODY_CEILING={mod.LIFECYCLE_BODY_CEILING}: {mod.findings}")

mod.findings.clear()
mod.check_eager_surface(KERNEL_BYTES)
if mod.findings:
    failures.append(f"baseline check_eager_surface({KERNEL_BYTES}) is not clean at shipped "
                     f"EAGER_BUDGET={mod.EAGER_BUDGET} / EAGER_EXEMPTIONS="
                     f"{mod.EAGER_EXEMPTIONS}: {mod.findings}")

# -- the GENERAL ceiling must bind a general node. It cannot be probed with
# graft any more: graft is a lifecycle node and answers to the other ceiling,
# so a probe at 900 would now pass while proving nothing. Use the largest node
# the general ceiling actually governs, discovered rather than named, so this
# keeps binding when the largest one changes.
_general = [(len(b.strip("\n").splitlines()), l)
            for l, _f, b in mod.machinery_nodes() if l not in mod.LIFECYCLE_NODES]
_gmax_lines, _gmax_label = max(_general)
mod.MACHINERY_BODY_CEILING = _gmax_lines - 1
mod.findings.clear()
mod.check_body_ceiling()
if not mod.findings:
    failures.append(f"MACHINERY_BODY_CEILING={_gmax_lines - 1} produced zero "
                     f"findings — the general body ceiling cannot fail")
elif not any(_gmax_label in f for f in mod.findings):
    failures.append(f"MACHINERY_BODY_CEILING={_gmax_lines - 1} findings never "
                     f"name {_gmax_label} ({_gmax_lines} lines): {mod.findings}")
mod.MACHINERY_BODY_CEILING = shipped_ceiling  # restore (in-process only; file untouched)

# -- the LIFECYCLE ceiling must bind too, and must bind ONLY the three. An
# exemption nobody can trip is an exemption that has quietly become "no limit",
# which is the thing the owner decision explicitly declined to grant.
_lifecycle = [(len(b.strip("\n").splitlines()), l)
              for l, _f, b in mod.machinery_nodes() if l in mod.LIFECYCLE_NODES]
if len(_lifecycle) != len(mod.LIFECYCLE_NODES):
    failures.append(f"LIFECYCLE_NODES names {sorted(mod.LIFECYCLE_NODES)} but only "
                     f"{sorted(l for _n, l in _lifecycle)} are machinery nodes — a "
                     f"name that matches nothing exempts nothing and hides a typo")
_lmax_lines, _lmax_label = max(_lifecycle)
mod.LIFECYCLE_BODY_CEILING = _lmax_lines - 1
mod.findings.clear()
mod.check_body_ceiling()
if not any(_lmax_label in f for f in mod.findings):
    failures.append(f"LIFECYCLE_BODY_CEILING={_lmax_lines - 1} never names "
                     f"{_lmax_label} ({_lmax_lines} lines) — the lifecycle "
                     f"ceiling cannot fail: {mod.findings}")
mod.LIFECYCLE_BODY_CEILING = shipped_lifecycle

# -- and the exemption must be REAL: at a general ceiling below every lifecycle
# node, none of the three may be reported. If they were, they would be paying
# the general ceiling anyway and the decision would be inert.
mod.MACHINERY_BODY_CEILING = min(n for n, _l in _lifecycle) - 1
mod.findings.clear()
mod.check_body_ceiling()
_leaked = [f for f in mod.findings if any(n in f for n in mod.LIFECYCLE_NODES)]
if _leaked:
    failures.append(f"with MACHINERY_BODY_CEILING below every lifecycle node, "
                     f"the lifecycle nodes were still reported — the exemption "
                     f"does not apply: {_leaked}")
mod.MACHINERY_BODY_CEILING = shipped_ceiling

# -- EAGER_BUDGET=20000, EAGER_EXEMPTIONS={} must produce >=4 findings (every
# harness but the already-exempt one, at today's measured surface).
mod.EAGER_BUDGET = 20_000
mod.EAGER_EXEMPTIONS = {}
mod.findings.clear()
mod.check_eager_surface(KERNEL_BYTES)
if len(mod.findings) < 4:
    failures.append(f"EAGER_BUDGET=20000 / EAGER_EXEMPTIONS={{}} produced only "
                     f"{len(mod.findings)} finding(s), expected >=4: {mod.findings}")

# -- the exemption ratchet still has zero slack, proved on a SYNTHETIC entry.
# github-copilot used to sit in EAGER_EXEMPTIONS at 138 535 bytes, because its
# skill projections shipped whole bodies as always-applied context. They are
# pointers now and it came in under the budget, so the ledger is empty and this
# probe can no longer use it. The mechanism still has to be shown to bite: plant
# an exemption one byte under a harness's real figure and require exactly one
# finding naming it.
mod.EAGER_BUDGET = shipped_eager_budget
mod.findings.clear()
mod.EAGER_EXEMPTIONS = {}
mod.check_eager_surface(KERNEL_BYTES)
_baseline = len(mod.findings)
if _baseline != 0:
    failures.append(f"with no exemptions and the shipped budget, every harness "
                     f"should be under: {mod.findings}")
# Recompute one harness's real figure, then exempt it one byte tighter.
_nodes = list(mod.machinery_nodes())
_ad = sum(len(mod.description_of(f)) for l, f, _b in _nodes if l.startswith("agents/"))
_sd = sum(len(mod.description_of(f)) for l, f, _b in _nodes if l.startswith("skills/"))
_claude = KERNEL_BYTES + _ad + _sd
mod.EAGER_EXEMPTIONS = {"claude-code": (_claude - 1, "one byte under the real figure")}
mod.findings.clear()
mod.check_eager_surface(KERNEL_BYTES)
if len(mod.findings) != 1:
    failures.append(f"an exemption one byte under the real figure produced "
                     f"{len(mod.findings)} finding(s), expected exactly 1: {mod.findings}")
elif "RECORDED exemption" not in mod.findings[0]:
    failures.append(f"the one finding does not mention 'RECORDED exemption': {mod.findings[0]}")

if failures:
    for f in failures:
        print("BUDGET-PROBE-FAIL: " + f)
    sys.exit(1)
print("BUDGET-PROBE-OK")
PY
}

PROBE_RC=0
PROBE_OUT="$(run_budget_probe)" || PROBE_RC=$?
printf '%s\n' "$PROBE_OUT"
[[ "$PROBE_RC" -eq 0 ]] || fail "the seed-lint.py budget probe found a non-binding budget (see BUDGET-PROBE-FAIL lines above)"
grep -q "BUDGET-PROBE-OK" <<<"$PROBE_OUT" || fail "budget probe did not report success"

echo "seed-budgets: OK — special-character target paths install cleanly; the general and lifecycle body ceilings, the eager-surface budget, and the zero-slack exemption ratchet all bind"
