# microsoft-graph — platform

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). This is a **hosted-platform surface**: the
> Microsoft Graph REST API has no package to install and no version number of
> its own beyond the `v1.0` and `beta` URL segments. Its documentation has no
> version-pinned URL (a `view=graph-rest-1.0` page always shows the current
> text), so this page is pinned by **retrieval date** instead: the surface below
> was confirmed against the upstream reference on **2026-10-14**. Items marked
> observed in practice were seen in live calls against the documented
> surface, not stated by the docs. Which endpoints, permissions and SDK a project uses is the project's
> pin, recorded by `ingest-library` in its own wiki page. Re-confirm anything
> load-bearing against current upstream docs.

## What it is
**Microsoft Graph** is the single REST endpoint, `https://graph.microsoft.com`,
for Microsoft 365, Microsoft Entra ID and Microsoft Intune data: users, groups,
directory roles, sign-in and audit logs, authentication-method registration,
Conditional Access policies, managed devices and their compliance, and Intune
report exports, among much else. Every resource is JSON under one of two
version segments, with the same OAuth 2.0 bearer token from the Microsoft
identity platform.

This page covers the API's common contract (versions, authentication,
permissions, paging, throttling, batching) and the read surfaces that identity
and device-management reporting depend on: Entra users and sign-in activity,
sign-in logs, authentication-method registration details, Intune managed
devices, compliance state, and Intune report export jobs. Token acquisition is
the client library's job; for Java it is [`../maven/msal4j.md`](../maven/msal4j.md).

Microsoft publishes SDKs over the same API; the Java one is
`com.microsoft.graph:microsoft-graph` (the v1.0 surface; beta has a separate
SDK). A caller can equally use a plain HTTP client, and then owns paging,
throttling and the models itself.

## Install, setup and configuration
- **Nothing installs for the REST route.** A caller needs an app registration
  in the tenant, a credential for it, the application permissions it calls
  with, admin consent for those permissions, and the base URL
  `https://graph.microsoft.com/v1.0`.
- **Token:** app-only access (a daemon or scheduled job) uses the OAuth 2.0
  client credentials grant with scope `https://graph.microsoft.com/.default`,
  which returns a token carrying every application permission already
  consented for Graph. Send it as `Authorization: Bearer {token}`.
- **Permissions** are named per API on each reference page, in a table read
  "least to most privileged". Application permissions are tenant-wide and need
  an administrator's consent.
- **Licences.** Some surfaces need a tenant licence before they answer:
  - the Intune API needs an active Intune licence for the tenant;
  - `signInActivity` on users needs Microsoft Entra ID P1 or P2 (and
    `AuditLog.Read.All`);
  - sign-in and audit log retention depends on the Entra edition (Operational
    behaviour).
- **SDK (optional):** the Java SDK states Java 8+ at runtime; its
  `azure-identity` dependency is needed only when authenticating through a
  `TokenCredential`. Upstream supports only the latest SDK major line, with the
  previous one kept for security fixes for 12 months after a new major ships.

## Core API / usage shape
- **Versions:** `/v1.0` is generally available and supported for production;
  `/beta` is not (Major lines).
- **Query parameters** (support varies per API; each reference page lists its
  own): `$select` (choose properties; many resources return only a default
  subset otherwise), `$filter`, `$top`, `$orderby`, `$count`, `$search`,
  `$expand`. On directory objects, advanced queries need the header
  `ConsistencyLevel: eventual` together with `$count=true`.
- **Paging:** a response with more data carries `@odata.nextLink`; GET that
  whole URL, unchanged, until no link comes back.
- **Errors:** an `error` object with `code`, `message` and `innerError`
  (`request-id`, `date`); `429 Too Many Requests` with `Retry-After` when
  throttled.
- **Batching:** `POST /v1.0/$batch` with up to 20 requests, each with a unique
  `id`, a `method` and a relative `url` (plus `headers` and `body`); responses
  come back keyed by `id`, in any order, each with its own `status`. `dependsOn`
  sequences requests, and a dependent of a failed request gets 424.
