#!/usr/bin/env python3
"""Fail CI if the resolved Gradle SBOMs regress to known vulnerable versions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_BUILD_TOOL = {
    ("com.google.guava", "guava"): "33.7.2-jre",
    ("org.apache.commons", "commons-lang3"): "3.18.0",
    ("org.bitbucket.b_c", "jose4j"): "0.9.6",
    ("org.bouncycastle", "bcpkix-jdk18on"): "1.85",
    ("org.bouncycastle", "bcprov-jdk18on"): "1.85",
    ("org.jdom", "jdom2"): "2.0.6.1",
    ("org.jetbrains.kotlin", "kotlin-gradle-plugin"): "2.4.21",
    ("org.apache.httpcomponents", "httpclient"): "4.5.14",
}

KNOWN_VULNERABLE = {
    ("com.google.guava", "guava", "33.4.0-jre"),
    ("org.apache.commons", "commons-lang3", "3.16.0"),
    ("org.bitbucket.b_c", "jose4j", "0.9.5"),
    ("org.bouncycastle", "bcpkix-jdk18on", "1.79"),
    ("org.bouncycastle", "bcprov-jdk18on", "1.79"),
    ("org.jdom", "jdom2", "2.0.6"),
    ("org.jetbrains.kotlin", "kotlin-gradle-plugin", "2.2.10"),
}


def load_bom(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"Missing SBOM: {path}")
    bom = json.loads(path.read_text(encoding="utf-8"))
    if bom.get("bomFormat") != "CycloneDX" or bom.get("specVersion") != "1.5":
        raise SystemExit(f"Invalid CycloneDX 1.5 SBOM: {path}")
    components = bom.get("components")
    if not isinstance(components, list) or not components:
        raise SystemExit(f"SBOM has no components: {path}")
    purls = [c.get("purl") for c in components]
    if any(not p for p in purls) or len(purls) != len(set(purls)):
        raise SystemExit(f"SBOM has missing or duplicate package URLs: {path}")
    return bom


def index_components(bom: dict) -> dict[tuple[str, str], str]:
    result = {}
    for component in bom["components"]:
        key = (component.get("group", ""), component.get("name", ""))
        version = component.get("version", "")
        if key in result and result[key] != version:
            raise SystemExit(f"Multiple selected versions for {key}: {result[key]} and {version}")
        result[key] = version
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    root = parser.parse_args().root

    names = {
        "build-tool": "gradle-build-tool.cdx.json",
        "compile": "android-compile.cdx.json",
        "runtime": "android-runtime.cdx.json",
        "test": "android-test.cdx.json",
    }
    boms = {scope: load_bom(root / filename) for scope, filename in names.items()}
    build = index_components(boms["build-tool"])

    for coordinate, expected in EXPECTED_BUILD_TOOL.items():
        actual = build.get(coordinate)
        if actual != expected:
            raise SystemExit(f"Build-tool pin mismatch for {coordinate}: expected {expected}, found {actual}")

    all_components = []
    for bom in boms.values():
        all_components.extend(
            (c.get("group", ""), c.get("name", ""), c.get("version", ""))
            for c in bom["components"]
        )
    regressions = sorted(KNOWN_VULNERABLE.intersection(all_components))
    if regressions:
        raise SystemExit(f"Known vulnerable dependency versions remain in resolved SBOMs: {regressions}")

    if any(group == "io.netty" for group, _, _ in all_components):
        raise SystemExit("Unexpected Netty components remain after disabling optional Develocity CI injection")

    print("PASS: four categorized CycloneDX SBOMs validated")
    print("PASS: all seven build-tool remediation pins and patched HttpClient version are selected")
    print("PASS: no known vulnerable versions or injected Netty components remain")


if __name__ == "__main__":
    main()
