---
stack:
  - library-corpus/maven/spring-boot
---
# Tool: renamed-config-key-auditor

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the capability, the
> oracle choice, the interface shape and the flattening rule are portable; the
> parsing of the project's own configuration documents is written against
> whatever formats the adopting project serves.

## 0. Identity

- **Category:** ops
- **Name:** renamed-config-key-auditor
- **Language / runtime:** any (an HTTP client, a reader for the project's
  configuration documents, and a parser for the vendor's published catalogue
  are the whole requirement)
- **Stability:** **blueprint**. No portable implementation ships here. Reading
  the configuration a project actually serves means parsing nested documents,
  and the formats configuration is usually written in are rarely covered by a
  language's standard library. A self-contained implementation would therefore
  have to supply its own configuration parsing, which is real work an adopting
  project should budget for before it starts. Everything above the parser is
  portable and is the value of the page.

## 1. What it does

Before a framework's major-version jump, answers which of the configuration
keys a project actually serves the target generation will **silently ignore**.

Frameworks that bind configuration by key name usually accept an unknown key
without complaint. The key is read, matched against nothing, and the default
applies. The service starts, reports healthy, and behaves as though the setting
had never been written. Nothing fails, which is why this class of defect is
found in production rather than in a gate: a timeout that reverted to its
default, a pool size nobody set, a feature toggle that has quietly been off
since the upgrade.

The tool exists because the configuration and the framework version move
independently, and the framework has no interest in telling anyone. A key that
was correct for one generation stays in the file, looking correct, long after
the generation that read it is gone.

## 2. Interface & invocation

```sh
renamed-config-key-audit \
  --root <root of the configuration the project actually serves> \
  --from <source generation> --to <target generation> \
  [--classpath <the destination build's resolved artifacts>] \
  [--json]
```

- **Inputs:** two required, one optional. The **root of the served configuration**
  (whatever the project really serves: a directory of files, a mirror pulled
  from a configuration server, a bundled resource tree) and the **source and
  target generations** of the framework. Both are required and
  neither has a default; a default root is how a tool becomes unshareable, and a
  default generation pair is how it becomes wrong. Optionally, the
  **destination classpath** (the artifacts the migrated build resolves), which
  turns on the metadata oracle (§3); it has no default either.
- **Outputs:** one row per served key the target generation will ignore, each
  naming the key, the file it was found in, and the **vendor's own verdict**
  for it: renamed to some other key, removed outright, or superseded by a
  different mechanism. The verdict is quoted from the catalogue rather than
  inferred, so a reader can check it at the source. Each row names the oracle
  that produced it; with a classpath, a served key that no metadata on that
  classpath declares (compared in canonical form, §3) is listed apart as
  unaudited.
- **Exit codes:** non-zero when the set is non-empty, so the tool is usable as a
  pre-migration gate and not only as a report.
- **Preconditions:** the configuration root is readable; the vendor's catalogue
  for the two generations is reachable and parseable.

## 3. Approach / algorithm

### The vendor's catalogue is the oracle

The tool does not pattern-match key names, and it carries **no rename list of
its own**. A hand-kept list is wrong the day after it is written, and worse, it
is wrong silently: it keeps returning clean results for the renames nobody
remembered to add.

Instead the tool fetches the **framework vendor's own published, machine-readable
changelog of renamed and removed configuration keys** for the two generations in
question, and uses that as its oracle. Where a vendor publishes no such
catalogue, the tool has no oracle, and it says so and stops rather than
degrading into a guess dressed as a finding.

This is the same discipline its two nearest neighbours follow, and the three
differ only in which authority they ask. One asks a live credentialed store
whether a declared name exists there; one asks the configuration system's own
resolver what a layered configuration resolves to; this one asks the vendor what
it renamed.

### A second oracle: configuration metadata on the destination classpath

Some frameworks also publish the same knowledge **per artifact**, inside each
library jar, as machine-readable configuration metadata. Spring Boot is the
worked example: each jar can carry `META-INF/spring-configuration-metadata.json`,
whose properties may hold a `deprecation` object with a `level` and a
`replacement`. Upstream defines the levels: `warning` (the default) means the
property "should still be bound", and `error` means it "is no longer managed
and is not bound". A served key whose metadata says `level: error` is a key
the framework ignores, which is exactly this tool's finding, and the
`replacement` is the vendor's verdict to quote.

