---
name: opencode-live-verification
description: Seed-only. How a steward re-verifies the opencode adapter against a running OpenCode 2 release, surface by surface, and records the version, so a beta host's change is found by a repeated check instead of by a plant.
id: skill.opencode-live-verification
kind: skill
origin: seed-only
owns:
  - opencode-live-verification.when
  - opencode-live-verification.setup
  - opencode-live-verification.checks
  - opencode-live-verification.record
load_when:
  - "verify the opencode adapter on a new OpenCode 2 release, re-run the live checks"
  - "raise or lower an opencode cell of the host capability matrix"
---

# opencode-live-verification

OpenCode 2 is a beta whose plugin API may change between releases. The gate cannot need it, so what the adapter holds on that host is verified by this procedure, run by hand from the seed and never placed in a plant ([ADR-0021](../decisions/adr-0021-seed-only-procedures-stay-home.md)). A matrix cell for opencode rises only on an observation made here; documentation and fixture runs lower or hold a cell, they do not raise one.

## When to apply (`opencode-live-verification.when`)

- A new OpenCode 2 release is installed and a steward is about to cite it.
- Before a release that changes an opencode surface.
- When a plant reports that a route suggestion, a status register, a refusal or a specialist is missing on opencode.

## Setup (`opencode-live-verification.setup`)

1. Install the release under test and read its version from `opencode2 --version`.
2. Make a fresh git repository in a temporary directory outside the seed, install the seed into it with `install.sh opencode --project-dir <dir>`, and run the host from that directory.
3. Isolate the host from the operator's own configuration where the release offers a switch (a test home, no Claude Code skill discovery, no free-model catalog, no auto-update). Read the release's environment variable names from its documentation; do not copy a name from this page.
4. Choose the model for the runs with the owner before the first call. Every run sends prompts to a model endpoint, so use synthetic prompts only, keep the count small, and never write the host's shell environment, which carries credentials, into a file.
5. Fill the opencode cells of `docs/graph/models.md` in the temporary plant with one selector the endpoint serves (a `#<variant>` suffix on some rows), then re-run `install.sh opencode`.

## Checks (`opencode-live-verification.checks`)

Each check names the surface, the command, and the expected observation. Report each as passed, failed, not run, unavailable or inconclusive, with the host version.

| # | Surface | Do | Expect |
|---|---|---|---|
| 1 | Load | `opencode2 debug agents` in the plant, with the host's log level at warning | every graph agent listed once under its callable name, no configuration warning, `subagent_depth` accepted under `experimental` |
| 2 | Registration | read the same listing | each specialist's `mode`, its model (and variant) from the map, and its `permissions` as rendered |
| 3 | Tool bound | run a read-only leaf and ask it to write a file | the host refuses or hides the edit tool; no file appears |
| 4 | Leaf cannot delegate | ask a leaf to launch a subagent | refused by the host |
| 5 | Delegation list | run a coordinator and ask it to launch an agent outside its list, then one inside | outside refused, inside runs |
| 6 | Depth | a chain of three launches | the third level is reachable; one past `experimental.subagent_depth` is refused with the host's depth message |
| 7 | Route | send a first prompt, then a second in the same session | the route suggestion arrives once, as a synthetic message ahead of the prompt, byte-identical to the core's text; the user's prompt is unedited |
| 8 | Status | open a new session | the status register arrives once |
| 9 | Child | have a session launch a subagent | the child's first prompt gets neither message |
| 10 | Bounded execution | ask for a command the guard lists, then its bounded form | the first is refused with the core's reason text, which the model reports; the second runs |
| 11 | Core removed | delete a core, repeat 7 and 10 | nothing is injected, nothing is blocked, and `install.sh opencode --check` names the missing core |
| 12 | Re-install | re-install over a plant in the earlier shape | the host loads the plant with no warning |

A check that needs a model to act (3 to 10) is inconclusive when the model never attempts the action; ask again in plainer words before recording that.

## Record (`opencode-live-verification.record`)

Write the verified version into `integrations/opencode/verified-version`, the one home; the adapter README and the host matrix cite it and the seed lint holds both to it. Each matrix cell's evidence line carries the version it was observed on. A check that now fails lowers its cell in the same change and opens a defect in the matrix with what would close it.
