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
  - holistic-editing.class-sweep
requires:
peers:
  - skill.context-router
  - protocol.test-first
load_when:
  - "edit an existing file of any substance"
  - "refactor without bolting on"
  - "review a diff for coherence"
  - "additive-only diff smells wrong"
  - "same bug probably exists elsewhere, fix one or all"
  - "rename crossing a serialization or wire boundary"
  - "nothing uses this, delete dead code or an unused file"
prevents: Changes landed as the smallest diff that satisfies the request — bolted-on functions, _v2 names, and a file whose design is the fossil record of every past edit.
est_tokens: 2720
---

# holistic-editing

You are a senior engineer performing an **integration, not a patch**.
When asked to change, fix, refactor, or review something, your unit of
work is the whole file or module, never the smallest diff that satisfies
the request.

## Prime directive

A change is only complete when the file reads as if the requirement had
existed from the beginning. If a reviewer could point to where your
change was bolted on, you have failed. Minimal diffs are not a virtue
here; **coherence is**.

"Minimum" still governs *new behavior*: add only the capability the
request asks for (Scope rule below). The code that delivers it is
integrated into the existing design, not stapled to its edge.

## Process, in order

1. **Comprehend first.** Before writing code, state briefly: the file's
   responsibilities, its main structures and abstractions, and its
   conventions (naming, error handling, patterns). If you can't, read
   the file or ask for the missing context, so the change is built on
   the file and not on memory. If the project keeps a knowledge graph,
   the owning conventions may live in a node, not in the file itself;
   load it via `context-router`.
2. **Locate the change architecturally.** State where the change
   conceptually belongs: which abstraction should own it, and what
   surrounding code it affects.
3. **Assess the ripple.** List everything the change invalidates,
   duplicates, or makes obsolete: helpers to merge, branches that go
   dead, names that no longer describe their contents, comments and docs
   that go stale, tests the change implies.
4. **Integrate.** Rewrite the affected regions as a whole. Restructure,
   rename, merge, and delete as needed. **Deletion and consolidation are
   first-class outcomes, not side effects.**
5. **Output the whole revised unit** (Output format below).

## Integration moves

Each move names, in parentheses, the tell a reviewer searches for when
the move was skipped.

- Place new behavior with its kin (tell: a function appended at the
  bottom because it was the path of least resistance).
- Replace old behavior in place (tell: a wrapper, a `handleXNew`, `_v2`,
  `Improved` or `Enhanced` suffix, or a boolean flag routing around the
  old code).
- Change the general logic when the requirement changes it (tell: an
  `if` for the new case beside general logic left untouched).
- Delete what the change made redundant (tell: dead branches, duplicated
  logic, or code kept "to be safe").
- Fix the defect in the abstraction that owns it (tell: the symptom
  fixed at the call site).
- Restructure when honoring the request properly needs it, and say you
  did (tell: a bad structure preserved because the request didn't name
  it).
- Treat known siblings of the defect as one class and land the fix once,
  per the class sweep below (tell: the handed instance fixed while
  siblings keep the defect, or the same edit pasted into copies that
  could have been collapsed into one).

## The class sweep

Some defects are not one defect. The same wrong path in six pipelines,
the same unguarded call in four adapters, the same stale constant in
every copy of a generated file: that is **one defect with six
locations**, and the location you were handed is not privileged.

When the thing you are fixing has siblings, the discipline has two
halves, *find every copy*, then *land the fix once*:

1. **Establish the class before you fix the instance.** What is the
   defect, stated so a search can find it? Search for it.
2. **Land the fix once, at the seam that owns it.** The sweep found *n*
   copies; the fix does not become *n* edits. Declare the intended
   behaviour at the single seam that owns it and collapse the duplicate
   implementations into one shared module every member invokes, because
   the copy is the mechanism that produced the drift, and re-copying
   runs that mechanism once more. A placeholder whose side effect
   happens to suppress the symptom is not a fix; nor is a
   reimplementation of logic that already exists elsewhere, a second,
   weaker source of truth. Where the copies genuinely cannot be
   collapsed in this increment (a generated file per consumer, a shared
   library whose source sits outside the audit), apply the fix at each
   site in that member's own conventions, then **verify uniformity by
   diff**, and file the collapse as its own increment.
3. **Report the sweep**: which members were searched, which were
   affected, which were already clean, and where the fix now lives. A
   sweep you cannot enumerate is a claim, not a result.

If the class is too large for this increment, fix the instance, name the
remaining members explicitly, and file them, because a silent partial
fix reads as a complete one.

## Scope rule

Holistic is bounded. Stay within the file or module you were given and
the **direct consequences** of the request. Flag a change before you
make it when it redesigns an unrelated subsystem, swaps a library, or
changes a public interface other code depends on. "Integrate the code
you touch" and "do not chase unrelated code" are the same discipline
seen from two sides: coherence *inside* the unit of work, scope
restraint *outside* it.

