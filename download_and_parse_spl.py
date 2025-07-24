import os
import pandas as pd
import json

CSV_PATH = r"C:\\medicinegpt\\drug_dataset.csv\\drugs_side_effects_drugs_com.csv"
OUTPUT_JSON = "drug_data/drugs.json"

print("📥 Loading dataset...")
df = pd.read_csv(CSV_PATH)
print("🔎 Columns:", list(df.columns))

# Drop rows with missing essential info
df = df.dropna(subset=["drug_name", "medical_condition", "side_effects"])

parsed = []

for _, row in df.iterrows():
    parsed.append({
        "name": row["drug_name"],
        "description": f"{row['medical_condition']} - {row.get('medical_condition_description', '')}",
        "warnings": row["side_effects"],
        "brand_names": row.get("brand_names", ""),
        "generic_name": row.get("generic_name", "")
    })

# Save to JSON
os.makedirs("drug_data", exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(parsed)} drugs to {OUTPUT_JSON}")
# faiss_index_builder.py



