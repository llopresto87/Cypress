# spring-cloud-netflix-eureka — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Eureka is Netflix's service-discovery server and client. A Eureka server keeps
a registry of running instances (and can run as a highly available group of
peers that replicate registry state to each other); clients register
themselves and look peers up by application id. Spring Cloud Netflix wires it
into Spring Boot through two starters, versioned by the Spring Cloud train BOM
([`spring-cloud.md`](./spring-cloud.md) owns the train):
`org.springframework.cloud:spring-cloud-starter-netflix-eureka-client` and
`org.springframework.cloud:spring-cloud-starter-netflix-eureka-server`. The
client starter brings `com.netflix.eureka:eureka-client` and
`spring-cloud-starter-loadbalancer`. Since train 2020.0 Spring Cloud Netflix
carries Eureka only (Ribbon, Hystrix, Zuul, Archaius and Turbine are gone).
Its major is 3 on train 2021.0, 4 on trains 2022.0 to 2025.0, and 5 on train
2025.1. Upstream home: https://docs.spring.io/spring-cloud-netflix/reference/,
source on GitHub `spring-cloud/spring-cloud-netflix`, and the Netflix wiki for
Eureka itself.

## Install, setup and configuration
- **Client.** With the client starter on the class path the application
  registers itself and can query the registry. It is both an instance
  (`eureka.instance.*`) and a client (`eureka.client.*`). Locate the server
  with `eureka.client.serviceUrl.defaultZone: http://localhost:8761/eureka/`.
  `defaultZone` must be written in camel case: `serviceUrl` is a map, so
  Boot's relaxed binding does not apply.
- **Instance identity.** The service id and virtual host default to
  `${spring.application.name}`, the non-secure port to `${server.port}`, and the
  instance id to
  `${spring.cloud.client.hostname}:${spring.application.name}:${spring.application.instance_id:${server.port}}`
  (override with `eureka.instance.instanceId`).
- **Host or IP.** `eureka.instance.preferIpAddress=true` (default false)
  registers the IP instead of the hostname; when Java cannot work out the
  hostname, the IP is sent. `eureka.instance.hostname` is the only explicit way
  to set the hostname.
- **Turning it off:** `eureka.client.enabled=false`, or
  `spring.cloud.discovery.enabled=false`.
- **Lease and fetch defaults:** renewal every 30 s
  (`eureka.instance.lease-renewal-interval-in-seconds`), expiry after 90 s
  without renewal (`lease-expiration-duration-in-seconds`), registry fetch
  every 30 s (`eureka.client.registry-fetch-interval-seconds`), first
  instance-info replication after 40 s.
- **Server.** `@EnableEurekaServer` on a Boot application; the UI and HTTP API
  live under `/eureka/*`, and 8761 is the conventional port. Every server is
  also a client and wants at least one peer URL; a standalone server sets
  `eureka.client.registerWithEureka=false` and `fetchRegistry=false`. Peers
  that list each other in `defaultZone` synchronize registrations while
  connected.
- **Server defaults:** `eureka.server.enable-self-preservation=true`,
  `renewal-percent-threshold=0.85`, `expected-client-renewal-interval-seconds=30`,
  `response-cache-update-interval-ms=30000`, `use-read-only-response-cache=true`.
  Spring Cloud does not apply Netflix's start-up warm-up wait;
  `eureka.server.defaultOpenForTrafficCount=0` turns it on.

## Core API / usage shape
- Use the generic `org.springframework.cloud.client.discovery.DiscoveryClient`
  (`getInstances("STORES")`) or name-addressed clients (OpenFeign,
  `@LoadBalanced` clients, gateway `lb://` routes) rather than the native
  `com.netflix.discovery.EurekaClient`.
- No annotation is needed on a client: the starter on the class path is
  enough. `@EnableEurekaClient` was removed on train 2022.0, and
  `@EnableDiscoveryClient` is no longer required.
