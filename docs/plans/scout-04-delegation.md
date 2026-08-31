# Scout-04: Delegation / Roster Model — prime-agent

*Scout session: read-only research. All claims verified against source.*  
*prime-agent v0.8.1 at `/home/okik/.local/opt/node-v24/lib/node_modules/prime-agent`*  
*Written: 2026-08-28*

---

## 1. THE CRUX: Does prime-agent have a static agent-roster directory?

**NO.** Prime Agent has **no static agent-roster directory** that a session
enumerates at startup. There is no equivalent of Claude Code's `.claude/agents/*.md`
enumeration — no directory that the runtime scans to build a registry of
spawnable named agent types.

**Source evidence (dist/):**
- `dist/core/skills.js:6052-6400` — the only directory-scanning code at startup
  is `loadSkillsFromDir()` for SKILL.md files in `~/.prime/agent/skills/`,
  `.prime/agent/skills/`, `~/.agents/skills/`, `.agents/skills/`. No agents/ dir scan.
- `dist/core/resource-loader.js:3631-6100` — `DefaultResourceLoader` has fields:
  `skills`, `prompts`, `themes`, `agentsFiles`. The `agentsFiles` field holds only
  `AGENTS.md` / `CLAUDE.md` context files (plain project instructions), NOT an
  enumerable agent type registry.
- `dist/core/resource-loader.js` `loadContextFileFromDir()` — tries candidates
  `["AGENTS.md", "AGENTS.MD", "CLAUDE.md", "CLAUDE.MD"]` in `agentDir` and ancestor
  dirs. This is context-file loading, not roster loading.
- `grep -r 'readdirSync.*agent\|agents.*enumerate'` over all dist/ JS → zero matches.
- `dist/core/agent-session.js:8420-8422` — the only "spawn child" gate is
  `if (this._rlmDepth >= this._rlmMaxDepth) throw Error(...)`. No "is this agent
  registered?" lookup exists.

---

## 2. Delegation mechanism: `await rlm(brief)` only

Delegation is **entirely a runtime primitive**. When the parent wants a child:

```python
handle = await rlm("Review authentication and reply with findings.", name="auth-reviewer")
```

- `dist/core/agent-session.js:8400-8450` (`runRlmChild`): checks depth, resolves
  model, creates `sub-xxxxxxxx` artifact dir, returns `RLMSpawnHandle` immediately.
- `dist/core/rlm-runtime.js` and `prime-agent-runtime/src/rlm/__init__.py` — the
  Python shim bridges `rlm()` calls via Jupyter comm to the TypeScript host.
- Children are full `AgentSession` instances, not "type-registered" specialists.
  There is no concept of a spawnable named type: every `rlm()` call creates a fresh
  child with whatever system prompt the parent provides in the brief.

**No name-based "spawn by type" API exists.** The `name=` kwarg is just a readable
session label — it does not select a pre-registered persona.

---

## 3. Continual-harness subagent specs

The continual harness (`rlm.harness`) has a `subagent` entry kind
(`prime-agent-runtime/src/rlm/harness.py:HarnessEntry` dataclass). Schema:

```json
{
  "schema": 1,
  "entries": {
    "prompt": {},
    "memory": {},
    "skill": {},
    "subagent": {}
  }
}
```

A subagent spec is a **routing hint / delegation template** that appears in the
system prompt. It tells the model WHEN to spawn a child and HOW to brief it. It
does NOT create a spawnable named type. The agent still spawns via `await rlm(brief)`.

### (a) Best first-class home for the 17-agent roster

Two complementary homes:

1. **Primary: `.prime/agent/agents/*.md` (brief-source files on disk).**
   The orchestrator reads the relevant `agents/<name>.md` file and embeds its
   persona + tool-bound + delegation contract verbatim into the `rlm(brief)` call.
   This is already the design in `integrations/prime-agent/README.md` (D4 decision)
   and mirrors exactly the "role-emulation fallback" path from `delegation.md`
   (`delegation.harness-registration`). **On Prime Agent, this is not a fallback —
   it is the primary and only path, because there is no native roster registration.**

2. **Optional enhancement: continual-harness subagent specs** (`rlm.harness.create_subagent`).
   These appear in the system prompt as persistent context, helping the model know
   when to delegate and to whom. Best created via `/refine` or inline Python after
   install. They augment the brief-source files; they do NOT replace them.

The plain files win on every practical axis: they are committable, diffable, lintable
by the existing `agent-lint.py`, and immediately available to any `rlm()` call without
a session restart or a global harness write.

### (b) Can continual-harness specs be SEEDED from committed repo files at install time?

**No — not natively.** The harness state is stored in one of two places:

- **Global:** `~/.prime/agent/harness/harness_state.json`
  (`dist/core/refinement/refinement.js:getGlobalHarnessStateDir()`)
- **Local (session):** `<session-artifact-dir>/harness/harness_state.json`
  (`dist/core/refinement/refinement.js:getLocalHarnessStateDir()`)

There is no project-scoped harness state path. The settings schema
(`dist/core/settings-manager.d.ts:Settings`) has no harness-related key. The env
vars `RLM_GLOBAL_HARNESS_STATE_DIR` and `RLM_HARNESS_STATE_DIR` are injected by the
TypeScript host (`agent-session.js:7508-7517`) into the kernel, but they point to the
same `~/.prime/agent/harness/` and session-artifact dirs — not to committed files.

**Workaround for install:** `install.sh install_prime_agent` COULD write a seed
`~/.prime/agent/harness/harness_state.json` as a post-install step. However:
- It would overwrite existing global state (destructive if the user already has entries).
- The 17-agent roster is more ergonomically hosted as brief-source `.md` files.
- The plan's §12-OQ1 resolved: "no — session/user-local state, not committable install artifacts".

**Recommendation:** Do NOT seed harness subagent specs at install time. The `.prime/agent/agents/*.md`
brief-source files are the committed, installable, lintable home. Harness specs are 
user/session-local and should be created by the user or agent via `/refine` after first 
growth (if they want the roster in their global context).

---

## 4. Recursion depth bounding

### Default depth

The default `RLM_MAX_DEPTH` is **2** (hard-coded in `agent-session.js:37393-37400`):
```js
return { maxDepth: 2, source: "default" };
```

This means: root (depth 0) can spawn children (depth 1) can spawn grandchildren (depth 2);
grandchildren at depth 2 CANNOT spawn further because `2 >= 2`.

### Priority chain (_resolveRlmMaxDepth, `agent-session.js:36645-37400`)

| Priority | Source | Knob |
|----------|--------|------|
| 1 (highest) | persisted in chat session | `/rlm-max-depth <int>` slash command |
| 2 | config object | `config.rlmMaxDepth` (passed at spawn) — children inherit parent's configured value |
| 3 | global settings | `~/.prime/agent/settings.json` → `"rlmMaxDepth": <int>` |
| 4 | env var | `RLM_MAX_DEPTH=<int>` |
| 5 (lowest) | hard-coded default | 2 |

Sources: `dist/core/settings-manager.d.ts` (Settings interface has `rlmMaxDepth?: number`),
`dist/core/slash-commands.js:5169-5175` (`/rlm-max-depth [<int> [--global]]`).

**Note:** `rlmMaxDepth` is NOT documented in `docs/settings.md` but IS in the TypeScript
type definitions and IS read by `SettingsManager.getRlmMaxDepth()` from settings.json.

### Is there a config knob analogous to opencode's `subagent_depth`?

**YES** — three knobs:
1. `/rlm-max-depth <n>` in chat (immediate, per-session, persisted in transcript).
2. `"rlmMaxDepth": n` in `.prime/agent/settings.json` (project-scoped).
3. `RLM_MAX_DEPTH=n` environment variable.

The seed's orchestrator claims `max_spawn_depth: 3` (deepest legal chain is
orchestrator → coordinator → leaf). The default of 2 allows this (depth 0+1+2).
No change to the prime-agent depth knobs is needed for the seed's topology.

---

## 5. No "installed but not spawnable" trap on prime-agent

On Claude Code and opencode, `agents/*.md` files are enumerated once at session start.
Agents installed mid-session require a session restart to become spawnable by name.
This is the `delegation.harness-registration` trap.

**On prime-agent, this trap does not exist.** Because delegation is always `await rlm(brief)`
with an inline brief (not a name lookup into a session registry), any brief written to
`.prime/agent/agents/<name>.md` during or after install is immediately usable by the very
next `rlm()` call. No session restart needed. The `log_registration_notice` in install.sh
is NOT needed for the prime-agent path.

---

## 6. Concrete recommendation for 17-agent roster as first-class prime-agent

### The mapping (aligned with D4 from prime-agent-integration.md §6)

```
agents/*.md  →  .prime/agent/agents/*.md   (brief sources, copied or symlinked by install.sh)
```

The orchestrator uses them like this:
```python
# Read the brief source for the specialist needed
brief_src = Path("docs/graph/agents/01-architect.md").read_text()
# Spawn with the brief embedded
handle = await rlm(
    f"You are the architect. {brief_src}\n\n<TASK>Design the auth boundary for...",
    name="architect",
    model="anthropic/claude-opus-4-5",  # per model: opus in frontmatter
)
```

