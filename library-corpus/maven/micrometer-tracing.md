# micrometer-tracing — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Micrometer Tracing is a vendor-neutral tracing **facade** for JVM code
(`io.micrometer.tracing.Tracer`, `Span`, baggage) that plugs into the
Micrometer Observation API. A tracing setup has three parts: the facade
(`io.micrometer:micrometer-tracing`), one **bridge** to a tracer
implementation (`io.micrometer:micrometer-tracing-bridge-brave` for OpenZipkin
Brave, or `io.micrometer:micrometer-tracing-bridge-otel` for OpenTelemetry), and
a **reporter or exporter** (Zipkin's Brave reporter, or an OpenTelemetry
exporter such as OTLP). Versions come from
`io.micrometer:micrometer-tracing-bom`, or from Spring Boot's BOM. It succeeds
Spring Cloud Sleuth, which [`sleuth-zipkin`](./sleuth-zipkin.md) covers; it is a
replacement rather than a rename, since coordinates, packages and property keys
all differ. Reference: https://docs.micrometer.io/tracing/reference/.

## Install, setup and configuration
- **Pick the bridge once, early.** The bridge decides the exporter and the
  backend that every service talks to (observed in practice).
- **Spring Boot 3:** tracing auto-configuration ships in Actuator, so a service
  needs `spring-boot-starter-actuator`, a bridge and a reporter or exporter;
  Zipkin's Brave reporter is `io.zipkin.reporter2:zipkin-reporter-brave`.
- **Spring Boot 4:** declare `spring-boot-starter-zipkin` (Brave with Zipkin) or
  `spring-boot-starter-opentelemetry` (OpenTelemetry with OTLP). These starters
  bring the auto-configuration modules: `spring-boot-starter-zipkin` brings
  `spring-boot-micrometer-tracing-brave`, `spring-boot-zipkin` and the Brave
  bridge. Observed in practice, verified at class
  path, jar and run time: declaring only the bridge and reporter libraries
  yields no `Tracer` bean, no spans and no error, because the bridge jar carries
  no auto-configuration of its own.
- **Sampling.** `management.tracing.sampling.probability` defaults to `0.1`:
  Boot samples 10 % of requests to avoid overwhelming the backend. Set `1.0`
  where every trace matters (development, low-traffic services).
- **Propagation** (read from Boot's configuration metadata, observed in
  practice): `management.tracing.propagation.produce` defaults to `[W3C]`;
  `consume` defaults to `[W3C, B3, B3_MULTI]`;
  `management.tracing.propagation.type` sets both.
- **Master switch.** `management.tracing.enabled` on Boot 3,
  `management.tracing.export.enabled` on Boot 4.
- **Zipkin exporter keys.** Boot 3: `management.zipkin.tracing.*`. Boot 4:
  `management.tracing.export.zipkin.*`. Both default `endpoint` to
  `http://localhost:9411/api/v2/spans`; on Boot 4 `enabled` defaults to true and
  `encoding` to json. The old
  `management.zipkin.tracing.{endpoint,connect-timeout,read-timeout,encoding}`
  keys carry an error-level deprecation in the Boot 4 metadata, and an
  error-level property is not bound, so `MANAGEMENT_ZIPKIN_TRACING_ENDPOINT`
  does nothing. The metadata dates the deprecation earlier, but the Boot 3
  reference still lists the old key as current, so treat it as a Boot 4 break.
- **Log correlation.** With Micrometer Tracing, Boot adds a correlation id built
  from the `traceId` and `spanId` MDC values to log lines by default.

## Core API / usage shape
- Spans: `Span span = tracer.nextSpan().name("op")`, then
  `try (Tracer.SpanInScope ws = tracer.withSpan(span.start())) { ... }`,
  `span.tag(key, value)`, and `span.end()` in `finally`. `nextSpan()` makes
  the current span the parent; putting a span in scope sets the thread-local
  context and, when configured, the MDC.
- Prefer the Observation API (inject `ObservationRegistry`;
  `Observation.createNotStarted(name, registry).lowCardinalityKeyValue(key, value).observe(...)`):
  one observation yields both a metric and a span through the registered
  handlers. Use the lower-level `Tracer` only for a span without a metric.
- Baggage: `try (BaggageInScope scope = tracer.createBaggageInScope(name,
  value)) { ... }`. It propagates automatically with W3C; with B3 only the
  fields listed in `management.tracing.baggage.remote-fields` cross the wire.
  `management.tracing.baggage.correlation.fields` puts fields in the MDC.
