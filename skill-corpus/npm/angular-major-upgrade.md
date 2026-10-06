---
name: angular-major-upgrade
description: Move an Angular application across one or more major lines, one major per hop, with the companion packages, TypeScript, Node.js and the builder moved in step and each hop proven by the shipped image build. Invoke when an Angular line leaves support, an advisory is fixed only on a newer major, or a multi-major upgrade is being planned.
id: skill.angular-major-upgrade
tier: 2
kind: skill
title: angular-major-upgrade, the Angular specialization of framework-version-migration
owns:
  - angular-major-upgrade.baseline-repair
  - angular-major-upgrade.hop-procedure
  - angular-major-upgrade.builder-migration
  - angular-major-upgrade.style-parity
requires:
load_when:
  - "upgrade angular to a newer major, multi-major ng update chain"
  - "ng update writes a mixed angular family, peer dependency conflict during the angular upgrade"
  - "migrate to the application builder, drop openssl-legacy-provider"
  - "angular upgrade builds locally but the image does not"
stack:
  - library-corpus/language/angular
est_tokens: 2713
---

# Suggested skill: angular-major-upgrade

> Optional procedure, **stack-keyed** on Angular: specializes
> `skill-corpus/framework-version-migration.md`, which owns the generic
> sequence (characterize first, staged increments, the intended-delta
> allowlist, the ADR with its fallback trigger). This page adds only what an
> Angular hop needs: the baseline repair before the first hop, the per-hop
> recipe, the builder migration, the companion set, and the gates that catch
> a green unit run over a broken shippable bundle. The framework facts
> (release cadence, `ng update`'s one-major rule, the builder lineage, the
> OpenSSL 3 workaround, standalone and control-flow history) live on
> `library-corpus/language/angular.md`, Major lines; the companions' own
> facts on `library-corpus/npm/angular-material.md`,
> `library-corpus/npm/keycloak-angular.md` and `library-corpus/npm/primeng.md`.
> **Composes** `protocols/verify.md`, `protocols/ingest-library.md` (a
> companion with no release for the target major) and `agents/05-security.md`
> (the advisory re-check) by reference. Parameters: `<source-major>`,
> `<target-major>`, `<image-node>` (the Node.js line the build image uses).

## When to apply

- The Angular major in use is out of support, or an advisory is fixed only on
  a newer major, and the application must look and behave as before.
- A chain of several majors is planned: each hop is a run of this page.
- Not for a minor or patch bump inside one major.

**Hard boundary: the shipped artifact is the gate, not the unit run.** A hop
is done when the production image builds and serves, not when `ng test`
passes. Observed in practice, more than once: a unit suite stayed green while
`ng build` could not resolve a module the specs never imported.

## Step 0, before the first hop: repair the baseline

*Replaces: starting the first `ng update` on whatever the tree currently
installs.*

- **`npm ci` must pass plain**, with no `--legacy-peer-deps` and no
  `.npmrc` setting it. That flag tells npm not to install peer dependencies,
  so a lockfile written under it can lack a peer the build imports directly.
  Observed in practice: three peers the application imported vanished from
  the lockfile after installs under that flag; the image build failed on
  "Cannot find module" while the unit run stayed green. Promote a directly
  imported peer to a direct dependency at the version the last good lockfile
  had, and regenerate the lockfile with a plain `npm install`.
- **Run every install, build, test and lockfile generation on the Node.js
  line the image builds with** (`<image-node>`), and inside the range the
  current major declares (`library-corpus/language/angular.md` links the
  version table). A code-migration run is the exception: `--migrate-only`
  (step 2) fetches a temporary newer CLI that can need a newer Node.js line
  than the image's, and a migration is a source transform that does not
  depend on the runtime. Observed in practice, it had to run on a newer line. Observed in
  practice: on a Node.js line the CLI calls unsupported, `ng update`'s
  resolver misbehaved; on the image's line it did not. A local build on
  another Node.js line proves nothing about the image.
