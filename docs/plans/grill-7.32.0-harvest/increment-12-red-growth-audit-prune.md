<!-- Increment 12 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 12: RED: growth-audit skips nested plant copies and symlinked subtrees
- Item: C4 (class S), the growth-audit half
- Spec contracts: none: contained seed tool. Why: a symlinked seed checkout under a plant turned every corpus row DANGLING
- Files touched: `tests/test-growth-audit.sh` (new scenarios only)
- Tests to write (RED): (a) a plant holding a nested directory with its own `.cypress/seed.json` reports no row from inside it; (b) a symlinked subtree is not walked; (c) guard: an ordinary subdirectory is still walked. Observed red: (a) and (b)
- Behavior added: none (tests only)
- Gate: `bash tests/test-growth-audit.sh`: known scenarios green, the new non-guard scenarios red
- Rollback path: drop the scenarios
- Effort: medium-low
- Phase: RED
- Depends on: increment 1
