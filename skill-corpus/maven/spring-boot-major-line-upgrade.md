---
name: spring-boot-major-line-upgrade
description: Move a Spring Boot codebase across major lines (or to the last line of its current major) with behavior preserved, gated against the silent break classes. Invoke when a Boot line reaches end of support, an advisory is fixed only on a newer major, or a ported service builds green but lost a capability.
id: skill.spring-boot-major-line-upgrade
tier: 2
kind: skill
title: spring-boot-major-line-upgrade, the Spring Boot specialization of framework-version-migration
owns:
  - spring-boot-major-line-upgrade.danger-classes
  - spring-boot-major-line-upgrade.procedure
  - spring-boot-major-line-upgrade.gate-set
  - spring-boot-major-line-upgrade.pitfalls-by-major-line
requires:
load_when:
  - "upgrade spring boot to the next major line, migrate off boot 2 or boot 3"
  - "javax to jakarta namespace move, spring security dsl migration"
  - "the service builds green after the boot upgrade but something stopped working"
  - "gate a spring boot port before deploy"
stack:
  - library-corpus/maven/spring-boot
est_tokens: 5200
---

# Suggested skill: spring-boot-major-line-upgrade

> Optional procedure, **stack-keyed**: withdrawn only where the plant's build
> declares Spring Boot on a line older than the one it must reach. It
> specializes `skill-corpus/framework-version-migration.md`, which owns the
> generic sequence (characterize first, staged increments, codemod
> completeness, consumer enumeration, the intended-delta allowlist, the ADR
> with its fallback trigger). This page restates none of that and carries only
> what Spring Boot adds: where its breaks hide, the order its build graph
> imposes, the gates that catch its silent failures, and the proof after
> deploy. Composes `verify` and `verify-disagreement`, `test-first`,
> `adr-writer` and `security` by reference, plus the tools
> `tool-corpus/ops/renamed-config-key-auditor.md` and
> `tool-corpus/ops/container-deploy-pipeline.md`. Each library's own API diff
> stays on its library page and in the plant's `ingest-library` pass.
> Parameters: `<source-line>`, `<target-line>`, `<cloud-train>` (where Spring
> Cloud is used), `<rollout>` (lockstep, or one unit at a time).

## When to apply

- The Boot line in use is at or past the end of open-source support, or an
  advisory is fixed only on a newer major, and the application must behave
  afterwards as it did before.
- The hop to the last line of the *current* major (the same-namespace
  ceiling, Step 0) is covered too: it breaks in the same silent ways and takes
  the same gates.
- Not for a patch bump inside one line: the BOM carries that, and the library
  page owns it.

This procedure ONLY moves a Spring Boot codebase across lines while preserving
behavior; hardening or feature work that rides along is a separate, named
increment with its own intended-delta rows, because a mixed diff hides which
change moved a behavior.

## The shape of the danger

**A Boot hop fails silently.** The build goes green, the container reports
healthy, and a capability is gone. Six classes recur, and the gate set is
planned around them, not around the compile:

1. **A configuration key renamed or removed.** Boot ignores a key it does not
   know, the default applies, and the service still starts: a datastore client
   falls back to its localhost default, a raised limit drops back, a gateway
   binds zero routes.
2. **Path matching changed.** A security whitelist entry matches more or less
   than it did, or a trailing-slash path stops matching.
3. **The wire shape changed.** A serialization default or the JSON library's
   major moved, so output differs while every test that does not freeze the
   bytes passes; a customizer written for the old JSON line compiles and is
   inert.
4. **Present but not auto-configured.** Libraries sit on the classpath without
   the starter that carries their auto-configuration, so no bean is created and
   nothing reports it.
5. **Context assembly.** A bean injected off any request path no longer
   exists, so the application context does not start. This one is loud, but
   only after deploy if the gates never assemble a context.
6. **The ORM behaves differently for the same call.** A merge, a generated
   DDL statement, or a dialect lookup that worked on the old ORM major does
   something else on the new one.

## The procedure

### Step 0 — Choose the target line and the ceiling

Replaces "take the newest line" and "take the next line".

- **Read each candidate line's support window** (the generic page, step 0).
  A line past its open-source end can still serve as the build line of an
  in-house library in transit (Step 1).
- **With Spring Cloud, the train is a binding constraint.** The train's own
  release statement can bless a newer Boot line than the Boot version its BOM
  manages by default. Declare Boot through the starter parent, import the
  train BOM for the Cloud artifacts only, and record the train's default Boot
  line as the fallback, with the build-resolution gate as its trigger, in the
  ADR the generic page requires.
