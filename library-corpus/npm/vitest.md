# vitest — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Vitest is a test runner and assertion library built on Vite. It runs test
files through Vite's transform and resolve pipeline, so a project's Vite
plugins and aliases apply to its tests, and it runs ES modules, TypeScript and
JSX without a separate compile step. Its API is Jest-compatible in shape
(`describe`, `test`/`it`, `expect`, and a `vi` helper in place of `jest`),
with Chai built in for assertions.

It is a development dependency: nothing of it ships with application code.
It runs unit and integration tests in Node.js by default, in a simulated DOM
(`jsdom`, `happy-dom`) when configured, or in real browsers through Browser
Mode.

- **npm package:** `vitest`. Licence: MIT. Upstream home: vitest.dev (guide
  and config reference) and the vitest-dev/vitest repository on GitHub.
- Companion packages, each needed only for the feature it names:
  - `@vitest/coverage-v8`: needed when coverage runs with the default `v8`
    provider.
  - `@vitest/coverage-istanbul`: needed when coverage runs with the
    `istanbul` provider.
  - `@vitest/ui`: needed for the `--ui` browser front end.
  - `@vitest/browser-playwright` or `@vitest/browser-preview`: needed for
    Browser Mode (the WebdriverIO provider moved to a community-maintained
    package in the 5 line).
- A DOM environment needs its simulation library installed beside Vitest
  (jsdom or happy-dom, whichever `environment` names). Those are independent
  libraries with their own surface, not part of this page.

## Install, setup and configuration
- `npm install -D vitest`. `vite` is a peer dependency in the 5 line: npm,
  pnpm, Bun and Deno install it automatically, Yarn does not, so Yarn users
  add `vite` explicitly. The companion packages above are peers pinned to
  Vitest's own exact version: bump them together with `vitest`.
- Runtime floor per line (from each migration guide): the 4 line needs Vite 6
  or later and Node.js 20 or later; the 5 line needs Vite 6.4 or later and
  Node.js 22.12 or later.
- **Config file resolution.** Without `--config`, Vitest looks in the project
  root for `vitest.config.{ts,mts,cts,js,mjs,cjs}` first and
  `vite.config.{…}` second, and runs without a config if neither exists. A
  `vitest.config.*` takes priority and the `vite.config` is then ignored
  entirely (use `mergeConfig` to extend it). Options live under `test` in a
  `defineConfig` imported from `vitest/config`; a `vite.config` that imports
  `defineConfig` from `vite` adds `/// <reference types="vitest/config" />`.
  JSON config is not supported. From the 5 line, config files are no longer
  looked up in parent directories.
- Settings that shape every run, with their defaults:
  - `include`: `['**/*.{test,spec}.?(c|m)[jt]s?(x)']`, resolved against
    `root`. Setting it replaces the default; spread `configDefaults.include`
    to extend it. `dir` limits the directory searched, and upstream calls it
    faster than excluding files.
  - `environment`: `'node'`. Alternatives are `jsdom`, `happy-dom`,
    `edge-runtime`, or a custom `vitest-environment-<name>` package or file.
    A `// @vitest-environment <name>` comment at the top of a file overrides
    it for that file.
  - `globals`: `false`. Test APIs are imported from `vitest`; `true` installs
    them globally, and TypeScript then needs `vitest/globals` in `types`.
  - `pool`: `'forks'` (child processes). `threads` uses worker threads;
    `vmThreads` and `vmForks` run each file in a VM context.
  - `fileParallelism`: `true`. `false` runs one file at a time (it forces
    `maxWorkers` to 1); it does not affect tests inside a file.
  - `maxWorkers`: all available parallelism in a single run, half of it in
    watch mode; a number or a percentage string such as `'50%'`.
  - `isolate`: `true`. Each test file gets a fresh worker and environment.
    It has no effect in the VM pools, which always isolate.
  - `testTimeout` 5000 ms and `hookTimeout` 10000 ms in Node (15000 and
    30000 with Browser Mode on); `0` disables either. `teardownTimeout`
    10000 ms bounds the wait for shutdown.
  - `setupFiles`: run inside each worker before every test file.
    `globalSetup`: runs once in the main process before workers start,
    exporting `setup`/`teardown` (or a default function returning teardown).
  - `env`: values put on `process.env` and `import.meta.env` inside tests,
    not in the main process.
  - Mock housekeeping, each run before every test: `clearMocks` (call
    history; default `true` from the 5 line, `false` before), `mockReset`
    (history and implementation; default `false`), `restoreMocks` (restores
    `vi.spyOn` spies; default `false`), `unstubEnvs` and `unstubGlobals`
    (default `false`).
  - `coverage.enabled` `false`, `coverage.provider` `'v8'`,
    `coverage.reportsDirectory` `'./coverage'` (deleted before each run while
    `coverage.clean` is on, its default).
