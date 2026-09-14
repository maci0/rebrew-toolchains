#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — mwcps2/3.0b50-030527-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/mwcps2-3.0b50-030527/mwccps2.exe "$@"
