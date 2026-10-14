# jsoup — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A Java HTML parser that implements the WHATWG HTML5 parsing algorithm: it turns
any HTML, however malformed, into a DOM the way a browser would, then lets code
query it with CSS selectors (and XPath), read and change it, serialize it, and
clean untrusted HTML against an allow-list. It also has a small HTTP client
(`Jsoup.connect`) for fetching and parsing a page in one step. Common uses: test
assertions on server-rendered HTML, scraping, and sanitizing user-supplied
HTML.

- `org.jsoup:jsoup`: the whole library, one jar with no required runtime
  dependencies.

Upstream home: https://jsoup.org/ (cookbook and API reference) and the
`jhy/jsoup` repository. Licence: MIT.

## Install, setup and configuration
- One dependency, `org.jsoup:jsoup`, with an explicit version: the common
  framework BOMs do not manage it. Declare it `<scope>test</scope>` when it only
  parses responses in tests. The minimum Java version is Java 8 (the 1.19.1
  release notes restate it); from 1.19.1 the jar is a multi-release jar with
  Java 11+ classes beside the Java 8 ones, so a shaded or fat jar must keep
  the multi-release manifest entry.
- **Parser choice** is the main setting. `Jsoup.parse(html)` uses the HTML
  parser (`Parser.htmlParser()`), which "treats input as HTML5, and enforces the
  creation of a normalised document". `Parser.xmlParser()` "assumes no knowledge
  of the incoming tags and does not treat it as HTML" and builds the tree as
  written. Pass a parser with `Jsoup.parse(html, baseUri, parser)`.
- **Parser settings:** `setTrackErrors(maxErrors)` then `getErrors()` records
  parse errors (off by default); `setMaxDepth(n)` caps the number of open
  elements. The HTML parser defaults to a depth of 512 from 1.22.1, and from
  1.23.2 the XML parser defaults to the same 512 (before that it was
  unlimited unless set).
- **Base URI:** `parse(html, baseUri)` resolves relative URLs; with no base URI,
  `absUrl` and `attr("abs:href")` work only when the HTML carries a
  `<base href>`.
- **Output settings** (`document.outputSettings()`): `prettyPrint` defaults to
  true, so `html()` and `outerHtml()` re-indent the markup; turn it off to get
  output that "will generally look like the input". `syntax(xml)` emits
  self-closing tags and switches the escape mode to `xhtml`.
- **HTTP client defaults** (`Connection`): a total request timeout of 30 s (0
  means infinite), a 2 MB body cap (the body is truncated beyond it; 0 means
  unlimited), redirects followed, an `IOException` on 4xx/5xx unless
  `ignoreHttpErrors(true)`, and an `IOException` on an unrecognised content type
  unless `ignoreContentType(true)`. Only `http` and `https` URLs are accepted.
  `Jsoup.newSession()` keeps settings and cookies across requests. HTTP/2 on
  Java 11+ arrived in 1.19.1 as an opt-in (`jsoup.useHttpClient=true`, the JDK
  `HttpClient`); from 1.21.1 the JDK `HttpClient` is the default when present
  (`-Djsoup.useHttpClient=false` turns it off).

## Core API / usage shape
- **Parse:** `Jsoup.parse(String)`, `Jsoup.parse(String, baseUri)`,
  `Jsoup.parse(File|Path, charset)`, and `Jsoup.parseBodyFragment(html)` for a
  fragment that should land inside `<body>`. Parsing a non-null string always
  succeeds and yields a `Document` with at least a head and a body.
- **Select:** `element.select(css)` returns `Elements` (a `List<Element>`);
  `selectFirst(css)` returns the first match or null; `expectFirst(css)` (from
  1.15.2) throws `IllegalArgumentException` when nothing matches. Selector
  syntax covers tag, `#id`, `.class`, attribute forms (`[attr]`, `[attr=val]`,
  `[attr^=…]`, `[attr$=…]`, `[attr*=…]`, `[attr~=regex]`, `[^data-]`),
  combinators (`E F`, `E > F`, `E + F`, `E ~ F`, `E, F`) and pseudo-selectors
  such as `:has()`, `:not()`, `:contains()`, `:containsOwn()`.
- **Read:** `attr(key)`, `hasAttr(key)`, `absUrl(key)`; `text()` (the
  normalized text of the element and its children), `ownText()` (this element's
  own text only), `wholeText()` (source whitespace kept, `<br>` as newline);
  `html()` and `outerHtml()`; `id()`, `tagName()`, `className()`,
  `hasClass(name)`. On `Elements`, `attr(key)` returns the value from the first
  element that has it, `hasAttr` is true if any has it, and `eachAttr` lists the
  values of those that have it.
- **Modify:** every accessor has a setter (`attr(key, value)`, `text(...)`,
  `html(...)`), plus `append`, `remove`, `wrap` and kin.
- **Clean:** `Jsoup.clean(bodyHtml, Safelist)` returns safe HTML;
  `Jsoup.isValid(bodyHtml, Safelist)` tests input against a safelist;
  `new Cleaner(safelist).clean(document)` cleans a whole `Document`.
- **Fetch:** `Jsoup.connect(url).get()` / `.post()` fetches and parses;
  `.execute()` returns the raw `Response`.

## Idioms & best practices
- Parse server-rendered HTML with the HTML parser, never the XML parser. HTML5
  output is not guaranteed to be well-formed XML (void elements, optional end
  tags, boolean attributes), and the XML parser would build a different tree
  from what a browser builds. Parse a partial response (a fragment returned for
  an in-page swap) with `parseBodyFragment` or plain `parse`, both of which
  wrap it in a body.
- Use `expectFirst` when the element must exist, so a miss fails at the lookup
  with the selector in the message rather than as a later null dereference.
