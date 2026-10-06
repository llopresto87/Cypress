# Tool: hashed-lock-closure-check

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the
> closure-measurement method is portable across any package manager with a
> hash-pinned, dry-run-capable resolver; the exact flags belong on that package
> manager's own library page (§7), not here. The doctrine this tool exists to
> satisfy, that a lock is resolved in an empty environment for the target
> platform or it is not closed, is owned by `core/method/release-posture.md` §3
> and is linked, not restated.

## 0. Identity

- **Category:** ops
- **Name:** hashed-lock-closure-check
- **Language / runtime:** any (a resolver-in-dry-run-mode invocation and a
  set comparison are the whole requirement)
- **Stability:** **blueprint**: the measurement method is stack-neutral, but
  the resolver invocation is written against one package manager's own
  dry-run/report flags, which belong on that manager's library page.

## 1. What it does

Measures whether a **hash-pinned lock file** (a `--require-hashes`-style
requirement set, or the equivalent in another ecosystem) is genuinely
**closed**, meaning every transitive dependency the target platform will
actually need has a pin, before that gap is discovered the expensive way, as a
hashed-install failure in the middle of an image build. It exists because a
lock file is usually generated once, by hand or by a partial script run, and
nothing re-checks it as the dependency graph shifts underneath: a new
transitive dependency, a marker-gated package that only applies on some
platforms, or a package silently satisfied by whatever happens to already be
installed in the environment that generated the lock.

## 2. Interface & invocation

```sh
lock-closure-check \
  --lock <hash-pinned requirement file> \
  --top-level <the direct dependencies alone> \
  --target-platform <platform/interpreter/ABI triple> \
  [--fail-on-drift]
```

- **Inputs:** the full hash-pinned lock file; the same direct dependencies
  with no lock (the top-level requirement set alone); the target platform,
  interpreter, and ABI the resolution must be measured for, never the
  measuring host's own defaults.
- **Outputs:** the resolved package set from the lock, the resolved package
  set from the top-level alone, and their diff; any environment marker found
  in either resolution and whether it evaluates true or false for the target
  platform; a closed/open verdict, decided by package name; and, listed
  separately, each package both sides reach at different versions, reported
  as "a pin would change".
- **Exit codes:** 0 both resolutions reach the same package names and the
  lock is closed (version differences, if any, are listed but do not open
  it); 1 the two resolutions disagree by name (either a lock pin the
  top-level set no longer needs, or a top-level dependency the lock is
  missing a pin for), or, under `--fail-on-drift`, a pin would change; 2
  usage error or
  the resolver itself could not run (never conflated with 1: a tool failure
  is not a closure finding).
- **Preconditions:** a disposable, empty environment for the target
  platform, never the environment used to generate the lock, and never the
  invoking host's own environment (see §3, and §5's central pitfall).

## 3. Approach / algorithm

### An empty environment, not the measuring host's own

Run the resolver's own dry-run/report mode from a clean environment,
explicitly told the **target** platform, interpreter, and ABI, not
whatever the measuring host happens to be. A resolver's dry-run report
omits any requirement the measuring environment **already satisfies**, by
design: it reports what it would need to *change*, not the full closure. A
report taken from a non-empty environment therefore silently drops every
package that environment happened to already have installed, and a lock
built from that report is missing exactly those pins, invisible until the
hashed install runs somewhere that does not have them pre-installed, which
is precisely what an image build's disposable layer looks like.

### Run it twice, and compare

1. Resolve the **stripped lock** (the lock with its hashes removed and its
   `==` version pins kept) for the target platform. Stripping the hashes
   lets the resolver run in dry-run mode without the hash check; the kept
   pins mean it still resolves the locked versions, so this pass shows what
   the lock itself closes over.
2. Resolve the **top-level requirements alone** (no lock at all) for the
   same target platform.
3. **Compare the two resulting package sets by name.** The names must
   agree exactly; that is the closure verdict. A
   package in the lock that the top-level resolution no longer reaches is a
   **surplus pin** (safe to remove, but a sign the direct dependencies
   changed without the lock being regenerated). A package the top-level
   resolution reaches that the lock does not pin is the dangerous case: a
   **missing pin**, invisible until `--require-hashes`-style install fails
   at build time. A package both passes reach at **different versions** is
   neither: the lock is still closed over it, but the top-level pass shows
   that regenerating the lock would move its pin. Report it separately as "a
   pin would change", never as a closure gap.

### Check markers explicitly

Read every environment marker (a `; platform_system == "..."` -style
qualifier, or the equivalent) that either resolution reports, and evaluate
it against the **target** platform, not the measuring host's. A marker that
is false everywhere the project actually deploys is fine to carry; a marker
that is only checked against the measuring host's own platform can hide a
gap that appears only on the real target.

### Run it whenever a pin changes, and leave the failure somewhere it can be read

