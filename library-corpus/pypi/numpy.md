# numpy — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
NumPy is the foundational numerical-computing package for Python: a
homogeneous, N-dimensional array (`ndarray`) backed by contiguous C memory,
with vectorized element-wise operations, linear algebra, FFTs, and random
number generation. It is the numeric substrate most of the scientific Python
ecosystem (SciPy, pandas, scikit-learn, image and ML libraries) builds on and
interoperates through. PyPI package name `numpy`.

## Install, setup and configuration
- `pip install numpy`. This page has no confirmed source for the source-build
  toolchain or for the choice of BLAS library.
- Behaviour is set per call (`dtype=`, `casting=`, `out=`).
- NEP 29 and SPEC 0 recommend which NumPy (and Python) versions downstream
  projects should support. They are guidance for dependents, not a statement of
  when NumPy stops patching a line.

## Core API / usage shape
- **`ndarray`**: the core type — a fixed-size, typed, multi-dimensional array.
  Created via `np.array`, `np.zeros`/`np.ones`/`np.arange`/`np.linspace`, etc.
- **`dtype`**: every array has one element type (e.g. `float64`, `int32`,
  `bool`); operations may up-cast per type-promotion rules.
- **Broadcasting**: operations between arrays of different but compatible shapes
  virtually stretch the smaller across the larger without copying, following a
  defined shape-alignment rule (trailing dimensions must match or be 1).
- **Vectorization**: express computation as whole-array operations and ufuncs
  rather than Python loops; the work runs in compiled code.
- **Indexing / slicing**: basic slices return **views** (shared memory); fancy
  indexing (integer/boolean arrays) returns **copies**.

## Idioms & best practices
- Vectorize: replace explicit Python loops with array operations and ufuncs for
  large speedups and clarity.
- Be intentional about dtype (memory and precision) and choose it explicitly for
  large arrays rather than relying on default promotion.
- Use broadcasting to avoid materializing large intermediate arrays.
- Prefer the modern `np.random.default_rng()` generator API over the legacy
  global random functions for new code.
- Observed in practice: carry the indices that `argmax`, `find_peaks` and their
  kin return, instead of finding a value again by matching
  (`np.isclose(a, v)`, `a == v`). On quantized or integer data such as sensor
  counts, value matching collides, pairs the wrong events and inflates counts
  with no error.
- Observed in practice: when one element of several aligned arrays has to be
  discarded, drop it from every array together, or carry a boolean mask.
  Writing `np.nan` into one array and aggregating with `nanmean` hides the
  discard, and the survivors shift if a later step re-aligns the arrays.

## General pitfalls
- **Views vs copies**: a slice is a view — mutating it mutates the original;
  fancy indexing copies. Confusing the two causes silent aliasing bugs or
  unexpected non-mutation. Use `.copy()` when independence is required.
- **Floating-point comparison**: never compare floats with `==`; use
  `np.isclose` / `np.allclose` with tolerances.
- Broadcasting can silently succeed on unintended shapes and produce a wrong-shape
  result rather than an error; assert shapes when it matters.
- Writing a float into an int array by assignment (`a[i] = 1.5`) or converting
  with `astype(int)` drops the fraction without warning (`astype` defaults to
  `casting="unsafe"`). In-place ufuncs do not: `a *= 1.5` or
  `np.multiply(a, 1.5, out=a)` on an int array raises `UFuncTypeError`, because
  ufuncs default to `casting="same_kind"`.
- `np.asarray(x, dtype=float)` raises on non-numeric strings in an object
  array (a placeholder such as `"-"`); coerce text at the boundary first (the
  pandas coerce path is on `library-corpus/pypi/pandas.md`).

## Testing
- `numpy.testing.assert_allclose(actual, desired, rtol=1e-07, atol=0)` and
  `assert_array_equal` compare arrays and report where they differ; plain `==`
  returns an array, and `assert (a == b).all()` hides the location.
- Observed in practice: an exact pin on a numeric library with no recorded
  reason is a finding. Before bumping it, write a characterization (golden
  output) test on real inputs and diff the outputs across the bump.

## Security defaults
- `np.load(..., allow_pickle=False)` is the default. Object arrays load through
  `pickle`, which the docs call not secure against maliciously constructed
  data, so `allow_pickle=True` on an untrusted `.npy` or `.npz` can execute
  code. Keep the default at a trust boundary.

## Operational behaviour
- Arrays live in memory, and many operations allocate a full-size result;
  `out=` and in-place operators reuse a buffer.
- Many NumPy operations release the GIL, so threads that spend most of their
  time in low-level NumPy code run in parallel, unlike pure-Python code (the
  offload pools are on `library-corpus/language/python.md`). The thread-safety
  guide recommends that each worker own its arrays; mutating an array shared
  between threads needs care the library does not provide.

## Interop
- SciPy, pandas and most numeric libraries take and return `ndarray`; their
  pages are `library-corpus/pypi/scipy.md` and `library-corpus/pypi/pandas.md`.
- Compiled extensions build against the NumPy C ABI, so a NumPy major-line
  move must be matched by every compiled dependent (below).
- Each SciPy release declares an upper bound on NumPy, so an old exact SciPy
  pin caps NumPy; upgrade the two together.

## Major lines

### 1.x line
- The scalar aliases `np.bool`, `np.int`, `np.float` and `np.object` were
  deprecated and then removed during the late 1.x releases. Use the builtins
  (`bool`, `int`, `float`, `object`) or sized types such as `np.int64`.

### 2.x line
- The C ABI breaks: an extension compiled against 1.x fails to import under
  2.x. Move the whole numeric stack (NumPy, SciPy, pandas, and every compiled
  dependent) together, behind a characterization test.
- Many aliases and namespace members are removed; read the 2.0 migration guide
  before the move.

## Upstream docs
- Docs: https://numpy.org/doc/stable/
- Repo: https://github.com/numpy/numpy
