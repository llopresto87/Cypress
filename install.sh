#!/usr/bin/env bash
# install.sh — CYPRESS installer
#
# Usage:
#   install.sh <tool> [--project-dir PATH] [--symlink|--copy] [--force]
#                     [--print-config]
#
# <tool> is one of:
#   claude-code        — Drop CLAUDE.md + .claude/ into the project.
#   opencode           — Drop AGENTS.md + .opencode/ + opencode.json.
#                         (one config file; opencode auto-discovers
#                          .opencode/{agents,commands,skills}/ by convention)
#   codex              — Drop AGENTS.md + .codex/; print ~/.codex/config.toml hints.
#   github-copilot     — Generate .github/ from sources (transformed; not symlinked).
#   prime-agent        — Drop AGENTS.md + .prime/agent/ (skills, prompts, agents,
#                         route-extension, settings).
#   all                — Run claude-code, opencode, codex, github-copilot, and prime-agent.
#
# Options:
#   --project-dir PATH   Target project directory (default: $PWD).
#   --symlink            Symlink files into the project (opt-in; edits to a
#                         placed file write back into the seed).
#   --copy               Copy files into the project (default; keeps the seed
#                         isolated from project edits).
#   --force              Overwrite existing target files without prompting.
#   --print-config       For `codex`: print the config.toml lines with
#                         resolved paths instead of editing anything.
#   --check              For `github-copilot`: verify the generated .github/
#                         views are in sync with the seed sources; write
#                         nothing; exit non-zero if stale (CI drift gate).
#   -h, --help           Show this help.
#
# The seed system's source files are not modified. The installer
# copies them by default so project edits never write back into the
# seed; --symlink instead links to them (edits then propagate both
# ways). To uninstall, delete the dropped files and directories from
# the project.

set -euo pipefail

SEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$PWD"
LINK_MODE="copy"   # copy by default; --symlink opts into live seed links
FORCE=0
PRINT_CONFIG=0
CHECK=0
TOOLS=()

# --- helpers ---------------------------------------------------------

die() { printf "ERROR: %s\n" "$*" >&2; exit 1; }
log() { printf "[seed] %s\n" "$*"; }
warn() { printf "[seed] WARNING: %s\n" "$*" >&2; }

# log_registration_notice AGENT_DIR
# Every supported harness enumerates its agent directory when a SESSION
# STARTS, so the session that ran this installer holds a registry from
# before the projection existed and cannot spawn the roster by name — the
# "installed but not spawnable" trap that stalls a first growth. One home
# for the rule: core/method/delegation.md, fact
# delegation.harness-registration; this is only its install-time notice.
log_registration_notice() {
    local agent_dir="$1"
    log ""
    log "NEXT STEP — placed, but not yet spawnable in the session that ran this"
    log "  installer: the harness enumerated $agent_dir when that session"
    log "  started. Before running grow/graft or dispatching a specialist by"
    log "  name, start a NEW agent session rooted at:"
    log "    $PROJECT_DIR"
    log "  (the plant — never the seed directory). If a restart is impossible,"
    log "  use the recorded role-emulation fallback in"
    log "  docs/graph/method/delegation.md (delegation.harness-registration)."
}

# place_file SOURCE DEST
# Symlinks or copies SOURCE to DEST per $LINK_MODE; backs up existing
# DEST when --force not set; prompts otherwise.
place_file() {
    local src="$1" dest="$2"
    [[ -e "$src" ]] || die "missing source: $src"
    mkdir -p "$(dirname "$dest")"
    if [[ -e "$dest" || -L "$dest" ]]; then
        # an already-correct destination needs no backup and no rewrite:
        # backing up byte-identical files buries the graft-audit signal
        # under hundreds of no-op .bak entries on every re-run
        case "$LINK_MODE" in
            copy)    [[ -f "$dest" && ! -L "$dest" ]] && cmp -s "$src" "$dest" && return 0 ;;
            symlink) [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]] && return 0 ;;
        esac
        if [[ $FORCE -eq 1 ]]; then
            rm -f "$dest"
        else
            local bak="${dest}.bak-$(date +%Y%m%d-%H%M%S)"
            mv "$dest" "$bak"
            warn "backed up existing $dest -> $bak"
        fi
    fi
    case "$LINK_MODE" in
        symlink) ln -s "$src" "$dest" ;;
        copy)    cp "$src" "$dest" ;;
        *)       die "unknown link mode: $LINK_MODE" ;;
    esac
}

