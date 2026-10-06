# spring-cloud-gateway — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Spring Cloud's API gateway: it routes requests to downstream APIs and adds
cross-cutting concerns (security, metrics, resilience) on the way. Routes match
requests with predicates and transform them with filters. It comes in two
flavours, a full Server (standalone or embedded) and Proxy Exchange (a
`ProxyExchange` parameter in annotation-based handlers), each with a WebFlux
(reactive, Netty) and a Web MVC (servlet) variant. Coordinates, version from
the Spring Cloud train BOM
([`spring-cloud.md`](./spring-cloud.md) owns the train):
- from train 2025.0: `org.springframework.cloud:spring-cloud-starter-gateway-server-webflux`
  and `org.springframework.cloud:spring-cloud-starter-gateway-server-webmvc`;
- earlier trains: `org.springframework.cloud:spring-cloud-starter-gateway`
  (reactive) and, from train 2023.0, `org.springframework.cloud:spring-cloud-starter-gateway-mvc`
  (servlet).

The gateway's own major differs from the train number: 3 on train 2021.0
(Boot 2), 4 on trains 2022.0 to 2025.0 (Boot 3), 5 on train 2025.1 (Boot 4).
Upstream home: https://docs.spring.io/spring-cloud-gateway/reference/, source
on GitHub `spring-cloud/spring-cloud-gateway`.

## Install, setup and configuration
- **WebFlux server** needs the Netty runtime: it does not run in a servlet
  container or as a WAR, and synchronous libraries and patterns (Spring Data
  and Spring Security, for example) may not apply. `spring.cloud.gateway.enabled=false`
  keeps the starter but turns the gateway off.
- **Web MVC server** runs on Spring WebMvc.fn under Tomcat or Jetty;
  `spring.cloud.gateway.server.webmvc.enabled=false` turns it off.
- **Property prefix:** `spring.cloud.gateway.server.webflux.*` on current
  trains (`routes`, `default-filters`, `discovery.locator.*`, `httpclient.*`,
  `filter.secure-headers.*`, `globalcors.*`, `trusted-proxies`,
  `loadbalancer.use404`, `metrics.enabled`), and
  `spring.cloud.gateway.server.webmvc.*` for MVC. The configuration-properties
  appendix is authoritative: several prose pages still show the older
  `spring.cloud.gateway.*` prefix in their examples.
- **Route definition:** `id`, `uri`, `predicates`, `filters`, and optional
  `order` and `metadata`. Predicates and filters take a shortcut form
  (`Cookie=mycookie,mycookievalue`) or an expanded `name` plus `args` form. A
  route URI without a port defaults to 80/443, and any path on a route URI is
  ignored.
- **Defaults:** `discovery.locator.enabled=false`; `httpclient.connect-timeout`
  30 s (milliseconds); `httpclient.response-timeout` (a Duration) has no
  listed default; `metrics.enabled=false`; `loadbalancer.use404=false`.
- **Per-route timeouts** go in route `metadata` (`response-timeout`,
  `connect-timeout`, in ms); a negative per-route `response-timeout` disables
  the global one for that route.
- **CORS:** `globalcors.cors-configurations` maps URL patterns to Spring
  `CorsConfiguration`; `globalcors.add-to-simple-url-handler-mapping=true`
  answers preflight requests no route matches; per-route CORS goes in route
  metadata `cors`.

## Core API / usage shape
- **Flow:** the handler mapping matches a request to a route, and a
  route-specific filter chain runs "pre" logic, the proxied request, then
  "post" logic.
- **Predicates** include After, Before, Between, Cookie, Header, Host, Method,
  Path, Query, ReadBody, RemoteAddr, Version and Weight; one route's predicates
  combine with `and`.
- **Filters** include AddRequestHeader, RewritePath, StripPrefix, PrefixPath,
  SetPath, Retry, RequestRateLimiter, CircuitBreaker, FallbackHeaders,
  DedupeResponseHeader, SecureHeaders, TokenRelay,
  ModifyRequestBody/ModifyResponseBody and RequestSize; `default-filters`
  apply to every route.
