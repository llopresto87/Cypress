# stripe-java — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The official Java SDK for the Stripe payments API — a typed client that wraps
Stripe's REST API with model classes for core payment objects and helpers for
verifying inbound webhooks. The canonical Maven artifact is
`com.stripe:stripe-java`.

## Core API / usage shape
- `Stripe.apiKey` is set once to authenticate all subsequent calls.
- Resource model classes (e.g. `Customer`, `PaymentIntent`, `Charge`) expose
  static `create`/`retrieve`/`list` methods that mirror the corresponding REST
  endpoints and return typed objects.
- `Event` together with `Webhook.constructEvent(payload, sigHeader,
  endpointSecret)` is the standard way to authenticate and deserialize inbound
  webhook payloads before acting on their event types.

## Idioms & best practices
- Treat Stripe as the system of record for payment state; consuming
  applications typically need no local persistence mirroring Stripe objects —
  fetch from Stripe rather than duplicate.
- Verify webhooks with the SDK's built-in `Webhook.constructEvent(...)`: it
  encapsulates a well-tested routine (signing secret, timestamp tolerance,
  replay protection) that a hand-rolled verifier has to get right in full, and
  any bespoke substitute needs the same scrutiny.
- Keep API-key configuration in one place so authentication and environment
  selection are not scattered across call sites.

## General pitfalls
- Stripe distinguishes test-mode keys (an `sk_test_...` prefix) from live-mode
  keys. Code exercised only against a test key is not validated against live
  behavior; the two modes are separate environments and must both be
  considered before release.

## Upstream docs
- https://github.com/stripe/stripe-java
- https://stripe.com/docs/api?lang=java
- https://stripe.com/docs/webhooks
