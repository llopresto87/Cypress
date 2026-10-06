# Suggested skill: characterize-undocumented-device-protocol

> Optional procedure: a project has to drive a device or service through a
> protocol its vendor does not document (a binary TCP command set, a web UI's
> private endpoints, a serial framing), reconstructed from public
> implementations and from the device itself. **Composes**
> `skills/research-and-ingest/SKILL.md` (source ranking and the conflict
> rule), `protocols/specify.md` (the spec each new capability gets),
> `protocols/test-first.md` (the offline RED), `protocols/verify.md` (what a
> gate proves), `core/method/restrictive-policy.md` (a write sits behind an
> explicit flag), `core/method/contract-posture.md` (§3: an unversioned
> contract has one document) and `core/method/stewardship-posture.md` (§3:
> synthetic data, and §1: record the decision and its evidence) by reference.
> What it adds is the order in which an unknown wire format becomes trusted,
> with the device touched as little and as late as possible.

**Instantiate by supplying:** `<DEVICE>` (the device family and the
firmware or release line in play), `<CHANNEL_A>` (the undocumented protocol
being adopted), `<CHANNEL_B>` (an independent channel that reports at least
one of the same facts: a web UI, a second protocol, a label on the device),
`<READ_COMMAND>` (a command on `<CHANNEL_A>` that only reads, ideally an
identity such as a serial number), `<WRITE_COMMAND>` (the first command that
changes state), `<SOURCES>` (the public implementations found), and
`<PROTOCOL_DOC>` (the plant's one document for this protocol, under its API
or integration notes).

## When to apply

- The capability the project needs exists only on a channel the vendor does
  not document, and the documented channel cannot do it.
- Community SDKs, reference implementations or security advisories describe
  the protocol, and none of them is authoritative.
- A previous attempt "worked once" and nobody can say why.

Stop before step 1 when the device's owner has not authorized the work, or
when the only route to the protocol is defeating an access control. This
procedure reads public sources and talks to devices the project is allowed
to manage. It does not break in.

## 1. Discover by fingerprint, without logging in

Find candidate devices by what they answer without credentials: which ports
are open, and what an unauthenticated request returns (a banner, a fixed
error body). Compare that signature with a unit the project already knows.
Do not attempt a login, a default credential or a command at this stage. A
matching fingerprint says "same family", and nothing more about firmware or
configuration.

Record each candidate with the evidence that matched and the evidence that
excluded the near misses (a host that answers HTTP but lacks the second port
is not the device).

## 2. Corroborate the framing from at least two independent sources

Before any contact on `<CHANNEL_A>`, collect `<SOURCES>`: SDKs in other
languages, reference implementations, packet captures published with an
advisory. Rank and reconcile them by `skills/research-and-ingest/SKILL.md`.
Two rules specific to protocols:

- **Code beats prose.** When a README and its own code disagree (byte order is
  the usual one), the code is what was run against a device. Take the code,
  and check whether a second implementation agrees.
- **A source can corroborate part of the protocol.** An advisory for an older
  model may share the command codes and differ in framing. Record exactly
  what each source supports, field by field.

Write the result into `<PROTOCOL_DOC>` before writing code: the frame layout
(start byte, address, command, length, payload, checksum), each field's width
and byte order, which bytes the checksum covers (does it include the start
byte?), and the checksum's own byte order. That order can differ from the
other fields in the same frame: a checksum sent low byte first in a frame
whose address and length go high byte first is not rare. Also record how a
response differs from a request (an echoed command plus a fixed offset is
common), how success is signalled, and any unsolicited frame the device can
send (a keepalive that needs a reply, or the connection stalls). Cite the
source of every line.

A published example frame that carries its checksum can settle a byte-order
dispute between sources. Recompute the checksum over the example under each
candidate field order. Usually only one reading matches, and that reading is
the one the example's author sent.

**Identify a checksum by its parameters, not by its name.** A CRC is fully
defined by width, polynomial, initial value, input and output reflection,
and final XOR, and the catalogue check value is its output over the ASCII
bytes `123456789` (the CRC RevEng catalogue lists these per algorithm). Names
collide: two 16-bit CRCs that differ only in the final XOR have different
names and different check values (in that catalogue, CRC-16/MCRF4XX checks to
`0x6F91` and CRC-16/IBM-SDLC, also called X-25, to `0x906E`). An
implementation's comment can name one and compute the other. The polynomial
has two spellings too. The catalogue writes it in normal form (`0x1021`),
and a reflected table implementation carries the bit-reversed constant
(`0x8408`). Both are the same polynomial. Record the parameter set and the
check value, and test against the check value.

## 3. Write the offline tests first

The codec (frame building, frame parsing, checksum) is pure logic: test it
with no device and no network (`protocols/test-first.md`). The suite holds:

- **The checksum against an independent reference.** A table-driven
  implementation is checked against a plain bit-by-bit loop over several
  inputs (empty, one byte, all 256 byte values), and against the catalogue
  check value.
- **Byte-exact request frames.** For each command the plant will send, the
  exact bytes the builder must produce.
