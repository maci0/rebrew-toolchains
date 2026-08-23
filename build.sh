#!/usr/bin/env bash
# Build the rebrew toolchain docker images from this repo.
#
#   ./build.sh                 # build every image (toolchains in parallel)
#   ./build.sh msvc6           # build one (dir name: msvc/6.0-win32 or the tag suffix)
#   ./build.sh 6.0-win32       # ...also accepted
#
# The base image is built first; the toolchain images depend only on it and
# are independent of each other, so after it they run REBREW_BUILD_JOBS at a
# time (default 4).  Every build downloads its pinned source tarball, so a
# full sweep is network-bound and parallelism cuts wall-clock roughly by the
# job count.  Set REBREW_BUILD_JOBS=1 for strictly sequential builds.
#
# The images are self-contained: every image downloads its pinned,
# sha256-verified source from the URL recorded in sources.json (curl inside
# the Dockerfile) — 32-bit from archaic-msvc / archaic-toolchains, and the
# six 16-bit toolchains (msvc10, msvc15, msvc1.52, tc20, tc16, delphi16)
# from their archaic-toolchains repos.  No media tarballs are needed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-rebrew}"
JOBS="${REBREW_BUILD_JOBS:-4}"
case "$JOBS" in
  '' | *[!0-9]* | 0) echo "REBREW_BUILD_JOBS must be a positive integer (got '$JOBS')" >&2; exit 2 ;;
esac

# rebrew profile name -> toolchain dir + pinned url/sha256, parsed from
# sources.json (the single source of truth; a parse failure must stop the
# build, not silently drop profiles).
PINS="$(awk -F'"' '
    /^  "[^"]+": \{$/    { key = $2 }
    /^    "host_dir": "/ { dir[key] = $4 }
    /^    "url": "/      { url[key] = $4 }
    /^    "sha256": "/   { sha[key] = $4 }
    END { for (k in dir) print k "\t" dir[k] "\t" url[k] "\t" sha[k] }
' "$ROOT/sources.json")"
[ -n "$PINS" ] || { echo "failed to parse $ROOT/sources.json" >&2; exit 2; }

# Each pinned url/sha256 also appears verbatim in the host_dir's Dockerfile
# (its curl + sha256sum RUN is what actually builds the image), so the two
# are kept in sync by hand.  Verify they agree before building anything: a
# one-sided edit must fail the run, not fetch something sources.json does
# not pin.
while IFS=$'\t' read -r profile dir url sha; do
  if [ ! -f "$ROOT/$dir/Dockerfile" ]; then
    echo "sources.json: host_dir '$dir' ($profile) has no Dockerfile" >&2
    exit 2
  fi
  grep -Fq -- "$url" "$ROOT/$dir/Dockerfile" || {
    echo "sources.json: pinned url of '$profile' is missing from $dir/Dockerfile — manifest and image disagree" >&2
    exit 2
  }
  grep -Fq -- "$sha" "$ROOT/$dir/Dockerfile" || {
    echo "sources.json: pinned sha256 of '$profile' is missing from $dir/Dockerfile — manifest and image disagree" >&2
    exit 2
  }
done <<<"$PINS"

# rebrew profile name -> toolchain dir (resolve_dir's profile lookup).
PROFILE_DIRS="$(printf '%s\n' "$PINS" | awk -F'\t' '{ print $1 "=" $2 }')"


resolve_dir() {
  local arg="$1"
  # Family-qualified path to a toolchain dir (e.g. msvc/6.0-win32).
  # Only a dir that actually holds a Dockerfile counts — a bare family dir
  # like `watcom/` has no Dockerfile and must fall through to the profile
  # lookup below (the `watcom` profile would otherwise short-circuit here).
  [ -f "$ROOT/$arg/Dockerfile" ] && { echo "${arg%/}"; return; }
  # Bare dir name (6.0-win32) — normalize an optional trailing slash.
  # `1.0-win16` and `2.0-win32` exist under more than one family (msvc+delphi,
  # msvc+watcom), so an ambiguous bare name is rejected with guidance rather
  # than silently building an arbitrary family's image.
  local last="${arg%/}" match="" count=0 d
  for d in "$ROOT"/*/*/; do
    [ "$(basename "$d")" = "$last" ] && [ -f "$d/Dockerfile" ] || continue
    match="${d#$ROOT/}"
    match="${match%/}"  # glob yields a trailing slash — strip it
    count=$((count + 1))
  done
  if [ "$count" -gt 1 ]; then
    # Die here rather than returning empty: the caller's "unknown toolchain"
    # fallback would misreport an ambiguous name as a nonexistent one.  The
    # status propagates out of resolve_dir's command substitution and, under
    # set -e, stops the script.
    echo "ambiguous toolchain name '$arg' — matches multiple families; use a family-qualified path (e.g. msvc/$last or watcom/$last)" >&2
    exit 2
  fi
  [ "$count" -eq 1 ] && { echo "$match"; return; }
  # rebrew profile name (msvc6, borlandc55, watcom, ...) -> dir
  for kv in $PROFILE_DIRS; do
    if [ "${kv%%=*}" = "$arg" ]; then
      echo "${kv#*=}"
      return
    fi
  done
  echo ""
}

