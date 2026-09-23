// route-extension.ts — progressive-discovery enforcement for Prime Agent.
//
// The Prime Agent parity of Claude Code's route-hook.py. It subscribes to the
// `before_agent_start` event (fired after the user submits a prompt, before the
// agent loop) and injects a one-line pointer at the kernel plus the graph
// router's suggested node set as a prepended message — the same text as the
// hook's full mode, using Prime Agent's native extension API instead of a
// shell hook (SPEC-0003).
//
// The prompt reaches the router as one `--plan=` argv value (pi.exec spawns
// without a shell), and router output that does not begin with the exact echo
// of the prompt is dropped, so the prompt is never passed back in.
//
// It keeps no state. With no session id on this event there is nothing to
// key a record on, so every routed prompt gets the full text. Remembering
// which nodes were already surfaced is the model's job here, in its IPython
// kernel, as the `## Surfaced nodes` section of APPEND_SYSTEM.md asks.
//
// Installed to `.prime/agent/extensions/route-extension.ts` by
// `install.sh prime-agent`. Prime Agent auto-discovers `.prime/agent/extensions/`
// and transpiles .ts at runtime (jiti) — no build step. The bundled
// `.prime/agent/settings.json` also lists it explicitly for locked-down configs.
//
// It NEVER blocks: any error (missing graph, router failure, timeout) degrades
// to the pointer line or to silence. The kernel's own FIRST MOVE is the
// non-extension floor, so route-first holds even with this extension disabled.

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// Short/trivial prompts don't need routing (mirror route-hook.py).
const TRIVIAL = new Set([
  "", "yes", "no", "ok", "thanks", "thank you", "go", "continue", "y", "n",
]);

// The graph linter lives at docs/graph/graph-lint.py — the scaffold the
// installer drops, and the only path it writes. Walk up from cwd to find the
// project root. A candidate no writer produces is not a fallback: the only file
// it could ever select is one this project did not put there, so a path is
// listed here only while something writes it (mirrors route-hook.py).
const CANDIDATES = [
  ["docs", "graph", "graph-lint.py"],
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

// The same two literals as route-hook.py, so the hosts cannot drift apart.
const POINTER = "Route first: the kernel's FIRST MOVE and \u00a70 apply to this prompt.";
const SUGGESTION_HEADER = "Router suggestion (a keyword heuristic \u2014 reason over it):";

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
              "INSTALL_PROMPT.md; /initialize is the entry fork behind it \u2014 " +
              "grow when there is source to scout, from-scratch when the " +
              "repository is empty.",
            display: true,
          },
        };
      }

      let content = POINTER;
      try {
        const r = await pi.exec("python3", [found.lint, `--plan=${prompt}`], {
          timeout: 15_000,
          cwd: found.root,
        });
        // graph-lint --plan echoes the prompt as `task: <prompt>` and a blank
        // line; anything else is a router failure and keeps the pointer alone.
        const prefix = `task: ${prompt}\n\n`;
        if (r.code === 0 && r.stdout.startsWith(prefix)) {
          const remainder = r.stdout.slice(prefix.length).trim();
          content += "\n\n" + SUGGESTION_HEADER + "\n" + remainder;
        }
      } catch {
        // fail open: keep the pointer line
      }

      return { message: { customType: "cypress-route", content, display: true } };
    } catch {
      // never block a prompt
      return;
    }
  });
}
