# pino — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Pino is a low-overhead structured logger for Node.js. Each log call writes one
line of newline-delimited JSON (NDJSON) carrying a numeric `level`, a `time`, the
logger's bindings (by default `pid` and `hostname`), any fields from a merging
object, and the message under `msg`. Pino itself does no formatting, shipping or
rotation in the application's thread: those jobs belong to transports (modules
run on a worker thread) or to separate processes reading the output, and upstream
recommends doing any log transformation or transmission there.

- **npm package:** `pino`. Licence: MIT. Upstream home: getpino.io (the docs) and
  the pinojs/pino repository on GitHub. Types ship in the package from the 7
  line, so `@types/pino` is not needed (see Major lines).
- The page also covers these packages from the same organisation, each needed
  only for the use named:
  - `pino-pretty`: needed only to turn NDJSON into human-readable output in
    development, as a transport target or a CLI pipe.
  - `pino-http`: needed only for HTTP request logging in Express, Node's core
    `http`, and other frameworks that take its middleware; it gives each request
    a child logger at `req.log`.
  - `pino-test`: needed only to assert on log output in tests.
- `sonic-boom` (the fast file-descriptor writer behind `pino.destination`) and
  `thread-stream` (the worker-thread stream behind transports) are pino's own
  dependencies, named here because their options and behaviour surface through
  pino's API; a project does not install them itself.

## Install, setup and configuration
- `npm install pino`; `npm install --save-dev pino-pretty` for development
  output (upstream recommends against using `pino-pretty` in production and
  recommends installing it as a dev dependency); `npm install pino-http` for
  request logging.
- `pino([options], [destination])` returns a logger. With no destination it
  writes to standard output through `pino.destination(1)`, a sonic-boom stream.
  Upstream says the default configuration usually gives the best performance for
  logging to stdout. When something (a process manager, say) has monkey-patched
  `process.stdout.write`, pino writes to `process.stdout` instead.
- Options and their defaults:
  - `level`: `'info'`. The minimum level logged; one of `fatal`, `error`,
    `warn`, `info`, `debug`, `trace` or `silent`. Values are `trace` 10,
    `debug` 20, `info` 30, `warn` 40, `error` 50, `fatal` 60, `silent`
    Infinity. `customLevels` adds levels; `useOnlyCustomLevels` replaces them.
  - `name`: unset. When set, every line gains a `name` field.
  - `base`: `{ pid, hostname }`. Set it to `undefined` to drop both fields.
  - `timestamp`: `true`, which writes epoch milliseconds as `"time"`. A
    function returns a partial JSON string; `pino.stdTimeFunctions` offers
    `epochTime` (the default), `unixTime`, `nullTime`, `isoTime` (ISO 8601 in
    UTC) and `isoTimeNano`. Upstream cautions that formatting time in-process
    significantly affects logging performance.
  - `messageKey`: `'msg'`; `errorKey`: `'err'`; `nestedKey`: `null`. Setting
    `nestedKey` puts every logged object under that key, so its properties
    cannot collide with `level`, `time`, `pid` and the other pino fields.
  - `serializers`: `{ err: pino.stdSerializers.err }`. A serializer runs on a
    top-level property whose key matches exactly; the `err` serializer also
    runs when the logged value itself is an `Error`. Serializers must return a
    JSON-able value and must never throw.
  - `redact`: unset. An array of paths, or `{ paths, censor, remove }`.
    `censor` defaults to `'[Redacted]'` and may be a synchronous function
    `(value, path) => replacement`; `remove: true` drops the key as well as the
    value. See Security defaults.
  - `formatters`: `level(label, number)` reshapes the level field (default
    `{ level: number }`), `bindings(bindings)` reshapes the bindings once at
    creation, and `log(object)` reshapes each logged object.
  - `mixin`: unset. A function called on every active log call whose returned
    object is merged into the line.
  - `hooks`: `logMethod(args, method, level)` rewrites a call's arguments and
    must call `method.apply(this, args)`; `streamWrite(s)` rewrites the
    stringified line before it is written. Hooks must be synchronous.
  - `depthLimit` 5 and `edgeLimit` 100 apply only in the fallback serializer,
    which pino uses after `JSON.stringify` throws; they are not general limits
    on output size.
  - `msgPrefix` (unset) prefixes every message of the logger and its
    children; `enabled` (`true`) set to `false` disables logging; `crlf`
    (`false`) ends lines with `\r\n`.
  - `transport`: shorthand for `pino.transport()` (below). When it is set, a
    separate `destination` argument is an error.
