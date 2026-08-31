# EU-US Data Privacy Framework adequacy — EU

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Status is contested (`in force — under appeal`) — this schema's
> legal_status vocabulary distinguishes "valid but contested" from settled
> law; do not silently launder one into the other. Entry contract:
> `../_schema.md`.

Commission Implementing Decision (EU) 2023/1795.

**Instrument kind:** `regulation`-family (a Commission implementing decision —
directly applicable, no transposition).

**This is the worked example for `legal_status: in force — under appeal`.** It
is currently a valid transfer basis **and** it is contested before the CJEU. A
corpus that could only say "in force" would silently launder a contested basis
into a settled one.

---

### `eu-dpf-adequacy-2023-1795`

- **instrument:** Commission Implementing Decision (EU) 2023/1795 of 10 July
  2023 pursuant to Regulation (EU) 2016/679 on the adequate level of protection
  of personal data under the EU–US Data Privacy Framework — *implementing
  decision*
- **provision:** the decision as a whole (the adequacy finding)
- **text_form:** `normalized summary`
- **text:** The Commission found that the United States ensures an adequate
  level of protection for personal data transferred from the EU to
  organisations self-certified under the EU–US Data Privacy Framework.
  Practically: a transfer to a DPF-certified US recipient rests on adequacy and
  does **not** additionally require Art. 46 safeguards such as SCCs.
- **official_url:** EUR-Lex CELEX **32023D1795** —
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023D1795
- **consulted:** **the decision itself was not re-fetched in this pass.** Status
  and litigation history were read from IAPP
  (https://iapp.org/news/a/european-general-court-dismisses-latombe-challenge-upholds-eu-us-data-privacy-framework)
  and the EU Law Analysis blog
  (http://eulawanalysis.blogspot.com/2025/10/the-general-court-of-european-union.html),
  both dated October 2025 — **verification_grade:** `secondary-corroborated`
- **language_version:** English; the consulted material is commentary about the
  decision, not the decision text
- **verified:** 2026-07-31
- **legal_status:** **`in force — under appeal`**

**Litigation history — as at 2026-07-31, against the Court's own record:**

- Challenged by MEP Philippe Latombe.
- **court:** General Court of the European Union (Tenth Chamber, Extended
  Composition) · **docket:** **Case T-553/23**, *Latombe v Commission* ·
  **decision_date:** **3 September 2025**. The General Court **dismissed** the
  annulment action, finding the Data Protection Review Court sufficiently
  independent, US bulk-collection limits adequate, and security/automated-decision
  protections substantially equivalent. The judgment is citable in full form; its
  **reasoning text is still not fetched** — see `../case-law/` →
  `gc-latombe-2025-judgment`.
- **court:** Court of Justice of the European Union · **docket:** **Case
  C-703/25 P** · Latombe **appealed on 31 October 2025**. The docket is
  confirmed on InfoCuria, the Court's own case-management database
  (`proxy-sourced`).
- **The case's status on the Court's own record remains "Pending"** as of
  2026-07-31. **No hearing date is recorded.**

> ### ⚠ A 4 June 2026 Order exists and its content is UNCONFIRMED
>
> InfoCuria lists one case-law document against C-703/25 P: an **Order of
> 04/06/2026, ECLI:EU:C:2026:465**. It postdates every other source on this page.
> **Its content and legal effect could not be retrieved** — EUR-Lex returned
> "document does not exist" for four CELEX variants, through the same proxy route
> that works for everything else.
>
> **Do not infer its effect.** Orders that do not close a case are routine. The
> status field still reads "Pending", which under the Court's own convention
> means the case is open. **"An Order exists" must not collapse into either "the
> appeal was decided" or "nothing has happened"** — both would be fabrications on
> the evidence available.
>
> **Consequence for `legal_status`:** it stays **`in force — under appeal`**.
> This uncertainty is a reason to keep the contest visible, never a reason to
> resolve it in either direction. Flag the Order to the DPO explicitly; it is the
> corpus's highest-value open ingest request.

**What follows, and what does not.** A US sub-processor covered by DPF
self-certification currently needs no SCCs — that is the state of the law
today. But this adequacy basis is under live appeal at the EU's highest court,
which has struck down **both** predecessor frameworks (Safe Harbor,
Privacy Shield). "Settled" is the wrong word for a compliance document with a
multi-year horizon. The honest form is: **valid today, monitored risk, with a
review trigger on the CJEU hearing or ruling.** Whether to rely on it is the
DPO's call, not this corpus's.

## Not transcribed

1. **The content of the 4 June 2026 Order (ECLI:EU:C:2026:465)** — highest
   priority. Use EUR-Lex's search interface or InfoCuria's document-download
   link; four guessed CELEX ids have already failed.
2. A **hearing date**, if one has since been set.
3. The **decision text itself** from EUR-Lex, to lift this entry above
   `secondary-corroborated`. Untried through the `r.jina.ai` proxy route that
   worked for the GDPR and the NIS2 Directive — **worth one attempt.**

## Neighbours

- `gdpr.md` — `gdpr-art-44`, `gdpr-art-46-1-2c`, `gdpr-art-49-1`.
- `../case-law/` — `gc-latombe-2025-judgment`.
- `../_schema.md`
