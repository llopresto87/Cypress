# docker-host-hardening — container

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. The hardening floor for a Linux host that runs Docker
> workloads. Orientation, NOT a version-pinned runbook — for exact package
> versions and CVEs, ingest against the host's actual release. Durable surface
> = *what* to harden and *why*; the exact command for each is the plant's to
> pin.

## What it is
A container host has two attack surfaces most app-security checklists miss: the
**host OS** itself (SSH, users, firewall, updates) and the **Docker daemon**,
which by default is a root-equivalent control plane. Hardening the host is a
precondition of any deploy onto it — a hardened image on an open host is a soft
target. This page is the standing floor a bring-up brings the host to before
the first `compose up`, re-runnable idempotently.

This page owns **what** each control is and **why** it matters. Applying the
floor in order, and gating each control on evidence that it is actually active,
is a *procedure* and belongs to `skill-corpus/harden-docker-host.md` — which
composes this page rather than restating it. Read this to understand a control;
run that to install one.

## The hardening floor

- **Users & SSH.** No routine work as `root`; a non-root deploy user with
  scoped `sudo`. SSH is **key-only** (`PasswordAuthentication no`), root login
  off (`PermitRootLogin no` — or `prohibit-password` where a key-only root is a
  deliberate deploy convention), on a maintained OpenSSH. Key auth, not
  passwords, everywhere.
- **Firewall — default-deny, but an operator choice.** A host firewall
  (ufw/nftables) that denies inbound by default and opens **only the edge** the
  fleet publishes is the goal — but it is the one control that can lock out
  access or collide with an **upstream firewall** (the hypervisor / LXC host, a
  cloud security group), so applying it is an operator decision, not automatic
  (gate it on explicit sign-off, from an out-of-band session). Its always-on
  complement, **not** optional, is loopback binding (below): even with no host
  firewall, sensitive ports never bind `0.0.0.0`. Network position is never a
  substitute for either.
- **The Docker daemon is a root-equivalent surface.** Anyone who can reach the
  docker socket effectively controls the host. So: **never publish the socket**
  (no `-p` on `2375/2376`, no bind-mounting `/var/run/docker.sock` into an
  untrusted container); prefer **rootless Docker** or enable **user-namespace
  remapping** (`userns-remap`) so container root ≠ host root; drop capabilities
  and set `no-new-privileges` on containers that don't need more; keep the
  socket `root:docker` and membership in the `docker` group tightly held (it is
  equivalent to root).
- **Automatic security updates.** Unattended security upgrades enabled for the
  OS; base images and the engine kept on a supported (non-EOL) line.
- **Least-exposure containers.** Bind sensitive service ports to **loopback**,
  publish only the edge, run containers non-root, mount secrets/certs
  **read-only**, and cap resources so one container can't starve the host.
- **Disk hygiene.** Reclaim with `docker builder prune` + image/container/
  network prune; **never `--volumes`** (that is the persistent data).

## General pitfalls
- **`docker` group membership == root.** Treating it as an "ordinary" group is a
  privilege-escalation path; scope it like root access.
- **A published daemon socket / a socket bind-mounted into a container** is
  remote root on the host — the single highest-impact container-host mistake.
- **Firewall vs Docker's iptables rules.** Docker writes its own iptables/nft
  rules for published ports and can **bypass a naive ufw allow-list** — a port
  published with `-p` can be reachable even when ufw "denies" it. Bind to
  loopback (`127.0.0.1:host:container`) or constrain Docker's iptables handling;
  do not assume the host firewall alone contains a published port.
- **"Internal-only" is not a control.** A dead config server, an internal LXC,
  or a private subnet does not compensate for an open socket, password SSH, or a
  disabled-auth flag; treat the host as exposed and harden regardless.
- **EOL base/host** silently accrues unpatchable CVEs; the lifecycle gate is
  part of hardening, not separate from it.

## Upstream docs
- https://docs.docker.com/engine/security/
- https://docs.docker.com/engine/security/rootless/
- CIS Benchmarks (Docker; Ubuntu Linux) — the authoritative checklists
