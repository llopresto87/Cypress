# resilience4j — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A lightweight fault-tolerance library for the JVM, built as composable
functional decorators. It wraps a call (any functional interface, lambda or
method reference) with a circuit breaker, rate limiter, retry, bulkhead, time
limiter or cache, so a failing or slow dependency degrades into a fallback
instead of cascading through the system; decorators stack. Core modules are
`io.github.resilience4j:resilience4j-circuitbreaker`,
`io.github.resilience4j:resilience4j-ratelimiter`,
`io.github.resilience4j:resilience4j-retry`,
`io.github.resilience4j:resilience4j-bulkhead`,
`io.github.resilience4j:resilience4j-timelimiter`, and
`io.github.resilience4j:resilience4j-all` for the `Decorators` builder. Spring
Boot integration: `io.github.resilience4j:resilience4j-spring-boot2`,
`io.github.resilience4j:resilience4j-spring-boot3`, and
`io.github.resilience4j:resilience4j-spring-boot4` (newest 2.x releases only).
Spring Cloud CircuitBreaker wraps it as
`org.springframework.cloud:spring-cloud-starter-circuitbreaker-resilience4j`
(servlet) and
`org.springframework.cloud:spring-cloud-starter-circuitbreaker-reactor-resilience4j`
(reactive). Upstream home: https://resilience4j.readme.io, source on GitHub
`resilience4j/resilience4j`; Spring Cloud CircuitBreaker at
https://docs.spring.io/spring-cloud-circuitbreaker/reference/.

## Install, setup and configuration
- **Runtime expectations.** The Boot module expects
  `spring-boot-starter-actuator` and the AOP starter at runtime
  (`spring-boot-starter-aop`, renamed `spring-boot-starter-aspectj` on Boot 4);
  WebFlux also needs `resilience4j-reactor`. Neither the Spring Cloud starter
  nor the Boot module brings AspectJ itself.
- **Property layout.** `resilience4j.<module>.configs.<name>` (with `default`
  as the shared base) and `resilience4j.<module>.instances.<name>` with
  `baseConfig`; a `<Module>ConfigCustomizer` bean overrides one instance in
  code. Spring Cloud CircuitBreaker: properties beat Java `Customizer`
  configuration, an id's config beats its group's, which beats the global
  default, and `create("id")` with no matching instance uses the global
  defaults. `spring.cloud.circuitbreaker.resilience4j.enabled=false` turns the
  Spring Cloud auto-configuration off.
- **CircuitBreaker defaults:** `failureRateThreshold` 50%,
  `slowCallRateThreshold` 100%, `slowCallDurationThreshold` 60 s,
  `permittedNumberOfCallsInHalfOpenState` 10, `maxWaitDurationInHalfOpenState`
  0 (wait indefinitely), `slidingWindowType` COUNT_BASED, `slidingWindowSize`
  100, `minimumNumberOfCalls` 100, `waitDurationInOpenState` 60 s,
  `automaticTransitionFromOpenToHalfOpenEnabled` false; every exception is
  recorded as a failure and none is ignored.
- `recordExceptions`: once set, every other exception counts as a success
  unless ignored. `ignoreExceptions` count as neither failure nor success,
  even if also recorded.
- **Other defaults:** Retry `maxAttempts` 3 (the first call included),
  `waitDuration` 500 ms at a constant interval. Bulkhead `maxConcurrentCalls`
  25, `maxWaitDuration` 0. TimeLimiter `timeoutDuration` 1 s.

## Core API / usage shape
- **States:** CLOSED, OPEN and HALF_OPEN, plus METRICS_ONLY, DISABLED and
  FORCED_OPEN. OPEN rejects calls with `CallNotPermittedException`; after
  `waitDurationInOpenState` the breaker goes HALF_OPEN and lets the permitted
  calls probe.
- **Annotations:** `@CircuitBreaker`, `@Retry`, `@RateLimiter`, `@Bulkhead`
  (semaphore by default, `type = THREADPOOL` for a thread-pool bulkhead) and
  `@TimeLimiter`, on synchronous, `CompletableFuture` and Reactor return types.
- **Fallbacks** work like a catch block: every exception goes to the
  best-matching fallback, whatever the breaker state. The fallback lives in the
  same class with the same signature plus one exception parameter.
- **Aspect order,** outermost first:
  `Retry ( CircuitBreaker ( RateLimiter ( TimeLimiter ( Bulkhead ( Function ) ) ) ) )`.
  The `*AspectOrder` properties change it (higher value, higher priority), or
  chain functionally instead.
- **Spring Cloud CircuitBreaker:** `Resilience4JCircuitBreakerFactory` /
  `ReactiveResilience4JCircuitBreakerFactory` with `configureDefault` and
  `configure(..., ids)` customizers; `addCircuitBreakerCustomizer` attaches
  event handlers.
- **Feign and Gateway:** with `spring.cloud.openfeign.circuitbreaker.enabled=true`
  every Feign method is wrapped, under generated ids such as `FooClientbar`
  ([`spring-cloud-openfeign.md`](./spring-cloud-openfeign.md)); the gateway's
  `CircuitBreaker` route filter uses the reactive starter
  ([`spring-cloud-gateway.md`](./spring-cloud-gateway.md)).

## Idioms & best practices
- Apply resilience at the boundary to a remote dependency (HTTP, messaging,
  database), not to in-process logic.
- Pair every breaker with a meaningful fallback: a sensible default or a fast,
  explicit failure turns an open breaker into degraded service instead of an
  outage.
