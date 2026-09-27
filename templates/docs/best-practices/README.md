# Best practices

This shelf holds one page per stack element or per discipline, and each page
states an external standard and where this project stands against it. That is
what the page is for: a reader opens it to learn what the standard asks and
whether this project meets it, departs from it on purpose, or was never
checked. The definition of a normative page, and why description alone does
not belong here, is `../templates/prompts/growth-coverage-record.md`
("A `best-practices/` page is normative"). A page that only describes what the
project happens to do belongs in `../architecture/`.

Pages are created when a subject earns one. Do not seed empty files.

## Who owns a page

Every page is the `artifacts:` leaf of exactly one node. A page about a stack
element is owned by that element's `expertise.*` node. A page about a
discipline or concept the graph already names is owned by that `domain.*`
node. `skill.knowledge-graph` ("Where a grounded idea attaches") decides which
one applies. A page no node reaches is a page the router never surfaces.

## The shape of a page

1. **The standard.** What the external source says, cited to what was actually
   retrieved: the normalized copy under `../sources/normalized/`, logged in
   `../sources/index.md`. Cite the documentation host for the version the
   project runs, not the "latest" page, because guidance moves between majors.
   A claim with no retrieved source is not written.
2. **Where this project stands.** One row or paragraph per point of the
   standard. Each says either *measured*, with the file and line that show it,
   or *not measured in this pass*. An unchecked point is never presented as
   compliant.
3. **Departures.** Anything the standard says not to do that this project does,
   written down with its reason. A departure the owner has decided to keep is
   a `deviation.*` node, and the page links it.
4. **What was not measured.** Every page ends with this section: the parts of
   the standard this pass did not check, so the next reader knows where the
   page's silence is ignorance rather than compliance.

## What a page never restates

- **The version pin.** It lives in `../libraries/<slug>.md` §0. The page names
  the major it was written against and links there.
- **When the element is in play.** That is the owning `expertise.*` node's
  applicability fact.
- **This project's own conventions.** Those belong to the subsystem, platform
  or stack node that owns them.

## Facts a page cannot get from code

A standard often turns on facts that are not software facts. Two kinds recur:

- **Organizational facts**: who is accountable for a control, how often it is
  reviewed, who signs off. Code cannot show them. Write them as out of scope
  for the page, or `not recorded` with an open question to the owner, and
  never infer them from a config file or a commit author.
- **Jurisdictional parameters**: a retention period, a notification deadline,
  a statutory threshold. Name the parameter as open and cite the provision
  that sets it once someone confirms it. Never invent a value. How erasure and
  statutory retention interact in the data itself is
  `method.contract-posture` §7.

## Pages

| Page | Owning node | Grounding (`../sources/normalized/`) |
|---|---|---|

No page here replaces an active spec, an ADR, a library page, or a policy the
owner has approved.
