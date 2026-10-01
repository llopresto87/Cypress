#!/usr/bin/env python3
"""route-hook.py — the per-prompt hook core: it points each prompt at the
kernel and attaches the graph router's suggestion, naming a node by id alone
once this session has already been shown it. It runs on every first-class
host: Claude Code and VS Code Copilot (Agent Hooks, Preview) read
`.claude/settings.json` hooks and pass the stdin envelope; Prime Agent's
`route-extension.ts` runs it from `.prime/agent/hooks/` with the argv
envelope. Both get the same `hookSpecificOutput.additionalContext` back.

On Claude Code it is installed to `.claude/route-hook.py` and wired under
hooks.UserPromptSubmit. The host passes `{"prompt": "..."}` (plus `cwd`,
`session_id`, `hook_event_name`) on stdin. Any argument that begins `--`
selects the argv envelope instead (`--prompt=`, `--session-id=`, `--depth=`,
`--origin=`, one element each), and stdin is not read. Whatever
`additionalContext` this returns is injected as a prepended message before the
model answers. The rules themselves live in the kernel; this hook only points
at them (SPEC-0003).

Four parts, kept apart:

- The envelope and the not-routed rule. A trivial prompt, a child session
  (`--depth` above 0), a turn whose `--origin` is not a person, and a prompt
  that opens with a NON_HUMAN_MARKERS entry get nothing: no router run, no
  ledger access.
- The router call. The prompt reaches `docs/graph/graph-lint.py` as one
  `--plan-json=<prompt>` argv value, with no shell. The answer is a
  `cypress.plan/1` document that carries the prompt's SHA-256, never the
  prompt; a document that fails validation, or is bound to another prompt, is
  a router failure. An engine older than this hook, which argparse makes
  reject `--plan-json`, is named in one notice line instead, never routed by
  parsing `--plan` text. The route text is rendered here from the validated
  fields alone, in the compact grammar `graph-lint.py --plan` prints.
- The mode decision (`decide`), a pure function of the router's ids, the
  session ledger and REFRESH_EVERY. Full mode is the pointer line and the
  router's suggestion; reminder mode names what this session was already
  shown by id on one `seen:` line, and gives entry lines and skip items only
  for what is new.
- The session ledger, `.cypress/session/<session_id>.json`. This file is its
  one owner: path rule, schema, descriptor-relative I/O, garbage collection
  and `reset_ledger`, which status-hook.py loads from here on a session start.

Every doubt resolves toward the full injection. It never blocks: exit 0
always; once graph-lint.py resolves, a routed prompt gets at least the
pointer line, and any ledger failure emits the full text with one stderr line.

Context injection REQUIRES JSON on stdout — plain text is not injected by
Copilot.
"""

import hashlib
import itertools
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

# The same script may live at .claude/route-hook.py,
# .github/hooks/route-hook.py or .prime/agent/hooks/route-hook.py (different
# depths), so find the project root by walking up for the graph linter rather
# than assuming a depth.
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
# A prompt whose first non-whitespace text begins with one of these was not
# typed by a person: a host notification, another session's message, a local
# command's output, or a Prime Agent agent-message delivery, background-command
# completion or harness digest. It is not routed and does not count toward
# REFRESH_EVERY (SPEC-0003 §6).
NON_HUMAN_MARKERS = ("<task-notification>", "Another Claude session sent a message:",
                     "<local-command-", "[agent-message from ", "[bash-done ",
                     "[harness-digest]")

# --- injected text (SPEC-0003 §6; compared byte for byte by the tests) ---
POINTER = "Route first: the kernel's FIRST MOVE and \u00a70 apply to this prompt."
SUGGESTION_HEADER = "Router suggestion (a keyword heuristic \u2014 reason over it):"
REMINDER_HEADER = "LOAD {} ~{}t (reminder)"
SEEN_LINE = "seen: {} (surfaced earlier this session; open if not in view)"
SKIP_HEADER = "skip (cross only if the task needs it):"     # also a literal in graph-lint.py
ENGINE_OLDER = "No route: graph-lint.py lacks --plan-json; graft the engine."
NO_GRAPH = ("No knowledge graph found (docs/graph/). Use the canonical "
            "INSTALL_PROMPT.md; /initialize is the entry fork behind it \u2014 "
            "grow when there is source to scout, from-scratch when the "
            "repository is empty.")


