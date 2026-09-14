#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gcc/egcs-1.1.2-4c-n64
# cc wrapper — native N64 compiler from a flat vendor tree.
#
# The tree is a flat dump (driver, cc1, cpp, binutils) whose driver resolves
# its tools through COMPILER_PATH, so the wrapper points that at the install
# directory and execs the driver with the caller's arguments unchanged.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
COMPILER_PATH=/opt/gcc-egcs-1.1.2-4c
export COMPILER_PATH
rebrew_exec /opt/gcc-egcs-1.1.2-4c/gcc "$@"
