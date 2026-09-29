# Tool: parallel-suite-runner

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. Orientation for a reusable tool, and drop-in: the script
> below is stdlib-only and runs against any repository on a POSIX host through
> `--repo`.

## 0. Identity

- **Category:** testing
- **Name:** parallel-suite-runner
- **Language / runtime:** python3, **stdlib only**. It needs Python 3.8 or
  later; the live core count uses `os.process_cpu_count()` where it exists
  (3.13+) and falls back to `os.cpu_count()`.
- **Stability:** **portable** across POSIX hosts, drop-in. The timeout kill
  uses process groups (`os.killpg`, `start_new_session`), which Windows does
  not have. An adopting project copies the script, points `-s` at its test
  directory, and records its known-failing ids as a baseline file.

## 1. What it does

It runs a stdlib-`unittest` suite across many processes and judges the result
against a known-failing baseline **by test id**. It replaces two steps that a
suite with standing failures repeats several times per increment:

1. a serial `python3 -m unittest discover -s <tests> -p 'test_*.py'`, which on a
   large suite takes minutes;
2. comparing its failures by hand against a list of the ones already known.

On a suite of about twelve hundred tests the serial run took close to six
minutes and the runner took under a minute and a half, with an identical set of
failing ids. That identity is the whole point. A faster run that reports
different failures is not a faster version of the same gate.

The runner starts one `python3` process per test module, N at a time, largest
file first. Each process gets the start directory at `sys.path[0]` and the
repository root as its cwd, which is how `discover -s` loads modules. It reads
the `FAIL:` / `ERROR:` header lines that unittest prints after a line of `=`, so
its ids match a serial run's exactly, subtest suffix included.

It prints one summary:

- the summed counts: tests run, failures, errors, skips;
- the failing ids that are **not** in the baseline ("new");
- the baseline ids that failed, and the baseline ids that did not;
- any shard that was re-run after a timeout;
- the five slowest shards, and any shard whose outcome could not be read;
- the log directory.

**It fails closed.** It exits 1 when a new id appears, when any shard cannot be
read as a result, even if every id that shard did print is in the baseline, and
when the shards ran no test at all. A shard is unreadable if it printed no
`Ran N tests` line, exited with anything but 0, 1 or 5, exited 1 with no id,
exited 0 with ids, printed a different number of ids than its failures plus
errors, or timed out on both of its attempts. A crash never reads as a pass,
and neither does an empty run: exit 5 from one shard is a module with no tests
in it, but a run whose shards ran 0 tests in total prints `no tests ran` and
fails.

**A timed-out shard is re-run once.** That is the one place the runner departs
from a plain parallel runner, and it exists because a parallel run loads the
machine in a way a serial run does not: a shard that would finish serially can
stall behind its neighbours. So the first timeout kills the shard's whole
process group and runs it again, alone in its worker slot. A timeout is never
itself turned into a failing test id: it names no test, and inventing one would
put a fake entry in the id comparison and the ready-made baseline. If the re-run
completes, its result is the shard's result, and the summary still names the
shard as re-run so a slow or hanging test stays visible. If the re-run times out
too, the shard is unreadable and the run fails.

## 2. Interface & invocation

```sh
python3 parallel-suite-runner.py [--repo DIR] [-s START] [-p PATTERN] [-j N]
    [--baseline FILE] [--serial GLOB]... [--split GLOB]... [--split-ways N]
    [--timeout SECONDS] [--logs DIR] [--python EXE]
```

| Flag | Default | Meaning |
|---|---|---|
| `--repo` | cwd | repository root, and the cwd of every shard |
| `-s` / `--start` | `tests` | start dir, relative to `--repo` |
| `-p` / `--pattern` | `test_*.py` | module file pattern, matched at the top level of the start dir (as `discover` without packages) |
| `-j` / `--jobs` | 2 × usable cores, read live at startup | processes at once |
| `--baseline` | none | lines of `FAIL: <id>` / `ERROR: <id>`; `#` comments and blank lines allowed |
| `--serial GLOB` | none | modules to run alone, in one process, after the pool drains (repeatable) |
| `--split GLOB` | none | modules whose test classes are sliced across `--split-ways` processes (repeatable) |
| `--split-ways` | 4 | slices per split module |
| `--timeout` | 900 | seconds per shard attempt; on expiry the whole process group is killed and the shard is re-run once |
| `--logs` | a new temp dir | one log per shard, plus `summary.txt`, `failing-ids.txt` and a `DONE` marker |
| `--python` | this interpreter | interpreter for the shards |

