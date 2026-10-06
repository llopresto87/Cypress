# sleuth-zipkin — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Distributed tracing for Spring applications, reported to a Zipkin collector.
Tracing instruments an application with trace and span ids, puts them in the
logging context, and propagates them across service boundaries (inbound and
outbound HTTP, messaging, scheduled work), so one request can be followed
across services; a reporter exports finished spans to Zipkin, where a trace
shows as a timeline.

**The Spring tracing surface changed at the Boot 3 boundary.** This page
covers the Boot 2 side and the crossing:
- **Boot 2 (Spring Cloud trains 2020.0 and 2021.0): Spring Cloud Sleuth.**
  `org.springframework.cloud:spring-cloud-starter-sleuth` (Brave by default)
  plus `org.springframework.cloud:spring-cloud-sleuth-zipkin`, versioned by the
  Spring Cloud BOM. Sleuth is no longer actively maintained, its last line is
  3.1, and it does not work with Boot 3 or later; train 2022.0 removed it.
  Sleuth 2 on earlier trains is not covered here.
- **Boot 3 and later: Micrometer Tracing** replaces Sleuth (upstream calls it
  essentially a Spring-agnostic copy of Sleuth). Its coordinates, keys,
  defaults, API and tests are on [`micrometer-tracing.md`](./micrometer-tracing.md);
  this page keeps Sleuth and the crossing.

The concepts (spans, context propagation, sampling, an exporter shipping to a
collector) carry across; the coordinates, keys and defaults do not. Upstream
homes: https://docs.spring.io/spring-cloud-sleuth/docs/current/reference/html/
and https://zipkin.io for the collector.

## Install, setup and configuration
### Sleuth (Boot 2)
- Propagation defaults to B3 (`spring.sleuth.propagation.type` takes a list;
  Brave supports `AWS`, `B3`, `W3C`). `spring.sleuth.trace-id128` defaults to
  false and `spring.sleuth.supports-join` to true.
- The default sampler is rate-limited, 10 traces per second
  (`spring.sleuth.sampler.rate`; upstream says to use more than 100 per second
  with extreme caution), not a fraction; `spring.sleuth.sampler.probability`
  switches to a probability. Trace ids reach the logs whether or not a trace
  is sampled.
- Zipkin: `spring.zipkin.base-url` defaults to `http://localhost:9411/`; a
  service id in that URL is resolved through discovery
  (`spring.zipkin.discovery-client-enabled=false` turns it off).
  `spring.zipkin.sender.type` selects web, rabbit, kafka or activemq sending;
  set it explicitly for a messaging sender.

### Crossing to Micrometer Tracing
- After the move, `logging.pattern.correlation` can restore the Sleuth log
  layout `[${spring.application.name:},%X{traceId:-},%X{spanId:-}]`.

## Core API / usage shape
- Instrumentation is largely automatic once the dependencies are present: the
  framework wraps common entry and exit points, creates spans, and adds the
  ids to every log line.
- Context crosses the wire in standard headers, so a downstream service
  continues the trace instead of starting one.
- **Sleuth manual spans:** `tracer.nextSpan().name(...)`,
  `tracer.withSpan(span.start())`, `span.end()` in `finally`; `@NewSpan` and
  `@ContinueSpan`.
- **Moving to Micrometer Tracing:** most code migrates by changing the package
  from `org.springframework.cloud.sleuth` to `io.micrometer.tracing`.

## Idioms & best practices
- Tracing is configuration, not code: let the framework carry context, use the
  Boot-provided client builders, and never hand-roll trace headers.
- Let the Spring Cloud BOM govern the Sleuth starter's version. This holds only
  for coordinates the train manages: an older-era starter such as
  `spring-cloud-starter-zipkin` may be unmanaged and need an explicit version,
  which is version skew. Observed in practice: on the Sleuth 3 line the managed
  pair is `spring-cloud-starter-sleuth` plus `spring-cloud-sleuth-zipkin`. See
  [`spring-cloud.md`](./spring-cloud.md), which owns the BOM rule.
