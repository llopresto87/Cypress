---
stack:
  - library-corpus/maven/rabbitmq
  - library-corpus/maven/spring-cloud-stream
  - library-corpus/nuget/MassTransit.RabbitMQ
  - library-corpus/nuget/RabbitMQ.Client
  - library-corpus/pypi/pika
---

# Tool: fire-and-forget-command-observer

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A complete reference implementation for an AMQP
> 0-9-1 broker (RabbitMQ); it depends on the `pika` client, so it is a blueprint
> by this corpus's definition, but it was run as written (§4).

## 0. Identity

- **Category:** testing
- **Name:** fire-and-forget-command-observer
- **Language / runtime:** python3; stdlib for the buffer and the HTTP surface,
  `pika` for the broker connection (`library-corpus/pypi/pika.md`)
- **Stability:** **blueprint**: the implementation below is complete and was
  run against a real broker, but it needs a third-party client. A plant on
  another language keeps the design (§3) and writes the consumer with its own
  client.

## 1. What it does

A producer publishes a command to a message broker and does not wait for an
answer: start a job, print a label, wake a device. The consumer that used to
act on it (a device, an external system, a service that was retired) is gone
in the environment under test. Nothing then shows whether the command was
sent, with which routing key and which body. The producer's own log says only
that it called "send".

The observer stands in for that consumer in staging. It binds its own durable
queue to the producer's exchange, records every command it receives in a
bounded in-memory buffer, acknowledges it, and exposes the record over a small
internal HTTP surface. An end-to-end test can then trigger the user action and
assert that exactly the expected command came out.

It is test infrastructure for a non-production environment. It acts on
nothing, and it never runs where the real consumer runs.

## 2. Interface & invocation

```sh
OBSERVER_ENABLED=1 \
AMQP_URL='amqp://<user>:<password>@<broker>:5672/%2F' \
EXCHANGE=<producer exchange> EXCHANGE_TYPE=topic EXCHANGE_DURABLE=1 \
python3 observer.py

python3 observer.py --self-test        # buffer and HTTP surface, no broker
```

- **Required environment:** `OBSERVER_ENABLED=1` (it is off by default);
  `AMQP_URL`; `EXCHANGE`, `EXCHANGE_TYPE` (`direct`, `fanout`, `topic`,
  `headers`, or a plugin type starting with `x-`), `EXCHANGE_DURABLE` (`0` or
  `1`; any other value refuses the start), copied from the producer's
  declaration.
- **Credentials:** from the environment, never from the source. Either put
  them in `AMQP_URL`, percent-encoded (`@` is `%40`, `:` is `%3A`, `/` is
  `%2F`; the default vhost `/` is `%2F` too), or set `AMQP_USER` and
  `AMQP_PASSWORD` to the raw values the producer receives and leave them out
  of the URL. A URL that does not parse refuses the start with a message.
- **Optional environment:** `EXCHANGE_AUTO_DELETE` (`0` or `1`, default `0`)
  and `EXCHANGE_ARGS` (a JSON object, default `{}`), used only when the
  observer declares the exchange itself (§3); `QUEUE` (default
  `<exchange>.observer`);
  `BINDING_KEYS`, comma-separated (default `#`); `QUEUE_MAX`, the broker-side
  cap on queued messages (default 10000); `QUEUE_EXPIRES_MS`, delete the
  queue after it has had no consumer for this long (default 0, never);
  `BUFFER_MAX`, the in-memory record (default 1000); `HTTP_BIND` and
  `HTTP_PORT` (default `0.0.0.0:8090`, on the internal network only);
  `DEPLOY_PROFILE`, where `prod` or `production` as a whole word (`eu-prod`,
  `Production`) stops the start; `nonprod-staging` does not.
- **HTTP surface:**
  - `GET /health` returns 200 `{"status":"UP","bound":true}` once the queue
    is bound and consuming, and 503 until then and while the broker is away.
  - `GET /observed` returns `{"count", "next", "observed": [...]}`. Each entry
    has `seq`, `routingKey`, `body`, `receivedAt`. `?key=K` filters on the
    routing key; `?since=N` returns only entries after sequence `N`, and
    `next` is the cursor for the following call.
  - `POST /reset` clears the buffer.
