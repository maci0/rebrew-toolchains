#!/bin/sh
# dcc wrapper — stage the Delphi 1.0 toolchain into a fresh DOSBox C:
# drive, run DCC headless, copy the produced EXE + log to /work (uses the
# shared wrapper helpers).
#
# DCC is a 16-bit DOS program: a long source basename would be 8.3-truncated
# in DOSBox ("Error 15: File not found"), so the source is staged under the
# fixed short name SRC.DPR and the produced SRC.EXE is copied back under the
# original basename's stem so callers get a predictable output name.
# DOSBox FAT-uppercases outputs (HELLO.EXE, DCCOUT.TXT).
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"

_sandbox=$(mktemp -d /tmp/dcc.XXXXXX) || rebrew_die "mktemp failed"
trap 'rm -rf "$_sandbox"' EXIT

cp -r /opt/delphi10/. "$_sandbox"/ || rebrew_die "cannot stage Delphi toolchain tree"
cp "$SRC" "$_sandbox/SRC.DPR" || rebrew_die "cannot stage source $SRC"

# DCC reads DCC.CFG for the RTL/VCL unit paths.
printf '/m\n/cw\n/rC:\\DELPHI\\LIB\n/uC:\\DELPHI\\LIB\n/iC:\\DELPHI\\LIB\n' > "$_sandbox/DCC.CFG"

rebrew_dosbox_run "$_sandbox" "C:\\DCC.EXE SRC.DPR > C:\\dccout.txt"
# Returns 0 once SRC.EXE is copied back as ${STEM}.EXE; otherwise dies
# embedding the compiler log and how DOSBox itself ended.
rebrew_dosbox_collect "$_sandbox" DCCOUT.TXT dccout.txt \
    SRC.EXE "${STEM}.EXE" "DCC produced no executable"
