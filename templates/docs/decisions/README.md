# Architecture Decision Records

Each non-obvious technical decision lives here as
`adr-NNNN-short-slug.md`, using `templates/adr.template.md`.

Numbers are monotonic. To replace a decision, write a new ADR with a
new number whose frontmatter `status:` is `accepted` and set the old
ADR's frontmatter to `status: superseded` + `superseded_by: ADR-NNNN`.
Status lives in frontmatter only (the schema's lifecycle vocabulary:
`proposed | accepted | open | deferred | hotfix | rejected | superseded |
closed`); the `## Status` body section is a pointer. List open and
hotfix decisions with `python3 docs/graph/status-register.py --by-kind adr --open --hotfix`.

## Index

<!--
The Status column mirrors each ADR's frontmatter `status:` (the single home is
the ADR). Regenerate this table with
`python3 docs/graph/status-register.py --by-kind adr` rather than editing it
by hand; a hand-edited status here is a second home and will drift.
-->

| # | Title | Status | Date |
|---|---|---|---|
