#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — watcom/10.5-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_run /opt/watcom-10.5/binnt/wcc386.exe -i="Z:\\opt\\watcom-10.5\\h" -i="Z:\\opt\\watcom-10.5\\h\\nt" "$@"
