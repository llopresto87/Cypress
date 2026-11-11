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
# an opencode plant is refused the same way: its agent type carries the charter
O="$(mktemp -d)"; bash "$ROOT/install.sh" opencode --project-dir "$O" >/dev/null 2>&1
rc=0; msg="$(cd "$O" && "$PY" docs/graph/brief.py --role tester --spawn-id s.0 --task t --route r --charter --part "$T/part.txt" 2>&1 >/dev/null)" || rc=$?
[[ $rc -eq 2 ]] && grep -q "opencode" <<<"$msg" \
  && ok "X502 CHARTER_FLAG_ONLY_FOR_PRIME_AGENT: --charter is refused where .opencode/agents/ carries the role" \
  || bad "X502 CHARTER_FLAG_ONLY_FOR_PRIME_AGENT" "rc $rc: $msg"
rm -rf "$O"
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
# X505 TOKEN_LEDGER_RECORDS_HOST_USAGE: host usage per spawn_id, beside the
# spawn log, stored as given or `not recorded`; refusals leave it unchanged
x505=0; TL="$T/docs/graph/plans/tokens.jsonl"
tok() { (cd "$T" && "$PY" docs/graph/brief.py "$@"); }
out="$(echo '{"input": 12, "cache_write": 300, "cache_write_5m": 200, "cache_write_1h": 100, "cache_read": 9000, "output": 40, "model": "m-1", "source": "usage file"}' \
  | tok --tokens o.9.reviewer.1 --usage - 2>&1)" || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "full usage: $out"; x505=1; }
[[ "$out" == "tokens: o.9.reviewer.1 — m-1 — input 12, cache write 300 (5m 200, 1h 100), cache read 9000, output 40 — source: usage file" ]] \
  || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "stdout: $out"; x505=1; }
echo '{"output": 7, "model": "m-2"}' > "$T/partial.json"
tok --tokens o.9.reviewer.2 --usage partial.json >/dev/null 2>&1 || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "partial refused"; x505=1; }
echo '{}' | tok --tokens o.9.security.3 --usage - >/dev/null 2>&1 || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "empty refused"; x505=1; }
"$PY" - "$TL" <<'PY' || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "ledger rows"; x505=1; }
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
keys = ["spawn_id", "model", "input", "cache_write", "cache_write_5m", "cache_write_1h", "cache_read", "output", "source"]
assert all(sorted(r) == sorted(keys) for r in rows), rows
by = {r["spawn_id"]: r for r in rows}
assert by["o.9.reviewer.1"]["cache_write_1h"] == 100 and by["o.9.reviewer.1"]["input"] == 12, by
NR = "not recorded"
assert by["o.9.reviewer.2"]["output"] == 7 and by["o.9.reviewer.2"]["input"] == NR and by["o.9.reviewer.2"]["source"] == NR, by
assert all(by["o.9.security.3"][k] == NR for k in keys[1:]), by
PY
before="$(cat "$TL")"
for row in "unknown|nobody.1|{}|not in the spawn log" "again|o.9.reviewer.1|{}|already" \
           "frac|orchestrator.3.tester.1|{\"input\": 1.5}|whole number" "key|orchestrator.3.tester.1|{\"price\": 3}|price"; do
  IFS='|' read -r n sid js want <<<"$row"
  rc=0; msg="$(echo "$js" | tok --tokens "$sid" --usage - 2>&1)" || rc=$?
  [[ $rc -eq 2 ]] && grep -q "$want" <<<"$msg" || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "$n: rc $rc: $msg"; x505=1; }
done
[[ "$(cat "$TL")" == "$before" ]] || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "a refusal changed the ledger"; x505=1; }
[[ $x505 == 0 ]] && ok "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE: full, partial and empty usage stored as given or not recorded; refusals leave the ledger unchanged"
# X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT: one count per message id
# (its last record), the 5m and 1h writes apart, a synthetic record ignored
x506=0
u() { printf '{"type":"assistant","message":{"id":"%s","model":"%s","usage":{"input_tokens":%s,"cache_creation_input_tokens":%s,"cache_read_input_tokens":%s,"output_tokens":%s,"cache_creation":{"ephemeral_5m_input_tokens":%s,"ephemeral_1h_input_tokens":%s}}}}\n' "$@"; }
{ echo '{"type":"user","message":{"role":"user","content":"go"}}'
  u m1 claude-x 2 100 0 5 100 0; u m1 claude-x 2 100 0 551 100 0
  u m2 claude-x 3 10 100 20 0 10; u s1 '<synthetic>' 0 0 0 0 0 0; } > "$T/agent-a1.jsonl"
out="$(tok --tokens orchestrator.3.tester.1 --transcript agent-a1.jsonl 2>&1)" || { bad "X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT" "$out"; x506=1; }
[[ "$out" == "tokens: orchestrator.3.tester.1 — claude-x — input 5, cache write 110 (5m 100, 1h 10), cache read 100, output 571 — source: claude-code transcript" ]] \
  || { bad "X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT" "stdout: $out"; x506=1; }
(cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id o.9.tester.7 --task t --route r --effort "low (x)" --part part.txt >/dev/null 2>&1) || true
echo '{"type":"user","message":{"role":"user","content":"go"}}' > "$T/agent-a2.jsonl"
out="$(tok --tokens o.9.tester.7 --transcript agent-a2.jsonl 2>&1)" || { bad "X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT" "$out"; x506=1; }
[[ "$out" == "tokens: o.9.tester.7 — not recorded — input not recorded, cache write not recorded (5m not recorded, 1h not recorded), cache read not recorded, output not recorded — source: claude-code transcript" ]] \
  || { bad "X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT" "no usage: $out"; x506=1; }
[[ $x506 == 0 ]] && ok "X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT: one count per message id, 5m and 1h apart, no usage is not recorded"
# X505/X506 malformed input: a transcript line that is not an object is
# skipped; a ledger line that is not JSON refuses --tokens with one line, exit 2
x507=0
for i in 8 9; do (cd "$T" && "$PY" docs/graph/brief.py --role tester --spawn-id o.9.tester.$i --task t --route r --effort "low (x)" --part part.txt >/dev/null 2>&1) || true; done
{ echo '5'; echo '[1]'; u m3 claude-x 2 0 0 1 0 0; } > "$T/agent-a3.jsonl"
rc=0; out="$(tok --tokens o.9.tester.8 --transcript agent-a3.jsonl 2>&1)" || rc=$?
[[ $rc -eq 0 ]] && grep -q '^tokens: o.9.tester.8 — claude-x — input 2,' <<<"$out" \
  || { bad "X506 TOKEN_LEDGER_READS_A_CLAUDE_CODE_TRANSCRIPT" "non-object line: rc $rc: $out"; x507=1; }
held="$(cat "$TL")"; printf '{"spawn_id": "o.9.x"\n' >> "$TL"
rc=0; out="$(echo '{}' | tok --tokens o.9.tester.9 --usage - 2>"$T/err")" || rc=$?
[[ $rc -eq 2 && -z "$out" && $(wc -l <"$T/err") -eq 1 ]] && grep -q '^brief: .*tokens.jsonl.* line ' "$T/err" \
  || { bad "X505 TOKEN_LEDGER_RECORDS_HOST_USAGE" "malformed ledger: rc $rc: $(cat "$T/err")"; x507=1; }
printf '%s\n' "$held" > "$TL"
[[ $x507 == 0 ]] && ok "X505/X506 malformed input: a non-object transcript line is skipped; a malformed ledger line refuses with one line, exit 2"
# X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS: the Spawns, Serial waits and
# Tokens lines from a hand spawn log and ledger, byte for byte, and they pass
# session-metrics.py unchanged beside the lead's own lines
x515=0; FB="$ROOT/tests/fixtures/brief-log"; E5="$T/docs/graph/plans/e5"
mkdir -p "$E5"; cp "$FB/spawns.jsonl" "$FB/tokens.jsonl" "$E5/"
rc=0; got="$(cd "$T" && "$PY" docs/graph/brief.py --log --plan "$E5/grill.md" 2>&1)" || rc=$?
[[ $rc -eq 0 && "$got" == "$(cat "$FB/log.out")" ]] || { bad "X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS" "rc $rc: $got"; x515=1; }
{ printf '# Changelog\n\n## T2 delivery — e5 — 2026-11-10\n\n### Session metrics\n'
  printf -- '- Tier: T2 covered (reclassified: none)\n- Route bands: GREEN×1 HIGH×1 — overrides: none\n'
  printf -- '- Retries: none\n- Gates: 3 run, 0 failed\n- Full-suite runs: 1 (0 red)\n- Overflow notes: none\n'
  printf -- '- Quality: review Critical 0, Major 0; no mutation pass\n'
  grep -E '^- (Spawns|Serial waits|Tokens):' <<<"$got"; } > "$T/e5-changelog.md"
m="$(cd "$T" && "$PY" docs/graph/session-metrics.py --since 2026-11-10 --changelog e5-changelog.md 2>&1)" \
  && grep -q '^session metrics: PASS' <<<"$m" || { bad "X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS" "reader: $m"; x515=1; }
rm "$E5/tokens.jsonl"
got="$(cd "$T" && "$PY" docs/graph/brief.py --log --plan "$E5/grill.md" 2>/dev/null | tail -1)"
[[ "$got" == "- Tokens: not recorded: no spawn has a record in the token ledger tokens.jsonl" ]] \
  || { bad "X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS" "no ledger: $got"; x515=1; }
printf '{"spawn_id": "orchestrator.1"\n' > "$E5/tokens.jsonl"
got="$(cd "$T" && "$PY" docs/graph/brief.py --log --plan "$E5/grill.md" 2>/dev/null | tail -1)"
[[ "$got" == "- Tokens: not recorded: tokens.jsonl line 1 is not a JSON record" ]] \
  || { bad "X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS" "bad ledger: $got"; x515=1; }
rc=0; got="$(cd "$T" && "$PY" docs/graph/brief.py --log --plan "$T/docs/graph/plans/e5none/grill.md" 2>&1)" || rc=$?
[[ $rc -eq 1 && "$got" == "brief: no spawns logged at $T/docs/graph/plans/e5none/spawns.jsonl" ]] \
  || { bad "X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS" "empty log: rc $rc: $got"; x515=1; }
