# ahrs — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
AHRS is a pure-Python toolbox of attitude and heading estimation algorithms
built on NumPy: estimators (filters) that turn gyroscope, accelerometer and
magnetometer samples into orientation, plus quaternion, direction-cosine-matrix
and other orientation utilities. The distribution is `AHRS` (installed as
`pip install ahrs`); the import is `ahrs`. Licence: MIT. The project states its
focus as prototyping, teaching, testing and modularity, with performance not
the main goal, and its docs say it is in no way recommended for commercial
use (a project statement, not a licence term).

## Install, setup and configuration
- `pip install ahrs`. The runtime dependencies are NumPy and docutils. The
  registry metadata and the installation page disagree on the minimum Python
  version; the registry metadata is what pip enforces.
- There is no global configuration. Each estimator is configured through its
  constructor: sampling `frequency` (default 100.0 Hz) or step `Dt` (default
  `1/frequency`), the filter gains, and an optional initial orientation `q0`.
  Gains, `frequency` and `Dt` are validated as positive numbers.

## Core API / usage shape
- Estimators are classes under `ahrs.filters`, imported as
  `from ahrs.filters import Madgwick`. The catalogue includes angular-rate
  integration, AQUA, Complementary, Davenport, EKF, FAMC, FLAE, Fourati, FQA,
  Madgwick, Mahony, OLEQ, QUEST, ROLEQ, SAAM, Tilt and TRIAD (and FKF/UKF on
  the 0.4 line). The estimator page says, per filter, whether it is recursive
  or instantaneous and which sensors it needs.
- Batch: `Madgwick(gyr=gyr, acc=acc[, mag=mag], frequency=..., gain=...)`
  computes every orientation at construction and stores them in `.Q`, an
  N-by-4 array. With `mag` it uses the MARG update; without it, the IMU update.
  `gain_imu` (default 0.033) and `gain_marg` (default 0.041) set the two gains
  separately.
- Streaming: `f.updateIMU(q, gyr, acc, dt=None)` returns the next quaternion
  from the previous one and one sample; `f.updateMARG(q, gyr, acc, mag,
  dt=None)` adds a magnetometer sample. Seed the loop with `[1.0, 0.0, 0.0,
  0.0]` and reassign `f.Dt` (or pass `dt`) when the sample step changes.
- Units: gyroscope in rad/s, accelerometer in m/s², magnetometer in mT, each
  as N-by-3 arrays. Quaternions are scalar-first `(w, x, y, z)` and use the
  Hamilton product.

## Idioms & best practices
- Pass the true sampling rate of the data as `frequency` (or `Dt`) every time;
  never rely on the default.
- Give `q0` as a normalized quaternion (the docs call it a versor).
- Observed in practice: use the batch constructor when all samples are
  available and the streaming update only for live data or irregular timing.
  The batch constructor still loops in Python internally, so the gain is
  convenience, not vectorized speed.
- Change a gain only behind a characterization test: the gains trade
  correction of gyroscope drift against sensitivity to accelerometer and
  magnetometer noise.

## General pitfalls
- `frequency` defaults to 100 Hz. Data sampled at another rate, with neither
  `frequency` nor `Dt` given, is integrated with the wrong time step on every
  sample, and nothing fails.
- No unit conversion is applied. Degrees per second, g, or raw sensor counts
  produce plausible-looking but wrong orientations.
- Quaternion order: AHRS is scalar-first; SciPy `Rotation` is scalar-last.
  Reorder at the boundary (`library-corpus/pypi/scipy.md` holds the bridge).
- CPU cost grows linearly with the sample count in pure Python; long recordings
  are slow.
- Observed in practice: a port of another tool's filter (a MATLAB `imufilter`,
  say) does not match it bit for bit, because algorithm variants, gains and
  initial-orientation handling differ. Keep the reference implementation's
  output as the oracle. Upstream says nothing on cross-tool equivalence.

## Testing
- Upstream publishes no testing guidance for callers. The observed practice is
  a characterization test: run the filter on a recorded input with fixed
  `frequency`, gains and `q0`, and compare `.Q` with stored reference output
  under a numeric tolerance (`numpy.testing.assert_allclose`).

## Security defaults
- The estimators take NumPy arrays and do no network, file or deserialization
  work, so the library adds no attack surface of its own beyond what NumPy
  carries.

## Operational behaviour
- A pure computation library: no threads, services, files or state outside the
  estimator object. The only operational cost is CPU time per sample.

## Interop
- Inputs and outputs are NumPy arrays; `.Q` feeds straight into NumPy code.
- SciPy `Rotation` needs scalar-last quaternions; reorder (or use SciPy's
  scalar-first option where your SciPy line has it), as described on
  `library-corpus/pypi/scipy.md`.

## Major lines
Releases are 0.x, so a minor line can change the API, and a caret constraint
on a 0.x line admits only that line.

### 0.3 line
- The estimator catalogue above without FKF and UKF.

### 0.4 line
- Adds the FKF and UKF filters and the `sensors` and `geodesy` submodules.

## Upstream docs
- Docs: https://ahrs.readthedocs.io/
- Repo: https://github.com/Mayitzin/ahrs
