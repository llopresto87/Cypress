<!-- Increment 22 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 22: GREEN: graft-audit and growth-audit disclose an unfilled map
- Item: the audit change increment 17 fails on
- Spec contracts: none: contained, as increment 17
- Files touched: `tools/graft-audit.py`, `tools/growth-audit.py`
- Tests to write (RED): none: increment 17 holds them
- Behavior added: `--unfilled` prints an unfilled `models.md` on a disclosed line, outside the blocking count, and `--rename` and `--prune` leave it; `required_collections` skips `models.md`, the plant's configuration rather than a collection a scout gathers, and the audit reports it when unfilled. That also clears seed-lint's growth-intake finding for `models.md` with no change to its `unscouted` set
- Gate: `bash tests/test-graft-tools.sh`, `bash tests/test-growth-audit.sh` green; `python3 tests/seed-lint.py` no longer reports `growth-evidence-ledger.md: no section feeds 'models.md'`
- Rollback path: revert both tools
- Effort: medium
- Phase: GREEN
- Depends on: increment 17
