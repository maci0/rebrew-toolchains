#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gcc/3.2-rh8-linux-i386
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
COMPILER_PATH=/opt/rh8/bin
LD_LIBRARY_PATH=/opt/rh8/lib
export COMPILER_PATH LD_LIBRARY_PATH
rebrew_exec /opt/rh8/bin/i386-redhat-linux-gcc "$@"
