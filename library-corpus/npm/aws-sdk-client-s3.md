# aws-sdk-client-s3 — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The Amazon S3 client of the AWS SDK for JavaScript v3: a modular,
code-generated client for the S3 API that runs in Node.js, browsers and
React Native. It talks to Amazon S3 and, through a custom endpoint, to any
S3-compatible object store (a self-hosted server such as
[MinIO](../container/minio.md), or a vendor's S3-compatible service). Licence:
Apache-2.0. All v3 packages are published from one repository.

- `@aws-sdk/client-s3`: the S3 client (`S3Client`, one `...Command` class per
  operation, and the aggregated `S3` class); needed for any S3 access.
- `@aws-sdk/s3-request-presigner`: `getSignedUrl`, which turns a client and a
  command into a time-limited presigned URL; needed only when a browser or a
  third party must read or write an object without credentials.
- `@aws-sdk/lib-storage`: `Upload`, a managed multipart upload for large bodies
  or streams of unknown length; needed only for uploads that a single
  `PutObject` cannot carry.

Upstream home: the developer guide at
https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/, the API
reference at https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/client/s3/,
and the source at https://github.com/aws/aws-sdk-js-v3 (the client under
`clients/client-s3`, the configuration guide in `supplemental-docs/CLIENTS.md`,
the v2 migration guide in `UPGRADING.md`).

## Install, setup and configuration
- `npm install @aws-sdk/client-s3`, plus the presigner or `lib-storage` only
  when used. Each v3 release states its minimum Node.js version in the
  repository README's support-policy table; the floor rises as Node.js LTS
  lines leave support, so a project on an old runtime cannot take the newest
  client.
- Constructor settings that matter in practice:
  - `region`: a string or an async function returning one. Required for AWS;
    an S3-compatible store accepts any value its server expects (often any
    string), but the SDK still signs with it.
  - `credentials`: when omitted, Node.js uses the default credential provider
    chain (environment, shared files, container and instance roles); browsers
    have no default chain. A literal `{ accessKeyId, secretAccessKey }` object
    is upstream's testing-only form.
  - `endpoint`: overrides the rule-based endpoint resolution entirely; a URL
    string, or an `Endpoint`/`EndpointV2` object or async function.
  - `forcePathStyle`: default `false`. When `false` the client addresses a
    bucket as a virtual host (`<bucket>.<host>/<key>`); `true` puts the bucket
    in the path (`<host>/<bucket>/<key>`). v2's `s3ForcePathStyle` was renamed
    to this.
  - `requestHandler`: in Node.js a `NodeHttpHandler` over `node:http`/`https`
    (used even when global `fetch` exists), keep-alive on, 50 sockets per
    client by default; `maxSockets`, `requestTimeout` and `connectionTimeout`
    are set here. Browsers use a `fetch`-based handler.
  - `maxAttempts` / `retryMode` / `retryStrategy`: exponential backoff on
    transient errors; a `retryStrategy` overrides the other two.
  - S3-specific: `requestChecksumCalculation` and `responseChecksumValidation`
    (`WHEN_SUPPORTED` by default, or `WHEN_REQUIRED`; also settable as
    `AWS_REQUEST_CHECKSUM_CALCULATION` / `AWS_RESPONSE_CHECKSUM_VALIDATION` or
    the shared config file), `followRegionRedirects` (retry a 301 in the right
    region; a last resort with added latency), `bucketEndpoint` (the endpoint
    is a bucket URL and `Bucket` is ignored), `expectContinueHeader` (sends
    `Expect: 100-continue` above 2 MB by default, and for streams of unknown
    size).

## Core API / usage shape
- **Client plus command.** Construct one `S3Client`, build a command
  (`new GetObjectCommand({ Bucket, Key })`, `PutObjectCommand`,
  `DeleteObjectCommand`, `HeadObjectCommand`, `ListObjectsV2Command`, …) and
  `await client.send(command)`. The aggregated `S3` class exposes the same
  operations as methods (`s3.getObject(...)`); upstream recommends the bare
  client plus commands when bundling, because it tree-shakes.
- **Streaming output.** `GetObject`'s `Body` is a runtime-specific stream (a
  Node.js `Readable` on Node.js, the browser's own stream type in browsers)
  carrying SDK mixin methods: `transformToString(encoding?)`,
  `transformToByteArray()` and `transformToWebStream()`. Each reads the stream,
  so it can be called once; a second call throws because a stream cannot be
  rewound. Piping the body to a file or to another upload also consumes it.
