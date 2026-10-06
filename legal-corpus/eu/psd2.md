# Directive (EU) 2015/2366 (PSD2), as amended: EU

> Project-agnostic legal citation notes, kept in the seed's legal corpus
> (`legal-corpus/README.md`). Entry contract: `../_schema.md`. A directive binds
> Member States, not persons: see `transposed_by` before citing any entry for a
> national obligation.

**Instrument kind:** `directive`. The provisions below are the strong customer
authentication (SCA) block. Its technical requirements and exemptions sit in
the delegated regulation that Art. 98 mandates: `sca-rts-2018-389.md`.

## Standing fields: the inheritable half of the entry contract

One instrument, one consolidated text, one fetch. These fields hold for every
entry below unless the entry states its own value:

- **instrument:** Directive (EU) 2015/2366 of the European Parliament and of
  the Council of 25 November 2015 on payment services in the internal market,
  amending Directives 2002/65/EC, 2009/110/EC and 2013/36/EU and Regulation
  (EU) No 1093/2010, and repealing Directive 2007/64/EC (OJ L 337 23.12.2015,
  p. 35), as amended. *directive*
- **official_url:** consolidated:
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02015L2366-20250117
  · original:
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32015L2366
- **consulted:** the consolidated text, fetched on 2026-10-05 directly from
  EUR-Lex at the consolidated URL above (HTTP 200, no WAF challenge on this
  pass) **and** from the Publications Office repository
  (`https://publications.europa.eu/resource/celex/02015L2366-20250117`, which
  resolved to cellar `7968d8a5-d7ed-11ef-be2a-01aa75ed71a1.0006.02`). The two
  texts of every article below were compared and are identical.
  **verification_grade:** `primary-fetched`. Earlier passes met an AWS WAF
  challenge (HTTP 202) at EUR-Lex; this pass did not. Re-probe rather than
  inherit either result.
- **language_version:** English, **consolidated text as at 17.01.2025**
  (document `02015L2366 — EN — 17.01.2025 — 002.001`). The Publications Office
  SPARQL index, queried on 2026-10-05, lists three consolidations, 2015-12-23,
  2024-04-08 and 2025-01-17, and none later. The consolidation names its
  amending acts: Directive (EU) 2022/2556 (M1) and Regulation (EU) 2024/886
  (M2), plus a corrigendum (OJ L 102, 23.4.2018, p. 97). The consolidation
  itself states that it "has no legal effect"; the authentic text is the OJ
  publication.
- **verified:** 2026-10-05
- **legal_status:** `in force`
- **transposed_by:** `not recorded — ingest pending`. No national transposing
  act of this directive is in this corpus. · **transposition_status:** `not
  recorded` · **divergence:** `not assessed`. Until a transposing act is
  ingested, every entry below is citable for Union-level scope and structure
  only, and each citation must carry that limit.

---

### `psd2-art-4-30`

- **provision:** Article 4, point (30), definition of "strong customer
  authentication"
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > (30) ‘strong customer authentication’ means an authentication based on the use of two or more elements categorised as knowledge (something only the user knows), possession (something only the user possesses) and inherence (something the user is) that are independent, in that the breach of one does not compromise the reliability of the others, and is designed in such a way as to protect the confidentiality of the authentication data;

- **notes:** the consolidation marks Article 4 as original text (▼B) up to and
  including point (30): no amending act changed this definition.

### `psd2-art-97`

- **provision:** Article 97, "Authentication" (paragraphs 1 to 5)
- **text_form:** **verbatim** (complete)
- **text (EN, verbatim):**

  > 1. Member States shall ensure that a payment service provider applies
  > strong customer authentication where the payer:
  >
  > (a) accesses its payment account online;
  >
  > (b) initiates an electronic payment transaction;
  >
  > (c) carries out any action through a remote channel which may imply a risk
  > of payment fraud or other abuses.
  >
  > 2. With regard to the initiation of electronic payment transactions as
  > referred to in point (b) of paragraph 1, Member States shall ensure that,
  > for electronic remote payment transactions, payment service providers
  > apply strong customer authentication that includes elements which
  > dynamically link the transaction to a specific amount and a specific
  > payee.
  >
  > 3. With regard to paragraph 1, Member States shall ensure that payment
  > service providers have in place adequate security measures to protect the
  > confidentiality and integrity of payment service users’ personalised
  > security credentials.
  >
  > 4. Paragraphs 2 and 3 shall also apply where payments are initiated
  > through a payment initiation service provider. Paragraphs 1 and 3 shall
  > also apply when the information is requested through an account
  > information service provider.
  >
  > 5. Member States shall ensure that the account servicing payment service
  > provider allows the payment initiation service provider and the account
  > information service provider to rely on the authentication procedures
  > provided by the account servicing payment service provider to the payment
  > service user in accordance with paragraphs 1 and 3 and, where the payment
  > initiation service provider is involved, in accordance with paragraphs 1,
  > 2 and 3.

