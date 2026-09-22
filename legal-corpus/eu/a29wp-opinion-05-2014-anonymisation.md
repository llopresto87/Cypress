# A29WP Opinion 05/2014 on Anonymisation Techniques (WP216) — EU

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Entry contract: `../_schema.md`.

**Read the status field before you cite this.** This opinion is **not binding
law**, it was adopted under a Directive that has since been repealed, and its
standing under the Regulation that replaced it is an **open question this page
does not settle**. The evidence for that sits in the standing `legal_status`
below, with its sources, so the next reader can weigh it rather than re-run it.

## Standing fields — the inheritable half of the entry contract

One instrument, one document, one fetch. The inheritable fields
(`../_schema.md`, "The citability contract") are therefore stated once, here,
instead of under each entry:

- **instrument:** Article 29 Data Protection Working Party, *Opinion 05/2014 on
  Anonymisation Techniques*, reference `0829/14/EN`, `WP216`, adopted on
  **10 April 2014** — **kind:** `guidance`: the opinion of the independent
  advisory body set up under Article 29 of Directive 95/46/EC, **not binding
  law**. That body was the predecessor of the European Data Protection Board.
- **provision:** never inherited. Each entry names its own numbered section and
  the PDF page range it was transcribed from, because this document is long and
  is cited by section.
- **official_url:**
  https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf
- **consulted:** a direct `curl` of that URL on 2026-09-22 — HTTP 200,
  `application/pdf`, 738,776 bytes, 37 pages — written to a file, text-extracted
  and read from the file rather than summarized in flight —
  **verification_grade:** `primary-fetched`. **No proxy and no mirror were
  needed:** the Commission's document host answered a plain non-browser request.
  The predecessor body's archive has been reorganised more than once since
  publication, so treat this URL as one to **re-probe** on each pass rather than
  inherit; on the recorded date it resolved.
- **language_version:** English. The opinion **as adopted** on 10 April 2014, and
  the only edition there is. The document served carries no revision or version
  marker anywhere in its 37 pages — `rev.`, `revision` and `version` return no
  match in the extracted text — unlike the WP29 documents the successor body
  later endorsed, which carry explicit `rev.01` markers. An opinion of this body
  is adopted once and is not consolidated.
- **verified:** 2026-09-22
- **legal_status:** `unverified — open question`. The question was researched in
  this pass against primary documents and **came back unresolved, with evidence
  pointing both ways**:
  - Directive 95/46/EC, under which this opinion was adopted, was **repealed with
    effect from 25 May 2018** by Art. 94(1) of Regulation (EU) 2016/679, and
    Art. 94(2) provides that references to the adopting Working Party "shall be
    construed as references to the European Data Protection Board" (read in the
    same pass from the Regulation's own text — see `gdpr.md`).
  - The EDPB's **Endorsement 1/2018** (Brussels, 25 May 2018), retrieved and read
    in full in this pass, names **sixteen** Working Party documents it endorses,
    and **this opinion is not among them**. That is a verified absence from the
    endorsement list, **not** an express withdrawal: the endorsement says nothing
    about the documents it omits. Read at
    https://www.edpb.europa.eu/system/files_en?file=2026-04%2Fendorsement_of_wp29_documents_en_0.pdf
  - Against that, the EDPB's own **Guidelines 4/2019 on Article 25, Version 2.0,
    adopted 20 October 2020** cite this opinion twice, at footnotes 18 and 19 on
    PDF p. 13, at the same publisher URL recorded above. Read at
    https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_201904_dataprotection_by_design_and_by_default_v2.0_en.pdf
  - **So: neither carried forward nor repudiated.** Cite it for what it
    demonstrably is — the pre-Regulation reading of the predecessor body, which
    the successor body still references — and never as endorsed guidance under
    the present Regulation. Do not assert currency in either direction.

Where an entry states any of these fields inline, **the entry's own value wins.**

---

## Section locator — where each proposition sits in the PDF

| You want… | It is at… |
|---|---|
| the **identifiability test** and the three criteria an effective anonymisation must defeat | **§2.2.2, "Potential Identifiability of Anonymised Data"**, PDF pp. 8–10 |
| **why pseudonymisation is not anonymisation**, and the techniques it covers | **§4 and §4.1–4.3**, PDF pp. 20–23 |
| the **per-technique residual-risk table** and the case-by-case conclusion | **§5.1–5.2**, PDF pp. 23–24 |

