## §8 Review round 3 — and where the loop converged

Round 3 confirmed all ten round-2 fixes and found six more things. The pattern
across three rounds is worth naming: **every round found the previous round's
fix to be narrower than the class it claimed**, and never in the same place
twice.

### The one that would have broken CI on arrival

`${corpus@Q}` is a bash 4.4 parameter transformation. macOS ships bash 3.2, and
this release added a CI matrix that runs the gate on macOS. It sat in the branch
that repairs a corrupted stamp — so on the mac leg, the code that exists to
handle a damaged record would itself fail with "bad substitution". Plain quotes
now. This repo already avoids `mapfile` for the same reason, with comments
saying so, and the construct got in anyway.

### Checks narrower than the class they name, again

- **Preflight reached one directory level.** `adapter_dirs()` lists `.claude`,
  `.claude/agents`, and so on; a read-only `.claude/skills/library-wiki/` or
  `docs/graph/protocols/` fell through to `ensure_dir`'s late check — a clean
  error, but only after the kernel and most of the graph were on disk. A
  list-driven check cannot keep preflight's promise that a refusal writes
  nothing. It now walks the directories that actually exist under the target, at
  any depth, before the first byte.
- **M1 completeness covered claude-code only.** Dropping
  `.prime/agent/APPEND_SYSTEM.md` or `opencode.json` left the suite printing
  "OK — 376 destinations". Now every adapter's machinery is enumerated.
- **The templates regression crashed instead of reporting.** `find` on a missing
  directory fails the pipeline under `pipefail`, so `set -e` killed the test
  before its own `M1 VIOLATED` diagnostic could print: exit 1, **zero bytes of
  output**. A test that fails without saying why is barely better than one that
  passes.
- **Partial stamp corruption was invisible.** The check fired only when the
  whole file was unparseable. A crash mid-write leaving `"legal_corpus": "ye`
  kept version and tools intact, so a recorded decision reset to `undecided`
  looking exactly like a fresh plant. The stamp is now handed to a JSON parser
  rather than inferred from which fields came back empty.

### A passing run that printed FAIL

`tests/test_gate_registry.py` ran the real 34-entry registry against a two-line
fixture `run.sh`, so every **clean** gate run emitted ~30
`!! registry lists X but run.sh no longer runs it` lines and a
`gate-registry: FAIL` banner as routine noise. Not a false green — the suite
still turned genuinely red — but a passing run that prints the word a reader
scans for teaches them to skim past it, and defeats any `grep FAIL` wrapped
around the gate. A clean run now contains **zero** occurrences of FAIL.

### Where a reviewer's finding turned out not to be ours

Round 3 reported two confident-wrong routes as surviving the bigram work:
`"this shelf is not load bearing, it's just decorative"` and `"single source of
truth for customer data"`, both HIGH to `devils-advocate`. Checked against
`d7588e2`: **both route identically at baseline.** They are a standing property
of a lexical router whose triggers contain ordinary English idioms, not a
regression this release introduced, and `from scratch` is HIGH in both versions
too. The bigram feature restores a case the fragment discount broke and adds no
new confident-wrong; the one it did add (`design time`) is closed.

That check is the reason to keep a baseline copy around. Without it the honest
answer and the flattering answer are indistinguishable, and the flattering one
here would have been "we introduced these".

### Convergence

Three rounds, each finding real defects in the previous round's work, and the
count per round fell — nine, then six, then six of which two were cosmetic and
one was not ours. The loop is not finished in the sense that nothing remains;
it is finished in the sense that the remaining findings are about the *limits*
of the mechanisms rather than defects in them: a lexical router cannot
disambiguate senses, a lexical overlap floor cannot establish provenance, and a
preflight cannot enumerate a directory that does not exist yet. Those are
written down where the mechanism is, not carried as open work.

---
