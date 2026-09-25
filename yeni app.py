
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# MÜŞTERİ 360° | ÜRÜN ODAKLI ANALİZ
# Yalnızca sentetik demo verileriyle çalışır.
# ============================================================

st.set_page_config(
    page_title="Müşteri 360°",
    page_icon="🏦",
    layout="wide",
)

KLASOR = Path(__file__).resolve().parent
CSV_DOSYASI = KLASOR / "musteri_portfoyu.csv"
NOT_DOSYASI = KLASOR / "demo_gorusme_notlari.json"

URUNLER = [
    "Ticari Kredi",
    "POS",
    "Teminat Mektubu",
    "Döviz İşlemleri",
    "Mevduat",
]

GENEL_SORULAR = {
    "Ticari Kredi":
        "İşletme sermayesi veya yatırım finansmanı ihtiyacınız oluyor mu?",
    "POS":
        "Kartlı tahsilat yapıyor musunuz? Mevcut ödeme yöntemleriniz yeterli mi?",
    "Teminat Mektubu":
        "İhale veya sözleşmelerinizde banka teminatına ihtiyaç oluyor mu?",
    "Döviz İşlemleri":
        "Döviz cinsinden tahsilat veya ödeme yapıyor musunuz?",
    "Mevduat":
        "İşletmenizin dönemsel nakit fazlasını nasıl değerlendiriyorsunuz?",
}

SEKTOR_SORULARI = {
    "Perakende": {
        "POS":
            "Mağaza ve internet satışlarınızda kartlı tahsilatı nasıl yönetiyorsunuz?",
    },
    "Dış Ticaret": {
        "Döviz İşlemleri":
            "İthalat ve ihracat ödemelerinizi hangi para birimleriyle yapıyorsunuz?",
    },
    "İnşaat": {
        "Teminat Mektubu":
            "Devam eden projelerinizde ihale veya sözleşme teminatına ihtiyaç oluyor mu?",
    },
    "İmalat": {
        "Ticari Kredi":
            "Hammadde alımı ile satış tahsilatı arasında finansman ihtiyacı oluşuyor mu?",
    },
    "Lojistik": {
        "Döviz İşlemleri":
            "Uluslararası taşımacılıktan kaynaklanan döviz tahsilatınız veya ödemeniz var mı?",
    },
    "Tekstil": {
        "Döviz İşlemleri":
            "Yurt dışı satış veya hammadde alımlarınızda döviz işlemi yapıyor musunuz?",
    },
    "Gıda": {
        "Ticari Kredi":
            "Mevsimsel stok ve tedarik dönemlerinde finansman ihtiyacınız değişiyor mu?",
    },
    "Hizmet": {
        "POS":
            "Hizmet bedellerinizi müşterilerinizden hangi yöntemlerle tahsil ediyorsunuz?",
    },
}


