---
status: accepted
status_date: 2026-09-28
owner: seed steward
---

# ADR-0013: harness memory is not a home; a session writes what it learns to a session record in the plant, and canonize files it

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.31.0,
planned in
[`../plans/grill-7.31.0-wave-scheduling.md`](../plans/grill-7.31.0-wave-scheduling.md)
(§6, §7, §9, the memory-residency rows). The owner stated the rule and chose
where its harness instruction lives, so it is filed `accepted`. It supersedes
no earlier ADR. It narrows one clause of `method.stewardship-posture` §6 (below).
The owner's words are kept with the round's working records outside the seed.

## Date

2026-09-28

## Context

The owner stated the rule during the 7.31.0 round:

> "i don't want memories to sit in calude code or the harness memory as much as
> possible. memories instead should be codified into the plant - first as a
> "runtime/spec/session .md file" then picked up by docs-librarian in the
> canonize step and properly maintained"

On where the instruction to the harnesses lives:

> "we need the explicit instructions for the harnesses to live somewhere -i
> think this one should live in the kernel"

And on scope and timing: "fold it into the 7.31 with the rest", designed by a
fresh architect before the round's first RED.

The seed already holds most of this. What exists:

- `method.stewardship-posture` §6 (`stewardship-posture.compounding-knowledge`)
  says a standing owner rule is persisted in the graph, a plant-specific
  working rule goes to the plant's `crosscut.operator` node, and harness memory
  holds "at most a one-line pointer to that home, plus transient resume state".
  `templates/docs/nodes/_operator.template.md` points there.
- The kernel's §3.2 anchor ends "ahead of memory", and `skill.context-router`
  (`rule.knowledge`) says the graph outranks memory of APIs and versions.
- `protocol.canonize` takes worker handbacks, overflow notes, tool and skill
  candidates, the status register and deviation candidates as inputs.

What is missing:

1. **There is no place for a learning between the moment it is learned and
   the close-out.** An owner rule said mid-session, a corrected assumption,
   or where paused work stands, lives in the transcript or in harness memory
   until canonize runs. A session that ends early (its context is exhausted,
   or the owner stops it) loses what the transcript held, so harness memory
   has been where it survived.
2. **Resume state is explicitly allowed in harness memory.** Stewardship §6's
   "plus transient resume state" is the clause the owner's rule removes.
   During this round, a harness memory entry still described the previous
   release as in progress after it had shipped. Resume state in private
   memory is invisible to every other harness and to fresh-context workers,
   and nobody checks it for staleness.
3. **The kernel names no place.** "Ahead of memory" tells a session what to
   distrust, not where to write. A harness that keeps memory automatically
   fills it by default.
4. **One overlay instructs the opposite.** The Prime Agent overlay
   (`integrations/prime-agent/APPEND_SYSTEM.md`, the close-out bullets, and
   its README) sends "a cross-session operating lesson (a durable fact, …
   preference …)" to Prime Agent's own continual harness.
5. **Canonize names no session-level input.** Its inputs are the workers'
   handbacks. What the orchestrating session itself learned has no named
   input.

## Decision

Harness memory is not a home. The orchestrating session writes each learning
(an owner rule, a corrected assumption, resume state) to a session record at
`docs/graph/plans/sessions/<YYYY-MM-DD>-<slug>.md` at the moment it is learned,
and starts from the newest record. Canonize takes the record as a named input,
files each item in its one graph home or records why not, and lists the
harness-memory entries that can be retired. Retiring an entry is the owner's
decision, taken by name. The kernel's §3.2 carries one sentence pointing there;
the rule's one home is `method.stewardship-posture`
(`stewardship-posture.session-record`), and the filing step's home is
`protocol.canonize` (`canonize.session-record`).

The central tradeoff: the record is a plain file the session writes and a
future session must choose to read, where harness memory is injected
automatically. The kernel sentence closes that gap by telling every session to
start from the newest record. It costs 179 of the kernel's 248 free bytes.

## Consequences

- **Kernel.** §3.2 gains one sentence (the exact text is in the plan's
  kernel increment). The kernel grows from 7,752 to 7,931 bytes, leaving 69
  under `KERNEL_BUDGET`. Every harness's eager surface grows by the same
  179 bytes. The front-door pages that publish those figures
  (`README.md`, `documentation/host-capability-matrix.md`) are re-derived
  from seed-lint's computation in the same increment, because
  `check_published_eager_figures` fails on any figure it does not compute.
- **Stewardship §6** keeps its rule on standing owner rules and loses
  "transient resume state" as a harness-memory allowance. It gains
  `stewardship-posture.session-record`: what counts as a learning, when it is
  written, the path and shape, reading the newest record at session start,
  and migrating a harness that already holds memories. Workers do not write
  records; they hand back, and canonize already reads handbacks.
- **Canonize** gains `canonize.session-record`: the brief names the record
  or records, and the librarian walks every unmarked item, appends one status
  line per item to the record's "Canonize status" section, and hands back the
  harness entries that can be retired. The session owns the record, as it
  owns `grill.md` and `changelog.md`; the librarian only appends status lines.
  No sixth close-out duty is created: the record is a source of knowledge
  candidates, which the close-out already requires.
