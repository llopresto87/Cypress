# EU scope & size-category definitions — EU

> Project-agnostic legal citation notes, folded into the seed by the harvest
> protocol. Entry contract: `../_schema.md`.

Directive 2005/29/EC Art. 2(a)/(n) and Recommendation 2003/361/EC.

**Instrument kinds:** `directive` and `recommendation`. Grouped on one page
because **they are only useful read together** — they are the two anchors the
NIS2 scope question hangs on (`nis2.md`). "Is this an online marketplace?" runs
through Directive 2005/29/EC; "is it big enough to be captured at all?" runs
through Recommendation 2003/361/EC. Each has its own citable id.

---

## ⚠ Two traps live on this page

1. **Amendment trap (Art. 2(n)).** The **original 2005 text has no point (n)**.
   It was inserted by the 2019 "Omnibus" Directive (EU) 2019/2161, applicable
   from 28 May 2022. Fetching the original CELEX yields "the definition does not
   exist" — which is wrong. Both ids are recorded below.
2. **Wrong-category trap (the SME thresholds).** The NIS2 size gate is pinned to
   the **medium**-enterprise ceiling, not the **small** one. The two figures sit
   in the same article and read alike; taking the small-enterprise threshold for
   the gate changes which entities are captured at all. Confirm which *category*
   a figure defines before reusing it, not merely that the figure appears in the
   document.

---

## Standing fields — the inheritable half of the entry contract

Both documents on this page were retrieved the same way on the same day, so the
inheritable fields (`../_schema.md`, "The citability contract") are stated once,
here, rather than restated under every entry:

- **Stated per entry, never inherited:** `instrument` (this page deliberately
  holds two, and they are not interchangeable), `provision`, `official_url` —
  each entry names the EUR-Lex CELEX record it was read from, and
  `dir-2005-29-ce-art-2-n` names the *original* CELEX too, because for that
  point the two differ (trap 1).
- **consulted:** a direct `curl` fetch of the EUR-Lex `TXT/HTML` endpoint for
  each document — **no proxy and no mirror** — **verification_grade:**
  `primary-fetched`.
  **The durable lesson, and the reason it is recorded here rather than three
  times below: EUR-Lex's WAF block is not site-wide.** Both documents on this
  page served cleanly to a direct `curl` in the *same session* in which the GDPR
  and NIS2 Directive full texts had to be routed through the `r.jina.ai` proxy.
  The blockage tracks document size or rendering path, not the domain. **A
  future ingest should try a direct fetch first and record which route worked**,
  instead of inheriting "EUR-Lex is blocked" as a property of the publisher.
- **language_version:** English throughout. The **edition** is load-bearing on
  this page and stays per entry: `dir-2005-29-ce-art-2-a` the original 2005
  text, `dir-2005-29-ce-art-2-n` the consolidated text `02005L0029-20220528`,
  and `rec-2003-361-ce-annex-art-2` the act as published (CELEX `32003H0361`) —
  for which whether any consolidated version exists is
  `not recorded — ingest pending`.
- **verified:** 2026-07-31.
- **legal_status:** `in force` for all three entries.

Where an entry states any of these fields inline, **the entry's own value wins.**

---

### `dir-2005-29-ce-art-2-a` — "consumer"

- **instrument:** Directive 2005/29/EC of the European Parliament and of the
  Council of 11 May 2005 concerning unfair business-to-consumer commercial
  practices in the internal market — *directive*
- **provision:** Article 2(a) — definition of "consumer"
- **text_form:** **verbatim**
- **text (EN, verbatim):** "'consumer' means any natural person who, in
  commercial practices covered by this Directive, is acting for purposes which
  are outside his trade, business, craft or profession;"
- **official_url:**
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32005L0029
- **language_version:** English, **original 2005 text** (this point is unamended
  since 2005; the consolidated text carries the same wording)
- **legal_status:** `in force` — the Directive as amended; **point (a) itself is
  unamended**, which is why the original text is citable for it.
- **transposed_by:** `not recorded — ingest pending` ·
  **transposition_status:** not recorded · **divergence:** not assessed
- **notes:** This definition is the anchor beneath any national provision that
  turns on "consumatori" — including the Italian decree's
  `it-dlgs-138-mercato-online`, where a "consumer" resolves to a **natural
  person acting outside trade, business, craft or profession**. The practical
  consequence is structural: where no party to a transaction meets that
  definition, the consumer anchor is not satisfied. **This entry supplies the
  test, not the answer**; applying it to a concrete set of facts is the
  controller's own qualification.

