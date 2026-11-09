#!/usr/bin/env bash
set -Eeuo pipefail

cd frontend
adb wait-for-device

booted=""
for attempt in $(seq 1 120); do
  booted="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
  if [[ "$booted" == "1" ]]; then
    break
  fi
  sleep 5
done

if [[ "$booted" != "1" ]]; then
  adb logcat -d -t 2000 > /tmp/maalenex-emulator-boot.log || true
  cat /tmp/maalenex-emulator-boot.log
  echo "Android emulator did not become ready within 10 minutes." >&2
  exit 1
fi

adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell monkey -p com.maalenex.moto 1

# Allow the Capacitor WebView and Android activity to settle before inspection.
sleep 20
foreground=""
for attempt in $(seq 1 12); do
  foreground="$(adb shell dumpsys activity activities 2>/dev/null || true)"
  if grep -E 'mResumedActivity|topResumedActivity' <<<"$foreground" | grep -q 'com.maalenex.moto'; then
    break
  fi
  sleep 5
done
if ! grep -E 'mResumedActivity|topResumedActivity' <<<"$foreground" | grep -q 'com.maalenex.moto'; then
  echo "MaaleNex Moto did not remain in the foreground." >&2
  adb logcat -d -t 3000 > maalenex-emulator-logcat.txt || true
  exit 1
fi

# UIAutomator can briefly return a null root while the launcher/WebView settles.
dumped=""
for attempt in $(seq 1 6); do
  if adb shell uiautomator dump /sdcard/maalenex-window.xml >/dev/null 2>&1 &&
     adb pull /sdcard/maalenex-window.xml ./maalenex-window.xml >/dev/null 2>&1 &&
     test -s ./maalenex-window.xml; then
    dumped="yes"
    break
  fi
  sleep 5
done
if [[ "$dumped" != "yes" ]]; then
  adb logcat -d -t 3000 > maalenex-emulator-logcat.txt || true
  echo "Android UI hierarchy could not be captured after six attempts." >&2
  exit 1
fi

grep -q "MAALE NEX MOTO" ./maalenex-window.xml
adb exec-out screencap -p > maalenex-emulator.png

if adb logcat -d -t 3000 -s AndroidRuntime:E | grep -q 'FATAL EXCEPTION'; then
  adb logcat -d -t 3000 -s AndroidRuntime:E
  exit 1
fi

test -s maalenex-window.xml
test -s maalenex-emulator.png
echo "Android emulator install, launch, foreground, UI hierarchy, screenshot, and fatal-exception checks passed."