- **Java routes:** a `RouteLocator` bean built with `RouteLocatorBuilder`
  (`builder.routes().route(r -> r.path(...).filters(...).uri(...))`).
- **`lb://<service>`:** Spring Cloud LoadBalancer resolves the name at request
  time. No instance gives 503 (404 with `loadbalancer.use404=true`). The
  instance's `isSecure` decides the downstream scheme, so an HTTPS request can
  go downstream over HTTP.
- **Discovery locator:** with `discovery.locator.enabled=true` and a
  `DiscoveryClient`, the gateway creates one route per registered service:
  `lb://<service-id>`, predicate `Path=/serviceId/**`, and a `RewritePath`
  that strips the service id. It needs `spring-cloud-starter-loadbalancer`.
- **CircuitBreaker filter:** needs
  `spring-cloud-starter-circuitbreaker-reactor-resilience4j`; `fallbackUri`
  accepts only `forward:` URIs; the cause is in the
  `CIRCUITBREAKER_EXECUTION_EXCEPTION_ATTR` exchange attribute; it can trip on
  configured status codes.
- **RequestRateLimiter:** 429 by default; the default `KeyResolver` is
  `PrincipalNameKeyResolver`; a request with no key is denied by default
  (`deny-empty-key`, `empty-key-status-code`).
- **TokenRelay:** forwards an OAuth2 access token downstream, from a named
  `ClientRegistration` or the authenticated user.

## Idioms & best practices
- Keep routes as configuration data, versioned with the configuration
  (observed in practice; upstream offers YAML and the Java DSL without
  preferring one).
- On the WebFlux gateway use the reactive breaker starter; servlet resilience4j
  configuration does not apply there ([`resilience4j.md`](./resilience4j.md))
  (observed in practice; follows from the WebFlux-only runtime).
- Add `SecureHeaders` as a default filter.
- When the actuator endpoint is needed, set
  `management.endpoint.gateway.access=read-only`, as the docs recommend.
- Read the resolved gateway version from the dependency tree: the pom names
  only the train (observed in practice as the habit that avoids a wrong
  reference version).
- Set `response-timeout` explicitly, since no default is listed.

## General pitfalls
- **Train 2025.0 renames.** `spring-cloud-starter-gateway` became
  `spring-cloud-starter-gateway-server-webflux` (old name deprecated with a log
  warning) and `spring.cloud.gateway.*` became
  `spring.cloud.gateway.server.webflux.*` (MVC: `spring.cloud.gateway.mvc.*`
  to `spring.cloud.gateway.server.webmvc.*`). The properties class binds only
  the new prefix; the gateway's migration listener for old `routes` and
  `default-filters` keys runs only with `spring-boot-properties-migrator` on
  the class path. Observed in practice: without it the gateway starts healthy
  with zero routes, and only a route-binding test catches it.
- **Locator filters replace the defaults.** Setting
  `discovery.locator.filters` replaces the whole default list; without
  re-declaring `RewritePath` the service id is not stripped and the downstream
  answers 404.
- **The discovery locator exposes every registered service** by name, which is
  an exposure decision, not a convenience.
- **Forwarded-for spoofing.** `XForwardedRemoteAddressResolver::trustAll` takes
  the first `X-Forwarded-For` address and is spoofable; use `maxTrustedIndex`
  set to the number of trusted hops in front of the gateway (0 or less fails at
  startup).
- **Forwarded headers need `trusted-proxies`.** `Forwarded` and
  `X-Forwarded-*` are added downstream only when `trusted-proxies` holds a
  regular expression of trusted proxies; newer releases disable them by
  default. Set it when downstream services need those headers.
- **Two CORS layers, two allow-lists.** A request passes the gateway's
  `globalcors` and then each service's own CORS configuration, and an origin
  missing from either is refused with a bare 403 before any controller runs.
  A proxied same-origin call other than GET or HEAD carries `Origin` too
  ([`same-origin-web-edge`](../../skill-corpus/same-origin-web-edge.md), step
  7, holds the edge-side procedure), and behind a proxy Spring compares it
  with the scheme, host and port the server sees (unless forwarded headers are
  applied), not the browser's, so a same-origin POST can be processed as
  cross-origin. Keep the page's own origin in each layer's list, with scheme
  and port written exactly.
