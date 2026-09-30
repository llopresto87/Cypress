<!-- Increment 3 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 3: This pass: ADR-0021, ADR-0022, the spec amendments and this plan
- Item: the decision records and contracts the tooling wave needs, and the round's plan of record (session ruling S2: a T3 round has one, `rule.grill`)
- Spec contracts: none: authoring. The contracts it writes are live from this pass and are named by the RED increments 14 to 16, which prove them
- Files touched: `docs/decisions/adr-0021-seed-only-procedures-stay-home.md`, `docs/decisions/adr-0022-the-plant-model-map.md`, `docs/decisions/index.md`, `docs/specs/SPEC-0001-install-placement.md`, `docs/specs/SPEC-0003-per-prompt-injection.md`, `docs/specs/SPEC-0005-cycle-economy.md`, `docs/plans/grill-7.35.0-positive-voice.md`, `docs/plans/grill-7.35.0-positive-voice/*.md`, `tests/run.sh` (the `ACTIVE_PLAN` line only)
- Tests to write (RED): none: records only; increments 14 to 18 write the tests
- Behavior added: none. The gate's plan step lints this plan instead of the 7.32.0 plan
- Gate: `python3 templates/knowledge-graph/grill-lint.py --plan docs/plans/grill-7.35.0-positive-voice.md --specs docs/specs --decisions docs/decisions` PASS; `spec-lint.py --specs docs/specs --root .` shape clean, its only findings the new contracts, uncovered until 14 to 16; `python3 tools/status-register.py --root docs/decisions --by-kind adr` lists both new ADRs `proposed`; `python3 tools/prose-lint.py --file <f>` on each file written, against its pre-edit copy
- Rollback path: revert the pass, and point `ACTIVE_PLAN` back at `docs/plans/grill-7.32.0-harvest.md`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: written in two architect passes. The second applied the session's rulings S1, S3 and S4 on the first pass's findings: `install.sh opencode --check` (OPENCODE_CHECK_DETECTS_DRIFT replaces a recorded gap), the four-alias `model:` set, and an unfilled map disclosed at graft instead of blocked on
