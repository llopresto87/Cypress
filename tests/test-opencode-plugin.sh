#!/usr/bin/env bash
# The OpenCode 2 envelope of the hook cores: `integrations/opencode/cypress-plugin.ts`
# runs route-hook.py, status-hook.py and bound-hook.py and hands back what they
# return, composing no text, writing no file and deciding nothing (SPEC-0003,
# ADR-0024). Two parts:
#
#   P1-P8  structural, always run: what the plugin imports, how it spawns, the
#          timeout, the guard around each hook registration, the PYTHON line
#          install.sh rewrites.
#   F1-F7  a fixture run, when `bun` is on PATH: the plugin is loaded against a
#          stub host context in a temp plant holding the real cores, and every
#          text it injects or refusal it makes is compared byte for byte with
#          the same core run directly. Without bun this part prints SKIPPED with
#          the reason and a `SKIPPED-PART:` line, so the gate summary names the
#          step as passed in part; with CYPRESS_REQUIRE_BUN=1 (the CI job that
#          installs bun) a missing bun fails the file instead.
#
# Contracts held here: X520 OPENCODE_PLUGIN_IS_A_THIN_ENVELOPE (P1-P8),
# X521 OPENCODE_PLUGIN_INJECTS_THE_CORES_TEXT_ONCE (F1, F2, F4) and
# X522 OPENCODE_SHELL_GUARD_REFUSES_WITH_THE_CORES_REASON (F3, F5, F6, F7) and
# X930 OPENCODE_PLUGIN_CASES_RUN_IN_CI (the require-bun mode).
#
# Synthetic data only. The stub `@opencode/plugin` is a two-line module in the
# temp plant's node_modules; the host's own module is bundled in the host.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN="$ROOT/integrations/opencode/cypress-plugin.ts"
CORES="$ROOT/integrations/claude-code"
BUN="${CYPRESS_BUN:-bun}"   # X930 points it at a name that cannot be found
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$PLUGIN" ]] || fail "P1 plugin not found: $PLUGIN"
echo "  P1 the plugin file exists — OK"

# --- structural ---------------------------------------------------------------
python3 - "$PLUGIN" "$CORES" <<'PY' || fail "structural checks (named above)"
import re, sys
from pathlib import Path

src = Path(sys.argv[1]).read_text(encoding="utf-8")
cores = Path(sys.argv[2])
code = re.sub(r"//[^\n]*", "", src)                 # comments out; strings stay
problems = []

def check(cond, msg):
    if not cond:
        problems.append(msg)

imports = re.findall(r"""^\s*import\b[^;]*?from\s+["']([^"']+)["']""", code, re.M)
imports += re.findall(r"""\brequire\(\s*["']([^"']+)["']""", code)
imports += re.findall(r"""\bimport\(\s*["']([^"']+)["']""", code)
bad = [m for m in imports if m != "@opencode/plugin" and not m.startswith("node:")]
check(imports and not bad, f"P2 imports outside @opencode/plugin and node:*: {bad}")
check("@opencode/plugin" in imports, "P2 the plugin does not import @opencode/plugin")
oks = ["P2 imports only @opencode/plugin and node:* (no package.json, no install)"]

for pat, what in ((r"\bexec(?:Sync)?\(", "exec("), (r"\bexecFile(?:Sync)?\(", "execFile("),
                  (r"shell:\s*true", "shell: true"), (r"\bspawnSync\(", "spawnSync("),
                  (r"Bun\.\$", "Bun.$"), (r"\beval\(", "eval(")):
    check(not re.search(pat, code), f"P3 the plugin uses {what}")
spawns = re.findall(r"\bspawn\(\s*PYTHON\s*,\s*\[", code)
check(len(spawns) == 1, f"P3 expected one `spawn(PYTHON, [...])`, found {len(spawns)}")
check(re.search(r"shell:\s*false", code), "P3 the spawn does not say `shell: false`")
check("-S" in code and '"-S", script' in code, "P3 the core is not run as `PYTHON -S <script>`")
oks.append("P3 one spawn of PYTHON with an argument vector, no shell, no exec")

