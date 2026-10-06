# OpenTelemetry.Extensions.Hosting — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`OpenTelemetry.Extensions.Hosting` connects the OpenTelemetry .NET SDK to the
.NET Generic Host and the ASP.NET Core host. It registers an `IHostedService`
that starts the `TracerProvider`, `MeterProvider` and logger provider with the
host and disposes them when the host stops. It also gives one builder,
`OpenTelemetryBuilder`, for all three signals. The NuGet package id is
`OpenTelemetry.Extensions.Hosting`; it depends on the `OpenTelemetry` SDK
package. The source is the `open-telemetry/opentelemetry-dotnet` repository.
Licence: Apache-2.0. It targets .NET Framework 4.6.2, .NET Standard 2.0 and
current .NET.

## Install, setup and configuration
- `dotnet add package OpenTelemetry.Extensions.Hosting`, plus one package per
  instrumentation (for example `OpenTelemetry.Instrumentation.AspNetCore`,
  `OpenTelemetry.Instrumentation.Http`) and per exporter (for example
  `OpenTelemetry.Exporter.OpenTelemetryProtocol` for OTLP).
- Call `AddOpenTelemetry()` once in the host's startup code. Recent 1.x
  releases also offer `builder.AddOpenTelemetry()` on `IHostApplicationBuilder`.
  It seeds `service.name` from `IHostEnvironment.ApplicationName` and
  `deployment.environment.name` from the environment name, as low-priority
  defaults, and makes the host configuration visible to extensions during
  setup.
- Configuration keys follow the OpenTelemetry specification's environment
  variables, read through `IConfiguration`, so they can also come from
  `appsettings.json` or the command line. The ones that matter most:
  `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`,
  `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL` (`grpc` or
  `http/protobuf`), `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_EXPORTER_OTLP_TIMEOUT`,
  `OTEL_TRACES_SAMPLER` and `OTEL_TRACES_SAMPLER_ARG`. Values set in code take
  precedence over environment variables.
- OTLP exporter defaults: protocol gRPC to `localhost:4317`; with
  `http/protobuf` the default is `localhost:4318`. Metrics export every 60 s
  with cumulative temporality.
- Trace defaults: no `ActivitySource` is listened to until you add it, and the
  sampler is `ParentBased(root=AlwaysOn)`.
- Logger defaults (`OpenTelemetryLoggerOptions`): `IncludeFormattedMessage`,
  `IncludeScopes` and `ParseStateValues` are all `false`.

## Core API / usage shape
- `services.AddOpenTelemetry()` returns an `OpenTelemetryBuilder` with
  `ConfigureResource(Action<ResourceBuilder>)`,
  `WithTracing(Action<TracerProviderBuilder>)`,
  `WithMetrics(Action<MeterProviderBuilder>)`,
  `WithLogging(Action<LoggerProviderBuilder>)` and, from the OTLP exporter
  package, `UseOtlpExporter()`.
- Inside the signal builders: `AddSource("MyCompany.MyProduct.*")` for traces,
  `AddMeter("...")` for metrics, `AddAspNetCoreInstrumentation()`,
  `AddHttpClientInstrumentation()`, `SetSampler(...)`, and per-signal
  exporters such as `AddOtlpExporter()` or `AddConsoleExporter()`.
- `builder.Logging.AddOpenTelemetry(o => { ... })` configures the
  `ILogger` bridge and its `OpenTelemetryLoggerOptions`.
- `services.ConfigureOpenTelemetryTracerProvider(...)` and
  `ConfigureOpenTelemetryMeterProvider(...)` add to the providers from other
  places in the code without calling `AddOpenTelemetry()` again.
- `ConfigureResource(r => r.AddDetector(sp => ...))` resolves an
  `IResourceDetector` from DI at startup.
- Hosts with no hosted services (Blazor, for example) resolve
  `ITelemetryHostInitializer` and call `Initialize()` at startup; this
  interface exists in recent 1.x releases.

## Idioms & best practices
- Call `AddOpenTelemetry()` from application host code only. Library code
  follows the separate library-author guidance and does not register
  providers.
- Calling `AddOpenTelemetry()` more than once is safe: one `TracerProvider`
  and one `MeterProvider` exist per `IServiceCollection`. For separate
  providers, use `Sdk.CreateTracerProviderBuilder()` /
  `Sdk.CreateMeterProviderBuilder()`.
- Use the unified `AddOpenTelemetry()` builder, not the old per-signal
  `AddOpenTelemetryTracing` / `AddOpenTelemetryMetrics` entry points.
- Prefer `UseOtlpExporter()` when every signal goes to one OTLP endpoint. It
  can be called only once, and it cannot be mixed with signal-specific
  `AddOtlpExporter` calls; either mistake throws `NotSupportedException`.
- Name `ActivitySource`s and `Meter`s under a common prefix and subscribe with
  a wildcard, so new sources are not silently missed.
- Turn on `IncludeScopes` and `IncludeFormattedMessage` when log records must
  carry their scopes and rendered text. Both default to off. Observed in
  practice: services set both to `true` on the logging bridge so exported
  records kept scopes and the rendered message. Upstream documents the `false`
  defaults and adds that the formatted message is still included when no
  message template is found.

