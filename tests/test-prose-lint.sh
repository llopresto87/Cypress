#!/usr/bin/env bash
# test-prose-lint.sh — the mechanical floor under the humanizer skill does what
# a reviewer relies on it for:
#   plain technical prose PASSES, and the dashes, the "delve"/"not X but Y" and
#     the tells sitting inside a code fence, a table row or the frontmatter are
#     never reported (the tool lints PROSE, so masking is the whole contract);
#   a planted tell FAILS with file:line and the name of the pattern: the § of
#     the humanizer patterns, the letter of the human-prose diagnostics;
#   one weak tell alone passes, three weak tells in one paragraph fail as a
#     "weak cluster", and --strict fails on a single dash;
#   the dash allowance is a rate: 3/1000 by default, the sample's own rate with
#     --sample, zero under --strict;
#   --against REV proves the rewrite kept its facts — a dropped number, a
#     reworded heading or a downgraded requirement level FAILS, a pure reword
#     PASSES;
#   a scan that matched nothing REFUSES to print a pass (a lint over an empty
#     set is a green lie), and scan() is importable.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINT="$ROOT/tools/prose-lint.py"
FIX="$ROOT/tests/fixtures/prose"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*" >&2; [ -f "$TMP/out" ] && cat "$TMP/out" >&2; exit 1; }

# run <expected-rc> <args...> -> output in $TMP/out
run() {
  local want="$1"; shift
  local rc=0
  python3 "$LINT" "$@" >"$TMP/out" 2>&1 || rc=$?
  [ "$rc" -eq "$want" ] || fail "expected exit $want, got $rc (args: $*)"
}

# 1. Plain technical prose passes, and the summary carries the word count the
#    dash rate is measured against.
run 0 --file "$FIX/clean.md"
grep -q "prose lint: PASS" "$TMP/out" || fail "clean prose did not report PASS"
grep -qE "[0-9]+ words" "$TMP/out" || fail "summary carries no word count"
grep -qE "dashes [0-9.]+/1000" "$TMP/out" || fail "summary carries no dash rate"
grep -q "§" "$TMP/out" && fail "clean prose produced a finding"
echo "  clean prose passes, summary names word count + dash rate — OK"

# 2. Masking is the contract: a code fence, a table row and the frontmatter all
#    hold the exact strings the detectors hunt for (delve, not X but Y, em
#    dashes) and NONE of them may be reported. --strict drops the dash
#    allowance to zero, so a masked dash that leaked would surface here.
run 0 --strict --file "$FIX/clean.md"
grep -q "delve" "$TMP/out" && fail "a word inside a code fence was reported"
grep -q "§8" "$TMP/out" && fail "a dash in a fence/table/frontmatter was counted"
grep -q "§1 " "$TMP/out" && fail "not-X-but-Y inside a code fence was reported"
echo "  fence + table + frontmatter content never reported, even --strict — OK"

# 3. Every planted tell is named with its file, its line and its § number.
run 1 --file "$FIX/telly.md"
grep -q "telly.md:3: §1 strong" "$TMP/out" || fail "§1 not-X-but-Y missed"
grep -q "telly.md:3: §4 strong" "$TMP/out" || fail "§4 staged opener missed"
grep -q "telly.md:5: §12 weak" "$TMP/out" || fail "§12 overused word missed"
[ "$(grep -c "telly.md:5: §12 weak" "$TMP/out")" -ge 2 ] \
  || fail "only one of the two §12 words on line 5 reported"
grep -q "telly.md:9: §19 strong" "$TMP/out" || fail "§19 bold-label run missed"
grep -q "telly.md:13: §22 strong" "$TMP/out" || fail "§22 chatbot residue missed"
grep -q "telly.md:15: W strong" "$TMP/out" || fail "W synthetic friendliness missed"
grep -q "telly.md:17: X strong" "$TMP/out" || fail "X meta-writing residue missed"
grep -q "telly.md:5: §8 strong" "$TMP/out" || fail "§8 dash over the allowance missed"
grep -q "prose lint: FAIL" "$TMP/out" || fail "planted tells did not FAIL"
echo "  planted §1/§4/§8/§12/§19/§22 + W/X each named with file:line — OK"

# 4. A weak tell alone is printed and forgiven; three in one paragraph are a
#    cluster and fail. This is the skill's own "weak alone needs company" rule.
run 0 --file "$FIX/weak-alone.md"
grep -q "§18 weak" "$TMP/out" || fail "the lone weak tell was not printed"
grep -q "prose lint: PASS" "$TMP/out" || fail "a lone weak tell must not fail"
run 1 --file "$FIX/weak-cluster.md"
grep -q "weak cluster" "$TMP/out" || fail "three weak tells in a paragraph not clustered"
grep -q "1 weak cluster(s)" "$TMP/out" || fail "summary did not count the cluster"
echo "  weak alone passes, three in one paragraph fail as a cluster — OK"

