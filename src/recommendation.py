import pandas as pd
import numpy as np
import joblib
import os
import json

# Define paths
MODELS_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\models"
DATA_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\src\processed_data"

def load_resources():
    print("Loading resources...")
    # Load Scaler
    scaler_params = pd.read_csv(os.path.join(DATA_DIR, "scaler_params.csv"), index_col=0)
    
    # Load Ideal Profile
    try:
        ideal_profile = pd.read_csv(os.path.join(DATA_DIR, "ideal_profile.csv"), index_col=0).squeeze()
    except FileNotFoundError:
        print("Warning: Ideal profile not found. Using defaults.")
        ideal_profile = pd.Series({'N': 200, 'P': 300, 'K': 500, 'pH': 6.8, 'EC': 700, 'OC': 0.80})

    # Load Model (Random Forest by default)
    try:
        model = joblib.load(os.path.join(MODELS_DIR, "random_forest.joblib"))
    except FileNotFoundError:
        print("Error: Model file not found.")
        return None, None, None

    return model, scaler_params, ideal_profile

def get_recommendation(n, p, k, ph, ec, oc):
    model, scaler_params, ideal = load_resources()
    if model is None:
        return "System Error"

    # Input Array
    input_data = np.array([[n, p, k, ph, ec, oc]])
    
    # Manual Scaling (since we saved params manually, or load scaler object if saved)
    # Applying standard scaling: (x - mean) / scale
    input_scaled = input_data.copy()
    features = ['N', 'P', 'K', 'pH', 'EC', 'OC']
    for i, col in enumerate(features):
        mean = scaler_params.loc[col, 'mean']
        scale = scaler_params.loc[col, 'scale']
        input_scaled[0, i] = (input_data[0, i] - mean) / scale
        
    # Predict
    fertility_class = model.predict(input_scaled)[0]
    fertility_labels = {0: "Low Fertility", 1: "Medium Fertility", 2: "High Fertility"}
    label = fertility_labels.get(fertility_class, "Unknown")
    
    print(f"\n--- Analysis ---")
    print(f"Inputs: N={n}, P={p}, K={k}, pH={ph}, EC={ec}, OC={oc}")
    print(f"Prediction: {label} (Class {fertility_class})")
    
    recommendations = []
    
    # Logic: If not High Fertility, check deficiencies
    if fertility_class < 2:
        recommendations.append(f"Soil is '{label}'. Improvement needed.")
        
        # Check N
        if n < ideal['N'] * 0.8:
            diff = int(ideal['N'] - n)
            recommendations.append(f"- Nitrogen is Low (Deficit ~{diff}). Add Urea or Compost.")
        
        # Check P
        if p < ideal['P'] * 0.8:
            recommendations.append(f"- Phosphorus is Low. Add SP-36 or Rock Phosphate.")
            
        # Check K
        if k < ideal['K'] * 0.8:
            recommendations.append(f"- Potassium is Low. Add KCL or Wood Ash.")
            
        # Check pH
        if ph < 5.5:
            recommendations.append("- pH is Acidic. Add Lime (Dolomit).")
        elif ph > 7.5:
            recommendations.append("- pH is Basic. Add Sulfur or Organic Matter.")
            
        # Check OC
        if oc < 0.5:
            recommendations.append("- Low Organic Carbon. Add Manure/Compost.")
            
    else:
        recommendations.append("Soil is Highly Fertile. Maintain current management.")
        
    return "\n".join(recommendations)

# Example Usage — nilai sensor 7-in-1
if __name__ == "__main__":
    # Test Case 1: Low Fertility (tanah miskin hara)
    print("\n[TEST 1 — Kurang Subur]")
    print(get_recommendation(n=50, p=80, k=60, ph=5.0, ec=200, oc=0.40))
    
    # Test Case 2: High Fertility (tanah subur)
    print("\n[TEST 2 — Sangat Subur]")
    print(get_recommendation(n=300, p=600, k=700, ph=6.8, ec=1200, oc=0.65))
