#!/bin/sh
# cc wrapper — native N64 compiler from a flat vendor tree.
#
# The tree is a flat dump (driver, cc1, cpp, binutils) whose driver resolves
# its tools through COMPILER_PATH, so the wrapper points that at the install
# directory and execs the driver with the caller's arguments unchanged.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"

COMPILER_PATH=/opt/gcc-4.4.0-mips64-elf
export COMPILER_PATH
rebrew_exec /opt/gcc-4.4.0-mips64-elf/bin/mips64-elf-gcc -I /opt/gcc-4.4.0-mips64-elf/mips64-elf/include "$@"
