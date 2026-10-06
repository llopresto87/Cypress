---
id: method.host-parity
tier: 2
kind: method
origin: seed
title: host parity — the authoring host is not the execution target, validate where it runs, inspection writes nothing
owns:
  - engineering-posture.host-parity
  - engineering-posture.no-write-inspection
requires:
peers:
  - method.engineering-posture
  - method.minimum-sufficient-work
  - method.decision-economy
  - method.bounded-execution
load_when:
  - "works locally but fails in CI or on the target host"
  - "did this run touch production"
  - "inspect a shared host or workspace read-only, a fix lets a loop continue past a failure"
  - "mutating run against live infrastructure, the dry run passed, which hosts the target selector resolves to"
  - "automation converges the account it authenticates with, its own access path"
prevents: A green result on the authoring host reported as working on the target, an inspection that writes to a shared host, and a loop fix that carries on past what a failure protected.
est_tokens: 1296
---

## The machine you build on is not the machine it runs on

Where a change is authored and where it executes are different systems
with different shells, tool versions, path layouts, package names, line
endings, locales, and privileges. A green result on the authoring host
is evidence about the authoring host. It is not evidence about the
target, and presenting it as such is a sources-of-truth error
(`method.engineering-posture` §1): the target is authoritative for
claims about the target, exactly as the spec is authoritative for
claims about intent.

Two corollaries carry most of the failures:

- **Validate where it runs, or say that you did not.** Exercise the
  change on the execution target, in a faithful container, or in CI.
  Where none of those is available, the honest report is "verified on
  the authoring host only; unverified on <target>", which is useful.
  Silence, which reads as verified, is not. A claim that the change works
  cites the execution target or real CI. A local reproduction is for
  diagnosis only.
- **Existing locally is not existing.** A file the build resolves from
  the working tree but that is untracked, ignored, or unpushed does not
  exist for CI, for a teammate, or for the deployed artifact. Before
  claiming delivery, confirm the artifact is where the *consumer* will
  look for it, not merely where you left it. Describe that location by
  its role ("the directory holding the application checkouts"), because
  a position ("the sibling checkout") is true on one machine and false
  on the other.

The same reasoning governs a local model, a local service, or a local
credential standing in for a remote one: the substitute is a
convenience for iteration, never the evidence.

When the target is live infrastructure, classify the blast radius before
running anything (local, read, artifact-producing, or mutating), because
a "dry run" still authenticates, reads, scans, and writes local
artifacts, and a read-shaped endpoint can allocate from a finite pool. A
green dry run is structural evidence only, because a step can skip or
defer in dry-run mode the work that fails for real: follow it with a
scoped real apply before claiming the change works. Before any mutating
run, resolve the target selector to the concrete list of hosts it
matches and confirm that list, because a shorthand that resolves
differently from what its author meant aims the run somewhere else, or
nowhere. Validate the whole declared change set for self-lockout before
executing any part of it (the guard sits before the first mutation, not
between mutations); confirm the target is the project's own, by an
ownership marker, before acting on it; and exclude the automation's own
access path and identity from the set it manages while still asserting
it keeps the privileges it needs. That exclusion is the default, and
overriding it takes an explicit, named flag set by a decision, never on
the agent's own initiative, because converging the identity the
automation authenticates with can lock it out of everything it manages.
Whether the target is a real production system at all is a plant fact:
`plant.environment_class` in the router's frontmatter answers it once,
and every run reads it there. Which environment a given run actually
touched is a different question, and it is answered from first-hand
identity evidence: the host's own identity, the runner that executed the
job, the file a line of text came from. A word in a log prefix or a
script's name is a label somebody chose. It is not evidence of where the
code ran.

### Inspection writes nothing (`engineering-posture.no-write-inspection`)

Inspecting a shared host writes nothing there. A shared host is any machine
or workspace that another session, person or process also uses. Some commands
that look like reads are writes: `git fetch` in a shared workspace moves refs
that everyone working there sees, and a status command can refresh an index or
take a lock. Run a command that might write on a copy you own, because on the
shared host it changes state that other sessions see.

### A loop that carries on past a failure re-checks what the failure guarded

A fix that lets a loop continue past a failure re-checks what the failure
protected. A failure that stops a loop also stops the later iterations from
acting on whatever state the failure left behind. Before you change the loop to
carry on, name the condition the failure was guarding, re-check it, and let
each later iteration act only while it holds. Without that check, the fix turns
one failed step into a run of damaging ones.

## Neighbours

- `method.engineering-posture`: load when the question is sources of truth, how much context to load, whether structure earns its cost, integrating a change, or side effects at a boundary.
- `method.bounded-execution`: load when a command may hang or outlive its session, or a run must be judged running, stuck or finished.