- `vitest` alone starts watch mode in an interactive terminal and a single
  run in CI or when stdin is not a TTY. `vitest run` always runs once. Tools
  like `lint-staged` need `--run` so the command exits.

## Core API / usage shape
```ts
import { describe, expect, test, vi, beforeAll, afterAll } from 'vitest'

describe('cart', () => {
  beforeAll(async () => { /* shared setup; may return a teardown function */ })
  afterAll(async () => { /* release what beforeAll opened */ })

  test('totals line items', () => {
    expect(total([{ price: 2, qty: 3 }])).toBe(6)
  })

  test('calls the pricing service once', async () => {
    const fetchPrice = vi.fn().mockResolvedValue(10)
    await expect(priceOf('sku', fetchPrice)).resolves.toBe(10)
    expect(fetchPrice).toHaveBeenCalledTimes(1)
  })
})
```
- `test`/`it` with `.skip`, `.only`, `.todo`, `.each`/`.for` and
  `.concurrent`; options go in the second argument
  (`test(name, { retry: 2 }, fn)`), and a timeout number may still be the
  last argument.
- `expect` with Jest-style matchers, `.resolves`/`.rejects`, `expect.poll`
  for retried assertions, snapshots (`toMatchSnapshot`,
  `toMatchInlineSnapshot`), and `expect.extend` for custom matchers.
- `vi`: `vi.fn`, `vi.spyOn`, `vi.mock`/`vi.doMock` (module mocks; a factory
  returns an object naming every export, and `importOriginal` gives the real
  module for partial mocks), `vi.useFakeTimers`/`vi.setSystemTime`,
  `vi.stubEnv`, `vi.stubGlobal`.
- `vi.mock` is hoisted above every import in the file, because Vitest
  rewrites static imports into dynamic ones after it. `vi.doMock` is not
  hoisted.
- Test context and fixtures: `test.extend` builds fixtures injected by name,
  optionally scoped to a `file` or a `worker` (scoped fixtures from the 3.2
  release), with `onCleanup` for teardown. `aroundEach`/`aroundAll` (from the 4.1 release)
  wrap each test, for example in a database transaction that rolls back.
- Type tests: `expectTypeOf` and `assertType` in `*.test-d.ts` files, checked
  by `tsc` (or `vue-tsc`) under `--typecheck`; those files are analysed, not
  run.
- Projects (`test.projects`, which replaced `workspace`) run several
  configurations in one process, each with its own `include`, environment
  and pool options.

## Idioms & best practices
- Import test APIs from `vitest` and leave `globals` off unless a library
  needs them; upstream calls the default the explicit one. A library such
  as Testing Library relies on globals for its automatic cleanup and skips
  it without them.
- Keep tests in the `node` environment unless they need a DOM. DOM
  environments are expensive: upstream measures `jsdom` at roughly
  200-500 ms per import and `happy-dom` at roughly 90-200 ms, paid per file
  with isolation on. Name the DOM per file with a `@vitest-environment`
  comment, or split DOM tests into their own project.
- Size parallelism to the heaviest thing a test file starts. Every worker is
  a process (or thread) with its own copy of whatever the file boots, so
  memory grows with `maxWorkers`. A suite that shares an external resource
  that cannot take concurrent access (a database) runs with
  `fileParallelism: false`, which upstream names as the case for it.
  Observed in practice: a suite where every file boots an in-process
  database engine needs file parallelism off (or a low `maxWorkers`) to stay
  inside the machine's memory; upstream states the general cost (more
  workers, more memory) but not this case. The engine's own per-test
  pattern (a fresh instance, or a `clone()` of a migrated one) is on
  [electric-sql-pglite](electric-sql-pglite.md); the ORM side (a database
  per file, clients closed in teardown) is on [drizzle-orm](drizzle-orm.md).
- Put a per-test data reset where it cannot leak: a file- or worker-scoped
  fixture that opens the database once, and `aroundEach` wrapping each test
  in a transaction that rolls back. The rollback isolates database data
  only; with `isolate: false`, module state still crosses files in a worker.
- Profile before tuning: the `Duration` line splits the run into
  environment, import, transform, setup and tests, and `vitest doctor`
  measures alternative configurations, including whether the suite passes
  with `isolate: false`.
