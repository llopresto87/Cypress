// route-extension.ts — progressive-discovery enforcement for Prime Agent.
//
// The Prime Agent parity of Claude Code's route-hook.py. It subscribes to the
// `before_agent_start` event (fired after the user submits a prompt, before the
// agent loop) and injects the route-first mandate plus the graph router's
// suggested node set as a prepended message — the same behaviour, using Prime
// Agent's native extension API instead of a shell hook.
//
// Installed to `.prime/agent/extensions/route-extension.ts` by
// `install.sh prime-agent`. Prime Agent auto-discovers `.prime/agent/extensions/`
// and transpiles .ts at runtime (jiti) — no build step. The bundled
// `.prime/agent/settings.json` also lists it explicitly for locked-down configs.
//
// It NEVER blocks: any error (missing graph, router failure, timeout) degrades
// to the bare mandate or to silence. The kernel's own FIRST-MOVE mandate is the
// non-extension floor, so route-first holds even with this extension disabled.

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// Short/trivial prompts don't need routing (mirror route-hook.py).
const TRIVIAL = new Set([
  "", "yes", "no", "ok", "thanks", "thank you", "go", "continue", "y", "n",
]);

// The graph linter lives at docs/graph/graph-lint.py (the scaffold the installer
// drops) or tools/graph-lint.py. Walk up from cwd to find the project root.
const CANDIDATES = [
  ["docs", "graph", "graph-lint.py"],
  ["tools", "graph-lint.py"],
];

function findLint(startDir: string): { lint: string; root: string } | null {
  let p = path.resolve(startDir);
  for (let i = 0; i < 7; i++) {
    for (const parts of CANDIDATES) {
      const candidate = path.join(p, ...parts);
      if (fs.existsSync(candidate)) return { lint: candidate, root: p };
    }
    const parent = path.dirname(p);
    if (parent === p) break;
    p = parent;
  }
  return null;
}

const MANDATE =
  "PROGRESSIVE DISCOVERY IS REQUIRED. Before reading source or writing " +
  "anything, open docs/graph/index.md, load only the nodes this task needs, " +
  "and state which you loaded and which you deliberately skipped. Do not " +
  "bulk-read to orient. Then classify the task tier out loud (kernel " +
  "\u00a70: T0 question / T1 trivial non-behavioral edit / T2 spec-covered " +
  "change / T3 everything else) \u2014 process follows the tier.";

export default function routeExtension(pi: ExtensionAPI): void {
  pi.on("before_agent_start", async (event, ctx) => {
    try {
      const prompt = (event.prompt || "").trim();
      if (TRIVIAL.has(prompt.toLowerCase()) || prompt.length < 8) return;

      const found = findLint(ctx.cwd);
      if (!found) {
        return {
          message: {
            customType: "cypress-route",
            content:
              "No knowledge graph found (docs/graph/). Use the canonical " +
              "INSTALL_PROMPT.md; /initialize is only a tool adapter.",
            display: true,
          },
        };
      }

      let content = MANDATE;
      try {
        const r = await pi.exec("python3", [found.lint, "--plan", prompt], {
          timeout: 15_000,
          cwd: found.root,
        });
        if (r.code === 0 && r.stdout.trim()) {
          // graph-lint --plan prints a 2-line header, then the suggested nodes.
          const body = r.stdout.split("\n").slice(2).join("\n").trim();
          if (body) {
            content +=
              "\n\nRouter suggestion (a keyword heuristic \u2014 reason over it):\n" +
              body;
          }
        }
      } catch {
        // fail open: keep the bare mandate
      }

      return { message: { customType: "cypress-route", content, display: true } };
    } catch {
      // never block a prompt
      return;
    }
  });
}
