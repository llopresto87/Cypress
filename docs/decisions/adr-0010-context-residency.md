# ADR-0010: text enters a session once, at the lowest residency class that serves it, and the per-prompt hooks hold to that

## Status

`proposed`. Recorded 2026-09-24 at the close of the 7.28.0 "context residency"
harvest, planned in
[`../plans/grill-7.28.0-context-residency.md`](../plans/grill-7.28.0-context-residency.md)
and contracted in
[`../specs/SPEC-0003-per-prompt-injection.md`](../specs/SPEC-0003-per-prompt-injection.md).
The owner ratifies it. The owner decisions it transcribes were given on
2026-09-23 (plan §1.1 and §16) and are not re-opened here. It supersedes no
earlier ADR. It also carries the threat model security owes for the session
ledger (plan §17 row 9, SPEC-0003 §11).

## Date

2026-09-24

## Context

Before 7.28.0 the Claude Code route hook injected about 3.5 KB on every
non-trivial prompt. A scripted 20-prompt session injected 69,408 B in total
(plan §0.3), and most of it repeated: the same mandate paragraph on every row,
the same `root` and `skill.knowledge-graph` LOAD lines on 14 of 15 rows read,
and the same NOT LOADED peers. The mandate restated kernel FIRST MOVE and the
§0 tier table, a second home for rules the kernel already holds resident. A
defect made it worse: the hook stripped two lines of `graph-lint --plan`
output, so a multi-line prompt came back into its own session. One 6,010 B
prompt produced a 10,070 B injection carrying the prompt verbatim, and Prime
Agent's `route-extension.ts` had the same defect.

The method had a rule for which text enters a session (load minimally,
`rule.knowledge`) and none for how long it stays. Doing nothing leaves every
session paying for the same bytes on every prompt, and leaves any pasted
secret in a prompt duplicated into the injection.

## Decision

**Every text that can enter a session belongs to one of four residency
classes, placed by a test rather than by file type, and enters once, at the
lowest class that serves it, staying by reference until a reset; the per-prompt
hooks are held to this on each host as far as that host allows.**

### The rule and its home

The rule, its four classes (resident in full, resident as a pointer, once per
session, per lookup) and their placing tests have one home:
`skills/context-router/SKILL.md`, section "Residency", fact key
`context-router.residency`. This ADR records why and does not restate the
table. The plan's ledger (§2.2) placed every source the harvest found.

### The spawn-boundary exception

Repetition across a spawn is not duplication. A spawned worker starts with an
empty context and receives no hook output, so text that crosses into a spawn
is resident for that context and is sent in full every time. Dedup applies
within one context and never across a spawn. The brief templates therefore did
not change (I-2, `BRIEF_TEMPLATES_BYTE_IDENTICAL`), and the Prime Agent set is
never handed to an `rlm()` child (`PRIME_OVERLAY_KEEPS_SURFACED_SET`).

### A hook knows what it surfaced, never what the model read

