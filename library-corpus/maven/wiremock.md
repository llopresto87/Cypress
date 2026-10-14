# wiremock — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
WireMock is an HTTP stub server for tests: it runs a real HTTP(S) server,
answers requests from stub mappings defined in Java or JSON, records what it
received so tests can verify calls, and can inject delays and faults. A test
points the client under test at WireMock instead of the real service. It runs
in-process in a JVM test, as a standalone process, or as a container image.

- `org.wiremock:wiremock`: the standard jar, for in-process use in tests. On
  the 3.x line it embeds Jetty 11 and depends on Jetty, Jackson 2, Guava,
  Apache HttpClient 5, Handlebars, JSONPath and XMLUnit as ordinary
  dependencies.
- `org.wiremock:wiremock-jetty12`: the same server on Jetty 12, from 3.5.0. It
  depends on `org.wiremock:wiremock` with its Jetty excluded, and adds Jetty
  12's core modules and the `ee10` servlet modules. Needed on a classpath
  where a framework already manages Jetty 12, so Jetty 11 cannot live there.
- `org.wiremock:wiremock-standalone`: an uber jar with most dependencies
  shaded into private packages, so it does not clash with the project's own
  versions. It is also the runnable jar for the standalone process.
- `com.github.tomakehurst:wiremock-jre8` and
  `com.github.tomakehurst:wiremock-jre8-standalone`: the 2.x coordinates,
  renamed to the two `org.wiremock` artifacts above in 3.0.0.

`org.wiremock.integrations:wiremock-spring-boot`, the Spring Boot test
integration, is a separate project, cited in Testing. Upstream home:
https://wiremock.org/docs/ and https://github.com/wiremock/wiremock. The Java
packages stay under `com.github.tomakehurst.wiremock` on every line.

## Install, setup and configuration
- **Choose the artifact by classpath.** The standard jar is the default.
  `-jetty12` is for a build whose framework already manages Jetty 12. The
  standalone jar avoids every dependency conflict, at the cost described
  under General pitfalls. Declare it in `test` scope, because neither the
  stub server nor its Jetty belongs in the application.
- **Java.** 3.0.0 dropped Java 8; its upgrade guide says to move to Java 11
  or 17. The Jetty 12 module lists Java 17 as a prerequisite.
- **No framework BOM manages WireMock.** Spring Boot's dependency BOM has no
  WireMock entry, so the project states the version.
- **Configuration** goes through `WireMockConfiguration.options()` (alias
  `wireMockConfig()`), passed to `new WireMockServer(...)` or to the JUnit
  extension. Defaults that matter:
  - `port`: 8080; `dynamicPort()` picks a free one. `httpsPort` is off unless
    set; `dynamicHttpsPort()` picks one.
  - `bindAddress`: the configuration page says it defaults to the loopback
    adapter, while the 3.x source's default is `0.0.0.0`, all interfaces. Set it
    explicitly (see Security defaults).
  - Files and mappings root: `src/test/resources` when started
    programmatically (`usingFilesUnderDirectory`, `usingFilesUnderClasspath`).
  - The request journal records every request without limit by default
    (`maxRequestJournalEntries`, `disableRequestJournal`); verification needs
    it.
  - Responses are sent chunked by default (`useChunkedTransferEncoding`:
    `ALWAYS`, `BODY_FILE`, `NEVER`), so stubbed responses carry no
    `Content-Length` unless the policy changes.
  - Response templating is enabled in local mode by default when started
    programmatically (from 3.0.0). From 3.7.0 the compiled-template cache
    holds 1000 entries by default; before, it was unlimited.
  - `jettyHeaderBufferSize` (default 8192) limits request header size;
    `gzipDisabled(true)` stops response gzipping.
  - `notifier(...)`: logging goes to SLF4J by default.

## Core API / usage shape
- **Server:** `WireMockServer server = new WireMockServer(options().dynamicPort());
  server.start(); ... server.stop();`. `server.port()` and `server.baseUrl()`
  tell the client where to go. The server object carries the same stubbing and
  verification DSL as the static client.
- **Stubbing:** `stubFor(get(urlPathEqualTo("/things")).withQueryParam("q",
  equalTo("x")).willReturn(okJson("{...}")))`. Request builders cover method
  (`get`, `post`, `any`, `getOrHead`), URL, headers, cookies, query and form
  parameters, basic auth and body. Response builders are `aResponse()` with
  `withStatus`, `withHeader`, `withBody` and `withBodyFile`, plus shortcuts
  (`ok`, `okJson`, `status`).
