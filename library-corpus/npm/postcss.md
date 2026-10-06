# postcss — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
PostCSS is a CSS-to-CSS transformation engine: it parses stylesheet source
into an abstract syntax tree, hands that tree to an ordered list of plugins, and
stringifies the result back to CSS plus an optional source map. It ships no
transformations of its own. Every behavior comes from a plugin: vendor
prefixing, future-syntax lowering, nesting, minification, utility generation,
linting, asset URL rewriting.

It is almost always a **build-time** dependency rather than something application
code imports. Most front-end toolchains embed it: a framework CLI, a bundler's
CSS pipeline, or a utility-CSS framework will pull it in, which is why it shows
up in a dependency tree with no import of it anywhere in the source.

- **npm package:** `postcss`. Licence: MIT. Upstream home: postcss.org (API
  reference) and the postcss/postcss repository on GitHub. Its runtime
  dependencies are small: `nanoid`, `picocolors` and `source-map-js`.
- Config loading for most runners comes from the separate
  `postcss-load-config` package.

## Install, setup and configuration
- `npm install --save-dev postcss`, plus the plugins you list and, unless a
  toolchain already embeds it, a runner: `postcss-cli` for the command line,
  `postcss-loader` for webpack, `gulp-postcss` for gulp. Parcel has PostCSS
  built in.
- Configuration file. A `postcss.config.js` (or a `postcss` key in the
  package manifest) exporting `{ plugins: [...] }` is what every integrating
  toolchain looks for; plugins are listed there, in order. Through
  `postcss-load-config` the file may also be `.postcssrc` (JSON or YAML; an
  explicit `.json`/`.yml` extension is recommended), `.postcssrc.js`, or
  `postcss.config` with a `.js`, `.mjs`, `.cjs`, `.ts`, `.mts` or `.cts`
  extension. TypeScript configs need `tsx` or `jiti` installed, and YAML
  configs need `yaml`.
- A JavaScript config may export a function of a context object (`ctx.env`,
  `ctx.options`, and so on) to switch plugins per environment. Plugins can be
  an object keyed by plugin name (`{}` or `null` loads defaults, `false`
  skips the plugin) or an array of required plugin instances. `postcss-loader`
  treats the object form as deprecated, so use the array form in configs it
  loads. Order is top-down in both forms.
- Process options and their defaults: `from` and `to` (input and output file
  names, normally set by the runner; leave them out of the config file),
  `map` (source-map options; `postcss-load-config` defaults it to `false`),
  and `parser`, `syntax`, `stringifier` (all default to plain CSS).
- Source-map options, when a map is on: `inline` defaults to `true` (the map
  is embedded in the CSS as a Base64 comment, and `result.map` stays empty);
  `annotation` defaults to adding a comment that points at the map;
  `sourcesContent` defaults to `true` (the original source text goes into
  the map); `prev` reads an earlier tool's map from the input automatically,
  or takes one explicitly, or `false` to ignore it; `absolute` writes
  absolute paths.

## Core API / usage shape
```js
const postcss = require('postcss');

const result = await postcss([pluginA, pluginB({ option: true })])
  .process(css, { from: 'src/app.css', to: 'dist/app.css', map: { inline: false } });

result.css;        // transformed CSS
result.map;        // source map, when requested
result.warnings(); // plugin warnings
```
- `postcss(plugins)` returns a `Processor`. Create it once and reuse it for
  many files.
- **AST node types.** `Root`, `AtRule`, `Rule`, `Declaration`, `Comment`, each
  with `nodes`, `parent`, `source` (original position), and mutation helpers
  (`append`, `prepend`, `insertBefore`, `remove`, `replaceWith`, `clone`).
  `postcss.parse(css, { from })` returns a `Root` without running plugins.
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
  `Once`, `Root`, `AtRule` and `Rule` run before a node's children, and the
  `...Exit` variants after them. `prepare(result)` returns listeners built
  per run, which is where per-file state belongs. A visitor that changes the
  tree causes the changed or added nodes (and their parents) to be visited
  again, so plugins compose without a fixed number of passes; only `Once` and
  `OnceExit` never run twice.
- Plugins report through the result: `result.warn(text, { node })` for
  warnings, `throw node.error(text)` for errors tied to a source position, and
  `dependency` or `dir-dependency` messages for files a plugin read.
- **Alternative syntaxes.** A different parser/stringifier can be supplied
  (`{ syntax, parser, stringifier }`) to operate on SCSS-like or template-embedded
  CSS; the core parser handles standard CSS.

## Idioms & best practices
- **Keep it in devDependencies, not dependencies.** It is a build-only transform;
  placing it in the runtime dependency set inflates the shipped dependency graph
  and, with it, the advisory surface the project must answer for. Once moved,
  keep it moved: a careless dependency-tool run is the kind of change that
  reverts it (observed in practice).
- Treat plugin order as configuration, not formatting. Syntax-lowering
  plugins must run before prefixing; minification belongs last; a plugin that
  generates declarations must precede anything meant to transform them.
  Reordering the list changes the output.
- Always pass `from` (and `to` when writing a file). Without it, source maps
  and error messages lose their original position and every diagnostic points
  at nothing.
- Await the result. `process()` returns a lazily evaluated result; the work
  happens when it is awaited or when `.css` is read. Runners must use only the
  asynchronous API; the synchronous one is for debugging.
- Prefer the visitor API to a manual `walk` in new plugins: subscribing to a
  node type, or to a property name such as `Declaration: { color }`, is
  faster and composes better.
