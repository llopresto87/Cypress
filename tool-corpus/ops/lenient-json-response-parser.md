# Tool: lenient-json-response-parser

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable tool: the script below runs as-is, and a
> plant wires it into whatever reads the responses (a filter, a client, a
> probe).

## 0. Identity

- **Category:** ops
- **Name:** lenient-json-response-parser
- **Language / runtime:** python3, **stdlib only** (`json`, `base64`)
- **Stability:** **portable**. The normalizer, the strict parse, the missing-key
  rule and the token-claim decoder are complete. A plant adds only the call
  site: a template filter, an HTTP client wrapper or a command-line probe.

## 1. What it does

Many embedded web servers (device admin pages, appliance consoles, firmware
web UIs) answer with a body that their own web page evaluates as a JavaScript
object literal. It looks like JSON, but it is not: keys are bare, strings may
be single-quoted, and lists and objects end with a trailing comma. A strict
JSON parser refuses it.

This tool is the **one parsing home** for those bodies. It rewrites the literal
into strict JSON, then parses it strictly. A body that still does not parse
raises an error. It never returns an empty object.

It also decodes the claims of the session token such servers often hand out
(three base64url segments, `header.payload.signature`), which callers read to
find a user id or an expiry.

**When not to use it.** Do not use it on a server that returns real JSON: use
the strict parser and keep the strictness. Do not use it on a body the server
documents as some other format. And never use a decoded token claim to make an
authorization decision (§5).

## 2. Interface & invocation

```sh
python3 lenient-json.py [--key <name>] < body   # print the body, or one key, as strict JSON
python3 lenient-json.py --claims < token        # print a token's claims, unverified
python3 lenient-json.py --key token < body | python3 lenient-json.py --claims   # token field, then its claims
python3 lenient-json.py --self-test             # run the fixture self-test
```

As a library: `parse(text)`, `get(text, key[, default])`,
`token_claims(token)` and `normalize(text)`, all in the script below. Each
takes the body as `str`. Any other type raises `TypeError` (§4 says why a
call site must not pass one).

- **Inputs:** the response body as text; a key name for `--key`; a token
  (or a body holding one, after the caller extracts it) for `--claims`.
- **Outputs:** strict JSON on stdout, with keys sorted. Errors go to stderr as
  one line, with an offset. The offset counts characters in the normalized
  text, not in the raw body: quoting a bare key and dropping a trailing comma
  move every later position, so look near the offset, not at it. An error
  never quotes the body, because response bodies hold session tokens.
- **Exit codes:** 0 parsed; 1 the body does not parse, the key is absent, or
  the token does not decode; 2 usage error.
- **Preconditions:** none beyond python3.

## 3. Approach / algorithm

### Normalize outside strings, then parse strictly

The tool scans the body once, left to right, and tracks whether it is inside a
string. It rewrites only text **outside** string literals:

1. A single-quoted string becomes a double-quoted string. An escaped
   apostrophe (`\'`) inside it becomes a plain apostrophe, and a double quote
   inside it is escaped.
2. A bare identifier in key position is quoted. Key position means: right
   after `{` or `,`, and followed (after optional blanks) by `:`. Identifiers
   use the JavaScript start set (letters, `_`, `$`) and may contain digits.
3. A comma whose next non-blank character is `}` or `]` is dropped.

Everything else passes through unchanged, and `json.loads` then accepts it or
refuses it. Python's `json.loads` is not strict by default: it accepts `NaN`,
`Infinity` and `-Infinity`, which no JSON value can hold, and it keeps the last
of two equal keys in one object. The tool passes it a `parse_constant` that
refuses the three constants and an `object_pairs_hook` that refuses a
duplicate key, so the output it prints is always JSON. The tool adds no "best
effort" recovery after that. A partial
parse is a guess, and a guess here becomes a wrong value in a later step.

### Two corrections to the naive version

The usual first version of this parser has two defects. Both are easy to
write, and both make wrong results look like correct ones.

- **A blanket replace of `'` with `"` corrupts values.** It also rewrites the
  apostrophe in a double-quoted value such as `"O'Brien"`, which turns the
  body into broken JSON. That is why rule 1 above works per string literal,
  and why the scan tracks string state at all. The same scan keeps rules 2 and
  3 away from string content: `"{k: 1,}"` inside a value is text, not
  structure.
- **Returning `{}` on a parse failure is fail-open.** Every caller then reads
  "no such field" or "empty list", which is a plausible answer. A login page
  served instead of data, a firmware change in the response shape and a
  truncated body all become a quiet empty result. The tool raises instead. A
  caller that wants a fallback must ask for it by name (`get(..., default=)`)
  at the one place where a fallback is correct.

