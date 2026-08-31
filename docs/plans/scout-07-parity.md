# Scout-07: Seed-Side Parity Audit — Claude Code First-Class + Gate Question

**Scope:** READ-ONLY research into what makes claude-code first-class in the CYPRESS seed
and the exact answer to the gate question for prime-agent CI parity.

**Date:** 2026-08-29  
**Author:** scout-07 (sonnet-4.6 sub-agent)

---

## 1. What Makes Claude Code First-Class

Seven concrete artifacts beyond documentation make claude-code first-class. No other
integration (opencode, codex, github-copilot, prime-agent) has all seven.

### 1.1 Mechanical gate binary: `agent-lint.py`

**Source:** `integrations/claude-code/agent-lint.py` (19 626 bytes)  
**Install target:** `.claude/agent-lint.py` (placed by `install.sh:install_claude_code()`)

Three modes:

| Mode | Purpose | Exit code |
|------|---------|-----------|
| `--lint [--dir PATH]` | Validate every agent's frontmatter: `routing_triggers` present; `can_delegate == (Task in tools)`; bounded-delegation depth/allowlist invariant | 0 ok / 1 error / 2 fatal |
| `--eval [--dir PATH]` | Run `_routes.golden.tsv` against the roster; assert top-1 accuracy ≥ 90 % and all `LOW`-labeled rows return LOW/NONE | 0 ok / 1 fail / 2 fatal |
| `--route "TASK" [--dir PATH]` | IDF-weighted rank; print confidence band HIGH/MEDIUM/LOW/NONE | 0 |

**Key code fact** (`agent-lint.py:main()`, lines ~340-360):

```python
if args.dir:
    adir = Path(args.dir)      # NO .claude path assumption — bypasses find_agents_dir()
    ...
else:
    adir = find_agents_dir()   # walks up looking for .claude/agents/ ONLY in this branch
```

`find_agents_dir()` is the **only place** `.claude/agents/` is hardcoded
(`AGENTS_REL = Path(".claude") / "agents"`, line ~21). When `--dir` is passed the
`.claude` assumption is completely bypassed. `load_agents(adir)` just globs `adir/*.md`;
`cmd_eval` looks for `adir/_routes.golden.tsv`. Any directory of properly-formatted
`*.md` files + golden `.tsv` works identically.

### 1.2 Seed-side CI gates in `tests/run.sh`

Lines 13–14 of `tests/run.sh`:

```bash
python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint --dir "$ROOT/agents"
python3 "$ROOT/integrations/claude-code/agent-lint.py" --eval --dir "$ROOT/agents"
```

These run the SEED's own `agents/` directory (not a `.claude/` projection). They
are the P0 and eval gates that fail the entire CI suite if any agent's frontmatter
is malformed or the routing accuracy drops below 90 %.

### 1.3 In-plant install verification: `tests/test-full-install.sh`

After running `install.sh claude-code` into a temp dir, this script:

```bash
need "$T/.claude/agent-lint.py" claude-code          # gate binary is installed
python3 "$T/.claude/agent-lint.py" --lint >/dev/null # roster valid in-plant
cmp -s "$ROOT/agents/_routes.golden.tsv"        "$T/.claude/agents/_routes.golden.tsv"         # golden corpus not drifted
```

No other integration runs an analogous in-plant lint gate. opencode/codex/github-copilot
sections only check file presence.

### 1.4 Full behavioral test suite: `tests/test_agent_lint.py`

37-test pytest suite (33 780 bytes) covering `--route`, `--lint`, `--eval`, confidence
bands, IDF scoring, frontmatter parser edge cases, and golden corpus shape. Run
conditionally in `run.sh` (requires pytest; loud skip, not silent).

### 1.5 Native hook: `integrations/claude-code/settings.json` + `route-hook.py`

```json
"hooks": {
  "UserPromptSubmit": [{
    "hooks": [{ "type": "command",
      "command": "python3 "${CLAUDE_PROJECT_DIR:-$PWD}/.claude/route-hook.py" || true" }]
  }]
}
```

