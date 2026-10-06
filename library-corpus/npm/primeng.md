# primeng — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Angular UI component library from PrimeTek. Its npm packages:

- `primeng`: the components (buttons, dialogs, tables, selects, menus, dynamic
  dialogs, tooltips, etc.).
- `@primeng/themes`: the themes package of earlier lines.

Current lines take their themes from `@primeuix/themes`, and icons come from
PrimeIcons. Docs live at primeng.dev (primeng.org redirects there).
Licence depends on the major line: releases through the 21 line are MIT,
except builds tagged `-lts`, which carry a separate commercial LTS licence.
From the 22 line, PrimeNG ships as part of PrimeUI under a dual
Community/Commercial licence that needs a licence key (see Major lines).

## Install, setup and configuration
- `npm install primeng @primeuix/themes`.
- Register `providePrimeNG({...})` from `primeng/config` in the application
  providers. The settings it takes, with their defaults:
  - `theme`: `{ preset, options }`. Built-in presets are Aura, Material, Lara
    and Nora. `options.prefix` names the CSS variables (default `p`, so
    `primary.color` becomes `var(--p-primary-color)`).
    `options.darkModeSelector` defaults to `system`, which emits a
    `prefers-color-scheme: dark` media query; set a class such as `.app-dark`
    for a manual toggle, or `false`/`none` to disable dark mode.
    `options.cssLayer` (default `false`) wraps the styles in a CSS cascade
    layer. `options.cssVariables` chooses whether component tokens become CSS
    variables or inlined values.
  - `ripple`: the optional click ripple, off by default.
  - `inputVariant`: `outlined` (default) or `filled`.
  - `overlayAppendTo`: where overlays attach, `self` (the host element, the
    default) or `body`.
  - `zIndex`: base z-index per component category (modal, overlay, menu,
    tooltip); layering is otherwise managed automatically.
  - `csp.nonce`: the nonce put on the style elements PrimeNG generates.
  - `filterMatchModeOptions` and `translation`: table filter modes and the
    locale strings (day and month names, ARIA labels).
  - `license`: the PrimeUI licence key, from the 22 line.
- Inject `PrimeNG` to change configuration at runtime, for example
  `ripple.set(true)` or `setTranslation(...)`.

## Core API / usage shape
- Theming uses `@primeuix/themes` (with `definePreset` + a base preset such as `Aura`).
  A theme is a base (style rules with CSS-variable placeholders) plus a preset
  of design tokens in three tiers: primitive (palettes such as `blue-500`),
  semantic (`primary.color`, with a `colorScheme` group for light and dark)
  and component (`button.background`). `definePreset(Aura, {...})` overrides
  tokens of an existing preset; `updatePreset`, `updatePrimaryPalette` and
  `usePreset` change the theme at runtime.
- Import components by their current names (e.g. `Select`, `ToggleSwitch`, `Popover`, `DatePicker`, `Drawer`); several older aliases (e.g. `Dropdown`, `InputSwitch`, `OverlayPanel`, `Calendar`, `Sidebar`) have been renamed/removed across majors.
  Each component imports on its own, so the bundle holds only what is used.
- Unstyled mode drops the token CSS entirely and leaves styling to the app,
  usually Tailwind through pass-through attributes.
- Pass-through (`pt`) maps a component's internal DOM sections to classes,
  ARIA or data attributes, per instance or globally through the `pt` option.
- `DialogService.open(Component, config)` opens a dynamic dialog and returns a
  `DynamicDialogRef`; `ref.close(value)` delivers the value to the caller's
  `onClose` stream.

## Idioms & best practices
- Prefer the native `class` attribute over component `styleClass` inputs.
- Prefer `ng-template` with a template reference variable over the `pTemplate` directive.
- Style through design tokens, preferably a custom preset, rather than
  overriding component CSS classes; upstream calls class overrides a last
  resort. Use primitive tokens for the palette, semantic tokens for shared
  design elements, and component tokens only for one component.
- Buttons: on the 20 and 21 lines, use the `pButtonIcon` / `pButtonLabel`
  directives rather than the older `icon`/`label`/`iconPos`/`loadingIcon`
  inputs. From the 22 line those directives are deprecated in turn: place the
  icon and label directly inside the `[pButton]` host and use `iconOnly` for
  icon-only buttons.
- Use the `invalid` input to mark a form component invalid; the built-in
  `ng-invalid.ng-dirty` styling remains for compatibility and is slated for
  removal.
- Provide `DialogService` in the component that opens dynamic dialogs, and
  close the open `DynamicDialogRef` in `ngOnDestroy`.

## General pitfalls
- **Renames and theming changes cluster at major boundaries:** aliases removed in a major fail to resolve, and the theming package itself has moved across majors, so both imports and theme setup break together. Consult the version-specific migration guide for current names when crossing a major.
- The name `Sidebar` means two different components. The 18 line renamed the
  old Sidebar to `Drawer` and the 20 line removed the alias; the 22 line adds
  a new, unrelated `Sidebar` component. Examples and answers written for the
  old Sidebar do not describe the new one.
- An overlay inside a `Dialog` (a select panel, say) is clipped by the
  dialog's overflow. Append it to `body` with `appendTo` or allow overflow in
  the dialog.
- On the 21 line `showTransitionOptions` and `hideTransitionOptions` still
  exist but are ignored, because animations moved to CSS.
- From the 22 line components size in `rem` against a 16px root, where
  earlier lines assumed 14px. An app with a 14px root that upgrades without
  the `-compat` preset variants sees every component resize.
- **Maintenance status:** the upstream repository is no longer under active
  development and receives security fixes only; development continues under
  PrimeUI, and published MIT versions stay MIT. Observed in practice: the
  GitHub repository was seen archived (read-only) for a time during that
  transition. The GitHub API now reports it as not archived, and its README
  states the security-fixes-only status.

