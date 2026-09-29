---
status: active
status_date: 2026-09-29
owner: architect
status_evidence: tests/test-prompt-hooks.sh, tests/test-code-anchor.sh, tests/test-seed-lint.sh, tests/seed-lint.py, tests/test-nested-checkout.sh, tests/test_graph_lint.py (RED landed with this promotion; §10 says which rows are red)
---

# SPEC-0003: per-prompt injection

## 0. Metadata

- **Identifier:** SPEC-0003-per-prompt-injection
- **Status:** see frontmatter (single home)
- **Sign-offs:** product [x] · architect [x] · tester [x] · security [x]
  Each role signed on its own re-check of 2026-09-23; the tester's sign is
  conditional on E1 to E3 as applied here (§12).
  Amended 2026-09-29 by the architect (test consolidation, §12): two contracts
  retired, one rewritten, fixture clauses narrowed. The sign-offs above
  predate the amendment and were not re-taken.

- **Owner:** architect
- **Date:** 2026-09-23
- **Last reviewed:** 2026-09-23
- **Related grill section:** docs/plans/grill-7.28.0-context-residency.md §3, §4, §5, §8, §16, §17
- **Related ADRs:** adr-0003-enforcement-layering-honesty (the enforcement classes); adr-0009-host-support-tiers; adr-0010-context-residency (the Residency Rule and this spec's threat model)
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

Since 7.32.0 the spec also covers two additions on the hooks already wired.
The router's entry line names each node's file beside its id, and the hooks
pass it through. At session start, `status-hook.py` and `status-extension.ts`
inject the one line that `docs/graph/code-anchor.py --compare` prints, which
says whether code moved since canonize recorded `.cypress/anchor.json`
(ADR-0018).

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
  - since 7.32.0, the path column of the router's entry line, which the hooks
    pass through, while the ledger still stores ids only
  - since 7.32.0, the code-anchor line at session start, and
    `.cypress/anchor.json`, which `code-anchor.py --record` writes at canonize
    and a hook reads, under the same persistence rules as the ledger (I-7)
  - the invariants the plan names I-1, I-2, I-3, I-6, I-7 and I-8, as far as
    a test can observe them
- **Out of scope:**
  - the router's ranking. Its output format is out of scope except the path
    column of the entry line (7.32.0); the rest is parsed as it is
  - the status summary text of `status-hook.py` and `status-extension.ts`.
    Only the ledger reset and, since 7.32.0, the code-anchor line are added
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
  - opencode's code-anchor line. It has no hook, so it reads the line canonize
    writes into the newest session record, and no contract here covers it
  - codex and github-copilot, frozen by ADR-0009, which get nothing new. The
    only Copilot obligation is that the Claude Code hook keeps failing open on
    its envelope. Copilot runs `status-hook.py` through
    `.claude/settings.json`, so it also sees the code-anchor line
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
- **Given:** a valid ledger, and a prompt holding an embedded NUL byte (sent
  as `\u0000` in the JSON envelope), which no argv can carry
- **When:** the hook runs
- **Then:** the injection is the pointer line alone, and the ledger is
  byte-identical with an unchanged mtime
- **And:** stdout is one valid hook envelope, and no traceback reaches stderr

### Contract: ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY
- **Given:** a valid ledger, a prompt holding a sentinel token, and a stub
  whose output is the §6 body with no `task:` line
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
- **Given:** the fixed text `integrations/claude-code/route-hook.py` injects
  (the §6 injection texts it authors, not the router's output), and a recorded
  byte ceiling on it that may only fall
- **When:** `tests/seed-lint.py` runs
- **Then:** the check fails when that text grows past the ceiling, so a kernel
  rule cannot be restated in the per-prompt text without the growth being
  seen (I-8)
- **And:** a planted line that grows the text past the ceiling makes the check
  fail
- **Note:** until 2026-09-29 this contract matched four-token runs of the
  kernel's §0 cells and FIRST MOVE steps, and `T0` to `T3` tokens. A short
  paraphrase that does not grow the text is no longer caught (§12)

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
  `"new"`, an unknown extra field), and the same envelope carrying
  `session_id` set to JSON `null`
- **When:** the hook runs on the same prompt twice
- **Then:** both injections are full mode, no file is created under
  `.cypress/session/`, and there is no stderr, so ADR-0009's
  `CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE` stays green

### Contract: LEDGER_INVALID_SESSION_ID_FULL
- **Given:** a `session_id` from each of: `../../escape`, `a/b`, and a string
  holding a NUL byte
- **When:** the hook runs
- **Then:** the injection is full mode, no file is created or modified in the
  temp plant tree or its parent directory (compared by a snapshot taken before
  and after), and stderr has one line that does not contain the raw id
- **And:** the id is tested against the §6 session-id pattern before any path
  is built from it

### Contract: LEDGER_CORRUPT_FULL
- **Given:** a ledger file holding, in turn: invalid JSON; valid JSON with an
  extra key; a file over `LEDGER_MAX_BYTES`
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
- **Given:** a ledger with `prompt_count` 3, and in turn the `source`
  `startup` and an absent `source`
- **When:** `status-hook.py` runs with that `source` and the same `session_id`
- **Then:** the ledger has `prompt_count` 0, empty `surfaced` and
  `peers_seen`, and `last_reset.source` equal to the source, or `"unknown"`
  for an absent `source` (and for a value outside the §6 `reset_source`
  pattern)
- **And:** the next non-trivial prompt gets a full injection

### Contract: STATUS_HOOK_NO_LEDGER_WRITES_NOTHING
- **Given:** a plant with a graph and `.cypress/`, and in turn a valid
  `session_id` with no ledger file, no `session_id`, and the invalid
  `session_id` `../../escape`
- **When:** `status-hook.py` runs on `SessionStart`
- **Then:** no file under `.cypress/` is created or modified, and the next
  non-trivial prompt for the valid id gets a full injection

### Contract: STATUS_HOOK_RESETS_WITHOUT_REGISTER
- **Given:** a plant with a graph and a ledger, and no `status-register.py`
- **When:** `status-hook.py` runs on `SessionStart`
- **Then:** the ledger is reset as in `STATUS_HOOK_RESETS_LEDGER`, and no
  status summary is written
- **And:** stdout carries only the code-anchor injection of
  `STATUS_HOOK_INJECTS_THE_ANCHOR_LINE`, or the not-checked line of
  `STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION` (7.32.0)

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
- **Given:** an existing valid ledger
- **When:** the hook updates it and the replace fails (the hook run through a
  `runpy` wrapper that makes `os.replace` and `os.rename` raise `OSError`)
- **Then:** the original ledger is byte-identical, the injection is full mode,
  and stderr has one line. An interrupted replace leaves the old ledger intact

### Contract: LEDGER_SYMLINK_REFUSED
- **Given:** in turn:
  - `.cypress/session` as a symlink to a directory outside the temp plant
  - `.cypress/session/<sid>.json` as a symlink to an outside file holding a
    valid version-1 ledger for the same sid, with `prompt_count` 1 and
    `surfaced` equal to the LOAD ids, so following the link would give
    reminder mode
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
- **Given:** the hook run through a `runpy` wrapper that makes `os.replace`
  raise `PermissionError` (this case runs as root too)
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
  `GC_MAX_FILES` ledger files remain, the current one among them; no stale
  temp file remains; and `notes.txt`, `bad name.json` and `.gitignore` are
  byte-identical
- **And:** a stale temp file planted after that prompt survives the next prompt
  of the same session, which updates the ledger rather than creating it

### Spawn boundary (I-2)

### Contract: BRIEF_TEMPLATES_BYTE_IDENTICAL
- **Given:** `templates/prompts/graph-session-bootstrap.md` and
  `templates/prompts/handback-payload.md`, and the baseline revision: the
  7.32.0 commit that puts owner rule R5's two sentences into step 4 of the
  canonical `GRAPH DISCIPLINE` block (its SHA is written into §10 when that
  commit lands; the baseline before it was the 7.27.0 release commit, §12)
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
- **Then:** it contains the substrings `` `task: ${prompt}\n\n` `` and
  `startsWith(`: the echo is stripped by testing the exact prefix, and output
  without it yields the pointer line alone (§7 `ROUTER_FAILED`)

### Contract: ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE
- **Given:** the extension source
- **When:** it is read
- **Then:** it contains exactly one `pi.exec(` and the substring `--plan=${`,
  so the prompt travels inside the `--plan=` element

### Contract: ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK
- **Given:** the pointer line and the full-mode suggestion header of §6
- **When:** both sources are read, with string-literal escapes decoded, since
  `route-extension.ts` spells non-ASCII characters as escapes: a backslash
  and `u00a7` for the section sign, a backslash and `u2014` for the dash
- **Then:** each string occurs verbatim in both `route-hook.py` and
  `route-extension.ts`, so the two surfaces cannot drift apart in wording

### Contract: ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE
- **Given:** the extension source
- **When:** it is read
- **Then:** it calls no filesystem write (no match of `\bNAME\s*\(` for any
  NAME of `writeFile`, `writeFileSync`, `appendFile`, `appendFileSync`,
  `mkdir`, `mkdirSync`, `rename`, `renameSync`, `createWriteStream`,
  `copyFile`, `copyFileSync`, `cp`, `cpSync`, `open`, `openSync`, `truncate`,
  `truncateSync`, `symlink`, `symlinkSync`)
- **Note:** a consequence, not asserted: with no state, every non-trivial
  prompt with a graph takes the full-mode path, and the extension cannot hold
  a record that outlives a session in its process

### Contract: PRIME_OVERLAY_KEEPS_SURFACED_SET
- **Given:** `integrations/prime-agent/APPEND_SYSTEM.md`
- **When:** it is read
- **Then:** the section names `_cypress_surfaced`

### Contract: PRIME_OVERLAY_NEVER_SAYS_LOADED
- **Given:** the section
- **When:** it is read
- **Then:** it contains no `loaded` in any letter case (I-6)
- **And:** the case fails when the section is absent, so it cannot pass on an
  empty match

### Contract: PRIME_OVERLAY_SECTION_WITHIN_CEILING
- **Given:** the section
- **When:** its UTF-8 bytes are counted
- **Then:** the count is at most `OVERLAY_SECTION_MAX_BYTES` (§6)

### Contract: PRIME_EAGER_SURFACE_WITHIN_BUDGET
- **Given:** the overlay with the section added
- **When:** `tests/seed-lint.py` runs `check_eager_surface`
- **Then:** the prime-agent surface (kernel bytes, skill descriptions and
  overlay bytes) is at most `EAGER_BUDGET`, and
  `check_published_figures` passes, so the prime-agent figures in
  `documentation/host-capability-matrix.md` equal the new computation

### Router path column (7.32.0)

`PLAN_ENTRY_NAMES_THE_NODE_FILE` runs the real `graph-lint.py` in a plant
built for the test. `ROUTE_HOOK_KEEPS_THE_PATH` runs the hook as above, with a
stub whose entry lines carry the path.

### Contract: PLAN_ENTRY_NAMES_THE_NODE_FILE
- **Given:** a graph whose node `root` lives at `docs/graph/nodes/root.md`
- **When:** `python3 docs/graph/graph-lint.py --plan "<task>"` runs from the
  plant root
- **Then:** every entry line under `LOAD (` and `NOT LOADED (` is two spaces,
  the node id, whitespace, the node's file path relative to the plant root,
  whitespace, then the text the line carried before 7.32.0
- **And:** the id is still the line's first token, so a parser that reads only
  the id is unaffected

### Contract: ROUTE_HOOK_KEEPS_THE_PATH
- **Given:** the stub router prints entry lines in the pathed grammar
- **When:** `route-hook.py` runs for a first prompt and then a later prompt
- **Then:** the full injection holds every entry line verbatim, path included,
  and each entry line under `New for this task:` in the reminder holds its path
- **And:** the ledger's `surfaced` and `peers_seen` hold node ids only

### Code anchor (7.32.0)

The tool contracts run `docs/graph/code-anchor.py` from the root of a plant
built from Git repositories, not a hook. `ANCHOR_RECORD_REFUSES_A_SYMLINK` is
the one contract in this spec whose exit code is non-zero. The status-hook
contracts use a stub tool in the plant of the reset contracts.

### Contract: ANCHOR_RECORD_NAMES_EVERY_REPOSITORY
- **Given:** a plant that is a Git work tree with one commit and one modified
  tracked file, holding a nested Git work tree that one node names in `repo:`
- **When:** `python3 docs/graph/code-anchor.py --record` runs from the plant root
- **Then:** `.cypress/anchor.json` holds one entry per repository, naming the
  path, the branch, the commit, and each uncommitted path with its content
  hash
- **And:** stdout is the one session-record line of §6, and the exit code is 0

### Contract: ANCHOR_QUIET_WHEN_NOTHING_MOVED
- **Given:** an anchor recorded as above, and no commit, checkout or file edit
  since
- **When:** `code-anchor.py --compare` runs
- **Then:** stdout is exactly the one quiet line of §6, at most
  `ANCHOR_QUIET_MAX_BYTES` bytes, and nothing else

### Contract: ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED
- **Given:** an anchor, then a new commit that changes `src/a.py` and
  `docs/graph/nodes/x.md`
- **When:** `code-anchor.py --compare` runs
- **Then:** stdout is the moved header of §6 and one repository line naming the
  old and new short commits and `src/a.py`
- **And:** no line names `docs/graph/nodes/x.md`, because paths under
  `docs/graph/` and `.cypress/` are the graph and its state, not code

### Contract: ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED
- **Given:** an anchor recorded on branch `main`, then a checkout of a branch
  `topic` whose tip changes `src/b.py`
- **When:** `code-anchor.py --compare` runs
- **Then:** the repository line names `main -> topic` and `src/b.py`

### Contract: ANCHOR_NAMES_NEW_UNCOMMITTED_WORK
- **Given:** an anchor recorded while `src/a.py` carried uncommitted work
- **When:** `src/a.py` is edited again and `src/c.py` is created, and
  `code-anchor.py --compare` runs
- **Then:** the repository line names `src/a.py` and `src/c.py` as uncommitted
- **And:** given instead that `src/a.py` was committed unchanged since the
  anchor, no line names it, because its content equals what the graph was
  reconciled against

### Contract: ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION
- **Given:** in turn: no `.cypress/anchor.json`; one that is not JSON; one with
  an unknown `version`; a recorded commit this clone does not have; `git`
  absent from `PATH`
- **When:** `code-anchor.py --compare` runs
- **Then:** stdout is the not-recorded line of §6 with the matching reason (for
  the missing commit, the repository line of that reason), and the exit code
  is 0
- **And:** no file is written

### Contract: ANCHOR_OUTPUT_WITHIN_BUDGET
- **Given:** an anchor, then a commit that changes 300 code paths
- **When:** `code-anchor.py --compare` runs
- **Then:** stdout is at most `ANCHOR_MAX_BYTES` bytes, names at most
  `ANCHOR_MAX_PATHS` paths, and ends with the more-paths line of §6
- **And:** `code-anchor.py --compare --all` names all 300

### Contract: ANCHOR_COMPARE_WRITES_NOTHING
- **Given:** any plant state above
- **When:** `code-anchor.py --compare` runs
- **Then:** no file under the plant root is created or modified, and the Git
  index is byte-identical

### Contract: ANCHOR_RECORD_REFUSES_A_SYMLINK
- **Given:** `.cypress/anchor.json` is a symlink to a file outside the plant,
  and in turn `.cypress/` does not exist
- **When:** `code-anchor.py --record` runs
- **Then:** the outside file is byte-identical, the symlink is not followed, no
  `.cypress/` is created, stderr has one line, and the exit code is non-zero

### Contract: STATUS_HOOK_INJECTS_THE_ANCHOR_LINE
- **Given:** a plant with `docs/graph/code-anchor.py`, and in turn with and
  without `docs/graph/status-register.py`
- **When:** `status-hook.py` runs on `SessionStart`
- **Then:** `additionalContext` ends with the line `code-anchor.py --compare`
  prints, after the status summary when there is one, and the hook exits 0
- **And:** the ledger reset of `STATUS_HOOK_RESETS_LEDGER` is unchanged
- **And:** this line, or the not-checked line of
  `STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION`, is injected once per
  session: `integrations/claude-code/settings.json` and the Copilot
  `hooks/status.json` wire `status-hook.py` under `SessionStart` alone

### Contract: STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION
- **Given:** a plant without `status-register.py`, and in turn
  `code-anchor.py` absent and `code-anchor.py` running past `ANCHOR_TIMEOUT`
- **When:** `status-hook.py` runs on `SessionStart`
- **Then:** `additionalContext` carries the not-checked line of §6, and the hook
  exits 0

### Contract: STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE
- **Given:** `integrations/prime-agent/status-extension.ts`, read as text
- **When:** its source is checked
- **Then:** it contains the substrings `code-anchor.py`, `--compare` and the
  not-checked line of §6: it runs the comparison and injects its output, or
  the not-checked line when the call fails
- **Note:** structural, as every Prime Agent contract here; it proves the
  source, not what the host runs


### Pending amendments, 7.32.0 (not yet contracts)

This block holds what the 7.32.0 plan still adds to this spec and has not yet
promoted. A heading here moves into §4 or §7 in the commit that lands its RED
test (`verify.status-evidence`), and until then `spec-lint.py` counts none of
it. The plan of record is `docs/plans/grill-7.32.0-harvest.md`; its §9 names
the increment that promotes each one. The path column and the code anchor, with
their failures and data shapes, left this block with the RED of increments 6
to 8 (§12), and the BRIEF_TEMPLATES_BYTE_IDENTICAL baseline amendment with the
commit that lands owner rule R5's sentences, so the block is empty. The
decision behind the anchor is
[ADR-0018](../decisions/adr-0018-code-fact-freshness-anchor.md); the one behind
the path column is decision 9 of that plan's §6.

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
  Since 7.32.0 each session start runs one subprocess more,
  `code-anchor.py --compare`, bounded by `ANCHOR_TIMEOUT`; no prompt runs one.

## 6. Data shapes

### Host envelopes read

```yaml
user_prompt_submit_stdin:      # Claude Code; Copilot sends a subset plus extras
  prompt:          { type: string }                  # or initialPrompt
  hook_event_name: { type: string, optional: true }  # or hookEventName
  session_id:      { type: string, optional: true }  # this exact key only; sessionId and other spellings are ignored; null is absent
  extra fields:    ignored

session_start_stdin:
  session_id:      { type: string, optional: true }  # this exact key only; null is absent
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

**Size on write.** `write_ledger` serializes the document first and refuses
one over `LEDGER_MAX_BYTES` before any temp file exists, so the write side
and the read side hold the same bound. The two list caps do not imply it:
`SURFACED_MAX` ids at the node-id pattern's full length, in both lists,
serialize to more than `LEDGER_MAX_BYTES`, and without the write-side check
the hook would write a file its next read refuses as oversized. A refused
write is a ledger failure: full mode and one stderr line. The state is then
steady: a first prompt leaves no file, a later one leaves the earlier ledger
as it was, so every prompt that would grow past the bound gets the same full
injection and the same one line, and no temp file is left behind. Because a refused write leaves the earlier ledger in place, `prompt_count` stops advancing, so the periodic refresh never fires and the session stays on full injections until the next SessionStart. That is the inclusive direction, and it is reachable only when node ids average well over 60 characters; real graph ids run 20 to 30.

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

GC is housekeeping and is kept apart from the write. When it fails (the scan,
a stat, or an unlink raises), the prompt costs at most one stderr line, and
the ledger is still written and the chosen text still emitted.

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

In the Prime Agent structural block of `tests/test-prompt-hooks.sh`, its one home:

| Name | Value |
|---|---|
| `OVERLAY_SECTION_MAX_BYTES` | 512, the ceiling. The section's own size is not restated here; `PRIME_OVERLAY_SECTION_WITHIN_CEILING` holds it under this value |

In `tests/seed-lint.py`, its one home (registered `max` in `tests/ratchets.json`):

| Name | Value |
|---|---|
| `HOOK_TEXT_MAX_BYTES` | 851, the ceiling `HOOK_TEXT_RESTATES_NO_KERNEL_RULE` holds. `hook_text_bytes()` measures the whole `# --- injected text` block of `route-hook.py`, from that line up to the next `# --- ` line, so the block's comment lines count too. It may only fall |

### Router output grammar (input; the path column since 7.32.0)

From `templates/knowledge-graph/graph-lint.py` `--plan`: the line
`task: <prompt>` and a blank line, which the hook removes as one exact prefix
built from the prompt it passed as `--plan=`; then notice lines `  ! <text>`
and a blank line when any exist; then the header
`LOAD (<n> nodes, ~<t> tokens):` and entry lines `  <id>  <path>  <title>` with
an optional `   <- composed by …` suffix; then optionally a blank line, the
header `NOT LOADED (with the reason; cross only if the task requires it):` and
entry lines `  <id>  <path>  <reason>`. `<path>` is the node's file relative to
the plant root (7.32.0; before it, an entry line had no path). An entry's id is
its first whitespace-delimited token and must match the node-id pattern.

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
  - the reminder's surfaced or peers_seen would exceed SURFACED_MAX   # a refresh
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

The `SURFACED_MAX` line is deliberate. A reminder only adds ids, so a long
session could grow a list past the cap that `ledger_problem` enforces on
read; instead that prompt takes the full injection, which rebuilds both lists
from the current router output alone.

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

### Code anchor file, version 1 (7.32.0)

Path: `<ROOT>/.cypress/anchor.json`, where `ROOT` is the plant root. Only
`code-anchor.py --record` writes it; `--compare` and the hooks only read it.

```yaml
anchor_file:                       # <ROOT>/.cypress/anchor.json, written only by --record
  required: [version, recorded_at, repositories]
  additional_keys: forbidden
  fields:
    version:      { type: integer, const: 1 }
    recorded_at:  { type: string, format: iso8601_utc }
    repositories:
      type: array
      of:
        path:            { type: string }        # relative to ROOT; "." is the plant root
        branch:          { type: [string, null] } # null when HEAD is detached
        commit:          { type: string, pattern: '^[0-9a-f]{40}$' }
        dirty:           { type: object, of: { path: git blob hash, or "deleted" } }
        dirty_overflow:  { type: boolean }        # more than ANCHOR_DIRTY_MAX paths; compare treats every path as moved
  file: written 0644, atomically, never through a symlink; an existing name that is not a regular file (a symlink, a directory, a FIFO) is refused and left as it is; `.cypress/` is never created
```

Governed repositories are the plant root, when it is a Git work tree, plus each
distinct `repo:` value in node frontmatter under `docs/graph/` that resolves,
inside the plant root, to a directory holding `.git`. `--record` finds them;
`--compare` reads the list from the anchor.

A path counts as moved when it is not under `docs/graph/` or `.cypress/` and
any of these holds: it changed between the recorded commit and `HEAD`; it is
uncommitted now and was not uncommitted at the anchor; or its current content
hash differs from the one recorded for it. A path whose current content equals
its recorded hash has not moved.

### Code anchor constants and texts (7.32.0)

In `tools/code-anchor.py`, placed as `docs/graph/code-anchor.py`, one home
each, except `ANCHOR_TIMEOUT`. That one is a module-level literal in
`status-hook.py`, as `ROUTER_TIMEOUT` is in `route-hook.py`, and
`status-extension.ts` keeps its own `timeout` in the `pi.exec` options.

| Constant | Value | Holds |
|---|---|---|
| `ANCHOR_QUIET_MAX_BYTES` | 160 | the quiet line |
| `ANCHOR_MAX_PATHS` | 20 | paths named before the more-paths line |
| `ANCHOR_MAX_BYTES` | 2048 | the whole `--compare` output |
| `ANCHOR_DIRTY_MAX` | 256 | uncommitted paths recorded per repository |
| `ANCHOR_TIMEOUT` | 5 s | the hook's wait for the tool; each Git call inside the tool waits at most 10 s |

Exact texts (`<n>`, `<reason>` and the bracketed parts are filled in):

```text
quiet:         Code anchor: no code changed since the last canonize (repositories: <n>). The graph's facts about code are current.
moved header:  Code anchor: code changed since the last canonize. Facts about the paths below may be stale; check them against the code. Every other fact stands as the graph states it.
repo line:     - <repo>: <commit <old7>..<new7> | branch <old> -> <new> | uncommitted>: <path>, <path>, ...
more-paths:    - and <k> more path(s): python3 docs/graph/code-anchor.py --compare --all
not recorded:  Code anchor: not recorded (<reason>). Facts about code in the graph are unverified until the next canonize records one; settled facts stay settled.
not checked:   Code anchor: not checked this session (the comparison did not run). Facts about code in the graph are unverified.
record line:   Code anchor recorded <UTC>: <repo> <branch>@<sha7> (<k> uncommitted); ...
```

## 7. Failure modes

(Authored by `architect`. Security adds adversarial cases.)

Field values below are fragments and carry no closing period.

One rule holds for every failure below: no stderr line either hook writes
carries a raw session id, valid or not. A line built from an `OSError` uses
its `strerror`, or the exception's type name when it has none, and never the
exception's text, which names the file, and a ledger's file name is the id.

### Failure: ROUTER_FAILED
- **Trigger:** `graph-lint.py` exits non-zero, runs past `ROUTER_TIMEOUT`, or
  prints nothing; the prompt holds a NUL byte or exceeds the OS argument
  limit; the output lacks the exact echo prefix
- **Response:** the pointer line alone, exit 0, on both hosts
- **Side effects:** the ledger is byte-identical with an unchanged mtime, and
  the prompt appears in no injection, ledger file or stderr line
- **Recovery:** the next prompt tries again

### Failure: SESSION_ID_REFUSED
- **Trigger:** `session_id` present, not `null`, and failing the §6 pattern,
  a non-string included. A `null` id is absent (§6), so
  `LEDGER_ABSENT_SESSION_ID_FULL` holds and no stderr line is written
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
- **Trigger:** `status-hook.py` cannot load `reset_ledger` from its sibling;
  the stat of this session's ledger fails with any error but not-found; or
  the reset write fails
- **Response:** the status summary is still injected, with one stderr line
- **Side effects:** by trigger. Sibling missing: the ledger is untouched,
  because `status-hook.py` owns no path rule. Stat fails: the ledger is
  untouched, and nothing is written. Write fails: `reset_ledger`
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
  Stdin nested past the JSON parser's limit (`RecursionError`) leaves no
  prompt to route, so `route-hook.py` emits the pointer line alone with one
  stderr line; stdin that is plainly not JSON, empty stdin included, stays
  silent, as Copilot's fail-open case needs. `status-hook.py` emits its
  summary when built, with at most one stderr line: nested stdin costs that
  line and the summary still runs, and a register that fails or prints
  output that does not decode is silence. The extension's outer guard returns
  nothing, as at 7.27.0, and its inner guard keeps the pointer line
- **Side effects:** none beyond an atomic write that either completed or did
  not
- **Recovery:** none needed

### Failure: ANCHOR_UNUSABLE
- **Contracts:** ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION
- **Trigger:** the anchor is missing, not JSON, of another version, or refused
  by the persistence rules
- **Response:** the not-recorded line, exit 0
- **Side effects:** none
- **Recovery:** the next canonize records a new anchor

### Failure: ANCHOR_COMMIT_UNREACHABLE
- **Contracts:** ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION
- **Trigger:** a recorded commit is not in this clone (a shallow clone, a
  rewritten branch, a fresh clone of a fork)
- **Response:** that repository's line says its code facts are unverified
- **Side effects:** none
- **Recovery:** fetch the commit, or let the next canonize re-anchor

### Failure: ANCHOR_CHECK_DID_NOT_RUN
- **Contracts:** STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION,
  STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE
- **Trigger:** the tool is missing, fails or times out
- **Response:** the not-checked line; the session is never blocked
- **Side effects:** none
- **Recovery:** re-install or graft, which places the tool

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

Edge, third prompt whose router adds `[redacted]` to LOAD and
`[redacted]` to NOT LOADED:

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.
New for this task: [redacted]
  [redacted]      graph linters
Surfaced earlier this session: root, skill.knowledge-graph — open if not in view.
Not suggested, not listed before (cross only if needed):
  [redacted]           peer of [redacted]
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
- [ ] AC-2: per-prompt text points at the kernel, and its fixed text is held
      under a byte ceiling. Maps to ROUTE_HOOK_POINTS_AT_KERNEL,
      HOOK_TEXT_RESTATES_NO_KERNEL_RULE,
      ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK
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
- [ ] AC-12: the router names each node's file, and the hooks keep it while
      the ledger stores ids only. Maps to PLAN_ENTRY_NAMES_THE_NODE_FILE,
      ROUTE_HOOK_KEEPS_THE_PATH
- [ ] AC-13: canonize records the code anchor in one command, and a session
      start says in one line whether code moved since. Maps to
      ANCHOR_RECORD_NAMES_EVERY_REPOSITORY, ANCHOR_QUIET_WHEN_NOTHING_MOVED,
      ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED,
      ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED,
      ANCHOR_NAMES_NEW_UNCOMMITTED_WORK, ANCHOR_OUTPUT_WITHIN_BUDGET
- [ ] AC-14: every doubt about the anchor resolves toward checking the code,
      and comparing writes nothing. Maps to
      ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION, ANCHOR_COMPARE_WRITES_NOTHING,
      ANCHOR_RECORD_REFUSES_A_SYMLINK
- [ ] AC-15: both first-class session starts carry the anchor line, with or
      without a status register. Maps to STATUS_HOOK_INJECTS_THE_ANCHOR_LINE,
      STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION,
      STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE

## 10. Test mapping

(Drafted by `architect`; `tester` owns this table and fills the test names.)

At RED (2026-09-23) every contract has a test and every row names it. A row
is `red` where its case was run and observed failing for the missing behaviour,
and `green` where the case passes on arrival and was shown able to fail by a
reverted scratch mutation (named in the row). `tests/seed-lint.py`
`check_spec_test_mapping` binds each `tests/*.sh` row by the label that opens
its Test case cell, which the cited file contains.

Binding, fixed at this revision (tester R22):

- Rows citing `tests/test-prompt-hooks.sh` or `tests/test-code-anchor.sh`
  use the fixed-width labels `X101` to `X143` reserved below, one per contract, `X144` to `X150` for the cases
  the review of 2deda6a..343445f added, and `X151` to `X163` for the 7.32.0
  contracts (§12). Each case's OK line reads
  `X1NN <SLUG>: … — OK`, so both the label and the slug appear in that case.
  Fixed width keeps one label from matching inside another. When the case is
  written, the row gets the bare path.
- Rows citing `tests/test-seed-lint.sh` use `X201` the same way.
- Rows citing `tests/seed-lint.py` carry exactly the bare function name in the
  Test case cell, and nothing else, once the row leaves `pending`. Any text
  after the name makes `_spec_green_rows` fall back to a search of the whole
  file, so the notes for these rows sit in the Level cell. Already written that
  way below. `check_spec_rows_name_their_contract` then looks for the
  slug inside that function and requires an assertion there (`fail(` counts),
  so `check_hook_text_restates_no_kernel_rule` names its slug,
  `check_eager_surface` names `PRIME_EAGER_SURFACE_WITHIN_BUDGET`, and `check` (the function that
  holds the GRAPH DISCIPLINE identity check; this bullet read `main` until RED)
  names `BRIEF_TEMPLATES_BYTE_IDENTICAL` beside it.
- The RED commit that moves this spec to `active` carries all 45 slugs in
  `tests/`. Fewer would fail `SPEC_UNCOVERED_BUDGET`, which `ratchets.json`
  holds ceiling-only.

Placement is by subject (test consolidation, 2026-09-29):
`tests/test-prompt-hooks.sh` holds the route-hook and status-hook cases, the
Copilot fail-open rows inside X118 and X124, and the Prime Agent structural
cases, overlay included, in one Python block. `tests/test-code-anchor.sh` holds
the code-anchor tool cases. `tests/test-bound-hook.sh` keeps the bounded-execution
guard only. Every Prime Agent row is at structural strength: it reads text and
observes no model.

Techniques the cases rely on:

- `REFRESH_EVERY` and `ROUTER_TIMEOUT` are read by regex from the copied hook.
  `X142` rewrites `ROUTER_TIMEOUT` to 1 against a stub
  that sleeps 3 s, so the timeout branch runs without a 15 s wait.
- Fault injection (`X133`, which holds X129's failed replace) runs the hook
  through a `runpy` wrapper that patches `os.replace` and `os.rename`, so it
  works as root. No case skips as root.
- `X162` rewrites the copied `status-hook.py`'s `ANCHOR_TIMEOUT` to 1
  against a stub tool that sleeps 3 s. `X152` to `X160` build real Git
  repositories under a `HOME` of their own, and copy `tools/code-anchor.py` to
  `docs/graph/` of the plant, where the installer places it.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO | X101 | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE | X102 | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN | X103; the NUL prompt | tests/test-prompt-hooks.sh | integration | green |
| ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY | X104; one stub mode | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_HOOK_POINTS_AT_KERNEL | X105, inside X106: the full-mode compare puts the pointer line first | tests/test-prompt-hooks.sh | integration | green |
| HOOK_TEXT_RESTATES_NO_KERNEL_RULE | check_hook_text_restates_no_kernel_rule | tests/seed-lint.py | unit; the byte budget on the hook's fixed text; the function names the slug in the finding it raises | green |
| HOOK_TEXT_RESTATES_NO_KERNEL_RULE | X201; a planted line grows the hook text past its byte ceiling | tests/test-seed-lint.sh | integration | green |
| LEDGER_FIRST_PROMPT_FULL | X106 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_LATER_PROMPT_REMINDER | X107 | tests/test-prompt-hooks.sh | integration | green |
| REMINDER_KEEPS_NOTICE_LINES | X108, inside X109 (the same notice-body run) | tests/test-prompt-hooks.sh | integration | green |
| REMINDER_SAYS_SURFACED_NEVER_LOADED | X109 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_NEW_IDS_LISTED | X110 | tests/test-prompt-hooks.sh | integration | green |
| REMINDER_DROPS_PEERS_ALREADY_SHOWN | X111 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_EVERY_LOAD_ID_NAMED | X106, X107, X110, X113, X120 and X123 hold the six ledger states (absent, every id surfaced, one outside, `REFRESH_EVERY`, invalid JSON, count 0 after a reset), each by an exact-text compare | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_REFRESH_EVERY_N | X113; constant read by regex, N and N−1 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_TRIVIAL_PROMPT_UNTOUCHED | X114; green on arrival; RED shown by mutation (trivial-prompt early return removed) | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_UNUSED_WITHOUT_GRAPH | X115; green on arrival; RED shown by mutation (no-graph path creating a file under `.cypress/session/`) | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_NEVER_EMITS_UNROUTED_ID | X116, inside X107: one unrouted id in the ledger, absent from the injection | tests/test-prompt-hooks.sh | integration | green |
| UNPARSEABLE_ROUTER_OUTPUT_FULL | X117 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_ABSENT_SESSION_ID_FULL | X118; two envelopes, and it holds the CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE block | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_INVALID_SESSION_ID_FULL | X119; three ids, tree snapshot before and after | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_CORRUPT_FULL | X120; three shapes | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_UNKNOWN_VERSION_FULL | X121, a row of X120 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_EXPIRED_FULL | X122, a row of X120 | tests/test-prompt-hooks.sh | integration | green |
| STATUS_HOOK_RESETS_LEDGER | X123; `startup` and an absent source | tests/test-prompt-hooks.sh | integration | green |
| STATUS_HOOK_NO_LEDGER_WRITES_NOTHING | X124; three ids | tests/test-prompt-hooks.sh | integration | green |
| STATUS_HOOK_RESETS_WITHOUT_REGISTER | X125 | tests/test-prompt-hooks.sh | integration | green |
| STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER | X127 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_GITIGNORED | X128 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_WRITE_IS_ATOMIC | X129, the failed-replace row inside X133; fault injection through `runpy` | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_SYMLINK_REFUSED | X130; three cases under a 5 s timeout | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_FOREIGN_OR_WRITABLE_REFUSED | X131; runs as root too | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_NO_CYPRESS_DIR_NO_WRITE | X132; red on arrival (no pointer line, no stderr line yet) | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_WRITE_FAILURE_FAILS_OPEN | X133; the `runpy` case, which runs as root | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_GC_BOUNDED | X134; old ledgers go, foreign files stay | tests/test-prompt-hooks.sh | integration | green |
| BRIEF_TEMPLATES_BYTE_IDENTICAL | check | tests/seed-lint.py | verify gate; the slug sits in a comment beside the existing GRAPH DISCIPLINE identity check in `check` (not `main`, which holds no such check), and the verify record is `git diff --quiet <baseline> -- templates/prompts/graph-session-bootstrap.md templates/prompts/handback-payload.md`, where `<baseline>` is the 7.32.0 commit that lands owner rule R5's two sentences in step 4, commit `9ba5b4b` (until 7.32.0 it was `ac61a3f`, the 7.27.0 release commit, the parent of Slice A's first commit). Green on arrival (exit 0 at RED); RED shown by mutation (a byte appended to either template gives exit 1, and a drifted embedded block fails the identity check). Held at `pending` until the top-level-def scope defect in `check_spec_rows_name_their_contract` was fixed (§12); green since, and binding (the slug found inside the function) | green |
| ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX | X135; structural, substrings | tests/test-prompt-hooks.sh | unit | green |
| ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE | X136, inside X135; structural, substrings | tests/test-prompt-hooks.sh | unit | green |
| ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK | X137; structural, escapes decoded, plain substrings | tests/test-prompt-hooks.sh | unit | green |
| ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE | X138; structural, the fs-write ban | tests/test-prompt-hooks.sh | unit | green |
| PRIME_OVERLAY_KEEPS_SURFACED_SET | X139, inside X141: the section names `_cypress_surfaced` | tests/test-prompt-hooks.sh | unit | green |
| PRIME_OVERLAY_NEVER_SAYS_LOADED | X140, inside X141: no `loaded` in the section; fails on an absent section | tests/test-prompt-hooks.sh | unit | green |
| PRIME_OVERLAY_SECTION_WITHIN_CEILING | X141; structural; holds `OVERLAY_SECTION_MAX_BYTES` | tests/test-prompt-hooks.sh | unit | green |
| PRIME_EAGER_SURFACE_WITHIN_BUDGET | check_eager_surface | tests/seed-lint.py | unit; an existing check, run with check_published_eager_figures; green on arrival, and red on the section's arrival until the matrix figures are updated. RED shown by mutation (the overlay grown in a scratch copy fails the published-figures check). Held at `pending` until the top-level-def scope defect in `check_spec_rows_name_their_contract` was fixed (§12); green since, and binding (the slug found inside the function) | green |
| ROUTER_FAILED | X142; non-zero exit, empty output, and timeout with `ROUTER_TIMEOUT` rewritten to 1 | tests/test-prompt-hooks.sh | integration | green |
| SESSION_ID_REFUSED | X119, the case of LEDGER_INVALID_SESSION_ID_FULL | tests/test-prompt-hooks.sh | integration; its cases pass at GREEN (2026-09-23), and each names this failure slug after its contract slug, on its OK and FAIL lines (`X1NN <SLUG>; failure …`) | green |
| LEDGER_UNUSABLE | X120 (with its X121 and X122 rows), X130 (file symlink and FIFO) and X131, the cases of the contracts named there | tests/test-prompt-hooks.sh | integration; its cases pass at GREEN (2026-09-23), and each names this failure slug after its contract slug, on its OK and FAIL lines (`X1NN <SLUG>; failure …`) | green |
| LEDGER_DIR_UNUSABLE | X130, X131 and X132, the cases of the contracts named there | tests/test-prompt-hooks.sh | integration; its cases pass at GREEN (2026-09-23), and each names this failure slug after its contract slug, on its OK and FAIL lines (`X1NN <SLUG>; failure …`) | green |
| RESET_NOT_WRITTEN | X143, for the write-fails trigger; the sibling-missing trigger is X127 | tests/test-prompt-hooks.sh | integration | green |
| PRIME_MODEL_IGNORES_SURFACED_INSTRUCTION | no test; model behaviour, soft (§11). The no-omission half rests on ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX and ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE | — | — | pending |
| PRIME_SURFACED_SET_TRUSTED_WHILE_STALE | no test; model behaviour (§11) | — | — | pending |
| UNEXPECTED_EXCEPTION | X144; a status register printing non-UTF-8 bytes; red on arrival (a traceback) | tests/test-prompt-hooks.sh | integration | green |
| UNEXPECTED_EXCEPTION | X145; 100 000 nested `[` on stdin, both hooks; red on arrival (a traceback, no pointer line) | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO | X146; CRLF and lone-CR prompts against their `\n` twin; red on arrival (newline translation broke the echo match) | tests/test-prompt-hooks.sh | integration | green |
| RESET_NOT_WRITTEN | X147, a second fault row of X143: the ledger stat fails | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_WRITE_FAILURE_FAILS_OPEN | X148; a ledger that would pass `LEDGER_MAX_BYTES`, one prompt: not written, full mode | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_GC_BOUNDED | X149, a fault row of X134: GC's scan fails and the ledger is still written | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX | X150, inside X135; structural | tests/test-prompt-hooks.sh | unit | green |
| PLAN_ENTRY_NAMES_THE_NODE_FILE | test_plan_entry_names_the_node_file | tests/test_graph_lint.py | integration; red on arrival (entry lines carry no path); the fixture puts one node at `docs/graph/agents/04-tester.md`, a path its id does not spell | green |
| ROUTE_HOOK_KEEPS_THE_PATH | X151, inside X110: pathed entry lines are the default body, and the ledger holds ids only | tests/test-prompt-hooks.sh | integration | green |
| ANCHOR_RECORD_NAMES_EVERY_REPOSITORY | X152; every repository named | tests/test-code-anchor.sh | integration | green |
| ANCHOR_QUIET_WHEN_NOTHING_MOVED | X153; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_NAMES_PATHS_WHEN_THE_COMMIT_MOVED | X154; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_NAMES_BOTH_BRANCHES_WHEN_THE_BRANCH_MOVED | X155; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_NAMES_NEW_UNCOMMITTED_WORK | X156; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION | X157; five causes; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_OUTPUT_WITHIN_BUDGET | X158; 300 changed paths; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_COMPARE_WRITES_NOTHING | X159; five plant states with a stale index; red on arrival (no tool) | tests/test-code-anchor.sh | integration | green |
| ANCHOR_RECORD_REFUSES_A_SYMLINK | X160; a symlink and a missing `.cypress/` refused | tests/test-code-anchor.sh | integration | green |
| ANCHOR_RECORD_REFUSES_A_SYMLINK | X166, a row of X160: a directory at the anchor name is refused as not a regular file (§6 anchor file) | tests/test-code-anchor.sh | integration | green |
| STATUS_HOOK_INJECTS_THE_ANCHOR_LINE | X161; with and without a register; red on arrival (no anchor line); its ledger-reset assertion is a guard, green on arrival | tests/test-prompt-hooks.sh | integration | green |
| STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION | X162; two causes (absent, timeout), no register | tests/test-prompt-hooks.sh | integration | green |
| STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION | X165; structural: `ANCHOR_TIMEOUT` in `status-hook.py` equals the `status-extension.ts` timeout over 1000 | tests/test-prompt-hooks.sh | unit | green |
| STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE | X163; structural, substrings | tests/test-prompt-hooks.sh | unit | green |
| STATUS_HOOK_INJECTS_THE_ANCHOR_LINE | X164; structural: `settings.json` and the Copilot `status.json` wire `status-hook.py` under `SessionStart` alone | tests/test-prompt-hooks.sh | unit | green |
| ANCHOR_UNUSABLE | X157, the case of the contract named there | tests/test-code-anchor.sh | integration; the case names this failure slug after its contract slug | green |
| ANCHOR_COMMIT_UNREACHABLE | X157, the case of the contract named there | tests/test-code-anchor.sh | integration; the case names this failure slug after its contract slug | green |
| ANCHOR_CHECK_DID_NOT_RUN | X162 and X163, the cases of the contracts named there | tests/test-prompt-hooks.sh | integration and unit; each names this failure slug after its contract slug | green |

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
| No behavioural test for `route-extension.ts` or the overlay | The eight Prime Agent structural contracts prove text and shape, not behaviour of the extension or the model | accepted at structural strength, as plan §5 records | owner | residual; a TypeScript runtime in the gate, not planned |
| The prime-agent eager figure in `README.md:50` and `:338` | `check_published_eager_figures` matches only a figure followed by `B` or `bytes`, and these two lines carry none, so they can go stale with the gate green | updated by hand in the commit that adds the section | implementer | residual; a check change is outside this spec |
| A ledger or session directory owned by another user | The owner test of §6 has no gate case, since it needs a second account | the mode cases run in the gate (`LEDGER_FOREIGN_OR_WRITABLE_REFUSED`); the owner half is shown by reading the code at review | security | residual |
| How `pi.exec` decodes the child's line endings before it returns | X150 (inside X135) proves only that `route-extension.ts` tests the exact echo prefix. If `pi.exec` itself rewrites CR or CRLF, a CRLF prompt's echo stops matching and the extension falls back to the pointer line alone | not recorded. X150 is structural only, and no runtime test observes `pi.exec` | architect | Unknown |
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
    `[redacted]`) and suppressed routing, against I-1. The exact
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
- 2026-09-23, GREEN (implementer), no assertion edited. Slice A:
  `route-hook.py` rewritten around the pointer line, the exact-echo router
  call, the pure `decide`, and the descriptor-relative session ledger;
  `status-hook.py` loads `reset_ledger` from its sibling and resets on every
  source. Slice D: `route-extension.ts` takes the echo fix, the `--plan=`
  value and the two shared literals, and holds no state; `APPEND_SYSTEM.md`
  gains the `## Surfaced nodes` section (350 B); the prime-agent eager figure
  moves from 24 094 to 24 444 in `documentation/host-capability-matrix.md`
  and `README.md`, and the matrix gains a "Per-session injection dedup" row
  that records the model-kept set as soft and model-cooperative. seed-lint:
  `check_hook_text_restates_no_kernel_rule` added and wired into `check`. §10:
  44 rows `red` → `green`, none left `red`. Held at `pending`: `SESSION_ID_REFUSED`,
  `LEDGER_UNUSABLE` and `LEDGER_DIR_UNUSABLE`, whose cases pass but name no
  such slug, so `check_spec_rows_name_their_contract` cannot bind them (a
  tester edit); and, unchanged, the two rows the tester held for the
  top-level-def scope defect, which stays a separate RED/GREEN pair.
