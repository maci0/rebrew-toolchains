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
  '' | *[!0-9]* | 0)
    echo "REBREW_BUILD_JOBS must be a positive integer (got '$JOBS')" >&2
    exit 2
    ;;
  *) ;;  # valid: falls through to the build
esac
# Wall-clock cap per image build (seconds).  Every build downloads its pinned
# tarball over the network; a stalled transfer would otherwise hold a pool
# slot forever.  The default is far above any healthy build so only genuine
# hangs are killed; raise it for very slow links.
BUILD_TIMEOUT="${REBREW_BUILD_TIMEOUT:-3600}"
case "$BUILD_TIMEOUT" in
  '' | *[!0-9]* | 0)
    echo "REBREW_BUILD_TIMEOUT must be a positive integer of seconds (got '$BUILD_TIMEOUT')" >&2
    exit 2
    ;;
  *) ;;  # valid: falls through to the build
esac

# rebrew profile name -> toolchain dir + pinned url/sha256, parsed from
# sources.json (the single source of truth; a parse failure must stop the
# build, not silently drop profiles).  Every profile header is emitted even
# when its fields are missing, so the loop below can reject incomplete pins
# instead of validating them vacuously.
PINS="$(awk -F'"' '
    /^  "[^"]+": \{$/    { key = $2; seen[key] = 1 }
    /^    "host_dir": "/ { dir[key] = $4 }
    /^    "url": "/      { url[key] = $4 }
    /^    "sha256": "/   { sha[key] = $4 }
    END {
      for (k in seen)
        print k "\t" dir[k] "\t" url[k] "\t" sha[k]
    }
' "$ROOT/sources.json")"
[ -n "$PINS" ] || { echo "failed to parse $ROOT/sources.json" >&2; exit 2; }

