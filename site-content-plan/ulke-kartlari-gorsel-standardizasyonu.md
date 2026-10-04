# Ülke Kartları Görsel Standardizasyonu

Amaç: Ülkeler sayfasındaki her ülke kartında o ülkeye özgü, bir daha başka ülke kartında tekrar kullanılmayan gerçek bir destinasyon görseli kullanmak.

## Kurallar
- Aynı görsel iki farklı ülkede kesinlikle kullanılmayacak.
- Görsel, ilgili ülkenin tanınabilir şehir, mimari, doğal alan veya simgesini göstermeli.
- Bayrak ile kart görseli aynı ülkeye ait olmalı.
- Mümkünse yatay 16:9 veya kart oranına uygun yüksek çözünürlüklü görseller tercih edilmeli.
- Stok görsel tekrarları, jenerik uçak/terminal/bulut fotoğrafları ülke kartlarında kullanılmamalı.
- Görseller WebP/AVIF olarak optimize edilmeli ve lazy-load kullanılmalı.
- Alt metinler SEO uyumlu ve doğal olmalı: ör. `Fransa vizesi - Paris şehir görünümü`.

## Önerilen ülke-görsel eşleşmeleri
- Bulgaristan: Sofya / Aleksandr Nevski Katedrali
- Hırvatistan: Dubrovnik eski şehir
- Çekya: Prag / Charles Bridge
- Danimarka: Kopenhag / Nyhavn
- Estonya: Tallinn eski şehir
- Finlandiya: Helsinki / Senato Meydanı
- Fransa: Paris / Eyfel veya şehir panoraması
- Yunanistan: Atina / Akropolis veya Santorini
- Macaristan: Budapeşte / Parlamento Binası
- İzlanda: şelale, siyah kum sahili veya Reykjavik
- İtalya: Roma / Kolezyum veya Venedik
- Letonya: Riga eski şehir
- Lihtenştayn: Vaduz / Alp manzarası
- Litvanya: Vilnius eski şehir
- Lüksemburg: Lüksemburg şehir merkezi / eski şehir
- Malta: Valletta / Grand Harbour
- Hollanda: Amsterdam kanalları
- Norveç: Bergen / fiyort
- Polonya: Krakow eski şehir
- Portekiz: Lizbon / tramvay veya Porto
- Romanya: Bükreş veya Braşov / Peleş Şatosu
- Almanya: Berlin / Brandenburg Kapısı
- Avusturya: Viyana / Schönbrunn veya şehir merkezi
- Belçika: Brüksel / Grand Place
- İsviçre: Zürih/Luzern veya Alp manzarası
- İsveç: Stockholm eski şehir
- Slovenya: Ljubljana / Bled Gölü
- Slovakya: Bratislava eski şehir
- İspanya: Madrid / Barcelona / Sagrada Familia

## Uygulama notu
Mevcut ülkeler grid'i, tüm kart görsellerinin tek bir veri kaynağından (`countryImages`) okunacağı şekilde düzenlenmeli. Her ülke için benzersiz bir dosya yolu tanımlanmalı ve tekrar kontrolü build aşamasında yapılmalı.
