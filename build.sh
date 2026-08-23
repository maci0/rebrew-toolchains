#!/usr/bin/env bash
# Build the rebrew toolchain docker images from this repo.
#
#   ./build.sh                 # build every image
#   ./build.sh msvc6           # build one (dir name: msvc/6.0-win32 or the tag suffix)
#   ./build.sh 6.0-win32       # ...also accepted
#
# The images are self-contained: every image downloads its pinned,
# sha256-verified source from the URL recorded in sources.json (curl inside
# the Dockerfile) — 32-bit from archaic-msvc / archaic-toolchains, and the
# six 16-bit toolchains (msvc10, msvc15, msvc1.52, tc20, tc16, delphi16)
# from their archaic-toolchains repos.  No media tarballs are needed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-rebrew}"

# rebrew profile name -> toolchain dir, generated from sources.json (the
# single source of truth for the mapping; a parse failure must stop the
# build, not silently drop profiles).
PROFILE_DIRS="$(awk '
    /^  "[^"]+": \{$/ { key = $1; sub(/^"/, "", key); sub(/":$/, "", key) }
    /^    "host_dir": "/ { v = $0; sub(/^.*"host_dir": "/, "", v); sub(/",$/, "", v); print key "=" v }
' "$ROOT/sources.json")"
[ -n "$PROFILE_DIRS" ] || { echo "failed to parse $ROOT/sources.json" >&2; exit 2; }


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
    echo "ambiguous toolchain name '$arg' — matches multiple families; use a family-qualified path (e.g. msvc/$last or watcom/$last)" >&2
    echo ""
    return
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

build_one() {
  local dir="$1"
  local family verarch
  family="${dir%%/*}"
  verarch="${dir#*/}"
  if [ ! -f "$ROOT/$dir/Dockerfile" ]; then
    echo "no Dockerfile in $dir" >&2
    exit 2
  fi
  local tag="$PREFIX/$family:$verarch"
  # The shared base is always tagged :1.0 — every toolchain Dockerfile's
  # FROM/BASE_IMAGE and the --build-arg below point at it, so a manual
  # `./build.sh base` rebuild must land on that same tag.
  [ "$dir" = "base" ] && tag="$PREFIX/base:1.0"
  echo "==> building $tag (from $dir)"
  docker build --build-arg "BASE_IMAGE=$PREFIX/base:1.0" -t "$tag" "$ROOT/$dir"
}

# base image first — tag :1.0 to match the FROM ${BASE_IMAGE} default and the
# build-arg we pass to every toolchain Dockerfile.
echo "==> building $PREFIX/base:1.0"
docker build -t "$PREFIX/base:1.0" "$ROOT/base"

if [ $# -eq 0 ]; then
  for d in "$ROOT"/*/*/; do
    [ -f "$d/Dockerfile" ] || continue
    rel="${d#$ROOT/}"
    rel="${rel%/}"  # the glob yields a trailing slash — strip it
    build_one "$rel"
  done
else
  for arg in "$@"; do
    dir="$(resolve_dir "$arg")"
    [ -n "$dir" ] || { echo "unknown toolchain: $arg" >&2; exit 2; }
    build_one "$dir"
  done
fi
echo "done."
