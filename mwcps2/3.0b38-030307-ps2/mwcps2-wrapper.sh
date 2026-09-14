#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — mwcps2/3.0b38-030307-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/mwcps2-3.0b38-030307/mwccps2.exe "$@"
