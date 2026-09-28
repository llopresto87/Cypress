<!-- Increment 24 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 24: Prose: ADR-0002 states its invariant and points at the roster's one home
- Item: D3 (class S), decision 3
- Spec contracts: none: an append-only decision record
- Files touched: `docs/decisions/adr-0002-bounded-delegation-hybrid.md` (one dated amendment appended; nothing above it edited), `docs/decisions/index.md` (the 0002 row's status cell only)
- Tests to write (RED): none: prose
- Behavior added: the ADR names the invariant it owns (the six delegators and the depth cap) and points at `manifest.json` and agent frontmatter for the current roster, so its count cannot go stale again
- Gate: `python3 tests/seed-lint.py` PASS; `python3 tools/prose-lint.py --file` on the ADR with no new finding against a scratch-copy baseline
- Rollback path: revert the appended amendment
- Effort: low
- Phase: prose
- Depends on: increment 1
