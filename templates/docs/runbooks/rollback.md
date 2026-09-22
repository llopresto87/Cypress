# Rollback

How to get back to a known-good state, how fast, and what data is preserved.

## Doctrine (read before acting)

- **Fix-forward is the default.** On a failure, the first move is the smallest
  reversible containment or a forward fix — not a reversal. Reversal is for
  when forward is slower or riskier than going back.
- **Reversal is never autonomous.** No rollback or restore runs on its own or
  as a reflex; it requires an explicit human go-ahead that names the resource
  and the intent. A tool proposes and stops.
- **Reversible before destructive.** A config/artifact rollback (no data loss)
  is a different, lower gate than a data restore (destructive, lossy). Never
  reach for the destructive path when the reversible one recovers the fault.

## Path A — config / artifact rollback (reversible, no data migration)

1. Repoint to the previous immutable artifact reference: `<cmd>`
2. Re-run the smoke gate: `<cmd>` — a gate asserting the current artifact
   identity is *expected* to go red here, because the reversal deliberately
   restored an earlier one, and that red is the gate working. Update the
   expectation in the same change as the reversal (`protocol.verify`: an
   assertion that fails because the product deliberately changed is updated,
   never reverted around); never widen it to accept any version, because
   catching a stale artifact is the failure this gate exists for.
- How fast: `<target>`
- Data preserved: all — this path touches no data.

## Path B — data restore (destructive — separate, explicit approval)

1. Human go-ahead recorded (who, when, naming the datastore): `<...>`
2. Restore from the captured rollback point: `<cmd>`
3. Verify integrity + re-run the smoke gate: `<cmd>`
- How fast: `<target>`
- Data preserved / lost: `<exactly what the restore window drops>`

## Path B when the capability does not exist yet

Do not write a procedure here that has never been run, and do not leave this
section blank: an invented restore is believed exactly when it matters most,
and a blank one is indistinguishable from an unfinished edit. Replace the
procedure with the ordered chain of what would have to exist before it could
be written, each item a precondition of the next, recorded `absent
(YYYY-MM-DD)` with its owner:

1. `<the capture exists and runs on a schedule>`
2. `<its completion is observable — a marker written by the run itself, not
   the absence of an error>`
3. `<a restore has been performed from that capture into a scratch target,
   with an integrity check on the restored state>`
4. `<the whole reversal has been rehearsed end to end and the run recorded>`
5. `<the retention and the acceptable loss window are decided, not inherited
   from a default>`

Until item 1 holds, the reversal this file promises does not exist, and every
claim above that depends on it says so. Recorded this way the gap is a
decision with an owner rather than an oversight.

## Records

### Rollback <date> — Path <A|B>
- Trigger: `<what failed>` — reversal chosen over fix-forward because `<why>`
- Approved by: `<human>` (Path B only)
- Outcome: `<result>`

<!-- Append per rollback. A rollback that was needed is telemetry for grill §12. -->
