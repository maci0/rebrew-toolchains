#!/bin/sh
# tc16 wrapper — stage the vendored Turbo C++ 3.1 tree into a fresh DOSBox
# C: drive and run TCC.EXE headless (uses the shared wrapper helpers).
#
# Invoke:  tcc <source.c> [flags...]
#
# Design notes:
# - TCC 3.1 is a 16-bit DOS program; the source is staged under the fixed
#   short name SRC.C and the produced object is copied back to /work as
#   <source-stem>.OBJ (DOSBox FAT-uppercases on write).
# - All args after the source are forwarded to TCC verbatim, so the GA
#   flag sweep (-O1, -G1, ...) actually reaches the compiler.
# - INCLUDE/LIB point at the vendored tree baked into the image.
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"

flags=""
for a in "$@"; do
    [ "$a" = "$SRC" ] && continue
    flags="$flags $a"
done

sandbox=$(mktemp -d /tmp/tc16.XXXXXX)
trap 'rm -rf "$sandbox"' EXIT

cp -r /opt/tc31/. "$sandbox"/
cp "$SRC" "$sandbox/SRC.C"

rebrew_dosbox_run "$sandbox" \
    "C:\\BIN\\TCC.EXE -c -I\\INCLUDE -oSRC.OBJ $flags SRC.C > C:\\tcout.txt"

cp "$sandbox"/TCOUT.TXT /work/tcout.txt 2>/dev/null || true
if rebrew_copy_back "$sandbox" SRC.OBJ "${STEM}.OBJ"; then
    exit 0
fi
# The compile workdir is transient (compile_to_obj cleans it up), so the
# bare "see /work/tcout.txt" hint leaves the user with nothing to read —
# embed the compiler log in the error instead.
if [ -f "$sandbox"/TCOUT.TXT ]; then
    rebrew_die "TCC produced no object; compiler log:\n$(cat "$sandbox"/TCOUT.TXT 2>/dev/null)"
else
    rebrew_die "TCC produced no object (no compiler log written)"
fi
