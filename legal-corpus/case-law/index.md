# Case law & regulator decisions

> Project-agnostic citation notes, folded into the seed by the harvest
> protocol. Cross-jurisdictional judicial and regulatory-authority decisions,
> one entry per case/decision. A recorded VERIFIED ABSENCE of a decision (a
> search that did not find one to exist) is itself a valid, citable entry —
> see the rules on this in `../_schema.md`. Entry contract: `../_schema.md`.

**Instrument kind:** `case-law` / `regulator-decision`. Grouped on one page
because these entries are only useful when compared — a national judgment, the
supranational principle behind it, and the *absence* of an equivalent decision
in a third jurisdiction are one argument, not three. Each has its own citable
id.

**For this kind, one field outranks the rest: whether the primary text was
actually fetched.** A judgment citation is the highest-risk item in a compliance
document after a number. **Updated 2026-07-31 (gap-fill pass):** the blanket
statement that "not one entry on this page rests on a fetched primary court
record" is **no longer true** — Breyer's operative ruling, the LG München Tenor,
the Latombe docket record and the Garante DPIA list were all retrieved. Grade
per entry; the page no longer has one answer.

---

### `cjeu-c-582-14-breyer`

- **instrument:** Court of Justice of the European Union — *case-law*
- **court:** CJEU (Second Chamber) · **docket:** C-582/14, *Patrick Breyer v
  Bundesrepublik Deutschland* · **decision_date:** 19 October 2016
