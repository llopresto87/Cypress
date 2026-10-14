# Resend — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The .NET SDK for Resend, a hosted email-sending API. It wraps the Resend REST
API (`https://api.resend.com`) behind one interface, `IResend`, covering
sending (single, batch, scheduled), reading sent and received mail, domains,
API keys, contacts, suppressions and webhooks. The package id is `Resend`;
the source is `resend/resend-dotnet`, MIT licensed. The service's own docs
are at `resend.com/docs`. The repository README states that the package
targets .NET 8 and .NET 10, and that .NET 9 apps use the .NET 8 build.

While the SDK is on its 0.x line, a minor release may change the API (Major
lines).

## Install, setup and configuration
- `dotnet add package Resend`.
- Prerequisites on the service side: an API key, and a verified sending
  domain. Until a domain is verified, the API accepts mail only to the
  account owner's own address (a 403 `validation_error`).
- Registration: the repository README shows `services.AddResend(o =>
  o.ApiToken = ...)`. The service's .NET guide shows the longer form:
  `services.AddHttpClient<ResendClient>()`,
  `services.Configure<ResendClientOptions>(o => o.ApiToken = ...)`,
  `services.AddTransient<IResend, ResendClient>()`. Use what the pinned
  version provides. `ResendClient` takes `IOptionsSnapshot<ResendClientOptions>`
  and an `HttpClient`, so it also works without DI.
- `ResendClientOptions`:
  - `ApiToken`: the API key. In the SDK source, an empty value falls back to
    the `RESEND_API_KEY` environment variable.
  - `ApiUrl`: default `https://api.resend.com`.
  - `ThrowExceptions`: default `true`. When `false`, failures come back as a
    `ResendResponse` with `Success == false` and `Exception` set, instead of
    being thrown.
- The client sets the base address, a `Bearer` authorization header, an
  `Accept: application/json` header and a `User-Agent` on the `HttpClient` it
  is given. The API rejects requests without a `User-Agent` (403); the SDK
  always sends one.

## Core API / usage shape
- `IResend.EmailSendAsync(EmailMessage, ct)` returns
  `ResendResponse<Guid>`, the id of the created email in `Content`.
- `EmailMessage`: `From` (`"Name <address>"` or an address), `To`, `Cc`,
  `Bcc`, `ReplyTo` (address lists), `Subject`, `TextBody`, `HtmlBody`,
  `Headers` (custom headers), `Attachments`, `Tags`, and `MomentSchedule` for
  scheduled sending.
- `EmailSendAsync(idempotencyKey, message, ct)` sends the `Idempotency-Key`
  header (see Idioms).
- `EmailBatchAsync(messages)` sends up to 100 messages in one call and returns
  their ids in request order. A validation-mode overload returns per-message
  results.
- Other surface on the same interface: `EmailRetrieveAsync`, `EmailListAsync`,
  `EmailRescheduleAsync`, `EmailCancelAsync` (scheduled mail), domain, API-key,
  contact, suppression and received-email operations.
- Responses carry `Limits` (`ResendRateLimit`: `Limit`, `Remaining`, `Reset`,
  `RetryAfter`, `Policy`) read from the `ratelimit-*` and `retry-after`
  headers.
