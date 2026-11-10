# opencode integration

This adapter targets **OpenCode 2**, the generation that runs as `opencode2`.
It was last verified live against OpenCode 2.2.6; that version's one home is
[`verified-version`](verified-version), and the seed lint holds this page and
the [host capability matrix](../../documentation/host-capability-matrix.md) to
it. OpenCode 1 (`opencode`) is not supported: nothing is built, tested or
documented for it. The adapter name, the installer argument, the install stamp
and the `.opencode/` paths keep the name `opencode`.

opencode is a `first-class` host, at parity with Claude Code
([ADR-0033](../../docs/decisions/adr-0033-opencode-first-class-on-opencode-2.md)):
a feature that ships on one first-class host is owed here, through the host's
own mechanism where OpenCode 2 holds it, through a thin plugin envelope over the
shared hook core where only its plugin API does, and otherwise as a defect to
close, listed [below](#differences-from-claude-code-defects-to-close).
`install.sh all` installs it.

## What the host reads

OpenCode 2 reads, by convention and with no config key naming the location:

1. `AGENTS.md`, the project rules file, as the host documents it. The seed
   relies on no `CLAUDE.md` fallback, and none is verified live.
2. `.opencode/agents/<name>.md`, one agent per file. The file name is the
   agent's id. A frontmatter field the host cannot read voids the whole file
   with no diagnostic: on 2.2.6 a `tools:` list did, which is why every agent
   is rendered in the host's own fields (below).
3. `.opencode/plugins/*.ts`, loaded on its own and run with Bun, with no build
   step.
4. `.opencode/commands/*.md` and `.opencode/skills/<name>/SKILL.md`. The seed
   places both; that OpenCode 2 reads them is not verified live.
5. `opencode.json`, the project config. The seed ships the `.json` form only:
   with both `opencode.json` and `opencode.jsonc` at one tier the winner is
   unspecified, so a project could edit one and have the other apply.

## Seed to host

| Seed source | opencode path |
|---|---|
| `core/AGENTS.md` | `AGENTS.md` (copy by default; `--symlink` opt-in) |
| `agents/*.md` | `.opencode/agents/<callable name>.md`, rendered (below) |
| `skills/*/SKILL.md` | `.opencode/skills/*/SKILL.md` |
| protocols with `command: true` | `.opencode/commands/*.md`, generated |
| `integrations/claude-code/{route,status,bound}-hook.py` | `.opencode/hooks/`, byte-identical |
| `integrations/opencode/cypress-plugin.ts` | `.opencode/plugins/cypress.ts` |
| `integrations/opencode/opencode.json` | `opencode.json` (copied, so the project can edit it) |
| `templates/` | `docs/graph/templates/` (graph nodes) |
| `templates/docs/` | `docs/graph/` (missing leaves added on install) |

> **The projection is taken from the graph, not from the seed.** The rows
> above read `seed → host` for brevity; the real path is
> `seed → docs/graph/{agents,skills}/ → host`, and `install.sh`'s own log
> lines say so. That is why a plant-commissioned expert that a grow run writes
> into `docs/graph/agents/` is projected here too, and why
> `tools/growth-audit.py` reports one that reached the graph but not the host
> as `UNGROWN`. When a newly placed agent becomes spawnable is
> `delegation.harness-registration`
> (`docs/graph/method/delegation-bounds.md`).

## The native agent file

`install.sh opencode` transforms each graph agent into OpenCode 2's own shape
(`render_opencode_agents` in `install.sh`; SPEC-0001, the `OPENCODE_*`
contracts):

- **File name.** The agent's callable name, the graph file name without its
  `<digits>-` prefix: `02-implementer.md` becomes `implementer.md`, and the
  host lists it as `implementer`.
- **Fields.** Only the host's own: `description`, `mode`, `model` where the
  map names one, and `permissions`. `mode` is `subagent`, except the
  orchestrator, which is `primary`: a selectable primary agent that no other
  agent may launch. None of the seed's `tools:` list, `effort`,
  `can_delegate`, `routing_triggers` or graph fields reaches the host, and no
  OpenCode 1 field is written.
- **Permissions.** The rules open with one that denies every action, then
  allow each host action the charter's tools map to in
  [`tool-permissions.json`](tool-permissions.json), the one home of that map,
  with the host's guard on `.env` files restored after `read`. The host applies
  the last matching rule, so the narrow rule wins. A tool name the table does
  not carry stops the render, naming the charter and the tool, with every
  projection as it was.
- **Delegation.** A charter with `Task` gets a rule denying every `subagent`
  launch, then one allow per agent in its `delegates_to:`. A charter without
  `Task` launches nothing. The allowlist is the agent's own host rules, so it
  holds without a brief.
- **Body.** The charter's body, followed by each always-loaded section its
  `always_loads:` names, composed by `tools/agent_compose.py`, the composer
  Claude Code's projection uses: the two bodies are byte-identical. After an
  edit to one of those nodes, `install.sh opencode --recompose-agents` rewrites
  `.opencode/agents/` and `.opencode/skills/` only.
- **Model.** The `model:` line comes from the plant's model map,
  `docs/graph/models.md`, at the agent's class and effort
  ([ADR-0022](../../docs/decisions/adr-0022-the-plant-model-map.md)): `opus`
  reads the authoring row, `sonnet` the investigation row, `haiku` the
  investigation-low row. A cell is a `provider/model` selector and may end in
  `#<variant>` (`provider/model#high`), which the host registers as the
  model's variant; that is how the map expresses an effort on a model that has
  one, and the installer guesses no variant name. Where the map names no model
  (a `-` or placeholder cell, a missing row, `inherit`), the line is left out
  and the agent runs on its caller's model; the installer prints how many. A
  map that breaks its grammar stops the run before any projection is placed.
  After you edit the map, re-run `install.sh opencode`.

On OpenCode 2.2.6, `opencode2 debug agents` lists all 20 seed agents under
their callable names with the mode, the model and variant, and the rules as
rendered, and prints no configuration warning.

## opencode.json

The bundled config carries only keys that are valid on OpenCode 2 and
load-bearing:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "experimental": {
    "subagent_depth": 3
  }
}
```

- **`$schema`** is `https://opencode.ai/config.json`. The `config-schema.json`
  URL returns 404, so an editor pointed at it validates nothing.
