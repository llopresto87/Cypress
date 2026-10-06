# Tool: destructive-command-guard-hook

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable tool: the hook below runs as-is on an
> agent host with a pre-tool hook surface, and a plant adjusts two lists at its
> top.

## 0. Identity

- **Category:** ops
- **Name:** destructive-command-guard-hook
- **Language / runtime:** python3, **stdlib only** (`json`, `re`, `fnmatch`)
- **Stability:** **portable**. The command splitting, the three tiers, the
  exit-code contract and the self-test are complete. A plant edits
  `GOVERNANCE_GLOBS` and chooses `PROFILE`; the wiring line is per host (§2).

## 1. What it does

A pre-tool hook that runs before every shell call and every file edit an agent
makes, and sorts the call into one of three tiers:

1. **Deny** irreversible local destruction: `git reset --hard`, a
   discarding `git checkout` or `git restore`, `git clean -f`,
   `git stash drop` or `clear`, a recursive delete of `/`, `~`, `$HOME`, `.`,
   `..` or `*`, a filesystem format (`mkfs*`, `wipefs`, `shred`), and `dd`
   writing to a raw device.
2. **Ask** before a version-control change and before any other recursive
   delete. Which version-control verbs ask depends on the profile (§3).
3. **Ask** before an edit to a governance file: instruction files, agent
   charters, protocol and method nodes, hook wiring.

Everything else passes with no decision, so the host's own permission rules
still apply.

It exists because written rules get skipped. The kernel's boundary (deleting,
force-pushing, dropping and rotating each wait for a confirmation that names
the resource) and `method.vcs-posture` §2 (publishing is a separate
authorization) are advisory text. This hook makes the most damaging cases of
both a decision the host enforces. Deleting files is covered only for a
recursive `rm`: `rm -f file`, `git rm -f` and `find -delete` pass with no
decision, and the kernel's rule for them stays advisory. It is the destructive-command sibling of
the seed's `bound-hook.py`, which refuses blocking-prone commands, and it uses
the same exit-code contract.

**When not to use it.** It is not a sandbox. It reads command words, so a
command reached by indirection (a script that runs `git reset --hard`, an
alias, a `make` target) passes. Use it as a guard against the common direct
case, together with the host's own deny rules and a sandbox where the risk
calls for one.

## 2. Interface & invocation

```sh
python3 destructive-guard.py              # reads one hook payload on stdin
python3 destructive-guard.py --self-test  # runs the fixture self-test
```

