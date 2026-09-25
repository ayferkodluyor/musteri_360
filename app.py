
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================================
# MÜŞTERİ 360° | AI RELATIONSHIP INTELLIGENCE
# Ticari ve KOBİ müşteri portföyü - Sentetik demo
# ============================================================

st.set_page_config(
    page_title="Müşteri 360° | AI Relationship Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

VERI_DOSYASI = Path(__file__).resolve().parent / "musteri_portfoyu.csv"

AYLAR = {
    1: "Nisan",
    2: "Mayıs",
    3: "Haziran",
    4: "Temmuz",
    5: "Ağustos",
    6: "Eylül",
}

URUNLER = [
    "Ticari Kredi",
    "POS",
    "Teminat Mektubu",
    "Döviz İşlemleri",
    "Mevduat",
]

RENKLER = {
    "İstikrarlı": "#16A085",
    "İzleme": "#F2B84B",
    "İnceleme gerekli": "#E76F6F",
}

# Yalnızca prototipte kullanılan örnek uyarı eşikleri.
HACIM_ESIGI = -30
BAKIYE_ESIGI = -30


# ============================================================
# GÖRSEL TASARIM
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #F4F7FC;
        color: #14243A;
    }

    [data-testid="stSidebar"] {
        background: #14243A;
    }

    [data-testid="stSidebar"] * {
        color: #F0F5FF;
    }

    .hero {
        background: linear-gradient(115deg, #14243A, #214C78);
        padding: 30px 34px;
        border-radius: 18px;
        color: white;
        margin-bottom: 22px;
    }

    .hero-title {
        font-size: 35px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #D8E8FA;
        font-size: 15px;
    }

    .hero-tag {
        display: inline-block;
        background: #2C608B;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 12px;
        margin-bottom: 12px;
        color: white;
    }

    .section-title {
        font-size: 23px;
        font-weight: 750;
        color: #14243A;
        margin: 16px 0;
    }

    .info-box {
        background: white;
        border: 1px solid #E1E8F2;
        border-radius: 14px;
        padding: 19px 21px;
        margin: 12px 0;
        color: #263A53;
        line-height: 1.65;
    }

    .ai-box {
        background: #EDF3FF;
        border-left: 5px solid #5266D9;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        color: #24345A;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2EAF4;
        border-radius: 15px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(20, 36, 58, 0.035);
    }

    div[data-testid="stMetricLabel"] {
        color: #52657D;
    }

    div[data-testid="stMetricValue"] {
        color: #14243A;
    }

    div.stButton > button[kind="primary"] {
        background: #21588A;
        border: none;
        border-radius: 10px;
        color: white;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #173F68;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def baslik(metin):
    st.markdown(
        f'<div class="section-title">{metin}</div>',
        unsafe_allow_html=True,
    )


def bilgi_kutusu(metin):
    st.markdown(
        f'<div class="info-box">{metin}</div>',
        unsafe_allow_html=True,
    )


def tl(deger):
    return f"{deger:,.0f} TL".replace(",", ".")


def yuzde(deger):
    return f"%{abs(deger):.1f}".replace(".", ",")


def degisim_yazisi(deger):
    isaret = "+" if deger > 0 else ""
    return f"{isaret}{deger:.1f}%".replace(".", ",")


def yuzde_degisim(eski, yeni):
    if eski == 0:
        return 0.0 if yeni == 0 else None

    return (yeni - eski) / eski * 100


def urunleri_ayir(metin):
    if pd.isna(metin):
        return []

    return [
        urun.strip()
        for urun in str(metin).split(",")
        if urun.strip()
    ]


# ============================================================
# VERİYİ OKUMA VE ANALİZ
# ============================================================

@st.cache_data
def veriyi_yukle():
    df = pd.read_csv(VERI_DOSYASI, encoding="utf-8-sig")

    sayisal_alanlar = [
        "ay_no",
        "islem_hacmi",
        "ortalama_bakiye",
        "aktif_urun_sayisi",
    ]

    for alan in sayisal_alanlar:
        df[alan] = pd.to_numeric(df[alan], errors="coerce")

    df = df.dropna(subset=sayisal_alanlar)

    return df.sort_values(["musteri_kodu", "ay_no"])


def portfoy_ozeti_olustur(df):
    satirlar = []

    for musteri_kodu, grup in df.groupby("musteri_kodu"):
        grup = grup.sort_values("ay_no")

        onceki = grup[grup["ay_no"].between(1, 3)]
        guncel = grup[grup["ay_no"].between(4, 6)]

        if len(onceki) != 3 or len(guncel) != 3:
            continue

        ilk = grup.iloc[0]
        son = grup.iloc[-1]

        eski_hacim = onceki["islem_hacmi"].mean()
        yeni_hacim = guncel["islem_hacmi"].mean()

        eski_bakiye = onceki["ortalama_bakiye"].mean()
        yeni_bakiye = guncel["ortalama_bakiye"].mean()

        hacim_degisim = yuzde_degisim(eski_hacim, yeni_hacim)
        bakiye_degisim = yuzde_degisim(eski_bakiye, yeni_bakiye)

        eski_urunler = set(urunleri_ayir(ilk["aktif_urunler"]))
        yeni_urunler = set(urunleri_ayir(son["aktif_urunler"]))

        kaybolan_urunler = sorted(eski_urunler - yeni_urunler)

        uyari_hacim = (
            hacim_degisim is not None
            and hacim_degisim <= HACIM_ESIGI
        )

        uyari_bakiye = (
            bakiye_degisim is not None
            and bakiye_degisim <= BAKIYE_ESIGI
        )

        uyari_urun = len(kaybolan_urunler) > 0

        uyari_sayisi = sum(
            [uyari_hacim, uyari_bakiye, uyari_urun]
        )

        if uyari_sayisi >= 2:
            durum = "İnceleme gerekli"
        elif uyari_sayisi == 1:
            durum = "İzleme"
        else:
            durum = "İstikrarlı"

        gerekceler = []

        if uyari_hacim:
            gerekceler.append(
                f"İşlem hacmi {yuzde(hacim_degisim)} azaldı"
            )

        if uyari_bakiye:
            gerekceler.append(
                f"Ortalama bakiye {yuzde(bakiye_degisim)} azaldı"
            )

        if uyari_urun:
            gerekceler.append(
                "Ürün kullanımından çıkan: "
                + ", ".join(kaybolan_urunler)
            )

        satirlar.append(
            {
                "musteri_kodu": musteri_kodu,
                "firma_adi": son["firma_adi"],
                "sektor": son["sektor"],
                "segment": son["segment"],
                "onceki_hacim": eski_hacim,
                "guncel_hacim": yeni_hacim,
                "hacim_degisim": hacim_degisim,
                "onceki_bakiye": eski_bakiye,
                "guncel_bakiye": yeni_bakiye,
                "bakiye_degisim": bakiye_degisim,
                "onceki_urun_sayisi": len(eski_urunler),
                "aktif_urun_sayisi": len(yeni_urunler),
                "aktif_urunler": ", ".join(sorted(yeni_urunler)),
                "kaybolan_urunler": ", ".join(kaybolan_urunler),
                "uyari_sayisi": uyari_sayisi,
                "durum": durum,
                "gerekceler": (
                    " | ".join(gerekceler)
                    if gerekceler
                    else "Tanımlı uyarı eşiği aşılmadı"
                ),
            }
        )

    return pd.DataFrame(satirlar)


def firsatlari_bul(musteri):
    """
    Kural tabanlı, yalnızca görüşmede araştırılabilecek
    ürün fırsatları. Satış veya uygunluk kararı değildir.
    """

    mevcut = set(urunleri_ayir(musteri["aktif_urunler"]))
    sektor = musteri["sektor"]

    firsatlar = []

    if sektor == "Perakende" and "POS" not in mevcut:
        firsatlar.append(
            {
                "urun": "POS",
                "gerekce": (
                    "Müşteri perakende sektöründe faaliyet gösteriyor "
                    "ve güncel ürün listesinde POS bulunmuyor."
                ),
                "soru": (
                    "Kartlı satış yapıyor musunuz? "
                    "Mevcut POS kullanımınız ve ihtiyaçlarınız nelerdir?"
                ),
            }
        )

    if sektor == "Dış Ticaret" and "Döviz İşlemleri" not in mevcut:
        firsatlar.append(
            {
                "urun": "Döviz İşlemleri",
                "gerekce": (
                    "Müşteri dış ticaret sektöründe faaliyet gösteriyor "
                    "ve güncel ürün listesinde döviz işlemleri bulunmuyor."
                ),
                "soru": (
                    "Döviz işlemlerinizi hangi kanallardan "
                    "gerçekleştiriyorsunuz? Mevcut ihtiyaçlarınız nelerdir?"
                ),
            }
        )

    if sektor == "İnşaat" and "Teminat Mektubu" not in mevcut:
        firsatlar.append(
            {
                "urun": "Teminat Mektubu",
                "gerekce": (
                    "Müşteri inşaat sektöründe faaliyet gösteriyor "
                    "ve güncel ürün listesinde teminat mektubu bulunmuyor."
                ),
                "soru": (
                    "Devam eden projelerinizde veya sözleşmelerinizde "
                    "teminat mektubu ihtiyacınız oluyor mu?"
                ),
            }
        )

    return firsatlar


# ============================================================
# YEREL AI BAĞLANTISI
# ============================================================

def yerel_ai_analizi(musteri, firsatlar):
    """
    Ollama bilgisayarda çalışıyorsa seçili müşterinin
    özetini yerel modele gönderir.

    Modelden gelen metin doğrulanmış bankacılık
    değerlendirmesi olarak kullanılmamalıdır.
    """

    firsat_metni = "\n".join(
        f"- {f['urun']}: {f['gerekce']}"
        for f in firsatlar
    )

    if not firsat_metni:
        firsat_metni = (
            "Tanımlı kurallara göre belirgin bir ek ürün "
            "görüşme fırsatı bulunmadı."
        )

    hacim = degisim_yazisi(musteri["hacim_degisim"])
    bakiye = degisim_yazisi(musteri["bakiye_degisim"])

    prompt = f"""
Sen ticari bankacılık için görüşme hazırlığı yapan
Türkçe bir yapay zekâ asistanısın.

Yalnızca aşağıdaki sentetik müşteri verilerini kullan.

Müşteri: {musteri['firma_adi']}
Sektör: {musteri['sektor']}
Segment: {musteri['segment']}

İşlem hacmi değişimi: {hacim}
Ortalama bakiye değişimi: {bakiye}

Önceki ürün sayısı: {musteri['onceki_urun_sayisi']}
Güncel ürün sayısı: {musteri['aktif_urun_sayisi']}

Güncel ürünler: {musteri['aktif_urunler']}
Uyarı gerekçeleri: {musteri['gerekceler']}

Araştırılabilecek ürün fırsatları:
{firsat_metni}

Türkçe ve kısa bir rapor hazırla.

Şu başlıkları kullan:

İLİŞKİ ÖZETİ:
Verilen rakamları doğru kullanarak ilişki değişimini açıkla.

GÖRÜŞME HAZIRLIĞI:
Müşteriye sorulabilecek iki somut soru yaz.

DERİNLEŞME:
Yalnızca verilen fırsatları değerlendir.
Fırsat yoksa bunu belirt.

Müşterinin bankadan ayrıldığını iddia etme.
Kredi veya ürün uygunluğu kararı verme.
Verilmeyen müşteri bilgilerini uydurma.
Yüzdeleri değiştirme.
"""

    cevap = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "qwen2.5:0.5b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 350,
                "num_ctx": 2048,
            },
            "keep_alive": "0",
        },
        timeout=120,
    )

    cevap.raise_for_status()

    return cevap.json().get("response", "").strip()


