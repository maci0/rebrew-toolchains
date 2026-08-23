#!/bin/sh
# cl10 wrapper — compile one translation unit with the vendored MSVC 1.0
# tree under DOSBox (uses the shared wrapper helpers).
#
# Invoke:  cl10 <source.c> [flags...]
#
# Design notes (same contract as the other 16-bit wrappers):
# - CL 1.0 is a 16-bit Phar Lap DOS program: it cannot open long
#   filenames (DOSBox 8.3-truncates them, C1083).  The source is staged
#   under the fixed short name SRC.C, and the produced object is copied
#   back to /work as <source-stem>.OBJ.
# - All other args are forwarded to CL verbatim, so the GA flag sweep
#   (/O1, /Gs, ...) actually reaches the compiler.
# - INCLUDE/LIB point at the vendored tree baked into the image.
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_flags_except_source "$@"

rebrew_dosbox_compile /opt/msvc10 cl10 \
    "set INCLUDE=C:\\INCLUDE
set LIB=C:\\LIB
C:\\BIN\\CL.EXE /nologo /c $FLAGS SRC.C > C:\\clout.txt" \
    clout.txt
