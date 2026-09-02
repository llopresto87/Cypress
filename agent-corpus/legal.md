# Suggested expert: legal — NOW IN BASE ROSTER

> **This role has been promoted to the base roster.**
>
> As of version 6.12.0, `legal` is a first-class seed agent at
> `agents/14-legal.md`, installed by default into every plant. The agent-
> corpus entry below is retained for historical reference and to document
> the mandate that was harvested into the base roster.

The full legal expert is now shipped as `agent.legal` in the base roster:

- **Charter:** `agents/14-legal.md` (the active, spawnable agent)
- **Load cost:** every plant pays the per-session cost of the legal agent
- **Withdrawal:** installed by default; removal is a plant's own decision

## Original mandate (now implemented in the base roster agent)

Owns reasoning about a **body of externally-authored rules** — regulatory
codes, standards catalogs, compliance requirements — against a **curated,
verified legal corpus** (`docs/graph/legal/`) as its *only* knowledge source:
never live search, never model memory. A corpus gap produces an explicit,
fixed-form refusal ("not recorded — needs ingest"), **never** a reconstructed
rule, number, or citation.

Every finding keeps four parts always distinct — the **verified underlying
fact** with its evidence pointer, the **cited external rule** by its corpus id
carrying whatever provenance grade the corpus recorded for it, the analyst's own
**explicitly-labelled assessment** connecting the two, and a standing
**boundary** reserving the final authoritative determination to a named human
role outside the agent — and every claim in a deliverable maps to a corpus-entry
ledger row, a claim with no row blocking the deliverable. Citations are
re-checked against the corpus's recorded status before each reuse, never carried
on the strength of having shipped once.

## When to use

- The project must reason about a body of externally-authored rules whose
  wording drifts and whose misstatement is high-cost.
- The exact rule text must come from a **source of record** rather than model
  recall, and "roughly what the rule says" is not an acceptable output.

## routing_triggers (exemplars)

See `agents/14-legal.md` for the authoritative list.
