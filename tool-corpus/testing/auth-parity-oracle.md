# Tool: auth-parity-oracle

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: a stack-neutral pattern, not a
> portable script. The adopting project instantiates its **own** authenticator
> as the oracle; there is nothing generic to copy but the contract.

## 0. Identity

- **Category:** testing
- **Name:** auth-parity-oracle
- **Language / runtime:** any — it runs inside the project's existing test
  framework, in the same process or runtime as the component under test
- **Stability:** **blueprint only** — no portable implementation; the value is
  the one-directional parity contract and the drive-the-real-component-as-oracle
  technique

## 1. What it does

Tests an **upstream, pre-authentication decision** against the **real downstream
authenticator**, rather than against a hand-written table of expected answers.

The shape recurs wherever something must decide *"is a credential present and
well-formed enough to act on?"* **ahead of** the component that will make the
authoritative decision: a pre-authentication guard, a proxy or gateway rule, a
routing filter, a rate-limit or cache key, a cheap reject path in front of an
expensive verifier. Two implementations now hold an opinion about the same
credential, and they can drift.

**The direction of the drift is what bites.** The upstream guard is usually
where some check lives that the authoritative authenticator does not itself
perform — a revocation or introspection call, a rate-limit, an audit record.
So a guard that is *stricter* than the authenticator is the dangerous one: a
credential it fails to recognise still reaches the authenticator, still
authenticates, and silently skips the check that only the guard performs. The
recorded failure of this shape was a family of credential encodings that the
guard's parser did not recognise and the authenticator's did; each one produced
an authenticated identity that never reached introspection, so revocation was
inert on every request carrying one.

The durable insight is about what **not** to do. Do **not** gate the upstream
decision against a hand-written table of expected outcomes. That table and the
guard were written by the same person, from the same reading of the same
specification, on the same afternoon. **Two hand-written expectations that agree
prove only that one author held one belief twice.** Every misreading of the
credential format is faithfully reproduced in both, and the test goes green on
exactly the inputs where the system is wrong.

Instead: **instantiate the real authenticator and ask it.**

## 2. Interface & invocation

Not a CLI. A test fixture with two collaborators and one assertion:

```
oracle   = <real authenticator, offline-configured>
guard    = <the upstream component under test>

for value in credential_corpus:
    assert not (oracle.authenticates(value) and not guard.recognises(value))
```

- **Inputs:** a corpus of candidate credential values — well-formed, malformed,
  truncated, empty, absent, wrong-shape, right-shape-wrong-signature,
  expired, structurally valid but semantically rejected; plus the real
  authenticator's **offline** configuration.
- **Outputs:** for each value, the guard's decision, the oracle's decision, and a
  pass/fail on the one-directional contract. On failure, report **the value's
  class**, both decisions, and the direction of the violation.
- **Preconditions:** the authenticator can be constructed **without network
  access** — no discovery document fetch, no key-set retrieval, no live issuer —
  and stripped to the minimum configuration that still makes the real decision.

## 3. Approach / algorithm

### Instantiate the real downstream component, stripped bare

Construct the authenticator the production path uses, with:

- **no network discovery** — configure keys, issuers, and parameters inline from
  local material rather than letting it fetch anything;
- **no event hooks beyond the one under test** — every callback, logger,
  enricher, or side-effecting handler that is not part of the decision is
  removed, so the fixture cannot pass or fail for a reason unrelated to
  authentication;
- **its real validation logic intact** — this is the part that must not be
  touched, because it is the oracle.

Then ask it the direct question: *would this credential value produce an
authenticated identity?* Its answer is the truth the test is written against.

### The contract: agreement in one direction only

The guard must agree with the live answer **asymmetrically**, and the direction
is the opposite of the one most readers reach for first:

- **Every credential the authenticator would accept must be recognised by the
  guard.** This is the whole contract. The guard is what routes a credential
  into the check the authoritative layer does not perform, so a credential that
  authenticates without passing through the guard has skipped that check
  entirely — while every log line and every status code says the request was
  authenticated normally.
- **The converse is not required and is not asserted.** The guard may recognise
  and process a credential the authenticator later rejects. That costs one
  wasted round trip and opens nothing.

