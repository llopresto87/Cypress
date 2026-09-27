<!--
Template: findings-report.template.md (the contract) + findings-report.template.html (the form)
Authored by: ui-ux-designer (the visual system); filled by whichever agent owns
the findings: security, pentest, legal, reviewer; re-cut by report-editor
Lives at: docs/graph/templates/ (placed by the installer). A filled report goes
wherever the plant keeps delivered reports; the findings themselves keep their
own home (a risk register, a pentest record), and the report only renders them.
Used: when security or compliance findings go to a reader as one standalone,
accessible document that survives e-mail, print and greyscale.
Fill by copying the .html file and following the contract below. This file is
the contract; the .html file is the form.
-->

# Findings report: the generation contract

`findings-report.template.html` is one self-contained HTML file: no external
dependency, no CDN, styles and script inline. It serves two twin reports, a
security report and a compliance report, from the same markup. This file says
how to fill it without breaking what makes it worth reusing.

## Why the form is kept rather than redrawn

Severity is encoded on **four independent channels**: colour, glyph, written
label, and the pattern of the card's side bar. The report therefore stays
readable in greyscale print and for a colour-blind reader. Every badge also
carries a visually hidden prefix for screen readers ("Severity: ", "Status: "),
and every glyph is `aria-hidden`. That accessibility floor is expensive to
derive and easy to lose when someone redraws a report from scratch, so a plant
fills this form instead.

It is a template and not a tool. It has a stable, documented interface (the
tables below), but no executable entry point and no test, so it gets no
`tools/` card (`skill.toolcraft`). If a generator is ever written against this
contract, the generator is the tool and gets the card, and this file becomes
its input format.

## The fill rules

- Duplicate the block between `<!-- CARD-TEMPLATE-START -->` and
  `<!-- CARD-TEMPLATE-END -->` once per finding. Insert the copies into
  `<!-- SECTION: APP -->` or `<!-- SECTION: PLATFORM -->`, by where the fix
  lands.
- **The template never reorders anything.** Cards go in the order the data
  already decided (the sample's method note states severity descending, then
  effort ascending). Ordering is a decision about the findings, and it is made
  where the findings live.
- A field that does not apply has its whole `<dt>`/`<dd>` pair removed. It is
  never left empty.
- A value that was not established is written `not recorded`. The report never
  guesses.
- State the severity floor in the method note. Entries below it move to
  "Considered and excluded", one line each with the reason for the downgrade,
  so the review stays traceable.
- Remove `div.notice` (the sample warning) from a real report. Update the `h1`,
  the `<time datetime="…">` date, the report revision, and each
  `span.sec-count` ("N findings").
- English is the default. Set `<html lang>` and translate the labels, the
  legend and the screen-reader prefixes into the plant's deliverable language,
  which the `plant:` block in `docs/graph/index.md` declares. Keep the class
  names as they are: they are the contract.
- Every sample card, repository, path and quotation in the form is a synthetic
  placeholder. A real report replaces all of them.

## Field → markup

| Data field | Element / class | Notes |
|---|---|---|
| id | `span.f-id` | monospace; also `id="f-<ID>"` on `article.finding`, the anchor cross-references point at |
| title | `h3.f-title` with `id="f-<ID>-h"` | named by the article's `aria-labelledby` |
| severity | `span.badge.sev-*` **and** the `finding--*` class on the `article` | change both together |
| status | `span.badge.st-*` | |
| where to fix | `span.badge.loc-app` or `span.badge.loc-platform` | text `Application code: <name>` or `Platform layer: <name>` |
| effort | `span.badge.eff`, band letter in `<strong>`, band also in `title` | |
| file:line (1–3) | `ul.f-loc > li` | one `li` per location, text `path:line` |
| concrete harm | `dt.f-label.f-label-harm` + `dd.f-body.f-harm` | two to five sentences; the heaviest type on the card |
| obligation breached | `div.f-obligation-row` > `blockquote.f-obligation` + `cite` | compliance report only (see the switch below); quoted verbatim from a retrieved copy of the source, never from memory |
| related decision / spec | `dd.f-body.f-decision`; when there is none, add `.is-absent` and write "No related decision recorded." | |
| minimal fix | `dd.f-body` with `<p>` and, when needed, `pre.f-code > code` | scrolls horizontally inside its own box on screen; wraps in print |
| cross-reference | `p.f-xref`, outside the `dl`, at the end of the card | optional; when absent, remove the paragraph |

## Badge vocabularies

| Badge | Classes and glyphs |
|---|---|
| severity | `sev-critical` (`◆` Critical), `sev-high` (`▲` High), `sev-medium` (`◇` Medium), `sev-low` (`△` Low). On the `article`: `finding--critical` (solid bar, heavy border), `finding--high` (dashed bar), `finding--medium` (dotted bar), `finding--low` (hollow bar) |
| status | `st-open` (`●`), `st-partial` (`◐`), `st-blocked` (`■`), `st-closed-residual` (`○`) |
| where to fix | `loc-app` (`▣`), `loc-platform` (`◈`) |
| effort | `XS` up to 1 hour, `S` half a day, `M` 1–2 days, `L` 3 days or more |

The effort bands and the severity definitions in the legend are this
template's declared conventions, not a standard. When the project fixes other
bands, change them in the legend **and** in every badge's `title`. A new
severity level or status needs all four channels before it ships: colour
tokens in every theme and in print, a glyph no other badge uses, a label, and
a bar pattern.

## The report-kind switch and the other markers

One attribute on `<body>` selects the report. `data-report="compliance"`
shows every `.f-obligation-row`; `data-report="security"` hides them through
CSS. The markup stays identical in both reports, so a card can move between
them unchanged.

The other marked blocks repeat the same way as the card:

- `<!-- META-ROW-TEMPLATE-* -->`: one table row per repository or surface in
  scope, with the branch, the commit verified, and the date verified.
- `<!-- EXCLUDED-ROW-TEMPLATE-* -->`: one line per entry considered and
  downgraded.
- `<!-- XREF-ROW-TEMPLATE-* -->`: one line per entry the twin report also
  covers, linking to its card anchor.

The theme follows the operating system and can be forced with
`data-theme="light"` or `data-theme="dark"` on `<html>`. Print forces the light
theme, keeps the colours, and never splits a card across pages.

## Neighbours

- `report-editor`, a candidate role in the seed's `agent-corpus/`: re-cuts a
  finished report for a reader who can act on only part of it, and brings
  reports onto this one visual system.
- `agent.ui-ux-designer`: owns the visual system itself; a change to the
  tokens or the channels is its call.
- `method.prose-posture`: the register of the harm and fix text.
