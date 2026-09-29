import pytest

from tahmin import fiyat_tahmin_et, secenekleri_yukle, tahmin_araligi, yuvarla

ORNEK = {
    "marka": "Honda", "seri": "Civic", "yil": 2018, "kilometre": 100_000,
    "yakit_tipi": "Benzin", "vites_tipi": "Otomatik", "kasa_tipi": "Sedan", "renk": "Beyaz",
    "motor_hacmi": 1600, "motor_gucu": 125, "degisen_sayisi": 0, "boyali_sayisi": 0,
    "kimden": "Sahibinden",
}


def test_makul_bir_fiyat_uretir():
    alt, ust = secenekleri_yukle()["aralik"]["fiyat"]
    assert alt < fiyat_tahmin_et(ORNEK) < ust


def test_yeni_arac_daha_pahali():
    assert fiyat_tahmin_et({**ORNEK, "yil": 2022}) > fiyat_tahmin_et({**ORNEK, "yil": 2012})


def test_cok_kilometreli_arac_daha_ucuz():
    assert fiyat_tahmin_et({**ORNEK, "kilometre": 300_000}) < fiyat_tahmin_et({**ORNEK, "kilometre": 30_000})


def test_degisen_boyali_bilinmeden_de_calisir():
    assert fiyat_tahmin_et({**ORNEK, "degisen_sayisi": None, "boyali_sayisi": None}) > 0


def test_eksik_alan_hata_verir():
    eksik = {k: v for k, v in ORNEK.items() if k != "yil"}
    with pytest.raises(ValueError):
        fiyat_tahmin_et(eksik)


def test_secenekler_tutarli():
    s = secenekleri_yukle()
    for marka, seriler in s["markalar"].items():
        for seri in seriler:
            assert f"{marka}|{seri}" in s["seri_varsayilan"]


def test_aralik_ve_yuvarlama():
    assert tahmin_araligi(100, 10) == pytest.approx((90, 110))
    assert yuvarla(847_312) == 845_000
