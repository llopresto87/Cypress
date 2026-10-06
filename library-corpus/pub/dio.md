# dio — pub

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). A plant can adopt this page instead of scouting
> dio's surface; it still runs `ingest-library` against its own `pubspec.lock`
> for the exact version and its changelog.

## What it is
`dio` is an HTTP client for Dart and Flutter. On top of the platform transport
it adds interceptors, global configuration, request cancellation, `FormData`
and multipart upload, file download, progress callbacks, timeouts and
pluggable adapters. On native platforms it uses `dart:io` `HttpClient` through
`IOHttpClientAdapter`; on the web it uses the browser through
`BrowserHttpClientAdapter` (shipped in the separate `dio_web_adapter`
package). It is maintained by the CFUG community under the MIT licence.

Upstream home: https://pub.dev/packages/dio and
https://github.com/cfug/dio . The README and the CHANGELOG warn that breaking
changes may land in minor as well as major releases, so read the changelog
before any upgrade.

## Install, setup and configuration
- Add `dio` to `dependencies` in `pubspec.yaml`. Import `package:dio/dio.dart`;
  platform classes come from `package:dio/io.dart` (native) and
  `package:dio/browser.dart` (web).
- `Dio(BaseOptions(...))` creates an instance with defaults; `dio.options`
  changes them later; `dio.clone()` copies an instance. Per-request `Options`
  are merged over the `BaseOptions`.
- Defaults that matter:
  - `connectTimeout`, `sendTimeout`, `receiveTimeout` and `transformTimeout`:
    null, which means no limit (`Duration.zero` also means no limit).
  - `responseType`: JSON, parsed when the response content type is JSON.
  - `followRedirects` true with `maxRedirects` 5; `persistentConnection` true.
  - `receiveDataWhenStatusError` true, so an error response keeps its body.
  - `validateStatus` decides which status codes count as success (by default
    the 2xx range).
  - `listFormat` `ListFormat.multi` (`a=1&a=2`).
  - Request bodies are serialized as JSON by default; a default interceptor
    (`ImplyContentTypeInterceptor`) sets the content type and can be removed.
  - The default transformer is `FusedTransformer`; JSON bodies above a size
    threshold (50 KB) are decoded in a background isolate on native. The README
    still names `BackgroundTransformer`; the source and the changelog win.
- Proxy and certificates on native: `IOHttpClientAdapter(createHttpClient: ...)`
  returns a configured `HttpClient` (`findProxy`, `SecurityContext`). Neither
  applies on web.

## Core API / usage shape
- Requests: `get`, `post`, `put`, `patch`, `delete`, `head`, `download`, the
  general `request<T>(path, data:, queryParameters:, options:, cancelToken:,
  onSendProgress:, onReceiveProgress:)` and `fetch(RequestOptions)`. `data` is
  allowed on every method.
- `Response<T>`: `data`, `statusCode`, `statusMessage`, `headers`,
  `requestOptions`, `redirects` and `extra`.
- Forms: `FormData.fromMap({...})` with `MultipartFile.fromFile(...)`; for
  `x-www-form-urlencoded` set `contentType: Headers.formUrlEncodedContentType`.
  Build a new `FormData` for every request, or `clone()` it.
- Progress: `onSendProgress` and `onReceiveProgress`. Sending a stream with send
  progress needs a `content-length` header.
- Cancellation: a `CancelToken` passed to one or many requests;
  `token.cancel('reason')`; test an error with `CancelToken.isCancel(e)`.
- Interceptors: add an `InterceptorsWrapper(onRequest:, onResponse:, onError:)`
  or a subclass of `Interceptor` to `dio.interceptors`. Each callback receives a
  handler and must end with `handler.next(...)`, `handler.resolve(response)` or
  `handler.reject(exception)`. `QueuedInterceptor` lets requests enter one at a
  time, with separate queues for `onRequest`, `onResponse` and `onError`.
- Errors: a failed request throws `DioException` with `type`
  (`connectionTimeout`, `sendTimeout`, `receiveTimeout`, `badCertificate`,
  `badResponse`, `cancel`, `connectionError`, `transformTimeout`, `unknown`),
  `response` (null when no HTTP answer arrived), `requestOptions`, `error` and
  `message`.
- Extension points: implement `HttpClientAdapter` for a custom transport, a
  `Transformer` for custom body handling, or build on `DioMixin`.

## Idioms & best practices
- Share one configured `Dio` instance: the README recommends a singleton so
  headers, base URL and timeouts are managed in one place. Observed in
  practice: projects that built one `Dio` per repository had to repeat every new
  default in each one.
- Always set explicit timeouts.
- Cancel in-flight requests with a `CancelToken` when the screen or owner that
  started them is disposed.
- Catch `on DioException catch (e)` and branch first on `e.response == null`
  (transport failure: DNS, no network, TLS abort, CORS block) versus
  `e.response!.statusCode` (the server answered). Observed in practice: a
  blanket catch that mapped every failure to "wrong credentials" hid a TLS
  abort.
- Token refresh, observed in practice in bearer-token apps with concurrent
  requests (the README does not describe refresh): do the refresh in a
  `QueuedInterceptor` so concurrent 401 responses trigger one refresh while the
  rest wait; send the refresh call and the single retry through a separate
  `Dio` that has no auth interceptor; exempt the auth endpoints from the
  interceptor by path. The reasoning in practice is that this avoids a refresh loop
  and a request waiting on its own queue; upstream does not use the word
  deadlock, but its changelog records queue stalls from callbacks that never
  finish.
