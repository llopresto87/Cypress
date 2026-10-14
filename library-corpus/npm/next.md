# next — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Next.js is a React framework for full-stack web applications: file-system
routing, server rendering and streaming, React Server Components, Server
Functions for mutations, route handlers for HTTP endpoints, image and font
optimization, and its own dev server, bundler integration and production
server. The npm package is `next`.

It ships two routers, which can live in one application and differ in almost
every API:

- **App Router** (`app/` directory): React Server Components by default,
  `"use client"` for client components, layouts, `loading`/`error` files,
  Server Functions (`"use server"`), route handlers (`route.ts`), and the
  `next/navigation` and `next/headers` APIs. Upstream recommends it for new
  applications.
- **Pages Router** (`pages/` directory): every page is a client-hydrated React
  component, data comes from `getServerSideProps`, `getStaticProps` and
  `getStaticPaths`, and `pages/_app` and `pages/_document` wrap every page.

`next` declares `react` and `react-dom` as required peer dependencies, and the
upgrade guides install all three together (with `@types/react` and
`@types/react-dom` in a TypeScript project). They are React's own packages,
used by every React project, so they are cited here, not owned: the lockstep
rule below binds them only where `next` is present. `@next/codemod` runs
through `npx` for upgrades and is never installed.

The own-package list (each needed beside `next`):

- `eslint-config-next`: needed when the project lints with ESLint and wants
  the framework's rules.
- `@next/eslint-plugin-next`: needed when the ESLint config uses the
  framework's plugin; the upgrade guides move it together with
  `eslint-config-next` and `eslint`.
