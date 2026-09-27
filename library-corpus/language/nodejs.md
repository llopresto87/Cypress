# nodejs — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Node.js is the JavaScript runtime built on V8, shipped with the `npm` package
manager. It runs JavaScript and TypeScript tooling (bundlers, linters, test
runners, the TypeScript compiler) as well as server code. Individual npm packages
have their own pages under `npm/`; this page covers the runtime and how it gets
onto a machine or an image.

## Core API / usage shape
- Node.js publishes a release schedule: which majors become LTS lines and when
  each line reaches end of life. Read the schedule rather than a remembered rule
  about which majors are LTS; the project has changed its cadence before.
- The runtime reaches a build in one of three ways:
  - **An official image** (`node:<major>` and its slim and Alpine variants), the
    usual choice when Node is the image's main job.
  - **The operating system's own `nodejs` package.** Distribution packages are
    frozen at the distribution's release, so they often lag several majors and
    may already be past end of life.
  - **A vendor package repository** (the NodeSource distributions are the common
    one), used when an image built for something else also needs a current Node.
- A package declares the Node versions it supports in `engines.node`. npm warns
  on a mismatch (`EBADENGINE`) and installs anyway unless `engine-strict` is set.

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
  time.** Security updates retire old package versions from the repository, so
  `nodejs=<exact version>` eventually stops resolving. Pin the major and record
  what was installed.
- An `engines` mismatch is a warning, not an error, by default. A green install
  does not show that the runtime matches what the packages declare.

## Upstream docs
- https://nodejs.org/en/about/previous-releases: Node.js release lines and
  their support schedule
- https://nodejs.org/docs/latest/api/: Node.js API documentation
- https://docs.npmjs.com/cli/configuring-npm/package-json#engines: the
  `engines` field
- https://github.com/nodesource/distributions: NodeSource distributions
  (setup scripts and the manual signed-apt installation guide)
