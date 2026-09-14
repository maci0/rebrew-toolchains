#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — msvc/8.0-portable-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
export INCLUDE="Z:\\opt\\msvc8.0-portable\\include"
export LIB="Z:\\opt\\msvc8.0-portable\\lib"
rebrew_run /opt/msvc8.0-portable/bin/cl.exe "$@"
