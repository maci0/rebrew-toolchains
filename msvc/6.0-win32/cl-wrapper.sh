#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — msvc/6.0-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
export INCLUDE="Z:\\opt\\msvc6.0\\VC98\\Include"
export LIB="Z:\\opt\\msvc6.0\\VC98\\Lib"
rebrew_run /opt/msvc6.0/VC98/Bin/CL.EXE "$@"