This oracle covers what a single changelog cannot: every library that ships
metadata, including companion frameworks, at the exact versions the target
resolves. Its rule is strict: **read the metadata from the destination
classpath, the one the migrated build will resolve**, not from the current
build. To get it, resolve the migrated build's artifacts with the destination
POM (`mvn dependency:copy-dependencies`, or `dependency:build-classpath` for
the list of paths; the capture rules are on
`tool-corpus/ops/resolved-dependency-gate.md`) and read
`META-INF/spring-configuration-metadata.json` from each jar. The audit cannot
know which module owns a key whose module is absent. What it can compute is
which served keys no metadata on that classpath declares: those are
unaudited, never clean. A module the migration will add but has not yet
declared is the usual cause.

Use both oracles when both exist, and report which one produced each row.
Spring Boot also ships a runtime form of the same check,
`spring-boot-properties-migrator`, which reports renamed keys at startup and
remaps them temporarily (`library-corpus/maven/spring-boot.md`); it sees only
the keys a started application actually loads, so it complements an offline
audit and does not replace it.

### Flatten before you compare

1. Fetch and parse the catalogue into old-to-new pairs, keeping each entry's
   verdict text. Drop a self-mapping row (old key equals new key), and keep a
   removed key (empty replacement) as a finding with no replacement.
2. **Flatten every configuration document under the root to fully-qualified key
   paths.** This is the step people get wrong. A nested document hides a key
   from any search that reads the file as lines, and a key that appears at two
   different depths is two different keys even when its leaf name is identical.
   The served key set is the set of fully-qualified paths, and the comparison is
   meaningless until the flattening is complete.
3. **Compare in canonical form.** A served key can be spelled in camelCase
   or snake_case (Spring Boot binds them relaxed), carry list indices
   (`servers[0].host`), or sit under a map-typed property that metadata
   declares once (`logging.level` covers `logging.level.<logger>`). Bring both
   sides to the canonical form (lower case, kebab-case, list indices dropped)
   and treat a map-typed metadata property (its `type` is a `java.util.Map`)
   as a prefix. Without this, such keys are all reported unaudited, or missed.
4. Intersect the served key set with the catalogue's retired set.
5. Report the intersection, each row carrying its file and the vendor's verdict.

### Enduring idioms

- **Run it against the destination generation before the migration lands**, not
  after. The whole value of the tool is being the gate that fires while the
  change is still cheap to make; run afterwards, it is an incident report.
- **One generation hop per run.** A key renamed twice appears on the retired
  list only under the hop that retired it, so a single query spanning several
  generations loses the middle steps and reports fewer findings than exist. Walk
  the hops in order and take the union.
- **Record which catalogue version answered.** The result is only as good as the
  catalogue behind it, and a reader six months later needs to know which one that
  was.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the choice of oracle and the refusal to keep a
  rename list; the two-input interface with no defaults; the fully-qualified
  flattening rule; the one-hop-per-run idiom; reporting the vendor's verdict
  rather than a derived one; the non-zero exit that makes it a gate.
- **Portable too:** reading per-artifact metadata from the destination
  classpath, the canonical-form comparison, and listing a served key that no
  metadata declares as unaudited.
- **Write per project:** the reader for the configuration documents the project
  serves, and the fetch and parse of the vendor's catalogue format. Both are
  format-bound, and the configuration reader is the larger of the two.
- **Adopting note:** a project whose configuration is served from a
  configuration server rather than from files needs the root to address that
  server's view, not a local checkout of it. The two drift, and the served one
  is the one the framework reads.

## 5. Pitfalls and sharp edges

- **A clean run is not proof the configuration is correct.** It proves exactly
  one thing: no served key is on the vendor's retired list. A key that was never
  valid passes. A key that is still valid but now means something different
  passes. Say what the green means in the tool's own output, so a reader cannot
  inflate it.
- **The catalogue is the vendor's, and it is incomplete by construction.**
  Vendors record the renames they chose to record, and a generation whose
  catalogue is thin will produce a thin result that looks identical to a clean
  one. Report the catalogue version alongside the findings and read an empty
  result against a sparse catalogue as weak evidence.
