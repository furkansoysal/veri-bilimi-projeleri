import pytest

from analiz import Uyari, dusus_var_mi


def test_ortalamanin_altinda_uyari_verir():
    onceki = [100, 102, 101, 99, 100, 98, 100]  # ortalama 100
    assert dusus_var_mi(97, onceki, 7) == pytest.approx(100)


def test_ortalamanin_ustunde_uyari_vermez():
    assert dusus_var_mi(101, [100] * 7, 7) is None


def test_ortalamaya_esitse_uyari_vermez():
    assert dusus_var_mi(100, [100] * 7, 7) is None


def test_yetersiz_gecmiste_karar_vermez():
    assert dusus_var_mi(1, [100] * 6, 7) is None


def test_sadece_en_yeni_kayitlar_kullanilir():
    # Liste yeniden eskiye; 8. eleman (çok yüksek) hesaba katılmamalı.
    onceki = [10] * 7 + [1000]
    assert dusus_var_mi(9, onceki, 7) == pytest.approx(10)


def test_fark_yuzde():
    assert Uyari("X", "2026-09-29", 95, 100).fark_yuzde == pytest.approx(-5)
