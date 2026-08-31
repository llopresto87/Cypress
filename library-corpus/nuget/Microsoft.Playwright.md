# Microsoft.Playwright — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The **.NET binding** for Playwright's cross-browser automation: it launches real
browser engines (Chromium, Firefox, WebKit) and drives them through locators,
network interception, and JavaScript evaluation. Same underlying tool as the
JS/TS ecosystem's Playwright; `../npm/playwright-test.md` covers that binding
and its test runner.

## Core API / usage shape
- Entry sequence: `Playwright.CreateAsync()` → `Chromium.LaunchAsync()` (or
  `Firefox`/`Webkit`) → `NewPageAsync()`. Each step yields a disposable object;
  the driver process behind them is real and must be torn down.
- The `Locator` API is the primary targeting mechanism — it is lazy and
  auto-waiting, so it re-resolves at action time. Prefer it over raw selectors
  plus manual waits, which is where flakiness comes from.
- Network interception: `Page.RouteAsync(pattern, handler)` intercepts matching
  requests; the handler resolves them with `RouteFulfillAsync` (serve a canned
  response) or `ContinueAsync` (let it through, optionally modified).
- `WaitForURLAsync` synchronizes on navigation; `EvaluateAsync<T>(jsExpression)`
  runs JavaScript in page context and marshals the result back to .NET — the way
  to inspect browser-side state such as storage.
- Browser binaries are installed out-of-band from the package itself, so a
  working install is a two-part setup (package + engines) on every machine and CI
  runner.

## Idioms & best practices
- Let locator auto-waiting do the synchronizing; explicit sleeps convert a timing
  bug into an intermittent one.
- Dispose the playwright/browser/context chain deterministically — a leaked
  browser process outlives the test run.

## General pitfalls
- **Response-header APIs can flatten multi-value headers:** a single HTTP
  response may legitimately carry the same header more than once — `Set-Cookie`
  being the canonical case — but header-inspection surfaces frequently expose
  headers as a flat map, collapsing repeats into one combined value or returning
  only the first. Code that must see *every* instance (verifying that each cookie
  propagates through an interceptor, for example) will silently assert against a
  partial view and pass while missing cookies. Check which representation the API
  in use actually returns rather than assuming repetition is preserved, and reach
  for the array-returning variant when one exists.

## Upstream docs
- https://playwright.dev/dotnet/
- https://github.com/microsoft/playwright-dotnet
- https://www.nuget.org/packages/Microsoft.Playwright
