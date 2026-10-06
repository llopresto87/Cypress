# scipy — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
SciPy is the scientific-computing library layered on top of NumPy (see the
`numpy` page). It groups algorithms into submodules (optimization,
integration, interpolation, signal processing, linear algebra, statistics,
spatial data structures and transforms, and more), all operating on NumPy
arrays. PyPI package name `scipy`.

## Install, setup and configuration
- `pip install scipy`. Its main runtime dependency is NumPy. SciPy releases are
  not tied to NumPy releases; the toolchain roadmap says each release aims to
  stay compatible with at least the four previous NumPy releases.
- Observed in practice: each SciPy release also declares an upper bound on
  NumPy in its metadata, so an old exact SciPy pin caps NumPy. Upgrade the two
  together.
- There is no global configuration; behaviour is set per call.

## Core API / usage shape
- `scipy.signal`: digital signal processing (filtering, convolution, spectral
  analysis, peak finding, smoothing). For example, `savgol_filter` applies a
  Savitzky-Golay filter that smooths a series by fitting successive low-order
  polynomials over a sliding window, preserving peak shape better than a moving
  average. Its signature is `savgol_filter(x, window_length, polyorder,
  deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0)`; input that is not
  single or double precision float is converted to float64.
- `scipy.spatial.transform.Rotation`: represents 3D rotations and converts
  between representations (quaternions, rotation matrices, Euler angles, and
  rotation vectors) through `from_quat`, `as_quat`, `from_euler`, `as_euler`,
  and their kin.
- Other submodules: `scipy.optimize`, `scipy.integrate`,
  `scipy.interpolate`, `scipy.linalg`, `scipy.stats`, `scipy.sparse` cover the
  rest of the numerical toolkit.
- Explicit submodule imports (`from scipy import signal`) are the portable,
  idiomatic form. Recent lines load submodules lazily on first attribute access,
  so `import scipy; scipy.signal...` also works there; older lines may raise
  `AttributeError`.

## Idioms & best practices
- Import the specific submodule you need rather than relying on attribute access
  off bare `scipy`, which depends on the line's lazy loading.
- Keep data in NumPy arrays and feed them directly to SciPy routines; avoid
  Python-level loops around per-element SciPy calls.
- For smoothing a noisy series where peak height/position matters, prefer
  `savgol_filter` over a plain moving average.
- Where your line has it, pass `scalar_first=True` to `from_quat` / `as_quat`
  instead of reordering quaternion components by hand.

## General pitfalls
- **Quaternion ordering is a load-bearing cross-library convention.**
  `scipy.spatial.transform.Rotation` uses **scalar-LAST** quaternion order:
  `(x, y, z, w)`, unless `scalar_first=True` is passed. Many other rotation
  libraries, engines, and file formats use **scalar-FIRST** order:
  `(w, x, y, z)`. Before piping a quaternion from one library into another,
  check the convention and reorder if needed; a silent scalar-first/last
  mismatch produces a plausible-looking but wrong rotation rather than an error.
- Euler-angle conversions depend on the axis sequence and on intrinsic versus
  extrinsic rotation. In the `seq` string of `from_euler` / `as_euler`,
  uppercase letters (`"XYZ"`) mean intrinsic and lowercase (`"xyz"`) mean
  extrinsic, and the two cannot be mixed in one call. Normalising the case of
  a sequence string silently changes the angles.
- `savgol_filter` requires `polyorder < window_length`, and under the default
  `mode='interp'` also `window_length <= len(x)`, so a short segment raises;
  the other modes pad instead.
- Observed in practice: code that shrinks `window_length` for short inputs must
  keep it valid (above `polyorder`, and odd where the caller requires it), or
  the call raises or the code silently falls back to a hard-coded default.
  Make any fallback window explicit and tested.
- SciPy inherits NumPy's float-comparison and view/copy subtleties; results are
  numerical approximations, so compare with tolerances.

## Testing
- Compare results with `numpy.testing.assert_allclose` and explicit
  tolerances; SciPy outputs are approximations and can shift between releases.
- Observed in practice: an unexplained exact pin on a numeric library is a
  finding, not a style fix. Write a characterization (golden output) test
  before bumping it, and diff the outputs.

## Security defaults
- The numerical routines take arrays and do no network or code-loading work.
  File readers (`scipy.io`) are not covered by this page.

## Operational behaviour
- Everything runs in process on in-memory arrays. This page has no confirmed
  source on SciPy's threading or memory behaviour beyond what NumPy documents.

## Interop
- Built on NumPy (`library-corpus/pypi/numpy.md`): arrays in, arrays out, and
  the NumPy version window above.
- Quaternions from libraries that use scalar-first order (for example
  `library-corpus/pypi/ahrs.md`) need reordering, or `scalar_first=True`,
  before `Rotation.from_quat`.

## Major lines

### 1.x line
- Every release this page covers is on the 1.x line, and features arrive
  within it: lazy submodule loading and the
  `scalar_first` argument on `Rotation` exist only on recent 1.x releases, so
  check your pin before relying on either.
- The supported Python and NumPy windows move forward over the line (the
  toolchain roadmap lists them).

## Upstream docs
- Docs: https://docs.scipy.org/doc/scipy/
- Repo: https://github.com/scipy/scipy
