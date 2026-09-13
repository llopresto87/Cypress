# pypdfium2 — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`pypdfium2` is a Python binding to **PDFium**, the C++ PDF engine that renders
PDFs in Chromium. It provides fast, dependency-light access to a PDF's
structure — page count, page dimensions, metadata, outline — plus page
rasterization to a bitmap and page text extraction, all without shelling out to
an external binary.

Its distinguishing property on an ingestion or document-processing path is
**cheapness**: reading a document's page count or page sizes does not require
parsing, layout analysis, or a model pass, so it can be used to *plan* expensive
work before committing to it.

- **PyPI package:** `pypdfium2`; imported as `pypdfium2` (commonly aliased
  `pdfium`).
- Ships as **prebuilt native wheels** per platform — there is no pure-Python
  fallback.

## Core API / usage shape
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(path_or_bytes_or_filelike)   # optional password=...
n_pages = len(pdf)                                    # the cheap fact
page = pdf[0]
width, height = page.get_size()                       # points

bitmap = page.render(scale=2)                         # raster at 2x 72dpi
image = bitmap.to_pil()                               # or .to_numpy()

textpage = page.get_textpage()
text = textpage.get_text_range()                      # or get_text_bounded(...)

pdf.close()
```
- A document is a container of pages; indexing and iteration yield page objects.
- `render(scale=...)` is expressed as a multiple of 72 dpi, so a target DPI is
  `dpi / 72`.
- Text extraction goes through a separate *text page* object obtained from a
  page.
- Outline/table-of-contents, page labels, form handling, and document saving are
  exposed on the document object.
- The full PDFium C API is reachable under the raw namespace for anything the
  ergonomic layer does not wrap.

## Idioms & best practices
- **Read the page count before dispatching an expensive parse.** A heavyweight
  document parser (a layout/OCR service, a model-backed extractor) can only
  report a page count *after* doing the work; this library reports it beforehand
  for almost nothing, which is the whole reason to carry it alongside one.
- **Tile a large document into page windows** — `[1, n]` split into 1-based
  inclusive ranges — parse each window separately, and feed every window's output
  through the same downstream loop under a single document identity. Memory and
  latency then scale with the window, not with the document.
- **Keep a fast path for documents that fit one window**: they take the historical
  unranged parse unchanged, so windowing adds no cost to the common small case.
- **Close what you open, innermost first.** Pages and text pages hold native
  handles into their parent document; free them before the document, or use them
  as context managers. Letting a page outlive its document is a use-after-free at
  the C level, not a Python exception.
- **Render at the scale you actually need.** Rasterization cost grows with the
  square of the scale factor, and an oversized bitmap is the usual cause of a
  page-processing job that looks CPU-bound for no reason.
- **Serialize access.** Treat a document object as owned by one thread or one
  task; drive parallelism by processing separate documents (or separate document
  handles) concurrently, not by sharing one handle.

## General pitfalls
- **A failed page count is easy to make invisible.** The natural implementation
  falls back to a whole-document parse when the count cannot be read — which
  means a failure of this library degrades throughput and memory behavior
  *silently* instead of failing loudly. Log and count that fallback, or a
  regression here is undetectable.
- **It is a native-binary dependency.** Wheels are platform-specific; an
  unusual architecture, a musl-based image, or a locked-down build environment
  can leave no installable wheel and no source fallback. Check the target
  platform before adopting it.
- **A page count is not a parse result.** It is not interchangeable with the page
  count a document parser reports after parsing — which is precisely the point,
  but it also means the two can disagree on malformed or unusual files.
- **Encrypted documents need the password at open time**, and some PDFs are
  readable but permission-restricted; the failure arrives when the document is
  opened, not when a page is touched.
- **Page indices are zero-based in the API while document-facing page ranges are
  conventionally one-based.** Off-by-one at that boundary is the recurring bug in
  any windowing scheme.
- **Text extraction returns the text objects in the file, in file order** — not a
  reading-order reconstruction. For columns, tables, or scanned pages it is a raw
  input to layout analysis, not a substitute for it, and a scanned page yields
  nothing at all.
- **The ergonomic API has been reshaped across major lines** (naming, object
  lifecycle, rendering entry points). Examples found in the wild are often written
  against a different line than the one installed — confirm against the pin in
  use rather than trusting a snippet.

## Upstream docs
- Docs: https://pypdfium2.readthedocs.io/
- Repo: https://github.com/pypdfium2-team/pypdfium2
- PDFium (the underlying engine): https://pdfium.googlesource.com/pdfium/