Wiring on a host that uses the `PreToolUse` contract (one entry for the shell
tool, one for the editing tools; the matcher is a regular expression over the
tool name):

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command",
                  "command": "python3 \"${CLAUDE_PROJECT_DIR:-$PWD}/.claude/destructive-guard.py\""}]},
      {"matcher": "Edit|Write|MultiEdit|NotebookEdit",
       "hooks": [{"type": "command",
                  "command": "python3 \"${CLAUDE_PROJECT_DIR:-$PWD}/.claude/destructive-guard.py\""}]}
    ]
  }
}
```

The script path goes through `${CLAUDE_PROJECT_DIR}`, the same form the
seed's `bound-hook.py` wiring uses. Upstream says hook handlers "run in the
current directory", and that directory follows the agent's `cd`. A relative
path such as `python3 .claude/destructive-guard.py` stops resolving after
the agent runs `cd src`, and §5 says what that does. `${CLAUDE_PROJECT_DIR}`
is the project root where the session started. The `$PWD` fallback serves a
host that does not set it.

- **Inputs:** the host's hook payload on stdin. The hook reads only
  `tool_name`, `tool_input.command` (shell), `tool_input.file_path` or
  `tool_input.notebook_path` (edits) and `cwd`, plus the
  `CLAUDE_PROJECT_DIR` environment variable, which upstream exports to the
  hook process.
- **Outputs and exit codes:**
  - deny: one line on stderr naming the rule and the offending command, exit 2;
  - ask: one JSON object on stdout,
    `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
    "permissionDecision": "ask", "permissionDecisionReason": "..."}}`,
    exit 0;
  - no decision: nothing on stdout, exit 0.
  - every internal error, unreadable stdin, and a tool the hook does not know:
    exit 0 with no decision.
- **Preconditions:** python3 on the host; the hook wired **without** `|| true`
  (a hook that cannot block is not a guard).

## 3. Approach / algorithm

### Read the command, never the payload

The hook takes `tool_input.command` and nothing else from a shell call. The
naive version lowercases the whole payload and greps it. It then matches
`git commit` or `rm -rf /` inside the **content of a file being written** (a
note, a runbook, this page), and denies a harmless edit. False positives like
that teach people to remove the guard. For edits, the hook reads only the
target path.

### Split the command into simple commands

1. Unwrap `bash -c "..."`, `sh -c '...'` and `eval "..."`, so the payload is
   checked in place of the wrapper. The `-c` may sit inside a flag cluster
   (`bash -lc`, `sh -ec`) or after `-o <option>`.
2. Blank every quoted string to spaces. A pattern inside an argument
   (`echo "git reset --hard"`, `grep 'rm -rf /' notes.md`) is then not a
   command.
3. Split at `;`, `&&`, `||`, `|`, `&`, newlines, `$(`, backticks and braces.
4. Strip prefix words from each piece: `VAR=value`, `sudo` and `doas` and
   `env` with their flags, `command`, `exec`, `nohup`, `setsid`, `time`,
   `nice`, `timeout N`, `xargs`. A flag that takes an argument is stripped
   with it (`sudo -u root`, `env -u NAME`); otherwise `root` would be read as
   the command word and the real command would pass.
5. For `git`, skip its global options (`-C <dir>`, `-c <k=v>`, `--git-dir`,
   `--work-tree`, `--no-pager`) to reach the subcommand.

Deny rules run over every piece first, then ask rules. The first hit decides,
so a `deny` anywhere in a chain wins over an `ask`.

### Precise targets, not prefixes

- A recursive `rm` is **denied** only when a target is exactly `/`, `/*`, `~`,
  `~/`, `$HOME`, `.`, `..` or `*`. A quoted target is checked on the raw
  command, because the masking blanks it: `"$HOME"`, `"/"` and `'.'` are
  denied, while a quoted `'~'` or `"*"` names a literal file and only asks.
  The naive pattern `rm -rf /` also matches
  `rm -rf /tmp/build`. Every other recursive delete **asks**, because the
  kernel boundary wants the resource named, not refused.
- `dd` is denied only with `of=/dev/...`. The naive `dd if=` matches every
  `dd`, including one that writes an image file.
- `git restore` is denied without `--staged` (it discards the working tree),
  and passes with it (it only unstages).

### Two profiles for version control

- **`posture` (the default)** asks before the verbs that publish, rewrite or
  discard history: `push`, `pull`, `rebase`, `reset`, `merge`, `tag`
  (creating or deleting), `revert`, `cherry-pick`, `update-ref`,
  `filter-branch`, `filter-repo`, `replace`, `worktree`, `gc`, `prune`,
  `reflog expire|delete`, `commit --amend`, a branch delete, rename or force,
  and `stash` (push or pop). It also asks before the publishing acts a shell
  command can do outside git: opening or merging a pull request
  (`gh pr create|merge`, `glab mr create|merge`) and creating or deleting a
  release (`gh release create|delete`). A local `add`, `commit` or `switch`
  passes. This
  follows `method.vcs-posture` §1: the local commit is the resting state of
  work, and an agent commits at every green increment.
- **`strict`** asks before every mutating verb, `add` and `commit` included,
  and before the same publishing acts. It fits a plant whose owner has ruled
  that agents never commit. Under
  `strict`, an unattended run cannot commit at all (see §5, headless runs).

Read-only forms pass under both profiles: `status`, `log`, `diff`, `branch`
and `tag` with no arguments or with `--list`, `stash list` and `stash show`,
`worktree list`, and `reflog` with no subcommand.

### The exit-code contract

- **Deny with exit 2 and the reason on stderr.** On this host contract, exit 2
  blocks the call whatever stdout holds, and the model reads stderr as the
  reason. Upstream states that a hook "that blocks by exiting 2 routes the
  same way as `deny`: Claude sees the stderr message as the denial reason".
  The naive version printed a JSON `deny` and also exited 2, with nothing on
  stderr. Upstream records that older releases handled JSON on exit 2
  differently. Reason-on-stderr works the same on every release.
- **Ask with exit 0 and JSON on stdout.** `"ask"` shows the user a permission
  prompt that carries `permissionDecisionReason`. Exit 0 is the code upstream
  names for structured JSON output.
- **Fail open on the hook's own errors.** Every internal error exits 0 and
  writes one line to stderr. Upstream: stderr from a hook that exits 0 goes to
  the debug log only. A bug inside the script therefore degrades to "no
  guard", and it cannot block every call. This is the same trade
  `bound-hook.py` makes. A script that never starts is a different case, and
  one of its forms does block every call (§5).

```python
#!/usr/bin/env python3
"""destructive-guard: a PreToolUse hook that stops irreversible commands and
asks before version-control and governance changes.

Wired in the host's settings under hooks.PreToolUse, once with the matcher for
the shell tool and once for the file-editing tools, WITHOUT `|| true`: a hook
that cannot block is not a guard. The host passes
{"tool_name": ..., "tool_input": {...}} on stdin.

Three tiers, checked in this order:
  deny  irreversible local destruction          -> reason on stderr, exit 2
  ask   a version-control change (PROFILE)      -> JSON "ask" on stdout, exit 0
  ask   an edit to a governance file            -> JSON "ask" on stdout, exit 0
Anything else, and every internal error, exits 0 with no decision, so the
host's normal permission flow applies. A bug here degrades to no guard; it
can never block every call.

Only tool_input.command (shell) and tool_input.file_path / notebook_path
(edits) are read, never the whole payload: the text of a file being written
is data, not a command.

  destructive-guard.py              read one hook payload on stdin
  destructive-guard.py --self-test  run the fixture self-test
Stdlib only.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys

SHELL_TOOLS = {"Bash"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

# "posture": ask before VCS changes that publish, rewrite or discard history;
#            a local add/commit stays free (a local commit is the resting state
#            of work). "strict": ask before every VCS mutation.
PROFILE = "posture"

# Governance files: instructions, charters, hook wiring. Globs are matched
# against the path relative to the project root and against its basename.
GOVERNANCE_GLOBS = [
    "AGENTS.md", "CLAUDE.md", "GEMINI.md",
    ".claude/settings.json", ".claude/settings.local.json",
    ".claude/agents/*", ".claude/commands/*", ".claude/*.py",
    "docs/graph/agents/*", "docs/graph/protocols/*", "docs/graph/method/*",
    ".github/copilot-instructions.md", ".github/instructions/*",
    ".github/agents/*", ".github/hooks/*",
]

VCS_MUTATING = {"add", "am", "apply", "branch", "checkout", "cherry-pick",
                "clean", "commit", "merge", "mv", "pull", "push", "rebase",
                "reset", "restore", "revert", "rm", "stash", "switch", "tag",
                "update-ref", "filter-branch", "filter-repo", "replace",
                "notes", "worktree", "gc", "prune", "reflog"}
VCS_POSTURE = {"push", "pull", "rebase", "reset", "merge", "tag", "revert",
               "cherry-pick", "update-ref", "filter-branch", "filter-repo",
               "replace", "worktree", "gc", "prune", "reflog"}

# Publishing acts a shell command can do outside git (vcs-posture §2):
# opening or merging a pull/merge request, creating or deleting a release.
PUBLISH = re.compile(r"(?:\S*/)?(?:gh|glab)\s+(pr|mr|release)\s+(create|merge|delete)\b")
SEPARATOR = re.compile(r"\|\||&&|\$\(|[;\n|&(){}`]")
QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'')
# `-c` may sit inside a flag cluster: `bash -lc '...'`, `sh -ec '...'`;
# `-o pipefail` before it is skipped.
WRAPPER = re.compile(r"\b(?:bash|sh|zsh|dash)\s+(?:--?[A-Za-z][A-Za-z-]*\s+|[-+]o\s+\S+\s+)*"
                     r"-[A-Za-z]*c[A-Za-z]*\s+|\beval\s+")
