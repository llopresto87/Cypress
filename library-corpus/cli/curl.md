# curl — cli

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a tool, NOT a version-pinned page. curl
> usually arrives from the host's package manager or a base image rather than a
> project lockfile, so the version that matters is the one on the machine that
> runs the script: record it with `ingest-library` in the project's own page,
> and check any behavior below that this page flags as version-sensitive against
> that version.

## What it is
curl is the command-line HTTP (and many-protocol) client built on libcurl. In a
project it is most often the glue in shell scripts and pipeline steps that call a
REST API with a credential. That is the use this page covers: how a credential
reaches curl, where it can leak, and what curl does with it when the server
redirects.

## Core API / usage shape
```
curl -H 'Name: value' URL          # add a request header (repeatable)
curl -H @file URL                  # read headers from a file, one per line
curl -H @- URL                     # read headers from stdin
curl -u ':TOKEN' URL               # basic auth; an empty user name suits token schemes
curl -L URL                        # --location: follow redirects
curl --location-trusted URL        # follow redirects AND resend credentials to another host
curl -v | --trace FILE | --trace-ascii FILE   # show the exchange, headers included
curl -fsS URL                      # --fail --silent --show-error: non-2xx is a non-zero exit, errors still print
```

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
  `-sS` so progress output stays quiet but errors still print.

## General pitfalls
- **A header file hides the credential from argv, not from verbose output.**
  `-v`, `--trace` and `--trace-ascii` print every header sent, and upstream
  documents no redaction of any header value, however it reached curl. A token
  passed through `@file` is exactly as exposed by a stray `-v` in a pipeline log
  as one written on the command line. Keep verbose and trace flags off any
  logged invocation that carries a secret.
- **Redirect protection covers host, port and scheme only on a recent enough
  curl.** Without `--location-trusted`, curl drops `Authorization` and `Cookie`
  when a redirect changes the host, the port or the scheme, for headers from a
  file exactly as for literal ones. Older releases compared the host name only,
  so a redirect to the same host on another port or scheme could still leak the
  header. The protection widened across releases: confirm it on the version the
  script actually runs on before relying on it.
- **Blank lines and comments in a header file are undocumented.** The `--form`
  option's own `@file` reader documents skipping blank and `#` lines; the
  `--header` reader says nothing either way. Do not assume a `#` comment is
  ignored in a header file a person might edit.
- **curl follows no redirects by default, but a wrapper may.** Plain curl stops
  at a 3xx unless `-L` is given. Scripts often add `-L` everywhere out of habit;
  when a credential rides the request, ask whether following the redirect is
  wanted at all, and treat an unexpected 3xx from an API as a failure.

## Upstream docs
- Manual (every option; see `-H`, `-v`, `-L`, `--location-trusted`):
  https://curl.se/docs/manpage.html
- Security advisories index: https://curl.se/docs/security.html
- Source: https://github.com/curl/curl
- Project home: https://curl.se/