- **Field-order tests** for every multi-byte field (address, length), with
  values whose bytes all differ, so a swapped order cannot pass.
- **Rejection tests**: a wrong start byte, a corrupted checksum, a frame cut
  short. Each must raise, never return a partial result.
- **Unsolicited frames**: a keepalive in the stream is recognized and does not
  get parsed as the answer. The parser consumes the whole frame (length,
  payload and checksum) and checks its checksum, so the frame's tail cannot
  desync the next read. Take the fixture's shape from a reference
  implementation or a capture, not from the parser under test: a fixture
  built to match the parser hides a parser that stops after the length.

A response fixture built by the code under test proves only that the code
agrees with itself. Anchor the suite with frames captured from a real device
(step 4) as soon as they exist, and keep the independent checksum reference,
so a shared bug in builder and parser cannot pass.

## 4. The first live call reads, and is checked on another channel

The first contact on `<CHANNEL_A>` is `<READ_COMMAND>`, a command that only
reads. Then cross-validate its answer against `<CHANNEL_B>`: the serial number
the new protocol returns must equal the one the web UI or the label reports.
One fact, two independent channels: when they agree, the framing and checksum
are right, and that is stronger than a successful exchange alone.

When the two channels disagree, stop. The framing, a byte order or the
checksum is suspect. Return to step 2, and send nothing that writes until the
read agrees.

Capture the request and response bytes of this call and add them to the
offline suite as fixtures, with real identifiers replaced by synthetic ones
where they are personal or site-specific (`stewardship-posture.synthetic-data-only`).

## 5. The first write is behind `apply=false`, and the no-op is proven

Implement `<WRITE_COMMAND>` behind a flag whose default is `false`
(`core/method/restrictive-policy.md`). A dry-run mode the tool offers is a
no-op too. Run it first with the flag off and prove that run is a true no-op:
nothing is sent on `<CHANNEL_A>`, and the run reports no change. Prove it
offline with a transport stub that fails the test if anything is sent, and
once live by the run report. Then run it with the flag on, once, against one
device, with someone watching the physical effect, and record the device's
acknowledgement and the observed effect side by side.

The write fails loudly when it does not succeed:

- A non-success return code fails the run, with the code in the message. It
  is never reported as success.
- A malformed frame, a checksum mismatch, a refused connection and a timeout
  each fail with a clear message.
- A refusal path never observed live stays an open acceptance item in the
  spec. It is not a silent pass.

A one-shot action (a relay pulse, a door release) has no state to read back
and converge. The spec says so, and the run reports a change on each
acknowledged send.

## 6. Record the security posture as a finding

An undocumented protocol often has no authentication and no encryption. Test
what it accepts without credentials, and record the result as a security
finding with its reach ("anything with network access to this port can do X")
and the mitigation (restrict the port to the control host's management
network; treat it like an unauthenticated administrative shell). Do not
implement a protocol-level lock you have not tested, such as a connection
password: setting one can lock out the automation that already depends on the
device.

## 7. Keep a "deliberately not implemented" list

`<PROTOCOL_DOC>` lists every command the sources document that the plant
does not implement, and why. A later request for one of them is a new
capability with its own spec (`protocols/specify.md`), never a drive-by
addition to a working codec. If the spec was written after the code (a
common outcome of a first exploration), mark it back-written.

## 8. Re-verify on every firmware change

The protocol's behaviour is the firmware's behaviour. After any firmware or
release change, rerun step 4 (read and cross-validate) before trusting a
write, and re-measure every limit the plant encoded.

## Pitfalls

- **A documented limit is a measurement.** A page-size cap or a field width
  written in a community source, or in the plant's own notes, can be wrong, and
  wrong in the unsafe direction. Re-measure it on the device, and page to the
  total the device reports instead of assuming one page. A hard-coded page size
  truncates a larger population without an error.
- **A validator inferred from the sample encodes the sample.** When early
  examples all share one width, a rule of that width rejects the first wider
  real value, or a device that drops leading zeros. Derive the rule from the
  domain, or widen it on the first contrary evidence.
- **A refusal is evidence about the request.** A request that failed on the
  client side (a malformed frame, a local file the client tried to read) says
  nothing about the device. Confirm a request reached the device before
  recording what the device refused.
- **The device's address in a response can differ from the request.** Some
  protocols accept a wildcard address in a request and echo the real one in
  the response. Parse the response's address; do not assert it equals what
  was sent.

## Reference files

- `skills/research-and-ingest/SKILL.md` (ranking and reconciling sources)
- `protocols/specify.md` (a spec per capability; back-written status)
- `protocols/test-first.md` (offline RED before the live call)
- `protocols/verify.md` (what a passing gate does and does not prove)
- `core/method/restrictive-policy.md` (writes behind an explicit flag)
- `core/method/contract-posture.md` (§3, one document per unversioned
  contract)
- `core/method/stewardship-posture.md` (§1 evidence, §3 synthetic data)
- Upstream: the CRC RevEng catalogue of parametrised CRC algorithms
  (reveng.sourceforge.io/crc-catalogue/)
