#!/bin/sh
# cl15 wrapper — stage the vendored MSVC 1.5 tree into a fresh DOSBox
# C: drive and run CL.EXE headless (uses the shared wrapper helpers).
#
# Invoke:  cl15 <source.c> [flags...]
#
# Design notes (same contract as the cl16 wrapper for 1.52):
# - CL 1.5 is a 16-bit Phar Lap DOS program: it cannot open long
#   filenames (DOSBox 8.3-truncates them, C1083).  The source is
#   staged under the fixed short name SRC.C, and the produced object
#   is copied back to /work as <source-stem>.OBJ so callers get a
#   predictable name (DOSBox FAT-uppercases on write).
# - All args after the source are forwarded to CL verbatim, so the GA
#   flag sweep (/O1, /Gs, ...) actually reaches the compiler.
# - INCLUDE/LIB point at the vendored tree baked into the image.
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"

flags=""
for a in "$@"; do
    [ "$a" = "$SRC" ] && continue
    flags="$flags $a"
done

sandbox=$(mktemp -d /tmp/cl15.XXXXXX)
trap 'rm -rf "$sandbox"' EXIT

cp -r /opt/msvc15/. "$sandbox"/
cp "$SRC" "$sandbox/SRC.C"

rebrew_dosbox_run "$sandbox" \
    "set INCLUDE=C:\\INCLUDE
set LIB=C:\\LIB
C:\\BIN\\CL.EXE /nologo /c $flags SRC.C > C:\\clout.txt"

cp "$sandbox"/CLOUT.TXT /work/clout.txt 2>/dev/null || true
if rebrew_copy_back "$sandbox" SRC.OBJ "$STEM.OBJ"; then
    exit 0
fi
rebrew_die "CL produced no object (see /work/clout.txt)"
