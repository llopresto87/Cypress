#!/usr/bin/env python3
"""route-hook.py — a UserPromptSubmit hook that points each prompt at the
kernel and attaches the graph router's suggestion, naming a node by id alone
once this session has already been shown it. Works in BOTH Claude Code and
VS Code Copilot (Agent Hooks, Preview): both read `.claude/settings.json`
hooks, and both inject context via the `hookSpecificOutput.additionalContext`
output shape.

Installed to `.claude/route-hook.py` and wired in `.claude/settings.json`
under hooks.UserPromptSubmit, this runs on every prompt. The host passes
`{"prompt": "..."}` (plus `cwd`, `session_id`, `hook_event_name`) on stdin;
whatever `additionalContext` this returns is injected as a prepended message
before the model answers. The rules themselves live in the kernel; this hook
only points at them (SPEC-0003).

Three parts, kept apart:

- The router call. The prompt reaches `docs/graph/graph-lint.py` as one
  `--plan=<prompt>` argv value, with no shell. Output that does not begin with
  the exact echo `task: <prompt>` and a blank line is a router failure, so the
  prompt is never passed back into the session.
- The mode decision (`decide`), a pure function of the router's ids, the
  session ledger and REFRESH_EVERY. Full mode is the pointer line and the
  router's suggestion; reminder mode names what this session was already
  shown by id, and gives entry lines only for what is new.
- The session ledger, `.cypress/session/<session_id>.json`. This file is its
  one owner: path rule, schema, descriptor-relative I/O, garbage collection
  and `reset_ledger`, which status-hook.py loads from here on SessionStart.

Every doubt resolves toward the full injection. It never blocks: exit 0
always; once graph-lint.py resolves, at least the pointer line is emitted,
and any ledger failure emits the full text with one stderr line.

Context injection REQUIRES JSON on stdout — plain text is not injected by
Copilot.
"""

import json
import os
import re
import secrets
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple

# The same script may live at .claude/route-hook.py or
# .github/hooks/route-hook.py (different depths), so find the project
# root by walking up for the graph linter rather than assuming a depth.
#
# One candidate, and it is the one the installer writes. A candidate list is a
# claim about where the artifact is written, so a path no writer produces is
# not a fallback: the only file it could ever select is one this project did
# not put there. That is the unbounded reach `_is_plant_root` below bounds,
# arriving through the list instead of through the walk. A path is listed here
# only while something writes it, and is deleted in the change that retires
# the writer.
CANDIDATES = (Path("docs") / "graph" / "graph-lint.py",)


# --- canonical plant-root boundary ---
def _is_plant_root(p) -> bool:
    """True where an upward walk must stop, that directory INCLUDED.

    Unbounded, these walks ascend seven or eight levels from both the cwd and
    the script's own directory and take the first artifact they find. A plant
    checked out inside another checkout therefore used the ANCESTOR's — a file
    the plant does not own, chosen by directory nesting. Reproduced from a git
    repo at `outer/sub/child` with no roster of its own: `agent-lint.py --route`
    returned the ancestor repository's agent at HIGH confidence, score 36, and
    `--lint` printed OK over that foreign roster.

    Callers test their candidate BEFORE calling this, so a plant whose artifact
    sits at its own repo root is still found; only the step BEYOND the root is
    denied.
    """
    return (p / ".git").exists() or (p / ".cypress").is_dir()
# --- end canonical plant-root boundary ---


def find_lint():
    """Locate the plant's graph linter by walking up — but never out of the
    plant. The walk stops at the first directory that looks like a project
    root (`.git`, or the seed stamp `.cypress/`), that directory included.

    Unbounded, the walk ascended seven levels from BOTH the cwd and the script
    directory and executed the first graph-lint.py it found. A plant checked
    out inside another checkout therefore ran the ANCESTOR's linter on every
    prompt — a script the plant does not own, chosen by directory nesting.
    Reproduced during the 7.15.0 audit: from a git repo at `outer/child`, the
    walk resolved to `outer/docs/graph/graph-lint.py`.
    """
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    seen = set()
    for start in starts:
        p = start
        for _ in range(7):
            if p in seen:
                break
            seen.add(p)
            for rel in CANDIDATES:
                if (p / rel).exists():
                    return p / rel, p
            if _is_plant_root(p):
                break
            if p.parent == p:
                break
            p = p.parent
    return None, Path.cwd()


LINT, ROOT = find_lint()

TRIVIAL = {"", "yes", "no", "ok", "thanks", "thank you", "go", "continue", "y", "n"}

