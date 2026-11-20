#!/usr/bin/env python3
"""Convert Gradle's resolved dependency report into a minimal CycloneDX 1.5 SBOM.

Gradle verification-metadata.xml is an integrity/checksum inventory, not a
resolved dependency lockfile. This parser uses the selected versions printed
by Gradle's dependency reports (including conflict-resolution arrows).
"""
from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path
from urllib.parse import quote

COORDINATE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+):(?P<name>[A-Za-z0-9_.-]+):"
    r"(?P<requested>[^\s()]+)(?:\s+->\s+(?P<selected>[^\s()]+))?"
)


def read_components(paths: list[Path]) -> dict[str, dict[str, str]]:
    components: dict[str, dict[str, str]] = {}
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"Missing Gradle dependency report: {path}")
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            # Constraints are not resolved artifacts. Their selected artifact
            # appears elsewhere in the dependency tree.
            if "(c)" in line or "FAILED" in line:
                continue
            match = COORDINATE.search(line)
            if not match:
                continue
            group = match.group("group")
            name = match.group("name")
            version = match.group("selected") or match.group("requested")
            if version in {"unspecified", "project"} or version.startswith("{"):
                continue
            purl = (
                "pkg:maven/"
                + quote(group, safe=".-_")
                + "/"
                + quote(name, safe=".-_")
                + "@"
                + quote(version, safe=".+-_")
            )
            components[purl] = {
                "type": "library",
                "bom-ref": purl,
                "group": group,
                "name": name,
                "version": version,
                "purl": purl,
            }
    return components


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, help="Gradle dependency report; repeatable")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    paths = [Path(p) for p in args.input]
    components = read_components(paths)
    if not components:
        raise SystemExit("No resolved Maven coordinates were extracted; refusing to emit an empty SBOM")
    ordered = [components[k] for k in sorted(components)]
    serial = uuid.uuid5(uuid.NAMESPACE_URL, "|".join(sorted(components)))
    bom = {
        "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "properties": [
                {"name": "gradle.report", "value": str(p)}
                for p in paths
            ]
        },
        "components": ordered,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bom, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}: {len(ordered)} resolved components from {len(paths)} report(s)")


if __name__ == "__main__":
    main()
