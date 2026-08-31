# Scout 03: prime-agent Skills Loading — Research Findings

**Source**: prime-agent v0.8.1 at `/home/okik/.local/opt/node-v24/lib/node_modules/prime-agent`  
**Key files read**: `dist/core/skills.js`, `dist/core/package-manager.js`, `dist/core/resource-loader.js`,  
`dist/core/settings-manager.js`, `dist/core/agent-session.js`, `dist/core/config.js`,  
`dist/utils/frontmatter.js`, `integrations/prime-agent/README.md`

---

## 1. Discovery Directories and Precedence

### Automatic discovery (no config needed)

prime-agent auto-discovers skills from these directories in priority order:

| Rank | Path | Scope | Source |
|------|------|-------|--------|
| 0 (highest) | CWD + `.prime/agent/skills` listed in `.prime/agent/settings.json` `skills` array | project+settings | `package-manager.js:resourcePrecedenceRank` |
| 1 | CWD + `.prime/agent/skills` (auto-scan) | project+auto | `package-manager.js:~69710` |
| 1 | CWD + `.agents/skills`, then parent dirs up to git root | project+auto | `package-manager.js:collectAncestorAgentsSkillDirs:9045` |
| 2 | `~/.prime/agent/skills` listed in `~/.prime/agent/settings.json` `skills` array | user+settings | `settings-manager.js:getSkillPaths` |
| 3 | `~/.prime/agent/skills` (auto-scan) | user+auto | `package-manager.js:~70377` |
| 3 | `~/.agents/skills` (auto-scan) | user+auto | `package-manager.js:~69117` |
| 4 | Packages (`packages` setting, npm/git) | package | `package-manager.js:resourcePrecedenceRank` |
| 5 (lowest) | `prime-agent/dist/skills/` (bundled) | builtin | `config.js:getBundledSkillsDir` |

`CONFIG_DIR_NAME = ".prime/agent"` (from `config.js:16795`), so project dir is `CWD/.prime/agent/`.

**Collision rule**: Within the same tier, first-seen wins. `loadSkills()` uses a `Map<name, skill>` that never overwrites (`skills.js:~13000+`). Across tiers, precedence ranking sorts before dedup (`package-manager.js:toResolvedPaths`).

### Settings `skills` array

`~/.prime/agent/settings.json` and `CWD/.prime/agent/settings.json` can carry:
```json
{ "skills": ["path/to/dir", "path/to/SKILL.md"] }
```
Each entry may be a directory (recursively scanned) or an absolute `.md` path.  
`~` expansion is supported (`settings-manager.js:getSkillPaths`, `skills.js:normalizePath`).

### `enableBuiltinSkills` flag

Bundled skills load only when `enableBuiltinSkills=true` (default: true, `settings-manager.js:728`).  
The bundled `websearch` skill is OFF by default unless `bundledSkills.websearch=true`.

---

## 2. SKILL.md Discovery Within a Directory

From `skills.js:loadSkillsFromDirInternal` (~line 5500+):

1. Scan directory entries for `SKILL.md`.
2. If found: treat the **directory** as a skill root. Do NOT recurse further. Load `SKILL.md`.
3. If not found: recurse into subdirectories. Also load root-level `.md` files (if `includeRootFiles=true`).

So the canonical structure is: `<skills-dir>/<skill-name>/SKILL.md`.

---

## 3. SKILL.md Frontmatter Schema

### Fields prime-agent reads

From `skills.js:loadSkillFromFile` (~line 9900+):

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | No | string | Falls back to parent directory name if absent |
| `description` | **Yes** | string | Must be non-empty, max 1024 chars. Skill is DROPPED if absent. |
| `disable-model-invocation` | No | boolean | If `true`, skill is excluded from system prompt but can still be invoked via `/skill:name`. Default: false. |

### Validation rules for `name`

From `skills.js:validateName` (~line 3700):
- Must equal the parent directory name (warning if not, but does not drop skill)
- Max 64 characters
- Must match `^[a-z0-9-]+$` (lowercase, digits, hyphens only)
- Must not start or end with `-`
- Must not contain `--`

### Python skill detection

If the skill directory contains `pyproject.toml` AND `src/<import-name>/__init__.py` (where `import-name = name.replace("-", "_")`), prime-agent classifies it as `kind: "python"` and includes `python_import` in the system prompt XML block.

### What prime-agent IGNORES

All CYPRESS graph-node fields are silently ignored by prime-agent:
- `id`, `tier`, `kind`, `origin`, `title`, `owns`, `requires`, `peers`, `load_when`, `artifacts`, `est_tokens`

These fields serve the CYPRESS seed's own `seed-lint.py` and graph system only.

---

## 4. Frontmatter Parsing

From `dist/utils/frontmatter.js`:

```js
// Expects content starting with "---
" and ending at next "
---"
const { parse } = require("yaml");  // npm yaml@2.9.0
```

npm `yaml@2.x` is stricter than Python's yaml in some contexts but more lenient in others.  
**Critical gotcha**: Unquoted colons in string values break YAML if followed by a space.

