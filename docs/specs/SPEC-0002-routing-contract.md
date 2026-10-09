---
status: back-written
status_date: 2026-10-07
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
  The one pass held since covers only the 8.1.2 rows: product [x]
  (2026-10-09, `product-8.1.2c`: §3 states the seed skill a path route adds,
  that only seed skills are added, the fixed order and the cap; AC-11 maps
  PATH_ROUTE_ADDS_SEED_SKILL_PHRASES, PATH_ROUTE_SKILL_ADDITION_IS_CAPPED and
  the failure PATH_ROUTE_SKILLS_OVER_CAP; read against the ADR-0026
  "Amendment, 8.1.2" the owner ratified). The rest of the spec stays
  unsigned, as above.

- **Owner:** data-ml
- **Date:** 2026-09-13
- **Last reviewed:** 2026-10-07
- **Related grill section:** docs/plans/grill-7.15.0-remediation.md §0.3, §5 slice 7; docs/plans/grill-7.37.0-routing-context.md §9 (the node router, 7.37.0); docs/plans/grill-8.1.2-tool-surfacing.md §12 question 12 (a path route adds the seed skills whose phrase the task holds, 8.1.2)
- **Related ADRs:** adr-0001-mechanical-agent-router, adr-0003-enforcement-layering-honesty, adr-0026-node-router-ladder-and-gated-corpus (accepted; its "Amendment, 8.1.2" ratified by the owner 2026-10-07, commit af0bbb0), adr-0030-a-seed-tool-is-surfaced-by-a-seed-skill
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

Since 7.37.0 it also covers the node router, `graph-lint.py --plan` (the
`resolve()` function) and its `--eval`, which had no contract and no corpus.
A measured node-route corpus showed it loading forbidden nodes on every
adversarial row and abstaining on one of nine unknown-domain rows
(ADR-0026). The change is to routing quality, measured per class; no token
saving is claimed for it.

## 2. Scope

- **In scope:**
  - what `--eval` reports and what it gates on
  - the corpus classes and what each is evidence for
  - confidence-band semantics and abstention
  - the honesty checks that keep the held-out set held out
  - since 7.37.0, the node router: the order of its signal tiers, its cap,
    its abstentions and their notices, the lexical guards it shares with the
    agent router, and `graph-lint.py --eval`
  - since 8.1.2, the seed skills a path route adds beside the node that owns
    the path (ADR-0026 "Amendment, 8.1.2"), and the gap and slot rules by
    which a task holds a trigger phrase across a path or an identifier it
    names
- **Out of scope:**
  - the scoring algorithms' internals (ADR-0001 and ADR-0026 own the designs;
    changing them requires re-measuring against this spec, not amending it).
    The node router's tier order is contracted because a task can observe it
  - the format of the node router's output, which SPEC-0003 covers
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

The node router answers a task with the nodes to read. When the task names a
node id or a path, that wins over any word match. When the task names a
path a node owns and also holds a trigger phrase of a seed skill, the skill
loads beside the owning node, so a question about a file reaches the seed
skill that says how to answer it (8.1.2). Only a skill the seed ships is
added this way: a plant's own skill, or a seed page of another kind, whose
phrase the task holds does not load beside the path. The owning node is
listed first and the added skills after it, always in the same order, so
the same task loads the same nodes every time. At most
`PATH_TIER_SKILL_CAP` skills are added; when the task holds the phrases of
more, none is added and the owning node loads alone, so naming a file never
floods the session. A task that names a node id gets that node and no added
skill. When nothing matches
confidently, it loads nothing and its notice names the protocol entry nodes
and asks for a sharper task line, instead of forcing root. A pasted brief is
not routed: the notice asks for the task line.

## 4. Functional contracts

### Contract: EVERY_NUMBER_NAMES_ITS_CORPUS
- **Given:** any figure either router's `--eval` prints (`agent-lint.py` or,
  since 7.37.0, `graph-lint.py`)
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
- **Given:** a row in either held-out class (`paraphrase` or `adversarial`),
  in either router's corpus; for the node corpus the target's vocabulary is
  the `load_when` of its required ids
- **When:** its vocabulary overlap with its target exceeds
  `PARAPHRASE_MAX_OVERLAP` (0.50; it was 0.80 until a reviewer smuggled four
  trigger copies past it)
- **Then:** the gate FAILS, naming the row
- **And:** the failure is fatal, not a warning — a diagnostic with no effect on
  exit status tells a reader something is wrong and the gate that all is fine
- **Node corpus:** the overlap is the larger of the task side (the share of
  the row's content words the target's `load_when` holds) and the trigger
  side, read only over `load_when` pieces of `HELD_OUT_PIECE_WORDS` content
  words or more (§6). A node's pieces are often one or two words
  (`canonize`, `grill.md`); a row that names one whole is about that node,
  not written from its triggers, and read at every length four of the fifteen
  verbatim owner prompts measured 1.0. A piece of three words held verbatim
  is a trigger copy, and the row is a contract row
- **Node corpus ceiling:** amended 2026-10-01 (architect pass on increment
  3). The node corpus's overlap is a different measure from the agent
  corpus's, so its ceiling is the node router's own constant,
  `GRAPH_PARAPHRASE_MAX_OVERLAP` in `graph-lint.py`, not a second copy of
  `PARAPHRASE_MAX_OVERLAP`. Both it and `HELD_OUT_PIECE_WORDS` are ratchets
  registered `max` in `tests/ratchets.json`, because raising either one
  loosens this rule. Before the amendment `graph-lint.py` defined
  `PARAPHRASE_MAX_OVERLAP` with nothing binding it to agent-lint's value, and a
  raise to 0.9 passed every gate

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
- **When:** the agent router returns LOW or NONE, or the node router loads
  nothing with a `no_signal` notice
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
- **Then:** it matches at the near-match tier, never the standalone tier, in
  both routers (the node router since 7.37.0)
- **And:** `chain` taken from `supply-chain` cannot carry a confident route for
  a task about a chain of calls

### Contract: RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH
- **Given:** a term matching only one agent
- **When:** the match is a compound fragment, a prefix fold, or a
  description-only graze
- **Then:** it does not receive the full rare-term weight, in both routers
  (the node router since 7.37.0)
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

### Contract: A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT
- **Given:** a first- or second-person pronoun in a task or a routing trigger
- **When:** the task is scored
- **Then:** it contributes nothing, in both routers
- **And:** `we` was live in three shipped triggers and `our` earned the
  rare-term bonus, routing a task to `security` on the strength of the word
  "our"
- **Note:** since 7.37.0 a test scores a pronoun against both routers (§11
  recorded none before)

### Contract: VACUOUS_CORPUS_IS_REFUSED
- **Given:** a corpus in which every row expects abstention
- **When:** either router's `--eval` runs
- **Then:** it fails closed rather than scoring 1.0 over zero routes
- **And:** the node corpus also refuses, naming the row, an adversarial row
  whose `forbidden_ids` is `-` (it baits nothing, yet counts toward
  `GRAPH_ADVERSARIAL_MIN_ROWS`) and an unknown-domain row that lists required
  ids. The refusal names the offending row by its task text. Added
  2026-10-01 (architect pass on increment 3, reviewer note N7)

