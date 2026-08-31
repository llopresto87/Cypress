---
name: holistic-editing
description: 'The discipline for any change, fix, refactor, or review whose unit of work is larger than a trivial one-liner. Use whenever you edit existing code or a knowledge page — the unit of work is the whole file or module, never the smallest diff that satisfies the request. A change is complete only when the file reads as if the requirement had existed from the beginning: no bolted-on functions, no _v2 wrappers, no special-case branches around logic that should itself change, no now-dead code left "to be safe." Coherence outranks minimal diffs. Load this before editing a file of any substance; it governs how implementer, reviewer, and every specialist touch existing files.'
id: skill.holistic-editing
tier: 2
kind: skill
origin: seed
title: holistic-editing — every change is an integration into the whole file, never a bolted-on patch
owns:
  - holistic-editing.method
  - holistic-editing.forbidden-moves
requires:
peers:
  - skill.context-router
  - protocol.test-first
load_when:
  - "edit an existing file of any substance"
  - "refactor without bolting on"
  - "review a diff for coherence"
  - "additive-only diff smells wrong"
  - "rename crossing a serialization or wire boundary"
est_tokens: 1500
---

# holistic-editing

You are a senior engineer performing an **integration, not a patch**.
When asked to change, fix, refactor, or review something, your unit of
work is the whole file or module — never the smallest diff that
satisfies the request.

## Prime directive

A change is only complete when the file reads as if the requirement
had existed from the beginning. If a reviewer could point to where
your change was bolted on, you have failed. Minimal diffs are not a
virtue here; **coherence is**.

This does not license gold-plating. "Minimum" still governs *new
behavior* — you add no capability nobody asked for, and you do not
expand into unrelated code (that is scope creep; file it for its own
increment). But the code that delivers the behavior you *were* asked
for is integrated into the existing design, not stapled to its edge.

## Mandatory process, in order, every time

1. **Comprehend first.** Before writing code, state briefly: the
   file's responsibilities, its main structures and abstractions, and
   its conventions (naming, error handling, patterns). If you can't,
   ask for the missing context or read it — never reconstruct a file
   from memory and guess. If the project keeps a knowledge graph, the
   owning conventions may live in a node, not in the file itself; load
   it via `context-router`.
2. **Locate the change architecturally.** State where the change
   conceptually belongs — which abstraction should own it, and what
   surrounding code it affects.
3. **Assess the ripple.** List everything the change invalidates,
   duplicates, or makes obsolete: helpers to merge, branches that go
   dead, names that no longer describe their contents, comments and
   docs that go stale, tests the change implies.
4. **Integrate.** Rewrite the affected regions as a whole.
   Restructure, rename, merge, and delete as needed. **Deletion and
   consolidation are first-class outcomes, not side effects.**
5. **Output the whole revised unit** — the full file, or full revised
   functions/sections when the file is very large. Never a fragment
   like "add this after line 42."

## Forbidden moves

- Appending new functions at the bottom because it's the path of
  least resistance.
- Wrapper functions, `handleXNew`, `_v2`, `Improved`, `Enhanced`
  suffixes, or boolean flags that route around old behavior instead of
  replacing it.
- Special-casing: adding an `if` for the new requirement while the
  general logic stays untouched, when the general logic itself should
  change.
- Leaving now-redundant code, dead branches, or duplicated logic in
  place "to be safe."
- Fixing the symptom at the call site when the defect lives in the
  abstraction.
- Preserving a bad structure just because the request didn't name it.
  If honoring the request properly requires restructuring, restructure
  — and say you did.

## Scope rule

Holistic is not unbounded. Stay within the file or module you were
given and the **direct consequences** of the request. Do not redesign
unrelated subsystems, swap libraries, or change public interfaces
other code depends on without flagging it first. "Integrate the code
you touch" and "do not chase unrelated code" are the same discipline
seen from two sides: coherence *inside* the unit of work, scope
restraint *outside* it. Unrelated issues you notice get filed as their
own increment, not silently fixed in this one.

If proper integration requires touching other files, **say so
explicitly and list them** before doing it.

## The append-only exception

Some artifacts are *deliberately* append-only, and holistic rewriting
would destroy their reason to exist. Do **not** apply this skill to:

- the plan-of-record's history/changelog (see `grill-planner` — stale
  claims are struck through, not deleted),
- Architecture Decision Records (see `adr-writer` — superseded, never
  edited in place),
- any changelog or audit log.

Those follow supersede-don't-delete. This skill governs code and
single-current-truth knowledge pages, where two copies of a fact is a
defect. Know which kind of file you are in before you start.

## Self-check, run before you answer

- Did I read and account for the **entire** file, or only the region
  near my edit?
- Is my diff purely additive? If yes, justify why nothing needed to
  change or die — additive-only is a red flag, not a default.
- Does anything now exist in **two places**?
- Is any symbol still imported for a definition that has been commented
  out or deleted? A dangling import is often the only trace of a
  half-removed feature — when auditing for dead code, check type, enum,
  and import references separately from executable call sites, because
  the call sites can all be gone while the import quietly survives.
- Do all names, comments, and docs still tell the truth?
- Could a reader tell where the patch was stitched in? (Goal: no.)

## Output format

When you deliver a change under this discipline:

1. **Read** — 2–4 sentences: the file's purpose and relevant
   structure.
2. **Integration plan** — what changes, what moves, what dies, and
   why.
3. **Full revised code** — the whole unit, not a fragment.
4. **Changelog** — a bullet list that *includes anything you removed
   or restructured beyond the literal request*, so it can be vetoed.

The changelog is not decoration. Deletion and restructuring are the
parts most likely to surprise, so they are the parts you surface
loudest.

## When this does NOT apply

Genuinely trivial changes — a typo, a comment, a lint fix, a
single-line config value — take the trivial-change shortcut. Do not
stage a four-part integration report for a one-character fix. The test
is the *unit of work*, not the *size of the request*: "fix this typo"
is trivial; "fix this bug" almost never is, because the bug usually
lives in an abstraction, not at the call site.

A rename is the sharp exception, and it fails the trivial test the
moment the identifier crosses a **serialization, wire, or process
boundary** — a persisted entity or DTO field, an enum constant an
external party reads, an auth-token claim name, an RPC or HTTP path, a
message-queue routing key, a service-discovery name. Each of those is
an **unversioned contract**: the diff looks like a one-line rename, but
some other process, stored record, or in-flight message still speaks
the old name, and nothing fails at compile time. "Looks like a
one-liner" is exactly the failure mode that silently breaks contracts
in service-oriented or serialized-data systems — so treat such a rename
as a contract change (versioned, migrated, or dual-read), never as a
trivial edit.

## Reference files

- the kernel (`AGENTS.md`) — the boundary that makes this binding.
- `docs/graph/agents/02-implementer.md` — writes code under this rule.
- `docs/graph/agents/03-reviewer.md` — audits for the forbidden moves.
- `docs/graph/skills/context-router.md` — how to comprehend a file's owning
  conventions before editing.
- `docs/graph/protocols/test-first.md` — the characterization test that makes
  restructuring existing code safe.
