#!/usr/bin/env bash
# Bounded-execution guard contract: `integrations/claude-code/bound-hook.py` is
# a PreToolUse hook on the Bash tool. It must BLOCK (exit 2) a blocking-prone
# command that carries neither a bound nor a detached launch, and must stay out
# of the way (exit 0) everywhere else — including when it cannot understand its
# own input. Guards the class of defect where a guard hook either lets the
# hanging command through or, worse, bricks a session by blocking on a bug.
#
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
# --- a heredoc body is data, not commands -------------------------------------
expect Bash "$(printf "cat > brief.md <<'EOF'\nmake the tests pass\nnpm install stays prose\nEOF")" 0 "a heredoc body is not a command"
expect Bash "$(printf 'python3 - <<EOF\nmake = 1\nEOF\necho done')" 0 "an unquoted heredoc delimiter masks its body too"
expect Bash "$(printf "cat > f <<'EOF'\nprose\nEOF\nmake test")" 2 "a command after the heredoc still blocks"

# --- equivalent spellings of a command the hook already blocks (R7) ----------
# Each is the same operation as a row of BLOCKING_PRONE spelled another way: an
# abbreviated subcommand, a module invocation, or a drop-in for the same tool.
expect Bash 'npm i'                                     2 "npm i is npm install"
expect Bash 'npm add left-pad'                          2 "npm add is npm install"
expect Bash 'pnpm install'                              2 "pnpm install is a package install"
expect Bash 'pnpm i'                                    2 "pnpm i is a package install"
expect Bash 'pnpm add left-pad'                         2 "pnpm add is a package install"
expect Bash 'yarn install'                              2 "yarn install is a package install"
expect Bash 'yarn add left-pad'                         2 "yarn add is a package install"
expect Bash 'bun install'                               2 "bun install is a package install"
expect Bash 'bun add left-pad'                          2 "bun add is a package install"
expect Bash 'npm clean-install'                         2 "npm clean-install is npm ci"
expect Bash 'npm ic'                                    2 "npm ic is npm ci"
expect Bash 'python -m pip install requests'            2 "python -m pip install is pip install"
expect Bash 'python3 -m pip install requests'           2 "python3 -m pip install is pip install"
expect Bash 'python3.14 -m pip install requests'        2 "a versioned interpreter's -m pip install is pip install"
expect Bash 'uv pip install requests'                   2 "uv pip install is pip install"
expect Bash 'podman run alpine sh'                      2 "an attached podman run is an attached docker run"
expect Bash 'docker container run alpine sh'            2 "docker container run is docker run"
expect Bash 'nerdctl run alpine sh'                     2 "an attached nerdctl run is an attached docker run"
expect Bash 'docker exec -ti web sh'                    2 "docker exec -ti is docker exec -it"
expect Bash 'docker exec -i -t web sh'                  2 "docker exec -i -t is docker exec -it"
expect Bash 'docker exec --interactive --tty web sh'    2 "docker exec --interactive --tty is docker exec -it"
expect Bash 'podman exec -it web sh'                    2 "podman exec -it is docker exec -it"
expect Bash 'cargo b'                                   2 "cargo b is cargo build"
expect Bash 'gmake'                                     2 "gmake is make"
expect Bash 'gmake test'                                2 "gmake with a target is make with a target"
expect Bash 'tail -F app.log'                           2 "tail -F is tail -f"
expect Bash 'tail -n 20 --follow app.log'               2 "tail --follow is tail -f"
expect Bash 'journalctl --follow -u web'                2 "journalctl --follow is journalctl -f"
# the bounded form and the exemptions of the blocked row carry over
expect Bash 'timeout 60 npm i'                          0 "bound npm i passes"
expect Bash 'timeout 60 pnpm install'                   0 "bound pnpm install passes"
expect Bash 'timeout 60 yarn add left-pad'              0 "bound yarn add passes"
expect Bash 'timeout 60 bun install'                    0 "bound bun install passes"
expect Bash 'timeout 60 python -m pip install requests' 0 "bound python -m pip install passes"
expect Bash 'timeout 60 uv pip install requests'        0 "bound uv pip install passes"
expect Bash 'timeout 30 tail -F app.log'                0 "bound tail -F passes"
expect Bash 'timeout 30 journalctl --follow -u web'     0 "bound journalctl --follow passes"
expect Bash 'timeout 30 podman exec -it web sh'         0 "bound podman exec -it passes"
expect Bash 'timeout 600 gmake'                         0 "bound gmake passes"
expect Bash 'timeout 300 cargo b'                       0 "bound cargo b passes"
expect Bash 'gmake -n'                                  0 "gmake dry run passes"
expect Bash 'podman run -d alpine sleep 1'              0 "detached podman run passes"
# a non-equivalent command stays allowed, as before
expect Bash 'npm info left-pad'                         0 "npm info is not an install"
expect Bash 'npm list'                                  0 "npm list is not an install"
expect Bash 'npm run lint'                              0 "npm run is not an install"
expect Bash 'pnpm list'                                 0 "pnpm list is not an install"
expect Bash 'yarn why left-pad'                         0 "yarn why is not an install"
expect Bash 'bun run dev.ts'                            0 "bun run is not an install"
expect Bash 'python -m pytest tests'                    0 "python -m pytest is not pip"
expect Bash 'python3 -m pip list'                       0 "python -m pip list is not an install"
expect Bash 'python3 -m pip --version'                  0 "python -m pip --version is not an install"
expect Bash 'uv pip list'                               0 "uv pip list is not an install"
expect Bash 'uv run pytest'                             0 "uv run is not an install"
expect Bash 'podman ps'                                 0 "podman ps is not a run"
expect Bash 'docker container ls'                       0 "docker container ls is not a run"
expect Bash 'docker exec web ls'                        0 "a non-interactive docker exec passes"
expect Bash 'docker exec -i web cat /etc/hostname'      0 "docker exec -i alone is not a tty session"
expect Bash 'cargo test'                                0 "cargo test is not cargo build"
expect Bash 'tail -n 5 app.log'                         0 "tail without a follow flag passes"
expect Bash 'journalctl -u web --no-pager'              0 "journalctl without a follow flag passes"
expect Bash 'git log --follow src/a.py'                 0 "git log --follow is not a log follower"
expect Bash 'echo gmake'                                0 "gmake as an argument is not a command"
# quoted text and a heredoc body are data, whatever they spell
expect Bash 'echo "run npm i or pnpm install first"'    0 "a quoted npm i is text"
expect Bash "echo 'python -m pip install x; tail -F f'" 0 "a single-quoted spelling is text"
expect Bash "$(printf "cat > notes.md <<'EOF'\nuv pip install x\ngmake\ntail -F app.log\nEOF")" 0 "a heredoc body holding the new spellings is not a command"
expect Bash "$(printf "cat > f <<'EOF'\nprose\nEOF\npnpm install")" 2 "a new spelling after a heredoc still blocks"

