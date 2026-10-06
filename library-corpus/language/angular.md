# angular — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Angular is Google's TypeScript-first web application framework, distributed as a
family of `@angular/*` npm packages: `@angular/core`, `@angular/common`,
`@angular/compiler`, `@angular/compiler-cli`, `@angular/forms`,
`@angular/router`, `@angular/platform-browser`,
`@angular/platform-browser-dynamic` and `@angular/animations`. The CLI and build
tooling are `@angular/cli`, `@angular/build` (the esbuild-based builders) and the
older webpack-based `@angular-devkit/build-angular`. Server-side rendering is
optional, through `@angular/ssr` and `@angular/platform-server`. Zone-based
change detection uses the separate `zone.js` package.

Upstream home: the documentation at https://angular.dev/ and the source at
https://github.com/angular/angular (framework) and
https://github.com/angular/angular-cli (CLI and builders).

## Install, setup and configuration
- The CLI is installed with `npm install -g @angular/cli`, and `ng new <name>`
  creates a workspace with a first application in it. The CLI needs a Node.js
  line that is in active or maintenance LTS.
- The `@angular/*` framework packages move together on a shared major/minor
  line; the CLI/build tooling is versioned independently of them. Their
  majors still have to match: upstream requires the same major for
  `@angular/core` and the CLI.
- Each Angular major declares the Node.js, TypeScript and RxJS ranges it
  supports (`angular.dev/reference/versions`). `@angular/compiler-cli` accepts
  only a bounded TypeScript range, so TypeScript is upgraded together with the
  Angular major that accepts the new version, never on its own. The ranges
  themselves are pins: read them from that table for the project's major. A
  build image on a Node outside the range may build today and fail on the next
  release, so treat a Node error during `ng build` as this mismatch first.
- `angular.json` holds the workspace. Each project has targets (`build`,
  `serve`, `test`), each with `options` and named `configurations`.
  - The `build` target that `ng new` writes has a `production` and a
    `development` configuration. `defaultConfiguration` picks the one used
    when none is named; when it is unset, `options` apply unchanged.
    `ng serve` uses the development build.
  - `fileReplacements` swaps one source file for another per configuration.
    By default no file is replaced. `ng generate environments` creates
    `src/environments/` and wires the replacement: in that layout the base
    `environment.ts` is the production default and the development
    configuration replaces it with `environment.development.ts`.
  - `budgets` sets size thresholds per configuration. Each entry has a `type`
    (`initial` for the JavaScript and CSS that bootstrap the app, `bundle` with
    a `name` for one bundle, `anyComponentStyle` and others), a warning and an
    error threshold, and an optional `baseline` (default 0). Crossing an error
    threshold fails the build. Lazy routes (`loadChildren`/`loadComponent`)
    are the main lever for staying under the `initial` budget.
  - `allowedCommonJsDependencies` lists CommonJS packages whose build warning
    should be silenced. Upstream prefers ESM dependencies, because CommonJS
    modules defeat the bundler's optimisation and make bundles larger.
  - `define` (application builder) replaces identifiers with constant values
    at build time, from `angular.json` or `ng build --define NAME=VALUE`. Every
    value is written as a string.
  - `outputHashing` adds content hashes to output file names. The builder's own
    default is `none`; the `production` configuration that `ng new` writes sets
    `all`.
  - `optimization.styles.inlineCritical` (critical CSS inlining) is on by
    default in optimised builds.
  - `<base href>` in `index.html`, or `--base-href` per build, sets the URL
    the app resolves relative paths against when it is served under a path
    prefix.
- The dev server proxy, a `proxy.conf.json` wired by `ng serve --proxy-config`
  or by the `serve` target's `proxyConfig` option, sends matching paths to a
  backend. It is what makes relative API paths work in development. Changes to
  the file need an `ng serve` restart.
