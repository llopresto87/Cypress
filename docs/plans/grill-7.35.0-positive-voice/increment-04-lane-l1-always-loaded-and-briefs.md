<!-- Increment 4 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 4: Prose: lane L1, the always-loaded surfaces and the brief templates, in the positive voice
- Item: the owner's instructions 1 to 3 (§2) over the always-loaded surfaces and the brief templates: the kernel, the host overlays and hooks, the root prompts and `templates/prompts/`, under the round's rewrite conventions (kept outside the seed) and `skills/holistic-editing/SKILL.md`: closing prohibition lists folded into the sections that own their rules, "do X, because Y" in place of "do not", one home per rule, history narration out of doctrine, stale facts corrected
- Spec contracts: none: prose. No spec owns the voice of these files. Text a contract already pins is held by its existing check, and the final tip (increment 25) re-runs every one
- Files touched: `GRAFT_PROMPT.md`, `HARVEST_PROMPT.md`, `INSTALL_PROMPT.md`, `core/AGENTS.md`, `integrations/claude-code/README.md`, `integrations/claude-code/agent-lint.py`, `integrations/claude-code/bound-hook.py`, `integrations/claude-code/frontmatter.py`, `integrations/claude-code/route-hook.py`, `integrations/claude-code/settings.json`, `integrations/claude-code/status-hook.py`, `integrations/opencode/README.md`, `integrations/opencode/opencode.json`, `integrations/prime-agent/APPEND_SYSTEM.md`, `integrations/prime-agent/README.md`, `integrations/prime-agent/route-extension.ts`, `integrations/prime-agent/settings.json`, `integrations/prime-agent/status-extension.ts`, `templates/prompts/clean-context-validation-brief.md`, `templates/prompts/graph-session-bootstrap.md`, `templates/prompts/growth-author-brief.md`, `templates/prompts/growth-coverage-record.md`, `templates/prompts/growth-evidence-ledger.md`, `templates/prompts/growth-scout-brief.md`, `templates/prompts/handback-payload.md`, `templates/prompts/investigation-brief.md`, `templates/prompts/node-authoring-brief.md`
- Tests to write (RED): none: prose. Routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`) stays frozen, except a change the lane recorded with the router tests green; its negatives are listed for a later routing round (§12)
- Behavior added: none: the same rules, stated as the right move and its reason
- Gate: the lane's checks as its handback records them (kept outside the seed): `prose-lint.py --file` per file against its pre-edit copy, and the router or eval tests where the lane touched routing text; the full gate at the final tip
- Rollback path: `git checkout 7b219d7 -- <the files above>`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30; its cross-lane items went to increment 13 or to the tooling wave
