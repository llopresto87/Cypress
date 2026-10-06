# docker-host-hardening — container

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). The hardening floor for a Linux host that runs
> Docker workloads. Orientation, NOT a version-pinned runbook. For exact package
> versions and CVEs, ingest against the host's actual release. Durable surface =
> *what* to harden and *why*; the exact command for each is the plant's to pin.

## What it is
A container host has two attack surfaces most app-security checklists miss: the
**host OS** itself (SSH, users, firewall, updates) and the **Docker daemon**,
which by default is a root-equivalent control plane. Hardening the host is a
precondition of any deploy onto it: a hardened image on an open host is a soft
target. This page is the standing floor a bring-up brings the host to before
the first `compose up`, re-runnable idempotently.

This page owns **what** each control is and **why** it matters. Applying the
floor in order, and gating each control on evidence that it is actually active,
is a *procedure* and belongs to `skill-corpus/harden-docker-host.md`, which
composes this page rather than restating it. Read this to understand a control;
run that to install one.

## Install, setup and configuration
- **Users & SSH.** No routine work as `root`; a non-root deploy user with
  scoped `sudo`. SSH is **key-only** (`PasswordAuthentication no`) with
  `PermitRootLogin prohibit-password`: root logs in by public key, root
  password login is off. Run a maintained OpenSSH. Key auth, not passwords,
  everywhere.
- **Automatic security updates.** Unattended security upgrades enabled for the
  OS; base images and the engine kept on a supported (non-EOL) line.
- **User-namespace remapping** (`userns-remap` in `daemon.json`) makes
  container root differ from host root. The subordinate UID and GID ranges
  must belong to an existing user, and upstream advises turning it on for a
  new installation. Remapped root cannot reach host paths owned by host UIDs,
  so bind mounts and existing volumes can turn unreadable: test against the
  live volumes before switching. On the Engine 29 line, a `userns-remap` host
  cannot use the containerd image store and keeps the classic one.
- **Log rotation.** The default `json-file` log driver performs no rotation:
  set `log-opts` `max-size` and `max-file` (string values, for example `"10m"`
  and `"3"`) in `daemon.json`, or use the `local` driver, which rotates by
  default.

## Core API / usage shape
- **Prove the confinement is on.** `docker info --format
  '{{json .SecurityOptions}}'` lists the active security options (for example
  `name=apparmor`, `name=seccomp,profile=…`, and userns or rootless where
  chosen). Observed in practice: nesting or relaxed profiles dropped entries
  silently, so check the list after every host or engine change, off-host if
  possible.
- **Disk hygiene.** Reclaim with `docker builder prune` + image/container/
  network prune; **never `--volumes`** (that is the persistent data).

## Idioms & best practices
- **Firewall: default-deny, but an operator choice.** A host firewall
  (ufw/nftables) that denies inbound by default and opens **only the edge** the
  fleet publishes is the goal, but it is the one control that can lock out
  access or collide with an **upstream firewall** (the hypervisor / LXC host, a
  cloud security group), so applying it is an operator decision, not automatic
  (gate it on explicit sign-off, from an out-of-band session). Its always-on
  complement, **not** optional, is loopback binding (below): even with no host
  firewall, sensitive ports never bind `0.0.0.0`. Network position is never a
  substitute for either.
- **Least-exposure containers.** Bind sensitive service ports to **loopback**,
  publish only the edge, run containers non-root, mount secrets/certs
  **read-only**, and cap resources so one container can't starve the host.
- **Socket consumers.** A `:ro` socket mount is not attenuation: a reader can
  list containers, read their environment (secrets included) and stream every
  container's logs. A socket proxy that forwards the whole API only moves the
  finding; only an endpoint-filtered proxy (logs only, say) reduces privilege.
  Observed in practice: removing the socket from a log or metrics collector
  that discovers containers through it blinded ingestion silently, so verify
  with a per-service coverage check, not "logs are flowing".

## Docker inside an LXC guest
The hypervisor side (`pct set --features`, raw `lxc.*` lines) is on
[`platform/proxmox-ve.md`](../platform/proxmox-ve.md); the guest side is here.

- **Prerequisites.** The CT feature `nesting=1`, and for an unprivileged CT
  `keyctl=1` (the hypervisor docs say it is required for Docker), applied by a
  CT restart.
- **Runtime gate before any Compose work.** `docker run --rm hello-world` (or
  `busybox true`) succeeds, and `docker info` shows cgroup v2, the systemd
  cgroup driver and the storage driver actually in use (check overlay on a ZFS
  or btrfs root filesystem; do not assume it). Observed in practice: debugging
  Compose before this gate passed wasted the session.
