# CYPRESS: placing corpus pages in a plant

Since 8.0.0 a plant can take single pages from the seed's library, skill
and tool corpora by naming them. A placed page gives the plant a
version-aware page it can work from without a research pass. Nothing is
placed by default: the owner confirms a list, and the installer places that
list and records it.

The commands and output below come from `./install.sh --help` and from runs
on a temporary project at seed `efd75fe`. The contracts are SPEC-0001 §4 and
§6 "Selective placement"
([SPEC-0001](../docs/specs/SPEC-0001-install-placement.md)). What each
corpus holds is in the
[corpora reference](corpora-and-integrations-reference.md#a4-inventory).

---

## Step 1: ask what matches

```
./install.sh <host> --expertise propose --project-dir <project>
```

The installer runs `tools/corpus-match.py` from the seed over the
project's manifests and prints one line per matching page. It writes
nothing, not even a stamp. For a project whose `requirements.txt` lists
`fastapi==0.115.0`, `pydantic>=2` and `redis`:

```
library-corpus/language/python  requirements.txt: (present)
library-corpus/pypi/fastapi  requirements.txt: fastapi==0.115.0
library-corpus/pypi/pydantic  requirements.txt: pydantic>=2
library-corpus/pypi/redis  requirements.txt: redis
tool-corpus/ops/resolved-dependency-gate  stack: library-corpus/language/python
```

A library line names the manifest entry that matched. A skill or tool line
names the library page its `stack:` field points to, so it is proposed
because that library matched.

The matcher reads the direct dependencies each manifest declares. It does
not read lockfile transitives, and it skips scratch copies, host
directories, nested plants and symlinked directories. A language page
matches by the declaration of the language, and a `cli` or `platform` page
by its named trigger files, images, Actions or hook ids. An unreadable
manifest is named on stderr, and the run still exits 0.

The matcher reads names, not need. It can propose a page the project only
cites, and it never proposes a page no manifest names, such as a cloud CLI
a script calls. Strike the ids you do not want and add the ones it missed.

## Step 2: place the list

```
./install.sh <host> --expertise <id>[,<id>...] --project-dir <project>
```

A corpus id is the page's seed path without `.md`:
`library-corpus/<key>/<name>`, `skill-corpus/<key>/<name>` or
`tool-corpus/<category>/<name>`. The installer places exactly the pages
named, whether or not a manifest matched them:

| Corpus | Lands at | Provenance |
|---|---|---|
| library | `docs/graph/libraries/<name>.md` | first line `<!-- origin: corpus@<seed version> id: <corpus id> -->` |
| tool | `docs/graph/tools/<name>.md` | the same first line |
| skill (stack-keyed pages only) | `docs/graph/skills/<name>.md`, a routable skill node | frontmatter `origin: corpus@<seed version>` |

```
$ ./install.sh claude-code --expertise library-corpus/pypi/fastapi,tool-corpus/ops/resolved-dependency-gate --project-dir /tmp/ep
...
[seed] placing the corpus pages recorded or listed for this plant (--expertise)
[seed]   docs/graph/libraries/fastapi.md  (library-corpus/pypi/fastapi, corpus@8.1.0)
[seed]   docs/graph/tools/resolved-dependency-gate.md  (tool-corpus/ops/resolved-dependency-gate, corpus@8.1.0)
```

The legal and agent corpora are not placed this way. The legal corpus keeps
its whole-or-none choice, `--legal-corpus`.

### What the installer refuses

Before the first write, the installer refuses, by name:

- an id that names no page;
- an id holding `..` or starting with `/`;
- two ids that share a destination, such as `pypi/redis` beside
  `container/redis`;
- an id whose destination another recorded id owns;
- an id that would land on a node or leaf the seed places itself.

```
  pypi/nope: names no page under library-corpus/, skill-corpus/ or tool-corpus/ (an id is <corpus>/<key>/<name>, without .md; the legal and agent corpora are not placed this way)
Fix the list (`install.sh <host> --expertise propose` prints the ids this
project matches) and re-run. Nothing has been written.
```

## The record, and later installs

Each placed page is recorded in `.cypress/seed.json` under the key
`expertise`: its id, its path and the SHA-256 of the bytes written, sorted
by id.

```json
[
 {
  "id": "library-corpus/pypi/fastapi",
  "path": "docs/graph/libraries/fastapi.md",
  "sha256": "c433c14ce95077d78c4cc2cecbddc8270b75a5e237b74d2b050c9f1e2098f3a8"
 },
 ...
]
```

A plant that never used the flag has no such key. A later install places
every recorded page again from the running seed, together with any id the
run adds:

- A page still equal to its recorded hash is replaced, with a backup, only
  when the seed would write different bytes.
- A page the plant edited, or a plant-owned page that was there first, is
  left byte-identical and named in the log for graft Phase 4.
- No run removes a recorded id or deletes a page. A page the seed later
  withdraws stays in the plant, and the installer warns instead of placing
  it again.

`install.sh <host> --check` names each recorded page that is missing or
stale and fails on either. An edited page is named but does not change the
exit code:

```
[seed] --check: expertise page docs/graph/libraries/fastapi.md (library-corpus/pypi/fastapi) was edited by the plant; left for graft Phase 4 to merge the corpus's newer layer into it
[seed] --check: no recorded expertise page is missing or stale; the 1 plant-edited one(s) above wait for graft Phase 4.
```

## Where the protocols use it

- [grow](protocols-reference.md#grow) runs both steps before it pays for any
  retrieval: it proposes the list, and the owner confirms it.
- [graft](protocols-reference.md#graft) treats the recorded list as an owner
  decision that silence keeps, and refreshes it.
- [ingest-library](protocols-reference.md#corpus-first-ingest-librarycorpus-first)
  checks for a placed page first. When one exists, it skips the scout and
  pins only the version delta against the plant's lockfile.

## The `stack:` field

A skill or tool page links to the library it serves through a `stack:`
field that names library corpus ids. A stack-keyed skill page lives at
`skill-corpus/<key>/<name>.md` under a key the library corpus defines,
carries node frontmatter plus `stack:`, and gets its `origin:` line only
when it is placed. A flat skill page carries no `stack:` and is not placed
by this flag. A tool page may carry `stack:`, and only a tool page with the
field can be proposed. `tests/seed-lint.py` checks the field on every
corpus page.

## See also

- [INSTALL.md](../INSTALL.md): the installer's flags.
- [What's new in 8.0 and 8.1](whats-new-8.md).
