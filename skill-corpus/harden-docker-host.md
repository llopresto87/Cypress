# Suggested skill: harden-docker-host

> Optional procedure: bring a Linux host (recent Ubuntu LTS, e.g. 24.04 /
> 26.04) that runs Docker to a security floor, idempotently, and prove each
> control is actually active. Owns the *procedure*; the *what/why* of each
> control lives in `library-corpus/container/docker-host-hardening.md`, and
> this skill applies that floor in order and gates it. Run by `reliability`
> during bring-up, called from the deploy method's host-prep step, or on
> demand to audit an existing host. Parameterized by `<host>`, `<ssh-user>`,
> `<ssh-key>`.

## When to apply

- Before the first `compose up` on a fresh host (a bring-up precondition).
- Auditing or re-baselining an existing host: the procedure is a no-op-safe
  re-run, so it doubles as a drift check.
- Any time `reliability` stands up or hands over infrastructure.

Apply the whole floor on every host, one on a private or "internal-only"
network included: network position is not a control.

## The procedure (idempotent; apply then verify each; presence is not enforcement)

Apply the floor from `docker-host-hardening.md` in this order, and after each
control verify it is actually active:

0. **Prepare the host when Docker runs inside an LXC guest.** Skip this step
   on a VM or bare metal. The hypervisor side (the CT `features`, raw `lxc.*`
   lines) is `library-corpus/platform/proxmox-ve.md`; the guest side, with
   the failure modes and the security trade, is the "Docker inside an LXC
   guest" section of `docker-host-hardening.md`. Do not start with Compose
   errors, because a guest that cannot run one container makes every
   Compose symptom misleading:
   1. Ask the operator to enable `nesting` on the CT, plus `keyctl` for an
      unprivileged CT, and to restart the CT. This is a hypervisor act that
      the guest cannot perform.
   2. Gate the runtime before any Compose work, with the check that
      section names (a throwaway container exits 0; `docker info` shows the
      cgroup version, cgroup driver and storage driver in use).
   3. If container creation fails with a permission error on a sysctl write,
      that is the section's unprivileged-CT failure mode: stop and take its
      fallback to the operator, a privileged CT reserved for this one
      workload or a VM. Record the choice and the security trade it makes.
   4. Re-run the gate after every hypervisor, guest kernel or engine
      upgrade.

1. **Deploy user + SSH.** Ensure a non-root user with scoped `sudo`. Set SSH
   key-only: `PasswordAuthentication no` and
   `PermitRootLogin prohibit-password`, so root logs in by public key only (the
   deploy method connects as root by key) and no account logs in by password.
   Reload sshd.
   Verify: a password auth attempt, as root or any user, is refused; the key
   still logs in. Keep the old session open until a new key session logs in,
   so a bad sshd config cannot lock you out.
2. **Firewall, operator-gated.** The host firewall is the one control that can
   lock you out or collide with an upstream firewall (the hypervisor / LXC
   host, a cloud security group), so it is operator-gated: propose a
   default-deny-inbound ruleset that opens only the published edge port(s),
   and apply it on the operator's explicit go-ahead from an out-of-band
   session, because the SSH session you are in is the one it could sever. If
   declined, record that and rely on loopback binding (step 4) for
   containment; sensitive ports still bind to loopback only. Verify (only when
   applied): the edge answers; a sensitive port is refused off-host.
3. **Docker daemon as a root-equivalent surface.** Enable rootless Docker or
   `userns-remap`; keep the socket local to the host and mounted only into
   trusted containers; hold `docker`-group membership as tightly as root,
   because it is root. On a host that already holds data, test
   `userns-remap` against the existing named volumes and bind mounts on a
   copy or in a maintenance window first; `docker-host-hardening.md`
   (user-namespace remapping) says what breaks. Verify: the daemon socket is
   not listening on any TCP port; container root ≠ host root.
4. **The ufw-vs-Docker-iptables trap.** Confirm a `-p`-published port is not
   reachable off-host *past* a firewall "deny"; bind sensitive ports to
   loopback (`127.0.0.1:host:container`) rather than trusting the host firewall
   to contain Docker's own iptables rules. Verify from off-host.
5. **Automatic security updates + lifecycle.** Enable unattended security
   upgrades; confirm the OS line and the engine are supported. Verify: the
   timer is active; the release is supported.
6. **Least-exposure defaults.** Containers run non-root, `no-new-privileges`,
   dropped capabilities, read-only secret/cert mounts, resource caps. Verify on
   a representative container.
7. **Daemon-level confinement and log rotation.** Apply the log-rotation
   setting from `docker-host-hardening.md`. Verify from the operator's
   machine over SSH, not from a report the host writes about itself: read
   the security options and the logging driver with the check that page
   gives ("Prove the confinement is on") and compare them with the intended
   floor (AppArmor or SELinux, seccomp, and userns or rootless where you
   chose it). Repeat the check after every host or engine change.

Record each control as applied+verified or absent-with-reason in the host's
`operations.md` / `verification.md` runbook: a hardening step that ran but
asserted nothing is a green lie.

## Reference files

- `library-corpus/container/docker-host-hardening.md` (the floor: *what* to
  harden and *why*; this page is the *how*, in order, with a gate per control)
- `library-corpus/platform/proxmox-ve.md` (the hypervisor side of step 0)
- `agents/06-reliability.md` (the agent that runs this), `agents/05-security.md`
- `skill-corpus/deploy-fleet-on-remote-docker-host.md` (the bring-up whose
  host-prep step calls this)
- `templates/docs/runbooks/{operations,verification}.md` (where results land)