# 5. The human-prose diagnostics that count per paragraph rather than per
#    phrase: corporate glaze (E), over-transitioning (K), premature conclusion
#    language (V) and empty intensifiers (S). All four are weak, so they are
#    printed and forgiven alone, fail under --strict, and fail unforgiven once
#    three of them share a paragraph.
run 0 --file "$FIX/glaze.md"
grep -q "glaze.md:3: E weak" "$TMP/out" || fail "E corporate glaze missed"
grep -q "glaze.md:7: K weak" "$TMP/out" || fail "K over-transitioning missed"
grep -q "glaze.md:10: V weak" "$TMP/out" || fail "V premature conclusion missed"
grep -q "prose lint: PASS" "$TMP/out" || fail "weak-only diagnostics must not fail alone"
run 1 --strict --file "$FIX/glaze.md"
run 1 --file "$FIX/intensifiers.md"
grep -q "S weak" "$TMP/out" || fail "S empty intensifiers missed"
grep -q "weak cluster" "$TMP/out" || fail "three intensifiers in a paragraph not clustered"
echo "  E/K/V weak alone, three S intensifiers cluster and fail — OK"

# 6. The dash allowance is a rate, and --strict sets it to zero.
printf '# Note\n\nThe cache keeps the last value — the next read returns it.\n' \
  >"$TMP/one-dash.md"
run 1 --strict --file "$TMP/one-dash.md"
grep -q "§8 strong" "$TMP/out" || fail "--strict did not fail on a single dash"
run 1 --file "$FIX/dashy.md"
grep -q "§8 strong" "$TMP/out" || fail "a dash-heavy file passed the 3/1000 allowance"
run 0 --file "$FIX/dashy.md" --sample "$FIX/sample.md"
grep -q "prose lint: PASS" "$TMP/out" \
  || fail "--sample did not raise the allowance to the sample's own rate"
run 1 --strict --file "$FIX/dashy.md" --sample "$FIX/sample.md"
grep -q "§8 strong" "$TMP/out" || fail "--strict did not override --sample"
echo "  dash rate: 3/1000 default, sample's rate with --sample, 0 --strict — OK"

# 7. --against REV: the humanizer's "check the draft" step, made mechanical. A
#    rewrite may change every sentence; it may not change the facts.
GR="$TMP/repo"
mkdir -p "$GR"
cat >"$GR/doc.md" <<'MD'
# Cache notes

The cache holds 5000 entries and expires each one after 600 seconds.
A miss goes to the renderer, which writes the result back into the store.
A client must send an ETag header on every conditional request.
MD
git -C "$GR" init -q
git -C "$GR" add doc.md
git -C "$GR" -c user.email=t@example.invalid -c user.name=t \
  -c commit.gpgsign=false commit -q -m base

cat >"$GR/doc.md" <<'MD'
# Cache notes

The cache holds 5000 entries, and each one expires after 600 seconds.
On a miss the renderer builds the page, and the result goes back into the store.
A client must send an ETag header on every conditional request.
MD
run 0 --file "$GR/doc.md" --against HEAD
grep -q "prose lint: PASS" "$TMP/out" || fail "a pure reword was reported as fact drift"

cat >"$GR/doc.md" <<'MD'
# Cache notes

The cache holds 5000 entries and expires each one after ten minutes.
A miss goes to the renderer, which writes the result back into the store.
A client must send an ETag header on every conditional request.
MD
run 1 --file "$GR/doc.md" --against HEAD
grep -q "fact drift" "$TMP/out" || fail "a dropped number was not reported as drift"
grep -q "600" "$TMP/out" || fail "the drift report does not name the dropped number"

cat >"$GR/doc.md" <<'MD'
# Cache behaviour

The cache holds 5000 entries and expires each one after 600 seconds.
A miss goes to the renderer, which writes the result back into the store.
A client must send an ETag header on every conditional request.
MD
run 1 --file "$GR/doc.md" --against HEAD
grep -q "fact drift" "$TMP/out" || fail "a reworded heading was not reported as drift"
grep -q "Cache notes" "$TMP/out" || fail "the drift report does not name the heading"

cat >"$GR/doc.md" <<'MD'
# Cache notes

