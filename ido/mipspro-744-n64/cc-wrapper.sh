#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ido/mipspro-744-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ido-mipspro-744/usr/bin/qemu-irix -L /opt/ido-mipspro-744 /opt/ido-mipspro-744/usr/lib/driver -I /opt/ido-mipspro-744/usr/include "$@"
