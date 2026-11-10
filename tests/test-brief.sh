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
for want in ("compiled", "executed (", "statically inspected", "device-tested", "deferred (", "what it ran"):
    if want not in out:
        sys.exit(f"  missing: {want}")
PY
grep -q '^name: tester' <<<"$out" && bad "charter off by default" "frontmatter present" || ok "no charter unless asked"
rc=0; msg="$(cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id s.0 --task t --route r --charter --part part.txt 2>&1 >/dev/null)" || rc=$?
[[ $rc -eq 2 ]] && grep -q "Prime Agent" <<<"$msg" \
  && ok "X501 CHARTER_FLAG_ONLY_FOR_PRIME_AGENT: --charter is refused where .claude/agents/ carries the role" \
  || bad "X501 CHARTER_FLAG_ONLY_FOR_PRIME_AGENT" "rc $rc: $msg"
mkdir -p "$T/.prime/agent"
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
  | grep -q '^- o.9.security.1 — produced_by: security — route: r — effort: high (security path) — role-emulated (no registered type)$' \
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
             "the effect's callers", "confirm", "every input channel", "assistive technology",
             "every state change", "recreation"):
    if want not in block:
        sys.exit(f"  the SECURITY PATH block lacks: {want}")
PY
# X500 PLAN_ROLE_LEAVES_OUT_THE_ROLES_OWN_PROMPT: step 1 routes with the
# worker's role, and the caller hears when a task line routes no expertise
grep -q -- '--plan "write the RED tests for SPEC-0001 increment 2" --role tester' <<<"$out" \
  && ok "X500 PLAN_ROLE_LEAVES_OUT_THE_ROLES_OWN_PROMPT: step 1 carries --role <role>" || bad "X500 --role" "step 1 lacks --role tester"
err="$(cd "$T" && "$PY" docs/graph/brief.py --role implementer --spawn-id o.9.implementer.1 \
      --task "make the increment 15 tests pass (GREEN)" --route r --part part.txt 2>&1 >/dev/null)"
grep -q "routes no expertise" <<<"$err" \
  && ok "X500 BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE: a generic task line is named to the caller" \
  || bad "X500 BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE" "no warning: $err"
printf -- '---\nid: expertise.widget\ntier: 2\nkind: expertise\norigin: project\ntitle: widget\nowns:\n  - widget.applicability\nload_when:\n  - "widget toolkit screen"\nest_tokens: 100\n---\n\nWidget.\n' \
  > "$T/docs/graph/nodes/expertise.widget.md"
err="$(cd "$T" && "$PY" docs/graph/brief.py --role implementer --spawn-id o.9.implementer.2 \
      --task "make the widget toolkit screen tests pass" --route r --part part.txt 2>&1 >/dev/null)"
grep -q "routes no expertise" <<<"$err" \
  && bad "X500 BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE" "warned on a task line that routes expertise.widget: $err" \
  || ok "X500 BRIEF_WARNS_ON_A_ROUTE_WITHOUT_EXPERTISE: a task line that routes expertise composes quietly"
rm -f "$T/docs/graph/nodes/expertise.widget.md"
# X502 BRIEF_DERIVES_THE_SPAWN_EFFORT: the role and task kind (and the
# increment's label) give the spawn's effort, printed to the caller and logged
eff() { (cd "$T" && "$PY" docs/graph/brief.py --spawn-id "o.9.eff.$1" --task t --route r --part part.txt "${@:2}" 2>&1 >/dev/null) || return $?; }
x502=0
for row in "1|effort: low (reviewer recheck)|--role reviewer --kind recheck" \
           "2|effort: medium (implementer increment, label hard)|--role implementer --kind increment --label hard" \
           "2e|effort: low (implementer increment, label medium-hard)|--role implementer --kind increment --label medium-hard" \
           "2f|effort: low (implementer increment, label medium)|--role implementer --kind increment --label medium" \
           "2g|effort: low (implementer increment)|--role implementer --kind increment" \
           "2b|effort: high (tester red, label hard)|--role tester --kind red --label hard" \
           "2c|effort: low (implementer flow)|--role implementer --kind flow" \
           "2d|effort: low (implementer fix)|--role implementer --kind fix" \
           "2h|effort: low (implementer fix, over trust)|--role implementer --kind trust,fix" \
           "2i|effort: low (implementer trust)|--role implementer --kind trust" \
           "2j|effort: low (tester amend, over red-trust)|--role tester --kind red-trust,amend" \
           "3|effort: low (implementer increment, label medium-low)|--role implementer --kind increment --label medium-low" \
           "4|effort: medium (architect ruling)|--role architect --kind ruling" \
           "5|effort: high (security path)|--role tester --kind red --security-path" \
           "5b|effort: medium (tester findings)|--role tester --kind findings --security-path" \
           "5c|effort: high (security path)|--role security --kind findings" \
           "6|effort: medium (tester definition default)|--role tester"; do
  IFS='|' read -r n want args <<<"$row"
  # shellcheck disable=SC2086
  got="$(eff "$n" $args)" || true
  grep -qF "$want" <<<"$got" || { bad "X502 BRIEF_DERIVES_THE_SPAWN_EFFORT" "fixture $n: want '$want', got: $got"; x502=1; }
