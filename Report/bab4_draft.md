# BAB IV
# HASIL DAN PEMBAHASAN

> [!NOTE]
> Draft ini difokuskan pada sisi **AI/Machine Learning**.
> Bagian yang perlu dilengkapi ditandai `[TODO]`.

---

## 4.1 Analisis Kebutuhan

Pada tahap ini, dilakukan analisis terhadap kebutuhan utama dalam membangun model prediksi kecerdasan buatan, yang terbagi menjadi kebutuhan data sebagai bahan pelatihan (*training*) dan kebutuhan perangkat komputasi *edge* untuk tahap implementasi (*deployment*).

### 4.1.1 Analisis Kebutuhan Data

Kebutuhan data merupakan elemen paling krusial dalam pengembangan algoritma *Machine Learning*. Dalam penelitian ini, dataset yang digunakan untuk melatih dan menguji model diperoleh dari dua sumber utama:

1. **Data Primer** — Merupakan data hasil pengukuran yang diakuisisi secara langsung menggunakan sistem monitoring IoT pada lahan pertanian padi milik Kelompok Tani Famili Sejahtera di Kampung Geger Bitung, Desa Cijeruk, Kabupaten Bogor. Total data primer yang berhasil dikumpulkan sebanyak **136 sampel** dengan parameter: Nitrogen (N), Fosfor (P), Kalium (K), pH, *Electrical Conductivity* (EC), Kelembaban, Suhu, dan estimasi Karbon Organik (OC). Data primer digunakan untuk menguji keandalan prediksi model pada kondisi aktual di lapangan.

2. **Data Sekunder** — Dataset kualitas tanah yang diperoleh dari platform Kaggle dengan jumlah **880 sampel**. Dataset ini memiliki fitur yang relevan meliputi N, P, K, pH, EC, OC, serta label kesuburan tanah (*Output*) dalam tiga kelas: 0 (Kurang Subur), 1 (Subur), dan 2 (Sangat Subur). Data sekunder dipilih sebagai data utama pelatihan model karena memiliki jumlah yang memadai, variasi kelas yang lebih lengkap, serta struktur yang sesuai dengan parameter sensor.

Fitur (*variabel bebas*) yang digunakan untuk melatih model terdiri dari enam parameter fisik dan kimia tanah:

| No | Fitur | Satuan | Keterangan |
|----|-------|--------|------------|
| 1 | Nitrogen (N) | mg/kg | Unsur hara makro primer |
| 2 | Fosfor (P) | mg/kg | Unsur hara makro esensial |
| 3 | Kalium (K) | mg/kg | Unsur hara makro |
| 4 | pH | - | Tingkat keasaman tanah |
| 5 | EC | µS/cm | Konduktivitas listrik tanah |
| 6 | Karbon Organik (OC) | % | Kandungan bahan organik |

Variabel terikat (*dependen*) yang menjadi target prediksi akhir dari model klasifikasi adalah **status kesuburan tanah** yang terbagi menjadi tiga kelas:

| Kode | Label | Deskripsi |
|------|-------|-----------|
| 0 | Kurang Subur | Tanah dengan kandungan hara rendah |
| 1 | Subur | Tanah dengan kandungan hara sedang |
| 2 | Sangat Subur | Tanah dengan kandungan hara optimal |

### 4.1.2 Analisis Kebutuhan Perangkat Lunak

Untuk mendukung proses pelatihan, evaluasi, dan *deployment* model kecerdasan buatan, dibutuhkan perangkat lunak sebagai berikut:

| No | Perangkat Lunak | Fungsi |
|----|-----------------|--------|
| 1 | Python 3.x | Bahasa pemrograman utama untuk pengolahan data dan pelatihan model |
| 2 | scikit-learn | Implementasi algoritma Random Forest, SVM, dan Neural Network |
| 3 | XGBoost | Implementasi algoritma XGBoost |
| 4 | pandas, numpy | Manipulasi dan pemrosesan data tabular |
| 5 | matplotlib, seaborn | Visualisasi hasil evaluasi dan *confusion matrix* |
| 6 | micromlgen | Konversi model ML ke kode C untuk *deployment* ke mikrokontroler |
| 7 | Arduino IDE 2.x | Pemrograman firmware ESP32 untuk inferensi *on-device* |

---

## 4.2 Perancangan Sistem

### 4.2.1 Alur Kerja Pengembangan Model AI

Pengembangan model kecerdasan buatan dalam penelitian ini mengikuti alur kerja (*pipeline*) yang sistematis, terdiri dari dua fase utama:

**Fase 1 — Pelatihan Model (Offline, di PC):**

```
Dataset (CSV) → Pelabelan → Preprocessing → Training → Evaluasi → Tuning → Export
```

1. **Pengumpulan Data** — Data sensor dikumpulkan via koneksi serial dan disimpan ke `real_data_raw.csv`
2. **Pelabelan Otomatis** — Data primer diberi label kesuburan berdasarkan framework Balittanah 2009
3. **Pra-pemrosesan Data** — Seleksi fitur, pembagian data (80:20), dan normalisasi *StandardScaler*
4. **Pelatihan & Komparasi** — Empat algoritma ML dilatih dan dibandingkan performanya
5. **Hyperparameter Tuning** — Model terbaik dioptimasi menggunakan *GridSearchCV*
6. **Ekspor Model** — Model final dikonversi ke kode C menggunakan `micromlgen`

**Fase 2 — Inferensi Real-Time (Online, di ESP32):**

```
Sensor → Data → Normalisasi → Model AI → Prediksi → Rekomendasi → LCD
```

Mikrokontroler ESP32 menjalankan model Random Forest yang telah di-*embed* untuk melakukan klasifikasi kesuburan tanah secara *on-device* tanpa memerlukan koneksi internet.

`[TODO: Sisipkan Gambar Diagram Alur Kerja Sistem]`

### 4.2.2 Perancangan Sistem Pelabelan (Auto-Labeling)

Pelabelan data primer dilakukan secara otomatis menggunakan sistem skor yang mengacu pada **framework Balittanah/PPT Bogor 2009**, yang diadaptasi untuk output sensor digital 7-in-1. Setiap parameter diberi skor 0 (Rendah), 1 (Sedang), atau 2 (Tinggi) berdasarkan threshold berikut:

| Parameter | Rendah (skor 0) | Sedang (skor 1) | Tinggi (skor 2) |
|-----------|-----------------|-----------------|-----------------|
| N (mg/kg) | < 100 | 100–200 | > 200 |
| P (mg/kg) | < 10 | 10–30 | > 30 |
| K (mg/kg) | < 100 | 100–300 | > 300 |
| OC (%) | < 1.0 | 1.0–2.0 | > 2.0 |
| pH | < 5.5 atau > 7.5 | 5.5–6.5 | 6.6–7.5 |
| EC (µS/cm) | > 2000 | 800–2000 | < 800 |

Total skor dari keenam parameter kemudian dipetakan ke kelas kesuburan:
- Skor 0–4 → **Kurang Subur** (kelas 0)
- Skor 5–8 → **Subur** (kelas 1)
- Skor 9–12 → **Sangat Subur** (kelas 2)

Justifikasi adaptasi threshold: sensor 7-in-1 mengukur kadar unsur hara *tersedia* (*available*), bukan N-total atau P₂O₅/K₂O ekstrak HCl seperti metode laboratorium konvensional, sehingga threshold diturunkan dari distribusi statistik data sensor sambil mempertahankan framework 3-kelas Balittanah.

### 4.2.3 Perancangan Algoritma Klasifikasi

Sesuai dengan metodologi pada Bab III, empat algoritma *Machine Learning* digunakan dan dibandingkan performanya:

1. **Random Forest** — Algoritma *ensemble learning* yang membangun banyak pohon keputusan secara paralel dengan mekanisme *bagging* dan menentukan prediksi melalui *voting* mayoritas. Diinisialisasi dengan `n_estimators=100` dan `random_state=42`.

2. **XGBoost** — Algoritma *gradient boosting* yang membangun pohon secara sekuensial di mana setiap pohon baru bertujuan memperbaiki kesalahan (*residual*) pohon sebelumnya. Menggunakan `eval_metric='mlogloss'` untuk kasus multi-kelas.

3. **SVM (RBF Kernel)** — Algoritma yang mencari *hyperplane* optimal untuk memisahkan kelas data dengan margin maksimal. Menggunakan kernel *Radial Basis Function* (RBF) untuk menangani data non-linier.

4. **Neural Network (MLP)** — *Multi-Layer Perceptron* dengan arsitektur dua *hidden layer* (64 dan 32 neuron) dan iterasi maksimal 1000 *epoch*.

---

## 4.3 Implementasi Sistem

### 4.3.1 Implementasi Pengumpulan Data