- The CLI's generated `tsconfig.json` sets `experimentalDecorators: true`,
  because Angular's decorators use TypeScript's legacy decorator semantics,
  and an ES2022 `target`. When a project's `target` is below ES2022 or unset,
  the build raises it to ES2022 and defaults `useDefineForClassFields` to
  `false` unless the project set it, and warns that it did so. Templates
  through the 17 line wrote `useDefineForClassFields: false` explicitly.
  Observed in practice: projects treat both settings as fixed, and flipping
  either one to "modernise" the config breaks decorator and field
  initialisation in existing code. Upstream gives the reason for the field
  default (a TypeScript class-field change that breaks some decorators) and
  says nothing about removing the decorator requirement.
- The template-strictness flags live under `angularCompilerOptions`:
  `strictTemplates`, `strictInjectionParameters` and
  `strictInputAccessModifiers`. A workspace created in strict mode turns them
  on.
- `skipTests: true` in a project's schematics configuration stops
  `ng generate` from writing `.spec.ts` files (the schematic default is
  `false`).

## Core API / usage shape
- The idioms below (standalone bootstrap, `inject()`, signals, built-in control
  flow, functional guards and interceptors) do not exist on older majors, so
  check the project's pin before applying one; the Major lines section says
  where each one starts.
- The modern, upstream-recommended entry point is standalone bootstrap:
  `bootstrapApplication(AppComponent, { providers: [...] })` with no root
  `NgModule`, and standalone components (an explicit `standalone: true` before
  Angular 19, where the option defaulted to `false`; from 19 on standalone is
  the default and a component declared in an `NgModule` says
  `standalone: false`). Application-wide
  providers are passed in that bootstrap options object.
- `importProvidersFrom(SomeModule)` brings the providers of a remaining
  `NgModule` into a standalone bootstrap.
- Dependencies are obtained with the `inject()` function, in a field
  initializer or inside a function, instead of through constructor
  parameters. Route guards are plain functions (`CanActivateFn` and kin),
  not guard classes.
- `provideAppInitializer(fn)` runs a function, which may return a promise or
  an observable, before the application finishes starting. It supersedes the
  `APP_INITIALIZER` multi-provider token.
- HTTP is configured through `provideHttpClient`, with **functional
  interceptors** registered via `withInterceptors`, the upstream-recommended
  approach; it is one of the providers supplied at bootstrap.
  - The order of the `withInterceptors([...])` array is the order a request
    passes through the chain, and the order carries weight: an interceptor
    that adds the bearer token has to run before the error-handling
    interceptors that inspect the response.
  - Class-based interceptors registered through the `HTTP_INTERCEPTORS`
    multi-provider run only when `provideHttpClient` is given
    `withInterceptorsFromDi()`. They run in provider registration order, which
    upstream calls hard to predict in a large DI tree.
  - Other features: `withXsrfConfiguration` and `withNoXsrfProtection` (see
    Security defaults), `withJsonpSupport`, `withRequestsMadeViaParent`, and
    the transport switch between `fetch` and `XMLHttpRequest`, whose default
    changed across major lines.
- Reactivity is signal-based: `signal`, `computed` and `effect`, with signal
  inputs (`input()`, `output()`, `model()`) in place of the `@Input()`/`@Output()`
  decorators. `toSignal()` (from `@angular/core/rxjs-interop`) bridges an
  observable into a signal, which is how reactive-forms streams such as
  `valueChanges` and `statusChanges` reach a signal-based template.
- Templates use the built-in control flow blocks (`@if`, `@for`, `@switch`)
  rather than the `*ngIf`/`*ngFor` structural directives.
- Change detection is either zone-based (`zone.js` patches async APIs and
  `provideZoneChangeDetection` configures it) or zoneless
  (`provideZonelessChangeDetection`), where signals, template events and
  `markForCheck` tell Angular when to check. A zoneless app has to drop code
  that waits on `NgZone.onStable` or `NgZone.onMicrotaskEmpty`, and
  `NgZone.isStable` is always `true` there.
- SSR is opt-in: apps without `@angular/ssr` / `platform-server` (no `server.ts`,
  no SSR dependency) run purely client-side.

## Idioms & best practices
- Prefer standalone components and `bootstrapApplication` over the legacy root
  `NgModule` bootstrap. Standalone components can compose directly; for a
  simple or single-screen app they can be wired together without pulling in the
  Router at all.
