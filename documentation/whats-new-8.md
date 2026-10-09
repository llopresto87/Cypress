# CYPRESS: what's new in 8.0 and 8.1

This page lists the features of 8.0 and 8.1 that a user or an agent
works with, and links each one to the guide or reference section that
explains it. The full record of each release, with every fix, is
[CHANGELOG.md](../CHANGELOG.md).

---

## 8.1.2: ready after the install

**The install builds the index.** Every install that places files, and so
every graft, ends by running `docs/graph/source-index.py build` and
printing its report. `growth-audit.py` prints the same report after its
verdicts at every grow and graft. The report is advice and never fails
either. It gives the counts and the build time, then each setup gap with a
`fix:` line: `TEST_GLOBS` unset or matching nothing, a `repo:` value that
names nothing, a Git repository inside the plant that no node names
(`repository-unnamed`), and hints about the test class and about patterns
in `docs/graph/source-index.json` that match no file. Guide:
[source-index.md, The build report](source-index.md#the-build-report).

**A seed skill for the tool.** `skill.source-index` routes the four code
questions to the tool and says how to act on the report. The kernel's
"Where to look next" names it in one line. Reference:
[skills-and-templates-reference.md, A.12](skills-and-templates-reference.md#a12-source-index).

**The router reads questions about files.** A file path or a code name
inside a trigger phrase no longer breaks it, and stands in for the
phrase's word `file` or `name`. A path route loads up to two seed skills
whose phrase the task holds beside the node that owns the file. Reference:
[DOCUMENTATION.md §5.7](../DOCUMENTATION.md#57-expertise-reaches-the-worker-that-needs-it).

**Upgrading to 8.1.2.** A graft brings the skill, the kernel line and the
router, and prints the report at its end. Act on each `fix:` line; the
cache bound is now 196 MiB.

## 8.1.0: the source index

**The source index.** `docs/graph/source-index.py` answers, from the code
and without a model, which code depends on a set of files (`impact`), which
tests a change reaches (`affected-tests`), which graph pages cite a file
(`anchors`), and where a name is defined (`symbols`). `--history` adds files
that changed together in past commits, and `anchors --moved` takes its
inputs from the code anchor. Guide: [source-index.md](source-index.md).

**The protocols call it on demand.** verify runs `affected-tests` after
GREEN, canonize runs `anchors --moved` before it records the code anchor,
and grow and adopt-existing hand the scouts the `inventory` of
`build --json`. Each step runs the tool once; no hook runs it. Guide:
[source-index.md, When the protocols call it](source-index.md#when-the-protocols-call-it).

**The `repo:` rule.** What a node's `repo:` value names on disk decides
what the node claims, the same way for the router and for `anchors`. A
folder or a file claims the paths under it, with or without a trailing
slash; a repository or the plant root claims nothing. A value that names
nothing on disk is read as before, and `anchors` reports it as
`repo-unresolved`. Guide:
[source-index.md, The `repo:` rule](source-index.md#the-repo-rule). The
router's side is in
[DOCUMENTATION.md §5.7](../DOCUMENTATION.md#57-expertise-reaches-the-worker-that-needs-it).

**New placed tools.** Every install places `docs/graph/source-index.py`,
`docs/graph/source_paths.py` (the path rules shared by `code-anchor.py`,
`source-index.py` and the router) and `docs/graph/plant_walk.py`. The
index lives in `.cypress/source-index/`; in 8.1.0 the first query built it,
and since 8.1.2 the install does. Reference:
[skills-and-templates-reference.md, the placed seed tools](skills-and-templates-reference.md#summary-table--seed-tools-placed-beside-the-contract-files).

**Upgrading to 8.1.0.** A graft brings the new tools and protocol steps.
Before you read an `affected-tests` answer as a gate set, list the plant's
fixtures, helpers and suite runner under `exclude` in
`docs/graph/source-index.json`
([Plant configuration](source-index.md#plant-configuration)). A node whose
`repo:` names a folder or file without a slash starts routing on it after
the graft.

## 8.0.0: corpus pages placed on request

**Corpus placement.** `install.sh <host> --expertise propose` prints the
library, tool and stack-keyed skill pages the project's manifests match.
`install.sh <host> --expertise <id>[,<id>...]` places exactly those pages,
records them in `.cypress/seed.json` under `expertise`, and later installs
refresh the ones nobody edited. Guide:
[corpus-placement.md](corpus-placement.md).

**Larger corpora.** The library corpus grew from 91 to 131 pages, with new
`galaxy` and `pub` ecosystems; the skill corpus from 12 to 33 pages, with
stack-keyed pages under `skill-corpus/<key>/`; the tool corpus from 24 to
40 pages; the agent corpus from 6 to 8 roles; and the legal corpus from 13
to 16 instrument pages. Every corpus admits a page only at the
withdraw-ready bar. Reference:
[corpora-and-integrations-reference.md, Part A](corpora-and-integrations-reference.md#part-a--the-corpora).

**Session metrics.** `docs/graph/session-metrics.py` reads the Session
metrics block that deliver appends to `changelog.md`. deliver runs its lint
role on the entry it appends:

```
python3 docs/graph/session-metrics.py --since <the date in that heading> --entry <the line of that heading>
```

harvest reads its query role with `--all --json`, and `--labels` prints the
labels the block uses, which the tool takes from the plant's deliver node
at run time. A full-form delivery whose block is missing or malformed is
reported. Reference:
[protocols-reference.md, The two forms](protocols-reference.md#the-two-forms-deliverforms);
contracts: [SPEC-0006](../docs/specs/SPEC-0006-session-metrics.md).

**A louder `install.sh --check`.** Besides the generated views, `--check`
now runs each wired context hook once, names each recorded expertise page
that is missing or stale, and names each agent or skill in a harness
directory with no graph home: `RETIRED` for a seed entry the running seed
no longer ships, `ORPHAN` for one the plant authored there. It deletes
nothing. A context hook whose script is missing prints one line,
`cypress: hook script missing: <path>; continuing without it. Re-run
install.sh to restore it.`, instead of nothing. Reference:
[integrations/claude-code/README.md](../integrations/claude-code/README.md).

**Stricter spec discovery.** A spec is `specs/SPEC-*.md`. Any other
Markdown file in the specs directory, apart from its index and readme, now
fails spec-lint and grill-lint as a misnamed spec. Rename it, or it is
never checked.

**Graft from an old stamp.** `tools/graft-ledger.py` takes
`--base-dir <dir>`, a copy of the seed at the stamped version, when the
seed's history no longer holds that version; `graft-run` infers the
adapters of an old stamp, and graft re-checks at the end every file its
record says it merged or kept. Reference:
[protocols-reference.md, graft](protocols-reference.md#graft).

**Harvest takes knowledge whole.** harvest generalizes a candidate instead
of rejecting it, admits a stack-bound procedure as a stack-keyed page, and
admits the version facts a library documents; each fact carries a
provenance class. canonize keeps a harvest-candidate record from
`docs/graph/plans/_harvest-candidates.template.md`. Decision:
[ADR-0028](../docs/decisions/adr-0028-harvest-takes-knowledge-whole.md);
reference: [protocols-reference.md, harvest](protocols-reference.md#harvest)
and [canonize](protocols-reference.md#canonize).

**Doctrine.** Planning, delegation, the postures and the lifecycle
protocols carry new rules, among them a scoped standing grant for repeated
non-production acts, asked for once at plan approval
(`vcs-posture.publish-authorization` in
[core/method/vcs-posture.md](../core/method/vcs-posture.md)), and a walking
skeleton first for a new pipeline or deploy path. The list is in the 8.0.0
entry of [CHANGELOG.md](../CHANGELOG.md); each rule lives in the node that
owns its subject and reaches an existing plant through `graft`.
