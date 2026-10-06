# Tool: live-contract-check-harness

> Project-agnostic capability notes, kept in the seed's tool corpus
> (`tool-corpus/README.md`). A portable skeleton: the generic part of the script
> runs as-is; a plant replaces the example groups with its own contracts.

## 0. Identity

- **Category:** testing
- **Name:** live-contract-check-harness
- **Language / runtime:** bash (3.2 or later), `curl` 7.55 or later (for
  `-H @file`), and `python3` with the standard library only, for JSON
- **Stability:** **portable**. The mode handling, the verdict model, the
  secret handling, the companion lint and the self-test are complete; the
  contract groups are examples to replace.

## 1. What it does

A dependency-light black-box harness that checks a deployed service from the
outside, contract by contract. Checks are grouped by the contract they hold
(a spec's contract, an acceptance criterion, a finding's fix). Each run says,
per group, which way the group is expected to come out:

- **`--red`**: the defect is still there, and the check must see it. A check
  that passes in RED mode is `RED-UNEXPECTED-GREEN`, and it **fails the run**:
  either the defect is already gone or the check does not discriminate.
- **`--green`**: the contract must hold. A failing check is `FAIL`.

That is the test-first cycle (`protocols/test-first.md`) for a contract only
a running deployment can show. Run the group `--red` before the fix ships,
and `--green` after. A check that never showed RED proved nothing when it
turns GREEN. The procedure around it (the choice between a deploy per
increment and a single deploy, the single RED run, interlocks, the
contracts that can go RED only after a deploy, the synthetic-data decision)
is `skill-corpus/deploy-gated-red-green.md`; this page is the `<HARNESS>`
that procedure names, and its verdicts are the ones that procedure relies
on.

Guards (checks marked `(guard)`) hold behavior that must not change, and they
must pass in either mode.

A companion static lint (`lint-harness.sh`) reads the harness's source and
fails it when a credential could reach a command line or a log.

## 2. Interface & invocation

```sh
read -rs E2E_A_PASSWORD; export E2E_A_USER=<synthetic user> E2E_A_PASSWORD
BASE=https://<host> bash contract-checks.sh --red ITEMS --green AUTH
BASE=https://<host> bash contract-checks.sh --green ALL
bash contract-checks.sh --plan --red ITEMS          # offline: no request, no credentials
bash lint-harness.sh contract-checks.sh             # the static lint
bash selftest.sh                                    # both, against a local synthetic service
```

- **Inputs:** `--red` and `--green` take a comma-separated group list or
  `ALL`; both may be given, for different groups. `BASE` is the service's
  base URL. Credentials come from the environment only, one pair per
  principal `P` listed in `PRINCIPALS`: `E2E_<P>_USER` and
  `E2E_<P>_PASSWORD` (read the password with `read -rs` and export it). An
  optional `CURL_INSECURE=1` allows a self-signed edge; verification is on by
  default. A check that is opt-in reads its own switch (the skeleton's
  `E2E_ENABLE_FAILED_LOGIN=1`).
- **Outputs:** the run start in UTC (RFC 3339, for a server-log `--since`),
  then one line per check, with the HTTP status and the first assertion that
  did not hold, then a `RESULT:` count line. Every row the run writes carries
  the synthetic prefix printed at the start (`E2E-<UTC timestamp>`), so it
  can be found and cleaned up. The verdicts:

  | verdict | meaning | fails the run |
  |---|---|---|
  | `PASS` / `FAIL` | a GREEN check, or a guard in either mode, held / did not | `FAIL` does |
  | `RED-OK` | a RED check saw the defect | no |
  | `RED-UNEXPECTED-GREEN` | a RED check saw no defect: it does not discriminate | yes |
  | `HARNESS-ERROR` | the check could not reach a verdict: no HTTP answer, or a value the request depends on was missing | yes |
  | `NOT-EXERCISED` | a precondition was absent: an opt-in check left off, data the target does not hold, a subject an earlier check did not create | no; record it |
  | `SKIPPED-INTERLOCK` | a damaging RED request was held back because no earlier check in the run confirmed the pre-fix state | no; record it |
  | `WARN spec-drift` | a RED check failed at a status other than the one the spec documents for the defect today | no; route it to the architect |

- **Exit codes:** `0` when there is no `FAIL`, no `RED-UNEXPECTED-GREEN` and
  no `HARNESS-ERROR`; `1` otherwise; `2` for a usage error or a preflight
  abort before any check ran, and for a harness that broke mid-run (an
  `ABORT harness error mid-run` line and no `RESULT:` line). A group listed
  in both `--red` and `--green` is a usage error.
- **`--plan`** prints the checks each selected group would run, in order,
  with no network and no credentials. Use it to review a run before spending
  a login on it.

## 3. Approach / algorithm

**Assertion chain, then a verdict.** A check sends its request, then calls
`h_reset` and one `h_req "<what must hold>" <command>` per assertion. The
first assertion that does not hold is remembered. `judge GROUP CHECK DETAIL
[RED_STATUS]` turns the chain into a verdict by the group's mode: in GREEN,
all held is `PASS`; in RED, all held is `RED-UNEXPECTED-GREEN` and anything
failing is `RED-OK`. `guard CHECK DETAIL` is `PASS` or `FAIL` whatever the
mode. `detail [STATUS]` names the status the verdict is about; a check that
made later requests (a snapshot after a write) passes the write's status.

**A RED is for the right reason or it is not a RED.** In RED mode any failed
assertion would otherwise count, including no answer at all, a mistyped
route or an expired token. Two rules narrow it. A status of `000` (curl got
no HTTP answer) is never `RED-OK`, nor `FAIL`: it is `HARNESS-ERROR` in
either mode. And each judged check passes `RED_STATUS`, the status the spec
documents for the defect today; when a RED run sees another, the run prints
`WARN spec-drift`. The warning does not fail the run: the procedure routes it
to the architect instead of editing the expectation. Until it is resolved,
that check's `RED-OK` is not recorded as its RED.

