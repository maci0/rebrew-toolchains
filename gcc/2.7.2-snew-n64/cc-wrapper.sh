#!/bin/sh
# cc wrapper — native SN64 tree plus the modern-asn64.py assembler.
#
# This build ships native Linux tools but no assembler: decomp.me assembles
# through `modern-asn64.py`, a Python script that drives GNU as for the MIPS
# side.  The wrapper runs the same three steps:
#   cpp -lang-c -undef f.c | cc1 ... -o f.s
#   python3 modern-asn64.py mips-linux-gnu-as f.s ... -o f.o
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

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT
cd "$_work" || rebrew_die "cannot enter temporary directory"

# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split
/opt/gcc-2.7.2-snew/cpp -lang-c -undef "$SRC_ABS" > src.i     || rebrew_die "preprocessing $SRC failed"

# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a flag list; the helper exits by design
( rebrew_exec /opt/gcc-2.7.2-snew/cc1 -mfp32 -mgp32 -G0 -quiet -mcpu=vr4300 -fno-exceptions $CC_FLAGS -o out.s < src.i )     || rebrew_die "cc1 failed on $SRC"

python3 /opt/gcc-2.7.2-snew/modern-asn64.py mips-linux-gnu-as out.s -G0 -EB -mips3 -O1     -mabi=32 -mgp32 -march=vr4300 -mfp32 -mno-shared -o "$OUT_ABS"
