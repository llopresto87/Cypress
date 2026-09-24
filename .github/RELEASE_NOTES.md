## 7.28.0 — context residency: the per-prompt hooks stop repeating what a session already has (2026-09-24)

**The Claude Code route hook now injects less than a third of what it did.**
Over the scripted 20-prompt session the harvest measured against, per-prompt
injection fell from 69,408 B to 22,301 B (−68%), and to 26,958 B (−61%) with
session resets at prompts 8 and 15. The hook keeps a session ledger of the node
ids it has already shown. A later prompt gets the pointer line, the full entry
line of each node new to the session, one `Surfaced earlier this session:` line
naming the rest by id, and only the peers not listed before. Every node the
router suggests is still named on every prompt. The full injection comes back
after any `SessionStart` (startup, resume, clear, compact, fork, or a source the
hook does not know), every 10 routed prompts, and whenever the ledger is
missing, unreadable, expired, oversized or from another session. The hook
never says a node was loaded or read, because it cannot know that; it knows
only what it showed.

**The refresh interval is 10 prompts, and the measurement chose it.** N = 5
gave 29,666 B without resets and 35,224 B with them; N = 20 gave 16,972 B and
26,958 B. N = 10 matches N = 20 once resets occur, and keeps a reminder at most
9 prompts away from a full injection. N = 5 cost more than 30% over N = 10 on
both runs, well past the 10% the plan allowed for preferring the shorter window.

**Multi-line prompts are no longer pasted back into the session.** The hook
stripped two lines of router output, so a prompt of several lines came back as
part of its own injection. A 6,010 B multi-line prompt used to produce a
10,070 B injection carrying the prompt verbatim; it now produces 3,653 B with
no echo. The hook removes the exact `task: <prompt>` prefix it expects, and
router output that lacks it is treated as a router failure and yields the
pointer line alone, so a secret pasted into a prompt is not duplicated. The
prompt now reaches the router as one `--plan=` value, so a prompt starting
with `--` cannot be read as an option. Prime Agent's extension had the same
echo and got the same fix.

**The mandate paragraph is one pointer line.** Each routed prompt used to
restate the kernel's FIRST MOVE and §0 tier table. It now says `Route first:
the kernel's FIRST MOVE and §0 apply to this prompt.` A new `seed-lint` check,
`check_hook_text_restates_no_kernel_rule`, derives the kernel's §0 cells and
FIRST MOVE steps from `core/AGENTS.md` and fails when either per-prompt surface,
or the new Prime Agent overlay section, repeats four words of them in a row or
names a tier.

**The ledger stays out of git and out of harm's way.** It lives at
`.cypress/session/<session_id>.json`. Installed plants do not ignore
`.cypress/`, so the hook writes a `.gitignore` of `*` into that directory the
first time it creates it and never edits a plant's own `.gitignore`. All
ledger I/O goes through directory descriptors that follow no symlink, a ledger
or directory owned by another user or writable by group or others is refused,
and garbage collection is bounded. `status-hook.py` resets the ledger on every
`SessionStart`. The threat model is in
[ADR-0010](docs/decisions/adr-0010-context-residency.md).

**Prime Agent gets the echo fix and the pointer line, and a surfaced set that
nothing enforces.** `route-extension.ts` keeps no state and still injects in
full on every prompt, so no saving in injected bytes is claimed for Prime
Agent. The `APPEND_SYSTEM.md` overlay gains a `## Surfaced nodes` section
asking the model to keep `_cypress_surfaced`, a Python set of the node ids it
has opened, in the session's IPython kernel, and not to re-open one whose
content is still in view. That is the owner's choice, and it is soft under
ADR-0003: model-kept, unenforced and unmeasured. The section costs every Prime
Agent session 350 B: its eager surface goes from 24,094 B to 24,444 B.

**Every other host's eager surface is unchanged.** Claude Code stays at
26,261 B. Shortening agent and skill descriptions to pointers was planned and
parked by the owner: `agent-lint` scores the agent `description`, and cutting
agent descriptions to 120 characters broke `--eval`. No pointer was shortened, so
none had to be lengthened back. opencode ships no per-prompt hook, so it has
nothing to dedup, and the gap is recorded in the host matrix. Codex and Copilot
are frozen and get nothing new; Copilot, which runs the Claude Code hooks
through `.claude/settings.json` and whose docs make the session id optional,
gets the full injection whenever it sends none.

**What stayed byte-identical.** `agent-lint --eval` output, and the two brief
templates every spawn carries, compared against the 7.27.0 release commit
`ac61a3f`. A spawned worker starts empty and receives no hook output, so it
sees exactly what it saw before. The harness-native selection measurement was
not run: neither the eager surface nor the first-prompt router suggestion
changed materially, since the only first-prompt change is the mandate
becoming the pointer line and the echo going away.

**The Residency Rule has a home.** `skills/context-router/SKILL.md` gains a
Residency section, fact key `context-router.residency`: text enters a session
once, at the lowest of four classes that serves it, and stays by reference
until a reset, with repetition across a spawn exempt. ADR-0010 records the
reasoning and stays `proposed` until the owner ratifies it.

**Also in this release.** Three contract slugs of the plant spec
`SPEC-0001-gate-assertion-floor`, lost from `tests/test-seed-lint.sh` when
7.23.0 renamed the cases that carried them, are restored as comments, so that
plant's `spec-lint` is green again. `check_spec_rows_name_their_contract` bound
a top-level function's scope to a single newline, so no top-level `seed-lint`
function could bind a green spec row; its anchor is fixed, with a planted case.
`SPEC-0003-per-prompt-injection` is `active` with 45 contracts, signed by
product, architect, tester and security.
