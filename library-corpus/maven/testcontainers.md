# testcontainers — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Testcontainers for Java starts throwaway Docker containers from tests, so
integration tests run against real databases, brokers and images instead of
in-memory stand-ins. Core artifact: `org.testcontainers:testcontainers`; JUnit 5
support: `org.testcontainers:testcontainers-junit-jupiter` (on the 1 line
`org.testcontainers:junit-jupiter`); database and service modules such as
`org.testcontainers:testcontainers-mysql` and
`org.testcontainers:testcontainers-postgresql` (on the 1 line
`org.testcontainers:mysql`, `org.testcontainers:postgresql`); versions from
`org.testcontainers:testcontainers-bom`. Spring Boot's BOM manages the family,
and `org.springframework.boot:spring-boot-testcontainers` adds Boot's
integration. Home: https://java.testcontainers.org. The .NET sibling is
[`Testcontainers.PostgreSql`](../nuget/Testcontainers.PostgreSql.md); the
concepts (a reaper container, disposable containers, mapped ports) carry over.

## Install, setup and configuration
- Import `testcontainers-bom` (or rely on Boot's BOM) and declare modules
  without versions, in `test` scope.
- It needs a Docker-API-compatible runtime: Docker locally, Testcontainers
  Cloud, or another compatible runtime.
- **Configuration sources**, in order: environment variables,
  `~/.testcontainers.properties`, then `testcontainers.properties` on the class
  path. Main environment variables: `DOCKER_HOST` (the Docker endpoint, such as
  `unix:///var/run/docker.sock`), `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE` (the
  socket path that Ryuk, Docker Compose and similar helper containers mount),
  `TESTCONTAINERS_HOST_OVERRIDE` (the host on which mapped ports are reachable),
  `TESTCONTAINERS_RYUK_DISABLED`.
- **Ryuk**, the resource reaper container, removes containers after the run and
  at JVM shutdown. Some environments need it privileged
  (`ryuk.container.privileged = true`). Where privileged containers are not
  allowed, `TESTCONTAINERS_RYUK_DISABLED=true` turns it off; cleanup then
  happens only at a normal JVM shutdown, so a `kill -9` leaks containers.
- **Image mirrors.** `TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX` (or
  `hub.image.name.prefix` in a properties file) prefixes every Docker Hub image
  with a registry mirror; an `ImageNameSubstitutor` gives full control.

## Core API / usage shape
- `new GenericContainer<>(DockerImageName.parse("image:tag")).withExposedPorts(port)`,
  or a module class (`MySQLContainer`, `PostgreSQLContainer`,
  `MongoDBContainer`, ...) with typed accessors such as `getJdbcUrl()`.
- `start()` and `stop()`, or `try`-with-resources; `getHost()` and
  `getMappedPort(port)` give the address to use. The exposed port is the
  container's view: on the host Testcontainers maps it to a **random** free
  port, by design, so always ask for the mapped port at run time.
- **Readiness.** By default a container counts as started when its exposed port
  listens, with a 60-second timeout; `withStartupTimeout(...)` changes the
  timeout and `waitingFor(...)` takes other wait strategies (an HTTP endpoint,
  a log message, a health check).
- **JUnit 5:** `@Testcontainers` on the class and `@Container` on fields.
  Static fields are shared by all test methods of the class (started once,
  stopped after the last); instance fields restart for every test method. The
  extension is tested only with sequential execution; parallel use is
  unsupported.
- **Singleton containers:** start a container in a static initializer of an
  abstract base class; every subclass reuses it, and Ryuk stops it at the end
  of the suite.
- **JDBC URL shortcut:** `jdbc:tc:<module>:<tag>:///<database>` starts the
  container on first connection with no code.
- **Spring Boot:** the `@ServiceConnection` and `@DynamicPropertySource` wiring
  is on [`spring-boot`](./spring-boot.md), under Testing.

## Idioms & best practices
- Use the **image tags production runs**. A test against a different major
  passes without testing the real target (observed in practice).
- When the point of a test is that the served configuration reaches the store,
  inject the container's coordinates as ordinary `spring.*` properties rather
  than through a shortcut that bypasses the configuration (observed in
  practice).
- Share expensive containers per class (static fields) or per suite
  (singleton pattern); restart per method only when tests mutate state that
  cannot be reset.
- On a host where Docker **must** exist (a CI gate), fail the test when Docker
  is unreachable instead of skipping it: an assumption turns "Docker
  unreachable for any reason" into *skipped*, which reads as green (observed in
  practice).