Pengumpulan data lapangan dilakukan menggunakan skrip Python (`data_collector.py`) yang terhubung ke ESP32 via koneksi serial USB (baud rate 115200). Skrip ini bekerja secara otomatis: mendeteksi port COM, mem-*parse* data CSV dari output serial sensor, dan menyimpan setiap bacaan ke file `real_data_raw.csv` beserta *timestamp* dan nama lokasi pengambilan sampel.

Total data primer yang berhasil dikumpulkan:
- **Jumlah sampel**: 136 sampel
- **Lokasi**: Lahan pertanian padi, Kelompok Tani Famili Sejahtera, Cijeruk, Bogor
- **Interval pengambilan**: ±20 detik per sampel
- **Parameter**: N, P, K, pH, EC, OC (estimasi), Kelembaban, Suhu

### 4.3.2 Implementasi Pra-pemrosesan Data

Pra-pemrosesan data dilakukan menggunakan skrip `data_processing.py` dengan tahapan sebagai berikut:

**a) Seleksi Fitur**

Dari keseluruhan kolom yang tersedia pada dataset, dipilih 6 fitur utama yang paling relevan dengan kualitas tanah: **N, P, K, pH, EC, dan OC**. Fitur-fitur ini dipilih berdasarkan parameter yang dapat diukur oleh sensor dan memiliki korelasi langsung dengan kesuburan tanah menurut literatur.

**b) Pembagian Data (Data Splitting)**

Dataset dibagi menjadi **80% data latih** dan **20% data uji** menggunakan metode *stratified sampling* (`stratify=y`) untuk memastikan proporsi setiap kelas kesuburan tetap seimbang pada kedua subset data.

**c) Normalisasi (Standard Scaling)**

Normalisasi dilakukan menggunakan `StandardScaler` dari scikit-learn yang mentransformasi setiap fitur ke distribusi dengan *mean* = 0 dan *standard deviation* = 1. Transformasi ini penting karena fitur-fitur memiliki rentang nilai yang sangat berbeda (misalnya N: 6–383 mg/kg vs pH: 0.9–11.15).

Formula normalisasi: `z = (x − μ) / σ`

Parameter *scaler* yang diperoleh:

| Fitur | Mean (μ) | Scale (σ) |
|-------|----------|-----------|
| N | 146.77 | 51.48 |
| P | 11.00 | 4.17 |
| K | 557.63 | 187.76 |
| pH | 7.07 | 0.66 |
| EC | 0.60 | 0.24 |
| OC | 0.69 | 0.31 |

Parameter *mean* dan *scale* disimpan dan kemudian ditanamkan (*embedded*) ke firmware ESP32 agar proses normalisasi dapat dilakukan secara identik saat inferensi *on-device*.

### 4.3.3 Implementasi Pelatihan dan Komparasi Model

Pelatihan keempat algoritma klasifikasi dilakukan menggunakan skrip `model_comparison.py`. Setiap model dilatih pada data latih yang telah dinormalisasi, kemudian dievaluasi menggunakan:

- **Metrik pada data uji**: Accuracy, Precision (*weighted*), Recall (*weighted*), dan F1-Score (*weighted*)
- **Validasi silang**: 5-*fold Cross Validation* pada data latih untuk mengukur stabilitas dan kemampuan generalisasi model

Seluruh model disimpan dalam format `.joblib` dan *confusion matrix* divisualisasikan untuk analisis lebih lanjut.

### 4.3.4 Implementasi Hyperparameter Tuning

Model dengan performa terbaik (Random Forest) selanjutnya dioptimasi menggunakan `GridSearchCV` dengan 3-*fold cross validation*. Parameter yang dioptimasi:

| Hyperparameter | Nilai yang Dicoba | Keterangan |
|----------------|-------------------|------------|
| `n_estimators` | 50, 100, 200 | Jumlah pohon keputusan |
| `max_depth` | None, 10, 20, 30 | Kedalaman maksimal pohon |
| `min_samples_split` | 2, 5, 10 | Minimum sampel untuk pemisahan node |
| `min_samples_leaf` | 1, 2, 4 | Minimum sampel pada daun pohon |

Total kombinasi parameter yang dievaluasi: 3 × 4 × 3 × 3 = **108 kombinasi**.

`[TODO: Tambahkan hasil best_params_ dan perbandingan akurasi sebelum vs sesudah tuning]`

### 4.3.5 Implementasi Deployment ke ESP32

