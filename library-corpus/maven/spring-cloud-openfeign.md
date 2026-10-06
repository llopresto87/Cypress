# spring-cloud-openfeign — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The declarative HTTP-client module of the Spring Cloud family. A remote API is
described as an annotated Java interface and Feign generates the
implementation at runtime, so inter-service calls read like local method
calls. Spring Cloud adds Spring MVC annotations, Spring Web's
`HttpMessageConverters`, and integration with discovery, Spring Cloud
LoadBalancer and Spring Cloud CircuitBreaker. Coordinates:
`org.springframework.cloud:spring-cloud-starter-openfeign`, versioned by the
train BOM ([`spring-cloud.md`](./spring-cloud.md) owns the train). The
OpenFeign major follows the train: 3 on 2021.0, 4 on 2022.0 to 2025.0, 5 on
2025.1. Upstream says the project is feature-complete: no reactive clients
will be added, and it suggests Spring's HTTP Service Clients (blocking and
reactive) for new work. Upstream home:
https://docs.spring.io/spring-cloud-openfeign/reference/, source on GitHub
`spring-cloud/spring-cloud-openfeign`.

## Install, setup and configuration
- `@EnableFeignClients` on the application (or a `@Configuration` class with
  `basePackages` or `clients`) scans for `@FeignClient` interfaces.
- `@FeignClient("stores")`: the value is a client name, used to create a
  LoadBalancer client for that service id; `url` sets an absolute URL instead.
  The bean name is the interface's fully qualified name (`qualifiers` adds an
  alias); `contextId` separates several clients with the same name.
- Each named client gets its own child context holding a `Decoder`, `Encoder`
  and `Contract`. `configuration = FooConfiguration.class` overrides beans on
  top of `FeignClientsConfiguration`; keep that class out of
  `@ComponentScan`, or it becomes the default for every client.
- **Default beans:** `ResponseEntityDecoder` around `SpringDecoder`,
  `SpringEncoder`, `Slf4jLogger`, `SpringMvcContract`, `FeignCircuitBreaker.Builder`
  and `Retryer.NEVER_RETRY`. With LoadBalancer on the class path the client is
  `FeignBlockingLoadBalancerClient`. `Logger.Level`, `ErrorDecoder`,
  `Request.Options`, `RequestInterceptor` and `QueryMapEncoder` beans are
  picked up from the context when defined.
- **Properties** (`spring.cloud.openfeign.client.config.<name>` or
  `.default`): `url`, `connectTimeout`, `readTimeout`, `loggerLevel`,
  `errorDecoder`, `retryer`, `defaultQueryParameters`,
  `defaultRequestHeaders`, `requestInterceptors`, `dismiss404`, `encoder`,
  `decoder`, `contract`, `capabilities`. When properties and a
  `@Configuration` bean both exist, properties win unless
  `spring.cloud.openfeign.client.default-to-properties=false`.
- **Timeouts:** Feign's own `Request.Options` defaults are 10 s connect and
  60 s read, following redirects.
- **Other defaults:** `circuitbreaker.enabled=false`,
  `circuitbreaker.alphanumeric-ids.enabled=true`, `client.refresh-enabled=false`,
  `oauth2.enabled=false`, `lazy-attributes-resolution=false`,
  `autoconfiguration.jackson.enabled=true`.
- **HTTP client:** Apache HttpClient 5 is used when on the class path
  (`httpclient.hc5.enabled=false` turns it off); pool defaults are 200
  connections, 50 per route, 900 s time to live. `httpclient.*` applies to
  all clients, `httpclient.hc5.*` to HC5, `httpclient.http2.*` to the JDK
  HTTP/2 client. The `Client` bean must be a singleton, or each client builds
  its own connection pool.

## Core API / usage shape
- **Method mapping:** interface methods carry Spring MVC annotations
  (`@GetMapping`, `@PathVariable`, `@RequestParam`, `@RequestBody`,
  `@RequestHeader`); `@SpringQueryMap` binds a POJO or map as query
  parameters.
