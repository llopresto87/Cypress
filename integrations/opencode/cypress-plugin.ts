// cypress-plugin.ts — the OpenCode 2 envelope of the three hook cores.
//
// Claude Code runs three Python cores as hooks: route-hook.py on every prompt,
// status-hook.py when a session starts, and bound-hook.py before every shell
// call. This file runs the same three files on OpenCode 2's plugin hooks and
// hands back what they return. Every decision is the core's: whether a turn is
// routed, the session ledger, whether a child session gets anything, which
// command is refused and the words of the refusal (SPEC-0003, ADR-0024). This
// file composes no text, writes no file and decides nothing.
//
// - ROUTE: on the `prompt` session hook it runs route-hook.py with the argv
//   envelope Prime Agent uses (`--prompt=`, `--session-id=`, `--depth=`, one
//   element each) and adds the core's `additionalContext` to the session as a
//   synthetic message, which reaches the model on that turn before the prompt
//   and stays in the session's history.
// - STATUS: on the first prompt this process sees for a session it first runs
//   status-hook.py (`--source=startup`, `--session-id=`, `--depth=`) and adds
//   what it returns the same way. The core keeps the residency rule: it resets
//   the route ledger and gives a child session nothing.
// - BOUND: on the permission `evaluate` hook, for a shell call, it passes the
//   command to bound-hook.py on stdin in the PreToolUse shape Claude Code uses.
//   When the core refuses (exit 2), the call is refused through the host with
//   the core's stderr as the message, byte for byte. Otherwise the call is left
//   as the host decided it.
//
// The depth is the number of `parentID` links above the session, read with
// `session.get`: a root session has none. A value this host does not give is
// left out, and the core then fails toward inclusion (SPEC-0003 I-1).
//
// Installed to `.opencode/plugins/cypress.ts` by `install.sh opencode`, beside
// the cores at `.opencode/hooks/`. OpenCode 2 loads `.opencode/plugins/` on its
// own and runs TypeScript with Bun, with no build step and no install: the one
// import outside `node:` is the host's bundled `@opencode/plugin`.
//
// Each core runs with no shell (spawn with an argument vector), with a timeout,
// and only from the directory the install placed it in. A missing core, a
// timeout, an error or a hook this host does not offer injects nothing and
// refuses nothing. Each hook is registered in its own guard, so a hook the host
// lacks leaves the others working. The kernel's own FIRST MOVE is the floor, so
// route-first holds without this file.

import { Plugin } from "@opencode/plugin";
import { spawn } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

// The interpreter the cores run on. install.sh writes here the Python it found
// at the seed's floor (SPEC-0001 HOOKS_RUN_ON_THE_FLOOR_INTERPRETER).
const PYTHON = "python3";

// Each wait outlasts every wait inside its core: route-hook.py waits up to
// ROUTER_TIMEOUT for the router; status-hook.py waits for the register and
// then ANCHOR_TIMEOUT for the code anchor; bound-hook.py runs no process.
const ROUTE_TIMEOUT_MS = 20_000;
const STATUS_TIMEOUT_MS = 25_000;
const BOUND_TIMEOUT_MS = 10_000;

// The longest `parentID` chain read before the depth is left out.
const DEPTH_WALK_MAX = 32;

type Ran = { code: number | null; stdout: string; stderr: string };

// The cores sit in `../hooks/` beside this file's own directory; when that
// directory cannot be resolved, in the project's `.opencode/hooks/`. No upward
// walk: a core this install did not place is never run.
function hooksDir(ctx: any): string | undefined {
  try {
    return path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "hooks");
  } catch {
    const dir = projectDir(ctx);
    return dir ? path.join(dir, ".opencode", "hooks") : undefined;
  }
}

function projectDir(ctx: any): string | undefined {
  try {
    const dir = ctx?.location?.directory;
    return typeof dir === "string" && dir ? dir : undefined;
  } catch {
    return undefined;
  }
}

function corePath(ctx: any, name: string): string | undefined {
  try {
    const dir = hooksDir(ctx);
    if (!dir) return undefined;
    const script = path.join(dir, name);
    return fs.existsSync(script) ? script : undefined;
  } catch {
    return undefined;
  }
}

// Run one core with no shell. Resolves with its exit code and output, or with
// nothing on a spawn error or a timeout (the core is then killed). Never rejects.
function runCore(ctx: any, name: string, args: string[], input: string, timeoutMs: number): Promise<Ran | undefined> {
  return new Promise((resolve) => {
    let settled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const done = (r: Ran | undefined) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve(r);
    };
    const script = corePath(ctx, name);
    if (!script) return done(undefined);
    try {
      const child = spawn(PYTHON, ["-S", script, ...args], {
        cwd: projectDir(ctx) ?? process.cwd(),
        shell: false,
        stdio: ["pipe", "pipe", "pipe"],
      });
      timer = setTimeout(() => {
        try { child.kill("SIGKILL"); } catch { /* already gone */ }
        done(undefined);
      }, timeoutMs);
      const out: Buffer[] = [];
      const err: Buffer[] = [];
      child.stdout?.on("data", (b: Buffer) => out.push(b));
      child.stderr?.on("data", (b: Buffer) => err.push(b));
      child.on("error", () => done(undefined));
      child.on("close", (code: number | null) =>
        done({ code, stdout: Buffer.concat(out).toString("utf8"), stderr: Buffer.concat(err).toString("utf8") }));
      child.stdin?.on("error", () => { /* a core that does not read stdin */ });
      child.stdin?.end(input);
    } catch {
      done(undefined);
    }
  });
}