- **Unprivileged-CT failure mode.** Observed in practice: container creation
  failed with "permission denied" writing `net.ipv4.ip_unprivileged_port_start`
  (the Docker default sysctl, see [`docker.md`](docker.md)), blocked by the
  CT's AppArmor and procfs confinement; nesting and cgroup overrides did not
  fix it, and whether it bites varies across runc, LXC and AppArmor releases.
  The hypervisor's 9 line lists a known AppArmor issue for nested containers.
  Fall back to a privileged CT or a VM, and smoke-test after every host or
  engine upgrade.
- **The security trade.** The relaxations used to make nested Docker work
  (`lxc.apparmor.profile: unconfined`, `lxc.cgroup2.devices.allow: a`,
  `lxc.mount.auto: proc:rw sys:rw`, an emptied `lxc.cap.drop`, a privileged CT
  where container root is host root) weaken the CT boundary. Keep Docker in
  LXC to single-purpose CTs, and prefer a VM when isolation from the
  hypervisor matters (the hypervisor's own docs recommend nesting inside a VM
  for maximum isolation).
- **Group membership timing.** Adding a user to the `docker` group takes
  effect only in a new login session (in Ansible, `meta: reset_connection`).

## General pitfalls
- **`docker` group membership == root.** Treating it as an "ordinary" group is a
  privilege-escalation path; scope it like root access. The same reach is how
  root-owned debris that containers leave on a host without sudo gets repaired
  (procedure and lasting fix on [`docker.md`](docker.md), Idioms); record that
  as a use of root, not as a workaround.
- **A published daemon socket / a socket bind-mounted into a container** is
  remote root on the host, the single highest-impact container-host mistake.
- **Firewall vs Docker's iptables rules.** Docker writes its own iptables/nft
  rules for published ports and can **bypass a naive ufw allow-list**: a port
  published with `-p` can be reachable even when ufw "denies" it. Bind to
  loopback (`127.0.0.1:host:container`) or constrain Docker's iptables handling;
  do not assume the host firewall alone contains a published port.
- **"Internal-only" is not a control.** A dead config server, an internal LXC,
  or a private subnet does not compensate for an open socket, password SSH, or a
  disabled-auth flag; treat the host as exposed and harden regardless.
- **EOL base/host** silently accrues unpatchable CVEs; the lifecycle gate is
  part of hardening, not separate from it.
- **Unrotated logs fill the disk.** `json-file` without `max-size` grows until
  the host runs out of space, and a full disk then takes down every service.

## Testing
- `docker info` Security Options and logging driver, checked against the
  intended floor after every engine or host upgrade.
- From an external host, scan the published ports and confirm only the edge
  answers; confirm `2375`/`2376` are closed.
- For each socket consumer, list the API calls it needs and confirm the proxy
  in front of it refuses everything else.
- For a log collector, assert every service appears in the collected stream.

## Security defaults
- **The Docker daemon is a root-equivalent surface.** Anyone who can reach the
  docker socket effectively controls the host. So: **never publish the socket**
  (no `-p` on `2375/2376`, no bind-mounting `/var/run/docker.sock` into any
  container: a "trusted" collector with a `:ro` mount has the same API reach,
  since read-only on the socket file does not limit API calls); prefer
  **rootless Docker** or enable **user-namespace remapping** (`userns-remap`)
  so container root ≠ host root; drop capabilities and set `no-new-privileges`
  on containers that don't need more; keep the socket `root:docker` and
  membership in the `docker` group tightly held (it is equivalent to root).

## Operational behaviour
- **User-namespace remapping is not a free switch on a live host.** Enabling
  `userns-remap` moves Docker to a separate data root under
  `/var/lib/docker/<uid>.<gid>/`, which masks every existing image, container
  and volume; disabling it later hides whatever was created while it was on.
- **Log settings** apply only to containers created after a daemon restart.
- **Disk exhaustion** from unrotated logs: see General pitfalls, "Unrotated
  logs fill the disk".

## Interop
- The Engine and image-store details: [`docker.md`](docker.md).
- Compose-level hardening (`no-new-privileges`, `cap_drop`, resource limits):
  [`docker-compose.md`](docker-compose.md).
- Hypervisor side of Docker in LXC:
  [`platform/proxmox-ve.md`](../platform/proxmox-ve.md).

## Major lines
The engine's major lines, including the Engine 29 image-store and cgroup
changes, are on [`docker.md`](docker.md), Major lines.

## Upstream docs
- https://docs.docker.com/engine/security/
- https://docs.docker.com/engine/security/userns-remap/
- https://docs.docker.com/engine/logging/configure/
- https://docs.docker.com/engine/logging/drivers/json-file/
- https://docs.docker.com/engine/security/apparmor/
- https://docs.docker.com/engine/security/seccomp/
- https://docs.docker.com/engine/security/rootless/
- CIS Benchmarks (Docker; Ubuntu Linux), the authoritative checklists
