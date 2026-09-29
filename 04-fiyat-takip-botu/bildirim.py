"""Uyarıları iletir: her zaman ekrana, varsa GitHub Actions özetine ve Telegram'a."""

import os

import requests

from ayarlar import ORTALAMA_KAYIT


def tl(deger):
    """48982.5 -> '48.982,50' (Türkçe sayı biçimi)."""
    return f"{deger:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def uyari_metni(uyari, ad):
    return (f"📉 {ad}: {tl(uyari.fiyat)} TL — son {ORTALAMA_KAYIT} kaydın ortalamasının "
            f"(%{tl(abs(uyari.fark_yuzde))}) altında ({tl(uyari.ortalama)} TL)")


def github_ozeti(fiyat_satirlari, uyari_satirlari):
    """GitHub Actions'ta çalışıyorsa çalıştırma sayfasına bir özet tablosu yazar."""
    yol = os.environ.get("GITHUB_STEP_SUMMARY")
    if not yol:
        return
    satirlar = ["## Günlük fiyat kontrolü", "", "| Varlık | Tarih | Fiyat (TL) |", "|---|---|---:|"]
    satirlar += [f"| {ad} | {tarih} | {tl(fiyat)} |" for ad, tarih, fiyat in fiyat_satirlari]
    satirlar += ["", "### Uyarılar", ""]
    satirlar += [f"- {m}" for m in uyari_satirlari] or ["Uyarı yok."]
    with open(yol, "a", encoding="utf-8") as f:
        f.write("\n".join(satirlar) + "\n")


def telegram(mesaj):
    """TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID tanımlıysa mesaj gönderir; değilse sessizce geçer."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    sohbet = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and sohbet):
        return False
    yanit = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": sohbet, "text": mesaj},
        timeout=30,
    )
    yanit.raise_for_status()
    return True
