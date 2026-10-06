# EDPB Guidelines 2/2023 on the technical scope of Art. 5(3) ePrivacy Directive: EU

> Project-agnostic legal citation notes, kept in the seed's legal corpus
> (`legal-corpus/README.md`). Entry contract: `../_schema.md`.

**Instrument kind:** `guidance`. A supervisory body's interpretive reading,
**not binding law**, of the provision recorded as `eprivacy-dir-2002-58-art-5-3`
(`eprivacy-directive.md`). Cite it as guidance and never as the rule itself.
The Guidelines analyse when Art. 5(3) applies. By their own paragraph 4 they do
not analyse the exemptions from consent.

## Standing fields: the inheritable half of the entry contract

One instrument, one document, one fetch. These fields hold for every entry
below unless the entry states its own value:

- **instrument:** European Data Protection Board, *Guidelines 2/2023 on
  Technical Scope of Art. 5(3) of ePrivacy Directive*, Version 2.0. *guidance*
- **official_url:** landing page:
  https://www.edpb.europa.eu/documents/guideline/guidelines-22023-on-technical-scope-of-art-53-of-eprivacy-directive_en
  (the older path
  https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-22023-technical-scope-art-53-eprivacy-directive_en
  answers HTTP 302 to it; the landing page says "Final version" and
  "Version 2.0") · PDF:
  https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf
- **consulted:** a direct `curl` fetch of that PDF on 2026-10-05 (HTTP 200; it
  redirected to
  https://www.edpb.europa.eu/system/files/documents/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf),
  15 pages, text-extracted with `pdftotext` and read from the file. The
  landing page answered HTTP 200 after that redirect. **verification_grade:**
  `primary-fetched`. No proxy, no blockage.
- **language_version:** English, **Version 2.0**, "Adopted on 7 October 2024".
  The document's own version history: "Version 1.0 14 November 2023 Adoption
  of the Guidelines for public consultation"; "Version 2.0 7 October 2024
  Adoption of the Guidelines after public consultation". Cite Version 2.0;
  Version 1.0 is the consultation draft.
- **verified:** 2026-10-05
- **legal_status:** `in force` (as guidance)

Transcription rule for every entry: paragraph text is reproduced as printed,
including the source's own spelling and quotation marks. A footnote reference
numeral is shown as `[fn N]`; the footnote text is not transcribed.

---

### `edpb-gl-02-2023-para-1`

- **provision:** paragraph 1 (section 1, Introduction): Art. 5(3) is not
  limited to cookies
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 1. According to Article 5(3) ePD, ‘the storing of information, or the
  > gaining of access to information already stored, in the terminal equipment
  > of a subscriber or user’ is only allowed on the basis of consent or
  > necessity for specific purposes set out in that Article. As reminded in
  > Recital 24 of the ePD[fn 2], the goal of that provision is to protect the
  > users’ terminal equipment, as they are part of the private sphere of the
  > users. It results from the wording of the Article, that Article 5(3) ePD
  > does not exclusively apply to cookies, but also to ‘similar technologies’.
  > However, there is currently no comprehensive list of the technical
  > operations covered by Article 5(3) ePD.

### `edpb-gl-02-2023-para-6`

- **provision:** paragraph 6 (section 2.1, "Key elements for the applicability
  of Article 5(3) ePD"): the three criteria
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 6. Article 5(3) ePD applies if:
  >
  > a. CRITERION A: the operations carried out relate to ‘information’. It
  > should be noted that the term used is not ’personal data’, but
  > ‘information’.
  >
  > b. CRITERION B: the operations carried out involve a ‘terminal equipment’
  > of a subscriber or user (B.1), which imply the need to assess the notion
  > of a ‘public communications network’ (B.2).
  >
  > c. CRITERION C the operations carried out indeed constitute ‘storage’
  > (C.1) or a ‘gaining of access’ (C.2). Those two notions can be studied
  > independently, as reminded in WP29 Opinion 9/2014: ‘Use of the words
  > “stored or accessed” indicates that the storage and access do not need to
  > occur within the same communication and do not need to be performed by the
  > same party’[fn 5].
  >
  > For the sake of readability, the entity gaining access to information
  > stored in the user’s terminal equipment will be hereafter referred to as
  > an ‘accessing entity’.

- **notes:** Criterion A turns on "information", not "personal data", as the
  paragraph itself says. Whether personal data is involved is a separate
  question under `gdpr.md`.

### `edpb-gl-02-2023-para-53`

- **provision:** paragraph 53 (section 3.2, "Local processing")
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 53. If at any point and for example in the client-side code, the processed
  > information is made available to a third-party, for example sent back over
  > the network to a server, such an operation (instructed by the entity
  > producing the client-side code distributed on the user terminal equipment)
  > would constitute a ‘gaining of access to information already stored’. The
  > fact that this information is being produced locally does not preclude the
  > application of Article 5(3) ePD.

- **notes:** paragraph 52, which describes the local-processing case this
  paragraph rules on, is `not recorded`.

### `edpb-gl-02-2023-paras-54-56`

- **provision:** paragraphs 54 to 56 (section 3.3, "Tracking based on IP
  only")
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 54. Some providers are developing solutions that only rely on the
  > collection of one component, namely the IP address, in order to track the
  > navigation[fn 28] of the user, in some case across multiple domains. In
  > that context Article 5(3) ePD could apply even though the instruction to
  > make the IP available has been made by a different entity than the
  > receiving one.
  >
  > 55. However, gaining access to IP addresses would only trigger the
  > application of Article 5(3) ePD in cases where this information originates
  > from the terminal equipment of a subscriber or user. While it is not
  > systematically the case (for example when CGNAT[fn 29] is activated), the
  > static outbound IPv4 originating from a user’s router would fall within
  > that case, as well as IPV6 addresses since they are partly defined by the
  > host. Unless the entity can ensure that the IP address does not originate
  > from the terminal equipment of a user or subscriber, it has to take all
  > the steps pursuant to the Article 5(3) ePD.
  >
  > 56. While the present guidelines do not analyse the application of the
  > exemptions to the obligation to collect consent provided by Article 5(3)
  > ePD, it is important to once again recall that the applicability of this
  > article does not systematically mean that consent needs to be collected.
  > The EDPB thus reminds that in each case it would have to be assessed if a
  > consent is needed or whether an exemption under Article 5(3) ePD could
  > apply[fn 30].

- **notes:** paragraph 56 is the Guidelines' general reminder that
  applicability of Art. 5(3) "does not systematically mean that consent needs
  to be collected". It sits in the IP section and is cited across use cases.

### `edpb-gl-02-2023-paras-57-60`

- **provision:** paragraphs 57 to 60 (section 3.4, "Intermittent and mediated
  IoT reporting")
- **text_form:** **verbatim**
- **text (EN, verbatim):**

  > 57. IoT (Internet of Things) devices produce information continuously over
  > time, for example through sensors embedded in the device, which may or may
  > not be locally pre-processed. In many cases, information is made available
  > to a remote server, but the modalities of that collection can vary.
  >
  > 58. Some IoT devices have a direct connection to a public communication
  > network with a cellular SIM card. Other may have an indirect connection to
  > a public communication network, for example through the use of WIFI or the
  > relay of information to another device through a point-to-point connection
  > (for example, through Bluetooth). The other device can for example be a
  > smartphone or a dedicated gateway which may or may not pre-process the
  > information before sending it to the server.
  >
  > 59. IoT devices might be instructed by the manufacturer to always stream
  > the collected information, yet still locally cache the information first,
  > for example until a connection is available.
  >
  > 60. In any case the IoT device, where it is connected (directly or
  > indirectly) to a public communications network, would itself be considered
  > a terminal equipment. The fact that the information is streamed or cached
  > for intermittent reporting does not change the nature of that information.
  > In both situations Article 5(3) ePD would apply as there is, through the
  > instruction of code on the IoT device to send the dynamically stored data
  > to the remote server, a ‘gaining of access’.

- **notes:** paragraph 60 states the conclusion; paragraphs 57 to 59 set out
  the cases it covers (direct cellular connection, indirect connection through
  Wi-Fi or a point-to-point relay to a smartphone or gateway, streaming with
  local caching). Quote paragraph 60 with the case it is applied to.

---

## Recorded gaps

- **Every other paragraph**, including the analysis of each criterion
  (sections 2.2 to 2.6), the URL and pixel tracking case (section 3.1) and the
  unique-identifier case (section 3.5): `not recorded`.
- **The footnotes** referenced in the entries above: `not recorded`.

## Neighbours

- `eprivacy-directive.md`: `eprivacy-dir-2002-58-art-5-3`, the provision these Guidelines read.
- `../national/it-codice-privacy.md`: `it-codice-privacy-art-122`, the Italian provision that transposes it.
- `../_schema.md`

