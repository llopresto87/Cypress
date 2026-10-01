---
status: implemented
status_date: 2026-10-01
owner: architect
status_evidence: tests/test-prompt-hooks.sh, tests/test-code-anchor.sh, tests/test-seed-lint.sh, tests/seed-lint.py, tests/test-nested-checkout.sh, tests/test_graph_lint.py (every §10 row green at the 7.37.0 release tip; all wired into tests/run.sh)
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
  Amended 2026-09-30 by the architect (7.35.0, §12):
  BRIEF_TEMPLATES_BYTE_IDENTICAL takes in the `COMPANION` block and moves its
  baseline. The sign-offs were not re-taken for it either.
  Amended 2026-10-01 by the architect (7.37.0, §12): one Python hook core on
  both first-class hosts, `--plan-json` and the compact route grammar,
  `--show`, children and non-human turns unrouted; seven contracts and two
  failures retired. The sign-offs were not re-taken for it.

- **Owner:** architect
- **Date:** 2026-09-23
- **Last reviewed:** 2026-09-23
- **Related grill section:** docs/plans/grill-7.28.0-context-residency.md §3, §4, §5, §8, §16, §17; docs/plans/grill-7.37.0-routing-context.md §9 (the 7.37.0 amendment)
- **Related ADRs:** adr-0003-enforcement-layering-honesty (the enforcement classes); adr-0009-host-support-tiers; adr-0010-context-residency (the Residency Rule and this spec's threat model; superseded in part by adr-0024); adr-0024-one-hook-core-per-session-residency; adr-0025-compact-route-lines-json-between-programs; adr-0027-first-move-runs-the-router (`PLAN_PRINTS_PLANT_BLOCK`)
- **Supersedes:** —
- **Superseded by:** —

## 1. Summary

This spec covers the text the per-prompt surfaces inject into a session, and
how each first-class host avoids re-sending what a session already surfaced.
Since 7.37.0 one Python core does it on both first-class hosts:
`integrations/claude-code/route-hook.py` on `UserPromptSubmit` (which Copilot
also runs, because it reads `.claude/settings.json`), and the same script,
placed at `.prime/agent/hooks/route-hook.py`, which
`integrations/prime-agent/route-extension.ts` calls on `before_agent_start`
through an argv envelope. The core keeps a session ledger on disk, and
`status-hook.py` resets it at every session start on both hosts. A child
session and a turn a person did not type get no injection (ADR-0024).

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

Since 7.37.0 the router speaks two formats. Models read the compact grammar
that `graph-lint.py --plan` prints, which keeps the resolved path on every id;
the core reads `graph-lint.py --plan-json`, a versioned document, and renders
the same grammar from it. `graph-lint.py --show <id>...` prints a node with its
router and spawn keys dropped and every edge and leaf pointer kept (ADR-0025).

## 2. Scope

- **In scope:**
  - the exact text each surface injects, in full mode and in reminder mode
  - the router call: the prompt as one `--plan-json=` value, and the
    validation of the `cypress.plan/1` document the core reads (7.37.0; it
    replaced the exact-echo rule of the text output)
  - the Claude Code session ledger under `.cypress/session/`: path rule,
    schema, validation, descriptor-relative I/O, owner and mode checks,
    garbage collection, atomic write, self-ignoring directory, reset
  - since 7.37.0, the argv envelope of `route-hook.py` and `status-hook.py`,
    their placement at `.prime/agent/hooks/`, and the two Prime Agent
    extensions as envelopes that compose no text and write no file
  - since 7.37.0, the rule that a child session (`--depth` above 0) and a turn
    a person did not type get no injection
  - since 7.37.0, the output of `graph-lint.py --plan`, `--plan-json` and
    `--show`: the views of the graph a model or a hook reads
  - the fail-open behaviour of both hooks on a Copilot-shaped envelope
  - since 7.32.0, the path column of the router's entry line, which the hooks
    pass through, while the ledger still stores ids only
  - since 7.32.0, the code-anchor line at session start, and
    `.cypress/anchor.json`, which `code-anchor.py --record` writes at canonize
    and a hook reads, under the same persistence rules as the ledger (I-7)
  - the invariants the plan names I-1, I-2, I-3, I-6, I-7 and I-8, as far as
    a test can observe them
- **Out of scope:**
  - the router's ranking, which SPEC-0002 covers since 7.37.0. Its output
    formats are in scope here
  - the status summary text of `status-hook.py` and `status-extension.ts`.
    Only the ledger reset and, since 7.32.0, the code-anchor line are added
  - agent and skill `description`s (Slices B and C, parked; plan §1.1)
  - the Residency Rule prose and the fact key `context-router.residency` added
    to `skills/context-router/SKILL.md` `owns:`. That is Slice E; this spec
    enforces the rule on the hooks, and the skill is the rule's one home
  - `APPEND_SYSTEM.md`, beyond the eager-surface budget it counts toward. The
    `## Surfaced nodes` section it carried from 7.28.0 is deleted in 7.37.0
  - opencode, which ships no per-prompt injection, so there is nothing to
    dedup. The gap is recorded in `documentation/host-capability-matrix.md`
  - opencode's code-anchor line. It has no hook, so it reads the line canonize
    writes into the newest session record, and no contract here covers it
  - codex and github-copilot, frozen by ADR-0009, which get nothing new. The
    only Copilot obligation is that the Claude Code hook keeps failing open on
    its envelope. Copilot runs `status-hook.py` through
    `.claude/settings.json`, so it also sees the code-anchor line
  - a session-file ledger on Prime Agent (`details` and `getBranch()`),
    deferred by ADR-0024

## 3. User-facing behavior

(Drafted by `architect`; revised by `product`.)

This change has two users. The model in a session reads what the hooks inject
before each prompt. The plant owner pays for those bytes and needs the hooks to
be honest about what they save.

**Claude Code, Copilot through `.claude/settings.json`, and Prime Agent**

The core is the same on both first-class hosts, so the text is the same.

- First routed prompt of a session: the pointer line, a blank line,
  `Router suggestion (a keyword heuristic — reason over it):`, then the route
  in the compact grammar of §6, with the path of every node it names. The
  prompt is never pasted back (§8, first example).
- Later prompts: the pointer line; the router's notice lines; a
  `LOAD <n> ~<t>t (reminder)` line; the full entry line of each node suggested
  now and not before in this session; one `seen:` line naming by id the nodes
  suggested for this prompt that were suggested earlier, telling the model to
  open what is not in its view; and a `skip` block with only the peers the
  router has not listed before. When nothing is new the injection is three
  lines (§8). No line the hook writes says a node was read or loaded.
- Peers listed earlier are not repeated. They return at the next full
  injection.
- The full injection returns after any session start (on Claude Code:
  startup, resume, clear, compaction, fork; on Prime Agent: `session_start` of
  any reason, `session_compact`, `session_tree`, `refine_complete`), after
  `REFRESH_EVERY` routed prompts, and whenever the session record is missing,
  unreadable, expired, from another session or otherwise suspect. When the
  host gives no session id (Copilot; Prime Agent if the session id cannot be
  read), every prompt gets the full injection and no dedup saving.
- Trivial prompts inject nothing and are not counted. Neither does a turn a
  person did not type (a task notification, a peer or agent message), nor any
  prompt of a child session. A plant with no graph gets the existing no-graph
  message. If the router fails, or its document fails validation, the model
  sees the pointer line alone.
- The status register and the code anchor arrive once per session start,
  never in a child (on Prime Agent this replaces the once-per-process flag).
- The session never blocks, because every path exits 0. When the hook falls
  back to full, it writes one line to its error output saying why, never the
  raw session id.
- For the owner: the record is a small file under `.cypress/session/`, ignored
  by git through that directory's own `.gitignore` and pruned by the hook. The
  measured saving is stated in ADR-0024 (follow-up route characters -73% on a
  real Prime Agent session; injected route and status 4.5% -> 0.67% of its
  processed tokens), and `SESSION_INJECTION_WITHIN_BUDGET` holds a synthetic
  session's injected bytes under a ratchet.
- One known path can leave the model with ids but no titles after context
  loss: if the reset at session start fails, reminders continue for at most
  `REFRESH_EVERY` − 1 prompts. The ids are still named, and the line still
  says to open what is out of view (§7 `RESET_NOT_WRITTEN`).

**Spawned agents** on either host get the same brief text as before, byte for
byte, and no injection: the brief's GRAPH DISCIPLINE step 1 routes their task
line.

The injected text has no visual interface. The accessibility floor applies
only as plain, unambiguous wording.

## 4. Functional contracts

(Authored by `architect`. Reviewed by `tester` for testability.)

Unless a contract says otherwise, each one runs the shipped
`integrations/claude-code/route-hook.py` (or `status-hook.py`) copied into
`.claude/` of a temp plant: a directory holding `.git/`, `.cypress/` and a stub
`docs/graph/graph-lint.py`. Since 7.37.0 the stub answers
`--plan-json=<task>` with a `cypress.plan/1` document (§6) whose
`task_sha256` is the SHA-256 of the value it received and whose other fields
are a fixed body; contracts that need other output say so. "The router's LOAD
ids" are the document's `load` ids and "the NOT LOADED ids" its `skip` ids.
The hook's stdin is a JSON envelope (§6); the argv envelope gives the same
result (`HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE`). "Full
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
- **And:** the injection's `LOAD ` header line is present, so the route was
  used and only the prompt left out
- **Note:** amended 2026-10-01: the core reads `--plan-json`, which carries a
  hash of the task instead of an echo, so nothing is stripped; the Then is
  unchanged

### Contract: ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE
- **Given:** a prompt of 8 or more characters that starts with `--` and has no
  space, and a stub router that records its argv
- **When:** the hook runs
- **Then:** the stub's argv carries exactly one argument beginning
  `--plan-json=`, whose value is the prompt, and no argument beginning
  `--plan=`, and the injection carries the stub's body

### Contract: ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN
- **Given:** a valid ledger, and a prompt holding an embedded NUL byte (sent
  as `\u0000` in the JSON envelope), which no argv can carry
- **When:** the hook runs
- **Then:** the injection is the pointer line alone, and the ledger is
  byte-identical with an unchanged mtime
- **And:** stdout is one valid hook envelope, and no traceback reaches stderr

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
- **Note:** the 7.37.0 compact grammar changes the reminder literals, so the
  ceiling is re-baselined once, to the measured block, in the commit that
  lands them (§6 `HOOK_TEXT_MAX_BYTES`); it may only fall after that

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
- **Then:** the injection is exactly three lines: the pointer line, the
  reminder header `LOAD <n> ~<t>t (reminder)` of §6, and the `seen:` line of
  §6 naming those LOAD ids in the router's order

### Contract: REMINDER_KEEPS_NOTICE_LINES
- **Given:** a ledger, and a stub document whose `notices` are not empty, with
  the LOAD ids all in `surfaced`
- **When:** the hook runs
- **Then:** each notice appears as the line `! <text>`, its `text` verbatim, in
  the document's order, straight after the pointer line

### Contract: REMINDER_SAYS_SURFACED_NEVER_LOADED
- **Given:** any reminder-mode injection, from a stub whose entry and notice
  lines do not contain the word
- **When:** it is inspected
- **Then:** every known id it names is on the `seen:` line, which ends
  `(surfaced earlier this session; open if not in view)`, and no line the hook
  authors contains `loaded` in any letter case (I-6)
- **Note:** `LOAD` in the reminder header is the router's recommendation
  vocabulary, as in full mode, not the hook's claim about what the model read

### Contract: LEDGER_NEW_IDS_LISTED
- **Given:** a ledger, and a prompt whose LOAD set holds one id outside
  `surfaced`
- **When:** the hook runs
- **Then:** that id's entry line in the §6 grammar is present after the
  reminder header, and the id is not on the `seen:` line
- **And:** the ledger's `surfaced` now contains that id

### Contract: REMINDER_DROPS_PEERS_ALREADY_SHOWN
- **Given:** a ledger whose `peers_seen` holds `agent.implementer`, and a
  router NOT LOADED block naming `agent.implementer` and one unseen peer
- **When:** the hook runs in reminder mode
- **Then:** the unseen peer appears as `<id>=<path>` in a group of the `skip`
  block of §6, and no line names `agent.implementer`
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
  7.35.0 commit that lands that round's template changes, among them the
  canonical `COMPANION` block of `graph-session-bootstrap.md` (owner ruling
  D2), commit `dd7591d`; the baseline before
  it was the 7.32.0 commit that put owner rule R5's two sentences into step 4
  of the canonical `GRAPH DISCIPLINE` block, and before that the 7.27.0
  release commit (§12)
- **When:** `git diff --quiet <baseline> -- templates/prompts/graph-session-bootstrap.md templates/prompts/handback-payload.md`
  runs at verify
- **Then:** it exits 0, and `tests/seed-lint.py`'s canonical-block identity
  check passes across the five embedding templates for both fenced blocks of
  `graph-session-bootstrap.md`, `GRAPH DISCIPLINE` and `COMPANION`
- **And:** a `COMPANION` block that differs by one byte in any one of the five
  templates is a finding naming that template

### Envelopes, children and non-human turns (7.37.0)

These run the hook as above. "The argv envelope" is §6's; a run "emits
nothing" when stdout is empty, stderr is empty, and no file under `.cypress/`
is created or modified (mtimes included).

### Contract: HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE
- **Given:** in turn these states, each built twice: no ledger; a ledger with
  `prompt_count` 1; a ledger with `prompt_count` equal to `REFRESH_EVERY`; an
  invalid session id; no session id; and, for `status-hook.py`, a ledger with
  `prompt_count` 3 and the source `compact`
- **When:** the hook runs once with the stdin envelope and once with the argv
  envelope carrying the same prompt, session id and source
- **Then:** stdout, stderr and every byte under `.cypress/session/` are
  identical between the two runs, apart from the ledger's `last_reset.at`
  timestamp
- **And:** an argv option outside the §6 envelope makes the hook emit nothing
  but one stderr line naming the option

### Contract: CHILD_SESSION_GETS_NO_INJECTION
- **Given:** a plant with a graph and a ledger directory, and in turn
  `route-hook.py` and `status-hook.py` run with `--depth=1`
- **When:** each runs on a non-trivial prompt (or with `--source=startup`)
- **Then:** each emits nothing
- **And:** with `--depth=0`, with no `--depth`, and with `--depth=x`, the
  route hook gives full mode on a first prompt and the status hook its
  summary, as without the option (I-1: an unreadable depth is routed)

### Contract: NON_HUMAN_TURN_NOT_ROUTED
- **Given:** a ledger with `prompt_count` 2, and in turn: a prompt whose first
  non-whitespace text begins with each entry of `NON_HUMAN_MARKERS` (§6),
  through stdin and through argv; and a plain prompt with `--origin=agent`
- **When:** the route hook runs
- **Then:** it emits nothing, and the ledger is byte-identical with an
  unchanged mtime, so the turn does not count toward `REFRESH_EVERY`
- **And:** the plain prompt with `--origin=human`, with no `--origin`, and
  with an `--origin` value off the §6 pattern is routed as without the option

### Contract: SESSION_INJECTION_WITHIN_BUDGET
- **Given:** a synthetic scripted session under `tests/fixtures/`: a fixed list
  of prompts, one session id, and reset points, over the seed's fixture graph
  with the real `graph-lint.py`
- **When:** every prompt runs through the route hook's argv envelope in order,
  with `status-hook.py --source=compact` at each reset point
- **Then:** the injected bytes of the whole session, summed over every
  `additionalContext` either hook returns, the status hook's included, are at
  most `SESSION_INJECTION_MAX_BYTES` (§6): the budget is everything the model
  receives
- **And:** no injection carries a line of any prompt

### Prime Agent (first-class; the shared core, structural tests)

Since 7.37.0 the two extensions are envelopes. `route-extension.ts` runs
`route-hook.py` on `before_agent_start` and returns its `additionalContext`;
`status-extension.ts` runs `status-hook.py` on the session events of §6 and
injects what it returned on the next prompt of that session, once. The
behaviour is the core's, proved above through the argv envelope. The gate has
no TypeScript runtime and no model in the loop, so the contracts here read
`integrations/prime-agent/route-extension.ts` and `status-extension.ts` as
text. Phrase checks are case-sensitive. The three host facts these rest on are
probed on a live Prime Agent session before the GREEN of the adapter (§6
host facts); a probe is evidence, not a gate row.

### Contract: ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE
- **Given:** the `route-extension.ts` source
- **When:** it is read
- **Then:** it contains exactly one `pi.exec(` and the substring `--prompt=${`,
  so the prompt travels inside one `--prompt=` element

### Contract: PRIME_SESSION_ID_PASSED
- **Given:** the `route-extension.ts` source
- **When:** it is read
- **Then:** it contains `route-hook.py`, `getSessionId(`, `rlmDepth`,
  `--session-id=`, `--depth=`, `--origin=` and `additionalContext`, and
  contains neither `graph-lint.py` nor `--plan`: it calls the core with the
  session's id and depth and composes no text of its own
- **And:** it calls no filesystem write (no match of `\bNAME\s*\(` for any
  NAME of `writeFile`, `writeFileSync`, `appendFile`, `appendFileSync`,
  `mkdir`, `mkdirSync`, `rename`, `renameSync`, `createWriteStream`,
  `copyFile`, `copyFileSync`, `cp`, `cpSync`, `open`, `openSync`, `truncate`,
  `truncateSync`, `symlink`, `symlinkSync`, `appendEntry`)
- **And:** its `pi.exec` `timeout` is greater than `ROUTER_TIMEOUT` × 1000

### Contract: PRIME_RESET_ON_EVENTS
- **Given:** the `status-extension.ts` and `route-extension.ts` sources
- **When:** they are read
- **Then:** `status-extension.ts` subscribes `session_start`,
  `session_compact`, `session_tree` and `refine_complete`, and contains
  `status-hook.py` and `--source=`
- **And:** `route-extension.ts` contains exactly one `pi.on(`, for
  `before_agent_start`, so the ledger has one reset path, `status-hook.py`, on
  both hosts

### Contract: STATUS_ONCE_PER_SESSION
- **Given:** the `status-extension.ts` source
- **When:** it is read
- **Then:** it contains no `let shown`, contains `getSessionId(` and
  `--depth=`, and keys the text it holds by session id: it contains
  `.delete(`, so a text is injected once and then dropped
- **And:** on a `before_agent_start` for a session id it has seen no event
  for, it runs `status-hook.py` with `--source=startup` (the substring
  `--source=startup` is present), so a missed `session_start` costs no status
- **Note:** a child gets no status because the core emits nothing for
  `--depth` above 0 (`CHILD_SESSION_GETS_NO_INJECTION`)

### Contract: EVERY_RESOLVER_PATH_IS_INSTALLED
- **Given:** a plant installed by `install.sh`, the candidate lists of
  `route-hook.py` (`CANDIDATES`) and `status-hook.py` (`CANDIDATES`,
  `ANCHOR_CANDIDATES`), and the core script each placed extension runs from
  its `hooks_dir` (§6)
- **When:** each path a hook or extension resolver may select is looked up in
  the installed plant
- **Then:** every one of them exists there: no resolver selects a path the
  installer does not write
- **Note:** added 2026-10-01 to own the existing M11 check; the CANDIDATES
  rule of §6, stated as a contract

### Contract: PRIME_EAGER_SURFACE_WITHIN_BUDGET
- **Given:** the overlay without the `## Surfaced nodes` section (removed in
  7.37.0)
- **When:** `tests/seed-lint.py` runs `check_eager_surface`
- **Then:** the prime-agent surface (kernel bytes, skill descriptions and
  overlay bytes) is at most `EAGER_BUDGET`, and
  `check_published_figures` passes, so the prime-agent figures in
  `documentation/host-capability-matrix.md` equal the new computation

### Router output: compact grammar, `--plan-json` and `--show` (7.32.0, 7.37.0)

The `PLAN_*` and `SHOW_*` contracts run the real `graph-lint.py` in a plant
built for the test, from the plant root, with exit code 0 unless they say
otherwise. The fixture graph holds one node at `docs/graph/agents/04-tester.md`,
a path its id does not spell, one node with frontmatter-only `artifacts` and
`plant_knowledge` entries, and an `index.md` with a full `plant:` block. The
`ROUTE_*` contracts run the hook as above.

### Contract: PLAN_ENTRY_NAMES_THE_NODE_FILE
- **Given:** the fixture graph and a task that loads at least two nodes and
  leaves at least one peer unloaded
- **When:** `python3 docs/graph/graph-lint.py --plan "<task>"` runs
- **Then:** the output is the compact grammar of §6: every LOAD entry line is
  the node id, one space, the node's file path relative to the plant root,
  ` | `, and the title with its slug prefix removed; every skipped node appears
  as `<id>=<path>` in one `skip` group; no line is padded with runs of spaces
- **And:** no line begins `task:`, and the id is the first token of every
  LOAD entry line
- **Note:** rewritten 2026-10-01; from 7.32.0 the entry line was two spaces,
  the id padded to a column, the path and the title

### Contract: PLAN_PRINTS_PLANT_BLOCK
- **Given:** the fixture graph, and in turn an `index.md` with a full `plant:`
  block and one without a `plant:` block
- **When:** `--plan` runs on a task that loads a node
- **Then:** with the block, the output has exactly one line
  `plant: environment_class=<v> commit_attribution=<v> deliverable_language=<v> comment_language=<v>`,
  the four values as `index.md` gives them, before the `LOAD` line; without
  the block, it has no line beginning `plant:`
- **And:** a block that is unfilled or partial prints no `plant:` line, and
  `--plan-json` carries `plant: null`: any of the four keys missing or empty,
  or a value that is a placeholder (it starts with `<`), with or without a
  trailing inline comment (`<ephemeral-test | staging>  # x`)
- **And:** a reminder-mode injection carries no line beginning `plant:`; the
  facts ride the full injection only

### Contract: PLAN_JSON_SCHEMA
- **Given:** the fixture graph and a task that loads at least one node, leaves
  at least one peer unloaded and raises a notice
- **When:** `graph-lint.py --plan-json=<task>` runs
- **Then:** stdout is one JSON object that satisfies the §6
  `cypress.plan/1` schema, with `schema` equal to `cypress.plan/1`, no key
  outside the schema, every `id` matching the node-id pattern and every
  `path` the relative-path pattern

### Contract: PLAN_JSON_CARRIES_NO_PROMPT
- **Given:** a task holding a sentinel token that is in no id, title, path,
  trigger or `load_when` of the fixture graph
- **When:** `--plan-json=<task>` runs
- **Then:** the sentinel appears nowhere in stdout, and no field holds the
  task: the only task-derived strings are `how.detail` values of kind
  `inferred` and `named_path`, which are paths the task names and a node owns.
  The `how.detail` of kinds `phrase` and `composed` is the node's own trigger
  piece as written, never a span of the task
- **Note:** amended 2026-10-01 (7.37.0, architect pass on increment 3): a
  composed child now needs its own trigger phrase (SPEC-0002
  `COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE`), so its detail is the node's text and
  no longer a task word. Sign-offs not re-taken

### Contract: PLAN_JSON_HASH_BINDS_TASK
- **Given:** in turn a one-line task, a task with LF, CRLF and lone-CR line
  ends, and a task holding non-ASCII text
- **When:** `--plan-json=<task>` runs
- **Then:** `task_sha256` is the lowercase hex SHA-256 of the task's UTF-8
  bytes exactly as received in argv

### Contract: PLAN_JSON_EQUALS_PLAN
- **Given:** a fixture task set of at least three tasks: one with a notice,
  one with a composed entry, and one that loads nothing (amended 2026-10-01:
  the node router no longer promotes, SPEC-0002
  `PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE`)
- **When:** `--plan` and `--plan-json` run on each
- **Then:** both carry the same notices, the same LOAD ids with the same paths
  and `how`, the same skipped ids with the same paths, kinds and `via`, in the
  same order, and the same token total

### Contract: ROUTE_HOOK_READS_PLAN_JSON
- **Given:** a valid ledger, and in turn a stub that prints: a document whose
  `schema` is not `cypress.plan/1`; one whose `task_sha256` is not the hash of
  the prompt; one with an `id` off the node-id pattern; one with a `path` that
  is absolute or holds a `..` segment; one with a key outside the schema; and
  output that is not JSON
- **When:** the hook runs
- **Then:** the injection is the pointer line alone, the ledger is
  byte-identical with an unchanged mtime, and stderr has one line
- **And:** no stub output byte that is not a validated field reaches the
  injection

### Contract: ROUTE_FULL_TEXT_EQUALS_PLAN
- **Given:** the real `graph-lint.py` over the fixture graph, no ledger, and
  the task set of `PLAN_JSON_EQUALS_PLAN`
- **When:** the hook runs on each task
- **Then:** the injection after the pointer line, the blank line and the
  suggestion header equals `graph-lint.py --plan "<task>"` stdout byte for
  byte, apart from one trailing newline
- **Note:** one grammar, two renderers; this contract keeps them aligned
  (ADR-0025)
- **Note:** amended 2026-10-01: from 7.32.0 until plan increment 2 the
  comparison removed the `task: <task>` line and the blank line after it;
  the compact grammar prints no echo, so stdout is compared whole

### Contract: ROUTE_HOOK_KEEPS_THE_PATH
- **Given:** a stub document whose `load` and `skip` entries carry paths
- **When:** `route-hook.py` runs for a first prompt and then a later prompt
  with one new LOAD id and one unseen peer
- **Then:** the full injection names the path of every LOAD and skipped entry,
  and the reminder's new entry line and new `skip` item each carry their path
- **And:** the ledger's `surfaced` and `peers_seen` hold node ids only

### Contract: SHOW_KEEPS_EVERY_POINTER
- **Given:** every node of the fixture graph
- **When:** `graph-lint.py --show <id>` runs for each
- **Then:** every `requires`, `peers`, `composes` and `delegates_to` id of the
  node's frontmatter, and every `artifacts`, `libraries` and
  `plant_knowledge` entry resolved to its path, appears on its §6 header line
- **And:** the header's first line names the node's file path relative to the
  plant root

### Contract: SHOW_DROPS_ROUTER_AND_SPAWN_KEYS
- **Given:** an agent node and an expertise node of the fixture graph
- **When:** `--show` runs on both ids in one call
- **Then:** no header line names any of `load_when`, `routing_triggers`,
  `est_tokens`, `tier`, `kind`, `name`, `description`, `prevents`, `tools`,
  `model`, `effort`, `can_delegate`, `max_spawn_depth` or `command`, and the
  two nodes are separated by one blank line before the next `# ` header

### Contract: SHOW_BODY_VERBATIM
- **Given:** a node whose body holds a fenced block, a table and trailing
  whitespace on a line
- **When:** `--show` runs on it
- **Then:** the output after the header and one blank line equals the file's
  bytes after its closing frontmatter fence and the blank line that follows
  it

### Contract: SHOW_UNKNOWN_ID_FAILS
- **Given:** one known id and one id that names no node
- **When:** `--show <known> <unknown>` runs
- **Then:** the exit code is 2, stdout is empty, and stderr names the unknown
  id

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

### Contract: ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE
- **Given:** an anchor, then new untracked files `src/__pycache__/a.cpython-312.pyc`,
  `src/b.pyc`, `src/c.py.bak`, `src/d.py.bak-20261001-091322` and `src/e.py`
- **When:** `code-anchor.py --compare` runs
- **Then:** the repository line names `src/e.py` and none of the other four,
  and a more-paths count, when there is one, counts after the filter
- **And:** `--compare --all` names the same paths
- **And:** only the installer's backup suffixes are noise: an untracked
  `src/x.bak-config.yaml` and `src/config.bak/settings.py` are named, and
  `src/y.py.bak-20260928-163636` is not

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

- **Compatibility:** `route-hook.py`, `status-hook.py` and `graph-lint.py`
  stay stdlib `python3`. The extensions add no import. The copies at
  `.prime/agent/hooks/` are byte-identical to the Claude Code ones.
- **Security:** the session id is read only from the exact key `session_id`
  and becomes a filename only after it passes the §6 pattern. All ledger I/O
  follows the §6 descriptor discipline: no symlink is followed, nothing is
  read before `fstat` shows a regular file, a session directory or ledger
  owned by another user or writable by group or others is refused, and
  `.gitignore` is created only when absent. The hook never creates
  `.cypress/`, since that directory marks a plant root for `_is_plant_root`.
  On both hosts the prompt reaches the core as one `--prompt=` argv element or
  the stdin envelope, and the router as one `--plan-json=` element, with no
  shell (§6 host facts for `pi.exec`). The router's document carries a hash of
  the task, never the task, and a document that fails §6 validation is
  dropped rather than passed through. The argv envelope's values pass the same
  patterns as the stdin ones. The extensions write no file; on Prime Agent the
  core writes the same ledger, under the same rules, as on Claude Code. The
  threat model is ADR-0010's, with ADR-0024's additions.
- **Reliability:** every path exits 0. Once `graph-lint.py` resolves,
  `route-hook.py` emits at least the pointer line, whatever fails after,
  unless the turn is not routed (a child, a non-human turn). No new hook event
  is wired in `.claude/settings.json`. On Prime Agent, `status-extension.ts`
  subscribes four session events (§6) and `route-extension.ts` one.
- **Cost:** ledger work adds no subprocess and no network call. Each routed
  prompt adds one read of at most `LEDGER_MAX_BYTES` + 1 bytes and one atomic
  write. Garbage collection runs only when a ledger is created, and reads at
  most `GC_SCAN_MAX` directory entries. On Prime Agent each routed prompt runs
  one `python3` process more than before (the core, which runs the router);
  each session event runs `status-hook.py` once. Latency is not a target
  (`--plan` costs about 70 ms). The measured token effect is ADR-0024's;
  `SESSION_INJECTION_WITHIN_BUDGET` holds a synthetic session under a ratchet.
  Each session start runs `code-anchor.py --compare` once, bounded by
  `ANCHOR_TIMEOUT`; no prompt runs one.

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

hook_stdout:                     # unchanged shape; the same in argv mode
  hookSpecificOutput:
    hookEventName:     { type: string }
    additionalContext: { type: string }              # the injection
```

**Argv envelope (7.37.0).** Any argument that begins `--` selects argv mode,
and stdin is not read. Each option is one argv element `--name=value`; an
option outside this list makes the hook emit nothing but one stderr line.

```yaml
route_hook_argv:                 # Prime Agent's route-extension.ts; same core as the stdin envelope
  --prompt:     { type: string, required: true }     # one element; the prompt never passes a shell
  --session-id: { type: string, optional: true }     # session_id_pattern, else treated as an invalid id
  --depth:      { type: string, optional: true }     # decimal integer; > 0 means a child: emit nothing; absent or not an integer: routed (I-1)
  --origin:     { type: string, optional: true }     # "human" or absent: routed; another value on origin_pattern: emit nothing; off the pattern: routed (I-1)

status_hook_argv:                # Prime Agent's status-extension.ts
  --session-id: { type: string, optional: true }
  --source:     { type: string, optional: true }     # reset_source; the Prime Agent event or session_start reason
  --depth:      { type: string, optional: true }     # as above; > 0: emit nothing and reset nothing
```

### Patterns

```yaml
session_id_pattern: '^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$'   # else: no session id
node_id_pattern:    '^[a-z][a-z0-9_.-]{0,127}$'
reset_source:       '^[a-z_-]{1,32}$'                        # else stored as "unknown"
origin_pattern:     '^[a-z_-]{1,32}$'                        # 7.37.0; off the pattern is treated as absent
relative_path:      '^(?!/)(?!.*(^|/)\.\.(/|$))[A-Za-z0-9_./-]+$' # 7.37.0; a path in a plan document
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
| `ROUTER_TIMEOUT` | 15 s, a module-level literal. Since 7.37.0 `route-extension.ts` runs the core, not the router, so its `pi.exec` `timeout` is longer than this (`PRIME_SESSION_ID_PASSED`) |
| `LEDGER_TTL` | 12 h |
| `GC_MAX_AGE` | 7 days |
| `GC_MAX_FILES` | 32 |
| `GC_SCAN_MAX` | 256 |
| `TEMP_PREFIX` | `.tmp-` |
| `TEMP_MAX_AGE` | 1 h |
| `LEDGER_MAX_BYTES` | 64 KiB |
| `SURFACED_MAX` | 512 |

Also in `route-hook.py` (7.37.0):

| Name | Value |
|---|---|
| `NON_HUMAN_MARKERS` | `<task-notification>`, `Another Claude session sent a message:`, `<local-command-`, `[agent-message from `, `[bash-done `, `[harness-digest]`. A prompt whose first non-whitespace text begins with one is not routed. The last three are Prime Agent host turns: the delivery header of an agent message (observed 2026-10-01), a background command's completion notice (fires `before_agent_start` at depth 0, live probe of 7.37.0 increment 1) and the host-generated harness digest; the list may shrink when a probe shows the host envelope carries an origin |

Also in `route-hook.py`, its one home, registered `max` in
`tests/ratchets.json` (7.37.0):

| Name | Value |
|---|---|
| `SESSION_INJECTION_MAX_BYTES` | 4960, the measured total of `SESSION_INJECTION_WITHIN_BUDGET`'s scripted session at the GREEN of plan increment 1: every byte of `additionalContext` the session receives, the route hook's and the status hook's `--source=compact` injections alike. It may only fall |

In `tests/seed-lint.py`, its one home (registered `max` in `tests/ratchets.json`):

| Name | Value |
|---|---|
| `HOOK_TEXT_MAX_BYTES` | 724, the ceiling `HOOK_TEXT_RESTATES_NO_KERNEL_RULE` holds. `hook_text_bytes()` measures the whole `# --- injected text` block of `route-hook.py`, from that line up to the next `# --- ` line, so the block's comment lines count too. It may only fall. The 7.37.0 compact reminder literals re-baselined it once, from 851 to the measured block, 724 (plan increment 2) |

### Router output (the path column since 7.32.0; compact grammar and `cypress.plan/1` since 7.37.0)

`templates/knowledge-graph/graph-lint.py` has three model- and hook-facing
views. `--plan` prints the compact grammar and the core renders the same
grammar from the document; `ROUTE_FULL_TEXT_EQUALS_PLAN` holds the two equal.

**`--plan "<task>"`, the compact grammar.** One line each, no column padding,
in this order; a part is absent when it is empty:

```text
! <notice text>                          one line per notice, router order
plant: environment_class=<v> commit_attribution=<v> deliverable_language=<v> comment_language=<v>
LOAD <n> ~<t>t                           always present; n may be 0
<id> <path> | <title>[ <- <how>]         one per LOAD node, sorted by id
skip (cross only if the task needs it):
 peer of <via>: <id>=<path> <id>=<path> ...
 composed by <via>, no specific term: <id>=<path> ...
```

- `<path>` is the node's file relative to the plant root, on every id (owner
  ruling O1: the model is handed the resolved fact).
