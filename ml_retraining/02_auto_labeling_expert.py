import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Paths
BASE_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah"
INPUT_CSV = os.path.join(BASE_DIR, "ml_retraining", "data", "cleaned_data.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "ml_retraining", "data", "labeled_data.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "ml_retraining", "plots")

# ============================================================
# KRITERIA SKOR (Sistem Pakar Balittanah yang Diadaptasi)
# ============================================================

def score_N(N_mgkg):
    if N_mgkg < 100:    return 0
    elif N_mgkg <= 200: return 1
    else:               return 2

def score_P(P_mgkg):
    if P_mgkg < 100:    return 0
    elif P_mgkg <= 300: return 1
    else:               return 2

def score_K(K_mgkg):
    if K_mgkg < 100:    return 0
    elif K_mgkg <= 300: return 1
    else:               return 2

def score_OC(OC_pct):
    if OC_pct < 0.5:    return 0
    elif OC_pct <= 1.0: return 1
    else:               return 2

def score_pH(pH):
    if pH < 5.5 or pH > 7.5: return 0
    elif pH <= 6.5:          return 1
    else:                    return 2

def score_EC(EC_uscm):
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

def main():
    print("=" * 60)
    print(" TAHAP 2: AUTO-LABELING (EXPERT SYSTEM BALITTANAH)")
    print("=" * 60)

    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print("ERROR: File cleaned_data.csv tidak ditemukan!")
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
    df['Label_KMeans'] = df['Output'].map(LABEL_NAME) # Kita tetap pakai nama kolom Label_KMeans agar script 03 tidak rusak
    
    # Hapus kolom skor sementara
    cols_to_drop = ['skor_N', 'skor_P', 'skor_K', 'skor_OC', 'skor_pH', 'skor_EC', 'total_skor', 'Output']
    df.drop(columns=cols_to_drop, inplace=True)

    # Simpan hasil
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print("\n--- Distribusi Label Pakar ---")
    print(df['Label_KMeans'].value_counts())

    # Bikin Pie Chart Distribusi
    plt.figure(figsize=(8, 8))
    df['Label_KMeans'].value_counts().plot.pie(autopct='%1.1f%%', colors=['lightcoral', 'gold', 'lightgreen'])
    plt.title("Distribusi Label Kesuburan (Sistem Pakar Balittanah)")
    plt.ylabel("")
    pie_path = os.path.join(PLOTS_DIR, "expert_label_distribution.png")
    plt.savefig(pie_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\nBerhasil menyimpan data ke: {OUTPUT_CSV}")
    print(f"Gambar plot pie tersimpan di: {pie_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
