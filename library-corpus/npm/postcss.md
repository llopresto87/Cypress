# postcss — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
PostCSS is a **CSS-to-CSS transformation engine**: it parses stylesheet source
into an abstract syntax tree, hands that tree to an ordered list of plugins, and
stringifies the result back to CSS plus an optional source map. It ships no
transformations of its own — every behavior comes from a plugin (vendor
prefixing, future-syntax lowering, nesting, minification, utility generation,
linting, asset URL rewriting).

It is almost always a **build-time** dependency rather than something application
code imports. Most front-end toolchains embed it: a framework CLI, a bundler's
CSS pipeline, or a utility-CSS framework will pull it in, which is why it shows
up in a dependency tree with no import of it anywhere in the source.

- **npm package:** `postcss`.

## Core API / usage shape
```js
const postcss = require('postcss');

const result = await postcss([pluginA, pluginB({ option: true })])
  .process(css, { from: 'src/app.css', to: 'dist/app.css', map: { inline: false } });

result.css;        // transformed CSS
result.map;        // source map, when requested
result.warnings(); // plugin warnings
```
- **Configuration file.** A `postcss.config.js` (or a `postcss` key in the
  package manifest) exporting `{ plugins: [...] }` is what every integrating
  toolchain looks for; plugins are listed there, in order.
- **AST node types.** `Root`, `AtRule`, `Rule`, `Declaration`, `Comment` — each
  with `nodes`, `parent`, `source` (original position), and mutation helpers
  (`append`, `prepend`, `insertBefore`, `remove`, `replaceWith`, `clone`).
- **Plugin shape (visitor API).** A plugin is a function returning an object with
  a `postcssPlugin` name and visitor keys invoked as the tree is walked:
  ```js
  module.exports = () => ({
    postcssPlugin: 'my-plugin',
    Once(root, helpers) { /* whole-document work */ },
    Declaration(decl) { /* every declaration */ },
    AtRule: { media(atRule) { /* only @media */ } },
  });
  module.exports.postcss = true;
  ```
  A visitor mutating the tree causes the changed subtree to be re-visited, so
  plugins compose without a fixed number of passes.
- **Alternative syntaxes.** A different parser/stringifier can be supplied
  (`{ syntax, parser, stringifier }`) to operate on SCSS-like or template-embedded
  CSS; the core parser handles standard CSS.

## Idioms & best practices
- **Keep it in devDependencies, not dependencies.** It is a build-only transform;
  placing it in the runtime dependency set inflates the shipped dependency graph
  and, with it, the advisory surface the project must answer for. Once moved,
  keep it moved — this is the kind of change a careless dependency-tool run
  reverts.
- **Treat plugin order as configuration, not formatting.** Syntax-lowering
  plugins must run before prefixing; minification belongs last; a plugin that
  generates declarations must precede anything meant to transform them.
  Reordering the list changes the output.
- **Always pass `from`** (and `to` when writing a file). Without it, source maps
  and error messages lose their original position and every diagnostic points at
  nothing.
- **Await the result.** `process()` returns a lazily-evaluated result; the work
  happens when it is awaited or when `.css` is read.
- **Prefer the visitor API to a manual `walk`** in new plugins: it gets
  re-visiting, better performance, and cleaner composition for free.
- **Let the integrating toolchain own the config.** One `postcss.config.js` at
  the project root, consumed by the bundler or framework CLI, beats several
  tool-specific plugin lists that drift apart.
- **Preserve `node.source`** when replacing nodes (clone and mutate rather than
  constructing fresh), or downstream source maps go wrong.

## General pitfalls
- **Reading `.css` synchronously when an async plugin is in the list throws.**
  Any asynchronous plugin makes the whole pipeline asynchronous, and the error
  message ("use async API") is easy to misread as a configuration problem.
- **It is a dependency you did not choose.** Toolchains embed it transitively, so
  the version in the lockfile is frequently decided by a framework's CLI rather
  than by the project. A direct entry in the manifest exists mainly to control
  that resolution — which is a resolution decision, not an API decision.
- **The core understands syntax, not semantics.** It does not know that two
  selectors are equivalent or that a declaration is redundant; anything semantic
  is a plugin's judgment, and plugins disagree.
- **Non-standard syntax needs a matching parser.** Feeding SCSS/Less source to
  the default parser fails, or worse, silently mangles constructs it does not
  recognize.
- **Source-map chaining is easy to break.** Each stage must consume the previous
  stage's map and emit a new one; a single stage that drops the incoming map
  leaves every later position wrong, and nothing errors.
- **Plugin ecosystems age faster than the core.** A plugin written against an
  older plugin API, or duplicating what the modern preset already does, is the
  usual cause of a mysterious double transformation.
- **A build-only tool still carries transitive risk.** Being development-only
  reduces what ships, not what runs on a build machine with repository
  credentials — it is a mitigation of blast radius, not of exposure.

## Upstream docs
- Docs / repo: https://github.com/postcss/postcss
- Plugin API: https://postcss.org/api/
- Plugin directory: https://www.postcss.parts/
