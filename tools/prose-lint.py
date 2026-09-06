#!/usr/bin/env python3
"""prose-lint: the mechanical floor under the prose skills.

Two doctrines are gated here, and they agree on the shape of the problem:
the humanizer skill 3.0.0, whose patterns are numbered §1 to §25, and the
human-prose doctrine 4.0.0 (derived from blader/humanizer), whose
Diagnostic Framework is lettered A to X. A finding is reported under the
§ number when a humanizer pattern names it and under the letter when only
human-prose does, so a reader can always trace a finding back to the
sentence of doctrine that asks for it. A phrase both sources name is
reported under both.

Both skills remove the marks of AI writing without changing what the
prose says. Most of that work is judgement: whether a contrast carries
information, whether a short paragraph earns its place, whether the
result still sounds like the writer. None of that is checked here, and
this tool does not pretend to. It catches the subset of tells that a
pattern can decide, and it proves the rewrite kept its facts, which is
the one step a reviewer cannot do by reading.

Two rules of that doctrine bind this tool as much as its user. A word
list is a prompt to inspect context, never a ban: precise prose sometimes
needs the word, so every vocabulary detector here is weak, printed and
forgiven until other tells share its paragraph. Punctuation is controlled
for overuse, not forbidden: §8 is a rate, 3 dashes per 1,000 prose words
by default, the sample's own rate under --sample, and zero only when
--strict is asked for.

What it can judge:

  phrase tells      the fixed watch-for lists the skill enumerates:
                    not-X-but-Y (§1), one-line closers (§2), sayings that
                    sound deep (§3), staged openers (§4), arguing with no
                    one (§5), stacked qualifiers (§9), overused words
                    (§12), inflated significance (§13), vague association
                    (§14), sales language (§16), borrowed authority
                    (§17), is/are avoidance (§18), curly quotes (§21),
                    chatbot residue (§22), knowledge-limit disclaimers
                    (§23), previous-version narration (§25); and from
                    human-prose, empty intensifiers (S), premature
                    conclusion language (V), synthetic friendliness (W)
                    and meta-writing residue (X)
  shape tells       a rate of dashes per 1,000 prose words (§8), a run of
                    three bold-labelled list items (§19), decorative
                    headings, emoji, arrows and rule stacks (§20), a
                    heading restated by the sentence under it (§24), a
                    closer repeated after two or more sections (§2), and
                    per paragraph, corporate glaze (E) and
                    over-transitioning (K)
  fact drift        with --against REV: numbers, headings, inline code,
                    fenced code, link targets and requirement levels (the
                    modal verbs must, must not, shall, should, may, never,
                    required, prohibited) must survive the rewrite as
                    identical multisets, whatever happened to the
                    sentences around them. A requirement downgraded from
                    must to should is a fidelity failure like any other

What it cannot judge: voice. Whether a kept sentence adds anything,
whether a contrast is real, whether the rewrite still reads like the
writer, whether a dash is the right dash, whether an intensifier carries
degree the evidence supports. The skills do that; this file is the floor
under them, not a substitute for them.

Severity follows the skills' own ordering. Strong tells (§1 to §5, §13,
§16, §17, §19, §22, §23, §24, W, X, and a dash rate over its allowance)
fail on one sighting. Weak tells are printed and forgiven, because a person makes
any one of them on purpose; they fail under --strict, or when three of
them share a paragraph, which is the skill's "weak alone needs company"
rule made countable.

Only prose is scanned. YAML frontmatter, fenced code, inline code, HTML
comments, link targets, bare URLs and table rows are blanked before any
detector runs, so a dash in a command, a "delve" in a code sample or a
not-X-but-Y in a quoted fence is never a finding. Blanking preserves line
numbers: removed spans become spaces, never deleted lines.

Usage:
    prose-lint.py [--root <dir> ...] [--file <path> ...] [--glob <pat> ...]
                  [--against <rev>] [--strict] [--sample <file>]
                  [--changelog-ok]

    --root          directory scanned recursively (repeatable; default: .)
    --file          one file, scanned whatever --glob says (repeatable)
    --glob          filename pattern under each --root (repeatable;
                    default: *.md)
    --against REV   compare each scanned file against `git show REV:path`
                    and fail on fact drift
    --strict        weak tells fail too, and the dash allowance is zero
    --sample FILE   a writing sample; its own dash rate becomes the
                    allowance, the way the skill lets a sample override §8
    --changelog-ok  this text is about change, so §25 does not apply

Exit 0 clean, 1 with findings, 2 on a usage error, including a run that
matched no file at all, which would otherwise print the same clean
verdict a real scan earns.

Importable: scan() returns a Report (findings, files, words, dashes,
rate), so a host linter reuses the detection and renders it in its own
voice instead of parsing this CLI's output. Dependency-free.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_GLOBS = ("*.md",)
DEFAULT_DASH_PER_1000 = 3.0
WEAK_CLUSTER_SIZE = 3
CHANGELOG_NAMES = ("changelog", "release", "migration")


@dataclass(frozen=True)
class Finding:
    """One tell. `rule` is the skill's section number, `severity` one of
    strong, weak, cluster, drift. Rendering stays here so every caller
    prints the same shape."""
    path: str
    line: int
    rule: str
    severity: str
    text: str

    def render(self) -> str:
        if self.severity == "cluster":
            return f"{self.path}:{self.line}: weak cluster — {self.text}"
        if self.severity == "drift":
            return f"{self.path}: fact drift — {self.text}"
        return (f"{self.path}:{self.line}: {self.rule} "
                f"{self.severity} — {self.text}")


@dataclass
class Report:
    """A whole scan: the findings plus the totals the dash rate is
    measured against, and the notes that are informational only."""
    findings: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    files: int = 0
    words: int = 0
    dashes: int = 0
    allowance: float = DEFAULT_DASH_PER_1000

    @property
    def rate(self) -> float:
        return (self.dashes * 1000.0 / self.words) if self.words else 0.0


# ---------------------------------------------------------------- masking

def _blank(m) -> str:
    """Replace a span with spaces, keeping its newlines, so every line
    number downstream still points at the line the reader sees."""
    return re.sub(r"[^\n]", " ", m.group(0))


FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
CODE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)*?\1")
LINK_TARGET_RE = re.compile(r"(?<=\])\([^)\n]*\)")
URL_RE = re.compile(r"<?\b(?:https?|ftp)://[^\s>)]+>?", re.I)
TABLE_ROW_RE = re.compile(r"^[ \t]*\|")


def mask(text: str) -> list:
    """The prose of a Markdown file, as a list of lines with everything
    that is not prose replaced by spaces. Blockquotes are prose and stay:
    a tell inside a quote of one's own draft is still a tell."""
    lines = text.splitlines()
    # 1. frontmatter
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                for i in range(0, j + 1):
                    lines[i] = " " * len(lines[i])
                break
    # 2. fenced code blocks, fence lines included
    fence = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0]
                lines[i] = " " * len(line)
            continue
        lines[i] = " " * len(line)
        if m and m.group(1)[0] == fence:
            fence = None
    # 3. table rows
    for i, line in enumerate(lines):
        if TABLE_ROW_RE.match(line):
            lines[i] = " " * len(line)
    # 4. spans: HTML comments, inline code, link targets, bare URLs
    joined = "\n".join(lines)
    for rx in (COMMENT_RE, CODE_SPAN_RE, LINK_TARGET_RE, URL_RE):
        joined = rx.sub(_blank, joined)
    return joined.split("\n")


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")


