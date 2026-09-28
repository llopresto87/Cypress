<!-- Increment 51 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 51: Prose: the harvest's integrity gates G1 to G11
- Item: the round's gate (`protocol.harvest`)
- Spec contracts: none: gate evidence
- Files touched: none in the seed; the gate record is kept with the round's working records outside the seed
- Tests to write (RED): none: the gates of `protocols/harvest.md`, the independent faithful-import review (G3) by a second Opus reviewer who wrote none of the round, and the donor-plant check (G5) that the plant is byte-identical to its pre-harvest snapshot
- Behavior added: none
- Gate: every harvest gate passes, or its absence is recorded with the reason; nothing faked green
- Rollback path: none needed
- Effort: medium
- Phase: prose
- Depends on: increment 23, increment 24, increment 41, increment 42, increment 43, increment 44, increment 45, increment 46, increment 47, increment 48, increment 50, increment 54, increment 55
