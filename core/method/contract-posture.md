---
id: method.contract-posture
tier: 2
kind: method
origin: seed
title: contract posture — fail loudly on missing input, reject out-of-domain values, own the unversioned contract, assert order and precision, honest errors, server-side authorization, visibility on every read surface, payload-free logs
owns:
  - contract-posture.required-input
  - contract-posture.domain
  - contract-posture.unversioned
  - contract-posture.ordering
  - contract-posture.errors
  - contract-posture.authorization
  - contract-posture.read-surfaces
  - contract-posture.logging
requires:
peers:
  - method.secrets-posture
  - method.release-posture
  - method.incident-posture
  - method.design-posture
  - protocol.specify
  - skill.holistic-editing
load_when:
  - "missing env var or required config, add a default or fail loudly at startup"
  - "invalid or malformed input, clamp coerce repair or reject it"
  - "message format between two services with no schema registry, who owns the contract"
  - "field order, list ordering, or decimal rounding precision in a serialized payload"
  - "what should the error response say, status code, leaking a stack trace"
  - "authorization check, derive the acting user from the token not the request body"
  - "soft delete, visibility predicate on every read surface, cache key leak"
  - "what to log, correlation id, never payloads or tokens"
est_tokens: 1900
---

# Contract posture

The promises a running system makes at its boundaries: what it accepts
and refuses, what it tells a caller, who it believes, what it shows, what
it writes about itself. Where validation and error handling *live* is
`method.design-posture` §6; this node owns what the contract must say.

## 1. Missing required input fails loudly, at one layer, naming the offender

Required configuration, credentials, and fields are validated once at
the earliest common layer — one schema-checked module the rest of the
code may not bypass — and a missing one fails the run with a non-zero
exit naming every offender. A default added to silence the failure
converts a loud deploy failure into a silent wrong value in production;
an interpolation that substitutes blank is the same defect. A service
whose security depends on a supplied secret refuses to start without it
and says which one; a known sample or placeholder value is a boot
failure; a configuration that can disable a security control fails
closed at startup rather than trusting every deployment path to override
it. Optionality is declared — "optional" means the artifact works
without it — never inferred from a loader's behaviour, and a field whose
absence would bind a silent zero in a non-nullable type is mandatory. The
guard against a fallback that substitutes a *value* is `protocol.verify`'s.

## 2. Reject out-of-domain input rather than repairing it

A component that receives a value outside its domain refuses it and
persists nothing — never rounds, clamps, truncates, coerces, merges, or
substitutes — because downstream the repair is indistinguishable from
the measurement; refusal is non-destructive and retryable. Schema-validate
every input at the boundary so nothing past it is untrusted; decide an
upload's type from its own bytes with a cheap pre-decode gate, never from
a client-supplied label; a parser building authoritative structure
rejects ambiguous or repeated input rather than merging it. Ignoring
unknown properties buys forward compatibility and pays in silent data
loss — where that matters, a test asserts the literal value arrived.

## 3. Own an unversioned contract in one document and validate on both sides

Where no schema registry or consumer-driven contract test exists, one
frozen document owns the contract — named owner, numbered amendment log;
implementers may not edit it, and disagreement is escalated and settled
by an attributed amendment, never by local reinterpretation. It carries
one worked example per distinct contract shape, precise enough that a
wrong rule contradicts it and derived from the consuming code, not
copied from a live instance. Producer and consumer each assert exact
literal values at the boundary — the producer defines validity, the
consumer keeps a backstop against any producer version it may meet —
and each assertion names the defect it would have caught. No change
lands before the real producers and consumers are enumerated by name,
the unknown ones that could still be affected stated, the change
classified against them with its reversibility, and the ADR question
argued either way. A breaking change to a published contract ships once,
as one coordinated release with written notice, never as a defective old
version kept alive behind a version segment. Cross-service references
are opaque identifiers whose integrity lives in code and tests, not the
store; a format hardens once clients you do not deploy in lockstep
persist it, so keep it opaque. A rename crossing a serialization, wire,
or process boundary is a contract change (`skill.holistic-editing`).

## 4. Where order or precision carries meaning, it is an asserted contract

