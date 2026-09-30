---
name: verify-disagreement
description: What to do when a check and its subject disagree, when a change must preserve behavior, and when a suite meets a known defect. Use when a gate fails and the code looks right, before a refactor or migration, or when tolerating a known bug.
id: protocol.verify-disagreement
tier: 2
kind: protocol
origin: seed
title: verify disagreement — preserved behavior, known defects, and a check that disagrees with its subject
owns:
  - verify.characterize
  - verify.measure-integrity
requires:
peers:
  - protocol.verify
  - protocol.verify-new-gates
load_when:
  - "refactor or migration must preserve behavior"
  - "golden master, stored oracle before a migration"
  - "the checker disagrees with the file, fix the tool or the declaration"
  - "tolerate a known defect, a known bug stays red until its fix lands"
  - "a gate fails and the code looks right, which one is wrong"
prevents: A refactor shipped on "the tests pass" with its behavior changed, a gate silently relaxed around a known bug, and a check satisfied by editing what it measures.
est_tokens: 1800
---

# Protocol: verify, disagreement and exceptions

## Behavior-preserving changes (refactors, migrations, dependency bumps)

When a change must preserve observable behavior (a refactor, a framework
or dependency migration, a re-platforming), the gate is **unchanged
behavior**, a stronger claim than "it builds and the tests pass". Two
disciplines make that mechanically checkable:

- **Characterize first, then change, and land the oracle as its own
  slice.** Before touching the code, capture a stored oracle of the
  current observable behavior (endpoint responses, persisted shapes,
  message payloads, computed outputs), one golden master per consumer,
  normalized to mask only volatile leaves (timestamps, ids, tokens).
  Capture it read-only: once a migration has overwritten the system,
  that evidence is unrecoverable. The oracle must exist and pass on the
  *pre-change* code and land **before any code change**, or the
  preservation claim is unfalsifiable; a new guard is seeded green from
  today's state and tightened only in the increment that can prove the
  tightening safe. On a codebase with no tests this baseline is often
  the only executable gate: say so, and treat effort estimates as
  floors carrying that risk. The test-shaped form of the same move, the
  characterization test that becomes your RED, is
  `docs/graph/protocols/test-first.md`'s characterize-first rule.
- **Diff against the baseline; allow only an enumerated intended-delta
  list.** After the change, re-capture and diff. The gate passes only if
  everything matches the baseline *except* an explicit list of intended
  deltas, each row naming the change and why the flip is a deliberate
  strengthening, not a convenience relaxation. Byte-identical output is the
  wrong contract; observable-behavior preservation is. An unexplained diff,
  or an additive-only edit to the pinning tests, is a red flag to justify
  before the gate is green, never a silent re-baseline.

## Tolerating a known defect

A suite that meets a confirmed bug keeps its gate as it is. The test that
uncovered the bug stays unchanged as the bug's acceptance check, and the bug
follows `test-first.known-bug` (in `protocol.test-first`): marked for
a fix, the owner told, `implementer` dispatched, the same test re-run. The
declared red advertises the hole until the fix lands; a relaxed, skipped or
re-pointed gate would hide it.

## When the check and its subject disagree

What a gate measures is the **effective state**: the resolved, merged,
deployed reality, read back through the same path a real client takes,
never a declaration, a source file, a tool's own change report, or an
exit code that says the state *should* have converged. A slice that
mocks a layer has not proven the architecture, and a check that reaches
the service by a shortcut cannot see faults in the path it skipped.

The same holds for a control: verify its flag value and its wiring on
every code path that can produce the outcome, not the presence of the
implementing code, the documentation, or the fact that the system works,
and state the strength it actually enforces, never the strength its name
implies; present-but-unwired permission machinery is protection that does
not exist.

Establish that wiring by following the invocation chain itself
(definition to build step to entry point to lifecycle hook) rather than
searching the repository for the gate's name: a component's automation
can be defined in a different repository than the code it guards, and a
gate can be invoked by a hook that never names it, so a name search
answers a question about text while reporting an answer about behavior.

When the check and its subject disagree, **the instrument is the first
suspect.** Put the prior on the checker: read the raw source at the
cited location and verify a tool's finding against the underlying data
before recording it. The checks, in the order a probe meets them:

- **Shell expansion.** A probe can be corrupted *before it runs*, because
  a shell expands the command you typed rather than the command you
  meant: a variable reference immediately followed by a delimiter the
  shell also reads as an expansion modifier, or a pattern handed unquoted
  to a program that does its own matching, is rewritten before the check
  ever sees its input. Prefer a probe that takes the path or pattern as
  its own argument, where no shell parsing can reach it, over one that
  splices it into a combined string (a `ref:path` or `host:port` token),
  and quote every glob meant for the program so the shell passes it
  through untouched.
- **Exit code over emptiness.** Read the probe's **exit code**, never the
  emptiness of its output: a corrupted probe and a clean negative both
  come back empty, and only one of them means what you are about to write
  down.
- **Contradictory measurements.** Two of your own contradictory
  measurements indict your method, not the other reader, unless the
  subject itself changed between the two readings.
- **Mutable subjects.** Two honest, dated observations of a *mutable*
  system that disagree are two facts about two moments, not one wrong
  measurement: keep both with their dates, and name the fresh observation
  that would settle which holds now as `not recorded` rather than
  guessing it.
- **Shape match.** Match the instrument's shape to the subject's: a
  line-oriented scan over multi-line constructs produces a number that
  looks like evidence and is not.
- **Resolver over parser.** When the measurement interprets a structured
  format (a merged configuration, a manifest, a lockfile), prefer the
  format's own resolver, offline where it can run, over a parser you
  write: a reimplementation encodes a modelling choice the real resolver
  does not share, and its answer describes your model of the format,
  which may differ from the effective state.
- **Retract with the tool.** A tool that produced a false positive is
  fixed or deleted in the same change that retracts its output; a
  discredited tool left in place will be quoted again.

Satisfy a check by fixing its subject or its instrument. Removing the
thing it observes (retiring an observed value is a separate, argued
decision from making it correct), falsifying the declaration the tool
reads (fix the tool, so the declaration keeps meaning intent), or
reverting the change that tripped it only silences the check. When an
assertion fails because the product *deliberately* changed, update the
assertion; a deliberate change, least of all a security revocation, is
never reverted to make a suite green. When it fails because it found a
real defect, the test stays as written and the defect goes to a decision
owner under the known-bug rule above, rather than the test being adjusted
until it passes; and when the test you discount was a contract's only
verifier, record the coverage loss with the discount.

A second measurement confirms the first only if it **re-derives the
result from the artifact by a different method**: a recount that reuses
the upstream number or premise is the same measurement written twice,
and three counts sharing one premise are one count.

## Neighbours

- `protocol.verify`: load when running the gates for a change.
- `protocol.verify-new-gates`: load when marking work closed, or
  adding a new gate.
