---
stack:
  - library-corpus/cli/trivy
  - library-corpus/container/docker
---
# Tool: container-vuln-scan-and-aggregate

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Two halves: a scan driver (a **BLUEPRINT**, because
> it drives a container engine and a scanner image the adopting project pins)
> and a report aggregator (a complete stdlib script with its own fixture
> self-test). The scanner surface is Trivy's; its flags and failure modes are on
> `library-corpus/cli/trivy.md` and are linked, not restated.

## 0. Identity

- **Category:** ops
- **Name:** container-vuln-scan-and-aggregate
- **Language / runtime:** the driver is bash plus a container engine and the
  scanner run as a container (nothing installed on the host); the aggregator
  is python3, stdlib only.
- **Stability:** **portable** for the aggregator (§3.2), which ran its
  self-test and a synthetic report set when it was folded in (§6). The driver
  (§3.1) is a blueprint: it is syntax-checked and its flags are taken from the
  scanner's own reference, but its socket, cache and user wiring depend on
  the host.

## 1. What it does

Answers "which images that this project will deploy, and which of its declared
dependencies, carry known vulnerabilities, and how bad are they?" with numbers
a reviewer can trust. It exists because the two common shortcuts both mislead:
recalling advisories by hand misses most of them and invents some, and a
scanner run over "whatever images are on this host" scans the wrong set.

- The **driver** scans each image on an explicit target list, and optionally a
  directory of dependency manifests in filesystem (SCA) mode, with a pinned
  scanner image. It writes one JSON report per target and fails when any
  target produced no report.
- The **aggregator** reads those reports and prints, per target, the counts by
  severity and a deduplicated top-N table (severity, best CVSS, advisory id,
  package, installed and fixed version), then a total. It can refuse stale or
  missing reports, diff against an earlier run, and apply a fail threshold
  that the caller chooses.

The output is the ground truth that a security review checks its claims
against: a finding recalled from memory that the scanner does not show is
re-checked, not repeated.

## 2. Interface & invocation

```sh
# 1. build or pull exactly the images that will deploy, then scan them
SCANNER_IMAGE=<scanner image pinned by digest> \
  vuln-scan-fleet.sh <out-dir> $(docker compose config --images)

# 2. summarize; quote the glob
vuln-scan-aggregate.py --expect <n targets> --since <out-dir>/.scan-started \
  [--baseline '<previous-run>/*.json'] [--fail-on CRITICAL,HIGH] '<out-dir>/*.json'
```

- **Driver inputs:** an output directory; the image references to scan (no
  default: `docker compose config --images` prints the images a Compose
  project names, which is the usual source); `SCANNER_IMAGE`, required and
  pinned by digest; optional `CACHE_DIR`, `MANIFEST_DIR`, `CONFIG_DIR` and
  `SKIP_DB_UPDATE=1` (skips both the vulnerability database and the Java
  index database update).
- **Driver outputs:** `<out-dir>/<target>.json` per image (with `/`, `:` and
  `@` mapped to `_`), `<out-dir>/manifests.json` when `MANIFEST_DIR` is set,
  `<out-dir>/misconfig/config.json` when `CONFIG_DIR` is set, this run's
  stderr in `<out-dir>/scan.err`, and a `.scan-started` marker. Exit 0 when
  every target produced a non-empty report; 2 for a failed target, a missing
  argument or an unset `SCANNER_IMAGE`.
- **Aggregator inputs:** a quoted glob of reports; optional `--top N`
  (default 10), `--expect N`, `--since <marker>`, `--baseline '<glob>'`,
  `--fail-on <severities>`. `--expect` counts every report the glob matches,
  so with `MANIFEST_DIR` set it is the number of images plus one. Give each
  run its own output directory, or copy the previous reports aside first:
  the driver deletes `*.json` in its output directory, so a `--baseline` glob
  that points there finds nothing from the earlier run.
- **Aggregator outputs:** per-target blocks and a total line; with
  `--baseline`, the findings that are new and the ones that are resolved,
  keyed by target, advisory id and package.
- **Aggregator exit codes:** 0 report written and no `--fail-on` severity
  present; 1 a `--fail-on` severity is present, or `--baseline` found new
  findings while `--fail-on` is set; 2 usage error, no file matched, a file
  that does not parse, a count that differs from `--expect`, or a report older
  than `--since`.