# place_kernel DEST
# Place the bootstrap kernel at DEST, where DEST is a repo-root kernel file:
# CLAUDE.md (read by Claude Code) or AGENTS.md (read by Prime Agent, opencode,
# and Codex; AGENTS.md wins over CLAUDE.md within a directory). To let ONE plant
# run Claude Code and Prime Agent INTERCHANGEABLY off byte-identical project
# instructions, the two kernel files are collapsed to a single source of truth:
# the first one placed is a real file (a seed copy by default, or a seed symlink
# under --symlink), and the second becomes a PROJECT-LOCAL relative symlink to
# the first. The link is between the two project files, never to the seed, so
# copy-mode isolation from the seed is preserved. Editing the kernel then updates
# both harnesses at once — no drift. On a platform without symlinks the second
# file degrades to an independent copy (identical at install; may drift on edit).
place_kernel() {
    local dest="$1" name sibling seed_kernel
    name="$(basename "$dest")"
    seed_kernel="$SEED_ROOT/core/AGENTS.md"
    case "$name" in
        CLAUDE.md) sibling="$PROJECT_DIR/AGENTS.md" ;;
        AGENTS.md) sibling="$PROJECT_DIR/CLAUDE.md" ;;
        *)         place_file "$seed_kernel" "$dest"; return ;;
    esac

    # ONE real file holds the kernel; the other is a PROJECT-LOCAL relative
    # symlink to it, so Claude Code (CLAUDE.md) and Prime Agent / opencode /
    # Codex (AGENTS.md) run off byte-identical instructions. The real file's
    # BODY is ALWAYS brought to the current seed kernel: a graft that merely
    # re-points the symlink and leaves a STALE kernel body is the exact bug this
    # guards against (it also left no .bak, so graft-audit could not see it).
    # A stale body is fast-forwarded WITH a per-file .bak; a pristine body is
    # left untouched (idempotent, no backup churn).
    local realfile
    if [[ -f "$dest" && ! -L "$dest" ]]; then realfile="$dest"
    elif [[ -f "$sibling" && ! -L "$sibling" ]]; then realfile="$sibling"
    else realfile="$dest"; fi

    # 1) Fast-forward the canonical real file to the current seed kernel.
    if [[ -f "$realfile" && ! -L "$realfile" ]] && cmp -s "$seed_kernel" "$realfile"; then
        : # already current — no backup, no rewrite
    else
        if [[ -f "$realfile" && ! -L "$realfile" && $FORCE -ne 1 ]]; then
            local bak="${realfile}.bak-$(date +%Y%m%d-%H%M%S)"
            cp "$realfile" "$bak"; warn "backed up existing $realfile -> $bak"
        fi
        rm -f "$realfile"
        cp "$seed_kernel" "$realfile"
        log "kernel: $(basename "$realfile") fast-forwarded to the current seed kernel"
    fi

    # 2) Point the OTHER kernel file at the real file via a project-local symlink.
    local other
    if [[ "$realfile" == "$dest" ]]; then other="$sibling"; else other="$dest"; fi
    if [[ -L "$other" && "$(readlink "$other")" == "$(basename "$realfile")" ]]; then
        log "kernel: $(basename "$other") -> $(basename "$realfile") (shared kernel — interchangeable Claude Code / Prime Agent)"
        return
    fi
    if [[ -f "$other" && ! -L "$other" && $FORCE -ne 1 ]] && ! cmp -s "$seed_kernel" "$other"; then
        local bak2="${other}.bak-$(date +%Y%m%d-%H%M%S)"
        cp "$other" "$bak2"; warn "backed up existing $other -> $bak2"
    fi
    rm -f "$other"
    if ln -s "$(basename "$realfile")" "$other" 2>/dev/null; then
        log "kernel: $(basename "$other") -> $(basename "$realfile") (shared kernel — interchangeable Claude Code / Prime Agent)"
    else
        cp "$seed_kernel" "$other"
        warn "symlink unavailable; placing $(basename "$other") as an independent kernel copy (may drift on edit)"
    fi
}
# place_tree SRC_DIR DEST_DIR [PATTERN]
# Mirrors every file matching PATTERN (default *) from SRC_DIR into
# DEST_DIR by calling place_file for each.
place_tree() {
    local src="$1" dest="$2" pattern="${3:-*}"
    [[ -d "$src" ]] || die "missing source dir: $src"
    mkdir -p "$dest"
    local f
    while IFS= read -r -d '' f; do
        local rel="${f#"$src"/}"   # quoted: an unquoted $src is a glob pattern
        place_file "$f" "$dest/$rel"
    done < <(find "$src" -type f -name "$pattern" -print0)
}

