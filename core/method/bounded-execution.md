---
id: method.bounded-execution
tier: 2
kind: method
origin: seed
title: bounded execution — a command that may outlive its session is detached, logged, polled with a bound and ended by a marker
owns:
  - toolcraft.bounded-execution
requires:
peers:
  - method.engineering-posture
  - method.minimum-sufficient-work
  - method.decision-economy
  - method.host-parity
load_when:
  - "command hung, session stuck, wrap in a timeout, run detached"
  - "is the run stuck, check it by id"
prevents: A hung command that wedges the session, a stall retried unchanged, and a run called finished because its output stopped.
est_tokens: 793
---

## 14. A command that may outlive its session is bounded (`toolcraft.bounded-execution`)

This discipline was filed under the toolcraft protocol because that was the
nearest node when it was written. It is not tool-authoring doctrine — it binds
every session that runs anything, whether or not a tool comes out of it — so it
lives here, beside the rest of the engineering posture. `skill.toolcraft` points at
it and does not restate it.

A tool is only durable if the session that runs it survives it. Every command an
agent runs is bounded, and anything that may outlive the bound is detached,
logged to disk, and terminated by a marker:

1. A foreground command carries an explicit bound. Service control, process
   signalling and installers are the commands that hang most and get no
   exemption.
2. Work that may legitimately exceed the bound is never run in the
   foreground: it is launched detached with hangup trapped, its process
   group recorded to a file, its output written to a durable log under the
   project, and it ends with a terminal result line and an exit-code file.
3. Waiting is bounded polling of that log for new bytes or the marker. A
   poll that sees no new evidence for a fixed number of intervals stops and
   reports "no progress since T"; it never re-issues the same command.
4. "Running" is claimed only on an observed liveness signal — the pid alive
   and the log growing, or device utilisation — never on the launch having
   returned. A run is identified by the id the tool returned when it
   launched it, never by its position in a list of runs, and "stuck" or
   "never started" is claimed only from that run's own progress output.
5. A process is stopped by its recorded pid or process group with bounded
   escalation, never by a pattern that can match the shell issuing the kill.
6. Completion is the marker, not the absence of output and not a timeout;
   a liveness threshold is derived from measured durations of that task
   class, not guessed.

A timeout alone covers only the first clause. The other five are what
distinguish "finished" from "stuck" when the work is long, and a stall is
reported, never repeated.

These clauses are delivered as a mechanism where the harness has a hook
surface: the Claude Code integration installs a pre-tool guard
(`.claude/bound-hook.py`) that refuses a blocking-prone shell command carrying
neither a bound nor a detached launch, so clause 1 is enforced before it is
read. Harnesses without a hook surface carry the clauses as the agent's own
discipline; their integration notes say so.

## Neighbours

- `method.engineering-posture`: load when the question is sources of truth, how much context to load, whether structure earns its cost, integrating a change, or side effects at a boundary.
- `method.host-parity`: load when a result on the authoring host must stand for the target, inspection touches a shared host, or a loop is made to continue past a failure.