- **Preconditions:** a container engine; the images present locally (built or
  pulled first); network access to the scanner's databases unless an
  up-to-date cache is supplied.

## 3. Approach / algorithm

### 3.1 The scan driver (blueprint)

1. **Fix the target list before scanning.** Build or pull the deploy set,
   then pass exactly those references. A scan of every local image includes
   leftovers and misses anything not yet built.
2. **Pin the scanner.** A `latest` scanner tag changes the rules between two
   runs that are meant to be compared. The scanner's results are outside its
   own compatibility policy (`library-corpus/cli/trivy.md`, "Major lines"), so
   a scanner bump is a reason to re-scan a known target and diff.
3. **One report per target, JSON.** Text tables are for people; the JSON is
   what the aggregator, the diff and any gate read.
4. **Clear old reports and mark the start.** A report left by an earlier run
   passes a presence check with old numbers. The driver deletes `*.json` in
   the output directory and touches `.scan-started` before the first scan; the
   aggregator's `--since` refuses any report older than that marker.
5. **Count failures, do not swallow them.** A target whose scan exits non-zero
   or leaves no report is a failure of the run. The driver exits 2 and names
   it; it never writes a zero for it.
6. **Scan the configuration too, apart.** With `CONFIG_DIR` set, the driver
   runs the scanner's `config` target over that directory, mounted read-only,
   for Dockerfile and IaC misconfigurations (`library-corpus/cli/trivy.md`,
   "Core API / usage shape" and "Misconfiguration in images"). It writes its own JSON under `misconfig/`, outside the
   aggregator's glob, because the aggregator reads vulnerabilities only.

The driver runs the scanner with `docker run` from the host. A project that
wants the scan inside Compose instead declares a scanner service under
`profiles: ["security"]`, so it starts only on request, with the same socket
and cache mounts and an entrypoint script that runs these same commands inside
the scanner container.

```bash
#!/usr/bin/env bash
# vuln-scan-fleet.sh: scan every image that will deploy, plus the project's
# dependency manifests, with a containerized and pinned scanner. One JSON
# report per target. Usage: vuln-scan-fleet.sh <out-dir> <image> [<image> ...]
# Env: SCANNER_IMAGE (required, pinned by digest), CACHE_DIR (default
#      ~/.cache/vuln-scan), MANIFEST_DIR (optional, scanned in filesystem mode),
#      SKIP_DB_UPDATE=1 (offline, only when the cached DBs are known current),
#      CONFIG_DIR (optional, misconfiguration pass, report in <out-dir>/misconfig/).
set -uo pipefail
[ "$#" -ge 1 ] || { echo "usage: vuln-scan-fleet.sh <out-dir> <image> [<image> ...]" >&2; exit 2; }
OUT="$1"; shift
[ "$#" -gt 0 ] || { echo "no image given: refusing to report an empty scan" >&2; exit 2; }
[ -n "${SCANNER_IMAGE:-}" ] || { echo "set SCANNER_IMAGE to a digest-pinned scanner image" >&2; exit 2; }
CACHE="${CACHE_DIR:-$HOME/.cache/vuln-scan}"
mkdir -p "$OUT" "$CACHE"
SOCK_GID="$(stat -c %g /var/run/docker.sock 2>/dev/null || stat -f %g /var/run/docker.sock)"
rm -f "$OUT"/*.json "$OUT"/misconfig/*.json  # never let an old report pass as this run's
: > "$OUT/scan.err"                     # this run's errors only
touch "$OUT/.scan-started"
db=(); [ "${SKIP_DB_UPDATE:-0}" = 1 ] && db=(--skip-db-update --skip-java-db-update)
failed=0
scan() {  # scan <out-name> <scanner args...>
  local name="$1"; shift
  docker run --rm --user "$(id -u):$(id -g)" --group-add "$SOCK_GID" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$CACHE":/cache -v "$(cd "$OUT" && pwd)":/out \
    "$SCANNER_IMAGE" "$@" --cache-dir /cache "${db[@]}" \
      --format json --output "/out/$name.json" --quiet 2>>"$OUT/scan.err"
  if [ $? -ne 0 ] || [ ! -s "$OUT/$name.json" ]; then
    echo "FAILED $name" >&2; failed=$((failed + 1))
  else
    echo "ok     $name"
  fi
}
for img in "$@"; do
  scan "$(printf '%s' "$img" | tr '/:@' '___')" image --scanners vuln "$img"
done
if [ -n "${MANIFEST_DIR:-}" ]; then
  docker run --rm --user "$(id -u):$(id -g)" -v "$CACHE":/cache \
    -v "$(cd "$MANIFEST_DIR" && pwd)":/src:ro -v "$(cd "$OUT" && pwd)":/out \
    "$SCANNER_IMAGE" fs --scanners vuln --cache-dir /cache "${db[@]}" \
      --format json --output /out/manifests.json --quiet /src 2>>"$OUT/scan.err"
  if [ $? -ne 0 ] || [ ! -s "$OUT/manifests.json" ]; then
    echo "FAILED manifests" >&2; failed=$((failed + 1))
  else
    echo "ok     manifests"
  fi
fi
if [ -n "${CONFIG_DIR:-}" ]; then        # misconfigurations, not vulnerabilities:
  mkdir -p "$OUT/misconfig"              # kept out of the aggregator's glob
  docker run --rm --user "$(id -u):$(id -g)" -v "$CACHE":/cache \
    -v "$(cd "$CONFIG_DIR" && pwd)":/src:ro -v "$(cd "$OUT/misconfig" && pwd)":/out \
    "$SCANNER_IMAGE" config --cache-dir /cache \
      --format json --output /out/config.json --quiet /src 2>>"$OUT/scan.err"
  if [ $? -ne 0 ] || [ ! -s "$OUT/misconfig/config.json" ]; then
    echo "FAILED config" >&2; failed=$((failed + 1))
  else
    echo "ok     config"
  fi
fi
[ "$failed" -eq 0 ] || { echo "$failed target(s) failed: see $OUT/scan.err" >&2; exit 2; }
```