- 2026-09-23, gate defect fixed (tester), no contract changed.
  `check_spec_rows_name_their_contract` in `tests/seed-lint.py` found a cited
  function with `^\s*def NAME\b` under `re.M`. The `\s*` crossed the blank
  lines above a top-level `def`, so the bound scope was one newline and no
  top-level seed-lint function could bind a green row. RED: the planted case
  `case_spec_row_toplevel_def` in `tests/test-seed-lint.sh` (a green row citing
  a top-level function, under two blank lines, that names its slug) failed with
  the "does not name their contract" finding. GREEN: the anchor is now
  `^[ \t]*def`. The case's second half, where only the next function names the
  slug, still fails, so the scope is the function body and not the file.
  `BRIEF_TEMPLATES_BYTE_IDENTICAL` and `PRIME_EAGER_SURFACE_WITHIN_BUDGET` move
  `pending` → `green`, and both bind: removing the slug from `check_eager_surface`
  in a scratch copy fails the check. No row of SPEC-0001, SPEC-0002 or any
  other SPEC-0003 row changes binding under the fix; the SPEC-0002 method
  scopes only lose one leading newline. The comment above
  `check_hook_text_restates_no_kernel_rule` stays as documentation, and the two
  Level notes that credited it with the binding are corrected.
- 2026-09-23, failure slugs named (tester), test text only, no assertion
  changed. The cases that exercise `SESSION_ID_REFUSED` (`X119`),
  `LEDGER_UNUSABLE` (`X120`, `X121`, `X122`, `X130`, `X131`) and
  `LEDGER_DIR_UNUSABLE` (`X130`, `X131`, `X132`) in `tests/test-bound-hook.sh`
  now name the failure slug in their `@case` slug, so it prints on the case's
  OK and FAIL lines as `X1NN <SLUG>; failure <FAILURE_SLUG>: …`. The three rows
  move `pending` → `green`. Left at `pending`, with no test by design:
  `PRIME_MODEL_IGNORES_SURFACED_INSTRUCTION`,
  `PRIME_SURFACED_SET_TRUSTED_WHILE_STALE` and `UNEXPECTED_EXCEPTION`.
