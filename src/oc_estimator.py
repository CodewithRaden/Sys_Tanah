"""
OC Estimator - Multivariate Regression (Enhanced)
===================================================
Pendekatan 1 : Polynomial + interaction features dari N, P, K, pH, EC
Pendekatan 2 : Pedotransfer via rasio C/N (literatur tanah Indonesia)
Pendekatan 3 : Regresi linear murni (baseline)

Output:
  - models/oc_estimator.joblib
  - models/oc_coefficients.txt  (koefisien siap di-embed ke ESP32)
"""

import pandas as pd
import numpy as np
import joblib, os
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

DATA_PATH = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\dataset1.csv"
MODEL_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\models"
os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
FEATURES = ['N', 'P', 'K', 'pH', 'EC']
TARGET   = 'OC'

X_raw = df[FEATURES].values
y     = df[TARGET].values

print(f"Dataset  : {len(df)} sampel")
print(f"OC range : {y.min():.3f} – {y.max():.3f} | mean: {y.mean():.3f} | std: {y.std():.3f}")

X_train, X_test, y_train, y_test = train_test_split(X_raw, y, test_size=0.2, random_state=42)

# ===========================================================
# Pendekatan 1: Linear Regression murni (baseline)
# ===========================================================
lr = LinearRegression()
lr.fit(X_train, y_train)
r2_lr = r2_score(y_test, lr.predict(X_test))
cv_lr = cross_val_score(lr, X_raw, y, cv=5, scoring='r2').mean()
print(f"\n[1] Linear Regression       R²={r2_lr:.4f}  CV-R²={cv_lr:.4f}")

# ===========================================================
# Pendekatan 2: Polynomial degree-2 + Ridge (interaksi fitur)
# ===========================================================
poly_pipe = Pipeline([
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('ridge', Ridge(alpha=1.0))
])
poly_pipe.fit(X_train, y_train)
r2_poly = r2_score(y_test, poly_pipe.predict(X_test))
cv_poly = cross_val_score(poly_pipe, X_raw, y, cv=5, scoring='r2').mean()
print(f"[2] Poly(2) + Ridge         R²={r2_poly:.4f}  CV-R²={cv_poly:.4f}")

# ===========================================================
# Pendekatan 3: Fitur manual dari pengetahuan agronomi
#   - Ratio C/N  : OC berkaitan erat dengan N (C/N ~ 10–12 untuk lahan pertanian)
#   - pH factor  : tanah masam cenderung rendah OC (proses dekomposisi lambat)
#   - EC factor  : EC tinggi → salinity → hambat akumulasi OM
# Fitur baru: N_norm (N/1000), pH_dev (|pH - 6.5|), N×pH, N/K
# ===========================================================
def make_agro_features(X):
    N   = X[:, 0]; P = X[:, 1]; K = X[:, 2]
    pH  = X[:, 3]; EC = X[:, 4]
    N_pct    = N / 1000.0          # konversi mg/kg → approx %
    pH_dev   = np.abs(pH - 6.5)   # deviasi dari pH optimal
    N_x_pH   = N_pct * pH          # interaksi N-pH
    N_div_K  = N / (K + 1e-6)     # rasio N:K
    EC_sq    = EC ** 2             # non-linear EC
    return np.column_stack([N_pct, pH_dev, N_x_pH, N_div_K, EC_sq, P/1000.0])

X_agro_train = make_agro_features(X_train)
X_agro_test  = make_agro_features(X_test)
X_agro_all   = make_agro_features(X_raw)

agro = LinearRegression()
agro.fit(X_agro_train, y_train)
r2_agro = r2_score(y_test, agro.predict(X_agro_test))
cv_agro = cross_val_score(agro, X_agro_all, y, cv=5, scoring='r2').mean()
print(f"[3] Agronomy Features + LR  R²={r2_agro:.4f}  CV-R²={cv_agro:.4f}")

# ===========================================================
# Pendekatan 4: Pedotransfer berbasis Rasio C/N (literatur)
# OC(%) ≈ k × N(%) = k × N(mg/kg) / 10000
# k = rasio C/N (typical Indonesia: 8–15, fit dari data)
# ===========================================================
N_pct_all = X_raw[:, 0] / 10000.0  # mg/kg → %
cn_ratio  = np.mean(y / (N_pct_all + 1e-9))  # rata-rata C/N dari data
print(f"\n[4] Pedotransfer C/N        estimated C/N ratio = {cn_ratio:.2f}")
y_pred_cn = N_pct_all * cn_ratio
r2_cn  = r2_score(y, y_pred_cn)
mae_cn = mean_absolute_error(y, y_pred_cn)
print(f"    R²={r2_cn:.4f}  MAE={mae_cn:.4f}")

