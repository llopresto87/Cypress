---
status: back-written
status_date: 2026-09-13
owner: data-ml
status_evidence: tests/test_agent_lint.py (CorpusHonestyTests, CompoundFragmentTests), agents/_routes.golden.tsv, tests/run.sh
---

# SPEC-0002: routing contract

## 0. Metadata

- **Identifier:** SPEC-0002-routing-contract
- **Status:** see frontmatter (single home)
- **Sign-offs:** none, and none is owed. This spec is `back-written` — the
  schema's own status for documented existing behaviour (`_schema.md`) — so
  there was no RED for a promotion to land with and no product/architect/tester
  pass has been held. An earlier draft asserted signatures dated to a RED that
  never landed; that was fabricated to satisfy a linter and is recorded here so
  the correction is not silently absorbed. `active` was then used with a long
  argument for why it was honest, which was an argument for `back-written` by
  another name while the right value sat in the schema.

- **Owner:** data-ml
- **Date:** 2026-09-13
- **Last reviewed:** 2026-09-13
- **Related grill section:** docs/plans/grill-7.15.0-remediation.md §0.3, §5 slice 7
- **Related ADRs:** adr-0001-mechanical-agent-router, adr-0003-enforcement-layering-honesty
- **Supersedes:** —
- **Superseded by:** —

## 1. Summary

What `agent-lint.py --route` and `--eval` are allowed to claim. The router is a
keyword heuristic, and its confidence band is cited in delegation briefs as
evidence for choosing a specialist — so a band that does not mean what it says is
worse than no band. This contracts what each reported number measures, which
corpus it was measured over, and which failure the gate is actually gating on.

It exists because the previous report was a single line — `top-1 accuracy 100.0%
(55/55)` — over a corpus whose tasks had been written out of the triggers they
select. 46 of those 55 rows were a verbatim vocabulary subset of their own
target. The number was arithmetically true and measured mutual consistency under
the name "accuracy".

## 2. Scope

- **In scope:**
  - what `--eval` reports and what it gates on
  - the corpus classes and what each is evidence for
  - confidence-band semantics and abstention
  - the honesty checks that keep the held-out set held out
- **Out of scope:**
  - the scoring algorithm's internals (ADR-0001 owns the design; changing it
    requires re-measuring against this spec, not amending it)
  - whether a semantic adjudication layer should exist — a Track E question
    gated on measurement, not settled here
  - which specialist is correct for a given task, which is the corpus's content

## 3. User-facing behavior

A session asks the router for a specialist. It returns a ranked list and a band.
HIGH means the evidence is strong enough to cite; LOW and NONE mean the router
has no useful signal and the orchestrator should reason instead. The router
never pretends. When the seed reports how well it routes, it reports one number
per corpus class and says what each class is evidence for, so a reader cannot
mistake self-consistency for skill.

## 4. Functional contracts

### Contract: EVERY_NUMBER_NAMES_ITS_CORPUS
- **Given:** any figure `--eval` prints
- **When:** it is reported
- **Then:** the corpus class it was computed over is named on the same line
- **And:** the classes are never averaged into a single headline figure

### Contract: OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY
- **Given:** a per-class result
- **When:** it is printed
- **Then:** the mean vocabulary overlap between each task and the agent it names
  is printed with it
- **And:** a reader gets the accuracy and the reason to distrust it together

### Contract: HELD_OUT_STAYS_HELD_OUT
- **Given:** a row in either held-out class (`paraphrase` or `adversarial`)
- **When:** its vocabulary overlap with its target exceeds
  `PARAPHRASE_MAX_OVERLAP` (0.50; it was 0.80 until a reviewer smuggled four
  trigger copies past it)
- **Then:** the gate FAILS, naming the row
- **And:** the failure is fatal, not a warning — a diagnostic with no effect on
  exit status tells a reader something is wrong and the gate that all is fine

### Contract: HELD_OUT_SET_MAY_NOT_BE_EMPTIED
- **Given:** the paraphrase class
- **When:** it holds fewer rows than `PARAPHRASE_MIN_ROWS`
- **Then:** the gate fails
- **And:** shrinking the set is closed as a route to protecting a number, the
  same way relabelling is
- **Note:** the floor is named rather than typed. It was written here as the
  literal `15` while `NEITHER_HELD_OUT_SET_MAY_BE_THINNED` below states the
  same floor for the same class by naming the constant — two homes for one
  number, latent rather than wrong only because they still agree.

