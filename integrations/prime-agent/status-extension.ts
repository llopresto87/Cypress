// status-extension.ts — surface the lifecycle status register and the code
// anchor once per session.
//
// The Prime Agent parity of Claude Code's status-hook.py (SessionStart). Prime
// Agent's extension API fires `before_agent_start` per prompt, so this module
// keeps a process-local flag and injects only on the FIRST prompt of the
// session: `status-register.py --summary` — open / hotfix / deferred counts
// and the oldest items. Then, whether or not a register exists, it adds what
// `code-anchor.py --compare` prints, all as one prepended message. Not per prompt; nothing
// for the model to remember; subagents (rlm children) get nothing.
// route-extension.ts, which runs on every prompt, never runs the anchor.
//
// Installed to `.prime/agent/extensions/status-extension.ts` by
// `install.sh prime-agent`; auto-discovered like route-extension.ts.
// It NEVER blocks: a missing or broken register degrades to silence, and an
// anchor comparison that did not run is the not-checked line (SPEC-0003).

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const CANDIDATES = [
  ["docs", "graph", "status-register.py"],
  ["tools", "status-register.py"],
];
const ANCHOR_CANDIDATES = [["docs", "graph", "code-anchor.py"]];
const ANCHOR_NOT_CHECKED =
  "Code anchor: not checked this session (the comparison did not run). Facts about code in the graph are unverified.";

function findTool(startDir: string, candidates: string[][]): { tool: string; root: string } | null {
  let p = path.resolve(startDir);
  for (let i = 0; i < 7; i++) {
    for (const parts of candidates) {
      const candidate = path.join(p, ...parts);
      if (fs.existsSync(candidate)) return { tool: candidate, root: p };
    }
    const parent = path.dirname(p);
    if (parent === p) break;
    p = parent;
  }
  return null;
}

// The anchor line: what `code-anchor.py --compare` prints, run from the plant
// root, or the not-checked line when the tool is absent, fails, prints
// nothing or times out. Never empty.
async function codeAnchor(pi: ExtensionAPI, cwd: string): Promise<string> {
  try {
    const anchor = findTool(cwd, ANCHOR_CANDIDATES);
    if (!anchor) return ANCHOR_NOT_CHECKED;
    const a = await pi.exec(
      "python3",
      [anchor.tool, "--compare"],
      { timeout: 15_000, cwd: anchor.root },
    );
    const line = (a.stdout || "").trim();
    if (a.code !== 0 || !line) return ANCHOR_NOT_CHECKED;
    return line;
  } catch {
    return ANCHOR_NOT_CHECKED;
  }
}

// The register's summary line, or "" when there is none.
async function statusSummary(pi: ExtensionAPI, cwd: string): Promise<string> {
  try {
    const found = findTool(cwd, CANDIDATES);
    if (!found) return "";
    const r = await pi.exec(
      "python3",
      [found.tool, "--summary", "--root", path.join(found.root, "docs", "graph")],
      { timeout: 15_000, cwd: found.root },
    );
    const summary = (r.stdout || "").trim();
    if ((r.code !== 0 && r.code !== 1) || !summary) return "";
    return (
      "Status register (lifecycle debt in this plant, from frontmatter — " +
      "read it, do not re-infer it): " + summary
    );
  } catch {
    return "";
  }
}

let shown = false;

export default function statusExtension(pi: ExtensionAPI): void {
  pi.on("before_agent_start", async (_event, ctx) => {
    if (shown) return;
    shown = true;
    try {
      const summary = await statusSummary(pi, ctx.cwd);
      const anchor = await codeAnchor(pi, ctx.cwd);
      return {
        message: {
          customType: "cypress-status",
          content: [summary, anchor].filter((part) => part).join("\n"),
          display: true,
        },
      };
    } catch {
      return;
    }
  });
}
