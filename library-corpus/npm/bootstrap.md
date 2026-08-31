# bootstrap — npm

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A CSS and component framework: a responsive grid, typography, prebuilt UI
components, and utility classes. It can be consumed two ways — as an npm
package compiled through a Sass build, or as plain CDN `<link>`/`<script>`
includes with no bundler at all.

## Core API / usage shape
- The surface is a class system: grid classes, table classes, component
  classes, and single-purpose utility classes applied directly in markup.
- No build step is required for CDN-only use — the compiled CSS/JS are dropped
  in via `<link>` and `<script>`.
- Because it is class-driven, it is usable in hand-authored static HTML with
  zero tooling; the Sass build is only needed when customizing the source.

## Idioms & best practices
- For customization, consume the npm package and compile the Sass so overrides
  live in source; reserve CDN includes for the zero-tooling / static-HTML case.
- Compose layouts from grid and utility classes rather than writing bespoke CSS
  for spacing, alignment, and responsiveness.

## General pitfalls
- CDN-only delivery is a hard external-network dependency at render time: there
  is no offline or air-gapped fallback unless the assets are self-hosted.
- Loading any framework via CDN without Subresource Integrity (SRI) hashes is a
  supply-chain risk — a tampered or swapped CDN asset executes unchecked. The
  absence of SRI on third-party `<link>`/`<script>` includes is a general risk
  pattern, not specific to this framework.

## Upstream docs
- https://getbootstrap.com
