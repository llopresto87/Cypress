# INSTALL.md

How to drop CYPRESS into a project, keep it up-to-date, and remove it when no
longer wanted.

**There is one entry point: [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md).** Paste it
into an agent-capable chat and it does the whole job — it *places* every seed
file into your target and then *grows* the target into a complete, full-depth
`docs/graph/` knowledge system. `install.sh` (documented below) is only the
placement mechanism that prompt invokes; `docs/graph/protocols/grow.md` is the
growth doctrine it executes, including the **completeness contract**
(`grow.completeness-contract`) that binds the orchestrating model to grow every
evidence-backed node and leaf — not a skeleton. This page is the reference for
the shell installer and the housekeeping (upgrade, uninstall, troubleshooting)
around that one flow.

## Prerequisites

- A POSIX shell (bash on macOS/Linux/WSL; Git Bash on Windows).
- `python3` (for the GitHub Copilot frontmatter transformation only).
- The seed system unzipped or cloned somewhere stable. In the default
  copy mode the seed path is only read at install time; in `--symlink`
  mode the placed files reference it, so don't move it after install.

## One-shot install and grow

The primary, coding-tool-neutral way to install **and grow** the seed is to
paste [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) into an agent-capable chat. That
prompt runs one flow in three phases: **PLACE** (invoke `install.sh` to drop
every seed file into the target — this phase may run from a chat rooted at the
seed), **HAND OFF** (re-enter the prompt in a fresh session rooted at the target,
because a host registers its agent roster at session start — see
`docs/graph/method/delegation.md`, `delegation.harness-registration`), and
**GROW IN FULL** (execute `docs/graph/protocols/grow.md` end to end, honoring its
completeness contract so every evidence-backed collection is covered). The chat
remains the orchestration/planning plane and spawns Sonnet-class scouts plus
Opus-class authors. The shell installer below is the PLACE-phase mechanism; you
rarely call it directly.

From the seed system directory:

```sh
./install.sh <tool> [--project-dir PATH] [--symlink|--copy] [--force]
```

`<tool>` is one of:
- `claude-code` — drops `CLAUDE.md` + `.claude/`.
- `opencode` — drops `AGENTS.md` + `.opencode/` + `opencode.json`.
- `codex` — drops `AGENTS.md` + `.codex/`; prints
  `~/.codex/config.toml` hints.
- `github-copilot` — generates `.github/` from sources (transformed,
  not symlinked).
- `prime-agent` — drops `AGENTS.md` + `.prime/agent/` (skills, prompts,
  agents, `route-extension.ts`, `settings.json`).
- `all` — runs all five.

### Examples

```sh
# Claude Code, current directory
./install.sh claude-code

# All five tools, explicit target
./install.sh all --project-dir ~/code/my-project

# Force overwrite without backups
./install.sh opencode --force

# Opt into symlink mode (edits to placed files write back into the seed)
./install.sh claude-code --symlink
```

## What the installer does

For each tool:
1. Drops the bootstrap kernel at the expected path (`CLAUDE.md` for
   Claude Code; `AGENTS.md` for the others). The kernel is small by
   design: everything else activates progressively through the graph.
2. Installs the entire method surface INTO the graph — protocols,
   skills (flattened `<name>.md`), agents, `method/` posture nodes, and
   the Tier-3 template artifacts — as seed-owned routable nodes under
   `docs/graph/{protocols,skills,agents,method,templates}/`.
3. Copies (or, with `--symlink`, links) harness projections where the
   tool demands a fixed location — agents and skills only — plus
   tool-specific files (slash commands, settings, config).
4. Ensures `docs/graph/` has the schema, linter, router, nodes directory,
   and every missing leaf collection from `templates/docs/`. Existing files
   are preserved. `INSTALL_PROMPT.md` then orchestrates source-grounded
   growth; `/initialize` is only an optional coding-tool adapter.
5. Installs the canonical prompt as `EXPERT_SEED_INSTALL_PROMPT.md` at the
   target root so later growth/refresh sessions remain tool-neutral.

For `github-copilot` specifically, files are *transformed* (not
symlinked) because Copilot expects different frontmatter shapes. Each
generated file carries a "GENERATED — do not edit" banner. Re-run the
installer after editing any source file to regenerate the Copilot
views, and use `--check` to detect drift without writing:

```sh
# CI drift gate: exits non-zero if the .github/ views are stale
./install.sh github-copilot --check
```

## Copy mode vs symlink mode

| Mode    | When                 | Pros                                                          | Cons                                                        |
|---------|----------------------|--------------------------------------------------------------|------------------------------------------------------------|
| copy    | Default (all OS)     | Project stays isolated; project edits never write back into the seed | Must re-run the installer to pull seed updates             |
| symlink | Opt-in (`--symlink`) | Edits to the seed propagate instantly                        | Seed path must stay stable; project edits write back into the seed |

Copy is the default so a project can customize its placed agents,
protocols, and commands without mutating the shared seed. Pass
`--symlink` to opt into live-linked files; `--copy` is accepted
explicitly but is already the default.

## What gets backed up

If a target file already exists, the installer:
- With `--force`: silently overwrites.
- Without `--force`: renames the existing file to
  `<path>.bak-<timestamp>` and warns.

