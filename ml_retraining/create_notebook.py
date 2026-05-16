import json
import os

notebook_dict = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Pipeline Machine Learning - Prediksi Kesuburan Tanah\n",
                "\n",
                "Notebook ini berisi seluruh tahapan untuk memproses dataset tanah riil, melabeli data menggunakan kriteria pakar (Balittanah), dan melatih serta membandingkan beberapa model Machine Learning (Random Forest, SVM, XGBoost, Neural Network).\n",
                "Sangat cocok untuk dilampirkan atau didemonstrasikan pada saat sidang skripsi."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import numpy as np\n",
                "import os\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import joblib\n",
                "from sklearn.model_selection import train_test_split\n",
                "from sklearn.preprocessing import LabelEncoder, StandardScaler\n",
                "from sklearn.ensemble import RandomForestClassifier\n",
                "from sklearn.svm import SVC\n",
                "from sklearn.neural_network import MLPClassifier\n",
                "import xgboost as xgb\n",
                "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix\n",
                "\n",
                "# Konfigurasi Matplotlib\n",
                "plt.style.use('seaborn-v0_8-whitegrid')\n",
                "%matplotlib inline"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Tahap 1: Data Cleaning\n",
                "Memuat dataset asli, menghapus kolom lama (dari Kaggle), dan memfilter baris yang bernilai kosong (NaN)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "INPUT_CSV = '../soil_dataset.csv'\n",
                "\n",
                "# Load Data\n",
                "df = pd.read_csv(INPUT_CSV)\n",
                "print(f\"Total baris awal: {len(df)}\")\n",
                "\n",
                "# Hapus Kolom Lama\n",
                "cols_to_drop = ['ai_label', 'recommendation']\n",
                "df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors='ignore')\n",
                "\n",
                "# Filter missing values pada sensor\n",
                "required_sensors = ['N', 'P', 'K', 'pH', 'EC', 'OC_est']\n",
                "df.dropna(subset=required_sensors, inplace=True)\n",
                "\n",
                "print(f\"Total baris setelah cleaning: {len(df)}\")\n",
                "display(df.head())"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Tahap 2: Auto Labeling (Sistem Pakar Balittanah)\n",
                "Menggunakan logika Rule-Based Expert System untuk memberikan skor kesuburan berdasarkan nilai N, P, K, pH, EC, dan OC yang telah disesuaikan (dikalibrasi) untuk sensor IoT."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def score_N(N_mgkg):\n",
                "    if N_mgkg < 100: return 0\n",
                "    elif N_mgkg <= 200: return 1\n",
                "    else: return 2\n",
                "\n",
                "def score_P(P_mgkg):\n",
                "    if P_mgkg < 100: return 0\n",
                "    elif P_mgkg <= 300: return 1\n",
                "    else: return 2\n",
                "\n",
                "def score_K(K_mgkg):\n",
                "    if K_mgkg < 100: return 0\n",
                "    elif K_mgkg <= 300: return 1\n",
                "    else: return 2\n",
                "\n",
                "def score_OC(OC_pct):\n",
                "    if OC_pct < 0.5: return 0\n",
                "    elif OC_pct <= 1.0: return 1\n",
                "    else: return 2\n",
                "\n",
                "def score_pH(pH):\n",
                "    if pH < 5.5 or pH > 7.5: return 0\n",
                "    elif pH <= 6.5: return 1\n",
                "    else: return 2\n",
                "\n",
                "def score_EC(EC_uscm):\n",
                "    if EC_uscm > 2000: return 0\n",
                "    elif EC_uscm > 800: return 1\n",
                "    else: return 2\n",
                "\n",
                "def compute_label(row):\n",
                "    total = (score_N(row['N']) + score_P(row['P']) + score_K(row['K']) +\n",
                "             score_OC(row['OC_est']) + score_pH(row['pH']) + score_EC(row['EC']))\n",
                "    if total <= 4: return 0\n",
                "    elif total <= 8: return 1\n",
                "    else: return 2\n",
                "\n",
                "LABEL_NAME = {0: \"Kurang Subur\", 1: \"Subur\", 2: \"Sangat Subur\"}\n",
                "\n",
                "df['Output'] = df.apply(compute_label, axis=1)\n",
                "df['Label'] = df['Output'].map(LABEL_NAME)\n",
                "\n",
                "# Visualisasi Distribusi\n",
                "plt.figure(figsize=(6, 6))\n",
                "df['Label'].value_counts().plot.pie(autopct='%1.1f%%', colors=['lightcoral', 'gold', 'lightgreen'])\n",
                "plt.title(\"Distribusi Label Kesuburan (Sistem Pakar)\")\n",
                "plt.ylabel(\"\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Tahap 3: Model Training & Comparison\n",
                "Melatih dan membandingkan 4 model Machine Learning: Random Forest, SVM, XGBoost, dan Neural Network."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "X = df[required_sensors]\n",
                "y_raw = df['Label']\n",
                "\n",
                "# Label Encoding\n",
                "le = LabelEncoder()\n",
                "y = le.fit_transform(y_raw)\n",
                "class_names = le.classes_\n",
                "\n",
                "# Standarisasi Fitur\n",
                "scaler = StandardScaler()\n",
                "X_scaled = scaler.fit_transform(X)\n",
                "\n",
                "# Split Data (80% Train, 20% Test)\n",
                "X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)\n",
                "\n",
                "# Inisialisasi Model\n",
                "models = {\n",
                "    \"Random Forest\": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),\n",
                "    \"SVM\": SVC(kernel='rbf', probability=True, random_state=42),\n",
                "    \"XGBoost\": xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),\n",
                "    \"Neural Network\": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)\n",
                "}\n",
                "\n",
                "results = {}\n",
                "best_model_name = \"\"\n",
                "best_accuracy = 0\n",
                "best_model_obj = None\n",
                "\n",
                "print(\"--- HASIL PERBANDINGAN MODEL ---\")\n",
                "for name, model in models.items():\n",
                "    model.fit(X_train, y_train)\n",
                "    y_pred = model.predict(X_test)\n",
                "    acc = accuracy_score(y_test, y_pred)\n",
                "    results[name] = acc\n",
                "    print(f\"{name:<15}: {acc*100:.2f}%\")\n",
                "    \n",
                "    if acc > best_accuracy:\n",
                "        best_accuracy = acc\n",
                "        best_model_name = name\n",
                "        best_model_obj = model\n",
                "\n",
                "print(f\"\\nModel Terbaik: {best_model_name}\")\n",
                "\n",
                "# Visualisasi Bar Chart\n",
                "plt.figure(figsize=(8, 5))\n",
                "colors = ['skyblue', 'lightgreen', 'salmon', 'orchid']\n",
                "bars = plt.bar(results.keys(), [acc * 100 for acc in results.values()], color=colors)\n",
                "plt.title('Perbandingan Akurasi Algoritma Machine Learning')\n",
                "plt.ylabel('Akurasi (%)')\n",
                "plt.ylim(0, 110)\n",
                "for bar in bars:\n",
                "    yval = bar.get_height()\n",
                "    plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', ha='center', va='bottom', fontweight='bold')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Tahap 4: Detail Evaluasi Model Terbaik\n",
                "Memvisualisasikan *Confusion Matrix* dan *Feature Importance* (jika algoritma berbasis tree)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "y_pred_best = best_model_obj.predict(X_test)\n",
                "\n",
                "print(\"Classification Report:\")\n",
                "print(classification_report(y_test, y_pred_best, target_names=class_names))\n",
                "\n",
                "# Confusion Matrix\n",
                "cm = confusion_matrix(y_test, y_pred_best)\n",
                "plt.figure(figsize=(6, 5))\n",
                "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)\n",
                "plt.title(f'Confusion Matrix - {best_model_name}')\n",
                "plt.ylabel('Aktual')\n",
                "plt.xlabel('Prediksi')\n",
                "plt.show()\n",
                "\n",
                "# Feature Importance (Hanya untuk RF / XGBoost)\n",
                "if hasattr(best_model_obj, 'feature_importances_'):\n",
                "    importances = best_model_obj.feature_importances_\n",
                "    indices = np.argsort(importances)[::-1]\n",
                "    plt.figure(figsize=(8, 5))\n",
                "    plt.title(f\"Feature Importance ({best_model_name})\")\n",
                "    plt.bar(range(len(required_sensors)), importances[indices], color=\"coral\", align=\"center\")\n",
                "    plt.xticks(range(len(required_sensors)), [required_sensors[i] for i in indices])\n",
                "    plt.ylabel(\"Tingkat Kepentingan\")\n",
                "    plt.show()\n",
                "else:\n",
                "    print(\"Model terbaik bukan berbasis pohon, lewati plot feature importance.\")"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

out_path = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\ml_retraining\pipeline_skripsi.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print(f"Jupyter Notebook berhasil dibuat di: {out_path}")