- `@next/env`: needed when code outside the Next.js runtime (a test runner's
  or an ORM's config file) must load `.env*` files the way Next.js does.

Licence: MIT. Upstream home: the documentation at https://nextjs.org/docs and
the source at https://github.com/vercel/next.js.

## Install, setup and configuration
- `npx create-next-app@latest` scaffolds a project; `--yes` takes the
  recommended defaults (TypeScript, ESLint, Tailwind CSS, App Router,
  Turbopack, the `@/*` import alias). A manual install is
  `npm i next@latest react@latest react-dom@latest` plus the scripts
  `next dev`, `next build` and `next start`.
- Requirements as the docs state them for the 16 line: Node.js 20.9 or later,
  TypeScript 5.1 or later; the supported browsers are Chrome, Edge and
  Firefox 111+ and Safari 16.4+. The registry metadata declares the same Node
  floor in `engines`.
- **Which React runs.** The App Router uses the React canary build that ships
  inside `next` (it includes the stable React 19 changes); the Pages Router
  uses the React version in `package.json`. Upstream still asks for `react`
  and `react-dom` in `package.json` for tooling and ecosystem compatibility.
- **`next.config.js`** (or `.mjs`/`.ts`) holds framework settings: `images`,
  `output`, `serverExternalPackages`, `turbopack`, `cacheComponents`,
  `serverActions` (`allowedOrigins`, `bodySizeLimit`), `poweredByHeader`,
  `generateBuildId`, `deploymentId`, `cacheHandler`.
- **Images.** `next/image` optimizes only sources the config allows: local
  paths (optionally narrowed by `images.localPatterns`) and remote URLs
  matched by `images.remotePatterns` (protocol, hostname, port, pathname,
  search). `images.domains` is deprecated in favour of `remotePatterns`.
  Defaults worth knowing: `minimumCacheTTL` is 4 hours on the 16 line,
  `qualities` is `[75]` on the 16 line, `maximumRedirects` is 3 on the 16
  line, `contentDispositionType` is `attachment`, `formats` is WebP only
  until AVIF is added, and SVG is not optimized unless `dangerouslyAllowSVG`
  is set.
- **Environment variables.** Lookup order, stopping at the first hit:
  `process.env`, `.env.$(NODE_ENV).local`, `.env.local` (skipped when
  `NODE_ENV` is `test`), `.env.$(NODE_ENV)`, `.env`. `NODE_ENV` defaults to
  `development` under `next dev` and `production` for every other command.
  Only `NEXT_PUBLIC_`-prefixed variables reach the browser, and they are
  inlined into the bundle at `next build`.
- **Bundler.** Turbopack is the default for `next dev` and `next build` from
  the 16 line; `--webpack` opts out. Turbopack options live under the
  top-level `turbopack` key.
- **Linting.** From the 16 line `next lint` is gone and `next build` no longer
  lints; run ESLint or Biome from a package script.
- **Deployable output.** `output: 'standalone'` makes `next build` trace the
  files the server needs into `.next/standalone`, with a minimal `server.js`
  that runs without `node_modules`. It does not copy `public/` or
  `.next/static`; copy them into `standalone/public` and
  `standalone/.next/static`, or serve them from a CDN. `PORT` and `HOSTNAME`
  set the listen address. `output: 'export'` produces a static site (no
  server features).

## Core API / usage shape
- **App Router file conventions:** `layout`, `page`, `loading`, `error`,
  `not-found`, `template`, `default` (parallel-route fallback) and `route`
  files inside route segment folders; `[param]` folders for dynamic segments;
  `@slot` folders for parallel routes. The root layout is required and
  renders `<html>` and `<body>`.
- **Server and Client Components.** Components are Server Components unless
  a module starts with `"use client"`, which declares the boundary between
  the server and client module graphs. Props crossing that boundary must be
  serializable by React. Context providers and components that need state,
  effects or browser APIs belong on the client side of it.
- **Request-time APIs.** `cookies()`, `headers()` and `draftMode()` from
  `next/headers`, and the `params` and `searchParams` props, are
  asynchronous: `await` them in Server Components, or unwrap with React's
  `use()` in a synchronous component.
- **Server Functions.** A function in a `"use server"` module (or with an
  inline `"use server"`) can be passed to a form's `action` or called from a
  client component; React's `useActionState` and `useFormStatus` drive the
  form state. After a mutation, `revalidatePath`, `revalidateTag`, `updateTag`
  and `refresh` from `next/cache` update cached data and the client router.
- **Route handlers** (`route.ts`) export `GET`, `POST` and the other HTTP
  methods over the Web `Request`/`Response` API.
- **Proxy** (`proxy.ts`, named `middleware.ts` before the 16 line) runs before
  routing on matched requests: redirects, rewrites, header and cookie work,
  via `NextResponse`. Its `matcher` must be a constant.
- **Navigation:** `next/link` and `useRouter`, `usePathname`,
  `useSearchParams`, `redirect` and `notFound` from `next/navigation`.
- **Assets:** `next/image` (`src`, `alt`, `width`/`height` or `fill`,
  `sizes`, `quality`, `preload`, `loader`, `unoptimized`), `next/font`, and
  `next/script`.
- **Pages Router:** `getServerSideProps`, `getStaticProps` (with
  `revalidate` for incremental static regeneration), `getStaticPaths`, API
  routes under `pages/api`, `next/router`.
- **Startup hook:** an `instrumentation` file exporting `register()`, called
  once per server instance before it serves requests.

## Idioms & best practices
- Default to Server Components and push `"use client"` down to the
  interactive leaves; every module imported from a client module becomes
  client code and ships to the browser.
- Mark modules that must never reach the browser with `import 'server-only'`.
  Upstream recommends a data access layer: one server-only module that does
  authentication, authorization and data access and returns only the fields
  a caller needs, with Server Functions kept thin on top of it.
- Validate every Server Function's input at runtime (a schema library such
  as [zod](zod.md), parsed once at the boundary), and
  check authentication and authorization inside each one, reading identity
  from cookies or headers rather than from a parameter.
- Allow remote images by the narrowest `remotePatterns` entry that works:
  protocol, exact hostname, and a pathname prefix, instead of a whole host.
