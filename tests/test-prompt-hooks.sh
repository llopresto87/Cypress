#!/usr/bin/env bash
# SPEC-0003 per-prompt injection: the Claude Code hooks route-hook.py and
# status-hook.py, and the Prime Agent extensions. VS Code's Copilot runs the
# same hooks from `.claude/settings.json` on an envelope with no `session_id`
# (a frozen host, ADR-0009); X118 and X124 hold that they fail open there.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() { echo "FAIL: $*" >&2; exit 1; }

FO="$(mktemp -d)"
trap 'rm -rf "$FO"' EXIT

# --- route-hook.py and status-hook.py (X101-X134, X142-X149, X151, X161-X162)
# One case per SPEC-0003 §4 contract and §7 failure, bound by the §10 labels.
# Each case prints `X1NN <SLUG>: … — OK`. The shipped hooks are copied into
# `.claude/` of a temp plant (`.git/`, `.cypress/`, a stub
# `docs/graph/graph-lint.py` that echoes `task: <prompt>`, a blank line and a
# fixed body). Fault injection runs a hook through a `runpy` wrapper, so it
# works as root. `SPEC0003_ONLY=X101,X113` runs a subset.
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
# §6 constants used by value. REFRESH_EVERY, ROUTER_TIMEOUT and ANCHOR_TIMEOUT
# are read from the copied hook by regex instead (spec §10).
LEDGER_MAX_BYTES = 64 * 1024
DAY = 86400
SID = "3b9f1c2e-5d4a-4e8b-9a61-0c7f2d8e1a44"

# The router's entry lines carry the node file after the id (X151).
BODY = (
    "LOAD (2 nodes, ~900 tokens):\n"
    "  root                         docs/graph/nodes/root.md  knowledge graph router\n"
    "  skill.knowledge-graph        docs/graph/skills/knowledge-graph.md  knowledge-graph authoring\n"
    "\n"
    "NOT LOADED (with the reason; cross only if the task requires it):\n"
    "  agent.implementer            docs/graph/agents/03-implementer.md  peer of skill.knowledge-graph\n"
    "  domain.sprocketry            docs/graph/nodes/domain.sprocketry.md  peer of skill.knowledge-graph\n")
NOTICES = ["  ! notice one: the widget terms matched nothing specific",
           "  ! notice two: consider the index before the nodes"]
NOTICE_BODY = "\n".join(NOTICES) + "\n\n" + BODY
# A NOT LOADED id that is also in LOAD, so `peers_seen = not_loaded - load` shows.
OVERLAP_BODY = BODY + "  skill.knowledge-graph        docs/graph/skills/knowledge-graph.md  peer of root\n"
UNPARSEABLE = "no router header in this output\nsecond remainder line\n"


def parse_body(body):
    load, nl, sect = [], [], None
    for ln in body.splitlines():
        if ln.startswith("LOAD ("):
            sect = load
        elif ln.startswith("NOT LOADED ("):
            sect = nl
        elif ln.startswith("  ") and not ln.startswith("  ! ") and sect is not None:
            sect.append((ln.split()[0], ln))
    return load, nl


def ids(entries):
    return [i for i, _ in entries]


LOAD, NL = parse_body(BODY)
LOAD_IDS, NL_IDS = ids(LOAD), ids(NL)

STUB = r"""#!/usr/bin/env python3
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
else:
    sys.stdout.write("task: " + plan + "\n\n" + BODY)
sys.exit(1 if MODE == "exit1" else 0)
"""
REGISTER = 'print("0 open, 0 hotfix, 0 deferred")\n'
SUMMARY = "0 open, 0 hotfix, 0 deferred"
WRAPPER = WORK / "fault-wrapper.py"
WRAPPER.write_text(r"""
import errno, os, runpy, sys
kind, hook = sys.argv[1], sys.argv[2]
def _refuse(*a, **k):
    if kind == "perm":
        raise PermissionError(errno.EACCES, "injected by the SPEC-0003 fault wrapper")
    raise OSError(errno.EIO, "injected by the SPEC-0003 fault wrapper")
if kind == "statfail":                    # X147: the ledger stat fails, naming the file
    _real_stat = os.stat
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
""")


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
    """A §6 ledger, mode 0600 in a 0700 session directory, `age` seconds old."""
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


