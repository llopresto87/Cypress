# Directive (EU) 2022/2555 (NIS2) — EU + national transposition

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Orientation for citing this directive and its transposing national
> acts where recorded — a directive alone does not bind persons; the
> transposing national act does (see `transposed_by` per entry). Confirm
> currency before relying on any entry, especially size-gate thresholds and
> deadlines, which are the highest-risk fields here. Entry contract:
> `../_schema.md`.

**Instrument kind:** `directive` — **binds Member States, not persons.** What a
national authority enforces is the **transposing act**. The national
transposition recorded here is Italy's **D.Lgs. 138/2024** and the ACN
determinazioni made under it. Ingested 2026-07-31.

---

## ⚠ CITATION TRAP — read before writing the word "Art. 34"

**The Italian decree's Art. 34 is a different provision from the Directive's
Art. 34.**

| | Art. 34 |
|---|---|
| **Directive (EU) 2022/2555** | **sanctions** (the €10M/2% and €7M/1.4% ceilings) |
| **D.Lgs. 138/2024** | **supervisory criteria** — Capo V "Monitoraggio, vigilanza ed esecuzione", *not* sanctions |

**The Italian sanction figures are in decree Art. 38** (`it-dlgs-138-art-38`),
which cross-references decree Art. 34's criteria.

**"NIS2 Art. 34" cited for sanctions in an Italian context is wrong.** Say which
instrument. This is a same-number/different-subject collision, it is exactly the
kind of error that survives review because it looks right, and it is why this
page splits its entries by instrument rather than by topic.

## Standing fields — FOUR provenance groups, and they must not be flattened

Every entry inherits `official_url`, `consulted` + `verification_grade`,
`language_version`, `verified` and `legal_status` from **its group below** —
never from a page-level banner. Averaging the four into one page-level
"verified" would launder two of them (`../_schema.md` rule 4). `provision`,
`text_form` and `text` are **always stated per entry**. Where an entry states any
inheritable field inline, **the entry's own value wins.**

**`instrument` comes from the id prefix**, because this page carries three
instruments and none of them is the page's default:

| id prefix | instrument | kind |
|---|---|---|
| `nis2-dir-…` | Directive (EU) 2022/2555 (NIS2) | `directive` — binds Member States, not persons |
| `it-dlgs-138-…` | D.Lgs. 138/2024 (Italian transposing decree) | national statute |
| `acn-…` | ACN determinazione or published register made under that decree | regulator decision |

An entry whose heading names both a Directive article **and** a decree article
cites the **Directive** as its instrument and records the decree article in
`transposed_by`; the decree's own provisions have their own `it-dlgs-138-…`
entries. Where the two diverge, the decree is what a national authority enforces.

### Group A — Directive Arts. 20, 21, 23, 34

- **consulted:** EUR-Lex full EN text, retrieved via the `r.jina.ai` read-only
  proxy and read directly — **verification_grade:** `proxy-sourced`. **A proxy is
  not the official source.**
- **official_url:** https://eur-lex.europa.eu/eli/dir/2022/2555/oj/eng ·
  IT: https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32022L2555
- **language_version:** English, original OJ text as published; no consolidated
  version recorded as at 2026-07-31.
- **verified:** 2026-07-31 · **legal_status:** `in force`

### Group B — every other Directive entry (Arts. 2(1), 3, 6(28), Annexes I/II)

- **consulted:** EUR-Lex blocked on every direct URL pattern by an AWS WAF
  bot-challenge; text taken from the `nis-2-directive.com` mirror and
  cross-checked against independent commentary. **Not re-fetched**, though these
  articles are present in the retained snapshot —
  **verification_grade:** `secondary-corroborated`. **Not verified against the
  official text; never present a Group B entry as a quotation.**
- **official_url:** as Group A (the same OJ act).
- **language_version:** English via the mirror, original OJ text as published.
- **verified:** 2026-07-31 · **legal_status:** `in force`

### Group C — D.Lgs. 138/2024 article text

- **consulted:** the official Gazzetta Ufficiale PDF, text extracted
  programmatically from PDF content streams —
  **verification_grade:** `primary-fetched`.
- **official_url:** https://www.gazzettaufficiale.it/eli/id/2024/10/01/24G00155/SG
  · Normattiva: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2024-09-04;138
- **language_version:** Italian, as published in the GU (original publication
  text; no Normattiva *"Testo in vigore dal:"* consolidation header was recorded
  in this pass).
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **Extraction caveat, recorded so a refresh knows how this was obtained:** the
  GU PDF was parsed by **ad-hoc content-stream extraction — no PDF renderer was
  available**. That is why article *titles* and specific quoted fragments are
  `verbatim` while some surrounding paragraphs are marked "not extracted in this
  pass". A refresh with a real renderer should be able to complete them.

### Group D — the ACN determinazioni and published registers

- **consulted:** the official PDFs from `acn.gov.it`, fetched directly, no proxy,
  parsed cleanly — **verification_grade:** `primary-fetched`. A published
  register page carries its own weaker grade inline where it is not a PDF.
- **official_url:** **stated per entry** — each determinazione has its own.
- **language_version:** Italian, as published.
- **verified:** 2026-07-31 · **legal_status:** `in force`

## ⚠⚠ The Italian baseline-measures deadline is a ROLLING per-entity clock — **"31 October 2026" is not a rule**

> ### The rule is a formula, not a date
>
> **ACN Determinazione n. 379907/2025, Art. 3(1), verbatim:**
>
> > Il termine per l'adozione delle misure di sicurezza di base di cui agli
> > allegati 1 e 2 è fissato in **diciotto mesi dalla ricezione, da parte del
> > soggetto NIS, della comunicazione di inserimento nell'elenco dei soggetti
> > NIS**.
>
> ### **BASELINE MEASURES: 18 MONTHS FROM *THAT ENTITY'S OWN* NOTIFICATION OF INCLUSION.**
> ### **INCIDENT NOTIFICATION (Art. 3(2)): 9 MONTHS FROM THE SAME NOTIFICATION.**
>
> **This is a rolling, per-entity clock. It is not a cohort date and not a
> calendar date.** Two entities notified three months apart have deadlines three
> months apart. **A rolling clock and a fixed date produce different answers per
> entity** — which is exactly why substituting one for the other is not a
> rounding error.