# sudo, doas and env options that take an argument are consumed with it, so
# `sudo -u root rm -rf /` reaches `rm`, not `root`.
SUDO_OPTS = (r"(?:\s+(?:-[A-Za-z]*[ugphCDRTU]\s*[^\s-]\S*|--[a-z-]+=\S+|"
             r"--(?:user|group|host|prompt|chdir|chroot|other-user|close-from|"
             r"command-timeout)\s+\S+|-[A-Za-z]+|--[a-z-]+))*")
PREFIX = re.compile(
    r"(?:[A-Za-z_][A-Za-z0-9_]*=\S*|sudo" + SUDO_OPTS + r"|doas(?:\s+(?:-[uC]\s*\S+|-[A-Za-z]+))*|"
    r"env(?:\s+(?:-[uCS]\s*\S+|--(?:unset|chdir|split-string)(?:=|\s+)\S+|-[A-Za-z0-9]*|--[a-z-]+))*|"
    r"command|exec|nohup|"
    r"setsid|time|nice(?:\s+-n\s*-?\d+)?|timeout(?:\s+-\S+)*\s+[0-9.]+[smhd]?|"
    r"xargs(?:\s+-\S+)*|then|else|do)\s+")
GIT_GLOBAL = re.compile(r"(?:-C\s+\S+|-c\s+\S+|--git-dir(?:=|\s+)\S+|"
                        r"--work-tree(?:=|\s+)\S+|--no-pager|-P)\s+")


