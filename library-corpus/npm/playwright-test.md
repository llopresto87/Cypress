# @playwright/test — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Playwright test runner + browser automation library. Provides `defineConfig`, `devices`, the `test` API (`test.extend`/`describe`/`skip`), `expect`, and types (`Page`, `Browser`, `BrowserContext`, `Locator`, `APIRequestContext`, `TestInfo`). Includes an API-testing `request` context for REST calls without a browser.

The page covers the npm package `@playwright/test`. It drives Chromium, Firefox and WebKit, plus branded Chrome and Edge and emulated mobile devices, from one API. Upstream home: playwright.dev and the `microsoft/playwright` repository. The .NET binding has its own page, [`../nuget/Microsoft.Playwright.md`](../nuget/Microsoft.Playwright.md).

## Install, setup and configuration
`npm init playwright@latest` creates a project or adds Playwright to an existing one. It asks for TypeScript or JavaScript, the tests folder, an optional GitHub Actions workflow, and whether to install browsers, and it does not overwrite existing tests. To add it by hand: `npm install -D @playwright/test`, then `npx playwright install --with-deps`.

Each Playwright release needs specific browser builds, so run `npx playwright install` again after every update. `npx playwright install chromium` installs one browser; `npx playwright install-deps` installs only the operating-system packages. Browsers go to a per-user cache (`~/.cache/ms-playwright` on Linux) and take a few hundred megabytes each. `PLAYWRIGHT_BROWSERS_PATH` moves that cache. Upstream lists the supported Node.js and operating-system releases on its install page, and that list moves with Playwright releases.

`playwright.config.ts` exports `defineConfig({...})`. Runner options sit at the top level; browser and context options go under `use`. The settings that matter most, with their defaults:

- `testDir`, `testMatch` (default: files matching `.*(test|spec).(js|ts|mjs)`) and `testIgnore` choose the test files.
- `timeout`: 30000 ms per test. Fixture setup and `beforeEach` hooks count against it.
- `expect.timeout`: 5000 ms for web-first assertions.
- `fullyParallel`: off. Files run in parallel, but tests inside one file run in order in one worker.
- `workers`: half the logical CPU cores by default, from the CLI. Upstream recommends `1` on CI for stability and sharding for scale.
- `retries`: 0 unless set. Upstream's template uses 2 on CI only.
- `forbidOnly`: fails the run if a `test.only` was left in. Turn it on for CI.
- `reporter`: `list` from the CLI by default; the generated config uses `html`.
- `outputDir`: `test-results`, for traces, screenshots and videos.
- `use.baseURL`, so `page.goto('/')` works; `use.trace` (the template uses `'on-first-retry'`); `use.storageState` for a signed-in start; `use.testIdAttribute` (default `data-testid`).
- `projects`: one entry per browser or setup, each with its own `use`, plus `dependencies` and `teardown`.
- `webServer`: `{ command, url, reuseExistingServer }` starts the app before the tests and waits for the URL.
- `globalSetup` and `globalTeardown`: paths to modules that each export one function.

## Core API / usage shape
- Configure via `defineConfig` and `devices`; author tests with `test`/`expect` and fixtures via `test.extend`.
- The `request` module (distinct from `page.request`) creates an independent `APIRequestContext` for REST setup/teardown without driving a browser: `request.newContext()`, then `.post()`/`.get()`/`.delete()`, and `.dispose()`; responses expose `.ok()`/`.status()`/`.text()`/`.json()`/`.headers()`.
- Built-in fixtures arrive as test arguments: `page`, `context`, `browser`, `request`, `browserName`. A fixture defined with `test.extend` sets up before `await use(value)` and tears down after it. It runs only when a test asks for it, unless declared `{ auto: true }`.
- A fixture is test-scoped by default and torn down after each test. A `{ scope: 'worker' }` fixture lives as long as its worker process. When fixture A depends on fixture B, B is set up first and torn down last.
- Locators: `page.getByRole(role, { name })`, `getByLabel`, `getByPlaceholder`, `getByText`, `getByAltText`, `getByTitle`, `getByTestId`, and `page.locator(css or xpath)` as the last resort. Narrow them with `.filter({ hasText })` and chaining. A locator that matches more than one element throws a strict-mode error when you act on it.
- Web-first assertions retry until they pass or time out: `toBeVisible`, `toHaveText`, `toHaveCount`, `toHaveURL`, `toHaveTitle` and the rest of the auto-retrying set.
- Grouping and control: `test.describe`, `test.describe.configure({ mode: 'parallel' | 'serial', retries })`, `test.skip`, `test.only`, `beforeEach`, `afterEach`, `beforeAll`, `afterAll`.
- `testInfo` gives a test its metadata, including `testInfo.retry`, `outputPath()` and `attach()`.

