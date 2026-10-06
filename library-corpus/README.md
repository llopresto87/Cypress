# Library corpus

**Project-agnostic, durable** notes for third-party libraries, languages,
runtimes and platforms, their version facts stated with what they qualify. A
plant pulls a page with `install.sh <host> --expertise <id>`, or reads it here
when `ingest-library` runs inside the seed. New pages enter through the
**harvest** protocol (`protocols/harvest.md`).

## Purpose

Ingesting a dependency is expensive, and most of that cost is paid rediscovering
the same **surface** every time: what the library is for, its core API, how it
is idiomatically used. That surface barely moves between versions. This corpus holds
it, so the next project starts from a page it can work from and then ingests
only the version-specific delta.

The next plant's `ingest-library` **checks this corpus first**: if a surface
page exists, it seeds the project's `docs/graph/libraries/<name>.md` from it as
the orientation layer, then fetches only the pinned facts it needs (exact
version, its advisories, its deprecations) against the project's real lockfile.
A version fact the page already states narrows that fetch: the project confirms
it against its own pin instead of rediscovering it.

## The admission bar: withdraw-ready

A page lands here only when a new plant could adopt it **instead of running a
research-scout on that library's surface**. A page that only orients the reader
and leaves the scout to run anyway is a thin slice, and it waits until it is
complete. A withdraw-ready page covers, under the library's own name:

- its purpose and upstream home (the docs and the source repository);
- install, setup and configuration semantics: what each setting means and what
  its default does;
- its core API and canonical usage, written for the general case and never a
  project's call-sites;
- the idioms and best practices that hold across releases;
- its pitfalls, including the battle-tested ones a plant learned in production;
- its testing patterns;
- its security defaults, and what a careless setting opens;
- its operational behaviour: startup, shutdown, resource use, failure and
  recovery;
- its interop with the libraries it is commonly used beside;
- a section per major line wherever the surface differs between major lines.

A section with nothing to say for that library says so in one line, so a
reader can tell a gap from an omission. Pages admitted before this bar was set
may fall short of it; they stay orientation until a later pass brings them up to
it.

**Provenance of an observed fact.** A fact a plant observed, which upstream
contradicts or says nothing about, stays on the page. It is labelled as
observed, with the conditions it was observed under and what the upstream docs
say on the point, and it is never silently resolved in either direction: the
next reader decides with both in front of them. A fact no plant observed and no
upstream source supports, which a worker supplied from its own knowledge, does
not land until a fetched source confirms it (`protocols/harvest.md` §Phase 1, "A
plant fact may be wrong"). An observed fact carries no version of the plant that
observed it.

## What belongs here (surface, durable)

- The capability the library provides; its ecosystem and canonical package name.
- Its core API shape and canonical usage, in general form.
- Idioms and best practices that hold **across releases**.
- Pitfalls inherent to the tool, and the ones plants met using it.
- The upstream doc and repository home.
- Differences between **major lines** of the page's own subject, each in its
  own section.
- **Version facts** that the library's own release notes or documentation state,
  each written with the subject it qualifies: the minimum version a feature or
  setting needs, the version where a behaviour, a default or a coordinate
  changed, a deprecation or removal version, a pitfall bound to some versions
  only.

## What stays OUT

These are the *project's* concern, or are kept out until the owner rules
otherwise, so they never enter the corpus:

- Security facts: CVE ids, advisories, and any fact whose purpose is to warn
  about an exposure in some releases. Vulnerability scanners and advisory feeds
  own them. A page's security defaults section (what a setting opens) is
  configuration and stays.
- A project's own version: the version one project runs or resolved. It is
  never stated here and never cited as evidence ("seen on N"); it lives in the
  project's own page, §0, rediscovered by `ingest-library` against its
  lockfile.
- A bare version number with nothing attached to it. A version earns its place
  by the fact it qualifies ("from N the default is X"), never on its own.
- Calendar dates, except a platform page's retrieval date (the last rule
  below).

**A major line is not a pin.** The boundary between two major lines of the
page's own subject (a framework's 2 and 3 lines, say) is part of its durable
surface: it names a family of releases, not one release, and it outlives every
patch inside it. A page may therefore carry a section per major line, and a
stack-keyed skill page may be an upgrade across one. A finer version fact (a
minor or patch release where something changed, an "added in" note) is
admissible too, when the library's release notes or docs state it, written
in the section of the line it belongs to. A security fact, a calendar date and
a project's own version still stay out.