- **Destinations.** `pino.destination(opts)` takes a path or file descriptor, or
  an object with `dest`, `sync` (`false`, asynchronous, is the default),
  `minLength` (bytes buffered before a write), `append` (default `true`) and
  `mkdir` (default `false`). An ordinary Node writable stream also works, but
  upstream strongly recommends `pino.destination` for throughput. A string that
  is an integer (`'1'`) is coerced to a file descriptor.
- **Transports.** `pino.transport({ target, options })` starts a worker thread
  running the target module (an installed package name or an absolute path) and
  returns a stream to pass to `pino()`. `targets: [...]` fans out to several
  destinations, each with its own `level` (default `info`); `pipeline: [...]`
  chains `Transform` streams before a final destination; `dedupe: true` sends a
  line only to the target with the highest matching level. `options` cross the
  thread boundary by structured clone, so they cannot hold functions.
  `worker.autoEnd: false` turns off the automatic flush on exit, leaving
  `transport.end()` to the caller. Transports run asynchronously unless
  `sync: true` is set in the transport options.
- **Level filtering with transports.** With a single `target` or `pipeline`,
  only `logger.level` filters, and a top-level `level` in the transport options
  is not used. With `targets`, each target filters on its own `level` in the
  worker, but the logger's level still gates what leaves the main thread, so it
  must be at or below the lowest target level.
- Built-in targets: `pino/file` (writes to `destination`, default `1`, that
  is stdout; it appends unless `append: false` and creates directories only
  with `mkdir: true`) and `pino-pretty` once installed.

## Core API / usage shape
```js
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  redact: ['req.headers.authorization', 'req.headers.cookie', '*.password'],
});

logger.info('server started');                       // message only
logger.info({ orderId, items: 3 }, 'order accepted'); // merging object + message
logger.error({ err }, 'payment failed');              // error under `err`
logger.warn('retry %d of %d', attempt, max);          // printf-style

const reqLog = logger.child({ requestId });           // bindings on every line
reqLog.debug('cache miss');
```
- Every level method has the signature `([mergingObject], [message],
  [...interpolationValues])`. Each enumerable key of the merging object is copied
  to the top level of the line. The message supports `%s`, `%d`, `%o`, `%O` and
  `%j`; arguments past the placeholders are not concatenated.
- An `Error` passed first is wrapped as `{ err: error }`; when no message is
  given and the object is an `Error` or has an `err`, the error's message
  becomes `msg`.
- `logger.child(bindings, [options])` returns a logger that writes to the same
  stream and adds the bindings to every line. It inherits the parent's level at
  creation time; `options.level`, `options.msgPrefix`, `options.redact` (an
  empty array clears the inherited paths) and `options.serializers` override the
  parent. Serializers run on child bindings once, when the child is created.
- `logger.level` is a getter and setter; `logger.isLevelEnabled(level)` guards
  expensive argument building; `logger.bindings()` and
  `logger.setBindings(bindings)` read and add bindings; the `level-change`
  event reports level changes.
- `logger.flush([cb])` flushes buffered output of an asynchronous destination,
  and the callback says when it is done. `logger.fatal()` always flushes the
  destination synchronously, because fatal lines are meant to be the last before
  the process stops.
- `pino.multistream(streams, opts)` writes to several streams on the main
  thread, each with its own minimum level; the logger's own `level` must be the
  lowest of them.
- `pino.stdSerializers` (from `pino-std-serializers`: `err`, `errWithCause`,
  `req`, `res` and wrappers to extend them) and `pino.stdTimeFunctions` are
  statics usable as options. The default `err` serializer writes `type`,
  `message`, `stack` and any other enumerable property of the error; it appends
  an `error.cause`'s message and stack to the top-level ones and drops the
  cause's other properties. `errWithCause` keeps the cause as a nested object.
- `pino-http`: `require('pino-http')(opts)` returns a middleware that logs a
  "request completed" or "request errored" line per request (`autoLogging`,
  default `true`, with an `ignore(req, res)` filter), puts a child logger on
  `req.log`, and takes every pino option plus `logger` (a parent pino
  instance), `genReqId(req, res)`, `customLogLevel(req, res, err)`,
  `customProps` and message and object overrides.

## Idioms & best practices
- **One configured root logger, children for context.** Create the logger once
  (level, redaction, serializers, base fields) and derive a child per module,
  request or job. Upstream's benchmarks show child creation and child logging
  cost little, and the shared root keeps redaction and serializers consistent.
