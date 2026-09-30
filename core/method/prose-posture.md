---
id: method.prose-posture
tier: 2
kind: method
origin: seed
title: prose posture — prose a person reads is written by judgment — meaning governs style, the information contract is preserved, genre outranks generic advice
owns:
  - prose-posture.meaning-governs-style
  - prose-posture.information-contract
  - prose-posture.claim-classes
  - prose-posture.structure-carries-emphasis
  - prose-posture.genre-outranks
  - prose-posture.voice-as-constraint
  - prose-posture.diagnostics
  - prose-posture.anti-patterns
  - prose-posture.provenance-integrity
  - prose-posture.decision-rules
  - prose-posture.stop-conditions
requires:
peers:
  - method.engineering-posture
  - skill.humanizer
  - protocol.deliver
load_when:
  - "how should documentation, a report, a brief, or a memo read; what makes prose credible"
  - "is this sentence too strong for the evidence; may becomes will; correlation into causation"
  - "does this document need a conclusion, a key-takeaways box, a challenges section"
  - "which claims are facts, which are inferences, which are recommendations; claim classes"
  - "keep or remove a dash, a contrast, a list, a bold label; is this pattern doing work"
  - "should this be a list or prose; when to use a table; sentence case headings"
  - "do not fake a human voice; no planted typos, no detector chasing, no invented anecdotes"
  - "when to stop editing; difference is not improvement; over-editing stable language"
prevents: Prose written to a style rule instead of to its meaning, with the genre ignored and the information contract broken in the name of readability.
est_tokens: 4317
---

# Prose posture

Prose a person reads is part of the work product: documentation, README
text, ADR and spec bodies, runbooks, delivery summaries, pull-request
descriptions, briefs and reports for the owner. Its value depends on the
reader understanding and trusting it. This node holds the doctrine for such
prose. The procedure that applies it is the `humanizer` skill; the mechanical
floor is `docs/graph/prose-lint.py`. Instruction text a model reads follows
the voice rule of `method.engineering-posture` §8.

The job is not to make text perform "human" as a costume. The job is prose
that reads as the product of a writer who understands the subject, knows the
audience, has a reason for each paragraph, and revised with judgment. A
detector score, a perplexity figure, or a burstiness metric is never an
editorial objective.

## 1. Meaning governs style

Every stylistic choice serves meaning, emphasis, audience, or genre.

- Vary sentence length because different thoughts need different space,
  never to manufacture randomness.
- Replace a word when it is vague, inflated, repetitive, tonally wrong, or
  less precise than an alternative, never because a model uses it often.
- Keep any contrast, list, transition, dash, fragment, passive, or repeated
  opening that performs a clear local function. Remove the ones that do not.

Word lists and pattern catalogues are prompts to inspect context. None of
them is a ban.

## 2. Preserve the information contract

When revising supplied material, distinguish wording from substance.
Preserve, unless the owner authorizes a substantive change: facts, names,
numbers, dates, units, definitions, rankings, comparisons, conditions,
exceptions, causal claims, uncertainty, scope, quoted language, citations
and their attachment to a claim, legal or technical qualifications,
commitments and requirement levels, and explicitly stated opinions.

Keep every claim at the strength, breadth, certainty, causality, and scope
the source supports: an attributed claim keeps its attribution, a
correlation stays a correlation, an estimate stays an estimate, and "may"
stays "may" even where "will" would sound more decisive. A cleaner sentence
that changes the information contract is a failed edit.

Code, commands, flags, paths, URLs, configuration keys, identifiers, schema
fields, frontmatter, table data, and link targets stay byte-exact.
Required legal, compliance, or contractual wording is clarified around,
never rewritten. Modal distinctions (must, shall, should, may, prohibited)
stay exactly as written. Quotations stay exact.

## 3. Claim classes

Where evidence matters, each statement is one of: established fact
(directly supported by the material or an authoritative source),
attributed claim (a source says it; the document does not establish it),
inference (a reasonable conclusion from evidence), recommendation,
assumption (accepted to enable analysis), unknown, or contested (credible
sources disagree). Wording follows the class. A substantial rewrite whose
loss risk is material keeps a quiet claim ledger (item, source meaning,
required detail, class, destination, status) as a verification instrument,
not as a deliverable. When synthesizing several sources, agreement,
difference, and uncertainty stay distinguishable; a false consensus is a
fabrication.

## 4. Structure carries emphasis

An important point gets its weight from placement, evidence, stated
consequence, space, and its connection to the decision or task, not from
adjectives, boldface, fragments, or dramatic closers. Show why a fact
matters rather than calling it crucial.