- Prefer `inject()` over constructor parameter injection, and functional route
  guards over class-based ones.
- Prefer functional HTTP interceptors (`withInterceptors`) over class-based
  interceptors. Do not mix a functional chain with the DI-bridged class chain:
  two chains make the relative order easy to misjudge.
- The style guide's own rules:
  - Mark the properties Angular initializes `readonly`: inputs, outputs,
    models and queries. `readonly` does not apply to decorator-based inputs,
    which is one more reason to prefer signal inputs.
  - Mark class members that only the template reads `protected`, so they stay
    out of the component's public API, which dependency injection and queries
    can reach. A `computed()` that exists for the template is the textbook case.
  - Prefer `[class.x]`/`[class]` and `[style.x]`/`[style]` bindings over the
    `NgClass`/`NgStyle` directives. The guide gives a performance reason as
    well as a readability one: the directives cost more than the built-in
    bindings.
  - Organize by feature area. Avoid directories named after a code type
    (`components`, `directives`, `services`).
  - Name files with hyphens, matching the TypeScript identifier they export.
    Put a unit test beside its code as `<name>.spec.ts`.
  - Implement the lifecycle hook interface (`implements OnInit`) for each hook
    a class uses.
- Use `ChangeDetectionStrategy.OnPush`. Reading a signal in an OnPush component
  marks it for check, which is where the signal model pays off; under default
  change detection most of that payoff is lost.
- Model derived state with `computed`, not with an `effect` that writes one
  signal from another. The signals guide says so directly: effects are not for
  propagating state changes.
- Keep the `@angular/*` framework packages aligned on the same version line;
  upgrade them together. When a move matters (a security fix, say), raise the
  **declared** range floor in `package.json` as well as the lockfile, so a
  later install cannot resolve back below it.
- Turn on the compiler's template strictness (`strictTemplates`,
  `strictInjectionParameters`, `strictInputAccessModifiers` under
  `angularCompilerOptions`). They go beyond the style guide, and they
  make a mechanical sweep, such as the `protected` one above, safe to do file
  by file. Where tests are thin, `strictTemplates` is the main safety net,
  because it turns template errors into build errors.
- Where a file departs from the guide, the guide ranks consistency within that
  file above its own rules. A departure is a reason to plan a sweep, not to leave
  one file half-converted.
- Use a same-origin, relative API base. Call the backend as `api/...` or
  `/api` through the app's own reverse-proxy edge, not through an
  absolute URL in `environment*.ts`, and derive a WebSocket endpoint as
  path-only or protocol-relative so `ws`/`wss` follows the page scheme. This
  removes CORS from the picture and survives a host or domain change without
  a rebuild. Observed in practice; upstream supports it
  from two sides: the dev proxy exists to serve relative paths, and
  `HttpClient` sends its XSRF header only to relative and same-origin URLs.
- Under a path prefix, use document-relative URLs. `HttpClient` resolves a
  relative URL against the document base (`<base href>`), while a
  root-absolute `/...` URL (in the API base, in CSS `url(/...)`, in
  `<img src="/...">`) escapes the prefix and lands on the proxy root. Observed
  in practice.
- To keep deploy-specific values out of the bundle, load them at runtime.
  Observed in practice: `main.ts` fetches a `config.json` (written by the
  container entrypoint, or mounted) before `bootstrapApplication`, refuses to
  start without it, and provides the values through DI. It is the
  rebuild-free alternative to `fileReplacements`. An entrypoint that writes
  into the web root needs write permission there, which a non-root web-server
  image does not grant by default.
- When the backend publishes an OpenAPI document, generate the HTTP client
  from it. Hand-written services drift from the server with no error.
  Observed in practice.
- If a project has no specs, check whether `skipTests` in the schematics
  configuration caused it before concluding nobody wrote tests.

## General pitfalls
- **The unversioned docs host serves the current major.** `angular.dev` shows
  the latest release, which may not be the major the project runs. Upstream
  keeps version-pinned hosts (`v<major>.angular.dev`); cite the one matching
  the project's major, or a rule from a newer line gets applied to code that
  ships on an older one.
