# pandas — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`pandas` provides labelled, in-memory tables (`DataFrame`) and one-dimensional
labelled arrays (`Series`), each carrying an `Index`, built on NumPy. It adds
missing-data handling, automatic and explicit alignment on labels, group-by,
merge and join, reshaping, time series, and readers and writers for many file
formats. The distribution and the import are both `pandas`, imported by
convention as `pd`. Licence: BSD-3-Clause.

## Install, setup and configuration
- `pip install pandas` (or conda-forge), into a virtual environment. The
  required runtime dependencies are NumPy and `python-dateutil`, plus `tzdata`
  on Windows and Pyodide. pandas supports each dependency back to a release
  roughly two years old at the time of its own major or minor release.
- Optional dependencies enable single methods and install through extras, for
  example `pip install "pandas[excel]"`, `pandas[performance]` (bottleneck,
  numba, numexpr), `pandas[pyarrow]`. A missing optional dependency raises
  `ImportError` when the method that needs it is called, never at import, so a
  green import says nothing about `read_excel` or `read_parquet`.

## Core API / usage shape
- Construct with `pd.DataFrame(data, index=, columns=)` or a reader:
  `read_csv` (with `usecols=` and `chunksize=`), `read_parquet`, `read_excel`,
  `read_json`, `read_sql`, `read_html`, `read_pickle`. Each writer mirrors its
  reader (`to_csv`, `to_parquet`, ...).
- Select with `.loc` (labels) and `.iloc` (positions); assign conditionally with
  `df.loc[mask, "col"] = value`.
- `pd.to_numeric(arg, errors="raise", downcast=None)` parses to float64 or
  int64. `errors="coerce"` turns every unparseable value into NaN.
- `DataFrame.apply(func, axis=0)` passes each column as a `Series` (axis=1
  passes each row).
- `DataFrame.to_numpy(dtype=None, copy=False, na_value=...)` is the documented
  way out to NumPy. It may copy and coerce, which can be expensive.
- `DataFrame.query(expr)` and `pd.eval(expr)` evaluate string expressions;
  `query` reads local variables as `@name` and odd column names in backticks.
- `groupby(...).agg(...)`, `merge`, `concat`, `pivot_table` cover aggregation
  and joining.

## Idioms & best practices
- Coerce untrusted or mixed text column by column with
  `df.apply(pd.to_numeric, errors="coerce")`, then count the NaN cells it
  produced and fail above a threshold you chose. The threshold step is observed
  in practice; the docs only say that coerce yields NaN.
- Observed in practice: `np.asarray(x, dtype=float)` raises on placeholder
  strings such as `"-"` in an object array, while the coerce path above turns
  them into NaN, so the two are not interchangeable at a data boundary. The
  pandas docs do not compare the two.
- Test for missing values with `isna()` / `notna()` and handle them with
  `dropna()` / `fillna()`, never with `==`.
- Leave a frame through `.to_numpy()` with an explicit `dtype` and `na_value`.
  `.values` is not deprecated, yet only `to_numpy` lets you say what a missing
  value becomes.
- For large data, choose narrow dtypes (`category` for repeated text), load
  only the columns you need (`usecols`), and stream with `chunksize`.
- Observed in practice: pandas pulled in only for a little boundary cleanup is
  heavy runtime weight in a small service image. Replace it only behind a
  characterization test that pins the old outputs. The docs are silent on this
  trade-off.

## General pitfalls
- `to_numeric(errors="coerce")` never raises: bad input silently becomes NaN,
  so a data-quality failure reaches the output unless you count it.
- Missing values do not compare like `None`: `np.nan == np.nan` is False,
  `pd.NaT == pd.NaT` is False, and `pd.NA == pd.NA` is NA. Comparisons
  propagate the missing value.
- With NumPy dtypes, one missing value turns an integer or bool column into
  float64 or object. The nullable dtypes (`"Int64"`, `"boolean"`) keep the type
  and use `pd.NA`.
