## 7.26.0 — a harvest: the gates a grown plant proved wrong, and two corpus entries fetched from their publisher (2026-09-22)

A mature plant was harvested back into the seed. What follows is the generalized
residue: no plant identity, no stack, no counts belonging to any project.

**The full gate was red on a non-Linux steward's machine, and had been.** Three
suites failed, and none of them in shipped behaviour. Two built their fixture
root with `mktemp -d` and compared that unresolved path against a value the code
under test deliberately canonicalises, so a symlinked temp root made a correct
answer look wrong; both now resolve the root where they create it. The third
captured a count through a `wc -l` that right-aligns on BSD, which the seed
already guards against in about twenty places across seven suites — that one was
the exception, not a missing rule, so it gained the existing idiom and no new
doctrine.

**`prose-lint` §19 contradicted the templates the seed ships.** A mandated
metadata block and the Given/When/Then contracts `spec-lint` requires are
written in exactly the bullet shape §19 watches for, so two shipped tools
disagreed over the same bytes and the losing side was the one with a spec. The
detector now separates the genres the way `mask()` already separates a table
from prose: a record's field does not close as a sentence, and a bold-label run
that does is still caught. The planted positive in the fixtures is untouched.

**A router floor asserted a safety margin it did not have.** Its comment claimed
tightening carried no risk to any installed project, while the floor is scored
against the roster a project has grown — so the first specialist a project adds
could take the gate down. The floor is now keyed to the roster it was measured
over, mirroring how the routing spec already keys its class floors to a corpus
that declares classes. **The recorded value did not move**; scoping is not
loosening, and nothing was blessed.

**A plan may no longer cite a decision that is filed nowhere.** The plan linter
already resolved library and contract citations in both directions; decisions
were the one identifier nobody checked, and the rule sat in a skill's list of
"judgments the lint cannot make" while naming only the direction that is
genuinely judgment. The mechanical direction is now a check beside its two
siblings, and the skill keeps a pointer rather than a second statement. A
decision not yet accepted is filed with the status that says so.

**Audit tools that reported the wrong defect.** A malformed citation was
reported as a missing file; a snapshot check reported a file it never looked
for; a token audit matched inside ordinary words; a schema check could not tell
a re-authored contract from a dropped one; an ordering prefix made a plant's
experts fail a name rule the seed's own roster does not obey; a graft audit's
day-granular date could not separate a run from its same-day remedies; a
preserved configuration value lost the comment that explained it; a drift gate
compared its own backups and was therefore unpassable after its first run. Each
is a code fix with a regression test, and each left the doctrine where it
already lived.

**An agent may now declare that one of the collections it reads has no subject
here.** A role that reads several collections got one verdict for all of them,
so a project holding the subject of some and not others had no honest status to
record. Absences are now per-collection, each carrying the reason and the paths
that establish it, under the same evidence bar as any other status.

**Two of these fixes make a gate quieter**, which is the shape of a weakened
gate and is said plainly here for that reason: a check that reported a file it
had never looked for now looks, and a name rule that failed an ordering prefix
now strips it. Both were reporting things they had not established. Neither
narrowing is taken on trust: each arrives paired with the case that fires the
gate on the genuine defect, so what shrank is the false positive and not the
catch. Remove the snapshot and the first still reports, with the resolved path
a reader can list; declare a name that disagrees with its file for real and the
second still fails. A narrowing whose true-positive half is not asserted in the
same change is a weakening with better manners.

**Doctrine the plant's operations proved, and the seed did not own.** A gate
found incapable of failing never worked, so the window in which its verdict
meant nothing is recorded beside it and the increments it appeared to authorize
can be re-read. A negative result is evidence about the subject presented, never
about a fresh equivalent submitted after it. A safety property held only because
a capability is missing is conditional, not structural. A component that redacts
a credential from its own output has made a claim about one channel and none
other. An alert nobody receives and no alert at all are the same outcome. A
recorded non-upgrade carries the condition it rests on and is re-measured before
that condition lapses. A page claiming a dependency is current names the version
and the support phase; those are two claims.

