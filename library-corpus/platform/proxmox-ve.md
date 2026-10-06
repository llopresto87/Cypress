# proxmox-ve — platform

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). This is a **self-hosted platform surface**:
> Proxmox VE has major lines but no package in a project lockfile, so the page
> is pinned by major line plus **retrieval date**. The surface below was
> confirmed against the upstream admin guide of the 9 line, its man pages, API
> schema and wiki on **2026-10-05**. Orientation only: for a project's own
> nodes, storages, bridges, VMIDs and templates, run `ingest-library` against
> the project, and re-confirm anything load-bearing against the docs of the
> major the hosts run.

## What it is
Proxmox VE is a Debian-based open-source virtualization platform (AGPL-3.0).
One product runs full VMs with KVM/QEMU and system containers (CTs) with LXC,
and adds storage, clustering, backup, a firewall, HA and a web UI. Home:
pve.proxmox.com (admin guide, man pages, API viewer, wiki); packages from
download.proxmox.com and enterprise.proxmox.com.

The surfaces a plant drives:
- the CLI tools: `qm` (VMs), `pct` (CTs), `pvesm` (storage), `pveam` (CT
  template downloads), `pvesh` (the whole REST API from a shell), `pveum`
  (users and permissions), `vzdump` (backup), `pvecm` (cluster) and the
  `pveXtoY` upgrade checkers;
- the REST API at `https://<host>:8006/api2/json/`;
- the config files in `/etc/pve`, the cluster file system `pmxcfs`.

The CLI and the API share one JSON-schema parameter model, so a CLI option has
the same name as the API parameter. `pmxcfs` is database-backed, held in RAM,
limited to 128 MiB, replicated to every cluster node in real time over
corosync, and read-only on a node that has lost quorum.

## Install, setup and configuration
- **Install.** The bare-metal ISO installer is the supported path; installing
  on top of a stock Debian is documented for custom disk layouts. On a
  Debian-first install the hostname must resolve to a non-loopback address
  (`hostname --ip-address`), so remove any `/etc/hosts` line that maps it to
  loopback. Hardware: 64-bit x86 with VT-x/AMD-V, or arm64; for production,
  about 2 GB for the host plus guest memory, about 1 GB of RAM per TB of ZFS or
  Ceph storage, and redundant SSD storage.
- **Repositories.** The enterprise repository is enabled by default and needs
  a subscription key. Without one, disable it and add `pve-no-subscription`
  (upstream: not for production). The Debian base repositories are always
  needed too. Repository codenames and the Ceph release name belong to one
  major line (see Major lines).
- **Network.** Host networking is `/etc/network/interfaces`, applied with
  `ifreload -a` (ifupdown2) or a reboot. Bridges are conventionally `vmbr<N>`
  (`vmbr0` is the standard one), bonds `bond<N>`, VLAN devices
  `<device>.<vlan>`. Bridges are per-node host config.
- **Boot.** After changing the kernel command line, run
  `proxmox-boot-tool refresh` (on GRUB hosts, the equivalent of
  `update-grub`); `efibootmgr -v` shows which bootloader is in use.
- **Cluster.** Install each node with its final hostname and IP: they cannot
  change after the cluster is created. Corosync wants latency under 5 ms and
  ideally its own NIC; reliable quorum needs three votes (a QDevice gives a
  two-node cluster its third). Kronosnet is the default transport; switching
  to plain `udp`/`udpu` loses encryption and redundancy. Time must be tightly
  synchronized (chrony is the default).
- **Certificates.** Each cluster makes its own self-signed CA
  (`/etc/pve/pve-root-ca.pem`) and signs the node certificates `pveproxy`
  serves.
- **Datacenter settings** live in `/etc/pve/datacenter.cfg`; `next-id` bounds
  the automatic VMID pool (`lower` 100 inclusive, `upper` 1000000 exclusive).
- **Default storage** after install (`/etc/pve/storage.cfg`): `local`
  (directory `/var/lib/vz`, content `iso,vztmpl,backup`) plus either
  `local-lvm` (LVM-thin, `rootdir,images`) or `local-zfs` (ZFS,
  `images,rootdir`).

## Core API / usage shape
### Guest IDs
- VMs and CTs share one integer namespace (100 to 999999999), unique across
  the cluster. `pmxcfs` checks for duplicates, but `GET /cluster/nextid`
  (`pvesh get /cluster/nextid --vmid <id>`) only asserts an ID is free at the
  time of the check, so a race remains.