def count_words(mlines) -> int:
    return sum(len(WORD_RE.findall(l)) for l in mlines)


DASH_RE = re.compile(r"—|–|(?<= )--(?= )")


def dash_hits(mlines):
    """(line number, matched text) for every dash used as a connector.
    An en dash between digits is a range, and a hyphen inside a word is a
    hyphen: neither counts."""
    hits = []
    for n, line in enumerate(mlines, 1):
        for m in DASH_RE.finditer(line):
            if m.group(0) == "–":
                before = line[m.start() - 1] if m.start() else ""
                after = line[m.end()] if m.end() < len(line) else ""
                if before.isdigit() and after.isdigit():
                    continue
            hits.append((n, m.group(0)))
    return hits


# ------------------------------------------------------------- detectors

def phrase(p: str) -> str:
    """A literal watch-for phrase as a regex: whitespace is flexible, an
    apostrophe matches either shape, and word edges are anchored."""
    body = r"\s+".join(re.escape(w) for w in p.split())
    body = body.replace("'", "['’]")
    pre = r"\b" if re.match(r"\w", p) else ""
    post = r"\b" if re.search(r"\w$", p) else ""
    return pre + body + post


def group(rule, severity, patterns, initial=False, literal=True):
    joined = "|".join(phrase(p) if literal else p for p in patterns)
    return (rule, severity, re.compile(f"(?:{joined})", re.I), initial)