timeouts = dict(re.findall(r"^const (\w+_TIMEOUT_MS) = ([\d_]+);$", code, re.M))
check(set(timeouts) == {"ROUTE_TIMEOUT_MS", "STATUS_TIMEOUT_MS", "BOUND_TIMEOUT_MS"},
      f"P4 timeout constants {sorted(timeouts)}")
check(re.search(r"setTimeout\(", code) and re.search(r"\.kill\(", code),
      "P4 a timed-out core is not killed")
core = (cores / "route-hook.py").read_text(encoding="utf-8")
router = re.search(r"^ROUTER_TIMEOUT = (\d+)", core, re.M)
status = (cores / "status-hook.py").read_text(encoding="utf-8")
anchor = re.search(r"^ANCHOR_TIMEOUT = ([\d.]+)", status, re.M)
waits = sum(float(v) for v in re.findall(r"\btimeout=([\d.]+)", status))
if router and "ROUTE_TIMEOUT_MS" in timeouts:
    check(int(timeouts["ROUTE_TIMEOUT_MS"].replace("_", "")) > int(router[1]) * 1000,
          "P4 ROUTE_TIMEOUT_MS is not above route-hook.py's ROUTER_TIMEOUT")
if anchor and "STATUS_TIMEOUT_MS" in timeouts:
    check(int(timeouts["STATUS_TIMEOUT_MS"].replace("_", "")) > (waits + float(anchor[1])) * 1000,
          "P4 STATUS_TIMEOUT_MS is not above status-hook.py's waits plus ANCHOR_TIMEOUT")
oks.append("P4 each core runs under a timeout above its own waits, and is killed past it")

# Every registration sits inside its own try block, and nothing else registers.
regs = [m.start() for m in re.finditer(r"ctx\.(?:session|permission)\.hook\(", code)]
check(len(regs) == 2, f"P5 expected two hook registrations, found {len(regs)}")
for pos in regs:
    head = code[:pos].rstrip()
    check(head.endswith("try {"), f"P5 a hook registration is not the first statement of its own try block: "
                                  f"{code[pos:pos+40]!r}")
check(re.search(r'ctx\.session\.hook\("prompt"', code), "P5 no prompt hook")
check(re.search(r'ctx\.permission\.hook\("evaluate"', code), "P5 no permission evaluate hook")
oks.append("P5 two registrations (prompt, evaluate), each in its own try block")

# install.sh's render_hook_python rewrites exactly this line in a .ts source.
check(len(re.findall(r'^const PYTHON = "python3";$', src, re.M)) == 1,
      'P6 the plugin lacks exactly one `const PYTHON = "python3";` line for install.sh to rewrite')
oks.append("P6 one `const PYTHON = \"python3\";` line, the shape install.sh rewrites")

# The envelope composes no text and writes no file.
for pat, what in ((r"\bfs\.(?:write|append|mkdir|rm|unlink|rename|copy|create)\w*\(", "a filesystem write"),
                  (r"\bBun\.write\(", "Bun.write"), (r"\bconsole\.\w+\(", "console output"),
                  (r"\benv\b", "the environment")):
    check(not re.search(pat, code), f"P7 the plugin names {what}")
check(not re.search(r"graph-lint|status-register|code-anchor", code),
      "P7 the plugin names a tool the core runs; it must call the core alone")
check(re.search(r"synthetic\(\{\s*sessionID,\s*text,\s*resume:\s*false\s*\}\)", code),
      "P7 injection is not `session.synthetic({ sessionID, text, resume: false })`: without `resume: false` "
      "each injected message starts a model call of its own")
oks.append("P7 no write, no console, no environment, no router: the cores alone")

for name in ("route-hook.py", "status-hook.py", "bound-hook.py"):
    check(f'"{name}"' in code, f"P8 the plugin does not run {name}")
