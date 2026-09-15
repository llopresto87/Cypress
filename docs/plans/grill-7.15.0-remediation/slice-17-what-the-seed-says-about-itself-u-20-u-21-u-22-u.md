### Slice 17 — What the seed says about itself (U-20, U-21, U-22, U-24)

**Tier:** T2. Restatement only; no mechanism changed.

**U-20 — agnosticism narrowed to what is true.** The machinery is stack-agnostic;
the shipped corpora are not. `library-corpus` is 81 pages of which nuget + maven
are 43 (**53%**), a .NET/Java estate. `legal-corpus/national/` carries exactly
one jurisdiction (`it`). The claim now scopes itself to the machinery and states
what an adopter on another stack actually receives — including the fact, verified
against `install.sh`, that the library corpus does not install into a plant at
all (only the legal corpus has a placement path).

**U-21 — two claims separated.** The stated motivation is API drift across
versions; the shipped pages are version-durable and unpinned. Those are different
artifacts making different promises, and each is now attached to the one that
delivers it: durable orientation from the shipped corpus, version-pinned and
lockfile-validated pages from a plant's own `ingest-library` run.

**U-22 — inventory drift, and one omission that was not a count.**
`documentation/agents-reference.md` was missing the `legal` agent **entirely** —
absent from the summary table, the delegation edge list, the model-class counts
and the per-agent sections, while the file said "18 agents" and the roster has
had 19 since 6.12.0. That is not a stale number; it is a specialist a reader of
the reference would not know exists. Also corrected: the ADR list (cited
`0001..0004`, disk has six), three corpus inventory tables (tool-corpus 7→14,
agent-corpus 5→7, skill-corpus 4→11), and the `--eval` methodology block, which
still described one blended "100% top-1" figure over 58 rows.

**U-24 — the host capability matrix.** `documentation/host-capability-matrix.md`:
12 capabilities × 5 adapters, every cell one of ADR-0003's six classes, each
derived from `install.sh`'s five installers and the integrations' own config
rather than from prose. It records the two facts that "tool agnostic" was
hiding: github-copilot pays **121 543 bytes (~30 400 tokens)** of eager context
against ~24 557 elsewhere and is classified **degraded**, not at parity; and
prime-agent enumerates no static roster at all, so specialist discovery there is
a different mechanism rather than a missing one.

### Cross-boundary defects this work surfaced

Four defects were reported by an agent that did not own the files. Three were
real and are fixed here:

- `integrations/codex/config.toml.example` registered 13 of 14 skills
  (`humanizer` missing) while `integrations/codex/README.md` claimed it "shows
  the full set". Fixed and verified: the example and the generated snippet both
  parse as TOML and carry 14 entries.
- `agents/01-architect.md` still framed `legal` as a role to withdraw from the
  corpus "if the roster lacks it". The roster has not lacked it since 6.12.0.
  The genuine constraint is different and is now what the charter says:
  architect's `delegates_to` is `tester` and `research-scout`, so the default
  path is a **handback naming `legal`**, not a spawn.
- `CLAUDE.md`'s gate count drifted twice inside the session that was editing it —
  23, then 24 — which is precisely what a count in prose does. It no longer
  states one; it points at `gate-registry.py --summary`, the thing that derives
  it. The same treatment was applied to the fixtures-only figure beside it.

The fourth (`manifest.json` missing two templates) was already closed in slice 12.