**Where the widely-circulated "31 October 2026" comes from.** Press commentary
(`cybersecurity360.it` and several other secondary sources) computed it by adding
18 months to the **2025 notification round**. That round is recorded in this
corpus only as "Apr 2025 (12–13 Apr per one source)", itself
`secondary-corroborated`. **12–13 April 2025 + 18 months lands on 12–13 October
2026, not 31 October** — so the press figure is a rounded restatement for a
cohort, not a computation this corpus can reproduce, let alone a
determinazione-stated figure. The determinazione text does not contain that date
anywhere.

**What to do with it:**

1. **Never present "31 October 2026" as a quoted or determinazione-stated date.**
   At best it approximates when the clock runs out for the 2025 cohort.
2. **Cite the formula.** It is `primary-fetched`, it is durable, and it is the
   headline claim of the entry.
3. **A precise date for a specific entity requires that entity's own
   notification-receipt date** — a per-entity fact this corpus cannot supply.
4. **The weak link in the deadline chain is the 2025 notification date**, not the
   determinazione text. That remains `secondary-corroborated` and is the item to
   chase if a cohort-level date is ever needed.

---

## 1. Identity

### `nis2-dir-2022-2555`

- **instrument:** Directive (EU) 2022/2555 of the European Parliament and of the
  Council of 14 December 2022 on measures for a high common level of
  cybersecurity across the Union, amending Regulation (EU) No 910/2014 and
  Directive (EU) 2018/1972, and repealing Directive (EU) 2016/1148 (NIS 2
  Directive) — *directive*
- **provision:** the act as a whole
- **text_form:** `normalized summary`
- **text:** Sets the EU-wide baseline for cybersecurity risk management,
  governance, incident reporting and supervision of essential and important
  entities. Repeals NIS1 (Directive (EU) 2016/1148) with effect from
  **18 October 2024**.
- **published:** OJ L 333, 27.12.2022, pp. 80–152 · **CELEX:** 32022L2555
- **official_url:** https://eur-lex.europa.eu/eli/dir/2022/2555/oj/eng ·
  IT: https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32022L2555
- **consulted:** mirror + two independent secondary sources; **EUR-Lex blocked
  by bot-challenge** — **verification_grade:** `secondary-corroborated`
- **language_version:** English (via mirror), original OJ text as published; no
  consolidated version recorded as at 2026-07-31
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-2024` (Italy) ·
  **transposition_status:** adopted · **divergence:** see the Art. 34 trap above
  and `it-dlgs-138-art-38`; no systematic divergence analysis was performed —
  `not assessed`
- **entry into force:** 16 January 2023 (20 days after OJ publication — the
  standard EU rule). **The Directive's own final article number was not read**
  (WAF block); corroborated from Covington "Inside Privacy" and the EFTA/EEA-Lex
  factsheet. **unverified — confirm the article number before citing it.**
- **transposition deadline:** **17 October 2024** — corroborated by Wikipedia
  (citing the Directive) and by the Italian decree's own adoption on
  4 September 2024, ahead of it.

### `it-dlgs-138-2024`

- **instrument:** Decreto Legislativo 4 settembre 2024, n. 138 — *national
  transposing act*
- **provision:** the act as a whole
- **official title (IT):** "Recepimento della direttiva (UE) 2022/2555, relativa
  a misure per un livello comune elevato di cibersicurezza nell'Unione, recante
  modifica del regolamento (UE) n. 910/2014 e della direttiva (UE) 2018/1972 e
  che abroga la direttiva (UE) 2016/1148."
  **Caveat preserved:** the title came from a search snippet quoting the
  decree's heading and was **not** re-verified character-for-character against
  the extracted PDF title page — **treat the exact punctuation as indicative;
  confirm against Normattiva before quoting it verbatim in a legal document.**
- **text_form:** `normalized summary` (the act as a whole; individual articles
  below carry `verbatim` where extracted)
- **published:** Gazzetta Ufficiale n. 230, 1 October 2024, codice redazionale
  **24G00155**
- **official_url:**
  https://www.gazzettaufficiale.it/eli/id/2024/10/01/24G00155/SG ·
  Normattiva:
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2024-09-04;138
- **consulted:** the official GU PDF (content-stream extraction) + ACN's own
  "la normativa" page — **verification_grade:** `primary-fetched`
- **language_version:** Italian, as published in the GU (original publication
  text; no Normattiva *"Testo in vigore dal:"* consolidation header was recorded
  in this pass)
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **entry into force:** **16 October 2024**, stated directly by ACN and
  consistent with Italy's standard 15-day *vacatio legis* (1 Oct + 15 days).
- **repeals:** D.Lgs. 65/2018 (Italy's NIS1 transposition).
- **structure:** 6 Capi, 44 articles + 4 Allegati — Capo I generali (1–8) ·
  Capo II quadro nazionale (9–17) · Capo III cooperazione (18–22) ·
  Capo IV obblighi di gestione del rischio e notifica (23–33) ·
  Capo V monitoraggio, vigilanza ed esecuzione (34–39) ·
  Capo VI finali e transitorie (40–44).
- **notes — two sharp edges from the extraction, preserved:**
  1. **No dedicated "Entrata in vigore" article was found for this decree** in
     the primary PDF. The extraction did find an "Art. 4 — Entrata in vigore"
     clause elsewhere in the *same GU issue n. 230*, which **bundles multiple
     unrelated acts in one PDF**. That clause belongs to a **different act** and
     **must not be conflated** with D.Lgs. 138/2024.
  2. **Date conflict, unresolved:** one secondary source
     (autorita-trasporti.it) says the decree's provisions "apply from
     18/10/2024". That is almost certainly the EU-level NIS1-repeal date, not
     the Italian decree's entry into force. Both dates are recorded; **confirm
     which date governs which obligation** if it becomes decision-relevant.

---

## 2. Scope

### `nis2-dir-art-2-1` — the size gate

- **provision:** Directive Art. 2(1)
- **text_form:** `normalized summary` (the mirror reproduced the article text,
  but this corpus does not treat mirror text as quotable)
- **text:** The Directive applies to public or private entities of a type
  referred to in Annex I or II which qualify as **medium-sized enterprises**
  under Article 2 of the Annex to Recommendation 2003/361/EC, or exceed those
  ceilings — i.e. from the medium-enterprise threshold **up** — subject to
  size-independent exceptions (telecom, trust-service and DNS providers, sole
  providers of a critical service in a Member State, public administration,
  and entities designated critical under Directive (EU) 2022/2557).
- **official_url:**
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022L2555
- **consulted:** mirror — **verification_grade:** `secondary-corroborated` for
  the Art. 2(1) text itself. **The thresholds it points at are
  `primary-fetched`** from Recommendation 2003/361/EC, Annex Art. 2, retrieved
  from EUR-Lex.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-2024` (Italy — D.Lgs. 138/2024 transposes the
  Directive as a whole); the decree article transposing *this* provision is
  `not recorded — ingest pending` · **transposition_status:** adopted ·
  **divergence:** `not assessed`

