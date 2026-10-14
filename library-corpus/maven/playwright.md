# playwright — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Playwright for Java: the Java binding of Microsoft's browser-automation engine.
It drives Chromium, Firefox and WebKit (plus installed branded Chrome and Edge)
through one synchronous API: launch a browser, open isolated contexts and pages,
find elements with auto-waiting locators, intercept the network, evaluate
JavaScript, and assert with retrying assertions. It is a library, not a test
runner: tests run under JUnit or TestNG, and an optional JUnit extension
supplies fixtures.

- `com.microsoft.playwright:playwright`: the API. It pulls in the driver
  artifacts (`com.microsoft.playwright:driver` and
  `com.microsoft.playwright:driver-bundle`, the Node.js driver the Java client
  talks to) and Gson for the wire protocol. The JUnit fixtures
  (`com.microsoft.playwright.junit.UsePlaywright`) and the assertions
  (`com.microsoft.playwright.assertions.PlaywrightAssertions`) ship inside it.

The same engine has two other pages here: the npm runner and its browser
handling, [`../npm/playwright-test.md`](../npm/playwright-test.md), and the .NET
binding, [`../nuget/Microsoft.Playwright.md`](../nuget/Microsoft.Playwright.md).
The bindings share browser builds, the locator model and the actionability
rules, not an API. Upstream home: https://playwright.dev/java/ and the
`microsoft/playwright-java` repository.

## Install, setup and configuration
- **Dependency:** one Maven dependency, `com.microsoft.playwright:playwright`.
  Upstream's system requirements are Java 8 or later, and a list of supported
  Windows, macOS and Debian/Ubuntu releases that moves with Playwright
  releases. Alpine and other musl distributions are not supported. Declare it
  with `<scope>test</scope>` when it serves only tests: the driver artifacts are
  large, and test scope keeps all of them off the runtime classpath. A framework
  BOM does not manage Playwright, so the version is explicit.
