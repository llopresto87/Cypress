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
- **`strict` is not the ceiling.** Several checks sit outside the `strict`
  family and must be turned on by name:
  - `noUncheckedIndexedAccess`: an indexed access yields `T | undefined`. It
    has real defect-finding power in code that indexes arrays and record maps.
  - `exactOptionalPropertyTypes`: an optional property `{ a?: string }` stops
    accepting an explicit `undefined`.
  - The style checks `noImplicitReturns`, `noImplicitOverride`,
    `noFallthroughCasesInSwitch` and `noPropertyAccessFromIndexSignature`.
- **`import type`** (type-only imports) is the correct pattern under
  `isolatedModules: true`, which requires unambiguous type-only imports so each
  file can be transpiled independently. `verbatimModuleSyntax` goes further: an
  import without the `type` modifier is kept in the output as written, and one
  with it is dropped, so what is emitted is readable from the source.
- **`moduleResolution`** selects how imports are resolved; the `bundler` setting
  targets bundler-based builds rather than Node's own resolution algorithm and
  pairs naturally with `isolatedModules` / `importHelpers`.
- For code run by Node itself, `module: "nodenext"` floats: it tracks the
  newest Node behavior the compiler knows, and implies a floating `target`. The
  fixed `node<NN>` module modes pin one Node line's behavior instead.
- `types` in `compilerOptions` limits which `@types/*` packages load
  automatically. An empty list loads none; naming only what the code runs
  against (`["node"]` for Node-side code) keeps unrelated ambient types out.

## Idioms & best practices
- Enable `strict` from the start of a project rather than retrofitting it, then
  add `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`. On an
  existing codebase, count the errors each one produces with `tsc --noEmit`
  before deciding whether it is a cheap change.
- Use `import type` / `export type` under `isolatedModules` (and with
  single-file transpilers) to keep type-only references from affecting emit.
- Pick `moduleResolution` to match the actual build pipeline (bundler vs. Node).
  For Node-side code, choose deliberately between the floating `nodenext` and a
  fixed `node<NN>` mode matching the Node line the code runs on.
- Treat each explicit `any` (`: any`, `as any`, `<any>`) as a hole through every
  check above. `strict` does not forbid it; a lint rule does.
- A statement about a `tsconfig.json` is a configuration reading, not a
  type-check result. Only running `tsc --noEmit` (as a gate, in CI) says whether
  the code checks.

## General pitfalls
- **A compiler bump is a source-breaking event by design.** Both the `lib.d.ts`
  type hierarchy (e.g. relationships between `ArrayBuffer` and TypedArrays like
  Node's `Buffer`) and generic type-argument inference are refined across
  releases, so previously-clean code can start failing to compile without any
  source change. The usual fixes are realigning the ambient type packages
  (`@types/node`) and making the implicit explicit: explicit element types,
  explicit type arguments on the generic calls that now infer differently.
- `skipLibCheck: true` skips type-checking of every declaration file, the
  project's own `.d.ts` files included, so a broken ambient declaration can go
  unnoticed.
- A repository with no `tsc --noEmit` step type-checks only what its bundler or
  test runner happens to check. Many transpile-only runners strip types without
  checking them.

## Upstream docs
- https://www.typescriptlang.org/docs/: official TypeScript documentation
- https://www.typescriptlang.org/tsconfig/: the `tsconfig.json` reference
  (every flag named above)
- https://github.com/microsoft/TypeScript: TypeScript source repository
