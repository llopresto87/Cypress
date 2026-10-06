---
id: method.delegation-bounds
tier: 2
kind: method
origin: seed
title: delegation bounds — spawn allowlists and depth, host registration, the turn, and the spawn trace
owns:
  - delegation.bounds
  - delegation.harness-registration
  - delegation.turn
  - delegation.tracing
requires:
peers:
  - method.delegation
  - method.delegation-briefs
load_when:
  - "delegation depth, allowlist, can this agent spawn"
  - "a spawn went silent, several spawns stalled at once, missing spawn_id"
  - "unknown agent type, specialist not registered, no such subagent"
  - "the roster was just installed, can I spawn it yet"
prevents: Uncapped spawn chains, dispatches to unregistered specialist types, completed workers re-tasked as correspondents, and untraceable spawns.
est_tokens: 2149
---

## Delegation is bounded

The coordinators (`orchestrator`, `multi-agent-architect`,
`growth-orchestrator`, `architect`, `reviewer`, `docs-librarian`) hold
the spawn tool and spawn only within their `delegates_to` allowlist.
On Claude Code the spawn tool is named `Agent`, and `Task`, the name the
shipped agents list, is its accepted alias; either grants it, bare or
parenthesized, and in a subagent definition the host ignores the
parenthesized type list, so the allowlist and `max_spawn_depth` are the
seed's own soft caps, read only by `agent-lint --lint`. The deepest
legal chain, depth 3, is likewise the seed's design ceiling, not the
host's.

