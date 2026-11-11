# EDPB Guidelines 03/2026 on web scraping in the context of generative AI (EU)

> Project-agnostic legal citation notes, kept in the seed's legal corpus
> (`legal-corpus/README.md`). Entry contract: `../_schema.md`.

**Instrument kind:** `guidance`. A supervisory body's interpretive reading,
**not binding law**, and in this case **not final either**: the document read
is Version 1.0, which its own version history describes as "adoption of the
guidelines for public consultation". Cite it as a consultation draft of
guidance, never as the rule itself and never as the EDPB's settled position.

**Scope, by the document's own paragraphs 1–6:** web scraping by **private
entities** of data from sources external to the organisation, **for training or
fine-tuning generative AI**. Paragraph 5 states that the Guidelines do not
address processing of an organisation's own personal data. A use outside that
scope is at most an analogy, and a deliverable that draws one must say so.

**UNREVIEWED: this page was admitted into the corpus without a human review
(owner decision of 2026-11-11).** Its text was re-fetched from the publisher
and compared mechanically with this page on that date; no person has read it.

## Standing fields: the inheritable half of the entry contract

One instrument, one document, one fetch. These fields hold for every entry
below unless the entry states its own value:

- **instrument:** European Data Protection Board, *Guidelines 03/2026 on web
  scraping in the context of generative AI*, Version 1.0, "Adopted on 07 July
  2026". *guidance*
- **official_url:** PDF:
  https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_2020603_webscraping_v1_en_0.pdf
  · landing page: `not recorded`
- **consulted:** a direct `curl` fetch of that PDF on 2026-11-11 (HTTP 200),
  text extracted with macOS PDFKit (not OCR) and read from the
  extracted text; each paragraph below was checked against that text
  (whitespace- and quote-normalised) on the same day. **verification_grade:**
  `primary-fetched`. No proxy, no blockage. **Not reviewed by a human.**
- **language_version:** English, the **original** text of **Version 1.0**. The
  version history in the document: "Version 1.0 07 July 2026 adoption of the
  guidelines for public consultation". No later version is recorded here.
- **verified:** 2026-11-11
- **legal_status:** `in force` (as guidance) **in its consultation-draft form
  only**: Version 1.0 adopted for public consultation; whether a final version
  has been adopted is `not recorded`. The consultation end date (30 October
  2026) comes from secondary commentary only (`secondary-corroborated`); the PDF
  itself states no end date.

Transcription rule for every entry: paragraph text is reproduced as printed,
including the source's own spelling and quotation marks. A footnote reference
numeral is shown as `[fn N]`; the footnote text is not transcribed. Footnotes
the text cites and that this corpus does not hold: EDPB Opinion 28/2024,
EDPB Guidelines 1/2024 on Art. 6(1)(f), WP29 WP260 rev.01 (all `not recorded`).

---

### `edpb-gl-03-2026-para-25`

- **provision:** paragraph 25: individual information may not be required where
  Art. 14(5)(b) applies
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 25 Depending on how the data processing is precisely designed, it is possible that the controller of the web scraping might not have to inform data subjects individually about the web scraping, if providing the information proves impossible or requires disproportionate effort (Article 14 (5)(b) GDPR).

### `edpb-gl-03-2026-para-26`

- **provision:** paragraph 26: where impossibility or disproportionate effort
  typically arises
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 26 Impossibility or disproportionate effort typically arises in circumstances where the personal data were not obtained from the data subject.[fn 7]

### `edpb-gl-03-2026-para-27`

- **provision:** paragraph 27: the Art. 14(5)(b) exception outside archiving,
  research and statistics
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 27 Informing the data subjects individually may be impossible or require disproportionate effort in particular for processing “for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes”, subject to the safeguards referred to in Article 89(1) GDPR.[fn 8] While the word “in particular” clarifies that there may be other cases where it would be impossible or require disproportionate effort to inform data subjects,[fn 9] this exception should not be routinely relied upon by controllers who are not processing personal data for the purposes of archiving in the public interest, for scientific or historical research purposes or statistical purposes.[fn 10]

### `edpb-gl-03-2026-para-28`

- **provision:** paragraph 28: the balancing exercise for Art. 14(5)(b)
- **text_form:** **verbatim** (the three items are a bulleted list in the PDF)
- **text (EN, verbatim):**

  > 28 Where a controller seeks to rely on the exception in Article 14(5)(b) GDPR, it should assess the effort involved for the controller to provide the information to the data subject against the impact and effects on the data subject if they were not provided with the information.[fn 11] The balancing exercise should be carried out with regard to the dataset as a whole and not on every single piece of personal data, and should take into account:
  > • the number of data subjects,
  > • the age of the data,
  > • any appropriate safeguards adopted.[fn 12]

### `edpb-gl-03-2026-para-30`

- **provision:** paragraph 30, first two sentences: publishing the information
  as the measure always required under Art. 14(5)(b)
- **text_form:** **verbatim** (an excerpt: the first two sentences; the rest of
  the paragraph, on what a public notice should contain, is not transcribed)
- **text (EN, verbatim):**

  > 30 In cases where informing data subjects individually proves impossible or would require disproportionate effort, the controller must take appropriate measures to protect the data subject’s rights, freedoms and legitimate interests. One appropriate measure that controllers must always take, as specified in Article 14(5)(b), is to make the information publicly available.[fn 14]

### `edpb-gl-03-2026-para-45`

- **provision:** paragraph 45, first two sentences: publicly available data and
  consent
- **text_form:** **verbatim** (an excerpt: the first two sentences; the
  paragraph continues on robots.txt and is not transcribed)
- **text (EN, verbatim):**

  > 45 Sometimes data subjects are not even aware of the fact that their data are publicly available online. When data subjects make their personal data available online, for example on a web page accessible to everyone, this does not mean that the data subjects gave their consent to the scraping of their personal data for a specific purpose.

- **notes (page-wide, what a consumer must not over-claim):** every entry on
  this page is a consultation draft of non-binding guidance, scoped to scraping
  for generative AI. The provision it reads is `gdpr-art-14-5`
  (`gdpr.md`).

## Neighbours

- `../_schema.md`: the entry contract.
- `gdpr.md`: `gdpr-art-14-5`, the provision paragraphs 25–30 read.
- `edpb-guidelines-02-2023.md`: the same page shape, for a final (Version 2.0)
  EDPB guideline.
