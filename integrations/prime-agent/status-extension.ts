// status-extension.ts — the Prime Agent envelope of the session-start hook core.
//
// It runs `status-hook.py`, the Python core Claude Code runs on SessionStart,
// with the argv envelope on each session event that can leave the model
// without context it was shown: `session_start` (every reason),
// `session_compact`, `session_tree` and `refine_complete`. The core resets the
// session ledger route-hook.py keeps, and returns the status register summary
// and the code anchor line. This file holds that text, keyed by session id,
// and injects it on the next prompt of that session, once. A session with no
// event seen (a missed `session_start`) runs the core as `startup` first. A
// child session (`rlmDepth` above 0) gets nothing, because the core emits
// nothing for it (SPEC-0003, ADR-0024). This file composes no text and writes
// no file.
//
// Installed to `.prime/agent/extensions/status-extension.ts` by
// `install.sh prime-agent`, beside the core at `.prime/agent/hooks/`, and
// auto-discovered like route-extension.ts. It NEVER blocks: a missing core, a
// timeout or any error injects nothing.

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
  const script = path.join(dir, "status-hook.py");
  return fs.existsSync(script) ? script : undefined;
}

function sessionId(ctx: Session): string | undefined {
  try {
    const id = ctx.sessionManager.getSessionId();
    return typeof id === "string" && id ? id : undefined;
  } catch {
    return undefined;
  }
}

// `--session-id=` and `--depth=` for this session, each left out when the host
// does not give it: no session id resets nothing, no depth is a parent.
function sessionOptions(ctx: Session): string[] {
  const options: string[] = [];
  const id = sessionId(ctx);
  if (id) options.push(`--session-id=${id}`);
  try {
    const depth = ctx.sessionManager.getHeader()?.rlmDepth;
    if (Number.isInteger(depth)) options.push(`--depth=${depth}`);
  } catch {
    // no depth: the core treats the session as a parent
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

async function runCore(pi: ExtensionAPI, ctx: Session, source: string): Promise<string | undefined> {
  try {
    const script = corePath(ctx);
    if (!script) return undefined;
    const r = await pi.exec("python3", [script, source, ...sessionOptions(ctx)],
      { timeout: 25_000, cwd: ctx.cwd });
    return additionalContext(r.stdout);
  } catch {
    return undefined;
  }
}

// The text each session is owed, not yet injected, keyed by session id (the
// empty key when the id cannot be read), and every session an event was seen for.
const held = new Map<string, Promise<string | undefined>>();
const seen = new Set<string>();

// The returned promise settles when the core has run, so the reset is written
// before the host, which awaits session handlers, delivers the next prompt to
// route-extension.ts. It never rejects: runCore catches every error.
function reset(pi: ExtensionAPI, ctx: Session, source: string): Promise<string | undefined> {
  const key = sessionId(ctx) ?? "";
  const pending = runCore(pi, ctx, source);
  seen.add(key);
  held.set(key, pending);
  return pending;
}

export default function statusExtension(pi: ExtensionAPI): void {
  pi.on("session_start", async (event, ctx) => {
    await reset(pi, ctx, `--source=${event.reason ?? "unknown"}`);
  });
  pi.on("session_compact", async (_event, ctx) => {
    await reset(pi, ctx, "--source=session_compact");
  });
  pi.on("session_tree", async (_event, ctx) => {
    await reset(pi, ctx, "--source=session_tree");
  });
  pi.on("refine_complete", async (_event, ctx) => {
    await reset(pi, ctx, "--source=refine_complete");
  });
  pi.on("before_agent_start", async (_event, ctx) => {
    try {
      const key = sessionId(ctx) ?? "";
      if (!seen.has(key)) reset(pi, ctx, "--source=startup");
      const pending = held.get(key);
      held.delete(key);
      const content = pending && (await pending);
      if (!content) return;
      return { message: { customType: "cypress-status", content, display: true } };
    } catch {
      return;
    }
  });
}
