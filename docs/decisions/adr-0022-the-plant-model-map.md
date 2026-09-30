---
status: proposed
status_date: 2026-09-30
owner: seed steward
---

# ADR-0022: a plant names its models once, in its model map; nodes name the class, and each host reads the map in its own way

## Status

See frontmatter, which is the single home. Filed 2026-09-30 for 7.35.0 from the
owner's ruling D9 of that round, which is kept with the round's working records
outside the seed. This record stays `proposed` until the increments it names
land. While proposed it was revised on the same date by the session's rulings
S1, S3 and S4 on the architect's first findings: the opencode projections get a
drift check (S1), the `model:` token set is every alias Claude Code accepts
(S3), and an unfilled map is disclosed at graft, not blocked on (S4). It supersedes ADR-0019 in part: the two-line Opus rule and the non-Opus
task-kind table that ADR-0019 left in the Prime Agent overlay move into the
plant's model map. ADR-0019's core stands and widens: the seed names no model
version at all, and a protocol names the class.

## Date

2026-09-30

## Context

The owner's ruling D9:

> "we need to find a way for this to work for both prime angent, claude code and
> opencode. prime agent and opencode can use any and all models beyond
> anthropic"

The owner's standing rule is that agents run only the models the plant defines.
Four facts stand against both today:

- ADR-0019 left a version rule (Opus 5.5, Opus 4.6 for very light authoring, a
  Sonnet floor) and a non-Opus task-kind table in
  `integrations/prime-agent/APPEND_SYSTEM.md`, a seed file every Prime Agent
  session loads. Each model release makes it stale, and it names one provider.
- The same overlay tells a spawn whose model is missing to take the nearest
  higher model of the same family. That runs a model the plant did not define.
- Every agent carries `model: opus` or `model: sonnet`. Claude Code reads those
  aliases natively and picks the version. opencode wants a `provider/model`
  string, and a subagent with no model runs on its caller's model. An inline
  `agent.<name>.model` in `opencode.json` loses to the projected
  `.opencode/agents/` file on a conflicting key, so config alone cannot set it.
- `agents/multi-agent-architect.md` pins model versions for client systems.

## Decision

