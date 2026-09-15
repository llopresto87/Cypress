# Evidence for the reach findings

Every number in the plan's §2 is reproduced here with the probe that produced it.
Where a slice later lands a permanent test, that test supersedes this page as the
authority and this page becomes the record of what was true on **2026-09-14** at
`d7588e2` + working tree.

Probes were run as throwaway scripts against the two routers' own functions
(imported, never reimplemented), so nothing here is a second implementation of
the scorer. Slice 3 turns the ones worth keeping into `tests/test_router_reach.py`.

---

## E1 — the fold against its own documented examples

`agent-lint.py:129` and `graph-lint.py:105` both read
`STEM = 6  # prefix length for the singular/plural fold (…)`, naming
`test/tests`, `node/nodes`, `order/orders`.

```
task term       agent token      _match   (2=direct, 1=fold, 0=miss)
  node          nodes               0
  nodes         node                0
  test          tests               0
  tests         test                0
  order         orders              0
  orders        order               0
  check         checked             0
  checked       check               0
  spec          specs               0
  claim         claims              0
  risk          risks               0
  audit         audits              0
  document      documented          1      <- works: both >= 6, shared prefix
  design        designing           1
  deliver       delivered           1
```

Three of the three examples the comments cite score 0.

## E2 — reach loss across both routers

```
THE FOLD ITS OWN COMMENT CLAIMS: singular roster word <- plural in the task
  roster singular tokens probed: 266
  MISS  (score 0 — the agent is simply unreachable):   85  32%
  fold  (score 1 — half strength):                    181  68%

  a task writing any of these plurals reaches NOTHING:
    adopts, adrs, agents, apis, asyncs, audits, brands, breaks, bugs, builds,
    chains, checks, claims, codes, cycles, diffs, drafts, evals, facts, fixes,
    fleets, flows, graphs, homes, hosts, loads, maps, merges, models, names,
    nodes, pages, picks, proofs, risks, roles, routes, …
```

```
KNOWLEDGE ROUTER (graph-lint.py, installed into EVERY plant) — STEM=6
  load_when triggers across seed machinery nodes: 251
  singular load_when tokens: 693
  unreachable by their own plural: 267  (39%)
```

The second table is the one that matters most: it is what a grown plant's
sessions use to decide which knowledge to load, and a third of its vocabulary
cannot be reached by a plural.

## E3 — tense changes the route

```
MEDIUM  pentest          16 | devils=12 | our penetration test report needs its citations checked
MEDIUM  devils-advocate  16 | devils=16 | our penetration test report needs its citations check
```

`devils-advocate`'s trigger is *"check this deliverable's citations against the
sources they name"*. `check` hits it for 8; `checked` hits it for 0.

## E4 — the scoring arithmetic behind all three recorded misroutes

```
"write a threat model for the new onboarding screen layout"          → ui-ux HIGH
  ui-ux-designer   screen=12 [w3·e4 TRIG]   layout=12 [w3·e4 TRIG]  = 24
  security         threat=8  [w2·e4 TRIG]   model=4   [w1·e4 TRIG]  = 12

"the delegation caps we agreed are written down nowhere in the graph" → m-a-a HIGH
  multi-agent-arch caps=12   [w3·e4 TRIG]   delegation=8 [w2·e4]    = 20
  docs-librarian   graph=4   [w1·e4 TRIG]                           =  4

"our penetration test report needs its citations checked"            → pentest MEDIUM
  pentest          penetration=12 [w3·e4]   test=4  [w1·e4]         = 16
  devils-advocate  citations=8    [w2·e4]   report=4 [w2·e2 desc]   = 12
```

Note `delegation caps`: `multi-agent-architect`'s fourth trigger is literally
*"review the orchestration framework and delegation caps"*. The row leans on a
verbatim trigger phrase, which is the adversarial class working as designed — but
it also means the expected answer (`docs-librarian`) is the weakest of the three,
since a steward could defensibly route that work to `multi-agent-architect` with
a documentation deliverable. Recorded so the row can be re-judged in S5 rather
than defended.

## E5 — charter holes

Derived probe (`>=5` uses in own body, `<=4` other charters, unreachable from
name+triggers+description):

```
  orchestrator           lane(12), contained(9), specify(6), covered(6), expertise(5), edit(5)
  architect              legal(7)
  security               scan(7), keys(6), prefix(5)
  reliability            release(6), procedure(6), local(5)
  product                smallest(5)
  ui-ux-designer         criteria(7)
  legal                  date(13), article(10), provision(8), instrument(6), designated(6)
  multi-agent-architect  shared(9), tree(5), plain(5), loop(5), deterministic(5), checklist(5)
  seed-installer         root(5)
  -> 27 unreachable charter words across 19 agents
```

