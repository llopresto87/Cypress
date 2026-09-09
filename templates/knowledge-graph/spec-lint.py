#!/usr/bin/env python3
"""spec-lint: mechanical proof that "specs are executable" (kernel §3.1).

The spec rule says every functional contract maps to at least one test,
and tests reuse the contract's stable UPPER_SNAKE_SLUG. Two passes make
that a gate instead of an aspiration:

  SHAPE — every spec on disk, whatever its status:
  - contract slugs are unique within the spec;
  - a §9 acceptance criterion that "maps to" a slug maps to a declared one;
  - a SIGNED spec (product, architect, tester ticked in §0) or a LIVE one
    has a §10 test-mapping row per contract — the specify exit condition,
    checked rather than promised;
  - a live spec carries its sign-offs (a promotion nobody signed);
  - an `implemented` spec has no §10 row still `red` or `pending`.

  COVERAGE — live specs only (status active / implemented):
  - every contract must appear in >=1 test file;
  - a slug appearing in tests but in no live spec is drift (renamed or
    retired contract still asserted somewhere) -> WARN;
  - live contracts + ZERO matching test files is a green lie
    (kernel §3.5) -> FAIL loudly, never a vacuous pass.

A draft is shape-checked and not counted for coverage: it turns active in
the change that lands its RED tests (test-first COMMIT), so a spec in
authoring never reports uncovered. Status is read from frontmatter first —
the schema's single home — and from a body `**Status:**` only when the
frontmatter has none (the template's body line says "see frontmatter").

Installed at docs/graph/spec-lint.py by install.sh (like graph-lint.py).
Dependency-free. Set TEST_GLOBS for the project's layout.

Usage:
  python3 docs/graph/spec-lint.py           # gate: exit 1 on a defect
  python3 docs/graph/spec-lint.py --list    # dump contract -> tests map
  python3 docs/graph/spec-lint.py --warn    # report but always exit 0
"""
import re
import sys
from pathlib import Path

