# spring-security — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The authentication and authorization framework for Spring applications. It
intercepts requests through a chain of servlet filters, establishes who the
caller is (AuthN), decides what they may do (AuthZ), and applies cross-cutting
protections (CSRF, CORS, security headers, session management). Canonical
coordinates: `org.springframework.boot:spring-boot-starter-security`.

## Core API / usage shape
- **Filter chain**: a `SecurityFilterChain` bean is configured with an
  `HttpSecurity` builder; each request passes through an ordered set of filters
  ending in authorization checks. Multiple chains can be scoped by request
  matcher.
- **Authorization rules**: declared fluently — public endpoints permitted, the
  rest authenticated, and role/authority constraints per matcher.
- **Password encoders**: a `PasswordEncoder` bean (bcrypt/argon2/PBKDF2, or a
  `DelegatingPasswordEncoder` that prefixes the algorithm id) hashes and
  verifies credentials; passwords are never compared in plaintext.
- **Method security**: enabling annotation-based security allows
  `@PreAuthorize` / `@PostAuthorize` / `@Secured` on service methods for
  authorization close to the business logic.
- **Custom token / JWT filters**: a bespoke `OncePerRequestFilter` is inserted
  into the chain (before the username/password filter) to read a bearer token,
  validate it, build an `Authentication`, and place it in the
  `SecurityContextHolder`. Resource-server support can also validate JWTs
  declaratively.
- **CORS**: configured via a `CorsConfigurationSource` bean and enabled on the
  chain so pre-flight and cross-origin requests are handled before AuthZ.

## Idioms & best practices
- Prefer the resource-server / declarative JWT support over a hand-rolled filter
  unless you need custom token semantics; if custom, register the filter at a
  precise position rather than replacing the chain.
- Use a `DelegatingPasswordEncoder` so stored hashes carry their algorithm and
  can be upgraded over time without a flag day.
- Keep authorization intent explicit: combine coarse URL rules with method
  security for defense in depth rather than relying on one layer.
- Configure CORS inside Spring Security (not only at a separate web-MVC layer),
  or pre-flight requests can be blocked by the security filters first.

## General pitfalls
- A URL allow-list entry must match the **computed** request mapping — the
  concatenation of a controller's class-level path prefix and the method-level
  path — not the raw annotation pattern read in isolation. An allow-list that
  matches only the method path (or only the prefix) silently fails to permit the
  real, combined route, and the endpoint is unexpectedly secured (or exposed).
- Filter ordering matters: inserting a custom filter at the wrong position means
  the `SecurityContext` is empty when authorization runs, or a token is never
  read. Register relative to a known filter.
- Disabling CSRF is appropriate for stateless token APIs but dangerous for
  cookie/session-based flows; the decision must follow the session model.
- Matcher syntax (Ant vs path-pattern) and trailing-slash handling differ across
  lines and cause allow-lists to miss; verify matches against the actual
  dispatched path.

## Upstream docs
- https://spring.io/projects/spring-security
- https://docs.spring.io/spring-security/reference/
- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-security
