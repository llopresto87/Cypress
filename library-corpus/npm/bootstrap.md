# bootstrap — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A CSS and component framework: a responsive grid, typography, prebuilt UI
components, utility classes, and optional JavaScript plugins. The npm package
is `bootstrap`; its positioning dependency for dropdowns, popovers and
tooltips is `@popperjs/core`. It can be consumed two ways: as an npm package
compiled through a Sass build, or as plain CDN `<link>`/`<script>` includes
with no bundler at all. Licence: MIT. Upstream home: getbootstrap.com, source
in the twbs/bootstrap repository.

## Install, setup and configuration
- npm: `npm install bootstrap` (plus `@popperjs/core` when you use dropdowns,
  popovers or tooltips from the separate, non-bundled build). Importing
  `bootstrap` loads every plugin onto one object; the `js/dist/*.js` files load
  plugins one at a time. The package manifest's `sass` key points to the main
  Sass source and its `style` key to the default compiled CSS.
- CDN: one `<link>` for `bootstrap.min.css` in the `<head>` and one `<script>`
  for `bootstrap.bundle.min.js` before `</body>`. The bundle includes Popper;
  `bootstrap.min.js` does not, and then Popper must load first. Include
  `bootstrap.js` or `bootstrap.min.js`, never both.
- Required page globals: the HTML5 doctype (without it styling comes out
  incomplete) and the responsive viewport meta tag
  (`width=device-width, initial-scale=1`).
- Sass customization: keep Bootstrap's files untouched and write your own
  stylesheet that imports them. Every Bootstrap variable carries `!default`,
  so an override placed after `functions` and before `variables` wins. Some
  variables default to `null` and emit nothing until set. The build needs a
  Sass compiler (Dart Sass) and Autoprefixer to match the official CSS.
- Plugin defaults are changeable globally through each plugin's
  `Constructor.Default` object, for example `bootstrap.Modal.Default.keyboard = false`.

## Core API / usage shape
- The surface is a class system: grid classes, table classes, component
  classes, and single-purpose utility classes applied directly in markup.
- No build step is required for CDN-only use: the compiled CSS/JS are dropped
  in via `<link>` and `<script>`.
- Because it is class-driven, it is usable in hand-authored static HTML with
  zero tooling; the Sass build is only needed when customizing the source.
- Only some components need the JavaScript: accordion and collapse, alerts
  (dismissing), buttons (toggle states), carousel, dropdowns, modals, navbar,
  tabs, offcanvas, scrollspy, toasts, tooltips and popovers. A page using only
  grid, content and utilities needs none. Of those, only dropdowns, popovers
  and tooltips use Popper.
- Plugins are driven by `data-bs-*` attributes in markup or by constructors:
  `new bootstrap.Modal(elementOrSelector, options)`, with
  `getInstance(el)` (returns `null` when none exists),
  `getOrCreateInstance(el, options)` and `dispose()`. Options can also come
  from `data-bs-<option>` in kebab case or a JSON `data-bs-config`; a later
  source overrides an earlier one.
- Events come in pairs: `show.bs.modal` fires at the start and can be
  cancelled with `preventDefault()`, and `shown.bs.modal` fires when the
  transition ends.
- Compiled CSS comes whole (`bootstrap.css`) or in parts
  (`bootstrap-grid.css`, `bootstrap-utilities.css`, `bootstrap-reboot.css`),
  each with a right-to-left (`.rtl`) variant.

## Idioms & best practices
- For customization, consume the npm package and compile the Sass so overrides
  live in source; reserve CDN includes for the zero-tooling / static-HTML case.
  Import only the Sass partials you need, following the order of upstream's
  own `bootstrap.scss`.
- Compose layouts from grid and utility classes rather than writing bespoke CSS
  for spacing, alignment, and responsiveness.
- In React, Vue or Angular apps use the CSS but not Bootstrap's JavaScript;
  upstream points to framework packages instead (for Angular, `ng-bootstrap`
  or `ngx-bootstrap`).
- With CDN includes, always set `integrity` together with
  `crossorigin="anonymous"`, keep the version in the URL so the hash stays
  valid, and update both on every upgrade.
- When offline delivery matters, vendor the same files with the same hashes
  into the image or static bundle instead of loading them from a CDN.
- Tooltips and popovers are opt-in for performance: initialize each one
  yourself.

## General pitfalls
- CDN-only delivery is a hard external-network dependency at render time: there
  is no offline or air-gapped fallback unless the assets are self-hosted.
- Loading any framework via CDN without Subresource Integrity (SRI) hashes is a
  supply-chain risk: a tampered or swapped CDN asset executes unchecked. The
  absence of SRI on third-party `<link>`/`<script>` includes is a general risk
  pattern, not specific to this framework. When the same file comes from
  another CDN, compare hashes of the same algorithm; a different `sha384`
  means the file was changed.
- Observed in practice: a Google Fonts stylesheet loaded next to Bootstrap
  cannot carry a fixed SRI hash, because the service generates it per
  browser. Self-host the fonts when integrity matters. The Bootstrap docs do
  not cover fonts.
