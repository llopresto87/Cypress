# Suggested skill: deploy-gated-red-green

> Optional procedure: run the RED → GREEN discipline when the only oracle that
> can observe a contract is a deployed system and every deploy costs something.
> `protocols/test-first.md` owns the cycle, the rule that a failing test
> authorizes each change, and the recorded exceptions; `protocols/verify.md`
> owns the gate states, the runbook rule that the red is recorded before the
> green, and the lower-bound rule for a harness that stops at its first failing
> assertion; `core/method/delegation-cycle-economy.md` owns the tip cadence
> (the full run once, at the batch tip). This page adds what none of them
> carries: the explicit choice between a deploy per increment and a single
> deploy, the order of a single-deploy cycle, the exception for a contract that
> can fail only after an earlier deploy, and the rules for the synthetic data
> such checks leave behind. It composes all of them by reference.
> Parameterized by `<TARGET>` (the deployed system the owner authorized for
> live checks), `<DEPLOY_COMMAND>`, `<HARNESS>` (the black-box check runner),
> `<GROUPS>` (one group of checks per increment), `<STATIC_CHECKS>` (one
> structural source check per increment), `<SYNTHETIC_PREFIX>` and
> `<RUNBOOK>` (the verification runbook).

## When to apply

All three of these hold:

- **The contract is observable only on a deployed build.** The project has no
  in-process test framework and the owner has ruled against adding one (for
  example a "no new dependencies" decision), or the contract sits at a seam
  only the running deployment exercises: a security proxy, the routing table,
  persistence behaviour behind a framework.
- **No cheaper oracle exists.** A local stack was assessed and found
  impractical, and the reason is recorded (the tool is not installed on the
  operator machine, a second deployment on the shared host breaks a
  one-deployment-per-host rule). If a local stack or an in-process harness is
  available, use it and run `protocols/test-first.md` unchanged.
- **Each deploy has a real cost**: wall time, a rebuild, an approval, downtime
  on a host other people use.

The procedure is an exception to the per-increment RED, so it is recorded as
one: an entry in the plan's exceptions section (grill.md §9) with its
rationale, the date, the owner's decision it rests on, and its residual risk,
as the exceptions section of `protocols/test-first.md` requires.

## 1. Choose the mode explicitly, before any check is written

There are two modes. Write the choice into the spec as a reversible decision
and mirror it into the plan, because every later step depends on it.

- **Mode P: one deploy per increment.** Each increment closes locally, deploys,
  and runs its own behavioural GREEN while the later groups run RED. This is
  the ordinary cycle with a deploy inside it.
- **Mode S: one deploy at the end.** Behavioural RED is collected once,
  against the live pre-fix build, before any production change. Each increment
  closes locally by compile plus its static check. One deploy follows, then one
  GREEN run over every group. The per-increment authorization then holds
  behaviourally only in aggregate, and the record says so.

Weigh three things, and write down the value of each:

| Factor | Points to Mode S | Points to Mode P |
|---|---|---|
| Cost of one deploy | high: a full rebuild, an approval per deploy, downtime others notice | low: a fast pipeline, no approval per deploy |
| Blast radius of a bad deploy | bounded: one service, a throwaway or staging target, a rollback point recorded and cheap | wide: shared infrastructure, real users, a rollback that is slow or untested |
| Contracts that can go RED only after an earlier increment is deployed | none, or few, and each has a static check plus a GREEN assertion strong enough to stand alone | several, or any in a security, data-integrity or money contract |

Two more facts belong in the decision:

- **What Mode P's intermediate runs leave behind.** A RED run against a
  partly fixed build can write records that no API can delete and that every
  user of the target then sees (a synthetic entry in a shared catalogue or
  dropdown, for example). Mode S avoids those writes at the price of the
  exceptions in step 7.
- **What the deploy authorization covers.** An approval for one deploy to one
  host after the local gates are green does not cover five.

The owner makes the call. Mode S stays reversible: Mode P can resume at any
later deploy.

The rest of this page is the Mode S procedure. Under Mode P, steps 2 and 3
run as written, and steps 4 to 6 repeat once per increment, each deploy
followed by a run with the landed groups in `--green` and the rest in `--red`.

## 2. Build the harness and the static checks first

Before any production file changes, the tester builds two tools. This is test
tooling only. It replaces "write the failing test", which the project cannot
run in-process, and clears the gate "the harness exists and the static checks
are RED for the right reason".

**`<HARNESS>`, the black-box checks**, grouped by contract, one group per
increment. Each run names which groups it runs RED and which GREEN. A portable
skeleton of such a harness, with its verdict model, secret handling and
self-test, is `tool-corpus/testing/live-contract-check-harness.md`. The
properties this procedure relies on:

- A group listed in both the RED and the GREEN set is a usage error. Unlisted
  groups are skipped, and the guards of a listed group always run.
- Each check reports exactly one verdict, from the verdict table on the tool
  page. This procedure reads three of them: `RED-OK` (the expected RED),
  `RED-UNEXPECTED-GREEN` (the check does not discriminate, so the run fails)
  and `NOT-EXERCISED` (a precondition was absent; never a pass).