The ledger records ids the router suggested and the hook showed. It cannot
observe whether the model opened, read or still holds them. So the hook never
says a node was loaded or read: its reminder line reads `Surfaced earlier this
session:` and tells the model to open what is not in view (I-6,
`REMINDER_SAYS_SURFACED_NEVER_LOADED`). The router's own `LOAD` and `NOT
LOADED` headers stay in full mode, because they are the router's
recommendation, not a claim by the hook.

### Fail toward inclusion

Every doubt resolves to the full injection (I-1): no session id, an invalid
one, a ledger that is corrupt, of unknown version, expired, oversized, from
another session, not a regular file, foreign-owned or group-writable, router
output that cannot be parsed, any `SessionStart` whatever its source, and every
`REFRESH_EVERY` (10) routed prompts. Two residual paths lean toward omission and
are recorded, not closed. On Claude Code, a failed reset at session start
leaves reminders running for at most `REFRESH_EVERY` − 1 prompts
(`RESET_NOT_WRITTEN`). On Prime Agent, a model that trusts a stale set after
compaction can skip a read (`PRIME_SURFACED_SET_TRUSTED_WHILE_STALE`). In both,
the router still names every routed id on every prompt (I-3).

### Why the ledger lives under `.cypress/session/`

The ledger is `<plant>/.cypress/session/<session_id>.json`. `.cypress/` is
where the seed already keeps per-plant state, and `find_lint()` already
resolves its root, so no new path rule was needed. But installed plants do not
gitignore `.cypress/`: `.cypress/seed.json` is meant to be committed, and the
`.gitignore` that carries `.cypress/` is the seed's own (plan §0.6). So the
hook makes the directory ignore itself: on first creation it writes
`.cypress/session/.gitignore` containing `*`, create-only and never rewritten
(`LEDGER_GITIGNORED`). No plant-owned file is edited and the installer gains no
write site. The hook never creates `.cypress/` itself, because that directory
marks a plant root.

### Per-host outcome under ADR-0009

| Host | Tier | Outcome |
|---|---|---|
| claude-code | first-class | Implemented: echo fix, `--plan=` as one value, the pointer line, the session ledger with reminder mode, and the reset in `status-hook.py` on every `SessionStart`. Enforced by the hook. |
| prime-agent | first-class | The echo fix and the pointer line in `route-extension.ts`, which keeps no state and injects in full on every prompt. Dedup is a model-kept variable, `_cypress_surfaced`, in the session's IPython kernel, instructed by the `## Surfaced nodes` section of the `APPEND_SYSTEM.md` overlay. Its enforcement class is soft under [ADR-0003](adr-0003-enforcement-layering-honesty.md), by owner decision (plan §16). No injected-byte saving is claimed. The section adds 350 B to the eager surface (24,094 B to 24,444 B), under a 512 B ceiling. |
| opencode | supported | Nothing ships. opencode has no per-prompt hook, so there is nothing to dedup; the gap is recorded in `documentation/host-capability-matrix.md`. |
| codex | frozen | Nothing. Upstream documents hooks the seed does not wire (ADR-0009). |
| github-copilot | frozen | Nothing new. Copilot runs the Claude Code hooks through `.claude/settings.json`, and its docs make `session_id` optional. Without one, every prompt gets the full injection and no saving is claimed; the hooks fail open on its envelope (`LEDGER_ABSENT_SESSION_ID_FULL`). |

## Threat model

The ledger is the first runtime state a seed hook writes into a plant, and the
per-prompt surfaces take the user's prompt as input. Condensed from SPEC-0003
§5, §6 and §7, where each mitigation is specified in full.

