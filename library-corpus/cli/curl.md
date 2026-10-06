# curl — cli

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. curl usually arrives from the host's package manager or a
> base image rather than a project lockfile, so the version that matters is the
> one on the machine that runs the script: record it with `ingest-library` in
> the project's own page, and check any behavior below that this page flags as
> version-sensitive against that version.

## What it is
curl is the command-line HTTP (and many-protocol) client built on libcurl. In a
project it is most often the glue in shell scripts and pipeline steps that call a
REST API with a credential. That is the use this page covers: how a credential
reaches curl, where it can leak, and what curl does with it when the server
redirects. curl and libcurl are released together under the curl licence, an
MIT/X-style licence (SPDX `curl`).

## Install, setup and configuration
- curl comes from the operating system's package manager or the base image;
  minimal and distroless images often leave it out. `curl --version` prints
  the curl and libcurl versions, the TLS backend, and the protocols and
  features this build supports. Read it on the machine that runs the script,
  because builds differ in TLS library, HTTP/2 and HTTP/3 support.
- **curl reads a config file before the command line.** Unless the first
  argument is `-q` (`--disable`), curl loads a default `.curlrc`, searched in
  `$CURL_HOME`, `$XDG_CONFIG_HOME`, then `$HOME` (with Windows-specific places
  after), and applies it even when `-K`/`--config` names another file. A
  script that must behave the same on every machine starts with `curl -q`.
- `-K file` (`--config`) reads options from a file, one per line, long names
  allowed without the dashes. It is another way to keep a secret out of argv.
- **Proxy environment variables apply silently.** curl honours
  `<scheme>_proxy` (`https_proxy`, `ALL_PROXY`) and `NO_PROXY`. `http_proxy`
  is accepted only in lowercase, because CGI turns an incoming `Proxy:` header
  into `HTTP_PROXY`. `--noproxy` overrides per call.

## Core API / usage shape
```
curl -H 'Name: value' URL          # add a request header (repeatable)
curl -H @file URL                  # read headers from a file, one per line
curl -H @- URL                     # read headers from stdin
curl -u ':TOKEN' URL               # basic auth; an empty user name suits token schemes
curl --oauth2-bearer TOKEN URL     # Authorization: Bearer, as curl's own credential
curl -L URL                        # --location: follow redirects
curl --location-trusted URL        # follow redirects AND resend credentials to another host
curl -v | --trace FILE | --trace-ascii FILE   # show the exchange, headers included
curl -fsS URL                      # --fail --silent --show-error: non-2xx is a non-zero exit, errors still print
curl --fail-with-body URL          # like --fail, but still writes the error body
curl -w '%{http_code}' -o out URL  # --write-out: print fields such as the status after the transfer
curl --connect-timeout S -m S URL  # bound the connect phase and the whole transfer
curl --retry N URL                 # retry transient failures with backoff
```
- In `-v` output, `>` marks a header curl sent, `<` a header it received, `}`
  and `{` data sent and received, and `*` curl's own informational lines. Grep
  for `^> ` to see exactly which headers left the machine.
- `-f` exits with code 22 and writes no body on a status of 400 or more.
  `-m` and `--connect-timeout` expiring exit with 28.

## Idioms & best practices
- **Keep a credential out of argv with a header file.** A header passed as
  `-H "Authorization: Bearer $TOKEN"` is a process argument, visible in `ps`, in
  shell history and to any tool that logs command lines. Write the header to a
  file that only the current user can read, pass `-H @file`, and remove the file
  on exit:
  ```sh
  umask 077
  headerfile="$(mktemp)"
  trap 'rm -f "$headerfile"' EXIT
  printf 'Authorization: Bearer %s\n' "$TOKEN" > "$headerfile"
  curl -fsS -H "@${headerfile}" "$url"
  ```
  The `trap` goes in right after `mktemp`, so the file is removed however the
  script exits, including when `curl -f` fails under `set -e`.
  Feeding the header on stdin (`-H @-`) avoids the file altogether when the
  script's stdin is free. Generate the file from a script rather than by hand
  (see the header-file pitfall below).
- **Never add `--location-trusted` for convenience.** It is the documented
  opt-in that makes curl resend `Authorization` and `Cookie` headers to a
  different host on redirect. Upstream's own examples pair it with explicit user
  credentials to show it exists for callers who *want* cross-host forwarding. If
  a redirect is breaking a call, find out where it goes before trusting it.
- **Prefer failing loudly.** `-f` (`--fail`) turns an HTTP error status into a
  non-zero exit, so a script cannot mistake an error page for data. Combine with
  `-sS` so progress output stays quiet but errors still print. Use
  `--fail-with-body` when the error body is worth keeping for the log.
- **Bound every call.** Most curl operations have no timeout by default. Set
  `--connect-timeout` and `-m` (`--max-time`) on anything a pipeline waits on.
- **Retry only what is safe to repeat.** `--retry N` retries timeouts and HTTP
  408, 429, 500, 502, 503, 504, 522 and 524, waiting one second and doubling up
  to ten minutes, and honours `Retry-After`. A refused connection is retried
  only with `--retry-connrefused`, and other errors only with
  `--retry-all-errors`. Upstream calls that one the sledgehammer: it can send
  or receive data twice, and output piped or redirected by the shell is not
  reset before a retry.

