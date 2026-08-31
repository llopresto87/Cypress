# typescript — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
TypeScript is Microsoft's typed superset of JavaScript and its compiler (`tsc`),
distributed as the `typescript` npm package (usually a dev dependency). It adds
static types over JavaScript and emits plain JavaScript. Type-checking behavior
is configured through `tsconfig.json`.

## Core API / usage shape
- **Strict mode** (`strict: true`) is the recommended baseline, enabling the
  family of strict null/type checks.
- **`import type`** (type-only imports) is the correct pattern under
  `isolatedModules: true`, which requires unambiguous type-only imports so each
  file can be transpiled independently.
- **`moduleResolution`** selects how imports are resolved; the `bundler` setting
  targets bundler-based builds rather than Node's own resolution algorithm and
  pairs naturally with `isolatedModules` / `importHelpers`.

## Idioms & best practices
- Enable `strict` from the start of a project rather than retrofitting it.
- Use `import type` / `export type` under `isolatedModules` (and with
  single-file transpilers) to keep type-only references from affecting emit.
- Pick `moduleResolution` to match the actual build pipeline (bundler vs. Node).

## General pitfalls
- **A compiler bump is a source-breaking event by design.** Both the `lib.d.ts`
  type hierarchy (e.g. relationships between `ArrayBuffer` and TypedArrays like
  Node's `Buffer`) and generic type-argument inference are refined across
  releases, so previously-clean code can start failing to compile without any
  source change. The usual fixes are realigning the ambient type packages
  (`@types/node`) and making the implicit explicit — explicit element types,
  explicit type arguments on the generic calls that now infer differently.

## Upstream docs
- https://www.typescriptlang.org/docs/ — official TypeScript documentation
- https://github.com/microsoft/TypeScript — TypeScript source repository
