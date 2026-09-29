"""Uyarı kuralı: fiyat, önceki kayıtların ortalamasının altına düştü mü?"""

from dataclasses import dataclass


@dataclass
class Uyari:
    varlik: str
    tarih: str
    fiyat: float
    ortalama: float

    @property
    def fark_yuzde(self):
        return (self.fiyat / self.ortalama - 1) * 100


def dusus_var_mi(fiyat, onceki_fiyatlar, gereken_kayit):
    """Fiyat, önceki kayıtların ortalamasının altındaysa ortalamayı, değilse None döndürür.

    Yeterli geçmiş yoksa (ör. ilk günler) karar verilmez ve None döner.
    """
    if len(onceki_fiyatlar) < gereken_kayit:
        return None
    ortalama = sum(onceki_fiyatlar[:gereken_kayit]) / gereken_kayit
    return ortalama if fiyat < ortalama else None