# place_docs_skeleton: install every knowledge artifact beneath the one
# docs/graph/ root. Plant-authored content is preserved: scaffold files
# and template leaves are added only when missing. The seed-owned
# machinery subtrees (protocols/skills/agents/method/templates) are
# fast-forwarded to the current seed — identical files untouched,
# changed files backed up (unless --force) for graft-audit to inspect.
place_docs_skeleton() {
    place_graph_scaffold
    place_graph_machinery
    local src="$SEED_ROOT/templates/docs" dest="$PROJECT_DIR/docs/graph" f rel
    log "populating missing unified-graph leaves in docs/graph/"
    while IFS= read -r -d '' f; do
        rel="${f#"$src"/}"         # quoted: an unquoted $src is a glob pattern
        if [[ ! -e "$dest/$rel" && ! -L "$dest/$rel" ]]; then
            mkdir -p "$(dirname "$dest/$rel")"
            cp "$f" "$dest/$rel"
        fi
    done < <(find "$src" -type f -print0)
}

# place_graph_machinery: the seed's method surface — protocols, skills
# (flattened <name>.md), agents, method/posture nodes, and the Tier-3
# template artifacts — lives INSIDE the graph as seed-owned routable
# nodes (kind protocol/skill/agent/method, origin: seed). This is the
# single home; any tool-dir copies are harness projections of it.
place_graph_machinery() {
    local g="$PROJECT_DIR/docs/graph"
    log "installing the method surface into docs/graph/ (protocols, skills, agents, method, templates)"
    place_tree "$SEED_ROOT/protocols"   "$g/protocols" "*.md"
    place_tree "$SEED_ROOT/core/method" "$g/method"    "*.md"
    place_tree "$SEED_ROOT/agents"      "$g/agents"    "*.md"
    # the golden routing corpus rides with the roster so the kernel-
    # mandated router can run --eval (a graft exit gate) on EVERY harness,
    # not only where .claude/agents/ exists
    place_file "$SEED_ROOT/agents/_routes.golden.tsv" "$g/agents/_routes.golden.tsv"
    local d name
    for d in "$SEED_ROOT/skills"/*/; do
        name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$g/skills/$name.md"
    done
    place_tree "$SEED_ROOT/templates" "$g/templates"
}

# place_graph_scaffold: drop the knowledge-graph home (schema, linter,
# router index, empty nodes/) into docs/graph/. Add missing files only.
place_graph_scaffold() {
    local g="$PROJECT_DIR/docs/graph"
    log "ensuring unified knowledge graph in docs/graph/"
    mkdir -p "$g/nodes"
    [[ -e "$g/_schema.md" ]] || cp "$SEED_ROOT/templates/knowledge-graph/_schema.md" "$g/_schema.md"
    [[ -e "$g/graph-lint.py" ]] || cp "$SEED_ROOT/templates/knowledge-graph/graph-lint.py" "$g/graph-lint.py"
    [[ -e "$g/spec-lint.py" ]] || cp "$SEED_ROOT/templates/knowledge-graph/spec-lint.py" "$g/spec-lint.py"
    # the agent router is kernel-mandated on EVERY harness ("python3
    # docs/graph/agent-lint.py --route"); claude-code additionally projects
    # it to .claude/agent-lint.py. Unlike the graph engines (add-if-missing,
    # reconciled by graft-graph-engine.py), the router carries NO project
    # config, so it fast-forwards like machinery: identical -> untouched,
    # changed -> backed up and replaced (graft-audit inspects the backup).
    place_file "$SEED_ROOT/integrations/claude-code/agent-lint.py" "$g/agent-lint.py"
    [[ -e "$g/index.md" ]] || cp "$SEED_ROOT/templates/knowledge-graph/index.md" "$g/index.md"
    log "  run /initialize to discover the project and grow the graph"
}

# command_protocols: print the basename of every protocol node that
# declares `command: true` in its frontmatter — the single home for
# "which protocols are user-facing slash commands." The user-sovereign
# meta-loop (graft/grow/harvest) and canonize-folded toolcraft carry no
# such field, so they are commands in no harness.
command_protocols() {
    local f name
    for f in "$SEED_ROOT/protocols"/*.md; do
        name="$(basename "$f" .md)"
        if awk '/^---$/{c++; next} c==1 && /^command:[[:space:]]*true[[:space:]]*$/{found=1} c>=2{exit} END{exit !found}' "$f"; then
            printf '%s\n' "$name"
        fi
    done
}

# generate_slash_commands DEST_DIR
# Emit one thin slash-command file per command-protocol. Each command is a
# pure PROJECTION of its protocol node: it routes the session into
# docs/graph/protocols/<name>.md, which owns the full discipline. No command
# content is authored outside the graph — the node is the single home.
generate_slash_commands() {
    local dest="$1" name
    mkdir -p "$dest"
    while IFS= read -r name; do
        cat > "$dest/$name.md" <<EOF
---
description: Enter the \`$name\` protocol. See docs/graph/protocols/$name.md for the full discipline.
---

<!-- GENERATED from protocols/$name.md by install.sh — do not edit here; edit the node and re-run. -->

Enter the **$name** protocol. Read \`docs/graph/protocols/$name.md\` and follow
its discipline for the current task.

Before acting, state which protocol you are entering and confirm its entry
conditions are met; if they are not, back up to the protocol that produces the
missing inputs. Then run the protocol, and end the session with
\`docs/graph/protocols/deliver.md\`.
EOF
    done < <(command_protocols)
}

# --- per-tool installers --------------------------------------------

install_claude_code() {
    log "installing for Claude Code in $PROJECT_DIR"
    place_kernel "$PROJECT_DIR/CLAUDE.md"
    # Harness PROJECTIONS only — the home of agents and skills is
    # docs/graph/{agents,skills}/ (place_graph_machinery); these copies
    # exist because the harness spawns agents and loads skills from
    # fixed locations. Protocols, templates, method/posture nodes have
    # no harness location and are graph-only.
    place_tree "$SEED_ROOT/agents"      "$PROJECT_DIR/.claude/agents"      "*.md"
    # The golden routing corpus is a peer of the agent defs (not a *.md, so
    # place_tree skips it); agent-lint.py --eval loads it from .claude/agents/.
    place_file "$SEED_ROOT/agents/_routes.golden.tsv" \
               "$PROJECT_DIR/.claude/agents/_routes.golden.tsv"
    for d in "$SEED_ROOT/skills"/*/; do
        local name; name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$PROJECT_DIR/.claude/skills/$name/SKILL.md"
    done
    # Slash commands — generated projections of the command-protocol nodes
    # (those declaring `command: true`). No authored command tree; the node
    # is the single home, the command routes into it.
    generate_slash_commands "$PROJECT_DIR/.claude/commands"
    # Settings file is copied (so the project can edit it).
    cp "$SEED_ROOT/integrations/claude-code/settings.json" \
       "$PROJECT_DIR/.claude/settings.json"
    # Progressive-discovery enforcement hook (referenced by settings.json).
    cp "$SEED_ROOT/integrations/claude-code/route-hook.py" \
       "$PROJECT_DIR/.claude/route-hook.py"
    # Mechanical agent-router / roster linter / eval gate, invoked as
    # `python3 .claude/agent-lint.py` by 00-orchestrator.md, the brief
    # templates, and the deliver assertion. Scores .claude/agents/.
    cp "$SEED_ROOT/integrations/claude-code/agent-lint.py" \
       "$PROJECT_DIR/.claude/agent-lint.py"
    place_docs_skeleton
    log "Claude Code install done."
    log "  CLAUDE.md             -> core/AGENTS.md (bootstrap kernel)"
    log "  docs/graph/           -> the ONE knowledge system: method surface"
    log "                           (protocols, skills, agents, method, templates) + project graph"
    log "  .claude/agents/       (harness projection of docs/graph/agents/)"
    log "  .claude/skills/       (harness projection of docs/graph/skills/)"
    log "  .claude/commands/     (tool-specific slash commands)"
    log "  .claude/settings.json (commit to share with team)"
    log_registration_notice ".claude/agents/"
}

