# pdfbox — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Apache PDFBox is a low-level Java library for creating, reading, editing,
rendering, signing and extracting text from PDF documents. It works at the
level of pages, content streams, fonts and the PDF object model: it draws text
and graphics at coordinates you give it, and has no layout engine (no
paragraphs, line wrapping or tables). Upstream home: https://pdfbox.apache.org
(per-line docs under `/3.0/` and `/2.0/`), source at
https://github.com/apache/pdfbox. All components share the groupId
`org.apache.pdfbox`.

- `org.apache.pdfbox:pdfbox`: the main library (`PDDocument`, pages, content
  streams, fonts, text extraction, rendering, forms, encryption, signatures);
  needed for any PDF work, and it brings `fontbox` and, on the 3.0 line,
  `pdfbox-io` with it.
- `org.apache.pdfbox:fontbox`: font parsing (TrueType, OpenType, CFF, Type 1)
  and font metrics; needed directly only when code reads a font's glyphs or
  metrics itself (`TTFParser`, `TrueTypeFont`).
- `org.apache.pdfbox:pdfbox-io`: the IO classes (readers, stream caches),
  split into their own module on the 3.0 line.
- `org.apache.pdfbox:xmpbox`: XMP metadata; needed only to read or write a
  document's XMP stream (PDF/A, for instance). Upstream's dependencies page
  says declaring `pdfbox` brings `xmpbox` transitively, but the 3.0 line's
  `pdfbox` POM declares no dependency on it: declare it on its own when it is
  needed, and check the resolved tree.
- `org.apache.pdfbox:preflight`: PDF/A-1b validation; needed only to validate.
- `org.apache.pdfbox:pdfbox-tools` and the `pdfbox-app` jar: the command-line
  tools; not a library dependency.

## Install, setup and configuration
- Declare `org.apache.pdfbox:pdfbox`. Spring Boot's BOM does not manage it, so
  the version is set explicitly. Runtime needs Java 8 (both lines) and
  `commons-logging`, which wraps whatever logging library is present or falls
  back to `java.util.logging`.
- **Optional components, picked up when on the classpath:** JBIG2 image
  reading (`org.apache.pdfbox:jbig2-imageio`), JPEG 2000 reading and TIFF
  writing (`com.github.jai-imageio:jai-imageio-core` and
  `jai-imageio-jpeg2000`), more reliable JPEG decoding (TwelveMonkeys
  `imageio-jpeg`). Without them, those image formats are disabled and a
  warning is logged. Upstream flags the JAI licences as incompatible with
  Apache 2.0: check them before adding. Public-key encryption and signing need
  Bouncy Castle (the dependencies page names `bcprov`, `bcpkix` and `bcmail`;
  the `pdfbox` POM declares the first two optional), so a project that signs
  adds them itself.
- **Stream cache** (3.0): a document buffers the streams it writes through a
  `StreamCacheCreateFunction`. `IOUtils.createMemoryOnlyStreamCache()` keeps
  them in unrestricted main memory, `IOUtils.createTempFileOnlyStreamCache()`
  uses a `ScratchFile` of unrestricted size on disk, and
  `() -> new ScratchFile(MemoryUsageSetting.setupMixed(maxMainMemoryBytes))`
  mixes the two. `new PDDocument()` and the `Loader.loadPDF` overloads without
  a cache argument use the memory-only cache.
- **Compression:** from 3.0, `save` writes compressed object streams by
  default; `save(out, CompressParameters.NO_COMPRESSION)` turns that off (PDF/A-1b
  needs it).

## Core API / usage shape
- **Create:** `try (PDDocument doc = new PDDocument()) { PDPage page = new
  PDPage(PDRectangle.A4); doc.addPage(page); try (PDPageContentStream cs = new
  PDPageContentStream(doc, page)) { cs.beginText(); cs.setFont(font, 11);
  cs.newLineAtOffset(x, y); cs.showText(text); cs.endText(); } doc.save(out);
  }`. Coordinates are in points (1/72 inch) from the bottom-left corner of the
  page. Close each content stream before saving, or the page comes out empty.
- **Load (3.0):** `Loader.loadPDF(...)` from a `byte[]`, a `File`, or a
  `RandomAccessRead` (`RandomAccessReadBuffer` in memory,
  `RandomAccessReadBufferedFile` with a page cache over a file,
  `RandomAccessReadMemoryMappedFile`), with optional password, key store and
  stream cache. There is no `InputStream` overload: wrap the stream in
  `new RandomAccessReadBuffer(inputStream)`, which copies it into memory.
  `Loader.loadFDF` does the same for FDF.
- **Fonts:** `PDType0Font.load(doc, file or inputStream)` embeds a TrueType
  font as a Type 0 (CID) font and subsets it on `save`; the three-argument
  form takes `embedSubset` (false when the font is for an AcroForm).
  `PDType0Font.load(doc, trueTypeFont, embedSubset)` reuses an already parsed
  FontBox font. The standard 14 fonts need no file:
  `new PDType1Font(Standard14Fonts.FontName.HELVETICA)` on 3.0
  (`PDType1Font.HELVETICA` on 2.0); they are not embedded and are limited to
  WinAnsiEncoding.
