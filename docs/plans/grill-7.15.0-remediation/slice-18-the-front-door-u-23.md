### Slice 18 — The front door (U-23)

**Tier:** T1. The last open non-Track-E entry, and the doctrine said to do it
last, which is why it is here.

The finding was that a reader met several hundred lines of doctrine and a private
vocabulary before reaching an install instruction. Measured at the start of this
slice: the first `install.sh` line was at **README line 111**. It is now at
**line 38**, behind a block that answers the three questions an evaluator
actually has — what it is, what it costs to run, and the one command.

The cost table is the part worth keeping honest, and every figure in it is
measured rather than estimated, reproduced from `seed-lint.py`'s own
`check_eager_surface` at the time of writing:

| Claim in README | Measured |
|---|---|
| ~24 600 B (~6 100 tokens) on Claude Code / opencode / Codex | 24 557 (6 139) |
| ~19 900 B on Prime Agent | 19 920 |
| ~121 500 B on GitHub Copilot | 121 543 |
| kernel 7 564 B under a hard 8 000 budget | 7 564 |
| 10–20% method overhead on small, well-specified work | slice 15's single observation |

The Copilot outlier is stated in the same table rather than in a footnote, and
the paragraph under it says why and links the capability matrix. A front door
that quotes the good number and hides the bad one is the thing this remediation
exists to stop.

The doctrine's other half — "move doctrine to its own file" — was **not** done.
The README is 424 lines and the material below the fold is coherent where it
sits; splitting it would create a second home for the same explanation and buy
nothing a reader who has already got their answer at line 38 would notice. That
is a narrowing of the disposition, recorded rather than silently skipped.

### End-to-end check, and one bound it exposed

Installed all five adapters into a real git repository carrying a hand-written
`AGENTS.md` ("Rule: always rebase."), a source file and a `.gitignore`, with the
legal corpus. Result: the team's file was backed up and remains recoverable, the
source was untouched, 16 corpus pages landed, an identical re-run produced zero
new backups, and `graft-audit.py` classified the single backup with zero
`UNMAPPED`. The install announced the kernel overwrite in four explicit warning
lines naming the backup and saying that a recorded deviation is not in the new
body.

**The bound.** With default tokens the audit reports that backup as `DELTA` and
prints `clean — no plant knowledge overwritten, no customization buried`. Run
with the plant's own vocabulary (`--tokens rebase`) it correctly reports
`1 FF-overwritten plant customization — RE-INTEGRATE or ratify`.

Both verdicts are true to what the tool measures: `clean` means *nothing was
buried*, and the backup is present and classified, not buried. But the default
run's reassurance depends on the steward supplying the words their own project
uses. That is designed — `--tokens` exists precisely because the seed cannot
enumerate a plant's vocabulary — and it is documented inside `graft-audit.py`.
It is recorded here because "every backup is classifiable" (M8) is a weaker
claim than "the audit will notice your customization", and only the first is
what this remediation established.

---