def unwrap(cmd: str, depth: int = 0) -> str:
    """Replace `bash -c "..."` and `eval "..."` with their payload."""
    if depth > 4:
        return cmd
    m = WRAPPER.search(cmd)
    if not m:
        return cmd
    q = QUOTED.match(cmd, m.end())
    if not q:
        return cmd
    body = q.group(0)[1:-1]
    return unwrap(cmd[:m.start()] + " ; " + body + " ; " + cmd[q.end():], depth + 1)


def segments(cmd: str):
    """Each simple command, with quoted strings blanked to spaces so that a
    pattern inside an argument (`echo "git reset --hard"`) is not a command."""
    masked = QUOTED.sub(lambda m: " " * len(m.group(0)), cmd)
    starts = [0] + [m.end() for m in SEPARATOR.finditer(masked)]
    ends = [m.start() for m in SEPARATOR.finditer(masked)] + [len(masked)]
    for s, e in zip(starts, ends):
        seg = masked[s:e].strip()
        while True:
            m = PREFIX.match(seg)
            if not m:
                break
            seg = seg[m.end():]
        if seg:
            yield seg, cmd[s:e].strip()


def git_words(seg: str):
    """(subcommand, rest) for a git invocation, past git's global options."""
    m = re.match(r"(?:\S*/)?git\s+", seg)
    if not m:
        return None
    rest = seg[m.end():]
    while True:
        g = GIT_GLOBAL.match(rest)
        if not g:
            break
        rest = rest[g.end():]
    parts = rest.split(None, 1)
    return (parts[0], parts[1] if len(parts) > 1 else "") if parts else None


# A quoted target is blanked by the masking, so these are read from the raw
# segment. Double quotes expand `$HOME`; neither quote expands `~` or `*`.
QUOTED_DENY_TARGET = re.compile(r'"(?:/|\$HOME/?|\$\{HOME\}/?|\.{1,2}/?)"|\'(?:/|\.{1,2}/?)\'')


def deny_reason(seg: str, raw: str = ""):
    words = seg.split()
    name = words[0].rsplit("/", 1)[-1]
    gw = git_words(seg)
    if gw:
        sub, rest = gw
        if sub == "reset" and re.search(r"(?:^|\s)--hard\b", rest):
            return "git reset --hard discards uncommitted work"
        if sub == "checkout" and re.search(r"(?:^|\s)(?:--(?:\s|$)|\.(?:\s|$)|-f\b|--force\b)", rest):
            return "git checkout -- / . / --force discards uncommitted work"
        if sub == "restore" and not re.search(r"(?:^|\s)(?:--staged|-S)\b", rest):
            return "git restore without --staged discards uncommitted work"
        if sub == "clean" and re.search(r"(?:^|\s)(?:-[A-Za-z]*f|--force)", rest):
            return "git clean -f deletes untracked files"
        if sub == "stash" and re.match(r"(?:drop|clear)\b", rest):
            return "git stash drop/clear deletes stashed work"
        return None
    if name == "rm" and any(re.fullmatch(r"-[A-Za-z]*[rR][A-Za-z]*|--recursive", w) for w in words[1:]):
        targets = [w for w in words[1:] if not w.startswith("-")]
        for t in targets:
            if re.fullmatch(r"/|/\*|~/?\*?|\$HOME/?\*?|\$\{HOME\}/?\*?|\.{1,2}/?|\*", t):
                return f"recursive delete of {t!r}"
        for q in QUOTED_DENY_TARGET.finditer(raw):
            if re.match(r"\s|$", raw[q.end():q.end() + 1] or " ") and re.search(r"\s$", raw[:q.start()]):
                return f"recursive delete of {q.group(0)}"
        return None
    if name.startswith("mkfs") or name in {"wipefs", "shred"}:
        return f"{name} destroys data on its target"
    if name == "dd" and re.search(r"(?:^|\s)of=/dev/", seg):
        return "dd writes to a raw device"
    return None