**Example** — `test-first/SKILL.md` line 7:
```
title: test-first — shape each test: lowest level, contract-named, one outcome
```
The substring `test:` after a space is parsed as a nested mapping key. This causes:  
`ScannerError: Nested mappings are not allowed in compact mappings`  
`loadSkillFromFile` catches this and returns `{ skill: null, diagnostics: [...] }`.  
**Result: the `test-first` skill is silently absent from prime-agent's skill list.**

All other 12 CYPRESS `skills/*/SKILL.md` files parse successfully. Verified by running the npm yaml parser directly.

---

## 5. Do Seed SKILL.md Files Load Unchanged?

**12 of 13 load unchanged.** The one exception is `skills/test-first/SKILL.md`.

Root cause: the `title` frontmatter field contains an unquoted colon that breaks the npm yaml parser.

Fix required: quote the title value:
```yaml
title: 'test-first — shape each test: lowest level, contract-named, one outcome'
```

No other transform is needed. prime-agent ignores the seed-specific graph fields (`id`, `tier`, `kind`, etc.) silently.

---

## 6. `/skill:name` Behavior

From `agent-session.js:_expandSkillCommand` (~line 179667):

1. If user input starts with `/skill:`, prime-agent looks up the skill by name in the loaded skill list.
2. If found: reads the file, strips frontmatter, wraps body in `<skill name="..." location="...">` XML block, and injects it into the conversation.
3. If not found: passes input through unchanged.
4. The `baseDir` is the skill directory (parent of `SKILL.md`), and relative paths in the skill body are resolved against it.

### `enableSkillCommands` flag

- Default: `true` (`settings-manager.js:728`).
- When `true`: `/skill:name` appears in the **autocomplete dropdown** (`interactive-mode.js:905`).
- When `false`: autocomplete hides them. The flag does **NOT** block actual `/skill:` expansion — `_expandSkillCommand` is called unconditionally for non-internal prompts.
- Setting: `~/.prime/agent/settings.json` or `CWD/.prime/agent/settings.json` → `"enableSkillCommands": false`.

### `disableModelInvocation` flag

From `skills.js:loadSkillFromFile`:
- SKILL.md frontmatter: `disable-model-invocation: true`
- Effect: skill is excluded from the `<available_skills>` XML block in the system prompt (`skills.js:formatSkillsForPrompt:~10300`).
- The skill is still reachable via `/skill:name`.
- Use case: skills too verbose to show in every session but useful on demand.

---

## 7. System Prompt Injection

From `dist/core/system-prompt.js`:

Skills are appended as XML only when the model has file access tools:
```xml
<available_skills>
  <skill>
    <name>context-router</name>
    <type>markdown</type>
    <description>...</description>
    <location>/path/to/SKILL.md</location>
  </skill>
  ...
</available_skills>
```
Python skills include `<python_import>import_name</python_import>`.

---

## 8. Installing Seed Skills for prime-agent

The existing `integrations/prime-agent/README.md` specifies the install target:

```
CWD/.prime/agent/skills/<name>/SKILL.md
```

This maps to the "project+auto" discovery tier (rank 1 in the precedence table).

The bundled `integrations/prime-agent/README.md` also recommends listing this path explicitly in `.prime/agent/settings.json`:
```json
{ "skills": [".prime/agent/skills"] }
```
This upgrades discovery to rank 0 (project+settings), ensuring skills survive even if convention discovery is disabled.

---

## 9. Gotchas for Copy-Mode Install

1. **YAML colon gotcha**: Any SKILL.md whose `title` (or other non-`description` field) contains `<word>:<space>` will fail YAML parse and silently drop that skill. The `description` field in CYPRESS skills is already single-quoted, which is safe. The `title` field in `test-first/SKILL.md` is NOT quoted and breaks parsing. **Fix before install.**

2. **Name must match directory**: `validateName` warns (not errors) if `name != parent-dir-name`. Skills still load with the mismatch, but `/skill:name` invocation uses the SKILL.md `name` field, while system-prompt XML uses the same. Inconsistency causes user confusion. All 12 working CYPRESS skills already match.

3. **description is the gate**: A SKILL.md with no `description` returns `null` — silently absent. Every CYPRESS skill has description, so no issue now, but a future null-description will silently vanish.

4. **Collision by name**: If two directories have the same `name`, first-loaded wins. CYPRESS skills all have unique names.

5. **No `.prime/agent` in cwd = no project-scope discovery**: If the project never creates `.prime/agent/`, the project-scope tier is empty. Only user and bundled skills load. The integration README's `settings.json` explicit listing covers this case.

6. **`test-first` YAML fix is the only change needed to ship all 13 skills**: quote the `title` value. No other CYPRESS SKILL.md field needs modification.

---

## Summary Table: CYPRESS SKILL.md Compatibility with prime-agent

| Field | prime-agent reads? | Needed? | Action |
|-------|-------------------|---------|--------|
| `name` | Yes (falls back to dir) | Yes, present | No change |
| `description` | Yes, required | Yes, present | No change |
| `disable-model-invocation` | Yes | Not set (default false) | No change needed |
| `id`, `tier`, `kind`, `origin` | Ignored | N/A (seed-lint only) | No change |
| `title`, `owns`, `load_when`, etc. | Ignored | N/A (seed-lint only) | **Must be valid YAML** ← gotcha |

---

*Report written: scout-03-skills.md*
