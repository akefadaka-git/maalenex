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
    seen: set[tuple[str, str]] = set()
    for icon in icons:
        src = icon.get("src", "")
        if not src.startswith("/") or ".." in Path(src).parts:
            fail(f"unsafe or non-root-relative icon path: {src!r}")
        file_path = PUBLIC / src.lstrip("/")
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
    android_project_ready = (ROOT / "android/gradlew").is_file() and (
        (ROOT / "android/settings.gradle").is_file() or (ROOT / "android/settings.gradle.kts").is_file()
    ) and ((ROOT / "android/app/build.gradle").is_file() or (ROOT / "android/app/build.gradle.kts").is_file())
    print("PASS: PWA manifest references existing SVGs with matching intrinsic dimensions.")
    print("PASS: 512px maskable icon has full-bleed background and centered safe-zone artwork.")
    print("PASS: Android adaptive, round, foreground, background and monochrome XML resources parse and reference required layers.")
    if android_project_ready:
        print("INFO: Android Gradle project scaffold detected; run the Gradle resource task in CI.")
    else:
        print("SKIP: Android Gradle build/resource compilation — this repository currently contains resources only; no Gradle wrapper, settings file, app build file or AndroidManifest.xml.")
        print("SKIP: Density-specific legacy mipmap PNGs — minSdk and a buildable Android module are not defined; do not generate unreferenced binaries before the Android shell is scaffolded.")


if __name__ == "__main__":
    main()