This check earns its keep only if it runs at the moment a pin changes, not
on a fixed schedule that can lag behind an edit by days. And because the
consequence of an open closure is a **build-time** failure, not a
closure-check failure (the hashed install itself is what actually breaks,
downstream, inside an image build), and that failure must leave its own log
somewhere a later reader can reach; this tool does not own that rule
(`core/method/contract-posture.md` §5 does, and it is linked, not restated
here).

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** measuring from an empty, target-platform
  environment rather than the measuring host's own; the twice-run comparison
  (stripped lock, pins kept, vs. top-level alone); the closure verdict by
  package name, with version differences reported separately as "a pin
  would change"; treating a name mismatch in either direction (surplus pin,
  missing pin) as a finding; checking every marker
  against the target platform explicitly; running the check on every pin
  change rather than on a schedule.
- **Blueprint (write per package manager):** the resolver's own dry-run/
  report invocation and its exact flags for "do not consult what is already
  installed," "resolve for this target platform/interpreter/ABI, not the
  host's," and "prefer binary artifacts only": these are named on the
  package manager's own library page (§7), never duplicated here.
- **Adopting note:** confirm the resolver's dry-run mode genuinely does not
  consult the local environment at all: a mode that merely *reports*
  without installing can still silently consult what is present, which is
  the exact defect this tool exists to catch (see §5).

## 5. Pitfalls and sharp edges

- **A resolver's dry-run report taken from a non-empty environment silently
  omits already-satisfied requirements. This is the central failure mode,
  not an edge case.** A single package pre-installed on the measuring host
  is enough to drop its own pin (and any pin that only exists to satisfy
  it) from the reported closure, with no error, no warning, and a fully
  green resolution. The fix is not "remember to use a clean venv this time";
  it is asserting the flag that forces the resolver to ignore what is
  installed, every single run, as part of the invocation this tool wraps.
- **Comparing counts, not package identities, misses a same-count
  substitution.** Two resolutions with the same number of packages can still
  disagree about *which* packages they are; the closure comparison must be
  a set diff by name, never a count. Versions are compared too, but only to
  report which pins would change; folding them into the closure verdict
  would call a closed lock open because upstream shipped a newer release.
- **A missing pin is invisible until the hashed install runs, and it runs
  inside a build, not inside this check.** This check's whole value is
  moving that discovery earlier, from a failed image build, hours or days
  later, back to the moment the pin changed.
- **A platform marker checked against the wrong platform hides exactly the
  gap the marker exists to describe.** Always evaluate against the declared
  target, never against the measuring host, even when they happen to match
  today.
- **This check proves the lock is closed; it does not build the image and
  does not prove the packages install cleanly inside the real build
  environment.** Say so when citing it: it is a resolution-time guarantee,
  not a build-time one.

## 6. Tests that cover it

Cover, against a fake/stub resolver (no real package index, no network): an
environment with a package pre-installed produces a smaller reported closure
than the same resolution with the "ignore installed" flag asserted, and the
tool fails closed if that flag is not present in the invocation it builds;
a stripped-lock resolution and a top-level-alone resolution that agree
report a closed verdict; a top-level resolution that reaches one package the
lock does not pin reports a missing-pin finding naming that package; a lock
pin the top-level resolution no longer reaches reports a surplus-pin
finding, distinctly from a missing pin; a package both resolutions reach at
different versions is reported as "a pin would change" with a closed
verdict and exit 0, and exits 1 only under `--fail-on-drift`; a marker evaluated against the
target platform differs correctly from the same marker evaluated against a
different platform; a resolver invocation failure (bad flags, unreachable
index) exits with the tool-failure code, never the drift code.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Posture home (link, not restate):** `core/method/release-posture.md` §3:
  "a lock is resolved in an empty environment for the target platform... a
  resolver report taken where packages are already installed silently omits
  them, so a hashed lock computed that way is not closed. Resolve and check
  lock closure from a clean environment with the target platform's markers
  whenever a pin changes." That paragraph also states plainly: "the package
  manager's flags for it belong on its library page," which is why this
  tool page names no specific resolver flag.
- **Posture home (link, not restate):** `core/method/contract-posture.md` §5:
  a step that does work, including a build a hashed-install failure would
  break, writes its output to a durable place a later reader can reach.
- **Related tools:** `tool-corpus/ops/registry-digest-resolver.md` (the same
  discipline: verify a closure or an identity independently, against its
  own address, rather than trusting a cached or partial view, applied to a
  container registry tag instead of a language package manager's lock).
- **Package-manager-specific flags:** land on that package manager's own
  `library-corpus/<ecosystem>/<name>.md` page (for example, a Python
  toolchain's own dry-run/report/target-platform flags), never here.
- **Sources:** distilled from practice; no external URL.
  The general method (dry-run resolution, ignore-installed, twice-run
  comparison) is a documented capability of common package-manager
  resolvers, and the exact flag names are cited on the package manager's own
  library page rather than here.

## 8. Changelog

- 2026-09-26 — created by
  docs-librarian.
- 2026-09-26 — corrected after review: the stripped lock keeps its `==` pins; the closure verdict is by package name, and version differences are reported separately as "a pin would change".
