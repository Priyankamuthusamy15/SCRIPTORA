from flask import Flask, request, render_template, jsonify
import faiss, pickle, json, subprocess
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Load FAISS index and metadata
with open("faiss_index/index.pkl", "rb") as f:
    faiss_index, metadata = pickle.load(f)

# Re-load the model
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_faiss(query):
    try:
        emb = model.encode([query])
        D, I = faiss_index.search(emb, 3)
        results = [metadata[i] for i in I[0]]
        return results
    except Exception as e:
        print(f"⚠️ FAISS search error: {e}")
        return []

def ask_ollama(context, question):
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer briefly and clearly."
    )
    result = subprocess.run(["ollama", "run", "mistral", prompt], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").strip()

@app.route('/')
def homepage():
    return render_template("chatbot.html")

@app.route('/ask', methods=["POST"])
def ask():
    user_question = request.json["question"]
    docs = search_faiss(user_question)
    if not docs:
        return jsonify({"response": "No relevant information found."})
    
    combined_context = "\n\n".join(d["description"] + "\n" + d["warnings"] for d in docs)
    answer = ask_ollama(combined_context, user_question)
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(port=5001, debug=True)

