#!/bin/sh
# wcc386 wrapper — Watcom C/C++ 10.6 32-bit compiler (Windows PE).
#
# Invoke:  wcc386 [flags...] <source.c>
#
# The compiler is a Windows binary, so it runs through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo uses the minimal
# loader decomp.me's own images rely on) under the common watchdog.  The
# header search paths are baked in as Windows-style Z: paths because Watcom
# rejects Unix '/' in them.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_run /opt/watcom-10.6/binnt/wcc386.exe \
    -i="Z:\\opt\\watcom-10.6\\h" -i="Z:\\opt\\watcom-10.6\\h\\nt" "$@"
