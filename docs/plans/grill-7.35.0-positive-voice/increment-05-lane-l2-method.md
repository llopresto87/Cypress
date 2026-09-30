<!-- Increment 5 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 5: Prose: lane L2, the method leaves under `core/method/` and `core/operating-principles.md`, in the positive voice
- Item: the owner's instructions 1 to 3 (§2) over the method leaves under `core/method/` and `core/operating-principles.md`, under the round's rewrite conventions (kept outside the seed) and `skills/holistic-editing/SKILL.md`: closing prohibition lists folded into the sections that own their rules, "do X, because Y" in place of "do not", one home per rule, history narration out of doctrine, stale facts corrected
- Spec contracts: none: prose. No spec owns the voice of these files. Text a contract already pins is held by its existing check, and the final tip (increment 25) re-runs every one
- Files touched: `core/method/bounded-execution.md`, `core/method/contract-posture.md`, `core/method/decision-economy.md`, `core/method/delegation-bounds.md`, `core/method/delegation-briefs.md`, `core/method/delegation-cycle-economy.md`, `core/method/delegation-model-classes.md`, `core/method/delegation-sequencing.md`, `core/method/delegation.md`, `core/method/design-governance.md`, `core/method/design-posture.md`, `core/method/engineering-posture.md`, `core/method/host-parity.md`, `core/method/incident-posture.md`, `core/method/maintenance-contracts.md`, `core/method/minimum-sufficient-work.md`, `core/method/prose-posture.md`, `core/method/release-posture.md`, `core/method/restrictive-policy.md`, `core/method/secrets-posture.md`, `core/method/stewardship-posture.md`, `core/method/tiers.md`, `core/method/vcs-posture.md`, `core/operating-principles.md`
- Tests to write (RED): none: prose. Routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`) stays frozen, except a change the lane recorded with the router tests green; its negatives are listed for a later routing round (§12)
- Behavior added: none: the same rules, stated as the right move and its reason
- Gate: the lane's checks as its handback records them (kept outside the seed): `prose-lint.py --file` per file against its pre-edit copy, and the router or eval tests where the lane touched routing text; the full gate at the final tip
- Rollback path: `git checkout 7b219d7 -- <the files above>`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30; its cross-lane items went to increment 13 or to the tooling wave