**A missing input is never a verdict.** A value the request depends on that
is empty or `null` makes the check `HARNESS-ERROR`, which fails the run,
never a product `FAIL`. Two helpers cover the two cases. `need VALUE CHECK
WHY` guards a shell value carried from an earlier answer (the id a create
returned). `py fields FILE f…` guards a request body built from a read: it
exits non-zero when a field the write depends on is absent or `null`. A body
built from a read response is not what the real client sends. One harness of
this kind copied a record from a read into its update request. The read
returned the record's id as `null`, the real client set the id from its own
state, and the update failed in the harness only. The same rule stops a
`null` id from becoming a request for `/items/null`.

**An absent precondition is recorded, not failed.** An opt-in check left
off, data the target does not hold, or a subject an earlier check did not
create reports `NOT-EXERCISED` with its reason. A damaging RED request that
no earlier check in the run cleared reports `SKIPPED-INTERLOCK`. Neither
fails the run, and both are counted in `RESULT:` and must be written into
the verification record with their reason.

**A preflight resolves the run's inputs.** After every principal has logged
in, the plant's `preflight` function resolves each id the checks need (a
known subject, the principals' permissions) and aborts with `die2` before
any check if one is missing. The skeleton derives an id guaranteed not to
exist as the largest id plus 100000.

**A status code alone does not prove a rejected write wrote nothing.**
Snapshot the collection before and after the write and compare:
`py delta BEFORE AFTER K` asserts the row count moved by exactly `K`, and
`py same-json A B` asserts nothing changed. The skeleton's
`ITEMS_2` (an update that must not add a row) and `ITEMS_3` (an update of a
missing item that must write nothing) show both.

**Secrets never reach argv, a log or a world-readable file.**

- `mktemp -d` creates the work directory `0700` by itself; the script's
  `umask 077` makes every file the shell creates in it `0600`.
- The EXIT trap removes the work directory on every exit; INT and TERM exit
  `2`, which runs it. The same trap turns any exit before the `RESULT:` line
  (a crash of the harness itself) into exit `2` with an `ABORT` line, so it
  never reads as a product `FAIL`.
- The login body is printed by the Python helper from the environment and
  piped to `curl --data @-`. Request bodies are files fed on stdin with
  `--data @-`.
- The bearer token is parsed from the login response by the helper, which
  writes the `Authorization:` line to a `0600` header file. Every request
  passes it as `-H @file`, so it is never an argument of any process.
- Tracing is never on: `set -x` would print the expanded command lines, and
  `curl -v` prints the header file's contents (`library-corpus/cli/curl.md`
  holds why).

**One login attempt per principal.** Each principal in `PRINCIPALS` logs in
once, into its own header file; a failure aborts with exit `2`. Retrying a
failed login against a live service can lock the account.

**Local preflight before the first request.** The script reads the major and
minor number from `curl --version` and aborts when it is older than 7.55. A
behavior probe cannot tell: an older curl accepts `-H @file`, but over HTTP
it then sends no `Authorization` header, every authorized check gets 401, and
in RED mode those would read as defects. It also checks that `python3`
exists, before it uses a login, and checks `BASE` and each credential
variable before any request.

**The static lint holds the secret rules over the source.** `lint-harness.sh`
first joins backslash continuation lines, then fails the file when, on any
non-comment `curl` command, there is `-u`, `--user`, `--oauth2-bearer` or the
word `bearer`, `password` or `token`; an inline body (`-d` or a short-flag
cluster ending in `d` such as `-sd`, `--data`, `--data-ascii`,
`--data-binary`, `--data-raw`, `--data-urlencode`, `--json`, not followed by
`@`); or verbose output (`-v` or a cluster holding it such as `-sv`,
`--verbose`, `--trace`, `--trace-ascii`). It also fails a `set -x` or a `-x`
shebang, and the absence of `--data @-`, `-H @`, a `umask 077` line or a
`trap … EXIT`. The rules are per command on purpose: a helper that touches a
token runs as its own command, outside any `curl` command.

## 4. Portable vs blueprint

- **Portable (use as-is):** everything below the `generic part` marker in
  `contract-checks.sh`; `lint-harness.sh`; the shape of `selftest.sh`.
- **Project-specific (fill in):** `GROUPS_ALL`, one `plan_<GROUP>` and one
  `run_<GROUP>` function per group; `PRINCIPALS` (one login and one header
  file each; `N` is the anonymous caller); `LOGIN_PATH` and the token field
  in the helper's `login-parse`; `preflight`; each judged check's documented
  RED status; extra helper commands for the JSON the checks read; the
  synthetic service in `selftest.sh`. Group and principal names are letters,
  digits and `_`, because each becomes part of a shell variable name.

