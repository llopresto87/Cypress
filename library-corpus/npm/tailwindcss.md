# tailwindcss — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Tailwind CSS is a utility-first CSS framework and the build tool that compiles
it. Markup is styled with small single-purpose classes (`flex`, `px-4`,
`text-sm`, `hover:bg-sky-700`, `md:grid-cols-3`). At build time Tailwind scans
the project's source files as plain text for tokens that look like class names
and generates CSS only for the ones it recognises. Nothing of it runs in the
browser: the output is a static stylesheet.

The page covers the framework and its first-party integration packages; the
surface differs sharply between the 3 and 4 lines (see Major lines):

- `tailwindcss`: the framework itself (theme, Preflight base styles,
  utilities). In the 3 line it is also the PostCSS plugin and the CLI; from the
  4 line it is the CSS entry point (`@import "tailwindcss"`) that one of the
  integration packages below compiles.
- `@tailwindcss/postcss`: needed from the 4 line when the build runs Tailwind
  through PostCSS (most framework toolchains, and any build with a
  `postcss.config.*`).
- `@tailwindcss/vite`: needed from the 4 line when the build is Vite-based;
  upstream recommends it over the PostCSS plugin there.
- `@tailwindcss/cli`: needed from the 4 line when the stylesheet is compiled
  by Tailwind's own command line rather than a bundler.

Licence: MIT. Upstream home: the docs at tailwindcss.com (the 3 line's docs
at v3.tailwindcss.com), the framework source in the `tailwindlabs/tailwindcss`
repository, and the docs source in `tailwindlabs/tailwindcss.com`.

## Install, setup and configuration
- **4 line, PostCSS.** `npm install tailwindcss @tailwindcss/postcss postcss`,
  register `"@tailwindcss/postcss": {}` in `postcss.config.mjs` (or wherever
  the toolchain reads PostCSS plugins), and put `@import "tailwindcss";` at the
  top of the main stylesheet. The plugin bundles `@import`ed CSS and adds
  vendor prefixes itself, so `postcss-import` and `autoprefixer` come out of
  the plugin list. The generic PostCSS config rules are on
  [postcss](postcss.md).
- **4 line, Vite.** `npm install tailwindcss @tailwindcss/vite`, add
  `tailwindcss()` to the Vite `plugins` array, and the same
  `@import "tailwindcss";`.
- **4 line, CLI.** `npm install tailwindcss @tailwindcss/cli`, the same
  import, then `npx @tailwindcss/cli -i ./src/input.css -o ./src/output.css
  --watch`.
- **Configuration lives in CSS from the 4 line.** No configuration file is
  needed or looked for. The directives that replace it:
  - `@theme { --color-brand-500: …; --font-display: …; --breakpoint-3xl:
    120rem; }` defines **theme variables**. Each namespace drives a family of
    utilities or variants (`--color-*` the colour utilities, `--font-*`
    `font-*`, `--breakpoint-*` the responsive variants, `--spacing` the
    spacing scale, `--radius-*`, `--shadow-*`, `--animate-*`, and so on).
    Redefining a default variable overrides it; `--color-*: initial;` clears a
    whole namespace, and `--*: initial;` drops the entire default theme.
    Theme variables must sit at the top level, never nested under a selector
    or media query.
  - `@theme inline { … }` makes utilities use a variable's *value*, which is
    needed when a theme variable refers to another variable; without it the
    reference resolves where the theme variable is defined and can fall back
    unexpectedly. `@theme static` emits every theme variable, where the
    default emits only the ones used.
  - `@source "<path>"` adds a path to class scanning, `@source not "<path>"`
    excludes one, `@import "tailwindcss" source("../src")` sets the scan base
    (default: the current working directory), and `source(none)` turns
    automatic detection off. `@source inline("…")` forces classes to be
    generated (brace expansion supported), and `@source not inline("…")`
    suppresses them.
  - `@utility name { … }` registers a custom utility that works with every
    variant; `@custom-variant name (selector);` adds or overrides a variant;
    `@variant dark { … }` applies a variant inside custom CSS.
  - `@import "tailwindcss" prefix(tw);` puts a prefix on every class (as
    `tw:flex`) and on the generated variables (`--tw-…`); theme variables are
    still written unprefixed.
