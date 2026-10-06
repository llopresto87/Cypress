# stripe-java — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The official Java SDK for the Stripe payments API: typed models, typed
parameter builders and webhook verification. Coordinates
`com.stripe:stripe-java`, with Google Gson as its one runtime dependency; it
supports the LTS JDKs from 8 up, and the Spring Boot BOM does not manage it.
The SDK uses semantic versioning, and every major is tied to one Stripe API
version: each SDK release calls the API version that was current when it was
released. New features and fixes, security fixes included, land only on the
latest major; older majors stay downloadable but receive no updates. Upstream
home: https://github.com/stripe/stripe-java (README), Javadoc at
https://stripe.dev/stripe-java, API reference at https://docs.stripe.com/api
with Java examples.

## Install, setup and configuration
- **Client pattern (v23 and later):** `StripeClient client = new StripeClient("sk_...")`
  or `StripeClient.builder()...build()`. There is no global state, so several
  clients with different keys can coexist. The legacy pattern, a static
  `Stripe.apiKey` with static resource methods such as
  `Customer.create(params)`, still works but is slated for deprecation, and new
  endpoints will be reachable only through `StripeClient`.
- **HTTP defaults:** connect timeout 30 s, read timeout 80 s (the README warns
  against short read timeouts); up to 2 network retries since v27 (0 before),
  with idempotency keys added so retries are safe. `RequestOptions` overrides
  per request: API key, idempotency key, `Stripe-Account` for Connect,
  timeouts, retries.
- **Telemetry:** request latency is reported to Stripe by default;
  `Stripe.enableTelemetry = false` turns it off.
- **DNS:** the README recommends a JVM DNS cache TTL
  (`networkaddress.cache.ttl`) of 60 seconds, because Stripe's addresses can
  change and a forever-cached address fails every request until restart.
- `Stripe-Notice` response headers are printed in an agent environment, and
  outside one for calls to test accounts or sandboxes;
  `STRIPE_SUPPRESS_NOTICES=true` suppresses them outside an agent environment.
- Keep API-key configuration in one place so authentication and environment
  selection are not scattered across call sites.

## Core API / usage shape
- **Calls (v23 and later):**
  `client.v1().customers().create(CustomerCreateParams.builder().setEmail(..).build())`;
  `retrieve`, `list` and `update` follow the same service pattern, over typed
  resource models such as `Customer`, `PaymentIntent` and `Charge`. Errors are
  `StripeException` subclasses.
- **Webhooks:** `Webhook.constructEvent(payload, sigHeader, endpointSecret)`
  verifies the `Stripe-Signature` header (HMAC, scheme `v1`, constant-time
  comparison) and its timestamp, then parses the `Event`; any failure throws
  `SignatureVerificationException`. `Webhook.Signature.verifyHeader(...)` only
  verifies; `constructEventWithoutVerification` only parses (for input already
  verified, such as an EventBridge envelope). On `StripeClient` (v27 and later)
  the method is `parseSnapshotEvent()`, with `parseThinEvent()` for thin
  events.
- **Event payloads:** `event.getDataObjectDeserializer().getObject()` returns an
  `Optional` that is empty when the event's API version differs from the SDK's
  `Stripe.API_VERSION`; `deserializeUnsafe()` forces it and `getRawJson()`
  gives the raw data.
- **Fields the SDK does not model:** `putExtraParam(...)` on params,
  `getRawJsonObject()` on responses, and `rawRequest(...)` on `StripeClient`
  from v27.

## Idioms & best practices
- Treat Stripe as the system of record and fetch objects from it (for example
  after an out-of-order event) rather than mirroring them locally (the fetch is
  upstream advice; the no-mirror stance is observed in practice).
- Verify every webhook with the SDK, using the endpoint's own `whsec_` secret,
  on the raw request body. The SDK routine handles the secret, timestamp
  tolerance and replay window; a hand-rolled verifier has to get all of it
  right.
- Return 2xx quickly, before heavy work, and process the event asynchronously.
- Dedupe by event id (and, where two events describe one change, by
  `data.object` id plus `event.type`); never use `created` for ordering or
  dedupe, and never depend on event order.
- Put idempotency keys (V4 UUIDs suggested, at most 255 characters, no personal
  data) on create requests that may be retried. Stripe may prune keys after 24
  hours, after which a reused key creates a new request.
- Use restricted keys (`rk_`) with only the permissions needed; Stripe no
  longer recommends secret keys (`sk_`) for new uses.

