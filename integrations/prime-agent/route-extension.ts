// route-extension.ts — the Prime Agent envelope of the per-prompt hook core.
//
// On `before_agent_start` (fired after a prompt is submitted, before the agent
// loop) it runs `route-hook.py`, the Python core Claude Code runs on every
// prompt, with the argv envelope, and injects the `additionalContext` the core
// returns as a prepended message. Every decision is the core's: whether the
// turn is routed, the router call, the session ledger and the text (SPEC-0003,
// ADR-0024). This file composes no text and writes no file.
//
// The prompt travels as one `--prompt=` element, and pi.exec spawns without a
// shell. The session id and the session header's `rlmDepth` go beside it, so
// the core keeps one ledger per session and injects nothing into a child
// session. A value this host does not give is left out, and the core then
// fails toward inclusion (I-1): no session id is the full injection on every
// prompt, no depth is a routed prompt.
//
// Installed to `.prime/agent/extensions/route-extension.ts` by
// `install.sh prime-agent`, beside the core at `.prime/agent/hooks/`. Prime
// Agent auto-discovers `.prime/agent/extensions/` and transpiles .ts at
// runtime (jiti), with no build step; under jiti `__dirname` is this file's
// own directory. The bundled `.prime/agent/settings.json` also lists it.
//
// It NEVER blocks: a missing core, a timeout or any error injects nothing. The
// kernel's own FIRST MOVE is the floor, so route-first holds without it.

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

type Session = {
  cwd: string;
  sessionManager: { getSessionId(): string; getHeader(): { rlmDepth?: unknown } | null };
};

// The core sits in `../hooks/` beside this file's directory; when that
// directory cannot be resolved, in the plant's `.prime/agent/hooks/`. No
// upward walk: a core this install did not place is never run.
function corePath(ctx: Session): string | undefined {
  const dir = typeof __dirname === "string"
    ? path.join(__dirname, "..", "hooks")
    : path.join(ctx.cwd, ".prime", "agent", "hooks");
  const script = path.join(dir, "route-hook.py");
  return fs.existsSync(script) ? script : undefined;
}

// `--session-id=` and `--depth=` for this session, each left out when the host
// does not give it.
function sessionOptions(ctx: Session): string[] {
  const options: string[] = [];
  try {
    const id = ctx.sessionManager.getSessionId();
    if (typeof id === "string" && id) options.push(`--session-id=${id}`);
  } catch {
    // no session id: the core injects in full
  }
  try {
    const depth = ctx.sessionManager.getHeader()?.rlmDepth;
    if (Number.isInteger(depth)) options.push(`--depth=${depth}`);
  } catch {
    // no depth: the core routes the prompt
  }
  return options;
}

// The core's `hookSpecificOutput.additionalContext`, or nothing when it printed
// nothing or no hook envelope.
function additionalContext(stdout: string): string | undefined {
  try {
    const text = JSON.parse(stdout)?.hookSpecificOutput?.additionalContext;
    return typeof text === "string" && text ? text : undefined;
  } catch {
    return undefined;
  }
}

export default function routeExtension(pi: ExtensionAPI): void {
  pi.on("before_agent_start", async (event, ctx) => {
    try {
      const script = corePath(ctx);
      if (!script) return;
      const options = [`--prompt=${event.prompt ?? ""}`, ...sessionOptions(ctx)];
      // The turn's origin, when the host gives one. Prime Agent's event carries
      // none today, so a delivered agent message is told apart by the core's
      // leading marker, and a child session by its depth.
      const origin = (event as { origin?: unknown }).origin;
      if (typeof origin === "string") options.push(`--origin=${origin}`);
      const r = await pi.exec("python3", [script, ...options], { timeout: 20_000, cwd: ctx.cwd });
      const content = additionalContext(r.stdout);
      if (!content) return;
      return { message: { customType: "cypress-route", content, display: true } };
    } catch {
      // never block a prompt
      return;
    }
  });
}