- Name integration tests `*IT` and bind Failsafe, or they never run (see
  [`maven`](../cli/maven.md)).

## General pitfalls
- **Engine API floor** (observed in practice and in upstream issues). Docker
  Engines keep raising the minimum API version they serve. Older Testcontainers
  lines ship a client that falls back to an old API version when it cannot
  negotiate; a newer engine rejects it, Testcontainers reports "Could not find a
  valid Docker environment", and every Docker-guarded test skips although
  Docker is running. The durable fix is a Testcontainers line whose client
  negotiates (upstream raised the default API version within the 2 line). The
  stop-gap is a `docker-java.properties` with `api.version=` on the test class
  path. Pinning an older engine works but downgrades the build host.
- **Fixed host ports.** Hard-coding a host port defeats the random mapping and
  collides with local services and parallel runs.
- **Reusable containers** (`withReuse(true)` plus an opt-in per environment) are
  experimental: they stay running after the tests, and upstream says they are
  not suited for CI.

## Testing
This page is itself about testing; the patterns are in the sections above. For
tests that run inside a build container, see Operational behaviour.

## Security defaults
- Testcontainers drives the Docker daemon, and access to its socket is
  root-equivalent on the host (see [`docker`](../container/docker.md) and
  [`docker-host-hardening`](../container/docker-host-hardening.md)); mounting
  the socket into a build container hands that container the host.
- Ryuk may need privileged mode; disabling it trades that for leaked containers.
- Pull through a trusted mirror with the image-name prefix rather than from
  arbitrary registries.

## Operational behaviour
- **Running tests inside a container (Docker outside of Docker).** Mount the
  host socket (`-v /var/run/docker.sock:/var/run/docker.sock`), and mount the
  source directory **at the same path** inside the container
  (`-v $PWD:$PWD -w $PWD`), because the bind mounts Testcontainers requests are
  resolved on the host. Set `TESTCONTAINERS_HOST_OVERRIDE` when mapped ports
  are reachable on another host name (Docker Desktop uses
  `host.docker.internal`). Observed in practice: a non-root build user needs a
  supplementary group whose **numeric** GID matches the socket's group on the
  host.
- Start-up and pull times are not recorded here; upstream gives no numbers.
  Image pulls go through the mirror prefix above when one is set.

## Interop
- [`spring-boot`](./spring-boot.md): `spring-boot-testcontainers`,
  `@ServiceConnection`, `@DynamicPropertySource`, and BOM management.
- [`maven`](../cli/maven.md): Failsafe for `*IT` classes.
- [`docker`](../container/docker.md): the engine it drives.
- Database pages such as [`mysql-connector-j`](./mysql-connector-j.md) and
  [`postgres`](../container/postgres.md): match the image to production.

## Major lines
### 1.x
Module artifacts without a prefix (`org.testcontainers:mysql`,
`org.testcontainers:junit-jupiter`); JUnit 4 support included; container classes
in the core package (`org.testcontainers.containers`).

### 2.x
Every module is renamed with a `testcontainers-` prefix
(`org.testcontainers:testcontainers-mysql`,
`org.testcontainers:testcontainers-junit-jupiter`); a version bump across the
boundary without the rename fails to resolve. Container classes move to
`org.testcontainers.<module>` (for example `org.testcontainers.mysql`). JUnit 4
support is removed. The bundled Docker client and its API-version default were
updated within the line.

## Upstream docs
- https://java.testcontainers.org/
- https://java.testcontainers.org/test_framework_integration/junit_5/
- https://java.testcontainers.org/test_framework_integration/manual_lifecycle_control/
- https://java.testcontainers.org/features/configuration/
- https://java.testcontainers.org/features/startup_and_waits/
- https://java.testcontainers.org/supported_docker_environment/continuous_integration/dind_patterns/
- https://github.com/testcontainers/testcontainers-java/releases
- https://docs.spring.io/spring-boot/reference/testing/testcontainers.html
