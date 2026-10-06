# spring-security — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The authentication and authorization framework for Spring applications. It
intercepts requests through a chain of servlet filters, establishes who the
caller is (AuthN), decides what they may do (AuthZ), and applies cross-cutting
protections (CSRF, CORS, security headers, session management). Canonical
coordinates: `org.springframework.boot:spring-boot-starter-security`; the core
artifacts are `org.springframework.security:spring-security-web` and
`org.springframework.security:spring-security-config`, with
`org.springframework.security:spring-security-messaging` for STOMP and
`org.springframework.security:spring-security-test` for tests.
Reference: https://docs.spring.io/spring-security/reference/.

## Install, setup and configuration
- Adding the Boot starter secures the application at once. With Spring Boot
  and no `SecurityFilterChain` bean of your own, Boot's defaults apply,
  including securing every actuator except `/health`; declaring your own chain
  makes Boot back off entirely (see [`spring-boot`](./spring-boot.md)).
- Configure with `SecurityFilterChain` beans built from `HttpSecurity` and the
  lambda DSL; method security with `@EnableMethodSecurity`.
- `spring.security.filter.dispatcher-types` (Boot) and
  `dispatcherTypeMatchers` (DSL) control which servlet dispatches the chain
  sees.

## Core API / usage shape
- **Filter chain**: a `SecurityFilterChain` bean is configured with an
  `HttpSecurity` builder; each request passes through an ordered set of filters
  ending in authorization checks. Multiple chains can be scoped by request
  matcher.
- **Several chains.** Each chain is scoped with `securityMatcher` (an
  `antMatcher` on 5) and ordered with `@Order`; `FilterChainProxy` invokes
  **only the first chain that matches**. A request that matches no chain's
  matcher gets no chain at all, so give the last chain a catch-all matcher.
- **Authorization rules**: declared fluently, public endpoints permitted, the
  rest authenticated, and role/authority constraints per matcher. Rules
  evaluate in declaration order and the first match wins, so `anyRequest()`
  goes last; prefer `anyRequest().denyAll()` when "anything not listed is
  merely authenticated" is not the intent.
- **`authorizeHttpRequests`** (built on `AuthorizationManager`) replaces
  `authorizeRequests` (`FilterSecurityInterceptor`). Its `AuthorizationFilter`
  is last in the chain by default and runs on every dispatch (REQUEST, FORWARD,
  ERROR, INCLUDE), so error pages and forwards need their own rule, for example
  `dispatcherTypeMatchers(DispatcherType.FORWARD, DispatcherType.ERROR).permitAll()`.
- **Password encoders**: a `PasswordEncoder` bean (bcrypt/argon2/PBKDF2, or a
  `DelegatingPasswordEncoder` that prefixes the algorithm id) hashes and
  verifies credentials; passwords are never compared in plaintext. Stored
  hashes then read `{id}encodedPassword`.
- **Method security**: enabling annotation-based security allows
  `@PreAuthorize` / `@PostAuthorize` / `@Secured` on service methods for
  authorization close to the business logic. `@EnableMethodSecurity`
  (`AuthorizationManager`-based, pre/post annotations on by default) replaces
  `@EnableGlobalMethodSecurity(prePostEnabled = true)`.
- **Custom token / JWT filters**: a bespoke `OncePerRequestFilter` is inserted
  into the chain (before the username/password filter) to read a bearer token,
  validate it, build an `Authentication`, and place it in the
  `SecurityContextHolder`. Resource-server support can also validate JWTs
  declaratively.
- **CORS**: configured via a `CorsConfigurationSource` bean and enabled on the
  chain so pre-flight and cross-origin requests are handled before AuthZ.
- **Neighbour modules.** `spring-security-messaging` secures STOMP inbound
  channels (see [`spring-websocket`](./spring-websocket.md));
  `spring-security-data` exposes security expressions to Spring Data queries.

## Idioms & best practices
- Prefer the resource-server / declarative JWT support over a hand-rolled filter
  unless you need custom token semantics; if custom, register the filter at a
  precise position rather than replacing the chain.
- **Revocation without giving up stateless validation.** When every service
  validates signed access tokens on its own, keep access tokens short-lived and
  put revocation on an opaque refresh token held in a registry in the issuer's
  existing database. A stolen access token then dies within minutes, and no
  service adds a per-request lookup or a shared cache. Calls that have no
  caller token (login and registration reaching other services) get a
  short-lived service token signed by the same issuer key, carrying one
  dedicated authority that endpoints admit explicitly. Never open the endpoint,
  and never rely on network position.
- Use a `DelegatingPasswordEncoder` so stored hashes carry their algorithm and
  can be upgraded over time without a flag day. A bare encoder stores hashes
  with no `{id}` prefix, so any later change of encoder becomes a data
  migration.