- 2026-09-23, review fixes (implementer), with the orchestrator's decisions
  of 2026-09-23 on the review of 2deda6a..343445f. No assertion edited. RED
  was `X144`–`X150` and the extended `X118` in `tests/test-bound-hook.sh`, and
  `X203` in `tests/test-seed-lint.sh`.
  - (a) `"session_id": null` is absent: §6 envelopes say so,
    `SESSION_ID_REFUSED` excludes it, and `LEDGER_ABSENT_SESSION_ID_FULL`
    gains the null variant.
  - (b) `UNEXPECTED_EXCEPTION`: nested stdin gives `route-hook.py` the
    pointer line and one stderr line; plain invalid JSON stays silent;
    `status-hook.py` owes at most one stderr line, and its register call is
    guarded broadly again, so output that does not decode is silence.
  - (c) A §7 rule: no stderr line carries a raw session id, valid or not.
    `RESET_NOT_WRITTEN` gains the stat-failure trigger.
  - (d) §6: `write_ledger` enforces `LEDGER_MAX_BYTES`, the steady state is
    recorded, and so is why the list caps do not imply the byte cap.
  - (e) §6: a GC failure is isolated from the write, at most one stderr line.
    GC now reads at most `GC_SCAN_MAX` entries; it fetched one past the cap.
  - (f) §6: the `SURFACED_MAX` overflow refresh in the mode decision is now
    written down, not only coded.
  - (g) §10: rows for `X144`–`X150` and `X203`; `UNEXPECTED_EXCEPTION` moves
    `pending` → `green`.
  - (h) §11: how `pi.exec` decodes line endings is an Unknown; `X150` is
    structural only.
  - Code: the router's output is decoded as UTF-8 with no newline
    translation, so a CRLF or lone-CR prompt routes like its `\n` twin.
    `seed-lint.py` fails `PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE` when the
    overlay holds zero or several `## Surfaced nodes` sections instead of
    skipping. The host capability matrix drops its unchecked "350 bytes" for
    `OVERLAY_SECTION_MAX_BYTES` and footnotes the Copilot dedup cell ³, the
    Routing hook row's install condition.
