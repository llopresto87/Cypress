---
id: method.security-controls
tier: 2
kind: method
origin: seed
title: security controls — the adversarial negative controls a security contract's RED writes and the security pass confirms
owns:
  - security-controls.checklist
requires:
peers:
  - protocol.test-first
load_when:
  - "negative control, evasion class, bypass the static rule"
  - "disabled action reachable by another path, every path to the effect"
prevents: A security contract that goes green on the controls the spec plants while its rule is still evadable by an alias, a helper, a string-built name or a comment, or its disabled action is still reachable by another path.
est_tokens: 400
---

# Security controls

A security contract's RED writes these controls, and the security pass
confirms them (`test-first.security-path`). `brief.py` embeds the block below
byte for byte in a security brief and in any brief composed with
`--security-path`.

```
SECURITY PATH
RED: for each security contract, write one negative control per class below that applies, and record "n/a: <why>" for each other class.
1. An import or alias rename of the guarded name.
2. A helper, wrapper or factory call that reaches it indirectly.
3. A string-built or reflective name.
4. The allowed shape present only inside a comment or a string.
5. Line terminators other than \n: CR, CRLF, U+2028, U+2029, NEL, in comments, strings and scanned code.
6. An unpinned value where one value is allowed: prefix and suffix extensions, case variants, extra fields or parameters.
For a contract that disables or gates an action, write one test per path to the action's effect, found from the effect's callers (confirm, retry, back or resume, resize, deep link, callback, a race), beyond the widget the spec names. Paths include every input channel (pointer, keyboard, assistive technology) and every state change between enabling and effect (resize, recreation).
Security pass: confirm each control and each path test exists and fails when its guard is removed; a class with neither a control nor an n/a reason, or a path to the effect no test covers, is a finding. A bypass counts once you have run it; report each attempt, blocked or bypass, with the test that pins it.
```