- **The first source-incompatible break is the namespace break.** The
  generic page's step 0 splits the jump there into two tiers. For Boot, the
  last line of the source major that keeps `javax.*` is the first tier; the
  namespace layer is owed whatever the final target, and each later major
  adds its own layer (see Pitfalls by major line).
- **The JDK floor.** Raise the JDK to the target line's minimum or above, as
  its own first increment. Prefer the most mature long-term-support JDK at or
  above the floor over the newest; a newer one is a reversible follow-up once
  the migration is green.

### Step 1 — Order the build graph

Replaces "bump the application first and see what breaks".

- **In-house artifacts compiled against the framework are co-upgrades.** A
  shared module, an internal library, or a vendored jar that declares the Boot
  parent or imports its BOM is rebuilt in dependency order, upstream first,
  and republished or re-vendored before any consumer builds against it.
- **Across the namespace break this is mandatory**: a jar compiled against
  `javax.*` does not link into a `jakarta.*` application. **Within a
  same-namespace hop** the consumer's BOM decides the runtime classpath, so an
  in-house jar compiled against the older line still runs; record it as a
  known divergence, not as upgraded.
- **Rollout and shared libraries** follow the generic page's step 4 (one
  release line per generation behind one entry signature; lockstep when the
  estate cannot run mixed). For Boot, a consumer that has to rewrite its own
  security chain to adopt the library cannot roll back alone, and one unit at
  a time also needs a wire shape pinned across lines and served configuration
  both lines can read (Step 5).

### Step 2 — Baseline what Boot can lose

The Spring specifics of the generic page's characterize-first step.

- **The by-name suite record** (generic page, step 1) is built in the same
  JDK with the same dependency cache, never from the working copy.
- **Every gate in Step 6 is run green on the pre-migration commit** before it
  counts (generic page, step 1); run a guard written after the port began in
  a detached worktree at the baseline commit.
- **The external witnesses** (generic page, step 1) for a Boot service are
  trace export at the collector, the metrics scrape, broker bindings and
  discovery registration. An in-memory collector keeps nothing across
  restarts, so the time stamp is what makes a reading usable.
- **Freeze the wire**: serialization fixtures per payload family, covering
  responses and the bodies one service sends another, plus the
  unknown-field, absent-field and null-field outcomes.
- **Snapshot the security and operations surface**: the whitelist read back
  from the real security configuration, the exposed Actuator endpoints, and
  the reference database schema as DDL.

### Step 3 — Build-file delta

Replaces "change the parent version and rebuild".

- **Parent or BOM to the target line, and the matching Cloud train.** Then
  delete the property overrides the old parent needed.
- **A `<property>` version override applies through parent inheritance and
  not to an imported BOM.** A module that imports the BOM needs explicit
  `dependencyManagement` for the same override. An advisory override dropped
  in passing regresses silently, so diff the resolved tree, not the pom.
- **Remove build-command version overrides** (`-D<lib>.version=…`) that fight
  the BOM; one can break the BOM import outright.
- **A coordinate that moved** (a new group or artifact id) falls out of the
  BOM's management: change the coordinate, not the version.
- **Prefer the starter to hand-declared runtime libraries.** Declaring a
  capability's libraries without its starter reproduces danger class 4.
- **Companion libraries pinned to the old line have majors of their own**: the
  API-document generator, the JWT library, the circuit-breaker starter, a
  query-class generator's classifier. Each is its own increment, and its
  library page owns its API diff.
- **A transitive jar the old line brought can vanish** (an annotation jar is
  the usual one). Replace the usage with the framework's own equivalent rather
  than re-declaring the dead transitive.
- **Gate:** resolution, then assertions over the resolved tree (the weaver
  that annotation-driven resilience needs is present, excluded serializers are
  absent, moved coordinates resolve), then compile.

### Step 4 — Source delta

- **Run the mechanical rewrite with a recipe tool, then hand-finish.**
  OpenRewrite's Maven plugin runs a recipe without editing the build:
  `mvn -U org.openrewrite.maven:rewrite-maven-plugin:<plugin version>:run -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-spring:RELEASE -Drewrite.activeRecipes=<recipe id>`,
  with the upgrade recipe for the target line (the
  `org.openrewrite.java.spring.boot<major>.UpgradeSpringBoot_<major>_<minor>`
  family) or `org.openrewrite.java.migrate.jakarta.JavaxMigrationToJakarta`
  for the namespace alone. `run` edits sources in place, so start from a
  clean commit and review the diff; `dryRun` writes a patch under each
  module's `target/` instead. These recipes are published under the Moderne
  Source Available License, not an open-source licence, and where they are
  published can change: check the recipe's current licence and where it is
  published, and that the coordinates resolve, before planning on them. Observed in
  practice, the recipe output still needed a hand-finish: security rules
  whose meaning changed while their name stayed, the JSON-library policy,
  and package moves the recipe did not cover. The gates below prove the
  result; the recipe run proves nothing by itself.
