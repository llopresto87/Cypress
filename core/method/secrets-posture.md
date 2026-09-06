---
id: method.secrets-posture
tier: 2
kind: method
origin: seed
title: secrets posture — one channel in and none out, names not values, compromise means rotation, lifetime bounds damage
owns:
  - secrets-posture.channel
  - secrets-posture.recording
  - secrets-posture.compromise
  - secrets-posture.lifetime
requires:
peers:
  - method.release-posture
  - method.incident-posture
  - method.contract-posture
  - protocol.verify
  - protocol.recover
load_when:
  - "where do credentials live, dotenv values or a secret store, how a password reaches a subprocess"
  - "can I print, log, mask, or document a secret value"
  - "a credential leaked into source history, rotate it or scrub the history"
  - "token TTL versus revocation list, credential lifetime and rotation"
  - "generate a fresh password or key during deploy without overwriting the live one"
est_tokens: 1550
---

# Secrets posture

How live credentials are stored, moved, written about, remediated, and
aged. Four facts, each the single home of its rule; the kernel §4
boundaries ("do not paste secrets", "do not rotate without a named
confirmation") are the floor this node builds on, not a second copy.

## 1. Secrets enter through one validated channel and leave through none

Credentials live in a secret store or in one encrypted,
version-control-excluded file loaded by explicit reference — never
auto-loaded, never scattered as inline blobs across many files. At start
they are materialized onto ephemeral storage from that source, never
bind-mounted from a shared host; they reach a child process on stdin or
through a scoped environment, never on the command line; each step's
environment is limited to the variables that step needs, so a crash trace
cannot dump the whole set; and an authenticated call is made in-process
rather than by shelling out with the secret in argv. They leave through
nothing — not logs, not error bodies, not client payloads, not serialized
records, not committed artifacts. Automation that handles secrets
structurally refuses debug modes that would print them (a shell trace
flag, a verbose variable dump) and offers targeted output instead. The
repository holds the example/template environment file; a populated one
is never committed and never printed. Exclusion from version control is
not encryption and not authorization: an unencrypted ignored file is one
forced add from being history. Where two independent gates can enforce
the secret-at-rest invariant (staging and publication), both fail closed,
so one bypassed gate cannot publish plaintext. A capture, interception,
or debug service holding real credential material (a mail sink with
reset tokens) is a sensitive store even in staging: internal-only, absent
from production. Whole-system configuration dumps are secret-bearing by
default — restricted paths, suppressed from task logs — rather than
judged field by field. `plant.environment_class` (`docs/graph/index.md`)
decides what "disposable" means here: a generated throwaway credential is
correct under `ephemeral-test` and a defect under `real-production`; the
rule is the same, the class supplies the verdict.

## 2. Record a secret by name and location only

Any artifact — log, gate output, diagnostic, ADR, graph node, handback —
records a credential's key name and where it lives, never its value, not
even partially masked: a mask still leaks shape, length, and prefix into
a permanent searchable record. The key names and locations are the
useful artifact — the credential *interface* a rebuild must supply; the
values add only exposure. Investigating an exposure establishes existence
by metadata alone (a tree listing, a filename, a scanner hit) and never
opens the blob — reading it materializes live bytes into a transcript.
When coverage evidence is needed from secret-bearing data, emit shape and
counts, keep the raw material inside a log-suppressed boundary, and state
that the summary is not a backup. The rule is enforced against your own
documents: a value found written out is redacted in place with a note
saying so, and a pointer to the source replaces it; a credential in
unreachable code is documented as exposed anyway. A change touching a
secret-bearing area declares itself secret-neutral by contract —
pre-existing exposure stays out of scope but is not worsened, and no fix
adds a secret even while solving a secret problem.

## 3. A credential that reached version control is compromised

Any credential that entered a repository, a build artifact, or
infrastructure you no longer control is actively compromised; key
material whose status is unclear (placeholder or live?) is treated as
live and its rotation costed. Removing it from the working tree, the
file, or the history is hygiene — a history rewrite is an owner decision,
never the remedy. The remedy, in order: neutralize with an environment
override that outranks file configuration (editing the committed file
changes nothing about the history); externalize the secret out of the
artifact so rotation becomes a configuration swap rather than a rebuild
of every consumer; then rotate in descending blast-radius order —
signing keys, then datastore credentials, then third-party integration
keys — under the explicit confirmation kernel §4 requires, with a
secret-scan re-run (with its positive control, `protocol.verify`) as each
rotation's exit gate. Two operations share only the word: a credential a
third party still honours is a live exposure revocable today; one
guarding only systems you control is a never-reuse constraint on future
generation. Code carrying a credential is deleted from source, not
disabled or profile-gated. A plant that knowingly carries a committed
credential for a bounded time records that as a `deviation` node whose
`ends_when` is the rotation, never as an accepted state.

## 4. Bound exposure by lifetime, freshness, and non-reuse

Prefer short credential lifetimes to revocation lists: a denylist covers
only the compromises someone reports; a short TTL bounds every
compromise, including the silent ones. Where a denylist exists anyway,
key it on the credential's stable identifier claims, not on a hash of the
malleable serialized form. Generate secrets fresh at the point of use,
before anything is provisioned or listens on a network — standing a
system up on old values rebuilds the exposure into the new environment —
and never echo the generated value into a log or transcript; an
environment's own secret files are read-only during an automated change.
Generation is idempotent and never overwrites an existing value, so
re-running convergence cannot rotate a live credential by accident; a
first-touch convergence rotates at most once, re-authenticates, and
verifies before the next target. Never reuse one generated value across
tenants — one recovered value would unlock many. Absent a secret
manager, reusing an existing trust root beats minting another secret
(each new one adds rotation surface without adding security), but record
where a single-issuer trust root concentrates total compromise, at the
place the key lives, not only where it is validated. A one-time code's
strength is the product of its entropy, validity window, and attempt
limit; a small code space is acceptable only with a short window and
enforced throttling. Account-security operations require fresh
re-authentication, invalidate other sessions, and rate-limit the re-auth
path itself. Under `ephemeral-test` a long-lived static credential is a
convenience; under `real-production` it is a finding.

## Neighbours

- `method.contract-posture` — what a service does when a required secret
  is missing, and what logs may carry — cross when the question is
  startup validation or log content rather than the secret itself.
- `method.incident-posture` — containment and register rows once an
  exposure is an incident — cross when sequencing a remediation backlog.
- `method.release-posture` — supply-chain gates and the artifact a secret
  must not be baked into — cross when the secret rides a build.
- `protocol.verify` — the secret scan is a gate with a null-result
  control — cross when reporting "no secrets found".
- `protocol.recover` — a failed rotation is a failure to classify before
  retrying — cross when the rotation itself goes wrong.