- Disable `isolate` only for suites that clean up after themselves; it is
  the largest speed-up for side-effect-free Node tests and the largest
  source of cross-file leaks.
- Keep a separate type-check step. Vitest transforms TypeScript through
  Vite, which transpiles per file and does not type-check, so a red type
  error does not fail a test run; run `tsc --noEmit` (or `--typecheck` for
  type tests) as its own gate.
- Resolve path aliases the way the build does: Vite ignores `tsconfig.json`
  `paths` and `baseUrl`, so add `vite-tsconfig-paths` or declare `alias`
  with absolute paths (a relative alias resolves against the importing
  file).
- In `vitest.config` an array option replaces the default; spread
  `configDefaults.include`/`configDefaults.exclude` to extend it.

## General pitfalls
- **Watch mode is the default.** A script that calls bare `vitest` hangs a
  hook or pipeline step on an interactive terminal; use `vitest run`.
- **`vitest.config.*` hides `vite.config.*`.** Plugins and aliases defined
  only in the Vite config vanish from tests once a Vitest config exists,
  unless it merges the Vite config.
- **The `threads` pool has process-level limits.** `process.chdir()` is
  unavailable, setting `TZ` inside a worker thread does not change the time
  zone, native addons that are not thread-safe can segfault, and Node's
  `fetch` can leave a worker that fails to terminate. The default `forks`
  pool has none of these; set `TZ` before workers start (shell, config file
  or `globalSetup`).
- **The VM pools leak by design.** ES modules imported in a VM context stay
  cached, so workers restart when they pass `vmMemoryLimit`; errors thrown by
  native modules fail `instanceof Error`. Recycling is cheap in `vmForks`
  and expensive in `vmThreads`.
- **`globalSetup` and tests share no globals.** It runs in the main process
  before workers exist; pass serializable data with `project.provide` and
  read it with `inject`.
- **Mock state leaks between tests unless something clears it.** Before the
  5 line `clearMocks` is off, so a `vi.fn()` keeps its calls from earlier
  tests; `mockReset` and `restoreMocks` stay off in every line. With
  concurrent tests, any of these resets mocks another running test is using.
- **`vi.mock` does not run where it is written.** It is hoisted above
  imports, so variables it closes over must come from `vi.hoisted`. A nested
  call warned before the 5 line and throws from it. A module already
  imported by a setup file is cached and is not mocked in the test file.
- **`mockReset` differs from Jest.** Vitest resets to the original
  implementation (from the 3 line), where Jest resets to an empty function.
- **Mocks of `node_modules` do not reach other packages.** A module mocked in
  a test is not mocked inside an external dependency that imports it unless
  that dependency is inlined (`server.deps.inline`).
- **Unawaited async assertions.** `expect(p).resolves…` without `await` was
  auto-awaited with a warning before the 5 line and fails the test from it.
- **Coverage only sees loaded files by default (from the 4 line).** Without
  `coverage.include`, files no test imports are missing from the report
  rather than shown at zero; set `coverage.include` to the source tree.

## Testing
This page's subject is the test runner itself. Upstream's guidance for
testing with it is the idioms above; the one self-test worth having is a CI
step that runs `vitest run` (and, separately, the type-check) and fails on a
non-zero exit.

## Security defaults
- The API server that backs the UI and Browser Mode is off by default
  (`api: false`) and listens only on `localhost` when on. Anyone who can reach
  it can write files and run code in the project: exposing it on another
  host is what opens that. From the 4.1 release, `api.allowWrite` and
  `api.allowExec` default to `false` whenever the host is not `localhost` or
  `127.0.0.1`; turning them back on re-opens it.
- From the 5 line, the UI requires the token Vitest prints in its URL.
- `vitest.config.*`, `setupFiles`, `globalSetup`, custom environments and
  every plugin are code that runs with the developer's or CI's permissions.
- Coverage and reports are written into the project (`./coverage`, and in
  the 5 line `.vitest/`); keep them out of version control and out of
  published packages.

## Operational behaviour
- A run starts one Vite server in the main process and a pool of workers
  (`maxWorkers`); each test file runs in one worker. On machines with many
  cores the main process can become the bottleneck, and upstream suggests
  sharding (`--shard=i/n` with the `blob` reporter, then `--merge-reports`).
- Within a file, tests run sequentially unless marked `concurrent`;
  concurrent tests share their file's worker and gain only while they await.
  Hooks run serially, and `afterAll`/`afterEach` in reverse order (from the
  2 line).
