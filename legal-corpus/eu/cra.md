# Regulation (EU) 2024/2847 (Cyber Resilience Act) — EU

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Orientation for citing this regulation — verified against primary
> sources where stated per entry; confirm currency before relying on any entry
> for a consequential determination, especially per-obligation application
> dates (this instrument has STAGGERED application — check `applies_from` on
> every entry, never assume the whole act applies uniformly from one date).
> Entry contract: `../_schema.md`.

**Instrument kind:** `regulation` — directly applicable, **with staggered
application dates**. Ingested 2026-07-31.

**Instrument:** Regulation (EU) 2024/2847 of the European Parliament and of the
Council of 23 October 2024 on horizontal cybersecurity requirements for products
with digital elements and amending Regulations (EU) No 168/2013 and
(EU) No 2019/1020 and Directive (EU) 2020/1828 (Cyber Resilience Act).
**Adopted** 23 October 2024 (Strasbourg) · **published** `OJ L, 2024/2847`,
20 November 2024 · **CELEX** 32024R2847.
**official_url:** https://eur-lex.europa.eu/eli/reg/2024/2847/oj (EN) ·
https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024R2847 (IT)

---

## Standing fields — the inheritable half of the entry contract

Every entry below was sourced the same way, on the same day, from the same
instrument, so the inheritable fields (`../_schema.md`, "The citability
contract") are stated once here rather than restated under each entry:

- **instrument:** Regulation (EU) 2024/2847 (Cyber Resilience Act) —
  *regulation*. **Page-wide:** every entry below cites this one instrument
  unless it says otherwise, and exactly one does
  (`cra-enisa-srp-readiness`, which is not a legal-text entry at all).
- **provision:** never inherited — each entry states its own article, annex or
  recital.
- **official_url:** the ELI / CELEX links in the header above (EN and IT).
- **consulted:** the Official Journal **HTML and PDF renders** of those EUR-Lex
  URLs, routed through the **`r.jina.ai` read-only proxy** —
  **verification_grade:** `proxy-sourced`. **A third-party proxy is not the
  official source, however faithful it appeared:** do not write any entry on
  this page up as verified against EUR-Lex.
- **language_version:** English, OJ text, **original as published** — no
  consolidated version recorded as at 2026-07-31. The **Italian** text was
  confirmed reachable at the `/IT/` path and its title is consistent with the
  English, but it was **not deep-parsed**; an Italian-language ingest is future
  work if Italian-jurisdiction citations are needed.
- **verified:** 2026-07-31.
- **legal_status:** **`partially applicable`** — the schema's value for a
  staggered instrument, and the honest one here. The act is **in force**
  (10 December 2024, `cra-art-71-1`), but on the verified date only Chapter IV
  had begun to apply. Per-obligation `applies_from` is therefore **mandatory**
  (`../_schema.md`, instrument kind 1), and several entries carry
  `not yet applicable` in their own right.
- **applies_from:** **2027-12-11** — the Regulation's general application date,
  verbatim in `cra-art-71-2-application`. Exactly two limbs depart from it,
  Art. 14 (**2026-09-11**) and Chapter IV (**2026-06-11**), and each is stated
  on the entry that records it. Definitions, scope and recitals take the general
  date: they are read as part of the act, not as obligations with clocks of
  their own.

Where an entry states any of these fields inline, **the entry's own value wins.**

### Why the grade is `proxy-sourced` and not `primary-fetched`

`eur-lex.europa.eu` sits behind an **AWS CloudFront + WAF JS-challenge**
(`x-amzn-waf-action: challenge`) that blocks non-browser clients outright —
both direct `curl` and `WebFetch` returned empty / HTTP 202. The Official
Journal text was obtained by routing the same EUR-Lex URLs through the proxy.
The content appeared faithful and complete, and the mitigations were real:

- **Two renders were required, and the difference matters.** The HTML render of
  the EUR-Lex document carries Articles 1–71 plus footnotes but **no annexes**;
  only the PDF render carries the full text **including Annexes I–VIII**. Any
  Annex-referencing entry must be sourced from the PDF render — a fact worth
  recording, because the HTML render looks complete until an Annex is needed.
- **Headline dates cross-checked** against the European Commission's own CRA
  summary page (`digital-strategy.ec.europa.eu/en/policies/cra-summary`), which
  independently states the 10 December 2024 entry into force.
- **Recital numbers were assigned positionally.** In the PDF-derived text a
  recital's number renders as a bracketed marker **preceding** its paragraph,
  and citations here follow that rule, spot-checked against the early recitals
  (1)–(9), which render inline and confirm it. **Re-verify a recital number
  before citing it in a filing.**

**Re-probed 2026-07-31 — the block is unchanged, and this page's grade stands.**
A direct `curl -IL` against
`https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R2847`
returned the **identical signature** already recorded here:

```
HTTP/1.1 202 Accepted
Server: CloudFront
x-amzn-waf-action: challenge
Content-Length: 0
```

This was a genuine attempt, not a skipped one, and it **reconfirms rather than
changes** the `proxy-sourced` grade. **Do not re-attempt the same direct probe
expecting a different result** without specific reason to believe the
publisher's WAF configuration has changed. Note the contrast worth knowing:
**older or smaller EUR-Lex documents served cleanly to a direct `curl` in the
same session** (Directive 2005/29/EC, Recommendation 2003/361/EC), so the block
tracks document size or rendering path, **not the domain as a whole**.

**If re-verifying:** try direct EUR-Lex first; on a 202/challenge, fall back to
the same proxy pattern and record which route worked.

---

## Application dates are **per obligation** — the instrument being in force does not mean an obligation bites

| id | what applies | date | status 2026-07-31 |
|---|---|---|---|
| `cra-art-71-1` | **entry into force** | **10 Dec 2024** | past |
| `cra-art-71-2-chapter-iv` | **Chapter IV (Arts. 35–51)** — notification of conformity assessment bodies | **11 Jun 2026** | **already applicable** |
| `cra-art-35-2` | Member States "strive to ensure" enough notified bodies exist | 11 Dec 2026 | not yet due |
| `cra-art-71-2-art-14` | **Art. 14 reporting obligations** (actively exploited vulnerabilities + severe incidents) | **11 Sep 2026** | **not yet applicable** |
| `cra-art-71-2-application` | **full application** — Annex I essential requirements, Arts. 13 and 18–34 economic-operator duties, CE marking, conformity assessment, Annex III/IV classification consequences | **11 Dec 2027** | not yet applicable |
| — | Directive (EU) 2020/1828 (consumer representative actions) becomes applicable to CRA infringements | 11 Dec 2027 | not yet applicable |

**The date most likely to be missed entirely** is **11 June 2026** — Chapter IV
is less commonly cited than the Sept 2026 / Dec 2027 dates and is **already
binding**.

---

## 1. Dates and identity

### `cra-art-71-1`

- **provision:** Art. 71(1) — entry into force
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"This Regulation shall enter into force on the twentieth day
  following that of its publication in the Official Journal of the European
  Union"*, i.e. **10 December 2024**.
- **legal_status:** `in force` · **notes:** the date was independently
  corroborated by the Commission's own CRA summary page.

### `cra-art-71-2-application`

- **provision:** Art. 71(2), first sentence
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"This Regulation shall apply from 11 December 2027."*
- **legal_status:** `not yet applicable` · **applies_from:** 2027-12-11

### `cra-art-71-2-art-14`

- **provision:** Art. 71(2), second sentence, Art. 14 limb
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"...Article 14 shall apply from 11 September 2026..."*
- **legal_status:** `not yet applicable` · **applies_from:** 2026-09-11
- **notes:** the most urgent forward-looking date.

### `cra-art-71-2-chapter-iv`

- **provision:** Art. 71(2), second sentence, Chapter IV limb
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"...Chapter IV (Articles 35 to 51) shall apply from 11 June 2026"*
- **legal_status:** **`in force`** · **applies_from:** 2026-06-11 — **already
  binding as at 2026-07-31.**

### `cra-art-35-2`

- **provision:** Art. 35(2) — notification
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"Member States shall strive to ensure, by 11 December 2026 that
  there is a sufficient number of notified bodies in the Union to carry out
  conformity assessments..."*
- **legal_status:** `in force` (Chapter IV applies) · **applies_from:**
  2026-12-11 for the target date
- **notes:** a **Member-State best-efforts duty**, not a manufacturer compliance
  deadline. Do not present it as one.

---

## 2. Scope — product with digital elements, SaaS, open source

### `cra-art-2-1`

- **provision:** Art. 2(1) — scope
- **text_form:** `verbatim` (proxy-sourced)
- **text:** applies *"to products with digital elements made available on the
  market, the intended purpose or reasonably foreseeable use of which includes a
  direct or indirect logical or physical data connection to a device or
  network."*
- **legal_status:** `not yet applicable` (with the instrument's staggered dates)

### `cra-art-3-1`

- **provision:** Art. 3(1) — definition, "product with digital elements"
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"a software or hardware product and its remote data processing
  solutions, including software or hardware components being placed on the
  market separately."*

### `cra-art-3-2`

- **provision:** Art. 3(2) — definition, "remote data processing"
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"data processing at a distance for which the software is designed
  and developed by the manufacturer, or under the responsibility of the
  manufacturer, and the absence of which would prevent the product with digital
  elements from performing one of its functions."*

### `cra-art-3-21-22`

- **provision:** Art. 3(21) and 3(22) — "placing on the market" / "making
  available on the market"
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"'placing on the market' means the first making available of a
  product with digital elements on the Union market"*; *"'making available on
  the market' means the supply of a product with digital elements for
  distribution or use on the Union market **in the course of a commercial
  activity**, whether in return for payment or free of charge."*

### `cra-recital-11`

- **provision:** Recital 11
- **text_form:** `verbatim` (proxy-sourced)
- **text:** remote data processing solutions are in scope *"irrespective of
  whether data is processed or stored locally on the user's device or remotely
  by the manufacturer"*, but only *"in so far as it is necessary for a
  product... to perform its functions."*

### `cra-recital-12`

- **provision:** Recital 12 — **the load-bearing scope recital**
- **text_form:** `verbatim` (proxy-sourced)
- **text:** *"Directive (EU) 2022/2555 applies to cloud computing services and
  cloud service models, such as Software as a Service (SaaS), Platform as a
  Service (PaaS) or Infrastructure as a Service (IaaS)"*, and *"websites that do
  not support the functionality of a product with digital elements, or cloud
  services designed and developed outside the responsibility of a manufacturer
  of a product with digital elements do not fall within the scope of this
  Regulation"*.
- **notes:** pure SaaS is generally routed to **NIS2** (`nis2.md`), not the CRA
  — **unless** the cloud component is the manufacturer's own remote-data-
  processing solution integral to a CRA-scoped product. That exception is where
  the boundary is genuinely contestable, and the recital's exclusion presupposes
  the cloud service is *not* the manufacturer's own remote-data-processing
  solution.

### `cra-art-2-2-4` · `cra-art-2-7-8` — exclusions

- **provision:** Art. 2(2)–(4) — products covered by sector-specific EU rules;
  Art. 2(7)–(8) — national-security, defence and classified-information
  products. One id per limb, both recorded in this block.
- **text_form:** `normalized summary` — **not the article's words; do not quote
  it**, for either id. (proxy-sourced; both limbs were read in the OJ render and
  the exclusion list is condensed here, not transcribed. Cite the substance and
  the id; a filing that needs the exclusion wording must go to the OJ text.)
- **text:** Excludes products already covered by sector-specific EU rules —
  medical devices (Reg. (EU) 2017/745), in-vitro diagnostics
  (Reg. (EU) 2017/746), motor-vehicle type-approval (Reg. (EU) 2019/2144),
  civil-aviation-certified products (Reg. (EU) 2018/1139), marine equipment
  (Dir. 2014/90/EU); and products developed or modified exclusively for national
  security or defence, or specifically designed to process classified
  information.

### `cra-art-3-48` · `cra-art-3-14` · `cra-art-24` · `cra-recital-17` · `cra-recital-18` · `cra-recital-19` · `cra-recital-20` — open source

**Open source.** Seven ids, one block: two definitions, the steward duty, and
the four recitals that set the scope test. One id per limb.

- **provision:** Art. 3(48) — definition of free and open-source software;
  Art. 3(14) — definition of the open-source software steward; Art. 24 —
  steward obligations; Recitals 17, 18, 19 and 20.
- **text_form:** **per id, not uniform** — `normalized summary` for
  `cra-art-3-48`, `cra-art-3-14` and `cra-art-24`: **not the Regulation's
  words; do not quote them**, cite the substance and the id. In
  `cra-art-3-48` the quotation marks mark the **defined term** only — the
  definition that follows them is restated, not transcribed. `verbatim`
  (proxy-sourced) for `cra-recital-17`, `cra-recital-18`, `cra-recital-19` and
  `cra-recital-20`, and there **only for the spans inside quotation marks**;
  the unquoted sentences around those spans are restatement or this corpus's
  own reading, and are **not** quotable.
- **legal_status:** `not yet applicable` for `cra-art-24` ·
  **applies_from:** 2027-12-11 — the general date; Art. 24 sits outside both
  departing limbs (Art. 14, and Chapter IV = Arts. 35–51). The definitions and
  the recitals take the same general date, read as part of the act.
- **text (per id, below):** each of the following bullets carries that
  id's content.
- `cra-art-3-48` — "free and open-source software" means software whose source
  code is openly shared and which is made available under a free and open-source
  licence granting all rights to make it freely accessible, usable, modifiable
  and redistributable.
- `cra-recital-17` — policy goal of accommodating FOSS development models,
  *"in particular by microenterprises and small and medium-sized enterprises,
  including start-ups, individuals, not-for-profit organisations, and academic
  research organisations."*
- `cra-recital-18` — **the commercial-activity test:** *"only free and
  open-source software made available on the market, and therefore supplied for
  distribution or use in the course of a commercial activity, should fall within
  the scope of this Regulation"*. Funding source and release cadence alone do
  not make an activity commercial; **monetisation by the manufacturer does.**
- `cra-recital-19` / `cra-art-3-14` — the **open-source software steward**: a
  legal person, other than a manufacturer, systematically providing sustained
  support for the development of specific FOSS products intended for commercial
  activities and ensuring their viability. Stewards get *"a light-touch and
  tailor-made regulatory regime"* instead of full manufacturer obligations, and
  are **barred from affixing the CE marking**.
- `cra-art-24` — steward obligations: put in place and document a cybersecurity
  policy for vulnerability handling, and cooperate with market surveillance
  authorities on request. Only a subset of Art. 14's reporting duties applies,
  and only to the extent the steward is involved in the development, or where
  severe incidents affect the steward's own development infrastructure.
- `cra-recital-20` — *"The sole act of hosting products with digital elements on
  open repositories, including through package managers or on collaboration
  platforms, does not in itself constitute the making available on the market of
  a product with digital elements."*

---

## 3. Obligations if in scope

### `cra-annex-i-part-i` — essential cybersecurity requirements (product properties)

- **provision:** Annex I, Part I — essential cybersecurity requirements relating
  to the properties of products with digital elements
- **text_form:** `normalized summary` — **not the Annex's words; do not quote
   it.** (proxy-sourced; the 13 lettered points a–m were read in full from the
   OJ **PDF** render and are condensed here, not transcribed. Cite the Annex
   itself for any wording.)
- **text:** Thirteen categories of product properties: no known exploitable
  vulnerabilities at market release; secure-by-default configuration;
  security-update mechanisms; access control; confidentiality and integrity of
  data; data minimisation; availability and resilience; limited attack surface;
  exploitation mitigation; security logging with user opt-out; and secure,
  permanent **data erasure by the user**.
- **legal_status:** `not yet applicable` · **applies_from:** 2027-12-11

### `cra-annex-i-part-ii` — vulnerability handling

- **provision:** Annex I, Part II — vulnerability-handling requirements
- **text_form:** `normalized summary` — **not the Annex's words; do not quote
   it.** (proxy-sourced; the 8 numbered points were read from the PDF render and
   are condensed here, not transcribed.)
- **text:** Eight manufacturer duties: identify and document vulnerabilities and
  components (**including drawing up an SBOM**); remediate without delay; test
  regularly; publicly disclose fixed vulnerabilities; maintain a coordinated
  vulnerability disclosure policy; facilitate reporting channels; distribute
  updates securely; disseminate available security updates without delay, free
  of charge, with advisory messages.
- **legal_status:** `not yet applicable` · **applies_from:** 2027-12-11

### `cra-annex-i-part-ii-1` — the SBOM requirement specifically

- **provision:** Annex I, Part II, point (1) — the SBOM requirement
- **text_form:** `verbatim` (proxy-sourced)
- **text:** manufacturers must identify and document *"components contained in
  products with digital elements, including by drawing up a software bill of
  materials in a commonly used and machine-readable format covering at the very
  least the top-level dependencies of the products"*.
- **legal_status:** `not yet applicable` · **applies_from:** 2027-12-11
- **notes:** publishing an SBOM is a technical fact and not, by itself,
  compliance — the obligation does not bind until 2027-12-11 and only for a
  product in scope.

### `cra-art-13-1-3` · `cra-art-13-6` · `cra-art-13-8` · `cra-art-13-9` — manufacturer duties

- **provision:** Article 13(1)–(3), (6), (8) and (9) — manufacturer duties
- **text_form:** **per id, not uniform** — `normalized summary` for
  `cra-art-13-1-3`: **not the article's words; do not quote it**, cite the
  substance and the id. `verbatim` (proxy-sourced) for `cra-art-13-6`,
  `cra-art-13-8` and `cra-art-13-9`, and there only for the spans inside
  quotation marks; the unquoted sentences around those spans are restatement
  and are **not** quotable.
- **legal_status:** `not yet applicable` · **applies_from:** 2027-12-11
- **text (per id, below):** each of the following bullets carries that
  id's content.
- `cra-art-13-1-3` — on placing a product on the market, ensure design,
  development and production comply with Annex I Part I, and document and keep
  updated a cybersecurity risk assessment covering intended purpose, reasonably
  foreseeable use, and length of expected use.
- `cra-art-13-6` — on identifying a vulnerability in a component *"including in
  an open source-component"* integrated in the product, report it to the entity
  maintaining that component and remediate per Annex I Part II, sharing any fix
  *"where appropriate in a machine-readable format."*
- `cra-art-13-8` — the **support period** must reflect the expected length of
  use, factoring in user expectations, product nature and comparable products;
  *"the support period shall be **at least five years**"*, or the expected use
  time if shorter. The five-year figure is a **statutory floor, not a target** —
  shorter only where expected use genuinely is, and extendable by future
  Commission delegated acts for specific product categories.
- `cra-art-13-9` — each security update issued during the support period
  *"remains available... for a minimum of **10 years** or for the remainder of
  the support period, whichever is longer."*

### `cra-art-14` — reporting (the duty that starts 11 Sep 2026)

- **provision:** Art. 14(1)–(5); Art. 16 establishes the Single Reporting
  Platform
- **text_form:** `normalized summary` — **not the article's words; do not quote
   it.** The prose below is a restatement; the **hour and day figures within it
   were confirmed against the primary text, not memory** (proxy-sourced), and a
   deadline is the highest-risk field on this page
- **legal_status:** `not yet applicable` · **applies_from:** **2026-09-11**
- **text:**
  - **Art. 14(1)–(2) — actively exploited vulnerabilities** (cite
    `cra-art-14` + the paragraph): simultaneous
    notification to the coordinating CSIRT and ENISA via the Single Reporting
    Platform — early warning within **24 hours** of the manufacturer becoming
    aware; fuller vulnerability notification within **72 hours**; final report
    **no later than 14 days** after a corrective or mitigating measure becomes
    available.
  - **Art. 14(3)–(4) — severe incidents** (cite `cra-art-14` + the
    paragraph): same channel — early warning within
    **24 hours**, incident notification within **72 hours**, final report
    **within one month** of the incident notification.
  - **Art. 14(5)** (cite `cra-art-14` + the paragraph) — an incident
    is **severe** where it negatively affects, or
    is capable of negatively affecting, the product's ability to protect the
    availability, authenticity, integrity or confidentiality of sensitive or
    important data or functions, or has led or could lead to the introduction or
    execution of malicious code in the product or in a user's network and
    information systems.

### `cra-art-28-30` · `cra-art-32` — conformity and CE marking

- **provision:** Articles 28–30 and Article 32 — conformity assessment and CE marking
- **text_form:** `normalized summary` for **both** ids — **not the articles'
   words; do not quote either.** (proxy-sourced; `cra-art-32` additionally draws
   on the corresponding recital, and the module labels A, B, C, H were confirmed
   present in the source.) · **applies_from:** 2027-12-11
- **text (per id, below):** each of the following bullets carries that
  id's content.
- `cra-art-28-30` — manufacturers must draw up an EU declaration of conformity
  once compliance with Annex I is demonstrated via the chosen conformity
  assessment procedure, and affix the **CE marking**; a product that has not
  undergone this cannot lawfully bear CE marking under the CRA regime.
- `cra-art-32` — products **not** classified important/critical may self-assess
  via internal control (module A); **important Class I** may self-assess only
  when applying harmonised standards, otherwise need third-party assessment
  (modules B+C or H); **important Class II and all critical** products always
  require third-party assessment.

### `cra-annex-iii` — important products

- **provision:** Annex III — important products (Class I and Class II)
- **text_form:** `normalized summary` — **not the Annex's words; do not quote
   it.** (proxy-sourced; the full category lists were read from the Annex III PDF
   render and are condensed here, not transcribed.) · **applies_from:** 2027-12-11
- **text:** **Class I (19 categories)** — including identity/access management,
  browsers, password managers, VPN products, **network management systems**,
  SIEM, operating systems, routers/modems/switches, security-function
  microprocessors and microcontrollers, ASIC/FPGA with security functions,
  smart-home security products, connected toys with social/tracking features,
  health-monitoring wearables. **Class II (4 categories)** — including
  hypervisors and container runtimes, firewalls/IDS/IPS, tamper-resistant
  microprocessors and microcontrollers.
- **notes:** classification into these lists changes both the
  conformity-assessment route (`cra-art-32`) and the penalty tier
  (`cra-art-64-2` vs `cra-art-64-3`).

### `cra-annex-iv` — critical products

- **provision:** Annex IV — critical products
- **text_form:** `normalized summary` — **not the Annex's words; do not quote
  it.** (proxy-sourced; the full 3-item list was read and is condensed here, not
  transcribed. The list is complete — the immediately-following "ANNEX V"
  boundary marker confirms nothing was truncated — but completeness of the
  items is not verbatim reproduction of them.) ·
  **applies_from:** 2027-12-11
- **text:** (1) hardware devices with security boxes; (2) smart meter gateways
  within smart metering systems (per Dir. (EU) 2019/944 Art. 2(23)) and other
  devices for advanced security purposes, including secure cryptoprocessing;
  (3) smartcards or similar devices, including secure elements.

---

## 4. Penalties

`text_form`: for the three table rows below, only the **figures** are
verbatim from the primary text (proxy-sourced, retrieved, **not
memory**) — the scope wording is a compressed restatement, per the
id-formation note; `cra-art-64-10` carries its own entry and grade. **applies_from:** 2027-12-11 (with Art. 14's own
date for Art. 14 breaches).

**Id-formation rule — how the first three rows are citable.** `cra-art-64-2`,
`cra-art-64-3` and `cra-art-64-4` have **no standalone `###` entry**;
`cra-art-64-10` does, immediately below. The three table ids are citable
through **this section block** — which states their shared `text_form`,
provenance and `applies_from` — **plus the article and ceiling stated in their
own row**, and through the block the page-wide standing fields above
(instrument, official_url, consulted/`proxy-sourced`, language_version,
verified, legal_status). That is the eight-field set, exactly the inheritance
`../international/iso-27001.md` states for its control ids. Two limits, and
they bind: what each row reproduces from the primary text is its **figures**
(the ceiling and the percentage) — **the scope wording in the `provision`
column is a compressed restatement, not the article's words, so quote the
numbers and never the phrasing**; and because these rows are not `###`
entries, the corpus's lint gate never checks them against the citability
contract. A ceiling is a number, the highest-risk field there is
(`../_schema.md` rule 5): cite it with its `proxy-sourced` grade at the point
of use.

| id | provision | ceiling |
|---|---|---|
| `cra-art-64-2` | Art. 64(2) | Annex I essential requirements or Arts. 13/14 duties — up to **€15,000,000 or 2.5%** of total worldwide annual turnover (preceding financial year), whichever is higher |
| `cra-art-64-3` | Art. 64(3) | Arts. 18–23, 28, 30(1)–(4), 31(1)–(4), 32(1)–(3), 33(5), 39, 41, 47, 49, 53 — up to **€10,000,000 or 2%**, whichever is higher |
| `cra-art-64-4` | Art. 64(4) | supplying incorrect, incomplete or misleading information to notified bodies or market surveillance authorities — up to **€5,000,000 or 1%**, whichever is higher |
| `cra-art-64-10` | Art. 64(10) | carve-out, see below |

### `cra-art-64-10` — the carve-out, and an **unsettled reading**

- **provision:** Article 64(10) — the carve-out from the fines in paragraphs 3–9
- **text_form:** `normalized summary` — **not the article's words; do not
   quote it.** (proxy-sourced; the article was read in full and is restated
   here. The one phrase reproduced verbatim is quoted in the notes below.)
- **text:** Fines under paragraphs 3–9 do **not** apply to (a) microenterprises
  and small enterprises for missing the 24-hour early-warning deadline of
  Art. 14(2)(a)/14(4)(a), or (b) any infringement by **open-source software
  stewards**.
- **legal_status:** `not yet applicable`
- **notes — flagged as analysis, not fact:** paragraph 10 is worded *"by way of
  derogation from paragraphs 3 to 9"* and therefore, **on its face, does not
  reach paragraph 2** — the Annex I / Art. 13 / Art. 14 substantive-fine tier.
  That reading is **this corpus's interpretation, not a settled legal
  conclusion**. Confirm with counsel before relying on any exemption.

---

## 5. Interaction with NIS2 and the GDPR

### `cra-recital-72`

- **provision:** Recital 72
- **text_form:** `verbatim` (proxy-sourced) for the recital; the
  "distinct duty" characterisation below is **synthesis, not a quote**
- **text:** The recital addresses overlap directly, noting *"other complementary
  reporting requirements laid down in Union law, such as Regulation (EU)
  2016/679 [GDPR], Regulation (EU) 2022/2554 [DORA], Directive 2002/58/EC
  [ePrivacy] and Directive (EU) 2022/2555 [NIS2]"* and encouraging Member States
  to consider **national single entry points** for such reporting — while making
  clear that using one *"should not affect the application of the provisions of
  Regulation (EU) 2016/679 and Directive 2002/58/EC"*.
- **synthesis (this corpus's, labelled as such):** CRA Art. 14 reporting is a
  **distinct, additional** duty layered on top of GDPR Art. 33 and NIS2 Art. 23
  (`nis2-dir-art-23`) reporting — **not a substitute for either**. Different
  triggers (product vulnerability/incident vs personal-data breach vs
  NIS2-entity incident), different recipients (ENISA / coordinating CSIRT vs
  supervisory authority vs national CSIRT/competent authority), and clocks that
  are structurally similar in duration but administratively separate.
- **notes:** whether any Member State has stood up a genuine single entry point
  that would functionally merge these filings is a per-jurisdiction question
  this corpus does not record; confirm it for the jurisdiction in question.

### `cra-recital-13`

- **provision:** Recital 13
- **text_form:** `normalized summary` — **not the recital's words; do not quote
   it.** (proxy-sourced; the recital was read in full and is condensed here.)
- **text:** NIS2 can impose **additional** supply-chain cybersecurity
  requirements on essential/important entities that use products meeting only
  the CRA floor; conversely Member States cannot use the CRA to impose
  additional CRA-harmonised requirements on manufacturers beyond it. The two
  regimes regulate **different actors** — CRA: manufacturers of products;
  NIS2: essential/important entities as users/operators — and **can both apply
  to the same organisation in different capacities**.
- **notes:** **the recital number was inferred from its position** immediately
  preceding the "(14)" marker in the PDF render. **Cross-check the live
  numbering before citing it in a filing.**

---

## 6. Operational readiness — **not a legal-text fact**

### `cra-enisa-srp-readiness`

- **instrument:** — (operational status of ENISA's Single Reporting Platform)
- **provision:** **not a provision** — the operational readiness of ENISA's Single Reporting Platform, deliberately quarantined on this page as a non-law fact
- **text_form:** `topic only`
- **text:** Two secondary compliance-industry sources report that the **Single
  Reporting Platform** required for Art. 14 notifications was **still not live
  as of late June 2026**, with registration instructions and the reporting
  format allegedly still unpublished. If accurate, that is a live
  compliance-readiness gap roughly six weeks before the 11 September 2026
  statutory deadline.
- **official_url:** — · **consulted:**
  https://www.cyberresilienceact.eu/news/cra-single-reporting-platform-not-yet-live.html
  · https://www.crowell.com/en/insights/client-alerts/eu-cyber-resilience-act-countdown-11-september-2026-incidentvulnerability-reporting-deadline-is-less-than-100-days-away
  — **verification_grade:** `secondary-corroborated`
- **verified:** 2026-07-31 · **legal_status:** n/a — **not law**
- **notes:** **kept deliberately separate from every legal-text entry on this
  page.** This is an operational/journalistic claim; EUR-Lex cannot confirm or
  deny platform *operational* status, only the *legal* obligation date. **Do not
  give it the evidentiary weight of the Regulation's own text.**
  **unverified — confirm directly at enisa.europa.eu.**

---

## Verification pitfalls specific to this instrument

- **The three headline dates** (10 Dec 2024, 11 Sep 2026, 11 Dec 2027) and the
  five-year support-period floor were confirmed against the primary text and
  match the commonly-circulated figures — no disagreement was found.
- **The date easy to under-weight rather than misremember:** `11 June 2026`
  (Chapter IV), already in force — the one most likely to be **missed entirely**.
- **One claim unverifiable through EUR-Lex by construction:**
  `cra-enisa-srp-readiness` — platform operational status is not a legal-text
  fact.
- **One reading offered as analysis, not fact:** the `cra-art-64-10`
  derogation scope.

## Ingest requests (open)

- Direct EUR-Lex retrieval (or a licensed/official mirror) to lift this page
  from `proxy-sourced`.
- Italian-language ingest of the CRA if Italian-jurisdiction citations are
  needed.
- ENISA's own statement on Single Reporting Platform availability.
- Live re-check of the recital numbering used by `cra-recital-13`.

## Neighbours

- `nis2.md` — `cra-recital-12` routes SaaS/PaaS/IaaS **to NIS2**;
  `cra-recital-13` explains dual application. The same EUR-Lex WAF blocks the
  NIS2 Directive text, and the proxy route recorded above is the workaround that
  lifts those entries off secondary sources.
- `../_schema.md` — the entry contract.
- GDPR Art. 33 breach notification and ISO/IEC 27001 secure-development and
  vulnerability-management controls are the adjacent regimes most often cited
  alongside this one; neither is recorded in this corpus.