| Threat | Mitigation | Pinned by | Residual |
|---|---|---|---|
| The session id becomes a filename, so a hostile id (`../x`) could name a path outside the session directory | Read only from the exact key `session_id`; used only if it matches `^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$`, else treated as no id (full mode). `null` is absent. No stderr line carries a raw id, valid or not | `LEDGER_INVALID_SESSION_ID_FULL`, `SESSION_ID_REFUSED` | none recorded |
| Symlink, FIFO or TOCTOU substitution at `.cypress`, `.cypress/session`, the ledger or `.gitignore`, redirecting a write or hanging a read | Descriptor-relative I/O: directories opened with `O_DIRECTORY` and `O_NOFOLLOW`, every later call relative via `dir_fd`; ledger opened with `O_NOFOLLOW` and `O_NONBLOCK` and read only after `fstat` shows a regular file; temp file `O_EXCL`, moved with `os.replace` inside the directory descriptor. No path-string fallback: a platform lacking the flags or `dir_fd` support gets full mode | `LEDGER_SYMLINK_REFUSED`, `LEDGER_WRITE_IS_ATOMIC` | none recorded |
| Shared-plant ledger poisoning: another local user plants a ledger to suppress suggestions | Session directory and ledger refused unless owned by `geteuid()` and not writable by group or others; created 0700 and 0600. A poisoned ledger can only shorten entry lines, never add text: only ids in the current router output are emitted, and every LOAD id is still named | `LEDGER_FOREIGN_OR_WRITABLE_REFUSED` (mode half), `LEDGER_NEVER_EMITS_UNROUTED_ID`, `LEDGER_EVERY_LOAD_ID_NAMED` | a ledger owned by another user has no gate case, since it needs a second account; shown by reading the code at review |
| Prompt echo, duplicating a pasted secret into the injection, the ledger or stderr | The router output must begin with the exact prefix `task: <prompt>` and a blank line, built from the value passed; output without it is a router failure and yields the pointer line alone. The ledger stores ids only. A broader containment rule was retracted because it suppressed routing on short prompts (security S1) | `ROUTE_HOOK_STRIPS_MULTILINE_PROMPT_ECHO`, `ROUTER_OUTPUT_WITHOUT_ECHO_PREFIX_POINTER_ONLY`, `LEDGER_FIRST_PROMPT_FULL`, `ROUTE_EXTENSION_STRIPS_EXACT_ECHO_PREFIX` (structural) | on Prime Agent the rule is pinned structurally only; how `pi.exec` decodes line endings is Unknown (SPEC-0003 §11) |
| Argv injection: a prompt starting with `--` parsed as a router option | The prompt is one `--plan=<prompt>` element, with no shell on either host (`pi.exec` spawns with `shell: false`). A prompt holding NUL or over the OS argument limit is a router failure | `ROUTE_HOOK_PASSES_PROMPT_AS_ONE_OPTION_VALUE`, `ROUTE_HOOK_UNPASSABLE_PROMPT_FAILS_OPEN`, `ROUTE_EXTENSION_PASSES_PROMPT_AS_ONE_OPTION_VALUE` | none recorded |
| Denial of service: a flooded session directory, an oversized or deeply nested ledger, stale temp files, a slow router | GC runs only on ledger creation and reads at most `GC_SCAN_MAX` (256) entries; at most `GC_MAX_FILES` (32) ledgers kept, none older than `GC_MAX_AGE` (7 days); temp files swept after `TEMP_MAX_AGE` (1 h); `LEDGER_MAX_BYTES` (64 KiB) enforced on read and on write; a parser `RecursionError` makes the ledger unusable; `ROUTER_TIMEOUT` 15 s | `LEDGER_GC_BOUNDED`, `LEDGER_CORRUPT_FULL`, `LEDGER_WRITE_FAILURE_FAILS_OPEN`, `ROUTER_FAILED` | the Claude Code default hook timeout is not recorded |
| Model-side suppression on Prime Agent: injected content tells the model to fill `_cypress_surfaced` with ids it never opened | None in code; the set is soft by design. Bounded by the full injection on every prompt, which still names every routed id. The set holds public node ids only; a persistent session may snapshot it outside the plant tree | none; model behaviour is unobserved | residual, recorded in SPEC-0003 §11 |

## Evidence behind the targets

Measured on the scripted 20-prompt session of plan §0.3, against the 69,408 B
baseline. The close record is plan §18.

| `REFRESH_EVERY` | No resets | Resets at prompts 8 and 15 |
|---|---|---|
| 5 | 29,666 B | 35,224 B |
| 10 (chosen) | 22,301 B (−68%) | 26,958 B (−61%) |
| 20 | 16,972 B | 26,958 B |

N = 10 matches N = 20 once resets occur, and bounds how long a reminder can
drift from a full injection to 9 prompts. N = 5 costs 33% more than N = 10
without resets and 31% more with them, far above the plan's 10% threshold for
preferring it (plan §4.7). The echo fix alone takes the 6,010 B multi-line prompt from a
10,070 B injection to 3,653 B.

## Consequences

- The Claude Code hook owns a persisted format, ledger version 1. Any other
  version is unusable and replaced, so a later format change needs no
  migration.
