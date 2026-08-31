# Scout-05: prime-agent Extension API for Route Enforcement

**Task:** Determine the exact prime-agent extension contract to replicate
`integrations/claude-code/route-hook.py` as a `prime-agent` extension.

**Sources verified against dist/ source, not just docs.**

---

## 1. Extension Discovery

prime-agent auto-discovers extensions from four locations (loader.js, `discoverExtensionsInDir`):

| Location | Scope |
|---|---|
| `<cwd>/.prime/agent/extensions/*.ts` | Project-local (direct file) |
| `<cwd>/.prime/agent/extensions/*/index.ts` | Project-local (subdir) |
| `~/.prime/agent/extensions/*.ts` | Global (direct file) |
| `~/.prime/agent/extensions/*/index.ts` | Global (subdir) |

**Source:** `dist/core/extensions/loader.js`, function `discoverExtensionsInDir`:
```js
// CONFIG_DIR_NAME = ".prime/agent"  (dist/config.js line ~4)
const localExtDir = path.join(cwd, CONFIG_DIR_NAME, "extensions");
const globalExtDir = path.join(agentDir, "extensions");  // agentDir = ~/.prime/agent
```

`isExtensionFile` accepts `.ts` and `.js` only (not `.mts`, `.cts`).

**Discovery order:** local project first, then global; deduplicated by resolved path.

---

## 2. TypeScript Loading — No Build Step Required

Extensions are loaded via **jiti** (`dist/core/extensions/loader.js`, `loadExtensionModule`):

```js
const { createJiti } = await import("jiti/static");
const jiti = createJiti(import.meta.url, {
  moduleCache: false,
  // In Node.js: alias-based module resolution
  // In Bun bundle: virtualModules from bundled-modules.js
});
const module = await jiti.import(extensionPath, { default: true });
```

**Conclusion:** prime-agent loads `.ts` files DIRECTLY — no `tsc`, `esbuild`, or `npm run build`
step is needed. jiti does runtime TypeScript transpilation. This applies in both Node.js
and Bun binary modes.

---