## Testing
Upstream documents no testing guidance for consumers (no harnesses or test
utilities); none was observed in practice.

## Security defaults
- Tooltip content renders as text by default. Setting `escape` to `false`
  renders it as HTML, so never combine that with text from users or an API.
- Styled mode injects `<style>` elements at runtime. Under a Content Security
  Policy that restricts styles, set `csp.nonce` in `providePrimeNG` to the
  page's nonce.
- From the 22 line the licence key sits in the app configuration. Upstream
  says verification runs offline, with no telemetry or remote connection.

## Operational behaviour
- Styled mode builds its CSS variables from the preset in the browser and
  adds them as generated style elements (hence the CSP nonce). Runtime theme
  changes (`updatePreset`, `usePreset`) apply without a rebuild.
- Overlays attach to their host element unless `appendTo` or
  `overlayAppendTo` says `body`; z-indexes are assigned automatically per
  category.
- From the 21 line, animations are plain CSS, so the `provideAnimationsAsync`
  provider is no longer needed for PrimeNG.
- From the 22 line, a missing, invalid or expired licence key may make the
  components show a licence notice.

## Interop
- Angular: every PrimeNG major declares peer ranges on the matching
  `@angular/*` major and `@angular/cdk`, plus `rxjs` 6 or 7. Move it with each
  framework hop; see [angular](../language/angular.md).
- Tailwind CSS: unstyled mode plus pass-through is upstream's recommended
  pairing, and the `tailwindcss-primeui` plugin adds PrimeNG-specific
  variants.
- PrimeFlex: the 18 line and later need PrimeFlex 4; PrimeFlex 3 does not
  work with them.
- Runtime translation works with ngx-translate through
  `PrimeNG.setTranslation`.
- [rxjs](rxjs.md): `DynamicDialogRef.onClose` and other component events are
  Observables.

## Major lines

### 17 line and earlier
- Styled mode came from compiled Sass themes: a `theme.css` from
  `primeng/resources` included in the app and swapped at runtime for dark mode.
  Configuration went through `PrimeNGConfig`.

### 18 and 19 lines
- Styled mode was rebuilt on design tokens and CSS variables without Sass.
  `theme.css` and `primeng/resources` are gone, so a custom theme from the 17
  line must be recreated as a preset.
- `PrimeNGConfig` became `PrimeNG`, configured through `providePrimeNG`.
- Renames, with the old names deprecated but still working: Calendar to
  DatePicker, Dropdown to Select, InputSwitch to ToggleSwitch, OverlayPanel to
  Popover, Sidebar to Drawer. Deprecated in favour of other components: Chips
  (AutoComplete with `multiple` and no typeahead), TabMenu (Tabs without
  panels), Steps (Stepper without panels), Messages and InlineMessage
  (Message), TabView (Tabs), and `pDefer` (Angular `@defer`).
- Removed: TriStateCheckbox (Checkbox with indeterminate), DataViewLayoutOptions
  (SelectButton), `pAnimate` (`pAnimateOnScroll`), and the `.p-link`,
  `.p-highlight` and `.p-fluid` classes. The `Message` interface in
  `primeng/api` became `ToastMessageOptions`; the Message component is no
  longer closable by default and does not auto-dismiss.

### 20 line
- PrimeTek moved to semantic versioning with no breaking changes between
  majors. Styles come from `@primeuix/styles` and presets from
  `@primeuix/themes`; `@primeng/themes` still works as a wrapper.
- The 18-line deprecations above were removed.
- Deprecated, for removal in the 22 line: `@primeng/themes`, `pTemplate`,
  `styleClass` on host-enabled components, the global `inputStyle` config
  (use `inputVariant`), camelCase selectors (use kebab case), the `pButton`
  `icon`/`label`/`iconPos`/`loadingIcon`/`buttonProps` inputs, and the
  `pBadge` directive (use OverlayBadge).

### 21 line
- Pass-through attributes, unstyled mode, CSS-based animations and initial
  zoneless support. The one breaking change is that the transition-option
  inputs stop working. `pButtonIcon` and `pButtonLabel` are deprecated from
  here.

### 22 line
- First release under PrimeUI, licensed Community (free, for organisations
  under upstream's size and revenue limits) or Commercial (per developer),
  with a licence key in `providePrimeNG`. The licence file also forbids
  redistributing the package as a component library or development tool.
  Check eligibility before upgrading.
- The public GitHub repository stops active development: it receives
  security fixes for the MIT releases only, its issues are read-only, and new
  releases come from PrimeUI. Upstream states the MIT releases stay MIT.
- Removes everything deprecated in the 20 and 21 lines. Deprecates, for
  removal in the 24 line, MultiSelect (Select with `multiple`), PanelMenu,
  Password (the `pInputPassword` directive), Galleria and Image (Gallery),
  ColorPicker (InputColor), the InputMask component (a `pInputMask`
  directive), Chart and Editor (replaced by PrimeUI PRO components), and
  ScrollPanel (ScrollArea).
- The 16px root assumption and the new `Sidebar` described in the pitfalls.

## Upstream docs
- Official docs: https://primeng.dev/
- Installation and configuration: https://primeng.dev/installation,
  https://primeng.dev/configuration
- Theming: https://primeng.dev/theming/styled,
  https://primeng.dev/theming/unstyled, https://primeng.dev/passthrough
- Migration guides: https://primeng.dev/migration (one page per major from
  v19 on, which also covers the 18 line)
- Plain-text docs for tools: https://primeng.dev/llms/llms.txt (each page also
  serves as `<page>.md`)
- Source: https://github.com/primefaces/primeng (the MIT lines; security fixes
  only from the 22 line, see its README and LICENSE.md)
