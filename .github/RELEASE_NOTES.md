## 8.5.1 — the worth check spares by what a plant declares (2026-11-11)

8.5.0 left five things short, and the owner asked on 2026-11-11 for each to be
closed in a point release. The worth check chose which tests to spare from the
words in a test's name, comments and identifiers, so a plainly named security
test could be flagged and a test whose name only claimed a regression passed.
A few loaded prompts and method lines still carried sentences the 8.5.0 rule
had replaced. On opencode no launch list named `legal`, so the architect's own
legal checkpoint could not spawn it. The OpenCode plugin's fixture cases ran in
no CI job. And the token ledger's transcript reader had been checked against
hand-written transcripts only. The plan of record is
`docs/plans/grill-8.5.1-follow-ups.md`.

The kernel is 7043 bytes, and the always-loaded surface on Claude Code and
opencode is 67065 bytes, as in 8.5.0; no always-loaded file grew. Measured on a
fresh install, the composed prompts are 41387 bytes for the architect (41589
in 8.5.0), 42944 for the tester (42960), 47902 for the reviewer (47914), 44845
for the orchestrator (unchanged) and 58985 for the implementer (58991).

### The worth check spares by declaration

The owner decided on 2026-11-11 that the worth check spares a test by what the
plant declares about it, and uses its word list only where the plant declares
nothing (SPEC-0009).

- **A §10 row decides first.** A test whose row has origin `bug` or
  `security control` is spared. A row with any other origin decides alone, so
  the test's name no longer spares a test a §10 row maps.
- **A marked trust path spares the tests that reach it.** A test that reads or
  imports a file on one of the plant's marked trust paths is spared. The check
  finds those files through the plant's source index and
  `graph-lint.py --trust-claims`. When it cannot consult them, the run prints
  `trust paths not consulted: <reason>` and falls back to the word list.
- **The word list is the fallback.** It applies to a test with no §10 row, and
  its security words only in a plant that marks no trust path. The words role,
  lockout, origin, allowed and jwt joined it as a stopgap.
- **What the check cannot see is `not judged`.** An assertion inside a helper,
  a comparison with a golden file and a snapshot were spared in 8.5.0 as
  documented limits. They are now listed as `not judged` and counted with the
  not checked, so the delivery record's `Not checked by worth check` count
  includes them.
- **The failure message offers the remedies first.** It names the keep line,
  strengthening the test, recording its §10 row and marking the trust path, and
  says that a trust-path, bug-origin or security-control test is never removed
  to clear a flag. It never leads with removal.
- **`--removal-list` holds every test back**, with the reason, when the plant's
  trust paths were not read in full or a spec could not be opened, because it
  cannot then tell which tests sit on a trust path.
- **An independent security review** of the change on 2026-11-11 found one
  blocking issue: the removal list offered a trust-path test for removal while
  the trust paths could not be read. It was fixed and re-verified; the
  re-verification found that an unreadable spec let the same thing through, and
  that was fixed too. The security sign is given.
- **Three limits are accepted.** A deleted baseline is written afresh by the
  next `--write-baseline`, and only the diff of the tracked file shows it
  (detective). A test the source index reaches only through its floor is
  spared, and its reason names the test's own path. In a plant that marks trust
  paths, a security test off those paths with no §10 row is flagged; the keep
  line, or its §10 row, is the remedy.
- **The spec lint reads a §10 Test cell as the worth check does.** It accepts
  a TypeScript title with spaces and a `./`-prefixed path; every existing spec
  lints byte for byte as before. `spec-lint.py` is a graph engine that only
  gains here, and it reaches an existing plant through graft's engine
  reconciliation alone, with nothing of the plant's for graft to preserve.

### Retired sentences leave every composed prompt

The owner decided on 2026-11-11 that the sentences the 8.5.0 rule replaced
leave every composed prompt. `method.engineering-posture` §2 now says that
logic waits on a failing test and that a declarative or presentational
contract is proved by its declared run or review.
`delegation.green-self-test` says the implementer writes production files
alone off the merged path. The tester's and the reviewer's charters name the
always-loaded rule without saying where it sits in the prompt. A search found
three more lines, in the architect's charter, `protocol.from-scratch` and
`protocol.test-first`, and each was rewritten.

A `FORBIDDEN` table in `tools/delivery_rules.py`, beside the must-reach table,
keeps the retired sentences out. `install.sh <host> --check` reads it over a
plant's agents, the seed's gate over the composed agents, and a `--tree` mode
over the seed's method source.

### `legal` is launchable on opencode

The method's legal checkpoint has the architect spawn `legal`, so the
architect's `delegates_to` now names it. A roster check in
`tools/roster-justification.py --gaps`, in the same gate step, fails an agent
that no list names unless its frontmatter says
`launched_by: none  # <reason>`.

An existing opencode plant receives the new list on re-install: the architect's
charter is seed-owned, so it is fast-forwarded with a backup, and
`.opencode/agents/` is regenerated. A plant that kept its own architect charter
through graft adds `legal` to that charter's `delegates_to` and runs
`install.sh opencode --recompose-agents`.

### The plugin's cases run in CI, and the gate names a part it skipped

The owner decided on 2026-11-11 that at least one CI job runs the plugin's
fixture cases. A new job, `opencode-plugin` in `.github/workflows/gate.yml`,
installs one bun release checked against a recorded checksum and runs the
plugin's behaviour cases with `CYPRESS_REQUIRE_BUN=1`, which fails the job
where bun is missing instead of skipping the cases. A gate step that skips part
of itself prints `SKIPPED-PART: ...`, and the gate summary names it
(`N passed in part: <step> (<what was skipped>)`). The job has not run on
GitHub yet: it was run by hand on Linux, and the cases passed under bun 1.3.14.
This is seed-only and places nothing in a plant.

### The token ledger's reader, checked on real transcripts

On 2026-11-11 the reader was run over three real Claude Code subagent
transcripts, of 7, 52 and 151 messages, and its sums equalled an independent
computation. A redacted real transcript is now a fixture (X950), seen red
against a reader that counts every record. The one-hour cache-write path was 0
in all three, so the hand-written case alone still covers it. Billing is not
verified. This is seed-only and places nothing in a plant.

### What an existing plant does to receive this release

- **Re-install** brings the charters, the method nodes, `worth-check.py` and
  the other placed tools, with each replaced seed-owned file kept as a
  timestamped backup.
- **Graft** brings `spec-lint.py`, whose one change is the Test cell rule above,
  through its engine reconciliation; `grill-lint.py` is unchanged.
- **Shape:** nothing. No spec or plan form changed, so no plant file needs a
  migration.
