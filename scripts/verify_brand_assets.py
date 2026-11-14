#!/usr/bin/env python3
"""Validate MaaleNex PWA and Android launcher icon resources without third-party packages."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "frontend/public"
RES = ROOT / "android/app/src/main/res"
ANDROID = "{http://schemas.android.com/apk/res/android}"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def svg_dimensions(path: Path) -> tuple[int, int]:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        fail(f"{path.relative_to(ROOT)} is not valid SVG/XML: {exc}")
    if not root.tag.endswith("svg"):
        fail(f"{path.relative_to(ROOT)} root element is not svg")
    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) != 4:
        fail(f"{path.relative_to(ROOT)} must declare a four-value viewBox")
    try:
        width = int(float(re.sub(r"[^0-9.].*$", "", root.attrib["width"])))
        height = int(float(re.sub(r"[^0-9.].*$", "", root.attrib["height"])))
    except (KeyError, ValueError):
        fail(f"{path.relative_to(ROOT)} must declare numeric width and height")
    return width, height


def main() -> None:
    manifest_path = PUBLIC / "site.webmanifest"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    icons = manifest.get("icons", [])
    if len(icons) < 2:
        fail("manifest must provide at least 192 and 512 PWA icons")
    # Validate every SVG shipped in the public asset tree, not only manifest icons.
    for svg_path in sorted(PUBLIC.rglob("*.svg")):
        width, height = svg_dimensions(svg_path)
        root = ET.parse(svg_path).getroot()
        view_box = [float(value) for value in root.attrib["viewBox"].replace(",", " ").split()]
        if width <= 0 or height <= 0 or view_box[2] <= 0 or view_box[3] <= 0:
            fail(f"{svg_path.relative_to(ROOT)} has non-positive dimensions")
        if abs((width / height) - (view_box[2] / view_box[3])) > 0.01:
            fail(f"{svg_path.relative_to(ROOT)} intrinsic dimensions do not match its viewBox aspect ratio")

    seen: set[tuple[str, str]] = set()
    for icon in icons:
        src = icon.get("src", "")
        relative_src = src.lstrip("/") if src.startswith("/") else src
        if Path(relative_src).is_absolute() or ".." in Path(relative_src).parts:
            fail(f"unsafe icon path: {src!r}")
        file_path = PUBLIC / relative_src
        if not file_path.is_file():
            fail(f"manifest icon does not exist: {src}")
        if icon.get("type") != "image/svg+xml":
            fail(f"{src} has an incorrect manifest MIME type")
        expected = {"192x192": (192, 192), "512x512": (512, 512)}.get(icon.get("sizes"))
        if expected is None:
            fail(f"unexpected PWA icon size declaration: {icon.get('sizes')!r}")
        actual = svg_dimensions(file_path)
        if actual != expected:
            fail(f"{src} declares {expected}, SVG intrinsic dimensions are {actual}")
        seen.add((icon["sizes"], icon.get("purpose", "any")))
    if ("192x192", "any") not in seen:
        fail("manifest must provide a 192x192 any-purpose icon")
    if ("512x512", "maskable") not in seen:
        fail("manifest must provide a 512x512 maskable icon")

    maskable = ET.parse(PUBLIC / "pwa-512.svg").getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    background = maskable.find("svg:rect", ns)
    if background is None or any(background.attrib.get(k) != v for k, v in {
        "x": "0", "y": "0", "width": "256", "height": "256"
    }.items()):
        fail("maskable PWA icon must have a full-bleed 256x256 background")
    foreground_group = maskable.find("svg:g", ns)
    if foreground_group is None or foreground_group.attrib.get("transform") != "translate(128 128) scale(0.72) translate(-128 -128)":
        fail("maskable PWA foreground must use the centered 0.72 safe-zone scale")

    adaptive_paths = [
        RES / "mipmap-anydpi-v26/ic_launcher.xml",
        RES / "mipmap-anydpi-v26/ic_launcher_round.xml",
    ]
    for path in adaptive_paths:
        if not path.is_file():
            fail(f"missing adaptive icon definition: {path.relative_to(ROOT)}")
        root = ET.parse(path).getroot()
        if not root.tag.endswith("adaptive-icon"):
            fail(f"{path.relative_to(ROOT)} is not an adaptive-icon resource")
        required = {"background", "foreground", "monochrome"}
        present = {child.tag.rsplit("}", 1)[-1] for child in root}
        if not required.issubset(present):
            fail(f"{path.relative_to(ROOT)} missing layers: {sorted(required - present)}")
        refs = {child.attrib.get(ANDROID + "drawable", "") for child in root}
        expected_refs = {"@color/ic_launcher_background", "@drawable/ic_launcher_foreground", "@drawable/ic_launcher_monochrome"}
        if not expected_refs.issubset(refs):
            fail(f"{path.relative_to(ROOT)} has incorrect or missing resource references")

    for filename in ("ic_launcher_foreground.xml", "ic_launcher_monochrome.xml"):
        path = RES / "drawable" / filename
        root = ET.parse(path).getroot()
        if not root.tag.endswith("vector"):
            fail(f"{path.relative_to(ROOT)} is not a vector drawable")
        if root.attrib.get(ANDROID + "width") != "108dp" or root.attrib.get(ANDROID + "height") != "108dp":
            fail(f"{path.relative_to(ROOT)} must use 108dp x 108dp adaptive canvas")
        group = root.find("group")
        if group is None or group.attrib.get(ANDROID + "pivotX") != "54" or group.attrib.get(ANDROID + "pivotY") != "54":
            fail(f"{path.relative_to(ROOT)} has no group centered on the 54dp canvas midpoint")
        if float(group.attrib.get(ANDROID + "scaleX", "1")) > 1 or float(group.attrib.get(ANDROID + "scaleY", "1")) > 1:
            fail(f"{path.relative_to(ROOT)} artwork exceeds the 108dp adaptive canvas")

    bg = RES / "values/ic_launcher_background.xml"
    ET.parse(bg)
    manifest_path = ROOT / "android/app/src/main/AndroidManifest.xml"
    gradle_path = ROOT / "android/app/build.gradle.kts"
    if not manifest_path.is_file() or not gradle_path.is_file():
        fail("Android application manifest or Gradle module is missing")
    android_manifest = ET.parse(manifest_path).getroot()
    app = android_manifest.find("application")
    if app is None or app.attrib.get(ANDROID + "icon") != "@mipmap/ic_launcher" or app.attrib.get(ANDROID + "roundIcon") != "@mipmap/ic_launcher_round":
        fail("Android manifest must register standard and round launcher resources")
    gradle_text = gradle_path.read_text(encoding="utf-8")
    if 'applicationId = "com.maalenex.moto"' not in gradle_text or "minSdk = 23" not in gradle_text:
        fail("Android application ID or minimum SDK differs from the verified contract")
    for fallback in ("mipmap-anydpi/ic_launcher.xml", "mipmap-anydpi/ic_launcher_round.xml"):
        fallback_path = RES / fallback
        fallback_root = ET.parse(fallback_path).getroot()
        if not fallback_root.tag.endswith("vector"):
            fail(f"{fallback} must be a vector fallback for API 23–25")
    activity_path = ROOT / "android/app/src/main/java/com/maalenex/moto/MainActivity.kt"
    if not activity_path.is_file():
        fail("Native Android MainActivity is missing")
    activity_text = activity_path.read_text(encoding="utf-8")
    if "settings.allowFileAccess = false" not in activity_text or "settings.allowContentAccess = false" not in activity_text:
        fail("Android WebView must disable file and content URL access")
    if "addJavascriptInterface" in activity_text:
        fail("Android WebView must not expose a JavaScript bridge")
    if "shouldOverrideUrlLoading" not in activity_text or "APP_ASSET_HOST" not in activity_text:
        fail("Android WebView must restrict top-level navigation to the local asset origin")
    permissions = android_manifest.findall("uses-permission")
    if any(p.attrib.get(ANDROID + "name") == "android.permission.INTERNET" for p in permissions):
        fail("Offline packaged shell must not request INTERNET permission before a reviewed API integration")
    for strings_file in ("values/strings.xml", "values-am/strings.xml"):
        if not (RES / strings_file).is_file():
            fail(f"Missing localized app label resource: {strings_file}")
    android_project_ready = (ROOT / "android/settings.gradle.kts").is_file() and (ROOT / "android/app/build.gradle.kts").is_file()
    print("PASS: PWA manifest references existing SVGs with matching intrinsic dimensions.")
    print("PASS: 512px maskable icon has full-bleed background and centered safe-zone artwork.")
    print("PASS: Android adaptive, round, foreground, background and monochrome XML resources parse and reference required layers.")
    if android_project_ready:
        print("PASS: Android application ID, minSdk 23, manifest icon registration, native activity and Gradle module are present.")
        print("PASS: API 23–25 use scalable anydpi vector launcher fallbacks; API 26+ use adaptive icons; Android 13+ receives monochrome layer.")
        print("INFO: Density-specific PNG fallbacks are not required for the selected API 23+ range because vector drawables are supported.")
    else:
        fail("Android Gradle project scaffold is incomplete")


if __name__ == "__main__":
    main()
