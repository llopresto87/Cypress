# Accounting & tax retention duties (Italy)

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Entry contract: `../_schema.md`.

**Art. 2220 c.c. · Art. 39 DPR 633/72 · Art. 22 DPR 600/73**

**Instrument kind:** `national statute` (three distinct Italian instruments).
They share a page because **they must be read together** — separating them is
how the imprecise single "ten-year Italian accounting duty" arises. Each has its
own entry id, its own status and its own verification grade.

**These are the provisions `gdpr-art-17-3-b` points at.** The erasure exemption
is only as wide as the obligation these articles actually impose.

---

### `it-cc-art-2220`

- **instrument:** Codice Civile (R.D. 16 marzo 1942, n. 262), Article 2220 —
  *national statute*
- **provision:** Art. 2220 c.c. — "Conservazione delle scritture contabili"
- **text_form:** `normalized summary`
- **text:** Accounting records must be kept for **ten years from the date of the
  last entry**; invoices, and correspondence sent and received (letters,
  telegrams), must likewise be kept for ten years from their date. The records
  may be kept as images provided they are legible and faithful to the original.
- **official_url:** https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.progressivo=0&art.idArticolo=2220&art.versione=2&art.codiceRedazionale=042U0262&art.dataPubblicazioneGazzetta=1942-04-04&art.idGruppo=281&art.idSottoArticolo1=10&art.idSottoArticolo=1&art.flagTipoArticolo=2
  (Gazzetta Ufficiale — authoritative)
- **consulted:** the Gazzetta Ufficiale article page above, corroborated by
  Brocardi.it, La Legge per Tutti and misterlex.it (consistent) —
  **verification_grade:** `primary-fetched`
- **language_version:** Italian, current consolidated version
- **verified:** 2026-07-31
- **legal_status:** `in force`
- **notes:** The best-sourced entry of the three. This is the ten-year figure —
  but see `it-dpr-600-1973-art-22`: ten years is **not an absolute ceiling**.

### `it-dpr-633-1972-art-39`

- **instrument:** D.P.R. 26 ottobre 1972, n. 633 (VAT decree), Article 39 —
  *national statute*
- **provision:** Art. 39 DPR 633/72 — "Tenuta e conservazione dei registri e dei
  documenti"
- **text_form:** **verbatim**
- **text (IT, verbatim, the operative retention clause):** "I registri, i
  bollettari, gli schedari e i tabulati, nonché le fatture, le bollette doganali
  e gli altri documenti previsti dal presente decreto devono essere conservati **a
  norma dell'articolo 22 del decreto del Presidente della Repubblica 29 settembre
  1973, n. 600**. Le fatture elettroniche sono conservate in modalità
  elettronica… Le fatture create in formato elettronico e quelle cartacee possono
  essere conservate elettronicamente. Il luogo di conservazione elettronica delle
  stesse… può essere situato in un altro Stato, a condizione che con lo stesso
  esista uno strumento giuridico che disciplini la reciproca assistenza. Il
  soggetto passivo stabilito nel territorio dello Stato assicura, per finalità di
  controllo, l'accesso automatizzato all'archivio e che tutti i documenti ed i
  dati in esso contenuti… siano stampabili e trasferibili su altro supporto
  informatico."
- **also present:** a later-added clause imposing a specific **ten-year**
  retention duty on VAT-facilitating **electronic interface operators**
  (marketplaces and platforms) in respect of non-taxable end-consumer
  transactions. Whether that clause reaches a given operator is a scope question
  this entry does not answer.
- **official_url:**
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art39!vig=
- **consulted:** **direct `curl` fetch against Normattiva's `uri-res/N2Ls`
  permalink resolver** with the `~art39!vig=` article suffix —
  **verification_grade:** `primary-fetched`. No proxy, no blockage.
- **language_version:** Italian, **consolidated text**. Normattiva's header
  states **"Testo in vigore dal: 30-6-2021 al: 31-12-2026"** — note the
  **forward-looking end date on the in-force marker itself**; re-check this entry
  closer to end-2026.
- **verified:** 2026-07-31
- **legal_status:** `in force` (for the consolidation window stated above)
- **notes:** **Art. 39 does not itself state the ten-year figure.** It
  cross-refers to **Art. 22 DPR 600/73** as the operative duration provision —
  which is the article that makes the period open-ended. **Precision:** citing
  "DPR 633/72" generically is wrong; the operative provision for conservation is
  **Article 39**. Cite the article, not the decree.

