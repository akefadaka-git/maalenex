#!/bin/sh
set -eu

DEVICE="${ANDROID_SERIAL:-emulator-5554}"
APK="android/app/build/outputs/apk/debug/app-debug.apk"
PACKAGE="com.maalenex.moto"
ACTIVITY="$PACKAGE/.MainActivity"
ARTIFACT_DIR="artifacts/android-smoke"
LOG_FILE="$ARTIFACT_DIR/logcat.txt"
EVIDENCE_FILE="$ARTIFACT_DIR/evidence.txt"

mkdir -p "$ARTIFACT_DIR"

adb_cmd() {
  adb -s "$DEVICE" "$@"
}

capture_diagnostics() {
  adb_cmd logcat -b all -d -v brief -t 5000 > "$LOG_FILE" 2>&1 || true
  tail -n 2000 "$LOG_FILE" > "$ARTIFACT_DIR/logcat-bounded.txt" 2>/dev/null || true
  {
    echo "DEVICE=$DEVICE"
    echo "PACKAGE=$PACKAGE"
    echo "CAPTURED_AT_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "--- app pid ---"
    adb_cmd shell pidof "$PACKAGE" 2>&1 || true
    echo "--- resumed activity ---"
    adb_cmd shell dumpsys activity activities 2>&1 | grep -E 'mResumedActivity|topResumedActivity|Resumed:' || true
  } >> "$EVIDENCE_FILE"
}