Unevenness follows importance: give each section, list, and paragraph the
size its content needs (diagnostic G), and spend words where the reader's
uncertainty, risk, or decision difficulty is highest.

Every section answers a real reader question or performs a real function;
a heading that exists because a template usually has one is cut. Every
paragraph has one governing job (establish a fact, explain a mechanism,
interpret evidence, compare options, qualify, exemplify, state a
consequence, recommend, define, direct). Order follows reader need:
decision first for briefs, finding first for analyses, instruction first
for procedures, chronology only when the sequence itself explains the
subject. Repetition stays when it protects comprehension, precision, or
navigation (a technical term repeated to avoid an ambiguous pronoun, a
requirement restated where readers enter, a warning at the point of action)
and goes when a later sentence paraphrases the previous one for emphasis.

## 5. Genre outranks generic style advice

The same sentence can be right in a memo and wrong in API documentation.
Apply the conventions of the actual document type first. Defaults for the
genres this system produces:

| Genre | Prioritize | Do not |
|---|---|---|
| Technical documentation, README, runbook | task success, exact terminology, prerequisites, observable behavior, inputs and outputs, examples, failure modes, recovery, version and environment constraints | add flourish to a procedure; vary a canonical term for style; soften mandatory wording |
| Engineering and design records (ADR, spec, plan) | problem, constraints, current behavior, alternatives considered, decision, tradeoffs, interfaces, failure modes, migration, verification | dress a preference as an inevitability; blur "we chose" and "the system requires" |
| Delivery summary, executive brief | the decision or issue, why it matters to this reader, essential evidence, options or recommendation, risk, next action, early | fill with scene-setting the reader already has; list five next steps |
| Policy, procedure, protocol | scope, definitions only where necessary, requirements, responsibilities, exceptions, escalation, records | "humanize" away mandatory wording; mix modal verbs |
| Research or evidence summary, library page | question, source quality, consensus, disagreement, uncertainty, effect size, limitations | turn a mixed evidence base into a confident narrative |
| Proposal | problem, proposed change, rationale, scope, cost where known, tradeoffs, risks, implementation, success criteria | oversell; omit limitations |

Write for a specific reader, even an implied one: an operator's document
privileges action and failure conditions; an owner's brief privileges
decisions, consequences, evidence, and tradeoffs; an engineer's document
needs mechanisms, interfaces, and edge cases. Anything handed to the
owner expands project- or agent-internal shorthand (increment ids, lane
names, finding codes, spawn ids) on first use: the reader was not in
the session that coined it.

## 6. Voice is a constraint, not decoration

With a reliable writing sample, infer the system of choices behind it
(sentence length and range, clause density, openings, paragraph length,
punctuation habits, contraction rate, person, register, directness,
parentheticals, transitions, signposting, humor, confidence) and preserve
those tendencies where they do not conflict with accuracy or the task.
Match tendencies, not isolated quirks: a single dash or fragment
establishes no rule. Correct typos, duplicated words, malformed citations,
and formatting glitches; they are noise, not voice.

Without a sample, the default is direct, unshowy, specific, and comfortable
with ordinary language, inferred from document type, audience, subject, and
context. "Professional" does not mean inflated or bureaucratic. The plant's
`plant:` block in `docs/graph/index.md` names the `deliverable_language`
and `comment_language`; prose is written in the declared language.
Naturalness comes from those established choices; imitating imperfection is
a deception, bounded in §9.

## 7. Diagnostics

A pattern below warrants revision when it weakens meaning, rhythm,
credibility, or genre fit. The letters are the vocabulary `prose-lint.py`
reports beside the humanizer's numbered tells.

