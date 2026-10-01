<!-- Increment 4 of `docs/plans/grill-7.37.0-routing-context.md`; its §9 index row points here. -->

### Increment 4: the kernel FIRST MOVE runs the router, only if a measurement favours it
- Item: owner ruling D2 and ADR-0027. Conditional: it lands only if the measurement below shows the new first move does not raise session tokens; otherwise this row is struck with the dated measurement and ADR-0027 is closed as rejected
- Spec contracts: SPEC-0003/PLAN_PRINTS_PLANT_BLOCK
- Files touched: `templates/knowledge-graph/graph-lint.py` and `integrations/claude-code/route-hook.py` (the `plant:` line, both renderers); `core/AGENTS.md` (FIRST MOVE, §5 line); `integrations/prime-agent/APPEND_SYSTEM.md` (line 8 points at the FIRST MOVE instead of `index.md`); `skills/context-router/SKILL.md` (route first); `templates/knowledge-graph/index.md` (the placeholder names itself the fallback map); `tests/test_graph_lint.py`
- Tests to write (RED): 1 case over SPEC-0003/PLAN_PRINTS_PLANT_BLOCK. The doctrine edits: none, they are declarative; proved by `python3 tests/seed-lint.py` (kernel budget at most 8,000 bytes, restatement check), `bash tests/test-full-install.sh` (the pre-growth pointer reached through the placeholder index), and `graph-lint.py --plan` on an ungrown fixture printing `no_signal` with `protocol.initialize` among its ids
- Behavior added: the `plant:` line in full plans; the FIRST MOVE text of ADR-0027
- Gate: the precondition first: a replay of the round's real short sessions after increment 3, scoring the first move as it is (route text plus the observed `index.md` reads) against the new one (route text, `--show` reads, the notice fallback); land only if the new one is not larger. Then `bash tests/run.sh`
- Precondition result (2026-10-01, replay over real short sessions in seven plants, cl100k-compatible count, route held at the new hook text in both arms): the new first move is not larger on either host. Prime Agent, 15 sessions: first-move window 25,359 -> 14,739 (-42%), whole session 56,662 -> 37,846 (-33%); Claude Code, 9 sessions: 56,189 -> 32,418 (-42%), one session larger by 56 tokens. It assumes the model stops opening `index.md`; the Prime Agent first-move break-even is 14.2% of sessions still reading it, against 33% (5 of 15) before. The increment proceeded and ADR-0027 records the result
- Rollback path: revert; kernel text, one skill section, one overlay line, one renderer line
- Effort: medium-low
- Phase: RED
- Depends on: increment 3
