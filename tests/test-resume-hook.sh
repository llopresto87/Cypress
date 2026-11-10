#!/usr/bin/env bash
# test-resume-hook.sh — the cold-resume guard (integrations/claude-code/resume-hook.py)
# refuses a SendMessage to a worker idle past its configured cache lifetime unless the host cut the
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
# X507 RESUME_GUARD_FOLLOWS_THE_CONFIGURED_CACHE_LIFETIME: the cold threshold is
# the worker cache lifetime the host is configured for (environment, project and
# user settings, the agent's `experimental: cacheTtl`), 300 s when unreadable.
P="$W/plant"; H="$W/home"; mkdir -p "$P/.claude/agents" "$H/.claude"
w5='{"type":"assistant","message":{"id":"m1","role":"assistant","usage":{"cache_creation_input_tokens":900,"cache_creation":{"ephemeral_5m_input_tokens":900,"ephemeral_1h_input_tokens":0}},"content":[]}}'
w1='{"type":"assistant","message":{"id":"m0","role":"assistant","usage":{"cache_creation_input_tokens":900,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":900}},"content":[]}}'
w1p='{"type":"assistant","message":{"id":"m0","role":"assistant","usage":{"cache_creation_input_tokens":0},"content":[]}}'
w0='{"type":"assistant","message":{"id":"m2","role":"assistant","usage":{"cache_creation_input_tokens":0,"cache_read_input_tokens":500},"content":[]}}'
for m in 4 30 90; do
    printf '%s\n' "$w1" "$HANDBACK" > "$S/agent-ai$m.jsonl"
    printf '{"agentType":"worker","isBuiltIn":false}' > "$S/agent-ai$m.meta.json"
done
"$PY" - "$S" <<'PY'
import os, sys, time
for m in (4, 30, 90):
    t = time.time() - m * 60
    os.utime(f"{sys.argv[1]}/agent-ai{m}.jsonl", (t, t))
PY
agent() { printf -- '---\nname: worker\n%s---\n# worker\n' "$1" > "$P/.claude/agents/02-worker.md"; }
reset() { rm -f "$P/.claude/settings.json" "$P/.claude/settings.local.json" "$H/.claude/settings.json"; agent ''; }
x507() {  # label allowed-idle-minutes... (the rest refused); extra env in XENV
    local label="$1" m want got; shift
    for m in 4 30 90; do
        want=2; for a in "$@"; do [[ "$a" == "$m" ]] && want=0; done
        got=0
        printf '%s' "$(env ai$m 'Implement increment 12')" | command env -u CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL \
            -u FORCE_PROMPT_CACHING_5M -u ENABLE_PROMPT_CACHING_1H -u CLAUDE_CODE_PROMPT_CACHE_TTL \
            HOME="$H" CLAUDE_PROJECT_DIR="$P" ${XENV:-} "$PY" "$HOOK" >/dev/null 2>"$W/err" || got=$?
        if [[ "$got" != "$want" ]]; then
            echo "  X507 RESUME_GUARD_FOLLOWS_THE_CONFIGURED_CACHE_LIFETIME $label, idle $m min — FAIL (exit $got, want $want): $(cat "$W/err")"; fail=1; x=1
        fi
    done
}
x=0
reset
for v in 5m 1h bogus unset; do
    if [[ $v == 1h ]]; then al="4 30"; else al="4"; fi
    if [[ $v == unset ]]; then XENV=""; else XENV="CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=$v"; fi
    x507 "env variable $v" $al
    XENV=""
    [[ $v != unset ]] && printf '{"subagentPromptCacheTtl":"%s"}' "$v" > "$P/.claude/settings.json"
    x507 "project setting $v" $al; reset
    [[ $v != unset ]] && agent "experimental:
  cacheTtl: $v
"
    x507 "agent frontmatter $v (a frontmatter 1h is not trusted)" 4; reset
done
XENV="ENABLE_PROMPT_CACHING_1H=1"; x507 "enable-1h variable" 4 30
XENV="FORCE_PROMPT_CACHING_5M=1 CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=1h"; x507 "force-5m over the env variable" 4
XENV="CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=5m"; printf '{"subagentPromptCacheTtl":"1h"}' > "$P/.claude/settings.json"
x507 "env variable 5m over a setting 1h" 4; XENV=""
printf '{"subagentPromptCacheTtl":"5m"}' > "$P/.claude/settings.local.json"; x507 "local setting 5m over shared 1h" 4; reset
printf '{"env":{"CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL":"1h"}}' > "$P/.claude/settings.json"; x507 "settings env block 1h" 4 30; reset
printf '{"subagentPromptCacheTtl":"1h"}' > "$H/.claude/settings.json"; x507 "user setting 1h" 4 30; reset
agent "experimental:
  cacheTtl: 5m
"; XENV="ENABLE_PROMPT_CACHING_1H=1"; x507 "frontmatter 5m over enable-1h" 4; XENV=""; reset
printf 'not json' > "$P/.claude/settings.json"; x507 "unreadable settings" 4; reset
printf '%s' "$(env ai90 'Implement increment 12')" | command env -u CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL HOME="$H" CLAUDE_PROJECT_DIR="$P" \
    CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=1h "$PY" "$HOOK" 2>"$W/err" >/dev/null || true
grep -q '60-minute' "$W/err" || { echo "  X507 refusal names the resolved lifetime — FAIL: $(cat "$W/err")"; fail=1; x=1; }
# A configured 1h counts only when the worker's transcript shows the host wrote
# a one-hour cache: the last record with cache-creation tokens decides.
written() { for m in 4 30 90; do printf '%s\n' "$@" "$HANDBACK" > "$S/agent-ai$m.jsonl"; done
    "$PY" - "$S" <<'PY'
import os, sys, time
for m in (4, 30, 90):
    t = time.time() - m * 60
    os.utime(f"{sys.argv[1]}/agent-ai{m}.jsonl", (t, t))
PY
}
XENV="CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=1h"
written "$w1" "$w5" "$w0"; x507 "configured 1h, last write 5m only" 4
written "$w1p" "$w1" "$w0"; x507 "configured 1h, last write one hour (repeated id, last record wins)" 4 30
written "$w1" "$w1p"; x507 "configured 1h, last record of the 1h id has no write" 4
written "$w0"; x507 "configured 1h, no creation tokens" 4
XENV="ENABLE_PROMPT_CACHING_1H=1"; written "$w5"; x507 "enable-1h, last write 5m only" 4
XENV="ENABLE_PROMPT_CACHING_1H=true"; written "$w1"; x507 "enable-1h other than 1 is not documented" 4
XENV=""
[[ $x == 0 ]] && echo "  X507 RESUME_GUARD_FOLLOWS_THE_CONFIGURED_CACHE_LIFETIME: 5m, 1h, invalid and unset from each source against 4, 30 and 90 min idle — OK"
if [[ "$fail" == 0 ]]; then echo "test-resume-hook: PASS"; else echo "test-resume-hook: FAIL"; exit 1; fi