> #### ⚠ The gate is the MEDIUM-enterprise ceiling, **not** the small-enterprise one
>
> | | Headcount | Turnover | Balance sheet |
> |---|---|---|---|
> | **medium — the NIS2 gate** | **fewer than 250** | **≤ EUR 50 million** | **≤ EUR 43 million** |
> | small — *a different category, frequently substituted in error* | fewer than 50 | ≤ EUR 10 million | ≤ EUR 10 million |
>
> **Which figure is used changes which entities are captured at all.** An entity
> with 120 employees and EUR 30M turnover sits squarely inside the medium band
> and is therefore in scope on size, subject to the sector tests — a conclusion
> the small-enterprise figures would obscure.
>
> A wrong number carrying an "unverified" flag is a sharper failure than the
> flag implies: "unverified" invites *confirmation*, and confirming a figure
> lifted from the wrong category preserves the error rather than catching it.
> See `../_schema.md` → "The amendment trap", rule 5: confirm which **category**
> a figure defines, not merely that the figure appears in the document.
>
> **Not evaluated:** the Recommendation's autonomous / partner / linked-enterprise
> **aggregation rules** (Annex Arts. 3–6) decide *whose* headcount and turnover
> count for a given legal entity, and for a subsidiary in a group they are often
> decisive. `not recorded` in this corpus.

- **notes:** **Below this gate none of the sector questions matter**, subject to
  NIS2's own narrow size-independent exceptions (telecom, trust-service and DNS
  providers, sole providers of a critical service in a Member State, public
  administration, and entities designated critical under Directive (EU)
  2022/2557).

### `nis2-dir-art-3` — essential vs important

- **provision:** Directive Art. 3
- **text_form:** `normalized summary` · **verification_grade:**
  `secondary-corroborated`
- **text:** Annex I + large enterprise → **essential**. Annex I + medium →
  **important**. **Annex II entities of any size → important**, not essential,
  unless individually designated otherwise by the Member State. Narrow
  size-independent exceptions are essential regardless of size (qualified trust
  service providers, TLD registries, DNS service providers).
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-2024` (Italy — D.Lgs. 138/2024 transposes the
  Directive as a whole); the decree article transposing *this* provision is
  `not recorded — ingest pending` · **transposition_status:** adopted ·
  **divergence:** `not assessed`
- **notes:** the widely-repeated framing that essential entities face **ex-ante
  and ex-post** supervision while important entities face **ex-post only** is a
  **secondary-source summary** that was **not** verified against the Directive's
  supervision articles (Arts. 32–33) — `unverified — confirm before relying on
  it`.

### `nis2-dir-annex-i` — 11 sectors of high criticality

- **provision:** Annex I — sectors of high criticality
- **text_form:** `normalized summary` · **verification_grade:**
  `secondary-corroborated` (two independent mirrors agree)
- **text:** Energy · Transport · Banking · Financial market infrastructures ·
  Health · Drinking water · Waste water · **Digital infrastructure** (IXPs, DNS
  providers, TLD registries, **cloud computing providers**, data centres, CDNs,
  trust service providers, electronic communications providers) · **ICT service
  management (B2B)** (managed service providers, managed security service
  providers) · Public administration · Space.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-2024` (Italy — D.Lgs. 138/2024 transposes the
  Directive as a whole); the decree annex transposing *this* annex is
  `not recorded — ingest pending`. **Do not map it to the ACN determinazione's
  Allegati 1–4** — those are baseline-measure and incident specifications, not
  sector lists · **transposition_status:** adopted ·
  **divergence:** `not assessed`

### `nis2-dir-annex-ii` — 7 other critical sectors

- **provision:** Annex II — other critical sectors
- **text_form:** `normalized summary` · **verification_grade:**
  `secondary-corroborated` (two independent mirrors agree)
