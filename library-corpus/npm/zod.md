# zod — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Zod is a TypeScript-first schema validation library: one schema definition
gives a runtime parser for untrusted data and, through `z.infer`, the static
type of the parsed result. It has no runtime dependencies, runs in Node.js
and browsers, and its schemas are immutable (every method returns a new
schema). Licence: MIT. Applications use it at their boundaries: environment
variables at startup, request bodies, form input, messages and API
responses.

- `zod`: the package. One install carries several entry points (see Major
  lines): `zod` (the current major's classic API), `zod/mini` (the
  tree-shakable functional API), and the permanent subpaths `zod/v3`,
  `zod/v4`, `zod/v4/mini` and `zod/v4/core`.
- `@zod/mini`: a standalone package that re-exports `zod/mini` through a
  peer dependency on `zod`, its version tracking `zod`. Needed only by
  projects that prefer the separate package name.

Upstream home: https://zod.dev/ (docs, release notes, migration guide) and
the source at https://github.com/colinhacks/zod.

## Install, setup and configuration
- `npm install zod`. Zod 4 is tested against TypeScript 5.5 and later
  (older compilers may work but are unsupported), and upstream requires
  `"strict": true` in `tsconfig.json`.
- No setup step and no global configuration is needed. Optional globals
  (Zod 4): `z.config({ customError })` for a global error message function,
  and `z.config(<locale>())` with a locale imported from `zod/locales`. The
  classic API loads the `en` locale automatically; Zod Mini loads none, so
  every message there is `Invalid input` until a locale is configured.
- **Pick one entry point per codebase** and import it as a namespace,
  `import * as z from "zod"` (or `"zod/mini"`). The subpath tables are under
  Major lines.

## Core API / usage shape
- **Schemas.** Primitives (`z.string()`, `z.number()`, `z.boolean()`,
  `z.bigint()`, `z.date()`), literals and enums (`z.literal`, `z.enum`),
  composites (`z.object`, `z.array`, `z.tuple`, `z.union`,
  `z.discriminatedUnion`, `z.record(key, value)`, `z.map`, `z.set`), and
  modifiers (`.optional()`, `.nullable()`, `.nullish()`, `.default()`,
  `.catch()`). In Zod 4 string formats are top-level schemas: `z.email()`,
  `z.url()`, `z.uuid()`, `z.ipv4()`, `z.iso.datetime()`, and so on.
- **Parsing.** `schema.parse(data)` returns a validated deep clone or throws
  a `ZodError`; `schema.safeParse(data)` returns `{ success: true, data }` or
  `{ success: false, error }` and never throws. Schemas with async
  refinements or transforms need `parseAsync`/`safeParseAsync`.
- **Errors.** `ZodError.issues` is the array of issues, each with `code`,
  `path`, `message` and code-specific fields. Formatting helpers in Zod 4:
  `z.treeifyError(err)` (nested), `z.flattenError(err)` (one level, for flat
  forms), `z.prettifyError(err)` (a human-readable string). Custom messages go
  through the unified `error` parameter: `z.string().min(5, { error: "Too
  short." })`, or a function of the issue.
- **Types.** `z.infer<typeof S>` (same as `z.output`) and `z.input<typeof S>`;
  they differ once a schema transforms or coerces.
- **Objects.** `z.object` strips unknown keys by default; `z.strictObject`
  rejects them; `z.looseObject` passes them through. `.extend()`, `.pick()`,
  `.omit()`, `.partial()`, `.required()` derive new object schemas.
- **Coercion.** `z.coerce.string()`, `.number()`, `.boolean()`, `.bigint()`,
  `.date()` run the input through `String`, `Number`, `Boolean`, `BigInt`
  and `new Date` before validating. Their input type is `unknown`.
- **Refinement and transformation.** `.refine(fn, { error, path })` and
  `.superRefine`/`.check` add custom checks; `.transform(fn)` changes the
  output; `.pipe(schema)` chains a second schema on the output; `z.preprocess`
  transforms before validation. `z.stringbool()` (Zod 4) parses boolean-like
  strings.

