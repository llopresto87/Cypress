<!-- Increment 15 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 15: RED: agent-lint holds model: to the four aliases
- Item: ADR-0022 and session ruling S3: the `model:` token is one of `opus`, `sonnet`, `haiku`, `inherit`, for plant agents as well
- Spec contracts: SPEC-0005/AGENT_DECLARES_MODEL_CLASS (with its failure AGENT_MODEL_OUTSIDE_SET_AFTER_GRAFT)
- Files touched: `tests/test_agent_lint.py` (a `LintModelClassTests` class; the `agent_md` helper omits `model:` when given `model=None`, as it does for `effort`)
- Tests to write (RED): `test_lint_accepts_each_model_class_token` a guard: one agent per alias, one of them `origin: project`, exit 0; `test_lint_fails_on_missing_model`; `test_lint_fails_on_model_outside_the_set` with a full id `provider-a/model-x`; `test_lint_fails_on_plant_agent_with_model_outside_the_set` with `origin: project` and a full id. Observed red: the three refusals exit 0 on the unmodified agent-lint
- Behavior added: none (tests only)
- Gate: `python3 -m unittest tests.test_agent_lint` from the seed root: three named failures, the guard and every existing case green
- Rollback path: drop the new class and the helper change
- Effort: low
- Phase: RED
- Depends on: increment 3
