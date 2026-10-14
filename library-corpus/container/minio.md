# minio — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile / base-image tag.

## What it is
MinIO is an S3-compatible object storage server written in Go, released under
the GNU AGPLv3. In a containerized stack it runs as one service holding
buckets of objects on a data directory, answering the S3 API on one port and
serving a web UI on a second. Applications reach it with any S3 client (the
JavaScript one is [`npm/aws-sdk-client-s3`](../npm/aws-sdk-client-s3.md));
administration goes through MinIO's own client, `mc` (also shipped as the
image `minio/mc`), a command-line tool for buckets, objects, users and policies
against any S3-compatible endpoint. The page is keyed by the server image
`minio` (`minio/minio` on Docker Hub, `quay.io/minio/minio`); the `mc` image is
covered here but deliberately not an own-package item, because the bare name
`mc` would propose this page for unrelated images of that name.

Upstream home: the source at https://github.com/minio/minio, the community
documentation at https://docs.min.io/community/minio-object-store/ (its source
at https://github.com/minio/docs).

**Distribution status, as the vendor states it.** The `minio/minio`
repository is archived and its README opens with "THIS REPOSITORY IS NO LONGER
MAINTAINED", pointing to the commercial AIStor editions as the alternatives.
The README also says the community edition is distributed as source code
only: pre-compiled binaries are no longer provided, the historical binaries
"will not receive updates", and users build from source (`go install`) or
build their own image from the repository's `Dockerfile`. The last community
release's notes tell container users to clone the source and build the image.
When this page was researched, the Docker Hub repositories `minio/minio` and
`minio/mc` answered "not found" and `quay.io/minio/minio` refused an anonymous
pull; the vendor has published no statement about the registries. A project
that pulls either image by name should treat it as a dependency that may no
longer resolve, and mirror what it runs.

## Install, setup and configuration
- **Run shape.** `minio server /data --console-address ":9001"`: the S3 API on
  port 9000 and the web UI on 9001. Without `--console-address` the UI listens
  on a random port. `/data` is the data path and belongs on a volume or a
  dedicated drive; upstream warns that data on an ephemeral container path is
  lost when the container restarts or is deleted.
- **Topology.** A single container is a single-node deployment
  (single-drive, or multi-drive with numbered paths such as
  `/mnt/drive-{1...4}`); upstream positions container deployments for early
  development and evaluation, supports distributed (multi-node) MinIO in
  containers only on Kubernetes through its Operator, and does not support or
  document distributed clusters on Docker Compose or Swarm. Erasure-coding
  parity is chosen from the topology at setup, and objects keep the parity
  they were written with.
- **Root credentials.** `MINIO_ROOT_USER` (the access key) and
  `MINIO_ROOT_PASSWORD` (the secret key) of the root user, environment only.
  Both default to `minioadmin` when unset. `MINIO_API_ROOT_ACCESS=off`
  disables the root account for API use (root credentials must still be set);
  disabling it without another admin user locks administration out until it
  is set back to `on`.
- **Addressing.** `MINIO_DOMAIN` set to the server's fully qualified name
  enables virtual-host-style requests (`<bucket>.<domain>`); without it the
  server accepts only path-style requests (`<host>/<bucket>/<key>`). With it
  set, every subdomain of that name is reserved for bucket names.
- **UI.** `MINIO_BROWSER=off` disables the embedded UI.
- **Images.** Upstream images are built on Red Hat UBI micro; an image built
  from the repository's `Dockerfile` expects a `minio` binary built first in
  the project root.

## Core API / usage shape
- **S3 API.** Buckets and objects through standard S3 operations (`PutObject`,
  `GetObject`, `DeleteObject`, `ListObjectsV2`, multipart upload, presigned
  URLs). Clients point a custom endpoint at port 9000 and enable path-style
  addressing unless `MINIO_DOMAIN` is configured and resolvable.
- **`mc` client.** `mc alias set <alias> <url> <access-key> <secret-key>`
  stores a target; then `mc mb <alias>/<bucket>` (`-p`/`--ignore-existing` to
  succeed when it exists, `--with-lock` for object locking), `mc cp`,
  `mc ls`, `mc mirror`, and `mc admin info <alias>`.
- **Identity and policy.** `mc admin user add` creates a user;
  `mc admin policy attach <alias> <policy> --user <user>` grants a policy (the
  built-ins are `readonly`, `readwrite`, `writeonly` and `diagnostics`; the
  docs name `consoleAdmin` as the policy of an admin user); `mc admin accesskey create <alias> <user>` issues an access
  and secret key pair for a user, optionally narrowed by a policy file and
  given an expiry.
- **Anonymous access.** `mc anonymous set <none|download|upload|public>
  <alias>/<bucket>[/<prefix>]` sets an unauthenticated policy on a bucket or
  prefix.
- **Health.** `/minio/health/live` (node online), `/minio/health/cluster`
  (write quorum; `503` without it) and `/minio/health/cluster/read` (read
  quorum) answer with a status code only and need no authentication.

## Idioms & best practices
- **Pin the exact `RELEASE.` tag, or better, a digest of an image you build.**
  MinIO tags its releases `RELEASE.<UTC timestamp>` with no semantic version
  and no stable channel, so a floating tag such as `latest` moves to whatever
  was built last, and nothing in the tag says whether a step is compatible.
  Now that the community edition ships as source only, the reproducible form
  is an image the project builds from a tagged commit and stores in its own
  registry.
