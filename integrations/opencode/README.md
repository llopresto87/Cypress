# opencode integration

opencode reads:
1. `AGENTS.md` (project rules — its preferred filename) OR `CLAUDE.md` as fallback.
2. `.opencode/agents/*.md` (agent definitions with YAML frontmatter).
3. `.opencode/commands/*.md` (custom slash commands).
4. `.opencode/skills/<name>/SKILL.md` (or `.claude/skills/`, `~/.claude/skills/`
   as Claude-Code-compatible fallbacks).
5. `opencode.json` (project config; can also define agents and commands
   inline under the `agent` / `command` keys — the seed does not, because the
   markdown files above are their single home). The seed ships only the
   `.json` form, never a `.jsonc` twin; the reason is below.

All four directory locations above are discovered **by convention**. No config
key sets them, and the config schema rejects unknown keys outright
(`additionalProperties: false`), so a config that tries to declare them is not
merely redundant — it is invalid.

opencode is Claude-Code-compatible by default: if no opencode-native
files exist, it reads `CLAUDE.md` and `~/.claude/skills/`. This means
a project set up for Claude Code already works in opencode.

This seed system maps to opencode as follows:

| Seed file                | opencode path                                      |
|--------------------------|----------------------------------------------------|
| `core/AGENTS.md`         | `AGENTS.md` (copy by default; `--symlink` opt-in)  |
| `agents/*.md`            | `.opencode/agents/*.md`                            |
| `skills/*/SKILL.md`      | `.opencode/skills/*/SKILL.md`                      |
| protocols → commands     | `.opencode/commands/*.md`                          |
| `templates/`             | `templates/` (kept at repo root, untouched)        |
| `templates/docs/`        | `docs/graph/` (missing leaves added on install)    |

### Known gap: the agent frontmatter is Claude-Code-shaped

The seed's `agents/*.md` carry Claude Code's frontmatter, and opencode's
markdown-agent contract is *not* a superset of it. Verified against
`opencode.ai/docs/agents` and `opencode.ai/config.json`, opencode recognizes
`description`, `mode`, `model`, `temperature`, `permission`, `disable`, `color`,
`top_p`, `steps`, `hidden` — and reads two of the seed's fields differently:

| seed frontmatter | opencode expects | consequence today |
|------------------|------------------|-------------------|
| `model: opus` / `model: sonnet` | `provider/model`, e.g. `anthropic/claude-sonnet-4-5` | the seed's model-class policy is not applied; agents run on the session default |
| `tools: [Read, Glob, Grep, Bash]` (list) | `permission: {edit: deny, bash: deny}` (`tools` object is deprecated) | a read-only leaf's tool bound is not enforced by the harness |

Neither is fixable in `opencode.json` — the fix is for `install.sh` to emit a
**transformed** projection for opencode the way it already does for Copilot
(`install_github_copilot` rewrites frontmatter per agent). Until then, treat the
model class and the leaf tool bound as brief-enforced on opencode, exactly as
`docs/graph/method/delegation.md` describes for role emulation
(`delegation.harness-registration`).

## Slash commands

Every protocol whose node declares `command: true` in its frontmatter is
exposed as a slash command; `install.sh` **generates** one command file per
such node into `.opencode/commands/` — the same roster as every other
harness, since all draw from the same `command:` field. Each is a short
pointer into the corresponding `docs/graph/protocols/<name>.md` node (the
single home). The user-sovereign meta-loop protocols (`graft`, `grow`,
`harvest`) and the canonize-folded `toolcraft` carry no `command:` field and
are commands on no harness.

## opencode.json

The bundled config is deliberately almost empty — every key it used to carry was
either invalid or redundant:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "subagent_depth": 3
}
```

- **`$schema`** — `https://opencode.ai/config.json`. The older
  `config-schema.json` URL now returns **404**; an editor pointed at it silently
  validates nothing.
- **`subagent_depth: 3`** — this is the load-bearing key. opencode defaults it to
  **1**, which "prevents subagents from launching subagents", and that alone
  collapses the seed's bounded-delegation topology: the deepest legal chain is
  depth 3 (`orchestrator` → `multi-agent-architect` → `architect` → leaf), so
  every coordinator's `max_spawn_depth` is unreachable at the default. The value
  must equal the highest `max_spawn_depth` in `agents/*.md`; `tests/seed-lint.py`
  enforces that the two agree.
- **no `instructions`** — opencode auto-loads project `AGENTS.md` as its rules
  file, so listing it again risks loading the kernel twice per session. The
  budget check in `tests/seed-lint.py` accounts for the auto-loaded kernel plus
  anything declared here.
- **no `agents` / `commands` / `skills` directory keys** — `agents` and
  `commands` are not config keys at all (the real ones are `agent` and
  `command`, and they hold *inline definitions*, not directories); `skills` is a
  real key but takes `{paths, urls}` for *additional* folders. All three
  directories are found by convention. Since the schema sets
  `additionalProperties: false`, the old `{"directory": ...}` entries were
  rejected keys, not harmless hints.
- **MCP servers** use the `mcp` key (not `mcp_servers`), shaped
  `{"<name>": {"type": "local", "command": [...], "environment": {...}}}`. The
  seed declares none: a documentation MCP is a project choice, and
  `research-scout` works from plain web fetch without one.

One config file ships, not two. opencode reads `opencode.json` **or**
`opencode.jsonc`, and with both present at the same tier the winner is
unspecified — the seed previously installed both, so a project could edit one and
have the other apply.

## Install

```sh
/path/to/cypress/install.sh opencode
```

Creates copies by default (`--symlink` opts into live seed links) from the seed source to:
- `AGENTS.md` → `core/AGENTS.md`
- `.opencode/agents/*.md` → `agents/*.md`
- `.opencode/skills/<name>/SKILL.md` → `skills/<name>/SKILL.md`
- `.opencode/commands/*.md` → generated by install.sh, one per protocol node with `command: true`
- `opencode.json` → `integrations/opencode/opencode.json` (copied,
  not symlinked, so the project can edit it)
- `docs/graph/` scaffolded; missing leaves populated from `templates/docs/`

## When both Claude Code and opencode are present

opencode prefers `AGENTS.md` over `CLAUDE.md`. If the project has
both, they should point at the same content — keep one as the
canonical file and symlink the other to it. The installer does this.
