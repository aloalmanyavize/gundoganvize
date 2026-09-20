#!/usr/bin/env python3
"""Gündoğan Vize: reviewed evergreen guides and sourced news, no fabricated updates."""
import argparse
import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://gundoganvize.com"
START = "<!-- GVN_EDITORIAL_START -->"
END = "<!-- GVN_EDITORIAL_END -->"
OFFICIAL = ("home-affairs.ec.europa.eu", "eeas.europa.eu", "travel-europe.europa.eu")


def esc(value):
    return html.escape(str(value), quote=True)


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(items, news=False):
    seen = set()
    for item in items:
        slug = item["slug"]
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), slug
        assert slug not in seen, slug
        seen.add(slug)
        assert item.get("approved") is True or news, slug
        assert len(item["title"]) >= 26 and len(item["description"]) >= 55, slug
        assert len(item["sections"]) >= 3, slug
        assert urlparse(item["source"]).hostname in OFFICIAL, slug
        if news:
            assert date.fromisoformat(item["source_date"]) <= date.today(), slug
        for section in item["sections"]:
            assert len(section["text"]) > 80, slug


def article(item, pubdate, is_news):
    kind = "haberler" if is_news else "blog"
    url = BASE + "/" + kind + "/" + item["slug"] + "/"
    desc = item["description"]
    title = item["title"]
    source_date = ("Kaynak duyurusu: " + item["source_date"] + " · ") if is_news else ""
    source_label = "AB resmî açıklaması" if is_news else "Avrupa Komisyonu başvuru rehberi"
    schema = {
        "@context": "https://schema.org", "@type": "NewsArticle" if is_news else "BlogPosting",
        "headline": title, "description": desc, "mainEntityOfPage": url,
        "datePublished": pubdate, "dateModified": pubdate,
        "inLanguage": "tr-TR", "image": [BASE + item["image"]],
        "author": {"@type": "Organization", "name": "Gündoğan Vize"},
        "publisher": {"@type": "Organization", "name": "Gündoğan Vize", "url": BASE},
        "isBasedOn": item["source"]
    }
    blocks = "".join(
        "<section class='gvArticleBlock'><h2>" + esc(s["heading"]) + "</h2><p>" +
        esc(s["text"]) + "</p></section>" for s in item["sections"]
    )
    return ("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#082b58">"""
    + "<title>" + esc(title) + " | Gündoğan Vize</title>"
    + '<meta name="description" content="' + esc(desc) + '">'
    + '<link rel="canonical" href="' + esc(url) + '">'
    + '<meta property="og:type" content="article"><meta property="og:title" content="' + esc(title) + '">'
    + '<meta property="og:description" content="' + esc(desc) + '">'
    + '<meta property="og:image" content="' + BASE + item["image"] + '">'
    + '<meta property="og:url" content="' + esc(url) + '">'
    + '<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/editorial/editorial.css">'
    + '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
    + '</head><body><header><div class="wrap head"><a class="logo" href="/">GÜNDOĞAN VİZE<small>SCHENGEN VİZE DANIŞMANLIĞI</small></a>'
    + '<nav><a href="/ulkeler/">Ülkeler</a><a href="/gerekli-evraklar/">Gerekli Evraklar</a><a href="/blog/">Blog</a><a href="/haberler/">Haberler</a></nav>'
    + '<div class="headActions"><a class="miniPhone" href="tel:+903129112423">0312 911 24 23</a></div></div></header><main>'
    + '<section class="gvArticleHero"><div class="wrap"><p class="gvKicker">' + ("RESMÎ KAYNAKLI VİZE GELİŞMESİ" if is_news else "GÜNDOĞAN VİZE • BAŞVURU REHBERİ") + '</p>'
    + '<h1>' + esc(title) + '</h1><p class="gvLead">' + esc(desc) + '</p><p class="gvMeta">' + source_date + 'Gündoğan Vize yayını: ' + esc(pubdate) + '</p>'
    + '<img src="' + esc(item["image"]) + '" width="1120" height="560" alt="' + esc(title) + ' için bilgilendirici vize illüstrasyonu" fetchpriority="high"></div></section>'
    + '<article class="gvArticleBody wrap">' + blocks
    + '<section class="gvSource"><h2>Resmî kaynak ve kapsam</h2><p>Bu içerik bilgilendirme amaçlıdır. Kurallar ve yerel uygulamalar değişebilir; başvurudan önce ilgili temsilciliğin güncel listesini doğrulayın.</p>'
    + '<p><a href="' + esc(item["source"]) + '" target="_blank" rel="noopener noreferrer">' + source_label + ' →</a></p></section>'
    + '<div class="gvArticleCta"><h2>Başvuru dosyanızı birlikte planlayın</h2><p>Bağımsız danışmanlık sunuyoruz. Randevu kontenjanı ve vize kararı yetkili kurumlara aittir.</p>'
    + '<a class="btn" href="/randevu-talebi/">Randevu talebi oluştur</a> <a class="ghostBtn" href="/gerekli-evraklar/">Evrakları incele</a></div></article>'
    + '</main><footer><div class="wrap foot"><div><b>GÜNDOĞAN VİZE</b><p>Ankara merkezli bağımsız vize danışmanlığı.</p></div><div><a href="/">Ana sayfa</a><br><a href="/blog/">Blog</a><br><a href="/haberler/">Haberler</a></div></div></footer></body></html>\n')


def collect(items, category):
    result = []
    for item in items:
        path = ROOT / category / item["slug"] / "index.html"
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            m = re.search(r"Gündoğan Vize yayını: ([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
            result.append((m.group(1) if m else "2026-09-20", category, item))
    result.sort(key=lambda row: (row[0], row[2]["slug"]), reverse=True)
    return result


def cards(rows):
    return "".join(
        '<a class="gvStory" href="/' + category + '/' + esc(item["slug"]) + '/">'
        + '<img src="' + esc(item["image"]) + '" loading="lazy" width="720" height="360" alt="' + esc(item["title"]) + ' için editoryal illüstrasyon">'
        + '<div><span class="gvStoryType">' + ("HABER • RESMÎ KAYNAK" if category == "haberler" else "REHBER • DOSYA HAZIRLIĞI")
        + '</span><h3>' + esc(item["title"]) + '</h3><p>' + esc(item["description"]) + '</p>'
        + '<small>Yayın: ' + pub + ((" · Kaynak: " + item["source_date"]) if category == "haberler" else "") + '</small></div></a>'
        for pub, category, item in rows)


def sync_index(path, title, rows, all_href):
    target = ROOT / path
    content = target.read_text(encoding="utf-8")
    assert content.count(START) == 1 and content.count(END) == 1, path
    markup = (
        '<section class="section gvEditorial"><div class="wrap"><div class="gvEditorialHead"><div><span class="eyebrow">GÜNDOĞAN VİZE EDİTORYAL</span>'
        + '<h2>' + esc(title) + '</h2><p>Özgün rehberler ve resmî kaynağa dayanan gelişmeler. Yayın ile kaynak tarihi ayrı gösterilir.</p></div>'
        + '<a class="ghostBtn" href="' + all_href + '">Tüm içerikler →</a></div>'
        + '<div class="gvStories">' + cards(rows) + '</div></div></section>'
        if rows else ""
    )
    new = content[:content.index(START) + len(START)] + markup + content[content.index(END):]
    if new != content:
        target.write_text(new, encoding="utf-8")


def sitemap_update(posts):
    path = ROOT / "sitemap.xml"
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"<!-- GVN_SITEMAP_START -->.*?<!-- GVN_SITEMAP_END -->", "", content, flags=re.S)
    entries = "".join(
        "<url><loc>" + BASE + "/" + group + "/" + esc(item["slug"])
        + "/</loc><lastmod>" + pub + "</lastmod></url>\n"
        for pub, group, item in posts
    )
    content = content.replace("</urlset>", "<!-- GVN_SITEMAP_START -->\n" + entries + "<!-- GVN_SITEMAP_END -->\n</urlset>")
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--publish-one", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    blog = read_json("editorial/queue.json")
    news = read_json("editorial/news.json")
    validate(blog)
    validate(news, news=True)
    if args.check:
        for page in ("index.html", "blog/index.html", "haberler/index.html"):
            value = (ROOT / page).read_text(encoding="utf-8")
            assert START in value and END in value
        print("Editorial content, official sources, index markers: OK")
        return
    now = date.today().isoformat()
    amount = 3 if args.bootstrap else (1 if args.publish_one else 0)
    for item in blog:
        path = ROOT / "blog" / item["slug"] / "index.html"
        if not path.exists() and amount:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(article(item, now, False), encoding="utf-8")
            print("Published evergreen guide:", path)
            amount -= 1
    for item in news:
        path = ROOT / "haberler" / item["slug"] / "index.html"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(article(item, now, True), encoding="utf-8")
            print("Published sourced news:", path)
    blogs = collect(blog, "blog")
    articles = collect(news, "haberler")
    sync_index("index.html", "Yeni rehberler ve resmî kaynaklı gelişmeler", (blogs + articles)[:3], "/blog/")
    sync_index("blog/index.html", "Yeni yayımlanan vize rehberleri", blogs, "/ulkeler/")
    sync_index("haberler/index.html", "Resmî kaynağa dayanan haber dosyaları", articles, "/blog/")
    sitemap_update(blogs + articles)
    print("Published:", len(blogs), "guides and", len(articles), "news explainers")


if __name__ == "__main__":
    main()
