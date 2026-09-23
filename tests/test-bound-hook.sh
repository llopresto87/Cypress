#!/usr/bin/env bash
# Bounded-execution guard contract: `integrations/claude-code/bound-hook.py` is
# a PreToolUse hook on the Bash tool. It must BLOCK (exit 2) a blocking-prone
# command that carries neither a bound nor a detached launch, and must stay out
# of the way (exit 0) everywhere else — including when it cannot understand its
# own input. Guards the class of defect where a guard hook either lets the
# hanging command through or, worse, bricks a session by blocking on a bug.
#
# The scope widens past the guard to every Claude Code hook that reaches another
# host: VS Code's Copilot agent hooks read `.claude/settings.json`, so
# route-hook.py and status-hook.py run under Copilot too, on an envelope with no
# `session_id`, `source` fixed at "new" and fields Claude Code never sends.
# Copilot is a frozen host (ADR-0009): the seed stops designing for it, and
# these hooks must keep failing open on it anyway (the last section below).
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

# --- CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE (ADR-0009) -----------------
# Given the shipped route-hook.py and status-hook.py, placed where the installer
# puts them (.claude/), when each is fed a Copilot-shaped stdin (no session_id,
# source "new", an unknown extra field) and also an empty stdin, then each exits
# 0 and writes nothing to stderr. A non-zero exit or a traceback on stderr is
# what a host reads as a failed or blocking hook. Two plants: one with no graph
# (the degrade path) and one whose linter and register answer (the inject path).
FO="$(mktemp -d)"
trap 'rm -rf "$FO"' EXIT
for plant in bare graph; do
  mkdir -p "$FO/$plant/.cypress" "$FO/$plant/.claude"
  cp "$ROOT/integrations/claude-code/route-hook.py" "$ROOT/integrations/claude-code/status-hook.py" \
     "$FO/$plant/.claude/"
done
mkdir -p "$FO/graph/docs/graph"
printf '#!/usr/bin/env python3\nprint("task: stub")\nprint()\nprint("LOAD (1 node): root")\n' \
  >"$FO/graph/docs/graph/graph-lint.py"
printf '#!/usr/bin/env python3\nprint("0 open, 0 hotfix, 0 deferred")\n' \
  >"$FO/graph/docs/graph/status-register.py"

copilot_envelope() {  # $1 = hook event name  $2 = plant dir
  python3 - "$1" "$2" <<'PY'
import json, sys
event, cwd = sys.argv[1], sys.argv[2]
env = {"hook_event_name": event, "source": "new", "cwd": cwd,
       "copilotRequestId": "not-a-claude-code-field", "timestamp": "2026-09-23T00:00:00Z"}
if event == "UserPromptSubmit":
    env["prompt"] = "write failing tests for the installer host support tiers"
print(json.dumps(env))   # deliberately no session_id
PY
}

fail_open() {  # $1 = plant  $2 = hook file  $3 = raw stdin  $4 = label
  local rc err
  set +e
  err="$(cd "$FO/$1" && printf '%s' "$3" | python3 ".claude/$2" 2>&1 >/dev/null)"
  rc=$?
  set -e
  [[ "$rc" == 0 ]] \
    || fail "CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE: $2 ($1 plant, $4) exited $rc — stderr: $err"
  [[ -z "$err" ]] \
    || fail "CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE: $2 ($1 plant, $4) wrote to stderr: $err"
}

for plant in bare graph; do
  fail_open "$plant" route-hook.py  "$(copilot_envelope UserPromptSubmit "$FO/$plant")" "Copilot envelope"
  fail_open "$plant" status-hook.py "$(copilot_envelope SessionStart "$FO/$plant")"     "Copilot envelope"
  fail_open "$plant" route-hook.py  "" "empty stdin"
  fail_open "$plant" status-hook.py "" "empty stdin"
done
echo "  CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE: route-hook and status-hook fail open on a Copilot envelope and on empty stdin — OK"


# --- SPEC-0003 per-prompt injection: the Claude Code hooks (X101-X134, X142-X149)
# One case per contract of docs/specs/SPEC-0003-per-prompt-injection.md §4 and
# per tested failure of §7, bound by the fixed-width labels its §10 reserves.
# Every case prints `X1NN <SLUG>: … — OK`, so a label and its slug sit together.
# A case that also exercises a §7 failure mode names it after the contract,
# `X1NN <SLUG>; failure <FAILURE_SLUG>: …`, on its OK and its FAIL line alike.
# This extends the CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE section above: the
# same shipped hooks, copied into `.claude/` of a temp plant (a directory
# holding `.git/`, `.cypress/` and a stub `docs/graph/graph-lint.py`).
#
# The stub router answers like the real one: argparse reads `--plan`, and it
# prints `task: <value>`, a blank line, then a fixed §6-grammar body. Every
# test prompt is a sentinel that occurs nowhere in a stub body. Fault injection
# runs a hook through a `runpy` wrapper that patches `os.replace`/`os.rename`,
# so it works as root (spec §10, tester R12/R14). Every case runs; the block
# fails if any did. `SPEC0003_ONLY=X101,X113` runs a subset.
SPEC3_RC=0
mkdir -p "$FO/spec0003"
python3 - "$ROOT" "$FO/spec0003" <<'PY' || SPEC3_RC=1
import hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile, time, traceback
from pathlib import Path

SEED = Path(sys.argv[1])
WORK = Path(sys.argv[2])
HOOKS = SEED / "integrations" / "claude-code"
ONLY = {s.strip() for s in os.environ.get("SPEC0003_ONLY", "").split(",") if s.strip()}
os.umask(0o022)                                   # spec §4: tests run with umask 022

# §6 injection texts, compared exactly.
POINTER = "Route first: the kernel's FIRST MOVE and \u00a70 apply to this prompt."
SUGGESTION_HEADER = "Router suggestion (a keyword heuristic \u2014 reason over it):"
SURFACED_PREFIX = "Surfaced earlier this session: "
SURFACED_TAIL = " \u2014 open if not in view."
NEW_PREFIX = "New for this task: "
PEERS_HEADER = "Not suggested, not listed before (cross only if needed):"
NO_GRAPH = ("No knowledge graph found (docs/graph/). Use the canonical "
            "INSTALL_PROMPT.md; /initialize is the entry fork behind it \u2014 "
            "grow when there is source to scout, from-scratch when the "
            "repository is empty.")
# §6 constants used by value. route-hook.py is their one home; REFRESH_EVERY and
# ROUTER_TIMEOUT are read from the copied hook by regex instead (spec §10).
LEDGER_MAX_BYTES = 64 * 1024
GC_MAX_FILES = 32
GC_SCAN_MAX = 256
DAY = 86400
SID = "3b9f1c2e-5d4a-4e8b-9a61-0c7f2d8e1a44"
SID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
NODE_RE = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
RESET_RE = re.compile(r"^[a-z_-]{1,32}$")
ISO_RE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|\+00:00)$")
LEDGER_KEYS = {"version", "session_id", "prompt_count", "surfaced", "peers_seen", "last_reset"}

BODY = (
    "LOAD (2 nodes, ~900 tokens):\n"
    "  root                         knowledge graph router\n"
    "  skill.knowledge-graph        knowledge-graph authoring\n"
    "\n"
    "NOT LOADED (with the reason; cross only if the task requires it):\n"
    "  agent.implementer            peer of skill.knowledge-graph\n"
    "  domain.frontmatter           peer of skill.knowledge-graph\n")
NOTICES = ["  ! notice one: the widget terms matched nothing specific",
           "  ! notice two: consider the index before the nodes"]
NOTICE_BODY = "\n".join(NOTICES) + "\n\n" + BODY
# A NOT LOADED id that is also in LOAD, so `peers_seen = not_loaded - load` shows.
OVERLAP_BODY = BODY + "  skill.knowledge-graph        peer of root\n"
UNPARSEABLE = "no router header in this output\nsecond remainder line\n"


def parse_body(body):
    notices, load, nl, sect = [], [], [], None
    for ln in body.splitlines():
        if ln.startswith("  ! "):
            notices.append(ln)
        elif ln.startswith("LOAD ("):
            sect = load
        elif ln.startswith("NOT LOADED ("):
            sect = nl
        elif ln.startswith("  ") and sect is not None:
            sect.append((ln.split()[0], ln))
    return notices, load, nl


def ids(entries):
    return [i for i, _ in entries]


_, LOAD, NL = parse_body(BODY)
LOAD_IDS, NL_IDS = ids(LOAD), ids(NL)

STUB = r'''#!/usr/bin/env python3
import argparse, json, sys, time
from pathlib import Path
MODE = %r
BODY = %r
if MODE == "argv":                       # X102 only: the log is a file in the plant
    Path(__file__).with_name("stub-argv.json").write_text(json.dumps(sys.argv[1:]))
ap = argparse.ArgumentParser()
ap.add_argument("--plan")
args, _ = ap.parse_known_args()
plan = args.plan or ""
if MODE == "sleep":
    time.sleep(3)
if MODE == "empty":
    sys.exit(0)
if MODE == "noecho":
    sys.stdout.write(BODY)
elif MODE == "otherecho":
    sys.stdout.write("task: a different task entirely\n\n" + BODY)
elif MODE == "noblank":
    sys.stdout.write("task: " + plan + "\n" + BODY)
else:
    sys.stdout.write("task: " + plan + "\n\n" + BODY)
sys.exit(1 if MODE == "exit1" else 0)
'''
REGISTER = 'print("0 open, 0 hotfix, 0 deferred")\n'
WRAPPER = WORK / "fault-wrapper.py"
WRAPPER.write_text(r'''
import errno, os, runpy, sys
kind, hook = sys.argv[1], sys.argv[2]
def _refuse(*a, **k):
    if kind == "perm":
        raise PermissionError(errno.EACCES, "injected by the SPEC-0003 fault wrapper")
    raise OSError(errno.EIO, "injected by the SPEC-0003 fault wrapper")
if kind == "statfail":                    # X147: the ledger stat fails as a real one would,
    _real_stat = os.stat                  # carrying the file name in the exception
    def _stat(path, *a, dir_fd=None, **k):
        if dir_fd is not None and str(path).endswith(".json"):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return _real_stat(path, *a, dir_fd=dir_fd, **k)
    os.stat = _stat
elif kind == "scandirfail":               # X149: GC's directory scan fails
    def _scandir(*a, **k):
        raise OSError(errno.EIO, os.strerror(errno.EIO))
    os.supports_fd.add(_scandir)          # the hook's capability probe looks it up here
    os.scandir = _scandir
else:
    os.replace = _refuse
    if kind != "perm":
        os.rename = _refuse
sys.argv = [hook]
runpy.run_path(hook, run_name="__main__")
''')