install_opencode() {
    log "installing for opencode in $PROJECT_DIR"
    place_kernel "$PROJECT_DIR/AGENTS.md"   # NOT raw place_file: the kernel
    # may already be the CLAUDE.md-shared file; bypassing place_kernel made
    # this call and prime-agent's ping-pong the file into fresh .bak churn
    # on every re-run
    # Harness projections of docs/graph/{agents,skills}/ (the home).
    place_tree "$SEED_ROOT/agents"    "$PROJECT_DIR/.opencode/agents"    "*.md"
    for d in "$SEED_ROOT/skills"/*/; do
        local name; name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$PROJECT_DIR/.opencode/skills/$name/SKILL.md"
    done
    # Slash commands — the same generated projections as every other harness.
    generate_slash_commands "$PROJECT_DIR/.opencode/commands"
    # ONE config file only. opencode reads opencode.json OR opencode.jsonc and
    # the precedence between two files at the same tier is unspecified — the
    # seed shipped both and let the harness pick. Strict JSON is also the form
    # tests/seed-lint.py and tests/test-full-install.sh can parse; the rationale
    # for what this file does NOT declare lives in integrations/opencode/README.md.
    cp "$SEED_ROOT/integrations/opencode/opencode.json" \
       "$PROJECT_DIR/opencode.json"
    place_docs_skeleton
    log "opencode install done."
    log "  AGENTS.md             -> core/AGENTS.md (bootstrap kernel)"
    log "  docs/graph/           -> the ONE knowledge system (method surface + project graph)"
    log "  .opencode/agents/     (harness projection of docs/graph/agents/)"
    log "  .opencode/skills/     (harness projection of docs/graph/skills/)"
    log "  .opencode/commands/   (tool-specific slash commands)"
    log "  opencode.json         (commit to share with team)"
    log_registration_notice ".opencode/agents/"
}

install_codex() {
    log "installing for Codex CLI in $PROJECT_DIR"
    place_kernel "$PROJECT_DIR/AGENTS.md"   # NOT raw place_file: the kernel
    # may already be the CLAUDE.md-shared file; bypassing place_kernel made
    # this call and prime-agent's ping-pong the file into fresh .bak churn
    # on every re-run
    # Harness projections of docs/graph/{agents,skills}/ (the home).
    place_tree "$SEED_ROOT/agents"    "$PROJECT_DIR/.codex/agents"    "*.md"
    for d in "$SEED_ROOT/skills"/*/; do
        local name; name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$PROJECT_DIR/.codex/skills/$name/SKILL.md"
    done
    place_docs_skeleton

    # Generate config snippet with resolved paths
    local snippet="$PROJECT_DIR/.codex/codex-config-snippet.toml"
    sed "s|/abs/path/to/project|$PROJECT_DIR|g" \
        "$SEED_ROOT/integrations/codex/config.toml.example" > "$snippet"
    log "Codex install done."
    log "  AGENTS.md            -> core/AGENTS.md (bootstrap kernel)"
    log "  docs/graph/          -> the ONE knowledge system (method surface + project graph)"
    log "  .codex/agents/       (harness projection of docs/graph/agents/)"
    log "  .codex/skills/       (harness projection of docs/graph/skills/)"
    log ""
    log "ACTION NEEDED: merge this snippet into ~/.codex/config.toml:"
    log "  $snippet"
    if [[ $PRINT_CONFIG -eq 1 ]]; then
        echo "----- BEGIN ~/.codex/config.toml additions -----"
        cat "$snippet"
        echo "----- END -----"
    fi
    log_registration_notice ".codex/agents/"
}

