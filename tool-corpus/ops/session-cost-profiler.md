# Tool: session-cost-profiler

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the metric set and
> the checkpoint discipline are portable; the reader that extracts them from a
> harness's own session/subagent transcripts is host-specific, because each
> harness records a session in its own format. §3 specifies one adapter, for
> Claude Code, from Claude Code's own official documentation (§7); every other
> harness this seed integrates is **not recorded** and is an adapter-writing
> task for whoever adopts this page against it.

## 0. Identity

- **Category:** ops
- **Name:** session-cost-profiler
- **Language / runtime:** any (a reader for the host's own transcript format,
  plus simple aggregation, is the whole requirement)
- **Stability:** **blueprint** — no portable implementation. The metric
  contract (§2) and the checkpoint discipline (§3) are stack-neutral; the
  transcript reader is not, because it is bound to one harness's own
  recording format.

## 1. What it does

Reads a harness's own record of a session — the main conversation and every
subagent it spawned — and reports **how the session spent itself**: spawns,
tokens, and wall time broken down per agent type and per activity; the
interval between a RED test landing and the GREEN that closed it; the size of
each handback; where the session stalled; and how many times the full test
suite ran. It exists because a long session's cost is invisible while it is
still cheap to change and painfully visible only in hindsight — the gap
between "an early hour" and "a much later hour" of the same session is not
felt until someone totals the whole thing after the fact, by which point the
pattern that drove the cost has usually already repeated many times over.

It reports **two lines, never one**: a cost line and a quality line. A
session that got cheaper by skipping review, skipping red-before-green, or
skipping the full suite has not actually gotten more efficient — it has
moved its cost somewhere this profiler would miss if it measured spend alone.

## 2. Interface & invocation

```sh
session-cost-profile \
  --session <path or id the host uses to address one session's transcripts> \
  [--since <checkpoint marker>] \
  [--json]
```

- **Inputs:** the session's own transcript(s), read directly from wherever
  the host harness records them — never re-derived from a summary someone
  wrote about the session, and never from a handback's own self-reported
  numbers taken on faith (a handback's claim is exactly the kind of
  machine-written summary this tool exists to check against the transcript
  it describes).
- **Outputs:** two reported lines per checkpoint (§3) —
  - **Cost:** spawns and their model/effort class, tokens, and wall time,
    broken down per agent type and per activity; RED-to-GREEN intervals;
    handback sizes; stalls (a gap in the transcript with no tool call and no
    output, past a stated threshold); full-suite run counts.
  - **Quality:** review findings per increment (Critical/Major counts, not
    just "reviewed: yes"); RED tests logged before their GREEN (a "red tip"
    the session never actually watched fail); reversals (a change undone or
    re-done within the session); mutants killed/total where a mutation pass
    ran, or its explicit absence.
- **Exit codes:** 0 the report was produced; 1 the named session's transcripts
  could not be read at all; 2 usage error.
- **Preconditions:** read access to the host's session/subagent transcript
  store for the named session.

## 3. Approach / algorithm

### Run it at every batch checkpoint, not only at the end

The metrics this tool reports are exactly the shape of the "Session metrics"
block a delivery already carries at the very end of a session — spawn counts,
route bands, gate counts, full-suite run counts, and the review/mutant
quality line. What this tool adds is **when** to compute them: at each batch
boundary during the session, not only once at the end, so the cost curve is
visible while there is still time to change course. A number produced only
after the session is already over is a post-mortem, not a control signal.

### The Claude Code adapter (from Claude Code's own documentation)

Claude Code's official documentation (hooks and sub-agents pages, §7)
documents a hook-based subagent lifecycle, and that is the mechanism this
adapter is built on:

- **Spawn boundaries and agent type.** `SubagentStart` and `SubagentStop` are
  hook events matched on `agent_type`. A hook registered on those two events
  is the adapter's spawn-boundary instrument: it fires with the agent type
  already resolved, at exactly the moments a spawn starts and ends, with no
  need to parse a transcript file's own internal format to find them.
- **Hooks reach inside a subagent, not just around it.** Upstream documents
  that hooks from settings files, managed policy settings, and plugins also
  run inside subagents, and that `PreToolUse`/`PostToolUse` fire the same
  configured hooks there as in the main conversation, with `agent_id` and
  `agent_type` in the hook input to name the subagent. That gives the adapter
  a per-tool-call instrument inside a spawned agent, usable for stall
  detection (the gap between a `PostToolUse` and the next `PreToolUse`) and
  for counting activity by kind (which tool, how often) without needing the
  transcript's raw storage format either.