- **Browsers are a second install.** Each Playwright release needs specific
  browser builds, so browsers are installed again after every library update.
  The CLI runs through Maven:
  `mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="install chromium"`.
  `install --with-deps` also installs the operating-system packages (it needs
  root and the distribution's package manager); `install-deps` installs only
  those. `install --only-shell` fetches only the headless shell Chromium uses
  for headless runs; the "new headless" mode (launch channel `chromium`) needs
  the full build instead, and `--no-shell` skips the shell.
- **`Playwright.create()` installs browsers by itself.** The client runs the
  driver's `install` with no browser argument, so the first `create()` on a
  clean machine downloads every browser (Chromium, Firefox and WebKit), not only
  the one the code launches (upstream's intro states it; observed in practice
  as several hundred megabytes on first use). `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`
  (any value but `0` or `false`) turns the automatic install off; install the
  one browser with the CLI and set the variable for the test run.
- **Cache and download environment:** browsers go to a per-user cache
  (`~/.cache/ms-playwright` on Linux, `~/Library/Caches/ms-playwright` on macOS,
  `%USERPROFILE%\AppData\Local\ms-playwright` on Windows).
  `PLAYWRIGHT_BROWSERS_PATH` moves it, and must be set for `mvn test` as well as
  for the install. `PLAYWRIGHT_DOWNLOAD_HOST` (or the per-browser
  `PLAYWRIGHT_CHROMIUM_DOWNLOAD_HOST` and kin) points the download at an
  internal mirror; `HTTPS_PROXY` routes it through a proxy, and
  `NODE_EXTRA_CA_CERTS` trusts an intercepting proxy's root CA.
  `PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT` is an idle timeout, 30 s by default.
  Unused browser versions are garbage-collected unless
  `PLAYWRIGHT_SKIP_BROWSER_GC=1` or `install --no-remove`.
- **Driver location:** by default the client extracts its Node.js driver from
  the jar into a fresh temporary directory on every launch
  (`-Dplaywright.driver.tmpdir` chooses where). `PLAYWRIGHT_DRIVER_DIR` or
  `-Dplaywright.cli.dir` points at a pre-extracted driver instead, and
  `PLAYWRIGHT_NODEJS_PATH` (`-Dplaywright.nodejs.path`) at a Node.js already on
  the machine.
- **The vendor runner image,** `mcr.microsoft.com/playwright/java:v<version>`
  (with `-noble`, `-jammy` and similar Ubuntu suffixes), holds the browsers and
  their system packages, a JDK and Maven, with `PLAYWRIGHT_BROWSERS_PATH` and
  `PLAYWRIGHT_DRIVER_DIR` preset. It does not hold the library: the project
  still declares it. Upstream: the library version and the image version must
  match, or "Playwright will be unable to locate browser executables". The
  image's JDK is the Ubuntu distribution's OpenJDK package (the Dockerfile at
  the image's tag names the major), not the vendor JDK a project's own build
  image may use, so tests in that image run on a second JDK.
- **Container flags upstream recommends:** `--init` (no zombie processes under
  PID 1) and `--ipc=host` ("Chromium can run out of memory and crash" without
  it); `--cap-add=SYS_ADMIN` only as a local troubleshooting step. Observed in
  practice: `--shm-size` of about a gigabyte without `--ipc=host` was enough for
  headless Chromium under a memory- and PID-capped container. Playwright's
  source launches Chromium with `--disable-dev-shm-usage` in its default
  switches. Upstream's documented advice is still `--ipc=host`; the shm-size
  route is an observed alternative for runners that must not share the host
  IPC namespace, not an upstream recommendation.
- **Timeouts:** actions and navigations default to 30 s
  (`setDefaultTimeout`, `setDefaultNavigationTimeout` on a page or context);
  `PlaywrightAssertions` assertions retry for 5 s
  (`PlaywrightAssertions.setDefaultAssertionTimeout`).

## Core API / usage shape
- **Object chain:** `Playwright.create()` → `playwright.chromium()` (or
  `firefox()`, `webkit()`) → `launch(new BrowserType.LaunchOptions().setHeadless(true))`
  → `browser.newContext(...)` → `context.newPage()`. `Playwright` is
  `AutoCloseable`; close it (try-with-resources) and the browser and driver go
  with it. Headless is the default.
- **Context options** (`Browser.NewContextOptions`): viewport, locale, color
  scheme, reduced motion, forced colors, `baseURL`, `storageState`,
  `ignoreHTTPSErrors`, `bypassCSP`, `serviceWorkers`, `javaScriptEnabled`. A
  context is the unit of isolation: cookies, storage and cache.
- **Locators:** `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Save"))`,
  `getByLabel`, `getByText`, `getByTestId`, `page.locator(css)`, narrowed with
  `.filter(...)`. Actions (`click`, `fill`, `check`, `press`) auto-wait for
  actionability: the locator resolves to exactly one element that is visible,
  stable, receives events, is enabled and is not inert (the npm page explains
  the counter-intuitive cases).
- **Assertions:** `import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;`
  then `assertThat(locator).hasText(...)`, `.isVisible()`, `.hasCount(...)`,
  `assertThat(page).hasURL(...)`, `assertThat(response).isOK()`; each retries
  until it passes or times out, and `.not()` negates.
- **Navigation:** `page.navigate(url)` waits for `load` by default.
  `page.waitForURL(glob)` waits for the next page after a click; upstream
  deprecates `waitForNavigation` as "inherently racy" in its favour.
- **Evaluation:** `page.evaluate("() => ...", arg)` runs JavaScript in the page
  and marshals serializable values back; `page.addInitScript(...)` runs a script
  in every new document before the page's own scripts.
- **Network:** `context.route(pattern, route -> route.fulfill(...) | route.resume() | route.abort())`;
  every matching request stalls until the handler resolves it.
- **Waiting on the Java side:** `page.waitForCondition(BooleanSupplier)` blocks
  while Playwright keeps dispatching events (upstream's example waits for
  console messages collected by a listener); `page.waitForFunction(js)` polls a
  JavaScript predicate in the page; `locator.waitFor(...)` waits for an element
  state. `page.waitForTimeout(ms)` is discouraged ("Never wait for timeout in
  production").
- **API testing:** `playwright.request().newContext(...)` gives an
  `APIRequestContext` for HTTP setup and teardown without a browser.

## Idioms & best practices
- **One `Playwright` per thread.** Upstream: "Playwright Java is not thread
  safe"; every object it creates must be used on the thread that created the
  `Playwright`, or behind synchronization. Under JUnit parallel execution, run
  classes concurrently and the methods of one class on its own thread, with one
  `Playwright` and `Browser` per class.
- **Share the browser, isolate the context.** Create `Playwright` and `Browser`
  once per class (`@BeforeAll`), a fresh `BrowserContext` and `Page` per test,
  and close the context in `@AfterEach`. `@UsePlaywright` does this with
  injected `page`, `browserContext`, `browser`, `playwright` and `request`
  fixtures; an `OptionsFactory` sets launch and context options. Upstream marks
  the JUnit integration experimental.
- **Wait on a signal, never on the clock,** and on the next state rather than on
  a load event: after an action that loads a new document, wait for an element
  of that document (a locator wait or `assertThat(...)`) or for
  `waitForURL`, not for `waitForLoadState` alone (pitfalls below).
- Prefer a locator wait or `assertThat` to `waitForFunction` and
  `waitForCondition` whenever the condition is visible in the DOM.
- **Create contexts in one place** when they need security-relevant options
  (`ignoreHTTPSErrors`, a route that aborts other origins, blocked service
  workers), so a test cannot get the relaxed option without the guard that goes
  with it.
- Restrict browser installs to what the tests launch: CLI-install one browser
  and set `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` for the run.
- Move the library and the runner image together; a check that compares the
  dependency version with the image tag keeps them from drifting.

## General pitfalls
- **A string predicate in `waitForFunction` fails under a strict CSP.** Under a
  `script-src` without `'unsafe-eval'`, `waitForFunction("...")` fails with
  "EvalError: Refused to evaluate a string as JavaScript", while
  `page.evaluate` with the same string works. Upstream's issue tracker records
  it for the Java binding, with `bypassCSP` as the maintainer's suggestion;
  observed in practice the same way. Better than turning CSP off: poll from
  Java (`evaluate` inside a loop or `waitForCondition`) or wait on a locator.
- **`waitForCondition` can stall on a quiet page.** Observed in practice: a
  predicate that read page state through `evaluate` took seconds longer than a
  locator wait for the same element, and worked well only where the page kept
  producing events. Upstream documents the method for conditions that "depend
  on page events" and does not describe its re-check cadence; the client source
  re-evaluates the predicate between short polls of its message queue, so the
  mechanism of the stall was not established. Use a locator wait for DOM state.
- **Click, then `waitForLoadState`, can resolve on the old document.**
  Upstream: "The navigation must have been committed when this method is
  called. If current document has already reached the required state, resolves
  immediately." If the click's navigation has not committed yet, the call
  returns at once against the page being left, although upstream's own usage
  example shows exactly that pair. Wait for an element of the next state (or
  `waitForURL`) first, then for the load state if it still matters.
- **Autofocus lands after `load`.** The HTML standard focuses `autofocus`
  candidates during the event loop's rendering update, not as part of document
  load, so a keyboard walk started right after navigation can begin before the
  field is focused. Wait for the focused state (`:focus` on the expected
  element) before sending keys that depend on focus. Observed in practice and
  consistent with the standard.
- **`Thread.sleep` freezes the client.** In the synchronous API, events are
  dispatched only while a Playwright call is on the stack, so no event handler
  runs during `Thread.sleep`; `page.waitForTimeout` keeps dispatching.
- **Browser and library drift.** A browser cache or image from another
  Playwright version shows up as "unable to locate browser executables";
  reinstall browsers after every bump.
- **The first run downloads every browser** unless the automatic install is
  turned off (Install, above), which matters on metered or egress-restricted
  build agents.
- **Root in a container disables the Chromium sandbox** (upstream). Acceptable
  for a project's own tests, not for visiting untrusted sites.
- Observed in practice: a container started with `--cap-drop ALL` keeps uid 0
  but loses `CAP_DAC_OVERRIDE`, so it cannot write into a mounted tree owned by
  another uid (the build's `target/` directory, say); hand the tree to the
  container's user before the run.

## Testing
- Run browser tests as their own group (a JUnit tag or a naming pattern
  selected by a Maven profile), so the default build stays browser-free and the
  browser group runs where browsers are installed or in the vendor image.
- Give each test, and each data-driven sub-case, its own context: empty storage
  and cookies, no leakage between cases.
- Capture evidence on failure: `page.screenshot(...)` into the build output.
- An application started in the test JVM (an embedded server on a random port)
  can be driven directly: the browser runs as a child process of the same
  machine or container.
- Testcontainers works from inside the vendor image when the Docker socket or
  host is reachable (observed in practice); see
  [`testcontainers.md`](testcontainers.md).

## Security defaults
- `ignoreHTTPSErrors` and `bypassCSP` default to false, and service workers to
  `allow`. Turning off certificate checks or the page's CSP removes protections
  the test may be meant to prove; when a test needs a self-signed server
  certificate, pair `ignoreHTTPSErrors` with a route that aborts requests to
  any other origin.
- The vendor image runs browsers as root, which disables the Chromium sandbox.
  For untrusted pages, upstream runs a non-root user with its seccomp profile and
  states the image is meant for testing and development.
- Browsers download from Microsoft's CDN at install time and, by default, on the
  first `create()`. On a locked-down network use the vendor image (no download
  at test time) or `PLAYWRIGHT_DOWNLOAD_HOST` pointing at an internal mirror.
- `storageState` files hold live session cookies; keep them out of version
  control (the npm page says more).

## Operational behaviour
- Each `Playwright` starts a Node.js driver process; each `launch()` starts a
  browser process. Closing `Playwright` ends both.
- First use on a clean machine is slow (the browser download, bounded by a
  ten-minute install timeout in the client); later runs reuse the cache.
- Disk: the driver-bundle jar is large, and each browser adds a few hundred
  megabytes to the cache. In a container, mount the cache or use the vendor
  image, or every container downloads again.
- Memory: headless Chromium needs enough shared memory (Install, container
  flags) and memory for each page. Observed in practice: a headless-Chromium
  test stage fitted in a container memory limit of a few gigabytes with a PID
  limit in the low thousands.

## Interop
- [`../npm/playwright-test.md`](../npm/playwright-test.md): the npm runner, the
  browser model, actionability and locator advice shared by every binding.
- [`../nuget/Microsoft.Playwright.md`](../nuget/Microsoft.Playwright.md): the
  .NET binding.
- [`spring-boot.md`](spring-boot.md): a framework BOM may manage Gson at a
  version lower than the one Playwright's POM asks for, and the BOM wins.
  Observed in practice: Playwright worked on the BOM-managed Gson. Pin Gson
  explicitly only when a Playwright release fails on the managed one.
- [`testcontainers.md`](testcontainers.md): running containers from the
  browser stage.
- [`../container/docker.md`](../container/docker.md): the runner-image flags
  above.

## Major lines
Playwright for Java has stayed on the 1 major line, versioned in step with the
other bindings (the runner images of every language share one version number). Behaviour changes, browser updates and dropped platforms arrive
in minor releases, so read the release notes for the version in use and keep the
library, the browsers and any runner image on the same number.

## Upstream docs
- Installation and system requirements: https://playwright.dev/java/docs/intro
- Browsers, install CLI, cache and environment variables: https://playwright.dev/java/docs/browsers
- Docker image and run flags: https://playwright.dev/java/docs/docker
- Navigations: https://playwright.dev/java/docs/navigations
- Actionability: https://playwright.dev/java/docs/actionability
- Evaluating JavaScript: https://playwright.dev/java/docs/evaluating
- Test runners: https://playwright.dev/java/docs/test-runners
- JUnit fixtures: https://playwright.dev/java/docs/junit
- Multithreading: https://playwright.dev/java/docs/multithreading
- Page API (`waitForLoadState`, `waitForFunction`, `waitForCondition`): https://playwright.dev/java/docs/api/class-page
- Assertions: https://playwright.dev/java/docs/api/class-playwrightassertions
- Release notes: https://playwright.dev/java/docs/release-notes
- Source: https://github.com/microsoft/playwright-java
- `waitForFunction` under CSP: https://github.com/microsoft/playwright/issues/7395