- `<title>` is the frontmatter `title` with a leading `<slug> — ` removed when
  `<slug>` equals the id's last dotted segment.
- `<how>` is printed for these kinds only: `inferred from "<path>"`, `composed by <via> on "<term>"`,
  `owns "<path>"` (a named path), `phrase "<phrase>"` (a trigger phrase).
- Skip groups follow the order this section lists the reasons, every `peer
  of` group before every `composed by` group, and by `via` within a reason;
  ids are sorted within a group (ruling of 2026-10-01).
- The `plant:` line is printed only from the plan increment that lands
  `PLAN_PRINTS_PLANT_BLOCK` (ADR-0027).
- No line echoes the task.

**`--plan-json=<task>`, schema `cypress.plan/1`.** One JSON object on stdout:

```yaml
plan_document:
  required: [schema, task_sha256, plant, notices, est_tokens, load, skip]
  additional_keys: forbidden
  fields:
    schema:      { const: "cypress.plan/1" }
    task_sha256: { type: string, pattern: '^[0-9a-f]{64}$' }   # SHA-256 of the task's UTF-8 bytes as received
    plant:       { type: [null, object], fields: { environment_class, commit_attribution, deliverable_language, comment_language: string } }
    notices:     { type: array, of: { code: { enum: [wide_descent, inference_skipped, long_task, no_signal] }, text: string } }
    est_tokens:  { type: integer, min: 0 }                       # the LOAD token total
    load:        { type: array, sorted_by: id, of: { id: node_id, path: relative_path, title: string,
                   how: { kind: { enum: [scored, requires, inferred, composed, named_id, named_path, phrase] },
                          detail: [null, string], via: [null, node_id] } } }
    skip:        { type: array, ordered_as: the --plan text, of: { id: node_id, path: relative_path, kind: { enum: [peer, composed] }, via: node_id } }
```

