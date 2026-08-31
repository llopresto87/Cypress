#!/usr/bin/env python3
"""legal-lint: enforce legal-corpus/_schema.md's citability contract.

The schema is categorical: an entry missing any one of the eight required
fields is NON-CITABLE, "no partial credit and no 'good enough for a draft'".
Nothing enforced that. seed-lint.py scans legal-corpus/ only for leaked
host-IPs, pinned CVEs and dangling cross-references — none of which knows what
a legal entry is. The contract that decides whether the corpus is usable at all
was guarded by an ad-hoc script that lived outside the repo.

That matters more here than in the other corpora because of who reads this one.
The corpus-bound analyst role (agent-corpus/legal.md) has exactly one defining
discipline: NO CORPUS ENTRY -> NO CLAIM. A gap must produce a refusal rather
than a fabrication. That only works if a malformed entry is *detectably*
malformed — an entry missing `verified` still looks like an entry, so the
refusal never fires and a stale citation ships instead.

What this checks:

  1. CITABILITY — all eight fields, inline or resolvably inherited.
  2. GRADE HONESTY — an entry graded `verbatim` must actually carry quoted or
     blockquoted text. Grading a paraphrase as the law's own words is the
     falsification the schema's two "never soften" fields exist to prevent, and
     it has shipped before: 18 entries carried it, inherited from a donor.
  3. CONTROLLED VOCABULARY — text_form / legal_status values must be ones the
     schema defines.
  4. NEVER-INHERITABLE fields are inline: provision, text_form, text.

Inheritance is real and legitimate: a page states the fields its entries share
in a header block (one instrument, one fetch), and a multi-instrument page
states them per provenance group. Flattening distinct provenance into one
page-level banner is what _schema.md rule 4 forbids; inheriting from a stated
block is not. So a field counts as satisfied when the entry states it OR the
page header declares it.

Files are selected by CONTENT, never by name: any file holding at least one
`### \\`id\\`` entry is a content page. An earlier name-based rule ("skip
index.md") silently excluded case-law/index.md — seven entries of the kind the
schema itself calls the highest-risk in a compliance document after a number.

Dependency-free; exit 0 clean, 1 with findings.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "legal-corpus"

# The eight required fields, split by whether a page may supply them for its
# entries. `id` is the entry heading itself.
INHERITABLE = ["instrument", "official_url", "consulted", "language_version",
               "verified", "legal_status"]
ALWAYS_INLINE = ["provision", "text_form", "text"]

TEXT_FORMS = ["verbatim", "normalized summary",
              "wording withheld — requires licensed copy", "topic only"]
LEGAL_STATUSES = [
    "in force", "not yet applicable", "partially applicable",
    "transposition pending", "annulled", "superseded", "withdrawn",
    "published — current edition", "not recorded", "pending",
    "unverified — open question", "n/a",
]

findings: list[str] = []


def fail(msg: str) -> None:
    findings.append(msg)


def entry_blocks(text: str):
    """Yield (id, body) per entry. Group headings (### Group A) are not ids."""
    parts = re.split(r"(?m)^### `([^`]+)`", text)
    for i in range(1, len(parts), 2):
        # stop the body at the next ## section so a trailing page section
        # is not attributed to the last entry
        yield parts[i], re.split(r"(?m)^## ", parts[i + 1])[0]


def has_field(body: str, field: str) -> bool:
    """Anywhere in the entry, not only at bullet start.

    Entries legitimately pack two fields onto one bullet
    (`- **verified:** 2026-07-31 · **legal_status:** `in force``), so a
    start-of-bullet anchor reports a false missing field. The bolded
    `**field:**` form is specific enough to match mid-line safely.
    """
    return bool(re.search(rf"\*\*{re.escape(field)}[^:]*:\*\*", body))


def without_notes(body: str) -> str:
    """The entry minus its `notes` blocks.

    Scoping the grade-honesty check matters in both directions, and getting it
    wrong is easy:

    * Scanning the WHOLE entry lets a quotation sitting in `notes` satisfy a
      `verbatim` grade whose own `text` is a paraphrase — the falsification
      this linter exists to catch.
    * Scanning ONLY a `**text:**` bullet is too narrow: entries legitimately
      carry the source's words in purpose-named bullets
      (`**decree text, verbatim:**`, `**the … test, EN verbatim:**`), and a
      naive `**text...**` match also swallows `**text_form:**`, whose value is
      a grade rather than the wording.

    Excluding `notes` and counting quotation anywhere else satisfies both.
    """
    out, keep = [], True
    for line in body.splitlines():
        m = re.match(r"\s*[-*]\s*\*\*([^:*]+)", line)
        if m:
            keep = not m.group(1).strip().lower().startswith("notes")
        if keep:
            out.append(line)
    return "\n".join(out)


def quoted(body: str) -> bool:
    """Does the entry actually carry the source's words, outside its notes?"""
    seg = without_notes(body)
    return any(c in seg for c in ('"', "“", "«")) or \
        bool(re.search(r"(?m)^\s*>", seg))


def check() -> None:
    if not CORPUS.is_dir():
        return
    pages = 0
    entries = 0
    # The contract itself is not a content page: _schema.md's `### `text_form``
    # and `### `instrument-provision-id`` are vocabulary sections and the entry
    # template. This excludes ONE exact path, not a filename pattern — the
    # name-based rule that skipped every `index.md` is exactly the bug that hid
    # case-law/index.md's seven entries.
    schema_page = CORPUS / "_schema.md"
    for path in sorted(CORPUS.rglob("*.md")):
        if path == schema_page:
            continue
        text = path.read_text(encoding="utf-8")
        blocks = list(entry_blocks(text))
        if not blocks:
            continue  # selection by content, never by filename
        pages += 1
        rel = path.relative_to(ROOT)
        header = text.split("### `")[0]
        supplied = {f for f in INHERITABLE
                    if re.search(rf"(?mi)\*\*{re.escape(f)}[:*]", header)}
        by_prefix = "id prefix" in header

        for eid, body in blocks:
            entries += 1
            for field in ALWAYS_INLINE:
                if not has_field(body, field):
                    fail(f"{rel}: `{eid}` has no `{field}` — non-citable "
                         f"({field} is never inherited)")
            for field in INHERITABLE:
                if has_field(body, field) or field in supplied:
                    continue
                if field == "instrument" and by_prefix:
                    continue  # page derives instrument from the id prefix
                fail(f"{rel}: `{eid}` has no `{field}`, and the page header "
                     f"supplies none — non-citable under _schema.md")

            tf = re.search(r"\*\*text_form:\*\*\s*(.*)", body)
            if tf:
                val = tf.group(1).lower()
                if not any(v.split(" —")[0] in val for v in TEXT_FORMS):
                    fail(f"{rel}: `{eid}` text_form is not a schema value: "
                         f"{tf.group(1).strip()[:60]!r}")
                # grade honesty — the falsification the schema forbids
                if re.match(r"\s*\*{0,2}`?verbatim", val) and not quoted(body):
                    fail(f"{rel}: `{eid}` is graded `verbatim` but its text "
                         f"carries no quoted or blockquoted wording — a "
                         f"paraphrase graded as the source's own words")

            ls = re.search(r"\*\*legal_status:\*\*\s*(.*)", body)
            if ls and not any(v in ls.group(1).lower() for v in LEGAL_STATUSES):
                fail(f"{rel}: `{eid}` legal_status is not a schema value: "
                     f"{ls.group(1).strip()[:60]!r}")

    if not findings:
        print(f"legal lint: PASS — {entries} entries across {pages} pages")


def main() -> int:
    check()
    if findings:
        print(f"legal lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
