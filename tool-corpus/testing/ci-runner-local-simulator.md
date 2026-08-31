# Tool: ci-runner-local-simulator

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: a stack-neutral *pattern*, not
> a portable script. The adopting plant builds it against its own CI system,
> infrastructure API, and repo layout.

## 0. Identity

- **Category:** testing
- **Name:** ci-runner-local-simulator
- **Language / runtime:** any (the pattern is language-agnostic; typically a
  bash/script driver plus a query against the CI/infra API)
- **Stability:** **blueprint only** — no portable implementation; the value is
  the two-tier reconstruction pattern and its hard rules

## 1. What it does

Reconstructs the CI agent's environment **locally** so a developer can run any
repo command exactly as the real runner would — without pushing a commit and
waiting for the pipeline. It exists to collapse the edit → push → wait → read-log
loop into a local run, and to stop each project from re-inventing a fragile,
hand-maintained "fake CI env" that drifts from the real one.

## 2. Interface & invocation

```sh
ci-local.sh [--project <id>] -- <command to run as the runner would>
#   --project: which project/pipeline to simulate (required if ambiguous)
#   everything after -- : the repo command to execute in the reconstructed env
```

- **Inputs:** a project/pipeline selector; the command to run; a **declarative
  project-manifest block** that names the infra source and variable sets (no
  target/host literals baked into the script).
- **Outputs:** the command's own output, run in an environment populated as CI
  would populate it; a clear failure if the target is ambiguous (see §3).
- **Preconditions:** access to the live infrastructure/CI API for the portable
  values; the machine-local file for host-only values.

## 3. Approach / algorithm

**Two-tier environment reconstruction** — the core durable idea:

1. **Portable / project-level tier:** values that are the same for any agent
   running this project (variable groups, non-secret config, service coordinates)
   are **queried live from the infrastructure/CI API** at run time, so they never
   go stale in a checked-in copy.
2. **Machine-local / host-only tier:** values that are specific to *this*
   developer's machine (local paths, local credentials, a personal token) live in
   a **separate local file** that is never committed and never queried from
   shared infra.

   The two tiers are merged into the process environment, then the requested repo
   command runs as if the real runner had populated it.

**Config is fully declarative.** All target/infra coordinates come from a
**project-manifest block**, not baked-in literals — so the same simulator serves
**many projects unchanged**; adding a project is a manifest entry, not a code
edit.

**Hard rule — fail loud on ambiguity.** If the target is ambiguous (multiple
candidate projects, pipelines, or hosts match), the tool **must FAIL and
enumerate every candidate by name** — it must **never silently guess** one.
Silently picking a candidate reconstructs the wrong environment and produces
confidently-wrong local results, which is worse than not running.

## 4. Portable vs blueprint

- **Blueprint (the whole page):** there is no stack-neutral implementation to
  copy. The adopting project builds the driver against its own CI system's API,
  its own secret store, and its own manifest format.
- **Durable across every implementation:** (a) the two-tier split — live-queried
  project values vs a local host-only file; (b) declarative manifest config with
  no baked-in target literals; (c) fail-loud-and-enumerate on ambiguity.

## 5. Pitfalls and sharp edges

- **Silently guessing the target** is the cardinal sin — it yields a plausible
  but wrong environment. Enumerate and stop.
- **Baking target/host literals into the script** couples it to one project and
  defeats reuse; keep everything in the manifest.
- **Committing the host-only tier** leaks local credentials and makes the "local"
  file drift into a shared fiction; keep it out of version control.
- **Trusting a stale checked-in copy of project values** reintroduces the drift
  the live query exists to prevent.
- **Simulation is not the pipeline.** A local run approximates the runner; it
  does not replace a real CI run for the gate of record.

## 6. Tests that cover it

Cover: an ambiguous target produces a non-zero exit that lists all candidates by
name; a fully-specified target reconstructs the expected variable set; host-only
values come from the local file, not the shared query; adding a project is a
manifest-only change.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/container-deploy-pipeline.md` (the pipeline
  whose runner environment this simulates); `tool-corpus/ops/env-secret-rotation.md`
  (the secret file the host-only tier may read from);
  `tool-corpus/testing/failure-signature-triage.md` (consumes the result files
  the runs reconstructed here produce, so N baseline runs are cheap).
- **Sources:** distilled from harvested plant experience; no external URL.

## 8. Changelog

- 2026-07-16 — created from harvested, generalized capability, by docs-librarian.
