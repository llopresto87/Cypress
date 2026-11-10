---
id: method.delegation-light-variants
tier: 2
kind: method
origin: seed
title: delegation light variants — a low-budget variant of a specialist for small mechanical work, and when it escalates
owns:
  - delegation.light-variants
requires:
peers:
  - method.delegation
  - method.delegation-model-classes
load_when:
  - "light variant, light reviewer or tester, one-line-fix implementer"
  - "small mechanical work on the investigation class, when a light variant escalates"
prevents: A cheap variant handed a security surface or a design question it cannot carry, or small work sent to the full agent for want of a bounded brief.
est_tokens: 717
---

## Light variants (`delegation.light-variants`)

**A light variant is a budget, not a new mandate.** A plant may instantiate a
low-budget variant of an existing specialist for small, mechanical work (a
pinned test, a one-line fix, a follow-up diff). The variant keeps the base
agent's mandate unchanged, runs on the investigation class at low effort, and
its definition `requires:` the base agent and names it as the escalation
target. Like any commissioned expert (`delegation.routing`, in
`method.delegation`), it joins only the project's roster.

It reads only the exact ranges its brief names, as `file:line` spans: the spec
rows, the diff hunks, the test functions. It still runs the graph discipline's
`--plan` and reports the output, but it loads only the nodes the brief names
and lists every other one as skipped, brief-scoped.

**Escalation is mechanical.** The variant stops with `blocked-out-of-domain`
and names the base agent as `recommended_next` when any of these holds,
whatever the work's size:

- deciding the work needs a line outside the ranges the brief names;
- the diff changes a line outside the hunks the brief names;
- the diff changes a spec contract, a public interface, a persisted format, or
  any line on a security surface (authentication, authorization, secrets, a
  credential holder, input from outside the trust boundary);
- the named ranges raise a question the brief does not answer: a second
  reading of a contract, or a design choice.

**Security surfaces go to the full agent.** Work that touches one runs on the
full agent at the class the table gives, whatever its size, because the
investigation class at low effort cannot carry a security surface. The caller
applies this before routing, and the third escalation condition is the
variant's backstop when the caller misjudged it.

**Still an independent reviewer.** A light reviewer is a reviewer at a smaller
budget, independent in the same way: someone other than the author, from
outside the lane whose output it reviews. It runs the independent review the
step requires, more cheaply, when the work is small.

**Size the brief to the class before routing to it.** The caller gives a light
variant the smallest context that decides the work: the exact ranges, the few
binding rules quoted, a short checklist, the gates and the handback. A caller
that cannot bound the reading that tightly has work that is not small, and
routes it to the base agent or splits it into briefs of one source each. A
brief that asks a variant to transcribe from several sources is not small
either, and the variant's decline is the correct outcome. The cost of the
re-route belongs to the brief.
