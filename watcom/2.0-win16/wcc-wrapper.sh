#!/bin/sh
# wcc wrapper — native 16-bit Open Watcom compiler under the shared watchdog
# contract (uses the wrapper-common helpers).
#
# Invoke:  wcc [flags...] <source.c>
#
# wcc is a native Linux binary, so there is no PE loader to select and
# REBREW_RUNNER does not apply.  The run is still capped by
# REBREW_RUNNER_TIMEOUT (seconds, default 600) so a hung compile fails
# loudly like every other entrypoint.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_exec /opt/watcom/binl/wcc "$@"