`skip` is in the order the `--plan` text prints the skipped ids
(`PLAN_JSON_EQUALS_PLAN`): the skip-group order above, by id within a group.

The enums name every kind the router emits once SPEC-0002's node-router
contracts land, so the schema does not change between increments. `promoted`
left the enum on 2026-10-01, before `cypress.plan/1` shipped in any release:
the node router no longer promotes (SPEC-0002
`PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE`). The
document carries no copy of the task; the only task-derived strings are
`how.detail` of kinds `inferred` and `named_path`, a path the task names and a
node owns. The core validates a document against this schema, the node-id
pattern and the relative-path pattern before it renders anything; a document
that fails is `ROUTER_FAILED`. A later schema is a new name.

**`--show <id>...`.** For each id, in the order given, separated by one blank
line:

```text
# <id> <path>: <title>
owns: <key>, <key>
requires: <id>, <id>
peers: <id>, <id>
composes: <id>, <id>
delegates_to: <id>, <id>
artifacts: <path>, ...
libraries: <path>, ...
plant_knowledge: <path>, ...
origin: <seed|project>[ repo: <v>][ status: <v> status_date: <v> owner: <v> ends_when: <v> scope: <v> reason: <v> recorded_in: <v> departs_from: <v>]

<body verbatim>
```