# ============================================================
# VERİYİ HAZIRLA
# ============================================================

if not VERI_DOSYASI.exists():
    st.error(
        "musteri_portfoyu.csv bulunamadı. "
        "Önce veri_uret.py dosyasını çalıştır."
    )
    st.stop()

try:
    veri = veriyi_yukle()
    portfoy = portfoy_ozeti_olustur(veri)
except Exception as hata:
    st.error(f"Veri hazırlanırken hata oluştu: {hata}")
    st.stop()

if portfoy.empty:
    st.error("Analiz edilebilecek müşteri verisi bulunamadı.")
    st.stop()


# ============================================================
# SOL MENÜ
# ============================================================

with st.sidebar:
    st.markdown("## 🏦 Müşteri 360°")
    st.caption("AI Relationship Intelligence")

    st.divider()

    sayfa = st.radio(
        "MENÜ",
        [
            "📊 Yönetici Kokpiti",
            "👤 Müşteri 360°",
            "✨ AI Portföy Asistanı",
            "🎯 Derinleşme Merkezi",
            "📋 Aksiyon Merkezi",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    segment_secimi = st.multiselect(
        "Müşteri segmenti",
        ["KOBİ", "Ticari"],
        default=["KOBİ", "Ticari"],
    )

    sektorler = sorted(portfoy["sektor"].unique())

    sektor_secimi = st.multiselect(
        "Sektör",
        sektorler,
        default=sektorler,
    )

    st.divider()
    st.caption("🔒 Tamamen sentetik veri")
    st.caption("Yerel prototip · Sürüm 1.0")


filtreli = portfoy[
    portfoy["segment"].isin(segment_secimi)
    & portfoy["sektor"].isin(sektor_secimi)
].copy()

if filtreli.empty:
    st.warning("Seçtiğin filtrelere uygun müşteri bulunamadı.")
    st.stop()


# ============================================================
# ÜST BAŞLIK
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">AI RELATIONSHIP INTELLIGENCE</div>
        <div class="hero-title">Müşteri 360°</div>
        <div class="hero-subtitle">
            Ticari ve KOBİ müşterileri için ilişki sağlığı,
            erken uyarı ve derinleşme platformu
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 1. YÖNETİCİ KOKPİTİ
# ============================================================

if sayfa == "📊 Yönetici Kokpiti":

    baslik("Portföy Genel Görünümü")

    toplam = len(filtreli)

    inceleme = int(
        (filtreli["durum"] == "İnceleme gerekli").sum()
    )

    izleme = int(
        (filtreli["durum"] == "İzleme").sum()
    )

    ortalama_urun = filtreli["aktif_urun_sayisi"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Toplam Müşteri", f"{toplam:,}".replace(",", "."))
    c2.metric("İnceleme Gerekli", inceleme)
    c3.metric("İzleme Listesi", izleme)
    c4.metric("Ortalama Ürün Sayısı", f"{ortalama_urun:.1f}")

    st.write("")

    sol, sag = st.columns([1, 1.4])

    with sol:
        baslik("İlişki Sağlığı Dağılımı")

        dagilim = (
            filtreli["durum"]
            .value_counts()
            .reindex(
                ["İstikrarlı", "İzleme", "İnceleme gerekli"],
                fill_value=0,
            )
            .reset_index()
        )

        dagilim.columns = ["Durum", "Müşteri"]

        fig = px.pie(
            dagilim,
            names="Durum",
            values="Müşteri",
            hole=0.67,
            color="Durum",
            color_discrete_map=RENKLER,
        )

        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
        )

        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig, use_container_width=True)

    with sag:
        baslik("Sektörlere Göre Müşteri Sayısı")

        sektor_grafik = (
            filtreli.groupby("sektor")
            .size()
            .reset_index(name="Müşteri")
            .sort_values("Müşteri", ascending=True)
        )

        fig = px.bar(
            sektor_grafik,
            x="Müşteri",
            y="sektor",
            orientation="h",
            color_discrete_sequence=["#21588A"],
            labels={"sektor": "Sektör"},
        )

        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig, use_container_width=True)

    baslik("Öncelikli İnceleme Listesi")

    oncelikli = filtreli[
        filtreli["durum"] == "İnceleme gerekli"
    ].sort_values(
        ["uyari_sayisi", "hacim_degisim"],
        ascending=[False, True],
    )

    st.dataframe(
        oncelikli[
            [
                "firma_adi",
                "sektor",
                "segment",
                "uyari_sayisi",
                "gerekceler",
            ]
        ].head(15),
        use_container_width=True,
        hide_index=True,
        column_config={
            "firma_adi": "Müşteri",
            "sektor": "Sektör",
            "segment": "Segment",
            "uyari_sayisi": "Uyarı Sayısı",
            "gerekceler": "İnceleme Gerekçesi",
        },
    )

    st.caption(
        "İlişki durumu, prototipte tanımlanan üç uyarı "
        "göstergesine dayanır. Müşteri kaybı olasılığı "
        "veya kredi risk derecesi değildir."
    )