The same rule covers a missing key: `get(text, key)` raises `KeyError` unless
the caller passes an explicit `default`.

### Token claims

`token_claims` splits the token on `.`, requires three segments, takes the
middle one, restores the `=` padding that base64url strips
(`"=" * (-len(seg) % 4)`), decodes it and parses it as a JSON object. Any
failure raises. It does not verify the signature. The tool has no key, and
for this use (find the user id the server assigned, or log the expiry) the
signature does not matter. For any trust decision it matters, and §5 says so.

```python
#!/usr/bin/env python3
"""lenient-json: one parsing home for the non-strict JSON an embedded web
server returns (bare keys, single-quoted strings, trailing commas).

Normalize outside string literals only, then parse strictly. A body that still
does not parse raises; it never comes back as an empty object.

  lenient-json.py [--key NAME] < body     print the parsed body (or one key) as strict JSON
  lenient-json.py --claims < token        print the claims of a three-part token, UNVERIFIED
  lenient-json.py --self-test             run the fixture self-test

Exit 0 parsed; 1 the body does not parse, or the key is absent; 2 usage.
Stdlib only.
"""
from __future__ import annotations

import base64
import json
import sys

IDENT_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$")
IDENT_REST = IDENT_START | set("0123456789")


class LenientJSONError(ValueError):
    """The body is not JSON even after normalization. The message carries a
    position, never the body: response bodies hold tokens."""


def _skip_ws(text: str, i: int) -> int:
    while i < len(text) and text[i] in " \t\r\n":
        i += 1
    return i


def normalize(text: str) -> str:
    """Rewrite a JavaScript-style object literal into strict JSON.

    One left-to-right scan that tracks whether it is inside a string, so that
    nothing inside a string value is ever rewritten:
      - a single-quoted string becomes a double-quoted one (an apostrophe
        inside a double-quoted value is left alone; a double quote inside a
        single-quoted value is escaped);
      - a bare identifier in key position (after '{' or ',', followed by ':')
        is quoted;
      - a comma whose next non-blank character is '}' or ']' is dropped.
    Anything else passes through unchanged, for json.loads to accept or refuse.
    """
    if not isinstance(text, str):
        raise TypeError("normalize() takes the response body as str")
    out: list[str] = []
    i, n = 0, len(text)
    expect_key = False            # true right after '{' or ','
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i, expect_key = j + 1, False
            continue
        if c == "'":
            j, buf = i + 1, ['"']
            while j < n and text[j] != "'":
                ch = text[j]
                if ch == "\\" and j + 1 < n:
                    nxt = text[j + 1]
                    buf.append("'" if nxt == "'" else "\\" + nxt)
                    j += 2
                    continue
                buf.append('\\"' if ch == '"' else ch)
                j += 1
            if j >= n:
                raise LenientJSONError(f"unterminated single-quoted string at offset {i}")
            buf.append('"')
            out.append("".join(buf))
            i, expect_key = j + 1, False
            continue
        if c == ",":
            k = _skip_ws(text, i + 1)
            if k < n and text[k] in "}]":
                i = k                  # trailing comma: drop it
                continue
            out.append(c)
            i, expect_key = i + 1, True
            continue
        if c in "{":
            out.append(c)
            i, expect_key = i + 1, True
            continue
        if expect_key and c in IDENT_START:
            j = i + 1
            while j < n and text[j] in IDENT_REST:
                j += 1
            k = _skip_ws(text, j)
            if k < n and text[k] == ":":
                out.append('"' + text[i:j] + '"')
                i, expect_key = j, False
                continue
        if c not in " \t\r\n":
            expect_key = False
        out.append(c)
        i += 1
    return "".join(out)


def _refuse_constant(name: str):
    # json.loads accepts NaN, Infinity and -Infinity unless told otherwise
    raise LenientJSONError(f"{name} is not a JSON value")


def _refuse_duplicates(pairs: list) -> dict:
    # json.loads keeps the last of two equal keys unless told otherwise
    obj: dict = {}
    for k, v in pairs:
        if k in obj:
            raise LenientJSONError(f"duplicate key {k!r} in one object")
        obj[k] = v
    return obj


def parse(text: str):
    """Normalize, then parse strictly. Raises LenientJSONError on failure,
    including the NaN/Infinity constants and a duplicate key, which plain
    json.loads accepts."""
    try:
        return json.loads(normalize(text), parse_constant=_refuse_constant,
                          object_pairs_hook=_refuse_duplicates)
    except json.JSONDecodeError as exc:
        raise LenientJSONError(
            f"body is not JSON after normalization: {exc.msg} at offset {exc.pos}") from None


_MISSING = object()


def get(text: str, key: str, default=_MISSING):
    """One top-level key. A missing key raises KeyError unless the caller
    passes an explicit default: an absent field is a finding, not a blank."""
    data = parse(text)
    if not isinstance(data, dict):
        raise LenientJSONError(f"body is a {type(data).__name__}, not an object")
    if key in data:
        return data[key]
    if default is _MISSING:
        raise KeyError(key)
    return default


def token_claims(token: str) -> dict:
    """Decode the middle segment of a three-part token (header.payload.signature)
    as base64url JSON, restoring the padding the encoding strips.

    This does NOT verify the signature. The claims are untrusted input, fit
    for logging and routing a request, never for an authorization decision.
    """
    if not isinstance(token, str):
        raise LenientJSONError("token is not a string")
    parts = token.strip().split(".")
    if len(parts) != 3 or not parts[1]:
        raise LenientJSONError(f"token has {len(parts)} segment(s), expected 3")
    seg = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        claims = json.loads(base64.urlsafe_b64decode(seg.encode("ascii")))
    except (ValueError, UnicodeError) as exc:
        raise LenientJSONError(f"token payload does not decode: {type(exc).__name__}") from None
    if not isinstance(claims, dict):
        raise LenientJSONError("token payload is not a JSON object")
    return claims


def _b64url(obj) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def self_test() -> None:
    # bare keys, single quotes, trailing commas, nesting
    body = "{ok:1, msg:'saved', list:[1,2,], nested:{a_b:true,},}"
    assert parse(body) == {"ok": 1, "msg": "saved", "list": [1, 2], "nested": {"a_b": True}}
    # an apostrophe inside a double-quoted value survives (the blanket-replace bug)
    assert parse('{name:"O\'Brien", note:"it\'s fine"}') == {"name": "O'Brien", "note": "it's fine"}
    # a double quote inside a single-quoted value is escaped, an escaped apostrophe kept
    assert parse("{q:'say \"hi\"', a:'don\\'t'}") == {"q": 'say "hi"', "a": "don't"}
    # text that looks like a key or a trailing comma INSIDE a string is untouched
    assert parse("{s:'x, }', t:\"{k: 1,}\"}") == {"s": "x, }", "t": "{k: 1,}"}
    # strict JSON passes through unchanged
    assert parse('{"a": [1, {"b": null}]}') == {"a": [1, {"b": None}]}
    # a body that is not JSON raises: never an empty object (the fail-open bug)
    for bad in ("<html>login</html>", "{a:}", "", "{a:'open}",
                "{a:NaN}", "{a:Infinity}", "{a:-Infinity}", "{a:1, a:2}"):
        try:
            parse(bad)
        except LenientJSONError as exc:
            assert "login" not in str(exc), "the error leaked body content"
        else:
            raise AssertionError(f"{bad!r} parsed instead of raising")
    # a missing key raises unless a default is explicit
    try:
        get("{a:1}", "b")
    except KeyError:
        pass
    else:
        raise AssertionError("missing key returned a value")
    assert get("{a:1}", "b", default=None) is None
    # token claims: padding restored for every payload length mod 4
    for uid in ("1", "12", "123", "1234"):
        tok = _b64url({"alg": "none"}) + "." + _b64url({"uid": uid}) + ".sig"
        assert token_claims(tok) == {"uid": uid}, uid
    for bad in ("only.two", "a.!!!.c", "", "a.." ):
        try:
            token_claims(bad)
        except LenientJSONError:
            pass
        else:
            raise AssertionError(f"{bad!r} decoded instead of raising")
    print("self-test: PASS (bare keys, quotes in values, strings untouched, "
          "strict passthrough, refuse non-JSON, NaN and duplicate keys, missing key, "
          "token padding, bad token)")


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        self_test()
        return 0
    if argv == ["--claims"]:
        try:
            print(json.dumps(token_claims(sys.stdin.read()), sort_keys=True))
        except LenientJSONError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        return 0
    key = None
    if argv[:1] == ["--key"] and len(argv) == 2:
        key = argv[1]
    elif argv:
        print(__doc__, file=sys.stderr)
        return 2
    body = sys.stdin.read()
    try:
        out = parse(body) if key is None else get(body, key)
    except LenientJSONError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyError:
        print(f"ERROR: key {key!r} is absent from the body", file=sys.stderr)
        return 1
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Recorded run of the self-test and of the script on a synthetic fixture (a body
with bare keys, single-quoted strings, trailing commas and an apostrophe inside
a double-quoted value; then a login page served in place of data; then a
synthetic unsigned token):

```text
$ python3 lenient-json.py --self-test
self-test: PASS (bare keys, quotes in values, strings untouched, strict passthrough, refuse non-JSON, NaN and duplicate keys, missing key, token padding, bad token)
$ cat body.txt
{status:'ok',user:{name:"O'Neil",roles:['a','b',],},}
$ python3 lenient-json.py < body.txt                     # exit 0
{"status": "ok", "user": {"name": "O'Neil", "roles": ["a", "b"]}}
$ python3 lenient-json.py --key user < body.txt          # exit 0
{"name": "O'Neil", "roles": ["a", "b"]}
$ python3 lenient-json.py --key missing < body.txt       # exit 1
ERROR: key 'missing' is absent from the body
$ printf '<html>sign in</html>' | python3 lenient-json.py   # exit 1
ERROR: body is not JSON after normalization: Expecting value at offset 0
$ python3 lenient-json.py --claims < tok.txt             # exit 0
{"iss": "device", "uid": "7"}
```

The naive version (blanket quote replace, `{}` on failure) returned `{}` for
both `body.txt` and the login page.

## 4. Portable vs blueprint

- **Portable (use as-is):** the string-aware normalizer, the strict parse
  that raises, the explicit-default rule for a missing key, the token-claim
  decoder with padding restored, the error messages that never quote the body.
- **Write per project:** the call site. In a configuration-management tool
  this is usually a filter plugin that wraps `parse` and `get`. In an HTTP
  client it is one response hook. Keep it to **one** call site per project, so
  that a change in the server's format is fixed in one place.
- **An already-decoded value must not reach `parse`.** Some HTTP clients
  decode a response themselves when its content type says JSON, and then hand
  the call site a dict or a list. `parse` raises `TypeError` on that. The
  wrapper checks the type first and passes a dict or list through unchanged;
  only a `str` goes to `parse` or `get`.
- **Adopting note:** put the error where the operator sees it. A template
  filter that raises fails the task that called it, which is the intent. Do
  not catch the error in the wrapper to "keep the run going".

## 5. Pitfalls and sharp edges

- **Normalization is not a JavaScript parser.** It handles the three
  departures listed in §3. Comments, unquoted values such as `undefined`,
  `NaN` and `Infinity` (JavaScript accepts them, JSON has no value for them),
  hexadecimal numbers, numeric keys and template strings are not rewritten,
  and the strict parse refuses them. That refusal is correct: extend the
  normalizer with a test for the new case when a real server needs it, and do
  not add a fallback.
- **A body that parses can still be the wrong body.** A server that answers an
  expired session with a small valid object (`{err:1}`) parses cleanly. Check
  the field that says the call worked before reading the data fields.
- **A decoded claim is untrusted.** Anyone can write a token with any claims.
  Reading `uid` to label a log line or to address the next request on the same
  session is fine. Deciding what someone may do from it is not: that needs
  signature verification with the server's key, through a real token library.
- **Never print the body in an error.** The body that failed to parse is often
  the login answer, and it carries the token. Report the offset and the parser
  message only.
- **One home, or the fix happens twice.** Ad hoc regular expressions over the
  raw body (to pull out a token, for example) are a second parser. They miss
  the format change the real parser was fixed for. Route every read through
  `parse` or `get`.

## 6. Tests that cover it

The self-test in the script above (`lenient-json.py --self-test`) asserts:
bare keys, single-quoted strings and trailing commas at several depths parse
to the expected object; an apostrophe inside a double-quoted value survives; a
double quote inside a single-quoted value is escaped and an escaped apostrophe
is kept; key-like and comma-like text inside a string is not rewritten; strict
JSON passes through unchanged; an HTML page, an empty body, an incomplete
value and an unterminated string all raise, and no error quotes the body;
`NaN`, `Infinity`, `-Infinity` and a duplicate key raise; a missing key raises unless a default is explicit; a token payload of each
length modulo 4 decodes; a token with two segments, an undecodable payload or
an empty payload raises.

- **How to run the tests:** `python3 lenient-json.py --self-test` (exit 0 on
  pass; an `AssertionError` names the case that failed).

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (whether the
  server answers at all; this page reads what it answered);
  `tool-corpus/ops/structured-secret-field-detector.md` (the same rule that a
  missing input is a failure, never a clean result).
- **Sources:** distilled from practice. The base64url
  alphabet is RFC 4648 §5. Signed-token formats such as RFC 7515 (§2) encode
  with every trailing `=` omitted, which is why the decoder restores it.

## 8. Changelog

- 2026-10-05: created. A naive parser replaces every apostrophe and returns
  an empty object on failure; this page ships a string-aware version with its
  self-test.
- 2026-10-05: review fixes. The parse now refuses `NaN`, `Infinity` and a
  duplicate key, which plain `json.loads` accepts; the error offset is
  documented as an offset into the normalized text; the call-site rule for an
  already-decoded value and the two-step token form are stated.
