from analiz import Uyari
from veritabani import baglan, fiyat_kaydet, onceki_fiyatlar, uyari_kaydet


def test_ayni_gun_tekrar_kayit_guncellenir(tmp_path):
    db = baglan(tmp_path / "test.sqlite")
    fiyat_kaydet(db, "2026-09-29", "USDTRY", 48.9)
    fiyat_kaydet(db, "2026-09-29", "USDTRY", 49.1)
    assert db.execute("SELECT COUNT(*), MAX(fiyat) FROM fiyatlar").fetchone() == (1, 49.1)


def test_onceki_fiyatlar_bugunu_haric_tutar_ve_yeniden_eskiye_siralar(tmp_path):
    db = baglan(tmp_path / "test.sqlite")
    for gun, fiyat in [("2026-09-26", 1.0), ("2026-09-27", 2.0), ("2026-09-28", 3.0), ("2026-09-29", 4.0)]:
        fiyat_kaydet(db, gun, "BTCTRY", fiyat)
    assert onceki_fiyatlar(db, "BTCTRY", "2026-09-29", 2) == [3.0, 2.0]


def test_ayni_uyari_ikinci_kez_kaydedilmez(tmp_path):
    db = baglan(tmp_path / "test.sqlite")
    uyari = Uyari("EURTRY", "2026-09-29", 56.0, 57.0)
    assert uyari_kaydet(db, uyari) is True
    assert uyari_kaydet(db, uyari) is False