- **provision:** the judgment's **operative part** ("hereby rules")
- **text_form:** **verbatim** (the Court's own operative ruling, EN)
- **text (EN, verbatim):**

  > On those grounds, the Court (Second Chamber) hereby rules:
  >
  > 1. Article 2(a) of Directive 95/46/EC … must be interpreted as meaning that a dynamic IP address registered by an online media services provider when a person accesses a website that the provider makes accessible to the public constitutes personal data within the meaning of that provision, in relation to that provider, where the latter has the legal means which enable it to identify the data subject with additional data which the internet service provider has about that person.
  >
  > 2. Article 7(f) of Directive 95/46 must be interpreted as precluding the legislation of a Member State, pursuant to which an online media services provider may collect and use personal data relating to a user of those services, without his consent, only in so far as that the collection and use of that data are necessary to facilitate and charge for the specific use of those services by that user, even though the objective aiming to ensure the general operability of those services may justify the use of those data after a consultation period of those websites.

- **official_url:**
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62014CJ0582
- **consulted:** direct `curl` through the `r.jina.ai` proxy against the EUR-Lex
  judgment page — **verification_grade:** `proxy-sourced`. A **material upgrade**
  from the previous `secondary-corroborated` grade (four commentary sources, the
  judgment itself unfetched), **but a proxy is still not the official source.**
- **language_version:** English (EUR-Lex translation; the language of the case
  was German)
- **verified:** 2026-07-31
- **legal_status:** `in force` (a standing CJEU precedent; decided under
  Directive 95/46/EC, applied to GDPR-era reasoning by later practice)
- **notes:** The operative ruling matches the corpus's previous normalized
  summary closely — **this is a provenance upgrade, not a substantive
  correction.** The judgment predates the GDPR and was decided under the 1995
  Directive; a deliverable should say so rather than presenting it as a GDPR case.

### `gc-latombe-2025-judgment`

- **instrument:** General Court of the European Union — *case-law*
- **court:** General Court (Tenth Chamber, Extended Composition) ·
  **docket:** **T-553/23**, *Latombe v Commission* · **decision_date:**
  3 September 2025
- **provision:** dismissal of the annulment action against the EU–US DPF
  adequacy decision
- **text_form:** `topic only` (docket identification and outcome; the judgment's
  own reasoning text was **not** fetched)
- **text:** The General Court dismissed MEP Philippe Latombe's action for
  annulment of Commission Implementing Decision (EU) 2023/1795, finding the Data
  Protection Review Court sufficiently independent, US bulk-collection
  limitations adequate, and security and automated-decision protections
  substantially equivalent.
- **official_url:**
  https://infocuria.curia.europa.eu/tabs/affair?lang=EN&searchTerm=%22C-703%2F25%20P%22&publishedId=T-553%2F23
- **consulted:** the InfoCuria case record's "Related case(s)" field, fetched by
  `curl` through the `r.jina.ai` proxy (direct `curia.europa.eu` returned HTTP
  403, confirming the standing blockage). Independently corroborated by a
  University of Copenhagen research-portal citation and a StreamLex case summary,
  both naming T-553/23 for the same 3 September 2025 judgment —
  **verification_grade:** `proxy-sourced` for the docket
- **language_version:** English (InfoCuria interface; the case's own language of
  procedure is French)
- **verified:** 2026-07-31
- **legal_status:** `in force — under appeal` (see
  `cjeu-c-703-25-p-latombe-appeal`)
- **notes:** **The docket was the single missing field that made this entry
  non-citable as a judgment reference. It is now supplied.** The full citable
  form is: *General Court (Tenth Chamber, Extended Composition), judgment of
  3 September 2025, Case **T-553/23**, Latombe v Commission*. The judgment's own
  **reasoning text is still not fetched** — cite the outcome and the docket, not
  the Court's words. The adequacy decision's own status lives in
  `../eu/eu-us-dpf-adequacy.md`.

### `cjeu-c-703-25-p-latombe-appeal`

- **instrument:** Court of Justice of the European Union — *case-law (pending)*
- **court:** Court of Justice · **docket:** **C-703/25 P**, *Latombe v
  Commission* · **filed:** 31 October 2025
- **provision:** appeal against `gc-latombe-2025-judgment` (Case T-553/23)
- **text_form:** `topic only` (procedural and docket facts, not a holding)
- **text:** InfoCuria's case record confirms: procedure type "Actions for
  annulment" / "Appeals"; subject matter "Principles of Union law" / "Protection
  of personal data"; application lodged 31 October 2025; language of the case
  French; appellant Philippe Latombe. The record lists one case-law document —
  **an Order of 04/06/2026, ECLI:EU:C:2026:465** — and one analysis document,
  "Application (OJ), 22/12/2025" (CELEX 62025CN0703). **The displayed status
  remains "Pending."**
- **official_url:**
  https://infocuria.curia.europa.eu/tabs/affair?lang=EN&searchTerm=%22C-703%2F25+P%22&publishedId=C-703%2F25+P
- **consulted:** direct `curl` through the `r.jina.ai` proxy against the
  InfoCuria case page — **verification_grade:** `proxy-sourced`. A **material
  upgrade** from the previous `secondary-corroborated` grade (search-engine
  synthesis): InfoCuria is the Court's own case-management database. **The docket
  number C-703/25 P is now confirmed on the Court's own record** and no longer
  carries the "unconfirmed, from synthesis" caveat.
- **language_version:** English (InfoCuria interface; language of the case French)
- **verified:** 2026-07-31
- **legal_status:** `pending`

> #### ⚠ The 4 June 2026 Order — a new development whose content is UNCONFIRMED
>
> An Order was issued **4 June 2026**, **ECLI:EU:C:2026:465**. This is a genuine,
> recent, previously-unrecorded development that postdates every other source in
> this corpus on the DPF question. **Its content and legal effect could not be
> retrieved.**
>
> - EUR-Lex returned "the requested document does not exist" for CELEX
>   `62025CO0703` and, on a second targeted attempt, for the variants
>   `62025CO0703(01)`, `62025CJ0703` and `62025CB0703` — through the **same proxy
>   route that works for everything else**. Likely not yet indexed, or indexed
>   under a different number.
> - **Do not infer its effect in either direction.** Orders that do **not** close
>   a case are common — time limits, interventions, joinder, expedited-procedure
>   requests. Which kind this is **is not recorded**.
> - **Do not let "Pending" plus "an Order exists" collapse into either "the
>   appeal was dismissed" or "nothing happened."** Both are fabrications on the
>   evidence obtained. **The only honest statement is:** an order was issued
>   4 June 2026 (ECLI:EU:C:2026:465); its content and effect are not confirmed;
>   the case remained open on the Court's own record as of 2026-07-31.
> - Training-data intuition will suggest that a docket with an Order against it
>   has been resolved. **InfoCuria's own status field says otherwise.**
> - **This is the highest-value open ingest request in the corpus.** Retry via
>   EUR-Lex's own search interface or InfoCuria's document-download link — **not**
>   a guessed CELEX id, which has now failed four times.

- **notes:** A pending appeal against an adequacy decision is the kind of entry
  that goes stale fastest — this is the single most important thing on this page
  to re-verify before reuse. **A hearing date is `not recorded`** — none was
  found in this pass, and commentary as of "May 2026" still reported none
  announced.

### `garante-elenco-dpia-2018` — the Italian national DPIA list

- **instrument:** Garante per la protezione dei dati personali — Provvedimento
  n. 467 dell'11 ottobre 2018, "Elenco delle tipologie di trattamenti soggetti al
  meccanismo di coerenza da sottoporre a valutazione d'impatto", adopted under
  **Art. 35(4) GDPR** (`gdpr-art-35-4`) — *regulator decision*
- **authority:** Garante (IT) · **docket:** doc-web **9058979** (provvedimento) /
  doc-web **9059358** (Allegato 1, the list) · **decision_date:** 11 October 2018
  · **published:** Gazzetta Ufficiale n. 269, 19 November 2018
- **provision:** Allegato 1 — the twelve types of processing subject to a
  mandatory DPIA
- **text_form:** **normalized summary** — an abbreviated English rendering of
  each item's operative subject, **not the Italian original's words; do not
  quote it**. The complete Italian wording was fetched but is not transcribed
  here; cite this entry by id and substance only.
- **text (EN, abbreviated — operative subject of each of the twelve items):**
  1. large-scale evaluative or **scoring** processing, and **profiling** or
     predictive activity (including online or via apps) on professional
     performance, economic situation, health, preferences, reliability,
     behaviour, location or movements;
  2. **automated decisions** producing legal effects or similarly significant
     effects, including decisions preventing exercise of a right or continued
     performance of a contract;
  3. **systematic use of data for observation, monitoring or control** of data
     subjects, including collection over networks, online or via apps, and the
     processing of **unique identifiers** identifying users of information-society
     services with respect to usage habits and viewing data over prolonged
     periods — expressly including **metadata processing** carried out "**not
     only for profiling, but more generally for organisational reasons, budget
     forecasting, technological upgrade, network improvement, anti-fraud,
     anti-spam, security etc.**";
  4. large-scale processing of **extremely personal** data (family/private life,
     electronic-communications data, location, financial data);
  5. workplace processing via technological systems permitting **remote
     monitoring of employees** (including CCTV and geolocation);
  6. non-occasional processing of data on **vulnerable subjects** (minors,
     disabled, elderly, mentally ill, patients, asylum seekers);
  7. processing using **innovative technologies** (IoT, AI systems, voice
     assistants with voice/text scanning, wearables, proximity/Wi-Fi tracking)
     whenever at least one further WP 248 rev.01 criterion also applies;
  8. large-scale **exchange of data between different controllers** by electronic
     means;
  9. processing by **interconnection, combination or matching** of information,
     including cross-referencing digital-goods consumption with payment data;
  10. Art. 9 special-category or Art. 10 criminal-conviction data
      **interconnected with other data collected for different purposes**;
  11. systematic processing of **biometric** data;
  12. systematic processing of **genetic** data.
- **official_url:**
  https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9058979
  (provvedimento) ·
  https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9059358
  (Allegato 1)
- **consulted:** direct `curl` fetch of the Allegato 1 PDF from
  `garanteprivacy.it`'s own document store, text-extracted —
  **verification_grade:** `primary-fetched`. **No proxy, no CAPTCHA, no WAF
  block** — the Garante's docweb pages and document store are directly reachable.
- **language_version:** Italian
- **verified:** 2026-07-31 · **legal_status:** `in force`
- **notes — item 3 is broader than a first read suggests.** Its second sentence
  reaches metadata processed for organisational, budget-forecasting,
  technological-upgrade, network-improvement, anti-fraud, anti-spam and
  **security** purposes — not only metadata processed for profiling. A reading
  that stops at "profiling" understates the item's reach.
- **the list is explicitly non-exhaustive.** The provvedimento states it is
  "riferito esclusivamente a tipologie di trattamento soggette al meccanismo di
  coerenza", and the general WP 248 rev.01 nine-criteria test (two or more
  criteria met ⇒ high risk) remains independently applicable. **"Not on this
  list" is never by itself a complete DPIA-applicability answer.**