| | Diagnostic | Watch for | Repair |
|---|---|---|---|
| A | Staging instead of content | "Let's dive in", "Here's what you need to know", "The real question is", "At its core", "It is important to note", an opener that restates the heading | Begin with the claim, context, or action the reader needs. Keep signposting that navigates a genuinely complex argument. |
| B | Empty contrast | not X but Y; not only X but Y; this isn't about X, it's about Y; "rather than" where X was never a live option; the same contrast split across sentences | Keep a contrast when both sides inform or it corrects a plausible misunderstanding. Otherwise state the positive claim. |
| C | Inflated significance | pivotal, transformative, game-changing, crucial, profound, testament, enduring legacy, broader landscape, marks a new era; a stock "challenges and outlook" section; a send-off paragraph | Give the evidence, consequence, comparison, or decision that makes the point matter. End on the last concrete fact. |
| D | Generic authority | "experts agree", "research shows", "industry best practice", "widely recognized", "it is well known" without a source | Cite the authority, narrow the claim, or remove it. Never invent a source. |
| E | Corporate glaze | every noun an initiative, capability, opportunity, framework, journey, ecosystem, landscape, alignment, transformation, enablement | Name the people, systems, actions, constraints, and results. Keep canonical domain terms. |
| F | Abstract noun chains | "implementation effectiveness improvement planning" | Recover the actors and verbs. |
| G | Mechanical balance | exactly three items repeatedly; identically sized sections; First/Second/Third by reflex; a pro and con for every point; mirror-image paragraphs | Weight by actual information. |
| H | Repeated rhetorical architecture | broad claim, three examples, dramatic closer; concession, reversal, "ultimately" | One instance may be natural; repetition reveals a template. Change the form where the content asks for it. |
| I | Summary echo | a sentence or paragraph repeating the previous point in grander words; "That is the real win." | Cut it or replace it with a real implication. |
| J | False objection | "some might argue", "you may think", "it would be tempting", "one could simply" with no real stakeholder or option behind it | Remove imaginary debate. Keep real alternatives and objections. |
| K | Over-transitioning | Additionally, Moreover, Furthermore, On the other hand at the head of nearly every sentence | Improve the order; use fewer, exact transitions that name the relation. |
| L | Listification | prose broken into bullets because each sentence could be one | Bullets for scanning, steps, options, criteria, reference. Prose for causal, argumentative, interpretive, or sequential relationships. |
| M | Over-sectioning | a heading every paragraph or two | Merge sections whose headings are not distinct reader questions. |
| N | Formatting as emphasis | bold labels on every bullet, Title Case everywhere, callouts and "Key takeaway" boxes, emojis or arrows as decoration, a rule between every section | Formatting follows importance and the document's conventions. Sentence case by default. |
| O | Uniform cadence | many sentences of similar length, clause count, and opening | Repair the syntax only where meaning supports a different shape; never randomize. |
| P | Repeated subject openings | adjacent sentences opening with the same pronoun or noun by accident | Merge, reorder, or vary the subject. Keep deliberate anaphora. |
| Q | Dash dependence | dashes connecting nearly every elaboration, aside, or reversal | Choose the real relation: period, comma, colon, parentheses, conjunction, or a rewritten sentence. A dash that matches the voice and performs a useful turn stays. Overuse is controlled; existence is not banned. |
| R | Qualifier stacking | could potentially, might perhaps, arguably could, repeated scope disclaimers | Keep the minimum qualifier the evidence requires. Never strip real uncertainty to sound confident. |
| S | Empty intensifiers | very, truly, incredibly, highly, deeply, particularly when they change nothing | Keep an intensifier only when degree is part of the meaning and no measurement exists. |
| T | Missing actors | passive or nominalized constructions that hide responsibility | Restore the actor when the source establishes it and responsibility matters. Passive stays when the actor is unknown, irrelevant, or the object deserves emphasis. |
| U | Vague reference | this, that, it, these issues, the above, the latter with no immediate referent | Name the thing. |
| V | Premature conclusion language | ultimately, in conclusion, all things considered, the bottom line without a synthesis | State the conclusion itself. |
| W | Synthetic friendliness | Great question, The good news is, Don't worry, Luckily, You're all set | Remove it unless the voice and purpose call for it. |
| X | Meta-writing residue | "Here is a revised version", "As requested", "I hope this helps", "Let me know if", notes to self, placeholder commentary, unrequested explanations of the editing | Remove outright. It is the most certain tell and the easiest to miss when it wraps real content. |

These diagnostics are built on one language's vocabulary. On a document
written in another, run the tool for its language-independent checks only
(structural repetition, decorative formatting, heading density,
punctuation) and record every vocabulary-based finding as **inapplicable**
rather than clean. A silent detector there has reported that it cannot read
the document, never that the prose is good, and the two look identical in
the output. Where a genre or a companion skill *mandates* a shape (a
required field block that reads as repeated bold labels, a required title
or heading punctuation that inflates a whole-file dash rate), a
language-independent check also fires on the mandated structure and cannot
tell it from the tell it is named after. There the finding is advisory:
record why it was kept and leave the mandated shape.

Stock model vocabulary (`additionally`, `crucial`, `delve`, `enhance`,
`fostering`, `highlight` as a verb, `interplay`, `intricate`, `key` as an
adjective, `landscape` as an abstraction, `meticulous`, `pivotal`,
`showcase`, `tapestry`, `testament`, `underscore` as a verb, `valuable`,
`vibrant`) is a prompt to inspect the sentence (§1); a formal word outside
the list is not a tell by itself, and technical uses of words like `gate`
or `robust` are not tells.

## 8. Anti-patterns of editing

