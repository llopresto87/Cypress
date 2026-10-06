# ng2-pdf-viewer — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`ng2-pdf-viewer` is an Angular component that renders PDF documents inside the
page. It wraps Mozilla's pdf.js, published on npm as `pdfjs-dist`, and adds an
Angular template API (`<pdf-viewer>`) for the source, paging, zoom, rotation,
text selection, search and load events. MIT licensed.

Upstream home: https://github.com/VadimDez/ng2-pdf-viewer (README, changelog,
source) with a demo at https://vadimdez.github.io/ng2-pdf-viewer/. pdf.js
itself lives at https://mozilla.github.io/pdf.js/ and
https://github.com/mozilla/pdf.js.

## Install, setup and configuration
- Install by Angular line, per the README: `npm install ng2-pdf-viewer` for
  Angular 12 and later (partial-Ivy library bundles), `ng2-pdf-viewer@^7`
  for Angular 4 to 11, and the 3 line for older Angular.
- The package declares no `peerDependencies`. Its runtime dependencies are
  `tslib` and `pdfjs-dist` at one exact version per wrapper release, so the
  wrapper never blocks an Angular upgrade through a peer range, and the pdf.js
  version moves only when the wrapper moves.
- Import `PdfViewerModule`. The wrapper exports an NgModule only (its
  component is not declared standalone), so a standalone component lists
  `PdfViewerModule` in its `imports`.
- The pdf.js worker runs as a separate script. By default the wrapper loads
  it from a public CDN (jsDelivr), at the path matching the bundled pdf.js
  version. To self-host it, copy the worker file from `pdfjs-dist` into the
  app's assets and set `window.pdfWorkerSrc` to its URL before the component
  is created. A version-specific `window['pdfWorkerSrc' + <pdf.js version>]`
  exists for pages that load more than one pdf.js version.
- Character maps (CMaps, needed for non-Latin text) also default to a public
  CDN (unpkg). To self-host, copy `node_modules/pdfjs-dist/cmaps` into the
  assets and bind `[c-maps-url]` to that path.

## Core API / usage shape
```html
<pdf-viewer
  [src]="pdfSrc"
  [render-text]="true"
  [original-size]="false"
  [show-all]="true"
  (after-load-complete)="onLoaded($event)"
  (error)="onError($event)"
  style="display: block; height: 80vh"
></pdf-viewer>
```

- `[src]` takes a URL string, a `Uint8Array` or `ArrayBuffer` (anything with
  `byteLength` is passed to pdf.js as data), or a pdf.js document-source
  object. A protected document is fetched with cookies through
  `{ url, withCredentials: true }`.
- Paging and layout: `[page]` / `[(page)]`, `[show-all]`, `[stick-to-page]`,
  `[original-size]`, `[fit-to-page]`, `[zoom]`, `[zoom-scale]`
  (`'page-width'` by default, or `'page-fit'`, `'page-height'`), `[rotation]`
  (steps of 90), `[autoresize]`, `[show-borders]`.
- Text: `[render-text]` turns on the selectable text layer, `[render-text-mode]`
  chooses disabled (0), enabled (1) or enhanced (2), and
  `[external-link-target]` sets where document links open.
- Events: `(after-load-complete)` passes the `PDFDocumentProxy`,
  `(page-rendered)`, `(pages-initialized)`, `(text-layer-rendered)`,
  `(on-progress)` with `loaded`/`total`, and `(error)`.
- Search: take the component with `@ViewChild(PdfViewerComponent)` and
  dispatch a `find` event on its `eventBus` (`query`, `type: 'again'`,
  `caseSensitive`, `highlightAll`, `phraseSearch`).
- A local file is read with `FileReader.readAsArrayBuffer` and the result is
  bound to `[src]`.

## Idioms & best practices
- Give the `pdf-viewer` element an explicit height (for example `100vh`).
  Without it, `[(page)]` never updates while the user scrolls.
- `[page]` is required when `[show-all]` is false.
- `[autoresize]` works only with `[original-size]="false"` and a `max-width`
  or `display` set on the element.
- Self-host the worker and the CMaps in production, so the viewer depends on
  no third-party CDN at runtime.
- Observed in practice (the README describes the `src` types but not this
  step): when a backend delivers the document as a base64 data URI, strip the
  `data:application/pdf;base64,` prefix and decode the rest into a
  `Uint8Array` or `ArrayBuffer` before binding it.
- Observed in practice: render the viewer only once the bytes exist, and check
  the content type first. The viewer renders PDFs only, so another attachment
  type needs another path.

