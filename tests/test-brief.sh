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
             "protocol.test-first RED names tester", "Write the RED tests §10 names", "graph_route:", "gates:"):
    if want not in out:
        sys.exit(f"  missing: {want}")
for gone in ("produced_by:", "route_evidence:", "- effort:", "- spawn_id:"):
    if gone in out:
        sys.exit(f"  echo field still asked for: {gone}")
for want in ():
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
L="$T/docs/graph/plans/spawns.jsonl"
"$PY" - "$L" <<'PY' && ok "X492 SPAWN_LOG_RECORDS_THE_ATTRIBUTION: each composed brief is logged: spawn_id, role, route, effort" || fail=1
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
r = next(r for r in rows if r["spawn_id"] == "orchestrator.3.tester.1")
assert r["role"] == "tester" and r["route"] == "protocol.test-first RED names tester" and r["effort"] == "medium (row 3)", r
PY
(cd "$T" && "$PY" docs/graph/brief.py --log) | grep -q '^- orchestrator.3.tester.1 — produced_by: tester — route: protocol.test-first RED names tester' \
  && ok "X492 SPAWN_LOG_RECORDS_THE_ATTRIBUTION: --log prints the delivery's attribution lines" || bad "--log" "line missing"
(cd "$T" && "$PY" docs/graph/brief.py --role security --spawn-id o.9.security.1 --task t --route r --emulated "no registered type" --part part.txt >/dev/null && "$PY" docs/graph/brief.py --log) \
  | grep -q '^- o.9.security.1 — produced_by: security — route: r — role-emulated (no registered type)$' \
  && ok "X492 SPAWN_LOG_RECORDS_THE_ATTRIBUTION: an emulated spawn is logged and printed as such" || bad "--emulated" "not in the log"
rc=0; msg="$(cd "$T" && "$PY" docs/graph/brief.py --role architect --spawn-id orchestrator.3.tester.1 --task t --route r --part part.txt 2>&1 >/dev/null)" || rc=$?
[[ $rc -eq 2 ]] && grep -q "already logged for role 'tester'" <<<"$msg" && ok "X492 SPAWN_LOG_RECORDS_THE_ATTRIBUTION: a spawn_id reused for another role is refused" || bad "re-mint" "rc $rc: $msg"
sec="$(cd "$T" && "$PY" docs/graph/brief.py --role security --spawn-id o.9.security.2 --task t --route r --part part.txt)"
"$PY" - "$T/docs/graph/method/security-controls.md" "$sec" "$out" <<'PY' && ok "X495 TRUST_PATH_TAKES_THE_SECURITY_PASS: a security brief carries the SECURITY PATH block byte for byte; no other role's does" || fail=1
import re, sys
block = re.search(r"```\n(SECURITY PATH\n.*?)```", open(sys.argv[1]).read(), re.S)
if not block:
    sys.exit("  no SECURITY PATH block in method/security-controls.md")
if block.group(1) not in sys.argv[2]:
    sys.exit("  the security brief lacks the SECURITY PATH block")
if "SECURITY PATH" in sys.argv[3]:
    sys.exit("  a tester brief carries the SECURITY PATH block")
PY
red="$(cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id o.9.tester.3 --task t --route r --security-path --part part.txt)"
"$PY" - "$T/docs/graph/method/security-controls.md" "$red" "$sec" <<'PY' && ok "X498 SECURITY_CONTRACTS_CARRY_ADVERSARIAL_RED_CONTROLS: a tester brief with --security-path carries the block; it asks one negative control per class, a test per path to a gated effect, and the pass confirms them" || fail=1
import re, sys
block = re.search(r"```\n(SECURITY PATH\n.*?)```", open(sys.argv[1]).read(), re.S).group(1)
if block not in sys.argv[2]:
    sys.exit("  a tester brief with --security-path lacks the SECURITY PATH block")
for want in ("one negative control per class", "n/a: <why>", "import or alias", "helper", "factory",
             "string-built", "comment", "U+2028", "unpinned value", "path to the action's effect",
             "the effect's callers", "confirm"):
    if want not in block:
        sys.exit(f"  the SECURITY PATH block lacks: {want}")
PY
rc=0; (cd "$T" && "$PY" docs/graph/brief.py --role nobody --spawn-id s --task t --route r --part part.txt) >/dev/null 2>&1 || rc=$?
[[ $rc -ne 0 ]] && ok "unknown role refused" || bad "unknown role" "exit 0"
[[ "$fail" == 0 ]] && echo "test-brief: PASS" || { echo "test-brief: FAIL"; exit 1; }