- **Move `javax.*` to `jakarta.*` for the moved specifications only**, test
  sources included. The moved set is the Jakarta EE 9 namespace list; copy it
  from the definition of the `JavaxMigrationToJakarta` recipe (its
  `jakarta-ee-9` recipe file in `rewrite-migrate-java`) rather than from the
  codebase's own imports. The ones most codebases hit are persistence,
  validation, servlet, transaction, mail, XML binding, REST, and the
  annotations directly in `javax.annotation` (`PostConstruct`, `PreDestroy`,
  `Resource`, `Priority`, `Generated`). The list also holds `javax.inject`,
  `javax.annotation.security` (`RolesAllowed`, `PermitAll`, `DenyAll`),
  `javax.annotation.sql`, `javax.activation`, `javax.websocket`, `javax.jms`,
  `javax.json`, `javax.el`, `javax.ejb`, `javax.enterprise`,
  `javax.interceptor`, `javax.batch`, `javax.decorator`, `javax.resource`,
  `javax.xml.soap`, `javax.xml.ws`, `javax.jws`, `javax.security.enterprise`,
  `javax.security.jacc` and `javax.security.auth.message`. The Java SE
  `javax.*` packages stay (`javax.sql`, `javax.crypto`, `javax.naming`,
  `javax.xml.parsers`, `javax.annotation.processing`; `javax.security.auth`,
  `javax.security.cert` and `javax.security.sasl` while their sibling
  `javax.security.auth.message` moves; and `javax.transaction.xa`, which
  stays in Java SE while the rest of `javax.transaction` moves), and so do
  non-Jakarta annotation jars that only share the prefix (the nullness
  annotations `javax.annotation.Nonnull` and `Nullable`, and
  `javax.annotation.concurrent`). Run the census inside every repository
  or module that builds (generic page, step 3). **A validation
  annotation left on the old namespace compiles and never runs**: prove a
  malformed input still gets its pre-migration rejection, including a value
  that violates its real domain bound and not merely null.
- **Gate the namespace with a static search, not with the compile.** The gate
  passes when, across every module's sources, no reference to the moved set
  remains (imports and fully qualified names in code alike), no file holds
  both the old and the new path of one specification, and every module that
  validates input still carries its `jakarta.validation.constraints`
  annotations (a rename, never a deletion). Match the moved set exactly: a
  pattern widened to all of `javax.*` flags the Java SE packages above and
  invites a wrong fix. The compile is a diagnostic beside the gate, because
  later increments (the security DSL, a companion library's major) still
  break it by design; a compile error that is itself a namespace error flips
  the gate.
- **Auto-configuration package moves**, in test imports too, and the
  customizer classes of the JSON library.
- **Security configuration**: the adapter base class gives way to a
  `SecurityFilterChain` bean; `authorizeRequests` → `authorizeHttpRequests`;
  `antMatchers`/`mvcMatchers` → `requestMatchers`; `@EnableGlobalMethodSecurity`
  → `@EnableMethodSecurity` (the old annotation is deprecated, and current
  releases keep it only with an extra access module), and add
  `@Configuration` beside `@EnableWebSecurity` and `@EnableMethodSecurity`,
  which stopped implying it. Keep the rules in first-match order with
  `anyRequest` last and a `denyAll` catch-all; express public paths with
  `permitAll`, not with the ignoring API; permit the FORWARD and ERROR
  dispatcher types explicitly where error pages forward, because authorization
  now applies to every dispatch type. Rewrite each whitelist entry into
  path-pattern syntax no broader than before; a suffix glob such as `/x**`
  does not mean what it did. Where the security code is copied across units,
  diff the copies after each increment.
- **Removed framework APIs**: the status type in exception handlers, removed
  URI-builder factories, metrics tag providers replaced by an
  observation-convention bean.
- **Delete unused imports** rather than rewriting them.

### Step 5 — Configuration surface

Replaces "it started, so the config is fine".

- **Run `renamed-config-key-auditor` against the destination classpath, after
  confirming that the module owning each key is on that classpath.** An audit
  over a classpath missing a starter classifies that starter's keys by hand,
  and gets them wrong.
- **Close every reported key through a named channel**: the served
  configuration, a deployment-layer override, or the module's own file. An
  override carries the condition that retires it, and the override's own key
  is checked against the destination metadata, because an override can itself
  be a removed key.
- **Cover what the audit cannot see**: companion frameworks' renames (a
  gateway's route-property prefix), removed *values* (a dialect class named in
  a property), and keys whose raised value was the point (a request-header
  limit).