- 2026-09-24, close (architect), no contract changed. §6 Constants: the
  `OVERLAY_SECTION_MAX_BYTES` row dropped "about 350 B", a figure for the
  section that no check holds (reviewer finding, the same figure the host
  matrix dropped in the review fixes). The row now names the ceiling and the
  contract that holds the section under it. ADR-0010 is written, `proposed`.
- 2026-09-24 (appended by the 7.29.0 front-door harvest, increment 8):
  donor-identifying tokens were replaced in place in this record under the one
  scoped exception to append-only in `CLAUDE.md` Conventions
  ([ADR-0011](../decisions/adr-0011-donor-token-redaction.md), `proposed`).
  Class of token removed: node ids of the project the seed was harvested from,
  seven spans in §8 and §12, each span replaced by the one placeholder
  `[redacted]`; no sentence was reworded or deleted. The original text remains
  at tag v7.28.0 and in history. History was not rewritten, and published tags
  and Releases keep it.
- 2026-09-28: 7.32.0 harvest, written ahead of its RED tests. §4 gains a block
  of pending amendments: the code-anchor line at session start
  ([ADR-0018](../decisions/adr-0018-code-fact-freshness-anchor.md): twelve
  anchor and hook contracts, three failure modes, the anchor file's shape, its
  constants and exact texts), the path column of the router's entry line (two
  contracts), and a pending amendment to BRIEF_TEMPLATES_BYTE_IDENTICAL's
  baseline for owner rule R5. They are headed so that `spec-lint.py` counts
  none of them; each moves into §4 or §7 in the commit that lands its RED
  (`verify.status-evidence`), with its §10 row. No live contract changed.
