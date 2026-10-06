# docling — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`docling` is a document parsing/conversion library that turns PDFs, HTML, and
other formats into a structured `DoclingDocument`, with per-format processing
pipelines (OCR, layout, etc.). Companion packages in the same line include
`docling-core`, `docling-ibm-models`, `docling-parse`, and integrations such as
`llama-index-readers-docling`.

## Install, setup and configuration
- `pip install docling` (MIT licence); recent lines need Python 3.10 or newer.
  It runs on macOS, Linux and Windows. A `docling` CLI ships with it
  (`docling myfile.pdf --to json --to md --no-ocr`).
- Models (layout, table structure, OCR and others) download automatically on
  first use into the user cache. `docling-tools models download` prefetches
  them; `artifacts_path` / `DOCLING_ARTIFACTS_PATH` loads them from a local
  directory instead.
- OCR engines are pluggable (EasyOCR, Tesseract, RapidOCR and others); each
  has its own options object passed through the pipeline options.
- CPU threads default to 4; `OMP_NUM_THREADS` changes it, and
  `accelerator_options.num_threads` sets model inference threads.

## Core API / usage shape
- `DocumentConverter.convert(source=...)` returns a `ConversionResult` whose
  `.document` is a full `DoclingDocument` with structure preserved.
- `DoclingDocument.export_to_markdown()` exports the parsed document to Markdown;
  structure metadata such as `DocItemLabel.TITLE` / `DocItemLabel.SECTION_HEADER`
  is available on the document.
- Per-format pipeline configuration is the documented pattern: route a format
  through `DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(
  pipeline_options=PdfPipelineOptions(...))})` rather than relying on defaults.
  This is how you toggle `do_ocr` and other options per format.

## Idioms & best practices
- Use `DocumentConverter` directly (not thin wrappers) when you need document-
  structure metadata in addition to exported text; wrappers can drop rich
  structure and may double-parse.
- OCR language configuration must be passed via the pipeline's `ocr_options.lang`;
  passing only `do_ocr=True` does not apply any configured language list.
- Moving from the in-process `DocumentConverter` to docling-serve changes the
  return shape; the pitfall is on `library-corpus/pypi/docling-serve.md`.
- Prefetch models for offline or air-gapped hosts with
  `docling-tools models download`, then point the pipeline at them with
  `PdfPipelineOptions(artifacts_path=...)`, `--artifacts-path`, or
  `DOCLING_ARTIFACTS_PATH`.
- Bound the work per document with `converter.convert(source,
  max_num_pages=..., max_file_size=...)`.

## General pitfalls
- Document parsers (PDF/HTML/LaTeX/archive backends) carry an untrusted-input
  attack surface: enabling OCR triggers model downloads (archive extraction),
  HTML/LaTeX inputs can reference external/local files, and archive/XML backends
  can be abused (XXE, zip bombs, path traversal). Treat untrusted documents as
  hostile, sandbox conversion, and keep optional network/rendering features
  (e.g. browser-based HTML rendering, local file fetch) disabled unless needed.
- Sending document content to a remote model service needs an explicit
  `enable_remote_services=True` in the pipeline options; without it the call
  raises `OperationNotAllowed`. That switch covers user data only: model weight
  downloads follow the prefetch settings above.

## Testing
- Upstream documents no testing guide for callers. A test environment needs the
  models prefetched (or network access on first run), because conversion loads
  them before the first document.

## Security defaults
- Remote model services are off by default (`OperationNotAllowed` unless
  enabled), so document content stays in process.
- The untrusted-input surface is in the pitfalls above: sandbox conversion of
  documents you did not produce, and keep network-reaching features off.

## Operational behaviour
- The first conversion downloads models unless they were prefetched, so cold
  start is slow and needs network access.
- Conversion uses 4 CPU threads by default; `max_num_pages` and
  `max_file_size` bound the work spent on one document.

## Interop
- `docling-serve` runs the same conversion as an HTTP service
  (`library-corpus/pypi/docling-serve.md`).
- `llama-index-readers-docling` feeds converted documents into LlamaIndex
  (`library-corpus/pypi/llama-index-core.md`).
- `pypdfium2` is the cheap way to read page counts and sizes before deciding to
  run a full conversion (`library-corpus/pypi/pypdfium2.md`).

## Major lines

### 1.x line
- `DocumentConverter.convert` takes a batch, and
  `convert_single` converts one file.

### 2.x line
- Converts PDF, Word, PowerPoint, HTML and images into a new universal
  `DoclingDocument` that keeps the document hierarchy, with a new API and CLI.
  `convert` now takes a single input (it was `convert_single`) and
  `convert_all` takes many (it was `convert`).

## Upstream docs
- Docs: https://docling-project.github.io/docling/
- Repo: https://github.com/docling-project/docling
