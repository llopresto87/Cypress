# Evidence record: method overhead on one small task

The record behind the overhead figure in the README's cost section. It carries
the outcomes of the one measurement, the method, the date and the seed
revision, and nothing else.

- **Figure:** 11% more tokens per task: 131 583 tokens with the method's brief
  against 118 973 tokens without it, on one task, run once in each condition.
- **Other outcomes:** the same run took 72 tool calls with the method against
  60 without it (20% more), and 12m 40s of wall clock against 10m 32s (20%
  more). Both runs fixed all three linters. Only the run with the method showed
  a red-before-green proof for each fix. The run without the method found a
  fourth linter with the same defect, which the run with the method did not,
  because its brief named three.
- **Conditions:** one task, run once in each condition, by one model class. The
  task was small, well localized and highly specified. The measurement ends at
  the first delivery and does not speak to larger work.
- **Method:** one small, well-specified task (three linters answered an
  unreadable file by skipping it silently; make each report and fail, and add a
  test) was run twice from the same starting revision by the same model class.
  One run received a brief carrying the method; the other received a five-line
  description of the defect and no method. Each ran in its own isolated working
  tree, and the token totals were compared. The full account, with its
  conditions, is [slice 15 of the 7.15.0 remediation plan](../grill-7.15.0-remediation/slice-15-what-a-t3-costs-measured-u-17.md).
- **Date:** not recorded to the day. The runs started from a revision committed
  on 2026-09-13, and the result was recorded in the 7.16.0 release on
  2026-09-15.
- **Seed revision:** `d7588e2`
