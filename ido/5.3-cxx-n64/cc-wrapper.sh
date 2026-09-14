#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ido/5.3-cxx-n64
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ido-5.3-c++/usr/bin/qemu-irix -silent -L /opt/ido-5.3-c++ /opt/ido-5.3-c++/usr/lib/CC -I /opt/ido-5.3-c++/usr/include "$@"