// The core's `hookSpecificOutput.additionalContext`, or nothing when it printed
// nothing or no hook envelope.
function additionalContext(r: Ran | undefined): string | undefined {
  try {
    const text = r ? JSON.parse(r.stdout)?.hookSpecificOutput?.additionalContext : undefined;
    return typeof text === "string" && text ? text : undefined;
  } catch {
    return undefined;
  }
}

// The `parentID` of a session, "" for a session with none, or nothing when the
// host did not answer.
async function parentOf(ctx: any, sessionID: string): Promise<string | undefined> {
  try {
    const got = await ctx.session.get({ sessionID });
    if (!got || typeof got !== "object") return undefined;
    const s = "parentID" in got || !("data" in got) ? got : got.data;
    const parent = s?.parentID;
    return typeof parent === "string" && parent ? parent : "";
  } catch {
    return undefined;
  }
}

// How many `parentID` links sit above the session: 0 for a root session, or
// nothing when the host did not answer for the session itself. A chain the
// host stops answering part way up is still a child: the links read so far.
async function depthOf(ctx: any, sessionID: string): Promise<number | undefined> {
  let id = sessionID;
  for (let depth = 0; depth < DEPTH_WALK_MAX; depth++) {
    const parent = await parentOf(ctx, id);
    if (parent === undefined) return depth > 0 ? depth : undefined;
    if (!parent) return depth;
    id = parent;
  }
  return undefined;
}

// `--session-id=` and `--depth=`, each left out when the host does not give it.
function sessionOptions(sessionID: unknown, depth: number | undefined): string[] {
  const options: string[] = [];
  if (typeof sessionID === "string" && sessionID) options.push(`--session-id=${sessionID}`);
  if (Number.isInteger(depth)) options.push(`--depth=${depth}`);
  return options;
}

// True when the host marks the turn as one it wrote itself, not a typed prompt.
function synthetic(a: any): boolean {
  try {
    return a?.metadata?.synthetic === true || a?.delivery === "synthetic" || a?.delivery?.synthetic === true;
  } catch {
    return false;
  }
}

// `resume: false` adds the message without starting a turn of its own: the
// prompt being admitted starts the turn, and the message reaches the model in
// it, before the prompt. Without it each message starts a model call by itself.
async function inject(ctx: any, sessionID: string, text: string | undefined): Promise<void> {
  if (!text) return;
  try {
    await ctx.session.synthetic({ sessionID, text, resume: false });
  } catch {
    // never block a prompt
  }
}

// The sessions this process has run status-hook.py for.
const started = new Set<string>();

async function onPrompt(ctx: any, a: any): Promise<void> {
  const sessionID = a?.sessionID;
  const text = a?.prompt?.text;
  if (typeof sessionID !== "string" || !sessionID) return;
  if (typeof text !== "string" || !text.trim() || synthetic(a)) return;
  const depth = await depthOf(ctx, sessionID);
  const options = sessionOptions(sessionID, depth);
  if (!started.has(sessionID)) {
    started.add(sessionID);
    const status = await runCore(ctx, "status-hook.py", ["--source=startup", ...options], "", STATUS_TIMEOUT_MS);
    await inject(ctx, sessionID, additionalContext(status));
  }
  const route = await runCore(ctx, "route-hook.py", [`--prompt=${text}`, ...options], "", ROUTE_TIMEOUT_MS);
  await inject(ctx, sessionID, additionalContext(route));
}

async function onEvaluate(ctx: any, a: any): Promise<void> {
  if (a?.action !== "shell") return;
  const command = Array.isArray(a.resources) ? a.resources[0] : undefined;
  if (typeof command !== "string" || !command.trim()) return;
  const input = JSON.stringify({ hook_event_name: "PreToolUse", tool_name: "Bash", tool_input: { command } });
  const r = await runCore(ctx, "bound-hook.py", [], input, BOUND_TIMEOUT_MS);
  if (r && r.code === 2 && r.stderr) {
    a.effect = "deny";
    a.message = r.stderr;
  }
}

export default Plugin.define({
  id: "cypress",
  setup(ctx: any) {
    try {
      ctx.session.hook("prompt", async (a: any) => {
        try {
          await onPrompt(ctx, a);
        } catch {
          // never block a prompt
        }
      });
    } catch {
      // this host offers no prompt hook: nothing is injected
    }
    try {
      ctx.permission.hook("evaluate", async (a: any) => {
        try {
          await onEvaluate(ctx, a);
        } catch {
          // a guard that fails allows the call
        }
      });
    } catch {
      // this host offers no evaluate hook: no command is refused
    }
  },
});
