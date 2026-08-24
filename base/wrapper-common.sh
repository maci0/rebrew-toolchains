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
            *) ;;  # valid timeout passes through unchanged
        esac
        printf '%s' "$2"
    else
        printf '%s' "$1"
    fi
}

# rebrew_pick_source "$@" — locates the readable source file among the args
# (MSVC-style invocations put flags first, e.g. "/c f.c"; POSIX-style put the
# source first).  The first arg that is not a flag and resolves to a readable
# regular file wins — including absolute paths like /work/f.c, which would
# otherwise be misclassified as MSVC flags by their leading '/'; a real MSVC
# flag (/c, /O2, ...) is never an existing file at the filesystem root.
# Sets $SRC (the file) and $STEM (basename without the final extension).
# Exits with a message on misuse.
rebrew_pick_source() {
    [ "$#" -ge 1 ] || rebrew_die "usage: <source> [flags...]"
    SRC=""
    for _a in "$@"; do
        case "$_a" in
            -*) continue ;;  # POSIX-style flags start with '-'
            *) ;;  # everything else: the regular-file test below decides
        esac
        if [ -f "$_a" ] && [ -r "$_a" ]; then
            SRC="$_a"
            break
        fi
    done
    [ -n "$SRC" ] || rebrew_die "no readable source file in: $*"
    _base=$(basename "$SRC")
    STEM="${_base%.*}"
    [ -n "$STEM" ] || rebrew_die "source basename '$SRC' has no stem"
}

# rebrew_now_secs — integer seconds from a step-free clock for elapsed-time
# measurement: /proc/uptime reads the kernel's boottime clock, which NTP
# steps and manual clock changes never jump (unlike date +%s), so watchdog
# start/now pairs taken across a run measure real elapsed time even when
# the wall clock is corrected mid-run.  Falls back to date +%s where
# /proc/uptime does not exist (non-Linux hosts running the test harness).
# Every <start> fed to rebrew_watchdog_status must come from this helper:
# values from different sources are not comparable.
rebrew_now_secs() {
    _up=""
    if [ -r /proc/uptime ]; then
        read -r _up _rest < /proc/uptime 2>/dev/null || _up=""
    fi
    case "${_up:-}" in
        '' | *[!0-9.]*) date +%s ;;
        *) printf '%s' "${_up%%.*}" ;;
    esac
}

# rebrew_watchdog_status <start-secs> <timeout> <status> — echoes the status
# with watchdog escalations normalized to 124.  GNU timeout reports its own
# TERM kill as 124, but when the run survives --kill-after and is SIGKILLed
# it reports the raw 128+9 (= 137), which would otherwise pass through as if
# the tool itself died and defeat the fail-loud contract.  An external kill
# of the tool mid-run also exits 137, but well before the cap, so the
# elapsed-time guard keeps that passing through unchanged.  <start-secs>
# must be a rebrew_now_secs reading taken immediately before the run.
rebrew_watchdog_status() {
    [ "$3" -eq 137 ] || { printf '%s' "$3"; return; }
    _now=$(rebrew_now_secs)
    if [ $((_now - $1)) -ge "$2" ]; then
        printf '124'
    else
        printf '%s' "$3"
    fi
}

# rebrew_exec <exe> [args...] — runs a command under the watchdog cap shared
# by every entrypoint (REBREW_RUNNER_TIMEOUT, seconds, default 600): the
# command's own exit status passes through unchanged, and only a watchdog
# kill (hung compiler) dies with its own explicit error naming the knob.
# This is the single implementation of the fail-loud contract; rebrew_run
# and the native-binary wrappers both go through it.
rebrew_exec() {
    # Deliberate `|| exit 1`: rebrew_timeout_secs prints its own error and
    # returns nonzero; the explicit handling is the documented contract.
    # shellcheck disable=SC2310
    _exec_timeout=$(rebrew_timeout_secs 600 \
        "${REBREW_RUNNER_TIMEOUT:-}" REBREW_RUNNER_TIMEOUT) || exit 1
    set +e
    _start=$(rebrew_now_secs)
    timeout --kill-after=10 "$_exec_timeout" "$@"
    _status=$(rebrew_watchdog_status "$_start" "$_exec_timeout" "$?")
    set -e
    if [ "$_status" -eq 124 ]; then
        rebrew_die "$1 exceeded ${_exec_timeout}s" \
            "(REBREW_RUNNER_TIMEOUT) and was killed"
    fi
    exit "$_status"
}

