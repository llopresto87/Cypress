# primeng — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Angular UI component library (buttons, dialogs, tables, selects, menus, dynamic dialogs, tooltips, etc.). MIT licensed.

## Core API / usage shape
- Theming uses `@primeuix/themes` (with `definePreset` + a base preset such as `Aura`).
- Import components by their current names (e.g. `Select`, `ToggleSwitch`, `Popover`, `DatePicker`, `Drawer`); several older aliases (e.g. `Dropdown`, `InputSwitch`, `OverlayPanel`, `Calendar`, `Sidebar`) have been renamed/removed across majors.

## Idioms & best practices
- Prefer the native `class` attribute over component `styleClass` inputs.
- Prefer `ng-template` with a template reference variable over the `pTemplate` directive.
- Use the `pButtonIcon` / `pButtonLabel` directives rather than the older `icon`/`label`/`iconPos`/`loadingIcon` button inputs.

## General pitfalls
- **Renames and theming changes cluster at major boundaries:** aliases removed in a major fail to resolve, and the theming package itself has moved across majors, so both imports and theme setup break together. Consult the version-specific migration guide for current names when crossing a major.
- **Maintenance status:** the upstream primefaces/primeng GitHub repository has been archived (read-only) as the project transitions toward PrimeUI. Published MIT-licensed versions remain installable, but expect no new upstream development on this repo.

## Upstream docs
- Official docs: https://primeng.dev/
- Migration guides: https://primeng.dev/migration
- Source: https://github.com/primefaces/primeng
