#!/usr/bin/env bash
# test-brief.sh — tools/brief.py composes a delegation brief from the plant's
# canonical templates: both bootstrap blocks byte-identical with their slots
# filled, the handback payload block, the charter body only on request, and a
# refusal for an unknown role or an unfilled slot.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
bash "$ROOT/install.sh" claude-code --project-dir "$T" >/dev/null 2>&1
B="$T/docs/graph/brief.py"
fail=0; ok() { echo "  $1 — OK"; }; bad() { echo "  $1 — FAIL: $2"; fail=1; }
[[ -f "$B" ]] && ok "installed at docs/graph/brief.py" || { bad "installed" "missing"; exit 1; }
printf 'Write the RED tests §10 names for increment 2.\n' > "$T/part.txt"
out="$(cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id orchestrator.3.tester.1 \
      --task "write the RED tests for SPEC-0001 increment 2" --route "protocol.test-first RED names tester" \
      --effort "medium (row 3)" --part part.txt)" || { bad "composes" "exit $?"; exit 1; }
"$PY" - "$T" "$out" <<'PY' && ok "blocks byte-identical, slots filled, payload carried" || fail=1
import re, sys
root, out = sys.argv[1], sys.argv[2]
canon = open(f"{root}/docs/graph/templates/prompts/graph-session-bootstrap.md").read()
for name in ("GRAPH DISCIPLINE", "COMPANION"):
    block = re.search(r"```\n(" + name + r".*?)```", canon, re.S).group(1)
    skeleton = re.sub(r"\{\{.*?\}\}", "\x00", block, flags=re.S)
    parts = [re.escape(p) for p in skeleton.split("\x00")]
    if not re.search("(?s)" + ".+?".join(parts), out):
        sys.exit(f"  {name} block not carried byte-identical")
if "{{" in out.split("## Handback", 1)[0]:
    sys.exit("  an unfilled slot reached the brief (the handback fields are the worker's)")
for want in ("orchestrator.3.tester.1", "write the RED tests for SPEC-0001 increment 2",
             "protocol.test-first RED names tester", "Write the RED tests §10 names", "produced_by:", "graph_route:"):
    if want not in out:
        sys.exit(f"  missing: {want}")
PY
grep -q '^name: tester' <<<"$out" && bad "charter off by default" "frontmatter present" || ok "no charter unless asked"
out2="$(cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id s.1 --task t --route r --charter --part part.txt)"
grep -q 'You are the test engineer' <<<"$out2" && ! grep -q '^routing_triggers:' <<<"$out2" \
  && ok "--charter carries the body without frontmatter" || bad "--charter" "body missing or frontmatter kept"
ptr="$(cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id orchestrator.3.tester.1 \
      --task "write the RED tests for SPEC-0001 increment 2" --route "protocol.test-first RED names tester" \
      --part part.txt --out docs/graph/plans/u/briefs/orchestrator.3.tester.1.md)"
[[ $(wc -l <<<"$ptr") -le 3 ]] && grep -q 'docs/graph/plans/u/briefs/orchestrator.3.tester.1.md' <<<"$ptr" \
  && ! grep -q 'GRAPH DISCIPLINE' <<<"$ptr" \
  && grep -q 'GRAPH DISCIPLINE' "$T/docs/graph/plans/u/briefs/orchestrator.3.tester.1.md" \
  && ok "--out writes the brief to the file and prints only a pointer" || bad "--out" "pointer or file wrong"
rc=0; (cd "$T" && "$PY" docs/graph/brief.py --role nobody --spawn-id s --task t --route r --part part.txt) >/dev/null 2>&1 || rc=$?
[[ $rc -ne 0 ]] && ok "unknown role refused" || bad "unknown role" "exit 0"
[[ "$fail" == 0 ]] && echo "test-brief: PASS" || { echo "test-brief: FAIL"; exit 1; }