- **Entra users and sign-in activity:**
  - `GET /users?$select=id,accountEnabled,userType,signInActivity,...`:
    application permission `User.Read.All` (`signInActivity` also needs
    `AuditLog.Read.All` and P1/P2). Default page size 100 and maximum 999, or
    a maximum of 500 when `signInActivity` is selected or filtered on. `$skip`
    is not supported.
  - `signInActivity` carries `lastSignInDateTime` (last interactive attempt,
    successful or not), `lastNonInteractiveSignInDateTime` (last
    non-interactive attempt, successful or not) and
    `lastSuccessfulSignInDateTime` (last successful sign-in of either kind).
- **Sign-in logs:** `GET /auditLogs/signIns`, application permission
  `AuditLog.Read.All`. Default and maximum page 1,000, newest first; filter on
  a `createdDateTime` range to avoid timeouts. `appliedConditionalAccessPolicies`
  is returned only when the app also holds `Policy.Read.All`,
  `Policy.Read.ConditionalAccess` or `Policy.ReadWrite.ConditionalAccess`;
  otherwise the property is silently omitted.
- **Authentication-method registration:**
  `GET /reports/authenticationMethods/userRegistrationDetails`, application
  permission `AuditLog.Read.All`. Per user: `isMfaRegistered`, `isMfaCapable`,
  `isSsprRegistered`, `isSsprEnabled`, `isSsprCapable`, `isPasswordlessCapable`,
  `isAdmin`, `methodsRegistered`, `userType`; `$filter` on the booleans.
- **Intune managed devices:** `GET /deviceManagement/managedDevices`,
  application permission `DeviceManagementManagedDevices.Read.All`. Each
  `managedDevice` carries `complianceState`, `complianceGracePeriodExpirationDateTime`,
  `isEncrypted`, `jailBroken`, `lastSyncDateTime`, `managementAgent`,
  `azureADDeviceId`, `userPrincipalName` and more. The v1.0 list page documents
  no OData query parameters, so `$select` support there is unconfirmed.
