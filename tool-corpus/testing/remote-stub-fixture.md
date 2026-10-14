# Tool: remote-stub-fixture

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the stub-on-PATH
> technique, the path rewrite, the call logs and the scenario scripts are
> portable; which binaries are stubbed and what each scenario prints are the
> adopting project's.

## 0. Identity

- **Category:** testing
- **Name:** remote-stub-fixture
- **Language / runtime:** the test language's standard library (writing small
  executable files, setting `PATH`) plus `bash` for the stubs themselves; no
  network, no container engine, no remote host
- **Stability:** **blueprint**. The shape is stack-neutral; the stub bodies
  are written against the exact argument forms the scripts under test use.

## 1. What it does

Lets a script that drives a remote machine (over a remote shell, a file
sync, a container engine on that host, a timeout wrapper) be unit-tested on
the local machine with no network. Executable stubs with the real tools'
names go first on `PATH`; each one runs the "remote" side locally, under a
temporary root, and logs how it was called. The script under test runs
unchanged: it believes it is talking to a remote host.

It exists because remote-driving scripts are otherwise tested only by running
them for real, which needs the host, takes minutes, and cannot produce on
demand the cases that matter most: a hung stage, a dead transport, a failed
build, a missing image. Those paths go untested, and they are the ones that
decide whether a timeout reads as a red suite or a lost link reads as a test
failure.

It is not `tool-corpus/testing/ci-runner-local-simulator.md`, which rebuilds
a CI runner's *environment* so a real command runs as the runner would; this
fixture fakes the *remote tools* so the script that calls them can be tested.

## 2. Interface & invocation

A test-support module, not a test module and not a CLI:

```text
fixture = FakeRemote(tmp_dir)       # writes the stubs, creates the fake root
fixture.scenario(<script text>)     # what the remote build/test step does
env = fixture.env(**overrides)      # PATH with the stubs first, plus the
                                    # variables the stubs read
run(<script under test>, env=env)   # the real script, unchanged
fixture.call_log("ssh")             # every call, for assertions
```

- **Inputs:** a temp directory; per test, a scenario script (what the remote
  step prints, how long it runs, its exit status); overrides for the
  variables the script under test reads (its host name set to an address
  that cannot resolve, its key path set to an empty device).
- **Outputs:** the stubs in `<tmp>/fakebin`, a fake remote root in
  `<tmp>/fakeroot`, and one log per stubbed tool in that root.
- **Preconditions:** the script under test calls its tools by bare name
  (resolved through `PATH`), never by absolute path; the real file-sync tool
  and the real timeout tool exist locally for the stubs to delegate to.

## 3. Approach / algorithm

1. **Stubs first on `PATH`.** Write one executable per remote tool into
   `fakebin` and prepend it to `PATH` in the environment handed to the
   script. Nothing in the script changes.
2. **The remote side runs locally, under a temp root.** The remote-shell
   stub takes the command string it was given and runs it with a local
   shell, after rewriting every occurrence of the remote working directory
   to the fake root. The file-sync stub does the same to its destination
   (`host:/remote/dir` becomes `<fakeroot>/dir`) and delegates a purely
   local copy to the real tool. The rewrite is what guarantees that no test
   can write to the real remote directory, even when a test is wrong.
3. **Tools that are not the subject succeed silently.** Ownership changes,
   image inspection and pulls print nothing and exit 0, unless a test sets
   a variable that switches on a failure mode (an image missing until it is
   pulled, a pull that fails with a given status).
4. **The build step is a scenario script.** The container-engine stub, on a
   `run`, changes into the requested working directory and executes the
   current scenario with the run's arguments as its own, so a scenario can
   read a test selector from them. Scenarios are plain shell text kept in the
   fixture as constants: a pass that writes the report files the real tool
   writes, a failure naming a test id, a hang (`exec sleep` longer than the
   script's timeout), a dead transport (exit with the remote shell's own
   connection-failure status), a run where nothing executed.
5. **Every call is logged.** Each stub appends its arguments (and, for the
   remote shell, the rewritten command) to `<fakeroot>/<tool>.log`, so a test
   asserts how the script called the remote: that a keepalive option was
   passed, that the container got a name the cleanup can find, that the
   timeout wrapped the right command.
6. **Short clocks.** The script under test exposes its heartbeat and
   timeout intervals as variables; the fixture sets them to a second or
   two, so a hang test runs in seconds.

## 4. Portable vs blueprint

- **Portable:** stubs first on `PATH`; the path rewrite of the remote
  working directory into a temp root on both the remote-shell and the
  file-sync stub; silent success for tools that are not the subject, with
  opt-in failure switches; scenario scripts for the remote build step; one
  call log per tool; short clocks through variables.
- **Write per project:** the remote working directory to rewrite, the
  argument forms each stub must understand (only those the scripts under
  test use), the report files a pass scenario writes, the scenario set.
- **Port note:** a test language without easy subprocess control can still
  do this from a shell test harness; the technique is `PATH` resolution,
  not a library.

## 5. Pitfalls and sharp edges

- **A remote shell treats options and the command differently.** The stub
  must take the last argument as the command and ignore the options before
  it, and it must exit 0 for a control-socket query (`-O`) or a script that
  checks its multiplexed connection hangs or fails for the wrong reason.
- **A missed rewrite writes to a real path.** Rewrite every form the script
  produces (with and without a trailing slash), and keep the remote
  directory a fixture constant shared by both stubs, so a script change
  that adds a new form fails a test instead of writing outside the root.
- **The environment leaks into the stubs.** A test run from inside a
  version-control hook inherits that hook's index variable; drop it from
  the environment the fixture builds, or a `git` call inside a scenario
  reads the wrong index.
- **The platform's timeout tool may have another name.** Where the system
  ships it under a prefixed name, the timeout stub delegates to that name;
  check it exists before the suite runs, or every timeout test fails for a
  reason that has nothing to do with the script.
- **A stub that accepts everything proves little.** Assert on the call logs
  (the options passed, the command run), not only on the script's exit
  status; a script that stops calling the remote at all would otherwise
  still pass.
- **Not a test module.** Name the file outside the test runner's discovery
  pattern, or it is collected as an empty suite.

## 6. Tests that cover it

The fixture is proved through the tests that use it, plus a few of its own:
a pass scenario through the script under test ends green and the report
files exist under the fake root; a hang scenario ends in the script's
timeout status within the short clock; a dead-transport scenario is reported
as a lost link, not as a test failure; a failure scenario names its test id;
the remote-shell log shows the keepalive option; a command naming the
remote directory never touches it (the fake root receives the write).

- **How to run the tests:** `<the plant's test command for its script tests>`

## 7. References & neighbours

- **Tools it tests:** `tool-corpus/testing/staged-index-commit-gate.md` and
  `tool-corpus/testing/long-stage-progress-runner.md` (both drive a remote
  build host; this fixture is how their hang, lost-link and failure paths
  are tested); `tool-corpus/testing/batched-mutant-runner.md` and
  `tool-corpus/testing/sandboxed-browser-test-runner.md` (their
  container-engine and remote calls).
- **Related tools:** `tool-corpus/testing/ci-runner-local-simulator.md`
  (rebuilds a runner's environment for a real command; the opposite
  direction); `tool-corpus/testing/working-tree-snapshot.md` (the same
  "name the helper so the runner does not collect it" rule).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14 — created by harvest.
