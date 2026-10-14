# spring-security — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The authentication and authorization framework for Spring applications. It
intercepts requests through a chain of servlet filters, establishes who the
caller is (AuthN), decides what they may do (AuthZ), and applies cross-cutting
protections (CSRF, CORS, security headers, session management). It also signs
users in through an external OpenID Connect or OAuth 2.0 provider. Reference:
https://docs.spring.io/spring-security/reference/.

- `org.springframework.boot:spring-boot-starter-security`: the Boot starter;
  needed in any Boot application that uses the framework.
- `org.springframework.security:spring-security-web`: the servlet filter chain
  and request matchers.
- `org.springframework.security:spring-security-config`: the `HttpSecurity`
  DSL and the `@Enable...` annotations.
- `org.springframework.security:spring-security-messaging`: needed to secure
  STOMP inbound channels.
- `org.springframework.security:spring-security-test`: needed for the test
  support (`@WithMockUser`, MockMvc post-processors).
- `org.springframework.boot:spring-boot-starter-oauth2-client`: the Boot
  starter for OAuth2 login and OIDC login; needed when users sign in through an
  external provider.
- `org.springframework.security:spring-security-oauth2-client`: the client
  side of OAuth 2.0 and OIDC login (registrations, the authorization request,
  token clients, ID-token validation); needed with the starter above or
  without Boot.
- `org.springframework.security:spring-security-oauth2-jose`: JWT decoding and
  signing on Nimbus (`NimbusJwtDecoder`, JWT client assertions); needed for
  OIDC login, and comes with the OAuth2 client starter.

The resource-server module, which validates bearer tokens declaratively, and
the authorization-server module are cited in later sections, not covered.

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
- **OAuth2 / OIDC login** (`spring-security-oauth2-client`). A provider is a
  `ClientRegistration`, from Boot properties under
  `spring.security.oauth2.client.registration.<id>` and `.provider.<id>` or
  built in code, enabled with `http.oauth2Login(...)`. The default callback is
  `{baseUrl}/login/oauth2/code/{registrationId}`, and it must be registered at
  the provider exactly. With `issuer-uri` the client reads the provider's
  discovery metadata, which also supplies `end_session_endpoint` for logout; a
  registration with explicit authorization, token and JWK-set URIs makes no
  discovery call. `ClientSettings.requireProofKey` decides PKCE for a
  confidential client (see Security defaults and Major lines).

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
- **The authorization request** is built by
  `DefaultOAuth2AuthorizationRequestResolver`. It adds `state`, a `nonce` when
  the registration has the `openid` scope, and the PKCE challenge when PKCE
  applies. `setAuthorizationRequestCustomizer(...)` adds parameters through
  `additionalParameters(...)` (`prompt`, `max_age`, `response_mode`); a
  wrapping `OAuth2AuthorizationRequestResolver` sees the `HttpServletRequest`
  and can apply a customizer to one path only, such as a re-authentication
  step.
- **ID-token validation.** `OidcIdTokenValidator` checks the required claims,
  `iss` against the registration's issuer, `aud` containing the client id, the
  `azp` rules, and `exp` and `iat` with a 60-second default clock skew; the
  login provider checks the `nonce`. Nothing else: tenant, authentication
  method (`amr`) or `auth_time` checks are the application's. Add them with a
  `JwtDecoderFactory<ClientRegistration>` bean whose decoder runs
  `JwtValidators.createDefaultWithValidators(new OidcIdTokenValidator(registration), extra...)`,
  with `OidcIdTokenDecoderFactory.createDefaultClaimTypeConverters()`, or with
  `OidcIdTokenDecoderFactory#setJwtValidatorFactory`. The reference says to
  cache one decoder per registration. A validator sees only the token, so a
  freshness check against the request that started the login belongs in the
  success handler.
- **Token clients.** The authorization-code exchange runs through an
  `OAuth2AccessTokenResponseClient`; declaring one as a bean replaces the
  default, and `setRestClient(...)` replaces its HTTP client. The JWK set is
  fetched by the ID-token decoder, and UserInfo by the user service (`OidcUserService`, which delegates to `DefaultOAuth2UserService`),
  each with its own client. Each hop is a separate place to set timeouts, TLS,
  redirects and a host allow-list.