def expect_fresh_ledger(p, what):
    """The ledger is valid JSON again, rebuilt at prompt_count 1."""
    try:
        d = read_ledger(p)
    except Exception as e:                        # noqa: BLE001
        raise CaseFail(f"{what}: the ledger was not replaced by valid JSON ({e})")
    check(d.get("version") == 1 and d.get("prompt_count") == 1,
          f"{what}: expected a version-1 ledger at prompt_count 1, got {d!r}")


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


def no_traceback(r, what):
    check("Traceback" not in r.err, f"{what}: a traceback reached stderr — {r.ctx()}")


def at_most_one_err(r, what):
    check(r.err == "" or one_err_line(r), f"{what}: expected at most one stderr line — {r.ctx()}")


def collect(problems, fn):
    try:
        fn()
    except CaseFail as e:
        problems.append(str(e))


CASES = []


def case(label, slug):
    def deco(fn):
        CASES.append((label, slug, fn))
        return fn
    return deco


# ---------------------------------------------------------------- echo, pointer, ledger modes
# LEDGER_EVERY_LOAD_ID_NAMED: X106, X107, X110, X113, X120 and X123 hold its six
# ledger states, each by an exact-text compare.
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
    before = sig(led)
    r = route(p, "zq-nul-0103 before\x00after the byte")
    check(r.envelope_ok, f"stdout is not one valid hook envelope — {r.ctx()}")
    check(is_pointer_only(r), f"expected the pointer line alone — {r.ctx()}")
    check(sig(led) == before, "the ledger changed (bytes or mtime)")
    no_traceback(r, "NUL byte")
    return "a NUL-byte prompt: pointer line alone, ledger untouched"


@case("X104", "ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY")
def x104(base):
    p = Plant(base)
    led = write_ledger(p)
    sentinel = "zq-sentinel-0104"
    prompt = sentinel + " plan the widget ledger"
    p.stub("noecho")
    before = sig(led)
    r = route(p, prompt)
    check(is_pointer_only(r), f"expected the pointer line alone — {r.ctx()}")
    check(sentinel not in (r.inj or "") and sentinel not in r.err,
          f"the prompt sentinel leaked into the injection or stderr — {r.ctx()}")
    check(sentinel.encode() not in session_bytes(p), "the sentinel is in .cypress/session/")
    check(sig(led) == before, "the ledger changed (bytes or mtime)")
    return "output without the `task:` echo: pointer line alone, nothing leaked"


@case("X106", "LEDGER_FIRST_PROMPT_FULL")
def x106(base):
    p = Plant(base, body=OVERLAP_BODY)
    sentinel = "zq-sentinel-0106"
    r = route(p, sentinel + " first widget prompt")
    expect_full(r, "first prompt", OVERLAP_BODY)      # X105 ROUTE_HOOK_POINTS_AT_KERNEL: pointer first
    check(r.err == "", f"expected no stderr — {r.ctx()}")
    check(p.ledger().is_file(), "no ledger was written")
    d = read_ledger(p)
    load, nl = parse_body(OVERLAP_BODY)
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
    d = read_ledger(p)                          # X116 LEDGER_NEVER_EMITS_UNROUTED_ID
    d["surfaced"] = sorted(d["surfaced"] + ["zz.unrouted-sentinel"])
    p.ledger().write_text(json.dumps(d))
    r = route(p, "zq-sentinel-0107c third widget prompt")
    check(r.inj is not None and "zz.unrouted-sentinel" not in r.inj, f"an unrouted ledger id was injected — {r.ctx()}")
    return "second prompt, nothing new: exactly the pointer and the Surfaced line; no unrouted id"


@case("X109", "REMINDER_SAYS_SURFACED_NEVER_LOADED")
def x109(base):
    p = Plant(base, body=NOTICE_BODY)
    write_ledger(p, surfaced=["root"], peers_seen=["agent.implementer"])
    r = route(p, "zq-sentinel-0109 widget ledger work")
    check(is_reminder(r), f"expected reminder mode — {r.ctx()}")
    lines = r.inj.split("\n")
    check(lines[1:1 + len(NOTICES)] == NOTICES,             # X108 REMINDER_KEEPS_NOTICE_LINES
          f"the notice lines are not verbatim straight after the pointer line — {r.ctx()}")
    check(any(l.startswith(SURFACED_PREFIX) for l in lines), f"no Surfaced line — {r.ctx()}")
    for l in lines:
        if re.search(r"(?<![\w.-])root(?![\w.-])", l):
            check(l.startswith(SURFACED_PREFIX), f"a known id is named outside the Surfaced line: {l!r}")
        check(not re.search("loaded", l, re.I), f"a line says `loaded`: {l!r}")
    return "notices kept after the pointer; a known id only on the Surfaced line; no line says loaded"


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
    d = read_ledger(p)                          # X151 ROUTE_HOOK_KEEPS_THE_PATH: ids in the ledger
    check(d.get("surfaced") == sorted(LOAD_IDS), f"surfaced {d.get('surfaced')!r} must hold the node ids only")
    return "an id outside surfaced gets `New for this task:` and its pathed entry line; the ledger holds ids"


