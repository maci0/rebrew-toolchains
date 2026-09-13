#!/bin/sh
# cc wrapper — Cygnus 2.7-96Q3 (Sega Saturn) pipeline.
#
#   cpp -> cc1 -> as -> sh-elf-objcopy (-Icoff-sh -Oelf32-sh)
#
# The three compiler stages are DOS binaries, so each runs in its own dosemu2
# session (see rebrew_dosemu_run).  Host cpp does the preprocessing, exactly as
# decomp.me's recipe does, and the final coff-sh -> elf32-sh conversion uses the
# Linux sh-elf-objcopy (the archive's DOS OBJCOPY.EXE does not run).
#
#   cc -c f.c -o f.o
#
# -o names the output (default <stem>.o); every other argument goes to CC1.
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

# The DOS side sees this directory as drive D:; CRLF input because CPP.EXE is
# a DOS binary.
# shellcheck disable=SC2086  # CC_FLAGS is a deliberate flag list, word-split
/usr/bin/cpp -E "$SRC_ABS" | unix2dos > dos_src.c \
    || rebrew_die "preprocessing $SRC failed"

rebrew_dosemu_run "$_work" /opt/saturn-cygnus \
    "CPP.EXE D:\\dos_src.c -o D:\\src_proc.c"
if [ ! -s "$_work/src_proc.c" ]; then
    _note=$(rebrew_dosemu_failure_note)
    rebrew_die "cpp.exe produced no preprocessed source for $SRC$_note"
fi

# shellcheck disable=SC2086  # CC_FLAGS is a flag list, word-split
rebrew_dosemu_run "$_work" /opt/saturn-cygnus \
    "CC1.EXE -quiet $CC_FLAGS D:\\src_proc.c -o D:\\output.s"
if [ ! -s "$_work/output.s" ]; then
    _note=$(rebrew_dosemu_failure_note)
    rebrew_die "cc1.exe produced no assembly for $SRC$_note"
fi

rebrew_dosemu_run "$_work" /opt/saturn-cygnus \
    "AS.EXE D:\\output.s -o D:\\output.o"
if [ ! -s "$_work/output.o" ]; then
    _note=$(rebrew_dosemu_failure_note)
    rebrew_die "as.exe produced no object for $SRC$_note"
fi

# The archive's DOS OBJCOPY.EXE cannot do this conversion under dosemu2
# (silent, errorlevel 1), so the Linux sh-elf-objcopy does it — decomp.me's
# own recipe uses sh-elf-objcopy for this step too.
sh-elf-objcopy -Icoff-sh -Oelf32-sh "$_work/output.o" "$OUT_ABS"
