#!/bin/sh
# run-wrapper-tests.sh — behavioral harness for base/wrapper-common.sh.
#
# Pins the runner/watchdog contract with stub wine/wibo binaries: runner
# dispatch, argv passthrough, exit-status passthrough, timeout-knob
# validation and the watchdog kill.  Run via `make test` or directly;
# exits nonzero on any failure.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WC="$ROOT/base/wrapper-common.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
BIN="$TMP/bin"
mkdir -p "$BIN"

# mk_stub <name> — stub runner: logs its argv, exits with $STUB_STATUS.
# The \$ escapes keep the references literal so they expand when the stub
# runs, not when it is generated.
mk_stub() {
  cat > "$BIN/$1" <<EOF
#!/bin/sh
echo "$1 \$*" >> "\$STUB_LOG"
exit "\${STUB_STATUS:-0}"
EOF
  chmod +x "$BIN/$1"
}
mk_stub wine
mk_stub wibo

STUB_LOG="$TMP/log"
export STUB_LOG

fail=0
check() { # <name> <expected> <actual>
  if [ "$2" = "$3" ]; then
    echo "ok   $1"
  else
    echo "FAIL $1:"
    echo "  expected [$2]"
    echo "  actual   [$3]"
    fail=1
  fi
}

# 1. default runner is wine, args forwarded verbatim
: > "$STUB_LOG"
out=$(PATH="$BIN:$PATH" sh -c '. '"$WC"'; rebrew_run /opt/x/CL.EXE /c f.c')
st=$?
log=$(cat "$STUB_LOG")
check "default wine forwards argv" \
  "status=0 log=[wine /opt/x/CL.EXE /c f.c]" "status=$st log=[$log]"

# 2. explicit wibo selection
: > "$STUB_LOG"
out=$(PATH="$BIN:$PATH" REBREW_RUNNER=wibo sh -c '. '"$WC"'; rebrew_run /opt/x/CL.EXE /c f.c')
st=$?
log=$(cat "$STUB_LOG")
check "wibo forwards argv" \
  "status=0 log=[wibo /opt/x/CL.EXE /c f.c]" "status=$st log=[$log]"

# 3. unknown runner dies loudly without running anything
out=$(PATH="$BIN:$PATH" REBREW_RUNNER=dosbox sh -c '. '"$WC"'; rebrew_run /bin/echo hi' 2>&1)
st=$?
case "$out" in
  *"unknown REBREW_RUNNER 'dosbox'"*)
    if [ "$st" -eq 1 ]; then
      echo "ok   unknown runner dies loudly"
    else
      check "unknown runner dies loudly" "exit 1" "exit $st"
    fi
    ;;
  *) check "unknown runner dies loudly" "die message" "$out" ;;
esac

# 4. the tool's own exit status passes through unchanged
: > "$STUB_LOG"
env STUB_STATUS=7 PATH="$BIN:$PATH" REBREW_RUNNER=wibo \
  sh -c '. '"$WC"'; rebrew_run /opt/x/tool.exe' >/dev/null 2>&1
st=$?
log=$(cat "$STUB_LOG")
check "tool exit status passes through" \
  "status=7 log=[wibo /opt/x/tool.exe]" "status=$st log=[$log]"

# 5. invalid timeout knob rejected without running the tool
: > "$STUB_LOG"
out=$(PATH="$BIN:$PATH" REBREW_RUNNER_TIMEOUT=nope \
  sh -c '. '"$WC"'; rebrew_run /opt/x/tool.exe' 2>&1)
st=$?
case "$out" in
  *"must be a positive integer"*)
    if [ "$st" -eq 1 ] && [ ! -s "$STUB_LOG" ]; then
      echo "ok   invalid timeout knob rejected"
    else
      echo "FAIL invalid timeout knob rejected: st=$st but tool log not empty"
      fail=1
    fi
    ;;
  *) echo "FAIL invalid timeout knob rejected: [$out]"; fail=1 ;;
esac

# 6. hung tool killed at the cap -> explicit error naming the knob
SLOW="$BIN/slowdir"
mkdir -p "$SLOW"
printf '#!/bin/sh\nsleep 30\n' > "$SLOW/wine"
chmod +x "$SLOW/wine"
out=$(PATH="$SLOW:$BIN:$PATH" REBREW_RUNNER_TIMEOUT=1 \
  sh -c '. '"$WC"'; rebrew_run /opt/x/hang.exe' 2>&1)
st=$?
rm -rf "$SLOW"
case "$out" in
  *"exceeded 1s (REBREW_RUNNER_TIMEOUT) and was killed"*)
    if [ "$st" -eq 1 ]; then
      echo "ok   watchdog kill fails loudly"
    else
      check "watchdog kill fails loudly" "exit 1" "exit $st"
    fi
    ;;
  *) echo "FAIL watchdog kill fails loudly: st=$st out=[$out]"; fail=1 ;;
esac

if [ "$fail" -eq 0 ]; then
  echo "ALL-PASS"
else
  echo "HARNESS-FAILURES"
fi
exit "$fail"
