# jakarta-mail — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The standard JVM API for sending and receiving email, most often used to send
transactional mail over SMTP from a server application. It models a mail
session, messages, addresses and transports, and supports MIME multipart
bodies (HTML and plain-text alternatives, attachments, inline images). It is a
platform- and protocol-independent framework, an optional package for Java SE
and part of Jakarta EE.

Coordinates depend on the line, and the artifact name does not tell you the
namespace, so check the package root:
- The 1.x line (JavaMail 1.6, identical to Jakarta Mail 1.6) ships as
  `com.sun.mail:jakarta.mail` and still uses the `javax.mail` package root;
  the older JavaMail coordinate before the move to Eclipse was
  `com.sun.mail:javax.mail`.
- The 2.0 line (Jakarta EE 9) keeps the artifact `com.sun.mail:jakarta.mail`
  but moves to the `jakarta.mail` package root.
- From 2.1 (Jakarta EE 10) the API ships alone as
  `jakarta.mail:jakarta.mail-api`, and the implementation is Eclipse Angus Mail,
  `org.eclipse.angus:angus-mail` (with Angus Activation), "the direct successor
  of JavaMail/JakartaMail"; `org.eclipse.angus:jakarta.mail` is a single jar
  with API and implementation. The API-only artifact also exists late in the
  1.6 line, so its 1.6 versions are `javax.mail` and its 2.x versions
  `jakarta.mail`.

Spring wraps it in `org.springframework.mail` (`JavaMailSender`), added with
`org.springframework.boot:spring-boot-starter-mail`. Upstream homes:
https://jakartaee.github.io/mail-api/ (spec and API) and
https://eclipse-ee4j.github.io/angus-mail/ (implementation).

## Install, setup and configuration
- **What the Boot starter pulls:** Boot 2: `spring-context-support` plus
  `com.sun.mail:jakarta.mail` 1.6 (`javax.mail`). Boot 3:
  `org.eclipse.angus:jakarta.mail`. Boot 4: the `spring-boot-mail` module with
  `jakarta.mail:jakarta.mail-api` (compile) and `org.eclipse.angus:angus-mail`
  (runtime).
