# opentelemetry-sdk-node — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
OpenTelemetry JS is the JavaScript implementation of OpenTelemetry, the
vendor-neutral standard for traces, metrics and logs. On Node.js it is a family
of packages: a small API that code is instrumented against, an SDK that turns
those calls into real telemetry, instrumentation packages that patch common
libraries, and exporters that ship the data to a collector or backend. Without
an SDK registered, every API call is a no-op.

- `@opentelemetry/api`: the API, made of interfaces, enums and no-op
  implementations (`trace`, `context`, `metrics`, `propagation`, `diag`).
  Needed by every package or module that creates spans or metrics, and the only
  OpenTelemetry package a library should depend on.
- `@opentelemetry/sdk-node`: the `NodeSDK` class, which wires the tracing and
  metrics SDKs, resource detection, propagation, exporters and
  instrumentations in one object. Needed once per application process, in the
  bootstrap file; libraries never need it.
- `@opentelemetry/auto-instrumentations-node`: a metapackage bundling the
  Node instrumentations (http, express, pg, redis, pino and many more) behind
  `getNodeAutoInstrumentations()` and a `register` entry point for zero-code
  setup. Needed when the application wants spans from its libraries without
  instrumenting them by hand; it lives in the separate contrib repository and is
  versioned independently.
- `@opentelemetry/exporter-trace-otlp-proto`: the OTLP trace exporter over
  HTTP with protobuf payloads. Needed when spans go to an OTLP endpoint and the
  code constructs the exporter itself (the SDK's own default protocol).
- `@opentelemetry/exporter-trace-otlp-http`: the OTLP trace exporter over
  HTTP with JSON payloads. Needed when the endpoint wants OTLP/JSON, or in a
  browser.
- `@opentelemetry/exporter-trace-otlp-grpc`: the OTLP trace exporter over
  gRPC. Needed when the collector is reached on its gRPC port; not usable in
  browsers.

Supporting packages the examples below cite but this page does not own:
the tracing SDK (`@opentelemetry/sdk-trace-node` and
`@opentelemetry/sdk-trace-base` in the 2 line, `@opentelemetry/sdk-trace` in
the 3 line: tracer provider, span processors, `ConsoleSpanExporter`),
`@opentelemetry/sdk-metrics` (meter provider, metric readers,
`ConsoleMetricExporter`), `@opentelemetry/resources`,
`@opentelemetry/semantic-conventions`, `@opentelemetry/instrumentation`
(the ESM loader hook), and the per-signal metric exporters
(`@opentelemetry/exporter-metrics-otlp-proto`, `-http`, `-grpc`).

Licence: Apache-2.0. Upstream home: https://opentelemetry.io/docs/languages/js/
and the repositories open-telemetry/opentelemetry-js (API, SDK, OTLP
exporters) and open-telemetry/opentelemetry-js-contrib (instrumentations,
auto-instrumentations).

## Install, setup and configuration
- Application: `npm install @opentelemetry/api @opentelemetry/sdk-node
  @opentelemetry/auto-instrumentations-node`, plus an exporter package when
  the code constructs one. Library: `@opentelemetry/api` only.
- **The SDK lives in its own bootstrap file that runs before the
  application.** Upstream's shape:
  ```js
  // instrumentation.mjs
  import { NodeSDK } from '@opentelemetry/sdk-node';
  import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-proto';
  import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

  const sdk = new NodeSDK({
    serviceName: 'my-service',
    traceExporter: new OTLPTraceExporter({ url: 'http://collector:4318/v1/traces' }),
    instrumentations: [getNodeAutoInstrumentations()],
  });
  sdk.start();
  ```
  Load it with `node --require ./instrumentation.cjs app.js` (CommonJS) or
  `node --import ./instrumentation.mjs app.js`. Running a TypeScript bootstrap
  through `--import` needs Node.js 20 or later.
- **ES modules need the loader hook as well.** An app that is ESM (a `.mjs`
  entry, `"type": "module"`, or TypeScript compiled to ESM) must also pass
  `--experimental-loader=@opentelemetry/instrumentation/hook.mjs`, on the
  command line or in `NODE_OPTIONS`; without it, imported modules are not
  patched. Upstream names this the only supported hook (calling
  `import-in-the-middle/hook.mjs` directly may stop working) and says the
  recommendation will move to Node's `module.register()`.
- **Zero-code setup.** `node --require
  @opentelemetry/auto-instrumentations-node/register app.js` (or `--import`
  plus the loader hook for ESM) starts an SDK configured only from `OTEL_*`
  environment variables. Instrumentation options cannot be set that way;
  anything beyond enabling and disabling needs the programmatic bootstrap.
- `NodeSDK` options and their defaults: `traceExporter` (wrapped in a
  `BatchSpanProcessor`) or `spanProcessors`; a metric reader (`metricReader`
  in the 2 line, the `metricReaders` array in the 3 line; metrics stay
  uninitialized without one); `views`; `logRecordProcessors`;
  `instrumentations` (none by default); `resource` and `serviceName`;
  `autoDetectResources` (default `true`) and `resourceDetectors` (default env,
  process, host); `sampler` (default samples every trace); `contextManager`
  (default `AsyncLocalStorage`); `textMapPropagator` (default W3C Trace
  Context plus Baggage); `spanLimits`.
- **When the code sets no trace exporter**, `NodeSDK` does not drop spans: it
  builds the default OTLP exporter (HTTP/protobuf) with a batch processor and
  sends to `http://localhost:4318/v1/traces` unless an endpoint variable says
  otherwise. Only a missing metric reader leaves a signal off.
- Environment variables the SDK reads (code options win where both exist):
  - `OTEL_SERVICE_NAME` (default `unknown_service`; overrides a `service.name`
    in `OTEL_RESOURCE_ATTRIBUTES`) and `OTEL_RESOURCE_ATTRIBUTES`
    (`k1=v1,k2=v2`).
  - `OTEL_TRACES_EXPORTER` (the Node SDK README lists `otlp`, `zipkin` and
    `none`; default `otlp`), `OTEL_METRICS_EXPORTER` (`otlp`, `prometheus`, `console`,
    `none`; default `otlp`), `OTEL_LOGS_EXPORTER` (`otlp`, `console`,
    `none`; default `otlp`).
  - `OTEL_EXPORTER_OTLP_PROTOCOL` (`grpc`, `http/protobuf`, `http/json`;
    the Node SDK defaults to `http/protobuf`), with per-signal variants.
  - `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://localhost:4318` for HTTP,
    `http://localhost:4317` for gRPC). For HTTP the SDK appends `/v1/traces`,
    `/v1/metrics`, `/v1/logs`; the per-signal
    `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` gets no path added, so it carries
    the path itself (upstream's default and examples end in `/v1/traces`). gRPC endpoints never take a path.
  - `OTEL_EXPORTER_OTLP_HEADERS` (`k=v,k=v`, added to every export) and
    `OTEL_EXPORTER_OTLP_TIMEOUT` (default 10000 ms).
  - `OTEL_TRACES_SAMPLER` (default `parentbased_always_on`) and
    `OTEL_TRACES_SAMPLER_ARG` (a ratio for the `traceidratio` samplers).
  - `OTEL_PROPAGATORS` (default `tracecontext,baggage`).
  - `OTEL_METRIC_EXPORT_INTERVAL` (default 60000 ms) and
    `OTEL_METRIC_EXPORT_TIMEOUT` (default 30000 ms).
  - `OTEL_NODE_RESOURCE_DETECTORS` (`env`, `host`, `os`, `process`,
    `serviceinstance`, `all`, `none`; run in the order listed). The
    auto-instrumentations `register` entry point also accepts `container` and
    the cloud detectors (`alibaba`, `aws`, `azure`, `gcp`).
  - `OTEL_NODE_ENABLED_INSTRUMENTATIONS` and
    `OTEL_NODE_DISABLED_INSTRUMENTATIONS` (auto-instrumentations only; names
    without the `@opentelemetry/instrumentation-` prefix; the disabled list is
    applied last, so a name in both is disabled).
  - `OTEL_SDK_DISABLED=true` turns the SDK off; `OTEL_LOG_LEVEL` (`none`
    through `all`, default `info`) sets its own diagnostic logging.

## Core API / usage shape
```js
import { trace, SpanStatusCode } from '@opentelemetry/api';

const tracer = trace.getTracer('orders', '1.2.0'); // scope name required, version recommended

export async function placeOrder(order) {
  return tracer.startActiveSpan('placeOrder', async (span) => {
    try {
      span.setAttribute('order.items', order.items.length);
      return await save(order);
    } catch (err) {
      span.recordException(err);
      span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
      throw err;
    } finally {
      span.end();
    }
  });
}
```
- `trace.getTracer(name, version)` and `metrics.getMeter(name, version)`
  return a tracer or meter for one instrumentation scope; upstream advises
  calling them where needed rather than exporting an instance, which avoids
  load-order problems.
- `startActiveSpan(name, fn)` makes the span current for the callback, so
  spans started inside become its children; upstream recommends it in most
  cases. `startSpan` creates a span without making it current (sibling work).
- Spans have status `Unset` by default, meaning completed without error. Set
  `ERROR` on failure and pair it with `recordException`; `OK` is for an
  explicit success override only. Events (`addEvent`) are timestamped messages
  on a span; links tie a span to causally related ones.
- Metrics instruments: counter (`add`, non-negative), up-down counter,
  histogram (`record`), and observable counter, up-down counter and gauge read
  through callbacks.
- `@opentelemetry/semantic-conventions` exports the standard attribute names
  (`ATTR_SERVICE_NAME`, HTTP and database attributes) as constants.
- `diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG)` shows what the
  SDK is doing when nothing arrives at the backend.
- `sdk.shutdown()` returns a promise that flushes and stops every provider.

## Idioms & best practices
- Instrument against `@opentelemetry/api` only. Keep `NodeSDK`, exporters and
  instrumentation choices in the one bootstrap file, so the backend can change
  without touching instrumented code. A library depends on the API alone and
  emits telemetry only when the application installs an SDK.
- Start the SDK first, from a preload flag rather than an import at the top of
  the entry file: the flag guarantees ordering even when the bundler or the
  module system would hoist other imports.
- Set `service.name` (`serviceName` or `OTEL_SERVICE_NAME`): upstream calls it
  mandatory, and `unknown_service` is what every unnamed process reports.
  Add `service.version`.
- Keep the default batch span processor. `SimpleSpanProcessor` exports each span
  as it ends and can add significant overhead; it suits tests and debugging.
- Export to an OpenTelemetry Collector in production rather than straight to a
  vendor backend: upstream recommends routing telemetry through it.
- Prefer individual instrumentation packages when the set is known: the
  metapackage is convenient but enlarges the dependency graph. When listing
  them by hand, put `HttpInstrumentation` before framework instrumentations
  such as Express, which expect the HTTP layer to be instrumented.
- Shut the SDK down on `SIGTERM` (and before a short-lived script exits) so
  the last batch is flushed.
- Use the console exporters (`ConsoleSpanExporter`, `ConsoleMetricExporter`)
  only for local debugging.

## General pitfalls
- **The API and the SDK do not share a version.** Packages ship in three
  release lines: the API (`@opentelemetry/api`, a 1.x line), the stable SDK
  packages (one shared version), and the experimental packages (one shared
  0.x version), which include `@opentelemetry/sdk-node`, the OTLP exporters and
  `@opentelemetry/instrumentation`. Contrib packages such as the
  auto-instrumentations metapackage follow their own versions. Upgrade the
  stable and experimental sets together, using upstream's compatibility table,
  and check each package's minimum API peer version.
- **A late start yields no telemetry and no error.** Instrumentation patches a
  module when it is loaded; anything loaded before `sdk.start()` stays
  unpatched, and code that ran before the SDK registered received no-op
  tracers and meters.
- **A second copy of the API can go silent.** The API keeps its global
  registration on a process-wide object; a package whose API copy is
  incompatible with the registered one gets the no-op implementation. Keep one
  resolved `@opentelemetry/api` in the tree.
- **An ESM app without the loader hook runs uninstrumented.** `--import` alone
  loads the bootstrap first, but ESM imports are patched only through the hook.
  `ts-node` requires CommonJS; `tsx` runs TypeScript as ESM only with `--import`.
- **Two preloads conflict.** A `--require .../register` left in `NODE_OPTIONS`
  alongside a hand-written bootstrap loaded with `--import` or `--require`
  sets the SDK up twice; upstream tells users to make sure no such conflicting
  flag is present.
- **No exporter in code is not "no export".** `NodeSDK` falls back to OTLP over
  HTTP to localhost, so a process with no collector beside it keeps exporting
  to an endpoint where nothing listens. Set `OTEL_TRACES_EXPORTER=none` (or `OTEL_SDK_DISABLED=true`)
  to switch export off on purpose; with the API and no SDK at all, spans are
  no-ops and cost almost nothing.
- **A traces endpoint without its path.** The base
  `OTEL_EXPORTER_OTLP_ENDPOINT` gets `/v1/traces` appended; the per-signal
  variable does not, so a bare host there posts to the wrong URL.
- **Unended spans.** A span that is never ended is never exported, and a child
  left open keeps measuring past its work. Always end in `finally`.
- `fs` and `host-metrics` are off by default in the auto-instrumentations
  metapackage, and `OTEL_NODE_ENABLED_INSTRUMENTATIONS` is the switch that
  turns a default-disabled one on.

## Testing
- Upstream's Node.js docs give no test recipe for applications. What they do
  give: `SimpleSpanProcessor` exports each span as it ends, which suits tests
  and debugging where the batch delay gets in the way.
- To check a bootstrap end to end, run the app with the console exporters and
  `OTEL_LOG_LEVEL=debug` and confirm spans print per request.
- A test that only checks the API calls passes even with no SDK running, since
  the API never throws for being unconfigured.

## Security defaults
- The OTLP endpoints default to plain `http://` on localhost. A remote
  collector needs an `https://` URL; nothing upgrades it for you.
- `OTEL_EXPORTER_OTLP_HEADERS` is where backend credentials usually go. It
  is an environment variable, so it is readable by anything that can read the
  process environment.
- Span attributes, events, recorded exceptions and resource attributes leave
  the process as-is. Instrumentations record request details (methods, URLs,
  statement shapes), and resource detectors (`host`, `process`, `os`) describe
  the machine; restrict `OTEL_NODE_RESOURCE_DETECTORS` and use instrumentation
  hooks when that matters.
- The SDK's diagnostic log always goes to the console; `debug` is very verbose
  and upstream recommends `info` in production.
- In a browser, the OTLP endpoint must be allowed by the Content Security
  Policy and CORS, and upstream advises a reverse proxy in front of the
  collector rather than exposing it.

## Operational behaviour
- Startup: `sdk.start()` detects resources, registers the global providers and
  propagator, and enables the instrumentations. An async resource detector's
  attribute values may still be pending when the first spans are created.
- Export: spans are batched and sent in the background; metrics are read and
  exported every `OTEL_METRIC_EXPORT_INTERVAL` (default 60 s). Each export
  request times out after `OTEL_EXPORTER_OTLP_TIMEOUT` (default 10 s).
- Shutdown: `sdk.shutdown()` flushes pending batches and stops the providers.
  A process killed or exiting without it loses whatever is still buffered.
- Cost: sampling defaults to every trace (`parentbased_always_on`); lower it
  with `traceidratio` samplers where volume matters. The batch processor keeps
  per-span overhead off the request path.
- Disabled: `OTEL_SDK_DISABLED=true` leaves the API in no-op mode.

## Interop
- [pino](pino.md): `@opentelemetry/instrumentation-pino` (part of the
  auto-instrumentations set) injects `trace_id`, `span_id` and `trace_flags`
  into every record logged inside an active span (`logKeys` renames them) and,
  for pino 7 and later, can also forward records to the Logs SDK when a logger
  provider is configured. Start the SDK before pino is loaded.
- Natively instrumented frameworks (Next.js, for one) emit spans once an SDK is
  registered, with no instrumentation package.
- Collectors and backends: anything that accepts OTLP, a Zipkin server through
  `@opentelemetry/exporter-zipkin`, or Prometheus, preferably through its
  OTLP receiver and otherwise through `@opentelemetry/exporter-prometheus`
  (a scrape endpoint on port 9464).
- Fastify: the auto-instrumentations set no longer includes a fastify
  instrumentation; upstream points to `@fastify/otel`.

## Major lines

### Stable SDK 1.x (experimental 0.5x and earlier)
- `new Resource({...})`, `Resource.default()`, synchronous resource detectors,
  `BasicTracerProvider#addSpanProcessor` and `MeterProvider#addMetricReader`
  are the setup idioms; the tracer providers read `OTEL_TRACES_EXPORTER` and
  `OTEL_PROPAGATORS` themselves.

### Stable SDK 2.x (experimental 0.200 and later)
- The stable 2.0 packages pair with the experimental 0.200 packages, and
  `@opentelemetry/api` stays on its 1.x line.
- Minimums: Node.js `^18.19.0 || >=20.6.0`; TypeScript 5.0.4, which also
  applies to `@opentelemetry/api` and `@opentelemetry/semantic-conventions`;
  ES2022 output for every package except the API packages and
  semantic-conventions.
- `Resource` is no longer exported: use `resourceFromAttributes()`,
  `defaultResource()` and `emptyResource()`; sync and async detectors merge
  (`detectResources`, `hostDetector`).
- Span processors and metric readers go in the constructor
  (`spanProcessors`, `readers`); `addSpanProcessor`, `addMetricReader` and
  `BasicTracerProvider#register()` are gone, and only `NodeSDK` reads
  `OTEL_TRACES_EXPORTER` and `OTEL_PROPAGATORS`.
- `parentSpanId` becomes `parentSpanContext`, `instrumentationLibrary`
  becomes `instrumentationScope`, and an invalid `OTEL_TRACES_SAMPLER` falls
  back to the parent-based always-on sampler.
- `NodeSDK`'s `metricReader` option narrows to the `IMetricReader` type.
- The auto-instrumentations metapackage states compatibility with API and SDK
  2.0 and later.

### Stable SDK 3.x (experimental 0.300 and later)
Upstream's 3.x migration guide and announcement were written ahead of the
final 3.0 release, while npm carried the 3 line only as release candidates
under the `canary` tag (`latest` still on the 2 line): confirm each item below
against the final 3.0 release notes before relying on it. The API stays on its 1.x line
with no breaking changes for instrumented code, though a 3-line SDK may need a
newer API minor.
- Node.js `>=22.15.0` for every package except `@opentelemetry/api` and
  `@opentelemetry/semantic-conventions`.
- One tracing SDK, `@opentelemetry/sdk-trace`, replaces `sdk-trace-base`,
  `sdk-trace-node` and `sdk-trace-web`. `BasicTracerProvider` becomes
  `TracerProvider`; `NodeTracerProvider#register()` is gone, so code that
  builds its own provider sets the global provider, context manager and
  propagator itself. The tracing SDK no longer reads `OTEL_TRACES_SAMPLER`,
  the span-limit variables or the `OTEL_BSP_*` batch settings: upstream
  directs environment-driven configuration to `NodeSDK`.
- Processor constructors take an options object:
  `new BatchSpanProcessor({ exporter, ... })`,
  `new SimpleSpanProcessor({ exporter, ... })`.
- `NodeSDK` drops its singular options (`metricReader`, `spanProcessor`,
  `logRecordProcessor`) for the arrays `metricReaders`, `spanProcessors`
  and `logRecordProcessors`, and drops its namespace re-exports (`api`,
  `core`, `tracing`, `node`, `logs`, `metrics`, `resources`): import from
  each package directly.
- The Logs API moves into `@opentelemetry/api`; `@opentelemetry/api-logs`
  is removed.
- Packages with Node and browser builds pick the Node build through the
  `node` condition of a `#platform` import, so a bundler must support the
  `imports` and `exports` fields, and a bundle built for Node without the
  `node` condition silently gets the browser build.
- The Jaeger exporter and propagator are removed: export OTLP, and move every
  service to W3C Trace Context together (or run both propagators while they
  move), since a mixed fleet breaks trace correlation.

## Upstream docs
- Node.js getting started: https://opentelemetry.io/docs/languages/js/getting-started/nodejs/
- Instrumentation (API usage): https://opentelemetry.io/docs/languages/js/instrumentation/
- Exporters: https://opentelemetry.io/docs/languages/js/exporters/
- Instrumentation libraries: https://opentelemetry.io/docs/languages/js/libraries/
- Zero-code: https://opentelemetry.io/docs/zero-code/js/
- SDK environment variables: https://opentelemetry.io/docs/languages/sdk-configuration/
- ESM support: https://github.com/open-telemetry/opentelemetry-js/blob/main/doc/esm-support.md
- Upgrade to 2.x: https://github.com/open-telemetry/opentelemetry-js/blob/main/doc/upgrade-to-2.x.md
- Upgrade to 3.x: https://github.com/open-telemetry/opentelemetry-js/blob/main/doc/3.x/migration-guide.md
- SDK repository and compatibility table: https://github.com/open-telemetry/opentelemetry-js
- Contrib (auto-instrumentations): https://github.com/open-telemetry/opentelemetry-js-contrib
