# Slice 5 — reversibility, operationalized

**Depends on:** slice 2 (the backups gate must have a detector before a restore
procedure can trust what it finds).
**Scope:** `graft.md` primarily; `grow.md` and `harvest.md` inherit the
"what is not recoverable" statement.

## The defect

`graft.md` asserts reversibility **nine times** — `:3`, `:8`, `:67`, `:81`,
`:178`, `:252`, `:665`, `:957`, `:1015` — and operationalizes it zero times.
Grepping `rollback|revert|restore|unwind` across the file returns no procedure:

- no command to restore from `.bak-*`
- no ordering for a multi-adapter unwind
- no statement of what is **not** recoverable
- no verification that a restore succeeded

The description promises *"Every upgrade is additive, backed up, and
reversible"*. That is the protocol's headline safety claim and it is the one
claim with no procedure behind it.

## What makes this urgent rather than tidy

Two permanent-loss paths and one recorded exception are **already known and
written down elsewhere**, which means the claim is not merely unproven — it is
known to be false in three named cases:

1. **`.cypress/seed.json`** — the one recorded exception to recoverability. It
   carries a fresh `installed_at` every run, so a backup policy would leave one
   `.bak` per install for ever. `place_state` writes it atomically with no backup,
   deliberately.
2. **The second kernel file.** A project's own instructions replaced with no
   record.
3. **A failed adopted-instruction note-write after the kernel was already
   swapped** — the next run saw a kernel matching the seed, therefore no deviation
   to report, and never filed it. `install.sh:341-358` sweeps orphaned backups
   precisely because *"the cost of missing it is permanent."*

All three live in a handoff record and in `install.sh` comments. None is in the
protocol that promises reversibility.

## The change

A new section in `graft.md`, sized to the job (~40 lines), placed where a reader
who has just been told the upgrade is reversible will find it.

**(a) The restore procedure.** Concretely: how `.bak-<date>-<time>` names map to
their originals, the order to restore a multi-adapter plant, and what to do about
files placed by `place_if_missing` (which leave no backup because they only ever
add). Not prose about it — the commands.

**(b) What is not recoverable, named.** The three above, each with the reason.
This is the part that cannot wait: a steward who believes the graft is reversible
will take risks calibrated to that belief, and in three cases the belief is wrong.

**(c) Verification that a restore worked.** The same standard slice 2 applies to
every other gate. `graft-audit.py` already classifies backups; a restore is
verified when the audit reports the pre-graft state, not when the `cp` exits 0.

**(d) The precondition `:79-81` makes, examined.** *"The plant's working tree is
clean, or the steward accepts a backup-only safety net."* That sentence is
untouched since the initial import, and "backup-only safety net" is exactly the
assumption the defining defect of 7.16.0 falsified — 86 destinations produced no
backup at all. Either the sentence is now true because the writer is unified (in
which case say so and cite the gate), or it needs the caveat. It cannot stay as
an unexamined assurance.

## Interaction with git

`graft.md:1005-1007` says graft *"does not fetch/switch/commit/push its Git
state. It records Git state as provenance."* That is right and stays. But nothing
says what happens if the plant's tree is **dirty** when Phase 7 applies — which is
exactly where an unwind would need git and cannot use it. The restore procedure
must state the answer, even if the answer is "refuse".

## Deletions, named

Of the nine reversibility assertions, the ones that are pure restatement go:
`:957` and `:1015` restate `:3` and `:67` in the quality bar and out-of-scope
sections. They are replaced by a pointer to the new section — which is slice 1's
rule applied to a claim rather than a gate.
