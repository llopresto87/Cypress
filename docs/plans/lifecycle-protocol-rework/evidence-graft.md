# Evidence — `protocols/graft.md`

Mined from `CHANGELOG.md` (4 381 lines), 18 plans, 7 ADRs, and the diff of every
one of the 13 commits that touched the file. Citations are current-tree line
numbers or commit shas.

## Size and structure

747 → 992 body lines, **+33% in 14 days across 13 commits. No commit has ever
removed a section.** The initial import `6dde434` already carries 4.6.0 → 6.8.0
squashed, so "unchanged since import" means unchanged since 6.8.0.

| sha | version | body | Δ | what was added |
|---|---|---|---|---|
| `6dde434` | ≈6.8.0 | 747 | — | the whole file |
| `c8706d7` | 6.9.1/2 | 755 | +8 | `_schema.md`/`index.md` are the plant's; `--tokens=`/`--engine=` forms |
| `b4de261` | 6.12/13.0 | 767 | +12 | the **kernel-current gate** |
| `53f845a` | 6.14/7.0.0 | 821 | **+54** | status migration; unfilled-scaffolds gate; two output sections; two gate rows |
| `ba5d0d0` | 7.0.1 | 830 | +9 | kernel gate → three verdicts |
| `6fbfe66` | 7.1.0 | 830 | 0 | one word |
| `713d32a` | 7.3.0 | 880 | **+50** | "run grow's loop"; coverage gate; provenance rewritten around the real stamp |
| `e9c1896` | 7.5.0 | 905 | +25 | expertise rows; `UNSTAFFED`; the unspawnable-projection clause |
| `7917a04` | 7.9.0 | 908 | +3 | `--engine` pair form |
| `7ff4b55` | 7.10.0 | 927 | +19 | `SILENT`; the "filled elsewhere" drift class |
| `bb90f8d` | 7.11.0 | 930 | +3 | whole-legal-corpus rule |
| `5b46114` | 7.12.0 | 932 | +2 | jurisdiction re-ask |
| — | 7.13.0–7.15.0 | 932 | **0** | **four releases, including the roster-projection fix, left it untouched** |
| worktree | 7.16.0 | 992 | +60 | shape migration |

Sections added after import, each traceable to an incident: status migration
(`53f845a`), shape migration (worktree), unfilled-scaffolds gate (`53f845a`),
kernel-current gate (`b4de261`/`ba5d0d0`), coverage gate (`713d32a`), the
"filled elsewhere" drift class (`7ff4b55`). **Sections removed: one** — the
GRAPH DISCIPLINE block, replaced by a pointer at `c8706d7`.

## The defining defect

Three plant customizations destroyed, zero backups, and `graft-audit.py`
reporting *"clean — no plant knowledge overwritten, no customization buried."*
The verdict was inverted because the audit enumerates `*.bak-*` and can only see
what the canonical writer produces; a write that bypassed the writer *"was not
audited badly — it was **invisible**."* 17 bypass sites across 4 idioms = 86
files per `install.sh all`.

Fixed entirely in tooling. **`graft.md:677-679` — the sentence instructing
reliance on installer backups — was not touched.**

## Fixes that landed in a tool and never reached the procedure

Sixteen, tabulated in `slice-03-absorb-the-tool-only-fixes.md`. The asymmetry
that produced them: defects found by a human operator on a live graft reached the
text almost every time; defects found by the seed auditing its own tools landed
in the tool and stopped.

## Accretion

| Duplicated fact | Homes |
|---|---|
| one-home-per-dependency | `:504-520`, `:513-514`, `:763-774`, `:969-971` |
| the rootstock line | `:83-94`, `:131-134`, `:658-665`, `:940` |
| the three-way reconciliation | `:194-223` and again at `:433-448`, 240 lines apart |
| "relocating is not reconciling" | `:300` and `:316-319` — both added in reaction to the **same** operator complaint |
| every Phase 7 gate | its prose bullet + its integrity-gate row — **two homes, written in the same commit, every time since 6.12.0** |

Escalating emphasis on rules that kept being violated: *"Grafted is not grown"*
(`:527`, 5.4.0) → a whole new block *"Run grow's loop, do not re-invent it"*
(`:532`, 7.3.0) → a mechanical gate (`:707-728`). Three layers on one rule.

Later text narrowing earlier text without amending it: `:126` absolute, narrowed
at `:369-372`; `:131-134` absolute, narrowed at `:136-142` and `:681-684`.

## Never changed since import

`## Trigger` (settled — user-sovereignty is enforced mechanically by
`seed-lint`'s command-roster guard), `## The three-way reconciliation` (settled —
survived twelve versions), `## When to invoke` (`:79-81` **unexamined** — the
"backup-only safety net" is the assumption the defining defect falsified),
**Phase 7's opening sentence** (unexamined, and the single most consequential
untouched line in the file), Phase 1 (reads the stamp with no corruption
handling), Phase 2 (its ledger has no schema and no tool), Phase 8 (six lines,
and it is the ratification boundary every destructive step depends on).

## Gate rows and verification

Ten integrity-gate rows. Three name no command (`:907`, `:909`, `:910`) in a file
that at `:810-811` demands *"each check names its command and result"*. The row
that would have caught the defining defect (`:910`) has no detector. One row
(`:901`) has failed in **both** directions — false-clean, and cry-wolf on
untouched machinery.

Reversibility asserted at `:3`, `:8`, `:67`, `:81`, `:178`, `:252`, `:665`,
`:957`, `:1015`. No restore command, no unwind ordering, no statement of what is
unrecoverable, no verification a restore succeeded.

## Frontmatter

`owns:` unchanged in 13 commits, weighing ~50 / 50 / 570 lines — **~370 body
lines belong to none of the three declared facts**. `requires:` empty against
seven real dependencies. `load_when:` unchanged: four triggers, all variations on
"upgrade this plant"; three sections have no trigger. `est_tokens` 9790 → 16037,
the last jump +4000 for +60 lines, revealing that earlier values had drifted low
under a 2×-loose honesty check.