# --- injected text (SPEC-0003 §6; compared byte for byte by the tests) ---
# POINTER and SUGGESTION_HEADER are also literals in the Prime Agent twin,
# integrations/prime-agent/route-extension.ts, so the two cannot drift apart.
POINTER = "Route first: the kernel's FIRST MOVE and \u00a70 apply to this prompt."
SUGGESTION_HEADER = "Router suggestion (a keyword heuristic \u2014 reason over it):"
NEW_PREFIX = "New for this task: "
SURFACED_LINE = "Surfaced earlier this session: {} \u2014 open if not in view."
PEERS_HEADER = "Not suggested, not listed before (cross only if needed):"
NO_GRAPH = ("No knowledge graph found (docs/graph/). Use the canonical "
            "INSTALL_PROMPT.md; /initialize is the entry fork behind it \u2014 "
            "grow when there is source to scout, from-scratch when the "
            "repository is empty.")

# --- ledger constants: this file is their one home ---
LEDGER_VERSION = 1
REFRESH_EVERY = 10          # routed prompts per full injection; plan §4.7 may retune it
ROUTER_TIMEOUT = 15         # seconds
LEDGER_TTL = 12 * 3600
GC_MAX_AGE = 7 * 86400
GC_MAX_FILES = 32
GC_SCAN_MAX = 256
TEMP_PREFIX = ".tmp-"
TEMP_MAX_AGE = 3600
LEDGER_MAX_BYTES = 64 * 1024
SURFACED_MAX = 512

SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
NODE_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
RESET_SOURCE = re.compile(r"^[a-z_-]{1,32}$")
TEMP_NAME = re.compile(r"^" + re.escape(TEMP_PREFIX) + r"[A-Za-z0-9_-]{1,64}$")
ISO_UTC = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(Z|\+00:00)$")
LEDGER_KEYS = ("version", "session_id", "prompt_count", "surfaced", "peers_seen", "last_reset")
SESSION_DIR = (".cypress", "session")
GITIGNORE = ".gitignore"

# Every ledger call is relative to a directory descriptor. A platform without
# these has no safe way to refuse a symlink, so it gets no ledger at all, never
# a path-string fallback. os.replace rides on renameat, which CPython lists
# under the name `rename`.
DIR_FD_CALLS = {"open", "mkdir", "stat", "unlink", "rename"}


def emit(text: str, event: str) -> None:
    if not text:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event or "UserPromptSubmit",
            "additionalContext": text,
        }
    }))


def warn(message: str) -> None:
    """The one stderr line a fallback owes. Never carries the raw session id."""
    print(f"route-hook: {message}", file=sys.stderr)


# --- the router call -------------------------------------------------------
class Entry(NamedTuple):
    node: str
    line: str


class Suggestion(NamedTuple):
    notices: list
    load: list
    not_loaded: list