### Contract: CONFIDENT_WRONG_IS_THE_GATE
- **Given:** any corpus class OTHER than `adversarial`
- **When:** the router returns a confident band and the wrong specialist
- **Then:** the gate fails, with a budget of zero
- **And:** top-1 accuracy is reported but is not what the gate turns on

### Contract: NEITHER_HELD_OUT_SET_MAY_BE_THINNED
- **Given:** the `paraphrase` or `adversarial` class
- **When:** it holds fewer rows than its recorded floor (`PARAPHRASE_MIN_ROWS`,
  `ADVERSARIAL_MIN_ROWS`)
- **Then:** the gate FAILS, naming the class and the floor
- **And:** this is what makes a shrink-only budget mean anything — a budget that
  can only fall is worthless if the corpus under it can fall too, so deleting
  the rows the router fails is closed off as a route to a better number
- **Except:** a corpus that declares no class column at all. Every plant grown
  before these classes existed carries a two-column corpus, and failing them on
  upgrade would break every one, so `load_golden` sets `classed = False` and all
  three floors switch off. That exemption is keyed on the DATA, which makes it
  reachable by deletion: stripping the third column from every row and dropping
  both held-out classes reports `OK — contract consistency 98.4% (60/61)` and
  exits 0, with the gate reduced to a contract-consistency check. The exemption
  is correct for a field plant and is closed for the seed's own corpus by
  `test_the_shipped_corpus_may_not_drop_its_class_column`, which requires all
  three classes to be declared and each held-out class to meet its floor.

### Contract: THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO
- **Given:** the `adversarial` class, whose rows exist to bait the router
- **When:** confident-wrong answers are counted within it
- **Then:** the gate fails only above `ADVERSARIAL_CONFIDENT_WRONG_BUDGET`,
  which is a recorded ratchet in `tests/ratchets.json` and may only fall
- **And:** the budget is non-zero by design — a bait that never succeeds is not
  a bait, and a zero here would be satisfied by writing weaker rows. It is the
  one place a confident-wrong answer is tolerated, and it is tolerated in a
  named, counted, shrink-only class rather than silently
- **And:** lowering it is only legitimate when the ROUTER improved; tuning a
  trigger to a row, or rewriting the row, is the dishonesty the class exists
  to expose

### Contract: ABSTENTION_IS_A_CORRECT_OUTCOME
- **Given:** a paraphrase row the router has no signal for
- **When:** it returns LOW or NONE
- **Then:** the gate does not fail *on that row*
- **And:** the reverse rule would push the fix toward widening triggers until
  something matches, which is how a router starts answering confidently about
  things it cannot know
- **Except:** the class as a whole carries `PARAPHRASE_FLOOR`, a shrink-only
  floor on confident-correct answers. A corpus of 17 paraphrase rows that
  abstains on all 17, with zero confident-wrong, FAILS — so abstention is
  correct per row and insufficient in aggregate. This is the mirror of
  `THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO`: one bounds confident-wrong
  from above, the other bounds confident-correct from below.
- **And:** that floor is an absolute count, so it is bounded by the roster it
  was measured over — `AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER` below.

### Contract: AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER
- **Given:** `PARAPHRASE_FLOOR`, an absolute count of confident-correct
  held-out answers
- **When:** the roster being scored is not the one the floor was measured over,
  meaning every node of it carrying the `origin: seed` ownership marker, named
  by `MEASURED_ROSTER_ORIGIN`
- **Then:** the count is reported and the gate does not turn on it
- **And:** the floor's recorded VALUE is unchanged by this scoping. Scoping
  says what the number is measured over; it is not a route to moving the
  number, which stays a ratchet in `tests/ratchets.json` and the owner's to
  widen
- **And:** the reason is that scoring is relative to the set of agents being
  ranked. Every agent a roster gains raises the document frequency of ordinary
  words and lowers every term's weight, so a top pick that is still correct can
  fall below the confidence band and be counted as an abstention. Enlarging the
  roster is what the growth protocols exist to do, so a floor keyed to whatever
  roster is on disk is a penalty for taking the path the seed mandates.
  `EVAL_THRESHOLD` was set with documented headroom for exactly that shift and
  this floor was set with none, which is the asymmetry being closed
