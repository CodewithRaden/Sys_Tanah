import joblib
import os
from micromlgen import port

MODELS_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\models"
OUTPUT_DIR = r"c:\Users\DELL GAMING\Documents\Kuliah\Semester8\Sys_Tanah\esp32_code"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the tuned RF model
model_path = os.path.join(MODELS_DIR, "random_forest_tuned.joblib")
print(f"Loading model from {model_path}...")
clf = joblib.load(model_path)

# Export to C code
print("Exporting to C header...")
c_code = port(clf, classmap={0: 'Low', 1: 'Medium', 2: 'High'})

output_path = os.path.join(OUTPUT_DIR, "model.h")
with open(output_path, "w") as f:
    f.write(c_code)

print(f"Done! C header saved to: {output_path}")
print(f"\nPreview (first 20 lines):")
lines = c_code.split('\n')
for line in lines[:20]:
    print(line)
