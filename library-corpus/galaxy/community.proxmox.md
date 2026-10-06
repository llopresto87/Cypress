# community.proxmox — galaxy

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`community.proxmox` is the community Ansible collection for Proxmox VE. It
holds modules for QEMU/KVM virtual machines (`proxmox_kvm`), LXC containers
(`proxmox`), disks (`proxmox_disk`), templates (`proxmox_template`), snapshots
(`proxmox_snap`), storage, roles and firewall, read-only `*_info` modules
(`proxmox_storage_info` and others), an inventory plugin and, on the 2.x line,
a connection plugin. Galaxy namespace `community`, name `proxmox`; licence
GPL-3.0-or-later. The modules split out of `community.general`, which keeps
only redirects to them. It is not part of ansible-core
(`library-corpus/pypi/ansible-core.md`).

## Install, setup and configuration
- `ansible-galaxy collection install community.proxmox`, or an entry with a
  pinned `version:` range in `collections/requirements.yml`. A copy installed
  from Galaxy is not upgraded when the `ansible` community package is.
- Python requirements, on the host that executes the module: `proxmoxer` and
  `requests`. The collection documents a minimum `proxmoxer` version: read it
  from the README's requirements list or the module page's Requirements, not
  from the README's install command, which still names an older floor.
- Connection options on every module: `api_host`, `api_user`, and either
  `api_password` or an API token (`api_token_id` plus `api_token_secret`);
  `validate_certs`, `ca_path` for a private CA, and `api_timeout`.
  Each falls back to an environment variable: `PROXMOX_HOST`, `PROXMOX_USER`,
  `PROXMOX_PASSWORD`, `PROXMOX_TOKEN_ID`, `PROXMOX_TOKEN_SECRET`,
  `PROXMOX_PORT`.

## Core API / usage shape
- `proxmox_kvm` creates, clones, updates and deletes VMs. `state` is one of
  `present` (default), `started`, `stopped`, `restarted`, `absent`, `current`,
  `template`, `paused`, `hibernated`. `node` and `name` are required for
  `present`; with `present`, no `vmid`, and an existing VM of that name, the
  module changes nothing.
- Cloning with `proxmox_kvm`: `clone` names the source VM (required to start a
  clone; any value once `vmid` is set), `vmid` is the **source** VM's id, and
  `newid` is the id of the new VM (the next free id is fetched when unset).
  `full: false` makes a linked clone; `storage`, `format` and `timeout` apply
  to a full clone.
  ```yaml
  - community.proxmox.proxmox_kvm:
      api_host: "{{ pve_api_host }}"
      api_user: "{{ pve_api_user }}"
      api_token_id: "{{ pve_token_id }}"
      api_token_secret: "{{ vault_pve_token_secret }}"
      node: "{{ pve_node }}"
      clone: template-name
      vmid: 9000          # the template being cloned
      newid: 120          # the new VM
      name: web-01
      full: true
      storage: "{{ pve_vm_storage }}"
      timeout: 600
    delegate_to: localhost
  ```
- `proxmox` manages LXC containers (`state` present, started, stopped,
  restarted, absent, template; `storage` defaults to `local`).
- `proxmox_disk` works on one disk key (`scsi0`, `virtio1`, ...) with `state`
  `present`, `resized`, `detached`, `moved` or `absent`. A `size` with a `+`
  prefix grows the disk by that amount; without it the size is absolute.
- `proxmox_snap` creates, deletes and restores snapshots of VMs and containers;
  `proxmox_template` uploads and deletes templates;
  `proxmox_storage_info` reads storage definitions.
- Cloud-init is set through `proxmox_kvm` options: `ciuser`, `cipassword`,
  `cicustom`, `nameservers`, `searchdomains`, `sshkeys`, `ipconfig`.

## Idioms & best practices
- Observed in practice: run the modules against the Proxmox API from the
  control node (`delegate_to: localhost`, or `connection: local`), never on the
  hypervisor. The Python requirements then apply to the control node's
  interpreter, and the hypervisor needs no `proxmoxer` (an OS package there can
  be too old). Point `ansible_python_interpreter` for localhost at the
  interpreter that has `proxmoxer` (the interpreter drift is on the
  ansible-core page). Upstream says only that the requirements apply to the
  executing host.