# --- ledger and budget constants: this file is their one home ---
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
# What the scripted session under tests/fixtures/session-injection/ receives
# in all, summed over every additionalContext, the status hook's resets
# included (SPEC-0003 SESSION_INJECTION_WITHIN_BUDGET). Recorded in
# tests/ratchets.json; it may only fall.
SESSION_INJECTION_MAX_BYTES = 4960

SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
NODE_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")
RESET_SOURCE = re.compile(r"^[a-z_-]{1,32}$")
ORIGIN = re.compile(r"^[a-z_-]{1,32}$")
CHILD_DEPTH = re.compile(r"^0*[1-9][0-9]*$")      # a decimal integer above 0
RELATIVE_PATH = re.compile(r"^(?!/)(?!.*(^|/)\.\.(/|$))[A-Za-z0-9_./-]+$")
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


def reason(e: OSError) -> str:
    """Why an OS call failed, for a stderr line: the strerror, else the type
    name. Never str(e), which carries the file name, and a ledger's file name
    is the raw session id."""
    return e.strerror or type(e).__name__


# --- the router call -------------------------------------------------------
# The `cypress.plan/1` document `graph-lint.py --plan-json` prints (SPEC-0003
# §6), and the compact `--plan` grammar the route is rendered in from it.
PLAN_SCHEMA = "cypress.plan/1"
PLAN_KEYS = {"schema", "task_sha256", "plant", "notices", "est_tokens", "load", "skip"}
PLANT_KEYS = ("environment_class", "commit_attribution", "deliverable_language",
              "comment_language")       # the `plant:` line's order
NOTICE_CODES = {"wide_descent", "inference_skipped", "long_task", "no_signal"}
HOW_KINDS = {"scored", "requires", "inferred", "composed",
             "named_id", "named_path", "phrase"}
SKIP_GROUPS = {"peer": " peer of {}: ", "composed": " composed by {}, no specific term: "}
LOAD_HEADER = "LOAD {} ~{}t"


class Entry(NamedTuple):
    node: str
    line: str               # a LOAD entry line, or a skip group's `<id>=<path>` item
    group: str = ""         # a skip entry's group line, up to its items


class Suggestion(NamedTuple):
    notices: list           # the notice lines, as `--plan` prints them
    plant: list             # the `plant:` line, or nothing when the document has no facts
    est_tokens: int
    load: list              # [Entry], by id
    not_loaded: list        # [Entry], in the router's order: grouped, by id within a group


class RouterFailed(Exception):
    """The router gave no usable document. A message, when there is one, is
    the stderr line this prompt owes; it never carries a byte the router
    printed. A `notice`, when there is one, is the line the injection carries
    after the pointer."""

    def __init__(self, message: str = "", notice: str = ""):
        super().__init__(message)
        self.notice = notice


