# Scout 08: Dogfooding — Should the Seed Carry `.prime/agent/`?

**Facet:** Whether the CYPRESS seed repo itself should carry `.prime/agent/`
scaffolding so a Prime Agent session developing the seed gets first-class
experience equal to Claude Code.

**Verdict: YES — but minimally. One .gitignore line, not source files.**

---

## 1. What the seed already dogfoods today

### Claude Code (existing)
- `CLAUDE.md` at repo root — seed-specific dev instructions (gates, conventions).
  Auto-loaded by CC as the project kernel.
- `.claude/settings.local.json` (gitignored) — Bash permission hints:
  `Bash(python3 docs/graph/graph-lint.py)`, `git config *`, `git fetch *`, etc.

### Prime Agent (current state)
- `CLAUDE.md` at repo root — **also auto-loaded by prime-agent**.
  Verified in `dist/core/resource-loader.js:1284`:
  ```js
  function loadContextFileFromDir(dir) {
      const candidates = ["AGENTS.md", "AGENTS.MD", "CLAUDE.md", "CLAUDE.MD"];
      for (const filename of candidates) { ... }
  }
  ```
  `loadProjectContextFiles()` walks from cwd up through all ancestors,
  collects every matching file, and concatenates them. CLAUDE.md at the
  seed root IS loaded automatically.
- `.prime/agent/` — **does not exist**. Not gitignored.

---

## 2. The self-install guard (does not apply here)

`install.sh:20569`:
```bash
# Sanity: refuse to install into the seed itself.
[[ "$PROJECT_DIR" != "$SEED_ROOT" ]] || die \
    "refusing to install the seed system into itself; pass --project-dir"
```

This guard fires only when a dev runs `install.sh` with the seed as the
target project. It does **not** fire because the seed carries a
`.prime/agent/` directory. The guard is about the installer command, not
about what files exist at the seed root. Adding `.prime/agent/settings.json`
to the seed for dogfooding is **orthogonal** to the self-install guard.

---

## 3. Gap analysis: CC dev experience vs PA dev experience

| Element | Claude Code dev | Prime Agent dev |
|---|---|---|
| Seed-specific kernel | CLAUDE.md (explicit load) | CLAUDE.md (auto-loaded ✓) |
| Gates / conventions | CLAUDE.md: "bash tests/run.sh" | CLAUDE.md: same ✓ |
| Bash permissions | `.claude/settings.local.json` (gitignored) | **No PA equivalent** |
| Skill projections | None (`.claude/` is gitignored; plant skills not in seed) | None needed (same reasoning) |
| Prompt commands | None (seed has no installed graph) | None needed ✓ |
| Route-extension | Not in seed `.claude/` | Not needed in seed ✓ |
| Git noise | `.claude/` gitignored — no noise | `.prime/` NOT gitignored → local PA sessions create `settings.json` in `.prime/agent/` showing as untracked |

**The only real gap:** `.prime/` is not in `.gitignore`.

PA stores harness state and sessions globally at `~/.prime/agent/` (confirmed
via `dist/core/refinement/refinement.js`: `getGlobalHarnessStateDir(agentDir)`
and `dist/core/session-manager.js`: `getDefaultSessionDir()` → `getSessionsDir(agentDir)`).
The **only** project-local file PA writes is `.prime/agent/settings.json`,
created when a dev changes settings via `/settings`. Without `.prime/` in
`.gitignore`, this shows as an untracked file in the seed repo.

---

## 4. Why committed `.prime/agent/` source files are NOT the answer

The PA integration README (`integrations/prime-agent/README.md`) describes
a settings.json for PLANTS:
```json
{
  "extensions": [".prime/agent/extensions"],
  "skills": [".prime/agent/skills"],
  "prompts": [".prime/agent/prompts"]
}
```
These paths only make sense after `install.sh prime-agent` places the
resources there. The **seed does not have** `.prime/agent/skills/`,
`extensions/`, or `prompts/` — it has no installed graph. Committing a
settings.json pointing at empty directories adds confusion without benefit.

PA settings do **not** have a Bash-permissions model (the only thing in
`.claude/settings.local.json`). There is nothing to commit.

