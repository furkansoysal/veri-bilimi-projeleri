"""Takip edilen varlıklar ve genel ayarlar."""

import os
from pathlib import Path

PROJE_KLASORU = Path(__file__).resolve().parent

# Veritabanı yolu ortam değişkeniyle değiştirilebilir (ör. bilgisayarda ayrı bir dosya kullanmak için).
VERITABANI = Path(os.environ.get("FIYAT_DB", PROJE_KLASORU / "veri" / "fiyatlar.sqlite"))
CIKTI = PROJE_KLASORU / "cikti"

ORTALAMA_KAYIT = 7  # uyarı için bugünkü fiyatın karşılaştırıldığı önceki kayıt sayısı
GECMIS_GUN = 90     # ilk kurulumda veritabanına doldurulan geçmiş

# 1 troy ons = 31.1034768 gram. PAXG token'ı 1 ons fiziki altına endeksli.
ONS_GRAM = 31.1034768

VARLIKLAR = {
    "USDTRY": {
        "ad": "Dolar/TL",
        "kaynak": "frankfurter",
        "baz": "USD",
        "renk": "#2a78d6",
    },
    "EURTRY": {
        "ad": "Euro/TL",
        "kaynak": "frankfurter",
        "baz": "EUR",
        "renk": "#4a3aa7",
    },
    "GRAMALTIN": {
        "ad": "Gram altın",
        "kaynak": "coingecko",
        "coin": "pax-gold",
        "carpan": 1 / ONS_GRAM,
        "renk": "#eda100",
    },
    "BTCTRY": {
        "ad": "Bitcoin",
        "kaynak": "coingecko",
        "coin": "bitcoin",
        "carpan": 1.0,
        "renk": "#1baf7a",
    },
}
