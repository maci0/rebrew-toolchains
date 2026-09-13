#!/bin/sh
# gcc wrapper — Red Hat 8 GCC 3.2 (i386-redhat-linux, native, under the shared
# watchdog contract).
#
# Invoke:  gcc [flags...] <source.c>
#
# The tree is a relocated Red Hat prefix: COMPILER_PATH points the driver at
# its own bin/ (cc1, as) and LD_LIBRARY_PATH at the bundled shared libraries
# (libbfd and friends) that its assembler links.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
COMPILER_PATH=/opt/rh8/bin
LD_LIBRARY_PATH=/opt/rh8/lib
export COMPILER_PATH LD_LIBRARY_PATH
rebrew_exec /opt/rh8/bin/i386-redhat-linux-gcc "$@"