- `status-hook.py` loads `reset_ledger` from its sibling and carries no path
  rule of its own (`STATUS_HOOK_RESET_OWNS_NO_PATH_RULE`).
- Per-prompt text may not restate a kernel rule. `seed-lint`'s
  `check_hook_text_restates_no_kernel_rule` derives what it looks for from
  `core/AGENTS.md` (I-8), and covers the Prime Agent overlay section too.
- The eager surface moves on Prime Agent only, by 350 B. `EAGER_BUDGET` is
  unchanged.
- The Residency Rule prose in the skill is fixed and unpinned: no gate asserts
  that it stays. The behaviour it governs on the hooks is pinned by
  SPEC-0003's 45 contracts. If this decision were silently reversed on Claude
  Code, `LEDGER_LATER_PROMPT_REMINDER` and `ROUTE_HOOK_POINTS_AT_KERNEL` would
  fail first.

## Alternatives rejected

### Shorten agent and skill descriptions to pointers now

Parked by the owner (plan §1.1, decision 1). `agent-lint` scores the agent
`description`. Cutting every agent description to 120 characters moved
`--eval` from rc 0 to rc 1: paraphrase confident-correct fell from 4 to 2,
under a floor of 4, and adversarial confident-wrong rose from 3 to 4, over a
budget of 3. Fourteen charter words are covered only by the description under
`CHARTER_VOCAB_DEBT` 12 at zero slack. Skill descriptions were parked with
them by the same decision. The options kept for later are in plan §18.

### A module-variable ledger in `route-extension.ts`

SPEC-0003's first draft held the Prime Agent ledger in a module-scope `let`,
reset on `session_start` and compaction. The owner chose the model-kept set
instead (plan §16). The draft carried open questions the chosen design does
not have: whether `session_start` fires before the handler registers, and
whether `rlm()` children share the module instance (SPEC-0003 §11, both moot
now). `ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE` pins the extension stateless.

### A ledger in the Prime Agent session file through `pi.appendEntry`

Rejected by owner choice. `ROUTE_EXTENSION_HOLDS_NO_LEDGER_STATE` forbids a
`pi.appendEntry` call in the extension.

### Reset on `PreCompact`

`PreCompact` fires before compaction, which can still be blocked or fail, so
it would reset without cause. It covers compaction only, leaving `resume` and
`clear` to a second path. And it would be a new hook entry in
`.claude/settings.json`, which Copilot also reads. `SessionStart` fires after
context is actually gone and is already wired (plan §4.5).

### Append `.cypress/session/` to the plant's `.gitignore` from `install.sh`

That file is plant-owned, the installer has no write site for it, and adding
one would put an edit to a team file inside SPEC-0001's placement contract. A
plant that never ran the hook would carry a rule for a directory it does not
have (plan §4.6).

## Reversibility

`reversible`. Removing the ledger is a code change in `route-hook.py` and
`status-hook.py`; ledger files already written are ignored by git through
their own directory's `.gitignore` and expire under GC, so no plant data is
migrated. `REFRESH_EVERY` is one literal. The Prime Agent section is one block
of an overlay the installer places. The Residency Rule is one subsection of a
skill. The one change that would not be cheap is dropping version 1 support
while plants still hold version-1 files, and I-1 already treats any unknown
version as absent.

## References

- Spec: `docs/specs/SPEC-0003-per-prompt-injection.md` (45 contracts; §5, §6,
  §7 for the threat model in full)
- Plan: `docs/plans/grill-7.28.0-context-residency.md` §1.1, §2, §4.5, §4.6,
  §4.7, §16, §17, §18
- Rule home: `skills/context-router/SKILL.md`, `context-router.residency`
- [ADR-0003](adr-0003-enforcement-layering-honesty.md) for the soft class;
  [ADR-0009](adr-0009-host-support-tiers.md) for the host tiers
- `documentation/host-capability-matrix.md`, row "Per-session injection dedup"
