#!/usr/bin/env bash
# Every shipped tool answers `--help` on its own terms, on the Python floor
# (E19, SPEC-0001 HOOKS_RUN_ON_THE_FLOOR_INTERPRETER).
#
# U-10 recorded that `graft-audit.py --help` exited 2 through the unknown-option
# path. Fixing that one file closed the instance: a sweep found `growth-audit.py`
# emitting the entry's own quoted string ("!! unknown option --help") from the
# same directory with the same idiom, and `graft-graph-engine.py` printing its
# docstring and then exiting 2 anyway.
#
# The defect is not any one tool, so neither is the check: this walks the tool
# directories and holds all of them, which means a tool added later is covered
# without anyone remembering.
#
# The interpreter is the floor's, found the way install.sh finds it
# (SPEC-0001 HOOKS_RUN_ON_THE_FLOOR_INTERPRETER): `python3` when it is at the
# floor, else the first `python3.<n>` at or above it. A plant runs these scripts
# on that interpreter, so a construct the floor does not parse fails here and
# not in a plant. The floor's one home is SPEC-0005 §5 "Compatibility";
# install.sh carries the copy it resolves by, and this check holds the two
# equal. Every shipped script, the hooks included, must also compile on it.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fails=0
checked=0
fail() { echo "FAIL: $*" >&2; fails=$((fails + 1)); }

FLOOR="$(sed -n 's/^PYTHON_FLOOR="\([0-9]*\.[0-9]*\)"$/\1/p' "$ROOT/install.sh")"
[[ -n "$FLOOR" ]] || { echo "FAIL: install.sh declares no PYTHON_FLOOR" >&2; exit 1; }
grep -qF "The seed's minimum Python is $FLOOR" "$ROOT/docs/specs/SPEC-0005-cycle-economy.md" \
    || fail "install.sh's PYTHON_FLOOR ($FLOOR) is not the floor SPEC-0005 §5 states, the floor's one home"

PY=""
major="${FLOOR%%.*}"; minor="${FLOOR#*.}"
for cand in python3 $(n=0; while [[ $n -lt 10 ]]; do printf 'python%s.%s ' "$major" $((minor + n)); n=$((n + 1)); done); do
    command -v "$cand" >/dev/null 2>&1 || continue
    "$cand" -c "import sys; sys.exit(0 if sys.version_info >= ($major, $minor) else 1)" >/dev/null 2>&1 || continue
    PY="$cand"; break
done
if [[ -z "$PY" ]]; then
    echo "tool-help: SKIPPED — no Python $FLOOR or newer on PATH (python3 or python$FLOOR); the floor is not checked here"
    exit 0
fi

# Tools a user is pointed at. Library modules (no CLI) are excluded by the
# `__main__` test below rather than by a hand-kept list.
compiled=0
while IFS= read -r tool; do
    rel="${tool#$ROOT/}"
    # Every shipped script parses on the floor, hooks and library modules
    # included: a hook dies silently behind `|| true` when it does not.
    "$PY" -c 'import sys; compile(open(sys.argv[1], encoding="utf-8").read(), sys.argv[1], "exec")' \
        "$tool" </dev/null 2>/dev/null || fail "$rel does not compile on $PY (Python $FLOOR floor)"
    compiled=$((compiled + 1))
    grep -q '__name__ == "__main__"' "$tool" || continue
    # Hooks are invoked BY a harness with a JSON payload on stdin, never by a
    # person with flags; they are excluded here by shape rather than by name so
    # a new tool does not have to be remembered into this sweep.
    case "$tool" in *-hook.py) continue ;; esac
    checked=$((checked + 1))
    # `< /dev/null`, or the tool inherits this loop's stdin and eats the file
    # list: the first version of this sweep checked 2 tools of 17 and said OK,
    # which is the same false green it exists to catch.
    out="$(cd "$ROOT" && "$PY" "$tool" --help </dev/null 2>&1)" && rc=0 || rc=$?
    if [[ $rc -ne 0 ]]; then
        fail "$rel --help exited $rc on $PY. A shipped CLI must answer --help rather \
than route it into the unknown-option path or treat it as an argument."
        continue
    fi
    [[ -n "$out" ]] || fail "$rel --help exited 0 and printed nothing"
done < <(find "$ROOT/tools" "$ROOT/templates/knowledge-graph" \
              "$ROOT/integrations" -name '*.py' -not -path '*/__pycache__/*' \
              2>/dev/null | sort)

[[ $checked -gt 10 ]] || fail "only $checked tool(s) discovered — the sweep is not reaching them"

if (( fails )); then
    echo "tool-help: FAIL — $fails finding(s) across $checked tool(s) on $PY" >&2
    exit 1
fi
echo "tool-help: OK — $compiled shipped scripts compile and $checked tools answer --help on $PY (floor $FLOOR)"
