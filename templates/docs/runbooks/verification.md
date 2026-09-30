# Verification

The verification gates for this project. Every gate has an exact
command and an expected outcome.

## Gates

List only the gates the project's blast radius calls for
(`test-first.proportionate-checks`); a row is added by owner decision.

| Gate | Command | Expected outcome | Trusted since |
|---|---|---|---|
| `<gate>` | `<cmd>` | `<exit status and what it asserts>` | `<date>` |

`Trusted since` is the date this gate was last shown to fail for the reason
it claims to guard against. A gate with no such date has authorized nothing,
whatever it has been printing.

### When a gate is found to have been vacuous

A gate discovered to have been wired to the wrong artifact, run against an
empty input set, or otherwise incapable of failing did not merely stop
working: it was never working, and every green it reported was a claim about
nothing. Fixing the wiring silently leaves those greens standing as evidence.

Record the finding next to the gate, where its next reader looks:

- Gate: `<name>` — vacuous from `<when it was introduced or last verified>` to
  `<when it was caught>`
- How it passed without asserting: `<the wiring, the empty input set, the
  stale artifact it was reading>`
- What the greens in that window did and did not cover: `<the property nobody
  was actually checking>`
- Re-established by: `<the planted violation that turned it red, dated>`
- What else reads the same way: `<any gate sharing the wiring, input set or
  assumption — checked, or recorded as not checked>`

Then move this gate's `Trusted since` to the new date. The window is the
useful artifact: it is the list of increments whose verification record now
has a hole in it.

### When a gate is always red for a reason unrelated to what it guards

Why this is a defect and when to file it: the chronic red in
`protocol.verify`, Workflow item 5. Record it here, next to the gates.

- Chronically red: `<gate>`: red since `<when>` for `<reason unrelated
  to the property>`; owner `<who>`

## Per-increment records

### Increment <title> (YYYY-MM-DD)
- Baseline of record: `<the tree unmodified: each check already failing
  before this increment, by name>`
- Formatter: `<command>` — PASS
- Linter: `<command>` — PASS
- ...
- Pre-existing, named and not absorbed: `<each failure this increment
  found and did not cause, reproduced, left untouched>`
- Absent / carried (recorded, not faked green): `<each check not run or
  weaker than it should be, and why, including "not verified against a
  running system" where that holds>`
- Mutation register (where mutation was run): `<mutants killed / alive>`;
  control `<the mutant that must stay alive, and did>`; withdrawn
  `<any mutant ruled out, and why; for example it broke the parse rather
  than the behaviour>`

<!-- Append a section per increment as it ships. -->
