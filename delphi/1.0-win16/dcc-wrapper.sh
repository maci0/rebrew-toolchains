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
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"

sandbox=$(mktemp -d /tmp/dcc.XXXXXX)
trap 'rm -rf "$sandbox"' EXIT

cp -r /opt/delphi10/. "$sandbox"/
cp "$SRC" "$sandbox/SRC.DPR"

# DCC reads DCC.CFG for the RTL/VCL unit paths.
printf '/m\n/cw\n/rC:\\DELPHI\\LIB\n/uC:\\DELPHI\\LIB\n/iC:\\DELPHI\\LIB\n' > "$sandbox/DCC.CFG"

rebrew_dosbox_run "$sandbox" "C:\\DCC.EXE SRC.DPR > C:\\dccout.txt"

cp "$sandbox"/DCCOUT.TXT /work/dccout.txt 2>/dev/null || true
if rebrew_copy_back "$sandbox" SRC.EXE "${STEM}.EXE"; then
    exit 0
fi
rebrew_log "DCC produced no executable (log: /work/dccout.txt)"
cat "$sandbox/DCCOUT.TXT" 2>/dev/null >&2 || true
rebrew_die "compile failed"
