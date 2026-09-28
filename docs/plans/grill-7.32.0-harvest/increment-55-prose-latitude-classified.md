<!-- Increment 55 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 55: Prose: the session classifies the design latitude the way it classifies a tier
- Item: the owner's latitude rule of 2026-09-28 (class P)
- Spec contracts: none: protocol text. Why: the owner, verbatim: "the 3 values needs to be present and those postures/modes need to go akin to Tiers mode - need to be engaged based on request/tone/what we are trying to accomplish - or when in doubt asked to use at the beginning of the spec definition/request". Today `specify.design-latitude` asks the owner every time, in step 0
- Files touched: `protocols/specify-joint-pass.md` (the body of "Design latitude": the three values `creative`, `balanced` and `simple` stay as they are; the session classifies the latitude from the request, its tone and what the work is trying to accomplish, states it out loud with the reason, the way it states a tier, and asks the owner at the start of the spec definition only when in doubt; the answer is still a §6 row whose first cell begins `Design latitude:`, with the reason or the owner's quote as evidence; step 0 of the joint pass table reads as a classification, not an ask; the frontmatter's `description:` byte-identical), `core/method/tiers.md` (one pointer line in the body: the design latitude is classified the same way, at `specify.design-latitude`; the frontmatter unchanged)
- Tests to write (RED): none (prose)
- Behavior added: before a spec, every plant's session names the latitude with its reason, and asks the owner only when the request leaves it in doubt
- Gate: `python3 tests/seed-lint.py` gains no finding (stale pointers: `specify.design-latitude` resolves; body ceilings); `python3 tools/prose-lint.py --file` on both files, no new tell against a copy taken before the edit; `python3 integrations/claude-code/agent-lint.py --eval` unchanged; no always-loaded byte added: both `description:` fields byte-identical and the kernel untouched (R2)
- Rollback path: revert both files
- Effort: low
- Phase: prose
- Depends on: increment 1
