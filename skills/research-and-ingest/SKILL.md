---
name: research-and-ingest
description: Find authoritative sources on the web (or via documentation MCP servers like Context7/DeepWiki), download or snapshot them when allowed, normalize them into clean Markdown, and stage them for the library-wiki. Use whenever a new library/spec/API/standard is being added, a wiki page is stale, an ADR needs current evidence, or a behavior best practice needs verification. Always prefer official upstream sources and version-pinned content over training data.
id: skill.research-and-ingest
tier: 2
kind: skill
origin: seed
title: research-and-ingest — fetch, snapshot, and normalize authoritative upstream sources for the wiki
owns:
  - research-and-ingest.method
  - research-and-ingest.source-ranking
requires:
peers:
  - skill.library-wiki
  - agent.research-scout
load_when:
  - "research a library before adding it"
  - "fetch upstream documentation"
  - "snapshot and normalize a source"
  - "refresh sources for a stale wiki page"
  - "use context7 or deepwiki for docs"
artifacts:
  - templates/library-page.template.md
est_tokens: 1200
---

# research-and-ingest

This skill is invoked by `research-scout` to fetch external content
in a disciplined way. The output of this skill is two artifacts:
raw snapshots in `docs/graph/sources/raw/` (when license allows) and
normalized summaries in `docs/graph/sources/normalized/`, plus a row in
`docs/graph/sources/index.md`. The wiki page (created by `library-wiki`)
draws from these.

## When to apply this skill

- A new dependency is being evaluated or added.
- A wiki page's "Last reviewed" date is older than the project's
  review cadence, or its pin no longer matches the lockfile.
- An ADR is being written and needs current evidence.
- An LLM/VLM feature is being designed and needs the provider's
  current behavior documentation.
- A spec is being authored and refers to a standard (RFC, schema,
  protocol) the project hasn't read recently.

## Source ranking

When two sources disagree, prefer in this order:
1. Official upstream documentation for the exact version in use.
2. Official upstream source code (especially public API surface,
   examples directory, CHANGELOG).
3. Official upstream blog posts and migration guides.
4. Security advisories from trusted bodies (CVE, CISA, OWASP,
   official upstream advisories).
5. Well-maintained community resources with current dates.
6. Recent blog posts from credible authors.
7. Anything else, marked clearly with reliability `community` or
   `mirror`.

Never cite a forum answer older than a year for a fast-moving
library without verifying against current docs. Never paste a forum
answer into the wiki without testing it.

## Workflow (per source)

### 1. Identify

For each source you intend to ingest, note:
- Authority (who maintains it).
- Version coverage (which versions of the library/spec it covers).
- Date (when it was last updated upstream).
- License (whether snapshotting is allowed).
- Slug (the filename you'll use locally).

### 2. Fetch

Use the host tool's web-fetch capability. If a documentation MCP
server is configured (Context7, DeepWiki, `llms.txt` provider,
similar), prefer it for fast, version-aware retrieval. The MCP
server does not replace the wiki; it just gets you upstream content
faster than crawling.

### 3. Snapshot (when allowed)

When the license permits, write the raw content to
`docs/graph/sources/raw/<slug>-<retrieved-date>.<ext>`. Acceptable
extensions: `.md`, `.html`, `.pdf`, `.txt`, `.json`. Strip nothing
from the raw file — preserve provenance.

### 4. Normalize

Produce `docs/graph/sources/normalized/<slug>.md`:
- Clean Markdown, no navigation chrome, no ads, no tracking
  pixels, no boilerplate footers.
- Keep upstream headings; drop everything else that is not
  decision-relevant.
- At the top, the metadata block:

```markdown
---
source-title: <title>
source-url: <url>
source-maintainer: <name>
source-version-coverage: <e.g. "1.4 - 1.6">
retrieved: YYYY-MM-DD
license: <SPDX or "see source">
reliability: official | community-trusted | community | mirror
---
```

### 5. Register

Add a row to `docs/graph/sources/index.md`:

```
| <title> | <url> | <maintainer> | YYYY-MM-DD | <version> | <reliability> | <relevance> | <one-line notes> |
```

### 6. Hand off to the wiki

Notify `docs-librarian` that new normalized sources are available
so they can integrate them into the relevant wiki page in
`docs/graph/libraries/`.

## Documentation MCP servers (when available)

If the project has any of these configured, prefer them for
fetching upstream content:

- **Context7** (`@upstash/context7-mcp`): current docs for many
  libraries, addressable by library ID and version. Use the
  library-ID form for precision.
- **DeepWiki**: open-source repository summaries.
- **`llms.txt` providers**: projects that publish a
  machine-readable docs index.

When you use one, cite the source in the normalized file's
metadata with the MCP server name and the date.

The local wiki is still authoritative for the project. The MCP
server gets you upstream content faster; the wiki page is your
distillation of what this project actually does with that content.

## Disagreement handling

If two sources disagree:
1. Note the version coverage of each.
2. Prefer the more recent official source.
3. If a security advisory disagrees with the docs, the advisory
   wins.
4. If the disagreement persists, record both with their versions
   in the wiki page, and open a question in grill.md §12.

## Source reconciliation (lightweight drift check)

Between full research passes, run a cheap periodic reconciliation: diff
the currently-resolved dependency versions and manifests/locks against
the versions recorded in the library wiki, **without** re-running research
or re-fetching upstream. Classify each line:

- **no mismatch** — the wiki pin still matches what resolves; nothing to do.
- **refresh before the next API-affecting change** — the pin has drifted
  but no work is about to touch that surface; flag it, don't re-ingest yet.
- **superseded — treat as historical** — the recorded version is gone from
  the resolved set; mark the wiki content as historical.

This catches silent pin drift that accumulates between full passes, at a
fraction of the cost. It is distinct from a full research pass (which
re-fetches and re-normalizes upstream content) and from
`validate-knowledge` (which tests whether the wiki *prose* is navigable
and correct, not whether its pins are still current).

## Anti-patterns

- **Ingesting paywalled or login-walled content** without the user's
  explicit OK.
- **Paraphrasing past the point** where the paraphrase still says
  what the source said.
- **Skipping the version pin.** "Latest" is not a version.
- **Snapshotting forbidden content.** When the license disallows
  snapshotting, link only; do not store.
- **Ingesting from one source per topic.** For non-trivial topics,
  cross-check against the source code.

## Reference files

- `docs/graph/templates/library-page.template.md` — where this skill's output
  ultimately lands.
- `docs/graph/protocols/ingest-library.md` — the parent protocol.
- `docs/graph/agents/10-research-scout.md` — the agent that runs this.
- `docs/graph/skills/library-wiki.md` — the wiki-maintenance skill.
