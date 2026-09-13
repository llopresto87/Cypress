# eclipse-temurin — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile / base-image tag.

## What it is
Eclipse Temurin is the OpenJDK build produced by the Eclipse Adoptium project —
a freely redistributable, TCK-tested Java runtime and development kit. Its
container images (`eclipse-temurin` on Docker Hub) are the common neutral base
for building and running JVM workloads: no vendor account, no click-through
licence, and the same binaries across CI, developer machines, and deployment.

Two image families matter and are routinely confused:

- **`-jdk`** — the full development kit: `javac`, `jar`, `jlink`, `jcmd`,
  diagnostics. Use it to *compile*.
- **`-jre`** — the runtime only, no compiler and no tooling. Use it to *run*, and
  it is materially smaller.

Tags also vary by OS base (a glibc distribution, an Alpine/musl variant, and
enterprise-base variants), and that choice is behavioral, not cosmetic.

## Core API / usage shape
- As a base image in a Dockerfile:
  ```dockerfile
  FROM eclipse-temurin:<tag>-jdk AS build
  # compile here
  FROM eclipse-temurin:<tag>-jre
  COPY --from=build /app/target/app.jar /app/app.jar
  ENTRYPOINT ["java", "-jar", "/app/app.jar"]
  ```
- The image contributes the standard JDK/JRE command surface — `java`, `javac`,
  `jar`, `jlink`, `jdeps`, `keytool` — plus `JAVA_HOME` already set on `PATH`.
- Tag shape is a **major line** (`NN-jdk`) or a **full build identifier**; the
  first is a moving pointer that is re-resolved on every pull, the second is
  stable.
- `jlink` / `jdeps` build a trimmed custom runtime image from the JDK variant
  when even the `-jre` image is larger than the application needs.

## Idioms & best practices
- **Compile in the `-jdk` stage, ship the `-jre` stage.** The shipped image then
  contains no compiler, no build tooling, and a much smaller attack surface.
- **Pin a full build tag when reproducibility matters.** A bare major tag means
  a rebuild months later silently uses a different compiler and a different
  runtime, with no diff anywhere in the repository to show it.
- **When extending a closed base image (a server you are writing a plugin for),
  compile against jars copied out of that very image** rather than resolving the
  same libraries from a package repository. The build then needs no repository
  access at all and version drift between the plugin and its host is impossible
  by construction.
- **Size the heap relative to the container, not absolutely.** Modern JVMs are
  container-aware and read cgroup limits; percentage-of-RAM flags track a
  changed memory limit, a hard-coded maximum heap does not.
- **Order the build stage so dependency resolution is cached** — copy the build
  descriptor and resolve dependencies before copying sources — so an ordinary
  source edit does not re-download the world.
- **Run as a non-root user in the runtime stage**, and keep the build stage's
  toolchain out of it.

## General pitfalls
- **A major-line tag is a moving target.** `NN-jdk` resolves to whatever build
  was current at pull time, and that resolution is not recorded anywhere by
  default — so "the same Dockerfile" can produce two different compilers.
- **Class-file version mismatch is the classic failure.** Code compiled by a
  newer JDK will not load on an older runtime; the symptom is an
  `UnsupportedClassVersionError` at start-up, not at build. Build and runtime
  images must be reconciled deliberately, and cross-compiling for an older target
  needs an explicit release flag rather than a hopeful assumption.
- **`-jre` has no `javac`.** A build step that quietly landed in the runtime
  stage fails with "command not found" and reads like a corrupted image.
- **The musl-based variants are a different libc.** Anything with native
  dependencies — JNI libraries, native database drivers, some profilers — can
  fail or behave differently there, and the failure surfaces at run time in the
  smallest image, which is exactly where it is hardest to debug.
- **Compiling against a classpath assembled by hand is fragile.** Libraries
  commonly carry annotations referencing classes absent from a partial classpath,
  so warnings-as-errors turns a harmless annotation reference into a build
  failure; either complete the classpath or accept the warnings knowingly.
- **A build-stage-only base image is invisible to dependency tooling.** It ships
  in no artifact, appears in no manifest or lockfile, and is therefore missed by
  inventory and by anything that reports the stack's components — it still
  decides what your bytecode is.
- **Slim images omit things the JDK assumes.** Locale data, timezone data, CA
  certificates, and fonts are common casualties; the symptom is a date, a TLS
  handshake, or image rendering failing only in the container.

## Upstream docs
- https://adoptium.net/docs/
- https://hub.docker.com/_/eclipse-temurin
- https://github.com/adoptium/containers
