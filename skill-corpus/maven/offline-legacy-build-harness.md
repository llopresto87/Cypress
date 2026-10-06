---
name: offline-legacy-build-harness
description: Compile and run a legacy Maven project's tests on a workstation, offline, without editing its frozen POMs, when a bare build fails on the JDK, on a dead repository, or on a private artifact no public repository holds. Invoke before characterization tests, a new RED test, or a fix verification on such a project.
id: skill.offline-legacy-build-harness
tier: 2
kind: skill
title: offline-legacy-build-harness, three idempotent moves that make a legacy Maven build run its tests offline
owns:
  - offline-legacy-build-harness.procedure
  - offline-legacy-build-harness.failure-table
requires:
load_when:
  - "run the tests of a legacy maven service locally"
  - "mvn test fails: source option no longer supported, dead nexus, missing private artifact"
  - "build a characterization suite for an old java service before a migration"
stack:
  - library-corpus/cli/maven
est_tokens: 2300
---

# Suggested skill: offline-legacy-build-harness

> Optional procedure, **stack-keyed** on Maven: the one method for building
> and testing a legacy JVM project on a workstation with no access to the
> repositories its POMs declare. A bare `mvn test` on such a project fails in
> three independent ways (a JDK that cannot compile it, a declared repository
> that no longer answers, an in-house artifact no public repository holds),
> and each is solved once here, outside the POMs, instead of being re-hit per
> service. **Composes** `protocols/test-first.md` and `protocols/verify.md`
> (the harness serves RED and GREEN; it proves nothing by itself),
> `skill-corpus/vendor-dependency-from-dead-registry.md` (how a private
> artifact is rebuilt from source at the right commit) and
> `library-corpus/cli/maven.md` (settings, mirror and offline semantics) by
> reference. It adds the order of the three moves, the gate after each, and
> the symptom table that says which move a failure belongs to.

**Instantiate by supplying:** `<SOURCE_LEVEL>` (the `source`/`target` or
`release` level the POMs compile at), `<PROCESSORS>` (the annotation
processors the POMs declare, with their versions), `<JDK_HOME>` (the JDK you
pin), `<DEAD_REPOS>` (each repository id and URL the POMs or their parents
declare that no longer answers), `<SETTINGS>` (the user settings file the
harness keeps beside the project), `<VENDORED>` (each in-house artifact as
source or jar, with its coordinates), and `<MODULE>` (the module whose tests
run, as its path from the reactor root or as `[groupId]:artifactId`; every
command runs from the reactor root).

## When to apply

- A legacy service's tests must run locally: a characterization suite before
  a migration (`skill-corpus/framework-version-migration.md`, step 1), a new
  RED test, or the verification of a fix.
- `mvn test` fails with a source-level error, an annotation-processor crash,
  a hang or a transfer error on a repository host that is gone, or a missing
  artifact whose group id is in-house.

**Hard boundary: the POMs are frozen.** The project's POMs describe what was
built and shipped; the harness changes the environment around them, never
the POMs. Dropping a dead repository from a POM, raising its source level or
bumping its processor makes the tests run against a project that is no longer
the one under characterization, and the edit lands in the next commit by
accident. Every move below is a JDK choice, a settings file or the local
repository, and each one is undone by deleting it.

## 1. Pin a JDK that can build the project as written

*Replaces: running on whatever JDK the Maven installation defaults to, then
editing the POM until it compiles.*

- **Read the two constraints from the POMs.** The JDK must still accept
  `<SOURCE_LEVEL>`: each JDK release drops the oldest levels, and javac then
  stops with "Source option N is no longer supported". It must also be a JDK
  that each processor in `<PROCESSORS>` supports at its declared version: an
  annotation processor older than the compiling JDK fails with a crash during
  annotation processing or with "cannot find symbol" on generated accessors
  (`library-corpus/maven/lombok.md`, General pitfalls). Pick the oldest
  long-term-support JDK that satisfies both, not the newest.
- **Pin it for the whole invocation.** Set `JAVA_HOME=<JDK_HOME>` in the
  command or the wrapper script (step 5). When the host's Maven must keep
  running on another JDK, a `toolchains.xml` file alone does nothing: Maven's
  toolchains guide needs the toolchains plugin in the project POM as well,
  and that is a POM edit. The form that needs no POM edit is the plugin's
  `select-jdk-toolchain` goal (since its 3.2.0 release) named on the command
  line ahead of the phase, with the constraint as a user property:
  `mvn -s <SETTINGS> org.apache.maven.plugins:maven-toolchains-plugin:<version>:select-jdk-toolchain -Dtoolchain.jdk.version=<constraint> compile`.
  It discovers installed JDKs or reads `toolchains.xml`. The compile gate
  below then proves that the toolchain was selected: a source-level error
  means it was not.
- **Gate:** `mvn -version` reports `<JDK_HOME>` as the Java home it runs on,
  and `mvn -q -s <SETTINGS> compile -pl <MODULE> -am` passes the compile, or fails
  only on a missing artifact (moves 2 and 3), never on the source level or a
  processor crash. When the JDK did not take, the error is the source-level
  one again.

## 2. Neutralize every dead repository from a user settings file

*Replaces: deleting the `<repository>` from the POM, or waiting out its
timeout on every build.*

- **Write `<SETTINGS>` with one mirror** that replaces every non-local
  repository with the public central repository:

```xml
<settings>
  <mirrors>
    <mirror>
      <id>central-for-everything</id>
      <mirrorOf>external:*</mirrorOf>
      <url>https://repo.maven.apache.org/maven2</url>
    </mirror>
  </mirrors>
</settings>
```

