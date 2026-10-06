# Tool: not-affected-statement-generator

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). This page is a **BLUEPRINT**: the table-driven
> design, the refuse-to-emit checks, the determinism rule and the replay check
> are portable; reading one scanner's result format and writing one statement
> format are written per project.

## 0. Identity

- **Category:** ops
- **Name:** not-affected-statement-generator
- **Language / runtime:** any. A JSON reader for the scanner's results and a
  JSON writer for the statement document are the whole requirement; both are
  in most standard libraries.
- **Stability:** **blueprint**. The design was worked out in a real triage of
  several hundred residual findings and has not been built.
  No portable implementation ships, because the result format, the statement
  format and the gate that reads them differ per project. The checks and the
  determinism rule are the value of the page.

## 1. What it does

After a vulnerability scan, some findings remain that do not affect the
product: the vulnerable code is not present, is never executed, or cannot be
reached by an attacker. A VEX ("Vulnerability Exploitability eXchange")
document records that, one **not-affected statement** per advisory, and a
scanner that reads the document drops the matching findings from its report.

Writing a few statements by hand works. Writing hundreds does not: each one
is a chance to name the wrong package, suppress a finding that still matters
elsewhere, or drift from the evidence. This tool **generates** the statements
from one reviewed **disposition table**, deterministically, and refuses every
row that would make a false statement.

**When not to use it.** Do not use it to make a scan green. A row belongs in
the table only after the finding has been judged, with evidence, against a
closed vocabulary (fix it, accept it with a named precondition, or not
present / not on the execution path). Findings that can be fixed by a
version bump are bumped first (§3, check c). The judgment is a person's; the
generator only writes down what was decided, correctly.

## 2. Interface & invocation

```sh
not-affected-gen \
  --table <disposition table> --results <named scan run's results> \
  --template <document metadata> --out <statement document> \
  [--admit-id <pattern>]... [--admit-product-type <type>]... \
  [--issued <timestamp>] [--as-of <date>] [--dry-run]
```