diagnose() {
  echo "::error::Android emulator readiness or WebView probe verification failed"
  echo "--- adb version ---"
  adb version 2>&1 || true
  echo "--- adb devices -l ---"
  adb devices -l 2>&1 || true
  echo "--- emulator processes ---"
  ps aux 2>&1 | grep -E '[e]mulator|[q]emu' || true
  echo "--- boot properties ---"
  adb_cmd shell getprop sys.boot_completed 2>&1 || true
  echo "--- recent Android logcat ---"
  capture_diagnostics
  tail -n 300 "$ARTIFACT_DIR/logcat-bounded.txt" 2>/dev/null || true
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

# Establish a clean evidence window before launching this exact APK.
adb_cmd logcat -c
adb_cmd shell am force-stop "$PACKAGE"
adb_cmd shell am start -n "$ACTIVITY"

launched=false
attempt=0
APP_PID=""
while [ "$attempt" -lt 60 ]; do
  activity_state="$(adb_cmd shell dumpsys activity activities 2>/dev/null | grep -E 'mResumedActivity|topResumedActivity|Resumed:' || true)"
  APP_PID="$(adb_cmd shell pidof "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
  if printf '%s\n' "$activity_state" | grep -F "$PACKAGE" | grep -F 'MainActivity' >/dev/null 2>&1 &&
     [ -n "$APP_PID" ]; then
    launched=true
    echo "Confirmed resumed activity: $activity_state"
    echo "APP_PID=$APP_PID" | tee -a "$EVIDENCE_FILE"
    break
  fi
  attempt=$((attempt + 1))
  sleep 2
done
if [ "$launched" != "true" ]; then
  echo "MainActivity did not become the resumed foreground activity within 120 seconds"
  exit 1
fi

webview_ready=false
attempt=0
while [ "$attempt" -lt 45 ]; do
  adb_cmd logcat -d -v brief > "$ARTIFACT_DIR/logcat-live.txt" 2>/dev/null || true
  if grep -F "MaaleNexWebView" "$ARTIFACT_DIR/logcat-live.txt" | grep -F "WEBVIEW_PAGE_FINISHED" >/dev/null 2>&1 &&
     grep -F "MaaleNexWebView" "$ARTIFACT_DIR/logcat-live.txt" | grep -F "WEBVIEW_JS_PROBE_JSON" >/dev/null 2>&1; then
    webview_ready=true
    break
  fi
  attempt=$((attempt + 1))
  sleep 2
done
if [ "$webview_ready" != "true" ]; then
  echo "WebView page load or decoded JavaScript probe did not complete"
  exit 1
fi

capture_diagnostics
python3 - "$ARTIFACT_DIR/logcat.txt" "$ARTIFACT_DIR/logcat-bounded.txt" "$APP_PID" "$ARTIFACT_DIR/probe.json" <<'PY'
import json
import re
import sys
from pathlib import Path

full_log = Path(sys.argv[1]).read_text(errors="replace")
pid = sys.argv[3]
probe_path = Path(sys.argv[4])
summary = Path(__import__("os").environ["GITHUB_STEP_SUMMARY"]) if __import__("os").environ.get("GITHUB_STEP_SUMMARY") else None

def fail(message):
    print(f"FAIL: {message}")
    if summary:
        with summary.open("a", encoding="utf-8") as stream:
            stream.write(f"- **FAIL**: {message}\n")
    raise SystemExit(1)

# Android logcat brief format includes the emitting process PID.
pid_marker = re.compile(rf"\(\s*{re.escape(pid)}\)\s*:")
records = []
page_finished = False
for line in full_log.splitlines():
    if not pid_marker.search(line):
        continue
    if "WEBVIEW_PAGE_FINISHED" in line and "https://appassets.androidplatform.net/assets/www/index.html" in line:
        page_finished = True
    marker = "WEBVIEW_JS_PROBE_JSON "
    if marker in line:
        records.append((line, line.split(marker, 1)[1]))

if not page_finished:
    fail("expected packaged-document WEBVIEW_PAGE_FINISHED evidence missing for app PID")
if len(records) != 1:
    fail(f"expected exactly one decoded probe record for app PID; observed {len(records)}")

original_line, raw_json = records[0]
try:
    payload = json.loads(raw_json)
except Exception as error:
    fail(f"decoded probe payload is not valid JSON ({type(error).__name__})")

expected = {"schemaVersion", "readyState", "title", "rootPresent", "rootTextLength"}
if not isinstance(payload, dict) or set(payload) != expected:
    fail("probe object keys do not exactly match the version-1 schema")
if type(payload["schemaVersion"]) is not int or payload["schemaVersion"] != 1:
    fail("schemaVersion must be integer 1")
if payload["readyState"] != "complete" or type(payload["readyState"]) is not str:
    fail('readyState must be the string "complete"')
if type(payload["title"]) is not str:
    fail("title must be a string")
if type(payload["rootPresent"]) is not bool or payload["rootPresent"] is not True:
    fail("rootPresent must be boolean true")
if type(payload["rootTextLength"]) is not int or payload["rootTextLength"] <= 0:
    fail("rootTextLength must be a positive integer")

for forbidden, label in (
    ("WEBVIEW_MAIN_FRAME_ERROR", "main-frame load error"),
    ("WEBVIEW_RENDERER_GONE", "WebView renderer loss"),
    ("FATAL EXCEPTION", "fatal Android exception"),
    ("WEBVIEW_CSP_VIOLATION", "Content Security Policy violation"),
):
    if forbidden in full_log:
        fail(f"{label} detected during smoke window")
for line in full_log.splitlines():
    if pid in line and (
        "has died" in line or "am_proc_died" in line or "Process died" in line
    ):
        fail("app process-death event detected during smoke window")

# Persist and summarize the exact JSON text emitted by native code, without re-serialization.
probe_path.write_text(raw_json + "\n", encoding="utf-8")
print("PASS: WEBVIEW_PAGE_FINISHED for the packaged document")
print(f"PASS: exactly one decoded probe record from app PID {pid}")
print(f"WEBVIEW_JS_PROBE_JSON {raw_json}")
for check in (
    "schemaVersion == 1",
    'readyState == "complete"',
    "rootPresent == true",
    "rootTextLength is a positive integer",
    "no main-frame error, renderer loss, or FATAL EXCEPTION",
    "no Content Security Policy violation",
):
    print(f"PASS: {check}")
if summary:
    with summary.open("a", encoding="utf-8") as stream:
        stream.write("## Android WebView runtime probe\n\n")
        stream.write(f"- App PID: `{pid}`\n")
        stream.write("- PASS: exactly one decoded probe record from the current app process\n")
        stream.write(f"- Exact decoded payload: `WEBVIEW_JS_PROBE_JSON {raw_json}`\n")
        stream.write("- PASS: schemaVersion=1; readyState=complete; rootPresent=true; rootTextLength is a positive integer\n")
        stream.write("- PASS: no main-frame error, renderer loss, or fatal exception in the smoke window\n")
PY

CURRENT_PID="$(adb_cmd shell pidof "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
if [ "$CURRENT_PID" != "$APP_PID" ]; then
  echo "FAIL: app process identity changed or process died (before=$APP_PID after=$CURRENT_PID)"
  exit 1
fi
echo "PASS: app process remained alive with PID $APP_PID"
echo "CAPACITOR_BRIDGE: NOT PRESENT — this app uses Android WebView directly"
echo "NATIVE_PLUGINS: NOT REGISTERED — no Capacitor plugin runtime/dependencies are configured"
echo "PASS: APK installed and $ACTIVITY reached resumed foreground state on $DEVICE"