- **Images:** `PDImageXObject.createFromByteArray(doc, bytes, name)` or
  `PDImageXObject.createFromFile(path, doc)` (note the argument order), drawn with `cs.drawImage(image, x, y, w, h)`.
- **Text extraction:** `new PDFTextStripper().getText(doc)`, with
  `setSortByPosition(true)` for reading order by position and
  `setStartPage`/`setEndPage` for a range.
- **Rendering:** `new PDFRenderer(doc).renderImageWithDPI(pageIndex, dpi)`.
- **Metadata:** `doc.getDocumentInformation()` returns the `/Info` dictionary
  (title, author, subject, keywords, creator, producer, dates), created empty
  if absent. PDF 2.0 deprecates it except `/CreationDate` and `/ModDate`; the
  XMP stream (`PDDocumentCatalog.setMetadata`, with `xmpbox`) is the PDF 2.0
  home for the rest.
- **Forms:** `doc.getDocumentCatalog().getAcroForm()` (with fix-ups, below),
  `getFieldTree()` for every field rather than `getFields()`, which returns only
  the root fields.

## Idioms & best practices
- Open every `PDDocument` and `PDPageContentStream` in try-with-resources;
  every document object created must be closed, including the one a load
  replaced.
- **Load each font once per document.** A `PDType0Font` is bound to the
  document it was loaded into: that document subsets it at `save` and closes
  it at `close`. Load it once per document and reuse it on every page; a font
  object is never shared across documents. Observed in practice: each weight
  loaded once per document from bytes read off the classpath, with a test
  asserting `PDFont.isEmbedded()`.
- Choose the stream cache on purpose. The memory-only default writes nothing
  to disk, which suits short documents generated in a request (observed in
  practice: a generator built with `new
  PDDocument(IOUtils.createMemoryOnlyStreamCache())` wrote nothing under
  `java.io.tmpdir`, and a test asserted it). For large inputs or outputs, bound
  memory with a mixed or temp-file cache.
- **Filter text to the font's glyphs before drawing.** A code point the
  embedded font lacks makes `showText` throw (General pitfalls). Observed in
  practice: parse the font with FontBox (`new TTFParser().parse(new
  RandomAccessReadBuffer(bytes))`), collect the code points its Unicode cmap
  maps (`getUnicodeCmapLookup()`), and replace anything outside that set
  before it reaches the content stream. The same parse gives advance widths
  (`getAdvanceWidth(gid) * 1000 / getUnitsPerEm()`, in text-space units) for
  measuring and wrapping text, which PDFBox does not do for you.
- Set the metadata you want to publish explicitly (`setTitle`, `setProducer`,
  ...). Observed in practice: a document created and saved by PDFBox carried
  no Producer entry and no XMP stream unless the application set them; the
  3.0 writer's source contains no code that fills them.
- For paragraph and table layout, use one of the layout libraries upstream's
  FAQ lists on top of PDFBox, or Apache FOP, rather than hand-coding a layout
  engine.

## General pitfalls
- **3.0 removed every load method from `PDDocument`.** `PDDocument.load(...)`
  is gone; use `Loader.loadPDF(...)` (no `InputStream` overload, see Core API).
  The `MemoryUsageSetting` load parameter became a `StreamCacheCreateFunction`.
