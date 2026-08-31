# Scout 06 — Settings, Packages, MCP/ACP (prime-agent 0.8.1)

**Date:** 2025-08-28  
**Verified against:** `/home/okik/.local/opt/node-v24/lib/node_modules/prime-agent` (v0.8.1)  
**Primary sources:** `dist/core/settings-manager.{js,d.ts}`, `dist/core/package-manager.js`, `dist/core/resource-loader.js`, `docs/{settings,packages,extensions,acp,mcp-integrations}.md`

---

## A. Settings schema — resources keys, additive vs override, no-double-load guarantee

### Verified resource keys (from `dist/core/settings-manager.d.ts`)

The `Settings` interface (lines ~130–180 in `settings-manager.d.ts`) contains exactly:

```typescript
packages?: PackageSource[];      // npm/git/local packages → all resource types
extensions?: string[];           // explicit extension files/dirs
skills?: string[];               // explicit skill files/dirs
prompts?: string[];              // explicit prompt-template files/dirs
themes?: string[];               // explicit theme files/dirs
enableSkillCommands?: boolean;   // register skills as /skill:name (default: true)
enableBuiltinSkills?: boolean;   // load built-in skills shipped with prime-agent (default: true)
bundledSkills?: BundledSkillsSettings;  // { websearch?: boolean }
```

No `instructions` key. No `kernelInstructions` key. No `subagentDepth`/`subagent_depth` key.

### ADDITIVE, not override

**`extensions`/`skills`/`prompts` are ADDITIVE to convention discovery.**

Source: `dist/core/package-manager.js`:

1. `resolve()` (line 659): calls `resolveLocalEntries()` for explicit settings entries, THEN calls
   `addAutoDiscoveredResources()` for convention dirs.
2. Convention dirs always scanned regardless of whether settings arrays are populated:
   - `.prime/agent/extensions/` (project)
   - `.prime/agent/skills/` (project)
   - `.prime/agent/prompts/` (project)
   - `~/.prime/agent/{extensions,skills,prompts}/` (global)
   - `.agents/skills/` in cwd and ancestor dirs up to git root
3. `addResource()` (line 1856): `if (!map.has(path)) map.set(...)` — first-write wins;
   project-scope resources beat global.

**Semantics of entries in settings arrays:**
- Plain paths (no prefix, no glob): loaded as additional explicit files/dirs
  (`resolveLocalEntries`, line 1726).
- `!pattern`: exclude matching paths from auto-discovered convention-dir resources
  (`isEnabledByOverrides` via `getOverridePatterns`, lines 503–521).
- `+path`: force-include exact path.
- `-path`: force-exclude exact path.
- `*`/`?` glob patterns: include matching files.

**Listing a dir in `skills: [".prime/agent/skills"]` is therefore redundant with convention
discovery** (the dir is already auto-scanned) but harmless — it adds no extra load and doesn't
suppress anything.

### No `instructions` key — no double-load risk

The full `Settings` interface has been read from the compiled type declaration
(`dist/core/settings-manager.d.ts`). There is no `instructions` key, no `kernelInstructions`
key, and no analogue that would inject the kernel a second time.

Prime Agent auto-loads context files (`AGENTS.md` or `CLAUDE.md`) from the cwd and ancestor
directories (`dist/core/resource-loader.js` → `loadProjectContextFiles`, line 31).
There is no settings key to declare them again, so the kernel cannot double-load regardless of
what is written in `.prime/agent/settings.json`.

### No project-scope subagent-depth cap

`rlmMaxDepth` exists in the `Settings` interface, but `getRlmMaxDepth()` reads from
`this.globalSettings` only (`dist/core/settings-manager.js:479–480`):

```js
getRlmMaxDepth() {
    return this.globalSettings.rlmMaxDepth;  // line 480 — global ONLY
}
```

Setting `rlmMaxDepth` in a project `.prime/agent/settings.json` has no effect.
The depth is controlled globally or via `/rlm-max-depth` chat command.
The seed's delegation depth enforcement lives in `agents/*.md` `max_spawn_depth` frontmatter,
which is read by the orchestrator at runtime — this is the correct enforcement layer.

### Recommended minimal settings.json

```json
{
  "extensions": [".prime/agent/extensions"],
  "skills": [".prime/agent/skills"],
  "prompts": [".prime/agent/prompts"]
}
```

These three lines are **redundant with convention discovery** but provide robustness: they
ensure the seed's directories load even under a locked-down or custom `agentDir` config.
Do NOT add an `instructions` key (does not exist).
Do NOT add `rlmMaxDepth` in project scope (silently ignored).

---

## B. Packages mechanism — ship as package vs loose committed files

### What the packages mechanism is

`prime-agent package install npm:@foo/bar` / `git:...` / `./local-path` installs a package
and writes its source to `settings.json`. A package declares resources in `package.json`
under the `pi` key, or uses convention dirs:

```json
{
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"]
  }
}
```

`prime-agent package install ./relative/path` works for local directories; path goes into
settings, no copy. Auto-update: `prime-agent package update` updates non-pinned packages.

### Could CYPRESS ship as a Prime Agent package?

**Yes, technically.** Add `package.json` with a `pi` key pointing to the install targets,
add `"pi-package"` keyword for discoverability. Users then do:

```bash
prime-agent package install git:github.com/org/cypress-seed
```

This would auto-install skills, prompts, extensions into the running agent on first use (or
startup if already in settings), and `package update` would pull new commits.

### Should it? Pros/cons for committed-to-repo integration

