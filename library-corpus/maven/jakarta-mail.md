# jakarta-mail — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The standard JVM API for sending and receiving email — most commonly used to
send transactional mail over SMTP from a server application. It models a mail
session, messages, addresses, and transports, and supports MIME multipart
bodies (HTML + plaintext alternatives, attachments, inline images). Canonical
coordinates: `com.sun.mail:jakarta.mail` (API `jakarta.mail:jakarta.mail-api`).

## Core API / usage shape
- **`Session`**: created from a `Properties` map describing the SMTP host, port,
  authentication, and transport security (STARTTLS / implicit TLS); the root
  factory object for everything else.
- **`MimeMessage`**: the message — from/to/cc/bcc addresses (`InternetAddress`),
  subject, and content. A `MimeMultipart` assembles alternative bodies and
  attachments as `MimeBodyPart`s.
- **`Transport`**: sends the message. `Transport.send(message)` opens, sends, and
  closes in one call; obtaining a `Transport` explicitly lets you connect once
  and send many.
- **Authentication**: an `Authenticator` (or transport-level credentials)
  supplies username/password for authenticated SMTP relays.

## Idioms & best practices
- Build a multipart/alternative message with both a plaintext and an HTML part
  so clients that cannot render HTML still show readable content.
- Reuse a connected `Transport` for batches rather than paying connection setup
  per message.
- Keep SMTP host, credentials, and TLS settings in external configuration, not
  in code, and always use a TLS-secured transport for authenticated relays.
- Higher-level helpers (framework mail senders, templating) usually wrap this
  API; drop to it directly for control over MIME structure or headers.

## General pitfalls
- **`javax.mail` → `jakarta.mail` namespace split**: as part of the broader
  Java EE → Jakarta EE move, the package root changed from `javax.mail.*` to
  `jakarta.mail.*`. This is a conceptual, source-incompatible rename: the two
  namespaces are mutually exclusive on a classpath, and a dependency (or
  framework) built against one will not satisfy imports of the other. Confirm
  which namespace the surrounding stack expects before adding the API; do not
  mix both on one classpath.
- SMTP-specific behavior (STARTTLS vs implicit TLS, auth requirements, relay
  restrictions) lives in the `Properties`/`Session` config; a subtly wrong
  property silently fails to send or falls back to an insecure transport.
- Sending is blocking network I/O; doing it inline on a request thread couples
  response latency to the mail server — prefer an async/queued path for volume.

## Upstream docs
- https://jakartaee.github.io/mail-api/
- https://eclipse-ee4j.github.io/mail/
- https://mvnrepository.com/artifact/com.sun.mail/jakarta.mail
