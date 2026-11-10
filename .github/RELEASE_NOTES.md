## 8.3.2 — a missing guard script no longer blocks, and fixes from an independent review (2026-11-10)

An independent review of 8.3.1 confirmed eight defects. This round reproduces
each, fixes it and adds a test that failed first. A plant installed without
changes behaves as before, except where a defect below says otherwise. The
kernel is 7049 bytes and the always-loaded figures of every host are the same
as 8.3.1's; the brief blocks did not change. The review's other findings change
a default the owner set, or need evidence this round could not produce; they
are written up for the owner and not landed.

### The round in brief

- **A missing guard script no longer blocks the tool it guards.** The Bash and
  SendMessage guards ran `python3 <script>` with no existence test, and
  `python3` exits 2 on a missing file, which the host reads as a refusal. The
  settings commands now test that the script is a regular file. When it is, the
  script runs and its exit code passes through, so exit 2 still blocks. When it
  is absent, a dangling link or a directory, the command exits 0 and prints
  `cypress: hook script missing: <path>; the guard is off. Re-run install.sh to
  restore it.` on stderr. Only the Claude Code adapter wires such a guard.
- **`--check` names a missing guard script.** It looked only at the two
  context hooks. It now fails with the event, matcher and path of a missing
  `PreToolUse` script and the remedy, and still runs no guard.
- **The hooks' documentation states the real failure model.** A bug inside a
  guard allows the call; a missing script is the wiring's case.
- **The source index describes the plant's code.** After an install it
  listed the installer's own hooks, agents, skills, commands, prompts and
  kernel files as the plant's code. The installer's stamp does not list the
  files it placed, and a directory rule would hide a file the plant wrote
  beside them, so the index now skips a list of the exact paths the installer
  places. A test installs every host and fails on a placed file the list lacks.
- **`--check` flags a drifted skill.** It compared the Claude Code agents with
  their nodes and left `.claude/skills/` unchecked, so an edit to a skill's
  node passed. It now names each skill projection that differs from its node.
  `install.sh claude-code --recompose-agents` re-projects skills as well as
  agents, backs up a projection it replaces, and writes no node.
- **The gate runs as uid 0.** Two cases depend on `chmod` denying access, which
  it does not for root. Each now prints one SKIPPED line there and is unchanged
  for any other user.
- **The bound hook treats equivalent spellings alike.** `npm i`, `npm add`,
  `pnpm`, `yarn` and `bun` installs, `npm clean-install`, `python -m pip
  install`, `uv pip install`, `podman` and `nerdctl` runs, `docker exec -ti`,
  `cargo b`, `gmake`, `tail -F` and the `--follow` forms are blocked as the
  commands they spell, and pass when bounded. Quoted text, heredoc bodies and
  commands that are not equivalent (`npm info`, `pip list`, `git log --follow`)
  stay allowed.
- **The front door states the whole measurement.** The README cost row read
  "11% more tokens". The record behind it also reports 20% more tool calls, 20%
  more wall-clock time, a defect that the run without the method found and the
  run with it missed, and that it was one task run once. The row now says all
  of it, and a seed-lint check holds each number to the record or the slice it
  cites.

### Also in this round

- Seven owner decision notes in
  `docs/plans/owner-decisions-8.3.2-review-fixes.md`, prepared and not adopted:
  the bound hook's scope, the interpreter floor, the knowledge rule, token
  estimates, copied code, undated corpus pages and the evidence for 8.3.0's
  figures.
- The test that pinned the unguarded `PreToolUse` command now pins the
  exit-preserving, missing-script-safe form.
- Not done: `--check` still does not compare skill projections of the other
  hosts (plan row 12.2).
- The plan of record is `docs/plans/grill-8.3.2-review-fixes.md`.
