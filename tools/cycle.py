#!/usr/bin/env python3
"""cycle.py — the state of a build cycle in one read (SPEC-0005 "Cycle driver").

The lead used to work out by hand which increments are ready, which are held
and why, what the tip may see red, and whether the RED hashes still hold
(`delegation.waves`, `delegation.green-self-test`). This prints it from:

  - the plan's §9, through grill-lint.py's own `plan_graph` and `pack` (the
    reading of §9 and the batch table have one home, and it is there);
  - the spawn log, `spawns.jsonl` beside the plan (`brief.py` writes it);
  - the batch record, `docs/graph/plans/<unit>/batch-record.txt`;
  - the question files, `docs/graph/plans/<unit>/questions/batch-<N>.md`;
  - git: an increment has landed when every contract slug its §9 row names
    appears in the slug of a GREEN commit subject on the current branch, in
    the format `test-first.cycle` defines (`feat(<scope>): <slug> — implements
    SPEC-NNNN` or `fix(<scope>): <slug> — adds regression for SPEC-NNNN`); a
    RED, spec or plan commit naming the slug lands nothing. The result is an
    inference and is printed as one; with no history or no contract it is
    `landed: unknown`.

It never spawns and decides no tier, ruling or acceptance: a hold condition,
a failure's attribution and a ruling are the lead's and the architect's, and
the record only carries what they decided.

Usage:
  python3 docs/graph/cycle.py --unit UNIT [--plan P]
  python3 docs/graph/cycle.py record-red N --unit UNIT --file PATH... --test ID... [--ruling RID]
  python3 docs/graph/cycle.py record-red N --unit UNIT --wrong "REASON"
  python3 docs/graph/cycle.py record-tip --unit UNIT [--not-run ID]... [--fail N ID]...

The report (stdout), in this order: the `cycle:` header; `ready RED tester:`,
`ready prose writer:`, `ready GREEN implementer:` per batch, or `ready: nothing
is ready to spawn`; `in flight:`; `waits:`; `held:` with the one condition of
`delegation.waves` that holds it; `expected-red:`; `not run:`; `mismatch:`;
`question:` for an unruled entry it cannot attribute; `ruling pass:`.
The report writes nothing. Exit 0; 1 when a recorded RED file no longer
matches its hash (the GREEN is re-briefed from the recorded RED); 2 with one
stderr line `cycle: <file>[:<line>]: <reason>` on malformed input or a
refused write, and no report.

`record-red` and `record-tip` are the only writes, each atomic (a temporary
file and a rename). The record's line format has one home,
`delegation.green-self-test` in method/delegation-cycle-economy.md.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KINDS = ("red", "test", "wrong", "ruled", "expected-red", "not-run", "fail")
HEADER = "# batch record (delegation.green-self-test): written by cycle.py record-red and record-tip"
NAMED_RE = re.compile(r"\bincrements?\s+(\d+(?:\s*(?:,|and|to|-|–)\s*\d+)*)", re.I)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SLUG_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
GREEN_SUBJECT = re.compile(r"^(?:feat|fix)\([^)]*\): (.+?) — (?:implements|adds regression for) SPEC-\d+\s*$")
NOT_PROSE_WORKERS = ("reviewer", "architect", "security", "devils-advocate")


class Refusal(Exception):
    """One stderr line, exit 2."""


def grill_lint():
    sys.dont_write_bytecode = True      # the report writes nothing, not even a bytecode cache
    for path in (HERE / "grill-lint.py", HERE.parent / "templates" / "knowledge-graph" / "grill-lint.py"):
        if path.is_file():
            spec = importlib.util.spec_from_file_location("cypress_grill_lint", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if not hasattr(mod, "plan_graph") or not hasattr(mod, "pack"):
                raise Refusal(f"{path}: predates cycle.py (no plan_graph or pack); graft the plant")
            return mod
    raise Refusal(f"{HERE / 'grill-lint.py'}: not found beside cycle.py")


def named(text: str) -> set[int]:
    """Increment numbers a text names: `increment 7`, `increments 3, 4`, `1-8`."""
    out: set[int] = set()
    for m in NAMED_RE.finditer(text or ""):
        parts = re.split(r"\s*(?:,|and)\s*", m.group(1))
        for p in parts:
            r = re.split(r"\s*(?:to|-|–)\s*", p)
            if len(r) == 2 and r[0].isdigit() and r[1].isdigit() and 0 <= int(r[1]) - int(r[0]) <= 1000:
                out.update(range(int(r[0]), int(r[1]) + 1))
            else:
                out.update(int(x) for x in r if x.isdigit())
    return out


def git(top: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(top), *args], capture_output=True, text=True, errors="replace")


def read_utf8(path: Path, shown: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise Refusal(f"{shown}: not valid UTF-8 (byte {e.start})")
    except OSError as e:
        raise Refusal(f"{shown}: {e.strerror or e}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Cycle:
    def __init__(self, plan: Path, unit: str):
        self.plan = plan.resolve()
        if not self.plan.is_file():
            raise Refusal(f"{plan}: no plan")
        r = git(self.plan.parent, "rev-parse", "--show-toplevel")
        if r.returncode == 0:
            self.top = Path(r.stdout.strip()).resolve()
        else:
            self.top = next((d for d in self.plan.parents if (d / "docs" / "graph").is_dir()), self.plan.parent)
        self.unit_dir = self.plan.parent / unit
        self.record_path = self.unit_dir / "batch-record.txt"
        self.gl = grill_lint()
        self._read_plan()
        self._read_record()
        self._read_spawns()
        self._read_questions()
        self._read_commits()

    def rel(self, p: Path) -> str:
        try:
            return str(p.resolve().relative_to(self.top))
        except ValueError:
            return str(p)

    # ---- inputs --------------------------------------------------------------
    def _read_plan(self):
        gl = self.gl
        text = gl.strip_comments(self.plan.read_text(encoding="utf-8", errors="replace"))
        fails: list[str] = []
        incs = gl.increments(gl.sections(text).get(9, ""), fails, self.plan)
        graph, efforts, defect, _libs, _refs = gl.plan_graph(incs, fails)
        numbers = [n for n, *_ in graph]
        if defect or len(set(numbers)) < len(numbers):
            raise Refusal(f"{self.rel(self.plan)}: §9 has dependency defects or duplicate increment "
                          f"numbers; grill-lint.py names them")
        self.graph = graph
        self.order = {n: i for i, n in enumerate(numbers)}
        self.deps = {n: list(dict.fromkeys(d)) for n, _t, d, *_ in graph}
        self.phase = {n: (ph.split()[0] if ph else "") for n, *_, ph, _f in graph}
        self.contracts = {n: {c.split("/", 1)[1] for c in refs} for n, _t, _d, _l, refs, *_ in graph}
        self.tokens = gl.file_tokens(graph)
        self.label = gl.effort_labels(graph, efforts)
        self.own_greens = {r: [g for g in numbers if self.phase[g] in ("GREEN", "prose")
                               and r in self.deps[g] and self.contracts[g] & self.contracts[r]]
                           for r in numbers if self.phase[r] == "RED"}

    def _known(self, n: str, where: str) -> int:
        if not n.isdigit() or int(n) not in self.order:
            raise Refusal(f"{where}: increment {n} is not in §9 of {self.rel(self.plan)}")
        return int(n)

    def _read_record(self):
        self.red: dict[int, dict[str, str]] = {}
        self.tests: dict[int, set[str]] = {}
        self.wrong: dict[int, str] = {}
        self.ruled: set[tuple[str, int, str, str]] = set()
        self.expected: set[str] = set()
        self.not_run: set[str] = set()
        self.fails: set[tuple[int, str]] = set()
        if not self.record_path.is_file():
            return
        shown = self.rel(self.record_path)
        for i, raw in enumerate(read_utf8(self.record_path, shown).splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            where = f"{shown}:{i}"
            kind, _, rest = line.partition(" ")
            rest = rest.strip()
            if kind not in KINDS:
                raise Refusal(f"{where}: unknown kind {kind!r} ({', '.join(KINDS)})")
            if not rest:
                raise Refusal(f"{where}: {kind} carries nothing")
            if kind == "red":
                f = rest.split(" ", 2)
                if len(f) < 3 or not SHA_RE.match(f[1]):
                    raise Refusal(f"{where}: red is `red <increment> <sha256> <path>`")
                self.red.setdefault(self._known(f[0], where), {})[f[2]] = f[1]
            elif kind in ("test", "wrong", "fail"):
                f = rest.split(" ", 1)
                if len(f) < 2:
                    raise Refusal(f"{where}: {kind} is `{kind} <increment> <text>`")
                n = self._known(f[0], where)
                if kind == "test":
                    self.tests.setdefault(n, set()).add(f[1])
                elif kind == "wrong":
                    self.wrong[n] = f[1]
                else:
                    self.fails.add((n, f[1]))
            elif kind == "ruled":
                f = rest.split(" ", 3)
                if len(f) < 4 or not SHA_RE.match(f[2]):
                    raise Refusal(f"{where}: ruled is `ruled <ruling> <increment> <sha256> <path>`")
                self.ruled.add((f[0], self._known(f[1], where), f[2], f[3]))
            elif kind == "expected-red":
                self.expected.add(rest)
            else:
                self.not_run.add(rest)

    def _read_spawns(self):
        self.in_flight: dict[int, tuple[str, str]] = {}
        log = self.plan.parent / "spawns.jsonl"
        self.spawns: list[dict] = []
        if not log.is_file():
            return
        for i, raw in enumerate(read_utf8(log, self.rel(log)).splitlines(), 1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except ValueError:
                row = None
            if not isinstance(row, dict):
                raise Refusal(f"{self.rel(log)}:{i}: not a JSON object")
            self.spawns.append(row)

    def _read_questions(self):
        self.entries: list[dict] = []
        qdir = self.unit_dir / "questions"
        if not qdir.is_dir():
            return
        files = sorted(qdir.glob("batch-*.md"),
                       key=lambda p: (int(m.group(1)) if (m := re.search(r"(\d+)", p.stem)) else 0, p.name))
        for path in files:
            text = path.read_text(encoding="utf-8", errors="replace")
            ruled = set(re.findall(r"^###\s+R(\d+\.\d+)\b", text, re.M))
            for m in re.finditer(r"^##\s+Q(\d+\.\d+)\b.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S):
                body = dict((k.lower(), v.strip()) for k, v in
                            re.findall(r"^-\s*(where|work held|proposed reading):(.*)$", m.group(2), re.M | re.I))
                self.entries.append({
                    "id": "Q" + m.group(1), "key": tuple(int(x) for x in m.group(1).split(".")),
                    "file": f"questions/{path.name}", "ruled": m.group(1) in ruled,
                    "provisional": body.get("proposed reading", "").lower().startswith("provisional"),
                    "text": f"{body.get('where', '')} {body.get('work held', '')}"})

    def _read_commits(self):
        log = git(self.top, "log", "--format=%s", "HEAD")
        named_slugs = None
        if log.returncode == 0:
            named_slugs = {s for line in log.stdout.splitlines()
                           if (m := GREEN_SUBJECT.match(line)) for s in SLUG_RE.findall(m.group(1))}
        self.committed: set[int] = set()
        self.unknown: list[int] = []
        for n in self.order:
            if named_slugs is None or not self.contracts[n]:
                self.unknown.append(n)
            elif self.contracts[n] <= named_slugs:
                self.committed.add(n)

    # ---- derived state ---------------------------------------------------------
    def recorded(self) -> set[int]:
        return {n for n in self.red if n not in self.wrong}

    def lane_live(self, r: int) -> bool:
        """An observed RED holds its files as a live lane until its own GREEN commits."""
        return not any(g in self.committed for g in self.own_greens.get(r, []))

    def satisfied(self, d: int, n: int) -> bool:
        if self.phase[d] == "RED":
            og = self.own_greens.get(d, [])
            if n in og:
                return d in self.recorded()
            return any(g in self.committed for g in og)
        return d in self.committed

    def touches(self, e: dict, n: int) -> int:
        """0, or the condition (1, or 2 for its own RED's test) an entry holds n under."""
        text = e["text"]
        if any(p in text for p in self.red.get(n, {})):
            return 2
        if n in named(text) or any(t in text for t in self.tokens[n]) \
                or self.contracts[n] & set(SLUG_RE.findall(text)):
            return 1
        return 0

    def state(self):
        nums = sorted(self.order, key=self.order.get)
        recorded = self.recorded()
        unruled = sorted((e for e in self.entries if not e["ruled"]), key=lambda e: (e["file"], e["key"]))
        holding = [e for e in unruled if not e["provisional"]]
        held: dict[int, str] = {}
        for n in nums:
            why = []
            for e in holding:
                c = self.touches(e, n)
                if c == 1:
                    why.append((1, f"condition 1: unruled {e['id']} in {e['file']} touches it"))
                elif c == 2:
                    path = next(p for p in sorted(self.red[n]) if p in e["text"])
                    why.append((2, f"condition 2: unruled {e['id']} in {e['file']} questions its test {path}"))
            if n in self.wrong:
                why.append((2, f"condition 2: its RED failed for the wrong reason: {self.wrong[n]}"))
            for fn, tid in sorted(self.fails):
                if fn == n:
                    why.append((3, f"condition 3: tip failure {tid} attributed to it"))
            if why:
                held[n] = min(why, key=lambda w: w[0])[1]
            elif n not in self.committed:
                via = next((d for d in self.deps[n] if d in held), None)
                if via is not None:
                    held[n] = f"with increment {via}, which it depends on"
        unattributed = [e for e in holding if not any(self.touches(e, n) for n in nums)]

        flight: dict[int, str] = {}
        for row in self.spawns:
            role = str(row.get("role", ""))
            for n in sorted(named(str(row.get("task", ""))) & set(nums)):
                ph = self.phase[n]
                fits = (role == "tester") if ph == "RED" else (role == "implementer") if ph == "GREEN" \
                    else role not in NOT_PROSE_WORKERS
                done = (n in self.red or n in self.wrong) if ph == "RED" else n in self.committed
                if fits and not done:
                    flight[n] = f"{row.get('spawn_id', '?')} ({role}), " + \
                        ("no RED recorded" if ph == "RED" else "not committed")

        lanes: list[tuple[int, str, set[int]]] = []     # (owner, file, increments the lane admits)
        for m in sorted(flight):
            lanes += [(m, t, {m}) for t in self.tokens[m]]
        for r in sorted(recorded):
            if self.lane_live(r):
                lanes += [(r, p, {r, *self.own_greens.get(r, [])}) for p in sorted(self.red[r])]
        ready: dict[str, list[int]] = {"RED": [], "prose": [], "GREEN": []}
        waits: list[str] = []
        for n in nums:
            ph = self.phase[n]
            if ph not in ready or n in self.committed or n in held or n in flight \
                    or (ph == "RED" and (n in self.red or n in self.wrong)):
                continue
            if not all(self.satisfied(d, n) for d in self.deps[n]):
                continue
            clash = next(((m, f) for m, f, admits in lanes if n not in admits
                          for t in self.tokens[n] if self.gl.shared_file(t, f)), None)
            if clash:
                waits.append(f"waits: increment {n} — shares {clash[1]} with the live lane of increment {clash[0]}")
                continue
            ready[ph].append(n)

        expected = sorted({t for r in recorded if self.lane_live(r) for t in self.tests.get(r, ())})
        mismatches = []
        for r in sorted(recorded):
            if not self.lane_live(r):
                continue
            for p, want in sorted(self.red[r].items()):
                f = self.top / p
                now = sha256(f)[:12] if f.is_file() else "missing"
                if now != want[:12]:
                    mismatches.append(f"mismatch: {p} — increment {r} recorded {want[:12]}, now {now}")
        return held, unruled, unattributed, flight, waits, ready, expected, mismatches

    # ---- the report --------------------------------------------------------------
    def report(self) -> tuple[list[str], int]:
        held, unruled, unattributed, flight, waits, ready, expected, mismatches = self.state()
        out = [f"cycle: {self.plan.name}, unit {self.unit_dir.name} — {len(self.order)} increment(s): "
               f"{len(self.committed)} committed, {len(self.recorded())} RED observed, "
               f"{len(flight)} in flight, {len(held)} held"]
        worker = self.gl.WORKER
        for ph in ("RED", "prose", "GREEN"):
            if ready[ph]:
                for _b, describe in self.gl.pack(ready[ph], ph, self.tokens, self.label, self.order, []):
                    out.append(f"ready {ph} {worker[ph]}: {describe}")
        if not any(ready.values()):
            out.append("ready: nothing is ready to spawn")
        out += [f"in flight: increment {n} — {flight[n]}" for n in sorted(flight)]
        out += waits
        out += [f"held: increment {n} — {held[n]}" for n in sorted(held)]
        if self.committed:
            out.append("landed (inferred from commit subjects): increment(s) "
                       + ", ".join(map(str, sorted(self.committed, key=self.order.get))))
        if self.unknown:
            out.append("landed: unknown (no commit names its contracts) — increment(s) "
                       + ", ".join(map(str, self.unknown)))
        out += [f"expected-red: {t}" for t in expected] or ["expected-red: none"]
        out += [f"not run: {t}" for t in sorted(self.not_run)]
        out += mismatches
        out += [f"question: {e['id']} in {e['file']} touches no increment by number, file or contract "
                f"— the lead attributes it" for e in unattributed]
        why = []
        if unruled:
            why.append("unruled " + ", ".join(e["id"] + (" (provisional)" if e["provisional"] else "")
                                              for e in unruled))
        if held:
            why.append("held increments " + ", ".join(map(str, sorted(held))))
        out.append(f"ruling pass: owed — {'; '.join(why)}" if why
                   else "ruling pass: not owed — no unruled question entry and nothing held")
        return out, 1 if mismatches else 0

    # ---- writes ----------------------------------------------------------------
    def write_record(self):
        rows: list[tuple] = []
        rows += [(0, n, p, f"red {n} {s} {p}") for n, files in self.red.items() for p, s in files.items()]
        rows += [(1, n, t, f"test {n} {t}") for n, ts in self.tests.items() for t in ts]
        rows += [(2, n, "", f"wrong {n} {why}") for n, why in self.wrong.items()]
        rows += [(3, n, f"{rid} {p}", f"ruled {rid} {n} {s} {p}") for rid, n, s, p in self.ruled]
        rows += [(4, 0, t, f"expected-red {t}") for t in self.expected]
        rows += [(5, 0, t, f"not-run {t}") for t in self.not_run]
        rows += [(6, n, t, f"fail {n} {t}") for n, t in self.fails]
        text = "\n".join([HEADER] + [r[3] for r in sorted(rows)]) + "\n"
        self.unit_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.record_path.with_name(f".{self.record_path.name}.tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, self.record_path)

    def record_red(self, n: int, files: list[str], tests: list[str], wrong: str | None, ruling: str | None) -> str:
        shown = self.rel(self.plan)
        if n not in self.order:
            raise Refusal(f"{shown}: increment {n} is not in §9")
        if self.phase[n] != "RED":
            raise Refusal(f"{shown}: increment {n} is {self.phase[n] or 'without a Phase:'}, not a RED")
        rec = self.rel(self.record_path)
        if wrong is not None:
            if files or tests:
                raise Refusal(f"{rec}: --wrong records no files and no test ids")
            if not wrong.strip():
                raise Refusal(f"{rec}: --wrong needs the reason")
            self.red.pop(n, None)
            self.tests.pop(n, None)
            self.wrong[n] = " ".join(wrong.split())
            self.write_record()
            return f"recorded: increment {n} — the RED failed for the wrong reason, in {rec}"
        if not files or not tests:
            raise Refusal(f"{rec}: record-red needs at least one --file and one --test")
        new: dict[str, str] = {}
        for f in files:
            p = Path(f) if Path(f).is_absolute() else Path.cwd() / f
            try:
                rp = str(p.resolve().relative_to(self.top))
            except ValueError:
                raise Refusal(f"{f}: outside the work tree {self.top}")
            if not p.is_file():
                raise Refusal(f"{f}: no such file")
            new[rp] = sha256(p)
        old = self.red.get(n, {})
        if old and old != new:
            if not ruling:
                raise Refusal(f"{rec}: increment {n} already has RED hashes that differ; a re-record "
                              f"after a ruling names it with --ruling RID")
            for p, s in old.items():
                if new.get(p) != s:
                    self.ruled.add((ruling, n, s, p))
        self.red[n] = new
        self.tests[n] = {" ".join(t.split()) for t in tests if t.strip()}
        self.wrong.pop(n, None)
        self.write_record()
        return f"recorded: increment {n} — {len(new)} file(s), {len(self.tests[n])} test id(s) in {rec}"

    def record_tip(self, not_run: list[str], fails: list[list[str]]) -> str:
        rec = self.rel(self.record_path)
        attributed = set()
        for n, tid in fails:
            attributed.add((self._known(n, rec), " ".join(tid.split())))
        expected = self.state()[6]
        self.expected = set(expected)
        self.not_run = {" ".join(t.split()) for t in not_run if t.strip()}
        self.fails = attributed
        self.write_record()
        return (f"recorded: tip — {len(self.expected)} expected-red, {len(self.not_run)} not run, "
                f"{len(self.fails)} failure(s) attributed in {rec}")


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv and argv[0] in ("record-red", "record-tip") else None
    ap = argparse.ArgumentParser(prog=f"cycle.py{' ' + cmd if cmd else ''}", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    if cmd == "record-red":
        ap.add_argument("increment", type=int)
        ap.add_argument("--file", action="append", default=[])
        ap.add_argument("--test", action="append", default=[])
        ap.add_argument("--wrong")
        ap.add_argument("--ruling")
    elif cmd == "record-tip":
        ap.add_argument("--not-run", action="append", default=[])
        ap.add_argument("--fail", nargs=2, action="append", default=[], metavar=("N", "ID"))
    ap.add_argument("--unit", required=True, help="the unit of work: docs/graph/plans/<unit>/")
    ap.add_argument("--plan", default=str(HERE / "plans" / "grill.md"))
    args = ap.parse_args(argv[1:] if cmd else argv)
    try:
        if "/" in args.unit or args.unit in ("", ".", ".."):
            raise Refusal(f"--unit {args.unit!r}: one directory name under the plan's directory")
        cyc = Cycle(Path(args.plan), args.unit)
        if cmd == "record-red":
            print(cyc.record_red(args.increment, args.file, args.test, args.wrong, args.ruling))
            return 0
        if cmd == "record-tip":
            print(cyc.record_tip(args.not_run, args.fail))
            return 0
        lines, rc = cyc.report()
    except Refusal as e:
        print(f"cycle: {e}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
