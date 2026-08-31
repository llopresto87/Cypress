# Legal corpus — the router

One row per instrument. This is to **statute** what `library-corpus/` is to
dependencies, and it exists for the same reason: memory of legal text drifts
exactly like memory of a library API.

- **Entry contract:** `_schema.md`. Read it before writing or citing anything —
  including **"The amendment trap"**, which is mandatory.
- **What belongs here and what never does:** `README.md`.
- **Written by** `docs-librarian`, ingested by `research-scout`, read by the
  role in `agent-corpus/legal.md`.

**Provenance is graded per entry, never per page.** A page may hold a
primary-fetched verbatim article beside a withheld standard control. Read the
entry's own `text_form`, `verification_grade`, `verified` and `legal_status`
before citing it — a page-level claim about any of those is always wrong.

## Instruments

| Instrument | Kind | Page | Coverage |
|---|---|---|---|
| Regulation (EU) 2016/679 (**GDPR**) | regulation | [eu/gdpr.md](eu/gdpr.md) | core definitions, the Art. 5 principles, lawful bases and special categories, the data-subject rights block, controller/processor obligations, records, security, breach notification, DPIA, certification, and the Chapter V transfer regime |
| Regulation (EU) 2024/2847 (**CRA**) | regulation, **staggered application** | [eu/cra.md](eu/cra.md) | scope and product classes, open-source treatment, essential cybersecurity requirements, SBOM, vulnerability-handling and reporting duties, conformity assessment and CE marking, penalties — with per-obligation application dates |
| Directive (EU) 2022/2555 (**NIS2**) | directive (+ transposing acts) | [eu/nis2.md](eu/nis2.md) | entity scope and sectors, risk-management measures, incident-reporting duties and their clock, governance and management liability, supervision and sanctions, plus national transposition linkage |
| Directive 2002/58/EC (**ePrivacy**) | directive | [eu/eprivacy-directive.md](eu/eprivacy-directive.md) | terminal-equipment storage and access (cookies and equivalents), confidentiality of communications — **original vs as-amended text is load-bearing here** |
| **EU scope definitions** (consumer / marketplace / SME thresholds) | directive + recommendation | [eu/eu-scope-definitions.md](eu/eu-scope-definitions.md) | the cross-cutting definitional anchors other instruments' scope tests point at, including the enterprise-size categories and their thresholds |
| Commission Implementing Decision (EU) 2023/1795 (**EU–US DPF adequacy**) | implementing decision | [eu/eu-us-dpf-adequacy.md](eu/eu-us-dpf-adequacy.md) | the adequacy basis for transfers to certified US organisations, its conditions, and its litigation history |
| Commission Implementing Decision (EU) 2021/914 (**SCCs**) | implementing decision | [eu/scc-2021-914.md](eu/scc-2021-914.md) | the four-module standard contractual clauses as the contractual transfer safeguard: module structure, operative articles, application dates, and what they replaced |
| **EDPB Guidelines 07/2020** (controller / processor) | supervisory guidance | [eu/edpb-guidelines-07-2020.md](eu/edpb-guidelines-07-2020.md) | the controller/processor/joint-controller qualification test and the processor-contract-content guidance — **guidance, not binding law; cite it as such** |
| **ISO/IEC 27001** (and its companion standards) | standard | [international/iso-27001.md](international/iso-27001.md) | identity and current edition, the management-system clause structure, the Annex A control set and Statement of Applicability — **wording withheld; citable by identifier and title only** |
| **Case law & regulator decisions** | case-law / regulator-decision | [case-law/index.md](case-law/index.md) | court judgments and supervisory-authority decisions bearing on the instruments above, each with court/authority, docket and decision date — including verified absences |
| **National: data-protection code** (IT) | national statute | [national/it-codice-privacy.md](national/it-codice-privacy.md) | the national adaptation of the data-protection regime, including the terminal-equipment/cookie provision that gives the ePrivacy rule national effect |
| **National: workers' statute** (IT) | national statute | [national/it-workers-statute.md](national/it-workers-statute.md) | the remote-control / employee-monitoring provision: permitted purposes, the collective-agreement or authority-authorisation gate, the work-tool carve-out, and the notice obligation |
| **National: accounting & tax retention** (IT) | national statute (multi-provision) | [national/it-accounting-retention.md](national/it-accounting-retention.md) | the statutory duty to retain accounting and tax records, its period, and its open-ended extension — the standing counterweight to erasure duties |

## What to read for what

| Question | Page |
|---|---|
| lawful basis, minimisation, storage limitation, accountability | `eu/gdpr.md` |
| transparency duties, access, portability, erasure | `eu/gdpr.md` |
| controller vs processor, joint controllership, processor-contract content | `eu/edpb-guidelines-07-2020.md` + `eu/gdpr.md` |
| transferring personal data outside the Union | `eu/eu-us-dpf-adequacy.md` + `eu/scc-2021-914.md` + `eu/gdpr.md` Chapter V |
| cookies, third-party assets, terminal-equipment storage | `eu/eprivacy-directive.md` + `national/it-codice-privacy.md` |
| breach / incident notification — **separate duties under separate regimes** | `eu/gdpr.md`, `eu/nis2.md`, `eu/cra.md` |
| "does this regime apply to us?" — entity size and sector gates | `eu/eu-scope-definitions.md`, then the instrument's own scope entries |
| product-side security obligations for software placed on the market | `eu/cra.md` |
| ISMS scope, Annex A controls, Statement of Applicability | `international/iso-27001.md` |
| how long must records be kept, and what blocks erasure | `national/it-accounting-retention.md` |
| employee monitoring and remote-control equipment | `national/it-workers-statute.md` |
| whether a court or authority has already decided a point | `case-law/index.md` |

## Standing hazards

Stated in full in `_schema.md`; the short form, because these are the ones that
cost the most:

1. **The amendment trap.** Original text and consolidated text sit under the
   same article number and read identically in tone. An entry must say which one
   it holds.
2. **Same number, different subject.** A directive's article N and its
   transposing act's article N routinely address unrelated matters. Cite the act
   the enforcing authority actually applies.
3. **`in force` ≠ settled.** An instrument can be valid and under appeal at the
   same time. Carry the contest with the citation.
4. **A number is the highest-risk field there is** — deadlines, thresholds, fine
   ceilings. A deadline that is a *formula* must never be recorded as a
   *calendar date*.
5. **Guidance is not law**, and a standard is not a legal basis. Both are citable
   for what they are, neither for more.