- **text:** Postal and courier services · Waste management · Chemicals · Food ·
  Manufacturing · **Digital providers: providers of online marketplaces,
  providers of online search engines, providers of social networking services
  platforms** · Research.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-2024` (Italy — D.Lgs. 138/2024 transposes the
  Directive as a whole); the decree annex transposing *this* annex is
  `not recorded — ingest pending`. **Do not map it to the ACN determinazione's
  Allegati 1–4** — those are baseline-measure and incident specifications, not
  sector lists · **transposition_status:** adopted ·
  **divergence:** `not assessed`
- **notes:** **Annex II.6, "providers of online marketplaces"**, sits in
  **Annex II** — the **important**-entity track — never Annex I, regardless of
  size.

### `nis2-dir-art-6-28` — "online marketplace" (EU level)

- **provision:** Directive Art. 6(28)
- **text_form:** `normalized summary` · **verification_grade:**
  `secondary-corroborated`
- **text:** "online marketplace" means an online marketplace as defined in
  Article 2, point (n), of Directive 2005/29/EC.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-mercato-online` — the D.Lgs. 138/2024
  definitions article, whose «mercato online» definition this page records
  verbatim and which carries the same Art. 2(n) cross-reference (the decree's
  definitions **article number** is `not recorded — ingest pending`) ·
  **transposition_status:** adopted · **divergence:** `not assessed`
- **notes:** Art. 2(n) of Directive 2005/29/EC was **inserted by Directive (EU)
  2019/2161** (the Omnibus Directive) — the original 2005 text has no point (n).
  Cite the **consolidated** Directive 2005/29/EC, never the original.

### `it-dlgs-138-mercato-online` — the national definition, **verbatim**

- **instrument:** D.Lgs. 138/2024, definitions article — *national transposing
  act*
- **provision:** the definitions article, «mercato online» — the article *number* is `not recorded — ingest pending` (the extraction captured the definition text, not its article heading)
- **text_form:** **`verbatim`** (primary extraction from the official GU PDF)
- **text (IT, verbatim):**
  > «mercato online»: un servizio che utilizza un software, compresi siti web,
  > parte di siti web o un'applicazione, gestito da o per conto del
  > professionista, che permette ai consumatori di concludere contratti a
  > distanza con altri professionisti o consumatori, quale definito
  > all'articolo 2, lettera n), della direttiva 2005/29/CE del Parlamento
  > europeo e del Consiglio, dell'11 maggio 2005.
- **English gloss (NOT an official translation):** "a service using software,
  including websites, part of a website, or an application, operated by or on
  behalf of the trader, that allows **consumers** to conclude distance contracts
  with other traders or consumers, as defined in Art. 2(n) of Directive
  2005/29/EC."
- **official_url:**
  https://www.gazzettaufficiale.it/eli/id/2024/10/01/24G00155/SG
- **consulted:** official GU PDF, content-stream extraction —
  **verification_grade:** `primary-fetched`
- **language_version:** Italian, GU text
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **notes — how the definition is structured:** **the operative word is
  "consumatori".** The definition is structurally a **two-sided-market test**
  requiring (a) a software/platform layer operated by or for a trader,
  (b) connecting **third parties** to conclude contracts, and (c) at least one
  side described as **consumers**. Whether a **B2B-only** platform qualifies
  therefore turns on that consumer anchor.
  Directive 2005/29/EC defines "consumer" as "any natural person who … is acting
  for purposes which are outside his trade, business, craft or profession"
  (Art. 2(a)); that wording is `primary-fetched` from EUR-Lex. The decree's
  cross-reference is accurate and current, and the EU-level definition of "online
  marketplace" it points at (Art. 2(n), **inserted by the 2019 Omnibus
  Directive**) matches this decree wording almost verbatim.
  **What that settles and what it does not:** it makes the *test* citable — a
  natural person acting outside trade or profession — and it supplies a
  **structural** argument that a genuinely B2B-only platform has no party meeting
  it. It does not, by itself, qualify or disqualify any given platform; that is a
  fact-specific determination. Secondary commentary (flexiblebit.com)
  additionally reads a first-party single-vendor webshop as outside "online
  marketplace" on the separate, structural ground that it lacks the multi-vendor
  intermediary function.

---

## 3. Obligations

### `nis2-dir-art-21` / `it-dlgs-138-art-24` — risk-management measures

- **provision:** Directive Art. 21(1)–(2); Italian decree **Art. 24**
  ("Obblighi in materia di misure di gestione dei rischi per la sicurezza
  informatica")
- **text_form:** **`verbatim`** for the Directive's Art. 21(1)–(5) (fetched
  2026-07-31); the decree's **article number, title and opening clause are
  `verbatim`** from the GU extraction, its full paragraph text was **not
  extracted in this pass**
- **verification_grade:** Directive limb **`proxy-sourced`**; decree limb
  `primary-fetched` (title/number/opening clause only)
- **text:** Both essential and important entities must implement "appropriate
  and proportionate technical, operational and organisational measures" on an
  all-hazards basis, covering: (a) risk-analysis and information-system security
  policies; (b) incident handling; (c) business continuity — backup, disaster
  recovery — and crisis management; (d) **supply-chain security**, including
  security aspects of relationships with direct suppliers and service providers;
  (e) security in acquisition, development and maintenance, including
  vulnerability handling and disclosure; (f) policies to assess the
  effectiveness of the measures; (g) basic cyber hygiene and training;
  (h) cryptography and encryption policies; (i) HR security, access control,
  asset management; (j) MFA/continuous authentication, secured voice/video/text
  and emergency communications. Para. 3 requires weighing supplier-specific
  vulnerabilities and suppliers' secure-development practices; para. 4 requires
  prompt corrective action on identified non-compliance. The ten-category list
  (a)–(j) above matches the fetched primary text almost word for word.
