#!/usr/bin/env bash
set -Eeuo pipefail

cd frontend
adb wait-for-device

booted=""
for attempt in $(seq 1 60); do
  booted="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
  if [[ "$booted" == "1" ]]; then
    break
  fi
  sleep 5
done

if [[ "$booted" != "1" ]]; then
  adb logcat -d -t 2000 > /tmp/maalenex-emulator-boot.log || true
  cat /tmp/maalenex-emulator-boot.log
  echo "Android emulator did not become ready within 5 minutes." >&2
  exit 1
fi

adb shell pm grant com.maalenex.moto android.permission.INTERNET 2>/dev/null || true
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell monkey -p com.maalenex.moto 1
sleep 12
adb shell dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity' | grep -q 'com.maalenex.moto'
adb shell uiautomator dump /sdcard/maalenex-window.xml >/dev/null
adb pull /sdcard/maalenex-window.xml ./maalenex-window.xml
grep -q "MAALE NEX MOTO" ./maalenex-window.xml
adb exec-out screencap -p > maalenex-emulator.png

if adb logcat -d -t 3000 -s AndroidRuntime:E | grep -q 'FATAL EXCEPTION'; then
  adb logcat -d -t 3000 -s AndroidRuntime:E
  exit 1
fi

test -s maalenex-window.xml
test -s maalenex-emulator.png
echo "Android emulator install, launch, foreground, UI hierarchy, screenshot, and fatal-exception checks passed."