The cache holds 5000 entries and expires each one after 600 seconds.
A miss goes to the renderer, which writes the result back into the store.
A client should send an ETag header on every conditional request.
MD
run 1 --file "$GR/doc.md" --against HEAD
grep -q "requirement level" "$TMP/out" \
  || fail "must -> should was not reported as a requirement-level change"
grep -qE "requirement level.*dropped.*must" "$TMP/out" \
  || fail "the drift report does not name the dropped requirement level"

printf '# Extra\n\nA short paragraph about the store and the keys it holds.\n' \
  >"$GR/new.md"
run 0 --file "$GR/new.md" --against HEAD
grep -q "new in working copy" "$TMP/out" || fail "a file absent from REV was not reported as new"
echo "  --against: reword passes; number, heading, must -> should fail — OK"

# 8. A scan that matched no file must not read as a clean one (exit 2, not 0).
run 2 --root "$FIX" --glob '*.rst'
grep -q "refusing a vacuous pass" "$TMP/out" || fail "empty scan not refused"
grep -q "prose lint: PASS" "$TMP/out" && fail "an empty scan printed a pass line"
run 2 --root "$FIX/does-not-exist"
grep -q "no such path" "$TMP/out" || fail "missing root not refused"
run 2 --file "$FIX/clean.md" --sample "$FIX/does-not-exist.md"
echo "  refuses a vacuous scan, a missing path and a missing sample — OK"

# 9. The reuse contract: scan() is importable, so a host linter renders these
#    findings in its own voice instead of parsing this CLI's output.
python3 - "$LINT" "$FIX" <<'PY' >"$TMP/out" 2>&1 || fail "import contract broken"
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("prose_lint", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fix = Path(sys.argv[2])
rep = mod.scan([fix / "telly.md"], relative_to=fix)
seen = {(f.path, f.line, f.rule, f.severity) for f in rep.findings}
assert ("telly.md", 3, "§1", "strong") in seen, sorted(seen)
assert ("telly.md", 13, "§22", "strong") in seen, sorted(seen)
assert ("telly.md", 5, "§12", "weak") in seen, sorted(seen)
assert rep.words > 0 and rep.dashes >= 4, (rep.words, rep.dashes)
clean = mod.scan([fix / "clean.md"], relative_to=fix)
assert clean.findings == [], clean.findings
print("import contract: OK")
PY
grep -q "import contract: OK" "$TMP/out" || fail "import contract assertions did not run"
echo "  scan() importable, returning structured findings — OK"

echo "test-prose-lint: PASS"

# --- a labelled range is not a connector dash -----------------------------
# The en dash in `T0–T3` or `§1–§12` spans a range, exactly as `2–3` does; only
# the bare-digit form was exempt, so the seed's own canonical notation for its
# tiers and section spans was charged against the §8 rate. That pushes an
# author toward rewriting correct prose to satisfy the meter, which is the one
# thing a prose gate must never reward.
RTMP="$(mktemp -d)"; trap 'rm -rf "$RTMP"' EXIT
cat > "$RTMP/ranges.md" <<'MD'
# Ranges

Every task is classified T0–T3 before acting, and a spec uses the stable
section numbers §1–§12 so tooling can index into it. The plan keeps §0–§15,
and the kernel anchors run §3.1–§3.8. A scout reads 2–3 nodes, no more.
MD
python3 "$LINT" --file "$RTMP/ranges.md" >"$RTMP/out" 2>&1 \
    || { cat "$RTMP/out" >&2; echo "test-prose-lint: FAIL — labelled ranges counted as connector dashes" >&2; exit 1; }
grep -q "dashes 0.0/1000" "$RTMP/out" \
    || { cat "$RTMP/out" >&2; echo "test-prose-lint: FAIL — a range still charged the dash rate" >&2; exit 1; }

# A real en-dash connector still counts: the left side is a word, not an endpoint.
cat > "$RTMP/connector.md" <<'MD'
# Connector

The gate depth follows blast radius – and asserts something – before done.
The router resolves nodes – the few a task needs – then declares the skips.
A worker returns evidence – always – and the session records it in the plan.
MD
python3 "$LINT" --file "$RTMP/connector.md" >"$RTMP/out2" 2>&1 \
    && { cat "$RTMP/out2" >&2; echo "test-prose-lint: FAIL — en-dash connectors stopped counting" >&2; exit 1; }
grep -q "dash as connector" "$RTMP/out2" \
    || { cat "$RTMP/out2" >&2; echo "test-prose-lint: FAIL — the connector was not named" >&2; exit 1; }

echo "test-prose-lint: labelled ranges exempt, connectors still caught — OK"
