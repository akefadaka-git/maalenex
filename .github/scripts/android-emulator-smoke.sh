#!/bin/sh
set -eu

DEVICE="${ANDROID_SERIAL:-emulator-5554}"
APK="android/app/build/outputs/apk/debug/app-debug.apk"
PACKAGE="com.maalenex.moto"
ACTIVITY="$PACKAGE/.MainActivity"
LOG_FILE="${TMPDIR:-/tmp}/maalenex-android-logcat.txt"

adb_cmd() {
  adb -s "$DEVICE" "$@"
}

diagnose() {
  echo "::error::Android emulator readiness or smoke test failed"
  echo "--- adb version ---"
  adb version 2>&1 || true
  echo "--- adb devices -l ---"
  adb devices -l 2>&1 || true
  echo "--- emulator processes ---"
  ps aux 2>&1 | grep -E '[e]mulator|[q]emu' || true
  echo "--- emulator ports ---"
  lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep -E '5554|5555|5037' || true
  echo "--- boot properties ---"
  adb_cmd shell getprop sys.boot_completed 2>&1 || true
  echo "--- resumed and focused activities ---"
  adb_cmd shell dumpsys activity activities 2>&1 | grep -E 'mResumedActivity|topResumedActivity|Resumed:' || true
  echo "--- recent emulator text logs ---"
  for root in /tmp/android-runner "$HOME/.android/avd"; do
    if [ -d "$root" ]; then
      find "$root" -type f \( -name '*.log' -o -name 'emulator*.log' \) -print 2>/dev/null |
      head -n 20 |
      while IFS= read -r log; do
        echo "### $log"
        tail -n 120 "$log" 2>/dev/null || true
      done
    fi
  done
  echo "--- recent Android logcat ---"
  adb_cmd logcat -b all -d -t 1600 2>&1 | tail -n 300 || true
}

trap 'status=$?; if [ "$status" -ne 0 ]; then diagnose; fi; exit "$status"' 0

echo "Waiting for $DEVICE to be online and fully booted"
ready=false
attempt=0
while [ "$attempt" -lt 60 ]; do
  state="$(adb devices 2>/dev/null | awk -v d="$DEVICE" '$1==d {print $2}' || true)"
  if [ "$state" = "device" ]; then
    boot="$(adb_cmd shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
    if [ "$boot" = "1" ]; then
      ready=true
      break
    fi
  fi
  attempt=$((attempt + 1))
  sleep 2
done
if [ "$ready" != "true" ]; then
  echo "Emulator did not become ready"
  exit 1
fi

adb_cmd shell input keyevent 82
adb_cmd shell settings put global window_animation_scale 0
adb_cmd shell settings put global transition_animation_scale 0
adb_cmd shell settings put global animator_duration_scale 0
test -s "$APK"
adb_cmd install -r "$APK"
adb_cmd shell am force-stop "$PACKAGE"
adb_cmd shell am start -n "$ACTIVITY"

launched=false
attempt=0
while [ "$attempt" -lt 60 ]; do
  activity_state="$(adb_cmd shell dumpsys activity activities 2>/dev/null | grep -E 'mResumedActivity|topResumedActivity|Resumed:' || true)"
  if printf '%s\n' "$activity_state" | grep -F "$PACKAGE" | grep -F 'MainActivity' >/dev/null 2>&1 &&
     adb_cmd shell pidof "$PACKAGE" >/dev/null 2>&1; then
    launched=true
    echo "Confirmed resumed activity: $activity_state"
    break
  fi
  attempt=$((attempt + 1))
  sleep 2
done
if [ "$launched" != "true" ]; then
  echo "MainActivity did not become the resumed foreground activity within 120 seconds"
  exit 1
fi

adb_cmd logcat -b all -d -t 4000 > "$LOG_FILE"
if grep -q "FATAL EXCEPTION" "$LOG_FILE"; then
  tail -n 400 "$LOG_FILE"
  echo "Fatal Android exception detected"
  exit 1
fi
echo "PASS: APK installed and $ACTIVITY reached resumed foreground state on $DEVICE"
