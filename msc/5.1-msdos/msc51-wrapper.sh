#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — msc/5.1-msdos
# msc51 wrapper — Microsoft C 5.1 compiler under DOSBox (shared helpers).
#
# Invoke:  mscl <source.c> [flags...]
#
# Design notes (same contract as the other 16-bit wrappers):
# - CL 5.1 is a 16-bit DOS program, so the source is staged under the fixed
# short name SRC.C and the object is copied back to /work as
# <source-stem>.OBJ.  Compiles are object-only (/c), so no library path is
# configured; INCLUDE points at the vendored tree.
# - Every other argument is forwarded to CL verbatim.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_flags_except_source "$@"

rebrew_dosbox_compile /opt/msc51 msc51 \
    "set INCLUDE=C:\\INCLUDE
C:\\BIN\\CL.EXE /c $FLAGS SRC.C > C:\\mscout.txt" \
    mscout.txt
