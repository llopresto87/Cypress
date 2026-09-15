#!/usr/bin/env bash
# test-lint-audibility.sh — V5: no gate skips an input silently. Three
# linters used to catch an unreadable file (bad permissions, bad encoding,
# a race with something deleting it) with a bare `except: continue` — no
# diagnostic, no effect on exit status, so a gate that could not even read
# its input still printed the same PASS a real scan earns. This proves the
# fix for all three: prose-lint.py, status-register.py, spec-lint.py.
#   For each: an unreadable input makes the tool exit non-zero AND print a
#   diagnostic naming the path and the reason; a clean, readable input
#   still passes exactly as before.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T="$(mktemp -d)"
trap 'chmod -R u+w "$T" 2>/dev/null || true; rm -rf "$T"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# make_unreadable PATH — plant a file the tool cannot read. chmod 000 is
# preferred (it exercises the real OSError a gate hits in CI), but a
# process running as root ignores permission bits, which would make the
# whole test vacuous — it would "pass" without ever exercising the fix. So
# after chmod 000 we check whether the file actually became unreadable to
# us; if not (root, or some other override), fall back to an invalid UTF-8
# byte sequence, which triggers UnicodeDecodeError instead and is immune
# to who owns the process.
make_unreadable() {
  local f="$1"
  printf 'plain content that would otherwise lint clean\n' >"$f"
  chmod 000 "$f"
  if [ -r "$f" ]; then
    chmod u+w "$f"
    printf '\xff\xfe invalid utf-8, unreadable as text\n' >"$f"
  fi
}

# ---------------------------------------------------------------- prose-lint
PROSE_BAD="$T/prose-bad.md"
make_unreadable "$PROSE_BAD"
out="$(python3 "$ROOT/tools/prose-lint.py" --file "$PROSE_BAD" 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 1 ] || fail "prose-lint: unreadable input should exit 1, got $rc ($out)"
grep -q "$PROSE_BAD" <<<"$out" || fail "prose-lint: diagnostic does not name the path ($out)"
grep -qi "unreadable" <<<"$out" || fail "prose-lint: diagnostic does not say why ($out)"
echo "  prose-lint: unreadable input exits non-zero and names path + reason — OK"

out="$(python3 "$ROOT/tools/prose-lint.py" --file "$ROOT/tests/fixtures/prose/clean.md" 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 0 ] || fail "prose-lint: a clean file must still pass, got $rc ($out)"
grep -q "prose lint: PASS" <<<"$out" || fail "prose-lint: clean file did not report PASS"
echo "  prose-lint: a clean readable file still passes — OK"

# ------------------------------------------------------------ status-register
STATUS_ROOT="$T/status"
mkdir -p "$STATUS_ROOT"
make_unreadable "$STATUS_ROOT/bad.md"
out="$(python3 "$ROOT/tools/status-register.py" --root "$STATUS_ROOT" 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 1 ] || fail "status-register: unreadable input should exit 1, got $rc ($out)"
grep -q "bad.md" <<<"$out" || fail "status-register: diagnostic does not name the path ($out)"
grep -qi "unreadable" <<<"$out" || fail "status-register: diagnostic does not say why ($out)"
echo "  status-register: unreadable input exits non-zero and names path + reason — OK"

out="$(python3 "$ROOT/tools/status-register.py" --root "$ROOT/tests/fixtures/status/clean" 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 0 ] || fail "status-register: a clean tree must still pass, got $rc ($out)"
grep -q "status register: PASS" <<<"$out" || fail "status-register: clean tree did not report PASS"
echo "  status-register: a clean readable tree still passes — OK"

# ----------------------------------------------------------------- spec-lint
# spec-lint.py reads its own location to find docs/graph/{specs,../../tests}
# (it is installed at docs/graph/spec-lint.py in a plant), so each case gets
# its own scratch tree shaped the same way.
spec_tree() {  # spec_tree DIR — a minimal live spec with one covered contract
  local dir="$1"
  mkdir -p "$dir/docs/graph/specs" "$dir/tests"
  cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$dir/docs/graph/spec-lint.py"
  cat >"$dir/docs/graph/specs/SPEC-0001-thing.md" <<'MD'
---
status: active
status_date: 2026-09-13
---

# Thing

## 0. Metadata
- **Status:** see frontmatter (single home)
- **Sign-offs:** product [x] · architect [x] · tester [x] · security [ ]

## 4. Functional contracts

### Contract: DO_THING
- **Given:** a
- **When:** b
- **Then:** c

## 7. Failure modes

### Failure: THING_FAILS
- **Trigger:** x

## 9. Acceptance criteria

- [ ] AC-1: does the thing — maps to DO_THING

## 10. Test mapping

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| DO_THING | test_do_thing | tests/test_thing.py | unit | green |
MD
}

