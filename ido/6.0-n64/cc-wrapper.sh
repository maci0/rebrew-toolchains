#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ido/6.0-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ido-6.0/usr/bin/qemu-irix -L /opt/ido-6.0 /opt/ido-6.0/usr/lib/driver -I /opt/ido-6.0/usr/include "$@"
