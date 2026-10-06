# nodejs — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Node.js is the JavaScript runtime built on V8, shipped with the `npm` package
manager. It runs JavaScript and TypeScript tooling (bundlers, linters, test
runners, the TypeScript compiler) as well as server code. Individual npm packages
have their own pages under `npm/`; this page covers the runtime and how it gets
onto a machine or an image. The runtime is not an npm package: it arrives as
the official `node` container image, as an operating-system package named
`nodejs`, or as NodeSource's `nodejs` package from its own repository.

Upstream home: https://nodejs.org/ (docs, release schedule) and the source at
https://github.com/nodejs/node. The NodeSource distributions live at
https://github.com/nodesource/distributions.

## Install, setup and configuration
- The runtime reaches a build in one of three ways:
  - **An official image** (`node:<major>` and its slim and Alpine variants), the
    usual choice when Node is the image's main job.
  - **The operating system's own `nodejs` package.** Distribution packages are
    frozen at the distribution's release, so they often lag several majors and
    may already be past end of life.
  - **A vendor package repository** (the NodeSource distributions are the common
    one), used when an image built for something else also needs a current Node.
- NodeSource's signed apt repository, configured by hand (its "Repository
  Manual Installation" guide), takes three steps:
  1. Download the key from
     `https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key` and dearmor
     it into a keyring, for example
     `curl -fsSL <key-url> | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg`.
  2. Add a deb822 source, `/etc/apt/sources.list.d/nodesource.sources`:
     ```
     Types: deb
     URIs: https://deb.nodesource.com/node_<major>.x
     Suites: nodistro
     Components: main
     Signed-By: /etc/apt/keyrings/nodesource.gpg
     ```
     The repository URI names the major. The suite is the
     distribution-agnostic `nodistro`, not the Debian or Ubuntu codename.
  3. `apt-get update`, then `apt-get install -y nodejs`.
- NodeSource's setup script (`setup_<major>.x`, or `setup_lts.x` and
  `setup_current.x`) does the same work as a downloaded shell script. It
  installs `apt-transport-https`, `ca-certificates`, `curl` and `gnupg`,
  writes the key to `/usr/share/keyrings/nodesource.gpg` and the `.sources`
  entry with an `Architectures` line, and adds apt preferences that pin
  `nodejs` from NodeSource's origin at priority 600, so the distribution's
  own `nodejs` does not win. It accepts only `amd64` and `arm64`. The manual
  guide writes no preference file.
- The RPM equivalent is a `.repo` file pointing at
  `https://rpm.nodesource.com/pub_<major>.x/nodistro/nodejs/<arch>` with
  `gpgcheck=1`.
- A package declares the Node versions it supports in `engines.node`. npm warns
  on a mismatch (`EBADENGINE`) and installs anyway unless `engine-strict` is set.
  Upstream describes the field as advisory: without `engine-strict` it only
  produces warnings.
- `NODE_OPTIONS` passes command-line options to every `node` process through
  the environment (a space-separated list). Options on the actual command line
  override it.

## Core API / usage shape
- Node.js publishes a release schedule: which majors become LTS lines and when
  each line reaches end of life. Read the schedule rather than a remembered rule
  about which majors are LTS; the project has changed its cadence before.
- Under the current plan a new major is branched every six months.
  Even-numbered majors become LTS lines; odd-numbered majors never do. A line
  moves through Current, Active LTS (audited fixes and features) and
  Maintenance (critical fixes and security updates), then reaches end of life.
  Upstream says production should run only Active LTS or Maintenance LTS
  lines.
- Each Node major bundles its own npm. `node --version` and `npm --version`
  report what an image or a machine actually runs.
- The runtime carries its own test runner, the `node:test` module (`node --test`
  runs it), stable from the 20 line.

## Idioms & best practices
- **Match the major the consuming build uses.** Any image or toolchain that runs
  a project's JavaScript tooling (lint, audit, SBOM, tests) should run the same
  Node major as the project's own build. Define it as "match the build image"
  and move the two together; do not track it as an independent number.
- **Choose the vendor install method deliberately, and record the choice.** A
  vendor repository offers two routes:
  - **Signed apt repository:** download the vendor key, dearmor it into
    `/etc/apt/keyrings/`, and add a deb822 `.sources` entry whose `Signed-By`
    names that keyring; then install `nodejs` with apt. No downloaded script is
    executed. Take the key's fingerprint from the downloaded key itself
    (`gpg --show-keys --with-fingerprint`), never from prose.
  - **The vendor's setup script** (`setup_<major>.x`): download and run a shell
    script that does the keyring and source setup for you. It is the vendor's own
    maintained script, but it is still download-and-execute at build time.
  Either can be right. Leaving the choice as an unexamined default is the
  mistake.
- Pin a vendor-repository install to the **major** (the repository URL or script
  names it), and record the installed version at build time, for example by
  writing `node --version` and `npm --version` into a manifest in the image.
- Verify the method and the versions inside the built image. A plan or a brief
  that names the install method proves nothing about the Dockerfile. Observed
  in practice: a brief required the signed-apt route while the Dockerfile ran
  the setup script.