A line is printed only when its key is present. `<title>` is cut as in
`--plan`. Node edges print as bare ids, which `--show` resolves. Leaf entries
print as paths relative to the plant root, a directory entry keeping its
trailing `/`; a `libraries` slug resolves to its page. Not printed: `load_when`,
`routing_triggers`, `est_tokens`, `tier`, `kind`, `name`, `description`,
`prevents`, and the spawn keys `tools`, `model`, `effort`, `can_delegate`,
`max_spawn_depth`, `command`. Any other key the header does not classify is
kept, never dropped: after the `origin:` line, in frontmatter order, as
`<key>: <value>`, a list joined with `, ` (ruling of 2026-10-01; a plant's own
keys survive). An unknown id exits 2 and prints nothing. The file stays
canonical; the view is derived on every call and never cached.

### Injection texts (exact; the tests compare against them)

Each text below is a single string literal in `route-hook.py`, inside its
`# --- injected text` block, except the route itself, which the core renders
from the document in the grammar above. The skip header is also a literal in
`graph-lint.py`; `ROUTE_FULL_TEXT_EQUALS_PLAN` holds the two equal.

- **Pointer line (`POINTER`):**
  `Route first: the kernel's FIRST MOVE and §0 apply to this prompt.`
- **Full mode:** the pointer line, a blank line, the suggestion header
  (`SUGGESTION_HEADER`)
  `Router suggestion (a keyword heuristic — reason over it):`, then the route
  rendered from the document, equal to `--plan` output for the same task.
- **Reminder mode**, in this order, each part omitted when empty:
  1. the pointer line;
  2. the notice lines, `! <text>`;
  3. `LOAD <n> ~<t>t (reminder)` (`REMINDER_HEADER`), with the document's
     LOAD count and token total;
  4. the entry line of each LOAD id not in `surfaced`, in the grammar above;
  5. `seen: <ids> (surfaced earlier this session; open if not in view)`
     (`SEEN_LINE`);
  6. `skip (cross only if the task needs it):` (`SKIP_HEADER`), then the
     groups of the grammar above holding only skipped ids in neither
     `surfaced` nor `peers_seen`.

  Ids on the `seen:` line are joined with `, ` in the router's order. No
  `plant:` line: it is resident from the full injection.
- **Router failed:** the pointer line alone.
- **Not routed** (a trivial prompt, a child, a non-human turn): nothing.

### Mode decision (pure; kept apart from file I/O in the script)

```yaml
inputs:  [router_ids (load, skip), ledger_or_absent, REFRESH_EVERY, depth, origin, prompt]
not routed when any of:          # emit nothing; no router run, no ledger access
  - the prompt is trivial
  - depth is an integer > 0
  - origin is on origin_pattern and is not "human"
  - the prompt's first non-whitespace text begins with a NON_HUMAN_MARKERS entry
router failed when any of:       # no ledger access at all
  - graph-lint.py exits non-zero, exceeds ROUTER_TIMEOUT, or prints nothing
  - the prompt cannot be passed (NUL byte, over the OS argument limit)
  - the output is not a document that passes the cypress.plan/1 validation,
    task_sha256 included
full when any of:
  - ledger absent or unusable
  - prompt_count == 0            # a reset was recorded
  - prompt_count >= REFRESH_EVERY
  - the reminder's surfaced or peers_seen would exceed SURFACED_MAX   # a refresh
otherwise: reminder
after full:     prompt_count = 1; surfaced = load; peers_seen = skip - load
after reminder: prompt_count += 1; surfaced |= load; peers_seen |= (skip - surfaced)
```

Order of work in `route-hook.py`: read the envelope; decide not-routed;
resolve `graph-lint.py`; run the router; validate the document; build the
full-mode text; then, in one guarded block, read the ledger, decide,
compose the chosen text, and write the ledger; emit. The chosen text is emitted
only when the whole block succeeds. If any step of the block fails, the
full-mode text already in hand is emitted with one stderr line, so a ledger
failure can neither drop the injection nor leave a reminder that no ledger
records.

The `SURFACED_MAX` line is deliberate. A reminder only adds ids, so a long
session could grow a list past the cap that `ledger_problem` enforces on
read; instead that prompt takes the full injection, which rebuilds both lists
from the current router output alone.

Since 7.37.0 this decision runs on both first-class hosts, in the same
script.

### Prime Agent envelope and host facts (7.37.0)

The model-kept set `_cypress_surfaced` and the overlay's `## Surfaced nodes`
section of 7.28.0 are retired by ADR-0024. On Prime Agent:

```yaml
route_extension:                 # .prime/agent/extensions/route-extension.ts
  on: before_agent_start
  runs: python3 <hooks>/route-hook.py --prompt=<prompt> --session-id=<getSessionId()> --depth=<header rlmDepth> --origin=<origin>
  returns: hookSpecificOutput.additionalContext of stdout as the message content; nothing when stdout is empty or not JSON
status_extension:                # .prime/agent/extensions/status-extension.ts
  on: [session_start (every reason), session_compact, session_tree, refine_complete]
  runs: python3 <hooks>/status-hook.py --session-id=<id> --source=<reason or event> --depth=<n>
  holds: the returned additionalContext, keyed by session id
  on_before_agent_start: inject the held text for this session id once, then drop it; for a session id with no event seen, run status-hook.py with --source=startup first
hooks_dir: the extension's sibling `../hooks/`; when the extension cannot
  resolve its own directory, `<ctx.cwd>/.prime/agent/hooks/`; no upward walk.
  A missing script means no injection (the kernel's FIRST MOVE is the floor)
fail_open: an unreadable session id is omitted (full mode, I-1); an unreadable
  depth is omitted (routed, I-1); any exception returns nothing
```

Host facts. Classifications as in the 7.28.0 research pass unless the row
says otherwise; the source paths are under the steward plant's
`docs/graph/sources/raw/`.