```bash
#!/usr/bin/env bash
# contract-checks.sh: live black-box checks of a deployed service, grouped by
# contract, each group run in RED mode (the defect must still show) or GREEN
# mode (the contract must hold). Needs bash, curl >= 7.55 (-H @file) and
# python3 (stdlib only). Run it from the operator's machine, not the target.
#
#   BASE=https://<host> bash contract-checks.sh --red ITEMS --green AUTH
#   BASE=https://<host> bash contract-checks.sh --green ALL
#   bash contract-checks.sh --plan --red ITEMS     # offline: no request, no credentials
#
# Credentials come from the environment only: E2E_<P>_USER, E2E_<P>_PASSWORD
# for each principal P in PRINCIPALS.
#   read -rs E2E_A_PASSWORD; export E2E_A_PASSWORD
# Bodies go on stdin (--data @-); each Authorization header lives in a 0600
# file inside a 0700 work dir (-H @file); the work dir is removed on exit.
# Never add tracing (set -x, curl -v) to this script: lint-harness.sh fails it.
#
# Exit: 0 = no FAIL, no RED-UNEXPECTED-GREEN, no HARNESS-ERROR;
#       1 = otherwise; 2 = usage or preflight abort before any check,
#       or the harness itself broke mid-run (no RESULT line).
set -euo pipefail
umask 077

# ---------------------------------------------------------------- plant part --
GROUPS_ALL="AUTH ITEMS"                       # the contract groups, in run order
PRINCIPALS="A"                                # one login each; N is the anonymous caller
LOGIN_PATH=/login
plan_AUTH()  { echo "AUTH_1_LOGIN_GRANTS_ITEM_LIST AUTH_2_ANONYMOUS_LIST_IS_401(guard) AUTH_3_WRONG_PASSWORD_IS_401(guard,opt-in)"; }
plan_ITEMS() { echo "ITEMS_1_CREATED_ITEM_READS_BACK_ITS_NAME ITEMS_2_RENAME_UPDATES_IN_PLACE ITEMS_3_UPDATE_OF_A_MISSING_ITEM_WRITES_NOTHING(guard)"; }

preflight() {          # resolve every id the checks need; abort before any check if one is missing
  req A GET /items
  [ "$CODE" = 200 ] || die2 "preflight: GET /items -> HTTP $CODE"
  MISSING_ID=$(( $(py max-id "$RESP") + 100000 ))   # an id guaranteed not to exist
}

run_AUTH() {
  local c
  req N GET /items; h_reset
  h_req "status 401" test "$CODE" = 401
  guard AUTH_2_ANONYMOUS_LIST_IS_401 "$(detail)"
  req A GET /items; h_reset
  h_req "status 200" test "$CODE" = 200
  h_req "body is a JSON list" py is-list "$RESP"
  judge AUTH AUTH_1_LOGIN_GRANTS_ITEM_LIST "$(detail)" 401
  c=AUTH_3_WRONG_PASSWORD_IS_401
  if [ "${E2E_ENABLE_FAILED_LOGIN:-0}" != 1 ]; then  # a failed login counts toward a lockout
    not_exercised "$c" "opt-in, off (set E2E_ENABLE_FAILED_LOGIN=1)"
    return 0
  fi
  py login-body A wrong >"$WORKDIR/bad-login.json"
  req N POST "$LOGIN_PATH" "$WORKDIR/bad-login.json"; h_reset
  h_req "status 401" test "$CODE" = 401
  guard "$c" "$(detail)"
}

ITEM_ID=""; ITEM_READ=""
run_ITEMS() {
  local c=ITEMS_1_CREATED_ITEM_READS_BACK_ITS_NAME body="$WORKDIR/item.json" code
  local before="$WORKDIR/items0.json" after="$WORKDIR/items1.json"
  ITEM_READ="$WORKDIR/item-read.json"
  py write-json "$body" "{\"name\": \"$PFX-item\"}"
  req A POST /items "$body"
  ITEM_ID=$(py get "$RESP" id)
  if need "$ITEM_ID" "$c" "POST /items -> HTTP $CODE returned no id"; then
    req A GET "/items/$ITEM_ID"; cp "$RESP" "$ITEM_READ"; h_reset
    h_req "status 200" test "$CODE" = 200
    h_req "name = $PFX-item" test "$(py get "$RESP" name)" = "$PFX-item"
    judge ITEMS "$c" "$(detail)" 200
  else
    ITEM_ID=""
  fi

  c=ITEMS_2_RENAME_UPDATES_IN_PLACE      # body built from a read: assert its fields first
  if [ -z "$ITEM_ID" ]; then
    not_exercised "$c" "no item was created in this run"
  elif ! py fields "$ITEM_READ" id name; then
    harness_error "$c" "GET /items/$ITEM_ID lacks id or name; a body built from it is not what the client sends"
  else
    py patch-json "$body" "$ITEM_READ" "{\"name\": \"$PFX-renamed\"}"
    req A GET /items; cp "$RESP" "$before"
    req A PUT "/items/$ITEM_ID" "$body"; code=$CODE
    req A GET /items; cp "$RESP" "$after"; h_reset
    h_req "status 200" test "$code" = 200
    h_req "no row added" py delta "$before" "$after" 0
    judge ITEMS "$c" "$(detail "$code")" 200
  fi
  # A damaging RED request goes out only after an earlier check in this run
  # confirmed the pre-fix state; otherwise:  interlock "$c" "pre-fix state not confirmed"

  c=ITEMS_3_UPDATE_OF_A_MISSING_ITEM_WRITES_NOTHING
  py write-json "$body" "{\"id\": $MISSING_ID, \"name\": \"$PFX-ghost\"}"
  req A GET /items; cp "$RESP" "$before"
  req A PUT "/items/$MISSING_ID" "$body"; code=$CODE
  req A GET /items; cp "$RESP" "$after"; h_reset
  h_req "status 404" test "$code" = 404
  h_req "collection unchanged" py same-json "$before" "$after"
  guard "$c" "$(detail "$code")"
}

# ------------------------------------------------------------ generic part --
RED=$'\e[31m'; GRN=$'\e[32m'; YEL=$'\e[33m'; NC=$'\e[0m'
[ -t 1 ] || { RED=""; GRN=""; YEL=""; NC=""; }
die2() { echo "${RED}ABORT${NC} $1" >&2; exit 2; }
usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; }

phase() { local v="PH_$1"; printf '%s' "${!v:-}"; }
set_phase() {                                 # set_phase red|green "G1,G2" | ALL
  local ph=$1 list=$2 g cur arr
  [ "$list" = ALL ] && list=${GROUPS_ALL// /,}
  IFS=, read -r -a arr <<<"$list"
  [ "${#arr[@]}" -gt 0 ] || die2 "empty group list for --$ph"
  for g in "${arr[@]}"; do
    case " $GROUPS_ALL " in *" $g "*) ;; *) die2 "unknown group '$g' (known: $GROUPS_ALL, or ALL)";; esac
    cur=$(phase "$g")
    [ -z "$cur" ] || [ "$cur" = "$ph" ] || die2 "group $g listed in both --red and --green"
    printf -v "PH_$g" '%s' "$ph"
  done
}

PLAN=0
[ "$#" -gt 0 ] || { usage; die2 "no mode given (need --red and/or --green)"; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --red)   [ "$#" -ge 2 ] || die2 "--red needs a group list";   set_phase red "$2"; shift 2;;
    --green) [ "$#" -ge 2 ] || die2 "--green needs a group list"; set_phase green "$2"; shift 2;;
    --plan)  PLAN=1; shift;;
    -h|--help) usage; exit 0;;
    *) die2 "unknown argument '$1'";;
  esac
done
ACTIVE=0
for g in $GROUPS_ALL; do [ -n "$(phase "$g")" ] && ACTIVE=1; done
[ "$ACTIVE" = 1 ] || die2 "no group selected"

# Local preflight first, so an unusable curl never spends a login attempt.
# A version check: an older curl sends a literal "@file" header, not the file.
curl_ok() {
  local v; v=$(curl --version 2>/dev/null | sed -n '1s/^curl \([0-9][0-9]*\)\.\([0-9][0-9]*\).*/\1 \2/p')
  set -- $v
  [ "${1:-0}" -gt 7 ] || { [ "${1:-0}" -eq 7 ] && [ "${2:-0}" -ge 55 ]; }
}
curl_ok || die2 "local curl is missing or older than 7.55 (needs -H @file)"
command -v python3 >/dev/null 2>&1 || die2 "python3 not found"

if [ "$PLAN" = 1 ]; then
  echo "contract checks: PLAN (offline; no request is sent)"
  echo "target would be: ${BASE:-<BASE unset>}"
  for g in $GROUPS_ALL; do
    ph=$(phase "$g")
    if [ -z "$ph" ]; then echo "  $g: skipped"; continue; fi
    echo "  $g: --$ph"
    for c in $("plan_$g"); do echo "      $c"; done
  done
  exit 0
fi

[ -n "${BASE:-}" ] || die2 "BASE is not set"
for p in $PRINCIPALS; do
  for v in "E2E_${p}_USER" "E2E_${p}_PASSWORD"; do
    [ -n "${!v:-}" ] || die2 "missing environment variable $v (never put it in a file or argv)"
  done
done
CURL_K=(); [ "${CURL_INSECURE:-0}" = 1 ] && CURL_K=(-k)   # opt-in, for a self-signed edge
WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/contract.XXXXXX")
DONE=0
trap 'rc=$?; rm -rf "$WORKDIR"; if [ "$DONE" != 1 ] && [ "$rc" != 2 ]; then echo "${RED}ABORT${NC} harness error mid-run (exit $rc, no RESULT line)" >&2; exit 2; fi' EXIT
trap 'exit 2' INT TERM
H="$WORKDIR/helper.py"; RESP="$WORKDIR/resp"

cat >"$H" <<'PY'
import json, os, sys
def load(p):
    t = open(p, encoding="utf-8", errors="replace").read()
    try:
        return json.loads(t) if t.strip() else None
    except ValueError:
        return t
def wr(p, text):
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
def rows(p):
    d = load(p)
    return d if isinstance(d, list) else None
cmd, a = sys.argv[1], sys.argv[2:]
if cmd == "login-body":                 # login-body P [wrong]: credentials from the environment only
    pw = os.environ["E2E_%s_PASSWORD" % a[0]] + ("-wrong" if a[1:] == ["wrong"] else "")
    sys.stdout.write(json.dumps({"username": os.environ["E2E_%s_USER" % a[0]], "password": pw}))
elif cmd == "login-parse":              # stdin = login response; writes the header file
    try:
        d = json.loads(sys.stdin.read() or "null")
    except ValueError:
        d = None
    tok = d.get("token") if isinstance(d, dict) else None
    if not tok:
        sys.exit(1)
    wr(a[0], "Authorization: Bearer %s\n" % tok)
elif cmd == "get":                      # get FILE dotted.path -> value, or "" if absent/null
    o = load(a[0])
    for k in a[1].split("."):
        o = o.get(k) if isinstance(o, dict) else None
    sys.stdout.write("" if o is None else (json.dumps(o) if isinstance(o, (dict, list)) else str(o)))
elif cmd == "fields":                   # fields FILE f...: each field present and not null
    d = load(a[0])
    sys.exit(0 if isinstance(d, dict) and all(d.get(f) is not None for f in a[1:]) else 1)
elif cmd == "is-list":
    sys.exit(0 if isinstance(load(a[0]), list) else 1)
elif cmd == "max-id":                   # max-id FILE: largest "id" in a list (0 if none)
    ids = [r.get("id") for r in rows(a[0]) or [] if isinstance(r, dict)]
    print(max([i for i in ids if isinstance(i, int)] or [0]))
elif cmd == "delta":                    # delta BEFORE AFTER K: len(after) - len(before) == K
    b, f = rows(a[0]), rows(a[1])
    sys.exit(0 if b is not None and f is not None and len(f) - len(b) == int(a[2]) else 1)
elif cmd == "same-json":                # same-json A B: equal JSON (a rejected write wrote nothing)
    sys.exit(0 if load(a[0]) == load(a[1]) else 1)
elif cmd == "write-json":               # validates the JSON before it is sent
    wr(a[0], json.dumps(json.loads(a[1])))
elif cmd == "patch-json":               # patch-json OUT SRC JSON: SRC object with JSON's keys set
    d = load(a[1])
    if not isinstance(d, dict):
        sys.exit(1)
    d.update(json.loads(a[2]))
    wr(a[0], json.dumps(d))
else:
    sys.exit("unknown helper command %s" % cmd)
PY
py() { python3 "$H" "$@"; }

n_pass=0; n_fail=0; n_redok=0; n_ueg=0; n_herr=0; n_nx=0; n_skip=0; n_warn=0
v_pass()  { echo "${GRN}  PASS${NC} $1"; n_pass=$((n_pass+1)); }
v_fail()  { echo "${RED}  FAIL${NC} $1"; n_fail=$((n_fail+1)); }
v_redok() { echo "${YEL}  RED-OK${NC} $1"; n_redok=$((n_redok+1)); }
v_ueg()   { echo "${RED}  RED-UNEXPECTED-GREEN${NC} $1"; n_ueg=$((n_ueg+1)); }
harness_error() { echo "${RED}  HARNESS-ERROR${NC} $1 - $2"; n_herr=$((n_herr+1)); }
not_exercised() { echo "${YEL}  NOT-EXERCISED${NC} $1 - $2"; n_nx=$((n_nx+1)); }
interlock()     { echo "${YEL}  SKIPPED-INTERLOCK${NC} $1 - $2"; n_skip=$((n_skip+1)); }
spec_drift()    { echo "${YEL}  WARN spec-drift${NC} $1"; n_warn=$((n_warn+1)); }

H_OK=1; H_WHY=""
h_reset() { H_OK=1; H_WHY=""; }
h_req() {                                     # h_req "what must hold" cmd args...
  local d=$1; shift
  if [ "$H_OK" = 1 ] && ! "$@"; then H_OK=0; H_WHY=$d; fi
}
detail() {                                    # detail [STATUS]: defaults to the last request's
  local s=${1:-$CODE}
  if [ "$H_OK" = 1 ]; then echo "HTTP $s"; else echo "HTTP $s; not: $H_WHY"; fi
}
status_of() { local s=${1#HTTP }; printf '%s' "${s:0:3}"; }   # the status a detail is about
judge() {                                     # judge GROUP CHECK DETAIL [DOCUMENTED_RED_STATUS]
  local s; s=$(status_of "$3")
  if [ "$s" = 000 ]; then harness_error "$2" "$3 (no HTTP answer)"; return 0; fi
  if [ "$(phase "$1")" = green ]; then
    if [ "$H_OK" = 1 ]; then v_pass "$2 - $3"; else v_fail "$2 - $3"; fi
  else
    if [ "$H_OK" = 1 ]; then v_ueg "$2 - $3 (the check does not discriminate)"; else v_redok "$2 - $3"; fi
    if [ -n "${4:-}" ] && [ "$s" != "$4" ]; then
      spec_drift "$2: documented RED status $4, observed $s (route to the architect)"
    fi
  fi
}
guard() {                                     # guard CHECK DETAIL: PASS or FAIL in either mode
  local s; s=$(status_of "$2")
  if [ "$s" = 000 ]; then harness_error "$1 (guard)" "$2 (no HTTP answer)"
  elif [ "$H_OK" = 1 ]; then v_pass "$1 (guard) - $2"; else v_fail "$1 (guard) - $2"; fi
}
need() {                                      # need VALUE CHECK WHY: a missing input is never a verdict
  case "$1" in ''|null|None) harness_error "$2" "$3"; return 1;; esac
}

CODE=""
hdr_of() {
  case " $PRINCIPALS " in *" $1 "*) echo "$WORKDIR/hdr_$1"; return;; esac
  [ "$1" = N ] && { echo /dev/null; return; }
  die2 "bad principal $1"
}
req() {                                       # req PRINCIPAL METHOD PATH [BODYFILE]
  local h; h=$(hdr_of "$1"); : >"$RESP"
  if [ -n "${4:-}" ]; then
    CODE=$(curl -s ${CURL_K[@]+"${CURL_K[@]}"} --max-time 25 -o "$RESP" -w '%{http_code}' -H @"$h" -H 'Content-Type: application/json' -X "$2" --data @- "$BASE$3" <"$4") || CODE=000
  else
    CODE=$(curl -s ${CURL_K[@]+"${CURL_K[@]}"} --max-time 25 -o "$RESP" -w '%{http_code}' -H @"$h" -X "$2" "$BASE$3") || CODE=000
  fi
}
login() {                                     # login PRINCIPAL: exactly one attempt, no retry
  CODE=$(py login-body "$1" | curl -s ${CURL_K[@]+"${CURL_K[@]}"} --max-time 25 -o "$RESP" -w '%{http_code}' -H 'Content-Type: application/json' -X POST --data @- "$BASE$LOGIN_PATH") || CODE=000
  [ "$CODE" = 200 ] || die2 "preflight: login $1 -> HTTP $CODE (one attempt only; not retried)"
  py login-parse "$WORKDIR/hdr_$1" <"$RESP" || die2 "preflight: no token in the login response of $1"
  : >"$RESP"
}

RUN_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)      # RFC 3339, for a server-log --since
PFX="E2E-$(printf '%s' "$RUN_START" | tr -d ':-')"   # every row this run writes carries it
echo "contract checks; target: $BASE; run start (UTC): $RUN_START; synthetic prefix: $PFX"
for g in $GROUPS_ALL; do ph=$(phase "$g"); echo "  group $g: ${ph:-skipped}"; done
for p in $PRINCIPALS; do login "$p"; done
preflight
for g in $GROUPS_ALL; do
  if [ -n "$(phase "$g")" ]; then "run_$g"; fi
done

echo "RESULT: $n_pass PASS, $n_redok RED-OK, $n_fail FAIL, $n_ueg RED-UNEXPECTED-GREEN, $n_herr HARNESS-ERROR, $n_nx NOT-EXERCISED, $n_skip SKIPPED-INTERLOCK, $n_warn WARN spec-drift"
DONE=1
if [ "$n_fail" -eq 0 ] && [ "$n_ueg" -eq 0 ] && [ "$n_herr" -eq 0 ]; then exit 0; fi
exit 1
```

