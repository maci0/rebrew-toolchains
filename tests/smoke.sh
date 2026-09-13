#!/bin/sh
# smoke.sh — build and compile with one image per runtime class.
#
# `make lint`/`make test` are file-level checks: they can prove a Dockerfile's
# pins are present and its contract is met, but not that the image produces an
# object.  This is the smallest runnable version of the check every image in
# this repo passed by hand before it landed — the class of bug it catches is
# "the build succeeds and the wrapper runs, but the compiler emits nothing",
# which has shipped here more than once (see docs/ADDING-TOOLCHAIN.md).
#
# Usage:  tests/smoke.sh [profile ...]     (default: one image per runtime)
#
# Needs Docker and network access for the first build of each image.  The
# dosemu2 images additionally need /dev/kvm (GitHub's ubuntu runners have it)
# and are skipped with a message where it is missing, so the same script runs
# on a developer machine and in CI.
set -eu

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# The expected fragments below are deliberately loose: they must hold for any
# file(1) magic database, which words the same object differently across
# distributions ("Intel i386 COFF" here, "Intel 80386 COFF" on Ubuntu).  They
# still catch the failure this harness exists for — an empty object, or one for
# the wrong target.
command -v file >/dev/null 2>&1 || {
    echo "smoke: the file(1) command is required to identify the artifacts" >&2
    exit 1
}

work="$(mktemp -d "${TMPDIR:-/tmp}/rebrew-smoke.XXXXXX")"
trap 'rm -rf "$work"' EXIT
# The toolchain images drop to uid 1000 (`rebrew`), so the mount must be
# readable *and writable* by that uid.  `mktemp -d` is 0700, and a CI runner's
# user is uid 1001, not 1000: without this the container cannot traverse the
# mount (every compile reports "no readable source file") or write the object
# back.  0777 on a throwaway scratch dir is deliberate — a real `-v "$PWD":/work`
# works because a developer's uid is normally 1000.
chmod 777 "$work"

fail=0

# host_dir_of <profile> — the manifest's install directory, or empty.
host_dir_of() {
    python3 - "$1" <<'EOF'
import json, sys
entry = json.load(open("sources.json")).get(sys.argv[1])
print(entry["host_dir"] if entry else "")
EOF
}

# run_case <profile> <arguments> <artifact> <expected-fragment> [extra docker args...]
# `arguments` is the image's own documented invocation (they differ: cl takes
# /c, bcc32 -c, the DOSBox and dosemu2 wrappers -c -o), and `artifact` is the
# file that invocation produces (DOSBox FAT-uppercases names).
run_case() {
    profile="$1"
    args="$2"
    artifact_name="$3"
    expect="$4"
    shift 4
    host_dir="$(host_dir_of "$profile")"
    if [ -z "$host_dir" ]; then
        echo "FAIL $profile: not in sources.json" >&2
        fail=1
        return 0
    fi
    tag="rebrew/${host_dir%%/*}:${host_dir#*/}"
    echo "== $profile ($tag)"
    printf 'int f(int x){return x+1;}\n' > "$work/t.c"
    chmod 644 "$work/t.c"
    rm -f "$work/t.o" "$work/t.obj"
    if ! ./build.sh "$host_dir" >"$work/build.log" 2>&1; then
        echo "FAIL $profile: build failed" >&2
        tail -20 "$work/build.log" >&2
        fail=1
        return 0
    fi
    # shellcheck disable=SC2086  # args are a deliberately word-split list
    if ! docker run --rm "$@" -v "$work":/work -w /work "$tag" \
        $args >"$work/compile.log" 2>&1; then
        echo "FAIL $profile: compile failed" >&2
        tail -20 "$work/compile.log" >&2
        fail=1
        return 0
    fi
    # DOSBox keeps the stem's case and uppercases the extension (t.OBJ), and
    # Borland writes .obj for a .c source, so match the name case-insensitively.
    artifact="$(find "$work" -maxdepth 1 -iname "$artifact_name" | head -n 1)"
    if [ -z "$artifact" ] || [ ! -s "$artifact" ]; then
        echo "FAIL $profile: no object produced" >&2
        tail -20 "$work/compile.log" >&2
        fail=1
        return 0
    fi
    # `file` is the cheap check that the object is for the intended target —
    # a compiler that silently emits an empty object fails here.
    kind="$(file -b "$artifact")"
    if [ -n "$expect" ] && ! printf '%s' "$kind" | grep -q "$expect"; then
        echo "FAIL $profile: object is '$kind' (wanted $expect)" >&2
        fail=1
        return 0
    fi
    echo "ok  $profile: $kind"
    return 0
}

if [ "$#" -gt 0 ]; then
    for profile in "$@"; do
        run_case "$profile" '-c t.c -o t.o' t.o ''
    done
else
    # One image per runtime: native ELF, qemu-irix, wibo, wine, DOSBox, and
    # (below, when KVM is available) dosemu2.
    while IFS='|' read -r profile args artifact expect; do
        [ -n "$profile" ] || continue
        run_case "$profile" "$args" "$artifact" "$expect"
    done <<'CASES'
ido-7.1|-c t.c -o t.o|t.o|MIPS
ido-4.1|-c t.c -o t.o|t.o|MIPS
msvc-6.0-sp6|/c t.c|t.obj|COFF
icc-5.0.1-010525z|-c t.c -o t.obj|t.obj|COFF
borland-5.6|-c t.c|t.obj|relocatable
msc-6.0|t.c|t.obj|relocatable
CASES
    if [ -e /dev/kvm ]; then
        while IFS='|' read -r profile args artifact expect; do
            [ -n "$profile" ] || continue
            run_case "$profile" "$args" "$artifact" "$expect" --device /dev/kvm
        done <<'DOS_CASES'
psyq-3.3|-c t.c -o t.o|t.o|MIPS
saturn-cygnus-2.7-96Q3|-c t.c -o t.o|t.o|Renesas SH
DOS_CASES
    else
        echo "-- skipping the dosemu2 cases: no /dev/kvm on this host"
    fi
fi

[ "$fail" -eq 0 ] || { echo "smoke: FAILED" >&2; exit 1; }
echo "smoke: all cases passed"