@case("X111", "REMINDER_DROPS_PEERS_ALREADY_SHOWN")
def x111(base):
    p = Plant(base)
    write_ledger(p, peers_seen=["agent.implementer"])
    r = route(p, "zq-sentinel-0111 widget ledger work")
    check(is_reminder(r), f"expected reminder mode — {r.ctx()}")
    lines = r.inj.split("\n")
    check(PEERS_HEADER in lines, f"no `{PEERS_HEADER}` line — {r.ctx()}")
    i = lines.index(PEERS_HEADER)
    check(dict(NL)["domain.sprocketry"] in lines[i + 1:], f"the unseen peer's entry line is missing — {r.ctx()}")
    check(not any("agent.implementer" in l for l in lines), f"a peer already shown was repeated — {r.ctx()}")
    check("domain.sprocketry" in read_ledger(p).get("peers_seen", []), "the unseen peer was not added to peers_seen")
    return "a peer already shown is dropped; the unseen one is listed and recorded"


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
    return f"count REFRESH_EVERY ({n}) refreshes and rebuilds; N-1 reminds"


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
    for what, env in (("Copilot envelope", copilot), ("session_id null", dict(copilot, session_id=None))):
        for turn in (1, 2):
            r = route(p, prompt, envelope=env)
            expect_full(r, f"{what}, prompt {turn}")
            check(r.err == "", f"{what}, prompt {turn}: expected no stderr — {r.ctx()}")
            check(not p.sess.exists(), f"{what}: something was created under .cypress/session/")
    r = run_hook(p, "")                       # CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE
    check(r.rc == 0 and r.err == "", f"empty stdin: expected exit 0 and no stderr — {r.ctx()}")
    return "no `session_id` key, or a null one: full mode every time, no file, no stderr; empty stdin exits 0"


INVALID_SIDS = ["../../escape", "a/b", "ab\x00cd"]


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
        check(str(sid) not in r.err, f"session_id {sid!r}: stderr carries the raw id")
    return "three unsafe ids: full mode, one stderr line without the id, nothing written"


@case("X120", "LEDGER_CORRUPT_FULL; failure LEDGER_UNUSABLE")
def x120(base):
    p = Plant(base)
    good = ledger_doc(prompt_count=3)
    variants = [                                  # (what, raw, age); X121 and X122 are rows
        ("invalid JSON", "{not valid json", 60),
        ("extra key", json.dumps(dict(good, extra=1)), 60),
        ("over LEDGER_MAX_BYTES", json.dumps(good) + " " * (LEDGER_MAX_BYTES + 100), 60),
        ("X121 LEDGER_UNKNOWN_VERSION_FULL: version 2", json.dumps(dict(good, version=2)), 60),
        ("X122 LEDGER_EXPIRED_FULL: older than LEDGER_TTL", json.dumps(good), DAY),
    ]
    for what, raw, age in variants:
        write_ledger(p, raw=raw, age=age)
        r = route(p, "zq-sentinel-0120 widget ledger work")
        expect_full(r, what)
        expect_one_err(r, what)
        expect_fresh_ledger(p, what)
    return "corrupt, version 2 and expired ledgers: full mode, one stderr line, a fresh v1 ledger at count 1"


# ---------------------------------------------------------------- reset
def expect_reset(p, source_want, what):
    check(p.ledger().is_file(), f"{what}: the ledger is gone")
    d = read_ledger(p)
    check(d["prompt_count"] == 0 and d["surfaced"] == [] and d["peers_seen"] == []
          and isinstance(d["last_reset"], dict) and d["last_reset"].get("source") == source_want,
          f"{what}: expected count 0, empty sets, last_reset.source {source_want!r}; got {d!r}")


