# sharp — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
sharp is a Node-API module for server-side image processing, built on the
libvips image library. Its typical use is converting large images in common
formats into smaller, web-friendly JPEG, PNG, WebP, GIF and AVIF output of
varying dimensions. Beyond resizing it rotates, extracts, composites,
gamma-corrects and reads metadata. It handles colour spaces, embedded ICC
profiles and alpha channels, and resamples with Lanczos by default.

It runs on any JavaScript runtime with Node-API v9 support (Node.js, Deno,
Bun). It processes images in small regions instead of whole decoded frames,
stays non-blocking on libuv's thread pool, and spawns no child processes.
Upstream reports resizing as typically 4x to 5x faster than the quickest
ImageMagick and GraphicsMagick settings.

- **npm package:** `sharp`. Licence: Apache-2.0. Upstream home:
  https://sharp.pixelplumbing.com (docs) and the lovell/sharp repository on
  GitHub.
- The native binaries ship as platform packages named `@img/sharp-<platform>`
  (for example `@img/sharp-linux-x64`, `@img/sharp-linuxmusl-arm64`,
  `@img/sharp-darwin-arm64`), plus `@img/sharp-libvips-<platform>`. sharp
  declares them as optional dependencies, and the package manager installs
  the one matching the machine. A project never imports them directly.
- `@img/sharp-wasm32`: the WebAssembly build. It is needed only on a runtime
  with no prebuilt native binary, installed beside `sharp`.

## Install, setup and configuration
- `npm install sharp` (or `pnpm add`, `yarn add`, `bun add`;
  `deno add npm:sharp`). The package manager **must be allowed to install
  optional dependencies**, because the binary arrives that way. Upstream's
  docs open with this caution.
- Prebuilt binaries cover macOS (x64, ARM64), Linux on glibc and musl for the
  common architectures (x64 needs a CPU with SSE4.2; glibc and musl lower
  bounds are listed on the install page), Windows (x64, ARM64; x86 is
  deprecated) and FreeBSD through WebAssembly. They support JPEG, PNG, Ultra
  HDR, WebP, AVIF, TIFF, GIF and SVG input. No system libvips or compiler is
  needed on those platforms.
