---
name: review-rendered-ui
description: Verify a UI change by rendering every surface in both colour schemes at two widths, judging each render against the design baseline, turning each structural defect into a failing page test, and recording the renders as evidence. Invoke when only structure-level page tests have run on a UI change.
id: skill.review-rendered-ui
tier: 2
kind: skill
title: review-rendered-ui, a looked-at render as the evidence a UI change was seen
owns:
  - review-rendered-ui.render-matrix
  - review-rendered-ui.structural-defect-to-red
requires:
load_when:
  - "look at the rendered ui before calling it done"
  - "screenshot every page in light and dark mode"
  - "page tests pass but nobody has seen the render"
  - "visual review of the ui change"
prevents: A UI change is reported verified on structural page tests alone while the drawn page shows empty containers, a broken layout at one width, or flat type weight.
est_tokens: 1396
---

# Suggested skill: review-rendered-ui

> Optional procedure: a UI change is not verified until a real render of it has
> been looked at. Structure-level page tests over parsed markup pass against a
> tree no human has seen drawn; this procedure captures every surface rendered,
> in both colour schemes and at two widths, judges it against the design
> baseline, and turns each structural defect it finds back into a failing page
> test. Composes `protocols/verify.md` (the verification gate this is a required
> step of), `protocols/test-first.md` (a defect found here earns a RED before it
> is fixed), and `core/method/design-posture.md` (the baseline the render is
> judged against) by reference; it seeds no data (`skill-corpus/seed-demo-world-for-manual-ui-review.md`
> owns getting a reviewable instance populated, and runs before this). Parameterized
> by `<SURFACES>` (every page or screen of every client the product exposes),
> `<DESIGN_BASELINE>` (the mockups and design tokens to judge against), and
> `<RENDER_HARNESS>` (how a real render is produced: a headless browser, a
> device, a kiosk).

## When to apply

- A UI change is being verified and only structure-level tests (assertions over
  parsed markup, not a render) have run. Those tests passing is not done: they
  pass against a tree nobody has seen drawn, and the first renders routinely
  surface visual and template defects the structural tests cannot reach.
- A UI slice is about to be reported complete, or a design review is due.

## The one rule: a passing structural suite is not a looked-at render

Assertions over parsed markup prove the tree has the right shape; they say
nothing about what it looks like drawn. A suite of such tests can be green while
the rendered page shows a header-only table (a region whose rows never came), a
titled section with nothing under it, a broken layout at one width, or type that
reads as the same weight everywhere. "Green page tests" is therefore evidence
the structure holds, never evidence the UI was seen. This procedure is the step
that supplies the missing evidence.

## The procedure

### 1. Render every surface, in both schemes, at two widths

Capture `<SURFACES>`, every page of every client, rendered through
`<RENDER_HARNESS>`, each in the light and dark colour scheme and at a wide and a
narrow width. A surface missing from the set is a surface nobody verified;
enumerate them from the product's own routing, not from memory.

### 2. Judge each render against the design baseline

Compare each capture to `<DESIGN_BASELINE>`: spacing, colour, type, and layout
at each width. Two traps:

- **An empty container is a defect, not an empty state.** A table region with no
  rows, a titled section with nothing beneath it, a chrome element around absent
  content: each is a defect to record, because the structural test that built
  the container passed without ever asking whether anything filled it.
- **Judge type weight only under a font that carries the weight.** A render host
  whose fallback font has no bold face draws every weight the same, so a weight
  judgement made under such a fallback is meaningless. Confirm the intended font
  with its bold face is the one that rendered before grading emphasis.

### 3. Turn each structural defect into a RED

A defect that is structural (the container that renders empty because no code
path fills it, the section with no data behind it) is a gap in the page tests,
not only a visual blemish. Write the page test that fails on it, watch it fail,
then fix it (`protocols/test-first.md`): the render review found the hole, and
the suite that missed it gains the row that would have caught it. A purely
visual defect with no structural cause (a token value, a spacing constant) is
corrected against the baseline and re-rendered.

### 4. Record the renders as the evidence

The verification record (`protocols/verify.md`) carries that the renders were
looked at, at which schemes and widths, with the defects found and their
disposition: a fixed-and-re-rendered row, or a published one. A UI change whose
record shows only structural test counts is reported as unverified for render.

## Reference files

- `protocols/verify.md` (the verification gate this is a required step of, and
  where the render evidence is recorded)
- `protocols/test-first.md` (a structural defect found here earns a RED before
  it is fixed)
- `core/method/design-posture.md` (the baseline each render is judged against)
- `skill-corpus/seed-demo-world-for-manual-ui-review.md` (populates the
  reviewable instance this procedure then renders; runs first)