### `dir-2005-29-ce-art-2-n` — "online marketplace"

- **instrument:** Directive 2005/29/EC, **consolidated text as amended by
  Directive (EU) 2019/2161** (the "Omnibus Directive", which inserted points (m)
  and (n) into Article 2) — *directive, consolidated version*
- **provision:** Article 2(n) — definition of "online marketplace"
- **text_form:** **verbatim**
- **text (EN, verbatim):** "'online marketplace' means a service using software,
  including a website, part of a website or an application, operated by or on
  behalf of a trader which allows consumers to conclude distance contracts with
  other traders or consumers."
- **official_url:** consolidated —
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02005L0029-20220528
  · original (has **no** point (n)) —
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32005L0029
- **language_version:** English, **consolidated text** as at the 28 May 2022
  application date of the Omnibus amendments (CELEX `02005L0029-20220528`)
- **transposed_by:** `not recorded — ingest pending` ·
  **transposition_status:** not recorded · **divergence:** not assessed
- **notes:** **the amendment trap — see the box above**, which is why this is a
  separate entry from `dir-2005-29-ce-art-2-a`. Substantively, this definition
  matches the Italian decree's `it-dlgs-138-mercato-online` wording almost
  verbatim (both require a software/platform layer connecting traders/consumers
  to conclude distance contracts), which confirms the decree's cross-reference is
  accurate and current. The consumer anchor is `dir-2005-29-ce-art-2-a`.

### `rec-2003-361-ce-annex-art-2` — the SME thresholds

- **instrument:** Commission Recommendation of 6 May 2003 concerning the
  definition of micro, small and medium-sized enterprises (2003/361/EC) —
  *recommendation*. Non-binding at EU level in itself, but **binding wherever an
  instrument cross-references it**, as NIS2 Art. 2(1) does.
- **provision:** Annex, Title I, Article 2 — "Staff headcount and financial
  ceilings determining enterprise categories"
- **text_form:** **verbatim** (the headline thresholds; the full article is in
  the retained snapshot)
- **text (EN, verbatim):** "1. The category of micro, small and medium-sized
  enterprises (SMEs) is made up of enterprises which employ fewer than 250
  persons and which have an annual turnover not exceeding EUR 50 million, and/or
  an annual balance sheet total not exceeding EUR 43 million."
- **the three categories, as the same article defines them:**

  | Category | Headcount | Turnover | Balance sheet |
  |---|---|---|---|
  | **medium** (the NIS2 gate) | fewer than 250 | ≤ EUR 50 million | ≤ EUR 43 million |
  | small | fewer than 50 | ≤ EUR 10 million | ≤ EUR 10 million |
  | micro | fewer than 10 | ≤ EUR 2 million | ≤ EUR 2 million |

- **official_url:**
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32003H0361
- **language_version:** English, the act as published (CELEX `32003H0361`);
  whether a consolidated version of the Recommendation exists is
  `not recorded — ingest pending`, so treat this as the **original** text and
  re-check before a consequential determination (`../_schema.md`, "The
  amendment trap").
- **notes — which category the NIS2 gate uses, and it changes who is captured.**
  NIS2's size gate (`nis2-dir-art-2-1`) is pinned to the
  **medium**-enterprise ceiling "or above": the ceiling that takes an entity out
  of scope on size alone is **fewer than 250 employees**, with EUR 50M turnover /
  EUR 43M balance sheet. It is **not** the small-enterprise figure (~50
  employees, EUR 10M / EUR 10M), which is the common conflation.
- **not evaluated, and often decisive:** the Recommendation's Annex Arts. 3–6
  set the **autonomous / partner / linked enterprise** aggregation rules, which
  determine *whose* headcount and turnover count for a given legal entity. For a
  subsidiary inside a larger group these frequently decide the answer. They are
  **not transcribed here** — `not recorded`.

---

## Not transcribed

- Recommendation 2003/361/EC **Annex Arts. 3–6** (autonomous / partner / linked
  enterprise aggregation), needed whenever corporate-group structure bears on
  the size gate.
- Authority or Commission guidance applying the "mercato online" definition to
  platforms with no consumer party. **None was found; that absence is not an
  answer.**

## Neighbours

- `nis2.md` — `nis2-dir-art-2-1` (the size gate), `it-dlgs-138-mercato-online`
  (the consumer anchor), `nis2-dir-art-6-28` (the Directive's own
  cross-reference to Art. 2(n)).
- `eprivacy-directive.md` — the sibling amendment trap.
- `../_schema.md` — "The amendment trap".