- **also verbatim in the retained snapshot:** Art. 21(5)'s implementing-act
  mandate (technical and methodological requirements for cloud, CDN, managed
  service, **online-marketplace** and other digital providers, due by
  17 October 2024).
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-art-24` — D.Lgs. 138/2024 **Art. 24**, per
  this entry's own provision line · **transposition_status:** adopted ·
  **divergence:** `not assessed` — the decree article's full paragraph text was
  not extracted in this pass, so no word-level comparison is possible yet

### `nis2-dir-art-21-2-d` — supply-chain security

- **provision:** Directive Art. 21(2)(d) and 21(3)
- **text_form:** `normalized summary` · **verification_grade:**
  `secondary-corroborated`
- **text:** Supply-chain security, including security-related aspects of the
  relationship between each entity and its **direct suppliers or service
  providers**; entities must take into account each direct supplier's specific
  vulnerabilities and the overall quality of its products and cybersecurity
  practices, including its secure development procedures.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-art-24` — D.Lgs. 138/2024 **Art. 24**
  transposes Directive Art. 21; the decree **paragraph** corresponding to
  Art. 21(2)(d) specifically is `not recorded — ingest pending` ·
  **transposition_status:** adopted · **divergence:** `not assessed`
- **notes — the indirect-reach mechanism:** where a **customer** is itself an
  in-scope essential or important entity, that customer's own Art. 21(2)(d)
  duties extend to **its direct suppliers**, including its software suppliers.
  The customer may then have to assess a supplier's secure-development
  practices, vulnerability handling and product quality. **NIS2 can therefore
  reach a supplier contractually even where the supplier is never itself
  classified as an essential or important entity.** That is a commercial and
  engineering consequence, not a legal qualification of the supplier.

### `nis2-dir-art-23` / `it-dlgs-138-art-25` — incident reporting

