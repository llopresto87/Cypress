# Prime Agent integration

[Prime Agent](https://app.primeintellect.ai) is an RLM-native coding and
research harness built around a persistent IPython kernel (a live Python
process, not the seed's kernel file), recursive subagents (`rlm.spawn()`), durable
sessions, and a continual-harness state ledger. This adapter makes the seed a
first-class Prime Agent citizen, and this page says where each seed file lands.

Prime Agent discovers resources by convention (verified against
prime-agent 0.8.1 `README.md` + `docs/`; the `rlm.spawn` API against the
0.9.7 runtime):

1. **Context files (the kernel)**: `AGENTS.md` **or** `CLAUDE.md`,
   auto-loaded from `~/.prime/agent/`, every parent directory of the
   cwd, and the cwd itself. All matches are concatenated. The kernel
   goes here.
2. **Prompt templates (slash commands)**: `.prime/agent/prompts/<name>.md`,
   invoked as `/<name>`. Frontmatter carries `description`. The protocols
   go here.
3. **Skills**: `.prime/agent/skills/<name>/SKILL.md`, auto-discovered
   and also invokable as `/skill:<name>`. Same Agent-Skills `SKILL.md`
   shape the seed already ships, so no transform is needed.
4. **Extensions**: `.prime/agent/extensions/*.ts`, TypeScript modules
   that subscribe to lifecycle events. The routing pointer that prompts
   progressive discovery lives here ([routing pointer](../../DOCUMENTATION.md#enf-route-hook)).
5. **Settings**: `.prime/agent/settings.json` (project scope), which
   overrides `~/.prime/agent/settings.json` (global).

This seed system maps to Prime Agent as follows:

| Seed file                    | Prime Agent path                                   |
|------------------------------|----------------------------------------------------|
| `core/AGENTS.md`             | `AGENTS.md` (copy by default; `--symlink` opt-in)  |
| `agents/*.md`                | `.prime/agent/agents/*.md` (brief sources — see below) |
| `skills/*/SKILL.md`          | `.prime/agent/skills/*/SKILL.md`                   |
| protocols → slash commands   | `.prime/agent/prompts/*.md` (generated projections) |
| routing pointer              | `.prime/agent/extensions/route-extension.ts`       |
| status register and code anchor (once per session start) | `.prime/agent/extensions/status-extension.ts` |
| `integrations/claude-code/{route,status}-hook.py` | `.prime/agent/hooks/` (the core both extensions run) |
| `templates/`                 | `docs/graph/templates/` (graph nodes)        |
| `templates/docs/` (graph leaves) | `docs/graph/` (missing leaves added on install) |

## Delegation: no static roster, so no registration lag

This is the one place Prime Agent differs sharply from Claude Code and
opencode, and the difference is in the seed's favour.

Prime Agent has **no static agent-roster directory that a session
enumerates at start**. Delegation is a runtime primitive: the
orchestrator spawns a clean-context child with an inline brief via
`await rlm.spawn("<brief>", name="<role>")`, and reusable delegation specs are persisted in
the **continual harness** (`rlm.harness`), not as spawnable-by-name
registry files.

Two consequences:

- The seed's `agents/*.md` are installed to `.prime/agent/agents/*.md`
  as **brief sources**. The orchestrator reads the relevant roster file
  and passes its persona + tool bound + delegation contract into the
  `rlm.spawn()` call — exactly the brief-carried role emulation that
  `docs/graph/method/delegation-bounds.md` (`delegation.harness-registration`)
  already prescribes for any harness whose native registration does not
  carry the seed's model class or tool bound.
- Because there is no session-start enumeration, the **"installed but
  not spawnable" trap does not exist on Prime Agent**. A roster brief
  written to disk — by an install, a graft, or a freshly commissioned
  expert — is usable by the very next `rlm.spawn()` call in the same session;
  no restart is needed. The recorded fallback in
  `delegation.harness-registration` is therefore the *normal* path here,
  not a workaround.

If you want the roster reachable as reusable specs across sessions,
persist the briefs as continual-harness subagent specifications
(`rlm.harness.create_subagent(...)`). That is a project
choice; the committed single home stays `.prime/agent/agents/*.md`.

## Slash commands

Every protocol whose node declares `command: true` in its frontmatter is
exposed as a slash command; `install.sh` **generates** one prompt-template
file per such node into `.prime/agent/prompts/`. Each is a short pointer
into the corresponding `docs/graph/protocols/<name>.md` node (the single
home). How the other hosts get the same roster is in the
[host capability matrix](../../documentation/host-capability-matrix.md#slash-commands). The user-sovereign meta-loop protocols (`graft`,
`grow`, `harvest`) carry no `command:`
field and are commands on no harness.

## Progressive-discovery pointer (extension)

Progressive discovery (route the task, load only the nodes it needs,
declare what you skipped, then classify the tier) is guidance a capable
model follows and a weaker one skips. Prime Agent adds the route to every
prompt through its extension event bus, with the same hook core Claude Code
runs. Like the hook, it adds text and holds nothing
([routing pointer](../../DOCUMENTATION.md#enf-route-hook)):

- `route-extension.ts` subscribes to **`before_agent_start`** (fired
  after the user submits a prompt, before the agent loop). It runs
  `.prime/agent/hooks/route-hook.py`, a byte-identical copy of Claude
  Code's route hook, with the prompt, the session id and the session depth
  as argv values, and injects the text the core returns. It composes no
  text of its own.
- The core keeps one ledger per session under `.cypress/session/`. The
  first routed prompt gets the pointer line and the router's suggestion,
  each node id beside its file. A later prompt names a node this session
  was already shown by id on one `seen:` line and gives full lines only for
  what is new. A full injection returns after each reset, every
  `REFRESH_EVERY` routed prompts, and on any doubt about the ledger
  (SPEC-0003, ADR-0024).
- A child session (`rlmDepth` above 0) and a turn a person did not type,
  such as a delivered agent message or a harness digest, are not routed.
- `status-extension.ts` runs `.prime/agent/hooks/status-hook.py` on
  `session_start`, `session_compact`, `session_tree` and `refine_complete`.
  The core resets the ledger and returns the status register summary and
  the code-anchor line, which the extension injects on the next prompt of
  that session, once. A child session gets nothing.
- Both are **fail-open**: a missing core, a timeout or any error injects
  nothing, so the prompt always goes through. The core waits up to 15 s for
  the router.
- Both are auto-discovered from `.prime/agent/extensions/`. The bundled
  `settings.json` also lists the directory explicitly so they still load if
  a project disables convention discovery.

The kernel this seed installs also leads with its "FIRST MOVE", so even
with the extensions disabled the route-first instruction is the first thing
the model reads. The model then runs
`python3 docs/graph/graph-lint.py --plan "<task>"` itself.

## Native execution — using Prime Agent's edge over Claude Code

Prime Agent is RLM-native, with primitives Claude Code does not have: recursive
`rlm.spawn()` subagents you spawn and fan out from the IPython kernel, a
persistent kernel that *is* your tool, `agent_message` / `agent_observe` for
coordinating children, and goals / heartbeats for long-running work. It also
has a **continual harness** (`rlm.harness`: memories, prompt notes, skills,
reusable subagent specs), though operating lessons still go to the plant's
session record (see Close-out). A first-class integration uses these
primitives directly.

That guidance ships as **`.prime/agent/APPEND_SYSTEM.md`** — a native-execution
overlay the installer drops in. Prime Agent **appends it to the system prompt on
every session**, and Claude Code does not read it (it is not `CLAUDE.md`/`AGENTS.md`
and lives under `.prime/agent/`). It does not replace or contradict the shared
kernel; it maps the kernel's discipline onto Prime Agent's primitives:

- **Delegation** → read a `.prime/agent/agents/<role>.md` brief and spawn
  `await rlm.spawn(brief + task, name=role, model=..., thinking=...)`; fan out
  several single-scoped children in parallel, one facet each; collect
  handbacks via `agent_message`; supervise with `agent_observe`.
- **Model policy** → each roster brief's `model:` field names the class, and
  the plant's model map (`docs/graph/models.md`) names the model and provider
  for that class and effort, from any provider the Prime Agent catalog
  carries. The overlay resolves it per spawn with `rlm.find_models(...)` and
  passes the effort as `thinking=`.
- **Checks** → run `bash tests/run.sh` and the linters directly in the kernel;
  keep evidence in variables.
- **Close-out** → three destinations: project knowledge into `docs/graph/`
  via canonize; any reusable tool or project skill **in the plant**, committed
  (home `docs/graph/skills/<name>.md`, projected to
  `.prime/agent/skills/<name>/SKILL.md`, per `skill.toolcraft`); and
  *operating* lessons to the plant's session record in
  `docs/graph/plans/sessions/` (`method.stewardship-posture`). The overlay's
  Close-out section holds the routing, including what the continual harness
  (`rlm.harness`) may keep.
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
  wrongly nest to `.prime/agent/.prime/agent/prompts`.
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
by one of:

- `/rlm-max-depth 3` — per session, persisted in the session branch;
- `~/.prime/agent/settings.json` → `{ "rlmMaxDepth": 3 }` — global, all
  projects;
- `RLM_MAX_DEPTH=3` — environment, for a non-interactive/CI run.

The seed's per-role depth bounds themselves stay carried by the brief
(`agents/*.md` `max_spawn_depth`), read straight from the roster brief the
orchestrator spawns — the runtime limit is only the outer ceiling
([delegation fields](../../DOCUMENTATION.md#enf-delegation-frontmatter)).

## Install

```sh
/path/to/cypress/install.sh prime-agent
```

Creates (copies by default; `--symlink` opts into live seed links):
- `AGENTS.md` → `core/AGENTS.md` (bootstrap kernel, auto-loaded)
- `.prime/agent/agents/*.md` → `agents/*.md` (roster brief sources)
- `.prime/agent/skills/<name>/SKILL.md` → `skills/<name>/SKILL.md`
- `.prime/agent/prompts/*.md` → generated, one per protocol node with
  `command: true`
- `.prime/agent/hooks/route-hook.py`, `.prime/agent/hooks/status-hook.py` →
  copied from `integrations/claude-code/` (the hook core both extensions run)
- `.prime/agent/extensions/status-extension.ts` → copied (after each
  session start, compaction, tree switch or refine, injects
  `status-register.py --summary` and the line `docs/graph/code-anchor.py
  --compare` prints, or the not-checked line when the comparison did not
  run within 5 s)
- `.prime/agent/extensions/route-extension.ts` → copied (the route on each
  prompt)
- `.prime/agent/settings.json` → copied (so the project can edit it)
- `.prime/agent/APPEND_SYSTEM.md` → copied (RLM-native execution overlay,
  appended to the system prompt every session)
- `docs/graph/` → scaffold + missing leaves from `templates/docs/`

### CI parity

Check the roster in the plant's CI the same way as on Claude Code
([agent-lint row](../../DOCUMENTATION.md#enf-agent-lint)):

```sh
python3 docs/graph/agent-lint.py --lint --eval --dir .prime/agent/agents
```

`--lint` validates the routing/delegation frontmatter; `--eval` runs the
golden routing set against it. A roster edit that breaks either fails the
build.

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
  hand). `tests/test-full-install.sh` checks this coexistence in both orders,
  in the seed's own test run ([own-gate row](../../DOCUMENTATION.md#enf-seed-gate)).
- **Parallel harness trees, no collision.** `.claude/{agents,skills,commands}`
  and `.prime/agent/{agents,skills,prompts,extensions}` sit side by side; each
  harness reads only its own. The roster, skills, and command set are the same
  because both are projections of the same `docs/graph/` nodes.
- **One shared knowledge graph.** `docs/graph/` is installed once and read by
  both — the single home for all project knowledge.
- **One routing pointer per session type.** A Claude Code session fires
  `.claude/route-hook.py` (UserPromptSubmit); a Prime Agent session fires
  `.prime/agent/extensions/route-extension.ts` (`before_agent_start`), which
  runs its own copy of the same script. They run in different session types,
  so there is no double-firing.

Switching harness is just opening the plant in the other tool — nothing to
re-install, nothing to reconcile.
