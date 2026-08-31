# OpenTelemetry.Extensions.Hosting — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Hosting integration for OpenTelemetry .NET. It provides the extension methods
that wire the OpenTelemetry `TracerProvider`, `MeterProvider`, and log provider
into the .NET Generic Host / ASP.NET Core host.

## Core API / usage shape
- `builder.Services.AddOpenTelemetry()` returns an `OpenTelemetryBuilder`, which
  exposes `ConfigureResource(Action<ResourceBuilder>)`,
  `WithTracing(Action<TracerProviderBuilder>)`,
  `WithMetrics(Action<MeterProviderBuilder>)`,
  `WithLogging(Action<LoggerProviderBuilder>)`, and `UseOtlpExporter()`.
- Logging can also be configured via
  `builder.Logging.AddOpenTelemetry(Action<OpenTelemetryLoggerOptions>)`.

## Idioms & best practices
- `AddOpenTelemetry()` is intended to be called by application host code, not by
  library code (library authors have separate instrumentation guidance).
- Calling `AddOpenTelemetry()` multiple times does not create multiple
  providers — only one TracerProvider and/or MeterProvider is instantiated per
  `IServiceCollection` regardless of how many times it is called.
- Use the unified `AddOpenTelemetry()` + `WithTracing()`/`WithMetrics()` builder
  pattern rather than the older per-signal `AddOpenTelemetryTracing` /
  `AddOpenTelemetryMetrics` entry points.

## Upstream docs
- https://opentelemetry.io/docs/languages/net/
- https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/src/OpenTelemetry.Extensions.Hosting
- https://www.nuget.org/packages/OpenTelemetry.Extensions.Hosting
