#!/usr/bin/env bash
# Build the rebrew toolchain docker images from this repo.
#
#   ./build.sh                 # build every image
#   ./build.sh msvc6           # build one (dir name: msvc/6.0-win32 or the tag suffix)
#   ./build.sh 6.0-win32       # ...also accepted
#
# The images are self-contained: they download their pinned, sha256-verified
# source from the URL recorded in sources.json (curl inside the Dockerfile).
# Six 16-bit toolchains (msvc10, msvc15, msvc1.52, tc20, tc31, delphi10) are
# built from reconstructed media tarballs that are NOT redistributed here
# (see README "Copyright"): place the tarball next to its Dockerfile first.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-rebrew}"

# 16-bit dirs whose Dockerfile COPYs an in-repo media tarball.
NEEDS_TARBALL="msvc/1.0-win16 msvc/1.5-win16 msvc/1.52-win16 borland/2.0-win16 borland/3.1-win16 delphi/1.0-win16"

# rebrew profile name -> toolchain dir (generated from sources.json).
PROFILE_DIRS="borlandc55=borland/5.5-win32 delphi16=delphi/1.0-win16 msvc1.52=msvc/1.52-win16 msvc10=msvc/1.0-win16 msvc1000=msvc/10.0-win32 msvc1000sp1=msvc/10.0-sp1-win32 msvc1100=msvc/11.0-win32 msvc15=msvc/1.5-win16 msvc200=msvc/2.0-win32 msvc400=msvc/4.0-win32 msvc410=msvc/4.1-win32 msvc420=msvc/4.2-win32 msvc5=msvc/5.0-win32 msvc500sp1=msvc/5.0-sp1-win32 msvc500sp2=msvc/5.0-sp2-win32 msvc500sp3=msvc/5.0-sp3-win32 msvc6=msvc/6.0-win32 msvc600sp1=msvc/6.0-sp1-win32 msvc600sp2=msvc/6.0-sp2-win32 msvc600sp3=msvc/6.0-sp3-win32 msvc600sp4=msvc/6.0-sp4-win32 msvc600sp5=msvc/6.0-sp5-win32 msvc600sp6=msvc/6.0-sp6-win32 msvc7=msvc/7.0-win32 msvc700=msvc/7.0-rtm-win32 msvc700sp1=msvc/7.0-sp1-win32 msvc710=msvc/7.1-win32 msvc710sp1=msvc/7.1-sp1-win32 msvc800=msvc/8.0-win32 msvc800sp1=msvc/8.0-sp1-win32 msvc900=msvc/9.0-win32 msvc900sp1=msvc/9.0-sp1-win32 tc16=borland/3.1-win16 tc20=borland/2.0-win16 watcom=watcom/2.0-win32"


resolve_dir() {
  local arg="$1"
  # already a family-qualified dir?
  [ -d "$ROOT/$arg" ] && { echo "${arg%/}"; return; }
  # bare dir name (6.0-win32)
  for d in "$ROOT"/*/*/; do
    if [ "$(basename "$d")" = "$arg" ]; then
      echo "${d#$ROOT/}"
      return
    fi
  done
  # bare dir with trailing slash (6.0-win32/) — normalize
  for d in "$ROOT"/*/*/; do
    [ "$(basename "$d")" = "${arg%/}" ] && { echo "${d#$ROOT/}"; return; }
  done
  # rebrew profile name (msvc6) -> dir
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
  echo "==> building $tag (from $dir)"
  if [[ " $NEEDS_TARBALL " == *" $dir "* ]]; then
    local tb
    tb="$(grep -o 'COPY [^ ]*\.tar\.xz' "$ROOT/$dir/Dockerfile" | awk '{print $2}' || true)"
    if [ -n "$tb" ] && [ ! -f "$ROOT/$dir/$tb" ]; then
      echo "ERROR: $dir needs '$tb' (reconstructed media - see README Copyright section)" >&2
      exit 2
    fi
  fi
  docker build -t "$tag" "$ROOT/$dir"
}

# base image first
echo "==> building $PREFIX/base"
docker build -t "$PREFIX/base" "$ROOT/base"

if [ $# -eq 0 ]; then
  for d in "$ROOT"/*/*/; do
    [ -f "$d/Dockerfile" ] || continue
    build_one "${d#$ROOT/}"
  done
else
  for arg in "$@"; do
    dir="$(resolve_dir "$arg")"
    [ -n "$dir" ] || { echo "unknown toolchain: $arg" >&2; exit 2; }
    build_one "$dir"
  done
fi
echo "done."