- Add `LogInterceptor` last, and never with credentials in play.
- Keep navigation and `BuildContext` out of interceptors: a 401 can arrive
  before any widget is mounted. Signal an auth state holder (a bloc or a
  stream) instead (observed in practice; the docs are silent).

## General pitfalls
- A null or zero timeout means no limit, so a request on a dead network can
  wait forever.
- `receiveTimeout` is not a cap on total duration: it bounds the wait for the
  first bytes and the gap between received chunks. `transformTimeout` is best
  effort on web.
- An interceptor callback that never calls its handler leaves the request
  hanging. Normal interceptors run concurrently; only `QueuedInterceptor`
  serializes, and a queued callback that throws or never finishes can stall
  the queue (several such stalls were fixed during the 5 line, so stay on a
  recent release of it).
- Reusing a `FormData` or `MultipartFile` across requests throws ("Cannot
  finalize").
- A class that `implements Interceptor` instead of extending it broke on some
  releases of the 5 line; extend `Interceptor` or `QueuedInterceptor`.
- On web, redirect options do not apply (the browser follows redirects), a
  proxy cannot be set, a download is buffered in memory and the second argument
  is only a suggested file name, and non-simple requests trigger a CORS
  preflight the server must answer.
- `DioError` is deprecated in favour of `DioException`, and
  `onHttpClientCreate` in favour of `createHttpClient`.

## Testing
- Stub at the transport: implement `HttpClientAdapter` (it must be implemented,
  not extended) and assign it to `dio.httpClientAdapter`, so tests run without
  a network.
- Stub inside an interceptor: `handler.resolve(Response(requestOptions:
  options, data: ...))` answers a request without sending it; the README shows
  this.
- The fetched upstream sources give no guidance on mocking libraries, and no
  network-layer tests in practice were available to learn from; that part is a
  gap.

## Security defaults
- TLS verification is on by default.
- `badCertificateCallback` on the `dart:io` `HttpClient` runs only for a
  certificate the platform already rejected. An unconditional `=> true`
  without a further check disables verification.
- Pinning recipes from the README: (a) pin the leaf by building the client with
  `SecurityContext(withTrustedRoots: false)` and accepting in
  `badCertificateCallback`, then compare the SHA-256 fingerprint in
  `IOHttpClientAdapter.validateCertificate`, returning false when `cert` is
  null; (b) pin a CA by comparing PEM in the callback, or by loading it with
  `SecurityContext.setTrustedCertificates` (PEM or PKCS12; a PKCS12 password
  puts a secret in the code). `validateCertificate` sees the leaf, runs only
  after the chain is accepted, and allows the certificate when it is absent.
- The README notes CA pinning suits certificates from a third-party CA. Pinning
  a public key or a CA rather than a rotating leaf is observed practice, not an
  upstream rule.
- Pinning does nothing on web, where the browser owns TLS.
- Observed in practice: `HttpOverrides.global` installs a process-wide
  `HttpClient` factory and so affects every `dart:io` client in the process,
  not only dio (standard `dart:io` behaviour; the dio docs do not mention it).
  Gate any trust of a self-signed development certificate on the build mode, or
  trust the development CA explicitly.
- `LogInterceptor` prints headers and bodies. Its default printer is active only
  in debug mode (assertions on), but `debugPrint`, often passed in Flutter, is
  not debug-only. Keep it out of release builds and away from `Authorization`
  headers and credential bodies.

## Operational behaviour
- Connections are persistent by default.
- Body decoding is done by the transformer; large JSON is decoded off the main
  isolate on native.
- Recent releases of the 5 line propagate backpressure from a response stream
  to the socket; older ones could buffer a large stream into memory.
- HTTP/2 comes from the separate `dio_http2_adapter` package, and cookie
  management from a separate plugin package.

## Interop
- Flutter web needs `dio_web_adapter`, resolved automatically as a dependency.
- Commonly used as the data provider under a repository layer that a state
  manager such as `library-corpus/pub/flutter_bloc` consumes.
- Tokens for an auth interceptor usually come from
  `library-corpus/pub/flutter_secure_storage`.
- Browser CORS and TLS rules for a Flutter web client:
  `library-corpus/language/flutter`.

## Major lines
### dio 3
Added Flutter web support and moved the cookie manager to its own package.
Redirect options stopped applying on web.

### dio 4
Null safety; the handler-based interceptor API; `fetch`; `ListFormat.multi` as
default. `QueuedInterceptor` arrived during this line.

### dio 5
- Timeouts are `Duration` values (breaking from 4).
- `HttpClientAdapter` must be implemented, not extended; `validateCertificate`
  added; native and web classes split into `package:dio/io.dart` and
  `package:dio/browser.dart`; content-type constants lost their default
  charset.
- During the line: `DioError` deprecated for `DioException`; `LogInterceptor`
  debug-only by default; `FusedTransformer` became the default transformer;
  the web adapter moved to `dio_web_adapter`; `transformTimeout` and the HTTP
  `QUERY` methods were added; `DefaultHttpClientAdapter` and
  `onHttpClientCreate` were deprecated for removal at the next major.

## Upstream docs
- https://pub.dev/packages/dio
- https://github.com/cfug/dio
- https://github.com/cfug/dio/blob/main/dio/README.md
- https://github.com/cfug/dio/blob/main/dio/CHANGELOG.md
