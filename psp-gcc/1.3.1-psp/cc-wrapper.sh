#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — psp-gcc/1.3.1-psp
# cc wrapper — PSP GCC (mipsallegrex).
#
# The vendor driver is a 32-bit i386 binary and finds its cc1/binutils through
# the prefix baked in at build time, so this wrapper only normalizes `-o` and
# forwards every other flag.
#
# cc -c f.c -o f.o
#
# The driver prints a `pspspecs not found` warning: those scripts are for
# linking, and compiling does not need them.
#
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

# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split
rebrew_exec /usr/local/psp/devkit/bin/gcc -c $CC_FLAGS -o "$OUT_ABS" "$SRC_ABS"