- **Boot keys:** a `JavaMailSender` is auto-configured when `spring.mail.host`
  is set. `port` has no default (the protocol's own applies), `protocol`
  `smtp`, `default-encoding` UTF-8, `username`, `password`, `properties.*` (raw
  Session properties), `jndi-name` (overrides every other Session setting),
  `test-connection` false, `ssl.enabled` false (sets
  `mail.<protocol>.ssl.enable`), `ssl.bundle`, `ssl.verify-hostname` true.
- **SMTP timeouts** (same names on JavaMail 1.6 and Angus):
  `mail.smtp.connectiontimeout`, `mail.smtp.timeout` (read) and
  `mail.smtp.writetimeout` all default to infinite. `writetimeout` costs one
  thread per connection.
- **TLS:** `mail.smtp.starttls.enable` (default false) uses STARTTLS if the
  server offers it and otherwise "the connection continues without the use of
  TLS"; `mail.smtp.starttls.required` (default false) makes the connection fail
  instead. `mail.smtp.ssl.enable` gives implicit TLS. `mail.smtp.ssl.trust="*"`
  trusts every host.
- **Server identity:** `mail.smtp.ssl.checkserveridentity` defaults to false on
  JavaMail 1.6 and to true on Angus Mail. (Angus's SSLNOTES file still says the
  check is off by default; its javadoc and changelog are the newer statements.)

## Core API / usage shape
- **`Session`:** created from a `Properties` map describing the SMTP host, port,
  authentication (`mail.smtp.auth`) and transport security; the root factory
  for everything else.
- **`MimeMessage`:** from/to/cc/bcc addresses (`InternetAddress`), subject and
  content. A `MimeMultipart` assembles alternative bodies and attachments as
  `MimeBodyPart`s.
- **`Transport`:** sends the message. `Transport.send(message)` opens, sends and
  closes in one call. A `Transport` obtained explicitly is connected, sent
  through with `sendMessage` and closed by the caller; reusing one connected
  `Transport` for many messages is seed advice the fetched docs do not state
  (the `Transport` javadoc was not checked).
- **Authentication:** an `Authenticator`, or credentials on `Transport.connect`.
- **Spring:** `SimpleMailMessage` for plain text;
  `JavaMailSender.send(MimeMessagePreparator)`; `MimeMessageHelper(message, true)`
  for multipart, with `addAttachment(...)`, `addInline(contentId, resource)`
  referenced as `<img src='cid:...'>`, and `setText(plain, html)` for both
  alternatives. Provider exceptions map to Spring's `MailException` hierarchy.

## Idioms & best practices
- Build a multipart/alternative message with a plain-text and an HTML part so
  clients that cannot render HTML still show readable content.
- Set the three SMTP timeouts explicitly; Boot's reference shows 5000, 3000 and
  5000 ms through `spring.mail.properties[...]`.
- Use `starttls.enable` together with `starttls.required=true`, or implicit TLS,
  and set `ssl.checkserveridentity=true` explicitly so the behaviour does not
  depend on the implementation line.
- **Inline images:** `MimeMessageHelper`'s default `MULTIPART_MODE_MIXED_RELATED`
  puts text and inline parts in a nested `multipart/related` part and
  attachments in the `multipart/mixed` root (upstream calls it "arguably the
  most correct MIME structure"). Reference inline parts by `cid:` Content-ID,
  and add the text before the inline resources, since the other order does not
  work. Observed in practice: `cid:` inline images avoid the remote-image
  blocking of mail clients; upstream documents only the mechanism.
- Use a template library ([`freemarker.md`](./freemarker.md)) for non-trivial
  content.
- Keep SMTP host, credentials and TLS settings in external configuration;
  higher-level helpers wrap this API, so drop to it directly only for control
  over MIME structure or headers.

## General pitfalls
- **The artifact name hides the namespace** (see What it is): check the package
  root, not the coordinate.
- **`javax.mail` to `jakarta.mail` is a source-incompatible rename;** migrating
  means changing every import. Both package roots can be loaded at once, but
  code compiled against one does not satisfy imports of the other, so confirm
  which root the surrounding stack expects.
- **Angus 2 renamed the implementation packages** from `com.sun.mail` to
  `org.eclipse.angus.mail`, so code importing implementation classes
  (`com.sun.mail.smtp.*`, `com.sun.mail.util.MailSSLSocketFactory`) breaks.
- **Infinite timeouts:** an unresponsive SMTP server blocks the sending thread
  forever. Observed in practice: sending from a message-consumer thread lets
  one hung server stall the consumption of a whole queue.
- **STARTTLS downgrade:** `starttls.enable` without `starttls.required`
  continues in plaintext, login included, when the server does not offer
  STARTTLS.
- **No identity check on 1.6:** on Boot 2 the server certificate's host name is
  not checked by default.
- **Host-supplied jars.** Observed in practice: when the mail jars come from a
  host runtime (an application server or identity-server image) rather than
  the build manifest, the API version changes with that runtime and dependency
  diffing cannot see it.
- Sending is blocking network I/O; inline on a request thread it couples
  response latency to the mail server, so prefer a queued path for volume.

## Testing
- `spring.mail.test-connection=true` checks the mail server at startup.
- Upstream (Jakarta Mail, Angus, Spring) ships no SMTP test harness; tests use
  a local capture SMTP server, which is a community tool rather than part of
  this library.

## Security defaults
- Defaults by line: 1.6 has no server-identity check, optional STARTTLS and
  infinite timeouts; Angus checks server identity but STARTTLS is still
  optional and timeouts are still infinite. Boot's `spring.mail.ssl.verify-hostname`
  defaults to true for its own SSL support.
- `ssl.trust="*"` turns off certificate trust checks; keep it to tests.
- Keep `spring.mail.password` out of the repository (observed in practice:
  committed SMTP credentials).

## Operational behaviour
- Each SMTP write timeout runs on a scheduled executor thread per connection.
- Every send is a network round trip to the relay. Seed advice, not stated in
  the fetched docs: a connected `Transport` reused for a batch saves the
  per-message connection setup.

## Interop
- Spring Framework (`JavaMailSender`, `MimeMessageHelper`), Spring Boot
  (auto-configuration, SSL bundles), Jakarta Activation (Angus Activation),
  FreeMarker templates, and application or identity servers that ship their own
  mail jars.

## Major lines
### 1.6 (`javax.mail`; Boot 2)
- `com.sun.mail:jakarta.mail`; server identity unchecked by default.

### 2.0 (`jakarta.mail`; Jakarta EE 9)
- Same artifact; only the namespace changed, plus a Java SE 8 minimum.

### Jakarta EE 10 and later (Boot 3 and 4)
- API-only `jakarta.mail-api` plus Angus Mail. Angus checks server identity by
  default (changed on its 1 line) and renames its implementation packages to
  `org.eclipse.angus.mail` on its 2 line. Boot 4 splits mail into
  `spring-boot-mail` with `angus-mail` at runtime scope.

## Upstream docs
- https://jakartaee.github.io/mail-api/
- https://eclipse-ee4j.github.io/angus-mail/
- https://docs.spring.io/spring-framework/reference/integration/email.html
- https://docs.spring.io/spring-boot/reference/io/email.html
