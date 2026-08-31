# jjwt — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A Java library to create, sign, and parse JSON Web Tokens (JWTs). The canonical
Maven artifact is `io.jsonwebtoken:jjwt`, distributed as the module set
`jjwt-api` (the compile-time surface), `jjwt-impl` (the runtime
implementation), and a serialization module such as `jjwt-jackson` (JSON
marshalling) — the api module is used at compile time while impl and the
serializer are pulled in at runtime.

## Core API / usage shape
- `Jwts.builder()` starts a fluent chain that sets claims (subject, issuer,
  audience, expiration, issued-at, and arbitrary custom claims) and signs with
  a key and algorithm to produce a compact, URL-safe JWT string.
- `Jwts.parser()` builds a parser configured with the verification key; it
  verifies a compact JWT's signature and yields its claims, rejecting tokens
  that fail signature or expiration checks.
- With symmetric algorithms the same secret key both signs and verifies. With
  asymmetric algorithms the issuer signs with the private key and every
  consumer validates with the matching public key.

## Idioms & best practices
- Use the fluent builder for issuance and the parser for validation rather than
  assembling token strings by hand.
- Keep signing and verification keys paired and, for asymmetric algorithms,
  strictly separated — only the issuer holds the private key; consumers hold
  only the public key.
- Wrap issuance and validation in a small internal service rather than calling
  the builder/parser ad hoc at each call site, so key handling and claim
  conventions live in one place.

## General pitfalls
- The library's distribution evolved from an early single-jar form to a split
  into separate api/impl/serializer artifacts alongside a revised, typed
  key-builder API. Crossing that lineage boundary is a breaking API change, not
  a drop-in bump — code and dependencies must be migrated together.
- Older distributions can additionally require JAXB on the classpath when run
  on modern JDKs from which JAXB was removed; a missing runtime dependency
  surfaces only when a token is issued or parsed.

## Upstream docs
- https://github.com/jwtk/jjwt
- https://javadoc.io/doc/io.jsonwebtoken/jjwt-api
