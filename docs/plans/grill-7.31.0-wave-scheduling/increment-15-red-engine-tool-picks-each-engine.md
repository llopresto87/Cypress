### Increment 15 — RED: the engine tool picks each engine's config, and the audit checks every engine
- Spec contracts: SPEC-0001/ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE, SPEC-0001/ENGINE_AUDIT_CHECKS_EVERY_PAIR
- Files touched: `tests/test-graft-tools.sh`: new cases after every existing one, each with an invariant label. They build their plant files in the script's temp directory from the seed's real `templates/knowledge-graph/{graph-lint,spec-lint,grill-lint}.py`. `tools/gate-registry.py`: the one `test-graft-tools.sh` entry, only if its "Reads" line is no longer true once the cases read the seed's engines (the R0.5 precedent)
- Tests to write (RED): (a) a stale `grill-lint.py` (the seed copy with every line containing `waves` removed), reconciled with no `--preserve`, exits 0, equals the seed's file byte for byte, and leaves one `.bak-*`; (b) a `spec-lint.py` whose `TEST_GLOBS` the plant changed, reconciled with no `--preserve`, exits 0 and keeps the plant's `TEST_GLOBS`; (c) an explicit `--preserve=ROOT_ID` on a graph-lint-shaped pair still wins; (d) `graft-audit.py <plant> <seed>` given two `--engine` pairs, one current and one stale, prints one currency line per pair, each naming its plant file; (e) the same run with a malformed second pair exits non-zero. Observed red: (a) and (b) exit 2 with `REFUSE: seed engine lacks config 'ROOT_ID'`; (d) prints one line
- Behavior added: none (tests only)
- Gate: `bash tests/test-graft-tools.sh` runs every existing case green and fails first on the new cases' labels; `python3 tools/gate-registry.py --summary` still classifies every step
- Rollback path: drop the new cases (and the registry line, if changed)
- Effort: medium-low
- Phase: RED
- Depends on: none
