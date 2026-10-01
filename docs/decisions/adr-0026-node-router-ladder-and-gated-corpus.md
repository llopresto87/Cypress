---
status: accepted
status_date: 2026-10-01
owner: seed steward
---

# ADR-0026: the node router ranks named ids and paths above words, abstains instead of forcing root, and is gated on a node-route corpus

## Status

See frontmatter, which is the single home. Filed 2026-10-01 for 7.37.0 from
the round's routing investigation, kept with the round's working records
outside the seed, and the session's settled items S6 to S8, which the owner
let stand. The increment it names landed in the same round, and the record was
flipped to `accepted` at the release pass of 2026-10-01. It supersedes no
earlier ADR. It is the node router's counterpart of
[ADR-0001](adr-0001-mechanical-agent-router.md), and it brings the node router
under SPEC-0002.

## Date

2026-10-01

## Context

`graph-lint.py --plan` (`resolve()`) scores a task against every node's
`load_when` with IDF weights, promotes expertise nodes on their trigger
phrases, and follows `requires:` eagerly. SPEC-0002 contracts what the agent
router may claim; nothing contracts the node router, and no corpus measures
it.

The investigation wrote a 74-row node-route corpus over a grown plant, in the
four classes of SPEC-0002, and measured the stock router per class:

| Class | Rows | Required recall | Irrelevant share of loaded tokens | Forbidden hits | Correct abstentions |
|---|---|---|---|---|---|
| contract | 22 | 22/23 | 0.49 | 0 | n/a |
| paraphrase | 29 | 15/38 | 0.72 | 0 | n/a |
| adversarial | 14 | 7/13 | 0.78 | 19, on 14 of 14 rows | n/a |
| unknown-domain | 9 | n/a | 0.88 | 0 | 1/9 |

It traced the over-selection to named mechanisms: no length normalization,
so a pasted brief matches everything; expertise promoted on a bag of words,
and 94 of 183 trigger phrases are one token; composition descent on any word
of the task; filler words that still carry IDF weight; trailing punctuation
that changes a term; kind prefixes and whole paths scored as words; and root
forced when nothing scores. No token saving was measured for any of this: the
case is routing quality. A prototype ladder of strong signals (an id named,
a path named, a contiguous trigger phrase) with an absolute floor cut
adversarial forbidden hits from 19 to 3 and raised unknown-domain abstentions
from 1 to 8 of 9, with contract and paraphrase recall within noise. On a long
brief the strong tiers made it worse (28 nodes to 13 nodes but a larger token
total), so they need a cap, and long input needs its own rule.

## Decision

`resolve()` takes the first tier that hits, in this order: an exact node id
in the task; a path the task names (an exact node file, the longest non-bare
`repo:` prefix, an expertise file pattern, a basename only when unique); a
contiguous trigger phrase of at least two content tokens; then the lexical
score with SPEC-0002's guards ported from the agent router and a floor of two
distinct confident terms. A strong tier that hits more than three nodes falls
through. A task with no signal loads nothing and its notice names the protocol
entry nodes and asks for a sharper task line; a task over `LONG_TASK_TERMS`
distinct terms loads nothing and asks for the task line.
`graph-lint.py --eval <tsv>` gates the router per class against ratchets.

## Consequences

- This is a quality change, measured as precision and recall per corpus class.
  It claims no token saving. In the measured Prime Agent session the model
  opened about 8% of the LOAD nodes it was shown, so fewer suggestions save
  injected lines, which per-session residency (ADR-0024) already removes on
  follow-ups, and not node reads.
- Root is no longer forced. A task with no signal gets an empty plan and one
  `no_signal` notice: "no node matches this task; route a sharper task line,
  or enter a protocol:" followed by the ids of the `kind: protocol` nodes. On
  the seed's graph that line is about 410 characters (about 155 tokens at the
  measured 2.65 characters per token). It replaces today's unknown-domain
  route, about 1,360 tokens, and it does not send the model to
  `docs/graph/index.md`, about 5,500 tokens, which would cost more than the
  route it replaces. The kernel keeps `index.md` as the fallback when the
  plan stays empty after the notice (ADR-0027). A pre-growth plant gets the same notice, since its
  protocol nodes are installed; the placeholder index keeps the pre-growth
  pointer (ADR-0017).
- A pasted brief is not routed. The `long_task` notice tells the model to run
  `--plan` on the task line, which it knows and the router does not.
- `requires:` stays eager. The hub cost comes from wrong seeds, and the ladder
  fixes the seeds.
- The corpus splits by where the gate runs. The seed gates the rows whose ids
  are all seed-owned, plus the unknown-domain rows: 32 of the 74, run against
  an installed fixture graph, with bait rows the tester adds because only one
  adversarial row is over seed nodes. `tests/graph-routes.golden.tsv` holds 39
  rows: 8 contract, 14 paraphrase, 8 adversarial and 9 unknown-domain. Paraphrase rows are copied verbatim and
  never tuned. The full 74-row corpus stays the round's measurement over the
  steward plant; filing it in a plant waits for a graft.
- Ratchets in `tests/ratchets.json`, set at the measured values after the
  change and tighten-only: contract recall (min), adversarial forbidden hits
  (max), unknown-domain abstentions (min), irrelevant share per class (max),
  paraphrase and adversarial row counts (min).
- The measurement runs after the code lands, never as a toggle in product
  code. It ran over the 74 rows at each GREEN step of the increment, on a copy
  of the steward plant's graph, because the round's work stayed uncommitted
  until release; the result is below.
- `--eval` ships to plants inside `graph-lint.py`, which graft already
  reconciles; no new file.