check(re.search(r'import\.meta\.url\)\),\s*"\.\.",\s*"hooks"\)', code),
      "P8 the cores are not looked up in ../hooks beside the plugin's own directory")
check(re.search(r'"\.opencode",\s*"hooks"', code), "P8 no `.opencode/hooks` fallback")
check(not re.search(r"\bwhile\s*\(", code) and len(re.findall(r"path\.dirname\(", code)) == 1,
      "P8 the core lookup walks upward")
oks.append("P8 the three cores, from ../hooks or .opencode/hooks, no upward walk")

if problems:
    print("", file=sys.stderr)
    for p in problems:
        print(f"FAIL: {p}", file=sys.stderr)
    sys.exit(1)
for ok in oks:
    print(f"  {ok} — OK")
PY

# --- X930 OPENCODE_PLUGIN_CASES_RUN_IN_CI: the require-bun mode ----------------
# This file run again with a bun that cannot be found: by default it passes in
# part and names the skipped half on a SKIPPED-PART line the gate runner reads;
# with CYPRESS_REQUIRE_BUN=1 (the CI job's setting) it exits non-zero instead.
if [[ -z "${CYPRESS_PLUGIN_SELFCHECK:-}" ]]; then
  set +e
  soft="$(CYPRESS_PLUGIN_SELFCHECK=1 CYPRESS_BUN=cypress-no-such-bun CYPRESS_REQUIRE_BUN= \
          bash "${BASH_SOURCE[0]}" 2>&1)"; soft_rc=$?
  hard="$(CYPRESS_PLUGIN_SELFCHECK=1 CYPRESS_BUN=cypress-no-such-bun CYPRESS_REQUIRE_BUN=1 \
          bash "${BASH_SOURCE[0]}" 2>&1)"; hard_rc=$?
  set -e
  [[ $soft_rc -eq 0 ]] || fail "X930 without bun and without CYPRESS_REQUIRE_BUN the file exits $soft_rc, expected 0: $soft"
  grep -q '^SKIPPED-PART: fixture half skipped: bun not found$' <<<"$soft" \
    || fail "X930 without bun the file prints no 'SKIPPED-PART: fixture half skipped: bun not found' line: $soft"
  [[ $hard_rc -ne 0 ]] || fail "X930 CYPRESS_REQUIRE_BUN=1 without bun exits 0; the CI job would pass with the fixture half unrun"
  grep -q 'CYPRESS_REQUIRE_BUN' <<<"$hard" || fail "X930 the require-bun failure does not name CYPRESS_REQUIRE_BUN: $hard"
  echo "  X930 OPENCODE_PLUGIN_CASES_RUN_IN_CI: without bun the file passes in part with a SKIPPED-PART line, and CYPRESS_REQUIRE_BUN=1 makes it fail — OK"
fi

# --- fixture run under bun ----------------------------------------------------
if ! command -v "$BUN" >/dev/null 2>&1; then
  if [[ "${CYPRESS_REQUIRE_BUN:-}" == 1 ]]; then
    fail "F1-F7 fixture run: bun is not on PATH and CYPRESS_REQUIRE_BUN=1 requires it; the fixture half cannot run"
  fi
  echo "  F1-F7 fixture run: SKIPPED — bun is not on PATH, so the plugin cannot be loaded here; only P1-P8 ran"
  echo "SKIPPED-PART: fixture half skipped: bun not found"
  echo "test-opencode-plugin: PASS (structural only; the fixture run was SKIPPED)"
  exit 0
fi

