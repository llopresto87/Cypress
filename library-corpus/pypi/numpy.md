# numpy — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
NumPy is the foundational numerical-computing package for Python: a
homogeneous, N-dimensional array (`ndarray`) backed by contiguous C memory,
with vectorized element-wise operations, linear algebra, FFTs, and random
number generation. It is the numeric substrate most of the scientific Python
ecosystem (SciPy, pandas, scikit-learn, image and ML libraries) builds on and
interoperates through. PyPI package name `numpy`.

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

## General pitfalls
- **Views vs copies**: a slice is a view — mutating it mutates the original;
  fancy indexing copies. Confusing the two causes silent aliasing bugs or
  unexpected non-mutation. Use `.copy()` when independence is required.
- **Floating-point comparison**: never compare floats with `==`; use
  `np.isclose` / `np.allclose` with tolerances.
- Broadcasting can silently succeed on unintended shapes and produce a wrong-shape
  result rather than an error; assert shapes when it matters.
- In-place operations and dtype promotion can truncate (e.g. writing a float into
  an int array) without warning.

## Upstream docs
- Docs: https://numpy.org/doc/stable/
- Repo: https://github.com/numpy/numpy
