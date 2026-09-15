#!/usr/bin/env bash
# Every shipped tool answers `--help` on its own terms.
#
# U-10 recorded that `graft-audit.py --help` exited 2 through the unknown-option
# path. Fixing that one file closed the instance: a sweep found `growth-audit.py`
# emitting the entry's own quoted string ("!! unknown option --help") from the
# same directory with the same idiom, `graft-graph-engine.py` printing its
# docstring and then exiting 2 anyway, and `check-coverage-binder.py` taking
# `--help` as a PATH and dying with a FileNotFoundError traceback.
#
# The defect is not any one tool, so neither is the check: this walks the tool
# directories and holds all of them, which means a tool added later is covered
# without anyone remembering.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fails=0
checked=0
fail() { echo "FAIL: $*" >&2; fails=$((fails + 1)); }

# Tools a user is pointed at. Library modules (no CLI) are excluded by the
# `__main__` test below rather than by a hand-kept list.
while IFS= read -r tool; do
    grep -q '__name__ == "__main__"' "$tool" || continue
    # Hooks are invoked BY a harness with a JSON payload on stdin, never by a
    # person with flags; they are excluded here by shape rather than by name so
    # a new tool does not have to be remembered into this sweep.
    case "$tool" in *-hook.py) continue ;; esac
    checked=$((checked + 1))
    rel="${tool#$ROOT/}"
    # `< /dev/null`, or the tool inherits this loop's stdin and eats the file
    # list: the first version of this sweep checked 2 tools of 17 and said OK,
    # which is the same false green it exists to catch.
    out="$(cd "$ROOT" && python3 "$tool" --help </dev/null 2>&1)" && rc=0 || rc=$?
    if [[ $rc -ne 0 ]]; then
        fail "$rel --help exited $rc. A shipped CLI must answer --help rather \
than route it into the unknown-option path or treat it as an argument."
        continue
    fi
    [[ -n "$out" ]] || fail "$rel --help exited 0 and printed nothing"
done < <(find "$ROOT/tools" "$ROOT/templates/knowledge-graph" \
              "$ROOT/integrations" -name '*.py' -not -path '*/__pycache__/*' \
              2>/dev/null | sort)

[[ $checked -gt 10 ]] || fail "only $checked tool(s) discovered — the sweep is not reaching them"

if (( fails )); then
    echo "tool-help: FAIL — $fails finding(s) across $checked tool(s)" >&2
    exit 1
fi
echo "tool-help: OK — $checked shipped tools answer --help"
