# pypdfium2 — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`pypdfium2` is a Python binding to **PDFium**, the C++ PDF engine that renders
PDFs in Chromium. It provides fast, dependency-light access to a PDF's
structure (page count, page dimensions, metadata, outline), plus page
rasterization to a bitmap and page text extraction, all without shelling out to
an external binary.

Its distinguishing property on an ingestion or document-processing path is
**cheapness**: reading a document's page count or page sizes does not require
parsing, layout analysis, or a model pass, so it can be used to *plan* expensive
work before committing to it.

- **PyPI package:** `pypdfium2`; imported as `pypdfium2` (commonly aliased
  `pdfium`).
- Ships as **prebuilt native wheels** per platform; there is no pure-Python
  fallback.

## Install, setup and configuration
- `python -m pip install -U pypdfium2` installs a prebuilt wheel that bundles a
  PDFium binary where one exists for the platform (the binaries come from the
  pdfium-binaries project). Licence: Apache-2.0 or BSD-3-Clause; PDFium itself
  is liberally licensed.
- JavaScript/XFA-enabled PDFium needs a setup run that bypasses wheels:
  `PDFIUM_PLATFORM=auto-v8 pip install -v pypdfium2 --no-binary pypdfium2`.
- Optional runtime dependencies (Pillow for `to_pil()`, NumPy for
  `to_numpy()`) load only when used.
- Upstream's API-stability promises cover the helpers, not the setup code,
  which may change at any time.

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
- **Tile a large document into page windows**: `[1, n]` split into 1-based
  inclusive ranges; parse each window separately, and feed every window's output
  through the same downstream loop under a single document identity. Memory and
  latency then scale with the window, not with the document.
- **Keep a fast path for documents that fit one window**: they take the historical
  unranged parse unchanged, so windowing adds no cost to the common small case.
- **Close what you open.** Pages and text pages hold native handles into their
  parent document, and an unclosed handle is freed only when its finalizer runs.
  Close explicitly, or open the document in a `with` block. The helper classes
  track parents and kids: closing a document first closes its open pages and
  text pages, and the source says callers need not mind the order. With the raw
  `pdfium_c` API you close in hierarchical order yourself, child before parent.
- **Render at the scale you actually need.** `scale` multiplies the pixels per
  PDF canvas unit along each axis (the `render` docstring), so the bitmap's
  pixel count and memory grow with the square of the scale factor.
- **Serialize access.** PDFium is not thread-safe: no two PDFium calls may run
  at the same time across threads, not even on different documents, and doing so
  can crash or corrupt the process. The same holds for the library's own
  helpers. Threads are fine only if a single PDFium call runs at a time (for
  example behind a mutex). To parallelize expensive work such as rendering, use
  separate processes, not threads.

## General pitfalls
- **A failed page count is easy to make invisible.** The natural implementation
  falls back to a whole-document parse when the count cannot be read, which
  means a failure of this library degrades throughput and memory behavior
  *silently* instead of failing loudly. Log and count that fallback, or a
  regression here is undetectable.
- **It is a native-binary dependency.** Wheels are platform-specific. Without a
  wheel for the platform, upstream's setup looks for a system pdfium or tries to
  build pdfium from source; an unusual architecture, a musl-based image, or a
  locked-down build environment can make both fail. Check the target platform
  against upstream's platform support page before adopting it.
- **A page count is not a parse result.** It is not interchangeable with the page
  count a document parser reports after parsing. That is precisely the point,
  but it also means the two can disagree on malformed or unusual files.
- **Encrypted documents need the password at open time**, and some PDFs are
  readable but permission-restricted; the failure arrives when the document is
  opened, not when a page is touched.
- **Page indices are zero-based in the API while document-facing page ranges are
  conventionally one-based.** Off-by-one at that boundary is the recurring bug in
  any windowing scheme.
- **Text extraction returns the text objects in the file, in file order**, not a
  reading-order reconstruction. For columns, tables, or scanned pages it is a raw
  input to layout analysis, not a substitute for it, and a scanned page yields
  nothing at all.
- **The ergonomic API has been reshaped across major lines** (naming, object
  lifecycle, rendering entry points). Examples found in the wild are often written
  against a different line than the one installed. Confirm against the pin in
  use rather than trusting a snippet.

## Testing
- Upstream documents no testing guide for callers. Keep a small set of fixture
  PDFs that covers the cases the pitfalls name (encrypted, permission-restricted,
  scanned, malformed) and assert page counts and sizes on them; a page count is
  cheap enough to check on every fixture.
- Exercise the fallback path deliberately (a file whose count cannot be read)
  and assert that the fallback is logged and counted.

## Security defaults
- PDFium parses untrusted binary input in native code inside your process, so
  a fault in it is a fault in your process. Separate worker processes (the same
  ones parallelism needs) keep such a fault away from the caller.
- JavaScript/XFA support is absent from the default wheels and must be asked
  for explicitly (install above).

## Operational behaviour
- Thread safety: one PDFium call at a time per process (idioms above).
  Parallelism comes from processes.
- Memory is held by native handles until pages, text pages and documents are
  closed; close them innermost first.
- Rendering cost grows with the square of the scale factor.

## Interop
- Commonly carried beside a heavyweight parser such as Docling, to read page
  counts before dispatching work (`library-corpus/pypi/docling.md`).
- Bitmaps convert to Pillow images or NumPy arrays (`library-corpus/pypi/numpy.md`).

## Major lines
- The ergonomic API was reshaped across major lines (pitfalls above). This
  page does not record the per-line differences; read the changelog for the
  line you pin, and treat examples from another line as suspect.

## Upstream docs
- Docs: https://pypdfium2.readthedocs.io/
- Repo: https://github.com/pypdfium2-team/pypdfium2
- PDFium (the underlying engine): https://pdfium.googlesource.com/pdfium/