- Keep authorization intent explicit: combine coarse URL rules with method
  security for defense in depth rather than relying on one layer.
- Configure CORS inside Spring Security (not only at a separate web-MVC layer),
  or pre-flight requests can be blocked by the security filters first. The
  reason: a pre-flight request carries no cookies or credentials, so with
  security first it is rejected as unauthenticated. Use
  `http.cors(withDefaults())` with a `CorsConfigurationSource` bean.
- Prefer `permitAll()` over `WebSecurityCustomizer.ignoring()`: an ignored
  request bypasses the whole chain, including security headers and CORS.
- Strip a bearer prefix with an anchored, case-exact check
  (`startsWith("Bearer ")` then `substring`), never `replace("Bearer", "")`,
  which also edits token content and accepts malformed headers.
- Give any configuration flag that relaxes the chain a fail-closed default.
  Observed in practice: a flag that turns the whole chain into `permitAll`,
  left `true` in a default or production profile, is a classic self-inflicted
  exposure.

## General pitfalls
- A URL allow-list entry must match the **computed** request mapping — the
  concatenation of a controller's class-level path prefix and the method-level
  path — not the raw annotation pattern read in isolation. An allow-list that
  matches only the method path (or only the prefix) silently fails to permit the
  real, combined route, and the endpoint is unexpectedly secured (or exposed).
  Patterns are also written relative to the servlet context path: one that
  repeats the context path, or omits a gateway prefix, silently mismatches
  (observed in practice).
- Filter ordering matters: inserting a custom filter at the wrong position means
  the `SecurityContext` is empty when authorization runs, or a token is never
  read. Register relative to a known filter. A filter that is also a Spring bean
  is registered a second time by Boot at the container level; see
  [`spring-framework`](./spring-framework.md) for the fix.
- Disabling CSRF is appropriate for stateless token APIs but dangerous for
  cookie/session-based flows; the decision must follow the session model.
  Upstream recommends CSRF protection for any request a browser could send for
  a normal user, and disabling it only for a service used by non-browser
  clients. "Stateless" alone is not the test: protection is safe to drop only
  when the credential travels in something the browser does not attach on its
  own (an `Authorization: Bearer` header). A token in a cookie, or HTTP Basic,
  still needs CSRF protection.
- Matcher syntax (Ant vs path-pattern) and trailing-slash handling differ across
  lines and cause allow-lists to miss; verify matches against the actual
  dispatched path. On 5, `antMatchers("/admin")` and MVC matching can disagree
  (for example on `/admin/`), which allows a bypass; `mvcMatchers` follows
  MVC's own matching.
- **Renaming `antMatchers` to `requestMatchers` changes the matcher**
  (path-pattern semantics). Re-verify each allow-list string against the
  dispatched paths rather than renaming mechanically: a `**` glued to a segment
  (`/swagger-ui**`) parses differently or fails, since `**` is valid only as a
  whole trailing segment.
- **CORS wildcard with credentials.** `CorsConfiguration` refuses
  `allowCredentials(true)` with `allowedOrigins("*")`, but
  `setAllowedOriginPatterns("*")` with credentials passes that check and
  accepts credentialed requests from any origin. The validation rule is
  upstream; the pattern form was met in production. Upstream also warns
  that credentialed CORS "establishes a high level of trust" with the
  configured domains. Keep one CORS emitter per service: a legacy servlet
  filter or MVC mapping that also writes CORS headers produces duplicated or
  contradictory headers (`*` beside credentials), and it can also swallow
  filter-chain exceptions. Find every emitter before tuning one. Prove the
  result with a preflight from an unlisted origin, which must get no
  `Access-Control-Allow-Origin`. Make the production allow-list required
  configuration with no committed default, so the service does not start
  without it.
- **Login failures must look the same.** The stock DAO provider reports an
  unknown user as bad credentials (`hideUserNotFoundExceptions` is true by
  default). A hand-written login path that dereferences a missing user, or
  answers differently for one, turns "no such user" into a 500 beside the 401
  for a wrong password and tells a caller which accounts exist. Probe both
  cases and expect the same status and body.
- **Inherited method-security rules.** A `@PreAuthorize` or `@PostAuthorize`
  on a generic base class or interface method also governs an override that
  declares none, so an owner-only rule written for the base type can deny
  every role on a subclass. Check the hierarchy for inherited annotations, and
  redeclare the rule on the override.
- During a DSL migration, an extra `csrf().ignoringAntMatchers(...)` on a chain
  whose CSRF is already disabled does nothing; remove it rather than translate
  it (observed in practice).

## Testing
- `spring-security-test` adds `@WithMockUser` and related annotations for
  method and MVC tests, request post-processors for MockMvc, and
  `SecurityMockMvcConfigurers.springSecurity()` to apply the chain to a
  `MockMvc` built by hand.
