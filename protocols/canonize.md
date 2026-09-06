---
name: canonize
description: The single end-of-task close-out spawn. At the completion of every non-trivial task, spawn the docs-librarian ONCE with a combined brief that (a) persists into docs/graph any knowledge of interest the work surfaced (b) catalogs in docs/graph/tools any durable tool it produced (the toolcraft doctrine, kernel §3.8, executes inside this same spawn — never a second one), (c) walks the open/hotfix status register item by item and moves — in frontmatter, with evidence — what this session actually moved, and (d) records every decision that departs from a standard the graph owns as both an ADR entry and a standing `deviation.*` node. A task is not complete until all four are done or explicitly recorded empty. For Tier 0/1 tasks (kernel §0), the session self-records "nothing of interest / no tool" in the delivery instead of spawning. Runs before deliver signs off.
id: protocol.canonize
tier: 2
kind: protocol
origin: seed
title: canonize — the single close-out spawn that persists knowledge and catalogs tools
owns:
  - rule.canonize
  - canonize.close-out-flow
  - canonize.status-review
  - canonize.deviation-capture
requires:
  - protocol.toolcraft
peers:
  - protocol.deliver
  - protocol.harvest
  - skill.adr-writer
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/tool-page.template.md
  - templates/skill.template.md
  - templates/docs/nodes/_deviation.template.md
load_when:
  - "task is finishing, close out, before deliver"
  - "persist what we learned into the graph"
  - "spawn the docs-librarian, canonize"
  - "catalog a tool or skill the work produced"
  - "status review at close-out: did each register item move this session"
  - "we departed from the standard, record the deviation and why"
est_tokens: 2200
command: true
---

# Protocol: canonize — the close-out spawn

This node owns **the canonize rule** — knowledge of interest is
captured before a task is done. Work generates knowledge and
capabilities; if either lives only in the session transcript, it dies
with the session and the next agent rediscovers or rewrites it the
hard way. Every T2/T3 task ends with **one** docs-librarian spawn —
the close-out — persisting into `docs/graph/` the facts, sharp edges,
corrected assumptions, provenance, and missed `load_when:` triggers
the work surfaced; cataloging its durable tools (the toolcraft rule)
in the same pass; moving the lifecycle status of whatever the session
closed, parked, or patched; and writing each deliberate departure from
a graph-owned standard as a standing deviation. Facts land in the
graph, tools in the catalog, status in frontmatter, deviations in
`nodes/` — one execution for all of it, because a second spawn with
the same bootstrap and the same lint run would be pure coordination
waste. The librarian owns the graph's **fact-bearing surfaces** —
nodes, wiki pages, the tool catalog — and one-home-per-fact; the
session never edits those. The session-owned operational artifacts
under the same root — grill.md and changelog.md — are the deliberate
exception: the session writes them directly, and the verification
runbook is written by the tester worker that ran the gates
(`docs/graph/protocols/verify.md` and
`docs/graph/agents/04-tester.md` agree on that). A delivery that
changed understanding but left the graph
untouched is a silent knowledge leak — the same failure class as a
green lie.

## When to invoke

- At the completion of every **Tier 2/3** task or increment (kernel §0),
  before `deliver`.
- Whenever the work surfaced a fact the graph does not own, contradicted
  one it does, or produced a tool a future session will run again.
- **Tier 0/1 shortcut:** a question answered or a trivial non-behavioral
  edit needs no spawn. The session writes one line in the delivery —
  "canonize: nothing of interest / no tool, because …" — and that
  satisfies the fail-closed doctrine. If a T0/T1 task *did* surface
  something durable (it happens), it escalates: spawn the librarian.

## What the one brief carries

**Knowledge candidates** (§3.7) — canonize this:
- a new or changed fact about the project's structure or capability;
- a sharp edge that bit (and the tell that would spot it next time);
- a corrected assumption — the graph asserted X, the work proved not-X;
- provenance for a claim (the source/path/symbol that grounds it);
- a `load_when:` trigger that should have matched this task and didn't;
- a new library idiom or pitfall learned while using a dependency.

**Tool candidates** (§3.8, `docs/graph/protocols/toolcraft.md` owns the doctrine) —
catalog any durable tool the work produced: recurs across sessions,
stable interface, test-authorized, lives in the repo. The worker
handbacks already name these in `tools_built`; the brief forwards them.

**Skill candidates** (§3.8, the procedure sibling of a tool — the
doctrine lives in `docs/graph/protocols/toolcraft.md`) — forward any repeatable
multi-step procedure the work walked that a future session will walk
again: named in `skills_built` on a handback, or the same sequence now
appearing a third time in grill/changelog. The brief forwards the
candidates; the librarian authors them.