- **A hook attached to a subagent's own lifetime, not the session's.**
  Upstream documents that a hook placed in a subagent's own frontmatter runs
  only while that subagent is running and is removed when it finishes; a
  `Stop` hook there becomes `SubagentStop`. That is the scoping rule this
  adapter relies on to attribute a measurement to the one spawn that
  produced it, rather than to the session as a whole. A skill's frontmatter
  hook does not work this way: once the skill is invoked it keeps running
  for the rest of the session, so it cannot scope a measurement to one
  spawn. And a project-level subagent's frontmatter hooks are skipped until
  the folder holding the agent file is trusted; the subagent still runs, so
  an untrusted checkout yields a spawn with no measurement rather than an
  error on screen.
- **Not recorded, in Claude Code's official documentation, for this
  adapter:** the on-disk transcript file location and schema; how a token
  count or a dollar cost is exposed per turn or per spawn; how a handback's
  byte size is read back out of a completed spawn. These are the gaps a full
  implementation of this adapter would still need to close — by a further
  `ingest-library` pass against Claude Code's own current documentation, not
  by guessing a path or a field name here.

### Other hosts

Every harness besides Claude Code that this seed integrates (Prime Agent,
opencode, Codex, Copilot) is **not recorded** for this tool: this page cites
no source for any of their transcript formats, so no adapter is specified for
them here. Building one is a straightforward repeat of this page's method —
find what that harness's own documentation records about its session/subagent
lifecycle and hook (or equivalent) surface, and adapt §3's Claude Code section
as the template — but it is future work, not a fact this page invents.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the two-line report contract (cost and
  quality, never cost alone); the metric set in §2; the checkpoint discipline
  (run it at each batch boundary, not only at the end); reading the
  transcript directly rather than trusting a handback's self-reported
  numbers.
- **Blueprint (write per host):** the transcript/hook reader itself. §3 gives
  the Claude Code adapter's instrumentation points as far as the seed's
  source record documents them; every other host is unspecified here.
- **Adopting note:** where a harness exposes no hook or transcript-read
  surface at all, the quality line's inputs (review findings, red tips,
  reversals, mutants killed) may need to be sourced from the project's own
  gate logs and grill.md entries instead of the transcript — say so plainly
  rather than reporting an empty quality line as if nothing needed measuring.

## 5. Pitfalls and sharp edges

- **A cost number with no quality number invites the wrong optimization.** A
  session that spawns fewer agents by skipping review, or that shows fewer
  full-suite runs because it stopped running the suite, looks cheaper and is
  not — the two-line report exists precisely so a reader cannot see one
  without the other.
- **Trusting a handback's self-reported size or timing is circular.** A
  handback that misreports its own gate results is exactly the kind of
  claim-vs-artifact gap this profiler should be catching, not repeating; read
  the transcript, not the summary written about it.
- **A stall threshold that is too short reports normal thinking time as a
  stall, and one that is too long hides a real hang.** Calibrate it from
  measured durations of the task class actually being run, the same
  discipline `core/method/bounded-execution.md` already states for
  liveness thresholds generally — this tool does not get an exemption from
  that rule merely because it is measuring rather than executing.
- **A metric computed only once, at the end, cannot change the session it
  describes.** The entire reason for the checkpoint discipline in §3 is that
  a cost curve seen early is actionable and the same curve seen at delivery
  is a historical record.

## 6. Tests that cover it

Cover: the Claude Code adapter correctly attributes a `SubagentStart`/
`SubagentStop` pair to its `agent_type` and reports the elapsed wall time
between them; a `PreToolUse`/`PostToolUse` gap past the stall threshold is
reported as a stall and a gap under it is not; a hook-scoped measurement
taken inside one subagent's lifetime is never attributed to a different
concurrent spawn, and a tool event carrying `agent_id` is attributed to that
spawn, not to the main conversation; a spawn with no hook events at all is
reported as unmeasured rather than as a zero-cost spawn; the report always emits both a cost line and a quality
line, never one without the other; a session with no mutation pass reports
that absence explicitly rather than a zero that could be misread as "zero
mutants survived."

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/parallel-suite-runner.md` (a
  different axis of run-time measurement — per-module test wall time, not
  per-agent session cost); `tool-corpus/testing/failure-signature-triage.md`
  (post-hoc failure classification, a neighbor for the quality line's
  reversal/red-tip detection).
- **Sources:** Claude Code sub-agents docs, https://code.claude.com/docs/en/sub-agents
  (Anthropic, official); Claude Code hooks docs, https://code.claude.com/docs/en/hooks
  (Anthropic, official); the hook claims in §3 were checked against both
  pages on 2026-09-26. The Claude Code adapter in §3 is built only from what those pages document, and
  the gaps it leaves are named there rather than filled by inference.

## 8. Changelog

- 2026-09-26 — created by
  docs-librarian.
- 2026-09-26 — corrected after review: hook claims checked against the upstream hooks and sub-agents pages; skill frontmatter hooks are session-scoped, not spawn-scoped; the untrusted-folder gap.