- **Except:** the seed's own roster, which is entirely seed-owned and therefore
  always the measured one, so the gate is live wherever the number was
  measured. Like the `classed` exemption above, this one is keyed on an INPUT
  and is reachable by changing that input, and a roster that declares no origin
  at all takes it too. That is the fail-open side of the same trade: an
  unrecognised roster yields a number to read rather than a verdict nobody can
  act on.

### Contract: CONTRACT_ROW_ABSTENTION_IS_A_DEFECT
- **Given:** a row labelled `contract`
- **When:** the router abstains on it
- **Then:** it is reported as a defect — the agent's own trigger no longer
  selects it

### Contract: UNKNOWN_DOMAIN_MUST_ABSTAIN
- **Given:** a row labelled `unknown-domain`
- **When:** the router scores it
- **Then:** the band is LOW or NONE, routing the session to the commission path,
  and a leak fails the gate
- **Except:** this is a property of the corpus, not a universal property of the
  router. It was written as "a task nothing on the roster is written for" and
  that reading is false: two ordinary roster words co-occurring are enough for
  HIGH, because each is a full-strength hit at weight 2 and the runner-up is
  not. `design a crop rotation for the north field` routes HIGH to `security`
  (16 against 4); `diagnose the rattle and the suspension design in my car`
  routes HIGH to `multi-agent-architect`. Nothing on the roster is written for
  agronomy or auto repair.
- **And:** an earlier version of this clause said "requiring a second
  independent signal before HIGH would close it". That was written without being
  tested, and it is false. Three mechanisms were tried and measured against the
  shipped corpus: requiring two contributing terms (the foreign probes already
  have four or five — loose matching makes weak hits count); capping how much of
  the score one term may supply (probes 0.33-0.50, real rows 0.22-0.40, fully
  overlapping); and an absolute score floor (probes 14-16, real HIGH rows 16-72,
  so a floor at 17 closes the probes and costs four real rows, two of them from
  the paraphrase class). **A foreign-domain task is not winning on a lucky rare
  word — it collects the same scattered weak matches a real task does**, which is
  why no lexical rule separates them.
- **Therefore:** the band is RELATIVE and this spec does not claim otherwise. It
  says the winner beat the runner-up; it cannot say the task belongs to this
  roster. What mitigates it is that `--route` is advice a model mediates rather
  than a gate, so a confidently-wrong route is a bad hint and not a wrong
  action — and `--route` now prints a NOTE when the absolute score sits at the
  bottom of the range real tasks occupy. Telling `crop rotation` from `key
  rotation` is meaning rather than spelling, which is the case for the semantic
  layer recorded as the deferred U-34 decision, not something to be fixed here.

### Contract: COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE
- **Given:** a term that appears only as a fragment of a hyphenated compound on
  either side of the comparison
- **When:** it is matched
- **Then:** it matches at the near-match tier, never the standalone tier
- **And:** `chain` taken from `supply-chain` cannot carry a confident route for
  a task about a chain of calls

### Contract: RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH
- **Given:** a term matching only one agent
- **When:** the match is a compound fragment, a prefix fold, or a
  description-only graze
- **Then:** it does not receive the full rare-term weight
- **And:** "distinctive" means a confident match is rare, not that a rare word
  brushed something

### Contract: AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS
- **Given:** a task word and a roster word that differ only by a regular English
  inflection (`nodes`/`node`, `checked`/`check`, `duties`/`duty`)
- **When:** they are matched
- **Then:** they match at the standalone tier, in BOTH routers, and the reduction
  is applied symmetrically to the task side and the roster side
- **And:** a route may not depend on the tense or number of a word — the first
  version of this rule tested only whether the task's word PREFIXED a roster
  word, which a plural never does, and 32% of the agent roster's vocabulary and
  39% of the node set's was unreachable by its own plural

### Contract: A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS
- **Given:** two distinct roster words that reduce to one stem
- **When:** the routers are gated
- **Then:** the collision must appear in the reviewed fixture, or the gate fails
- **And:** no mechanical rule separates a true merge (`pin`/`pinned`) from a
  false one (`rat`/`rating`), so the review is a person and the gate only makes
  skipping it impossible

### Contract: A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT
- **Given:** a first- or second-person pronoun in a task or a routing trigger
- **When:** the task is scored
- **Then:** it contributes nothing, in both routers
- **And:** `we` was live in three shipped triggers and `our` earned the
  rare-term bonus, routing a task to `security` on the strength of the word
  "our"

