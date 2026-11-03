#!/usr/bin/env python3
"""resume-hook.py — a PreToolUse guard on SendMessage: new work goes to a fresh
worker, not to one whose prompt cache has expired (`delegation.continuation`).

Installed to `.claude/resume-hook.py` and wired in `.claude/settings.json` under
hooks.PreToolUse with `"matcher": "SendMessage"`. The host passes
`{"tool_name", "tool_input": {"to", "message"}, "transcript_path"}` on stdin.
Claude Code keeps a worker's transcript at
`<transcript without .jsonl>/subagents/agent-<to>.jsonl`; its mtime is the
worker's last activity. A worker idle longer than COLD_AFTER (5 minutes) has no warm cache,
so a message re-reads its whole context uncached and acts on state other lanes
may have changed. Two cases are told apart from the transcript's tail:

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
import re
import sys
import time
from pathlib import Path

COLD_AFTER = 300             # seconds: a subagent's prompt cache lives 5 min; past it a
                             # message rewrites the whole context (Claude Code: worker
                             # calls after 5-10 min idle wrote ~217K tokens each)
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
        last = last_assistant(worker)
        if last.get("isApiErrorMessage"):
            return 0
        state = ("it already handed back, so there is nothing to resume"
                 if handed_back(last) else "it left no host error record")
    except Exception as e:                    # noqa: BLE001 — fail open
        print(f"resume-hook: not checked ({type(e).__name__})", file=sys.stderr)
        return 0
    print(f"cypress: worker {to} has been idle {int(idle // 60)} min and {state}; its "
          f"prompt cache has expired, so this message would re-read its whole context "
          f"uncached. New work goes to a fresh worker with a full brief "
          f"(delegation.continuation). A worker the host cut off (limit, network or "
          f"server error) is resumed without this check. If this is a small follow-up "
          f"that needs its context, or the worker stopped with no error record, start "
          f"the message with `{DECLARATION} <reason>`.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
