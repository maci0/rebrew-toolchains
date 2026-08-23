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

# rebrew_timeout_secs <default> <value> <name> — echoes the effective
# watchdog timeout in seconds for an external run (emulator or PE loader).
# A hung compiler must fail loudly instead of blocking the caller forever;
# <value> (usually ${NAME:-}) must be empty or a positive integer.
# Returns nonzero (after printing the reason) on bad input rather than
# exiting: the helpers run in command substitution, where `exit` would only
# leave the subshell and leak an empty value into the caller.  Callers must
# handle the status (e.g. `t=$(rebrew_timeout_secs ...) || exit 1`).
rebrew_timeout_secs() {
    if [ -n "$2" ]; then
        case "$2" in
            '' | *[!0-9]* | 0)
                echo "rebrew: $3 must be a positive integer of seconds (got '$2')" >&2
                return 1
                ;;
        esac
        printf '%s' "$2"
    else
        printf '%s' "$1"
    fi
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

# rebrew_watchdog_status <start-secs> <timeout> <status> — echoes the status
# with watchdog escalations normalized to 124.  GNU timeout reports its own
# TERM kill as 124, but when the run survives --kill-after and is SIGKILLed
# it reports the raw 128+9 (= 137), which would otherwise pass through as if
# the tool itself died and defeat the fail-loud contract.  An external kill
# of the tool mid-run also exits 137, but well before the cap, so the
# elapsed-time guard keeps that passing through unchanged.
rebrew_watchdog_status() {
    [ "$3" -eq 137 ] || { printf '%s' "$3"; return; }
    if [ $(($(date +%s) - $1)) -ge "$2" ]; then
        printf '124'
    else
        printf '%s' "$3"
    fi
}

# rebrew_run <exe> [args...] — runs a Windows PE binary through the runtime
# selected by $REBREW_RUNNER: "wine" (default; full Wine, most compatible) or
# "wibo" (the minimal decompals PE loader — much faster for plain console
# tools like cl.exe/bcc32.exe, but only implements a subset of Win32).
#
# The run is capped by REBREW_RUNNER_TIMEOUT (seconds, default 600): the
# tool's own exit status passes through unchanged, and only a watchdog kill
# (hung compiler) dies with its own explicit error.
rebrew_run() {
    _runner_timeout=$(rebrew_timeout_secs 600 "${REBREW_RUNNER_TIMEOUT:-}" REBREW_RUNNER_TIMEOUT) || exit 1
    case "${REBREW_RUNNER:-wine}" in
        wine) _runner=wine ;;
        wibo) _runner=wibo ;;
        *) rebrew_die "unknown REBREW_RUNNER '${REBREW_RUNNER}' (wine|wibo)" ;;
    esac
    set +e
    _start=$(date +%s)
    timeout --kill-after=10 "$_runner_timeout" "$_runner" "$@"
    _status=$(rebrew_watchdog_status "$_start" "$_runner_timeout" "$?")
    set -e
    if [ "$_status" -eq 124 ]; then
        rebrew_die "$_runner run exceeded ${_runner_timeout}s (REBREW_RUNNER_TIMEOUT) and was killed"
    fi
    exit "$_status"
}

# rebrew_dosbox_run <sandbox> <autoexec-line> — writes a headless DOSBox
# config that mounts the sandbox as C:, runs the autoexec line, and exits.
# The run's output is kept in <sandbox>/dosbox.log and its exit status in
# $DOSBOX_STATUS so callers can tell an emulator crash/timeout from a
# compile that ran and failed.  REBREW_DOSBOX_TIMEOUT (seconds, default 600)
# caps the run.
DOSBOX_STATUS=0
rebrew_dosbox_run() {
    sandbox="$1"
    autoexec="$2"
    _dosbox_timeout=$(rebrew_timeout_secs 600 "${REBREW_DOSBOX_TIMEOUT:-}" REBREW_DOSBOX_TIMEOUT) || exit 1
    _start=$(date +%s)
    printf '[sdl]\nfullscreen=false\n\n[cpu]\ncycles=fixed 30000\n\n[autoexec]\nmount c %s\nC:\ncd \\\n%s\nexit\n' \
        "$sandbox" "$autoexec" > "$sandbox/toolchain.conf"
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        timeout --kill-after=10 "$_dosbox_timeout" \
        dosbox -conf "$sandbox/toolchain.conf" -noconsole >"$sandbox/dosbox.log" 2>&1 || DOSBOX_STATUS=$?
    DOSBOX_STATUS=$(rebrew_watchdog_status "$_start" "$_dosbox_timeout" "$DOSBOX_STATUS")
}