- **Exit codes:** the process exits `3` when the broker rejects the exchange
  or queue declaration (`406 PRECONDITION_FAILED`), and `4` when the broker
  refuses the login or the vhost (`403 ACCESS_REFUSED`). It refuses to start
  (exit `1`, with a message) when it is not enabled, when the profile is
  production, when a declaration variable is missing or invalid, or when
  `AMQP_URL` does not parse. A lost connection is retried, not fatal.

## 3. Approach / algorithm

**Use the producer's exchange; declare it only when it is missing.** The
observer first declares the exchange passively. The AMQP 0-9-1
specification says a passive declare ignores every field except the name, so
it cannot fail on a mismatch: when the producer has already declared the
exchange, the observer binds to it whatever its type, durability or
arguments. Only when the passive declare fails with 404 (the exchange does
not exist yet) does the observer declare it actively, on a new channel, with
`EXCHANGE_TYPE`, `EXCHANGE_DURABLE`, `EXCHANGE_AUTO_DELETE` and
`EXCHANGE_ARGS`. Those values must still equal the producer's declaration,
because the producer declares the same exchange later. Declaring an exchange
that already exists is accepted only when type, durable and arguments are
equal (AMQP 0-9-1 `exchange.declare`, rule "equivalent"). On RabbitMQ a
mismatch closes the channel with `406 PRECONDITION_FAILED - inequivalent arg
'durable' …` (or `'type'`), and here it is the producer that fails
(reproduced, §4). Observed on a RabbitMQ 4 broker, beyond what the AMQP rule
names: RabbitMQ also compares `auto_delete` and the `alternate-exchange`
argument (`inequivalent arg 'auto_delete'`, `inequivalent arg
'alternate-exchange'`). The observer treats a 406 as a configuration error
and exits `3` instead of retrying it forever. Starting the observer before
the producer is therefore the risky order; start the producer first where
the stack allows it.

**Bind a durable queue of its own with a catch-all key.** On a topic
exchange the binding key `#` matches every routing key, so the queue gets a
copy of every command without touching the producer's topology. On a fanout
exchange the key is ignored. On a direct exchange there is no wildcard: set
`BINDING_KEYS` to each key the producer uses. The queue is the observer's own
(`<exchange>.observer`), never a queue a real consumer reads, or the two would
share the messages between them. It is durable, so commands published while
the observer restarts wait in the broker and are recorded when it comes back
(reproduced, §4).

**Record, then acknowledge.** The callback appends the command to the buffer
and then acks it, so a crash between the two redelivers rather than loses it.
Prefetch is capped at 20.

**Bound both sides.** The in-memory buffer drops its oldest entry beyond
`BUFFER_MAX`. The broker queue is declared with `x-max-length` (`QUEUE_MAX`);
RabbitMQ's default overflow behaviour for it is `drop-head`, the oldest
message first. With `QUEUE_EXPIRES_MS`, the queue argument `x-expires`
deletes the queue after it has had no consumer for that long, so a retired
observer does not leave a queue that fills forever. A queue is "unused" for
`x-expires` only when it has no consumers, was not redeclared, and saw no
`basic.get`. Both values could instead be set as broker policies; a
declaration argument that later differs from the existing queue's is the same
406 as an exchange mismatch, so change them by deleting the queue first.

**Health means bound.** `/health` reports 200 only while the queue is bound
and consuming. A test that waits for health before triggering the action
therefore never fires a command into an exchange nobody is listening to.

**Reconnect with capped backoff.** A lost connection marks the observer
unbound and retries after 2, 4, 8, … seconds, capped at 30, so it survives a
broker restart. A refused login is not retried: a wrong password never heals,
and a retry loop would show only as a 503 health. The observer exits `4`.

**Staging only, internal only, default off.** The observer starts only with
`OBSERVER_ENABLED=1`, refuses a production profile, and publishes no port:
the test reaches it from inside the network
(`tool-corpus/testing/in-network-e2e-harness.md`). The reset is a POST, so a
link checker or a browser prefetch cannot clear it.

