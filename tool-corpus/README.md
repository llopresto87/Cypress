# Tool corpus

**Project-agnostic, durable** reusable tools — folded back into the seed by the
**harvest** protocol (`protocols/harvest.md`, `HARVEST_PROMPT.md`) from a plant's
`docs/graph/tools/` catalog. The artifact mirror of `agent-corpus/` (roles) and
`skill-corpus/` (procedures), and the cross-project mirror of a plant's tool
catalog exactly as `library-corpus/` mirrors its library wiki and
`legal-corpus/` its legal leaves.

## Purpose

A plant builds durable tools during its life (kernel §3.8, `toolcraft`). Most of
that value is not the one project's wiring but the **capability and the approach**
— what the tool does, its interface shape, the algorithm behind it. When that is
genuinely stack-neutral, harvest folds it here so the next plant starts from a
working tool (or a clear blueprint) instead of reinventing the wheel.

The next plant's `toolcraft` / `grow` **checks this corpus first**: if a matching
tool exists, it seeds the project's `docs/graph/tools/<name>.md` from it as the
orientation layer — adopting the portable implementation when the stack matches,
or re-authoring against the project's own stack (test-first) when it does not.

## What belongs here (surface + portable implementation, durable)

- The capability the tool provides and the recurring operation it exists for.
- Its interface shape: invocation, inputs, outputs — general, not one project's
  paths or arguments.
- The portable implementation, **when the tool is genuinely stack-neutral** (a
  self-contained script with no third-party or project dependencies, like the
  seed's own `graph-lint.py` / `agent-lint.py`).
- The approach/algorithm and enduring idioms for using it.
- Conceptual pitfalls inherent to the tool.

## What stays OUT (project-bound, ephemeral)

These are the *plant's* concern and belong in its `docs/graph/tools/<name>.md`,
never here:

- Project names, domain nouns, paths, credentials, or dataset shapes.
- Stack-pinned specifics — a version-locked dependency, a call-site tied to one
  repo's layout, an environment only this project has.
- Anything that reads like this project's operations rather than a reusable tool.

## Layout

```
tool-corpus/<category>/<name>.md
```

- Keyed by **category, not project** — one page per tool.
- `<category>` — the kind of work the tool does. Currently populated: `ops`
  (deploy pipelines, secret rotation, cert generation, disposable test-identity
  provisioning) and `testing` (smoke suites, CI-runner simulation,
  failure-signature triage). Further categories such as `scaffolding`,
  `codegen`, `data`, and `analysis` are added as they are harvested.
- `<name>` — the canonical id, lowercased, kebab-case.

## Rules

- **Agnostic or it does not belong here.** No project name, domain noun, path,
  credential, or dataset shape. If you cannot describe the tool without naming
  the plant, it is not ready to harvest.
- **Durable or it does not belong here.** A tool bound to one stack pin or one
  repo's layout is the plant's, not the seed's. A corpus page reads like a
  general-purpose utility's own README, not one project's runbook step.
- **Orientation, not gospel.** Adopt the portable implementation only when the
  stack matches; otherwise treat the page as a blueprint and re-author against
  the project's real stack, test-first. Confirm the tool still fits before use.