def run_router(prompt: str):
    """The router's output with the exact echo prefix removed, or None when the
    router failed: a non-zero exit, a timeout, no output, a prompt the OS
    cannot pass as an argument (a NUL byte, over the argument limit), or output
    that does not begin with `task: <prompt>` and a blank line."""
    try:
        out = subprocess.run(
            [sys.executable, str(LINT), "--plan=" + prompt],
            capture_output=True, text=True, timeout=ROUTER_TIMEOUT, cwd=str(ROOT),
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    prefix = f"task: {prompt}\n\n"
    if out.returncode != 0 or not out.stdout.startswith(prefix):
        return None
    return out.stdout[len(prefix):]


def parse_suggestion(remainder: str):
    """The router's notice lines and LOAD / NOT LOADED entries, in its order,
    or None when the remainder does not follow the `--plan` grammar."""
    notices, load, not_loaded = [], [], []
    section = None
    for line in remainder.splitlines():
        if not line.strip():
            continue
        if section is None and line.startswith("  ! "):
            notices.append(line)
        elif section is None and line.startswith("LOAD ("):
            section = load
        elif section is load and line.startswith("NOT LOADED ("):
            section = not_loaded
        elif section is not None and line.startswith("  "):
            node = line.split()[0]
            if not NODE_ID.match(node):
                return None
            section.append(Entry(node, line))
        else:
            return None
    if section is None:
        return None
    return Suggestion(notices, load, not_loaded)


def full_text(remainder: str) -> str:
    return POINTER + "\n\n" + SUGGESTION_HEADER + "\n" + remainder.strip()


# --- the mode decision (pure) ----------------------------------------------
def decide(ledger, suggestion: Suggestion):
    """Which text this prompt gets, and the ledger fields after it.

    Full when there is no usable record, a reset was recorded (count 0), or
    REFRESH_EVERY routed prompts have passed; a full injection rebuilds the
    record from itself alone. Otherwise reminder, which only adds. A reminder
    that would overflow SURFACED_MAX is a refresh instead.
    """
    load = {e.node for e in suggestion.load}
    not_loaded = {e.node for e in suggestion.not_loaded}
    if ledger is not None and 0 < ledger["prompt_count"] < REFRESH_EVERY:
        surfaced = set(ledger["surfaced"]) | load
        peers = set(ledger["peers_seen"]) | (not_loaded - surfaced)
        if len(surfaced) <= SURFACED_MAX and len(peers) <= SURFACED_MAX:
            return "reminder", ledger["prompt_count"] + 1, surfaced, peers
    return "full", 1, load, not_loaded - load


def reminder_text(ledger, suggestion: Suggestion) -> str:
    """Reminder mode: the pointer, the router's notices, the entry lines of what
    is new this session, one line naming the rest by id, and only the peers
    not listed before. Each part is dropped when empty."""
    shown = set(ledger["surfaced"])
    new = [e for e in suggestion.load if e.node not in shown]
    known = [e.node for e in suggestion.load if e.node in shown]
    listed = shown | {e.node for e in suggestion.load} | set(ledger["peers_seen"])
    peers = [e.line for e in suggestion.not_loaded if e.node not in listed]
    lines = [POINTER, *suggestion.notices]
    if new:
        lines.append(NEW_PREFIX + ", ".join(e.node for e in new))
        lines.extend(e.line for e in new)
    if known:
        lines.append(SURFACED_LINE.format(", ".join(known)))
    if peers:
        lines.append(PEERS_HEADER)
        lines.extend(peers)
    return "\n".join(lines)


# --- the session ledger ----------------------------------------------------
class LedgerUnusable(Exception):
    """A ledger or its directory that fails a §6 rule. The message is the
    stderr line, and never carries the raw session id."""


def valid_session_id(value) -> bool:
    return isinstance(value, str) and bool(SESSION_ID.match(value))


def ledger_problem(doc, session_id: str):
    """Why `doc` is not a version-1 ledger for `session_id`, or None."""
    if not isinstance(doc, dict) or set(doc) != set(LEDGER_KEYS):
        return "not a ledger object"
    if type(doc["version"]) is not int or doc["version"] != LEDGER_VERSION:
        return "unknown version"
    if doc["session_id"] != session_id:
        return "records another session"
    count = doc["prompt_count"]
    if type(count) is not int or count < 0:
        return "bad prompt_count"
    for key in ("surfaced", "peers_seen"):
        ids = doc[key]
        if (not isinstance(ids, list) or len(ids) > SURFACED_MAX
                or not all(isinstance(i, str) and NODE_ID.match(i) for i in ids)
                or ids != sorted(set(ids))):
            return f"bad {key}"
    reset = doc["last_reset"]
    if reset is not None and not (
            isinstance(reset, dict) and set(reset) == {"source", "at"}
            and isinstance(reset["source"], str) and RESET_SOURCE.match(reset["source"])
            and isinstance(reset["at"], str) and ISO_UTC.match(reset["at"])):
        return "bad last_reset"
    return None


def ledger_doc(session_id, prompt_count, surfaced, peers_seen, last_reset):
    return {"version": LEDGER_VERSION, "session_id": session_id,
            "prompt_count": prompt_count, "surfaced": sorted(surfaced),
            "peers_seen": sorted(peers_seen), "last_reset": last_reset}


def _refused_by_mode(st) -> bool:
    return st.st_uid != os.geteuid() or bool(st.st_mode & 0o022)


def open_session_dir(create: bool):
    """A descriptor on <ROOT>/.cypress/session, opened without following a
    symlink at either step, owned by this user and writable by no one else.

    With `create`, the session directory and its self-ignoring `.gitignore`
    are made when absent; `.cypress/` never is, since it marks a plant root.
    Without it, an absent directory returns None. Anything else unusable
    raises LedgerUnusable naming the path.
    """
    if not (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
            and DIR_FD_CALLS <= {f.__name__ for f in os.supports_dir_fd}
            and os.scandir in os.supports_fd):
        raise LedgerUnusable("no descriptor-relative file calls on this platform; "
                             "no session ledger")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    top_name, sub_name = SESSION_DIR
    try:
        top = os.open(ROOT / top_name, flags)
    except FileNotFoundError:
        if not create:
            return None
        raise LedgerUnusable(f"{top_name}/ is missing, and this hook never creates it")
    except OSError as e:
        raise LedgerUnusable(f"{top_name}/ unusable ({e.strerror})")
    where = "/".join(SESSION_DIR)
    try:
        if create:
            try:
                os.mkdir(sub_name, 0o700, dir_fd=top)
            except FileExistsError:
                pass
        fd = os.open(sub_name, flags, dir_fd=top)
    except FileNotFoundError:
        if not create:
            return None
        raise LedgerUnusable(f"{where}/ could not be created")
    except OSError as e:
        raise LedgerUnusable(f"{where}/ unusable ({e.strerror})")
    finally:
        os.close(top)
    try:
        if _refused_by_mode(os.fstat(fd)):
            raise LedgerUnusable(f"{where}/ is another user's or writable by group or others")
        try:
            st = os.stat(GITIGNORE, dir_fd=fd, follow_symlinks=False)
            if not stat.S_ISREG(st.st_mode):
                raise LedgerUnusable(f"{where}/{GITIGNORE} is not a regular file")
        except FileNotFoundError:
            if create:
                ignore = os.open(GITIGNORE, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=fd)
                try:
                    os.write(ignore, b"*\n")
                finally:
                    os.close(ignore)
    except BaseException:
        os.close(fd)
        raise
    return fd


def read_ledger(dir_fd: int, session_id: str, now: float):
    """This session's ledger, None when there is none, or LedgerUnusable. At
    most LEDGER_MAX_BYTES + 1 bytes are read, and only after fstat shows a
    regular file this user owns and nobody else can write."""
    try:
        fd = os.open(session_id + ".json", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=dir_fd)
    except FileNotFoundError:
        return None
    except OSError as e:
        raise LedgerUnusable(f"session ledger unusable ({e.strerror})")
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise LedgerUnusable("session ledger is not a regular file")
        if _refused_by_mode(st):
            raise LedgerUnusable("session ledger is another user's or writable by group or others")
        if now - st.st_mtime > LEDGER_TTL:
            raise LedgerUnusable("session ledger expired")
        raw = b""
        while len(raw) <= LEDGER_MAX_BYTES:
            chunk = os.read(fd, LEDGER_MAX_BYTES + 1 - len(raw))
            if not chunk:
                break
            raw += chunk
    finally:
        os.close(fd)
    if len(raw) > LEDGER_MAX_BYTES:
        raise LedgerUnusable("session ledger oversized")
    try:
        doc = json.loads(raw)
    except (ValueError, RecursionError):
        raise LedgerUnusable("session ledger is not valid JSON")
    problem = ledger_problem(doc, session_id)
    if problem:
        raise LedgerUnusable(f"session ledger unusable ({problem})")
    return doc


def write_ledger(dir_fd: int, doc: dict) -> None:
    """Replace this session's ledger atomically: a 0600 temp file created
    exclusively, then os.replace onto the name. On any failure the temp file is
    removed and the old ledger, if any, stays as it was."""
    problem = ledger_problem(doc, doc.get("session_id"))
    if problem:
        raise LedgerUnusable(f"refusing to write a ledger that breaks its schema ({problem})")
    tmp = TEMP_PREFIX + secrets.token_hex(8)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dir_fd)
    try:
        try:
            os.write(fd, (json.dumps(doc) + "\n").encode())
        finally:
            os.close(fd)
        os.replace(tmp, doc["session_id"] + ".json", src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        try:
            os.unlink(tmp, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        raise


def _remove(dir_fd: int, name: str) -> None:
    try:
        os.unlink(name, dir_fd=dir_fd)
    except FileNotFoundError:
        pass


def collect_garbage(dir_fd: int, keep: str, now: float) -> None:
    """Run when a session's ledger is first created. Reads at most GC_SCAN_MAX
    entries, and removes only regular files: ledgers older than GC_MAX_AGE,
    temp files older than TEMP_MAX_AGE, then the oldest ledgers until the new
    one will make GC_MAX_FILES. Any other name is never touched."""
    ledgers = []
    with os.scandir(dir_fd) as entries:
        for scanned, entry in enumerate(entries):
            if scanned >= GC_SCAN_MAX:
                break
            name = entry.name
            is_ledger = name.endswith(".json") and bool(SESSION_ID.match(name[:-5]))
            if name == keep or not (is_ledger or TEMP_NAME.match(name)):
                continue
            if not entry.is_file(follow_symlinks=False):
                continue
            mtime = entry.stat(follow_symlinks=False).st_mtime
            if now - mtime > (GC_MAX_AGE if is_ledger else TEMP_MAX_AGE):
                _remove(dir_fd, name)
            elif is_ledger:
                ledgers.append((mtime, name))
    ledgers.sort(reverse=True)
    for _, name in ledgers[GC_MAX_FILES - 1:]:
        _remove(dir_fd, name)


def inject_with_ledger(session_id: str, suggestion: Suggestion, full: str):
    """Read the ledger, decide, compose, write. Returns (text, note), where a
    note is the one stderr line this prompt owes. Raises on any failure, and
    the caller then falls back to `full`, so a reminder is only ever emitted
    when a ledger records it."""
    now = time.time()
    dir_fd = open_session_dir(create=True)
    try:
        note = None
        try:
            ledger = read_ledger(dir_fd, session_id, now)
            created = ledger is None
        except LedgerUnusable as e:
            ledger, created, note = None, False, f"{e}; full injection"
        mode, count, surfaced, peers = decide(ledger, suggestion)
        text = full if mode == "full" else reminder_text(ledger, suggestion)
        last_reset = ledger["last_reset"] if ledger else None
        if created:
            collect_garbage(dir_fd, session_id + ".json", now)
        write_ledger(dir_fd, ledger_doc(session_id, count, surfaced, peers, last_reset))
    finally:
        os.close(dir_fd)
    return text, note


def reset_ledger(session_id, source) -> None:
    """Record a session start in this session's ledger: count 0, no surfaced
    ids, no peers, and `last_reset`. The next routed prompt is therefore full.

    Called by status-hook.py on every SessionStart source, so the ledger keeps
    one owner. Writes nothing when there is no session id, no graph, or no
    ledger for this session. Raises LedgerUnusable for a refused id or an
    unusable directory; when the write fails the ledger is unlinked instead,
    and it still raises, since the caller owes a stderr line either way.
    """
    if session_id is None or LINT is None:
        return
    if not valid_session_id(session_id):
        raise LedgerUnusable("session_id refused (not a safe filename); no reset")
    if not (isinstance(source, str) and RESET_SOURCE.match(source)):
        source = "unknown"
    dir_fd = open_session_dir(create=False)
    if dir_fd is None:
        return
    name = session_id + ".json"
    try:
        try:
            os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            write_ledger(dir_fd, ledger_doc(session_id, 0, (), (), {"source": source, "at": at}))
        except OSError as e:
            try:
                os.unlink(name, dir_fd=dir_fd)
            except OSError as gone:
                raise LedgerUnusable(f"reset not written ({e.strerror}) and the stale "
                                     f"ledger could not be removed ({gone.strerror})")
            raise LedgerUnusable(f"reset not written ({e.strerror}); ledger removed instead")
    finally:
        os.close(dir_fd)


# --- the hook ----------------------------------------------------------------
def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(data, dict):
        return 0
    prompt = data.get("prompt") or data.get("initialPrompt") or ""
    if not isinstance(prompt, str):
        return 0
    prompt = prompt.strip()
    event = data.get("hook_event_name") or data.get("hookEventName") or "UserPromptSubmit"

    if prompt.lower() in TRIVIAL or len(prompt) < 8:
        return 0

    if LINT is None:
        emit(NO_GRAPH, event)
        return 0

    remainder = run_router(prompt)
    if remainder is None:
        emit(POINTER, event)
        return 0
    full = full_text(remainder)

    text, note = full, None
    if "session_id" in data:                      # the exact key only; Copilot sends none
        session_id = data["session_id"]
        suggestion = parse_suggestion(remainder)
        if not valid_session_id(session_id):
            note = "session_id refused (not a safe filename); full injection"
        elif suggestion is None:
            note = "router output not parseable after the echo; full injection, ledger unchanged"
        else:
            try:
                text, note = inject_with_ledger(session_id, suggestion, full)
            except LedgerUnusable as e:
                text, note = full, f"{e}; full injection"
            except OSError as e:
                text, note = full, f"session ledger not written ({e.strerror}); full injection"
            except Exception as e:                # noqa: BLE001 — fail open to the full text
                text, note = full, f"session ledger step failed ({type(e).__name__}); full injection"
    if note:
        warn(note)
    emit(text, event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