[[ $x515 == 0 ]] && ok "X515 BRIEF_LOG_PRINTS_THE_DERIVABLE_METRICS: Spawns, Serial waits and Tokens print from the log and ledger and pass the reader unchanged"
# X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH: one notice, logged, only for an
# undersized batch while more of its phase is ready; never a refusal
x516=0; FC="$ROOT/tests/fixtures/cycle"; mkdir -p "$T/tests"; cp "$FC"/files/tests/* "$T/tests/"
e6() {  # e6 DIR ROLE INCREMENTS [extra flags] -> stderr of the composition
  local d="$T/docs/graph/plans/$1"; mkdir -p "$d"; [[ -f "$d/grill.md" ]] || cp "$FC/grill.md" "$d/grill.md"
  (cd "$T" && "$PY" docs/graph/brief.py --role "$2" --spawn-id "$1.$2" --task "the batch" --route r --effort "low (x)" \
     --part part.txt --plan "$d/grill.md" --unit u --increments "$3" "${@:4}" 2>&1 >/dev/null)
}
notice() { grep '^brief: batch notice' <<<"$1" || true; }
n="$(notice "$(e6 e6a tester 1)")"
[[ "$n" == "brief: batch notice — increment 1 is 1 of the batch table's 7 for RED low; ready to join it: 2, 8 (delegation.effort-scale)" ]] \
  || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "undersized: $n"; x516=1; }
"$PY" - "$T/docs/graph/plans/e6a/spawns.jsonl" "$n" <<'PY' || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "not logged"; x516=1; }
import json, sys
r = [json.loads(l) for l in open(sys.argv[1])][-1]
assert r["notice"] == sys.argv[2][len("brief: "):], r
PY
[[ -z "$(notice "$(e6 e6b tester 1,2,8)")" ]] || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "exact batch noticed"; x516=1; }
mkdir -p "$T/docs/graph/plans/e6c"; cp "$FC/grill.md" "$T/docs/graph/plans/e6c/grill.md"
(cd "$T" && "$PY" docs/graph/cycle.py record-red 1 --unit u --plan docs/graph/plans/e6c/grill.md --file tests/test_alpha.sh --test a.1 >/dev/null \
  && "$PY" docs/graph/cycle.py record-red 2 --unit u --plan docs/graph/plans/e6c/grill.md --file tests/test_beta.sh --test b.1 >/dev/null) \
  || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "record-red"; x516=1; }
cp -R "$T/docs/graph/plans/e6c" "$T/docs/graph/plans/e6d"
[[ -z "$(notice "$(e6 e6c implementer 3 --security-path)")" ]] || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "security batch of one noticed"; x516=1; }
[[ -z "$(notice "$(e6 e6d implementer 3 --alone concurrency)")" ]] || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "concurrency batch of one noticed"; x516=1; }
mkdir -p "$T/docs/graph/plans/e6e"; cp "$FC/grill.md" "$T/docs/graph/plans/e6e/grill.md"
(cd "$T" && "$PY" docs/graph/cycle.py record-red 1 --unit u --plan docs/graph/plans/e6e/grill.md --file tests/test_alpha.sh --test a.1 >/dev/null)
rc=0; msg="$(e6 e6e implementer 3)" || rc=$?
[[ $rc -eq 0 && -z "$(notice "$msg")" ]] || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "nothing else ready: rc $rc: $msg"; x516=1; }
! grep -q '"notice"' "$T/docs/graph/plans/e6e/spawns.jsonl" || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "an empty notice was logged"; x516=1; }
rc=0; msg="$(e6 e6f tester 99)" || rc=$?
[[ $rc -eq 0 ]] && grep -q '^brief: batch notice skipped — ' <<<"$msg" || { bad "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH" "unknown increment blocked: rc $rc: $msg"; x516=1; }
[[ $x516 == 0 ]] && ok "X516 BRIEF_NOTICES_AN_UNDERSIZED_BATCH: an undersized batch with more ready notices once and logs it; exact, security, concurrency and nothing-else-ready do not"
# X545 BRIEF_NAMES_THE_EVIDENCE_A_RUN_OR_REVIEW_OWES: an increment whose §9 row
# carries Run: or Review: puts the evidence it owes under the handback block
x545=0; d="$T/docs/graph/plans/e7"; mkdir -p "$d"
"$PY" - "$FC/grill.md" "$d/grill.md" <<'PY'
import sys
t = open(sys.argv[1]).read()
t = t.replace("- Phase: GREEN", "- Run: `make build && grep -c Send dist/index.html`\n- Phase: GREEN", 1)
t = t.replace("- Phase: prose", "- Review (names what the reviewer confirms): the guide's wording\n- Phase: prose", 1)
open(sys.argv[2], "w").write(t)
PY
ev() { (cd "$T" && "$PY" docs/graph/brief.py --role "$1" --spawn-id "e7.$1.$2" --task t --route r --effort "low (x)" \
     --part part.txt --plan "$d/grill.md" --unit u --increments "$2" 2>/dev/null); }
got="$(ev implementer 3)"
[[ "$(sed -n '/^## Handback/,$p' <<<"$got" | grep -c '^## Evidence this hand-back owes')" == 1 ]] \
  && grep -qF -- '- increment 3 runs `make build && grep -c Send dist/index.html`: put that command and its result under `gates:` executed' <<<"$got" \
  || { bad "X545 BRIEF_NAMES_THE_EVIDENCE_A_RUN_OR_REVIEW_OWES" "run: $(tail -4 <<<"$got")"; x545=1; }
got="$(ev reviewer 7)"
grep -qF -- "- increment 7 is reviewed for the guide's wording: confirm it, or name what fails it, in the report body" <<<"$got" \
  || { bad "X545 BRIEF_NAMES_THE_EVIDENCE_A_RUN_OR_REVIEW_OWES" "review: $(tail -4 <<<"$got")"; x545=1; }
! grep -q 'Evidence this hand-back owes' <<<"$(ev tester 1)" || { bad "X545 BRIEF_NAMES_THE_EVIDENCE_A_RUN_OR_REVIEW_OWES" "a RED increment got the section"; x545=1; }
[[ $x545 == 0 ]] && ok "X545 BRIEF_NAMES_THE_EVIDENCE_A_RUN_OR_REVIEW_OWES: a Run: or Review: increment's brief names the evidence its hand-back owes; a RED increment's does not"
# X517 BRIEF_DERIVES_THE_MODEL_CLASS: the class table beside the effort table
# reproduces each role's `model:`, so every role and kind composes the brief it
# composed before the table existed (hashes captured from the prior tip); a row
# changed to another class adds one Model line
x517=0
T2="$T/x517"; mkdir -p "$T2"; bash "$ROOT/install.sh" claude-code --project-dir "$T2" >/dev/null 2>&1
printf 'Do the task.\n' > "$T2/part.txt"
"$PY" - "$T2/docs/graph/brief.py" "$ROOT/tests/fixtures/brief-class/before.sha256" "$T2" "$PY" <<'PY' || x517=1
import hashlib, importlib.util, subprocess, sys
b, want, root, py = sys.argv[1:]
s = importlib.util.spec_from_file_location("brief", b); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
rows = m.effort_rows()
classes = m.class_rows() if hasattr(m, "class_rows") else {}
for role, kind in sorted(rows):
    if classes.get((role, kind)) is None:
        print(f"  X517 BRIEF_DERIVES_THE_MODEL_CLASS — FAIL: no class row for {role} {kind}")
        sys.exit(1)
got = []
for role, kind in sorted(rows):
    r = subprocess.run([py, "docs/graph/brief.py", "--role", role, "--kind", kind, "--label", "medium",
                        "--spawn-id", f"o.c.{role}.{kind}", "--task", "t", "--route", "r", "--part", "part.txt"],
                       cwd=root, capture_output=True, text=True)
    out = r.stdout + r.stderr + ("" if r.returncode == 0 else f"exit {r.returncode}\n")
    got.append(f"{hashlib.sha256(out.encode()).hexdigest()}  {role} {kind}")
exp = open(want).read().split("\n")[:-1]
diff = sorted(set(got) ^ set(exp))
if diff:
    print("  X517 BRIEF_DERIVES_THE_MODEL_CLASS — FAIL: output changed for " + "; ".join(diff))
    sys.exit(1)
PY
N="$T2/docs/graph/method/delegation-model-classes.md"; cp "$N" "$T2/node.bak"
"$PY" - "$N" <<'PY' || x517=1
import re, sys
p = sys.argv[1]; t = open(p).read()
t, n = re.subn(r"^\| implementer \| `fix` \| opus \|$", "| implementer | `fix` | sonnet |", t, flags=re.M)
open(p, "w").write(t)
sys.exit(0 if n == 1 else 1)
PY
err="$(cd "$T2" && "$PY" docs/graph/brief.py --role implementer --kind fix --spawn-id o.x517.m --task t --route r \
       --part part.txt --out docs/graph/plans/x517.md 2>&1 >/dev/null)" || x517=1
[[ "$(grep -c '^Model: sonnet (implementer fix, definition default opus)$' "$T2/docs/graph/plans/x517.md" 2>/dev/null)" == 1 ]] \
  && [[ "$(grep -c '^model: sonnet' <<<"$err")" == 1 ]] \
  || { bad "X517 BRIEF_DERIVES_THE_MODEL_CLASS" "changed row: want one Model line; stderr: $err"; x517=1; }
cp "$T2/node.bak" "$N"
[[ $x517 == 0 ]] && ok "X517 BRIEF_DERIVES_THE_MODEL_CLASS: every role and kind composes its prior brief byte for byte; a changed class row adds one Model line" \
  || bad "X517 BRIEF_DERIVES_THE_MODEL_CLASS" "see above"
# X570 to X575 (SPEC-0008): who writes the test. A low-band increment off trust
# paths composes one implementer brief (`--kind merged`); a trust path, a label
# above the band, stateful or concurrent code and a bug reproduction owe a tester
d="$T/docs/graph/plans/e8"; mkdir -p "$d" "$T/docs/graph/specs"
"$PY" - "$FC/grill.md" "$d/grill.md" <<'PY'
import sys
t = open(sys.argv[1]).read()
t = t.replace("- Files touched: `tests/test_delta.sh`\n- Tests to write (RED): delta.case_one\n- Rollback path: delete the test\n- Effort: low",
              "- Files touched: `tests/test_delta.sh`\n- Tests to write (RED): delta.case_one\n- Rollback path: delete the test\n- Effort: medium-low", 1)
inc = lambda n, title, slug, files, tests, effort, phase, dep: (
    f"### Increment {n} — {title}\n- Spec contracts: {slug}\n- Files touched: `{files}`\n- Tests to write (RED): {tests}\n"
    f"- Rollback path: revert\n- Effort: {effort}\n- Phase: {phase}\n- Depends on: {dep}\n\n")
extra = (inc(9, "RED vault", "SPEC-0001/VAULT", "tests/test_vault.sh", "vault.case_one", "low", "RED", "none")
         + inc(10, "GREEN vault", "SPEC-0001/VAULT", "app/vault/lock.py", "none — increment 9 wrote them", "low", "GREEN", "increment 9")
         + inc(11, "RED retry", "SPEC-0009/RETRY_IS_IDEMPOTENT", "tests/test_retry.sh",
               'SPEC-0009 §10 rows: "Retry after timeout double-charges"', "medium-low", "RED", "none")
         + inc(12, "reproduce and fix the empty-input crash", "none — contained lane (tiers.contained-lane)",
               "tests/test_parse.sh` and `app/parse.py", "parse.empty_input_regression", "low", "RED and GREEN", "none")
         + inc(13, "reproduce and fix the stale lock", "none — contained lane (tiers.contained-lane)",
               "tests/test_lock.sh` and `app/vault/lock.py", "lock.stale_regression", "low", "RED and GREEN", "none"))
assert "### Increment 8" in t
open(sys.argv[2], "w").write(t.replace("## 15. Changelog", extra + "## 15. Changelog"))
PY
printf '# SPEC-0009\n\n## 10. Test mapping\n\n| Risk (what breaks, for whom) | Test (file::name, lowest level) | Covers | Origin | Status |\n|---|---|---|---|---|\n| Retry after timeout double-charges | tests/test_retry.sh::retry_is_idempotent | RETRY_IS_IDEMPOTENT | bug | pending |\n' \
  > "$T/docs/graph/specs/SPEC-0009-retry.md"
mg() {  # mg ID ROLE KIND INCREMENTS [extra] -> "rc|stderr" and the brief in $T/mg.out
  local rc=0 err
  err="$(cd "$T" && "$PY" docs/graph/brief.py --role "$2" --kind "$3" --spawn-id "e8.$1" --task t --route r \
         --part part.txt --plan "$d/grill.md" --unit u --increments "$4" "${@:5}" 2>&1 >"$T/mg.out")" || rc=$?
  printf '%s|%s' "$rc" "$err"
}
rc_of() { local g; g="$(mg "$@")"; printf '%s' "${g%%|*}"; }
WV="$T/docs/graph/nodes/crosscut.vault.md"
x571=0; got="$(mg 1 implementer merged 1,3)"
[[ "${got%%|*}" == 2 ]] && grep -q "increments 1,3 owe a tester RED spawn: the plant marks no trust path, so the doubt is read as one" <<<"$got" \
  || { bad "X571 TRUST_PATH_INCREMENT_OWES_A_TESTER" "no marking: $got"; x571=1; }
printf -- '---\nid: crosscut.vault\ntier: 2\ntrust: true\nkind: crosscut\norigin: project\ntitle: vault\nowns:\n  - vault.menu\nload_when:\n  - "app/vault/**"\nest_tokens: 100\n---\n\nVault.\n' > "$WV"
x570=0; got="$(mg 2 implementer merged 1,3)"
[[ "${got%%|*}" == 0 ]] && grep -qF "effort: low (implementer merged, label low)" <<<"$got" \
  && grep -q '^## One spawn: the test first, then the code' "$T/mg.out" \
  && grep -qF "write the test increment 1 cites and see it fail for the right reason before any code" "$T/mg.out" \
  && grep -qF "record both observations" "$T/mg.out" \
  || { bad "X570 LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF" "eligible: $got"; x570=1; }
"$PY" - "$d/spawns.jsonl" <<'PY' || { bad "X570 LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF" "merged not logged"; x570=1; }
import json, sys
r = [json.loads(l) for l in open(sys.argv[1])][-1]
assert r["spawn_id"] == "e8.2" and r["merged"] == [1, 3], r
PY
got="$(cd "$T" && "$PY" docs/graph/brief.py --role implementer --kind merged --spawn-id e8.2b --task t --route r --part part.txt 2>&1 >/dev/null)" && rc=0 || rc=$?
[[ $rc == 2 ]] && grep -q "merged reads --increments" <<<"$got" || { bad "X570 LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF" "no increments: $rc $got"; x570=1; }
[[ $x570 == 0 ]] && ok "X570 LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF: a low-band increment off trust paths composes one implementer brief, RED seen first and both observations recorded, logged as merged"
got="$(mg 3 implementer merged 9,10)"
[[ "${got%%|*}" == 2 ]] && grep -q "increments 9,10 owe a tester RED spawn: on a trust path (app/vault/lock.py: crosscut.vault)" <<<"$got" \
  || { bad "X571 TRUST_PATH_INCREMENT_OWES_A_TESTER" "trust path: $got"; x571=1; }
got="$(mg 4 tester red 9 --label low)"
[[ "${got%%|*}" == 0 ]] && ! grep -q "one implementer spawn" <<<"$got" || { bad "X571 TRUST_PATH_INCREMENT_OWES_A_TESTER" "tester brief: $got"; x571=1; }
[[ $x571 == 0 ]] && ok "X571 TRUST_PATH_INCREMENT_OWES_A_TESTER: a trust-path increment, or any in a plant that marks no trust path, is refused the merged brief and composes a tester RED brief"
x572=0; got="$(mg 5 implementer merged 5,6)"
[[ "${got%%|*}" == 2 ]] && grep -q "increments 5,6 owe a tester RED spawn: label medium is above the low-risk band (low, medium-low)" <<<"$got" \
  || { bad "X572 ABOVE_BAND_INCREMENT_OWES_A_TESTER" "medium: $got"; x572=1; }
[[ "$(rc_of 6 tester red 5 --label medium)" == 0 ]] || { bad "X572 ABOVE_BAND_INCREMENT_OWES_A_TESTER" "tester brief refused"; x572=1; }
[[ $x572 == 0 ]] && ok "X572 ABOVE_BAND_INCREMENT_OWES_A_TESTER: an increment above the low-risk band is refused the merged brief and composes a tester RED brief"
x573=0; got="$(mg 7 implementer merged 11)"
[[ "${got%%|*}" == 2 ]] && grep -q "increment 11 owes a tester RED spawn: its test reproduces a bug (SPEC-0009 §10 origin bug)" <<<"$got" \
  || { bad "X573 STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER" "bug: $got"; x573=1; }
got="$(mg 8 implementer merged 1,3 --alone "a shared counter")"
[[ "${got%%|*}" == 2 ]] && grep -q "increments 1,3 owe a tester RED spawn: stateful or concurrent (a shared counter)" <<<"$got" \
  || { bad "X573 STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER" "concurrent: $got"; x573=1; }
[[ "$(rc_of 9 tester red 11 --label medium-low)" == 0 ]] || { bad "X573 STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER" "tester brief refused"; x573=1; }
[[ $x573 == 0 ]] && ok "X573 STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER: a bug reproduction or a stateful or concurrent increment is refused the merged brief and composes a tester RED brief"
x574=0; EN="$T/docs/graph/method/delegation-cycle-economy.md"; cp "$EN" "$T/economy.bak"
[[ "$(rc_of 10 implementer merged 8)" == 0 ]] || { bad "X574 LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE" "medium-low refused under the default"; x574=1; }
"$PY" - "$EN" <<'PY' || { bad "X574 LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE" "no band line in the node"; x574=1; }
import sys
p = sys.argv[1]; t = open(p).read(); old = "**The low-risk band** is `low` and `medium-low` ("
assert t.count(old) == 1, "band line"
open(p, "w").write(t.replace(old, "**The low-risk band** is `low` ("))
PY
got="$(mg 11 implementer merged 8)"
[[ "${got%%|*}" == 2 ]] && grep -q "increment 8 owes a tester RED spawn: label medium-low is above the low-risk band (low)" <<<"$got" \
  || { bad "X574 LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE" "moved band: $got"; x574=1; }
cp "$T/economy.bak" "$EN"
[[ $x574 == 0 ]] && ok "X574 LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE: the band is the effort-scale node's line; moving it there moves the brief"
x575=0; got="$(mg 12 tester red 1 --label low)"
[[ "${got%%|*}" == 0 ]] && grep -qF "brief: increment 1 is in the low-risk band off trust paths: one implementer spawn writes its test and code (--role implementer --kind merged; tiers.execution-paths)" <<<"$got" \
  || { bad "X575 TESTER_BRIEF_NAMES_THE_MERGED_PATH" "eligible: $got"; x575=1; }
[[ $x575 == 0 ]] && ok "X575 TESTER_BRIEF_NAMES_THE_MERGED_PATH: a tester brief for a low-band increment off trust paths names the merged path to the caller; a trust-path one does not"
# X730 to X731 (SPEC-0008): a contained-lane defect (no spec contract over it)
# keeps one worker writing its reproduction test and the fix; a bug-origin §10
# row in a spec'd increment still owes a tester (X573)
x730=0; got="$(mg 13 implementer merged 12)"
[[ "${got%%|*}" == 0 ]] && grep -qF "write the test increment 12 cites and see it fail for the right reason before any code" "$T/mg.out" \
  || { bad "X730 CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF" "contained defect: $got"; x730=1; }
"$PY" - "$d/spawns.jsonl" <<'PY' || { bad "X730 CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF" "merged not logged"; x730=1; }
import json, sys
r = [json.loads(l) for l in open(sys.argv[1])][-1]
assert r["spawn_id"] == "e8.13" and r["merged"] == [12], r
PY
got="$(mg 14 tester red 12 --label low)"
[[ "${got%%|*}" == 0 ]] && grep -qF "brief: increment 12 is in the low-risk band off trust paths" <<<"$got" \
  || { bad "X730 CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF" "tester notice: $got"; x730=1; }
[[ $x730 == 0 ]] && ok "X730 CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF: a contained-lane defect composes one implementer brief that writes the reproduction test, sees it fail, then fixes"
x731=0; got="$(mg 15 implementer merged 13)"
[[ "${got%%|*}" == 2 ]] && grep -qF "increment 13 owes a tester RED spawn: on a trust path (app/vault/lock.py: crosscut.vault);" <<<"$got" \
  && ! grep -q "reproduces a bug" <<<"$got" \
  || { bad "X731 CONTAINED_LANE_DEFECT_KEEPS_THE_OTHER_REASONS" "trust path: $got"; x731=1; }
[[ $x731 == 0 ]] && ok "X731 CONTAINED_LANE_DEFECT_KEEPS_THE_OTHER_REASONS: a contained-lane defect on a trust path owes a tester for the trust path, never for the reproduction"
# X740 to X748 (SPEC-0008): the merged brief fails closed. A band, a trust-path
# claim or a §10 origin that cannot be read refuses it, naming what could not be
# read and what fixes it, and the tester brief still composes; a `design`-origin
# §10 row keeps the merged brief that a `bug`-origin row on the same increment
# refuses. Increments 1,3 (low, off the trust path crosscut.vault claims)
# compose the merged brief whenever every reading answers (X570).
"$PY" - "$d/grill.md" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
inc = lambda n, title, slug, files, tests, phase, dep: (
    f"### Increment {n} — {title}\n- Spec contracts: {slug}\n- Files touched: {files}\n- Tests to write (RED): {tests}\n"
    f"- Rollback path: revert\n- Effort: low\n- Phase: {phase}\n- Depends on: {dep}\n\n")
extra = (inc(14, "RED ledger", "SPEC-0001/LEDGER", "`tests/test_ledger.sh`", "ledger.case_one", "RED", "none")
         + inc(15, "GREEN ledger", "SPEC-0001/LEDGER", "app/vault/ledger.py", "none — increment 14 wrote them", "GREEN", "increment 14")
         + inc(16, "RED tally", "SPEC-0001/TALLY", "the tally tests", "tally.case_one", "RED", "none")
         + inc(17, "RED render", "SPEC-0010/RENDER_IS_STABLE", "`tests/test_render.sh`", "render.case_one", "RED", "none"))
open(p, "w").write(t.replace("## 15. Changelog", extra + "## 15. Changelog"))
PY
refused() {  # refused LABEL CASE ID INCREMENTS WANT... -> the merged brief exits 2 naming each WANT; a tester brief composes
  local label="$1" case="$2" id="$3" incs="$4" got w; shift 4
  got="$(mg "$id" implementer merged "$incs")"
  [[ "${got%%|*}" == 2 ]] && grep -qF "owe" <<<"$got" && grep -qF "a tester RED spawn:" <<<"$got" \
    || { bad "$label" "$case: not refused: $got"; return 1; }
  for w in "$@"; do grep -qF -- "$w" <<<"$got" || { bad "$label" "$case: refusal lacks '$w': $got"; return 1; }; done
  [[ "$(rc_of "$id.t" tester red "${incs%%,*}" --label low)" == 0 ]] || { bad "$label" "$case: tester brief refused"; return 1; }
}
x740=0; cp "$EN" "$T/economy.bak"
"$PY" - "$EN" <<'PY'
import re, sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(re.sub(r"^- \*\*The low-risk band\*\* is .*\n", "", t, count=1, flags=re.M))
PY
refused "X740 BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "band line removed" 20 1,3 "the low-risk band cannot be read" "delegation-cycle-economy.md has no" \
  "restore the \`**The low-risk band** is ...\` line (delegation.effort-scale)" || x740=1
"$PY" - "$T/economy.bak" "$EN" <<'PY'
import sys
t = open(sys.argv[1]).read()
open(sys.argv[2], "w").write(t.replace("**The low-risk band** is `low` and `medium-low` (", "**The low-risk band** is the owner's to set (", 1))
PY
refused "X740 BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "band line naming no label" 21 1,3 "the low-risk band cannot be read" "names no label" || x740=1
rm -f "$EN"
refused "X740 BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "effort-scale node missing" 22 1,3 "the low-risk band cannot be read" "delegation-cycle-economy.md" "restore" || x740=1
cp "$T/economy.bak" "$EN"
[[ "$(rc_of 23 implementer merged 1,3)" == 0 ]] || { bad "X740 BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "the restored band refuses"; x740=1; }
[[ $x740 == 0 ]] && ok "X740 BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF (failure BAND_LINE_MISSING): a missing band line, a line naming no label and a missing node refuse the merged brief, naming the line to restore"
NG="$T/docs/graph/nodes"
x741=0; mv "$NG" "$T/nodes.away"
refused "X741 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "nodes directory missing" 24 1,3 "the trust-path claims cannot be read" "docs/graph/nodes/ is missing" "restore" || x741=1
mv "$T/nodes.away" "$NG"
[[ $x741 == 0 ]] && ok "X741 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: a missing nodes directory is named apart from a plant that marks no trust path"
x742=0; printf -- '---\nid: crosscut.broken\nkind: crosscut\ntrust: true\nload_when:\n  - "src/**"\n' > "$NG/crosscut.broken.md"
refused "X742 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "unterminated frontmatter" 25 1,3 "the trust-path claims cannot be read" "crosscut.broken.md: unterminated frontmatter" \
  "repair it so graph-lint.py --trust-claims answers" || x742=1
rm -f "$NG/crosscut.broken.md"
[[ $x742 == 0 ]] && ok "X742 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: a node whose frontmatter cannot be read refuses the merged brief, naming the node"
x743=0; printf -- '---\nid: crosscut.sealed\ntier: 2\ntrust: true\nkind: crosscut\norigin: project\ntitle: sealed\nowns:\n  - sealed.menu\nload_when:\n  - "src/**"\nest_tokens: 100\n---\n\nSealed.\n' > "$NG/crosscut.sealed.md"
chmod 000 "$NG/crosscut.sealed.md"
if [[ -r "$NG/crosscut.sealed.md" ]]; then
  ok "X743 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: skipped, this user reads a mode-000 file"
else
  refused "X743 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "unreadable node" 26 1,3 "the trust-path claims cannot be read" "crosscut.sealed.md" || x743=1
  [[ $x743 == 0 ]] && ok "X743 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: a node the composer cannot open refuses the merged brief, naming the node"
fi
chmod 644 "$NG/crosscut.sealed.md"; rm -f "$NG/crosscut.sealed.md"
x744=0; mkdir -p "$NG/vault"; mv "$WV" "$NG/vault/crosscut.vault.md"
refused "X744 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "trust crosscut below nodes/" 27 9,10 "nodes/vault/crosscut.vault.md" "move it up" || x744=1
mv "$NG/vault/crosscut.vault.md" "$WV"; rmdir "$NG/vault"
[[ $x744 == 0 ]] && ok "X744 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: a trust crosscut below nodes/, which graph-lint.py reads no node from, refuses the merged brief"
x745=0; GL="$T/docs/graph/graph-lint.py"; mv "$GL" "$T/graph-lint.away"
refused "X745 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "graph-lint.py not answering" 28 1,3 "the trust-path claims cannot be read" "graph-lint.py --trust-claims did not answer" \
  "run it and repair what it names" || x745=1
mv "$T/graph-lint.away" "$GL"
[[ $x745 == 0 ]] && ok "X745 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: graph-lint.py --trust-claims not answering refuses the merged brief, naming the fix"
x746=0
refused "X746 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "an unquoted trust path" 29 14,15 "on a trust path (app/vault/ledger.py: crosscut.vault)" || x746=1
refused "X746 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "no path named" 30 16 "increment 16 names no path under Files touched" "name the files it touches" || x746=1
[[ $x746 == 0 ]] && ok "X746 TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: Files touched is read through grill-lint.py's path reader, and an increment naming no path refuses the merged brief"
x747=0; SL="$T/docs/graph/spec-lint.py"; mv "$SL" "$T/spec-lint.away"
refused "X747 BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "spec-lint.py missing" 31 11 "the §10 origins cannot be read" "spec-lint.py" "restore" || x747=1
mv "$T/spec-lint.away" "$SL"
S9="$T/docs/graph/specs/SPEC-0009-retry.md"; chmod 000 "$S9"
if [[ ! -r "$S9" ]]; then
  refused "X747 BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF" "spec unreadable" 32 11 "the §10 origins cannot be read" "SPEC-0009-retry.md" || x747=1
fi
chmod 644 "$S9"
[[ $x747 == 0 ]] && ok "X747 BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF: a §10 origin the composer cannot read refuses the merged brief, naming what to restore"
x748=0; S10="$T/docs/graph/specs/SPEC-0010-render.md"
printf '# SPEC-0010\n\n## 10. Test mapping\n\n| Risk (what breaks, for whom) | Test (file::name, lowest level) | Covers | Origin | Status |\n|---|---|---|---|---|\n| A page renders twice | tests/test_render.sh::render_is_stable | RENDER_IS_STABLE | design | pending |\n' > "$S10"
got="$(mg 33 implementer merged 17)"
[[ "${got%%|*}" == 0 ]] && grep -qF "write the test increment 17 cites" "$T/mg.out" \
  || { bad "X748 DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF" "design origin refused: $got"; x748=1; }
"$PY" - "$S10" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read(); open(p, "w").write(t.replace("| design |", "| bug |", 1))
PY
got="$(mg 34 implementer merged 17)"
[[ "${got%%|*}" == 2 ]] && grep -qF "increment 17 owes a tester RED spawn: its test reproduces a bug (SPEC-0010 §10 origin bug)" <<<"$got" \
  || { bad "X748 DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF" "bug origin on the same increment: $got"; x748=1; }
[[ $x748 == 0 ]] && ok "X748 DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF: a design-origin §10 row composes the merged brief; the same row of origin bug owes a tester"
rm -f "$WV"
rc=0; (cd "$T" && "$PY" docs/graph/brief.py --role nobody --spawn-id s --task t --route r --part part.txt) >/dev/null 2>&1 || rc=$?
[[ $rc -ne 0 ]] && ok "unknown role refused" || bad "unknown role" "exit 0"
[[ "$fail" == 0 ]] && echo "test-brief: PASS" || { echo "test-brief: FAIL"; exit 1; }