- **Inputs:** the flags above; the test modules under the start dir; the
  optional baseline file.
- **Outputs:** the summary on stdout, also written to `summary.txt`. Its
  load-bearing lines are `new failing ids: <n>` followed by one indented id per
  line, `crashed or timed-out shards: <n>` followed by
  `  <shard>: <reason> (log <path>)` lines, and a final `RESULT: PASS` or
  `RESULT: FAIL`. `failing-ids.txt` holds every failing id, sorted, one per
  line, and is a ready baseline. `DONE` holds the exit status, so a caller can
  tell a finished run from one that was killed.
- **Exit codes:** 0 no new id, every shard readable, and at least one test
  ran; 1 a new id, an unreadable shard, or no test run at all; 2 usage error. A missing baseline file or a malformed
  baseline line is exit 2, never an empty baseline that lets everything pass.
  Without `--baseline`, every failing id is new.
- **Preconditions:** the suite is stdlib `unittest`, laid out as modules at the
  top level of one start directory, on a POSIX host.

## 3. Approach / algorithm

Every shard is a subprocess with its own session, so a timeout can kill the
whole process group, grandchildren included. A thread pool of `-j` workers
drains the shard list; split slices go first because they are the known-slow
ones, and `--serial` modules run afterwards in one process of their own. After
every shard has finished, the runner sums counts, takes the union of failing
ids, and compares it with the baseline as sets.

