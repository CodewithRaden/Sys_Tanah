import pandas as pd
import numpy as np
import os
import joblib
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report

# Define paths
PROCESSED_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\src\processed_data"
MODELS_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\models"
RESULTS_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\results"

def load_data():
    print("Loading processed data...")
    X_train = pd.read_csv(os.path.join(PROCESSED_DIR, "X_train.csv"))
    X_test = pd.read_csv(os.path.join(PROCESSED_DIR, "X_test.csv"))
    y_train = pd.read_csv(os.path.join(PROCESSED_DIR, "y_train.csv")).values.ravel()
    y_test = pd.read_csv(os.path.join(PROCESSED_DIR, "y_test.csv")).values.ravel()
    return X_train, X_test, y_train, y_test

def tune_random_forest(X_train, X_test, y_train, y_test):
    print("\n--- Starting Random Forest Hyperparameter Tuning ---")
    
    # 1. Baseline Model (Before Tuning)
    print("\nEvaluating Baseline (Default) Model...")
    baseline_model = RandomForestClassifier(random_state=42)
    baseline_model.fit(X_train, y_train)
    y_pred_base = baseline_model.predict(X_test)
    acc_base = accuracy_score(y_test, y_pred_base)
    print(f"Baseline Accuracy: {acc_base:.4f} ({acc_base*100:.2f}%)")

    # 2. Hyperparameter Grid
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    # 3. Grid Search (After Tuning)
    print("\nRunning GridSearchCV (This may take a minute)...")
    start_time = time.time()
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, 
                               cv=3, n_jobs=-1, verbose=2, scoring='accuracy')
    
    grid_search.fit(X_train, y_train)
    end_time = time.time()
    
    print(f"\nTuning Completed in {end_time - start_time:.2f} seconds.")
    print(f"Best Parameters Found: {grid_search.best_params_}")
    
    # Minimize the tuned model validation
    best_model = grid_search.best_estimator_
    y_pred_tuned = best_model.predict(X_test)
    acc_tuned = accuracy_score(y_test, y_pred_tuned)
    
    print("\n--- Results Comparison ---")
    print(f"Before Tuning (Default): {acc_base:.4f}")
    print(f"After Tuning (Optimized): {acc_tuned:.4f}")
    
    improvement = acc_tuned - acc_base
    print(f"Improvement: {improvement*100:.2f}%")
    
    # Save Best Model
    joblib.dump(best_model, os.path.join(MODELS_DIR, "random_forest_tuned.joblib"))
    print(f"Tuned model saved to {os.path.join(MODELS_DIR, 'random_forest_tuned.joblib')}")
    
    return acc_base, acc_tuned, grid_search.best_params_

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data()
    tune_random_forest(X_train, X_test, y_train, y_test)
