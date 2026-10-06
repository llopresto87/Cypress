# Tool: chained-pipeline-run-driver

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the refusal
> vocabulary, the retry/idempotence split, and the progress-visibility contract
> are portable; the transport that talks to the hosted CI/CD platform's REST or
> CLI surface is vendor-specific and is written against whatever platform the
> adopting project uses. Composes `skill-corpus/drive-hosted-cicd-cli.md`
> (session login, the two-branch trap, run-by-id proof) by reference and
> restates none of it; this page's subject is chaining two runs together and
> staying honest about a long wait, not authenticating or ref-proving.

## 0. Identity

- **Category:** ops
- **Name:** chained-pipeline-run-driver
- **Language / runtime:** any (a client for the platform's queue/wait/download
  calls, or a wrapper over its CLI, is the whole requirement)
- **Stability:** **blueprint**: no portable implementation, because the
  client that queues and polls a named platform's runs has no stack-neutral
  form. Everything above that client (the allow-list, the refusals, the
  retry split, the progress contract) is portable and is the value of the
  page.

## 1. What it does

Drives a **two-stage pipeline chain** on a hosted CI/CD platform: queue the
first named pipeline, wait for it, and, only if it succeeded, queue a
second named pipeline **bound to the first run's own id**, wait for that,
download its artifacts, and print a status-only summary. It exists to retire
the hand-run version of this chain: a developer or an on-call engineer
re-typing the same queue/wait/queue/wait/download sequence from a scratch
script every time the chain must run, with no consistent refusal or progress
behavior between one occasion and the next.

It also carries an **attach mode**: bind to an already-queued first run
instead of queueing a new one, for re-attaching a summary/download pass
without re-running work that already happened.

**When not to use it.** It is not a general client for the platform: it
knows only the pipelines on its allow-list and the one chain between them.
Do not queue a real run "just to see" what the tool would send; `--dry-run`
prints the resolved request and exists for exactly that. And do not point it
at a production target; it refuses those by construction (§3).

## 2. Interface & invocation

```sh
chained-pipeline-run \
  --pipeline-a <name> --pipeline-b <name> \
  --self-ref <ref for pipeline A> [--params <key=value,...>] \
  [--attach-run-id <existing pipeline-A run id>] [--first-only] \
  [--is-release <true|false>] [--out <dir>] \
  [--poll-interval <seconds>] [--max-polls <count>] \
  [--net-retries <count>] [--net-retry-sleep <seconds>] \
  [--request-timeout <seconds>] \
  [--dry-run]
```

- **Inputs:** an **allow-list of named pipelines** (never a bare id on the
  command line — see §3); the ref pipeline A runs against; parameters for the
  queue call; poll/retry bounds; a credential read from the environment only,
  never on argv, never printed.
- **Outputs:** at start, the worst-case wait the configured bounds allow
  (§3); one line per pipeline naming its run id and terminal state; a
  progress line on the first poll and on every observed state change (never
  silent — see §3); downloaded artifacts under `--out`; a summary that prints
  **status only** — id, terminal state, and a named reason on failure — and
  never the content of what the run produced.
- **Exit codes:** a closed vocabulary. 0 both runs (or the one run in
  `--first-only`) succeeded; 1 a run did not succeed; 2 a hard refusal fired
  (§3) or a usage error (missing required flag, malformed parameters); adding
  an outcome means adding a code, not overloading one.
- **Preconditions:** network reach to the platform; a credential with
  permission to queue and read both named pipelines.

## 3. Approach / algorithm

### A closed allow-list, never a bare id

The tool knows a small, named set of pipelines (`--pipeline-a`/`--pipeline-b`
resolve through a fixed name→id table the adopting project owns). **There is
no option that accepts a bare pipeline id anywhere in the interface.** A bare
id lets a caller queue an unintended pipeline by typo or by copy-paste from
the wrong run; the allow-list turns that class of mistake into a refused,
named argument instead of an unintended queue call.

### Production-shaped literals are refused before any network call

Every resolved parameter — the ref, the queue parameters, any per-target
override — is scanned for a production-shaped literal (a pool, queue, group,
or host name the adopting project marks as production) **before the client
is even constructed**. The refusal fires on the literal appearing *anywhere*
in the resolved input, not only in the field it was expected in: a production
name smuggled into a free-form parameter refuses exactly like one in the ref
itself. `--dry-run` returns before a client exists at all, so it is
structurally incapable of making this call, let alone reaching a production
target.

### The retry split: idempotent reads retry, a queue call never does

A **queue (create) call is never retried automatically.** It is not
idempotent: a retried queue call after a lost response can create a second
run for the same intent. On a network failure during a queue call, the tool
fails loudly and says plainly that the run **may or may not already exist**
and must be checked by hand before anyone retries — it does not guess and it
does not requeue. Only **idempotent reads** — polling a run's status,
listing failed records, downloading an artifact — retry transient network
errors, bounded by `--net-retries`. The count is retries after the first
attempt, so one read makes at most `--net-retries` + 1 attempts.

### The wait is bounded, and its true bound is printed

The wait loop is bounded rather than looping forever, but its bound is not
`--max-polls × --poll-interval`. Every poll is itself a read that can retry,
and every retry can first spend a whole request timeout. The true worst case
is

```text
max_polls × (poll_interval + (net_retries + 1) × request_timeout + net_retries × net_retry_sleep)
```

With 20 retries, a 60-second timeout and a 15-second retry sleep, a single
stalled poll makes 21 attempts and sleeps 20 times: 21 × 60 + 20 × 15 =
1,560 seconds, 26 minutes before the next one starts. The tool
computes this figure from its resolved bounds and prints it at start, so the
operator knows how long "still waiting" can legitimately last before it
means something is wrong.

