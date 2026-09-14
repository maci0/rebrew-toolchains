#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gcc/2.8.1-pm-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/gcc-2.8.1-pm/gcc -B /opt/gcc-2.8.1-pm/ "$@"