| Fact | Class | Source |
|---|---|---|
| `pi.exec` spawns with `shell: false`, so argv elements are not shell-parsed | Documented (source read) | installed `@earendil-works/pi-coding-agent` 0.75.3, `dist/core/exec.js:12-16`, read 2026-09-23 |
| `session_start` reason ∈ `startup`, `reload`, `new`, `resume`, `fork` | Documented | `prime-agent-2026-09-17.txt:312-322` |
| Compaction events `session_before_compact`, `session_compact`, `session_compact_failed` | Documented | `prime-agent-2026-09-17.txt:502-541` |
| An `agent_message` delivered to an idle child fires `before_agent_start` and was routed; four deliveries to a parent produced no route | Observed 2026-10-01 on real transcripts | the round's refutation pass, kept with the round's working records outside the seed |
| A delivered agent message opens with the line `[agent-message from <role>:<id>]` | Observed 2026-10-01 | the same session's own transcript |
| `ctx.sessionManager.getSessionId()` answers in `before_agent_start` and in `session_start`, and equals the session header `id` | Observed 2026-10-01, Prime Agent 0.9.8 | live probe, recorded in plan increment 1 |
| `ctx.sessionManager.getHeader()` carries `rlmDepth` (0 in a parent, 1 in a child) and `parentSession` (absent at depth 0) | Observed 2026-10-01, Prime Agent 0.9.8 | live probe, recorded in plan increment 1 |
| Under jiti `__dirname` names the extension's own directory; `import.meta.url` is a `data:` URL | Observed 2026-10-01, Prime Agent 0.9.8 | live probe, recorded in plan increment 1 |
| The extension module is evaluated once per session, parent and child alike, in one process | Observed 2026-10-01, Prime Agent 0.9.8 | live probe, recorded in plan increment 1 |
| The `before_agent_start` event carries `type`, `prompt`, `images`, `systemPrompt` and `systemPromptOptions`, and no origin of the turn, so `route-extension.ts` passes `--origin` only if a later host adds an `origin` field | Documented (source read) | the Prime Agent 0.9.8 binary, `emitBeforeAgentStart`, read 2026-10-01 |

If the first probe fails, Prime Agent stays in full mode (the extension
passes no `--session-id`) and the session-file ledger reopens (ADR-0024).

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
its recorded hash has not moved. Since 7.37.0 a path is never named, nor
counted, when a segment is `__pycache__` or its name ends `.pyc` or `.bak` or
matches `*.bak-<digit>*`, the timestamped backup the installer writes. A name
holding `.bak-` before other text (`x.bak-config.yaml`) and a directory named
`*.bak` are code (`ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE`).

### Code anchor constants and texts (7.32.0)

In `tools/code-anchor.py`, placed as `docs/graph/code-anchor.py`, one home
each, except `ANCHOR_TIMEOUT`. That one is a module-level literal in
`status-hook.py`, as `ROUTER_TIMEOUT` is in `route-hook.py`. Since 7.37.0
`status-extension.ts` runs `status-hook.py`, so this one value bounds the
anchor on both hosts, and the extension's `pi.exec` `timeout` bounds the
whole core.

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
  limit; the output is not a `cypress.plan/1` document that passes §6
  validation, its `task_sha256` included (`ROUTE_HOOK_READS_PLAN_JSON`);
  an engine that rejects `--plan-json` is `ENGINE_OLDER_THAN_HOOK_IS_NAMED`
- **Response:** the pointer line alone, exit 0, on both hosts, with one stderr
  line when the document failed validation
- **Side effects:** the ledger is byte-identical with an unchanged mtime, and
  the prompt appears in no injection, ledger file or stderr line
- **Recovery:** the next prompt tries again

### Failure: ENGINE_OLDER_THAN_HOOK_IS_NAMED
- **Trigger:** `graph-lint.py` exits 2 with argparse's rejection of
  `--plan-json` on stderr: the plant's engine predates the hook (a graft
  refused, a KEEP-PLANT engine, a symlinked engine, a plain re-install over
  an older engine). The hook tells it from every other failure by exactly
  two facts: exit status 2 and the bytes `unrecognized arguments: --plan-json`
  in the engine's stderr. Any other non-zero exit is `ROUTER_FAILED`
- **Response:** the pointer line and exactly one notice line after it, exit 0,
  on both hosts. The notice names `graph-lint.py`, `--plan-json` and the fix,
  a graft of the engine. No stderr line. The hook never falls back to parsing
  `--plan` text
- **Side effects:** as `ROUTER_FAILED`: the ledger is byte-identical with an
  unchanged mtime, none is created, and the prompt appears in no injection,
  ledger file or stderr line
- **Recovery:** re-run graft's engine step (`tools/graft-graph-engine.py`).
  A plain re-install leaves the engine byte-unchanged (adr-0014); the notice
  is what it leaves the hook to say (SPEC-0001
  `REINSTALL_ENGINE_SERVES_THE_HOOKS`)

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

### Failure: PRIME_SESSION_UNKNOWN
- **Contracts:** PRIME_SESSION_ID_PASSED, CHILD_SESSION_GETS_NO_INJECTION
- **Trigger:** on Prime Agent, `getSessionId()` throws or returns nothing, or
  the session header gives no readable depth
- **Response:** the extension omits that option; the core gives full mode on
  every routed prompt (no session id) or routes the prompt (no depth), as
  before 7.37.0
- **Side effects:** no ledger is written without a session id; a child whose
  depth cannot be read is routed on its brief, as before 7.37.0
- **Recovery:** none needed. The direction is inclusion (I-1); the cost is the
  pre-7.37.0 cost

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
  output that does not decode is silence. Each extension's guard returns
  nothing
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
- **Contracts:** STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION
- **Trigger:** the tool is missing, fails or times out
- **Response:** the not-checked line; the session is never blocked
- **Side effects:** none
- **Recovery:** re-install or graft, which places the tool

## 8. Examples

The final grammar of 7.37.0. Stub document, used for every example below; the
ids are illustrative, not a plant's real graph, and the hash is shortened here.

```json
{"schema": "cypress.plan/1", "task_sha256": "9f2c…", "plant": null, "notices": [],
 "est_tokens": 900,
 "load": [{"id": "root", "path": "docs/graph/nodes/root.md", "title": "root — knowledge graph router",
           "how": {"kind": "scored", "detail": null, "via": null}},
          {"id": "skill.knowledge-graph", "path": "docs/graph/skills/knowledge-graph.md",
           "title": "knowledge-graph — knowledge-graph authoring", "how": {"kind": "requires", "detail": null, "via": "root"}}],
 "skip": [{"id": "agent.implementer", "path": "docs/graph/agents/02-implementer.md", "kind": "peer", "via": "skill.knowledge-graph"}]}
```

Happy, first prompt, `session_id` `3b9f1c2e-5d4a-4e8b-9a61-0c7f2d8e1a44`, no
ledger. Injection (full mode):

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.

Router suggestion (a keyword heuristic — reason over it):
LOAD 2 ~900t
root docs/graph/nodes/root.md | knowledge graph router
skill.knowledge-graph docs/graph/skills/knowledge-graph.md | knowledge-graph authoring
skip (cross only if the task needs it):
 peer of skill.knowledge-graph: agent.implementer=docs/graph/agents/02-implementer.md
```

Ledger afterwards (mode 0600):

```json
{"version": 1, "session_id": "3b9f1c2e-5d4a-4e8b-9a61-0c7f2d8e1a44",
 "prompt_count": 1, "surfaced": ["root", "skill.knowledge-graph"],
 "peers_seen": ["agent.implementer"], "last_reset": null}
```

Edge, second prompt with the same document. Injection (reminder mode, three
lines):

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.
LOAD 2 ~900t (reminder)
seen: root, skill.knowledge-graph (surfaced earlier this session; open if not in view)
```

Edge, third prompt whose document adds `subsystem.graph-linters` to `load` and
`domain.frontmatter` to `skip`:

```
Route first: the kernel's FIRST MOVE and §0 apply to this prompt.
LOAD 3 ~1400t (reminder)
subsystem.graph-linters docs/graph/nodes/subsystem.graph-linters.md | graph linters
seen: root, skill.knowledge-graph (surfaced earlier this session; open if not in view)
skip (cross only if the task needs it):
 peer of subsystem.graph-linters: domain.frontmatter=docs/graph/nodes/domain.frontmatter.md
```

Failure, `session_id` `../../escape`: full mode as in the first example, no
file created, one stderr line such as
`route-hook: session_id refused (not a safe filename); full injection`.

Failure, ledger file holding `{"version": 2, …}`: full mode, one stderr line
naming the ledger path, and the file replaced by a valid version-1 ledger with
`prompt_count` 1.

Failure, a document whose `task_sha256` is not the hash of the prompt: the
pointer line alone, one stderr line, and the ledger untouched.

Prime Agent, the same three prompts: the same three injections, from the same
script through the argv envelope. A child spawned on the second prompt gets
nothing on any of its prompts; its brief routes its task line. A parent's
message delivered to that child, beginning `[agent-message from parent:…]`,
gets nothing either.

## 9. Acceptance criteria

(Drafted by `architect` and revised by `product`. Each criterion names the
contracts it maps to.)

- [ ] AC-1: no injection carries the user's prompt back into the session.
      Maps to ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO,
      ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE,
      ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN,
      ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE,
      PLAN_JSON_CARRIES_NO_PROMPT, PLAN_JSON_HASH_BINDS_TASK
- [ ] AC-2: per-prompt text points at the kernel, and its fixed text is held
      under a byte ceiling. Maps to ROUTE_HOOK_POINTS_AT_KERNEL,
      HOOK_TEXT_RESTATES_NO_KERNEL_RULE
- [ ] AC-3: between one full injection and the next, a node the router already
      suggested this session is named by id on the `seen:` line and its entry
      line is not repeated, on both first-class hosts. No line the hook writes
      contains `loaded` in any letter case. Maps to LEDGER_FIRST_PROMPT_FULL,
      LEDGER_LATER_PROMPT_REMINDER, REMINDER_KEEPS_NOTICE_LINES,
      REMINDER_SAYS_SURFACED_NEVER_LOADED, LEDGER_NEW_IDS_LISTED,
      REMINDER_DROPS_PEERS_ALREADY_SHOWN, LEDGER_EVERY_LOAD_ID_NAMED
- [ ] AC-4: each of these gives the full injection, exit 0, and at most one
      error line: no session id; an invalid session id; a ledger that is
      corrupt, of unknown version, expired, oversized or from another session.
      A router document that fails validation gives the pointer line alone.
      Maps to LEDGER_ABSENT_SESSION_ID_FULL, LEDGER_INVALID_SESSION_ID_FULL,
      LEDGER_CORRUPT_FULL, LEDGER_UNKNOWN_VERSION_FULL, LEDGER_EXPIRED_FULL,
      ROUTE_HOOK_READS_PLAN_JSON
- [ ] AC-5: the first routed prompt after any `SessionStart` source, and the
      first after `REFRESH_EVERY` routed prompts, gets the full injection, and
      on Prime Agent each session event resets the ledger. Maps to
      STATUS_HOOK_RESETS_LEDGER, STATUS_HOOK_NO_LEDGER_WRITES_NOTHING,
      STATUS_HOOK_RESETS_WITHOUT_REGISTER, LEDGER_REFRESH_EVERY_N,
      PRIME_RESET_ON_EVENTS
- [ ] AC-6: the record is safe, bounded, invisible to git and never read as
      instructions. Maps to LEDGER_GITIGNORED, LEDGER_WRITE_IS_ATOMIC,
      LEDGER_SYMLINK_REFUSED, LEDGER_FOREIGN_OR_WRITABLE_REFUSED,
      LEDGER_NO_CYPRESS_DIR_NO_WRITE, LEDGER_WRITE_FAILURE_FAILS_OPEN,
      LEDGER_GC_BOUNDED, LEDGER_NEVER_EMITS_UNROUTED_ID,
      LEDGER_UNUSED_WITHOUT_GRAPH, LEDGER_TRIVIAL_PROMPT_UNTOUCHED,
      STATUS_HOOK_WITHOUT_SIBLING_LEAVES_LEDGER
