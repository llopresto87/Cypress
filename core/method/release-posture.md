---
id: method.release-posture
tier: 2
kind: method
origin: seed
title: release posture — promoting the attested artifact, rehearsed reversal, one governing lockfile, irreversible steps land last
owns:
  - release-posture.artifact-identity
  - release-posture.readiness
  - release-posture.dependency-graph
  - release-posture.advisories
  - release-posture.ordering
  - release-posture.rollout
requires:
peers:
  - method.secrets-posture
  - method.incident-posture
  - method.contract-posture
  - protocol.verify
  - protocol.ingest-library
load_when:
  - "rebuild at release or promote the verified artifact, immutable digest not a floating tag"
  - "is this release ready, rehearsed rollback and a verified restore point"
  - "lockfile checked in, pin transitive dependencies, base image, and the toolchain"
  - "suppress a vulnerability advisory, upgrade now or hold the version"
  - "which increment lands first, the irreversible step and the landing order"
  - "ship the release order across services, canary the lowest-risk one then fan out"
est_tokens: 1900
---

# Release posture

What ships, when it may ship, what it is built from, and in what order it
lands and rolls out. Gates are `protocol.verify`'s; adopting a dependency
is `protocol.ingest-library`'s; this node owns the release-side rules.

## 1. Ship the exact verified artifact, pinned immutably

The thing released is the byte-identical artifact that passed
verification, promoted by immutable digest — an exact tag *and* the
digest, never a floating tag — with only configuration changing between
environments; the previous configuration stays on disk and provably
recreatable so reversal needs no rebuild. Rebuilding at release
invalidates every gate that ran before it. The artifact carries no
environment identity (a client bundle addresses its serving edge by
relative path, no host baked in). A commit id proves authorship, not
deployment — a claim that a fix or control ships carries an ancestry
check against the shipping reference. Every externally supplied
identifier written into a deployment file (an image tag, a version) is
verified to resolve before it is committed. Enforce the pin with a
tag-policy lint that fails the build.

**The argued exception.** One line of practice builds on the target host
at deploy time — no registry, ship source, build there — because a
silently stale local image cache is worse than the build cost and "what
was tested" is then "what runs". The rule stands; the exception is
legitimate only when `plant.environment_class` is `ephemeral-test` or
`staging`, or when no artifact registry exists and the plant records the
departure as a `deviation` node whose `ends_when` is the registry and
whose rollback runbook names the missing artifact identity as the
residual it is. Under `real-production` with a registry available,
build-on-host is a defect, not a preference.

## 2. Releasable means green on the exact artifact, a rehearsed reversal, a verified restore point

"Deployed" and "production-ready" are different claims. A release is not
releasable without green verification on the exact artifact, a rehearsed
reversal path, and a restore point captured *before* the change and
verified after capture (it exists, carries its completion marker, its
reference rows are intact). An assumed backup is not a rollback point; an
untested rollback is not a rollback; a teardown script is not a reversal;
never write a recovery procedure you have not run — an invented rollback
is believed exactly when it matters most. Before each release record the
previous build identifiers and the migration and message-schema
compatibility; refuse a generic rollback across an irreversible
migration; where deployments auto-apply migrations, record that reverting
the artifact does not revert the schema; removing a migration's reverse
path is a recorded decision in the rollback runbook. A release checklist
covers both sides of every contract change, migration and rollback
compatibility, the absence of secrets or real data in fixtures
(`method.stewardship-posture`), and what the release deliberately does
not include. A missing or unrehearsed path is recorded `absent` with a
date (`protocol.verify` gate states), never implied. Under
`ephemeral-test` a deferred rehearsal is tolerable; under
`real-production` it is `hotfix`-class debt with an owner.

## 3. Pin the whole resolved graph through one governing source