- 2026-09-28: 7.32.0 harvest, the RED of plan increments 6, 7 and 8. The
  fourteen pending contracts and three pending failures move into §4 and §7
  with their RED tests: `PLAN_ENTRY_NAMES_THE_NODE_FILE` (a new test in
  `tests/test_graph_lint.py`), `ROUTE_HOOK_KEEPS_THE_PATH`, the nine anchor
  contracts, the three session-start hook contracts, and the failures
  `ANCHOR_UNUSABLE`, `ANCHOR_COMMIT_UNREACHABLE` and `ANCHOR_CHECK_DID_NOT_RUN`
  (`X151` to `X163` in `tests/test-bound-hook.sh`). §6 gains the pathed entry
  line, the anchor file's shape, and the anchor's constants and exact texts,
  with `ANCHOR_TIMEOUT` a module-level literal in `status-hook.py` so `X162`
  can rewrite it. §1, §2 and §5 widen as the pending block said. §10 gains
  seventeen rows: `X151` is green on arrival and shown able to fail by a
  scratch mutation; every other row is `red`. The pending block keeps only the
  BRIEF_TEMPLATES_BYTE_IDENTICAL amendment. No earlier contract changed.
- 2026-09-28: 7.32.0 rulings on the RED of increments 6 to 8.
  `STATUS_HOOK_RESETS_WITHOUT_REGISTER` is amended with the owner's
  agreement: a plant without a register still gets no status summary, and its
  stdout may carry the code-anchor line or the not-checked line, as the two
  anchor hook contracts require. `X125` now asserts that (stdout empty or one
  hook envelope, every injected line a `Code anchor: ` line); its §10 row is
  unchanged. `STATUS_HOOK_INJECTS_THE_ANCHOR_LINE` and
  `STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE` now say plainly that the line is
  injected once per session (Claude Code on `SessionStart`, Prime Agent on the
  first prompt), and never by the per-prompt route hook or extension or any
  pre-tool hook. No contract was added. §9 gains AC-12 to AC-15 for the
  contracts promoted with that RED.