```bash
#!/usr/bin/env bash
# lint-harness.sh FILE: static checks that a live-test shell script keeps its
# secrets off argv and out of logs. Exit 0 PASS, 1 FAIL, 2 usage.
set -u
[ "$#" -eq 1 ] || { echo "usage: lint-harness.sh <script>" >&2; exit 2; }
f=$1
[ -f "$f" ] || { echo "no such file: $f" >&2; exit 2; }
rc=0; fail() { echo "FAIL $1"; rc=1; }
# Join backslash continuations first, so a flag on a second line is still read.
code=$(awk '{ if (sub(/\\$/, "")) { buf = buf $0 " "; next } print buf $0; buf = "" }' "$f" \
  | grep -nE '^[^#]*curl' || true)
grep -iE '[[:space:]](-[a-zA-Z]*u|--user|--oauth2-bearer)([[:space:]]|=|$)|bearer|password|token' <<<"$code" \
  && fail "a credential or token on a curl command line"
grep -E '[[:space:]](-[a-zA-Z]*d|--data(-ascii|-binary|-raw|-urlencode)?|--json)([[:space:]]+|=)?[^@[:space:]=-]' <<<"$code" \
  && fail "an inline request body on a curl command line (use --data @-)"
grep -E '[[:space:]](-[a-zA-Z]*v[a-zA-Z]*|--verbose|--trace(-ascii)?)([[:space:]]|=|$)' <<<"$code" \
  && fail "curl verbose or trace output (prints the header file's contents)"
grep -nE '^[[:space:]]*set[[:space:]].*(-[a-zA-Z]*x|xtrace)|^#!.*[[:space:]]-[a-zA-Z]*x' "$f" && fail "set -x"
grep -qE -- '--data @-' "$f" || fail "no body fed via --data @-"
grep -qE -- '-H[[:space:]]+@' "$f" || fail "no header file fed via -H @<file>"
grep -qE '^[[:space:]]*umask[[:space:]]+0?077' "$f" || fail "no umask 077 before the work directory is created"
grep -qE '^[[:space:]]*trap[[:space:]].*EXIT' "$f" || fail "no trap ... EXIT cleanup"
[ "$rc" -eq 0 ] && echo "lint-harness: PASS ($f)" || echo "lint-harness: FAIL ($f)"
exit "$rc"
```

