# The routers can be reached by the words people actually type

**Status:** slices 1-4 implemented and gated; slice 5 closed with a NEGATIVE
result recorded rather than a class shipped; slice 6 recorded. The adversarial
confident-wrong budget fell from 3 to 2 as a consequence, which answered the
open Decision B of `grill-7.15.0-remediation/HANDOFF.md` §4 by measurement
rather than by the owner accepting a judgement — **and it was returned to 3 on
2026-09-15**, because review found the fall had been bought by a defect: `down`
was missing from `STOPWORDS`, and a 2×2 ablation attributed the fall to the
roster additions rather than to this plan's scorer repair. The current value is
`python3 tools/ratchet-lint.py --show`, and the reasoning is at the constant in
`integrations/claude-code/agent-lint.py`; neither is restated here.
**Baseline commit:** `d7588e2` (7.15.0), working tree at 7.16.0.
**Origin:** owner question on the three `adversarial` misroutes recorded in
`grill-7.15.0-remediation/HANDOFF.md` §4 Decision B — *"why is the wrong pick
being shown? have you tried differently worded but similar prompts?"* The answer
to the second question is what produced this plan: nobody had, and the corpus
cannot, because every golden row is written in the same base word forms the
triggers use.

This file is the authoritative ledger. Each slice is a child file under
`router-lexical-reach/`; §8 indexes them and `seed-lint.py`'s
`check_plan_ledgers` enforces the bijection.

---

## §1 Scope, and why it is bigger than the agent router

Two routers share one scorer by copy:

| Router | File | Installed to | Decides |
|---|---|---|---|
| specialist router | `integrations/claude-code/agent-lint.py` | `docs/graph/agent-lint.py` + `.claude/agent-lint.py` | which agent does the work |
| knowledge router | `templates/knowledge-graph/graph-lint.py` | `docs/graph/graph-lint.py` | which nodes a session loads |

`STEM = 6`, `_match()`, `_terms()` and `_tokens()` are duplicated between them —
already recorded as the genuine half of U-32. **Every defect below is present in
both**, which means every one of them ships into every grown plant and decides
what a plant's sessions read, not merely what this repository routes.

## §2 Findings

### F1 — the morphological fold is dead for every word shorter than six characters

```python
STEM = 6  # prefix length for the singular/plural fold (test/tests, node/nodes)
...
if len(term) >= STEM and any(k.startswith(term[:STEM]) for k in toks):
    return 1
```

The test is one-sided: the *task's* term must be at least six characters, and
its first six must **prefix** a roster token. For a plural to fold onto its
singular, the plural must prefix the singular — which it never does, because it
is longer. Both copies of the comment name examples the code cannot handle:

| term | roster token | `_match` | expected |
|---|---|---|---|
| `nodes` | `node` | **0** | the fold, per the comment |
| `node` | `nodes` | **0** | the fold, per the comment |
| `tests` | `test` | **0** | the fold, per the comment |
| `orders` | `order` | **0** | the fold, per the comment |
| `checked` | `check` | **0** | — |
| `documented` | `documentation` | 1 | works: both ≥ 6, shared prefix |

The fold works only where **both** words are at least six characters and share a
six-character prefix. That is the minority of English work vocabulary and almost
none of this roster's.

**Measured reach loss** (`tests/test_router_reach.py` derives these; do not
trust the copy here):

| Vocabulary | singular tokens | unreachable by their own plural | remainder, at half strength |
|---|---|---|---|
| agent roster `name` + `routing_triggers` | 266 | **85 (32%)** | 181 (68%) |
| seed machinery `load_when:` | 693 | **267 (39%)** | 426 (61%) |

A task writing `agents`, `nodes`, `specs`, `risks`, `claims`, `facts`, `graphs`,
`models`, `routes`, `flows`, `pages`, `checks` or `audits` scores **zero** on the
token the roster actually holds.