tag_for() {
  local dir="$1" family verarch
  family="${dir%%/*}"
  verarch="${dir#*/}"
  local tag="$PREFIX/$family:$verarch"
  # The shared base is always tagged :1.0 — every toolchain Dockerfile's
  # FROM/BASE_IMAGE and the --build-arg below point at it, so a manual
  # `./build.sh base` rebuild must land on that same tag.
  [ "$dir" = "base" ] && tag="$PREFIX/base:1.0"
  printf '%s' "$tag"
}

# Per-build docker output is buffered in a log file under LOG_DIR so
# concurrent builds do not interleave on the terminal; the start and result
# lines stream as usual, a failure dumps its full log.
LOG_DIR=""
cleanup_logs() { [ -z "$LOG_DIR" ] || rm -rf "$LOG_DIR"; }
trap cleanup_logs EXIT

# build_pool <dir>... — run the toolchain builds, JOBS at a time.  Any
# failed build is reported with its log and fails the whole run.
build_pool() {
  LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/rebrew-build.XXXXXX")"
  local fail=0 running=0 dir log tag
  for dir in "$@"; do
    log="$LOG_DIR/${dir//\//-}.log"
    (
      tag="$(tag_for "$dir")"
      echo "==> building $tag (from $dir)"
      if docker build --build-arg "BASE_IMAGE=$PREFIX/base:1.0" -t "$tag" "$ROOT/$dir" >>"$log" 2>&1; then
        echo "==> built $tag"
      else
        echo "==> FAILED $tag — build log:"
        cat "$log"
        exit 1
      fi
    ) &
    running=$((running + 1))
    if [ "$running" -ge "$JOBS" ]; then
      wait -n || fail=1
      running=$((running - 1))
    fi
  done
  while [ "$running" -gt 0 ]; do
    wait -n || fail=1
    running=$((running - 1))
  done
  rm -rf "$LOG_DIR"; LOG_DIR=""
  [ "$fail" -eq 0 ] || { echo "one or more image builds failed" >&2; exit 1; }
}

# base image first — tag :1.0 to match the FROM ${BASE_IMAGE} default and the
# build-arg we pass to every toolchain Dockerfile.  It must exist before the
# pool starts: every toolchain image's FROM resolves against it.
echo "==> building $PREFIX/base:1.0"
docker build -t "$PREFIX/base:1.0" "$ROOT/base"

dirs=()
if [ $# -eq 0 ]; then
  for d in "$ROOT"/*/*/; do
    [ -f "$d/Dockerfile" ] || continue
    rel="${d#$ROOT/}"
    rel="${rel%/}"  # the glob yields a trailing slash — strip it
    dirs+=("$rel")
  done
else
  declare -A want=()
  for arg in "$@"; do
    dir="$(resolve_dir "$arg")"
    [ -n "$dir" ] || { echo "unknown toolchain: $arg" >&2; exit 2; }
    [ -n "${want[$dir]:-}" ] && continue  # duplicate args build once
    want[$dir]=1
    dirs+=("$dir")
  done
fi

# Validate every target before launching the pool so a typo fails fast
# instead of after sibling builds have burned bandwidth.
for dir in "${dirs[@]}"; do
  [ -f "$ROOT/$dir/Dockerfile" ] || { echo "no Dockerfile in $dir" >&2; exit 2; }
done

build_pool "${dirs[@]}"
echo "done."