- **Serving a key is not the same as the framework reading it.** A key under a
  profile that never activates is served and never bound, and the tool has no way
  to know which profiles a deployment selects. It reports served keys; an
  operator reads the result knowing that, and the report says so rather than
  leaving it to be assumed.
- **A classpath audit is only as complete as the classpath it read.**
  Observed in practice: an audit over a large resolved classpath that lacked
  one tracing module classified that module's endpoint key by hand, called a
  deprecated spelling (metadata `level: error`) correct, and the deployment
  then set a key that bound nothing. The fix is mechanical: treat a served key
  that no metadata on the read classpath declares (after the canonical-form
  comparison) as unaudited, never as clean, and resolve the classpath from
  the destination POM so the missing module appears.
- **One vendor's catalogue does not cover its companions.** A framework's
  changelog records its own renames. Renames in companion frameworks (a cloud
  or gateway layer, a client library with its own prefix) and in third-party
  libraries are outside it, and so outside a clean run. The metadata oracle
  covers those that ship metadata; the rest need their own release notes.
- **A removed value is not a renamed key.** A configuration value that names
  a class (a dialect, a driver, a strategy) can be removed while its key stays
  valid. Neither oracle checks values, so a key-clean run can still start a
  service that fails at its first use of that class. List the keys whose
  values are class names, and check each value against the target's own
  release notes.
- **A parser that returns nothing must fail.** If the vendor changes the shape
  of its published catalogue, a scraper returns an empty map and the audit
  reports "no stale keys". Pin the parser with a test over a saved copy of the
  catalogue, and refuse a run whose catalogue parsed to zero entries.
- **A removal is not always a rename.** Where the catalogue says a key was
  superseded by a different mechanism, there is no replacement key to write and
  the fix is a design change. Reporting those rows in the same shape as the
  renames invites someone to look for a new key that does not exist.

## 6. Tests that cover it

Cover: a served key on the catalogue's retired list is reported once, with its
file and the vendor's verdict; a served key absent from the catalogue is not
reported; a key nested several levels deep is found and reported at its
fully-qualified path; the same leaf name at two different depths yields two
distinct keys and is not collapsed; an unreachable or unparseable catalogue
refuses the run rather than reporting a clean result; an empty finding set exits
zero and a non-empty set exits non-zero; a multi-generation jump run as a single
query is proven to miss a twice-renamed key that the per-hop runs find; a
metadata entry with `level: error` is reported with its `replacement`, and one
with `level: warning` is not; a served key that no metadata on the classpath
declares is reported as unaudited; a camelCase, snake_case or indexed
spelling and a key under a map-typed property match their metadata entry; a
self-mapping catalogue row is dropped and a removed key is kept; a catalogue
that parses to zero entries refuses the run.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/declared-variable-existence-auditor.md`
  (asks a live store whether a declared name exists there, which is a different
  authority answering a different question);
  `tool-corpus/ops/layered-config-merge-verifier.md` (asks the configuration
  system's own resolver what a layered configuration resolves to, and owns the
  guard-strength questions this tool does not touch).
- **Library page:** `library-corpus/maven/spring-boot.md` (unknown keys bind
  nothing; the properties migrator).
- **Sources:** distilled from practice; the catalogue it reads
  is the framework vendor's own configuration-changelog publication, named by the
  adopting project rather than by this page. For the metadata oracle: Spring
  Boot, "Configuration Metadata", metadata format and the `deprecation` levels
  (<https://docs.spring.io/spring-boot/specification/configuration-metadata/format.html>);
  Spring Boot, "Externalized Configuration", relaxed binding and the
  canonical kebab-case form
  (<https://docs.spring.io/spring-boot/reference/features/external-config.html>).

## 8. Changelog

- 2026-09-22 — created by docs-librarian.
  Ships as a blueprint: an implementation needs a third-party parser, so no
  portable script travels with the page.
- 2026-10-05: enriched by tool-smith: the second
  oracle (per-artifact configuration metadata on the destination classpath)
  and four pitfalls (classpath completeness, companion frameworks, removed
  values, an empty parse).
- 2026-10-05: review fixes. The comparison now states its canonical form
  (relaxed spellings, list indices, map-typed properties as prefixes). The
  unaudited rule says what the tool can compute: a served key that no
  metadata declares. How to obtain the destination classpath, the catalogue
  parser's treatment of self-mapping and removed rows, and the `stack:`
  field are added.
