# docling — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`docling` is a document parsing/conversion library that turns PDFs, HTML, and
other formats into a structured `DoclingDocument`, with per-format processing
pipelines (OCR, layout, etc.). Companion packages in the same line include
`docling-core`, `docling-ibm-models`, `docling-parse`, and integrations such as
`llama-index-readers-docling`.

## Core API / usage shape
- `DocumentConverter.convert(source=...)` returns a `ConversionResult` whose
  `.document` is a full `DoclingDocument` with structure preserved.
- `DoclingDocument.export_to_markdown()` exports the parsed document to Markdown;
  structure metadata such as `DocItemLabel.TITLE` / `DocItemLabel.SECTION_HEADER`
  is available on the document.
- Per-format pipeline configuration is the documented pattern: route a format
  through `DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(
  pipeline_options=PdfPipelineOptions(...))})` rather than relying on defaults —
  this is how you toggle `do_ocr` and other options per format.

## Idioms & best practices
- Use `DocumentConverter` directly (not thin wrappers) when you need document-
  structure metadata in addition to exported text; wrappers can drop rich
  structure and may double-parse.
- OCR language configuration must be passed via the pipeline's `ocr_options.lang`;
  passing only `do_ocr=True` does not apply any configured language list.

## General pitfalls
- Document parsers (PDF/HTML/LaTeX/archive backends) carry an untrusted-input
  attack surface: enabling OCR triggers model downloads (archive extraction),
  HTML/LaTeX inputs can reference external/local files, and archive/XML backends
  can be abused (XXE, zip bombs, path traversal). Treat untrusted documents as
  hostile, sandbox conversion, and keep optional network/rendering features
  (e.g. browser-based HTML rendering, local file fetch) disabled unless needed.

## Upstream docs
- Docs: https://docling-project.github.io/docling/
- Repo: https://github.com/docling-project/docling