- **Defaults that flipped**: circular bean references refused, trailing-slash
  matching gone, the path-matching strategy, the JSON mapper. Restoring an old
  default with its escape property is an intended-delta row with a retirement
  condition, never a silent fix.
- **Pin Actuator exposure explicitly per unit** rather than inheriting a
  line's default, and assert the sensitive endpoints stay closed.
- **A wildcard CORS origin with credentials is refused**: enumerate the
  origins, and never escape through the origin-pattern wildcard.
- **Served configuration in a mixed estate**: a config server serving old
  keys to a new binary is an incompatible pair that nothing reports. Serve
  both keys through the transition: add the new key beside the old one at the
  source, because each line's binary ignores the other line's key, so one
  served file is correct for both. A unit that migrates before that rename
  lands gets a deployment-layer override in the same commit as its version
  bump, because that is the one channel the unit owns. A dual-served
  credential is two copies of one secret: keep credentials on the override
  channel, or serve the second name as a reference to the first. Deleting the old key is the one
  irreversible step and comes last, after a guard shows that no unit still on
  the old line reads it; the test that pinned the old key is retired in that
  same commit.

### Step 6 — The gate set

Every gate is RED by mutation (`verify`) and green on the pre-migration
commit (Step 2).

| Gate | Catches |
|---|---|
| Static namespace gate (Step 4), run on every module | a reference left on the moved namespace, a dual path, a dropped constraint annotation |
| Configuration-binding test, no container runtime needed | a key that stopped binding (class 1) |
| Context-assembly test: the full application context starts | an off-path bean that kills startup (class 5); a binding gate does not prove boot |
| Connectivity integration test against a real instance, asserting the **resolved host**, not mere reachability | a datastore silently pointed at localhost |
| Capability-wiring test: a live, non-no-op bean per auto-configured capability, plus the endpoint key this line binds | a library present but not auto-configured (class 4) |
| Whitelist-closure test, read by reflection from the real security configuration | a path opened or closed by the matcher change (class 2) |
| Frozen-fixture serialization golden, byte-identical, for responses and inter-service request bodies | a wire-shape change (class 3) |
| Route-table binding test, plus a drift test while the route table has two homes | a gateway healthy with zero routes |
| DDL diff against the reference schema; insert-versus-update on entities that arrive over the wire | ORM behavior change (class 6) |