- **What `@import "tailwindcss"` brings in:** the cascade layers
  `theme, base, components, utilities`, then `theme.css` (the default theme),
  `preflight.css` (the base reset) and `utilities.css`. Importing those three
  files individually instead is how Preflight is left out.
- **Default theme.** The palette is defined in OKLCH, the breakpoints are
  `sm` 40rem, `md` 48rem, `lg` 64rem, `xl` 80rem and `2xl` 96rem, and the
  spacing unit is `--spacing: 0.25rem`.
- **Dark mode.** The `dark:` variant follows `prefers-color-scheme` by
  default. To drive it from a class or attribute, override it:
  `@custom-variant dark (&:where(.dark, .dark *));`.
- **3 line.** Configuration is a `tailwind.config.js` (created with
  `npx tailwindcss init`; `-p` also writes a `postcss.config.js`), found
  automatically at the project root, with the `content` globs as its
  essential key. See Major lines.

## Core API / usage shape
```css
/* app.css, 4 line */
@import "tailwindcss";

@theme {
  --color-brand-500: oklch(0.72 0.11 221.19);
  --font-display: "Inter", sans-serif;
}

@utility content-auto {
  content-visibility: auto;
}
```
```html
<button class="bg-brand-500 px-4 py-2 font-display hover:opacity-90 md:px-6">…</button>
```
- **Utilities and variants.** A class is a utility optionally prefixed by
  stacked variants (`dark:md:hover:…`), and from the 4 line variants apply left
  to right. Arbitrary values use brackets (`top-[117px]`), and a CSS variable as
  a value uses parentheses in the 4 line (`bg-(--brand)`). The important
  modifier goes at the end of the class in the 4 line (`bg-red-500!`).
- **Theme values in custom CSS.** Every theme variable compiles to a real CSS
  variable on `:root`, so custom CSS and inline styles use
  `var(--color-gray-700)` directly; JavaScript reads a resolved value with
  `getComputedStyle(document.documentElement).getPropertyValue("--shadow-xl")`.
- **Build-time functions (4 line).** `--alpha(var(--color-lime-300) / 50%)`
  compiles to a `color-mix()`; `--spacing(4)` compiles to
  `calc(var(--spacing) * 4)`.
- **`@apply`** inlines existing utilities into custom CSS (useful for styling
  markup you do not control). In a stylesheet bundled separately from the main
  one (a CSS module, a Vue/Svelte/Astro `<style>` block), `@apply` and
  `@variant` see no theme until `@reference "../app.css";` (or
  `@reference "tailwindcss";` for an uncustomised theme) is added; `@reference`
  imports definitions without emitting CSS.
- **Compatibility directives (4 line).** `@config "./tailwind.config.js";`
  loads a legacy JavaScript config, `@plugin "<package or path>";` loads a
  legacy JavaScript plugin, and `theme(--breakpoint-xl)` still works where a
  CSS variable cannot (media queries). The dot-notation `theme(colors.red.500)`
  is deprecated.

## Idioms & best practices
- **Write complete class names.** Scanning is textual, so a class assembled at
  runtime (`` `bg-${color}-600` ``) never exists in the source and is never
  generated. Map each prop value to a full, literal class string instead.
- **Keep design tokens in `@theme`, plain variables in `:root`.** Use `@theme`
  for a value that should produce utilities, and `:root` for a variable that
  should not.
- **Prefer `@utility` to `@layer components` for reusable classes in the 4
  line.** Custom utilities are sorted by the number of properties they set, so
  a component class such as `.btn` can still be overridden by a plain utility.
- **Prefer CSS variables to `@apply` in component-scoped styles.** A scoped
  stylesheet that only uses `var(--color-…)` needs no Tailwind processing, which
  upstream notes also makes the build faster.
- **Avoid CSS modules and component `<style>` blocks where possible.** The
  build runs Tailwind once per separately bundled stylesheet, so fifty CSS
  modules mean fifty Tailwind runs.
- **Use the upgrade tool for a 3 → 4 move** (`npx @tailwindcss/upgrade`, which
  needs Node.js 20 or later) on a new branch, then review the diff and check
  the pages in a browser; it migrates dependencies, the config file and
  template class names, but complex projects still need hand fixes.
