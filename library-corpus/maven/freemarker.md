# freemarker — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Apache FreeMarker, a general-purpose Java template engine that merges a
template with a data model to produce text output — HTML pages, email bodies,
config files, or any other text. The canonical Maven artifact is
`org.freemarker:freemarker`; Spring applications often pull it in transitively
via `spring-boot-starter-freemarker`.

## Core API / usage shape
- Author templates as separate `.ftl` resource files containing literal text
  interleaved with FreeMarker directives and interpolations.
- At runtime a `Configuration` object holds engine settings and a template
  loader; it hands back a `Template` for a named `.ftl`.
- `Template.process(dataModel, writer)` merges the template against a data
  model (commonly a `Map`, or beans) and writes the rendered text to the
  supplied writer.
- It can be used purely for text or email generation with no web-MVC view
  layer involved.

## Idioms & best practices
- Keep templates as separate resource files, distinct from Java code, so
  presentation can change without recompiling.
- Drive rendering from a data model passed at render time rather than
  hardcoding values into templates.
- Reuse a single configured `Configuration` instance rather than reconstructing
  it per render.

## General pitfalls
- Missing or misspelled template parameters are caught only at render time as
  runtime errors — template correctness is not compile-checked, so a mismatch
  between the model and what the template references surfaces late unless
  templates have explicit rendering tests exercising each template with a
  representative model.

## Upstream docs
- https://freemarker.apache.org/
- https://freemarker.apache.org/docs/