def ask_reason(seg: str):
    gw = git_words(seg)
    if gw:
        sub, rest = gw
        if sub not in VCS_MUTATING:
            return None
        if sub == "branch" and not re.search(r"(?:^|\s)-(?:[dDmMcCf]|-delete|-move|-copy|-force)\b", rest):
            return None                       # listing branches reads only
        if sub == "stash" and re.match(r"(?:list|show)\b", rest):
            return None
        if sub == "tag" and not rest.strip() or sub == "tag" and re.match(r"(?:-l|--list)\b", rest):
            return None                       # listing tags reads only
        if sub == "worktree" and re.match(r"list\b", rest):
            return None
        if sub == "reflog" and not re.match(r"(?:expire|delete)\b", rest):
            return None
        if PROFILE == "strict" or sub in VCS_POSTURE:
            return f"version-control change: git {sub}"
        if sub == "commit" and re.search(r"(?:^|\s)--amend\b", rest):
            return "version-control change: git commit --amend rewrites a commit"
        if sub == "branch":
            return "version-control change: git branch delete/rename/force"
        if sub == "stash":
            return "version-control change: git stash"
        return None
    name = seg.split()[0].rsplit("/", 1)[-1]
    pub = PUBLISH.match(seg)
    if pub:                                   # publishing: both profiles ask
        return f"publishing: {name} {pub.group(1)} {pub.group(2)}"
    if name == "rm" and any(re.fullmatch(r"-[A-Za-z]*[rR][A-Za-z]*|--recursive", w) for w in seg.split()[1:]):
        return "recursive delete: confirm the resource by name"
    return None


def governance_hit(path: str, root: str):
    """Match the target against GOVERNANCE_GLOBS. The payload's `cwd` follows
    the agent's `cd`, so a path made relative to it misses
    `.claude/settings.json` once the agent works in a subdirectory. The path
    is therefore made relative to the project root (CLAUDE_PROJECT_DIR, else
    cwd), and every trailing part of it is matched as well, so a root the hook
    was not told still finds `docs/graph/agents/x.md` under `/w/sub/`."""
    if not path:
        return None
    rel = path
    if root and path.startswith(root.rstrip("/") + "/"):
        rel = path[len(root.rstrip("/")) + 1:]
    parts = path.strip("/").split("/")
    tails = {rel} | {"/".join(parts[i:]) for i in range(len(parts))}
    for g in GOVERNANCE_GLOBS:
        if any(fnmatch.fnmatch(t, g) for t in tails):
            return f"governance file edit: {rel}"
    return None


def decide(payload: dict, project_dir: str | None = None):
    """('deny'|'ask'|None, reason)."""
    if project_dir is None:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    tool = payload.get("tool_name")
    ti = payload.get("tool_input") or {}
    if tool in SHELL_TOOLS:
        cmd = ti.get("command")
        if not isinstance(cmd, str) or not cmd.strip():
            return None, ""
        segs = list(segments(unwrap(cmd)))
        for seg, raw in segs:
            r = deny_reason(seg, raw)
            if r:
                return "deny", f"{r}: `{raw}`"
        for seg, raw in segs:
            r = ask_reason(seg)
            if r:
                return "ask", f"{r}: `{raw}`"
        return None, ""
    if tool in EDIT_TOOLS:
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        r = governance_hit(str(path), project_dir or str(payload.get("cwd") or ""))
        return ("ask", r) if r else (None, "")
    return None, ""


def emit(decision, reason, out=sys.stdout, err=sys.stderr) -> int:
    if decision == "deny":
        err.write("[destructive-guard] BLOCKED: " + reason +
                  ". Irreversible; ask the owner to run it, naming the resource.\n")
        return 2
    if decision == "ask":
        out.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "[destructive-guard] " + reason}}) + "\n")
    return 0


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    return emit(*decide(payload))


