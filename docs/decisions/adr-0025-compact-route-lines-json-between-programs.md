---
status: accepted
status_date: 2026-10-01
owner: seed steward
---

# ADR-0025: the router talks to models in compact lines that keep every resolved path; JSON is only for programs; nodes are read through `--show`

## Status

See frontmatter, which is the single home. Filed 2026-10-01 for 7.37.0 from
the owner's rulings on the round's JSON proposal, D3 and O1, kept with the
round's working records outside the seed. The increments it names landed in
the same round, and the record was flipped to `accepted` at the release pass of
2026-10-01. It supersedes no earlier ADR.

## Date

2026-10-01

## Context

`graph-lint.py --plan` prints a wide layout: an echo of the task, padded
columns, the reason "cross only if the task requires it" on every NOT LOADED
line, and titles that repeat the node's slug. Its readers are models: the
route hooks inject it, a spawned worker runs it as brief step 1, and on the
hookless hosts it is the only route. The hooks parse the same text, so the
format serves two readers with different needs.

The owner proposed JSON as "a more effective format to talk to an llm than
markdown", and asked for a slim view of a node after routing, on the
condition that "the part were a node points to a leaf is preserved" (D3).

The investigation measured one plan, same content, in five renderings. Counts
are a cl100k-compatible token count and characters / 4:

| Rendering | cl100k | chars/4 |
|---|---|---|
| current text | 1,143 | 1,304 |
| JSON objects | 1,338 (+17%) | 1,434 |
| JSON columnar | 760 (-34%) | 837 |
| compact lines, a path on every id | 681 (-40%) | 761 |
| compact lines, a path only where the id does not spell it | 537 (-53%) | 616 |

JSON objects cost more than the text they would replace. On the owner's own
criterion, compact lines win.

The size of the win is small next to residency. On the measured Prime Agent
session, per-session residency and unrouted children (ADR-0024) take injected
route and status text from 4.5% to 0.67% of processed tokens; compact lines on
top take it to 0.46%, about 5% of the round's measured saving. On follow-up
routes the compact grammar adds 7 points on the real session and 12 on the
short-session replay, after residency's 73 and 59. A node opened through
`--show` saves about 207 cl100k against the raw file; the measured parent
opened 6 nodes in 10 prompts.

63% to 73% of a node's frontmatter is router input, spawn configuration, or a
copy of the body (`load_when`, `routing_triggers`, `est_tokens`, `tier`,
`kind`, `description`, `prevents`, spawn keys). A model that opens a node after
routing pays for all of it. A mechanical check over the plant's 118 nodes
dropped those keys and lost no edge and no leaf pointer, including the 28
`artifacts` and 8 `plant_knowledge` pointers that appear only in frontmatter.

On the path column the owner ruled O1: "keep. an overarching rule/doctrine of
this project ais that we store information into durable form into the
docs/graph so that the model does not need to figure it out itself, so this
falls exacfly in that scope". The principle: the model is handed resolved
facts, and is never asked to derive one.

## Decision

`graph-lint.py --plan` prints only the compact grammar, with the resolved path
on every id; `--plan-json` prints a versioned document, `cypress.plan/1`, for
programs, and is the hooks' only input; and `graph-lint.py --show <id>...`
prints a node with its router and spawn keys dropped and every edge and leaf
pointer kept.

## Consequences

- Sequence: `--plan-json`, holding only what the hooks consume, lands with the
  hook core (ADR-0024), because the core reads nothing else. The compact
  grammar and `--show` land next, and change what both renderers print.
- One grammar, two renderers: `graph-lint.py --plan` and the hook core, which
  renders from the JSON. `ROUTE_FULL_TEXT_EQUALS_PLAN` holds the two equal.
- The JSON carries the plant's four `plant:` scalars from the start. The text
  prints them since the FIRST MOVE change of ADR-0027 landed, because from
  then on a session may never read them from `index.md`.
- The hooks stop parsing router text. `task_sha256` replaces the echo, so no
  prompt byte comes back; ids and paths are checked against their patterns;
  the leading-indent defect of the text parser goes with it. A plant whose
  `graph-lint.py` and hooks come from different seed versions fails loudly on
  the schema name instead of misreading text.
- `--show` is derived on every call and never cached. The raw file stays
  canonical, and an edit still opens the file at the header's path.
- The model learns `--show` from the kernel's FIRST MOVE and
  `skills/context-router/SKILL.md`. The brief templates do not change.
- An inferred entry prints `inferred from "<path>"` without the matching
  pattern, in both renderers; the pattern stays a node fact, read through
  `--show` (SPEC-0005, 2026-10-01).
- A person at a terminal reads the compact lines too. No wide format is kept.
- `test_graph_lint.py`'s `--plan` helpers and `PLAN_ENTRY_NAMES_THE_NODE_FILE`
  are rewritten for the new grammar.
- Contracts: SPEC-0003 `PLAN_ENTRY_NAMES_THE_NODE_FILE`,
  `PLAN_JSON_SCHEMA`, `PLAN_JSON_CARRIES_NO_PROMPT`,
  `PLAN_JSON_HASH_BINDS_TASK`, `PLAN_JSON_EQUALS_PLAN`,
  `SHOW_KEEPS_EVERY_POINTER`, `SHOW_DROPS_ROUTER_AND_SPAWN_KEYS`,
  `SHOW_BODY_VERBATIM`, `SHOW_UNKNOWN_ID_FAILS`, `ROUTE_HOOK_READS_PLAN_JSON`,
  `ROUTE_FULL_TEXT_EQUALS_PLAN`.

## Alternatives considered

- **JSON to the model.** Rejected: +17% against the current text in object
  form. The columnar form is shorter, but still longer than compact lines, and
  a model reads it no better.
- **Drop a path where the id spells it.** Rejected by O1: it saves about 144
  cl100k per full route, and asks the model to apply a path rule the graph can
  state.
- **Keep the wide `--plan` beside a `--plan --compact` flag.** Rejected: two
  model-facing formats, and the default, the one models are told to run, stays
  the wasteful one.
- **The hook imports `resolve()` by path.** Rejected: it couples the hook to
  an unversioned internal tuple, and a graft can leave a plant's
  `graph-lint.py` and its hooks at different seed versions.
- **Store the graph as JSON.** Rejected: it costs the model more, and every
  view this round needs derives from the Markdown on demand.
- **Generate or drop a node's `## Neighbours` section.** Rejected: its prose
  says why a boundary exists, which frontmatter cannot.

## Reversibility

`reversible`. `cypress.plan/1` is new and owned by its producer; a later
schema is a new name. No stored format changes.

## References

- Spec: SPEC-0003 (the plan grammar, the JSON schema, `--show`)
- Plan: `docs/plans/grill-7.37.0-routing-context.md`, increments 1 and 2
- [ADR-0024](adr-0024-one-hook-core-per-session-residency.md) (the core that
  reads the JSON), [ADR-0027](adr-0027-first-move-runs-the-router.md) (the
  kernel names `--show`)
- Owner rulings on JSON, D3 and O1 of 7.37.0, and the round's measurements,
  kept with the round's working records outside the seed
