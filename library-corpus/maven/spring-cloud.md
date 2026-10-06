# spring-cloud — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A family of microservice-platform projects built on
[Spring Boot](./spring-boot.md) and released together as a "release train":
service discovery, an API gateway, centralized configuration, declarative HTTP
clients and client-side load balancing. One BOM aligns them,
`org.springframework.cloud:spring-cloud-dependencies` (type `pom`, scope
`import` in `dependencyManagement`); capabilities are then added as member
starters with no version, for example
`org.springframework.cloud:spring-cloud-starter-config` (config client),
`org.springframework.cloud:spring-cloud-config-server` (config server) and
`org.springframework.cloud:spring-cloud-starter-loadbalancer`. Gateway,
Eureka, OpenFeign and the circuit breaker have their own pages:
[`spring-cloud-gateway.md`](./spring-cloud-gateway.md),
[`spring-cloud-netflix-eureka.md`](./spring-cloud-netflix-eureka.md),
[`spring-cloud-openfeign.md`](./spring-cloud-openfeign.md),
[`resilience4j.md`](./resilience4j.md). This page owns the train, Config and
the Commons layer (discovery abstraction, LoadBalancer, bootstrap, refresh).
Upstream home: https://spring.io/projects/spring-cloud, reference at
https://docs.spring.io/spring-cloud-release/reference/.

Trains use calendar versions `YYYY.MINOR.MICRO` from the 2020.0 train (earlier trains had
London-station names such as Hoxton) and also carry a codename (2021.0
Jubilee, 2022.0 Kilburn, 2023.0 Leyton, 2024.0 Moorgate, 2025.0 Northfields,
2025.1 Oakwood). Each member project has its own version line inside a train;
the pom names only the train. A train has no support timeline of its own: its
projects are supported while the newest Boot line it supports is, and lose
support within about three months after that Boot line ends.