- [ ] AC-7: spawned workers get the same brief text as before and no injected
      route or status; a turn a person did not type is not routed. Maps to
      BRIEF_TEMPLATES_BYTE_IDENTICAL, CHILD_SESSION_GETS_NO_INJECTION,
      NON_HUMAN_TURN_NOT_ROUTED
- [ ] AC-8: the Prime Agent overlay stays inside the eager budget, and falls
      by the retired section. Maps to PRIME_EAGER_SURFACE_WITHIN_BUDGET
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
- [ ] AC-10: Prime Agent gets the same residency as Claude Code through the
      same script; its extensions compose no text and write no file, and the
      status reaches each session start once. Maps to
      HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE, PRIME_SESSION_ID_PASSED,
      STATUS_ONCE_PER_SESSION
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
      ANCHOR_NAMES_NEW_UNCOMMITTED_WORK, ANCHOR_OUTPUT_WITHIN_BUDGET,
      ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE
- [ ] AC-14: every doubt about the anchor resolves toward checking the code,
      and comparing writes nothing. Maps to
      ANCHOR_ABSENT_FAILS_TOWARD_INCLUSION, ANCHOR_COMPARE_WRITES_NOTHING,
      ANCHOR_RECORD_REFUSES_A_SYMLINK
- [ ] AC-15: both first-class session starts carry the anchor line, with or
      without a status register. Maps to STATUS_HOOK_INJECTS_THE_ANCHOR_LINE,
      STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION, STATUS_ONCE_PER_SESSION
- [ ] AC-16 (7.37.0): programs read the router through a versioned document
      that the model-facing text equals. Maps to PLAN_JSON_SCHEMA,
      PLAN_JSON_EQUALS_PLAN, ROUTE_FULL_TEXT_EQUALS_PLAN
- [ ] AC-17 (7.37.0): a node read after routing keeps every pointer and drops
      the router and spawn keys. Maps to SHOW_KEEPS_EVERY_POINTER,
      SHOW_DROPS_ROUTER_AND_SPAWN_KEYS, SHOW_BODY_VERBATIM,
      SHOW_UNKNOWN_ID_FAILS
- [ ] AC-18 (7.37.0): a synthetic session's injected bytes stay under a
      ratchet that may only fall. Maps to SESSION_INJECTION_WITHIN_BUDGET
- [ ] AC-19 (7.37.0, if ADR-0027 lands): the full plan carries the plant's
      four `plant:` facts. Maps to PLAN_PRINTS_PLANT_BLOCK

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

