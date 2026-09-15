### Slice 3 — The plant's record cannot contradict its disk

**Tier:** T3. **Entries:** U-05 (superseded, now pinned), U-06 (closed).

**Counterexample.** `--legal-corpus no` over a plant carrying the corpus
recorded `"legal_corpus": "no"` while 16 pages sat on disk — exit 0, silent.
`agent.legal` answers from the corpus, not from the stamp, so the plant kept
reasoning from instruments its own record denied having.

**Target behaviour.** The transition is **refused**, naming both honest ways
out (keep the corpus and record `yes`, or remove it deliberately and then
record `no`). Deleting law a plant may already have reasoned from is
user-sovereign; the doctrine pre-ratifies explicit rejection, so no new
destructive command was added. Verified: `no` on a fresh plant is allowed;
`no → yes` allowed; `yes → no` with the corpus present refused with **both the
disk and the record untouched**; deliberate removal then `no` allowed.

**U-05 was superseded, and is now pinned.** The state reducer already merged
correctly at HEAD, but nothing tested it, so it could regress in silence.
`tests/test-plant-state.sh` pins S1–S6 including order independence.

**Honest limit recorded.** The completeness check counted `.bak-*` siblings as
corpus pages and used `-ge`, so four backups would let a twelve-page corpus
satisfy a sixteen-page check. It now counts pages and demands equality. This
correction carries **no behavioural regression**, because `place_tree` never
fails to place a page and no public-interface sequence produces the partial
corpus the old check would have waved through. It becomes testable the day
placement can fail partway. The test says so in place, so nobody reads the
passing assertion as proof of the stricter check.

### Verification run at this slice boundary

`bash tests/run.sh` → **EXIT=0**, now including
`install-placement: OK — 376 destinations recoverable, symlink-safe,
idempotent, link-uniform, audit-classifiable` and `plant-state: OK`.
Kernel 7 564 bytes, unchanged. Placed file set 376 files/links.

### Prevention

| Closed | Gate that makes it non-recurring |
|---|---|
| U-01, U-02, U-04, U-09b | `test-install-placement.sh` M7/M2/M9, over a *discovered* destination set |
| U-03 | same suite, M8: zero UNMAPPED backups, plus `graft-audit.py` now exits 1 on UNRESOLVED |
| U-05, U-06 | `test-plant-state.sh` S1–S6 |
| U-07 | one sentence shared by code, help text and `INSTALL.md`; `place_kernel` no longer has its own backup branch to diverge |
| U-08 | special-character targets verified to substitute literally and parse as TOML |
| U-10, U-11 | direct probes recorded above |
| U-09a | failure and drift are separate verdicts |

**Still unprotected:** an intermittent M3 churn observed once during this audit
and not reproduced in 10 suite runs or 12 install-twice cycles. It is recorded
as **Unknown** rather than closed. What changed: the M3 assertion now NAMES the
churned files instead of counting them, so a recurrence is diagnosable instead
of being lost.