- Pin the image major (`node:<major>`), and set `engines.node` in
  `package.json`, so CI, local machines and the build image agree.

## General pitfalls
- **A different major is a different analysis.** Each Node major bundles its
  own npm, and packages declare the majors they support. Running `npm ci`, a
  linter or a test runner under a major other than the project's build can
  resolve and behave differently from the build it is meant to check. An
  `EBADENGINE` warning on first run is the usual symptom.
- **Never substitute the distribution's `nodejs` package for the vendor
  repository without checking its major.** It installs cleanly and may be
  several majors behind and past end of life.
- **An exact version pin against a vendor apt repository breaks the build over
  time.** Observed in practice: security updates retire old package versions
  from the repository, so `nodejs=<exact version>` eventually stops resolving.
  Pin the major and record what was installed. NodeSource's own wiki shows how
  to install an exact version (`apt-cache policy nodejs`, then
  `apt-get install nodejs=<version>`) and says nothing about how long a
  version stays available.
- An `engines` mismatch is a warning, not an error, by default. A green install
  does not show that the runtime matches what the packages declare.
- A floating `node` image tag (no major) is a different runtime on every pull.
  It is how a CI pipeline silently crosses a major boundary, such as the
  OpenSSL 3 change below.
- A repository configured under NodeSource's older layout (a
  `nodesource.list` with a distribution codename) has to be removed, key and
  list together, before the `nodistro` source is added.

## Testing
- For a Node install in an image, the test is a smoke run inside the built
  image: `node --version` and `npm --version`, checked against the intended
  major. Reading the Dockerfile is not the same check.
- For code, the built-in `node:test` runner needs no extra dependency; projects
  on a framework usually use that framework's runner instead.

## Security defaults
- The signed-apt route verifies every package against the keyring named in
  `Signed-By`, and no downloaded script runs. The setup-script route runs a
  downloaded shell script as root at build time.
- Node 17 and later ship OpenSSL 3, which rejects legacy algorithms and short
  key sizes by default. `--openssl-legacy-provider` turns the legacy provider
  back on for the whole process, which upstream presents as a temporary
  workaround, not a setting to keep.
- A line past end of life gets no security fixes, and a Maintenance line gets
  only critical ones. The distribution's own `nodejs` package is the usual way
  an image ends up on an end-of-life line.

## Operational behaviour
- In a static web app's image, Node usually runs only in the build stage; the
  shipped image serves files and carries no Node. Code that runs Node in
  production needs the same major in the runtime stage as in the build stage.
- `NODE_OPTIONS` set in an image or a CI job applies to every `node` process
  there, including tools that did not ask for it.
- An apt-based install updates within the major on every rebuild unless the
  version is pinned, which is why the installed version is recorded at build
  time.

## Interop
- npm ships with Node; per-package facts live on the `npm/` pages.
  `npm run <name>` also runs `pre<name>` and `post<name>` scripts when they
  exist (not under `--ignore-scripts`), so a check wired as `prebuild` runs in
  every image build that calls `npm run build` while no pipeline file names it.
  The general rule of following the invocation chain is in
  [`protocols/verify-disagreement.md`](../../protocols/verify-disagreement.md).
- [typescript](typescript.md): `@types/node` should follow the Node line the
  code runs on.
- [angular](angular.md): each Angular major declares the Node range it
  supports, and the Angular page owns the OpenSSL 3 and webpack build fact.
- [docker](../container/docker.md): the `node:<major>` images and multi-stage
  builds.

## Major lines

### Even and odd majors
- Even-numbered majors become LTS lines and odd-numbered majors stay Current
  only, under the current release plan. Check the schedule before relying on
  it.

### The 17 line and OpenSSL 3
- Node 17 moved to OpenSSL 3. Code that uses an algorithm OpenSSL 3 no longer
  allows by default fails with `ERR_OSSL_EVP_UNSUPPORTED`, and
  `--openssl-legacy-provider` was added as a temporary workaround. The
  consequence for webpack-era front-end builds, and the fix, are on
  [angular](angular.md) (Major lines, "Webpack-era builds and OpenSSL 3").

### NodeSource repository layout
- NodeSource now publishes DEB and RPM packages under the single `nodistro`
  suite instead of one suite per distribution release, with a `.sources` file
  (deb822) where older guides wrote a `nodesource.list`. Older instructions that
  name a distribution codename describe the retired layout.

## Upstream docs
- https://nodejs.org/en/about/previous-releases: Node.js release lines and
  their support schedule
- https://github.com/nodejs/Release: the release plan and phases
- https://nodejs.org/docs/latest/api/: Node.js API documentation
  (`cli.html` for `NODE_OPTIONS` and `--openssl-legacy-provider`, `test.html`
  for the test runner)
- https://docs.npmjs.com/cli/configuring-npm/package-json#engines: the
  `engines` field
- https://docs.npmjs.com/cli/using-npm/scripts: `pre` and `post` lifecycle
  scripts
- https://github.com/nodesource/distributions: NodeSource distributions
  (setup scripts and the manual signed-apt installation guide)
- https://github.com/nodesource/distributions/wiki/Repository-Manual-Installation:
  the manual signed-apt and RPM setup