`route-hook.py` runs `graph-lint.py --plan` on every prompt and injects the
progressive-discovery mandate + router suggestion as `additionalContext`. This is a
**native harness hook**, not a skill or instruction. VS Code Copilot also reads this
settings file (shared hook), but only claude-code treats it as authoritative.

### 1.6 `install.sh` `install_claude_code()` function

Places 8 artifact types:
- `CLAUDE.md` → `core/AGENTS.md`
- `.claude/agents/*.md` (harness projection of `agents/`)
- `.claude/agents/_routes.golden.tsv` (routing corpus, placed separately)
- `.claude/skills/<name>/SKILL.md`
- `.claude/commands/*.md` (generated slash commands, one per `command: true` protocol)
- `.claude/settings.json` (hooks + directories config)
- `.claude/route-hook.py` (progressive discovery enforcement)
- `.claude/agent-lint.py` (mechanical router gate)

No other integration places a gate binary or a golden corpus projection.

### 1.7 `manifest.json` entries

```json
"agent_router": {
  "tool": "integrations/claude-code/agent-lint.py",
  "installed_at": ".claude/agent-lint.py",
  "golden_set_installed_at": ".claude/agents/_routes.golden.tsv",
  ...
}
```

plus an `integrations` array entry `{"tool": "claude-code", ...}`. prime-agent
currently appears in **neither** block.

---

## 2. Prime-Agent Current State (Gap Inventory)

| Artifact | claude-code | prime-agent |
|----------|-------------|-------------|
| `integrations/<tool>/README.md` | ✓ | ✓ (exists) |
| `install.sh` function | ✓ `install_claude_code()` | ✗ missing |
| `manifest.json` integrations entry | ✓ | ✗ missing |
| `manifest.json` agent_router entry | ✓ | ✗ no separate entry needed (shared) |
| run.sh seed-side lint gate | ✓ (shared `--dir agents/`) | ✓ (already shared) |
| run.sh seed-side eval gate | ✓ (shared `--dir agents/`) | ✓ (already shared) |
| test-full-install.sh in-plant section | ✓ | ✗ missing |
| hook / enforcement mechanism | `.claude/settings.json` + `route-hook.py` | `route-extension.ts` (described in README, not yet shipped in seed) |
| Golden corpus installed to tool dir | `.claude/agents/_routes.golden.tsv` | ✗ needs `.prime/agent/agents/_routes.golden.tsv` |

### 2.1 prime-agent architecture note

prime-agent has **no static session-start agent roster**. From `dist/core/resource-loader.js`
and `dist/config.js`:

- `getAgentDir()` → `~/.prime/agent/` (not a session registry of spawnable agents)
- `loadProjectContextFiles()` loads `AGENTS.md` / `CLAUDE.md` — the kernel, not a roster
- Skills: `~/.prime/agent/skills/`, `.prime/agent/skills/`, `~/.agents/skills/`, `.agents/skills/`
- Prompts: `~/.prime/agent/prompts/`, `.prime/agent/prompts/`
- Extensions: `~/.prime/agent/extensions/`, `.prime/agent/extensions/`
- **No `agents/` discovery in any source file** — there is no harness-level enumeration of `.prime/agent/agents/`

The seed's `agents/*.md` installed to `.prime/agent/agents/*.md` are **brief sources**
(the orchestrator reads them and passes them into `rlm()` calls). This is documented
correctly in `integrations/prime-agent/README.md`. It is not a gap in the README — it is
a fundamental architectural difference.

### 2.2 Extension event confirmed

`dist/core/extensions/types.d.ts` line 503: `before_agent_start` event fires
"after user submits prompt but before agent loop." `BeforeAgentStartEventResult`
(line 741) supports `message` injection and `systemPrompt` replacement — equivalent
to claude-code's `additionalContext` hook output. The `route-extension.ts` described
in the README can be built against this verified API.

---

## 3. The Gate Question — Answer

### 3.1 Question