```python
#!/usr/bin/env python3
"""parallel-suite-runner: run a stdlib-unittest suite across N processes and
compare its failing ids against a known-failing baseline.

Each test module runs in its own python process, with the start directory at
sys.path[0] and the cwd at --repo, the same way `discover -s` loads it. N
workers pull modules off a queue, largest file first. Modules matching --serial
run afterwards, alone, in one process. Modules matching --split have their test
classes sliced across --split-ways processes, for the few modules that set the
wall time. A shard that times out is re-run once; a timeout is never reported
as a failing test id.

Exit codes: 0 no new failing id, every shard readable, and at least one test
ran; 1 a new failing id, a shard whose outcome cannot be read, or no test run
at all (fail closed); 2 usage error (missing start dir, missing or malformed
baseline). Stdlib and POSIX only: the timeout kill uses process groups.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SEPARATOR = "=" * 70
ID_RE = re.compile(r"^(FAIL|ERROR): (.+)$")
RAN_RE = re.compile(r"^Ran (\d+) tests? in ")
COUNT_RE = re.compile(r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)")

# Loads the named modules exactly as `discover -s <start>` would find them:
# the start dir first on sys.path, the cwd left at the repository root.
BOOTSTRAP = (
    "import sys, unittest; sys.path.insert(0, sys.argv[1]); "
    "unittest.main(module=None, argv=['unittest'] + sys.argv[2:])"
)
# Runs slice K of N of one module's test classes. The loader enumerates the
# classes, so every class lands in exactly one slice by construction.
SPLIT_BOOTSTRAP = r"""
import importlib, sys, unittest
sys.path.insert(0, sys.argv[1]); mod, k, n = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
names = []
for suite in unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(mod)):
    for test in suite:
        c = type(test)
        name = f"{c.__module__}.{c.__qualname__}" if c.__module__ == mod else test.id()
        if name not in names:
            names.append(name)
mine = names[k::n]
print(f"# slice {k}/{n}: " + " ".join(mine), file=sys.stderr, flush=True)
if not mine:
    print("\n" + "-" * 70 + "\nRan 0 tests in 0.000s\n\nOK", file=sys.stderr); sys.exit(0)
unittest.main(module=None, argv=["unittest"] + mine)
"""


def default_jobs() -> int:
    """Two workers per usable core, read live so the run scales with the host.

    Most test modules wait on subprocesses and the filesystem rather than the
    CPU, so modest oversubscription beats one worker per core.
    """
    count = getattr(os, "process_cpu_count", os.cpu_count)() or 1
    return 2 * count


@dataclass
class ShardResult:
    name: str
    modules: List[str]
    log: Path
    split: Optional[Tuple[int, int]] = None  # (k, n): slice k of n of one module's classes
    seconds: float = 0.0
    returncode: Optional[int] = None
    timed_out: bool = False
    rerun: bool = False  # the first attempt timed out and this result is the re-run's
    ran: Optional[int] = None
    counts: Dict[str, int] = field(default_factory=dict)
    ids: List[str] = field(default_factory=list)

    @property
    def unreadable(self) -> Optional[str]:
        """Why this shard's outcome cannot be read as a result, or None."""
        if self.timed_out:
            return "timed out, and again on its one re-run"
        if self.ran is None:
            return f"no 'Ran N tests' line (exit {self.returncode})"
        if self.returncode not in (0, 1, 5):
            return f"exit {self.returncode}"
        if self.returncode == 1 and not self.ids:
            return "exit 1 with no FAIL/ERROR id"
        if self.returncode == 0 and self.ids:
            return "exit 0 with FAIL/ERROR ids"
        expected = self.counts.get("failures", 0) + self.counts.get("errors", 0)
        if len(self.ids) != expected:
            # A mangled or interleaved log can drop a header; a lost id must
            # not let the shard's remaining, baselined ids read as its result.
            return f"{len(self.ids)} FAIL/ERROR ids parsed for {expected} failures+errors"
        return None


def parse_log(result: ShardResult) -> None:
    lines = result.log.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, line in enumerate(lines):
        # unittest prints each failure header right after a line of '='.
        if i > 0 and lines[i - 1] == SEPARATOR and ID_RE.match(line):
            result.ids.append(line)
        m = RAN_RE.match(line)
        if m:
            result.ran = int(m.group(1))
    for line in reversed(lines):
        if line.startswith(("OK", "FAILED")):
            result.counts = {k: int(v) for k, v in COUNT_RE.findall(line)}
            break


def attempt(result: ShardResult, cmd: List[str], repo: Path, timeout: float) -> None:
    """Run one attempt into result.log. A timeout kills the whole process group
    and leaves ids, counts and the run line unset: it names no test."""
    result.returncode, result.timed_out, result.ran = None, False, None
    result.counts, result.ids = {}, []
    with result.log.open("w", encoding="utf-8") as out:
        out.write("# " + " ".join(result.modules) + "\n")
        out.flush()
        proc = subprocess.Popen(cmd, cwd=repo, stdout=out, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
        try:
            result.returncode = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            result.timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # the group finished between the timeout and the kill
            proc.wait()
            out.write(f"\n# KILLED after {timeout:.0f}s timeout\n")
    if not result.timed_out:
        parse_log(result)


def run_shard(result: ShardResult, python: str, repo: Path, start: Path, timeout: float) -> ShardResult:
    if result.split:
        cmd = [python, "-c", SPLIT_BOOTSTRAP, str(start), result.modules[0], *map(str, result.split)]
    else:
        cmd = [python, "-c", BOOTSTRAP, str(start)] + result.modules
    t0 = time.monotonic()
    attempt(result, cmd, repo, timeout)
    if result.timed_out:
        # One re-run, and only one: a shard can stall behind loaded neighbours,
        # but a second timeout is a real hang and fails the run.
        result.log.replace(result.log.with_name(result.log.stem + ".timed-out.log"))
        result.rerun = True
        attempt(result, cmd, repo, timeout)
    result.seconds = time.monotonic() - t0
    return result


def read_baseline(path: Path) -> Set[str]:
    ids = set()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if not ID_RE.match(line):
            raise ValueError(f"{path}:{n}: not a 'FAIL: <id>' or 'ERROR: <id>' line: {line[:80]}")
        ids.add(line)
    return ids


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, default=Path.cwd(), help="repository root; the cwd of every shard (default: cwd)")
    ap.add_argument("-s", "--start", default="tests", help="start dir, relative to --repo (default: tests)")
    ap.add_argument("-p", "--pattern", default="test_*.py", help="module file pattern (default: test_*.py)")
    ap.add_argument("-j", "--jobs", type=int, default=default_jobs(),
                    help=f"parallel processes (default: 2 x usable cores, here {default_jobs()})")
    ap.add_argument("--baseline", type=Path, help="known-failing ids, one 'FAIL: <id>' / 'ERROR: <id>' per line")
    ap.add_argument("--serial", action="append", default=[], metavar="GLOB",
                    help="module file glob to run alone, in one shard, after the pool (repeatable)")
    ap.add_argument("--split", action="append", default=[], metavar="GLOB",
                    help="module file glob whose test classes are sliced across --split-ways shards (repeatable)")
    ap.add_argument("--split-ways", type=int, default=4, metavar="N", help="slices per --split module (default: 4)")
    ap.add_argument("--timeout", type=float, default=900,
                    help="seconds per shard attempt; a timed-out shard is re-run once (default: 900)")
    ap.add_argument("--logs", type=Path, help="directory for per-shard logs (default: a new temp dir)")
    ap.add_argument("--python", default=sys.executable, help="interpreter for the shards (default: this one)")
    a = ap.parse_args(argv)

    repo = a.repo.resolve()
    start = (repo / a.start).resolve()
    if not start.is_dir():
        print(f"error: start dir not found: {start}", file=sys.stderr)
        return 2
    baseline: Set[str] = set()
    if a.baseline is not None:
        if not a.baseline.is_file():
            print(f"error: baseline file not found: {a.baseline}", file=sys.stderr)
            return 2
        try:
            baseline = read_baseline(a.baseline)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    if a.jobs < 1 or a.split_ways < 1:
        print("error: -j and --split-ways must be >= 1", file=sys.stderr)
        return 2

    files = sorted(start.glob(a.pattern), key=lambda p: (-p.stat().st_size, p.name))
    files = [f for f in files if f.is_file() and f.suffix == ".py"]
    if not files:
        print(f"error: no module matches {a.pattern!r} in {start}", file=sys.stderr)
        return 2
    serial = [f for f in files if any(fnmatch.fnmatch(f.name, g) for g in a.serial)]
    pooled = [f for f in files if f not in serial]

    logs = a.logs or Path(tempfile.mkdtemp(prefix="parallel-suite-"))
    logs.mkdir(parents=True, exist_ok=True)
    shards = []
    for f in pooled:
        if any(fnmatch.fnmatch(f.name, g) for g in a.split):
            n = a.split_ways
            shards += [ShardResult(f"{f.stem}[{k}/{n}]", [f.stem], logs / f"{f.stem}.{k}of{n}.log", (k, n))
                       for k in range(n)]
        else:
            shards.append(ShardResult(f.stem, [f.stem], logs / f"{f.stem}.log"))
    shards.sort(key=lambda s: s.split is None)  # split slices are the known-slow ones: start them first
    serial_shard = ShardResult("serial", [f.stem for f in sorted(serial)], logs / "serial-shard.log") if serial else None

    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        list(pool.map(lambda s: run_shard(s, a.python, repo, start, a.timeout), shards))
    if serial_shard:
        run_shard(serial_shard, a.python, repo, start, a.timeout)
        shards.append(serial_shard)
    wall = time.monotonic() - t0

    def label(s: ShardResult) -> str:
        return s.name if s.name != "serial" else ", ".join(s.modules)

    totals = {k: 0 for k in ("failures", "errors", "skipped")}
    ran = 0
    failing: Set[str] = set()
    broken = []
    for s in shards:
        ran += s.ran or 0
        for k in totals:
            totals[k] += s.counts.get(k, 0)
        failing.update(s.ids)
        why = s.unreadable
        if why:
            broken.append((s, why))
    new = sorted(failing - baseline)
    known = sorted(failing & baseline)
    absent = sorted(baseline - failing)
    rerun = [s for s in shards if s.rerun]

    (logs / "failing-ids.txt").write_text("".join(i + "\n" for i in sorted(failing)), encoding="utf-8")
    out = [
        f"parallel-suite-runner: {len(files)} modules, {a.jobs} jobs, {len(serial)} serial, wall {wall:.1f}s",
        f"ran {ran}  failures {totals['failures']}  errors {totals['errors']}  skipped {totals['skipped']}",
    ]
    if a.baseline is not None:
        out.append(f"baseline {a.baseline}: {len(baseline)} ids, {len(known)} failed as known, {len(absent)} did not fail")
    else:
        out.append("baseline: none given, so every failing id counts as new")
    out.append(f"new failing ids: {len(new)}")
    out += [f"  {i}" for i in new]
    if a.baseline is not None:
        out.append(f"baseline ids that failed: {len(known)}")
        out += [f"  {i}" for i in known]
        if absent:
            out.append(f"baseline ids that did NOT fail: {len(absent)}")
            out += [f"  {i}" for i in absent]
    if ran == 0:
        out.append("no tests ran: every shard ran 0 tests, which is not a pass")
    if rerun:
        out.append(f"re-run after a timeout: {len(rerun)}")
        out += [f"  {label(s)} (first attempt: {s.log.with_name(s.log.stem + '.timed-out.log')})" for s in rerun]
    slow = sorted(shards, key=lambda s: -s.seconds)[:5]
    out.append("slowest shards: " + ", ".join(f"{s.name} {s.seconds:.0f}s" for s in slow))
    out.append(f"crashed or timed-out shards: {len(broken)}")
    out += [f"  {label(s)}: {why} (log {s.log})" for s, why in broken]
    out.append(f"logs: {logs}  (all failing ids: {logs / 'failing-ids.txt'})")
    status = 1 if (new or broken or ran == 0) else 0
    out.append("RESULT: " + ("FAIL" if status else "PASS"))
    text = "\n".join(out) + "\n"
    (logs / "summary.txt").write_text(text, encoding="utf-8")
    (logs / "DONE").write_text(f"exit {status}\n", encoding="utf-8")
    sys.stdout.write(text)
    return status


if __name__ == "__main__":
    sys.exit(main())
```

