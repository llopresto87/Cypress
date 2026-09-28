<!-- Increment 1 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 1: This pass: the plan as a ledger, the pending spec amendments, ADR-0015 to ADR-0020
- Item: G3 (class B), part one; the spec and decision records of every item below
- Spec contracts: none: authoring. The contracts this round adds are written as a pending block in SPEC-0001 §4 and SPEC-0003 §4, and the RED increments below promote them
- Files touched: `docs/plans/grill-7.32.0-harvest.md`, `docs/plans/grill-7.32.0-harvest/increment-*.md` (53 files), `docs/specs/SPEC-0001-install-placement.md` (the pending block of §4, §0 Related ADRs, one §12 entry), `docs/specs/SPEC-0003-per-prompt-injection.md` (the pending block of §4, one §12 entry), `docs/decisions/adr-0015-cross-repository-decision-references.md`, `docs/decisions/adr-0016-stamp-carries-keys-it-does-not-own.md`, `docs/decisions/adr-0017-pre-growth-pointers-leave-the-kernel.md`, `docs/decisions/adr-0018-code-fact-freshness-anchor.md`, `docs/decisions/adr-0019-no-opus-version-table-in-the-seed.md`, `docs/decisions/adr-0020-a-plans-ledger-lives-beside-it.md`, `docs/decisions/index.md` (six rows)
- Tests to write (RED): none: records only. The pending headings are chosen so that `spec-lint.py` counts none of them
- Behavior added: none; the round has a plan of record, a spec text for every contract it adds, and a decision record for each decision with consequences
- Gate: `python3 tests/seed-lint.py` PASS; `python3 templates/knowledge-graph/spec-lint.py --specs docs/specs --root . --uncovered-budget 2` unchanged at 2/128 live contracts uncovered; `python3 tools/prose-lint.py --file <f>` on every file written; grill-lint over this plan through a staged layout (§10), whose only findings are the pending-contract references
- Rollback path: revert the pass; nothing else depends on it until increment 2 starts
- Effort: hard
- Phase: prose
- Depends on: none
