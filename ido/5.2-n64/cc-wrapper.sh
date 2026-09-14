#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ido/5.2-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ido-5.2/usr/bin/qemu-irix -L /opt/ido-5.2 /opt/ido-5.2/usr/lib/driver -I /opt/ido-5.2/usr/include "$@"
