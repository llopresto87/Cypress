# jasperreports — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
JasperReports Library is an open-source Java reporting engine: it reads data
from any source and produces page-oriented documents exported to PDF, HTML,
Excel, OpenOffice, Word and other formats. Report templates are XML
(`.jrxml`), usually edited with Jaspersoft Studio. Coordinates: the core
`net.sf.jasperreports:jasperreports` and the expression functions
`net.sf.jasperreports:jasperreports-functions`; on the 7 line optional features
are separate jars, among them:

- `net.sf.jasperreports:jasperreports-pdf`
- `net.sf.jasperreports:jasperreports-jdt`
- `net.sf.jasperreports:jasperreports-fonts`
- `net.sf.jasperreports:jasperreports-charts`
- `net.sf.jasperreports:jasperreports-excel-poi`
- `net.sf.jasperreports:jasperreports-groovy`
- `net.sf.jasperreports:jasperreports-javascript`
- `net.sf.jasperreports:jasperreports-json`
- `net.sf.jasperreports:jasperreports-servlets`
- `net.sf.jasperreports:jasperreports-spring`
- `net.sf.jasperreports:jasperreports-maven-plugin`

No Spring Boot BOM manages any `net.sf.jasperreports` artifact, so the project
pins the version. Licence LGPL-3.0. Upstream home: source on GitHub `Jaspersoft/jasperreports`;
documentation (samples, configuration and functions references, Javadoc) at
https://jasperreports.sourceforge.net.

## Install, setup and configuration
- **6 line:** the core jar has the PDF writer (`com.github.librepdf:openpdf`)
  and the Eclipse JDT compiler (`org.eclipse.jdt:ecj`) as normal dependencies;
  batik (SVG), POI, Groovy, Rhino, Spring, servlet and persistence APIs,
  barcode libraries and others are declared `optional`, so they are not
  transitive and the consumer declares what it uses.
- **7 line:** the core no longer carries `openpdf` or `ecj`; they moved to
  `jasperreports-pdf` and `jasperreports-jdt`. A consumer that exports PDF or
  compiles Java-expression templates at run time must add those jars. Batik is
  a normal dependency of the 7 core.
- **Jackson:** both lines bring Jackson 2 (`jackson-core`, `-databind`,
  `-annotations`, `jackson-dataformat-xml`) as transitives; in a Boot build the
  Boot BOM's Jackson management overrides those versions (observed in practice
  as the only thing keeping old Jackson versions out).
- **Properties:** `net.sf.jasperreports.*` properties live in a global
  `jasperreports.properties`, in a context, or on a report. Selected defaults:
  - `net.sf.jasperreports.when.no.data.type` = `NoPages`;
  - `net.sf.jasperreports.awt.ignore.missing.font` = false (a font missing from
    font extensions and the JVM raises `JRFontNotFoundException`);
  - `net.sf.jasperreports.default.font.name` = SansSerif;
  - `net.sf.jasperreports.default.pdf.embedded` = false;
  - the governors `net.sf.jasperreports.governor.max.pages.enabled` and
    `...timeout.enabled` = false;
  - `net.sf.jasperreports.compiler.keep.java.file` = false.
- **Expression compiler:** `net.sf.jasperreports.compiler.<language>` per
  expression language; for Java, `net.sf.jasperreports.compiler.class`
  overrides detection, otherwise JDT is used when present and then the JDK
  compiler. `net.sf.jasperreports.compiler.classpath` defaults to
  `java.class.path`.

## Core API / usage shape
- **Three stages, three facades:** compile with `JasperCompileManager`
  (`.jrxml` to `JasperReport`), fill with `JasperFillManager` (report,
  parameter `Map` and a `JRDataSource` or JDBC `Connection` to `JasperPrint`),
  export with `JasperExportManager` or an exporter class (`JasperPrint` to PDF
  and other formats):
  `JasperFillManager.fillReport(JasperCompileManager.compileReport(in), params, dataSource)`,
  then `JasperExportManager.exportReportToPdfStream(print, out)`.
- Templates read parameters as `$P{NAME}`, fields as `$F{...}` and variables
  as `$V{...}`.
- Compiling generates a class (or a script for Groovy and JavaScript) holding
  every report expression, used while filling; a compiled `JasperReport` is
  validated and mostly read-only.
- **Data sources:** `JRBeanCollectionDataSource(Collection)` wraps JavaBeans
  already in memory; `JREmptyDataSource(n)` simulates n records with all fields
  null, for pages driven only by parameters.
- `JasperPrint.addPage(...)` and `copyFrom(JasperPrint)` merge several filled
  prints into one document (a cover page in front of a body, say).
- **Large reports:** pass a virtualizer (`JRFileVirtualizer`,
  `JRSwapFileVirtualizer`, `JRGzipVirtualizer`) as the
  `JRParameter.REPORT_VIRTUALIZER` fill parameter; pages beyond `maxSize` go to
  disk. Virtualization is not set in the JRXML.

## Idioms & best practices
- Compile once and cache the `JasperReport`, or precompile `.jrxml` to
  `.jasper` at build time (`jasperreports-maven-plugin`). Run-time compilation
  generates and compiles Java source through JDT, so compiling per request
  repeats that cost (observed in practice as a real cost).
