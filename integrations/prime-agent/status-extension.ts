// status-extension.ts — surface the lifecycle status register once per session.
//
// The Prime Agent parity of Claude Code's status-hook.py (SessionStart). Prime
// Agent's extension API fires `before_agent_start` per prompt, so this module
// keeps a process-local flag and injects only on the FIRST prompt of the
// session: `status-register.py --summary` — open / hotfix / deferred counts
// and the oldest items — as a prepended message. Not per prompt; nothing for
// the model to remember; subagents (rlm children) get nothing.
//
// Installed to `.prime/agent/extensions/status-extension.ts` by
// `install.sh prime-agent`; auto-discovered like route-extension.ts.
// It NEVER blocks: any error degrades to silence.

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const CANDIDATES = [
  ["docs", "graph", "status-register.py"],
  ["tools", "status-register.py"],
];

function findRegister(startDir: string): { tool: string; root: string } | null {
  let p = path.resolve(startDir);
  for (let i = 0; i < 7; i++) {
    for (const parts of CANDIDATES) {
      const candidate = path.join(p, ...parts);
      if (fs.existsSync(candidate)) return { tool: candidate, root: p };
    }
    const parent = path.dirname(p);
    if (parent === p) break;
    p = parent;
  }
  return null;
}

let shown = false;

export default function statusExtension(pi: ExtensionAPI): void {
  pi.on("before_agent_start", async (_event, ctx) => {
    if (shown) return;
    shown = true;
    try {
      const found = findRegister(ctx.cwd);
      if (!found) return;
      const r = await pi.exec(
        "python3",
        [found.tool, "--summary", "--root", path.join(found.root, "docs", "graph")],
        { timeout: 15_000, cwd: found.root },
      );
      const summary = (r.stdout || "").trim();
      if ((r.code !== 0 && r.code !== 1) || !summary) return;
      return {
        message: {
          customType: "cypress-status",
          content:
            "Status register (lifecycle debt in this plant, from frontmatter — " +
            "read it, do not re-infer it): " + summary,
          display: true,
        },
      };
    } catch {
      return;
    }
  });
}
