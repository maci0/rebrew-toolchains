#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — armcc/5.04-82-3ds
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/armcc-5.04-82/bin/armcc.exe -I /opt/armcc-5.04-82/include "$@"