- **Record the baseline**: `ng build --configuration production` output and
  bundle sizes against the budgets, `ng lint`, the unit run by test name, and
  the production image built from the committed tree. These are the readings
  each hop is compared with.
- **Gate:** all of the above green on the unchanged major, committed as its
  own increment.

## The hop recipe, once per major

*Replaces: `ng update` straight to the target, or several majors in one
step.*

`ng update` moves one major at a time (`library-corpus/language/angular.md`).
For each hop from N to N+1:

1. **Read the hop's floors** from the version table and the update guide for
   N → N+1: the TypeScript range, the Node.js range, the `zone.js` and RxJS
   ranges, and the guide's manual steps.
2. **Move the whole framework family to one consistent set.** Every
   `@angular/*` framework package to the same version, the CLI and the build
   packages to their matching release, Material and CDK to their matching
   release, TypeScript and `zone.js` into the declared ranges. Use
   `ng update @angular/core@<N+1> @angular/cli@<N+1>` first. Observed in
   practice: on a tree with many third-party peers the resolver wrote a split
   family (some packages on N+1, others on an unrelated version), plain and
   with `--force`; the fix was to set the family's versions by hand in
   `package.json`, regenerate the lockfile with plain `npm install`, then run
   the hop's code migrations alone with
   `ng update <package> --migrate-only --from <N> --to <N+1>`.
3. **Check `package.json` after any migration run.** Observed in practice:
   `--migrate-only` fetched a newer temporary CLI, and that CLI rewrote build
   dependencies to its own newer major. Put them back to the hop's versions.