# §12: the skill's list, minus gate/gated/gating and robust, whose
# technical senses dominate a repository like this one. "key" is matched
# only in its adjectival frame, since the noun is everywhere in software.
OVERUSED = [
    r"actually", r"additionally",
    r"align(?:s|ed|ing)?\s+with", r"bolstered", r"crucial",
    r"deep\s+dive", r"delv(?:e|es|ed|ing)",
    r"emphasi[sz](?:e|es|ed|ing)", r"enduring", r"enhanc(?:e|es|ed|ing)",
    r"foster(?:s|ed|ing)", r"garner(?:s|ed|ing)?",
    r"highlight(?:s|ed|ing)?", r"interplay",
    r"intricate|intricac(?:y|ies)",
    r"key\s+(?:role|part|player|factor|component|element|insight|"
    r"takeaway|aspect|point|difference|feature|moment|driver)",
    r"landscape", r"meticulous(?:ly)?", r"pivotal", r"quietly",
    r"showcas(?:e|es|ed|ing)", r"tapestry", r"testament",
    r"underscor(?:e|es|ed|ing)", r"valuable", r"vibrant",
]

LINE_DETECTORS = [
    # §1 not X but Y, in its one-line forms.
    ("§1", "strong", re.compile(
        r"\bnot\s+(?:just\s+|only\s+|merely\s+|simply\s+)?"
        r"[^.!?\n]{0,60}?\bbut\b", re.I), False),
    ("§1", "strong", re.compile(
        r"\bit['’]?s\s+not\b[^.!?\n]{0,60}?,\s*it['’]?s\b",
        re.I), False),
    ("§1", "weak", re.compile(r"\brather\s+than\b", re.I), False),
    group("§2", "strong", ["That is the real win", "That's the real win",
                           "Read that again", "Let that sink in"]),
    group("§3", "strong", ["the real question is", "at its core",
                           "what really matters", "the heart of the matter",
                           "the language of", "the currency of",
                           "the architecture of", "becomes a trap"]),
    group("§4", "strong", ["Let's dive in", "let's explore",
                           "let's break this down",
                           "here's what you need to know",
                           "without further ado", "Here's the thing",
                           "The thing is", "Let's be honest", "Real talk"],
          initial=True),
    ("§5", "strong", re.compile(
        r"\bthis\s+(?:is\s+not|isn['’]t)\s+(?:mainly\s+)?about\b",
        re.I), False),
    group("§5", "strong", ["I'm not saying", "To be clear",
                           "Don't get me wrong", "This is not to say",
                           "Some might say", "A tempting approach would be",
                           "One might be tempted to", "You might think"]),
    group("§9", "weak", ["to be fair", "it's also possible",
                         "could potentially", "might arguably",
                         "in some cases it may"]),
    group("§12", "weak", OVERUSED, literal=False),
    group("§13", "strong", ["stands as a testament", "pivotal moment",
                            "crucial moment", "plays a key role",
                            "underscores its importance",
                            "reflects a broader", "lasting legacy",
                            "enduring legacy", "setting the stage for",
                            "evolving landscape", "indelible mark",
                            "the future looks bright",
                            "exciting times ahead",
                            "a step in the right direction"]),
    group("§14", "weak", ["associated with", "in connection with",
                          "linked to", "tied to"]),
    group("§16", "strong", ["boasts", "nestled", "in the heart of",
                            "breathtaking", "must-visit", "stunning",
                            "diverse array", "groundbreaking", "renowned"]),
    group("§17", "strong", ["experts argue", "experts believe",
                            "observers have cited", "industry reports",
                            "some critics", "several publications",
                            "active social media presence"]),
    group("§18", "weak", ["serves as", "stands as", "functions as",
                          "operates as", "refers to"]),
    ("§21", "weak", re.compile(r"[“”‘’]"), False),
    # human-prose diagnostics with no humanizer number of their own.
    group("S", "weak", ["very", "truly", "incredibly", "highly", "deeply",
                        "particularly"]),
    group("V", "weak", ["ultimately", "in conclusion",
                        "all things considered", "the bottom line"]),
    group("W", "strong", ["Great question", "The good news is",
                          "Don't worry", "Luckily", "Excitingly",
                          "You're all set"]),
    group("X", "strong", ["Here is a revised version", "As requested"]),
    group("§22", "strong", ["I hope this helps", "Of course!", "Certainly!",
                            "Great question", "You're absolutely right",
                            "Would you like", "Want me to",
                            "Should I continue", "Let me know if"]),
    group("§23", "strong", ["up to my last training update",
                            "while specific details are limited",
                            "based on available information",
                            "not widely documented", "it is believed that",
                            "maintains a low profile"]),
]