def run_router(prompt: str) -> dict:
    """The router's `cypress.plan/1` document for `prompt`, validated and
    bound to it by its SHA-256. Raises RouterFailed, silently for a router that
    failed (a non-zero exit, a timeout, no output, or a prompt the OS cannot
    pass as an argument: a NUL byte, over the argument limit), with one stderr
    line for output that is not such a document, and with the ENGINE_OLDER
    notice for an engine whose argparse rejects the option: exit 2 and
    `unrecognized arguments: --plan-json` on stderr (SPEC-0003
    ENGINE_OLDER_THAN_HOOK_IS_NAMED)."""
    try:
        out = subprocess.run(
            [sys.executable, str(LINT), "--plan-json=" + prompt],
            capture_output=True, timeout=ROUTER_TIMEOUT, cwd=str(ROOT),
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        raise RouterFailed() from None
    if out.returncode == 2 and b"unrecognized arguments: --plan-json" in out.stderr:
        raise RouterFailed(notice=ENGINE_OLDER)
    if out.returncode != 0 or not out.stdout.strip():
        raise RouterFailed()
    try:
        doc = json.loads(out.stdout)
    except (ValueError, RecursionError):
        raise RouterFailed("router output is not JSON; pointer line only") from None
    digest = hashlib.sha256(prompt.encode("utf-8", "surrogateescape")).hexdigest()
    problem = plan_problem(doc, digest)
    if problem:
        raise RouterFailed(f"router output is not a valid {PLAN_SCHEMA} document "
                           f"({problem}); pointer line only")
    return doc


def _is(value, pattern) -> bool:
    return isinstance(value, str) and bool(pattern.fullmatch(value))


def _member(value, allowed) -> bool:
    return isinstance(value, str) and value in allowed


def _node_ref(e, keys) -> bool:
    return (isinstance(e, dict) and set(e) == keys
            and _is(e["id"], NODE_ID) and _is(e["path"], RELATIVE_PATH))


def plan_problem(doc, digest: str):
    """Why `doc` is not a `cypress.plan/1` document bound to the prompt whose
    SHA-256 is `digest`, or None. The reason names the rule, never a value."""
    if not isinstance(doc, dict) or set(doc) != PLAN_KEYS:
        return "not a plan object"
    if doc["schema"] != PLAN_SCHEMA:
        return "unknown schema"
    if doc["task_sha256"] != digest:
        return "bound to another prompt"
    plant = doc["plant"]
    if plant is not None and not (isinstance(plant, dict) and set(plant) == set(PLANT_KEYS)
                                  and all(isinstance(v, str) for v in plant.values())):
        return "bad plant"
    notices = doc["notices"]
    if not (isinstance(notices, list) and all(
            isinstance(n, dict) and set(n) == {"code", "text"}
            and _member(n["code"], NOTICE_CODES) and isinstance(n["text"], str)
            for n in notices)):
        return "bad notices"
    if type(doc["est_tokens"]) is not int or doc["est_tokens"] < 0:
        return "bad est_tokens"
    load = doc["load"]
    if not (isinstance(load, list) and all(
            _node_ref(e, {"id", "path", "title", "how"}) and isinstance(e["title"], str)
            and isinstance(e["how"], dict) and set(e["how"]) == {"kind", "detail", "via"}
            and _member(e["how"]["kind"], HOW_KINDS)
            and (e["how"]["detail"] is None or isinstance(e["how"]["detail"], str))
            and (e["how"]["via"] is None or _is(e["how"]["via"], NODE_ID))
            for e in load)):
        return "bad load entry"
    if [e["id"] for e in load] != sorted(e["id"] for e in load):
        return "load not sorted by id"
    skip = doc["skip"]
    if not (isinstance(skip, list) and all(
            _node_ref(e, {"id", "path", "kind", "via"}) and _member(e["kind"], SKIP_GROUPS)
            and _is(e["via"], NODE_ID) for e in skip)):
        return "bad skip entry"
    return None


def how_suffix(how: dict):
    """The `<- …` the `--plan` grammar prints after a LOAD entry, or None."""
    kind, detail, via = how["kind"], how["detail"], how["via"]
    if kind == "inferred":
        return f'inferred from "{detail}"'
    if kind == "composed":
        return f'composed by {via} on "{detail}"'
    if kind == "named_path":
        return f'owns "{detail}"'
    if kind == "phrase":
        return f'phrase "{detail}"'
    return None


def suggest(doc: dict) -> Suggestion:
    """A validated document as the lines `--plan` prints for it: a LOAD entry
    is `<id> <path> | <title>[ <- <how>]`, the title without a leading
    `<slug> — ` its id already says; a skipped one is an `<id>=<path>`
    item of its group; the plant facts, when the document has them, are the
    one `plant:` line, in PLANT_KEYS order."""
    load = []
    for e in doc["load"]:
        title = e["title"].removeprefix(e["id"].rsplit(".", 1)[-1] + " \u2014 ")
        suffix = how_suffix(e["how"])
        load.append(Entry(e["id"], f"{e['id']} {e['path']} | {title}"
                          + (f" <- {suffix}" if suffix else "")))
    not_loaded = [Entry(e["id"], f"{e['id']}={e['path']}", SKIP_GROUPS[e["kind"]].format(e["via"]))
                  for e in doc["skip"]]
    plant = doc["plant"]
    return Suggestion([f"! {n['text']}" for n in doc["notices"]],
                      ["plant: " + " ".join(f"{k}={plant[k]}" for k in PLANT_KEYS)] if plant else [],
                      doc["est_tokens"], load, not_loaded)


def skip_block(entries: list) -> list:
    """The skip header and one line per group, its items in the given order;
    nothing when there are no entries."""
    groups = {}
    for e in entries:
        groups.setdefault(e.group, []).append(e.line)
    return ([SKIP_HEADER] if groups else []) + [g + " ".join(items) for g, items in groups.items()]


def full_text(suggestion: Suggestion) -> str:
    """Full mode: the pointer, the suggestion header, and the route exactly as
    `graph-lint.py --plan` prints it (SPEC-0003 ROUTE_FULL_TEXT_EQUALS_PLAN)."""
    return "\n".join([POINTER, "", SUGGESTION_HEADER, *suggestion.notices, *suggestion.plant,
                      LOAD_HEADER.format(len(suggestion.load), suggestion.est_tokens),
                      *(e.line for e in suggestion.load), *skip_block(suggestion.not_loaded)])


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
    """Reminder mode: the pointer, the router's notices, the reminder header,
    the entry lines of what is new this session, one `seen:` line naming the
    rest by id, and a skip block of only the ids not listed before. Each part
    after the header is dropped when empty; no `plant:` line, which the full
    injection left resident."""
    shown = set(ledger["surfaced"])
    new = [e.line for e in suggestion.load if e.node not in shown]
    known = [e.node for e in suggestion.load if e.node in shown]
    listed = shown | {e.node for e in suggestion.load} | set(ledger["peers_seen"])
    lines = [POINTER, *suggestion.notices,
             REMINDER_HEADER.format(len(suggestion.load), suggestion.est_tokens), *new]
    if known:
        lines.append(SEEN_LINE.format(", ".join(known)))
    lines += skip_block([e for e in suggestion.not_loaded if e.node not in listed])
    return "\n".join(lines)


# --- the session ledger ----------------------------------------------------
class LedgerUnusable(Exception):
    """A ledger or its directory that fails a §6 rule. The message is the
    stderr line, and never carries the raw session id."""


def valid_session_id(value) -> bool:
    return isinstance(value, str) and bool(SESSION_ID.fullmatch(value))


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
                or not all(isinstance(i, str) and NODE_ID.fullmatch(i) for i in ids)
                or ids != sorted(set(ids))):
            return f"bad {key}"
    reset = doc["last_reset"]
    if reset is not None and not (
            isinstance(reset, dict) and set(reset) == {"source", "at"}
            and isinstance(reset["source"], str) and RESET_SOURCE.fullmatch(reset["source"])
            and isinstance(reset["at"], str) and ISO_UTC.fullmatch(reset["at"])):
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
        raise LedgerUnusable(f"{top_name}/ unusable ({reason(e)})")
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
        raise LedgerUnusable(f"{where}/ unusable ({reason(e)})")
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
    except OSError as e:
        os.close(fd)
        raise LedgerUnusable(f"{where}/ unusable ({reason(e)})") from None
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
        raise LedgerUnusable(f"session ledger unusable ({reason(e)})")
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
    removed and the old ledger, if any, stays as it was.

    A document over LEDGER_MAX_BYTES is refused before any file is made:
    SURFACED_MAX ids at the pattern's full length serialize past it, and
    read_ledger would refuse the file as oversized on the next prompt."""
    problem = ledger_problem(doc, doc.get("session_id"))
    if problem:
        raise LedgerUnusable(f"refusing to write a ledger that breaks its schema ({problem})")
    data = (json.dumps(doc) + "\n").encode()
    if len(data) > LEDGER_MAX_BYTES:
        raise LedgerUnusable(f"refusing to write a ledger of {len(data)} B, over "
                             f"LEDGER_MAX_BYTES; not written")
    tmp = TEMP_PREFIX + secrets.token_hex(8)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dir_fd)
    try:
        try:
            os.write(fd, data)
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
        for entry in itertools.islice(entries, GC_SCAN_MAX):
            name = entry.name
            is_ledger = name.endswith(".json") and bool(SESSION_ID.fullmatch(name[:-5]))
            if name == keep or not (is_ledger or TEMP_NAME.fullmatch(name)):
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
    when a ledger records it. Garbage collection is housekeeping, not part of
    that record: its failure is the note, and the write still runs."""
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
            try:
                collect_garbage(dir_fd, session_id + ".json", now)
            except OSError as e:
                note = f"session ledger GC skipped ({reason(e)})"
        write_ledger(dir_fd, ledger_doc(session_id, count, surfaced, peers, last_reset))
    finally:
        os.close(dir_fd)
    return text, note