## General pitfalls
- A forgotten `AddSource` or `AddMeter` gives no error and no data: the SDK
  listens to nothing by default. Upstream calls this a common mistake.
- Sources and meters cannot be added after a provider is built.
- `AddOpenTelemetry()` inserts its services at the start of the collection,
  but that does not guarantee the SDK is running while other hosted services
  start, so their early telemetry can be lost.
- The default `ParentBased` sampler follows the caller's sampling decision.
  An upstream service that does not sample makes this service drop its spans
  too.
- With `http/protobuf`, an endpoint set on a signal exporter must include the
  signal path (`/v1/traces`); the base URL given to `UseOtlpExporter` gets the
  path appended for you.
- A `LoggerFactory` you create yourself must be disposed before exit or logs
  are dropped, and must not be disposed early or logging becomes a no-op.
- A Prometheus scraping endpoint mapped on a `MeterProvider` that has no
  Prometheus exporter throws while the middleware is built, so the host never
  starts serving ("A PrometheusExporter could not be found configured on the
  provided MeterProvider"). Guard the mapping with the same switch that adds
  the exporter. Observed in practice: with `OTEL_SDK_DISABLED=true`, which
  recent 1.x SDK releases honour by returning no-op providers, an
  unconditionally mapped endpoint crash-looped the service at start-up. Later
  releases of the pre-release `OpenTelemetry.Exporter.Prometheus.AspNetCore`
  package answer the scrape with an empty response on the SDK's no-op
  provider instead, so whether `OTEL_SDK_DISABLED` alone still crashes depends
  on the exporter version paired with the SDK; read that package's changelog
  for the pinned pair.

## Testing
- `OpenTelemetry.Exporter.InMemory` collects `Activity`, metric and
  `LogRecord` items into a list for assertions. It is for tests only.
- In a host-based test, add the in-memory exporter through
  `ConfigureOpenTelemetryTracerProvider(b => b.AddInMemoryExporter(list))`,
  not through a second provider; repeated `AddOpenTelemetry()` calls share the
  same providers.
- Force export before asserting, for example by disposing the provider or
  the test host, because batch processors and the metric reader export on a
  schedule.

## Security defaults
- The OTLP default endpoint is plain `localhost`; a remote collector needs an
  explicit `https` endpoint. Custom CA trust and mutual TLS are configured with
  `OTEL_EXPORTER_OTLP_CERTIFICATE`, `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` and
  `OTEL_EXPORTER_OTLP_CLIENT_KEY` (on .NET 8 and newer).
- Backend credentials usually travel in `OTEL_EXPORTER_OTLP_HEADERS`. Treat
  that value as a secret.
- Logs, span attributes and scopes can carry passwords, tokens and personal
  data. Upstream points to log redaction. Turning on `IncludeScopes` or
  `IncludeFormattedMessage` widens what leaves the process.

## Operational behaviour
- Start: the hosted service starts the providers with the host. If the SDK
  cannot start, it throws and the host does not start.
- Stop: the providers are disposed with the service container. Disposal calls
  `Shutdown` on every processor, which flushes pending batches. A process killed
  without a graceful host stop loses the last batch.
- Traces and logs export through batch processors (queue size, batch size and
  delay are configurable through the `OTEL_BSP_*` and `OTEL_BLRP_*` variables).
  Metrics export through a periodic reader.
- `WithMetrics` registers an `IMetricsListener` named `OpenTelemetry`, so the
  `Metrics:EnabledMetrics` configuration of `Microsoft.Extensions.Diagnostics`
  can switch meters on and off.
- The SDK writes the internal logs of its components to self-diagnostics,
  enabled with `OTEL_DOTNET_SELF_DIAGNOSTICS_LOG_DIRECTORY` or
  `OTEL_DOTNET_SELF_DIAGNOSTICS_SINKS`. Look there first when telemetry goes
  missing.

## Interop
- ASP.NET Core and `HttpClient`: instrumentation packages create the server
  and client spans and the HTTP metrics.
- `Microsoft.Extensions.Logging`: the logger provider bridges `ILogger` to
  OpenTelemetry logs; log records correlate with the active trace
  automatically.
- `Microsoft.Extensions.Diagnostics` metrics configuration: see the
  `IMetricsListener` point above.
- Libraries that emit through `ActivitySource` or `Meter` (Polly's `Polly`
  meter, for example) need only `AddSource` / `AddMeter` with their names.

## Major lines

### 1.x line
- The only stable line. The first stable release introduced
  `AddOpenTelemetry()` as the single entry point; pre-release versions had
  `AddOpenTelemetryTracing`, `AddOpenTelemetryMetrics`, `Configure` and
  `GetServices`, and all four are removed.
- Within 1.x, features arrive in minor releases: `WithLogging` became stable
  API, `UseOtlpExporter` appeared, and recent releases add the
  `IHostApplicationBuilder` overload and `ITelemetryHostInitializer`. Check the
  package changelog for the pinned version before relying on one of these.

## Upstream docs
- https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/src/OpenTelemetry.Extensions.Hosting
- https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry.Extensions.Hosting/CHANGELOG.md
- https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/src/OpenTelemetry.Exporter.OpenTelemetryProtocol
- https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/docs
- https://opentelemetry.io/docs/languages/dotnet/
- https://www.nuget.org/packages/OpenTelemetry.Extensions.Hosting