One dependency-management source governs direct and transitive versions,
toolchains, and base images at explicitly pinned versions, with lock
files committed and inherited package feeds cleared so a machine-level
source cannot inject a dependency. Pin the toolchain at invocation —
default resolution varies by machine and by moment and surfaces as a
misleading unrelated error — and keep it inside the build container so a
target is reproducible from a bare OS plus the container runtime. A
toolchain pin does not reach the container base image: pin that
separately, and check that compile target and runtime base agree. A range
is a compatibility policy, never proof of the installed version; bounded
ranges without a committed lock are a recorded reproducibility gap. Every
hand-pin outside the governing source is an exception justified and
recorded on the dependency's library page (`protocol.ingest-library`),
never applied silently in a build file — and a pin is verified to reach
the resolved graph, because an override at the wrong layer is silently
ineffective and a pin whose transitive reach is off is where version
splits come from. Where a version is the mitigation for a vulnerability
class, record the floor as forbidden-to-downgrade and enforce it with an
automated check; shared build templates are consumed at pinned release
tags, rolling-branch consumption being an opted-in, recorded risk.

## 4. Never suppress an advisory; decide upgrades on measured reachability

Vulnerability advisories are promoted to build errors, never suppressed;
suppressions are replaced by explicit remediation pins, and a scan bypass
is a logged risk acceptance on the register (`method.incident-posture`),
not a passing gate. Each upgrade or deliberate non-upgrade is decided on
whether the advisory is actually reachable in this codebase and whether
the newer version is genuinely better — measured, since a newer release
can carry more findings or fail to boot — and every non-upgrade is
recorded with the measurement that justified it. An archived or
commercially relicensed upstream is a production blocker regardless of
current exposure: record the escape hatch before you need it, and the
licence option a multi-licensed dependency is used under. Dependencies
whose upgrade could silently change computed results are held constant
behind a golden-value characterization test (`protocol.test-first`). Do
not stack two risky upgrades on one change: the proven line on the
production path, the newer as a separately reversible fast-follow
(`method.engineering-posture`: boring on the production path); forced off
an end-of-life generation, target the supported line with the longest
runway, and budget the upgrade by the hand-written rewrites it may spend.
Four supply-chain gates run in CI — advisories failing on high severity,
committed-secret scanning, static analysis for injection patterns, image
scanning under the pinned-tag policy — each with the positive control
`protocol.verify` requires of a zero.

## 5. Land the reversible parts first; gate the one-way step on their evidence

Where two or more steps interact, their order is load-bearing and stated
as a binding constraint, justified by what the wrong order would hide.
Reversible, low-blast-radius increments land first and prove the rule;
the irreversible step is named as such and lands only with all reversible
evidence already green. Never let a sequencing choice convert a loud
failure into a silent one: nothing that removes a failure's reproduction
lands before its evidence is captured (a cache that would drive the
failure count to zero without fixing the defect waits for the trace); a
validation, threshold, or metric is gated behind the fix that makes a
corrupt input real, never layered on top of it; when a file governed by
an exclusion rule moves, the rule changes first and the file second.

## 6. Roll out one lowest-risk target at a time, in a recorded order

Deploy and migrate one component or consumer at a time in an explicit,
recorded dependency order: the lowest-value target first to shake out the
mechanism, the highest blast radius last, health criteria at each step
(running, healthy, restart count zero), the rollback point captured
beforehand, a per-target reversal path. Fleet-wide risky operations run
serialized; propagating a change beyond the primary write is a separate
decision with its own explicit flag. Preserve the ability to build,
deploy, and migrate one component at a time — a restructure that makes
the unit of change all-or-nothing is the largest one-way door a program
can open. Where a component resolves its dependency once at startup,
deployment order is load-bearing: write the rule down the first time it
bites, then fix it in configuration so order stops mattering. A change
to the single component all traffic passes through
needs explicit human authorization, a written step order, and the gate
that would catch a regression at each step. **Lockstep versus
incremental** is decided by whether the running system can hold a mixed
state and whether there are live users to protect, not by a preference
for small steps: under `ephemeral-test` with no live users a lockstep
cut is legitimate; under `real-production` incremental is the default,
and a mixed-version fleet is a deliberate, recorded state with a test
proving the versions interoperate across the wire.

## Neighbours

- `method.incident-posture` — fix-forward or reversal once live; the register.
- `method.secrets-posture` — the credential that must not ride the artifact.
- `method.contract-posture` — wire contracts compatible on both sides on release.
- `protocol.verify` — gate states, null-result controls; cross for what "green" means.
- `protocol.ingest-library` — one dependency and its library page; cross per library.
