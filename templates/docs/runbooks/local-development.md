# Local development

The exact commands a fresh laptop runs to set up, develop, and
verify this project. **Every command listed here is expected to
work**; if a command stops working, fix this runbook in the same
increment as the underlying change.

## Prerequisites
- <runtime version>
- <package manager version>
- <other tools>
- <invocation prerequisite, if any: the env file to source, the vault to
  unlock, the wrapper every command runs under>

An invocation prerequisite applies to **every** command below, not only
the first. Write it into each command, or into one wrapper script the
commands call. A prerequisite stated once at the top gets dropped by
whoever copies the third command on its own, and the failure it causes
looks like a bug in the command.

## Setup
```sh
<clone>
<install dependencies>
<post-install steps>
```

## Run
```sh
<start the project locally>
```

## Verify
See `verification.md` for the exact gate commands.

## Troubleshooting
- <known issue> — <fix>

A troubleshooting entry has a fix. Something that will bite a fresh
environment and has no fix yet is an open gap instead: file it once in
the register (`status: deferred`, with its owner and the condition that
reopens it) and reference it from here by name. Do not grow a second
status list inside this file — a gap tracked in two places is a gap
whose two entries will disagree about whether it is still open.
