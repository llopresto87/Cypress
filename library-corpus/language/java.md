# java — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Java SE is a statically typed language and platform specified through the Java
Community Process; OpenJDK is the reference implementation, and each feature
release has an OpenJDK project page that lists its JEPs. Two facts about a Java
project live in different places and must be read separately:

- the **language level**: the compiler `--release` value, held in the build
  descriptor (for Maven, `maven.compiler.release`; the Spring Boot parent maps
  `<java.version>` onto it);
- the **runtime build**: the JDK or JRE that executes the code, held in the base
  image or on the host.

A feature release ships every six months and a maintenance (security) update
every three months. Long-term support is a vendor decision, not an OpenJDK
promise: the 17, 21 and 25 project pages say each is an LTS "from most
vendors". Since 2021 an LTS has arrived every two years (17, 21, 25); 11
predates that cadence. The distribution decides the support dates. Eclipse Temurin, for example, supports
each LTS for at least four years and ends a non-LTS release when its successor
ships; Oracle's commercial dates cover Oracle's builds only. Cite the
distribution's own support page, never a date copied onto a page like this one.

## Install, setup and configuration
- **Compile with `--release N`, not `-source N -target N`.** JEP 247: `-source`
  and `-target` fix the syntax and the class-file version but still compile
  against the newest platform API, so code can call an API that the older
  runtime lacks. `--release` also pins the API surface. Maven exposes it as
  `<release>` / `maven.compiler.release` (the compiling JDK must be 9 or
  later).
- **Class-file direction.** Every release has a class-file major version, and a
  runtime loads the range `45..N`: a newer runtime runs older bytecode; an older
  runtime refuses newer bytecode. The refusal shows up at start-up; the error
  seen in practice is `UnsupportedClassVersionError` (the JVMS page does not name
  it).
- **One level for every module.** Set the release in one property and change it
  everywhere at once, or a multi-module build compiles at mixed levels.
- **Annotation processing (`-proc:none|only|full`).** On JDK 21 and 22, javac
  prints a note when it finds processors on the class path without explicit
  configuration. From JDK 23, processing runs only when it is configured
  (`-processor`, `--processor-path`, `--processor-module-path`) or requested
  with `-proc:full` / `-proc:only`. Declare processors explicitly (Maven:
  `<annotationProcessorPaths>`; see [`maven`](../cli/maven.md)).
- **Default charset.** Since JDK 18 the standard APIs default to UTF-8 (JEP 400),
  except console I/O.
- **Dynamic agents.** JDK 21 warns when an agent is loaded into a running JVM
  (JEP 451); `-XX:+EnableDynamicAgentLoading` silences it for tools that need
  it, and a later release intends to disallow dynamic loading by default.
- **Preview features** need `--enable-preview` together with `--release` (or
  `-source`); incubator APIs need their incubator module.

## Core API / usage shape
Language and platform features by the release that made them final:

| release | feature (JEP) |
|---|---|
| 10 | local-variable type inference `var` (286) |
| 11 | `var` in lambda parameters (323), the `java.net.http` HTTP client (321), single-file source launch (330) |
| 14 | switch expressions (361) |
| 15 | text blocks (378) |
| 16 | records (395), pattern matching for `instanceof` (394) |
| 17 | sealed classes (409) |
| 21 | pattern matching for `switch` (441), record patterns (440), sequenced collections (431), virtual threads (444), generational ZGC (439) |
| 25 | scoped values (506), compact source files and instance main methods (512), flexible constructor bodies (513), compact object headers (519), generational Shenandoah (521), Key Derivation Function API (510) |

- **Virtual threads** (21) are JDK-managed lightweight threads for the
  thread-per-request style; `Executors.newVirtualThreadPerTaskExecutor()` is the
  entry point.
- **Sequenced collections** (21) add interfaces with uniform first/last access
  and reverse-order views for collections with a defined encounter order.
- The JDK 25 page also lists preview and incubator items (stable values,
  structured concurrency, primitive types in patterns, the vector API, module
  import declarations); they are not part of the stable language.

## Idioms & best practices
- Pin the level with `--release` in one place; record the runtime separately in
  the image or host; keep the runtime at or above the level.
- On JDK 21 to 23 with virtual threads, guard long blocking I/O with
  `ReentrantLock` rather than `synchronized`: a virtual thread that blocks inside
  `synchronized` pins its carrier there. Short or rare `synchronized` sections
  need no change. JDK 24 removes most of that pinning (JEP 491).
- Upgrade a library that needs deep reflection into JDK internals; treat
  `--add-opens` as a stop-gap with an owner and an exit.
- Observed in practice: a modern language level says nothing about the dialect
  the code is written in. Compiling at 17 does not mean the code uses records,
  `sealed` or patterns; read the module before assuming its idioms, and write in
  the dialect of the module you land in.

## General pitfalls
- **Strong encapsulation (17, JEP 403).** JDK internals are encapsulated except
  critical ones such as `sun.misc.Unsafe`; `--illegal-access` becomes obsolete
  (a warning, no effect) and only `--add-opens` / `--add-exports` remain. Deep
  reflection into `java.*` internals fails **at run time, not at compile time**
  (in practice, `InaccessibleObjectException`). Reflection over application
  classes is unaffected. On 11 the default was `--illegal-access=permit`; 16
  already denied by default (JEP 396).