- Authenticate with an API token rather than a password, keep the secret in
  vault, and validate the API certificate with `ca_path` instead of turning off
  `validate_certs`.
- Observed in practice: cloud-init values take effect when the guest boots.
  Start or reboot the clone, then gate SSH work behind
  `ansible.builtin.wait_for_connection`. The docs say only that custom files
  replace the generated ones at start.
- Observed in practice: drift on a long-lived cloud-init VM is cheaper to fix
  by destroying it and re-cloning from the template than by incremental
  updates, given the update limits below.

## General pitfalls
- Clone ids: mixing up `vmid` (source) and `newid` (target) aims later steps at
  the template itself.
- `state: present` on an existing VM changes nothing unless `update: true`.
  Even then `net`, `virtio`, `virtiofs`, `ide`, `sata` and `scsi` (NICs and
  disks) are not updated without `update_unsafe: true`, because updating them
  can change MAC addresses or create new disks; `update_unsafe` also lifts the
  limits on `efidisk0` and `tpmstate0` and, per the docs, "might result in
  a permanent loss of data". Updating `pool` is disabled. A VM that "exists with
  the wrong spec" after a rerun is this behaviour, not a bug.
- `proxmox_disk` only grows a disk; the PVE API does not shrink one. Growing
  the guest's partition and filesystem is outside the module. Observed in
  practice: a clone starts with the template's disk size, so resize it
  explicitly and check free space inside the guest before runtime steps.
- Observed in practice: Proxmox VE validates a VM `name` as a DNS name
  (lowercase letters, digits and hyphens; no underscores), and the API rejects
  anything else. The module docs say nothing about name rules.
- Observed in practice: the storage named in a disk spec must exist on the
  target node and allow the needed content type, and storage names can differ
  per node. Preflight with `proxmox_storage_info` (or `pvesm status` on the
  node). The docs document the `storage` option, not the content-type rule.
- Some LXC `features` need a privileged container. Observed in practice:
  Docker inside an unprivileged LXC container fails on sysctl writes even with
  nesting enabled, so Docker hosts belong in a VM or a privileged container.
  That is a Proxmox and LXC platform fact; the collection docs are silent on it.

## Testing
- `proxmox_kvm` declares no check-mode support, so `--check` predicts nothing
  about VM changes.
- Validate with the `*_info` modules (read-only), then a scoped real run against
  one disposable VM, and read the resulting configuration back.
- Observed in practice: a preflight play run before any create checks that the
  storage exists, that the name is DNS-valid, that the id is free, and that
  `proxmoxer` imports in the module's interpreter.

## Security defaults
- Tasks that pass `api_password` or `api_token_secret` should run with
  `no_log: true`.
- TLS: use `ca_path` for a private CA; `validate_certs: false` disables
  verification of the API certificate.
- `update_unsafe` and the destructive disk operations can lose data.

## Operational behaviour
- Long operations (clone, resize) wait up to the module's `timeout`;
  each API call is bounded by `api_timeout`.
- All work goes through the PVE HTTP API from wherever the module runs; the
  collection keeps no state between runs.

## Interop
- `community.general` keeps redirect entries for the old Proxmox module names,
  with a deprecation and removal at a future `community.general` major. With
  both collections installed one module answers to two names; call only the
  `community.proxmox.*` FQCN.
- Runs beside ansible-core's `delegate_to` and interpreter settings
  (`library-corpus/pypi/ansible-core.md`).

## Major lines

### 1.x line
- The first releases after the split from `community.general`; the 1.x line
  adds `ca_path`, `api_timeout`, and `present` as the default `state`.

### 2.x line
- Raises the minimum `proxmoxer` version (read it from the collection's
  requirements, see Install); adds TOTP authentication,
  `destroy_unreferenced_disks`, `cmode`, and a connection plugin. Some
  node-firewall module names become redirects, to be removed at 3.x.

## Upstream docs
- Docs: https://docs.ansible.com/ansible/latest/collections/community/proxmox/
- Repo: https://github.com/ansible-collections/community.proxmox
