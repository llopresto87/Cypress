# Tool: citation-anchor-resolver

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). Orientation for a reusable tool, a blueprint: the
> candidate filter, the resolution order and the never-guess rule are
> stack-neutral and stdlib-only; the governed root, the pruned directories and
> the extension vocabulary are the project's.

## 0. Identity

- **Category:** ops
- **Name:** citation-anchor-resolver
- **Language / runtime:** python3, **stdlib only** (a gate must run on a bare
  interpreter).
- **Stability:** **blueprint**: its first run found an out-of-range anchor no
  other gate caught, but no regression test was kept with it; build the
  mutation fixture in §6 before trusting an adoption

## 1. What it does

Resolves every `path:line` citation in a knowledge graph's pages against the
governed source tree and fails on anchors a reader cannot follow:

- **ERROR**: no file anywhere in the tree can be the target; a cited line or
  range end is past the target's last line; line 0; an inverted range.
- **WARN**: the anchor resolves, but not as written: a bare basename with no
  directory; a path elided with `...`; several real files match (ambiguous,
  resolved to none, so its lines went unchecked); only the basename matches and
  every directory component written is wrong.

A wrong anchor is the costliest defect a source-citing graph carries: the claim
reads as verified, the reader follows it and lands on the wrong line or on
nothing. Hand review finds these at a sampling rate; this finds all of them.

**What it cannot check, said in its own output:** whether the claim at the
line is true. A resolving anchor is **well-formed, not correct**; source
fidelity stays a reviewer's job. Nor can it tell whether a uniquely matched
suffix is the file the author meant.

The seed's own graph tools answer different questions:
`source-index.py anchors` answers the inverse ("which pages cite these
files?"), and `code-anchor.py` reports which code moved since the graph was
last reconciled. Neither resolves a page's anchors to lines.

## 2. Interface & invocation

```
resolver              # gate: exit 1 on any ERROR, warnings counted in the summary
resolver --warn       # report errors and warnings, exit 0
resolver --list       # every citation with its resolved target and line count
resolver --rejected   # every `word:number` shape discarded as a non-citation
```

- **Scans:** every markdown page under the graph root except blank-form
  directories (templates), with **fenced code blocks blanked** (line numbers
  kept), because a command line in a fence is not a citation.
- **Output:** one line per finding (`page:line  cite - why`), then a summary:
  citations found, resolved in range, resolved only via a unique suffix match,
  counts per class, and how many were pinned to no single file.
- **The `--rejected` view is the tuning surface:** read it after adoption to
  confirm the filters drop only non-citations.

## 3. Approach / algorithm

**1. Candidate extraction.** A regex finds `path:lines` where lines is `12`,
`12-14` or a comma list of those. Context rules kill the common false shapes:
the match may not start after `/`, `:`, `,`, `}` or a word character, and may
not end before a word character, a second `:`, or `.<digit>`. That rejects
URLs and `host:port`, package coordinates, image tags, version pins, times and
ratios, member references. Then the basename must look like a file (a known
extension, a known extension-less name such as a build file, or a known
dotfile) and the path must contain a letter. **Existence redeems shape:** a
candidate with an unfamiliar name is kept when a real file of that path
exists, because existence can only add true positives.

**2. Resolution, fixed precedence, no searching first:**

1. relative to the governed root; 2. relative to the graph root; 3. relative to
the citing page's directory; each kept only if it stays inside the root.

**3. Suffix match.** When direct resolution fails, look the basename up in an
index of every real file under the root (vendored and generated directories
pruned) and match **exact trailing components**: drop everything up to the last
`...`, then shed leading components one at a time, most specific first.

- one match: resolved (not a guess); if only the basename survived while the
  citation wrote directories, warn "directory mismatch";
- several matches: warn "ambiguous", **resolve none**; never break the tie;
- no match: ERROR "missing".

**4. Range check** against the target's line count (cached per file): every
span must satisfy `1 <= start <= end <= EOF`.

The never-guess rule is the design: choosing between same-named files is how a
resolver manufactures false passes and false failures.

## 4. Portable vs blueprint

- **Portable (carry over):** the candidate regex with its context rules; the
  file-shape filter with existence redemption; fence blanking; the three-step
  direct resolution; trailing-component matching with elision handling; the
  never-guess tie rule; the range check; the "well-formed, not correct" line in
  the output.
- **Fill in per project:** the governed root (a multi-repository umbrella or a
  single repository); pruned directories; the extension and extension-less
  vocabularies of the languages really cited; the graph's skip directories.

## 5. Pitfalls and sharp edges

- **Zero citations is not a pass.** A broken regex or a moved graph root yields
  "0 citations, 0 errors". Fail when the citation count falls below a floor
  stated for the graph (or below a fraction of the previous run).
- **Pruning decides ambiguity.** An unpruned build-output or dependency
  directory duplicates real filenames and turns good anchors ambiguous. Prune
  what nobody cites.
- **Suffix resolution can bless the wrong file** when only one same-named file
  exists but the author meant a deleted one. The directory-mismatch warning is
  the signal; read those.
- **Line counting:** count newlines, plus one when the file does not end in a
  newline; an empty file has zero lines, so any anchor into it is out of range.
- **Read targets with replacement decoding** so one non-UTF-8 file cannot
  crash the gate; a crash is not a verdict.

## 6. Tests that cover it

Build a **mutation fixture** before adopting: a tiny governed tree and a graph
page carrying exactly one anchor per class, each asserted to produce its
finding and nothing else: a valid anchor (no finding); a missing file; a line
past EOF; line 0; an inverted range; a bare basename; an elided path; two
same-named files (ambiguous, lines unchecked); a wrong directory with a
uniquely matching basename (mismatch). Add the false-shape set (a URL with a
port, a package coordinate with a version, an image tag, a time, a reference
inside a fence) and assert none is a citation; and a zero-citation graph that
fails the floor.

- **How to run the tests:** `<the plant's test command for its implementation>`

## 7. References & neighbours

- **Seed tools:** `tools/source-index.py` (`anchors`: the inverse question,
  which pages cite a file); `tools/code-anchor.py` (which code moved since the
  graph last matched it).
- **Skills:** `skills/knowledge-graph` (the graph whose citations this checks);
  `skills/validate-knowledge` (the reviewer pass that owns claim fidelity).
- **Sources:** distilled from practice; no external URL.

## 8. Changelog

- 2026-10-14: created as a blueprint from a dependency-free resolver whose
  first run found an out-of-range anchor no other gate caught; the proving
  fixture was not kept, so §6 states the one to build.