@case("X123", "STATUS_HOOK_RESETS_LEDGER")
def x123(base):
    sources = [("startup", "startup"), (MISSING, "unknown")]
    for i, (src, want) in enumerate(sources):
        what = f"source {'absent' if src is MISSING else repr(src)}"
        p = Plant(base, name=f"plant{i}", register=True)
        write_ledger(p, prompt_count=3)
        status(p, source=src)
        expect_reset(p, want, what)
        expect_full(route(p, "zq-sentinel-0123 widget ledger work"), f"{what}, next prompt")
    return "`startup` and an absent source reset the ledger; the next prompt is full"


@case("X124", "STATUS_HOOK_NO_LEDGER_WRITES_NOTHING")
def x124(base):
    p = Plant(base, register=True)
    for what, sid in (("valid id, no ledger", SID), ("no session_id", MISSING),
                      ("invalid id", "../../escape")):
        before = snapshot(p.dir / ".cypress")
        r = status(p, sid=sid, source="startup")
        diff = snap_diff(before, snapshot(p.dir / ".cypress"))
        check(not diff, f"{what}: status-hook wrote under .cypress/: {diff}")
        if sid is MISSING:                    # CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE
            check(r.err == "", f"{what}: expected no stderr — {r.ctx()}")
    r = run_hook(p, "", hook=p.hook("status-hook.py"))
    check(r.rc == 0 and r.err == "", f"empty stdin: expected exit 0 and no stderr — {r.ctx()}")
    expect_full(route(p, "zq-sentinel-0124 widget ledger work"), "next prompt for the valid id")
    return "no ledger, no id or a bad id: status-hook writes nothing; next prompt full"


@case("X125", "STATUS_HOOK_RESETS_WITHOUT_REGISTER")
def x125(base):
    p = Plant(base)                                     # a graph, no status-register.py
    write_ledger(p, prompt_count=3)
    r = status(p, source="startup")
    expect_reset(p, "startup", "no register")
    lines = [l for l in (r.inj or "").split("\n") if l]
    check(r.out == "" or r.envelope_ok, f"stdout is neither empty nor one hook envelope — {r.ctx()}")
    check(all(l.startswith("Code anchor: ") for l in lines),
          f"no register: stdout carries more than the code-anchor line — {r.ctx()}")
    return "no register: the ledger still resets; no status summary, at most the code-anchor line"


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
    q = Plant(base, name="statfail", register=True)          # X147: the ledger stat fails
    write_ledger(q, prompt_count=3)
    r = status(q, source="startup", wrapper="statfail")
    no_traceback(r, "ledger stat fails")
    check(r.inj is not None and SUMMARY in r.inj, f"ledger stat fails: no status summary — {r.ctx()}")
    expect_one_err(r, "ledger stat fails")
    check(SID not in r.err, f"the reset's stderr line carries the raw session id — {r.ctx()}")
    return "reset write or ledger stat fails: summary injected, one stderr line; a failed write unlinks"


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


@case("X130", "LEDGER_SYMLINK_REFUSED; failures LEDGER_UNUSABLE, LEDGER_DIR_UNUSABLE")
def x130(base):
    def reminder_ledger(path):
        path.write_text(json.dumps(ledger_doc()))
        os.chmod(path, 0o600)
        t = time.time() - 60
        os.utime(path, (t, t))

    for i, what in enumerate(("`.cypress/session` a symlink", "the ledger a symlink", "the ledger a FIFO")):
        cb = base / f"c{i}"
        cb.mkdir()
        out = cb / "outside"
        out.mkdir()
        p = Plant(cb)
        if i == 0:
            os.chmod(out, 0o700)
            (out / ".gitignore").write_text("*\n")
            reminder_ledger(out / f"{SID}.json")
            os.symlink(out, p.sess)
        elif i == 1:
            ensure_session_dir(p)
            reminder_ledger(out / "ledger.json")
            os.symlink(out / "ledger.json", p.ledger())
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
    return "session-dir symlink, ledger symlink, FIFO: exit 0 within 5 s, outside untouched, full, one stderr line"


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
    for kind, what in (("perm", "os.replace raises PermissionError"), ("oserror", "X129 LEDGER_WRITE_IS_ATOMIC: os.replace fails")):
        p = Plant(base, name=kind)
        led = write_ledger(p)
        old = led.read_bytes()
        r = route(p, "zq-sentinel-0133 widget ledger work", wrapper=kind)
        expect_full(r, what)
        expect_one_err(r, what)
        check(led.read_bytes() == old, f"{what}: a failed replace changed the ledger")
    return "a replace that fails gives full mode and one stderr line and leaves the ledger intact"