Every passage below was checked back against the fetched PDF's extracted text,
character for character with whitespace collapsed. **One typographic
normalisation was applied and it is the only difference:** the source's curly
quotation marks are rendered straight, and a quotation nested inside a quotation
is rendered with single marks where the source used double. The wording is
untouched, and the source's own grammatical slips are reproduced, not corrected.
A passage that spans a PDF page break is noted as a page range and carries no
marker in the text.

---

### `a29wp-wp216-identifiability` — the test and the three criteria (§2.2.2)

- **provision:** §2.2.2, "Potential Identifiability of Anonymised Data",
  PDF pp. 8–10
- **text_form:** **verbatim** (selected passages)
- **text (EN, verbatim — the three criteria, p. 9):** "An effective
  anonymisation solution prevents all parties from singling out an individual in
  a dataset, from linking two records within a dataset (or between two separate
  datasets) and from inferring any information in such dataset. Generally
  speaking, therefore, removing directly identifying elements in itself is not
  enough to ensure that identification of the data subject is no longer possible.
  It will often be necessary to take additional measures to prevent
  identification, once again depending on the context and purposes of the
  processing for which the anonymised data are intended."
- **text (EN, verbatim — what "identification" reaches, p. 10):** "It must be
  clear that 'identification' not only means the possibility of retrieving a
  person's name and/or address, but also includes potential identifiability by
  singling out, linkability and inference. Furthermore, for data protection law
  to apply, it does not matter what the intentions are of the data controller or
  recipient. As long as the data are identifiable, data protection rules apply."
- **text (EN, verbatim — the reach of the reasonableness test, p. 9):**
  "Secondly, 'the means likely reasonably to be used to determine whether a
  person is identifiable' are those to be used 'by the controller or by any other
  person'. Thus, it is critical to understand that when a data controller does
  not delete the original (identifiable) data at event-level, and the data
  controller hands over part of this dataset (for example after removal or
  masking of identifiable data), the resulting dataset is still personal data.
  Only if the data controller would aggregate the data to a level where the
  individual events are no longer identifiable, the resulting dataset can be
  qualified as anonymous."
- **notes:** the three criteria — **singling out, linkability, inference** — are
  what the rest of the document measures every technique against, and they are
  the part of this opinion most often cited. The passage on retained source data
  is the opinion's own gloss on the "all the means likely reasonably to be used"
  wording of Recital 26 of Directive 95/46/EC. **The counterpart recital under
  the present Regulation is not the same text**, and the difference runs toward
  this opinion rather than away from it: the Regulation's Recital 26 adds that
  data which have undergone pseudonymisation and could be attributed to a person
  by the use of additional information "should be considered to be information on
  an identifiable natural person", and it names "singling out" inside the
  reasonableness test itself. Both recitals were read in the pass that wrote this
  entry and **neither is recorded in this corpus**, so neither is citable from
  here. Whether a given dataset satisfies the three criteria is a question of
  fact for the controller, and nothing here decides it.

### `a29wp-wp216-pseudonymisation` — pseudonymisation is not anonymisation (§4)

- **provision:** §4, "Pseudonymisation", with §4.1 "Guarantees", §4.2 "Common
  mistakes" and §4.3 "Shortcomings of Pseudonymisation", PDF pp. 20–23
- **text_form:** **verbatim** (selected passages)
- **text (EN, verbatim — the operative statement, p. 20):** "Pseudonymisation
  consists of replacing one attribute (typically a unique attribute) in a record
  by another. The natural person is therefore still likely to be identified
  indirectly; accordingly, pseudonymisation when used alone will not result in an
  anonymous dataset. […] Pseudonymisation reduces the linkability of a dataset
  with the original identity of a data subject; as such, it is a useful security
  measure but not a method of anonymisation."
- **text (EN, verbatim — the replay shortcoming of a hash, p. 20):** "Hash
  function: this corresponds to a function which returns a fixed size output from
  an input of any size (the input may be a single attribute or a set of
  attributes) and cannot be reversed; this means that the reversal risk seen with
  encryption no longer exists. However, if the range of input values the hash
  function are known they can be replayed through the hash function in order to
  derive the correct value for a particular record. […] Hash functions are
  usually designed to be relatively fast to compute, and are subject to brute
  force attacks. Pre-computed tables can also be created to allow for the bulk
  reversal of a large set of hash values." And on salting: "The use of a
  salted-hash function (where a random value, known as the 'salt', is added to
  the attribute being hashed) can reduce the likelihood of deriving the input
  value but nevertheless, calculating the original attribute value hidden behind
  the result of a salted hash function may still be feasible with reasonable
  means."
