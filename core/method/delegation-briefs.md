---
id: method.delegation-briefs
tier: 2
kind: method
origin: seed
title: delegation briefs — what every brief carries across the spawn boundary
owns:
  - delegation.briefs
requires:
peers:
  - method.delegation
  - method.delegation-cycle-economy
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/prompts/handback-payload.md
load_when:
  - "spawn a worker, write a delegation brief"
  - "shared rules file for several spawns, pass a handback by path, the brief is too big"
prevents: Briefs that drop the embedded graph discipline, paraphrase owner words, harden preferences into bans, or paste long handbacks through context.
est_tokens: 1352
---

## Every brief carries the graph discipline

No hook the seed installs carries this discipline or the routing
context into a worker's turn, so the brief is their only carrier across
the boundary. On Claude Code, hooks configured in settings also run
inside a subagent: its tool calls fire the same `PreToolUse` and
`PostToolUse` hooks as the main conversation, with the subagent named in
the hook input, and `SubagentStart` and `SubagentStop` mark its spawn
and finish ([hooks reference](https://code.claude.com/docs/en/hooks),
retrieved 2026-09-24). The seed's pre-Bash guard therefore fires on a
worker's Bash calls, but it guards commands and carries no routing
context. The route hook is prompt-scoped (`UserPromptSubmit`); the
hooks reference does not say that event fires for a subagent's turn,
and one observed run saw no prompt-injected text reach one. No hook the
seed installs reads a worker's result either, so the handback block is
the only reliable carrier back. Embed the canonical block from
`docs/graph/templates/prompts/graph-session-bootstrap.md` verbatim,
plus the routing evidence and the handback requirement
(`docs/graph/templates/prompts/handback-payload.md` — `produced_by` and
`route_evidence` feed the deliver-time attribution assertion,
`protocol.deliver`). Write that brief's task line in the domain's own
words — it is the string the worker hands to `--plan`, so the terms it
names are what compose the worker's expertise closure, and a task line
vaguer than the work loads a graph vaguer than the work. Parameterized
briefs live in `docs/graph/templates/prompts/`; use them.

**A fact the brief supplies is a lead, not evidence.** A path, a line number,
an identifier or a prior finding handed down in a brief is what the caller
believed when it wrote the brief; the worker confirms it against the artifact or
the register before building on it, and reports the correction when it does not
hold. The duty runs both ways: a correction to a supplied fact carries the same
burden of proof as the claim it corrects, so "the brief is wrong" is itself a
claim that cites the artifact.

The caller's half of that duty: **write a brief's status lines from the live
record** (the spec row, the commit log, the run record), never from the plan or
an older brief. A plan is a working record and goes stale, and a worker copies
what it is given.

**Name every concurrent writer.** A brief issued while other lanes are live
(`delegation.lanes`) names each concurrent writer and the files it holds. The
worker can then tell its own failures and edits from another lane's, and it
does not "fix" a file it does not own.

**Carry each constraint at its stated strength.** "Avoid X where you
can" is a preference the worker weighs against the goal; "no X" is a
bound it does not cross; "prefer Y" ranks options without excluding
the rest. Restating any of them as another is a brief-fidelity defect,
and it is the expensive kind: the worker inherits the distortion, not
the instruction, and reports a blocker that exists only in the brief.
Hardening a preference is as much a corruption as relaxing a bound —
tightening is not the safe direction, it is the direction that stalls
work nobody prohibited.

**When the owner's own words bind the work, quote them.** The brief carries
them verbatim, because a paraphrase is where strength drifts. An owner rule that
binds more than the current spawn is also written to a durable file that the
session and every later brief read. A rule held only in the caller's context is
lost at the next compaction and has to be taught again.

**A prohibition names its alternative.** A brief that forbids an action also
names the approved way to get what that action would have given, so the
forbidden path is never the easy one. The usual alternative for "do not touch
the live tree" is a before-copy in scratch, compared afterwards with `diff`,
`grep` or `wc`. A plain recursive copy of a checkout keeps its version-control
metadata, so the scratch copy must exclude it. Otherwise version-control
commands run inside the copy still find a repository, and in a copy of a linked
worktree that repository is the original. A worker that crosses a boundary reports the crossing in
its handback, and that report is correct behaviour. A brief rule alone does not
hold against a reflex, so where the host has a hook surface, the durable fix is
a pre-tool guard that refuses the forbidden command.

**Handbacks travel by path, not by paste.** When a worker needs an earlier
worker's handback, the brief gives it the path of that handback on disk and the
worker reads it there. The caller does not relay a long handback through its
own context. For a worker with no shell, the caller writes each needed handback
to a file without reading it into its own context, and the brief points at
those files. The handback template (`templates/prompts/handback-payload.md`)
owns what a handback carries and where its bulk goes.

**Shared rules go in one file.** When several workers run under the same
rules (the owner's words, the gates, the mechanics, the lanes, forbidden
tokens), the caller writes them once to one file, and each brief says "read
that file whole and obey it", followed by that brief's own part. The rules file
carries those shared rules and nothing more. It keeps briefs short, keeps every
worker on the same text, and survives a compaction of the caller. The graph
discipline block is still embedded verbatim in every brief: that one embedding
requirement does not move into the rules file.
