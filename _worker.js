const SITE_HOST = "gundoganvize.com";
const SITE_ORIGIN = `https://${SITE_HOST}`;

function cleanPath(pathname) {
  let path = pathname || "/";
  path = path.replace(/\/index\.html$/i, "/");
  path = path.replace(/\/{2,}/g, "/");
  if (!path.startsWith("/")) path = `/${path}`;
  const last = path.split("/").pop() || "";
  const looksLikeFile = last.includes(".");
  if (path !== "/" && !looksLikeFile && !path.endsWith("/")) path += "/";
  return path || "/";
}

function canonicalUrl(url) {
  return `${SITE_ORIGIN}${cleanPath(url.pathname)}`;
}

function replaceCanonical(html, canonical) {
  const tag = `<link rel="canonical" href="${canonical}">`;
  if (/<link\s+[^>]*rel=["']canonical["'][^>]*>/i.test(html)) {
    return html.replace(/<link\s+[^>]*rel=["']canonical["'][^>]*>/i, tag);
  }
  return html.replace(/<head([^>]*)>/i, `<head$1>${tag}`);
}

function patchNorway2026Facts(html, path) {
  if (path !== "/norvec-vizesi/") return html;
  const replacements = [
    ["NOK 500 günlük finans kuralı", "konaklama durumuna göre güncel UDI finans rehberi"],
    ["NOK 500/gün finans kuralı", "UDI 300/1.300 NOK finans rehberi"],
    ["Günlük 500 NOK ve banka dosyası", "Konaklamaya göre 300/1.300 NOK ve banka dosyası"],
    ["<b>500 NOK</b><span>Günlük maddi imkân eşiği</span>", "<b>300 / 1.300 NOK</b><span>UDI günlük mali yeterlilik rehberi</span>"],
    ["Norveç'in günlük 500 NOK eşiğine ek olarak ulaşım, otel ve dönüş masraflarını karşılayabilecek mali kapasite gösterilmelidir.", "UDI'nin güncel rehberinde önceden ödenmiş konaklama veya aile/arkadaş yanında kalış için günlük 300 NOK; konaklama önceden belgelenmemişse günlük 1.300 NOK referans alınır. Birlikte seyahat edenlerde ikinci durumda kişi başı en az 1.000 NOK rehberi uygulanır; gerçek ulaşım, konaklama ve dönüş masrafları ayrıca karşılanabilir olmalıdır."],
    ["<h2>Norveç Vizesinde 500 NOK Günlük Maddi İmkân Kuralı</h2><p>Norveç'in Türkiye için resmî vize sayfası, başvuru sahibinin Norveç ve Schengen alanında kaldığı süre boyunca <strong>en az günlük 500 NOK</strong> maddi imkânı belgeleyebilmesini ister. Bu rakamı yalnızca “hesaba koyulacak para” olarak düşünmek yanlıştır; dönüş yolculuğu, konaklama ve gerçek seyahat masrafları da dosyanın finansal mantığında değerlendirilir.</p>", "<h2>Norveç Vizesinde Güncel Mali Yeterlilik Rehberi</h2><p>UDI'nin güncel rehberine göre mali yeterlilik her dosyada bireysel değerlendirilir. Genel referans, aile/arkadaş yanında veya önceden ödenmiş konaklamada <strong>günlük 300 NOK</strong>; tüm konaklama önceden belgelenmemişse <strong>günlük 1.300 NOK</strong> seviyesidir. Birlikte seyahat edenlerde ikinci durumda kişi başına en az 1.000 NOK rehberi belirtilir. Dönüş yolculuğu ve gerçek seyahat masrafları da karşılanabilir olmalıdır.</p>"],
    ["<b>500 NOK kuralını yalnızca son gün yatırılan bakiye olarak görmek</b><p>Düzenli gelir ve hesap geçmişi finansal güvenilirliğin önemli parçasıdır.</p>", "<b>Güncel UDI mali yeterlilik rehberini sabit tek tutar sanmak</b><p>Konaklama durumuna göre 300/1.300 NOK referansları ve dosyanın gerçek seyahat bütçesi birlikte değerlendirilir; düzenli gelir ve hesap geçmişi de önemlidir.</p>"],
    ["<summary>Norveç vizesi için banka hesabında ne kadar para olmalı?</summary><p>Resmî Türkiye sayfasında en az günlük 500 NOK maddi imkân şartı belirtilir. Bunun yanında dönüş yolculuğu ve gerçek seyahat maliyetlerinin karşılanabilirliği de önemlidir.</p>", "<summary>Norveç vizesi için banka hesabında ne kadar para olmalı?</summary><p>UDI'nin güncel rehberinde yeterlilik bireysel değerlendirilir: aile/arkadaş yanında veya önceden ödenmiş konaklamada günlük 300 NOK; konaklama önceden belgelenmemişse günlük 1.300 NOK referans alınır. Birlikte seyahat edenlerde ikinci durumda kişi başı en az 1.000 NOK rehberi belirtilir. Dönüş ve gerçek seyahat maliyetleri ayrıca karşılanabilir olmalıdır.</p>"],
    ["Norveç'in Türkiye sayfası, başvuru sahibinin Norveç ve Schengen'deki kalışı boyunca en az günlük 500 NOK maddi imkanı belgeleyebilmesini ister. Yeterli kişisel kaynak yoksa Norveç'teki ziyaretçi sponsorluk formu kullanabilir.", "UDI'nin güncel rehberinde mali yeterlilik bireysel değerlendirilir. Genel referans, aile/arkadaş yanında veya önceden ödenmiş konaklamada günlük 300 NOK; konaklama önceden belgelenmemişse günlük 1.300 NOK'tur. Yeterli kişisel kaynak yoksa Norveç'teki ziyaretçi sponsorluk formu kullanılabilir."],
  ];
  let out = html;
  for (const [from, to] of replacements) out = out.replace(from, to);
  return out;
}

function patchDenmark2026Status(html, path) {
  if (path !== "/danimarka-vizesi/") return html;
  const replacements = [
    ["31 Temmuz 2026 Büyükelçilik duyurusu", "18 Eylül 2026 Büyükelçilik güncellemesi"],
    ["Danimarka’nın Türkiye’deki resmî sayfası 31 Temmuz 2026 tarihinde, Ankara Büyükelçiliğine gelen vize başvurularındaki olağanüstü yoğunluk nedeniyle işlem sürelerinin normalden çok daha uzun olduğunu duyurdu. Duyuruda o tarihte 30 Nisan 2026 tarihine kadar alınmış başvuruların işlendiği belirtiliyor.", "Danimarka’nın Türkiye’deki resmî sayfası 18 Eylül 2026 tarihinde güncellendi. Ankara Büyükelçiliğine gelen olağanüstü sayıdaki vize başvuruları nedeniyle işlem sürelerinin normalden çok daha uzun olduğu ve o tarihte 19 Haziran 2026 tarihinden itibaren yapılan başvuruların değerlendirildiği bildiriliyor."],
    ["Normal Schengen değerlendirme süresi 15 takvim günü olsa da Danimarka Büyükelçiliği Ankara 31 Temmuz 2026 güncellemesinde olağanüstü yoğunluk nedeniyle işlem süresinin normalden çok daha uzun olduğunu bildirmiştir. Güncel durum seyahat öncesinde resmi kaynaktan kontrol edilmelidir.", "Danimarka Büyükelçiliği Ankara’nın 18 Eylül 2026 güncellemesine göre olağanüstü başvuru yoğunluğu nedeniyle işlem süresi normalden çok daha uzundur; Büyükelçilik o tarihte 19 Haziran 2026 tarihinden itibaren yapılan başvuruları değerlendirdiğini bildirmiştir. Kişisel seyahat planları nedeniyle dosyaların hızlandırılması mümkün değildir; güncel durum seyahat öncesinde resmî kaynaktan kontrol edilmelidir."],
  ];
  let out = html;
  for (const [from, to] of replacements) out = out.replace(from, to);
  return out;
}

function addItalyArticleSchema(html, path) {
  if (path !== "/italya-vizesi/" || html.includes('"@id":"https://gundoganvize.com/italya-vizesi/#article"')) return html;
  const schema = {"@context":"https://schema.org","@type":"Article","@id":"https://gundoganvize.com/italya-vizesi/#article","headline":"İtalya Vizesi: iDATA Randevu, Evraklar ve Finans Rehberi","description":"Türkiye’den İtalya Schengen vizesi için iDATA randevu süreci, konsolosluk yetki bölgesi, evraklar, mali yeterlilik, sigorta ve başvuru rehberi.","mainEntityOfPage":{"@type":"WebPage","@id":"https://gundoganvize.com/italya-vizesi/"},"author":{"@type":"Organization","name":"Gündoğan Vize","url":"https://gundoganvize.com/hakkimizda/"},"publisher":{"@type":"Organization","name":"Gündoğan Vize","url":"https://gundoganvize.com/"},"dateModified":"2026-09-24","inLanguage":"tr-TR","isAccessibleForFree":true};
  return html.replace(/<\/head>/i, `<script type="application/ld+json">${JSON.stringify(schema)}</script></head>`);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isCustomDomain = url.hostname === SITE_HOST || url.hostname === `www.${SITE_HOST}`;
    const path = cleanPath(url.pathname);
    if (isCustomDomain && (url.protocol !== "https:" || url.hostname !== SITE_HOST || path !== url.pathname)) {
      const target = new URL(`${SITE_ORIGIN}${path}`);
      target.search = url.search;
      return new Response(null, { status: 301, headers: { Location: target.toString(), "Cache-Control": "public, max-age=3600, s-maxage=3600", "X-GundoganVize-Canonical-Redirect": "2026-09-17" } });
    }
    const response = await env.ASSETS.fetch(request);
    const headers = new Headers(response.headers);
    if (url.hostname.endsWith(".pages.dev")) headers.set("X-Robots-Tag", "noindex, nofollow");
    const type = headers.get("content-type") || "";
    if (!type.includes("text/html")) return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
    const canonical = canonicalUrl(url);
    let body = replaceCanonical(await response.text(), canonical);
    body = patchNorway2026Facts(body, path);
    body = patchDenmark2026Status(body, path);
    body = addItalyArticleSchema(body, path);
    headers.delete("content-length");
    headers.set("Link", `<${canonical}>; rel="canonical"`);
    return new Response(body, { status: response.status, statusText: response.statusText, headers });
  },
};
