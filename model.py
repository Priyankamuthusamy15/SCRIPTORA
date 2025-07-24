import faiss
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch

# Load drug database
df = pd.read_csv("C:\\medicinegpt\\drug.csv")

# Load model for embeddings
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Function to generate embeddings
def get_embedding(text):
    if not isinstance(text, str) or text.strip() == "":
        print(f"❌ Skipping invalid input: {text}")
        return np.zeros((10000,), dtype="float32")  # Return a zero vector to avoid FAISS issues
    
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        return model(**tokens).last_hidden_state[:, 0, :].numpy().astype("float32")


# Create FAISS index
d = 10000
index = faiss.IndexFlatL2(d)


# Compute and add embeddings to FAISS
# Ensure all values in df["drug_name"] are strings
df["drug_name"] = df["drug_name"].astype(str)

# Debugging: Print non-string or empty values
for i, drug in enumerate(df["drug_name"]):
    if not isinstance(drug, str) or drug.strip() == "":
        print(f"❌ Invalid value at index {i}: {drug}")

# Convert drugs to embeddings
embeddings = np.array([get_embedding(drug) for drug in df["drug_name"] if isinstance(drug, str) and drug.strip() != ""])

index.add(embeddings)

# Save FAISS index
faiss.write_index(index, "drug_index.faiss")
np.save("drug_names.npy", df["drug_name"].values, allow_pickle=True)

print("✅ FAISS index rebuilt successfully!")