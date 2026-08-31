# Prime Agent integration

[Prime Agent](https://app.primeintellect.ai) is an RLM-native coding and
research harness built around a persistent IPython kernel, recursive
subagents (`rlm()`), durable sessions, and a continual-harness state
ledger. This adapter makes the seed a first-class Prime Agent citizen.

Prime Agent discovers resources by convention (verified against
prime-agent 0.8.1 `README.md` + `docs/`):

1. **Context files (the kernel)** — `AGENTS.md` **or** `CLAUDE.md`,
   auto-loaded from `~/.prime/agent/`, every parent directory of the
   cwd, and the cwd itself. All matches are concatenated. The kernel
   goes here.
2. **Prompt templates (slash commands)** — `.prime/agent/prompts/<name>.md`,
   invoked as `/<name>`. Frontmatter carries `description`. The protocols
   go here.
3. **Skills** — `.prime/agent/skills/<name>/SKILL.md`, auto-discovered
   and also invokable as `/skill:<name>`. Same Agent-Skills `SKILL.md`
   shape the seed already ships, so no transform is needed.
4. **Extensions** — `.prime/agent/extensions/*.ts`, TypeScript modules
   that subscribe to lifecycle events. The progressive-discovery
   enforcement lives here.
5. **Settings** — `.prime/agent/settings.json` (project scope), which
   overrides `~/.prime/agent/settings.json` (global).

This seed system maps to Prime Agent as follows:

| Seed file                    | Prime Agent path                                   |
|------------------------------|----------------------------------------------------|
| `core/AGENTS.md`             | `AGENTS.md` (symlink or copy at repo root)         |
| `agents/*.md`                | `.prime/agent/agents/*.md` (brief sources — see below) |
| `skills/*/SKILL.md`          | `.prime/agent/skills/*/SKILL.md`                   |
| protocols → slash commands   | `.prime/agent/prompts/*.md` (generated projections) |
| route enforcement            | `.prime/agent/extensions/route-extension.ts`       |
| `templates/`                 | `templates/` (kept at repo root, untouched)        |
| `templates/docs/` (graph leaves) | `docs/graph/` (missing leaves added on install) |

## Delegation: no static roster, so no registration lag

This is the one place Prime Agent differs sharply from Claude Code and
opencode, and the difference is in the seed's favour.

Prime Agent has **no static agent-roster directory that a session
enumerates at start**. Delegation is a runtime primitive: the
orchestrator spawns a clean-context child with an inline brief via
`await rlm("<brief>")`, and reusable delegation specs are persisted in
the **continual harness** (`rlm.harness`), not as spawnable-by-name
registry files.

Two consequences:

- The seed's `agents/*.md` are installed to `.prime/agent/agents/*.md`
  as **brief sources**. The orchestrator reads the relevant roster file
  and passes its persona + tool bound + delegation contract into the
  `rlm()` call — exactly the brief-enforced role emulation that
  `docs/graph/method/delegation.md` (`delegation.harness-registration`)
  already prescribes for any harness whose native registration cannot
  carry the seed's model class or tool bound.
- Because there is no session-start enumeration, the **"installed but
  not spawnable" trap does not exist on Prime Agent**. A roster brief
  written to disk — by an install, a graft, or a freshly commissioned
  expert — is usable by the very next `rlm()` call in the same session;
  no restart is required. The recorded fallback in
  `delegation.harness-registration` is therefore the *normal* path here,
  never a workaround.

If you want the roster reachable as reusable specs across sessions,
persist the briefs as continual-harness subagent specifications
(`rlm.harness.create_subagent(...)` / `refine`). That is a project
choice; the committed single home stays `.prime/agent/agents/*.md`.

## Slash commands

Every protocol whose node declares `command: true` in its frontmatter is
exposed as a slash command; `install.sh` **generates** one prompt-template
file per such node into `.prime/agent/prompts/` — the same roster as every
other harness, since all draw from the same `command:` field. Each is a
short pointer into the corresponding `docs/graph/protocols/<name>.md`
node (the single home). The user-sovereign meta-loop protocols (`graft`,
`grow`, `harvest`) and the canonize-folded `toolcraft` carry no `command:`
field and are commands on no harness.

## Progressive-discovery enforcement (extension)

Progressive discovery — open the graph router, load only the nodes a task
needs, declare what you skipped, then classify the tier — is guidance a
capable model follows and a weaker one skips. Prime Agent lets you enforce
it deterministically the same way Claude Code does, through its extension
event bus:

- `route-extension.ts` subscribes to **`before_agent_start`** (fired
  after the user submits a prompt, before the agent loop; it can inject
  a message and modify the system prompt). It runs the graph router
  (`python3 docs/graph/graph-lint.py --plan "<prompt>"`) on the actual
  prompt and injects the route-first mandate plus the router's suggested
  node set — the same behaviour as the cross-tool `route-hook.py`, using
  Prime Agent's native extension API instead of a shell hook.
- It is **fail-open**: any error (missing graph, router failure) degrades
  to the bare mandate or to silence, and it never blocks a prompt.
- It is auto-discovered from `.prime/agent/extensions/`. The bundled
  `settings.json` also lists it explicitly so it still loads if a project
  disables convention discovery.

The kernel this seed installs also leads with a blunt, tool-free
"FIRST MOVE" mandate, so even with the extension disabled the route-first
instruction is the first thing the model reads.

## Native execution — using Prime Agent's edge over Claude Code

Prime Agent is RLM-native, with primitives Claude Code does not have: recursive
`rlm()` subagents you spawn and fan out from the IPython kernel, a persistent
kernel that *is* your tool, a **continual harness** (`refine`, memories,
reusable subagent specs) for cross-session memory, `agent_message` /
`agent_observe` for coordinating children, and goals / heartbeats for
long-running work. A first-class integration should exploit these, not run the
seed as "Claude Code with different paths."

That guidance ships as **`.prime/agent/APPEND_SYSTEM.md`** — a native-execution
overlay the installer drops in. Prime Agent **appends it to the system prompt on
every session**, and Claude Code never reads it (it is not `CLAUDE.md`/`AGENTS.md`
and lives under `.prime/agent/`). It does not replace or contradict the shared
kernel; it maps the kernel's discipline onto Prime Agent's primitives:

- **Delegation** → read a `.prime/agent/agents/<role>.md` brief and spawn
  `await rlm(brief + task, name=role, model=...)`; fan out MULTIPLE
  single-scoped children in parallel (never one broad worker); collect handbacks
  via `agent_message`; supervise with `agent_observe`.
- **Model policy** → Sonnet-class (floor `claude-sonnet-4-6`) for read-only
  scouting, Opus-class for authoring — straight from each roster brief's
  `model:` field.
- **Gates** → run `bash tests/run.sh` and the linters directly in the kernel;
  keep evidence in variables.
- **Close-out** → canonize into `docs/graph/` **and** persist reusable operating
  lessons with the continual harness (`refine.run(...)`) — the cross-session
  memory Claude Code lacks.
- **Long-running work** → a nonblocking control loop with `goal` and
  `rlm_heartbeat`; end the turn and fan-in on replies instead of polling.

Because it is a plain `APPEND_SYSTEM.md`, a project can edit it, and a global
`~/.prime/agent/APPEND_SYSTEM.md` is superseded inside this plant (project wins).

## settings.json

The bundled config only lists the seed's own resource directories, with
**bare relative names**:

```json
{
  "extensions": ["extensions"],
  "skills": ["skills"],
  "prompts": ["prompts"]
}
```

- **Paths are relative to `.prime/agent/`, not the repo root.** Prime Agent
  resolves resource entries in `.prime/agent/settings.json` against that
  file's own directory (`resolve(cwd/.prime/agent, entry)`), so `"prompts"`
  means `.prime/agent/prompts`. Writing `".prime/agent/prompts"` here would
  wrongly nest to `.prime/agent/.prime/agent/prompts` — do not do it.
- **Redundant with convention discovery.** Prime Agent already auto-scans
  `.prime/agent/{extensions,skills,prompts}/`. The arrays are listed only so
  the seed's directories still load under a locked-down or non-default
  config; deduplication means nothing loads twice.
- **No `instructions` / context-file key** — Prime Agent auto-loads the
  project `AGENTS.md` (the kernel) through a separate context-file walk, so
  there is nothing to re-declare and no way to double-load it from here.

### Recursion depth — a global/session/env dial, never committed

Prime Agent bounds recursion with `RLM_MAX_DEPTH` (**default 2**). Unlike
opencode's committable `subagent_depth`, this is **not** settable from a
project `.prime/agent/settings.json` — `getRlmMaxDepth()` reads *global*
settings only, so a committed value is silently ignored. The seed's deepest
legal delegation chain reaches `max_spawn_depth: 3` (orchestrator →
multi-agent-architect → architect → leaf), which needs a depth of 3.

Default depth-2 work (the common T2/T3 path) runs unchanged. To exercise the
seed's **deepest** multi-coordinator topology on Prime Agent, raise the limit
by ONE of:

- `/rlm-max-depth 3` — per session, persisted in the session branch;
- `~/.prime/agent/settings.json` → `{ "rlmMaxDepth": 3 }` — global, all
  projects;
- `RLM_MAX_DEPTH=3` — environment, for a non-interactive/CI run.

The seed's per-role depth bounds themselves stay brief-enforced
(`agents/*.md` `max_spawn_depth`), read straight from the roster brief the
orchestrator spawns — the runtime limit is only the outer ceiling.

## Install

```sh
/path/to/cypress/install.sh prime-agent
```

Creates (symlinks by default under `--symlink`, copies otherwise):
- `AGENTS.md` → `core/AGENTS.md` (bootstrap kernel, auto-loaded)
- `.prime/agent/agents/*.md` → `agents/*.md` (roster brief sources)
- `.prime/agent/skills/<name>/SKILL.md` → `skills/<name>/SKILL.md`
- `.prime/agent/prompts/*.md` → generated, one per protocol node with
  `command: true`
- `.prime/agent/extensions/route-extension.ts` → copied (progressive-
  discovery enforcement)
- `.prime/agent/settings.json` → copied (so the project can edit it)
- `.prime/agent/APPEND_SYSTEM.md` → copied (RLM-native execution overlay,
  appended to the system prompt every session)
- `docs/graph/` → scaffold + missing leaves from `templates/docs/`

## Interchangeable with Claude Code in one plant

Claude Code and Prime Agent are the two first-class citizens, and a single
plant is meant to run **either one, interchangeably**, off the same project
knowledge. Install both — in one command or in two, in any order:

```sh
/path/to/cypress/install.sh claude-code prime-agent
```

What you get in that plant:

- **One shared kernel, no drift.** Claude Code reads `CLAUDE.md`; Prime Agent
  reads `AGENTS.md` (it wins over `CLAUDE.md` in a directory). The installer
  collapses the two to a **single source of truth**: the first placed is the
  real file, the second a project-local relative symlink to it (`AGENTS.md ->
  CLAUDE.md` or the reverse, depending on order). Editing the kernel updates
  both harnesses at once. On a platform without symlinks the second file
  degrades to an independent copy (identical at install; keep them in sync by
  hand). `tests/test-full-install.sh` gates this coexistence in both orders.
- **Parallel harness trees, no collision.** `.claude/{agents,skills,commands}`
  and `.prime/agent/{agents,skills,prompts,extensions}` sit side by side; each
  harness reads only its own. The roster, skills, and command set are the same
  because both are projections of the same `docs/graph/` nodes.
- **One shared knowledge graph.** `docs/graph/` is installed once and read by
  both — the single home for all project knowledge.
- **Enforcement per session type.** A Claude Code session fires
  `.claude/route-hook.py` (UserPromptSubmit); a Prime Agent session fires
  `.prime/agent/extensions/route-extension.ts` (`before_agent_start`). They run
  in different session types, so there is no double-firing.

Switching harness is just opening the plant in the other tool — nothing to
re-install, nothing to reconcile.
