# Local development

The exact commands a fresh laptop runs to set up, develop, and
verify this project. **Every command listed here is expected to
work**; if a command stops working, fix this runbook in the same
increment as the underlying change.

## Prerequisites
- <runtime version>
- <package manager version>
- <other tools>

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