- Size the breaker to the traffic: with 100-call windows and
  `minimumNumberOfCalls` 100, a low-traffic dependency never opens it.
- Use `ignoreExceptions` (or a predicate) so mapped client errors (4xx business
  exceptions) do not count as failures.
- Keep retry outside the breaker, as the default order does, and retry only
  idempotent calls.
- Name instances after what the code actually creates: the annotation `name`,
  `create("id")`, or the Feign-generated id, which is not the client name.
- Publish breaker state: metrics such as `resilience4j.circuitbreaker.calls`,
  `.state` and `.failure.rate` are published automatically; add a registry
  such as `micrometer-registry-prometheus`.

## General pitfalls
- **No AspectJ, no protection.** The Boot module creates its
  `CircuitBreakerAspect` only when `org.aspectj.lang.ProceedingJoinPoint` is on
  the class path, and otherwise logs at DEBUG that aspects are inactive.
  Annotated methods then run unprotected with no error. Observed in practice:
  the weaver often arrives only transitively through another starter, so two
  services with identical resilience code differ in protection; gate AspectJ's
  presence in the dependency tree.
- **Boot 4:** an explicit `spring-boot-starter-aop` no longer resolves from the
  Boot BOM; it is `spring-boot-starter-aspectj` now.
- **The hidden 1 s cut.** Spring Cloud CircuitBreaker applies a time limiter to
  every execution unless it is disabled, with `TimeLimiterConfig.ofDefaults()`
  (1 s). A wrapped call (a Feign method, say) is cut at 1 s, often before the
  HTTP client's read timeout. Raise `resilience4j.timelimiter` for the instance
  or set `spring.cloud.circuitbreaker.resilience4j.disable-time-limiter=true`.
- **Health can take the instance down.** Health indicators are off by default
  because an OPEN breaker turns the application status DOWN. With
  `registerHealthIndicator` and `management.health.circuitbreakers.enabled=true`,
  one failing dependency can pull the whole instance out of a load balancer or
  orchestrator (an inference from the DOWN mapping).
- **Lost security context.** Spring Cloud CircuitBreaker runs the call on an
  executor; the security context follows only when the factory uses a
  `DelegatingSecurityContextExecutorService` (for example through
  `configureGroupExecutorService`).
- **Unmatched instance names.** Observed in practice: an `instances` entry
  whose name matches no created breaker is never used, and the code's breaker
  runs on defaults with no warning.
- **Servlet versus reactive.** The two Spring Cloud starters are different
  artifacts; a WebFlux gateway needs the reactor one. The `resilience4j.*`
  property layout is the same for both.
- **Declared but dormant.** The library on the class path protects nothing by
  itself; verify that a breaker is exercised on a real call path. Observed in
  practice: configuration often lives in served config (a config server), so a
  source-only search can wrongly conclude a breaker is unconfigured.
- **Retry on a breaker** amplifies load against a failing dependency when the
  order or the counts are not chosen deliberately.
- **Fallbacks mask outages.** A fallback degrades silently; without alerting on
  breaker state, a failing dependency reads as success (observed in practice:
  visible is not alerted).

## Testing
- Drive state through the `CircuitBreakerRegistry`: FORCED_OPEN and DISABLED
  exist for that control, and OPEN must yield `CallNotPermittedException` into
  the fallback.
- Assert the aspect is active: a context test that checks a
  `CircuitBreakerAspect` bean exists catches the dormant case (the bean is
  conditional on AspectJ; the test is observed in practice).
- Use a test profile with a small `slidingWindowSize` and
  `minimumNumberOfCalls`, so a few failures open the breaker.
- Breaker state is at `/actuator/circuitbreakers` and events at
  `/actuator/circuitbreakerevents` (latest 100 by default); both need explicit
  web exposure, since only `health` is exposed by default.

## Security defaults
- Resilience4j adds no authentication of its own; its actuator endpoints follow
  Boot's exposure rules. Security-context propagation across the Spring Cloud
  executor is opt-in (above). The library has no other security surface.

## Operational behaviour
- Without automatic transition, OPEN becomes HALF_OPEN only when a call
  arrives after `waitDurationInOpenState`; with it, a monitoring thread moves
  every breaker.
- RateLimiter splits time into cycles of `limitRefreshPeriod`, each with
  `limitForPeriod` permissions.
- Breaker state maps to health as CLOSED UP, OPEN DOWN, HALF_OPEN UNKNOWN.

## Interop
- OpenFeign (wrapping and fallbacks), Gateway (route filter with `forward:`
  fallback), Micrometer (metrics), Boot actuator (health and endpoints).
- Spring Retry is a different library; Boot 4 no longer manages its version.

## Major lines
### Resilience4j 1
- Java 8 with Vavr; Boot 2 through `resilience4j-spring-boot2`, with actuator
  and `spring-boot-starter-aop` expected at runtime.

### Resilience4j 2
- Java 17. `resilience4j-spring-boot2` and `-spring-boot3`, and
  `-spring-boot4` from the newest 2.x releases; same runtime expectations.
  Under Boot 4 the AOP starter is `spring-boot-starter-aspectj`, and Spring
  Cloud CircuitBreaker's Boot 4 line still builds on
  `resilience4j-spring-boot3`.

### Resilience4j 3
- Described on the main branch (Java 21, virtual-thread schedulers) but not
  released when this page was last checked; do not treat it as current.

## Upstream docs
- https://resilience4j.readme.io/docs/getting-started-3
- https://resilience4j.readme.io/docs/circuitbreaker
- https://github.com/resilience4j/resilience4j
- https://docs.spring.io/spring-cloud-circuitbreaker/reference/