- **notes:** the duty-holder the article names is the "payment service
  provider"; the article imposes no duty on a payee as such. The consolidation
  marks the article as original text (▼B). **Application date is a formula,
  not a calendar date.** Art. 115(4) of the same consolidated text reads: "By
  way of derogation from paragraph 2, Member States shall ensure the
  application of the security measures referred to in Articles 65, 66, 67 and
  97 from 18 months after the date of entry into force of the regulatory
  technical standards referred to in Article 98." The resulting date depends
  on the entry into force of the delegated regulation;
  `sca-rts-2018-389-art-38` records that regulation's own application dates.

### `psd2-art-98`

- **provision:** Article 98, "Regulatory technical standards on authentication
  and communication" (paragraphs 1 to 5)
- **text_form:** **verbatim** (complete)
- **text (EN, verbatim):**

  > 1. EBA shall, in close cooperation with the ECB and after consulting all
  > relevant stakeholders, including those in the payment services market,
  > reflecting all interests involved, develop draft regulatory technical
  > standards addressed to payment service providers as set out in Article
  > 1(1) of this Directive in accordance with Article 10 of Regulation (EU) No
  > 1093/2010 specifying:
  >
  > (a) the requirements of the strong customer authentication referred to in
  > Article 97(1) and (2);
  >
  > (b) the exemptions from the application of Article 97(1), (2) and (3),
  > based on the criteria established in paragraph 3 of this Article;
  >
  > (c) the requirements with which security measures have to comply, in
  > accordance with Article 97(3) in order to protect the confidentiality and
  > the integrity of the payment service users’ personalised security
  > credentials; and
  >
  > (d) the requirements for common and secure open standards of communication
  > for the purpose of identification, authentication, notification, and
  > information, as well as for the implementation of security measures,
  > between account servicing payment service providers, payment initiation
  > service providers, account information service providers, payers, payees
  > and other payment service providers.
  >
  > 2. The draft regulatory technical standards referred to in paragraph 1
  > shall be developed by EBA in order to:
  >
  > (a) ensure an appropriate level of security for payment service users and
  > payment service providers, through the adoption of effective and
  > risk-based requirements;
  >
  > (b) ensure the safety of payment service users’ funds and personal data;
  >
  > (c) secure and maintain fair competition among all payment service
  > providers;
  >
  > (d) ensure technology and business-model neutrality;
  >
  > (e) allow for the development of user-friendly, accessible and innovative
  > means of payment.
  >
  > 3. The exemptions referred to in point (b) of paragraph 1 shall be based
  > on the following criteria:
  >
  > (a) the level of risk involved in the service provided;
  >
  > (b) the amount, the recurrence of the transaction, or both;
  >
  > (c) the payment channel used for the execution of the transaction.
  >
  > 4. EBA shall submit the draft regulatory technical standards referred to
  > in paragraph 1 to the Commission by 13 January 2017.
  >
  > Power is delegated to the Commission to adopt those regulatory technical
  > standards in accordance with Articles 10 to 14 of Regulation (EU) No
  > 1093/2010.
  >
  > 5. In accordance with Article 10 of Regulation (EU) No 1093/2010, EBA
  > shall review and, if appropriate, update the regulatory technical
  > standards on a regular basis in order, inter alia, to take account of
  > innovation and technological developments, and of the provisions of
  > Chapter II of Regulation (EU) 2022/2554.

- **notes:** paragraphs 1 to 4 are original text (▼B); paragraph 5 was
  replaced by Directive (EU) 2022/2556, Article 7(6) (marked ▼M1). **Amendment
  trap: the 2015 original's paragraph 5 ends at "technological developments"
  and lacks the closing words "and of the provisions of Chapter II of
  Regulation (EU) 2022/2554".** Both texts were read from the Publications
  Office on 2026-10-05 (`32015L2366`, cellar
  `dd85ef2e-a953-11e5-b528-01aa75ed71a1.0006.03`; `32022L2556`, cellar
  `e2e67364-85bd-11ed-9887-01aa75ed71a1.0006.03`). The standards this article mandates were
  adopted as Commission Delegated Regulation (EU) 2018/389: see
  `sca-rts-2018-389.md`.

---

## Recorded gaps

- **National transposition.** No transposing act of this directive is in this
  corpus (`transposed_by` above). Ingest request: the transposing act of the
  plant's jurisdiction, consolidated, with its in-force header.
- **Successor instruments.** The legislative status of any proposal to replace
  or amend this directive was not checked in this pass: `not recorded`. Do not
  cite a proposal as law.
- **Every other article** of the directive: `not recorded`.

## Neighbours

- `sca-rts-2018-389.md`: the delegated regulation adopted under Art. 98, with
  the SCA requirements and the exemptions.
- `gdpr.md`: the data-protection regime that applies to the same payment data
  in parallel.
- `../_schema.md`