The generic class the probe cannot see, found by hand instead:

```
== does the docs agent know the word 'document'?
  document        name=0 trigger=0 desc=0   _match(trig)=0
  documentation   name=0 trigger=0 desc=0   _match(trig)=0
  documented      name=0 trigger=0 desc=0   _match(trig)=0
  write           name=0 trigger=0 desc=0   _match(trig)=0
  written         name=0 trigger=0 desc=0   _match(trig)=0
  record          name=0 trigger=0 desc=0   _match(trig)=0
  graph           trigger=2   wiki  trigger=2   dedupe  trigger=2

== does the security agent know 'attack' / 'stride' / 'vulnerability'?
  attack          0      surface        0
  stride          0      vulnerability  0
  risk            trigger=2   threat  trigger=2
```

## E6 — two probes that came back clean, recorded so they are not re-run

```
PROBE: does each agent's OWN trigger route to it?
  -> 0/80 of the roster's own triggers misroute

PROBE: does each agent's OWN description route to it?
  -> 0/19 agents' descriptions misroute

PROBE: does each agent's own charter prose route to it?
  -> 1/19 — `pentest`'s charter routes to `legal` (its prose is about written
     authorization and scope, which is legal's vocabulary). Real, small, and
     folded into S4 rather than given its own slice.
```

The roster is not internally colliding. The defect is **reach**, not conflict —
which is why S1–S4 add vocabulary and normalisation and change no weight.

## E7 — the stemmer prototype, and why the corpus barely moves

Collision check over the roster's 363 `name`+`trigger` tokens: 347 distinct
stems, 16 collisions, **all 16 singular/plural pairs of the same word**:

```
   adapter <- adapter, adapters          citation <- citation, citations
   adopt   <- adopt, adopting            claim    <- claim, claims
   check   <- check, checks              duty     <- duties, duty
   fact    <- fact, facts                fail     <- failing, fails
   flow    <- flow, flows                module   <- module, modules
   obligation <- obligation, obligations right    <- right, rights
   repository <- repositories, repository source  <- source, sources
   specialist <- specialist, specialists  test    <- test, tests
```

Zero false merges. `analysis`/`analyses` is the one known miss.

Effect on the current golden corpus:

```
--- BEFORE
   contract        n=56  correct=55  abstained=1   WRONG=0
   paraphrase      n=17  correct=2   abstained=15  WRONG=0
   adversarial     n=12  correct=3   abstained=6   WRONG=3
   unknown-domain  n=5   correct=5   abstained=0   WRONG=0
--- AFTER (symmetric stemming)
   contract        n=56  correct=55  abstained=1   WRONG=0
   paraphrase      n=17  correct=3   abstained=14  WRONG=0
   adversarial     n=12  correct=4   abstained=5   WRONG=3
   unknown-domain  n=5   correct=5   abstained=0   WRONG=0
```

**Two rows.** A third of the vocabulary is restored and the score moves by two
rows, because every golden row is written in the same base forms the triggers
use. This is the single strongest argument for S5: the corpus shares the blind
spot it exists to measure.

## E8 — the hand sweep, and why it is not admissible as a measurement

26 rewordings of the three recorded misroutes: **17 confidently wrong, 7
correct, 2 abstentions**. The failures are confident rather than abstentions —
under rewording the router does not become uncertain, it becomes confidently
wrong somewhere else.

Two rows worth carrying:

```
WRONG  document the delegation caps we agreed          HIGH  multi-agent-architect  (docs-librarian scores 0)
abst   the retry limits … written nowhere in the graph LOW   —   (bait removed, still does not route)
```

The first is the most natural phrasing of documentation work, not a trick. The
second shows the bait is not the whole problem: with it removed the correct agent
still does not surface.

**Why it is not a measurement:** these 26 were written by the author after seeing
the failures, so they are selected for failure. They justify S5's rows; they do
not substitute for them. S5's rows must be authored to the corpus's own rule —
written without reading the triggers, then labelled.

---

## E9 — after the fix: what moved and what did not

Reproduced 2026-09-14, after slices 1–5.

```
  roster singular tokens unreachable by their own plural:      0  (was 85 / 32%)
  load_when singular tokens unreachable by their own plural:   0  (was 267 / 39%)
```

```
                          before        after
  contract              55/56         57/58
  paraphrase             2/17          4/17
  adversarial correct    3/12          5/12
  adversarial WRONG         3             2      <- ratcheted down
  unknown-domain          5/5           5/5
  charter vocab holes      27            12      <- ratcheted, enumerated
```