def reset_ledger(session_id, source) -> None:
    """Record a session start in this session's ledger: count 0, no surfaced
    ids, no peers, and `last_reset`. The next routed prompt is therefore full.

    Called by status-hook.py on every SessionStart source, so the ledger keeps
    one owner. Writes nothing when there is no session id, no graph, or no
    ledger for this session. Raises LedgerUnusable for a refused id, an
    unusable directory, or a ledger that cannot be stat'ed; when the write
    fails the ledger is unlinked instead, and it still raises, since the caller
    owes a stderr line either way. Every message is safe to print as it is.
    """
    if session_id is None or LINT is None:
        return
    if not valid_session_id(session_id):
        raise LedgerUnusable("session_id refused (not a safe filename); no reset")
    if not (isinstance(source, str) and RESET_SOURCE.fullmatch(source)):
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
        except OSError as e:
            raise LedgerUnusable(f"session ledger unusable ({reason(e)}); no reset") from None
        at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            write_ledger(dir_fd, ledger_doc(session_id, 0, (), (), {"source": source, "at": at}))
        except OSError as e:
            try:
                os.unlink(name, dir_fd=dir_fd)
            except OSError as gone:
                raise LedgerUnusable(f"reset not written ({reason(e)}) and the stale "
                                     f"ledger could not be removed ({reason(gone)})") from None
            raise LedgerUnusable(f"reset not written ({reason(e)}); ledger removed instead") from None
    finally:
        os.close(dir_fd)