### F2 — the half-strength fold is strong enough to change the answer

Identical task, one word's tense:

```
"our penetration test report needs its citations checked"  → pentest 16,  devils 12   WRONG
"our penetration test report needs its citations check"    → devils 16,  pentest 16   right
```

`checked` scores 0 against `devils-advocate`'s trigger word `check`; `check`
scores 2. Four points, and the route changes. A route that turns on tense is not
a route, and this is the mechanism behind one of the three recorded misroutes —
which means that row was measuring English morphology, not router judgement.

### F3 — charters that cannot be reached by their own subject

Derived (`>= 5` uses in an agent's own body, `<= 4` other charters using it,
absent from that agent's `name` + `routing_triggers` + `description`): **27
unreachable charter words across 19 agents**, e.g. `orchestrator`/`lane`,
`legal`/`provision`, `security`/`scan`, `multi-agent-architect`/`deterministic`.

**The bound on that probe, recorded because it matters:** it finds only
*distinctive* holes. It cannot find a hole where the missing word is common
across charters but is nonetheless the agent's defining term, and that is the
worse class:

| Agent | Absent from name, triggers **and** description |
|---|---|
| `docs-librarian` | `document`, `documentation`, `documented`, `write`, `written`, `record` |
| `security` | `attack`, `surface`, `vulnerability`, `stride` |

`docs-librarian` holds `graph`, `wiki`, `dedupe`, `node`. The documentation agent
is not reachable by the word documentation. `security` holds `threat` and `risk`
only; `vulnerability` belongs to `pentest`, so *"assess our vulnerabilities"* —
design-time work — routes to the hands-on exploit agent. These were found by
rewording tasks by hand, which is the only instrument that finds them, which is
F5.

### F4 — IDF scores what a task is about, never what it asks for

Not a bug; a consequence of the design, recorded here because it bounds what
F1–F3 can fix. Weight is rarity: a term matching one agent scores 3, one
matching many scores 1. In this roster the rare terms are **domain nouns** and
the common terms are **work verbs**:

```
"write a threat model for the new onboarding screen layout"
  ui-ux-designer   screen=12 [w3]  layout=12 [w3]   = 24   ← the setting
  security         threat=8  [w2]  model=4   [w1]   = 12   ← the job
```

A bait row is by construction a task whose nouns belong to agent X and whose verb
belongs to agent Y, so a purely lexical IDF scorer must lose it. All three
recorded adversarial failures have exactly this shape. **This plan does not
propose to fix F4** — see §6.

### F5 — the corpus cannot see F1, and has no cell for the failure it does see

Applying a symmetric stemmer (prototype, §4 S1) to the current corpus moves
**two rows**: `paraphrase` 2→3 confident-correct, `adversarial` 3→4, with no
change to `contract` or `unknown-domain` and no change to the confident-wrong
count. A third of the vocabulary is restored and the score barely moves, because
**every golden row is written in the same base forms as the triggers**. The
corpus shares the defect it is supposed to measure.

Separately, the four classes leave one cell empty:

| | base wording | reworded |
|---|---|---|
| **not baited** | `contract` (n=56) | `paraphrase` (n=17) |
| **baited** | `adversarial` (n=12) | **— nothing —** |

A hand sweep of 26 rewordings of the three recorded misroutes produced **17
confidently wrong, 7 correct, 2 abstentions** — and the failures were confident,
not abstentions: the router does not become uncertain under rewording, it becomes
confidently wrong somewhere else. Those 26 were written by the author *after*
seeing the failures and are not admissible as a measurement; they are the reason
the empty cell gets filled by rows written to the corpus's own authoring rule.

## §3 What is being claimed, and what is not

- **Claimed:** F1 and F2 are defects with a mechanical fix and a regression that
  can be observed red. F3 is a defect in the roster's data, not its code.
- **Not claimed:** that fixing them improves the recorded eval much. §2 F5 says
  it improves it by two rows. The value is reach, and reach is not what the
  present corpus measures — which is why S5 exists and why the honest order is
  *fix the instrument, then re-measure, then let the budgets fall where they land*.
- **Not claimed:** that any number in §2 should be trusted from this page. Each
  is derived by a test added in the slice that cites it.

## §4 Slices

| # | Slice | Touches | Red first |
|---|---|---|---|
| 1 | Symmetric stemming in the specialist router | `agent-lint.py` | `nodes`→`node` scores 0 |
| 2 | The same fix in the knowledge router, and a drift gate | `graph-lint.py`, `seed-lint.py` | the two `_match` bodies differ silently |
| 3 | A stem-collision gate | `tests/test_router_reach.py` | two unrelated roster words merge |
| 4 | Close the charter holes | `agents/*.md`, `seed-lint.py` | `document` reaches nothing |
| 5 | The empty corpus cell, and re-measurement | `_routes.golden.tsv`, `ratchets.json` | no baited-reworded row exists |
| 6 | Record F4 and its measurement; implement nothing | this plan, ADR | — |

### S1 — symmetric stemming, specialist router

Replace the one-sided prefix probe with a deterministic suffix stemmer applied
to **both** sides, so comparison is stem-to-stem and an inflection scores at the
strength of the word it inflects rather than half.

```
exact token hit            → 2   (unchanged)
same stem                  → the token's own strength (2 for name/trigger)
six-char prefix fold       → 1   (kept as the long-word fallback)
none                       → 0
```

Suffix order, each with a minimum length, plus a `KEEP` set for words whose
final `s` is not a plural (`analysis`, `status`, `process`, `class`, `bias`,
`https`, `devops`, …):

```
ies→y | sses→ss | ches/shes/xes→ch/sh/x | ing→∅ (undouble) | ed→∅ | es→∅ | s→∅
```

Prototype result on the roster's 363 `name`+`trigger` tokens: 347 distinct stems,
**16 stems collapsing more than one token, all 16 of them singular/plural pairs
of the same word** (`fact`/`facts`, `claim`/`claims`, `duty`/`duties`,
`repository`/`repositories`, …) and zero false merges. `analysis`/`analyses` is a
known miss, handled by `KEEP` plus an `-es`-on-`-is` rule or accepted and
recorded.

**Red first:** a test asserting `_match("nodes", {"node"}) == 2` and the whole
table in F1 — the fold's own documented examples — before any edit.

### S2 — the same fix in the knowledge router, and a gate against re-drift

`graph-lint.py` gets the identical stemmer. Because it is a copy and copies
drift — this defect is *itself* a drift artifact, the compound-fragment fix
having reached only one of the two — the slice also adds a `seed-lint` check that
the two implementations of `_match`/`_terms`/`_tokens`/`STEM`/`_stem` are
byte-identical after normalising the docstring, in the same shape as the existing
canonical-block byte-identity check for the brief templates.

**Red first:** perturb one copy by a character; the check must fail. This gate
also retires half of U-32 with a mechanism instead of a note.

**Consequence to state in the CHANGELOG, not bury:** this changes node routing
for every already-grown plant. That is the same consequence that made the
compound-fragment fix wait on U-36, and it is why it is a separate slice with its
own entry rather than a quiet ride-along on S1.

### S3 — a stem-collision gate

The risk a stemmer introduces is a *false* merge — two unrelated roster words
reduced to one stem, silently widening an agent's reach. S3 adds
`tests/test_router_reach.py`, which derives from the roster on every run:

1. every stem collision, asserted against a reviewed allowlist of inflection
   pairs, so a **new** collision fails rather than passes quietly;
2. the F1 reach table (32% / 39%), asserted to be **0%** afterwards and ratcheted
   so it cannot climb;
3. the F2 tense pair, asserted to route identically.

This is the slice that makes §2's numbers derived rather than asserted, per §3.

### S4 — close the charter holes

Add the missing vocabulary to the frontmatter of the named agents, and add a
`seed-lint` check that keeps holes from coming back: a word an agent uses at
least five times in its own body, used by no more than four other charters, must
be reachable through that agent's `name`, `routing_triggers` or `description`.

That check enforces the *derivable* class only. The generic class (F3's second
table) cannot be derived, so it is closed by hand here and held by the corpus
rows added in S5 — the honest division, stated rather than blurred.

**Not to be done:** adding a trigger whose only purpose is to satisfy a golden
row. The test for whether a word belongs is whether the agent's own charter uses
it, which is what the check measures.

### S5 — fill the empty cell and re-measure — **CLOSED WITH A NEGATIVE RESULT**

**What was planned:** an `inflected` class, plus a `baited-paraphrase` class.

**What happened.** 18 inflected rows were hand-derived from existing contract
rows. **All 18 passed before the fix as well as after.** An exhaustive search
over every single-word inflection of every contract row found 22 rows that
change the verdict, of which exactly **2 are grammatical English**. A class of
18 rows where 16 pass either way is coverage to look at, not evidence — the
shape of false green this repository has a taxonomy for — so the class was not
shipped. The two real rows were added as ordinary contract rows, and the reason
is written into the corpus header where the next author will meet it.

The cause is worth keeping: **the corpus's rows are vocabulary-rich**, so one
inflection rarely moves them. The defect bites short, natural phrasings, which
is precisely what the corpus does not contain. Vocabulary is therefore measured
directly and exhaustively by `tests/test_router_reach.py` — 0% of either
router's vocabulary unreachable by its own plural, ratcheted — rather than
sampled through sentences. A sentence samples; that test enumerates.

The **baited-and-reworded** cell is still empty, and stays empty rather than
being faked: filling it honestly needs an author who has not read the triggers,
and the 7.16.0 author had read all of them. Carried as open work, named in the
corpus header.

### S5 as planned (retained for the record)

1. Add an `inflected` set: existing contract rows restated in plural/past/gerund
   form. These fail today and pass after S1 — the regression that shows S1 is
   worth its code, which the present corpus cannot show.
2. Add a `baited-paraphrase` class: each adversarial row reworded by the corpus's
   own authoring rule (written without reading the triggers, then labelled),
   filling the cell in F5's table.
3. Re-run `--eval`. **Record what it measures, do not tune to it.**

**How the budgets move, stated in advance so the move is not mistaken for a
waiver.** A new class gets a **new** recorded baseline; that is a measurement,
not a loosening, and `ratchet-lint` should carry it as its own key with its own
`--bless`. The existing `ADVERSARIAL_CONFIDENT_WRONG_BUDGET` must **not** be
raised to absorb new rows — if the reworded rows fail, they fail in their own
class where the number is visible. If the existing 3 falls on its own after S1
and S4, ratchet it down and Decision B answers itself without the owner having to
accept anything.

### S6 — record F4; implement nothing

F4 is an architectural limit of lexical IDF routing, and the candidate
remedies — a separate `work_verbs:` scoring channel, a per-term contribution cap,
a stricter `HIGH_RATIO` that converts confident-wrong into abstention — are each
larger than this plan and each need the S5 corpus to be judged against. This
slice writes F4 and its measurement into the record and stops. It is also the
honest input to **Decision D**: the case for a semantic layer should be argued
against a router whose lexical reach has been repaired, not against one that
cannot match `nodes` to `node`.

## §5 Gates

Every slice lands with a red observed first. `bash tests/run.sh` green at the
end of each. `python3 tools/ratchet-lint.py --show` after S5, with any movement
named in the CHANGELOG entry and, where a limit rises, put to the owner.

## §6 What this plan deliberately does not do

- It does not tune any weight, floor or band to improve a corpus score. S1–S4
  change what the scorer can *see*; none of them change what it *prefers*.
- It does not fix F4.
- It does not touch `docs/graph/` routing for grown plants beyond S2's stated
  consequence, and S2 says so where a reader will meet it.

## §7 Evidence

`router-lexical-reach/evidence-reach.md` holds the probe transcripts behind
every number in §2, and names the scratch scripts they came from so a reader can
re-derive rather than believe.

## §8 What actually landed

| # | Slice | State | Where |
|---|---|---|---|
| 1 | Symmetric stemming, specialist router | done | canonical block in `agent-lint.py` |
| 2 | Same in the knowledge router + drift gate | done | `graph-lint.py`; `seed-lint.check_canonical_router_blocks` |
| 3 | Stem-collision gate | done | `tests/test_router_reach.py`, `tests/fixtures/router/stem-collisions.json` |
| 4 | Close the charter holes | done, 27 -> 12 | 7 agents; `seed-lint.check_charter_vocabulary`, `CHARTER_VOCAB_DEBT` |
| 5 | The empty corpus cell | **negative result recorded** | `agents/_routes.golden.tsv` header |
| 6 | Record F4, implement nothing | done | §2 F4 above |

### Measured effect

| | before | after |
|---|---|---|
| roster vocabulary unreachable by its own plural | 32% | **0%** |
| `load_when` vocabulary unreachable by its own plural | 39% | **0%** |
| contract | 55/56 | 57/58 |
| paraphrase confident-correct | 2/17 | **4/17** |
| adversarial confident-correct | 3/12 | **5/12** |
| adversarial CONFIDENT-WRONG | 3 | **2** (budget ratcheted down) |
| charter words no task can route on | 27 | **12**, ratcheted |

### Five things found while fixing, that were not in the plan

1. **Pronouns were scoreable routing vocabulary.** `we` was already written into
   three shipped triggers, so every task saying "we need X" paid three agents a
   weight-2 match. A fourth trigger writing `our` earned the *rare-term* bonus
   and routed "our chain of language-model calls loops forever" HIGH to
   `security` on the strength of the word "our". Fixed by a canonical stopword
   block, now byte-identical across both routers and gated.
2. **A trigger grounded in its charter can still be wrong.** `scan` and
   `signing keys` are both squarely in `security`'s charter, and both cost an
   adversarial row the moment they were added — a deploy pipeline's scan step
   is `reliability`'s, and "signing keys" reached "signed documentation". They
   were withdrawn and are recorded as debt **with the measurement**, not with an
   opinion. Charter-grounding is necessary and not sufficient; the corpus is the
   check.
3. **Stale bytecode served a suite that was measuring code not in the file.**
   Editing `("ing", 3, 6)` to `("ing", 3, 7)` changes neither mtime-relevant
   size nor length, so the `.pyc` validated. `test_router_reach.py` now compiles
   the routers from source text, as `ratchet-lint.py` already did for the same
   reason.
4. **The undoubling rule reduced `added` to `ad`.** Found by the invariant test
   written to justify a performance prefilter, not by any routing test — the
   optimisation is what made the invariant worth asserting, and asserting it is
   what found the defect. Cost is recorded: routing is **2.3x slower** than
   7.15.0 (~2.3 ms vs ~1.0 ms per route), measured in E12, with the further fix
   named and deliberately not taken.
5. **`documentation/agents-reference.md` mirrors two things and gated neither.**
   Its per-agent "Golden routing tasks" heading claims *every row expecting this
   agent* and listed only the original contract rows — 3 of `architect`'s 5, 2
   of `legal`'s 7. A partial list presented as complete, in the file that
   documents the roster. Both halves are now regenerated from their homes, each
   row carries its class, and `seed-lint.check_agents_reference` holds them.

## §9 Slice records

| # | Slice | Record |
|---|---|---|
| — | Evidence for §2 | `router-lexical-reach/evidence-reach.md` |