install_github_copilot() {
    log "installing for GitHub Copilot in $PROJECT_DIR"
    # Repo-root kernel — Copilot reads both .github/copilot-instructions.md AND AGENTS.md.
    # place_file, not cp: a raw cp onto an existing symlink writes THROUGH it
    # and clobbers the target file; place_file's backup mv takes the link itself.
    mkdir -p "$PROJECT_DIR/.github"
    place_file "$SEED_ROOT/core/AGENTS.md" "$PROJECT_DIR/.github/copilot-instructions.md"
    place_kernel "$PROJECT_DIR/AGENTS.md"   # NOT raw place_file: the kernel
    # may already be the CLAUDE.md-shared file; bypassing place_kernel made
    # this call and prime-agent's ping-pong the file into fresh .bak churn
    # on every re-run

    # Agents -> .github/agents/<name>.agent.md (transformed frontmatter)
    mkdir -p "$PROJECT_DIR/.github/agents"
    for f in "$SEED_ROOT/agents"/*.md; do
        local name; name="$(basename "$f" .md | sed -E 's/^[0-9]+-//')"
        # Strip the universal frontmatter; rewrite for Copilot.
        python3 - "$f" "$PROJECT_DIR/.github/agents/$name.agent.md" <<'PYEOF'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    open(dst, "w").write(text); sys.exit(0)
fm = m.group(1)
body = text[m.end():]
desc = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.S | re.M)
description = (desc.group(1).strip() if desc else "").replace("\n", " ").strip()
# Per-agent tool mapping — the source frontmatter's tools: allowlist IS the
# discipline; projecting one fixed superset (the old behavior) silently gave
# read-only agents editFiles/runCommands on Copilot.
tm = re.search(r"^tools:\s*\[([^\]]*)\]", fm, re.M)
src_tools = {t.strip() for t in (tm.group(1).split(",") if tm else []) if t.strip()}
# read set + runCommands always: the GRAPH DISCIPLINE bootstrap mandates
# `python3 docs/graph/graph-lint.py --plan` / agent-lint --route in EVERY
# session, so command execution is a baseline capability on Copilot even for
# Bash-less charters. Write access (editFiles) and web reach (fetch,
# githubRepo — a REMOTE GitHub search, not local) stay allowlist-derived;
# runTasks (workspace task runner) requires Bash. `Task` (subagent spawning)
# has no Copilot equivalent and is not projected.
cop = ["codebase", "search", "usages", "findTestFiles", "runCommands"]
if src_tools & {"Write", "Edit"}:
    cop.append("editFiles")
if "Bash" in src_tools:
    cop.append("runTasks")
if src_tools & {"WebSearch", "WebFetch"}:
    cop += ["fetch", "githubRepo"]
tools_line = "tools: [" + ", ".join(f"'{t}'" for t in cop) + "]"
out = (
    "---\n"
    f"description: {description}\n"
    f"{tools_line}\n"
    "---\n\n"
    f"<!-- GENERATED from {src.rsplit('/', 1)[-1]} by install.sh github-copilot — do not edit here; edit the seed source and re-run. -->\n\n"
) + body
open(dst, "w").write(out)
PYEOF
    done

    # Protocols -> .github/prompts/<name>.prompt.md, one per command-protocol
    # (frontmatter `command: true`). The user-sovereign meta-loop protocols
    # (graft/grow/harvest) and the canonize-folded toolcraft carry no command
    # field, so they are not exposed as Copilot prompts either; the command
    # surface a user sees is the same on every harness.
    mkdir -p "$PROJECT_DIR/.github/prompts"
    local name f
    while IFS= read -r name; do
        f="$SEED_ROOT/protocols/$name.md"
        python3 - "$f" "$PROJECT_DIR/.github/prompts/$name.prompt.md" <<'PYEOF'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
fm = m.group(1) if m else ""
body = text[m.end():] if m else text
desc = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.S | re.M)
description = (desc.group(1).strip() if desc else "").replace("\n", " ").strip()
out = (
    "---\n"
    "mode: 'agent'\n"
    f"description: {description}\n"
    "tools: ['codebase', 'editFiles', 'fetch', 'findTestFiles', "
    "'githubRepo', 'search', 'usages', 'runCommands']\n"
    "---\n\n"
    f"<!-- GENERATED from {src.rsplit('/', 1)[-1]} by install.sh github-copilot — do not edit here; edit the seed source and re-run. -->\n\n"
) + body
open(dst, "w").write(out)
PYEOF
    done < <(command_protocols)

    # Skills -> .github/instructions/<name>-skill.instructions.md
    mkdir -p "$PROJECT_DIR/.github/instructions"
    for d in "$SEED_ROOT/skills"/*/; do
        local name; name="$(basename "$d")"
        python3 - "${d%/}/SKILL.md" "$PROJECT_DIR/.github/instructions/$name-skill.instructions.md" <<'PYEOF'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
fm = m.group(1) if m else ""
body = text[m.end():] if m else text
desc = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", fm, re.S | re.M)
description = (desc.group(1).strip() if desc else "").replace("\n", " ").strip()
out = (
    "---\n"
    f"description: {description}\n"
    "applyTo: '**'\n"
    "---\n\n"
    f"<!-- GENERATED from {src.rsplit('/', 1)[-1]} by install.sh github-copilot — do not edit here; edit the seed source and re-run. -->\n\n"
) + body
open(dst, "w").write(out)
PYEOF
    done

    # Progressive-discovery enforcement hook for VS Code Agent Hooks
    # (Preview). VS Code also reads .claude/settings.json hooks, so only
    # install the .github/hooks/ config when the Claude Code hook is
    # absent — otherwise the hook would fire twice.
    if [[ -f "$PROJECT_DIR/.claude/settings.json" ]]; then
        log "  (skipping .github/hooks/ — .claude/settings.json already carries the hook, which VS Code reads)"
    else
        mkdir -p "$PROJECT_DIR/.github/hooks"
        cp "$SEED_ROOT/integrations/claude-code/route-hook.py" \
           "$PROJECT_DIR/.github/hooks/route-hook.py"
        cp "$SEED_ROOT/integrations/github-copilot/hooks/route.json" \
           "$PROJECT_DIR/.github/hooks/route.json"
        log "  .github/hooks/route.json + route-hook.py (enforce progressive discovery)"
    fi

    place_docs_skeleton
    log "GitHub Copilot install done."
    log "  .github/copilot-instructions.md       (bootstrap kernel)"
    log "  AGENTS.md                              (kernel mirror)"
    log "  docs/graph/                            (the ONE knowledge system: method surface + project graph)"
    log "  .github/agents/<name>.agent.md         (harness projection, transformed from docs/graph/agents/)"
    log "  .github/prompts/<name>.prompt.md       (harness projection, transformed from docs/graph/protocols/)"
    log "  .github/instructions/<name>-skill.*    (harness projection, transformed from docs/graph/skills/)"
    log_registration_notice ".github/agents/"
}


