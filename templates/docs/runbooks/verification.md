# Verification

The verification gates for this project. Every gate has an exact
command and an expected outcome.

## Gates

| Gate | Command | Expected outcome |
|---|---|---|
| formatter   | `<cmd>` | exit 0, no diff |
| linter      | `<cmd>` | exit 0, no warnings above threshold |
| type check  | `<cmd>` | exit 0 |
| unit tests  | `<cmd>` | exit 0, N cases pass |
| integration | `<cmd>` | exit 0 |
| build       | `<cmd>` | artifact produced |
| smoke test  | `<cmd>` | deployed system responds 200 to `/health` |
| eval suite  | `<cmd>` | rubric score >= gate threshold |

## Per-increment records

### Increment <title> (YYYY-MM-DD)
- Formatter: `<command>` — PASS
- Linter: `<command>` — PASS
- ...

<!-- Append a section per increment as it ships. -->
