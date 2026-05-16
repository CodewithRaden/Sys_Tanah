import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
import json
import time

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_score

# Define paths
PROCESSED_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\src\processed_data"
RESULTS_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\results"
MODELS_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\models"

# Create directories
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def load_data():
    print("Loading processed data...")
    try:
        X_train = pd.read_csv(os.path.join(PROCESSED_DIR, "X_train.csv"))
        X_test = pd.read_csv(os.path.join(PROCESSED_DIR, "X_test.csv"))
        y_train = pd.read_csv(os.path.join(PROCESSED_DIR, "y_train.csv")).values.ravel()
        y_test = pd.read_csv(os.path.join(PROCESSED_DIR, "y_test.csv")).values.ravel()
        return X_train, X_test, y_train, y_test
    except FileNotFoundError:
        print("Error: Processed data files not found. Run data_processing.py first.")
        return None, None, None, None

def train_and_evaluate(models, X_train, X_test, y_train, y_test):
    results = []
    
    # Fertility Classes
    classes = [0, 1, 2] # 0: Low, 1: Medium, 2: High
    class_names = ['Low', 'Medium', 'High']

    for name, model in models.items():
        print(f"\nTraining {name}...")
        start_time = time.time()
        
        # Train
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        # Predict
        infer_start = time.time()
        y_pred = model.predict(X_test)
        infer_time = time.time() - infer_start
        latency_sec = infer_time / len(X_test)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        print(f"{name} Results:")
        print(f"  Accuracy: {acc:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  Training Time: {train_time:.2f}s")
        print(f"  Inference Latency: {latency_sec:.6f} s/sample")
        
        # Cross Validation (5-fold) on TRAIN set
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Save results
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1_Score": f1,
            "CV_Accuracy_Mean": cv_scores.mean(),
            "CV_Accuracy_Std": cv_scores.std(),
            "Training_Time_Sec": train_time,
            "Inference_Latency_s": latency_sec
        })
        
        # Save Model
        model_path = os.path.join(MODELS_DIR, f"{name.replace(' ', '_').lower()}.joblib")
        joblib.dump(model, model_path)
        print(f"  Model saved to {model_path}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred, labels=classes)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=class_names, yticklabels=class_names)
        plt.title(f'Confusion Matrix - {name}')
        plt.ylabel('True Fertility Label')
        plt.xlabel('Predicted Fertility Label')
        plt.savefig(os.path.join(RESULTS_DIR, f"confusion_matrix_{name.replace(' ', '_').lower()}.png"))
        plt.close()
        
    return pd.DataFrame(results)

def plot_comparison(results_df):
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Model", y="Accuracy", data=results_df, palette="viridis")
    plt.title("Model Accuracy Comparison (Soil Fertility)")
    plt.ylim(0, 1.05)
    for index, row in results_df.iterrows():
        plt.text(index, row.Accuracy + 0.02, f"{row.Accuracy:.3f}", color='black', ha="center")
    plt.savefig(os.path.join(RESULTS_DIR, "model_comparison_accuracy.png"))
    plt.close()

def main():
    X_train, X_test, y_train, y_test = load_data()
    
    if X_train is None:
        return

    # Initialize Models
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),
        "SVM": SVC(kernel='rbf', probability=True, random_state=42),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
    }
    
    # Run Comparison
    results_df = train_and_evaluate(models, X_train, X_test, y_train, y_test)
    
    # Save Metrics CSV
    results_path = os.path.join(RESULTS_DIR, "model_comparison_metrics.csv")
    results_df.to_csv(results_path, index=False)
    print(f"\nAll results saved to {results_path}")
    
    # Plot
    plot_comparison(results_df)
    print("Comparison plots generated.")

if __name__ == "__main__":
    main()
