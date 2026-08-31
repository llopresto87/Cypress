# Microsoft.Extensions.Http.Resilience — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Provides Polly-based HTTP resilience pipelines (retry, circuit breaker, timeout,
hedging) for outbound `HttpClient` calls. It builds on Polly
(https://github.com/App-vNext/Polly).

## Core API / usage shape
- Register the standard pipeline on an `IHttpClientBuilder` with
  `AddStandardResilienceHandler(options => {...})`. Options expose `Retry`
  (`MaxRetryAttempts`, `Delay`, `BackoffType`, `UseJitter`, `DisableFor(...)`,
  `DisableForUnsafeHttpMethods()`), `CircuitBreaker` (`SamplingDuration`,
  `MinimumThroughput`, `FailureRatio`, `BreakDuration`), `AttemptTimeout`, and
  `TotalRequestTimeout`.
- For custom or multiple pipelines, use `AddResilienceHandler(name, pipeline => {...})`
  and compose strategies with `pipeline.AddRetry(new HttpRetryStrategyOptions {...})`
  and `pipeline.AddTimeout(TimeSpan)`.
- Options validation requires `CircuitBreaker.SamplingDuration` to be at least
  double `AttemptTimeout.Timeout`.

## Idioms & best practices
- Add only one resilience handler per `HttpClient`; avoid stacking handlers. Use
  `AddResilienceHandler` when you genuinely need multiple/custom pipelines.
- The standard resilience handler retries all HTTP methods, including unsafe
  ones (POST/PUT/PATCH/DELETE). Disable retries for non-idempotent calls via
  `options.Retry.DisableFor(...)` or `DisableForUnsafeHttpMethods()` to avoid
  duplicate side effects.

## General pitfalls
- When combining retry and timeout with a customized `ShouldHandle`, decide
  explicitly whether it should handle Polly's `TimeoutRejectedException` — this
  is *not* the standard `System.TimeoutException`.
- Ordering matters relative to other outbound handlers (e.g. telemetry/gRPC
  client factory handlers); registration order can cause incompatibilities or
  lost telemetry.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience
- https://github.com/dotnet/extensions
- https://www.nuget.org/packages/Microsoft.Extensions.Http.Resilience