- **Placement.** The form ships as
  `templates/docs/plans/sessions/_session-record.template.md`. The installer's
  existing `templates/docs/**` walk (`place_docs_skeleton`, add-if-missing)
  places it, so every plant gets `docs/graph/plans/sessions/` with no installer
  code change. The underscore keeps it out of `graph-lint`, `graft-audit`'s
  unfilled-scaffold report and `status-register`. `graph-lint` does not scan
  `plans/` at all, and a record carries no `status:` key, so the register
  skips it. growth-audit's collection set is unchanged, because `plans/` is
  already a row.
- **Prime Agent overlay.** The close-out bullet that sent operating lessons to
  the continual harness now sends them to the session record. The continual
  harness keeps at most a pointer. This removes a contradiction rather than
  adding a second home.
- **Tests that fail if this is silently reversed.** Three:
  - seed-lint's kernel check fails when §3.2 stops naming
    `docs/graph/plans/sessions/` or `method.stewardship-posture`, or when
    `templates/docs/plans/sessions/` holds no form;
  - seed-lint's `ADOPTED_RULE_HOMES` entries fail when either new key loses
    its home;
  - the plant-state installer case fails when a fresh install lacks the form
    or a re-install touches a plant's records.
  The contracts are SPEC-0005 `KERNEL_POINTS_AT_THE_SESSION_RECORD` and
  `ADOPTED_RULE_HOMES`, and SPEC-0001 `SESSION_RECORD_FORM_IS_PLACED`.
- **Existing plants** receive the kernel sentence, the doctrine and the form
  by graft. A plant's `CLAUDE.md` is never edited in place.
- **Not tested, judged by review:** whether a session actually writes at the
  moment of learning, and whether the librarian's placement of each item is
  right. Both are `judgment` in ADR-0003's vocabulary.
- **Wiki:** none. No library is involved.

## Alternatives considered

- **Harness memory stays a home for resume state (today's §6).** It is
  rejected by the owner's rule. It is also private to one harness, unseen by
  fresh-context workers, and unchecked for staleness. This round met a stale
  entry.
- **The instruction lives only in each harness's overlay or adapter.** This
  is rejected for three reasons. The owner placed it in the kernel. Only one
  of the five hosts has an overlay a session always reads, so four would get
  no instruction. And five overlays would be five homes for one rule.
- **The full rule lives in `skill.context-router` (`rule.knowledge`), beside
  "ahead of memory".** This is rejected because the harness-memory rule
  already has a home in `method.stewardship-posture` §6, which the operator
  template points at. Moving it would leave a moved key and stale pointers.
  `context-router` is also a loading procedure and an oversized leaf. The
  kernel's §3.2 sentence names the one home, and `rule.knowledge` is
  unchanged.
- **A new node kind, or a new routable node, for session records.** This is
  rejected because a record is session-owned working state, like `grill.md`,
  not a fact-owning node. Routing it would put transient text in the router
  and give the graph two homes for each fact until canonize ran.
- **A dedicated spec for the track.** This is rejected. Seed-lint refuses a
  seed spec in `draft` (`check_spec_test_mapping`), so a spec written ahead
  of its RED would break the gate or claim a false `active`. The contracts
  also extend two existing mechanisms: SPEC-0005's adopted rule homes and
  SPEC-0001's placement.
- **The installer creates an empty `plans/sessions/` directory in code.**
  This is rejected. It needs a new write site that SPEC-0001's
  `SINGLE_WRITER` census would have to count, and git does not keep empty
  directories. Shipping the form through the existing walk creates the
  directory and delivers the shape in one file.
- **A shipped Claude Code setting that turns off the host's automatic
  memory.** Deferred, not rejected. The host fact is not recorded in the
  graph, and the setting would change a host default for every plant owner.
  It is put to the owner as an open question in the plan's §12.

## Reversibility

`reversible until tagged`. Before v7.31.0 is tagged, every piece is a revert
of prose, one template file and three test additions. After the tag, the
kernel sentence and the form have reached plants through graft, so removing
them needs a release of its own. No plant data is migrated either way. A plant's
records are its own files and stay where they are.

## References

- Spec: [SPEC-0005](../specs/SPEC-0005-cycle-economy.md) (`KERNEL_POINTS_AT_THE_SESSION_RECORD`, `ADOPTED_RULE_HOMES`), [SPEC-0001](../specs/SPEC-0001-install-placement.md) (`SESSION_RECORD_FORM_IS_PLACED`)
- Grill: [`../plans/grill-7.31.0-wave-scheduling.md`](../plans/grill-7.31.0-wave-scheduling.md) §6, §7, §9 (increments 10 to 13), §11, §12
- Doctrine: `core/method/stewardship-posture.md` §6, `protocols/canonize.md`, `core/AGENTS.md` §3.2, `templates/docs/nodes/_operator.template.md`
- Related: [ADR-0003](adr-0003-enforcement-layering-honesty.md) (enforcement classes), [ADR-0010](adr-0010-context-residency.md) (residency classes)
