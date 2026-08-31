---
name: canonize
description: The single end-of-task close-out spawn. At the completion of every non-trivial task, spawn the docs-librarian ONCE with a combined brief that (a) persists into docs/graph any knowledge of interest the work surfaced and (b) catalogs in docs/graph/tools any durable tool it produced (the toolcraft doctrine, kernel §3.8, executes inside this same spawn — never a second one). A task is not complete until both are done or explicitly recorded empty. For Tier 0/1 tasks (kernel §0), the session self-records "nothing of interest / no tool" in the delivery instead of spawning. Runs before deliver signs off.
id: protocol.canonize
tier: 2
kind: protocol
origin: seed
title: canonize — the single close-out spawn that persists knowledge and catalogs tools
owns:
  - rule.canonize
  - canonize.close-out-flow
requires:
  - protocol.toolcraft
peers:
  - protocol.deliver
  - protocol.harvest
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/tool-page.template.md
  - templates/skill.template.md
load_when:
  - "task is finishing, close out, before deliver"
  - "persist what we learned into the graph"
  - "spawn the docs-librarian, canonize"
  - "catalog a tool or skill the work produced"
est_tokens: 1300
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
the work surfaced, and cataloging its durable tools (the toolcraft
rule) in the same pass: facts land in the graph, durable tools land
in the catalog. Two doctrines, one execution — a second spawn with
the same bootstrap and the same lint run would be pure coordination
waste. The librarian owns the graph's **fact-bearing surfaces** —
nodes, wiki pages, the tool catalog — and one-home-per-fact; the
session never edits those. The session-owned operational artifacts
under the same root — grill.md, the verification runbook,
changelog.md — are the deliberate exception: the session writes them
directly. A delivery that changed understanding but left the graph
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

**Neither list includes:** ephemeral scratch, secrets/credentials,
production or personal data, speculation (write "not recorded"),
project-specific material aimed at the seed (that is `harvest`'s
agnosticism gate), throwaway prototypes or genuine one-offs.

## The flow (one spawn)

1. **Assemble candidates** from the finished work and the workers'
   handback payloads: facts with evidence, tools with path + entry point
   + invocation + covering test.
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
   from its owning node; each recurring procedure gets
   `docs/graph/templates/skill.template.md` filled into `.claude/skills/<name>/SKILL.md`
   (checking `skill-corpus/` first for a ready one, deduping against skills
   already present, composing existing disciplines by reference);
   `load_when:` triggers that failed to fire are sharpened. One `graph-lint`
   run confirms the graph stays clean.
4. **Confirm or record-empty.** The librarian hands back nodes/fact-keys
   touched and tool cards written, or an explicit "nothing of interest,
   because …" / "no durable tool, because …" — with the lint result.

## Fail-closed doctrine

A task is **not complete** until its knowledge is canonized, any durable
tool is cataloged, and any recurring procedure is crystallized into a
project skill — or each is explicitly recorded empty with a reason
(this node and `docs/graph/protocols/toolcraft.md` own the rule; toolcraft owns what
counts as durable). An uncaptured fact is a silent knowledge leak; an
uncaptured tool or procedure is a silent capability leak — the same
failure class as a green lie (§3.5). `deliver` (§3.6) does not sign off
until this close-out has run (or the T0/T1 self-record line is present).

## Relationship to the other protocols

- `deliver` produces the human-facing cold-pickup **summary**; canonize
  persists the machine-facing **graph knowledge and tool catalog**.
- `toolcraft` (`docs/graph/protocols/toolcraft.md`) owns the *doctrine* of what
  counts as a durable tool; canonize owns the *execution* — there is no
  separate toolcraft spawn.
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
- You do not canonize secrets, production data, or speculation.
- You do not duplicate a fact or a tool card that already has a home;
  update it in place.
