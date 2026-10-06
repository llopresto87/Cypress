---
name: lumen-upgrade
description: A synthetic stack-keyed skill page for the corpus-placement cases; upgrades the lumen-core library.
id: skill.lumen-upgrade
tier: 2
kind: skill
title: lumen-upgrade, a synthetic stack-keyed procedure used only by the corpus-placement cases
owns:
  - lumen-upgrade.steps
requires:
load_when:
  - "upgrade the lumen-core library"
stack:
  - library-corpus/maven/lumen-core
est_tokens: 150
---

# Suggested skill: lumen-upgrade

> Optional procedure, keyed under `maven/`.

## When to apply

The plant's build declares the library this page's `stack:` field names.

## Procedure

1. Read the library page it names, then upgrade one module at a time.