- **Treat hover as an enhancement.** From the 4 line `hover:` applies only
  where the primary input supports hover, so touch devices do not get hover
  styles on tap.
- **Give an unstyled list `role="list"`** where it is really a list: Preflight
  removes list styling, and upstream notes that VoiceOver then stops
  announcing it as a list.

## General pitfalls
- **A 3-line setup under the 4 line produces no styles.** The 4 line removed
  the `@tailwind base; @tailwind components; @tailwind utilities;` directives
  in favour of `@import "tailwindcss"`, moved the PostCSS plugin into
  `@tailwindcss/postcss` and the CLI into `@tailwindcss/cli`, and no longer
  detects a `tailwind.config.js` automatically (it loads only through
  `@config`). Observed in practice: following a 3-line tutorial on the 4 line
  yields a build that succeeds and a stylesheet without the expected utilities,
  with no error; the upgrade guide documents the removals but does not describe
  the symptom.
- **Classes that are never scanned are never generated.** From the 4 line,
  files in `.gitignore`, `node_modules`, binary files, CSS files and package
  manager lockfiles are skipped, so a component library shipped in
  `node_modules` needs an explicit `@source`. In the 3 line the same symptom
  comes from `content` globs that miss a file extension or a new folder.
- **Dynamic class names** (see Idioms) fail silently in both lines.
- **Some 3-line class names changed meaning in the 4 line rather than
  disappearing.** The bare scales moved down a step (`shadow-sm` → `shadow-xs`,
  `shadow` → `shadow-sm`, and the same for `drop-shadow`, `blur`,
  `backdrop-blur` and `rounded`), so an unconverted `shadow-sm` still compiles
  but looks different. `outline-none` became `outline-hidden` (the new
  `outline-none` really sets `outline-style: none`), and `ring` became
  `ring-3` (bare `ring` is now 1px and `currentColor`).
- **Default colours changed.** Borders and dividers default to
  `currentColor` (the 3 line used `gray-200`), and placeholder text to the
  current text colour at half opacity; a project that relied on the old
  defaults must state the colour or restore it in `@layer base`.
- **Selector changes for `space-*` and `divide-*`.** The 4 line selects
  `> :not(:last-child)` and sets the bottom/end margin or border; spacing on
  inline children or extra margins on children can shift. Upstream suggests
  flex or grid with `gap` instead.
- **Transform resets.** From the 4 line `rotate-*`, `scale-*` and
  `translate-*` use the individual CSS properties, so `transform-none` no
  longer resets them and `transition-[opacity,transform]` no longer animates
  them; list `scale`, `rotate` or `translate` instead.
- **The display class no longer beats the `hidden` attribute** in the 4 line;
  remove the attribute to show the element.
- **Sass, Less and Stylus are not supported in the 4 line,** either for the
  stylesheet or for component `<style>` blocks; Tailwind itself handles
  imports, nesting (through Lightning CSS) and prefixes.
- **3 line, infinite rebuild loop:** a build tool without glob support for
  PostCSS dependency messages (webpack, for one) watches whole directories, so
  writing the output CSS inside a scanned directory retriggers the build.
  Narrow the `content` globs, or compile with the Tailwind CLI.

## Testing
Upstream documents no testing patterns for projects that use Tailwind. The
failures on this page (unscanned paths, dynamic names, a 3-line setup on the 4
line, renamed scales) show only in the compiled stylesheet and the rendered
page, so they are caught by inspecting the build output or by browser-level
tests, not by unit tests.

## Security defaults
- No runtime surface: the output is static CSS.
- A JavaScript config loaded with `@config`, and every plugin loaded with
  `@plugin` (a package name or a local path), is code that runs at build time
  with the build's permissions.

## Operational behaviour
- Build-time only. The integration (PostCSS plugin, Vite plugin or CLI)
  scans sources, generates CSS for recognised tokens and writes one
  stylesheet; with watch mode, a change to a scanned file rebuilds.
- Only CSS variables that are used are emitted unless `@theme static` asks for
  all of them.
- Every separately bundled stylesheet (CSS module, component `<style>` block)
  is another Tailwind run, which is the main build-time cost to watch.
