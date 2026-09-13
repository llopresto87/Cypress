# smtp4dev — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tag.

## What it is
smtp4dev (`rnwood/smtp4dev`) is a **development mail catcher**: an SMTP server
that accepts mail from an application, stores it, and never delivers it onward.
It exposes a web UI (and an HTTP API, plus IMAP for exercising a real mail
client) where the captured messages can be read — headers, body parts, HTML
source, attachments — so flows that depend on email can be exercised end to end
without a real relay and without mailing anyone.

It is the local-environment terminator of the mail path: invitation, verification,
password-reset and notification flows all become observable and assertable.

## Core API / usage shape
- Runs as a container with two surfaces: the **SMTP listener** the application
  points at, and the **web UI / API** an operator or an end-to-end test reads.
- Configuration is supplied as environment variables following the .NET
  configuration convention, where `__` nests a key:
  ```
  ServerOptions__HostName
  ServerOptions__Port
  ServerOptions__TlsMode                     # none | implicit TLS | STARTTLS
  ServerOptions__TlsCertificate              # certificate file path
  ServerOptions__TlsCertificatePrivateKey    # key file path
  ServerOptions__SecureConnectionRequired    # refuse cleartext sessions
  ```
  Further sections govern how many messages are retained, the base path the UI is
  served under (for hosting it behind a reverse proxy), and an optional relay
  section that forwards captured mail on to a real server when that is wanted.
- Messages are readable programmatically through its HTTP API, which is what lets
  an end-to-end test assert on a delivered message rather than on "we called
  send".

## Idioms & best practices
- **Make the local transport match the real one.** Give the catcher a
  certificate and require a secure connection, so the development path exercises
  the same TLS mode the deployed path uses. A catcher that only speaks cleartext
  proves nothing about a relay that requires TLS, and the difference surfaces
  first in the environment that matters.
- **Refuse the cleartext escape hatch, and refuse it permanently.** A "just for
  local" toggle that disables transport security is reintroduced by the next
  person who hits a certificate problem; remove the option rather than
  documenting it.
- **Put the web UI behind an authenticating reverse proxy.** The UI exposes whole
  message bodies — invitation links, reset tokens, personal data — so it is an
  administrative surface, not a status page, and belongs behind the same
  authentication boundary as any other admin tool.
- **Keep it to the local profile only.** The deployed profile points at a real
  relay and composes no catcher at all; the catcher's presence in a
  non-development environment is itself the defect.
- **Mount certificates read-only from an ignored secrets directory**, never baked
  into an image or committed.
- **Assert on captured mail in end-to-end tests** through the API, so mail-shaped
  regressions fail a test instead of being noticed by a human much later.

## General pitfalls
- **It stores complete message bodies in plaintext by design.** Everything a real
  mailbox would receive — tokens, links, personal data — is readable by anyone
  who reaches it. Treat it as a development-only service, never expose it
  publicly, and never point a production system at it.
- **A missing certificate pair fails bring-up at the mount**, before any
  configuration error is reported, so the error message is about a file or a
  volume rather than about mail — an easy half hour lost.
- **Services that validate their mail configuration at start-up take the catcher
  down with them.** Identity servers in particular refuse to boot on an invalid
  SMTP configuration, so a broken local mail catcher becomes a local
  authentication outage, which looks nothing like a mail problem.
- **Implicit TLS and STARTTLS are not interchangeable.** A client configured for
  one against a server configured for the other fails in a way that reads like a
  network error rather than a negotiation mismatch.
- **A private or self-signed certificate must be trusted by the sending client.**
  Otherwise every send fails verification, which again surfaces as an unhelpful
  transport error.
- **It is a catcher, not a relay.** Nothing reaches a real recipient, which is
  the point — but it also means deliverability, spam classification, and relay
  authentication are entirely untested by it.

## Upstream docs
- https://github.com/rnwood/smtp4dev
- https://hub.docker.com/r/rnwood/smtp4dev
