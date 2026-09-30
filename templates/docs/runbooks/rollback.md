# Rollback

How to get back to a known-good state, how fast, and what data is preserved.

## Doctrine (read before acting)

- **Fix-forward is the default.** On a failure, the first move is the smallest
  reversible containment or a forward fix, not a reversal. Reversal is for
  when forward is slower or riskier than going back.
- **Reversal waits for a human.** A rollback or restore runs ONLY on an
  explicit human go-ahead that names the resource and the intent, never on its
  own or as a reflex. A tool proposes and stops.
- **Reversible before destructive.** A config/artifact rollback (no data loss)
  is a different, lower gate than a data restore (destructive, lossy). Take
  the reversible path whenever it recovers the fault; the destructive path is
  the last resort.

## Recorded before each release

What the pre-release record must hold is set by `method.release-posture`
§2; these are its fields, filled per release before deploying.

- Previous build identifiers: `<artifact@digest per component>`
- Migration compatibility: `<reversible | irreversible, and whether
  deployment auto-applies it>`
- Message-schema compatibility: `<can the previous artifact read what the
  new one writes>`
- Derived state: `<caches, search or vector indexes, materialized views;
  can the previous artifact use what the new one built>`. Reverting code
  over a derived store the newer version built is a mixed-version state
  too, and Path A below does not undo it.

## Path A — config / artifact rollback (reversible, no data migration)

1. Repoint to the previous immutable artifact reference: `<cmd>`
2. Re-run the smoke gate: `<cmd>` — a gate asserting the current artifact
   identity is *expected* to go red here, because the reversal deliberately
   restored an earlier one, and that red is the gate working. Update the
   expectation to the restored artifact's identity in the same change as the
   reversal (`protocol.verify` owns why), keeping it pinned to one exact
   version, because catching a stale artifact is this gate's job.
- How fast: `<target>`
- Data preserved: all; this path touches no data.

## Path B — data restore (destructive — separate, explicit approval)

1. Human go-ahead recorded (who, when, naming the datastore): `<...>`
2. Restore from the captured rollback point: `<cmd>`
3. Verify integrity + re-run the smoke gate: `<cmd>`
- How fast: `<target>`
- Data preserved / lost: `<exactly what the restore window drops>`

## Path B when the capability does not exist yet

Fill this section with the ordered chain of what would have to exist before a
restore procedure could be written, each item a precondition of the next,
recorded `absent (YYYY-MM-DD)` with its owner, because an invented restore is
believed exactly when it matters most and a blank section reads as an
unfinished edit:

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
