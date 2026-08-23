#!/bin/sh
# tc20 wrapper — compile one translation unit with the vendored Turbo C 2.0
# tree under DOSBox (uses the shared wrapper helpers).
#
# Invoke:  tcc <source.c> [flags...]
#
# Design notes (same contract as the other 16-bit wrappers):
# - TCC 2.0 is a 16-bit DOS program.  The source is staged under the fixed
#   short name SRC.C, and the produced object is copied back to /work as
#   <source-stem>.OBJ.
# - All other args are forwarded to TCC verbatim, so the GA flag sweep
#   (-O1, -G1, ...) actually reaches the compiler.
# - INCLUDE/LIB point at the vendored tree baked into the image.
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_flags_except_source "$@"

rebrew_dosbox_compile /opt/tc20 tc20 \
    "C:\\BIN\\TCC.EXE -c -I\\INCLUDE -oSRC.OBJ $FLAGS SRC.C > C:\\tcout.txt" \
    tcout.txt