The installer never deletes files outside of `.claude/`,
`.opencode/`, `.codex/`, or `.github/`. In `docs/graph/` it adds
missing scaffold and template leaves only and never touches
plant-authored content (`nodes/`, `specs/`, and the rest of the
graph you grow); the seed-owned machinery subtrees (`protocols/`,
`skills/`, `agents/`, `method/`, `templates/`) are fast-forwarded
to the current seed — byte-identical files are left untouched, and
anything that differs is backed up first (unless `--force`) so
`tools/graft-audit.py` can prove no customization was buried.

## Verifying the install

After installing:

```sh
# Confirm the kernel is in place
head -3 CLAUDE.md      # for Claude Code
head -3 AGENTS.md      # for opencode / codex / copilot

# Confirm agents loaded
ls .claude/agents/     # or .opencode/agents/  or .codex/agents/

# For Claude Code, list the slash commands inside the tool
# In a Claude Code session, run: /help

# For Copilot, in VS Code:
# - Verify .github/copilot-instructions.md exists
# - Open the Copilot Chat agent picker and confirm the custom agents
#   appear
```

`ls` proves the files are placed; it does not prove the tool can spawn
them. Every supported harness enumerates its agent directory when a
session *starts*, so the session that ran the installer still holds the
registry from before it — and a session rooted at the seed never holds
the project's roster at all. **Start a new session rooted at the project**
before running `grow` / `graft` or dispatching a specialist by name. The
installer prints this as its NEXT STEP; the full rule, including the
role-emulation fallback for when a restart is impossible, lives in
`docs/graph/method/delegation.md` (`delegation.harness-registration`).

## Codex post-install

The installer prints a path to a generated config snippet:

```
[seed] ACTION NEEDED: merge this snippet into ~/.codex/config.toml:
[seed]   /your/project/.codex/codex-config-snippet.toml
```

Merge that file into your global `~/.codex/config.toml` to register
all thirteen skills. The installer does not modify your global config
without consent.

## Upgrading

If you copied (the default), re-run the installer to pull seed updates:

```sh
./install.sh <tool> --force
```

If you used `--symlink`, edits to the seed propagate automatically —
just `git pull` or update the seed source; no re-install needed.

`--force` skips the backup chatter when you know the existing files
are just outdated copies.

## Uninstalling

The installer doesn't ship an uninstall command because the
operation is one shell line per tool:

```sh
# Claude Code
rm -rf CLAUDE.md .claude/

# opencode
rm -rf AGENTS.md .opencode/ opencode.json

# Codex
rm -rf AGENTS.md .codex/
# Then remove the [[skills.config]] entries from ~/.codex/config.toml.

# GitHub Copilot
rm -rf .github/copilot-instructions.md .github/agents \
        .github/prompts .github/instructions .github/templates \
        .github/hooks
# If AGENTS.md was also installed for Copilot, remove it too.
```

Your existing `docs/graph/` knowledge files are untouched.

## Multi-tool projects

Installing multiple tools is supported and common. They share the
same kernel (`AGENTS.md` / `CLAUDE.md`) and unified graph. If
the kernel target conflicts (e.g. opencode installs `AGENTS.md`
then Codex installs `AGENTS.md` over the same path), the installer
warns and backs up.

**Claude Code + Prime Agent, interchangeably.** These two are the
first-class harnesses, and one plant can run either. Install both:

```sh
./install.sh claude-code prime-agent
```

The installer collapses `CLAUDE.md` (Claude Code) and `AGENTS.md`
(Prime Agent) into a **single shared kernel file** — one is the real
file, the other a project-local symlink to it — so editing the kernel
updates both harnesses and they never drift. `.claude/` and
`.prime/agent/` sit side by side; `docs/graph/` is shared. Switching
harness is just opening the plant in the other tool. (On a platform
without symlinks the second kernel is an independent copy; keep the two
in sync by hand.)

Recommended order if installing all five:

```sh
./install.sh claude-code      # CLAUDE.md, no conflict with AGENTS.md
./install.sh opencode         # AGENTS.md (fresh)
./install.sh codex            # AGENTS.md (already present and identical — left untouched)
./install.sh github-copilot   # .github/copilot-instructions.md (no conflict)
./install.sh prime-agent      # AGENTS.md (present and identical — untouched); adds .prime/agent/
```

Or simply `./install.sh all`.

## Troubleshooting

**"refusing to install the seed system into itself"**
You ran the installer from inside the seed directory with no
`--project-dir`. Pass `--project-dir` to a target project.

**Symlinks don't work on my system**
Use `--copy`. Common on Windows without developer mode or admin
rights.

**Copilot doesn't see the custom agents**
Verify `.github/agents/<name>.agent.md` exists (post-rename from
the legacy `.chatmode.md`). In VS Code, run the
`Chat: Configure Custom Agents` command to confirm discovery.

**Codex truncates AGENTS.md**
Raise `project_doc_max_bytes` in `~/.codex/config.toml`. The
provided snippet sets it to 64 KiB.

**Agents not triggering in opencode**
`opencode.json` does not (and cannot) list the agent directory — opencode
discovers `.opencode/agents/*.md` by convention. Confirm the files are there,
then confirm the session started *after* they were placed
(`docs/graph/method/delegation.md`, `delegation.harness-registration`). Note the
known gap in `integrations/opencode/README.md`: the seed's `model:` and `tools:`
frontmatter are Claude-Code-shaped, so on opencode the model class and a leaf's
tool bound are brief-enforced rather than harness-enforced.