### 3.2 The aggregator (portable)

1. Expand the quoted glob; no match is exit 2. With `--since`, any report
   older than the marker is exit 2. With `--expect`, a different count is
   exit 2: a missing target is a failed run, not a clean one.
2. Parse each file as JSON and require `ArtifactName`; anything else is
   exit 2 with the file named.
3. For each vulnerability, count it under its severity (any value outside
   CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN counts as UNKNOWN), and take the best
   CVSS score across every source in its `CVSS` object, reading `V40Score`,
   `V3Score` and `V2Score`. These are the score keys the scanner writes. Use
   the score only for ordering; the advisory id is the authority.
4. Sort by severity, then descending score, then id; deduplicate the top table
   by advisory id, package and installed version; print the top N at MEDIUM
   and above. Totals count every occurrence, so the same advisory in two
   copies of a library counts twice.
5. Print LOW and UNKNOWN apart from the MEDIUM-and-above totals, so a zero
   at MEDIUM and above is never read as "no findings". Print a note for a
   report with no `Results`, and for one whose `Metadata.OS.EOSL` is true.
6. With `--baseline`, compare the set of (target, advisory id, package) at
   MEDIUM and above with the earlier run's set, and list what is new and what
   was resolved.
7. With `--fail-on`, exit 1 when the total holds any listed severity. The
   threshold is the caller's decision, so there is no default.

