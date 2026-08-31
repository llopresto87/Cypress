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
reliability risk, not diligence.

## Common failures and triage

| Symptom | Likely cause | First check | Fix / escalation |
|---|---|---|---|
| `<what you see>` | `<usual cause>` | `<command/dashboard>` | `<action, or who to escalate to>` |

## Inspecting the running system

- Inspect runtime / logs: `<cmd>` — with redaction; never emit secrets or
  sensitive fields to logs or traces.
- Trace the broker / queue / dead-letter state: `<cmd>`
- Check external-dependency health: `<cmd>`

<!-- Keep current: an operations doc that has stopped matching reality is worse
than none, because it is trusted. -->
