#!/usr/bin/env python3
"""Verify the packaged SPA CSP for the keyless MapLibre/OpenFreeMap runtime."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import sys


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.policies = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "meta":
            return
        values = dict(attrs)
        if values.get("http-equiv", "").lower() == "content-security-policy":
            self.policies.append(values.get("content", ""))


path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(f"FAIL: built HTML missing: {path}")
parser = MetaParser()
parser.feed(path.read_text(encoding="utf-8"))
if len(parser.policies) != 1:
    raise SystemExit(f"FAIL: expected exactly one CSP meta element; found {len(parser.policies)}")

directives = {}
for item in parser.policies[0].split(";"):
    parts = item.strip().split()
    if not parts:
        continue
    name = parts[0].lower()
    if name in directives:
        raise SystemExit(f"FAIL: duplicate CSP directive: {name}")
    directives[name] = parts[1:]
if not directives:
    raise SystemExit("FAIL: CSP policy is empty")

required = {
    "default-src": ["'none'"],
    "base-uri": ["'none'"],
    "object-src": ["'none'"],
    "frame-src": ["'none'"],
    "child-src": ["'none'"],
    "form-action": ["'self'"],
    "script-src": ["'self'", "https://unpkg.com"],
    "script-src-attr": ["'none'"],
    "style-src": ["'self'"],
    "style-src-elem": ["'self'", "https://unpkg.com"],
    "style-src-attr": ["'none'"],
    "img-src": ["'self'", "data:", "blob:"],
    "font-src": ["'self'"],
    "media-src": ["'self'"],
    "worker-src": ["'self'", "blob:"],
    "manifest-src": ["'self'"],
}
for name, expected in required.items():
    if directives.get(name) != expected:
        raise SystemExit(f"FAIL: CSP directive {name} expected {expected}, got {directives.get(name)}")

connect_sources = directives.get("connect-src", [])
if not connect_sources or connect_sources[0] != "'self'":
    raise SystemExit(f"FAIL: connect-src must begin with self: {connect_sources}")
if connect_sources.count("https://tiles.openfreemap.org") != 1:
    raise SystemExit(f"FAIL: connect-src must allow the exact OpenFreeMap tile origin: {connect_sources}")
if connect_sources.count("https://unpkg.com") != 1:
    raise SystemExit(f"FAIL: connect-src must allow UNPKG for MapLibre's cross-origin worker fetch: {connect_sources}")
api_sources = [source for source in connect_sources[1:] if source not in {"https://tiles.openfreemap.org", "https://unpkg.com"}]
if len(api_sources) > 1:
    raise SystemExit(f"FAIL: at most one configured API origin is allowed: {api_sources}")
if api_sources:
    api_origin = urlsplit(api_sources[0])
    local_http = api_origin.scheme == "http" and api_origin.hostname in {"localhost", "127.0.0.1", "::1"}
    if not api_origin.netloc or (api_origin.scheme != "https" and not local_http):
        raise SystemExit(f"FAIL: API CSP origin must be HTTPS (HTTP only for localhost): {api_sources[0]}")
    if api_origin.username or api_origin.password or api_origin.path not in {"", "/"} or api_origin.query or api_origin.fragment:
        raise SystemExit(f"FAIL: API CSP entry must be an origin only: {api_sources[0]}")

for name, sources in directives.items():
    if "*" in sources or any("*." in source for source in sources):
        raise SystemExit(f"FAIL: wildcard source is not permitted in {name}: {sources}")
    if "'unsafe-eval'" in sources or "'unsafe-inline'" in sources:
        raise SystemExit(f"FAIL: unsafe script/style execution is not permitted in {name}: {sources}")
    if name not in required and name != "connect-src":
        raise SystemExit(f"FAIL: unexpected CSP directive {name}: {sources}")

print("PASS: exactly one restrictive CSP policy is present in packaged index.html")
for name, sources in directives.items():
    print(f"PASS: CSP {name} = {' '.join(sources)}")
print("PASS: only the pinned MapLibre CDN and exact OpenFreeMap tile origin are permitted")
print("PASS: UNPKG is allowed in connect-src only for the pinned MapLibre worker fetch")
print("PASS: no Google Maps, wildcard hosts, unsafe-inline or unsafe-eval source is permitted")