@case("X134", "LEDGER_GC_BOUNDED")
def x134(base):
    now = time.time()
    p = Plant(base)
    ensure_session_dir(p)
    s = p.sess
    for i in range(3):
        f = s / f"old-ledger-{i}.json"
        f.write_text(json.dumps(ledger_doc(f"old-ledger-{i}")))
        os.chmod(f, 0o600)
        os.utime(f, (now - 8 * DAY, now - 8 * DAY))
    (s / "notes.txt").write_text("owner notes\n")
    route(p, "zq-sentinel-0134 widget ledger work")
    names = set(os.listdir(s))
    check(p.ledger().is_file(), "the current session's ledger was not created")
    check(not any(n.startswith("old-ledger-") for n in names), "a ledger older than GC_MAX_AGE survived")
    check((s / "notes.txt").read_text() == "owner notes\n", "a foreign file was changed or removed")
    q = Plant(base, name="scanfail")                          # X149: GC's scan fails
    r = route(q, "zq-sentinel-0149 widget ledger work", wrapper="scandirfail")
    expect_full(r, "GC scan fails")
    at_most_one_err(r, "GC scan fails")
    check(q.ledger().is_file() and read_ledger(q)["prompt_count"] == 1,
          f"a failed GC blocked the ledger write — {r.ctx()}")
    return "GC on creation: old ledgers go, foreign files stay; a failed scan still writes the ledger"


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


# ---------------------------------------------------------------- fail-open regressions
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
    r = run_hook(p, nested)
    s = run_hook(p, nested, hook=p.hook("status-hook.py"))
    check(r.rc == 0 and "Traceback" not in r.err and one_err_line(r) and is_pointer_only(r),
          f"route-hook, 100 000 nested `[`: expected exit 0, one stderr line, the pointer line — {r.ctx()}")
    check(s.rc == 0 and "Traceback" not in s.err and (s.err == "" or one_err_line(s))
          and s.inj is not None and SUMMARY in s.inj,
          f"status-hook, 100 000 nested `[`: expected exit 0, at most one stderr line, the summary — {s.ctx()}")
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


@case("X148", "LEDGER_WRITE_FAILURE_FAILS_OPEN")
def x148(base):
    # Node ids at the pattern's upper length, enough that the ledger the hook
    # would write is over LEDGER_MAX_BYTES while each list is within 512.
    def nid(kind, i):
        return f"{kind}.{i:04d}." + "x" * 110
    load = [nid("load", i) for i in range(300)]
    nl = [nid("peer", i) for i in range(300)]
    body = (f"LOAD ({len(load)} nodes, ~9 tokens):\n" + "".join(f"  {n}  a\n" for n in load)
            + "\nNOT LOADED (with the reason; cross only if the task requires it):\n"
            + "".join(f"  {n}  b\n" for n in nl))
    p = Plant(base, body=body)
    r = route(p, "zq-sentinel-0148 widget ledger work")
    expect_full(r, "oversize ledger", remainder=body)
    check(not p.ledger().exists(), "a ledger over LEDGER_MAX_BYTES was written")
    expect_one_err(r, "a ledger over LEDGER_MAX_BYTES is refused, not written")
    return "a ledger over LEDGER_MAX_BYTES is not written; full mode and one stderr line"


# ---------------------------------------------------------------- the anchor line at session start
ANCHOR_LINE = "Code anchor: zq-sentinel-0161 a fixed line from the test's stub tool."
NOT_CHECKED = ("Code anchor: not checked this session (the comparison did not run). "
               "Facts about code in the graph are unverified.")
ANCHOR_STUB = r"""#!/usr/bin/env python3
import json, sys, time
from pathlib import Path
MODE = %r
LINE = %r
Path(__file__).with_name("anchor-argv.json").write_text(json.dumps(sys.argv[1:]))
if MODE == "sleep":
    time.sleep(3)
args = sys.argv[1:]
if "--compare" in args and "--record" not in args and "--all" not in args:
    print(LINE)
else:
    print("Code anchor: zq-wrong-mode-0161 the stub was not run as --compare alone")
"""


