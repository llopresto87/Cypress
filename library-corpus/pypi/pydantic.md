# pydantic — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`pydantic` (v2) is a data validation and schema library built on type hints.
Models subclass `BaseModel`; `pydantic-settings` (`BaseSettings`) is a companion
package for typed configuration loading.

## Core API / usage shape
- Define models by subclassing `BaseModel` with typed fields.
- `@field_validator(...)` must be paired with `@classmethod`:
  ```python
  @field_validator(...)
  @classmethod
  def check(cls, v): ...
  ```
- Serialize with `model_dump_json()` / `model_dump(mode="json")`; parse with
  `model_validate_json()`.
- `pydantic_settings.BaseSettings` with `model_config = {"env_file": ".env", ...}`
  loads config from a dotenv file and environment variables.

## Idioms & best practices
- Prefer `model_dump_json()` / `model_dump(mode="json")` over manual
  `json.dumps(model.dict())` when serializing for wire transport or test
  assertions.
- With `BaseSettings`, environment variables take priority over dotenv values,
  and an `env_file` with a bare filename only checks the current working
  directory (not parent directories).

## General pitfalls
- In `before` validators, avoid mutating the input value before raising a
  `ValidationError`, since the mutated value may still be passed along to other
  validators in the chain.
- `BaseSettings` validates default values by default (unlike plain `BaseModel`),
  which can produce unexpected validation errors.
- With a dotenv `env_file`, pydantic-settings enforces the model's `extra` setting
  (default `forbid`), so unrecognized keys in the `.env` file raise a
  `ValidationError` unless `extra='ignore'` is set.

## Upstream docs
- Docs: https://docs.pydantic.dev/
- Repo: https://github.com/pydantic/pydantic
