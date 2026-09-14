#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — borland/5.5-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_run /opt/bcc55/Bin/bcc32.exe -I/opt/bcc55/Include -L/opt/bcc55/Lib "$@"
