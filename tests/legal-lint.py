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
  5. THE AMENDMENT TRAP — an entry on an amendable instrument must state the
     EDITION of the text it read. _schema.md has always been categorical here
     ("an entry that does not say is non-citable"), and nothing enforced it, so
     the corpus accumulated entries whose text could be the original or the
     consolidated version with nothing in the record to tell them apart. An
     unamended reading of an amended instrument reads exactly like a correct
     one; that is what makes this the trap it is named for, and why a rule
     stated in prose and unenforced was worth so little. Decisions are exempt
     structurally: a judgment or a regulator's decision is not amended.

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
# Two layouts, because this linter now ships into plants as well as running in
# the seed. In the seed it sits at tests/ and the corpus is legal-corpus/; in a
# plant it sits at docs/graph/ and the corpus is docs/graph/legal/corpus/.
# Resolving from the file's own location and assuming ONE layout is the trap
# spec-lint fell into — it looked for a directory that did not exist, printed
# SKIP, exited 0, and the seed's own specs went unchecked for weeks. So the
# layout is CHOSEN explicitly, `--corpus DIR` overrides it, and a corpus that is
# nowhere is a refusal rather than a skip.
_HERE = Path(__file__).resolve().parent
if (_HERE / "legal" / "corpus").is_dir():
    CORPUS = _HERE / "legal" / "corpus"          # installed into a plant
else:
    CORPUS = ROOT / "legal-corpus"               # running in the seed

# The eight required fields, split by whether a page may supply them for its
# entries. `id` is the entry heading itself.
INHERITABLE = ["instrument", "official_url", "consulted", "language_version",
               "verified", "legal_status"]
ALWAYS_INLINE = ["provision", "text_form", "text"]

# What counts as stating an edition. The field is NAMED `language_version`, so
# ordinary prose about the LANGUAGE trips any loose keyword: "Italian,
# original-language text" and "the Italian version published by the OJ" both say
# nothing about the edition while containing "original" and "version". A marker
# set that accepts those is a gate that passes the exact entries it exists to
# catch, so each pattern below has to be an edition CLAIM, not a word.
#
# An explicit "not recorded" passes on purpose — it is an admission, which is
# the point; what must fail is silence, which is indistinguishable from a
# correct entry.
EDITION_MARKERS = (
    r"consolidat",                      # consolidated / consolidation / consolidato
    r"as amended",
    r"as at\b",
    r"\boriginal(?![\s-]*language)",    # "original OJ text" yes; "original-language" no
    r"as published",
    r"as adopted",
    r"in vigore dal",                   # national consolidation portal header
    r"ult\. agg",
    r"\bversion\s+\d",                  # a guideline's own version number
    r"\bv\d+(\.\d+)*\b",
    r"\d+(?:st|nd|rd|th)\s+edition",
    r"\d{4}[a-z\s]{0,15}edition",      # "2022 edition", "2022 third edition"
    r"\bedition\s+of\b",
    r"\bedition\b[^.\n]{0,20}\d{4}",
    r"not recorded",
)

