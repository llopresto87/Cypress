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

## General pitfalls
- **A caret range can resolve higher than declared:** a `^` range permits any newer minor within the major, so fresh installs can land on a much later minor than the number written in `package.json`. Always check the lockfile / `node_modules/@playwright/test/package.json` for the version actually installed — the declared range is not necessarily the running version.
- **Browser channel/engine changes across minors can break snapshots:** headless-mode changes and dropped OS support arrive in specific releases and may require updating snapshots; verify browser behavior against the installed version.

## Upstream docs
- Official docs: https://playwright.dev/docs/api/class-test
- Release notes: https://playwright.dev/docs/release-notes
- Source: https://github.com/microsoft/playwright
- npm: https://www.npmjs.com/package/@playwright/test