install_prime_agent() {
    log "installing for Prime Agent in $PROJECT_DIR"
    # Kernel — Prime Agent auto-loads AGENTS.md (or CLAUDE.md) from the repo
    # root (AGENTS.md wins in a directory). place_kernel shares ONE kernel file
    # with a co-installed Claude Code (CLAUDE.md), so a single plant runs both
    # harnesses interchangeably off byte-identical project instructions.
    place_kernel "$PROJECT_DIR/AGENTS.md"
    # Roster BRIEF SOURCES. Prime Agent has NO static roster enumerated at
    # session start; delegation is a runtime rlm() spawn with an inline brief.
    # So agents/*.md land as on-disk brief sources the orchestrator reads and
    # embeds into rlm() calls. The golden routing corpus rides along (place_tree
    # skips the non-*.md file) so agent-lint.py can score the roster in CI —
    # the SAME gate claude-code runs, pointed at this dir (full parity).
    place_tree "$SEED_ROOT/agents"      "$PROJECT_DIR/.prime/agent/agents"      "*.md"
    place_file "$SEED_ROOT/agents/_routes.golden.tsv" \
               "$PROJECT_DIR/.prime/agent/agents/_routes.golden.tsv"
    # Skills — the same Agent-Skills SKILL.md the seed ships, no transform.
    local d name
    for d in "$SEED_ROOT/skills"/*/; do
        name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$PROJECT_DIR/.prime/agent/skills/$name/SKILL.md"
    done
    # Slash commands — generated prompt-template projections of the
    # command-protocol nodes, the same roster as every other harness.
    generate_slash_commands "$PROJECT_DIR/.prime/agent/prompts"
    # Progressive-discovery enforcement extension (before_agent_start) — the
    # Prime Agent parity of claude-code's route-hook.py. Copied so it is editable.
    mkdir -p "$PROJECT_DIR/.prime/agent/extensions"
    cp "$SEED_ROOT/integrations/prime-agent/route-extension.ts" \
       "$PROJECT_DIR/.prime/agent/extensions/route-extension.ts"
    # Settings — copied (so the project can edit it).
    cp "$SEED_ROOT/integrations/prime-agent/settings.json" \
       "$PROJECT_DIR/.prime/agent/settings.json"
    # Native-execution overlay — APPENDED to Prime Agent's system prompt every
    # session (Claude Code never reads it). Teaches the model to run the seed's
    # discipline with Prime Agent's RLM-native primitives (recursive rlm()
    # subagents, the continual harness, agent_message handbacks, in-kernel gates)
    # instead of emulating a file-based harness. Copied so the project can edit it.
    cp "$SEED_ROOT/integrations/prime-agent/APPEND_SYSTEM.md" \
       "$PROJECT_DIR/.prime/agent/APPEND_SYSTEM.md"
    place_docs_skeleton
    log "Prime Agent install done."
    log "  AGENTS.md                  -> core/AGENTS.md (bootstrap kernel, auto-loaded)"
    log "  docs/graph/                -> the ONE knowledge system: method surface + project graph"
    log "  .prime/agent/agents/       (roster BRIEF SOURCES — read one, spawn an rlm() child with it)"
    log "  .prime/agent/skills/       (harness projection of docs/graph/skills/)"
    log "  .prime/agent/prompts/      (slash-command prompt templates)"
    log "  .prime/agent/extensions/   (route-extension.ts — progressive-discovery enforcement)"
    log "  .prime/agent/settings.json (commit to share with team)"
    log "  .prime/agent/APPEND_SYSTEM.md (RLM-native execution overlay — appended to the system prompt)"
    # Unlike claude-code/opencode, Prime Agent does NOT enumerate a roster at
    # session start, so there is no "installed but not spawnable" lag here: a
    # brief written to .prime/agent/agents/ is usable by the very next rlm()
    # call in the same session. One home for the rule and why it does not bite
    # here: core/method/delegation.md (delegation.harness-registration).
    log ""
    log "NOTE: no roster-registration restart is needed on Prime Agent — the"
    log "  briefs in .prime/agent/agents/ are usable IMMEDIATELY by rlm()"
    log "  (docs/graph/method/delegation.md, delegation.harness-registration)."
}

# --- args ------------------------------------------------------------

usage() {
    sed -n '/^# install.sh/,/^$/p' "$0" | sed -E 's/^# ?//'
    exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        claude-code|opencode|codex|github-copilot|prime-agent|all) TOOLS+=("$1"); shift ;;
        --project-dir) PROJECT_DIR="$(cd "$2" && pwd)"; shift 2 ;;
        --symlink) LINK_MODE="symlink"; shift ;;
        --copy)    LINK_MODE="copy";    shift ;;
        --force)   FORCE=1; shift ;;
        --print-config) PRINT_CONFIG=1; shift ;;
        --check)   CHECK=1; shift ;;
        -h|--help) usage 0 ;;
        *) die "unknown argument: $1 (try --help)" ;;
    esac
done

[[ ${#TOOLS[@]} -gt 0 ]] || die "no tool specified (try --help)"

# Sanity: refuse to install into the seed itself.
[[ "$PROJECT_DIR" != "$SEED_ROOT" ]] || die \
    "refusing to install the seed system into itself; pass --project-dir"

# Expand 'all'
expanded=()
for t in "${TOOLS[@]}"; do
    case "$t" in
        all) expanded+=(claude-code opencode codex github-copilot prime-agent) ;;
        *)   expanded+=("$t") ;;
    esac
done

# --check: verify generated views are in sync, write nothing. Only the
# github-copilot views are generated (transformed) rather than symlinked,
# so they are the only ones that can drift; the others are safe by
# construction. Regenerate to a temp dir and diff.
if [[ ${CHECK:-0} -eq 1 ]]; then
    stale=0
    for tool in "${expanded[@]}"; do
        [[ "$tool" == "github-copilot" ]] || continue
        tmp="$(mktemp -d)"; orig="$PROJECT_DIR"
        # Reproduce the target's multi-tool hook state. Copilot installation
        # intentionally omits .github/hooks when Claude's settings already
        # provide the same VS Code-compatible hook; an empty temp directory
        # otherwise generates hooks that can never match the real target.
        if [[ -f "$orig/.claude/settings.json" ]]; then
            mkdir -p "$tmp/.claude"
            : > "$tmp/.claude/settings.json"
        fi
        PROJECT_DIR="$tmp"; FORCE=1
        install_github_copilot >/dev/null 2>&1 || true
        PROJECT_DIR="$orig"
        if diff -rq "$tmp/.github" "$orig/.github" >/dev/null 2>&1 \
           && diff -q "$tmp/AGENTS.md" "$orig/AGENTS.md" >/dev/null 2>&1; then
            log "Copilot views up to date."
        else
            warn "Copilot views are STALE — re-run: install.sh github-copilot --force"
            stale=1
        fi
        rm -rf "$tmp"
    done
    exit $stale
fi

for tool in "${expanded[@]}"; do
    case "$tool" in
        claude-code)    install_claude_code ;;
        opencode)       install_opencode ;;
        codex)          install_codex ;;
        github-copilot) install_github_copilot ;;
        prime-agent)    install_prime_agent ;;
        *)              die "unknown tool: $tool" ;;
    esac
done

# Keep the canonical tool-neutral entry discoverable from the installed
# project. This is orchestration control, not project knowledge; maintained
# project facts still live exclusively below docs/graph/.
place_file "$SEED_ROOT/INSTALL_PROMPT.md" "$PROJECT_DIR/EXPERT_SEED_INSTALL_PROMPT.md"

log "done. FILES ARE PLACED — the project is NOT grown yet."
log ""
log "Next step (the HAND OFF phase): open a NEW agent-capable chat ROOTED AT the"
log "target directory (never the seed — the roster registers at session start,"
log "see delegation.harness-registration) and paste the one entry prompt from:"
log ""
log "    $PROJECT_DIR/EXPERT_SEED_INSTALL_PROMPT.md"
log ""
log "That prompt drives the GROW IN FULL phase: Sonnet-class scouts and"
log "Opus-class authors execute docs/graph/protocols/grow.md end to end under"
log "its completeness contract (grow.completeness-contract) — every"
log "evidence-backed node and leaf, not a skeleton. /initialize is only a"
log "coding-tool adapter to the same flow."