- **URL matchers:** `urlEqualTo` and `urlMatching` match path *and* query
  string; `urlPathEqualTo`, `urlPathMatching` and `urlPathTemplate` match the
  path only, and query parameters are then matched with `withQueryParam` in any
  order.
- **Body matchers:** `equalTo`, `containing`, `matching` (regex),
  `equalToJson(json, ignoreArrayOrder, ignoreExtraElements)`,
  `matchesJsonPath`, `matchesJsonSchema`, `equalToXml`, `matchesXPath`, and
  `not(...)`.
- **Precedence:** when several stubs match, the most recently added one wins,
  unless `atPriority(n)` says otherwise (1 is highest; the default is 5).
- **Verification:** `verify(postRequestedFor(urlEqualTo("/x")).withHeader(...))`,
  `verify(3, ...)`, `verify(lessThan(5), ...)` and kin; `findAll(...)` returns
  the logged requests. `findUnmatchedRequests()` and `findNearMissesFor(...)`
  explain why a request matched no stub.
- **Faults and delays:** `withFixedDelay(ms)`, `withLogNormalRandomDelay`,
  `withChunkedDribbleDelay(chunks, totalMs)`, a global `setGlobalFixedDelay`,
  and `withFault(Fault.EMPTY_RESPONSE | MALFORMED_RESPONSE_CHUNK |
  RANDOM_DATA_THEN_CLOSE | CONNECTION_RESET_BY_PEER)`.
- **State:** `inScenario(name).whenScenarioStateIs(STARTED)
  .willSetStateTo(next)` makes the same request answer differently over a
  sequence; every scenario starts in `Scenario.STARTED`, and
  `resetAllScenarios()` rewinds them.
- **Remote client:** `WireMock.configureFor(host, port)` points the static DSL
  at another server; `new WireMock(host, port)` talks to several. The same
  operations are available as the JSON admin API under `/__admin`.

## Idioms & best practices
- **Dynamic ports always.** Start on `dynamicPort()` and inject the URL into
  the client under test, so parallel test runs and CI agents never collide.
- **Match on path plus explicit parameters.** Prefer `urlPathEqualTo` with
  `withQueryParam` to `urlEqualTo` with a query string; the latter depends on
  parameter order and encoding.
- **Verify what matters, and let unmatched requests fail.** A stub that
  answers anything (`any(anyUrl())`) hides a wrong path. The JUnit extension
  fails a test on unmatched requests by default; keep it so.
- **Catch-all stubs at low priority.** Give a fallback stub a high priority
  number (low precedence) so specific stubs win regardless of the order in
  which they were added.
- **Prove error handling with faults, not only status codes.** A 500 tests one
  branch; `CONNECTION_RESET_BY_PEER`, `EMPTY_RESPONSE` and a dribble delay
  longer than the client's read timeout test the others.
- **Keep large or shared payloads as files** (`withBodyFile`, under the files
  root's `__files`), and JSON mappings under `mappings`, so the same stubs
  serve a standalone or container instance.
- **Use synthetic data in stubs.** Recorded traffic (`record` and playback)
  captures whatever the real service returned; scrub it before committing.

## General pitfalls
- **The servlet-profile modules escape a framework BOM.** Jetty 12 splits into
  core modules (`org.eclipse.jetty:jetty-*`) and per-Jakarta-EE-profile
  servlet modules (`org.eclipse.jetty.ee10:jetty-ee10-*`,
  `org.eclipse.jetty.ee11:jetty-ee11-*`). `wiremock-jetty12` uses the `ee10`
  modules and its POM manages them at the Jetty version it was built against.
  A framework BOM that manages Jetty core at a different line, and imports a
  different profile BOM, moves the core modules but leaves the `ee10` ones
  behind. Spring Boot's 3.5 BOM imports `jetty-ee10-bom` and its 4.0 BOM
  imports `jetty-ee11-bom`, so under Boot 4 the skew appears. Observed in
  practice: the stub server failed at startup with `NoSuchMethodError` in
  `ServletContextHandler`'s static initializer (core and `ee10` modules from
  different Jetty minors). The fix that held: import
  `org.eclipse.jetty.ee10:jetty-ee10-bom` in the project's
  `<dependencyManagement>` at the framework's own Jetty version property
  (`${jetty.version}` under Boot), so both halves resolve to one Jetty line.
  The import adds no artifact, it only aligns versions; keep every Jetty module
  in `test` scope. Upstream's Jetty 12 page does not discuss BOMs.