```bash
#!/usr/bin/env bash
# selftest.sh: proves contract-checks.sh and lint-harness.sh against a local
# synthetic service. Run from the directory holding both scripts.
set -uo pipefail
umask 077
T=$(mktemp -d); SRV=""; trap 'kill "$SRV" 2>/dev/null; rm -rf "$T"' EXIT
cat >"$T/svc.py" <<'PY'
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
MODE = os.environ.get("MODE", "fixed")   # defect, drift, fixed, null-id, read-null-id, drop, nolist
items = {}
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def authed(self):
        return self.headers.get("Authorization") == "Bearer t0k3n"
    def body(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
    def item_id(self):
        tail = self.path.rsplit("/", 1)[1]
        return int(tail) if tail.isdigit() else None
    def do_POST(self):
        body = self.body()
        if self.path == "/login":
            ok = body == {"username": "e2e", "password": "pw"}
            return self.send(200 if ok else 401, {"token": "t0k3n"} if ok else {})
        if self.path == "/items" and self.authed():
            if MODE == "null-id":
                return self.send(201, {"id": None})
            i = len(items) + 1; items[i] = dict(body, id=i); return self.send(201, {"id": i})
        self.send(401, {})
    def do_PUT(self):
        body = self.body(); i = self.item_id()
        if not self.authed():
            return self.send(401, {})
        if i not in items:
            return self.send(404, {})
        if MODE in ("defect", "drift"):           # the bug: an update appends a copy
            j = len(items) + 1; items[j] = dict(body, id=j); return self.send(200, items[j])
        if body.get("id") != i:
            return self.send(400, {"error": "id mismatch"})
        items[i] = body; self.send(200, body)
    def do_GET(self):
        if not self.authed():
            return self.send(401, {})
        if self.path == "/items":
            return self.send(503 if MODE == "nolist" else 200, list(items.values()))
        i = self.item_id()
        if i not in items:
            return self.send(404, {})
        if MODE == "drop":                         # no HTTP answer at all
            self.close_connection = True; return
        item = dict(items[i])
        if MODE in ("defect", "drift"):            # the bug the RED run must still see
            item["name"] = "truncated"
        if MODE == "read-null-id":                 # the read omits what the write needs
            item["id"] = None
        self.send(500 if MODE == "drift" else 200, item)
s = HTTPServer(("127.0.0.1", 0), H); print(s.server_port, flush=True); s.serve_forever()
PY
start() {
  : >"$T/port"; MODE=$1 python3 "$T/svc.py" >"$T/port" & SRV=$!
  local n=0; while [ ! -s "$T/port" ] && [ "$n" -lt 100 ]; do sleep 0.1; n=$((n+1)); done
  export BASE="http://127.0.0.1:$(cat "$T/port")"
}
stop() { kill "$SRV"; wait "$SRV" 2>/dev/null; }
fails=0
expect() {   # expect RC "label" cmd...
  local want=$1 what=$2; shift 2
  "$@" >"$T/out" 2>&1; local got=$?
  if [ "$got" = "$want" ]; then echo "ok   $what (exit $got)"; else
    echo "FAIL $what: exit $got, wanted $want"; cat "$T/out"; fails=$((fails+1)); fi
}
has()    { grep -q "$1" "$T/out" || { echo "FAIL no line: $1"; cat "$T/out"; fails=$((fails+1)); }; }
hasnot() { ! grep -q "$1" "$T/out" || { echo "FAIL unwanted line: $1"; fails=$((fails+1)); }; }
export E2E_A_USER=e2e E2E_A_PASSWORD=pw
expect 2 "no mode is a usage error"            bash contract-checks.sh
expect 2 "group in both --red and --green"     bash contract-checks.sh --red AUTH --green AUTH
expect 2 "unknown group"                       bash contract-checks.sh --green NOPE
expect 0 "--plan offline without BASE or credentials" env -u E2E_A_PASSWORD bash contract-checks.sh --plan --red ITEMS
has "ITEMS_1_CREATED_ITEM_READS_BACK_ITS_NAME"
start defect
expect 2 "missing credential aborts before any request" env -u E2E_A_PASSWORD bash contract-checks.sh --green ALL
expect 0 "RED-OK while the defect is present"  bash contract-checks.sh --green AUTH --red ITEMS
has "RED-OK ITEMS_1"; has "RED-OK ITEMS_2"; has "NOT-EXERCISED AUTH_3"; hasnot "WARN spec-drift ITEMS"
expect 1 "GREEN fails while the defect is present" bash contract-checks.sh --green ALL
stop; start fixed
expect 1 "RED-UNEXPECTED-GREEN fails the run"  bash contract-checks.sh --red ITEMS
has "RED-UNEXPECTED-GREEN ITEMS_1"
expect 0 "GREEN passes once fixed; NOT-EXERCISED does not fail" bash contract-checks.sh --green ALL
has "PASS ITEMS_3_UPDATE_OF_A_MISSING_ITEM_WRITES_NOTHING (guard)"; has "NOT-EXERCISED AUTH_3"
expect 0 "an opt-in check runs when enabled"   env E2E_ENABLE_FAILED_LOGIN=1 bash contract-checks.sh --green AUTH
has "PASS AUTH_3_WRONG_PASSWORD_IS_401 (guard)"
stop; start drift
expect 0 "a RED at an undocumented status warns of spec drift" bash contract-checks.sh --red ITEMS
has "WARN spec-drift ITEMS_1_.*documented RED status 200, observed 500"
stop; start drop
expect 1 "no HTTP answer is a HARNESS-ERROR, never RED-OK" bash contract-checks.sh --red ITEMS
has "HARNESS-ERROR ITEMS_1"; hasnot "RED-OK ITEMS_1"
stop; start null-id
expect 1 "a null id from a create is a HARNESS-ERROR" bash contract-checks.sh --green ITEMS
has "HARNESS-ERROR ITEMS_1"; has "NOT-EXERCISED ITEMS_2"
stop; start read-null-id
expect 1 "a body built from a read with a null id is a HARNESS-ERROR, not a FAIL" bash contract-checks.sh --green ITEMS
has "HARNESS-ERROR ITEMS_2"; hasnot "FAIL ITEMS_2"
stop; start nolist
expect 2 "a failed preflight aborts before any check" bash contract-checks.sh --green ALL
hasnot "PASS"
stop; start fixed
expect 2 "a failed login aborts, one attempt"  env E2E_A_PASSWORD=wrong bash contract-checks.sh --green AUTH
sed 's/^run_ITEMS() {$/run_ITEMS() { false/' contract-checks.sh >"$T/crash.sh"
expect 2 "a harness crash mid-run exits 2, not 1" bash "$T/crash.sh" --green ITEMS
has "harness error mid-run"; hasnot "RESULT:"
stop
expect 0 "lint passes the harness"             bash lint-harness.sh contract-checks.sh
expect 2 "lint with no argument is a usage error" bash lint-harness.sh
for bad in 'curl -s -H "Authorization: Bearer $T" "$BASE/x"' \
           'curl -s -d "{\"a\":1}" "$BASE/x"' 'set -x' 'curl -v -H @"$h" "$BASE/x"' \
           'curl -sv -H @"$h" "$BASE/x"' 'curl -s -sd "{\"a\":1}" "$BASE/x"' \
           'curl -s --data-ascii "{\"a\":1}" "$BASE/x"' \
           $'curl -s -o /dev/null \\\n  -H "Authorization: Bearer $T" "$BASE/x"' \
           $'curl -s -o /dev/null \\\n  -v "$BASE/x"'; do
  { cat contract-checks.sh; printf '%s\n' "$bad"; } >"$T/bad.sh"
  expect 1 "lint fails a planted: ${bad//$'\n'/ }" bash lint-harness.sh "$T/bad.sh"
done
grep -v '^umask 077' contract-checks.sh >"$T/nou.sh"
expect 1 "lint fails a missing umask"          bash lint-harness.sh "$T/nou.sh"
[ "$fails" -eq 0 ] && echo "selftest: PASS" || echo "selftest: $fails FAIL"
[ "$fails" -eq 0 ]
```