- **Java EE and CORBA removed (11, JEP 320).** `java.xml.ws`, `java.xml.bind`,
  `java.activation`, `java.xml.ws.annotation`, `java.corba`,
  `java.transaction` and `java.se.ee` are gone; add them as explicit
  dependencies. Older libraries that assumed them (XML and token libraries
  built for Java 8) fail at run time.
- **Annotation processors on JDK 23+.** A build that relied on class-path
  discovery (Lombok or MapStruct without `annotationProcessorPaths`) can compile
  without generating code and fail later on missing symbols. The release note
  states the default change; the Lombok and MapStruct consequence is an
  inference from it.
- **Dynamic agent warning (21).** Test tooling that self-attaches an agent at
  run time prints the warning unless the agent is passed with `-javaagent` or
  `-XX:+EnableDynamicAgentLoading` is set. JEP 451 names serviceability tools;
  its reach into mocking libraries is an inference.
- **Scanners do not see the JVM** (observed in practice). The compile level is a
  compiler flag, not an artifact, so an SBOM or CVE scan built from the build
  descriptor never lists the JDK or JRE that runs. Only a base-image scan, of a
  base pinned closely enough to be reproducible, makes the runtime visible. See
  [`eclipse-temurin`](../container/eclipse-temurin.md).

## Testing
- Run the suite on the runtime that production uses, and on the newest LTS as
  well: denied reflection (JEP 403) and the dynamic-agent warning (JEP 451)
  appear only at run time. The failure modes are upstream facts; running both
  is advice.

## Security defaults
- The Security Manager cannot serve as a sandbox: deprecated for removal in 17
  (JEP 411), permanently disabled in 24 (JEP 486; the API remains for a later
  removal).
- Context-specific deserialization filters (17, JEP 415) let an application set
  the filter per call site through a JVM-wide filter factory.
- Dynamic agent loading is moving toward off by default for integrity
  (JEP 451).
- Strong encapsulation (17) closes reflective access to JDK internals unless a
  flag opens it; every `--add-opens` widens that again.

## Operational behaviour
- A project that does not take the quarterly update runs a JVM that upstream has
  already patched. LTS support has two parts that are easy to conflate: binaries
  that remain available (a floor of years, per distribution, which moves) and
  the quarterly security content (plant framing of the Temurin support page).
- Non-LTS releases leave support when the next release ships.
- Container-aware heap sizing is on
  [`eclipse-temurin`](../container/eclipse-temurin.md), under Install, setup and
  configuration.

## Interop
- **Spring.** Spring Framework 6 and Spring Boot 3 require Java 17 and
  Jakarta EE 9 or later; Framework 7 keeps the 17 baseline, moves to Jakarta EE
  11, supports JDK 17 to 25 and later, and its team recommends JDK 25 or later
  for production. The last Framework 5 line runs on JDK 8 to 21. Boot 4 requires Java 17 or
  later. Plan a language-level bump together with the framework major. See
  [`spring-framework`](../maven/spring-framework.md) and
  [`spring-boot`](../maven/spring-boot.md).
- **Maven.** The compiler plugin owns `release`, `parameters` and the processor
  path; toolchains let a build compile with a JDK other than the one running
  Maven. See [`maven`](../cli/maven.md).
- **Container base images.** The runtime build comes from the base image; see
  [`eclipse-temurin`](../container/eclipse-temurin.md) for its variants and pin
  discipline.

## Major lines
### Java 11
`var` (also in lambda parameters), the HTTP client, single-file launch. No
switch expressions, text blocks, records, `instanceof` patterns or sealed
classes. The Java EE and CORBA modules are removed. Illegal reflective access
is permitted with a warning by default.

### Java 17
Switch expressions, text blocks, records, `instanceof` patterns and sealed
classes are all available. Strong encapsulation (JEP 403). Security Manager
deprecated for removal (JEP 411), RMI Activation removed (JEP 407), the
experimental AOT and JIT compiler removed (JEP 410), the Applet API deprecated
for removal (JEP 398), strict floating-point semantics restored (JEP 306),
context-specific deserialization filters (JEP 415). Pattern matching for
`switch` is only a preview here (JEP 406).

### Java 21
Virtual threads, sequenced collections, record patterns, pattern matching for
`switch`, generational ZGC, and the dynamic-agent warning. Record patterns in
the header of an enhanced `for` were dropped before release. Unnamed patterns
and variables, string templates and scoped values are previews in 21.

### Between 21 and 25
JDK 23 stops running class-path annotation processors by default. JDK 24
removes most virtual-thread pinning on `synchronized` (pinning on native frames
and foreign calls remains) and permanently disables the Security Manager.

### Java 25
Scoped values, compact source files and instance main methods, flexible
constructor bodies, compact object headers, generational Shenandoah, and the
KDF API are final. Stable values, structured concurrency, primitive patterns
and PEM encodings are previews. The 32-bit x86 port is removed (JEP 503).

## Upstream docs
- https://openjdk.org/projects/jdk/ (per-release pages: `/17/`, `/21/`, `/25/`)
- https://openjdk.org/jeps/ (each JEP named above)
- https://docs.oracle.com/en/java/javase/21/docs/specs/man/javac.html and the 25 equivalent
- https://www.oracle.com/java/technologies/javase/23-relnote-issues.html
- https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html (class-file versions)
- https://docs.oracle.com/en/java/javase/17/migrate/ and the 21 equivalent
- https://adoptium.net/support/ (a distribution's support policy)