def self_test() -> None:
    def d(tool, cwd="/w", root="", **ti):
        return decide({"tool_name": tool, "tool_input": ti, "cwd": cwd}, project_dir=root)[0]
    deny = ["git reset --hard HEAD~1", "git -C sub reset --hard", "git checkout -- a.txt",
            "git checkout .", "git restore src/", "git clean -fd", "git clean -xdf",
            "git stash drop", "rm -rf /", "rm -rf ~", "sudo rm -fr /*", "rm -r -f .",
            "mkfs.ext4 /dev/sdb1", "dd if=img of=/dev/sda bs=4M",
            "cd x && git reset --hard", "bash -c 'git clean -fd'", "timeout 5 git reset --hard",
            "sudo -u root rm -rf /", "sudo -E -u root rm -rf /", "doas rm -rf /",
            "env -i rm -rf /", "env -u PATH rm -rf ~", "bash -lc 'git reset --hard'",
            'rm -rf "$HOME"', 'rm -rf "/"', "rm -rf '.'"]
    for c in deny:
        assert d("Bash", command=c) == "deny", c
    ask = ["git push origin main", "git push --force", "git rebase -i HEAD~3",
           "git reset HEAD~1", "git tag v1", "git merge feature", "git branch -D old",
           "git commit --amend", "git stash", "rm -rf build/", "bash -lc 'git push'",
           "sh -ec 'git push origin main'", "gh pr create --fill", "gh pr merge 12",
           "glab mr merge 3", "gh release create v1", "zsh -o pipefail -c 'git push'"]
    for c in ask:
        assert d("Bash", command=c) == "ask", c
    allow = ["git status", "git log --oneline", "git diff", "git add -A", "git commit -m x",
             "git switch -c topic", "git branch", "git tag", "git stash list",
             "echo 'git reset --hard'", 'grep -n "rm -rf /" notes.md',
             "dd if=/dev/zero of=disk.img bs=1M count=1", "rm -f one.txt", "ls -la", "git restore --staged a",
             "sudo -u app ls /", "gh pr list", "gh release view v1", 'rm -f "/"']
    for c in allow:
        assert d("Bash", command=c) is None, c
    # strict profile asks on every mutation, still allows reads
    global PROFILE
    PROFILE = "strict"
    try:
        assert d("Bash", command="git commit -m x") == "ask"
        assert d("Bash", command="git add .") == "ask"
        assert d("Bash", command="git status") is None
    finally:
        PROFILE = "posture"
    # a file BODY that mentions a command is data, not a command (a known false positive)
    assert d("Write", file_path="/w/notes.md", content="run git reset --hard then git push") is None
    assert d("Edit", file_path="/w/README.md", old_string="a", new_string="git commit") is None
    # governance edits ask, wherever they are addressed from
    assert d("Edit", file_path="/w/CLAUDE.md") == "ask"
    assert d("Write", file_path="/w/.claude/settings.json") == "ask"
    assert d("Edit", file_path="/w/docs/graph/agents/tester.md") == "ask"
    assert d("Edit", file_path="/w/src/app.py") is None
    # the payload cwd follows the agent's `cd`: governance still asks from a subdirectory
    assert d("Write", cwd="/w/src", file_path="/w/.claude/settings.json") == "ask"
    assert d("Edit", cwd="/w/sub", file_path="/w/docs/graph/agents/x.md") == "ask"
    assert d("Write", cwd="/w/src", root="/w", file_path="/w/.claude/settings.json") == "ask"
    assert d("Edit", cwd="/w/src", root="/w", file_path="/w/src/app.py") is None
    # a user-level copy outside the repository matches through its trailing parts
    assert d("Edit", root="/w", file_path="/x/.claude/agents/a.md") == "ask"
    # other tools and malformed input: no decision
    assert d("Read", file_path="/w/CLAUDE.md") is None
    assert decide({"tool_name": "Bash", "tool_input": {}})[0] is None
    # exit-code contract
    import io
    o, e = io.StringIO(), io.StringIO()
    assert emit("deny", "x", o, e) == 2 and "BLOCKED" in e.getvalue() and o.getvalue() == ""
    o, e = io.StringIO(), io.StringIO()
    assert emit("ask", "y", o, e) == 0
    assert json.loads(o.getvalue())["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert emit(None, "", io.StringIO(), io.StringIO()) == 0
    print(f"self-test: PASS ({len(deny)} deny, {len(ask)} ask, {len(allow)} allow, strict "
          "profile, body text ignored, governance edits, exit-code contract)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        sys.exit(0)
    try:
        sys.exit(main())
    except Exception as exc:  # a guard bug must never brick a session
        sys.stderr.write("[destructive-guard] internal error, allowing: %s\n" % exc)
        sys.exit(0)
```

Recorded run of the self-test and of the hook on synthetic payloads:

```text
$ python3 destructive-guard.py --self-test
self-test: PASS (26 deny, 17 ask, 19 allow, strict profile, body text ignored, governance edits, exit-code contract)
$ echo '{"tool_name":"Bash","tool_input":{"command":"git reset --hard origin/main"}}' | python3 destructive-guard.py
[destructive-guard] BLOCKED: git reset --hard discards uncommitted work: `git reset --hard origin/main`. Irreversible; ask the owner to run it, naming the resource.
exit 2
$ echo '{"tool_name":"Bash","tool_input":{"command":"git push origin topic"}}' | python3 destructive-guard.py
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[destructive-guard] version-control change: git push: `git push origin topic`"}}
exit 0
$ echo '{"tool_name":"Write","tool_input":{"file_path":"/w/notes.md","content":"git reset --hard"}}' | python3 destructive-guard.py
exit 0
$ echo '{"tool_name":"Edit","tool_input":{"file_path":"/w/AGENTS.md"}}' | python3 destructive-guard.py
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "[destructive-guard] governance file edit: /w/AGENTS.md"}}
exit 0
$ echo 'not json' | python3 destructive-guard.py
exit 0
```

The third payload writes a file whose content says `git reset --hard`. The
naive hook denied it, and it also denied `rm -rf /tmp/build`. This hook allows
the first and asks on the second.

## 4. Portable vs blueprint

- **Portable (use as-is):** the command splitting, the deny rules, the two
  version-control profiles, the governance-path check, the exit-code contract,
  the self-test.
- **Write per project:** `GOVERNANCE_GLOBS` (the files whose edits need a
  person: list the plant's own instruction files, charters and hook wiring;
  every trailing part of the target path is matched, so the user-level
  copies under the home directory, such as `~/.claude/agents/`, ask too, and
  a host that keeps user instructions in another folder needs its own glob),
  `PROFILE`, and the wiring entry for the host in use.
- **Adopting notes:**
  - The tool names (`Bash`, `Edit`, `Write`, `MultiEdit`, `NotebookEdit`) and
    the payload fields are those of one host's hook contract. A host with a
    different contract needs its names in `SHELL_TOOLS` and `EDIT_TOOLS`, and
    its own output shape in `emit`.
  - A second host, the editor-based agent whose hook files live in the
    repository under `.github/hooks/`, documents the same contract in its
    Local hooks reference: exit 2 is a blocking error with stderr given to
    the model, and `hookSpecificOutput` takes `permissionDecision` `ask`.
    The same reference says that host ignores `matcher` values, so the hook
    runs for every tool, and that "tool names and input schemas differ
    between harnesses". On that host `SHELL_TOOLS` and `EDIT_TOOLS` must hold
    its own tool names, read from its debug log. With the names of this
    page's host, the hook gets a tool it does not know on every call and
    passes everything without a sound.
  - Install the script where the host's settings can reach it, next to the
    other hooks, and add it to the hook inventory the plant already keeps.

## 5. Pitfalls and sharp edges

- **"Ask" is a deny in a headless run.** Upstream: in a non-interactive run
  where nobody can answer the prompt, the call is denied and the model reads
  the reason. Upstream also says the host's deny and ask rules are evaluated
  whatever the hook returns. It does not say that an allow rule cancels a
  hook's `ask`, so do not count on one. An unattended job that must push or
  tag does that step outside the agent (the job's own script, after the agent
  ends), not through a weaker guard. This is also why `strict` breaks
  unattended commits.
- **A hook that does not start fails in two directions.** On this contract
  only exit 2 blocks, and a broken start produces three different codes:
  - a wrong script path: `python3` exits **2** ("can't open file"), so every
    shell call and every edit is blocked and the session is stuck. A relative
    path in the wiring turns wrong as soon as the agent runs `cd`, which is
    why the wiring in §2 goes through `${CLAUDE_PROJECT_DIR}`;
  - a syntax error in the script: exit 1, so everything is allowed;
  - a missing interpreter: the shell exits 127, so everything is allowed.

  Run `--self-test` after every edit. After installing, run the wired
  command from a subdirectory of the project twice: once with a known-deny
  payload (it must exit 2 with the guard's own reason) and once with an
  ordinary command such as `ls` (it must exit 0).
- **Indirection passes.** A script, an alias, a task-runner target, or a
  shell edit of a governance file (`sed -i` on an instruction file) is not
  seen. The hook covers the direct case; the host's deny rules and review
  cover the rest.
- **Quote masking can hide a real command.** `bash -c` and `eval` payloads
  are unwrapped, but a command built inside another interpreter
  (`python -c "os.system('git reset --hard')"`) is a quoted argument and
  passes. Do not try to parse every interpreter. Keep that case for review.
- **Keep the deny list short.** Every deny is a hard stop that the agent must
  hand to a person. Deny only what cannot be undone locally. Everything that
  can be undone, or only needs a name, belongs in ask.
- **The reason is for the model, so make it actionable.** The deny line names
  the rule, quotes the command, and says what to do next: ask the owner, and
  name the resource. A bare "blocked" makes the agent retry with a variant.

## 6. Tests that cover it

The self-test in the script above (`destructive-guard.py --self-test`)
asserts: each deny pattern is denied, including behind `cd x &&`, inside
`bash -c '...'` and `bash -lc '...'`, behind `timeout`, behind `sudo`,
`sudo -u root`, `doas`, `env -i` and `env -u NAME`, after `git -C <dir>`, and
with a quoted `"$HOME"`, `"/"` or `'.'` target; each posture-profile verb
asks, including inside `bash -lc` and `sh -ec` and after `-o pipefail`;
opening or merging a pull request and creating a release ask; `rm -rf build/`
asks; reads (`status`,
`log`, `diff`, a bare `branch` or `tag`, `stash list`), local `add` and
`commit`, quoted mentions inside `echo` and `grep`, `dd` to a file and a
non-recursive `rm`, `sudo -u app ls` and a read-only `gh` command pass; the strict profile asks on `add` and `commit` and
still passes `status`; a file body that mentions destructive commands is not
read; edits to the instruction file, the host settings file and an agent
charter ask, also when the payload `cwd` is a subdirectory and with or
without a project root, and an edit to a source file passes; another tool, and a payload
without a command, get no decision; deny writes stderr and returns 2, ask
writes the JSON and returns 0, no decision returns 0.

- **How to run the tests:** `python3 destructive-guard.py --self-test` (exit 0
  on pass; an `AssertionError` names the command that was misclassified).

## 7. References & neighbours

- **Related tools:** `integrations/claude-code/bound-hook.py` (the seed's
  blocking-prone command guard, the same contract applied to a different
  hazard); `core/method/vcs-posture.md` (§1 local commit, §2 publishing
  authorization, which the `posture` profile mechanizes);
  `tool-corpus/testing/working-tree-snapshot.md` (how to copy a working tree
  safely, which removes one reason to reach for a destructive reset).
- **Sources:** distilled from practice. The hook contract
  (exit codes, `permissionDecision` values, headless behaviour, stderr
  routing, `${CLAUDE_PROJECT_DIR}`, the working directory of a handler) is
  the host's hooks reference: https://code.claude.com/docs/en/hooks
  (retrieved 2026-10-05). The second host's contract is its Local hooks
  reference: https://code.visualstudio.com/docs/agents/reference/hooks-reference
  (retrieved 2026-10-05).

## 8. Changelog

- 2026-10-05: created. Reads only the command and the target path, not the
  whole payload; denies `rm -rf` and `dd` on exact targets, not prefixes;
  reason on stderr for a deny; a `posture` profile beside the `strict` one.
- 2026-10-05: review fixes. The wiring goes through `${CLAUDE_PROJECT_DIR}`,
  and the pitfall for a hook that does not start now gives the three exit
  codes. Governance paths resolve against the project root, not the payload
  `cwd`. A command behind `sudo -u`, `doas`, `env -i` or `bash -lc` is
  reached, and a quoted
  `"$HOME"` or `"/"` target is denied. Both profiles ask before a pull
  request is opened or merged and before a release is created. The second
  host's facts now cite its reference; the unconfirmed allow-rule remedy is
  gone.