Model Random Forest yang telah di-*tuning* diekspor ke format kode C menggunakan library `micromlgen`. File `model.h` yang dihasilkan (±1.1 MB) berisi representasi setiap pohon keputusan sebagai fungsi C dengan operasi *if-else* yang dapat dieksekusi langsung oleh ESP32 tanpa memerlukan library ML tambahan.

Firmware ESP32 (`soil_fertility.ino`) mengimplementasikan keseluruhan *pipeline* inferensi secara *on-device*:
1. Pembacaan data sensor via protokol Modbus RTU
2. Normalisasi fitur menggunakan parameter *scaler* yang telah ditanamkan
3. Inferensi model Random Forest untuk klasifikasi kesuburan
4. Pemberian rekomendasi pemupukan berdasarkan defisiensi parameter
5. Tampilan hasil pada LCD 16×4

---

## 4.4 Pengujian

### 4.4.1 Deskripsi Pengujian

Pengujian dilakukan untuk mengevaluasi performa model kecerdasan buatan dalam mengklasifikasikan kualitas tanah. Pengujian terbagi menjadi:

1. **Pengujian Performa Model** — Membandingkan akurasi keempat algoritma ML (Random Forest, XGBoost, SVM, Neural Network) menggunakan metrik berbasis *Confusion Matrix* (Accuracy, Precision, Recall, F1-Score) dan *Cross Validation*.
2. **Pengujian Sistem Terintegrasi** — Menguji kemampuan model yang telah di-*deploy* pada ESP32 dalam melakukan klasifikasi secara *real-time* pada data sensor aktual.

### 4.4.2 Prosedur Pengujian

**A. Prosedur Pengujian Performa Model:**
1. Dataset sekunder (880 sampel, 3 kelas) dimuat
2. Dipilih 6 fitur utama (N, P, K, pH, EC, OC)
3. Data dibagi 80:20 (latih:uji) dengan *stratified sampling*
4. Fitur dinormalisasi menggunakan *StandardScaler*
5. Keempat model dilatih pada data latih
6. Prediksi dilakukan pada data uji
7. Metrik evaluasi dihitung: Accuracy, Precision, Recall, F1-Score
8. Validasi silang 5-*fold* dilakukan pada data latih
9. *Confusion Matrix* divisualisasikan untuk setiap model

**B. Prosedur Pengujian Sistem Terintegrasi:**
1. Sensor ditancapkan ke sampel tanah pada lahan uji
2. ESP32 membaca data sensor dan melakukan inferensi *on-device*
3. Hasil prediksi dan rekomendasi ditampilkan pada LCD
4. Waktu inferensi (*latency*) diukur menggunakan fungsi `micros()` pada ESP32
5. Hasil prediksi dicatat dan dibandingkan dengan label yang diharapkan

### 4.4.3 Data Hasil Pengujian

#### A. Hasil Perbandingan Performa Model

**Tabel 4.1 Perbandingan Performa Model Klasifikasi Kualitas Tanah**

| Model | Accuracy | Precision | Recall | F1-Score | CV Accuracy (Mean ± Std) |
|-------|----------|-----------|--------|----------|--------------------------|
| **Random Forest** | **0.8807** | **0.8507** | **0.8807** | **0.8654** | **0.9148 ± 0.0065** |
| XGBoost | 0.8636 | 0.8435 | 0.8636 | 0.8535 | 0.8991 ± 0.0152 |
| SVM | 0.8636 | 0.8291 | 0.8636 | 0.8438 | 0.8835 ± 0.0227 |
| Neural Network | 0.8466 | 0.8441 | 0.8466 | 0.8450 | 0.8793 ± 0.0003 |

`[TODO: Sisipkan Gambar — Grafik Perbandingan Akurasi Model (model_comparison_accuracy.png)]`

#### B. Confusion Matrix

`[TODO: Sisipkan Gambar — Confusion Matrix Random Forest]`
`[TODO: Sisipkan Gambar — Confusion Matrix XGBoost]`
`[TODO: Sisipkan Gambar — Confusion Matrix SVM]`
`[TODO: Sisipkan Gambar — Confusion Matrix Neural Network]`

#### C. Hasil Pengujian Sistem Terintegrasi

`[TODO: Isi tabel berdasarkan pengujian langsung di lapangan]`

**Tabel 4.2 Hasil Pengujian Prediksi pada Data Lapangan**

| No | Sampel | N | P | K | pH | EC | OC | Prediksi AI | Label Seharusnya | Sesuai? |
|----|--------|---|---|---|----|----|-----|-------------|------------------|---------|
| 1 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Tabel 4.3 Hasil Pengujian Latensi Inferensi pada ESP32**

