---
id: method.design-governance
tier: 2
kind: method
origin: seed
title: design governance — the project's contract outranks the brief and the industry default; maintained primitives for security-critical machinery
owns:
  - design-posture.project-contract-outranks
  - design-posture.maintained-primitives
requires:
peers:
  - method.design-posture
  - method.secrets-posture
load_when:
  - "task brief conflicts with the project spec or constraint, which outranks"
  - "roll your own crypto or session primitive, maintained library"
prevents: A brief, expert or industry default that overrides the signed spec by widening scope, and home-grown crypto, session or trust-anchor code.
est_tokens: 781
---

## 14. The project's own contract outranks the brief, the expert, and the industry default

When a task brief, a general design principle (including those in
`method.design-posture`), an outside expert's recommendation, or an
industry-standard convention conflicts with the project's signed
specification or a recorded constraint, the project's contract wins. Do
the smaller thing that honors the contract and escalate the conflict as
a deliberate spec change, re-signed, rather than resolving it by widening
scope on your own authority, which destroys the acceptance evidence the
spec produced. The goal-precedence order (safety, then explicit
requirements and binding contracts, then correctness…) is stated once in
`method.minimum-sufficient-work` §5; this section says what it means
when the *brief itself* is what conflicts.

Record the rejection *by constraint*, not on merit, so a later reader
does not reopen it as a technical dispute. A standing, deliberate
departure from a standard is a `deviation` node with its `ends_when`, so
a lapse is never mistaken for a decision nor a decision re-litigated as
a lapse.

An industry default is not automatically right: where the project has
measured that the standard shape re-opens a channel a hardening change
closed, it is refused. A chosen library's default that violates a
committed constraint is overridden explicitly inside the recorded
decision, beside the library's name. Centralize an owner-maintained
literal only when that refactor is requested; duplication alone does not
authorize it. An implementer's off-spec invention is read as a spec
defect: the spec left the value unstated, so specify it and pin it with
a test.

## 15. Adopt maintained primitives for security-critical machinery

Adopt a maintained component for cryptographic, session, and
trust-anchor primitives; rolling your own is a declined risk, not a
capability. Choose a trust anchor the environment can actually validate:
where a namespace is unreachable from a public issuer, own the root and
own a distribution path for every platform family you manage, because an
anchor nobody can verify is decoration. Close a vulnerability by
replacing the vulnerable component with a maintained equivalent that
keeps the capability; removing the user-visible feature is a regression
disguised as a fix. Where the system lives on a few hand-tuned queries
or a few readable outputs, prefer the component whose output you can
read and control over the one with the nicer developer experience. Where
data sovereignty or cost predictability outranks time-to-market,
self-hostable open components are a priced trade: the operational
surface is the price, accepted in the decision record rather than
discovered later. `method.engineering-posture` §11 owns the general
boring-on-the-production-path rule; this is its sharpest instance: on the
path that handles identity, money, user data, or production traffic,
novel is a synonym for untested, and the maintained library is the
boring choice. Handling the secrets themselves (channel, recording,
compromise, lifetime) is `method.secrets-posture`.

## Neighbours

- `method.design-posture`: load when should I split this class, single
  responsibility.
- `method.secrets-posture`: load when where do credentials live, dotenv
  values or a secret store, how a password reaches a subprocess.