## 4. Portable vs blueprint

- **Portable (use as-is):** the whole script. That covers one process per
  module with the start dir on `sys.path` and the repository root as cwd; ids
  read from unittest's own failure headers; the set comparison by id; the
  fail-closed readability rule; the single re-run after a timeout; the
  process-group kill; the ready-baseline `failing-ids.txt`; and the `DONE`
  marker.
- **Fill in per project:** the start dir (`-s`), the baseline file and its
  location, and the `--split` / `--serial` lists. Pick the split modules from
  the `slowest shards:` line of a real run, and re-pick them when that line
  changes.
- **Port note:** for another test framework the shape carries over: one
  process per file, ids read from the framework's own failure report, a set
  comparison against a baseline of ids, and the same fail-closed rule. Only the
  bootstrap command and the log parser are rewritten.

## 5. Pitfalls and sharp edges

- **Compare ids, never counts.** A run with the same number of failures as the
  baseline can still hold a new failure under a different id. Counts across two
  different trees say even less. Compare failing ids, on one tree.
- **Process isolation is stricter than serial `discover`.** Every module gets a
  fresh interpreter. A test that passes only because another module ran first
  in the same process fails here, and that failure is a real finding about the
  test, not about the runner. When the runner and a serial run disagree, one
  serial `discover` is the reference.