Two caps are the harness's own. Every other agent is a spawn-less
leaf: its `tools:` line is present and names neither `Agent` nor
`Task` (a missing line inherits every tool, the spawn tool included),
which holds whenever the specialist was registered as a type (see the
next section for the case where it was not). And the host limits how
deep subagents may spawn subagents: the limit is configurable by
environment, its default is on the host's
[sub-agents page](https://code.claude.com/docs/en/sub-agents)
(retrieved 2026-09-24), and at the limit the host withholds the spawn
tool from every subagent except a fork. At an out-of-domain boundary a
leaf stops and hands back, naming the next specialist, because the work
belongs to that specialist's charter. `agent-lint --lint` enforces the
frontmatter invariants.

## A specialist is spawnable only once the host registered it

`docs/graph/agents/` is the home; a *spawnable* specialist is the host's
**projection** of it (`.claude/agents/`, `.opencode/agents/`,
`.codex/agents/`, `.github/agents/`), and when a host sees a file
written there mid-session is host-dependent. Claude Code watches its
project and user agent directories and uses a file added or edited
mid-session for the next delegation, with no restart, except in three
cases its sub-agents page names: the first file written into an
`agents/` directory new in that session, directories added with
`--add-dir`, and sessions started with slash commands disabled. A first
install into a plant with no `.claude/agents/` creates that directory
mid-session, so it is the first case. Other hosts are not recorded
here. Spawning a specialist by name therefore has two preconditions:
the session's project root is the plant, and the host registered the
projection. Prime Agent has no session-start roster enumeration: its
projection `.prime/agent/agents/` holds brief sources the orchestrator
passes into a runtime `rlm.spawn(...)` call, so a brief written
mid-session is spawnable at once and the trap below does not arise
there. Anything that *writes* a projection mid-session (the install, a
graft's roster delta, a newly commissioned expert: `delegation.routing`,
in `method.delegation`) can produce a specialist that is on disk and not
yet spawnable, so check registration before the first dispatch.

The installer's `project_agents` and `project_skills` project only the
top level of the plant's `docs/graph/agents/` and `docs/graph/skills/`
(a skill as the flattened `docs/graph/skills/<name>.md`, projected to
`<adapter>/skills/<name>/SKILL.md`) and skip `_`-prefixed files,
`index.md` and `README.md`. Place each node at that level: a node one
directory down is on disk and unspawnable.

**Preflight once per protocol, before the first dispatch.** Attempt one
throwaway dispatch of the type with a trivial task, or read the host's
own agent-listing surface if it has one. `agent-lint --route` answers
fit only: it globs the on-disk projection, so it can name at HIGH
confidence exactly the types an unregistered session cannot spawn.

**Remedy, in order.** (1) Re-enter the protocol from a session rooted at
the *plant*, the directory that owns the projection (for an umbrella,
the umbrella root, not a sibling repo). That also loads the plant's
kernel and route hook, which the install was supposed to guarantee
anyway. A session rooted at the seed never registers a plant's roster
however often it restarts: the seed is a source to copy from, not a
root to work in. (2) If your host offers an explicit reload of its
agent directory, that is cheaper; re-run the preflight afterward,
because an unverified reload is not a remedy.

**Fallback: role emulation.** When neither remedy is available, spawn
the host's generic worker and rebuild the specialist inside the brief:

- pin the model to the specialist's `model:` class
  (`delegation.model-classes`, in `method.delegation-model-classes`);
- embed `docs/graph/agents/<name>.md` **verbatim** as the worker's role;
- restore in prose every bound the frontmatter no longer enforces: the
  `tools:` allowlist as an explicit prohibition; for a leaf
  (`can_delegate: false`) "you hold no spawn tool: at an out-of-domain
  boundary STOP and hand back"; and for a **coordinator**, its
  `delegates_to` allowlist and `max_spawn_depth` as a named ceiling,
  and the sequencing rule (`delegation.sequencing`, in
  `method.delegation-sequencing`). An emulated coordinator with no
  restated ceiling is an uncapped spawner; one with no restated
  sequence issues every spawn at once;
- **carry this section down.** An emulated coordinator will reach its own
  by-name dispatches inside a subagent that cannot restart the session,
  so its brief hands it both the preflight and this fallback for its
  children;
- stamp `produced_by: <role>` (the role, never the generic type) plus
  `harness_override: role-emulated (<reason>)`, so `protocol.deliver`
  can tell a recorded emulation from a silent substitution. Stamping the
  role alone makes the two identical.

Role emulation is a degradation: a generic worker carries the spawn tool
and write tools, so the leaf recursion cap and the read-only bound drop
from harness-enforced to brief-requested. Scope it to the phase that
needed it, and report it in the delivery as a recorded deviation
(`protocol.deliver`).

## What a "turn" is

A **turn** is one **spawn → return cycle of a single worker**: the caller
spawns it, it works for as many tool calls as it needs, and it returns control
once. That return ends the turn. A turn is *not* one tool call, not one
assistant message, and not one exchange with the user.

A worker therefore hands back exactly once per spawn, on all three ways a
turn can end: it finished (`complete`), it hit work outside its domain
(`blocked-out-of-domain`), or it failed (`failed`). The payload is required
in all three; a leaf that stops at a domain boundary still returns it.

Because the turn ends at that return, a worker whose run has **completed** is
not a correspondent: sending it more work does not resume it. Continuing that
line of work means spawning a fresh worker with a full brief, and the new one
inherits none of the old one's context, so carry whatever the finished worker
established forward in the new brief. A caller who treats a completed worker
as re-taskable loses the follow-up silently: the work is neither done nor
refused, it was never spawned.

Wait for a worker still inside its turn: where the host delivers a completion
as an event, wait for that event and do other ready work meanwhile. One tell
is worth knowing: when several independent spawns go silent at the same time,
suspect the host (it slept, lost its connection, or hit a usage limit) before
the agents. Independent workers do not stall together by chance, so the fix
is on the host side, not in the briefs.

A worker stopped by a usage or rate limit is still inside its turn: it has
not handed back. **Resume it once the limit lifts; never spawn a replacement.**
A resumed worker keeps its context and its write set. A replacement starts
cold, and while the original may still be alive the two are two writers on one
write set. The retry discipline is `protocol.recover`'s transient class. Judge
whether a worker is alive by its newest log or record entry and that entry's
timestamp, not by a status badge: a host can show a worker as failed while it
is still writing.

Where a document means something else, it says so in words rather than reusing
this term: "per exchange with the user" for a conversational round, "each time
the caller re-reads the payload" for a caller-side read.

## Every spawn is traced

Every delegation carries a **`spawn_id`**, a dot-chained correlation id
the caller mints by extending its own: the session's first spawns are
`orchestrator.1`, `orchestrator.2`, …; a coordinator spawned as
`orchestrator.3` mints `orchestrator.3.architect.1` for its own first
child, and so on. The brief states it; the handback echoes it verbatim
(`spawn_id:` field, `templates/prompts/handback-payload.md`); the
delivery record and grill.md §15 cite it wherever a spawn's work is
referenced. The chain is the trace: any handback's id reconstructs the
full delegation path without any infrastructure, and an id deeper than
the caller's `max_spawn_depth` allows is a bound violation on its face.
Only a caller mints one; a leaf has no children to trace.

Before a session resumed after a compaction or a restart mints its next
`spawn_id`, it cites the highest ordinal already on record (the
plan-of-record, §15, or the handbacks on disk) and continues the chain from
there, because an id minted without that evidence may reuse one already
issued. **Mint a `spawn_id` at spawn time and at no other time.** A spawn
that ran without one is recorded as missing and cited by its artifact path
and commit, because an id minted afterwards to fill the gap is a fabricated
trace.