Amendment of 2026-10-01 (7.37.0): the rows of retired contracts left with
them (§12); a rewritten contract's row keeps its case label and reads
`pending` until its case is rewritten at RED; a new contract's row reads
`pending` with no test file until the tester names its case. Until then
`spec-lint.py` counts these as uncovered, as at 7.35.0. The shared stub of
`tests/test-prompt-hooks.sh` moves to the `cypress.plan/1` form at the RED of
plan increment 1; the cases of unchanged contracts keep their assertions.

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
| ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO | X101 | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 1 (the And reads a `LOAD ` header line); green on arrival, as its Then is unchanged and today's core already holds it | green |
| ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE | X102 | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 1; red on arrival (the core passes `--plan=`) | green |
| ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN | X103; the NUL prompt | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_HOOK_POINTS_AT_KERNEL | X105, inside X106: the full-mode compare puts the pointer line first | tests/test-prompt-hooks.sh | integration | green |
| HOOK_TEXT_RESTATES_NO_KERNEL_RULE | check_hook_text_restates_no_kernel_rule | tests/seed-lint.py | unit; the byte budget on the hook's fixed text; the function names the slug in the finding it raises; rewritten 2026-10-01; at the RED of plan increment 2 the check needs no change (it measures the whole block, whatever its literals), and the one re-baseline of `HOOK_TEXT_MAX_BYTES` is the GREEN's | green |
| HOOK_TEXT_RESTATES_NO_KERNEL_RULE | X201; a planted line grows the hook text past its byte ceiling | tests/test-seed-lint.sh | integration; rewritten at the RED of plan increment 2: the line is planted after the `# --- injected text` marker, not on `NEW_PREFIX`, which the compact reminder removes | green |
| LEDGER_FIRST_PROMPT_FULL | X106 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_LATER_PROMPT_REMINDER | X107 | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 2; red at the RED of plan increment 2 (the reminder is the 7.28.0 Surfaced line, not `LOAD <n> ~<t>t (reminder)` and `seen:`; the first, full prompt is in the 7.32.0 layout); green at the GREEN of plan increment 2 | green |
| REMINDER_KEEPS_NOTICE_LINES | X108, inside X109 (the same notice-body run) | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 2; red at the RED of plan increment 2 (notices print as `  ! <text>`, not `! <text>`); green at the GREEN of plan increment 2 | green |
| REMINDER_SAYS_SURFACED_NEVER_LOADED | X109 | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 2; red at the RED of plan increment 2 (the X108 notice compare fails first; no `seen:` line); green at the GREEN of plan increment 2 | green |
| LEDGER_NEW_IDS_LISTED | X110 | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 2; red at the RED of plan increment 2 (the full prompt is in the 7.32.0 layout; no `LOAD <n> ~<t>t (reminder)` header); green at the GREEN of plan increment 2 | green |
| REMINDER_DROPS_PEERS_ALREADY_SHOWN | X111 | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 2; red at the RED of plan increment 2 (no `skip (cross only if the task needs it):` block); green at the GREEN of plan increment 2 | green |
| LEDGER_EVERY_LOAD_ID_NAMED | X106, X107, X110, X113, X120 and X123 hold the six ledger states (absent, every id surfaced, one outside, `REFRESH_EVERY`, invalid JSON, count 0 after a reset), each by an exact-text compare | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_REFRESH_EVERY_N | X113; constant read by regex, N and N−1 | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_TRIVIAL_PROMPT_UNTOUCHED | X114; green on arrival; RED shown by mutation (trivial-prompt early return removed) | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_UNUSED_WITHOUT_GRAPH | X115; green on arrival; RED shown by mutation (no-graph path creating a file under `.cypress/session/`) | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_NEVER_EMITS_UNROUTED_ID | X116, inside X107: one unrouted id in the ledger, absent from the injection | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_ABSENT_SESSION_ID_FULL | X118; two envelopes, and it holds the CLAUDE_HOOKS_FAIL_OPEN_ON_COPILOT_ENVELOPE block | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_INVALID_SESSION_ID_FULL | X119; four ids through stdin (`../../escape`, `a/b`, `ab\x00cd`, `abc\n`) and `abc\n` through argv (`--session-id=abc\n`), one fresh plant per row, tree snapshot before and after | tests/test-prompt-hooks.sh | integration; the `abc\n` rows red at 7.37.0 increment 1 review (F2: a `$`-anchored `SESSION_ID.match` accepts the trailing newline, so ledger `abc\n.json` is written, both envelopes); green at its GREEN (`fullmatch` at every pattern check in route-hook.py) | green |
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
| BRIEF_TEMPLATES_BYTE_IDENTICAL | check | tests/seed-lint.py | verify gate; the slug sits in a comment beside the existing GRAPH DISCIPLINE identity check in `check` (not `main`, which holds no such check), and the verify record is `git diff --quiet <baseline> -- templates/prompts/graph-session-bootstrap.md templates/prompts/handback-payload.md`, where `<baseline>` is the 7.32.0 commit that lands owner rule R5's two sentences in step 4, commit `9ba5b4b` (until 7.32.0 it was `ac61a3f`, the 7.27.0 release commit, the parent of Slice A's first commit). From 7.35.0 the baseline is commit `dd7591d`, the commit that lands that round's template changes, the `COMPANION` block among them. Green on arrival (exit 0 at RED); RED shown by mutation (a byte appended to either template gives exit 1, and a drifted embedded block fails the identity check). Held at `pending` until the top-level-def scope defect in `check_spec_rows_name_their_contract` was fixed (§12); green since, and binding (the slug found inside the function) | green |
| BRIEF_TEMPLATES_BYTE_IDENTICAL | X396 COMPANION block drift: one word changed inside the `COMPANION` block of one embedding template is a finding naming that template | tests/test-seed-lint.sh | unit | green |
| ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE | X136; structural, substrings; was inside X135, which retired | tests/test-prompt-hooks.sh | unit; rewritten 2026-10-01 and its case at the RED of plan increment 1; red on arrival (no `--prompt=${`) | green |
| PRIME_EAGER_SURFACE_WITHIN_BUDGET | check_eager_surface | tests/seed-lint.py | unit; an existing check, run with check_published_eager_figures; green on arrival, and red on the section's arrival until the matrix figures are updated. RED shown by mutation (the overlay grown in a scratch copy fails the published-figures check). Held at `pending` until the top-level-def scope defect in `check_spec_rows_name_their_contract` was fixed (§12); green since, and binding (the slug found inside the function); rewritten 2026-10-01; the 7.37.0 RED kept the existing check as its case (no new test), and the published half is green once the release doc pass re-derived the matrix figures | green |
| ROUTER_FAILED | X142; non-zero exit, empty output, and timeout with `ROUTER_TIMEOUT` rewritten to 1 | tests/test-prompt-hooks.sh | integration | green |
| ENGINE_OLDER_THAN_HOOK_IS_NAMED | X177; mixed version: the real `v7.36.0` graph-lint.py, which rejects `--plan-json` (argparse exit 2), under the new route-hook, first prompt and a ledgered prompt: the pointer line and one notice line naming `graph-lint.py`, `--plan-json` and `graft`, the prompt absent, exit 0, no stderr, ledger untouched or absent | tests/test-prompt-hooks.sh | integration; red on arrival (the pointer line alone) | green |
| SESSION_ID_REFUSED | X119, the case of LEDGER_INVALID_SESSION_ID_FULL | tests/test-prompt-hooks.sh | integration; its cases pass at GREEN (2026-09-23), and each names this failure slug after its contract slug, on its OK and FAIL lines (`X1NN <SLUG>; failure …`); red again with X119's `abc\n` rows (F2), green at their GREEN | green |
| LEDGER_UNUSABLE | X120 (with its X121 and X122 rows), X130 (file symlink and FIFO) and X131, the cases of the contracts named there | tests/test-prompt-hooks.sh | integration; its cases pass at GREEN (2026-09-23), and each names this failure slug after its contract slug, on its OK and FAIL lines (`X1NN <SLUG>; failure …`) | green |
| LEDGER_DIR_UNUSABLE | X130, X131 and X132, the cases of the contracts named there | tests/test-prompt-hooks.sh | integration; its cases pass at GREEN (2026-09-23), and each names this failure slug after its contract slug, on its OK and FAIL lines (`X1NN <SLUG>; failure …`) | green |
| RESET_NOT_WRITTEN | X143, for the write-fails trigger; the sibling-missing trigger is X127 | tests/test-prompt-hooks.sh | integration | green |
| UNEXPECTED_EXCEPTION | X144; a status register printing non-UTF-8 bytes; red on arrival (a traceback) | tests/test-prompt-hooks.sh | integration | green |
| UNEXPECTED_EXCEPTION | X145; 100 000 nested `[` on stdin, both hooks; red on arrival (a traceback, no pointer line) | tests/test-prompt-hooks.sh | integration | green |
| ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO | X146; CRLF and lone-CR prompts against their `\n` twin; red on arrival (newline translation broke the echo match) | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01; at the RED of plan increment 1 its assertions stand unchanged against the `cypress.plan/1` stub | green |
| RESET_NOT_WRITTEN | X147, a second fault row of X143: the ledger stat fails | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_WRITE_FAILURE_FAILS_OPEN | X148; a ledger that would pass `LEDGER_MAX_BYTES`, one prompt: not written, full mode | tests/test-prompt-hooks.sh | integration | green |
| LEDGER_GC_BOUNDED | X149, a fault row of X134: GC's scan fails and the ledger is still written | tests/test-prompt-hooks.sh | integration | green |
| PLAN_ENTRY_NAMES_THE_NODE_FILE | test_plan_entry_names_the_node_file | tests/test_graph_lint.py | integration; the fixture puts one node at `docs/graph/agents/04-tester.md`, a path its id does not spell, with a `tester — ` title prefix; rewritten 2026-10-01 and its case at the RED of plan increment 2, red (`--plan` prints `task:`, padded columns and the 7.32.0 headers); still red at the GREEN of plan increment 2, for a harness reason: the `widget ledger tester` title adds task terms to `agent.tester`, its score lifts the cut above `subsystem.alpha`, and LOAD is two nodes (question file of the GREEN); green at the REFACTOR of plan increment 2, the fixture title now `tester — reads the gearbox`, which holds no task term | green |
| ROUTE_HOOK_KEEPS_THE_PATH | X151, inside X110: the full injection names every LOAD and skipped path; the reminder's new entry line and new `<id>=<path>` skip item carry theirs; the ledger holds ids only | tests/test-prompt-hooks.sh | integration; rewritten 2026-10-01 and its case at the RED of plan increment 2, red with X110; green at the GREEN of plan increment 2 | green |
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
| STATUS_HOOK_INJECTS_THE_ANCHOR_LINE | X164; structural: `settings.json` and the Copilot `status.json` wire `status-hook.py` under `SessionStart` alone | tests/test-prompt-hooks.sh | unit | green |
| ANCHOR_UNUSABLE | X157, the case of the contract named there | tests/test-code-anchor.sh | integration; the case names this failure slug after its contract slug | green |
| ANCHOR_COMMIT_UNREACHABLE | X157, the case of the contract named there | tests/test-code-anchor.sh | integration; the case names this failure slug after its contract slug | green |
| ANCHOR_CHECK_DID_NOT_RUN | X162, the case of the contract named there (X163 retired with STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE, 2026-10-01) | tests/test-prompt-hooks.sh | integration; it names this failure slug after its contract slug | green |
| PLAN_JSON_SCHEMA | test_plan_json_schema | tests/test_graph_lint.py | integration; the PLAN_* fixture plant (`plan_fixture_plant`), the notice task; red on arrival (`--plan-json` unrecognized). Since 2026-10-01 its task must load, skip and raise a notice under the SPEC-0002 ladder (a `wide_descent` task); the tester re-picks it | green |
| PLAN_JSON_CARRIES_NO_PROMPT | test_plan_json_carries_no_prompt | tests/test_graph_lint.py | integration; red on arrival (`--plan-json` unrecognized) | green |
| PLAN_JSON_HASH_BINDS_TASK | test_plan_json_hash_binds_task | tests/test_graph_lint.py | integration; five rows (one line, LF, CRLF, lone CR, non-ASCII); red on arrival (`--plan-json` unrecognized) | green |
| PLAN_JSON_EQUALS_PLAN | test_plan_json_equals_plan | tests/test_graph_lint.py | integration; since 2026-10-01 its `PLAN_TASK_SET` and its harness key need a `composed` entry under the SPEC-0002 ladder (row `pending` until the tester's rewrite); `PLAN_TASK_SET` (a notice with a composed entry, a node whose path its id does not spell, a rootless task that loads nothing, and from plan increment 2 an inferred entry); red on arrival (`--plan-json` unrecognized); its parser `text_plan` rewritten to the compact grammar at the RED of plan increment 2, red again until `--plan` prints that grammar; green at the GREEN of plan increment 2 | green |
| ROUTE_HOOK_READS_PLAN_JSON | X167; seven stub modes (bad schema, bad hash, off-pattern id, absolute path, `..` path, extra key, not JSON) | tests/test-prompt-hooks.sh | integration; red on arrival (the core reads the text view, so each gives a reminder) | green |
| ROUTE_FULL_TEXT_EQUALS_PLAN | X168; the `PLAN_TASK_SET` of tests/test_graph_lint.py over the real router, with an inferred-expertise task added at the RED of plan increment 2 (reviewer N1); `--plan` stdout is compared whole, with no echo removed | tests/test-prompt-hooks.sh | integration; red at the RED of plan increment 2 (`--plan` still prints its `task:` echo; on the inferred task it also prints ` via "<pattern>"`, which the document does not carry); green at the GREEN of plan increment 2 | green |
| HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE | X169; five route states, the status compact reset, and an unknown option on each hook | tests/test-prompt-hooks.sh | integration; red on arrival (no argv envelope: the argv run emits nothing) | green |
| CHILD_SESSION_GETS_NO_INJECTION | X170; `--depth=1` on both hooks, then `--depth=0`, absent and `x` | tests/test-prompt-hooks.sh | integration; red on arrival (the status hook injects at depth 1; the route hook ignores argv) | green |
| NON_HUMAN_TURN_NOT_ROUTED | X171; each `NON_HUMAN_MARKERS` entry through stdin and argv, `--origin=agent`, then `human`, absent and off-pattern | tests/test-prompt-hooks.sh | integration; red on arrival (a marker prompt is routed and counted); the `[bash-done ` (`[bash-done pid:1 exit:0]`) and `[harness-digest]` rows red at 7.37.0 increment 1 review (F1: both routed with a reminder and counted); green at its GREEN (both markers in `NON_HUMAN_MARKERS`) | green |
| SESSION_INJECTION_WITHIN_BUDGET | X172; tests/fixtures/session-injection/scripted-session.json over the PLAN_* fixture plant; the ceiling is read from tests/ratchets.json | tests/test-prompt-hooks.sh | integration; red on arrival (no argv envelope, so no full injection; and `SESSION_INJECTION_MAX_BYTES` is not registered until GREEN measures it) | green |
| PRIME_SESSION_ID_PASSED | X173 | tests/test-prompt-hooks.sh | unit; structural; red on arrival (no `getSessionId(`, `rlmDepth`, argv options) | green |
| PRIME_RESET_ON_EVENTS | X174 | tests/test-prompt-hooks.sh | unit; structural; red on arrival (status-extension.ts subscribes `before_agent_start` alone) | green |
| STATUS_ONCE_PER_SESSION | X175 | tests/test-prompt-hooks.sh | unit; structural; red on arrival (`let shown`) | green |
| PRIME_SESSION_UNKNOWN | X170 and X173, the cases of the contracts named in §7 (an unreadable depth is routed; no session id is full mode) | tests/test-prompt-hooks.sh | integration; each names this failure slug after its contract slug | green |
| STATUS_HOOK_ANCHOR_FAILURE_FAILS_TOWARD_INCLUSION | X165; structural: one `ANCHOR_TIMEOUT =` literal in `status-hook.py`, the `code-anchor.py --compare` run waits on it, `status-extension.ts` names no anchor, has one `pi.exec(` and its one timeout exceeds the core's waits plus `ANCHOR_TIMEOUT` | tests/test-prompt-hooks.sh | unit; structural; rewritten at the 7.37.0 increment 1 REFACTOR; no mutation run recorded | green |
| EVERY_RESOLVER_PATH_IS_INSTALLED | M11; reads `route-hook.py` CANDIDATES, `status-hook.py` CANDIDATES and ANCHOR_CANDIDATES, and each placed extension's `path.join(__dirname, "..", "hooks")` script, then requires each path in the installed plant | tests/test-install-placement.sh | integration; the status-hook lists added at 7.37.0 increment 1 review, red (`tools/status-register.py`: no installer writes it); M11 passes at its GREEN (the path dropped from status-hook.py CANDIDATES); the slug added 2026-10-01 at the RED of plan increment 2, and M11 names it | green |
| SHOW_KEEPS_EVERY_POINTER | test_show_keeps_every_pointer; every node of the `show_fixture_plant`, the expected values read from each raw file's frontmatter | tests/test_graph_lint.py | integration; red on arrival (`--show` is not an option: argparse exits 2); green at the GREEN of plan increment 2 | green |
| SHOW_DROPS_ROUTER_AND_SPAWN_KEYS | test_show_drops_router_and_spawn_keys | tests/test_graph_lint.py | integration; red on arrival (`--show` is not an option); green at the GREEN of plan increment 2 | green |
| SHOW_BODY_VERBATIM | test_show_body_verbatim | tests/test_graph_lint.py | integration; red on arrival (`--show` is not an option); green at the GREEN of plan increment 2 | green |
| SHOW_UNKNOWN_ID_FAILS | test_show_unknown_id_fails; a harness step first requires `--show root` to exit 0 | tests/test_graph_lint.py | integration; red on arrival (`--show root` exits 2: not an option); green at the GREEN of plan increment 2 | green |
| ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE | X176; one real path, then 21 real paths so the more-paths line must count after the filter; `--compare` and `--compare --all` | tests/test-code-anchor.sh | integration; red on arrival (the uncommitted line names all four build and backup files); green at the GREEN of plan increment 2 | green |
| ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE | X176, its second case: untracked `src/x.bak-config.yaml`, `src/config.bak/settings.py` and `src/y.py.bak-20260928-163636`; `--compare` and `--compare --all` name the first two and not the third | tests/test-code-anchor.sh | integration; red on arrival (`x.bak-config.yaml` is filtered); the `config.bak/` arm passes today, a guard held by a filter that matches a directory segment | green |
| PLAN_PRINTS_PLANT_BLOCK | test_plan_prints_plant_block; the `planted` fixture (PLANT_FACTS in index.md) and `main` (no block); the hook side is X168 over the `planted` row of PLAN_TASK_SET | tests/test_graph_lint.py, tests/test-prompt-hooks.sh (X168) | integration; red on arrival (the `planted` subtest: `--plan` printed no `plant:` line), green since increment 4; the `main` subtest is the guard | green |
| PLAN_PRINTS_PLANT_BLOCK, the unfilled-or-partial And | test_plan_prints_plant_block, subtests `placeholder` (`<ephemeral-test \| staging>`), `placeholder-commented` (`<ephemeral-test \| staging>  # x`) and `partial` (`comment_language` dropped) | tests/test_graph_lint.py | integration; added at increment 4 review FIX-2; `placeholder-commented` red on arrival (`--plan` printed `plant: environment_class=<ephemeral-test \| staging>  # x ...`: plant_block keeps the comment tail, so _unfilled sees no closing `>`); `placeholder` and `partial` green on arrival, guards; green since the FIX-2 GREEN (plant_block drops an inline `# comment` tail) | green |
| PLAN_PRINTS_PLANT_BLOCK, the reminder And | X178; the `planted` fixture plant: the full injection carries PLANT_LINE, the second prompt's reminder carries no `plant:` line | tests/test-prompt-hooks.sh | integration; added at increment 4 review N4; green on arrival, a characterization of an untested clause (route-hook.py reminder_text never reads the plan's `plant`) | green |

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
| Whether an `rlm()` child receives the `APPEND_SYSTEM.md` overlay | Decided whether a child keeps a set of its own | **Moot 2026-10-01:** the set is retired (ADR-0024) | architect | resolved |
| Whether a model on Prime Agent follows the section's instruction | The 7.28.0 Prime Agent saving depended on it | **Moot 2026-10-01:** the section is retired; Prime Agent residency is the core's ledger (ADR-0024) | owner | resolved |
| Model-side suppression on Prime Agent (security review) | Prompt-injected content could fill `_cypress_surfaced` | **Moot 2026-10-01:** the set is retired; the ledger is written only by the core, under the §6 persistence rules | security | resolved |
| The spawn-boundary claim for Claude Code hooks | I-2 rests on hooks not crossing into a spawn (`status-hook.py:13-15`) | taken from the hook's own docstring. The tester found no existing test of hooks at the spawn boundary (2026-09-23), so the test is not recorded, and this spec adds none | tester | residual |
| No behavioural test for the Prime Agent extensions | The extensions are proved by reading their text | Since 7.37.0 they are envelopes: the behaviour is the core's, run by the gate through the argv envelope; the envelope wiring is structural and the three host facts of §6 are probed live before GREEN | owner | residual; a TypeScript runtime in the gate, not planned |
| The prime-agent eager figure in `README.md:50` and `:338` | `check_published_eager_figures` matches only a figure followed by `B` or `bytes`, and these two lines carry none, so they can go stale with the gate green | updated by hand in the commit that adds the section | implementer | residual; a check change is outside this spec |
| A ledger or session directory owned by another user | The owner test of §6 has no gate case, since it needs a second account | the mode cases run in the gate (`LEDGER_FOREIGN_OR_WRITABLE_REFUSED`); the owner half is shown by reading the code at review | security | residual |
| How `pi.exec` decodes the child's line endings | The 7.28.0 extension matched an exact echo, which a decoded CR would break | **Moot 2026-10-01:** the core hashes the prompt it passes and the router hashes what it receives, so both see the same bytes; no echo is matched | architect | resolved |
| `getSessionId()` in `before_agent_start`; `rlmDepth` or `parentSession` on the session header; the extension's own directory under jiti | Prime Agent residency (first), child suppression (second) and finding the hooks (third) rest on them | not recorded; each failure falls toward inclusion (§7 `PRIME_SESSION_UNKNOWN`) | orchestrator | a live probe on Prime Agent before the GREEN of plan increment 1, recorded as evidence |
| Whether Claude Code's `UserPromptSubmit` envelope carries the turn's origin | The transcript records `origin.kind`; the hook would read it instead of `NON_HUMAN_MARKERS` | not recorded; the markers hold until a probe shows it | architect | a probe at the RED of plan increment 1 |
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
- 2026-09-30: 7.35.0, owner ruling D2 ("lint to keep the aligned"), by the
  architect, written ahead of its RED. The companion bullets that the five
  brief templates each worded for themselves become one canonical fenced
  block that opens `COMPANION`, in `graph-session-bootstrap.md`, embedded
  byte-identical in the five templates. BRIEF_TEMPLATES_BYTE_IDENTICAL's Then
  covers both canonical blocks, a new And-clause names the drifted template,
  and its baseline moves to the 7.35.0 commit that lands the round's template
  changes; the 7.32.0 baseline `9ba5b4b` stops matching the moment those
  changes land. §10 gains X396 (`tests/test-seed-lint.sh`), `red` until its
  RED lands; the existing `check` row is unchanged apart from the baseline
  note. No other contract changed; the status stays `active`.
