# EDPB Guidelines 07/2020 (controller/processor) — EU

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Entry contract: `../_schema.md`.

## Standing fields — the inheritable half of the entry contract

One instrument, one document, one fetch. The inheritable fields
(`../_schema.md`, "The citability contract") are therefore stated once, here,
instead of under each entry:

- **instrument:** European Data Protection Board, *Guidelines 07/2020 on the
  concepts of controller and processor in the GDPR*, Version 2.1 —
  **kind:** `guidance`: a regulator's interpretive reading, **not binding law**,
  but the reading supervisory authorities apply. Every entry below cites this
  one instrument.
- **provision:** never inherited. Each entry names its own Part and §, with the
  PDF page range — this document is cited by section and its two most-cited
  sections are easy to confuse (see the locator below).
- **official_url:**
  https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-072020-concepts-controller-and-processor-gdpr_en
  · PDF:
  https://www.edpb.europa.eu/system/files/documents/2023-10/EDPB_guidelines_202007_controllerprocessor_final_en.pdf
- **consulted:** a direct `curl` fetch of that PDF from `edpb.europa.eu`, 51
  pages, text-extracted — **verification_grade:** `primary-fetched`. **No proxy
  was needed: the EDPB document server is not JS-gated the way EUR-Lex is.**
  Where an entry's passages come from a specific page range, it says so.
- **language_version:** English, "final version", **Version 2.1**. Draft adopted
  **2 September 2020**; final version adopted **7 July 2021**; minor corrections
  **20 September 2022**. **Cite both dates, and do not re-litigate this:** many
  secondary sources say simply "adopted 2020" — that is the **draft** date, and
  a deliverable that repeats it can be accused of resting on a superseded draft.
  The PDF's hosting path carries a `2023-10` timestamp; the fetched document
  declares itself Version 2.1, so that path is a **re-publication artifact, not
  a later substantive version**. No substantive later version was found.
- **verified:** 2026-07-31.
- **legal_status:** `in force` (as guidance).

Where an entry states any of these fields inline, **the entry's own value wins.**

---

## Section locator — where each test actually sits in the PDF

The two most-cited sections of this document are easy to confuse, and citing
the wrong one points a reader at the wrong argument.

| You want… | It is at… |
|---|---|
| **the controller/processor qualification test** — "who determines", purposes and *essential* means | **Part I, §2.1.2 ("Determines") and §2.1.4 ("Purposes and means")**, PDF pp. 11 and 14–17 |
| the **content of the Art. 28(3) processor contract**, sub-paragraph by sub-paragraph | **Part II, §1.3 and §1.4**, PDF pp. 34–42 |

§1.3–1.4 exists and is useful — it is Part II's processor-contract-content
section. It is **not** the qualification test.

---

### `edpb-gl-07-2020` — the qualification test (Part I §2.1.2 / §2.1.4)

