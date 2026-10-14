# MailKit — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A mail client library for .NET: SMTP for sending, IMAP and POP3 for reading
mail off a server. Message construction (headers, bodies, alternative views,
attachments) belongs to the companion MimeKit library, whose `MimeMessage` is
what MailKit sends and returns. Both are by the same author, MIT licensed, and
live in `jstedfast/MailKit` and `jstedfast/MimeKit`, with API docs at
`mimekit.net/docs`. The packages this page covers:

- `MailKit`: the SMTP, IMAP and POP3 clients. Needed to talk to a mail server.
- `MimeKit`: the MIME message model, parser and writer (`MimeMessage`,
  `BodyBuilder`, `MailboxAddress`), plus S/MIME, OpenPGP and DKIM. MailKit
  depends on it at a minimum version, so it arrives with MailKit; it is also
  used alone to build, parse or save messages.

## Install, setup and configuration
- `dotnet add package MailKit` (brings `MimeKit`). The MailKit package declares
  MimeKit as a dependency with a minimum version, and each MailKit release
  raises that minimum; a central package pin that lists both keeps them in
  step.
- `SecureSocketOptions` decides transport security on connect:
  - `None`: no TLS.
  - `Auto` (the default when the argument is omitted): MailKit picks by port,
    and if the server supports neither SSL nor STARTTLS the connection
    continues unencrypted.
  - `SslOnConnect`: TLS from the first byte (the "SSL ports": SMTP 465, IMAP
    993, POP3 995).
  - `StartTls`: upgrade with STARTTLS after the greeting; throws
    `NotSupportedException` if the server does not offer it.
  - `StartTlsWhenAvailable`: upgrade only if the server offers STARTTLS,
    otherwise continue in plain text.
- The `Connect(host, port, bool useSsl)` overload only chooses whether the
  connection is SSL-wrapped; with `false`, STARTTLS is still used when the
  server offers it. Port 0 means the protocol's default port.
- `SslProtocols` on the client sets the allowed protocol versions. Upstream
  keeps removing protocols it no longer considers secure from the default set
  (its FAQ lists SSL 2.0, SSL 3.0, TLS 1.0 and TLS 1.1 as off by default), so
  an old server can fail the handshake after an upgrade.
- `CheckCertificateRevocation` (on by default) checks the server
  certificate's revocation status; `ServerCertificateValidationCallback`
  replaces certificate validation.
- On .NET (Core) and .NET 5+, only the Unicode encodings, ASCII and ISO-8859-1
  exist until the app calls
  `Encoding.RegisterProvider(CodePagesEncodingProvider.Instance)` once at
  startup; MimeKit already references `System.Text.Encoding.CodePages`.

## Core API / usage shape
- The send lifecycle is explicit: `using var client = new SmtpClient();` →
  `ConnectAsync(host, port, SecureSocketOptions)` → `AuthenticateAsync(user,
  password)` when the server needs it → `SendAsync(MimeMessage)` →
  `DisconnectAsync(true)`. Each stage fails on its own, so an error is
  attributable to connect, authenticate or send.
- `AuthenticateAsync` also takes a `SaslMechanism` (for example
  `SaslMechanismOAuth2`) for token-based login; upstream has guides for
  OAuth 2.0 against Exchange Online and Gmail.
- IMAP and POP3 clients follow the same connect, authenticate, act,
  disconnect shape. An IMAP server has one open folder at a time: opening a
  second folder closes the first, and a move or copy needs only the source
  folder open.
- Building a message (MimeKit): `new MimeMessage()`, `From.Add(new
  MailboxAddress(name, address))`, `To.Add(...)`, `Subject`, then a body.
  `new BodyBuilder { TextBody = ..., HtmlBody = ... }` with `Attachments.Add`
  and `LinkedResources.Add` (inline images referenced by `cid:`), then
  `message.Body = builder.ToMessageBody()`, which builds the MIME tree from
  the text bodies, linked resources and attachments. Built by hand, the text
  and HTML parts go into a `MultipartAlternative`, least faithful first
  (`text/plain`, then `text/html`), and that goes into a `multipart/mixed`
  with any attachments.
