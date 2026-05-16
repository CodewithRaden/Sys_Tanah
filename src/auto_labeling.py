"""
Auto-Labeling Dataset Tanah Real
=================================
Memberi label kesuburan (0=Kurang Subur, 1=Subur, 2=Sangat Subur)
berdasarkan framework Balittanah/PPT Bogor 2009, dengan threshold
**diselaraskan** untuk output sensor digital NPK 7-in-1 via Modbus.

Sensor mengukur unsur hara *tersedia* (available, mg/kg), BUKAN
N-total atau P2O5/K2O ekstrak HCl seperti metode lab buku.

Justifikasi threshold (disesuaikan ke range sensor 7-in-1):
  N     : <100 / 100–200 / >200 mg/kg — adaptasi dari Balittanah 2009.
  P     : <100 / 100–300 / >300 mg/kg — sensor 7-in-1 mengukur
          P-available yang nilainya 10–100× lebih besar dari
          P2O5 (metode lab). Threshold disesuaikan agar ketiga kelas
          muncul secara proporsional pada data sensor.
  K     : <100 / 100–300 / >300 mg/kg — adaptasi dari Balittanah 2009.
  OC    : <0.5 / 0.5–1.0 / >1.0 %  — diturunkan karena estimasi OC
          via pedotransfer (rasio C/N + pH) menghasilkan range sempit.
  pH    : Langsung dari buku (tidak perlu konversi).
  EC    : Threshold salinitas umum dalam µS/cm (tidak ada di buku).

Sistem Skor:
  0 = Rendah, 1 = Sedang, 2 = Tinggi  (per parameter)
  Total 0–4  → 0 (Kurang Subur)
  Total 5–8  → 1 (Subur)
  Total 9–12 → 2 (Sangat Subur)

Input  : data/real_data_raw.csv
Output : data/real_data_labeled.csv
"""

import pandas as pd
import numpy as np
import os

INPUT_CSV  = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\data\real_data_raw.csv"
OUTPUT_CSV = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\data\real_data_labeled.csv"

# ============================================================
# KRITERIA SKOR
# Framework: Balittanah 2009 (diadaptasi ke range sensor digital)
# ============================================================

def score_N(N_mgkg):
    """
    N tersedia (mg/kg) — sensor 7-in-1.
    Ref framework: Balittanah 2009 (N Total), diadaptasi.
      < 100 mg/kg  → Rendah     (0)
      100–200      → Sedang     (1)
      > 200        → Tinggi     (2)
    """
    if N_mgkg < 100:    return 0
    elif N_mgkg <= 200: return 1
    else:               return 2

def score_P(P_mgkg):
    """
    P tersedia (mg/kg) — sensor 7-in-1.
    Sensor mengukur P-available → range jauh lebih tinggi dari P2O5 lab.
    Threshold diselaraskan dengan distribusi output sensor:
      < 100 mg/kg  → Rendah     (0)
      100–300      → Sedang     (1)
      > 300        → Tinggi     (2)
    """
    if P_mgkg < 100:    return 0
    elif P_mgkg <= 300: return 1
    else:               return 2

def score_K(K_mgkg):
    """
    K tersedia (mg/kg) — sensor 7-in-1.
    Ref framework: Balittanah 2009 (K2O HCl), diadaptasi.
      < 100 mg/kg  → Rendah     (0)
      100–300      → Sedang     (1)
      > 300        → Tinggi     (2)
    """
    if K_mgkg < 100:    return 0
    elif K_mgkg <= 300: return 1
    else:               return 2

def score_OC(OC_pct):
    """
    C-Organik / OC (%) — estimasi via pedotransfer (C/N + pH).
    Pedotransfer menghasilkan range sempit (~0.5–0.7%), sehingga
    threshold diturunkan agar klasifikasi tetap bermakna:
      < 0.5 %      → Rendah     (0)
      0.5–1.0 %    → Sedang     (1)
      > 1.0 %      → Tinggi     (2)
    """
    if OC_pct < 0.5:    return 0
    elif OC_pct <= 1.0: return 1
    else:               return 2