> agent-lint.py lints a STATIC roster (`.claude/agents/*.md`) and scores routing over
> `agents/_routes.golden.tsv`. prime-agent has no static session-start roster.
> What is the RIGHT prime-agent parity for this GATE?
>
> (a) Point the SAME agent-lint.py `--dir` at installed `.prime/agent/agents/*.md`?
> (b) prime-agent-specific validator?

### 3.2 Answer: Option (a) — point the SAME `agent-lint.py --dir` at `.prime/agent/agents/`

**Reasoning:**

1. **Code supports it with zero changes.** The `--dir` flag fully bypasses the
   `.claude/agents/` assumption (verified in `agent-lint.py:main()` lines ~340-360
   above). Any directory of `*.md` files with the frontmatter schema works.

2. **Same check = true parity.** A separate validator would test different things and
   create a lower bar. Using the same binary with `--dir` means the same frontmatter
   rules, the same routing accuracy threshold (90 %), and the same novel-stack LOW-guard.

3. **The brief-source nature is not an obstacle.** The agents in `.prime/agent/agents/*.md`
   ARE static `.md` files on disk with YAML frontmatter. agent-lint.py does not care
   that prime-agent doesn't enumerate them at session start — it only cares that the
   files have valid frontmatter and their routing_triggers score correctly.

4. **Seed-side gates already shared.** `run.sh` lines 13-14 run `--lint` and `--eval`
   against `$ROOT/agents/` — the upstream source. Both integrations use this shared
   gate. No new seed-side run.sh line is needed.

5. **The only missing piece is the plant-side gate** in `test-full-install.sh`: verify
   that `install.sh prime-agent` places the agents, copies the golden corpus, and that
   `--lint` passes in-plant.

### 3.3 Exact wiring for parity

**`install.sh` — add `install_prime_agent()` function:**

```bash
install_prime_agent() {
    log "installing for Prime Agent in $PROJECT_DIR"
    place_file "$SEED_ROOT/core/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
    # Harness projections (brief sources — orchestrator reads, passes into rlm())
    place_tree "$SEED_ROOT/agents" "$PROJECT_DIR/.prime/agent/agents" "*.md"
    place_file "$SEED_ROOT/agents/_routes.golden.tsv"                "$PROJECT_DIR/.prime/agent/agents/_routes.golden.tsv"
    for d in "$SEED_ROOT/skills"/*/; do
        local name; name="$(basename "$d")"
        place_file "${d%/}/SKILL.md" "$PROJECT_DIR/.prime/agent/skills/$name/SKILL.md"
    done
    # Slash commands — same generated projections as other harnesses
    generate_slash_commands "$PROJECT_DIR/.prime/agent/prompts"
    # Settings file and progressive-discovery extension
    cp "$SEED_ROOT/integrations/prime-agent/settings.json"        "$PROJECT_DIR/.prime/agent/settings.json"
    cp "$SEED_ROOT/integrations/prime-agent/route-extension.ts"        "$PROJECT_DIR/.prime/agent/extensions/route-extension.ts"
    place_docs_skeleton
    log "Prime Agent install done."
    log_registration_notice ".prime/agent/agents/ (brief sources — spawn via rlm())"
}
```

Also add `prime-agent` to the `TOOLS` argument parser and the `all` expansion.

**`tests/test-full-install.sh` — add prime-agent section (after opencode section):**

```bash
"$ROOT/install.sh" prime-agent --project-dir "$T" --copy --force >/dev/null
need "$T/AGENTS.md" prime-agent
need "$T/.prime/agent/agents/00-orchestrator.md" prime-agent
need "$T/.prime/agent/agents/_routes.golden.tsv" prime-agent
need "$T/.prime/agent/skills/context-router/SKILL.md" prime-agent
need "$T/.prime/agent/prompts/recover.md" prime-agent
[[ ! -e "$T/.prime/agent/protocols" ]] || { echo "STALE .prime/agent/protocols" >&2; exit 1; }
[[ ! -e "$T/.prime/agent/templates" ]] || { echo "STALE .prime/agent/templates" >&2; exit 1; }
# THE GATE: agent-lint.py --dir works with no code change; golden must not drift
python3 "$ROOT/integrations/claude-code/agent-lint.py" --lint     --dir "$T/.prime/agent/agents" >/dev/null
cmp -s "$ROOT/agents/_routes.golden.tsv"        "$T/.prime/agent/agents/_routes.golden.tsv"     || { echo "golden routing corpus drifted: prime-agent projection" >&2; exit 1; }
assert_cmd_roster "$T/.prime/agent/prompts" .md "prime-agent prompts"
```

