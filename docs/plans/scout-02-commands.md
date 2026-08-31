# Scout-02: Prime Agent Prompt Templates (Slash Commands)

**Scope:** How `prime-agent` discovers, loads, and expands prompt templates,
and whether the seed's `generate_slash_commands` output works with zero transform.

**Verified against:** `prime-agent@0.8.1` at
`/home/okik/.local/opt/node-v24/lib/node_modules/prime-agent/dist/`

---

## 1. Discovery Paths

Paths searched in order (first-seen-by-name wins on collision):

| Priority | Path | Source key |
|----------|------|-----------|
| 1 | `<cwd>/.prime/agent/prompts/*.md` | project auto-scan |
| 2 | `~/.prime/agent/prompts/*.md` | global auto-scan |
| 3 | Explicit paths from project `settings.json` `prompts` array | project settings |
| 4 | Explicit paths from `~/.prime/agent/settings.json` `prompts` array | global settings |
| 5 | CLI flag `--prompt-template <path>` (repeatable) | cli |

Sources: `dist/core/package-manager.js` (auto-scan at `collectAutoPromptEntries`);
`dist/core/settings-manager.js` (`getPromptTemplatePaths`);
`dist/cli/args.js` (`--prompt-template`).

**`CONFIG_DIR_NAME`** resolves to `.prime/agent` because
`package.json` sets `piConfig.configDir = ".prime/agent"`.
Source: `dist/config.js` line: `CONFIG_DIR_NAME = pkg.piConfig?.configDir || ".prime/agent"`.

**`agentDir`** defaults to `~/.prime/agent` (via `getAgentDir()`) unless
`PI_CODING_AGENT_DIR` env var overrides it.
Source: `dist/config.js` (`getAgentDir`, `ENV_AGENT_DIR`).

**Discovery is non-recursive.** Only direct `*.md` files in the prompts directory are loaded.
Subdirectories are ignored. Symlinks to files are followed; broken symlinks are skipped.
Source: `dist/core/prompt-templates.js` (`loadTemplatesFromDir`).

**Settings `prompts` array** accepts file paths or directory paths.
Paths in `~/.prime/agent/settings.json` resolve relative to `~/.prime/agent/`.
Paths in `.prime/agent/settings.json` resolve relative to `.prime/agent/`.
`~` and absolute paths are also accepted.
Source: `dist/core/settings-manager.js` (`getPromptTemplatePaths`);
`dist/core/resource-loader.js` (`updatePromptsFromPaths`).

---

## 2. File Format and Frontmatter Schema

```markdown
---
description: Short one-line description shown in autocomplete
argument-hint: "<required-arg> [optional-arg]"
---

Body text. $1, $2, $@ / $ARGUMENTS, ${@:N}, ${@:N:L} are substituted with
the arguments the user types after /name.
```

**Name** = `basename(filename, '.md')`. File `specify.md` → command `/specify`.
Source: `dist/core/prompt-templates.js` (`loadTemplateFromFile`).

**`description`** (string, optional):
- If absent or empty, the first non-empty line of the body (truncated to 60 chars) is used.
Source: `dist/core/prompt-templates.js` (`loadTemplateFromFile`).

**`argument-hint`** (string, optional):
- Shown before description in autocomplete dropdown.
- Conventional: `<angle>` = required, `[square]` = optional.
Source: `dist/core/prompt-templates.js` (`loadTemplateFromFile`, `PromptTemplate` interface);
`dist/core/prompt-templates.d.ts`.

