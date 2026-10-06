# jib-maven-plugin — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Jib builds Docker and OCI images for Java applications straight from the build,
with no Dockerfile. It lays the application out as separate layers
(dependencies, resources, classes) instead of one fat jar, so a rebuild reuses
the layers that did not change. The Maven plugin is
`com.google.cloud.tools:jib-maven-plugin`; a Gradle plugin and the Jib CLI share
the same core. Home: https://github.com/GoogleContainerTools/jib (the
`jib-maven-plugin` directory holds the plugin README, the reference for every
option). Upstream marks the project stable.

## Install, setup and configuration
- Add the plugin under `<build><plugins>` with `<to><image>` set, or pass
  `-Dimage=` / `-Djib.to.image=`. One-shot use without touching the POM:
  `mvn compile com.google.cloud.tools:jib-maven-plugin:<version>:build -Dimage=<ref>`.
- **Goals.**
  - `jib:build` builds and pushes straight to a registry; it talks to the
    registry itself and needs no Docker daemon.
  - `jib:dockerBuild` builds into a local Docker daemon through the `docker`
    command-line tool, which must be on the `PATH` with a reachable daemon
    (`dockerClient.executable` and `dockerClient.environment` adjust it).
  - `jib:buildTar` writes `target/jib-image.tar` (load it with
    `docker load --input`) and needs neither at build time.
  Every goal writes the image digest and image ID to `target/jib-image.digest`
  and `target/jib-image.id` (`outputPaths`).
- **Lifecycle binding.** An `<execution>` with `<phase>package</phase>` and goal
  `build` makes `mvn package` build the image. Skip with `<skip>` or
  `-Djib.skip=true` (useful per module in a multi-module build).
- **Base image (`<from><image>`).** The default is an `eclipse-temurin` JRE image
  matching the project's Java version (`jetty` for WAR projects). Prefixes pick
  the source: none or `registry://` (a registry), `docker://` (the local
  daemon), `tar://` (a tarball). The default tag moves; pin a digest for strong
  reproducibility.
- **Target tags and credentials.** With no tag, `:latest` is implied;
  `<to><tags>` adds more. Credentials come from `<to><auth>`, `credHelper`,
  Docker config files and credential helpers, or Maven settings `<server>`
  entries (encrypt the Maven password).
- **`<container>` options.** `jvmFlags`, `mainClass` (inferred when absent),
  `args`, `entrypoint` (when set, `jvmFlags`, `mainClass`, `extraClasspath` and
  `expandClasspathDependencies` are ignored; `INHERIT` keeps the base image's
  entrypoint), `environment`, `ports`, `labels`, `user`, `appRoot`, `format`
  (Docker or OCI), `creationTime`, `filesModificationTime`.
- `containerizingMode` defaults to `exploded` (individual class and resource
  files in layers); `packaged` puts the built jar into the image.
  `allowInsecureRegistries` defaults to false.
- **Extra files.** `extraDirectories` (default `src/main/jib`) copies files into
  the image relative to the container root, each directory as its own layer;
  the build fails when a configured `from` path does not exist.
- **Reproducibility.** The image creation time defaults to the Unix epoch, which
  is why `docker images` shows an image created decades ago;
  `USE_CURRENT_TIMESTAMP` or an ISO 8601 value changes it at the cost of
  reproducibility.

## Core API / usage shape
- **Image layout:** `/app/libs/` (dependencies), `/app/resources/`,
  `/app/classes/`. Default entrypoint:
  `java <jvmFlags> -cp /app/resources:/app/classes:/app/libs/* <mainClass>`.
  The files `/app/jib-classpath-file` and `/app/jib-main-class-file` expose the
  default class path and main class to custom start scripts.
- **Layers:** other dependencies, snapshot dependencies, project dependencies,
  resources, classes, and one per extra directory; files that change often sit
  apart from those that rarely change.
- Jib runs no commands during the build (no `apt-get`); a step like that
  belongs in a custom base image named in `<from><image>`.
- Multi-module projects need special handling of project dependencies; the
  upstream multi-module example shows it.
- WAR projects default to a Jetty base image and `appRoot` handling.

## Idioms & best practices
- Pin `<from><image>` to a version or a digest, and keep it a maintained base
  image.
- Use `jib:dockerBuild` for local development and `jib:build` in CI, where no
  daemon is needed.
- Tag with a version or digest as well as any moving tag, and keep the digest
  file as the record of the exact build.
- When a pipeline builds with a Dockerfile instead, pass `-Djib.skip=true` and
  remove the Jib binding once Jib is retired.

