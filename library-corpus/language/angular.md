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
- The idioms below (standalone bootstrap, `inject()`, signals, built-in control
  flow, functional guards and interceptors) do not exist on older majors, so
  check the project's pin before applying one.
- The modern, upstream-recommended entry point is standalone bootstrap:
  `bootstrapApplication(AppComponent, { providers: [...] })` with no root
  `NgModule`, and components declared `standalone: true`. Application-wide
  providers are passed in that bootstrap options object.
- Dependencies are obtained with the `inject()` function, in a field
  initializer or inside a function, instead of through constructor
  parameters. Route guards are plain functions (`CanActivateFn` and kin),
  not guard classes.
- HTTP is configured through `provideHttpClient`, with **functional
  interceptors** registered via `withInterceptors`, the upstream-recommended
  approach; it is one of the providers supplied at bootstrap.
- Reactivity is signal-based: `signal`, `computed` and `effect`, with signal
  inputs (`input()`, `output()`, `model()`) in place of the `@Input()`/`@Output()`
  decorators. `toSignal()` (from `@angular/core/rxjs-interop`) bridges an
  observable into a signal, which is how reactive-forms streams such as
  `valueChanges` and `statusChanges` reach a signal-based template.
- Templates use the built-in control flow blocks (`@if`, `@for`, `@switch`)
  rather than the `*ngIf`/`*ngFor` structural directives.
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
  interceptors.
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
  by file.
- Where a file departs from the guide, the guide ranks consistency within that
  file above its own rules. A departure is a reason to plan a sweep, not to leave
  one file half-converted.

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
- Server-side rendering introduces a distinct security and behavior surface
  (e.g. URL normalization / origin handling) that does not exist in
  client-only apps; whether it applies depends on whether SSR packages are used.
- **Bindings are sanitized; the bypass is the sharp corner.** Angular escapes
  interpolation and sanitizes `[innerHTML]` by default, but the security guide
  still names binding an attacker-controllable value into `innerHTML` as the
  usual XSS route. The `bypassSecurityTrust*` methods of `DomSanitizer` switch
  that protection off for one value. Treat each call as a security decision,
  and trace where each `[innerHTML]` value comes from.
- A count of `effect()` calls, or of `[innerHTML]` bindings, is not an audit.
  Whether an effect propagates state, or a bound value can carry attacker
  content, is only known once each site is read.

## Upstream docs
- https://angular.dev/: official Angular documentation (current major)
- https://angular.dev/style-guide: the style guide; version-pinned copies at
  `https://v<major>.angular.dev/style-guide`
- https://angular.dev/best-practices/security: sanitization and the
  `DomSanitizer` bypass methods
- https://github.com/angular/angular: Angular source repository