class CaseFail(Exception):
    pass


def check(cond, msg):
    if not cond:
        raise CaseFail(msg)


class Plant:
    def __init__(self, base, name="plant", graph=True, cypress=True, git=True,
                 hooks=("route-hook.py", "status-hook.py"), register=False,
                 mode="echo", body=BODY):
        self.dir = base / name
        (self.dir / ".claude").mkdir(parents=True)
        if git:
            (self.dir / ".git").mkdir()
        if cypress:
            (self.dir / ".cypress").mkdir()
        for h in hooks:
            shutil.copy(HOOKS / h, self.dir / ".claude" / h)
        if graph:
            (self.dir / "docs" / "graph").mkdir(parents=True)
            self.stub(mode, body)
        if register:
            (self.dir / "docs" / "graph").mkdir(parents=True, exist_ok=True)
            (self.dir / "docs" / "graph" / "status-register.py").write_text(REGISTER)

    def stub(self, mode="echo", body=BODY):
        (self.dir / "docs" / "graph" / "graph-lint.py").write_text(STUB % (mode, body))

    @property
    def sess(self):
        return self.dir / ".cypress" / "session"

    def ledger(self, sid=SID):
        return self.sess / f"{sid}.json"

    def hook(self, name="route-hook.py"):
        return self.dir / ".claude" / name


def ensure_session_dir(plant, mode=0o700):
    plant.sess.mkdir(parents=True, exist_ok=True)
    os.chmod(plant.sess, mode)
    gi = plant.sess / ".gitignore"
    if not gi.exists() and not gi.is_symlink():
        gi.write_text("*\n")


def ledger_doc(sid=SID, prompt_count=1, surfaced=None, peers_seen=None,
               last_reset=None, version=1):
    return {"version": version, "session_id": sid, "prompt_count": prompt_count,
            "surfaced": sorted(LOAD_IDS if surfaced is None else surfaced),
            "peers_seen": sorted(NL_IDS if peers_seen is None else peers_seen),
            "last_reset": last_reset}


def write_ledger(plant, sid=SID, raw=None, fmode=0o600, age=60, **fields):
    """A §6 ledger for `sid`, mode 0600 in a 0700 session directory, whose mtime
    is `age` seconds in the past so an unchanged mtime is observable."""
    ensure_session_dir(plant)
    p = plant.ledger(sid)
    data = raw if raw is not None else json.dumps(ledger_doc(sid, **fields))
    p.write_bytes(data.encode() if isinstance(data, str) else data)
    os.chmod(p, fmode)
    t = time.time() - age
    os.utime(p, (t, t))
    return p


def sig(p):
    st = os.lstat(p)
    return (Path(p).read_bytes(), st.st_mtime_ns, st.st_ino)


def ledger_problems(path, sid=SID):
    if not path.is_file() or path.is_symlink():
        return [f"{path.name}: no regular ledger file"]
    raw = path.read_bytes()
    out = []
    if len(raw) > LEDGER_MAX_BYTES:
        out.append(f"{len(raw)} bytes, over LEDGER_MAX_BYTES")
    try:
        d = json.loads(raw)
    except Exception as e:                        # noqa: BLE001
        return [f"not JSON ({e})"]
    if not isinstance(d, dict) or set(d) != LEDGER_KEYS:
        return [f"keys {sorted(d) if isinstance(d, dict) else type(d).__name__} != {sorted(LEDGER_KEYS)}"]
    if d["version"] != 1 or type(d["version"]) is not int:
        out.append(f"version {d['version']!r}")
    if d["session_id"] != sid:
        out.append(f"session_id {d['session_id']!r} != {sid!r}")
    if type(d["prompt_count"]) is not int or d["prompt_count"] < 0:
        out.append(f"prompt_count {d['prompt_count']!r}")
    for k in ("surfaced", "peers_seen"):
        v = d[k]
        if (not isinstance(v, list) or not all(isinstance(x, str) and NODE_RE.match(x) for x in v)
                or v != sorted(set(v)) or len(v) > 512):
            out.append(f"{k} {v!r} is not a sorted unique list of node ids")
    lr = d["last_reset"]
    if lr is not None and not (isinstance(lr, dict) and set(lr) == {"source", "at"}
                               and isinstance(lr["source"], str) and RESET_RE.match(lr["source"])
                               and isinstance(lr["at"], str) and ISO_RE.match(lr["at"])):
        out.append(f"last_reset {lr!r}")
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        out.append(f"mode {oct(stat.S_IMODE(path.stat().st_mode))}, not 0600")
    return out


def read_ledger(plant, sid=SID):
    return json.loads(plant.ledger(sid).read_text())


class Run:
    def __init__(self, rc, out, err, timed_out=False):
        self.rc, self.out, self.err, self.timed_out = rc, out, err, timed_out
        self.inj = None
        self.envelope_ok = False
        if out.strip():
            try:
                lines = out.strip("\n").split("\n")
                obj = json.loads(lines[0])
                self.inj = obj["hookSpecificOutput"]["additionalContext"]
                self.envelope_ok = (len(lines) == 1 and isinstance(self.inj, str)
                                    and isinstance(obj["hookSpecificOutput"].get("hookEventName"), str))
            except Exception:                     # noqa: BLE001
                self.inj = None

    def ctx(self):
        return (f"exit {self.rc}; stdout {self.out[:600]!r}; stderr {self.err[:600]!r}"
                + ("; TIMED OUT" if self.timed_out else ""))


MISSING = object()


def run_hook(plant, stdin, hook=None, wrapper=None, timeout=20):
    hook = hook or plant.hook()
    cmd = [sys.executable, str(hook)]
    if wrapper:
        cmd = [sys.executable, str(WRAPPER), wrapper, str(hook)]
    try:
        r = subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                           timeout=timeout, cwd=str(plant.dir))
    except subprocess.TimeoutExpired as e:
        def s(x):
            return x.decode(errors="replace") if isinstance(x, bytes) else (x or "")
        return Run(None, s(e.stdout), s(e.stderr), timed_out=True)
    return Run(r.returncode, r.stdout, r.stderr)


def route(plant, prompt, sid=SID, envelope=None, **kw):
    env = envelope if envelope is not None else {
        "hook_event_name": "UserPromptSubmit", "prompt": prompt, "cwd": str(plant.dir)}
    if envelope is None and sid is not MISSING:
        env["session_id"] = sid
    r = run_hook(plant, json.dumps(env), **kw)
    check(r.rc == 0, f"the hook must exit 0 — {r.ctx()}")
    return r


def status(plant, sid=SID, source=MISSING, **kw):
    env = {"hook_event_name": "SessionStart", "cwd": str(plant.dir)}
    if sid is not MISSING:
        env["session_id"] = sid
    if source is not MISSING:
        env["source"] = source
    r = run_hook(plant, json.dumps(env), hook=plant.hook("status-hook.py"), **kw)
    check(r.rc == 0, f"status-hook must exit 0 — {r.ctx()}")
    return r


def full_text(remainder):
    return POINTER + "\n\n" + SUGGESTION_HEADER + "\n" + remainder.strip()


def is_full(r, remainder=BODY):
    return r.inj is not None and r.inj.rstrip() == full_text(remainder)


def is_pointer_only(r):
    return r.inj is not None and r.inj.rstrip("\n") == POINTER


def is_reminder(r):
    return (r.inj is not None and r.inj.split("\n")[0] == POINTER
            and SUGGESTION_HEADER not in r.inj and len(r.inj.rstrip("\n").split("\n")) >= 2)


def one_err_line(r):
    return r.err.count("\n") == 1 and r.err.endswith("\n")


def expect_full(r, what, remainder=BODY):
    check(is_full(r, remainder), f"{what}: expected full mode (pointer line, blank, "
          f"suggestion header, router output minus the echo) — {r.ctx()}")


def expect_one_err(r, what):
    check(one_err_line(r), f"{what}: expected exactly one stderr line — {r.ctx()}")


def snapshot(root, skip=()):
    snap = {}
    for dp, dns, fns in os.walk(root, followlinks=False):
        rel_dp = os.path.relpath(dp, root)
        dns[:] = [d for d in dns if d != "__pycache__"
                  and os.path.normpath(os.path.join(rel_dp, d)) not in skip]
        for n in dns + fns:
            p = os.path.join(dp, n)
            rel = os.path.normpath(os.path.relpath(p, root))
            if rel in skip:
                continue
            st = os.lstat(p)
            if stat.S_ISREG(st.st_mode):
                h = hashlib.sha256(Path(p).read_bytes()).hexdigest()
                snap[rel] = ("f", stat.S_IMODE(st.st_mode), h, st.st_mtime_ns)
            elif stat.S_ISLNK(st.st_mode):
                snap[rel] = ("l", os.readlink(p))
            elif stat.S_ISDIR(st.st_mode):
                snap[rel] = ("d", stat.S_IMODE(st.st_mode))
            else:
                snap[rel] = ("o", stat.S_IFMT(st.st_mode), st.st_mtime_ns)
    return snap