### `lg-muenchen-i-3-o-17493-20`

- **instrument:** Landgericht München I (German first-instance civil court) —
  *case-law*
- **court:** LG München I · **docket:** 3 O 17493/20 · **decision_date:**
  20 January 2022
- **provision:** the judgment's Tenor and holding on dynamic Google Fonts
  embedding
- **text_form:** `normalized summary` **with quoted fragments** — the source is
  an official state-government legal database reproducing the Tenor and specific
  reasoning passages, **not** the court's own certified full-text copy. Treat the
  German fragment below as a genuine quotation *via that republication*; treat
  the surrounding summary as normalized.
- **text — Tenor:** the court ordered the defendant to (1) cease disclosing the
  claimant's IP address to Google via Google Fonts, on pain of a fine of up to
  €250,000 or imprisonment of up to six months; (2) disclose whether and what
  personal data concerning the claimant had been processed; (3) pay €100 in
  damages plus interest at five percentage points above base rate from
  28 January 2021.
- **text — reasoning, quoted (German):** "Google Fonts kann durch die Beklagte
  auch genutzt werden, ohne dass beim Aufruf der Webseite eine Verbindung zu
  einem Google-Server hergestellt wird" — i.e. the court **rejected the
  Art. 6(1)(f) legitimate-interest defence precisely because a non-infringing,
  locally-hosted alternative to the dynamic live-connect embedding existed**, so
  disclosing the visitor's IP address to Google was not "necessary". The court
  also held a dynamic IP address is personal data because the operator has the
  abstract legal means to identify the individual behind it, and set damages at
  €100 reflecting a "not insignificant" (*erheblich*) interference given repeated
  transmission to the US and inadequate US data-protection standards — **a 2022
  judgment, predating the 2023 DPF adequacy decision** — with a deterrent
  function under Art. 82.