```python
#!/usr/bin/env python3
"""vuln-scan-aggregate: summarize scanner JSON reports (Trivy's JSON shape)
into per-target severity totals and a deduplicated top-N table.

Usage:
  vuln-scan-aggregate.py [--top N] [--expect N] [--since FILE]
                         [--baseline 'OLD_GLOB'] [--fail-on SEV[,SEV]] 'GLOB'
  vuln-scan-aggregate.py --self-test

Quote the glob: the script expands it. Exit 0: report written (and no
--fail-on severity found). Exit 1: a --fail-on severity was found, or
--baseline found new findings while --fail-on is set. Exit 2: usage error,
no file matched, a file that does not parse, a count that differs from
--expect, or a report older than --since.
"""
import argparse
import glob
import json
import os
import sys
import tempfile

RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
TOTALLED = ("CRITICAL", "HIGH", "MEDIUM")
# Trivy's CVSS object per source: V40Score, V3Score, V2Score (trivy-db types).
SCORE_KEYS = ("V40Score", "V3Score", "V2Score")


def best_cvss(v):
    best = 0.0
    for data in (v.get("CVSS") or {}).values():
        for k in SCORE_KEYS:
            s = (data or {}).get(k)
            if isinstance(s, (int, float)) and s > best:
                best = float(s)
    return best


class ReportError(Exception):
    pass


def summarize(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise ReportError(f"{path}: not a readable JSON report ({exc})")
    if not isinstance(data, dict) or "ArtifactName" not in data:
        raise ReportError(f"{path}: no ArtifactName; not a scanner JSON report")
    counts = {s: 0 for s in RANK}
    vulns = []
    results = data.get("Results")
    for res in results or []:
        for v in res.get("Vulnerabilities") or []:
            sev = v.get("Severity", "UNKNOWN")
            sev = sev if sev in RANK else "UNKNOWN"
            counts[sev] += 1
            vulns.append({"id": v.get("VulnerabilityID", ""), "pkg": v.get("PkgName", ""),
                          "installed": v.get("InstalledVersion", ""),
                          "fixed": v.get("FixedVersion") or "-", "sev": sev,
                          "cvss": best_cvss(v)})
    vulns.sort(key=lambda x: (RANK[x["sev"]], -x["cvss"], x["id"]))
    seen, uniq = set(), []
    for v in vulns:
        key = (v["id"], v["pkg"], v["installed"])
        if key not in seen:
            seen.add(key)
            uniq.append(v)
    eosl = bool(((data.get("Metadata") or {}).get("OS") or {}).get("EOSL"))
    return {"name": data.get("ArtifactName"), "type": data.get("ArtifactType", ""),
            "counts": counts, "vulns": uniq, "has_results": results is not None,
            "eosl": eosl}


def load_all(pattern, since):
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise ReportError(f"no file matched {pattern!r} (quote the glob)")
    if since:
        floor = os.path.getmtime(since)
        old = [p for p in paths if os.path.getmtime(p) < floor]
        if old:
            raise ReportError("report(s) older than --since, left by an earlier run: "
                              + ", ".join(old))
    return paths, [summarize(p) for p in paths]


def keys_of(reports):
    return {(r["name"], v["id"], v["pkg"]) for r in reports for v in r["vulns"]
            if v["sev"] in TOTALLED}


def run(a, out=sys.stdout):
    try:
        paths, reports = load_all(a.glob, a.since)
        if a.expect is not None and len(paths) != a.expect:
            raise ReportError(f"expected {a.expect} report(s), found {len(paths)}: "
                              "a target was not scanned, or an extra file is in the directory")
        base = load_all(a.baseline, None)[1] if a.baseline else None
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    grand = {s: 0 for s in RANK}
    for p, r in zip(paths, reports):
        for s in RANK:
            grand[s] += r["counts"][s]
        c = r["counts"]
        print("=" * 72, file=out)
        print(f"TARGET {r['name']} [{r['type']}] file={os.path.basename(p)}", file=out)
        print(f"  CRITICAL={c['CRITICAL']} HIGH={c['HIGH']} MEDIUM={c['MEDIUM']} "
              f"(below MEDIUM: LOW={c['LOW']} UNKNOWN={c['UNKNOWN']})", file=out)
        if not r["has_results"]:
            print("  note: the report has no Results section; nothing was inventoried",
                  file=out)
        if r["eosl"]:
            print("  note: the OS is past its end of service life; detection may be "
                  "insufficient, so low counts here do not mean clean", file=out)
        top = [v for v in r["vulns"] if v["sev"] in TOTALLED][: a.top]
        for v in top:
            print(f"    {v['sev']:8} {v['cvss']:4.1f} {v['id']:20} {v['pkg']:30} "
                  f"{v['installed']} -> {v['fixed']}", file=out)
    print("=" * 72, file=out)
    print(f"TOTAL {len(paths)} target(s): CRITICAL={grand['CRITICAL']} HIGH={grand['HIGH']} "
          f"MEDIUM={grand['MEDIUM']} (below MEDIUM: LOW={grand['LOW']} "
          f"UNKNOWN={grand['UNKNOWN']})", file=out)
    rc = 0
    if base is not None:
        now, then = keys_of(reports), keys_of(base)
        new, gone = sorted(now - then), sorted(then - now)
        print(f"BASELINE new={len(new)} resolved={len(gone)}", file=out)
        for k in new:
            print(f"  NEW      {k[0]}  {k[1]}  {k[2]}", file=out)
        for k in gone:
            print(f"  RESOLVED {k[0]}  {k[1]}  {k[2]}", file=out)
        if new and a.fail_on:
            rc = 1
    if a.fail_on:
        bad = [s for s in a.fail_on.split(",") if grand.get(s.strip().upper(), 0)]
        if bad:
            print(f"FAIL: findings at {','.join(bad)}", file=out)
            rc = 1
    return rc


def self_test():
    import io
    def report(name, vulns):
        return {"SchemaVersion": 2, "ArtifactName": name, "ArtifactType": "container_image",
                "Results": [{"Target": name, "Class": "os-pkgs", "Vulnerabilities": vulns}]}
    def v(i, pkg, sev, cvss, fixed="1.1"):
        d = {"VulnerabilityID": i, "PkgName": pkg, "InstalledVersion": "1.0",
             "Severity": sev, "CVSS": {"nvd": {"V3Score": cvss}}}
        if fixed:
            d["FixedVersion"] = fixed
        return d
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        new, old = os.path.join(tmp, "new"), os.path.join(tmp, "old")
        os.mkdir(new); os.mkdir(old)
        cur = [v("TEST-0002", "libb", "HIGH", 7.5, fixed=None), v("TEST-0001", "liba", "CRITICAL", 9.8),
               v("TEST-0001", "liba", "CRITICAL", 9.8), v("TEST-0003", "libc", "MEDIUM", 5.0),
               v("TEST-0004", "libd", "LOW", 2.0)]
        json.dump(report("example/app:1", cur), open(os.path.join(new, "app.json"), "w"))
        json.dump({"SchemaVersion": 2, "ArtifactName": "example/empty:1",
                   "Metadata": {"OS": {"Family": "example", "EOSL": True}}},
                  open(os.path.join(new, "empty.json"), "w"))
        json.dump(report("example/app:1", [v("TEST-0003", "libc", "MEDIUM", 5.0),
                                           v("TEST-0009", "libz", "HIGH", 8.0)]),
                  open(os.path.join(old, "app.json"), "w"))
        def go(*argv):
            ap = parser(); a = ap.parse_args(list(argv)); buf = io.StringIO()
            return run(a, out=buf), buf.getvalue()
        g = os.path.join(new, "*.json")
        rc, text = go(g)
        checks += [
            (rc == 0, "a plain report exits 0"),
            ("CRITICAL=2 HIGH=1 MEDIUM=1 (below MEDIUM: LOW=1 UNKNOWN=0)" in text,
             "totals count every occurrence; LOW and UNKNOWN shown apart"),
            (text.index("TEST-0001") < text.index("TEST-0002"), "CRITICAL ordered first"),
            (" 9.8 " in text, "V3Score read (the key Trivy writes)"),
            ("-> -" in text, "a missing FixedVersion renders as -"),
            (text.count("TEST-0001") == 1, "top table deduplicated"),
            ("nothing was inventoried" in text, "a report with no Results says so"),
            ("end of service life" in text, "an end-of-life OS is flagged"),
        ]
        rc, text = go("--fail-on", "CRITICAL", g)
        checks.append((rc == 1 and "FAIL: findings at CRITICAL" in text, "--fail-on fails"))
        rc, text = go("--baseline", os.path.join(old, "*.json"), g)
        checks.append(("BASELINE new=2 resolved=1" in text, "baseline diff by finding key"))
        checks.append((go("--expect", "3", g)[0] == 2, "--expect mismatch exits 2"))
        checks.append((go(os.path.join(tmp, "none", "*.json"))[0] == 2, "no match exits 2"))
        open(os.path.join(new, "broken.json"), "w").write("{")
        checks.append((go(g)[0] == 2, "an unparseable report exits 2"))
        os.remove(os.path.join(new, "broken.json"))
        marker = os.path.join(tmp, "marker")
        open(marker, "w").write("")
        os.utime(os.path.join(new, "app.json"), (0, 0))
        checks.append((go("--since", marker, g)[0] == 2, "a stale report exits 2"))
    failed = [n for ok, n in checks if not ok]
    for n in failed:
        print(f"FAIL {n}", file=sys.stderr)
    print("self-test:", "FAIL" if failed else f"PASS ({len(checks)} checks)")
    return 1 if failed else 0


def parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("glob", nargs="?")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--expect", type=int)
    ap.add_argument("--since")
    ap.add_argument("--baseline")
    ap.add_argument("--fail-on", default="")
    ap.add_argument("--self-test", action="store_true")
    return ap


def main():
    ap = parser()
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.glob:
        ap.print_usage(sys.stderr)
        return 2
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
```

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the aggregator script with its self-test; the
  rules it encodes (stale and missing reports refused, every score key read,
  LOW and UNKNOWN shown apart, baseline diff by finding key, caller-chosen
  threshold).
