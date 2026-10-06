# Tool: touched-file-lint-hook

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable hook script: it runs as-is under any
> agent harness that runs a command after each tool call; the linter and the
> file globs are the plant's.

## 0. Identity

- **Category:** testing
- **Name:** touched-file-lint-hook
- **Language / runtime:** python3, **stdlib only**, plus `git` for the
  touched-file set and whatever linter the plant names
- **Stability:** **portable**. The touched-set rule, the fail-closed
  blocking, the timeout and crash handling, the session preflight and the
  self-test are complete. The output contract follows one harness's hook
  reference (Claude Code); another harness needs the check in §5.

## 1. What it does

Two hooks for an agent session, one script.

**`post-tool`** runs after every tool call. It lints exactly the files the
session has changed so far, and blocks the turn when the lint fails. "Blocks"
means the failure goes back to the model as feedback next to the tool result,
so it fixes the file before it moves on. The lint is incremental (only the
touched files, so it is cheap on every edit) and deterministic (it runs every
time; it is not a reminder the model may skip). It is **fail-closed**: a
linter that is not installed, hangs or crashes blocks too, because "cannot
lint" is not "clean".

**`preflight`** runs once at session start. It checks that the environment
variables and command-line tools the repository's gates need are present and
runnable, and injects a warning list into the session. It is **fail-open**:
it never stops the session; it makes sure the model knows, before it plans,
that a gate will be inert.

Neither replaces the repository's full gate. Run that at delivery, because a
hook sees only what this session touched and a lint is not the whole gate.

## 2. Interface & invocation

```sh
touched_lint.py post-tool --glob '<glob>' [--glob '<glob>' ...] -- <linter> [<args>...]
touched_lint.py preflight [--require-env NAME[:file][=hint] ...] [--require-tool TOOL[=hint] ...]
touched_lint.py --self-test
```

- **`post-tool` inputs:** one or more `--glob` patterns, read as git
  pathspecs relative to the repository root (`*.yml` matches in every
  directory, `config/*.yml` only under `config/`); the linter command after
  `--`, which receives the touched files as trailing arguments and runs from
  the repository root, so give it as a command on `PATH` or an absolute path;
  the hook payload on stdin (optional; its `cwd`, when present, picks the
  repository, and its `tool_input.file_path` is added to the set);
  `TOUCHED_LINT_TIMEOUT` seconds (default 100).
- **`post-tool` outputs and exits:** exit `0` with no output when nothing
  matches or the lint passes. Exit `2` to block, with the reason (the files
  and the first 40 lines of linter output) on stderr and as JSON on stdout:
  `{"decision": "block", "reason": …}`. A wiring mistake (an unknown option,
  an option with no value, no `--glob`, no linter) also exits `2`, with
  `misconfigured` in the reason.
- **`preflight` inputs:** `--require-env NAME` (must be non-empty),
  `--require-env NAME:file` (must name an existing file), `--require-tool
  TOOL` (must run `TOOL --version` with exit 0 within 10 seconds). An
  optional `=hint` on either is appended to its warning, so the warning says
  how to fix it (`--require-tool 'yamllint=install it with pip'`).
  `TOUCHED_PREFLIGHT_BUDGET` seconds (default 20) caps the whole check; keep
  it below the `SessionStart` hook's `timeout`.