### Node router (`graph-lint.py`), since 7.37.0

These run the real `graph-lint.py --plan-json=<task>` over a fixture graph
built for the test, and read the document's `load`, `how` and `notices`
(SPEC-0003 §6). "Loads N" means N is in `load`; the `requires:` closure of a
loaded node always loads with it. Tiers, phrases and constants are §6's.

### Contract: GRAPH_ROUTE_NAMED_ID_LOADS_IT
- **Given:** a task that names an exact dotted node id (`kind.slug`) among
  other words, one of which alone would seed a different node lexically
- **When:** the router runs
- **Then:** the named node loads with `how.kind` `named_id`, and the node the
  other word would seed does not load
- **And:** a task word equal to an id with no `.` is not a tier-1 hit. The
  only such id is `root`, and it is an English word: `root cause of the
  crash` and `a pipe of edges from root to leaf` loaded root alone as
  `named_id` and nothing else. Root is named by its path (tier 2); the word
  `root` is an ordinary lexical term
- **Note:** amended 2026-10-01 (architect pass on increment 3, reviewer
  finding F2). Sign-offs not re-taken

### Contract: GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER
- **Given:** in turn a task naming: a node's file path; a path under a node's
  `repo:` prefix that is not a repository root; a path an expertise node's
  file pattern matches; a basename that one node file alone carries
- **When:** the router runs
- **Then:** the owning node loads with `how.kind` `named_path` (or
  `inferred` for the expertise pattern) and `how.detail` the path as named
- **And:** a basename two node files share loads neither by this tier, and a
  `repo:` value that names a repository root claims no path

### Contract: PATH_ROUTE_ADDS_SEED_SKILL_PHRASES
- **Given:** a fixture graph whose node `subsystem.app` claims `src/app.py`
  by `repo: src` over an existing folder `src/`, and a task naming
  `src/app.py` that holds, contiguous, one trigger phrase of each of: a
  `kind: skill` node with `origin: seed`; a `kind: skill` node with another
  `origin`, or none; a node of another kind with `origin: seed`
- **When:** the router runs
- **Then:** `load` holds `subsystem.app` with `how.kind` `named_path` and the
  seed skill with `how.kind` `phrase` and `how.detail` its phrase, with the
  skill's `requires:` closure; neither of the other two nodes loads
- **And:** the same task with the path removed routes by tier 3, as before
  8.1.2; a task that names a node id (tier 1) adds no skill; a tier-2 hit on
  more than `STRONG_TIER_CAP` nodes falls through to tier 3, as before
- **And:** a tier-2 `inferred` entry (an expertise file pattern) adds the
  seed skill the same way, and a seed skill that tier 2 itself loaded loads
  once, with its tier-2 kind
- **Note:** added 2026-10-07 for 8.1.2, on the owner's ruling of plan
  `docs/plans/grill-8.1.2-tool-surfacing.md` §12 question 12, option (a)

### Contract: PATH_ROUTE_SKILL_ADDITION_IS_CAPPED
- **Given:** the graph of PATH_ROUTE_ADDS_SEED_SKILL_PHRASES, and in turn a
  task naming `src/app.py` that holds the phrases of exactly
  `PATH_TIER_SKILL_CAP` seed skills and one that holds the phrases of one
  more
- **When:** `--plan-json` runs twice for each task
- **Then:** the first task loads every such skill, listed after the tier-2
  entries in node-id order; the second adds none and loads the tier-2
  entries with their closure alone (§7 `PATH_ROUTE_SKILLS_OVER_CAP`)
- **And:** the two runs of each task print the same `load`, byte for byte

### Contract: GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE
- **Given:** a task holding, contiguous, the content tokens of one trigger
  phrase (§6) of node N, of at least two content tokens, and naming no id or
  path
- **When:** the router runs
- **Then:** N loads with `how.kind` `phrase` and `how.detail` that phrase
- **And:** the same tokens in another order, or with a content word between
  them that is neither a path nor an identifier (§6), do not load N by this
  tier

### Contract: PATH_OR_IDENTIFIER_DOES_NOT_BREAK_A_PHRASE
- **Given:** a node N whose trigger phrase is `tests reach` (content tokens
  `tests`, `reach`), and in turn the tasks `which tests does a change to
  src/app.py reach`, `which tests save_order reach`, `which tests saveOrder
  reach` and `which tests widget reach`, no node owning any path they name
- **When:** the router runs
- **Then:** the first three load N with `how.kind` `phrase` and `how.detail`
  `tests reach`: a path or an identifier (§6) between two tokens of a phrase
  does not break the phrase
- **And:** the fourth does not load N by the phrase tier: `widget` is a
  content word that is neither
- **And:** the same holds for the seed skills a tier-2 route adds
  (PATH_ROUTE_ADDS_SEED_SKILL_PHRASES) and for composition descent, which
  read a phrase by the same rule; a phrase of one token is unchanged
  (`PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE`)
- **Note:** added 2026-10-09 for 8.1.2 (`architect-8.1.2i`): without it the
  owner's option (a) loaded no seed skill for the tasks it was ruled for,
  because the path a task names sits between the words of the skill's phrase

### Contract: PATH_OR_IDENTIFIER_FILLS_A_SLOT_WORD
- **Given:** a node N whose trigger phrases are `depends on this file`
  (`depends`, `file`) and `where is a name defined` (`name`, `defined`), and
  in turn the tasks `what depends on src/app.py`, `where is save_order
  defined`, `where is saveOrder defined` and `what depends on widget`, no
  node owning any path they name
- **When:** the router runs
- **Then:** the first three load N with `how.kind` `phrase`: a path word holds
  the phrase token `file`, and an identifier word holds the phrase token
  `name` (§6, slot words)
- **And:** the fourth does not load N by the phrase tier: a content word that
  is neither a path nor an identifier holds no slot word
- **And:** a task that writes the word `file` or `name` itself holds the slot
  as any word holds its token; a path does not hold `name`, and an
  identifier does not hold `file`

### Contract: STRONG_TIER_OVER_CAP_FALLS_THROUGH
- **Given:** a task that names more than `STRONG_TIER_CAP` node ids
- **When:** the router runs
- **Then:** no node loads with `how.kind` `named_id`; the result is the next
  tier's, as for the same task with the ids removed from the tier count
- **And:** the cap covers tiers 1 and 2 only. Tier 3 is not capped: every
  phrase hit loads (`PHRASE_TIER_FLOODS_LOAD`, §7). ADR-0026 says the same since
  its amendment of 2026-10-01

### Contract: PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE
- **Given:** an expertise node whose trigger is a two-word phrase, and in
  turn a task holding both words apart, and a task holding the phrase
