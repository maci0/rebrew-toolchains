#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — armcc/4.0-821-3ds
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/armcc-4.0-821/bin/armcc.exe -I /opt/armcc-4.0-821/include "$@"