- **official_url:**
  https://www.gesetze-bayern.de/Content/Document/Y-300-Z-BECKRS-B-2022-N-612?hl=true
- **consulted:** `gesetze-bayern.de`, the **official legal-information portal of
  the Free State of Bavaria** (a Land government service, comparable in kind to
  Normattiva for Italian legislation), which republishes the judgment under its
  BeckRS citation — **verification_grade:** `primary-fetched` for the Tenor and
  the quoted reasoning fragment, **with this caveat stated in prose because
  `../_schema.md` requires it for case law: this is a state legal database's
  record of the decision, not a download of the court's own certified original.**
  It is one tier above the four commercial-commentary sources previously relied
  on; it is **not** identical to obtaining the court's file copy.
- **language_version:** German (original judgment language, as excerpted by the
  Bavarian portal)
- **verified:** 2026-07-31
- **legal_status:** `in force` as a first-instance decision
- **notes:** **`rewis.io` is now confirmed blocked by a Cloudflare bot-challenge
  (CAPTCHA), not a simple HTTP 403 — and the block survives the `r.jina.ai`
  proxy**, which fetched Cloudflare's challenge page rather than the judgment.
  **Do not retry rewis.io without a browser-rendering tool.** Use
  `gesetze-bayern.de` / BeckRS-citation lookups for German case law instead —
  a durable retrieval lesson. Unchanged: this is a **German first-instance**
  civil judgment. It is persuasive, **not binding outside its own jurisdiction**,
  and not an EU-level authority. `cjeu-c-582-14-breyer` is the EU-level link in
  the same reasoning chain; the ePrivacy terminal-storage question
  (Directive 2002/58/EC Art. 5(3)) is a **separate** question this judgment does
  **not** decide.

### `garante-9782874-google-analytics`

- **instrument:** Garante per la protezione dei dati personali — *regulator
  decision*
- **authority:** Garante (IT) · **docket:** provvedimento, doc-web **9782874** ·
  **decision_date:** 23 June 2022
- **provision:** the Garante's finding on Google Analytics
- **text_form:** `topic only`
- **text:** The Garante's formal action on **Google Analytics**, concerning US
  transfer via analytics cookies. Related to, but legally distinct from, the
  third-party-font question — the mechanism at issue is transfer, not asset
  loading.
- **official_url:**
  https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9782874