- Do not call the native `EurekaClient` from `@PostConstruct`, `@Scheduled` or
  anywhere the context may not have started: it initializes in a
  `SmartLifecycle` at phase 0.
- `eureka.instance.metadataMap` publishes key/value metadata to other clients.
  Spring Cloud gives some keys meaning, such as `zone` for LoadBalancer zone
  preference and Config Server credentials for discovery-first config.
- **Health.** By default Eureka uses only the heartbeat, so an instance is
  announced `UP` whatever its actuator health says.
  `eureka.client.healthcheck.enabled=true` propagates the application's health;
  set it in `application.yml`, because in `bootstrap.yml` it can register the
  instance as `UNKNOWN`.
- **Secure registration.** `eureka.instance.nonSecurePortEnabled=false` and
  `securePortEnabled=true` make `DiscoveryClient` hand out `https` URIs; the
  status and home page URLs need their own overrides.
- **Transport (5 line).** The native client talks to the server through
  `RestClient`, `WebClient` or Jersey; `RestClient` needs `spring-boot-restclient`,
  `WebClient` needs `spring-boot-webclient` plus
  `eureka.client.webclient.enabled=true`.

## Idioms & best practices
- Give every service a `spring.application.name`: it is the id that discovery,
  Feign and `lb://` routes use. Observed in practice: name clients and routes
  after it, never after a repository or image name.
- Advertise a host callers can resolve. Observed in practice: in containers,
  set `eureka.instance.hostname` (or `preferIpAddress`) so a registrant does not
  publish a name only it can resolve, and a non-JVM registrant using a Eureka
  client library must do the same.
- Keep the lease renewal interval at its default in production; the server's
  calculations assume it.
- Switch off a standalone server's own client behaviour (above).

## General pitfalls
- **`default-zone` silently does nothing.** Use `defaultZone`.
- **Registration is slow by design.** With a 30 s heartbeat, an instance is
  discoverable only once the instance, server and client caches agree, which
  can take three heartbeats.
- **Refresh unregisters.** A refresh of the Eureka client briefly unregisters
  it, so every instance of a service can vanish for a moment;
  `eureka.client.refresh.enable=false` avoids it. AOT and native images need
  refresh off (`spring.cloud.refresh.enabled=false`) and cannot use a random
  port; the Eureka server supports neither.
- **Self-preservation.** When more instances than the threshold miss renewals
  at once, the server stops evicting anything until renewals recover, so dead
  instances can stay listed.
- **Health is not propagated by default.** The properties appendix lists
  `true` as the default of `eureka.client.healthcheck.enabled`, but the
  auto-configuration activates only when the property is set, and the
  reference says health is not propagated by default. Trust the reference.
- **Transitive XML stack.** `eureka-client` declares
  `com.thoughtworks.xstream:xstream` at compile scope and
  `org.codehaus.jettison:jettison` at runtime scope, so both reach every
  application with the client starter. The client fetches the registry as
  JSON. Observed in practice: excluding both from the client starter is safe,
  gated by a dependency-tree check that they are absent and the client still
  resolves. The exclusion is for clients only. The server's default full-XML
  codec is built on XStream (upstream source), so the same exclusion in the
  server module stopped it at start-up with `ClassNotFoundException` (observed
  in practice); scope the exclusion and its tree gate to client modules.
- **Server down.** Running clients keep resolving from their cached registry. A
  client that starts while the server is down has no cache, so its
  name-addressed calls fail, into a fallback if one exists (observed in
  practice, under that condition).
- A Thymeleaf application can stop the server's FreeMarker templates loading;
  set `spring.freemarker.template-loader-path=classpath:/templates/` and
  `prefer-file-system-access=false`.

## Testing
- Turn Eureka off in tests that do not need discovery
  (`eureka.client.enabled=false` or `spring.cloud.discovery.enabled=false`) and
  supply instances through `SimpleDiscoveryClient` properties
  (`spring.cloud.discovery.client.simple.instances.<id>[0].uri`).