4. **Move each companion with the hop.** Material and CDK follow the
   framework's majors. Auth adapters and UI kits publish a compatibility
   table or peer range per Angular major (the companions' library pages).
   For any other package with an `@angular/*` peer, read
   `npm view <package>@<candidate> peerDependencies` before the hop: a newer
   release on the same line often widens the range (observed in practice: a
   calendar wrapper whose range stopped below the target was fixed by a patch
   release of the same line); when no release admits the target major, stop
   and take it through `protocols/ingest-library.md` and an owner decision,
   since a replacement is a new dependency. Read each companion's licence on
   its new major as well; a licence can change between lines.
5. **Apply the required migrations; defer the optional ones.** The hop's
   required schematics (removed APIs, renamed theming APIs, HTTP provider
   functions) are part of the hop. Optional bulk refactors that the update
   offers (block control flow, standalone conversion, zoneless) are a large
   diff that fixes nothing the hop broke: revert them and schedule each as
   its own increment with its own gate.
6. **Review every migration diff**, security-bearing code first (guards,
   interceptors, authentication providers). A migration's own output can be
   incomplete. Observed in practice: the HTTP-provider migration removed the
   `HttpClientModule` import but left `importProvidersFrom(HttpClientModule)`
   in a standalone bootstrap file, so the file failed to compile; the fix was the
   provider function that keeps the existing interceptor chain.
   **Then fix only what the hop broke**: TypeScript errors from the new range
   (an implicit-any or a stricter check, usually mechanical), template
   compiler errors, theming renames. A behavior change goes through the
   intended-delta allowlist (`framework-version-migration` step 5).
7. **Run the gates** (below), regenerate the lockfile on `<image-node>`, and
   build the production image. Commit the hop as one increment, with its
   before and after versions and the migrations applied.

## The builder migration, as its own hop or increment

- An older webpack-based build on Node.js 17 or later can need the
  `--openssl-legacy-provider` stopgap; a later webpack 5 release added its own
  md4 implementation for Node.js 17, so try the build without the flag first.
  The esbuild-based `application` builder needs neither
  (`library-corpus/language/angular.md`, Webpack-era builds and OpenSSL 3).
- **A namespace import of a CommonJS default export** (`import * as X from
  '<package>'`, then `new X()`) is not constructable under esbuild, and the
  build fails on it. Observed in practice, it was the one code fix the
  builder switch needed: change it to a default import
  (`import X from '<package>'`).
- **Run the official schematic**, `ng update @angular/cli --name use-application-builder`,
  rather than hand-editing `angular.json`; it maps the options that carry
  over and removes the ones that do not.
- **The output directory moves.** The `application` builder writes the
  browser bundle under `<outputPath>/browser/`, and the schematic says so.
  Either set `outputPath` to `{ "base": "<dir>", "browser": "" }` to keep the
  old layout, or change the image's copy step and the web server's root in
  the same increment. Observed in practice: left alone, the image would have
  served an empty root while the local build looked fine.
- **Check that the test builder still exists** in the package the schematic
  points the project at. Observed in practice: the switch moved the builders
  to a package that, at that major, had no Karma builder, which would have
  broken the unit gate; the test target stayed on the older build package.
- **Remove `--openssl-legacy-provider`** from scripts, `NODE_OPTIONS` and the
  image in the same increment, and prove the build passes without it.
- Do it at the first hop whose schematic offers it, as a separate increment,
  not inside a hop that already moves the framework.

## The gate set, per hop

Every gate ran green on the baseline (step 0) before it counts.

| gate | catches |
|---|---|
| plain `npm ci`, then `ng build --configuration production` on `<image-node>` | a lockfile that lacks a peer, a family split across versions, a template or type error |
| the production image builds and serves its root page | a moved output directory, a Node.js base image below the new floor |
| bundle budgets unchanged, never raised to pass | a hop that pulls in a large dependency or a builder change that defeats tree shaking |
| `ng lint` and the unit run, compared by test name with the baseline | lost or skipped specs |
| style-selector parity (below) | a theming selector the application's styles target that the new major no longer emits |
| visual comparison of key screens, where the project has one | spacing and density shifts that keep every selector |
| the advisory scan after the last hop (`agents/05-security.md`) | the advisories the upgrade was for, still present |

**Style-selector parity.** Build the global styles bundle at N and at N+1,
extract every component-library class selector each emits (for Material,
the `.mat-` prefixed ones), and intersect both with the selectors the
application's own stylesheets target. A selector the application targets
that N emitted and N+1 does not is a candidate lost override. Before calling
it lost, check whether the component library's runtime code still applies
that class to its host element (search the library's shipped `.mjs` files at
N+1): the theme bundle is not the only place a class comes from, and a class
still set at run time keeps the application's override matching even though
the theme rule keyed on it moved. A candidate that the runtime code does not
set at N+1 is a lost override, and the hop owns it. Observed in practice over five
consecutive hops: the check showed the targeted selectors unchanged at every
hop, and the candidates it raised at one hop were all false positives of
this kind. It does
not prove pixel identity; a screenshot comparison covers that. Build the two
sides in separate `git worktree`s rather than with `git stash`, which races
any other writer in the same tree.

## Node.js and the image

When a hop's Node.js range drops the image's line, move the image's Node.js
base in that hop, to a line inside the new range with the most support left
(`library-corpus/language/nodejs.md`), and pin it as `engines.node` too so
local and image builds agree. Never leave the image on an end-of-life line
because the build still passes.

## What it does not cover

- The framework's API changes per major: the update guide and
  `library-corpus/language/angular.md`.
- Replacing a companion that has no release for the target major: a new
  dependency, `protocols/ingest-library.md`.

## Reference files

- `skill-corpus/framework-version-migration.md` (the generic sequence)
- `library-corpus/language/angular.md` (Major lines, version table, builder
  lineage, OpenSSL 3)
- `library-corpus/npm/angular-material.md`,
  `library-corpus/npm/keycloak-angular.md`, `library-corpus/npm/primeng.md`
- `library-corpus/language/nodejs.md`
- `protocols/verify.md`, `protocols/ingest-library.md`,
  `agents/05-security.md`