- **consulted:** the URL above was identified but the decision text was **not
  summarized in detail** in the ingest pass —
  **verification_grade:** `not-fetched` for its content; the reference itself is
  official
- **language_version:** Italian
- **verified:** 2026-07-31
- **legal_status:** `in force`
- **notes:** Usable today only as *"the Garante has acted on US transfers via
  analytics cookies"*. Anything more specific requires an ingest of the
  provvedimento text.

### `absent-garante-google-fonts` — a verified **absence**

- **instrument:** — (this entry records that a decision **does not exist**) —
  *regulator decision, absent*
- **authority:** Garante (IT) — searched · **docket:** n/a ·
  **decision_date:** n/a
- **provision:** n/a — the searched-for subject is a Garante decision on remote
  Google Fonts loading
- **text_form:** `topic only`
- **text:** **No formal Garante provvedimento specifically on Google Fonts was
  found.** The only Italian-specific activity located is the **Monitora PA**
  campaign (8 August 2022), a **private activist** action that sent legal
  notices to roughly 10,000 Italian public administrations alleging GDPR
  violations from remote Google Fonts loading. It is **not** an authority
  decision and carries no regulatory weight of its own.
- **official_url:** n/a · context (secondary):
  https://www.agendadigitale.eu/sicurezza/privacy/google-fonts-nuova-grana-per-gli-animatori-digitali-il-problema-e-le-soluzioni/
- **consulted:** search across Garante publications plus Italian legal press —
  **verification_grade:** `secondary-corroborated` (an absence can only be
  evidenced this way)
- **language_version:** Italian
- **verified:** 2026-07-31
- **legal_status:** `not recorded — no such decision found`
- **notes:** **This entry exists to stop a specific fabrication.** Training-data
  intuition suggests an Italian regulatory decision parallel to the German one
  exists. It does not. A deliverable must **not** cite "a Garante decision on
  Google Fonts". The correct framing: no Italian regulatory decision on this
  specific pattern; the closest authority is
  `lg-muenchen-i-3-o-17493-20` (German case law) and `cjeu-c-582-14-breyer` (the
  IP-address-as-personal-data principle), with
  `garante-9782874-google-analytics` as an adjacent Italian enforcement analogy
  on the transfer logic — **not** on the asset-loading mechanic.

---

## Ingest requests (open)

**Closed by the 2026-07-31 gap-fill pass** (kept visible so no one re-opens
them): the T-553/23 docket · the primary CJEU docket page for C-703/25 P · a
non-`rewis.io` route to the LG München judgment · the Breyer judgment text.

Still open, in priority order:

1. **The 4 June 2026 Order (ECLI:EU:C:2026:465) on C-703/25 P** — the
   highest-value outstanding request in the whole corpus. Four guessed CELEX ids
   have failed; **use EUR-Lex's own search interface or InfoCuria's
   document-download link instead.**
2. `gc-latombe-2025-judgment` — the **judgment's own reasoning text** (only the
   docket and outcome are recorded).
3. `garante-9782874-google-analytics` — the provvedimento's own content. **Not
   attempted in the gap-fill pass** (out of that brief's scope), so it is
   genuinely untried, not blocked.
4. A **hearing date** for C-703/25 P, if one has since been set.

## Neighbours

Sibling pages appear as their scopes are harvested; a link below to a page that
is not yet present means that instrument has no entry in this corpus **yet**,
which under `../_schema.md` reads as `not recorded — ingest pending`, never as
"no such rule".

- `../_schema.md` — the entry contract, including the `case-law` /
  `regulator-decision` instrument kind and the rule that a verified absence is
  itself citable.
- `../eu/eu-us-dpf-adequacy.md` — the adequacy decision the Latombe entries
  contest.
- `../eu/gdpr.md` — `gdpr-art-6-1-f` (the basis LG München rejected) and
  `gdpr-art-35-4` (the basis for the Garante DPIA list).
- `../national/it-codice-privacy.md` — `it-codice-privacy-art-122`, the Italian
  provision the font/cookie question runs through.
- `../eu/eprivacy-directive.md` — Art. 5(3) and the **separate** terminal-storage
  question; a finding there does not resolve the IP-disclosure question these
  judgments concern, and vice versa.