- **Configure `redact` before logging request or response objects.** A merging
  object is serialized whole, and `pino-http`'s default request serializer
  includes the request headers, so authorization headers and cookies reach the
  log unless their paths are redacted. Name explicit paths: upstream measures
  wildcard redaction as markedly more expensive than listed keys.
- **Log structured fields, not formatted strings.** Put data in the merging
  object and keep `msg` a stable phrase, so log queries match on fields.
- **Keep untrusted objects under a key of your own.** Upstream warns not to pass
  an externally supplied object as the merging object, a child's bindings or
  `setBindings`: its top-level keys land at the root of the line and can collide
  with `level`, `time`, `msg` or security fields. Log `{ untrusted: obj }`, and
  only when it is needed.
- **Keep pretty-printing in development.** Upstream recommends against
  `pino-pretty` in production; production output stays NDJSON on stdout, and
  prettifying happens on the reading side (`node app.js | pino-pretty`) or with a
  development-only transport.
- **Do transformation and shipping off the main thread.** Upstream's advice is
  to transform or transmit logs in a transport (a worker thread) or a separate
  process, never in the application's event loop.
- **Rotate with an external tool.** Upstream recommends `logrotate`.
  `copytruncate` can lose a few lines; the alternative is
  `destination.reopen()` from a `SIGHUP` or `SIGUSR2` handler signalled by the
  rotation tool.
- **Keep the numeric level when using several targets.** Per-target routing
  reads the numeric `level`, so a `formatters.level` that renames it or turns it
  into a label breaks multi-target filtering; upstream says pino then throws or
  warns. Turn levels into labels in a transport, after routing.

## General pitfalls
- **A second plain argument disappears.** `logger.info('a', 'b')` logs only
  `"a"`: arguments with no placeholder are not concatenated (since the 6 line).
  Use a placeholder or a merging object.
- **A `msg` in the merging object is overwritten** by the message argument.
  Upstream's workaround is a `logMethod` hook that copies it to another key.
- **Duplicate keys reach the output.** Pino builds strings, not objects, so a
  child binding that repeats a parent binding or a pino field appears twice in
  the line. `JSON.parse` keeps the last value, but other parsers may not.
- **Lines can be lost at exit with an asynchronous destination or a transport.**
  Pino registers exit handlers that flush (see Operational behaviour), but a
  transport boots asynchronously, so a `process.exit()` before its `ready`
  event drops what was logged. Upstream also warns that asynchronous logging on
  AWS Lambda tends to delay or lose lines, and recommends `sync: true` there.
- **`logger.flush()` does not flush `pino-pretty`.** The pretty transport's
  stream exposes no flush primitive to the worker, so a flush only guarantees
  the main-thread buffer and the shared buffer were drained.
- **A transport `'error'` is fatal.** Upstream says an error event from a
  transport is not recoverable and the process must be terminated.
