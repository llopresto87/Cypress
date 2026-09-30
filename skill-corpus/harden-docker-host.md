# Suggested skill: harden-docker-host

> Optional procedure — bring a Linux host (recent Ubuntu LTS, e.g. 24.04 /
> 26.04) that runs Docker to a security floor, idempotently, and prove each
> control is actually active. Owns the *procedure*; the *what/why* of each
> control lives in `library-corpus/container/docker-host-hardening.md`, and
> this skill applies that floor in order and gates it. Run by `reliability`
> during bring-up, called from the deploy method's host-prep step, or on
> demand to audit an existing host. Parameterized by `<host>`, `<ssh-user>`,
> `<ssh-key>`.

## When to apply

- Before the first `compose up` on a fresh host (a bring-up precondition).
- Auditing or re-baselining an existing host — the procedure is a no-op-safe
  re-run, so it doubles as a drift check.
- Any time `reliability` stands up or hands over infrastructure.

Apply the whole floor on every host, one on a private or "internal-only"
network included: network position is not a control.

## The procedure (idempotent; apply then verify each — presence is not enforcement)

Apply the floor from `docker-host-hardening.md` in this order, and after each
control verify it is actually active:

1. **Deploy user + SSH.** Ensure a non-root user with scoped `sudo`. Set SSH
   key-only: `PasswordAuthentication no` and
   `PermitRootLogin prohibit-password`, so root logs in by public key only (the
   deploy method connects as root by key) and no account logs in by password.
   Reload sshd.
   Verify: a password auth attempt, as root or any user, is refused; the key
   still logs in. Keep the old session open until a new key session logs in,
   so a bad sshd config cannot lock you out.
2. **Firewall — operator-gated.** The host firewall is the one control that can
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
   because it is root. Verify: the daemon socket is not listening on any TCP
   port; container root ≠ host root.
4. **The ufw-vs-Docker-iptables trap.** Confirm a `-p`-published port is not
   reachable off-host *past* a firewall "deny" — bind sensitive ports to
   loopback (`127.0.0.1:host:container`) rather than trusting the host firewall
   to contain Docker's own iptables rules. Verify from off-host.
5. **Automatic security updates + lifecycle.** Enable unattended security
   upgrades; confirm the OS line and the engine are supported. Verify: the
   timer is active; the release is supported.
6. **Least-exposure defaults.** Containers run non-root, `no-new-privileges`,
   dropped capabilities, read-only secret/cert mounts, resource caps. Verify on
   a representative container.

Record each control as applied+verified or absent-with-reason in the host's
`operations.md` / `verification.md` runbook — a hardening step that ran but
asserted nothing is a green lie.

## Reference files

- `library-corpus/container/docker-host-hardening.md` (the floor: *what* to
  harden and *why* — this page is the *how*, in order, with a gate per control)
- `agents/06-reliability.md` (the agent that runs this), `agents/05-security.md`
- `skill-corpus/deploy-fleet-on-remote-docker-host.md` (the bring-up whose
  host-prep step calls this)
- `templates/docs/runbooks/{operations,verification}.md` (where results land)