PREV_VERSION = group("§25", "weak", ["previously", "no longer", "used to be",
                                     "was replaced", "the old approach"])

# §1 split across two sentences, so it is matched over a whole paragraph.
SPLIT_CONTRAST_RE = re.compile(
    r"\bthis\s+does\s+not\s+mean\b[^.!?\n]{0,120}[.!?]\s+it\s+means\b",
    re.I | re.S)

# E: the nouns that replace people, systems and results with programme
# vocabulary. One is a word choice; three in a paragraph is glaze.
GLAZE_RE = re.compile(
    r"\b(?:initiatives?|capabilit(?:y|ies)|opportunit(?:y|ies)|frameworks?|"
    r"journeys?|ecosystems?|landscapes?|alignments?|transformations?|"
    r"optimi[sz]ations?|enablement)\b", re.I)
GLAZE_MIN = 3
# K: a connective at the start of nearly every sentence. Three in one
# paragraph is the rate the diagnostic describes.
TRANSITION_RE = re.compile(
    r"(?:" + "|".join(phrase(p) for p in
                      ("Additionally", "Moreover", "Furthermore",
                       "On the other hand")) + r")", re.I)
TRANSITION_MIN = 3

MARKER_RE = re.compile(r"^[ \t]*(?:(?:[-*+>]|\d+[.)])[ \t]+|#+[ \t]+|>[ \t]*)*")
SENTENCE_END_RE = re.compile(r"[.!?][\"')\]”’]*\s+")
LIST_ITEM_RE = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+")
BOLD_LABEL_RE = re.compile(
    r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\*\*[^*\n]{1,60}?:?\*\*:?")
HEADING_RE = re.compile(r"^[ \t]*(#+)[ \t]+(.*\S)")
HRULE_RE = re.compile(r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$")
EMOJI_RE = re.compile(
    "[→➔➡\U0001F300-\U0001FAFF☀-➿⬀-⯿]")
TITLE_STOPWORDS = frozenset("""a an and as at but by for from in into nor of on
or over per the to up via with is are it its that this""".split())


def sentence_starts(line: str) -> set:
    """Offsets in a line where a sentence begins: after the leading list,
    quote or heading markers, and after each sentence terminator. §4 is a
    tell only as an opener, so it is matched at these offsets alone."""
    starts = {MARKER_RE.match(line).end()}
    for m in SENTENCE_END_RE.finditer(line):
        starts.add(m.end())
    return starts


def blocks(mlines):
    """The paragraphs of the masked prose, in order, each with its first
    line number, its lines, its text and the index of the heading it sits
    under. A heading is its own block, which is what §24 compares."""
    out, cur = [], None
    section = 0
    for n, line in enumerate(mlines, 1):
        if not line.strip():
            cur = None
            continue
        head = HEADING_RE.match(line)
        if head:
            section += 1
        if cur is None or head:
            cur = {"start": n, "lines": [], "section": section,
                   "heading": bool(head)}
            out.append(cur)
        cur["lines"].append((n, line))
        if head:
            cur = None
    for b in out:
        b["text"] = "\n".join(t for _, t in b["lines"])
    return out


def paragraph_ids(mlines) -> dict:
    """line number -> paragraph index, so weak tells can be clustered by
    the paragraph they share."""
    ids = {}
    for i, b in enumerate(blocks(mlines)):
        for n, _ in b["lines"]:
            ids[n] = i
    return ids


def words_of(text) -> list:
    return [w.lower() for w in WORD_RE.findall(text)]


def is_title_case(text: str) -> bool:
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'’-]*", text)]
    if len(words) < 4:
        return False
    body = [w for w in words if w.lower() not in TITLE_STOPWORDS]
    if len(body) < 2:
        return False
    return all(w[0].isupper() for w in body)


def structural(rel, mlines, add):
    """The tells that live in shape rather than in a phrase: §2 repeated
    closers, §19 bold-label runs, §20 decoration, §24 a heading restated
    under itself, and §1 split across two sentences."""
    bs = blocks(mlines)

    # §1 across a sentence boundary.
    for b in bs:
        for m in SPLIT_CONTRAST_RE.finditer(b["text"]):
            line = b["start"] + b["text"][:m.start()].count("\n")
            add(Finding(rel, line, "§1", "strong",
                        " ".join(m.group(0).split())))

    # §2 the same short closer after two or more different sections.
    closers = defaultdict(list)
    for b in bs:
        if b["heading"]:
            continue
        text = " ".join(b["text"].split())
        if not text:
            continue
        if len(re.split(r"(?<=[.!?])\s+", text)) > 1:
            continue
        if len(words_of(text)) > 8:
            continue
        closers[text.lower()].append(b)
    for text, found in closers.items():
        if len({b["section"] for b in found}) >= 2:
            for b in found:
                add(Finding(rel, b["start"], "§2", "strong",
                            f"closer repeated after "
                            f"{len({x['section'] for x in found})} sections: "
                            f"{' '.join(b['text'].split())}"))

    # E corporate glaze and K over-transitioning, both counted over a
    # whole paragraph: one sighting of either is a word choice.
    for b in bs:
        if b["heading"]:
            continue
        glaze = GLAZE_RE.findall(b["text"])
        if len(glaze) >= GLAZE_MIN:
            add(Finding(rel, b["start"], "E", "weak",
                        f"corporate glaze, {len(glaze)} programme nouns in "
                        f"one paragraph: "
                        f"{', '.join(sorted({g.lower() for g in glaze}))}"))
        opens = []
        for n, line in b["lines"]:
            starts = sentence_starts(line)
            opens += [m.group(0) for m in TRANSITION_RE.finditer(line)
                      if m.start() in starts]
        if len(opens) >= TRANSITION_MIN:
            add(Finding(rel, b["start"], "K", "weak",
                        f"over-transitioning, {len(opens)} sentences of one "
                        f"paragraph open with a connective: "
                        f"{', '.join(opens)}"))

    # §19 three or more consecutive bold-labelled list items.
    run = []
    for n, line in enumerate(mlines, 1):
        if BOLD_LABEL_RE.match(line):
            run.append((n, line))
            continue
        if LIST_ITEM_RE.match(line):
            run = []
            continue
        if line.strip():
            run = []
        if len(run) >= 3:
            add(Finding(rel, run[0][0], "§19", "strong",
                        f"{len(run)} consecutive bold-label list items"))
            run = []
        if not line.strip() and len(run) < 3:
            run = []
    if len(run) >= 3:
        add(Finding(rel, run[0][0], "§19", "strong",
                    f"{len(run)} consecutive bold-label list items"))

    # §20 decoration: title-case headings, emoji or arrows, rule stacks.
    rules = []
    for n, line in enumerate(mlines, 1):
        head = HEADING_RE.match(line)
        if head and is_title_case(head.group(2)):
            add(Finding(rel, n, "§20", "weak",
                        f"title-case heading: {head.group(2)}"))
        if head or LIST_ITEM_RE.match(line):
            for m in EMOJI_RE.finditer(line):
                add(Finding(rel, n, "§20", "weak",
                            f"decoration in a heading or list item: "
                            f"{m.group(0)}"))
        if HRULE_RE.match(line):
            rules.append(n)
    if len(rules) >= 3:
        for n in rules:
            add(Finding(rel, n, "§20", "weak",
                        f"{len(rules)} horizontal rules in one file"))

    # §24 a heading restated by the sentence under it.
    for i, b in enumerate(bs):
        if not b["heading"] or i + 1 >= len(bs):
            continue
        nxt = bs[i + 1]
        if nxt["heading"]:
            continue
        hw = set(words_of(HEADING_RE.match(b["text"]).group(2)))
        pw = words_of(" ".join(nxt["text"].split()))
        if not hw or len(pw) > 6:
            continue
        if len(hw & set(pw)) / len(hw) >= 0.6:
            add(Finding(rel, nxt["start"], "§24", "strong",
                        f"first sentence restates the heading: "
                        f"{' '.join(nxt['text'].split())}"))


# ------------------------------------------------------------ fact drift

CODE_SPAN_FACT_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)*\b")
HEADING_FACT_RE = re.compile(r"(?m)^#+ .*$")
# A requirement level is a fact: "must" and "should" oblige different
# things, so a rewrite that trades one for the other changed the document
# whatever it did to the sentence. "must not" is matched before "must" so
# a prohibition is never counted as an obligation.
MODAL_RE = re.compile(
    r"\b(?:must not|must|shall|should|may|never|required|prohibited)\b",
    re.I)


def code_blocks(text: str) -> list:
    out, cur, fence = [], None, None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence, cur = m.group(1)[0], [line]
            continue
        cur.append(line)
        if m and m.group(1)[0] == fence:
            out.append("\n".join(cur))
            fence, cur = None, None
    if cur:
        out.append("\n".join(cur))
    return out


def facts(text: str) -> dict:
    """The classes a rewrite must preserve, each as a multiset. Sentences
    may change freely; these may not."""
    return {
        "number": Counter(NUMBER_RE.findall(text)),
        "heading": Counter(h.strip() for h in HEADING_FACT_RE.findall(text)),
        "inline code": Counter(m.group(0)
                               for m in CODE_SPAN_FACT_RE.finditer(text)),
        "code block": Counter(code_blocks(text)),
        "link target": Counter(LINK_TARGET_RE.findall(text)),
        # Prose only: a modal inside a code sample is an argument name,
        # not a promise to the reader.
        "requirement level": Counter(
            " ".join(m.group(0).lower().split())
            for m in MODAL_RE.finditer("\n".join(mask(text)))),
    }


def _short(items) -> str:
    out = []
    for value, n in sorted(items.items()):
        one = " ".join(value.split())
        if len(one) > 60:
            one = one[:57] + "..."
        out.append(one if n == 1 else f"{one} (x{n})")
    return ", ".join(out)


def git_root(path: Path):
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           cwd=str(path.parent), capture_output=True,
                           text=True, check=False)
    except OSError:
        return None
    return Path(r.stdout.strip()) if r.returncode == 0 else None


