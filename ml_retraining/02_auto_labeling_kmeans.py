import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Paths
BASE_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah"
INPUT_CSV = os.path.join(BASE_DIR, "ml_retraining", "data", "cleaned_data.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "ml_retraining", "data", "labeled_data.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "ml_retraining", "plots")

def main():
    print("=" * 50)
    print(" TAHAP 2: AUTO-LABELING DENGAN K-MEANS")
    print("=" * 50)

    # 1. Load Cleaned Data
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print("ERROR: File cleaned_data.csv tidak ditemukan!")
        return

    features = ['N', 'P', 'K', 'pH', 'EC', 'OC_est']
    X = df[features].copy()

    # 2. Standarisasi Fitur
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. K-Means Clustering (k=3)
    print("Menjalankan K-Means Clustering dengan k=3...")
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    # 4. Mengurutkan Cluster (Kurang Subur, Subur, Sangat Subur)
    # Kita lihat rata-rata nilai fitur tiap cluster untuk menentukan mana yang Kurang, Sedang, Tinggi
    cluster_means = df.groupby('Cluster')[features].mean()
    print("\nRata-rata nilai fitur per cluster:")
    print(cluster_means)

    # Menggunakan jumlah fitur yang distandarisasi untuk menentukan peringkat kesuburan
    # Tanah yang lebih subur secara umum punya N,P,K,OC yang lebih tinggi
    scaled_means = pd.DataFrame(scaler.transform(cluster_means), columns=features)
    # Membuat skor kesuburan kasar (misalnya jumlah N+P+K+OC)
    fertility_score = scaled_means['N'] + scaled_means['P'] + scaled_means['K'] + scaled_means['OC_est']
    
    # Urutkan berdasarkan skor kesuburan
    sorted_clusters = fertility_score.sort_values().index.tolist()
    
    label_map = {
        sorted_clusters[0]: "Kurang Subur",
        sorted_clusters[1]: "Subur",
        sorted_clusters[2]: "Sangat Subur"
    }

    df['Label_KMeans'] = df['Cluster'].map(label_map)
    
    # 5. Visualisasi Cluster (PCA 2D) untuk Skripsi
    print("\nMembuat plot visualisasi PCA untuk Laporan Skripsi...")
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df['PCA1'] = X_pca[:, 0]
    df['PCA2'] = X_pca[:, 1]

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='PCA1', y='PCA2', hue='Label_KMeans', data=df, palette=['red', 'orange', 'green'], alpha=0.7)
    plt.title('Sebaran 3 Kelas Kesuburan Tanah Berdasarkan K-Means Clustering')
    plt.xlabel('Principal Component 1 (Merangkum sebagian besar variansi NPK)')
    plt.ylabel('Principal Component 2')
    plt.legend(title='Kesuburan Tanah')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    pca_plot_path = os.path.join(PLOTS_DIR, "kmeans_clusters_pca.png")
    plt.savefig(pca_plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Bar chart rata-rata per kelas
    plt.figure(figsize=(12, 6))
    cluster_means.set_index(pd.Series(cluster_means.index).map(label_map)).plot(kind='bar', colormap='viridis', figsize=(10, 6))
    plt.title('Rata-rata Nilai Sensor pada Masing-Masing Kelas Kesuburan')
    plt.ylabel('Nilai (mg/kg, %, dll)')
    plt.xlabel('Kelas Kesuburan')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    bar_plot_path = os.path.join(PLOTS_DIR, "kmeans_cluster_means.png")
    plt.savefig(bar_plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Simpan hasil pelabelan
    # Menghapus kolom sementara
    df.drop(columns=['Cluster', 'PCA1', 'PCA2'], inplace=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\nBerhasil menyimpan data yang sudah dilabeli ke:\n{OUTPUT_CSV}")
    print(f"Gambar plot tersimpan di:\n- {pca_plot_path}\n- {bar_plot_path}")
    print("\nDistribusi Label Baru:")
    print(df['Label_KMeans'].value_counts())
    print("=" * 50)

if __name__ == "__main__":
    main()