Read the asymmetry as a floor on **permissiveness**, not a ceiling: the guard
must be at least as accepting as the authenticator, and may be more. The
intuition that an upstream guard should be conservative is what produces the
defect — a coarse guard is not a safe default here, it is the bypass.

State that direction in the test's own name and failure message. The moment
someone "tightens" it into a two-way equality, it starts failing for guards that
are legitimately broader, and the fix applied under time pressure is to narrow
the guard — which reopens the gap the test exists to close.

### The generalization

One level above the specific case: **drive the real component as an oracle
rather than mocking its judgment.** A mock encodes what the author believes the
component decides; the component decides. Whenever a test's expected value is a
restatement of another component's behaviour, and that component can be
constructed offline, construct it — and let the test compare two implementations
that were written by different people for different reasons, which is the only
comparison that carries information.

This applies far beyond authentication: a parser and its fast-path pre-check, a
validator and its client-side mirror, a query planner and its cost estimate, a
permission check and its cached approximation.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** there is no stack-neutral code. The oracle is
  the project's own authenticator, and constructing it offline is entirely
  specific to that component.
- **Durable across every implementation:** (a) never gate an upstream decision on
  a hand-written expectation table; (b) instantiate the real downstream component,
  stripped to offline configuration, as the oracle; (c) require agreement in one
  direction only — everything the oracle authenticates must be recognised by the
  guard, never the reverse; (d) build the corpus around **classes** of
  malformation, not a handful of happy-path values.

## 5. Pitfalls and sharp edges

- **Two hand-written expectations that agree prove nothing.** This is the defect
  the pattern exists to remove; it survives review because the test and the code
  read as obviously consistent — they are, with each other, and possibly with
  nothing else.
- **Turning the contract into two-way equality breaks correct guards.** A guard
  may legitimately recognise more than the authenticator accepts. Encode the
  asymmetry; do not let a later reader "fix" it into equality.
- **Recognising is not accepting, and the difference is the whole contract.**
  Ask the oracle whether the value would yield an **authenticated identity** —
  not whether some parser was invoked. A guard can extract a token that cannot
  possibly validate, and a test written against "did the parser run?" goes red
  on values that were never a bypass, which teaches the next reader to distrust
  the gate.
- **A mocked oracle is just the expectation table wearing a costume.** If the
  authenticator's decision is stubbed, the test has returned to comparing an
  author's belief with itself, with more machinery.
- **An authenticator that quietly falls back is a false oracle.** Some
  implementations degrade to a permissive path when their configuration is
  incomplete — no keys, no issuer, discovery disabled. Assert that the oracle
  **rejects** a known-bad value before trusting any of its accepts; an oracle
  that accepts everything makes the parity contract vacuously true.
- **Offline configuration can change the decision.** Stripping discovery or
  hooks must not strip validation. Prove the stripped oracle still rejects the
  classes it is supposed to reject, in the same fixture.
- **The corpus is the coverage.** The contract is only as strong as the values it
  is evaluated over. Enumerate malformation **classes** — absent, empty,
  wrong-scheme, truncated, structurally-valid-but-unverifiable, expired,
  right-shape-wrong-key — rather than collecting a few strings that once caused
  a bug.
- **Parity is not authorization.** The oracle answers whether a credential
  authenticates, not whether the identity may do the thing. Keep that question in
  its own tests.

## 6. Tests that cover it

Cover: for every value in the corpus, the guard never accepts where the oracle
rejects; a guard deliberately more conservative than the oracle **passes** (the
asymmetry regression); a guard mutated to accept one class the oracle rejects
**fails**, and the failure message names the class and both decisions; the oracle
itself rejects a known-bad value, proving it is not a permissive stub; the oracle
is constructed with no network call, verified by running the fixture with the
network unavailable.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (asserts the
  mechanical fact at the protocol level, the same posture from outside);
  `tool-corpus/ops/config-driven-server-response-harness.md` (measures what a
  server really emits rather than what its configuration is believed to say —
  the same measure-do-not-predict move, one layer out);
  `tool-corpus/ops/disposable-test-identity-provisioner.md` (mints the throwaway
  identities a credential corpus can be built from).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-09-13 — created from harvested, generalized capability, by docs-librarian.