An agent's `model:` token is one of the aliases Claude Code accepts (`opus`,
`sonnet`, `haiku`, `inherit`; the seed's own agents use `opus` and `sonnet`)
and names a class (authoring, investigation, investigation at low effort, or
the caller's model), and the model each host runs for a class and an effort
lives in one plant-owned leaf, `docs/graph/models.md`, which the seed
ships as an unfilled template placed only when missing; Claude Code reads the
alias natively, Prime Agent resolves the map on each spawn, and
`install.sh opencode` writes the map's `provider/model` into each projected
agent, or no `model:` line where the map has no filled row.

## Consequences

- The seed carries no model version. The overlay's version rule, its task-kind
  table and its nearest-higher fallback leave it; the overlay says how to read
  the map. `agents/multi-agent-architect.md` names client models by class and
  takes the concrete model from the client project's provider wiki page.
- The home of the rule is `delegation.model-map` in
  `core/method/delegation-model-classes.md`. The map is a leaf outside the node
  directories, so a dotted model id is not read as a version leak.
- A listed selector that does not resolve stops the spawn and is reported. An
  unfilled row makes the spawn inherit its caller's model, and the routing
  evidence says so (`model: inherited (map row unfilled)`). No model is
  substituted.
- opencode: the projection stops being verbatim. The stamp records
  `verbatim: false` for opencode, the projected agents are generated copies
  under `--symlink`, and a map edit takes a re-run of `install.sh opencode`. An
  unreadable map fails the opencode install before any agent is projected.
  ADR-0009 installed opencode "with its current install surfaces unchanged";
  this changes one line of each projected agent. ADR-0009's tiers are
  unchanged, and the host carries `provider/model` natively.
- `install.sh opencode --check` renders the expected projections from the
  graph and the map and compares them with `.opencode/agents/` (S1). The graft
  pickup's projection check already runs `install.sh <tool> --check` for a
  projection that is not verbatim, so it reports a hand edit, or a map edit
  with no re-run, instead of "none drifted". `all --check` checks the opencode
  projections of a plant that records opencode.
- `agent-lint.py --lint` holds `model:` to the four aliases, for plant agents
  as well (S3). A plant agent that pins `haiku` or `inherit` keeps passing
  after its graft; one with no `model:` or a full model id fails. The opencode
  projection reads `haiku` as the `investigation | low` row and writes no
  model line for `inherit`.
- An unfilled map blocks nothing (S4). `graft.gate.scaffolds` lists
  `docs/graph/models.md` byte-identical to its template as a disclosed row and
  passes on it, and `growth-audit.py` reports it without failing, because an
  unfilled row already has a defined meaning: the spawn inherits its caller's
  model and says so.
- A new provider is a line in the map's Providers list, plus a `libraries/` page
  when an agent needs that provider's facts. The owner may still rule that a
  provider is a dependency that goes through `ingest-library`.
- The Prime Agent eager figure falls with the overlay, and the round's docs
  pass re-derives every published copy.
- The owner's plant fills its own map at its close-out, from the owner's rules.
- Contracts: SPEC-0001 `MODEL_MAP_TEMPLATE_IS_PLACED`,
  `OPENCODE_MODEL_FROM_MAP`, `OPENCODE_NO_MAP_ROW_NO_MODEL_LINE`,
  `OPENCODE_MAP_UNREADABLE_FAILS_CLOSED`, `OPENCODE_CHECK_DETECTS_DRIFT`;
  SPEC-0005 `AGENT_DECLARES_MODEL_CLASS`. Tests that fail if this is reversed:
  their rows in `tests/test-full-install.sh` and `tests/test_agent_lint.py`,
  and the disclosed-map cases of `tests/test-graft-tools.sh` and
  `tests/test-growth-audit.sh` (no spec contract: the change is to the report of
  two seed-only audit tools, not to a write into a plant).

## Alternatives considered

- **A neutral `model_class:` key with a transform for every host.** Rejected:
  Claude Code's projection would stop being verbatim, and Claude Code is the one
  host where model selection is mechanically enforced today.
- **The map in the `plant:` block of `docs/graph/index.md`.** Rejected: that
  block allows one level of nesting and a fixed key set, and every router read
  pays for its bytes.
- **The map under `libraries/`.** Rejected: a library page carries an exact pin
  and an index row for a dependency's facts, and the map is the plant's choice.
- **Seed-shipped default selectors.** Rejected: agents run only the models the
  plant defines, and an unfilled row already falls back to the caller's model
  without naming one.
- **Hold the token to `opus` and `sonnet`.** Rejected (S3): a plant agent that
  pins `haiku` or `inherit` would fail its next graft for a value its own host
  accepts, and both have a defined reading in the map.
- **Accept the silent opencode drift check.** Rejected (S1): a pickup that
  reports "none drifted" after checking nothing is a green that asserts
  nothing (`rule.verify`).
- **An inline `agent.<name>.model` in `opencode.json`.** Rejected: the projected
  agent file wins on the conflicting key.
- **Keep ADR-0019's rule in the overlay.** Rejected: it keeps a version in the
  seed, serves Prime Agent alone, and leaves opencode on a token it cannot read.
- **Fall back to the nearest higher model on a miss.** Rejected: it runs a model
  the plant did not define.

## Reversibility

`reversible`: text, one leaf template and one install transform. A plant's
filled map belongs to the plant and survives a reversal.

## References

- Spec: SPEC-0001 (the map's placement and the opencode transform), SPEC-0005
  (`AGENT_DECLARES_MODEL_CLASS`)
- ADR-0019 (superseded in part), ADR-0009 (the opencode install surface)
- Owner ruling D9 of 7.35.0, kept with the round's working records outside the
  seed
