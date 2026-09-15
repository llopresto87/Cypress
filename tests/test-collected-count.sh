#!/usr/bin/env bash
# A suite may not quietly stop collecting tests.
#
# Nothing counted them. Renaming every `def test_*` in tests/test_agent_lint.py
# that no docs/specs §10 row cites — 27 of 50 — took it from "Ran 69" to
# "Ran 43" with `bash tests/run.sh` still at EXIT=0: seed-lint, spec-lint,
# gate-registry and ratchet-lint were all green over a suite that had lost more
# than a third of its assertions. Only a SPEC-CITED test was held, which is why
# the class looked closed.
#
# The floor is per suite and shrink-only in the wrong direction: it may rise
# freely (write more tests), and lowering one is an edit someone has to make on
# purpose, in `tests/collected.json`, in a diff a reader sees.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK="$ROOT/tests/collected.json"
fails=0
fail() { echo "FAIL: $*" >&2; fails=$((fails + 1)); }

[[ -f "$LOCK" ]] || { echo "FAIL: $LOCK is missing — the floors have no home" >&2; exit 1; }

while IFS=$'\t' read -r suite floor; do
    [[ -n "$suite" ]] || continue
    path="$ROOT/$suite"
    if [[ ! -f "$path" ]]; then
        fail "$suite is recorded in collected.json and no longer exists — a \
floor for a suite nobody runs is a floor nobody can trip."
        continue
    fi
    ran="$(python3 "$path" 2>&1 | grep -oE '^Ran [0-9]+' | grep -oE '[0-9]+' || true)"
    if [[ -z "$ran" ]]; then
        fail "$suite printed no 'Ran N tests' line — it may have stopped being \
a unittest suite, and this check cannot see what it collects."
        continue
    fi
    if (( ran < floor )); then
        fail "$suite collected $ran tests, under its recorded floor of $floor. \
Tests were removed, renamed out of collection, or a class stopped being \
discovered. If the drop is deliberate, lower the floor in tests/collected.json \
in the same change and say why."
    fi
done < <(python3 - "$LOCK" <<'PY'
import json, sys
for suite, floor in sorted(json.load(open(sys.argv[1]))["floors"].items()):
    print(f"{suite}\t{floor}")
PY
)

if (( fails )); then
    echo "collected-count: FAIL — $fails finding(s)" >&2
    exit 1
fi
echo "collected-count: OK — every recorded suite still collects at least its floor"
