#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — iop-gcc/2.95.2-102-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_run /opt/iop-gcc-2.95.2-102/bin/iop-gcc.exe -B /opt/iop-gcc-2.95.2-102/lib/gcc-lib/mipsel-scei-elfl/2.95.2/ "$@"
