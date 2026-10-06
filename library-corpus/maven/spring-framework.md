# spring-framework — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Spring Framework is the foundation under Spring Boot: the IoC container and the
programming and configuration model for enterprise Java. It integrates selected
Jakarta EE specifications (Servlet, WebSocket, JPA, Bean Validation) rather than
the whole platform. Its modules: the core container (`spring-core`,
`spring-beans`, `spring-context`, SpEL), AOP, `spring-tx`, data access,
`spring-web` with `spring-webmvc` (servlet) and `spring-webflux` (reactive),
`spring-websocket`, `spring-messaging`, and testing. Coordinates:
`org.springframework:spring-core`, `org.springframework:spring-beans`,
`org.springframework:spring-context`, `org.springframework:spring-web`,
`org.springframework:spring-webmvc`, `org.springframework:spring-webflux`,
`org.springframework:spring-tx`, `org.springframework:spring-test`; the BOM is
`org.springframework:spring-framework-bom`. A Spring Boot application gets it
through the starters, for example
`org.springframework.boot:spring-boot-starter-web` (Spring MVC) and
`org.springframework.boot:spring-boot-starter-webflux`. Reference:
https://docs.spring.io/spring-framework/reference/; source and wiki on GitHub.

Support is per generation and listed on the framework wiki's versions page:
each generation's last feature branch ends its open-source support some time
after the next generation ships, and commercial support runs separately. In a
Boot application the Boot BOM supplies the framework version; observed in
practice, pinning the framework separately from Boot only creates skew (the
docs list versions and do not prescribe this).

## Install, setup and configuration
- **Configuration styles.** Annotation-based (`@Autowired`, `@Inject`,
  `@PostConstruct`, `@PreDestroy`), Java-based (`@Configuration` classes with
  `@Bean` methods), and XML.
- **Profiles and environment.** `@Profile` makes a component eligible only when
  the profile is active; the `Environment` carries active profiles and
  properties.
- **Bean scopes.** `singleton` (the default, one instance per container),
  `prototype`, and the web scopes `request`, `session`, `application` and
  `websocket`.
- **Parameter names.** Name-based binding (`@PathVariable` and `@RequestParam`
  without an explicit name, constructor binding) needs classes compiled with
  `-parameters`; with Maven set `<parameters>true</parameters>` on the compiler
  plugin (the Boot parent does), with Kotlin `-java-parameters`. A Java agent can
  drop the parameter information at run time; the JDK fixed that in 19.
- **Path matching.** Spring MVC matches with `PathPattern`; the `AntPathMatcher`
  variant is deprecated. Customize through `WebMvcConfigurer.configurePathMatch`.

## Core API / usage shape
- **AOP is proxy-based.** Spring AOP uses a JDK dynamic proxy when the target
  implements an interface, otherwise a CGLIB subclass. Only calls that come in
  through the proxy are advised: a call from one method of the bean to another
  (self-invocation) bypasses the advice. AspectJ weaving (compile time or load
  time) has no such limit.
- **`@Transactional`.** In proxy mode, self-invocation starts no transaction even
  when the called method is annotated; the proxy must be fully initialized, so
  do not rely on it in `@PostConstruct`. Since 6, protected and
  package-visible methods are transactional on class-based proxies;
  interface-based proxies need public interface methods. Rollback by default
  happens on `RuntimeException` and `Error` only: a checked exception commits
  unless `rollbackFor` / `rollbackForClassName` says otherwise.
- **`@Async`, `@Scheduled` and the caching annotations** (`@Cacheable` and the
  rest) also default to proxy mode, so local calls inside the class are not
  intercepted; `aspectj` mode with weaving is the alternative.
- **HTTP clients.** `RestClient` is the synchronous fluent client (builder with
  base URL, default headers, interceptors, request factories, API versioning)
  and is thread-safe once built; `WebClient` is the reactive client; HTTP
  interface clients are annotated Java interfaces backed by generated proxies;
  `RestTemplate` is the older template-method client.
- **Filters, interceptors, advice.** A servlet `Filter` runs in the container
  before the `DispatcherServlet`. A `HandlerInterceptor` (`preHandle`,
  `postHandle`, `afterCompletion`) applies to handler-mapped requests; for
  `@ResponseBody` and `ResponseEntity` methods the response is committed before
  `postHandle`, so change the body with `ResponseBodyAdvice` instead.
  `@ControllerAdvice` / `@RestControllerAdvice` classes hold `@ExceptionHandler`
  methods that apply across controllers.