- The default palette is not proof of contrast. Some default button, alert
  and form-validation colors fall below the WCAG 4.5:1 text and 3:1 non-text
  ratios, mostly on light backgrounds; measure each pairing you use.
- Bootstrap's `prefers-reduced-motion` handling covers its own transitions
  only. Custom animations on the page need their own handling.
- Plugin methods are asynchronous: they return when a transition starts, and
  a call on a component that is still transitioning is ignored. Wait for the
  matching `shown`/`hidden` event before the next call or `dispose()`.
- Bootstrap's JavaScript and a framework that owns the DOM can both mutate the
  same element, which shows up as bugs such as a dropdown stuck open.
- Only one modal at a time; nested modals are unsupported. The `autofocus`
  attribute does nothing inside a modal (focus the field on
  `shown.bs.modal`), and a modal nested inside another fixed-position element
  misbehaves, so keep modal markup near the top level.
- Tooltips: a zero-length title never shows; tooltips on hidden or disabled
  elements need a wrapper element; hide a tooltip before removing its element.
- Recent Dart Sass releases print deprecation warnings when compiling the 5
  line's Sass. Upstream says they do not stop the build and can be ignored for
  now.

## Testing
Upstream documents no testing guidance for consumers; none was observed in
practice.

## Security defaults
- Tooltips and popovers sanitize every HTML-accepting option through an
  allow-list by default (common text tags, `a` with `href`/`target`/`rel`,
  `img` with `src`/`alt`, ARIA and a few global attributes). Extend
  `allowList` with care, or replace the sanitizer through `sanitizeFn` (for
  example with DOMPurify).
- Turning sanitization off, or widening the allow-list, is outside
  Bootstrap's security model: any XSS that follows is the app's. Never pass
  API-supplied text to an `html: true` tooltip or popover unsanitized.
- `sanitize`, `sanitizeFn` and `allowList` cannot be set through data
  attributes, only from JavaScript; upstream blocks them there for security
  reasons.

## Operational behaviour
- CSS-only pages need no runtime. Plugins configured through data attributes
  need no initialization code, except tooltips and popovers, which you
  initialize yourself.
- A modal removes scrolling from `<body>` while open and closes on a backdrop
  click by default. `dispose()` destroys an instance and its stored data.
- With JavaScript disabled, plugins have no fallback; use `<noscript>` or your
  own fallback where it matters.
- If `jQuery` is present on `window` (and `<body>` has no
  `data-bs-no-jquery`), the 5 line registers its plugins as jQuery plugins and
  emits its events through jQuery, so `addEventListener` no longer sees them.

## Interop
- Popper (`@popperjs/core`) positions dropdowns, popovers and tooltips.
- Angular, React, Vue: use the CSS with the framework, and a framework-native
  component package (`ng-bootstrap`, `ngx-bootstrap`, React Bootstrap,
  BootstrapVueNext) instead of Bootstrap's JavaScript.
- Sass toolchains: Dart Sass compiles the source; Autoprefixer adds vendor
  prefixes (see [postcss](postcss.md)).
- Browser ES modules: `bootstrap.esm.js` needs an import map (or
  `es-module-shims`) to resolve its `@popperjs/core` import.

## Major lines

### 4 line
- Plugins need jQuery, then Popper, then Bootstrap, in that order; the bundle
  includes Popper but not jQuery.
- Data attributes have no `bs` prefix (`data-toggle`). Later
  4.x releases have the tooltip and popover sanitizer, with the option named
  `whiteList`.
- Supports older browsers (including Internet Explorer 10 and 11); the
  compiler was LibSass.

### 5 line
- Drops jQuery (it stays optional), moves to Popper 2, switches to Dart Sass,
  and drops Internet Explorer and legacy Edge.
- Every data attribute gains the `bs` namespace (`data-bs-toggle`), and the
  sanitizer option becomes `allowList`.
- Left and right become start and end for right-to-left support: `.ml-*` and
  `.mr-*` become `.ms-*` and `.me-*`, `.pl-*`/`.pr-*` become `.ps-*`/`.pe-*`,
  and the `.text-*-left`/`-right` classes take `start`/`end`.
- `.sr-only` becomes `.visually-hidden` (and `.visually-hidden-focusable`,
  which must not be combined with `.visually-hidden`). Form layout classes
  (`.form-group`, `.form-row`, `.form-inline`) are gone in favour of grid and
  utilities, and labels need `.form-label`.
- A later 5.x release adds color modes: `data-bs-theme="light|dark"` on
  `<html>` or on any element, with a `color-mode()` mixin; they replace the
  per-component dark variants.

## Upstream docs
- https://getbootstrap.com
- Introduction and CDN usage: https://getbootstrap.com/docs/5.3/getting-started/introduction/
- JavaScript, including the sanitizer: https://getbootstrap.com/docs/5.3/getting-started/javascript/
- Accessibility: https://getbootstrap.com/docs/5.3/getting-started/accessibility/
- Sass customization: https://getbootstrap.com/docs/5.3/customize/sass/
- Migration from the 4 line: https://getbootstrap.com/docs/5.3/migration/
- Docs for every line: https://getbootstrap.com/docs/versions/
- Source: https://github.com/twbs/bootstrap