- **Errors.** A failed call rejects with a service exception whose `name`
  identifies the service error and whose `$metadata` carries
  `httpStatusCode` and the request ids (`requestId`, `extendedRequestId`,
  `cfId`).
- **Paginators.** Each paginated operation has a `paginate<Operation>`
  function (`paginateListObjectsV2({ client }, input)` for listing), an async
  iterator over pages used with `for await`.
- **Presigned URLs** (`@aws-sdk/s3-request-presigner`):
  `await getSignedUrl(client, new GetObjectCommand(...), { expiresIn })`;
  `expiresIn` defaults to 900 seconds. Works for `PutObjectCommand` too.
  `x-amz-*` headers are hoisted into the query string unless listed in
  `unhoistableHeaders`; other headers are signed only when listed in
  `signableHeaders`.
- **Managed upload** (`@aws-sdk/lib-storage`):
  `new Upload({ client, params: { Bucket, Key, Body } })` with `queueSize`
  (default 4 concurrent parts), `partSize` (at least 5 MB) and
  `leavePartsOnError` (default `false`: a failed upload is aborted). Await
  `upload.done()`; progress arrives as `httpUploadProgress` events.

## Idioms & best practices
- **One client per process (or per target), reused.** The client owns the
  connection pool; constructing one per request throws the pool away each
  time.
- **Always consume or destroy a `Body`.** Read it to completion with a
  transform helper or a pipe, or call `.destroy()` on a Node.js stream you do
  not need. When only metadata is needed, use `HeadObject` instead of
  `GetObject`.
- **Keep the S3-compatible settings together.** A self-hosted store needs
  `endpoint` and `forcePathStyle: true` (unless the server is configured for
  virtual-host addressing and DNS resolves bucket subdomains), with
  credentials from the store's own user or access key. Keep all three in one
  configuration object so a store change touches one place.
- **Install only the clients you use.** v3 is modular; the v2 monolith
  (`aws-sdk`) pulls every service in.
- **Bump the `@aws-sdk/*` packages together.** They come from one repository
  and build on shared runtime packages, so a presigner or `lib-storage` far
  from the client's version can pull a second copy of those into the install.
  This is advice drawn from the repository's layout; upstream states no
  compatibility rule between package versions.
- **Serve public reads without the SDK where possible.** A presigned URL or a
  public read path keeps large downloads off the application process.

