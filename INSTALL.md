# INSTALL.md

How to put CYPRESS into a project, keep it up to date, and take it out again.

There is one entry point: [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md). Paste it
into an agent-capable chat, meaning a coding tool's chat that can run commands
in your repository, and it does the whole job in two parts. First it *places*
every seed file (the files this repository ships) into your project; then it
*grows* your project's `docs/graph/` into a complete, full-depth knowledge
graph. `install.sh`, documented below, is only the placement step that prompt
runs. The growth follows `docs/graph/protocols/grow.md`, including its
**completeness contract** (`grow.completeness-contract`), which binds the model
running the growth to write every node and leaf your code gives evidence for,
to full depth. This page is the reference for the shell installer and for the
housekeeping around that one flow: upgrade, uninstall and troubleshooting.

## Prerequisites

- **bash** 3.2 or newer (macOS/Linux/WSL; Git Bash on Windows). Not any
  POSIX shell: `install.sh` declares `#!/usr/bin/env bash` on its first line
  and runs `set -euo pipefail`, an option POSIX's `set` does not define, so
  `dash` and other strict `/bin/sh` implementations fail. The 3.2 floor is
  what the script holds itself to: its comments name the bash 4+ constructs
  it avoids for macOS.
- `python3`. The installer runs short Python snippets to read an existing
  install stamp, fill the `plant:` entries of `docs/graph/index.md`, and write
  the Codex and GitHub Copilot files.
- The seed system unzipped or cloned somewhere stable. In the default
  copy mode the seed path is only read at install time; in `--symlink`
  mode the placed files reference the seed, so keep it at the path you
  installed from.

## One-shot install and grow

The main way to install and grow the seed, whichever coding tool you use,
is to paste [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) into an agent-capable chat.
That prompt runs one flow in three phases:

- **PLACE**: it runs `install.sh` to copy every seed file into your project.
  This phase may run from a chat rooted at the seed.
- **HAND OFF**: the prompt is entered again in a fresh session rooted at your
  project, because on a first install the session that placed the agents may
  not have registered them; see `docs/graph/method/delegation-bounds.md`,
  `delegation.harness-registration`.
- **GROW IN FULL**: the session carries out `docs/graph/protocols/grow.md` end
  to end, honoring its completeness contract so that every collection your code
  gives evidence for is covered.

The chat stays where the work is planned and coordinated, and it starts
investigation-class scouts and authoring-class authors to do it. The shell installer below
is the PLACE-phase mechanism, and you rarely call it directly.

From the seed system directory:

```sh
./install.sh <tool> [--project-dir PATH] [--symlink|--copy] [--force]
             [--environment-class CLASS] [--commit-attribution none|TRAILER]
             [--deliverable-language BCP47] [--comment-language BCP47]
             [--legal-corpus yes|no] [--legal-jurisdiction CC] [--print-config]
```

`<tool>` is one of the list below. Every tool gets the kernel under both
names, `CLAUDE.md` and `AGENTS.md`: the first one placed holds it, and the
other is a symlink to it.
- `claude-code`: drops `CLAUDE.md` + `.claude/`.
- `opencode`: drops `AGENTS.md` + `.opencode/` + `opencode.json`, with each
  agent's `model:` line written from the plant's model map,
  `docs/graph/models.md`.
- `codex`: deprecated, a frozen host
  ([ADR-0009](docs/decisions/adr-0009-host-support-tiers.md)); drops
  `AGENTS.md` + `.codex/`; prints `~/.codex/config.toml` hints.
- `github-copilot`: deprecated, a frozen host
  ([ADR-0009](docs/decisions/adr-0009-host-support-tiers.md)); generates
  `.github/` from sources (transformed, not symlinked).
- `prime-agent`: drops `AGENTS.md` + `.prime/agent/` (skills, prompts,
  agents, the hook core in `hooks/` and the two extensions that run it,
  `settings.json`).
- `all`: runs claude-code, opencode and prime-agent. Name `codex` or
  `github-copilot` as well to install a frozen host.

### Examples

```sh
# Claude Code, current directory
./install.sh claude-code

# The three maintained tools, explicit target
./install.sh all --project-dir ~/code/my-project

# Replace without the per-file warning (the backup is still made)
./install.sh opencode --force

# Opt into symlink mode (edits to placed files write back into the seed)
./install.sh claude-code --symlink
```

## What the installer does

For each tool:
1. Drops the bootstrap kernel (see above). The kernel is small by design,
   and everything else activates progressively through the graph.
2. Installs the entire method surface into the graph (protocols, skills
   flattened to `<name>.md`, agents, `method/` posture nodes and the Tier-3
   template artifacts) as seed-owned nodes the router can reach, under
   `docs/graph/{protocols,skills,agents,method,templates}/`.