## Idioms & best practices
- **Parse at the boundary, once.** Validate untrusted input where it enters
  (request handler, message consumer, configuration load) and pass the typed
  result inward, so the rest of the code never sees unvalidated data.
- **Validate the environment at startup with `parse`.** Build one schema for
  the configuration, parse `process.env` once when the process starts, and
  export the typed result; a misconfiguration then stops the boot with every
  bad variable listed, instead of failing on first use. Modules import the
  parsed object, never `process.env`.
- **Environment values are strings.** `z.number()` rejects `"8080"`; use
  `z.coerce.number()` (or a string schema piped to a number) for numeric
  settings, and `z.stringbool()` for flags (see the pitfall on
  `z.coerce.boolean()`). Give optional settings an explicit `.default()`.
- **Use `safeParse` where failure is an expected outcome** (a request body)
  and map the error to a 400 with `z.flattenError` or `z.treeifyError`; use
  `parse` where failure is a bug or a fatal misconfiguration.
- **Derive types from schemas** with `z.infer`, not the other way round, so
  the runtime check and the type cannot drift.
- **Prefer `z.strictObject` for inputs where an unexpected key is a client
  error**, and the default stripping `z.object` where extra keys are
  harmless.
- **Libraries** that accept user schemas declare `zod` as a peer dependency
  (and a dev dependency), import from the permalink `zod/v4/core` rather than
  `zod` or `zod/v4`, or accept any Standard Schema implementation instead of
  depending on Zod.

## General pitfalls
- **`z.coerce.boolean()` is `Boolean(input)`.** Every non-empty string is
  `true`, so the environment value `"false"` parses to `true`, and `"0"` to
  `true`. For boolean flags use `z.stringbool()` (Zod 4: accepts `true`,
  `1`, `yes`, `on`, `y`, `enabled` and their negatives, case-insensitively,
  and rejects anything else). On Zod 3, which lacks it, write the mapping
  with a transform or pipe, as upstream advises for full control over
  coercion.
- **`z.coerce.number()` is `Number(input)`**, so an empty string becomes `0`
  rather than an error; add `.min()`/`.positive()` or refuse empty strings
  first where `0` is not a valid value.
- **Mixing entry points.** A Zod 3 schema is not assignable to a Zod 4 type,
  and the two majors have different error shapes and method sets. Importing
  `zod` in one file and `zod/v3` or `zod/v4` in another builds schemas from
  two different libraries in one program, which fails at the type level or,
  worse, at runtime in `instanceof` checks. Pick one entry point.
- **`zod` means a different major depending on the installed version**:
  Zod 3 on `3.x`, Zod 4 on `4.x`. A library importing the bare `zod` changes
  behaviour when its users upgrade.
- **`.default()` short-circuits in Zod 4**: on `undefined` it returns the
  default without parsing it, so the default must match the output type.
  `.prefault()` gives the Zod 3 behaviour (parse the fallback).
- **A missing key under a `z.coerce.*` field errors in Zod 4** (Zod 3 coerced
  `undefined`); declare `.default()` explicitly.
- **Unknown keys are dropped silently** by `z.object`; code that expects a
  pass-through field loses it.

## Testing
- Schemas are pure: test them directly with `parse`/`safeParse` on valid and
  invalid fixtures and assert on `error.issues` (`code` and `path`) rather
  than on message text, which locales and custom errors change.
- `z.infer` keeps test fixtures typed against the schema; type-level checks
  (a test file compiled by `tsc`) catch schema/type drift.
- Test environment schemas with explicit maps of strings, including the
  empty string and `"false"`, which the coercion pitfalls above turn into
  valid-looking values.

## Security defaults
- Zod validates shape and format; it does not sanitise for HTML, SQL or
  shell contexts. Escape or parameterise at the sink as usual.
- `z.object` strips unknown keys, which also stops mass-assignment of fields
  the schema does not name; `z.looseObject` turns that protection off.
- In Zod 4 issues do not carry the input value by default, so that
  sensitive input is not logged by accident; the `reportInput: true` parse
  option adds it. Leave it off wherever errors reach logs or clients, and
  still map a `ZodError` to a client-safe form rather than returning it raw.
