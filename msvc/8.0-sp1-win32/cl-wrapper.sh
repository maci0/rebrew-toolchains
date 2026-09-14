#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — msvc/8.0-sp1-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_pick_source "$@"
rebrew_run /opt/msvc8.0-sp1/VC/bin/cl.exe "$@"