**`run.sh` — no new lines needed.** The existing lines 13-14 (`--lint` + `--eval`
against `$ROOT/agents/`) already serve as the shared seed-side gate for all integrations
including prime-agent. Do NOT add a duplicate prime-agent-specific run.sh line; that
would run the same check twice and give a false impression of separate validation.

**`manifest.json`:**

```json
{
  "integrations": [
    ...existing entries...,
    {"tool": "prime-agent", "dir": "integrations/prime-agent/", "method": "symlink + extension (TypeScript)"}
  ]
}
```

The `agent_router` block already describes the shared tool; no second entry needed.

---

## 4. Gotchas That Would Break a Copy-Mode Install

1. **No `_routes.golden.tsv` copy.** `place_tree ... "*.md"` skips `.tsv` files.
   The golden corpus MUST be placed separately (see `install_claude_code` which already
   does this with an explicit `place_file` call). Forgetting this makes `--eval` fail
   with `FATAL: missing golden corpus`.

2. **No `route-extension.ts` in the seed yet.** `integrations/prime-agent/README.md`
   describes a `route-extension.ts` but the file does not exist in the seed at the time
   of this audit. `install.sh` cannot copy a non-existent file. Either create it before
   wiring the install, or make the install conditional and skip the extension gracefully.

3. **Prompt file naming collision.** The existing slash-command generator
   (`generate_slash_commands`) emits `<name>.md` files. Both opencode and claude-code
   use `.md`. Prime-agent prompts also use `.md`. The assertion helper
   `assert_cmd_roster "$T/.prime/agent/prompts" .md` will work — but the directory must
   contain ONLY command-protocol projections, not the agent brief sources (which live in
   `.prime/agent/agents/`, a different directory).

4. **No harness registration — by design.** Unlike claude-code which enumerates
   `.claude/agents/` at session start, prime-agent never auto-registers the agents.
   The orchestrator must read the brief source and pass it to `rlm()`. This is not a
   bug to fix; it is the correct architecture. Document this in the `install.sh`
   registration notice rather than trying to work around it.

5. **settings.json key set differs.** prime-agent settings recognizes `extensions`,
   `skills`, `prompts`, `themes` as array keys (verified in
   `dist/core/settings-manager.js:672-710`). There is NO `agents` key. Do not add
   one — the schema will reject unknown keys or silently ignore them. The agents dir
   convention for prime-agent is `.prime/agent/agents/` (brief sources, not harness
   discovery).

6. **`--eval` gate requires `_routes.golden.tsv` in the same dir as agents.** If
   the plant install puts agents in `.prime/agent/agents/` but omits the `.tsv`,
   `cmd_eval` raises `FATAL: missing golden corpus` and exits 2. The `cmp` assertion
   in the test-full-install section catches drift after the fact, but the gate itself
   will simply fail loudly.

---

## 5. Conclusion

Prime-agent parity requires exactly four additions to the seed:

1. `install_prime_agent()` function in `install.sh` (with `prime-agent` and `all` wired)
2. A `prime-agent` section in `tests/test-full-install.sh` using `agent-lint.py --dir`
3. A `prime-agent` entry in `manifest.json` integrations array
4. The `route-extension.ts` file in `integrations/prime-agent/` (stub or full)

The `agent-lint.py` tool itself needs zero changes. The seed-side CI gates (`run.sh`
lines 13-14) are already shared infrastructure. The gate is mechanical linting of the
same `agents/*.md` files — it is simply run against the prime-agent projection directory
instead of `.claude/agents/` in the plant-side test.