- **Blueprint (write per host):** the driver's container wiring. Check, on the
  adopting host: where the engine socket lives and which group owns it; that
  the cache directory is writable by the user the scanner runs as; whether
  the scanner should run as the caller (the scanner page notes that a root
  container leaves root-owned reports a later cleanup cannot remove); and the
  scanner image digest.
- **Adopting note:** another scanner works if its JSON is mapped to the same
  fields (target name, advisory id, package, installed and fixed version,
  severity, scores) before the aggregator reads it. Keep the mapping in a
  separate step so the aggregator's tests still apply.

## 5. Pitfalls and sharp edges

- **Only local images are scanned in image mode.** Build or pull the deploy
  set first. A reference that is not present locally may fail, or may fall
  through to a registry image of the same name; either way it is not the
  image that deploys (`library-corpus/cli/trivy.md`, "Image source
  surprises").
- **A stale vulnerability database under-reports with no error.** Use
  `SKIP_DB_UPDATE=1` only when the cache is known to be current, and record
  the database timestamp next to the reports when the result is evidence. The
  switch covers the Java index database too: an image with Java artifacts
  otherwise still fetches it.
- **An end-of-life base image can scan clean.** Observed in practice: an
  image whose OS is past its end of service life reported 0 findings, and the
  scanner's only signal was a stderr warning that detection "may be
  insufficient", which `--quiet` suppresses. The JSON keeps the fact in
  `Metadata.OS.EOSL`; the aggregator prints it. The scanner can also fail on
  it by itself with `--exit-on-eol <code>` (`library-corpus/cli/trivy.md`);
  the aggregator's note stays, because it reads the reports after the fact.
  Treat such an image as a finding of its own: move to a supported base.
- **The scan-time severity filter decides what the aggregator can see.** A
  driver run with `--severity MEDIUM,HIGH,CRITICAL` writes no LOW findings,
  and the aggregator then prints LOW=0. The driver above sets no severity
  filter, so the reports are complete and the threshold stays in one place.
- **Quote the glob.** Unquoted, the shell expands it and only the first file
  reaches the script, which then reports one target as if it were all of
  them. `--expect` catches this.
- **Exit 0 with findings is the scanner's default**, and a scanner crash and a
  scanner finding can share exit code 1 (`library-corpus/cli/trivy.md`,
  "General pitfalls"). Gate on the aggregated report, which separates "did not
  run" (exit 2) from "found something" (exit 1).
- **A best-available score is not a source-pinned score.** Two sources can
  score the same advisory differently. Order by it, cite the advisory id.
- **A manifest scan can report a transitive version that does not ship.**
  Rank it on the resolved tree (`tool-corpus/ops/resolved-dependency-gate.md`,
  "Use the effective tree for review ranking too").
- **Residue that no version bump can fix** is recorded once, as
  framework-bound (`skill-corpus/vulnerability-reduction-by-version-bumps.md`,
  "Record framework-bound residue once").
- **Mounting the engine socket gives the scanner full control of the engine.**
  Mount it only where image mode needs it; filesystem mode does not.
- **Reports are sensitive.** They list every vulnerable package in what you
  deploy. Store them as restricted build output.

## 6. Tests that cover it

The aggregator carries its own fixture self-test (`--self-test`). It writes
synthetic reports (advisory ids of the form `TEST-0001`, never real ones) to a
temporary directory and checks: a plain report exits 0; totals count every
occurrence and show LOW and UNKNOWN apart; CRITICAL sorts first; a `V3Score`
is read; a missing fixed version renders as `-`; the top table is
deduplicated; a report with no `Results` says nothing was inventoried;
`--fail-on` exits 1; the baseline diff finds new and resolved findings by
key; an `--expect` mismatch, a glob with no match, an unparseable file and a
report older than `--since` each exit 2; an end-of-life OS is flagged.

Recorded when the page was written:

```
$ python3 vuln-scan-aggregate.py --self-test
self-test: PASS (14 checks)
$ python3 vuln-scan-aggregate.py --expect 2 --fail-on CRITICAL,HIGH 'scan/*.json'
TARGET example/api:2 [container_image] file=api.json
  CRITICAL=0 HIGH=1 MEDIUM=1 (below MEDIUM: LOW=0 UNKNOWN=0)
    HIGH      8.1 TEST-0101            libssl                         3.0.1 -> 3.0.2
    MEDIUM    5.0 TEST-0102            zlib                           1.2 -> -
TARGET example/web:2 [container_image] file=web.json
  CRITICAL=0 HIGH=0 MEDIUM=0 (below MEDIUM: LOW=0 UNKNOWN=0)
TOTAL 2 target(s): CRITICAL=0 HIGH=1 MEDIUM=1 (below MEDIUM: LOW=0 UNKNOWN=0)
FAIL: findings at HIGH
(exit 1; separator lines omitted)
```

The driver and the aggregator were also run once on a host with a container
engine, against two small public images, with the scanner pinned by digest
(the database was fetched on the first run and reused with
`SKIP_DB_UPDATE=1` on the second). Both targets produced a report and the
driver exited 0. The aggregator, given `--expect 2 --since <marker>`, printed
per-target totals (for the larger image, CRITICAL=7 HIGH=96 MEDIUM=166 with
LOW=143 and UNKNOWN=6 shown apart) and flagged both images as past their OS
end of service life. On that real report, 394 of 418 findings carried a CVSS
object, all of them under `V3Score`, `V2Score` or `V40Score`; a reader that
looks for `V31Score` and `V30Score` scored 346 of the 418 as 0. The smaller,
end-of-life image reported 0 findings while the scanner printed, on stderr,
that "the vulnerability detection may be insufficient"; with `--quiet` that
warning is not printed at all, and only `Metadata.OS.EOSL` in the JSON
carries it, which is why the aggregator reads it.

- **How to run the tests:** `python3 vuln-scan-aggregate.py --self-test` for
  the aggregator; for the driver, one run against a small public image whose
  report the aggregator then reads.

## 7. References & neighbours

- **Library pages:** `library-corpus/cli/trivy.md` (targets, scanners, exit
  codes, database and cache behaviour, the pitfalls this page links);
  `library-corpus/container/docker.md` (the engine);
  `library-corpus/container/docker-compose.md` (profiles, `config --images`).
- **Related tools:** `tool-corpus/ops/image-reference-pin-lint.md` (pins the
  references this scans); `tool-corpus/ops/registry-digest-resolver.md`;
  `tool-corpus/ops/resolved-dependency-gate.md` (whether a reported
  transitive version is the one that resolves).
- **Sources:** the scanner's CLI reference for `image`, `fs`, `--format`,
  `--output`, `--cache-dir`, `--skip-db-update`, `--skip-java-db-update` and
  `--exit-on-eol`
  (<https://trivy.dev/docs/latest/references/configuration/cli/trivy_image/>)
  and for `config`
  (<https://trivy.dev/docs/latest/references/configuration/cli/trivy_config/>);
  the scanner database's type definitions for the CVSS keys `V2Score`,
  `V3Score` and `V40Score`
  (<https://github.com/aquasecurity/trivy-db/blob/main/pkg/types/types.go>);
  the Compose CLI reference for `config --images`
  (<https://docs.docker.com/reference/cli/docker/compose/config/>).

## 8. Changelog

- 2026-10-05: created by tool-smith.
  Combines a fleet scan with an aggregator and a Compose-profile scan with a
  misconfiguration pass. Defects avoided: an aggregator that read `V31Score` and `V30Score`, keys the scanner does
  not write, so its ordering ignored every version-3 score; one driver scanned
  every local image with an unpinned `latest` scanner and reported a failed
  target only as a log line; the other swallowed a failed JSON scan with
  `|| true`; neither refused a stale report.
- 2026-10-05: review fixes. The driver's optional misconfiguration pass
  (`CONFIG_DIR`), carried by one source plant, is restored. `SKIP_DB_UPDATE`
  also skips the Java index database. `scan.err` is cleared per run, the
  manifest report is checked for content, and an unset `SCANNER_IMAGE` exits
  2. The scanner's `--exit-on-eol` is named, the baseline needs a separate
  directory, the Compose profile form is described in prose, and two
  restated rules became pointers.