**Runbook templates gained the shapes an operator had to invent.** A preface
naming the facts that decide how the generic incident loop runs here; a closing
section recording the capabilities the operator does not have, each naming the
promise it shrinks; and, where a reversal capability does not exist at all, the
ordered chain of preconditions that would let it be written — so the gap is a
decision with an owner instead of a blank. A gate asserting artifact identity is
expected to go red after a correct reversal, and the expectation is edited in
the same change rather than widened to accept anything.

**Corpora.** One reusable-tool page (a blueprint, no script: the portable
implementation would need its own configuration parsing, and the corpus admits
an implementation only when it is self-contained); two one-sentence fold-ins
into pages that already owned their subject. A suggested-expert catalog entry
was drafted for a standing weakness register and then **withdrawn**: an
independent review found the boundary it drew against the offensive-security
role contradicted that role's own file, which already owns reachability, the
per-hole regression test, and ownership to a re-attacked close. The one idea
that was genuinely net-new — a hunting index, held beside the threat models and
the risk register, recording what to try next and what a proof would look like
rather than what is true or what is planned — landed in that existing role
instead. A ruled-out entry is kept, because the paths already walked are the
ones re-walked when nothing records them.

The seed also had no withdraw formula for its suggested-expert catalog at all:
three nodes told a session to check the corpus and none said where a page
lives, so every page in it was reachable only by a session that already had the
seed. The consuming node now states the path, as it already did for the two
other corpora it withdraws from.

**Two legal entries, both fetched from the official publisher in this pass.** A
provision on national identification numbers was extracted from the original and
the consolidated edition and compared character by character before it was
recorded, so the amendment trap is closed for it by evidence; its status came
from the publisher's own metadata. A supervisory-guidance opinion was retrieved
in full, its quotations anchored to numbered sections and pages, and its status
recorded as the open question it is — neither carried forward nor repudiated by
the successor body — rather than resolved by preference. **No existing grade was
upgraded.** A recorded retrieval blockage was found stale in the helpful
direction and recorded as such; the entries it affects keep their grades until
each is re-read on its own date.

**The library corpus took nothing.** Every candidate's durable core sat in the
sections the durability gate names as rejects, and stripping the version labels
off a migration diff does not make it durable — it makes it an undated migration
diff, the same fact with its provenance deleted.

**The seed's own release gained a mechanism.** A version shipped by hand-tagging,
and nothing published a GitHub Release when it did. `tools/prepare-release.py` —
seed-only, absent from the plant-facing manifest — now stages
`.github/RELEASE_NOTES.md` from this entry's own text, taken verbatim rather
than redrafted: the entry already passed canonize's humanizer pass, and a second
draft for the same reader would be a second home for one fact.
`.github/workflows/release.yml` reads that staged file when a `vX.Y.Z` tag
matching `manifest.json`'s version is pushed, and hands it to `gh release create`
unedited — it authors nothing, since CI has no access to the judgment
`skills/humanizer` and `skill-corpus/discardme.md` both require. The staged file
is discardme-shaped: produced at commit time, consumed by the pipeline,
superseded rather than deleted by the next version's run. Publishing the tag
stays a human decision, the same as any other push.

### Landing this in a project

Two new checks can turn a currently-green project red, correctly: a plan citing
a decision that was never filed, and a library index whose rows do not register
their pages. A machinery upgrade installing a rule a graph has never been linted
against is not the project's fault, so both now share one staged-adoption mode.
The plan linter already had `--warn`; the graph linter gains it here, with the
same meaning in both — every finding printed in full, exit code held back, the
check itself untouched. A window is the honest way to buy time; a quieter check
is not. Run the plain form once the window closes, since a gate left in `--warn`
is a gate that cannot fail. The pending-section vocabulary that decides whether
an index row registers a page is stated in the graph schema.