## Idioms & best practices
- Use the `request` API-testing context for backend setup/teardown instead of driving the UI for data prep.
- To avoid caret drift, pin an exact version and commit the lockfile.
- **Locate by what the user sees.** Prefer `getByRole`, `getByLabel` and `getByPlaceholder` to CSS or XPath selectors. A class or id selector breaks when the styling changes, for a reason that has nothing to do with behavior. In a suite that already leans on CSS selectors, the cheap rule is that every new or touched locator uses a role or label, converted as the code is visited rather than in one sweep.
- `npx playwright codegen <url>` records actions and proposes locators, preferring role, text and test-id locators.
- **Wait on a signal, never on the clock.** Upstream marks `page.waitForTimeout` as discouraged: a test that waits for time is inherently flaky and the call is meant for debugging. Replace a sleep with a web-first assertion (`await expect(locator).toBeVisible()` and kin, which retry until they settle) or with a network signal. Raising the timeout is not a repair. Never write `expect(await locator.textContent())`: the manual assertion does not retry.
- Start a network wait before the action that triggers it, and await it after:
  ```ts
  const responsePromise = page.waitForResponse('**/api/items'); // no await here
  await page.getByRole('button', { name: 'Update' }).click();
  const response = await responsePromise;
  ```
  Awaiting `waitForResponse` after the click races the response and brings back the flake the change was meant to remove.
- Trace on failure, not on every test: `trace: 'on'` in the config records every test and is heavy. Use `'retain-on-failure'` (or `'on-first-retry'`) as the default and pass `--trace on` on the command line for a local run that needs a full trace. For CI failures, upstream prefers the trace viewer to videos and screenshots.
- Declare the browsers you mean to support. Upstream's example config declares chromium, firefox and webkit projects. Running one engine is a legitimate choice, but write down why, so the gap reads as a decision and not as drift.
- **Lint and type-check the tests themselves.** The `@typescript-eslint/no-floating-promises` rule catches a missing `await` before a Playwright call, which is the most common silent test bug. Run `tsc --noEmit` in CI so a wrong call signature fails the build. Neither gate helps unless CI actually runs it on each commit and pull request.
- Isolate each test. Give each test its own browser context, storage, cookies and data, created and torn down by a `test.extend` fixture, so no test depends on another test's leftovers.
- **Mock only what the test is not about.** For a third-party service a test merely passes through, `page.route(...).fulfill(...)` guarantees the response. A suite whose purpose is to prove a real integration (a real identity provider issuing a real token, say) should not mock that integration away, because the mock deletes the assertion.
- Use `expect.soft` for several independent checks in one test, so a failure reports all of them instead of stopping at the first.
- Keep Playwright current. Upstream's reason is that new releases test against the newest browsers before the public gets them.
- On CI, install only the browsers the projects use (`npx playwright install chromium --with-deps`) to save time and disk.

## General pitfalls
- **URL glob semantics are easy to misread:** in a URL glob, `*` matches any characters except `/`, `**` matches any characters including `/`, and `?` matches only a literal question mark. Use `*` where "any one character" was meant.
- **Actionability has counter-intuitive definitions.** Before replacing a sleep with an assertion, check that the assertion can settle. An element with `opacity: 0` counts as visible; a zero-size or `display: none` element does not. "Stable" means the bounding box held for two consecutive animation frames, so an element under a running animation is a legitimate reason a wait never resolves.
- **A caret range can resolve higher than declared:** a `^` range permits any newer minor within the major, so fresh installs can land on a much later minor than the number written in `package.json`. Always check the lockfile / `node_modules/@playwright/test/package.json` for the version actually installed. The declared range is not necessarily the running version.
- **Browser channel/engine changes across minors can break snapshots:** headless-mode changes and dropped OS support arrive in specific releases and may require updating snapshots; verify browser behavior against the installed version.
- A CLI `--grep` cannot bring back tests the config already excluded with `testIgnore` or a project-level `grepInvert`. An npm script named after a suite can collect zero tests. Observed in practice and confirmed with `--list`; upstream documents `--grep` as a filter and says nothing on precedence. Run the command with `--list` before treating a green run as coverage.
- A `--grep @tag` run has also been observed to collect the whole suite in a config with several projects, when only one project's test carried the tag. The mechanism was not established. Upstream does say that a filter selects the primary tests and then pulls in every test of the projects they depend on, and `--no-deps` turns that off. Do not assume a tag filter narrows a multi-project run; check with `--list`.
- The legacy `text=` selector is a case-insensitive substring match: `text=Login` also matches "Login to your area". Use `getByRole(..., { name, exact: true })` or `:text-is()` for an exact, case-sensitive match. Observed in practice and confirmed by upstream's selector docs, which recommend the modern text locators.
- After a test fails, the runner throws away its worker process and browser and starts a new one. `beforeAll` hooks run again in the new worker, so they must be safe to repeat.
- In `serial` mode, one failure skips the rest of the group, and retries rerun the whole group.
- `--only-changed` picks test files from a dependency-graph heuristic and can miss tests. Upstream says to run the full suite after it.
- Runner options belong at the top level of the config, not under `use`; upstream says so explicitly.

