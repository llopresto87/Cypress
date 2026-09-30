<!-- Increment 13 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 13: Prose: the cross-lane follow-up, one batch
- Item: every cross-lane text item the eight lanes and the release pass handed back, applied in one batch after all of them landed; it includes the S3 and S4 wording of the model map in `core/method/delegation-model-classes.md`, `templates/docs/models.md` and `protocols/graft.md`
- Spec contracts: none: prose, as increments 4 to 11
- Files touched: the method, protocol, skill, agent and template files the follow-up list names, a subset of the files of increments 4 to 12
- Scope: text only; every test, tool and installer item on the list belongs to the tooling wave (increments 14 to 23)
- Tests to write (RED): none: prose
- Behavior added: none
- Gate: `python3 tools/prose-lint.py --file` per file written; the router tests where a `description:` or `load_when` moved; `python3 tests/seed-lint.py` shows no new finding that names a file of this batch
- Rollback path: restore each file from its pre-edit copy, which the batch keeps outside the seed
- Effort: high
- Phase: prose
- Depends on: increment 4, increment 5, increment 6, increment 7, increment 8, increment 9, increment 10, increment 11, increment 12