- **Fallbacks:** `fallback = Impl.class` (a bean) supplies a degraded
  response; `fallbackFactory = Factory.class` also receives the cause.
- **Error translation:** a custom `ErrorDecoder` turns non-2xx responses into
  typed exceptions.
- **Circuit breaker:** with Spring Cloud CircuitBreaker on the class path and
  `spring.cloud.openfeign.circuitbreaker.enabled=true`, every client method is
  wrapped. Breaker names follow `<feignClientClassName>#<calledMethod>(<parameterTypes>)`
  (`FooClient#bar()`); with `alphanumeric-ids` on (the default) only the
  alphanumeric characters stay (`DemoClientgetDemo`), so the id can be a
  property key. A prototype-scoped plain `Feign.Builder` turns breakers off
  for one client; a `CircuitBreakerNameResolver` bean changes the naming. See
  [`resilience4j.md`](./resilience4j.md) for breaker behaviour.
- **Headers and auth:** `RequestInterceptor` beans (for example
  `BasicAuthRequestInterceptor`) add headers to every request of a client.
  With `spring-boot-starter-oauth2-client` and
  `spring.cloud.openfeign.oauth2.enabled=true`, an `OAuth2AccessTokenInterceptor`
  obtains a token through `OAuth2AuthorizedClientManager` before each request
  (registration from `oauth2.clientRegistrationId`, or the service id).
- **Logging:** the logger is named after the interface and logs only at
  `DEBUG`. `Logger.Level` is `NONE` (default), `BASIC`, `HEADERS` or `FULL`
  (headers, bodies and metadata).
- **Compression:** `spring.cloud.openfeign.compression.request.enabled` and
  `.response.enabled`.
- **Spring Data:** with Jackson and Spring Data present, `Page` and `Sort`
  converters are registered.

## Idioms & best practices
- Reserve `url` for external or fixed endpoints; address internal services by
  client name through discovery.
- Set connect and read timeouts explicitly, per client or under `default`;
  Feign's 10 s / 60 s defaults rarely suit an internal call.
- Centralize error translation in an `ErrorDecoder` so callers see typed
  exceptions.
- Use `fallbackFactory` when the degraded path must see the cause.
- Use the alphanumeric breaker ids as `resilience4j.circuitbreaker.instances.<id>`
  keys.
- Keep client interfaces thin and share DTOs deliberately; read
  `@FeignClient(name = ...)` (or `url`) to learn the target, since the
  interface name says nothing about it.

## General pitfalls
- **No retries.** The default `Retryer` is `NEVER_RETRY`, unlike plain Feign,
  which retries `IOException`s whatever the HTTP method. Add a retryer only for
  idempotent calls.
- **LoadBalancer is optional.** Name-addressed clients need
  `spring-cloud-starter-loadbalancer`, which the OpenFeign starter marks
  optional, so declare it. Without discovery the interface is still injectable
  and fails only at call time ([`spring-cloud.md`](./spring-cloud.md)).
- **Scanning scope.** An interface outside the scanned packages is never
  proxied, and injection fails at startup.
- **Every client bean is `@Primary`** (to win over fallback beans of the same
  type); set `primary = false` when that clashes with another bean.
- **`FULL` logging** writes headers and bodies, `Authorization` included; never
  in production.
- **Early use.** Calling Feign clients during bean initialization or
  configuration processing is not supported.
- **Contract limits.** `@FeignClient` interfaces should not be shared between
  server and client, and a class-level `@RequestMapping` on a client interface
  is no longer supported. `SpringMvcContract` is the default and can be
  replaced, so confirm which contract is active.
- **No `@RefreshScope` on clients;** use `client.refresh-enabled=true` (not
  compatible with AOT or native images).
- **Header propagation is not automatic.** A bearer token reaches a downstream
  service only through a `RequestInterceptor` (the OAuth2 support is one).
  Observed in practice: forwarding the end user's token makes downstream calls
  run with the user's authority, with no service identity unless one is built
  (for example client credentials through the OAuth2 support).
