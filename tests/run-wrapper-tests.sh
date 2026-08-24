#!/bin/sh
# run-wrapper-tests.sh — behavioral harness for base/wrapper-common.sh.
#
# Pins the runner/watchdog contract with stub wine/wibo/dosbox binaries:
# runner dispatch, argv passthrough, exit-status passthrough, timeout-knob
# validation, watchdog kill, source picking, flag assembly and the DOSBox
# run contract.  Run via `make test` or directly; exits nonzero on any
# failure.
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

# 6a. rebrew_timeout_secs unit contract: default, passthrough, boundaries
out=$(sh -c '. '"$WC"'; rebrew_timeout_secs 600 "" KNOB')
check "empty timeout knob takes the default" "600" "$out"
out=$(sh -c '. '"$WC"'; rebrew_timeout_secs 600 90 KNOB')
check "valid timeout knob passes through" "90" "$out"
for bad in 0 -1 abc 1x; do
  out=$(sh -c '. '"$WC"'; rebrew_timeout_secs 600 "$1" KNOB' sh "$bad" 2>&1)
  st=$?
  case "$out" in
    *"must be a positive integer"*)
      if [ "$st" -eq 1 ]; then
        echo "ok   reject timeout knob [$bad]"
      else
        echo "FAIL reject timeout knob [$bad]: st=$st"; fail=1
      fi
      ;;
    *) echo "FAIL reject timeout knob [$bad]: [$out]"; fail=1 ;;
  esac
done

# 7. rebrew_watchdog_status: 137 escalates to 124 only past the cap
out=$(sh -c '. '"$WC"'; rebrew_watchdog_status "$(date +%s)" 5 137')
check "137 below the cap passes through" "137" "$out"
out=$(sh -c '. '"$WC"'; rebrew_watchdog_status 0 5 137')
check "137 at the cap normalizes to 124" "124" "$out"
out=$(sh -c '. '"$WC"'; rebrew_watchdog_status "$(date +%s)" 5 7')
check "non-137 status untouched" "7" "$out"

# 8. rebrew_pick_source: first readable non-flag argument wins
: > "$TMP/f.c"
: > "$TMP/.hidden"
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source /c f.c && printf "SRC=[%s] STEM=[%s]" "$SRC" "$STEM"')
check "pick_source skips MSVC-style flags" "SRC=[f.c] STEM=[f]" "$out"
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source f.c /c && printf "SRC=[%s] STEM=[%s]" "$SRC" "$STEM"')
check "pick_source accepts source-first argv" "SRC=[f.c] STEM=[f]" "$out"
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source -O2 ghost.c f.c && printf "SRC=[%s]" "$SRC"')
check "pick_source skips flags and unreadable names" "SRC=[f.c]" "$out"
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source' 2>&1)
st=$?
case "$out" in
  *"usage:"*)
    if [ "$st" -eq 1 ]; then
      echo "ok   pick_source without args dies loudly"
    else
      echo "FAIL pick_source without args dies loudly: st=$st"; fail=1
    fi
    ;;
  *) echo "FAIL pick_source without args dies loudly: [$out]"; fail=1 ;;
esac
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source /c' 2>&1)
st=$?
case "$out" in
  *"no readable source file"*)
    if [ "$st" -eq 1 ]; then
      echo "ok   pick_source rejects flag-only argv"
    else
      echo "FAIL pick_source rejects flag-only argv: st=$st"; fail=1
    fi
    ;;
  *) echo "FAIL pick_source rejects flag-only argv: [$out]"; fail=1 ;;
esac
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source .hidden' 2>&1)
case "$out" in *"has no stem"*) echo "ok   pick_source rejects extensionless dotfile" ;;
  *) echo "FAIL pick_source rejects extensionless dotfile: [$out]"; fail=1 ;; esac
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source '"$TMP"'/f.c && printf "SRC=[%s] STEM=[%s]" "$SRC" "$STEM"')
check "pick_source accepts an absolute source path" "SRC=[$TMP/f.c] STEM=[f]" "$out"
mkdir -p "$TMP/adir"
out=$(cd "$TMP" && sh -c '. '"$WC"'; rebrew_pick_source adir f.c && printf "SRC=[%s]" "$SRC"')
check "pick_source skips directories" "SRC=[f.c]" "$out"

