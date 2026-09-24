# CYPRESS

## What CYPRESS is

CYPRESS copies instruction files, a Markdown method and small standard-library scripts into your repository, for the coding [agent](DOCUMENTATION.md#term-agent) you already use. It is not a library your code imports, not a service and not a model.

Installing only places files. A separate session, started by pasting one prompt, reads your repository and builds its [knowledge graph](DOCUMENTATION.md#term-knowledge-graph).

## Who it is for and not for

It is for developers who work in a code repository through a supported [harness](DOCUMENTATION.md#term-harness): Claude Code, Prime Agent, opencode, Codex or GitHub Copilot. Support differs by harness, and some are deprecated; the [host capability matrix](documentation/host-capability-matrix.md) and the [host support decision](docs/decisions/adr-0009-host-support-tiers.md) say which.

It is not tied to one language or stack; the shipped reference [corpora](DOCUMENTATION.md#term-corpus) lean toward some stacks. It is not for someone who does not use an agent-capable coding [tool](DOCUMENTATION.md#term-tool), because nothing in the install acts without a session.

## What installing does to your repository

An install writes these into your project: the [kernel](DOCUMENTATION.md#term-kernel) instruction file `CLAUDE.md` or `AGENTS.md` at the project root, the harness directory such as `.claude/`, the graph under `docs/graph/`, and the install stamp `.cypress/seed.json`. Other harnesses write elsewhere; the [install guide](INSTALL.md) lists where.

A differing file already in place is kept beside itself as a timestamped copy and then replaced, not merged. The one file replaced without a copy is the derived install stamp `.cypress/seed.json` ([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)).

The install does not touch application source, `.gitignore`, git history or CI.

## What it costs

| Figure | What it covers and how it was obtained |
|---|---|
| {{EAGER_CLAUDE_CODE}} bytes | per session on Claude Code: the always-loaded files, computed from the installed files by the test run of this repository; a lower bound |
| 11% more tokens | per task, on one small, well-specified task; measured once ([evidence record](docs/plans/front-door-evidence.md)) |

The always-loaded figure does not count files a session reads on demand, each worker it starts or the one-time setup pass. No money figure exists.

## Try it

```sh
git clone https://example.com/cypress.git
bash cypress/install.sh claude-code /path/to/your/project
```

Then paste the entry prompt into a new session rooted at the project. None of this needs the project's vocabulary. The clone command takes whatever the default branch holds when it runs, not a tagged release. A new session may be needed before started workers appear; `delegation.harness-registration` explains why.

<!-- first-screen-end -->

## How it works

CYPRESS is a written [workflow](DOCUMENTATION.md#term-workflow), not a program. The agent reads which steps a task needs and in what order, and does them itself. It hands steps that need a clean context to [subagents](DOCUMENTATION.md#term-subagent). The named step lists are [protocols](DOCUMENTATION.md#term-protocol), and the procedures read on demand are [skills](DOCUMENTATION.md#term-skill). A few [hooks](DOCUMENTATION.md#term-hook) and [linters](DOCUMENTATION.md#term-linter) check parts of the work; the rest depends on the model and on you.

After the install your repository is a [plant](DOCUMENTATION.md#term-plant), a project the method has grown into.

## Why it is built this way

Each design choice has a decision record, and the [decision index](docs/decisions/index.md) lists them with their status.

## What it does not do

### Requested, not enforced

- The task [tier](DOCUMENTATION.md#term-tier) is the model's own call ([tier classification](DOCUMENTATION.md#enf-tier-classification)).
- Writing a spec before code is asked of the model ([spec before code](DOCUMENTATION.md#enf-spec-before-code)).
- Writing a failing test before code is asked of the model ([test before code](DOCUMENTATION.md#enf-test-before-code)).

### Not yet measured

- The time a first install takes on a large repository: not measured.
- The cost of the one-time setup session: not recorded.

## Where to go next

- [The manual](DOCUMENTATION.md)
- [Glossary](DOCUMENTATION.md#glossary)
- [What each control holds and misses](DOCUMENTATION.md#enforcement)
- [Agents reference](documentation/agents-reference.md)
- [Protocols reference](documentation/protocols-reference.md)
- [Skills and templates reference](documentation/skills-and-templates-reference.md)
- [Host capability matrix](documentation/host-capability-matrix.md)
- [Decision index](docs/decisions/index.md)
- [Install guide](INSTALL.md)
