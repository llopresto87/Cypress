<!-- Increment 56 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 56: RED: the anchor fixture leaves no background Git writer and matches a placed plant
- Item: F (class P), fixture hardening from the cycle 1 ruling pass
- Spec contracts: SPEC-0003/ANCHOR_COMPARE_WRITES_NOTHING (its case X159 only; the contract is unchanged). Why: one X159 run in about 25 failed on `.git/objects/maintenance.lock`, which the background maintenance that the fixture's own `git commit` starts holds for a moment; a trace of `--compare` shows the tool starts no such process. And the fixture copies `code-anchor.py` alone, where `install.sh` places `frontmatter.py` beside it, which increment 62 needs
- Files touched: `tests/test-bound-hook.sh` (the code-anchor block only: the fixture's own Git calls carry `-c maintenance.auto=false -c gc.auto=0`, while `ENV`, which the tool also runs under, stays as it is, so X159 still sees any write the tool itself causes; the fixture plant gets the seed's canonical frontmatter reader beside the placed tool, as the installer places it)
- Tests to write (RED): none new. A fixture edit, green on arrival: every case of the block keeps its state
- Behavior added: none
- Gate: `bash tests/test-bound-hook.sh` green, X152 to X163 in the same state, over repeated runs; the orchestrator re-records the file's hash
- Rollback path: revert the fixture lines
- Effort: low
- Phase: RED
- Depends on: increment 31
