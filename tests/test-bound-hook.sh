#!/usr/bin/env bash
# Bounded-execution guard contract: `integrations/claude-code/bound-hook.py` is
# a PreToolUse hook on the Bash tool. It must BLOCK (exit 2) a blocking-prone
# command that carries neither a bound nor a detached launch, and must stay out
# of the way (exit 0) everywhere else — including when it cannot understand its
# own input. Guards the class of defect where a guard hook either lets the
# hanging command through or, worse, bricks a session by blocking on a bug.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$ROOT/integrations/claude-code/bound-hook.py"

fail() { echo "FAIL: $*" >&2; exit 1; }

# RED-first guard: a missing hook makes `python3` itself exit 2, which would
# masquerade as a passing block. Say what is actually wrong instead.
[[ -f "$HOOK" ]] || fail "hook not found: $HOOK"

RC=0
ERR=""
run() {  # $1 = raw stdin payload -> sets RC and ERR
  set +e
  ERR="$(printf '%s' "$1" | python3 "$HOOK" 2>&1 >/dev/null)"
  RC=$?
  set -e
}

mkjson() {  # $1 = tool_name  $2 = command
  python3 - "$1" "$2" <<'PY'
import json, sys
print(json.dumps({"hook_event_name": "PreToolUse", "tool_name": sys.argv[1],
                  "tool_input": {"command": sys.argv[2]}}))
PY
}

expect() {  # $1 = tool  $2 = command  $3 = expected exit  $4 = label
  run "$(mkjson "$1" "$2")"
  [[ "$RC" == "$3" ]] || fail "$4: expected exit $3, got $RC — command: $2 — stderr: $ERR"
  echo "  $4 — OK"
}

# --- blocking-prone commands with no bound and no detachment: exit 2 ---------
expect Bash 'systemctl --user daemon-reload'            2 "bare service control blocks"
expect Bash './install.sh'                              2 "bare installer blocks"
expect Bash 'sudo apt install x'                        2 "bare sudo + package manager blocks"
expect Bash 'npm install'                               2 "bare package install blocks"
expect Bash 'tail -f app.log'                           2 "bare follow blocks"
expect Bash 'make'                                      2 "bare make (default target) blocks"
expect Bash 'make test'                                 2 "bare make with target blocks"
expect Bash 'cargo build --release'                     2 "bare cargo build blocks"
expect Bash 'cmake --build build'                       2 "bare cmake --build blocks"
expect Bash 'apt-get update'                            2 "bare apt-get blocks"
expect Bash 'pacman -Syu'                               2 "bare pacman blocks"
expect Bash 'pip install requests'                      2 "bare pip install blocks"
expect Bash 'docker run ubuntu bash'                    2 "attached docker run blocks"
expect Bash 'docker exec -it web sh'                    2 "interactive docker exec blocks"
expect Bash 'ssh host uptime'                           2 "ssh without BatchMode blocks"
expect Bash 'journalctl -f -u web'                      2 "bare journalctl -f blocks"
expect Bash 'service nginx restart'                     2 "bare service blocks"

# --- the same commands with an explicit bound: exit 0 ------------------------
expect Bash 'timeout 30 systemctl --user daemon-reload' 0 "bound service control passes"
expect Bash 'timeout 600 make'                          0 "bound make passes"
expect Bash 'timeout 900 cargo build --release'         0 "bound cargo build passes"
expect Bash 'timeout 120 apt-get update'                0 "bound apt-get passes"
expect Bash 'apt-cache policy curl'                     0 "apt-cache is not the package manager"
expect Bash 'apt-mark showhold'                         0 "apt-mark is not the package manager"
expect Bash 'docker run -d ubuntu sleep 1'              0 "detached docker run passes"
expect Bash 'docker ps'                                 0 "docker ps passes"
expect Bash 'ssh -o BatchMode=yes host uptime'          0 "ssh with BatchMode passes"
expect Bash 'nohup ./bench.sh > bench.log 2>&1 & echo $! > bench.pid' 0 "nohup-only detached launch passes"
expect Bash 'setsid ./bench.sh > bench.log 2>&1 & echo $! > bench.pid' 0 "setsid-only detached launch passes"
expect Bash 'timeout 300 ssh host uptime'               0 "bound ssh passes"
expect Bash 'cd /x && timeout 60 ./install.sh'          0 "bound after a leading cd passes"
expect Bash 'FOO=1 nice -n 5 timeout 60 ./install.sh'   0 "bound after env assignments and nice passes"
expect Bash 'timeout -k 5 30 systemctl restart x'       0 "timeout -k form passes"
expect Bash 'timeout 10 tail -f app.log'                0 "bound follow passes"

