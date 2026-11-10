---
status: accepted
status_date: 2026-11-10
owner: seed steward
---

# ADR-0033: opencode is a first-class host, and the seed targets OpenCode 2 only

## Status

`accepted`. Recorded 2026-11-10 from two owner decisions given that day, which
this record transcribes and does not re-open. It supersedes the `supported`
row of [ADR-0009](adr-0009-host-support-tiers.md) and its rule "a feature
reaches opencode only where the host carries it natively, no workaround".
ADR-0009 keeps its text; its first-class and frozen rows stand.

## Date

2026-11-10

## Context

ADR-0009 made opencode a `supported` host: installed by `all`, with its
install surfaces unchanged, a feature only where the host carries it natively.
That rule was written against a host that offered no hook, no per-agent
permission and no plugin surface. The host has since split into two
generations. OpenCode 2 (the generation that runs as `opencode2`) carries a
plugin API (prompt, context, shell, tool and permission hooks), per-agent
permission rules and subagent rules, and a model variant per selector.
OpenCode 1 (`opencode`) does not.

Measured on OpenCode 2 on 2026-11-10 against the installer as it stood in
8.3.2: no projected specialist registers. An agent file whose frontmatter
carries a `tools: [...]` list is dropped without a diagnostic, and every seed
agent carries one. The `subagent_depth` key the seed ships is reported as an
unsupported legacy setting and omitted. The adapter was therefore not merely
`supported`; on the current generation it delivered the kernel and nothing
else.

## Decision

**The owner decided on 2026-11-10 that opencode becomes a first-class host,
at parity with Claude Code.** And **the owner decided on 2026-11-10 that the
seed supports OpenCode 2 only.** OpenCode 1 is out of scope: nothing is built,
tested or documented for it, and the files the seed places need not stay valid
on it.

| Tier | Hosts | What the seed commits to |
|---|---|---|
| `first-class` | `claude-code`, `opencode`, `prime-agent` | Feature parity is the target. A feature that ships on one is owed to the others, or its absence is recorded as a defect to close. |
| `supported` | none | The tier stays defined; no host sits in it. |
| `frozen` | `codex`, `github-copilot` | As in ADR-0009. |

The adapter keeps its name. The installer argument, the tier arrays, the
install stamp, the specs and the plant paths under `.opencode/` stay
`opencode`; the documents say which generation that means. Stamps recorded in
existing plants and spec contracts depend on the name.

`install.sh all` keeps its expansion and order: `claude-code opencode
prime-agent`.

## Consequences

- Parity is owed. Where OpenCode 2 holds a capability natively the seed uses
  the host's own mechanism. Where it holds it only through its plugin API, a
  thin plugin envelope over the one Python hook core is in scope (ADR-0024),
  and so is a generated transform of an agent charter. A workaround that
  decides anything the core decides is not.
- A gap is a defect to close. The host matrix records each remaining
  difference from Claude Code with what would close it.
- The projected agents use OpenCode 2's own frontmatter. The seed's
  Claude-Code-shaped fields do not reach the host, and no deprecated
  version 1 field is placed.
- OpenCode 1 plants are no longer served. An opencode plant installed from an
  earlier seed re-installs cleanly into the OpenCode 2 shape; the installer
  backs up what it replaces. Nothing is promised for OpenCode 1 afterwards,
  and the seed neither detects nor branches on it.
- The verified OpenCode 2 version has one home, `integrations/opencode/verified-version`.
  OpenCode 2 is a beta whose plugin API may change, so the live procedure is a
  recorded, repeatable document (`docs/skills/opencode-live-verification.md`),
  and no matrix cell rises on documentation or fixture evidence.
- The gate does not need OpenCode 2 or a network. Live verification is a
  separate procedure.
- The always-loaded budget stays a ratchet. Delivering the orchestrator's
  charter to opencode's main session would take its always-loaded surface past
  `EAGER_BUDGET`; that is an owner decision (D1), prepared in
  `docs/plans/owner-decisions-8.4.0-opencode-2.md`, and not taken here.

## Alternatives

- **Keep `supported` and fix the projection only.** Rejected by the owner:
  the tier rule would still forbid the hook and guard envelopes that parity
  needs.
- **Support both generations.** Rejected by the owner: a dual format doubles
  the surface for a generation the owner does not intend to serve.
- **Rename the adapter `opencode2`.** Rejected: stamps and contracts depend on
  the existing name.

## Reversibility

The tier is three array entries and one table. Moving opencode back to
`supported` or `frozen` is a new ADR and an array edit; the placed envelopes
and projections stay valid files in a plant until the next install replaces
them.
