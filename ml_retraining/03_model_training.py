import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Paths
BASE_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah"
INPUT_CSV = os.path.join(BASE_DIR, "ml_retraining", "data", "labeled_data.csv")
MODELS_DIR = os.path.join(BASE_DIR, "ml_retraining", "models")
PLOTS_DIR = os.path.join(BASE_DIR, "ml_retraining", "plots")

def main():
    print("=" * 60)
    print(" TAHAP 3: MODEL TRAINING & COMPARISON")
    print("=" * 60)

    # 1. Load Data
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print("ERROR: File labeled_data.csv tidak ditemukan!")
        return

    features = ['N', 'P', 'K', 'pH', 'EC', 'OC_est']
    X = df[features]
    y_raw = df['Label_KMeans']

    # Encode label string to int untuk XGBoost dan komputasi yang efisien
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    class_names = le.classes_
    print("Mapping Kelas Label:", dict(zip(range(len(class_names)), class_names)))

    # Untuk SVM dan Neural Network (MLP), data (X) perlu distandarisasi agar performanya maksimal
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Train-Test Split (80% Train, 20% Test)
    # Gunakan X_scaled untuk SVM/MLP, dan X untuk RF/XGBoost (karena tree-based tidak butuh scaling)
    # Namun demi keseragaman eksperimen perbandingan, kita pakai X_scaled untuk semuanya
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
    
    # Simpan nama fitur untuk feature importance nanti
    print(f"\nData latih (Train): {len(X_train)} baris")
    print(f"Data uji (Test): {len(X_test)} baris")

    # 3. Inisialisasi Model
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        "SVM": SVC(kernel='rbf', probability=True, random_state=42),
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }

    results = {}
    best_model_name = ""
    best_accuracy = 0
    best_model_obj = None

    print("\nMelatih dan mengevaluasi model...")
    # 4. Training & Evaluasi Loop
    for name, model in models.items():
        print(f" -> Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        results[name] = acc
        
        print(f"    Akurasi {name}: {acc * 100:.2f}%")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model_obj = model

    print("\n--- HASIL PERBANDINGAN MODEL ---")
    for name, acc in results.items():
        print(f"{name:<15}: {acc*100:.2f}%")
    
    print(f"\nModel Terbaik adalah: {best_model_name} dengan akurasi {best_accuracy*100:.2f}%")

    # 5. Visualisasi Perbandingan Model (Bar Chart)
    print("\nMembuat visualisasi perbandingan model...")
    plt.figure(figsize=(10, 6))
    colors = ['skyblue', 'lightgreen', 'salmon', 'orchid']
    bars = plt.bar(results.keys(), [acc * 100 for acc in results.values()], color=colors)
    plt.title('Perbandingan Akurasi Algoritma Machine Learning')
    plt.ylabel('Akurasi (%)')
    plt.ylim(0, 110)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', ha='center', va='bottom', fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    comp_plot_path = os.path.join(PLOTS_DIR, "model_comparison.png")
    plt.savefig(comp_plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Evaluasi Detail Model Terbaik
    print(f"\nMenghasilkan plot evaluasi detail untuk model terbaik ({best_model_name})...")
    y_pred_best = best_model_obj.predict(X_test)

    # 6. Visualisasi Confusion Matrix Model Terbaik
    cm = confusion_matrix(y_test, y_pred_best)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Confusion Matrix - {best_model_name}')
    plt.ylabel('Label Asli (Aktual)')
    plt.xlabel('Label Prediksi')
    
    cm_plot_path = os.path.join(PLOTS_DIR, f"confusion_matrix_{best_model_name.replace(' ', '_')}.png")
    plt.savefig(cm_plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 7. Visualisasi Feature Importance (Jika RF atau XGBoost yang menang)
    if hasattr(best_model_obj, 'feature_importances_'):
        importances = best_model_obj.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title(f"Feature Importance ({best_model_name})")
        plt.bar(range(len(features)), importances[indices], color="coral", align="center")
        plt.xticks(range(len(features)), [features[i] for i in indices])
        plt.ylabel("Tingkat Kepentingan")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        fi_plot_path = os.path.join(PLOTS_DIR, f"feature_importance_{best_model_name.replace(' ', '_')}.png")
        plt.savefig(fi_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        print("Model terbaik tidak memiliki atribut feature_importances_. Melewati plot feature importance.")

    # 8. Simpan Model Terbaik dan Scaler
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(best_model_obj, os.path.join(MODELS_DIR, "best_model.joblib"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.joblib"))
    
    print(f"\nModel {best_model_name}, Scaler, dan Label Encoder berhasil disimpan ke folder models/")
    print("=" * 60)
    print("PIPELINE SELESAI. Silakan cek folder 'plots' untuk perbandingan model.")

if __name__ == "__main__":
    main()