- **Inputs:**
  - **Disposition table** (committed, reviewed). One row per advisory id,
    with: the product identifiers (package URLs, "purls", as the scanner
    reports them), the justification (from the format's closed list, below),
    the impact statement, the evidence reference (the triage note and its
    section), the **evidence targets** (the scan targets, such as images or
    filesystems, where this advisory was judged), the person who **declared**
    the disposition, and the **review-by** date. The template may give a
    default review period per class; a row without either date source is
    refused (§3, check f).
  - **Results** of one **named** scan run, in the scanner's machine-readable
    format (for example SARIF or the scanner's JSON). The run id is recorded
    in the output.
  - **Template**: the document metadata (author, document id base, the fixed
    impact-statement wording per class, the "revisit if" sentence).
  - **Admitted id and product types**: what the consuming gate accepts, for
    example only `CVE-` ids, and only some purl types.
  - `--issued`: the timestamp to stamp when the content changed (never the
    clock; see §3, determinism).
  - `--as-of`: the date against which review-by dates are checked. The
    default is the named run's own scan time, read from its results, so the
    check does not read the clock either. With neither, the run exits 2.
- **Outputs:** the statement document, sorted; with `--dry-run`, nothing is
  written and a summary is printed instead: counts per class and per
  justification, the rows that would be emitted, the **refuse list** with the
  reason per row, and the statements that would be **retired**.
- **Exit codes:** 0 written (or dry run complete) with an empty refuse list;
  1 at least one row refused (the document is still written from the rows
  that passed, and the refuse list is printed); 2 usage error, unreadable
  input, a content change with no `--issued`, or no date for the review-by
  check.
- **Preconditions:** the scan run named by `--results` is the one the
  statements are meant for; the table has been reviewed.

### The statement format (OpenVEX)

The worked format is OpenVEX: a JSON document with `@context`, `@id`,
`author`, `timestamp`, `version` and `statements`. Each statement has
`vulnerability.name`, `products` (each with `@id`, optionally
`subcomponents`), `status`, and for `not_affected` either a `justification`
or an `impact_statement` (upstream: one of the two is required). The
justification is one of `component_not_present`,
`vulnerable_code_not_present`, `vulnerable_code_not_in_execute_path`,
`vulnerable_code_cannot_be_controlled_by_adversary`,
`inline_mitigations_already_exist`. Write both the justification and an
impact statement that cites the evidence. CSAF and CycloneDX VEX carry the
same facts in other shapes.

OpenVEX has no field for an expiry or a review date. The generator writes
the declarer and the review-by date into each statement's `status_notes`, a
free-text field upstream defines as how the status was determined, in one
fixed machine-readable form. The consuming gate parses that form, because
the document stays applied after the generator has run.

### One table row and the statement it produces

A synthetic row (the advisory id is a placeholder and the package is
obviously fake; the column names are the ones this page uses):

```yaml
- advisory: CVE-YYYY-NNNNN
  products: [pkg:deb/example/libexample1]
  justification: vulnerable_code_not_in_execute_path
  impact: headers-only        # a class: its fixed wording is in the template
  evidence_ref: triage-note §3
  evidence_targets: [registry.example/app-worker]
  declared_by: owner@example.invalid
  review_by: 2000-06-30
```

The statement written for it, inside the document's `statements` list:

```json
{
  "vulnerability": {"name": "CVE-YYYY-NNNNN"},
  "products": [{"@id": "pkg:deb/example/libexample1"}],
  "status": "not_affected",
  "justification": "vulnerable_code_not_in_execute_path",
  "impact_statement": "The package ships headers only; no code from it is compiled into or run by the target. Evidence: triage-note §3. Revisit if this package appears in a target outside its evidence targets.",
  "status_notes": "declared-by: owner@example.invalid; review-by: 2000-06-30; evidence-targets: registry.example/app-worker"
}
```

## 3. Approach / algorithm

### One table, reviewed once

The person reviews three things: the template, the table, and the dry-run
summary. They do not review hundreds of JSON objects. A class of findings
that is decided mechanically (for example, every advisory against a
headers-only package in one image) is **derived** from the results by a
rule, not typed into the table row by row; the rule is in the table, and the
review covers the rule.

### Refuse-to-emit checks

Each row passes all of these or is refused, with its reason, and never
emitted:

- **(a) Seen in the named run.** The advisory appears in the named run's
  results for each of the row's evidence targets and for the package the
  row's product names. A statement for something the run did not report is
  either stale or aimed at the wrong package.
- **(b) The product id is the scanner's package name.** Build the product id
  from the package identifier the scanner reports, not from the name the
  package has elsewhere. Distributions rename packages across releases (a
  library and its renamed successor package), and a statement that names the
  other name matches nothing. It suppresses no finding and looks correct.
- **(c) No other carrier.** Find every target in the results where the same
  advisory is reported against the same package. If any of them is not in
  the row's evidence targets, refuse. A product id without a version matches
  every version of the package, in every target the scanner reads the
  document for, so the statement would also suppress a carrier nobody
  judged, possibly one that is reachable or could simply be upgraded.
  Upgrade that carrier first, scan again, and only then write the statement
  for the carriers that remain. If the scanner supports scoping a statement
  to one image (an image product with the package as a subcomponent), that
  is the alternative; test that it matches the way the image is referenced
  before relying on it.
- **(d) The gate admits it.** The id type (a non-CVE advisory id, for
  example) and the product type must be ones the consuming gate accepts.
  Rows that fail are listed separately. They become upgrade or accept-as-risk
  decisions, recorded where accepted risks are recorded.
- **(e) One statement per advisory.** When the gate requires unique advisory
  ids, merge the products of one advisory into one statement, and refuse a
  table with two rows for one id and different justifications.
- **(f) Attributable and in date.** `core/method/release-posture.md` §4
  treats a not-affected statement as a suppression: one with no declared
  author or expiry, or past its expiry, suppresses nothing. So a row with no
  `declared_by`, or with no review-by date (its own, or the template's
  default for its class), is refused. A row whose review-by date is not
  later than the `--as-of` date is refused as expired, and an existing
  statement for it is retired and listed in the summary. The person renews
  the row in the table, with a new review-by date, or the advisory goes back
  to the scan. The consuming gate applies the same date rule to the
  `status_notes` form, because a document written before the date stays
  applied after it.

### Determinism and idempotence

- Sort statements by advisory id, and products and subcomponents by id. Write
  with fixed indentation and key order.
- Never read the clock. If the generated statements equal those in the
  existing document, keep its `timestamp` and `version`, so a re-run is
  byte-identical. If they differ, increment `version` (OpenVEX requires it
  on any content change) and set `timestamp` from `--issued`; refuse without
  it.
- OpenVEX defines `timestamp` as the time the document "was issued", and an
  optional `last_updated` as the time of its last change. The generator
  treats each content change as a new issue of the document, so it sets
  `timestamp` and does not write `last_updated`, which would always equal
  it. A statement inherits the document's `timestamp` as the time its
  information "was known to be true", and that is right after a change,
  because the run has just re-checked every row against the named run.
- **Retire** a statement whose advisory no longer appears in the named run
  for any carrier (an upgrade cleared it). Report it in the summary.
- If a gate also keeps its own list of expected statements, generate that
  list from the same table in the same run, or better, have the gate read
  the generated file. Two hand-kept lists drift. The same holds for any
  count a person reads (a "statements in force" line in a status page or a
  report): generate it in the same run.

### Replay against the matcher's real rule

Before any scanner run, replay the table against the generated document
using the scanner's own matching rule, implemented as a check (for the
worked scanner: package type, namespace and name compared; a missing version
matches every version; missing qualifiers match any; see
`library-corpus/cli/trivy.md`, VEX section):

1. Every emitted row's (target, package, advisory) from the results must
   match a statement.
2. **Negative control:** one advisory in the results that has no row must
   match no statement. A replay that matches everything proves nothing.

Then run the real scanner once with the document applied, and confirm the
suppressed count and the negative control again. Record the scanner version
and database date with the result.

### Wording of each impact statement

Each impact statement carries the evidence reference
(`Evidence: <triage note> §<n>`) and the fixed sentence "Revisit if this
package appears in a target outside its evidence targets." The template owns
both, so every statement has them. A template may also have one slot per
statement that is filled from the scanner rule's short description of the
advisory (for example, the affected subsystem), so that statements of one
class do not all read the same.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the reviewed table as the only input a
  person edits; derived classes for mechanical cases; checks (a) to (f); the
  dry-run summary with the refuse list; sorting and no clock; version and
  timestamp only on change; retiring cleared statements; generating any gate
  ledger from the same table; the replay with a negative control; the
  impact-statement wording.
- **Write per project:** the reader for the scanner's result format, the
  writer for the statement format, the admitted-type lists of the project's
  gate, and the template text.
- **Adopting note:** keep the generator next to the triage notes it cites,
  and run it in the same change that updates the table, so a statement and
  its evidence always move together.

## 5. Pitfalls and sharp edges

- **A version-less product suppresses every carrier.** This is check (c),
  and it is the trap with the highest cost: a statement written for an
  unreachable copy hides a reachable one.
- **The right advisory against the wrong package name matches nothing.**
  This is check (b). It is silent: the scan still shows the finding, and the
  statement looks fine to a reader.
- **A green replay is not a green scan.** The replay checks the generator
  against a model of the matcher. Run the real scanner with the document
  once per change; scanners change their matching between versions.
- **Statements outlive their evidence.** A later image can add a carrier that
  check (c) would have refused. The next generator run against the new
  results refuses that row, which is the alarm. Run the generator on every
  scan, not only when the table changes.
- **Never apply the document to the run that produces the inventory.** The
  bill of materials stays the unsuppressed record; statements apply to a
  later scan of it (`library-corpus/cli/trivy.md`).
- **A non-admitted id is not an accepted risk by default.** Rows refused by
  check (d) need a decision of their own: upgrade, or accept with a reason
  in the risk record. Do not leave them in the refuse list.

## 6. Tests that cover it

Cover with synthetic results (two targets, one package reported in both,
advisory ids that are obviously fake): a row whose advisory is not in the
named run is refused (a); a row whose product names a renamed package is
refused (b); a row whose advisory also appears in a target outside its
evidence targets is refused, and passes once that target's finding is
removed from the results (c); a non-admitted id type and a non-admitted
product type are refused and listed (d); two rows for one advisory merge, and
conflicting justifications refuse (e); a row with no declarer or no review-by
date is refused, a row whose review-by date is not later than `--as-of` is
refused and its existing statement retired, and the written `status_notes`
carries the declarer and the review-by date in the fixed form (f); two runs on the same input give
byte-identical output; a content change without `--issued` exits 2, and with
it increments `version`; a statement whose advisory left the results is
retired; the replay matches every emitted row and does not match the
negative control; `--dry-run` writes nothing.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Procedures:** `skill-corpus/vulnerability-reduction-by-version-bumps.md`
  (bump first: the campaign that leaves the residual this tool writes
  statements for); `skill-corpus/residual-finding-exploitability-judgment.md`
  (the closed vocabulary that decides each table row).
- **Doctrine:** `core/method/release-posture.md` §4 (a not-affected
  statement is a suppression: attributable, with a review date, and ignored
  once past it; check f).
- **Library notes:** `library-corpus/cli/trivy.md` (VEX inputs, formats,
  product matching and scoping for one scanner).
- **Related tools:** `tool-corpus/ops/registry-digest-resolver.md` (pin an
  image by digest, so the target a statement was judged against is the target
  scanned); `tool-corpus/ops/structured-secret-field-detector.md` (the same
  "refuse rather than report clean" rule for a missing input).
- **Sources:** distilled from practice. The statement
  fields, the justification list and the version rule are from the OpenVEX
  specification (https://github.com/openvex/spec, `OPENVEX-SPEC.md`,
  retrieved 2026-10-05).

## 8. Changelog

- 2026-10-05: created as a blueprint: the generator and its checks are
  specified, not built.
- 2026-10-05: review fixes. Check (f) makes each statement attributable and
  dated, as `release-posture` §4 requires; a sample table row and its
  statement are shown; the choice of `timestamp` over `last_updated` is
  stated; generated counts and the optional per-statement slot are named.