**No other frontmatter fields are consumed by the template loader.**
Any extra YAML keys (e.g., the seed's node fields: `id`, `kind`, `origin`, `owns`, etc.)
are silently ignored.
Source: `dist/core/prompt-templates.js` (`parseFrontmatter` via `dist/utils/frontmatter.js`).

**Frontmatter parsing:** YAML block between leading `---` and first subsequent `\n---`.
`yaml.parse()` via the `yaml` package. The body is everything after the closing `---`,
trimmed of leading/trailing whitespace.
Source: `dist/utils/frontmatter.js`.

---

## 3. Name Resolution: How `/name` Maps to a File

1. User types `/specify` in the editor.
2. `parseSlashCommand("/specify")` → `{ name: "specify", args: "" }`.
   Source: `dist/core/slash-commands.js`.
3. `expandPromptTemplate("/specify", templates)` is called.
4. `templates.find(t => t.name === "specify")` → exact string match.
5. `substituteArgs(template.content, parseCommandArgs(""))` → body text unchanged
   (no `$1`, `$@`, or `$ARGUMENTS` in the thin-pointer body).
6. Expanded body text is sent to the model as the user's message.
   Source: `dist/core/prompt-templates.js` (`expandPromptTemplate`, `substituteArgs`).

**Collision:** First-seen-by-name wins. Project templates beat global templates.
Source: `dist/core/resource-loader.js` (`dedupePrompts`).

---

## 4. TUI Command Priority (Gotcha)

The interactive TUI catches **builtin slash commands** at the TUI layer before
any template expansion. Builtin names include: `settings`, `model`, `effort`,
`fast`, `export`, `import`, `share`, `copy`, `btw`, `name`, `session`,
`system-prompt`, `logs`, `traces`, `context`, `changelog`, `update`, `hotkeys`,
`fork`, `clone`, `tree`, `login`, `logout`, `mcp`, `new`, `compact`, `refine`,
`goal`, `autonomous`, `rlm-max-depth`, `heartbeat`, `heartbeats`, `resume`,
`reload`, `fullscreen`, `quit`, and aliases `clear`, `usage`, `thinking`,
`rename`, `side`.

A template file whose name collides with any of these is **silently shadowed**:
the builtin executes; the template body is never sent to the model.
Source: `dist/modes/interactive/interactive-mode.js` (the long if-chain after
`commandName = resolveBuiltinSlashCommandName(...)`).

**The current seed's command protocols** (from `command_protocols()` in `install.sh`):
`brainstorm`, `canonize`, `deliver`, `from-scratch`, `grill`, `ingest-library`,
`initialize`, `recover`, `specify`, `test-first`, `verify`.

**None of these names collide with any prime-agent builtin.**
Verified by set intersection: result = ∅.

---

## 5. Thin Pointer Template: Does It Work Exactly Like Other Harnesses?

The seed's `generate_slash_commands` function (`install.sh:generate_slash_commands`)
emits files like:

```markdown
---
description: Enter the `specify` protocol. See docs/graph/protocols/specify.md for the full discipline.
---

<!-- GENERATED from protocols/specify.md by install.sh — do not edit here; edit the node and re-run. -->

Enter the **specify** protocol. Read `docs/graph/protocols/specify.md` and follow
its discipline for the current task.

Before acting, state which protocol you are entering and confirm its entry
conditions are met; if they are not, back up to the protocol that produces the
missing inputs. Then run the protocol, and end the session with
`docs/graph/protocols/deliver.md`.
```

For `prime-agent`:
- `description` key is consumed → shown in autocomplete.
- Body contains no argument placeholders → `substituteArgs` is a no-op.
- Body is sent verbatim to the model when `/specify` is typed.
- The model reads the pointer and follows `docs/graph/protocols/specify.md`.

**Verification:** Parsed with `dist/utils/frontmatter.js` logic (Python re-implementation):
frontmatter = `{'description': 'Enter the \`specify\` protocol. See docs/graph/protocols/specify.md for the full discipline.'}`,
body = the pointer text. Works.

**This is functionally identical to how Claude Code's `/.claude/commands/<name>.md`
and opencode's `/.opencode/commands/<name>.md` work.** All three harnesses:
1. Name the command from the filename.
2. Show `description` in autocomplete.
3. Expand the body as the user message on invocation.
4. Route the model into `docs/graph/protocols/<name>.md`.

**No transform is needed.** The same `generate_slash_commands` output works for
prime-agent with destination `.prime/agent/prompts/` instead of `.claude/commands/`
or `.opencode/commands/`.

---

## 6. Settings.json Integration

The planned `integrations/prime-agent/settings.json` includes:

```json
{
  "extensions": [".prime/agent/extensions"],
  "skills": [".prime/agent/skills"],
  "prompts": [".prime/agent/prompts"]
}
```

The `prompts` entry is **redundant with auto-discovery** (`.prime/agent/prompts/`
is auto-scanned by convention) but is present so templates load even if a project
disables convention discovery.
Source: `integrations/prime-agent/README.md`.

Paths in `.prime/agent/settings.json` resolve relative to `.prime/agent/`.
So the entry `".prime/agent/prompts"` resolves to `<cwd>/.prime/agent/.prime/agent/prompts` —
**this is a bug.** The correct value should be either `"prompts"` (relative to `.prime/agent/`)
or an absolute path, or the field can be omitted entirely (auto-discovery covers it).
Source: `dist/core/settings-manager.js` + `dist/core/package-manager.js`.

**Action item:** When writing `integrations/prime-agent/settings.json`, use `"prompts": ["prompts"]`
(relative to the settings file location = `.prime/agent/`) or omit the `prompts` key
and rely on auto-discovery.

---

## 7. Install Function Pattern

The `install.sh` currently lacks `install_prime_agent()`. The function should:

1. `place_file "$SEED_ROOT/core/AGENTS.md" "$PROJECT_DIR/AGENTS.md"`
2. `place_tree "$SEED_ROOT/agents" "$PROJECT_DIR/.prime/agent/agents" "*.md"`
3. `place_file ... SKILL.md` loop into `.prime/agent/skills/<name>/SKILL.md`
4. `generate_slash_commands "$PROJECT_DIR/.prime/agent/prompts"` ← **no special format needed**
5. Copy `integrations/prime-agent/settings.json` → `.prime/agent/settings.json`
6. Copy route extension → `.prime/agent/extensions/route-extension.ts`
7. `place_docs_skeleton`

`all` target in `install.sh` should add `prime-agent` to the expansion list.
Source: `integrations/prime-agent/README.md`; `install.sh` (`expanded=()` array).

---

## 8. Packages Discovery (Additional Path Source)

Prime Agent also loads prompts from **packages** (npm/git packages with a
`pi.prompts` entry or a `prompts/` directory). This is not relevant to the
seed's install path but is the mechanism for sharing templates with teams.
Source: `dist/core/package-manager.js` (`resolvePackageSources`);
`docs/packages.md`.

---

## Summary

| Question | Answer |
|----------|--------|
| Default project prompts dir | `<cwd>/.prime/agent/prompts/` |
| Default global prompts dir | `~/.prime/agent/prompts/` |
| Recursive scan? | No — flat dir only |
| Frontmatter fields used | `description` (string), `argument-hint` (string) |
| Name collision tiebreak | First-seen wins; project beats global |
| Builtin collision risk | None for current protocol names |
| Thin pointer format works? | Yes — no transform beyond destination path |
| Settings `prompts` path resolution | Relative to settings.json's parent dir |
| Potential settings.json bug | `".prime/agent/prompts"` is wrong relative path; use `"prompts"` or omit |