- Contracts: SPEC-0002 `GRAPH_ROUTE_NAMED_ID_LOADS_IT`,
  `GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER`,
  `GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE`, `STRONG_TIER_OVER_CAP_FALLS_THROUGH`,
  `PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE`, `COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE`,
  `PUNCTUATION_DOES_NOT_CHANGE_A_TERM`, `IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS`,
  `ONE_TERM_CANNOT_SEED_A_NODE`, `NO_SIGNAL_LOADS_NOTHING`,
  `LONG_TASK_ABSTAINS_WITH_NOTICE`, `GRAPH_EVAL_GATES_PER_CLASS`, and the
  corpus-honesty and both-routers contracts it widens to the node router.

## Alternatives considered

- **Route a long task on its headings or its first 600 characters.**
  Rejected: on the longest real brief they loaded 4 and 8 nodes of the wrong
  kind. Both guess over text the router cannot read, and both would be tuned
  on one paraphrase row.
- **Lazy `requires:` closure.** Rejected: it changes the `requires:` doctrine
  of `skills/knowledge-graph` to treat a symptom of wrong seeds.
- **A frontmatter key that names the code paths a node owns.** Deferred: a
  schema change in every plant, filled by graft, for a gain the corpus shows
  only on adversarial rows. It reopens if path-naming contract rows still miss
  after this change.
- **Embeddings or a semantic layer.** Rejected for this round: a new
  dependency. SPEC-0002 keeps semantic adjudication gated on measurement.
- **Keep root as the fallback.** Rejected: root on every unknown task loads a
  hub the task does not need, and `index.md` is the right orientation page.

## Amendment, 2026-10-01

Made while the record is `proposed`, by the architect pass on increment 3
(spawn `orchestrator.17.architect.1`), after the GREEN run and its review.
SPEC-0002 is the one home for each rule below; this paragraph records the
decision and the evidence.

- **The cap covers tiers 1 and 2.** The Decision's "a strong tier that hits
  more than three nodes" is read as the id tier and the path tier, which is
  what SPEC-0002 §6 says and the code does. The cap's measured reason, a long
  brief naming many ids and paths, belongs to those two tiers, and
  `LONG_TASK_TERMS` now covers the long brief too. Tier 3 stays uncapped under
  the owner's ruling that every phrase hit loads (SPEC-0002
  `PHRASE_TIER_FLOODS_LOAD`). No routed row of the 74-row plant corpus or the
  seed corpus held phrases of more than two nodes, so neither reading changes
  a measured route.
- **Tier 1 names dotted ids only.** `root` is an English word, and as a
  tier-1 hit it loaded root alone on `a pipe of edges from root to leaf`. The
  prototype this record measured matched dotted ids only.
- **No promotion in tier 4.** A trigger piece of one content token seeds
  nothing. On the 74-row corpus, one-token promotion was 7 of the 8 remaining
  adversarial forbidden hits and none of the required hits. Without it,
  forbidden hits fall to 2 (from 9 in the architect's variant run, 8 at the
  first GREEN) with no required hit lost in any class, which matches the
  prototype's figure of 3. A multi-word phrase is tier 3, so
  nothing else of promotion remains.
- **Kind words are not task terms.** This is the rule as the record and the
  spec already state it. The code had applied it to node names only.
- **The `GRAPH_*` ratchets gate only on the graph they were measured on**, every
  node `origin: seed` (SPEC-0002 `GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH`).
  On a grown plant they print, as
  `AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER` already provides for the agent
  router. The "ratchets" consequence above holds for the seed's own gate.

## Result, 2026-10-01

Measured over the 74-row corpus on a copy of the steward plant's graph (116
nodes), per class and never averaged; stock router, then the router as
shipped after the amendment above. Shares are of loaded estimated tokens.

| Class | Required recall | Irrelevant share | Forbidden hits | Correct abstentions |
|---|---|---|---|---|
| contract (22) | 22/23 -> 20/23 | 0.49 -> 0.39 | 0 -> 0 | n/a |
| paraphrase (29) | 15/38 -> 14/38 | 0.72 -> 0.62 | 0 -> 0 | n/a |
| adversarial (14) | 7/13 -> 7/13 | 0.78 -> 0.63 | 19 on 14 rows -> 2 on 2 rows | n/a |
| unknown-domain (9) | n/a | n/a | 0 -> 0 | 1/9 -> 8/9 |

The two contract rows lost are tasks with a single content word ("What is
this? Where does X live?", "Changing what a linter enforces"); the two-term
floor sends them to `no_signal`, and the notice names the protocol entry
nodes. The mean estimate loaded per unknown-domain row fell from 12,864 to
1,862 tokens. On the seed's own 39-row corpus, which the gate runs, the
ratchets in `tests/ratchets.json` were set from the post-change run: contract
recall 8/8, adversarial forbidden hits 0, unknown-domain abstentions 8 of 9,
irrelevant share at most 0.58, 0.51 and 0.43 for contract, paraphrase and
adversarial. A pasted brief now gets the one `long_task` notice line instead
of 28 nodes.

## Reversibility

`reversible`. A code change in one function and one flag. The ratchets revert
with it.

## References

- Spec: SPEC-0002 (the node router section)
- Plan: `docs/plans/grill-7.37.0-routing-context.md`, increment 3
- [ADR-0001](adr-0001-mechanical-agent-router.md) (the agent router),
  [ADR-0017](adr-0017-pre-growth-pointers-leave-the-kernel.md) (the placeholder
  index), [ADR-0014](adr-0014-graft-reconciles-every-graph-engine.md) (engine
  graft)
- The round's routing investigation and node-route corpus, kept with the
  round's working records outside the seed
