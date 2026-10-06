# Suggested skill: fleet-security-review

> Optional procedure: review the security of a whole multi-service system
> (many repositories, services and images, one identity layer) from first
> fan-out to a ranked remediation plan. Audits fan out by real boundary into
> one findings ledger, a real scanner is ground truth over remembered
> advisories, and no exploit-chain narrative ships before an adversarial pass
> has traced it against the deployed code. Composes
> `agents/05-security.md` (the boundary audits and the ledger),
> `agents/11-pentest.md` and `skill-corpus/adversarial-pentest-passes.md`
> (the adversarial verification of phase 4), `agents/01-architect.md` (the
> threat model and the diagrams of phase 3), `protocols/canonize.md` and
> `skills/toolcraft/` (canonize as you go), and
> `skill-corpus/vulnerability-reduction-by-version-bumps.md` and
> `skill-corpus/harden-docker-host.md` (the fixes phase 8 orders).
> Parameterized by `<FLEET_ROOT>` (the repositories under review),
> `<DEPLOYED_HOSTS>` (where the running images are), `<BOUNDARIES>` (the
> boundary set of phase 1) and `<FRAMING>` (the owner's cost and urgency
> framing for phase 8).

## When to apply

- A first security assessment of a system that has never had one.
- A periodic re-audit, or a re-audit after a major version or topology
  change.
- Before a system that nobody has reviewed, or that changed materially, is
  deployed where a network can reach it.

A sweep by generic checklist category is the move this procedure replaces.
Such a sweep misses the findings that live at a boundary, which are the
dangerous ones, and it trusts remembered advisory ids, which are often subtly
wrong.

## The invariant

Every phase after the fan-out reads **one findings ledger**, never the
separate audit transcripts. Where the scanner and anyone's memory disagree,
the scanner wins until a person shows why it is wrong. No finding with an
exploit-chain narrative reaches the report or the plan until an adversarial
pass has traced it against the deployed code. A refuted finding is corrected
**everywhere** it has already spread, the knowledge graph included.

## The procedure

### 1. Fan out by boundary

Dispatch independent audits concurrently, one per real boundary in
`<BOUNDARIES>`:

- one per **infrastructure layer** (every Dockerfile, compose file, proxy
  config and host), with each finding tagged "fixable with zero application
  code change" or not;
- one per **back-end service cluster**: a version inventory and the
  code-level attack surface;
- one per **front end**;
- one dedicated pass on the **identity and secrets layer**, because the
  highest-severity findings usually cluster there; it gets its own pass, not
  a line in a general audit;
- one **research pass** that builds a nearest-secure-version matrix from
  **live sources** (the upstream advisories and release notes, not memory),
  with OWASP and CIS references.

Consolidate everything into **one ledger file** before any later phase
starts: one row per finding with its id, boundary, evidence, severity,
remediation bucket and status. Each later phase reads the ledger, and each
correction is patched into the ledger, so it stays the one current source.

Gate: the ledger exists and every audit's findings are in it; no later phase
cites a transcript.

### 2. Make a real scanner the ground truth

Run a real scanner against **every image running** on `<DEPLOYED_HOSTS>`
(list the running containers; do not scan the images you assume exist), and
against every dependency manifest in filesystem mode, so it walks the real
transitive tree. A vendored internal library can drag in a cluster of
critical advisories that reading the top-level manifest never shows. The scan
driver, the report aggregator and the scanner's traps are on
`tool-corpus/ops/container-vuln-scan-and-aggregate.md`: only images present
locally are scanned, a stale vulnerability database under-reports with no
error, an end-of-life base image can scan clean, and an unquoted report glob
counts one target as all of them.

Cross-reference the scanner's output with the research pass and **flag each
disagreement** in the ledger: an advisory id cited wrongly, a cluster the
manual pass missed, a component the scanner did not see. Patch the ledger to
the scanner's result, and record why for each row where a person overruled
it.

Gate: every deployed image and every manifest has a scan result, and every
disagreement has a ledger row.

### 3. Synthesize in parallel

From the ledger, two independent renderings run concurrently:

- a **STRIDE threat model**;
- the **architecture diagrams**: the current topology with trust boundaries
  marked, an authentication-flow sequence for both the intended path and the
  attack path, one representative data-flow trace, and the proposed
  remediation topology.

### 4. Verify every exploit chain adversarially

This phase is mandatory. Before any top-ranked or exploit-chain finding
ships, a dedicated adversarial pass (`agents/11-pentest.md`, under the
evidence discipline of `skill-corpus/adversarial-pentest-passes.md`) traces
it against the real code:

- when the finding depends on how a specific library version behaves,
  inspect the artifact that is actually deployed (decompile the jar, read
  the installed package), not the documentation of some version;
- grep for the **absence** of a mitigating control yourself; do not take the
  audit's word that it is absent;
- trace an authorization or object-reference claim through the **full**
  request chain (entry point, service, data access), not the entry point
  alone.

A textbook-looking finding can be wrong. For example, a token
algorithm-confusion claim can fail closed in the deployed library,
while the real root cause is cheaper to exploit and worse (open
self-registration with no authorization behind it). A plan built on the
untraced claim fixes the wrong thing.

Gate: each exploit-chain finding is marked confirmed or refuted, with the
trace that decided it.

### 5. Propagate every correction

When phase 4 overturns a finding, correct it everywhere it appears: the
ledger, the threat model, the diagrams, and any fact already canonized into
the knowledge graph. A wrong "confirmed" fact in the graph is worse than a
wrong scratch note, because later sessions trust it. Re-task the graph's
owner to check the existing record against the corrected sources; appending
a correction beside the stale claim is not enough.

Gate: a search for the refuted claim across the ledger, the derived artifacts
and the graph finds it only where it is marked refuted.

### 6. Canonize as you go

Persist corrected facts, and the durable tools the review built (scan and
aggregation scripts, for example), as soon as a phase's findings are solid
(`protocols/canonize.md`; tools under the `toolcraft` doctrine). Do not batch
them to one final pass: the review survives an interrupted session, and later
phases build on corrected ground.

### 7. Finish the report before the plan

The plan takes the finished, corrected report as its input, so that it can
cite stable finding ids; a plan drawn in parallel cites findings that then
change. Publish the report as a rendered artifact meant to be read (a
self-contained HTML page with the diagrams, say), with a findings table where
every finding visibly carries its severity and remediation bucket.

### 8. Rank remediation by the owner's framing

Ask the owner for `<FRAMING>` before ordering anything, then follow it. A
workable default:

1. changes to compose files, Dockerfiles and host configuration only, which
   need zero application code, rank first whatever their severity;
2. dependency and image version bumps that keep behaviour come next
   (`skill-corpus/vulnerability-reduction-by-version-bumps.md`);
3. every other code change follows, ordered by effort.

The plan must say so explicitly when the highest risks of the **corrected**
ranking are not the cheapest fixes, and fast-track them ahead of the effort
order with a stated reason. Sorting by effort must never bury the most
dangerous confirmed finding under a pile of trivial ones.

To contain an exposure across many units, prefer the change you undo the same
way you made it. Turning the exposed surface off through the
environment channel needs no rehearsed rollback; a simultaneous
authentication change on every unit does. Apply it to one unit first, and
accept it by a differential: the changed unit stops exposing the surface, and
the units you did not change answer as before.

Plan authoring is a synthesis over a large, corrected evidence base. Run it
at the model class and effort the plant's delegation table assigns to
planning work (`core/method/delegation-model-classes.md`), not inline at
whatever tier the orchestrating session happens to run.

Gate: every plan item cites a ledger finding id; every fast-tracked item
states why.

## Anti-patterns

- Auditing by checklist category instead of by boundary.
- Later phases reading the audit transcripts instead of the ledger, or a
  correction landing in one transcript and not the ledger.
- Trusting remembered advisory ids over a scan, or scanning the images you
  assume are deployed instead of the running ones and their real dependency
  tree.
- Shipping an exploit-chain narrative nobody traced against the deployed
  artifact, the absence of the control, and the full request chain.
- Correcting a refuted finding in the report while the stale "confirmed"
  version lives on in the graph.
- Drawing the plan in parallel with the report, or letting the effort order
  bury the top confirmed risk.

## Reference files

- `agents/05-security.md`, `agents/11-pentest.md`, `agents/01-architect.md`
- `skill-corpus/adversarial-pentest-passes.md` (the adversarial evidence
  discipline of phase 4)
- `skill-corpus/vulnerability-reduction-by-version-bumps.md` (the bump
  campaign of phase 8's second bucket, and the residual triage after it)
- `tool-corpus/ops/container-vuln-scan-and-aggregate.md` (the scan driver and
  the report aggregator of phase 2, with the scanner's pitfalls)
- `skill-corpus/harden-docker-host.md` (the host floor many zero-code fixes
  apply)
- `protocols/canonize.md`, `skills/toolcraft/` (canonize as you go)
- `core/method/delegation-model-classes.md` (which model class authors the
  plan)
