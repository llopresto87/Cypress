---
id: method.delegation-continuation
tier: 2
kind: method
origin: seed
title: continuation — when a finished or rate-limited agent is continued, when a fresh brief replaces it, and what a continuation message carries
owns:
  - delegation.continuation
requires:
peers:
  - method.delegation-bounds
  - method.delegation-briefs
load_when:
  - "resume or continue a finished agent, or brief a fresh one"
  - "an agent hit a usage or rate limit, resume it or spawn a replacement"
  - "send a follow-up to an agent that already handed back"
prevents: A finished worker continued at full context-replay cost on state that is no longer true, a follow-up sent to a worker the host cannot continue, and a replacement spawned beside a rate-limited worker that is still writing.
est_tokens: 687
---

# Continuing a worker (`delegation.continuation`)

A worker's turn ends when it hands back (`delegation.turn`, in
`method.delegation-bounds`). This node decides when the next piece of that line
of work goes to the same worker and when it goes to a fresh one.

**Continue a worker in two cases only; otherwise brief a fresh one.** Where the
host can continue a worker with its context intact, the default is still a
fresh worker with a full brief, carrying forward whatever the earlier worker
established. Continue the earlier worker only when:

1. it has finished, and the follow-up is a small change that needs the context
   it built (the files it read, the reasoning behind its edits), so that a
   fresh brief would have to rebuild most of that context; or
2. a usage or rate limit stopped it mid-turn (below).

The cost is the reason. A continued worker replays its whole accumulated
context on every call, and once any prompt cache the host keeps for it has
expired, that replay is paid in full; it also carries state the
follow-up may act on although it is no longer true (file contents other lanes
have since changed, instructions a ruling superseded). A fresh brief carries
only what the follow-up needs. The owner decided on 2026-10-14 that an agent is
resumed only for a small change that needs its whole context or after a usage
limit, and briefed fresh otherwise.

The continuation message carries what changed since the worker's handback or
its stop (files other lanes wrote, rulings, its write set re-stated), the
follow-up task, and the re-brief its graph needs (`delegation.briefs`). The
continuation is not a spawn, so the worker keeps its `spawn_id` and returns a
fresh handback payload.

A worker stopped by a usage or rate limit is still inside its turn: it has
not handed back. **Resume it once the limit lifts; never spawn a replacement.**
A resumed worker keeps its context and its write set. A replacement starts
cold, and while the original may still be alive the two are two writers on one
write set. The retry discipline is `protocol.recover`'s transient class. Judge
whether a worker is alive by its newest log or record entry and that entry's
timestamp, not by a status badge: a host can show a worker as failed while it
is still writing.
