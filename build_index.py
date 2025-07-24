import json
import pickle
import os
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

INPUT_JSON = "drug_data/drugs.json"
OUTPUT_INDEX = "faiss_index/index.pkl"
os.makedirs("faiss_index", exist_ok=True)

# Load data
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Init sentence transformer
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings from drug "description + warnings"
print("🔍 Creating embeddings...")
texts = df["description"].fillna("") + " " + df["warnings"].fillna("")
embeddings = model.encode(texts.tolist())

# Build FAISS index
print("📦 Building FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
# Convert DataFrame to list of dicts
metadata = df.to_dict(orient="records")

# Save FAISS index and metadata
with open("faiss_index/index.pkl", "wb") as f:
    pickle.dump((index, metadata), f)


print(f"✅ FAISS index saved to {OUTPUT_INDEX}")