# ============================================================
# RENK VE GÖRÜNÜM
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f8ff;
        color: #17283e;
    }

    [data-testid="stSidebar"] {
        background: #1c2d42;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown * {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d7e2f0;
        border-radius: 12px;
        padding: 15px;
    }

    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"] * {
        color: #17283e !important;
        opacity: 1 !important;
    }

    /* Ana sayfadaki metin kutuları ve seçim alanları */
    [data-testid="stMain"] input,
    [data-testid="stMain"] textarea,
    [data-testid="stMain"] [data-baseweb="select"] input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] input::placeholder,
    [data-testid="stMain"] textarea::placeholder {
        color: #c7d1e1 !important;
        -webkit-text-fill-color: #c7d1e1 !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] [data-baseweb="input"],
    [data-testid="stMain"] [data-baseweb="textarea"],
    [data-testid="stMain"] [data-baseweb="select"] > div {
        background: #252933 !important;
        color: #ffffff !important;
    }

    [data-testid="stMain"] [data-baseweb="select"] span,
    [data-testid="stMain"] [data-baseweb="select"] div {
        color: #ffffff !important;
    }

    /* Açık zeminli bilgi kutularında okunabilir yazı */
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div {
        color: #17283e !important;
        opacity: 1 !important;
    }

    /* Metin alanı ve müşteri arama etiketleri */
    [data-testid="stMain"] label,
    [data-testid="stMain"] label p,
    [data-testid="stMain"] label span {
        color: #17283e !important;
        opacity: 1 !important;
    }

    .hero {
        background: #1c2d42;
        padding: 23px;
        border-radius: 14px;
        margin-bottom: 20px;
    }

    .hero h1,
    .hero p {
        color: #ffffff !important;
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
    }

    .urun-karti {
        background: #ffffff;
        border: 1px solid #d7e2f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
        min-height: 100px;
    }

    .urun-karti h4,
    .urun-karti p {
        color: #17283e !important;
        margin: 0 0 8px 0;
    }

    .kayitli-not {
        background: #ffffff;
        border: 2px solid #7ca5d1;
        border-radius: 12px;
        padding: 18px;
        margin: 12px 0;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        color: #17283e !important;
        font-size: 16px;
        line-height: 1.6;
    }

    .kayitli-not * {
        color: #17283e !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# VERİ
# ============================================================

def urunleri_ayir(deger):
    if pd.isna(deger):
        return set()

    return {
        parca.strip()
        for parca in str(deger).split(",")
        if parca.strip()
    }


@st.cache_data
def veriyi_oku():
    d = pd.read_csv(
        CSV_DOSYASI,
        encoding="utf-8-sig",
        dtype={"musteri_kodu": str},
    )

    gerekli = {
        "musteri_kodu",
        "firma_adi",
        "sektor",
        "segment",
        "ay_no",
        "aktif_urunler",
    }

    eksik = gerekli - set(d.columns)

    if eksik:
        raise ValueError(
            "CSV dosyasında eksik sütunlar: "
            + ", ".join(sorted(eksik))
        )

    d["ay_no"] = pd.to_numeric(
        d["ay_no"],
        errors="coerce",
    )

    d = d.dropna(subset=["ay_no"])

    son = (
        d.sort_values(["musteri_kodu", "ay_no"])
        .drop_duplicates(
            subset="musteri_kodu",
            keep="last",
        )
        .copy()
    )

    son["mevcut_urunler"] = son["aktif_urunler"].apply(
        lambda x: [
            urun
            for urun in URUNLER
            if urun in urunleri_ayir(x)
        ]
    )

    son["eksik_urunler"] = son["mevcut_urunler"].apply(
        lambda mevcut: [
            urun
            for urun in URUNLER
            if urun not in mevcut
        ]
    )

    son["urun_sayisi"] = son["mevcut_urunler"].apply(len)

    return son.sort_values("musteri_kodu")


# ============================================================
# GÖRÜŞME SORULARI VE RAPOR
# ============================================================

def soru_uret(musteri, urun):
    sektor = musteri["sektor"]

    return SEKTOR_SORULARI.get(
        sektor, {}
    ).get(
        urun,
        GENEL_SORULAR[urun],
    )


def rapor_uret(musteri):
    mevcut = musteri["mevcut_urunler"]
    eksik = musteri["eksik_urunler"]

    satirlar = [
        "MÜŞTERİ 360° | MÜŞTERİYE ÖZEL GÖRÜŞME RAPORU",
        "",
        f"Firma: {musteri['firma_adi']}",
        f"Müşteri kodu: {musteri['musteri_kodu']}",
        f"Sektör: {musteri['sektor']}",
        f"Segment: {musteri['segment']}",
        "",
        "1. GÜNCEL ÜRÜN DURUMU",
        "",
        f"Kullanılan ürün sayısı: {len(mevcut)} / {len(URUNLER)}",
        "Kullanılan ürünler: "
        + (", ".join(mevcut) if mevcut else "Listelenen ürün yok"),
        "",
        "2. GÜNCEL LİSTEDE BULUNMAYAN ÜRÜNLER",
        "",
        (
            ", ".join(eksik)
            if eksik
            else "Tanımlı beş ürünün tamamı listede bulunuyor."
        ),
        "",
        "3. GÖRÜŞMEDE SORULABİLECEK SORULAR",
        "",
    ]

    if eksik:
        for sira, urun in enumerate(eksik, start=1):
            satirlar.append(
                f"{sira}. {urun}: {soru_uret(musteri, urun)}"
            )
    else:
        satirlar.append(
            "1. Mevcut bankacılık ürünlerinizde "
            "iyileştirilmesini istediğiniz bir işlem "
            "veya hizmet var mı?"
        )

    satirlar.extend(
        [
            "",
            "4. ÖNEMLİ NOT",
            "",
            "Bu rapor sentetik demo verisiyle hazırlanmıştır. "
            "Bir ürünün listede bulunmaması, müşterinin "
            "o ürüne ihtiyaç duyduğu veya ürüne uygun "
            "olduğu anlamına gelmez.",
        ]
    )

    return "\n".join(satirlar)


# ============================================================
# NOT KAYDETME VE GERİ GÖSTERME
# ============================================================

def notlari_oku():
    if not NOT_DOSYASI.exists():
        return {}

    try:
        with NOT_DOSYASI.open(
            "r",
            encoding="utf-8",
        ) as dosya:
            sonuc = json.load(dosya)

        return sonuc if isinstance(sonuc, dict) else {}

    except (OSError, json.JSONDecodeError):
        st.error(
            "Kayıtlı not dosyası okunamadı. "
            "Mevcut dosyayı silmeden önce kontrol et."
        )
        return {}


def notu_kaydet(kod, metin):
    tum_notlar = notlari_oku()

    tum_notlar[kod] = {
        "metin": metin,
        "kayit_zamani": datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        ),
    }

    gecici_dosya = NOT_DOSYASI.with_suffix(".tmp")

    with gecici_dosya.open(
        "w",
        encoding="utf-8",
    ) as dosya:
        json.dump(
            tum_notlar,
            dosya,
            ensure_ascii=False,
            indent=2,
        )

    gecici_dosya.replace(NOT_DOSYASI)


def not_bolumu(musteri):
    kod = musteri["musteri_kodu"]
    kayit = notlari_oku().get(kod, {})

    st.subheader("📝 Görüşme notu")

    st.write(
        "Bu alana yazdığın notu kaydedebilir, "
        "daha sonra aynı müşteriyi seçerek tekrar görebilirsin."
    )

    # Aynı müşterinin notu farklı sayfalarda da aynı kalır.
    alan_anahtari = f"not_metni_{kod}"

    if alan_anahtari not in st.session_state:
        st.session_state[alan_anahtari] = kayit.get(
            "metin", ""
        )

    metin = st.text_area(
        "Görüşme notunu buraya yaz",
        key=alan_anahtari,
        height=160,
        placeholder="Örnek: Müşteriyle POS ihtiyacı görüşülecek.",
    )

    if st.button(
        "💾 Görüşme notunu kaydet",
        key=f"not_kaydet_{kod}",
        type="primary",
    ):
        try:
            notu_kaydet(kod, metin)
            st.success("Görüşme notu kaydedildi.")
            kayit = notlari_oku().get(kod, {})

        except OSError as hata:
            st.error(f"Not kaydedilemedi: {hata}")

    st.markdown("#### 📌 Son kaydedilen görüşme notu")

    if kayit:
        st.caption(
            "Kayıt zamanı: "
            + kayit.get("kayit_zamani", "Bilinmiyor")
        )

        st.markdown(
            '<div class="kayitli-not">'
            + html_kacis(kayit.get("metin", ""))
            + "</div>",
            unsafe_allow_html=True,
        )

    else:
        st.info(
            "Bu müşteri için henüz kaydedilmiş görüşme notu yok."
        )

    st.caption(
        "Notlar proje klasöründeki "
        "demo_gorusme_notlari.json dosyasında saklanır. "
        "Gerçek müşteri veya gizli banka bilgisi yazma."
    )


def html_kacis(metin):
    import html
    return html.escape(str(metin))


# ============================================================
# MÜŞTERİ SEÇİMİ
# ============================================================

def musteri_sec(kaynak, sayfa_anahtari):
    arama = st.text_input(
        "Müşteri kodu veya firma adıyla ara",
        key=f"arama_{sayfa_anahtari}",
        placeholder="Örn. M0007",
    ).strip()

    if arama:
        uygun = kaynak[
            kaynak["musteri_kodu"].str.contains(
                arama,
                case=False,
                regex=False,
            )
            |
            kaynak["firma_adi"].str.contains(
                arama,
                case=False,
                regex=False,
            )
        ]
    else:
        uygun = kaynak

    if uygun.empty:
        st.warning("Bu aramayla eşleşen müşteri yok.")
        return None

    etiketler = {
        satir["musteri_kodu"]: (
            f"{satir['musteri_kodu']} | "
            f"{satir['firma_adi']} | "
            f"{satir['sektor']} | "
            f"{satir['urun_sayisi']}/5 ürün"
        )
        for _, satir in uygun.iterrows()
    }

    secilen_kod = st.selectbox(
        "Müşteri seç",
        list(etiketler),
        format_func=lambda kod: etiketler[kod],
        key=f"musteri_{sayfa_anahtari}",
    )

    return uygun.loc[
        uygun["musteri_kodu"].eq(secilen_kod)
    ].iloc[0]


# ============================================================
# ORTAK EKRAN PARÇALARI
# ============================================================

def urun_haritasi(musteri):
    mevcut = set(musteri["mevcut_urunler"])

    a, b, c = st.columns(3)

    a.metric(
        "Kullandığı ürün sayısı",
        f"{len(mevcut)} / 5",
    )

    b.metric(
        "Listede bulunmayan ürün",
        len(URUNLER) - len(mevcut),
    )

    c.metric(
        "Görüşme konusu",
        len(musteri["eksik_urunler"]),
    )

    st.subheader("Müşterinin ürün haritası")

    kolonlar = st.columns(3)

    for sira, urun in enumerate(URUNLER):
        kullaniliyor = urun in mevcut

        durum = (
            "✓ Güncel listede bulunuyor"
            if kullaniliyor
            else "○ Güncel listede bulunmuyor"
        )

        with kolonlar[sira % 3]:
            st.markdown(
                '<div class="urun-karti">'
                f"<h4>{html_kacis(urun)}</h4>"
                f"<p>{html_kacis(durum)}</p>"
                "</div>",
                unsafe_allow_html=True,
            )


def rapor_goster(musteri, anahtar):
    st.subheader("📄 Müşteriye özel görüşme raporu")

    rapor = rapor_uret(musteri)

    st.code(
        rapor,
        language=None,
    )

    st.download_button(
        "📥 Müşteri raporunu indir (.txt)",
        data=rapor.encode("utf-8-sig"),
        file_name=(
            f"{musteri['musteri_kodu']}_musteri_raporu.txt"
        ),
        mime="text/plain",
        key=f"rapor_indir_{anahtar}",
        use_container_width=True,
    )


def grafik_goster(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(color="#17283e", size=14),
        title_font=dict(color="#17283e", size=18),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=380,
        margin=dict(l=30, r=35, t=65, b=40),
        xaxis=dict(
            color="#17283e",
            tickfont=dict(color="#17283e"),
            title_font=dict(color="#17283e"),
        ),
        yaxis=dict(
            color="#17283e",
            tickfont=dict(color="#17283e"),
            title_font=dict(color="#17283e"),
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# UYGULAMAYI BAŞLAT
# ============================================================

if not CSV_DOSYASI.exists():
    st.error(
        "musteri_portfoyu.csv bulunamadı. "
        "CSV dosyasını yeni app.py ile aynı klasöre koy."
    )
    st.stop()

try:
    portfoy = veriyi_oku()

except Exception as hata:
    st.error(f"Veri okunamadı: {hata}")
    st.stop()

if portfoy.empty:
    st.error("Gösterilecek müşteri bulunamadı.")
    st.stop()


# ============================================================
# SOL MENÜ
# ============================================================

with st.sidebar:
    st.markdown("## 🏦 Müşteri 360°")
    st.caption("Ürün ve görüşme analizi")

    sayfa = st.radio(
        "MENÜ",
        [
            "📊 Yönetici Kokpiti",
            "👤 Müşteri 360°",
            "📄 Al Raporu",
            "✨ Görüşme Asistanı",
            "🎯 Derinleşme Merkezi",
            "📋 Aksiyon Merkezi",
        ],
    )

    st.divider()

    segmentler = st.multiselect(
        "Segment",
        sorted(portfoy["segment"].unique()),
        default=sorted(portfoy["segment"].unique()),
    )

    sektorler = st.multiselect(
        "Sektör",
        sorted(portfoy["sektor"].unique()),
        default=sorted(portfoy["sektor"].unique()),
    )

    st.divider()
    st.caption("🔒 Sentetik veri · Düzeltilmiş sürüm 4.0")


filtreli = portfoy[
    portfoy["segment"].isin(segmentler)
    &
    portfoy["sektor"].isin(sektorler)
].copy()

st.markdown(
    """
    <div class="hero">
        <h1>Müşteri 360°</h1>
        <p>Ürün analizi · Müşteri görüşmesi · Rapor ve not takibi</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtreli.empty:
    st.warning(
        "Filtrelere uygun müşteri yok. "
        "Sol menüden segment veya sektör seçimini genişlet."
    )
    st.stop()


# ============================================================
# 1. YÖNETİCİ KOKPİTİ
# ============================================================

if sayfa == "📊 Yönetici Kokpiti":
    st.header("Portföy ürün görünümü")

    a, b, c = st.columns(3)

    a.metric("Toplam müşteri", len(filtreli))

    b.metric(
        "Ortalama kullanılan ürün",
        f"{filtreli['urun_sayisi'].mean():.1f} / 5",
    )

    c.metric(
        "En az bir ürünü listede bulunmayan müşteri",
        int(filtreli["urun_sayisi"].lt(5).sum()),
    )

    satirlar = []

    for urun in URUNLER:
        kullanan = int(
            filtreli["mevcut_urunler"].apply(
                lambda liste: urun in liste
            ).sum()
        )

        satirlar.append(
            {
                "Ürün": urun,
                "Kullanan müşteri": kullanan,
                "Listede bulunmayan": len(filtreli) - kullanan,
            }
        )

    urun_tablosu = pd.DataFrame(satirlar)

    fig = px.bar(
        urun_tablosu,
        x="Kullanan müşteri",
        y="Ürün",
        orientation="h",
        text="Kullanan müşteri",
        title="Hangi ürünü kaç müşteri kullanıyor?",
        color_discrete_sequence=["#285b8b"],
    )

    fig.update_traces(textposition="outside")
    grafik_goster(fig)

    st.dataframe(
        urun_tablosu,
        hide_index=True,
        use_container_width=True,
    )

    dagilim = (
        filtreli["urun_sayisi"]
        .value_counts()
        .reindex(range(6), fill_value=0)
        .rename_axis("Ürün sayısı")
        .reset_index(name="Müşteri sayısı")
    )

    fig = px.bar(
        dagilim,
        x="Ürün sayısı",
        y="Müşteri sayısı",
        text="Müşteri sayısı",
        title="Müşteriler kaç ürün kullanıyor?",
        color_discrete_sequence=["#159b83"],
    )

    grafik_goster(fig)


# ============================================================
# 2. MÜŞTERİ 360°
# ============================================================

elif sayfa == "👤 Müşteri 360°":
    st.header("Müşteri detay ekranı")

    musteri = musteri_sec(filtreli, "detay")

    if musteri is not None:
        st.subheader(
            f"{musteri['firma_adi']} · "
            f"{musteri['musteri_kodu']}"
        )

        st.caption(
            f"{musteri['segment']} · {musteri['sektor']}"
        )

        urun_haritasi(musteri)

        st.subheader("Listede bulunmayan ürünler")

        if musteri["eksik_urunler"]:
            for urun in musteri["eksik_urunler"]:
                st.write(f"• {urun}")

        else:
            st.success(
                "Tanımlı beş ürünün tamamı listede bulunuyor."
            )

        st.info(
            "Müşteriye özel raporu görmek için "
            "soldaki 'Al Raporu' menüsünü açabilirsin."
        )


# ============================================================
# 3. AL RAPORU
# ============================================================

elif sayfa == "📄 Al Raporu":
    st.header("Müşteriye özel rapor")

    musteri = musteri_sec(filtreli, "rapor")

    if musteri is not None:
        st.write(
            f"**Seçilen müşteri:** "
            f"{musteri['firma_adi']} "
            f"({musteri['musteri_kodu']})"
        )

        rapor_goster(musteri, "rapor_sayfasi")


# ============================================================
# 4. GÖRÜŞME ASİSTANI
# ============================================================

elif sayfa == "✨ Görüşme Asistanı":
    st.header("Müşteri görüşme asistanı")

    st.write(
        "Bir müşteri seçtiğinde, güncel listesinde "
        "bulunmayan ürünler için görüşme soruları açılır."
    )

    musteri = musteri_sec(filtreli, "asistan")

    if musteri is not None:
        st.subheader(
            f"{musteri['firma_adi']} için görüşme hazırlığı"
        )

        urun_haritasi(musteri)

        st.subheader("Görüşmede araştırılabilecek konular")

        if musteri["eksik_urunler"]:
            for urun in musteri["eksik_urunler"]:
                with st.expander(
                    f"{urun} · Görüşme sorusunu aç",
                    expanded=True,
                ):
                    st.write(soru_uret(musteri, urun))

        else:
            st.success(
                "Beş ürünün tamamı listede bulunuyor. "
                "Mevcut ürünlerin kullanım deneyimi görüşülebilir."
            )

        not_bolumu(musteri)


# ============================================================
# 5. DERİNLEŞME MERKEZİ
# ============================================================

elif sayfa == "🎯 Derinleşme Merkezi":
    st.header("Ürün bazında müşteri araştırması")

    urun = st.selectbox(
        "İncelemek istediğin ürünü seç",
        URUNLER,
    )

    kullanmayan = filtreli[
        filtreli["mevcut_urunler"].apply(
            lambda liste: urun not in liste
        )
    ]

    st.metric(
        f"{urun} listesinde bulunmayan müşteri",
        len(kullanmayan),
    )

    satirlar = []

    for _, musteri in kullanmayan.iterrows():
        satirlar.append(
            {
                "Kod": musteri["musteri_kodu"],
                "Firma": musteri["firma_adi"],
                "Sektör": musteri["sektor"],
                "Mevcut ürün sayısı": musteri["urun_sayisi"],
                "Görüşme sorusu": soru_uret(musteri, urun),
            }
        )

    if satirlar:
        tablo = pd.DataFrame(satirlar)

        st.dataframe(
            tablo,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Görüşme sorusu": st.column_config.TextColumn(
                    "Görüşme sorusu",
                    width="large",
                ),
            },
        )

        st.download_button(
            "📥 Görüşme listesini indir",
            data=tablo.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="urun_gorusme_listesi.csv",
            mime="text/csv",
        )

    else:
        st.info(
            "Seçili portföyde bu ürünü listesinde "
            "bulundurmayan müşteri yok."
        )


# ============================================================
# 6. AKSİYON MERKEZİ
# ============================================================

elif sayfa == "📋 Aksiyon Merkezi":
    st.header("Görüşme notları ve aksiyonlar")

    musteri = musteri_sec(filtreli, "aksiyon")

    if musteri is not None:
        st.subheader(
            f"{musteri['firma_adi']} · "
            f"{musteri['musteri_kodu']}"
        )

        st.write(
            "**Görüşülebilecek ürünler:** "
            + (
                ", ".join(musteri["eksik_urunler"])
                if musteri["eksik_urunler"]
                else "Beş ürünün tamamı listede bulunuyor."
            )
        )

        not_bolumu(musteri)

        rapor_goster(musteri, "aksiyon_sayfasi")


# ============================================================
# ALT BİLGİ
# ============================================================

st.divider()

st.caption(
    "Müşteri 360° · Düzeltilmiş sürüm 4.0 · "
    "Yalnızca sentetik demo verisi kullanır. "
    "Gerçek müşteri bilgisi veya otomatik "
    "bankacılık kararı içermez."
)