#!/usr/bin/env python3
"""bound-hook.py — a PreToolUse hook on the Bash tool that enforces bounded
execution.

Installed to `.claude/bound-hook.py` and wired in `.claude/settings.json`
under hooks.PreToolUse with `"matcher": "Bash"`, this runs before every
shell call. The host passes `{"tool_name": "...", "tool_input": {"command":
"..."}}` on stdin. A command that is blocking-prone — service control,
process signalling, package managers, installers, builds, followers — and
carries neither an explicit bound nor a detached launch is refused: the
reason and both accepted forms go to stderr and the hook exits 2, which
blocks the call and hands the model the reason.

This is a GUARD, so unlike the context-injecting hooks it is wired without
`|| true`: a hook that cannot block is not a guard. The asymmetry is paid
for on the other side — the script itself can only ever exit 0 or 2, and
every failure path inside it exits 0 with one line on stderr. A bug here
degrades to no guard; it can never brick a session by blocking everything.

Exit 0 = allow (also: not Bash, no command, unparseable stdin, internal
error). Exit 2 = block, reason on stderr.
"""

import json
import re
import sys

# ---------------------------------------------------------------------------
# Blocking-prone commands. Each entry is
#   (name, match, exempt, boundable)
#     match      regex tried at a command-word position, already past any path
#                prefix — so `./install.sh` is tested as `install.sh`
#     exempt     regex tried on the whole command from that position; when it
#                matches, this occurrence is not a hit at all (the flag that
#                makes the command non-blocking is already there)
#     boundable  True when a bound or a detached launch makes the call
#                acceptable. False for the pattern-killers: their hazard is
#                signalling the wrong process — including the shell issuing
#                the kill — and no bound repairs that.
# Extending this list is a one-line change.
# ---------------------------------------------------------------------------
BLOCKING_PRONE = [
    # service control: waits on the unit manager, which waits on the unit
    ("systemctl", r"systemctl\b",
     r"systemctl\b(?:\s+--?\S+)*\s+(?:status|show|is-active|is-enabled|is-failed|is-system-running|cat|list-\S+|get-default|show-environment)\b",
     True),
    ("service", r"service\s", r"service\s+\S+\s+status\b", True),
    # log followers: by construction they never return
    ("journalctl -f", r"journalctl\b[^;|&]*-f\b", None, True),
    ("tail -f", r"tail\b[^;|&]*-f\b", None, True),
    # pattern killers: the pattern can match the shell issuing the kill
    ("pkill", r"pkill\b", None, False),
    ("killall", r"killall\b", None, False),
    # signalling is by recorded pid or by a literal pid; a pattern is not a pid
    ("kill -", r"kill\s+-",
     r"kill\s+-\S+\s+(?:\d+|\$\(\s*cat\s+[^)]*pid[^)]*\)|`\s*cat\s+[^`]*pid[^`]*`)",
     False),
    # privilege escalation prompts for a password and then waits forever
    ("sudo", r"sudo\b", r"sudo\s+-n\b", True),
    # package managers: network, locks, and interactive confirmations
    ("apt", r"apt(?:-get)?(?![\w-])", None, True),   # not apt-cache / apt-mark / apt-key
    ("pacman", r"pacman\b", None, True),
    ("yay", r"yay\b", None, True),
    ("pip install", r"pip3?\s+install\b", None, True),
    ("npm install", r"npm\s+install\b", None, True),
    ("npm ci", r"npm\s+ci\b", None, True),
    # containers: an attached run or an interactive exec holds the terminal
    ("docker run", r"docker\s+run\b",
     r"docker\s+run\b[^;|&]*\s(?:-d\b|--detach\b)", True),
    ("docker exec -it", r"docker\s+exec\b[^;|&]*-it\b", None, True),
    # remote shells: without BatchMode they can sit on a prompt
    ("ssh", r"ssh\s", r"ssh\b[^;|&]*-o\s*BatchMode=yes", True),
    # installers and builds: unbounded by nature, and the ones most often left
    # to hang because "it usually finishes"
    ("install.sh", r"install\.sh\b", None, True),
    ("make", r"make\b", r"make\b[^;|&]*\s(?:-n|--dry-run|--just-print|-q|--question)\b", True),
    ("cargo build", r"cargo\s+build\b", None, True),
    ("cmake --build", r"cmake\s+--build\b", None, True),
    # a pipe into a shell runs whatever arrived: the installer case in disguise
    ("pipe to shell", r"(?:bash|sh|zsh|dash)(?:\s+-\S+)*\s*$", None, True),
]

# Where a new command word can begin: after a separator, or after a prefix word.
SEPARATOR = re.compile(r"\|\||&&|\$\(|[;\n|&(){}`]")

# Words that stand in front of the real command without being it. `timeout`
# is one of them, and seeing it here is what marks the position as bounded.
PREFIX_WORD = re.compile(
    r"""(?:
        [A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|\S*)          # VAR=value
      | timeout(?:\s+--preserve-status)?
               (?:\s+-k\s*[0-9.]+[smhd]?)?
               (?:\s+-s\s*\S+)?\s+[0-9.]+[smhd]?                # timeout [-k N] N
      | nice(?:\s+-n\s*-?\d+)?
      | ionice(?:\s+-c\s*\d+)?
      | sudo(?:\s+-n)?
      | env | command | exec | setsid | nohup | time | bash | sh
      | then | else | do
    )(?=\s)""",
    re.X,
)