- **Fallbacks that lie.** Observed in practice (measured): a fallback that
  returns a plausible default (false, an empty list) or throws the wrong
  exception is a correctness bug, not degradation. Read each fallback's
  behaviour.
- **Mapper mismatch across services.** The encoder and decoder use the
  application's message converters, so its JSON mapper. Observed in practice:
  a caller and a callee configured differently (one on Jackson 3, Boot 4's
  preferred library, one on Jackson 2) disagreed on property names and failed
  cross-service POSTs with `HttpMessageNotReadableException` (400). Pin mapper
  behaviour uniformly across every Feign participant; Boot 4 offers
  `spring.jackson.use-jackson2-defaults=true` to align with Jackson 2
  defaults. A partial pin is worse than none.

## Testing
- Point a client at a stub with `url` (the reference's own examples use
  `url = "http://localhost:${server.port}/"`), or supply instances through
  `SimpleDiscoveryClient` properties so name-addressed clients resolve without
  a registry.
- With Spring Cloud Contract, set
  `spring.cloud.openfeign.lazy-attributes-resolution=true`.
- Observed in practice: test fallbacks by making the stub fail and asserting
  the fallback's actual return value or exception, and catch mapper drift with
  an integration test that posts a real payload between two services'
  converters.

## Security defaults
- No authentication header is added by default; interceptors or the opt-in
  OAuth2 support add one.
- The default log level `NONE` exposes nothing; `HEADERS` and `FULL` expose
  headers, tokens included.
- `httpclient.disable-ssl-validation` exists; keep it off.

## Operational behaviour
- Calls run on a blocking client; there is no reactive support.
- With breakers on, every method is wrapped and the Spring Cloud CircuitBreaker
  time limiter applies (1 s by default; see
  [`resilience4j.md`](./resilience4j.md)), often well before the read timeout.
- With `feign-micrometer` on the class path and an `ObservationRegistry`, a
  Micrometer observation capability is added
  (`spring.cloud.openfeign.micrometer.enabled`).

## Interop
- Feign itself, which the page's module wraps: `io.github.openfeign:feign-core`
  and its sibling `feign-*` modules.
- LoadBalancer and discovery for name resolution
  ([`spring-cloud-netflix-eureka.md`](./spring-cloud-netflix-eureka.md)),
  Spring Cloud CircuitBreaker with Resilience4j, the Spring Security OAuth2
  client for tokens, Spring Data `Page`/`Sort`. The upstream replacement path
  is Spring's HTTP Service Clients.

## Major lines
### OpenFeign 3 (train 2021.0, Boot 2)
- Prefix `feign.*` (`feign.client.config.<name>`, `feign.circuitbreaker.enabled`);
  OkHttp, Apache HttpClient 4 and HC5 selected with `feign.okhttp.enabled`,
  `feign.httpclient.enabled`, `feign.httpclient.hc5.enabled`. `NEVER_RETRY` is
  already the default.

### OpenFeign 4 (trains 2022.0 to 2025.0, Boot 3)
- The prefix moves from `feign` to `spring.cloud.openfeign`, so old keys bind
  to nothing (follows from the prefix change; upstream states no compatibility
  shim); `...metrics` becomes `...micrometer`. Apache HttpClient 4
  support removed (HC5 recommended); `decode404` renamed `dismiss404`; OAuth2
  support moves to the Spring Security OAuth2 client;
  `autoconfiguration.jackson.enabled` defaults to true; `@FeignClient`
  attributes resolve eagerly; alphanumeric breaker ids become the default.

### OpenFeign 5 (train 2025.1, Boot 4)
- HC5 and the JDK HTTP/2 client are the documented clients; the project is
  feature-complete. Boot 4 prefers Jackson 3, which changes the converters the
  encoder and decoder use.

## Upstream docs
- https://docs.spring.io/spring-cloud-openfeign/reference/
- https://docs.spring.io/spring-cloud-openfeign/reference/appendix.html
- https://github.com/OpenFeign/feign
- https://github.com/spring-cloud/spring-cloud-release/wiki