- Treat `NEXT_PUBLIC_` values as build-time constants. A value that must vary
  per environment from one image is read on the server at request time
  (after `connection()` or another request-time API), not inlined.
- Upgrade with the codemod (`npx @next/codemod@canary upgrade latest`), which
  moves `next`, `react` and `react-dom` together, then work through the
  version guide's checklist. Upgrade `next`, `react`, `react-dom` and the
  React type packages in one change; never move one alone. For App Router
  code the React that renders is the build inside `next`, so a `react` bump
  in `package.json` without a `next` bump does not change it.
- Prefer Turbopack; keep a custom `webpack()` config only with a reason, since
  on the 16 line it makes a default `next build` fail.
- Behind a reverse proxy, forward the public host (`x-forwarded-host`) so the
  Server Function origin check compares the right hosts; list a host in
  `serverActions.allowedOrigins` only when the proxy cannot do that.

## General pitfalls
- **A remote image host that is not allow-listed fails at request time.**
  The optimizer answers `400 Bad Request` for any protocol, hostname, port,
  path or query string `remotePatterns` does not match, and the first sign
  is a broken image, not a build error (observed in practice, and stated by
  the docs). The same 400 answers a `quality` not in `images.qualities` on a
  direct optimizer request, and a local path outside `localPatterns`.
- **Allowed hosts' redirects are followed without re-checking.** A remote URL
  that matches `remotePatterns` and redirects is followed without validating
  the redirect target against the patterns again; `maximumRedirects` bounds
  or disables this.
- **Optimized images cannot be invalidated.** Their max age is the larger of
  `minimumCacheTTL` and the upstream `Cache-Control`, and the only ways to
  refresh one early are a new `src` or deleting `<distDir>/cache/images`.
- **`NEXT_PUBLIC_` values are frozen at build.** An image built once and
  promoted through environments carries the build environment's values. A
  non-prefixed variable read in client code becomes an empty string, not an
  error.
- **A Server Function is a public POST endpoint.** It is reachable by a direct
  request, whether or not the UI calls it. A proxy matcher that excludes a
  path also skips the Server Functions posted to it, so moving a function or
  changing the matcher can silently remove proxy-side checks.
- **Proxy without a matcher runs on everything**, static files and
  `_next/image` included, so an auth redirect there can block CSS, scripts
  and images.
- **Multiple instances need shared build secrets.** Each build generates its
  own Server Function encryption key; instances built separately fail with
  "Failed to find Server Action" unless `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`
  is the same for all. Rebuilding per environment also needs a consistent
  `generateBuildId` (or a `deploymentId`).
- **The server cache is per instance.** Pages, ISR output and `fetch` cache
  data live in memory and on local disk; `revalidateTag` on one instance
  does not reach the others without a custom cache handler.
- **Streaming needs an unbuffered path.** A proxy or load balancer that
  buffers responses delivers a streamed page all at once; nginx needs
  `X-Accel-Buffering: no` or buffering off.
- **`standalone` output misses static files** until `public/` and
  `.next/static` are copied next to `server.js`.
- **Pages Router global files do not cover `app/`.** Styles in
  `pages/_app` do not apply to `app/` routes, and styles in the root layout
  do not apply to `pages/`.

## Testing
- Unit and component tests run in Vitest or Jest with React Testing Library.
  Vitest does not support `async` Server Components, and upstream recommends
  end-to-end tests (Playwright, Cypress) for them.
- With `NODE_ENV=test`, `.env.local` is not loaded, so tests see the same
  defaults everywhere; use `loadEnvConfig` from `@next/env` to load env files
  the way Next.js does in a test setup file.
- Test Server Functions as endpoints too: a direct POST without a session must
  be refused, since the UI is not the only caller.
- For image allow-lists and qualities, request `/_next/image` directly in a
  test: an unsupported host or `q` value answers 400, which a page render
  hides as a broken image. Upstream's 16-line checklist asks for exactly
  this check.