def check_facts(path: Path, rel: str, rev: str, add, note):
    """Compare the working copy against `git show REV:path`, run from the
    file's own repository root so a scan can cross repositories."""
    top = git_root(path.resolve())
    if top is None:
        return
    try:
        inside = path.resolve().relative_to(top.resolve()).as_posix()
    except ValueError:
        return
    old = subprocess.run(["git", "show", f"{rev}:{inside}"], cwd=str(top),
                         capture_output=True, text=True, errors="replace",
                         check=False)
    if old.returncode != 0:
        note(f"{rel}: new in working copy (absent from {rev}), "
             f"fact check skipped")
        return
    before = facts(old.stdout)
    after = facts(path.read_text(encoding="utf-8", errors="replace"))
    drifted = False
    for cls in before:
        dropped = before[cls] - after[cls]
        added = after[cls] - before[cls]
        if dropped:
            drifted = True
            add(Finding(rel, 0, "facts", "drift",
                        f"{cls}(s) dropped since {rev}: {_short(dropped)}"))
        if added:
            drifted = True
            add(Finding(rel, 0, "facts", "drift",
                        f"{cls}(s) added since {rev}: {_short(added)}"))
    return drifted


# ------------------------------------------------------------------ scan

def iter_files(paths, globs=DEFAULT_GLOBS):
    """The files to scan: a directory contributes its matches for every
    glob, a file contributes itself. Sorted per root and de-duplicated by
    real path, so a run is reproducible and an overlapping --root/--file
    pair is scanned once."""
    seen: dict = {}
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for g in globs:
                for f in sorted(p.rglob(g)):
                    if f.is_file():
                        seen.setdefault(f.resolve(), f)
        elif p.is_file():
            seen.setdefault(p.resolve(), p)
    return list(seen.values())


