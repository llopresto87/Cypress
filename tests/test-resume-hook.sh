#!/usr/bin/env bash
# test-resume-hook.sh — the cold-resume guard (integrations/claude-code/resume-hook.py)
# refuses a SendMessage to a worker idle past COLD_AFTER unless the host cut the
# worker off (its last record an API error) or the message declares a continuation, and fails open on everything it cannot read.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/integrations/claude-code/resume-hook.py"
PY="${PYTHON:-python3}"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
mkdir -p "$W/proj/sess/subagents"
: > "$W/proj/sess.jsonl"
S="$W/proj/sess/subagents"
HANDBACK='{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","name":"SubagentHandback","input":{"message":"done"}}]}}'
TOOLRES='{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"ok"}]}}'
printf '%s\n%s\n' "$TOOLRES" "$HANDBACK" > "$S/agent-acold.jsonl"
printf '%s\n' "$HANDBACK" > "$S/agent-awarm.jsonl"
printf '%s\n' "$HANDBACK" > "$S/agent-aten.jsonl"
for kind in rate_limit server_error; do
    printf '%s\n{"type":"assistant","isApiErrorMessage":true,"error":"%s","message":{"role":"assistant","content":[{"type":"text","text":"API Error"}]}}\n' "$TOOLRES" "$kind" > "$S/agent-a$kind.jsonl"
done
"$PY" - "$S" <<'PY'
import os, sys, time
t = time.time() - 2 * 3600
for n in ("acold", "arate_limit", "aserver_error"):
    os.utime(f"{sys.argv[1]}/agent-{n}.jsonl", (t, t))
t10 = time.time() - 10 * 60
os.utime(f"{sys.argv[1]}/agent-aten.jsonl", (t10, t10))
PY
fail=0
run() {  # name expected_exit stdin
    local name="$1" want="$2" input="$3" got=0
    printf '%s' "$input" | "$PY" "$HOOK" >"$W/out" 2>"$W/err" || got=$?
    if [[ "$got" == "$want" ]]; then echo "  $name — OK"; else
        echo "  $name — FAIL (exit $got, want $want): $(cat "$W/err")"; fail=1; fi
}
env() { printf '{"tool_name":"SendMessage","transcript_path":"%s","tool_input":{"to":"%s","message":"%s"}}' "$W/proj/sess.jsonl" "$1" "$2"; }
run "cold worker that handed back, new work: refused" 2 "$(env acold 'Implement increment 12')"
run "cold worker cut by a usage limit: resume allowed" 0 "$(env arate_limit 'Your run was cut; resume')"
run "cold worker cut by a server error: resume allowed" 0 "$(env aserver_error 'Your run was cut; resume')"
run "cold worker, declared continuation: allowed" 0 "$(env acold 'continuation: usage limit lifted, finish increment 11')"
run "worker idle 10 min that handed back: refused (subagent cache lives 5 min)" 2 "$(env aten 'Implement increment 12')"
run "warm worker: allowed"                      0 "$(env awarm 'Implement increment 12')"
run "unknown worker: allowed"                   0 "$(env anone 'Implement increment 12')"
run "another tool: allowed"                     0 '{"tool_name":"Bash","tool_input":{"command":"ls"}}'
run "unparseable stdin: allowed"                0 'not json'
run "no transcript path: allowed"               0 '{"tool_name":"SendMessage","tool_input":{"to":"acold","message":"x"}}'
run "path-like id: allowed, never resolved"     0 "$(env '../../etc' 'x')"
printf '%s' "$(env acold 'Implement increment 12')" | "$PY" "$HOOK" 2>"$W/err" >/dev/null || true
grep -q 'continuation:' "$W/err" && grep -q 'delegation.continuation' "$W/err" && grep -q 'handed back' "$W/err" \
  && echo "  refusal names the declaration and the rule — OK" \
  || { echo "  refusal names the declaration and the rule — FAIL"; fail=1; }
if [[ "$fail" == 0 ]]; then echo "test-resume-hook: PASS"; else echo "test-resume-hook: FAIL"; exit 1; fi
