<!-- Increment 4 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 4: RED: the ledger verification tool proves a conversion byte for byte
- Item: D5 (class S), decision 5
- Spec contracts: none: contained seed tool; no spec owns it. Why: a plan converted to a ledger must be provably the same text, and the proof the graft wrote by hand counted characters and printed "bytes"
- Files touched: `tests/test-grill-lint.sh` (new cases in the collecting block only), `tests/fixtures/grill/` (new files only)
- Tests to write (RED): (a) `python3 tools/verify-ledger.py --monolith <m> --ledger <plan> --leaves <dir>` exits 0 and prints the byte count of the rebuilt file when the ledger and leaves rebuild <m> exactly; (b) one changed byte in a leaf exits 1 and names the leaf and the first differing byte offset; (c) a leaf no index row points at exits 1 and names it; (d) a multibyte character is counted as its UTF-8 bytes. Observed red: every case, because the tool does not exist
- Behavior added: none (tests only)
- Gate: `bash tests/test-grill-lint.sh`: existing cases green, one `FAIL <label>` per new case, exit 1
- Rollback path: drop the new cases
- Effort: medium-low
- Phase: RED
- Depends on: increment 1