- **Know what the selector does** (`library-corpus/cli/maven.md`, Mirrors).
  A matching mirror replaces the repository; Maven takes the first match and
  never aggregates. `external:*` matches every repository except `localhost`
  and `file://` ones, so a dead repository declared on `localhost` or as a
  file path is not covered: add its id to the `mirrorOf` list (no spaces in
  the list). A mirror for everything must hold every artifact the build
  needs, which is exactly what the in-house artifacts of move 3 break.
- **Keep credentials out.** The file needs none for the public central
  repository; it is committed beside the project, so it never carries a
  password.
- **Pass it on every invocation** with `-s <SETTINGS>`. A build without `-s`
  reads the user's default settings and goes back to the dead host.
- **Gate:** `mvn -s <SETTINGS> help:effective-settings` shows the mirror, and
  the build log of the next step contains no line naming a host from
  `<DEAD_REPOS>` (Maven logs each transfer as "Downloading from <id>: <url>").

## 3. Install each in-house artifact into the local repository, once

*Replaces: expecting the public repository to have it, or pointing a POM at
a path on disk.*

- **The local repository is consulted before any remote repository or
  mirror**, so an artifact installed there resolves offline under the
  coordinates the POMs already use.
- **From source**, build it with the step 1 JDK and the step 2 settings:
  `JAVA_HOME=<JDK_HOME> mvn -q -s <SETTINGS> -DskipTests -f <VENDORED>/pom.xml install`.
  The source must be the commit whose POM version equals the version the
  consumers declare, not the branch tip; finding that commit, and proving
  which artifacts are in-house, is
  `skill-corpus/vendor-dependency-from-dead-registry.md`.
- **From a jar with its POM**:
  `mvn -s <SETTINGS> install:install-file -Dfile=<artifact>.jar -DpomFile=<artifact>.pom`.
  A jar built by Maven carries its POM under `META-INF/maven/`, and
  `install-file` reads that one when `-DpomFile` is absent; otherwise it
  generates a minimal POM that declares no dependencies, and the artifact's
  own dependencies vanish from the consumer's tree. Pass `-DpomFile` whenever
  the jar has no embedded POM.
- **Gate:** `~/.m2/repository/<group path>/<artifact>/<version>/` holds the
  jar and its POM, and the consumer's `dependency:tree -s <SETTINGS>` lists
  the coordinates without a resolution error.

## 4. Run the tests through the harness

- **Command:** `JAVA_HOME=<JDK_HOME> mvn -s <SETTINGS> test -pl <MODULE> -am`
  from the reactor root. `-am` builds the sibling modules `<MODULE>` depends
  on in the same run; a module run on its own cannot resolve siblings that
  were never built or installed. It also runs those siblings' tests. Use
  `verify` instead of `test` when the module binds Failsafe for `*IT` classes (a module
  without that binding never runs them: `library-corpus/cli/maven.md`,
  General pitfalls).
- **Record the result by test name**, from the Surefire and Failsafe report
  directories, not by count; this list is what a later change is compared
  against (`skill-corpus/framework-version-migration.md`, step 1).
- **Gate:** the build ends in success, the named list is recorded, and the
  log holds no transfer line to a dead host. A run that cannot reach a gate
  state is recorded as not run (`protocols/verify.md`), never as green.
- **Fully offline afterwards**, when the workstation will lose the network
  too: run `mvn -s <SETTINGS> dependency:go-offline` once while online, then
  `-o` builds need nothing remote. `-U` and `-o` do not mix.

## 5. Make it repeatable

- Keep `<SETTINGS>`, the vendored sources and a short wrapper script beside
  the project (the script sets `JAVA_HOME`, passes `-s`, and runs the install
  of move 3 before the tests; every move is idempotent, so re-running is
  safe).
- Record in the plant's own harness skill which JDK was pinned and why
  (`<SOURCE_LEVEL>`, the processor version), so the next session does not
  re-derive it. The JDK pin is the plant's; this page holds only the method.

## Symptom table

| symptom | cause | move |
|---|---|---|
| `Source option N is no longer supported. Use M or later.` | the JDK is newer than the project's source level allows | 1 |
| a crash inside annotation processing, or "cannot find symbol" on getters and builders the code calls | the processor version predates the compiling JDK | 1 |
| a hang, then `Could not transfer artifact … from/to <id> (<dead URL>)` | no mirror covers that repository, or `-s` was omitted | 2 |
| `Blocked mirror for repositories: […]` | a declared repository is plain HTTP and current Maven blocks it (`library-corpus/cli/maven.md`, Security defaults) | 2, with the mirror on HTTPS |
| `Could not find artifact <in-house coordinates> in <mirror id>` | the in-house artifact is not in the local repository | 3 |
| `… This failure was cached in the local repository and resolution is not reattempted until the update interval … has elapsed or updates are forced` (older releases word it slightly differently) | an earlier failed lookup is cached | rerun once online with `-U` after fixing the cause |
| the build is green but fewer tests ran than the named baseline | `*IT` classes in a module with no Failsafe binding, or a test filter | 4 |

## Reference files

- `library-corpus/cli/maven.md` (settings, mirrors, offline, Surefire and
  Failsafe, plain-HTTP blocking)
- `library-corpus/maven/lombok.md` (processor versus JDK)
- `skill-corpus/vendor-dependency-from-dead-registry.md` (in-house artifacts
  rebuilt at the consumer's pinned version)
- `skill-corpus/framework-version-migration.md` (the characterization
  baseline this harness produces)
- `protocols/test-first.md`, `protocols/verify.md` (RED, GREEN, and a gate
  not run)
