# Suggested skill: vendor-dependency-from-dead-registry

> Optional procedure: a project's dependencies were resolved through a private
> package registry or repository manager that no longer answers, and the build
> must work again without it. It proves which packages were in-house,
> rebuilds each of those from source at the exact version the consumer was
> built against, points the consumer at the local artifact, and then closes the
> two gaps the regenerated resolution opens: leftover references to the dead
> host, and transitive dependencies that float to a new major. The steps are
> ecosystem-neutral; the npm and Maven arms give each step's commands.
> **Composes** `protocols/verify.md` (each step's gate, and a gate not run is
> recorded as not run), `core/method/secrets-posture.md` (the dead registry's
> credential), `skill-corpus/maven/offline-legacy-build-harness.md` (the Maven
> settings mirror and local install, when the goal is running tests on a
> workstation) and `skill-corpus/deploy-fleet-on-remote-docker-host.md` (when
> the build runs on a remote host) by reference.

**Instantiate by supplying:** `<DEAD_HOST>` (the registry's host, as it
appears in lockfiles, `.npmrc` or `settings.xml`), `<CONSUMER>` (the project
whose build fails), `<OLD_LOCK>` (the consumer's committed lockfile, or for
Maven the declared versions, before anything is regenerated), `<SOURCES>` (the
source repository of each in-house package) and `<VENDOR_DIR>` (where the
rebuilt artifacts live inside the consumer's build context, `vendor/` by
convention).

## When to apply

- An install or build fails on transfers to a registry host that refuses
  connections or no longer resolves, and that host was a private registry.
- A container build that used to pass fails at the dependency-install layer
  after the organization retired its registry.
- Not for a public registry outage: wait it out; nothing here applies.

**Hard boundary: the lockfile from before is evidence; keep it.** Copy
`<OLD_LOCK>` aside before any step touches it. It is the only record of the
exact version of each in-house package the consumer was built against, and of
the versions every transitive dependency had; steps 2 and 5 read it.

## 1. Prove which packages are in-house

*Replaces: vendoring everything the dead host served, or assuming everything
it served is lost.*

A private registry often proxied the public one too, so the lockfile can
record the dead host for ordinary public packages as well. Observed in
practice: public packages in a lockfile carried the dead host's URL too, and
one package was in-house. List each package recorded against `<DEAD_HOST>`,
then ask the public registry for that name and version:

- **npm:** `npm view <name>@<version> version --registry=https://registry.npmjs.org/`
  prints the version when the public registry has it.
- **Maven:** resolve `<groupId>:<artifactId>:<version>` against the central
  repository, for example
  `mvn -s <central-only settings> dependency:get -Dartifact=<g>:<a>:<v>`.

A package the public registry has is not vendored; it re-resolves in step 4.
**Gate:** a written list of the in-house packages, each with the exact version
from `<OLD_LOCK>`, and its source repository in `<SOURCES>`. A package with no
source anywhere is a blocker to report, not one to replace by a look-alike.

## 2. Find the commit that built the pinned version

*Replaces: building the source repository's current tip.*

The consumer was built against one version, and the tip has usually moved
past it, possibly with API changes. Read the exact version from `<OLD_LOCK>`
(not the range in the manifest: a caret or tilde range can admit later
versions the consumer never ran). Check out the commit where the package's
own manifest declares that version: a release tag when the project tagged
releases; otherwise search the history of the manifest file, for example
`git log --format='%h %s' -- <path>/package.json` and read the version at each
commit, or `git log -S'"version": "<v>"' -- <path>/package.json`.
**Gate:** at the checked-out commit, the manifest's version equals the pinned
version exactly.

## 3. Build it with its own toolchain, and pack it

- Build with the package's own build command, on a toolchain that commit can
  build with. An old package can need an old one: an annotation processor or a
  bundler that predates the current runtime fails on it. Pin the runtime the
  package was built on; never edit the package to fit a newer one.
- **npm:** run the package's build script, then `npm pack` in the directory
  that holds the publishable `package.json`. For a library inside a workspace,
  that is the build output directory the build writes, not the workspace
  root. `npm pack` writes `<name>-<version>.tgz` (a scoped name becomes
  `<scope>-<name>-<version>.tgz`); move it into `<VENDOR_DIR>`.
- **Maven:** `mvn -s <SETTINGS> -DskipTests install` at the commit, in
  dependency order when several in-house artifacts depend on each other (the
  one with no in-house dependencies first). `<SETTINGS>` is the settings file
  with the `external:*` mirror from step 4: an in-house POM usually declares
  the dead repository too, so it needs the mirror before it builds. The
  artifact lands in the local repository under the coordinates the consumer
  already declares, and the local repository is read before any remote one.