- **Mixed fleets:** on the Sleuth side set `spring.sleuth.propagation.type=w3c,b3`,
  `spring.sleuth.traceId128=true` and `spring.sleuth.supportsJoin=false`, so
  Boot 2 and Boot 3+ services continue each other's traces (the Micrometer
  migration guide's recipe).

## General pitfalls
- **Broken traces in a mixed fleet.** Sleuth produces B3 by default; Micrometer
  Tracing produces only W3C. A Boot 3+ caller's context is not continued by a
  default Sleuth callee, which is why the migration recipe above exists.
- **Boot 3 changed defaults:** 128-bit trace ids, no joined spans (client and
  server get separate spans), one propagation type per direction.
- On Boot 4 the install and key changes that break a migrated service silently
  are on [`micrometer-tracing.md`](./micrometer-tracing.md).
- **Sleuth keys are inert after the move.** Micrometer Tracing reads no
  `spring.sleuth.*` key, so a deliberate Sleuth sample rate is silently replaced
  by probability 0.1, which is not the Sleuth default either (10 per second).
- **Span names change.** Observed in practice: Sleuth instrumentation and
  Observation-based instrumentation name spans differently, so dashboards and
  queries keyed by span name break across the move. Upstream does not list the
  name changes.
- **A missing span proves nothing.** Sampling, an unreachable collector and no
  traffic look alike, and reporting is asynchronous, so a collector outage does
  not fail the application (observed in practice, consistent with the
  asynchronous reporter).
- **Sleuth sampler deadlock.** Using the sampler early (in `@PostConstruct`) can
  deadlock because sampler beans are refresh-scoped; define the sampler or set
  `spring.sleuth.sampler.refresh.enabled=false`.

## Testing
- Sleuth always put a real `Tracer` in the test context; Micrometer Tracing
  tests need an annotation (see [`micrometer-tracing.md`](./micrometer-tracing.md)).

## Security defaults
- Boot exposes only `health` over HTTP by default. On Sleuth the `traces`
  actuator endpoint holds finished spans (`management.endpoint.traces.queue-size`);
  do not expose it publicly.
- Sampling limits volume, not content: spans carry whatever the
  instrumentation records, so review tags before exposing a collector
  (observed in practice; upstream is silent on content filtering).
- For the Zipkin server's own security, see
  [`../container/zipkin.md`](../container/zipkin.md).

## Operational behaviour
- Spans are reported asynchronously; Sleuth senders are HTTP, RabbitMQ, Kafka
  and ActiveMQ.

## Interop
- **Zipkin server:** see [`../container/zipkin.md`](../container/zipkin.md).
- OpenFeign, Spring Cloud Stream/Rabbit and the web clients propagate context
  through instrumentation on both lines
  ([`spring-cloud-openfeign.md`](./spring-cloud-openfeign.md),
  [`spring-cloud-stream.md`](./spring-cloud-stream.md)).
- Logback and Log4j2 read the ids from the MDC.

## Major lines
### Boot 2: Sleuth 3 (trains 2020.0 and 2021.0)
- Sleuth 3 split `spring-cloud-sleuth-core` into `-api` and
  `-instrumentation` and added `-autoconfigure`. Keys under `spring.sleuth.*`
  and `spring.zipkin.*`; B3 propagation; rate-limited sampler.

### Boot 3 and later
- No Sleuth; moving off it is a coordinate rewrite, not a version bump. See
  [`micrometer-tracing.md`](./micrometer-tracing.md) Major lines.

## Upstream docs
- https://spring.io/projects/spring-cloud-sleuth
- https://docs.spring.io/spring-cloud-sleuth/docs/current/reference/html/appendix.html
- https://github.com/micrometer-metrics/tracing/wiki/Spring-Cloud-Sleuth-3.1-Migration-Guide
- https://zipkin.io/