- Errors are `ResendException` with `StatusCode`, `ErrorType` (the API's error
  `type`: `validation_error`, `invalid_api_key`, `restricted_api_key`,
  `rate_limit_exceeded`, `daily_quota_exceeded`, `monthly_quota_exceeded`,
  `invalid_idempotent_request`, `concurrent_idempotent_requests`, and the
  SDK's own `http_send_failed`, `missing_response`, `deserialization`),
  `Limits`, and `IsTransient`, true for the rate-limit, quota and
  HTTP-send-failure types.
- The service also accepts SMTP submission (host `smtp.resend.com`, user
  `resend`, the API key as password; implicit TLS on 465 or 2465, STARTTLS on
  25, 587 or 2587), so an SMTP client can stand in for the SDK.

## Idioms & best practices
- Send with an idempotency key whenever a send may be retried (from a queue
  consumer, an outbox, a retry policy). The service stores keys for 24 hours
  and answers a repeated request with the original response without sending
  again. Keys are 1 to 256 characters; upstream suggests a form such as
  `<event-type>/<entity-id>`. Over SMTP the header is
  `Resend-Idempotency-Key`.
- Send a `TextBody` with every `HtmlBody`.
- Keep `From` on the verified domain; the API rejects other domains.
- Inject `IResend` behind an application-level sender interface, so the
  provider can be swapped (for SMTP, or a capture server in development) and
  faked in tests.
- Retry only what `IsTransient` marks, and honour `RetryAfter`. A
  `monthly_quota_exceeded` is flagged transient by the SDK, but the docs'
  remedy is a plan upgrade, so a retry loop should not spin on it.
- Use a restricted API key ("Sending access", optionally limited to one
  domain) for a service that only sends.

## General pitfalls
- **Retrying a send without an idempotency key can send twice.** A timeout
  after the service accepted the request looks like a failure to the caller.
- **The same idempotency key with a different body fails** with 409
  `invalid_idempotent_request`; a second request with the same key while the
  first is in flight fails with 409 `concurrent_idempotent_requests`. Derive
  the key from the logical email, and build the body deterministically.
- **The SDK does not retry.** A transient error is thrown (or returned) on
  the first failure; resilience is the caller's or the `HttpClient`
  pipeline's job. Observed in practice: sends wrapped in a Polly resilience
  pipeline, with the provider registered underneath an outbox so callers never
  reach it directly.
- **Rate limits are per team, across all keys.** Every service sharing an
  account shares the limit; a burst returns 429 `rate_limit_exceeded`. Queue
  sends rather than fanning them out concurrently.
- **Batch sends: attachments are listed upstream as "not supported yet"**,
  and one invalid message fails the whole batch request. Check the batch
  docs before relying on either.
- **`ResendResponse<T>.Content` throws `InvalidOperationException`** when the
  response carries no value; check `Success` first when `ThrowExceptions` is
  off.
- **0.x versioning.** Observed in practice: teams pin the SDK exactly and
  read the release notes on every bump, because a 0.x minor may rename types
  or methods.

## Testing
- Fake `IResend` (it is an interface) or the application's own sender
  interface in unit tests.
- Against the real service, send to the `resend.dev` test addresses:
  `delivered@resend.dev`, `bounced@resend.dev` (an SMTP 550 5.1.1 bounce),
  `complained@resend.dev` (marked as spam) and `suppressed@resend.dev`. All
  but the suppressed address accept a `+label` (`delivered+signup@...`).
  Upstream advises against fake addresses and fake SMTP servers for this,
  since bounces damage the domain's reputation. Test sends count against the
  quota.
- Observed in practice: local development routes mail through the SMTP path
  to a local capture server instead of the API, which keeps development mail
  off the account and its quota. Upstream's testing page advises against fake
  SMTP servers for testing deliverability scenarios (bounces, complaints),
  which only the real service and its test addresses exercise.

## Security defaults
- The API is HTTPS only; plain HTTP is not supported.
- The API key is a bearer secret, shown once at creation. Keep it in a secret
  store and pass it through configuration, never in source; a `.env` file must
  be ignored by version control.
- A full-access key can create, read and delete every resource, including
  other keys; a sending-access key limits the damage of a leak.
- Webhook requests are signed (Svix). Verify the signature over the raw body
  before acting on a webhook; upstream also warns about replayed payloads.
- The provider stores sent messages (they can be listed and retrieved through
  the API and dashboard), so message bodies leave your systems. The data-
  processing terms of a hosted provider are a legal question for the project,
  outside this page.

## Operational behaviour
- Each call is one HTTPS request through the injected `HttpClient`, so
  handler lifetime, timeouts and resilience come from `IHttpClientFactory`
  configuration.
- Quotas: a daily quota on the free plan (a UTC calendar day) and a monthly
  quota on every plan, both counting sent and received mail, reported in the
  `x-resend-daily-quota` and `x-resend-monthly-quota` response headers;
  breaching one returns 429 with a quota error type.
- Delivery is asynchronous: a successful send means the email was accepted,
  not delivered. Delivery, bounce, complaint and suppression outcomes arrive
  as webhook events (`email.delivered`, `email.bounced`, `email.complained`,
  `email.suppressed` and others) or through `EmailRetrieveAsync`.
- Batch emails start in a `queued` state.

## Interop
- `MailKit.md`: the SMTP alternative, for the same service through its SMTP
  endpoint or for an on-premises relay.
- `Microsoft.Extensions.Http.Resilience.md`: retry and timeout handlers for
  the typed `HttpClient` the SDK uses.
- `MassTransit.RabbitMQ.md`: sending from a consumer behind a transactional
  outbox, with the idempotency key derived from the message id, gives
  at-least-once delivery without duplicate mail.

## Major lines

### 0.x line
- Below 1.0, semantic versioning gives no compatibility promise between
  minors; check the repository's release notes for each bump.
- This page reads the repository's current source and README; confirm that a
  member (the `AddResend` registration, batch validation modes, received-mail
  and suppression operations) exists in the pinned version before relying on
  it.

## Upstream docs
- https://resend.com/docs/send-with-dotnet
- https://resend.com/docs/api-reference/introduction
- https://resend.com/docs/api-reference/errors
- https://resend.com/docs/api-reference/rate-limit
- https://resend.com/docs/dashboard/emails/idempotency-keys
- https://resend.com/docs/dashboard/emails/batch-sending
- https://resend.com/docs/dashboard/emails/send-test-emails
- https://resend.com/docs/send-with-smtp
- https://resend.com/docs/webhooks/verify-webhooks-requests
- https://github.com/resend/resend-dotnet
- https://www.nuget.org/packages/Resend
