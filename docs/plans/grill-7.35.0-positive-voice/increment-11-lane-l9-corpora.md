<!-- Increment 11 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 11: Prose: lane L9, the agent, skill, tool and legal corpora, in the positive voice
- Item: the owner's instructions 1 to 3 (§2) over the agent, skill, tool and legal corpora, under the round's rewrite conventions (kept outside the seed) and `skills/holistic-editing/SKILL.md`: closing prohibition lists folded into the sections that own their rules, "do X, because Y" in place of "do not", one home per rule, history narration out of doctrine, stale facts corrected
- Spec contracts: none: prose. No spec owns the voice of these files. Text a contract already pins is held by its existing check, and the final tip (increment 25) re-runs every one
- Files touched: `agent-corpus/README.md`, `agent-corpus/claim-verifier.md`, `agent-corpus/client-frontend-specialist.md`, `agent-corpus/env-contract-manager.md`, `agent-corpus/integration-topologist.md`, `agent-corpus/legacy-runtime-reconstructor.md`, `agent-corpus/legal.md`, `agent-corpus/report-editor.md`, `skill-corpus/README.md`, `skill-corpus/adversarial-pentest-passes.md`, `skill-corpus/deploy-fleet-on-remote-docker-host.md`, `skill-corpus/discardme.md`, `skill-corpus/drive-hosted-cicd-cli.md`, `skill-corpus/framework-version-migration.md`, `skill-corpus/harden-docker-host.md`, `skill-corpus/live-patch-stopgap.md`, `skill-corpus/mutation-verify.md`, `skill-corpus/operator-compressed-fix-path.md`, `skill-corpus/prove-red-after-green.md`, `skill-corpus/release.md`, `skill-corpus/triage-unresolved-required-variable.md`, `tool-corpus/testing/http-smoke-suite.md`, `legal-corpus/_schema.md`, `legal-corpus/README.md`, `legal-corpus/index.md`
- Tests to write (RED): none: prose. Routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`) stays frozen, except a change the lane recorded with the router tests green; its negatives are listed for a later routing round (§12)
- Behavior added: none: the same rules, stated as the right move and its reason
- Gate: the lane's checks as its handback records them (kept outside the seed): `prose-lint.py --file` per file against its pre-edit copy, and the router or eval tests where the lane touched routing text; the full gate at the final tip
- Rollback path: `git checkout 7b219d7 -- <the files above>`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30; its cross-lane items went to increment 13 or to the tooling wave
