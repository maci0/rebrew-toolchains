#!/bin/sh
# icl wrapper — Intel C++ Compiler 5.0.1 (win32, Windows PE).
#
# Invoke:  icl -c f.c -o f.obj
#
# The compiler is a Windows binary, so it runs through the shared wine/wibo
# dispatcher (wibo by default is fine here; REBREW_RUNNER=wine also works).
# File arguments are handed over as Windows `Z:` paths because icl, like every
# `cl`-style driver, reads a leading `/` as an option.
#
# decomp.me layers Microsoft C 6.0 into the same directory for the *linker*
# (icl passes `/link` through to it); compiling with `/c` needs only Intel's
# own tree, so this image pins just the Intel asset.  That tree is available
# separately as `rebrew/msvc:6.0-win9x-win32` when linking is wanted.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o | -Fo)
            [ "$#" -ge 2 ] || rebrew_die "$1 requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;
        "$SRC") shift ;;
        *)
            CC_FLAGS="$CC_FLAGS $1"
            shift
            ;;
    esac
done
[ -n "$OUT" ] || OUT="$STEM.obj"
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_z() { printf 'Z:%s' "$1" | sed 's|/|\\|g'; }

export INCLUDE="Z:\\opt\\icc-5.0.1\\Include"

# Assign the converted paths first: SC2312 — a substitution inline in the
# argument list would mask the helper's exit status.
_out_z=$(_z "$OUT_ABS")
_src_z=$(_z "$SRC_ABS")
# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split
rebrew_run /opt/icc-5.0.1/Bin/icl.exe /c /nologo $CC_FLAGS \
    "/Fo$_out_z" "$_src_z"