def anchor_stub(plant, mode="line"):
    (plant.dir / "docs" / "graph" / "code-anchor.py").write_text(ANCHOR_STUB % (mode, ANCHOR_LINE))


@case("X161", "STATUS_HOOK_INJECTS_THE_ANCHOR_LINE")
def x161(base):
    problems = []
    for i, reg in enumerate((True, False)):
        what = "with a status register" if reg else "without a status register"

        def one():
            p = Plant(base, name=f"plant{i}", register=reg)
            anchor_stub(p)
            write_ledger(p, prompt_count=3)
            r = status(p, source="startup")
            lines = (r.inj or "").rstrip("\n").split("\n")
            check(r.inj is not None and lines[-1] == ANCHOR_LINE,
                  f"{what}: additionalContext does not end with the line the tool printed — {r.ctx()}")
            check((p.dir / "docs" / "graph" / "anchor-argv.json").is_file(),
                  f"{what}: the anchor tool was never run — {r.ctx()}")
            if reg:
                s = [k for k, l in enumerate(lines) if SUMMARY in l]
                check(s and s[0] < len(lines) - 1,
                      f"{what}: the status summary is not injected before the anchor line — {r.ctx()}")
            expect_reset(p, "startup", what)
        collect(problems, one)
    check(not problems, " || ".join(problems))
    return "with and without a register: the injection ends with the tool's line, after the summary; the reset holds"


@case("X162", "STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION; failure ANCHOR_CHECK_DID_NOT_RUN")
def x162(base):
    check(read_constant(HOOKS / "status-hook.py", "ANCHOR_TIMEOUT"),
          "ANCHOR_TIMEOUT: no module-level literal in status-hook.py")
    problems = []
    for mode, what in (("absent", "the tool is absent"), ("sleep", "the tool runs past ANCHOR_TIMEOUT (rewritten to 1)")):
        def one():
            p = Plant(base, name=mode)
            if mode == "sleep":
                anchor_stub(p, mode)
                rewrite_constant(p.hook("status-hook.py"), "ANCHOR_TIMEOUT", 1)
            r = status(p, source="startup")
            check(not r.timed_out, f"{what}: the hook did not return — {r.ctx()}")
            check(NOT_CHECKED in (r.inj or "").split("\n"), f"{what}: no not-checked line in additionalContext — {r.ctx()}")
            check(ANCHOR_LINE not in (r.inj or ""), f"{what}: the output of a tool that failed was injected — {r.ctx()}")
        collect(problems, one)
    check(not problems, " || ".join(problems))
    return "absent and timed out, no register: the not-checked line, exit 0"


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



# --- Prime Agent extensions and overlay, structural (X135-X141, X150, X163-X165)
# No TypeScript runtime and no model in the gate, so these read the sources as
# text and prove wording and shape, never what a model does (SPEC-0003 §10).
PRIME_RC=0
python3 - "$ROOT" <<'PY' || PRIME_RC=1
import json, re, sys, traceback
from pathlib import Path

SEED = Path(sys.argv[1])


def read(rel):
    src = (SEED / rel).read_text(encoding="utf-8")
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), src)   # escapes decoded


EXT = read("integrations/prime-agent/route-extension.ts")
STATUS_EXT = read("integrations/prime-agent/status-extension.ts")
HOOK = read("integrations/claude-code/route-hook.py")
STATUS_HOOK = read("integrations/claude-code/status-hook.py")
OVERLAY = read("integrations/prime-agent/APPEND_SYSTEM.md")
POINTER = "Route first: the kernel's FIRST MOVE and §0 apply to this prompt."
SUGGESTION_HEADER = "Router suggestion (a keyword heuristic — reason over it):"
NOT_CHECKED = ("Code anchor: not checked this session (the comparison did not run). "
               "Facts about code in the graph are unverified.")
OVERLAY_SECTION_MAX_BYTES = 512          # SPEC-0003 §6: this block is its one home


class CaseFail(Exception):
    pass


def check(cond, msg):
    if not cond:
        raise CaseFail(msg)


CASES = []


def case(label, slug):
    def deco(fn):
        CASES.append((label, slug, fn))
        return fn
    return deco