## General pitfalls
- With the default settings the viewer needs outbound access to two public
  CDNs. A client without internet access, or behind a Content-Security-Policy
  that does not allow those origins, gets a viewer that never renders.
- Observed in practice (upstream is silent): a strict Content-Security-Policy
  must allow the worker's origin in `worker-src` (or `script-src`), whether
  the worker is self-hosted or on the CDN.
- The worker file must match the bundled pdf.js version. A self-hosted
  worker left behind after a wrapper upgrade breaks rendering; the worker file
  name also changed from `.js` to `.mjs` across pdf.js major lines.
- Security advisories reach the wrapper through its exact-pinned
  `pdfjs-dist`. Watch that package's advisories as well as the wrapper's, and
  remember that only a wrapper release moves the pdf.js version.
- The wrapper's major does not track a pdf.js major: its 10 line spans pdf.js
  2, 3 and 4. A belief that it does was observed in practice and is
  contradicted by the changelog.
- A wrapper release can raise the TypeScript floor through its pdf.js
  version. Upstream had to pin pdf.js back once when a release required a
  TypeScript newer than an Angular LTS line accepted. Check the TypeScript
  range when upgrading.
- Observed in practice on older lines: pdf.js 2 and 3 shipped CommonJS, so the
  Angular build warned unless `pdfjs-dist` was listed in
  `allowedCommonJsDependencies`. Current `pdfjs-dist` (the 4 line on) ships ES
  modules, so the allowlist entry is no longer needed there.

## Testing
Upstream documents no testing guidance for consuming apps; the library's own
suite runs under Karma and Jasmine (`ng test`). Observed in practice, on thin
evidence: a host component that renders the viewer only when bytes are
present lets a component test that supplies no document skip pdf.js
entirely.

## Security defaults
- pdf.js renders untrusted documents. Older pdf.js releases (the 2 and 3
  lines, and the 4 line before its fix) could run attacker-supplied
  JavaScript when opening a malicious PDF while pdf.js's `isEvalSupported`
  option was true, its default. The fix removed that code path; the
  workaround on an unfixed version is `isEvalSupported: false`.
- On the current wrapper line, the component sets `isEvalSupported: false`
  whenever it builds the pdf.js parameters itself, which it does while a CMap
  URL is set (the default). If `[c-maps-url]` is cleared, `[src]` reaches
  pdf.js unchanged and the flag is whatever the source object says. The
  dependable fix is a wrapper release that bundles a fixed pdf.js.
- The wrapper also enables XFA form rendering (`enableXfa: true`) in the
  parameters it builds.
- `withCredentials: true` sends the browser's cookies when fetching a
  protected document; without it the request carries none.

## Operational behaviour
- Startup: the component sets the worker URL when it is constructed, then
  loads the document when `[src]` changes. Under server-side rendering it
  returns early and renders nothing.
- Teardown: `ngOnDestroy` clears the viewer and completes its internal
  streams.
- Resource use: upstream documents no figures.
- Failure: load and render errors arrive on `(error)`. A missing or
  mismatched worker shows up as a document that never loads.

## Interop
- Angular: no peer range. The README's install table maps Angular lines to
  wrapper lines; the repository builds with recent Angular tooling.
- pdf.js: one exact `pdfjs-dist` per wrapper release; its options can be
  passed through a document-source object in `[src]`.
- Angular build: [angular](../language/angular.md) owns
  `allowedCommonJsDependencies` and the build budgets.
- Material dialogs: observed in practice, the viewer hosted inside a modal
  dialog ([angular-material](angular-material.md)). The dialog content then
  needs the explicit height described above.

## Major lines

### 3 line
For Angular before 4. Legacy only.

### 7 line
For Angular 4 to 11, on pdf.js 2. Memory-leak fixes on destroy arrived here.

### 9 line
On pdf.js 2 with a minified worker. Late in the line, the version-specific
worker URL override arrived.

### 10 line
Built with Angular 16 tooling and installed for Angular 12 and later. It
started on pdf.js 2, moved to pdf.js 3 for the security fix above, and then
to pdf.js 4, which upstream says kept backwards compatibility. On pdf.js 4
the default worker path is the `.mjs` build under `legacy/build/`.

## Upstream docs
- https://github.com/VadimDez/ng2-pdf-viewer: README (install table, options,
  worker, CMaps, search)
- https://github.com/VadimDez/ng2-pdf-viewer/blob/master/CHANGELOG.md
- https://www.npmjs.com/package/ng2-pdf-viewer
- https://mozilla.github.io/pdf.js/ and https://github.com/mozilla/pdf.js:
  pdf.js, its API options and its security advisories