## General pitfalls
- **Wrong signing secret,** the most common verification failure. Secrets are
  unique per endpoint, differ between test and live mode for the same
  endpoint, and the `stripe listen` secret differs from a Dashboard endpoint's.
- **Mutated body.** Any change to the raw body (parsing and re-serializing JSON,
  whitespace, key order, encoding) breaks the signature: verify the exact UTF-8
  string Stripe sent. In Spring, read the body as a raw `String` or bytes before
  any JSON binding (an inference from the rule).
- **Tolerance 0.** `constructEvent` defaults to 300 s; a tolerance of 0 or less
  turns the recency check off, so replayed requests pass. Keep server clocks on
  NTP.
- **API version mismatch.** Event payloads are rendered in the account's (or the
  endpoint's) API version, while typed models follow the SDK's version; on a
  mismatch `getObject()` is empty and naive code drops the event. Create the
  webhook endpoint with `api_version` equal to the SDK's.
- **No other API version from a typed SDK.** In Java you cannot target a
  different API version than the SDK was built for, so an API upgrade is an SDK
  major upgrade, and staying on an old major freezes both fixes and API version.
- **Retries:** in live mode Stripe retries a failed delivery for up to three
  days with exponential back-off (a sandbox retries three times over a few
  hours), and an event can arrive twice; a disabled endpoint stops retries.
- **Preview SDKs** (`-beta.X`, `-alpha.X`) can break without a major bump; pin
  them exactly.
- **Test keys prove test behaviour only.** Sandbox and live are separate
  environments; code exercised only with `sk_test_` keys is not validated
  against live.

## Testing
- Use sandbox keys (`sk_test_`, `rk_test_`, `pk_test_`) and test cards (for
  example 4242 4242 4242 4242 with any future date); real card details in live
  mode for testing are prohibited.
- Locally, `stripe listen --forward-to localhost:<port>/<path>` forwards events
  and prints a session `whsec_` secret, and `stripe trigger <event>` (for
  example `payment_intent.succeeded`) sends test events.
- Unit-test the webhook path with `Webhook.Signature.generateSignatureHeader(payload, secret)`
  to build a valid header, and (an inference from the rules above) test a
  modified body, a wrong secret and an old
  timestamp.
- `StripeClient` has no static methods, which upstream notes makes it much
  easier to mock. The SDK's own tests run against `stripe-mock`.

## Security defaults
- The SDK verifies nothing unless the application calls it; verification is
  the application's job. The recency check is on by default (300 s).
- Webhook endpoints are HTTPS; Stripe publishes its sending IP list; roll
  endpoint secrets periodically (the old secret can stay valid for up to 24
  hours during a roll).
- Key types: publishable `pk_` (safe in front-end code), restricted `rk_` and
  secret `sk_` (never exposed). Webhook signing secrets are not API keys.

## Operational behaviour
- Network retries (2 by default since v27) cover intermittent network failures
  and other non-deterministic errors.
- Event delivery is at least once and unordered; each delivery attempt is signed
  afresh with a new timestamp.
- Stripe's documented path for upgrading a webhook endpoint's API version runs
  old and new endpoints side by side, so handlers must be idempotent.

## Interop
- Gson is the only runtime dependency; ProGuard must keep `com.stripe.**`.
- Stripe.js and the mobile SDKs create PaymentMethods on the client with the
  publishable key; the server confirms them with stripe-java.
- Amazon EventBridge and Azure Event Grid deliveries are parsed with
  `constructEventWithoutVerification`, which unwraps the envelope.

## Major lines
- One SDK major per breaking Stripe API version; the project wiki maps each
  major to its API version and links the migration guide to read before
  upgrading.

### Before v23
- Static resource pattern only (`Stripe.apiKey`, `Customer.create(...)`).

### v23
- `StripeClient` service pattern (no global configuration, no static methods);
  `RequestOptions` no longer inherit global `Stripe` settings; several internal
  APIs removed.

### v27
- Default network retries 0 → 2; `StripeClient.constructEvent` renamed
  `parseSnapshotEvent`, `parseThinEvent` added; `rawRequest` available.

## Upstream docs
- https://github.com/stripe/stripe-java
- https://github.com/stripe/stripe-java/wiki
- https://docs.stripe.com/api?lang=java
- https://docs.stripe.com/webhooks
- https://docs.stripe.com/keys
