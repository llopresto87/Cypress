# Operations

The steady-state operations reference: what to watch, what breaks, how to
triage.

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

## Inspecting the running system

- Inspect runtime / logs: `<cmd>` — with redaction; never emit secrets or
  sensitive fields to logs or traces.
- Trace the broker / queue / dead-letter state: `<cmd>`
- Check external-dependency health: `<cmd>`

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
