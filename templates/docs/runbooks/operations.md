# Operations

The steady-state operations reference: what to watch, what breaks, how to
triage.

## Boundaries

What the procedures in this file may not touch, written before any of
them, so that a person or an agent running one does not have to infer
the limits from the commands.

- Off limits: `<environments, hosts, credential groups this file never
  touches>`
- Credential: `<where it comes from; read from the environment in
  process, never printed, never pasted into a brief or a log>`
- Logs not to read: `<logs that may hold secrets or env values, and why>`

## Dashboards

| Dashboard | What it shows | Link |
|---|---|---|
| `<name>` | `<the signal>` | `<link>` |

## Alerts

| Alert | Condition (threshold) | Why it matters | Who acts |
|---|---|---|---|
| `<name>` | `<threshold + rationale>` | `<user/operational impact>` | `<role>` |

Every alert names a threshold **and its rationale**. An alert that fires on a
condition no human should act on is removed or downgraded — alert fatigue is a
reliability risk, not diligence. Every alert also names how its own delivery is
confirmed: a notification path that can fail without saying so is not a
mitigation, and an alert nobody receives and no alert at all are the same
outcome, and the difference is invisible precisely on the day it matters. Where a signal is the only
automated protection for a hazard, the check that the signal still fires is
itself a gate.

## Common failures and triage

| Symptom | Likely cause | First check | Fix / escalation |
|---|---|---|---|
| `<what you see>` | `<usual cause>` | `<command/dashboard>` | `<action, or who to escalate to>` |

### Expected non-green outcomes

Some procedures go red by design: a scan that fails on findings above its
threshold, a publish refused from a branch that may not publish. List each
one with the field that proves it is the designed verdict, so that nobody
chases it as a defect.

- `<procedure>`: `<the red it produces>`, designed, proven by `<field or
  log line>`

A red with no entry here is not expected, however familiar it has become.
A gate that stays red for a reason unrelated to what it guards belongs in
`verification.md` as chronically red, with an owner, and never in this
list.

## Inspecting the running system

- Inspect runtime / logs: `<cmd>` — with redaction; never emit secrets or
  sensitive fields to logs or traces.
- Trace the broker / queue / dead-letter state: `<cmd>`
- Check external-dependency health: `<cmd>`

## First access on a fresh environment

When the seed data deliberately carries no credential, a fresh environment
has no working login until an operator creates one, and that step belongs
here. If the procedure has its home in another runbook, link it rather
than restating it, and record here what to know before running it. Mark
any fallback it names (a self-service reset, a recovery address)
*unproven* until someone has exercised it: a fallback nobody has tried
may be decorative.

- Procedure: `<link to its one home>`
- Before you run it: `<forced first-login steps, what they block>`
- Fallback: `<fallback>`, proven `<date>` | unproven

## Pre-flight before a first deploy

The few commands that retire the largest risks of a deploy nothing has
yet exercised, in the order to run them. The paragraph says *why* each
risk matters; the command says *how you check*. Mark each one *executed*
(with the date and result) or *not executed*, so the list never reads as
done when it was only written.

1. `<cmd>`: retires `<risk>`; executed `<date, result>` | not executed

## What this operator cannot do here

An empty table above means one of two things, and they are not the same: the
row has not been filled in, or the capability does not exist. Say which. List
every operational capability this environment lacks, each recorded the way a
missing gate is recorded, with the owner who would add it and the promise
above that it shrinks.

- `<capability>`: absent (YYYY-MM-DD) — `<reason>`; owner `<who>`; bounds
  `<which promise above is smaller because of this>`

An operations document that describes the capabilities it wishes it had is
worse than none, for the same reason a drifted one is: it is trusted.

<!-- Keep current: an operations doc that has stopped matching reality is worse
than none, because it is trusted. -->
