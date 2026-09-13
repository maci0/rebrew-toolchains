#!/bin/sh
# cc wrapper — rebrew Apple GCC 3.1, build 1041 (macOS).
#
# The Apple cc1 emits Darwin assembly that GNU as cannot read, so the wrapper
# runs decomp.me's pipeline: cc1, then convert_gas_syntax.py, then
# powerpc-linux-gnu-as.  A C++ source (.cpp/.cc/.cxx/.C) uses cc1plus when the
# image ships one.
#
#   cc -c f.c -o f.o
#
# -o names the output (default <stem>.o); every other argument goes to cc1.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"
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
[ -n "$OUT" ] || OUT="$STEM.o"
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_cc1=/opt/gcc-3.1-1041/cc1
case "$SRC" in
    *.cpp | *.cc | *.cxx | *.C)
        [ -x /opt/gcc-3.1-1041/cc1 ] && _cc1=/opt/gcc-3.1-1041/cc1
        ;;
    *) ;;
esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT

# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a flag list; the helper exits by design
( rebrew_exec "$_cc1" -quiet $CC_FLAGS "$SRC_ABS" -o "$_work/out.s" ) \
    || rebrew_die "cc1 failed on $SRC"
python3 /opt/gcc-3.1-1041/convert_gas_syntax.py "$_work/out.s" "$STEM" new > "$_work/out_new.s" \
    || rebrew_die "assembler-syntax conversion failed for $SRC"
powerpc-linux-gnu-as "$_work/out_new.s" -o "$OUT_ABS"
