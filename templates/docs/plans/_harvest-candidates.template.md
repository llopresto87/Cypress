<!--
Template: docs/plans/_harvest-candidates.template.md
Lives at: docs/graph/plans/harvest-candidates.md, one record per plant. Create
it from this form the first time a lesson is flagged a harvest candidate;
until then the plant has no record, and that is not a gap.
Written by: the docs-librarian, at the canonize close-out
(canonize.harvest-candidates owns when a row is added). The owner, a session
record or a retrospective flags the lesson; the librarian adds the row.
What it is for: the plant's running list of lessons that may belong in the
seed, kept so a later harvest can start from what this plant already
flagged instead of re-reading its history. A row is a candidate, not a
decision: harvest is the owner's to start, and its own gates (agnosticism,
durability, non-redundancy) decide each row. The record is plant-authored, so no
install or graft replaces it, and a lesson whose charter a graft overwrote
survives here.
Each row points at the lesson's home in the plant, where the rule itself
lives; the row never restates the rule. A lesson with no home yet is placed
first, then listed.
Append only: never rewrite a row. Strike it (~~row~~) and add a dated note
saying why, or add the new evidence to the row's provenance cell with its
date. A secret, a credential, or production or personal data never enters
the record (kernel §4).
The leading underscore keeps this blank form out of the linters and audits;
name the copy `harvest-candidates.md`, without the underscore.
-->

# Harvest candidates

The lessons this plant has flagged as possibly belonging in the seed. Each
row links to the rule's home here; harvest triages the rows.

**Admission test.** Before adding a row, ask: would this still make sense in
a repository with none of this project's services or domain? If not, it is a
project rule: it stays in its home here and gets no row. A lesson bound to a
stack still gets a row, because harvest keys it by stack. The test is a first
filter only; harvest's agnosticism gate still decides.

| # | Candidate | Home in the plant (the rule lives here) | Provenance and trigger | First guess at class |
|---|---|---|---|---|
| H-<n> | <the lesson, one line> | <node id and fact key, or path#anchor> | <who flagged it, when, and what made it necessary> | <doctrine / procedure / tool / role / template> |