- **The framework family moves only as a set.** The framework packages declare
  exact peer dependencies on each other, so a targeted install or an update of
  one package cannot move it alone: the resolver refuses, or stays where it was.
  Move the whole family in one change.
- Within the `@angular/*` family, peer-dependency misalignment between core and
  cdk/animations/material can be masked by an installer's legacy-peer-deps escape
  hatch, silently permitting a drifted install that a clean, strict install would
  reject. Verify family alignment explicitly rather than trusting a green install.
- **The legacy-peer-deps escape hatch can also break the clean install.** It can
  prune peer-only dependencies from the lockfile. The local install passes, and
  the next clean install from that lockfile (`npm ci`, typically in a container
  build) fails with the manifest and the lockfile out of sync.
- The CLI/build tooling patch line drifts from the framework packages by design,
  so a matching framework line is no guarantee the tooling line matches.
- Dropping `withInterceptorsFromDi()` from `provideHttpClient` unhooks every
  class-based interceptor without an error. Observed in practice: the auth
  header and the error handler disappear, and requests still succeed against
  an open local backend, so nothing fails until a protected call does.
- A production configuration with no `fileReplacements` ships
  `environment.ts`, whatever an `environment.prod.ts` beside it says. Observed
  in practice: a deploy step rewrote the production file and the change never
  reached the bundle. Upstream states the cause: no file is replaced by
  default.
- **Build-time API URLs turn a host move into "CORS errors".** An absolute API
  or WebSocket URL baked into the bundle makes every call cross-origin to a
  dead or wrong host after a domain or host change, and the browser reports it
  as CORS. A smoke test that calls the backend directly cannot see it; verify
  through the browser path (page origin, then the edge). A page served over
  https that calls `ws://` or `http://` is blocked as mixed content. Observed
  in practice.
- **A returning browser can keep a stale bundle.** A cached `index.html`, or a
  service worker, keeps the old bundle and its baked configuration after a
  correct redeploy. Serve `index.html` uncached, make the hashed assets
  long-lived, and include a returning-visitor check in the post-deploy gate.
  Observed in practice; the web-server header mechanics are on
  [nginx](../container/nginx.md).
- A committed `proxy.conf.json` that points at a live host makes `ng serve`
  act on real data by default. The proxy target is an environment choice.
  Observed in practice.
- Proxy path patterns match differently per dev-server builder. Under the
  Vite-based `@angular/build:dev-server`, `/api` matches only `/api` and
  `/api/*` matches one path segment, so nested paths need `/api/**`. Under the
  webpack `@angular-devkit/build-angular:dev-server`, `/api` matches every
  sub-path. A proxy file carried across the builder switch can stop matching.
- `allowedCommonJsDependencies` hides the warning, not the cost. The bundle
  stays larger than an ESM dependency would make it.
- With DI, the last provider for a token wins. A token provided twice (a
  `LOCALE_ID`, say) makes an edit to the first copy look ineffective. Observed
  in practice.
- Server-side rendering introduces a distinct security and behavior surface
  (e.g. URL normalization / origin handling) that does not exist in
  client-only apps; whether it applies depends on whether SSR packages are used.
- A count of `effect()` calls, or of `[innerHTML]` bindings, is not an audit.
  Whether an effect propagates state, or a bound value can carry attacker
  content, is only known once each site is read.

## Testing
- `ng test` runs the `test` target in watch mode in an interactive terminal,
  and once on CI. New projects from the 21 line use Vitest through the
  `@angular/build:unit-test` builder, with `jsdom` (or `happy-dom`) emulating
  the DOM in Node. Earlier lines scaffolded Karma with Jasmine, which is still
  supported. The `test` options take `include` (default `**/*.spec.ts` and
  `**/*.test.ts`), `setupFiles`, `providersFile` (a default-exported provider
  array for every test), `coverage` and `browsers` (real-browser runs through
  a Vitest browser provider); `runnerConfig` points at a custom Vitest config.
