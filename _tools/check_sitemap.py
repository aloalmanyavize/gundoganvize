#!/usr/bin/env python3
"""Guard priority landing pages and published routes against sitemap regressions."""
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://gundoganvize.com"
LOC = "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"

def main():
    document = ET.parse(ROOT / "sitemap.xml")
    urls = [node.text for node in document.iter(LOC)]
    assert urls, "Sitemap is empty"
    assert len(urls) == len(set(urls)), "Duplicate URLs in sitemap"
    must_include = {
        BASE + "/",
        BASE + "/idata-ankara/",
        BASE + "/almanya-vizesi/",
        BASE + "/fransa-vizesi/",
        BASE + "/gerekli-evraklar/",
        BASE + "/randevu-talebi/",
    }
    missing = sorted(must_include - set(urls))
    assert not missing, f"Priority landing pages missing from sitemap: {missing}"
    assert len(urls) >= 60, f"Unexpectedly small sitemap: {len(urls)} URLs"
    for url in urls:
        p = urlsplit(url)
        assert p.scheme == "https" and p.netloc == "gundoganvize.com", f"Unexpected host: {url}"
        assert not p.query and not p.fragment, f"Noncanonical sitemap URL: {url}"
        assert p.path.endswith("/"), f"Missing trailing slash: {url}"
        page = ROOT / p.path.lstrip("/") / "index.html"
        assert page.is_file(), f"Sitemap URL has no source page: {url}"
    # Every public, indexable landing page must be represented.
    import re
    excluded = {"8d-wall-privacy", "node_modules", "dist"}
    expected = {BASE + "/"}
    for page in ROOT.rglob("index.html"):
        relative = page.relative_to(ROOT)
        if relative == Path("index.html"):
            continue
        if any(part.startswith((".", "_")) for part in relative.parts):
            continue
        if relative.parts[0] in excluded:
            continue
        html = page.read_text(encoding="utf-8")
        if re.search(r'<meta[^>]+name=["\\\']robots["\\\'][^>]+content=["\\\'][^"\\\']*noindex', html, re.I):
            continue
        expected.add(BASE + "/" + "/".join(relative.parts[:-1]) + "/")
    missing_pages = sorted(expected - set(urls))
    assert not missing_pages, f"Indexable pages missing from sitemap: {missing_pages}"
    print(f"Sitemap verified: {len(urls)} unique, source-backed canonical URLs.")

if __name__ == "__main__":
    main()
