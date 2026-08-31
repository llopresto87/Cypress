# Legal corpus

**Project-agnostic, citation-durable** entries for external law, regulation, and
standards — the statute mirror of `library-corpus/`. Folded back into the seed
by the **harvest** protocol (`protocols/harvest.md`, `HARVEST_PROMPT.md`), and
withdrawn by `grow` (and refreshed onto an already-grown project by `graft`)
when a project must reason about the same body of law.

## Purpose

Verifying a legal citation is expensive, and most of that cost is paid
rediscovering the same **primary text** every time: finding the official
publisher, getting past whatever blocks a non-browser client, reading the
provision, and correctly dating the edition you actually read. That text is
durable far longer than any one project's application of it — a statute outlives
several codebases. Harvest folds the durable **citation** into this corpus —
instrument, provision, its text (graded by how it was sourced), the official
source URL, the verification grade and date, the legal status — so the next
project that must comply with or reason about the same law starts from a sourced
orientation instead of a blank page, then confirms currency before relying on it.

`library-corpus/` is to a code dependency what this corpus is to a statute or a
standard, and the same caveat governs both: **a corpus entry is orientation to
confirm, not gospel to copy.** Law is amended.

## What belongs here (citation, durable)

- The **citable entry itself**: instrument identity in full official form, the
  provision cited, its text graded by `text_form`, the official publisher URL,
  the `verification_grade` and date, and the `legal_status` on that date.
- The **blockage** that stopped a primary fetch (HTTP 403, JS-gated page,
  paywall). That is a durable retrieval fact; the next pass should not
  rediscover it.
- A **verified absence** — a searched-for instrument or decision found not to
  exist. It stops the next reader assuming one does.

The corpus is keyed by **jurisdiction + instrument** exactly the way
`library-corpus/` is keyed by ecosystem + library. A .NET project does not need
the npm corpus; a project with no EU exposure does not need the EU corpus. But
inside its own scope, a citation is as reusable as a library's API surface —
the law says the same thing to every project subject to it.

## What stays OUT (application, project-bound)

This is the agnosticism boundary, and it is the sharp one — because legal
analysis *feels* portable and is not:

- **Any application of the law to a system.** "How this project's architecture
  does or does not trigger this provision" is not a fact about the provision.
- **Any project's own finding**, risk posture, gap, or remediation status.
- **Any source-file, path, component, endpoint, or vendor reference** used to
  ground such a finding.
- **Any determination** — whether a project is in scope, compliant, or exposed.

All of that is the *plant's* own `docs/graph/legal/` (or equivalent), generated
fresh per project **against** this corpus as its orientation layer, and never
copied back. The corpus states what the law says; the plant states what that
means for one system.

## Layout

```
legal-corpus/<scope>/<instrument-slug>.md
```

- Keyed by **instrument, not by the project reading it** — one page per
  instrument (or per tightly-coupled instrument family).
- `<scope>` — one of:
  - `eu` — Union-level instruments (regulations, directives, implementing
    decisions, supervisory-body guidance).
  - `national` — national-level statutes and decrees, **prefixed by country
    code** in the filename (`it-codice-privacy.md`, `de-…`, `fr-…`).
  - `international` — global standards bodies and treaty-level instruments.
  - `case-law` — judicial and regulator decisions. These routinely span
    jurisdictions (a Union court ruling on a national referral), so they get
    their own scope rather than forcing a jurisdiction pick.
- `<instrument-slug>` — the common short id, lowercased and kebab-cased
  (`gdpr.md`, `nis2.md`, `scc-2021-914.md`, `iso-27001.md`).

Entry shape is fixed by `_schema.md`; `index.md` is the router.

## Rules

- **Agnostic or it does not belong here.** No project name, domain noun, path,
  component, finding, or posture. If a sentence could not have been written
  before any project existed, it is application, not citation.
- **Durable or it does not belong here — and for law, durable means
  *edition-stated*.** Every entry must say whether its text is the **ORIGINAL**
  or the **CONSOLIDATED / as-amended** text, with the consolidation date. This
  is **the amendment trap**, and it is the single most dangerous failure this
  corpus exists to prevent: an unamended reading of an amended instrument reads
  exactly like a correct one and is wrong in the direction of under-compliance.
  A bare document identifier is insufficient provenance for anything amendable.
  Relatedly: **never upgrade a citation's verification grade without a new
  fetch.** Downgrading on new evidence is fine; upgrading without re-reading the
  source is falsification.
- **Orientation, not gospel.** A citation ages more slowly than a library API,
  but law amends, transposes, gets annulled, and comes under appeal. Confirm
  `verified` + `legal_status` before relying on an entry for anything
  consequential — and re-confirm for each reuse, because a citation that shipped
  once is not thereby still true.
- **Grade per entry, never per page.** A page may hold a primary-fetched
  verbatim article next to a secondary-corroborated summary. A page-level
  "verified" banner over mixed provenance is falsification that is hard to
  notice. See `_schema.md` rule 4.
- **Never delete a superseded entry.** Mark its status and link forward.

## The natural consumer

`agent-corpus/legal.md` is the specialist a project
would pair with a corpus like this one. Its whole discipline depends on exactly
this kind of rigorously-graded external corpus existing to read from: it reasons
about externally-authored rules using the corpus as its **only** knowledge
source, a corpus gap produces an explicit refusal rather than a reconstructed
citation, and each of its findings keeps the verified fact, the cited rule, its
own labelled assessment, and the human-authority boundary distinct. That
refusal-on-gap behaviour is only safe when the corpus is honest about what it
did and did not actually read — which is what `_schema.md` enforces.

## The withdraw contract (consumed by `grow` / `graft`)

When a project is subject to a body of externally-authored rules, check this
corpus **first**:

- **`grow`** (Phase 4, the `legal/` collection) seeds the project's
  `docs/graph/legal/<instrument>.md` from the matching corpus page as the
  **orientation layer** — the citation, its provenance, and its grading — and
  then the project authors its **own** application of the rule beside it.
- **`graft`** (Phases 2, 4 and 5) refreshes an already-grown project's legal
  leaves the same way, for instruments it is genuinely subject to.
- **Currency is never withdrawn, only the citation.** Before anything here is
  relied on for a consequential determination, re-confirm the entry's
  `verified` date and `legal_status` against the publisher. A corpus entry that
  cannot be re-confirmed is orientation only, and must be described as such.
- **Nothing flows back except a citation.** A project's application of a rule,
  its findings, and its determinations stay in the project — `harvest` mines a
  plant's legal leaves for the citation alone.

If no page matches, ingest from the publisher as usual; the durable citation
from that work becomes a harvest candidate for the next cycle.