- Assert attribute presence with `hasAttr` or an `[attr]` selector, not by
  comparing `attr(...)` to an empty string (pitfalls).
- Prefer `text()` for what a reader sees and `ownText()` when children must not
  count; use `wholeText()` only when whitespace matters.
- Give `parse` the page's URL as base URI whenever relative links will be read
  as absolute URLs.
- For sanitizing, start from the narrowest `Safelist` that fits (`none`,
  `simpleText`, `basic`, `basicWithImages`, `relaxed`) and widen it with
  `addTags`/`addAttributes`/`addProtocols` only as needed.

## General pitfalls
- **`attr()` on a missing attribute returns `""`, not null** ("to avoid
  nulls"); `absUrl` does the same when the attribute is missing or cannot be
  made absolute. An assertion such as `attr("aria-hidden")` equal to `""`
  passes both for a present empty attribute and for no attribute at all; use
  `hasAttr`.
- **Parsing never fails.** The HTML parser repairs any input, so a markup typo
  is not caught by parsing; assert on structure, or enable `setTrackErrors` and
  inspect `getErrors()`.
- **Selectors are case-insensitive,** including attribute values:
  `[data-state=Open]` also matches `open`. Compare values in code when case
  matters.
- **`:contains()` searches descendants as well;** `:containsOwn()` matches only
  the element's own text.
- **Pretty-printing rewrites whitespace** in `html()`/`outerHtml()` output;
  turn it off before comparing serialized markup.
- **`Jsoup.clean` treats its input as a body fragment.** It drops relative URLs
  unless a base URI is given and `preserveRelativeLinks(true)` is set; to clean
  a full document, use `Cleaner.clean(Document)` and allow the structural
  tags. Its output is still HTML even with `Safelist.none()`; call `text()` for
  plain text.
- **`isValid` does not replace `clean`:** upstream says input must always be
  normalized with `clean` before it is stored or shown, so enforced attributes
  are set and browser/jsoup parse differences are normalized.
- **`Whitelist` is gone.** It was renamed `Safelist` in 1.14.1 with a deprecated
  shim, and the shim was removed in 1.15.1.
- **The HTTP client truncates at 2 MB** by default ("the input truncated"):
  raise `maxBodySize` (0 for no cap) for large pages.

## Testing
- In web-layer tests, parse the response body
  (`Jsoup.parse(response.getContentAsString())` with a mock-MVC style harness)
  and assert with selectors: element present, count, text, attributes. It reads
  the HTML the server sent, without a browser, so it cannot prove anything that
  needs JavaScript, CSS, focus or layout; those need a real browser
  ([`playwright.md`](playwright.md)).
- Wrap the parse and the common lookups in a small test helper (one place that
  chooses the parser and turns a missing element into a readable failure).
- `Element.toString()` returns `outerHtml()`, which makes assertion failure
  messages readable.

## Security defaults
- Upstream describes the cleaner's parse as running "in a safe, sand-boxed
  environment": jsoup builds a tree from the markup and has no script engine.
- The cleaner is an allow-list sanitizer: it parses the input and lets only
  known-safe tags, attributes and URL protocols through, without regular
  expressions. `Safelist.basic()` enforces `rel=nofollow` on off-site links and
  allows no images; `relaxed()` allows structural HTML and images and does not
  add `nofollow`. Widening a safelist (adding attributes such as `style` or
  event handlers, or protocols such as `javascript`) reopens what the cleaner
  exists to block.
- URLs in cleaned output are made absolute by default
  (`preserveRelativeLinks` is false).
- `Jsoup.connect` follows redirects and accepts any `http`/`https` URL it is
  given: feeding it user-supplied URLs makes the server fetch arbitrary hosts.
  Validate the destination before fetching.
- The HTML parser's default depth cap of 512 (from 1.22.1) bounds stack growth
  on deeply nested input.

## Operational behaviour
- A parse builds the whole DOM in memory; very large documents cost memory in
  proportion. Upstream's cookbook covers a `StreamParser` for large documents.
- A configured `Cleaner` may be reused across concurrent threads, provided the
  shared `Safelist` is not mutated while in use (documentation clarified in
  1.22.2).

## Interop
- [`spring-framework.md`](spring-framework.md): the mock-MVC response body is
  the usual input in web-layer tests.
- [`thymeleaf.md`](thymeleaf.md): its HTML5 output is what such tests parse,
  with the HTML parser.
- [`playwright.md`](playwright.md): the real-browser counterpart for
  behaviour jsoup cannot see.

## Major lines
jsoup has stayed on the 1 major line. Behaviour and API changes arrive in minor
releases (the `Whitelist` removal in 1.15.1, the depth cap in 1.22.1, the
XML-parser depth default in 1.23.2), and deprecated APIs are announced with the
release that will remove them. Read `CHANGES.md` for each bump.

## Upstream docs
- Cookbook: https://jsoup.org/cookbook/
- Parse a document from a String: https://jsoup.org/cookbook/input/parse-document-from-string
- Extract attributes, text and HTML: https://jsoup.org/cookbook/extracting-data/attributes-text-html
- Sanitize untrusted HTML: https://jsoup.org/cookbook/cleaning-html/safelist-sanitizer
- Load a document from a URL: https://jsoup.org/cookbook/input/load-document-from-url
- API reference: https://jsoup.org/apidocs/ (`Jsoup`, `Node`, `Element`, `Elements`, `Parser`, `Selector`, `Safelist`, `Cleaner`, `Connection`, `Document.OutputSettings`)
- Changes: https://github.com/jhy/jsoup/blob/master/CHANGES.md and `change-archive.txt` for releases up to 1.17.1
- Source: https://github.com/jhy/jsoup