### A wait is never silent

The tool prints one flushed `<pipeline> <run-id> poll N/M: status=...
result=...` line on the **first** poll and on **every observed state
change** (repeats are suppressed in between). A retry during the wait names
its attempt count and its budget (`retry <error> (attempt K/N, sleeping
Ss): ...`), never a bare error with no count. This exists because a wait
that prints nothing between "queued" and a terminal result is
indistinguishable, from outside, between "still working, well within its
budget" and "hung" — and that ambiguity is exactly what makes an operator
kill a working run and re-queue it, which is the situation §5 exists to
prevent.

### Attach to an existing run

`--attach-run-id` binds to an already-queued first-stage run instead of
queueing a new one. The second stage's queue call, its wait, its downloads,
and its summary all behave identically to the queued-from-scratch path — the
attach only replaces "queue pipeline A" with "adopt this id and start
waiting on it."

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the closed pipeline allow-list with no
  bare-id option; the production-literal refusal scanning every resolved
  parameter before any network call; `--dry-run` returning before a client
  exists; the retry split (idempotent reads retry, bounded; the queue call
  never does); the bounded wait; the per-poll and per-state-change progress
  line with attempt/budget on every retry; the status-only summary
  (never report content); the attach-to-an-existing-run mode.
- **Vendor-specific (write per platform):** the queue/status/artifact-download
  endpoints or CLI verbs; how a run is bound to a prior run's id (a
  platform-specific "triggering resource" parameter shape); the
  authentication scheme and where the credential comes from; the exact
  production-literal vocabulary the adopting project refuses.
- **Adopting note:** where the platform's client library has its own retry
  policy, make sure it is not silently retrying the queue call underneath the
  tool's own "never retry a queue call" rule — a client-level retry defeats
  the guarantee even when the tool's own code path looks correct.

## 5. Pitfalls and sharp edges

- **A silent wait invites exactly the wrong intervention.** An operator
  watching a wait with no progress output, worried it has hung, kills the
  process and re-queues by hand — creating a duplicate run of work that was
  in fact proceeding normally. The fix is not a shorter timeout; it is
  visible progress, so "still working" and "hung" are never indistinguishable
  from outside.
- **An injected test transport silently defeats CLI retry flags.** When a
  test constructs the client itself and passes it in (to avoid touching a
  real network), any `--net-retries`/`--net-retry-sleep` flags parsed from
  the CLI become no-ops, because the code path that builds a client from
  those flags never runs. Set the injected client's own retry/sleep fields
  directly in a test, not the CLI flags the production path would use — a
  test that "passes the CLI flag" here is asserting nothing about the
  flag-parsing path at all.
- **Collapsing "the queue call's network failed" into "the run failed" loses
  the one fact that matters.** A lost response after a queue call means the
  operator's next move is "check by hand," not "retry" and not "assume it
  failed" — both of the wrong assumptions can duplicate a run or abandon one
  that actually started.
- **Piping a long-running tool through `tail` destroys the history needed to
  diagnose it.** `tail` shows nothing until the process exits and then only
  the last lines, so the progress lines that would tell "slow but working"
  from "hung" never reach the operator while it runs, and are gone after.
  Send the output to a file and follow the file instead, keeping the whole
  record.
- **Completion detection is a shape match, not a timing guess.** Match the
  platform's own terminal-state fields exactly (its own status/result
  vocabulary) rather than inferring completion from elapsed time or from the
  absence of further output; a wait that "gives up and assumes success" after
  a while is a silent false green the moment the platform is simply slower
  than expected. When a wait appears stuck on a run the platform already
  shows as finished, first feed that run's exact status response into the
  completion check (§6); it tells a detection defect from a silent wait.

## 6. Tests that cover it

Cover with an **injected fake transport** (no network, no real platform,
pipeline names supplied as parameters so the suite stays pack-agnostic): the
allow-list refuses any pipeline name outside it, and the parser itself never
grows a bare-id option; the production-literal refusal fires from the ref,
from a default parameter, and from a `--params`-supplied override, all before
any transport call is made; `--dry-run` never touches the transport and needs
no credential; the full chain (queue → wait → queue-bound-to-prior-id → wait
→ download → summarize); `--first-only` stopping before the second pipeline
is ever queued; a failed first-run stopping the chain before the second
pipeline is queued; a transient network error being retried on a read call
and **not** retried on the queue call; one flushed progress line per observed
state change (repeats suppressed), with the first poll always visible
between the "queued" line and the terminal result; a retry line naming its
attempt number and budget; the worst-case-wait line printed at start
matching the formula in §3 for the resolved bounds; a regression case that
feeds the platform's **real** terminal-state response (the exact status and
result fields, copied from a finished run with its values made synthetic)
and expects the wait to return completed on the **first** poll; the summary never printing run content, only id,
status, and a named reason on failure.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `skill-corpus/drive-hosted-cicd-cli.md` (session login,
  the two-branch trap, proving which ref a run actually built — this page
  composes it by reference for anything below the chain-specific behavior
  above); `tool-corpus/testing/ci-runner-local-simulator.md` (reconstructs
  the runner's environment locally; a different question from driving a
  hosted run remotely);
  `tool-corpus/ops/chained-pipeline-run-driver-azure-devops.md` (a portable,
  self-tested implementation of this design for one hosted platform).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-09-26 — created by
  docs-librarian.
- 2026-09-26 — corrected after review: the true worst-case wait formula, printed at start; when not to use it; the `tail` pitfall; the real terminal-state regression test.
