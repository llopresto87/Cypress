# Tool: long-stage-progress-runner

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the output
> contract, the heartbeat loop, the TIMEOUT status and the dead-transport rule
> are stack-neutral; the log parser is written against the adopting project's
> test runner, with one stack worked below.

## 0. Identity

- **Category:** testing
- **Name:** long-stage-progress-runner
- **Language / runtime:** a sourced shell helper (portable to bash 3.2 and BSD
  `awk`, so it runs unchanged on a stock macOS workstation and on Linux build
  hosts); the transport is a remote shell when the stage runs remotely.
- **Stability:** **blueprint**. The loop is a dozen lines; the parser is
  runner-specific.

## 1. What it does

Runs one long gate stage (a test suite, a smoke run, a mutation pass) that
takes more than a minute, often on another host, and makes it **observable
while it runs and diagnosable after it ends**:

- streams the stage's output to a log in a directory **announced on the first
  line**, with a stable `latest` link, so a human or agent can follow it;
- prints a **heartbeat** at a fixed interval naming the stage, its elapsed
  time, the unit currently running (a test class, a mutant), the counts so far,
  and an **idle** counter: seconds since the log last grew;
- reports **TIMEOUT as its own status**, distinct from FAIL, naming the units
  still in flight and the last one finished;
- makes a **dead transport fail fast** and names it as such, not as a test
  failure;
- **copies the runner's reports back whatever the outcome**, because a failed
  or timed-out run is exactly when they are needed.

It exists because a long silent stage reads the same whether it is working,
hung, or disconnected. A bound that is too short then looks like a red suite
with no failing test, and an agent re-runs or "fixes" tests that never failed.
A shared helper also keeps every gate's heartbeat format identical, so one
parser and one habit read them all.

## 2. Interface & invocation

```
. <helper>.sh
progress_heartbeat_from "${HEARTBEAT_SECS:-60}" || exit 2   # integer >= 1, else usage
trap progress_kill EXIT
progress_run KIND STAGE LOG CMD...        # returns CMD's exit code
progress_inflight LOG                      # units still running
progress_failures LOG                      # first few failing ids
progress_fetch_reports DEST REMOTE_DIR TRANSPORT...
```

- **Output lines** (the contract every caller and parser shares):

```
<stage>: started; streaming to <log> (heartbeat every <N>s)
HEARTBEAT <stage> <N>s last=<running|finished> <unit> run=<n> fail=<n> err=<n> idle=<s>s
STAGE <stage> PASS|FAIL|SKIPPED|TIMEOUT <s>s <detail>
```

- **TIMEOUT detail** names `still running: <units>` and the last finished unit.
- **Exit-code mapping:** the bound's exit code (124 from `timeout`) maps to
  TIMEOUT; the transport's own failure code (255 from `ssh`) maps to
  `FAIL transport failed or the link was lost`; any other non-zero is FAIL with
  the failing ids.
- **SKIPPED is never PASS.** A stage not requested, or skipped because an
  earlier one failed, prints SKIPPED and is recorded as absent.

## 3. Approach / algorithm

```
run CMD in the background, stdout+stderr to LOG
every second while it lives:
    if LOG size changed: changed = now
    every HEARTBEAT seconds: print HEARTBEAT with parser(LOG) and idle = now - changed
wait; return CMD's exit code
```

- **Bound the stage on both sides.** A local `timeout` above the remote one, and
  a remote `timeout` so the host-side run stops at its own bound even when the
  link is gone.
- **Transport keepalive.** Give the remote shell a keepalive (with OpenSSH,
  `ServerAliveInterval` times `ServerAliveCountMax` sets how long a dead link
  survives; about a minute is enough), so a dropped link fails in seconds rather
  than hanging until the stage's bound.
- **One parser for every view.** Status, counts, in-flight units, last
  finished and failing ids all come from one function with a mode argument, so
  the heartbeat and the final STAGE line never disagree.
- **Size the bound from a measured green run**, about three times its duration,
  and record the measurement next to the default. A bound copied from a guess
  is the false red this page exists to remove.

## 4. Portable vs blueprint

- **Portable:** the output lines; the announced log directory; idle from log
  growth; TIMEOUT and transport loss as their own statuses; reports copied back
  on every outcome; one parser; the measured-bound rule.
- **Fill in per project:** the parser for the runner's log format, the report
  directories to fetch, the transport, and the bounds.
- **Per stack, Maven with Surefire or Failsafe (`library-corpus/cli/maven.md`):**
  a unit starts at a `Running <class>` line and finishes at a per-class
  `Tests run: ..., Failures: ..., Errors: ... in <class>` line. Observed in
  practice: Surefire 2 writes ` - in` and Surefire 3 writes ` -- in`; read both. **Count only the
  per-class lines**: the aggregate `Tests run:` summary has no ` in <class>`
  ending and must never be added on top. With parallel forks, interleaved
  `Running` lines mean "currently running" is the newest class not yet
  finished. Fetch `target/surefire-reports` and `target/failsafe-reports`.

## 5. Pitfalls and sharp edges

- **A bound that is too short looks like a red suite.** The symptom is a stage
  that dies at exactly its bound with no failing test in the tail; TIMEOUT as
  its own status is what makes it legible.
- **`idle` is the dead-link and hang detector.** A rising idle with a live
  process is a silent stage or a stuck unit; the heartbeat's `last=running
  <unit>` names which.
- **The next run deletes the remote reports.** Copy them back on every
  outcome, and when the copy fails say where they are on the host.
- **Do not edit a sourced helper or its caller while a run is live**; a lazily
  read shell script runs the edited bytes.

## 6. Tests that cover it

- **The parser, from fixture logs:** per-class counts and never the aggregate;
  both separator forms; in-flight units with interleaved forks; failing ids; an
  empty log.
- **Each caller, against the stubs of `tool-corpus/testing/remote-stub-fixture.md`**
  (no network, no build): a pass announces the log and streams heartbeats; a
  timeout prints TIMEOUT, not FAIL, names the in-flight unit and still copies the
  reports; a failure names the failing ids; a lost link (stub exits 255) is named
  as such; a non-integer heartbeat is a usage error.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/staged-index-commit-gate.md`,
  `tool-corpus/testing/batched-mutant-runner.md` and
  `tool-corpus/testing/sandboxed-browser-test-runner.md` (stages that run
  through this helper); `tool-corpus/testing/fire-and-forget-command-observer.md`
  (observing a command whose effect lands later on a broker, a different
  problem); `tool-corpus/testing/parallel-suite-runner.md` (a local runner with
  its own per-shard timeout).
- **Sources:** distilled from practice; OpenSSH `ssh_config(5)` for the
  keepalive options.

## 8. Changelog

- 2026-10-14 — created by docs-librarian.
