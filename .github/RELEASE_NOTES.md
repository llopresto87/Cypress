## 8.6.0 — the source index reads more languages, from a harvest (2026-11-11)

This release folds back what a grown plant learned. The largest part is the
source index: it now reads links in several languages that until now got only
`language-not-read`. The library, skill and legal corpora gain pages and
depth, two doctrine lines and one template note are new, and a graft-run race
that the round's gate found is fixed. The owner decided on 2026-11-11 that the
seed's test doctrine, and everything else about tests, comes first and stays
as it is. The harvest's test-related proposals were saved for a later decision
and none was implemented.

The kernel is still 7043 bytes, and no always-loaded file changed.

### The source index reads the stack languages

The owner decided on 2026-11-11 that the language readers a grown plant built
for its own copy of the index ship in the seed. This amends SPEC-0007, which
had said the index would never read other languages. The readers sit together
in one module with no CLI, `tools/source_readers.py`. `source-index.py` loads
it by path from beside itself, and its bytes are part of the cache key.

- **Links:** Java imports, same-package type references and classpath
  resource names; Thymeleaf `th:replace`, `th:insert` and `th:include`
  fragments and the Java strings that name a template; YAML scalars, with
  Compose `build`, bind-mount `volumes` and secret `file:` keys; Dockerfile
  `COPY` and `ADD` sources; and nginx `include` paths mapped through the
  Compose bind mounts. A reader links only a path the inventory holds, so a
  library import or a container path makes no record.
- **Symbols:** Java types and SQL `CREATE` names are read line by line and
  are `maybe`. A SQL file defines names and links nothing.
- **What stays unread:** a language with no reader, such as Go, Kotlin, C# or
  Ruby, still answers `language-not-read`. The next reader is a new module or
  a new section of this one, and it waits on the owner's decision.
- **Proof:** eight new SPEC-0007 contracts, each held by a case seen red with
  the module absent. The installer places the module at
  `docs/graph/source_readers.py`, and graft's audit counts it among the
  delivered tools. Two existing lines in the source index's test file moved
  with the tool: its list of sibling modules, and the copied text of the line
  that says what `symbols` read. What those cases check is unchanged.

### Corpus depth

- **Skill corpus:** a new page, `pre-compaction-session-save`. Before a
  compaction that comes ahead of close-out, the session writes what only the
  conversation holds into its session record by a fixed list: the facts no
  handback placed and the environment facts the owner gave. The write is
  pointer-only, has a size cap and can run twice safely, and the session
  rereads the record afterwards. `protocol.canonize` points at it. The skill
  corpus README lists it under a new heading, "Sessions and continuity".
- **Skill corpus:** `deploy-fleet-on-remote-docker-host` gains two traps
  observed in practice. A tar stream over ssh that a short timeout cuts stops
  without an error, so count the files on the host after each export. A
  background job that keeps ssh's output open makes the call hang, so detach
  it with every descriptor redirected and poll it in a second call.
- **Library corpus:** nine pages gain pitfalls and observed behaviours across
  the container, language, build-ecosystem and command-line keys. Each fact
  is marked as confirmed upstream or observed, and one is marked as read from
  a library's source without being run.
- **Legal corpus:** ten GDPR entries (material scope, five definitions, the
  Art. 6(4) compatibility test, the Art. 14(5) exceptions, the Art. 23(1)
  restriction objectives and the Art. 89(1) research safeguards); five
  case-law and regulator entries; and a new page for EDPB Guidelines 03/2026,
  a consultation draft, with six paragraph entries. Each was fetched again
  from its publisher this round and is marked UNREVIEWED, since no human has
  reviewed it yet. `legal-corpus/index.md` routes the new rows.

### Doctrine and templates

- **Cleanup on a shared host** (`delegation.wave-integrity`): a brief that
  lets a worker clean up on a shared host limits removal to what the spawn
  created and named itself. That means a name carrying the lane and spawn id,
  run with auto-removal, and never a prefix or a pattern, because a pattern
  also matches what other writers or the owner run there.
- **Design leaves:** `templates/docs/design/README.md` now says that a leaf
  there is never routed, even with node frontmatter, because graph lint scans
  only the node and machinery directories. The owning node reaches it through
  an `artifacts:` edge.

### graft-run survives Git's background repack

A commit in a plant can leave Git's detached auto-maintenance running, and
that maintenance can pack and delete loose objects while `graft-run` copies
the plant. When every copy error is a file under the plant's `.git` that
vanished, the copy now waits for Git's maintenance lock to clear (up to 30
seconds) and starts again, at most three times. Any other error is raised as
before. This was not a harvested lesson: the round's gate hit the race in an
existing graft-run case, and any graft run right after a commit could hit it.
It has no red case of its own, because adding one would change the seed's
tests, which the owner's ruling holds still. The existing case is its evidence.
`graft-run` runs from the seed and places nothing in a plant.

### What an existing plant does to receive this release

- **Re-install** places `source_readers.py` beside `source-index.py` and
  fast-forwards the seed-owned method and protocol nodes, keeping each
  replaced file as a timestamped backup.
- **Graft** brings `source_readers.py` as a delivered tool. A plant whose own
  copy of the index grew its own readers can drop them for the seed module.
- **Corpus pages** arrive by need: `--expertise skill-corpus/<name>` and the
  library page ids place a page, and `--legal-corpus yes` places the whole
  legal corpus again.
- **Shape:** nothing. The design README is a leaf the installer places only
  when it is missing, so an existing plant keeps its own copy, and no spec or
  plan form changed.

### Harvest log

```
# Harvest — from a grown plant — 2026-11-11
Harvested:   one tool module with its spec contracts and cases; two
             skill-corpus pages (one new); nine library-corpus pages;
             legal-corpus entries on two pages, one new page and its
             index rows; two
             doctrine and template rules. No plant identity.
Generalized: every plant name, domain, path, credential, host and port,
             every stack fingerprint and identifying count, every plant
             version and every security fact stripped; documented version
             facts about a library kept with their subject; test fixtures
             invented.
Rejected:    rows redundant with a home the seed already owns; owner
             preferences that are not project-agnostic rules; a question
             that cannot be stated without the plant's use case; library
             pages below the withdraw-ready bar; project scripts bound to a
             stack, a host or a project; a change with no seed need.
Deferred:    the test-related proposals, saved and not implemented, by the
             owner's ruling of 2026-11-11.
```

### Seed integrity gate (verdicts only)

- G1 agnosticism-floor: PASS
- G2 agnosticism-judgment: PASS
- G3 faithful-import: PASS
- G4 availability: PASS
- G5 plant-untouched: PASS
- G6 self-consistency: PASS
- G7 clean-install: PASS
- G8 prose: PASS, genre exception recorded for the legal pages
- G9 minimum-sufficient: PASS, ratified by the steward
- G10 provenance: PASS
- G11 no-loosened-limit: PASS
- Version bump: 8.5.1 → 8.6.0
