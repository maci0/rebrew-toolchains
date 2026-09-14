#!/bin/sh
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
rebrew_pick_source "$@"
export INCLUDE="Z:\\opt\\msvc6.0-win9x\\Include"
rebrew_run /opt/msvc6.0-win9x/Bin/CL.EXE "$@"
