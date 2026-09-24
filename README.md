# CYPRESS

## What CYPRESS is

CYPRESS is an installer. It copies instruction files, a method written in Markdown and a few small Python scripts that need only the standard library into your repository, for the AI coding [agent](DOCUMENTATION.md#term-agent) you already use. It is not a library your code imports, not a service and not a model.

Installing only places files. A separate agent session, started when you paste one prompt, reads your repository and builds its [knowledge graph](DOCUMENTATION.md#term-knowledge-graph): short linked notes about your project that a session opens a few at a time instead of rereading the code. The method in those files asks the agent to size its process to each task's risk, to write a [specification](DOCUMENTATION.md#term-specification) and a failing test before the code, and to hand steps that need a clean context to separate workers.

## Who it is for and not for

It is for developers who work in a code repository through an agent [harness](DOCUMENTATION.md#term-harness) the installer supports: Claude Code, Prime Agent, opencode, Codex or GitHub Copilot. Support is not the same on every harness, and some of them are deprecated. The [host capability matrix's support table](documentation/host-capability-matrix.md#support-tiers-adr-0009) and the [host support decision record](docs/decisions/adr-0009-host-support-tiers.md) say which is which.

The method assumes no language, framework or stack. The reference [corpora](DOCUMENTATION.md#term-corpus) that ship with it are narrower: the library notes lean toward .NET and Java, and the legal citations cover one national jurisdiction. The library notes are not placed in your project, and the legal citations are placed only when you ask for them. The [corpora reference](documentation/corpora-and-integrations-reference.md) has the breakdown.

It is not for someone who does not use an agent-capable coding [tool](DOCUMENTATION.md#term-tool), because nothing in the install acts until an agent session reads it.

## What installing does to your repository

An install for Claude Code writes these into your project:

- the [kernel](DOCUMENTATION.md#term-kernel), a short instruction file the harness reads at the start of every session: `CLAUDE.md` at the project root, with `AGENTS.md` beside it as a symlink to it (a copy where symlinks are unavailable); on the other harnesses `AGENTS.md` holds the kernel and `CLAUDE.md` is the symlink;
- the harness directory `.claude/`, holding the agent definitions, the [skills](DOCUMENTATION.md#term-skill), slash commands, hook scripts and settings;
- `docs/graph/`, where the knowledge graph lives: the method's own notes, and a skeleton that the first session fills in from your code;
- the install stamp `.cypress/seed.json`, which records the version and options of the install;
- `EXPERT_SEED_INSTALL_PROMPT.md`, a local copy of the entry prompt for later sessions.

Other harnesses get their own directory in place of `.claude/`, such as `.opencode/` or `.prime/agent/`, and the [install guide](INSTALL.md) lists each one.

A file already in place that differs from the new one is kept beside itself as a timestamped copy and then replaced, not merged. A file that already matches is left alone. The one file replaced without a copy is the install stamp `.cypress/seed.json` ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)). Files under `docs/graph/` that belong to your project, such as the graph's index, are only added where missing ([project files kept](DOCUMENTATION.md#enf-plant-files-kept)). The one exception is the `plant:` entry of `docs/graph/index.md`, which the installer rewrites in place, also without a copy: it adds the entry if it is absent and puts each value you pass on the command line into a line still left as a placeholder, keeping any value already declared.

The install does not touch your application source, `.gitignore`, git history or CI.

## What it costs

| Figure | What it covers, and how it was obtained |
|---|---|
| 26 261 bytes | per session on Claude Code: the kernel plus the one-line description of every agent and skill, computed from the [seed](DOCUMENTATION.md#term-seed)'s files by this repository's test run; a lower bound, not a live reading |
| 11% more tokens | per task, against a session with no method, on one small, well-specified task; measured once ([evidence record](docs/plans/grill-7.29.0-front-door/method-overhead-evidence.md)) |

The always-loaded figure leaves out the notes a session opens on demand, each worker it starts, the text the hooks add to each prompt, and the one-time pass that builds the graph. The [host capability matrix](documentation/host-capability-matrix.md) gives the figure for each other harness. No money figure exists.

## Try it

```sh
git clone https://github.com/llopresto87/Cypress
./Cypress/install.sh claude-code --project-dir /path/to/your/project
```

The clone takes whatever the default branch holds when you run it, not a tagged release. The second command only places files, and it does not edit your code. Then open an agent session rooted at your project and paste [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) into it. That starts the one-time [growth](DOCUMENTATION.md#term-growth) pass, which reads your repository and builds its graph. None of these steps asks you to learn the project's vocabulary first.

On a first install, a harness may need a fresh session before it can start the agents that were just placed; the [delegation notes](core/method/delegation.md) record when, under `delegation.harness-registration`.

<!-- first-screen-end -->

## How it works

CYPRESS is a written [workflow](DOCUMENTATION.md#term-workflow), not a program. The agent reads which steps a task needs and in what order, carries them out itself, and hands the steps that need a clean context to subagents, while a few hooks and linters check parts of the work and the rest is left to the model and to you.

The steps are written down as [protocols](DOCUMENTATION.md#term-protocol), procedures a session follows in order, and the [protocols reference](documentation/protocols-reference.md) lists them. The method asks each task to be sorted into a risk [tier](DOCUMENTATION.md#term-tier) first, from a question (T0) to a change to architecture or contracts (T3), and the tier decides how much process the task gets. A T3 change gets a specification, a failing test before the code ([test-first development](DOCUMENTATION.md#term-test-first)), and review by separate workers.

Those workers are [specialists](DOCUMENTATION.md#term-specialist): roles such as `architect`, `tester` and `reviewer`, each defined in one file that names its tools and its model class. The [agents reference](documentation/agents-reference.md) lists all of them.

Before reading code, a session is asked to open the graph's [router](DOCUMENTATION.md#term-router), an index that points to the few [nodes](DOCUMENTATION.md#term-node) a task needs, and to load only those. This is [progressive disclosure](DOCUMENTATION.md#term-progressive-disclosure) applied to your own project. Each fact is meant to live in one node, with every other node linking to it ([one home per fact](DOCUMENTATION.md#term-one-home-per-fact)).

Once grown, your repository is a [plant](DOCUMENTATION.md#term-plant) of the [seed](DOCUMENTATION.md#term-seed), which is this repository. Lessons can travel between them later: [harvest](DOCUMENTATION.md#term-harvest) proposes a plant's lessons back to the seed, and [graft](DOCUMENTATION.md#term-graft) carries an updated seed onto a plant grown earlier. The method starts neither unless the [steward](DOCUMENTATION.md#term-steward) asks ([steward only](DOCUMENTATION.md#enf-steward-only)).

## Why it is built this way

A coding agent works inside a fixed context window, and an agent that has read everything has no signal about what matters. So the always-loaded part stays small and the rest is looked up when a task needs it. Process is sized to risk so that a typo fix does not pay a feature's coordination cost. Specifications and tests come first so that a reviewer can check the work against something written before it. Steps that need a clean context go to separate workers so that one step's reading does not crowd out the next.

Each of these choices has a decision record, and the [decision index](docs/decisions/index.md) lists them with their status.

## What it does not do

The method is written for the model to follow, and most of it is a request. For each mechanism, the manual's table of [what each control holds and misses](DOCUMENTATION.md#enforcement) names its class and its gaps.

### Requested, not enforced

- Choosing a task's tier is the model's own call, and no tool sees a tier chosen too low ([tier classification](DOCUMENTATION.md#enf-tier-classification)).
- Writing a specification before the code is asked of the model. A linter checks a written specification's shape, not when it was written ([spec before code](DOCUMENTATION.md#enf-spec-before-code)).
- Writing a failing test before the code is asked of the model, and no tool sees the order ([test before code](DOCUMENTATION.md#enf-test-before-code)).
- Opening the router first and working through a protocol are asked of the model. The [routing](DOCUMENTATION.md#term-routing) hook adds a pointer to each prompt and holds nothing ([protocol order](DOCUMENTATION.md#enf-protocol-order), [prompt pointer](DOCUMENTATION.md#enf-route-hook)).
- The linters report a fault only when someone runs them, and the install adds no CI to your project ([graph lint](DOCUMENTATION.md#enf-graph-lint), [this repository's own checks](DOCUMENTATION.md#enf-seed-gate)).
- The kernel's byte budget is checked only in this repository's own test run, and nothing re-measures the copy in your project ([kernel budget](DOCUMENTATION.md#enf-kernel-budget)).

### Not yet measured

- The overhead on a large task, one with a specification, several files and a rollback path: not measured. The one overhead figure above was measured once, on a small task.
- The tokens the one-time growth pass spends on a repository: not measured.
- Whether the method improves the quality of the work: not measured.
- Whether a host keeps the kernel's text after it compacts a long session: not recorded.

## Where to go next

- [The manual](DOCUMENTATION.md), the long-form guide
- [The glossary](DOCUMENTATION.md#glossary), one entry per project word
- [What each control holds and misses](DOCUMENTATION.md#enforcement)
- [Agents reference](documentation/agents-reference.md)
- [Protocols reference](documentation/protocols-reference.md)
- [Skills and templates reference](documentation/skills-and-templates-reference.md)
- [Host capability matrix](documentation/host-capability-matrix.md)
- [Decision index](docs/decisions/index.md)
- [Install guide](INSTALL.md), including upgrade and removal
- Per-harness notes: [Claude Code](integrations/claude-code/README.md), [Prime Agent](integrations/prime-agent/README.md), [opencode](integrations/opencode/README.md), [Codex](integrations/codex/README.md), [GitHub Copilot](integrations/github-copilot/README.md)
- To upgrade a plant grown earlier, the [graft prompt](GRAFT_PROMPT.md); to fold a plant's lessons back, the [harvest prompt](HARVEST_PROMPT.md)
- What changed in each release: the [changelog](CHANGELOG.md)

## License

CYPRESS is released under the MIT License. See [`LICENSE`](LICENSE).

Copyright (c) 2026 Luigi Lopresto.
