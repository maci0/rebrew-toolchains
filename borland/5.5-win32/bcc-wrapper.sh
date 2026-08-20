#!/bin/sh
# bcc wrapper — Borland C++ 5.5 (bcc32) under wine (uses the shared helpers).
#
# Invoke:  bcc <source.c> [flags...]
#
# bcc32 has no built-in include/lib path (unlike the MSVC trees), so the
# vendored Include/Lib are passed explicitly.  Flags are POSIX-style
# (-c -I<dir> -o...); the object defaults to <source>.obj.
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
exec wine /opt/bcc55/Bin/bcc32.exe -I/opt/bcc55/Include -L/opt/bcc55/Lib "$@"