# 9. rebrew_flags_except_source: source dropped, control characters rejected
out=$(cd "$TMP" && sh -c '. '"$WC"'; SRC=f.c; rebrew_flags_except_source /c -O2 f.c; printf "[%s]" "$FLAGS"')
check "flags_except_source drops the picked source" "[ /c -O2]" "$out"
out=$(cd "$TMP" && sh -c '. '"$WC"'; SRC=f.c; rebrew_flags_except_source && printf "[%s]" "$FLAGS"')
check "flags_except_source with no extra args" "[]" "$out"
out=$(cd "$TMP" && sh -c '. '"$WC"'; SRC=f.c; rebrew_flags_except_source "$1"' sh "$(printf 'a\nb')" 2>&1)
st=$?
case "$out" in
  *"control characters rejected"*)
    if [ "$st" -eq 1 ]; then
      echo "ok   flags_except_source rejects control chars"
    else
      echo "FAIL flags_except_source rejects control chars: st=$st"; fail=1
    fi
    ;;
  *) echo "FAIL flags_except_source rejects control chars: [$out]"; fail=1 ;;
esac

# 10. rebrew_dosbox_run: headless env, generated config, status capture
cat > "$BIN/dosbox" <<'EOF'
#!/bin/sh
echo "SDL=$SDL_VIDEODRIVER AUDIO=$SDL_AUDIODRIVER"
echo "dosbox $*"
for a in "$@"; do
  case "$a" in
    */toolchain.conf) cat "$a" ;;
  esac
done
exit "${STUB_STATUS:-0}"
EOF
chmod +x "$BIN/dosbox"
SBOX="$TMP/sbox"
mkdir -p "$SBOX"
out=$(PATH="$BIN:$PATH" STUB_STATUS=2 REBREW_DOSBOX_TIMEOUT=30 sh -c '
  . '"$WC"'
  rebrew_dosbox_run "'"$SBOX"'" "TCC -c SRC.C"
  printf "status=%s" "$DOSBOX_STATUS"
')
check "dosbox run captures the emulator exit status" "status=2" "$out"
log=$(cat "$SBOX/dosbox.log")
case "$log" in
  "SDL=dummy AUDIO=dummy"*"dosbox -conf $SBOX/toolchain.conf -noconsole"*)
    echo "ok   dosbox runs headless against the sandbox config" ;;
  *) echo "FAIL dosbox invocation/headless env: [$log]"; fail=1 ;;
esac
conf=$(cat "$SBOX/toolchain.conf")
case "$conf" in
  *"fullscreen=false"*"cycles=fixed 30000"*"[autoexec]"*"mount c $SBOX"*"TCC -c SRC.C"*"exit"*)
    echo "ok   dosbox config mounts sandbox and embeds autoexec" ;;
  *) echo "FAIL dosbox config content: [$conf]"; fail=1 ;;
esac
: > "$STUB_LOG"
rm -rf "$SBOX"  # fresh sandbox: the config must not exist unless this run wrote it
mkdir -p "$SBOX"
out=$(PATH="$BIN:$PATH" REBREW_DOSBOX_TIMEOUT=nope \
  sh -c '. '"$WC"'; rebrew_dosbox_run "'"$SBOX"'" "TCC -c SRC.C"' 2>&1)
case "$out" in
  *"must be a positive integer"*)
    if [ ! -s "$STUB_LOG" ] && [ ! -e "$SBOX/toolchain.conf" ]; then
      echo "ok   invalid DOSBOX_TIMEOUT rejected without running dosbox"
    else
      echo "FAIL invalid DOSBOX_TIMEOUT: dosbox ran or config was written"; fail=1
    fi
    ;;
  *) echo "FAIL invalid DOSBOX_TIMEOUT rejected: [$out]"; fail=1 ;;
esac
rm -rf "$SBOX"

# 11. hung tool killed at the cap -> explicit error naming the knob
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