# ============================================================
# MÜŞTERİ SEÇİMİ
# ============================================================

def musteri_sec():
    secenekler = filtreli.sort_values("firma_adi")

    kodlar = secenekler["musteri_kodu"].tolist()

    adlar = {
        satir["musteri_kodu"]: (
            f"{satir['firma_adi']} | "
            f"{satir['sektor']} | "
            f"{satir['durum']}"
        )
        for _, satir in secenekler.iterrows()
    }

    kod = st.selectbox(
        "Müşteri seç",
        kodlar,
        format_func=lambda x: adlar[x],
    )

    return filtreli[
        filtreli["musteri_kodu"] == kod
    ].iloc[0]


# ============================================================
# 2. MÜŞTERİ 360°
# ============================================================

if sayfa == "👤 Müşteri 360°":

    baslik("Müşteri Detay Analizi")

    musteri = musteri_sec()

    kod = musteri["musteri_kodu"]

    musteri_verisi = veri[
        veri["musteri_kodu"] == kod
    ].sort_values("ay_no")

    st.markdown(f"### {musteri['firma_adi']}")

    st.caption(
        f"{musteri['segment']} · {musteri['sektor']} · "
        f"Müşteri Kodu: {kod}"
    )

    st.info(f"İlişki durumu: {musteri['durum']}")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Ortalama İşlem Hacmi",
        tl(musteri["guncel_hacim"]),
        degisim_yazisi(musteri["hacim_degisim"]),
    )

    c2.metric(
        "Ortalama Hesap Bakiyesi",
        tl(musteri["guncel_bakiye"]),
        degisim_yazisi(musteri["bakiye_degisim"]),
    )

    c3.metric(
        "Aktif Ürün Sayısı",
        int(musteri["aktif_urun_sayisi"]),
        int(
            musteri["aktif_urun_sayisi"]
            - musteri["onceki_urun_sayisi"]
        ),
    )

    baslik("Altı Aylık Müşteri Eğilimleri")

    sol, sag = st.columns(2)

    with sol:
        fig = px.line(
            musteri_verisi,
            x="ay_no",
            y="islem_hacmi",
            markers=True,
            title="Aylık İşlem Hacmi",
            color_discrete_sequence=["#21588A"],
        )

        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=list(AYLAR.keys()),
                ticktext=list(AYLAR.values()),
                title="",
            ),
            yaxis_title="TL",
            height=340,
        )

        st.plotly_chart(fig, use_container_width=True)

    with sag:
        fig = px.line(
            musteri_verisi,
            x="ay_no",
            y="ortalama_bakiye",
            markers=True,
            title="Aylık Ortalama Bakiye",
            color_discrete_sequence=["#16A085"],
        )

        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=list(AYLAR.keys()),
                ticktext=list(AYLAR.values()),
                title="",
            ),
            yaxis_title="TL",
            height=340,
        )

        st.plotly_chart(fig, use_container_width=True)

    baslik("Ürün Kullanımı")

    fig = px.bar(
        musteri_verisi,
        x="ay_no",
        y="aktif_urun_sayisi",
        title="Aylık Aktif Ürün Sayısı",
        color_discrete_sequence=["#6585D8"],
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(AYLAR.keys()),
            ticktext=list(AYLAR.values()),
            title="",
        ),
        yaxis=dict(
            title="Aktif Ürün",
            dtick=1,
            rangemode="tozero",
        ),
        height=310,
    )

    st.plotly_chart(fig, use_container_width=True)

    bilgi_kutusu(
        "<b>Güncel aktif ürünler:</b><br>"
        + musteri["aktif_urunler"]
    )

    baslik("Erken Uyarı Göstergeleri")

    st.write(musteri["gerekceler"])

    st.caption(
        "Düşüşler müşteri kaybının kanıtı değildir. "
        "Mevsimsellik, faaliyet değişimi ve diğer nedenler "
        "müşteri görüşmesinde araştırılmalıdır."
    )


