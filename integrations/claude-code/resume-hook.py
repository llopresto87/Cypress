#!/usr/bin/env python3
"""resume-hook.py — a PreToolUse guard on SendMessage: new work goes to a fresh
worker, not to one whose prompt cache has expired (`delegation.continuation`).

Installed to `.claude/resume-hook.py` and wired in `.claude/settings.json` under
hooks.PreToolUse with `"matcher": "SendMessage"`. The host passes
`{"tool_name", "tool_input": {"to", "message"}, "transcript_path"}` on stdin.
Claude Code keeps a worker's transcript at
`<transcript without .jsonl>/subagents/agent-<to>.jsonl`; its mtime is the
worker's last activity. A worker idle longer than its cache lifetime has no warm
cache, so a message re-reads its whole context uncached and acts on state other
lanes may have changed.

The lifetime is the one the host is configured to give a worker, resolved by
the host's documented precedence, first match wins, over what a hook can read:
FORCE_PROMPT_CACHING_5M; CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL; the
`subagentPromptCacheTtl` setting (`.claude/settings.local.json`, then
`.claude/settings.json` under CLAUDE_PROJECT_DIR, then the user's
`~/.claude/settings.json`); the worker's agent definition (`experimental:
cacheTtl`, its `.claude/agents/` file found by the `agentType` of
`agent-<to>.meta.json`); ENABLE_PROMPT_CACHING_1H; the default. A variable is
read from the environment, then from the `env` block of those settings files.
Only `5m` and `1h` count; any other value, an unreadable source, and the
default give COLD_AFTER (300 s), the shorter lifetime, so the guard never
assumes a warm cache it cannot prove. A resolved `1h` counts only when the
worker's own transcript confirms it: the latest message with cache-creation
tokens (last record per message id) wrote `ephemeral_1h_input_tokens`; a
5m-only write, or none, gives 300 s, since a host can ignore the setting. A frontmatter `1h` also gives 300 s: the
host ignores it while a subscription draws on usage credits, which a hook
cannot see. Managed settings are not read. Two cases are told apart from the
transcript's tail:

- the host cut the worker off: its last assistant record is the host's API
  error (`isApiErrorMessage`: a usage or rate limit, a server or network
  error). It still owes its handback, so the resume is allowed.
- anything else, a worker that handed back above all: the message is new work
  for an old context and is refused (exit 2, reason on stderr), unless its
  first line starts `continuation:`, the caller's declaration that the
  follow-up is small and needs that context, or that the worker stopped
  without an error record (its parent session died).

Exit 0 = allow (also: another tool, unreadable stdin, unknown worker, internal
error). Exit 2 = refuse. A bug degrades to no guard; it never blocks every
message.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

COLD_AFTER = 300             # seconds: the default and the safe worker cache lifetime; past
                             # it a message rewrites the whole context (Claude Code: worker
                             # calls after 5-10 min idle wrote ~217K tokens each)
LIFETIMES = {"5m": 300, "1h": 3600}
TTL_VAR = "CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL"
FORCE_5M, ENABLE_1H = "FORCE_PROMPT_CACHING_5M", "ENABLE_PROMPT_CACHING_1H"
TAIL_BYTES = 256 * 1024      # read this much of the transcript's end for its last record
DECLARATION = "continuation:"
AGENT_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def last_assistant(worker: Path) -> dict:
    """The worker's last assistant record, read from the transcript's tail."""
    with worker.open("rb") as f:
        size = f.seek(0, 2)
        f.seek(max(0, size - TAIL_BYTES))
        lines = f.read().decode("utf-8", "replace").splitlines()
    for line in reversed(lines):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("type") == "assistant":
            return rec
    return {}


def handed_back(rec: dict) -> bool:
    content = (rec.get("message") or {}).get("content") or []
    return any(isinstance(b, dict) and b.get("name") == "SubagentHandback" for b in content)


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def frontmatter_ttl(agents: Path, agent_type: str):
    """`experimental: cacheTtl` of the agent file whose `name:` is agent_type."""
    if not agents.is_dir():
        return None
    for f in sorted(agents.glob("*.md")):
        lines = f.read_text(encoding="utf-8", errors="replace").split("\n")
        if not lines or lines[0].strip() != "---":
            continue
        head = []
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            head.append(ln)
        if f"name: {agent_type}" not in [h.strip() for h in head]:
            continue
        nested = False
        for ln in head:
            if not ln.startswith((" ", "\t")):
                nested = ln.strip() == "experimental:"
            elif nested and ln.strip().startswith("cacheTtl:"):
                return ln.split(":", 1)[1].strip().strip("'\"")
        return None
    return None


def wrote_1h(worker: Path) -> bool:
    """Whether the host's last cache write for this worker was a one-hour one:
    the last record per message id wins (the one home of that reading is
    `transcript_usage` in tools/brief.py, which a plant's .claude/ lacks), and
    the latest message with cache-creation tokens decides."""
    last = {}
    for line in worker.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        m = r.get("message") if isinstance(r, dict) and r.get("type") == "assistant" else None
        if isinstance(m, dict) and isinstance(m.get("usage"), dict):
            last.pop(m.get("id") or f"line{len(last)}", None)
            last[m.get("id") or f"line{len(last)}"] = m["usage"]
    for u in reversed(list(last.values())):
        if (u.get("cache_creation_input_tokens") or 0) > 0:
            return ((u.get("cache_creation") or {}).get("ephemeral_1h_input_tokens") or 0) > 0
    return False


def lifetime(environ, project: Path | None, home: Path | None, meta: Path) -> int:
    """The worker cache lifetime in seconds, by the host's precedence."""
    files = [project / ".claude" / n for n in ("settings.local.json", "settings.json")] if project else []
    if home:
        files.append(home / ".claude" / "settings.json")
    settings = [read_json(f) for f in files]
    env = {}
    for s in reversed(settings):
        block = s.get("env")
        if isinstance(block, dict):
            env.update({k: str(v) for k, v in block.items()})
    env.update(environ)

    def on(name: str) -> bool:
        return env.get(name, "").strip().lower() not in ("", "0", "false", "no", "off")

    if on(FORCE_5M):
        return COLD_AFTER
    found = env.get(TTL_VAR) or next((str(s["subagentPromptCacheTtl"]) for s in settings
                                      if "subagentPromptCacheTtl" in s), None)
    if found is None and project:
        agent_type = read_json(meta).get("agentType")
        if isinstance(agent_type, str) and agent_type:
            ttl = frontmatter_ttl(project / ".claude" / "agents", agent_type)
            if ttl is None and home:
                ttl = frontmatter_ttl(home / ".claude" / "agents", agent_type)
            if ttl is not None:
                return COLD_AFTER     # 5m, or a 1h the host may ignore: unknowable here
    if found is None:
        return LIFETIMES["1h"] if on(ENABLE_1H) else COLD_AFTER
    return LIFETIMES.get(found.strip(), COLD_AFTER)


def main() -> int:
    try:
        data = json.loads(sys.stdin.read())
        if data.get("tool_name") != "SendMessage":
            return 0
        tool_input = data.get("tool_input") or {}
        to = str(tool_input.get("to") or tool_input.get("recipient") or "")
        message = str(tool_input.get("message") or "")
        transcript = data.get("transcript_path")
        if not transcript or not AGENT_ID.match(to):
            return 0
        if message.lstrip().lower().startswith(DECLARATION):
            return 0
        worker = Path(transcript).with_suffix("") / "subagents" / f"agent-{to}.jsonl"
        if not worker.is_file():
            return 0
        idle = time.time() - worker.stat().st_mtime
        if idle <= COLD_AFTER:
            return 0
        project = os.environ.get("CLAUDE_PROJECT_DIR")
        home = os.environ.get("HOME")
        ttl = lifetime(dict(os.environ), Path(project) if project else None,
                       Path(home) if home else None, worker.with_suffix(".meta.json"))
        if ttl > COLD_AFTER and not wrote_1h(worker):
            ttl = COLD_AFTER                  # configured 1h the host has not shown it honours
        if idle <= ttl:
            return 0
        last = last_assistant(worker)
        if last.get("isApiErrorMessage"):
            return 0
        state = ("it already handed back, so there is nothing to resume"
                 if handed_back(last) else "it left no host error record")
    except Exception as e:                    # noqa: BLE001 — fail open
        print(f"resume-hook: not checked ({type(e).__name__})", file=sys.stderr)
        return 0
    print(f"cypress: worker {to} has been idle {int(idle // 60)} min and {state}; its "
          f"{ttl // 60}-minute prompt cache has expired, so this message would re-read its whole context "
          f"uncached. New work goes to a fresh worker with a full brief "
          f"(delegation.continuation). A worker the host cut off (limit, network or "
          f"server error) is resumed without this check. If this is a small follow-up "
          f"that needs its context, or the worker stopped with no error record, start "
          f"the message with `{DECLARATION} <reason>`.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