## General pitfalls
- **A header file hides the credential from argv, not from verbose output.**
  `-v`, `--trace` and `--trace-ascii` print every header sent, and upstream
  documents no redaction of any header value, however it reached curl. A token
  passed through `@file` is exactly as exposed by a stray `-v` in a pipeline log
  as one written on the command line. Keep verbose and trace flags off any
  logged invocation that carries a secret.
- **Only `Authorization` and `Cookie` are held back on a redirect.** The
  `--header` manual warns that headers set with `-H` go into every request,
  including the ones a redirect leads to on another host. curl strips only
  `Authorization:` and `Cookie:` when a redirect changes origin. An API key in
  any other header (`X-Api-Key`, say) follows `-L` to whatever host the
  redirect names. Do not combine `-L` with a custom secret header.
- **Redirect protection covers host, port and scheme only on a recent enough
  curl.** Without `--location-trusted`, curl drops `Authorization` and `Cookie`
  when a redirect changes the host, the port or the scheme, for headers from a
  file exactly as for literal ones. Releases before 7.83.0 compared the host
  name only, so a redirect to the same host on another port or scheme still
  carried the header. Confirm the version the script runs on (see Major lines).
- **Blank lines and comments in a header file are undocumented.** The `--form`
  option's own `@file` reader documents skipping blank and `#` lines; the
  `--header` reader says nothing either way. Do not assume a `#` comment is
  ignored in a header file a person might edit.
- **curl follows no redirects by default, but a wrapper may.** Plain curl stops
  at a 3xx unless `-L` is given. Scripts often add `-L` everywhere out of habit;
  when a credential rides the request, ask whether following the redirect is
  wanted at all, and treat an unexpected 3xx from an API as a failure.
- **`--fail` is not airtight.** Upstream notes that some non-success codes slip
  through, especially 401 and 407 when authentication is involved. Check the
  status with `-w '%{http_code}'` where it matters.
- **A user's `.curlrc` changes a script's behaviour.** Options such as `-L`,
  `-k` or a proxy in the default config file apply to every call that does not
  start with `-q`.

## Testing
Upstream's test suite covers curl itself and documents no pattern for testing
the scripts that call it. What a script can assert on is documented: the exit
code (22 from `--fail`, 28 from a timeout), the fields `-w`/`--write-out`
prints, and the `>` lines of `-v` output, which show exactly the headers sent.
Never run the verbose form with a real credential.

## Security defaults
- **TLS verification is on by default.** curl checks that the server's
  certificate is signed by a CA in its store and matches the host name. `-k`
  (`--insecure`) skips this and, for SFTP and SCP, the `known_hosts` check.
  Point at a private CA with `--cacert` instead.
- **Credentials stay with the first origin on redirect**, apart from the
  `-H` headers named above, unless `--location-trusted` is given.
- **`--proto` and `--proto-redir`** limit the protocols a call, or a redirect,
  may use, for example `--proto '=https'`.
- **A secret on the command line is public to the host.** Use `-H @file`,
  `-H @-`, `-K file` or a `.netrc` (`--netrc-file`) instead.

## Operational behaviour
- A curl process does one transfer (or a list of them) and exits; it keeps no
  state between runs unless a cookie jar, alt-svc cache or HSTS cache file is
  named.
- **Exit codes are the interface.** 0 means the transfer worked, which is not
  the same as an HTTP success unless `-f` or `--fail-with-body` is set.
- **No timeouts by default.** A stalled server holds the pipeline until
  something outside curl kills it; see the bound-every-call idiom.
- `-s` hides errors as well as progress; pair it with `-S`.

## Interop
- **Shell:** quote every URL and header. `&` and `?` mean something to the
  shell, and curl itself expands `{}` and `[]` in a URL as globs unless `-g`
  (`--globoff`) is given.
- **Container images:** a health check or build step that calls curl must
  install it or use another client (see Install, setup and configuration).

## Major lines

### 7.x line
- `-H @file` and `-H @-` exist from 7.55.0. Redirect stripping of
  `Authorization` and `Cookie` widened from a host-name check to host, port
  and scheme in 7.83.0. `--fail-with-body` arrives in 7.76.0 and
  `--retry-all-errors` in 7.71.0. An old 7.x build in a long-lived base image
  can lack all of these; check `curl --version`.

### 8.x line
- The move to 8 marks no break in the command line: every 8.x build has the
  header-file reader and the host, port and scheme redirect rule.
- `--variable` (with `--expand-<option>`) arrives in 8.3.0: it reads
  environment variables or files into option values, and `--variable %NAME`
  fails when the variable is unset.
- From 8.10.0 a repeated `-v` raises the trace level; a single `-v` resets it.

## Upstream docs
- Manual (every option; see `-H`, `-v`, `-L`, `--location-trusted`):
  https://curl.se/docs/manpage.html
- When each option was added:
  https://github.com/curl/curl/blob/master/docs/options-in-versions
- Everything curl (the long-form guide: config files, redirects, timeouts,
  proxies, verbose output): https://everything.curl.dev/
- SSL certificate verification: https://curl.se/docs/sslcerts.html
- Security advisories index: https://curl.se/docs/security.html
- Source: https://github.com/curl/curl
- Project home: https://curl.se/
