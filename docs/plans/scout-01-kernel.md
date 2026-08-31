# Scout-01: prime-agent Context/Kernel File Loading

**Source:** `dist/core/resource-loader.js` (v0.8.1)  
**Date:** 2025-01

---

## TL;DR

prime-agent loads **all** matching context files and **concatenates** them into the system
prompt (no first-wins). Within one directory, `AGENTS.md` beats `CLAUDE.md`. Discovery order
is: `~/.prime/agent/` → filesystem root → ... → cwd (root-to-leaf). No size truncation.
`--no-context-files` / `-nc` skips all discovery.

---

## 1. The Discovery Function

**File:** `dist/core/resource-loader.js:30–76`

```js
function loadContextFileFromDir(dir) {
    const candidates = ["AGENTS.md", "AGENTS.MD", "CLAUDE.md", "CLAUDE.MD"];
    for (const filename of candidates) {
        const filePath = join(dir, filename);
        if (existsSync(filePath)) {
            return { path: filePath, content: readFileSync(filePath, "utf-8") };
        }
    }
    return null;
}
```

**Within a single directory**: first-match wins. Order is:
1. `AGENTS.md`
2. `AGENTS.MD`
3. `CLAUDE.md`
4. `CLAUDE.MD`

**AGENTS.md beats CLAUDE.md in every directory.** If both exist, only AGENTS.md loads.

---

## 2. Discovery Order (full walk)

**File:** `dist/core/resource-loader.js:48–76`

```js
export function loadProjectContextFiles(options) {
    const { cwd, agentDir } = options;
    const contextFiles = [];
    const seenPaths = new Set();

    // 1. agentDir first (~/.prime/agent/)
    const globalContext = loadContextFileFromDir(agentDir);
    if (globalContext) {
        contextFiles.push(globalContext);
        seenPaths.add(globalContext.path);
    }

    // 2. Walk from cwd up to /
    const ancestorContextFiles = [];
    let currentDir = cwd;
    while (true) {
        const contextFile = loadContextFileFromDir(currentDir);
        if (contextFile && !seenPaths.has(contextFile.path)) {
            ancestorContextFiles.unshift(contextFile);  // prepend → root-to-leaf
            seenPaths.add(contextFile.path);
        }
        if (currentDir === "/") break;
        currentDir = resolve(currentDir, "..");
    }

    contextFiles.push(...ancestorContextFiles);
    return contextFiles;
}
```

**Resulting array order (what the model sees, top to bottom):**

| Position | Source | Example path |
|----------|--------|-------------|
| 1 | `agentDir` | `~/.prime/agent/AGENTS.md` (if it exists) |
| 2 | filesystem root | `/AGENTS.md` or `/CLAUDE.md` (rare) |
| ... | each ancestor dir | `/home/AGENTS.md`, `/home/user/AGENTS.md` |
| N | cwd | `<project-root>/AGENTS.md` or `CLAUDE.md` |

**All matches are concatenated in the system prompt** — none is skipped except:
- Deduplication by absolute path (`seenPaths`)
- `noContextFiles = true` → empty list

---

## 3. agentDir default

**File:** `dist/config.js:408–413`

```js
export const CONFIG_DIR_NAME = ".prime/agent";   // from piConfig.configDir
export function getAgentDir() {
    const envDir = process.env["PRIME_AGENT_CODING_AGENT_DIR"];
    if (envDir) return expandTildePath(envDir);
    return join(homedir(), CONFIG_DIR_NAME);      // → ~/.prime/agent
}
```

Default `agentDir` = `~/.prime/agent`.  
Override: env var `PRIME_AGENT_CODING_AGENT_DIR`.

---

## 4. --no-context-files / -nc flag

**File:** `dist/cli/args.js:197–198`

```js
else if (arg === "--no-context-files" || arg === "-nc") {
    result.noContextFiles = true;
}
```

**File:** `dist/cli/command-registry.js:220`

```
["-nc, --no-context-files", "Disable AGENTS.md and CLAUDE.md discovery"]
```

**File:** `dist/core/resource-loader.js:338`

```js
agentsFiles: this.noContextFiles ? [] : loadProjectContextFiles({ cwd: this.cwd, agentDir: this.agentDir }),
```

When set, `getAgentsFiles()` returns `[]`. The system prompt is built
with zero project context files. The flag is honoured in both CLI and
daemon-command parsing.

---

## 5. Injection into the system prompt

**File:** `dist/core/system-prompt.js:96–100`