- **Transport options must survive structured clone.** A function option (for
  example `pino-pretty`'s `messageFormat` as a function) is lost; wrap the
  transport in a small module of your own that sets it.
- **Redaction paths must never come from user input.** Paths are compiled at
  initialization and are case sensitive; a path with a hyphen needs brackets
  (`headers["x-api-key"]`).
- **Bundling needs extra files.** Because transports run in worker threads, a
  bundler must emit the worker files and every transport as separate files and
  set `globalThis.__bundlerPathsOverrides`; plugins exist for webpack, esbuild
  and Bun.
- **The browser build lacks the Node-only statics.** `pino.destination`,
  `pino.transport` and `pino.multistream` are absent (calling one throws a
  `TypeError`), and `flush` is a no-op whose callback never runs. Guard the
  call, not the environment, in shared code.
- `pino-pretty`'s CLI can fail with "stdout is not a tty" in mingw64-based
  shells such as Git for Windows Bash.

## Testing
- `pino-test` provides `sink()` (a stream to pass as the destination) and
  `once(stream, expected)` / `consecutive(stream, expectedList)` that compare
  the parsed lines against expected fields, with an optional custom assert
  function.
- Without it, pass any writable stream as the destination and parse its lines;
  setting `destination[Symbol.for('pino.metadata')] = true` exposes
  `lastLevel`, `lastMsg`, `lastObj` and `lastTime` on the destination after
  each write.
- Upstream's `pino-pretty` README says the only supported way to use it under
  Jest is as a synchronous stream, `pino(pretty({ sync: true }))`, because Jest
  allows no asynchronous work after a test ends.
- Assert redaction directly: log an object carrying the secret paths and
  check the censor value appears in their place.

## Security defaults
- Nothing is redacted by default, and the default `err` serializer writes the
  error's message and stack. Whatever the merging object, child bindings or an
  HTTP serializer carries reaches the log as written.
- `pino-http`'s default request serializer logs the request headers; request
  bodies are not logged by default, and upstream notes that enabling them
  risks persisting passwords and personal data unless redacted.
- `base` writes `pid` and `hostname` into every line; set `base: undefined`
  where the host name should not leave the machine.
- The `hooks.streamWrite` hook can scrub the final string, but upstream's
  redaction option is the supported mechanism for known paths.

## Operational behaviour
- **Writes.** The default destination writes asynchronously. Asynchronous
  logging with a buffer (`minLength`)
  has no one-to-one relation between log calls and writes, and a system
  failure can lose the last buffered lines. `sync: true` writes each line with a
  blocking call.
- **Exit.** For an asynchronous destination on the main thread, pino registers
  the stream with an exit hook: on `beforeExit` it flushes and ends the stream,
  and on `exit`, where no event loop remains, it flushes synchronously.
  `pino.transport()` likewise listens on `beforeExit` and `exit` to flush the
  worker, and the worker is terminated when its stream is garbage collected.
  After `process.exit()` the main event loop stops, so output written later
  through `console.log` or `process.stdout` does not appear.
- **Broken pipe.** On `EPIPE` the default destination stops writing silently
  instead of throwing.
- **Rotation.** `pino.destination` (sonic-boom) can `reopen()` its file after
  a rotation tool moves it.
- **Cost.** Serialization dominates; redaction without wildcards adds about two
  percent to `JSON.stringify`, wildcards add more, and in-process time
  formatting and pretty-printing are the expensive options.
- **Support policy.** Upstream supports each major line for at least six months
  and gives it security fixes for six more months after the next major ships. A
  pino major line supports every Node.js line that was current or in LTS when
  it shipped and never drops one within the line. Upstream may ship a breaking
  security change as a minor release, noted in the release notes.

## Interop
- Web frameworks: Fastify bundles pino (`logger: true`, or a pino options
  object, with `request.log`); Express, Node's core `http` and others use
  `pino-http`; Nest uses `nestjs-pino`.
- OpenTelemetry: `@opentelemetry/instrumentation-pino` adds `trace_id`,
  `span_id` and `trace_flags` to lines logged inside an active span (log
  correlation) and can send records to the OpenTelemetry Logs SDK (log
  sending, from pino's 7 line). `pino-opentelemetry-transport` does the
  sending from a transport worker instead, with its own SDK instance. The SDK
  side is on [opentelemetry-sdk-node](opentelemetry-sdk-node.md).
- Log shippers: a long list of transports (Elasticsearch, syslog, Sentry,
  cloud services, `pino-roll` for rotation) is maintained in upstream's
  transports document; check a transport supports the 7-line worker model
  before adopting it.
- Unix tools: NDJSON lines filter with `grep '"level":50'` or
  `jq 'select(.level >= 50)'`.

## Major lines

### 7 line
- Transports moved into worker threads (`pino.transport()` and the `transport`
  option, with `targets` and `pipeline`); separate-process transports are now
  called legacy transports. `pino.multistream()` was absorbed from
  `pino-multi-stream`.
- TypeScript types ship in the package; remove `@types/pino`.
- `prettyPrint` was deprecated in favour of the `pino-pretty` transport, and
  extreme mode was removed.
- The `err` serializer now also applies to an `Error` passed as the first
  argument.
- Asynchronous destinations and transports are flushed automatically on exit.

### 8 line
- Asynchronous logging became the default, and the deprecated `prettyPrint`
  option and `pino.final()` were removed. Code that set `prettyPrint: true`
  needs a `pino-pretty` transport; code that used `pino.final()` relies on the
  automatic exit flush.

### 9 line
- Dropped Node.js 14, 16 and 19.

### 10 line
- Upstream states the only breaking change is dropping Node.js 18.

## Upstream docs
- Docs: https://getpino.io/ (source in https://github.com/pinojs/pino/tree/main/docs)
- API: https://github.com/pinojs/pino/blob/main/docs/api.md
- Transports: https://github.com/pinojs/pino/blob/main/docs/transports.md
- Redaction: https://github.com/pinojs/pino/blob/main/docs/redaction.md
- Asynchronous logging: https://github.com/pinojs/pino/blob/main/docs/asynchronous.md
- Long-term support: https://github.com/pinojs/pino/blob/main/docs/lts.md
- Releases: https://github.com/pinojs/pino/releases
- pino-pretty: https://github.com/pinojs/pino-pretty
- pino-http: https://github.com/pinojs/pino-http
- pino-test: https://github.com/pinojs/pino-test
