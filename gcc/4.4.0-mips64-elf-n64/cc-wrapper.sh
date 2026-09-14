#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gcc/4.4.0-mips64-elf-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
COMPILER_PATH=/opt/gcc-4.4.0-mips64-elf
export COMPILER_PATH
rebrew_exec /opt/gcc-4.4.0-mips64-elf/bin/mips64-elf-gcc -I /opt/gcc-4.4.0-mips64-elf/mips64-elf/include "$@"