```js
if (contextFiles.length > 0) {
    prompt += "\n\n# Project Context\n\n";
    prompt += "Project-specific instructions and guidelines:\n\n";
    for (const { path: filePath, content } of contextFiles) {
        prompt += `## ${filePath}\n\n${content}\n\n`;
    }
}
```

Each file is inserted verbatim under its absolute path as a `## heading`.
**No size cap, no truncation.** The entire content of every matched file
is injected.

---

## 6. Is repo-root AGENTS.md the correct single kernel home?

**Yes.** In a target project (plant):

1. prime-agent's cwd = project root.
2. Walk hits project root last in the ancestor loop.
3. `AGENTS.md` at project root is the last (and highest-priority in reading
   order — nearest to the task) entry loaded.
4. The `core/AGENTS.md` in the CYPRESS seed is **the product shipped to
   plants**, placed at their root during `install.sh prime-agent`.
5. The existing `integrations/prime-agent/README.md` already documents
   this: "AGENTS.md → core/AGENTS.md (symlink or copy at repo root)".

This is consistent with opencode and Codex which also read `AGENTS.md`
at repo root.

---

## 7. CLAUDE.md precedence gotcha (copy-mode install)

**The critical gotcha:**

If a project has BOTH `AGENTS.md` **and** `CLAUDE.md` at its root, only
`AGENTS.md` is loaded from that directory — `CLAUDE.md` is silently
skipped (`dist/core/resource-loader.js:31–45`, candidate list order).

**In the CYPRESS seed repo itself:**
- Root has `CLAUDE.md` (meta-notes for Claude Code editors of the seed).
- `core/AGENTS.md` is the product (not at root).
- prime-agent running in the seed repo loads **only `CLAUDE.md`** — the
  seed-dev notes — which is correct behaviour for that context.

**In a target plant:**
- `install.sh prime-agent` places/symlinks `AGENTS.md` → `core/AGENTS.md`
  at project root.
- If Claude Code is also installed, the plant may have `CLAUDE.md` at root.
- prime-agent will load `AGENTS.md` and **ignore `CLAUDE.md`** in that
  directory.
- **Mitigation already documented in `integrations/prime-agent/README.md`**:
  "keep one kernel file canonical and symlink the other" — symlink
  `CLAUDE.md → AGENTS.md` so both tools read the same kernel and CLAUDE.md
  is never ignored.

**If CLAUDE.md is the single canonical file** (Claude Code primary), then
for prime-agent you must **also** create `AGENTS.md` (or a symlink) at
root — else prime-agent reads nothing from the project root.

---

## 8. Size budget

**None in the context-file pipeline.** The CYPRESS seed's own 8 000-byte
kernel budget (`tests/seed-lint.py`) is a seed-internal lint rule enforced
on `core/AGENTS.md`, not a prime-agent runtime limit.

prime-agent applies no byte or token cap to context files before injecting
them. Overlong files consume model context window directly.

---

## 9. Summary table

| Question | Answer | Source |
|---------|--------|--------|
| Files recognised | `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md`, `CLAUDE.MD` | `resource-loader.js:31` |
| Per-directory winner | First match in candidate list; AGENTS.md beats CLAUDE.md | `resource-loader.js:32` |
| Multiple dirs | ALL matches concatenated; no first-wins across dirs | `resource-loader.js:74` |
| Discovery order | `~/.prime/agent/` → `/` → ... → cwd (root-to-leaf) | `resource-loader.js:53–74` |
| agentDir default | `~/.prime/agent` | `config.js:413` |
| Disable flag | `--no-context-files` / `-nc` | `args.js:197–198` |
| Size budget | None | `system-prompt.js:96–100` |
| Correct kernel home | `AGENTS.md` at repo root | `resource-loader.js:60–73` |
| CLAUDE.md gotcha | Silently skipped if AGENTS.md exists in same dir | `resource-loader.js:31–45` |
| Mitigation | Symlink `CLAUDE.md → AGENTS.md` | `integrations/prime-agent/README.md` |

---

## 10. Recommended action for the seed

The seed's `integrations/prime-agent/README.md` already covers this
correctly. For `install.sh prime-agent`, the install must:

1. Place/symlink `AGENTS.md` → `core/AGENTS.md` at repo root.
2. If `CLAUDE.md` is also present at root (Claude Code co-install),
   optionally symlink `CLAUDE.md → AGENTS.md` to keep both tools in sync.
   Without this symlink, Claude Code reads `CLAUDE.md` (the plant's Claude
   kernel) while prime-agent reads `AGENTS.md` (the same kernel via the
   link) — they diverge only if `CLAUDE.md` and `AGENTS.md` have different
   content, which the symlink prevents.
3. Do **not** list the kernel in `settings.json` under an `instructions`
   key — prime-agent has no such key, and auto-discovery already loads it.
   Adding a manual path would double-inject it.
