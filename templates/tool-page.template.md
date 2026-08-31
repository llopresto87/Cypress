<!--
Template: tool-page.template.md
Authored by: docs-librarian
Lives at: docs/graph/tools/<tool-name>.md
Used: by `toolcraft` (kernel §3.8), whenever a task produces a durable,
reusable tool worth cataloging so the next session reuses it.
Filled by copying this template into the target path and replacing
every <placeholder>. Stable section numbers must not be renumbered;
agents and tooling index into them. Reached from the owning node via an
`artifacts:` edge (artifacts: - tools/<tool-name>.md) and registered in
docs/graph/tools/index.md.
-->

# Tool: <name>

## 0. Identity

- **Name:** <canonical, kebab-case>
- **Path:** <repo-relative path to the tool's code>
- **Language / runtime:** <e.g. python3, bash, node>
- **Owner:** <the agent/specialist responsible; "docs-librarian catalogs, <x> maintains">
- **Stability:** <"stable" | "experimental" | "deprecated — replaced by <name>">
- **Last reviewed:** YYYY-MM-DD by <agent>

## 1. What it does

One paragraph. The capability this tool provides and the recurring
operation it exists to stop the next session from reinventing. If a
different tool already does something adjacent, say so in §7.

## 2. Interface & invocation

The stable contract: how you run it, what it takes, what it returns.

```sh
<exact invocation, with flags/args>
```

- **Inputs:** <args, flags, env vars, files, stdin — each with type/shape>
- **Outputs:** <stdout/stderr/exit code, files written, side effects>
- **Preconditions:** <what must be true before running — services up, auth, cwd>

Treat this section as the tool's public API. Changing it is a versioned
change; record it in §8.

## 3. Where the code lives

The concrete files that make up the tool, and the entry point.

- **Entry point:** <path:symbol or path>
- **Supporting files:** <paths>
- **Dependencies:** <libraries it needs; link to docs/graph/libraries/<name>.md>

## 4. When to use it (and when not)

- **Use when:** <the task shapes this tool is the right answer for>
- **Do not use when:** <cases where a different tool or approach fits>
- **Idioms:** how this project drives the tool — conventions worth keeping
  consistent.

## 5. Pitfalls and sharp edges

What goes wrong. Each entry dated.

- **YYYY-MM-DD — <short title>:** what bit us, what to do instead.

## 6. Tests that cover it

The tests that authorize and pin this tool's behavior (§3.4). A tool with
no test is not durable — add one before cataloging.

- <path to test> — <what contract it pins>
- **How to run the tests:** `<command>`

## 7. References & neighbours

- **Owning node:** <docs/graph/nodes/<id>.md — the node whose `artifacts:` edge points here>
- **Related tools:** <docs/graph/tools/<other>.md — why, when to reach for it instead>
- **Decisions:** <ADR that recorded building this tool, if any>
- **Sources:** <URLs used to build it — retrieved YYYY-MM-DD>
- **Seed corpus:** <tool-corpus/<category>/<name>.md if this tool was seeded from or is a harvest candidate for the seed>

## 8. Changelog

- YYYY-MM-DD — created, by <agent>
- YYYY-MM-DD — interface change: <what and why>
- YYYY-MM-DD — recorded pitfall <name>
