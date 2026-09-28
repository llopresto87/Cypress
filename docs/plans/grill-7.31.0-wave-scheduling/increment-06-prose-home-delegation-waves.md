### Increment 6 — Prose: the home of `delegation.waves`
- Spec contracts: SPEC-0005/ADOPTED_RULE_HOMES (increment 2's entry turns green); the rule's text is doctrine accepted by review (SPEC-0005 AC-14 as product amends it, and product's readiness-and-carry criterion)
- Files touched: `core/method/delegation-sequencing.md`: a new `##` section after "Lanes", headed "Waves: RED ahead of GREEN" with the key `delegation.waves` in the heading, stating every row of SPEC-0005 §6 "Waves" and naming `grill-lint.py --waves` as where the session reads the schedule; frontmatter: `owns` gains `delegation.waves`, `title` gains "waves", one new `load_when` entry on RED waves ahead of GREEN (the representative phrase stays verbatim), `est_tokens` re-measured. (S3:) In the "Lanes" section (`delegation.lanes`), one short paragraph states §6 row S3: on a shared tree a worker runs no command that moves other writers' uncommitted files (`git stash`, `checkout`, `restore`, `reset`); for a baseline it copies the file or reads `git show HEAD:<path>`; the orchestrator commits each lane by pathspec. No `owns:` change for it
- Tests to write (RED): none new; increment 2's entry (the S3 paragraph is doctrine accepted by review)
- Behavior added: the rule has its one home
- Gate: `python3 tests/seed-lint.py` with no `delegation.waves` finding (plus the leaf ceiling and prevents overlap); `python3 -m unittest tests.test_router_reach tests.test_graph_lint` (the delegation routing cases; a stem collision is a question, not a fixture edit); `python3 tools/prose-lint.py --file core/method/delegation-sequencing.md`; the RED hash re-check before the commit
- Rollback path: revert with increment 2's entry
- Effort: medium
- Phase: prose
- Depends on: increment 2