**How a test uses it.** Wait for `/health` 200. Read `next` from
`/observed`. Trigger the user action through the real edge. Poll
`/observed?since=<next>&key=<expected key>` with a deadline until the command
appears, then assert its body. A deadline that passes is a failure, never a
skip. Using the cursor instead of `/reset` lets two tests run against the
same observer without clearing each other's record. With the in-network
harness the test reads:

```python
st, _ = h.get("/health", host="observer:8090"); assert st == 200, st
cursor = json.loads(h.get("/observed", host="observer:8090")[1])["next"]
h.post_json("/devices/A/open", {}, bearer=token)          # the user action, through the edge
deadline = time.monotonic() + 20
while time.monotonic() < deadline:
    got = json.loads(h.get(f"/observed?since={cursor}&key=DEVICE-A", host="observer:8090")[1])
    if got["count"]: break
    time.sleep(1)
assert got["count"] == 1 and json.loads(got["observed"][0]["body"])["op"] == "OPEN", got
```

Two observers that share one queue name split the messages between them, so
two stacks on one vhost each set their own `QUEUE`.

## 4. Portable vs blueprint

- **Reusable as written (Python plants):** the script below.
- **Blueprint (other stacks):** the declaration-equality rule, the own durable
  queue with a catch-all key, record-then-ack, the two bounds, health that
  means bound, the cursor, the fatal 406, the staging guards.
