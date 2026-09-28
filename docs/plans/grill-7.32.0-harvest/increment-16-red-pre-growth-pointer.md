<!-- Increment 16 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 16: RED: the pre-growth pointer sits in the placeholder index, not the kernel
- Item: 8a (class I and P), decision 8
- Spec contracts: SPEC-0001/PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX (promoted in this commit, with the §6 block delimiters and a §10 row)
- Files touched: `tests/test-full-install.sh` (new cases only), `docs/specs/SPEC-0001-install-placement.md` (the promotion, §6, §10 row)
- Tests to write (RED): a fresh `install.sh claude-code`: `docs/graph/index.md` holds one delimited pre-growth block naming `EXPERT_SEED_INSTALL_PROMPT.md` and `protocol.initialize`; `CLAUDE.md` names neither; a re-install over an index with no block leaves it byte-identical. Observed red: the block is absent and the kernel names both
- Behavior added: none (tests and the spec promotion)
- Gate: `bash tests/test-full-install.sh` red on the new cases only
- Rollback path: drop the cases and move the heading back
- Effort: low
- Phase: RED
- Depends on: increment 1
