#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — psyq/4.0-ps1
# cc wrapper — PSY-Q (PS1): the SDK's two-stage compiler pipeline.
#
# This SDK has no single driver.  CC1PSX.EXE compiles a preprocessed source
# to assembly, ASPSX.EXE assembles that into a Sony-format object, and that
# object still needs psyq-obj-parser to become an ELF relocatable.  The
# wrapper runs the same pipeline decomp.me's recipe does, so callers use it
# like an ordinary compiler:
#
# cc -c f.c -o f.o      # → f.o, a MIPS ELF relocatable
#
# The source is picked out of argv (flags may precede or follow it), -o names
# the output (default <stem>.o), and every other argument is forwarded to
# CC1PSX.  PSYQ_ROOT is set by the image to its own SDK tree.
#
# The PE stages run inside a scratch directory with *relative* filenames: the
# Sony tools mangle absolute Unix paths (they rewrite them as Windows paths),
# so only the native psyq-obj-parser ever sees an absolute path.
#
# Each PE stage is called in a subshell: the shared rebrew_run/rebrew_exec
# helper ends with `exit`, which is right for a one-command wrapper and fatal
# here — without the subshell the pipeline would stop after CC1PSX.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
# The image sets this; failing loudly beats exec'ing "/CC1PSX.EXE".
PSYQ_ROOT="${PSYQ_ROOT:?PSYQ_ROOT must point at the SDK tree (set by the image)}"

rebrew_pick_source "$@"

OUT=""
CC_FLAGS=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] || rebrew_die "-o requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;  # CC1PSX always compiles; the driver flag is ours
        "$SRC") shift ;;
        *)
            CC_FLAGS="$CC_FLAGS $1"
            shift
            ;;
    esac
done
[ -n "$OUT" ] || OUT="$STEM.o"

# resolve the caller's paths before changing directory
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT

cd "$_work" || rebrew_die "cannot enter temporary directory"

# CC1PSX consumes the preprocessed source on stdin and the SDK's own flow
# converts it to DOS line endings first, so keep both steps.
# shellcheck disable=SC2310  # rebrew_die exits; the `||` is the documented contract
/usr/bin/cpp -P "$SRC_ABS" | unix2dos > src.i \
    || rebrew_die "preprocessing $SRC failed"

# SC2310: the stage helpers exit on completion by design, so they are called
# in a subshell under `||`; set -e must not turn a handled failure into an exit.
# shellcheck disable=SC2086,SC2310  # CC_FLAGS is a deliberate flag list, word-split
( rebrew_run "$PSYQ_ROOT/CC1PSX.EXE" -quiet $CC_FLAGS -o out.s < src.i ) \
    || rebrew_die "CC1PSX failed on $SRC"
# shellcheck disable=SC2310  # same subshell contract as the CC1PSX stage
( rebrew_run "$PSYQ_ROOT/ASPSX.EXE" -quiet out.s -o out.bj ) \
    || rebrew_die "ASPSX failed on the assembly CC1PSX produced"

"$PSYQ_ROOT/psyq-obj-parser" out.bj -o "$OUT_ABS"
