#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — watcom/10.5-cxx-win32
# wpp386 wrapper — Watcom C/C++ 10.5 32-bit C++ compiler (Windows PE).
#
# Invoke:  wpp386 [flags...] <source.cpp>
#
# The compiler is a Windows binary, so it runs through the shared
# wine/wibo dispatcher (wine by default; REBREW_RUNNER=wibo uses the minimal
# loader decomp.me's own images rely on) under the common watchdog.  The
# header search paths are baked in as Windows-style Z: paths because Watcom
# rejects Unix '/' in them.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_run /opt/watcom-10.5-cxx/binnt/wpp386.exe -i="Z:\\opt\\watcom-10.5-cxx\\h" -i="Z:\\opt\\watcom-10.5-cxx\\h\\nt" "$@"
