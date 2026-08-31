# mapstruct — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A compile-time Java bean-mapping framework. You declare a mapping as a `@Mapper`
interface, and an annotation processor generates the implementation at build time
(for example, entity↔DTO conversion). Because the mapping code is generated and
plain, there is no runtime reflection and the mapping is visible, debuggable Java.

## Core API / usage shape
- **`@Mapper` interfaces**: declare the source and target types and any field-level
  mapping rules; the processor emits a concrete implementation class.
- **Generated implementations**: the generated impl does the field-by-field copy;
  it is ordinary Java, so it can be read and stepped through.

## Idioms & best practices
- The common shape is one mapper per entity, acting as an explicit DTO boundary
  layer: it keeps the transport/service tier decoupled from the shared domain
  model instead of leaking entities across tiers.

## General pitfalls
- **Annotation-processor order is load-bearing when paired with an
  accessor-generating processor.** When another processor generates the accessors
  MapStruct maps against (for example, a getter/setter/builder generator), the
  processors share the compile phase and ORDER matters. Without the binding that
  teaches the mapper about the generated accessors, the generated mapper can
  silently ignore those fields and produce null or blank output — with no compile
  error. Whenever two codegen tools share the compile phase, verify the processor
  chain and the binding between them rather than assuming defaults line up.

## Upstream docs
- https://mapstruct.org/
