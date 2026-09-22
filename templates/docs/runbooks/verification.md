# Verification

The verification gates for this project. Every gate has an exact
command and an expected outcome.

## Gates

| Gate | Command | Expected outcome | Trusted since |
|---|---|---|---|
| formatter   | `<cmd>` | exit 0, no diff | `<date>` |
| linter      | `<cmd>` | exit 0, no warnings above threshold | `<date>` |
| type check  | `<cmd>` | exit 0 | `<date>` |
| unit tests  | `<cmd>` | exit 0, N cases pass | `<date>` |
| integration | `<cmd>` | exit 0 | `<date>` |
| build       | `<cmd>` | artifact produced | `<date>` |
| smoke test  | `<cmd>` | deployed system responds 200 to `/health` | `<date>` |
| eval suite  | `<cmd>` | rubric score >= gate threshold | `<date>` |

`Trusted since` is the date this gate was last shown to fail for the reason
it claims to guard against. A gate with no such date has authorized nothing,
whatever it has been printing.

### When a gate is found to have been vacuous

A gate discovered to have been wired to the wrong artifact, run against an
empty input set, or otherwise incapable of failing did not merely stop
working — it was never working, and every green it reported was a claim about
nothing. Fixing the wiring silently leaves those greens standing as evidence.

Record the finding next to the gate, and never only in the commit that fixed
it:

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

## Per-increment records

### Increment <title> (YYYY-MM-DD)
- Formatter: `<command>` — PASS
- Linter: `<command>` — PASS
- ...

<!-- Append a section per increment as it ships. -->