- **The floor is the slowest class, not the core count.** Past a point, module
  splitting stops helping: the largest module sets the wall time. `--split`
  slices it by class, and then its single slowest class sets the floor.
- **More jobs is not always faster.** Measured on 8 cores, wall time improved
  up to about 2× cores and then got worse again as shards contended for CPU.
  Oversubscription pays because most tests wait on I/O, not because it scales
  without limit.
- **A lost id is caught by count, not by name.** A mangled or interleaved log
  can drop a `FAIL:` / `ERROR:` header, and the id that went missing is exactly
  the one the baseline comparison cannot see. So each shard's parsed ids must
  number its `failures` plus `errors`; a shard where they differ is unreadable,
  even when every id it did print is baselined.
- **Zero tests is not a pass.** Exit 5 from one shard means that module holds no
  tests, and the shard stays readable. A run in which every shard ran 0 tests
  fails with `no tests ran`: a wrong `-p` or `-s` must not read as a green
  suite.
- **The group can finish before the kill.** If a timed-out shard's process group
  exits between the timeout and `os.killpg`, the kill raises
  `ProcessLookupError`, and the runner ignores it and still treats the attempt
  as timed out. That branch is defensive and untested: the window is too narrow
  to hit on purpose from a test.
- **The re-run can hide a slow test.** A shard that timed out once and passed on
  its re-run passes the gate. The summary names it under
  `re-run after a timeout:`, and its first attempt's log is kept beside the
  shard log as `<shard>.timed-out.log`. Read that line; a shard that shows up
  there every run is a test to fix, or a timeout to raise.