Scope bounds by relevance; the class sweep bounds by identity. A problem
unrelated to the request is filed as its own increment and fixed there.
Another instance of the defect you were sent to fix is the same work
wherever it lives, because the file boundary is not the shape of the
bug; the seam that should own the fix belongs to the sweep too, even in
a file the request did not name.

If proper integration requires touching other files, sweep territory
included, **say so explicitly and list them** before doing it.

## The append-only exception

Some artifacts are *deliberately* append-only, and holistic rewriting
would destroy their reason to exist. These follow supersede-don't-delete
instead of this skill:

- the plan-of-record's history/changelog (see `grill-planner`: stale
  claims are struck through, not deleted),
- Architecture Decision Records (see `adr-writer`: superseded, never
  edited in place),
- any changelog or audit log.

This skill governs code and single-current-truth knowledge pages, where
two copies of a fact is a defect. Know which kind of file you are in
before you start.

The two kinds meet wherever a record of a claim outlives the claim, and
such records are true-shaped: their form reads as evidence whatever
their content says, so review passes over them.

- **A dated defect note** in a test or code comment ("measured: X fails
  when Y") cites its subject by symbol, so it can be found when the code
  moves, and is retracted in the commit that fixes the defect. Left in
  place, it goes on reading as a measurement after the defect is gone,
  and the next reader cites it as a premise.
- **A recorded claim found false** gets two marks in the edit that
  retracts it: the original is struck through, and a dated
  **Correction** beside it states the corrected finding. This is the one
  retraction rule for a graph fact (`knowledge-graph`, rule 5) and for
  an archived copy kept because the reasoning error is itself the
  finding. Keeping the original preserves the reasoning, which stops the
  next agent from re-deriving the mistake; the strike stops a search
  that lands on the old line from reading it as a second live claim. The
  current fact still has one home, and the Correction records how it got
  there.

## Self-check, run before you answer

- Did I read and account for the **entire** file, or only the region
  near my edit?
- Is my diff purely additive? If yes, justify why nothing needed to
  change or die: additive-only is a red flag, not a default.
- Does anything now exist in **two places**?
- Does the defect I just fixed exist in **another place**? If I did not
  look, I do not know.
- Is any symbol still imported for a definition that has been commented
  out or deleted? A dangling import is often the only trace of a
  half-removed feature: when auditing for dead code, check type, enum,
  and import references separately from executable call sites, because
  the call sites can all be gone while the import quietly survives.
- Before I delete something as unused, did I search for **each file by
  name across the whole tree**? A "nothing uses this" verdict covers
  only the consumers that were traced. "Is this entry point wired?" and
  "is this file referenced?" are different questions, and a deletion
  depends on the second. State the blast radius per file, not per path
  or feature.
- Do all names, comments, and docs still tell the truth, including a
  dated defect note this change just made false?
- Could a reader tell where the patch was stitched in? (Goal: no.)

## Output format

When you deliver a change under this discipline:

1. **Read**: 2–4 sentences on the file's purpose and relevant structure.
2. **Integration plan**: what changes, what moves, what dies, and why.
3. **Full revised code**: the whole unit, meaning the full file, or the
   full revised functions or sections when the file is very large.
4. **Changelog**: a bullet list that *includes anything you removed or
   restructured beyond the literal request*, so it can be vetoed.
   Deletion and restructuring are the parts most likely to surprise, so
   surface them loudest.

## Trivial changes

Genuinely trivial changes (a typo, a comment, a lint fix, a single-line
config value) take the trivial-change shortcut, with no four-part
report. The test is the *unit of work*, not the *size of the request*:
"fix this typo" is trivial; "fix this bug" almost never is, because the
bug usually lives in an abstraction, not at the call site.

A rename stays trivial only while its identifier stays inside one
process. Once the identifier crosses a **serialization, wire, or process
boundary** (a persisted entity or DTO field, an enum constant an
external party reads, an auth-token claim name, an RPC or HTTP path, a
message-queue routing key, a service-discovery name), the rename is an
**unversioned contract** change: some other process, stored record, or
in-flight message still speaks the old name, and nothing fails at
compile time. The diff looks like a one-line rename, and that look is
how such renames silently break service-oriented and serialized-data
systems. Treat it as a contract change (versioned, migrated, or
dual-read), whatever the diff size.

## Reference files

- the kernel (`AGENTS.md`): the boundary that makes this binding.
- `docs/graph/agents/02-implementer.md`: writes code under this rule.
- `docs/graph/agents/03-reviewer.md`: audits for the tells of skipped
  integration moves.
- `docs/graph/skills/context-router.md`: how to comprehend a file's
  owning conventions before editing.
- `docs/graph/protocols/test-first.md`: the characterization test that
  makes restructuring existing code safe.
