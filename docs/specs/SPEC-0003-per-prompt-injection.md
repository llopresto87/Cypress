---
status: active
status_date: 2026-09-23
owner: architect
status_evidence: tests/test-bound-hook.sh, tests/test-seed-lint.sh, tests/seed-lint.py, tests/test-nested-checkout.sh (RED landed with this promotion; §10 says which rows are red)
---

# SPEC-0003: per-prompt injection

## 0. Metadata

- **Identifier:** SPEC-0003-per-prompt-injection
- **Status:** see frontmatter (single home)
- **Sign-offs:** product [x] · architect [x] · tester [x] · security [x]
  Each role signed on its own re-check of 2026-09-23; the tester's sign is
  conditional on E1 to E3 as applied here (§12).

- **Owner:** architect
- **Date:** 2026-09-23
- **Last reviewed:** 2026-09-23
- **Related grill section:** docs/plans/grill-7.28.0-context-residency.md §3, §4, §5, §8, §16, §17
- **Related ADRs:** adr-0003-enforcement-layering-honesty (the enforcement classes); adr-0009-host-support-tiers; ADR-0010 (the Residency Rule and this spec's threat model, owed at the plan's §10 close, not written yet)
- **Supersedes:** —
- **Superseded by:** —

## 1. Summary

This spec covers the text that two per-prompt surfaces inject into a session:
`integrations/claude-code/route-hook.py` on `UserPromptSubmit` (which Copilot
also runs, because it reads `.claude/settings.json`), and
`integrations/prime-agent/route-extension.ts` on `before_agent_start`. It also
covers how each first-class host avoids re-reading what a session already
surfaced. On Claude Code the hook keeps a session ledger on disk and
`status-hook.py` resets it on `SessionStart`. On Prime Agent the extension
keeps no state and injects in full on every prompt, and the
`integrations/prime-agent/APPEND_SYSTEM.md` overlay asks the model to keep a
set of surfaced node ids as a Python variable in the session's IPython kernel.

It turns plan §4 into contracts. Four things are contracted. The prompt is
never echoed back into the injection: router output that does not begin with
the exact echo of the prompt counts as a router failure, so it is never passed
through. The injection points at the kernel and does not restate it. A node
surfaced earlier this session is named again by id rather than repeated in full
(Claude Code, enforced by the hook) or is not re-opened while its content is
still in view (Prime Agent, soft, kept by the model). Every doubt about that
last step resolves toward the full injection (I-1).

## 2. Scope

- **In scope:**
  - the exact text each surface injects, in full mode and in reminder mode
  - the router call on both hosts: the prompt as one `--plan=` value, and the
    exact-echo rule for the output
  - the Claude Code session ledger under `.cypress/session/`: path rule,
    schema, validation, descriptor-relative I/O, owner and mode checks,
    garbage collection, atomic write, self-ignoring directory, reset
  - the Prime Agent overlay section that asks the model to keep the surfaced
    set, and the absence of ledger state in `route-extension.ts`
  - the fail-open behaviour of both hooks on a Copilot-shaped envelope
  - the invariants the plan names I-1, I-2, I-3, I-6, I-7 and I-8, as far as
    a test can observe them
- **Out of scope:**
  - the router's ranking and its output format. `graph-lint.py` is plant-owned
    and create-only, so this spec parses its current output and does not change
    it (plan §4.1)
  - the status summary text of `status-hook.py` and `status-extension.ts`.
    Only the ledger reset is added to the hook
  - agent and skill `description`s (Slices B and C, parked; plan §1.1)
  - the Residency Rule prose and the fact key `context-router.residency` added
    to `skills/context-router/SKILL.md` `owns:`. That is Slice E; this spec
    enforces the rule on the hooks, and the skill is the rule's one home
  - whether a model on Prime Agent follows the overlay instruction. No gate
    observes model behaviour; §11 records the absence
  - the rest of `APPEND_SYSTEM.md`. An I-8 audit of the whole overlay stays
    plan §12 item 5; only the new section is held to I-6 and I-8 here
  - opencode, which ships no per-prompt injection, so there is nothing to
    dedup. The gap is recorded in `documentation/host-capability-matrix.md`
  - codex and github-copilot, frozen by ADR-0009, which get nothing new. The
    only Copilot obligation is that the Claude Code hook keeps failing open on
    its envelope
  - the `status-extension.ts` once-per-process flag (`let shown`), a known
    defect that this spec does not fix

## 3. User-facing behavior

(Drafted by `architect`; revised by `product`.)

This change has two users. The model in a session reads what the hooks inject
before each prompt. The plant owner pays for those bytes and needs the hooks to
be honest about what they save.

**Claude Code, and Copilot through `.claude/settings.json`**

- First routed prompt of a session: the pointer line, a blank line,
  `Router suggestion (a keyword heuristic — reason over it):`, then the
  router's LOAD and NOT LOADED blocks as before. The prompt is no longer pasted
  back, and the mandate paragraph is replaced by the one pointer line (§8,
  first example).
- Later prompts: the pointer line; the router's notice lines; `New for this
  task:` with the full entry line of each node suggested now and not before in
  this session; one `Surfaced earlier this session:` line naming by id only the
  nodes suggested for this prompt that were suggested earlier, telling the
  model to open what is not in its view; and, under `Not suggested, not listed
  before (cross only if needed):`, only peers the router has not listed
  before. When nothing is new the injection is two lines (§8). No line the hook
  writes says a node was read or loaded.
- Peers listed earlier are not repeated. They return at the next full
  injection and stay reachable through `docs/graph/index.md`.
- The full injection returns after any session start (startup, resume, clear,
  compaction, fork), after `REFRESH_EVERY` routed prompts, and whenever the
  session record is missing, unreadable, expired, from another session or
  otherwise suspect, or the router output cannot be parsed after the echo is
  removed. When Copilot sends no session id, every prompt gets the full
  injection and no dedup saving.
- Trivial prompts inject nothing and are not counted. A plant with no graph
  gets the existing no-graph message. If the router fails, the model sees the
  pointer line alone. Router output that does not start with the exact echo of
  the prompt counts as a failure, so the prompt is never passed back.
- The session never blocks, because every path exits 0. When the hook falls
  back to full, it writes one line to its error output saying why, never the
  raw session id.
- For the owner: the record is a small file under `.cypress/session/`, ignored
  by git through that directory's own `.gitignore` and pruned by the hook. No
  byte saving is claimed until the scripted 20-prompt session is measured
  against the 69,408 B baseline (plan §4.7), and the measured figure is stated
  in bytes.
- One known path can leave the model with ids but no titles after context
  loss: if the reset at session start fails, reminders continue for at most
  `REFRESH_EVERY` − 1 prompts. The ids are still named, and the line still
  says to open what is out of view (§7 `RESET_NOT_WRITTEN`).

**Prime Agent**

- Every routed prompt gets the full injection, with the echo removed and the
  same pointer line. Injected text is not deduplicated on this host, and no
  saving in injected bytes is claimed.
- The `## Surfaced nodes` overlay section asks the model to keep
  `_cypress_surfaced`, a Python set in its IPython kernel, of the nodes it has
  opened, and not to open one again while its content is still in view. Any
  saving is in node bodies not re-read. It is not measured, and nothing checks
  that the model complies.
- Every Prime Agent session pays for this instruction: at most
  `OVERLAY_SECTION_MAX_BYTES` more on the eager surface, published in bytes in
  the host capability matrix.
- A model that ignores the section re-reads nodes, which costs bytes and loses
  nothing. A model that keeps the set but skips the re-open after a compaction
  can work without a node body it believes it saw. The router still names the
  id on every prompt (§7 `PRIME_SURFACED_SET_TRUSTED_WHILE_STALE`).

**Spawned agents** on either host get the same brief text as before, byte for
byte, and start with no record of their own.

The injected text has no visual interface. The accessibility floor applies
only as plain, unambiguous wording.

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Unless a contract says otherwise, each one runs the shipped
`integrations/claude-code/route-hook.py` (or `status-hook.py`) copied into
`.claude/` of a temp plant: a directory holding `.git/`, `.cypress/` and a stub
`docs/graph/graph-lint.py`. The stub prints `task: <value of its --plan=
argument>` and a blank line, then a fixed body in the §6 grammar; contracts
that need other output say so. The hook's stdin is a JSON envelope (§6). "Full
mode" and "reminder mode" are the exact texts in §6. "Stderr has one line"
means exactly one newline-ended line, and "no stderr" means empty stderr.
Every contract also requires exit code 0. Tests run with umask 022.

### Prompt echo and kernel pointer

### Contract: ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO
- **Given:** a six-line prompt whose lines are six distinct token strings that
  appear in no id or title of the minimal graph, the fourth being a sentinel,
  and the real `templates/knowledge-graph/graph-lint.py` placed at
  `docs/graph/graph-lint.py` over that minimal graph
- **When:** the hook runs
- **Then:** the injection does not contain the sentinel, nor any line of the
  prompt, nor a line beginning `task:`
- **And:** the router's `LOAD (` header is present, so the strip removed the
  echo and not the body

### Contract: ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE
- **Given:** a prompt of 8 or more characters that starts with `--` and has no
  space, and a stub router that records its argv
- **When:** the hook runs
- **Then:** the stub's argv carries exactly one argument beginning `--plan=`,
  whose value is the prompt, and the injection carries the stub's body

### Contract: ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN
- **Given:** a valid ledger, and in turn a prompt holding an embedded NUL byte
  (sent as `\u0000` in the JSON envelope) and a prompt of 2 000 000
  characters, over both Linux's per-argument limit and macOS's `ARG_MAX`
- **When:** the hook runs
- **Then:** the injection is the pointer line alone, and the ledger is
  byte-identical with an unchanged mtime
- **And:** stdout is one valid hook envelope, and no traceback reaches stderr

### Contract: ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY
- **Given:** a valid ledger, a prompt holding a sentinel token, and in turn a
  stub whose output is: the §6 body with no `task:` line; `task: ` followed by
  other text, a blank line and the body; the exact `task: <prompt>` line with
  no blank line after it
- **When:** the hook runs
- **Then:** the injection is the pointer line alone
- **And:** the sentinel appears in no injection, in no file under
  `.cypress/session/` and in no stderr line, and the ledger is byte-identical
  with an unchanged mtime

### Contract: ROUTE_HOOK_POINTS_AT_KERNEL
- **Given:** any non-trivial prompt with a graph present and the router
  answering
- **When:** the hook runs
- **Then:** the first line of the injection is the pointer line of §6, byte
  for byte

### Contract: HOOK_TEXT_RESTATES_NO_KERNEL_RULE
- **Given:** `core/AGENTS.md`, from which the check derives the cells of the §0
  "The task is…" column and the FIRST MOVE numbered steps. Both that text and
  each scanned file are normalised the same way: `\uXXXX` escapes decoded,
  markdown `*` and backticks dropped, lowercased, then split into tokens that
  are runs of `[a-z0-9]`. The whole of each scanned file is read, comments and
  docstrings included
- **When:** `tests/seed-lint.py` scans `integrations/claude-code/route-hook.py`
  and `integrations/prime-agent/route-extension.ts`
- **Then:** the check fails on any run of four or more consecutive tokens from
  those cells or steps appearing in either file (I-8)