- Arithmetic and assignment align on index labels. A label present on one side
  only yields NaN, with no warning, which looks like data loss after a reorder or
  a reset index.
- `if series:` raises `ValueError` (the truth value is ambiguous); use `.any()`,
  `.all()`, `.empty`, or an explicit comparison.
- Chained assignment (`df["a"][0] = 1`, `df["a"].replace(1, 5, inplace=True)`)
  does not write back under Copy-on-Write. Assign through `.loc`, or assign the
  result of the method to the column.

## Testing
- `pandas.testing.assert_frame_equal(left, right, check_exact=, rtol=, atol=)`
  and `assert_series_equal` compare frames, dtypes and indexes; the tolerances
  apply to floating columns. A plain `==` gives an element-wise frame, and NaN
  never equals itself.
- Observed in practice: a pandas major-line bump changes dtypes and copy
  behaviour without failing an import, so a golden-output characterization test
  on real inputs, run before and after the bump, is the gate. The docs do not
  state this rule.

## Security defaults
- `read_pickle` (and any pickle input) can run arbitrary code: the docs warn
  that loading pickled data from untrusted sources is unsafe. Use Parquet, CSV
  or JSON at a trust boundary.
- `DataFrame.query` and `pd.eval` can run arbitrary code. User input must
  never reach the expression string.

## Operational behaviour
- Everything is in memory. The default dtypes are not the most compact,
  especially for text, and many operations copy, so peak memory is a multiple of
  the data size. Beyond memory, the scaling guide points to chunking or to other
  libraries such as Dask.
- The install pulls in NumPy and dateutil plus whatever extras you name, which
  counts in a small image.
- Failure and recovery are the caller's: pandas is a library with no service,
  thread pool or persistent state of its own to start, stop or recover.

## Interop
- NumPy: exchange through `to_numpy()`, the constructors, and `np.asarray`.
  The numeric pitfalls of the underlying arrays are on
  `library-corpus/pypi/numpy.md`.
- PyArrow is an optional backend: Arrow-backed dtypes (`"int64[pyarrow]"`)
  and Parquet IO use it, and in the 3.x line the default string dtype uses it
  when it is installed.
- Excel, Parquet, HTML and SQL readers each need their own optional package,
  listed with the reader on the IO page.

## Major lines

### 2.x line
- Copy-on-Write is opt-in (`pd.options.mode.copy_on_write = True`); the late
  2.x releases offer a `"warn"` mode that flags code whose behaviour will change.
  Upgrade to the last 2.x release first and clear its warnings before moving
  to 3.x.
- Strings default to `object` dtype; `pytz` is a required dependency.

### 3.x line
- Copy-on-Write is the default and only mode: every indexing result behaves as
  a copy, chained assignment never writes back, and the
  `mode.copy_on_write` option has no effect (it is slated for removal in 4.x).
  Under Copy-on-Write the array that `to_numpy()` returns for a plain view is
  read-only; copy it before writing.
- A dedicated string dtype (`str`) is inferred for text, Arrow-backed when
  PyArrow is installed and NumPy-object-backed otherwise; its missing value is
  always NaN. Code that tests `dtype == object` to find text columns breaks.
- `.values` and `np.asarray` on a frame holding NA in nullable dtypes give
  object dtype; pass `na_value=np.nan` to `to_numpy()` to keep float.
- `errors="ignore"` is gone from `to_numeric`, `to_datetime` and
  `to_timedelta`. Datetime and timedelta resolution is inferred instead of
  always nanoseconds. `pytz` is no longer required. Pickles written by pandas
  older than the 1.x line no longer load. The line requires Python 3.11 or newer.
- `pd.col()` expressions and callables in `DataFrame.assign` arrive as initial
  support.

## Upstream docs
- Docs: https://pandas.pydata.org/docs/
- Repo: https://github.com/pandas-dev/pandas