- **Async MVC.** Controllers can return `DeferredResult`, `Callable`,
  `WebAsyncTask`, streamed values (SSE) or reactive types.
- **Resources.** The `Resource` abstraction (`ClassPathResource`,
  `UrlResource`, `FileSystemResource`). `getFile()` works for a class-path
  resource on the file system, never for one inside an unexpanded jar; read
  with `getInputStream()` or through the URL.
- **Observability.** Server observations for Spring MVC come from
  `ServerHttpObservationFilter`; customize them with a
  `ServerRequestObservationConvention`, usually by extending
  `DefaultServerRequestObservationConvention`.
- **Null safety.** The codebase carries JSpecify nullness annotations.

## Idioms & best practices
- Constructor injection with `@Configuration` / `@Bean`; keep transactional,
  async and cached operations behind a bean boundary (call them through another
  bean) so the proxy applies.
- Use `RestClient` for new synchronous HTTP calls and `WebClient` for reactive
  or streaming work.
- Normalize trailing slashes with `UrlHandlerFilter` so authorization rules and
  request mappings see the same path.
- Map errors once, in `@RestControllerAdvice`, rather than per controller.

## General pitfalls
- **Self-invocation** bypasses `@Transactional`, `@Async`, `@Cacheable` and the
  other proxy-mode annotations.
- **Checked exceptions commit** by default.
- **A class-path resource inside a jar is not a file**: `Resource.getFile()`
  (and `ResourceUtils.getFile("classpath:...")`) fail inside a packaged
  application. Exploding the jar only hides the defect.
- **A `Filter` bean runs twice.** Spring Boot registers every `Filter` bean with
  the embedded container (mapped to `/*`); when the same filter is also added to
  a Spring Security chain it may run twice, in a different order, and a token
  filter "kept out of the security chain" still runs at the container level.
  Register a `FilterRegistrationBean` with `enabled` set to false so the
  security chain is the only registration (or do not make the filter a bean).
- **Trailing-slash matching is gone.** It was deprecated and turned off by
  default in 6 and removed in 7 (`trailingSlashMatch`,
  `matchOptionalTrailingSeparator`): `/x/` no longer matches a mapping for
  `/x`, and `setUseTrailingSlashMatch(true)` cannot restore it on 7. Map both
  paths on the handler, or use `UrlHandlerFilter` (added late in the 6 line) to
  redirect or rewrite. Audit clients and gateway routes that send trailing
  slashes.
- **Parameter names without `-parameters`** fail name-based binding from the
  later 6 releases on, where discovery from debug information was removed.

## Testing
- The TestContext framework is annotation-driven and independent of the test
  framework: JUnit Jupiter through `SpringExtension`, JUnit 4, and TestNG.
- `MockMvc` runs full Spring MVC request handling against mock requests and
  responses with no server; `MockMvcTester` adds an AssertJ API; `WebTestClient`
  can run against MockMvc.
- On 7, `SpringExtension` uses a test-method-scoped `ExtensionContext`, which
  can break custom `TestExecutionListener`s in `@Nested` hierarchies;
  `@SpringExtensionConfig` on the top-level class is the documented fix.

## Security defaults
- RPC-style remoting (HTTP Invoker, Hessian, JMS Invoker, JAX-WS) was removed in
  6, so that class of Java-deserialization endpoint no longer exists on 6 and
  later (the removal is upstream; the security reading is a plant inference).
- Trailing-slash matching was deprecated "for security reasons": URL-based
  authorization and handler mapping could disagree about a path.
  `UrlHandlerFilter` is the safer replacement.
- On 7, SpEL evaluation is capped at a default operation count (configurable
  through `SpelParserConfiguration` or `spring.expression.maxOperations`), and
  `SimpleEvaluationContext` no longer compiles expressions by default; both
  arrived in 7 maintenance releases.
- CORS credential rules (`allowCredentials` with wildcard origins) are on
  [`spring-security`](./spring-security.md).

## Operational behaviour
- Virtual threads (from the later 6 releases): `VirtualThreadTaskExecutor`, and
  a virtual-thread mode on `SimpleAsyncTaskExecutor` and
  `SimpleAsyncTaskScheduler`.