# rebrew_dosbox_failure_note — diagnostic suffix describing how the DOSBox
# run itself ended, appended to compile-failure messages so a crashed or
# timed-out emulator is not misreported as a plain compile failure.
rebrew_dosbox_failure_note() {
    if [ "${DOSBOX_STATUS:-0}" -eq 0 ]; then
        return 0
    fi
    if [ "$DOSBOX_STATUS" -eq 124 ]; then
        printf '; DOSBox was killed after exceeding REBREW_DOSBOX_TIMEOUT'
    else
        printf '; DOSBox exited abnormally (status %s)' "$DOSBOX_STATUS"
    fi
}

# rebrew_copy_back <sandbox> <src-name> <dest-name> — copies an artifact the
# DOSBox run produced back into the mounted /work dir (DOSBox FAT-uppercases
# names; the caller passes the uppercase source name).  Returns nonzero when
# the artifact is missing (the usual "compile produced nothing" case —
# callers test this with `if`); when the artifact exists but the copy fails
# (e.g. read-only /work) it dies saying so, since conflating that with a
# compile failure would misdiagnose the run.
rebrew_copy_back() {
    sandbox="$1"
    src_name="$2"
    dest_name="$3"
    [ -f "$sandbox/$src_name" ] || return 1
    cp "$sandbox/$src_name" "/work/$dest_name" || \
        rebrew_die "compiler produced $src_name but copying it to /work/$dest_name failed (is /work mounted writable?)"
    return 0
}

# rebrew_flags_except_source "$@" — sets $FLAGS to every argument except the
# picked source, space-joined for unquoted expansion inside the DOS command
# line (flags-first and source-first invocations both work).
rebrew_flags_except_source() {
    FLAGS=""
    for _a in "$@"; do
        [ "$_a" = "$SRC" ] && continue
        FLAGS="$FLAGS $_a"
    done
}

# rebrew_dosbox_compile <tree> <tmp-prefix> <autoexec> <log-name> — the
# shared DOSBox compile flow for the 16-bit C toolchains: stage the vendored
# toolchain <tree> plus the picked source (as the 8.3-safe SRC.C) into a
# fresh sandbox C: drive, run the <autoexec> line, copy the compiler log to
# /work/<log-name>, and copy SRC.OBJ back to /work as $STEM.OBJ.  Exits
# nonzero, embedding the compiler log, when no object was produced.
rebrew_dosbox_compile() {
    [ -n "${SRC:-}" ] || rebrew_die "rebrew_dosbox_compile: run rebrew_pick_source first"
    tree="$1"
    prefix="$2"
    autoexec="$3"
    log_name="$4"
    sandbox=$(mktemp -d "/tmp/${prefix}.XXXXXX") || rebrew_die "mktemp failed"
    trap 'rm -rf "$sandbox"' EXIT

    cp -r "$tree/." "$sandbox"/ || rebrew_die "cannot stage toolchain tree $tree"
    cp "$SRC" "$sandbox/SRC.C" || rebrew_die "cannot stage source $SRC"

    rebrew_dosbox_run "$sandbox" "$autoexec"

    sandbox_log="$(printf '%s' "$log_name" | tr '[:lower:]' '[:upper:]')"
    # The log lands in /work for tooling; it is also embedded in the failure
    # message in case that copy failed (e.g. read-only mount).
    if [ -f "$sandbox/$sandbox_log" ]; then
        cp "$sandbox/$sandbox_log" "/work/$log_name" 2>/dev/null || true
    fi
    if rebrew_copy_back "$sandbox" SRC.OBJ "$STEM.OBJ"; then
        return 0
    fi
    if [ -f "$sandbox/$sandbox_log" ]; then
        rebrew_die "compiler produced no object$(rebrew_dosbox_failure_note) (see /work/$log_name); compiler log:
$(cat "$sandbox/$sandbox_log" 2>/dev/null)"
    fi
    rebrew_die "compiler produced no object$(rebrew_dosbox_failure_note) (no compiler log written)"
}
