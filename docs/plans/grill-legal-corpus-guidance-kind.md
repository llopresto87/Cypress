# The legal corpus has a fifth instrument kind and a schema that defines four

**Status:** not started. Recorded during the 7.26.0 harvest, which added the
second page to use this kind. Deferred by the owner as out of scope for that
session.
**Baseline commit:** working tree at 7.26.0
**Owner:** seed steward
**Surface:** `legal-corpus/_schema.md`, and every page that declares
`kind: guidance`

## §1 The finding

`legal-corpus/_schema.md` §"Four instrument kinds — do not force one shape"
defines `regulation`, `directive`, `standard`, and `case-law` /
`regulator-decision`. Each names the fields it adds on top of the eight every
entry carries.

Two pages in the corpus declare a kind that section does not define:

- `legal-corpus/eu/edpb-guidelines-07-2020.md` declares `kind: guidance`, and
  describes it on the page as "a regulator's interpretive reading, not binding
  law"
- `legal-corpus/eu/a29wp-opinion-05-2014-anonymisation.md` declares the same
  kind for the opinion of an independent advisory body

The schema heading says not to force one shape, so a fifth kind is not itself a
violation. The gap is that the fifth kind carries a risk the four do not, and
no field records it.

## §2 Why guidance is structurally different

The four defined kinds each add the field that makes them citable. A
`regulation` that applies on a staggered schedule records `applies_from` per
obligation. A `directive` records `transposed_by`, because what a national
authority enforces is the transposing act and a directive alone cannot be cited
for a national obligation. A `standard` records what a reader cannot get,
because its normative wording is copyrighted. A decision records whether the
primary text was fetched.

Guidance has its own version of that question, and it is about **endorsement
currency**. Guidance can be issued by a body that no longer exists, under a law
since repealed, and then either carried forward by the successor body or left
behind. Nothing about the document itself shows which. A reader who cites
unendorsed guidance as current has made the same class of error as one who cites
a directive for a national obligation.

## §3 The case that exposed it

The A29WP opinion is the hard case, and it is already in the corpus with its
evidence gathered. The opinion was adopted under a Directive repealed in 2018.
The successor body's own endorsement list names sixteen carried-forward
documents and this is not among them, which is a verified absence rather than an
express withdrawal. Yet the same successor cites the opinion in later guidelines
at the publisher's own URL.

So the honest status is neither current nor withdrawn. The page records
`legal_status: unverified — open question` and lays out both directions.

The EDPB page, whose author is the successor body itself, records
`legal_status: in force (as guidance)`.

Both answers are right for their page. Both were improvised, because the schema
gave neither a field to fill. A third guidance page will improvise a third way.

## §4 The shape of the fix

Add a fifth kind to `_schema.md` with one mandatory field, modelled on how
`directive` handles transposition:

- `endorsement`, recording whether the issuing body's successor has carried
  the document forward. Values in the spirit of `transposition_status`: carried forward /
  not endorsed / expressly withdrawn / open question, each with the evidence
  that establishes it and the date it was read.
- The citation limit that follows, stated the way the directive section states
  its own: guidance whose `endorsement` is unresolved may be cited as the
  issuing body's reading at the time it was written, and never as current
  guidance under the law that replaced it.

Both existing pages already carry the substance in prose, so the migration is a
field extraction rather than new research. Neither needs a fresh fetch.

## §5 Verification

`tests/legal-lint.py` is the corpus contract check and already reports entry
and page counts with recorded edition debt. The new field belongs in whatever
it enforces per kind. A regression case proves a `guidance` page missing
`endorsement` fails, and that both existing pages pass once migrated.

## §6 Risks

| Risk | Mitigation | Verification |
|---|---|---|
| The migration rewrites a status that was carefully reasoned | Extract the existing prose into the field; change no value without a fresh read | Diff both pages' `legal_status` before and after; they must be unchanged |
| A fifth kind invites a sixth for every document type | The bar is a kind that needs a field the four do not supply, which is the same bar the four met | The new section states the field and the citation limit, as each existing kind does |

## §7 Open questions

| # | Question | Why it matters | Current assumption | How to resolve | Owner |
|---:|---|---|---|---|---|
| 1 | Is `endorsement` one field or two (status plus evidence) | The four kinds vary; `directive` uses three fields, `standard` two | One field carrying status, with evidence in the entry's existing consulted line | Read how `transposition_status` and `divergence` split, and follow it | steward |
| 2 | Does a guidance page whose issuing body still exists need the field at all | An unnecessary mandatory field is answered by rote | It does, recorded as carried forward by the issuing body itself | Decide when writing the section | steward |

## §8 What this plan does not do

It does not revisit either existing page's recorded status, and it does not
re-fetch either source. Both were verified from their publishers on 2026-09-22
and no grade may be raised without a new read. It also does not touch the four
defined kinds.
