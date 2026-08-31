# MailKit — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A full-featured mail client library for .NET covering **SMTP, IMAP, and POP3** —
sending mail and reading it back off a server. It is the transport half of the
pair; message construction (headers, bodies, alternative views, attachments) is
done with `MimeMessage` from the companion MimeKit library, which MailKit
consumes.

## Core API / usage shape
- The send lifecycle is explicit and sequential: `new SmtpClient()` →
  `ConnectAsync(host, port, SecureSocketOptions)` → optional
  `AuthenticateAsync(...)` → `SendAsync(MimeMessage)` → `DisconnectAsync(true)`.
  Nothing is implicit; there is no "just send this" one-liner.
- `SecureSocketOptions.{SslOnConnect, StartTls, None}` selects the
  transport-security mode **explicitly**, rather than inferring it from the port.
- The client is disposable and stateful — connection, authentication, and send
  are separate steps on the same instance, so failures are attributable to a
  specific stage.
- `MimeMessage` (MimeKit) builds the message itself: addresses, subject, and a
  body built from text/HTML alternatives and attachments.
- IMAP/POP3 clients follow the same connect/authenticate/act/disconnect shape,
  so a receive path reads structurally like the send path.

## Idioms & best practices
- Make the security mode and port a single deliberate configuration decision, and
  assert them together — they must agree, and the library will not reconcile them
  for you.
- Wrap the whole lifecycle so `DisconnectAsync(true)` runs even on failure; a
  half-open client is a resource leak against the mail server, not just locally.

## General pitfalls
- **No connection pooling, and conflicting security options fail silently:** by
  default each send is its own full connection lifecycle — connect, authenticate,
  send, disconnect — and any pooling or client reuse is something you build
  yourself, so a high-volume send path built the naive way pays a full handshake
  per message. Worse, if a configuration sets both SSL-on-connect and a StartTLS
  option, **SSL-on-connect silently wins**: the misconfiguration produces no
  error and no warning, it just uses a transport mode other than the one the
  configuration appears to request. Verify the negotiated mode empirically rather
  than reading it off the config.

## Upstream docs
- https://mimekit.net/docs/html/Introduction.htm
- https://github.com/jstedfast/MailKit
- https://www.nuget.org/packages/MailKit
