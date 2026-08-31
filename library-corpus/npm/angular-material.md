# angular-material — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Angular Material is Google's Material Design component kit for Angular: a set of
ready-made, accessible, themeable UI components (buttons, inputs, tables,
dialogs, menus, and so on). It is built on top of the Angular CDK
(`@angular/cdk`), a lower-level toolkit of behavior primitives — overlay,
portal, accessibility (a11y), drag-and-drop, layout, scrolling — that the
components use and that applications can use directly. Package name
`@angular/material` (with its peer `@angular/cdk`).

## Core API / usage shape
- **Per-feature NgModules**: components are grouped into feature modules that are
  imported where used — form-field (`MatFormFieldModule` with input/select),
  table (`MatTableModule`), dialog (`MatDialogModule`), stepper
  (`MatStepperModule`), tabs (`MatTabsModule`), snackbar (`MatSnackBarModule`),
  and many more. Import only the modules a template needs.
- **Theming**: components draw color/typography from a configured theme
  (Material palette + density), applied globally via styles.
- **CDK primitives**: `@angular/cdk` provides the overlay (floating-panel
  positioning), portal (dynamic content projection), and a11y (focus trapping,
  live announcements, key-manager) building blocks beneath overlay-based
  components like dialog, menu, tooltip, and autocomplete.
- **Services**: overlay-based components expose imperative services (e.g. a
  dialog service that opens a component and returns a reference / afterClosed
  stream; a snackbar service to show transient messages).

## Idioms & best practices
- Import Material feature modules granularly rather than one aggregate module, to
  keep the bundle lean.
- Define a single theme and let components inherit it instead of overriding
  per-component colors.
- Use the CDK directly (overlay/portal/a11y) when you need Material-grade
  behavior for a custom component rather than reimplementing focus/positioning.
- Rely on the built-in accessibility affordances (focus management, ARIA) and
  avoid breaking them with manual DOM manipulation.

## General pitfalls
- Forgetting to import the specific feature NgModule for a component used in a
  template yields a "not a known element" template error — each component group
  is its own module.
- Overlay-based components render in a CDK overlay container outside the normal
  component DOM subtree; global CSS selectors, theming, and tests must account
  for that detached location.
- Material and CDK version together and track the Angular major line; the pair
  must stay aligned with the framework version (a per-project pin concern).
  Verify that alignment explicitly rather than trusting a green install —
  `../language/angular.md` owns why a drifted `@angular/*`-family install can
  still resolve.
- Deep-styling internal component DOM via piercing selectors is brittle across
  releases as the internal markup changes; prefer supported theming APIs.

## Upstream docs
- https://material.angular.io/
- https://github.com/angular/components