- Let the integrating toolchain own the config. One `postcss.config.js` at
  the project root, consumed by the bundler or framework CLI, beats several
  tool-specific plugin lists that drift apart.
- Preserve `node.source` when replacing nodes (clone and mutate rather than
  constructing fresh), or downstream source maps go wrong.
- A plugin package lists `postcss` in `peerDependencies`, not
  `dependencies`, and takes helpers such as `decl` and `list` from the
  listener's second argument rather than importing `postcss`. Two copies of
  the core in one pipeline can break the AST.
- Rely only on the documented API; upstream may change undocumented
  properties in any minor release.
- To fail a build on any warning, add `postcss-fail-on-warn` as the last
  plugin; PostCSS has no built-in option for it.

## General pitfalls
- **Reading `.css` synchronously when an async plugin is in the list throws.**
  Any asynchronous plugin makes the whole pipeline asynchronous, and the error
  message ("use async API") is easy to misread as a configuration problem.
- **It is a dependency you did not choose.** Toolchains embed it transitively, so
  the version in the lockfile is frequently decided by a framework's CLI rather
  than by the project. A direct entry in the manifest exists mainly to control
  that resolution, which is a resolution decision, not an API decision.
- The core understands syntax, not semantics. It does not know that two
  selectors are equivalent or that a declaration is redundant; anything
  semantic is a plugin's judgment, and plugins disagree.
- Non-standard syntax needs a matching parser. Feeding SCSS/Less source to
  the default parser fails, or worse, silently mangles constructs it does not
  recognize. `postcss-scss` and `postcss-less` parse those syntaxes but do not
  compile them to CSS.
- Source-map chaining is easy to break. Each stage must consume the previous
  stage's map and emit a new one; a single stage that drops the incoming map
  leaves every later position wrong, and nothing errors.
- Plugin ecosystems age faster than the core. A plugin written against an
  older plugin API, or duplicating what the modern preset already does, is the
  usual cause of a mysterious double transformation.
- **A build-only tool still carries transitive risk.** Being development-only
  reduces what ships, not what runs on a build machine with repository
  credentials: it is a mitigation of blast radius, not of exposure.

## Testing
- Test a plugin by running it through `postcss([plugin(opts)]).process(input,
  { from: undefined })` and asserting both that `result.css` equals the
  expected output and that `result.warnings()` is empty. Upstream's plugin
  boilerplate ships this as its test template, using `node:test`, and the
  plugin guidelines make tests mandatory.
- Upstream asks plugins to be tested on the active Node.js LTS and the
  current release.
- Upstream gives no testing guidance for projects that only consume PostCSS
  through a toolchain; none was observed in practice.

## Security defaults
- With a map enabled and the defaults left alone, the map is inlined into the
  output CSS and carries the original source text (`inline` and
  `sourcesContent` both default to `true`). Turn maps off, or write them to a
  separate file, for CSS you ship to users.
- A JavaScript config file is code that runs at build time with the build's
  permissions, and so is every plugin it loads.
- Upstream takes vulnerability reports through the Tidelift security contact.

## Operational behaviour
- PostCSS runs only when a build runs: a runner parses each file, applies the
  plugins, and writes CSS and maps. A processor with no plugins returns a
  no-work result that does not even parse the CSS until its root is read.
- Errors: a CSS syntax error or a `node.error` throws `CssSyntaxError`, which
  carries the file, line and column (mapped through an earlier tool's source
  map when one exists). Runners print its message and `showSourceCode()`
  rather than a JavaScript stack, and print every `result.warnings()` entry.
- Watch mode: runners watch the files named in `dependency` and
  `dir-dependency` messages and rebuild when they change; a `dir-dependency`
  without a `glob` covers the directory recursively.
- Cost grows with the number of plugins and nodes visited. Node-type and
  property-name listeners are cheaper than walking the whole tree, and a
  cheap string check before a heavy value parser saves time.

## Interop
- Common plugins: Autoprefixer (vendor prefixes from Can I Use data),
  `postcss-preset-env` (future CSS syntax), `postcss-nested`, `cssnano`
  (minification), `postcss-import`, `postcss-url`, and Stylelint, which is
  built on PostCSS.
- Runners: `postcss-loader` (webpack), `postcss-cli`, `gulp-postcss`,
  `rollup-plugin-postcss`, Parcel's built-in support, and framework CLIs that
  embed it.
- Syntaxes: `postcss-scss`, `postcss-less`, `sugarss`, `postcss-html`,
  `postcss-safe-parser` (parses broken CSS) and CSS-in-JS syntaxes.
- [bootstrap](bootstrap.md): Bootstrap's Sass source expects Autoprefixer in
  the build to match its official CSS.

## Major lines

### 7 line
- Plugins were defined with `postcss.plugin(name, fn)` and walked the tree
  with `walk*` calls.

### 8 line
- Adds the visitor API and ES module support, and deprecates
  `postcss.plugin()`. A plugin built with it still runs, but prints a
  "postcss.plugin was deprecated" warning with a link to the migration guide.
- Plugins and runners must declare `postcss` in `peerDependencies`;
  extending the AST classes is prohibited; `sourceMap.sources` are treated as
  URLs, not file paths.
- Drops old Node.js versions and the `postcss.vendor` helpers.

## Upstream docs
- Docs / repo: https://github.com/postcss/postcss
- Plugin API: https://postcss.org/api/
- Plugin directory: https://www.postcss.parts/
- Writing a plugin, plugin guidelines and runner guidelines:
  https://github.com/postcss/postcss/tree/main/docs
- Config loading: https://github.com/postcss/postcss-load-config
