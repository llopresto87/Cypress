# smtp4dev — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
smtp4dev (`rnwood/smtp4dev`) is a **development mail catcher**: an SMTP server
that accepts mail from an application, stores it, and never delivers it onward.
It exposes a web UI (and an HTTP API, plus IMAP for exercising a real mail
client) where the captured messages can be read (headers, body parts, HTML
source, attachments), so flows that depend on email can be exercised end to end
without a real relay and without mailing anyone.

It is the local-environment terminator of the mail path: invitation, verification,
password-reset and notification flows all become observable and assertable.

## Install, setup and configuration
- **Image defaults.** Web UI on container port 80
  (`ServerOptions__Urls=http://*:80`), SMTP on 25, IMAP on 143, POP3 on 110;
  messages and settings in the `/smtp4dev` volume. Upstream's run example
  maps `-p 5000:80 -p 2525:25 -p 110:110`.
- **SMTP defaults.** `Port` 25, `AllowRemoteConnections` true (all
  interfaces), `AuthenticationRequired` false, `SmtpAllowAnyCredentials`
  true, `TlsMode` `None`: no authentication and no TLS until configured.
- **TLS modes.** `None`, `StartTls` or `ImplicitTls`; with no certificate
  given, a self-signed one is generated for the configured host name. The
  port stays independent of the mode (pairing implicit TLS with 465 is a
  convention, not an upstream default).
- **Other settings**: `NumberOfMessagesToKeep`, `BasePath` (serving the UI
  under a proxy prefix), `RelayOptions`, and `LockSettings`, which stops the
  web UI from changing settings.

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
  send". Interactive API docs are served at `/api`. The message routes:
  ```
  GET    /api/Messages                    # summaries, JSON
  GET    /api/Messages/{id}               # one message
  GET    /api/Messages/{id}/html | /plaintext | /source | /raw | /download
  GET    /api/Messages/{id}/part/{partid}/content | /source | /raw
  DELETE /api/Messages/{id}               # or DELETE /api/Messages/* for all
  ```
  `/api/sessions`, `/api/mailboxes` and `/api/server` cover SMTP sessions,
  mailboxes and server settings.

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
  message bodies (invitation links, reset tokens, personal data), so it is an
  administrative surface, not a status page, and belongs behind the same
  authentication boundary as any other admin tool.
- **Keep it to the local profile only.** The deployed profile points at a real
  relay and composes no catcher at all; the catcher's presence in a
  non-development environment is itself the defect.
- **Mount certificates read-only from an ignored secrets directory**, never baked
  into an image or committed.
- **Assert on captured mail in end-to-end tests** through the API, so mail-shaped
  regressions fail a test instead of being noticed by a human much later.
- **Keep the application's mail host overridable** by environment, with the
  catcher wired only into development and staging profiles.
- **Bind published ports to loopback** (`127.0.0.1:5000:80`), as upstream
  recommends, or reach the UI only through a proxy; a bare `-p 5000:80`
  publishes on every host interface.

## General pitfalls
- **It stores complete message bodies in plaintext by design.** Everything a real
  mailbox would receive (tokens, links, personal data) is readable by anyone
  who reaches it. Treat it as a development-only service, never expose it
  publicly, and never point a production system at it.
- **A missing certificate pair fails bring-up at the mount**, before any
  configuration error is reported, so the error message is about a file or a
  volume rather than about mail: an easy half hour lost.
- **Services whose start-up gates on mail-configuration validation take the
  catcher down with them.** An identity server set up that way (by its own
  entrypoint or start-up checks; the server product need not do it by default)
  refuses to boot on an invalid SMTP configuration, so a broken local mail
  catcher becomes a local authentication outage, which looks nothing like a mail
  problem.
- **Implicit TLS and STARTTLS are not interchangeable.** A client configured for
  one against a server configured for the other fails in a way that reads like a
  network error rather than a negotiation mismatch.
- **A private or self-signed certificate must be trusted by the sending client.**
  Otherwise every send fails verification, which again surfaces as an unhelpful
  transport error.
- **It is a catcher, not a relay.** Nothing reaches a real recipient, which is
  the point, but it also means deliverability, spam classification, and relay
  authentication are entirely untested by it.

- **The inbox is shared test state.** It empties on recreate unless the volume
  persists, and parallel tests see each other's mail: filter by your own
  recipient and time window.

## Testing
- Upstream intends the API for automated tests and points to Testcontainers
  examples.
- Delete all messages (`DELETE /api/Messages/*`) at the start of a suite, or
  filter by a unique recipient per test.
- Assert on the parsed parts (`/html`, `/plaintext`) for content and on
  `/raw` for headers.

## Security defaults
- SMTP accepts any sender from any address with no authentication and no TLS;
  the UI and API have no login.
- Every captured message is stored in clear text in the volume.
- `AuthenticationRequired`, `TlsMode` and `SecureConnectionRequired` are the
  switches to change.

## Operational behaviour
- Messages accumulate up to `NumberOfMessagesToKeep`, then the oldest go.
- `LockSettings` stops UI changes, which keeps the running configuration
  equal to the environment it was started with.

## Interop
- Identity servers that send realm mail: [`keycloak.md`](keycloak.md).
- Reverse proxy in front of the UI: [`nginx.md`](nginx.md).

## Major lines
Upstream publishes `v3`, `latest` and `prerelease` tags; no differences
between major lines are recorded here.

## Upstream docs
- https://github.com/rnwood/smtp4dev
- https://hub.docker.com/r/rnwood/smtp4dev
- https://github.com/rnwood/smtp4dev/blob/master/docs/API.md
- https://github.com/rnwood/smtp4dev/blob/master/docs/TLS-SSL-for-SMTP.md
- https://github.com/rnwood/smtp4dev/blob/master/docs/Docker-Security.md