- Migrating an existing suite from Karma to Vitest is experimental upstream
  and requires the `application` builder. The `unit-test` builder takes build
  options from a build configuration (`buildTarget`, the development one by
  default), not from the `test` target as the Karma builder did. The
  `refactor-jasmine-vitest` schematic rewrites test code only.
- `TestBed.configureTestingModule({ providers: [...] })` builds an isolated
  injector per test, and `TestBed.inject(Token)` reads from it. `TestBed`
  provides real dependencies by default; replace a slow or unpredictable one
  with `{ provide: Dep, useValue: stub }`.
- HTTP: provide `provideHttpClient(...)` **before** `provideHttpClientTesting()`,
  which overrides part of it. `HttpTestingController.expectOne(url)` asserts
  one matching request (it fails if more than one matches), `req.flush(body)`
  answers it, `req.flush(body, { status: 500, statusText })` simulates a
  server error, `match()` handles duplicates, and `verify()` in `afterEach`
  fails a test that left a request unanswered. Test an interceptor by
  registering it in the same `provideHttpClient` call
  (`withInterceptors([...])`, or `withInterceptorsFromDi()` for class-based
  ones) and inspecting the request the controller captured.
- Where zoneless is the default, `TestBed` runs zoneless even when `zone.js`
  is loaded; add `provideZoneChangeDetection()` to a test that needs zones,
  and use `await fixture.whenStable()`. Under Vitest, `fakeAsync`, `flush` and
  `waitForAsync` need `zone.js/plugins/vitest-patch` in the test polyfills;
  upstream recommends moving to native `async` and Vitest fake timers instead.
- `ng test --coverage` writes a coverage report to `coverage/`.
- Browser end-to-end tests are a separate tool; see
  [playwright-test](../npm/playwright-test.md).
- Observed in practice: a scaffolded runner with zero spec files, and CI that
  runs no test step, is a common state. A green build then says nothing about
  behavior.

## Security defaults
- **Bindings are sanitized; the bypass is the sharp corner.** Angular escapes
  interpolation and sanitizes `[innerHTML]` by default, but the security guide
  still names binding an attacker-controllable value into `innerHTML` as the
  usual XSS route. The `bypassSecurityTrust*` methods of `DomSanitizer` switch
  that protection off for one value. Treat each call as a security decision,
  and trace where each `[innerHTML]` value comes from. Resource URLs (an
  `<iframe src>`, say) cannot be sanitized at all, only trusted.
- Templates are trusted code. The default AOT compiler prevents template
  injection, so use it in every production build; the JIT compiler compiles
  templates in the browser at runtime.
- A Content-Security-Policy is the server's job. Angular inserts `<style>`
  elements at runtime, so a strict `style-src` needs a per-request nonce
  (`ngCspNonce` on the root element, or the `CSP_NONCE` token) or
  `'unsafe-inline'`. A nonce must be unique per response: a CDN that caches
  the HTML caches the nonce with it.
- The CLI adds inline scripts to `index.html` only for critical CSS inlining
  (on by default) and for subresource integrity. With `inlineCritical` off and
  SRI off, `script-src 'self'` holds without a nonce. Otherwise use
  `security.autoCsp`, which hashes the inline scripts at build time into a
  `<meta>` policy (not with SSR), or a nonce.
- Trusted Types can be enforced with the `angular` policy (plus
  `angular#unsafe-bypass` when the app uses the bypass methods,
  `angular#bundler` for lazy loading, `angular#unsafe-jit` for JIT). A browser
  without Trusted Types keeps the sanitizer's protection.
- XSRF: `HttpClient` reads the `XSRF-TOKEN` cookie and sends it as
  `X-XSRF-TOKEN` on mutating requests to relative and same-origin URLs, not on
  `GET` or `HEAD`. This is only the client half: the server has to set the
  cookie and check the header, or the protection does nothing. Give each app
  on a shared domain its own cookie name. `withNoXsrfProtection()` turns it
  off.
- `environment*.ts` files are public. Everything in them is compiled into the
  bundle every visitor downloads, so a secret never goes there.
