# eclipse-temurin — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
Eclipse Temurin is the OpenJDK build produced by the Eclipse Adoptium project:
a freely redistributable, TCK-tested Java runtime and development kit. Its
container images (`eclipse-temurin` on Docker Hub) are the common neutral base
for building and running JVM workloads: no vendor account, no click-through
licence, and the same binaries across CI, developer machines, and deployment.

Two image families matter and are routinely confused:

- **`-jdk`**: the full development kit: `javac`, `jar`, `jlink`, `jcmd`,
  diagnostics. Use it to *compile*.
- **`-jre`**: the runtime only, no compiler and no tooling. Use it to *run*, and
  it is materially smaller.

Tags also vary by OS base (a glibc distribution, an Alpine/musl variant, and
enterprise-base variants), and that choice is behavioral, not cosmetic. The
default glibc tags are Ubuntu-based, with suite codenames selecting the
release; `ubi*-minimal` and Windows variants also exist. The Dockerfiles live
in `adoptium/containers`.

## Install, setup and configuration
- **`JAVA_HOME`** is `/opt/java/openjdk`, already on `PATH`. To put a Temurin
  JDK into another base image, copy that directory from a Temurin image and set
  `JAVA_HOME` and `PATH` yourself (upstream's own recipe).
- **Internal CA trust.** Put PEM `.crt` files in `/certificates` and set
  `USE_SYSTEM_CA_CERTS` to any value: the entrypoint adds them to the JVM
  truststore and the OS store. Under a non-root user or a read-only root
  filesystem it builds a separate truststore instead (it needs a writable
  `/tmp`), extends `JAVA_TOOL_OPTIONS` to point at it, and exports the path as
  `JRE_CACERTS_PATH`. Not available on Windows images.
- **JVM options from the environment.** `JAVA_TOOL_OPTIONS` is the variable
  the JVM Tool Interface specifies (split on whitespace, read where the
  command line cannot be changed); the image itself uses it. Prefer it to
  `_JAVA_OPTIONS`, which the specifications do not document.
- **Container sizing defaults.** On Linux the JVM detects the container's
  memory and CPU limits by default (`-XX:-UseContainerSupport` turns that off;
  `-Xlog:os+container=trace` shows what it read). `MaxRAMPercentage` defaults
  to 25, so with no flags the maximum heap is about a quarter of the memory
  limit, or of host memory when the container has no limit.

## Core API / usage shape
- As a base image in a Dockerfile:
  ```dockerfile
  FROM eclipse-temurin:<tag>-jdk AS build
  # compile here
  FROM eclipse-temurin:<tag>-jre
  COPY --from=build /app/target/app.jar /app/app.jar
  ENTRYPOINT ["java", "-jar", "/app/app.jar"]
  ```
- The image contributes the standard JDK/JRE command surface (`java`, `javac`,
  `jar`, `jlink`, `jdeps`, `keytool`) plus `JAVA_HOME` already set on `PATH`.
- Tag shape is a **major line** (`NN-jdk`) or a **full build identifier**; the
  first is a moving pointer that is re-resolved on every pull, the second is
  stable.
- `jlink` / `jdeps` build a trimmed custom runtime image from the JDK variant
  when even the `-jre` image is larger than the application needs. Upstream
  recommends a `jlink`-built runtime over the stock `-jre` from the 21 line on,
  and shows the multi-stage recipe.
- The JDK often arrives inside another image (a build tool's
  `<tool>:<ver>-eclipse-temurin-<NN>` tag), which then floats on two lines at
  once.

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
- **Order the build stage so dependency resolution is cached**: copy the build
  descriptor and resolve dependencies before copying sources, so an ordinary
  source edit does not re-download the world.
- **Run as a non-root user in the runtime stage**, and keep the build stage's
  toolchain out of it. User creation differs by variant (`addgroup -S` /
  `adduser -S` on Alpine, `groupadd` / `useradd` on Ubuntu); give explicit
  uid and gid when the process must match the owner of a bind-mounted file.
- **Pin the OS suite** in the tag when the Dockerfile installs extra
  packages, so a base change does not alter what `apt` resolves.
- **Re-pin on the quarterly update cadence.** A digest pin freezes the JDK
  patch level and the OS packages; record the `java -version` build string
  with each re-pin.
- **Set the container memory limit first, then size by percentage.** A fixed
  `-Xmx` on many containers with no limit over-commits the host into the
  out-of-memory killer. "No flags" is a deliberate choice of a quarter-of-limit
  heap, not a neutral default.
- **Move the JVM major, the language level and the framework's supported
  Java range together**, in one change.
- **Cite the Adoptium lifecycle**, not another vendor's: LTS releases are
  built as long as OpenJDK upstream maintains them (at least four years), a
  non-LTS release ends with its successor, and updates come quarterly.

## General pitfalls
- **A major-line tag is a moving target.** `NN-jdk` resolves to whatever build
  was current at pull time, and that resolution is not recorded anywhere by
  default, so "the same Dockerfile" can produce two different compilers.
- **Class-file version mismatch is the classic failure.** Code compiled by a
  newer JDK will not load on an older runtime; the symptom is an
  `UnsupportedClassVersionError` at start-up, not at build. Build and runtime
  images must be reconciled deliberately, and cross-compiling for an older target
  needs an explicit release flag rather than a hopeful assumption.
- **`-jre` has no `javac`.** A build step that quietly landed in the runtime
  stage fails with "command not found" and reads like a corrupted image.
  Observed in practice, it also lacks `jar`, `jcmd`, `jstack` and `jmap`:
  explode a fat jar in the JDK stage, and take dumps from a sidecar or a debug
  image.
- **Health-check tools differ by variant.** Alpine has BusyBox `wget` but no
  `curl`, `bash` or `git`; the glibc `-jre` has neither `wget` nor `curl`
  (see [`docker.md`](docker.md)).
- **Build stage and runtime stage must agree** on the Java level: compile with
  `--release N` for the runtime image's major (why `-source`/`-target` is not
  enough is on [`language/java.md`](../language/java.md)).