# ============================================================
# 3. AI PORTFÖY ASİSTANI
# ============================================================

if sayfa == "✨ AI Portföy Asistanı":

    baslik("Yerel Yapay Zekâ ile Müşteri Analizi")

    st.caption(
        "Deneysel özellik · Ollama ve qwen2.5:0.5b modeli"
    )

    musteri = musteri_sec()

    firsatlar = firsatlari_bul(musteri)

    st.markdown(f"### {musteri['firma_adi']}")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "İşlem Hacmi Değişimi",
        degisim_yazisi(musteri["hacim_degisim"]),
    )

    c2.metric(
        "Bakiye Değişimi",
        degisim_yazisi(musteri["bakiye_degisim"]),
    )

    c3.metric(
        "Aktif Ürün",
        int(musteri["aktif_urun_sayisi"]),
    )

    bilgi_kutusu(
        "<b>Python tarafından hesaplanan uyarılar:</b><br>"
        + musteri["gerekceler"]
    )

    st.markdown(
        """
        <div class="ai-box">
            <b>✨ AI Portföy Asistanı</b><br><br>
            Yerel yapay zekâ, seçilen müşterinin analiz
            sonuçlarını kullanarak Türkçe görüşme hazırlığı
            oluşturmaya çalışır.
            <br><br>
            Modelin çıktısı deneysel niteliktedir.
            Rakamlar ve öneriler kontrol edilmelidir.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ AI Analizi Oluştur",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner(
            "Yerel yapay zekâ müşteri analizini hazırlıyor..."
        ):
            try:
                yanit = yerel_ai_analizi(musteri, firsatlar)

                if yanit:
                    st.markdown("### AI Görüşme Hazırlığı")
                    st.write(yanit)

                    st.warning(
                        "Bu metin küçük bir yerel dil modeli "
                        "tarafından üretilmiştir. Model hatalı "
                        "rakamlar veya desteklenmeyen yorumlar "
                        "üretebilir. Yukarıdaki Python "
                        "hesaplamalarını esas al."
                    )
                else:
                    st.warning(
                        "Model boş yanıt verdi. "
                        "Lütfen tekrar dene."
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Ollama bağlantısı kurulamadı. "
                    "Ollama uygulamasının açık olduğundan "
                    "emin ol. Diğer ekranları kullanmaya "
                    "devam edebilirsin."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "Yerel AI zamanında yanıt vermedi. "
                    "Bilgisayarın belleği veya modelin "
                    "çalışma hızı yetersiz olabilir."
                )

            except requests.exceptions.RequestException as hata:
                st.error(
                    "Yerel AI isteği tamamlanamadı. "
                    "Ollama'da qwen2.5:0.5b modelinin "
                    "kurulu olduğunu kontrol et."
                )
                st.caption(str(hata))

            except Exception as hata:
                st.error("AI yanıtı işlenirken hata oluştu.")
                st.caption(str(hata))

    st.divider()

    st.markdown("### Doğrulanabilir Görüşme Konuları")

    st.write(
        "İşlem hacmi değişiminin nedenleri ve müşterinin "
        "güncel faaliyet durumu araştırılabilir."
    )

    st.write(
        "Ortalama bakiye değişiminin nedenleri ve "
        "nakit yönetimi ihtiyaçları görüşülebilir."
    )

    if musteri["kaybolan_urunler"]:
        st.write(
            "Kullanımı sona eren ürünler hakkında "
            "müşterinin mevcut ihtiyaçları sorulabilir."
        )


# ============================================================
# 4. DERİNLEŞME MERKEZİ
# ============================================================

if sayfa == "🎯 Derinleşme Merkezi":

    baslik("Müşteri Derinleşme Fırsatları")

    st.caption(
        "Fırsatlar sektör ve güncel ürün listesine dayalı "
        "örnek iş kurallarıyla belirlenir. "
        "Ürün ihtiyacı veya satış olasılığı tahmini değildir."
    )

    musteri = musteri_sec()

    st.markdown(f"### {musteri['firma_adi']}")

    bilgi_kutusu(
        "<b>Sektör:</b> "
        + musteri["sektor"]
        + "<br><b>Mevcut ürünler:</b> "
        + musteri["aktif_urunler"]
    )

    firsatlar = firsatlari_bul(musteri)

    if not firsatlar:
        st.info(
            "Tanımlı kurallara göre bu müşteri için "
            "belirgin bir ek ürün görüşme fırsatı bulunmadı."
        )

    for firsat in firsatlar:
        with st.container(border=True):
            st.markdown(f"### 🎯 {firsat['urun']}")

            st.write("**Fırsat gerekçesi**")
            st.write(firsat["gerekce"])

            st.write("**Müşteri görüşmesinde sorulabilecek soru**")
            st.write(firsat["soru"])

            st.caption(
                "Müşterinin gerçek ihtiyacı ve ürün uygunluğu "
                "ayrıca değerlendirilmelidir."
            )

    st.divider()

    baslik("Portföy Genelinde Fırsat Görünümü")

    firsat_satirlari = []

    for _, satir in filtreli.iterrows():
        for firsat in firsatlari_bul(satir):
            firsat_satirlari.append(
                {
                    "Müşteri": satir["firma_adi"],
                    "Sektör": satir["sektor"],
                    "Ürün": firsat["urun"],
                    "Gerekçe": firsat["gerekce"],
                }
            )

    if firsat_satirlari:
        firsat_df = pd.DataFrame(firsat_satirlari)

        st.metric(
            "İncelenebilecek Müşteri Sayısı",
            firsat_df["Müşteri"].nunique(),
        )

        st.dataframe(
            firsat_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "Seçili portföyde tanımlı kurallara uygun "
            "fırsat bulunamadı."
        )


# ============================================================
# 5. AKSİYON MERKEZİ
# ============================================================

if sayfa == "📋 Aksiyon Merkezi":

    baslik("Portföy Aksiyon Merkezi")

    st.caption(
        "Bu liste portföy yöneticisinin incelemesi için "
        "hazırlanmıştır. Otomatik müşteri iletişimi veya "
        "ürün kararı oluşturmaz."
    )

    durum_secimi = st.multiselect(
        "İlişki durumu",
        ["İnceleme gerekli", "İzleme", "İstikrarlı"],
        default=["İnceleme gerekli", "İzleme"],
    )

    aksiyon = filtreli[
        filtreli["durum"].isin(durum_secimi)
    ].copy()

    aksiyon = aksiyon.sort_values(
        ["uyari_sayisi", "hacim_degisim"],
        ascending=[False, True],
    )

    st.metric(
        "Listelenen Müşteri",
        len(aksiyon),
    )

    aksiyon["Görüşme Konusu"] = (
        "İlişki değişimlerinin nedenleri ve "
        "güncel bankacılık ihtiyaçları"
    )

    gorunum = aksiyon[
        [
            "musteri_kodu",
            "firma_adi",
            "sektor",
            "durum",
            "uyari_sayisi",
            "gerekceler",
            "Görüşme Konusu",
        ]
    ].rename(
        columns={
            "musteri_kodu": "Müşteri Kodu",
            "firma_adi": "Müşteri",
            "sektor": "Sektör",
            "durum": "İlişki Durumu",
            "uyari_sayisi": "Uyarı Sayısı",
            "gerekceler": "İnceleme Gerekçesi",
        }
    )

    st.dataframe(
        gorunum,
        use_container_width=True,
        hide_index=True,
    )

    csv_verisi = gorunum.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Aksiyon Listesini CSV Olarak İndir",
        data=csv_verisi,
        file_name="musteri_360_aksiyon_listesi.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()

    baslik("Görüşme Notu")

    secenekler = aksiyon["musteri_kodu"].tolist()

    if secenekler:
        secilen_kod = st.selectbox(
            "Not hazırlanacak müşteri",
            secenekler,
            format_func=lambda kod: aksiyon.loc[
                aksiyon["musteri_kodu"] == kod,
                "firma_adi",
            ].iloc[0],
        )

        not_metni = st.text_area(
            "Görüşme hazırlığı / not",
            placeholder=(
                "Müşteriyle görüşmede araştırılacak "
                "konuları buraya yazabilirsin..."
            ),
            height=130,
        )

        if not_metni.strip():
            st.download_button(
                "📝 Görüşme Notunu İndir",
                data=not_metni.encode("utf-8-sig"),
                file_name=f"{secilen_kod}_gorusme_notu.txt",
                mime="text/plain",
            )

        st.caption(
            "Notlar bu prototipte otomatik olarak "
            "kaydedilmez. Saklamak istediğin notu indir."
        )

    else:
        st.info(
            "Seçilen ilişki durumunda müşteri bulunamadı."
        )


# ============================================================
# ALT BİLGİ
# ============================================================

st.divider()

st.caption(
    "Müşteri 360° | AI Relationship Intelligence · "
    "Sentetik veriyle geliştirilmiş portföy analizi prototipi. "
    "Gerçek banka verisi, doğrulanmış müşteri kaybı tahmini "
    "veya otomatik bankacılık kararı içermez."
)