def snap_diff(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def session_bytes(plant):
    out = b""
    if plant.sess.is_dir():
        for p in plant.sess.rglob("*"):
            if p.is_file() and not p.is_symlink():
                out += p.read_bytes()
    return out


def read_constant(hook_path, name):
    m = re.search(rf"^{name}\s*=\s*([0-9][0-9_.]*)\s*(?:#.*)?$", hook_path.read_text(), re.M)
    return m and float(m.group(1).replace("_", ""))


def rewrite_constant(hook_path, name, value):
    src = hook_path.read_text()
    new, n = re.subn(rf"^({name}\s*=\s*)[0-9][0-9_.]*", rf"\g<1>{value}", src, flags=re.M)
    check(n == 1, f"could not rewrite {name} in the hook copy")
    hook_path.write_text(new)


CASES = []


def case(label, slug):
    def deco(fn):
        CASES.append((label, slug, fn))
        return fn
    return deco


# ---------------------------------------------------------------- echo, pointer
@case("X101", "ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO")
def x101(base):
    p = Plant(base, graph=False)
    g = p.dir / "docs" / "graph"
    (g / "nodes").mkdir(parents=True)
    for f in ("graph-lint.py", "frontmatter.py"):
        shutil.copy(SEED / "templates" / "knowledge-graph" / f, g / f)
    (g / "nodes" / "root.md").write_text(
        "---\nid: root\ntier: 2\nkind: root\ntitle: minimal plant root\n"
        "owns: [root.identity]\nrequires: []\npeers: [subsystem.widgets]\n"
        "load_when: [\"anything\"]\nest_tokens: 100\n---\n# root\n")
    (g / "nodes" / "subsystem.widgets.md").write_text(
        "---\nid: subsystem.widgets\ntier: 2\nkind: subsystem\ntitle: widgets subsystem\n"
        "owns: [widgets.core]\nrequires: [root]\nload_when: [\"widgets\"]\n"
        "est_tokens: 100\n---\n# widgets\n")
    lines = ["kqv mlorp one", "brzt snav two", "qq fwee three",
             "zz-sentinel-echo-4412", "plonk grr five", "xxv yyw six"]
    r = route(p, "\n".join(lines))
    check(r.inj is not None, f"no injection — {r.ctx()}")
    check("zz-sentinel-echo-4412" not in r.inj, f"the sentinel (prompt line 4) was echoed: {r.inj!r}")
    for ln in lines:
        check(ln not in r.inj, f"prompt line {ln!r} was echoed: {r.inj!r}")
    check(not any(l.startswith("task:") for l in r.inj.split("\n")), f"a `task:` line survived: {r.inj!r}")
    check("LOAD (" in r.inj, f"the router's LOAD header is gone, so the strip took the body: {r.inj!r}")
    return "a six-line prompt, real router: no prompt line, no `task:` line, LOAD kept"


@case("X102", "ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE")
def x102(base):
    p = Plant(base, mode="argv")
    prompt = "--zqsentinel-argv-0102"
    r = route(p, prompt)
    log = p.dir / "docs" / "graph" / "stub-argv.json"
    check(log.is_file(), f"the stub router was never run — {r.ctx()}")
    argv = json.loads(log.read_text())
    plans = [a for a in argv if a.startswith("--plan=")]
    check(len(plans) == 1 and plans[0] == "--plan=" + prompt,
          f"expected exactly one `--plan=<prompt>` element, argv was {argv!r}")
    check(r.inj is not None and all(line in r.inj for _, line in LOAD + NL),
          f"the injection does not carry the stub's body — {r.ctx()}")
    return "a `--`-prefixed prompt reaches the router as one `--plan=` element"


@case("X103", "ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN")
def x103(base):
    p = Plant(base)
    led = write_ledger(p)
    for what, prompt in (("NUL byte", "zq-nul-0103 before\x00after the byte"),
                         ("2 000 000 characters", "zq-big-0103 " + "a" * 2_000_000)):
        before = sig(led)
        r = route(p, prompt, timeout=60)
        check(r.envelope_ok, f"{what}: stdout is not one valid hook envelope — {r.ctx()}")
        check(is_pointer_only(r), f"{what}: expected the pointer line alone — {r.ctx()}")
        check(sig(led) == before, f"{what}: the ledger changed (bytes or mtime)")
        check("Traceback" not in r.err, f"{what}: a traceback reached stderr — {r.ctx()}")
    return "NUL byte and 2 000 000-character prompts: pointer line alone, ledger untouched"


@case("X104", "ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY")
def x104(base):
    p = Plant(base)
    led = write_ledger(p)
    sentinel = "zq-sentinel-0104"
    prompt = sentinel + " plan the widget ledger"
    for mode, what in (("noecho", "no `task:` line"), ("otherecho", "`task:` with other text"),
                       ("noblank", "exact echo line, no blank line after it")):
        p.stub(mode)
        before = sig(led)
        r = route(p, prompt)
        check(is_pointer_only(r), f"{what}: expected the pointer line alone — {r.ctx()}")
        check(sentinel not in (r.inj or "") and sentinel not in r.err,
              f"{what}: the prompt sentinel leaked into the injection or stderr — {r.ctx()}")
        check(sentinel.encode() not in session_bytes(p), f"{what}: the sentinel is in .cypress/session/")
        check(sig(led) == before, f"{what}: the ledger changed (bytes or mtime)")
    return "three outputs without the exact echo prefix: pointer line alone, nothing leaked"


@case("X105", "ROUTE_HOOK_POINTS_AT_KERNEL")
def x105(base):
    p = Plant(base)
    r = route(p, "zq-sentinel-0105 widget ledger work")
    check(r.inj is not None and r.inj.split("\n")[0] == POINTER,
          f"the first line is not the §6 pointer line — {r.ctx()}")
    return "the first injected line is the pointer line, byte for byte"


# ---------------------------------------------------------------- ledger modes
@case("X106", "LEDGER_FIRST_PROMPT_FULL")
def x106(base):
    p = Plant(base, body=OVERLAP_BODY)
    sentinel = "zq-sentinel-0106"
    r = route(p, sentinel + " first widget prompt")
    expect_full(r, "first prompt", OVERLAP_BODY)
    check(r.err == "", f"expected no stderr — {r.ctx()}")
    check(p.ledger().is_file(), "no ledger was written")
    d = read_ledger(p)
    _, load, nl = parse_body(OVERLAP_BODY)
    check(d.get("prompt_count") == 1, f"prompt_count {d.get('prompt_count')!r}, expected 1")
    check(d.get("surfaced") == sorted(ids(load)), f"surfaced {d.get('surfaced')!r} != LOAD ids")
    want_peers = sorted(set(ids(nl)) - set(ids(load)))
    check(d.get("peers_seen") == want_peers, f"peers_seen {d.get('peers_seen')!r} != {want_peers!r}")
    check(sentinel.encode() not in session_bytes(p) and sentinel not in r.err,
          "the prompt sentinel reached .cypress/session/ or stderr")
    return "no ledger: full mode, ledger count 1 with LOAD ids and NOT LOADED minus LOAD"


@case("X107", "LEDGER_LATER_PROMPT_REMINDER")
def x107(base):
    p = Plant(base)
    first = route(p, "zq-sentinel-0107a first widget prompt")
    expect_full(first, "first prompt")
    r = route(p, "zq-sentinel-0107b second widget prompt")
    want = POINTER + "\n" + SURFACED_PREFIX + ", ".join(LOAD_IDS) + SURFACED_TAIL
    check(r.inj is not None and r.inj.rstrip("\n") == want,
          f"expected exactly the two reminder lines {want!r} — {r.ctx()}")
    return "second prompt, nothing new: exactly the pointer and the Surfaced line"


@case("X108", "REMINDER_KEEPS_NOTICE_LINES")
def x108(base):
    p = Plant(base, body=NOTICE_BODY)
    write_ledger(p)
    r = route(p, "zq-sentinel-0108 widget ledger work")
    lines = (r.inj or "").split("\n")
    check(lines[:1 + len(NOTICES)] == [POINTER] + NOTICES,
          f"the notice lines are not verbatim straight after the pointer line — {r.ctx()}")
    return "reminder mode keeps every notice line, right after the pointer"


@case("X109", "REMINDER_SAYS_SURFACED_NEVER_LOADED")
def x109(base):
    p = Plant(base, body=NOTICE_BODY)
    write_ledger(p, surfaced=["root"], peers_seen=["agent.implementer"])
    r = route(p, "zq-sentinel-0109 widget ledger work")
    check(is_reminder(r), f"expected reminder mode — {r.ctx()}")
    lines = r.inj.split("\n")
    check(any(l.startswith(SURFACED_PREFIX) for l in lines), f"no Surfaced line — {r.ctx()}")
    for l in lines:
        if re.search(r"(?<![\w.-])root(?![\w.-])", l):
            check(l.startswith(SURFACED_PREFIX), f"a known id is named outside the Surfaced line: {l!r}")
        check(not re.search("loaded", l, re.I), f"a line says `loaded`: {l!r}")
    return "a known id is named only on the Surfaced line; no line says loaded"


@case("X110", "LEDGER_NEW_IDS_LISTED")
def x110(base):
    p = Plant(base)
    write_ledger(p, surfaced=["root"])
    r = route(p, "zq-sentinel-0110 widget ledger work")
    lines = (r.inj or "").split("\n")
    head = NEW_PREFIX + "skill.knowledge-graph"
    check(head in lines, f"no `{head}` line — {r.ctx()}")
    i = lines.index(head)
    entry = dict(LOAD)["skill.knowledge-graph"]
    check(lines[i + 1:i + 2] == [entry], f"the new id's LOAD entry line does not follow verbatim — {r.ctx()}")
    check("skill.knowledge-graph" in read_ledger(p).get("surfaced", []), "the new id was not added to surfaced")
    return "an id outside surfaced gets `New for this task:` and its entry line"


@case("X111", "REMINDER_DROPS_PEERS_ALREADY_SHOWN")
def x111(base):
    p = Plant(base)
    write_ledger(p, peers_seen=["agent.implementer"])
    r = route(p, "zq-sentinel-0111 widget ledger work")
    check(is_reminder(r), f"expected reminder mode — {r.ctx()}")
    lines = r.inj.split("\n")
    check(PEERS_HEADER in lines, f"no `{PEERS_HEADER}` line — {r.ctx()}")
    i = lines.index(PEERS_HEADER)
    check(dict(NL)["domain.frontmatter"] in lines[i + 1:], f"the unseen peer's entry line is missing — {r.ctx()}")
    check(not any("agent.implementer" in l for l in lines), f"a peer already shown was repeated — {r.ctx()}")
    check("domain.frontmatter" in read_ledger(p).get("peers_seen", []), "the unseen peer was not added to peers_seen")
    return "a peer already shown is dropped; the unseen one is listed and recorded"


@case("X112", "LEDGER_EVERY_LOAD_ID_NAMED")
def x112(base):
    n = read_constant(HOOKS / "route-hook.py", "REFRESH_EVERY")
    problems = [] if n else ["REFRESH_EVERY: no module-level integer literal in route-hook.py"]
    states = [("absent", None), ("prompt_count 0", dict(prompt_count=0, surfaced=[], peers_seen=[])),
              ("count 1, all surfaced", dict()), ("count 1, one outside", dict(surfaced=["root"])),
              ("invalid JSON", dict(raw="{not json"))]
    if n:
        states.append(("count REFRESH_EVERY", dict(prompt_count=int(n))))
    for i, (what, st) in enumerate(states):
        p = Plant(base, name=f"plant{i}")
        if st is not None:
            write_ledger(p, **st)
        r = route(p, "zq-sentinel-0112 widget ledger work")
        for lid in LOAD_IDS:
            if r.inj is None or not re.search(rf"(?<![\w.-]){re.escape(lid)}(?![\w.-])", r.inj):
                problems.append(f"{what}: LOAD id {lid} is not named — {r.ctx()}")
    check(not problems, "; ".join(problems))
    return "every LOAD id is named in each of the six ledger states"


@case("X113", "LEDGER_REFRESH_EVERY_N")
def x113(base):
    n = read_constant(HOOKS / "route-hook.py", "REFRESH_EVERY")
    check(n and n == int(n) and n >= 2, "REFRESH_EVERY: no module-level integer literal >= 2 in route-hook.py")
    n = int(n)
    p = Plant(base, name="at-n")
    write_ledger(p, prompt_count=n, surfaced=LOAD_IDS + ["zz.refresh-sentinel"])
    r = route(p, "zq-sentinel-0113 widget ledger work")
    expect_full(r, f"count {n}")
    d = read_ledger(p)
    check(d.get("prompt_count") == 1 and d.get("surfaced") == sorted(LOAD_IDS)
          and d.get("peers_seen") == sorted(set(NL_IDS) - set(LOAD_IDS)),
          f"after a refresh the ledger must be rebuilt from this injection alone: {d!r}")
    p = Plant(base, name="below-n")
    write_ledger(p, prompt_count=n - 1)
    check(is_reminder(route(p, "zq-sentinel-0113 widget ledger work")), f"count {n - 1}: expected reminder mode")
    for count, want_full in ((3, True), (2, False)):
        p = Plant(base, name=f"n3-{count}")
        rewrite_constant(p.hook(), "REFRESH_EVERY", 3)
        write_ledger(p, prompt_count=count)
        r = route(p, "zq-sentinel-0113 widget ledger work")
        check(is_full(r) if want_full else is_reminder(r),
              f"REFRESH_EVERY rewritten to 3, count {count}: expected "
              f"{'full' if want_full else 'reminder'} mode — {r.ctx()}")
    return f"count REFRESH_EVERY ({n}) refreshes and rebuilds; N-1 reminds; holds when N is 3"


@case("X114", "LEDGER_TRIVIAL_PROMPT_UNTOUCHED")
def x114(base):
    p = Plant(base)
    led = write_ledger(p)
    for prompt in ("thank you", "Continue", "short"):
        before = sig(led)
        r = route(p, prompt)
        check(r.out == "", f"{prompt!r}: trivial prompt wrote to stdout — {r.ctx()}")
        check(sig(led) == before, f"{prompt!r}: the ledger changed (bytes or mtime)")
    return "trivial prompts: no stdout, ledger byte-identical, same mtime"


@case("X115", "LEDGER_UNUSED_WITHOUT_GRAPH")
def x115(base):
    p = Plant(base, graph=False)
    r = route(p, "zq-sentinel-0115 widget ledger work")
    check(r.inj == NO_GRAPH, f"expected the unchanged no-graph message — {r.ctx()}")
    check(not p.sess.exists() or not any(p.sess.iterdir()), "a file was created under .cypress/session/")
    return "no graph: the existing message, nothing under .cypress/session/"


@case("X116", "LEDGER_NEVER_EMITS_UNROUTED_ID")
def x116(base):
    p = Plant(base)
    write_ledger(p, surfaced=LOAD_IDS + ["zz.unrouted-sentinel"],
                 peers_seen=NL_IDS + ["zz.unrouted-sentinel"],
                 last_reset={"source": "zz-sentinel", "at": "2026-09-23T00:00:00Z"})
    r = route(p, "zq-sentinel-0116 widget ledger work")
    check(r.inj is not None, f"no injection — {r.ctx()}")
    for s in ("zz.unrouted-sentinel", "zz-sentinel"):
        check(s not in r.inj, f"ledger content {s!r} reached the injection: {r.inj!r}")
    return "ids and sources only the ledger holds never reach the injection"


@case("X117", "UNPARSEABLE_ROUTER_OUTPUT_FULL")
def x117(base):
    p = Plant(base, body=UNPARSEABLE)
    led = write_ledger(p)
    before = sig(led)
    r = route(p, "zq-sentinel-0117 widget ledger work")
    expect_full(r, "no LOAD header after the echo", UNPARSEABLE)
    check(sig(led) == before, "the ledger changed (bytes or mtime) on unparseable output")
    return "echo prefix but no LOAD header: full mode with the remainder, ledger untouched"


# ---------------------------------------------------------------- session identity
@case("X118", "LEDGER_ABSENT_SESSION_ID_FULL")
def x118(base):
    p = Plant(base)
    prompt = "zq-sentinel-0118 widget ledger work"
    copilot = {"hook_event_name": "UserPromptSubmit", "source": "new", "cwd": str(p.dir),
               "copilotRequestId": "not-a-claude-code-field", "prompt": prompt}
    # `"session_id": null` is absent, not refused: Copilot's fail-open intent,
    # so no stderr line (review of 2deda6a..343445f, nit).
    for what, env in (("Copilot envelope", copilot), ("sessionId spelling", dict(copilot, sessionId=SID)),
                      ("session_id null", dict(copilot, session_id=None))):
        for turn in (1, 2):
            r = route(p, prompt, envelope=env)
            expect_full(r, f"{what}, prompt {turn}")
            check(r.err == "", f"{what}, prompt {turn}: expected no stderr — {r.ctx()}")
            check(not p.sess.exists(), f"{what}: something was created under .cypress/session/")
    return "no `session_id` key, or a null one: full mode every time, no file, no stderr"


INVALID_SIDS = ["../../escape", "a/b", ".hidden", "", "a" * 129, 12345, "ab\x00cd"]


@case("X119", "LEDGER_INVALID_SESSION_ID_FULL; failure SESSION_ID_REFUSED")
def x119(base):
    p = Plant(base)
    for sid in INVALID_SIDS:
        before = snapshot(base)
        r = route(p, "zq-sentinel-0119 widget ledger work", sid=sid)
        expect_full(r, f"session_id {sid!r}")
        diff = snap_diff(before, snapshot(base))
        check(not diff, f"session_id {sid!r}: the plant or its parent changed: {diff}")
        expect_one_err(r, f"session_id {sid!r}")
        if sid != "":
            check(str(sid) not in r.err, f"session_id {sid!r}: stderr carries the raw id")
    return "seven unsafe ids: full mode, one stderr line without the id, nothing written"


@case("X120", "LEDGER_CORRUPT_FULL; failure LEDGER_UNUSABLE")
def x120(base):
    p = Plant(base)
    good = ledger_doc()
    variants = [
        ("invalid JSON", "{not valid json"),
        ("extra key", json.dumps(dict(good, extra=1))),
        ("id failing the pattern", json.dumps(dict(good, surfaced=sorted(["root", "Bad Id!"])))),
        ("session_id not the stem", json.dumps(dict(good, session_id="someone-else-0000"))),
        ("over LEDGER_MAX_BYTES", json.dumps(good) + " " * (LEDGER_MAX_BYTES + 100)),
        ("60 000 `[`", "[" * 60000),
    ]
    for what, raw in variants:
        write_ledger(p, raw=raw)
        r = route(p, "zq-sentinel-0120 widget ledger work")
        expect_full(r, what)
        expect_one_err(r, what)
        probs = ledger_problems(p.ledger())
        check(not probs, f"{what}: not replaced by a valid version-1 ledger: {probs}")
    return "six corrupt ledgers: full mode, one stderr line, replaced by a valid v1 ledger"


@case("X121", "LEDGER_UNKNOWN_VERSION_FULL; failure LEDGER_UNUSABLE")
def x121(base):
    p = Plant(base)
    write_ledger(p, version=2, prompt_count=3)
    r = route(p, "zq-sentinel-0121 widget ledger work")
    expect_full(r, "version 2")
    expect_one_err(r, "version 2")
    probs = ledger_problems(p.ledger())
    check(not probs and read_ledger(p)["prompt_count"] == 1,
          f"not replaced by a valid v1 ledger with prompt_count 1: {probs or read_ledger(p)}")
    return "version 2: full mode, one stderr line, replaced with a v1 ledger at count 1"


@case("X122", "LEDGER_EXPIRED_FULL; failure LEDGER_UNUSABLE")
def x122(base):
    p = Plant(base)
    write_ledger(p, prompt_count=3, age=DAY)            # older than LEDGER_TTL (12 h)
    r = route(p, "zq-sentinel-0122 widget ledger work")
    expect_full(r, "expired ledger")
    expect_one_err(r, "expired ledger")
    probs = ledger_problems(p.ledger())
    check(not probs and read_ledger(p)["prompt_count"] == 1,
          f"not replaced by a valid v1 ledger with prompt_count 1: {probs or read_ledger(p)}")
    return "a ledger older than LEDGER_TTL: full mode, one stderr line, count 1"


# ---------------------------------------------------------------- reset
def expect_reset(p, source_want, what):
    check(p.ledger().is_file(), f"{what}: the ledger is gone")
    probs = ledger_problems(p.ledger())
    check(not probs, f"{what}: the reset ledger is not a valid v1 ledger: {probs}")
    d = read_ledger(p)
    check(d["prompt_count"] == 0 and d["surfaced"] == [] and d["peers_seen"] == []
          and isinstance(d["last_reset"], dict) and d["last_reset"].get("source") == source_want,
          f"{what}: expected count 0, empty sets, last_reset.source {source_want!r}; got {d!r}")


@case("X123", "STATUS_HOOK_RESETS_LEDGER")
def x123(base):
    sources = [(s, s) for s in ("startup", "resume", "clear", "compact", "fork", "new")]
    sources += [("Weird Source!", "unknown"), (MISSING, "unknown")]
    for i, (src, want) in enumerate(sources):
        what = f"source {'absent' if src is MISSING else repr(src)}"
        p = Plant(base, name=f"plant{i}", register=True)
        write_ledger(p, prompt_count=3)
        status(p, source=src)
        expect_reset(p, want, what)
        expect_full(route(p, "zq-sentinel-0123 widget ledger work"), f"{what}, next prompt")
    return "every SessionStart source resets the ledger; the next prompt is full"


@case("X124", "STATUS_HOOK_NO_LEDGER_WRITES_NOTHING")
def x124(base):
    p = Plant(base, register=True)
    for what, sid in [("valid id, no ledger", SID), ("no session_id", MISSING)] + \
                     [(f"invalid id {s!r}", s) for s in INVALID_SIDS]:
        before = snapshot(p.dir / ".cypress")
        status(p, sid=sid, source="startup")
        diff = snap_diff(before, snapshot(p.dir / ".cypress"))
        check(not diff, f"{what}: status-hook wrote under .cypress/: {diff}")
    expect_full(route(p, "zq-sentinel-0124 widget ledger work"), "next prompt for the valid id")
    return "no ledger, no id or a bad id: status-hook writes nothing; next prompt full"


@case("X125", "STATUS_HOOK_RESETS_WITHOUT_REGISTER")
def x125(base):
    p = Plant(base)                                     # a graph, no status-register.py
    write_ledger(p, prompt_count=3)
    r = status(p, source="startup")
    expect_reset(p, "startup", "no register")
    check(r.out == "", f"expected nothing on stdout — {r.ctx()}")
    return "no register: the ledger still resets, stdout stays empty"


@case("X126", "STATUS_HOOK_RESET_OWNS_NO_PATH_RULE")
def x126(base):
    src = (HOOKS / "status-hook.py").read_text()
    check("{0,127}" not in src and "[A-Za-z0-9][A-Za-z0-9_-]" not in src,
          "status-hook.py carries the session-id pattern; the ledger has one owner")
    check(".cypress/session" not in src, "status-hook.py carries the string `.cypress/session`")
    check("reset_ledger" in src and "route-hook.py" in src,
          "status-hook.py does not obtain `reset_ledger` from its sibling route-hook.py")
    return "status-hook.py holds no path rule and takes reset_ledger from route-hook.py"


@case("X127", "STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER")
def x127(base):
    p = Plant(base, hooks=("status-hook.py",), register=True)
    led = write_ledger(p, prompt_count=3)
    before = sig(led)
    r = status(p, source="startup")
    check(sig(led) == before, "the ledger changed although route-hook.py is not beside status-hook.py")
    check(r.inj is not None and "0 open, 0 hotfix, 0 deferred" in r.inj, f"no status summary — {r.ctx()}")
    expect_one_err(r, "sibling missing")
    return "no sibling: ledger byte-identical, summary injected, one stderr line"


@case("X143", "RESET_NOT_WRITTEN")
def x143(base):
    p = Plant(base, register=True)
    write_ledger(p, prompt_count=3)
    r = status(p, source="startup", wrapper="oserror")
    check(r.inj is not None and "0 open, 0 hotfix, 0 deferred" in r.inj, f"no status summary — {r.ctx()}")
    expect_one_err(r, "reset write fails")
    check(not p.ledger().exists() and not p.ledger().is_symlink(),
          "the reset write failed and reset_ledger did not fall back to unlinking the ledger")
    return "reset write fails: summary injected, one stderr line, ledger unlinked"


# ---------------------------------------------------------------- persistence safety
def git(plant, *args):
    return subprocess.run(["git", "-C", str(plant.dir), *args], capture_output=True, text=True, timeout=20,
                          env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid"))


def gitignores(root):
    return {str(q.relative_to(root)): q.read_bytes() for q in root.rglob(".gitignore")
            if ".git" not in q.relative_to(root).parts[:1]}


@case("X128", "LEDGER_GITIGNORED")
def x128(base):
    p = Plant(base, git=False)
    check(git(p, "init", "-q").returncode == 0, "git init failed")
    git(p, "add", "-A")
    check(git(p, "commit", "-qm", "fixture").returncode == 0, "git commit failed")
    before = gitignores(p.dir)
    route(p, "zq-sentinel-0128 widget ledger work")
    gi = p.sess / ".gitignore"
    check(gi.is_file() and gi.read_bytes() == b"*\n", ".cypress/session/.gitignore is missing or not `*` + newline")
    check(p.ledger().is_file(), "no ledger was written")
    st = git(p, "status", "--porcelain", "--untracked-files=all").stdout
    check(".cypress/session/" not in st, f"git status lists the session directory: {st!r}")
    check(git(p, "check-ignore", "-q", f".cypress/session/{SID}.json").returncode == 0,
          "git check-ignore does not ignore the ledger")
    after = gitignores(p.dir)
    after.pop(".cypress/session/.gitignore", None)
    check(after == before, f"a .gitignore outside .cypress/session/ was created or changed: {sorted(after)}")
    q = Plant(base, name="owned")
    ensure_session_dir(q)
    (q.sess / ".gitignore").write_text("# the owner's own rules\n*.bak\n")
    before = (q.sess / ".gitignore").read_bytes()
    route(q, "zq-sentinel-0128 widget ledger work")
    check(q.ledger().is_file(), "with an owner's .gitignore present, no ledger was written")
    check((q.sess / ".gitignore").read_bytes() == before, "an existing .gitignore was rewritten")
    return "the session dir ignores itself; nothing else is touched; an existing .gitignore is kept"


@case("X129", "LEDGER_WRITE_IS_ATOMIC")
def x129(base):
    p = Plant(base)
    led = write_ledger(p)
    old = led.read_bytes()
    link = p.dir / "ledger-hardlink.json"
    os.link(led, link)
    route(p, "zq-sentinel-0129 widget ledger work")
    check(led.is_file() and os.stat(led).st_ino != os.stat(link).st_ino,
          "the ledger path still has the old inode: rewritten in place, not replaced")
    check(link.read_bytes() == old, "the hard-linked old ledger changed")
    names = sorted(os.listdir(p.sess))
    check(names == sorted([f"{SID}.json", ".gitignore"]), f"stray files in .cypress/session/: {names}")
    q = Plant(base, name="faulted")
    led = write_ledger(q)
    old = led.read_bytes()
    r = route(q, "zq-sentinel-0129 widget ledger work", wrapper="oserror")
    check(led.read_bytes() == old, "a failed replace changed the ledger")
    names = sorted(os.listdir(q.sess))
    check(names == sorted([f"{SID}.json", ".gitignore"]), f"a temp file was left behind: {names}")
    expect_full(r, "replace fails")
    expect_one_err(r, "replace fails")
    return "the ledger is replaced, not rewritten; a failed replace leaves it intact"


@case("X130", "LEDGER_SYMLINK_REFUSED; failures LEDGER_UNUSABLE, LEDGER_DIR_UNUSABLE")
def x130(base):
    def reminder_ledger(path):
        path.write_text(json.dumps(ledger_doc()))
        os.chmod(path, 0o600)
        t = time.time() - 60
        os.utime(path, (t, t))

    results = []
    for i, what in enumerate(("`.cypress` a symlink", "`.cypress/session` a symlink",
                              "the ledger a symlink", "`.gitignore` a symlink", "the ledger a FIFO")):
        cb = base / f"c{i}"
        cb.mkdir()
        out = cb / "outside"
        out.mkdir()
        p = Plant(cb, cypress=(i != 0))
        if i == 0:
            (out / "session").mkdir(mode=0o700)
            os.chmod(out / "session", 0o700)
            (out / "session" / ".gitignore").write_text("*\n")
            reminder_ledger(out / "session" / f"{SID}.json")
            os.symlink(out, p.dir / ".cypress")
        elif i == 1:
            os.chmod(out, 0o700)
            (out / ".gitignore").write_text("*\n")
            reminder_ledger(out / f"{SID}.json")
            os.symlink(out, p.sess)
        elif i == 2:
            ensure_session_dir(p)
            reminder_ledger(out / "ledger.json")
            os.symlink(out / "ledger.json", p.ledger())
        elif i == 3:
            p.sess.mkdir(mode=0o700)
            os.chmod(p.sess, 0o700)
            (out / "gitignore-target").write_text("*\n")
            os.symlink(out / "gitignore-target", p.sess / ".gitignore")
            reminder_ledger(p.ledger())
        else:
            ensure_session_dir(p)
            os.mkfifo(p.ledger(), 0o600)
        before = snapshot(cb, skip=("plant",))
        r = run_hook(p, json.dumps({"hook_event_name": "UserPromptSubmit", "session_id": SID,
                                    "prompt": "zq-sentinel-0130 widget ledger work"}), timeout=5)
        check(r.rc == 0 and not r.timed_out, f"{what}: must exit 0 within 5 s — {r.ctx()}")
        diff = snap_diff(before, snapshot(cb, skip=("plant",)))
        check(not diff, f"{what}: something outside the plant changed: {diff}")
        expect_full(r, what)
        expect_one_err(r, what)
        results.append(what)
    return "five link/FIFO shapes: exit 0 within 5 s, outside untouched, full, one stderr line"


@case("X131", "LEDGER_FOREIGN_OR_WRITABLE_REFUSED; failures LEDGER_UNUSABLE, LEDGER_DIR_UNUSABLE")
def x131(base):
    p = Plant(base, name="dir0777")
    write_ledger(p)
    os.chmod(p.sess, 0o777)
    before = snapshot(p.sess)
    r = route(p, "zq-sentinel-0131 widget ledger work")
    expect_full(r, "session dir 0777")
    expect_one_err(r, "session dir 0777")
    diff = snap_diff(before, snapshot(p.sess))
    check(not diff, f"session dir 0777: files were created or modified: {diff}")
    q = Plant(base, name="ledger0666")
    write_ledger(q, fmode=0o666)
    r = route(q, "zq-sentinel-0131 widget ledger work")
    expect_full(r, "ledger 0666")
    expect_one_err(r, "ledger 0666")
    f = Plant(base, name="fresh")
    route(f, "zq-sentinel-0131 widget ledger work")
    check(f.sess.is_dir() and stat.S_IMODE(os.stat(f.sess).st_mode) == 0o700,
          "the session directory the hook creates is not mode 0700")
    check(f.ledger().is_file() and stat.S_IMODE(os.stat(f.ledger()).st_mode) == 0o600,
          "the ledger the hook writes is not mode 0600")
    return "group/other-writable dir or ledger refused; created dir 0700, ledger 0600"


@case("X132", "LEDGER_NO_CYPRESS_DIR_NO_WRITE; failure LEDGER_DIR_UNUSABLE")
def x132(base):
    p = Plant(base, cypress=False)
    r = route(p, "zq-sentinel-0132 widget ledger work")
    check(not (p.dir / ".cypress").exists(), "the hook created .cypress/")
    expect_full(r, "no .cypress/")
    expect_one_err(r, "no .cypress/")
    check(".cypress" in r.err, f"the stderr line does not name the path — {r.ctx()}")
    return "no .cypress/: not created, full mode, one stderr line naming the path"


@case("X133", "LEDGER_WRITE_FAILURE_FAILS_OPEN")
def x133(base):
    note = ""
    if os.geteuid() == 0:
        note = "; read-only case SKIPPED: running as root"
    else:
        p = Plant(base, name="readonly")
        write_ledger(p)
        os.chmod(p.sess, 0o500)
        try:
            r = route(p, "zq-sentinel-0133 widget ledger work")
        finally:
            os.chmod(p.sess, 0o700)
        expect_full(r, "read-only session dir")
        expect_one_err(r, "read-only session dir")
    q = Plant(base, name="perm")
    write_ledger(q)
    r = route(q, "zq-sentinel-0133 widget ledger work", wrapper="perm")
    expect_full(r, "os.replace raises PermissionError")
    expect_one_err(r, "os.replace raises PermissionError")
    return "a write that fails gives full mode and one stderr line" + note


@case("X134", "LEDGER_GC_BOUNDED")
def x134(base):
    now = time.time()
    p = Plant(base)
    ensure_session_dir(p)
    s = p.sess

    def put(name, age, data=b"{}"):
        f = s / name
        f.write_bytes(data)
        os.chmod(f, 0o600)
        os.utime(f, (now - age, now - age))

    for i in range(40):
        put(f"old-ledger-{i:02d}.json", 8 * DAY + i, json.dumps(ledger_doc(f"old-ledger-{i:02d}")).encode())
    fresh = {f"fresh-ledger-{i:02d}.json": (i + 1) * 60 for i in range(40)}
    for name, age in fresh.items():
        put(name, age, json.dumps(ledger_doc(name[:-5])).encode())
    for i in range(10):
        put(f".tmp-stale{i:02d}", 2 * 3600)
    put("notes.txt", 60, b"owner notes\n")
    put("bad name.json", 60, b"{}")
    keep = {n: (s / n).read_bytes() for n in ("notes.txt", "bad name.json", ".gitignore")}
    route(p, "zq-sentinel-0134 widget ledger work")
    names = set(os.listdir(s))
    check(f"{SID}.json" in names, "the current session's ledger was not created")
    check(not any(n.startswith("old-ledger-") for n in names), "a ledger older than GC_MAX_AGE survived")
    ledgers = [n for n in names if n.endswith(".json") and SID_RE.match(n[:-5])]
    check(len(ledgers) <= GC_MAX_FILES, f"{len(ledgers)} ledger files remain, over GC_MAX_FILES")
    kept = [n for n in fresh if n in names]
    gone = [n for n in fresh if n not in names]
    check(not gone or min(fresh[n] for n in gone) > max(fresh[n] for n in kept),
          "the fresh ledgers removed were not the oldest")
    check(not any(n.startswith(".tmp-stale") for n in names), "a stale temp file survived")
    for n, b in keep.items():
        check((s / n).is_file() and (s / n).read_bytes() == b, f"{n} was changed or removed")
    put(".tmp-late", 2 * 3600)
    route(p, "zq-sentinel-0134 second widget prompt")
    check((s / ".tmp-late").exists(), "GC ran on an update, not only on creation")
    q = Plant(base, name="many")
    ensure_session_dir(q)
    s = q.sess
    for i in range(300):
        put(f".tmp-many{i:03d}", 2 * 3600)
    route(q, "zq-sentinel-0134 widget ledger work", sid="gc-scan-session")
    check((s / "gc-scan-session.json").is_file(), "the ledger was not created")
    removed = 300 - sum(1 for n in os.listdir(s) if n.startswith(".tmp-many"))
    check(removed <= GC_SCAN_MAX, f"one creation removed {removed} temp files, over GC_SCAN_MAX")
    return "GC on creation: old and excess ledgers and stale temps go, others kept, scan bounded"


@case("X142", "ROUTER_FAILED")
def x142(base):
    problems = []
    t = read_constant(HOOKS / "route-hook.py", "ROUTER_TIMEOUT")
    if not t:
        problems.append("ROUTER_TIMEOUT: no module-level literal in route-hook.py")
    sentinel = "zq-sentinel-0142"
    variants = [("exit1", "router exits non-zero"), ("empty", "router prints nothing")]
    if t:
        variants.append(("sleep", "router exceeds ROUTER_TIMEOUT (rewritten to 1)"))
    for i, (mode, what) in enumerate(variants):
        p = Plant(base, name=f"plant{i}", mode=mode)
        if mode == "sleep":
            rewrite_constant(p.hook(), "ROUTER_TIMEOUT", 1)
        led = write_ledger(p)
        before = sig(led)
        r = route(p, sentinel + " widget ledger work")
        if not is_pointer_only(r):
            problems.append(f"{what}: expected the pointer line alone — {r.ctx()}")
        if sig(led) != before:
            problems.append(f"{what}: the ledger changed")
        if sentinel in (r.inj or "") + r.err or sentinel.encode() in session_bytes(p):
            problems.append(f"{what}: the prompt leaked")
    check(not problems, "; ".join(problems))
    return "non-zero exit, empty output, timeout: pointer line alone, ledger untouched"


# ---------------------------------------------------------------- review of 2deda6a..343445f
# Fail-open regressions found by the reviewer. Each case names the contract or
# §7 failure it holds; X144 and X145 are the first cases of UNEXPECTED_EXCEPTION.
def no_traceback(r, what):
    check("Traceback" not in r.err, f"{what}: a traceback reached stderr — {r.ctx()}")


def at_most_one_err(r, what):
    check(r.err == "" or one_err_line(r), f"{what}: expected at most one stderr line — {r.ctx()}")


@case("X144", "UNEXPECTED_EXCEPTION")
def x144(base):
    p = Plant(base, register=True)
    (p.dir / "docs" / "graph" / "status-register.py").write_text(
        "import sys\nsys.stdout.buffer.write(b'\\xff\\xfe 3 open, \\xc3\\x28 hotfix\\n')\n")
    r = run_hook(p, json.dumps({"hook_event_name": "SessionStart", "session_id": SID,
                                "source": "startup", "cwd": str(p.dir)}), hook=p.hook("status-hook.py"))
    check(r.rc == 0, f"a register printing non-UTF-8 bytes: status-hook must exit 0 — {r.ctx()}")
    no_traceback(r, "non-UTF-8 register output")
    at_most_one_err(r, "non-UTF-8 register output")
    check(r.out.strip() == "" or r.envelope_ok,
          f"non-UTF-8 register output: stdout is neither empty nor one hook envelope — {r.ctx()}")
    return "status register printing non-UTF-8 bytes: exit 0, no traceback, at most one stderr line"


@case("X145", "UNEXPECTED_EXCEPTION")
def x145(base):
    nested = "[" * 100_000
    p = Plant(base, register=True)

    def route_half():
        r = run_hook(p, nested)
        check(r.rc == 0, f"route-hook, 100 000 nested `[` on stdin: must exit 0 — {r.ctx()}")
        no_traceback(r, "route-hook, nested stdin")
        check(r.envelope_ok and is_pointer_only(r),
              f"route-hook, nested stdin: graph-lint.py resolves, so the pointer line is owed — {r.ctx()}")
        expect_one_err(r, "route-hook, nested stdin")

    def status_half():
        s = run_hook(p, nested, hook=p.hook("status-hook.py"))
        check(s.rc == 0, f"status-hook, 100 000 nested `[` on stdin: must exit 0 — {s.ctx()}")
        no_traceback(s, "status-hook, nested stdin")
        check(s.inj is not None and "0 open, 0 hotfix, 0 deferred" in s.inj,
              f"status-hook, nested stdin: the summary can still be built and is owed — {s.ctx()}")
        at_most_one_err(s, "status-hook, nested stdin")

    problems = []
    for half in (route_half, status_half):
        try:
            half()
        except CaseFail as e:
            problems.append(str(e))
    check(not problems, " || ".join(problems))
    return "stdin nested past the parser: both hooks exit 0; route-hook keeps the pointer, status-hook the summary"


@case("X146", "ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO")
def x146(base):
    words = ("tighten the", "ledger gc please")
    lf = Plant(base, name="lf")
    ref = route(lf, "\n".join(words), sid=MISSING)
    check(is_full(ref), f"harness: the `\\n` prompt did not get full mode — {ref.ctx()}")
    problems = []
    for i, sep in enumerate(("\r\n", "\r")):
        p = Plant(base, name=f"cr{i}")
        r = route(p, sep.join(words))
        if not is_full(r):
            problems.append(f"{sep!r} prompt: expected the full routing a `\\n` prompt gets — {r.ctx()}")
        elif r.inj != ref.inj:
            problems.append(f"{sep!r} prompt: the suggestion differs from the `\\n` prompt's")
        if any(w in (r.inj or "") for w in words):
            problems.append(f"{sep!r} prompt: a prompt line was echoed into the injection")
        if not p.ledger().is_file():
            problems.append(f"{sep!r} prompt: no ledger was written for a routed first prompt")
    check(not problems, "; ".join(problems))
    return "a prompt with CRLF or a lone CR is routed like its `\\n` twin, with no echo"


@case("X147", "RESET_NOT_WRITTEN")
def x147(base):
    p = Plant(base, register=True)
    write_ledger(p, prompt_count=3)
    r = status(p, source="startup", wrapper="statfail")
    no_traceback(r, "ledger stat fails")
    check(r.inj is not None and "0 open, 0 hotfix, 0 deferred" in r.inj, f"no status summary — {r.ctx()}")
    expect_one_err(r, "ledger stat fails")
    check(SID not in r.err, f"the reset's stderr line carries the raw session id — {r.ctx()}")
    return "the ledger stat fails: summary injected, one stderr line, no raw session id"


@case("X148", "LEDGER_WRITE_FAILURE_FAILS_OPEN")
def x148(base):
    # Node ids at the pattern's upper length, enough of them that the ledger the
    # hook would write is over LEDGER_MAX_BYTES while each list is within 512.
    def nid(kind, i):
        return f"{kind}.{i:04d}." + "x" * 110
    load = [nid("load", i) for i in range(300)]
    nl = [nid("peer", i) for i in range(300)]
    body = (f"LOAD ({len(load)} nodes, ~9 tokens):\n" + "".join(f"  {n}  a\n" for n in load)
            + "\nNOT LOADED (with the reason; cross only if the task requires it):\n"
            + "".join(f"  {n}  b\n" for n in nl))
    projected = len(json.dumps(ledger_doc(surfaced=load, peers_seen=nl)).encode()) + 1
    check(projected > LEDGER_MAX_BYTES, f"harness: the projected ledger is only {projected} B")
    p = Plant(base, body=body)
    runs = []
    for turn in (1, 2, 3):
        r = route(p, f"zq-sentinel-0148 widget ledger work, prompt {turn}")
        expect_full(r, f"prompt {turn}", remainder=body)
        check(not p.ledger().exists(), f"prompt {turn}: a ledger of "
              f"{p.ledger().stat().st_size if p.ledger().exists() else 0} B was written, which the "
              f"next read refuses as oversized")
        expect_one_err(r, f"prompt {turn}: a ledger over LEDGER_MAX_BYTES is refused, not written")
        stray = [n for n in os.listdir(p.sess) if n != ".gitignore"] if p.sess.is_dir() else []
        check(not stray, f"prompt {turn}: files left in .cypress/session/: {stray}")
        runs.append(r.err)
    check(len(set(runs)) == 1, f"the outcome flip-flops between prompts: {runs!r}")
    return "a ledger over LEDGER_MAX_BYTES is never written; every prompt the same full mode and one line"


@case("X149", "LEDGER_GC_BOUNDED")
def x149(base):
    p = Plant(base)
    r1 = route(p, "zq-sentinel-0149 widget ledger work", wrapper="scandirfail")
    expect_full(r1, "first prompt, GC scan fails")
    at_most_one_err(r1, "first prompt, GC scan fails")
    check(p.ledger().is_file(), f"a failed GC blocked the ledger write — {r1.ctx()}")
    check(not ledger_problems(p.ledger()), f"the ledger is malformed: {ledger_problems(p.ledger())}")
    check(read_ledger(p)["prompt_count"] == 1, f"prompt_count {read_ledger(p)['prompt_count']}, not 1")
    r2 = route(p, "zq-sentinel-0149 second widget prompt", wrapper="scandirfail")
    check(is_reminder(r2), f"second prompt: expected reminder mode — {r2.ctx()}")
    return "GC failing on creation still writes the ledger; the next prompt is a reminder"


failed = []
for label, slug, fn in CASES:
    if ONLY and label not in ONLY:
        continue
    base = Path(tempfile.mkdtemp(prefix=f"{label}-", dir=WORK))
    try:
        note = fn(base)
        print(f"  {label} {slug}: {note} \u2014 OK")
    except CaseFail as e:
        failed.append(label)
        print(f"FAIL: {label} {slug}: {e}", file=sys.stderr)
    except Exception:                               # noqa: BLE001 — a harness bug, said as one
        failed.append(label)
        print(f"HARNESS ERROR: {label} {slug}:\n{traceback.format_exc()}", file=sys.stderr)
if failed:
    print(f"SPEC-0003 hook cases: FAIL — {len(failed)} case(s): {', '.join(failed)}", file=sys.stderr)
    sys.exit(1)
PY

# --- SPEC-0003 per-prompt injection: Prime Agent, structural (X135-X141) ------
# The gate has no TypeScript runtime and no model in the loop, so these read
# `integrations/prime-agent/route-extension.ts` and `APPEND_SYSTEM.md` as text,
# in the style of the resolver read in tests/test-install-placement.sh. They
# prove wording and shape, never what a model does (SPEC-0003 §4, §10).
PRIME_RC=0
python3 - "$ROOT" <<'PY' || PRIME_RC=1
import ast, io, re, sys, tokenize, traceback
from pathlib import Path

SEED = Path(sys.argv[1])
EXT = (SEED / "integrations" / "prime-agent" / "route-extension.ts").read_text(encoding="utf-8")
HOOK = (SEED / "integrations" / "claude-code" / "route-hook.py").read_text(encoding="utf-8")
OVERLAY = (SEED / "integrations" / "prime-agent" / "APPEND_SYSTEM.md").read_text(encoding="utf-8")
POINTER = "Route first: the kernel's FIRST MOVE and §0 apply to this prompt."
SUGGESTION_HEADER = "Router suggestion (a keyword heuristic — reason over it):"
OVERLAY_SECTION_MAX_BYTES = 512          # SPEC-0003 §6: this block is its one home


class CaseFail(Exception):
    pass


def check(cond, msg):
    if not cond:
        raise CaseFail(msg)


def block_after(src, open_idx):
    """The span from the opening bracket at open_idx to its match."""
    pairs = {"{": "}", "[": "]", "(": ")"}
    stack = []
    for i in range(open_idx, len(src)):
        c = src[i]
        if c in pairs:
            stack.append(pairs[c])
        elif stack and c == stack[-1]:
            stack.pop()
            if not stack:
                return open_idx, i
    return open_idx, len(src)


def split_top(s):
    out, depth, cur = [], 0, ""
    for c in s:
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += c
    if cur.strip():
        out.append(cur.strip())
    return out


def ts_literals(src):
    """(decoded value, start, end) of every string literal, comments skipped."""
    out, i, n = [], 0, len(src)
    esc = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", "\\": "\\", "'": "'", '"': '"', "`": "`"}
    while i < n:
        if src.startswith("//", i):
            i = src.find("\n", i)
            i = n if i < 0 else i
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        q = src[i]
        if q in "\"'`":
            j, val, templated = i + 1, "", False
            while j < n and src[j] != q:
                if src[j] == "\\":
                    k = src[j + 1]
                    if k == "u" and src[j + 2] == "{":
                        e = src.index("}", j)
                        val += chr(int(src[j + 3:e], 16))
                        j = e + 1
                        continue
                    if k == "u":
                        val += chr(int(src[j + 2:j + 6], 16))
                        j += 6
                        continue
                    if k == "x":
                        val += chr(int(src[j + 2:j + 4], 16))
                        j += 4
                        continue
                    val += esc.get(k, k)
                    j += 2
                    continue
                if q == "`" and src.startswith("${", j):
                    templated = True
                val += src[j]
                j += 1
            if not templated:
                out.append((val, i, j + 1))
            i = j + 1
            continue
        i += 1
    return out


def single_ts_literal(src, text):
    for val, s, e in ts_literals(src):
        if val == text:
            before = src[:s].rstrip()[-1:]
            after = src[e:].lstrip()[:1]
            if before != "+" and after != "+":
                return True
    return False


def single_py_literal(src, text):
    toks = [t for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type not in (tokenize.NL, tokenize.COMMENT)]
    for k, t in enumerate(toks):
        if t.type != tokenize.STRING:
            continue
        try:
            val = ast.literal_eval(t.string)
        except Exception:                          # noqa: BLE001 — f-strings, bytes
            continue
        if val != text:
            continue
        prev = toks[k - 1] if k else None
        nxt = toks[k + 1] if k + 1 < len(toks) else None
        if any(x is not None and (x.type == tokenize.STRING or x.string == "+") for x in (prev, nxt)):
            continue
        return True
    return False


def overlay_section():
    lines = OVERLAY.splitlines(keepends=True)
    heads = [i for i, l in enumerate(lines) if l.rstrip() == "## Surfaced nodes"]
    if len(heads) != 1:
        return None, len(heads)
    i = j = heads[0]
    j += 1
    while j < len(lines) and not lines[j].startswith("## "):
        j += 1
    return "".join(lines[i:j]), 1


def need_section():
    sec, count = overlay_section()
    check(sec is not None, f"APPEND_SYSTEM.md has {count} `## Surfaced nodes` sections; exactly one is required")
    return sec


CASES = []


def case(label, slug):
    def deco(fn):
        CASES.append((label, slug, fn))
        return fn
    return deco


@case("X135", "ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX")
def x135():
    m = re.search(r"(?:const|let)\s+(\w+)\s*=\s*`task: \$\{(\w+)\}\\n\\n`", EXT)
    check(m, "no prefix built as `task: ${prompt}\\n\\n` and bound to a name")
    prefix, pvar = m.group(1), m.group(2)
    check(f"`--plan=${{{pvar}}}`" in EXT, f"the prefix is not built from the `{pvar}` that goes into `--plan=`")
    check(re.search(rf"\.startsWith\(\s*{prefix}\s*\)", EXT), f"the output is not tested with startsWith({prefix})")
    sl = re.search(rf"\.slice\(\s*{prefix}\.length\s*\)(\.trim\(\))?", EXT)
    check(sl, f"the prefix is not removed with slice({prefix}.length)")
    check(not EXT[sl.end():].lstrip().startswith("."),
          "the remainder is transformed beyond trim()")
    check(not re.search(r"\.slice\(\s*\d", EXT), "a fixed `.slice(<n>)` is still applied")
    check(not re.search(r"split\(\s*[\"'`]\\n[\"'`]\s*\)", EXT), "the output is still split into lines")
    g = re.search(rf"if\s*\([^{{]*\.startsWith\(\s*{prefix}\s*\)[^{{]*\)\s*\{{", EXT)
    check(g, f"no `if (…startsWith({prefix})…) {{` branch")
    lo, hi = block_after(EXT, g.end() - 1)
    decl = re.search(r"(?:const|let|var)\s+(SUGGESTION_HEADER)\b", EXT)
    uses = [u.start() for u in re.finditer(r"\bSUGGESTION_HEADER\b", EXT)
            if not decl or u.start() != decl.start(1)]
    check(uses and all(lo < u < hi for u in uses), "SUGGESTION_HEADER is appended outside the startsWith branch")
    rd = re.search(rf"(?:const|let)\s+(\w+)\s*=\s*[^;\n]*\.slice\(\s*{prefix}\.length", EXT)
    if rd:
        rvar = rd.group(1)
        ruses = [u.start() for u in re.finditer(rf"\b{rvar}\b", EXT) if u.start() != rd.start(1)]
        check(ruses and all(lo < u < hi for u in ruses), f"the remainder `{rvar}` is used outside the branch")
    else:
        check(lo < sl.start() < hi, "the remainder is taken outside the startsWith branch")
    return "exact `task: ${prompt}\\n\\n` prefix, startsWith, slice(prefix.length), header only in that branch"


@case("X150", "ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX")
def x150():
    # The Prime Agent twin of X146. route-hook.py lost the echo of a CRLF prompt
    # to universal-newline decoding; the extension must compare the exec result's
    # stdout as it arrived. Structural only: what pi.exec does to line endings
    # before it returns is not observed here.
    m = re.search(r"(?:const|let)\s+(\w+)\s*=\s*await\s+pi\.exec\(", EXT)
    check(m, "the pi.exec result is not bound to a name")
    res = m.group(1)
    check(re.search(rf"\b{res}\.stdout\.startsWith\(\s*\w+\s*\)", EXT),
          f"the echo prefix is not tested against the raw `{res}.stdout`")
    check(not re.search(rf"\b{res}\.stdout\s*=[^=]", EXT), f"`{res}.stdout` is reassigned before the test")
    check("\\r" not in EXT and not re.search(r"\bEOL\b|\.normalize\(", EXT),
          "the router output is newline-normalised, so a CRLF prompt's echo no longer matches")
    return "the echo prefix is tested against the exec result's stdout as it arrived, no CR rewriting"


@case("X136", "ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE")
def x136():
    calls = [m.end() for m in re.finditer(r"\bpi\.exec\(", EXT)]
    check(len(calls) == 1, f"expected a single `pi.exec(` call, found {len(calls)}")
    _, close = block_after(EXT, calls[0] - 1)
    args = split_top(EXT[calls[0]:close])
    check(len(args) >= 2 and args[1].startswith("[") and args[1].endswith("]"),
          "no argv array literal written inline in the pi.exec( call")
    elems = split_top(args[1][1:-1])
    plan = [e for e in elems if re.fullmatch(r"`--plan=\$\{\w+\}`", e)]
    check(len(plan) == 1, f"no single `--plan=${{prompt}}` element in {elems}")
    pvar = re.search(r"\{(\w+)\}", plan[0]).group(1)
    check(not any(e in ('"--plan"', "'--plan'", "`--plan`") for e in elems),
          f"`--plan` is a separate element: {elems}")
    check(not any(re.search(rf"\b{pvar}\b", e) for e in elems if e is not plan[0]),
          f"the prompt is passed outside its `--plan=` element: {elems}")
    return "argv is an inline literal; the prompt appears only inside `--plan=`"


@case("X137", "ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK")
def x137():
    for name, text in (("POINTER", POINTER), ("SUGGESTION_HEADER", SUGGESTION_HEADER)):
        check(single_py_literal(HOOK, text), f"route-hook.py has no single string literal equal to {name} {text!r}")
        check(single_ts_literal(EXT, text), f"route-extension.ts has no single string literal equal to {name} {text!r}")
    return "the pointer line and the suggestion header are one literal each, in both sources"


@case("X138", "ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE")
def x138():
    allow = {"TRIVIAL", "CANDIDATES", "findLint", "POINTER", "SUGGESTION_HEADER", "routeExtension"}
    names = [m.group(5) for m in (re.match(r"^(export\s+)?(default\s+)?(async\s+)?(const|let|var|function|class)\s+(\w+)", l)
                                  for l in EXT.splitlines()) if m]
    extra = sorted(set(names) - allow)
    check(not extra, f"module-scope names outside the allowlist: {extra}")
    check(not any(re.match(r"^(export\s+)?(const|let|var)\s*[\[{]", l) for l in EXT.splitlines()),
          "a destructuring declaration at module scope")
    check("globalThis" not in EXT, "the source touches globalThis")
    ons = re.findall(r"\bpi\.on\(\s*([^,]*),", EXT)
    check(ons and all(o.strip() in ('"before_agent_start"', "'before_agent_start'") for o in ons),
          f"pi.on subscribes to something other than before_agent_start: {ons}")
    for p in ("Surfaced earlier this session:", "New for this task:",
              "Not suggested, not listed before (cross only if needed):"):
        check(p not in EXT, f"the extension carries the reminder-mode prefix {p!r}")
    check("pi.appendEntry" not in EXT, "the extension calls pi.appendEntry")
    for fn in ("writeFile", "writeFileSync", "appendFile", "appendFileSync", "mkdir", "mkdirSync",
               "rename", "renameSync", "createWriteStream", "copyFile", "copyFileSync", "cp", "cpSync",
               "open", "openSync", "truncate", "truncateSync", "symlink", "symlinkSync"):
        check(not re.search(rf"\b{fn}\s*\(", EXT), f"the extension calls {fn}(")
    return "allowlisted module scope, before_agent_start only, no reminder text, no writes"


@case("X139", "PRIME_OVERLAY_KEEPS_SURFACED_SET")
def x139():
    sec = need_section()
    flat = re.sub(r"\s+", " ", sec)
    for phrase in ("_cypress_surfaced", "IPython kernel", "surfaced earlier this session",
                   "re-open it if its content is not in view"):
        check(phrase in flat, f"the section lacks the phrase {phrase!r}")
    check("rlm" not in sec and "brief" not in sec, "the section mentions rlm or brief")
    return "one `## Surfaced nodes` section with the four phrases, no rlm, no brief"


@case("X140", "PRIME_OVERLAY_NEVER_SAYS_LOADED")
def x140():
    sec = need_section()
    check(not re.search("loaded", sec, re.I), "the section says `loaded`")
    return "the section never says loaded"


@case("X141", "PRIME_OVERLAY_SECTION_WITHIN_CEILING")
def x141():
    sec = need_section()
    n = len(sec.encode("utf-8"))
    check(n <= OVERLAY_SECTION_MAX_BYTES, f"the section is {n} B, over OVERLAY_SECTION_MAX_BYTES")
    return f"the section is {n} B, within {OVERLAY_SECTION_MAX_BYTES}"


failed = []
for label, slug, fn in CASES:
    try:
        print(f"  {label} {slug}: {fn()} — OK")
    except CaseFail as e:
        failed.append(label)
        print(f"FAIL: {label} {slug}: {e}", file=sys.stderr)
    except Exception:                               # noqa: BLE001
        failed.append(label)
        print(f"HARNESS ERROR: {label} {slug}:\n{traceback.format_exc()}", file=sys.stderr)
if failed:
    print(f"SPEC-0003 Prime Agent cases: FAIL — {len(failed)} case(s): {', '.join(failed)}", file=sys.stderr)
    sys.exit(1)
PY

[[ "$SPEC3_RC" == 0 && "$PRIME_RC" == 0 ]] \
  || fail "SPEC-0003 per-prompt injection: the case(s) named above failed"

echo "test-bound-hook: PASS"