- **text (EN, verbatim — §4.2, the mistake the section exists for, p. 21):**
  "Believing that a pseudonymised dataset is anonymised: Data controllers often
  assume that removing or replacing one or more attributes is enough to make the
  dataset anonymous. Many examples have shown that this is not the case; simply
  altering the ID does not prevent someone from identifying a data subject if
  quasi-identifiers remain in the dataset, or if the values of other attributes
  are still capable of identifying an individual."
- **notes:** the quoted ellipses mark where the section's enumeration of other
  techniques (secret-key encryption, keyed hash with stored key, deterministic
  encryption or keyed hash with the key deleted, tokenization) was left out; each
  is described in the same pages and is `not recorded` here. **Read the
  standing `legal_status` before relying on any of this.** The present Regulation
  defines pseudonymisation in its own Art. 4(5) and that definition is **not
  recorded in this corpus**; this opinion predates it and is not a substitute for
  it. Applying the "still feasible with reasonable means" observation to a
  concrete scheme is a question of fact for the controller, not something this
  entry decides.

### `a29wp-wp216-conclusions` — no technique is certain, and the risk table (§5)

- **provision:** §5.1 "Conclusions" and §5.2 "Recommendations", including
  Table 6, PDF pp. 23–24
- **text_form:** **verbatim** (selected passages, and the table reproduced as
  published)
- **text (EN, verbatim — §5.2, the finding the table summarises):** "Each
  technique described in this paper fails to meet with certainty the criteria of
  effective anonymisation (i.e. no singling out of an individual; no linkability
  between records relating to an individual; and no inference concerning an
  individual). However as some of these risks may be met in whole or in part by a
  given technique, careful engineering is necessary in devising the application
  of an individual technique to the specific situation and in applying a
  combination of those techniques as a way to enhance the robustness of the
  outcome."
- **text (EN, verbatim — §5.1, on residual risk):** "In many cases, an anonymised
  dataset can still present residual risk to data subjects. Indeed, even when it
  is no longer possible to precisely retrieve the record of an individual, it may
  remain possible to glean information about that individual with the help of
  other sources of information that are available (publicly or not)."
- **text (EN, Table 6 as published, "Strengths and Weaknesses of the Techniques
  Considered"):**

  | Technique | Is singling out still a risk? | Is linkability still a risk? | Is inference still a risk? |
  |---|---|---|---|
  | Pseudonymisation | Yes | Yes | Yes |
  | Noise addition | Yes | May not | May not |
  | Substitution | Yes | Yes | May not |
  | Aggregation or K-anonymity | No | Yes | Yes |
  | L-diversity | No | Yes | May not |
  | Differential privacy | May not | May not | May not |
  | Hashing/Tokenization | Yes | Yes | May not |

- **notes:** the table's cells are the opinion's own verdicts and are reproduced
  as published; the row and column wording is the source's. Read them against
  §5.2's own framing — **no row is a clearance**, and the opinion's standing
  recommendation is that "the optimal solution should be decided on a
  case-by-case basis". The three column headings are the same three criteria as
  `a29wp-wp216-identifiability`. **This table states no thresholds, percentages
  or parameters**, and the opinion says so in terms: "In most cases it is not
  possible to give minimum recommendations for parameters to use as each dataset
  needs to be considered on a case-by-case basis." An entry that reused a
  parameter from the technical annex would be carrying a number out of this
  document, and `../_schema.md` rule 5 governs that.

---

## Not transcribed

- **§1, §2.1, §2.2.1, §2.2.3 and §3 in full** — the introduction, the definitions
  against the repealed Directive, the lawfulness of anonymisation as a further
  processing, the risks of using anonymised data, and the technique-by-technique
  analysis of randomization and generalization. Present in the same PDF,
  `not recorded` here.
- **The technical annex, pp. 25–37.** It holds the worked parameters and the
  re-identification examples. `not recorded` deliberately: a number lifted out of
  a worked example reads exactly like a recommended parameter, and the opinion's
  own conclusion is that it is not giving any.
- **Reuse and copyright terms for the document** — `not recorded`. The passages
  quoted above are short excerpts cited for identification; the publisher's own
  reuse notice was not located in this pass.

## Neighbours

- `../_schema.md` — the entry contract, what each grade means, and the amendment
  trap.
- `edpb-guidelines-07-2020.md` — the other supervisory-guidance page in this
  corpus, and guidance of the **successor** body, so the status caveat above does
  not apply to it.
- `gdpr.md` — Art. 94, which repealed the Directive this opinion was adopted
  under and redirected references to the adopting body; and `gdpr-art-5-1-c`,
  `gdpr-art-25-1`, `gdpr-art-25-2` and `gdpr-art-32-1-b`, the provisions a
  de-identification question most often lands on.
