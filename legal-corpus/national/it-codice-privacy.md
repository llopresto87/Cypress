# Codice Privacy — D.Lgs. 196/2003 (Italy)

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Entry contract: `../_schema.md`.

**Instrument kind:** `national statute` (the Italian Personal Data Protection
Code, as amended — notably by D.Lgs. 101/2018 to align it with the GDPR). It is
the **Italian transposing vehicle for ePrivacy Directive 2002/58/EC Art. 5(3)**
(`../eu/eprivacy-directive.md`).

---

### `it-codice-privacy-art-122`

- **instrument:** D.Lgs. 30 giugno 2003, n. 196 ("Codice in materia di
  protezione dei dati personali"), as amended — *national statute*
- **provision:** Art. 122 — "Informazioni raccolte nei riguardi dell'contraente o
  dell'utente" *(sic — the article's own official title, grammatical quirk
  included; do not silently "correct" it in a citation)*
- **text_form:** **verbatim** (complete, all three paragraphs)
- **text (IT, verbatim):**

  > 1. L'archiviazione delle informazioni nell'apparecchio terminale di un
  > contraente o di un utente o l'accesso a informazioni già archiviate sono
  > consentiti unicamente a condizione che il contraente o l'utente abbia espresso
  > il proprio consenso dopo essere stato informato con modalità semplificate. Ciò
  > non vieta l'eventuale archiviazione tecnica o l'accesso alle informazioni già
  > archiviate se finalizzati unicamente ad effettuare la trasmissione di una
  > comunicazione su una rete di comunicazione elettronica, o nella misura
  > strettamente necessaria al fornitore di un servizio della società
  > dell'informazione esplicitamente richiesto dal contraente o dall'utente a
  > erogare tale servizio. Ai fini della determinazione delle modalità
  > semplificate di cui al primo periodo il Garante tiene anche conto delle
  > proposte formulate dalle associazioni maggiormente rappresentative a livello
  > nazionale dei consumatori e delle categorie economiche coinvolte, anche allo
  > scopo di garantire l'utilizzo di metodologie che assicurino l'effettiva
  > consapevolezza del contraente o dell'utente.
  >
  > 2. Ai fini dell'espressione del consenso di cui al comma 1, possono essere
  > utilizzate specifiche configurazioni di programmi informatici o di dispositivi
  > che siano di facile e chiara utilizzabilità per il contraente o l'utente.
  >
  > 2-bis. Salvo quanto previsto dal comma 1, è vietato l'uso di una rete di
  > comunicazione elettronica per accedere a informazioni archiviate
  > nell'apparecchio terminale di un contraente o di un utente, per archiviare
  > informazioni o per monitorare le operazioni dell'utente.

- **official_url:**
  https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-06-30;196~art122!vig=
- **consulted:** **direct `curl` fetch against Normattiva's `uri-res/N2Ls`
  permalink resolver** with the `~art122!vig=` article suffix, returning clean
  consolidated HTML — **verification_grade:** `primary-fetched`. No proxy, no
  blockage.
- **language_version:** Italian, **consolidated text**. Normattiva's own header
  states **"Testo in vigore dal: 19-9-2018"** — the version as amended, with the
  most recent relevant amendment effective 19 September 2018 (the same day the
  GDPR-alignment rewrite by D.Lgs. 101/2018 took effect). **No later in-force
  marker was shown**, so this is current as of the verification date.
- **verified:** 2026-07-31
- **legal_status:** `in force`
- **transposes:** `eprivacy-dir-2002-58-art-5-3` (the **consolidated**, post-2009
  opt-in text — see the amendment trap on that page). **Divergence: not assessed
  in detail**, but the two align in substance on the consent standard, and this
  article's two exceptions (transmission-necessity, explicitly-requested-service
  necessity) mirror Art. 5(3)'s almost word for word.
- **notes — the exemption structure.** Consent is required for storage in, or
  access to, terminal-equipment information **unless** (a) it is strictly for
  transmitting a communication over an electronic-communications network, or (b)
  it is strictly necessary to provide an information-society service **explicitly
  requested by the user**. **Paragraph 2-bis separately prohibits** using an
  electronic communications network to access, store or monitor terminal
  information outside the paragraph-1 exceptions. The two exceptions are narrow
  and are read against the *user's own* request for the service: something that
  is neither necessary to transmit the communication nor explicitly requested by
  the user falls within neither, and needs a consent basis under paragraph 1 **if**
  it results in terminal storage or access. Whether any given behaviour produces
  terminal storage or access is a technical question, not one this entry answers.

---

## Recorded gaps

- Any **Garante guidance on "modalità semplificate"** under paragraph 1 — the
  article expressly contemplates it and none is recorded here. `not recorded`.

## Neighbours

- `../eu/eprivacy-directive.md` — **the EU provision this transposes**, and its
  amendment trap.
- `../case-law/index.md` — `cjeu-c-582-14-breyer` (IP address as personal data),
  `lg-muenchen-i-3-o-17493-20` (third-party asset loading), and the **verified
  absence** of any Garante decision on Google Fonts.
- `../eu/gdpr.md` — `gdpr-art-4-11`, `gdpr-art-7-1` (consent), `gdpr-art-6-1-f`
  (the separate IP-disclosure basis).
- `../_schema.md`
