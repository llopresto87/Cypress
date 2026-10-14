# typescript — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
TypeScript is Microsoft's typed superset of JavaScript and its compiler (`tsc`),
distributed as the `typescript` npm package (usually a dev dependency). It adds
static types over JavaScript and emits plain JavaScript. Type-checking behavior
is configured through `tsconfig.json`. Ambient types for runtimes and untyped
packages come from `@types/*` packages (`@types/node` for Node.js), and
`tslib` holds the emit helpers that `importHelpers` imports instead of
inlining them in each file.

The compiler itself changed implementation across major lines: through the 6
line it is written in TypeScript and runs on a JavaScript engine; from the 7
line it is a native port written in Go, shipped under the same package name
and the same `tsc` command (see Major lines).

Upstream home: the documentation at https://www.typescriptlang.org/docs/, the
`tsconfig.json` reference at https://www.typescriptlang.org/tsconfig/, and the
source at https://github.com/microsoft/TypeScript.

## Install, setup and configuration
- Install the compiler per project as a dev dependency, so every build uses
  the version the lockfile pins; the handbook's global
  `npm install -g typescript` suits trying it out. Frameworks that compile
  TypeScript themselves (Angular's compiler-cli) bound the accepted version:
  see [angular](angular.md).
- Nightly builds install as `typescript@next`. On the 7 line, a project that
  also needs the 6 line (for a tool that imports the compiler as a library)
  installs both through npm aliases; see the 7 line below.
- `tsconfig.json` holds `compilerOptions` plus the file set (`files`,
  `include`, `exclude`). `extends` lets several configs (the app build, the
  spec build) share a base and differ only where they must.
- **Strict mode** (`strict: true`) is the recommended baseline. It turns on the
  strict family: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`,
  `strictBindCallApply`, `strictBuiltinIteratorReturn`,
  `strictPropertyInitialization`, `noImplicitThis`,
  `useUnknownInCatchVariables` and `alwaysStrict`. Each one can then be turned
  off on its own. Upstream warns that later releases may add checks to the
  family, so a compiler bump can produce new errors in code that did not
  change. The default of `strict` itself changed across major lines (see
  Major lines).
- **`strict` is not the ceiling.** Several checks sit outside the `strict`
  family and must be turned on by name:
  - `noUncheckedIndexedAccess`: an indexed access yields `T | undefined`. It
    has real defect-finding power in code that indexes arrays and record maps.
  - `exactOptionalPropertyTypes`: an optional property `{ a?: string }` stops
    accepting an explicit `undefined`.
  - The style checks `noImplicitReturns`, `noImplicitOverride`,
    `noFallthroughCasesInSwitch` and `noPropertyAccessFromIndexSignature`.
- **`isolatedModules: true`** makes the compiler reject code that a
  single-file transpiler (esbuild, Babel, a test runner's transform) cannot
  compile correctly, such as re-exporting an imported type without `type`, or
  `const enum` and `namespace` uses that need the whole program.
  **`verbatimModuleSyntax`** goes further: an import without the `type`
  modifier is kept in the output as written, and one with it is dropped, so
  what is emitted is readable from the source.
- **`moduleResolution`** selects how imports are resolved; the `bundler` setting
  targets bundler-based builds rather than Node's own resolution algorithm and
  pairs naturally with `isolatedModules` / `importHelpers`.
- For code run by Node itself, `module: "nodenext"` floats: it tracks the
  newest Node behavior the compiler knows, and implies a floating `target`. The
  fixed `node<NN>` module modes pin one Node line's behavior instead.
- `types` in `compilerOptions` limits which `@types/*` packages load
  automatically. An empty list loads none; naming only what the code runs
  against (`["node"]` for Node-side code) keeps unrelated ambient types out.
  A package left out of `types` still types correctly when imported; it only
  stops adding globals (`process`, a test runner's `describe`) and
  auto-import suggestions. Its default changed across major lines.
- `typeRoots` replaces the automatic upward walk for `@types` folders: once
  set, only the listed folders load, so a list without `./node_modules/@types`
  drops every package from there.
- `paths` maps import specifiers to locations for the type checker only. It
  does not rewrite the emitted import, so the bundler or runtime needs the same
  mapping. A `paths` alias is a workspace-wide convention: adding one for a
  single file changes the convention, not one file.
- `rootDir` sets the root of the input tree mirrored into the output
  directory. Its default changed in the 6 line (see Major lines), and upstream
  names it, with `types`, as the default change most likely to surprise;
  setting it explicitly (`"rootDir": "./src"`) keeps the output layout stable.
- `skipLibCheck: true` skips type-checking of every declaration file. It
  speeds up builds and is common in generated configs.
- `noEmit` type-checks without writing output. By default `tsc` still emits
  JavaScript when there are type errors; `noEmitOnError` stops that.
- `experimentalDecorators` enables TypeScript's legacy (pre-standard)
  decorators, and `useDefineForClassFields` switches class fields to the
  standard ECMAScript semantics. Frameworks built on legacy decorators depend
  on both settings; the Angular-side facts are on [angular](angular.md).
- `ignoreDeprecations` silences the deprecation errors of one release line
  (`"6.0"` for the 6 line's); it is a bridge for the duration of a migration,
  and the next major line does not honor it (see Major lines).

## Core API / usage shape
- `tsc` with no file arguments compiles the project the nearest
  `tsconfig.json` describes (searching up from the current directory);
  `tsc -p <config>` picks another config, and
  `tsc --noEmit` is the type-check-only run. `tsc --build` builds a graph of
  project references in dependency order, and `tsc --watch` rebuilds on
  change.
- **The compiler API.** Through the 6 line, the `typescript` package is also a
  library: linters, editor plugins and embedded-language tools (template
  checkers, single-file-component tooling) import it to parse and type-check.
  The 7 line's first release ships no programmatic API, so those tools stay on
  the 6 line (see the 7 line).
- **`import type`** (type-only imports) is the correct pattern under
  `isolatedModules: true`, which requires unambiguous type-only imports so each
  file can be transpiled independently.
- Type annotations are erased in the emitted JavaScript and never change
  runtime behavior.
- `// @ts-expect-error` suppresses the error on the next line and is itself an
  error when that line has none. `// @ts-ignore` suppresses silently, whether
  or not an error is there.

## Idioms & best practices
- Enable `strict` from the start of a project instead of retrofitting it, then
  add `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`. On an
  existing codebase, count the errors each one produces with `tsc --noEmit`
  before deciding whether it is a cheap change.
- Never weaken a strict flag to make a change compile; fix the type. Where
  tests are thin, `strict` (plus a framework's template checking, such as
  Angular's `strictTemplates`) is the main safety net.
- Under `useUnknownInCatchVariables`, narrow the `catch (e)` variable
  (`e instanceof Error`) before use. Under `strictPropertyInitialization`,
  give each class field an initializer, a constructor assignment, or an
  explicit definite-assignment `!`.
- Prefer `// @ts-expect-error` to `// @ts-ignore`, so a suppression fails once
  the error it hid is gone. `@ts-ignore` fits the middle of a compiler
  upgrade, where the same line errors on one version and not the other.
- Use `import type` / `export type` under `isolatedModules` (and with
  single-file transpilers) to keep type-only references from affecting emit.
- Pick `moduleResolution` to match the actual build pipeline (bundler vs. Node).
  For Node-side code, choose deliberately between the floating `nodenext` and a
  fixed `node<NN>` mode matching the Node line the code runs on.
- Split configs by audience. The app build lists no test-runner types (an
  empty or minimal `types`), and the spec config names only its runner's
  types (`["jasmine"]` or similar), so test globals
  never leak into app code.
- Where a framework compiles TypeScript (Angular's compiler-cli), upgrade the
  compiler together with the framework, never alone.
- Treat each explicit `any` (`: any`, `as any`, `<any>`) as a hole through every
  check above. `strict` does not forbid it; a lint rule does.
- A statement about a `tsconfig.json` is a configuration reading, not a
  type-check result. Only running `tsc --noEmit` (as a gate, in CI) says whether
  the code checks.
- Cross a major line in two steps: first reach a clean build on the outgoing
  line with its deprecation warnings cleared (no `ignoreDeprecations`), then
  move. Upstream's promise of identical results across the 6 and 7 lines is
  stated for exactly that starting point.

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
- A build that emits on error ships code the checker rejected. Without
  `noEmitOnError` (or a separate `--noEmit` gate that fails the pipeline), a
  red type-check and a produced bundle can coexist.
- Setting `typeRoots` to a custom folder silently drops `node_modules/@types`,
  and the symptom is a wave of "cannot find name" errors for globals.
- A `paths` alias that the bundler or runtime does not also know compiles
  cleanly and fails at runtime with an unresolved import.
- **The command-line compiler and the compiler library are not the same
  dependency.** Moving the `typescript` package to the 7 line upgrades `tsc`,
  and also removes the library every API-consuming tool (a type-aware linter,
  an embedded-language checker, an editor plugin) imports from it. Upgrade the
  command and keep those tools on the 6 line's compatibility package, rather
  than treating the bump as one step.

## Testing
- The type check is a test of its own: run `tsc --noEmit -p <config>` for each
  config (app and spec) as a CI step, because test runners that transpile per
  file do not type-check.
- Type-level tests use `// @ts-expect-error` on a line that must not compile;
  upstream introduced the directive with that use in mind, and the test fails
  once the line starts compiling.
- Give the spec config its runner's `types` so test globals resolve there
  and nowhere else.
- To compare the 6 and 7 lines on one codebase, run the 6 line with
  `--stableTypeOrdering`, which makes its type ordering match the 7 line's;
  the remaining differences in diagnostics are the real ones. Upstream warns
  the flag can slow type-checking by up to a quarter and is for diagnosis
  only, not a permanent setting.

## Security defaults
- TypeScript has no runtime security surface of its own: types are erased, so
  an annotation on data from the network, storage or a message validates
  nothing. Validate untrusted input at runtime.
- `any`, `as` casts and the `!` definite-assignment operator switch checks
  off for one expression each, and none of them shows up at runtime. Review
  them where untrusted data enters.

## Operational behaviour
- `tsc` is a build-time tool: it runs, emits (or only checks) and exits.
  Nothing of it runs in production unless the code imports `tslib` helpers.
- Compile time grows with the declaration files loaded. Upstream reports that
  setting `types` to the packages actually needed cut build times by 20 to 50
  percent in projects it examined, and `skipLibCheck` trades declaration
  checking for speed.
- Through the 6 line the compiler runs single-threaded on a JavaScript engine.
  The 7 line parallelizes parsing, type-checking and emit, and trades memory
  for speed through its worker settings (see the 7 line).
- A failed type check exits non-zero, which is what makes `tsc --noEmit` usable
  as a gate.

## Interop
- [angular](angular.md): the Angular compiler accepts a bounded TypeScript
  range per major, and Angular's decorators need `experimentalDecorators`.
  Angular's template checking embeds the compiler library, so upstream's
  advice for the 7 line's first release is to use the 7 line's `tsc` for
  project-wide checks and keep the 6 line for editor support.
- [nodejs](nodejs.md): `@types/node` should follow the Node line the code runs
  on, and the `node<NN>`/`nodenext` module modes model Node's resolution.
- [rxjs](../npm/rxjs.md): RxJS majors declare a minimum TypeScript version.
- Bundlers and single-file transpilers (esbuild, Babel, Vite) strip types
  without checking them, which is why `isolatedModules` exists.
- Type-aware linters (typescript-eslint) and embedded-language tooling (Vue,
  Svelte, Astro, MDX through Volar) consume the compiler library, not `tsc`;
  for the 7 line's first release upstream says they stay on the 6 line.

## Major lines

### The 5 line and earlier
- `strict` defaults to `false`, `types` defaults to every visible
  `@types` package (every `node_modules/@types` folder up the tree), and
  `moduleResolution: node` (Node 10's algorithm) and `baseUrl` as a lookup root
  are accepted without warning.
- `// @ts-expect-error` exists from a later 3 release onward; the catch-variable
  `unknown` behind `useUnknownInCatchVariables` arrived during the 4 line.

### The 6 line
- Upstream states it is the last line built on the JavaScript codebase, and
  that most of its changes prepare projects for the 7 line.
- Several defaults changed. `strict` is `true` (a config that relied on the
  old default must now say `strict: false`), `module` defaults to `esnext`,
  `target` floats to the newest supported ECMAScript year,
  `noUncheckedSideEffectImports` is on, `libReplacement` is off, `rootDir`
  defaults to `.` (the directory holding the `tsconfig.json`), and `types`
  defaults to `[]`.
- The `types` change hits many projects: missing globals (`process`, `fs`, a
  test runner's `describe`) appear as a flood of "cannot find name" errors.
  Upstream's fix is an explicit list, typically `"types": ["node"]`;
  `["*"]` restores the old behavior.
- Deprecated, still working with `"ignoreDeprecations": "6.0"`:
  `target: es5` (the lowest target becomes ES2015), `downlevelIteration`,
  `moduleResolution: node`/`node10`, `baseUrl` (no longer a lookup root;
  prefix each `paths` entry instead), setting `esModuleInterop`,
  `allowSyntheticDefaultImports` or `alwaysStrict` to `false`, the `module`
  keyword for namespace declarations (write `namespace`; an ambient
  `declare module "..."` is unaffected), the `asserts` keyword on imports
  (write `with`), and `/// <reference no-default-lib="true"/>` (use `noLib`
  or `libReplacement`). Passing files on the command line while a
  `tsconfig.json` exists is an error; `--ignoreConfig` compiles the named
  files without the config.
- Upstream's release notes read two ways on three more options. Each sits
  under a "Deprecated" heading, and the general note says every deprecated
  option keeps working under `"ignoreDeprecations": "6.0"`. The per-option
  text says otherwise: `outFile` "has been removed", `moduleResolution:
  classic` "has been removed", and the `module` values `amd`, `umd`,
  `systemjs` and `none` are listed as "no longer supported". The 7 line's
  announcement lists all three among the 6 line's deprecations that became
  hard errors. The safe course under either reading is to migrate off them (a
  bundler for `outFile` and the module formats, `nodenext` or `bundler` for
  `classic`) and not to rely on the flag.
- Adds `--stableTypeOrdering`, an opt-in that makes the 6 line order types
  the way the 7 line does, for diagnosing differences between the two (see
  Testing).

### The 7 line
- The 7 line is the native port of the compiler, written in Go. Upstream
  ported it keeping the structure and logic of the JavaScript codebase so
  that both compilers give the same results, and reports full builds
  typically 8 to 12 times faster than the 6 line, from native code,
  shared-memory multithreading and new optimizations.
- It installs as the same `typescript` package and runs as the same `tsc`
  command. During the preview the port shipped separately, as the
  `@typescript/native-preview` package with a `tsgo` command; from the 7.0
  release candidate onward the command is `tsc`, and nightlies move back to
  `typescript@next`.
- Compatibility target: code that compiles cleanly on the 6 line with
  `stableTypeOrdering` on and no `ignoreDeprecations` should compile
  identically. Every 6-line deprecation listed above is a hard error,
  `ignoreDeprecations` no longer rescues it, and `stableTypeOrdering` is
  always on. The 6 line's default changes carry over; upstream words the
  `target` default as the stable ECMAScript version before `esnext`.
- Behavior differences beyond those: inference from template literal types
  keeps Unicode surrogate pairs whole, which breaks type utilities that
  modeled UTF-16 code units (some string-length types); and checking of
  JavaScript files is reworked to match `.ts` analysis, so several JSDoc
  conveniences stop working (a value used as a type needs `typeof`, `@enum`
  and `@class` are no longer special, a standalone `?` is not a type,
  Closure-style function types and postfix `!` are unsupported, a type name
  must come from a `@typedef`). The `CHANGES.md` file in the
  microsoft/typescript-go repository lists the intentional differences from
  the 6 line.
- **No programmatic API in its first release.** Tools that import the
  compiler as a library stay on the 6 line through the compatibility package
  `@typescript/typescript6`, which re-exports the 6 line's API and provides a
  `tsc6` command. Upstream's recommended layout uses npm aliases: alias
  `typescript` to `@typescript/typescript6` for the API consumers, and add the
  7 line under a second alias for the command.
- Parallelism, with experimental controls: `--checkers` sets the number of
  type-checker workers (default 4; a fixed count keeps results
  deterministic, more workers use more memory, and upstream notes that
  changing the count can rarely surface order-dependent results);
  `--builders` sets how many referenced projects build at once under
  `--build` and multiplies with `--checkers`; `--singleThreaded` runs
  everything on one thread, for debugging, comparison or constrained
  machines.
- `--watch` is rebuilt on a native file watcher rather than polling.
- Editor support is a language server (LSP). Its first release covers the
  common editor features; embedded-language tooling that needs the compiler
  library does not run on it yet (see Interop).

## Upstream docs
- https://www.typescriptlang.org/docs/: official TypeScript documentation
- https://www.typescriptlang.org/tsconfig/: the `tsconfig.json` reference
  (every flag named above)
- https://www.typescriptlang.org/docs/handbook/release-notes/overview.html:
  release notes, including the 6 line's default changes and deprecations
- https://devblogs.microsoft.com/typescript/: the TypeScript team's blog,
  where each release is announced (the 7 line's announcement holds the
  side-by-side, parallelism and compatibility facts above)
- https://github.com/microsoft/TypeScript: TypeScript source repository
- https://github.com/microsoft/typescript-go: the native port's staging
  repository, closed once the port shipped (development continues in
  microsoft/TypeScript); its `CHANGES.md` lists the 6-to-7 differences
