#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — msvc/6.0-win9x-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
export INCLUDE="Z:\\opt\\msvc6.0-win9x\\Include"
rebrew_run /opt/msvc6.0-win9x/Bin/CL.EXE "$@"
