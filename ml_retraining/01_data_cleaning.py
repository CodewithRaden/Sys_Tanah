import pandas as pd
import os

# Paths
BASE_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah"
INPUT_CSV = os.path.join(BASE_DIR, "soil_dataset.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "ml_retraining", "data", "cleaned_data.csv")

def main():
    print("=" * 50)
    print(" TAHAP 1: DATA CLEANING")
    print("=" * 50)

    # 1. Load Data
    print(f"Membaca data dari: {INPUT_CSV}")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print("ERROR: File soil_dataset.csv tidak ditemukan!")
        return

    print(f"Total baris awal: {len(df)}")
    print(f"Kolom awal: {list(df.columns)}")

    # 2. Hapus Kolom Lama (ai_label, recommendation)
    cols_to_drop = ['ai_label', 'recommendation']
    for col in cols_to_drop:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            print(f"-> Menghapus kolom '{col}' (Data lama tidak relevan)")

    # 3. Handle Missing Values pada Kolom Penting
    required_sensors = ['N', 'P', 'K', 'pH', 'EC', 'OC_est']
    # Memastikan kolom sensor ada
    missing_cols = [c for c in required_sensors if c not in df.columns]
    if missing_cols:
        print(f"ERROR: Kolom sensor ini tidak ada di dataset: {missing_cols}")
        return

    initial_len = len(df)
    df.dropna(subset=required_sensors, inplace=True)
    print(f"-> Menghapus {initial_len - len(df)} baris yang memiliki nilai kosong (NaN)")

    # 4. Filter nilai ekstrem (Anomali Sensor)
    # a. Sensor tercabut (Nilai N, P, K, atau EC = 0)
    # b. Sensor baru dicolok / belum stabil (pH terlalu ekstrem, misalnya < 4.0 atau > 8.5)
    
    # Simpan jumlah baris sebelum filter
    len_before = len(df)
    
    # Buang nilai 0 pada NPK karena tidak mungkin secara agronomi (pasti sensor tercabut)
    df = df[(df['N'] > 0) & (df['P'] > 0) & (df['K'] > 0)]
    
    # Buang pH anomali (baru dicolok biasanya melonjak ke 9 atau turun drastis)
    # Tanah sawah normal di Indonesia umumnya berada di rentang pH 4.0 - 8.0
    df = df[(df['pH'] >= 4.0) & (df['pH'] <= 8.5)]
    
    # Buang EC yang 0
    df = df[df['EC'] > 0]
    
    len_after = len(df)
    print(f"-> Menghapus {len_before - len_after} baris anomali (Sensor tercabut / baru dicolok)")
    print(f"-> Sisa baris bersih siap dilatih: {len_after}")

    # 5. Simpan Data Bersih
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Berhasil menyimpan data yang sudah bersih ke:\n{OUTPUT_CSV}")
    print("=" * 50)

if __name__ == "__main__":
    main()
