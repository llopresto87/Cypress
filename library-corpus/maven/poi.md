# poi — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Apache POI is the pure-Java library for reading and writing Microsoft Office
file formats: Excel (`.xls` and `.xlsx`), Word, PowerPoint, Visio and Outlook
files. Most projects use it to write spreadsheet exports, or to read uploaded
spreadsheets. It ships as several jars under the group `org.apache.poi`:

- `org.apache.poi:poi`: the core jar. It holds the OLE2 file system (POIFS),
  document property sets (HPSF), the binary Excel format (HSSF, `.xls`) and
  the format-neutral `org.apache.poi.ss.usermodel` interfaces. Needed for
  every use.
- `org.apache.poi:poi-ooxml`: the Office Open XML formats: XSSF (`.xlsx`),
  its streaming writer SXSSF, XWPF (`.docx`), XSLF (`.pptx`), XDGF (`.vsdx`)
  and the OPC package layer (OpenXML4J). Needed for any `.xlsx` work, and for
  `WorkbookFactory`, which needs `poi-ooxml` even when it only opens `.xls`.
- `org.apache.poi:poi-ooxml-lite`: the XMLBeans-compiled OOXML schemas that
  the unit tests exercise. `poi-ooxml` depends on it, so it arrives
  transitively.
- `org.apache.poi:poi-ooxml-full`: every OOXML schema class. Needed only when
  code touches a part of the format that the lite jar leaves out (see General
  pitfalls).
- `org.apache.poi:poi-scratchpad`: the less mature older binary formats
  (HWPF `.doc`, HSLF `.ppt`, HDGF, HPBF, HSMF `.msg`, HWMF). Needed only for
  those.

POI follows semantic versioning from 4.0.0. Upstream home:
https://poi.apache.org/ (docs, component map, FAQ) and the source at
https://github.com/apache/poi.

## Install, setup and configuration
- **Coordinates.** For `.xlsx`, declare `org.apache.poi:poi-ooxml`. It brings
  `poi`, `poi-ooxml-lite`, XMLBeans, `commons-compress`, `commons-io`,
  `curvesapi`, `commons-collections4` and `log4j-api`. Signing, PDF and SVG
  support are optional dependencies of `poi-ooxml`, which a project adds
  itself when it uses them.
- **Every POI jar at one version.** Upstream says mixing jars from
  different versions "is not supported, and will fail to work in
  unpredictable ways". The Spring Boot BOM does not manage POI, so a project
  states the version itself. Declare it once (a property, or the jars side by
  side) so the jars move together.
- **XMLBeans version.** Upstream recommends the XMLBeans version the POI
  schemas were built with, and makes no promise about a much newer one. Let
  `poi-ooxml` choose it, unless a BOM in the build overrides it.
- **Logging.** POI logs through the Log4j 2 API (`log4j-api`) and ships no
  logging implementation, so the application's logging backend, reached
  through a provider or a bridge, decides where the output goes.
- **Java.** Upstream recommends running on a long-term-support Java release.
  The 5 line still supports Java 8, and that is why its JPMS module support is
  only partial: illegal-reflective-access warnings on newer JVMs are expected
  and harmless.
- **Temporary files** go under `java.io.tmpdir`, in a `poifiles` directory,
  through the default `TempFileCreationStrategy`. A custom strategy can be
  installed with `TempFile.setTempFileCreationStrategy`. Setting the system
  property `poi.delete.tmp.files.on.exit` adds delete-on-exit to each file. The
  `poifiles` directory itself is never deleted.
- **Hardening and limits** are static settings, documented on upstream's
  configuration page:
  - `ZipSecureFile.setMinInflateRatio` (default 0.01): rejects any package part
    that compresses better than 1%, as a zip bomb.
  - `ZipSecureFile.setMaxEntrySize`: caps the size of one zip entry.
  - `ZipSecureFile.setMaxTextSize`: caps extracted text, about 10 million
    characters by default from 5.1.0.
  - `IOUtils.setByteArrayMaxOverride`: replaces the per-record allocation
    limits.
  - `POIXMLTypeLoader.DEFAULT_XML_OPTIONS`: from 5.1.0, DOCTYPE declarations
    in the embedded XML are disallowed by default.
  - The 5.1.0 settings that move zip entries and package parts to temporary
    files (`ZipInputStreamZipEntrySource.setThresholdBytesForTempFiles`,
    `ZipPackage.setUseTempFilePackageParts`) are off by default, and so is
    their encryption.

