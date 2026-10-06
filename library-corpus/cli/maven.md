# maven — cli

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Apache Maven is a build and project-management tool built on a Project Object
Model (POM): a declarative build description, a lifecycle of phases, plugins
whose goals bind to those phases, and dependency resolution from remote
repositories into a local repository. Home: https://maven.apache.org. There is
no lockfile: Maven resolves the dependency graph on every build (observed in
practice; it matches how dependency mediation is documented). The host or the
build image supplies the Maven version, or the Maven Wrapper pins it per
repository.

Support: Maven maintains the last version of the last two GA series; older
series are end of life with no bug or security fixes, and Maven does not
distinguish end of life from end of support. Maven 3 runs on Java 8; Maven 4
runs on Java 17 and can still compile for older JDKs through the compiler
plugin or toolchains.

## Install, setup and configuration
- **Lifecycle.** The default lifecycle runs `validate`, `compile`, `test`,
  `package`, `verify`, `install`, `deploy` in order; a phase runs every phase
  before it, and plugin goals bound to each phase do the work.
- **Settings.** User settings are `${user.home}/.m2/settings.xml`, global
  settings `conf/settings.xml` in the installation; `-s` and `-gs` select
  others. Settings interpolate `${user.home}`, system properties and
  `${env.X}`. Top-level elements: `localRepository` (default
  `${user.home}/.m2/repository`), `interactiveMode`, `offline`,
  `pluginGroups`, `servers`, `mirrors`, `proxies`, `profiles`,
  `activeProfiles`.
- **Mirrors.** A `<mirror>` whose `mirrorOf` matches a repository id replaces
  that repository. There is at most one mirror per repository: Maven picks the
  first match (an exact id wins first) and never aggregates; use a repository
  manager for a combined view. `mirrorOf` syntax: `*` matches every id;
  `external:*` matches everything except localhost and `file://` repositories;
  `external:http:*` matches HTTP repositories except localhost; lists are
  comma-separated and `!id` excludes. **Whitespace breaks the list:**
  `!repo1, *` mirrors nothing, while `!repo1,*` mirrors everything except
  repo1. A `*` mirror must hold or proxy every artifact the build needs.
- **Credentials.** `<servers><server><id>` matches a repository or mirror id;
  passwords can be encrypted (`mvn -emp` for the master password, `mvn -ep` for
  a server password).
- **Offline.** `-o` / `--offline` or `<offline>true</offline>`. An offline build
  succeeds only when every dependency, plugin and plugin dependency is already
  local; `dependency:go-offline` resolves all of them (reports included) to warm
  the cache.
- **Maven Wrapper.** `mvn wrapper:wrapper` adds `mvnw`, `mvnw.cmd` and
  `.mvn/wrapper/maven-wrapper.properties` (`distributionUrl`); the script
  downloads the pinned Maven on first use, needs a POSIX shell, and reads
  `MVNW_USERNAME` / `MVNW_PASSWORD` for a protected repository.
- **Toolchains.** `toolchains.xml` (`-t` / `-gt`) lets a build compile and test
  with a JDK other than the one running Maven.
- **CLI options.** `-B` batch mode (no colour, no prompts), `-q` quiet, `-ntp` no
  transfer progress, `-U` force a check for missing releases and updated
  snapshots, `-o` offline, `-pl` select reactor projects (by
  `[groupId]:artifactId` or path), `-am` also build what they need, `-amd` also
  build what depends on them, `-rf` resume from a project, `-T` threads, `-f`
  another POM, `-P` profiles, `-D` a property, `-N` non-recursive, `-e` / `-X`
  error and debug output.