- 2026-10-01: 7.37.0, by the architect, written ahead of its RED
  ([ADR-0024](../decisions/adr-0024-one-hook-core-per-session-residency.md),
  [ADR-0025](../decisions/adr-0025-compact-route-lines-json-between-programs.md),
  [ADR-0027](../decisions/adr-0027-first-move-runs-the-router.md); plan
  `docs/plans/grill-7.37.0-routing-context.md`). The sign-offs in §0 predate
  it and were not re-taken. Owner rulings D1 (Prime Agent residency), D3 (a
  slim node view that keeps every leaf pointer) and O1 (keep every path), and
  the owner's note that the cost is in subsequent prompts. One Python core,
  `route-hook.py` and `status-hook.py`, serves both first-class hosts: Prime
  Agent's extensions call copies at `.prime/agent/hooks/` through an argv
  envelope, and a child session or a turn a person did not type gets no
  injection. The core reads `graph-lint.py --plan-json` (`cypress.plan/1`)
  instead of parsing text. Models read a compact grammar that keeps the path
  on every id, and `graph-lint.py --show`. §4 gains, live from this entry:
  PLAN_JSON_SCHEMA, PLAN_JSON_CARRIES_NO_PROMPT, PLAN_JSON_HASH_BINDS_TASK,
  PLAN_JSON_EQUALS_PLAN, ROUTE_HOOK_READS_PLAN_JSON,
  ROUTE_FULL_TEXT_EQUALS_PLAN, HOOK_ARGV_ENVELOPE_EQUALS_STDIN_ENVELOPE,
  CHILD_SESSION_GETS_NO_INJECTION, NON_HUMAN_TURN_NOT_ROUTED,
  SESSION_INJECTION_WITHIN_BUDGET, PRIME_SESSION_ID_PASSED,
  PRIME_RESET_ON_EVENTS, STATUS_ONCE_PER_SESSION, SHOW_KEEPS_EVERY_POINTER,
  SHOW_DROPS_ROUTER_AND_SPAWN_KEYS, SHOW_BODY_VERBATIM, SHOW_UNKNOWN_ID_FAILS,
  ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE, and PLAN_PRINTS_PLANT_BLOCK (which
  lands only with ADR-0027). Rewritten: ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO
  (its And), ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE (`--plan-json=`),
  ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE (`--prompt=`),
  PRIME_EAGER_SURFACE_WITHIN_BUDGET (no overlay section),
  LEDGER_LATER_PROMPT_REMINDER, REMINDER_KEEPS_NOTICE_LINES,
  REMINDER_SAYS_SURFACED_NEVER_LOADED, LEDGER_NEW_IDS_LISTED,
  REMINDER_DROPS_PEERS_ALREADY_SHOWN, ROUTE_HOOK_KEEPS_THE_PATH and
  PLAN_ENTRY_NAMES_THE_NODE_FILE (the compact grammar), and
  HOOK_TEXT_RESTATES_NO_KERNEL_RULE (one re-baseline of its ceiling). Retired,
  with their §10 rows: ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY and
  UNPARSEABLE_ROUTER_OUTPUT_FULL (folded into ROUTE_HOOK_READS_PLAN_JSON:
  there is no echo, and an invalid document gives the pointer line alone);
  ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX, ROUTE_EXTENSION_TEXT_MATCHES_ROUTE_HOOK
  and STATUS_EXTENSION_INJECTS_THE_ANCHOR_LINE (the extensions compose no
  text); ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE (its fs-write ban moves into
  PRIME_SESSION_ID_PASSED; the core now holds the ledger on Prime Agent);
  PRIME_OVERLAY_KEEPS_SURFACED_SET, PRIME_OVERLAY_NEVER_SAYS_LOADED and
  PRIME_OVERLAY_SECTION_WITHIN_CEILING (the section is deleted); and the
  failures PRIME_MODEL_IGNORES_SURFACED_INSTRUCTION and
  PRIME_SURFACED_SET_TRUSTED_WHILE_STALE. §7 gains PRIME_SESSION_UNKNOWN, and
  ROUTER_FAILED's trigger names the document validation. §1 to §3, §5, §6
  (argv envelope, patterns, constants `NON_HUMAN_MARKERS` and
  `SESSION_INJECTION_MAX_BYTES`, the three router views, the injection texts,
  the mode decision, the Prime Agent envelope and host facts, the anchor
  filter), §8, §9 (AC-16 to AC-19), §10 and §11 follow. The texts change in
  two steps, in plan order: the core and the JSON first, on the 7.28.0
  reminder literals; the compact grammar second. Until each RED lands,
  `spec-lint.py` counts its contracts as uncovered. The status stays
  `active`.
- 2026-10-01: 7.37.0 plan increment 2 GREEN, by the implementer (spawn
  `orchestrator.10.implementer.3`), with the orchestrator's rulings on the
  RED's questions. §6 pins the skip-group order (peers before composed, by
  `via`, ids sorted within a group; the JSON `skip` follows it), keeps every
  frontmatter key `--show` does not classify, states that `--show` cuts the
  title as `--plan` does and keeps a directory entry's trailing `/`, names
  the reminder literals, and drops the transition sentences of the 7.28.0
  literals and the 7.32.0 layout. ROUTE_FULL_TEXT_EQUALS_PLAN compares
  `--plan` stdout whole. `HOOK_TEXT_MAX_BYTES` is re-baselined from 851 to
  724 (a tightening). No contract added; the status stays `active`.
- 2026-10-01: 7.37.0 increment 2 review fixes, RED by the tester (spawn
  `orchestrator.12.tester.6`), on the orchestrator's rulings for reviewer F1
  and F4. §7 gains ENGINE_OLDER_THAN_HOOK_IS_NAMED: an engine that rejects
  `--plan-json` gives the pointer line and one notice line naming the graft,
  never a `--plan` text fallback; ROUTER_FAILED's trigger excludes it and X177
  moves to its row. ANCHOR_IGNORES_BUILD_AND_BACKUP_NOISE and the §6 anchor
  filter narrow the backup match to `*.bak` and `*.bak-<digit>*`. §10 gains
  the two rows, `red`. The status stays `active`.
- 2026-10-01: 7.37.0 increment 2 review fixes, GREEN by the implementer
  (spawn `orchestrator.14.implementer.4`). ENGINE_OLDER_THAN_HOOK_IS_NAMED's
  trigger states how the hook tells an old engine from any other failure
  (exit 2 plus argparse's `unrecognized arguments: --plan-json`), and its
  recovery follows adr-0014: graft's engine step, not a re-install. The
  X176 second case and X177 rows turn `green`. The status stays `active`.
- 2026-10-01: 7.37.0, by `architect` (spawn `orchestrator.17.architect.1`),
  after increment 3's GREEN. Sign-offs not re-taken. The node router no
  longer promotes (SPEC-0002 `PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE`), so
  `promoted` leaves the `cypress.plan/1` kind enum and the `<how>` list; it
  never shipped in a release. PLAN_JSON_CARRIES_NO_PROMPT reads the `phrase`
  and `composed` details as node text. PLAN_JSON_EQUALS_PLAN's task set needs
  a `composed` entry. The PLAN_JSON_SCHEMA and PLAN_JSON_EQUALS_PLAN rows are
  `pending` until the tester re-picks their fixture tasks under the ladder.
  The status stays `active`.
- 2026-10-01: 7.37.0 release pass, by `architect` (spawn
  `orchestrator.26.architect.1`). PRIME_EAGER_SURFACE_WITHIN_BUDGET reads
  `green`: the round's RED kept `check_eager_surface` as its case, and the
  published figures it is run with were re-derived by the release doc pass
  (plan increment 5). Every §10 row is now green, so the status moves from
  `active` to `implemented`. No contract changed; §11 keeps its open
  question on Claude Code's turn origin.