Ordering, layout, and numeric precision are first-class data, not
formatting reconstructed at render time. Where the consuming platform
gives order meaning, generate in declaration order, compare ordered
rather than as a set (a set comparison passes a silent reorder), preserve
order by filtering in place, surface name collisions, and treat any
reordering as a deliberate change; where a multi-step convergence can
strand an operator midway, step order is a documented safety contract
with exact-match counts at the finalizing step. Numeric precision is
specified uniformly at the wire boundary, with decimal rounding semantics
stated explicitly rather than inherited from the language's binary-float
rounding, which silently violates documented midpoint behaviour.

## 5. An error honestly describes what failed

An error carries its cause and a type or status that truthfully
describes what happened; a convenient but wrong type is a latent trap for
future callers. Where a platform limit or permission was hit, the failure
text carries the upstream's verbatim refusal, so a refusal is
distinguishable from an input error at the point of failure — the raw
text is often what later disproves an assumed cause. A status never
claims less acceptance than actually happened: misstated partial
acceptance produces client retry loops that re-send committed work.
Internal errors become one bounded envelope only at the API boundary,
where an unknown failure returns a generic code and leaks nothing.

## 6. Authorize server-side from the verified credential, once, and reuse it

The acting identity is derived server-side from the verified credential
at every trust boundary — never from a body, parameter, or header the
caller controls; a client-supplied identifier is input to be authorized,
not a claim of who is acting, and knowing an identifier confers no
permission. Authorization is enforced once in the service layer, per
operation and resource, and every surface reuses that check: the UI is a
navigation affordance, never the guard; hiding a path from documentation
is not authorization; where only URL-pattern rules exist, the gap is
recorded as a weaker-than-baseline posture. A denial does not disclose
existence — a resource the caller may not see answers not-found, and
authentication and visibility denials share one response shape and
timing class. A service-to-service caller is a narrowly scoped,
short-lived machine identity admitted by the same rules, never a widened
guard or trusted network position; a pre-authentication admission cap is
never placed over a class containing the legitimate caller, nor keyed on
a value the caller controls.

## 7. Visibility, deletion, and retention apply to every read surface

Decide visibility rules before building the surfaces that expose data,
and apply them as an explicit predicate on every write and every read
path — pages, APIs, search indexes, feeds, notifications, media
delivery, caches, background jobs — so the rule survives any engine; a
record removed from one surface but reachable from another is a leak. Deletion is a state change applied uniformly across
every surface and retained for audit, with a soft-delete grace window
before hard purge and released identifiers held unusable for at least
that window. Every new store of personal data registers in the erasure
inventory, enforced by a contract test, so deletion coverage cannot fall
behind the schema; where a statutory retention duty overrides erasure,
redact the personal fields and stamp the record, citing the provision.
Retention is set per record class by accountability value, not one
global window; a rotation cap on a log volume is a retention policy
whether or not anyone chose it. A cache key encodes the visibility scope
of what it stores; object keys for user content are opaque,
non-enumerable, and never publicly listable.

## 8. Log structured facts and identifiers, never payloads

Emit structured logs to a single stream with a correlation identifier on
every request, job, and delegation (`method.delegation`'s `spawn_id`),
carrying outcome and reason — actor handle, result, rejection reason,
size — and never the payload, credential, token, or private field that
caused it. Ad-hoc console output in application code is banned; tracing
uses a vendor-neutral API so the backend stays swappable; redaction
applies to traces and operational inspection exactly as to logging — a
trace is a data sink like any other. Any mechanism that displaces a
human-supplied value announces the name and the displacing mechanism
before the value is lost — one value-free line per overridden name,
silent when nothing changed — with a provenance view separating supplied
from effective values. A diagnostic capture window is anchored to the
event under investigation: a window that can hold more than one
occurrence yields a sample, not a trace.

## Neighbours

- `method.design-posture` — where validation and errors live; cross for placement.
- `method.secrets-posture` — the secret a startup check needs; cross when it is one.
- `method.incident-posture` — evidence a log must support; cross when a trace failed.
- `method.release-posture` — both sides compatible on release; cross when it ships.
- `protocol.specify` — the contract as an executable spec; cross when none exists.
- `skill.holistic-editing` — a rename crossing a wire boundary; cross before renaming.
