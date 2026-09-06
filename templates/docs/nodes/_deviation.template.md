---
id: deviation.<slug>
tier: 2
kind: deviation
title: <slug> — the standard departed from, in one line
owns:
  - deviation.<slug>.standing
requires:
  - <the node that owns the fact departed from>
peers:
  - <the node this departure most often collides with>
load_when:
  - "<the standard's own name — the words the router already matches>"
  - "<the operational situation in which the departure applies>"
est_tokens: <honest estimate of the body>
status: standing                      # the only status a live deviation carries
status_date: YYYY-MM-DD
owner: <agent or person accountable for the departure>
departs_from: <fact key or theme, e.g. secrets-posture.lifetime>
reason: <one paragraph — the operational constraint that forces the departure>
scope: <where it applies — paths, environments, components; nothing wider>
ends_when: <the condition that retires it, checkable by a later reader>
recorded_in: ADR-NNNN                 # the ADR that holds the history
---

<!--
Template: docs/nodes/_deviation.template.md
Lives at: docs/graph/nodes/deviation.<slug>.md   (filename MUST equal the id)
Used: one file per standing departure from a known standard, written at
canonize close-out when a decision departs from a standard and the owner
has said why (canonize.deviation-capture). The ADR named in `recorded_in`
is the history; this node is the standing truth the router surfaces
whenever the standard's topic comes up.
Contract: docs/graph/_schema.md — "Node kinds" (deviation) and "Lifecycle
status" (`standing` requires `ends_when`); graph-lint rule 13 enforces it.
The leading underscore keeps this blank form out of the linter; the node
you copy it to must not carry one.
-->

# <slug> — deviation from <the standard>

## What this is

A deliberate, reasoned, standing departure from `<departs_from>` — not a
lapse to be fixed and not a decision to re-litigate. Every field that
matters is in the frontmatter above; the body explains, it never
restates a value.

## Why

<The operational constraint, in the words a later reader needs to judge
whether it still holds. Name the alternative that was rejected and what
following the standard would cost here.>

## Scope

<The exact set the departure covers. Everything outside it follows the
standard; say so if the boundary is easy to misread.>

## How it ends

<What has to become true for `ends_when` to fire, and who notices. A
deviation with no observable end is a policy change wearing a
deviation's clothes — record that as a decision instead.>

## Where the history is

`<recorded_in>` — the ADR that records the decision, the alternatives,
and the discussion. Supersede it there; update this node's frontmatter
when the ADR changes.

## Example

```yaml
---
id: deviation.acme-billing-secret-lifetime
tier: 2
kind: deviation
title: acme-billing-secret-lifetime — the billing gateway keeps a 12-month API key
owns:
  - deviation.acme-billing-secret-lifetime.standing
requires:
  - crosscut.secrets
peers:
  - subsystem.billing
load_when:
  - "secret lifetime, key rotation, rotate the billing key"
  - "billing gateway credential expired"
est_tokens: 300
status: standing
status_date: 2026-01-15
owner: platform-team
departs_from: secrets-posture.lifetime
reason: The upstream payment gateway issues keys with a fixed 12-month lifetime and offers no rotation API; rotating on the 90-day standard would mean a manual re-issue and a checkout outage each quarter.
scope: The single gateway credential held in the billing service's secret-manager path; every other secret in the plant follows the 90-day rule.
ends_when: The gateway ships a rotation API, or the billing service moves to a provider that does.
recorded_in: ADR-0042
---
```
