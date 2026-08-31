# scipy — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
SciPy is the scientific-computing library layered on top of NumPy (see the
`numpy` page). It groups algorithms into submodules — optimization,
integration, interpolation, signal processing, linear algebra, statistics,
spatial data structures and transforms, and more — all operating on NumPy
arrays. PyPI package name `scipy`.

## Core API / usage shape
- **`scipy.signal`**: digital signal processing — filtering, convolution,
  spectral analysis, peak finding, and smoothing. For example, `savgol_filter`
  applies a Savitzky-Golay filter that smooths a series by fitting successive
  low-order polynomials over a sliding window, preserving peak shape better than
  a moving average.
- **`scipy.spatial.transform.Rotation`**: represents 3D rotations and converts
  between representations — quaternions, rotation matrices, Euler angles, and
  rotation vectors (`from_quat`, `as_quat`, `from_euler`, `as_euler`, etc.).
- **Other submodules**: `scipy.optimize`, `scipy.integrate`,
  `scipy.interpolate`, `scipy.linalg`, `scipy.stats`, `scipy.sparse` cover the
  rest of the numerical toolkit.
- Submodules are imported explicitly (`from scipy import signal`); the top-level
  `scipy` namespace does not eagerly expose them.

## Idioms & best practices
- Import the specific submodule you need rather than expecting attributes off
  bare `scipy`.
- Keep data in NumPy arrays and feed them directly to SciPy routines; avoid
  Python-level loops around per-element SciPy calls.
- For smoothing a noisy series where peak height/position matters, prefer
  `savgol_filter` over a plain moving average.

## General pitfalls
- **Quaternion ordering is a load-bearing cross-library convention.**
  `scipy.spatial.transform.Rotation` uses **scalar-LAST** quaternion order —
  `(x, y, z, w)`. Many other rotation libraries, engines, and file formats use
  **scalar-FIRST** order — `(w, x, y, z)`. Before piping a quaternion from one
  library into another, check the convention and reorder if needed; a silent
  scalar-first/last mismatch produces a plausible-looking but wrong rotation
  rather than an error.
- Euler-angle conversions depend on the axis sequence and intrinsic-vs-extrinsic
  convention (the string passed to `from_euler`/`as_euler`); mismatched
  conventions between producer and consumer give wrong angles silently.
- SciPy inherits NumPy's float-comparison and view/copy subtleties; results are
  numerical approximations, so compare with tolerances.

## Upstream docs
- Docs: https://docs.scipy.org/doc/scipy/
- Repo: https://github.com/scipy/scipy
