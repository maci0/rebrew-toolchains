#!/bin/sh
# wrapper-common.sh — shared helpers for rebrew toolchain entrypoints.
#
# Every toolchain image's ENTRYPOINT wrapper sources this file so the
# argument handling, source validation, DOSBox sandboxing and artifact
# copy-back are one implementation instead of N copies.
#
# Usage:  . /usr/local/lib/rebrew/wrapper-common.sh

rebrew_die() {
    echo "rebrew: $*" >&2
    exit 1
}

rebrew_log() {
    echo "rebrew: $*" >&2
}

# rebrew_pick_source "$@" — locates the readable source file among the args
# (MSVC-style invocations put flags first, e.g. "/c f.c"; POSIX-style put the
# source first).  The first arg that is not a flag and resolves to a readable
# file wins.  Sets $SRC (the file) and $STEM (basename without the final
# extension).  Exits with a message on misuse.
rebrew_pick_source() {
    [ "$#" -ge 1 ] || rebrew_die "usage: <source> [flags...]"
    SRC=""
    for _a in "$@"; do
        case "$_a" in
            -*) continue ;;
            /?*) continue ;;  # MSVC flags start with '/'
        esac
        if [ -r "$_a" ]; then
            SRC="$_a"
            break
        fi
    done
    [ -n "$SRC" ] || rebrew_die "no readable source file in: $*"
    _base=$(basename "$SRC")
    STEM="${_base%.*}"
    [ -n "$STEM" ] || rebrew_die "source basename '$SRC' has no stem"
}

# rebrew_dosbox_run <sandbox> <autoexec-line> — writes a headless DOSBox
# config that mounts the sandbox as C:, runs the autoexec line, and exits.
# Sets $DOX_LOG to the sandbox's toolchain log path (callers write it).
rebrew_dosbox_run() {
    sandbox="$1"
    autoexec="$2"
    printf '[sdl]\nfullscreen=false\n\n[cpu]\ncycles=fixed 30000\n\n[autoexec]\nmount c %s\nC:\ncd \\\n%s\nexit\n' \
        "$sandbox" "$autoexec" > "$sandbox/toolchain.conf"
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy dosbox -conf "$sandbox/toolchain.conf" -noconsole >/dev/null 2>&1 || true
}

# rebrew_copy_back <sandbox> <src-name> <dest-name> — copies an artifact the
# DOSBox run produced back into the mounted /work dir (DOSBox FAT-uppercases
# names; the caller passes the uppercase source name).
rebrew_copy_back() {
    sandbox="$1"
    src_name="$2"
    dest_name="$3"
    if [ -f "$sandbox/$src_name" ]; then
        cp "$sandbox/$src_name" "/work/$dest_name"
        return 0
    fi
    return 1
}
