# GitHub Copilot integration (VS Code & GitHub.com)

GitHub Copilot reads several customization layers, each with its own
file format:

1. **Repository instructions** —
   `.github/copilot-instructions.md` OR `AGENTS.md` at the repo
   root. Auto-applied to every Copilot Chat request in the
   workspace. The kernel goes here.
2. **Path-scoped instructions** —
   `.github/instructions/<name>.instructions.md`, each with a YAML
   `applyTo:` glob. Auto-applied when the user is working in a
   matching file path. We use these for specialist guidance that's
   relevant only in specific areas (e.g. test files, docs/).
3. **Prompt files** — `.github/prompts/<name>.prompt.md`, each with
   YAML frontmatter (mode, description, tools). Surface as slash
   commands in Copilot Chat. We use these for the protocols.
4. **Custom agents** — `.github/agents/<name>.agent.md` (formerly
   `.github/chatmodes/<name>.chatmode.md`). Surface in the Copilot
   Chat agent picker. We use these for the specialist personas.

This seed system maps to Copilot as follows:

| Seed file                | Copilot destination                                  |
|--------------------------|------------------------------------------------------|
| `core/AGENTS.md`         | `.github/copilot-instructions.md` (copy)             |
| `core/AGENTS.md`         | `AGENTS.md` at repo root (Copilot also reads this)   |
| `agents/*.md`            | `.github/agents/*.agent.md` (transformed)            |
| `skills/*/SKILL.md`      | `.github/instructions/*-skill.instructions.md` (transformed) |
| `protocols/*.md`         | `.github/prompts/*.prompt.md` (transformed)          |
| `templates/`             | `templates/` (kept at repo root, untouched)          |
| `templates/docs/`        | `docs/graph/` (missing leaves added on install)      |

## Why duplicates?

Copilot's discovery is filename-driven and the formats are
incompatible (different frontmatter keys, different folder
expectations). The installer transforms — it doesn't symlink — for
this integration, because the host expects specific filenames and
frontmatter shapes.

The source of truth remains the universal files in `agents/`,
`protocols/`, `skills/`, and `core/`. When you change a source
file, re-run `install.sh github-copilot` to regenerate the
transformed copies — then reload, because a regenerated
`.github/agents/*.agent.md` does not appear in the picker of the session that
regenerated it (`docs/graph/method/delegation.md`,
`delegation.harness-registration`).

## Frontmatter mapping

### Source agent → `.github/agents/<name>.agent.md`

```yaml
# Source (agents/01-architect.md) — quoted verbatim
---
name: architect
description: Senior system architect. ...
tools: [Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task]
model: opus
---

# Transformed (.github/agents/architect.agent.md)
---
description: Senior system architect. ...
tools: ['codebase', 'search', 'usages', 'findTestFiles', 'runCommands', 'editFiles', 'fetch', 'githubRepo']
---
```

The transform derives each agent's Copilot toolset from its OWN
`tools:` allowlist (the allowlist is the discipline — a write-less
agent must stay write-less on Copilot too):
- always granted: `codebase`, `search`, `usages`, `findTestFiles`,
  and `runCommands` — command execution is a baseline because the
  GRAPH DISCIPLINE bootstrap mandates running
  `python3 docs/graph/graph-lint.py --plan` / `agent-lint.py --route`
  in every session, Bash-less charters included
- `Write` / `Edit` → `editFiles`
- `Bash` → `runTasks` (the workspace task runner)
- `WebSearch` / `WebFetch` → `fetch`, `githubRepo` (both are REMOTE
  reach; `githubRepo` searches GitHub, so it is web-gated, not part of
  the local read set)

Two fields are deliberately NOT projected:
- `model:` — Copilot model ids churn; the class stays in the source
  node (`docs/graph/agents/<name>.md`) and the session picks the
  workspace default.
- `Task` — Copilot has no subagent spawning. The six coordinators'
  delegation flows (including the kernel's close-out-spawn mandate)
  degrade to the single session on Copilot: do the work sequentially
  in-session and record the deviation, rather than simulating personas
  in-chat (which the kernel forbids).

### Source protocol → `.github/prompts/<name>.prompt.md`

Protocol frontmatter (`name`, `description`) maps to the Copilot
prompt's frontmatter. The slash-command name is the filename, so
`from-scratch.prompt.md` becomes `/from-scratch`.

### Source skill → `.github/instructions/<name>-skill.instructions.md`

Copilot has no native "skill" concept; we represent them as
path-scoped instructions with broad `applyTo: '**'` globs so they
apply in any context. The frontmatter becomes:

```yaml
---
description: <skill description>
applyTo: '**'
---
```

## Install

```sh
/path/to/cypress/install.sh github-copilot
```

This generates `.github/` and `AGENTS.md` from the source. Re-run
after editing any source file.

## Conflict with existing `.github/copilot-instructions.md`

If the project already has a `.github/copilot-instructions.md`, the
installer:
1. Backs up the existing file to
   `.github/copilot-instructions.md.bak-<timestamp>`.
2. Writes the kernel.
3. Prints a diff so the maintainer can merge custom content back
   in.

## VS Code settings

For multi-root workspaces or monorepos where the open folder is a
sub-folder of the repo, enable
`chat.useCustomizationsInParentRepositories` so Copilot discovers
the seed's `.github/` from a parent.

## Enforcing progressive discovery in Copilot (Agent Hooks)

Progressive discovery — open the graph router, load only the nodes a
task needs, declare what you skipped — is guidance a capable model
follows and a small local model (e.g. an Ollama model behind Copilot)
often skips. You do not have to rely on the model following it: **VS
Code Agent Hooks (Preview) can enforce it deterministically**, the same
way Claude Code does, because the two share a hook format.

- **The hook is cross-tool.** `route-hook.py` runs on `UserPromptSubmit`,
  runs the graph router on the actual prompt, and returns the route-first
  mandate plus the suggested node set as
  `hookSpecificOutput.additionalContext`, which the host injects as a
  prepended message. It emits **JSON** (plain-text stdout is *not*
  injected by Copilot) and uses `${CLAUDE_PROJECT_DIR:-$PWD}` in the
  command — Claude Code sets `$CLAUDE_PROJECT_DIR`; Copilot doesn't, and
  falls back to `$PWD` (its hook cwd is the workspace root) — so the
  same command line resolves in both hosts.
- **VS Code reads `.claude/settings.json` hooks directly.** So if the
  project has the Claude Code install (`.claude/settings.json` +
  `.claude/route-hook.py`), Copilot picks up the same hook — nothing
  extra needed. A Copilot-only install also drops
  `.github/hooks/route.json` + `.github/hooks/route-hook.py` so it works
  standalone. Do not keep both configs, or the hook fires twice.
- **Enable it:** Agent Hooks are Preview — turn them on in VS Code
  (Copilot agent settings) and confirm the `route` hook is listed. The
  format may change while in Preview; see
  <https://code.visualstudio.com/docs/agent-customization/hooks>.

Hooks are the strongest lever, but two more help, especially with a weak
model:

1. **Use a capable model** — a 7–8B local model may still not act well on
   the injected context; the hook guarantees the context is *present*,
   not that the model reasons well over it.
2. **Fresh chat, don't attach the whole workspace** (`#codebase` /
   `@workspace`) — Copilot's own context-gathering fills the window
   before the model reasons, which is orthogonal to the graph.

The `.github/copilot-instructions.md` this seed generates also leads with
a blunt, tool-free "FIRST MOVE" mandate, so even without hooks enabled the
route-first instruction is the first thing the model reads.
