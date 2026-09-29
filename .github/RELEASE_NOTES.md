## 7.34.0 — a harvest: tests sized by contract, and grill-lint reads a spec's status from its frontmatter (2026-09-30)

A grown plant was harvested back into the seed. What ships here is the
general part: no plant identity, no stack, and no counts from any project.

**Signs that a check costs more than it is worth.** `test-first.proportionate-checks`
names four more. A test that passes on either of two implementations asserts
nothing, so it asserts the one mechanism, and a contract that allows two shapes
goes back as a spec ambiguity. Where a behavioral assertion is possible, no
test checks that code calls a function, imports a module or takes a path: a
mock that only counts calls fails on a rename and passes on wrong behavior.
A long setup, a helper of its own, or a comment that points at the one line
that matters marks a test as over budget, and the answer is a smaller test or none. A
property of a factory, a table or a loop is one case over the collection,
never one per element. The Mocking-everything anti-pattern in test-first now
links to the mock and either-or rules instead of repeating them.

**A plan names contracts, not test cases.** In `grill.increment-shape`, the
`Tests to write (RED):` field names the contract slugs and a case cap no
larger than the number of contracts. The tester names the cases. A plan that
lists test names writes the suite twice, once in prose that nobody runs. The
grill template follows the new shape.

**grill-lint reads a spec's status from its frontmatter first**, as spec-lint
already did. The spec template's body line says "see frontmatter", so
grill-lint read every spec as live and asked the plan to cover the contracts
of a retired spec. It no longer does. A regression case holds the fix.

The owner ruled that the doctrine changes carry no tests of their own ("don't
write tests about when to not write tests"). The lints are their proof.

Rejected: a second home for anti-patterns the skill already owns, and the
plant's own measured evidence.

### Harvest log

```
# Harvest — from a grown plant — 2026-09-30
Harvested:   four rules on an over-budget test in the test-first skill;
             a contract-and-cap shape for a plan's RED field, with the
             template; a grill-lint fix with its regression case.
             No plant identity.
Generalized: plant names, paths, stack and counts stripped.
Rejected:    a second home for anti-patterns the skill already owns; the
             plant's own measured evidence.
Decided:     the owner ruled that the doctrine changes carry no tests of
             their own; the lints are their proof.
```

### Seed integrity gate (verdicts only)

- G1 agnosticism-floor: PASS
- G2 agnosticism-judgment: PASS
- G3 faithful-import: PASS after correction (two thinned passages restored; one skipped rule added by owner ruling)
- G4 availability: PASS
- G5 plant-untouched: PASS
- G6 self-consistency: PASS
- G7 clean-install: PASS
- G8 prose: PASS, genre exception recorded (the heading dash and the version arrow are the entry format)
- G9 minimum-sufficient: PASS
- G10 provenance: PASS
- G11 no-loosened-limit: PASS
- Version bump: 7.33.0 → 7.34.0