### Contract: VACUOUS_CORPUS_IS_REFUSED
- **Given:** a corpus in which every row expects abstention
- **When:** `--eval` runs
- **Then:** it fails closed rather than scoring 1.0 over zero routes

## 5. Non-functional requirements

- **Compatibility:** stdlib `python3` only; the router runs on every harness.
- **Cost:** `--eval` is a gate step, so it runs in seconds over the whole corpus.

## 6. Data shapes

```yaml
# agents/_routes.golden.tsv — one row per task
row:
  task:     { type: string }
  expected: { type: string }   # a roster agent name, or the sentinel "LOW"
  class:    { enum: [contract, paraphrase, adversarial, unknown-domain],
              default: contract }

# what each class is evidence FOR
contract:       "the trigger set is self-consistent — NOT that the router generalizes"
paraphrase:     "generalization; authored without reading any trigger set"
adversarial:    "resistance to bait phrasings"
unknown-domain: "the commission path is reachable"
```

## 7. Failure modes

### Failure: MISLABELLED_PARAPHRASE
- **Trigger:** a trigger-derived row carries `class: paraphrase`
- **Response:** non-zero exit naming the row and its overlap
- **Side effects:** none
- **Recovery:** relabel it `contract`, or write a real paraphrase

### Failure: CONFIDENT_MISROUTE
- **Trigger:** a confident band on a wrong specialist
- **Response:** non-zero exit naming task, band, got and expected
- **Side effects:** none
- **Recovery:** fix the mechanism that produced the confidence; do not edit the
  row, and do not widen the band threshold to hide it

## 8. Examples

```
contract        n=61  confident-correct=60  abstained=1   CONFIDENT-WRONG=0   mean-overlap-with-target=0.96
paraphrase      n=17  confident-correct=4   abstained=13  CONFIDENT-WRONG=0   mean-overlap-with-target=0.15
adversarial     n=12  confident-correct=5   abstained=5   CONFIDENT-WRONG=2   mean-overlap-with-target=0.34
unknown-domain  n=5   confident-correct=5   abstained=0   CONFIDENT-WRONG=0   mean-overlap-with-target=0.00
```

The overlap figures are the point: the contract class shares almost all of its
vocabulary with the agent it selects and the paraphrase class shares little, so
they are not the same kind of evidence and averaging their accuracies would
produce a number describing neither. The `adversarial` line carries the only
tolerated confident-wrong count in the gate, against a ratcheted budget — a
worked example that omits it shows a reader a `--eval` report in which the one
place failure is permitted does not exist. This block was stale for four
consecutive review rounds; it is pasted from a live run rather than retyped.

```
$ agent-lint.py --route "chain of calls"
ROUTE (ranked, confidence: LOW)      # a fragment of `supply-chain` cannot carry HIGH

$ agent-lint.py --route "assess the supply-chain and secrets handling risk"
ROUTE (ranked, confidence: HIGH)     # the compound itself still routes
  security ... score=60
```

## 9. Acceptance criteria

- [x] AC-1: no figure is printed without its corpus — maps to
      EVERY_NUMBER_NAMES_ITS_CORPUS, OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY
- [x] AC-2: the held-out set cannot be quietly corrupted — maps to
      HELD_OUT_STAYS_HELD_OUT, HELD_OUT_SET_MAY_NOT_BE_EMPTIED
- [x] AC-3: the gate turns on confident-wrong, not top-1 — maps to
      CONFIDENT_WRONG_IS_THE_GATE, ABSTENTION_IS_A_CORRECT_OUTCOME
- [x] AC-4: a fragment cannot speak for its compound — maps to
      COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE, RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH
- [x] AC-5: the gate cannot pass vacuously — maps to VACUOUS_CORPUS_IS_REFUSED
- [x] AC-6: a route does not turn on the tense or number of a word — maps to
      AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS,
      A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS,
      A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT
- [x] AC-7: an absolute limit gates only where it was measured — maps to
      AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER

## 10. Test mapping

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| EVERY_NUMBER_NAMES_ITS_CORPUS | test_classes_are_reported_separately_and_never_averaged | tests/test_agent_lint.py | integration | green |
| OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY | test_classes_are_reported_separately_and_never_averaged | tests/test_agent_lint.py | integration | green |
| HELD_OUT_STAYS_HELD_OUT | test_a_near_copy_may_not_be_labelled_paraphrase | tests/test_agent_lint.py | integration | green |
| HELD_OUT_STAYS_HELD_OUT | test_a_padded_trigger_copy_cannot_pass_as_held_out | tests/test_agent_lint.py | integration | green |
| MISLABELLED_PARAPHRASE | test_a_near_copy_may_not_be_labelled_paraphrase | tests/test_agent_lint.py | integration | green |
| HELD_OUT_SET_MAY_NOT_BE_EMPTIED | test_golden_corpus_is_wellformed_and_covers_the_roster | tests/test_agent_lint.py | integration | green |
| HELD_OUT_SET_MAY_NOT_BE_EMPTIED | test_a_row_expecting_low_may_not_wear_another_class | tests/test_agent_lint.py | integration | green |
| CONFIDENT_WRONG_IS_THE_GATE | test_a_confident_wrong_route_fails_even_when_the_average_is_fine | tests/test_agent_lint.py | integration | green |
| THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO | test_exceeding_the_budget_fails_the_gate | tests/test_agent_lint.py | integration | green |
| THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO | test_the_shipped_corpus_sits_under_the_budget | tests/test_agent_lint.py | integration | green |
| NEITHER_HELD_OUT_SET_MAY_BE_THINNED | test_emptying_a_whole_class_is_refused | tests/test_agent_lint.py | integration | green |
| THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO | test_the_budget_is_ratcheted_shrink_only | tests/test_agent_lint.py | integration | green |
| CONFIDENT_MISROUTE | test_a_confident_wrong_route_fails_even_when_the_average_is_fine | tests/test_agent_lint.py | integration | green |
| ABSTENTION_IS_A_CORRECT_OUTCOME | test_abstention_on_a_held_out_row_is_not_a_failure | tests/test_agent_lint.py | integration | green |
| CONTRACT_ROW_ABSTENTION_IS_A_DEFECT | (no test — see §11) | — | — | pending |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_agent_router_matches_its_documented_examples | tests/test_router_reach.py | unit | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_knowledge_router_matches_its_documented_examples | tests/test_router_reach.py | unit | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_inflection_does_not_change_the_top_pick | tests/test_router_reach.py | integration | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_every_roster_word_is_reachable_by_its_plural | tests/test_router_reach.py | integration | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_every_load_when_word_is_reachable_by_its_plural | tests/test_router_reach.py | integration | green |
| A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS | test_agent_roster_collisions_are_reviewed | tests/test_router_reach.py | integration | green |
| A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS | test_load_when_collisions_are_reviewed | tests/test_router_reach.py | integration | green |
| A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT | (no test — see §11) | — | — | pending |
| UNKNOWN_DOMAIN_MUST_ABSTAIN | test_the_shipped_unknown_domain_rows_all_abstain | tests/test_agent_lint.py | integration | green |
| UNKNOWN_DOMAIN_MUST_ABSTAIN | test_a_leaking_unknown_domain_row_fails_the_gate | tests/test_agent_lint.py | integration | green |
| COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE | test_a_compound_fragment_does_not_earn_a_confident_route | tests/test_agent_lint.py | integration | green |
| COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE | test_the_compound_itself_still_routes | tests/test_agent_lint.py | integration | green |
| RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH | test_a_rare_word_matching_only_a_description_does_not_dominate | tests/test_agent_lint.py | integration | green |
| RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH | test_a_rare_word_in_a_real_trigger_still_dominates | tests/test_agent_lint.py | integration | green |
| COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE | test_a_de_hyphenated_compound_still_reaches_its_owner | tests/test_agent_lint.py | integration | green |
| COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE | test_an_invented_compound_earns_nothing | tests/test_agent_lint.py | integration | green |
| VACUOUS_CORPUS_IS_REFUSED | test_a_corpus_that_asks_for_no_routes_is_vacuous | tests/test_agent_lint.py | integration | green |
| AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER | test_a_grown_roster_reports_the_paraphrase_floor_instead_of_gating_on_it | tests/test_agent_lint.py | integration | green |
| AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER | test_the_measured_roster_still_gates_on_the_paraphrase_floor | tests/test_agent_lint.py | integration | green |
| AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER | test_scoping_the_floor_did_not_move_its_recorded_value | tests/test_agent_lint.py | integration | green |

