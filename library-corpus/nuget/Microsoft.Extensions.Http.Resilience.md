# Microsoft.Extensions.Http.Resilience — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`Microsoft.Extensions.Http.Resilience` adds resilience pipelines (rate
limiter, timeouts, retry, circuit breaker, hedging) to outbound `HttpClient`
calls made through `IHttpClientFactory`. It builds on
`Microsoft.Extensions.Resilience` and on Polly (https://github.com/App-vNext/Polly),
and it ships from the `dotnet/extensions` repository. The NuGet package id is
`Microsoft.Extensions.Http.Resilience`; the main namespace is
`Microsoft.Extensions.Http.Resilience`, and the option types it uses, such as
`DelayBackoffType`, come from the `Polly` namespace. Licence: MIT. It replaces
`Microsoft.Extensions.Http.Polly`, which Microsoft marks as deprecated.

## Install, setup and configuration
- `dotnet add package Microsoft.Extensions.Http.Resilience`. It brings
  `Microsoft.Extensions.Resilience`, `Microsoft.Extensions.Http.Diagnostics`
  and Polly with it.
- Every handler hangs off the `IHttpClientBuilder` that `AddHttpClient(...)`
  returns: named clients, typed clients, or
  `services.ConfigureHttpClientDefaults(b => b.AddStandardResilienceHandler())`
  for every client in the container.
- Options can come from code (`AddStandardResilienceHandler(o => ...)` or
  `.Configure(o => ...)` on the returned builder) or from configuration
  (`AddStandardResilienceHandler(IConfigurationSection)`), which binds
  `HttpStandardResilienceOptions`.
- Standard handler defaults, outermost to innermost:

  | Strategy | Option property | Defaults |
  |---|---|---|
  | Rate limiter | `RateLimiter` | 1000 concurrent permits, queue 0 |
  | Total timeout | `TotalRequestTimeout` | 30 s for the whole call, retries included |
  | Retry | `Retry` | 3 retries, exponential backoff, jitter on, 2 s base delay, honours `Retry-After` |
  | Circuit breaker | `CircuitBreaker` | 10% failure ratio, minimum throughput 100, 30 s sampling, 5 s break |
  | Attempt timeout | `AttemptTimeout` | 10 s per attempt |

- Retry and circuit breaker treat as transient: HTTP 5xx, 408 and 429, plus
  `HttpRequestException` and Polly's `TimeoutRejectedException`.
- Options are validated when the pipeline is built. `AttemptTimeout` must not
  exceed `TotalRequestTimeout`, and `CircuitBreaker.SamplingDuration` must be at
  least twice `AttemptTimeout.Timeout`. A violation is not a compile error: it
  surfaces as an options validation failure when the pipeline is first built.

## Core API / usage shape
- `AddStandardResilienceHandler()` adds the five-strategy pipeline above.
  Options expose `Retry` (`MaxRetryAttempts`, `Delay`, `BackoffType`,
  `UseJitter`, `ShouldRetryAfterHeader`, `ShouldHandle`, `DisableFor(...)`,
  `DisableForUnsafeHttpMethods()`), `CircuitBreaker` (`SamplingDuration`,
  `MinimumThroughput`, `FailureRatio`, `BreakDuration`), `RateLimiter`,
  `AttemptTimeout` and `TotalRequestTimeout`.
- `AddStandardHedgingHandler()` sends extra attempts in parallel when a
  request is slow or fails. It runs total timeout → hedging (1 to 10 attempts,
  2 s delay) → per-endpoint rate limiter, circuit breaker and attempt timeout.
  Circuit breakers are pooled per URL authority (scheme, host, port);
  `SelectPipelineByAuthority()` / `SelectPipelineBy(...)` set the key, and
  `ConfigureOrderedGroups` / `ConfigureWeightedGroups` route attempts across
  endpoints.
- `AddResilienceHandler(name, pipeline => { ... })` builds a custom
  `ResiliencePipelineBuilder<HttpResponseMessage>`: `AddRetry(new HttpRetryStrategyOptions {...})`,
  `AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions())`,
  `AddTimeout(TimeSpan)`, `AddConcurrencyLimiter(n)`, `AddFallback(...)`. The
  final pipeline name is the client name plus `name`. An overload that passes a
  `ResilienceHandlerContext` lets the pipeline read named options and call
  `EnableReloads<TOptions>(name)`, so a change in `appsettings.json` rebuilds
  the pipeline at runtime.
- Outside DI, wrap a handler yourself: `new ResilienceHandler(pipeline)` with
  a `SocketsHttpHandler` as inner handler, passed to a long-lived `HttpClient`.
- `request.SetResilienceContext(ctx)` / `GetResilienceContext()` carry a Polly
  `ResilienceContext` (operation key, properties) through the handler.

## Idioms & best practices
- Add one resilience handler per client and do not stack them. When a client
  needs a different pipeline, use `AddResilienceHandler` with the strategies
  you want.
- Disable retries for calls that are not idempotent:
  `o.Retry.DisableForUnsafeHttpMethods()` skips POST, PUT, PATCH, DELETE and
  CONNECT, and `DisableFor(HttpMethod.Post, ...)` picks methods by hand. The
  standard handler retries every method by default.
- Change one value at a time from the defaults and keep the validation
  invariants in view: raising `AttemptTimeout` usually means raising
  `CircuitBreaker.SamplingDuration` (to at least twice the attempt timeout) and
  `TotalRequestTimeout` too.
- Observed in practice: for a cheap, latency-sensitive dependency (a token
  introspection call, say), a custom handler with only a short retry and a
  short timeout, and no circuit breaker, was the better fit than the standard
  handler. The docs present the custom handler as the general way to get more
  control and do not discuss this case.
- Name custom pipelines and strategies. The names become the
  `pipeline.name` and `strategy.name` tags on Polly's metrics and logs.

## General pitfalls
- A client with no timeout strategy waits `HttpClient.Timeout`, which
  defaults to 100 s, on a slow dependency. Blocked calls then pile up in the
  caller. Observed in practice as the reason resilience was added at all; the
  100 s default is documented on `HttpClient.Timeout`.
- If you customize `ShouldHandle` on a retry that sits outside a timeout,
  decide whether it should handle `TimeoutRejectedException`. Polly throws that
  type on timeout, not `System.TimeoutException`.
- An open circuit throws `BrokenCircuitException`, and a rejected rate-limit
  permit throws `RateLimiterRejectedException`. Callers that only catch
  `HttpRequestException` miss both.
- Retrying POST without disabling it can insert a record twice.
- Registration order matters with other outbound handlers. Old Application
  Insights SDKs lose all telemetry when resilience is registered before
  `AddApplicationInsightsTelemetry()`; register telemetry first, or move to a
  fixed SDK. Old `Grpc.Net.ClientFactory` versions throw
  `InvalidOperationException` when the standard handlers are added to a gRPC
  client, and a build-time check warns about them
  (`SuppressCheckGrpcNetClientFactoryVersion` silences it).

## Testing
- Test your own settings and delegates, not Polly's internals. `Polly.Testing`
  provides `pipeline.GetPipelineDescriptor()`, which lists the strategies and
  their options so a test can assert the composition (for example, that retry
  has `MaxRetryAttempts = 4` and a timeout follows it).
- In unit tests of code that resolves a pipeline from
  `ResiliencePipelineProvider<string>`, substitute the provider and return
  `ResiliencePipeline.Empty`, so failure-path tests do not wait for real
  backoff delays.

## Security defaults
- The package opens no network surface and stores no credentials. Its
  security impact is behavioural: retries multiply the requests a dependency
  sees, and unsafe-method retries can repeat side effects. The default rate
  limiter caps concurrent outbound calls at 1000 per pipeline.
- Honouring `Retry-After` is on by default, so a server controls the delay
  before the next attempt. The total request timeout still bounds the whole
  call.

## Operational behaviour
- A pipeline is fetched from the resilience pipeline registry, keyed by client
  name and pipeline name, when the factory first creates a handler for that
  client. Option validation errors surface then, not at host startup.
- Each pipeline keeps in-memory state: circuit breaker health and rate limiter
  permits. The state is per process and per pipeline key; nothing is shared
  across instances or survives a restart.
- Telemetry is on by default through `Microsoft.Extensions.Resilience`:
  resilience events (`OnRetry`, `OnTimeout`, `OnCircuitOpened`,
  `OnRateLimiterRejected`, ...) are logged and counted on the
  `resilience.polly.strategy.events` instrument of the `Polly` meter.
  `services.AddResilienceEnricher()` adds `error.type`, `request.name` and
  `request.dependency.name` dimensions.
- `EnableReloads` rebuilds a pipeline when its bound options change, without
  restarting the process.

## Interop
- Polly: every strategy is a Polly strategy, and the Polly docs are the
  reference for each option. Use `AddResiliencePipeline` from
  `Microsoft.Extensions.Resilience` for non-HTTP work.
- `IHttpClientFactory` (`Microsoft.Extensions.Http`): handlers sit in the
  factory's handler chain, with the factory's handler pooling and lifetime.
- OpenTelemetry: add the `Polly` meter to the meter provider to export the
  resilience metrics.
- Application Insights and gRPC client factory: see the ordering and version
  pitfalls above.

## Major lines
The package version follows the .NET release line of `dotnet/extensions`.

### 8.x line
- First stable line. Targets .NET Framework 4.6.2, `net6.0` and `net8.0`.
  Standard resilience and hedging handlers, custom handlers and dynamic reload
  are all present. There is no `RemoveAllResilienceHandlers`.

### 9.x line
- Targets .NET Framework 4.6.2, `net8.0` and `net9.0`; `net6.0` is gone.
- Later 9.x releases add `RemoveAllResilienceHandlers()`, which clears handlers
  registered earlier (for example by `ConfigureHttpClientDefaults`) so one client
  can take a different pipeline. It is marked experimental: using it raises
  diagnostic `EXTEXP0001`, which you suppress on purpose.

### 10.x line
- Targets .NET Framework 4.6.2, `net8.0`, `net9.0`, `net10.0` and
  .NET Standard 2.0. `RemoveAllResilienceHandlers()` is still experimental.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience
- https://learn.microsoft.com/en-us/dotnet/core/resilience/
- https://github.com/dotnet/extensions/tree/main/src/Libraries/Microsoft.Extensions.Http.Resilience
- https://www.pollydocs.org/ (strategies, testing, telemetry)
- https://www.nuget.org/packages/Microsoft.Extensions.Http.Resilience
