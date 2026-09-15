### Slice 7 — The routing metric measures routing (U-13, U-14)

**Tier:** T3. **Invariants:** X1, X2, X6.

`--eval` printed `top-1 accuracy 100.0% (55/55)` and gated at ≥90%. The number
was arithmetically true and rhetorically false: **46 of those 55 tasks were a
verbatim vocabulary subset of the agent they select**, and exactly one row shared
under half its vocabulary with its target. The corpus had been written from the
triggers it scores, so it measured mutual consistency under the name "accuracy".

**U-14's stated root cause was wrong, and re-verification is what caught it.**
The ledger said HIGH was awarded on near-ties, and prescribed widening the
margin. The observed confident-wrong was `"our chain of language-model calls
loops forever and burns money"` → **HIGH `security`, 22 vs 4 — a 5.5× margin**,
already far past `HIGH_RATIO = 1.5`. Widening it would have changed nothing.

The actual cause, isolated to a two-word reproduction (`--route "chain of calls"`
→ HIGH `security`, 18): `security` carries the trigger *"assess the supply-chain
and secrets handling risk"*, the tokenizer splits `supply-chain` on the hyphen,
and `chain` then scores as a free-standing concept. A second mechanism compounded
it: IDF gives a term matching only one agent `weight 3` for being rare, so two
incidental words amplified by rarity out-voted the whole task.

Both fixed at the mechanism:

1. A compound fragment matches at the near-match tier, never the standalone
   tier — **on both sides** of the comparison, since `language-model` was
   likewise offering `model` at full strength to `security`'s "threat model".
   `min()` of the two claims keeps the score scale unchanged, so `FLOOR` and
   `HIGH_RATIO` stay calibrated to the same numbers.
2. The rare-term bonus requires a full-strength name or trigger hit.
   Distinctiveness amplifies a confident match, not a graze.

**Measured, on the same 20 rows authored before any of this work:**

| | before | after |
|---|---|---|
| confident-correct | 4 | **3** |
| abstained (by design) | 15 | **17** |
| **CONFIDENT-AND-WRONG** | 1 | **0** |
| contract-class consistency | 55/55 | **54/55** |

**This is a trade, not a win, and the negative half is recorded here with the
positive half.** Eliminating the confident-wrong cost two confidently-correct
routes: one paraphrase row (`architect`) and — pointedly — the single contract
row that was *not* trigger-derived (`legal`, overlap 0.33). The one row in the
old corpus that actually measured generalization is the one the fix regressed.
It is left failing and visible at 54/55 rather than relabelled to restore a
round number.

The trade is taken because the classes are not equivalent in cost: an abstention
spends one reasoning step, while a confident wrong route reaches the orchestrator
with a band the kernel instructs briefs to cite *as evidence for that
specialist*. The gate now reflects that ordering — it gates on
confident-wrong = 0, not on top-1.

**Reporting, per X1.** Every number names the corpus it was computed over, the
classes are never averaged, and each class publishes the mean overlap it was
measured at — so the accuracy and the reason to distrust it arrive on the same
line:

```
contract        n=55 confident-correct=54 abstained=1  CONFIDENT-WRONG=0 mean-overlap-with-target=0.95
paraphrase      n=18 confident-correct=3  abstained=15 CONFIDENT-WRONG=0 mean-overlap-with-target=0.15
unknown-domain  n=5  confident-correct=5  abstained=0  CONFIDENT-WRONG=0 mean-overlap-with-target=0.00
```

**X2 is mechanical, not a promise.** A row labelled `paraphrase` whose overlap
with its target exceeds 0.80 fails the gate — so "authored without reading the
triggers" is checkable, and relabelling a trigger-derived row to inflate the
held-out number is refused by name. The paraphrase set also may not drop below
15 rows, closing the other route to the same dishonesty. Both were proved to
fire; the mislabel check initially printed its diagnostic and exited 0, which is
the very defect slice 4 fixed in three linters, found in new code by testing the
gate instead of trusting it.
