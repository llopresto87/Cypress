## §10 Review round 4 — the last structural hole

Round 4 injected twelve regressions one at a time and ran the full gate on each.
**Eleven were caught**, each naming the file: five silently-dropped destinations
across five different adapters, a skipped backup, a destination following a
symlink, a kernel desync, a stamp contradicting the disk, a linter reverting to
silent skipping, `--eval` reporting a combined average, a trigger copy relabelled
into the held-out class, a router forced to answer HIGH on everything, an
unclassified gate step, and a removed test.

**The twelfth was not caught, and it was the same defect twice.**

> Bloat `core/AGENTS.md` past 8 000 bytes, raise `KERNEL_BUDGET` to 20 000 in
> `tests/seed-lint.py`, and the gate goes green.
>
> Break the edition markers on a legal page so 25 entries fail their citability
> contract, add those 25 IDs to `EDITION_DEBT` in `tests/legal-lint.py`, and
> `legal lint: PASS — 70 carrying recorded edition debt`.

Every budget, threshold and debt ledger in this repo is a plain literal sitting
in the same file as the check it governs. `test-seed-budgets.sh` proves each one
*can* fire — by overriding it in memory — and nothing proved the **shipped value**
had not been loosened to wave a real violation through. The doctrine forbids
exactly this ("never raise a budget so existing text fits"); nothing enforced the
sentence. `EDITION_DEBT`'s own comment says "a NEW entry may not join this list",
and only the opposite direction was checked.

`tools/ratchet-lint.py` records all ten limits in `tests/ratchets.json` with the
direction that counts as tightening. A ceiling may fall and a floor may rise
freely; loosening either fails until the recorded value changes too — a separate,
conspicuous edit to a file that exists for no other purpose. Both of the
reviewer's reproductions now fail the gate, and the full kernel-bloat scenario
that passed before exits 1.

**What it does not do, said in the tool itself:** nothing here stops someone
editing both files in one commit. What it stops is a limit being loosened
*silently*, inside a change that appears to be about something else. A tripwire,
not a vault.

### Writing it produced the sharpest bug of the whole remediation

The first version reported `current=7600` while the file on disk plainly read
`8_000`. Python validates its bytecode cache on **(mtime, size)** — and
`KERNEL_BUDGET = 8_000` and `KERNEL_BUDGET = 7_600` are the same byte length, so
restoring the file within the same second replayed the stale `.pyc`.

For most importers that is a curiosity. For a checker whose entire job is to
report what the shipped values *are*, reading a cache is the one thing it must
never do: it would report a loosened limit as unchanged, which is worse than
having no check. It compiles from source text now, every time, and says why.

A tool that verifies constants, defeated by a constant-length edit, found by its
own first run.

### Also closed

`--project-dir` pointing at a directory that does not exist produced the shell's
error rather than this tool's — the one unexercised path, because every test in
the suite happens to `mkdir -p` first and `INSTALL.md`'s example does not imply
the target must pre-exist.

### Convergence

Round 4's own judgement: the mechanisms are solid, and the single remaining gap
was structural rather than a bug in any of them — "nearly everything I tried to
break was already anticipated and pinned by name in a comment before I tried
it". That gap is now closed, and it was the last one any round classified as a
defect rather than a documented limit.

Findings per round: **9, 6, 6, 1**. The loop is converged — not because nothing
is left, but because what is left is written down as the boundary of the
mechanism rather than a hole in it: a lexical router cannot disambiguate senses,
a lexical overlap floor cannot establish provenance, a preflight cannot enumerate
a directory that does not exist yet, and a lock file cannot stop a determined
editor — only a quiet one.
