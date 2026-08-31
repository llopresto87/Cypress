# Directive 2002/58/EC (ePrivacy), as amended — EU

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. AMENDMENT TRAP: the 2002 original and the text in force (as
> amended by Directive 2009/136/EC) state OPPOSITE rules (opt-out vs.
> opt-in) — both CELEX ids are recorded per entry; never cite the original
> alone as current. A directive alone does not bind persons — cite the
> national transposing act for a national obligation (see `transposed_by`).
> Entry contract: `../_schema.md`.

**Instrument kind:** `directive` — **binds Member States, not persons.** In
Italy the binding provision is the transposing one, `it-codice-privacy-art-122`
(`../national/it-codice-privacy.md`).

---

## ⚠ AMENDMENT TRAP — the original text states the WRONG rule

**The 2002 original and the text in force say opposite things.**

| Edition | CELEX | Standard |
|---|---|---|
| Original, 2002 | `32002L0058` | the user must "be offered the possibility to refuse" — **opt-out** |
| Consolidated, as amended by Dir. 2009/136/EC (applicable from 19 Dec 2009) | `02002L0058-20091219` | the user **"has given his or her consent"**, having been informed — **opt-in, prior consent** |

**Fetching CELEX `32002L0058` alone silently produces the superseded opt-out
rule** — which is exactly what "the cookie law" is *not*. Both identifiers are
recorded here so the next reader cannot fall in.

---

### `eprivacy-dir-2002-58-art-5-3`

- **instrument:** Directive 2002/58/EC of the European Parliament and of the
  Council of 12 July 2002 concerning the processing of personal data and the
  protection of privacy in the electronic communications sector ("Directive on
  privacy and electronic communications"), **as amended by Directive
  2009/136/EC** — *directive, consolidated version*
- **provision:** Article 5(3) — storage of, or access to, information already
  stored in the terminal equipment of a subscriber or user
- **text_form:** **verbatim** (the current consolidated text; the superseded
  2002 wording is described, not reproduced, in the trap box above)
- **text (EN, verbatim, CURRENT consolidated text, in force):** "Member States
  shall ensure that the storing of information, or the gaining of access to
  information already stored, in the terminal equipment of a subscriber or user
  is only allowed on condition that the subscriber or user concerned **has given
  his or her consent**, having been provided with clear and comprehensive
  information, in accordance with Directive 95/46/EC, inter alia, about the
  purposes of the processing. This shall not prevent any technical storage or
  access for the sole purpose of carrying out the transmission of a
  communication over an electronic communications network, or as strictly
  necessary in order for the provider of an information society service
  explicitly requested by the subscriber or user to provide the service."
- **text (IT, verbatim, CURRENT consolidated text, in force):** "Gli Stati
  membri assicurano che l'archiviazione di informazioni oppure l'accesso a
  informazioni già archiviate nell'apparecchiatura terminale di un abbonato o di
  un utente sia consentito unicamente a condizione che l'abbonato o l'utente in
  questione **abbia espresso preliminarmente il proprio consenso**, dopo essere
  stato informato in modo chiaro e completo, a norma della direttiva 95/46/CE,
  tra l'altro sugli scopi del trattamento. Ciò non vieta l'eventuale
  archiviazione tecnica o l'accesso al solo fine di effettuare la trasmissione
  di una comunicazione su una rete di comunicazione elettronica, o nella misura
  strettamente necessaria al fornitore di un servizio della società
  dell'informazione esplicitamente richiesto dall'abbonato o dall'utente a
  erogare tale servizio."
- **official_url:** consolidated —
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02002L0058-20091219
  · original (superseded, do not cite as current) —
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32002L0058
- **consulted:** direct `curl` through the `r.jina.ai` read-only proxy against
  **both** CELEX ids, in EN and IT — **verification_grade:** `proxy-sourced`.
  **A proxy is not the official source.**
- **language_version:** English and Italian, **consolidated text** as amended by
  Directive 2009/136/EC (applicable from 19 December 2009)
- **verified:** 2026-07-31
- **legal_status:** `in force` (as amended)
- **transposed_by:** `it-codice-privacy-art-122` (D.Lgs. 196/2003 Art. 122, as
  amended — `primary-fetched` from Normattiva in the same pass) ·
  **transposition_status:** adopted · **divergence:** **not assessed in detail**,
  but the Italian wording ("il contraente o l'utente abbia espresso il proprio
  consenso dopo essere stato informato con modalità semplificate") tracks the
  current post-2009 EU consent standard closely, and Art. 122's two exceptions
  (transmission-necessity, explicitly-requested-service-necessity) mirror
  Art. 5(3)'s almost word for word.
- **notes:** **A directive alone is not citable for an Italian obligation.**
  For anything a Garante would enforce, cite `it-codice-privacy-art-122`; cite
  this entry for the EU-level standard and its structure.

---

## Scope of Art. 5(3) — what triggers it

**What Art. 5(3) is triggered by:** *storing* information in, or *gaining
access to* information already stored in, terminal equipment. Loading a font or
a script from a third-party CDN is, by itself, **not** within the article
**unless** the load sets a cookie, writes to local/session storage, or otherwise
persists or reads something on the device as a side effect.

Two limits on any such analysis, each of which is routinely mistaken for the
other:

1. **Cookies are not the whole of terminal storage.** Art. 5(3) also reaches
   `localStorage`, IndexedDB, ETags used as identifiers, and cache
   fingerprinting. An observation that no `Set-Cookie` header is returned says
   nothing about those mechanisms.
2. **The IP-disclosure question is separate.** Whether disclosing a user's IP
   address to a third-party origin by making the request at all needs a basis
   under Art. 6(1)(f) is a **different legal question** — see
   `cjeu-c-582-14-breyer` (IP addresses as personal data) and
   `lg-muenchen-i-3-o-17493-20` (a German court rejecting the
   legitimate-interest defence for *dynamic* Google Fonts embedding). A finding
   on terminal storage does not resolve it.

A point-in-time HTTP probe of a third-party origin is an observation with a
date, not a property of the service: a third party can begin setting a cookie at
any time without notice. Re-observe before relying on one; never promote it to a
settled fact.

## Not transcribed

- The **original 2002 wording of Art. 5(3) verbatim**, if a history argument is
  ever needed — described here, not reproduced.

## Neighbours

- `../national/it-codice-privacy.md` — `it-codice-privacy-art-122`, the
  provision that actually binds in Italy. **Cite that, not this, for an Italian
  obligation.**
- `../case-law/` — `cjeu-c-582-14-breyer`, `lg-muenchen-i-3-o-17493-20`, and the
  **verified absence** of any Garante decision on Google Fonts.
- `eu-scope-definitions.md` — the sibling amendment trap on Directive
  2005/29/EC Art. 2(n).
- `../_schema.md` — "The amendment trap".