def score_pH(pH):
    """
    pH H2O — langsung dari buku Balittanah 2009.
      < 5.5 atau > 7.5  → Tidak optimal  (0)
      5.5 – 6.5         → Agak Masam     (1)
      6.6 – 7.5         → Netral/Optimal (2)
    """
    if pH < 5.5 or pH > 7.5: return 0
    elif pH <= 6.5:           return 1
    else:                     return 2

def score_EC(EC_uscm):
    """
    EC (us/cm) — threshold salinitas praktis.
      > 2000  → Salin tinggi   (0)
      800–2000→ Sedang         (1)
      < 800   → Baik           (2)
    """
    if EC_uscm > 2000:   return 0
    elif EC_uscm > 800:  return 1
    else:                return 2

def compute_label(row):
    total = (score_N(row['N'])
           + score_P(row['P'])
           + score_K(row['K'])
           + score_OC(row['OC_est'])
           + score_pH(row['pH'])
           + score_EC(row['EC']))
    if total <= 4:   return 0
    elif total <= 8: return 1
    else:            return 2

LABEL_NAME = {0: "Kurang Subur", 1: "Subur", 2: "Sangat Subur"}

# ============================================================
def main():
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: File tidak ditemukan:\n  {INPUT_CSV}")
        print("Jalankan dulu: python src/data_collector.py")
        return

    df = pd.read_csv(INPUT_CSV)
    print(f"Membaca {len(df)} sampel dari:\n  {INPUT_CSV}\n")

    required = ['N', 'P', 'K', 'pH', 'EC', 'OC_est']
    missing  = [c for c in required if c not in df.columns]
    if missing:
        print(f"ERROR: Kolom tidak ditemukan: {missing}")
        return

    # Hitung skor
    df['skor_N']   = df['N'].apply(score_N)
    df['skor_P']   = df['P'].apply(score_P)
    df['skor_K']   = df['K'].apply(score_K)
    df['skor_OC']  = df['OC_est'].apply(score_OC)
    df['skor_pH']  = df['pH'].apply(score_pH)
    df['skor_EC']  = df['EC'].apply(score_EC)
    df['total_skor'] = (df['skor_N'] + df['skor_P'] + df['skor_K']
                      + df['skor_OC']+ df['skor_pH']+ df['skor_EC'])

    df['Output'] = df.apply(compute_label, axis=1)
    df['Label']  = df['Output'].map(LABEL_NAME)

    # Simpan
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    # Laporan
    print("=" * 68)
    print(f"  AUTO-LABELING SELESAI — {len(df)} Sampel")
    print(f"  Ref: Balittanah 2009 (diadaptasi untuk sensor digital)")
    print("=" * 68)
    print(f"  {'No':>3}  {'Lokasi':<16}  "
          f"{'N':>5}  {'P':>5}  {'K':>5}  {'pH':>4}  {'EC':>5}  {'OC':>4}  "
          f"{'Skor':>4}  Label")
    print("  " + "-" * 66)
    for _, r in df.iterrows():
        print(f"  {int(r['no']):>3}  {str(r.get('lokasi','?')):<16}  "
              f"{r['N']:>5.0f}  {r['P']:>5.1f}  {r['K']:>5.0f}  "
              f"{r['pH']:>4.2f}  {r['EC']:>5.0f}  {r['OC_est']:>4.2f}  "
              f"{r['total_skor']:>4.0f}  {r['Label']}")

    print("\n--- Distribusi Label ---")
    for lbl_id in [0, 1, 2]:
        lbl_name = LABEL_NAME[lbl_id]
        cnt = (df['Output'] == lbl_id).sum()
        pct = cnt / len(df) * 100
        bar = "█" * int(pct / 5)
        print(f"  {lbl_name:<15}: {cnt:3d} ({pct:5.1f}%)  {bar}")

    # Peringatan distribusi tidak merata
    if df['Output'].nunique() < 3:
        print("\n  ⚠ PERHATIAN: Hanya", df['Output'].nunique(),
              "kelas yang muncul. Tambah variasi sampel tanah")
        print("    (campur tanah dari lokasi berbeda, tambah pupuk, dll)")

    print(f"\nFile tersimpan  : {OUTPUT_CSV}")
    print("Langkah berikut : python src/data_processing.py")

if __name__ == "__main__":
    main()
