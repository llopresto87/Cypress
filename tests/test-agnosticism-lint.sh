#!/usr/bin/env bash
# test-agnosticism-lint.sh — the shared agnosticism gate does what any
# project-agnostic tree adopting it relies on:
#   a clean tree PASSES (documentation/loopback addresses are not leaks);
#   a leaked host address or pinned advisory FAILS with file:line and the term;
#   --forbid is caller-supplied, repeatable, case-insensitive and substring —
#     the same file passes with no --forbid and fails with one;
#   --glob/--file scope the scan — a bare --file scans that file and nothing
#     else — and a scan that matched nothing REFUSES to print a pass (a lint
#     over an empty set is a green lie);
#   scan()/iter_files() are importable, which is how tests/seed-lint.py runs
#     this check instead of keeping a second copy of it.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINT="$ROOT/tools/agnosticism-lint.py"
FIX="$ROOT/tests/fixtures/agnosticism"
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

# 1. A clean tree passes, recursively, and the addresses an example is
#    entitled to use (RFC 5737 documentation ranges, loopback, unspecified)
#    are not reported as leaks.
run 0 --root "$FIX/clean"
grep -q "agnosticism lint: PASS" "$TMP/out" || fail "clean tree did not report PASS"
grep -q "2 file(s) scanned" "$TMP/out" || fail "did not recurse into the nested file"
grep -q "leaked host-IP" "$TMP/out" && fail "a documentation/loopback address was reported as a leak"
echo "  clean tree passes; documentation + loopback addresses allowed — OK"

# 2. A leaked host address and a pinned advisory fail, each naming the file,
#    the line, and the offending term.
run 1 --root "$FIX/leaky"
grep -q "doc.md:3: leaked host-IP literal '198.18.7.42'" "$TMP/out" \
  || fail "host-IP finding missing its file:line + term"
grep -q "doc.md:6: pinned advisory 'CVE-2031-99999'" "$TMP/out" \
  || fail "advisory finding missing its file:line + term"
grep -q "FAIL (2 finding(s))" "$TMP/out" || fail "expected exactly 2 findings"
echo "  leaked address + pinned advisory fail with file:line + term — OK"

# 3. --glob scopes the scan and is repeatable: the same tree's .txt leak is
#    invisible under the default *.md and reported once *.txt is asked for.
grep -q "notes.txt" "$TMP/out" && fail "*.txt scanned under the default *.md glob"
run 1 --root "$FIX/leaky" --glob '*.md' --glob '*.txt'
grep -q "notes.txt:1: leaked host-IP literal '198.18.7.43'" "$TMP/out" \
  || fail "repeated --glob did not reach the second pattern"
echo "  --glob scopes the scan and is repeatable — OK"

# 4. --file scans one file whatever --glob says — and ONLY that file. A bare
#    --file once fell through to the "." default and silently scanned the whole
#    tree: a gate that widens its own scope reports findings the caller never
#    asked about, and hides which ones it was asked about.
run 1 --file "$FIX/leaky/notes.txt"
grep -q "notes.txt:1: leaked host-IP" "$TMP/out" || fail "--file did not scan the named file"
grep -q "1 file(s) scanned" "$TMP/out" && fail "unreachable: rc=1 prints no summary"
run 0 --file "$FIX/clean/doc.md"
grep -q "1 file(s) scanned" "$TMP/out" \
  || fail "bare --file widened the scan beyond the named file"
echo "  --file scans a named file regardless of --glob, and only it — OK"

# 5. Forbidden terms are the CALLER's: with none passed, a page full of one
#    project's names is clean — the tool never guesses an identity.
run 0 --root "$FIX/named"
echo "  no --forbid: project terms are not invented by the tool — OK"

# 6. --forbid is repeatable, and matches case-insensitively as a substring —
#    fail-closed, so a token also catches the compounds built from it.
run 1 --root "$FIX/named" --forbid widgetco --forbid j.doe
grep -q "doc.md:3: project-identifying term 'widgetco'" "$TMP/out" \
  || fail "first --forbid term not reported with file:line"
grep -q "doc.md:5: project-identifying term 'widgetco'" "$TMP/out" \
  || fail "term inside a path not reported"
grep -q "doc.md:5: project-identifying term 'j.doe'" "$TMP/out" \
  || fail "second --forbid term not reported (repeatable flag dropped?)"
grep -q "doc.md:7: project-identifying term 'WidgetCo'" "$TMP/out" \
  || fail "case-insensitive substring match missed"
grep -q "FAIL (4 finding(s))" "$TMP/out" || fail "expected exactly 4 findings"
echo "  --forbid repeatable, case-insensitive, substring, file:line — OK"

# 7. A scan that matched no file must not read as a clean one (exit 2, not 0):
#    a mistyped --glob would otherwise print the PASS a real scan earns.
run 2 --root "$FIX/clean" --glob '*.rst'
grep -q "refusing a vacuous pass" "$TMP/out" || fail "empty scan not refused"
run 2 --root "$FIX/does-not-exist"
grep -q "no such path" "$TMP/out" || fail "missing root not refused"
echo "  refuses a vacuous scan and a missing path (exit 2) — OK"

# 8. The reuse contract: seed-lint imports this file by path and renders the
#    findings itself. If scan()/iter_files() move or change shape, the seed's
#    own gate loses its agnosticism check silently.
python3 - "$LINT" "$FIX/leaky" <<'PY' >"$TMP/out" 2>&1 || fail "import contract broken"
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("agnosticism_lint", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
root = Path(sys.argv[2])
files = mod.iter_files([root])
assert [f.name for f in files] == ["doc.md"], files
found = mod.scan([root], relative_to=root)
assert [(f.path, f.line, f.rule) for f in found] == [
    ("doc.md", 3, "host-ip"), ("doc.md", 6, "advisory")], found
assert found[0].message.startswith("leaked host-IP literal"), found[0]
print("import contract: OK")
PY
grep -q "import contract: OK" "$TMP/out" || fail "import contract assertions did not run"
echo "  scan()/iter_files() importable — the seed-lint reuse contract — OK"

echo "test-agnosticism-lint: PASS"
