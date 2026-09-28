### Increment 44 — Prose: plant-reachable host facts, residual pointers and nits (ruling pass 6)
- Spec contracts: none — pointer and home repairs judged by review (SPEC-0005 §6 "Effort", as amended in v0.7)
- Files touched: `core/method/delegation-model-classes.md` (the Claude Code effort facts return to the `delegation.effort` section, from the overlay, with the source and retrieval date, because `install.sh` never places the overlay in a plant; the duplicate overlay pointer at :162-163 removed), `integrations/claude-code/README.md` (its effort section becomes a pointer to `docs/graph/method/delegation-model-classes.md`), `templates/agent.template.md` (its effort pointer names the leaf, not the overlay), `templates/knowledge-graph/_schema.md` (one sentence under the trigger-phrase note: a version-selecting piece carries the whole version token, such as `net10.0`, because parts under three characters are dropped), `documentation/agents-reference.md` (:17, :29, :37) and `documentation/skills-and-templates-reference.md` (:1464) (pointers to the siblings), `manifest.json` (:17, the three homes as bootstrap step 5 names them), `core/method/engineering-posture.md` (:143-145) and `core/method/contract-posture.md` (:181-182) (lines reflowed)
- Tests to write (RED): none — prose increment
- Behavior added: a plant reaches the host facts from its own graph; one home for them
- Gate: `python3 tests/seed-lint.py` (leaf ceiling on the model-class leaf, mirrors); `prose-lint` per file against baseline
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 36