- **The in-house package's own lockfile** can name `<DEAD_HOST>` as well, so
  its install at the old commit fails the same way. Apply step 4's npm arm to
  it first: drop its registry lines and re-resolve its public dependencies.
  When it depends on a further in-house package, that package goes through
  steps 1 to 3 too. When none of this makes it install, report it as a
  blocker.
- **Gate:** the tarball exists and `tar -tzf <tarball>` lists `package/package.json`
  with the pinned version, or the jar and its POM are in the local repository
  at the pinned version.

## 4. Point the consumer at the local artifact and re-resolve

- **npm:** change the dependency to `"<name>": "file:vendor/<name>-<version>.tgz"`
  in `package.json`, delete the registry lines for `<DEAD_HOST>` from every
  `.npmrc` the build reads (project, user, and any copied into an image),
  then regenerate the lockfile against the public registry with
  `npm install`. Commit the tarball with the consumer.
- **Maven:** neutralize the dead repository from a settings file with an
  `external:*` mirror to the central repository, never by editing the POMs
  (`skill-corpus/maven/offline-legacy-build-harness.md`, move 2), and keep
  the in-house artifacts in the local repository (step 3).
- **In a container build**, the vendored artifacts must be inside the build
  context and copied into the image **before** the install layer: an `npm ci`
  layer that runs before `COPY vendor ./vendor` cannot see the tarball. For
  Maven with a BuildKit cache mount on the local repository, the mount hides
  whatever an earlier layer copied to the same path: stage the artifacts
  outside the repository path (for example `/vendor-m2/`) and copy them into
  the mounted repository in the `RUN` that packages (why that copy and the
  packaging share one `RUN`: `skill-corpus/deploy-fleet-on-remote-docker-host.md`,
  Step 1). Or build the in-house artifacts in an earlier stage on their own
  toolchain and copy them across. When that stage installs into a
  cache-mounted repository too, the built artifacts exist only in the mount:
  copy them out of it, to a path outside the mount, in the same `RUN` that
  built them. Otherwise `COPY --from=<stage>` finds nothing to copy.
- **The dead registry's credential** (an auth token in `.npmrc`, a server
  entry in `settings.xml`) leaves the build with the registry lines; whether
  it must be revoked is `core/method/secrets-posture.md`'s question.
- **Gate:** `grep -c '<DEAD_HOST>'` over the regenerated lockfile, every
  `.npmrc` or settings file the build reads, and the build log returns 0. Grep
  the whole lockfile, not only the in-house entries: a public package still
  recorded against the dead host fails the next clean install exactly as
  before.

## 5. Audit the re-resolution for floating majors, and pin them

*Replaces: trusting the regenerated lockfile because the install succeeded.*

Regenerating resolves every loose range afresh. A transitive dependency that
nothing pinned (a type-definition package is the usual one, often reached only
through a `*` range) can jump to a major the project's toolchain cannot use,
and the failure then reads as a compiler error far from the cause. Observed in
practice: a regenerated lockfile pulled a type-definition package several
majors ahead of the one the project was built with, and compilation failed
until it was pinned back. Compare the two lockfiles and pin each package whose
major rose to the version `<OLD_LOCK>` recorded:

- **npm:** pin it in the `overrides` field of `package.json`, at the exact
  version from `<OLD_LOCK>`, then regenerate once more.
- **Maven:** there is no lockfile; versions come from the POMs and the BOMs
  they import, so an unpinned range is rare. Compare `mvn dependency:tree`
  before and after, and pin a moved version in `dependencyManagement`.
- **Gate:** the comparison lists no raised major that is not an intended
  change, and the build and the tests pass on the regenerated resolution.

The comparison for npm lockfiles, stdlib only (lockfile formats 1 to 3; exit 0
no major rose, 1 a major rose, 2 bad input; `--self-test` runs its fixture):

