#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ee-gcc/2.95.3-136-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/ee-gcc-2.95.3/bin/ee-gcc.exe "$@"