- **The standalone jar hides its dependencies.** Its POM declares none, and its
  Jetty and Jackson are shaded inside it. It ends the classpath conflict, but
  the dependency tree, version-alignment checks and dependency scanners no
  longer see those libraries, and a framework's Jetty upgrade never reaches
  them. Observed in practice: switching to the standalone jar made the
  conflict disappear and also removed the only test that exercised the Jetty
  line. Prefer the aligned non-shaded artifact when the build gates on its
  dependency tree.
- **Two Jackson lines on one classpath.** WireMock 3.x uses Jackson 2
  (`com.fasterxml.jackson`), while a framework on Jackson 3 uses
  `tools.jackson`. The group ids differ, so both resolve side by side (Spring
  Boot 4's BOM manages both); nothing breaks, but code must import the right
  `ObjectMapper` for each.
- **The default HTTPS certificate proves nothing about trust or host names.**
  WireMock serves a self-signed certificate from a keystore bundled in the
  jar, with a fixed personal common name and no Subject Alternative Name, so
  a client verifying host names rejects it for `localhost` even after the
  certificate itself is trusted. A test meant to show that the client refuses
  an untrusted certificate passes for the wrong reason. Serve a certificate
  generated for the test (for example with `keytool -ext san=dns:localhost`)
  through `keystorePath`, `keystorePassword` and `keyManagerPassword`. Upstream
  documents the self-signed default and the `PKIX path building failed` error,
  not the missing SAN.
- **Jetty 12 limitations** (upstream's list): a stubbed status message is not
  sent to the client, a base64 (or otherwise encoded) multipart body is not
  decoded to text, and a folder requested without a trailing slash is always
  redirected.
- **`CONNECTION_RESET_BY_PEER` is reliable only on Unix-like systems;** on
  Windows upstream says the connection is more likely to hang.
- **An unbounded request journal** keeps every request and logged response
  body; in long or load-style runs it exhausts the heap. Cap it with
  `maxRequestJournalEntries` and `maxLoggedResponseSize`.
- **Instance fields restart the server per test.** In the JUnit extension, a
  non-static `@RegisterExtension` field creates and starts a server before each
  test method; a static one lives for the class.

## Testing
- **JUnit 5:** `@WireMockTest` starts one server per test class on a random
  HTTP port (no HTTPS unless `httpsEnabled = true`), configures the static DSL,
  and resets stubs and the request log before each test. A
  `WireMockRuntimeInfo` parameter gives the port, base URL and an instance DSL.
  `@RegisterExtension static WireMockExtension wm = WireMockExtension.newInstance()
  .options(wireMockConfig().dynamicPort()).build()` runs any number of servers
  with full configuration. `resetOnEachTest(false)` (from 3.13.0) keeps stubs
  across methods; `failOnUnmatchedRequests(false)` relaxes the default
  failure; `proxyMode(true)` routes several host names through one server when
  the client honours the JVM proxy properties.
- **Spring Boot:** `org.wiremock.integrations:wiremock-spring-boot` adds
  `@EnableWireMock` to a `@SpringBootTest`, starts the server on a random port
  and exposes `wiremock.server.baseUrl` and `wiremock.server.port` as
  properties; `@ConfigureWireMock` names instances, renames the properties
  and points at mapping roots. Map the client's base-URL property to it in the
  test configuration only, so production never reads a stub address.
- **Containers:** the `wiremock/wiremock` image and the community
  Testcontainers modules run the same JSON mappings out of process; see
  [`testcontainers.md`](./testcontainers.md).
- Keep one test that starts the real server and sends a real request through
  the production HTTP client, on the classpath the application tests use; it
  is the test that catches the Jetty alignment problem above.

## Security defaults
- **Bind address:** do not rely on the default (the docs and the 3.x source
  disagree, Install above). On a shared CI agent or developer machine, set
  `bindAddress("127.0.0.1")` so the stub server and its admin API are not
  reachable from the network.
- **Admin API:** `/__admin` creates and deletes stubs and reads the request
  log; upstream sends CORS headers on admin responses always. Treat a reachable
  WireMock port as writable by whoever can reach it.
- **Proxying and recording** can reach any address unless restricted:
  `limitProxyTargets(NetworkAddressRules...)` allows or denies targets.
  `enableBrowserProxying` with a CA keystore makes WireMock mint certificates;
  keep that CA out of any real trust store.
- **HTTPS:** the bundled certificate is public, so it gives no
  confidentiality; client certificates (`needClientAuth`) need a trust store,
  and Jetty requires client certificates to carry SANs.
- Stubs and recordings are committed files: never store real credentials,
  tokens or personal data in them.

## Operational behaviour
- Startup binds the ports and starts Jetty in-process; `stop()` releases
  them. A server never stopped keeps its port and threads until the JVM exits.
- Jetty request threads, acceptors and the accept queue are configurable
  (`containerThreads`, `jettyAcceptors`, `jettyAcceptQueueSize`); upstream says
  they need tuning only for load testing, where `asynchronousResponseEnabled`
  frees threads during delays.
- Memory grows with the request journal and logged response bodies (see
  General pitfalls). Webhooks run on a pool of 10 threads by default
  (`withWebhookThreadPoolSize`, from 3.13.0).

## Interop
- [`spring-framework.md`](./spring-framework.md) and
  [`spring-boot.md`](./spring-boot.md): `WebClient`, `RestClient` and the
  framework's HTTP connectors are the usual clients under test; Boot's BOM is
  the usual source of the Jetty alignment problem.
- [`testcontainers.md`](./testcontainers.md): running WireMock as a container
  next to other test dependencies.
- [`jackson.md`](./jackson.md): WireMock's own Jackson 2 dependency.
- A servlet application on Tomcat or Undertow is unaffected by WireMock's
  embedded Jetty at runtime; the two servers are separate, and Jetty stays in
  test scope.

## Major lines
### 2.x
- Coordinates `com.github.tomakehurst:wiremock-jre8` and
  `wiremock-jre8-standalone`; Jetty 9; Java 8. The JSON API of 2.x stays
  compatible with 3.x.

### 3.x
- 3.0.0: group id `org.wiremock`, artifacts renamed to `wiremock` and
  `wiremock-standalone`; Java 8 dropped; Jetty 9 to Jetty 11; standalone entry
  point `wiremock.Run`; response templating on by default in local mode, so
  2.x code constructing `ResponseTemplateTransformer` no longer compiles;
  the legacy recorder deprecated. 3.1.0 folds the webhooks extension into the
  core, so its separate dependency must be removed.
- 3.5.0 adds Jetty 12 support through `wiremock-jetty12`.

### 4.x
- Published as betas, which upstream says will carry breaking changes. The
  core is split from its dependencies into `wiremock-core`, `wiremock-jetty`,
  `wiremock-junit5` (or `wiremock-junit4`) and `wiremock-httpclient-apache5`,
  with `wiremock-standalone` kept; only Jetty 12 is supported, later betas move
  to Jetty 12.1 with Jakarta EE 11, and Jetty classes are repackaged. Re-read
  this page's Jetty and artifact facts before adopting it.

## Upstream docs
- Download and installation: https://wiremock.org/docs/download-and-installation/
- Jetty 12: https://wiremock.org/docs/jetty-12/
- JUnit 5+ Jupiter: https://wiremock.org/docs/junit-jupiter/
- Plain Java: https://wiremock.org/docs/java-usage/
- Java configuration: https://wiremock.org/docs/configuration/
- Stubbing: https://wiremock.org/docs/stubbing/
- Request matching: https://wiremock.org/docs/request-matching/
- Verifying: https://wiremock.org/docs/verifying/
- Simulating faults: https://wiremock.org/docs/simulating-faults/
- Stateful behaviour: https://wiremock.org/docs/stateful-behaviour/
- HTTPS: https://wiremock.org/docs/https/
- Spring Boot integration: https://wiremock.org/docs/spring-boot/
- Testcontainers: https://wiremock.org/docs/solutions/testcontainers/
- Release notes: https://github.com/wiremock/wiremock/releases
- Source: https://github.com/wiremock/wiremock