# rebrew_run <exe> [args...] — runs a Windows PE binary through the runtime
# selected by $REBREW_RUNNER: "wine" (default; full Wine, most compatible) or
# "wibo" (the minimal decompals PE loader — much faster for plain console
# tools like cl.exe/bcc32.exe, but only implements a subset of Win32).
# The selected loader executes under the shared watchdog (rebrew_exec).
rebrew_run() {
    case "${REBREW_RUNNER:-wine}" in
        wine) _runner=wine ;;
        wibo) _runner=wibo ;;
        *) rebrew_die "unknown REBREW_RUNNER '${REBREW_RUNNER}' (wine|wibo)" ;;
    esac
    rebrew_exec "$_runner" "$@"
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
    # Deliberate `|| exit 1`: rebrew_timeout_secs prints its own error and
    # returns nonzero; the explicit handling is the documented contract.
    # shellcheck disable=SC2310
    _dosbox_timeout=$(rebrew_timeout_secs 600 \
        "${REBREW_DOSBOX_TIMEOUT:-}" REBREW_DOSBOX_TIMEOUT) || exit 1
    _start=$(rebrew_now_secs)
    {
        printf '[sdl]\nfullscreen=false\n\n[cpu]\ncycles=fixed 30000\n\n[autoexec]\n'
        printf 'mount c %s\nC:\ncd \\\n%s\nexit\n' \
            "$sandbox" "$autoexec"
    } > "$sandbox/toolchain.conf"
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        timeout --kill-after=10 "$_dosbox_timeout" \
        dosbox -conf "$sandbox/toolchain.conf" -noconsole \
            >"$sandbox/dosbox.log" 2>&1 || DOSBOX_STATUS=$?
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
# names; the caller passes the uppercase source name).  The copy is staged
# through /work/.<dest>.partial and renamed into place, so a copy that fails
# midway can never leave a truncated artifact looking like fresh compiler
# output; the pre-existing destination (if any) survives untouched.  Returns
# nonzero when the artifact is missing (the usual "compile produced nothing"
# case — callers test this with `if`); when the staging or rename fails
# (e.g. read-only /work) it dies saying so, since conflating that with a
# compile failure would misdiagnose the run.
rebrew_copy_back() {
    sandbox="$1"
    src_name="$2"
    dest_name="$3"
    [ -f "$sandbox/$src_name" ] || return 1
    _tmp="/work/.${dest_name}.partial"
    cp "$sandbox/$src_name" "$_tmp" || {
        rm -f "$_tmp"
        rebrew_die "compiler produced $src_name but copying it to /work/$dest_name failed" \
            "(is /work mounted writable?)"
    }
    mv "$_tmp" "/work/$dest_name" || {
        rm -f "$_tmp"
        rebrew_die "compiler produced $src_name but putting it in place at /work/$dest_name failed"
    }
    return 0
}

# rebrew_flags_except_source "$@" — sets $FLAGS to every argument except the
# picked source, space-joined for unquoted expansion inside the DOS command
# line (flags-first and source-first invocations both work).
#
# Arguments containing control characters are rejected before they reach
# $FLAGS: the value is embedded verbatim in the generated DOSBox config,
# where a raw newline (or carriage return) would terminate the compile
# command line and execute the remainder as its own autoexec command.
rebrew_flags_except_source() {
    FLAGS=""
    for _a in "$@"; do
        [ "$_a" = "$SRC" ] && continue
        case "$_a" in
            *[[:cntrl:]]*)
                _clean="$(printf '%s' "$_a" | tr -d '[:cntrl:]')"
                rebrew_die "argument with control characters rejected: ${_clean}"
                ;;
            *) ;;  # ordinary flag or non-source argument: kept in $FLAGS
        esac
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
    # Deliberate `if` on the helper: a missing artifact is the ordinary
    # "compile produced nothing" case, not an unhandled failure.
    # shellcheck disable=SC2310
    if rebrew_copy_back "$sandbox" SRC.OBJ "$STEM.OBJ"; then
        return 0
    fi
    _note=$(rebrew_dosbox_failure_note)
    if [ -f "$sandbox/$sandbox_log" ]; then
        _log="$(cat "$sandbox/$sandbox_log" 2>/dev/null)"
        rebrew_die "compiler produced no object${_note} (see /work/$log_name); compiler log:
$_log"
    fi
    rebrew_die "compiler produced no object${_note} (no compiler log written)"
}
