### Increment 22 — Prose: section pointers and the Claude Code effort note
- Spec contracts: none — pointer repoints judged by review (SPEC-0005 §7 STALE_POINTER recovery)
- Files touched: `integrations/claude-code/README.md` (the engineering-posture pointer repointed; the effort host note: Claude Code reads `effort:`, source and date, per-spawn override not recorded, departures recorded in the brief and row 1 fails closed), `integrations/opencode/README.md`, `integrations/codex/README.md`, `protocols/harvest.md`, `tool-corpus/ops/session-cost-profiler.md` (engineering-posture section pointers repointed by id)
- Tests to write (RED): none — prose increment
- Behavior added: no shipped pointer names a moved section by its old file and number
- Gate: `python3 tests/seed-lint.py` (front-door checks over the integration READMEs); `grep -rn 'engineering-posture.md §[5-7]\|engineering-posture.md §1[34]' core agents protocols skills templates integrations` returns nothing
- Rollback path: revert
- Effort: medium-low
- Phase: prose
- Depends on: increment 11
