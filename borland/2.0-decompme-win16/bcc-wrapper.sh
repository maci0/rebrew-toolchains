#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — borland/2.0-decompme-win16
# bcc wrapper — Borland C++ 2.0 (decomp.me repack) under DOSBox.
#
# Invoke:  bcc <source.c> [flags...]
#
# Design notes (same contract as the other 16-bit wrappers):
# - The compiler is a DOS program, so the source is staged under the fixed
# short name SRC.C and the object is copied back to /work as
# <source-stem>.OBJ.  INCLUDE points at the vendored tree.
# - Every other argument is forwarded to BCC verbatim.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_flags_except_source "$@"

rebrew_dosbox_compile /opt/bcc2.0dm bcc2.0 \
    "set INCLUDE=C:\\INCLUDE
C:\\BIN\\BCC.EXE -c $FLAGS SRC.C > C:\\bccout.txt" \
    bccout.txt
