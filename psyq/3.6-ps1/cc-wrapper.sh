#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — psyq/3.6-ps1
# cc wrapper — PSY-Q 3.6 pipeline (host cpp -> CC1PSX -> ASPSX -> obj parser).
#
# These are 1994 DOS binaries, so each stage runs in its own dosemu2 session
# (see rebrew_dosemu_run; DOSBox cannot load their DJGPP stub).  decomp.me's
# recipe, with the host cpp doing the preprocessing and the image's
# psyq-obj-parser converting the Sony object to an ELF relocatable.
#
# cc -c f.c -o f.o
#
# -o names the output (default <stem>.o); every other argument goes to CC1PSX.
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

# CC1PSX wants preprocessed input with DOS line endings; the DOS side sees this
# directory as drive D: (dosemu2's `+0 <dir> +1` image, set by the helper).
# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split
/usr/bin/cpp -E "$SRC_ABS" | unix2dos > dos_src.c \
    || rebrew_die "preprocessing $SRC failed"
{
    printf '@echo off\r\n'
    printf 'CC1PSX.EXE -quiet %s D:\\dos_src.c -o D:\\output.s\r\n' "$CC_FLAGS"
    printf 'EXIT /B\r\n'
} > COMPILE.BAT

rebrew_dosemu_run "$_work" /opt/psyq-3.6 "D:\\COMPILE.BAT"
if [ ! -s "$_work/output.s" ]; then
    # Assign first: SC2312 — a command substitution inside the message would
    # mask rebrew_dosemu_failure_note's own exit status.
    _note=$(rebrew_dosemu_failure_note)
    printf 'cc1psx produced no assembly for %s%s\n' "$SRC" "$_note" >&2
    sed -n '$p' "$_work/dosemu.log" >&2 2>/dev/null
    exit 1
fi

rebrew_dosemu_run "$_work" /opt/psyq-3.6 "ASPSX.EXE -quiet D:\\output.s -o D:\\output.obj"
if [ ! -s "$_work/output.obj" ]; then
    _note=$(rebrew_dosemu_failure_note)
    rebrew_die "aspsx produced no object for $SRC$_note"
fi

/opt/psyq-3.6/psyq-obj-parser "$_work/output.obj" -o "$OUT_ABS"