## Security defaults
- Only `NEXT_PUBLIC_` variables reach the browser; the rest are server-only.
  Putting a secret under that prefix publishes it in the bundle.
- Server Functions: action IDs are encrypted and non-deterministic, unused
  actions are dropped from the client bundle, closed-over variables are
  encrypted, the request's `Origin` host must match the app's own host
  (`serverActions.allowedOrigins` widens it), and the body limit is 1 MB
  (`serverActions.bodySizeLimit`). A request with no `Origin` header is
  allowed with a warning. None of this replaces authorization inside each
  function.
- Images: remote sources are refused unless `remotePatterns` allows them;
  SVG is not optimized unless `dangerouslyAllowSVG` is set (pair it with
  `contentDispositionType: 'attachment'` and a restrictive
  `contentSecurityPolicy`); from the 16 line, optimization of local IP
  addresses is blocked unless `dangerouslyAllowLocalIP` is set, which upstream
  says to enable only on private networks with the server-side request
  forgery risk understood.
- `x-powered-by` is sent by default; `poweredByHeader: false` removes it.
- A nonce-based Content Security Policy needs dynamic rendering, since nonces
  are applied at request time; static pages cannot carry one.
- Dynamically rendered pages are sent with
  `Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate`.
- Upstream recommends a reverse proxy in front of a self-hosted server for
  malformed requests, slow-connection attacks, payload limits and rate
  limiting.

## Operational behaviour
- `next start` (or the standalone `server.js`) is a long-running Node.js
  server. `register()` in the instrumentation file runs once at startup and
  must finish before requests are served.
- Shutdown: on `SIGINT` or `SIGTERM` the server finishes in-flight requests
  and pending `after()` callbacks before exiting; upstream recommends a drain
  period of 10 to 30 seconds.
- Image optimization runs on the server at request time, using `sharp` (an
  optional dependency of `next`), and caches results on disk; each extra
  format is cached separately. On glibc Linux it may need the memory
  allocator configuration described by `sharp`.
- The server cache defaults to memory plus local disk per instance; a custom
  `cacheHandler` (or `cacheHandlers` for `'use cache'`) moves it to shared
  storage, and the handler must serialize `Buffer` and `Map` values itself.
- A lockfile stops two `next dev` or two `next build` runs on one project
  from the 16 line.

## Interop
- [sharp](sharp.md): the image optimizer's engine; `sharp` notes on memory
  and platform packages apply to `next/image`.
- [tailwindcss](tailwindcss.md) and [postcss](postcss.md): the scaffolded
  styling pipeline.
- [typescript](../language/typescript.md): Next.js generates `tsconfig.json`
  on first run and supports `paths` and `baseUrl`; `npx next typegen`
  generates `PageProps`, `LayoutProps` and `RouteContext` helper types.
- [better-auth](better-auth.md): mounted on a route handler, with sessions
  read on the server; its page owns the handler and the cookie handling for
  Server Functions.
- [zod](zod.md): input validation for Server Functions and route handlers.
- [vitest](vitest.md) and [playwright-test](playwright-test.md): unit and
  end-to-end testing; `next` declares `@playwright/test` as an optional peer.
- [opentelemetry-sdk-node](opentelemetry-sdk-node.md): start a `NodeSDK` from
  `register()`, importing it only when `process.env.NEXT_RUNTIME === 'nodejs'`
  because it does not run on the edge runtime; upstream's lighter path is
  `@vercel/otel`. `NEXT_OTEL_VERBOSE=1` emits more framework spans.
- [nginx](../container/nginx.md) and [caddy](../container/caddy.md): the
  reverse proxy in front of `next start`; streaming needs it unbuffered.
- [nodejs](../language/nodejs.md): the Node floor moves with Next.js majors.

## Major lines

