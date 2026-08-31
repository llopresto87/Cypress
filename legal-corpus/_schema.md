# The legal corpus — entry contract

This file defines the shape of every entry under `legal-corpus/`. It is to
**statute** what `library-corpus/` is to dependencies, and it exists for the
same stated reason: *an agent's memory of legal text drifts exactly like its
memory of a library API.* Editions, application dates, and legal status move; a
remembered article number is a fabrication with a plausible face.

Read this once. After that, copy an existing entry.

## Who writes, who reads

- **`docs-librarian` writes.** This is a fact-bearing surface (kernel
  §3.2/§3.7). Entries are ingested by `research-scout` and finalized here.
- **The consuming analyst reads only** — the role described by
  `agent-corpus/legal.md`, instantiated in a project
  without `WebSearch`, `WebFetch`, or `Bash`. This corpus plus the project's own
  legal leaf is the *only* source of law it can reach. Its core rule is
  **no corpus entry → no claim**.

That asymmetry is deliberate and it is what makes this schema load-bearing. A
missing or malformed entry does not produce a bad citation — it produces a
**refusal**, which is the correct failure. Filling a gap with a plausible guess
is the single failure mode this whole corpus exists to prevent.

## The citability contract

An entry is **citable** only if it carries *all eight* fields below. An entry
missing any one of them is **non-citable** and must be treated by a consumer as
`not recorded — requires ingest`. There is no partial credit and no "good enough
for a draft".

| Field | Meaning |
|---|---|
| `id` | Stable citable identifier, lowercase-kebab, unique corpus-wide. Deliverables cite this id. Never renumber a published id; supersede it. |
| `instrument` | The instrument in full official form (e.g. `Regulation (EU) 2016/679 (GDPR)`), plus its kind (see below). |
| `provision` | The article / clause / control / docket identifier being cited. |
| `text_form` + `text` | The provision's content, and **what kind of content it is** (see `text_form` values). |
| `official_url` | The authoritative publisher's URL (the official journal, the national gazette, the standards body, the court, the authority). Recorded even when it could not be fetched. |
| `consulted` | What was *actually read* to write the entry, and its `verification_grade`. This is separate from `official_url` on purpose. |
| `language_version` | Language **and edition/consolidation** of the text consulted. For any instrument that can be amended, this field must say **original** or **consolidated (as at &lt;date&gt;)** — see "The amendment trap" below. |
| `verified` + `legal_status` | Date of verification, and the provision's legal status on that date. |