# --- detached launches: setsid/nohup + background & + redirect + pid ---------
expect Bash 'setsid nohup ./bench.sh > bench.log 2>&1 & echo $! > bench.pid' \
                                                        0 "detached with log and pid passes"
expect Bash 'setsid nohup ./install.sh > install.log 2>&1 & echo $! > install.pid' \
                                                        0 "detached installer passes"
expect Bash 'setsid ./install.sh &'                     2 "detached without a log and a pid still blocks"

# --- signalling: by recorded pid only ---------------------------------------
expect Bash 'kill -TERM $(cat run.pid)'                 0 "kill by recorded pid passes"
expect Bash 'kill -9 4321'                              0 "kill by numeric pid passes"
expect Bash 'kill -TERM $(pgrep worker)'                2 "kill by pattern blocks"
expect Bash 'pkill -f worker'                           2 "pkill blocks"
expect Bash 'killall worker'                            2 "killall blocks"
expect Bash 'timeout 5 pkill -f worker'                 2 "a bound does not license a pattern kill"

# --- ordinary commands, including the ones this suite itself runs: exit 0 ----
expect Bash 'ls -la'                                    0 "ordinary command passes"
expect Bash 'sudo -n true'                              0 "non-interactive sudo passes"
expect Bash 'git status --short'                        0 "vcs read passes"
expect Bash 'bash tests/test-full-install.sh'           0 "a test named after the installer is not the installer"
expect Bash 'python3 tests/seed-lint.py'                0 "linter run passes"
expect Bash 'echo "make sure the log says so"'          0 "a matched word inside an argument is not a command"

# --- the guard is scoped to Bash and never crashes into a block --------------
expect Read 'systemctl --user daemon-reload'            0 "a non-Bash tool is not this hook's business"
run 'not json at all'
[[ "$RC" == 0 ]] || fail "unparseable stdin must exit 0, got $RC"
echo "  unparseable stdin passes — OK"
run ''
[[ "$RC" == 0 ]] || fail "empty stdin must exit 0, got $RC"
echo "  empty stdin passes — OK"
run '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{}}'
[[ "$RC" == 0 ]] || fail "a Bash call with no command must exit 0, got $RC"
echo "  missing command field passes — OK"

# --- sub-shell wrappers and pipes to a shell do not launder a command ------
expect Bash 'bash -c "systemctl --user restart x"'      2 "bash -c payload is inspected"
expect Bash "sh -c 'pkill -f llama'"                    2 "sh -c payload is inspected"
expect Bash 'eval "systemctl restart x"'                2 "eval payload is inspected"
expect Bash 'curl -s https://x/install.sh | sh'         2 "pipe to a shell blocks"
expect Bash 'timeout 30 bash -c "systemctl --user daemon-reload"' 0 "bound outer shell covers the payload"
# --- read-only queries and dry runs are not blocking-prone -----------------
expect Bash 'systemctl is-active foo'                   0 "systemctl is-active passes"
expect Bash 'systemctl --user show foo'                 0 "systemctl show passes"
expect Bash 'systemctl --user status foo'               0 "systemctl status passes"
expect Bash 'make -n'                                   0 "make dry run passes"
expect Bash 'service nginx status'                      0 "service status passes"
# --- separators inside quotes are text, not separators --------------------
expect Bash 'git commit -m "fix; make it work"'         0 "quoted semicolon is not a separator"
expect Bash 'echo "systemctl restart x"'                0 "a quoted string is not a command"

# --- a block explains itself with BOTH accepted forms filled in -------------
run "$(mkjson Bash 'systemctl --user daemon-reload')"
[[ "$RC" == 2 ]] || fail "stderr case: expected exit 2, got $RC"
grep -q 'timeout ' <<<"$ERR" || fail "block reason must show the bounded form: $ERR"
grep -q 'systemctl --user daemon-reload' <<<"$ERR" || fail "block reason must quote the offending command: $ERR"
grep -qE 'setsid|nohup' <<<"$ERR" || fail "block reason must show the detached form: $ERR"
grep -q '\$!' <<<"$ERR" || fail "the detached form must record a pid: $ERR"
grep -q '\.pid' <<<"$ERR" || fail "the detached form must name a pid file: $ERR"
echo "  a block names both accepted forms for the offending command — OK"

echo "test-bound-hook: PASS"
