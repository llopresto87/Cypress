---
name: test-first
description: A synthetic stack-keyed skill page whose destination the seed's own skills/test-first node takes; used only to prove the preflight refuses it.
id: skill.test-first-corpus
tier: 2
kind: skill
title: test-first, a synthetic page that collides with a seed skill node
owns:
  - test-first-corpus.steps
requires:
load_when:
  - "a synthetic collision the corpus-placement cases refuse"
stack:
  - library-corpus/npm/unmatched-lib
est_tokens: 80
---

# Suggested skill: test-first

> A synthetic page. Its destination is a node the seed itself places.