- **`preflight` outputs:** always exit `0`. With warnings, one JSON object:
  `systemMessage` (shown to the user) and
  `hookSpecificOutput.additionalContext` (added to the model's context), both
  holding the list. With none, no output. A wiring mistake becomes one
  warning that says the preflight is misconfigured.
- **Wiring, Claude Code** (`.claude/settings.json`; add entries beside the
  hooks already there, never replace them):

  ```json
  {"hooks": {
    "PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "timeout": 120,
      "command": "python3 \"$CLAUDE_PROJECT_DIR/tools/touched_lint.py\" post-tool --glob '*.yml' --glob '*.yaml' -- yamllint -s"}]}],
    "SessionStart": [{"hooks": [{"type": "command", "timeout": 30,
      "command": "python3 \"$CLAUDE_PROJECT_DIR/tools/touched_lint.py\" preflight --require-tool yamllint"}]}]}}
  ```

- **Wiring, VS Code agent hooks** (`.github/hooks/<name>.json`):

  ```json
  {"hooks": {"PostToolUse": [{"type": "command", "timeout": 120,
    "command": "python3 tools/touched_lint.py post-tool --glob '*.yml' -- yamllint -s"}]}}
  ```

## 3. Approach / algorithm

**The touched set is the union of three git listings, plus the named file.**

- `git diff -z --name-only -- <globs>`: modified, not staged.
- `git diff -z --cached --name-only -- <globs>`: staged.
- `git ls-files -z --others --exclude-standard -- <globs>`: **untracked and
  not ignored**, the files the session created and nobody has added yet.
- The `tool_input.file_path` of the payload, when it lies inside the
  repository and its repository-relative path matches a glob.

Deleted paths are dropped (the linter would fail on a missing file). Ignored
files stay out unless the tool call named one. A hook of this kind that
uses only the first two listings lets a brand-new file escape the lint until
it is staged: the case where a lint matters most. A full-repository
validator uses `ls-files --others --exclude-standard` for the same reason.

The listings run with `-z`. Without it, git C-quotes any path with a byte
above 0x80, a double quote, a backslash or a control character
(`core.quotePath`), the quoted name is not a file on disk, and the file
silently leaves the set. The repository is the one around the payload's
`cwd` when the payload has one: Claude Code's hook reference says that field
follows the agent into a worktree or after a `cd`, while the project
directory stays at the session root. Both the root and the named path go
through `realpath`, so a project opened through a symlink still matches.

**Fail-closed in every way the hook can fail.** Each of these blocks:

- the lint fails;
- the linter is not on `PATH`;
- the linter runs longer than `TOUCHED_LINT_TIMEOUT`;
- the hook is wired wrong (a mistyped option, a missing value);
- the script itself raises.

The timeout, the wiring mistake and the crash need explicit handling. Claude Code's hook
reference says a command hook that reaches its configured `timeout` is
cancelled and its output discarded, so it renders no decision. An exit code
other than `0` or `2` is a non-blocking error there. Without the internal
timeout below the hook's own and the catch-all, a hung or broken linter would
let every edit through. A plain argument error would exit `1` and make the
guard inert from the first session, with only a hook-error notice. Set
`TOUCHED_LINT_TIMEOUT` below the hook's `timeout`.

**The block reaches the model two ways at once.** On exit `2`, Claude Code
gives the model the reason from a JSON blocking decision, and stderr
otherwise; VS Code's local hook runner gives the model stderr. For
`PostToolUse` the tool has already run, so the block cannot undo the write;
it puts the lint output in front of the model with the tool result. The
script writes the reason to stderr and the JSON (`decision: "block"`,
`reason`) to stdout, so either reading carries it. It does not repeat the
reason in `additionalContext`, which would put the same text in front of
the model twice.

**Outside a repository, `post-tool` does nothing**, even when the payload
names a matching file: there is no touched set and no root to run the linter
from.

**Preflight checks that a tool runs, not only that its name resolves.** A
version-manager shim is on `PATH` even when the tool is not installed for
the active version, and then the gate that calls it fails later with an
unrelated-looking error. `TOOL --version` with a 10-second limit tells the two
apart. All checks share one budget below the hook's `timeout`: a harness
that cancels a timed-out hook discards its output, so three hung tools would
otherwise make every warning vanish. When the budget runs out, the warning
names the tools left unchecked. The warnings go to both the user
(`systemMessage`) and the model (`additionalContext`): in Claude Code,
`systemMessage` is shown to the user, and `additionalContext` (or plain
stdout) is what the model sees at `SessionStart`. Each warning carries the
plant's remediation hint when one is given; practice showed that a
warning which says how to fix the gap is the useful kind.

## 4. Portable vs blueprint

- **Portable (use as-is):** the script below.
- **Project-specific (fill in):** the globs and the linter per file kind (one
  hook entry each); the environment variables and tools the gates need; the
  hook wiring for the harnesses in use.

```python
#!/usr/bin/env python3
"""touched-file-lint-hook: lint exactly the files the session changed, after
every tool call, and block when the lint fails or cannot run. A second mode
warns at session start which gate prerequisites are missing.

  touched_lint.py post-tool --glob '*.yml' --glob '*.yaml' -- yamllint -s
  touched_lint.py preflight --require-env 'SECRETS_FILE:file=run the init script first' \
      --require-tool 'yamllint=install yamllint'
  touched_lint.py --self-test

post-tool: exit 0 clean or nothing to lint; exit 2 block (lint failed, linter
absent, linter timed out, hook misconfigured or crashed), with the reason on
stderr and as JSON on stdout.
preflight: always exit 0 (fail-open); warnings go to stdout as JSON.
Stdlib only; needs git for the touched set.
"""
import fnmatch, json, os, shutil, subprocess, sys, time

LINT_TIMEOUT = int(os.environ.get("TOUCHED_LINT_TIMEOUT", "100"))      # below the hook's own
PREFLIGHT_BUDGET = int(os.environ.get("TOUCHED_PREFLIGHT_BUDGET", "20"))  # below SessionStart's


def git(*args, cwd=None):
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True)
    return p.returncode, os.fsdecode(p.stdout)


def read_payload():
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def touched(globs, payload, cwd=None):
    """Unstaged, staged and untracked-not-ignored files matching the globs,
    plus the file the tool call named; deleted paths dropped. Paths are
    relative to the repository root, and the linter runs there. The payload's
    cwd wins over the process cwd: it follows the agent into a worktree."""
    cwd = payload.get("cwd") or cwd
    rc, top = git("rev-parse", "--show-toplevel", cwd=cwd)
    if rc != 0:
        return None, []
    root = os.path.realpath(top.strip())
    names = set()
    for args in (("diff", "-z", "--name-only"), ("diff", "-z", "--cached", "--name-only"),
                 ("ls-files", "-z", "--others", "--exclude-standard")):
        rc, out = git(*args, "--", *globs, cwd=root)   # -z: no C-quoting of unusual names
        names.update(n for n in out.split("\0") if n)
    path = (payload.get("tool_input") or {}).get("file_path")
    if isinstance(path, str) and path:
        rel = os.path.relpath(os.path.realpath(os.path.join(cwd or os.getcwd(), path)), root)
        if not rel.startswith("..") and any(fnmatch.fnmatch(rel, g) for g in globs):
            names.add(rel)
    return root, sorted(n for n in names if os.path.isfile(os.path.join(root, n)))


def block(reason):
    sys.stderr.write(reason + "\n")
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}) + "\n")
    return 2


def post_tool(globs, linter, payload, cwd=None):
    root, files = touched(globs, payload, cwd)
    if not files:
        return 0
    if not shutil.which(linter[0]):
        return block(f"{linter[0]} is required to lint the touched files "
                     f"({', '.join(files)}) but is not installed: cannot lint is not clean.")
    try:
        p = subprocess.run([*linter, *files], cwd=root, capture_output=True, text=True,
                           timeout=LINT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return block(f"{linter[0]} did not finish in {LINT_TIMEOUT}s on: {', '.join(files)}")
    if p.returncode != 0:
        out = (p.stdout + p.stderr).strip().splitlines()
        shown = "\n".join(out[:40]) + ("\n..." if len(out) > 40 else "")
        return block(f"{linter[0]} failed on the files this session changed "
                     f"({', '.join(files)}):\n{shown}")
    return 0


def runs(tool, limit):
    """On PATH is not enough: a version-manager shim is on PATH and may not run."""
    if not shutil.which(tool):
        return False
    try:
        return subprocess.run([tool, "--version"], capture_output=True,
                              timeout=max(limit, 0.1)).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def preflight(envs, tools, env=None, budget=None):
    """envs: NAME[:file][=hint]; tools: TOOL[=hint]. The hint is appended to
    the warning, so the warning says how to fix what it reports."""
    env = os.environ if env is None else env
    deadline = time.monotonic() + (PREFLIGHT_BUDGET if budget is None else budget)
    warn = []
    for spec in envs:
        spec, _, hint = spec.partition("=")
        name, _, kind = spec.partition(":")
        val = env.get(name)
        if not val:
            warn.append(f"{name} is not set; gates that need it will not run.")
        elif kind == "file" and not os.path.isfile(val):
            warn.append(f"{name} names a file that does not exist; gates that need it will not run.")
        else:
            continue
        if hint:
            warn[-1] += " " + hint
    for i, spec in enumerate(tools):
        tool, _, hint = spec.partition("=")
        left = deadline - time.monotonic()
        if left <= 0:
            unchecked = ", ".join(s.partition("=")[0] for s in tools[i:])
            warn.append(f"preflight ran out of time; not checked: {unchecked}.")
            break
        if not runs(tool, min(10, left)):
            warn.append(f"{tool} is not installed or does not run; the lint or gate "
                        "that runs it is inert." + (" " + hint if hint else ""))
    if warn:
        session_warning("Environment warnings for this session:\n"
                        + "\n".join("- " + w for w in warn))
    return 0


def session_warning(msg):
    """systemMessage reaches the user; additionalContext reaches the model."""
    sys.stdout.write(json.dumps({"systemMessage": msg, "hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": msg}}) + "\n")
    return 0


def parse(argv):
    """Raise ValueError on any wiring mistake; main turns it into a block
    (post-tool) or a warning (preflight), never into a non-blocking exit 1."""
    mode, rest = argv[0], argv[1:]
    opts, linter = {"--glob": [], "--require-env": [], "--require-tool": []}, []
    if "--" in rest:
        i = rest.index("--")
        rest, linter = rest[:i], rest[i + 1:]
    if len(rest) % 2:
        raise ValueError(f"option {rest[-1]} has no value")
    for k, v in zip(rest[::2], rest[1::2]):
        if k not in opts:
            raise ValueError(f"unknown option {k}")
        if k == "--require-env" and v.partition("=")[0].partition(":")[2] not in ("", "file"):
            raise ValueError(f"unknown kind in --require-env {v} (only :file)")
        opts[k].append(v)
    return mode, opts, linter


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if not argv or argv[0] not in ("post-tool", "preflight"):
        sys.stderr.write(__doc__)
        return 2
    try:
        mode, opts, linter = parse(argv)
    except ValueError as exc:
        if argv[0] == "preflight":      # fail-open, but say the check itself is broken
            return session_warning(f"session preflight misconfigured: {exc}")
        return block(f"touched-file lint hook misconfigured: {exc}")
    if mode == "preflight":
        read_payload()
        return preflight(opts["--require-env"], opts["--require-tool"])
    if not opts["--glob"] or not linter:
        return block("touched-file lint hook misconfigured: post-tool needs --glob and a "
                     "linter after --")
    try:
        return post_tool(opts["--glob"], linter, read_payload())
    except Exception as exc:   # a crash must block, not exit 1 (non-blocking on most hosts)
        return block(f"touched-file lint hook failed: {type(exc).__name__}: {exc}")


def self_test():
    import contextlib, io, tempfile
    with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
        return _self_test(d, outside, contextlib, io)


def _self_test(d, outside, contextlib, io):
    d = os.path.realpath(d)
    run = lambda *a: subprocess.run(a, cwd=d, check=True, capture_output=True)
    run("git", "init", "-q")
    run("git", "config", "user.email", "t@example.test")
    run("git", "config", "user.name", "t")
    lint = os.path.join(d, "fake_lint.py")       # fails on a line saying BAD
    open(lint, "w").write("import sys\nbad=[f for f in sys.argv[1:] if 'BAD' in open(f).read()]\n"
                          "print('\\n'.join(b+': BAD found' for b in bad)); sys.exit(1 if bad else 0)\n")
    open(os.path.join(d, ".gitignore"), "w").write("ignored.yml\nfake_lint.py\nconf/*.yml\n")
    for name in ("a.yml", "gone.yml"):
        open(os.path.join(d, name), "w").write("ok: 1\n")
    run("git", "add", "."); run("git", "commit", "-qm", "init")
    linter = [sys.executable, lint]

    def call(fn, *a):
        o, e = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = fn(*a)
        return rc, o.getvalue(), e.getvalue()

    G = ["*.yml", "*.yaml"]
    assert call(post_tool, G, linter, {}, d)[0] == 0, "clean tree blocked"
    open(os.path.join(d, "new.yaml"), "w").write("x: BAD\n")       # untracked, never added
    rc, out, err = call(post_tool, G, linter, {}, d)
    assert rc == 2 and "new.yaml" in err and json.loads(out)["decision"] == "block", \
        "an untracked new file escaped the lint"
    os.remove(os.path.join(d, "new.yaml"))
    odd = "caff\u00e8 \"q\".yml"                                    # git C-quotes this without -z
    open(os.path.join(d, odd), "w").write("x: BAD\n")
    rc, _, err = call(post_tool, G, linter, {}, d)
    assert rc == 2 and odd in err, "a file with a non-ASCII or quoted name escaped the lint"
    os.remove(os.path.join(d, odd))
    open(os.path.join(d, "a.yml"), "w").write("ok: BAD\n")          # unstaged edit
    assert call(post_tool, G, linter, {}, d)[0] == 2
    run("git", "add", "a.yml")                                       # staged edit
    assert call(post_tool, G, linter, {}, d)[0] == 2
    run("git", "reset", "-q", "--hard")
    os.remove(os.path.join(d, "gone.yml"))                           # deleted: not linted
    open(os.path.join(d, "ignored.yml"), "w").write("BAD\n")         # ignored: not in the set
    open(os.path.join(d, "notes.txt"), "w").write("BAD\n")           # other extension
    os.mkdir(os.path.join(d, "conf"))
    open(os.path.join(d, "conf", "c.yml"), "w").write("BAD\n")       # ignored, in a subdirectory
    assert call(post_tool, G, linter, {}, d)[0] == 0, "deleted/ignored/other-extension linted"
    rc, out, err = call(post_tool, G, linter,
                        {"tool_input": {"file_path": os.path.join(d, "ignored.yml")}}, d)
    assert rc == 2 and "ignored.yml" in err, "the file the tool call named was not linted"
    rc, _, err = call(post_tool, ["conf/*.yml"], linter,
                      {"tool_input": {"file_path": os.path.join(d, "conf", "c.yml")}}, d)
    assert rc == 2, "a named file under a directory glob was not linted"
    link = os.path.join(outside, "link")
    os.symlink(d, link)
    rc, _, err = call(post_tool, G, linter,
                      {"cwd": link, "tool_input": {"file_path": os.path.join(link, "ignored.yml")}}, None)
    assert rc == 2 and "ignored.yml" in err, "a named file reached through a symlink was dropped"
    os.remove(link)
    assert call(post_tool, G, ["no-such-linter-xyz"], {}, d)[0] == 0, "nothing to lint, yet blocked"
    open(os.path.join(d, "b.yml"), "w").write("ok: 1\n")
    rc, _, err = call(post_tool, G, ["no-such-linter-xyz"], {}, d)
    assert rc == 2 and "not installed" in err, "an absent linter passed (fail-open)"
    global LINT_TIMEOUT
    LINT_TIMEOUT, saved = 1, LINT_TIMEOUT
    rc, _, err = call(post_tool, G, [sys.executable, "-c", "import time; time.sleep(5)"], {}, d)
    LINT_TIMEOUT = saved
    assert rc == 2 and "did not finish" in err, "a hung linter did not block"
    assert call(post_tool, G, linter, {}, outside)[0] == 0, "outside a repository, blocked"
    for argv in (["post-tool", "--globb", "*.yml", "--", "true"],
                 ["post-tool", "--glob", "*.yml", "--glob", "--", "true"],
                 ["post-tool", "--glob", "*.yml"]):
        rc, _, err = call(main, argv)
        assert rc == 2 and "misconfigured" in err, f"a wiring mistake did not block: {argv}"
    rc, out, _ = call(main, ["preflight", "--require-env", "HOME:dir"])
    assert rc == 0 and "misconfigured" in out, "a preflight wiring mistake was silent"
    rc, out, _ = call(preflight, ["NEEDED_VAR=source the init script", "FILE_VAR:file"],
                      ["no-such-tool-xyz=install it"], {"FILE_VAR": "/no/such/file"})
    msg = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert rc == 0 and "NEEDED_VAR" in msg and "FILE_VAR" in msg and "no-such-tool-xyz" in msg
    assert "source the init script" in msg and "install it" in msg, "a remediation hint was lost"
    rc, out, _ = call(preflight, [], ["git", "git"], {}, 0)
    assert rc == 0 and "ran out of time" in out, "an exhausted preflight budget was silent"
    rc, out, _ = call(preflight, ["HOME"], ["git"], {"HOME": "/"})
    assert rc == 0 and out == "", "preflight warned with everything present"
    print("self-test: PASS (untracked, unstaged and staged files linted; a non-ASCII name"
          " linted; deleted, ignored and other files skipped; named file linted, also under"
          " a directory glob and through a symlink; absent linter, hung linter and wiring"
          " mistakes block; no-op outside a repo; preflight warns with hints, within its"
          " budget, fail-open)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Recorded runs. A throwaway repository with one committed `a.yml`; the hook
fed a `PostToolUse`-shaped payload naming an untracked `new.yaml`; `yamllint`
as the linter (the repository path and timings are elided, nothing else):

```text
$ printf ... > new.yaml        # untracked, duplicate key
{"decision": "block", "reason": "yamllint failed on the files this session changed (new.yaml):\nnew.yaml\n  3:1       error    duplication of key \"key\" in mapping  (key-duplicates)", "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "yamllint failed on the files this session changed (new.yaml):\nnew.yaml\n  3:1       error    duplication of key \"key\" in mapping  (key-duplicates)"}}
exit 2
$ printf ... > new.yaml        # fixed
exit 0
$ same tree, linter absent
no-such-linter is required to lint the touched files (new.yaml) but is not installed: cannot lint is not clean.
exit 2
$ preflight
{"systemMessage": "Environment warnings for this session:\n- SECRETS_FILE is not set; gates that need it will not run.\n- no-such-linter is not installed or does not run; the lint or gate that runs it is inert.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Environment warnings for this session:\n- SECRETS_FILE is not set; gates that need it will not run.\n- no-such-linter is not installed or does not run; the lint or gate that runs it is inert."}}
exit 0
$ preflight, yamllint shim on PATH but not runnable
{"systemMessage": "Environment warnings for this session:\n- yamllint is not installed or does not run; the lint or gate that runs it is inert.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Environment warnings for this session:\n- yamllint is not installed or does not run; the lint or gate that runs it is inert."}}
exit 0
```

A second fixture after the fix pass: a throwaway repository, real `yamllint
-s` as the linter, the hook run as a command with a payload on stdin (paths
elided):

```text
clean tree                                          exit 0
untracked caffè.yml with a duplicate key            exit 2, "failed on ... (caffè.yml)"
--globb typo                                        exit 2, "misconfigured: unknown option --globb"
--glob with no value                                exit 2, "misconfigured: option --glob has no value"
ignored config/ignored2.yml named through a symlinked checkout     exit 2
same file named, --glob 'config/*.yml'              exit 2
outside a repository, payload names a failing file  exit 0
preflight, yamllint shim on PATH but not runnable   exit 0, warning ends "pip install yamllint" (the hint)
preflight --require-env HOME:dir                    exit 0, "session preflight misconfigured: unknown kind ..."
no arguments                                        exit 2
self-test: PASS (untracked, unstaged and staged files linted; a non-ASCII name linted; deleted, ignored and other files skipped; named file linted, also under a directory glob and through a symlink; absent linter, hung linter and wiring mistakes block; no-op outside a repo; preflight warns with hints, within its budget, fail-open)
```

## 5. Pitfalls and sharp edges

- **`git diff` misses new files.** Unstaged and staged changes are not the
  touched set. Add `git ls-files --others --exclude-standard`, or every file
  the session creates skips the lint.
- **`--name-only` without `-z` quotes non-ASCII names.** The quoted name
  matches no file, so a file named with an accent escapes the lint on every
  call except the one whose payload names it.
- **The hook process's directory is not the agent's.** In a worktree session
  the project directory stays at the main checkout. Read the payload's `cwd`,
  or the hook lints the wrong tree.
- **A fail-open lint hook is a reminder.** `|| true` on a guard, a missing
  linter treated as "nothing to report", a timeout the host swallows: each
  turns the hook into something that only works when it was not needed. The
  context hooks of a session are fail-open by design; a lint hook is a guard.
- **The same file is not the same contract on every harness.** Several
  harnesses read `.claude/settings.json` or `.github/hooks/*.json`, but
  events, matchers, payloads, exit codes and output fields differ between
  them; VS Code's documentation says so, and its local hook runner ignores
  `matcher` values, so every command for the event runs. This script does not
  depend on the matcher: it filters the touched set itself. VS Code's local
  hooks reference documents the same exit-`2` contract (stderr goes to the
  model, any other non-zero code is a warning to the user). Still test the
  block once in each harness in use: edit a file so the lint fails and
  confirm the model sees the lint output. Its `tool_input` fields are
  tool-specific, so `file_path` may be absent; the git listings still cover
  the edit.
- **`PostToolUse` cannot undo the write.** The block is feedback, not a
  rollback. To refuse a write before it happens, a `PreToolUse` hook has to
  lint the proposed content, which is a different tool.
- **The hook lints what the session touched since the last commit**, not
  only this turn's edit. A file left failing by an earlier turn keeps
  blocking until it is fixed or committed. That is intended; it is also why
  the files are listed in the reason.
- **Long file lists.** Every touched file goes to the linter on every tool
  call. On a large uncommitted change, commit at checkpoints or narrow the
  globs, and keep the internal timeout below the hook's.
- **A linter that resolves but does not run shows up as a lint failure.**
  A version-manager shim on `PATH` passes the "installed" check, then fails;
  the block reason then holds the shim's error, not lint output. It still
  blocks. The preflight's `--version` check names the cause at session start.
- **Preflight is not enforcement.** It warns. The gate that needs the
  variable or tool must still fail on its own when it is missing.
- **Two `SessionStart` hooks are normal.** If the harness already runs a
  session-start hook (a status summary, for example), add this one beside
  it. Both run.

## 6. Tests that cover it

`touched_lint.py --self-test` builds a throwaway git repository with a fake
linter that fails on the word `BAD`, and asserts: a clean tree passes; an
untracked new file is linted and blocks with JSON on stdout and the file named
on stderr; an untracked file with a non-ASCII and quoted name blocks; an
unstaged and a staged edit block; deleted, ignored and other-extension files
are not linted; an ignored file the payload names is linted, also under a
directory glob and when the payload reaches it through a symlink; an absent
linter passes when nothing matches and blocks when something does; a linter
that outlives the timeout blocks; outside a repository nothing happens; an
unknown option, an option with no value and a missing linter block; a
preflight wiring mistake becomes a warning; preflight lists a missing
variable, a variable naming a missing file and a missing tool with their
hints, reports an exhausted budget, and prints nothing when all are present.
The self-test removes its temporary directories.

- **How to run the tests:** `python3 touched_lint.py --self-test`; then the
  manual check in §5 in each harness.

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/destructive-command-guard-hook.md`
  (the `PreToolUse` guard of the same family; this page is the
  `PostToolUse` lint); `tool-corpus/testing/test-hygiene-lint.md` (a lint over
  test sources that this hook can run per edit);
  `tool-corpus/testing/working-tree-snapshot.md` (the same
  untracked-but-not-ignored listing, for copying a working tree).
- **Seed wiring:** `integrations/claude-code/settings.json` (the seed's own
  hooks, beside which these entries go).
- **Sources:** distilled from practice (a post-edit YAML
  lint hook and a session environment check); Claude Code hooks reference
  (https://code.claude.com/docs/en/hooks: exit codes, timeouts,
  `PostToolUse` and `SessionStart` input and output fields); VS Code agent
  hooks (https://code.visualstudio.com/docs/copilot/customization/hooks:
  shared hook files, differing behaviour, matchers ignored by the local
  runner); VS Code local hooks reference
  (https://code.visualstudio.com/docs/agents/reference/hooks-reference: exit
  `2` gives stderr to the model, `PostToolUse` and `SessionStart` output
  fields, a 30-second default `timeout`); git `ls-files` and `core.quotePath`
  (path quoting without `-z`).

## 8. Changelog

- 2026-10-05 — created from a post-edit lint hook and a
  session-start environment check, generalized: the touched set gained
  untracked-not-ignored files and the file the tool call named, a linter
  timeout and a crash now block, preflight checks that a tool runs (not only
  that it resolves on `PATH`), and its warnings go to the model as well as the
  user; by tool-smith.
- 2026-10-05 (review fix pass): a wiring mistake now blocks instead of
  exiting `1`; the listings use `-z`; the named file matches on its
  repository-relative path after `realpath`; the payload's `cwd` picks the
  repository; preflight has one time budget and per-check remediation hints
  (kept from the original check); the block JSON dropped the duplicate
  `additionalContext`. Two more defects are corrected without
  comment above: its hand-built JSON did not escape newlines, and it printed
  plain text before the JSON on stdout, so a host could not parse it; by
  tool-smith.