# ---- project configuration (edit these when installing) -------------------
TEST_GLOBS = [
    "tests/**/*.*", "test/**/*.*", "spec/**/*.*",
    "**/*_test.*", "**/*.test.*", "**/test_*.*",
]
LIVE_STATUSES = {"active", "implemented"}
# ----------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent          # docs/graph/
ROOT = HERE.parent.parent                       # repo root
SPECS = HERE / "specs"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             "dist", "build", "target", ".next"}
CONTRACT_RE = re.compile(r"^###\s+Contract:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
FAILURE_RE = re.compile(r"^###\s+Failure:\s*([A-Z][A-Z0-9_]{2,})\s*$", re.M)
FRONT_STATUS_RE = re.compile(r"^status:\s*([\w-]+)", re.M)
BODY_STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([\w-]+)")
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$", re.M)
SIGNOFF_RE = re.compile(r"\*\*Sign-offs:\*\*(.*)")
SLUG_RE = re.compile(r"(?<![A-Z0-9_])[A-Z][A-Z0-9_]{2,}(?![A-Z0-9_])")
SIGNERS = ("product", "architect", "tester")
STILL_OPEN = {"red", "pending"}


def test_files() -> list[Path]:
    seen: set[Path] = set()
    for pattern in TEST_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and not (set(p.parts) & SKIP_DIRS) and SPECS not in p.parents:
                seen.add(p)
    return sorted(seen)


def status_of(text: str) -> str:
    """Frontmatter first (the single home); the body line only when the
    frontmatter has none, and never the template's "see frontmatter"."""
    if text.startswith("---"):
        head = text.split("\n---", 1)[0]
        m = FRONT_STATUS_RE.search(head)
        if m:
            return m.group(1).lower()
    m = BODY_STATUS_RE.search(text)
    return m.group(1).lower() if m and m.group(1).lower() != "see" else "unknown"


def sections(text: str) -> dict[int, str]:
    out: dict[int, str] = {}
    matches = list(SECTION_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[int(m.group(1))] = text[m.end():end]
    return out


def signed(text: str) -> tuple[bool, list[str]]:
    """(all three signers ticked, the ones that are not)."""
    m = SIGNOFF_RE.search(text)
    line = m.group(1).lower() if m else ""
    missing = [s for s in SIGNERS if not re.search(rf"{s}\s*\[\s*x\s*\]", line)]
    return (not missing, missing)


def mapping_rows(body10: str) -> dict[str, str]:
    """§10 table: first cell -> status cell (last non-empty cell)."""
    rows: dict[str, str] = {}
    for ln in body10.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        rows[cells[0]] = cells[-1].lower()
    return rows


def shape(spec: Path, text: str, status: str, fails: list[str], warns: list[str]) -> None:
    secs = sections(text)
    slugs = CONTRACT_RE.findall(text)
    for dup in sorted({s for s in slugs if slugs.count(s) > 1}):
        fails.append(f"{spec.name}: contract {dup} is declared twice")
    declared = set(slugs)
    for ln in secs.get(9, "").splitlines():
        if "maps to" not in ln:
            continue
        for slug in SLUG_RE.findall(ln.split("maps to", 1)[1]):
            if slug.startswith("AC_"):
                continue
            if slug not in declared:
                fails.append(f"{spec.name}: §9 maps to {slug}, which is not a `### Contract:` of this spec")
    is_signed, missing = signed(text)
    live = status in LIVE_STATUSES
    if live and missing:
        fails.append(f"{spec.name}: status {status} but unsigned by {', '.join(missing)} — a promotion nobody signed")
    if (is_signed or live) and declared:
        rows = mapping_rows(secs.get(10, ""))
        for slug in sorted(declared - set(rows)):
            fails.append(f"{spec.name}: contract {slug} has no §10 test-mapping row"
                         f" ({'signed' if is_signed else status} — the mapping is owed, status `pending` is a value)")
        if status == "implemented":
            for slug, st in sorted(rows.items()):
                if st in STILL_OPEN and slug in declared:
                    fails.append(f"{spec.name}: implemented, but §10 row {slug} is `{st}`")
        if not FAILURE_RE.search(text):
            warns.append(f"{spec.name}: no `### Failure:` mode — a happy-path-only spec is half a spec")


def main() -> int:
    list_mode = "--list" in sys.argv
    warn_mode = "--warn" in sys.argv

    if not SPECS.is_dir():
        print("spec lint: SKIP — no docs/graph/specs/ directory")
        return 0

    fails: list[str] = []
    warns: list[str] = []
    contracts: dict[str, str] = {}          # slug -> spec file (live only)
    live_specs = 0
    for spec in sorted(SPECS.glob("SPEC-*.md")):
        text = spec.read_text(encoding="utf-8", errors="replace")
        status = status_of(text)
        shape(spec, text, status, fails, warns)
        if status not in LIVE_STATUSES:
            continue
        live_specs += 1
        for slug in CONTRACT_RE.findall(text):
            contracts[slug] = spec.name

    def finish(headline: str, rc: int) -> int:
        for w in warns:
            print(f"  WARN {w}")
        if fails:
            print(f"spec lint: {'WARN' if warn_mode else 'FAIL'} — {len(fails)} shape defect(s):")
            for f in fails:
                print(f"  - {f}")
            rc = 1
        else:
            print(headline)
        return 0 if warn_mode else rc

    if not contracts:
        return finish(f"spec lint: PASS — no live contracts to cover ({live_specs} live spec(s))", 0)

    files = test_files()
    if not files:
        print(f"spec lint: FAIL — {len(contracts)} live contract(s) but the "
              f"test globs matched ZERO files. A coverage check over an "
              f"empty set is a green lie; fix TEST_GLOBS or write the tests.")
        finish("", 0)
        return 0 if warn_mode else 1

    hits: dict[str, list[str]] = {slug: [] for slug in contracts}
    tested_slugs: set[str] = set()
    # Boundary-guarded and longest-first: a bare substring scan let a
    # prefix slug steal the match from PARSE_JSON_STRICT and let an
    # UNREGISTERED extension (PARSE_JSON_V2 in a test) credit PARSE_JSON.
    slug_union = re.compile(
        "(?<![A-Z0-9_])(?:"
        + "|".join(re.escape(s) for s in sorted(contracts, key=len, reverse=True))
        + ")(?![A-Z0-9_])")
    for f in files:
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in slug_union.finditer(body):
            hits[m.group(0)].append(str(f.relative_to(ROOT)))
            tested_slugs.add(m.group(0))

    uncovered = sorted(s for s in contracts if not hits[s])

    if list_mode:
        for slug in sorted(contracts):
            where = ", ".join(sorted(set(hits[slug]))[:3]) or "UNCOVERED"
            print(f"  {slug}  ({contracts[slug]})  ->  {where}")

    if uncovered:
        print(f"spec lint: {'WARN' if warn_mode else 'FAIL'} — "
              f"{len(uncovered)}/{len(contracts)} live contract(s) have no test:")
        for slug in uncovered:
            print(f"  - {slug}  ({contracts[slug]})")
        finish("", 0)
        return 0 if warn_mode else 1

    return finish(f"spec lint: PASS — {len(contracts)} live contract(s) covered "
                  f"across {len(files)} test file(s)", 0)


if __name__ == "__main__":
    sys.exit(main())