Most failed editing strategies are the sections above read in reverse:
synonym roulette (§1), detector chasing and planted imperfection (§9),
random burstiness (§1, diagnostic O), universal word or punctuation bans
(§1; dashes, semicolons, parentheses, and colons carry relationships and
voice, so control overuse, not existence), fake confidence (§2), and
template completion ("Challenges", "Future outlook", "Key takeaways", a
conclusion because templates have one: §4). Five have no other home:
maximal contraction; forced colloquialism ("honestly", "basically", casual
asides in formal material); fake nuance (caveats added to sound
thoughtful); parallelism at any cost (unlike items forced into one
grammatical shape); and over-editing stable language (a clear, exact,
genre-appropriate sentence changed because it could be; difference is not
improvement).

## 9. Authorship and provenance integrity

Polished prose from the owner's facts, notes, sources, or drafts is
legitimate. The prose states only the authorship, history, and experience
the owner or the source establishes. It must never claim a human wrote
text when that is not established, fabricate a personal history, firsthand
observation, interview, or lived experience, insert fake idiosyncrasies to
disguise machine assistance (typos, grammatical mistakes, fake
hesitations, random contractions, arbitrary fragments, invented
preferences, inconsistent punctuation, or slang the writer or genre did
not establish), advise that the text will evade detectors, revise toward a
detector score, or create fake drafts, timestamps, or revision histories.
First person uses only experiences, judgments, or actions established by
the owner or the source. `deliver.attribution-assertion` and the plant's
`commit_attribution` fact govern what a commit or deliverable says about
who produced it; this node governs only that the prose tells the truth
about it.

## 10. Decision rules

Keep a suspected pattern when at least one holds: it carries information;
it expresses a real logical relationship; it is normal for the writer's
demonstrated voice; it is useful in the genre; removing it would reduce
precision or comprehension; it creates intentional rhythm that suits the
passage. Revise it when at least one holds: it adds emphasis without
information; it repeats a structure mechanically; it obscures the actor or
action; it inflates significance; it weakens source fidelity; it creates
unnecessary symmetry; it reads as template residue; it consumes attention
without helping the reader.

Combine paragraphs that answer the same reader question, or whose second
only restates the first, or that were split only to make a dramatic
one-liner. Split when the reader question, actor, or time frame changes,
when evidence and recommendation need separation, or when a caveat changes
scope. Use a list when items are parallel and the reader will scan; use
prose when the value is in the relationships among ideas. Add detail that
is supported and resolves a likely uncertainty or changes action; cut
detail that duplicates, is irrelevant to the purpose, or adds no decision
value. When shortening, preserve in order: decision-critical facts,
requirements and constraints, evidence that changes confidence, caveats
that change interpretation, definitions that prevent ambiguity; cut first
throat-clearing, repeated framing, redundant examples, generic significance,
duplicate conclusions, and low-value transitions. Compression keeps
every uncertainty and condition.

## 11. Stop conditions

Stop when the document's purpose is clear from its content and structure;
every material claim is preserved or changed with authorization; evidence,
inference, and recommendation stay distinguishable; paragraphs have
identifiable jobs; section order follows reader need; terminology is
stable; the voice fits author, audience, and genre; no high-impact drafting
residue remains; no unsupported experience or provenance was introduced;
citations and quantities are intact; and further edits would mostly create
difference rather than improvement, whatever a detector says or however
distinctive each sentence already is.

## Doctrine compatibility

This posture yields to factual correctness, source fidelity, citation
requirements, security or privacy constraints, legal accuracy,
accessibility, required terminology, a style guide the owner or
organization supplies, project instructions, regulated or contractual
wording, localization requirements, technical syntax, data formats, code or
command integrity, and the owner's intent. When a style preference conflicts
with correctness or required wording, correctness wins. When a house style
conflicts with these defaults, the house style wins unless it creates a
substantive error. When an author's sample conflicts with the genre, the
two are reconciled: recognizable voice, usable document.

## Neighbours

- `docs/graph/skills/humanizer.md`: the procedure (document contract,
  progressive execution, the rewriting passes, verification, output modes)
  and the tool that floors it.
- `method.engineering-posture` §8: instruction economy and the voice rule
  for model-facing text; `method.decision-economy`: when to stop
  explaining, and reading a request literally.
- `docs/graph/protocols/deliver.md`: the delivery summary's quality bar,
  where this posture is applied last.

## Source

Adapted from two MIT-licensed skills: the humanizer skill by Siqi Chen
(2025; patterns from Wikipedia's "Signs of AI writing") and the
human-prose doctrine (4.0.0, derived from it). Upstream notices are kept at
`skills/humanizer/LICENSE.upstream` in the seed.
