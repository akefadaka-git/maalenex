#!/usr/bin/env bash
set -Eeuo pipefail

DEVICE="${ANDROID_SERIAL:-emulator-5554}"
APK="android/app/build/outputs/apk/debug/app-debug.apk"
PACKAGE="com.maalenex.moto"
ACTIVITY="$PACKAGE/.MainActivity"

adb_cmd() {
  timeout 8s adb -s "$DEVICE" "$@"
}

diagnose() {
  echo "::error::Android emulator readiness or smoke test failed"
  echo "--- adb version ---"; timeout 5s adb version || true
  echo "--- adb devices -l ---"; timeout 8s adb devices -l || true
  echo "--- emulator processes ---"; ps -ef | grep -E '[e]mulator|[q]emu' || true
  echo "--- emulator ports ---"; (ss -lntp 2>/dev/null | grep -E '5554|5555|5037' || true)
  echo "--- boot properties ---"; adb_cmd shell getprop sys.boot_completed 2>&1 || true
  echo "--- emulator runner files ---"
  find /tmp/android-runner "$HOME/.android/avd" -maxdepth 4 -type f -printf '%p (%s bytes)\\n' 2>/dev/null | head -n 40 || true
  echo "--- recent emulator text logs ---"
  while IFS= read -r log; do
    echo "### $log"
    tail -n 120 "$log" || true
  done < <(find /tmp/android-runner "$HOME/.android/avd" -type f \\( -name '*.log' -o -name 'emulator*.log' \\) -print 2>/dev/null | head -n 20)
  echo "--- recent Android logcat ---"
  timeout 10s adb -s "$DEVICE" logcat -b all -d -t 1200 2>&1 | tail -n 240 || true
}

trap 'status=$?; if [ "$status" -ne 0 ]; then diagnose; fi; exit "$status"' EXIT

echo "Waiting for $DEVICE to be online and fully booted"
ready=false
for attempt in $(seq 1 30); do
  state="$(timeout 5s adb devices 2>/dev/null | awk -v d="$DEVICE" '$1==d {print $2}' || true)"
  if [ "$state" = "device" ]; then
    boot="$(adb_cmd shell getprop sys.boot_completed 2>/dev/null | tr -d '\\r' || true)"
    if [ "$boot" = "1" ]; then ready=true; break; fi
  fi
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
timeout 90s adb -s "$DEVICE" install -r "$APK"
adb_cmd shell am force-stop "$PACKAGE"
timeout 30s adb -s "$DEVICE" shell am start -W -n "$ACTIVITY"

launched=false
for attempt in $(seq 1 30); do
  if adb_cmd shell pidof "$PACKAGE" >/dev/null 2>&1; then launched=true; break; fi
  sleep 2
done
if [ "$launched" != "true" ]; then
  echo "Application process did not remain alive after launch"
  exit 1
fi

timeout 10s adb -s "$DEVICE" logcat -b all -d -t 4000 > /tmp/maalenex-logcat.txt
if grep -q "FATAL EXCEPTION" /tmp/maalenex-logcat.txt; then
  tail -n 400 /tmp/maalenex-logcat.txt
  echo "Fatal Android exception detected"
  exit 1
fi
adb_cmd shell dumpsys activity activities | grep -q "$ACTIVITY"
echo "PASS: APK installed and $ACTIVITY launched on $DEVICE"
