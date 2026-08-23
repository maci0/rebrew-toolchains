#!/bin/sh
# bcc wrapper — Borland C++ 5.5 (bcc32) under wine or wibo (uses the shared
# helpers; set REBREW_RUNNER=wibo to skip wine for faster runs).
#
# Invoke:  bcc <source.c> [flags...]
#
# bcc32 has no built-in include/lib path (unlike the MSVC trees), so the
# vendored Include/Lib are passed explicitly.  Flags are POSIX-style
# (-c -I<dir> -o...); the object defaults to <source>.obj.
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
rebrew_run /opt/bcc55/Bin/bcc32.exe -I/opt/bcc55/Include -L/opt/bcc55/Lib "$@"