- **When:** the router runs
- **Then:** the first task produces no `phrase` entry for the node, and the
  second loads it with `how.kind` `phrase` (tier 3). The first task may still
  load the node as `scored` when its words are two distinct confident terms
  (tier 4, `ONE_TERM_CANNOT_SEED_A_NODE`); held apart they are no phrase
- **And:** a trigger piece that reduces to one content token (`json`,
  `the CI workflow` -> `workflow`) seeds its node by no tier, even on a whole
  task word equal to it. It serves composition descent only
  (`COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE`). Tier 4 has no promotion: an
  expertise node enters from tier 4 only as a scored entry, on two distinct
  confident terms (`ONE_TERM_CANNOT_SEED_A_NODE`)
- **Note:** amended 2026-10-01 (architect pass on increment 3). The first
  text kept one-token promotion beside the lexical tier. Measured over the
  round's 74-row plant corpus, one-token promotion produced 7 of the 8
  remaining adversarial forbidden hits and none of the required hits of any
  class; with it removed, required recall is unchanged in every class (20/23,
  14/38, 7/13), forbidden hits fall from 9 to 2 and the adversarial mean
  loaded `est_tokens` from 15,979 to 11,742 (`--plan-json` per row, the
  round's scorer). No row of either corpus requires an expertise node, so the
  recall cost for a task that names only a technology word is not measured.
  A multi-word expertise phrase is a tier-3 hit, so promotion was reachable
  only through one-token pieces. Sign-offs not re-taken

### Contract: COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE
- **Given:** a loaded expertise parent that composes child C, and in turn a
  task holding one word of C's trigger phrase and a task holding the phrase
- **When:** the router runs
- **Then:** C does not load for the first task and loads for the second, with
  `how.kind` `composed`
- **And:** descent runs inside the closure of an entry of any tier, from a
  parent that is itself an entry or that loaded through another node's
  `requires:`
- **And:** a child trigger piece that reduces to one content token loads C on
  a whole task word equal to it. Descent chooses among the children of a
  parent already loaded, so one word is enough there and nowhere else
  (`PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE`)
- **And:** a node that a loaded node `requires:` is reported `requires`, never
  `composed`, whichever edge the traversal meets first (§6 "How precedence")
- **Note:** the three `And` clauses were added 2026-10-01 (architect pass on
  increment 3). They carry over what SPEC-0005's retired
  `PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE` held. Sign-offs not re-taken

### Contract: PUNCTUATION_DOES_NOT_CHANGE_A_TERM
- **Given:** a task word followed by `.`, `,`, `:`, `;`, `?`, `!` or `)`
- **When:** the router runs
- **Then:** the result equals the result for the same task without the mark

### Contract: IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS
- **Given:** a task whose only words that match any node are a kind prefix
  (`domain`, `subsystem`, `protocol`, `skill`, `agent`, `expertise`,
  `method`, `crosscut`) and the segments of a path no node owns
- **When:** the router runs
- **Then:** nothing loads, and the notice is `no_signal`
- **And:** this holds when a node's `load_when` writes a kind word itself
  (`which protocol applies`). A kind prefix is not a term on the task side
  either: `the protocol and skill for an agent hook` loaded
  `domain.frontmatter` by a score built on those words
- **Note:** the `And` clause was added 2026-10-01 (architect pass on increment
  3, reviewer finding F1). The code removed kind words from node names only.
  Removing them from task terms too left required recall unchanged in every
  class of the 74-row plant corpus and of the seed corpus. Sign-offs not
  re-taken

### Contract: ONE_TERM_CANNOT_SEED_A_NODE
- **Given:** a task whose lexical match with node N is one distinct confident
  term, however rare
- **When:** the router runs
- **Then:** N does not load by the lexical tier
- **And:** with a second distinct confident term of N's added, N loads

### Contract: NO_SIGNAL_LOADS_NOTHING
- **Given:** a task no tier matches (an unknown-domain task)
- **When:** the router runs
- **Then:** `load` is empty, root does not load, and `notices` holds exactly
  one `no_signal` notice whose text is §6's `NO_SIGNAL_TEXT` followed by the
  ids of the graph's `kind: protocol` nodes, sorted
- **And:** the notice does not name `docs/graph/index.md`

### Contract: LONG_TASK_ABSTAINS_WITH_NOTICE
- **Given:** a task with more than `LONG_TASK_TERMS` distinct content terms,
  one of which names a node id
- **When:** the router runs
- **Then:** `load` is empty, and `notices` holds exactly one `long_task`
  notice whose text is §6's `LONG_TASK_TEXT` with the term count
- **And:** a task of exactly `LONG_TASK_TERMS` distinct content terms is
  routed

### Contract: GRAPH_EVAL_GATES_PER_CLASS
- **Given:** a node-route corpus in the §6 shape, and in turn the seed's
  corpus at `tests/graph-routes.golden.tsv` and a copy with one forbidden id
  added to a row the router loads
- **When:** `graph-lint.py --eval <tsv>` runs
- **Then:** for each class it prints, on lines naming the class, required
  recall, rows fully covered, mean loaded nodes, the irrelevant share of
  loaded `est_tokens`, forbidden hits, and correct abstentions; the seed's
  corpus exits 0, and the copy exits 1 naming the breached ratchet
- **And:** a class figure is never averaged with another class

### Contract: GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH
- **Given:** the `GRAPH_*` ratchets, measured on the seed's corpus over a fresh
  seed install, whose every node carries `origin: seed` (named by
  `MEASURED_GRAPH_ORIGIN` in `graph-lint.py`)
- **When:** `graph-lint.py --eval <tsv>` runs over a graph holding any node
  whose `origin` is not `seed`, a missing `origin` included (a grown plant)
- **Then:** every class figure prints, one line says the ratchets are reported
  and not gated on this graph, and no `GRAPH_*` ratchet changes the exit
  status
- **And:** the corpus-honesty checks still gate on every graph: a malformed
  or unknown-id row, a vacuous corpus, and a held-out row over
  `GRAPH_PARAPHRASE_MAX_OVERLAP`
- **And:** on the measured graph every ratchet gates, as
  `GRAPH_EVAL_GATES_PER_CLASS` states, and the ratchets' recorded values are
  unchanged by this scoping
- **And:** the reason is the one `AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER`
  gives for the agent router. `graph-lint.py` ships into every plant
  (ADR-0026), so a floor of 8 correct unknown-domain abstentions, row floors of
  14 and 8, and share ceilings measured over the 75-node seed install would
  gate a plant's own corpus over its own graph, which they were never measured
  on, and a plant with fewer rows could never pass. The line that says so
  carries no digit, so it names no figure without a class
- **Note:** added 2026-10-01 (architect pass on increment 3, reviewer
  finding F4). The same fail-open trade as the agent router: a pre-growth
  plant routing the seed graph alone takes the measured key

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

```yaml
# tests/graph-routes.golden.tsv — the node-route corpus (7.37.0); plants keep their own beside docs/graph/
row:                              # tab-separated; `#` lines are comments
  task:          { type: string }   # a literal task, or "@file:<name>" beside the TSV
  required_ids:  { type: string }   # comma list of node ids that must load; "-" = none (an abstention is correct)
  forbidden_ids: { type: string }   # comma list of node ids that must not load; "-" = none
  class:         { enum: [contract, paraphrase, adversarial, unknown-domain] }
```

The seed's corpus holds the rows of the round's 74-row measurement corpus
whose ids are all seed-owned, plus its unknown-domain rows (32 rows), and the
adversarial bait rows the tester adds, each naming the mechanism it baits.
Paraphrase rows are copied verbatim with their authoring date and never
tuned.

Node-router tiers, in order; the first tier with a hit decides the seeds:

| Tier | Hit | `how.kind` |
|---|---|---|
| 1 | an exact dotted node id as a task word (`root`, the one id with no `.`, is named by its path) | `named_id` |
| 2 | a node's file path; the longest `repo:` prefix of a path, ignoring a `repo:` value that names a repository root; an expertise file pattern; a basename one node file alone carries | `named_path`, `inferred` |
| 3 | a trigger phrase held contiguous | `phrase` |
| 4 | the lexical score, with at least two distinct confident terms per node | `scored` |

One addition follows tier 2, since 8.1.2 (ADR-0026 "Amendment, 8.1.2"). When
tier 2 decides the entries (`named_path` or `inferred`), each `kind: skill`
node with `origin: seed` whose trigger phrase the task holds, as tier 3
holds one, is added as an entry with `how.kind` `phrase`, after the tier-2
entries in node-id order; when more than `PATH_TIER_SKILL_CAP` such skills
hit, none is added. No other tier adds anything, and `how.kind` gains no
value, so the `cypress.plan/1` document (SPEC-0003 §6) is unchanged. A seed
skill says how a session uses a seed tool (ADR-0030), and the questions such
a tool answers usually name a file a plant node owns; without the addition
the first-tier rule loads the owner and never the skill. A node of another
origin is not added, so a plant's own phrases keep the first-tier rule. Measured 2026-10-07 on a fresh install of seed `373b341`: 3 of the 39
rows of `tests/graph-routes.golden.tsv` route by tier 2, and none holds a
phrase of any of the 15 seed skills, so no row, class figure or `GRAPH_*`
ratchet changes; a new seed skill's phrases are measured by the same gate
when it lands. The scripted session of SPEC-0003
`SESSION_INJECTION_WITHIN_BUDGET` names no owned path and holds no seed
skill, so `SESSION_INJECTION_MAX_BYTES` does not move.

`requires` and `composed` are closure kinds: they are reached from an entry of
any tier, never seeds. A tier-1 or tier-2 hit on more than `STRONG_TIER_CAP`
nodes is no hit; tier 3 is not capped. A
trigger phrase is one comma-separated piece of a `load_when` entry (or of an
expertise trigger); its content tokens are its words after the router's
stopword removal and inflection reduction, and a task holds it when those
tokens occur in the task's content-token sequence consecutively and in order,
read with two rules since 8.1.2 (`PATH_OR_IDENTIFIER_DOES_NOT_BREAK_A_PHRASE`,
`PATH_OR_IDENTIFIER_FILLS_A_SLOT_WORD`):

- **Gap rule.** Between two tokens of the phrase the task may hold any number
  of path words and identifier words, which are skipped. Only between: a
  phrase still starts at its first token and ends at its last.
- **Slot words.** A phrase token that is the word `file` is held by a path
  word, and one that is the word `name` by an identifier word, as well as by
  the word itself. A `load_when` piece writes the place of a file or a name
  the task will name as `this file`, `a file` or `a name`.

An identifier is a task word, as the content-token sequence reads it, that is
not a path and that, as written in the task before lowercasing, holds `_`
with a letter or digit on each side (`save_order`, `MAX_BYTES`) or a lowercase
letter directly followed by an uppercase one (`saveOrder`, `SaveOrder`,
`TypeScript`). A word written all in capitals (`README`, `JSON`) is not one.
The two rules only add holds: every phrase a task held before still holds, a
content word that is neither a path nor an identifier still breaks a phrase,
and a one-token piece is still read only as a whole task word equal to it.
They apply wherever a phrase is held: tier 3, the seed skills tier 2 adds,
and composition descent. An identifier stays a lexical term for tier 4, and a
path stays none (`IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS`). Measured 2026-10-09
(`architect-8.1.2i`, the rule prototyped on a scratch install of `cb57595`
plus the uncommitted 8.1.2 work): `tests/graph-routes.golden.tsv` gives the
same figures in every class, and over its 39 rows and the 96 task rows of
each of the two plants' `docs/graph/agents/_routes.golden.tsv` (their graphs
copied to a scratch directory), no task loads a different node list; only
the nine tasks written for this question changed, each now loading
`skill.source-index` by `phrase`.
A piece that reduces to one content token is not a phrase for tiers 3 and 4;
it is read only by composition descent. A kind prefix, a dotted node id, and a
path with its segments are not lexical terms of the task, and a node's name
drops its kind prefix. A path is a word holding `/` or `*`, or one that looks like a file name
(`main.tf`); `node.js` and `asp.net` therefore count as paths, never as
lexical terms. Trailing punctuation is removed before a term is compared.

How precedence: an entry keeps its tier's kind. The closure follows every
`requires:` edge it has met before it descends to a composed child, so a node
that the entries' `requires:` closure reaches is `requires`, never `composed`,
whichever edge the walk meets first. A node first reached by descent is
`composed`, also when a child loaded below it requires it back (a composed
child usually requires its composing parent).

Constants, in `graph-lint.py`, one home each:

| Name | Value |
|---|---|
| `STRONG_TIER_CAP` | 3 |
| `PATH_TIER_SKILL_CAP` | 2, the most seed skills a tier-2 route adds; over it none is added (8.1.2). No routed row of the 74-row plant corpus or the seed corpus held the phrases of more than two nodes (`PHRASE_TIER_FLOODS_LOAD`) |
| `LEXICAL_MIN_TERMS` | 2, the distinct confident terms a tier-4 entry needs |
| `LONG_TASK_TERMS` | 100, distinct content words; over every prompt a person typed in the round (the owner-framing row: 66) and an order of magnitude under the pasted brief (1,332). No row of the seed's corpus has more than 20 |
| `NO_SIGNAL_TEXT` | `no node matches this task; route a sharper task line, or enter a protocol:` |
| `LONG_TASK_TEXT` | `task too long to route (<n> terms); run --plan on the task line` |
| `HELD_OUT_PIECE_WORDS` | 3, the shortest `load_when` piece the trigger side of the node corpus's overlap reads; a ratchet, `max` |
| `GRAPH_PARAPHRASE_MAX_OVERLAP` | 0.50, the node corpus's held-out ceiling (`HELD_OUT_STAYS_HELD_OUT`); a ratchet, `max` |
| `MEASURED_GRAPH_ORIGIN` | `seed`, the `origin` every node of the graph the `GRAPH_*` ratchets were measured on carries (`GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH`) |

The `no_signal` notice text is `NO_SIGNAL_TEXT`, one space, then the
protocol ids sorted and separated by `, `.

The `no_signal` line on the seed's graph is about 410 characters (17 protocol
ids), about 155 tokens at the measured 2.65 characters per token; it replaces
an unknown-domain route of about 1,360 tokens, and is not a pointer to
`index.md` (about 5,500 tokens).

Ratchets in `tests/ratchets.json`, set at the values measured after the
change and tighten-only: `GRAPH_CONTRACT_RECALL_MIN`,
`GRAPH_ADVERSARIAL_FORBIDDEN_MAX`, `GRAPH_UNKNOWN_ABSTAIN_MIN`,
`GRAPH_IRRELEVANT_SHARE_MAX` (a map by class), `GRAPH_PARAPHRASE_MIN_ROWS`,
`GRAPH_ADVERSARIAL_MIN_ROWS`; they gate only on the measured graph
(`GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH`). `GRAPH_PARAPHRASE_MAX_OVERLAP` and
`HELD_OUT_PIECE_WORDS` are registered beside them and gate on every graph. On
any other graph `--eval` prints one line, after the class lines, that holds no
digit and says the ratchets are `not gated`; it may name the ratchets the
figures pass, by name only. The map has no `unknown-domain` key: every node
such a row loads is irrelevant, so its share is 0 or 1 and adds nothing to
`GRAPH_UNKNOWN_ABSTAIN_MIN`. The values live in `graph-lint.py` and
`tests/ratchets.json`; the gate step is `tests/graph-route-eval.sh`, which runs
`--eval` in a fresh install.

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

### Failure: GRAPH_ROUTE_RATCHET_BREACHED
- **Contracts:** GRAPH_EVAL_GATES_PER_CLASS, GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH
- **Trigger:** a node-router change or a `load_when` edit moves a class figure
  past its ratchet, on the measured graph
- **Response:** `graph-lint.py --eval` exits 1 naming the class, the figure
  and the ratchet; on any other graph the figure prints and the exit status
  does not change
- **Side effects:** none
- **Recovery:** fix the mechanism or the node; do not edit a held-out row, and
  loosen a ratchet only on purpose, in `tests/ratchets.json`

### Failure: PHRASE_TIER_FLOODS_LOAD
- **Contracts:** GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE
- **Trigger:** a task of up to `LONG_TASK_TERMS` words holds the trigger
  phrases of many nodes
- **Response:** every tier-3 hit loads, uncapped. This carries forward the
  owner's ruling for phrase hits (SPEC-0005, ruling pass 0, "every hit loads,
  uncapped"), which retired with `PROMOTION_FLOODS_LOAD`. Measured
  2026-10-01: no routed row of the 74-row plant corpus or the seed corpus held
  the phrases of more than two nodes, so a cap here would change no measured
  route
- **Side effects:** more tokens on a compound task
- **Recovery:** sharpen the trigger (`skill.knowledge-graph` rule 5); the
  owner may cap tier 3 under `STRONG_TIER_CAP` with a new amendment
- **Note:** added 2026-10-01 (architect pass on increment 3)

### Failure: PATH_ROUTE_SKILLS_OVER_CAP
- **Contracts:** PATH_ROUTE_SKILL_ADDITION_IS_CAPPED
- **Trigger:** a task naming a path a node owns holds the phrases of more
  than `PATH_TIER_SKILL_CAP` seed skills
- **Response:** no skill is added; the tier-2 entries load alone, as before
  8.1.2. A strong signal that names too much is no signal, as
  `STRONG_TIER_OVER_CAP_FALLS_THROUGH` holds for tiers 1 and 2
- **Side effects:** none
- **Recovery:** route the question without the path, or name the skill's id
  (tier 1); sharpen a seed skill's trigger (`skill.knowledge-graph` rule 5)
- **Note:** added 2026-10-07 for 8.1.2

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
      A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT
- [x] AC-7: an absolute limit gates only where it was measured — maps to
      AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER
- [ ] AC-8 (7.37.0): a task that names a node, by id, path or a trigger
      phrase, gets that node first, and a strong signal that names too much
      falls through — maps to GRAPH_ROUTE_NAMED_ID_LOADS_IT,
      GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER, GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE,
      STRONG_TIER_OVER_CAP_FALLS_THROUGH
- [ ] AC-9 (7.37.0): a scattered word cannot carry a node — maps to
      PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE, COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE,
      PUNCTUATION_DOES_NOT_CHANGE_A_TERM, IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS,
      ONE_TERM_CANNOT_SEED_A_NODE, RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH,
      COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE,
      A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT
- [ ] AC-10 (7.37.0): the node router abstains with a cheap notice instead of
      guessing, and is gated per class — maps to NO_SIGNAL_LOADS_NOTHING,
      LONG_TASK_ABSTAINS_WITH_NOTICE, GRAPH_EVAL_GATES_PER_CLASS,
      EVERY_NUMBER_NAMES_ITS_CORPUS, HELD_OUT_STAYS_HELD_OUT,
      VACUOUS_CORPUS_IS_REFUSED, ABSTENTION_IS_A_CORRECT_OUTCOME
- [ ] AC-11 (8.1.2): a task that names a path a node owns (by its `repo:`
      claim or an expertise file pattern) and holds, contiguous, the trigger
      phrase of a `kind: skill`, `origin: seed` node loads the owning node
      (`how.kind` `named_path`, or `inferred`) and then that skill
      (`how.kind` `phrase`, `how.detail` its phrase) with its `requires:`
      closure; a skill of another `origin` and a seed node of another kind
      whose phrases the same task holds do not load; a seed skill tier 2
      already loaded is listed once, with its tier-2 kind. A task naming a
      node id adds no skill, the same task without the path routes by tier 3
      as before 8.1.2, and a tier-2 hit on more than `STRONG_TIER_CAP` nodes
      still falls through. With the phrases of exactly `PATH_TIER_SKILL_CAP`
      seed skills, each loads after the tier-2 entries, in node-id order;
      with one more, none is added and the tier-2 entries load alone with
      their closure. Two runs of each task print the same `load`, byte for
      byte — maps to PATH_ROUTE_ADDS_SEED_SKILL_PHRASES,
      PATH_ROUTE_SKILL_ADDITION_IS_CAPPED (failure PATH_ROUTE_SKILLS_OVER_CAP)

## 10. Test mapping

| Contract / Failure | Test name | Test file | Level | Status |
|---|---|---|---|---|
| EVERY_NUMBER_NAMES_ITS_CORPUS | test_classes_are_reported_separately_and_never_averaged | tests/test_agent_lint.py | integration | green |
| OVERLAP_IS_PUBLISHED_BESIDE_ACCURACY | test_classes_are_reported_separately_and_never_averaged | tests/test_agent_lint.py | integration | green |
| HELD_OUT_STAYS_HELD_OUT | test_a_near_copy_may_not_be_labelled_paraphrase | tests/test_agent_lint.py | integration | green |
| HELD_OUT_STAYS_HELD_OUT | test_a_padded_trigger_copy_cannot_pass_as_held_out | tests/test_agent_lint.py | integration | green |
| MISLABELLED_PARAPHRASE | test_a_near_copy_may_not_be_labelled_paraphrase | tests/test_agent_lint.py | integration | green |
| HELD_OUT_SET_MAY_NOT_BE_EMPTIED | test_golden_corpus_is_wellformed_and_covers_the_roster | tests/test_agent_lint.py | integration | green |
| HELD_OUT_SET_MAY_NOT_BE_EMPTIED | test_a_padded_trigger_copy_cannot_pass_as_held_out | tests/test_agent_lint.py | integration | green |
| CONFIDENT_WRONG_IS_THE_GATE | test_a_confident_wrong_route_fails_even_when_the_average_is_fine | tests/test_agent_lint.py | integration | green |
| THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO | test_exceeding_the_budget_fails_the_gate | tests/test_agent_lint.py | integration; the shrink-only clause is held by the ratchet-lint step (`tools/ratchet-lint.py`) | green |
| NEITHER_HELD_OUT_SET_MAY_BE_THINNED | test_emptying_a_whole_class_is_refused | tests/test_agent_lint.py | integration | green |
| CONFIDENT_MISROUTE | test_a_confident_wrong_route_fails_even_when_the_average_is_fine | tests/test_agent_lint.py | integration | green |
| ABSTENTION_IS_A_CORRECT_OUTCOME | test_abstention_on_a_held_out_row_is_not_a_failure | tests/test_agent_lint.py | integration | green |
| CONTRACT_ROW_ABSTENTION_IS_A_DEFECT | (no test — see §11) | — | — | pending |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_agent_router_matches_its_documented_examples | tests/test_router_reach.py | unit | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_knowledge_router_matches_its_documented_examples | tests/test_router_reach.py | unit | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_inflection_does_not_change_the_top_pick | tests/test_router_reach.py | integration | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_every_roster_word_is_reachable_by_its_plural | tests/test_router_reach.py | integration | green |
| AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS | test_every_load_when_word_is_reachable_by_its_plural | tests/test_router_reach.py | integration | green |
| A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT | test_a_word_every_task_writes_cannot_select_an_agent (agent router: `agent-lint.py --route` on pronouns alone) | tests/test_graph_lint.py | integration; a characterization, green on arrival | green |
| UNKNOWN_DOMAIN_MUST_ABSTAIN | test_the_shipped_unknown_domain_rows_all_abstain | tests/test_agent_lint.py | integration | green |
| UNKNOWN_DOMAIN_MUST_ABSTAIN | test_a_leaking_unknown_domain_row_fails_the_gate | tests/test_agent_lint.py | integration | green |
| COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE | test_a_compound_fragment_does_not_earn_a_confident_route | tests/test_agent_lint.py | integration | green |
| RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH | test_a_rare_word_in_a_real_trigger_still_dominates | tests/test_agent_lint.py | integration | green |
| VACUOUS_CORPUS_IS_REFUSED | test_a_corpus_that_asks_for_no_routes_is_vacuous | tests/test_agent_lint.py | integration | green |
| AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER | test_a_grown_roster_reports_the_paraphrase_floor_instead_of_gating_on_it | tests/test_agent_lint.py | integration | green |
| AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER | test_the_measured_roster_still_gates_on_the_paraphrase_floor | tests/test_agent_lint.py | integration | green |
| GRAPH_ROUTE_NAMED_ID_LOADS_IT | test_graph_route_named_id_loads_it | tests/test_graph_lint.py | integration; gains the bare-`root` row (amended 2026-10-01) | green |
| GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER | test_graph_route_named_path_loads_its_owner | tests/test_graph_lint.py | integration | green |
| PATH_ROUTE_ADDS_SEED_SKILL_PHRASES | test_path_route_adds_seed_skill_phrases (8.1.2): the §4 fixture; arms path removed (tier 3 as before), named id (no skill added), tier 2 over `STRONG_TIER_CAP` (tier 3 as before), an `inferred` entry, a seed skill that tier 2 loaded (once, its tier-2 kind) | tests/test_graph_lint.py | integration | green |
| PATH_ROUTE_SKILL_ADDITION_IS_CAPPED | test_path_route_skill_addition_is_capped (8.1.2): exactly `PATH_TIER_SKILL_CAP` skills added in node-id order after the tier-2 entries; one more adds none; two runs byte-identical | tests/test_graph_lint.py | integration | green |
| PATH_ROUTE_SKILLS_OVER_CAP | test_path_route_skill_addition_is_capped, its over-cap arm | tests/test_graph_lint.py | integration | green |
| PATH_OR_IDENTIFIER_DOES_NOT_BREAK_A_PHRASE | test_path_or_identifier_does_not_break_a_phrase (8.1.2): the §4 fixture, one arm per task (a path, a snake_case and a camelCase identifier between the tokens load N by `phrase`; a content word between does not); an arm where a tier-2 route adds a seed skill whose phrase a path splits; an arm where a composed child's phrase is split by an identifier | tests/test_graph_lint.py | integration | red |
| PATH_OR_IDENTIFIER_FILLS_A_SLOT_WORD | test_path_or_identifier_fills_a_slot_word (8.1.2): the §4 fixture, one arm per task; an arm where a path stands for `name` and an identifier for `file`, neither loading N | tests/test_graph_lint.py | integration | red |
| GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE | test_graph_route_phrase_loads_its_node | tests/test_graph_lint.py | integration; gains the rows moved from SPEC-0005's retired promotion tests: a piece holding a slash and a space, stopwords and short words dropped, the first held piece in `load_when` order as `how.detail` | green |
| GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE | test_plan_phrase_entry_brings_required_parent | tests/test_graph_lint.py | integration; rewritten from SPEC-0005 `test_plan_promoted_node_brings_required_parent` | green |
| STRONG_TIER_OVER_CAP_FALLS_THROUGH | test_strong_tier_over_cap_falls_through | tests/test_graph_lint.py | integration; gains a row where four nodes' phrases load by tier 3, uncapped (amended 2026-10-01) | green |
| PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE | test_promotion_needs_a_contiguous_phrase | tests/test_graph_lint.py | integration; the one-token row now asserts the node does not load (amended 2026-10-01) | green |
| COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE | test_composed_child_needs_its_own_phrase | tests/test_graph_lint.py | integration; gains a row whose parent enters by tier 3 (from SPEC-0005 `test_plan_promoted_node_descends_to_named_child`) and a one-token child row | green |
| COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE | test_plan_descends_on_specific_term | tests/test_graph_lint.py | unit, DescentTests; rewritten from SPEC-0005: each level descends on its child's whole phrase, never on a prefix fold, a major on its whole TFM token as `composed` | green |
| COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE | test_plan_descends_from_required_node | tests/test_graph_lint.py | unit, DescentTests; the task holds the child's phrase | green |
| COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE | test_plan_requires_outranks_composed | tests/test_graph_lint.py | unit; rewritten from SPEC-0005 `test_plan_seed_closure_is_accounted_before_promotion` (§6 how precedence) | green |
| PUNCTUATION_DOES_NOT_CHANGE_A_TERM | test_punctuation_does_not_change_a_term | tests/test_graph_lint.py | integration | green |
| IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS | test_ids_and_paths_are_not_lexical_terms | tests/test_graph_lint.py | integration; gains a fixture whose `load_when` writes a kind word (amended 2026-10-01) | green |
| ONE_TERM_CANNOT_SEED_A_NODE | test_one_term_cannot_seed_a_node | tests/test_graph_lint.py | integration | green |
| NO_SIGNAL_LOADS_NOTHING | test_no_signal_loads_nothing | tests/test_graph_lint.py | integration | green |
| LONG_TASK_ABSTAINS_WITH_NOTICE | test_long_task_abstains_with_notice | tests/test_graph_lint.py | integration | green |
| GRAPH_EVAL_GATES_PER_CLASS | test_graph_eval_gates_per_class | tests/test_graph_lint.py | integration | green |
| GRAPH_ROUTE_RATCHET_BREACHED | test_graph_eval_gates_per_class (measured graph: exit 1 naming the ratchet, green) and test_graph_ratchets_are_keyed_to_their_graph (any other graph: figures print, exit unchanged, green); both docstrings name this slug | tests/test_graph_lint.py | integration | green |
| GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH | test_graph_ratchets_are_keyed_to_their_graph | tests/test_graph_lint.py | integration; a graph holding one node of another origin breaches a ratchet, prints, exits 0; the seed graph still exits 1 | green |
| PHRASE_TIER_FLOODS_LOAD | test_strong_tier_over_cap_falls_through, its uncapped tier-3 row | tests/test_graph_lint.py | integration | green |
| EVERY_NUMBER_NAMES_ITS_CORPUS | test_graph_eval_every_number_names_its_corpus (node router) | tests/test_graph_lint.py | integration | green |
| HELD_OUT_STAYS_HELD_OUT | test_graph_held_out_stays_held_out (node router) | tests/test_graph_lint.py | integration | green |
| VACUOUS_CORPUS_IS_REFUSED | test_graph_vacuous_corpus_is_refused (node router) | tests/test_graph_lint.py | integration; gains the bait-free adversarial row and the unknown-domain row with required ids (amended 2026-10-01) | green |
| ABSTENTION_IS_A_CORRECT_OUTCOME | test_graph_abstention_is_a_correct_outcome (node router) | tests/test_graph_lint.py | integration | green |
| RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH | test_rarity_amplifies_only_a_confident_match (node router) | tests/test_graph_lint.py | integration | green |
| COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE | test_compound_fragment_is_weak_evidence (node router) | tests/test_graph_lint.py | integration | green |
| A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT | test_a_word_every_task_writes_cannot_select_an_agent (node router) | tests/test_graph_lint.py | integration; a characterization of both routers, green on arrival (the shared stopword block already held it) | green |

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

## 12. Changelog

This section did not exist before 2026-09-29. It was added with the entry
below, as SPEC-0001's was, so that an amendment is recorded rather than made
silently. The file carries no version field; `status_date` in the frontmatter
moves with each entry here.

- 2026-09-29 — test consolidation (`docs/plans/grill-test-consolidation.md`,
  S2). A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS is retired with its
  reviewed fixture and its two tests, by the owner's confirmation of the
  plan's §4 line 53. Nothing replaces the review: a new false stem merge in
  real vocabulary is no longer gated. §9 AC-6 no longer names it. §10 follows the folds:
  THE_ADVERSARIAL_BUDGET_IS_RATCHETED_NOT_ZERO keeps
  `test_exceeding_the_budget_fails_the_gate`, and its shrink-only clause cites
  the ratchet-lint step; AN_ABSOLUTE_FLOOR_IS_KEYED_TO_ITS_ROSTER drops the
  value-unchanged row, since ratchet-lint refuses a lowering of
  `PARAPHRASE_FLOOR`; RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH and
  COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE each cite the one table test that holds
  their rows; HELD_OUT_SET_MAY_NOT_BE_EMPTIED's second row cites
  `test_a_padded_trigger_copy_cannot_pass_as_held_out`, the table that takes
  in `test_a_row_expecting_low_may_not_wear_another_class`. No router behaviour
  changed; the status stays `back-written`.
- 2026-10-01: 7.37.0, written ahead of its RED
  ([ADR-0026](../decisions/adr-0026-node-router-ladder-and-gated-corpus.md);
  plan `docs/plans/grill-7.37.0-routing-context.md`, increment 3). None of
  the sign-offs §0 says are not owed was taken. The scope gains the node
  router, `graph-lint.py --plan` and `--eval`, as a routing-quality change
  with no token claim. §4 gains, live from this entry, a node-router section:
  GRAPH_ROUTE_NAMED_ID_LOADS_IT, GRAPH_ROUTE_NAMED_PATH_LOADS_ITS_OWNER,
  GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE, STRONG_TIER_OVER_CAP_FALLS_THROUGH,
  PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE, COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE,
  PUNCTUATION_DOES_NOT_CHANGE_A_TERM, IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS,
  ONE_TERM_CANNOT_SEED_A_NODE, NO_SIGNAL_LOADS_NOTHING,
  LONG_TASK_ABSTAINS_WITH_NOTICE and GRAPH_EVAL_GATES_PER_CLASS. Widened to
  the node router: EVERY_NUMBER_NAMES_ITS_CORPUS, HELD_OUT_STAYS_HELD_OUT,
  VACUOUS_CORPUS_IS_REFUSED, ABSTENTION_IS_A_CORRECT_OUTCOME,
  RARITY_AMPLIFIES_ONLY_A_CONFIDENT_MATCH and COMPOUND_FRAGMENT_IS_WEAK_EVIDENCE;
  A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT, which already said "both
  routers", gains the test §11 recorded as missing. AN_INFLECTION_MATCHES_THE_WORD_IT_INFLECTS
  already holds both routers and is unchanged. §6 gains the node corpus
  shape, the tier table, the constants and the ratchet names; §7 gains
  GRAPH_ROUTE_RATCHET_BREACHED; §9 gains AC-8 to AC-10; §10 gains `pending`
  rows. Until the RED lands, `spec-lint.py` counts the new contracts as
  uncovered. The status stays `back-written`.
- 2026-10-01: 7.37.0, increment 3 GREEN. §10's node-router rows name their
  tests and turn `green`; A_WORD_EVERY_TASK_WRITES_CANNOT_SELECT_AN_AGENT is a
  characterization of both routers, green on arrival. HELD_OUT_STAYS_HELD_OUT
  states the node corpus's overlap rule (orchestrator ruling F1, 2026-10-01);
  under it one seed corpus row holding a three-word `load_when` piece verbatim
  was reclassified `contract` (the corpus comment records it), and
  `GRAPH_PARAPHRASE_MIN_ROWS` was set from the post-change count. §6 records
  `LONG_TASK_TERMS` (100), `LEXICAL_MIN_TERMS`, `HELD_OUT_PIECE_WORDS`, the
  `no_signal` id separator, the unknown-domain gap in
  `GRAPH_IRRELEVANT_SHARE_MAX`, and the gate step. The status stays
  `back-written`.
- 2026-10-01: 7.37.0, architect pass on increment 3 (spawn
  `orchestrator.17.architect.1`), after the GREEN run met 21 SPEC-0005 and
  SPEC-0003 tests that pin the old node router, and after the increment's
  review. Sign-offs not re-taken. GRAPH_ROUTE_NAMED_ID_LOADS_IT reads dotted
  ids only. STRONG_TIER_OVER_CAP_FALLS_THROUGH states that tier 3 is
  uncapped, and §7 gains PHRASE_TIER_FLOODS_LOAD, which carries the owner's
  uncapped-hit ruling forward from SPEC-0005. PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE
  removes one-token promotion, which leaves tier 4 with no promotion.
  COMPOSED_CHILD_NEEDS_ITS_OWN_PHRASE takes over what SPEC-0005's retired
  PLAN_PROMOTED_NODE_TAKES_ITS_CLOSURE held. IDS_AND_PATHS_ARE_NOT_LEXICAL_TERMS
  covers kind words on the task side. VACUOUS_CORPUS_IS_REFUSED refuses
  bait-free adversarial rows and unknown-domain rows with required ids.
  HELD_OUT_STAYS_HELD_OUT names the node router's own
  `GRAPH_PARAPHRASE_MAX_OVERLAP`. The new GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH
  keys the `GRAPH_*` ratchets to the seed graph. §6 gains the closure kinds,
  how precedence, the path-word rule and three constants; tier 4's kinds drop
  `promoted`. §10 rows whose tests gain or move rows read `pending` until that
  RED lands. Until then `spec-lint.py` counts GRAPH_RATCHETS_ARE_KEYED_TO_THEIR_GRAPH
  as uncovered, and `seed-lint` reports the three new test names as missing:
  `test_graph_ratchets_are_keyed_to_their_graph`,
  `test_plan_phrase_entry_brings_required_parent` and
  `test_plan_requires_outranks_composed`. The status stays `back-written`.
- 2026-10-01: 7.37.0, increment 3 GREEN after the architect pass (spawn
  `orchestrator.19.implementer.6`), with the orchestrator's rulings on the
  tester's questions. PROMOTION_NEEDS_A_CONTIGUOUS_PHRASE's Then says what the
  test asserts: no `phrase` entry for the words held apart, a `scored` entry
  under the two-term floor still possible (Q1). VACUOUS_CORPUS_IS_REFUSED names
  the row by its task text (Q4). §6 pins the digit-free `not gated` line (Q3)
  and states how precedence as the walk runs it: `requires:` edges before
  descent, so a parent a composed child requires back stays `composed` (the
  `two levels` descent row, green before this pass, holds it). The seven §10
  rows the RED left red are green. `GRAPH_IRRELEVANT_SHARE_MAX` tightens to
  paraphrase 0.51 and adversarial 0.43 from the post-change seed run. The
  status stays `back-written`.
- 2026-10-01: 7.37.0 release pass, by `architect` (spawn
  `orchestrator.26.architect.1`). Every node-router contract the round added
  or widened reads `green`, and the `--eval` step gates the seed corpus at
  the ratchets set from the post-change run (ADR-0026, its Result section).
  The one `pending` row is CONTRACT_ROW_ABSTENTION_IS_A_DEFECT, untested as
  §11 says. No contract changed. The status stays `back-written`.
- 2026-10-07: 8.1.2, written ahead of its RED by `architect-8.1.2e`, on the
  owner's ruling of plan `docs/plans/grill-8.1.2-tool-surfacing.md` §12
  question 12, option (a), "change now"
  ([ADR-0026](../decisions/adr-0026-node-router-ladder-and-gated-corpus.md)
  "Amendment, 8.1.2", ratification pending). When tier 2 decides, the
  router also adds the `origin: seed` skill nodes whose trigger phrase the
  task holds, at most `PATH_TIER_SKILL_CAP` (2), after the tier-2 entries in
  node-id order. §2 and §3 say so; §4 gains PATH_ROUTE_ADDS_SEED_SKILL_PHRASES
  and PATH_ROUTE_SKILL_ADDITION_IS_CAPPED; §6 states the addition, its
  measurement (no golden row, class figure or ratchet moves; the session
  injection budget does not move) and the constant; §7 gains
  PATH_ROUTE_SKILLS_OVER_CAP; §9 gains AC-11; §10 gains `pending` rows. The
  related-ADR line no longer calls ADR-0026 proposed. Until the RED lands,
  `spec-lint.py` counts the two contracts as uncovered. The status stays
  `back-written`.
- 2026-10-09: 8.1.2 product pass (`product-8.1.2c`), §3 states the seed
  skill a path route adds, that only seed skills are added, the fixed order
  and the cap; AC-11 maps PATH_ROUTE_ADDS_SEED_SKILL_PHRASES,
  PATH_ROUTE_SKILL_ADDITION_IS_CAPPED and the failure
  PATH_ROUTE_SKILLS_OVER_CAP; read against the ADR-0026 "Amendment, 8.1.2"
  the owner ratified 2026-10-07 (commit af0bbb0). §0's Related ADRs line is
  updated to record the ratification. No contract changed. The status stays
  `back-written`.
- 2026-10-09: 8.1.2 RED (`tester-R-8.1.2`). §10's PATH_ROUTE_ADDS_SEED_SKILL_PHRASES,
  PATH_ROUTE_SKILL_ADDITION_IS_CAPPED and PATH_ROUTE_SKILLS_OVER_CAP rows name
  their tests in `tests/test_graph_lint.py` and read `red`. No contract
  changed. The status stays `back-written`.
- 2026-10-09: 8.1.2 GREEN blocker ruled (`architect-8.1.2i`). The owned-path
  arm of SPEC-0007 SOURCE_INDEX_SKILL_ROUTES_ITS_FOUR_QUESTIONS could not go
  green: the path or identifier a task names sat between the words of the
  seed skill's phrase, so PATH_ROUTE_ADDS_SEED_SKILL_PHRASES added nothing.
  §4 gains PATH_OR_IDENTIFIER_DOES_NOT_BREAK_A_PHRASE and
  PATH_OR_IDENTIFIER_FILLS_A_SLOT_WORD; GRAPH_ROUTE_PHRASE_LOADS_ITS_NODE's
  And clause names the content word that still breaks a phrase; §2 and §6
  state the gap rule, the slot words, the identifier and the measurement (no
  class figure and no route of the measured rows moves); §10 gains two
  `pending` rows. ADR-0026's design (tier order, caps) is unchanged; plan
  `docs/plans/grill-8.1.2-tool-surfacing.md` §12 question 19 records the
  rule for the owner's veto. §3 and §9 are product's to follow. The status
  stays `back-written`.