- **`experimental.subagent_depth: 3`** is the load-bearing key. The host's
  default depth is 1, at which a subagent launches no subagent of its own, and
  that collapses the seed's delegation topology: the deepest chain is
  `orchestrator` → `multi-agent-architect` → `architect` → leaf. On 2.2.6 the
  key is accepted, three nested launches ran, and a fourth was refused with the
  host's message "Subagent depth limit reached (3)"; the top-level
  `subagent_depth` an earlier seed shipped is reported as an unsupported legacy
  setting and omitted. The value equals the highest `max_spawn_depth` in
  `agents/*.md`, and `tests/seed-lint.py` holds the two together
  ([own-gate row](../../DOCUMENTATION.md#enf-seed-gate),
  [delegation fields](../../DOCUMENTATION.md#enf-delegation-frontmatter)).
- **No `instructions`.** The host accepts the key and loads none of its
  entries, and `AGENTS.md` already reaches the session, so listing the kernel
  would only risk loading it twice.
- **No directory keys.** Agents, commands, skills and plugins are found by
  convention.
- **MCP servers** use the `mcp` key. The seed declares none: a documentation
  MCP is a project choice, and `research-scout` works from plain web fetch.

## The plugin and the hook core

`.opencode/plugins/cypress.ts` is a thin envelope over the three Python hook
cores in `.opencode/hooks/`, the same files Claude Code runs
([ADR-0024](../../docs/decisions/adr-0024-one-hook-core-per-session-residency.md);
SPEC-0003, the `OPENCODE_*` contracts). It composes no text, writes no file and
decides nothing; every decision is the core's.

- **Route.** On each prompt it runs `route-hook.py` and adds the core's text to
  the session as a synthetic message with `resume: false`, ahead of the user's
  prompt, which it leaves unedited. Without `resume: false` a synthetic message
  starts a model call of its own.
- **Status.** On the first prompt this host process sees for a session it
  first runs `status-hook.py` and adds its text the same way.
- **Bounded execution.** On the permission hook, for a shell command, it runs
  `bound-hook.py`. A command the core refuses is denied through the host with
  the core's reason as the message, byte for byte, so the model reads the
  reason and can re-issue the command in bounded form
  (`toolcraft.bounded-execution`). Other actions keep the effect the host
  decided.
- **Child sessions.** The plugin counts the `parentID` links above a session
  and passes that depth; the core gives a child session nothing. When the host
  cannot say what the session is, the depth is left out and the core injects
  in full.
- **Failure.** A missing core, a timeout or an error injects nothing and
  refuses nothing, and each hook is registered in its own guard, so a hook the
  host lacks leaves the others working. `install.sh opencode --check` names a
  missing core or plugin. The kernel's own FIRST MOVE is the route-first floor
  without the plugin.

The plugin imports only the host's bundled `@opencode/plugin` and `node:`
built-ins. On OpenCode 2.2.6 it loaded with no install step and no network;
the route and status texts arrived byte-identical to the cores' text, a child
session got nothing, and a refused shell command was denied with the core's
reason, which the model reported.

Why the injection is a synthetic message: on 2.2.6, editing the prompt text in
the prompt hook has no effect, and a keyed instruction entry reaches the model
in the system section, where a changed value would change the cached prefix. A
synthetic message is appended history and leaves the prefix alone.

## Install

```sh
/path/to/cypress/install.sh opencode
```

The installer places the files in the table above, scaffolds `docs/graph/`,
and prints one line saying the adapter targets OpenCode 2 and runs as
`opencode2`. It and every script it places need Python 3.14 or newer
(SPEC-0005 §5); with none on `PATH` it refuses before writing anything. The
plugin runs the cores on the interpreter the installer found.

### Re-installing over an earlier opencode plant

A plant installed by an earlier seed holds agent files named
`<digits>-<name>.md` with a `tools:` list, which OpenCode 2 drops without a
diagnostic, a top-level `subagent_depth`, and no plugin. Re-running
`install.sh opencode` moves each old agent file to a timestamped backup beside
it, so a plant's edit survives there, writes the native agents, replaces
`opencode.json` with a backup, and places the plugin and the cores. The
installer neither detects nor branches on OpenCode 1. Observed on 2.2.6 over a
plant installed by 8.3.2: the re-install succeeds, the host then lists every
agent with no warning, and `--check` is green.

### `--check`

`install.sh opencode --check` writes nothing and needs no OpenCode 2. It
exits non-zero, naming the file and the remedy, for an agent or skill
projection that differs from what the installer would place (a file in the
earlier numbered shape included, and a model-map edit not yet re-run), an
`opencode.json` in the earlier shape, a missing plugin, and a missing or
unusable hook core.

### Compose-kernel plants

In compose mode (`--kernel-mode compose`, where a team's own `AGENTS.md` stays
canonical and only `CLAUDE.md` carries the seed kernel), the host reads only
`AGENTS.md`, so an opencode session there does not see the seed kernel. This
is an open defect (below).

## Slash commands

Every protocol whose node declares `command: true` becomes one generated file
in `.opencode/commands/`, a short pointer into its
`docs/graph/protocols/<name>.md` node, the single home. The other hosts get
the same roster ([host capability matrix](../../documentation/host-capability-matrix.md#slash-commands)).
The user-sovereign meta-loop protocols (`graft`, `grow`, `harvest`) carry no
`command:` field and are commands on no host. That OpenCode 2 lists the
generated commands is not verified live.

## When both Claude Code and opencode are present

The installer keeps one kernel body for both: `CLAUDE.md` and `AGENTS.md` hold
the same text, one the real file and the other a project-local symlink or an
identical copy, so the two hosts cannot drift. OpenCode 2 reads `AGENTS.md`
(documented), so the seed relies on no `CLAUDE.md` fallback, and outside
compose mode the shared body makes the question moot. The orchestrator is the
default on Claude Code (its output style); on opencode it is a selectable
primary agent (below).

## Differences from Claude Code (defects to close)

The [host capability matrix](../../documentation/host-capability-matrix.md#defects-to-close)
is the one home of each difference, its evidence and what would close it:

1. The lead does not play the orchestrator; it is a selectable primary agent
   (owner decisions D1 and D2).
2. No worker-continuation guard.
3. The seed kernel is absent in a compose-kernel plant.
4. Per-session dedup is not verified live.
5. Effort is not verified to reach the provider.
6. No reset after a compaction.

## Live verification

The gate needs neither OpenCode 2 nor a network. What the adapter holds on a
running release is re-verified by hand with the seed-only procedure
[`opencode-live-verification.md`](../../docs/skills/opencode-live-verification.md);
a matrix cell for opencode rises only on an observation recorded there.
