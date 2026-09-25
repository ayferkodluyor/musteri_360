from pathlib import Path

import numpy as np
import pandas as pd


# Müşteri 360° - Tamamen sentetik örnek veri üretimi
# Gerçek banka veya müşteri verisi içermez.

RNG = np.random.default_rng(42)
MUSTERI_SAYISI = 1000
AYLAR = ["Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül"]

SEKTORLER = [
    "Tekstil", "Perakende", "İnşaat", "Gıda",
    "İmalat", "Lojistik", "Dış Ticaret", "Hizmet"
]

URUNLER = [
    "Ticari Kredi",
    "POS",
    "Teminat Mektubu",
    "Döviz İşlemleri",
    "Mevduat",
]

SATIRLAR = []

for i in range(1, MUSTERI_SAYISI + 1):
    musteri_kodu = f"M{i:04d}"
    firma_adi = f"Örnek Firma {i:04d}"
    sektor = str(RNG.choice(SEKTORLER))
    segment = str(RNG.choice(["KOBİ", "Ticari"], p=[0.7, 0.3]))

    temel_hacim = float(RNG.uniform(150_000, 5_000_000))
    temel_bakiye = float(RNG.uniform(30_000, 1_500_000))

    # Bazı müşterilerde son üç ayda düşüş senaryosu oluşturulur.
    senaryo = str(
        RNG.choice(
            ["istikrarli", "hacim_dususu", "bakiye_dususu", "coklu_dusus"],
            p=[0.50, 0.17, 0.16, 0.17],
        )
    )

    ilk_urun_sayisi = int(RNG.integers(2, 6))
    aktif_urunler = list(
        RNG.choice(URUNLER, size=ilk_urun_sayisi, replace=False)
    )

    for ay_no, ay in enumerate(AYLAR):
        hacim_carpani = float(RNG.uniform(0.93, 1.07))
        bakiye_carpani = float(RNG.uniform(0.93, 1.07))

        if ay_no >= 3:
            if senaryo in ["hacim_dususu", "coklu_dusus"]:
                hacim_carpani *= 0.55

            if senaryo in ["bakiye_dususu", "coklu_dusus"]:
                bakiye_carpani *= 0.55

        # Çoklu düşüş senaryosunda ürün kullanımında da azalma.
        if ay_no == 3 and senaryo == "coklu_dusus":
            if len(aktif_urunler) > 1:
                aktif_urunler.pop()

        SATIRLAR.append(
            {
                "musteri_kodu": musteri_kodu,
                "firma_adi": firma_adi,
                "sektor": sektor,
                "segment": segment,
                "ay": ay,
                "ay_no": ay_no + 1,
                "islem_hacmi": round(temel_hacim * hacim_carpani, 2),
                "ortalama_bakiye": round(temel_bakiye * bakiye_carpani, 2),
                "aktif_urun_sayisi": len(aktif_urunler),
                "aktif_urunler": ", ".join(aktif_urunler),
            }
        )

df = pd.DataFrame(SATIRLAR)

dosya_yolu = Path(__file__).resolve().parent / "musteri_portfoyu.csv"
df.to_csv(dosya_yolu, index=False, encoding="utf-8-sig")

print("Müşteri 360° veri seti oluşturuldu.")
print(f"Müşteri sayısı: {df['musteri_kodu'].nunique()}")
print(f"Toplam veri satırı: {len(df)}")
print(f"Dosya: {dosya_yolu}")