# --- the hook ----------------------------------------------------------------
ARGV_OPTIONS = ("prompt", "session-id", "depth", "origin")


class EnvelopeRefused(Exception):
    """An argv element outside the §6 envelope. The message names it."""


def argv_envelope(args) -> dict:
    """The argv envelope as {option: value}: one `--name=value` element per
    option, each name in ARGV_OPTIONS."""
    options = {}
    for arg in args:
        name, eq, value = arg.partition("=")
        if not (eq and name.startswith("--") and name[2:] in ARGV_OPTIONS):
            raise EnvelopeRefused(name[:64])
        options[name[2:]] = value
    return options


def routed(prompt: str, depth, origin) -> bool:
    """False for a turn that gets nothing at all: a trivial prompt, a child
    session, or a turn a person did not type. An unreadable depth or origin is
    routed (I-1)."""
    if prompt.lower() in TRIVIAL or len(prompt) < 8:
        return False
    if _is(depth, CHILD_DEPTH):
        return False
    if _is(origin, ORIGIN) and origin != "human":
        return False
    return not prompt.startswith(NON_HUMAN_MARKERS)


def main() -> int:
    args = sys.argv[1:]
    depth = origin = None
    if any(a.startswith("--") for a in args):     # the argv envelope; stdin is not read
        try:
            options = argv_envelope(args)
        except EnvelopeRefused as e:
            warn(f"option {e} is outside the argv envelope; nothing injected")
            return 0
        prompt, session_id = options.get("prompt", ""), options.get("session-id")
        depth, origin = options.get("depth"), options.get("origin")
        event = "UserPromptSubmit"
    else:
        try:
            data = json.load(sys.stdin)
        except RecursionError:                    # nested past the parser: no prompt to route
            warn("stdin nested past the JSON parser's limit; pointer line only")
            if LINT is not None:
                emit(POINTER, "UserPromptSubmit")
            return 0
        except ValueError:                        # not JSON, empty stdin included: silent
            return 0
        if not isinstance(data, dict):
            return 0
        prompt = data.get("prompt") or data.get("initialPrompt") or ""
        if not isinstance(prompt, str):
            return 0
        session_id = data.get("session_id")      # the exact key only; null is absent
        event = data.get("hook_event_name") or data.get("hookEventName") or "UserPromptSubmit"
    prompt = prompt.strip()

    if not routed(prompt, depth, origin):
        return 0

    if LINT is None:
        emit(NO_GRAPH, event)
        return 0

    try:
        suggestion = suggest(run_router(prompt))
    except RouterFailed as e:
        if str(e):
            warn(str(e))
        emit("\n".join([POINTER, e.notice]) if e.notice else POINTER, event)
        return 0
    full = full_text(suggestion)

    text, note = full, None
    if session_id is not None:
        if not valid_session_id(session_id):
            note = "session_id refused (not a safe filename); full injection"
        else:
            try:
                text, note = inject_with_ledger(session_id, suggestion, full)
            except LedgerUnusable as e:
                text, note = full, f"{e}; full injection"
            except OSError as e:
                text, note = full, f"session ledger not written ({reason(e)}); full injection"
            except Exception as e:                # noqa: BLE001 — fail open to the full text
                text, note = full, f"session ledger step failed ({type(e).__name__}); full injection"
    if note:
        warn(note)
    emit(text, event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
