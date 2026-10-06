# angular-material — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Angular Material is Google's Material Design component kit for Angular. It
ships as two packages from one repository, and the page covers both:

- `@angular/material`: a set of ready-made, accessible, themeable UI
  components (buttons, inputs, tables, dialogs, menus, and so on).
- `@angular/cdk`: the Angular CDK, the peer that Material is built on top of:
  a lower-level toolkit of behavior primitives (overlay, portal,
  accessibility (a11y), drag-and-drop, layout, scrolling, test harnesses) that
  the components use and that applications can use directly.

Licence: MIT.
Docs live at material.angular.dev (the older material.angular.io host
redirects there, and older majors keep versioned hosts such as
v18.material.angular.dev); source is the angular/components repository.

## Install, setup and configuration
- `ng add @angular/material` installs Material and the CDK, asks for a
  prebuilt or custom theme and whether to apply global typography, and then
  adds the Roboto and Material Symbols fonts to `index.html` plus a few global
  styles (no `body` margin, `height: 100%` on `html` and `body`, Roboto as the
  default font).
- A theme is required. Either add a prebuilt theme CSS file from
  `@angular/material/prebuilt-themes/` to the `styles` array in
  `angular.json`, or write a Sass theme file (see Core API).
- `MatIconRegistry` fetches remote SVG icons through `HttpClient`, so an app
  that registers icons by URL needs `provideHttpClient()`; without it the
  registry fails at runtime.
- App-wide defaults are injection tokens, each replacing a built-in default:
  `MAT_FORM_FIELD_DEFAULT_OPTIONS` (`appearance`, default `fill`),
  `MAT_SNACK_BAR_DEFAULT_OPTIONS` (for example a default `duration`),
  `MAT_DIALOG_DEFAULT_OPTIONS` and `MAT_TOOLTIP_DEFAULT_OPTIONS` (show and hide
  delays). Paginator labels and their ARIA text come from a `MatPaginatorIntl`
  you provide.

## Core API / usage shape
- **Per-feature NgModules**: components are grouped into feature modules that are
  imported where used (in recent lines the components and directives are also
  standalone, so a standalone component can list them directly in `imports`, and
  the NgModule is a convenience bundle), for example form-field (`MatFormFieldModule` with input/select),
  table (`MatTableModule`), dialog (`MatDialogModule`), stepper
  (`MatStepperModule`), tabs (`MatTabsModule`), snackbar (`MatSnackBarModule`),
  and many more. Import only the modules a template needs.
- **Theming**: components draw color/typography from a configured theme
  (Material palette + density), applied globally via styles. On current lines
  the `mat.theme` Sass mixin takes a map of `color` (a palette or a map with
  `primary`, `tertiary` and `theme-type`), `typography` (a font family or a
  map of plain and brand families and weights) and `density` (0 down to -5,
  each step about 4px tighter), and emits `--mat-sys-*` CSS variables. Colors
  use the CSS `light-dark()` function, so the app's `color-scheme` picks the
  mode; with no `color-scheme` declared, the light colors always apply.
- Token overrides: `mat.theme-overrides` (or the `$overrides` argument of
  `mat.theme`) changes system tokens, and each component has its own
  `mat.<component>-overrides` mixin. The override API validates token names,
  and upstream presents it as the way to stay compatible when tokens are
  added, moved or renamed.
- **CDK primitives**: `@angular/cdk` provides the overlay (floating-panel
  positioning), portal (dynamic content projection), and a11y (focus trapping,
  live announcements, key-manager) building blocks beneath overlay-based
  components like dialog, menu, tooltip, and autocomplete.
- Overlay-based components expose imperative services. The
  dialog service opens a component and returns a `MatDialogRef`, whose
  `afterClosed()` stream emits the value passed to `close(result)`; the dialog
  component reads its input through the `MAT_DIALOG_DATA` token. The snackbar
  service shows transient messages.

## Idioms & best practices
- Import Material feature modules granularly rather than one aggregate module, to
  keep the bundle lean.
- Define a single theme and let components inherit it instead of overriding
  per-component colors. Style your own components from the theme's
  `--mat-sys-*` variables (or the `mat.system-classes()` utility classes) so
  they follow the theme and its dark mode.
- Set app-wide component defaults once through the injection tokens above,
  not per instance.
- Spread the built-in defaults when overriding dialog defaults:
  `{...new MatDialogConfig(), disableClose: true}`. A per-call `open()` config
  is merged on top and always wins.
- Use the CDK directly (overlay/portal/a11y) when you need Material-grade
  behavior for a custom component rather than reimplementing focus/positioning.
- Rely on the built-in accessibility affordances (focus management, ARIA) and
  avoid breaking them with manual DOM manipulation. Give every dialog an
  `ariaLabel` or `ariaLabelledBy`, and every paginator an `aria-label`.
- Turn on `mat.strong-focus-indicators()` when the default focus styling is
  too faint for your contrast requirements.

## General pitfalls
- Forgetting to import the specific feature NgModule (or, in a standalone
  component, the component or directive itself) for a component used in a
  template yields a "not a known element" template error.
- Overlay-based components render in a CDK overlay container outside the normal
  component DOM subtree; global CSS selectors, theming, and tests must account
  for that detached location.
