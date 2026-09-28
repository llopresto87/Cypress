"""Rewrite §9 of a fixture plan as the scheduled fixture plan.

SPEC-0005 §6 "Wave report" names it: the valid plan `tests/test-grill-lint.sh`
builds (`write_plan`), with §9 replaced by five increments that carry a
`Phase:` field. The `GRILL_WAVES_*` cases start from it and change one field.

    python3 scheduled_plan.py <grill.md> [KEY=VALUE ...]

A KEY is a field letter and an increment number: `F3` is increment 3's
`Files touched:`, `D4` its `Depends on:`, `P1` its `Phase:` (an empty value
drops the field), `C2` its `Spec contracts:`, and `N3` the number its heading
carries (two headings may then carry one number).
"""
import sys
from pathlib import Path

INCREMENTS = [
    # n, title, phase, contracts, files, depends on
    (1, "Reject bad schemas", "RED", "SPEC-0001/REJECT_BAD_SCHEMA",
     "`tests/test_forms.py`", "none"),
    (2, "Validate schema", "GREEN", "SPEC-0001/REJECT_BAD_SCHEMA",
     "`src/forms/validate.py`",
     "increment 1; docs/graph/libraries/sqlalchemy.md"),
    (3, "Document the form", "prose", "none — prose",
     "`docs/forms.md`", "none"),
    (4, "Persist submissions", "RED", "SPEC-0001/SUBMIT_VALID_FORM",
     "`tests/test_store.py`", "increment 3"),
    (5, "Store submissions", "GREEN", "SPEC-0001/SUBMIT_VALID_FORM",
     "`src/forms/store.py`", "increment 2, increment 4"),
]

plan = Path(sys.argv[1])
edits = dict(a.split("=", 1) for a in sys.argv[2:])
text = plan.read_text()
start, end = text.index("## 9. Implementation Plan"), text.index("## 10.")

blocks = []
for n, title, phase, contracts, files, deps in INCREMENTS:
    phase = edits.get(f"P{n}", phase)
    lines = [
        f"### Increment {edits.get(f'N{n}', n)} — {title}",
        f"- Spec contracts: {edits.get(f'C{n}', contracts)}",
        f"- Files touched: {edits.get(f'F{n}', files)}",
        f"- Tests to write (RED): {'none — prose' if n == 3 else 'test_' + title.lower().replace(' ', '_')}",
        f"- Behavior added: {title.lower()}",
        "- Gate: unit tests",
        "- Rollback path: revert",
        "- Effort: low",
    ]
    if phase:
        lines.append(f"- Phase: {phase}")
    lines.append(f"- Depends on: {edits.get(f'D{n}', deps)}")
    blocks.append("\n".join(lines) + "\n")

section = "## 9. Implementation Plan\n\n" + "\n".join(blocks) + "\n"
plan.write_text(text[:start] + section + text[end:])
