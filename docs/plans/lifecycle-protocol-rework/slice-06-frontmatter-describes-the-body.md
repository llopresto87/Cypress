# Slice 6 — the frontmatter describes the body

**Depends on:** slices 1, 3, 4, 5 (measure after the body settles, not before).

## The defect

The frontmatter of all three files has drifted away from what the files contain.
This matters mechanically, not cosmetically: `owns:` is how a fact is addressed,
`load_when:` is how the router selects the node **without reading it**, and
`est_tokens` is what a session budgets against.

### `owns:` no longer covers the body

| File | Declared facts | Lines belonging to none of them |
|---|---|---|
| `graft.md` | 3, unchanged in 13 commits, weighing ~50 / 50 / 570 | **~370** — the three migration sections, Phase 5, the output format, provenance |
| `harvest.md` | 3 | **202 — 31% of the body**: the five corpus sections |
| `grow.md` | 6 | ~85 — Boundaries, the shape, Phase 3, Phase 5 |

`harvest`'s is the worst: the five corpus withdraw contracts are the thing
`grow`, `graft`, `ingest-library` and `toolcraft` actually consume, and they are
**not addressable by the router as a fact**.

### `load_when:` does not cover every way in

- `graft`: four triggers, all variations on "upgrade this plant". Three of its
  sections — the shape migration, the status migration, "the audit reported
  UNRESOLVED" — have no trigger that routes to them.
- `grow`: `grow.legal-corpus` (7.11.0) and its jurisdiction half (7.12.0) added
  38 body lines and **no trigger**. Nothing in `load_when:` mentions law, corpus,
  jurisdiction or compliance, so *"decide whether this plant carries the legal
  corpus"* does not route here.

### `requires:` is empty and false

`graft.md` declares no requirements while its body depends on `protocol.grow`,
`grow.completeness-contract`, `grow.stack-inventory`, `grow.legal-corpus`,
`delegation.harness-registration`, `deliver.numbered-decisions`, and
`engineering-posture`. `graph-lint` validates that *declared* edges resolve — not
that real dependencies are declared. The protocol says exactly this about a
plant's graph at `:801-803` and does not apply it to itself.

### `est_tokens` drifted, and the honesty check is too loose to notice

| File | trajectory | now |
|---|---|---|
| `graft` | 9790 → 10000 → 10800 → 11616 → 12037 → **16037** | a +4000 jump for +60 lines, where prior increments tracked ~13 tokens/line |
| `grow` | frozen at **7726 since 7.5.0** while the body grew 689 → 743 | stale |
| `harvest` | 7000 → 7600 → 7950 → **8043** | accurate, within 2% |

The graft jump is the tell: the *earlier* values had drifted low and nobody
noticed, because `graph-lint.py` checks honesty **within 2×**. A 2× band cannot
detect a 60% understatement. This is U-16 — *"`est_tokens` honesty-checked within
2× … never bounded"*.

## The change

1. **`owns:` gains the facts the bodies actually hold.** `harvest.corpus-contracts`
   for the 202 lines; `graft.migration` for the three migration sections. Adding
   a fact is cheap and makes 31% of a file addressable; the alternative is
   pretending the largest block in the file is part of something else.
2. **`load_when:` gains a trigger per entry path**, including the ones that are
   not "upgrade this plant": the corpus decision, the status and shape
   migrations, and the audit verdicts a steward arrives holding.
3. **`requires:` — CORRECTED 2026-09-14, after the first pass got it wrong.**
   The rule stated here was *"every node a phase instructs the reader to open is
   a requirement"*, and it is wrong. `_schema.md:24-25` defines `requires:` as
   the closure an agent **must** load, followed **transitively**, ALWAYS. A
   protocol that points at another protocol at one phase, on one path, is a
   `peers:` relationship — *"subjects an agent must not load unless the task
   explicitly crosses into them"*.

   Applying the wrong rule cost, measured: `protocol.grow` 7 726 → **19 691**
   eager tokens (+155%), dragging in `protocol.toolcraft` transitively through
   canonize although grow names toolcraft once, as a parenthetical pointer.
   `protocol.initialize` — a 230-token thin adapter — went to **19 921** because
   it requires grow. `protocol.graft` reached **41 951**.

   That is the one cost ADR-0007 argued away. Its §Context rests on *"the router
   selects a node from the `load_when:` triggers … it never opens a body to
   decide whether it wants the body"* — true of routing, and **false of
   `requires:`**, which is the single edge where a session pays for material it
   may not use. A rework justified by that argument must not violate it.

   The correct rule: **declare a node in `requires:` only when no path through
   this protocol can complete without it**, and prefer `peers:` for anything
   reached on one branch, at one phase, or as a pointer. A close-out invoked in
   the final section is a peer, not a requirement — `graft` and `harvest` both
   close out and neither requires `canonize`.
4. **`est_tokens` recomputed after the body settles**, by the same measure
   `seed-lint.py` uses — never by estimate.
5. **The honesty band tightens from 2× to something that can detect drift.**
   This is a ratchet change and therefore an owner decision: the number lives in
   `graph-lint.py:729`, it would join `tests/ratchets.json`, and tightening it
   will make some nodes fail until their declarations are corrected. Recommend
   **1.25×**, applied to machinery nodes first.

## Documentation that is wrong today

`documentation/protocols-reference.md:37` and `:1641` list harvest's `owns:` as
two facts and its `est_tokens` as **7000** (real: 8043). `harvest.availability-gate`
— added in direct response to an incident, and which then failed — exists in
exactly two places in the whole tree, and the seed's own reference documentation
is not one of them.

`seed-lint` already checks roster/manifest/README consistency. It does not check
the protocol reference against protocol frontmatter. It should; this is the same
one-home-per-fact check, one table over.