# --- a block explains itself with BOTH accepted forms filled in -------------
run "$(mkjson Bash 'systemctl --user daemon-reload')"
[[ "$RC" == 2 ]] || fail "stderr case: expected exit 2, got $RC"
grep -q 'timeout ' <<<"$ERR" || fail "block reason must show the bounded form: $ERR"
grep -q 'systemctl --user daemon-reload' <<<"$ERR" || fail "block reason must quote the offending command: $ERR"
grep -qE 'setsid|nohup' <<<"$ERR" || fail "block reason must show the detached form: $ERR"
grep -q '\$!' <<<"$ERR" || fail "the detached form must record a pid: $ERR"
grep -q '\.pid' <<<"$ERR" || fail "the detached form must name a pid file: $ERR"
echo "  a block names both accepted forms for the offending command — OK"

# --- opencode: the envelope cypress-plugin.ts sends ---------------------------
# The OpenCode 2 plugin runs `python3 -S <core>` with the permission request's
# command in the PreToolUse shape, serialised by JSON.stringify (no spaces).
# It refuses the call only on exit 2 with a reason on stderr, and hands that
# stderr to the host as the refusal message, byte for byte. So an allowed
# command must exit 0 with stderr empty, and a refused one exit 2 with the
# whole reason on stderr and nothing on stdout.
OC_OUT=""
oc_run() {  # $1 = command -> sets RC, ERR (stderr) and OC_OUT (stdout)
  local payload
  payload="$(python3 -c 'import json,sys; print(json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": sys.argv[1]}}, separators=(",", ":")), end="")' "$1")"
  local f
  f="$(mktemp)"
  set +e
  OC_OUT="$(printf '%s' "$payload" | python3 -S "$HOOK" 2>"$f")"
  RC=$?
  set -e
  ERR="$(cat "$f")"; rm -f "$f"
}
oc_expect() {  # $1 = command  $2 = expected exit  $3 = label
  oc_run "$1"
  [[ "$RC" == "$2" ]] || fail "opencode: $3: expected exit $2, got $RC — command: $1 — stderr: $ERR"
  [[ -z "$OC_OUT" ]] || fail "opencode: $3: the core wrote to stdout, which the plugin ignores: $OC_OUT"
  if [[ "$2" == 0 ]]; then
    [[ -z "$ERR" ]] || fail "opencode: $3: an allowed command left stderr: $ERR"
  else
    [[ "$ERR" == "[bound-hook] BLOCKED: "* ]] || fail "opencode: $3: the refusal reason is not on stderr: $ERR"
    grep -q 'timeout ' <<<"$ERR" || fail "opencode: $3: the refusal does not carry the bounded form: $ERR"
  fi
  echo "  opencode: $3 — OK"
}
oc_expect 'npm install'                      2 "python3 -S, compact JSON: a bare package install is refused with its reason on stderr"
oc_expect 'pkill -f worker'                  2 "python3 -S, compact JSON: a pattern kill is refused with its reason on stderr"
oc_expect 'timeout 60 npm install'           0 "python3 -S, compact JSON: a bound install passes with stderr empty"
oc_expect 'ls -la'                           0 "python3 -S, compact JSON: an ordinary command passes with stderr empty"
oc_expect "$(printf 'echo "a\\nb" && make test')" 2 "python3 -S, compact JSON: a command holding a quote and a backslash still reaches the core whole"

echo "test-bound-hook: PASS"