- **provision:** **Part I §2.1.2 ("Determines") and §2.1.4 ("Purposes and
  means")**, PDF pages 11 and 14–17
- **text_form:** **verbatim** (selected passages) + `normalized summary` for the
  surrounding argument
- **text (EN, verbatim, §2.1.2 — the operative test):** "One should look at the
  specific processing operations in question and understand who determines them,
  by first considering the following questions: 'why is this processing taking
  place?' and 'who decided that the processing should take place for a
  particular purpose?'" The Guidelines distinguish "control stemming from legal
  provisions" from "control stemming from factual influence", and state (§30):
  "the word 'determines' means that the entity that actually exerts a decisive
  influence on the purposes and means of the processing is the controller."
- **text (EN, verbatim, §2.1.4 — essential vs non-essential means, the test a
  platform-vendor/customer analysis actually needs):** "'Essential means' are
  traditionally and inherently reserved to the controller. While non-essential
  means can also be determined by the processor, essential means are to be
  determined by the controller. 'Essential means' are means that are closely
  linked to the purpose and the scope of the processing, such as the type of
  personal data which are processed ('which data shall be processed?'), the
  duration of the processing ('for how long shall they be processed?'), the
  categories of recipients ('who shall have access to them?') and the categories
  of data subjects ('whose personal data are being processed?')… 'Non-essential
  means' concern more practical aspects of implementation, such as the choice
  for a particular type of hard- or software or the detailed security measures
  which may be left to the processor to decide on."
- **the Guidelines' own worked example, quoted — standardised cloud storage:**
  "A large cloud storage provider offers its customers the ability to store
  large volumes of personal data. The service is completely standardised, with
  customers having little or no ability to customise the service… Company X will
  still be considered a controller, given its decision to make use of this
  particular cloud service provider in order to process personal data for its
  purposes. Insofar as the cloud service provider does not process the personal
  data for its own purposes and stores the data solely on behalf of its
  customers and in accordance with instructions, the service provider will be
  considered as a processor."
- **notes:** this is the section that answers whether a given party is a
  controller or a processor for a given processing operation. The worked example
  above tracks a standardised hosted-software arrangement closely and is
  directly useful, but applying it to a concrete set of facts (self-hosted vs
  vendor-hosted, degree of per-customer customisation, who decides retention and
  recipients) is a qualification the controller must make on its own facts — not
  something this entry decides.

### `edpb-gl-07-2020-part-ii-1-3-1-4` — the Art. 28(3) contract-content section

- **provision:** **Part II §1.3 ("Content of the contract or other legal act")
  and §1.4 ("Instructions infringing data protection law")**, PDF pp. 34–42
- **text_form:** **verbatim** (selected passages)
- **text (EN, verbatim, §1.3.1, on Art. 28(3)(a)):** "The need to specify this
  obligation stems from the fact that the processor processes data on behalf of
  the controller. Controllers must provide its processors with instructions
  related to each processing activity… The processor shall not go beyond what is
  instructed by the controller." And (§117): "When a processor processes data
  outside or beyond the controller's instructions, and this amounts to a
  decision determining the purposes and means of processing, the processor will
  be in breach of its obligations and will even be considered a controller in
  respect of that processing."
- **text (EN, on Art. 28(3)(h), §1.3.8):** the Guidelines describe the
  obligation as the processor's duty to "make available to the controller all
  information necessary to demonstrate compliance with the obligations laid down
  in Article 28 and allow for and contribute to audits, including inspections,
  conducted by the controller or another auditor mandated by the controller."
- **consulted:** the page-wide fetch above; the passages quoted here were taken
  from **PDF pp. 34–36**, the opening of a section that runs to p. 42 —
  **verification_grade:** `primary-fetched`
- **notes — the scope limit this section makes visible on primary text.**
  Art. 28(3)(h), and the EDPB's own gloss on it, are **unambiguously about the
  controller-over-processor relationship in an external vendor arrangement**.
  It is **not** authority for an *internal* audit-trail or access-logging
  obligation inside the controller's own systems. A finding citing 28(3)(h) for
  internal logging is misapplying it; the correct anchors are `gdpr-art-5-1-f`,
  `gdpr-art-24`, `gdpr-art-32-1-b`, and — for the internal-authorization
  question specifically — `gdpr-art-32-4`.

---

**No blanket rule on B2B roles.** There is **no blanket rule** that a B2B
customer is a controller of the data it puts into a supplier's platform. Any
deliverable that qualifies roles must argue it on the specific facts, using the
Part I §2.1 test above, not assume it in either direction.

## Not transcribed

- Part I §3 (joint controllers) and Part II §2 (consequences of joint
  controllership) — present in the same PDF, `not recorded` here; transcribe if
  a joint-controllership question arises.

## Neighbours

- `gdpr.md` — `gdpr-art-4-7`, `gdpr-art-4-8` (the definitions this guidance
  interprets), `gdpr-art-28-1`, `gdpr-art-28-3-a`, `gdpr-art-28-3-h`,
  `gdpr-art-32-4`.
- `../_schema.md`