# Entries that predate this check, frozen on 2026-09-13. The debt is enumerated
# rather than waived so it is countable and cannot grow: a NEW entry may not
# join this list, and an entry that later states its edition is reported as a
# stale row and must be struck from it. The ledger therefore shrinks on its own
# and can never quietly become the normal case.
EDITION_DEBT = {
    "acn-det-127434-baseline-2027", "acn-det-379907-2025",
    "eu-dpf-adequacy-2023-1795",
    "gdpr-art-13", "gdpr-art-14", "gdpr-art-15", "gdpr-art-16",
    "gdpr-art-17-3-b", "gdpr-art-18", "gdpr-art-19", "gdpr-art-20",
    "gdpr-art-21", "gdpr-art-22", "gdpr-art-28-3-b", "gdpr-art-28-3-c",
    "gdpr-art-28-3-d", "gdpr-art-28-3-e", "gdpr-art-28-3-f",
    "gdpr-art-28-3-g", "gdpr-art-34", "gdpr-art-36", "gdpr-art-4-11",
    "gdpr-art-4-7", "gdpr-art-4-8", "gdpr-art-45", "gdpr-art-47",
    "gdpr-art-5-1-a", "gdpr-art-5-1-b", "gdpr-art-5-1-c", "gdpr-art-5-1-d",
    "gdpr-art-5-1-e", "gdpr-art-5-1-f", "gdpr-art-5-2", "gdpr-art-6-1-a",
    "gdpr-art-6-1-b", "gdpr-art-6-1-f", "gdpr-art-7-1", "gdpr-art-77",
    "gdpr-art-82", "gdpr-art-9",
    "iso-27001-2022-amd1-2024", "iso-27001-certification-cycle",
    "iso-gdpr-art-42-relationship",
    "it-dlgs-138-art-38", "it-dlgs-138-mercato-online",
}

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
    The word boundary stops `text` from being satisfied by `**text_form:**` — an
    entry carrying only the grade, not the words, is non-citable.
    """
    return bool(re.search(rf"\*\*{re.escape(field)}\b[^:]*:\*\*", body))


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


def entry_starts(text: str) -> dict:
    """Byte offset of each entry heading, so an entry can be read in page order."""
    return {m.group(1): m.start()
            for m in re.finditer(r"(?m)^### `([^`]+)`", text)}


def edition_value(block: str, last: bool = False):
    """The `language_version` value as stated in BLOCK, or None if it states none.

    The value runs to the next bolded field bullet, so a multi-line edition note
    ("consolidated version recorded as at ...") is read whole rather than
    truncated at the newline. With `last`, return the FINAL such value in BLOCK
    rather than the first — see `inherited_edition`.
    """
    pat = re.compile(r"(?mi)\*\*language_version[:*]\*{0,2}(.*?)"
                     r"(?=\n\s*[-*]\s+\*\*|\n#|\Z)", re.S)
    found = pat.findall(block)
    if not found:
        return None
    return (found[-1] if last else found[0]).lower()


def inherited_edition(text: str, entry_start: int) -> str:
    """The edition an entry inherits: the NEAREST preceding group's, not the page's.

    A multi-instrument page states its fields per provenance GROUP, which is the
    shape `_schema.md` rule 4 requires. Reading the first `language_version` on
    the page therefore hands every entry the FIRST group's edition, so an entry
    under a later group that states none at all inherits a claim about a
    different fetch of a different instrument — a stated edition that was never
    stated about it. Take the last one that precedes the entry, ignoring values
    that belong to other entries rather than to a group.
    """
    prefix = text[:entry_start]
    prefix = re.sub(r"(?ms)^### `[^`]+`.*?(?=^### `|^## |\Z)", "", prefix)
    return edition_value(prefix, last=True) or ""


def states_edition(value: str) -> bool:
    """Does VALUE make an edition claim, as opposed to describing the language?"""
    return any(re.search(pat, value) for pat in EDITION_MARKERS)


def check() -> None:
    if not CORPUS.is_dir():
        return
    pages = 0
    entries = 0
    debt_seen = set()
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
        starts = entry_starts(text)
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
                # The grade value can span lines and can be compound
                # ("per id, not uniform — `normalized summary` for X;
                # `verbatim` for Y"): capture up to the next bullet, and
                # anchor NOTHING at the start — a start-anchored match let
                # any prefix text disable the honesty check entirely.
                seg = body[tf.start():]
                nxt = re.search(r"\n\s*[-*]\s+\*\*", seg)
                val = (seg[:nxt.start()] if nxt else seg).lower()
                if not any(v.split(" —")[0] in val for v in TEXT_FORMS):
                    fail(f"{rel}: `{eid}` text_form is not a schema value: "
                         f"{tf.group(1).strip()[:60]!r}")
                # grade honesty — the falsification the schema forbids.
                # A verbatim GRADE anywhere in the value (leading, or the
                # backticked/bolded token compound "per id" lines use)
                # claims the source's own words somewhere in the entry;
                # the entry must carry them. Plain prose mentions ("one
                # phrase reproduced verbatim is quoted in the notes") are
                # not grades and stay exempt.
                if (re.search(r"`verbatim`|\*\*verbatim\*\*|^\s*\*{0,2}`?verbatim",
                              val) and not quoted(body)):
                    fail(f"{rel}: `{eid}` is graded `verbatim` (in whole or "
                         f"per id) but its text carries no quoted or "
                         f"blockquoted wording — a paraphrase graded as "
                         f"the source's own words")

            ls = re.search(r"\*\*legal_status:\*\*\s*(.*)", body)
            if ls and not any(v in ls.group(1).lower() for v in LEGAL_STATUSES):
                fail(f"{rel}: `{eid}` legal_status is not a schema value: "
                     f"{ls.group(1).strip()[:60]!r}")

            # The amendment trap. A decision is not amended, so `case-law/`
            # is exempt by construction rather than by a list.
            if "case-law" not in rel.parts:
                ev = edition_value(body)
                if ev is None:
                    ev = inherited_edition(text, starts[eid])
                stated = states_edition(ev)
                if eid in EDITION_DEBT:
                    debt_seen.add(eid)
                    if stated:
                        fail(f"{rel}: `{eid}` now states its edition but is "
                             f"still listed in EDITION_DEBT — strike the row; "
                             f"the ledger only shrinks")
                elif not stated:
                    fail(f"{rel}: `{eid}` does not state the EDITION of the "
                         f"text it read (original, or consolidated as at a "
                         f"date) — non-citable under _schema.md's amendment "
                         f"trap. An unamended reading of an amended instrument "
                         f"is indistinguishable from a correct one.")

    # A ledger row for an entry that no longer exists is a row nobody can
    # discharge; it would keep the debt count honest-looking while hiding that
    # the entry it names is gone.
    for gone in sorted(EDITION_DEBT - debt_seen):
        fail(f"EDITION_DEBT lists `{gone}`, which is in no corpus page — "
             f"strike the row")

    if not findings:
        print(f"legal lint: PASS — {entries} entries across {pages} pages "
              f"({len(EDITION_DEBT)} carrying recorded edition debt)")


def main() -> int:
    global CORPUS
    if "--corpus" in sys.argv:
        i = sys.argv.index("--corpus")
        if i + 1 >= len(sys.argv):
            print("legal lint: FAIL — --corpus needs a directory", file=sys.stderr)
            return 1
        CORPUS = Path(sys.argv[i + 1]).resolve()
    if not CORPUS.is_dir():
        print(f"legal lint: FAIL — no corpus at {CORPUS}. A linter that cannot "
              f"find what it lints must say so, not pass.", file=sys.stderr)
        return 1
    check()
    if findings:
        print(f"legal lint: FAIL ({len(findings)} finding(s))")
        for f in findings:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