## 3. Import Package Name and Type

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
```

**Source:** `dist/core/extensions/types.d.ts` — `ExtensionAPI` is defined there and exported
from `dist/index.d.ts` via `dist/core/extensions/index.js`.

The loader aliases `@earendil-works/pi-coding-agent` to the local `dist/index.js` so
this import resolves without an npm install inside the extension directory.

Also available (no install needed, all aliased by the loader):
- `typebox` — parameter schemas
- `@earendil-works/pi-ai` — `StringEnum`, AI utilities
- `@earendil-works/pi-tui` — TUI components
- `node:fs`, `node:path`, `node:child_process`, etc. — all Node.js built-ins

---

## 4. `before_agent_start` Event — Exact Firing Point

**When it fires:** After user submits a prompt (and after skill/template expansion), but
before the agent loop starts. It is called from `AgentSession` (`dist/core/agent-session.js`
line ~4682) inside the preparation phase:

```js
const result = await this._extensionRunner.emitBeforeAgentStart(
  preparationAction.payload.text,  // expanded prompt text
  preparationAction.payload.images,
  basePromptSnapshot,              // current system prompt string
  this._baseSystemPromptOptions
);
```

**Source:** `dist/core/extensions/runner.js`, `emitBeforeAgentStart` method.

The handler receives `event: BeforeAgentStartEvent` (from `types.d.ts`):

```typescript
interface BeforeAgentStartEvent {
  type: "before_agent_start";
  prompt: string;               // expanded user prompt text
  images?: ImageContent[];      // attached images, if any
  systemPrompt: string;         // CHAINED: includes changes from earlier handlers
  systemPromptOptions: BuildSystemPromptOptions;  // structured data: tools, skills, etc.
}
```

Handlers run **sequentially** in extension load order. Each handler sees the system prompt
as modified by prior handlers (chained). `ctx.getSystemPrompt()` also returns the current
chained value.

---

## 5. Exact Return Object Shape

```typescript
interface BeforeAgentStartEventResult {
  message?: Pick<CustomMessage, "customType" | "content" | "display" | "details">;
  systemPrompt?: string;  // replaces system prompt for this turn (chained)
}
```

**Source:** `dist/core/extensions/types.d.ts`, `BeforeAgentStartEventResult`.

### `message` field (context injection):

```typescript
{
  customType: string;   // your extension identifier, e.g. "cypress-route"
  content: string | (TextContent | ImageContent)[];  // text sent to LLM
  display: boolean;     // true = shown in TUI; false = hidden in TUI
  details?: unknown;    // arbitrary metadata, NOT sent to LLM
}
```

**How the LLM sees it:** `_appendBeforeAgentStartMessages` (`agent-session.js`) adds it to
the message list as `role: "custom"`. Then `convertToLlm` (`dist/core/messages.js`) converts
it to `{ role: "user", content: [...] }` — so it arrives as a **user turn** prepended before
the agent starts. The `display` field only controls TUI visibility; the LLM always receives
the `content`.

**Exception:** Some built-in `customType` values are filtered out (slash commands, compaction,
refinement outcomes). Custom types from extensions are always passed through.

### `systemPrompt` field:

Returns the full replacement string for the system prompt for this turn. Prime Agent sets
`this.agent.state.systemPrompt` to this value for the duration of the turn, then restores
the base prompt after. Each extension's returned `systemPrompt` is chained — the next
handler sees the updated value via `event.systemPrompt`.

---

## 6. Shell-Out via `pi.exec` (Preferred)

Extensions have access to `pi.exec()` in the `ExtensionAPI`:

```typescript
pi.exec(command: string, args: string[], options?: ExecOptions): Promise<ExecResult>
// ExecResult: { stdout, stderr, code, killed }
// ExecOptions: { signal?, timeout?, cwd?, env? }
```

**Source:** `dist/core/extensions/loader.js`, `createExtensionAPI`, `exec` method.

Under the hood it uses `node:child_process.spawn` with `shell: false`
(verified in `dist/core/exec.js`). So the equivalent of route-hook.py's:

```python
subprocess.run([sys.executable, str(LINT), "--plan", prompt], ...)
```

becomes:

```typescript
const result = await pi.exec("python3", [lintPath, "--plan", prompt], {
  timeout: 15_000,
  cwd: rootDir,
});
```

Alternatively, extensions may import `node:child_process` directly (jiti does not restrict
Node.js built-ins). But `pi.exec` is idiomatic and handles abort signals, session env
vars, and per-subprocess env merging automatically.

---

## 7. Fail-Open Requirements

From route-hook.py: "never blocks — any error degrades to the mandate or silence, exit 0 always."

In prime-agent, handler errors are caught internally by the runner:

```js
// dist/core/extensions/runner.js, emitBeforeAgentStart:
try {
  const handlerResult = await handler(event, ctx);
  ...
} catch (err) {
  this.emitError({ extensionPath, event: "before_agent_start", error, stack });
}
```

The runner **logs the error and continues** — the agent run proceeds normally. So a thrown
exception from `before_agent_start` is itself fail-open. Nevertheless, explicit
try/catch inside the handler is still best practice to control the fallback content.

---

## 8. Minimal Correct Skeleton: `route-extension.ts`

```typescript
/**
 * route-extension.ts — prime-agent port of integrations/claude-code/route-hook.py
 *
 * Enforces progressive-discovery before every non-trivial prompt.
 * Mirrors the fail-open contract of the Claude Code hook exactly.
 *
 * Install at: <project>/.prime/agent/extensions/route-extension.ts
 * (auto-discovered; no build step needed — jiti transpiles TypeScript at runtime)
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const TRIVIAL = new Set([
  "", "yes", "no", "ok", "thanks", "thank you", "go", "continue", "y", "n",
]);

const LINT_CANDIDATES = [
  ["docs", "graph", "graph-lint.py"],
  ["tools", "graph-lint.py"],
];

function findLint(cwd: string): { lint: string; root: string } | null {
  const starts = [cwd];
  const seen = new Set<string>();
  for (const start of starts) {
    let p = start;
    for (let i = 0; i < 7; i++) {
      if (seen.has(p)) break;
      seen.add(p);
      for (const parts of LINT_CANDIDATES) {
        const candidate = path.join(p, ...parts);
        if (fs.existsSync(candidate)) {
          return { lint: candidate, root: p };
        }
      }
      const parent = path.dirname(p);
      if (parent === p) break;
      p = parent;
    }
  }
  return null;
}

export default function routeExtension(pi: ExtensionAPI) {
  pi.on("before_agent_start", async (event, ctx) => {
    const prompt = event.prompt.trim();

    // Skip trivial prompts — matches route-hook.py TRIVIAL set + length check
    if (TRIVIAL.has(prompt.toLowerCase()) || prompt.length < 8) {
      return;
    }

    const MANDATE =
      "PROGRESSIVE DISCOVERY IS REQUIRED. Before reading source or writing " +
      "anything, open docs/graph/index.md, load only the nodes this task " +
      "needs, and state which you loaded and which you deliberately " +
      "skipped. Do not bulk-read to orient. Then classify the task tier " +
      "out loud (kernel §0: T0 question / T1 trivial non-behavioral edit / " +
      "T2 spec-covered change / T3 everything else) — process follows the tier.";

    let content = MANDATE;

    // Attempt to run graph-lint.py --plan for router suggestions
    const found = findLint(ctx.cwd);
    if (found === null) {
      content =
        "No knowledge graph found (docs/graph/). Use the canonical " +
        "INSTALL_PROMPT.md; /initialize is only a tool adapter.";
    } else {
      try {
        const result = await pi.exec(
          "python3",
          [found.lint, "--plan", prompt],
          { timeout: 15_000, cwd: found.root },
        );
        if (result.code === 0 && result.stdout.trim()) {
          const body = result.stdout.split("\n").slice(2).join("\n").trim();
          if (body) {
            content +=
              "\n\nRouter suggestion (a keyword heuristic — reason over it):\n" +
              body;
          }
        }
      } catch {
        // Fail open — lint error never blocks the session
      }
    }

    return {
      message: {
        customType: "cypress-route",
        content,
        display: true,   // visible in TUI; set false to hide from user
      },
    };
  });
}
```

---

## 9. Gotchas for Copy-Mode Install

1. **Path is `.prime/agent/extensions/`, not `.prime/extensions/`.**
   `CONFIG_DIR_NAME = ".prime/agent"` (dist/config.js). The full project-local path is
   `<cwd>/.prime/agent/extensions/route-extension.ts`.

2. **No build step, but file MUST export a default function.**
   `loadExtensionModule` checks `typeof factory === "function"` — a missing or wrong export
   silently skips the extension with an error logged.

3. **`customType` collision:** pick a unique string; some built-in `customType` values
   (SESSION_SLASH_COMMAND, COMPACTION_OUTCOME, etc.) are filtered from LLM context. Custom
   types from extensions are always passed through.

4. **`display: true` vs `false`:** `display` only controls TUI visibility. Both values send
   `content` to the LLM as a user message. Use `display: true` so users see the mandate
   (matches route-hook.py intent where `additionalContext` is always visible to the user).

5. **`systemPrompt` vs `message`:** Use `message` to inject prepended context (like
   `additionalContext` in Claude Code). Use `systemPrompt` to append to or replace the
   system-level instructions. For route enforcement, `message` is the correct field —
   it maps directly to `hookSpecificOutput.additionalContext`.

6. **`pi.exec` uses `shell: false`.** Do NOT pass a shell string like `"python3 lint.py"`.
   Use the `args` array: `pi.exec("python3", [lintPath, "--plan", prompt])`.

7. **Handler exceptions are caught by the runner** (fail-open by default), but an explicit
   try/catch around the `pi.exec` call is still needed to control the fallback content
   (otherwise the handler returns `undefined` and no message is injected at all, rather
   than injecting the mandate without suggestions).

8. **jiti module cache is disabled** (`moduleCache: false`). Extensions are re-read from
   disk on every `/reload`. No stale transpilation cache issues.

9. **Node.js built-ins (`node:fs`, `node:path`, `node:child_process`) are available directly.**
   The docs confirm this; jiti does not restrict them. But prefer `pi.exec` over raw
   `child_process` for the abort-signal and session-env integration.

---

## 10. What `BeforeAgentStartEventResult.message` Is NOT

- It is NOT a system prompt. It is injected as a **user-role message** (via `convertToLlm`).
- It is NOT ephemeral. It is appended to the session store
  (`appendCustomMessageEntry` in agent-session.js line 2572).
- It is NOT filtered by `display`. Both `display: true` and `false` go to the LLM.

This matches Claude Code's `additionalContext` semantics exactly: injected as prepended
context before the model answers.

---

*Report written by scout-05. Verified against dist/ source. No source files edited.*