## Core API / usage shape
- **Format-neutral interfaces** (`org.apache.poi.ss.usermodel`): `Workbook`,
  `Sheet`, `Row`, `Cell`, `CellStyle`, `Font`, `DataFormat`, `CreationHelper`.
  Code written against them runs on `HSSFWorkbook` (`.xls`), `XSSFWorkbook`
  (`.xlsx`, held fully in memory) and `SXSSFWorkbook` (`.xlsx`, streaming
  write).
- **Open:** `WorkbookFactory.create(File)` picks the format by content.
  Opening from a `File` uses less memory than opening from an `InputStream`,
  which has to be buffered whole. The format-specific equivalents are
  `new XSSFWorkbook(OPCPackage.open(file))` and `new HSSFWorkbook(new
  POIFSFileSystem(file))`.
- **Write:** `wb.createSheet(name)` (an Excel sheet name has at most 31
  characters), `sheet.createRow(i)`, `row.createCell(j)`, then
  `cell.setCellValue(...)` with a `String`, `double`, `boolean`, date or
  `RichTextString`. `wb.write(OutputStream)` serializes the workbook, and
  `wb.close()` releases it. Both `Workbook` and `OPCPackage` are `Closeable`,
  so use try-with-resources.
- **Read:** `cell.getCellType()`, then the matching getter. A numeric getter
  on a string cell throws. Dates are numbers with a date format, so test them
  with `DateUtil.isCellDateFormatted(cell)`. `DataFormatter.formatCellValue(cell)`
  returns the text Excel would display, with the cell's format applied.
- **Styles and fonts** are workbook-level objects (`wb.createCellStyle()`,
  `wb.createFont()`) that cells share by reference.
- **Document metadata:** on an OOXML document, `getProperties()` returns
  `POIXMLProperties`. Its `getCoreProperties()` holds creator, title, dates and
  the like. Its `getExtendedProperties().getUnderlyingProperties()` holds the
  XMLBeans `CTProperties` of `docProps/app.xml`, Application among them.
- **Reading large files:** the event APIs (the HSSF event model, and XSSF's
  SAX-based reader) parse without building the object model. Upstream says
  they cut memory use by more than tenfold, at the cost of a lower-level API.

## Idioms & best practices
- **Pick the workbook class by size.** `XSSFWorkbook` keeps every row in
  memory and allows random access. Upstream says a moderate machine reads or
  writes 100 columns by 100,000 rows in a couple of seconds. `SXSSFWorkbook`
  keeps a sliding window of rows (100 by default; `new SXSSFWorkbook(n)`, or
  `-1` with manual `flushRows`) and spills the older rows to temporary files.
  It exists for very large sheets under a limited heap. Use `XSSFWorkbook`
  when the export must write no temporary file (see General pitfalls).
- **Create styles and fonts once and reuse them.** An `.xlsx` workbook allows
  at most 64,000 cell styles, and any workbook at most 32,767 unique fonts.
  Upstream's "wrong" example creates a style per cell, and that exhausts the
  limit on large sheets.
- **Escape a literal `_xHHHH_` before writing text.** XSSF decodes the
  OOXML escape `_xHHHH_` (a hexadecimal UTF-16 code unit, used for characters
  XML 1.0 cannot hold) whenever it reads a string, and it does not encode on
  write. To keep a value that happens to contain such a pattern, replace each
  underscore that opens one with `_x005F_`, the escaped underscore. Use a
  lookahead so that overlapping sequences are all caught:
  `Pattern.compile("_(?=x[0-9A-Fa-f]{4}_)")` with `replaceAll("_x005F_")`.
- **Clear the generator metadata when it must not leak.** A new
  `XSSFWorkbook` sets Application to "Apache POI" in `docProps/app.xml`, and
  the OPC package sets the core creator to "Generated by Apache POI
  OpenXML4J", with a creation date. To remove both:
  `getProperties().getCoreProperties().setCreator(null)` (a null or empty value
  leaves the property unset), and on
  `getProperties().getExtendedProperties().getUnderlyingProperties()` call
  `unsetApplication()` when `isSetApplication()` is true.
- **Use text cells deliberately.** Write a value that looks like a number (an
  identifier with leading zeros, say) with `setCellValue(String)`, so it stays
  a string cell. Write a real number as a `double` with a `DataFormat`.
- **Newlines in a cell** need a style with `setWrapText(true)`, or Excel shows
  them on one line.
- Open from a `File` rather than a stream when the file is on disk. When
  writing to a slow destination, wrap the output in a `BufferedOutputStream`.

