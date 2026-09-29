"""Fiyatları ücretsiz ve anahtar gerektirmeyen API'lerden çeker.

- Döviz: Frankfurter (Avrupa Merkez Bankası referans kurları, iş günlerinde güncellenir)
- Altın ve kripto: CoinGecko
Tüm fonksiyonlar {"YYYY-AA-GG": fiyat} sözlüğü döndürür; tarihler Türkiye saatine göredir.
"""

import datetime as dt
import time
from zoneinfo import ZoneInfo

import requests

TSI = ZoneInfo("Europe/Istanbul")
ZAMAN_ASIMI = 30

oturum = requests.Session()
oturum.headers["User-Agent"] = "fiyat-takip-botu/1.0 (github.com/furkansoysal/veri-bilimi-projeleri)"


def _json_getir(url, deneme=3):
    """GET isteği atar; hız sınırı (429) veya sunucu hatasında birkaç kez tekrar dener."""
    for i in range(deneme):
        yanit = oturum.get(url, timeout=ZAMAN_ASIMI)
        if yanit.status_code in (429, 500, 502, 503, 504) and i < deneme - 1:
            time.sleep(10 * (i + 1))
            continue
        yanit.raise_for_status()
        return yanit.json()


def frankfurter(baz, gun):
    """Son `gun` günün TL karşılığı kurlarını döndürür (hafta sonları veri yok)."""
    baslangic = dt.date.today() - dt.timedelta(days=gun)
    veri = _json_getir(f"https://api.frankfurter.dev/v1/{baslangic.isoformat()}..?base={baz}&symbols=TRY")
    return {tarih: kurlar["TRY"] for tarih, kurlar in veri["rates"].items()}


def coingecko(coin, gun, carpan=1.0):
    """Son `gun` günün TL fiyatlarını döndürür.

    Günlük noktalar gece yarısı (UTC) fiyatıdır; listenin son noktası anlık fiyattır,
    bu yüzden bugünün değeri her zaman güncel olur.
    """
    veri = _json_getir(
        f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
        f"?vs_currency=try&days={gun}&interval=daily"
    )
    sonuc = {}
    for zaman_ms, fiyat in veri["prices"]:
        tarih = dt.datetime.fromtimestamp(zaman_ms / 1000, tz=TSI).date().isoformat()
        sonuc[tarih] = fiyat * carpan  # aynı güne düşen sonraki nokta öncekini ezer
    return sonuc


def gecmis_getir(ayar, gun):
    """Bir varlığın son `gun` günlük fiyat geçmişi."""
    if ayar["kaynak"] == "frankfurter":
        return frankfurter(ayar["baz"], gun)
    if ayar["kaynak"] == "coingecko":
        return coingecko(ayar["coin"], gun, ayar["carpan"])
    raise ValueError(f"Bilinmeyen kaynak: {ayar['kaynak']}")


def son_fiyat(ayar):
    """Bir varlığın en güncel fiyatı: (tarih, fiyat)."""
    gecmis = gecmis_getir(ayar, gun=5)  # hafta sonu/tatil boşluklarını kapsayacak kadar geniş
    tarih = max(gecmis)
    return tarih, gecmis[tarih]
