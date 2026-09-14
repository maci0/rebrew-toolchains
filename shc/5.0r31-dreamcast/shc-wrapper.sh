#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — shc/5.0r31-dreamcast
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

SHC_LIB=/opt/shc-5.0r31/bin
SHC_TMP=${TMPDIR:-/tmp}
export SHC_LIB SHC_TMP
rebrew_run /opt/shc-5.0r31/bin/shc.exe "$@"