## General pitfalls
- **SXSSF writes temporary files.** It flushes each sheet's rows to a
  temporary XML file, one per sheet, and `write()` also builds the package
  through a temporary file. Upstream's example notes that 20 MB of CSV data can
  become more than a gigabyte of temporary XML. `setCompressTempFiles(true)`
  gzips them. The files stay until the workbook is disposed of: upstream's
  how-to says to call `dispose()`, and the current source deprecates
  `dispose()` because `close()` now does it, so always close the workbook in a
  try-with-resources block. `writeAvoidingTempFiles`
  (from 5.1.0, marked experimental) avoids the write-time file at the cost of
  memory, and upstream says other SXSSF code may still create temporary files.
  Observed in practice: an export requirement of "no temporary file" was met
  only by using `XSSFWorkbook`; a plan to switch to SXSSF for memory would have
  broken it.
- **SXSSF rows leave memory.** Once flushed, a row is no longer reachable
  through `getRow()`. Merged regions, hyperlinks and comments stay in memory
  even under SXSSF. SXSSF writes inline strings by default, and upstream notes
  that some clients do not accept them. The shared-strings option fixes that by
  keeping every unique string in memory.
- **`_xHHHH_` in source data** comes back changed (see Idioms). A value such as
  `_x202E_` read back becomes the right-to-left override character, so an
  export that cleans control characters before writing can still produce one.
- **A bare carriage return is kept.** Observed in practice: a string cell
  written with a lone CR (U+000D) reads back from `.xlsx` as CR, not as the LF
  that XML end-of-line normalization would give. Upstream documents CR only as
  an example of a character that `_x000D_` escapes. Test this if the export
  normalizes line endings.
- **`poi-ooxml-lite` misses rarely used schema classes.** Using such a part of
  the format fails with `NoClassDefFoundError: org/openxmlformats/schemas/...`.
  Add `poi-ooxml-full`, the full schema jar of about 16 MB against about 6 MB.
- **Mixed POI versions on the classpath** fail unpredictably, for example
  with `NoSuchMethodError` or `NoClassDefFoundError`. A transitive POI from
  another library (a reporting or document-conversion library) is the usual
  source. Check `mvn dependency:tree` for every `org.apache.poi` artifact.
- **Cell text is capped at 32,767 characters.** `setCellValue` throws
  `IllegalArgumentException` beyond that limit, on both formats. Truncate or
  split long values before writing.
- **One document per thread.** Different documents in different threads work.
  Upstream says the same workbook must not be used by several threads at once,
  and it does not test concurrent access to separate sheets of one workbook.
- **ThreadLocal warnings in servlet containers.** POI and XMLBeans cache in
  ThreadLocals, and a pooled-thread server such as Tomcat reports them as
  leaks. From 5.2.4, `org.apache.poi.util.ThreadLocalUtil.clearAllThreadLocals()`
  and `org.apache.xmlbeans.ThreadLocalUtil.clearAllThreadLocals()` clear them.
- Some operations use the JVM's font system, and on a host with no fonts
  installed they raise errors. From 5.2.3 the system property
  `org.apache.poi.ss.ignoreMissingFontSystem` makes POI ignore some of those
  errors; operations that cannot fall back on defaults, such as rendering,
  still fail. Install fonts in the image when the output depends on them.

## Testing
- Round-trip every export: write the workbook to bytes, reopen it with
  `WorkbookFactory.create`, and assert on cell types and values, not only on
  displayed text. A string written where a number was meant (or the reverse)
  shows only on the type.
- Cover in the round trip the values the format changes: a literal `_xHHHH_`,
  control characters, CR and LF, leading zeros, and text at the length cap.
- Assert the document properties when metadata matters: creator, Application
  and the dates sit in `docProps/core.xml` and `docProps/app.xml`.
- To assert that an export writes no temporary file, watch the `poifiles`
  directory under `java.io.tmpdir`, or install a `TempFileCreationStrategy`
  that fails the test.
- Upstream's examples include `SSPerformanceTest`, which times HSSF, XSSF and
  SXSSF writes for a given number of rows and columns. Upstream treats more
  than about 3 seconds for 50,000 by 50 cells in HSSF or SXSSF, or 20 seconds
  in XSSF, as a sign of an environment problem.