# Coba kombinasi dengan pH (pH rendah → OC lebih tinggi di lahan gambut)
# OC ≈ k × N(%) + m × (7 - pH)  → fit dari data
from numpy.linalg import lstsq
A = np.column_stack([N_pct_all, (7.0 - X_raw[:, 3]), np.ones(len(y))])
coefs, _, _, _ = lstsq(A, y, rcond=None)
y_pred_cn2 = A @ coefs
r2_cn2 = r2_score(y, y_pred_cn2)
print(f"[5] C/N + pH factor         R²={r2_cn2:.4f}  coefs={coefs}")

# ===========================================================
# Pilih model terbaik (berdasarkan CV R²)
# ===========================================================
candidates = {
    'Linear Regression'      : (cv_lr,   r2_lr,   'linear'),
    'Polynomial + Ridge'     : (cv_poly, r2_poly,  'poly'),
    'Agronomy Features'      : (cv_agro, r2_agro,  'agro'),
    'C/N Pedotransfer+pH'    : (r2_cn2,  r2_cn2,   'cn'),
}
best_name = max(candidates, key=lambda k: candidates[k][0])
print(f"\n{'='*45}")
print(f" Model Terpilih : {best_name}")
print(f" CV R²          : {candidates[best_name][0]:.4f}")
print(f" Test R²        : {candidates[best_name][1]:.4f}")
print(f"{'='*45}")

# ===========================================================
# Generate konstanta untuk ESP32 berdasarkan model terpilih
# Untuk ESP32 → SELALU gunakan linear formula (embeddable)
# Kita pilih formula yang paling interpretable:
#   OC = a0 + a1*(N/10000) + a2*(7.0-pH)
# ini langsung dari coefs lstsq di atas
# ===========================================================
a0, a1_N, a2_pH = coefs[2], coefs[0], coefs[1]

OC_MIN = float(max(0.05, y.min()))
OC_MAX = float(y.max())

coef_output = f"""
// ================================================================
// Estimasi OC (C-Organik) via Pedotransfer Function
// Referensi: Rasio C/N + faktor pH (disesuaikan dengan dataset)
// Dataset  : dataset1.csv | R² = {r2_cn2:.4f}
//
// Formula  :
//   N_pct = N_mgkg / 10000.0          (konversi mg/kg → %)
//   OC_est = {a0:.4f}
//          + {a1_N:.4f} * N_pct
//          + {a2_pH:.4f} * (7.0 - pH)
//   OC_est = constrain(OC_est, {OC_MIN:.3f}, {OC_MAX:.3f})
// ================================================================
const float OC_A0   = {a0:.6f}f;
const float OC_AN   = {a1_N:.6f}f;  // koef N (dalam %)
const float OC_APH  = {a2_pH:.6f}f; // koef (7 - pH)
const float OC_MIN_ = {OC_MIN:.4f}f;
const float OC_MAX_ = {OC_MAX:.4f}f;
"""
print(coef_output)

# Simpan
coef_path = os.path.join(MODEL_DIR, 'oc_coefficients.txt')
with open(coef_path, 'w', encoding='utf-8') as f:
    f.write(coef_output)
print(f"Koefisien disimpan: {coef_path}")

# Simpan model agro (terbaik untuk prediksi lebih akurat)
best_model_obj = poly_pipe if best_name == 'Polynomial + Ridge' else (
                 agro       if best_name == 'Agronomy Features' else lr)
joblib.dump(best_model_obj, os.path.join(MODEL_DIR, 'oc_estimator.joblib'))
print(f"Model tersimpan : models/oc_estimator.joblib")
print(f"\n=== KONSTANTA UNTUK ESP32 ===")
print(f"float n_pct = n / 10000.0f;")
print(f"float oc = {a0:.6f}f + {a1_N:.6f}f * n_pct + {a2_pH:.6f}f * (7.0f - ph);")
print(f"oc = constrain(oc, {OC_MIN:.4f}f, {OC_MAX:.4f}f);")