## 11. Open questions

**Two contracts have no regression.** `A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT`
cited `test_scoring_generic_word_does_not_misroute`, which routes "improve the
code" and asserts the band is not HIGH — that is the document-frequency
weighting, not the pronoun stopword list, and it touches one router where the
contract says "in both routers". No test scores a pronoun against either
stopword block — `tests/test_agent_lint.py` mentions pronouns in prose only, in the
class-deletion subtest, and the sentence here previously claimed the grep was empty, which it
is not.
Closing it means a test that scores a pronoun against both routers' stopword
blocks and asserts zero contribution. The row now reads `pending`.

**`CONTRACT_ROW_ABSTENTION_IS_A_DEFECT` has no regression.** Its §10 row cited
`test_eval_fails_below_threshold`, which builds a corpus of confidently-WRONG
contract rows and asserts a non-zero exit — none of those rows abstains, so the
test never exercised this contract and the row was certifying coverage that did
not exist. The live gate does print `✗ [contract] contract row abstained: …`
and exits 0, and `grep -rn "contract row abstained" tests/` finds nothing: the
one real abstention in the shipped corpus could be dropped from the report and
every gate would stay green. The row now reads `pending`. Closing it means a
test that plants an abstaining contract row and asserts the report names it.


**Recorded debt: how many contracts here carry no test naming them is not
written down.** Running the seed's own `spec-lint.py` against `docs/specs/` (it
cannot reach them in place — its `SPECS` path resolves inside
`templates/knowledge-graph/`, which `tools/gate-registry.py` discloses as a
scope gap) names the contracts with no test, and `seed-lint`'s
`check_spec_rows_name_their_contract` holds the stricter figure — whether THIS
row's test names THIS contract — against a recorded budget.

The figure used to sit here as a sentence, and it shipped wrong three times:
once because a contract was mapped and the numerator moved, once because a
contract was added in the same edit and the denominator did not, and once
because tests were renamed to carry their slugs and nobody came back to the
prose. It was a count with no deriving home, which is the defect CLAUDE.md
names, so it has no home here either. Derive it:

```sh
python3 templates/knowledge-graph/spec-lint.py --specs docs/specs
grep -c '^### Contract:' docs/specs/SPEC-*.md
```

This does not mean the behaviour is untested — §10 maps each contract to a test
that exists and passes, and those tests were checked by hand. It means the
mapping is held by a human reading a table rather than by a grep, so a renamed
test silently orphans its contract. `seed-lint`'s `check_spec_test_mapping`
catches a row citing a file that lacks the contract's LABEL (`M7`, `X1`), but
both specs name their contracts in words, and three SPEC-0001 rows cite a test
file carrying no label at all. The honest position is that §10 is a reviewed
claim, not a derived one.

Closing it means either renaming tests to carry their contract slug, or teaching
the mapping check to match on contract name. Neither is done; the number is here
so it is not invisible.



| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| The bands are not calibrated per specialist | HIGH is cited as evidence in briefs, so it should mean the same thing for every agent | HIGH currently means "best score clears FLOOR and leads the runner-up by 1.5x", which is a property of the scores and not a measured correctness rate | data-ml | a per-specialist calibration run over a corpus large enough to have per-agent rows |
| The paraphrase floor is met at exactly the router's achievement | `PARAPHRASE_FLOOR` is 4 and the router is confidently correct on 4 of 18 held-out rows, so the floor has zero slack and any regression fails the gate. That is the design ("a floor is what the router achieves"), not a gap — but it also means the floor cannot rise without the router improving, which is the measurement U-34 is for. Derive both halves with `agent-lint.py --eval --dir agents` and `ratchet-lint.py --show`; the comment block above `PARAPHRASE_FLOOR` is the home for the reasoning | Raising it requires improving the router and re-measuring, never editing a row. It moved DOWN once, when a two-way overlap check found a trigger copy in the held-out set, and UP from 2 to 4 when the two rows of slack were found to have no defender | data-ml | Track E measurement (U-34) |
| This table was once green against a test that did not exist | A spec whose §10 cites a fabricated name is worse than one with an honest gap: it certifies coverage nobody can find | Every row here has been grepped against the suite. Two contracts are honestly `pending`; the rest are a reviewed claim rather than a derived one, and `spec-lint.py --specs docs/specs` now derives the real figure on every gate run | data-ml | re-grep §10 on every spec change |
