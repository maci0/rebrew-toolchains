#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — watcom/11.0-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_run /opt/watcom-11.0/binnt/wcc386.exe -i="Z:\\opt\\watcom-11.0\\h" -i="Z:\\opt\\watcom-11.0\\h\\nt" "$@"
