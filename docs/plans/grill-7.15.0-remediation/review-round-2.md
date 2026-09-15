## §7 Review round 2 — verifying the fixes, and what verifying them found

Two reviewers re-ran round 1's findings and kept hunting. **All six round-1
installer fixes held as described.** The routing fixes held for the attacks they
were written against and not for the next one, which is the more useful result.

### The worst of it: a feature entirely broken in one mode

`--legal-corpus yes --symlink` **died every time**, with
`ERROR: legal corpus placed partially (0 of 16 pages)`, while all sixteen pages
sat there correct as symlinks. The completeness check counted `-type f` only.
The check written to prevent a partial corpus was the only thing preventing a
whole one, and it left a half-installed target behind.

`place_tree` already carries the lesson in a comment — *"`-type l` is not
optional. Under `--symlink` the graph home is a tree of SYMLINKS into the seed,
so a bare `-type f` matches none of them"* — and this code repeated the mistake
at four separate sites. They are one guarded helper now, and the suite tests the
corpus under **both** link modes, which no test had ever done.

### The honesty instrument, attacked again

- **Substitution beat the overlap threshold.** Changing two words in a six-to-
  nine word trigger lands at 0.67–0.71, under the 0.80 line, while still routing
  HIGH and correctly. Four such rows moved the held-out headline from 2/17 to
  6/21 with no warning printed. The threshold is now **0.50, measured**: the
  seventeen genuine rows top out at 0.43 and the attacks start at 0.67, so the
  line goes in the gap between the two populations rather than at a round
  number. It is recorded in the code as a floor and not a proof — a lexical
  measure cannot establish how a sentence was written, and saying so is part of
  the fix.
- **Duplication beat the row floor.** One genuinely correct paraphrase repeated
  twenty times reported **20 of 20 confident-correct** and exited 0 — a perfect
  generalization score from a single example, worse than the padding trick it
  replaced. Rows must now be distinct. Three of my own tests broke on that
  guard, correctly: they had been appending tasks the corpus already carried.

### My bigram fix introduced a confident-wrong

`"double check the design time constants in the config file"` routed **HIGH to
`security`**. Traced exactly: `design-time` is a real compound only because
`pentest` writes it; once admitted, the prefix fold matched it against
`security`'s unrelated trigger word "design" and contributed the two points that
carried it from 12 (below FLOOR) to 14. The known-compound gate decided *whether*
a bigram scored at all and not *who* could be credited for it.

A bigram is evidence the router synthesized — the task wrote two words and we
chose to read them as a compound. It now matches only where it literally appears
and earns no rare-term bonus. A compound we inferred can confirm a route; it
cannot create one. That also returned a joke task
(`"multi agent negotiation between chefs, just kidding"`) from HIGH to its
baseline MEDIUM.

### Checks that were narrower than the class they named

- **M1 completeness enumerated only graph nodes.** Patching the installer to
  skip `.claude/bound-hook.py` — the PreToolUse guard, the one hard-enforced
  control in the system — left the suite green. It now covers the adapter
  machinery and the template subtree.
- **`ensure_dir` returned on existence, never writability.** A read-only
  *subdirectory* still produced a raw `cp: Permission denied` mid-install.
  Preflight now refuses it before the first write.
- **The spec test-mapping check only understood Python citations.** SPEC-0001's
  §10 cites shell check names in prose, so a fabricated row citing a real `.sh`
  file passed silently — the same "certifies coverage nobody wrote" defect, in
  the one authoring style the check was not built against. The rows carry a
  machine-checkable anchor (the invariant label they open with), and that is now
  required to appear in the file cited.
- **The gate registry still missed three spellings** — direct execution on the
  executable bit, an interpreter through a variable, a versioned binary. None
  appear in `run.sh` today, which is exactly why they matter: the failure is a
  future line nobody classifies and a tool reporting OK about it. It also had
  **no regression of its own**, having been fixed twice by hand;
  `tests/test_gate_registry.py` now holds all nine spellings and both refusal
  directions, and fails when the parser matches nothing at all.
- **A corrupt or hand-edited stamp** silently reset a plant's recorded decisions
  to `undecided`, and an out-of-domain value was carried forward for ever while
  the log printed "undecided" — the file and the message disagreeing about the
  record. Both are repaired and announced.
- **The kernel deviation notice could be bypassed** by a kernel file symlinked
  at something else: the flag required `! -L`, so the notice never fired.

### The shipped corpus itself is clean

An independent re-audit of all seventeen held-out rows, with a from-scratch
overlap measure, against every agent's triggers rather than only the expected
one, found **no further contamination** — highest 0.43, and the lowest-overlap
contract row is the one the tool already surfaces as an honest abstention. The
exploits are in the mechanism, not the data, which is the right place for them
to have been.

### A sweep I ran on myself, before round 3 asked for it

The bigram feature credits a task that writes a compound without its hyphen. So:
take **every** hyphenated compound the roster uses (60 of them), write each one
spaced into an otherwise neutral sentence, and see how many route confidently.

**26 of 60 did.** Most were correct — an agent's own name written with a space
(`agent topology` → `multi-agent-architect`, `growth scout` → `growth-scout`),
which is the feature working. The bad ones all came from the same place:
compounds that live only in an agent's **description prose**, where they are
metaphors rather than routing vocabulary. `devils-advocate` writes "load-bearing
claim" and "claim-bearing deliverable"; `pentest` writes "design-time threat
models". So "the claim bearing situation in the billing module" routed **HIGH**
to an adversarial reviewer.

An inferred compound is now licensed only by an agent's **name or triggers** —
the vocabulary it chose for routing — never by its prose. The sweep drops to
**21 of 60**, and the remainder are declared vocabulary. `claim bearing` and
`file upload` fall to LOW; `design time` was already fixed by the exact-match
rule.

Writing the test for this caught a second thing worth recording: my first
version pointed at the `design time` case, which the exact-match rule already
covered, so re-admitting prose left it green. A test that passes for a reason
other than the one it names is the same defect as a spec citing a test nobody
wrote, one layer down. It now points at `claim bearing`, which only the prose
rule fixes, and it goes red when that rule is reverted.

**What is left, and stated rather than fixed:** `load-bearing` really is in
`devils-advocate`'s trigger list, so "the load bearing situation" still routes
there. A lexical router cannot tell structural engineering from claim
verification, and the tool says so in its own banner on every invocation —
*"Router suggestion is a keyword heuristic — reason over it, not an oracle."*
That is the honest boundary of the mechanism, not a defect in it.