# make_plant DIR [no-cores]: a temp plant holding the plugin, the real cores at
# .opencode/hooks/, a two-node graph with the real router, and the stub host module.
make_plant() {
  local d="$1"
  mkdir -p "$d/.git" "$d/.cypress" "$d/.opencode/plugins" "$d/.opencode/hooks" \
           "$d/docs/graph/nodes" "$d/node_modules/@opencode/plugin"
  cp "$PLUGIN" "$d/.opencode/plugins/cypress.ts"
  if [[ "${2:-}" != no-cores ]]; then
    for h in route-hook.py status-hook.py bound-hook.py; do cp "$CORES/$h" "$d/.opencode/hooks/$h"; done
  fi
  for f in graph-lint.py frontmatter.py source_paths.py; do
    cp "$ROOT/templates/knowledge-graph/$f" "$d/docs/graph/$f"
  done
  printf '%s\n' '---' 'id: root' 'tier: 2' 'kind: root' 'title: minimal plant root' \
    'owns: [root.identity]' 'requires: []' 'peers: [subsystem.widgets]' \
    'load_when: ["anything"]' 'est_tokens: 100' '---' '# root' > "$d/docs/graph/nodes/root.md"
  printf '%s\n' '---' 'id: subsystem.widgets' 'tier: 2' 'kind: subsystem' 'title: widgets subsystem' \
    'owns: [widgets.core]' 'requires: [root]' 'load_when: ["widgets"]' 'est_tokens: 100' '---' \
    '# widgets' > "$d/docs/graph/nodes/subsystem.widgets.md"
  printf '{"name":"@opencode/plugin","type":"module","main":"index.js"}\n' \
    > "$d/node_modules/@opencode/plugin/package.json"
  printf 'export const Plugin = { define: (d) => d };\n' > "$d/node_modules/@opencode/plugin/index.js"
}

# The driver loads the plugin against a stub host context and runs one scenario.
# Sessions: ses_root (no parentID), ses_child (parent ses_root), ses_gone
# (session.get throws). It prints one JSON document of what the plugin did.
cat > "$WORK/driver.ts" <<'TS'
const [pluginPath, plantDir, scenario] = process.argv.slice(2);
const registered: Record<string, (a: any) => Promise<void>> = {};
const synthetic: any[] = [];
const sessions: Record<string, any> = { ses_root: { id: "ses_root" }, ses_child: { id: "ses_child", parentID: "ses_root" } };
const noHooks = scenario === "no-session-hook";
const ctx: any = {
  location: { directory: plantDir },
  session: {
    hook(name: string, fn: any) { if (noHooks) throw new Error("no such hook"); registered["session." + name] = fn; },
    async get({ sessionID }: any) { if (!(sessionID in sessions)) throw new Error("not found"); return sessions[sessionID]; },
    async synthetic(x: any) { synthetic.push(x); },
  },
  permission: { hook(name: string, fn: any) { registered["permission." + name] = fn; } },
};
const out: any = { scenario, threw: null, registered: [], synthetic, effects: {}, ms: {} };
async function prompt(label: string, sessionID: string, text: string, extra: any = {}) {
  const t = Date.now();
  await registered["session.prompt"]?.({ sessionID, messageID: "msg_" + label, prompt: { text, files: [] }, metadata: {}, ...extra });
  out.ms[label] = Date.now() - t;
}
async function evaluate(label: string, command: string, action = "shell") {
  const a: any = { sessionID: "ses_root", agent: "build", action, resources: [command], source: "test", effect: "ask" };
  const t = Date.now();
  await registered["permission.evaluate"]?.(a);
  out.ms[label] = Date.now() - t;
  out.effects[label] = { effect: a.effect, message: a.message ?? null };
}
try {
  const mod = await import(pluginPath);
  mod.default.setup(ctx);
  out.registered = Object.keys(registered).sort();
  const P = process.env.FIX_PROMPT!;
  if (scenario === "main") {
    await prompt("root1", "ses_root", P);
    await prompt("child", "ses_child", P);
    await prompt("root2", "ses_root", P);
    await prompt("synthetic", "ses_root", P, { metadata: { synthetic: true } });
    await prompt("empty", "ses_root", "   ");
    await evaluate("refused", process.env.FIX_REFUSED!);
    await evaluate("allowed", process.env.FIX_ALLOWED!);
    await evaluate("not-shell", process.env.FIX_REFUSED!, "edit");
  } else if (scenario === "gone") {
    await prompt("gone", "ses_gone", P);
  } else {
    await prompt("root1", "ses_root", P);
    await evaluate("refused", process.env.FIX_REFUSED!);
  }
} catch (e) {
  out.threw = String(e);
}
console.log(JSON.stringify(out));
TS