- Ship fonts as a font extension jar (`jasperreports_extension.properties`,
  `fonts.xml` and the TTF files) instead of relying on host fonts; otherwise
  the JVM substitutes fonts and text can shift or be cut. The 7 line publishes
  `jasperreports-fonts` (DejaVu).
- Observed in practice: wrap one aggregate DTO as a singleton list for
  `JRBeanCollectionDataSource`, with nested collections feeding sub-datasets.
- Observed in practice: compute instants and other time logic in Java and pass
  them as parameters; template-side date arithmetic got daylight-saving changes
  wrong. Upstream says nothing on this.

## General pitfalls
- **No data, no pages.** With the default `whenNoDataType` (`NoPages`) an empty
  data source produces a document with no pages. Set `whenNoDataType`
  (`AllSectionsNoDetail`, `NoDataSection`) or use `JREmptyDataSource` for
  parameter-only pages.
- **Missing fonts throw** `JRFontNotFoundException` by default, and test and
  production hosts often have different fonts installed.
- **6 line optionals.** Optional dependencies (batik, POI, ...) must be
  declared by the consumer. Observed in practice: pinning one below the version
  Jasper declares brings back defects fixed in between, and nothing else in the
  build lifts it.
- **The 7 upgrade breaks templates.** `.jasper` files compiled by 6 cannot be
  loaded, and `.jrxml`/`.jrtx` files from 6 or older no longer load in 7 alone
  (the parser moved from Commons Digester to Jackson XML); Jaspersoft Studio 7
  converts them. Some Java package names changed with the jar split. Re-render
  every template; a coordinate bump is not enough.
- **3D charts:** the 7 line uses JFreeChart without 3D support, so Pie 3D,
  Bar 3D and Stacked Bar 3D charts render flat.
- **Virtualizer temp files** from `JRFileVirtualizer` remain until garbage
  collection unless `cleanup()` is called.

## Testing
- Observed in practice: one rendering test per template that compiles, fills
  with a representative model and exports, run with no network so a template
  cannot fetch images or fonts at render time;
  `net.sf.jasperreports.default.file.repository.enabled=false` and, on later 7
  releases, repository URL filtering help enforce that.
- Put the font extension on the test class path too, so the font check behaves
  the same in tests and production.
- Upstream runs its samples as Maven projects (`mvn clean compile exec:java`);
  they serve as reference fixtures.

## Security defaults
- **A template is code.** Report expressions are Java (or Groovy, JavaScript)
  compiled and run at fill time. Expression class filtering exists but is off
  by default (`net.sf.jasperreports.report.class.filter.enabled` false, allowed
  classes under `net.sf.jasperreports.report.class.whitelist.*`). Treat a
  template from an untrusted source as untrusted code.
- XML parsing rejects DOCTYPE declarations by default
  (`net.sf.jasperreports.xml.allow.doctype` false), which blocks XXE; enable it
  only for trusted input.
- Open unless set: the default repository resolves files from the local file
  system (`net.sf.jasperreports.default.file.repository.enabled` true);
  repository URL filtering is off (`...repository.url.filter.enabled` false);
  `$P!{}` query clause substitution is on (`...query.parameter.clause.enabled`
  true). Both switches exist only from later 7 releases; on the 6 line `$P!{}`
  is always on and there is no URL filter. Later 7 releases also add deserialization class filtering; CSV formula
  escaping (`...export.csv.escape.formula`) exists from late 6 releases.
- `$P!{}` pastes parameter text into the query; bind values with `$P{}`.

## Operational behaviour
- Fill memory grows with page count; virtualizers move pages to disk, and the
  page and time governors (off by default) stop runaway reports.
- Run-time compilation writes a temporary Java source (deleted unless
  `compiler.keep.java.file` is true) and compiles against `java.class.path`;
  in fat-jar or custom class-loader deployments the compile class path may need
  setting (an inference from the defaults).
- PDF fonts are not embedded by default (`default.pdf.embedded` false).

## Interop
- OpenPDF (PDF export, in `jasperreports-pdf` on 7), Eclipse JDT `ecj`
  (expression compiler, in `jasperreports-jdt` on 7), Jackson 2 (JRXML parsing
  on 7; transitive on both lines), Apache Batik (SVG), Apache POI (Excel),
  JFreeChart (charts), and the Spring Boot BOM, which overrides Jackson but
  does not manage Jasper.
- The 6 line targets `javax.*` APIs (servlet and persistence as optional
  dependencies); the 7 line is the Jakarta-migration line.

## Major lines
### 6
- Single core jar with the PDF writer and the JDT compiler; Commons Digester
  JRXML parser; `javax.*` optional coordinates (servlet API provided and
  optional); batik optional. New work is on 7; the fetched sources give no
  end-of-life statement for the 6 line.

### 7
- Ant build replaced by Maven; deprecated code removed; `.jasper`
  compatibility broken; `.jrxml`/`.jrtx` format changed (Digester to Jackson
  XML; old files need conversion); optional features split into separate jars
  (PDF, JDT, charts, fonts, Excel, servlets, Spring and others) for the Jakarta
  migration; no `javax.*` in the core; batik non-optional; some package names
  changed; JFreeChart without 3D.

The Java baseline of each line was not confirmed for this page.

## Upstream docs
- https://github.com/Jaspersoft/jasperreports
- https://jasperreports.sourceforge.net/config.reference.html
- https://jasperreports.sourceforge.net/sample.reference.html
- https://jasperreports.sourceforge.net/api/index.html
