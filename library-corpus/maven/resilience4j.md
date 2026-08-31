# resilience4j — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A lightweight fault-tolerance library for the JVM, built as composable
functional decorators. It provides a circuit breaker, rate limiter, retry,
bulkhead, and time limiter that wrap a call so a failing or slow dependency
degrades gracefully — falling back — instead of cascading failure through the
system. The core modules live under `io.github.resilience4j:*`; the Spring
Cloud CircuitBreaker integration is
`org.springframework.cloud:spring-cloud-starter-circuitbreaker-resilience4j`.

## Core API / usage shape
- The circuit breaker moves through closed, open, and half-open states: after a
  configurable failure rate it opens and short-circuits calls, then periodically
  probes with a half-open state before closing again.
- Via the Spring Cloud CircuitBreaker integration, an outbound client method
  (e.g. an HTTP client, or a declarative client per
  [`spring-cloud-openfeign.md`](./spring-cloud-openfeign.md)) is annotated with a
  circuit-breaker annotation paired with a fallback — a `FallbackFactory` or
  fallback method — that supplies a response when the breaker is open or the
  call fails.
- The other patterns compose with the breaker: retry re-attempts transient
  failures, the rate limiter caps call throughput, the bulkhead caps concurrent
  calls, and the time limiter bounds how long a call may run.

## Idioms & best practices
- Apply resilience at the boundary to a remote dependency (outbound HTTP,
  messaging, database), not to pure in-process logic where it adds no value.
- Always pair a breaker with a meaningful fallback: a fallback that returns a
  sensible default or a fast, explicit failure is what turns an open breaker
  from an outage into a degraded-but-serving state.

## General pitfalls
- A common failure mode is the dependency being on the classpath but never
  actually wired to any annotation or configured instance — "declared but
  dormant." Its mere presence gives a false sense of protection; verify that a
  breaker (or retry, or limiter) is genuinely exercised on a real call path, not
  just available.
- Retry stacked naively on top of a breaker can amplify load against a failing
  dependency; configure the interaction between retry and breaker deliberately
  rather than enabling both blindly.
- A fallback masks the outage it absorbs — it degrades silently, so pair it with
  metrics or alerting, or a failing dependency reads as success.

## Upstream docs
- https://resilience4j.readme.io/
- https://github.com/resilience4j/resilience4j
- https://spring.io/projects/spring-cloud-circuitbreaker