3. Copies (or, with `--symlink`, links) harness projections where the
   tool expects a fixed location, for agents and skills only, plus
   tool-specific files (slash commands, settings, config).
4. Places in `docs/graph/` the schema, the linter (whose `--plan` is the
   router), the `index.md` map, the nodes directory,
   and every missing leaf collection from `templates/docs/`, among them the
   model map `docs/graph/models.md`, which you fill once with the model each
   host runs for each class and effort. Existing files are preserved ([plant files kept](DOCUMENTATION.md#enf-plant-files-kept)). `INSTALL_PROMPT.md` then orchestrates source-grounded
   growth. `/initialize` is the entry fork behind it: grow when there is
   source to scout, from-scratch when the repository is empty.
5. Installs the canonical prompt as `EXPERT_SEED_INSTALL_PROMPT.md` at the
   target root so later growth/refresh sessions remain tool-neutral.

For `github-copilot` specifically, files are *transformed* (not
symlinked) because Copilot expects different frontmatter shapes. Each
generated file carries a "GENERATED — do not edit" banner. For `opencode`,
each agent is rendered with its `model:` line from the model map; after you
edit the map, re-run `install.sh opencode`. Re-run the installer after
editing any source file to regenerate these views, and use `--check` to
detect drift without writing:

```sh
# CI drift gate: exits non-zero if the generated views are stale
./install.sh github-copilot --check
./install.sh opencode --check
```

## The plant facts are yours to state

`docs/graph/index.md` carries a `plant:` section with four facts only the owner can
assert: `environment_class` (ephemeral-test, staging, real-production or mixed; it
decides what the release posture tolerates, build-on-host included), `commit_attribution`
(`none` or the trailer text), `deliverable_language` and `comment_language`. Pass them at
install time with those four flags, or fill the section by hand before grow or graft.

Two more decisions are the owner's, asked before a run, not settled during
one: `--legal-corpus yes|no`, which places the whole legal corpus or
records that this plant carries none, and `--legal-jurisdiction CC`, which names
the national layer. `agent.legal` can do exactly one thing until the first is
answered, which is to decline the work
([charter duties](DOCUMENTATION.md#enf-charter-duties)), and the installer says
so at the end of every run that leaves it undecided.
The installer keeps any value the plant already declares and names each
remaining placeholder as a NEXT STEP.

The model map, `docs/graph/models.md`, is the third owner decision: which
model each host runs for each class and effort. An unfilled row is not an
error: the agent runs on its caller's model, and graft reports the unfilled
map as a disclosed line
([ADR-0022](docs/decisions/adr-0022-the-plant-model-map.md)).

## Copy mode vs symlink mode

| Mode    | When                 | Pros                                                          | Cons                                                        |
|---------|----------------------|--------------------------------------------------------------|------------------------------------------------------------|
| copy    | Default (all OS)     | Project stays isolated; project edits do not write back into the seed | Must re-run the installer to pull seed updates             |
| symlink | Opt-in (`--symlink`) | Edits to the seed propagate instantly                        | Seed path must stay stable; project edits write back into the seed |

Copy is the default so a project can customize its placed agents,
protocols, and commands without mutating the shared seed. Pass
`--symlink` to opt into live-linked files; `--copy` is accepted
explicitly but is already the default.

## What gets backed up

If a target file already exists and differs from what is being placed,
the installer renames it to `<path>.bak-<timestamp>` and writes the new
body. A file that already matches is left alone, with no backup and no rewrite,
so re-installing over an unchanged project creates nothing.

`--force` suppresses the per-file warning, never the backup
([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)). The
backup is graft Phase 7's safety net and the input `tools/graft-audit.py`
reads, so a flag that discarded it would leave a graft with nothing to audit
and no way back. No mode overwrites without a recovery copy. Two files are
replaced without a copy, by design: the install stamp `.cypress/seed.json`,
which keeps every key the installer does not own, and
`.cypress/recreated-nodes.txt`, the whole list of seed nodes the last run
re-created. Both are derived, never authored, so a copy would carry no
recovery value.

If the destination is a symlink, the link is moved aside, not followed, so an
install does not modify a file outside the target directory
([backup before replace](DOCUMENTATION.md#enf-backup-before-replace)).

The installer never deletes files outside of `.claude/`,
`.opencode/`, `.codex/`, or `.github/`, with one exception: a second kernel
file identical to the seed kernel is removed and replaced by the symlink to
the first. In `docs/graph/` it adds
missing scaffold and template leaves only and never touches
plant-authored content (`nodes/`, `specs/`, and the rest of the
graph you grow); the seed-owned machinery subtrees (`protocols/`,
`skills/`, `agents/`, `method/`, `templates/`) are fast-forwarded
to the current seed: byte-identical files are left untouched, and
anything that differs is backed up first, so
`tools/graft-audit.py` can prove no customization was buried
([plant files kept](DOCUMENTATION.md#enf-plant-files-kept),
[graft audit](DOCUMENTATION.md#enf-graft-audit)).

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

The head command prints the start of the kernel, whose title names CYPRESS, and
`ls` lists the placed agent files. That shows the files are placed; it does not show that the tool can start
them. When a host picks up agent files placed during a running session is
host-dependent (the [host capability matrix](documentation/host-capability-matrix.md)
records it per host), and a session rooted at the seed does not hold the
project's roster at all. **Start a new session rooted at the project**
before running `grow` / `graft` or dispatching a specialist by name. The
installer prints this as its NEXT STEP
([registration notice](DOCUMENTATION.md#enf-registration-notice)); the full rule, including the
role-emulation fallback for when a restart is impossible, lives in
`docs/graph/method/delegation-bounds.md` (`delegation.harness-registration`).

## Codex post-install

The installer prints a path to a generated config snippet:

```
[seed] ACTION NEEDED: merge this snippet into ~/.codex/config.toml:
[seed]   /your/project/.codex/codex-config-snippet.toml
```

Merge that file into your global `~/.codex/config.toml` to register
all fifteen skills. The installer does not modify your global config
without consent.

## Upgrading

If you copied (the default), re-run the installer to pull seed updates:

```sh
./install.sh <tool> --force
```

If you used `--symlink`, edits to the seed propagate automatically:
`git pull` or otherwise update the seed source, and no re-install is needed.

For a grown plant, the reconciled upgrade is `graft`, through
[`GRAFT_PROMPT.md`](GRAFT_PROMPT.md): it adopts what the seed advanced,
keeps the plant's own divergences, and reports what it cannot reconcile.

## Uninstalling

The installer doesn't ship an uninstall command because the
operation is one shell line per tool:

```sh
# Claude Code
rm -rf CLAUDE.md AGENTS.md .claude/

# opencode
rm -rf AGENTS.md CLAUDE.md .opencode/ opencode.json

# Codex
rm -rf AGENTS.md CLAUDE.md .codex/
# Then remove the [[skills.config]] entries from ~/.codex/config.toml.

# GitHub Copilot
rm -rf AGENTS.md CLAUDE.md .github/copilot-instructions.md .github/agents \
        .github/prompts .github/instructions .github/hooks
```

`CLAUDE.md` and `AGENTS.md` are the kernel pair every tool shares, so keep
them while another tool stays installed. The lines above leave `.cypress/`
(the install stamp and the files beside it), `EXPERT_SEED_INSTALL_PROMPT.md`
and everything under
`docs/graph/` in place, your knowledge files included.

## Multi-tool projects

Installing multiple tools is supported and common. They share the
same kernel (`AGENTS.md` / `CLAUDE.md`) and unified graph.

**Claude Code + Prime Agent, interchangeably.** These two are the
first-class harnesses, and one plant can run either. Install both:

```sh
./install.sh claude-code prime-agent
```

The installer collapses `CLAUDE.md` (Claude Code) and `AGENTS.md`
(Prime Agent) into a **single shared kernel file**, one the real file and the
other a project-local symlink to it, so editing the kernel
updates both harnesses and the two do not drift apart; where symlinks are
unavailable, the second kernel is a copy you keep in sync by hand.
`.claude/` and `.prime/agent/` sit side by side; `docs/graph/` is shared.
Switching harness is just opening the plant in the other tool.

Recommended order if installing all five:

```sh
./install.sh claude-code      # CLAUDE.md, with AGENTS.md as a symlink to it
./install.sh opencode         # kernel pair already current, left untouched
./install.sh codex            # frozen host; kernel pair left untouched
./install.sh github-copilot   # frozen host; adds .github/copilot-instructions.md
./install.sh prime-agent      # kernel pair left untouched; adds .prime/agent/
```

`./install.sh all` covers the three maintained tools; `./install.sh all codex
github-copilot` adds the two frozen ones.

## Troubleshooting

**`refusing to install the seed system into itself`**
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
`opencode.json` has no key for the agent directory; opencode
discovers `.opencode/agents/*.md` by convention. Confirm the files are there,
then confirm the session started *after* they were placed
(`docs/graph/method/delegation-bounds.md`, `delegation.harness-registration`). Note the
known gap in `integrations/opencode/README.md`: the seed's `tools:` frontmatter
is Claude-Code-shaped, so on opencode a leaf's tool bound is carried by the
brief rather than held by the harness
([tool allow-list](DOCUMENTATION.md#enf-tool-allowlist)). An agent whose
`model:` line is missing runs on its caller's model, because the model map
names no opencode model for its class and effort.