- The 4 line is a ground-up rewrite of the engine; upstream reports full and
  incremental builds several times faster than the 3 line in its own
  benchmarks.

## Interop
- [postcss](postcss.md): in the 4 line Tailwind is one plugin,
  `@tailwindcss/postcss`, and replaces `postcss-import` and Autoprefixer; in
  the 3 line `tailwindcss` itself is the plugin, placed before `autoprefixer`.
- Vite: `@tailwindcss/vite` is the recommended integration from the 4 line.
- Vue, Svelte, Astro and CSS modules: each scoped stylesheet needs
  `@reference` to see the theme (see Core API).
- Legacy JavaScript plugins, such as `@tailwindcss/typography`, load through
  `@plugin` in the 4 line.

## Major lines

### 3 line
- Configuration is `tailwind.config.js`, found automatically at the project
  root; `content` lists the globs to scan, `safelist` forces classes,
  `darkMode` picks the strategy (`media` by default; the `selector` strategy
  replaced `class` in 3.4.1), and `theme.extend` adds tokens.
- The stylesheet uses `@tailwind base; @tailwind components; @tailwind
  utilities;`, and custom classes inside `@layer components` or
  `@layer utilities` become variant-aware utilities.
- `tailwindcss` is both the PostCSS plugin and the CLI (`npx tailwindcss -i
  … -o …`); vendor prefixes come from Autoprefixer (added automatically only by
  the CLI).
- Browser target: the latest stable Chrome, Firefox, Edge and Safari; no IE.
  The colour palette is defined in `rgb`.
- Upstream's advice for projects that must support browsers older than the
  4 line's baseline is to stay on the 3.4 release line.

### 4 line
- Configuration is CSS-first (`@import "tailwindcss"`, `@theme`, `@source`,
  `@utility`, `@custom-variant`); automatic content detection replaces
  `content`; the PostCSS plugin and the CLI moved to their own packages, and a
  first-party Vite plugin exists. `corePlugins`, `safelist` and `separator`
  from a JavaScript config are not supported, and `resolveConfig` was removed
  (read theme values as CSS variables).
- Built on cascade layers, `@property` and `color-mix()`. Upstream designs the
  line for Safari 16.4, Chrome 111 and Firefox 128 and says the 4.0 release
  does not work in older browsers. The default palette moved from `rgb` to
  OKLCH to use the wider P3 gamut.
- From 4.1, framework-specific fallbacks let pages render in older browsers:
  `oklab` colours render in older Safari, `@property`-based features (shadows,
  transforms, gradients) work in older Safari and Firefox, colours with an
  opacity modifier get inlined fallbacks, and an unsupported gradient
  interpolation falls back to the browser default. The line is still designed
  for the baseline above, and some details (a shadow colour) can differ.
- 4.1 also added `@source not` and `@source inline()` (the replacement for
  `safelist`).
- Breaking changes from the 3 line (renamed scales, `ring`, `outline-none`,
  default border and placeholder colours, `space-*`/`divide-*` selectors,
  variant stacking order, `bg-(--var)` syntax, `!` at the end, hover on
  hover-capable devices only, individual transform properties, buttons using
  `cursor: default`, dialog margins reset) are listed in Pitfalls and in the
  upgrade guide; `npx @tailwindcss/upgrade` automates most of them.

## Upstream docs
- Docs: https://tailwindcss.com/docs
- Installation (PostCSS, Vite, CLI tabs): https://tailwindcss.com/docs/installation
- Upgrade guide (3 → 4): https://tailwindcss.com/docs/upgrade-guide
- Theme variables: https://tailwindcss.com/docs/theme
- Detecting classes in source files: https://tailwindcss.com/docs/detecting-classes-in-source-files
- Functions and directives: https://tailwindcss.com/docs/functions-and-directives
- Compatibility (browsers, preprocessors, CSS modules): https://tailwindcss.com/docs/compatibility
- 4.1 release notes (older-browser fallbacks): https://tailwindcss.com/blog/tailwindcss-v4-1
- 3 line docs: https://v3.tailwindcss.com/docs
- Source: https://github.com/tailwindlabs/tailwindcss
