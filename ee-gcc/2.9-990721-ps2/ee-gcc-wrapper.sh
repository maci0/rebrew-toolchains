#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ee-gcc/2.9-990721-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ee-gcc-2.9-990721/bin/ee-gcc -B /opt/ee-gcc-2.9-990721/bin/ee- "$@"