## Install, setup and configuration
- **Train to Boot pairing** (the project page's table): 2025.1 with Boot 4;
  2025.0 with Boot 3.5; 2024.0 with 3.4; 2023.0 with 3.2 and 3.3; 2022.0 with
  3.0 and 3.1; 2021.0 with 2.6 and 2.7; 2020.0 with 2.4 and 2.5; Hoxton with
  2.2 and 2.3. Some rows support the newer Boot minor only from a named later
  service release of the train, so read the table, not just the row.
- **The BOM is BOM-only.** It manages Spring Cloud artifacts and nothing of
  Spring or Spring Boot. It declares a `spring-boot.version` property, but with
  a Boot parent the parent governs Boot.
- **Compatibility verifier.** At startup Spring Cloud checks the Boot version
  on the class path and fails with `APPLICATION FAILED TO START` when it is
  not compatible with the train. `spring.cloud.compatibility-verifier.enabled=false`
  turns it off; `...compatible-boot-versions` overrides the accepted list.
- **Config client.** `spring.config.import=optional:configserver:` connects to
  the default `http://localhost:8888`. Without `optional:`, a client that
  cannot connect fails to start. The URL goes in the import
  (`optional:configserver:http://host:8888`) or in `spring.cloud.config.uri`;
  the import wins. Config Data resolves twice, first with the `default`
  profile and then with the active ones, so served config can activate
  profiles.
- **Fail fast and retry.** `spring.cloud.config.fail-fast=true` (or leaving out
  `optional:`) halts startup on a connection failure. Retry needs fail-fast
  plus `spring-retry` and the AOP starter on the class path; the default is six
  attempts, 1000 ms initial backoff, multiplier 1.1
  (`spring.cloud.config.retry.*`). When the import sits in a profile-specific
  file, retry settings go as URL parameters on the import.
- **Discovery-first lookup.** `spring.cloud.config.discovery.enabled=true`
  (default false) finds the server through `DiscoveryClient`, at the cost of
  an extra round trip at startup.
- **Client credentials** go in the server URI or in
  `spring.cloud.config.username`/`password`.
- **Config Server.** `spring-cloud-config-server` plus `@EnableConfigServer`.
  It listens on 8080 like any Boot app; 8888 is the convention
  (`server.port=8888`). HTTP API: `/{application}/{profile}[/{label}]`,
  `/{application}-{profile}.yml`, `/{label}/{application}-{profile}.yml` and the
  `.properties` forms.
- **Git backend.** `spring.cloud.config.server.git.uri`; `search-paths` adds
  sub-directories (the top level is always searched), and placeholders work, so
  `search-paths: '{application}'` gives one folder per application. Credentials
  go in `username`/`password` properties, not the URL; SSH reads `~/.ssh` by
  default. `force-pull: true` recovers a dirty local clone. `cloneOnStart`
  checks a repository at startup.
- **`native` profile.** `spring.profiles.active=native` serves configuration
  from the file system or class path
  (`spring.cloud.config.server.native.searchLocations`; use the `file:` prefix).
- **Legacy bootstrap** (`bootstrap.yml`) is off by default from 2020.0;
  `spring.cloud.bootstrap.enabled=true` or `spring-cloud-starter-bootstrap`
  brings it back.

## Core API / usage shape
- **Service discovery:** a `DiscoveryClient` resolves logical service ids to
  instances (Eureka, Consul and Zookeeper implementations exist);
  `spring.cloud.discovery.enabled=false` turns discovery off. Without a
  registry-backed client, `SimpleDiscoveryClient` reads instances from
  `spring.cloud.discovery.client.simple.instances.<service>[n].uri`.
  Implementations register the local service by default;
  `spring.cloud.service-registry.auto-registration.enabled=false` stops that.
- **Load-balanced clients:** a `RestTemplate`, `RestClient.Builder` or
  `WebClient.Builder` bean marked `@LoadBalanced` resolves
  `http://<service-id>/...`. Auto-configuration does not create the
  `RestTemplate`; the application declares it.
- **Spring Cloud LoadBalancer:** a `ReactiveLoadBalancer` with Round-Robin
  (default) and Random implementations over a `ServiceInstanceListSupplier`
  (discovery-based by default). Per-service configuration through
  `@LoadBalancerClient(value = ..., configuration = ...)`.
- **API gateway and declarative clients:** routes and Feign clients address
  services by logical name (`lb://<service-id>`), resolved through discovery
  plus LoadBalancer; see their pages.
- **Refresh:** `@RefreshScope` beans are rebuilt on a configuration change, and
  `@ConfigurationProperties` beans are re-bound. Constructor-bound properties
  (records included) cannot be refreshed.
- **Encryption:** values prefixed `{cipher}` are decrypted by the server before
  it sends them; the server exposes `/encrypt` and `/decrypt`.

## Idioms & best practices
- Import the train BOM once and let it govern every member's version; pick the
  train from the Boot line, not the other way round.
- Read the compatibility table on the project page rather than the BOM's
  `spring-boot.version` property (observed in practice as the rule that avoids
  a mismatched pair).
- Address other services by logical name, the target's
  `spring.application.name` as registered. Observed in practice: a repository,
  image or container name does not resolve.
- Keep environment-specific settings in the config server so deployables stay
  identical across environments; one folder per application with
  `search-paths: '{application}'`.
- Store secrets as `{cipher}` values; keep the symmetric key out of files
  (`ENCRYPT_KEY` environment variable), and prefer an asymmetric RSA key from a
  keystore (`encrypt.keyStore.*`), which the docs call superior for security.
  `encrypt.key` cannot hold an asymmetric key; under legacy bootstrap it must
  be in `bootstrap.properties`.
- Use the LoadBalancer cache in production (Caffeine when on the class path);
  the non-cached supplier is for prototyping.

## General pitfalls
- **Config server without actuator leaks.** Without
  `spring-boot-starter-actuator` on the server, `/actuator/**` matches the
  config API `/{application}/{label}` and can serve configuration. Add the
  actuator, and give the health-check user no access to the config API.
- **Any client reads any application's config.** By default an authenticated
  client can ask for any `{application}`. Isolate secrets per service with a
  `SecurityFilterChain` rule matching `{application}` against the principal.
- **Undecryptable values vanish.** A value that cannot be decrypted is replaced
  by a key prefixed `invalid` with value `<n/a>`. Encrypted values in a
  `.properties` file must not be quoted.
- **A misconfigured git repository** is found only at the first client request
  unless `cloneOnStart` is set.
- **SSH key format for the git backend.** The git-backend reference states that
  JGit needs RSA private keys in PEM format (beginning
  `-----BEGIN RSA PRIVATE KEY-----`, made with `ssh-keygen -m PEM -t rsa`) and
  known_hosts entries in `ssh-rsa` form; a key in the OpenSSH format does not
  load. Observed in practice: an ed25519 key already on the host was refused,
  and the server could not clone. Check the key against the running release
  before rotating a credential the server needs at startup. Moving to a release
  on JGit's Apache MINA transport is a separate decision, and upstream does not
  state that it lifts the limit.
- **Ribbon, Hystrix and Zuul are gone** from 2020.0; LoadBalancer is the
  client-side balancer. Ribbon keys left in config bind to nothing (observed in
  practice).
- **Late instance changes.** LoadBalancer creates a child context per service id
  on the first request (`spring.cloud.loadbalancer.eager-load.clients` makes it
  eager), and the default instance cache has a 35 s TTL, so a new or removed
  instance is seen late.
- **Load-balanced retries are off** by default: for `RestTemplate` they turn on
  with Spring Retry on the class path; for the reactive client set
  `spring.cloud.loadbalancer.retry.enabled=true`.
- **Late resolution failures.** A logical name resolves only at request time,
  through LoadBalancer and a registered target. A missing load balancer or
  registration surfaces as a call-time failure, not a startup error.
- **Renamed keys and served config.** Observed in practice, more than once: a
  framework-major migration renames configuration keys (upstream confirms the
  renames, for example the OpenFeign and Gateway prefixes) while the config
  server keeps serving the old ones. The new binary ignores unknown keys and
  the dependency falls back to defaults with a green startup.
  `spring-boot-properties-migrator` reports deprecated keys at startup; gate
  migrations with startup connectivity checks.
- **Fleet drift.** Observed in practice: the compatibility promise is per build.
  Separately built repositories each import their own train, nothing compares
  them, and a fleet drifts. Upstream is silent on cross-repository drift.
- Discovery and config add startup-order dependencies: plan for the server
  being down (see `optional:` above and the Eureka page).

## Testing
- Replace discovery in tests with `SimpleDiscoveryClient` properties
  (`spring.cloud.discovery.client.simple.instances.<id>[0].uri=http://localhost:<port>`),
  or turn discovery off with `spring.cloud.discovery.enabled=false`.
- Keep the import `optional:` so a test context needs no running config server.
  To run with no config server at all (a test context, or a deployment whose
  server is gone), supply what the server used to serve: synthetic values in
  tests (never a real key), and in a deployment the committed per-service file
  through `spring.config.additional-location`, whose values override the
  default locations while environment variables still win over both. Where
  `application.yml` declares the import through a placeholder
  (`spring.config.import: ${SPRING_CONFIG_IMPORT:configserver:...}`), an empty
  `SPRING_CONFIG_IMPORT=` in the environment resolves it to nothing and
  removes the import (observed in practice). A literal import is not removed
  that way: Boot binds each file's `spring.config.import` from that file alone
  (Boot's source).
- Observed in practice: a property-binding test does not prove the context
  assembles. A missing bean resolved at assembly stops the service even when it
  is off the request path, so a framework-major migration needs both a binding
  gate and a `@SpringBootTest` context gate. Upstream is silent on this.
- The config client contributes a health indicator that tries to load
  configuration (cached); `management.health.config.enabled=false` turns it off.

## Security defaults
- The Config Server has no authentication of its own: add
  `spring-boot-starter-security` and set `spring.security.user.password` (the
  default random password is, in the docs' words, not useful in practice).
- Per-application isolation is not a default (see pitfalls). Always run the
  server with TLS in production, through `server.ssl.*` or a terminating proxy.
- The config client does not obtain OAuth2 tokens; a JWT-protected server
  needs the client to fetch and attach one.
- `/encrypt` and `/decrypt` assume they are secured and reachable only by
  authorized callers.
- Git credentials belong in properties, not the URI.
- With discovery-first lookup and HTTP Basic on the server, its credentials sit
  in the server's registration metadata (for Eureka,
  `eureka.instance.metadataMap`), readable from the registry: treat the
  registry as sensitive.

## Operational behaviour
- An unreachable config server stops startup unless the import is `optional:`;
  with `optional:` the app starts on local configuration (running with no
  server at all is under Testing). When the app starts without the
  server (an `optional:` import, or the legacy bootstrap context, which halts
  only with `fail-fast=true`), it fails later on a cascade of missing
  properties and a missing datasource (observed in practice), so read the
  first missing key as a symptom of the import.
- LoadBalancer: lazy per-service contexts, cached instance lists, an optional
  health-check supplier (recommended when a service has few instances and no
  registry-backed supplier), and zone preference from discovery metadata such
  as `eureka.instance.metadata-map.zone`.

## Interop
- **Boot:** the train is chosen per Boot generation, and the verifier enforces it.
- **Tracing:** Spring Cloud Sleuth left the train at 2022.0; its core moved to
  Micrometer Tracing. Moving off Sleuth is a coordinate change, not a version
  bump ([`sleuth-zipkin.md`](./sleuth-zipkin.md)).
- **Gateway and OpenFeign:** `lb://` routes and name-addressed clients need
  LoadBalancer on the class path.
- Spring Cloud Bus and Vault are separate projects that this page does not
  cover.

## Major lines
### 2020.0 (Boot 2.4/2.5)
- Ribbon, Hystrix and Zuul removed; bootstrap off by default;
  `spring.config.import` becomes the way to bind to Config Server.

### 2021.0 (Boot 2.6/2.7)
- The last Boot 2 train; its open-source support has ended.

### 2022.0 (Boot 3.0/3.1, Spring Framework 6)
- Sleuth removed from the train. `@EnableCircuitBreaker` and
  `@SpringCloudApplication` removed; `@EnableDiscoveryClient` no longer needed.
  `spring.config.use-legacy-processing=true` no longer enables bootstrap. The
  OpenFeign prefix moves from `feign` to `spring.cloud.openfeign`, and Eureka's
  `@EnableEurekaClient` is removed.

### 2023.0 and 2024.0
- The fetched release notes record no train-level breaking changes for these
  two trains.

### 2025.0 (Boot 3.5)
- Gateway modules, starters and property prefixes renamed; the old names are
  deprecated with a log warning ([`spring-cloud-gateway.md`](./spring-cloud-gateway.md)).

### 2025.1 (Boot 4, Spring Framework 7)
- Breaking changes for Jackson 3, JSpecify nullability, Framework 7 and Boot 4;
  `spring-cloud-starter-parent` removed. 2025.0 supports Boot 3.5 only, so a
  Boot 4 application needs 2025.1. Config-client retry still names
  `spring-retry` and the AOP starter, but on Boot 4 the AOP starter is
  `spring-boot-starter-aspectj` and Boot no longer manages `spring-retry`, so
  it needs an explicit version.

## Upstream docs
- https://spring.io/projects/spring-cloud
- https://docs.spring.io/spring-cloud-release/reference/
- https://docs.spring.io/spring-cloud-config/reference/
- https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/git-backend.html
- https://docs.spring.io/spring-cloud-commons/reference/
- https://github.com/spring-cloud/spring-cloud-release/wiki