done
"$PY" - "$T/docs/graph/plans/spawns.jsonl" <<'PY' || { bad "X502 BRIEF_DERIVES_THE_SPAWN_EFFORT" "derived effort not logged"; x502=1; }
import json, sys
rows = {r["spawn_id"]: r for r in map(json.loads, open(sys.argv[1]))}
assert rows["o.9.eff.1"]["effort"] == "low (reviewer recheck)", rows.get("o.9.eff.1")
PY
rc=0; msg="$(eff 7 --role reviewer --kind sweep)" || rc=$?
[[ $rc -eq 2 ]] && grep -q "recheck" <<<"$msg" || { bad "X502 BRIEF_DERIVES_THE_SPAWN_EFFORT" "unknown kind: rc $rc: $msg"; x502=1; }
[[ $x502 == 0 ]] && ok "X502 BRIEF_DERIVES_THE_SPAWN_EFFORT: role, kind and label give the effort, printed and logged; an unknown kind is refused"
# X503 REVIEW_BRIEF_NAMES_THE_SECURITY_PASS: a reviewer brief over a trust
# path tells the caller the security pass is owed, and --log blocks until a
# security spawn follows that review
printf -- '---\nid: crosscut.gate\ntier: 2\ntrust: true\nkind: crosscut\norigin: project\ntitle: gate\nowns:\n  - gate.menu\nload_when:\n  - "app/trusted/**"\nest_tokens: 100\n---\n\nGate.\n' \
  > "$T/docs/graph/nodes/crosscut.gate.md"
mkdir -p "$T/app/trusted" "$T/app/ui"
printf 'class Session:\n    pass\n' > "$T/app/trusted/session.py"; printf 'class Page:\n    pass\n' > "$T/app/ui/page.py"
git -C "$T/app" init -q && git -C "$T/app" add -A && git -C "$T/app" -c user.email=t@t -c user.name=t commit -qm base
printf 'class Gate:\n    pass\n' > "$T/app/trusted/gate.py"
printf 'Review the diff; the session is app/trusted/session.py.\n' > "$T/rev.txt"
printf 'Review app/ui/page.py.\n' > "$T/rev-ui.txt"
x503=0
err="$(cd "$T" && "$PY" docs/graph/brief.py --role reviewer --kind first --spawn-id o.9.reviewer.1 --task t --route r --part rev.txt 2>&1 >/dev/null)" || true
grep -q "SECURITY PASS REQUIRED after this review: app/trusted/gate.py, app/trusted/session.py" <<<"$err" \
  && grep -qF "effort: high (reviewer first-trust)" <<<"$err" \
  || { bad "X503 REVIEW_BRIEF_NAMES_THE_SECURITY_PASS" "no or wrong line: $err"; x503=1; }
rm "$T/app/trusted/gate.py"
err="$(cd "$T" && "$PY" docs/graph/brief.py --role reviewer --kind first --spawn-id o.9.reviewer.2 --task t --route r --part rev-ui.txt 2>&1 >/dev/null)" || true
grep -q "SECURITY PASS" <<<"$err" && { bad "X503 REVIEW_BRIEF_NAMES_THE_SECURITY_PASS" "named for a non-trust diff: $err"; x503=1; }
rc=0; msg="$(cd "$T" && "$PY" docs/graph/brief.py --log 2>&1 >/dev/null)" || rc=$?
[[ $rc -eq 1 ]] && grep -q "BLOCK: o.9.reviewer.1 reviewed trust-path files" <<<"$msg" \
  || { bad "X503 REVIEW_BRIEF_NAMES_THE_SECURITY_PASS" "--log without the security spawn: rc $rc: $msg"; x503=1; }
(cd "$T" && "$PY" docs/graph/brief.py --role security --spawn-id o.9.security.3 --task t --route r --part rev.txt >/dev/null 2>&1) || true
rc=0; (cd "$T" && "$PY" docs/graph/brief.py --log >/dev/null 2>&1) || rc=$?
[[ $rc -eq 0 ]] || { bad "X503 REVIEW_BRIEF_NAMES_THE_SECURITY_PASS" "--log still blocks after the security spawn: rc $rc"; x503=1; }
[[ $x503 == 0 ]] && ok "X503 REVIEW_BRIEF_NAMES_THE_SECURITY_PASS: a trust-path review names the pass; --log blocks until a security spawn follows"
rm -rf "$T/app" "$T/docs/graph/nodes/crosscut.gate.md"
rc=0; (cd "$T" && "$PY" docs/graph/brief.py --role nobody --spawn-id s --task t --route r --part part.txt) >/dev/null 2>&1 || rc=$?
[[ $rc -ne 0 ]] && ok "unknown role refused" || bad "unknown role" "exit 0"
[[ "$fail" == 0 ]] && echo "test-brief: PASS" || { echo "test-brief: FAIL"; exit 1; }
