"""İlk kurulumda veritabanını son 90 günün verisiyle doldurur.

Böylece 7 günlük ortalama kuralı ve grafikler ilk günden anlamlı çalışır.
Tekrar çalıştırmak güvenlidir: aynı günün kaydı güncellenir, çift kayıt oluşmaz.

Kullanım:  python gecmis_yukle.py
"""

from ayarlar import GECMIS_GUN, VARLIKLAR, VERITABANI
from kaynaklar import gecmis_getir
from veritabani import baglan, fiyat_kaydet


def main():
    baglanti = baglan(VERITABANI)
    for kod, ayar in VARLIKLAR.items():
        gecmis = gecmis_getir(ayar, GECMIS_GUN)
        for tarih, fiyat in gecmis.items():
            fiyat_kaydet(baglanti, tarih, kod, fiyat)
        print(f"{ayar['ad']:<11} {len(gecmis):>3} gün  ({min(gecmis)} → {max(gecmis)})")
    baglanti.commit()
    baglanti.close()


if __name__ == "__main__":
    main()