- **Client authentication.** `client_secret_basic` (the default when the
  registration has a secret), `client_secret_post` and `none` work as they are.
  `private_key_jwt` and `client_secret_jwt` need
  `NimbusJwtClientAuthenticationParametersConverter` added to the token client
  (`addParametersConverter`) with a resolver for the signing JWK; the
  `RestClient`-based token clients otherwise throw `IllegalArgumentException`
  naming the converter hooks. The assertion carries `iss`, `sub`, `aud`,
  `jti`, `iat` and `exp`; `setJwtClientAssertionCustomizer` changes its
  headers or claims, such as a certificate thumbprint a provider requires.

## Idioms & best practices
- Prefer the resource-server / declarative JWT support over a hand-rolled filter
  unless you need custom token semantics; if custom, register the filter at a
  precise position rather than replacing the chain.
- **Revocation without giving up stateless validation.** When every service
  validates signed access tokens on its own, keep access tokens short-lived and
  put revocation on an opaque refresh token held in a registry in the issuer's
  existing database. A stolen access token then dies within minutes, and no
  service adds a per-request lookup or a shared cache. Make each refresh token
  single-use: every refresh returns a new one and invalidates the one
  presented, and the registry keeps the link between them. A presented token
  that was already rotated means two parties hold it; the issuer cannot tell
  which one is the thief, so it revokes the live token of that chain and the
  user signs in again. This is the refresh-token rotation of the OAuth 2.0
  Security Best Current Practice (RFC 9700), which requires rotation or
  sender-constrained refresh tokens for public clients. Cover the reuse case in
  an end-to-end test, beside logout and expiry. Calls that have no
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
- **Key a signed-in user by issuer and subject.** OpenID Connect Core says
  `sub` and `iss` together are the only ID-token claims a client can rely on
  as a stable identifier; email, preferred username and display name can
  change or be reassigned. Store the pair (or the provider's documented
  immutable id) and link local accounts through it, never through an email
  match. Provider-specific identity claims are on the provider's own page: for
  Microsoft Entra ID (its `oid` and `tid` identifiers, and the `amr` and
  `auth_time` claims a v2.0 ID token carries only when the app requests them),
  see [`msal4j`](./msal4j.md).
- **Response mode.** The client sends no `response_mode`, so the provider
  answers with the default for the code flow, a query-string redirect. A
  provider that recommends `form_post` can get it through the authorization
  request customizer: the callback filter reads `code` and `state` from the
  request parameters, whether in the query or a POSTed form.
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
- **Path-pattern matchers match the decoded path.** `PathPatternRequestMatcher`
  (from 6.5) matches the request path as Spring's `PathContainer` parses it,
  one percent-decoded segment at a time, so `/%64evices` matches a pattern for
  `/devices`, as MVC itself would route it. Define each protected route once,
  as a request matcher, and reuse that matcher wherever the route is checked
  (authorization rules, cross-site checks, error classification). Never add a
  second check on the raw `getRequestURI()`: it disagrees with the matcher on
  any encoded request and can be walked around by encoding one character
  (observed in practice; the decoding is upstream).
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
- **PKCE for a confidential client** is on by default from 7 (Major lines). A
  provider that does not support PKCE for confidential clients needs
  `ClientSettings.requireProofKey(false)` on that registration, which the
  reference documents; no Boot property maps it, so the registration is then
  built in code (observed in practice; Boot's property mapper sets the client
  authentication method and no PKCE setting).
- **The token endpoint's HTTP client depends on the class path.** The default
  token client is `RestClient`-based on 7, so a test class path that carries
  Apache HttpClient or Jetty's client (an HTTP stub server brings them) sends
  the token request through a library production does not use; see
  [`spring-framework`](./spring-framework.md). Set the client explicitly when
  the outbound policy (allow-list, TLS, redirects, timeouts) is what a test
  proves.
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
- **OIDC login.** The `oidcLogin()` and `oauth2Login()` MockMvc
  post-processors place a ready `OidcUser` or `OAuth2User` in the context; no
  grant flow, token exchange or signature check runs, so they test
  authorization on the signed-in user and nothing about login. To exercise the
  authorization request, the token exchange and the ID-token validators, run
  the code flow against a stub provider: a registration with explicit
  authorization, token and JWK-set URIs pointing at the stub, a JWK set the
  stub serves, and ID tokens signed with its key, carrying the `nonce` from the
  authorization redirect (observed in practice; the reference ships no such
  recipe). Keep that seam in test configuration only, and assert the refusals
  too: a wrong algorithm, `alg: none`, a wrong issuer or audience, and each
  claim check the application adds.

## Security defaults
- The default response headers: `Cache-Control: no-cache, no-store,
  max-age=0, must-revalidate`, `Pragma: no-cache`, `Expires: 0`,
  `X-Content-Type-Options: nosniff`, `Strict-Transport-Security` (on HTTPS),
  `X-Frame-Options: DENY`, `X-XSS-Protection: 0`.