- Test each allow-list against the real dispatched path with MockMvc, an
  anonymous request per public route and an authenticated one per protected
  route; the computed-mapping and matcher-semantics pitfalls above show up
  nowhere else.

## Security defaults
- The default response headers: `Cache-Control: no-cache, no-store,
  max-age=0, must-revalidate`, `Pragma: no-cache`, `Expires: 0`,
  `X-Content-Type-Options: nosniff`, `Strict-Transport-Security` (on HTTPS),
  `X-Frame-Options: DENY`, `X-XSS-Protection: 0`.
- CSRF protection is on by default.
- `AuthorizationFilter` covers every dispatch type on 6 and later.
- Requests excluded with `ignoring()` get none of the above.

## Operational behaviour
- The chain runs on every request, so a slow `AuthenticationManager` or a remote
  token check is paid per request; the reference does not give numbers.
- Session and `SecurityContext` persistence follow the configured session
  policy; this page does not cover session management in depth.

## Interop
- [`spring-boot`](./spring-boot.md): actuator security and the back-off rule.
- [`spring-framework`](./spring-framework.md): MVC path matching, CORS support,
  and filter registration.
- [`spring-websocket`](./spring-websocket.md): message-level authorization.
- [`jjwt`](./jjwt.md): a common library behind hand-rolled token filters.
- [`springdoc-openapi`](./springdoc-openapi.md): allow-list entries for the
  documentation paths.

## Major lines
### Spring Security 5
`WebSecurityConfigurerAdapter` was the configuration base until the late 5
line deprecated it in favour of a component-based `SecurityFilterChain` bean
and the lambda DSL. `authorizeRequests`, `antMatchers`, `mvcMatchers` and
`regexMatchers` are current; `authorizeHttpRequests` skips ERROR and ASYNC
dispatches by default. The last 5 line is upstream's documented bridge: it runs
on Boot 2 and carries the 6 deprecations, a compiling checkpoint before the
Boot major.

Exposing `authenticationManagerBean()` from a `WebSecurityConfigurerAdapter`
while no authentication is configured (no `UserDetailsService`, no provider)
makes the manager delegate to itself and fail with `StackOverflowError`
(upstream issues). Observed in practice: enabling
`@EnableGlobalMethodSecurity` on that class triggered it at start-up on a
resource server. Drop the unused `authenticationManagerBean()` where the
service issues no logins, put method security on a dedicated
`GlobalMethodSecurityConfiguration` that supplies its own manager, or remove
the annotation where nothing uses `@PreAuthorize`. Keep a context-start test:
unit tests never reach the failure.

### Spring Security 6
Removes `WebSecurityConfigurerAdapter` and the `antMatchers` / `mvcMatchers` /
`regexMatchers` family in favour of `requestMatchers`. `authorizeRequests` stays
but is deprecated for removal in 7; `authorizeHttpRequests` replaces it. Filter signatures move to
`jakarta.servlet.*`. Authorization applies to every dispatch type, which can
newly block error pages. `@EnableMethodSecurity` replaces
`@EnableGlobalMethodSecurity`. A move that skips 6 (from 5 straight to 7) pays
the same renames (observed in practice).

### Spring Security 7
Removes `authorizeRequests` in favour of `authorizeHttpRequests`. Jackson 3
replaces Jackson 2: configure a Jackson 3 `JsonMapper.Builder` with
`SecurityJacksonModules` in place of a Jackson 2 `ObjectMapper` with
`SecurityJackson2Modules`, and prefer its module detection over registering
single modules such as `CoreJacksonModule`, because it adds type information
and a `PolymorphicTypeValidator`. The Jackson 3 format is compatible with the
now deprecated Jackson 2 one, so instances serialized under Jackson 2 still
deserialize. `spring-security-oauth2-authorization-server` uses Jackson 3 by
default; staying on Jackson 2 means excluding `tools.jackson.core:jackson-databind`
and adding `com.fasterxml.jackson.core:jackson-databind`.

The legacy WebSocket message-security configurer
(`AbstractSecurityWebSocketMessageBrokerConfigurer`,
`MessageSecurityMetadataSourceRegistry`) is removed; use
`@EnableWebSocketSecurity` with an `AuthorizationManager<Message<?>>`.

## Upstream docs
- https://spring.io/projects/spring-security
- https://docs.spring.io/spring-security/reference/
- https://docs.spring.io/spring-security/reference/servlet/architecture.html
- https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html
- https://docs.spring.io/spring-security/reference/features/exploits/csrf.html
- https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html
- https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html
- https://docs.spring.io/spring-security/reference/migration/index.html
- https://docs.spring.io/spring-security/reference/whats-new.html
- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-security
