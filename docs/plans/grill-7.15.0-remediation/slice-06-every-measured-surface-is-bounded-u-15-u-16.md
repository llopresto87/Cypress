### Slice 6 — Every measured surface is bounded (U-15, U-16)

**Tier:** T3. **Invariants:** X4, X5.

`est_tokens` was checked for *honesty* (within 2× of the measured body) and never
for a ceiling, so machinery could grow without limit provided it declared the
growth accurately. An honest number is not a budget. `graph-lint.py`'s 170-line
ceiling exempts machinery explicitly, so it bound none of the nodes that had
actually grown large.

Two budgets now exist in `tests/seed-lint.py`, and both were proved to bind:

| Budget | Value | Proof it can fail |
|---|---|---|
| `MACHINERY_BODY_CEILING` | 1 000 lines | set to 900 → `protocols/graft.md` (931) fails |
| `EAGER_BUDGET` | 32 000 bytes per harness | set to 20 000 → 4 harnesses fail |
| `EAGER_EXEMPTIONS` ratchet | copilot at 121 543 | lowered one byte → fails |

**The finding this produced, which was not in the ledger.** Measuring the eager
surface per harness rather than in aggregate showed **github-copilot pays
121 543 bytes (~30 400 tokens) before any routing happens — sixteen times the
kernel.** All fourteen skill projections carry `applyTo: '**'`, so every skill
*body* is always-applied context there, where every other harness reads only the
descriptions. The seed budgets its kernel at 8 000 bytes on the grounds that
"every session of every plant pays this file", while shipping 114 KB of
always-on skill bodies to one harness unmeasured.

It is recorded as an **enumerated, dated exemption with zero slack** rather than
waived by raising the budget — the idiom `legal-lint.py` already uses for edition
debt. The number may shrink, never grow. Narrowing the projection to a pointer
(which is what progressive discovery would do, and the bodies already live in
`docs/graph/skills/` where a session can read them on demand) changes what an
installed plant receives, so it is **owner decision 1** in §4 rather than a
change made here.

Restated in README: the `<500`-line claim is replaced by the measured
distribution (median 171, largest 932, ceiling 1 000, three nodes over 500) and
the eager table is published beside the kernel size.