---

## 5. Does the seed need a root `AGENTS.md`?

No. `resource-loader.js` picks CLAUDE.md when no AGENTS.md exists.
The seed already has CLAUDE.md with seed-specific dev instructions.
Adding AGENTS.md would load `core/AGENTS.md` (the plant kernel) instead —
which tells the model to open `docs/graph/index.md` (non-existent in the
seed). CLAUDE.md IS the correct seed dev context.

---

## 6. Recommendation: minimal concrete change

**Exactly one file to change:**

`/.gitignore` — add `.prime/` alongside the existing `.claude/`, `.opencode/`, `.codex/`:

```diff
 # Local per-tool overlays installed into a working project (not seed source)
 .claude/
 .opencode/
 .codex/
+.prime/
```

**Rationale:**
- `.claude/` is already gitignored (same reason: local dev state, not seed source).
- `.prime/` follows the same pattern.
- This prevents `git status` noise when a dev uses PA in the seed root.
- No committed `.prime/agent/` files are needed: CLAUDE.md auto-load already
  provides first-class dev context in PA sessions (verified vs source).
- The self-install guard is unaffected.

**No other file changes are needed for seed dogfooding parity.**

---

## 7. The "not a plant" invariant

CLAUDE.md states: "This repository IS the seed — not a grown plant."
`core/AGENTS.md` is the product shipped to plants; CLAUDE.md is the
seed-specific kernel.

Committing a `.prime/agent/settings.json` that points at
`.prime/agent/skills/` etc. would imply those plant artifacts exist in
the seed — a false assumption. It would also mislead future contributors
about what these files are for.

The `.gitignore` addition is the correct and minimal change:
it acknowledges that PA sessions may create `.prime/agent/settings.json`
locally, without pretending the seed is a plant.

---

## 8. Gotchas for a copy-mode install

These apply to PLANTS, not to seed dogfooding, but worth noting for the
parallel investigation:

1. **No `install_prime_agent` in `install.sh` yet** — the function is
   described in `integrations/prime-agent/README.md` but not implemented
   (confirmed: `prime` does not appear in install.sh).
2. **`integrations/prime-agent/` is incomplete** — only README.md exists;
   `settings.json` and `route-extension.ts` are not yet authored.
3. **manifest.json lists 4 integrations** (CC, opencode, codex, copilot);
   prime-agent is absent.
4. **tests/test-full-install.sh** has a "four-tool contract"; prime-agent
   is not tested.
5. **seed-lint.py** does not check prime-agent README for
   `delegation.harness-registration`.

These are INC1-INC4 from `docs/plans/prime-agent-integration.md` —
the full integration is in-progress. The dogfood `.gitignore` change
is independent of those increments and can land first.

---

## 9. Source citations

| Claim | Source |
|---|---|
| PA auto-loads CLAUDE.md from cwd | `dist/core/resource-loader.js:1284` |
| Project settings path = cwd/.prime/agent/settings.json | `dist/config.js`: `CONFIG_DIR_NAME = ".prime/agent"` |
| Harness state stored globally (not in cwd) | `dist/core/refinement/refinement.js`: `getGlobalHarnessStateDir(agentDir)` |
| Sessions stored globally | `dist/core/session-manager.js`: `getDefaultSessionDir(_cwd, agentDir)` |
| Self-install guard fires on PROJECT_DIR == SEED_ROOT | `install.sh:20569` |
| .claude/ is gitignored | `.gitignore` line 13 |
| .prime/ is NOT gitignored | `.gitignore` (absent) |
| PA skill discovery paths | `dist/core/skills.js:loadSkills()` |
| PA has no Bash permissions model | `docs/settings.md` (full settings reference, no allow/deny) |
| integrations/prime-agent/ has only README.md | `ls integrations/prime-agent/` |
| install.sh has no prime-agent support | `grep -q prime install.sh` → nothing |

---

*Written by research-scout (Sonnet 4.6), read-only pass.*
*Full detail in: /home/okik/cypress-6.6.0/cypress/docs/plans/scout-08-dogfood.md*