## Layout

```
library-corpus/<key>/<library>.md
```

- Keyed by **library, not version**: one page per library.
- `<key>`, the ecosystem key, is one of:
  - `language`: languages and their runtimes.
  - `npm`, `nuget`, `pypi`, `maven`: the package registries of those names.
  - `pub`: Dart and Flutter packages from the pub registry.
  - `galaxy`: Ansible collections from the Galaxy registry. Ansible itself is
    the `pypi/ansible-core` page, the package that ships it.
  - `container`: container-runtime tooling (engine, compose, and images serving
    as a runtime stage), not an installable package registry.
  - `cli`: general-purpose command-line tools that scripts and agents drive
    directly (`git`, `curl`, and build tools such as `maven`, whose page is
    `cli/maven`). They do have versions, but the host or base image supplies
    the version, not a project lockfile, so a page names the behaviors that
    differ across releases and the project records the version its machines
    run.
  - `platform`: the surfaces the last rule below admits, hosted or
    self-hosted: a platform's own CLI, its REST API, or its declarative
    pipeline or config DSL, whether a vendor runs the platform or the plant
    runs it on its own infrastructure (a virtualization or infrastructure
    manager, say).
- `<library>`: the canonical id as its ecosystem publishes it. npm drops the
  scope's `@` and reads its slash as a hyphen (`@microsoft/signalr` →
  `microsoft-signalr`); pypi uses the normalized form, lowercase with hyphens;
  nuget keeps the id as written, case included; pub keeps its underscores
  (`shared_preferences`); galaxy keeps the dotted collection name
  (`community.general`). Every other key uses the lowercased name.
- A page that covers packages beyond its `<library>` names them in its
  `## What it is` section in the shape SPEC-0001 §6 sets, "The own-package
  list" (`docs/specs/SPEC-0001-install-placement.md`). Each item there says
  when its package is needed, and material that holds for one package only
  names it, so a plant that uses a subset can tell the parts it adopts from
  the parts it leaves.

The `skill-corpus/` keys are these keys: a stack-keyed skill page lives at
`skill-corpus/<key>/<name>.md` under the key of the library it is bound to
(`skill-corpus/README.md`), and a `stack:` field on a skill or tool page names
pages of this corpus by their id, `library-corpus/<key>/<library>`.

**Admitting a new key.** A key is added together with its first page, never
ahead of it, and only when three things hold: the surface has its own naming
authority (a registry, or a published id scheme) so a page's name is the
canonical id without translation; no existing key already holds it (a build
tool's own surface goes under `cli`, a platform's under `platform`, a package
under its registry); and the first page meets the withdraw-ready bar. The key
is the ecosystem's own short name, and the list above gains it in the same
change. `http-api/`, a vendor's HTTP API with neither a package nor a CLI, is
deferred under this rule: it is admitted when one such API has a full ingest
and a second plant consumes it.

## Rules

- **Agnostic or it does not belong here.** No project name, domain noun, path,
  credential, or dataset shape.
- **Durable or it does not belong here.** A fact states the versions it holds
  for, or holds for all of them; a fact that silently assumes one release
  fails, and so does a project's own pin. A fact that reads like a security
  bulletin for one release fails: a page reads like the library's own
  documentation, its "changed in" notes included.
- **Orientation, not gospel.** A surface page ages slowly, but an API redesign
  across a major line can outdate it. Confirm against upstream; never read a
  project's pin from here (there are none to read). A version fact read here is
  checked against the project's own pin before it is relied on.
- **Platform DSLs and APIs may earn a page without a package.** A platform's
  declarative pipeline or config DSL (a CI platform's YAML schema, a deploy
  platform's manifest format) or its REST API has no installable package and no
  version number of its own (a REST API's `api-version` parameter is the
  caller's pin, recorded in the project's page, not here), yet its surface (the
  schema or wire shape, its idioms, its pitfalls) is just as reusable. Such a
  surface may get a library-wiki page under `platform`, pinned by
  **retrieval date** (when the surface was last confirmed against upstream)
  instead of a version number, since there is no version to pin.
