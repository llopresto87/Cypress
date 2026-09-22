# Tool: renamed-config-key-auditor

> Project-agnostic, durable capability notes, folded into the seed by the
> harvest protocol. This page is a **BLUEPRINT**: the capability, the oracle
> choice, the interface shape and the flattening rule are portable; the parsing
> of the project's own configuration documents is written against whatever
> formats the adopting project serves.

## 0. Identity

- **Category:** ops
- **Name:** renamed-config-key-auditor
- **Language / runtime:** any (an HTTP client, a reader for the project's
  configuration documents, and a parser for the vendor's published catalogue
  are the whole requirement)
- **Stability:** **blueprint**. No portable implementation ships here. Reading
  the configuration a project actually serves means parsing nested documents,
  and the formats configuration is usually written in are rarely covered by a
  language's standard library. A self-contained implementation would therefore
  have to supply its own configuration parsing, which is real work an adopting
  project should budget for before it starts. Everything above the parser is
  portable and is the value of the page.

## 1. What it does

Before a framework's major-version jump, answers which of the configuration
keys a project actually serves the target generation will **silently ignore**.

Frameworks that bind configuration by key name usually accept an unknown key
without complaint. The key is read, matched against nothing, and the default
applies. The service starts, reports healthy, and behaves as though the setting
had never been written. Nothing fails, which is why this class of defect is
found in production rather than in a gate: a timeout that reverted to its
default, a pool size nobody set, a feature toggle that has quietly been off
since the upgrade.

The tool exists because the configuration and the framework version move
independently, and the framework has no interest in telling anyone. A key that
was correct for one generation stays in the file, looking correct, long after
the generation that read it is gone.

## 2. Interface & invocation

```sh
renamed-config-key-audit \
  --root <root of the configuration the project actually serves> \
  --from <source generation> --to <target generation> \
  [--json]
```

- **Inputs:** two, and nothing else. The **root of the served configuration**
  (whatever the project really serves: a directory of files, a mirror pulled
  from a configuration server, a bundled resource tree) and the **source and
  target generations** of the framework. Both are required and
  neither has a default; a default root is how a tool becomes unshareable, and a
  default generation pair is how it becomes wrong.
- **Outputs:** one row per served key the target generation will ignore, each
  naming the key, the file it was found in, and the **vendor's own verdict**
  for it: renamed to some other key, removed outright, or superseded by a
  different mechanism. The verdict is quoted from the catalogue rather than
  inferred, so a reader can check it at the source.
- **Exit codes:** non-zero when the set is non-empty, so the tool is usable as a
  pre-migration gate and not only as a report.
- **Preconditions:** the configuration root is readable; the vendor's catalogue
  for the two generations is reachable and parseable.

## 3. Approach / algorithm

### The vendor's catalogue is the oracle

The tool does not pattern-match key names, and it carries **no rename list of
its own**. A hand-kept list is wrong the day after it is written, and worse, it
is wrong silently: it keeps returning clean results for the renames nobody
remembered to add.

Instead the tool fetches the **framework vendor's own published, machine-readable
changelog of renamed and removed configuration keys** for the two generations in
question, and uses that as its oracle. Where a vendor publishes no such
catalogue, the tool has no oracle, and it says so and stops rather than
degrading into a guess dressed as a finding.

This is the same discipline its two nearest neighbours follow, and the three
differ only in which authority they ask. One asks a live credentialed store
whether a declared name exists there; one asks the configuration system's own
resolver what a layered configuration resolves to; this one asks the vendor what
it renamed.

### Flatten before you compare

1. Fetch and parse the catalogue into old-to-new pairs, keeping each entry's
   verdict text.
2. **Flatten every configuration document under the root to fully-qualified key
   paths.** This is the step people get wrong. A nested document hides a key
   from any search that reads the file as lines, and a key that appears at two
   different depths is two different keys even when its leaf name is identical.
   The served key set is the set of fully-qualified paths, and the comparison is
   meaningless until the flattening is complete.
3. Intersect the served key set with the catalogue's retired set.
4. Report the intersection, each row carrying its file and the vendor's verdict.

### Enduring idioms

- **Run it against the destination generation before the migration lands**, not
  after. The whole value of the tool is being the gate that fires while the
  change is still cheap to make; run afterwards, it is an incident report.
- **One generation hop per run.** A key renamed twice appears on the retired
  list only under the hop that retired it, so a single query spanning several
  generations loses the middle steps and reports fewer findings than exist. Walk
  the hops in order and take the union.
- **Record which catalogue version answered.** The result is only as good as the
  catalogue behind it, and a reader six months later needs to know which one that
  was.

## 4. Portable vs blueprint

- **Portable (adopt verbatim):** the choice of oracle and the refusal to keep a
  rename list; the two-input interface with no defaults; the fully-qualified
  flattening rule; the one-hop-per-run idiom; reporting the vendor's verdict
  rather than a derived one; the non-zero exit that makes it a gate.
- **Write per project:** the reader for the configuration documents the project
  serves, and the fetch and parse of the vendor's catalogue format. Both are
  format-bound, and the configuration reader is the larger of the two.
- **Adopting note:** a project whose configuration is served from a
  configuration server rather than from files needs the root to address that
  server's view, not a local checkout of it. The two drift, and the served one
  is the one the framework reads.

## 5. Pitfalls and sharp edges

- **A clean run is not proof the configuration is correct.** It proves exactly
  one thing: no served key is on the vendor's retired list. A key that was never
  valid passes. A key that is still valid but now means something different
  passes. Say what the green means in the tool's own output, so a reader cannot
  inflate it.
- **The catalogue is the vendor's, and it is incomplete by construction.**
  Vendors record the renames they chose to record, and a generation whose
  catalogue is thin will produce a thin result that looks identical to a clean
  one. Report the catalogue version alongside the findings and read an empty
  result against a sparse catalogue as weak evidence.
- **Serving a key is not the same as the framework reading it.** A key under a
  profile that never activates is served and never bound, and the tool has no way
  to know which profiles a deployment selects. It reports served keys; an
  operator reads the result knowing that, and the report says so rather than
  leaving it to be assumed.
- **A removal is not always a rename.** Where the catalogue says a key was
  superseded by a different mechanism, there is no replacement key to write and
  the fix is a design change. Reporting those rows in the same shape as the
  renames invites someone to look for a new key that does not exist.

## 6. Tests that cover it

Cover: a served key on the catalogue's retired list is reported once, with its
file and the vendor's verdict; a served key absent from the catalogue is not
reported; a key nested several levels deep is found and reported at its
fully-qualified path; the same leaf name at two different depths yields two
distinct keys and is not collapsed; an unreachable or unparseable catalogue
refuses the run rather than reporting a clean result; an empty finding set exits
zero and a non-empty set exits non-zero; a multi-generation jump run as a single
query is proven to miss a twice-renamed key that the per-hop runs find.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Related tools:** `tool-corpus/ops/declared-variable-existence-auditor.md`
  (asks a live store whether a declared name exists there, which is a different
  authority answering a different question);
  `tool-corpus/ops/layered-config-merge-verifier.md` (asks the configuration
  system's own resolver what a layered configuration resolves to, and owns the
  guard-strength questions this tool does not touch).
- **Sources:** distilled from harvested plant experience; the catalogue it reads
  is the framework vendor's own configuration-changelog publication, named by the
  adopting project rather than by this page.

## 8. Changelog

- 2026-09-22 — created from harvested, generalized capability, by docs-librarian.
  Ships as a blueprint: the donor's implementation depended on a third-party
  parser, so no portable script travels with the page.
