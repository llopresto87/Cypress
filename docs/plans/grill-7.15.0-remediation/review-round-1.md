## §6 Review round 1 — what three independent reviewers found

Three reviewers were given disjoint scopes, told to be adversarial, and told
that their value was in what they found wrong. They were right to be. Every
item below was reproduced before it was fixed.

### Claims of mine that were false

**`install.sh all --symlink` churned backups without bound.** 1, then 3, then 5
on identical re-runs, for ever. `place_kernel` decided which of
`CLAUDE.md`/`AGENTS.md` held the kernel by testing for a plain regular file —
never true in symlink mode — so each of the five adapters claimed its own
destination and the pair flipped on every call. The content stayed
byte-identical throughout, so only `ls -la` could see it. **M3 was asserted as
holding and did not**, because the M3 check ran only under `--copy`. It now runs
in both modes.

**"Every byte goes through one of four named operations" was false.**
`place_kernel`'s sibling link is placed by a bare `mv`/`rm`/`ln -s`, and the
spec's SINGLE_WRITER contract said otherwise. The reviewer also disproved the
spec's own coverage note, which claimed M1 needed no test because the M7/M2
sweeps caught a bypass "by construction": patching `place_file` to skip one
protocol produced **zero** failures and a green suite.

The reason is worth keeping. The sweep discovers its file set from what the
install *produced*, so a destination the installer stopped writing is absent
from the set and is never checked. Discovery is the right way to ask "is
everything that got written safe"; it is structurally the wrong way to ask "did
everything that should be written get written". That second question now walks
the seed's own inventory, and the reviewer's exploit fails by name.

**A spec certified a test that was never written.** SPEC-0002 marked
`UNKNOWN_DOMAIN_MUST_ABSTAIN` **green** against
`test_eval_novel_stack_rows_stay_low`, a name appearing nowhere in the
repository. Two more contracts pointed at tests that exercised a different
scenario. Three real tests now exist, and `seed-lint.py` greps every `§10` cell
against the suite, so the defect cannot recur — proved by planting a fabricated
name and watching it fail.

**A dead assertion.** `is_plant_owned "$rel" || true` discarded its own result;
the comment described a check the code never performed.

**The M4 test's title oversold it.** It promised `--force` suppresses the
warning and asserted only that backups existed — on exactly the two files where
suppression was broken.

**The gate registry classified three of my own suites `none`** — no known
false-green exposure — and two of them demonstrably had some. Corrected to
`coverage`, each naming the specific blind spot a reviewer demonstrated.

**The registry's parser had blind spots.** It saw 4 of 8 real invocations in a
crafted `run.sh`, missing a line continuation, a subshell, an interpreter flag
before the path, and a relative path — and reported OK. A registry that cannot
see a gate fails in the quietest way available: by finding nothing to complain
about. It now reads all 7 spellings a reviewer could construct.

### Defects in the work, not just the claims

- **The legal corpus was invisible to the audit.** `seed_source_for` had no
  `legal/` branch, so editing any of its 16 pages produced an `UNMAPPED` backup
  *and* a false "plant knowledge overwrite" on a seed-owned page — both wrong,
  on a first-class documented feature. `legal/corpus/` is now seed-owned;
  `legal/index.md` is deliberately not, because that one really is the plant's.
- **The record could contradict the disk without a wrong flag.** Decide `yes`,
  lose the corpus out-of-band, install another adapter with no legal flag: the
  stamp still read `yes` over an empty directory. The refusal only ever fired on
  an explicit `--legal-corpus no`. The recorded decision now drives placement,
  and a restore is announced rather than silent.
- **`tests/test-full-install.sh` leaked a full install into `/tmp` on every gate
  run** — a second `trap ... EXIT` replaced the first rather than stacking.
- **Three new `seed-lint` checks had no planted violation**, contradicting that
  suite's own stated contract. They have one each now, and the body-ceiling case
  was rewritten after the first version passed for the wrong reason (the padding
  also tripped the `est_tokens` check).
- **Internal numeric contradictions in `seed-lint.py`'s own comments** — the
  file whose job is one-home-per-fact numeric claims.

### Where a reviewer was wrong, and the record of why

One reviewer reported README's body-size numbers as off by one. They are not:
931 and 170 are what `machinery_nodes()` measures, and `wc -l` minus frontmatter
gives 932 because the body's trailing newline is stripped. The inconsistency was
in `seed-lint.py`'s own comment, which said 932. Fixed there, and the discrepancy
is now explained in place so the next reader does not re-derive it.

The same reviewer asked for `--force` to suppress `place_kernel`'s warnings for
consistency. Half right. The generic "backed up existing X" line is chatter and
now respects `--force`; the **kernel deviation notice does not, by design** — it
says a deviation the plant deliberately recorded on the one file loaded by every
session is gone, and a flag meaning "yes, overwrite, stop asking" must not also
mean "and don't mention what you destroyed". `tests/test-unified-graph-install.sh`
pins that, which is how the attempted change was caught.