Recorded run of the self-test on bash 5.3 with curl 8.22; the same
self-test also passes, all lines `ok`, on bash 3.2.57 with curl 8.14 in a
container:

```text
$ bash selftest.sh
ok   no mode is a usage error (exit 2)
ok   group in both --red and --green (exit 2)
ok   unknown group (exit 2)
ok   --plan offline without BASE or credentials (exit 0)
ok   missing credential aborts before any request (exit 2)
ok   RED-OK while the defect is present (exit 0)
ok   GREEN fails while the defect is present (exit 1)
ok   RED-UNEXPECTED-GREEN fails the run (exit 1)
ok   GREEN passes once fixed; NOT-EXERCISED does not fail (exit 0)
ok   an opt-in check runs when enabled (exit 0)
ok   a RED at an undocumented status warns of spec drift (exit 0)
ok   no HTTP answer is a HARNESS-ERROR, never RED-OK (exit 1)
ok   a null id from a create is a HARNESS-ERROR (exit 1)
ok   a body built from a read with a null id is a HARNESS-ERROR, not a FAIL (exit 1)
ok   a failed preflight aborts before any check (exit 2)
ok   a failed login aborts, one attempt (exit 2)
ok   a harness crash mid-run exits 2, not 1 (exit 2)
ok   lint passes the harness (exit 0)
ok   lint with no argument is a usage error (exit 2)
ok   lint fails a planted: curl -s -H "Authorization: Bearer $T" "$BASE/x" (exit 1)
ok   lint fails a planted: curl -s -d "{\"a\":1}" "$BASE/x" (exit 1)
ok   lint fails a planted: set -x (exit 1)
ok   lint fails a planted: curl -v -H @"$h" "$BASE/x" (exit 1)
ok   lint fails a planted: curl -sv -H @"$h" "$BASE/x" (exit 1)
ok   lint fails a planted: curl -s -sd "{\"a\":1}" "$BASE/x" (exit 1)
ok   lint fails a planted: curl -s --data-ascii "{\"a\":1}" "$BASE/x" (exit 1)
ok   lint fails a planted: curl -s -o /dev/null \   -H "Authorization: Bearer $T" "$BASE/x" (exit 1)
ok   lint fails a planted: curl -s -o /dev/null \   -v "$BASE/x" (exit 1)
ok   lint fails a missing umask (exit 1)
selftest: PASS
```

