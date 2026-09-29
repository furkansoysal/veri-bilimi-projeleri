"""Kaydedilmiş modeli yükler ve tek bir araç için fiyat tahmini yapar.

Hem Streamlit arayüzü (app.py) hem de testler bu modülü kullanır.
"""

import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

MODEL_KLASORU = Path(__file__).resolve().parent / "model"

KATEGORIK = ["marka", "seri", "vites_tipi", "yakit_tipi", "kasa_tipi", "renk", "kimden"]
SAYISAL = ["yil", "kilometre", "motor_hacmi", "motor_gucu", "degisen_sayisi", "boyali_sayisi"]


@lru_cache(maxsize=1)
def model_yukle():
    return joblib.load(MODEL_KLASORU / "fiyat_modeli.joblib")


@lru_cache(maxsize=1)
def secenekleri_yukle():
    return json.loads((MODEL_KLASORU / "secenekler.json").read_text(encoding="utf-8"))


def fiyat_tahmin_et(arac):
    """`arac` sözlüğündeki bilgilerle tahmini fiyatı (TL) döndürür.

    Değişen/boyalı sayısı bilinmiyorsa None verilebilir; model bunu eğitimdeki gibi
    "bilgi yok" olarak işler.
    """
    eksik = set(KATEGORIK + SAYISAL) - arac.keys()
    if eksik:
        raise ValueError(f"Eksik alanlar: {sorted(eksik)}")
    satir = pd.DataFrame([{alan: arac[alan] for alan in KATEGORIK + SAYISAL}])
    satir[SAYISAL] = satir[SAYISAL].apply(pd.to_numeric)  # None -> NaN
    return float(model_yukle().predict(satir)[0])


def tahmin_araligi(tahmin, yuzde_hata):
    """Modelin tipik yüzde hatasına göre alt-üst sınır."""
    return tahmin * (1 - yuzde_hata / 100), tahmin * (1 + yuzde_hata / 100)


def yuvarla(tl, adim=5_000):
    """Tahmini ilan fiyatı gibi okunacak şekilde yuvarlar (ör. 847.312 -> 845.000)."""
    return round(tl / adim) * adim


def binlik(deger):
    """47312 -> '47.312'"""
    return f"{deger:,.0f}".replace(",", ".")


def ondalik(deger, basamak):
    """7.174 -> '7,2' (basamak=1)"""
    return f"{deger:.{basamak}f}".replace(".", ",")


def tl(deger):
    return f"{binlik(deger)} TL"