- Integration tests that must not register set
  `spring.cloud.service-registry.auto-registration.enabled=false`.
- Observed in practice: gate the transitive tree after a train bump or an
  exclusion (xstream and jettison absent, client still resolves).

## Security defaults
- The server has no authentication by default; add
  `spring-boot-starter-security`. Spring Security then requires a CSRF token on
  every request, which Eureka clients do not send, so ignore CSRF for
  `/eureka/**` only (current reference:
  `http.csrf().ignoringRequestMatchers("/eureka/**")` in a
  `SecurityFilterChain`), never everywhere.
- Client basic auth comes from credentials embedded in the `defaultZone` URL
  (`user:password@host`). Only the first set found is used; per-server
  credentials are not supported. Treat that URL as a secret.
- Mutual TLS for the client: `eureka.client.tls.enabled=true` plus key and
  trust stores (PKCS12 by default; the JVM trust store when none is given).
- Registry metadata is readable by every client: credentials placed there for
  discovery-first config are exposed to the registry's readers (an inference
  from the readable metadata; upstream does not state it).

## Operational behaviour
- Heartbeat every 30 s; the server drops an instance after 90 s without one;
  clients fetch deltas every 30 s and cache them; on shutdown the client sends
  a cancel that takes the instance out of traffic.
- The server keeps the registry in memory only, with no back-end store; heartbeats
  rebuild it.
- Client HTTP timeouts: all `RestClient` timeouts default to 3 minutes on the
  5 line (`eureka.client.restclient.timeout.*`, ms); on the 3 line the
  `RestTemplate` timeouts were infinite by default
  (`eureka.client.rest-template-timeout.*`).
- Server metrics (`eureka.server.instances` gauges) are off by default;
  `eureka.server.metrics.enabled=true`.
- Zones: `eureka.instance.metadataMap.zone` feeds LoadBalancer's zone
  preference; `eureka.client.preferSameZoneEureka=true` keeps a client on its
  zone's server.
- The server needs JAXB, which JDK 11 removed: add
  `org.glassfish.jaxb:jaxb-runtime`.

## Interop
- **LoadBalancer** resolves Eureka ids for Feign, `@LoadBalanced` clients and
  gateway `lb://` routes ([`spring-cloud-gateway.md`](./spring-cloud-gateway.md),
  [`spring-cloud-openfeign.md`](./spring-cloud-openfeign.md)).
- **Config Server** discovery-first lookup reads Eureka metadata
  ([`spring-cloud.md`](./spring-cloud.md)).
- **Non-JVM registrants** (a Python Eureka client library, say) follow the same
  advertised-host rules (observed in practice).

## Major lines
### Spring Cloud Netflix 3 (train 2021.0, Boot 2)
- `RestTemplate` transport by default (Jersey optional) with infinite timeouts;
  the security example uses `WebSecurityConfigurerAdapter` and
  `ignoringAntMatchers`; `@EnableEurekaClient` still exists.

### Spring Cloud Netflix 4 (trains 2022.0 to 2025.0, Boot 3)
- `@EnableEurekaClient` removed; `@EnableDiscoveryClient` no longer needed.

### Spring Cloud Netflix 5 (train 2025.1, Boot 4)
- `RestClient`, `WebClient` or Jersey transports through Boot 4's separate
  `spring-boot-restclient` and `spring-boot-webclient` modules; `RestClient`
  timeouts default to 3 minutes. The docs say the default client is planned
  to become `RestClient` in the next major.

## Upstream docs
- https://docs.spring.io/spring-cloud-netflix/reference/
- https://docs.spring.io/spring-cloud-netflix/reference/appendix.html
- https://github.com/spring-cloud/spring-cloud-netflix
- https://github.com/Netflix/eureka/wiki
