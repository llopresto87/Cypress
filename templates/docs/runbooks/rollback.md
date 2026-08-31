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
2. Re-run the smoke gate: `<cmd>`
- How fast: `<target>`
- Data preserved: all — this path touches no data.

## Path B — data restore (destructive — separate, explicit approval)

1. Human go-ahead recorded (who, when, naming the datastore): `<...>`
2. Restore from the captured rollback point: `<cmd>`
3. Verify integrity + re-run the smoke gate: `<cmd>`
- How fast: `<target>`
- Data preserved / lost: `<exactly what the restore window drops>`

## Records

### Rollback <date> — Path <A|B>
- Trigger: `<what failed>` — reversal chosen over fix-forward because `<why>`
- Approved by: `<human>` (Path B only)
- Outcome: `<result>`

<!-- Append per rollback. A rollback that was needed is telemetry for grill §12. -->
