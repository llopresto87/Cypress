# OpenAI Codex CLI integration

Codex reads:
1. `AGENTS.md` files, walking up from the working directory to the
   project root (the directory containing `.git` by default). Files
   merge top-down.
2. Fallback filenames if `AGENTS.md` is missing
   (`project_doc_fallback_filenames` in `~/.codex/config.toml`):
   `TEAM_GUIDE.md`, `.agents.md`, etc.
3. Skills registered via `[[skills.config]]` entries in
   `~/.codex/config.toml`.
4. Subagent role configuration via the `[agents]` section in
   `~/.codex/config.toml`.

Codex does not support `.claude/`-style directories of subagents
out of the box; subagents are configured globally in
`~/.codex/config.toml`. Project-local agents are surfaced by
including their contents in `AGENTS.md` (or by referencing them
from `AGENTS.md`).

This seed system maps to Codex as follows:

| Seed file                | Codex destination                                |
|--------------------------|--------------------------------------------------|
| `core/AGENTS.md`         | `AGENTS.md` at repo root (with sub-agents inlined or referenced) |
| `agents/*.md`            | `.codex/agents/*.md` (referenced from AGENTS.md) |
| `skills/*/SKILL.md`      | `.codex/skills/*/SKILL.md` (registered in `~/.codex/config.toml`) |
| `protocols/*.md`         | `docs/graph/protocols/*.md` (graph nodes; no `.codex/` copy) |
| `templates/`             | `templates/` (kept at repo root, untouched)      |
| `templates/docs/`        | `docs/graph/` (missing leaves added on install)  |

## AGENTS.md size budget

Codex truncates `AGENTS.md` at `project_doc_max_bytes` (default
32 KiB). The seed system's `AGENTS.md` is intentionally short
(~9 KB); the depth lives in the referenced files. To avoid
truncation, do not paste agent and protocol bodies into
`AGENTS.md` — keep them in `.codex/` and let the agent open them
on demand.

If your team needs more, set in `~/.codex/config.toml`:

```toml
project_doc_max_bytes = 65536
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
```

## Skills registration

Codex skills are not auto-discovered. Each one must be listed in
`~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/abs/path/to/project/.codex/skills/library-wiki/SKILL.md"
enabled = true

[[skills.config]]
path = "/abs/path/to/project/.codex/skills/spec-author/SKILL.md"
enabled = true
# ... one per skill
```

The bundled `config.toml.example` in this directory shows the full
set — one `[[skills.config]]` entry per skill the seed ships. Copy it
into `~/.codex/config.toml` and adjust the paths to the project root.

## Install

```sh
/path/to/cypress/install.sh codex
```

Creates (copies by default; `--symlink` opts into live seed links):
- `AGENTS.md` → copy of `core/AGENTS.md` (shared with a co-installed
  Claude Code kernel where present)
- `.codex/agents/*.md` → copies of `agents/*.md`
- `.codex/skills/<name>/SKILL.md` → copies of `skills/<name>/SKILL.md`
- protocols install once, as graph nodes: `docs/graph/protocols/*.md`
- A printed reminder showing the `~/.codex/config.toml` lines
  the user needs to add for skill registration (the installer
  does not modify global user config without consent).

Both of those land after the current session began, so nothing installed here is
addressable until a new session starts — the global-config merge doubly so.
`docs/graph/method/delegation.md` (`delegation.harness-registration`) owns that
rule and its recorded fallback.

## Approval modes and the verify rule

Codex has three approval modes: `untrusted`, `on-request`, `never`.
The seed system's `verify` protocol assumes the agent can run gate
commands; pick `on-request` for interactive sessions and `never` for
non-interactive CI runs (the latter requires a hardened sandbox).
