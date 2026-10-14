---
name: dead-hostname-audit
description: Audit every place a hostname declared gone for good is wired into the running system (environment config, mailed links, payload URLs, compiled bundles, proxy names, certificates), classify each occurrence by what breaks and what the fix costs, and never contact the old address. Invoke when an operator says a public name has stopped existing or passed to someone else.
id: skill.dead-hostname-audit
tier: 2
kind: skill
title: dead-hostname-audit, find and classify every wiring of a hostname that is gone for good
owns:
  - dead-hostname-audit.no-probe-boundary
  - dead-hostname-audit.wiring-surfaces
  - dead-hostname-audit.consequence-classes
requires:
load_when:
  - "this domain no longer exists"
  - "the hostname is gone for good"
  - "we lost the domain, find everywhere it is used"
  - "the old public hostname passed to someone else"
prevents: A retired hostname survives in mailed links, payload URLs and compiled bundles, and a well-meant reachability check sends traffic to whoever now owns the old address.
est_tokens: 1518
---

# Suggested skill: dead-hostname-audit

> Optional procedure: when an operator states that a public hostname has stopped
> existing, audit every place the name is wired into the running system (not only
> the DNS record or the one config you remember), classify each occurrence by
> what breaks, and never contact the address that used to resolve there.
> Composes `skill-corpus/triage-unresolved-required-variable.md` (the sibling
> triage for a required value that will not resolve; this page is its case for a
> name that is gone for good, not merely unset) and `core/method/incident-posture.md`
> §5 (the published residual the audit's unfixable rows become) by reference.
> Parameterized by `<DEAD_NAME>` (the hostname declared gone) and
> `<ENV_SET>` (the environments whose running configuration must be searched).

## When to apply

- An operator states that a public hostname, domain, or third-party endpoint
  has stopped existing, or has passed to someone else: not that it is
  temporarily down, but that the name will not come back as yours.
- A required value that resolves to such a name is unresolved, and the sibling
  triage above shows the name itself is the dead thing, not the variable.

It does not apply to a name that is merely misconfigured or temporarily
unreachable: that is the sibling triage, which ends by restoring the name, not
by auditing its removal.

## The one boundary: never probe the old address

A name that is not yours must not be contacted. The address `<DEAD_NAME>` used
to resolve to may now belong to a third party, and a probe (even a health
check) reaches a stranger's machine with your system's intent attached. The
whole audit reads your own configuration and code; it never sends a packet to
the dead name. A "does it still answer?" check is the one step this procedure
forbids outright.

## The procedure

### 1. Name the dead thing and the blast surface, in writing

Record `<DEAD_NAME>` exactly as it is written (bare host, fully-qualified, and
any alias), and list `<ENV_SET>`. The name can appear in forms a single grep
misses: a bare host in one place, fully-qualified in another, a wildcard parent,
a value assembled at build time from parts. List the spellings before searching
so the search covers them all.

### 2. Search every place a name is wired, not only the ones you remember

A hostname is reachable from a running system in more places than its DNS entry.
Search each, per environment, because the production profile may load a value a
development one never sees:

- **Per-environment configuration** the running profile loads (environment
  files, variable stores, rendered config).
- **Links the system mails to users**: account-recovery, verification, and
  notification templates, where a dead link silently fails for every user.
- **URLs returned in payloads**: API responses, redirects, webhook targets,
  and any address a client is told to call back.
- **Values compiled into a front-end bundle**: a chat socket, an analytics or
  media host baked in at build time, which no runtime config can override
  without a rebuild.
- **Reverse-proxy server names and upstreams**: virtual-host matches, proxy
  targets, and CORS or allow-list entries keyed on the name.
- **Certificate and renewal paths**: a cert whose subject or renewal challenge
  is bound to the dead name.

### 3. Classify each occurrence by consequence, not by count

For every hit, record what breaks and what the fix costs, because the two decide
the order of work:

- **What breaks**, stated as the user-visible effect: a recovery link that dead-
  ends, a payload URL a client cannot reach, a compiled bundle value that fails
  on load, a renewal that will stop issuing a cert.
- **The fix class**, either an **edit** (a config or template value changed in
  place) or a **rebuild** (a value compiled into an artifact, which cannot be
  fixed without rebuilding and redeploying it). A bundle-compiled value is the
  trap: it looks like one more config line but is reachable only through a build.
- **Whether a component actually reads it.** A declaration is not use. A
  constant that no running code path reads is a cleanup, not an outage: record
  it as not-affected with the evidence (no reader found), so the audit neither
  over-counts the harm nor leaves the dead name lying around.

### 4. Route the rows

Edits land as the fix they are. Rebuilds are sequenced as deploys, not quick
config changes. An occurrence that cannot be removed now (an external party
still mails the old link, say) becomes a published residual with its owner and
reopen trigger (`core/method/incident-posture.md` §5), so the dead name is
accounted for rather than forgotten.

## Reference files

- `skill-corpus/triage-unresolved-required-variable.md` (the sibling triage for
  a required value that will not resolve; this page is its gone-for-good case)
- `core/method/incident-posture.md` (§5, the published residual an unfixable
  occurrence becomes)