# Each pinned url/sha256 also appears verbatim in the host_dir's Dockerfile
# (its curl + sha256sum RUN is what actually builds the image), so the two
# are kept in sync by hand.  Verify they agree before building anything: a
# one-sided edit must fail the run, not fetch something sources.json does
# not pin.
while IFS=$'\t' read -r profile dir url sha; do
  if [ -z "$profile" ] || [ -z "$dir" ] || [ -z "$url" ] || [ -z "$sha" ]; then
    echo "sources.json: incomplete pin for profile '$profile':" \
      "host_dir, url and sha256 must all be present and non-empty" >&2
    exit 2
  fi
  if [ ! -f "$ROOT/$dir/Dockerfile" ]; then
    echo "sources.json: host_dir '$dir' ($profile) has no Dockerfile" >&2
    exit 2
  fi
  grep -Fq -- "$url" "$ROOT/$dir/Dockerfile" || {
    echo "sources.json: pinned url of '$profile' is missing from" \
      "$dir/Dockerfile — manifest and image disagree" >&2
    exit 2
  }
  grep -Fq -- "$sha" "$ROOT/$dir/Dockerfile" || {
    echo "sources.json: pinned sha256 of '$profile' is missing from" \
      "$dir/Dockerfile — manifest and image disagree" >&2
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
  local matches=()
  for d in "$ROOT"/*/*/; do
    [ "$(basename "$d")" = "$last" ] && [ -f "$d/Dockerfile" ] || continue
    match="${d#"$ROOT"/}"
    match="${match%/}"  # glob yields a trailing slash — strip it
    count=$((count + 1))
    matches+=("$match")
  done
  if [ "$count" -gt 1 ]; then
    # Die here rather than returning empty: the caller's "unknown toolchain"
    # fallback would misreport an ambiguous name as a nonexistent one.  The
    # status propagates out of resolve_dir's command substitution and, under
    # set -e, stops the script.
    echo "ambiguous toolchain name '$arg' — matches multiple families;" \
      "use a family-qualified path: ${matches[*]}" >&2
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
#
# In-flight builds are tracked in PIDS (everything running) and JOB_PIDS
# (pooled builds awaiting their report) so an interrupted sweep cannot leak
# them: bash runs EXIT traps only on normal exits, so SIGINT/SIGTERM are
# converted into exits whose trap TERM-then-KILLs every pending job — each
# job's direct background child is the watchdog `timeout`, which relays the
# signal to the docker build it supervises — and removes LOG_DIR.  Without
# this, every cancelled run would leave N docker processes running detached
# plus a /tmp/rebrew-build.* log dir behind.
LOG_DIR=""
PIDS=()
JOB_PIDS=()
JOB_TAGS=()
JOB_LOGS=()
# Set by reap_build when any pooled build fails; checked after the drain.
fail=0
cleanup() {
  local pid
  if [ "${#PIDS[@]}" -gt 0 ]; then
    for pid in "${PIDS[@]}"; do
      kill -TERM "$pid" 2>/dev/null || true
    done
    # Give the watchdogs a moment to relay the signal down their trees,
    # then force-kill anything still alive so nothing outlives us.
    sleep 2
    for pid in "${PIDS[@]}"; do
      kill -KILL "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
  fi
  [ -z "$LOG_DIR" ] || rm -rf "$LOG_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# reap_build — wait for the oldest in-flight build, report its outcome, and
# drop it from the tracking arrays.  FIFO order (not any-finished-first) is
# what lets plain pid arrays track exactly the jobs still running; build
# wall-clocks are similar enough that the slot idle time is negligible.
reap_build() {
  local status
  if wait "${JOB_PIDS[0]}"; then
    echo "==> built ${JOB_TAGS[0]}"
  else
    status=$?
    echo "==> FAILED ${JOB_TAGS[0]} — build log:"
    cat "${JOB_LOGS[0]}"
    if [ "$status" -eq 124 ]; then
      echo "==> build exceeded ${BUILD_TIMEOUT}s (REBREW_BUILD_TIMEOUT)" \
        "and was killed: ${JOB_TAGS[0]}" >&2
    fi
    fail=1
  fi
  JOB_PIDS=("${JOB_PIDS[@]:1}")
  JOB_TAGS=("${JOB_TAGS[@]:1}")
  JOB_LOGS=("${JOB_LOGS[@]:1}")
  PIDS=("${PIDS[@]:1}")
}

# build_pool <dir>... — run the toolchain builds, JOBS at a time.  Any
# failed build is reported with its log and fails the whole run.
build_pool() {
  LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/rebrew-build.XXXXXX")"
  local dir log tag
  for dir in "$@"; do
    log="$LOG_DIR/${dir//\//-}.log"
    tag="$(tag_for "$dir")"
    echo "==> building $tag (from $dir)"
    # The direct background child must be `timeout` itself (no wrapping
    # subshell): $! then names the process cleanup() has to signal.
    timeout --kill-after=30 "$BUILD_TIMEOUT" docker build \
      --build-arg "BASE_IMAGE=$PREFIX/base:1.0" -t "$tag" \
      "$ROOT/$dir" >>"$log" 2>&1 &
    PIDS+=("$!")
    JOB_PIDS+=("$!")
    JOB_TAGS+=("$tag")
    JOB_LOGS+=("$log")
    if [ "${#JOB_PIDS[@]}" -ge "$JOBS" ]; then
      reap_build
    fi
  done
  while [ "${#JOB_PIDS[@]}" -gt 0 ]; do
    reap_build
  done
  rm -rf "$LOG_DIR"; LOG_DIR=""
  [ "$fail" -eq 0 ] || { echo "one or more image builds failed" >&2; exit 1; }
}

# base image first — tag :1.0 to match the FROM ${BASE_IMAGE} default and the
# build-arg we pass to every toolchain Dockerfile.  It must exist before the
# pool starts: every toolchain image's FROM resolves against it.
# Backgrounded only so its pid is tracked and cleanup() can kill it if the
# run is interrupted mid-build; the wait makes it effectively synchronous
# and its output still streams to the terminal.
echo "==> building $PREFIX/base:1.0"
set +e
timeout --kill-after=30 "$BUILD_TIMEOUT" docker build \
  -t "$PREFIX/base:1.0" "$ROOT/base" &
PIDS+=("$!")
wait "${PIDS[0]}"
_status=$?
PIDS=("${PIDS[@]:1}")
set -e
if [ "$_status" -ne 0 ]; then
  if [ "$_status" -eq 124 ]; then
    echo "==> base image build exceeded ${BUILD_TIMEOUT}s (REBREW_BUILD_TIMEOUT)" \
      "and was killed" >&2
  fi
  echo "==> FAILED $PREFIX/base:1.0 (see docker output above)" >&2
  exit 1
fi

dirs=()
if [ $# -eq 0 ]; then
  for d in "$ROOT"/*/*/; do
    [ -f "$d/Dockerfile" ] || continue
    rel="${d#"$ROOT"/}"
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
