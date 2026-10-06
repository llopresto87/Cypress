# Tool corpus

**Project-agnostic, durable** reusable tools. `install.sh <host> --expertise propose`
lists a page when its `stack:` matches the plant's manifests, and
`install.sh <host> --expertise <id>` places it; new pages enter through the **harvest** protocol
(`protocols/harvest.md`). The artifact mirror of `agent-corpus/` (roles) and
`skill-corpus/` (procedures), and the cross-project mirror of a plant's tool
catalog exactly as `library-corpus/` mirrors its library wiki and
`legal-corpus/` its legal leaves.

## Purpose

A plant builds durable tools during its life (kernel §3.8, `toolcraft`). Most of
the value worth keeping is the **capability and the approach** (what the tool
does, its interface shape, the algorithm behind it); the one project's wiring is
the plant's. When that capability is genuinely stack-neutral, this corpus
holds it, so the next plant starts from a working tool (or a clear blueprint) instead
of reinventing the wheel.

The next plant's `toolcraft` and `grow` **check this corpus first**: if a
matching tool exists, it seeds the project's `docs/graph/tools/<name>.md` from
it as the orientation layer, adopting the portable implementation when the stack
matches, or re-authoring against the project's own stack (test-first) when it
does not.

## What belongs here (surface + portable implementation, durable)

- The capability the tool provides and the recurring operation it exists for.
- Its interface shape: invocation, inputs, outputs, in general form and never
  one project's paths or arguments.
- The portable implementation, **when the tool is genuinely stack-neutral** (a
  self-contained script with no third-party or project dependencies, like the
  seed's own `graph-lint.py` and `agent-lint.py`).
- The approach or algorithm, and the idioms for using it that hold over time.
- Pitfalls inherent to the tool.

## What stays OUT (project-bound, ephemeral)

These are the *plant's* concern and belong in its `docs/graph/tools/<name>.md`,
never here:

- Project names, domain nouns, paths, credentials, or dataset shapes.
- Plant-bound specifics: a dependency locked to one project's pin, a call-site
  bound to one repo's layout, an environment only this project has. A version
  fact about what the tool drives (the minimum version of a CLI it calls, a flag
  that changed) is admissible when that tool's release notes or docs state it; a
  security fact and a calendar date are not (`library-corpus/README.md`, "What
  stays OUT").
- Anything that reads like this project's operations instead of a reusable tool.

## The withdraw-ready bar for a procedure or a tool

The corpora share one admission bar, the withdraw-ready bar
(`library-corpus/README.md`): a page lands only when a new plant could adopt it
instead of rediscovering its subject. For a library that means the plant need
not run a research-scout on its surface. For a tool page, and for a
`skill-corpus/` page, it means a plant can **build the tool, or run the
procedure, from the page alone**: every input, step, default and failure it
needs is on the page or on a page it names, and nothing is left for the reader
to work out from the source plant. The library bar's provenance rule holds here
too: a fact a plant observed, which upstream contradicts or is silent on, stays,
labelled as observed with its conditions and what the docs say.

## The stack field

A tool page may carry a `stack:` field, the same field a stack-keyed skill page
carries (`skill-corpus/README.md`, "Stack-keyed pages"), in a frontmatter block
that opens the page:

```yaml
---
stack:
  - library-corpus/<key>/<library>
---
```

Each entry is a library-corpus id. The selective placement (SPEC-0001 §6)
proposes a tool page only through this field, when the plant's manifests match
a library it names; a page without it is never proposed, and whether a plant
adopts it stays `grow`'s judgment. A stack-neutral tool carries no `stack:`.
`python3 tests/seed-lint.py` fails a `stack:` entry that names no library-corpus
page.

## Layout

```
tool-corpus/<category>/<name>.md
```

- Keyed by **category, not project**: one page per tool.
- `<category>`: the kind of work the tool does. Currently populated:
  - `ops`:
    - delivery: deploy pipelines, chained pipeline-run driving (with an Azure
      DevOps arm), large-artifact staging, registry digest resolution, image
      pin linting;
    - secrets and certificates: secret rotation, cert generation,
      structured-secret field detection, source-default credential gating;
    - configuration: layered-config merge verification, declared-variable
      existence auditing, renamed-config-key auditing, orphaned scoped-config
      auditing, live-state probing into declared config, declared-consumer
      link generation, config-driven server response harnessing;
    - dependencies and vulnerabilities: hashed-lock closure checking, resolved
      dependency gating, container vulnerability scan aggregation,
      not-affected statement generation;
    - test identities and data: disposable test-identity provisioning,
      owner-scoped data seeding;
    - device and API adapters: lenient response parsing;
    - agent sessions: destructive-command guarding, session cost profiling.
  - `testing`: smoke suites, behavior-baseline capture, in-network end-to-end
    driving, fire-and-forget command observation, live contract checking,
    CI-runner simulation, failure-signature triage, working-tree snapshots,
    authentication-parity oracles, parallel suite running, static
    config-contract gating, cross-implementation parity verification,
    test-hygiene linting, touched-file lint hooks.

  Further categories such as `scaffolding`, `codegen`, `data`, and `analysis`
  are added as they are harvested.
- `<name>`: the canonical id, lowercased, kebab-case.

## Rules

- **Agnostic or it does not belong here.** No project name, domain noun, path,
  credential, or dataset shape. If you cannot describe the tool without naming
  the plant, it is not ready to harvest.
- **Durable or it does not belong here.** A tool bound to one project's pin or
  one repo's layout is the plant's, not the seed's. A tool that serves one stack
  belongs here with a `stack:` field (above). A corpus page reads like a
  general-purpose utility's own README, not one project's runbook step.
- **Orientation, not gospel.** Adopt the portable implementation only when the
  stack matches; otherwise treat the page as a blueprint and re-author against
  the project's real stack, test-first. Confirm the tool still fits before use.
- **A portability claim is a gate, not an adjective.** `tests/test-tool-corpus.sh`
  compiles every shell and Python implementation on a page declaring
  `Stability: portable`, exercises the behaviour of the pages that ship a
  runnable one, and fails a run whose selector matched almost nothing. Code an
  adopting project is invited to run as-is, that nobody has run, is the same
  green lie a gate that asserts nothing is. So a page either earns the word or
  says `blueprint`, which is an honest and common answer.