export FIX_PROMPT="zq-sentinel-oc01 widgets ledger work for the opencode fixture"
export FIX_REFUSED="npm install"
export FIX_ALLOWED="ls -la"

drive() {  # $1 = plant  $2 = scenario  -> JSON on stdout
  (cd "$WORK" && "$BUN" run "$WORK/driver.ts" "$1/.opencode/plugins/cypress.ts" "$1" "$2")
}

make_plant "$WORK/main"
make_plant "$WORK/twin"
make_plant "$WORK/gone"
make_plant "$WORK/gone-twin"
make_plant "$WORK/missing" no-cores
make_plant "$WORK/nohook"
make_plant "$WORK/slow"
# F6: cores that outlast a shortened wait. The plugin's timeout constants are
# rewritten in this copy only, so the case runs in seconds.
for h in route-hook.py status-hook.py bound-hook.py; do
  printf 'import time\ntime.sleep(6)\nprint("{\\"hookSpecificOutput\\": {\\"additionalContext\\": \\"zq-late\\"}}")\n' \
    > "$WORK/slow/.opencode/hooks/$h"
done
python3 - "$WORK/slow/.opencode/plugins/cypress.ts" <<'PY'
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t, n = re.subn(r"^(const (?:ROUTE|STATUS|BOUND)_TIMEOUT_MS = )[\d_]+;$", r"\g<1>1_000;", t, flags=re.M)
assert n == 3, n
open(p, "w", encoding="utf-8").write(t)
PY

drive "$WORK/main" main > "$WORK/main.json"
drive "$WORK/gone" gone > "$WORK/gone.json"
drive "$WORK/missing" missing > "$WORK/missing.json"
drive "$WORK/nohook" no-session-hook > "$WORK/nohook.json"
drive "$WORK/slow" slow > "$WORK/slow.json"

python3 - "$WORK" <<'PY' || fail "fixture run (named above)"
import json, subprocess, sys
from pathlib import Path

W = Path(sys.argv[1])
P, REFUSED, ALLOWED = ("zq-sentinel-oc01 widgets ledger work for the opencode fixture", "npm install", "ls -la")
problems = []

def check(cond, msg):
    if not cond:
        problems.append(msg)

def core(plant, name, args, stdin=""):
    """The core run directly, the way the plugin runs it: PYTHON -S, cwd the plant."""
    return subprocess.run([sys.executable, "-S", str(W / plant / ".opencode" / "hooks" / name), *args],
                          input=stdin, capture_output=True, text=True, cwd=str(W / plant), timeout=60)

def ctx_of(r):
    out = r.stdout.strip()
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else None

def load(name):
    return json.loads((W / f"{name}.json").read_text())

m = load("main")
check(m["threw"] is None, f"F1 the plugin threw: {m['threw']}")
check(m["registered"] == ["permission.evaluate", "session.prompt"], f"F1 registered {m['registered']}")

# The twin plant runs the cores directly in the order the plugin must run them.
root = ["--session-id=ses_root", "--depth=0"]
want = [ctx_of(core("twin", "status-hook.py", ["--source=startup", *root])),
        ctx_of(core("twin", "route-hook.py", [f"--prompt={P}", *root]))]
child = ["--session-id=ses_child", "--depth=1"]
check(ctx_of(core("twin", "status-hook.py", ["--source=startup", *child])) is None
      and ctx_of(core("twin", "route-hook.py", [f"--prompt={P}", *child])) is None,
      "harness: the cores injected into a child session")
want.append(ctx_of(core("twin", "route-hook.py", [f"--prompt={P}", *root])))
check(all(want), f"harness: a core returned nothing in the twin plant: {want}")
check(want[1] != want[2], "harness: the second route text equals the first, so it cannot tell a status re-run apart")
got = m["synthetic"]
check([x.get("sessionID") for x in got] == ["ses_root"] * 3,
      f"F2 synthetic calls went to {[x.get('sessionID') for x in got]}, expected three to ses_root and none to the child")
