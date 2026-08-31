# spring-cloud-openfeign — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The declarative HTTP-client module of the Spring Cloud family. A remote API is
described as an annotated Java interface; a proxy implementation is generated at
runtime, so inter-service calls read like local method calls. It is the
concrete client layer that the broader platform integrates with discovery and
load balancing — see [`spring-cloud.md`](./spring-cloud.md) for the platform.
Canonical coordinates:
`org.springframework.cloud:spring-cloud-starter-openfeign`.

## Core API / usage shape
- **`@EnableFeignClients`**: placed on a configuration/application class to
  scan for and instantiate the client interfaces.
- **`@FeignClient(name = "<service-id>")`**: annotates an interface; the `name`
  is a logical service id resolved through service discovery + client-side load
  balancing to a live instance, rather than a hard-coded host. A `url` can be
  set to bypass discovery and target a fixed endpoint.
- **Method mapping**: interface methods carry the same request-mapping
  annotations as a controller; parameters bind to path variables, query params,
  headers, and request bodies.
- **`FallbackFactory` / fallback**: a fallback implementation supplies a
  degraded response when calls fail; the factory form additionally receives the
  causing exception.
- **Custom `ErrorDecoder`**: translates non-2xx responses into typed exceptions
  instead of a generic client error.
- **Circuit-breaker pairing**: a client method can be wrapped by a circuit
  breaker so repeated failures route to the fallback instead of hammering an
  unhealthy dependency — see [`resilience4j.md`](./resilience4j.md) for breaker
  behavior and fallback discipline.

## Idioms & best practices
- Reserve `url` for external or fixed endpoints; everything internal is
  addressed by logical service id, per [`spring-cloud.md`](./spring-cloud.md).
- Centralize error translation in an `ErrorDecoder` so callers see meaningful
  typed exceptions rather than parsing raw responses.
- Use a `FallbackFactory` (not a plain fallback) when the degraded path needs to
  inspect or log the underlying cause.
- Keep client interfaces thin and share request/response DTOs deliberately;
  avoid leaking transport concerns into the interface contract.

## General pitfalls
- `@EnableFeignClients` scanning scope matters: an interface outside the scanned
  packages is never proxied and injection fails at startup.
- Clients addressed by `name` inherit the late-failing discovery resolution
  described in [`spring-cloud.md`](./spring-cloud.md) — the interface is
  injectable even when nothing can resolve the service id.
- Feign's own contract differs subtly from Spring MVC annotations across lines;
  confirm which contract is active before assuming controller-identical binding.

## Upstream docs
- https://spring.io/projects/spring-cloud-openfeign
- https://docs.spring.io/spring-cloud-openfeign/reference/
- https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-openfeign
