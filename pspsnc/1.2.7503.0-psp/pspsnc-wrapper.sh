#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — pspsnc/1.2.7503.0-psp
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/pspsnc-1.2.7503.0/pspsnc.exe -td=. "$@"
