#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — borland/5.6-win32
# bcc wrapper — Borland C++ 5.6 (bcc32) under wine or wibo (uses the shared
# helpers; set REBREW_RUNNER=wibo to skip wine for faster runs).
#
# Invoke:  bcc <source.c> [flags...]
#
# bcc32 has no built-in include/lib path (unlike the MSVC trees), so the
# vendored Include/Lib are passed explicitly.  Flags are POSIX-style
# (-c -I<dir> -o...); the object defaults to <source>.obj.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_run /opt/bcc56/BIN/BCC32.EXE -I/opt/bcc56/INCLUDE -L/opt/bcc56/LIB "$@"
