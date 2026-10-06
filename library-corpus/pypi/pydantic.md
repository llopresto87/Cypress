# pydantic — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A data validation and schema library built on type hints, with a companion
package for configuration:

- `pydantic`: the library (v2). Models subclass `BaseModel`.
- `pydantic-settings`: the companion package for typed configuration loading
  (`BaseSettings`).

## Install, setup and configuration
- `pip install pydantic`. Its dependencies are `pydantic-core` (the validation
  core, written in Rust), `typing-extensions` and `annotated-types`. Optional
  extras: `pydantic[email]` (the `email-validator` package) and
  `pydantic[timezone]` (`tzdata`).
- `pydantic-core` ships as compiled wheels. Its source build uses the
  `maturin` backend with PyO3 bindings, and its README lists a stable Rust
  toolchain as a build prerequisite, so installing it where no prebuilt wheel
  exists needs Rust.
- Per-model configuration is the `model_config` class attribute, a dict.
  `extra` decides what happens to unknown input keys: `'ignore'` (the default
  for `BaseModel`) drops them, `'forbid'` rejects them, `'allow'` keeps them in
  `__pydantic_extra__`.
- `pydantic_settings.BaseSettings` with `model_config = {"env_file": ".env", ...}`
  loads config from a dotenv file and environment variables. With
  `BaseSettings`, environment variables take priority over dotenv values, and an `env_file` with a bare
  filename only checks the current working directory (not parent directories).

## Core API / usage shape
- Define models by subclassing `BaseModel` with typed fields.
- `@field_validator(...)` is documented with `@classmethod` stacked under it
  (the form type checkers expect). pydantic applies `classmethod` itself when
  the first parameter is named `cls`, so a missing one does not fail at runtime:
  ```python
  @field_validator(...)
  @classmethod
  def check(cls, v): ...
  ```
- Serialize with `model_dump_json()` / `model_dump(mode="json")`; parse with
  `model_validate_json()`; validate a dict with `model_validate()`.
- Instances carry `model_fields_set` (fields explicitly given) and
  `model_extra` (extra fields kept under `extra='allow'`).

## Idioms & best practices
- Prefer `model_dump_json()` / `model_dump(mode="json")` over manual
  `json.dumps(model.dict())` when serializing for wire transport or test
  assertions.
- Express legitimate absence in the type (`float | None`), not with a sentinel
  value.
- Observed in practice: when pydantic arrives only through FastAPI it is
  declared nowhere, so a FastAPI bump can move it across minor releases with no
  manifest diff. Declare it directly, with a floor, if you rely on its
  behaviour.

## General pitfalls
- In `before` validators, avoid mutating the input value before raising a
  `ValidationError`, since the mutated value may still be passed along to other
  validators in the chain.
- `BaseSettings` validates default values by default (unlike plain `BaseModel`),
  which can produce unexpected validation errors.
- With a dotenv `env_file`, pydantic-settings enforces the model's `extra` setting
  (default `forbid`), so unrecognized keys in the `.env` file raise a
  `ValidationError` unless `extra='ignore'` is set.
- Validation is lax by default: `{"x": "123"}` validates into `x: int` as
  `123`. Strict mode turns such coercions into errors.
- Observed in practice: a broad `except` around model construction turns a
  `ValidationError` into its fallback path. If the fallback returns the same
  keys, it also passes key-set and shape tests; only golden value tests tell
  the two paths apart.

## Testing
- Construct models from literal dicts in tests, and assert both the accepted
  shape and the rejection (`pytest.raises(ValidationError)`) for each
  constraint that matters.
- Observed in practice: compare values, not only keys, so a silent fallback
  path (above) cannot pass for the validated one.

## Security defaults
- `BaseModel` ignores unknown keys by default. At a trust boundary where
  unexpected fields signal an error, set `extra='forbid'`.
- Lax coercion accepts strings for numbers and similar; use strict mode for
  input where a type mismatch should be rejected.

## Operational behaviour
- Validation runs in `pydantic-core`'s compiled code. This page has no
  confirmed source on pydantic's thread-safety or memory behaviour.

## Interop
- FastAPI builds request and response validation and the OpenAPI schema on
  pydantic models (`library-corpus/pypi/fastapi.md`).
- `pydantic-settings` is a separate distribution; install it alongside.

## Major lines

### 1.x line
- Methods `.dict()`, `.json()`, `parse_obj`, `parse_raw`, validators
  `@validator` / `@root_validator`, and an inner `class Config`.

### 2.x line
- The core is rewritten in Rust (`pydantic-core`). Renames: `.dict()` to
  `model_dump()`, `.json()` to `model_dump_json()`, `parse_obj` to
  `model_validate`, `parse_raw` to `model_validate_json`, `@validator` to
  `@field_validator` (no `each_item`), `class Config` to `model_config`.
  The old names are deprecated.
- The 1.x API stays importable as `pydantic.v1` for a gradual migration, and
  the `bump-pydantic` tool rewrites code automatically (in beta).

## Upstream docs
- Docs: https://docs.pydantic.dev/
- Migration guide: https://docs.pydantic.dev/latest/migration/
- Repo: https://github.com/pydantic/pydantic