- SSR adds a request-handling surface. The server validates `Host` and the
  forwarding headers against `allowedHosts` (in `angular.json`, the app
  engine options, or `NG_ALLOWED_HOSTS`) and answers an unknown host with
  `400`. The `Forwarded` and `X-Forwarded-*` headers are dropped unless
  `trustProxyHeaders` allows them. `allowedHosts: ['*']`, or trusting proxy
  headers that no proxy validates, opens host-header injection and SSRF.

## Operational behaviour
- `bootstrapApplication` returns a promise. Initialization does not complete
  until every `provideAppInitializer` function has finished, including any
  promise or observable it returns, so a runtime configuration fetch belongs
  before bootstrap or in an initializer.
- The `application` builder writes the browser bundle to
  `dist/<project>/browser`, where the webpack `browser` builder wrote
  `dist/<project>`. A Dockerfile or deploy step copying the old path breaks
  after the builder migration.
- `ng serve` is a development server: it skips optimisations and rebuilds on
  change. Production serves the built static files from a web server (or the
  SSR Node server, when SSR is used).
- A client-only build is static files: there is no Angular process to start
  or stop, and failure modes live in the web server and the browser cache
  (see the stale-bundle pitfall).
- Zone-based apps load `zone.js` and patch the browser's async APIs; a
  zoneless app removes it from the `polyfills` of the build and test targets
  and drops the dependency.

## Interop
- RxJS: `HttpClient` and reactive forms return observables, and
  `@angular/core/rxjs-interop` bridges them to signals. Each Angular major
  declares the RxJS range it accepts. See [rxjs](../npm/rxjs.md).
- Angular Material and CDK release in lockstep with the Angular major; see
  [angular-material](../npm/angular-material.md). Other Angular-coupled UI
  kits follow the framework major the same way, for example
  [primeng](../npm/primeng.md).
- Auth: [keycloak-angular](../npm/keycloak-angular.md) on
  [keycloak-js](../npm/keycloak-js.md); [jwt-decode](../npm/jwt-decode.md)
  decodes a token without verifying it.
- Messaging: [stomp-sockjs](../npm/stomp-sockjs.md) and
  [microsoft-signalr](../npm/microsoft-signalr.md). Keep the endpoint relative
  as in the same-origin idiom above.
- The compiler is [typescript](typescript.md), and the toolchain runs on
  [nodejs](nodejs.md). The built bundle is usually served by
  [nginx](../container/nginx.md).

## Major lines

### Release cadence and support window
- Through the 21 line, a major shipped about every six months and was
  supported for 18 months: 6 active, then 12 LTS. From the 22 line, a major
  ships about every 12 months and is supported for 24 months: 12 active, then
  12 LTS. Both figures are quoted in practice, and each is right for its lines.
- When a new major ships, the previous one leaves active support and gets
  only security fixes and fixes for regressions caused by third parties (a
  new browser, say).
- Deprecated APIs stay for at least two majors under the earlier policy; the
  current policy page says at least one major, about a year.

### Upgrading across majors
- `ng update` moves one major at a time. A multi-major upgrade is a chain of
  single-major hops, and each hop has its own TypeScript and Node.js
  prerequisites from the version table. Move the companion packages
  (Material/CDK, auth adapters, UI kits) with each hop.

### Standalone, `inject()`, signals and control flow
- Standalone components arrived as a developer preview in the 14 line, were
  stable from 15, and became the default in 19. `inject()` in constructors and
  field initializers and `loadComponent` date from the 14 line, and the
  `provideRouter`/`provideHttpClient` provider functions from 15.
- Built-in control flow (`@if`/`@for`/`@switch`) and stable `signal`/`computed`
  arrived with the 17 line. Signal inputs and `model()` came in later 17
  releases. Signal inputs, outputs, `model()` and signal queries were marked
  stable in 19, and `toSignal`/`toObservable` in 20.
- `provideAppInitializer()` arrived in 19, and `APP_INITIALIZER` has been
  deprecated since.

### Change detection: zone and zoneless
- Zoneless change detection was experimental
  (`provideExperimentalZonelessChangeDetection`) until the 20 line renamed it
  `provideZonelessChangeDetection`; a later 20 release marked it stable. From
  the 21 line zoneless is the default; `provideZoneChangeDetection` opts back
  into zones.

