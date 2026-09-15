### Slice 9 — Metamorphic stability measured (U-42)

**Tier:** T2 (measurement, no behaviour change).

Route stability under meaning-preserving rewrites, over the 55 contract rows,
five transformations, 236 transformed tasks in total. Command recorded in the
session; re-runnable against `agent-lint.py --route`.

| Transformation | n | same top-1 | band kept | became WRONG | became abstain |
|---|---|---|---|---|---|
| clause reorder (`A and B` → `B and A`) | 16 | 16 | 16 | **0** | 0 |
| irrelevant background prepended | 55 | 55 | 53 | **0** | 0 |
| punctuation stripped, `?` appended | 55 | 55 | 55 | **0** | 0 |
| numbers added (`about 3 files, ~200 lines`) | 55 | 54 | 55 | **0** | 0 |
| politeness wrapper (`could you please …, thanks`) | 55 | 55 | 55 | **0** | 0 |

**Classification:** still-valid on all five. Nothing brittle: no transformation
turned a correct route into a confident wrong one. Two rows changed band under
irrelevant background and one changed top-1 under added numbers, neither
crossing into a confident error.

**The honest caveat, stated because the number looks better than it is.** This
is measured over the **contract** corpus, whose tasks share ~95% of their
vocabulary with the agent they select. A lexical router is *expected* to be
stable there: the transformations add or move words without removing the ones
carrying the signal. Running the same transformations over the paraphrase class
would mostly measure whether an abstention stays an abstention, which is stable
by construction and evidence of nothing. So this result says the router is not
*fragile* to surface form; it does not say it generalizes. U-13's paraphrase
numbers remain the measure of that.