### `it-dpr-600-1973-art-22`

- **instrument:** D.P.R. 29 settembre 1973, n. 600 (income-tax assessment
  decree), Article 22 — *national statute*
- **provision:** Art. 22 DPR 600/73 — "Tenuta e conservazione delle scritture
  contabili"
- **text_form:** **verbatim**
- **text (IT, verbatim):** "Le scritture contabili obbligatorie ai sensi del
  presente decreto, di altre leggi tributarie, del codice civile o di leggi
  speciali devono essere conservate **fino a quando non siano definiti gli
  accertamenti relativi al corrispondente periodo d'imposta anche oltre il termine
  stabilito dall'articolo 2220 del codice civile** o da altre leggi tributarie,
  salvo il disposto dell'articolo 2457 del detto codice. Gli eventuali supporti
  meccanografici, elettronici e similari devono essere conservati fino a quando i
  dati contabili in essi contenuti non siano stati stampati sui libri e registri
  previsti dalle vigenti disposizioni di legge. L'autorità adita in sede
  contenziosa può limitare l'obbligo di conservazione alle scritture rilevanti per
  la risoluzione della controversia in corso. Fino allo stesso termine … devono
  essere conservati ordinatamente, per ciascun affare, gli originali delle
  lettere, dei telegrammi e delle fatture ricevuti e le copie delle lettere e dei
  telegrammi spediti e delle fatture emesse."
- **official_url:**
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art22!vig=
- **consulted:** **direct `curl` fetch against Normattiva's permalink resolver**
  (`~art22!vig=`) — **verification_grade:** `primary-fetched`
- **language_version:** Italian, **consolidated text**. Normattiva's header
  states **"Testo in vigore dal: 25-10-2001"**, with **no end date** — i.e. the
  settled current consolidation.
- **verified:** 2026-07-31
- **legal_status:** `in force`
- **notes:** **This is the primary confirmation of the "ten years is a floor,
  not a cap" reading**, standing on the statute rather than on commentary. The
  wording is explicit: records must be kept **"anche oltre"** — *even beyond* —
  the Art. 2220 civil-code term, while assessments for the relevant period remain
  open. The duty is therefore **tied to assessment finality, not to a fixed
  clock**. The third sentence also carries a counterweight worth knowing: **a
  court in litigation may narrow the conservation obligation** to the records
  relevant to the dispute.

---

## The correction this page exists to carry

**"The ten-year Italian accounting duty" is a simplification, and in one
direction it is unsafe.** Three things are true at once:

1. `it-cc-art-2220` sets **ten years** for accounting records, invoices and
   business correspondence.
2. `it-dpr-633-1972-art-39` imposes the parallel VAT conservation duty on
   invoices and registers.
3. `it-dpr-600-1973-art-22` **extends** the period while a tax assessment or
   dispute for the relevant year remains open.

So ten years is a **floor with an open-ended extension**, not a hard cap. A
retention design that treats it as a fixed ten-year window will under-retain
where a dispute is pending; a deliverable that presents the three provisions as
one interchangeable rule is imprecise in a way an auditor will notice.

**And the other direction matters more for `gdpr-art-17-3-b`:** these
provisions cover the *accounting and tax record*. They do not, on their face,
authorise retaining every personal-data field attached to a commercial
transaction. Over-claiming beyond the record content is not exempted.

## Sourcing notes

**The whole three-provision chain (Art. 2220 c.c. → Art. 39 → Art. 22) is
primary end to end.**

**A durable retrieval fact, recorded so the wrong assumption is not repeated:**
Normattiva is **not JS-gated**. A direct `curl` against
`normattiva.it/uri-res/N2Ls?urn:nir:...` with the `~art<N>!vig=` suffix returns
clean consolidated HTML **with an explicit in-force-date header**. Do not record
Normattiva as blocked without a fresh attempt.

**One thing to diarise:** Art. 39's Normattiva in-force marker reads
"dal 30-6-2021 **al: 31-12-2026**". **Re-verify that entry after that date.**

## Neighbours

- `../eu/gdpr.md` — `gdpr-art-17-3-b` (the exemption these provisions ground),
  `gdpr-art-5-1-e` (storage limitation, the countervailing principle).
- `../_schema.md`
