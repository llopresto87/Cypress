# spring-cloud — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A family of microservice-platform primitives built on
[Spring Boot](./spring-boot.md): service discovery, an API gateway, centralized
configuration, declarative HTTP clients, and client-side load balancing. The
modules are versioned together as a
"release train" and aligned by importing one BOM,
`org.springframework.cloud:spring-cloud-dependencies`, into
`dependencyManagement`; individual capabilities are then added as member
starters (e.g. Netflix Eureka server/client, Spring Cloud Gateway, Config
server/client, OpenFeign, LoadBalancer).

## Core API / usage shape
- **Service discovery**: a discovery server (e.g. Eureka) that clients register
  with and query; a `DiscoveryClient` abstraction resolves logical service names
  to live instances.
- **API gateway**: routes declared (via config or a route-builder DSL) that
  match incoming requests and forward them, with filters for cross-cutting
  concerns. Routes to discovered services use `lb://<service-name>` URIs, which
  the discovery client plus load balancer resolve to a concrete instance.
- **Centralized config**: a config server serves externalized configuration from
  a backing store; config clients fetch it at startup so settings live outside
  each deployable.
- **Declarative HTTP clients**: an annotated Java interface describes a remote
  API and a proxy implementation is generated, integrated with discovery and
  load balancing so calls target logical service names — see
  [`spring-cloud-openfeign.md`](./spring-cloud-openfeign.md) for that client's
  own surface.
- **Client-side load balancing**: requests to a logical service name are spread
  across the instances discovery returns, without a separate load-balancer hop.

## Idioms & best practices
- Import the release-train BOM once rather than pinning each starter
  independently; this is how Spring Cloud keeps its many modules mutually
  compatible with a given Spring Boot line. Match the release train to the Boot
  line in use.
- Address other services by logical name (through discovery / `lb://` URIs)
  rather than hard-coded hosts and ports, so instances can move and scale.
- Keep environment-specific settings in the centralized config server so
  deployables stay identical across environments.
- Use declarative Feign interfaces for inter-service HTTP rather than
  hand-written client boilerplate.

## General pitfalls
- Mixing module versions from different release trains breaks the compatibility
  the BOM guarantees; let the single BOM govern every member's version.
- Discovery and config introduce startup-order and availability dependencies: a
  client that cannot reach the discovery or config server may fail to start or
  degrade; plan for the server being unavailable.
- Resolving a logical service name — a gateway `lb://` route or a declarative
  client addressed by service id — only works when the load balancer is on the
  classpath and the target is actually registered with discovery. A missing
  registration surfaces late, as a resolution failure at call time, rather than
  as a clear startup error.

## Upstream docs
- https://spring.io/projects/spring-cloud
- https://docs.spring.io/spring-cloud-release/reference/
- https://mvnrepository.com/artifact/org.springframework.cloud