**Status review** (`canonize.status-review`) — the brief instructs the
librarian to run `python3 docs/graph/status-register.py --open --hotfix`
against the tree as the session left it and walk the result item by
item, asking of each: *did this move this session?* What the work
closed gets `status: closed` + `status_evidence` (the gate run, commit,
or path#anchor that proves it); what it patched improperly is `hotfix`
with an `owner`; what it parked is `deferred` with `reopen_when`. Moves
land in **frontmatter only, never body prose** — the vocabulary and its
companions are `docs/graph/_schema.md` §"Lifecycle status". An item
that did not move is left alone: the librarian records the session's
moves, it does not close what the work did not close. The brief carries
the instruction, not the register's output.

**Deviation candidates** (`canonize.deviation-capture`) — every
decision made this session that departs from a standard the graph owns
(a fact key, a posture node, a `best-practices/` leaf, an external norm
the graph records). The brief names the decision and the standard; the
librarian asks **why** — of the session, or of the handback that
carries the decision — and writes BOTH homes: the ADR entry (the
history; `docs/graph/skills/adr-writer.md`) and a `deviation.<slug>`
node in `docs/graph/nodes/` (the standing truth: `status: standing`,
`departs_from`, `reason`, `scope`, `ends_when`, `recorded_in` naming the
ADR), in the form of `docs/graph/nodes/_deviation.template.md` (the
seed ships it in its `templates/docs/` mirror; the underscore keeps the
blank form out of the router). A departure with no node is a lapse the next
session will "fix"; one with no ADR is a decision nobody can trace; with
both, the router surfaces it exactly when the topic comes up and it is
never re-litigated or mistaken for a lapse. If nobody can say why, it
is not a standing deviation — record it `status: open` with an owner
and let the next session decide.

**Neither list includes:** ephemeral scratch, secrets/credentials,
production or personal data, speculation (write "not recorded"),
project-specific material aimed at the seed (that is `harvest`'s
agnosticism gate), throwaway prototypes or genuine one-offs.

## The flow (one spawn)

1. **Assemble candidates** from the finished work and the workers'
   handback payloads: facts with evidence, tools with path + entry point
   + invocation + covering test, and every decision that departed from a
   graph-owned standard, each with the standard it departs from.
2. **Spawn the docs-librarian once** (Opus-class; it owns `docs/graph/`)
   with a brief that embeds the canonical block from
   `docs/graph/templates/prompts/graph-session-bootstrap.md` plus both candidate
   lists. This spawn is fail-closed, and a `grow`/`graft` session reaches it in
   the same session that installed the roster — so if the host has no such type,
   apply `delegation.harness-registration`
   (`docs/graph/method/delegation.md`): re-enter rooted at the plant or
   role-emulate and record it. Skipping the close-out because the type would not
   resolve is not one of the options.
3. **The librarian persists and catalogs in one pass:** each fact lands
   in exactly one node's `owns:` (dedupe against what the graph already
   owns — update, don't duplicate); each tool gets
   `docs/graph/templates/tool-page.template.md` filled into
   `docs/graph/tools/<name>.md`, an index row, and an `artifacts:` edge
   from its owning node (checking `tool-corpus/` first for a ready card —
   when working in the seed repo, or when the plant has harvested the tool
   corpus); each recurring procedure gets
   `docs/graph/templates/skill.template.md` filled into its home node
   `docs/graph/skills/<name>.md`, plus the projection in each harness
   directory the plant actually uses (`.claude/skills/<name>/SKILL.md` and
   kin) — checking `skill-corpus/` first for a ready one under the same
   condition, deduping against skills already present, composing existing
   disciplines by reference;
   `load_when:` triggers that failed to fire are sharpened. Then the
   librarian runs the status register (`--open --hotfix`) and walks it
   item by item, moving in frontmatter — with evidence — what this session
   moved; and writes each deviation candidate as ADR entry + `deviation.`
   node once its *why* is on record. One `graph-lint` run plus the
   register's lint role (`python3 docs/graph/status-register.py --root
   docs/graph`) confirm the graph stays clean.
4. **Confirm or record-empty.** The librarian hands back nodes/fact-keys
   touched, tool cards written, status items moved (id → new status +
   evidence), and deviation nodes written — or an explicit "nothing of
   interest, because …" / "no durable tool, because …" / "no status
   moved" / "no deviation" — with the lint results.

## Fail-closed doctrine

A task is **not complete** until its knowledge is canonized, any durable
tool is cataloged, and any recurring procedure is crystallized into a
project skill — or each is explicitly recorded empty with a reason
(this node and `docs/graph/protocols/toolcraft.md` own the rule; toolcraft owns what
counts as durable). An uncaptured fact is a silent knowledge leak; an
uncaptured tool or procedure is a silent capability leak; a status the
work moved but the frontmatter still shows `open` is the same leak in a
third form (the next session redoes closed work, or trusts a hotfix as
a fix); an unrecorded deviation is the fourth (a deliberate departure
read as a lapse and reverted) — all the same failure class as a green
lie (§3.5). `deliver` (§3.6) does not sign off
until this close-out has run (or the T0/T1 self-record line is present).

## Relationship to the other protocols

- `deliver` produces the human-facing cold-pickup **summary**; canonize
  persists the machine-facing **graph knowledge and tool catalog**.
- `toolcraft` (`docs/graph/protocols/toolcraft.md`) owns the *doctrine* of what
  counts as a durable tool; canonize owns the *execution* — there is no
  separate toolcraft spawn.
- `adr-writer` (`docs/graph/skills/adr-writer.md`) writes the ADR that
  carries a deviation's history; canonize owns the moment it is captured
  and the `deviation.*` node that makes it standing truth.
- `harvest` folds **project-agnostic** lessons and tools into the seed,
  user-triggered only; canonize keeps **project-specific** knowledge and
  tools in the plant. What harvest's agnosticism gate rejects still
  belongs here.

## What you do not do

- You do not close a Tier 2/3 task without the librarian spawn, and you
  do not skip the T0/T1 self-record line "because it was minor".
- You do not spawn the librarian twice for one task's close-out; facts
  and tools travel in the same brief.
- You do not write the graph's fact-bearing surfaces from the main
  session; the librarian owns them (the ownership split and its
  session-owned exception are stated in the rule above).
- You do not move a status in body prose, and you do not close an item
  the work did not close — `closed` needs `status_evidence`.
- You do not record a departure from a standard in the ADR alone or in
  a node alone; both, or it is not captured.
- You do not canonize secrets, production data, or speculation.
- You do not duplicate a fact or a tool card that already has a home;
  update it in place.
