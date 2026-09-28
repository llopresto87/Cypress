<!-- Increment 21 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 21: Prose: the three growth roles say only what they are for
- Item: 8b (class P), decision 8
- Spec contracts: none: agent descriptions accepted by review and held by the existing `agent-lint.py --eval` step
- Files touched: `agents/growth-orchestrator.md`, `agents/growth-scout.md`, `agents/seed-installer.md` (the `description:` line of each, and nothing else)
- Tests to write (RED): none new: the gate is the existing routing evaluation
- Behavior added: each description says what the role is for and that it runs inside grow, graft or adopt; always-loaded bytes fall
- Gate: `python3 integrations/claude-code/agent-lint.py --eval --dir agents`: confident-wrong does not rise and the paraphrase floor holds (compare with the baseline run on the unchanged tree); `--lint` PASS. The published eager figures in `README.md` and `documentation/host-capability-matrix.md` go stale here and stay expected-red at each tip until increment 52 (§12 question 4)
- Rollback path: revert the three lines
- Effort: medium-low
- Phase: prose
- Depends on: increment 19
