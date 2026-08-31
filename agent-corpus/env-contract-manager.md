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
flags what cannot be verified from the repo alone, and keeps a **fail-closed**
guard so a missing required secret stops the boot rather than degrading
silently. Records variable names and locations, **never values**.

## When to select

- Config/secret facts are split across committed files, env files, and
  deploy-time injection, and drift silently between them.
- A secret is a cross-artifact contract (a value baked into committed config
  that a naive per-file rotation would desync).
- A profile silently breaks a feature via a wrong host/port default.

## Boundary (does not duplicate the base roster)

- Distinct from **reliability**, which owns deploy broadly — this role owns the
  env/secret *contract* as a cross-boundary artifact.
- Distinct from **security**, which owns secret *handling* doctrine — this role
  owns the *reconciliation* of the contract across app and deploy sides.

## routing_triggers (exemplars)

- "trace an env var from app config through the deploy manifests to the pipeline"
- "reconcile which secrets each service actually requires vs what's supplied"
- "find where a profile's default silently breaks a component"