```python
#!/usr/bin/env python3
"""lock-major-drift: list packages whose major rose between two npm lockfiles.

usage: lock-major-drift.py <old package-lock.json> <new package-lock.json>
       lock-major-drift.py --self-test
Reads lockfile v2/v3 ("packages") or v1 ("dependencies"). Exit 0 when no
major rose, 1 when one did (each printed as name old -> new), 2 on bad input:
a file that is not a JSON object, or that yields no package versions.
"""
import json, sys


class BadLock(ValueError):
    pass


def versions(lock):
    if not isinstance(lock, dict):
        raise BadLock("not a lockfile: the top level is not a JSON object")
    out = {}
    for path, meta in (lock.get("packages") or {}).items():
        if path and isinstance(meta, dict) and "version" in meta:
            out.setdefault(path.rsplit("node_modules/", 1)[-1], set()).add(meta["version"])
    def walk(deps):
        for name, meta in (deps or {}).items():
            if not isinstance(meta, dict):
                continue
            if "version" in meta:
                out.setdefault(name, set()).add(meta["version"])
            walk(meta.get("dependencies"))
    if not out:
        walk(lock.get("dependencies"))
    if not out:
        raise BadLock("not a lockfile, or an empty one: no package versions found")
    return out


def major(v):
    head = v.split(".", 1)[0].lstrip("v^~=")
    return int(head) if head.isdigit() else None


def drift(old, new):
    rows = []
    o, n = versions(old), versions(new)
    for name in sorted(set(o) & set(n)):
        om = max((m for m in map(major, o[name]) if m is not None), default=None)
        nm = max((m for m in map(major, n[name]) if m is not None), default=None)
        if om is not None and nm is not None and nm > om:
            rows.append((name, ",".join(sorted(o[name])), ",".join(sorted(n[name]))))
    return rows


def self_test():
    old = {"lockfileVersion": 3, "packages": {"": {}, "node_modules/@types/node": {"version": "18.15.3"},
           "node_modules/left": {"version": "1.2.0"}, "node_modules/a/node_modules/left": {"version": "1.0.0"}}}
    new = {"lockfileVersion": 3, "packages": {"": {}, "node_modules/@types/node": {"version": "24.0.1"},
           "node_modules/left": {"version": "1.9.0"}, "node_modules/vendored": {"version": "0.0.14"}}}
    v1 = {"lockfileVersion": 1, "dependencies": {"left": {"version": "2.0.0"}}}
    assert drift(old, new) == [("@types/node", "18.15.3", "24.0.1")], drift(old, new)
    assert drift(old, old) == []
    assert drift(old, v1) == [("left", "1.0.0,1.2.0", "2.0.0")], drift(old, v1)
    manifest = {"name": "app", "version": "1.0.0", "dependencies": {"left": "^1.2.0"}}
    for bad in ({}, [], {"lockfileVersion": 3, "packages": {"": {}}}, manifest):
        try:
            drift(old, bad)
        except BadLock:
            continue
        raise AssertionError(f"accepted a non-lockfile: {bad!r}")
    print("self-test: ok")
    return 0


def main(argv):
    if argv[1:] == ["--self-test"]:
        return self_test()
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        old, new = (json.load(open(p, encoding="utf-8")) for p in argv[1:])
        rows = drift(old, new)
    except (OSError, ValueError, AttributeError, TypeError) as exc:
        print(f"lock-major-drift: bad input: {exc}", file=sys.stderr)
        return 2
    for name, a, b in rows:
        print(f"{name} {a} -> {b}")
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

Run as `python3 lock-major-drift.py <OLD_LOCK> package-lock.json`. It compares
the highest major each package had in either file, so a package that was
duplicated at two majors is reported only when the highest one rose. It
compares only the first version component: a `0.x` package whose minor rose
(`0.14` to `0.15`) is a breaking change under a caret range and is not
reported, so read those entries in the lockfile diff by hand. A file that is
not a lockfile, `package.json` passed by mistake included, exits 2: a run that
read no versions does not report clean.

## Failure table

| symptom | cause | step |
|---|---|---|
| install fails with connection refused or a timeout on `<DEAD_HOST>` | an entry or a registry line still points at the dead host | 4, grep the whole lockfile and every `.npmrc` |
| npm stops with "Exit handler never called!" | observed in practice as a side effect of repeated failed fetches to an unreachable registry, not a separate defect | 4 |
| `npm ci` in an image cannot find `file:vendor/…` | the vendor directory is copied after the install layer, or is outside the build context | 4 |
| the vendored package installs but its API does not match the consumer's calls | it was built from the tip, not from the pinned version's commit | 2 |
| compile errors in type definitions after regenerating | a transitive dependency floated to a new major | 5 |
| a Maven build in an image cannot find an in-house artifact that an earlier layer copied into the local repository | a cache mount on the repository path hides it | 4 |
| `npm ci` fails because `package.json` and the lockfile disagree | the lockfile was not regenerated after the `file:` change, or after an override was added | 4, 5 |

## Reference files

- `skill-corpus/maven/offline-legacy-build-harness.md` (the settings mirror
  and the local install, for running a legacy service's tests)
- `skill-corpus/deploy-fleet-on-remote-docker-host.md` (building on a remote
  host)
- `library-corpus/cli/maven.md` (mirrors, offline builds, BOM management)
- `library-corpus/language/nodejs.md` (npm)
- `core/method/secrets-posture.md` (the retired credential)
- `protocols/verify.md` (gates, and a gate not run)