SPEC_BAD="$T/spec-bad"
spec_tree "$SPEC_BAD"
make_unreadable "$SPEC_BAD/tests/test_thing.py"
out="$(cd "$SPEC_BAD" && python3 docs/graph/spec-lint.py 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 1 ] || fail "spec-lint: unreadable test file should exit 1, got $rc ($out)"
grep -q "test_thing.py" <<<"$out" || fail "spec-lint: diagnostic does not name the path ($out)"
grep -qi "unreadable" <<<"$out" || fail "spec-lint: diagnostic does not say why ($out)"
echo "  spec-lint: unreadable test file exits non-zero and names path + reason — OK"

SPEC_CLEAN="$T/spec-clean"
spec_tree "$SPEC_CLEAN"
printf 'def test_do_thing():  # DO_THING\n    pass\n' >"$SPEC_CLEAN/tests/test_thing.py"
out="$(cd "$SPEC_CLEAN" && python3 docs/graph/spec-lint.py 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 0 ] || fail "spec-lint: a clean, covered spec must still pass, got $rc ($out)"
grep -q "spec lint: PASS" <<<"$out" || fail "spec-lint: clean tree did not report PASS"
echo "  spec-lint: a clean, covered spec still passes — OK"

# --- agnosticism-lint ------------------------------------------------------
# The fourth instance of the same defect, and the one that says the most about
# how it survived: the ledger named three linters, the audit that fixed them was
# told three, and this one was found only because a second pass was not given
# the list. Its skip even carried a rationale — "binary or unreadable: carries
# no prose" — while DEFAULT_GLOBS is ("*.md",), so the only thing it could skip
# was a markdown file it failed to read. A stale reason reads exactly like a
# considered one.
AGN_DIR="$T/agn"
mkdir -p "$AGN_DIR"
printf '# ordinary page\nnothing forbidden here.\n' >"$AGN_DIR/ok.md"
AGN_BAD="$AGN_DIR/bad.md"
printf 'placeholder\n' >"$AGN_BAD"
make_unreadable "$AGN_BAD"
out="$(python3 "$ROOT/tools/agnosticism-lint.py" --root "$AGN_DIR" 2>&1)" && rc=0 || rc=$?
[ "$rc" -ne 0 ] || fail "agnosticism-lint: an unreadable page must not pass, got 0 ($out)"
grep -q "bad.md" <<<"$out" || fail "agnosticism-lint: the diagnostic must name the path ($out)"
grep -qi "could not be read\|unreadable" <<<"$out" \
    || fail "agnosticism-lint: the diagnostic must give the reason ($out)"
echo "  agnosticism-lint: unreadable page exits non-zero and names path + reason — OK"

out="$(python3 "$ROOT/tools/agnosticism-lint.py" --file "$AGN_DIR/ok.md" 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 0 ] || fail "agnosticism-lint: a clean page must still pass, got $rc ($out)"
echo "  agnosticism-lint: a clean page still passes — OK"

# 5. roster-justification.py — the fifth instance, and the one in a GATE STEP.
#
# Found after the other four were fixed, in a tool this same release wired into
# run.sh. Its reader turned both FrontmatterError and OSError into `{}` and the
# caller `continue`d, so an unreadable node left the DENOMINATOR: "0 node(s)
# with a gap, of 60" became "0 node(s) with a gap, of 59", exit 0, no
# diagnostic. Three reference documents publish this tool as the home for why
# each node is on the roster.
#
# It needs the real tree (it walks protocols/, skills/, agents/, method/), so
# this runs against a throwaway copy rather than a fixture.
RJ="$T/rjcopy"
mkdir -p "$RJ"
( cd "$ROOT" && tar --exclude=.git --exclude=__pycache__ --exclude='*.pyc' -cf - . ) \
    | ( cd "$RJ" && tar -xf - )
out="$(python3 "$RJ/tools/roster-justification.py" --gaps 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 0 ] || fail "roster-justification: a clean copy must pass, got $rc ($out)"
make_unreadable "$RJ/agents/05-security.md"
out="$(python3 "$RJ/tools/roster-justification.py" --gaps 2>&1)" && rc=0 || rc=$?
[ "$rc" -ne 0 ] || fail "roster-justification: an unreadable node must not pass, got 0 ($out)"
grep -q "05-security.md" <<<"$out" \
    || fail "roster-justification: the diagnostic must name the path ($out)"
grep -qi "could not be read\|unreadable" <<<"$out" \
    || fail "roster-justification: the diagnostic must give the reason ($out)"
grep -q "of 59" <<<"$out" \
    || fail "roster-justification: the count should still show the node is missing ($out)"
echo "  roster-justification: unreadable node exits non-zero and names path + reason — OK"

echo "test-lint-audibility: PASS"