- AOT processing inspects the `ApplicationContext` at build time and applies
  decisions that would otherwise run at start-up; native images build on it.
- Most `ClientHttpRequestFactory` implementations no longer buffer request
  bodies (later 6 releases), so `Content-Length` is not set for some content
  types such as JSON.
- On 7, `spring-jcl` is replaced by Apache Commons Logging; transparent for most
  applications.
- Not covered here (no fetch): data access beyond transactions (`JdbcTemplate`,
  `spring-orm`), JMS messaging, WebFlux internals, validation internals and
  scheduler configuration.

## Interop
- **Spring Boot** supplies the version and auto-configuration. Boot 3 requires
  Framework 6 and Java 17; Boot 4 requires Framework 7. See
  [`spring-boot`](./spring-boot.md).
- **Micrometer.** From 6 `spring-web` depends on `micrometer-observation`, and
  `RestTemplate`, `WebClient` and MVC server handling are instrumented. Boot 3
  removed its old metrics classes (`WebMvcMetricsFilter` replaced by
  `ServerHttpObservationFilter`; the `*TagsProvider` / `*TagsContributor`
  types deprecated), so custom tags become an observation convention bean. See
  [`micrometer-tracing`](./micrometer-tracing.md).
- **Jackson.** 7 supports Jackson 3 (`tools.jackson`) first and falls back to
  Jackson 2; Jackson 2 support is deprecated, with auto-detection planned to be
  disabled in a later 7 release and then removed. See [`jackson`](./jackson.md).
- **Spring Security** relies on MVC path matching; the `HandlerMappingIntrospector`
  SPI and the MVC `PathMatcher` are deprecated on 7. See
  [`spring-security`](./spring-security.md).
- **WebSocket and STOMP** live in `spring-websocket` and `spring-messaging`; see
  [`spring-websocket`](./spring-websocket.md).

## Major lines
### Framework 5
The `javax.*` generation; the last 5 line runs on JDK 8 to 21. Open-source
support has ended. Trailing-slash matching is on by default.

### Framework 6
Java 17 and Jakarta EE 9 baseline (`javax.*` becomes `jakarta.*`). RPC-style
remoting, Joda-Time support, EJB access and the Ehcache package removed.
Trailing-slash matching deprecated and off by default. Micrometer Observation
instrumentation added. Later 6 releases removed debug-info parameter-name
discovery (compile with `-parameters`), added `RestClient`, virtual-thread
support and `UrlHandlerFilter`, stopped buffering request bodies in most request
factories, and deprecated `UriComponentsBuilder.fromHttpUrl` in favour of
`fromUriString`. The last 6 feature branch ends the generation.

### Framework 7
JDK 17 baseline with JDK 25 recommended; Jakarta EE 11 baseline (Servlet 6.1,
JPA 3.2, Bean Validation 3.1). Removed: `spring-jcl`, support for the
`javax.annotation` and `javax.inject` annotations (use `jakarta.annotation`
and `jakarta.inject`), Undertow support, `ListenableFuture`, OkHttp3 support,
and the path-mapping options `suffixPatternMatch`, `trailingSlashMatch` and
`favorPathExtension`. `HttpHeaders` is no longer a `MultiValueMap`.
`RestTemplate` is deprecated in favour of `RestClient` and slated for removal
(the 6 reference lists it with no deprecation). JSpecify nullness, API
versioning, and resilience support: `RetryTemplate` and `RetryPolicy` in
`spring-core` (`org.springframework.core.retry`), with `@Retryable` and
`@ConcurrencyLimit` in `spring-context`, both enabled by
`@EnableResilientMethods` on a `@Configuration` class. Jackson 3 first. `UriComponentsBuilder.fromHttpUrl` is absent
from the 7 javadoc; the removal was met in practice while migrating (the release notes
do not mention it).

## Upstream docs
- https://docs.spring.io/spring-framework/reference/
- https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-Versions
- https://github.com/spring-projects/spring-framework/wiki (release notes per generation and feature branch)
- https://docs.spring.io/spring-framework/reference/core/aop/proxying.html
- https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html
- https://docs.spring.io/spring-framework/reference/integration/rest-clients.html
- https://docs.spring.io/spring-framework/reference/web/webmvc/filters.html
- https://docs.spring.io/spring-framework/reference/testing/testcontext-framework.html