- **Missing glyphs throw when text is shown.** With a `PDType0Font`, a code
  point the font has no glyph for throws `IllegalArgumentException` ("No glyph
  for U+XXXX ... in font ...") from `showText`, while the content stream is
  written. With a standard 14 font, a character outside WinAnsiEncoding throws
  "is not available in this font's encoding"; upstream's fix is to embed a font
  with `PDType0Font.load`.
- **Static standard-14 font instances were removed in 3.0;** construct
  `PDType1Font` with `Standard14Fonts.FontName`, and cache the instance
  yourself if wanted.
- **RGB as `int` triples compiles but fails on 3.0.** The 0-255 `int`
  overloads of `setStrokingColor` and `setNonStrokingColor` were removed; the
  call now resolves to the float overload, which accepts only 0-1 and throws at
  runtime. Pass a `java.awt.Color` or floats.
- **Never save over the input file;** parts of it are read during the save,
  which corrupts it.
- **Do not use a document after `close()`,** nor an encrypted document after
  `save`: 3.0 parses lazily, so a closed document can return wrong results
  instead of failing.
- **Not thread-safe:** one thread per `PDDocument`. Separate documents can be
  processed in parallel.
- **AcroForm fix-ups.** On 3.0, `getAcroForm()` applies fixes that mimic Adobe
  Reader (default font resources, fields from orphaned widgets, appearance
  streams); `getAcroForm(null)` skips them.
- **Complex-script shaping can change Latin output on 3.0.** GSUB support
  (Latin ligatures, some Indic scripts) may alter glyphs even in text that is
  not Indic; `TrueTypeFont.setEnableGsub(false)` turns it off. The 3.0 line
  shapes only one script per font, does not support GPOS, and offers
  AWT-based and FOP-based layout artifacts for fuller shaping.
- `importPage` is for pages from a loaded document, not from a document being
  generated, which can hold unfinished parts such as font subsetting data.
- A font loaded from the classpath that works from a file but not as a
  resource is usually corrupted by Maven resource filtering: exclude font
  files from filtering.

## Testing
- Round-trip what was generated: load the output with `Loader.loadPDF(bytes)`
  and assert with `PDFTextStripper` on the text, `getDocumentInformation()` on
  metadata, and `PDFont.isEmbedded()` on fonts. Observed in practice: a writer
  test extracted real non-ASCII text back from a PDF made with an embedded
  font.
- A subset font's name in the output carries a six-letter tag and a `+`
  before the font's own name (`ABCDEF+FontName`); assert it when subsetting
  matters.
- Assert the absence of temporary files (nothing new under `java.io.tmpdir`
  during a run) when a memory-only cache is a requirement.
- Text extraction follows content-stream order, so assert with
  `setSortByPosition(true)` when position defines reading order.

## Security defaults
- PDF parsing is where PDFBox's exposure lies; a service that only writes PDFs
  and parses no external file avoids most of it. For untrusted input, bound
  memory with a mixed or temp-file stream cache and a JVM heap limit, since the
  memory-only default is unrestricted.
- Text extraction respects the document's permission bits: a document that
  forbids extraction needs the owner password.
- Encryption is applied with `doc.protect(new StandardProtectionPolicy(owner,
  user, accessPermission))` before `save`; public-key encryption needs Bouncy
  Castle.
- Parsing a signed PDF does not verify or validate its signatures (DocMDP and
  usage-rights constraints included); upstream's `ShowSignature` example is a
  partial check, not a validator.
- Document metadata is whatever the application writes: check `/Info` and XMP
  before publishing a document that should not reveal its producer or author.

## Operational behaviour
- 3.0 parses incrementally (on demand), lowering the initial memory footprint;
  iterating all pages, reading annotations or signing can still load the whole
  document.
- Reading no longer uses a scratch file on 3.0; writing buffers streams in the
  configured cache. `RandomAccessReadBufferedFile` keeps a FIFO page cache of
  up to 1000 pages of 4 KB; a memory-mapped reader is limited to
  `Integer.MAX_VALUE` bytes, and PDFBox unmaps it itself to avoid locked files
  on Windows.
- Rendering memory grows with resolution: lower the DPI or scale, enable
  `setSubsamplingAllowed(true)`, do not hold rendered images, and close
  documents (upstream's OutOfMemoryError advice).
- Font subsetting happens during `save`, so a save with large embedded fonts
  costs CPU there.

## Interop
- FontBox (bundled) for font parsing; XMPBox for XMP metadata; Bouncy Castle
  for signatures and public-key encryption; JAI Image I/O and TwelveMonkeys for
  image formats.
- Layout libraries built on PDFBox (upstream's FAQ lists several) and Apache
  FOP for document layout.
- An embedded TrueType font's own licence governs embedding and subsetting;
  record it with the font, not here.

## Major lines
### 2.0
- `PDDocument.load(...)` overloads, with an optional `MemoryUsageSetting`;
  `new PDDocument()` uses main memory only. Static standard-14 font
  constants (`PDType1Font.HELVETICA`). `int` RGB colour overloads. Saving
  without object-stream compression (the 3.0 guide introduces compressed
  saving as the new default).

### 3.0
- Java 8 minimum. Every API deprecated on 2.0 is removed, except the
  deprecated `PDPageContentStream` calls, which stay but are treated as
  internal.
- New `pdfbox-io` module built on `java.nio`: `RandomAccessRead`
  readers, `RandomAccessStreamCache` caches, no scratch file when reading.
- `org.apache.pdfbox.Loader` replaces the `PDDocument.load` methods; the
  stream cache is a `StreamCacheCreateFunction`.
- Compressed saving by default; incremental parsing; static standard-14
  fonts removed; `int` colour overloads removed; annotation creation moves to
  the concrete subclasses (`PDAnnotationHighlight`, `PDAnnotationSquare`, ...);
  `org.apache.pdfbox.util.Charsets` removed in favour of
  `java.nio.charset.StandardCharsets`; `COSDocument.getObjects()` replaced by
  the xref table keys with `getObjectFromPool()`; AcroForm fix-ups on
  `getAcroForm()`; rewritten command-line app with exit codes and
  `--help`/`--version`.
- Latin ligatures and Bengali shaping from 3.0.0, Devanagari and Gujarati from
  3.0.2, `TrueTypeFont.setEnableGsub(false)` from 3.0.3.

## Upstream docs
- 3.0 migration guide: https://pdfbox.apache.org/3.0/migration.html
- 3.0 FAQ: https://pdfbox.apache.org/3.0/faq.html
- 3.0 dependencies: https://pdfbox.apache.org/3.0/dependencies.html
- Getting started: https://pdfbox.apache.org/3.0/getting-started.html
- Examples (fonts, images, signing): https://github.com/apache/pdfbox/tree/3.0/examples
- Source: https://github.com/apache/pdfbox
