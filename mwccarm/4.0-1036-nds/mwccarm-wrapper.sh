#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — mwccarm/4.0-1036-nds
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/mwccarm-4.0-1036/mwccarm.exe "$@"