Each major is in Active LTS until the next major ships, then in Maintenance
LTS (critical fixes and security updates only) until two years after its
first release. Upstream does not recommend serving production from `canary`.

### 13 and 14 lines
- The 13 line renamed the old `next/image` to `next/legacy/image` and made the
  then-future image component `next/image` (`alt` required, no `layout`
  prop).
- The 14 line raised the Node floor to 18.17, removed `next export` in favour
  of `output: 'export'`, moved `ImageResponse` to `next/og`, removed the
  `@next/font` package in favour of `next/font`, and deprecated
  `images.domains`. Its upgrade guide pairs it with React 18.

### 15 line
- The upgrade guide sets the minimum `react` and `react-dom` at 19; the
  package's declared peer range still admits `^18.2.0` beside `^19.0.0`, and
  the Pages Router runs the React in `package.json`. `useFormState` gives way
  to `useActionState`.
- Request-time APIs (`cookies`, `headers`, `draftMode`, `params`,
  `searchParams`) became asynchronous, with temporary synchronous access
  that warns in dev.
- Caching defaults reversed: `fetch` requests and `GET` route handlers are
  no longer cached by default, and page segments are no longer reused from
  the client router cache on navigation (`staleTimes` opts back in).
- `experimental.serverComponentsExternalPackages` became
  `serverExternalPackages`; `experimental.bundlePagesExternals` became
  `bundlePagesRouterDependencies`; `runtime: 'experimental-edge'` errors;
  `NextRequest` lost `geo` and `ip`; `contentDispositionType` defaults to
  `attachment`.

### 16 line
- Node.js 20.9+ and TypeScript 5.1+; Turbopack is the default bundler, and a
  custom `webpack` config fails a default `next build`.
- Synchronous access to request-time APIs is removed, and the image-generating
  and sitemap functions receive `params` and `id` as promises.
- `middleware` is deprecated and renamed `proxy`; proxy runs on Node.js only,
  so edge middleware stays `middleware` for now. Config flags follow
  (`skipMiddlewareUrlNormalize` became `skipProxyUrlNormalize`).
- `next/image` defaults changed: `minimumCacheTTL` 60 seconds to 4 hours,
  `16` dropped from `imageSizes`, `qualities` to `[75]` (other values are
  coerced to the nearest allowed one), `maximumRedirects` unlimited to 3,
  local IPs blocked, query strings on local images need
  `localPatterns.search`; `priority` is deprecated for `preload`;
  `next/legacy/image` and `images.domains` are deprecated.
- `revalidateTag` takes a `cacheLife` profile as a second argument;
  `updateTag` and `refresh` are new; `cacheLife` and `cacheTag` lose the
  `unstable_` prefix; Partial Prerendering moves behind `cacheComponents`.
- Every parallel-route slot needs a `default.js`, or the build fails.
- Removed: AMP, `next lint` and the config's `eslint` key,
  `serverRuntimeConfig` and `publicRuntimeConfig`, `experimental.dynamicIO`
  and `experimental.useCache`, `unstable_rootParams`.
- Next.js no longer overrides a global `scroll-behavior: smooth` on navigation
  unless `<html data-scroll-behavior="smooth">` is set; `next build` no longer
  prints per-route size metrics.

## Upstream docs
- https://nextjs.org/docs: documentation (App Router and Pages Router)
- https://nextjs.org/docs/app/getting-started/installation: requirements and
  setup
- https://nextjs.org/docs/app/guides/upgrading: per-major upgrade guides
- https://nextjs.org/docs/app/api-reference/components/image: `next/image`
  props, config and version history
- https://nextjs.org/docs/app/guides/data-security: Server Function and data
  security
- https://nextjs.org/docs/app/guides/self-hosting: reverse proxy, caching,
  multi-instance and shutdown
- https://nextjs.org/docs/app/guides/environment-variables
- https://nextjs.org/support-policy: LTS phases
- https://github.com/vercel/next.js: source and releases