- **The JRE stage never upgrades OS packages.** OS fixes arrive only by
  rebuilding on a newer base or re-pinning.
- **"Pullable" is not "supported".** A tag can stay pullable after it leaves
  the supported-tags list; that risk is separate from a floating tag.
- **No memory limit means host-sized heaps.** `MaxRAMPercentage` tracks only
  a real cgroup limit.
- **The musl-based variants are a different libc.** Anything with native
  dependencies (JNI libraries, native database drivers, some profilers) can
  fail or behave differently there, and the failure surfaces at run time in the
  smallest image, which is exactly where it is hardest to debug.
- **Compiling against a classpath assembled by hand is fragile.** Libraries
  commonly carry annotations referencing classes absent from a partial classpath,
  so warnings-as-errors turns a harmless annotation reference into a build
  failure; either complete the classpath or accept the warnings knowingly.
- **A build-stage-only base image is invisible to dependency tooling.** It ships
  in no artifact, appears in no manifest or lockfile, and is therefore missed by
  inventory and by anything that reports the stack's components, yet it still
  decides what your bytecode is.
- **Slim images omit things the JDK assumes.** Locale data, timezone data, CA
  certificates, and fonts are common casualties; the symptom is a date, a TLS
  handshake, or image rendering failing only in the container.

## Testing
- Run the test suite on the runtime image (same variant and libc), not only
  the JDK build image; musl, missing locales and missing CA certificates fail
  only there.
- Start the deployed container once with `-Xlog:os+container=trace` to
  confirm the memory and CPU limits the JVM sees.
- Smoke the health-check command inside the runtime image.

## Security defaults
- Images run as root unless the Dockerfile sets a user.
- The truststore is the JDK's default CA bundle until `/certificates` and
  `USE_SYSTEM_CA_CERTS` add to it.
- The `-jre` and `jlink` runtimes carry no compiler or diagnostic tools, which
  shrinks the attack surface and the debugging surface alike.

## Operational behaviour
- Heap and CPU count follow the container limits the JVM detects at start.
- The JVM is PID 1 when started in exec form, so it receives SIGTERM and runs
  shutdown hooks.

## Interop
- Build tools: [`cli/maven.md`](../cli/maven.md).
- Base-image tooling and health checks: [`docker.md`](docker.md).
- The Java language itself: [`language/java.md`](../language/java.md).

## Major lines
- **17 line**: strong encapsulation is final; what that breaks, and the
  `--add-opens` remedy, are on [`language/java.md`](../language/java.md).
- **21 line and later**: upstream recommends a `jlink`-built runtime over the
  stock `-jre` image.

## Upstream docs
- https://adoptium.net/docs/
- Support lifecycle and release roadmap: https://adoptium.net/support/
- https://hub.docker.com/_/eclipse-temurin
- https://github.com/adoptium/containers
- https://github.com/docker-library/docs/tree/master/eclipse-temurin
- https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html (container support, MaxRAMPercentage, JAVA_TOOL_OPTIONS)
