---
name: example-stack-procedure
description: A fixture of a stack-keyed suggested skill. seed-lint's cases copy it under skill-corpus/maven/ to prove a nested page is scanned and its stack field is checked.
id: skill.example-stack-procedure
tier: 2
kind: skill
title: example-stack-procedure, a nested skill-corpus page used only by the seed-lint cases
owns:
  - example-stack-procedure.steps
requires:
load_when:
  - "a fixture task names the example stack procedure"
stack:
  - library-corpus/maven/spring-boot
est_tokens: 200
---

# Suggested skill: example-stack-procedure

> Optional procedure, keyed under `maven/`. It specializes
> `skill-corpus/framework-version-migration.md` by reference and adds only the
> steps the keyed library needs.

## When to apply

The plant's build declares the library this page's `stack:` field names.

## Procedure

1. Read the generic page it specializes, then the library page it names.
2. Run the one step this fixture stands for, and name the gate it clears.

## Reference files

- `library-corpus/maven/spring-boot.md`