- `qm create` and `pct create` accept `--force`, which overwrites an existing
  guest with that ID (on `qm`, only with `--archive`, that is during a
  restore). A collision under `--force` replaces the wrong guest.
- A guest's config belongs to its node:
  `/etc/pve/nodes/<node>/qemu-server/<vmid>.conf` or `.../lxc/<vmid>.conf`. If
  the owner node is down, the documented recovery moves the file, after the
  failed node is fenced or powered off.

### Storage
- Pools are defined once, cluster-wide, in `/etc/pve/storage.cfg` as
  `<type>: <id>` plus properties. `nodes` limits which nodes have the pool;
  `shared` marks storage that already is shared and does not make local
  storage reachable.
- **Content types** gate what a pool may hold: `images` (VM disks), `rootdir`
  (CT data), `vztmpl` (CT templates), `backup`, `iso`, `snippets` (hook
  scripts, cloud-init files) and `import`. Not every storage type supports
  every content type.
- **Volume IDs** are `<storage>:<name>`: `local:iso/<file>.iso`,
  `local:vztmpl/<file>.tar.gz`, `local:230/<disk>` for a disk owned by VM 230.
  `pvesm path <volid>` prints the file path. On directory storage the layout is
  `images/<vmid>/`, `template/iso/`, `template/cache/`, `dump/`, `snippets/`,
  `import/`, so an uploaded ISO lands under `template/iso`.
- Disk images are `vm-<vmid>-<name>.<fmt>`; making a template turns them into
  read-only `base-<vmid>-<name>.<fmt>`. ZFS-backed CT volumes are
  `subvol-<vmid>-<name>` datasets.
- Snapshots and linked clones need ZFS, LVM-thin, Ceph or qcow2 on file
  storage. Thin pools that fill up give guests I/O errors. Storage without
  `O_DIRECT` needs cache mode `writeback` rather than `none`.
- CLI: `pvesm add <type> <id> ...`, `pvesm set <id> --disable 1`,
  `pvesm alloc`, `pvesm path`, `pvesm extractconfig` (read the config inside a
  backup).

### VMs (`qm`)
- `qm create`, then `qm template <vmid>`, then
  `qm clone <vmid> <newid> [--name --full --storage --target]`. Every later
  step addresses `<newid>`. A clone of a template is linked (copy-on-write)
  unless `--full`; a clone of a plain VM is always full. A template with
  linked clones cannot be deleted, and a linked clone cannot change storage.
  Clones get new MAC addresses and a new SMBIOS UUID, but keep the source's
  disk size and hardware.
- `qm disk resize <vmid> <disk> +5G` (or an absolute size) only grows;
  shrinking is unsupported. Check free space on the target pool.
- `name` (and a CT's `hostname`) must be a DNS name (`dns-name` format in the
  API schema). Observed in practice: a name with an underscore was rejected.
- NIC models: `virtio` (fastest), `e1000` (default), `rtl8139`, `vmxnet3`.
  Without `bridge=` the VM gets a slow user-mode NAT NIC meant for testing.
- QEMU guest agent: install it in the guest and set `agent: 1` (a full stop
  and start applies it); it reports IPs and freezes filesystems for backups.
- Hook scripts: `qm set <vmid> --hookscript <storage>:snippets/<script>`.
- `qm destroy <vmid> [--purge] [--destroy-unreferenced-disks]`; `--purge`
  also removes the guest from backup, replication and HA jobs.

### Containers (`pct`)
- CTs share the host kernel, confined by AppArmor, seccomp, cgroups and
  namespaces. Upstream says VMs isolate better and should host untrusted
  users.
- **Unprivileged** CTs (container root mapped to an unprivileged host user)
  are the default and safe by design. **Privileged** CTs are "unsafe": the LXC
  project does not treat new escapes from them as CVE-worthy. The guest needs
  systemd 220 or newer to run unprivileged, 231 or newer for cgroup v2.
- Templates: `pveam update`, `pveam download <storage> <template>`, then
  `pct create <vmid> <storage>:vztmpl/<template> ...`. Root passwords need at
  least 5 characters; SSH keys go one per line.
- **Features** (`pct set <vmid> --features nesting=1,keyctl=1`; all default
  0): `nesting` exposes host procfs and sysfs and is what systemd needs for
  service isolation; `keyctl` (unprivileged only) is "required to use docker
  inside a container", and with it `systemd-networkd` cannot run. Also `fuse`,
  `mknod`, `mount=<fstypes>`, `force_rw_sys`. A feature change takes effect
  when the CT restarts.
