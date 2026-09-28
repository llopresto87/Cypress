<!-- Increment 3 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 3: RED: grill-lint reports a qualified decision reference as external
- Item: G1 (class B), decision 1
- Spec contracts: none: contained; no spec owns grill-lint's decision check. Why: a correct citation of another repository's decision fails, and a colliding bare number passes silently (ADR-0015)
- Files touched: `tests/test-grill-lint.sh` (new cases in the collecting block only), `tests/fixtures/grill/` (new files only)
- Tests to write (RED): (a) a plan citing `seed:ADR-0009` with no local ADR-0009 lints PASS and prints one line naming `seed:ADR-0009` as external and not checked; (b) the same reference twice prints one line; (c) guard: a bare `ADR-0009` with no local file is still the existing "not filed" finding; (d) guard: a bare `ADR-0001` with a local file still resolves. Observed red: (a) and (b), where the unmodified tool reads the qualified form as a bare number
- Behavior added: none (tests only)
- Gate: `bash tests/test-grill-lint.sh`: existing cases green, one `FAIL <label>` line per non-guard new case, exit 1
- Rollback path: drop the new cases
- Effort: medium-low
- Phase: RED
- Depends on: increment 1