## General pitfalls
- **`Body` is not a `Buffer`.** Code ported from v2 that treats
  `GetObject`'s result as bytes breaks: v2 buffered the body, v3 returns a
  stream (upstream's migration guide states this).
- **An unconsumed body holds its socket.** With keep-alive on, a body that is
  never read keeps the connection checked out; enough of them exhaust the
  pool (50 sockets per client by default), and requests then queue. The SDK
  logs `socket usage at capacity=… additional requests are enqueued` when
  many requests wait.
- **Default checksums and S3-compatible stores.** From v3.729.0 the S3 client
  adds a CRC-based checksum to uploads and validates checksums on downloads
  by default (`WHEN_SUPPORTED`). AWS states that its SDKs may enable such
  defaults before third-party S3-compatible services support them; a store
  that does not may reject requests (upstream names `DeleteObjects`, which
  used to send `Content-MD5`, as the operation it knows to be affected).
  Setting both options to `WHEN_REQUIRED` restores opt-in behaviour, and
  upstream's MD5-fallback guide shows a middleware that sends `Content-MD5`
  for `DeleteObjects` only. Upstream does not recommend turning integrity
  checks off against AWS itself.
- **Virtual-host addressing against a self-hosted store.** With the default
  `forcePathStyle: false` the client asks for `<bucket>.<host>`, which a
  self-hosted server usually does not resolve or answer, so every call fails
  with a DNS or 404-style error (observed in practice against a self-hosted
  store; the MinIO docs state its server accepts only path-style requests
  unless configured with a domain).
- **`useGlobalEndpoint` is not cross-region access**; it only toggles the
  `us-east-1` hostname form. Use `followRegionRedirects` or the right region.
- **Presigned URLs carry the signer's rights until they expire.** Anyone
  holding one can use it; keep `expiresIn` short and presign only the single
  operation needed.
- **`partSize` below 5 MB is rejected** by `lib-storage`'s `Upload`, and a
  failed multipart upload with `leavePartsOnError: true` leaves billable
  parts behind until something aborts them.

## Testing
- Integration tests run best against a real S3-compatible server in a
  container (for example [MinIO](../container/minio.md)), configured exactly as
  production configures the client (`endpoint`, `forcePathStyle`, region,
  checksum settings), so path-style and checksum mismatches surface in the
  suite.
- A stream body can be read once: a test that reads it to assert content and
  then passes it on consumes it first. Read once into a variable.
- Unit tests that replace the network inject a stub `requestHandler`, or put
  the client behind the project's own storage port and fake the port; the
  client's middleware stack is also extensible for interception.

## Security defaults
- Credentials come from the default provider chain in Node.js; nothing is
  hard-coded unless code passes a literal, which upstream reserves for tests.
  Keep access keys out of source and logs.
- Requests are signed with Signature Version 4; a custom `http://` endpoint
  sends signed but unencrypted traffic, so object contents cross the network
  in clear text. Use HTTPS outside a trusted private network.
- Presigned URLs are bearer tokens for their lifetime (see pitfalls).
- Integrity checks are on by default (`WHEN_SUPPORTED`); switching them to
  `WHEN_REQUIRED` for a compatible store removes that protection for every
  operation that does not require it.

## Operational behaviour
- Connections are pooled per client with keep-alive; throughput is bounded by
  `maxSockets`, and unconsumed bodies count against it.
- Transient errors are retried with exponential backoff up to `maxAttempts`;
  other errors reject at once.
- Timeouts are off unless set: `connectionTimeout`, `requestTimeout` and
  `socketTimeout` on the Node.js handler all default to 0 (disabled). An
  exceeded `requestTimeout` only logs a warning unless `throwOnRequestTimeout`
  is `true` (an option from v3.910.0), which makes it throw a `TimeoutError`.

## Interop
- **S3-compatible servers:** [MinIO](../container/minio.md) needs path-style
  addressing and its own credentials; checksum defaults are the second thing
  to check against any third-party store.
- **Node.js streams:** a `Body` pipes into `fs.createWriteStream` or another
  upload; `transformToWebStream()` hands it to code that expects a web stream.
- **Runtime floor:** the client's minimum Node.js version follows the
  [nodejs](../language/nodejs.md) LTS schedule.

## Major lines
### v2 (`aws-sdk`) and v3 (`@aws-sdk/*`)
- v2 is one package holding every service, with `AWS.S3` methods returning a
  request object (`.promise()`); AWS has ended its support, and it receives no
  updates or releases. v3 is modular (one package per service), command-based,
  middleware-driven and the supported line.
- Moving from v2: `s3ForcePathStyle` became `forcePathStyle`;
  `GetObject` returns a stream instead of a buffered body; presigning moved to
  `@aws-sdk/s3-request-presigner` and managed upload to `@aws-sdk/lib-storage`.
  AWS publishes `aws-sdk-js-codemod` for the mechanical part.

### Within v3
- From v3.729.0, default request checksum calculation and response checksum
  validation for S3 (see pitfalls).
- Minimum Node.js rises over the line: v3.723.0 and later need Node.js 18 or
  newer, v3.968.0 and later Node.js 20 or newer (the README's table lists
  earlier floors).

## Upstream docs
- https://github.com/aws/aws-sdk-js-v3/blob/main/clients/client-s3/README.md
- https://github.com/aws/aws-sdk-js-v3/blob/main/supplemental-docs/CLIENTS.md
  (constructor options, request handler, socket exhaustion, S3 options)
- https://github.com/aws/aws-sdk-js-v3/blob/main/UPGRADING.md (v2 to v3)
- https://github.com/aws/aws-sdk-js-v3#streams and the Node.js support policy
  in the same README
- https://github.com/aws/aws-sdk-js-v3/blob/main/supplemental-docs/MD5_FALLBACK.md
- https://github.com/aws/aws-sdk-js-v3/issues/6810 (S3 default integrity change)
- https://docs.aws.amazon.com/sdkref/latest/guide/feature-dataintegrity.html
- https://github.com/aws/aws-sdk-js-v3/blob/main/packages/s3-request-presigner/README.md
- https://github.com/aws/aws-sdk-js-v3/blob/main/lib/lib-storage/README.md
- https://github.com/aws/aws-sdk-js (v2, end-of-support notice)
