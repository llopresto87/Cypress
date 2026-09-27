---
id: method.maintenance-contracts
tier: 2
kind: method
origin: seed
title: maintenance contracts — who maintains each artifact, what a generated one owes, and which copy wins on drift
owns:
  - design-posture.generated-artifacts
  - design-posture.doc-code-precedence
requires:
peers:
  - method.design-posture
load_when:
  - "generated artifact, regenerate not hand-edit, staleness check"
  - "who maintains this file, human-maintained, script-generated, or AI-seeded"
  - "documentation drift versus the implementation, precedence rule, which one wins"
prevents: A hand-edited generated file that nothing checks for staleness, and two documents that disagree with no rule for which one gets corrected.
est_tokens: 932
---

## 12. Every artifact has one maintenance contract; a generated one carries its marker, recipe, and staleness gate

Never assume an agent will maintain the project. Every artifact is
labelled with exactly one of three maintenance contracts:

1. **Human-maintained.** A person edits it, so it is designed for a
   human reader: comments, a stable and meaningful order, no shapes
   chosen for a machine's convenience.
2. **Script-generated.** A deterministic script emits it, under the
   obligations below.
3. **AI-seeded, then human-maintained.** An agent fills it once, a human
   reviews it at seeding, and humans own it from then on. It gets no
   staleness gate and no regenerate-and-diff check, because there is no
   generator to re-run. Any comparison against another source is an
   advisory report, never a build failure.

*Generated* means a deterministic script produced it, never that an
agent wrote it. So a category-3 artifact never gets a derivation engine
as its source of truth: derivation was its one-time seeding method, and
at most it feeds an advisory drift report.

Calling an artifact *generated* obliges four things together, or the
word means nothing: an in-file marker, human- and machine-visible, at
the top, in whatever syntax the format allows (a first key where the
format has no comments), naming the command that regenerates it and
forbidding hand edits; deterministic, byte-reproducible regeneration; a
ban on hand edits — the artifact is rebuild output, not source, so an
upgrade regenerates it and counts none of it toward its change budget;
and a staleness gate that fails when the artifact no longer matches its
source. Record the input provenance — which revision of every input the
artifact was derived from — because a green regeneration proves nothing
without it. A committed, script-generated, hand-editable file with
nothing to catch the drift is a live defect, not a stylistic gap. Where
two tools need the same content, author it once and generate the second
view; the graft protocol's treatment of harness projections regenerated
from their graph node is this rule applied to the seed's own machinery
(`protocol.graft`).

## 13. Doc-versus-code drift is a defect with a stated precedence rule

Two artifacts that describe the same thing will disagree eventually; the
design decision is who loses. State the precedence once: **code decides
facts about itself** — what a module does, which command works, which
keys are read — and **the recorded contract decides contracts** — what
the code was required to do. A violation of a recorded contract is a bug
in the code, not a documentation update (`method.engineering-posture`
§1: when spec and code disagree, find out which is wrong and fix that one
deliberately; the kernel §4 forbids silently changing the spec to fit).
A roll-up index that disagrees with the artifact it summarizes loses,
the index is corrected, and the record names which copy drifted. A stale
operational document is worse than none, because it is trusted at the
moment it is used: every command in a runbook is expected to work, and a
change that stales it fixes it in the same increment — or marks it stale
where it can no longer be kept current. A citation to a decision record
that does not exist is a finding, sharpest where it authorized weakening
a control; label it inline-only provenance rather than following it as if
a review had happened. A mechanism that grew enforcement points and
dependents without a contract is contracted retroactively — a spec with
`status: back-written`, labelled as such — never left to accrete below
the documentation line.

## Neighbours

- `method.design-posture`: load when should I split this class, single
  responsibility.
