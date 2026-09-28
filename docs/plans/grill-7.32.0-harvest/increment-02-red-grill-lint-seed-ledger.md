<!-- Increment 2 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 2: RED: grill-lint reads a seed-side ledger plan
- Item: G3 (class B), the linter half
- Spec contracts: none: contained, and no spec owns the plan and spec homes of `grill-lint.py` (SPEC-0005 contracts only its `--waves` report). Why: the seed cannot lint its own plans, so the owner's ledger rule is unenforced where the seed plans itself (ADR-0020)
- Files touched: `tests/test-grill-lint.sh` (new cases in the collecting block only), `tests/fixtures/grill/` (a new seed-shaped fixture: a plan file, the directory named for its stem, a specs directory and a decisions directory; new files only)
- Tests to write (RED): (a) a plan `docs/plans/round.md` with its ledger in `docs/plans/round/` and rows reading `docs/plans/round/increment-01-a.md` lints PASS with `--plan docs/plans/round.md --specs <specs> --decisions <decisions>`; (b) a file in `docs/plans/round/` no row indexes is an orphan finding; (c) a row pointing outside `docs/plans/round/` is refused; (d) a contract declared only in the `--specs` directory resolves, and one declared nowhere is the "invents a contract" finding; (e) an ADR filed only in the `--decisions` directory resolves; (f) guard: the existing plant layout (`plans/grill.md`, `plans/grill/`) still lints exactly as before. Observed red: (a) to (e) fail on the unmodified tool, which reads only `plans/grill/` and resolves specs and decisions beside itself
- Behavior added: none (tests only)
- Gate: `bash tests/test-grill-lint.sh`: every existing case green, then one `FAIL <label>` line per non-guard new case and exit 1; the guard passes
- Rollback path: drop the new cases and fixture files
- Effort: medium
- Phase: RED
- Depends on: increment 1