- **And:** the check also fails on any token matching `\bT[0-3]\b` in either
  file, read case-sensitively after escapes are decoded, so a paraphrase of
  the tier table that shares no four-token run is still caught
- **And:** a planted copy of a §0 cell in a scratch hook makes the check fail,
  and so does a planted `T2`, so both rules are shown to fire

### Session ledger: first prompt, later prompts, refresh

### Contract: LEDGER_FIRST_PROMPT_FULL
- **Given:** a valid `session_id`, no ledger file, and a prompt holding a
  sentinel token
- **When:** the hook runs on that prompt
- **Then:** the injection is full mode
- **And:** the ledger exists with `prompt_count` 1, `surfaced` equal to the
  router's LOAD ids, and `peers_seen` equal to the NOT LOADED ids that are not
  in LOAD, with no stderr
- **And:** the sentinel appears in no file under `.cypress/session/` and in no
  stderr line

### Contract: LEDGER_LATER_PROMPT_REMINDER
- **Given:** the ledger left by `LEDGER_FIRST_PROMPT_FULL`, and a second prompt
  whose router output has no notice lines, whose LOAD ids are a subset of
  `surfaced`, and whose NOT LOADED ids were all seen before
- **When:** the hook runs
- **Then:** the injection is exactly two lines: the pointer line, and the
  `Surfaced earlier this session:` line of §6 naming those LOAD ids in the
  router's order

### Contract: REMINDER_KEEPS_NOTICE_LINES
- **Given:** a ledger, and a stub router whose output has `  ! <text>` notice
  lines, with the LOAD ids all in `surfaced`
- **When:** the hook runs
- **Then:** every notice line appears verbatim, straight after the pointer line

### Contract: REMINDER_SAYS_SURFACED_NEVER_LOADED
- **Given:** any reminder-mode injection, from a stub whose entry and notice
  lines do not contain the word
- **When:** it is inspected
- **Then:** it contains `Surfaced earlier this session:` wherever a known id is
  named, and no line the hook authors contains `loaded` in any letter case (I-6)
- **Note:** the router's own `LOAD` and `NOT LOADED` headers appear only in
  full mode. They are the router's recommendation vocabulary, not the hook's
  claim about what the model read, so I-6 does not reach full mode

### Contract: LEDGER_NEW_IDS_LISTED
- **Given:** a ledger, and a prompt whose LOAD set holds one id outside
  `surfaced`
- **When:** the hook runs
- **Then:** the line `New for this task: <that id>` is present, followed by
  that id's router LOAD entry line verbatim
- **And:** the ledger's `surfaced` now contains that id

### Contract: REMINDER_DROPS_PEERS_ALREADY_SHOWN
- **Given:** a ledger whose `peers_seen` holds `agent.implementer`, and a
  router NOT LOADED block naming `agent.implementer` and one unseen peer