And `--plan` with no `BASE` and no credentials:

```text
$ bash contract-checks.sh --plan --red ITEMS --green AUTH
contract checks: PLAN (offline; no request is sent)
target would be: <BASE unset>
  AUTH: --green
      AUTH_1_LOGIN_GRANTS_ITEM_LIST
      AUTH_2_ANONYMOUS_LIST_IS_401(guard)
      AUTH_3_WRONG_PASSWORD_IS_401(guard,opt-in)
  ITEMS: --red
      ITEMS_1_CREATED_ITEM_READS_BACK_ITS_NAME
      ITEMS_2_RENAME_UPDATES_IN_PLACE
      ITEMS_3_UPDATE_OF_A_MISSING_ITEM_WRITES_NOTHING(guard)
```

The version preflight was also run against stand-in `curl` binaries that
print a 7.47.0 and a 7.55.0 version line: the first aborts with exit `2`,
the second passes. A real pre-7.55 curl was not run in this pass.

## 5. Pitfalls and sharp edges

- **A RED run that passes is not good news.** `RED-UNEXPECTED-GREEN` means
  the check cannot see the defect it was written for, or the defect is
  already gone. Either way the later GREEN proves nothing until the check is
  fixed. It fails the run on purpose.
- **A value carried forward from a response can be `null`.** Guard a shell
  value with `need` and a body built from a read with `py fields`; never send
  either unchecked. Build each request the way the real client builds it.
