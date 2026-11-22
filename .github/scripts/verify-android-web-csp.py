#!/usr/bin/env python3
"""Verify the packaged SPA's restrictive WebView CSP before Android packaging."""
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
    "script-src": ["'self'", "https://maps.googleapis.com", "https://maps.gstatic.com"],
    "script-src-attr": ["'none'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "style-src-attr": ["'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https://*.googleapis.com", "https://*.gstatic.com", "https://*.google.com", "https://*.googleusercontent.com"],
    "font-src": ["'self'", "https://fonts.gstatic.com"],
    "media-src": ["'self'"],
    "worker-src": ["'self'", "blob:"],
    "manifest-src": ["'self'"],
}
for name, expected in required.items():
    if directives.get(name) != expected:
        raise SystemExit(f"FAIL: CSP directive {name} expected {expected}, got {directives.get(name)}")

connect_sources = directives.get("connect-src", [])
google_connect = ["https://*.googleapis.com", "https://*.google.com", "https://*.gstatic.com"]
if not connect_sources or connect_sources[0] != "'self'" or not all(source in connect_sources for source in google_connect):
    raise SystemExit(f"FAIL: connect-src must include self and the explicit Google Maps service domains: {connect_sources}")
api_sources = [source for source in connect_sources[1:] if source not in google_connect]
if len(api_sources) > 1:
    raise SystemExit(f"FAIL: at most one configured API origin is allowed: {api_sources}")
if api_sources:
    api_origin = urlsplit(api_sources[0])
    local_http = api_origin.scheme == "http" and api_origin.hostname in {"localhost", "127.0.0.1", "::1"}
    if not api_origin.netloc or (api_origin.scheme != "https" and not local_http):
        raise SystemExit(f"FAIL: API CSP origin must be HTTPS (HTTP only for localhost): {api_sources[0]}")
    if api_origin.username or api_origin.password or api_origin.path not in {"", "/"} or api_origin.query or api_origin.fragment:
        raise SystemExit(f"FAIL: API CSP entry must be an origin only: {connect_sources[1]}")

for name, sources in directives.items():
    if "'unsafe-eval'" in sources:
        raise SystemExit(f"FAIL: unsafe-eval is not permitted in {name}: {sources}")
    if "*" in sources:
        raise SystemExit(f"FAIL: unrestricted wildcard is not permitted in {name}: {sources}")
    if any("*." in source and source not in {
        "https://*.googleapis.com", "https://*.gstatic.com",
        "https://*.google.com", "https://*.googleusercontent.com",
    } for source in sources):
        raise SystemExit(f"FAIL: non-Google wildcard source in {name}: {sources}")
    if "'unsafe-inline'" in sources and name not in {"style-src", "style-src-attr"}:
        raise SystemExit(f"FAIL: unsafe-inline is only permitted for Google Maps generated styles: {name} {sources}")
print("PASS: exactly one CSP policy is present in packaged index.html")
for name, sources in directives.items():
    print(f"PASS: CSP {name} = {' '.join(sources)}")
print("PASS: no wildcard, unsafe-inline, or unsafe-eval source")