- Boot instruments Spring MVC, WebFlux and the HTTP clients built from the
  auto-configured `RestTemplateBuilder`, `RestClient.Builder` and
  `WebClient.Builder`. A client built by hand does not propagate traces.

## Idioms & best practices
- Rely on the automatic Observation instrumentation (MVC, HTTP clients,
  `@Scheduled`) for operations it already covers; add spans by hand only for
  work it does not see (observed in practice).
- Choose one sampling rate for the whole fleet. A rate of 1 on a gateway beside
  defaults elsewhere makes "missing in Zipkin" ambiguous (observed in practice).
- Gate the wiring with a context test that asserts a real, non-no-op `Tracer`
  bean (observed in practice): every failure mode below is silent.
- **Async work:** wrap executors with `ContextExecutorService.wrap(...)` or
  `ContextScheduledExecutorService.wrap(...)` from the Context Propagation
  library; Reactor needs `Hooks.enableAutomaticContextPropagation()`.
- Custom metric tags on Framework 6 and later go in an `ObservationConvention`
  bean, replacing the old `*TagsProvider` types; see
  [`spring-framework`](./spring-framework.md).

## General pitfalls
- **Silent failure modes** (observed in practice). Missing auto-configuration,
  a collector that is down, a low sampling rate and a wrong property key all
  leave the application healthy, and "the collector looks empty" has several
  causes with no distinguishing signal.
- **Leftover Sleuth.** Remove Sleuth dependencies and configuration; what
  breaks silently in the move (inert keys, changed defaults, span names) is on
  [`sleuth-zipkin`](./sleuth-zipkin.md).
- **Audits only see what is on the class path** (observed in practice). A
  deprecation-metadata audit cannot flag a key whose module is absent.
- **Mixed fleets during a migration.** A default Sleuth service and a default
  Micrometer Tracing service do not share a propagation format; the break and
  the migration guide's recipe are on [`sleuth-zipkin`](./sleuth-zipkin.md).
- **Hand-built HTTP clients** lose propagation (see above).

## Testing
- `io.micrometer:micrometer-tracing-test` provides `SimpleTracer`, an in-memory
  `Tracer` for unit tests of custom handlers;
  `micrometer-tracing-integration-test` provides `SampleTestRunner`, which runs
  the code against the Brave and OpenTelemetry tracers and their reporters.
- Under `@SpringBootTest`, tracing components that report data are not
  auto-configured; annotate the test with `@AutoConfigureTracing` (Boot 4,
  from `spring-boot-micrometer-tracing-test`) when it needs them. A sliced test
  with that annotation gets a no-op `Tracer` and an `ObservationRegistry`. On Boot 3 the slice switch was
  `@AutoConfigureObservability`. A wiring test must account for this.

## Security defaults
- Trace and span ids, tags and baggage leave the process in headers and in
  exported spans: never tag secrets or personal data, and treat baggage as
  visible to every downstream service. The fetched references give this no
  section of their own; it follows from what propagation sends.
- The default 10 % sampling also limits how much request data reaches the
  backend.

## Operational behaviour
- On Boot 3 and later a `TracingAwareMeterObservationHandler` turns every
  completed observation into a span.
- How reporters buffer and retry when the collector is down is not covered by
  the fetched references; check the chosen reporter's documentation.
- With the OpenTelemetry bridge, Zipkin export is deprecated upstream and Boot
  plans to remove its auto-configuration within the Boot 4 line; prefer OTLP,
  or Brave when Zipkin is the backend.

## Interop
- [`spring-boot`](./spring-boot.md): starters, properties and test support.
- [`sleuth-zipkin`](./sleuth-zipkin.md): the predecessor and the crossing from
  it (mixed-fleet propagation, changed defaults).
- [`spring-framework`](./spring-framework.md): Observation instrumentation and
  conventions.
- Zipkin or an OpenTelemetry collector as the backend.

## Major lines
### With Spring Boot 3
Actuator carries the auto-configuration; add a bridge and a reporter. Zipkin
endpoint `management.zipkin.tracing.endpoint`; test switch
`@AutoConfigureObservability`.

### With Spring Boot 4
Dedicated starters (`spring-boot-starter-zipkin`,
`spring-boot-starter-opentelemetry`) bring the auto-configuration modules.
Zipkin endpoint `management.tracing.export.zipkin.endpoint`; test switch
`@AutoConfigureTracing`. OpenTelemetry-to-Zipkin support is deprecated.

## Upstream docs
- https://docs.micrometer.io/tracing/reference/
- https://docs.micrometer.io/tracing/reference/api.html
- https://docs.micrometer.io/tracing/reference/testing.html
- https://docs.spring.io/spring-boot/reference/actuator/tracing.html
- https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html