- **A RED check without its documented status cannot tell the defect from a
  typo.** Pass `RED_STATUS` to every judged check, and read a
  `WARN spec-drift` line before you record the RED.
- **Verbose output undoes the header file.** `library-corpus/cli/curl.md`
  holds why; the consequence here is that the lint fails `-v` and `--trace`
  on a `curl` command, so never debug the harness with them against a real
  account.
- **Run from the operator's machine, not the target host.** The checks are
  the client's view: run on the target, they bypass the edge they are meant
  to cross.
- **Writes on a live system stay.** Every row a run creates carries the
  synthetic prefix; record the ids the run printed, and agree with the owner
  beforehand that synthetic rows may stay or how they are removed.
- **State-destroying flows on a shared account** are covered by
  `tool-corpus/testing/http-smoke-suite.md` §5. For this harness the
  concrete one is repeated failed logins, which is why each principal logs
  in once and the wrong-password check is opt-in. Use a dedicated synthetic
  account (`tool-corpus/ops/disposable-test-identity-provisioner.md`).
- **`-k` hides a broken certificate.** It is opt-in (`CURL_INSECURE=1`) and
  only for an edge whose self-signed certificate you put there yourself.
- **Empty arrays and `set -u` on bash 3.2.** `"${arr[@]}"` on an empty array
  is an unbound-variable error before bash 4.4 (3.2 is the macOS system
  bash). The skeleton expands `CURL_K` as `${CURL_K[@]+"${CURL_K[@]}"}` for
  that reason.

## 6. Tests that cover it

`selftest.sh` starts a synthetic JSON service on a free local port in seven
variants (the defect present; the defect answering at an undocumented
status; fixed; a create returning a `null` id; a read returning a `null` id;
a read that gets no HTTP answer; a list that fails the preflight) and
asserts: no mode, a group in both modes and an unknown group exit `2`;
`--plan` runs with no `BASE` and no password and lists the checks; a missing
credential exits `2` before any request; RED mode reports `RED-OK` while the
defect is present and `RED-UNEXPECTED-GREEN` (exit `1`) once it is gone;
GREEN mode fails while the defect is present and passes once it is gone,
with an opt-in check left off as `NOT-EXERCISED` and exit `0`; the opt-in
check passes when switched on; a RED at an undocumented status prints `WARN
spec-drift`; no HTTP answer is `HARNESS-ERROR`, never `RED-OK`; a `null` id
from a create is `HARNESS-ERROR` and the check that depends on it
`NOT-EXERCISED`; a body built from a read with a `null` id is
`HARNESS-ERROR`, not `FAIL`; a failed preflight and a failed login abort
with `2`; a harness crash mid-run exits `2` with no `RESULT:` line. For the
lint: the harness passes; no argument exits `2`; a bearer header, an inline
body (`-d`, `-sd`, `--data-ascii`), `set -x`, verbose output (`-v`, `-sv`),
a bearer header or `-v` on a continuation line, and a missing `umask 077`
each fail.

- **How to run the tests:** `bash selftest.sh` from the directory holding
  the three scripts (exit 0 on pass).

## 7. References & neighbours

- **Related tools:** `tool-corpus/testing/http-smoke-suite.md` (whether the
  service serves at all, with no RED/GREEN modes);
  `tool-corpus/testing/in-network-e2e-harness.md` (end-to-end flows driven
  from inside the container network);
  `tool-corpus/ops/env-secret-rotation.md` (the same argv and tracing rules for
  a tool that writes secrets);
  `tool-corpus/testing/test-hygiene-lint.md` (a sibling source lint: test
  smells, where `lint-harness.sh` checks secret handling).
- **Library pages:** `library-corpus/cli/curl.md` (`-H @file`, `--data @-`,
  verbose output, the 7.55 floor).
- **Procedure:** `skill-corpus/deploy-gated-red-green.md` (the procedure
  this harness serves: modes, the single RED, interlocks, synthetic data);
  `protocols/test-first.md` (RED before GREEN);
  `protocols/verify-disagreement.md` (a failing check indicts the instrument
  first).
- **Sources:** distilled from practice (a live harness run
  against a deployed service, with its companion lint). Upstream: curl 7.55.0
  changes ("allow --header and --proxy-header read from file",
  https://curl.se/ch/7.55.0.html); the curl man page (`-H @filename`,
  `--data-ascii` "is an alias for --data", https://curl.se/docs/manpage.html);
  bash CHANGES, bash-4.4-rc2 item 3.a (the empty-array `nounset` error).

## 8. Changelog

- 2026-10-05 — created from a live-check script and its static
  lint, generalized: groups and principals became plant-filled functions,
  `NOT-EXERCISED` (now failing) guards values carried between requests, TLS
  verification is on unless opted out, the lint also fails `curl -v` and
  `--trace`, and a self-test against a synthetic service was added; by
  tool-smith.
- 2026-10-05 (review fix pass): the verdicts now match
  `skill-corpus/deploy-gated-red-green.md`: `NOT-EXERCISED` records an absent
  precondition without failing, a missing input or no HTTP answer is a
  failing `HARNESS-ERROR`, and the harness reports `SKIPPED-INTERLOCK` and
  `WARN spec-drift` (a documented RED status per check); the
  harness defect is described as it happened (a body built from a read) and
  `py fields` guards it; principals are a list with one login each; a
  `preflight` hook, before/after snapshot helpers and an RFC 3339 run start
  were added; the curl preflight compares the version; a crash mid-run exits
  `2`; the lint joins continuation lines, catches `-sv`, `-sd` and
  `--data-ascii`, and exits `2` on a usage error; the self-test passes on
  bash 3.2; by tool-smith.