### What install.sh prime-agent should place

```
.prime/agent/agents/*.md                   ← agents/*.md (brief sources)
.prime/agent/skills/<n>/SKILL.md           ← skills/<n>/SKILL.md
.prime/agent/prompts/<cmd>.md              ← generate_slash_commands output
.prime/agent/extensions/route-extension.ts ← fail-open enforcement
.prime/agent/settings.json                 ← minimal, pins resource dirs
AGENTS.md                                  ← core/AGENTS.md (kernel)
docs/graph/                                ← place_docs_skeleton
```

### What NOT to do

- Do NOT write a harness subagent spec for each of the 17 agents at install time —
  that's user/session-local state and would overwrite existing global harness entries.
- Do NOT create a fake "registration" layer or `agents.json` manifest — prime-agent
  has no such concept and the runtime needs none.
- Do NOT add `log_registration_notice` to the prime-agent install path — there is no
  registration lag.

### CI gate parity with Claude Code (`agent-lint.py`)

The plan (§16, "INC2.5") correctly identifies that `agent-lint.py --lint` and
`--eval` can be pointed at `.prime/agent/agents/*.md` directly (same frontmatter
format). The linter's `dir` assumption is the only thing to verify:
`agent-lint.py` globs `*.md` from a given dir; pass `.prime/agent/agents/` and it
lints the prime-agent brief sources with no changes to the linter itself.

---

## 7. Gotchas for a copy-mode install

1. **No name-based dispatch.** `await rlm("I need an architect")` does NOT look up
   `.prime/agent/agents/01-architect.md` automatically. The orchestrator must
   read the file and embed the persona. The AGENTS.md kernel + delegation.md
   guidance must make this explicit for prime-agent sessions.

2. **rlmMaxDepth default = 2 allows depth 0→1→2 (3 levels).** The seed's deepest
   legal chain is also 3 levels (orchestrator → coordinator → leaf). They match.
   But if a project wants `orchestrator → architect → leaf`, architect must be able
   to spawn (depth 2, which is AT the max). This works because depth 2 == max, but
   grandchildren at depth 2 CANNOT spawn (would need depth 3). Verify before
   running deep multi-coordinator topologies.

3. **No project-scoped harness state.** Global harness writes (`rlm.harness.create_subagent(global_=True)`)
   go to `~/.prime/agent/harness/harness_state.json` (shared across ALL projects).
   Local writes are session-scoped and ephemeral. There is no
   `.prime/agent/harness/harness_state.json` project file.

4. **harness seeding at install time would pollute global state** shared across
   all prime-agent projects on the machine. Do not write harness entries from install.sh.

5. **The `.prime/agent/agents/` directory has NO runtime meaning to prime-agent.**
   Prime Agent ignores it (no dir scan of agents/ happens). It is purely a
   brief-source convention for the orchestrator to read. This is both a feature
   (no registration lag) and a constraint (the orchestrator must be taught to
   read and embed briefs manually).

6. **settings.json `rlmMaxDepth` key is in the type definition but undocumented**
   in `docs/settings.md`. It works, but users won't find it in the docs. The
   `/rlm-max-depth` slash command is the documented runtime override.

---

## 8. File references (exact)

| Claim | Source file:line |
|-------|-----------------|
| No agents/ dir scan at startup | `dist/core/resource-loader.js:1284-1820` (only AGENTS.md/CLAUDE.md) |
| loadSkillsFromDir = only skills scanning | `dist/core/skills.js:6052-6400` |
| Default RLM_MAX_DEPTH = 2 | `dist/core/agent-session.js:37393-37400` |
| Priority chain for depth | `dist/core/agent-session.js:36645-37400` |
| /rlm-max-depth slash command | `dist/core/slash-commands.js:5169-5175` |
| rlmMaxDepth in settings type | `dist/core/settings-manager.d.ts:Settings` |
| Harness state schema (4 kinds) | `dist/core/refinement/refinement.d.ts:HarnessState` |
| Global harness at ~/.prime/agent/harness/ | `dist/core/refinement/refinement.js:8730` |
| No project harness path | `dist/core/settings-manager.d.ts` (no harness key in Settings) |
| RLM env vars injected to kernel | `dist/core/agent-session.js:7508-7517` |
| Depth check in runRlmChild | `dist/core/agent-session.js:8420-8422` |
| HarnessEntry Python schema | `prime-agent-runtime/src/rlm/harness.py:HarnessEntry` |
| Subagent spec CRUD API | `prime-agent-runtime/src/rlm/harness.py:create_subagent` |

---

*Full report: `/home/okik/cypress-6.6.0/cypress/docs/plans/scout-04-delegation.md`*