- 2026-09-28: 7.32.0: `ANCHOR_TIMEOUT` goes from 15 s to 5 s. The wait comes
  before a session's first answer, a compare costs milliseconds, and an
  expired wait gives the not-checked line. Only the §6 row changes: the 15 s
  wait in the §10 note on `X142` belongs to `ROUTER_TIMEOUT`, which keeps it.
- 2026-09-28: 7.32.0, plan increment 45. Owner rule R5 puts two sentences into
  step 4 of the canonical `GRAPH DISCIPLINE` block and, byte-identical, into the
  five embedding templates. BRIEF_TEMPLATES_BYTE_IDENTICAL's baseline revision
  becomes the commit that lands them, and its pending amendment leaves §4. The
  7.27.0 baseline `ac61a3f` had already stopped matching: `git diff --quiet
  ac61a3f` exits 1 on the two templates as they stood before this change. The
  seed-lint identity check is unchanged.
- 2026-09-28: 7.32.0 docs pass, ruling Q2 of the round's test-kill questions.
  §6's anchor file line said only that the file is never written through a
  symlink, while `tools/code-anchor.py` refuses any existing anchor name that is
  not a regular file (`write_anchor`). The line now says so. Spec text only: no
  contract changed, and no FIFO case was added; X166 already covers a directory.
