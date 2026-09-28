<!--
Template: docs/plans/sessions/_session-record.template.md
Lives at: docs/graph/plans/sessions/<YYYY-MM-DD>-<slug>.md, one record per
unit of work. The date is the day the unit's first session started; the slug
names the unit of work, lowercase with hyphens. A session that resumes the
unit appends to the same record.
Written by: the orchestrating session only, at the moment it learns each
item. Workers write none; they hand back. The docs-librarian appends only to
"Canonize status", at close-out.
Home of the rule (what counts as a learning, when to write it, reading the
newest record at session start): method.stewardship-posture
(stewardship-posture.session-record). How each item is filed:
protocol.canonize (canonize.session-record).
A record has no frontmatter and no status: key. It is working state, like
grill.md, and is not routed. Append only: correct an item with a new item
that names the one it corrects, and add a dated block to "Open threads"
instead of editing the last one. Never write a secret, a credential,
production or personal data, or speculation.
The leading underscore keeps this blank form out of the linters and audits;
the record you copy it to must not carry one.
-->

# Session record: <YYYY-MM-DD>, <unit of work>

<one line: the plan-of-record or task this record serves>

## Owner rules

### <n>. <the rule, as an instruction> (<YYYY-MM-DD>)

> "<the owner's words, verbatim, in the language they used>"

How it applies: <one short paragraph>

## Corrected assumptions

- <what was believed, and where it was written> → <what is true>; evidence: <path, command or commit>

## Open threads

### As of <YYYY-MM-DD>

- <where paused work stands; what comes next; what waits on whom>

## Harness memories to migrate

| Entry | Gist | Likely home |
|---|---|---|

## Canonize status

(Appended by the docs-librarian at close-out, one line per item.)

- <the line `python3 docs/graph/code-anchor.py --record` printed, `Code anchor recorded <UTC>: ...`, or its stderr line on a refusal>