- Parsing and saving: `MimeMessage.Load(stream)` / `LoadAsync`, and
  `message.WriteTo(stream)`; `FormatOptions` controls serialization (line
  length, new-line format, `International` for the internationalized-email
  formatting standards, and how attachment-name parameters are encoded).
- `MimeMessage` is `IDisposable`; `Dispose` releases its resources and leaves
  it unusable.

## Idioms & best practices
- Make the port and the `SecureSocketOptions` one decision and set them
  together: `SslOnConnect` with an SSL port, `StartTls` with a submission port.
  Prefer `StartTls` over `StartTlsWhenAvailable` or `Auto` on any network you
  do not control, so a server without STARTTLS fails instead of silently
  receiving credentials in plain text.
- Wrap the lifecycle so `DisconnectAsync(true)` runs on failure too; a
  half-open connection holds a session on the mail server, not only a local
  socket.
- Send both a `TextBody` and an `HtmlBody`. Not every client renders HTML, and
  a receiving client picks the last alternative it can display.
- For non-ASCII attachment names, MimeKit's default parameter encoding is the
  RFC 2231 form; Outlook before 2007 only understood the RFC 2047 form, which
  `ParameterEncodingMethod.Rfc2047` (per parameter or through `FormatOptions`)
  produces.
- The SMTP protocol does not file sent mail anywhere. To keep a copy in a
  "Sent" folder, append the message over IMAP yourself.

