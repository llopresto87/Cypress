### Slice 12 — Inventory drift closed at the mechanism (U-22, partial)

**Tier:** T2. **Invariant:** X7.

`manifest.json` cataloged 8 of the 10 top-level templates. `agent.template.md`
and `skill.template.md` were missing while README, the orchestrator charter,
`core/method/delegation.md` and three reference documents all told a reader to
use them.

The omission survived because `seed-lint.py` only ever asked "does what the
manifest claims exist?" — never "is what exists claimed?". The `agents[]` section
had the check both ways from the start; `protocols`, `skills` and `templates`
inherit it now, and it was proved to fail by removing one entry. Only the top
level of `templates/` is compared: `templates/docs/**` is a scaffold tree the
manifest catalogs as a single directory entry on purpose, and enumerating its
~28 leaves would be a second home for that list.