- **Raw LXC lines.** Any `lxc.*` key written into the CT config is passed to
  the LXC tools (for example `lxc.apparmor.profile = unconfined`, which
  upstream marks not for production). The format is `key: value`, `#` starts a
  comment, and snapshots are sections of the same file. Observed in practice:
  raw `lxc.*` changes took effect only after a full stop and start, and a hand
  edit left lines the parser rejected; upstream states neither.
- **Managed guest files.** At every CT start, PVE writes `/etc/hostname`,
  edits `/etc/hosts`, sets network and DNS (`nameserver`, `searchdomain`;
  the host's when neither is set), and on create sets the root password and
  regenerates SSH host keys. Its edits sit between `# --- BEGIN PVE ---` and
  `# --- END PVE ---`. `/etc/.pve-ignore.<name>` (for example
  `.pve-ignore.hosts`) leaves one file alone; `ostype: unmanaged` turns all of
  it off. Change DNS in the CT config, not inside the guest.
- **Mount points.** Storage-backed `mp0: <storage>:<size>,mp=<path>` are
  managed, snapshotted and backed up. Bind mounts of a host directory are not
  backed up, have no snapshots or quotas, and fight unprivileged ID mapping;
  use a dedicated source directory without symlinks, never `/`, `/var` or
  `/etc`. Device mounts are unmanaged.
- `--onboot 1` plus start order and delay control boot. A running CT cannot
  live-migrate; `pct migrate --restart` stops, moves and starts it.
- `pct destroy <vmid> --purge`; `pct unlock <vmid>` clears a stale lock only
  once the locking action is surely over. `pct start <vmid> --debug` (or
  `lxc-start -n <vmid> -F -l DEBUG -o <log>`) shows why a CT will not start.

### Cloud-init (VMs)
- The documented flow: import a distro cloud image
  (`qm set <vmid> --scsi0 <storage>:0,import-from=<image>`) or build a
  cloud-init-ready VM, add the drive (`qm set <vmid> --ide2 <storage>:cloudinit`),
  set `--boot order=scsi0` (and `--serial0 socket --vga serial0` if the image
  wants a serial console), `qm template`, then per clone
  `qm set <newid> --sshkey <file> --ipconfig0 ip=<cidr>,gw=<gw>`. Ubuntu cloud
  images need the `virtio-scsi-pci` controller.
- PVE renders the settings into a generated ISO on the cloud-init drive; the
  guest applies them when the VM first starts.
- Options: `ciuser`, `cipassword` (prefer SSH keys), `sshkeys`, `ipconfig<n>`
  (`ip=dhcp` by default), `nameserver`, `searchdomain`, `citype` (`nocloud`
  for Linux, `configdrive2` for Windows), `ciupgrade` (default 1: a package
  upgrade at first boot), and `cicustom` (`user=`, `network=`, `meta=`,
  `vendor=` snippet volumes).
- `qm cloudinit dump <vmid> user|network|meta` prints what PVE generates,
  `qm cloudinit pending <vmid>` shows pending values, and
  `qm cloudinit update <vmid>` regenerates the drive.
- Windows uses cloudbase-init; set `ostype` before the password, or it stays
  encrypted.

### API and authentication
- Two schemes: a ticket cookie (`PVEAuthCookie`, two hours, renewed by
  posting the old ticket as the password) plus a `CSRFPreventionToken` header
  on every write; or an API token in
  `Authorization: PVEAPIToken=USER@REALM!TOKENID=SECRET`.
- Tokens are the documented stateless path for automation: their own expiry,
  revocable without disabling the user, secret shown once, unusable for
  console endpoints. By default a token is **privilege-separated** (its rights
  are the intersection of the user's and its own ACLs), so it needs explicit
  ACLs.
- Every API method names the privilege it checks (clone: `VM.Clone` on the
  source and `VM.Allocate` on the new ID; config: a `VM.Config.*` privilege;
  start: `VM.PowerMgmt`).
- Realms: Linux PAM, the PVE realm, LDAP, Active Directory, OpenID Connect.
  Users in `/etc/pve/user.cfg`, realms in `/etc/pve/domains.cfg`.
- The API is stable within a major; removals and moves happen only at a major
  bump. New parameters and new returned fields are not breaking.
- `pvesh get|set|create|delete|ls <path>` drives the same API locally on a
  node.

## Idioms & best practices
- **One cloud-init template, many clones.** Set every cloud-init option before
  a clone's first start. Observed in practice: a clone started before its data
  was complete stayed unreachable until a reboot; automate configure, start,
  wait for SSH.
- **Preflight before applying**: the VMID is free; the storage exists on the
  target node with the right content type; the bridge exists on that node; the
  template is on that node's storage. Observed in practice, address uniqueness
  belongs in the same preflight, though PVE does not check it.
- **Assert the rendered user-data.** Observed in practice: an empty
  `#cloud-config` (a template whose variables were undefined) booted
  "successfully" with no users and no keys. Check
  `qm cloudinit dump <vmid> user` is non-empty and holds the expected keys.
- **One template lineage.** Observed in practice: automation that addresses a
  fixed disk key (`scsi0`) broke on clones of a template with another disk bus
  and boot order.
- **Recreate rather than retry** once cloud-init or config drift has piled up
  on a guest (observed in practice; upstream gives no retry advice).
- **Unprivileged CTs by default**, `nesting` and `keyctl` only for a workload
  that needs them, and a VM when isolation from the host matters (upstream
  calls nesting inside a VM the recommended practice for maximum isolation).
- **Bind mounts only from a dedicated host directory.**
- **API tokens with expiry and privilege separation on** for automation.
- **Give each CT a stable address and an internal DNS name** (observed in
  practice; upstream shows static `ip=` in `net0`).
- **Treat destructive and boot-path changes as high blast radius.** `--force`
  destroy and create, kernel command line, initramfs and VFIO module changes
  need an explicit approval step. Observed in practice: a misapplied
  passthrough config left a host unable to boot; upstream warns that
  `allow_unsafe_interrupts` can make a system unstable and that GRUB on
  LVM/UEFI hosts can fail to boot after an upgrade.

## General pitfalls
- **Storage IDs per node.** In one cluster a storage ID is defined once.
  Observed in practice: standalone nodes or separate clusters name the same
  kind of store differently, so read the pool list per cluster instead of
  hard-coding it.
- **Two entries for one store** give two volume IDs for one disk, and one
  store shared by two clusters breaks locking.
- **Bind-mounted data is outside `vzdump`** backups, silently.
- **In-guest edits are rewritten** at the next CT start unless a
  `.pve-ignore.*` file exists.
- **`ciupgrade` defaults to on**: a first-boot package upgrade can delay or
  change a fresh clone.
- **Custom cloud-init snippets** on storage that is not on every node stop the
  VM from starting after a migration.
- **`keyctl` costs `systemd-networkd`**, and `nesting` widens what the guest
  sees of the host.
- **Hostnames and IPs are frozen** once a cluster exists.
- **Passthrough:** the device leaves the host and every other guest, the
  guest can no longer live-migrate, and a passed-through GPU shows nothing in
  the web console.
- **Hard-coded repository sources** written for one major point at the wrong
  repositories on another.

## Testing
- `pveXtoY` (`pve8to9` and its predecessors) is the upgrade-readiness check:
  run it with `--full` before an upgrade and again after each fix; it only
  reports.
- Inspect before and after each change: `qm config <vmid>` (`--current` for
  applied values), `pct config <vmid>`, `qm cloudinit dump`,
  `qm cloudinit pending`, `pvesm path <volid>`,
  `pvesh get /cluster/nextid --vmid <id>`.
- Passthrough: `dmesg | grep -e DMAR -e IOMMU -e AMD-Vi`, `lsmod | grep vfio`,
  and the IOMMU groups through
  `pvesh get /nodes/<node>/hardware/pci --pci-class-blacklist ""`.
- CT start problems: `pct start <vmid> --debug`.
- Docker inside a CT: run the runtime gate on
  [`container/docker-host-hardening.md`](../container/docker-host-hardening.md)
  after every host or engine upgrade.

## Security defaults
- New CTs are unprivileged. On the 9 line, creating a privileged CT needs
  `Sys.Modify`.
- The PVE firewall is "completely disabled by default". Before enabling it at
  datacenter level, fill the `management` IP set (GUI, SSH, VNC, SPICE). Rules
  live in `/etc/pve/firewall/cluster.fw`, `nodes/<node>/host.fw` and
  `firewall/<vmid>.fw`, for host, VM and VNet zones. Ports: 8006 (web UI and
  API), 5900–5999 (VNC), 3128 (SPICE proxy), 22, 5405–5412/udp (corosync),
  60000–60050 (migration).
- API tokens are privilege-separated by default; their secret is shown once.
- The cluster CA is self-signed. `/etc/pve/priv/` is root-only; other
  `/etc/pve` files are readable by group `www-data`.
- AppArmor can be turned off per CT (`unconfined`); upstream says not for
  production. Relaxations for nested Docker weaken the CT boundary: see
  [`container/docker-host-hardening.md`](../container/docker-host-hardening.md).

## Operational behaviour
- A node that loses quorum turns `/etc/pve` read-only; guests are owned by
  nodes; HA needs three nodes, shared storage and redundant hardware (a
  hardware watchdog is optional, `softdog` otherwise).
- Migration from an older PVE to a newer one works; the reverse is
  unsupported. CTs migrate by restart; VMs with local passthrough cannot move
  online.
- Backups (`vzdump`): `stop`, `suspend` (kept for compatibility) and
  `snapshot` (live; uses the guest agent's freeze when `agent: 1`). Retention
  with `prune-backups` (`keep-last`, `keep-hourly`, `keep-daily`,
  `keep-weekly`, `keep-monthly`, `keep-yearly`). Restore with `qmrestore` or
  `pct restore`.
- A crash can leave a lock; `qm unlock`/`pct unlock` clear it.

## Interop
- Ansible collections, Terraform providers and API client libraries all call
  the same REST API with the same ticket or token auth; upstream maintains
  only the API. Module-level facts live on the Ansible collection pages
  (`library-corpus/galaxy/`).
- **Docker inside a CT**: the hypervisor side is here (`features`, raw
  `lxc.*` lines); the runtime gate, the failure modes and the security trade
  are on
  [`container/docker-host-hardening.md`](../container/docker-host-hardening.md).
  Observed in practice: Docker's overlay storage worked on a ZFS-backed CT
  rootfs on one ZFS and kernel line; check `docker info` rather than assume
  it. The durable form of "unprivileged CTs cannot run Docker" is "fragile
  across runc and AppArmor updates; smoke-test after upgrades".
- Proxmox Backup Server is the `pbs` storage type and has its own major
  upgrades.
- Ceph: external clusters serve as RBD or CephFS storage; a hyper-converged
  Ceph is tied to a minimum Ceph release per PVE major.

## Major lines
Upgrade one major at a time, from the last minor of the previous line, after
a backup and a clean `pveXtoY --full`.

### 7 to 8
- Debian base bullseye to bookworm: every Debian and PVE repository entry
  changes codename, and hyper-converged Ceph must first reach the release the
  new line requires.
- cgroup v2 is the default since the 7 line; on 8 the legacy v1 hierarchy
  could still be re-enabled by kernel parameter.

### 8 to 9
- Debian base bookworm to trixie. Repositories are described in deb822
  `.sources` files (`apt modernize-sources` converts the one-line `.list`
  form, which warns on trixie); `pvetest` is renamed `pve-test`.
- cgroup v1 is gone: CTs whose systemd is 230 or older (CentOS 7, Ubuntu 16.04
  era) no longer run.
- AppArmor 4: third-party profiles can regress, and upstream lists a known
  issue for nested containers (Docker in a CT).
- `/etc/sysctl.conf` is no longer read; use `/etc/sysctl.d/<NN>-<name>.conf`.
- NIC names can change with the new kernel
  (`pve-network-interface-pinning` pins them); a VirtIO NIC with unset MTU now
  inherits the bridge MTU instead of 1500.
- New LVs on LVM and LVM-thin have autoactivation off; a migration script
  covers existing ones.
- Privileges: `VM.Monitor` removed (use `Sys.Audit` and the finer guest-agent
  privileges), `VM.Replicate` added, `Sys.Modify` needed for privileged CTs.
  Review custom roles.
- GlusterFS storage support dropped.
- Added during the line: OCI images as CT templates, a nested-virtualization
  flag, TPM state in qcow2, and snapshots as volume chains on LVM and iSCSI
  (technology preview).

## Upstream docs
- https://pve.proxmox.com/pve-docs/ (admin guide; chapters pmxcfs, pct, qm, pvesm, pveum, sysadmin, pve-firewall, vzdump, pvecm, ha-manager)
- https://pve.proxmox.com/pve-docs/api-viewer/
- https://pve.proxmox.com/wiki/Proxmox_VE_API
- https://pve.proxmox.com/wiki/Package_Repositories
- https://pve.proxmox.com/wiki/Upgrade_from_8_to_9
- https://pve.proxmox.com/wiki/Upgrade_from_7_to_8
- https://pve.proxmox.com/wiki/Roadmap
- https://pve.proxmox.com/wiki/Linux_Container
