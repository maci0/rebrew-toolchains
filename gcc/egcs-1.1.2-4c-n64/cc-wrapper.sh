#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gcc/egcs-1.1.2-4c-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
COMPILER_PATH=/opt/gcc-egcs-1.1.2-4c
export COMPILER_PATH
rebrew_exec /opt/gcc-egcs-1.1.2-4c/gcc "$@"