- **When:** the hook runs in reminder mode
- **Then:** the unseen peer's entry line appears under `Not suggested, not
  listed before (cross only if needed):`, and no line naming
  `agent.implementer` appears
- **And:** the unseen peer is added to `peers_seen`

### Contract: LEDGER_EVERY_LOAD_ID_NAMED
- **Given:** one stubbed router output with a LOAD block, and in turn each of
  these ledger states: absent; `prompt_count` 0; `prompt_count` 1 with every
  LOAD id in `surfaced`; `prompt_count` 1 with one LOAD id outside `surfaced`;
  `prompt_count` equal to `REFRESH_EVERY`; unusable (invalid JSON)
- **When:** the hook injects
- **Then:** every id in the router's LOAD block appears in the injection (I-3)

### Contract: LEDGER_REFRESH_EVERY_N
- **Given:** a ledger whose `prompt_count` equals `REFRESH_EVERY`, read by
  regex from the copied `route-hook.py`, and whose `surfaced` holds the
  sentinel id `zz.refresh-sentinel`, absent from the current router output
- **When:** the next non-trivial prompt arrives
- **Then:** the injection is full mode, and the ledger's `prompt_count` is 1
  with `surfaced` and `peers_seen` rebuilt from this injection alone, so the
  sentinel is gone
- **And:** from a ledger whose `prompt_count` is `REFRESH_EVERY` − 1, the
  injection is reminder mode
- **And:** in a copy whose `REFRESH_EVERY` literal is rewritten to 3, a ledger
  at count 3 gives full mode and one at count 2 gives reminder mode

### Contract: LEDGER_TRIVIAL_PROMPT_UNTOUCHED
- **Given:** a ledger
- **When:** a trivial prompt arrives (one in the hook's `TRIVIAL` set, or under
  8 characters)
- **Then:** nothing is written to stdout and the ledger file is byte-identical
  with an unchanged mtime

### Contract: LEDGER_UNUSED_WITHOUT_GRAPH
- **Given:** a plant with `.cypress/` and no `docs/graph/graph-lint.py`, and a
  valid `session_id`
- **When:** the hook runs on a non-trivial prompt
- **Then:** the injection is the existing no-graph message, unchanged, and no
  file is created under `.cypress/session/`

### Contract: LEDGER_NEVER_EMITS_UNROUTED_ID
- **Given:** a valid ledger whose `surfaced` and `peers_seen` contain the
  sentinel id `zz.unrouted-sentinel`, which is no substring of any router
  output or fixed hook text, and whose `last_reset.source` is the sentinel
  `zz-sentinel`
- **When:** the hook runs
- **Then:** neither sentinel appears in the injection. Only ids present in the
  current router output are ever emitted (I-7: the ledger is state, never
  instructions)

### Contract: UNPARSEABLE_ROUTER_OUTPUT_FULL
- **Given:** a stub router whose output starts with the exact echo prefix and
  whose remainder has no recognisable `LOAD (` header
- **When:** the hook runs with a valid ledger
- **Then:** the injection is full mode carrying that remainder, and the ledger
  file is byte-identical with an unchanged mtime

### Session identity and fail toward inclusion (I-1)

### Contract: LEDGER_ABSENT_SESSION_ID_FULL
- **Given:** in turn, a Copilot-shaped envelope (no `session_id`, `source`
  `"new"`, an unknown extra field) and the same envelope carrying `sessionId`
  set to a value that passes the §6 session-id pattern
- **When:** the hook runs on the same prompt twice
- **Then:** both injections are full mode, no file is created under
  `.cypress/session/`, and there is no stderr, so ADR-0009's
  `CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE` stays green

### Contract: LEDGER_INVALID_SESSION_ID_FULL
- **Given:** a `session_id` from each of: `../../escape`, `a/b`, `.hidden`,
  an empty string, 129 characters of `a`, a JSON number, and a string holding
  a NUL byte
- **When:** the hook runs
- **Then:** the injection is full mode, no file is created or modified in the
  temp plant tree or its parent directory (compared by a snapshot taken before
  and after), and stderr has one line that, for each non-empty id, does not
  contain the raw id
- **And:** the id is tested against the §6 session-id pattern before any path
  is built from it

### Contract: LEDGER_CORRUPT_FULL
- **Given:** a ledger file holding, in turn: invalid JSON; valid JSON with an
  extra key; an id failing the id pattern; a `session_id` field that differs
  from the filename stem; a file over `LEDGER_MAX_BYTES`; 60 000 `[`
  characters, under `LEDGER_MAX_BYTES`, nested too deep for the JSON parser
- **When:** the hook runs
- **Then:** the injection is full mode, stderr has one line, and the file is
  replaced by a valid version-1 ledger for this session

### Contract: LEDGER_UNKNOWN_VERSION_FULL
- **Given:** an otherwise valid ledger with `version` 2
- **When:** the hook runs
- **Then:** the injection is full mode, stderr has one line, and the file is
  replaced by a valid version-1 ledger with `prompt_count` 1

### Contract: LEDGER_EXPIRED_FULL
- **Given:** a valid ledger whose mtime is older than `LEDGER_TTL`
- **When:** the hook runs
- **Then:** the injection is full mode, stderr has one line, and the file is
  replaced by a valid version-1 ledger with `prompt_count` 1

### Reset

### Contract: STATUS_HOOK_RESETS_LEDGER
- **Given:** a ledger with `prompt_count` 3, and in turn each `source` of
  `startup`, `resume`, `clear`, `compact`, `fork`, `new`, a value outside the
  §6 `reset_source` pattern, and an absent `source`
- **When:** `status-hook.py` runs with that `source` and the same `session_id`
- **Then:** the ledger has `prompt_count` 0, empty `surfaced` and
  `peers_seen`, and `last_reset.source` equal to the source, or `"unknown"`
  for a value outside the pattern and for an absent `source`
- **And:** the next non-trivial prompt gets a full injection

### Contract: STATUS_HOOK_NO_LEDGER_WRITES_NOTHING
- **Given:** a plant with a graph and `.cypress/`, and in turn a valid
  `session_id` with no ledger file, no `session_id`, and each invalid
  `session_id` of `LEDGER_INVALID_SESSION_ID_FULL`
- **When:** `status-hook.py` runs on `SessionStart`
- **Then:** no file under `.cypress/` is created or modified, and the next
  non-trivial prompt for the valid id gets a full injection

### Contract: STATUS_HOOK_RESETS_WITHOUT_REGISTER
- **Given:** a plant with a graph and a ledger, and no `status-register.py`
- **When:** `status-hook.py` runs on `SessionStart`
- **Then:** the ledger is reset as in `STATUS_HOOK_RESETS_LEDGER`, and nothing
  is written to stdout

### Contract: STATUS_HOOK_RESET_OWNS_NO_PATH_RULE
- **Given:** `integrations/claude-code/status-hook.py`
- **When:** its source is read
- **Then:** it carries neither the session-id pattern nor the string
  `.cypress/session`. It obtains `reset_ledger` from its sibling
  `route-hook.py`, so the ledger has one owner (I-4)
- **Note:** a planted `Path(root, ".cypress", "session")` passes this source
  check; `STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER` is the behavioural case
  that catches it

### Contract: STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER
- **Given:** `status-hook.py` in `.claude/` without `route-hook.py` beside it,
  a status register present, and a ledger with `prompt_count` 3
- **When:** it runs on `SessionStart`
- **Then:** the ledger is byte-identical, the status summary is still
  injected, and stderr has one line

### Persistence safety (I-7)

### Contract: LEDGER_GITIGNORED
- **Given:** the temp plant is a git repository with one commit and no
  `.gitignore`
- **When:** the hook writes a ledger
- **Then:** `.cypress/session/.gitignore` exists with content `*` and a
  newline, `git status --porcelain --untracked-files=all` lists nothing under
  `.cypress/session/`, `git check-ignore -q .cypress/session/<sid>.json`
  succeeds, and no `.gitignore` outside `.cypress/session/` was created or
  changed
- **And:** given instead a pre-existing regular `.cypress/session/.gitignore`
  holding other content, that file is byte-identical after the hook writes

### Contract: LEDGER_WRITE_IS_ATOMIC
- **Given:** an existing valid ledger, and a hard link to it in the temp plant
  root
- **When:** the hook updates the ledger
- **Then:** the ledger path's inode differs from the hard link's, the
  hard-linked file is byte-identical to the old ledger, and no file other than
  `<sid>.json` and `.gitignore` remains in `.cypress/session/`. The ledger was
  replaced, not rewritten in place
- **And:** when the replace fails (the hook run through a `runpy` wrapper that
  makes `os.replace` and `os.rename` raise `OSError`), the original ledger is
  byte-identical, no temp file remains, the injection is full mode, and stderr
  has one line. An interrupted replace leaves the old ledger intact

### Contract: LEDGER_SYMLINK_REFUSED
- **Given:** in turn:
  - `.cypress` as a symlink to a directory outside the temp plant that holds a
    `session/` directory with a valid ledger for this sid
  - `.cypress/session` as a symlink to a directory outside the temp plant
  - `.cypress/session/<sid>.json` as a symlink to an outside file holding a
    valid version-1 ledger for the same sid, with `prompt_count` 1 and
    `surfaced` equal to the LOAD ids, so following the link would give
    reminder mode
  - `.cypress/session/.gitignore` as a symlink to a file outside the temp plant
  - `.cypress/session/<sid>.json` as a FIFO
- **When:** the hook runs, under a 5 s timeout
- **Then:** it exits 0 within the timeout, every outside target is
  byte-identical with an unchanged mtime, nothing is created outside the temp
  plant, the injection is full mode, and stderr has one line

### Contract: LEDGER_FOREIGN_OR_WRITABLE_REFUSED
- **Given:** in turn, a `.cypress/session/` of mode 0777 holding a valid ledger
  that would give reminder mode, and a `.cypress/session/` of mode 0700 holding
  that ledger with mode 0666
- **When:** the hook runs
- **Then:** the injection is full mode and stderr has one line; in the first
  case nothing under `.cypress/session/` is created or modified
- **And:** in a fresh plant, the session directory the hook creates has mode
  0700 and the ledger it writes has mode 0600
- **Note:** these cases read mode bits, not access, so they run as root too. A
  ledger owned by another user needs a second account and is not in the gate
  (§11)

### Contract: LEDGER_NO_CYPRESS_DIR_NO_WRITE
- **Given:** a plant root with a graph and a `.git/` but no `.cypress/`
- **When:** the hook runs with a valid `session_id`
- **Then:** `.cypress/` is not created, the injection is full mode, and stderr
  has one line naming the path

### Contract: LEDGER_WRITE_FAILURE_FAILS_OPEN
- **Given:** in turn, `.cypress/session/` read-only (this case is skipped, and
  says so, when the suite runs as root), and the hook run through a `runpy`
  wrapper that makes `os.replace` raise `PermissionError` (this case runs as
  root too)
- **When:** the hook runs
- **Then:** the injection is full mode and stderr has one line

### Contract: LEDGER_GC_BOUNDED
- **Given:** no ledger for the current session, and in `.cypress/session/`: 40
  ledger files with mtimes older than `GC_MAX_AGE`; 40 fresh ledger files with
  distinct mtimes; 10 temp files named with `TEMP_PREFIX` and mtimes older than
  `TEMP_MAX_AGE`; a `notes.txt`; and a `bad name.json`, whose stem fails the
  session-id pattern
- **When:** the hook creates the current session's ledger
- **Then:** no ledger file older than `GC_MAX_AGE` remains; at most
  `GC_MAX_FILES` ledger files remain, the current one among them and the
  removed fresh ones being the oldest; no stale temp file remains; and
  `notes.txt`, `bad name.json` and `.gitignore` are byte-identical
- **And:** a stale temp file planted after that prompt survives the next prompt
  of the same session, which updates the ledger rather than creating it
- **And:** with 300 stale temp files present, one ledger creation removes at
  most `GC_SCAN_MAX` of them

### Spawn boundary (I-2)

### Contract: BRIEF_TEMPLATES_BYTE_IDENTICAL
- **Given:** `templates/prompts/graph-session-bootstrap.md` and
  `templates/prompts/handback-payload.md`, and the baseline revision: the 7.27.0
  release commit on the base branch, which is the parent of Slice A's first
  commit (its SHA is written into §10 at RED)
- **When:** `git diff --quiet <baseline> -- templates/prompts/graph-session-bootstrap.md templates/prompts/handback-payload.md`
  runs at verify
- **Then:** it exits 0, and `tests/seed-lint.py`'s existing GRAPH DISCIPLINE
  identity check still passes across the five embedding templates

### Prime Agent (first-class; soft dedup, structural tests)

**Enforcement class: soft**, in the vocabulary of
`adr-0003-enforcement-layering-honesty`. The surfaced set is kept by the model
because the overlay prose asks it to, and ADR-0003 §Decision counts prose an
agent reads as a soft enforcer. No harness refuses a model that ignores the
instruction, and no tool observes whether it complied. Nothing in this section
is enforced dedup, and no document may describe it as enforced.

Two host facts force this shape (§6 gives the classification and source of
each). No extension API reads or writes the IPython kernel, and no Python-side
hook runs per prompt. So `route-extension.ts` cannot see the set, and it keeps
injecting in full on every prompt. The Prime Agent saving in injected bytes is
therefore a recorded gap (§5, §11), and nothing here claims it.

The gate has no TypeScript runtime and no model in the loop, so every contract
here is pinned by reading `integrations/prime-agent/route-extension.ts` or
`integrations/prime-agent/APPEND_SYSTEM.md` as text (plan §5). The tests prove
the instruction's wording and the extension's shape. They prove nothing about
what a model does, and §10 records them at that strength. "The section" below
means the `## Surfaced nodes` section of `APPEND_SYSTEM.md`: its heading line
through the byte before the next line beginning `## `, or the end of the file.
Phrase checks are case-sensitive and run after every run of whitespace in the
section is collapsed to one space, so a line wrap cannot hide a phrase.

### Contract: ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX
- **Given:** the extension source
- **When:** it is read
- **Then:** the prefix is built as `` `task: ${prompt}\n\n` `` from the same
  `prompt` value that goes into the `--plan=` element, tested with
  `startsWith`, and removed with `slice(prefix.length)`; the remainder
  undergoes no transformation other than `trim`; and the source contains no
  `.slice(2)` or other fixed line count applied to `--plan` output
- **And:** the suggestion header and the remainder are appended to the content
  only inside the branch guarded by that `startsWith` test, so output without
  the exact prefix yields the pointer line alone (§7 `ROUTER_FAILED`)

### Contract: ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE
- **Given:** the extension source
- **When:** it is read
- **Then:** the argv is an array literal written inline in the single
  `pi.exec(` call, and it carries the prompt only inside a `--plan=` element,
  never as a separate element after `--plan`. The test fails when no such
  literal is found

### Contract: ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK
- **Given:** the pointer line and the full-mode suggestion header of §6
- **When:** both sources are read, with string-literal escapes decoded, since
  `route-extension.ts` spells non-ASCII characters as escapes: a backslash
  and `u00a7` for the section sign, a backslash and `u2014` for the dash
- **Then:** each string occurs verbatim in both `route-hook.py` and
  `route-extension.ts`, each as a single string literal with no `+`
  concatenation and no implicit concatenation, so the two surfaces cannot
  drift apart in wording

### Contract: ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE
- **Given:** the extension source, and the allowlist of module-scope names
  `TRIVIAL`, `CANDIDATES`, `findLint`, `POINTER`, `SUGGESTION_HEADER` and
  `routeExtension`
- **When:** it is read
- **Then:** every name declared on a line matching
  `^(export\s+)?(default\s+)?(async\s+)?(const|let|var|function|class)\s+(\w+)`
  is in the allowlist; no line matches `^(export\s+)?(const|let|var)\s*[\[{]`;
  the source contains no `globalThis`; it subscribes
  through `pi.on` to `before_agent_start` only; it contains none of the
  reminder-mode prefixes `Surfaced earlier this session:`, `New for this
  task:` and `Not suggested, not listed before (cross only if needed):`; and
  it calls no `pi.appendEntry` and no filesystem write (no match of
  `\bNAME\s*\(` for any NAME of `writeFile`,
  `writeFileSync`, `appendFile`, `appendFileSync`, `mkdir`, `mkdirSync`,
  `rename`, `renameSync`, `createWriteStream`, `copyFile`, `copyFileSync`,
  `cp`, `cpSync`, `open`, `openSync`, `truncate`, `truncateSync`, `symlink`,
  `symlinkSync`)
- **Note:** a consequence, not asserted: with no state, every non-trivial
  prompt with a graph takes the full-mode path, and the extension cannot hold
  a record that outlives a session in its process

### Contract: PRIME_OVERLAY_KEEPS_SURFACED_SET
- **Given:** `integrations/prime-agent/APPEND_SYSTEM.md`
- **When:** it is read
- **Then:** exactly one `## Surfaced nodes` section exists, and it contains the
  phrases `_cypress_surfaced`, `IPython kernel`,
  `surfaced earlier this session` and
  `re-open it if its content is not in view`
- **And:** the section contains neither `rlm` nor `brief`, so it never asks the
  model to hand the set to a child (I-2)

### Contract: PRIME_OVERLAY_NEVER_SAYS_LOADED
- **Given:** the section
- **When:** it is read
- **Then:** it contains no `loaded` in any letter case (I-6)
- **And:** the case fails when the section is absent, so it cannot pass on an
  empty match

### Contract: PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE
- **Given:** the §0 cells and FIRST MOVE steps that
  `HOOK_TEXT_RESTATES_NO_KERNEL_RULE` derives from `core/AGENTS.md`, under the
  same normalisation
- **When:** `tests/seed-lint.py` runs the same check over the section
- **Then:** the check fails on any run of four or more consecutive tokens from
  those cells or steps appearing in the section, or on any token matching
  `\bT[0-3]\b` in it (I-8)
- **And:** a planted copy of a FIRST MOVE step inside a scratch overlay's
  section makes the check fail, and the same copy outside the section does not

### Contract: PRIME_OVERLAY_SECTION_WITHIN_CEILING
- **Given:** the section
- **When:** its UTF-8 bytes are counted
- **Then:** the count is at most `OVERLAY_SECTION_MAX_BYTES` (§6)

### Contract: PRIME_EAGER_SURFACE_WITHIN_BUDGET
- **Given:** the overlay with the section added
- **When:** `tests/seed-lint.py` runs `check_eager_surface`
- **Then:** the prime-agent surface (kernel bytes, skill descriptions and
  overlay bytes) is at most `EAGER_BUDGET`, and
  `check_published_eager_figures` passes, so the prime-agent figures in
  `documentation/host-capability-matrix.md` equal the new computation

## 5. Non-functional requirements

- **Compatibility:** `route-hook.py` and `status-hook.py` stay stdlib
  `python3`. `route-extension.ts` adds no import.
- **Security:** the session id is read only from the exact key `session_id`
  and becomes a filename only after it passes the §6 pattern. All ledger I/O
  follows the §6 descriptor discipline: no symlink is followed, nothing is
  read before `fstat` shows a regular file, a session directory or ledger
  owned by another user or writable by group or others is refused, and
  `.gitignore` is created only when absent. The hook never creates
  `.cypress/`, since that directory marks a plant root for `_is_plant_root`.
  On both hosts the prompt reaches the router as one `--plan=` argv element
  with no shell (§6 host facts for `pi.exec`), and router output without the
  exact echo prefix is dropped rather than passed through. On Prime Agent the
  seed writes no state at all. The surfaced set lives in the host's kernel,
  and a persistent session may snapshot the kernel namespace to
  `kernel-state.dill` or `kernel-state.json` under the host's
  `session-artifacts/<root-session-id>/`, outside the plant tree (§6). The set
  holds node ids only, which are public graph identifiers. The threat model
  for this feature is written into ADR-0010 at the plan's §10 close.
- **Reliability:** every path exits 0. Once `graph-lint.py` resolves,
  `route-hook.py` emits at least the pointer line, whatever fails after. No new
  hook event is wired in `.claude/settings.json`, and `route-extension.ts`
  subscribes to no new Prime Agent event.
- **Cost:** ledger work adds no subprocess and no network call. Each routed
  prompt adds one read of at most `LEDGER_MAX_BYTES` + 1 bytes and one atomic
  write. Garbage collection runs only when a ledger is created, and reads at
  most `GC_SCAN_MAX` directory entries (plan §4.8, amended in plan §17). No
  byte saving is claimed until plan §4.7 has measured it. On Prime Agent the
  injected bytes shrink by the echo fix and the pointer line only; the dedup
  saving in injected bytes is a recorded gap. The prime-agent eager surface
  grows by the section's bytes, at most `OVERLAY_SECTION_MAX_BYTES`, paid on
  every Prime Agent session.

## 6. Data shapes

### Host envelopes read

```yaml
user_prompt_submit_stdin:      # Claude Code; Copilot sends a subset plus extras
  prompt:          { type: string }                  # or initialPrompt
  hook_event_name: { type: string, optional: true }  # or hookEventName
  session_id:      { type: string, optional: true }  # this exact key only; sessionId and other spellings are ignored
  extra fields:    ignored

session_start_stdin:
  session_id:      { type: string, optional: true }  # this exact key only
  source:          { type: string, optional: true }  # startup|resume|clear|compact|fork on Claude Code; "new" on Copilot; absent or off-pattern is stored as "unknown"

hook_stdout:                     # unchanged shape
  hookSpecificOutput:
    hookEventName:     { type: string }
    additionalContext: { type: string }              # the injection
```

### Patterns

```yaml
session_id_pattern: '^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$'   # else: no session id
node_id_pattern:    '^[a-z][a-z0-9_.-]{0,127}$'
reset_source:       '^[a-z_-]{1,32}$'                        # else stored as "unknown"
ledger_filename:    '<session_id_pattern stem>.json'
temp_filename:      '^\.tmp-[A-Za-z0-9_-]{1,64}$'            # TEMP_PREFIX plus a random suffix
```

### Ledger file, version 1 (Claude Code)

Path: `<ROOT>/.cypress/session/<session_id>.json`, where `ROOT` is the
directory `find_lint()` resolves. The session directory is created with mode
0700 and holds a `.gitignore` whose content is `*` and a newline.

```yaml
ledger:
  required: [version, session_id, prompt_count, surfaced, peers_seen, last_reset]
  additional_keys: forbidden
  fields:
    version:      { type: integer, const: 1 }
    session_id:   { type: string, equals: filename stem and stdin session_id }
    prompt_count: { type: integer, min: 0 }     # 0 = reset recorded, nothing injected since
    surfaced:     { type: array, of: node_id, sorted: true, unique: true, max: 512 }
    peers_seen:   { type: array, of: node_id, sorted: true, unique: true, max: 512 }
    last_reset:   { type: [null, object], fields: { source: reset_source, at: iso8601_utc } }
  file:
    kind: regular file, by fstat on a descriptor opened O_NOFOLLOW
    owner: st_uid == geteuid()
    mode: written 0600; unusable when mode & 0o022 != 0
    max_bytes: 65536
```

Any rule failing makes the ledger **unusable**, and an unusable ledger is
treated as absent (I-1). A parse that raises, `RecursionError` included, is a
failed rule.

**Descriptor discipline.** All ledger I/O goes through directory file
descriptors. The hook opens `<ROOT>/.cypress` with
`O_RDONLY|O_DIRECTORY|O_NOFOLLOW`, creates `session` inside it with
`mkdir(..., mode=0o700, dir_fd=...)` when absent, and opens `session` relative
to that descriptor with the same flags. Every later open, stat, replace and
unlink is relative to the session descriptor (`dir_fd=`), never a path string.
The session directory is usable only if `fstat` on its descriptor shows
`st_uid == os.geteuid()` and `st_mode & 0o022 == 0`; otherwise it is
`LEDGER_DIR_UNUSABLE`. The ledger is opened
`O_RDONLY|O_NOFOLLOW|O_NONBLOCK`; `fstat` on that descriptor must show
`S_ISREG` and pass the same owner and mode tests, and at most
`LEDGER_MAX_BYTES` + 1 bytes are read, so an oversized file is caught without
a separate stat. The temp file is created
`O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW` with mode 0600 under a `temp_filename`
name and moved into place with
`os.replace(tmp, name, src_dir_fd=fd, dst_dir_fd=fd)`; on any failure the temp
file is unlinked. `.gitignore` is created only when absent
(`O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW`) and never rewritten. When it exists and
is not a regular file, the directory is `LEDGER_DIR_UNUSABLE`. Where the
platform lacks `os.O_NOFOLLOW` or `os.O_DIRECTORY`, or `dir_fd` support for a
call the hook needs (`os.supports_dir_fd`), the ledger is
`LEDGER_DIR_UNUSABLE` and the injection is full mode. No path-string fallback
exists.

### Garbage collection

GC runs only when the hook creates a ledger, meaning no entry existed at this
session's ledger name before the write. It reads entries by iterating
`os.scandir(session_fd)` and stops after `GC_SCAN_MAX` entries; it never calls
`os.listdir`. It deletes, with `dir_fd` and
`follow_symlinks=False`, only regular files: a `ledger_filename` older than
`GC_MAX_AGE`, a `temp_filename` older than `TEMP_MAX_AGE`, and then the oldest
ledger files by mtime until at most `GC_MAX_FILES` ledger files remain. It
never deletes the current session's ledger, `.gitignore`, or any name matching
neither pattern.

### Constants

In `route-hook.py`, one home each:

| Name | Value |
|---|---|
| `LEDGER_VERSION` | 1 |
| `REFRESH_EVERY` | 10, a module-level integer literal ≥ 2. The plan §4.7 measurement record may change the value without re-opening this spec |
| `ROUTER_TIMEOUT` | 15 s, a module-level literal (`route-extension.ts` keeps its own `timeout: 15_000` in the `pi.exec` options) |
| `LEDGER_TTL` | 12 h |
| `GC_MAX_AGE` | 7 days |
| `GC_MAX_FILES` | 32 |
| `GC_SCAN_MAX` | 256 |
| `TEMP_PREFIX` | `.tmp-` |
| `TEMP_MAX_AGE` | 1 h |
| `LEDGER_MAX_BYTES` | 64 KiB |
| `SURFACED_MAX` | 512 |

In the Prime Agent structural block of `tests/test-bound-hook.sh`, its one home:

| Name | Value |
|---|---|
| `OVERLAY_SECTION_MAX_BYTES` | 512 (the proposed text below is about 350 B) |

### Router output grammar (input, not changed)

From `templates/knowledge-graph/graph-lint.py` `--plan`: the line
`task: <prompt>` and a blank line, which the hook removes as one exact prefix
built from the prompt it passed as `--plan=`; then notice lines `  ! <text>`
and a blank line when any exist; then the header
`LOAD (<n> nodes, ~<t> tokens):` and entry lines `  <id> <title>` with an
optional `   <- composed by …` suffix; then optionally a blank line, the header
`NOT LOADED (with the reason; cross only if the task requires it):` and entry
lines `  <id> <reason>`. An entry's id is its first whitespace-delimited token
and must match the node-id pattern.

Output that does not begin with that exact prefix is `ROUTER_FAILED` (§7) on
both hosts: the pointer line alone, never the raw output. The prefix check
alone suffices, because the router echoes the prompt only on its `task:` line
(`graph-lint.py:1225`). Only output that begins with the prefix and has no
recognisable `LOAD (` header after it is unparseable, which gives full mode
with the remainder.

### Injection texts (exact; the tests compare against them)

Each text below is a single string literal in each source that emits it, named
`POINTER` and `SUGGESTION_HEADER` where both sources carry it.

- **Pointer line (`POINTER`):**
  `Route first: the kernel's FIRST MOVE and §0 apply to this prompt.`
- **Full mode:** the pointer line, a blank line, the suggestion header
  (`SUGGESTION_HEADER`)
  `Router suggestion (a keyword heuristic — reason over it):`, then the
  router output with the echo prefix removed.
- **Reminder mode** (Claude Code only), in this order, each part omitted when
  empty:
  1. the pointer line;
  2. the router's notice lines, verbatim;
  3. `New for this task: <ids>`, then each of those ids' LOAD entry lines
     verbatim;
  4. `Surfaced earlier this session: <ids> — open if not in view.`;
  5. `Not suggested, not listed before (cross only if needed):`, then the NOT
     LOADED entry lines whose id is in neither `surfaced` nor `peers_seen`.

  Ids are joined with `, ` in the router's order.
- **Router failed:** the pointer line alone.

`route-extension.ts` emits full mode, router failed, and the unchanged
no-graph message. It never emits reminder mode.

### Mode decision (pure; kept apart from file I/O in the script)

```yaml
inputs:  [router_ids (load, not_loaded), ledger_or_absent, REFRESH_EVERY]
router failed when any of:       # no ledger access at all
  - graph-lint.py exits non-zero, exceeds ROUTER_TIMEOUT, or prints nothing
  - the prompt cannot be passed (NUL byte, over the OS argument limit)
  - output lacks the exact echo prefix
full when any of:
  - ledger absent or unusable
  - prompt_count == 0            # a reset was recorded
  - prompt_count >= REFRESH_EVERY
  - router output unparseable after the prefix   # the ledger is not updated
otherwise: reminder
after full:     prompt_count = 1; surfaced = load; peers_seen = not_loaded - load
after reminder: prompt_count += 1; surfaced |= load; peers_seen |= (not_loaded - surfaced)
```

Order of work in `route-hook.py`: resolve `graph-lint.py`; run the router;
build the full-mode text; then, in one guarded block, read the ledger, decide,
compose the chosen text, and write the ledger; emit. The chosen text is emitted
only when the whole block succeeds. If any step of the block fails, the
full-mode text already in hand is emitted with one stderr line, so a ledger
failure can neither drop the injection nor leave a reminder that no ledger
records.

This decision runs on Claude Code only. On Prime Agent the extension has no
ledger to decide with, so its mode is full on every routed prompt whose output
passes the prefix rule.

### Prime Agent surfaced set (model-kept, soft)

Owner decision of 2026-09-23 (grill §16). The Prime Agent record is a Python
variable in the session's IPython kernel, kept by the model and instructed by
the overlay. It replaces the module-scope `let` of the earlier draft.

```yaml
prime_surfaced_set:
  name:        _cypress_surfaced
  type:        set of str, each matching node_id_pattern
  home:        the session's IPython kernel namespace
  written_by:  the model, adding an id after it opens that node's body
  read_by:     the model, before it opens a body the router suggests
  membership_means: "surfaced earlier this session; re-open it if its content is not in view"
  membership_never_means: loaded, read, or in context now (I-6)
  lifetime:    the kernel's (see host facts below); no reset exists or is needed
  children:    an rlm() child has its own kernel, so its set starts empty (I-2)
  seed_code_access: none; no extension reads or writes it
  enforcement: soft (adr-0003-enforcement-layering-honesty)
```

A stale entry is harmless by construction of its meaning. Kernel state
survives compaction and context does not, so after a compaction the set names
ids whose content has left view. The wording tells the model to re-open those.
The set can therefore cost a read and never withholds a node: the router still
names every id on every prompt, because `route-extension.ts` always injects
in full (I-1, I-3).

The section text below is the one to ship. Its four phrases in
`PRIME_OVERLAY_KEEPS_SURFACED_SET` are normative; the implementer may reword
the rest within `OVERLAY_SECTION_MAX_BYTES`.

```markdown
## Surfaced nodes

Keep a Python set of graph node ids, `_cypress_surfaced`, in the IPython
kernel, and add each id whose node body you open. Before opening a body the
router suggests, check the set. An id in it means surfaced earlier this
session: re-open it if its content is not in view. IPython state outlives
compaction; your context does not.
```

Host facts this design rests on. Classifications are those of the Prime Agent
host research pass of 2026-09-23 (session scratchpad
`research-prime-state.md`, not snapshotted into the plant), except the
`pi.exec` row, which the security review of 2026-09-23 read from the installed
package. The other source paths are under the plant's `docs/graph/sources/raw/`.

| Fact | Class | Source |
|---|---|---|
| One IPython kernel per session, created lazily on first REPL use, a separate process from the TypeScript worker | Documented | `prime-agent-2026-09-17.txt:2724-2726`; `prime-agent-architecture-2026-09-16.md:15-27`, `:49` |
| Kernel state survives compaction; compaction touches LLM context only | Documented | `prime-agent-long-running-agents-2026-09-16.md:257`; `prime-agent-rlm-2026-09-16.md:137` |
| An `rlm()` child gets its own kernel, lazily, never the parent's | Documented | `prime-agent-architecture-2026-09-16.md:20`, `:45`; `prime-agent-2026-09-17.txt:2749`, `:2788-2801` |
| No `ExtensionAPI` method reads, writes or runs code in the kernel; `pi.exec` spawns an unrelated process | Documented (absence, checked against the full method list) | `prime-agent-2026-09-17.txt:1265-1680`, `:1529-1536` |
| `pi.exec` spawns with `shell: false` (`spawn(command, args, {shell: false})`), so the prompt in argv is not shell-parsed | Documented (source read) | installed `@earendil-works/pi-coding-agent` 0.75.3, `dist/core/exec.js:12-16`, read 2026-09-23 |
| No Python-side hook runs per prompt or at session start | Documented (absence) | `prime-agent-rlm-2026-09-16.md` core invariants; `prime-agent-skills-2026-09-16.md:132-134` |
| `session_start` reason ∈ `startup`, `reload`, `new`, `resume`, `fork` | Documented | `prime-agent-2026-09-17.txt:312-322`; `types.d.ts:416-422` per `pi-coding-agent-2026-09-17` normalized page |
| Compaction events `session_before_compact` (reason ∈ `manual`, `threshold`, `overflow`), `session_compact`, `session_compact_failed` | Documented | `prime-agent-2026-09-17.txt:502-541` |
| A persistent session may snapshot the kernel namespace to `kernel-state.dill` / `kernel-state.json` | Documented | `prime-agent-2026-09-17.txt:2736`, `:2857-2877` |
| `/resume` on a live worker reuses the same kernel process | Tentative inference | research pass §1 |
| `/new` starts a new kernel; `/fork` starts a fresh kernel | Strong inference (`/new`); Tentative inference (`/fork`) | research pass §1 |
| Whether an `rlm()` child receives the `APPEND_SYSTEM.md` overlay | not recorded | none |

The design needs none of the inferred or unrecorded rows to hold. Each outcome
leaves the model either with an empty set (it re-reads) or with a set whose
wording says to re-open what is out of view.

## 7. Failure modes

(Authored by `architect`. Security adds adversarial cases.)

Field values below are fragments and carry no closing period.

### Failure: ROUTER_FAILED
- **Trigger:** `graph-lint.py` exits non-zero, runs past `ROUTER_TIMEOUT`, or
  prints nothing; the prompt holds a NUL byte or exceeds the OS argument
  limit; the output lacks the exact echo prefix
- **Response:** the pointer line alone, exit 0, on both hosts
- **Side effects:** the ledger is byte-identical with an unchanged mtime, and
  the prompt appears in no injection, ledger file or stderr line
- **Recovery:** the next prompt tries again

### Failure: SESSION_ID_REFUSED
- **Trigger:** `session_id` present but failing the §6 pattern, a non-string
  included
- **Response:** full mode, and one stderr line that does not contain the raw id
- **Side effects:** no path is built from the id, and nothing is written
- **Recovery:** none needed, as every prompt of that session is full mode

### Failure: LEDGER_UNUSABLE
- **Trigger:** any §6 ledger rule fails: corrupt, nested past the parser's
  limit, unknown version, wrong session, expired, oversized, not a regular
  file (a symlink or a FIFO), owned by another user, or writable by group or
  others
- **Response:** full mode, and one stderr line
- **Side effects:** a fresh ledger is written atomically in its place when the
  directory is usable; a symlink at the ledger name is replaced, never followed
- **Recovery:** automatic

### Failure: LEDGER_DIR_UNUSABLE
- **Trigger:** `.cypress/` missing; `.cypress` or `.cypress/session` a symlink
  or not a directory; the session directory owned by another user or writable
  by group or others; `.cypress/session/.gitignore` present but not a regular
  file; permission denied
- **Response:** full mode, and one stderr line naming the path
- **Side effects:** nothing written, and the hook never creates `.cypress/`
- **Recovery:** none needed. Every prompt is full mode, as at 7.27.0 minus the
  echo

### Failure: RESET_NOT_WRITTEN
- **Trigger:** `status-hook.py` cannot load `reset_ledger` from its sibling, or
  the reset write fails
- **Response:** the status summary is still injected, with one stderr line
- **Side effects:** by trigger. Sibling missing: the ledger is untouched,
  because `status-hook.py` owns no path rule. Write fails: `reset_ledger`
  falls back to unlinking the file. Write and unlink both fail: a stale ledger
  stays
- **Recovery:** bounded by `REFRESH_EVERY` and `LEDGER_TTL`. This is the one
  Claude Code path where dedup can err toward omission, for at most N − 1
  prompts after a compaction. Recorded, not closed

### Failure: PRIME_MODEL_IGNORES_SURFACED_INSTRUCTION
- **Trigger:** on Prime Agent the model does not create `_cypress_surfaced`,
  does not add the ids it opens, or does not check the set before opening a
  body
- **Response:** none from the seed; nothing observes the model
- **Side effects:** extra body re-reads, and so extra context bytes. Never an
  omission: `route-extension.ts` forwards the router output with only the
  exact echo prefix removed and `trim` applied
  (`ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX`), so every routed id is named in
  full on every prompt, whatever the set holds. That holds at structural
  strength, which is the strength of every Prime Agent test
- **Recovery:** none needed. The cost is the pre-7.28.0 cost of re-reading

### Failure: PRIME_SURFACED_SET_TRUSTED_WHILE_STALE
- **Trigger:** after a compaction, a `/resume`, or any loss of context the
  kernel survives, the set names an id whose content is out of view, and the
  model skips the re-open the section asks for; or content injected into the
  session tells the model to add ids it never opened
- **Response:** none from the seed
- **Side effects:** the model works without a node body it believes it has
  seen. The router still names the id on every prompt (I-3), so the node stays
  discoverable, but the read can be missed. This is the one Prime Agent path
  toward omission
- **Recovery:** the section's wording is the only mitigation. Unlike
  `RESET_NOT_WRITTEN`, no refresh bound exists, since the extension keeps no
  count. Kept in §11 as a residual

### Failure: UNEXPECTED_EXCEPTION
- **Trigger:** any other exception in either hook or the extension
- **Response:** exit 0. Once `graph-lint.py` has resolved, `route-hook.py`
  emits at least the pointer line, and the full-mode text when the router
  output was already in hand, with one stderr line; before that, nothing.
  `status-hook.py` emits its summary when built, with one stderr line. The
  extension's outer guard returns nothing, as at 7.27.0, and its inner guard
  keeps the pointer line
- **Side effects:** none beyond an atomic write that either completed or did
  not
- **Recovery:** none needed

## 8. Examples

Stub router output, used for every example below. The ids are illustrative
node ids, not a plant's real graph. The prompt is the two lines of the echo.

```
task: tighten the ledger garbage collection
second line of the prompt

LOAD (2 nodes, ~900 tokens):
  root                         knowledge graph router
  skill.knowledge-graph        knowledge-graph authoring

NOT LOADED (with the reason; cross only if the task requires it):
  agent.implementer            peer of skill.knowledge-graph
```

Happy, first prompt, `session_id` `3b9f1c2e-5d4a-4e8b-9a61-0c7f2d8e1a44`, no
ledger. Injection (full mode):

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.

Router suggestion (a keyword heuristic — reason over it):
LOAD (2 nodes, ~900 tokens):
  root                         knowledge graph router
  skill.knowledge-graph        knowledge-graph authoring

NOT LOADED (with the reason; cross only if the task requires it):
  agent.implementer            peer of skill.knowledge-graph
```

Ledger afterwards (mode 0600):

```json
{"version": 1, "session_id": "3b9f1c2e-5d4a-4e8b-9a61-0c7f2d8e1a44",
 "prompt_count": 1, "surfaced": ["root", "skill.knowledge-graph"],
 "peers_seen": ["agent.implementer"], "last_reset": null}
```

Edge, second prompt with the same router output. Injection (reminder mode,
two lines):

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.
Surfaced earlier this session: root, skill.knowledge-graph — open if not in view.
```

Edge, third prompt whose router adds `subsystem.graph-linters` to LOAD and
`domain.frontmatter` to NOT LOADED:

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.
New for this task: subsystem.graph-linters
  subsystem.graph-linters      graph linters
Surfaced earlier this session: root, skill.knowledge-graph — open if not in view.
Not suggested, not listed before (cross only if needed):
  domain.frontmatter           peer of subsystem.graph-linters
```

Failure, `session_id` `../../escape`: full mode as in the first example, no
file created, one stderr line such as
`route-hook: session_id refused (not a safe filename); full injection`.

Failure, ledger file holding `{"version": 2, …}`: full mode, one stderr line
naming the ledger path, and the file replaced by a valid version-1 ledger with
`prompt_count` 1.

Failure, a stub whose output starts at `LOAD (` with no `task:` line: the
pointer line alone, and the ledger untouched.

Prime Agent, the same three prompts. Each injection is the full-mode text of
the first example. After the first prompt the model opens `root` and
`skill.knowledge-graph` and its kernel holds
`_cypress_surfaced == {"root", "skill.knowledge-graph"}`. On the second prompt
both ids are in the set and both bodies are in view, so it opens neither.
Then a threshold compaction summarises the early turns. The set is unchanged,
the bodies are gone from view, and on the next prompt the model re-opens
`root` because the set's meaning is "surfaced earlier, re-open if not in
view". A model that skipped the set would have opened both bodies on every
prompt, which costs bytes and loses nothing.

## 9. Acceptance criteria

(Drafted by `architect` and revised by `product`. Each criterion names the
contracts it maps to.)

- [ ] AC-1: no injection carries the user's prompt back into the session.
      Maps to ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO,
      ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE,
      ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN,
      ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY,
      ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX,
      ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE
- [ ] AC-2: per-prompt text, and the overlay section beside it, points at the
      kernel and restates none of it. Maps to ROUTE_HOOK_POINTS_AT_KERNEL,
      HOOK_TEXT_RESTATES_NO_KERNEL_RULE,
      ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK,
      PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE
- [ ] AC-3: between one full injection and the next, a node the router already
      suggested this session is named by id on the `Surfaced earlier this
      session:` line and its entry line is not repeated. No line the hook or
      the overlay section writes contains `loaded` in any letter case. Maps
      to LEDGER_FIRST_PROMPT_FULL, LEDGER_LATER_PROMPT_REMINDER,
      REMINDER_KEEPS_NOTICE_LINES, REMINDER_SAYS_SURFACED_NEVER_LOADED,
      LEDGER_NEW_IDS_LISTED, REMINDER_DROPS_PEERS_ALREADY_SHOWN,
      LEDGER_EVERY_LOAD_ID_NAMED, PRIME_OVERLAY_NEVER_SAYS_LOADED
- [ ] AC-4: each of these gives the full injection, exit 0, and at most one
      error line: no session id; an invalid session id; a ledger that is
      corrupt, of unknown version, expired, oversized or from another session;
      router output that carries the echo prefix but cannot be parsed after
      it. On Prime Agent every routed prompt is full. Maps to
      LEDGER_ABSENT_SESSION_ID_FULL, LEDGER_INVALID_SESSION_ID_FULL,
      LEDGER_CORRUPT_FULL, LEDGER_UNKNOWN_VERSION_FULL, LEDGER_EXPIRED_FULL,
      UNPARSEABLE_ROUTER_OUTPUT_FULL, ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE
- [ ] AC-5: the first routed prompt after any `SessionStart` source, and the
      first after `REFRESH_EVERY` routed prompts, gets the full injection. On
      Prime Agent the set means "surfaced earlier, re-open if not in view",
      never proof of what is in view. Maps to STATUS_HOOK_RESETS_LEDGER,
      STATUS_HOOK_NO_LEDGER_WRITES_NOTHING,
      STATUS_HOOK_RESETS_WITHOUT_REGISTER, LEDGER_REFRESH_EVERY_N,
      PRIME_OVERLAY_KEEPS_SURFACED_SET
- [ ] AC-6: the record is safe, bounded, invisible to git and never read as
      instructions. Maps to LEDGER_GITIGNORED, LEDGER_WRITE_IS_ATOMIC,
      LEDGER_SYMLINK_REFUSED, LEDGER_FOREIGN_OR_WRITABLE_REFUSED,
      LEDGER_NO_CYPRESS_DIR_NO_WRITE, LEDGER_WRITE_FAILURE_FAILS_OPEN,
      LEDGER_GC_BOUNDED, LEDGER_NEVER_EMITS_UNROUTED_ID,
      LEDGER_UNUSED_WITHOUT_GRAPH, LEDGER_TRIVIAL_PROMPT_UNTOUCHED,
      STATUS_HOOK_RESET_OWNS_NO_PATH_RULE,
      STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER,
      ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE
- [ ] AC-7: spawned workers see exactly what they saw before. Maps to
      BRIEF_TEMPLATES_BYTE_IDENTICAL, PRIME_OVERLAY_KEEPS_SURFACED_SET
- [ ] AC-8: the Prime Agent instruction stays brief and inside the eager
      budget. Maps to PRIME_OVERLAY_SECTION_WITHIN_CEILING,
      PRIME_EAGER_SURFACE_WITHIN_BUDGET
- [ ] AC-9: the scripted 20-prompt session (`measure/prompts.json`) runs
      through the Slice A hook with `REFRESH_EVERY` set to 5, 10 and 20, each
      once without resets and once with `--resets 8,15`. Plan §14 records the
      six totals and the injected bytes of every prompt, beside the 69,408 B
      baseline. In every run:
      - (a) the total is below 69,408 B;
      - (b) the first prompt after each reset, and each refresh prompt, is
        full mode;
      - (c) the reminder-mode prompts together inject fewer bytes than the
        full-mode text of the same router outputs;
      - (d) no prompt carries prompt text.

      The Claude Code saving published in `CHANGELOG.md` is the recorded
      figure for the chosen N, in bytes. The evidence is the plan §4.7 verify
      record, not a §10 test. Maps to LEDGER_LATER_PROMPT_REMINDER,
      LEDGER_REFRESH_EVERY_N, STATUS_HOOK_RESETS_LEDGER,
      ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO
- [ ] AC-10: Prime Agent is described as soft everywhere: `CHANGELOG.md`, the
      host capability matrix row and ADR-0010 call the surfaced set
      model-kept and unenforced, claim no injected-byte saving for Prime
      Agent, and state the eager-surface increase in bytes. The wording half
      is checked by the reviewer at verify and has no automated test. Maps to
      ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE,
      PRIME_OVERLAY_SECTION_WITHIN_CEILING, PRIME_EAGER_SURFACE_WITHIN_BUDGET
- [ ] AC-11: reminder mode drops nothing the model needs to navigate: every
      LOAD id, every notice line, and the entry line of every id new to this
      session. Maps to REMINDER_KEEPS_NOTICE_LINES,
      LEDGER_EVERY_LOAD_ID_NAMED, LEDGER_NEW_IDS_LISTED

## 10. Test mapping

(Drafted by `architect`; `tester` owns this table and fills the test names.)

At RED (2026-09-23) every contract has a test and every row names it. A row
is `red` where its case was run and observed failing for the missing behaviour,
and `green` where the case passes on arrival and was shown able to fail by a
reverted scratch mutation (named in the row). `tests/seed-lint.py`
`check_spec_test_mapping` binds each `tests/*.sh` row by the label that opens
its Test case cell, which the cited file contains.

Binding, fixed at this revision (tester R22):

- Rows citing `tests/test-bound-hook.sh` use the fixed-width labels `X101` to
  `X143` reserved below, one per contract. Each case's OK line reads
  `X1NN <SLUG>: … — OK`, so both the label and the slug appear in that case.
  Fixed width keeps one label from matching inside another. When the case is
  written, the row gets the bare path.
- Rows citing `tests/test-seed-lint.sh` use `X201` and `X202` the same way.
- Rows citing `tests/seed-lint.py` carry exactly the bare function name in the
  Test case cell, and nothing else, once the row leaves `pending`. Any text
  after the name makes `_spec_green_rows` fall back to a search of the whole
  file, so the notes for these rows sit in the Level cell. Already written that
  way below. `check_spec_rows_name_their_contract` then looks for the
  slug inside that function and requires an assertion there (`fail(` counts),
  so `check_hook_text_restates_no_kernel_rule` names both of its slugs,
  `check_eager_surface` names `PRIME_EAGER_SURFACE_WITHIN_BUDGET`, and `check` (the function that
  holds the GRAPH DISCIPLINE identity check; this bullet read `main` until RED)
  names `BRIEF_TEMPLATES_BYTE_IDENTICAL` beside it.
- The RED commit that moves this spec to `active` carries all 45 slugs in
  `tests/`. Fewer would fail `SPEC_UNCOVERED_BUDGET`, which `ratchets.json`
  holds ceiling-only.
- `tests/check-coverage-binder.py` forces one `# exercises:` marker per check,
  so the second planted case of `check_hook_text_restates_no_kernel_rule` (the
  overlay, `X202`) is enforced by this table alone.

Placement follows plan §8 and the orchestrator's decision of 2026-09-23 (§11):
after 7.27.0, `tests/test-bound-hook.sh` holds every Claude Code hook contract,
and its Copilot fail-open section is the one these cases extend. The Prime
Agent structural cases, overlay included, go in one Python block in that same
file, in the style of the resolver read at `tests/test-install-placement.sh:835`.
No new test file is named. Every Prime Agent row is at structural strength: it
reads text and observes no model.

Techniques the cases rely on:

- `REFRESH_EVERY` and `ROUTER_TIMEOUT` are read by regex from the copied hook.
  `X113` also rewrites the copy's `REFRESH_EVERY` literal to 3 and asserts the
  refresh happens at 3. `X142` rewrites `ROUTER_TIMEOUT` to 1 against a stub
  that sleeps 3 s, so the timeout branch runs without a 15 s wait.
- Fault injection (`X129`, `X133`) runs the hook through a `runpy` wrapper that
  patches `os.replace` and `os.rename`, so it works as root.
- Only the read-only-directory case of `X133` skips as root, and it says so.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO | X101 | tests/test-bound-hook.sh | integration | red |
| ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE | X102 | tests/test-bound-hook.sh | integration | red |
| ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN | X103; red on arrival (no pointer line yet); the spec's mutation (router call moved outside the guard) was also run against a scratch GREEN and fails it | tests/test-bound-hook.sh | integration | red |
| ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY | X104 | tests/test-bound-hook.sh | integration | red |
| ROUTE_HOOK_POINTS_AT_KERNEL | X105 | tests/test-bound-hook.sh | integration | red |
| HOOK_TEXT_RESTATES_NO_KERNEL_RULE | check_hook_text_restates_no_kernel_rule | tests/seed-lint.py | unit; a new check, entered in COVERED in tests/check-coverage-binder.py; red: the check does not exist yet, so X201 draws no finding and the binder names it | red |
| HOOK_TEXT_RESTATES_NO_KERNEL_RULE | X201; planted §0 cell and planted `T2`, tagged `# exercises: check_hook_text_restates_no_kernel_rule` | tests/test-seed-lint.sh | integration | red |
| LEDGER_FIRST_PROMPT_FULL | X106 | tests/test-bound-hook.sh | integration | red |
| LEDGER_LATER_PROMPT_REMINDER | X107 | tests/test-bound-hook.sh | integration | red |
| REMINDER_KEEPS_NOTICE_LINES | X108 | tests/test-bound-hook.sh | integration | red |
| REMINDER_SAYS_SURFACED_NEVER_LOADED | X109 | tests/test-bound-hook.sh | integration | red |
| LEDGER_NEW_IDS_LISTED | X110 | tests/test-bound-hook.sh | integration | red |
| REMINDER_DROPS_PEERS_ALREADY_SHOWN | X111 | tests/test-bound-hook.sh | integration | red |
| LEDGER_EVERY_LOAD_ID_NAMED | X112; the six ledger states of the contract | tests/test-bound-hook.sh | integration | red |
| LEDGER_REFRESH_EVERY_N | X113; constant read by regex, copy rewritten to 3 | tests/test-bound-hook.sh | integration | red |
| LEDGER_TRIVIAL_PROMPT_UNTOUCHED | X114; green on arrival; RED shown by mutation (trivial-prompt early return removed) | tests/test-bound-hook.sh | integration | green |
| LEDGER_UNUSED_WITHOUT_GRAPH | X115; green on arrival; RED shown by mutation (no-graph path creating a file under `.cypress/session/`) | tests/test-bound-hook.sh | integration | green |
| LEDGER_NEVER_EMITS_UNROUTED_ID | X116; green on arrival; RED shown by mutation (ledger content appended to the injection) | tests/test-bound-hook.sh | integration | green |
| UNPARSEABLE_ROUTER_OUTPUT_FULL | X117 | tests/test-bound-hook.sh | integration | red |
| LEDGER_ABSENT_SESSION_ID_FULL | X118; extends the CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE section; red on arrival (no pointer line yet) | tests/test-bound-hook.sh | integration | red |
| LEDGER_INVALID_SESSION_ID_FULL | X119; tree snapshot before and after | tests/test-bound-hook.sh | integration | red |
| LEDGER_CORRUPT_FULL | X120 | tests/test-bound-hook.sh | integration | red |
| LEDGER_UNKNOWN_VERSION_FULL | X121 | tests/test-bound-hook.sh | integration | red |
| LEDGER_EXPIRED_FULL | X122 | tests/test-bound-hook.sh | integration | red |
| STATUS_HOOK_RESETS_LEDGER | X123 | tests/test-bound-hook.sh | integration | red |
| STATUS_HOOK_NO_LEDGER_WRITES_NOTHING | X124 | tests/test-bound-hook.sh | integration | red |
| STATUS_HOOK_RESETS_WITHOUT_REGISTER | X125 | tests/test-bound-hook.sh | integration | red |
| STATUS_HOOK_RESET_OWNS_NO_PATH_RULE | X126; source assertion | tests/test-bound-hook.sh | unit | red |
| STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER | X127 | tests/test-bound-hook.sh | integration | red |
| LEDGER_GITIGNORED | X128 | tests/test-bound-hook.sh | integration | red |
| LEDGER_WRITE_IS_ATOMIC | X129; hard link, and fault injection through `runpy` | tests/test-bound-hook.sh | integration | red |
| LEDGER_SYMLINK_REFUSED | X130; five cases under a 5 s timeout | tests/test-bound-hook.sh | integration | red |
| LEDGER_FOREIGN_OR_WRITABLE_REFUSED | X131; runs as root too | tests/test-bound-hook.sh | integration | red |
| LEDGER_NO_CYPRESS_DIR_NO_WRITE | X132; red on arrival (no pointer line, no stderr line yet) | tests/test-bound-hook.sh | integration | red |
| LEDGER_WRITE_FAILURE_FAILS_OPEN | X133; chmod case skipped as root, and says so; `runpy` case runs as root | tests/test-bound-hook.sh | integration | red |
| LEDGER_GC_BOUNDED | X134 | tests/test-bound-hook.sh | integration | red |
| BRIEF_TEMPLATES_BYTE_IDENTICAL | check | tests/seed-lint.py | verify gate; the slug sits in a comment beside the existing GRAPH DISCIPLINE identity check in `check` (not `main`, which holds no such check), and the verify record is `git diff --quiet ac61a3f -- templates/prompts/graph-session-bootstrap.md templates/prompts/handback-payload.md`, where `ac61a3f` is the 7.27.0 release commit, the parent of Slice A's first commit. Green on arrival (exit 0 at RED); RED shown by mutation (a byte appended to either template gives exit 1, and a drifted embedded block fails the identity check) Row held at `pending`, not `green`: `check_spec_rows_name_their_contract` cannot bind a green row to a top-level seed-lint function (its `^\s*def NAME\b` match starts on the blank line above the def, so the scope it searches is one newline). Reported at RED as a gate defect; the row moves to green when that is fixed | pending |
| ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX | X135; structural | tests/test-bound-hook.sh | unit | red |
| ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE | X136; structural; fails when no inline argv literal is found | tests/test-bound-hook.sh | unit | red |
| ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK | X137; structural, escapes decoded, single literals | tests/test-bound-hook.sh | unit | red |
| ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE | X138; structural; red on arrival (module-scope `MANDATE`). Mutations run against a scratch GREEN: a module-scope `const SEEN = new Set<string>()` and a `pi.on("session_start", …)` each turn it red | tests/test-bound-hook.sh | unit | red |
| PRIME_OVERLAY_KEEPS_SURFACED_SET | X139; structural, reads `integrations/prime-agent/APPEND_SYSTEM.md`, case-sensitive | tests/test-bound-hook.sh | unit | red |
| PRIME_OVERLAY_NEVER_SAYS_LOADED | X140; structural; fails on an absent section | tests/test-bound-hook.sh | unit | red |
| PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE | check_hook_text_restates_no_kernel_rule | tests/seed-lint.py | unit; the same check, extended to the section; red: the check does not exist yet | red |
| PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE | X202; planted case in a scratch overlay's section | tests/test-seed-lint.sh | integration | red |
| PRIME_OVERLAY_SECTION_WITHIN_CEILING | X141; structural; holds `OVERLAY_SECTION_MAX_BYTES` | tests/test-bound-hook.sh | unit | red |
| PRIME_EAGER_SURFACE_WITHIN_BUDGET | check_eager_surface | tests/seed-lint.py | unit; an existing check, run with check_published_eager_figures; green on arrival, and red on the section's arrival until the matrix figures are updated. RED shown by mutation (the overlay grown in a scratch copy fails the published-figures check) Row held at `pending`, not `green`: `check_spec_rows_name_their_contract` cannot bind a green row to a top-level seed-lint function (its `^\s*def NAME\b` match starts on the blank line above the def, so the scope it searches is one newline). Reported at RED as a gate defect; the row moves to green when that is fixed | pending |
| ROUTER_FAILED | X142; non-zero exit, empty output, and timeout with `ROUTER_TIMEOUT` rewritten to 1 | tests/test-bound-hook.sh | integration | red |
| SESSION_ID_REFUSED | X119, the case of LEDGER_INVALID_SESSION_ID_FULL | tests/test-bound-hook.sh | integration | red |
| LEDGER_UNUSABLE | X120, X121, X122, X130 (file symlink and FIFO) and X131, the cases of the contracts named there | tests/test-bound-hook.sh | integration | red |
| LEDGER_DIR_UNUSABLE | X130, X131 and X132, the cases of the contracts named there | tests/test-bound-hook.sh | integration | red |
| RESET_NOT_WRITTEN | X143, for the write-fails trigger; the sibling-missing trigger is X127 | tests/test-bound-hook.sh | integration | red |
| PRIME_MODEL_IGNORES_SURFACED_INSTRUCTION | no test; model behaviour, soft (§11). The no-omission half rests on ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX and ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE | — | — | pending |
| PRIME_SURFACED_SET_TRUSTED_WHILE_STALE | no test; model behaviour (§11) | — | — | pending |
| UNEXPECTED_EXCEPTION | no test; covered only by the fail-open cases above | — | — | pending |

Existing tests that must change in the same commit as the RED cases (plan §9):
`tests/test-tier-lanes.sh` drops `route-hook.py` and `route-extension.ts` from
its "contained" list, because the pointer line no longer restates the tier
table (this is `HOOK_TEXT_RESTATES_NO_KERNEL_RULE` working, and the kernel
itself stays asserted at `:66`); `tests/test-nested-checkout.sh` gains one
assertion that `status-hook.py`'s sibling load still resolves inside the plant.
The commit that adds the overlay section also updates the prime-agent figures
in `documentation/host-capability-matrix.md` (`:93`, `:370`, held by
`check_published_eager_figures`) and in `README.md` (`:50`, `:338`, which that
check does not match, §11).

## 11. Open questions

Every row is resolved, a residual, or an Unknown. None blocks the move to
`active`.

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Draft status against `tests/seed-lint.py` `check_spec_test_mapping`, which fails every `docs/specs/SPEC-*.md` whose status is outside `active`, `implemented`, `back-written` | Landed as `draft`, this file would turn the full gate red | **Resolved 2026-09-23 (orchestrator):** the file stays uncommitted in the worktree until the commit that lands its RED cases and moves it to `active`. No `seed-lint` change | orchestrator | resolved |
| The name of Prime Agent's compaction event | The earlier draft subscribed to it to reset a module-scope ledger | **Resolved 2026-09-23 and moot.** The host research pass classes `session_before_compact` (reason `manual`, `threshold`, `overflow`), `session_compact` and `session_compact_failed` as Documented (§6). The extension now subscribes to no session event, and the kernel set needs no reset | architect | resolved |
| Whether `session_start` fires before the extension registers its handler | The earlier draft armed its ledger there | **Moot:** the extension holds no state (`ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE`) | architect | resolved |
| Whether `rlm()` children share the extension module instance with the parent | Shared state would judge one context against another's record | **Moot for state:** the extension holds none, and a child's kernel is its own (Documented, §6) | architect | resolved |
| Whether an `rlm()` child receives the `APPEND_SYSTEM.md` overlay | Decides whether a child keeps a set of its own | not recorded. Either answer keeps I-2: the child starts with an empty set or none, and re-reads what it needs | architect | Unknown; not needed for this spec |
| Whether a model on Prime Agent follows the section's instruction | The whole Prime Agent saving depends on it, and the stale-set omission path (`PRIME_SURFACED_SET_TRUSTED_WHILE_STALE`) is closed by wording alone | not measured. No eval of model behaviour on Prime Agent exists. Non-compliance costs re-reads; only a model that trusts a stale set risks a missed read | owner | residual; an eval over Prime Agent sessions, not planned |
| Model-side suppression on Prime Agent (security review) | Prompt-injected content can tell the model to fill `_cypress_surfaced` with ids it never opened | soft, and bounded by the full injection on every prompt, which still names every routed id (§7 `PRIME_SURFACED_SET_TRUSTED_WHILE_STALE`) | security | residual |
| The spawn-boundary claim for Claude Code hooks | I-2 rests on hooks not crossing into a spawn (`status-hook.py:13-15`) | taken from the hook's own docstring. The tester found no existing test of hooks at the spawn boundary (2026-09-23), so the test is not recorded, and this spec adds none | tester | residual |
| No behavioural test for `route-extension.ts` or the overlay | The nine Prime Agent structural contracts prove text and shape, not behaviour of the extension or the model | accepted at structural strength, as plan §5 records | owner | residual; a TypeScript runtime in the gate, not planned |
| The prime-agent eager figure in `README.md:50` and `:338` | `check_published_eager_figures` matches only a figure followed by `B` or `bytes`, and these two lines carry none, so they can go stale with the gate green | updated by hand in the commit that adds the section | implementer | residual; a check change is outside this spec |
| A ledger or session directory owned by another user | The owner test of §6 has no gate case, since it needs a second account | the mode cases run in the gate (`LEDGER_FOREIGN_OR_WRITABLE_REFUSED`); the owner half is shown by reading the code at review | security | residual |
| A future `st_nlink == 1` rule on the ledger | `LEDGER_WRITE_IS_ATOMIC` (X129) hard-links the old ledger, which gives it `st_nlink` 2, so such a rule would make that ledger unusable and change what X129 observes | no link-count rule exists today. Any change that adds one must also change X129's Given | architect | residual |
| The Claude Code default hook timeout | If the host kills the hook first, nothing is injected, not even the pointer line | not recorded. The seed sets none; `ROUTER_TIMEOUT` is 15 s and GC is bounded by `GC_SCAN_MAX` (plan §4.8, §11) | reliability | Unknown |
| The reminder header, renamed in the first draft from the plan's `Not loaded, not listed before:` to `Peers not listed before:` | The plan's header contained "loaded", which contradicts I-6; the first rename lost the router's "not suggested" meaning | **Resolved, product 2026-09-23:** renamed to `Not suggested, not listed before (cross only if needed):` so the header keeps the router's "not suggested" meaning | product | resolved |
| The reminder tail on Claude Code | On Claude Code "surfaced" means suggested, not opened, so "re-open" assumed a read | **Resolved, product 2026-09-23 (optional C6, taken):** `— open if not in view.` on Claude Code; the Prime Agent section keeps "re-open", where membership does mean the model opened the node | product | resolved |
| Router output without the exact echo prefix | Passing it through re-injects the prompt, which may hold pasted secrets (AC-1) | **Resolved, orchestrator 2026-09-23:** `ROUTER_FAILED`, the pointer line alone, never raw output. Only a present prefix followed by a missing `LOAD (` header gives full mode with the remainder (`ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY`) | orchestrator | resolved |
| `SessionStart` with no ledger, and an absent `source` | A test could not decide either case | **Resolved, orchestrator 2026-09-23:** nothing is written, so the next prompt finds no ledger and gets full mode (`STATUS_HOOK_NO_LEDGER_WRITES_NOTHING`); an absent `source` is stored as `"unknown"` | orchestrator | resolved |
| Test home and row binding strength | A `.sh` row binds to a label anywhere in the file; the tester recommended a Python unittest module so each `def test_<slug>` binds by function | **Resolved, orchestrator 2026-09-23:** the cases stay in `tests/test-bound-hook.sh` with the fixed-width labels of §10 (`X101` on; `X201` on in `tests/test-seed-lint.sh`). No new test module, because the harvest forbids new gate files and a new module would need a new `run.sh` step | orchestrator | resolved |
| `REFRESH_EVERY` final value | Contracts use the constant, not the number. Claude Code only | **Resolved, orchestrator 2026-09-23:** a module-level integer literal ≥ 2, set to 10. The plan §4.7 measurement record may change the value without re-opening this spec | orchestrator | resolved |
| `OVERLAY_SECTION_MAX_BYTES` final value | Bounds what every Prime Agent session pays for the section | **Resolved, orchestrator 2026-09-23:** 512, against a section text of about 350 B | orchestrator | resolved |
| The threat model security owes for this feature | Security's charter asks for one; the review was read-only | **Resolved, orchestrator 2026-09-23:** written as part of ADR-0010 at the plan's §10 close | security | resolved |
| The baseline revision of `BRIEF_TEMPLATES_BYTE_IDENTICAL` | A hard-coded sha256 would forbid every later legitimate edit | **Resolved, orchestrator 2026-09-23:** the 7.27.0 release commit on the base branch, the parent of Slice A's first commit. The orchestrator writes its SHA into §10 at RED | orchestrator | resolved |

## 12. Changelog

- 2026-09-23: created in `draft` from docs/plans/grill-7.28.0-context-residency.md
  §3, §4, §5, §8, with the owner decisions of 2026-09-23 applied: the hook
  contracts live here (plan §13.4); Prime Agent gets an in-memory ledger reset
  on `session_start` and compaction, replacing the plan's recorded gap (plan
  §13.1); reset on every `SessionStart` source (plan §13.2); reminder mode
  drops NOT LOADED lines already shown (plan §13.7). Against the plan, the
  reminder header reads `Peers not listed before:` (I-6), invalid session ids,
  corrupt, unknown-version and expired ledgers each write one stderr line, and
  a full injection rebuilds `surfaced` and `peers_seen` from itself. Contracts
  added beyond plan §4.3: `HOOK_TEXT_RESTATES_NO_KERNEL_RULE` (moved in from
  plan §8), `REMINDER_SAYS_SURFACED_NEVER_LOADED`,
  `REMINDER_DROPS_PEERS_ALREADY_SHOWN`, `LEDGER_WRITE_IS_ATOMIC`,
  `STATUS_HOOK_RESET_OWNS_NO_PATH_RULE`, `LEDGER_UNUSED_WITHOUT_GRAPH`,
  `BRIEF_TEMPLATES_BYTE_IDENTICAL`, and the seven `ROUTE_EXTENSION_*`
  contracts.
- 2026-09-23, revision in `draft`, owner decision on Prime Agent after the host
  research pass (grill §16). The Prime Agent record is a Python variable,
  `_cypress_surfaced`, in the session's IPython kernel, kept by the model under
  a new `## Surfaced nodes` section of `APPEND_SYSTEM.md`. Its enforcement class
  is soft. `route-extension.ts` keeps no state and injects in full on every
  prompt, so its injection-byte saving is a recorded gap. Removed:
  `ROUTE_EXTENSION_LEDGER_IS_IN_MEMORY`,
  `ROUTE_EXTENSION_RESETS_ON_SESSION_START`,
  `ROUTE_EXTENSION_RESETS_ON_COMPACTION`,
  `ROUTE_EXTENSION_FULL_UNTIL_SESSION_START`, and the failure
  `PRIME_RESET_EVENT_MISSED`. Added: `ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE`,
  `PRIME_OVERLAY_KEEPS_SURFACED_SET`, `PRIME_OVERLAY_NEVER_SAYS_LOADED`,
  `PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE`,
  `PRIME_OVERLAY_SECTION_WITHIN_CEILING`, `PRIME_EAGER_SURFACE_WITHIN_BUDGET`,
  and the failures `PRIME_MODEL_IGNORES_SURFACED_INSTRUCTION` and
  `PRIME_SURFACED_SET_TRUSTED_WHILE_STALE`.
  `ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK` now compares the pointer line and
  the full-mode header only, with escapes decoded. AC-8 added; AC-5 restated.
  §11 rows 1 to 4 resolved, the draft-status row by the orchestrator's
  decision that this file stays uncommitted until its RED commit moves it to
  `active`. Prose-lint repairs: §7 field values lost their closing periods, and
  the §3 and §9 attribution lines no longer repeat.
- 2026-09-23, revision in `draft` after the first sign-off round (product,
  security, tester), with the orchestrator's decisions on the points the
  reviews left open. Contracts: 39 before, 45 after. Plan §17 records what
  this changes in the plan.
  - Product: §3 replaced with product's text (C1), with the C6 tail and the
    exact-echo rule folded in. AC-3, AC-4 and AC-5 replaced, and AC-9, AC-10
    and AC-11 added (C2, C5). The reminder header is now `Not suggested, not
    listed before (cross only if needed):` in §4, §6 and §8 (C3). Added
    `REMINDER_KEEPS_NOTICE_LINES` (C5). The Claude Code reminder tail is
    `— open if not in view.`, and Prime Agent keeps "re-open" (C6). C1 to C3
    have landed; the product box awaits product's own tick (C4).
  - Security: descriptor-relative ledger I/O, create-only `.gitignore`, and
    the extended `LEDGER_SYMLINK_REFUSED` and `LEDGER_GITIGNORED` (F1). Owner
    and mode checks, and `LEDGER_FOREIGN_OR_WRITABLE_REFUSED` (F2). Output
    without the exact echo prefix is `ROUTER_FAILED`, with
    `ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY` and the sentinel check in
    `LEDGER_FIRST_PROMPT_FULL` (F3). GC bounded by `GC_SCAN_MAX`, temp files
    swept after `TEMP_MAX_AGE`, GC only on ledger creation, and a wider
    `LEDGER_GC_BOUNDED` (F4). `ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN` and the
    wider `ROUTER_FAILED` trigger (F5). `session_id` from the exact key only
    (F6). The `pi.exec` `shell: false` host fact (F7). The pointer line on
    every path after `graph-lint.py` resolves, the ledger work in its own
    guarded block, and the deep-nesting case (F8). The owed threat model goes
    into ADR-0010; model-side suppression on Prime Agent is a §11 residual.
  - Tester: R1 to R22 applied to §4, §6, §7 and §10. Split out of existing
    contracts: `STATUS_HOOK_NO_LEDGER_WRITES_NOTHING` (R9) and
    `STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER` (R10). `ROUTER_TIMEOUT` added
    (R16). The brief-template baseline is a git revision (R17). §10 reserves
    the labels `X101` to `X143`, `X201` and `X202` (R22). Also taken from the
    tester's optional list: case-sensitive overlay phrases, replacement
    asserted for unknown-version and expired ledgers, and no ledger update on
    unparseable output.
  - §11: every open row is resolved, a residual, or an Unknown. The architect
    box is ticked; product, tester and security tick theirs in a follow-up
    pass.
- 2026-09-23, final pass in `draft` after the reviewers' re-check. Contracts:
  45, unchanged. Status stays `draft` until the RED commit.
  - Sign-offs: product signed on its re-check; security signed on its
    re-check; tester signed on its re-check, conditional on E1 to E3 as
    applied here. All four boxes in §0 are ticked.
  - Security S1: the prompt-containment rule is retracted. A remainder that
    contains the prompt is no longer a router failure (§6 grammar, mode
    decision, §7 `ROUTER_FAILED`); the fourth case of
    `ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY` and the `includes(prompt)`
    discard in `ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX` are dropped. The rule
    fired on ordinary short prompts that are substrings of node ids
    (`canonize` in `protocol.canonize`, `graph-lint` in
    `subsystem.graph-linters`) and suppressed routing, against I-1. The exact
    prefix check alone suffices, since the router echoes the prompt only on
    its `task:` line (`graph-lint.py:1225`).
  - Security S2: GC iterates `os.scandir(session_fd)` and stops at
    `GC_SCAN_MAX`, never `os.listdir` (§6).
  - Security S3: a platform without `os.O_NOFOLLOW`, `os.O_DIRECTORY` or the
    needed `dir_fd` support makes the ledger `LEDGER_DIR_UNUSABLE`, with no
    path-string fallback (§6).
  - Tester E1: the oversized prompt in `ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN`
    is 2 000 000 characters, over both Linux's per-argument limit and macOS's
    `ARG_MAX`, since the gate runs on ubuntu-latest and macos-latest.
  - Tester E2: `ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE` also refuses a
    destructuring declaration at module scope.
  - Tester E3: the four `tests/seed-lint.py` rows carry exactly the bare
    function name in the Test case cell, with their notes moved to the Level
    cell, and the §10 binding bullet says so.
  - Tester E4: not applied. It guarded the containment rule that S1 retracts.
  - §10 X138 corrected: RED on arrival, not green, because today's
    module-scope `MANDATE` is outside the allowlist and `POINTER` and
    `SUGGESTION_HEADER` do not exist yet.
  - §11: a residual row records that X129's hard link gives the ledger
    `st_nlink` 2, so any future `st_nlink == 1` rule must change X129's Given.
- 2026-09-23, RED (tester). Status `draft` → `active`, with `status_evidence`.
  Every contract has a test: `X101`–`X143` in `tests/test-bound-hook.sh`
  (two Python blocks, Claude Code hooks and Prime Agent structural), `X201` and
  `X202` in `tests/test-seed-lint.sh`, slug comments beside the identity check
  in `check` and in `check_eager_surface`, and
  `check_hook_text_restates_no_kernel_rule` entered in COVERED. §10 rows moved
  from `pending` to `red` or `green` as observed, except the two
  green-on-arrival `tests/seed-lint.py` rows, held at `pending` because the
  gate cannot bind a green row to a top-level seed-lint function (reported). The
  BRIEF_TEMPLATES_BYTE_IDENTICAL baseline is `ac61a3f`. §10's binding bullet
  and that row named `main`; the GRAPH DISCIPLINE identity check lives in
  `check`, so both now say `check`. `tests/test-tier-lanes.sh` dropped the two
  hooks from its "contained" list and `tests/test-nested-checkout.sh` gained
  the sibling-reset assertion (plan §9).