- **An import error in a split module is a crash, not an `ERROR:` id.** The
  slice process imports the module to list its classes, so the failure lands
  before any run line. Serial `discover` would report a
  `unittest.loader._FailedTest` id instead. Both fail the run.
- **`setUpModule` and `setUpClass` run once per shard**, not once per suite.
  That is correct isolation, and it costs time on split modules.
- **Each shard's log starts with a `# <modules>` line** (`# slice k/n:
  <classes>` for a split shard), so a log can be traced back to what it ran.

## 6. Tests that cover it

The seed's portability gate drives the largest `python` block on this page
through its command line, over a synthetic stdlib-unittest package in a temp
dir. It pins:

- failing ids equal to a real serial `discover` over the same package, with the
  start dir importable and the repository root as cwd;
- the baseline compared by id: carried ids pass, a new id fails and is listed
  under `new failing ids:`, and an equal failure count with a different id
  fails;
- a shard that times out twice runs exactly twice, fails the run, is named as
  timed out, and adds no failing id;
- a shard that crashes before its run line, and one that exits 3 after a
  complete run, both fail closed and are named;
- a shard that printed fewer ids than its failures plus errors fails closed and
  is named, even though the id it did print is baselined;
- a suite in which no test ran exits 1 and says `no tests ran`;
- a missing baseline file and a malformed baseline line both exit 2.

A plant that adopts the script should also pin `--serial`, `--split` (every
class in exactly one slice, and more slices than classes), the live core-count
default, and the `DONE` marker. The seed no longer checks three behaviours, so
a plant that relies on them pins them too: one process per module with
overlapping lifetimes, a shard that times out once and passes when it is run
again (once only, adding no failing id), and the kill of a timed-out shard's
whole process group.

- **How to run the tests:** `bash tests/test-tool-corpus.sh` in the seed; in a
  plant, `<the plant's test command for its copy>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/failure-signature-triage.md`. This
  runner answers "did any new test id fail?"; that page goes one step further
  for a suite with a standing flake population, comparing failure signatures
  so that a known-flaky test failing in a new way is not waved through under
  its old name. `tool-corpus/testing/working-tree-snapshot.md` builds the
  throwaway tree a suite is often run inside.
- **Sources:** distilled from harvested plant experience; the id format and
  exit code 5 ("no tests ran", Python 3.12+) are stdlib `unittest` behaviour.
  The runner accepts exit 5 from one shard and refuses a run that ran nothing.

## 8. Changelog

- 2026-09-26: created from a harvested, generalized plant tool. The single
  re-run of a timed-out shard was added on import; before it, a timeout failed
  the run on its first occurrence. Same day: a run that ran no test fails, a
  shard whose parsed ids do not match its failures plus errors is unreadable,
  a process group that finished before the kill is tolerated, and the page
  names POSIX as the portability boundary.