def sample_rate(path: Path) -> float:
    """A writing sample's own dash rate. The skill lets a sample override
    §8, so the sample sets the allowance instead of the default."""
    mlines = mask(path.read_text(encoding="utf-8", errors="replace"))
    words = count_words(mlines)
    return (len(dash_hits(mlines)) * 1000.0 / words) if words else 0.0


def scan(paths, globs=DEFAULT_GLOBS, strict=False, sample=None,
         changelog_ok=False, against=None, relative_to=None):
    """Every tell over `paths`, in file order then line order, plus the
    totals. The dash rate is measured over the whole scan, since one dash
    is weak alone and a text full of them is not."""
    allowance = 0.0 if strict else (
        sample_rate(Path(sample)) if sample else DEFAULT_DASH_PER_1000)
    report = Report(allowance=allowance)
    findings: list = []
    add = findings.append
    dashes = []
    for f in iter_files(paths, globs):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue          # binary or unreadable: carries no prose
        rel = (f.relative_to(relative_to).as_posix()
               if relative_to else f.as_posix())
        mlines = mask(text)
        report.files += 1
        report.words += count_words(mlines)
        for n, hit in dash_hits(mlines):
            dashes.append((rel, n, hit))
        stem = f.name.lower()
        prev_ok = changelog_ok or stem.startswith(CHANGELOG_NAMES)
        detectors = list(LINE_DETECTORS)
        if not prev_ok:
            detectors.append(PREV_VERSION)
        for n, line in enumerate(mlines, 1):
            starts = None
            for rule, severity, rx, initial in detectors:
                for m in rx.finditer(line):
                    if initial:
                        if starts is None:
                            starts = sentence_starts(line)
                        if m.start() not in starts:
                            continue
                    add(Finding(rel, n, rule, severity,
                                " ".join(m.group(0).split())))
        structural(rel, mlines, add)
        if against:
            check_facts(f, rel, against, add, report.notes.append)

    report.dashes = len(dashes)
    # §8 is a rate, not an event: the dashes become findings only once the
    # scan as a whole is over its allowance.
    if report.rate > allowance + 1e-9:
        for rel, n, hit in dashes:
            add(Finding(rel, n, "§8", "strong",
                        f"dash as connector ('{hit}'), "
                        f"{report.rate:.1f}/1000 over an allowance of "
                        f"{allowance:.1f}/1000"))

    # A weak tell needs company: three in one paragraph is a cluster, and
    # the cluster fails where its members alone would not.
    by_para = defaultdict(list)
    for f in findings:
        if f.severity == "weak":
            by_para[(f.path, f.line)].append(f)
    para_index = {}
    for f in iter_files(paths, globs):
        rel = (f.relative_to(relative_to).as_posix()
               if relative_to else f.as_posix())
        try:
            para_index[rel] = paragraph_ids(
                mask(f.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, OSError):
            continue
    clustered = defaultdict(list)
    for (rel, line), fs in by_para.items():
        pid = para_index.get(rel, {}).get(line)
        if pid is not None:
            clustered[(rel, pid)].extend(fs)
    for (rel, _), fs in sorted(clustered.items()):
        if len(fs) >= WEAK_CLUSTER_SIZE:
            rules = ", ".join(sorted({x.rule for x in fs}))
            add(Finding(rel, min(x.line for x in fs), "cluster", "cluster",
                        f"{len(fs)} weak tells in one paragraph ({rules})"))

    report.findings = sorted(findings, key=lambda f: (f.path, f.line, f.rule))
    return report


def failing(report, strict=False):
    """What fails a run: every strong tell, every weak cluster, every fact
    drift, and, under --strict, the weak tells too."""
    return [f for f in report.findings
            if f.severity in ("strong", "cluster", "drift")
            or (strict and f.severity == "weak")]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", metavar="DIR",
                    help="directory to scan recursively "
                         "(repeatable; default: .)")
    ap.add_argument("--file", action="append", metavar="PATH", default=[],
                    help="one file to scan whatever --glob says (repeatable)")
    ap.add_argument("--glob", action="append", metavar="PAT",
                    help="filename pattern under each --root "
                         "(repeatable; default: *.md)")
    ap.add_argument("--against", metavar="REV",
                    help="git revision the facts must survive")
    ap.add_argument("--strict", action="store_true",
                    help="weak tells fail too, and no dash is allowed")
    ap.add_argument("--sample", metavar="FILE",
                    help="writing sample whose dash rate sets the allowance")
    ap.add_argument("--changelog-ok", action="store_true",
                    help="this text is about change, so §25 does not apply")
    args = ap.parse_args()

    # "." is the default only when the caller named nothing at all. A bare
    # --file must scan that file and nothing else: silently widening a scan
    # to the whole tree is the surprising direction for a gate to fail in.
    roots = args.root or ([] if args.file else ["."])
    globs = tuple(args.glob or DEFAULT_GLOBS)
    named = roots + args.file
    missing = [p for p in named if not Path(p).exists()]
    if args.sample and not Path(args.sample).is_file():
        missing.append(args.sample)
    if missing:
        for p in missing:
            print(f"  !! no such path: {p}")
        return 2

    files = iter_files([Path(p) for p in named], globs)
    # A scan over an empty set is a green lie: a mistyped --glob would
    # otherwise print the same PASS a real scan earns.
    if not files:
        print(f"  !! matched 0 files ({' '.join(globs)} under "
              f"{', '.join(named)}) — refusing a vacuous pass")
        return 2

    report = scan(files, globs=globs, strict=args.strict, sample=args.sample,
                  changelog_ok=args.changelog_ok, against=args.against)
    for f in report.findings:
        print(f"  {f.render()}")
    for n in report.notes:
        print(f"  {n}")
    bad = failing(report, strict=args.strict)
    tail = (f"{report.files} file(s), {report.words} words, "
            f"dashes {report.rate:.1f}/1000")
    if bad:
        clusters = sum(1 for f in bad if f.severity == "cluster")
        drift = len({f.path for f in bad if f.severity == "drift"})
        tells = len(bad) - clusters - sum(1 for f in bad
                                          if f.severity == "drift")
        print(f"prose lint: FAIL — {tells} strong tell(s), "
              f"{clusters} weak cluster(s), fact drift in {drift} file(s) "
              f"— {tail}")
        return 1
    print(f"prose lint: PASS — {tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
