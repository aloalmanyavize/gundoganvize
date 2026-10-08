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
OFFICIAL = ("home-affairs.ec.europa.eu", "eeas.europa.eu", "travel-europe.europa.eu", "idata.com.tr", "www.idata.com.tr")


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
        image = item.get("image", "")
        assert image.startswith("https://images.unsplash.com/photo-") or image.startswith("/assets/editorial/"), (slug, image)
        if news:
            assert date.fromisoformat(item["source_date"]) <= date.today(), slug
        for section in item["sections"]:
            assert len(section["text"]) > 80, slug


def editorial_image_url(item):
    """Use each approved article's image; supports local assets and HTTPS photos."""
    image = item["image"]
    return image if image.startswith("https://") else BASE + image


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
        "inLanguage": "tr-TR", "image": [editorial_image_url(item)],
        "author": {"@type": "Organization", "name": "Gündoğan Vize"},
        "publisher": {"@type": "Organization", "name": "Gündoğan Vize", "logo": {"@type": "ImageObject", "url": BASE + "/assets/logo.svg"}},
    }
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Ana Sayfa","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":"Haberler" if is_news else "Blog","item":BASE+"/"+kind+"/"},
        {"@type":"ListItem","position":3,"name":title,"item":url}]}
    image_url = editorial_image_url(item)
    sections = "".join(f'<section><h2>{esc(s["heading"])}</h2><p>{esc(s["text"])}</p></section>' for s in item["sections"])
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Gündoğan Vize</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{url}"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/editorial/editorial.css?v=20261008-topic-photos"><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script><script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script></head><body><header><div class="wrap head"><a class="logo" href="/">GÜNDOĞAN VİZE<small>SCHENGEN VİZE DANIŞMANLIĞI</small></a><nav><a href="/ulkeler/">Ülkeler</a><a href="/gerekli-evraklar/">Gerekli Evraklar</a><a href="/randevu-talebi/">Randevu Talebi</a><a href="/blog/">Blog</a><a href="/haberler/">Haberler</a></nav></div></header><main><section class="section"><div class="wrap visaContent"><article><span class="eyebrow">GÜNDOĞAN VİZE · {esc(pubdate)}</span><h1>{esc(title)}</h1><p class="lead">{esc(desc)}</p><figure class="gvArticlePhoto"><img src="{esc(image_url)}" width="1200" height="675" loading="eager" decoding="async" alt="{esc(title)}"><figcaption>Konuyla ilgili temsili fotoğraf</figcaption></figure>{sections}<div class="notice">{esc(source_date)}Kaynak: <a href="{esc(item['source'])}" target="_blank" rel="noopener">{source_label}</a>. Resmî prosedürler değişebilir; başvuru öncesinde ilgili dış temsilcilik ve yetkili başvuru merkezinin güncel sayfasını kontrol edin.</div></article></div></section></main></body></html>'''


def replace_editorial(path, cards):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    assert START in text and END in text, path
    block = START + "\n" + cards + "\n" + END
    p.write_text(text[:text.index(START)] + block + text[text.index(END)+len(END):], encoding="utf-8")


def card(item, kind):
    return f'<article class="gvStory"><img src="{esc(item["image"])}" alt="{esc(item["title"])}" loading="lazy"><div><span>{"HABER" if kind=="haberler" else "REHBER"}</span><h3><a href="/{kind}/{esc(item["slug"])}/">{esc(item["title"])}</a></h3><p>{esc(item["description"])}</p></div></article>'


def publish_one(items, pubdate):
    for item in sorted(items, key=lambda x: x.get("priority", 99)):
        out = ROOT / "blog" / item["slug"] / "index.html"
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(article(item, pubdate, False), encoding="utf-8")
            return item
    return None


def write_news(items, pubdate):
    for item in items:
        out = ROOT / "haberler" / item["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists():
            out.write_text(article(item, pubdate, True), encoding="utf-8")


def refresh_indices(blog, news):
    blog_cards = "\n".join(card(x, "blog") for x in sorted(blog, key=lambda x: x.get("priority", 99))[:12])
    news_cards = "\n".join(card(x, "haberler") for x in reversed(news[-6:]))
    replace_editorial("blog/index.html", blog_cards)
    replace_editorial("haberler/index.html", news_cards)
    replace_editorial("index.html", news_cards + "\n" + blog_cards[:12000])


def refresh_sitemap():
    urls = [BASE + "/"]
    for root in ("blog", "haberler"):
        for p in sorted((ROOT / root).glob("*/index.html")):
            urls.append(BASE + "/" + root + "/" + p.parent.name + "/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f'<url><loc>{u}</loc></url>' for u in urls) + '\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--bootstrap", action="store_true")
    ap.add_argument("--publish-one", action="store_true")
    args = ap.parse_args()
    blog = read_json("editorial/queue.json")
    news = read_json("editorial/news.json")
    validate(blog)
    validate(news, True)
    if args.check and not (args.bootstrap or args.publish_one):
        return
    pubdate = date.today().isoformat()
    write_news(news, pubdate)
    if args.bootstrap:
        for _ in range(min(4, len(blog))): publish_one(blog, pubdate)
    elif args.publish_one:
        publish_one(blog, pubdate)
    refresh_indices(blog, news)
    refresh_sitemap()


if __name__ == "__main__":
    main()