- Memory is per worker: what each file starts (a DOM, an in-process
  database, a large module graph) is multiplied by the number of workers
  running at once.
- Shutdown waits `teardownTimeout` for open handles before giving up; a test
  file that leaves a server, pool or timer open shows up there.
- `fsModuleCache` (on by default in the 5-line docs) persists transformed modules
  between runs, and `NODE_COMPILE_CACHE` adds Node's on-disk bytecode cache.
- Exit code is non-zero when any test fails, which makes `vitest run` usable
  as a gate.

## Interop
- Vite: Vitest reads the Vite config and its plugins, and resolves modules
  through Vite (Node tests use Vite's `ssr` environment, so custom export
  conditions go in `ssr.resolve.conditions`).
- [typescript](../language/typescript.md): Vitest strips types without
  checking them; keep `tsc --noEmit` as a separate gate.
- [playwright-test](playwright-test.md): end-to-end tests in a real browser
  belong to Playwright's runner; Vitest's Browser Mode drives Playwright as a
  provider for component and unit tests.
- Jest: the API is close but not identical (globals off by default, module
  factories return every export, `mockReset` semantics, no legacy timers,
  `vi.importActual` in place of `requireActual`).
- Testing Library expects globals for automatic cleanup.

## Major lines

### 2 line
- The default pool changed to `forks`; hooks run serially (stacked), with
  `sequence.hooks: 'parallel'` restoring the old behaviour.
- From the 2.1 release, a `typecheck.include` that overlaps `include` reports
  type tests and runtime tests separately; before it, it replaced `include`
  and the runtime tests did not run.

### 3 line
- `spy.mockReset` restores the original implementation instead of a no-op.
- `vi.useFakeTimers` fakes every available timer API (except `nextTick`) by
  default, `performance.now()` included.
- Test options as a third argument print a deprecation warning.
- `workspace` was renamed `projects` in the 3.2 release.

### 4 line
- The pool was rewritten: `maxThreads`/`maxForks` became `maxWorkers`,
  `singleThread`/`singleFork` became `maxWorkers: 1, isolate: false`,
  `poolOptions` was removed and its options moved to the top level
  (`memoryLimit` became `vmMemoryLimit`), and `minWorkers` was removed.
- Coverage: `coverage.all` and `coverage.extensions` were removed, and only
  loaded files are reported unless `coverage.include` is set; V8 coverage
  uses AST-based remapping only.
- Default `exclude` keeps only `node_modules` and `.git`.
- `vite-node` was replaced by Vite's module runner; `workspace`,
  `poolMatchGlobs`, `environmentMatchGlobs` and `deps.inline`/`external`
  (now under `server.deps`) were removed, and test options as a third
  argument no longer work.
- Mocks called with `new` construct instances, so a constructor mock's
  implementation must be a `function` or `class`, not an arrow function;
  `restoreAllMocks` only restores `vi.spyOn` spies.
- The browser provider is a factory object from `@vitest/browser-playwright`
  (and siblings), and `vitest/browser` replaces `@vitest/browser/context`.

### 5 line
- `clearMocks` defaults to `true`; inline projects inherit the root config
  (`extends: true`) and share its Vite server; `vite` is a peer dependency.
- Hoisted mocking calls outside the top level throw; unawaited async
  assertions and late `expect.poll` results fail the test.
- `test.sequential`, `describe.sequential` and the `sequential` option were
  removed (use `concurrent: false`); `bench` moved into the test context.
- Config files are not looked up in parent directories; coverage
  `include`/`exclude` match paths relative to the project root.
- Reports and artifacts share a `.vitest/` directory, and the `json` and
  `junit` reporters write files instead of stdout by default.
- `VITEST_POOL_ID` and `VITEST_WORKER_ID` are 1-based, so a per-worker
  resource name derived from them shifts by one.
- Fake timers and `setSystemTime` also mock `Temporal`; the UI needs its
  token URL; entry points deprecated in the 4.1 release
  (`vitest/environments`, `vitest/reporters`, `vitest/coverage` and others)
  are removed.

## Upstream docs
- Guide: https://vitest.dev/guide/
- Config reference: https://vitest.dev/config/
- Parallelism: https://vitest.dev/guide/parallelism
- Improving performance: https://vitest.dev/guide/improving-performance
- Common errors: https://vitest.dev/guide/common-errors
- Migration guide (current line, with links to earlier ones):
  https://vitest.dev/guide/migration
- Repository: https://github.com/vitest-dev/vitest