- 2026-09-29: test consolidation (`docs/plans/grill-test-consolidation.md`,
  S3), by the architect. The sign-offs in §0 predate it. Two contracts are
  retired: `STATUS_HOOK_RESET_OWNS_NO_PATH_RULE`, a source check whose
  behaviour `STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER` holds, and
  `PRIME_OVERLAY_RESTATES_NO_KERNEL_RULE`, whose section is held by
  `PRIME_OVERLAY_SECTION_WITHIN_CEILING`. `HOOK_TEXT_RESTATES_NO_KERNEL_RULE`
  becomes a byte ceiling on the hook's fixed text that may only fall; a short
  paraphrase of a kernel rule that does not grow the text is no longer caught.
  `PRIME_OVERLAY_KEEPS_SURFACED_SET` narrows to the section naming
  `_cypress_surfaced`. The `ROUTE_EXTENSION_*` and
  `STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE` contracts read the TypeScript as
  substrings, and `ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE` is the fs-write ban
  alone. Fixture clauses leave the contracts: the 2 000 000-character prompt;
  two of three stub outputs; one of three Copilot envelopes (`sessionId`);
  four of seven invalid ids; three of six corrupt ledgers; six of eight reset
  sources; the invalid ids of the no-write case to one; the `.cypress` and
  `.gitignore` symlink shapes; the rewrite of `REFRESH_EVERY` to 3; the
  hard-link Then of `LEDGER_WRITE_IS_ATOMIC` (the failed-replace clause
  stays); the read-only directory of `LEDGER_WRITE_FAILURE_FAILS_OPEN`; the GC
  removal order and the 300-file clause; the anchor record's exact shape; the
  atomic-replace clause of `ANCHOR_RECORD_REFUSES_A_SYMLINK`; the anchor
  failure causes to two, with no register; the once-per-session clause to the
  `SessionStart` wiring. §6 is unchanged: it still states the behaviour those
  clauses tested. §9 AC-2 and AC-6 follow. §10 follows the folds of the
  consolidation (X105 in X106; X108 in X109; X112 over X106, X107, X110, X113,
  X120 and X123; X116 in X107; X121 and X122 in X120; X129 in X133; X147 in
  X143; X149 in X134; X151 in X110; X166 in X160; X136 and X150 in X135; X139
  and X140 in X141; X201 is the byte-budget row; X202 and X203 go), and the
  technique notes for the rewrite to 3, the hard link and the coverage binder
  go. §11 drops the `st_nlink` row, which rested on the hard link. The §10
  file column changes when `tests/test-bound-hook.sh` is split, not here. No
  hook behaviour
  changed; the status stays `active`.
- 2026-09-29: consolidation close-out, by the docs-librarian (spawn
  `session.10.docs-librarian.1`). Spec text only; no contract changed.
  `status_evidence` names `tests/test-prompt-hooks.sh` and
  `tests/test-code-anchor.sh`, the homes of the cases split out of
  `tests/test-bound-hook.sh`, and the `OVERLAY_SECTION_MAX_BYTES` home in §6
  moves with them. §6 records `HOOK_TEXT_MAX_BYTES` (851) and what it
  measures, comment lines included. `PRIME_EAGER_SURFACE_WITHIN_BUDGET` names
  `check_published_figures`, the check that replaced
  `check_published_eager_figures`.