## General pitfalls
- **`Auto`, `StartTlsWhenAvailable` and `Connect(..., false)` can all end in
  a plain-text session** without an error, when the server does not offer
  STARTTLS. The configuration reads as "TLS where possible" and the wire
  carries the credentials in clear. Verify the negotiated mode (a protocol
  log, or the client's `IsSecure` / `IsEncrypted` after connecting) instead of
  reading it off the config.
- **Mapping two settings onto one option is the application's choice, not
  MailKit's.** `SecureSocketOptions` is a single enum; when an application
  derives it from two flags (say "use SSL" and "use STARTTLS"), its own code
  decides which wins when both are set. Observed in practice: such a mapping
  let "SSL on connect" silently take precedence when both flags were true.
  MailKit is not involved; upstream documents only the enum.
- **No connection pooling.** Each `SmtpClient` is one connection; a send path
  that creates a client per message pays a full connect, TLS handshake and
  authentication per message. To send many messages, keep one connected client
  and call `SendAsync` repeatedly (`NoOpAsync` keeps an idle connection
  alive), or build a pool yourself.
- **A client is one session.** The `ImapClient` reports "currently busy
  processing a command" when used from several threads; the async methods lock
  the client's `SyncRoot` themselves, the synchronous ones need the caller to.
- **A disposed `MimeMessage` cannot be read.** Code that disposes the message
  right after `SendAsync` (the usual `using`) breaks any later reader, including
  a test fake that inspects the body after the call returns. Observed in
  practice: a fake sender that read `HtmlBody` after the caller had disposed
  the message threw `ObjectDisposedException`; the fake must copy what it
  asserts on inside its own send method. Upstream documents only that
  `Dispose` leaves the message unusable.
- **MimeKit does not escape or sanitize HTML.** It sends the `HtmlBody` it is
  given. Observed in practice and consistent with the API: values interpolated
  into an HTML template must be encoded by the template layer, because nothing
  downstream will.
- **Garbled text or `NotSupportedException` ("No data is available for
  encoding")** on .NET (Core) means the code-pages provider was never
  registered (Install, setup and configuration).
- **`TypeLoadException` creating a `MimeMessage` on .NET Framework** comes
  from missing assembly binding redirects; upstream's fix is MimeKit and
  MailKit 4.0 or later, which ship `.dll.config` files, plus a redirect for
  `System.Runtime.CompilerServices.Unsafe`.

## Testing
- MailKit ships no test double for a mail server. Put an application-level
  sender interface over `SmtpClient` and fake that in unit tests, capturing
  what the fake must assert on during the call (see the disposal pitfall).
- For integration tests, run a local SMTP capture server in a container and
  point the client at it with `SecureSocketOptions.None` (or the server's TLS
  mode); assert on what the capture server received. Keep that plain-text
  setting out of production configuration.
- `new SmtpClient(new ProtocolLogger("smtp.log"))` records the whole SMTP
  conversation, the quickest way to see which TLS mode and auth mechanism
  were actually used.
- MimeKit messages can be built and parsed without a server, so message
  construction is unit-testable on its own: build, `WriteTo` a stream,
  `Load` it back, and assert on the parts.

## Security defaults
- The certificate is validated by default, revocation included, and old
  SSL/TLS versions are off by default. Setting
  `ServerCertificateValidationCallback = (s, c, h, e) => true` accepts any
  certificate, so anyone on the path can impersonate the server and read the
  credentials; upstream advises against it in production and suggests pinning
  known certificate values if a self-signed server must be trusted.
  Disabling `CheckCertificateRevocation` trades revocation checking for
  availability when CRL or OCSP servers are unreachable.
- `None`, `Auto` and `StartTlsWhenAvailable` permit plain text (General
  pitfalls).
- A protocol log contains the authentication exchange (the base64 blob after
  `AUTH` / `AUTHENTICATE`); upstream says to scrub it before sharing, and it
  must not reach shared log stores.
- SMTP credentials come from configuration backed by a secret store. Where
  the provider supports it, OAuth 2.0 (`SaslMechanismOAuth2`, upstream's
  Exchange and Gmail guides) avoids storing an account password.

## Operational behaviour
- Connection, TLS negotiation and authentication happen in `ConnectAsync` and
  `AuthenticateAsync`; `SendAsync` throws `ServiceNotConnectedException`
  when not connected, `SmtpCommandException` when the server rejects a
  command and `SmtpProtocolException` on an unexpected response. An
  `SslHandshakeException` on connect usually means, per upstream's FAQ, the
  wrong TLS mode for the port, an untrusted or expired certificate, an
  unreachable revocation server, or no common protocol version.
- The client holds one TCP connection until `DisconnectAsync`; a long-lived
  client keeps it alive with `NoOpAsync` and must be ready to reconnect.
- Dispose messages once sent, in particular those built from files or large
  attachments, whose content is read from streams.

## Interop
- Hosted email APIs that also accept SMTP submission (for example the one on
  `Resend.md`) can be reached with MailKit as the transport, using the
  provider's SMTP host, port and API-key credentials.
- `System.Net.Mail`: MimeKit allows an explicit cast from a
  `System.Net.Mail.MailMessage` to a `MimeMessage`, which eases moving code
  off the framework's older client.
- Background sending usually sits behind a queue or outbox
  (`MassTransit.RabbitMQ.md` for one); the message is built, sent and disposed
  inside the consumer.

## Major lines

### 4.x line
- 4.0 adds the `.dll.config` binding-redirect files for .NET Framework apps
  (the `TypeLoadException` pitfall).

### MimeKit 5.x line
- The MimeKit repository documents a 5.0 line that moves S/MIME, PGP/MIME,
  DKIM, ARC and DMARC support into a separate `MimeKit.Cryptography` assembly
  (initialized with `CryptographyModule.Initialize()` before parsing) and
  replaces the TNEF API (`TnefPart.ConvertToMessage()` and
  `ExtractAttachments()` are gone; load a `TnefMessage` and call
  `ConvertToMime()`). Read the porting guide before moving across.

## Upstream docs
- https://mimekit.net/docs/html/Introduction.htm
- https://mimekit.net/docs/html/T_MailKit_Security_SecureSocketOptions.htm
- https://mimekit.net/docs/html/Creating-Messages.htm
- https://github.com/jstedfast/MailKit (README, FAQ.md, ExchangeOAuth2.md,
  GMailOAuth2.md)
- https://github.com/jstedfast/MimeKit (README, FAQ.md)
- https://www.nuget.org/packages/MailKit
- https://www.nuget.org/packages/MimeKit
