#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — iop-gcc/2.8.1-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/iop-gcc-2.8.1/bin/iop-gcc -B /opt/iop-gcc-2.8.1/lib/gcc-lib/mipsel-scei-elfl/2.8.1/ "$@"