| Dimension | Package form | Loose committed files (current plan) |
|-----------|-------------|---------------------------------------|
| Installation UX | Single `prime-agent package install` command | `install.sh prime-agent` (same as all other harnesses) |
| File placement | Managed by prime-agent into `~/.prime/agent/` or `.prime/agent/` | `install.sh` controls exact symlinks/copies in target plant |
| Symlink support | No — package installs copy, not symlink | Yes — `install.sh --symlink` already works |
| Per-harness parity | Package form is prime-agent-specific; other harnesses (claude-code, opencode, codex) each use `install.sh` | Uniform: `install.sh <harness>` for all harnesses |
| Version pinning | `@ref` pins the package; unpinned gets `update` semantics | `install.sh` chooses what to copy/link from local checkout |
| git-committed settings.json | `packages` entry commits a remote URL, not local path | Direct resource files are committed as-is |
| `install.sh` contract | Would need a separate shim or `install.sh` would still be needed for docs/graph scaffold | `install.sh prime-agent` is clean, single surface |
| Double-install risk | Package installs to global/project npm dir; combined with install.sh could load resources twice | No: install.sh manages one tree of files |

**Verdict for committed-to-repo integration:** Use loose committed files + `install.sh prime-agent`.
The package mechanism is best for *distributing* a skill/extension library to arbitrary users
(npm/git pull model). For a seed where the plant already has the seed checked out (or the seed
IS the plant's tooling repo), `install.sh` provides better control: symlinks, per-harness
surgery, docs/graph scaffold, no npm publish step.

The package mechanism could supplement, not replace: a contributed `package.json` with `pi`
metadata would let someone install the seed's prime-agent resources without `install.sh`, but
maintaining that path in parallel adds surface area. Leave it as a future option if ecosystem
pull warrants it.

---

## C. ACP `_meta` / MCP — relevance for first-class support

### ACP `_meta`

From `docs/acp.md`:

```json
{
  "sessionUpdate": "session_info_update",
  "_meta": {
    "ai.primeintellect.prime-agent": {
      "subagents": [{ "id": "sub-1", "sessionName": "reviewer", "status": "running" }]
    }
  }
}
```

- Subagent trees, quality gates, goals, heartbeats, and compaction state are surfaced in `_meta`.
- Standard ACP clients (editors, harnesses) ignore `_meta` and still work.
- Prime Agent-aware clients or CI harnesses can read it for subagent visibility.
- **Relevance for first-class:** if CYPRESS adds an agent-lint CI gate for prime-agent (parity
  with claude-code's `agent-lint.py`), it could drive validation via ACP mode and read gate
  attempts from `_meta` — but this is optional plumbing, not a blocker.

### MCP project-settings gotcha ⚠️

From `docs/mcp-integrations.md`:

> "Project `.prime/agent/settings.json` MCP entries are **ignored for execution**"

Only `~/.prime/agent/settings.json` `mcpServers` entries are actually started/used.
A committed `.prime/agent/settings.json` `mcpServers` block will be read by the settings
parser but will NOT cause any MCP connection. This is by design (security: a repository
cannot start a local process or shadow a user server).

**Implication for CYPRESS:** Do NOT add `mcpServers` to the committed
`integrations/prime-agent/settings.json`. It would be a no-op and confusing. If MCP
integration is ever needed, document it as a user-level config step, not a plant-committed
setting.

ACP mode does allow per-session MCP via `session/new.mcpServers` (not persisted), which is
relevant if running prime-agent in ACP mode from CI.

---

## Summary table

| Question | Answer | Source |
|----------|--------|--------|
| Resource arrays additive or override? | **Additive** — convention dirs always scanned; arrays add explicit paths and can exclude via `!pattern` | `dist/core/package-manager.js:503–521,659–692,1737–1821` |
| `instructions` key exists? | **No** — not in `Settings` interface | `dist/core/settings-manager.d.ts` |
| `subagentDepth` project key? | **No** — `rlmMaxDepth` is global-only | `dist/core/settings-manager.js:479–480` |
| Listing a dir in settings.json | Redundant but harmless; adds robustness under non-default config | `package-manager.js:1776–1788` |
| Ship as prime-agent package? | Not recommended for committed-to-repo integration; `install.sh` is better | `docs/packages.md` + analysis |
| `mcpServers` in project settings.json | Ignored for execution — global-only | `docs/mcp-integrations.md` |
| ACP `_meta` | Subagent/gate visibility; standard clients ignore it safely | `docs/acp.md` |

---

## Gotchas for copy-mode install

1. **Do not put `mcpServers` in committed `.prime/agent/settings.json`** — silently no-op.
2. **`rlmMaxDepth` in project settings is silently ignored** — depth enforcement must come
   from briefs (`max_spawn_depth` frontmatter), not settings.
3. **Convention dirs are always scanned** — putting skills in `.prime/agent/skills/` is
   sufficient; listing them again in `settings.skills` is optional hardening only.
4. **No `instructions` key** — writing one does nothing; context files are auto-discovered
   via AGENTS.md/CLAUDE.md discovery chain, not via settings.
5. **`enableBuiltinSkills: false`** turns off all prime-agent built-in skills globally;
   prefer `bundledSkills.websearch: false` to disable only web search, or `-skillname/SKILL.md`
   to exclude specific built-ins, unless the seed wants to disable all.
6. **Project settings merge with global** (nested objects merge recursively, arrays replace);
   project `skills: [...]` replaces the global `skills` array entirely — not appended.
   This is standard JSON merge per `deepMergeSettings` (`settings-manager.js:9–29`).

---

*Full source inspection log: `dist/core/settings-manager.{js,d.ts}` (all Settings keys),
`dist/core/package-manager.js` (resolve, addAutoDiscoveredResources, isEnabledByOverrides,
getOverridePatterns, addResource), `dist/core/resource-loader.js` (reload flow),
`docs/settings.md`, `docs/packages.md`, `docs/acp.md`, `docs/mcp-integrations.md`,
`docs/extensions.md` (before_agent_start event type).*
