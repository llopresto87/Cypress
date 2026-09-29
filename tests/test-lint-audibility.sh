#!/usr/bin/env bash
# test-lint-audibility.sh — V5: no gate skips an input silently. For each tool,
# an unreadable input makes it exit non-zero AND print a diagnostic naming the
# path and the reason. The clean path of each tool is its own suite's case 1.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
. "$ROOT/tests/helpers/lintcase.sh"
T="$(mktemp -d)"
trap 'chmod -R u+w "$T" 2>/dev/null || true; rm -rf "$T"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# make_unreadable PATH — chmod 000; a process running as root still reads it,
# so then fall back to invalid UTF-8, which fails the decode for any owner.
make_unreadable() {
  local f="$1"
  printf 'plain content that would otherwise lint clean\n' >"$f"
  chmod 000 "$f"
  if [ -r "$f" ]; then
    chmod u+w "$f"
    printf '\xff\xfe invalid utf-8, unreadable as text\n' >"$f"
  fi
}

# unread_fails <tool> <path-needle> <rc> -- <cmd...>: exit <rc> (or any non-zero
# for "nz"), and the output names the path and says why.
unread_fails() {
  local tool="$1" needle="$2" want="$3" out rc
  shift 3; [ "${1:-}" = "--" ] && shift
  out="$("$@" 2>&1)" && rc=0 || rc=$?
  if [ "$want" = nz ]; then [ "$rc" -ne 0 ]; else [ "$rc" -eq "$want" ]; fi \
    || fail "$tool: unreadable input should exit $want, got $rc ($out)"
  grep -q "$needle" <<<"$out" || fail "$tool: diagnostic does not name the path ($out)"
  grep -qi "could not be read\|unreadable" <<<"$out" \
    || fail "$tool: diagnostic does not say why ($out)"
  echo "  $tool: unreadable input exits non-zero and names path + reason — OK"
}

# prose-lint
make_unreadable "$T/prose-bad.md"
unread_fails prose-lint "$T/prose-bad.md" 1 -- \
  python3 "$ROOT/tools/prose-lint.py" --file "$T/prose-bad.md"

# status-register
mkdir -p "$T/status"
make_unreadable "$T/status/bad.md"
unread_fails status-register bad.md 1 -- \
  python3 "$ROOT/tools/status-register.py" --root "$T/status"

# spec-lint reads its own location to find docs/graph/specs and tests/, so it
# runs from a scratch tree shaped like a plant.
SPEC="$T/spec"
mkdir -p "$SPEC/docs/graph/specs" "$SPEC/tests"
cp "$ROOT/templates/knowledge-graph/spec-lint.py" "$SPEC/docs/graph/spec-lint.py"
cat >"$SPEC/docs/graph/specs/SPEC-0001-thing.md" <<'MD'
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
make_unreadable "$SPEC/tests/test_thing.py"
unread_fails spec-lint test_thing.py 1 -- \
  bash -c 'cd "$1" && python3 docs/graph/spec-lint.py' _ "$SPEC"

# agnosticism-lint: DEFAULT_GLOBS is *.md, so a skipped read was always a page.
mkdir -p "$T/agn"
printf '# ordinary page\nnothing forbidden here.\n' >"$T/agn/ok.md"
make_unreadable "$T/agn/bad.md"
unread_fails agnosticism-lint bad.md nz -- \
  python3 "$ROOT/tools/agnosticism-lint.py" --root "$T/agn"

# roster-justification (a gate step): an unreadable node must also leave the
# denominator visibly ("of N" drops by one), not silently. It walks the real
# roster, so it runs on a copy of only what it reads.
RJ="$T/rjcopy"
mini_tree "$RJ" tools/roster-justification.py tools/frontmatter.py \
  agents protocols skills core/method
out="$(python3 "$RJ/tools/roster-justification.py" --gaps 2>&1)" && rc=0 || rc=$?
[ "$rc" -eq 0 ] || fail "roster-justification: a clean copy must pass, got $rc ($out)"
clean_count="$(sed -n 's/^.*of \([0-9][0-9]*\).*$/\1/p' <<<"$out")"
[ -n "$clean_count" ] || fail "roster-justification: no node count in the clean run ($out)"
make_unreadable "$RJ/agents/05-security.md"
unread_fails roster-justification 05-security.md nz -- \
  python3 "$RJ/tools/roster-justification.py" --gaps
out="$(python3 "$RJ/tools/roster-justification.py" --gaps 2>&1)" || true
grep -q "of $((clean_count - 1))" <<<"$out" \
  || fail "roster-justification: total should drop to $((clean_count - 1)) ($out)"
echo "  roster-justification: the unreadable node leaves the total visibly — OK"

echo "test-lint-audibility: PASS"
