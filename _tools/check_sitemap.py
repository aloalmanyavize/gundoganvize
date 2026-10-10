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
    print(f"Sitemap verified: {len(urls)} unique, source-backed canonical URLs.")

if __name__ == "__main__":
    main()
