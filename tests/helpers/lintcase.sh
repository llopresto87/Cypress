# lintcase.sh: small case helpers for the shell suites. Source it; needs bash.
#   expect_rc <rc> <needle> -- <cmd...>  run cmd; fail unless it exits <rc> and
#                                        its output holds <needle> ("" = any)
#   mini_tree <dst> <paths...>           copy only the named seed paths (relative
#                                        to the seed root) into <dst>
#   collect_case <label> <fn> <what>     run one case, print its own result
LINTCASE_SEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

expect_rc() {
  local want="$1" needle="$2" out rc
  shift 2; [ "${1:-}" = "--" ] && shift
  out="$("$@" 2>&1)" && rc=0 || rc=$?
  [ "$rc" -eq "$want" ] || { echo "exit $rc, want $want: $* :: ${out:0:600}"; return 1; }
  [ -z "$needle" ] || case "$out" in *"$needle"*) ;; *)
    echo "output lacks '$needle': $* :: ${out:0:600}"; return 1 ;; esac
}

mini_tree() {
  local dst="$1" p; shift
  for p in "$@"; do
    [ -e "$LINTCASE_SEED_ROOT/$p" ] || { echo "mini_tree: no $p in the seed" >&2; return 1; }
    mkdir -p "$dst/$(dirname "$p")" && cp -a "$LINTCASE_SEED_ROOT/$p" "$dst/$p"
  done
}

# collect_case runs a case function in a command substitution (a subshell): it
# prints `  <label> <what> — OK`, or `FAIL <label>: <why>` and sets
# CASE_FAILED=1, so one red case never hides the next. A case that starts with
# `set -e` fails on its first failing command. Cases run in call order; a later
# case may build on files an earlier one left. The suite checks CASE_FAILED at
# its end.
CASE_FAILED=0
collect_case() {
  local why rc
  set +e; why="$("$2" 2>&1)"; rc=$?; set -e
  if [ "$rc" -eq 0 ]; then
    echo "  $1 $3 — OK"
  else
    echo "FAIL $1 (exit $rc): $why" >&2
    CASE_FAILED=1
  fi
}