- **Project-specific (fill in):** the exchange name, type, durability and
  arguments (read from the producer's declaration, never guessed); the
  binding keys for a direct exchange; the image and the compose service, on
  the internal network with no published port. A sketch of both, built and
  run once (the observer reached health 200 as an unprivileged user):

```dockerfile
FROM python:3-alpine
RUN pip install --no-cache-dir pika
WORKDIR /app
COPY observer.py /app/observer.py
RUN adduser -D observer
USER observer
CMD ["python", "-u", "/app/observer.py"]
```

```yaml
  observer:                       # a service of the plant's compose file
    build: ./observer
    profiles: ["staging"]         # never part of the production profile
    depends_on:
      broker: { condition: service_healthy }
    environment:
      OBSERVER_ENABLED: "1"
      AMQP_URL: "amqp://broker:5672/%2F"
      AMQP_USER: "${BROKER_USER}"          # the producer's variables, raw
      AMQP_PASSWORD: "${BROKER_PASSWORD}"
      EXCHANGE: "device.commands"
      EXCHANGE_TYPE: "topic"
      EXCHANGE_DURABLE: "1"
    expose: ["8090"]              # internal only: no `ports:`
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8090/health')"]
      interval: 10s
```

```python
#!/usr/bin/env python3
"""fire-and-forget-command-observer: a staging-only stand-in for a downstream
consumer that is gone, so a command a producer publishes and forgets becomes
observable end to end.

  OBSERVER_ENABLED=1 EXCHANGE=<name> EXCHANGE_TYPE=topic EXCHANGE_DURABLE=1 \
  AMQP_URL=amqp://<user>:<password>@<broker>:5672/%2F observer.py
  observer.py --self-test          # the observation core, no broker needed

HTTP, internal network only:
  GET  /health                     200 {"status":"UP","bound":true} once the queue is
                                   bound; 503 {"bound":false} until then
  GET  /observed[?key=K][&since=N] {"count":n,"next":seq,"observed":[...]}
  POST /reset                      clears the buffer
The broker client is pika (imported only when consuming); everything else is stdlib.
"""
import json, os, re, sys, threading, time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class Buffer:
    """Bounded, thread-safe record of observed commands, oldest dropped first."""
    def __init__(self, maxlen):
        self._items = deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self._seq = 0
        self.bound = False

    def record(self, routing_key, body):
        with self._lock:
            self._seq += 1
            self._items.append({"seq": self._seq, "routingKey": routing_key,
                                "body": body, "receivedAt":
                                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})

    def query(self, key=None, since=0):
        with self._lock:
            items = [e for e in self._items if e["seq"] > since
                     and (key is None or e["routingKey"] == key)]
            return items, self._seq

    def clear(self):
        with self._lock:
            self._items.clear()


def make_handler(buf):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, payload):
            raw = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            url = urlparse(self.path)
            q = parse_qs(url.query)
            if url.path == "/health":
                self._send(200 if buf.bound else 503,
                           {"status": "UP" if buf.bound else "DOWN", "bound": buf.bound})
            elif url.path == "/observed":
                try:
                    since = int(q.get("since", ["0"])[0])
                except ValueError:
                    return self._send(400, {"error": "since must be an integer"})
                items, last = buf.query(q.get("key", [None])[0], since)
                self._send(200, {"count": len(items), "next": last, "observed": items})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            if urlparse(self.path).path == "/reset":
                buf.clear()
                self._send(200, {"status": "cleared"})
            else:
                self._send(404, {"error": "not found"})

        def log_message(self, *args):
            pass
    return Handler


def broker_params(cfg):
    """Connection parameters, built in the main thread so a malformed AMQP_URL
    refuses the start instead of killing the consumer thread."""
    import pika
    try:
        params = pika.URLParameters(cfg["amqp_url"])
    except ValueError as e:
        raise SystemExit(f"AMQP_URL is malformed ({e}); percent-encode the user and "
                         "password (@ is %40, : is %3A, / is %2F)") from None
    if cfg["amqp_user"] is not None:              # raw values, no encoding needed
        params.credentials = pika.PlainCredentials(cfg["amqp_user"], cfg["amqp_password"])
    params.heartbeat = 30
    params.blocked_connection_timeout = 30
    return params


def declare_exchange(conn, cfg):
    """Use the producer's exchange when it exists; declare it only when it does not.
    A passive declare compares nothing but the name, so it cannot fail with 406."""
    import pika
    ch = conn.channel()
    try:
        ch.exchange_declare(exchange=cfg["exchange"], passive=True)
        return ch
    except pika.exceptions.ChannelClosedByBroker as exc:
        if exc.reply_code != 404:
            raise
    ch = conn.channel()                           # the 404 closed the first channel
    # The observer declares first: this must equal what the producer will declare.
    ch.exchange_declare(exchange=cfg["exchange"], exchange_type=cfg["exchange_type"],
                        durable=cfg["exchange_durable"], auto_delete=cfg["exchange_auto_delete"],
                        arguments=cfg["exchange_args"] or None)
    return ch


def consume_forever(buf, cfg, params, stop=None):
    """Bind a durable queue to the producer's exchange and record every command.
    Reconnects with capped exponential backoff; `bound` is false while down."""
    import pika
    queue_args = {"x-max-length": cfg["queue_max"]}
    if cfg["queue_expires_ms"]:
        queue_args["x-expires"] = cfg["queue_expires_ms"]
    backoff = 2
    while not (stop and stop.is_set()):
        try:
            conn = pika.BlockingConnection(params)
            ch = declare_exchange(conn, cfg)
            ch.queue_declare(queue=cfg["queue"], durable=True, arguments=queue_args)
            for key in cfg["binding_keys"]:
                ch.queue_bind(queue=cfg["queue"], exchange=cfg["exchange"], routing_key=key)
            ch.basic_qos(prefetch_count=20)

            def on_message(c, method, _props, body):
                buf.record(method.routing_key, body.decode("utf-8", "replace"))
                c.basic_ack(delivery_tag=method.delivery_tag)   # ack after recording

            ch.basic_consume(queue=cfg["queue"], on_message_callback=on_message)
            buf.bound = True
            backoff = 2
            print(f"[observer] bound {cfg['queue']} -> {cfg['exchange']} "
                  f"{cfg['binding_keys']}", flush=True)
            ch.start_consuming()
        except (pika.exceptions.ProbableAuthenticationError,
                pika.exceptions.ProbableAccessDeniedError,
                pika.exceptions.AuthenticationError) as exc:
            buf.bound = False
            print(f"[observer] FATAL: the broker refused the login or the vhost "
                  f"({type(exc).__name__}: {exc}); check the credentials", flush=True)
            os._exit(4)                                  # a wrong password never heals
        except Exception as exc:  # keep the stand-in alive across broker churn
            buf.bound = False
            if getattr(exc, "reply_code", None) == 406:      # a declaration mismatch
                print(f"[observer] FATAL: {exc}; the exchange declaration must equal the "
                      "producer's (type, durable, auto_delete, arguments); a queue-argument "
                      "mismatch means delete the observer's queue first", flush=True)
                os._exit(3)                                  # never retry a config error
            print(f"[observer] broker connection lost ({type(exc).__name__}: {exc}); "
                  f"retrying in {backoff}s", flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)


PROD = re.compile(r"(?<![a-z])prod(uction)?(?![a-z])")
EXCHANGE_TYPES = ("direct", "fanout", "topic", "headers")


def config(env):
    if env.get("OBSERVER_ENABLED") != "1":
        raise SystemExit("observer is off: set OBSERVER_ENABLED=1 (staging only)")
    if PROD.search(env.get("DEPLOY_PROFILE", "").lower()):
        raise SystemExit("refusing to start: DEPLOY_PROFILE looks like production")
    for need in ("AMQP_URL", "EXCHANGE", "EXCHANGE_TYPE", "EXCHANGE_DURABLE"):
        if not env.get(need):
            raise SystemExit(f"{need} must be set; copy it from the producer's declaration")
    etype = env["EXCHANGE_TYPE"]
    if etype not in EXCHANGE_TYPES and not etype.startswith("x-"):
        raise SystemExit(f"EXCHANGE_TYPE {etype!r} is not one of {', '.join(EXCHANGE_TYPES)} "
                         "or a plugin type starting with x-")
    flags = {}
    for var, default in (("EXCHANGE_DURABLE", None), ("EXCHANGE_AUTO_DELETE", "0")):
        value = env.get(var, default)
        if value not in ("0", "1"):
            raise SystemExit(f"{var} must be 0 or 1, not {value!r}")
        flags[var] = value == "1"
    try:
        exchange_args = json.loads(env.get("EXCHANGE_ARGS", "{}"))
        assert isinstance(exchange_args, dict)
    except (ValueError, AssertionError):
        raise SystemExit("EXCHANGE_ARGS must be a JSON object") from None
    if ("AMQP_USER" in env) != ("AMQP_PASSWORD" in env):
        raise SystemExit("set AMQP_USER and AMQP_PASSWORD together, or neither")
    return {"amqp_url": env["AMQP_URL"], "exchange": env["EXCHANGE"],
            "amqp_user": env.get("AMQP_USER"), "amqp_password": env.get("AMQP_PASSWORD"),
            "exchange_type": etype,
            "exchange_durable": flags["EXCHANGE_DURABLE"],
            "exchange_auto_delete": flags["EXCHANGE_AUTO_DELETE"],
            "exchange_args": exchange_args,
            "queue": env.get("QUEUE", env["EXCHANGE"] + ".observer"),
            "binding_keys": env.get("BINDING_KEYS", "#").split(","),
            "queue_max": int(env.get("QUEUE_MAX", "10000")),
            "queue_expires_ms": int(env.get("QUEUE_EXPIRES_MS", "0")),
            "buffer_max": int(env.get("BUFFER_MAX", "1000")),
            "http_bind": env.get("HTTP_BIND", "0.0.0.0"),
            "http_port": int(env.get("HTTP_PORT", "8090"))}


def self_test():
    import urllib.request, urllib.error
    buf = Buffer(maxlen=3)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(buf))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}"

    def call(path, method="GET"):
        req = urllib.request.Request(base + path, method=method, data=b"" if method == "POST" else None)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    assert call("/health") == (503, {"status": "DOWN", "bound": False}), "UP before bound"
    buf.bound = True
    assert call("/health")[0] == 200
    for i in range(5):
        buf.record("DEVICE-A" if i % 2 == 0 else "DEVICE-B", f'{{"op":"OPEN","n":{i}}}')
    st, got = call("/observed")
    assert [e["seq"] for e in got["observed"]] == [3, 4, 5], f"not bounded: {got}"
    st, got = call("/observed?key=DEVICE-A")
    assert [e["seq"] for e in got["observed"]] == [3, 5], got
    st, got = call("/observed?since=4")
    assert [e["seq"] for e in got["observed"]] == [5] and got["next"] == 5, got
    assert call("/observed?since=x")[0] == 400
    assert call("/reset")[0] == 404, "a GET must not clear the buffer"
    assert call("/observed")[1]["count"] == 3
    assert call("/reset", "POST")[0] == 200 and call("/observed")[1]["count"] == 0
    good = {"OBSERVER_ENABLED": "1", "AMQP_URL": "amqp://x", "EXCHANGE": "e",
            "EXCHANGE_TYPE": "topic", "EXCHANGE_DURABLE": "1"}
    assert config(good)["exchange_durable"] is True
    assert config({**good, "DEPLOY_PROFILE": "nonprod-staging"})["exchange_args"] == {}
    assert config({**good, "EXCHANGE_TYPE": "x-delayed-message"})["exchange_auto_delete"] is False
    for bad in ({}, {**good, "DEPLOY_PROFILE": "Production"}, {**good, "DEPLOY_PROFILE": "eu-prod"},
                {k: v for k, v in good.items() if k != "EXCHANGE_DURABLE"},
                {**good, "EXCHANGE_DURABLE": "true"}, {**good, "EXCHANGE_TYPE": "Topic"},
                {**good, "EXCHANGE_AUTO_DELETE": "yes"}, {**good, "EXCHANGE_ARGS": "[1]"},
                {**good, "AMQP_USER": "u"}):
        try:
            config(bad)
        except SystemExit:
            pass
        else:
            raise AssertionError(f"started with {bad}")
    srv.shutdown()
    print("self-test: PASS (health 503 until bound, bounded buffer, key filter, since"
          " cursor, reset is POST only, default-off, production refusal by token,"
          " declaration required and checked)")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    cfg = config(os.environ)
    params = broker_params(cfg)
    buf = Buffer(cfg["buffer_max"])
    threading.Thread(target=consume_forever, args=(buf, cfg, params), daemon=True).start()
    print(f"[observer] observation endpoint on {cfg['http_bind']}:{cfg['http_port']}", flush=True)
    ThreadingHTTPServer((cfg["http_bind"], cfg["http_port"]), make_handler(buf)).serve_forever()
```

Recorded runs. The self-test, offline:

```text
$ python3 observer.py --self-test
self-test: PASS (health 503 until bound, bounded buffer, key filter, since cursor, reset is POST only, default-off, production refusal by token, declaration required and checked)
```

Against a RabbitMQ 4 broker in a container (user password `p@ss:w/rd`,
symbols on purpose), with a synthetic producer that declares a durable topic
exchange and publishes `{"op": "OPEN", "k": <key>}` under the given keys. The
observer ran with the percent-encoded `AMQP_URL` unless a line says
otherwise:

```text
$ curl -s -w ' %{http_code}' http://127.0.0.1:18091/health
{"status": "UP", "bound": true} 200
$ python3 producer.py DEVICE-A device.b.start
$ curl -s 'http://127.0.0.1:18091/observed?key=DEVICE-A'
{"count": 1, "next": 2, "observed": [{"seq": 1, "routingKey": "DEVICE-A", "body": "{\"op\": \"OPEN\", \"k\": \"DEVICE-A\"}", "receivedAt": "…"}]}
$ curl -s 'http://127.0.0.1:18091/observed?since=1'
{"count": 1, "next": 2, "observed": [{"seq": 2, "routingKey": "device.b.start", …}]}
GET /reset -> 404 ; POST /reset -> 200 ; GET /observed -> {"count": 0, "next": 2, "observed": []}

# broker restarted under a running observer
GET /health -> 503 {"status": "DOWN", "bound": false}
[observer] broker connection lost (ConnectionClosedByBroker: (320, "CONNECTION_FORCED - broker forced connection closure with reason 'shutdown'")); retrying in 2s
[observer] broker connection lost (IncompatibleProtocolError: StreamLostError: ('Transport indicated EOF',)); retrying in 4s
[observer] bound device.commands.observer -> device.commands ['#']        # then /health 200

# observer stopped, one command published, observer started again
{"count": 1, "next": 1, "observed": [{"seq": 1, "routingKey": "WHILE-DOWN", …}]}

# exchange already declared by the producer: the passive declare binds, whatever the settings
EXCHANGE_DURABLE=0 against the durable exchange           -> bound
producer exchange with {"alternate-exchange": "unrouted"} -> bound
producer exchange with auto_delete=true                   -> bound
# the same two exchanges declared actively with type and durability only (why passive comes first)
(406, "PRECONDITION_FAILED - inequivalent arg 'alternate-exchange' for exchange 'ae.commands' in vhost '/': received none but current is the value 'unrouted' of type 'longstr'")
(406, "PRECONDITION_FAILED - inequivalent arg 'auto_delete' for exchange 'ad.commands' in vhost '/': received 'false' but current is 'true'")

# exchange missing: the observer declares it with EXCHANGE_DURABLE=0, then the producer declares it durable
pika.exceptions.ChannelClosedByBroker: (406, "PRECONDITION_FAILED - inequivalent arg 'durable' for exchange 'fresh.commands' in vhost '/': received 'true' but current is 'false'")

# QUEUE_MAX=5 against the existing observer queue                      (exit 3)
[observer] FATAL: (406, "PRECONDITION_FAILED - inequivalent arg 'x-max-length' for queue 'device.commands.observer' in vhost '/': received '5' but current is '10000'"); the exchange declaration must equal the producer's (type, durable, auto_delete, arguments); a queue-argument mismatch means delete the observer's queue first
# AMQP_URL with the raw password                                        (exit 1)
AMQP_URL is malformed (Port could not be cast to integer value as 'w'); percent-encode the user and password (@ is %40, : is %3A, / is %2F)
# the same raw password in AMQP_USER / AMQP_PASSWORD                   -> bound
# wrong password, and a vhost that does not exist                      (exit 4, both)
[observer] FATAL: the broker refused the login or the vhost (ProbableAuthenticationError: ConnectionClosedByBroker: (403) 'ACCESS_REFUSED - Login was refused using authentication mechanism PLAIN. For details see the broker logfile.'); check the credentials
# EXCHANGE_DURABLE=true                                                 (exit 1)
EXCHANGE_DURABLE must be 0 or 1, not 'true'
```

## 5. Pitfalls and sharp edges

- **Client defaults are not the producer's declaration.** `pika`'s
  `exchange_declare` defaults to `exchange_type="direct"` and
  `durable=False`. A producer framework often declares durable exchanges, so
  an exchange declared from the defaults fails with 406. Copy each value from
  the producer's code or from the broker's exchange list.
- **A 406 or a refused login retried forever looks like a slow broker.** A
  declaration mismatch and a wrong password are both deterministic; the
  observer exits (`3`, `4`) instead of looping, and the health check stays
  503 until it is fixed.
- **A password with `@`, `:` or `/` breaks a hand-built `AMQP_URL`.** The
  URI grammar allows only unreserved characters, sub-delimiters and
  percent-encoded octets in the user and password. A raw `p@ss:w/rd` does not
  parse (`Port could not be cast to integer`). Percent-encode it, or pass
  `AMQP_USER` and `AMQP_PASSWORD`.
- **A passive declare does not check the settings.** When the producer's
  exchange exists, a wrong `EXCHANGE_TYPE` or `EXCHANGE_DURABLE` goes
  unnoticed until the day the observer starts first and declares the
  exchange, and then the producer fails with 406. Copy the values anyway.
- **Binding to the real consumer's queue steals its messages.** Consumers on
  one queue share its messages round-robin. The observer always declares its
  own queue.
- **`#` matches nothing on a direct exchange.** On a direct exchange the
  binding key is compared literally. List the keys.
- **The record is in memory.** It is bounded and lost on restart. It is a
  test-observation surface, not a store of record; the durable queue covers
  only the restart window.
- **A durable queue with no consumer grows without limit.** Set `QUEUE_MAX`,
  and `QUEUE_EXPIRES_MS` or delete the queue when the observer is retired.
- **A stand-in pinned to nothing hides drift.** The observer records what
  the producer sends; nothing checks that the retired consumer would have
  accepted it. Record the command shape the consumer documented (its
  contract) beside the test, and say in the test that it is pinned to that
  record, because nothing else can cross-check it.
- **Never in production, never published.** Default-off is not enough on its
  own; the observer also refuses a production profile. The client library
  lives only in the observer's image and is not a dependency of any
  production service.

## 6. Tests that cover it

`observer.py --self-test` starts the HTTP surface on a free local port with a
buffer of three and asserts: `/health` is 503 until bound and 200 after;
five records keep only the newest three; `?key=` filters; `?since=` returns
only later entries and a non-integer is 400; a GET on `/reset` is 404 and
does not clear; a POST clears; the start is refused when not enabled, under a
production profile (`Production`, `eu-prod`, but not `nonprod-staging`), with
a declaration variable missing, with `EXCHANGE_DURABLE=true`, an unknown
exchange type, a non-0/1 `EXCHANGE_AUTO_DELETE`, an `EXCHANGE_ARGS` that is
not a JSON object, and an `AMQP_USER` without `AMQP_PASSWORD`; a plugin type
starting with `x-` is accepted.

The broker behaviour (binding, delivery, retention over a restart, the
passive declare, the 406 and 403 exits, URL parsing) is covered by the live
run in §4. A
plant re-runs it once against its own broker before trusting the observer.

- **How to run the tests:** `python3 observer.py --self-test`; then the live
  sequence in §4 against a throwaway broker container.

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/in-network-e2e-harness.md` (the
  in-network client that polls `/observed`);
  `tool-corpus/testing/behavior-baseline-oracle.md` (a command shape read from
  `/observed` can be a `shape`-mode surface).
- **Library pages:** `library-corpus/pypi/pika.md`,
  `library-corpus/maven/rabbitmq.md`,
  `library-corpus/maven/spring-cloud-stream.md` (its Rabbit binder),
  `library-corpus/nuget/RabbitMQ.Client.md`,
  `library-corpus/nuget/MassTransit.RabbitMQ.md`.
- **Sources:** distilled from practice (a device stand-in
  used by a live command-path test); AMQP 0-9-1 specification
  (https://www.rabbitmq.com/resources/specs/amqp0-9-1.extended.xml,
  `exchange.declare` and `queue.declare` rules); RabbitMQ docs
  https://www.rabbitmq.com/docs/queues (property equivalence, 406),
  https://www.rabbitmq.com/docs/exchanges (topic `#`),
  https://www.rabbitmq.com/docs/ttl (`x-expires`),
  https://www.rabbitmq.com/docs/maxlength (`x-max-length`, `drop-head`),
  https://www.rabbitmq.com/docs/uri-spec (user and password encoding);
  pika `BlockingChannel` reference
  (https://pika.readthedocs.io/en/stable/modules/adapters/blocking.html).

## 8. Changelog

- 2026-10-05 — created from a device stand-in, generalized: the
  exchange declaration became required configuration instead of defaults,
  a 406 exits instead of looping, health reports the binding instead of
  always UP, reset moved from GET to POST, a `since` cursor and a broker-side
  queue cap and expiry were added, and the start is default-off with a
  production refusal; by tool-smith.
- 2026-10-05 — review fixes: the exchange is declared passively first and
  actively only when missing, with `EXCHANGE_AUTO_DELETE` and `EXCHANGE_ARGS`
  for that case; `AMQP_URL` is parsed before the consumer starts, with
  `AMQP_USER` and `AMQP_PASSWORD` as the raw-value alternative; a refused
  login exits `4`; the 406 message names the queue case; the declaration
  variables are validated and the production check matches whole words; §3
  gained a test snippet, §4 an image and compose sketch, and `stack:` the
  MassTransit and Spring Cloud Stream pages; the live run was redone; by
  tool-smith.