- **Cross-platform lockfiles.** A package manager picks the binary for the
  current OS and CPU at install time. A lockfile written on one platform and
  installed on another (a laptop's lockfile built in a Linux container) needs
  the other platform's package too. npm (v10+) offers only limited support,
  through `--os`, `--cpu` and `--libc` flags (`npm install --os=linux
  --libc=musl --cpu=x64 sharp`); upstream warns that npm lockfiles shared
  across platforms can cause installation problems, citing an open npm bug.
  yarn (v3+) and pnpm (v8+) use their `supportedArchitectures` setting.
- **Custom libvips.** A globally installed libvips at or above the version in
  the package's `config.libvips`, found through `pkg-config --modversion
  vips-cpp`, is used instead of the bundled one. Building from source
  (`npm explore sharp -- npm run build`) needs a C++17 compiler,
  `node-addon-api` and `node-gyp`. `SHARP_IGNORE_GLOBAL_LIBVIPS` and
  `SHARP_FORCE_GLOBAL_LIBVIPS` override the detection. A global libvips is
  unsupported on Windows and on macOS under Rosetta.
- **Bundlers.** Keep `sharp` out of the bundle: webpack `externals`, esbuild
  `external`, Vite `build.rollupOptions.external`. Electron packagers must
  unpack `sharp` and `@img` from the ASAR archive. Serverless deployment
  packages must contain the binary for the target architecture, and some
  package managers' symbolic links are not supported there.
- **TypeScript.** Types ship inside the package; `@types/sharp` is
  deprecated. `@types/node` is expected in dev dependencies.
- **Fonts.** Text images and SVG text find fonts through `fontconfig`. On
  Linux a missing configuration fails with "Fontconfig error: Cannot load
  default config file"; `FONTCONFIG_PATH` points to a custom location.
  Embedded SVG fonts are unsupported.
- **Constructor options and their defaults** (the input-side settings):
  - `failOn` (default `'warning'`): how sensitive to invalid pixel data, from
    `'none'` through `'truncated'` and `'error'` to `'warning'`; a higher
    level implies the lower ones. Invalid metadata always aborts. Upstream
    says to keep the default with untrusted input.
  - `limitInputPixels` (default 268402689, which is 0x3FFF × 0x3FFF): refuse
    an input whose width × height exceeds it. A number sets a limit, `true`
    restores the default, and `0` or `false` removes it.
  - `limitInputChannels` (default 5): the same for the channel count.
  - `unlimited` (default `false`): `true` removes the memory-exhaustion safety
    features for JPEG, PNG, SVG and HEIF.
  - `autoOrient` (default `false`): rotate or flip to match the EXIF
    `Orientation` tag.
  - `sequentialRead` (default `true`), `density` (default 72, for SVG and PDF
    rendering), `pages`/`page`/`animated` (multi-page input; one page by
    default), `ignoreIcc`, and `raw`, `create`, `text` and `join` for raw
    pixels, generated images, text rendering and joining an array of inputs.
- **Global settings.** `sharp.cache(options)` sets libvips' operation cache
  (defaults: 50 MB memory, 20 open files, 100 operations; `false` disables
  it). `sharp.concurrency(n)` sets threads per image: the CPU count by default,
  except on glibc Linux without jemalloc or without `MALLOC_ARENA_MAX`, where
  the default is 1 to reduce memory fragmentation. `0` resets it to the CPU count.

## Core API / usage shape
```js
import sharp from 'sharp';

const { data, info } = await sharp(inputBuffer, { limitInputPixels: 40_000_000 })
  .autoOrient()
  .resize({ width: 1200, withoutEnlargement: true })
  .webp({ quality: 80 })
  .toBuffer({ resolveWithObject: true });
```
- `sharp(input?, options?)` takes a Buffer, a TypedArray, a file path, an
  array of inputs, or nothing (then the instance is a writable stream). The
  instance is a `stream.Duplex`, so `readable.pipe(sharp().resize(300)).pipe(writable)`
  works; it emits `info` (output dimensions) and `warning` events.
- Operations chain and are applied when an output method runs: `resize`,
  `extract`, `extend`, `trim`, `rotate`, `autoOrient`, `flip`, `flop`,
  `composite`, `blur`, `sharpen`, `flatten`, `modulate` and others.
- `resize(width?, height?, options)`: `fit` is `cover` (the default, crops),
  `contain` (letterboxes), `fill` (stretches), `inside` or `outside`;
  `position` picks the crop gravity or an `entropy`/`attention` strategy;
  `kernel` defaults to `lanczos3`; `withoutEnlargement` stops upscaling. One
  resize per pipeline: an earlier call is ignored.
- Output format: `jpeg()`, `png()`, `webp()`, `gif()`, `avif()`, `tiff()`,
  `heif()`, `raw()`, or `toFormat(name, options)`. Without one, the output
  keeps the input format (SVG input becomes PNG); `toFile` infers it from the
  extension.
- Output sinks: `toBuffer()` (with `{ resolveWithObject: true }` it resolves
  `{ data, info }`), `toFile(path)` (resolves `info`), `toUint8Array()` (a
  transferable buffer), or piping the stream. Each returns a Promise unless a
  callback is passed.
- `metadata()` reads the header without decoding pixels: `format`,
  `mediaType`, `width`, `height`, `channels`, `space`, `hasAlpha`,
  `orientation`, `pages`, the raw `exif`/`icc`/`xmp` buffers. `width` and
  `height` ignore EXIF orientation; the `autoOrient` object in the response
  holds the oriented dimensions. It describes the input, not the output of
  the chained operations.
- `clone()` snapshots an instance, so several pipelines (one per output size)
  share one input.
- Metadata on output: the default **strips all metadata**, EXIF orientation
  and the ICC profile included, and converts to sRGB. `keepMetadata()` keeps
  everything; `keepExif()`, `keepIccProfile()`, `keepXmp()` keep one kind;
  `withExif()`, `withExifMerge()`, `withIccProfile()`, `withXmp()` and
  `withDensity()` write chosen values; `withMetadata()` keeps most metadata
  and adds an sRGB profile.
- `timeout({ seconds })` stops processing after that many seconds of libvips
  work (the default `0` means no limit); time spent queued for a thread does
  not count.

## Idioms & best practices
- **Orient explicitly.** Because output strips EXIF orientation by default, a
  photo whose pixels are stored sideways (with a tag saying how to turn them)
  comes out sideways unless the pipeline orients it. Call `autoOrient()` (or
  the constructor's `autoOrient: true`, or the legacy argument-less
  `rotate()`), which applies the tag to the pixels and then removes it.
  Upstream states that a `rotate(angle)`, `flip` or `flop` in the same
  pipeline logically runs after auto-orientation, whatever the call order.
- **Strip by default, keep on purpose.** The default output carries no EXIF,
  so no GPS position, camera serial or timestamps leak from a user's upload.
  Add only the `keep*`/`with*` calls whose content you mean to publish.
- **Treat every uploaded image as untrusted and re-encode it.** Keep `failOn`
  at its default, set `limitInputPixels` to the largest image the feature
  really needs rather than relying on the very large default, and set a
  `timeout`.
- **Decide the accepted formats yourself.** sharp detects the format from the
  content and decodes any format it supports, SVG included. Check
  `metadata().format` (or `mediaType`) against an allow-list before
  processing, and a cheap magic-bytes check before sharp runs at all keeps
  unwanted formats away from the decoder. Neither a file name nor a
  client-declared MIME type says what sharp will decode.
- **One input, several outputs:** build one instance, then `clone()` per
  variant (each with its own `resize` and encoder), and await them together.
- **Read dimensions before resizing when it matters:** `metadata()` is cheap
  and does not decode pixels; use its `autoOrient` dimensions for portrait
  photos.
- Prefer `resolveWithObject: true` when the caller needs the output's real
  dimensions and size; `withoutEnlargement` and `fit: 'inside'` can return
  something smaller than the target.

## General pitfalls
- **A missing platform package fails at load, not at install.** If the
  lockfile or the install omitted the `@img/sharp-*` package for the machine
  that runs the code (optional dependencies disabled, a lockfile from another
  platform, a pruned install), importing sharp throws "Could not load the
  "sharp" module using the <platform> runtime", with suggested fixes. Upstream
  ships no install script that would fail earlier. Observed in practice: a
  lockfile shared between a developer machine and a Linux container is the
  usual way this happens.
- **The pixel limit trusts the header.** `limitInputPixels` and
  `limitInputChannels` compare against dimensions the file declares; upstream
  says both assume that metadata can be trusted. Pair them with `failOn`, a
  `timeout` and a request-size limit, and never set `unlimited: true` on
  untrusted input.
- **Removing the limit is one character away.** `limitInputPixels: 0` or
  `false` disables the check entirely; `true` is the default, not "no limit".
- **Orientation lives in more than one place.** Auto-orientation reads only the
  EXIF `Orientation` tag; an XMP `tiff:Orientation` element is left untouched
  and is the consumer's problem.
- **Order matters for rotate, resize and extract.** `.rotate(x).extract(y)`
  and `.extract(y).rotate(x)` differ, and only one `rotate(angle)` and one
  `resize` per pipeline take effect: earlier calls are ignored silently.
- **`metadata()` describes the input.** Its dimensions do not reflect a resize
  or rotate in the chain, and ignore EXIF orientation.
- **Bundling sharp breaks it.** A bundler that inlines the module loses the
  native binary; mark it external.
- **The thread pool caps throughput.** Images in flight are limited by libuv's
  thread pool (4 threads by default); beyond that, work waits in
  `sharp.queue`.

## Testing
- Upstream gives no testing guidance for projects that use sharp; none was
  observed in practice beyond the following, which follow from the API.
- Assert on decoded results, not bytes: read the output back with
  `sharp(output).metadata()` and check `format`, `width`, `height` and that
  `exif` is absent (or present when it was kept).
- For orientation, use a fixture whose EXIF `Orientation` is not 1 and assert
  the output's dimensions are swapped as expected.
- Exercise the guards with fixtures: an image above the pixel limit must be
  refused, and a truncated file must fail under the default `failOn`.
- `sharp.versions` reports the sharp and libvips versions actually loaded,
  which helps a test or a startup log confirm which binary ran.

## Security defaults
- **Input guards are on by default:** a pixel ceiling (about 268 megapixels),
  a channel ceiling of 5, `failOn: 'warning'`, and the format libraries'
  memory-exhaustion protections. `unlimited: true`, `limitInputPixels: 0` or
  `false`, and a lower `failOn` level each switch one of them off.
- **No processing timeout by default**; a crafted image can keep a worker busy
  until one is set.
- **Metadata is stripped on output by default**, which keeps location and
  device data out of published images; `keepMetadata()`, `keepExif()` and
  `withMetadata()` put it back.
- SVG input is rendered, its text through the system's fonts; accept it from
  untrusted sources only if the feature needs it.

## Operational behaviour
- **Concurrency.** Images run on libuv's thread pool, whose size
  (`UV_THREADPOOL_SIZE`, default 4) caps how many images process in
  parallel; raise it before the process starts on machines with more cores.
  Each image may also use several libvips threads (`sharp.concurrency()`).
  Some encoders (AVIF) manage threads of their own.
- **Memory.** libvips streams small regions, so memory is far below the
  decoded image size. On glibc Linux the default allocator fragments under
  this workload, which is why sharp drops per-image concurrency to 1 there;
  upstream recommends jemalloc or `MALLOC_ARENA_MAX=2` (or 4) for long-running
  processes. musl (Alpine) and non-Linux systems are unaffected.
- **Cache.** libvips' operation cache is on by default (50 MB, 20 files, 100
  operations); `sharp.cache()` returns usage statistics and `sharp.cache(false)`
  turns it off.
- **Monitoring.** `sharp.queue` emits `change` with the number of tasks
  waiting for a thread; `sharp.counters()` returns queued and in-process
  counts.
- **Failure.** Invalid parameters throw synchronously; decode errors, limit
  violations and timeouts reject the output Promise. Non-critical problems are
  `warning` events.
- **Startup.** The native binary loads on first import; a missing or
  incompatible binary throws there (see pitfalls).

## Interop
- Node streams and the Web Streams API: a sharp instance is a Node
  `Duplex`, so it sits in a `pipe` chain between an upload stream and a
  storage or HTTP stream; upstream shows `Duplex.toWeb` for Web Streams
  (from Node.js 24.15.0).
- [typescript](../language/typescript.md): types ship in the package and
  expect `@types/node`.
- Alternatives upstream benchmarks against: jimp (pure JavaScript, slower),
  and the ImageMagick and GraphicsMagick wrappers (`imagemagick`, `gm`), which
  shell out to system binaries.

## Major lines
sharp is still on 0.x, and its minor releases are where breaking changes land
(the changelog marks them "Breaking"), so each 0.N line is a line of its own.

### 0.32 line
- TypeScript definitions are published in the package; `@types/sharp` is
  deprecated.
- Sequential read became the default where possible.

### 0.33 line
- Prebuilt binaries are distributed through the npm registry as optional
  platform packages and installed by the package manager; building from
  source needs `node-addon-api`.
- `sharp.vendor` was removed. `withMetadata()` was partly deprecated in favour
  of finer control: `keepExif`, `withExif`, `withExifMerge`, `keepIccProfile`,
  `withIccProfile` and `keepMetadata` arrived.
- The `trim` options must be an object.

### 0.34 line
- Breaking: an array of inputs is joined or animated; `removeAlpha` removes
  every alpha channel; non-animated GIF output no longer loops.
- `autoOrient()` and the `autoOrient` constructor option arrived (before it,
  argument-less `rotate()` was the way to orient).
- linux-x64 binaries require the v2 microarchitecture.

### 0.35 line
- Requires Node.js 20.9.0 or later (Node-API v9).
- The `install` script was removed: where no prebuilt binary exists, use the
  WebAssembly package or build from source by hand.
- `limitInputChannels` was added, with a default of 5.
- The deprecated `failOnError` constructor property was removed (use
  `failOn`), as were `paletteBitDepth` in metadata and the deprecated
  `sharpen` properties; `format.jp2k` became `format.jp2`.
- ES module support, `toUint8Array()`, `withDensity()`, and `mediaType` in
  the metadata response arrived; the WebAssembly binaries lost their
  experimental status.

## Upstream docs
- Docs home: https://sharp.pixelplumbing.com/
- Install (platforms, cross-platform lockfiles, bundlers, fonts):
  https://sharp.pixelplumbing.com/install/
- Constructor and input options: https://sharp.pixelplumbing.com/api-constructor/
- Output and metadata: https://sharp.pixelplumbing.com/api-output/
- Operations (rotate, autoOrient): https://sharp.pixelplumbing.com/api-operation/
- Performance (threads, allocator): https://sharp.pixelplumbing.com/performance/
- Changelog: https://sharp.pixelplumbing.com/changelog/
- Source: https://github.com/lovell/sharp