- Validating size (`.max()` on strings and arrays) bounds work done on
  untrusted input; an unbounded schema accepts arbitrarily large payloads.

## Operational behaviour
- Parsing is synchronous unless a schema contains async refinements or
  transforms; upstream states that `parse` on such a schema throws, so use
  `parseAsync` or `safeParseAsync`.
- `parse` returns a deep clone, so mutating the result does not touch the
  input.
- A thrown `ZodError` at startup (environment validation) stops the process
  with the issue list; that is the intended fail-fast.

## Interop
- Database and ORM types: validate input with Zod, then hand typed values to
  the query layer ([`drizzle-orm.md`](drizzle-orm.md)).
- Authentication libraries often validate their own inputs; Zod still owns
  application configuration such as secrets and base URLs
  ([`better-auth.md`](better-auth.md)).
- JSON Schema: Zod 4 converts schemas with `z.toJSONSchema()`.
- Standard Schema: Zod implements the shared interface, so libraries that
  accept "any Standard Schema validator" take Zod schemas without a Zod
  dependency.

## Major lines

### Entry points across the 3-to-4 transition
- From `zod@3.25.0` the package contains both majors: `zod` and `zod/v3`
  export Zod 3, `zod/v4` exports Zod 4 and `zod/v4-mini` Zod Mini.
- From `zod@4.0.0` the root `zod` exports Zod 4 and `zod/mini` Zod Mini;
  `zod/v3` still exports Zod 3. Upstream states that `zod/v4`, `zod/v4-mini`
  and `zod/v3` stay available permanently, and that no code changed between
  the last `3.25` release and `4.0.0`. After the upgrade the optional rewrite
  is `zod/v4` → `zod`, `zod/v4-mini` → `zod/mini`, Zod 3's `zod` →
  `zod/v3`.
- Upstream calls Zod 3 functionally end of life: security and unambiguous
  bug fixes only.

### 3 line
- Error customisation through `message`, `invalid_type_error`,
  `required_error` and `errorMap`; `ZodError.format()`, `.flatten()` and
  `.errors`.
- String formats are methods (`z.string().email()`); `.strict()`,
  `.passthrough()`, `.merge()` and `z.nativeEnum()` are current API.
- `.default()` parses the default against the input type; a `z.coerce.*`
  field coerces a missing key.

### 4 line (from the 3 line)
- One `error` parameter replaces `message` (still accepted, deprecated);
  `invalid_type_error`, `required_error` and `errorMap` are removed.
- `ZodError.format()` and `.flatten()` are deprecated for `z.treeifyError`
  and `z.flattenError`; `.errors` is removed (use `.issues`).
- String formats move to top-level schemas (`z.email()`); the method forms
  are deprecated. `.strict()`/`.passthrough()` give way to
  `z.strictObject`/`z.looseObject`, `.merge()` to `.extend()`,
  `z.nativeEnum()` to `z.enum()`.
- `z.record()` needs both key and value schemas; `.deepPartial()` is
  removed; `z.number()` rejects infinite values and `.int()` accepts safe
  integers only.
- `z.coerce.*` input types are `unknown`; `.default()` short-circuits and
  `.prefault()` keeps the old behaviour; defaults inside optional object
  fields are applied.
- Adds `z.stringbool()`, `zod/mini`, `z.toJSONSchema()`, `z.config()` and
  `zod/locales`; issues omit the input value unless `reportInput` is set.
- A community codemod (`zod-v3-to-v4`) exists; upstream lists it as
  unofficial.

## Upstream docs
- Docs: https://zod.dev/ (Intro, Basic usage, Defining schemas, Formatting
  errors, Customizing errors)
- Versioning: https://zod.dev/v4/versioning
- Release notes: https://zod.dev/v4; migration guide: https://zod.dev/v4/changelog
- Zod Mini: https://zod.dev/packages/mini; library authors: https://zod.dev/library-authors
- Source: https://github.com/colinhacks/zod
- npm: https://www.npmjs.com/package/zod