@case("X135", "ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX; ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE")
def x135():
    # X136 (the prompt as one `--plan=` value) and X150 (the echo tested on the raw stdout) are here.
    for s in ("`--plan=${", ".stdout.startsWith(", "`task: ${"):
        check(s in EXT, f"route-extension.ts lacks {s!r}")
    check(EXT.count("pi.exec(") == 1, f"expected one `pi.exec(` call, found {EXT.count('pi.exec(')}")
    return "`--plan=${…}`, the `task: ${…}` prefix tested on stdout with startsWith, one pi.exec"


@case("X137", "ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK")
def x137():
    for text in (POINTER, SUGGESTION_HEADER):
        check(f'"{text}"' in HOOK, f"route-hook.py has no literal {text!r}")
        check(f'"{text}"' in EXT, f"route-extension.ts has no literal {text!r}")
    return "the pointer line and the suggestion header are the same literal in both sources"


@case("X138", "ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE")
def x138():
    calls = re.findall(r"\b(writeFile|appendFile|mkdir|rename|createWriteStream|copyFile|cp|open|truncate|symlink)"
                       r"(?:Sync)?\s*\(", EXT)
    check(not calls, f"route-extension.ts calls an fs write: {calls}")
    return "no fs write call"


@case("X141", "PRIME_OVERLAY_SECTION_WITHIN_CEILING")
def x141():
    heads = [m.start() for m in re.finditer(r"^## Surfaced nodes\s*$", OVERLAY, re.M)]
    check(len(heads) == 1, f"APPEND_SYSTEM.md has {len(heads)} `## Surfaced nodes` sections; exactly one is required")
    nxt = re.search(r"^## ", OVERLAY[heads[0] + 3:], re.M)
    sec = OVERLAY[heads[0]:heads[0] + 3 + nxt.start()] if nxt else OVERLAY[heads[0]:]
    check("_cypress_surfaced" in sec, "X139 PRIME_OVERLAY_KEEPS_SURFACED_SET: the section does not name `_cypress_surfaced`")
    check(not re.search("loaded", sec, re.I), "X140 PRIME_OVERLAY_NEVER_SAYS_LOADED: the section says `loaded`")
    n = len(sec.encode("utf-8"))
    check(n <= OVERLAY_SECTION_MAX_BYTES, f"the section is {n} B, over OVERLAY_SECTION_MAX_BYTES")
    return f"one section naming `_cypress_surfaced`, never `loaded`, {n} B within {OVERLAY_SECTION_MAX_BYTES}"


@case("X163", "STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE; failure ANCHOR_CHECK_DID_NOT_RUN")
def x163():
    for s in ('"code-anchor.py"', '"--compare"', f'"{NOT_CHECKED}"'):
        check(s in STATUS_EXT, f"status-extension.ts lacks {s}")
    return "code-anchor.py, --compare and the not-checked literal"


@case("X164", "STATUS_HOOK_INJECTS_THE_ANCHOR_LINE, STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE; once per session")
def x164():
    for rel in ("integrations/claude-code/settings.json", "integrations/github-copilot/hooks/status.json"):
        hooks = json.loads(read(rel)).get("hooks") or {}
        events = sorted(ev for ev, entries in hooks.items() if "status-hook.py" in json.dumps(entries))
        check(events == ["SessionStart"], f"{rel} wires status-hook.py under {events}, not under SessionStart alone")
    return "settings.json and the Copilot status.json wire status-hook.py under SessionStart alone"


@case("X165", "STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION; ANCHOR_TIMEOUT is one value")
def x165():
    hook = re.findall(r"^ANCHOR_TIMEOUT\s*=\s*([\d.]+)", STATUS_HOOK, re.M)
    ext = re.findall(r'"--compare"\],\s*\{\s*timeout:\s*([\d_]+)', STATUS_EXT)
    check(len(hook) == 1 and len(ext) == 1, f"ANCHOR_TIMEOUT {hook}, the anchor's pi.exec timeout {ext}: one each")
    hook_s, ext_s = float(hook[0]), float(ext[0].replace("_", "")) / 1000
    check(hook_s == ext_s, f"status-hook.py ANCHOR_TIMEOUT {hook_s:g} s != status-extension.ts {ext_s:g} s")
    return f"status-hook.py and the anchor's pi.exec agree: {hook_s:g} s"


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

echo "test-prompt-hooks: PASS"
