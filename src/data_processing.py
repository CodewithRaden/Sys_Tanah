import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

# Define paths
DATA_PATH = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\dataset1.csv"
OUTPUT_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\src\processed_data"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_process_data():
    print(f"Loading data from {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"Error: File not found at {DATA_PATH}")
        return

    # ---- Auto-detect data source ----
    # Sensor 7-in-1 data  : kolom 'OC_est', EC dalam µS/cm
    # Dataset1 (Kaggle)   : kolom 'OC', EC dalam dS/m
    if 'OC_est' in df.columns and 'OC' not in df.columns:
        print("  [INFO] Detected sensor data format (OC_est, EC µS/cm)")
        df.rename(columns={'OC_est': 'OC'}, inplace=True)
    elif 'OC' in df.columns:
        print("  [INFO] Detected standard dataset format (OC, EC dS/m)")
    else:
        print("Error: Neither 'OC' nor 'OC_est' column found.")
        return

    # 1. Select Features
    # Target Features: N, P, K, pH, EC, OC
    # Target Label: Output
    
    required_features = ['N', 'P', 'K', 'pH', 'EC', 'OC']
    target_col = 'Output'
    
    # Check columns
    missing_cols = [col for col in required_features + [target_col] if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return

    print("Selecting features: N, P, K, pH, EC, OC...")
    X = df[required_features]
    y = df[target_col]
    
    # 2. Analyze Target
    print("\nTarget Class Distribution (Output):")
    print(y.value_counts().sort_index())
    
    # 3. Calculate "High Fertility" Profile (Class 2) for Recommendations
    # If Class 2 exists, we use it. If not, we might need to assume Class 1 or highest available.
    if 2 in y.unique():
        high_fertility_df = df[df[target_col] == 2][required_features]
        ideal_profile = high_fertility_df.mean()
        print("\nDerived Ideal Profile (Mean of Class 2 - High Fertility):")
        print(ideal_profile)
        # Save to CSV for recommendation logic
        ideal_profile.to_csv(os.path.join(OUTPUT_DIR, "ideal_profile.csv"))
    else:
        print("\nWarning: Class 2 (High Fertility) not found in dataset. Using Class 1 as target.")
        high_fertility_df = df[df[target_col] == 1][required_features]
        ideal_profile = high_fertility_df.mean()
        ideal_profile.to_csv(os.path.join(OUTPUT_DIR, "ideal_profile.csv"))

    # 4. Split Data (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 5. Scale Features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save processed files
    feature_names = required_features
    pd.DataFrame(X_train_scaled, columns=feature_names).to_csv(os.path.join(OUTPUT_DIR, "X_train.csv"), index=False)
    pd.DataFrame(X_test_scaled, columns=feature_names).to_csv(os.path.join(OUTPUT_DIR, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(OUTPUT_DIR, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(OUTPUT_DIR, "y_test.csv"), index=False)
    
    # Save Scaler Params
    scaler_params = pd.DataFrame({'mean': scaler.mean_, 'var': scaler.var_, 'scale': scaler.scale_}, index=feature_names)
    scaler_params.to_csv(os.path.join(OUTPUT_DIR, "scaler_params.csv"))
    
    print(f"\nProcessing complete. Files saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    load_and_process_data()