**Gate-framework traps** (the generic rule, that a skipped gate is not a
pass, is `verify`'s):

- In a Maven build, `*IT` classes run only in modules that bind the failsafe
  plugin. An integration test added as a migration gate in a module without
  that binding never executes.
- A container-test client older than the container engine's minimum API
  reports "no container runtime", and every runtime-guarded test skips on a
  host that has one. Tell this apart from the honest skip on a host without a
  runtime.
- An assumption-guarded test skips when run as root. Convert each such guard
  into a failure that names the missing precondition.

### Step 7 — Deploy and post-deploy proof

`container-deploy-pipeline` owns deploy and rollback; these are the Boot hop's
additions.

- **Record the running image's immutable reference before building the new
  one**, as `core/method/release-posture.md` already requires before each
  release: a rollback tag taken after the build can name the broken image.
- **Read the bundled library list inside the running artifact.** A failed
  image build can leave the old image running behind a deploy log that reports
  success.
- **Run the estate's post-deploy gate**, extending its per-unit expectations
  in the same change; otherwise it fails the deploy it was meant to confirm.
- **Take the external capability reading again**, with its time, and compare
  it with the Step 2 reading; with no before-reading, compare against a unit
  still on the old line.
- **In a mixed estate, sweep unauthenticated access across both lines in one
  run**, so the estate is asserted as a whole.

## Pitfalls by major line

Each section holds what a crossing of that boundary has been seen to break.
Key and class names are illustrations of a class, not a checklist; the
destination's own metadata and migration guide are the list.

### MAJOR-LINE 2 → the last 2.x line (the same-namespace ceiling)

- Circular bean references are refused by default.
- The default path-matching strategy moved to the path-pattern parser. An
  API-document generator built on the old matcher can fail even with the
  documented compatibility flag set; treat the flag as a hypothesis until the
  application boots with it, and plan the generator's replacement.
- The JDBC driver coordinate moved and the old one fell out of management.

### MAJOR-LINE 2 → 3 (the namespace layer, paid whatever the final target)

- `javax.*` → `jakarta.*`; the JDK floor rises; the Security DSL renames and
  the adapter's removal (Step 4).
- Trailing-slash matching is removed: audit HTTP clients and gateway routes,
  and restore per mapping only where a client depends on it.
- The tracing integration is replaced: a tracing facade plus a bridge plus a
  reporter in place of the old starter; custom metric tags move to
  observation conventions; no old tracing coordinate or key may remain.
- The ORM major arrives. Version-specific dialect classes are removed (this
  fails at startup, which is the lucky case). A merge on an entity whose
  identifier arrived non-null over the wire with no local row issues an update
  that matches nothing and throws, where the old major inserted; for a
  message-carried entity, insert by natural key and ignore the wire
  identifier. Under `ddl-auto: update`, diff the emitted DDL against the
  reference schema.
- Datastore key families are renamed (for example `spring.redis.*` to
  `spring.data.redis.*`), and so is the request-header-size key.
- Actuator masks sensitive values by default; pin the exposure anyway.
- A query-class generator needs its `jakarta` classifier.

### MAJOR-LINE 3 → 4

- **The default JSON library becomes the next Jackson major, and both lines
  ship.** A customizer for the old line is inert under the new default and its
  class moved package. Choose the policy for the whole estate in an ADR. To
  stay on the old line, declare the old line's support module and set the
  preferred-mapper property **on every participant of an inter-service
  call**. The reactive stack reads a different key from the servlet one, so a
  reactive gateway is the participant a servlet-only sweep misses (the module
  and both keys: `library-corpus/maven/jackson.md`). A partial pin puts a new-line encoder
  on one side and an old-line decoder on the other, and they disagree on
  property names (accessors with all-caps or version-sensitive names are the
  signature; plain camelCase is unaffected). Staying holds only while the old
  line receives security patches.
- **Auto-configuration is split into per-technology modules.** A capability
  whose libraries are declared without the matching starter gets no
  auto-configuration (tracing is the measured case).
- **More keys move**: datastore families again, the tracing exporter's
  endpoint, and the gateway's route-property prefix (which leaves the gateway
  healthy with zero routes).
- Companion API-document beans change shape, so an off-path injection of one
  fails context assembly.
- **Paged responses can change shape.** Observed in practice after a 3 → 4
  hop: a paged endpoint that serialized the data library's page type directly
  rendered its sort descriptor as a JSON array where the old line rendered an
  object, and the page-serialization mode property alone did not restore it;
  pinning the HTTP mapper to the old JSON line did. Spring Data's reference
  documentation recommends against letting Jackson render a returned `Page`
  as is, because `PageImpl` is a domain type whose JSON can change in a
  breaking way for unrelated reasons. It offers `PagedModel` as the stable
  shape, and `@EnableSpringDataWebSupport(pageSerializationMode = VIA_DTO)` to
  translate every returned page into it. The frozen-fixture golden (Step 6) is what catches
  the change either way.

### General, any line

- Raising the JDK can break an annotation processor that patches compiler
  internals. Observed in practice, one project: the processor was already on
  its newest release and still crashed the in-process compiler; a forked
  compiler invocation fixed it. Upstream's documented setup is the explicit
  processor path, which newer JDKs require anyway, so try that first
  (`library-corpus/maven/lombok.md`).

## What it does not cover

- The estate-wide serialization policy, which is an ADR each unit inherits.
- Host, image and build-cache mechanics (`container-deploy-pipeline`).
- Each library's own API diff (its library page; `ingest-library` for the
  pins).

## Reference files

- `skill-corpus/framework-version-migration.md` (the generic sequence this
  specializes)
- `protocols/verify.md`, `protocols/verify-disagreement.md` (RED by mutation,
  behavior preservation, the effective state)
- `protocols/test-first.md` (characterization tests as the RED spine)
- `skills/adr-writer/SKILL.md` (target line, fallback trigger, the
  serialization policy)
- `agents/05-security.md` (advisory gate on the target)
- `tool-corpus/ops/renamed-config-key-auditor.md`
- `tool-corpus/ops/container-deploy-pipeline.md`
- `library-corpus/maven/{spring-boot,spring-cloud,spring-security,hibernate-orm,sleuth-zipkin,springfox,springdoc-openapi,resilience4j,jjwt,querydsl,jackson,micrometer-tracing,testcontainers,spring-cloud-gateway,mysql-connector-j}.md`