Two fields carry the honesty of the whole corpus and must never be softened:
**`text_form`** (is this the law's words, or a summary of them?) and
**`verification_grade`** (was the official source actually fetched?).
"Corroborated via a mirror or secondary source" is **not** "verified against the
primary text", and upgrading one to the other is falsification.

### `text_form` — what the `text` field actually is

| Value | Means | May a deliverable quote it? |
|---|---|---|
| `verbatim` | The official wording, reproduced exactly, in the stated language. | Yes, as a quotation. |
| `normalized summary` | A faithful one-or-two-sentence restatement of the obligation. **Not the law's words.** | **No.** Cite the substance and the id; never present as a quotation. |
| `wording withheld — requires licensed copy` | The provision exists and is identified, but its normative text is copyrighted/paywalled and is deliberately not reproduced. The `text` field states the reason. | **No.** The entry is citable **by identifier and title only**. |
| `topic only` | Only the subject/skeleton of the provision is recorded — weaker than a normalized summary. | **No.** Usable to say a requirement exists, not to say what it says. |

**Quotability is per entry, never per page.** One page routinely holds a
verbatim article beside a withheld standard control beside a `topic only`
docket. Read the entry's own `text_form`; a page-level claim about quotability
is always wrong.

## The amendment trap — a standing, schema-level hazard

The highest-frequency defect in a legal corpus is not a missing entry, it is a
**correctly-cited superseded text**. It reads exactly like a correct entry, and
it fails silently. It takes three recurring shapes:

| Shape | What goes wrong |
|---|---|
| **The rule reversed** | The original provision states one regime and the amended text states its opposite (a notice/opt-out duty amended into prior-consent, for instance). Both texts sit under the same article number. |
| **The provision that did not exist yet** | An amending act *added* the point being cited. Fetch the original and the point is simply absent — which reads as "the definition is not there" rather than "you fetched the wrong edition". |
| **The number from the wrong category** | The right document, a live figure, the wrong band — a small-enterprise threshold read as the medium-enterprise gate, a notification window read as a reporting window. Nothing about the figure looks wrong. |

**The rules that follow, and they are not optional:**

1. **An entry must state whether its text is the ORIGINAL or the CONSOLIDATED
   text**, in `language_version`. An entry that does not say is **non-citable**,
   exactly like a missing field.
2. **A bare document identifier is insufficient provenance for an amendable
   instrument.** The original-act identifier and the consolidated-version
   identifier denote different documents with different rules. Record **both**
   where the distinction exists: the original for history, the consolidated (with
   its as-at date) for what binds today.
3. **Before treating a publication text as current, look for a consolidated
   version.** Fetching only the original silently produces a superseded rule, and
   a superseded rule reads exactly like a correct one.
4. **The same discipline applies to national consolidations.** National gazette
   and consolidation portals usually print an explicit in-force-from header —
   record it.
5. **A threshold, ceiling or headcount is a quotation too.** Confirm which
   *category* a figure defines before reusing it, not merely that the figure
   appears in the document.

### `verification_grade` — how strong the sourcing is

| Value | Means |
|---|---|
| `primary-fetched` | The official publisher's page/document was retrieved directly in the recorded pass. |
| `proxy-sourced` | The official document's text was obtained **through a third-party read-only proxy** because the publisher blocks non-browser clients. The content appeared faithful and complete, and raw snapshots were retained — **but a proxy is not the official source**, and this grade must never be written up as `primary-fetched`. State the proxy, the blockage it worked around, and where the snapshot lives. |
| `mirror-corroborated` | The official page was not retrievable by the available tooling; the text was read from a site that republishes the official text. The official URL is still recorded. |
| `secondary-corroborated` | Only commentary, practitioner notes, vendors, or aggregators were read. Multiple independent, consistent sources raise confidence but do not make it primary. |
| `not-fetched` | Asserted from search-result metadata or a catalogue listing only; nothing was read end-to-end. |

Anything below `primary-fetched` must state, in the entry, **what blocked the
primary fetch** (HTTP 403, JS-rendered page, paywall). That blockage is itself a
durable fact — the next pass should not rediscover it. It is also a fact that
goes stale in the *helpful* direction: a publisher recorded as unreachable may
be reachable on a fresh attempt, so a "blocked" note is re-probed, not inherited.

> **A retrieval lesson worth as much as any entry.** A summarizing fetch tool
> can truncate a large official document before reaching the articles and then
> report a false "not present". For any document beyond a few pages: fetch to a
> file, then read the file. Never trust a summarizing fetch's *negative* result
> about a large document.

### `legal_status` — a real field, not a formality

| Value | Means |
|---|---|
| `in force` | Applicable law today, unchallenged. |
| `in force — under appeal` | Currently valid **and** contested before a court whose ruling could annul it. Cite it as a basis *and* carry the contest. |
| `not yet applicable` | Adopted and in force as an act, but the specific obligation applies from a later date (see `applies_from`). |
| `partially applicable` | The instrument has **staggered application dates** and only some obligations bite today. Per-obligation `applies_from` is mandatory. |
| `transposition pending` | A directive whose national implementing act is not yet adopted, or not yet recorded here. Nothing national is citable from it. |
| `annulled` / `superseded` / `withdrawn` | No longer a valid basis. Kept on disk with a link forward; never deleted. |
| `published — current edition` | For standards: the edition in force. |
| `not recorded — ingest pending` | The corpus has a *slot* but no content. **Not citable.** |
| `pending` | A case not yet decided (an appeal on foot). Cite as pending, never as authority. |
| `n/a` | The entry records a **non-normative fact** — an operational status, a certification mechanism, a process — that has no legal status of its own. **Never valid for a provision:** a provision always has a status, even if that status is `not recorded`. |
| `unverified — open question` | The question was researched and **not resolved**. Do not assert it in either direction. |
| `not recorded — no such <thing> found` | A searched-for instrument or decision was **not found to exist**. A verified absence, and citable as one. |

A schema that cannot express **"valid but contested"** silently launders a
contested basis into a settled one. `in force — under appeal` exists for exactly
that.

## Four instrument kinds — do not force one shape

The corpus holds four structurally different kinds. Each adds fields to the
eight above.

### 1. `regulation` — directly applicable law

Adds nothing for a uniformly-applicable regulation. For an instrument with
**staggered application**, `applies_from` is recorded **per obligation, not per
instrument** — the act being in force does not mean a given obligation bites
yet. An entry for such an instrument that omits its own `applies_from` is
non-citable.

### 2. `directive` — binds Member States, not persons

Adds **transposition linkage**, and it is mandatory:

- `transposed_by` — the national implementing act (or
  `not recorded — ingest pending`).
- `transposition_status` — adopted / pending / partial.
- `divergence` — where the national act is known to differ from the directive,
  or `not assessed`.

**A directive alone is not citable for a national obligation.** What a national
authority enforces is the transposing act. An entry for a directive with
`transposed_by: not recorded` may be cited for Union-level scope and structure
only, and every such citation must carry that limit. Watch the
**same-number/different-subject trap**: a directive's article N and its
transposing act's article N routinely address different subjects.

### 3. `standard` — copyrighted and paywalled

Normative wording **must not** be reproduced. `text_form` is
`wording withheld — requires licensed copy` (or `topic only` for skeleton
facts), and the entry adds:

- `title_source` — where the identifier and published title came from, since
  titles circulate openly even when the requirement text does not.
- `licensed_copy_required_for` — exactly what a reader cannot get here (e.g.
  "the control's requirement, purpose and guidance text").

A standard's control is therefore **citable by identifier and title** while its
text is **explicitly unavailable**. This is a correctness requirement, not a
formatting preference: reproducing normative standards text would be an
infringement, and paraphrasing it *as if quoted* would be a fabrication.

### 4. `case-law` / `regulator-decision`

Adds `court` (or authority), `docket`, `decision_date`, and — the field that
matters most — whether the **primary text was actually fetched** or the citation
rests on secondary corroboration. That distinction lives in
`verification_grade`; for this kind it must also be restated in prose, because a
judgment citation is the highest-risk thing in a compliance document after a
number.

Also permitted, and valuable: an entry recording that a decision **does not
exist**. A verified absence stops the next reader from assuming one.

## Entry template

```markdown
### `instrument-provision-id`

- **instrument:** Full official form — *kind*
- **provision:** Article / clause / control / docket
- **text_form:** verbatim | normalized summary | wording withheld — requires licensed copy | topic only
- **text:** …
- **official_url:** …
- **consulted:** what was actually read — **verification_grade:** …
- **language_version:** …
- **verified:** YYYY-MM-DD
- **legal_status:** …
- **notes:** conflicts, sharp edges, what a consumer must not over-claim.
```

Kind-specific fields (`applies_from`, `transposed_by`,
`licensed_copy_required_for`, `court`/`docket`/`decision_date`) are added as
further bullets in the same block.

## Rules

1. **One home per provision.** A provision has exactly one entry. Other pages —
   and the project's own legal leaf — link to its id; they never restate the
   law. A page that needs a retention duty cites the entry id; it does not
   re-explain the article.
2. **Never fabricate.** No remembered article number, docket, date, threshold,
   or URL. An unknown is written `not recorded`.
3. **Never upgrade a flag.** A scout's `unverified` or "corroborated via mirror"
   survives canonization verbatim. Downgrading is allowed on new evidence;
   upgrading requires a new fetch, recorded.
4. **Never average provenance to the page.** A page may hold entries of very
   different strength — a primary-fetched national decree beside a
   secondary-sourced directive article. Grade **per entry**. A page-level
   "verified" banner over mixed provenance is the same falsification as
   upgrading a flag, and it is harder to notice.
5. **A number is the highest-risk field there is.** Deadlines, hour counts, fine
   ceilings, turnover percentages, thresholds and application dates carry their
   own verification grade in the entry that states them. A deadline resting on
   secondary corroboration must say so **at the point of use**, not only in a
   methods note. Two further habits, both learned the expensive way: a deadline
   expressed as a **formula** (N months from a per-entity trigger) must never be
   recorded as a **calendar date**, because the two give different answers per
   entity; and an `unverified` flag on a number invites confirmation rather than
   re-derivation, so re-derive.
6. **Status before reuse.** A citation that shipped once is not thereby
   verified. Re-read `verified` + `legal_status` every time.
7. **Never delete a superseded entry.** Mark it and link forward.
8. **Contractual documents are not law.** A vendor's contractual terms belong
   with that vendor (one home per fact); this corpus holds the provisions those
   terms are measured against.
9. **State the edition.** Original or consolidated, with the consolidation date
   and both document identifiers where they differ — see "The amendment trap".

## Neighbours

- `index.md` — the router: one row per instrument, kind, coverage.
- `README.md` — what belongs in this corpus and what never does.
- `library-corpus/` — the same doctrine, applied to dependencies.
- `agent-corpus/legal.md` — the role this schema is
  built to make safe.