- Material and CDK version together and track the Angular major line; the
  triple (core, material, cdk) must stay aligned with the framework version
  (a per-project pin concern). Verify that alignment explicitly in the
  lockfile's resolved versions, not only the declared ranges, rather than
  trusting a green install: `../language/angular.md` owns why a drifted
  `@angular/*`-family install can still resolve.
- Deep-styling internal component DOM via piercing selectors is brittle across
  releases as the internal markup changes; prefer supported theming APIs.
  Upstream treats component DOM and CSS classes as private and may change them
  in any release.
- One aggregate "material module" that re-exports every Material module puts
  all of them into whichever bundle imports it, so adding a module there is a
  bundle-wide decision (observed in practice; upstream advises granular
  imports but does not discuss the aggregate pattern).
- `MAT_DIALOG_DEFAULT_OPTIONS` replaces the built-in defaults wholesale.
  Providing only `{disableClose: true}` leaves `hasBackdrop` and the rest
  `undefined`.
- Density below 0 can hurt accessibility, and it does not apply to pop-up
  contexts such as the date picker.
- The snackbar does not take focus. Do not give a snackbar that carries an
  action a `duration`, and offer the same action somewhere else.

## Testing
- Test through the CDK component harnesses instead of querying internal DOM.
  Create a loader with `TestbedHarnessEnvironment.loader(fixture)` (from
  `@angular/cdk/testing/testbed`) and load harnesses such as
  `MatButtonHarness` (from `@angular/material/button/testing`) with
  `getHarness` or `getAllHarnesses`.
- Narrow the search with `getChildLoader(selector)` or the harness's static
  `with({ selector, ancestor, ... })` predicate rather than array indexes.
- Every harness method is async. Harnesses run change detection and wait for
  the fixture to be stable on their own, so the test drops its
  `detectChanges()` and `whenStable()` calls.
- Overlay content (dialogs, menus, select panels) sits outside the fixture.
  Load its harnesses from `TestbedHarnessEnvironment.documentRootLoader(fixture)`.
- Harnesses also run in Selenium WebDriver end-to-end tests through
  `@angular/cdk/testing/selenium-webdriver`.

## Security defaults
- `MatIconRegistry` requires every SVG URL and HTML string to be marked as
  trusted through Angular's `DomSanitizer`, as its guard against XSS. Marking a URL or string as trusted
  bypasses that guard, so trust only content your app controls.
- Remote SVG icons load through `HttpClient`, so they obey the same-origin
  policy: an icon URL must share the page's origin, or its server must allow
  cross-origin requests.

## Operational behaviour
- Overlay components attach their panels to an overlay container near the
  document root. An overlay created directly through the CDK uses the no-op
  scroll strategy by default; give a custom panel a reposition, close or
  block strategy.
- A dialog traps focus inside itself, focuses the first tabbable element by
  default (`autoFocus`), closes on Escape (unless `disableClose` is set, which
  breaks the expected dialog keyboard pattern), and completes its `MatDialogRef`
  streams when it closes.
- The snackbar announces through an `aria-live` region, `polite` by default.
- Theme styles are global CSS. Inside Shadow DOM, the theme must be loaded in
  each shadow root that holds a Material component.

## Interop
- Angular: Material and CDK release in lockstep with the framework major. See
  [angular](../language/angular.md).
- `HttpClient` is needed for remote SVG icons; `@angular/animations` is no
  longer needed on current lines (see Major lines).
- Fonts: `ng add` links Roboto and the Material Symbols icon font in
  `index.html`. Angular CLI projects inline Google Fonts stylesheets at build
  time by default.

## Major lines

### 15 line: MDC-based components
- Most components were reimplemented on Material Design Components (MDC). The
  TypeScript API stayed largely the same, but the DOM and CSS class names
  changed, so custom CSS copied from earlier examples no longer matches.
  `mat-chip-list` split into `mat-chip-set`, `mat-chip-listbox` and
  `mat-chip-grid`, and the slider gained a new API with an
  `<input matSliderThumb>`.
- The pre-MDC versions shipped alongside as `mat-legacy-*` components for the
  transition. They were removed in the 17 line.

### 18 and 19 lines: Material 3 theming
- The 18 line renamed the Material 2 Sass API with an `m2-` prefix
  (`m2-define-light-theme`, `$m2-indigo-palette`, and so on); `ng update`
  rewrites the names.
- From the 19 line, theming uses the `mat.theme` mixin and `--mat-sys-*`
  variables described above. An app whose theme still uses
  `mat.define-theme`, `define-light-theme` or `define-dark-theme` follows the
  theming guides on the v18 docs host. Of the eight prebuilt themes, four are
  Material 3 and four are Material 2; upstream says the M2 ones will be
  removed in a future version.

### Animations
- Up to the 19 line, `ng add` also installed `@angular/animations` and set up
  `BrowserAnimationsModule` (or `provideAnimations`). From a later 19.x
  release the components no longer depend on the animations package, and the
  21 line removed the exported per-component animation symbols
  (`matDialogAnimations` and the like).

## Upstream docs
- https://material.angular.dev/ (material.angular.io redirects here)
- Guides: getting started, theming, theming your components, using component
  harnesses: https://material.angular.dev/guide/theming
- CDK: https://material.angular.dev/cdk/categories
- https://github.com/angular/components (guides and per-component docs in the
  repository, and the CHANGELOG for major-line breaking changes)
