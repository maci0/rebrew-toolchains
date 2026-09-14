#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gcc/2.7.2-sn0006-n64
# cc wrapper — SN64 pipeline (host cpp -> cc1n64 -> asn64 -> obj parser).
#
# The vendored SN64 tools have no usable driver here, so
# The pipeline is decomp.me's recipe verbatim: preprocess with the host cpp
# (the defines the original driver supplies are baked in), compile with
# cc1n64.exe, assemble with asn64.exe, then convert the Sony object to an ELF
# relocatable with the image's psyq-obj-parser.
#
# cc -c f.c -o f.o
#
# -o names the output (default <stem>.o); every other argument goes to
# cc1n64.  The PE stages run in a scratch directory with relative filenames
# (they mangle absolute Unix paths) and inside subshells (the shared run
# helper exits by design, which would end the pipeline after stage one).
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

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT
cd "$_work" || rebrew_die "cannot enter temporary directory"

# SC2310: the run helper exits by design, so a stage is called in a subshell
# under `||`; set -e must not turn a handled failure into an exit.
# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a flag list, word-split
/usr/bin/cpp -E -lang-c -undef -D__GNUC__=2 -Dmips -D__mips__ -D__mips -Dn64 -D__n64__ -D__n64 -D_PSYQ -D__EXTENSIONS__ -D_MIPSEB -D__CHAR_UNSIGNED__ "$SRC_ABS" | ( rebrew_run /opt/gcc-2.7.2-sn0006/cc1n64.exe  $CC_FLAGS -o out.s ) \
    || rebrew_die "cc1n64 failed on $SRC"
# shellcheck disable=SC2310  # same subshell contract as the cc1n64 stage
( rebrew_run /opt/gcc-2.7.2-sn0006/asn64.exe -q -G0 out.s -o out.obj ) \
    || rebrew_die "asn64 failed on the assembly cc1n64 produced"
/opt/gcc-2.7.2-sn0006/psyq-obj-parser out.obj -o "$OUT_ABS" -b -n -s