PATH_PREFIX = re.compile(r"(?:[A-Za-z0-9_.~${}+-]*/)+")

# Detached launch: hangup escaped, backgrounded, output durable, pid recorded.
BACKGROUND = re.compile(r"(?<![>&])&(?!&)")
REDIRECT = re.compile(r">>?\s*(?![&\s])[^\s;|&]+")
PID_RECORDED = re.compile(r"\$!\s*>>?\s*\S+|--pid(?:file)?\b|\bpid[-_]?file\b")


# `bash -c "..."`, `sh -c '...'` and `eval "..."` run their payload: the payload
# is inspected in place of the wrapper, so a bound on the wrapper still counts.
WRAPPER = re.compile(
    r"""\b(?:bash|sh|zsh|dash)\s+(?:-[A-Za-z]+\s+)*-c\s+|\beval\s+"""
)
QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'')


def unwrap(cmd, depth=0):
    """Replace every shell wrapper plus its quoted payload with the payload."""
    if depth > 4:
        return cmd
    out, pos, changed = [], 0, False
    while True:
        m = WRAPPER.search(cmd, pos)
        if not m:
            out.append(cmd[pos:])
            break
        q = QUOTED.match(cmd, m.end())
        if not q:
            out.append(cmd[pos:m.end()])
            pos = m.end()
            continue
        body = q.group(0)[1:-1]
        if q.group(0)[0] == '"':
            body = re.sub(r"\\(.)", r"\1", body)
        out.append(cmd[pos:m.start()])
        out.append(body)
        pos = q.end()
        changed = True
    new = "".join(out)
    return unwrap(new, depth + 1) if changed else new


def masked(cmd):
    """The command with every quoted string blanked to spaces, same length, so
    separators and patterns are read only outside quotes."""
    return QUOTED.sub(lambda m: " " * len(m.group(0)), cmd)


def command_positions(cmd):
    """Every offset where a command word starts, with whether a bound is in
    scope at that offset. A bound is in scope when a `timeout` prefix word was
    consumed earlier in the same segment."""
    starts = [0] + [m.end() for m in SEPARATOR.finditer(cmd)]
    found = {}
    for start in starts:
        pos, bounded = start, False
        while True:
            while pos < len(cmd) and cmd[pos].isspace():
                pos += 1
            found[pos] = found.get(pos, False) or bounded
            m = PREFIX_WORD.match(cmd, pos)
            if not m or m.end() == pos:
                break
            if cmd[pos:m.end()].startswith("timeout"):
                bounded = True
            pos = m.end()
    return sorted(found.items())


def is_detached(cmd):
    return bool(
        ("setsid" in cmd or "nohup" in cmd)
        and BACKGROUND.search(cmd)
        and REDIRECT.search(cmd)
        and PID_RECORDED.search(cmd)
    )


def first_hit(cmd):
    """The earliest blocking-prone occurrence that nothing excuses, as
    (offset, name, boundable). Scans the quote-masked text."""
    text = masked(cmd)
    for pos, bounded in command_positions(text):
        offsets = [pos]
        p = PATH_PREFIX.match(text, pos)
        if p and p.end() > pos:
            offsets.append(p.end())
        for off in offsets:
            tail = text[off:]
            for name, match, exempt, boundable in BLOCKING_PRONE:
                if not re.match(match, tail):
                    continue
                if name == "pipe to shell" and not text[:pos].rstrip().endswith("|"):
                    continue
                if exempt and re.match(exempt, tail):
                    continue
                if boundable and bounded:
                    continue
                return off, name, boundable
    return None


def segment_of(cmd, offset):
    """The offending command on its own, without its neighbours."""
    text = masked(cmd)
    start = 0
    for m in SEPARATOR.finditer(text):
        if m.end() <= offset:
            start = m.end()
    end = len(cmd)
    for m in SEPARATOR.finditer(text):
        if m.start() > offset:
            end = m.start()
            break
    return cmd[start:end].strip()


def reason(cmd, offset, name, boundable):
    seg = segment_of(cmd, offset) or cmd.strip()
    tag = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") or "job"
    lines = [
        "[bound-hook] BLOCKED: `%s` is blocking-prone (%s) and carries no bound."
        % (seg, name),
        "Every foreground command carries an explicit bound; work that may exceed it "
        "is launched detached, logged and pid-recorded. Use one of these two forms:",
        "  (a) bounded:  timeout 30 %s" % seg,
        "  (b) detached: setsid nohup %s > %s.log 2>&1 & echo $! > %s.pid"
        % (seg, tag, tag),
    ]
    if not boundable:
        lines[1] = (
            "A process is stopped by its recorded pid or process group, never by a "
            "pattern that can match the shell issuing the kill. Use one of these forms:"
        )
        lines[2] = "  (a) by recorded pid:  kill -TERM $(cat %s.pid)" % tag
        lines[3] = "  (b) by literal pid:   kill -TERM <pid>   (after timeout 5 ...)"
    return "\n".join(lines)


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return 0
    except Exception:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        return 0
    if is_detached(cmd):
        cmd = unwrap(cmd); hit = first_hit(cmd)
        # A detached launch excuses the boundable patterns only.
        if hit is None or hit[2]:
            return 0
    cmd = unwrap(cmd); hit = first_hit(cmd)
    if hit is None:
        return 0
    sys.stderr.write(reason(cmd, *hit) + "\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # a guard bug must never brick a session
        sys.stderr.write("[bound-hook] internal error, allowing: %s\n" % exc)
        sys.exit(0)