- **Guards** are checks that already pass on the pre-fix build and must keep
  passing. They protect existing behaviour and authorize no code.
- Each check carries the status the spec documents for it today. When a RED
  run observes a different one, the harness warns of spec drift and the
  session routes it to the architect instead of editing the expectation.
- An offline plan mode prints what would run with no network and no
  credentials. The exit code separates green, failed, and aborted before any
  request was sent.
- A preflight resolves every id the checks need at run time (the principals'
  permissions, a known subject, an id guaranteed not to exist) and aborts the
  run before any check if one is missing.
- Credentials come from the environment only, never from an argument or the
  output. A token the harness obtains may travel in a private file inside a
  private work directory, which is a transport and not a source; the tool page
  carries those mechanics. Where the target counts failed logins, each principal logs in
  exactly once per run with no retry, so a wrong password cannot lock the
  account. The checks run from the operator's machine, not on the target host.

**`<STATIC_CHECKS>`, one per increment**, a structural check over the source
(a pattern match on the construct the fix adds). It pins code structure, not
behaviour, and it is RED now: the target file exists and the construct is
missing. Where a fix has a fail-open variant (an always-true authorization
expression, a catch-all that swallows the error), the check rejects that
variant by name. A check name the script does not know fails rather than
passing silently. Prove each static check bites by mutating a scratch copy
(`skill-corpus/mutation-verify.md`, "mutate by copy"). A static check over
the harness itself, for its secret-handling rules, belongs here too (the tool
page's companion lint is one).

Record in `<RUNBOOK>`: the static RED with each failing check named, the
dispatch and usage-error outcomes, and the offline plan. The live gates stay
`absent` in `protocols/verify.md`'s terms until they first run.

An increment with no possible static check has no per-increment RED at all.
Its only RED is the baseline run in step 3. Name that in the residual risk.

## 3. Collect the behavioural RED once, against the live pre-fix build

Run `<HARNESS>` with every group that can be RED today in `--red`, against the
deployed build, before any production change. This one run replaces the
per-increment behavioural RED and clears the gate "every non-guard check
`RED-OK`, every guard `PASS`, no `RED-UNEXPECTED-GREEN`".

- Leave out a group whose subject cannot exist on the pre-fix build (a check
  that edits a record only the fix can create). It could only report
  `NOT-EXERCISED`. That group falls under step 7.
- Print and record the run start in UTC. Where the defect leaves a signature
  in the server log, count it since the run start: at least one match now,
  zero after the fix. This second oracle tells a product failure from a check
  failing for an unrelated reason, such as a fixture that triggers a different
  error.
- **A `RED-UNEXPECTED-GREEN` blocks.** The check passes against the defect it
  is named for, so it is not evidence. Fix the check, and watch it fail,
  before any production change.
- **Interlock a RED request that would damage real data once the fix is
  live.** Send it only when an earlier check in the same run has confirmed the
  pre-fix state (for example, the read that the fix unblocks still returns
  403). Otherwise report it skipped. Prove such a contract's GREEN by
  composition: the gate that the earlier check proves open, plus the same
  operation on a synthetic subject.
- Record the full output in `<RUNBOOK>`, with the run start and what the run
  wrote, before any production file changes.

## 4. Close each increment locally, in plan order

Each increment goes through the cycle in `protocols/test-first.md` with one
substitution: its RED is its static check (step 2) plus its group's `RED-OK`
rows from step 3, and its local GREEN is the compile plus that static check
going from FAIL to PASS. No deploy happens here. This replaces the
per-increment deploy and clears the gate "compile passes, this increment's
static check passes". REVIEW and COMMIT run as the protocol says.

## 5. Run every local gate, then take a rollback point

Before the deploy, run the full compile, every static check (no argument
selects all), and the graph lint, all green. Then record the identity of the
artifact now running on `<TARGET>` and give it a name the deploy will not
reuse. A rebuild under the same name otherwise leaves the old artifact
reachable only by an identifier nobody wrote down. The restore point
discipline is `core/method/release-posture.md`'s. Rolling back needs the
owner's explicit go-ahead, and fixing forward is tried first
(`core/method/incident-posture.md`). A rollback does not remove synthetic
records the checks wrote.

## 6. Deploy once, then run one GREEN over every group

Run `<DEPLOY_COMMAND>` with its own smoke stage. Then run `<HARNESS>` with
every group in `--green`. This is the batch tip of
`core/method/delegation-cycle-economy.md`, and it clears the gate "every
check `PASS` or a recorded `NOT-EXERCISED`, no `FAIL`, no
`RED-UNEXPECTED-GREEN`, exit 0". Count the log signature again since the
GREEN run started: zero. Where a contract is visible only in a UI, add the
operator's manual observation. Record in `<RUNBOOK>`: the rollback point,
both runs, the log counts, and the ids of every synthetic record created.

**When a check fails here, judge the instrument first**
(`protocols/verify-disagreement.md`). Repeat the failing request by hand,
built as the real client builds it. If the product behaves as the contract
says, the defect is in the harness: fix it, re-run the same group, and record
the defect in `<RUNBOOK>` so nobody trusts that check before it is fixed. If
the product is wrong, do not redeploy blind. Route the failing group to its
increment and fix forward: the failing GREEN is that increment's new RED.
Report the run as failed until the corrected run is green.

**Observed in practice: the checks that never ran RED are where the harness
defects surface.** In one run of this procedure every product contract held,
yet the GREEN run failed exactly on the step-7 checks. Their first live run was the
GREEN. One of them built its write request by reading the record back and
sending it again, and the read response omitted the identifier the write
needed (the real client set it from its own state). No upstream
documentation speaks to this; it is a property of the procedure, and the
defence follows from it:

- Exercise the setup path of every step-7 check before the deploy: run its
  reads against the pre-fix build on any subject that already exists there,
  and confirm the response carries every field the write will need.
- In the harness, a request body built from a read asserts the fields it
  depends on, and a missing one is reported as a harness error, not as a
  product `FAIL`.
- Build each request the way the real client does, not from what the read
  endpoint happens to return.

## 7. A contract that can go RED only after an earlier deploy

Under Mode S, a check whose subject exists only once an earlier increment is
deployed has no behavioural RED. Do not hide it. Name it as an exception in
the plan's exceptions section, with:

- the contracts it covers and why their RED cannot be observed (the subject
  cannot exist on the pre-fix build);
- the residual risk in words: these checks are shown able to pass, not shown
  able to fail;
- the mitigations, each named: a static check that pins the construct the fix
  adds, and a GREEN assertion strong enough to stand alone (for a rejected
  request, assert that the state is unchanged afterwards, which shows the
  check runs inside the transaction and the rollback happened);
- the way to recover the RED later. At a deploy that happens anyway, the RED
  can be recovered after the fact (`skill-corpus/prove-red-after-green.md`).
  Mode P observes it directly.

Collect every unverifiable item in a "what cannot be verified" list in the
spec, beside the test mapping: no guard runs between deploys; contracts
stated at an in-process seam verified only through their external consumer;
data-dependent checks that may report `NOT-EXERCISED`; principals the
environment cannot supply; side effects the external interface cannot see.
Each item names the check that partly covers it, or says that none does.

## 8. Synthetic data: a fixed prefix and a named cleanup decision

Everything the checks write is synthetic
(`core/method/stewardship-posture.md`), never a copy of a real record.

- Every created record carries `<SYNTHETIC_PREFIX>` plus the run's UTC
  timestamp, so a person or a query can find every leftover. Contact fields
  use a reserved domain (`example.invalid`). A generated password comes from
  a cryptographic random source, is never printed, and is discarded at exit.
- Prefer a synthetic subject for any check that edits. When a check must
  tamper with a pre-existing record because no synthetic one exists, it sends
  a restoring request the moment its assertion fails and reports the restore
  outcome with the `FAIL`.
- Before the first run that writes, state what the runs leave behind and
  where a person using the target will see it. If no interface deletes those
  records, put the choice to the owner as a decision, recorded in the spec:
  (a) accept the leftovers and record their ids in `<RUNBOOK>`; (b) authorize a
  prefix-scoped cleanup after the final GREEN as a separate, named operation,
  since a cleanup by prefix is destructive and needs its own go-ahead; or (c)
  choose the mode whose runs avoid the write and accept its exceptions.

## Reference files

- `protocols/test-first.md` (owns the cycle this page adapts, the rule that a
  failing test authorizes each change, and the exceptions section where this
  procedure and its step-7 exceptions are recorded)
- `protocols/verify.md` (owns the gate states, the runbook rule that the red
  is recorded before the green, and the lower-bound rule for a harness whose
  first failing assertion hides the rest)
- `protocols/verify-disagreement.md` (a check that disagrees with its subject
  indicts the instrument first; step 6's triage)
- `core/method/delegation-cycle-economy.md` (the tip cadence: one full run at
  the batch tip, which the single GREEN is)
- `core/method/release-posture.md` (the restore point captured before the
  change; step 5)
- `core/method/incident-posture.md` (fix forward first; reversal only on an
  explicit confirmation)
- `core/method/stewardship-posture.md` (test data is synthetic, never
  production)
- `skill-corpus/mutation-verify.md` (proving a static check bites, by
  mutating a scratch copy)
- `skill-corpus/prove-red-after-green.md` (recovering the RED of a step-7
  contract after the fact)
- `tool-corpus/testing/live-contract-check-harness.md` (a portable
  `<HARNESS>`: RED and GREEN groups, the verdicts of step 2, a preflight
  abort, one login per run, the secret-handling rules and their static lint)
- `tool-corpus/testing/http-smoke-suite.md` (the smoke stage a deploy runs
  before the GREEN; it shows the service is serving and encodes none of the
  spec's contracts)
