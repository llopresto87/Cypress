### Increment 30 — Prose: skill and corpus pointer repairs (ruling pass 3)
- Spec contracts: none — pointer repairs judged by review
- Files touched: `skills/toolcraft/SKILL.md` (:151, the home of `toolcraft.bounded-execution` is `method.bounded-execution`), `skills/context-router/SKILL.md` (:263, the retrieval posture is `method.decision-economy` §6), `skill-corpus/drive-hosted-cicd-cli.md` (:12, :138, :224) and `library-corpus/platform/azure-devops-rest.md` (:82) (each `core/method/engineering-posture.md` cite for `toolcraft.bounded-execution` names `core/method/bounded-execution.md`)
- Tests to write (RED): none — prose increment
- Behavior added: the toolcraft sentence states the right home; no skill or corpus page cites the old file for a moved fact
- Gate: `python3 tests/seed-lint.py`; `bash tests/test-skill-corpus.sh` or the corpus test the tree carries for those pages
- Rollback path: revert
- Effort: low
- Phase: prose
- Depends on: increment 19
