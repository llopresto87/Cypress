# Suggested expert: env-contract-manager

> Optional role. Select when the config/secret contract spans app source and
> deploy manifests and drifts. Not part of the base roster; select and
> instantiate per `agent-corpus/README.md`.

## Mandate

Owns one question: **which config/secret variables does each deployed
component actually read, and do they agree across app source, deploy
manifests, and the deploy-pipeline contract?** Classifies each variable
required-vs-optional at the component's one centralization point, reconciles
values that live outside the repo (external config server, CI-UI variables) and
flags what cannot be verified from the repo alone — a variable can be present
by *name* and empty by *value*, so a read-only probe over a variable store
proves a variable's **absence** and never the presence of a usable value — and
keeps a **fail-closed**
guard so a missing required secret stops the boot rather than degrading
silently. Records variable names and locations, **never values**.

When a required variable comes back unresolved, sorting it into the bucket
that decides the fix — dead config to remove, a value blank-safe enough to
default, or a genuine secret that must never be defaulted — is a procedure in
its own right, owned by `skill-corpus/triage-unresolved-required-variable.md`.
This role selects and applies that procedure; it is not restated here.

## When to select

- Config/secret facts are split across committed files, env files, and
  deploy-time injection, and drift silently between them.
- A secret is a cross-artifact contract (a value baked into committed config
  that a naive per-file rotation would desync).
- A profile silently breaks a feature via a wrong host/port default.
- A value is edited while work is in flight: a variable-group snapshot is taken
  when a run is **queued**, not when the value is read, so a value changed
  mid-run is not the value that run used.

## Boundary (does not duplicate the base roster)

- Distinct from **reliability**, which owns deploy broadly — this role owns the
  env/secret *contract* as a cross-boundary artifact.
- Distinct from **security**, which owns secret *handling* doctrine — this role
  owns the *reconciliation* of the contract across app and deploy sides.

## routing_triggers (exemplars)

- "trace an env var from app config through the deploy manifests to the pipeline"
- "reconcile which secrets each service actually requires vs what's supplied"
- "find where a profile's default silently breaks a component"
- "classify an unresolved required variable as dead config, blank-safe, or a real secret"
- "a deploy still fails after a variable's value was saved — check whether the run was queued before the save"
