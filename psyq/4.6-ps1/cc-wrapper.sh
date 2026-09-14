#!/bin/sh
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
cat > SN.INI <<\INI
[ccpsx]
compiler_path=Z:\opt\psyq-4.6
assembler_path=Z:\opt\psyq-4.6
tmpdir=Z:\tmp
INI
SN_PATH=. rebrew_run /opt/psyq-4.6/CCPSX.EXE "$@"
