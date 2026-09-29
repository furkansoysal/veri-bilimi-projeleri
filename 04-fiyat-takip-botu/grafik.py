"""Veritabanındaki fiyat geçmişinden iki grafik üretir (cikti/ klasörüne).

1. degisim_karsilastirma.png — dört varlığın yüzde değişimi, aynı başlangıca (100) endeksli
2. fiyat_gecmisi.png         — her varlık ayrı panelde: fiyat, 7 kayıtlık ortalama, uyarı günleri

Kullanım:  python grafik.py
"""

import sqlite3

import matplotlib

matplotlib.use("Agg")  # ekransız ortamda (GitHub Actions) çalışabilsin diye
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

from ayarlar import CIKTI, GECMIS_GUN, ORTALAMA_KAYIT, VARLIKLAR, VERITABANI

METIN = "#0b0b0b"
IKINCIL = "#52514e"
SOLUK = "#8a8984"
IZGARA = "#e6e5e0"
KENAR = "#c3c2b7"


def sayi(deger, ondalik=0):
    return f"{deger:,.{ondalik}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def veriyi_oku():
    """fiyatlar tablosunu tarih × varlık biçiminde geniş bir tabloya çevirir."""
    with sqlite3.connect(VERITABANI) as baglanti:
        df = pd.read_sql("SELECT tarih, varlik, fiyat FROM fiyatlar", baglanti, parse_dates=["tarih"])
    genis = df.pivot(index="tarih", columns="varlik", values="fiyat").sort_index()
    son = genis.index.max()
    return genis[genis.index > son - pd.Timedelta(days=GECMIS_GUN)]


def eksen_sade(ax):
    ax.grid(axis="y", color=IZGARA, linewidth=0.8)
    for kenar in ("top", "right"):
        ax.spines[kenar].set_visible(False)
    for kenar in ("left", "bottom"):
        ax.spines[kenar].set_color(KENAR)
    ax.tick_params(colors=IKINCIL, labelsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))


def etiketleri_ayir(konumlar, en_az_bosluk):
    """Çizgi sonu etiketleri üst üste binmesin diye dikey konumları aralar."""
    sirali = sorted(konumlar.items(), key=lambda x: x[1])
    sonuc, onceki = {}, None
    for kod, y in sirali:
        if onceki is not None and y - onceki < en_az_bosluk:
            y = onceki + en_az_bosluk
        sonuc[kod], onceki = y, y
    return sonuc


def karsilastirma_grafigi(genis):
    # Döviz hafta sonu işlem görmez; boş günleri bir önceki kurla dolduruyoruz ki çizgiler kesilmesin.
    gunluk = genis.asfreq("D").ffill().dropna()
    endeks = gunluk / gunluk.iloc[0] * 100

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.axhline(100, color=SOLUK, linewidth=1, linestyle="--")

    uclar = {}
    for kod, ayar in VARLIKLAR.items():
        ax.plot(endeks.index, endeks[kod], color=ayar["renk"], linewidth=2)
        uclar[kod] = endeks[kod].iloc[-1]

    # Çizgi sonlarına doğrudan etiket: renk ayırt edemeyen biri de hangi çizginin ne olduğunu okuyabilsin.
    son_gun = endeks.index[-1]
    aralik = endeks.max().max() - endeks.min().min()
    for kod, y in etiketleri_ayir(uclar, aralik * 0.06).items():
        degisim = uclar[kod] - 100
        ax.annotate(
            f"{VARLIKLAR[kod]['ad']}  {'+' if degisim >= 0 else '−'}%{sayi(abs(degisim), 1)}",
            xy=(son_gun, uclar[kod]), xytext=(son_gun + pd.Timedelta(days=2), y), textcoords="data",
            va="center", fontsize=9.5, color=METIN, annotation_clip=False,
            arrowprops={"arrowstyle": "-", "color": VARLIKLAR[kod]["renk"], "linewidth": 1, "shrinkA": 0, "shrinkB": 2},
        )

    ax.set_title(f"Son {len(endeks)} günde değişim (başlangıç = 100)", loc="left",
                 fontsize=13, fontweight="bold", color=METIN)
    ax.set_ylabel("Endeks (başlangıç günü = 100)", color=METIN)
    ax.set_xlabel("Tarih", color=METIN)
    eksen_sade(ax)
    fig.text(0.01, 0.01, "Kaynak: Frankfurter (ECB kurları), CoinGecko · Gram altın PAXG üzerinden hesaplanmıştır",
             fontsize=8, color=SOLUK)
    fig.tight_layout()
    fig.subplots_adjust(right=0.8)
    fig.savefig(CIKTI / "degisim_karsilastirma.png", bbox_inches="tight")
    plt.close(fig)
    return endeks


def gecmis_grafigi(genis):
    fig, eksenler = plt.subplots(2, 2, figsize=(11, 7), dpi=150, sharex=True)

    for ax, (kod, ayar) in zip(eksenler.flat, VARLIKLAR.items()):
        seri = genis[kod].dropna()
        # Günlük betikteki kuralın aynısı: önceki 7 kaydın ortalaması (bugün hariç).
        ortalama = seri.shift(1).rolling(ORTALAMA_KAYIT).mean()
        uyari = seri[seri < ortalama]

        ax.plot(seri.index, seri, color=ayar["renk"], linewidth=2, label="Fiyat")
        ax.plot(ortalama.index, ortalama, color=SOLUK, linewidth=1.2, linestyle="--",
                label=f"Önceki {ORTALAMA_KAYIT} kaydın ortalaması")
        ax.scatter(uyari.index, uyari, s=28, facecolor="white", edgecolor=METIN, linewidth=1.2,
                   zorder=3, label="Ortalamanın altında (uyarı)")

        ondalik = 0 if seri.max() > 1000 else 2
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _, o=ondalik: sayi(v, o)))
        ax.set_title(f"{ayar['ad']} · {sayi(seri.iloc[-1], ondalik)} TL", loc="left",
                     fontsize=11, fontweight="bold", color=METIN, pad=18)
        ax.text(0, 1.02, f"{len(uyari)} uyarı günü", transform=ax.transAxes, ha="left", va="bottom",
                fontsize=8.5, color=IKINCIL)
        eksen_sade(ax)

    for ax in eksenler[:, 0]:
        ax.set_ylabel("Fiyat (TL)", color=METIN)
    tutamaclar, etiketler = eksenler.flat[0].get_legend_handles_labels()
    fig.suptitle("Fiyat geçmişi ve uyarı günleri", x=0.01, y=0.995, ha="left",
                 fontsize=13, fontweight="bold", color=METIN)
    fig.legend(tutamaclar, etiketler, loc="upper left", ncol=3, frameon=False, fontsize=9,
               bbox_to_anchor=(0.003, 0.965))
    fig.text(0.01, -0.01, "Kaynak: Frankfurter (ECB kurları), CoinGecko", fontsize=8, color=SOLUK)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(CIKTI / "fiyat_gecmisi.png", bbox_inches="tight")
    plt.close(fig)


def main():
    CIKTI.mkdir(exist_ok=True)
    genis = veriyi_oku()
    endeks = karsilastirma_grafigi(genis)
    gecmis_grafigi(genis)
    print(f"Grafikler kaydedildi: {CIKTI}  ({endeks.index[0]:%d.%m.%Y} – {endeks.index[-1]:%d.%m.%Y})")


if __name__ == "__main__":
    main()
