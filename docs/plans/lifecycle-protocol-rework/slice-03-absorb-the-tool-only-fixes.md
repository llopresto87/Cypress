# Slice 3 — the procedures absorb their own tool fixes

**Depends on:** slices 1 and 2 (each item lands as a table row or a step).

## The defect

Sorting every recorded defect in these three protocols by who found it produces a
clean split:

- Found by **a human on a live run** → reached the protocol text almost every
  time. `graft.md`'s migration steps (c)–(f) and its cross-author rebalance gate
  exist because one operator complained through four rounds on a live graft;
  steps (d) and (e) exist because they complained about the fix to the previous
  complaint. The record says so: *"that gap is exactly why they are now protocol
  text instead of tribal knowledge."*
- Found by **the seed auditing its own tooling** → landed in the tool and stopped.

The second list is ~28 items. The protocols learn from people and not from their
own gates.

## The items

### `graft` — 16

| # | Defect | Fix lives in | `graft.md` says |
|---|---|---|---|
| 1 | 86 destinations destroyed plant edits with no backup; audit reported clean | `install.sh` writer unification, `test-install-placement.sh` | `:677-679` still *"rely on"* the installer's backups |
| 2 | adopted-instruction ledger + orphan sweep | `install.sh:274-358` | **nothing** — and it is absent from `CHANGELOG.md` too |
| 3 | schema-currency check (`_schema.md` older than the machinery reading it) | `graft-audit.py`, 7.9.0 | `_schema.md` named 4×, always as "stays the plant's"; no gate row, no output slot |
| 4 | `--force` skipping backups — **twice**, 7.1.1 and 7.16.0 | `install.sh`, `INSTALL.md`, help text | `--force` appears **zero** times |
| 5 | `--symlink` kernel delivered a frozen copy | `install.sh` | `--symlink` appears **zero** times |
| 6 | stamp narrowing, corruption, `yes→no` contradiction | `install.sh`, `test-plant-state.sh` | reads the stamp as authoritative at `:245`, `:820` |
| 7 | `__pycache__` shipped into `docs/graph/templates/`, reported by the next graft as a file to reconcile | `install.sh place_tree` | no rule for a machinery-subtree file with no seed source |
| 8 | half-installed target; silently reverted deliberate deletions | `install.sh` preflight, `test-install-adoption.sh` | `:278-282` — *"Install the new machinery as usual"* |
| 9 | legal corpus invisible to the audit | `graft-audit.py` | nothing |
| 10 | `.prime/agent/` unmapped by the audit | `graft-audit.py` | territory listed; audit coverage of it never mentioned |
| 11 | seed's own phrasing read as plant signal (cry-wolf) | `graft-audit.py:389` | gate row `:901` presents PASS/BLOCK as trustworthy |
| 12 | `--date` mismatch → vacuous audit | `graft-audit.py` | `--date` never mentioned |
| 13 | adapters projected agents/skills from the seed, not the graph | `install.sh` 7.15.0 | `:312-315`, `:578-582` describe the **pre-7.15.0** installer — see slice 4 |
| 14 | `UNJUSTIFIED` / `UNGROWN` coverage verdicts | `growth-audit.py` | `:707-728` names the verdicts, never what produces them |
| 15 | `graft-audit.py --help` → "unknown option", exit 2 | `graft-audit.py` | n/a |
| 16 | the audit's "clean" depends on `--tokens`; under-supplied tokens produce a reassuring PASS over a buried customization | documented in the tool's docstring and one slice record | `:686` gives `--tokens=<plant tokens>` with **no guidance on what a plant's tokens are** |

Item 16 is the one to fix first. It is the central gate, its honest limit is
recorded everywhere except the procedure that invokes it, and the fix is cheap:
say where a plant's vocabulary comes from — its own `README`, its `product/`
nodes, the names in `.cypress/seed.json` — and say plainly that a `clean` result
is bounded by the tokens supplied.

Item 2 is the one with the strangest shape: a graft creates docs-librarian work
inside `docs/graph/plans/`, the one subtree `graft.md:424` declares outside the
audit's machinery subtrees, and never tells the steward it did.

### `grow` — 8 bypasses plus 4 unnamed tools

The eight ways the coverage gate reported green on an ungrown plant — *"an
adversarial review of this increment found the audit passing the exact plants it
was written to catch"* — live entirely in `tools/growth-audit.py`. Not one became
protocol text. The most consequential is documented as a **code comment**:

> appending one character to `design/README.md` or `legal/index.md` marked those
> collections COVERED — and their agents with them.

A reader of `grow.md` alone learns that *"template files existing at their paths
is never coverage"* (`:191`) and would reasonably conclude a materially-edited
template **is** coverage. The 400-byte authored-body floor exists nowhere in the
protocol.

Also:

| Tool | Status | `grow.md` |
|---|---|---|
| `prose-lint.py` | installed into every plant by `install.sh:721` | **never named.** Growth authors an entire graph of prose and never runs it |
| `agnosticism-lint.py` | instructed in Phase 4 `:556-564` | **absent from Phase 6's command block** — an instruction with no gate |
| `growth-audit.py --agents` / `--json` | the fast answer to "can every roster specialist work here?" | only one of four forms named |
| `growth-audit.py` `STALE` | three distinct conditions | `STALE` appears **zero** times, in a file that enumerates ten other verdicts |

And the 7.9.0 path-vs-content fix: the tool now accepts a collection's own
`index.md`/`README.md` as the legitimate home of an authored absence. `grow.md`
says the absence goes in the coverage record and never says to write it there —
so a run that follows the protocol exactly fails on a technicality the procedure
never mentioned.

### `harvest` — 4

| Defect | Fix lives in | `harvest.md` |
|---|---|---|
| `agnosticism-lint.py` silently skipped unreadable files, 6.14.0→7.16.0 — harvest's named "mechanical floor" could PASS over a file it never opened | `agnosticism-lint.py:110-119`, `test-lint-audibility.sh` | untouched. Phase 4 still says only *"pair it with a read of the diff"* |
| `skill.humanizer` declares harvest as one of its five execution sites | the skill, `prose-lint.py` | zero occurrences of "humanizer" or "prose" |
| 7.16.0 ratchet/gate-registry machinery now governs `harvest.md` itself | `ratchet-lint.py`, `gate-registry.py` | neither named |
| legal-corpus delivery | `install.sh`, `_schema.md`, `graft-audit.py` | `grow.md` and `graft.md` were updated; **harvest, whose gate had passed falsely, was not** |

The near-miss that proves the class: when `agnosticism-lint.py` was created it
was *deposited and not wired*, found only because someone applied **harvest's own
availability gate** to a non-harvest release — *"no protocol node named it, and no
plant received it, so an agent running harvest would read 'grep the diff' and
hand-roll one."* The fix was applied to that one tool and never generalized, and
`HARVEST_PROMPT.md` — a second entry point into the same protocol — was left out
of even that sweep.

## The change

Each item lands in exactly one of three places, and the slice records which:

1. **A gate table row** (slice 1's table) — when the tool already checks it and
   the procedure simply never said so.
2. **A step in the phase that does the work** — when the procedure must *act*
   differently, not merely verify.
3. **Explicitly nowhere, with the reason recorded here** — when the item is a
   tool-internal concern a procedure should not carry. Item 15 (`--help`) is one.

The default is (1). The test for (2) is whether a correct reader of the current
text would still do the wrong thing — which is the standard the record itself
set: *"The instruction was wrong, not the reading."*
