# angular — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Angular is Google's TypeScript-first web application framework, distributed as a
family of `@angular/*` npm packages (`core`, `common`, `compiler`, `forms`,
`router`, `platform-browser`, etc.) plus CLI/build tooling (`@angular/cli`,
`@angular/build`) and optional server-side rendering (`@angular/ssr`,
`@angular/platform-server`).

## Core API / usage shape
- The `@angular/*` framework packages move together on a shared major/minor
  line; the CLI/build tooling is versioned independently of them.
- The modern, upstream-recommended entry point is standalone bootstrap:
  `bootstrapApplication(AppComponent, { providers: [...] })` with no root
  `NgModule`, and components declared `standalone: true`. Application-wide
  providers are passed in that bootstrap options object.
- HTTP is configured through `provideHttpClient`, with **functional
  interceptors** registered via `withInterceptors` — the upstream-recommended
  approach; it is one of the providers supplied at bootstrap.
- SSR is opt-in: apps without `@angular/ssr` / `platform-server` (no `server.ts`,
  no SSR dependency) run purely client-side.

## Idioms & best practices
- Prefer standalone components and `bootstrapApplication` over the legacy root
  `NgModule` bootstrap. Standalone components can compose directly — for a
  simple or single-screen app they can be wired together without pulling in the
  Router at all.
- Prefer functional HTTP interceptors (`withInterceptors`) over class-based
  interceptors.
- Keep the `@angular/*` framework packages aligned on the same version line;
  upgrade them together.

## General pitfalls
- Server-side rendering introduces a distinct security and behavior surface
  (e.g. URL normalization / origin handling) that does not exist in
  client-only apps; whether it applies depends on whether SSR packages are used.
- The CLI/build tooling patch line drifts from the framework packages by design,
  so a matching framework line is no guarantee the tooling line matches.
- Within the `@angular/*` family, peer-dependency misalignment between core and
  cdk/animations/material can be masked by an installer's legacy-peer-deps escape
  hatch — silently permitting a drifted install that a clean, strict install would
  reject. Verify family alignment explicitly rather than trusting a green install.

## Upstream docs
- https://angular.dev/ — official Angular documentation
- https://github.com/angular/angular — Angular source repository