- CSRF protection is on by default.
- `AuthorizationFilter` covers every dispatch type on 6 and later.
- Requests excluded with `ignoring()` get none of the above.
- OIDC login sends `state` and a `nonce` and checks both on the callback; from
  7 it also sends a PKCE `S256` challenge for confidential clients.
- Logout is local by default: it ends the application session and leaves the
  provider's session alive, so the next login may complete without a prompt.
  `OidcClientInitiatedLogoutSuccessHandler` adds RP-initiated logout at the
  provider's `end_session_endpoint`, read from the discovery metadata.

## Operational behaviour
- The chain runs on every request, so a slow `AuthenticationManager` or a remote
  token check is paid per request; the reference does not give numbers.
- Session and `SecurityContext` persistence follow the configured session
  policy; this page does not cover session management in depth.
- **The context survives onto the error page.** From 6.0 the default
  `SecurityContextRepository` is a `DelegatingSecurityContextRepository` over
  a request-attribute repository and the session repository. The
  request-attribute half keeps the `SecurityContext` across the dispatches of
  one request, so when a servlet container clears it before the ERROR
  dispatch, the error page still sees the signed-in `Authentication` and can
  render user-specific navigation (observed in practice on a 403 page). On 5
  the default was the session repository alone.
- **Where the OAuth2 client keeps state.** The pending authorization request
  lives in the HTTP session (`HttpSessionOAuth2AuthorizationRequestRepository`),
  so the callback must reach an instance that can read that session. Authorized
  clients default to `InMemoryOAuth2AuthorizedClientService`, held in the
  process memory and lost on restart.

## Interop
- [`spring-boot`](./spring-boot.md): actuator security and the back-off rule.
- [`spring-framework`](./spring-framework.md): MVC path matching, CORS support,
  filter registration, and the `RestClient` request factories the OAuth2 token
  client runs on.
- [`spring-websocket`](./spring-websocket.md): message-level authorization.
- [`jjwt`](./jjwt.md): a common library behind hand-rolled token filters.
- [`springdoc-openapi`](./springdoc-openapi.md): allow-list entries for the
  documentation paths.

## Major lines
### Spring Security 5
`WebSecurityConfigurerAdapter` was the configuration base until 5.7.0-M2
deprecated it in favour of a component-based `SecurityFilterChain` bean (which
works from 5.4) and the lambda DSL. `authorizeRequests`, `antMatchers`, `mvcMatchers` and
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
6.0 removes `WebSecurityConfigurerAdapter` and the `antMatchers` / `mvcMatchers` /
`regexMatchers` family in favour of `requestMatchers`. The default
`SecurityContextRepository` gains the request-attribute half (Operational
behaviour). `authorizeRequests` stays
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

OAuth2 client: `ClientSettings.requireProofKey` (present, default false, on
6.5) defaults to true for the authorization-code grant, so confidential
clients send a PKCE challenge too. `oauth2Login()` exchanges the code through
`RestClientAuthorizationCodeTokenResponseClient` where 6.5 used
`DefaultAuthorizationCodeTokenResponseClient`; the `RestClient`-based clients
accept `none`, `client_secret_basic` and `client_secret_post` without a
converter.

## Upstream docs
- https://spring.io/projects/spring-security
- https://docs.spring.io/spring-security/reference/
- https://docs.spring.io/spring-security/reference/servlet/architecture.html
- https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html
- https://docs.spring.io/spring-security/reference/features/exploits/csrf.html
- https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html
- https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html
- https://docs.spring.io/spring-security/reference/servlet/authentication/persistence.html
- https://docs.spring.io/spring-security/reference/servlet/oauth2/login/core.html and .../login/advanced.html
- https://docs.spring.io/spring-security/reference/servlet/oauth2/client/authorization-grants.html
- https://docs.spring.io/spring-security/reference/servlet/oauth2/client/client-authentication.html
- https://docs.spring.io/spring-security/reference/servlet/oauth2/login/logout.html
- https://docs.spring.io/spring-security/reference/servlet/test/mockmvc/oauth2.html
- https://openid.net/specs/openid-connect-core-1_0.html (§5.7, claim stability)
- https://www.rfc-editor.org/rfc/rfc9700 (§4.14, refresh-token protection)
- https://docs.spring.io/spring-security/reference/migration/index.html
- https://docs.spring.io/spring-security/reference/whats-new.html
- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-security
