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
est_tokens: 711
---

## A command that may outlive its session is bounded (`toolcraft.bounded-execution`)

This discipline binds every session that runs a command, whether or not a tool
comes out of it; `skill.toolcraft` points here.

A tool is only durable if the session that runs it survives it. Every command an
agent runs is bounded, and anything that may outlive the bound is detached,
logged to disk, and terminated by a marker. A timeout covers clause 1 only;
clauses 2-6 tell "finished" from "stuck" when the work is long.

1. A foreground command carries an explicit bound. Service control, process
   signalling and installers hang most often, so they carry a bound too.
2. Work that may legitimately exceed the bound runs detached: hangup
   trapped, its process group recorded to a file, its output written to a
   durable log under the project, and a terminal result line and an
   exit-code file at the end.
3. Waiting is bounded polling of that log for new bytes or the marker. A
   poll that sees no new evidence for a fixed number of intervals stops and
   reports "no progress since T", so the next step is a diagnosis; an
   unchanged re-run only repeats the stall.
4. Claim "running" from an observed liveness signal (the pid alive and the
   log growing, or device utilisation); a returned launch proves only that
   the command started. Identify a run by the id the tool returned at
   launch, because list positions shift between reads, and claim "stuck" or
   "never started" only from that run's own progress output.
5. Stop a process by its recorded pid or process group, with bounded
   escalation; a name pattern can match the shell that issues the kill and
   end the session itself.
6. Completion is the marker, because silence and a timeout also happen to a
   stuck run. Derive a liveness threshold from measured durations of that
   task class.

These clauses are delivered as a mechanism where the harness has a hook
surface: the Claude Code integration installs a pre-tool guard
(`.claude/bound-hook.py`) that refuses a blocking-prone shell command carrying
neither a bound nor a detached launch, so clause 1 is enforced before it is
read. Harnesses without a hook surface carry the clauses as the agent's own
discipline; their integration notes say so.

## Neighbours

- `method.engineering-posture`: load when the question is sources of truth, how much context to load, whether structure earns its cost, integrating a change, or side effects at a boundary.
- `method.host-parity`: load when a result on the authoring host must stand for the target, inspection touches a shared host, or a loop is made to continue past a failure.
