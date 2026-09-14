#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ido/5.3-irix-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ido-irix-5.3/usr/bin/qemu-irix -L /opt/ido-irix-5.3 /opt/ido-irix-5.3/usr/lib/driver -I /opt/ido-irix-5.3/usr/include "$@"