The one contract row that abstains changed identity rather than count: the
`legal` row *"which recorded external rules apply to this finding"* now routes,
and the `devils-advocate` row *"what should this document claim and does not"*
now abstains at 12 against a floor of 13. The cause is IDF working correctly —
`docs-librarian` gaining documentation vocabulary made `document` less
distinctive, dropping its weight from 2 to 1. Stated because an unchanged count
would otherwise hide a swap.

## E10 — two variants measured and rejected

Both would recover that contract row. Both cost an adversarial row, returning
the confident-wrong count to 3:

| variant | contract | adversarial WRONG |
|---|---|---|
| **A — as shipped** | 57/58 | **2** |
| B — drop the 6-char prefix fold entirely, stemmer only | 58/58 | 3 |
| C — count only full-strength hits toward document frequency | 58/58 | 3 |

Rejected on the rule the gate itself states: a confident wrong answer is cited
in a delegation brief as evidence for the wrong specialist, while an abstention
prints *"no clear specialist — name the gap before filling it"*. Trading an
abstention for a confident misroute is the wrong direction, and it would also
have meant ratcheting a limit back up in the same change that earned the right
to ratchet it down.

C is worth remembering independently: document frequency currently counts a
*graze* as evidence that a word is common, which is inconsistent with the
neighbouring rule that a graze may not earn the rare-term bonus. It is a real
inconsistency; it is simply not free to fix.

## E11 — the inflected corpus class that was built and thrown away

18 rows hand-derived from existing contract rows, one word inflected each:

```
  OLD       NEW        expected               task
  PASS      PASS       implementer            make the failing tests pass
  PASS      PASS       docs-librarian         author graph nodes for the auth subsystem
  PASS      PASS       devils-advocate        checking this deliverable's citations against the sources they name
  PASS      PASS       security               assessing the supply-chain and secrets handling risk
  ... 14 more, all PASS/PASS ...
  MEDIUM/gr PASS       growth-orchestrator    adopting this project into the docs graph by subsystem boundary
```

**17 of 18 passed before the fix.** An exhaustive search over every single-word
inflection of every contract row then found 22 rows whose verdict changes, of
which two are grammatical English:

```
  reviewer             check->checking   OLD=LOW/reviewer         checking the change is integrated and not bolted on
  growth-orchestrator  adopt->adopting   OLD=MEDIUM/growth-scout  adopting this project into the docs graph by subsystem boundary
```

The rest read like `make the failing test passes`, `which recordeding external
rules apply`, `datas`, `eaches`, `multis-agent`.

So the class was not shipped. The two real rows went in as ordinary contract
rows and the reasoning went into the corpus header. The cause is the useful
part: **the golden rows are vocabulary-rich**, so one inflection rarely moves
them, while the defect bites short natural phrasings — which the corpus does not
contain. Vocabulary is therefore measured directly and exhaustively by
`tests/test_router_reach.py` rather than sampled through sentences.

## E12 — what the fix costs, measured

Reducing both sides of every comparison is not free. 1 840 routes over the
golden corpus, same machine, same run:

```
  7.15.0 (one-sided prefix fold)                 1.84 s
  stemmer, no prefilter                          5.09 s   (2.8x)
  stemmer + three-character prefix prefilter     4.15 s   (2.3x)
```

~2.3 ms per route against ~1.0 ms. Recorded rather than hidden, because a
reader deciding whether to put this scorer somewhere hot should know. The
prefilter skips a token whose first three characters match none of the term's
stems' first three; that is sound only while every form `_stems(w)` returns
starts with `w[:3]`, which is asserted by `StemPrefixInvariant` over both
routers' real vocabulary **and** a constructed table covering every rule.

**That test earned its place immediately.** It failed on `added`, which the
undoubling rule reduced to `ad` — `planning` -> `plann` -> `plan` is right, but
`added` -> `add` is already right and undoubling it is not. Undoubling is now
guarded to bases longer than three letters, which fixes `ebbed`, `egged` and
`adding` at the same time. Without the prefilter the bug would have been a quiet
over-merge instead of a caught one: the optimisation is what made the invariant
worth asserting, and asserting it is what found the defect.

Not pursued: hoisting the per-token reduction out of `_match` into the bucket
build. It is the real fix for the remaining 2.3x, and it means restructuring
`score()` in two files that must stay in sync — more risk than a millisecond on
a keyword heuristic is worth. Named here so it is a decision and not an
oversight.