### HttpClient transport and setup
- Through the 21 line, `HttpClient` used `XMLHttpRequest` by default and
  `withFetch()` opted into `fetch`. From the 22 line `fetch` is the default,
  `withFetch()` is deprecated, and `withXhr()` opts back into XHR. XHR on the
  server is deprecated: it can forward `Authorization` headers on cross-origin
  redirects.
- The current docs say `HttpClient` can be injected without calling
  `provideHttpClient` from the 21 line; interceptors and other features still
  need the call.

### Build system
- The builder moved from the webpack `browser` builder, through
  `browser-esbuild` (a drop-in, client-only esbuild builder), to the
  esbuild-based `application` builder, the default for new projects from the
  17 line and later shipped in the separate `@angular/build` package. From the
  18 line `ng update` offers the migration. In the 22 line the webpack builders
  (`@angular-devkit/build-angular`, `@angular-devkit/build-webpack`) are
  deprecated. Moving to `application` retires webpack-only workarounds.
- New projects use Vitest for unit tests from the 21 line; earlier lines used
  Karma with Jasmine (see Testing).

### Webpack-era builds and OpenSSL 3
- Node.js 17 and later ship OpenSSL 3, which rejects algorithms older webpack
  builds rely on. Observed in practice: a webpack-based
  Angular build on Node 17 or later fails with `ERR_OSSL_EVP_UNSUPPORTED`,
  because webpack hashes with md4. Node's own release notes name the same
  error for code that uses an algorithm OpenSSL 3 no longer allows, and offer
  `--openssl-legacy-provider` as a temporary workaround.
- `NODE_OPTIONS=--openssl-legacy-provider` is the stopgap. Node 16 shipped
  OpenSSL 1.1 and never hit the error, which is why some builds stay on an
  end-of-life Node. The fix is the esbuild `application` builder, which needs
  neither.
- A floating `node` image tag crosses this boundary silently; the pitfall is on
  [nodejs](nodejs.md). Pin `engines.node` and the image major so CI and local
  agree.

### NgModule-era and generator-scaffolded apps
- Cross-major drift inside the `@angular/*` family (core on one major,
  cdk/material/animations on later ones) survives only under the
  legacy-peer-deps escape hatch; a clean install fails (see General pitfalls).
- Observed in practice: older generator-scaffolded apps can build through a
  custom webpack configuration instead of `ng build`, and inject configuration
  with webpack's `DefinePlugin` (`process.env.X`), not with
  `environment.ts`. Read the webpack config before assuming the CLI pipeline.
  The application builder's `define` option is upstream's replacement for
  that pattern.

## Upstream docs
- https://angular.dev/: official Angular documentation (current major)
- https://angular.dev/style-guide: the style guide; version-pinned copies at
  `https://v<major>.angular.dev/style-guide`
- https://angular.dev/reference/releases: release cadence, support window,
  deprecation policy
- https://angular.dev/reference/versions: Node.js, TypeScript and RxJS ranges
  per major
- https://angular.dev/update-guide: the per-hop upgrade guide
- https://angular.dev/tools/cli/build and
  https://angular.dev/tools/cli/environments: build configurations, budgets,
  CommonJS dependencies, file replacements
- https://angular.dev/tools/cli/serve: the dev server and its proxy
- https://angular.dev/tools/cli/build-system-migration: the `application`
  builder and the migration to it
- https://angular.dev/guide/http/setup and
  https://angular.dev/guide/http/interceptors: `provideHttpClient` features
  and interceptors
- https://angular.dev/guide/testing and
  https://angular.dev/guide/http/testing: unit testing and HTTP testing
- https://angular.dev/guide/zoneless: zoneless change detection
- https://angular.dev/best-practices/security: sanitization, the
  `DomSanitizer` bypass methods, CSP, Trusted Types, XSRF, SSR host checks
- https://github.com/angular/angular: Angular source repository
- https://github.com/angular/angular-cli: CLI and builders