- **Never run with the default root credentials**, in any environment. Set a
  long random `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from a secret, and
  use root only to create users and policies.
- **Give each application its own user or access key** with a policy scoped to
  its bucket (or a custom policy narrower than `readwrite`), so a leaked
  application key cannot reach other buckets or administer the server.
- **Create buckets and policies from automation with `mc`**, idempotently
  (`mc mb --ignore-existing`), in a one-shot job that runs after the server is
  healthy.
- **Keep path-style addressing unless there is DNS for bucket subdomains.**
  Configure every client with the endpoint and path-style together.
- **Serve public reads deliberately.** Either a narrow `mc anonymous set
  download` on a prefix, presigned URLs, or a proxy in front; never `public`
  on a bucket holding anything else.
- **Plan for the maintenance status.** The community line receives no further
  releases from the vendor; record that in the project's dependency page and
  keep the store behind the S3 API so another S3-compatible server can replace
  it without touching application code.

## General pitfalls
- **A client left on virtual-host addressing fails against a default server.**
  The server accepts only path-style requests until `MINIO_DOMAIN` is set, so
  an S3 client with its default addressing resolves `<bucket>.<host>` and gets
  DNS errors or 404s (the AWS SDK's `forcePathStyle` defaults to `false`).
- **The embedded console lost its administration features.** MinIO's release
  notes deprecated the embedded UI console and moved it to the separate
  object-browser project, and removed external identity-provider logins
  (LDAP, OIDC) from the UI, which moved to AIStor; the STS APIs still work.
  Later community builds keep an object browser, so user, policy and server
  administration that used to be done in the UI now goes through `mc admin`.
  Treat the UI as a development convenience and keep administration in `mc`
  scripts.
- **Default credentials are public knowledge.** A server started without
  `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` accepts `minioadmin`/`minioadmin`
  for full administrative access on both ports.
- **A random UI port.** Without `--console-address` the UI port changes at
  every start, which breaks a published port mapping.
- **Data on an ephemeral container path is lost** when the container
  restarts or is deleted; mount `/data`.
- **Image names that no longer resolve.** A compose file or test that pulls
  `minio/minio` or `minio/mc` from a public registry can start failing without
  any change on the project side (see the distribution status above).
- **Parity is fixed per object.** Changing erasure-code parity later does not
  rewrite existing objects.

## Testing
- Run the same image (same tag or digest) in tests as in deployment, with the
  client configured exactly as deployed (endpoint, path-style, credentials,
  checksum settings), so addressing and integrity-header mismatches appear in
  the suite.
- Wait on `/minio/health/live` before creating buckets; create them with `mc`
  in the test setup.
- Assert from outside that an anonymous request to a private bucket is denied
  and that an application key cannot reach another bucket or run admin
  commands.

## Security defaults
- Root user and password default to `minioadmin` when unset: full control of
  the deployment to anyone who reaches the port.
- The documented container run serves plain HTTP; without TLS configured,
  S3 signatures still protect request integrity, but object contents and UI
  logins cross the network in clear text.
- A bucket answers only authenticated requests until an anonymous policy is
  set; `mc anonymous set upload|download|public` opens a bucket or prefix to
  unauthenticated writes, reads or both.
- Health endpoints are unauthenticated by design and expose only a status
  code.
- The UI is on by default (`MINIO_BROWSER=off` disables it); expose it only on
  a private network.

## Operational behaviour
- Starts serving on the data path at once; a single-node deployment has no
  redundancy beyond its drives' erasure coding, and a single-drive one has
  none.
- The liveness probe shows that the node is reachable, not that the cluster is
  healthy; upstream recommends metrics-based alerts for offline nodes and free
  drive space.
- The vendor provides no further community releases, so fixes reach a
  community deployment only through the project's own build from source.

## Interop
- S3 clients: [`npm/aws-sdk-client-s3`](../npm/aws-sdk-client-s3.md) needs
  `endpoint` plus `forcePathStyle: true`, and its default checksum behaviour
  should be checked against the server version in use.
- Compose health gating and secrets: [`docker-compose.md`](docker-compose.md).
- Metrics: MinIO exposes Prometheus metrics for alerting; see
  [`prometheus.md`](prometheus.md).

## Major lines
- MinIO has no semantic major lines: each release is a `RELEASE.` timestamp
  tag. The boundary that matters is the console change described in the
  pitfalls (the embedded UI deprecated, object-browser only, external
  identity logins removed) and the move of the community edition to
  source-only distribution, after which the repository was archived.

## Upstream docs
- https://github.com/minio/minio (README: maintenance notice, source-only
  distribution, default credentials, `mc` quickstart)
- https://github.com/minio/minio/releases (console deprecation; build-your-own
  container instructions)
- https://docs.min.io/community/minio-object-store/
- https://github.com/minio/docs/blob/main/source/reference/minio-server/settings/root-credentials.rst
- https://github.com/minio/docs/blob/main/source/reference/minio-server/settings/core.rst (`MINIO_DOMAIN`)
- https://github.com/minio/docs/blob/main/source/reference/minio-server/settings/console.rst
- https://github.com/minio/docs/blob/main/source/operations/deployments/baremetal-deploy-minio-as-a-container.rst
- https://github.com/minio/docs/blob/main/source/operations/monitoring/healthcheck-probe.rst
- https://github.com/minio/docs/tree/main/source/reference/minio-mc and
  `minio-mc-admin` (`mc mb`, `mc anonymous set`, `mc admin policy attach`,
  `mc admin accesskey create`)