check([x.get("text") for x in got] == want,
      "F2 the injected texts differ from the cores' additionalContext, byte for byte:\n"
      f"    got  {[x.get('text') for x in got]!r}\n    want {want!r}")
check(all(x.get("resume") is False for x in got), f"F2 a synthetic call without resume false: {got!r}")
print("  F1 the plugin loads and registers prompt and evaluate — OK" if not problems else "", end="")
print("\n  F2 root prompt: status then route text, each byte-identical to its core; second prompt: the core's "
      "reminder, status not re-run; child, synthetic-marked and empty prompts: nothing — OK" if not problems else "")

b = core("twin", "bound-hook.py", [], json.dumps(
    {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": REFUSED}}))
check(b.returncode == 2 and b.stderr, f"harness: bound-hook.py did not refuse {REFUSED!r}")
e = m["effects"]
check(e.get("refused") == {"effect": "deny", "message": b.stderr},
      f"F3 refused command: {e.get('refused')!r}, expected deny with the core's stderr {b.stderr!r}")
check(e.get("allowed") == {"effect": "ask", "message": None}, f"F3 allowed command was changed: {e.get('allowed')!r}")
check(e.get("not-shell") == {"effect": "ask", "message": None}, f"F3 a non-shell action was changed: {e.get('not-shell')!r}")
print("  F3 a refused command is denied with the core's stderr byte for byte; an allowed one and a non-shell "
      "action are left as the host decided — OK" if not problems else "")

g = load("gone")
gw = ctx_of(core("gone-twin", "route-hook.py", [f"--prompt={P}", "--session-id=ses_gone"]))
gs = ctx_of(core("gone-twin", "status-hook.py", ["--source=startup", "--session-id=ses_gone"]))
check(g["threw"] is None and [x.get("text") for x in g["synthetic"]] == [gs, gw],
      f"F4 a session the host does not answer for: expected the cores run with no --depth "
      f"(the full injection), got {g['synthetic']!r}")
print("  F4 session.get fails: --depth is left out and the cores' text is injected (fail toward inclusion) — OK"
      if not problems else "")

for name, label in (("missing", "F5 cores missing"), ("slow", "F6 cores past the timeout")):
    r = load(name)
    check(r["threw"] is None, f"{label}: the plugin threw: {r['threw']}")
    check(r["synthetic"] == [], f"{label}: something was injected: {r['synthetic']!r}")
    check(r["effects"].get("refused") == {"effect": "ask", "message": None},
          f"{label}: the command was not left as the host decided it (ask): {r['effects'].get('refused')!r}")
s = load("slow")
check(s["ms"].get("root1", 99_999) < 4_000 and s["ms"].get("refused", 99_999) < 3_000,
      f"F6 the plugin waited past its timeout: {s['ms']}")
print("  F5 cores missing: nothing injected, nothing refused, no throw — OK" if not problems else "")
print("  F6 cores slower than the timeout: killed, nothing injected, nothing refused — OK" if not problems else "")

n = load("nohook")
check(n["threw"] is None and n["registered"] == ["permission.evaluate"]
      and n["effects"].get("refused", {}).get("effect") == "deny",
      f"F7 a host without the prompt hook: {n!r}")
print("  F7 a host that throws on the prompt hook: setup survives and the guard still refuses — OK"
      if not problems else "")

if problems:
    for p in problems:
        print(f"FAIL: {p}", file=sys.stderr)
    sys.exit(1)
PY

echo "  held: X520 OPENCODE_PLUGIN_IS_A_THIN_ENVELOPE, X521 OPENCODE_PLUGIN_INJECTS_THE_CORES_TEXT_ONCE, X522 OPENCODE_SHELL_GUARD_REFUSES_WITH_THE_CORES_REASON, X930 OPENCODE_PLUGIN_CASES_RUN_IN_CI"
echo "test-opencode-plugin: PASS"