- **provision:** Directive Art. 23; Italian decree **Art. 25** ("Obblighi in
  materia di notifica di incidente" — title `verbatim` from the GU extraction)
- **text_form:** **`verbatim`** for the Directive's Art. 23(3) and 23(4)
  (fetched 2026-07-31); the two decree fragments quoted below are **`verbatim`**
- **verification_grade:** Directive limb **`proxy-sourced`**; decree limb
  `primary-fetched`
- **text:**

  | Stage | Deadline | Content |
  |---|---|---|
  | Early warning | **within 24 hours** of becoming aware of the significant incident | indicates suspected unlawful/malicious cause and possible cross-border impact |
  | Incident notification | **within 72 hours** of becoming aware | updates the early warning; initial severity/impact assessment; indicators of compromise where available |
  | Intermediate report | on request of the CSIRT/competent authority | status updates |
  | Final report | **within one month** of the incident notification (if the incident is ongoing: a progress report at one month, then a final report within one month of resolution) | detailed description, root cause / threat type, mitigations taken |

- **decree text, verbatim:** *"...senza indebito ritardo e comunque entro 24 ore
  da quando sono venuti a conoscenza dell'incidente significativo"* and
  *"...una relazione finale entro un mese dalla trasmissione della notifica
  dell'incidente"*. A separate 24-hour sub-rule for qualified trust service
  providers was confirmed in the same extraction.
- **recipients:** CSIRT Italia and/or the competent NIS authority (ACN or the
  relevant sectoral authority).
- **the "significant incident" test, Art. 23(3), EN verbatim:**

  > 3. An incident shall be considered to be significant if:
  > (a) it has caused or is capable of causing severe operational disruption of the services or financial loss for the entity concerned;
  > (b) it has affected or is capable of affecting other natural or legal persons by causing considerable material or non-material damage.

- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-art-25` — D.Lgs. 138/2024 **Art. 25**, per
  this entry's own provision line · **transposition_status:** adopted ·
  **divergence:** `not assessed` — the decree side is title-and-opening-clause
  only, so no word-level comparison is possible yet (see the note below)
- **notes:** **the decree side (`it-dlgs-138-art-25`) is title-and-opening-clause
  only**, so for an Italian obligation the decree wording remains unconfirmed —
  do not assume the transposition is word-identical to the Directive.
- **also verbatim (Art. 23(4)), and worth reading before designing an
  incident process:** the derogation requiring a **trust service provider** to
  notify within **24 hours** rather than 72 for incidents affecting its trust
  services, and Art. 23(4)(e)'s rule that an incident still ongoing at final-report
  time requires a **progress report then, and a final report within one month of
  the incident being handled**.

### `nis2-dir-art-20` / `it-dlgs-138-art-23` — governance and management liability

- **provision:** Directive Art. 20; Italian decree **Art. 23** ("Organi di
  amministrazione e organi direttivi" — title `verbatim` from the GU extraction)
- **text_form:** **`normalized summary`** for the Directive's Art. 20(1)–(2) —
  the wording was fetched 2026-07-31 but is restated here, **not transcribed; do
  not quote it** · **verification_grade:** Directive limb **`proxy-sourced`**;
  decree limb `primary-fetched` for the article number and title **only — the
  full paragraph text was not extracted in this pass; `unverified — confirm the
  decree's full text`**
- **text:** Management bodies of essential and important entities must approve
  the Art. 21 risk-management measures, oversee their implementation, and **can
  be held liable** for the entity's infringements of that article — without
  prejudice to national liability rules for public institutions and officials.
  Art. 20(2) requires management-body members to undergo cybersecurity training
  and encourages entities to extend similar training to employees generally.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-art-23` — D.Lgs. 138/2024 **Art. 23**, per
  this entry's own provision line · **transposition_status:** adopted ·
  **divergence:** `not assessed` — the decree article's full paragraph text was
  not extracted in this pass, so no word-level comparison is possible yet

### `it-dlgs-138-art-38` — sanctions (Italy), **verbatim**

- **provision:** D.Lgs. 138/2024 **Art. 38** ("Sanzioni amministrative")
- **text_form:** **`verbatim`** (primary extraction from the official GU PDF)
- **text (IT, verbatim) — essential entities:**
  > ...con sanzioni amministrative pecuniarie fino a un massimo di euro
  > 10.000.000 o del 2% del totale del fatturato annuo su scala mondiale per
  > l'esercizio precedente del soggetto, calcolato secondo le modalità previste
  > della raccomandazione 2003/361/CE della Commissione, del 6 maggio 2003, se
  > tale importo è superiore, il cui minimo è fissato nella misura di un
  > ventesimo del massimo edittale.
- **text (IT, verbatim) — important entities:**
  > ...con sanzioni amministrative pecuniarie fino a un massimo di euro
  > 7.000.000 o dell'1,4% del totale del fatturato annuo su scala mondiale per
  > l'esercizio precedente del soggetto...
- **in figures:** essential — up to **€10,000,000 or 2%** of total worldwide
  annual turnover for the preceding financial year, **whichever is higher**;
  important — up to **€7,000,000 or 1.4%**, whichever is higher.
- **official_url:**
  https://www.gazzettaufficiale.it/eli/id/2024/10/01/24G00155/SG
- **consulted:** official GU PDF — **verification_grade:** `primary-fetched`
- **language_version:** Italian, GU text
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **notes:** these match the Directive's Art. 34 ceilings (Member States must
  set national maxima at *least* that high), and were independently corroborated
  by secondary legal commentary **before** the primary text was extracted — so
  this is the best-evidenced entry on the page. **Cite decree Art. 38, never
  decree Art. 34** — see the trap at the top.

### `nis2-dir-art-34` — sanctions (EU level)

- **provision:** Directive Art. 34 — "General conditions for imposing
  administrative fines on essential and important entities"
- **text_form:** **`verbatim`** for paragraphs 4–5 (fetched 2026-07-31) ·
  **verification_grade:** **`proxy-sourced`**, independently corroborated by the
  primary decree text in `it-dlgs-138-art-38`
- **text (EN, verbatim, the ceiling paragraphs):**

  > 4. Member States shall ensure that where they infringe Article 21 or 23, essential entities are subject … to administrative fines of a maximum of at least EUR 10 000 000 or of a maximum of at least 2 % of the total worldwide annual turnover in the preceding financial year of the undertaking to which the essential entity belongs, whichever is higher.
  >
  > 5. Member States shall ensure that where they infringe Article 21 or 23, important entities are subject … to administrative fines of a maximum of at least EUR 7 000 000 or of a maximum of at least 1,4 % of the total worldwide annual turnover in the preceding financial year of the undertaking to which the important entity belongs, whichever is higher.

- **verified:** 2026-07-31 · **legal_status:** `in force`
- **transposed_by:** `it-dlgs-138-art-38` — D.Lgs. 138/2024 **Art. 38**
  ("Sanzioni amministrative"), **never** decree Art. 34; see the citation trap
  at the top of this page · **transposition_status:** adopted ·
  **divergence:** `not assessed` — the decree's ceilings match the Directive's
  minimum-maxima, but no systematic divergence analysis was performed
- **notes:** **the Art. 34 trap makes this entry easy to misuse: for an Italian
  obligation cite `it-dlgs-138-art-38`, never this entry and never decree
  Art. 34.** A directive does not bind persons.

### `it-dlgs-138-art-34` — the trap entry

- **provision:** D.Lgs. 138/2024 **Art. 34**, Capo V ("Monitoraggio, vigilanza
  ed esecuzione", Artt. 34–39)
- **text_form:** `topic only` · **verification_grade:** `primary-fetched` for
  its placement and subject; the article text was **not** extracted
- **text:** Supervisory **criteria** — **not** sanction amounts.
  `it-dlgs-138-art-38` cross-references these criteria.
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **notes:** this entry exists solely so that a search for "decree Art. 34"
  lands on the correction rather than on the sanctions.

---

## 4. Registration and phased compliance (Italy)

Legal basis: decree **Art. 7** ("Identificazione ed elencazione dei soggetti
essenziali e dei soggetti importanti") — **verbatim** from the GU extraction:
*"Dal 1° gennaio al 28 febbraio di ogni anno successivo..."* — and decree
**Art. 42** ("Fase di prima applicazione"), verbatim in context:
*"...ai sensi dell'articolo 7, entro il 17 gennaio 2025..."*.

**Art. 42's first-wave list explicitly names "fornitori di mercati online"**
(providers of online marketplaces), alongside *"i fornitori di servizi di cloud
computing, [fornitori di reti di] distribuzione dei contenuti, i fornitori di
servizi gestiti, i fornitori di servizi di sicurezza gestiti, ... di motori di
ricerca online o di piattaforme di servizi di social network."*

| id | milestone | date | status 2026-07-31 | basis | grade |
|---|---|---|---|---|---|
| `it-dlgs-138-art-42` | first-wave registration (cloud / data-centre / CDN / managed-service / managed-security / **online-marketplace** / search-engine / social-network providers) | **17 Jan 2025** | past | Art. 42(1) | `primary-fetched` for the date and basis; the **full enumerated provider list was reconstructed** from a nearby definitions passage plus one secondary source — corroborated, **not quoted end-to-end** |
| `it-dlgs-138-art-7` | general registration window, **recurring annually** | 1 Jan – 28 Feb | past (2025 cycle); recurring | Art. 7(1) | `primary-fetched` |
| `it-nis-acn-list-2025` | ACN compiles the essential/important list | end Mar 2025 | past | Art. 7 machinery | `secondary-corroborated` |
| `it-nis-acn-notify-2025` | ACN notifies each registrant of inclusion/exclusion | Apr 2025 (12–13 Apr per one source) | past | Art. 7 | `secondary-corroborated`; exact day **unverified** |
| `it-nis-governance-roster-2025` | governance-body roster / substitute point of contact | 31 Jul 2025 | past | Artt. 7, 23 | `secondary-corroborated`, **single source — unverified** |
| `it-nis-csirt-referent-2025` | CSIRT Italia referent designation | 20 Nov – 31 Dec 2025 | past | decree CSIRT provisions | `secondary-corroborated`, **single source — unverified** |
| `it-nis-incident-duty-live` | incident-notification obligation goes live | **mid-Jan 2026** (15 Jan per one source; "January 2026" per ACN) | past | Art. 25 | ACN page + secondary; exact day **unverified** |
| `it-nis-registry-update-2026` | annual registry data update window | 15 Apr – 31 May 2026 | past | Art. 7 | `secondary-corroborated` |
| `it-dlgs-138-art-30` | activity/service categorisation, first window | **from 1 May 2026** (through 30 Jun 2026 per one source) | past/closing | Art. 30 — verbatim: *"Ai fini di cui all'articolo 24, comma 1, dal 1° maggio..."* | `primary-fetched` for the **start** date; the 30 Jun end-date and the reference to *Determinazione ACN n. 155238* are **unverified** |
| `acn-det-379907-2025` | **baseline measures adoption** | **18 months from that entity's own notification of inclusion** — *not* a calendar date (see the banner above) | **rolling, per entity** | *Determinazione ACN n. 379907/2025*, **Art. 3(1)**, verbatim | **`primary-fetched`** — PDF fetched directly from `acn.gov.it` |
| `acn-det-379907-2025` | **basic significant-incident notification duty** | **9 months from that entity's own notification of inclusion** | rolling, per entity | same determinazione, **Art. 3(2)**, verbatim | **`primary-fetched`** |
| `acn-det-127434-baseline-2027` | baseline deadline for entities first listed **during calendar 2026** | **31 Jul 2027** | future | *Determinazione ACN n. 127434/2026*, Art. 1(1), verbatim | **`primary-fetched`** |
| `acn-det-127434-baseline-2027` | incident-notification duty for the **2026 cohort** | **runs from 1 Jan 2027** | future | same determinazione, Art. 1(2), verbatim | **`primary-fetched`** |

**Sanction for failure to register:** an administrative fine of up to **0.1% of
global annual turnover** — **secondary source, `unverified`**. **Confirm** the
exact article, and whether this is a separate, smaller penalty than the general
Art. 38 sanctions.

### `acn-det-379907-2025` — the baseline-measures determinazione, **verbatim**

- **instrument:** Determinazione del Direttore Generale dell'Agenzia per la
  cybersicurezza nazionale, adopted under **Art. 31(1)–(2)** and **Art. 42(1)(c)**
  of D.Lgs. 138/2024 — *authority determination*, subordinate to the decree
- **provision:** the determinazione as a whole; **Art. 3 is the operative
  deadline provision**, **Art. 9** its entry into force
- **text_form:** **`verbatim`** (all nine articles extracted from the primary PDF)
- **text (IT, verbatim) — Art. 3, "Termini per l'adozione delle specifiche di
  base":**

  > 1. Il termine per l'adozione delle misure di sicurezza di base di cui agli allegati 1 e 2 è fissato in diciotto mesi dalla ricezione, da parte del soggetto NIS della comunicazione di inserimento nell'elenco dei soggetti NIS.
  >
  > 2. Il termine per l'adempimento dell'obbligo di notifica degli incidenti significativi di base descritti negli allegati 3 e 4 è fissato in nove mesi dalla ricezione, da parte del soggetto NIS, della comunicazione di inserimento nell'elenco dei soggetti NIS.

- **text (IT, verbatim) — Art. 9, "Entrata in vigore e disposizioni transitorie":**

  > 1. La presente determinazione aggiorna e sostituisce la determinazione ACN n. 164179 del 14 aprile 2025.
  > 2. Per quanto non previsto dalla presente determinazione, si applicano le disposizioni del decreto NIS.
  > 3. La presente determinazione si applica a decorrere dal 15 gennaio 2026.

- **structure:** Art. 1 definitions and Art. 2 scope bind "soggetti essenziali"
  and "soggetti importanti" as defined by the decree, with **differentiated**
  annexes — **Allegato 1** baseline measures for *important* entities,
  **Allegato 2** for *essential*; **Allegato 3** and **Allegato 4** the
  corresponding significant-incident specifications. Arts. 4–6 add transitional
  and technical regimes for domain-name registries/registrars, former "operatori
  di servizi essenziali" (the pre-NIS2 category), and telecom operators.
- **what "misure di sicurezza di base" concretely requires (Art. 1(1)(j)):**
  "specifiche di base per gli obblighi di cui agli articoli 23 e 24 del decreto
  NIS, sviluppate in accordo al Framework nazionale [per la Cybersecurity e la
  Data Protection, ed. 2025] e organizzate in funzioni, categorie, sottocategorie
  e requisiti." **The measure-by-measure content lives in Annexes 1–4, which were
  NOT fetched** — they are separate documents on the ACN portal, referenced but
  not linked in the determinazione's own text. Secondary sources report 37
  measures / 87 requirements for important entities and 43 measures / 116
  requirements for essential entities; that count is **`secondary-corroborated`
  only** and is not confirmed against the primary annexes.
- **official_url:**
  https://www.acn.gov.it/portale/documents/d/guest/detacn_obblighi_2511-v3_signed
- **consulted:** the PDF fetched **directly** from `acn.gov.it` (no proxy) and
  text-extracted — **verification_grade:** `primary-fetched`
- **language_version:** Italian
- **verified:** 2026-07-31
- **legal_status:** `in force`, **applies from 15 January 2026**, superseding
  Determinazione ACN n. 164179 del 14 aprile 2025
- **identification caveat, preserved because it is an inference, not a
  self-declared fact:** **the fetched PDF never states "379907" or "19 dicembre
  2025" in its own body.** It was identified by matching its opening recital
  word-for-word against how the *later*, number-bearing determinazione describes
  "la propria Determinazione n. 379907 del 19 dicembre 2025 … che, ai sensi
  dell'articolo 42, comma 1, lettera c) … stabilisce le misure di sicurezza
  modalità e le specifiche di base per l'adempimento agli obblighi di cui agli
  articoli 23, 24, 25, 29 e 32 del decreto medesimo". **That cross-reference
  chain is the identification evidence.** It is strong; it is not the document
  declaring its own number.

### `acn-det-127434-baseline-2027` — the 2026-cohort follow-on, **verbatim**

- **instrument:** a later ACN determinazione (its own number is **not printed in
  the fetched body**; *sentito* the Tavolo on 9 April 2026; applies from
  **30 April 2026**) which explicitly references "la propria Determinazione
  n. 379907 del 19 dicembre 2025" — matching this corpus's existing description
  of Determinazione n. 127434/2026 — *authority determination*
- **provision:** Art. 1 — "Termini per l'adozione delle misure di sicurezza e per
  l'adempimento dell'obbligo di notifica degli incidenti significativi"
- **text_form:** **`verbatim`**
- **text (IT, verbatim):**

  > 1. Per i soggetti inseriti nell'elenco dei soggetti NIS nel corso dell'anno solare 2026 ai sensi dell'articolo 7, comma 3, lettera a), del decreto NIS, il termine per l'adozione delle misure di sicurezza, di cui agli allegati 1 e 2 della Determinazione ACN n. 379907 del 19 dicembre 2025, scade il **31 luglio 2027**.
  >
  > 2. Per i soggetti inseriti nell'elenco dei soggetti NIS nel corso dell'anno solare 2026 …, il termine per l'adempimento dell'obbligo di notifica degli incidenti significativi di base … decorre dal **1° gennaio 2027**.
  >
  > 3. Per i soggetti inseriti nell'elenco dei soggetti NIS nel corso dell'anno solare 2025, che permangono nell'elenco dei soggetti NIS 2026 …, rimangono fermi i termini di cui all'articolo 3 della Determinazione ACN n. 379907 del 19 dicembre 2025.

- **official_url:**
  https://www.acn.gov.it/portale/documents/d/guest/detacn_misuresicurezza-v4_post
- **consulted:** PDF fetched **directly** from `acn.gov.it`, text-extracted —
  **verification_grade:** `primary-fetched`
- **language_version:** Italian · **verified:** 2026-07-31 ·
  **legal_status:** `in force` from **30 April 2026**
- **notes:** paragraph 3 is the load-bearing one for the rolling-clock rule:
  2025-cohort entities remaining on the 2026 list **keep their original Art. 3
  terms — their own 18-months-from-notification clock — and do not get a new
  fixed date.** A fixed cohort date would have appeared here if one existed. It
  does not.

### `acn-registration-pages`

- **instrument:** ACN (Agenzia per la Cybersicurezza Nazionale) — *authority
  publication*
- **provision:** **not a legislative provision** — ACN's own published registration guidance pages, recorded for the process they describe
- **text_form:** `topic only` · **verification_grade:** `secondary-corroborated`
  (an official body's plain-language page, not primary legislative text — high
  authority, still not the law)
- **official_url:** https://www.acn.gov.it/portale/en/nis/registrazione ·
  https://www.acn.gov.it/portale/en/nis/la-normativa ·
  https://www.acn.gov.it/portale/en/w/normativa-nis-date-e-informazioni-utili-per-un-implementazione-efficace
- **verified:** 2026-07-31 · **legal_status:** `in force`

---

## Ingest requests (open, in priority order)

1. **The four Annexes to Determinazione n. 379907/2025** — the actual
   measure-by-measure and incident-specification lists. They are separate ACN
   portal documents, not linked from the determinazione's own text, and they are
   what an entity must actually *implement*. Highest practical value.
2. **The exact 2025 notification date(s).** Still `secondary-corroborated` ("Apr
   2025, 12–13 Apr per one source"), and the weakest link in the deadline chain
   — the determinazione text is primary.
3. **The remaining Directive entries** — Arts. 2(1), 3, 6(28), Annexes I and II
   are still mirror-sourced. They are present in the **retained full-text
   snapshot** and can be upgraded **without a new network fetch**.
4. **D.Lgs. 138/2024** — full paragraph text for Arts. 23, 24, 25 and 34, with a
   real PDF renderer rather than content-stream extraction. This matters most for
   Art. 25, where the Directive-side threshold is primary but the Italian
   wording is not.
5. **Recommendation 2003/361/EC Annex Arts. 3–6** — the autonomous / partner /
   linked-enterprise aggregation rules, where corporate-group structure bears on
   the size gate.
6. **Guidance on B2B-only platforms** under the "mercato online" definition (ACN
   FAQs, Commission guidance, case law). **None was found — that is not an
   answer.**
7. The Directive's own **entry-into-force article number**.
8. **Transposing acts of other Member States.** Only the Italian transposition
   is recorded here; every other Member State's obligations run through its own
   act, none of which this corpus holds.

## Neighbours

- `cra.md` — the other cybersecurity instrument; `cra-recital-12` routes
  SaaS/PaaS/IaaS **to NIS2**, and `cra-recital-13` explains how both regimes can
  bind the same organisation in different capacities.
- `../_schema.md` — the entry contract, including the amendment trap this page's
  size gate and the Art. 2(n) cross-reference both depend on.
- The scope anchors this page leans on — Directive 2005/29/EC Art. 2(a)
  ("consumer") and Art. 2(n) ("online marketplace"), and Recommendation
  2003/361/EC Annex Art. 2 (the size gate) — are quoted inline above but have no
  entry of their own in this corpus. So do GDPR Art. 33 breach notification (a
  **separate** duty from NIS2 incident reporting, with different triggers,
  recipients and clocks) and the ISO/IEC 27001 control vocabulary an Art. 21
  measures programme would be mapped through.
