# Slice 2 — every gate names its command, or declares itself judgment

**Depends on:** slice 1 (the table must exist).

## The defect

`graft.md:810` and `harvest.md:350` both say: *"a gate that runs but asserts
nothing is a green lie; **each check names its command and result**."* Both
sentences sit inside sections that violate them.

| File | Rows with no command | Which |
|---|---|---|
| `graft.md` | **3 of 10** | `:907` pure-graph rebalance, `:909` host loads upgraded kernel, `:910` backups present for every replaced file |
| `harvest.md` | **5 of 8** | faithful import `:293`, availability `:302`, plant untouched `:329`, clean install `:339`, minimum-sufficient `:341` |

`graft.md:910` is the sharpest: **the row that would have caught the defining
defect of 7.16.0 has no detector.** Three plant customizations were destroyed
with zero backups while the audit reported *"clean — no plant knowledge
overwritten"*, and the gate row asserting backups exist was a PASS/FAIL cell a
human filled in by looking.

`harvest.md`'s availability gate is the one with a recorded false PASS: 6.12.0
wrote *"No change needed — the machinery was present"*, and nine versions later
*"`install.sh` **never placed it. Not partially: not at all.**"* Every plant ever
grown got an empty `legal/` directory, and the analyst built around that corpus
could only refuse. The gate proved reachability by reading harvest's own prose.

## The change

Every row resolves to one of three states. No fourth state, and no blank.

**(a) A command exists — name it.** Free wins first:

| Row | Command |
|---|---|
| `harvest` plant untouched | `git -C <plant> status --porcelain` must be empty |
| `harvest` full self-consistency | `bash tests/run.sh` — already named, keep |
| `harvest` clean install | `install.sh --project-dir "$(mktemp -d)"` + `tests/test-full-install.sh` |
| `graft` host loads upgraded kernel | compare the placed kernel against `$SEED/core/AGENTS.md`; `graft-audit.py`'s kernel-currency check already computes this and has no reporting slot |
| `graft` backups present | `tools/graft-audit.py` totality — see (b) |

**(b) No command exists and the gate is load-bearing — build one.** Two:

1. **`graft` backups-present.** The audit enumerates `*.bak-*`, so it can only
   see what the canonical writer produces; a write that bypassed the writer was
   not audited badly, it was *invisible*. `install.sh` now has one writer, which
   makes totality checkable for the first time: assert every destination the
   install touched either produced a backup or is a `place_state`/
   `place_if_missing` destination by declaration. `tests/test-install-placement.sh`
   discovers the destination set already; this reuses that discovery rather than
   listing.
2. **`harvest` availability.** The gate must read `install.sh`, not harvest's
   prose. For each withdraw contract, resolve the claimed delivery path against
   what the installer actually places, and fail when a contract names a path no
   `place_*` call produces. This is the check whose absence cost nine versions.

**(c) No command is possible — say `judgment` and name the judge.** Faithful
import and minimum-sufficient fold-back are genuinely human calls. Mark them
`judgment`, name who makes it, and **delete the claim that every check names a
command** — replace it with the honest form: *every check names its command, or
names the judgment and who owns it.*

That deletion matters. The current sentence is false in both files, and a rule
stated where it is visibly broken teaches that rules here are decorative.

## Evidence this class is real, not theoretical

- 7.15.0's harvest integrity gate records **"Faithful import: PASS after
  correction — an independent review found four passages thinned out of their
  donors and one page that had inverted its donor's contract outright."** Five
  defects the gate as written did not detect; a separate adversarial review did.
- 6.9.1: a wrong plant root or wrong `--date` "found zero backups and printed the
  same *clean — no customization buried* exit-0 line a real audit earns."
- 7.9.0: `--engine` "announced itself as a skip… so the engine-currency gate
  simply did not run."

## Regression

Each new check lands RED first against the condition it was written for: the
availability check against the 6.12.0 legal-corpus state (a withdraw contract
naming a path `install.sh` does not place), the backups check against a
destination bypassing the writer.