## General pitfalls
- **A bound goal runs on every package.** A Jib goal bound to `package` builds,
  or pushes, an image on every `mvn package`. A Dockerfile pipeline must pass
  `-Djib.skip=true`, and a vestigial binding survives retirement unnoticed
  (observed in practice, more than once; the binding and skip option are
  upstream).
- **`jib:dockerBuild` needs Docker.** It shells out to the `docker` CLI, so it
  does not build without a daemon; only `jib:build` (and `jib:buildTar`) avoid
  one.
- **The base image is a second runtime pin.** It can disagree with the compile
  level: bytecode must not be newer than the base image's runtime (see
  [`java`](../language/java.md)). The `adoptopenjdk` and distroless defaults of
  older Jib lines, and the `openjdk` image, are stale choices; observed in
  practice, older configurations still name `openjdk` bases.
- **Docker Hub rate limits (HTTP 429).** Jib checks the cached base image with
  Docker Hub on every run unless the base is pinned by digest; a registry
  mirror, a digest pin, an offline build, a local daemon or registry base, or
  retries avoid it.
- **`latest`-only target tags** leave no immutable reference to roll back to
  (observed in practice; the docs state only that `latest` is implied).
- **Exploded class path.** Jib runs classes and jars from directories, so
  resource-as-file code that works under Jib can fail in a fat-jar image, where
  a jar entry is not a file (observed in practice; upstream confirms the layout,
  and Spring documents the jar rule). See
  [`spring-framework`](./spring-framework.md).
- **Registries without HTTPS.** Jib does not send credentials over plain HTTP
  unless `sendCredentialsOverHttp` is set (not recommended);
  `allowInsecureRegistries` ignores certificate errors and may fall back to
  HTTP.

## Testing
- Build to a tarball (`jib:buildTar`) or into the local daemon
  (`jib:dockerBuild`), then run and inspect the image; the digest and image ID
  files support assertions in CI. The outputs are upstream; using them as a test
  is advice. The FAQ explains how to inspect an image and turn on debugging.

## Security defaults
- `allowInsecureRegistries` is false. Credentials come from credential helpers
  or Docker config first, then Maven settings; encrypt Maven passwords.
- The plugin checks for new releases by fetching a text file, and the request is
  logged with path, source IP and user agent. Turn it off with the
  `jib.disableUpdateChecks` system property or `disableUpdateCheck` in the
  global Jib configuration.
- Default base images are third-party and unpinned; a digest gives
  supply-chain stability.

## Operational behaviour
- The creation time is the epoch for reproducibility; file modification times
  are set separately (`filesModificationTime`).
- Base-image layers are cached locally (on Linux under
  `$XDG_CACHE_HOME/google-cloud-tools-java/jib/`, else `~/.cache`), and the build
  cache keeps rebuilds fast. A global Jib configuration file holds options such
  as registry mirrors.

## Interop
- **Maven.** Lifecycle binding, settings credentials, and `-Djib.*`
  properties. See [`maven`](../cli/maven.md).
- **Docker and Dockerfile builds.** A Dockerfile pipeline is an alternative to
  Jib, not a layer on top; the FAQ documents a Dockerfile that mimics Jib's
  layout. See [`docker`](../container/docker.md).
- **Eclipse Temurin** images are the default base. See
  [`eclipse-temurin`](../container/eclipse-temurin.md).
- **Spring Boot.** The Maven plugin containerizes the project's classes and
  dependencies directly; the Jib CLI's jar mode treats Boot fat jars as an
  exception it can still layer. See [`spring-boot`](./spring-boot.md).

## Major lines
### Jib 2 and earlier
Default base image: distroless Java. To keep that behaviour on a later line,
name a distroless base explicitly.

### Jib 3
Default base `adoptopenjdk` at first, then official `eclipse-temurin` images
(`jetty` for WAR), extended over the line to new Java releases. Jib 3 also added
`<includes>` / `<excludes>` for extra directories, extension loading through
Maven dependency injection, and the class-path and main-class argument files.
Moving from Jib 2: pin your own base image to keep behaviour stable.

## Upstream docs
- https://github.com/GoogleContainerTools/jib/tree/master/jib-maven-plugin (README: every option)
- https://github.com/GoogleContainerTools/jib/blob/master/docs/faq.md
- https://github.com/GoogleContainerTools/jib/blob/master/docs/default_base_image.md
- https://github.com/GoogleContainerTools/jib/blob/master/jib-maven-plugin/CHANGELOG.md
- https://github.com/GoogleContainerTools/jib/blob/master/docs/privacy.md
