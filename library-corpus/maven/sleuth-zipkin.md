# sleuth-zipkin — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Distributed tracing for Spring applications. Spring Cloud Sleuth
(`org.springframework.cloud:spring-cloud-sleuth`) instruments an application
with trace and span identifiers, injects them into the logging context, and
propagates them across service boundaries — inbound and outbound HTTP calls,
messaging, and scheduled work — so a single request can be followed across
services. The companion Zipkin reporter
(`org.springframework.cloud:spring-cloud-sleuth-zipkin`) exports completed
spans to a Zipkin collector, where the trace can be visualized as a timeline.

**The Spring tracing surface has moved across major lines** — the underlying
instrumentation library and its package/configuration have changed, and the
Sleuth artifacts above are not the tracing entry point on every Spring line.
Confirm which tracing dependency and bridge apply to the line in use before
adopting the arrangement on this page; the concepts below (spans, context
propagation, sampling, an exporter shipping to a collector) carry across, the
coordinates do not.

## Core API / usage shape
- Instrumentation is largely automatic once the dependencies are present:
  Sleuth wraps the common entry and exit points, creates spans, and adds trace
  and span IDs to each log line so logs across services can be correlated by
  trace ID.
- A trace context is propagated over the wire using standard headers, so a
  downstream service continues the same trace rather than starting a new one.
- The Zipkin reporter batches finished spans and ships them to a configured
  collector endpoint; sampling controls what fraction of traces are reported.

## Idioms & best practices
- Let the framework carry the trace context end to end; avoid manually
  constructing or forwarding trace headers, which defeats the automatic
  propagation.
- Let the Spring Cloud release-train BOM govern the tracing starter's version
  rather than pinning it independently — see [`spring-cloud.md`](./spring-cloud.md),
  which owns the BOM rule.

## General pitfalls
- Spans are only useful if they reach the collector: unreachable collector
  endpoints or an overly aggressive sampling rate produce empty or misleading
  traces without failing the application.

## Upstream docs
- https://spring.io/projects/spring-cloud-sleuth
- https://micrometer.io/docs/tracing
- https://zipkin.io/
