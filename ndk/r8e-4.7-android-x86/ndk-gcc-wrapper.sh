#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ndk/r8e-4.7-android-x86
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ndk-r8e-4.7/toolchains/x86-4.7/prebuilt/linux-x86_64/bin/i686-linux-android-gcc --sysroot=/opt/ndk-r8e-4.7/platforms/android-9/arch-x86 "$@"
