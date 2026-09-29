#!/bin/sh
# dcc wrapper: stage the Delphi 1.0 toolchain into a fresh DOSBox C:
# drive, run DCC headless, copy the produced EXE + log to /work (uses the
# shared wrapper helpers).
#
# DCC is a 16-bit DOS program: a long source basename would be 8.3-truncated
# in DOSBox ("Error 15: File not found"), so a basename that does not fit 8.3
# is staged under the fixed short name SRC.DPR.  A basename that does fit is
# kept as-is: DCC takes the NE module name (the resident-name entry and the
# non-resident <name>.EXE entry) from the source basename, so staging every
# source as SRC.DPR made every build report module "SRC" and no build through
# this wrapper could ever match an original compiled from its own name.
# Either way the produced EXE is copied back under the original basename's
# stem so callers get a predictable output name.
# DOSBox FAT-uppercases outputs (HELLO.EXE, DCCOUT.TXT).
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"

_sandbox=$(mktemp -d /tmp/dcc.XXXXXX) || rebrew_die "mktemp failed"
trap 'rm -rf "$_sandbox"' EXIT

cp -r /opt/delphi10/. "$_sandbox"/ || rebrew_die "cannot stage Delphi toolchain tree"

# 8.3-safe basenames keep their name (see the module-name note above); only a
# basename DOSBox would truncate falls back to SRC.DPR.
_basename=${SRC##*/}
_base=${_basename%.*}
_ext=${_basename##*.}
_staged=SRC.DPR
case "$_basename" in
    *.*.*) ;;                    # more than one dot is never 8.3
    *[!A-Za-z0-9_.-]*) ;;        # a character DOS rejects in a filename
    *)
        if [ -n "$_base" ] && [ "${#_base}" -le 8 ] && [ "${#_ext}" -le 3 ]; then
            _staged=$_basename
        fi
        ;;
esac
cp "$SRC" "$_sandbox/$_staged" || rebrew_die "cannot stage source $SRC"

# DCC reads DCC.CFG for the RTL/VCL unit paths.
printf '/m\n/cw\n/rC:\\DELPHI\\LIB\n/uC:\\DELPHI\\LIB\n/iC:\\DELPHI\\LIB\n' > "$_sandbox/DCC.CFG"

rebrew_dosbox_run "$_sandbox" "C:\\DCC.EXE $_staged > C:\\dccout.txt"
# Returns 0 once the staged EXE is copied back as ${STEM}.EXE; otherwise dies
# embedding the compiler log and how DOSBox itself ended.  DOSBox's FAT
# uppercases the artifact name, so the lookup name is upper-cased too: a
# lower-case source (`t.dpr`) produces T.EXE, not t.EXE.
_staged_exe=$(printf '%s' "${_staged%.*}" | tr '[:lower:]' '[:upper:]').EXE
rebrew_dosbox_collect "$_sandbox" DCCOUT.TXT dccout.txt \
    "$_staged_exe" "${STEM}.EXE" "DCC produced no executable"
