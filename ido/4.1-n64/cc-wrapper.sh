#!/bin/sh
# cc wrapper — IDO 4.1 (N64) under qemu-irix-4.0, then ECOFF -> ELF.
#
# decomp.me's ido4.1 recipe: the bundled emulator runs the vendor IRIX `cc`
# with `-EL` (the little-endian N64 build), and the asset's own
# `ecoff_tool.py` converts the resulting ECOFF object into an ELF
# relocatable.  Native x86_64 host, no wine/DOSBox; the emulator needs
# GLIBC_2.38, which is why this image inherits the Ubuntu-noble base.
#
#   cc -c f.c -o f.o
#
# -o names the output (default <stem>.o); every other argument goes to the
# vendor driver.  The emulator call runs in a subshell because the shared run
# helper exits by design (which would end this script before the conversion).
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

# SC2310: the run helper exits by design, hence the subshell under `||`.
# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a flag list, word-split
( rebrew_exec /opt/ido-4.1/usr/bin/qemu-irix-4.0 -silent -L /opt/ido-4.1 \
    /opt/ido-4.1/usr/bin/cc -I /opt/ido-4.1/usr/include \
    -EL -c -Xcpluscomm $CC_FLAGS -o "$OUT_ABS" "$SRC_ABS" ) \
    || rebrew_die "qemu-irix-4.0 / IDO 4.1 failed on $SRC"

[ -s "$OUT_ABS" ] || rebrew_die "IDO 4.1 produced no object for $SRC"

python3 /opt/ido-4.1/usr/bin/ecoff_tool.py --convert-elf "$OUT_ABS" -o "$OUT_ABS"
