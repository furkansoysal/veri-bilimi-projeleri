"""İkinci el araç fiyat tahmini — Streamlit arayüzü.

Çalıştırma:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from tahmin import binlik, fiyat_tahmin_et, ondalik, secenekleri_yukle, tahmin_araligi, tl, yuvarla

KLASOR = Path(__file__).resolve().parent
KM_YILLIK = 15_000  # varsayılan kilometre için yıllık ortalama kullanım

st.set_page_config(page_title="İkinci El Araç Fiyat Tahmini", page_icon="🚗", layout="centered")

s = secenekleri_yukle()
basari = s["basari"]

st.title("🚗 İkinci El Araç Fiyat Tahmini")
st.caption(
    f"arabam.com'daki ~50 bin ilanla eğitilmiş bir makine öğrenmesi modeli. "
    f"Fiyatlar **{s['veri_tarihi']}** piyasasını yansıtır."
)

# Marka ve seri formun dışında: seri değişince aşağıdaki alanlar o serinin tipik değerleriyle dolsun.
markalar = sorted(s["markalar"])
sol, sag = st.columns(2)
marka = sol.selectbox("Marka", markalar, index=markalar.index("Renault") if "Renault" in markalar else 0)
seriler = s["markalar"][marka]
en_populer = max(seriler, key=lambda x: s["seri_varsayilan"][f"{marka}|{x}"]["adet"])
seri = sag.selectbox("Seri", seriler, index=seriler.index(en_populer))
tipik = s["seri_varsayilan"][f"{marka}|{seri}"]


def sira(liste, deger):
    return liste.index(deger) if deger in liste else 0


with st.form("arac"):
    sol, sag = st.columns(2)
    yil_min, yil_max = s["aralik"]["yil"]
    yil = sol.number_input("Model yılı", yil_min, yil_max, value=tipik["yil"], step=1)
    kilometre = sag.number_input("Kilometre", 0, s["aralik"]["kilometre"][1],
                                 value=max(0, (yil_max - tipik["yil"]) * KM_YILLIK), step=5_000)

    yakit = sol.selectbox("Yakıt", s["yakit_tipi"], index=sira(s["yakit_tipi"], tipik["yakit_tipi"]))
    vites = sag.selectbox("Vites", s["vites_tipi"], index=sira(s["vites_tipi"], tipik["vites_tipi"]))
    kasa = sol.selectbox("Kasa tipi", s["kasa_tipi"], index=sira(s["kasa_tipi"], tipik["kasa_tipi"]))
    renk = sag.selectbox("Renk", s["renk"])

    hacim = sol.number_input("Motor hacmi (cc)", 600, 7_000, value=int(tipik["motor_hacmi"]), step=100)
    guc = sag.number_input("Motor gücü (hp)", 40, 600, value=int(tipik["motor_gucu"]), step=5)

    degisen = sol.number_input("Değişen parça sayısı", 0, 13, value=0)
    boyali = sag.number_input("Boyalı parça sayısı", 0, 13, value=0)
    bilgi_yok = st.checkbox("Değişen/boyalı parça bilgisi bilinmiyor")

    kimden = st.radio("Satıcı", s["kimden"], horizontal=True)
    gonder = st.form_submit_button("Fiyatı tahmin et", type="primary", use_container_width=True)

if gonder:
    tahmin = fiyat_tahmin_et({
        "marka": marka, "seri": seri, "yil": yil, "kilometre": kilometre,
        "yakit_tipi": yakit, "vites_tipi": vites, "kasa_tipi": kasa, "renk": renk,
        "motor_hacmi": hacim, "motor_gucu": guc,
        "degisen_sayisi": None if bilgi_yok else degisen,
        "boyali_sayisi": None if bilgi_yok else boyali,
        "kimden": kimden,
    })
    alt, ust = tahmin_araligi(tahmin, basari["medyan_yuzde_hata"])

    st.metric("Tahmini fiyat", tl(yuvarla(tahmin)))
    st.write(
        f"Model bu tür ilanlarda tipik olarak **±%{basari['medyan_yuzde_hata']:.0f}** yanılıyor: "
        f"makul aralık **{tl(yuvarla(alt))} – {tl(yuvarla(ust))}**."
    )
    fiyat_min, fiyat_max = s["aralik"]["fiyat"]
    if not fiyat_min <= tahmin <= fiyat_max:
        st.warning("Bu tahmin, modelin eğitildiği fiyat aralığının dışında; güvenilirliği düşük.")
    st.info(f"Tahmin {s['veri_tarihi']} ilan fiyatlarına göredir; bugünkü piyasa enflasyon nedeniyle daha yüksek olabilir.")

with st.expander("Model hakkında"):
    st.markdown(
        f"""
- **Model:** gradient boosting (scikit-learn `HistGradientBoostingRegressor`), fiyatın logaritması üzerinde eğitildi
- **Veri:** {binlik(basari['egitim_satir'])} ilanla eğitildi, modelin hiç görmediği {binlik(basari['test_satir'])} ilanla test edildi
- **Ortalama hata:** {tl(basari['mae_tl'])} · **tipik hata:** %{ondalik(basari['medyan_yuzde_hata'], 1)} · **R²:** {ondalik(basari['r2'], 3)}
- Doğrusal regresyon ve random forest ile karşılaştırıldı; random forest'la aynı doğrulukta, dosyası ~200 kat küçük olduğu için bu model seçildi.
"""
    )
    st.image(str(KLASOR / "cikti" / "model_karsilastirma.png"))
    st.image(str(KLASOR / "cikti" / "ozellik_onemi.png"))

st.caption("Geliştiren: Ahmet Furkan Soysal · [Kaynak kod](https://github.com/furkansoysal/veri-bilimi-projeleri/tree/main/06-tahmin-modeli-arayuz)")