## Core API / usage shape
- **Parent POM versus imported BOM.** A `<parent>` passes on properties, plugin
  configuration and `dependencyManagement`. A dependency of type `pom` with
  `<scope>import</scope>` inside `<dependencyManagement>` is replaced by that
  POM's managed versions and nothing else; import exists because a project has
  only one parent. **Overriding a managed version through a `<properties>` entry
  (a library's version property) works only through parent inheritance.** With
  an imported BOM the property has no effect: add an explicit
  `<dependencyManagement>` entry placed *before* the BOM import.
- **Dependency mediation.** The nearest definition in the tree wins; at equal
  depth the first declaration wins; an explicit version in the POM is
  guaranteed. `dependencyManagement` sets the version of transitive
  dependencies too. Exclusions drop a transitive dependency; `optional`
  dependencies do not pass to consumers.
- **Compiler plugin.** `<release>` / `maven.compiler.release` passes javac
  `--release`; `<parameters>` / `maven.compiler.parameters` passes
  `-parameters` (default false); `<proc>` (`none`, `only`, `full`) controls
  annotation processing; `<annotationProcessorPaths>` limits processor discovery
  to the listed artifacts, and without it the class path is searched.
- **Tests.** Surefire runs `**/Test*.java`, `**/*Test.java`, `**/*Tests.java`
  and `**/*TestCase.java` in the `test` phase. Failsafe runs `**/IT*.java`,
  `**/*IT.java` and `**/*ITCase.java`, and only when it is bound to the
  `integration-test` and `verify` goals and the build reaches `verify`.
- **Skipping.** `-DskipTests` skips running tests but compiles them;
  `-Dmaven.test.skip=true` also skips compiling them, and Surefire, Failsafe
  and the compiler plugin all honour it. A `skipTests` property in the POM
  skips by default and still allows a command-line override.
- **Inspection.** `mvn dependency:tree` prints the resolved tree (text, DOT,
  GraphML, TGF, JSON).
- **Enforcer.** `maven-enforcer-plugin` (`enforcer:enforce`) checks rules per
  project, such as the required Maven or JDK version and dependency convergence.

## Idioms & best practices
- Keep one compile level and one plugin set for every module, and pin every
  plugin version: reproducibility and a complete `go-offline` both depend on it.
- Diff `mvn dependency:tree` per module before and after any parent or BOM move
  (observed in practice): it is the one view of what a version bump changed
  underneath.
- Warm an offline cache in one step, then build with `-o -B`.
- Reproducible builds: set `project.build.outputTimestamp`, use plugin versions
  that support it (`mvn artifact:check-buildplan` lists the ones to upgrade),
  and verify with `mvn clean install` then
  `mvn clean verify artifact:compare`.
- Neutralize a dead repository declared in a POM you cannot edit with a
  settings-level mirror rather than by editing the POM (the mechanism is
  upstream; the use is observed in practice).
- In CI, run `mvn -B -ntp` so logs carry no colour codes or download noise.

## General pitfalls
- **`*IT` classes that never run.** Without a bound Failsafe execution,
  integration tests named `*IT` match no Surefire pattern and are silently
  skipped.
- **`mvn verify` is a phase, not a test runner.** With no test sources and no
  verifier plugin bound, it runs only the default bindings; a green `verify`
  proves nothing about tests or checks.
- **Hand pins drift** (observed in practice; the docs describe the mechanism,
  not this failure). An explicit `<version>` on a dependency that a BOM already
  manages reintroduces drift, and in a fleet of separate repositories a hand pin
  in one does not reach the others.
- **Coordinate renames** (observed in practice). When upstream moves a
  groupId or artifactId, the old coordinate falls out of BOM management and a
  version-less declaration stops resolving; the fix is the new coordinate, not
  a version. Upstream announces such moves with a `<relocation>` element in the
  old coordinate's POM.
- **Annotation processors.** The compiler plugin page says to set `<proc>`
  explicitly from JDK 21; the JDK 23 release note says javac stops class-path
  discovery from 23 (21 and 22 print a note). Declare processors in
  `<annotationProcessorPaths>` (or pass `-proc:full`) rather than relying on
  discovery.
- **`release` limits some flags.** With `maven.compiler.release` set,
  `--add-exports`, `--add-reads` and `--patch-module` cannot modify system
  modules; unset `release` and use `source`/`target` when a build needs them.
- **`-U` and offline do not mix**: `-U` asks for remote checks that an offline
  build never makes.
- **Wrapper leftovers** (observed in practice). A
  `maven-wrapper.properties` file with no `mvnw` beside it pins nothing.

## Testing
- Unit tests run under Surefire in `test`; integration tests named `*IT` run
  under Failsafe bound to `integration-test` and `verify`. Failsafe's `verify`
  goal fails the build after the post-integration phase has torn the
  environment down, so cleanup always runs.
- Recent Surefire and Failsafe releases run every test through the JUnit
  Platform and choose the engine from the dependencies (`junit-jupiter-engine`,
  JUnit 4 through the Vintage engine, TestNG).
- Run integration tests with `mvn verify`, never `mvn integration-test`, so the
  teardown phases run.

## Security defaults
- **Plain-HTTP repositories are blocked.** Current Maven releases ship a
  blocking mirror for `external:http:*` in the global settings; a POM that
  points to an `http://` repository fails unless it is mirrored to HTTPS or the
  block is overridden. Upstream gives the reasons: hijacking of abandoned
  repository domains and download redirection. Older Maven 3 releases did not
  block, so a Maven upgrade can break a build that once passed.
- Keep credentials in `<servers>` with encrypted passwords; never commit them
  or bake a `settings.xml` with passwords into an image layer.
- Apache Maven's security model
  (https://maven.apache.org/security.html) assumes you trust the POM, the
  code, the dependencies and the repositories a build uses. Building untrusted
  code needs isolation that you provide. Upstream ships no binary patch for a
  single vulnerability; the fix is an upgrade to a Maven version that has it.

## Operational behaviour
- The local repository is `~/.m2/repository` unless `localRepository` moves
  it; every build reads and fills it.
- **The `maven` container image.** Tags combine a Maven and a JDK version
  (`maven:<maven>-eclipse-temurin-<jdk>`), and both halves float. Only the tags
  in the image README's supported list are rebuilt. The local repository can be
  shared across containers through a volume at `/root/.m2`; `$MAVEN_CONFIG`
  defaults to `/root/.m2` and may be a volume, so files copied there at build
  time can be hidden; put pre-seeded files in `/usr/share/maven/ref/`, which is
  copied in at container start.
- **BuildKit cache mounts** (observed in practice, reproduced). A
  `RUN --mount=type=cache` keeps `~/.m2` between builds outside the image
  layers. A step that installs an artifact into the mount and a later step that
  consumes it should share one `RUN`: when the first step is served from the
  layer cache, the mount can be cold for the second. The Dockerfile reference
  documents the cache mount, not this case.

## Interop
- **Spring Boot.** The starter parent supplies managed versions, plugin
  management, `maven.compiler.release` from `<java.version>`, and the
  `-parameters` flag. Without the parent, import `spring-boot-dependencies` as a
  BOM (versions only, no plugin management) and override versions with
  `<dependencyManagement>` entries before the import. Boot's system-requirements
  page names the minimum Maven version for each line. See [`spring-boot`](../maven/spring-boot.md).
- **JDK.** Maven runs on the JDK it starts with; the compile level is
  `release`; toolchains pick another JDK. See [`java`](../language/java.md).
- **Container builds.** See [`jib-maven-plugin`](../maven/jib-maven-plugin.md)
  for daemonless image builds and
  [`eclipse-temurin`](../container/eclipse-temurin.md) for the builder and
  runtime images.

## Major lines
### Maven 3
The production line. Later Maven 3 releases added the HTTP-repository block
and the `external:http:*` selector and `<blocked>` mirror parameter. Runs on
Java 8 or later.

### Maven 4
Runs on Java 17. POM model version 4.1.0; the consumer POM that is published is
separated from the build POM; modules are renamed subprojects; a `bom`
packaging type; reproducible-build mode on by default. When this page was last
confirmed against upstream, Maven 4 was a release candidate that the history
page said was not for production use.

## Upstream docs
- https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html
- https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html
- https://maven.apache.org/settings.html
- https://maven.apache.org/guides/mini/guide-mirror-settings.html
- https://maven.apache.org/guides/mini/guide-encryption.html
- https://maven.apache.org/ref/current/maven-embedder/cli.html
- https://maven.apache.org/plugins/maven-compiler-plugin/compile-mojo.html
- https://maven.apache.org/surefire/maven-failsafe-plugin/usage.html
- https://maven.apache.org/wrapper/
- https://maven.apache.org/guides/mini/guide-reproducible-builds.html
- https://maven.apache.org/docs/history.html and https://maven.apache.org/whatsnewinmaven4.html
- https://hub.docker.com/_/maven (image README)
