"""SQLite veritabanı işlemleri: tablo oluşturma, fiyat ve uyarı kaydı."""

import datetime as dt
import sqlite3
from pathlib import Path

SEMA = """
CREATE TABLE IF NOT EXISTS fiyatlar (
    tarih      TEXT NOT NULL,   -- YYYY-AA-GG
    varlik     TEXT NOT NULL,   -- ör. USDTRY
    fiyat      REAL NOT NULL,   -- TL
    kaydedilme TEXT NOT NULL,   -- satırın son yazıldığı an (UTC)
    PRIMARY KEY (tarih, varlik)
);

CREATE TABLE IF NOT EXISTS uyarilar (
    tarih      TEXT NOT NULL,
    varlik     TEXT NOT NULL,
    fiyat      REAL NOT NULL,
    ortalama   REAL NOT NULL,   -- karşılaştırılan önceki kayıtların ortalaması
    fark_yuzde REAL NOT NULL,   -- negatif = ortalamanın altında
    PRIMARY KEY (tarih, varlik)
);
"""


def baglan(yol):
    """Veritabanına bağlanır; dosya ya da tablolar yoksa oluşturur."""
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    baglanti = sqlite3.connect(yol)
    baglanti.executescript(SEMA)
    return baglanti


def fiyat_kaydet(baglanti, tarih, varlik, fiyat):
    """Günün fiyatını yazar. Aynı gün tekrar çalışırsa değer güncellenir, çift kayıt oluşmaz."""
    baglanti.execute(
        """
        INSERT INTO fiyatlar (tarih, varlik, fiyat, kaydedilme) VALUES (?, ?, ?, ?)
        ON CONFLICT (tarih, varlik) DO UPDATE SET fiyat = excluded.fiyat, kaydedilme = excluded.kaydedilme
        """,
        (tarih, varlik, fiyat, dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")),
    )


def onceki_fiyatlar(baglanti, varlik, tarih, adet):
    """`tarih`ten önceki en yeni `adet` kaydın fiyatları (yeniden eskiye)."""
    satirlar = baglanti.execute(
        "SELECT fiyat FROM fiyatlar WHERE varlik = ? AND tarih < ? ORDER BY tarih DESC LIMIT ?",
        (varlik, tarih, adet),
    ).fetchall()
    return [s[0] for s in satirlar]


def uyari_kaydet(baglanti, uyari):
    """Uyarıyı yazar. O gün için zaten kayıtlıysa False döner (aynı uyarı iki kez gönderilmesin)."""
    imlec = baglanti.execute(
        "INSERT OR IGNORE INTO uyarilar (tarih, varlik, fiyat, ortalama, fark_yuzde) VALUES (?, ?, ?, ?, ?)",
        (uyari.tarih, uyari.varlik, uyari.fiyat, uyari.ortalama, uyari.fark_yuzde),
    )
    return imlec.rowcount == 1
