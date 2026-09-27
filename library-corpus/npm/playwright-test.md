# @playwright/test — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Playwright test runner + browser automation library. Provides `defineConfig`, `devices`, the `test` API (`test.extend`/`describe`/`skip`), `expect`, and types (`Page`, `Browser`, `BrowserContext`, `Locator`, `APIRequestContext`, `TestInfo`). Includes an API-testing `request` context for REST calls without a browser.

## Core API / usage shape
- Configure via `defineConfig` and `devices`; author tests with `test`/`expect` and fixtures via `test.extend`.
- The `request` module (distinct from `page.request`) creates an independent `APIRequestContext` for REST setup/teardown without driving a browser: `request.newContext()`, then `.post()`/`.get()`/`.delete()`, and `.dispose()`; responses expose `.ok()`/`.status()`/`.text()`/`.json()`/`.headers()`.

## Idioms & best practices
- Use the `request` API-testing context for backend setup/teardown instead of driving the UI for data prep.
- To avoid caret drift, pin an exact version and commit the lockfile.
- **Locate by what the user sees.** Prefer `getByRole`, `getByLabel` and `getByPlaceholder` to CSS or XPath selectors. A class or id selector breaks when the styling changes, for a reason that has nothing to do with behavior. In a suite that already leans on CSS selectors, the cheap rule is that every new or touched locator uses a role or label, converted as the code is visited rather than in one sweep.
- **Wait on a signal, never on the clock.** Upstream marks `page.waitForTimeout` as discouraged: a test that waits for time is inherently flaky and the call is meant for debugging. Replace a sleep with a web-first assertion (`await expect(locator).toBeVisible()` and kin, which retry until they settle) or with a network signal. Raising the timeout is not a repair. Never write `expect(await locator.textContent())`: the manual assertion does not retry.
- **Start a network wait before the action that triggers it**, and await it after:
  ```ts
  const responsePromise = page.waitForResponse('**/api/items'); // no await here
  await page.getByRole('button', { name: 'Update' }).click();
  const response = await responsePromise;
  ```
  Awaiting `waitForResponse` after the click races the response and brings back the flake the change was meant to remove.
- Trace on failure, not on every test: `trace: 'on'` in the config records every test and is heavy. Use `'retain-on-failure'` (or `'on-first-retry'`) as the default and pass `--trace on` on the command line for a local run that needs a full trace.
- Declare the browsers you mean to support. Upstream's example config declares chromium, firefox and webkit projects. Running one engine is a legitimate choice, but write down why, so the gap reads as a decision and not as drift.
- **Lint and type-check the tests themselves.** The `@typescript-eslint/no-floating-promises` rule catches a missing `await` before a Playwright call, which is the most common silent test bug. Run `tsc --noEmit` in CI so a wrong call signature fails the build. Neither gate helps unless CI actually runs it on each commit and pull request.
- Isolate each test. Give each test its own browser context, storage, cookies and data, created and torn down by a `test.extend` fixture, so no test depends on another test's leftovers.
- **Mock only what the test is not about.** For a third-party service a test merely passes through, `page.route(...).fulfill(...)` guarantees the response. A suite whose purpose is to prove a real integration (a real identity provider issuing a real token, say) should not mock that integration away, because the mock deletes the assertion.
- Use `expect.soft` for several independent checks in one test, so a failure reports all of them instead of stopping at the first.

## General pitfalls
- **URL glob semantics are easy to misread:** in a URL glob, `*` matches any characters except `/`, `**` matches any characters including `/`, and `?` matches only a literal question mark. Use `*` where "any one character" was meant.
- **Actionability has counter-intuitive definitions.** Before replacing a sleep with an assertion, check that the assertion can settle. An element with `opacity: 0` counts as visible; a zero-size or `display: none` element does not. "Stable" means the bounding box held for two consecutive animation frames, so an element under a running animation is a legitimate reason a wait never resolves.
- **A caret range can resolve higher than declared:** a `^` range permits any newer minor within the major, so fresh installs can land on a much later minor than the number written in `package.json`. Always check the lockfile / `node_modules/@playwright/test/package.json` for the version actually installed — the declared range is not necessarily the running version.
- **Browser channel/engine changes across minors can break snapshots:** headless-mode changes and dropped OS support arrive in specific releases and may require updating snapshots; verify browser behavior against the installed version.

## Upstream docs
- Best practices (locators, web-first assertions, lint, isolation, third parties): https://playwright.dev/docs/best-practices
- Actionability checks: https://playwright.dev/docs/actionability
- Network events and URL glob patterns: https://playwright.dev/docs/network
- Official docs: https://playwright.dev/docs/api/class-test
- Release notes: https://playwright.dev/docs/release-notes
- Source: https://github.com/microsoft/playwright
- npm: https://www.npmjs.com/package/@playwright/test
