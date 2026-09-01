# Workers' Statute — Legge 300/1970 Art. 4 (Italy)

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Entry contract: `../_schema.md`.

**Instrument kind:** `national statute` (the "Statuto dei lavoratori" — the
Italian employment-relations statute).

---

### `it-workers-statute-art-4`

- **instrument:** Legge 20 maggio 1970, n. 300 (the Workers' Statute, "Statuto
  dei lavoratori") — *national statute*
- **provision:** Art. 4 — "Impianti audiovisivi e altri strumenti di controllo"
- **text_form:** **verbatim** (complete, all three commi)
- **text (IT, verbatim — consolidated):**

  > 1. Gli impianti audiovisivi e gli altri strumenti dai quali derivi anche la
  > possibilità di controllo a distanza dell'attività dei lavoratori possono
  > essere impiegati esclusivamente per esigenze organizzative e produttive, per
  > la sicurezza del lavoro e per la tutela del patrimonio aziendale e possono
  > essere installati previo accordo collettivo stipulato dalla rappresentanza
  > sindacale unitaria o dalle rappresentanze sindacali aziendali. In
  > alternativa, nel caso di imprese con unità produttive ubicate in diverse
  > province della stessa regione ovvero in più regioni, tale accordo può essere
  > stipulato dalle associazioni sindacali comparativamente più rappresentative
  > sul piano nazionale. ((In mancanza di accordo, gli impianti e gli strumenti
  > di cui al primo periodo possono essere installati previa autorizzazione
  > delle sede territoriale dell'Ispettorato nazionale del lavoro o, in
  > alternativa, nel caso di imprese con unità produttive dislocate negli ambiti
  > di competenza di più sedi territoriali, della sede centrale dell'Ispettorato
  > nazionale del lavoro. I provvedimenti di cui al terzo periodo sono
  > definitivi.))
  >
  > 2. La disposizione di cui al comma 1 non si applica agli strumenti utilizzati
  > dal lavoratore per rendere la prestazione lavorativa e agli strumenti di
  > registrazione degli accessi e delle presenze.
  >
  > 3. Le informazioni raccolte ai sensi dei commi 1 e 2 sono utilizzabili a
  > tutti i fini connessi al rapporto di lavoro a condizione che sia data al
  > lavoratore adeguata informazione delle modalità d'uso degli strumenti e di
  > effettuazione dei controlli e nel rispetto di quanto disposto dal decreto
  > legislativo 30 giugno 2003, n. 196.

- **official_url:**
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1970-05-20;300~art4!vig=
- **consulted:** **direct `curl` fetch against Normattiva's `uri-res/N2Ls`
  permalink resolver** with the `~art4!vig=` article suffix, returning clean
  consolidated HTML — **verification_grade:** `primary-fetched`. No proxy, no
  blockage (Normattiva is directly reachable).
- **language_version:** Italian, **consolidated text**. Normattiva's own header
  states **"Testo in vigore dal: 8-10-2016"**. **The fetched text includes the
  post-2015 amendments**: the current three-comma structure is the rewrite
  introduced by **D.Lgs. 14 settembre 2015, n. 151** (the "Jobs Act"
  modernisation), and the double-parenthesised third period of comma 1 — the
  **Ispettorato nazionale del lavoro authorisation** route — is marked by
  Normattiva's `((…))` convention as amendment-added text. **The specific act
  that produced the 8-10-2016 in-force marker is `not recorded`**: Normattiva's
  amendment list for the article is JS-loaded and was not present in the
  fetched rendering (the detail endpoint returns HTTP 404 without a session
  cookie). The original 1970 wording of Art. 4 is **not separately recorded**
  — the fetched page carries only the consolidated text.
- **verified:** 2026-08-05
- **legal_status:** `in force`
- **notes — the structure, which is what any worker-surveillance finding runs
  through.** Comma 1: remote-surveillance-capable equipment may be **used only
  for** organisational/production needs, work safety, and protection of company
  assets — and may be **installed only under a collective agreement** (RSU/RSA,
  or, for multi-province/multi-region operations, the most-representative
  national unions), **or, failing agreement, with prior authorisation of the
  local Labour Inspectorate** (INL) — the amendment-added third period. Comma 2:
  the **carve-out for work tools** — equipment the worker uses to perform the
  job, and access/attendance registration devices, fall outside comma 1. Comma
  3: collected information may be used for all employment-related purposes
  **only if** the worker has been given **adequate notice of how the tools are
  used and how the controls are carried out** — the notice obligation — and
  **in compliance with D.Lgs. 196/2003** (the Codice Privacy, GDPR-aligned; see
  `it-codice-privacy.md`). **Sharp edge:** the work-tool carve-out in comma 2
  removes the collective-agreement/authorisation gate for work-issued tools, but
  **comma 3's information duty still applies** to them — the notice obligation
  operates on both commi 1 and 2, and GDPR Art. 13 (`gdpr-art-13`) imposes the
  parallel information duty on the data controller. **GDPR interplay:**
  worker-data processing under this article typically rests on `gdpr-art-9`,
  Art. 9(2)(b) (special categories in employment law, where involved) and
  `gdpr-art-6-1-b`/`6-1-f`; the GDPR does **not** displace Art. 4 L. 300/1970 —
  the two regimes run together, and this article's consent-free,
  collective-negotiation model is the Italian answer the GDPR's Art. 88
  (employment context) contemplates.

---

## Recorded gaps

- **The 8-10-2016 amending act identification** — Normattiva's JS-loaded
  amendment list for Art. 4; the fetched rendering does not carry it. A
  browser-rendering pass or Normattiva's Akoma-Ntoso export would close it.
- **The original 1970 wording** of Art. 4 — not in the consolidated rendering;
  only the in-force text is recorded here.

## Neighbours

- `../eu/gdpr.md` — `gdpr-art-9` (special-category prohibition and its
  employment-law derogation), `gdpr-art-13` (the parallel information duty),
  `gdpr-art-6-1-f`/`6-1-b` (lawful basis).
- `it-codice-privacy.md` — the D.Lgs. 196/2003 compliance channel comma 3
  points at.
- `../case-law/index.md` — Garante enforcement on workplace monitoring, when ingested.
- `../_schema.md`