| No | Percobaan | Latency (detik) |
|----|-----------|-----------------|
| 1 | ... | ... |
| **Rata-rata** | | **...** |

### 4.4.4 Analisis Data dan Evaluasi Pengujian

#### A. Analisis Performa Model Klasifikasi

Berdasarkan hasil pengujian pada Tabel 4.1, model **Random Forest** menunjukkan performa terbaik di antara keempat algoritma yang diuji dengan akurasi sebesar **88,07%** dan rata-rata akurasi validasi silang sebesar **91,48%**. Berikut adalah analisis untuk masing-masing model:

1. **Random Forest** — Mencapai akurasi tertinggi (88,07%) dengan F1-Score 0,8654. Nilai *Cross Validation* yang tinggi (91,48%) dengan standar deviasi paling rendah (0,0065) mengindikasikan bahwa model memiliki kemampuan generalisasi yang baik dan tidak mengalami *overfitting*. Stabilitas ini disebabkan oleh mekanisme *bagging* yang membangun banyak pohon keputusan secara independen pada subset data yang berbeda, sehingga mengurangi varians prediksi.

2. **XGBoost** — Menempati posisi kedua dengan akurasi 86,36% dan F1-Score 0,8535. Meskipun XGBoost merupakan algoritma *boosting* yang umumnya unggul pada banyak kasus, performanya sedikit di bawah Random Forest. Hal ini kemungkinan disebabkan oleh ukuran dataset yang relatif terbatas (880 sampel) sehingga keunggulan *sequential error correction* dari XGBoost belum dapat dimanfaatkan secara optimal.

3. **SVM (RBF Kernel)** — Memperoleh akurasi setara XGBoost (86,36%) namun dengan Precision lebih rendah (82,91%). Standar deviasi CV yang lebih besar (0,0227) menunjukkan variabilitas performa yang lebih tinggi antar *fold*, mengindikasikan sensitivitas model terhadap komposisi data latih. Hal ini umum terjadi pada SVM ketika parameter C dan gamma belum dioptimasi secara mendalam.

4. **Neural Network (MLP)** — Menunjukkan performa terendah (84,66%) dengan waktu pelatihan terlama (1,509 detik). Arsitektur MLP dengan dua *hidden layer* (64, 32 neuron) kemungkinan memerlukan jumlah data yang lebih besar untuk dapat mempelajari representasi fitur secara optimal. Pada dataset dengan ukuran 880 sampel, model berbasis *tree* (Random Forest, XGBoost) cenderung lebih efektif dibandingkan *neural network*.

#### B. Justifikasi Pemilihan Random Forest sebagai Model Final

Berdasarkan hasil evaluasi komprehensif, **Random Forest** dipilih sebagai model final yang di-*deploy* ke mikrokontroler ESP32 dengan pertimbangan sebagai berikut:

| Aspek | Justifikasi |
|-------|-------------|
| **Akurasi** | Tertinggi di antara keempat model (88,07%) |
| **Generalisasi** | CV Accuracy terbaik (91,48%) dan paling stabil (std = 0,0065) |
| **Deployment** | Struktur pohon keputusan (*if-else*) dapat dikonversi ke kode C native tanpa library tambahan |
| **Efisiensi** | Inferensi hanya memerlukan operasi *if-else*, tidak memerlukan operasi matriks atau kernel |
| **Robustness** | Mekanisme *bagging* menjadikan model tahan terhadap *noise* pada data sensor |

#### C. Analisis Sistem Terintegrasi

`[TODO: Lengkapi analisis berdasarkan data Tabel 4.2 dan 4.3, mencakup:]`
- Tingkat kesesuaian prediksi *on-device* dengan label yang diharapkan
- Rata-rata latensi inferensi pada mikrokontroler ESP32
- Kendala yang ditemui selama pengujian lapangan dan solusinya

---

> [!IMPORTANT]
> **Checklist bagian yang perlu dilengkapi:**
> 1. Gambar diagram alur kerja/arsitektur sistem
> 2. Gambar confusion matrix (sudah ada di `results/`)
> 3. Gambar grafik perbandingan akurasi (sudah ada di `results/`)
> 4. Hasil `best_params_` dari hyperparameter tuning
> 5. Data pengujian lapangan (Tabel 4.2)
> 6. Data latensi inferensi ESP32 (Tabel 4.3)
> 7. Analisis pengujian sistem terintegrasi (sub-bab 4.4.4 C)