## Testing
- Do one-time setup in a setup project that other projects list in `dependencies`, with cleanup in a project named by its `teardown`. Upstream recommends this over `globalSetup`: the setup shows in the HTML report, records traces, and can use fixtures, `headless` and `testIdAttribute`. `globalSetup` and `globalTeardown` get none of that.
- Sign in once in a setup project, save `page.context().storageState({ path })`, and start the test projects from that file through `use.storageState`. For tests that change server-side state per user, use one account per worker in a worker-scoped fixture.
- Observed in practice: a per-test `test.extend` fixture creates a disposable user through the identity provider's admin REST API (using the `request` context), opens a fresh context and page, logs in through the real login page, and on teardown takes a screenshot, closes the context and deletes the user.
- Observed in practice: a `globalTeardown` sweeps leftover per-test resources (disposable users, records) across runs and crashed jobs, independent of any one test's fixture teardown. Upstream's recommended home for such a sweep is a teardown project.
- Guards and pure functions can be tested in the same runner with no browser: a test that never asks for `page` starts no browser. Observed in practice with `expect(fn).toThrow(regex)` and the `expect(value, message)` form for readable failures.
- Retries classify each test as passed, flaky (failed, then passed on retry) or failed. `--fail-on-flaky-tests` makes a flaky test fail the run, and `testInfo.retry` lets a test clean up before a retry.
- Flake hunting: `--repeat-each <N>` runs each test N times, and `--last-failed` reruns only the failures.
- Scale out with `--shard=current/all` across CI jobs. Inside one job, `test.describe.configure({ mode: 'parallel' })` runs the tests of one file in parallel.
- Visual snapshots: `-u` / `--update-snapshots` rewrites them. Without the flag, only missing snapshots are written.

## Security defaults
- A saved `storageState` file holds cookies and headers that can impersonate the test account. Upstream recommends a `playwright/.auth` folder listed in `.gitignore` and strongly discourages committing it.
- `forbidOnly` set on CI stops a stray `test.only` from silently shrinking the suite.
- Browsers download from Microsoft's CDN by default. `PLAYWRIGHT_DOWNLOAD_HOST` points the download at an internal mirror for locked-down networks.

## Operational behaviour
- Workers are separate operating-system processes, each with its own browser. Worker-scoped fixtures run once per worker, and a worker is reused across files while their worker fixtures match.
- Startup: `webServer` launches the app and waits for its URL. With `reuseExistingServer` on (the template sets it off for CI), an already running local server is used instead.
- Ordering: setup projects run first. Dependent projects start only after every setup test passed, then run in parallel. A failed setup skips its dependents.
- Timeouts: 30 s per test and 5 s per assertion by default. `--global-timeout` caps the whole run, which is unlimited by default.
- Artifacts land in `test-results`, and the HTML report in `playwright-report`; `npx playwright show-report` opens it.
- Disk: every installed browser takes a few hundred megabytes. `npx playwright uninstall` removes the browsers of the current installation, and `--all` removes those of other installations too.
- An empty run fails by default. `--pass-with-no-tests` makes a run with no tests found succeed.

## Interop
- [`../nuget/Microsoft.Playwright.md`](../nuget/Microsoft.Playwright.md): the .NET binding of the same engine.
- [`../language/nodejs.md`](../language/nodejs.md): the runtime the runner needs.
- [`../language/typescript.md`](../language/typescript.md): the default language for tests and the `tsc --noEmit` gate.
- [`keycloak-js.md`](keycloak-js.md) and [`../container/keycloak.md`](../container/keycloak.md): the login flow and admin API that identity fixtures drive.

## Major lines
`@playwright/test` has stayed on the 1 major line. Behavior changes, browser updates and dropped platforms arrive in minor releases, so read the release notes for the installed version, and keep the lockfile honest about which one that is.

## Upstream docs
- Best practices (locators, web-first assertions, lint, isolation, third parties): https://playwright.dev/docs/best-practices
- Actionability checks: https://playwright.dev/docs/actionability
- Network events and URL glob patterns: https://playwright.dev/docs/network
- Configuration: https://playwright.dev/docs/test-configuration
- Global setup and teardown, project dependencies: https://playwright.dev/docs/test-global-setup-teardown
- Projects: https://playwright.dev/docs/test-projects
- Fixtures: https://playwright.dev/docs/test-fixtures
- Locators: https://playwright.dev/docs/locators
- Other locators (legacy `text=`, CSS pseudo-classes): https://playwright.dev/docs/other-locators
- Authentication and `storageState`: https://playwright.dev/docs/auth
- Retries: https://playwright.dev/docs/test-retries
- Command line: https://playwright.dev/docs/test-cli
- Continuous integration: https://playwright.dev/docs/ci
- Browsers: https://playwright.dev/docs/browsers
- Installation: https://playwright.dev/docs/intro
- Official docs: https://playwright.dev/docs/api/class-test
- Release notes: https://playwright.dev/docs/release-notes
- Source: https://github.com/microsoft/playwright
- npm: https://www.npmjs.com/package/@playwright/test