- **`complianceState`** enum: `unknown` (0), `compliant` (1), `noncompliant`
  (2, "blocked from corporate resources"), `conflict` (3), `error` (4),
  `inGracePeriod` (254, "non-compliant but still has access to corporate
  resources"), `configManager` (255, "Managed by Config Manager").
- **Intune report export jobs** (the route for bulk report data):
  1. `POST /deviceManagement/reports/exportJobs` with `reportName` (required),
     `filter`, `select` (up to 256 columns), `format` (`csv` by default, or
     `json`) and `localizationType`;
  2. poll `GET /deviceManagement/reports/exportJobs/{id}` until `status` is
     `completed` (or `failed`); statuses are `unknown`, `notStarted`,
     `inProgress`, `completed`, `failed`;
  3. download the ZIP from `url` before `expirationDateTime`.
  Compliance-related report names include `DeviceCompliance`,
  `DeviceNonCompliance`, `DevicesWithoutCompliancePolicy` and its `V3`, and the
  per-policy status reports.

## Idioms & best practices
- **Least privilege per call.** Read each API's permission table and request
  the least-privileged application permission it lists; read surfaces need
  `.Read.All` permissions, with the export-job exception below.
- **Always `$select`** the properties you consume: smaller responses, and many
  properties are returned only when selected.
- **Follow `@odata.nextLink` verbatim.** Upstream: "Use the entire URL ... Don't
  try to extract the `$skiptoken` or `$skip` value and use it in a different
  request." A page may contain zero results and still carry a next link. After a
  retried page request, continue from the next link of the last successful
  response, never from a token returned by the retry, or the directory answers
  `DirectoryPageTokenNotFoundException`.
- **Re-send custom headers on every page.** On directory resources, headers such
  as `ConsistencyLevel` are not carried into the next-page request; set them
  again. `@odata.count` comes only on the first page.
- **Handle 429 as upstream says:** wait the `Retry-After` seconds, retry, and
  keep honouring `Retry-After` while it persists; without the header, back off
  exponentially. Never retry immediately: throttled requests still count.
- **Always name the export columns.** Upstream: "Don't build automation around
  default columns of any report export." Pass `select` explicitly and pass
  `format` explicitly.
- **Count compliance with the tenant setting in view.** A compliance figure
  read from `complianceState` must also know the tenant's "Mark devices with no
  compliance policy assigned as" value and cross-check the devices without a
  policy (the `DevicesWithoutCompliancePolicy` report), and must decide on
  purpose whether `inGracePeriod` counts as compliant.
- **Use the successful-only sign-in field** for "last used" or inactivity
  reporting (General pitfalls).
- **Keep history yourself.** Sign-in logs fall out of Graph after the retention
  window (Operational behaviour); a report that needs a longer look-back must
  store what it reads, or the tenant must route logs to storage.
- For change detection, prefer delta queries and change notifications to
  repeated full scans, which upstream names as a common cause of throttling.

## General pitfalls
- **`compliant` can mean "no policy was ever assigned".** The tenant-wide
  setting "Mark devices with no compliance policy assigned as" defaults to
  **Compliant** ("This security feature is off"), so a device that receives no
  compliance policy reports `compliant`. Upstream advises switching it to Not
  compliant when Conditional Access uses compliance.
- **Silence turns into non-compliance.** The tenant's "Compliance status
  validity period" (default 30 days, configurable 1 to 120) treats a device that
  has not reported on all its policies within the period as noncompliant.
- **`inGracePeriod` is non-compliant with access.** It is neither compliant nor
  blocked; `complianceGracePeriodExpirationDateTime` says when the grace ends.
- **Export jobs need a ReadWrite permission to create.** The create page lists
  only `DeviceManagementConfiguration.ReadWrite.All`,
  `DeviceManagementApps.ReadWrite.All` and
  `DeviceManagementManagedDevices.ReadWrite.All`, even though the job only
  reads; polling the job accepts the `.Read.All` permissions. A read-only
  consent set therefore cannot use the export route.
- **`lastSignInDateTime` counts failed attempts.** Upstream: "Since unsuccessful
  attempts are also logged, this value might not accurately reflect actual
  system usage. For tracking actual account access, please use the
  `lastSuccessfulSignInDateTime` property." The successful-only field was added
  later and is not backfilled, so it is empty for a user whose last success
  predates it.
- **`isMfaRegistered` is not `isMfaCapable`.** `isMfaRegistered` is true when
  the user registered a strong method "not necessarily ... allowed by the
  authentication methods policy"; `isMfaCapable` requires the method to be
  allowed. Report MFA readiness from `isMfaCapable`.
- **`userRegistrationDetails` skips disabled users** ("This method doesn't work
  for disabled users"), so it is not a full user census.
- **Conditional Access data drops out silently** from sign-in logs when the
  `Policy.*` permission is missing.
- **Report names carry upstream typos.** The available-reports reference lists
  `DeviceStatusByCompliacePolicyReport` and
  `DeviceStatusSummaryByCompliacePolicyReport` (and their `V3` forms) spelled
  "Compliace"; copy report names from the reference, never retype them.
- **Some resources return 429 without `Retry-After`:** the identity protection
  and Conditional Access resources say so explicitly. Code that waits only on
  the header must fall back to exponential back-off.
- **A `200` batch can hide failures:** each inner response has its own status,
  inner 429s are not retried by SDKs that retry unbatched requests, and a
  beta-only endpoint called inside a v1.0 batch fails with 405.
- **Paging varies by API:** default and maximum page sizes differ, an oversized
  `$top` may be ignored, clamped or rejected, and some collections
  (`directoryRole`) do not page at all.
- **Beta-only fields are not v1.0 fields.** Some managed-device and sign-in
  properties are documented on the beta reference only; reading them means
  calling `/beta`, which is unsupported in production.

## Testing
- Graph has no local emulator. Tests run against a stub HTTP server that
  serves recorded or synthetic responses shaped like the reference examples,
  with the token endpoint stubbed the same way.
- Cover the contract, not only the happy path: an `@odata.nextLink` chain
  (including a page with zero items), a 429 with and without `Retry-After`, a
  sign-in response without `appliedConditionalAccessPolicies`, a user without
  `lastSuccessfulSignInDateTime`, every `complianceState` member including
  `inGracePeriod` and `configManager`, and an export job that ends `failed` or
  whose `url` has expired.
- Observed in practice: contract tests built on synthetic stubs prove the
  client's handling of the documented shapes, and still leave the
  permission-to-behaviour questions (for example whether a `.Read.All` app can
  create an export job) to a run against a real tenant.

## Security defaults
- Application permissions are tenant-wide (`User.Read.All` reads every user).
  Grant only what each call needs, and review consent when calls are added.
- An export job's `url` is a pre-signed storage link: anyone holding it can
  download the report until it expires, so never log it or store it.
- `signInActivity`, sign-in logs and registration details are personal data;
  upstream frames the sign-in list API as a personal-data export.
- Access tokens for Graph are not for the caller to parse or validate; treat
  them as opaque (see [`../maven/msal4j.md`](../maven/msal4j.md)).
- The client credential (secret or certificate) is the app's whole identity;
  choosing and keeping it is on [`../maven/msal4j.md`](../maven/msal4j.md)
  (Idioms, "Choosing the credential").

## Operational behaviour
- **Throttling limits** (service-specific limits page):
  - global: 130,000 requests per 10 seconds per app across all tenants;
  - identity and access reports: 5 requests per 10 seconds per app per tenant,
    and `GET` with `signInActivity` 10 requests per minute;
  - Intune device configuration service (`deviceManagement`): reads 2,000 per
    20 seconds per tenant and 1,000 per app per tenant;
  - Intune devices service (`managedDevice` and kin): 4,000 per 20 seconds per
    tenant and 2,000 per app per tenant;
  - export jobs: 100 requests per minute per tenant, 48 per app;
  - identity protection and Conditional Access: 1 request per second per
    tenant, with no `Retry-After`.
  Batched requests count individually. Upstream points bulk extraction to
  Microsoft Graph Data Connect rather than the REST API.
- **Retention:** sign-in and audit logs are kept 7 days on Entra ID Free and
  30 days on P1 and P2; only events inside that window are returned, and an
  upgrade is not retroactive. Longer retention means routing the logs to a
  storage account through Azure Monitor. `signInActivity`, being a property of
  the user object, lasts as long as the user exists.
- **Compliance freshness:** `complianceState` reflects the device's last
  check-in and the policy refresh cycle, not the moment of the read.
- **Export jobs are asynchronous:** a job moves from `notStarted` through
  `inProgress` to `completed` or `failed`; the download link expires at
  `expirationDateTime`.

## Interop
- [`../maven/msal4j.md`](../maven/msal4j.md): acquiring the app-only token
  (`/.default` scope) from Java, and the Entra ID-token claim facts.
- `com.azure:azure-identity`: the credential layer the Graph SDKs accept.
- Intune and Conditional Access: device compliance reported to Entra is what a
  "require compliant device" Conditional Access control evaluates.

## Major lines
- **`v1.0`:** the current version, generally available and supported for
  production. Breaking changes ship only in a new version, and upstream
  declares a version or a GA API deprecated at least 24 months before removal.
  Additive changes (new nullable properties, new enum members, paging added to a
  collection, changed error codes or property order) are not breaking, so
  clients must tolerate unknown properties and enum values.
- **`beta`:** where APIs debut. Breaking changes and deprecations arrive "from
  time to time", promotion to v1.0 is not guaranteed, and "Use of beta APIs in
  production applications is not supported". An API marked "(preview)" behaves
  differently on beta or exists only there.

## Upstream docs
- Overview and reference: https://learn.microsoft.com/en-us/graph/api/overview
- Versioning and support: https://learn.microsoft.com/en-us/graph/versioning-and-support
- Paging: https://learn.microsoft.com/en-us/graph/paging
- Throttling: https://learn.microsoft.com/en-us/graph/throttling
- Service-specific limits: https://learn.microsoft.com/en-us/graph/throttling-limits
- JSON batching: https://learn.microsoft.com/en-us/graph/json-batching
- List users: https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0
- signInActivity: https://learn.microsoft.com/en-us/graph/api/resources/signinactivity?view=graph-rest-1.0
- List sign-ins: https://learn.microsoft.com/en-us/graph/api/signin-list?view=graph-rest-1.0
- userRegistrationDetails: https://learn.microsoft.com/en-us/graph/api/resources/userregistrationdetails?view=graph-rest-1.0
- Entra data retention: https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-reports-data-retention
- List managedDevices: https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-list?view=graph-rest-1.0
- complianceState: https://learn.microsoft.com/en-us/graph/api/resources/intune-devices-compliancestate?view=graph-rest-1.0
- Intune compliance settings: https://learn.microsoft.com/en-us/intune/device-security/compliance/overview
- Export Intune reports: https://learn.microsoft.com/en-us/intune/device-management/reports/export-graph-apis
- Available Intune reports: https://learn.microsoft.com/en-us/intune/device-management/reports/ref-graph-available-reports
- Java SDK: https://github.com/microsoftgraph/msgraph-sdk-java
