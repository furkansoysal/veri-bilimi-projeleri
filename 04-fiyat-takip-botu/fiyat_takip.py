"""Günlük çalışan ana betik: fiyatları çeker, kaydeder, düşüş varsa uyarır.

Kullanım:  python fiyat_takip.py
"""

import sys

import requests

from analiz import Uyari, dusus_var_mi
from ayarlar import ORTALAMA_KAYIT, VARLIKLAR, VERITABANI
from bildirim import github_ozeti, telegram, tl, uyari_metni
from kaynaklar import son_fiyat
from veritabani import baglan, fiyat_kaydet, onceki_fiyatlar, uyari_kaydet


def main():
    baglanti = baglan(VERITABANI)
    fiyat_satirlari, yeni_uyarilar, hatalar = [], [], []

    for kod, ayar in VARLIKLAR.items():
        try:
            tarih, fiyat = son_fiyat(ayar)
        except requests.RequestException as hata:
            hatalar.append(kod)
            print(f"✗ {ayar['ad']}: fiyat alınamadı ({hata})")
            continue

        # Karşılaştırma, bugünün kaydı yazılmadan ÖNCEKİ kayıtlarla yapılır.
        onceki = onceki_fiyatlar(baglanti, kod, tarih, ORTALAMA_KAYIT)
        fiyat_kaydet(baglanti, tarih, kod, fiyat)
        fiyat_satirlari.append((ayar["ad"], tarih, fiyat))
        print(f"✓ {ayar['ad']:<11} {tarih}  {tl(fiyat):>15} TL")

        ortalama = dusus_var_mi(fiyat, onceki, ORTALAMA_KAYIT)
        if ortalama is not None:
            uyari = Uyari(kod, tarih, fiyat, ortalama)
            # Hafta sonu döviz kuru değişmez; aynı günün uyarısı ikinci kez gönderilmez.
            if uyari_kaydet(baglanti, uyari):
                yeni_uyarilar.append(uyari_metni(uyari, ayar["ad"]))

    baglanti.commit()
    baglanti.close()

    print()
    for mesaj in yeni_uyarilar:
        print("UYARI:", mesaj)
    if not yeni_uyarilar:
        print("Yeni uyarı yok.")

    github_ozeti(fiyat_satirlari, yeni_uyarilar)
    if yeni_uyarilar and telegram("Fiyat uyarısı\n\n" + "\n".join(yeni_uyarilar)):
        print("Telegram bildirimi gönderildi.")

    # Hiçbir fiyat alınamadıysa hata koduyla çık ki otomasyon başarısız görünsün.
    return 1 if len(hatalar) == len(VARLIKLAR) else 0


if __name__ == "__main__":
    sys.exit(main())