- **Not a servlet app.** On WebFlux, servlet-only libraries, filters and
  configuration do not apply.

## Testing
- Test routes end to end with `@SpringBootTest(webEnvironment = RANDOM_PORT)`
  and `WebTestClient` against a stub downstream.
- Assert route binding: inject `GatewayProperties` and check the number of
  routes and default filters (the gateway's own migration tests do this). A
  green startup does not prove routes bound.
- Inspect routes through `/actuator/gateway/routes` (read-only) outside
  production.
- Wiretap (`httpclient.wiretap`, `httpserver.wiretap`, `reactor.netty` at
  DEBUG/TRACE) logs headers and bodies; keep it to debugging.

## Security defaults
- The `/gateway` actuator endpoint is disabled by default on the 5 line;
  `management.endpoint.gateway.access` (`read-only` or `unrestricted`) plus
  web or JMX exposure turns it on. `unrestricted` can create, refresh and
  delete routes. On the 3 line the endpoint was enabled by default and needed
  only exposure.
- Forwarded headers stay off until `trusted-proxies` is set.
- `SecureHeaders` defaults: `X-Xss-Protection: 1 (mode=block)`,
  `Strict-Transport-Security (max-age=631138519)`, `X-Frame-Options: DENY`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, a default
  `Content-Security-Policy`, `X-Download-Options: noopen`,
  `X-Permitted-Cross-Domain-Policies: none`. `secure-headers.disable` (lower
  case full names) drops individual headers; `Permissions-Policy` is opt-in.
- RequestRateLimiter denies requests with no resolvable key by default.

## Operational behaviour
- An `lb://` route with no instance fails at request time (503, or 404 with
  `use404`); see [`spring-cloud.md`](./spring-cloud.md) for LoadBalancer
  caching and lazy contexts.
- Connect timeout defaults to 30 s; response timeout is unset unless
  configured.
- Gateway metrics are off by default (`metrics.enabled=false`).
- Troubleshooting loggers: `org.springframework.cloud.gateway`,
  `org.springframework.http.server.reactive`,
  `org.springframework.web.reactive`, `reactor.netty`.

## Interop
- **LoadBalancer and discovery:** resolve `lb://`; Eureka, Consul, Zookeeper
  or Kubernetes supply instances
  ([`spring-cloud-netflix-eureka.md`](./spring-cloud-netflix-eureka.md)).
- **Resilience4j** through Spring Cloud CircuitBreaker, reactive starter only
  on WebFlux.
- **Spring Security:** reactive configuration on WebFlux; TokenRelay uses the
  OAuth2 client.

## Major lines
### Gateway 3 (train 2021.0, Boot 2)
- Reactive only; starter `spring-cloud-starter-gateway`; prefix
  `spring.cloud.gateway.*`; `/gateway` actuator enabled by default;
  `spring.cloud.gateway.trusted-proxies` already documented.

### Gateway 4 (trains 2022.0 to 2025.0, Boot 3)
- Same starter and prefix on Boot 3 at first. Train 2023.0 adds the servlet
  Server MVC variant (`spring-cloud-starter-gateway-mvc`, prefix
  `spring.cloud.gateway.mvc.*`). Train 2025.0 brings the starter and prefix
  renames above, with the old names deprecated.

### Gateway 5 (train 2025.1, Boot 4, Spring Framework 7)
- Current reference; new names only; `/gateway` access disabled by default
  through `management.endpoint.gateway.access`.

The Web MVC server's own predicate and filter catalogue was not read in depth
for this page; check the MVC reference before relying on a filter there.

## Upstream docs
- https://docs.spring.io/spring-cloud-gateway/reference/
- https://docs.spring.io/spring-cloud-gateway/reference/appendix.html
- https://github.com/spring-cloud/spring-cloud-gateway
- https://github.com/spring-cloud/spring-cloud-release/wiki
