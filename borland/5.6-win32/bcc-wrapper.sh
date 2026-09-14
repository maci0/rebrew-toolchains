#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — borland/5.6-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_run /opt/bcc56/BIN/BCC32.EXE -I/opt/bcc56/INCLUDE -L/opt/bcc56/LIB "$@"
