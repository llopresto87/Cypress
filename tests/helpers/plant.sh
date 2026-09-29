# plant.sh: one install per suite, copied per case. Source it; needs bash.
#   plant_base <hosts> [flags...]  install once into a cache keyed by hosts and
#                                  flags; sets PLANT_BASE to that directory
#   plant_copy <dst>               cp -a the last plant_base into <dst>
# The cache lives under $PLANT_CACHE, else $TMP/plant-cache; the suite's own
# EXIT trap removes it. A case that asserts first-install behavior installs
# fresh instead of copying.
PLANT_SEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLANT_BASE=""

plant_base() {
  local hosts="$1"; shift
  local cache="${PLANT_CACHE:-${TMP:?plant.sh: set TMP or PLANT_CACHE}/plant-cache}"
  local key; key="$(printf '%s' "$hosts $*" | tr -c 'A-Za-z0-9._-' '_')"
  PLANT_BASE="$cache/$key"
  [ -f "$PLANT_BASE.ok" ] && return 0
  rm -rf "$PLANT_BASE"; mkdir -p "$PLANT_BASE"
  bash "$PLANT_SEED_ROOT/install.sh" "$hosts" --project-dir "$PLANT_BASE" "$@" \
    >"$PLANT_BASE.log" 2>&1 \
    || { echo "plant_base: install.sh $hosts $* failed: $(tail -3 "$PLANT_BASE.log" | tr '\n' ' ')" >&2; return 1; }
  touch "$PLANT_BASE.ok"
}

plant_copy() {
  [ -n "$PLANT_BASE" ] || { echo "plant_copy: call plant_base first" >&2; return 1; }
  mkdir -p "$1" && cp -a "$PLANT_BASE/." "$1/"
}
