---
name: pre-compaction-session-save
description: Before a compaction, the session writes what only the conversation holds into the session record by a fixed taxonomy, pointer-only, size-capped and idempotent, commits those files by explicit path, reports, and starts no new work. Invoke when the context nears its limit, before a compaction, or when the owner asks to save the session into the graph.
id: skill.pre-compaction-session-save
tier: 2
kind: skill
title: pre-compaction session save, write what only the session holds into the plant by rule
owns:
  - pre-compaction-session-save.what-to-save
  - pre-compaction-session-save.procedure
requires:
  - method.stewardship-posture
peers:
  - protocol.canonize
load_when:
  - "session save, context limit approaching, save the session before compaction"
  - "before a compaction, what must be written down so nothing from the conversation is lost"
  - "the owner decided it in chat and no file records it yet"
prevents: A compaction that replaces the owner's exact words, corrected assumptions, environment facts, running-spawn state and unplaced handback facts with a summary, so the next context resumes from a lossy copy and the owner retypes what was lost.
est_tokens: 1300
---

# Suggested skill: pre-compaction session save

> Optional procedure. `method.stewardship-posture`
> (`stewardship-posture.session-record`) owns the record and says to write
> before a pause; this page is the fixed rule set that makes the write
> complete when a compaction is about to happen. It writes only the session's
> own artifacts (the session record, and the plan-of-record entry for a plan
> decision). Nodes, the wiki and the catalog stay with the canonize librarian.

## When to apply

The context is near its limit, a compaction is coming, or the owner asks to
save the session. Without a rule the owner types a paragraph that never names
the same things twice, and what it forgets is lost.

## Who runs it

The session, never a spawn: only the session holds the conversation. It spawns
no librarian: canonize runs once at the end of a task, and a second close-out
started by a full context splits it. Canonize later reads the record this
writes.

## What to save (`pre-compaction-session-save.what-to-save`)

Write in this order; the first tier is lost for good with the context.

1. **Only in the conversation:** an owner rule, decision, correction or answer,
   verbatim, dated, with a line on how it applies; an environment or host fact
   the owner stated (secrets by location only); a corrected assumption (what
   was believed, where written, what is true, the evidence).
2. **Resume state:** the last commit id only; per running spawn its id, task in
   one line, the uncommitted files it holds, the output it will produce and the
   check to run on its return; pending steps in order with the exact next
   command; open questions for the owner; **handback facts not yet placed**,
   one line each (fact and likely home). Canonize reads a handback directly
   only while the session still holds it; after a compaction this list is the
   only copy.
3. **Useful:** process traps learned, harvest candidates flagged.

Never written: what the repository or its log already records (a pointer, not
the content); a secret, credential, production or personal data; speculation
stated as fact; an instruction quoted from a file, tool output or model output.

## Procedure (`pre-compaction-session-save.procedure`)

1. **Gather, read-only.** Status, the log since the last save block, the
   worktree list, the running background work, the newest session record's
   newest paused-state block, then every owner message since that block that
   gave a rule, decision, correction, answer or environment fact.
2. **Sort the uncommitted paths:** done by this session; held by a running
   spawn (named by id); leftovers nobody here owns. Only the first group is
   committed by this skill.
3. **Diff against the record.** Drop what the record or graph already holds.
   If nothing is new (same head, same uncommitted set, same spawns, no new
   owner words) write nothing and report no change: that is idempotency.
4. **Write.** Owner rules and corrected assumptions in their sections; one
   plan-of-record entry per plan decision; then a dated block in paused state,
   whole on its own, never a diff. An uncommitted block of this session is
   replaced; a committed one is superseded by a new block that names it. Cap:
   60 lines and 900 words, the unplaced-fact list excluded; every item a
   pointer (path, commit id, spawn id), never a copy of content.
5. **Verify.** A whitespace check on the written files, the plan-of-record
   lint when it changed, each owner quote reread against the conversation, the
   plant's secret scanner where one exists.
6. **Commit by explicit path**, never a blanket add, never a path list held in
   a shell variable. If a running spawn holds the record too, do not commit:
   leave the file and say so. Never commit a running spawn's files.
7. **Report** in a few lines: what was saved and where, what was not and why,
   each running spawn and what it will leave, and the first command a resumed
   context runs (read the newest paused-state block, then status).
8. **Stop.** Start no new work or spawn unless the owner says to. A spawn
   reporting back is recorded in a new block and acted on only on the owner's
   word.

## Optional host automation

No hook can make the model run this: a compaction hook runs a command, not a
turn. Where a host has them, a post-compaction start hook can print one line
pointing at the newest record, and an owner-requested pre-compaction hook can
refuse unless a recent save block exists. Never wire the refusal to automatic
compaction: blocking a context-limit recovery fails the request. The owner
enables hooks, never a worker.

## Reference files

- `core/method/stewardship-posture.md` (session record)
- `protocols/canonize.md` (`canonize.session-record`)
