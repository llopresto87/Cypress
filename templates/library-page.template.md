<!--
Template: library-page.template.md
Authored by: docs-librarian, research-scout
Lives at: docs/graph/libraries/<library-name>.md
Used: on every new dependency or version refresh
Filled by copying this template into the target path. Fill §0–§3 on
creation; §4–§12 are demand-grown — add a section's body only when a
real fact exists (a bare page with an honest pin is a valid start;
never write "none" rows to look complete). Keep every section heading,
and never renumber them; agents and tooling index into them.
-->

# Library: <name>

## 0. Pin

- **Name:** <canonical>
- **Version:** <exact>
- **Ecosystem:** npm | PyPI | Go module | Maven | Cargo | OS pkg | container | RFC | spec
- **License:** <SPDX>
- **Maintenance signal:** <"healthy: last release N days ago" | "stale: …" | "archived">
- **Last reviewed:** YYYY-MM-DD by <agent>

## 1. Role in this project

One paragraph. Why this project uses this library and which capability
it provides. If we could be using a different library for this, say so
in §11.

## 2. Install

The exact command(s) run by `docs/graph/runbooks/local-development.md`:

```sh
<install command, with version pin>
```

If installation requires steps beyond a package manager (system
packages, post-install scripts, environment variables), record them
here and cross-link to the runbook.

## 3. Used API surface

The narrow slice of the library's API that this project actually uses.
**Not** a copy of upstream docs — just the names we touch and the
shapes we depend on.

```
<module>.<name>(<args>) -> <return type>   # used in src/<path>
<module>.<class>                            # used in src/<path>
```

When a new file starts using a new name, add a line here.

## 4. Project idioms

How we use this library *in this project*. The idioms we've adopted
and want kept consistent.

```pseudocode
# Idiom: <name>
# Use when: …
# Rationale: …
<short snippet>
```

If a new idiom is invented during an increment, file it here after
the test goes green.

## 5. Pitfalls and sharp edges

What goes wrong. Each entry dated.

- **YYYY-MM-DD — <short title>:** what bit us, what we do instead.

## 6. Deprecations in this version

What the upstream marks deprecated in the pinned version. What we do
about each one.

## 7. Security

- **Advisory feed:** <link or query>
- **Known CVEs affecting this pin:** <list with severities, or "none">
- **Watcher:** <agent / human / automation>

## 8. Upgrade path

- **Previous pin we ran:** <version>
- **What changed between previous and current:** <summary of CHANGELOG entries that affected us>
- **Next pin we are watching:** <version> — <reason to track>

## 9. Performance & cost notes

Relevant numbers we've measured for this library in this project
(latency, allocation, token cost, rate limits).

## 10. References

Sources used to build this page. Cite — do not paraphrase upstream
text verbatim.

- Official docs: <URL> — retrieved YYYY-MM-DD
- Source: <URL> — retrieved YYYY-MM-DD
- Release notes: <URL> — retrieved YYYY-MM-DD
- Security advisories: <URL>
- Other: <URL>

Raw snapshots in `docs/graph/sources/raw/`; normalized summaries in
`docs/graph/sources/normalized/`; index in `docs/graph/sources/index.md`.

## 11. Alternatives considered

If we evaluated other libraries for the same role, list them with the
reason each was rejected. Cross-link to the ADR that recorded the
choice.

## 12. Changelog

- YYYY-MM-DD — created, pin <version>, by <agent>
- YYYY-MM-DD — added idiom <name>
- YYYY-MM-DD — pinned <new version>; CHANGELOG diff in §8
- YYYY-MM-DD — recorded pitfall <name>
