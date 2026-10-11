#!/usr/bin/env python3
"""Static structural audit for Gündoğan Vize. Never claims to test live browser rendering."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"8d-wall-privacy", "node_modules", "dist"}
class Parse(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.images = []
        self.h1 = 0
    def handle_starttag(self, name, attrs):
        attributes = dict(attrs)
        if "id" in attributes and attributes["id"]:
            self.ids.add(attributes["id"])
        if name == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if name == "img":
            self.images.append(attributes)
        if name == "h1":
            self.h1 += 1

def resolve_local(value: str, page: Path) -> Path | None:
    if not value or value.startswith(("#", "//", "mailto:", "tel:", "javascript:", "data:")):
        return None
    url = urlsplit(value)
    if url.scheme in {"https", "http"}:
        if url.netloc not in {"gundoganvize.com", "www.gundoganvize.com"}:
            return None
        path = url.path
    elif url.scheme:
        return None
    else:
        path = url.path
    if not path:
        return None
    from posixpath import normpath
    if path.startswith("/"):
        relative = path.lstrip("/")
    else:
        relative = normpath(page.parent.relative_to(ROOT).as_posix() + "/" + path)
    relative = unquote(relative).lstrip("/")
    if not relative or relative == ".":
        return ROOT / "index.html"
    if relative.startswith("../") or ".." in Path(relative).parts:
        return ROOT / "__invalid__"
    candidate = ROOT / relative
    if candidate.is_dir() or path.endswith("/"):
        return candidate / "index.html"
    if not candidate.suffix:
        return candidate / "index.html"
    return candidate

def main() -> int:
    errors, warnings = [], []
    pages = sorted(
        p for p in ROOT.rglob("index.html")
        if not any(part.startswith(".") or part.startswith("_") for part in p.relative_to(ROOT).parts[:-1])
        and p.relative_to(ROOT).parts[0] not in EXCLUDED
    )
    for page in pages:
        s = page.read_text(encoding="utf-8")
        rel = page.relative_to(ROOT).as_posix()
        if not s.lstrip().lower().startswith("<!doctype html>"):
            errors.append(f"{rel}: HTML doctype missing")
        if re.search(r'<img\\b[^>]*<div\\b', s, re.I) or re.search(r'loading="lazy"\\s*<div', s):
            errors.append(f"{rel}: malformed image tag")
        if "https://gundoganvize.comhttps://" in s:
            errors.append(f"{rel}: malformed absolute image URL")
        doc = Parse()
        try:
            doc.feed(s)
            doc.close()
        except Exception as exc:
            errors.append(f"{rel}: HTML parsing error: {exc}")
            continue
        if doc.h1 != 1:
            errors.append(f"{rel}: expected one H1, found {doc.h1}")
        for href in doc.links:
            target = resolve_local(href, page)
            if target and not target.exists():
                errors.append(f"{rel}: broken internal href {href}")
            if href.startswith("#") and href[1:] and href[1:] not in doc.ids:
                warnings.append(f"{rel}: missing same-page anchor {href}")
        for img in doc.images:
            if not img.get("alt"):
                warnings.append(f"{rel}: image without descriptive alt")
            target = resolve_local(img.get("src", ""), page)
            if target and not target.exists():
                errors.append(f"{rel}: local image missing {img.get('src')}")
    blog = (ROOT / "blog/index.html").read_text(encoding="utf-8")
    news = (ROOT / "haberler/index.html").read_text(encoding="utf-8")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    countries = (ROOT / "ulkeler/index.html").read_text(encoding="utf-8")
    layout_checks = [
        ('blog archive grid', 'class="gvBlogArchive"' in blog and 'class="gvStories"' in blog),
        ('news archive grid', 'class="gvNewsArchive section"' in news and 'class="gvStories"' in news),
        ('country list count', len(re.findall(r'<a href="/[a-z-]+-vizesi/"', countries)) == 29),
        ('six services', len(re.findall(r'class="serviceCard"', home)) == 6),
        ('services anchor', 'id="hizmetler"' in home),
        ('styles repair import', "/site-repair.css" in (ROOT / "styles.css").read_text()),
    ]
    for label, good in layout_checks:
        if not good:
            errors.append("critical layout: " + label)
    for css_path in (ROOT / "styles.css",):
        css = css_path.read_text()
        for name in re.findall(r"@import\\s+url\\(['\\\"]?(/[^)'\\\"]+)", css):
            target = ROOT / name.lstrip("/").split("?")[0]
            if not target.exists():
                errors.append(f"missing imported CSS: {name}")
    print(f"Audited {len(pages)} public HTML pages; errors: {len(errors)}; warnings: {len(warnings)}")
    for item in errors[:80]:
        print("ERROR:", item)
    for item in warnings[:40]:
        print("WARNING:", item)
    if len(errors) > 80 or len(warnings) > 40:
        print("Remaining diagnostics omitted for brevity.")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