## Security defaults
- **Parsing untrusted files is the exposure.** Upstream's guidance: expect any
  exception, `StackOverflowError` included, and catch broadly; expect long
  parse times; expect high memory use from small compressed files; and, in a
  sensitive setting, parse in a separate process with memory and time limits.
  Upstream recommends never parsing files from untrusted or unknown sources,
  and does not treat a crafted file that exhausts memory as a vulnerability.
- The zip-bomb ratio, the entry-size cap, the text cap and the DOCTYPE ban are
  on by default (see Install). Loosening any of them
  (`setMinInflateRatio(0)`, `setDisallowDocTypeDeclaration(false)`, a large
  `setByteArrayMaxOverride`) removes a guard against crafted input.
- **Temporary files hold document content.** Upstream says the temp directory
  must not be readable or writable by untrusted users. The 5.1.0 temp-file
  encryption options are off by default.
- Decrypted and parsed data stays on the heap, and some keys are held in
  ThreadLocals. Upstream advises against running POI where untrusted users can
  read the JVM's memory.
- Writing only, from trusted data, avoids the parsing exposure entirely; the
  `_xHHHH_` round trip (General pitfalls) is the one input-shaped hazard left.

## Operational behaviour
- `XSSFWorkbook` memory grows with the number of cells, and a read from an
  `InputStream` first buffers the whole file. `SXSSFWorkbook` keeps memory
  roughly flat and trades it for temporary disk space. That disk space can
  exceed the final file size many times over unless the temp files are
  compressed.
- `close()` releases the package, and for SXSSF deletes its temporary files.
  Files left in `poifiles` by a crashed JVM stay until something removes them.
- POI does not ask the reading application to recalculate formulas unless told
  to: `XSSFWorkbook.setForceFormulaRecalculation(true)` sets the workbook flag
  that makes the application perform a full recalculation when it opens the
  file.

## Interop
- **Spring Boot:** the Boot BOM manages none of POI, XMLBeans,
  `commons-io`, `commons-compress` or `commons-collections4`, so POI's own
  versions apply unless another BOM or a nearer dependency overrides them.
  Boot does import the Log4j 2 BOM, which sets the `log4j-api` version.
- **Logging:** POI's Log4j 2 API calls reach Logback through the
  `log4j-to-slf4j` bridge, which `spring-boot-starter-logging` includes.
- **Reporting libraries:** [`jasperreports.md`](./jasperreports.md) uses POI
  for its Excel exporter and can bring its own POI version; check that every
  `org.apache.poi` artifact resolves to one version.
- **PDF:** `poi-ooxml`'s optional PDF rendering uses PDFBox
  ([`pdfbox.md`](./pdfbox.md)).

## Major lines
### 4.x
- Semantic versioning starts at 4.0.0. `commons-math3` and `commons-compress`
  became dependencies in 4.0.0, and SparseBitSet in 4.1.2. The schema jars were
  called `ooxml-schemas` (full) and `poi-ooxml-schemas` (lite). Upstream no
  longer supports 4.x and earlier.

### 5.x
- 5.0.0 renamed the schema jars: `ooxml-schemas` became `poi-ooxml-full` and
  `poi-ooxml-schemas` became `poi-ooxml-lite`; the `ooxml-security` jar is gone,
  its classes now in those two. Check every dependency when moving from 4.x.
- 5.1.0 added `commons-io`, disallowed DOCTYPE in embedded XML by default,
  added the temp-file settings for zip entries and package parts, and
  `SXSSFWorkbook.writeAvoidingTempFiles`. 5.2.4 added the ThreadLocal clearing
  utility.
- 5.2.3 was the last release with `poi-bin` archives; later releases are
  published only to Maven Central.

### 6.x
- Upstream's versioning page states that work on 6.0.0 has started, that it
  removes Java 8 support and some deprecated APIs, and that its exact scope is
  still open; the 5.5.x releases continue for critical fixes, and for a
  limited time after 6.0.0 ships. Migrate one major line at a time, after
  clearing deprecation warnings.

## Upstream docs
- Home and component map: https://poi.apache.org/components/index.html
- Spreadsheet how-to (SXSSF): https://poi.apache.org/components/spreadsheet/how-to.html
- Spreadsheet quick guide: https://poi.apache.org/components/spreadsheet/quick-guide.html
- FAQ: https://poi.apache.org/help/faq.html
- Configuration (limits, temp files): https://poi.apache.org/components/configuration.html
- Security guidance: https://poi.apache.org/security.html
- Versioning and migration: https://poi.apache.org/versioning.html
- Change log: https://poi.apache.org/changes.html
- Source: https://github.com/apache/poi
