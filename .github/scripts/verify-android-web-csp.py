#!/usr/bin/env python3
"""Verify the packaged SPA's restrictive WebView CSP before Android packaging."""
from html.parser import HTMLParser
from pathlib import Path
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
    if parts:
        directives[parts[0].lower()] = parts[1:]

required = {
    "default-src": ["'none'"],
    "base-uri": ["'none'"],
    "object-src": ["'none'"],
    "frame-src": ["'none'"],
    "child-src": ["'none'"],
    "form-action": ["'self'"],
    "script-src": ["'self'"],
    "script-src-attr": ["'none'"],
    "style-src": ["'self'"],
    "style-src-attr": ["'none'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'"],
    "media-src": ["'self'"],
    "connect-src": ["'self'"],
    "worker-src": ["'self'"],
    "manifest-src": ["'self'"],
}
for name, expected in required.items():
    if directives.get(name) != expected:
        raise SystemExit(f"FAIL: CSP directive {name} expected {expected}, got {directives.get(name)}")
for name, sources in directives.items():
    if "*" in sources or "'unsafe-inline'" in sources or "'unsafe-eval'" in sources:
        raise SystemExit(f"FAIL: unsafe CSP source in {name}: {sources}")
print("PASS: exactly one CSP policy is present in packaged index.html")
for name in required:
    print(f"PASS: CSP {name} = {' '.join(required[name])}")
print("PASS: no wildcard, unsafe-inline, or unsafe-eval source")
