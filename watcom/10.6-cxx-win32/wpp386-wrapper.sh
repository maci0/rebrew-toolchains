#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — watcom/10.6-cxx-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_run /opt/watcom-10.6-cxx/binnt/wpp386.exe -i="Z:\\opt\\watcom-10.6-cxx\\h" -i="Z:\\opt\\watcom-10.6-cxx\\h\\nt" "$@"
